// pnge-literature Go CLI
//
// Unified literature search client for OpenAlex, CrossRef, USGS Publications
// Warehouse, and DOE OSTI. Stdlib only — no external deps.
//
// Build:
//   go build -o pnge-lit golang_client.go
//
// Usage:
//   pnge-lit --source auto --query "direct lithium extraction" --limit 10
//   pnge-lit --source openalex --query "marcellus lithium" --year-from 2020
//   pnge-lit --doi 10.1016/j.watres.2020.116198
//   pnge-lit --source osti --query "critical minerals" --limit 20
//
// Emits a unified table by default or JSON records with --json.

package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"io"
	"net/http"
	"net/url"
	"os"
	"path/filepath"
	"regexp"
	"sort"
	"strings"
	"sync"
	"time"
)

// -----------------------------------------------------------------------------
// Canonical record
// -----------------------------------------------------------------------------

type Record struct {
	DOI        string   `json:"doi,omitempty"`
	Title      string   `json:"title"`
	Authors    []string `json:"authors"`
	Year       int      `json:"year,omitempty"`
	Venue      string   `json:"venue,omitempty"`
	Type       string   `json:"type,omitempty"`
	Abstract   string   `json:"abstract,omitempty"`
	Citations  int      `json:"citations,omitempty"`
	OpenAccess *bool    `json:"open_access,omitempty"`
	PDFURL     string   `json:"pdf_url,omitempty"`
	Source     string   `json:"source"`
	SourceID   string   `json:"source_id"`
	Provenance []string `json:"provenance,omitempty"`
}

// -----------------------------------------------------------------------------
// Main / flags
// -----------------------------------------------------------------------------

func main() {
	source := flag.String("source", "auto", "openalex|crossref|usgs|osti|auto")
	query := flag.String("query", "", "keyword search query")
	doi := flag.String("doi", "", "single DOI lookup")
	limit := flag.Int("limit", 10, "max results per source (1..50)")
	yearFrom := flag.Int("year-from", 0, "filter publication year >= YYYY")
	yearTo := flag.Int("year-to", 0, "filter publication year <= YYYY")
	mailtoFlag := flag.String("mailto", "", "polite pool contact email")
	asJSON := flag.Bool("json", false, "emit JSON records instead of table")
	flag.Parse()

	if *query == "" && *doi == "" {
		fmt.Fprintln(os.Stderr, "error: --query or --doi is required")
		os.Exit(2)
	}
	if *limit < 1 {
		*limit = 10
	}
	if *limit > 50 {
		*limit = 50
	}

	mailto := resolveMailto(*mailtoFlag)

	var records []Record

	if *doi != "" {
		r, err := lookupDOI(*doi, mailto)
		if err != nil {
			fmt.Fprintf(os.Stderr, "doi lookup failed: %v\n", err)
			os.Exit(1)
		}
		records = []Record{r}
	} else {
		records = runSearch(*source, *query, *limit, *yearFrom, *yearTo, mailto)
	}

	merged := Deduplicate(records)

	if *asJSON {
		enc := json.NewEncoder(os.Stdout)
		enc.SetIndent("", "  ")
		_ = enc.Encode(merged)
		return
	}

	printTable(merged, *query, *source)
}

// -----------------------------------------------------------------------------
// Credentials / polite-pool mailto resolution
// -----------------------------------------------------------------------------

func resolveMailto(flagVal string) string {
	if flagVal != "" {
		return flagVal
	}
	home, _ := os.UserHomeDir()
	candidates := []string{
		filepath.Join(home, ".config", "pnge-literature", "credentials"),
		filepath.Join(home, ".config", "crossref", "credentials"),
		filepath.Join(home, ".config", "openalex", "credentials"),
	}
	for _, p := range candidates {
		data, err := os.ReadFile(p)
		if err != nil {
			continue
		}
		for _, line := range strings.Split(string(data), "\n") {
			if strings.HasPrefix(line, "mailto=") {
				return strings.TrimPrefix(line, "mailto=")
			}
		}
	}
	for _, e := range []string{"PNGE_MAILTO", "CROSSREF_MAILTO", "OPENALEX_MAILTO"} {
		if v := os.Getenv(e); v != "" {
			return v
		}
	}
	return ""
}

