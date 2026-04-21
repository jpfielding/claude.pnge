// Package main is a self-contained DataCite REST client for the datacite-doi
// skill. Build with:
//
//	go build -o datacite datacite.go
//
// Usage (flags must precede positional args — stdlib flag quirk):
//
//	datacite search --client usgs.prod --size 10 "lithium produced water"
//	datacite resolve 10.5066/p9zkrwqf
//	datacite clients usgs
//
// No authentication required. Set DATACITE_UA to override the User-Agent.
package main

import (
	"encoding/json"
	"errors"
	"flag"
	"fmt"
	"io"
	"net/http"
	"net/url"
	"os"
	"strconv"
	"strings"
	"time"
)

const (
	defaultBaseURL = "https://api.datacite.org"
	defaultUA      = "claude-pnge-datacite-doi/1.0 (+https://github.com/anthropics/claude-code)"
	acceptHeader   = "application/vnd.api+json"
	httpTimeout    = 30 * time.Second
)

// DOIResource mirrors the JSON:API "dois" resource object. Only fields we
// actually render are unmarshalled; the rest is kept as raw JSON so callers
// that need more can decode on demand.
type DOIResource struct {
	ID         string        `json:"id"`
	Type       string        `json:"type"`
	Attributes DOIAttributes `json:"attributes"`
}

// DOIAttributes holds the subset of DataCite metadata fields the client
// pretty-prints. The upstream schema is much larger — see api_reference.md.
type DOIAttributes struct {
	DOI             string        `json:"doi"`
	Prefix          string        `json:"prefix"`
	Suffix          string        `json:"suffix"`
	Titles          []Title       `json:"titles"`
	Creators        []Creator     `json:"creators"`
	Publisher       string        `json:"publisher"`
	PublicationYear int           `json:"publicationYear"`
	Types           ResourceTypes `json:"types"`
	Descriptions    []Description `json:"descriptions"`
	Subjects        []Subject     `json:"subjects"`
	URL             string        `json:"url"`
	Created         string        `json:"created"`
	Updated         string        `json:"updated"`
	State           string        `json:"state"`
	Version         string        `json:"version"`
}

type Title struct {
	Title string `json:"title"`
}

type Creator struct {
	Name       string `json:"name"`
	NameType   string `json:"nameType"`
	GivenName  string `json:"givenName"`
	FamilyName string `json:"familyName"`
}

type ResourceTypes struct {
	ResourceType        string `json:"resourceType"`
	ResourceTypeGeneral string `json:"resourceTypeGeneral"`
}

type Description struct {
	Description     string `json:"description"`
	DescriptionType string `json:"descriptionType"`
}

type Subject struct {
	Subject string `json:"subject"`
}

// ListResponse is the JSON:API envelope returned by /dois and /clients list
// endpoints.
type ListResponse struct {
	Data  []DOIResource `json:"data"`
	Meta  Meta          `json:"meta"`
	Links Links         `json:"links"`
}

type SingleResponse struct {
	Data DOIResource `json:"data"`
}

type Meta struct {
	Total      int `json:"total"`
	TotalPages int `json:"totalPages"`
	Page       int `json:"page"`
}

type Links struct {
	Self string `json:"self"`
	Next string `json:"next"`
	Last string `json:"last"`
}

// ClientResource is returned by /clients (DataCite's term "client" == repository).
type ClientResource struct {
	ID         string `json:"id"`
	Attributes struct {
		Name          string `json:"name"`
		Year          int    `json:"year"`
		ContactEmail  string `json:"contactEmail"`
		RepositoryURL string `json:"repositoryUrl"`
	} `json:"attributes"`
}

type ClientListResponse struct {
	Data []ClientResource `json:"data"`
	Meta Meta             `json:"meta"`
}

// DataCiteClient is a tiny wrapper around net/http with sensible defaults.
// It is stateless and safe to share across goroutines.
type DataCiteClient struct {
	BaseURL    string
	UserAgent  string
	HTTPClient *http.Client
}

func NewClient() *DataCiteClient {
	ua := os.Getenv("DATACITE_UA")
	if ua == "" {
		ua = defaultUA
	}
	return &DataCiteClient{
		BaseURL:    defaultBaseURL,
		UserAgent:  ua,
		HTTPClient: &http.Client{Timeout: httpTimeout},
	}
}

// SearchParams controls /dois queries. Zero values are omitted.
type SearchParams struct {
	Query           string
	ClientID        string
	ProviderID      string
	ResourceTypeID  string
	PublicationYear int
	Sort            string
	Page            int
	PageSize        int
}

func (p SearchParams) encode() string {
	v := url.Values{}
	if p.Query != "" {
		v.Set("query", p.Query)
	}
	if p.ClientID != "" {
		v.Set("client-id", p.ClientID)
	}
	if p.ProviderID != "" {
		v.Set("provider-id", p.ProviderID)
	}
	if p.ResourceTypeID != "" {
		v.Set("resource-type-id", p.ResourceTypeID)
	}
	if p.PublicationYear > 0 {
		v.Set("publication-year", strconv.Itoa(p.PublicationYear))
	}
	if p.Sort != "" {
		v.Set("sort", p.Sort)
	}
	if p.Page > 0 {
		v.Set("page[number]", strconv.Itoa(p.Page))
	}
	size := p.PageSize
	if size <= 0 {
		size = 25
	}
	if size > 1000 {
		size = 1000
	}
	v.Set("page[size]", strconv.Itoa(size))
	return v.Encode()
}

