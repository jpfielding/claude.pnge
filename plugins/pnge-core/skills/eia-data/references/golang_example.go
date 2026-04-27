// eia_client.go — Minimal EIA API v2 client in Go
// Usage: EIA_API_KEY=yourkey go run eia_client.go
package main

import (
	"encoding/json"
	"fmt"
	"net/http"
	"net/url"
	"os"
	"path/filepath"
	"strings"
	"time"
)

const baseURL = "https://api.eia.gov/v2"

// EIAClient holds the API key and HTTP client.
type EIAClient struct {
	apiKey     string
	httpClient *http.Client
}

// DataRow is a generic row — EIA columns vary by route.
type DataRow map[string]interface{}

// EIAResponse mirrors the v2 response envelope.
type EIAResponse struct {
	Response struct {
		Total      int       `json:"total"`
		DateFormat string    `json:"dateFormat"`
		Frequency  string    `json:"frequency"`
		Data       []DataRow `json:"data"`
		Warning    string    `json:"warning,omitempty"`
	} `json:"response"`
	Request struct {
		Command string `json:"command"`
		Params  struct {
			Frequency string `json:"frequency"`
		} `json:"params"`
	} `json:"request"`
}

// resolveAPIKey checks ~/.config/eia/credentials then EIA_API_KEY env var.
func resolveAPIKey() (string, error) {
	home, err := os.UserHomeDir()
	if err == nil {
		creds := filepath.Join(home, ".config", "eia", "credentials")
		if data, err := os.ReadFile(creds); err == nil {
			for _, line := range strings.Split(string(data), "\n") {
				line = strings.TrimSpace(line)
				if strings.HasPrefix(line, "api_key=") {
					return strings.TrimPrefix(line, "api_key="), nil
				}
			}
		}
	}
	if key := os.Getenv("EIA_API_KEY"); key != "" {
		return key, nil
	}
	return "", fmt.Errorf("no EIA API key found; store in ~/.config/eia/credentials as api_key=YOUR_KEY")
}

// NewClient creates a client. Resolves key from credentials file or env var.
func NewClient(apiKey string) (*EIAClient, error) {
	if apiKey == "" {
		var err error
		apiKey, err = resolveAPIKey()
		if err != nil {
			return nil, err
		}
	}
	return &EIAClient{
		apiKey:     apiKey,
		httpClient: &http.Client{Timeout: 30 * time.Second},
	}, nil
}

// QueryParams holds common query parameters.
type QueryParams struct {
	Route     string            // e.g. "electricity/retail-sales/data/"
	Frequency string            // monthly, weekly, annual, hourly
	DataCols  []string          // e.g. ["price", "sales"]
	Facets    map[string]string // e.g. {"stateid": "TX", "sectorid": "RES"}
	Start     string            // e.g. "2023-01"
	End       string            // e.g. "2024-12"
	Length    int               // max 5000
	Offset    int
	SortCol   string // default: "period"
	SortDir   string // "asc" or "desc"
}

// Fetch executes a data request and returns parsed rows.
func (c *EIAClient) Fetch(p QueryParams) ([]DataRow, int, error) {
	if p.Length == 0 {
		p.Length = 5000
	}
	if p.SortCol == "" {
		p.SortCol = "period"
	}
	if p.SortDir == "" {
		p.SortDir = "desc"
	}

	u, err := url.Parse(fmt.Sprintf("%s/%s", baseURL, p.Route))
	if err != nil {
		return nil, 0, err
	}

	q := url.Values{}
	q.Set("api_key", c.apiKey)
	if p.Frequency != "" {
		q.Set("frequency", p.Frequency)
	}
	for _, col := range p.DataCols {
		q.Add("data[]", col)
	}
	for facet, val := range p.Facets {
		q.Add(fmt.Sprintf("facets[%s][]", facet), val)
	}
	if p.Start != "" {
		q.Set("start", p.Start)
	}
	if p.End != "" {
		q.Set("end", p.End)
	}
	q.Set("sort[0][column]", p.SortCol)
	q.Set("sort[0][direction]", p.SortDir)
	q.Set("offset", fmt.Sprintf("%d", p.Offset))
	q.Set("length", fmt.Sprintf("%d", p.Length))

	u.RawQuery = q.Encode()

	resp, err := c.httpClient.Get(u.String())
	if err != nil {
		return nil, 0, fmt.Errorf("HTTP error: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return nil, 0, fmt.Errorf("EIA API returned HTTP %d", resp.StatusCode)
	}

	var result EIAResponse
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return nil, 0, fmt.Errorf("JSON decode error: %w", err)
	}

	if result.Response.Warning != "" {
		fmt.Fprintf(os.Stderr, "EIA WARNING: %s\n", result.Response.Warning)
	}

	return result.Response.Data, result.Response.Total, nil
}

// FetchAll paginates automatically, returning all rows.
func (c *EIAClient) FetchAll(p QueryParams) ([]DataRow, error) {
	var all []DataRow
	p.Offset = 0
	p.Length = 5000

	for {
		rows, total, err := c.Fetch(p)
		if err != nil {
			return nil, err
		}
		all = append(all, rows...)
		p.Offset += len(rows)
		if p.Offset >= total {
			break
		}
	}
	return all, nil
}

// --- Example usage ---

func main() {
	client, err := NewClient("")
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}

	// Example: Texas residential electricity prices, last 12 months
	rows, total, err := client.Fetch(QueryParams{
		Route:     "electricity/retail-sales/data/",
		Frequency: "monthly",
		DataCols:  []string{"price"},
		Facets:    map[string]string{"stateid": "TX", "sectorid": "RES"},
		Length:    12,
	})
	if err != nil {
		fmt.Fprintln(os.Stderr, "fetch error:", err)
		os.Exit(1)
	}

	fmt.Printf("Total records available: %d | Fetched: %d\n\n", total, len(rows))
	fmt.Printf("%-12s  %-8s  %s\n", "Period", "Price", "Units")
	fmt.Println("------------------------------------")
	for _, row := range rows {
		fmt.Printf("%-12v  %-8v  %v\n", row["period"], row["price"], row["price-units"])
	}
}