// -----------------------------------------------------------------------------
// HTTP helpers
// -----------------------------------------------------------------------------

var httpClient = &http.Client{Timeout: 30 * time.Second}

func httpGet(u string, headers map[string]string) ([]byte, http.Header, int, error) {
	req, err := http.NewRequest("GET", u, nil)
	if err != nil {
		return nil, nil, 0, err
	}
	for k, v := range headers {
		req.Header.Set(k, v)
	}
	resp, err := httpClient.Do(req)
	if err != nil {
		return nil, nil, 0, err
	}
	defer resp.Body.Close()
	body, err := io.ReadAll(resp.Body)
	return body, resp.Header, resp.StatusCode, err
}

// -----------------------------------------------------------------------------
// Routing
// -----------------------------------------------------------------------------

var doiRE = regexp.MustCompile(`(?i)10\.\d{4,9}/\S+`)

func lookupDOI(raw, mailto string) (Record, error) {
	m := doiRE.FindString(raw)
	if m == "" {
		return Record{}, fmt.Errorf("not a valid DOI: %q", raw)
	}
	doi := strings.ToLower(m)
	switch {
	case strings.HasPrefix(doi, "10.3133/"):
		// USGS Numbered Series — USGS Pubs Warehouse lookup by indexId
		indexID := strings.TrimPrefix(doi, "10.3133/")
		return usgsPWSingle(indexID)
	case strings.HasPrefix(doi, "10.2172/"):
		return ostiSingle(strings.TrimPrefix(doi, "10.2172/"))
	case strings.HasPrefix(doi, "10.5066/"):
		return Record{}, fmt.Errorf("DOI %q is a DataCite DOI (USGS data release); use pnge-core:datacite-doi", doi)
	default:
		return crossrefSingle(doi, mailto)
	}
}

func runSearch(source, query string, limit, yearFrom, yearTo int, mailto string) []Record {
	sources := chooseSources(source, query)
	var wg sync.WaitGroup
	var mu sync.Mutex
	var all []Record
	for _, s := range sources {
		wg.Add(1)
		go func(name string) {
			defer wg.Done()
			var recs []Record
			var err error
			switch name {
			case "openalex":
				recs, err = openalexSearch(query, limit, yearFrom, yearTo, mailto)
			case "crossref":
				recs, err = crossrefSearch(query, limit, yearFrom, yearTo, mailto)
			case "usgs":
				recs, err = usgsPWSearch(query, limit, yearFrom, yearTo)
			case "osti":
				recs, err = ostiSearch(query, limit, yearFrom, yearTo)
			}
			if err != nil {
				fmt.Fprintf(os.Stderr, "%s error: %v\n", name, err)
				return
			}
			mu.Lock()
			all = append(all, recs...)
			mu.Unlock()
		}(s)
	}
	wg.Wait()
	return all
}

func chooseSources(source, query string) []string {
	s := strings.ToLower(source)
	if s != "auto" && s != "" {
		switch s {
		case "openalex", "crossref":
			return []string{s}
		case "usgs", "usgs-pw":
			return []string{"usgs"}
		case "osti", "doe-osti":
			return []string{"osti"}
		}
	}
	q := strings.ToLower(query)
	var out []string
	usgsCues := []string{"usgs", "fact sheet", "open-file report", "open file report", "professional paper"}
	ostiCues := []string{"doe", "netl", "sandia", "berkeley lab", "argonne", "pnnl", "ornl", "inl", "nrel", "lanl", "llnl", "national lab"}
	hasUSGS := matchesAny(q, usgsCues)
	hasOSTI := matchesAny(q, ostiCues)
	out = append(out, "openalex")
	if hasUSGS || matchesAny(q, []string{"lithium", "produced water", "critical mineral"}) {
		out = append(out, "usgs")
	}
	if hasOSTI || matchesAny(q, []string{"lithium", "produced water", "critical mineral", "dle"}) {
		out = append(out, "osti")
	}
	return out
}