// do executes an HTTP GET against the base URL, handling rate limits and
// unwrapping error bodies into a Go error.
func (c *DataCiteClient) do(path, query string, out any) error {
	u := c.BaseURL + path
	if query != "" {
		u = u + "?" + query
	}
	req, err := http.NewRequest(http.MethodGet, u, nil)
	if err != nil {
		return fmt.Errorf("build request: %w", err)
	}
	req.Header.Set("Accept", acceptHeader)
	req.Header.Set("User-Agent", c.UserAgent)

	resp, err := c.HTTPClient.Do(req)
	if err != nil {
		return fmt.Errorf("http: %w", err)
	}
	defer resp.Body.Close()

	body, _ := io.ReadAll(resp.Body)
	switch resp.StatusCode {
	case http.StatusOK:
		if err := json.Unmarshal(body, out); err != nil {
			return fmt.Errorf("decode: %w", err)
		}
		return nil
	case http.StatusNotFound:
		return errNotFound
	case http.StatusTooManyRequests:
		retry := resp.Header.Get("Retry-After")
		return fmt.Errorf("rate limited; retry-after=%q", retry)
	default:
		return fmt.Errorf("http %d: %s", resp.StatusCode, strings.TrimSpace(string(body)))
	}
}

var errNotFound = errors.New("not found")

// SearchDOIs runs a /dois query and returns the parsed envelope.
func (c *DataCiteClient) SearchDOIs(p SearchParams) (*ListResponse, error) {
	var out ListResponse
	if err := c.do("/dois", p.encode(), &out); err != nil {
		return nil, err
	}
	return &out, nil
}

// ResolveDOI fetches a single DOI record. A 404 is surfaced as errNotFound
// so callers can fall back to Crossref cleanly.
func (c *DataCiteClient) ResolveDOI(doi string) (*DOIResource, error) {
	doi = strings.TrimPrefix(doi, "https://doi.org/")
	doi = strings.TrimPrefix(doi, "doi:")
	var out SingleResponse
	if err := c.do("/dois/"+url.PathEscape(doi), "", &out); err != nil {
		return nil, err
	}
	return &out.Data, nil
}

// SearchClients runs a /clients query — useful for discovering the lowercase
// client-id to pass to SearchDOIs.
func (c *DataCiteClient) SearchClients(query string) (*ClientListResponse, error) {
	v := url.Values{}
	if query != "" {
		v.Set("query", query)
	}
	v.Set("page[size]", "25")
	var out ClientListResponse
	if err := c.do("/clients", v.Encode(), &out); err != nil {
		return nil, err
	}
	return &out, nil
}

// firstAbstract returns the first description of type "Abstract", falling
// back to the first description of any type. Empty string if none.
func firstAbstract(ds []Description) string {
	for _, d := range ds {
		if strings.EqualFold(d.DescriptionType, "Abstract") {
			return d.Description
		}
	}
	if len(ds) > 0 {
		return ds[0].Description
	}
	return ""
}

// truncate cuts a string to n runes, appending an ellipsis when cut. It
// respects rune boundaries so we do not split multi-byte UTF-8 characters.
func truncate(s string, n int) string {
	r := []rune(s)
	if len(r) <= n {
		return s
	}
	return string(r[:n]) + "..."
}

// joinCreators formats the first `max` creator names, appending "et al."
// when more creators exist. Used for compact table rows.
func joinCreators(cs []Creator, max int) string {
	if len(cs) == 0 {
		return "(no creators)"
	}
	names := make([]string, 0, max)
	for i, c := range cs {
		if i >= max {
			break
		}
		names = append(names, c.Name)
	}
	out := strings.Join(names, "; ")
	if len(cs) > max {
		out += "; et al."
	}
	return out
}

// printSearchTable renders a markdown table + summary block matching the
// EIA skill output style.
func printSearchTable(w io.Writer, resp *ListResponse, label string) {
	fmt.Fprintf(w, "## DataCite search: %s\n\n", label)
	fmt.Fprintf(w, "| DOI | Year | Type | Title |\n")
	fmt.Fprintf(w, "|-----|------|------|-------|\n")
	for _, d := range resp.Data {
		title := ""
		if len(d.Attributes.Titles) > 0 {
			title = d.Attributes.Titles[0].Title
		}
		fmt.Fprintf(w, "| %s | %d | %s | %s |\n",
			d.Attributes.DOI,
			d.Attributes.PublicationYear,
			d.Attributes.Types.ResourceTypeGeneral,
			truncate(strings.ReplaceAll(title, "|", "/"), 70),
		)
	}
	fmt.Fprintf(w, "\n**Total matches:** %d across %d page(s). Showing %d.\n",
		resp.Meta.Total, resp.Meta.TotalPages, len(resp.Data))
}