func matchesAny(hay string, needles []string) bool {
	for _, n := range needles {
		if strings.Contains(hay, n) {
			return true
		}
	}
	return false
}

// -----------------------------------------------------------------------------
// OpenAlex
// -----------------------------------------------------------------------------

type oaResp struct {
	Meta    struct {
		Count int `json:"count"`
	} `json:"meta"`
	Results []oaWork `json:"results"`
}

type oaWork struct {
	ID                    string `json:"id"`
	DOI                   string `json:"doi"`
	DisplayName           string `json:"display_name"`
	PublicationYear       int    `json:"publication_year"`
	Type                  string `json:"type"`
	CitedByCount          int    `json:"cited_by_count"`
	AbstractInvertedIndex map[string][]int `json:"abstract_inverted_index"`
	OpenAccess struct {
		IsOA  bool   `json:"is_oa"`
		OAURL string `json:"oa_url"`
	} `json:"open_access"`
	PrimaryLocation struct {
		Source struct {
			DisplayName string `json:"display_name"`
		} `json:"source"`
		PDFURL string `json:"pdf_url"`
	} `json:"primary_location"`
	Authorships []struct {
		Author struct {
			DisplayName string `json:"display_name"`
		} `json:"author"`
	} `json:"authorships"`
}

func openalexSearch(query string, limit, yFrom, yTo int, mailto string) ([]Record, error) {
	u, _ := url.Parse("https://api.openalex.org/works")
	q := u.Query()
	q.Set("search", query)
	q.Set("per-page", fmt.Sprintf("%d", limit))
	q.Set("sort", "cited_by_count:desc")
	filters := []string{}
	if yFrom > 0 {
		filters = append(filters, fmt.Sprintf("publication_year:>%d", yFrom-1))
	}
	if yTo > 0 {
		filters = append(filters, fmt.Sprintf("publication_year:<%d", yTo+1))
	}
	if len(filters) > 0 {
		q.Set("filter", strings.Join(filters, ","))
	}
	u.RawQuery = q.Encode()
	headers := map[string]string{
		"User-Agent": fmt.Sprintf("pnge-literature/1.0 (mailto:%s)", mailto),
	}
	body, _, code, err := httpGet(u.String(), headers)
	if err != nil {
		return nil, err
	}
	if code != 200 {
		return nil, fmt.Errorf("openalex HTTP %d", code)
	}
	var r oaResp
	if err := json.Unmarshal(body, &r); err != nil {
		return nil, err
	}
	var out []Record
	for _, w := range r.Results {
		rec := oaToRecord(w)
		out = append(out, rec)
	}
	return out, nil
}

func oaToRecord(w oaWork) Record {
	authors := []string{}
	for _, a := range w.Authorships {
		if a.Author.DisplayName != "" {
			authors = append(authors, a.Author.DisplayName)
		}
	}
	isOA := w.OpenAccess.IsOA
	doi := strings.ToLower(strings.TrimPrefix(w.DOI, "https://doi.org/"))
	return Record{
		DOI:        doi,
		Title:      w.DisplayName,
		Authors:    authors,
		Year:       w.PublicationYear,
		Venue:      w.PrimaryLocation.Source.DisplayName,
		Type:       w.Type,
		Abstract:   reconstructOAAbstract(w.AbstractInvertedIndex),
		Citations:  w.CitedByCount,
		OpenAccess: &isOA,
		PDFURL:     pickNonEmpty(w.OpenAccess.OAURL, w.PrimaryLocation.PDFURL),
		Source:     "openalex",
		SourceID:   strings.TrimPrefix(w.ID, "https://openalex.org/"),
	}
}

func reconstructOAAbstract(idx map[string][]int) string {
	if len(idx) == 0 {
		return ""
	}
	type pair struct {
		Pos  int
		Word string
	}
	var pairs []pair
	for w, ps := range idx {
		for _, p := range ps {
			pairs = append(pairs, pair{p, w})
		}
	}
	sort.Slice(pairs, func(i, j int) bool { return pairs[i].Pos < pairs[j].Pos })
	parts := make([]string, len(pairs))
	for i, p := range pairs {
		parts[i] = p.Word
	}
	return strings.Join(parts, " ")
}

// -----------------------------------------------------------------------------
// CrossRef
// -----------------------------------------------------------------------------

type crResp struct {
	Status  string `json:"status"`
	Message crMsg  `json:"message"`
}

type crMsg struct {
	TotalResults int      `json:"total-results"`
	Items        []crWork `json:"items"`
}

type crWork struct {
	DOI                 string     `json:"DOI"`
	Title               []string   `json:"title"`
	Author              []crAuthor `json:"author"`
	ContainerTitle      []string   `json:"container-title"`
	Type                string     `json:"type"`
	PublishedPrint      crDate     `json:"published-print"`
	PublishedOnline     crDate     `json:"published-online"`
	Issued              crDate     `json:"issued"`
	IsReferencedByCount int        `json:"is-referenced-by-count"`
	Abstract            string     `json:"abstract"`
	Link                []crLink   `json:"link"`
}

type crAuthor struct {
	Given  string `json:"given"`
	Family string `json:"family"`
}

type crDate struct {
	DateParts [][]int `json:"date-parts"`
}

type crLink struct {
	URL         string `json:"URL"`
	ContentType string `json:"content-type"`
}

func crossrefSearch(query string, limit, yFrom, yTo int, mailto string) ([]Record, error) {
	u, _ := url.Parse("https://api.crossref.org/works")
	q := u.Query()
	q.Set("query", query)
	q.Set("rows", fmt.Sprintf("%d", limit))
	q.Set("sort", "is-referenced-by-count")
	q.Set("order", "desc")
	q.Set("select", "DOI,title,author,type,published-print,published-online,issued,container-title,is-referenced-by-count,abstract,link")
	filters := []string{"type:journal-article"}
	if yFrom > 0 {
		filters = append(filters, fmt.Sprintf("from-pub-date:%d-01-01", yFrom))
	}
	if yTo > 0 {
		filters = append(filters, fmt.Sprintf("until-pub-date:%d-12-31", yTo))
	}
	q.Set("filter", strings.Join(filters, ","))
	if mailto != "" {
		q.Set("mailto", mailto)
	}
	u.RawQuery = q.Encode()
	body, _, code, err := httpGet(u.String(), nil)
	if err != nil {
		return nil, err
	}
	if code != 200 {
		return nil, fmt.Errorf("crossref HTTP %d", code)
	}
	var r crResp
	if err := json.Unmarshal(body, &r); err != nil {
		return nil, err
	}
	var out []Record
	for _, w := range r.Message.Items {
		out = append(out, crToRecord(w))
	}
	return out, nil
}

func crossrefSingle(doi, mailto string) (Record, error) {
	u := fmt.Sprintf("https://api.crossref.org/works/%s", doi)
	if mailto != "" {
		u += "?mailto=" + url.QueryEscape(mailto)
	}
	body, _, code, err := httpGet(u, nil)
	if err != nil {
		return Record{}, err
	}
	if code == 404 {
		return Record{}, fmt.Errorf("DOI %q not in Crossref; if prefix is 10.5066 or 10.25338 use pnge-core:datacite-doi", doi)
	}
	if code != 200 {
		return Record{}, fmt.Errorf("crossref HTTP %d", code)
	}
	var r struct {
		Message crWork `json:"message"`
	}
	if err := json.Unmarshal(body, &r); err != nil {
		return Record{}, err
	}
	return crToRecord(r.Message), nil
}