// printSingle renders a full DOI record for the `resolve` subcommand.
func printSingle(w io.Writer, d *DOIResource) {
	a := d.Attributes
	title := ""
	if len(a.Titles) > 0 {
		title = a.Titles[0].Title
	}
	fmt.Fprintf(w, "DOI:        %s\n", a.DOI)
	fmt.Fprintf(w, "Title:      %s\n", title)
	fmt.Fprintf(w, "Creators:   %s\n", joinCreators(a.Creators, 5))
	fmt.Fprintf(w, "Publisher:  %s\n", a.Publisher)
	fmt.Fprintf(w, "Year:       %d\n", a.PublicationYear)
	fmt.Fprintf(w, "Type:       %s (%s)\n", a.Types.ResourceTypeGeneral, a.Types.ResourceType)
	fmt.Fprintf(w, "URL:        %s\n", a.URL)
	fmt.Fprintf(w, "State:      %s\n", a.State)
	if ab := firstAbstract(a.Descriptions); ab != "" {
		fmt.Fprintf(w, "\nAbstract:\n%s\n", truncate(ab, 1200))
	}
}

// main is a thin CLI harness. Production callers should import
// DataCiteClient directly rather than shelling out to this binary.
func main() {
	if len(os.Args) < 2 {
		usage()
		os.Exit(2)
	}
	c := NewClient()
	switch os.Args[1] {
	case "search":
		cmdSearch(c, os.Args[2:])
	case "resolve":
		cmdResolve(c, os.Args[2:])
	case "clients":
		cmdClients(c, os.Args[2:])
	case "-h", "--help", "help":
		usage()
	default:
		fmt.Fprintf(os.Stderr, "unknown subcommand: %s\n", os.Args[1])
		usage()
		os.Exit(2)
	}
}

func usage() {
	fmt.Fprintln(os.Stderr, `datacite — DataCite REST client

Usage:
  datacite search <query> [--client ID] [--provider ID] [--type ID] [--year N] [--size N] [--sort KEY]
  datacite resolve <doi>
  datacite clients <query>

Note: flags must precede positional arguments (stdlib flag quirk).

Examples:
  datacite search --client usgs.prod --size 10 "lithium produced water"
  datacite resolve 10.5066/p9zkrwqf
  datacite clients usgs`)
}

func cmdSearch(c *DataCiteClient, args []string) {
	fs := flag.NewFlagSet("search", flag.ExitOnError)
	client := fs.String("client", "", "client-id filter (e.g. usgs.prod)")
	provider := fs.String("provider", "", "provider-id filter")
	rtype := fs.String("type", "", "resource-type-id filter (dataset, text, software, ...)")
	year := fs.Int("year", 0, "publication-year filter")
	size := fs.Int("size", 10, "page size (max 1000)")
	sort := fs.String("sort", "", "sort key (e.g. -created)")
	_ = fs.Parse(args)
	if fs.NArg() < 1 {
		fmt.Fprintln(os.Stderr, "search: missing query")
		os.Exit(2)
	}
	q := strings.Join(fs.Args(), " ")
	resp, err := c.SearchDOIs(SearchParams{
		Query: q, ClientID: *client, ProviderID: *provider,
		ResourceTypeID: *rtype, PublicationYear: *year,
		PageSize: *size, Sort: *sort,
	})
	if err != nil {
		fmt.Fprintln(os.Stderr, "search failed:", err)
		os.Exit(1)
	}
	label := fmt.Sprintf("%q", q)
	if *client != "" {
		label += fmt.Sprintf(" (client-id=%s)", *client)
	}
	printSearchTable(os.Stdout, resp, label)
}

func cmdResolve(c *DataCiteClient, args []string) {
	if len(args) < 1 {
		fmt.Fprintln(os.Stderr, "resolve: missing DOI")
		os.Exit(2)
	}
	d, err := c.ResolveDOI(args[0])
	if err != nil {
		if errors.Is(err, errNotFound) {
			fmt.Fprintln(os.Stderr, "not in DataCite — try the crossref-doi skill")
			os.Exit(3)
		}
		fmt.Fprintln(os.Stderr, "resolve failed:", err)
		os.Exit(1)
	}
	printSingle(os.Stdout, d)
}

func cmdClients(c *DataCiteClient, args []string) {
	q := ""
	if len(args) > 0 {
		q = strings.Join(args, " ")
	}
	resp, err := c.SearchClients(q)
	if err != nil {
		fmt.Fprintln(os.Stderr, "clients failed:", err)
		os.Exit(1)
	}
	fmt.Printf("%-24s  %s\n", "client-id", "name")
	fmt.Printf("%-24s  %s\n", strings.Repeat("-", 24), strings.Repeat("-", 40))
	for _, r := range resp.Data {
		fmt.Printf("%-24s  %s\n", r.ID, r.Attributes.Name)
	}
	fmt.Printf("\n%d of %d clients matched.\n", len(resp.Data), resp.Meta.Total)
}