func crToRecord(w crWork) Record {
	title := ""
	if len(w.Title) > 0 {
		title = stripHTML(w.Title[0])
	}
	venue := ""
	if len(w.ContainerTitle) > 0 {
		venue = w.ContainerTitle[0]
	}
	year := 0
	for _, d := range []crDate{w.PublishedPrint, w.PublishedOnline, w.Issued} {
		if len(d.DateParts) > 0 && len(d.DateParts[0]) > 0 {
			year = d.DateParts[0][0]
			break
		}
	}
	authors := []string{}
	for _, a := range w.Author {
		name := strings.TrimSpace(a.Family + ", " + shortFirst(a.Given))
		authors = append(authors, name)
	}
	pdf := ""
	if len(w.Link) > 0 {
		pdf = w.Link[0].URL
	}
	return Record{
		DOI:       strings.ToLower(w.DOI),
		Title:     title,
		Authors:   authors,
		Year:      year,
		Venue:     venue,
		Type:      w.Type,
		Abstract:  stripHTML(w.Abstract),
		Citations: w.IsReferencedByCount,
		PDFURL:    pdf,
		Source:    "crossref",
		SourceID:  strings.ToLower(w.DOI),
	}
}

func shortFirst(g string) string {
	g = strings.TrimSpace(g)
	if g == "" {
		return ""
	}
	return string(g[0]) + "."
}

// -----------------------------------------------------------------------------
// USGS Publications Warehouse
// -----------------------------------------------------------------------------

type usgsResp struct {
	RecordCount int          `json:"recordCount"`
	Records     []usgsRecord `json:"records"`
}

type usgsRecord struct {
	ID              int    `json:"id"`
	IndexID         string `json:"indexId"`
	Title           string `json:"title"`
	PublicationYear string `json:"publicationYear"`
	DOI             string `json:"doi"`
	DocAbstract     string `json:"docAbstract"`
	PublicationType struct {
		Text string `json:"text"`
	} `json:"publicationType"`
	SeriesTitle struct {
		Text string `json:"text"`
	} `json:"seriesTitle"`
	SeriesNumber string `json:"seriesNumber"`
	Contributors struct {
		Authors []struct {
			Family string `json:"family"`
			Given  string `json:"given"`
			USGS   bool   `json:"usgs"`
		} `json:"authors"`
	} `json:"contributors"`
	Links []struct {
		Type struct {
			Text string `json:"text"`
		} `json:"type"`
		URL string `json:"url"`
	} `json:"links"`
}

func usgsPWSearch(query string, limit, yFrom, yTo int) ([]Record, error) {
	u, _ := url.Parse("https://pubs.usgs.gov/pubs-services/publication")
	q := u.Query()
	q.Set("q", query)
	q.Set("page_size", fmt.Sprintf("%d", limit))
	if yFrom > 0 && yTo > 0 && yFrom == yTo {
		q.Set("year", fmt.Sprintf("%d", yFrom))
	}
	u.RawQuery = q.Encode()
	body, _, code, err := httpGet(u.String(), nil)
	if err != nil {
		return nil, err
	}
	if code != 200 {
		return nil, fmt.Errorf("usgs HTTP %d", code)
	}
	var r usgsResp
	if err := json.Unmarshal(body, &r); err != nil {
		return nil, err
	}
	var out []Record
	for _, rec := range r.Records {
		out = append(out, usgsToRecord(rec))
	}
	return out, nil
}

func usgsPWSingle(indexID string) (Record, error) {
	u := fmt.Sprintf("https://pubs.usgs.gov/pubs-services/publication/%s", indexID)
	body, _, code, err := httpGet(u, nil)
	if err != nil {
		return Record{}, err
	}
	if code != 200 {
		return Record{}, fmt.Errorf("usgs HTTP %d", code)
	}
	var rec usgsRecord
	if err := json.Unmarshal(body, &rec); err != nil {
		return Record{}, err
	}
	return usgsToRecord(rec), nil
}

func usgsToRecord(r usgsRecord) Record {
	authors := []string{}
	for _, a := range r.Contributors.Authors {
		authors = append(authors, strings.TrimSpace(a.Family+", "+shortFirst(a.Given)))
	}
	year := 0
	fmt.Sscanf(r.PublicationYear, "%d", &year)
	venue := strings.TrimSpace(r.SeriesTitle.Text + " " + r.SeriesNumber)
	pdf := ""
	for _, l := range r.Links {
		if l.Type.Text == "Document" {
			pdf = l.URL
			break
		}
	}
	trueVal := true
	return Record{
		DOI:        strings.ToLower(r.DOI),
		Title:      stripHTML(r.Title),
		Authors:    authors,
		Year:       year,
		Venue:      venue,
		Type:       r.PublicationType.Text,
		Abstract:   stripHTML(r.DocAbstract),
		OpenAccess: &trueVal,
		PDFURL:     pdf,
		Source:     "usgs-pw",
		SourceID:   r.IndexID,
	}
}

// -----------------------------------------------------------------------------
// DOE OSTI
// -----------------------------------------------------------------------------

type ostiRec struct {
	OSTIID          string   `json:"osti_id"`
	Title           string   `json:"title"`
	Authors         []string `json:"authors"`
	PublicationDate string   `json:"publication_date"`
	ProductType     string   `json:"product_type"`
	Description     string   `json:"description"`
	DOI             string   `json:"doi"`
	SponsorOrgs     []string `json:"sponsor_orgs"`
	ResearchOrgs    []string `json:"research_orgs"`
	Links           []struct {
		Rel  string `json:"rel"`
		Href string `json:"href"`
	} `json:"links"`
}

func ostiSearch(query string, limit, yFrom, yTo int) ([]Record, error) {
	u, _ := url.Parse("https://www.osti.gov/api/v1/records")
	q := u.Query()
	// Embed year in q to work around broken date filters
	qs := query
	if yFrom > 0 {
		qs += fmt.Sprintf(" %d", yFrom)
	}
	q.Set("q", qs)
	q.Set("rows", fmt.Sprintf("%d", limit))
	u.RawQuery = q.Encode()
	body, _, code, err := httpGet(u.String(), map[string]string{"Accept": "application/json"})
	if err != nil {
		return nil, err
	}
	if code != 200 {
		return nil, fmt.Errorf("osti HTTP %d", code)
	}
	var arr []ostiRec
	if err := json.Unmarshal(body, &arr); err != nil {
		return nil, err
	}
	var out []Record
	for _, r := range arr {
		out = append(out, ostiToRecord(r))
	}
	return out, nil
}

func ostiSingle(ostiID string) (Record, error) {
	u := fmt.Sprintf("https://www.osti.gov/api/v1/records/%s", ostiID)
	body, _, code, err := httpGet(u, map[string]string{"Accept": "application/json"})
	if err != nil {
		return Record{}, err
	}
	if code != 200 {
		return Record{}, fmt.Errorf("osti HTTP %d", code)
	}
	var arr []ostiRec
	if err := json.Unmarshal(body, &arr); err == nil && len(arr) > 0 {
		return ostiToRecord(arr[0]), nil
	}
	var r ostiRec
	if err := json.Unmarshal(body, &r); err != nil {
		return Record{}, err
	}
	return ostiToRecord(r), nil
}

func ostiToRecord(r ostiRec) Record {
	authors := []string{}
	for _, a := range r.Authors {
		name := a
		if i := strings.Index(a, " ["); i > 0 {
			name = a[:i]
		}
		authors = append(authors, strings.TrimSpace(name))
	}
	year := 0
	if len(r.PublicationDate) >= 4 {
		fmt.Sscanf(r.PublicationDate[:4], "%d", &year)
	}
	venue := ""
	if len(r.ResearchOrgs) > 0 {
		venue = r.ResearchOrgs[0]
	} else if len(r.SponsorOrgs) > 0 {
		venue = r.SponsorOrgs[0]
	}
	pdf := ""
	for _, l := range r.Links {
		if l.Rel == "fulltext" {
			pdf = l.Href
			break
		}
	}
	if pdf == "" && r.OSTIID != "" {
		pdf = "https://www.osti.gov/servlets/purl/" + r.OSTIID
	}
	isOA := pdf != ""
	return Record{
		DOI:        strings.ToLower(r.DOI),
		Title:      stripHTML(r.Title),
		Authors:    authors,
		Year:       year,
		Venue:      venue,
		Type:       r.ProductType,
		Abstract:   stripHTML(r.Description),
		OpenAccess: &isOA,
		PDFURL:     pdf,
		Source:     "doe-osti",
		SourceID:   r.OSTIID,
	}
}

// -----------------------------------------------------------------------------
// Deduplication
// -----------------------------------------------------------------------------

func Deduplicate(records []Record) []Record {
	byDOI := map[string][]Record{}
	var noDOI []Record
	for _, r := range records {
		if r.DOI != "" {
			byDOI[normalizeDOI(r.DOI)] = append(byDOI[normalizeDOI(r.DOI)], r)
		} else {
			noDOI = append(noDOI, r)
		}
	}
	var merged []Record
	for _, group := range byDOI {
		merged = append(merged, mergeGroup(group))
	}
	// Title fallback
	for _, r := range noDOI {
		placed := false
		nr := normalizeTitle(r.Title)
		for i := range merged {
			if titleSimilar(nr, normalizeTitle(merged[i].Title)) {
				merged[i] = mergeGroup([]Record{merged[i], r})
				placed = true
				break
			}
		}
		if !placed {
			merged = append(merged, r)
		}
	}
	sort.Slice(merged, func(i, j int) bool {
		if merged[i].Citations != merged[j].Citations {
			return merged[i].Citations > merged[j].Citations
		}
		return merged[i].Year > merged[j].Year
	})
	return merged
}

func normalizeDOI(d string) string {
	d = strings.ToLower(d)
	d = strings.TrimPrefix(d, "https://doi.org/")
	d = strings.TrimPrefix(d, "http://doi.org/")
	d = strings.TrimPrefix(d, "doi:")
	return strings.TrimSpace(d)
}

func normalizeTitle(t string) string {
	t = strings.ToLower(stripHTML(t))
	var b strings.Builder
	lastSpace := true
	for _, r := range t {
		if (r >= 'a' && r <= 'z') || (r >= '0' && r <= '9') {
			b.WriteRune(r)
			lastSpace = false
		} else if !lastSpace {
			b.WriteRune(' ')
			lastSpace = true
		}
	}
	return strings.TrimSpace(b.String())
}

func titleSimilar(a, b string) bool {
	if a == "" || b == "" {
		return false
	}
	if a == b {
		return true
	}
	maxLen := len(a)
	if len(b) > maxLen {
		maxLen = len(b)
	}
	if maxLen == 0 {
		return false
	}
	dist := levenshtein(a, b)
	ratio := 1.0 - float64(dist)/float64(maxLen)
	return ratio >= 0.92
}

func levenshtein(a, b string) int {
	if len(a) == 0 {
		return len(b)
	}
	if len(b) == 0 {
		return len(a)
	}
	prev := make([]int, len(b)+1)
	cur := make([]int, len(b)+1)
	for j := range prev {
		prev[j] = j
	}
	for i := 1; i <= len(a); i++ {
		cur[0] = i
		for j := 1; j <= len(b); j++ {
			cost := 1
			if a[i-1] == b[j-1] {
				cost = 0
			}
			cur[j] = min3(cur[j-1]+1, prev[j]+1, prev[j-1]+cost)
		}
		prev, cur = cur, prev
	}
	return prev[len(b)]
}

func min3(a, b, c int) int {
	m := a
	if b < m {
		m = b
	}
	if c < m {
		m = c
	}
	return m
}

func mergeGroup(group []Record) Record {
	if len(group) == 1 {
		r := group[0]
		r.Provenance = []string{r.Source}
		return r
	}
	out := group[0]
	sources := map[string]bool{out.Source: true}
	prov := []string{out.Source}
	for _, g := range group[1:] {
		if len(g.Title) > len(out.Title) {
			out.Title = g.Title
		}
		if len(g.Authors) > len(out.Authors) {
			out.Authors = g.Authors
		}
		if g.Year != 0 && (out.Year == 0 || g.Source == "crossref") {
			out.Year = g.Year
		}
		if g.Venue != "" && (out.Venue == "" || g.Source == "crossref") {
			out.Venue = g.Venue
		}
		if g.Type != "" && (out.Type == "" || g.Source == "crossref") {
			out.Type = g.Type
		}
		if len(g.Abstract) > len(out.Abstract) {
			out.Abstract = g.Abstract
		}
		if g.Citations > out.Citations {
			out.Citations = g.Citations
		}
		if g.OpenAccess != nil && *g.OpenAccess {
			t := true
			out.OpenAccess = &t
		}
		if out.PDFURL == "" && g.PDFURL != "" {
			out.PDFURL = g.PDFURL
		}
		if !sources[g.Source] {
			sources[g.Source] = true
			prov = append(prov, g.Source)
		}
	}
	names := make([]string, 0, len(sources))
	for s := range sources {
		names = append(names, s)
	}
	sort.Strings(names)
	out.Source = strings.Join(names, ",")
	out.Provenance = prov
	return out
}

func pickNonEmpty(vals ...string) string {
	for _, v := range vals {
		if v != "" {
			return v
		}
	}
	return ""
}

// -----------------------------------------------------------------------------
// Text helpers + printing
// -----------------------------------------------------------------------------

var htmlTagRE = regexp.MustCompile(`<[^>]*>`)

func stripHTML(s string) string {
	return strings.TrimSpace(htmlTagRE.ReplaceAllString(s, ""))
}

func truncate(s string, n int) string {
	if len(s) <= n {
		return s
	}
	return s[:n-1] + "…"
}

func printTable(records []Record, query, source string) {
	fmt.Printf("## Literature Search: %s\n\n", query)
	fmt.Printf("**Source:** %s  |  **Results:** %d\n\n", source, len(records))
	fmt.Println("| # | Year | Title | Authors | Venue | Cites | OA | DOI | Source |")
	fmt.Println("|---|------|-------|---------|-------|-------|----|-----|--------|")
	for i, r := range records {
		oa := "—"
		if r.OpenAccess != nil {
			if *r.OpenAccess {
				oa = "Yes"
			} else {
				oa = "No"
			}
		}
		authors := "—"
		if len(r.Authors) > 0 {
			authors = r.Authors[0]
			if len(r.Authors) >= 3 {
				authors += " et al."
			} else if len(r.Authors) == 2 {
				authors = r.Authors[0] + "; " + r.Authors[1]
			}
		}
		doi := r.DOI
		if doi == "" {
			doi = "—"
		}
		fmt.Printf("| %d | %d | %s | %s | %s | %d | %s | %s | %s |\n",
			i+1, r.Year, truncate(r.Title, 60), truncate(authors, 30),
			truncate(r.Venue, 30), r.Citations, oa, doi, r.Source)
	}
	fmt.Println()
}
