// Package okocc provides a minimal Go client for Oklahoma Corporation
// Commission (OCC) public data sources: the OCC ArcGIS Server (PUBLIC
// folder) for induced-seismicity directive AOIs and districts, and the
// per-county Class II saltwater disposal (SWD) PDFs.
//
// No credentials are required. Intended for research-scale bulk pulls.
//
// Usage:
//
//	c := okocc.NewClient()
//	aoi, err := c.QueryLayerGeoJSON(ctx,
//	    "PUBLIC/DIRECTIVE_AOIs/MapServer", 2, "1=1")
//	...
//	pdf, err := c.DownloadCountySWDPDF(ctx, "garfield", "./out")
//
// Cross-reference earthquakes via the usgs-earthquakes skill or the
// FDSN event service at https://earthquake.usgs.gov/fdsnws/event/1/query.
package okocc

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"net/http"
	"net/url"
	"os"
	"path/filepath"
	"strings"
	"time"
)

const (
	gisBase   = "https://gis.occ.ok.gov/server/rest/services"
	swdBase   = "https://oklahoma.gov/content/dam/ok/en/occ/documents/og/salth2o"
	userAgent = "claude-pnge-okocc/1.0 (+research; no credentials)"
)

// Client is a minimal OCC data client.
type Client struct {
	HTTP    *http.Client
	GISBase string // override for tests
	SWDBase string // override for tests
}

// NewClient returns a Client with a 60-second HTTP timeout.
func NewClient() *Client {
	return &Client{
		HTTP:    &http.Client{Timeout: 60 * time.Second},
		GISBase: gisBase,
		SWDBase: swdBase,
	}
}

// ServiceInfo is the minimal subset of an ArcGIS MapServer root JSON
// payload that callers typically need.
type ServiceInfo struct {
	CurrentVersion float64     `json:"currentVersion"`
	MapName        string      `json:"mapName"`
	Layers         []LayerInfo `json:"layers"`
	Tables         []LayerInfo `json:"tables"`
	MaxRecordCount int         `json:"maxRecordCount"`
	Capabilities   string      `json:"capabilities"`
}

// LayerInfo is the subset of ArcGIS layer metadata used for discovery.
type LayerInfo struct {
	ID            int    `json:"id"`
	Name          string `json:"name"`
	Type          string `json:"type"`
	GeometryType  string `json:"geometryType,omitempty"`
	ParentLayerID int    `json:"parentLayerId"`
}

// GetServiceInfo fetches the service root JSON for the given service
// path (e.g. "PUBLIC/INDUCED_SEISMICITY/MapServer").
func (c *Client) GetServiceInfo(ctx context.Context, servicePath string) (*ServiceInfo, error) {
	u := fmt.Sprintf("%s/%s?f=json", strings.TrimRight(c.GISBase, "/"),
		strings.TrimLeft(servicePath, "/"))
	req, err := http.NewRequestWithContext(ctx, http.MethodGet, u, nil)
	if err != nil {
		return nil, err
	}
	req.Header.Set("User-Agent", userAgent)
	resp, err := c.HTTP.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()
	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("GetServiceInfo %s: HTTP %d", u, resp.StatusCode)
	}
	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, err
	}
	// Check for ArcGIS error envelope (e.g. 499 Token Required)
	if strings.Contains(string(body), `"error":{`) {
		return nil, fmt.Errorf("ArcGIS error: %s", string(body))
	}
	var info ServiceInfo
	if err := json.Unmarshal(body, &info); err != nil {
		return nil, fmt.Errorf("decode service info: %w", err)
	}
	return &info, nil
}

// QueryLayerGeoJSON queries a MapServer layer and returns the raw
// GeoJSON FeatureCollection bytes. Pages automatically when a single
// request would exceed maxRecordCount.
//
// servicePath example: "PUBLIC/DIRECTIVE_AOIs/MapServer"
// layerID example: 2
// where example: "1=1" or "COUNTY='GARFIELD'"
func (c *Client) QueryLayerGeoJSON(ctx context.Context, servicePath string, layerID int, where string) ([]byte, error) {
	return c.queryLayer(ctx, servicePath, layerID, where, "geojson")
}

// QueryLayerJSON is like QueryLayerGeoJSON but returns the ArcGIS native
// JSON (attributes-focused, easier for tabular analysis).
func (c *Client) QueryLayerJSON(ctx context.Context, servicePath string, layerID int, where string) ([]byte, error) {
	return c.queryLayer(ctx, servicePath, layerID, where, "json")
}

func (c *Client) queryLayer(ctx context.Context, servicePath string, layerID int, where, format string) ([]byte, error) {
	base := fmt.Sprintf("%s/%s/%d/query",
		strings.TrimRight(c.GISBase, "/"),
		strings.Trim(servicePath, "/"), layerID)

	// First page to discover total and whether paging is needed.
	firstPage, exceeded, err := c.fetchPage(ctx, base, where, format, 0, 2000)
	if err != nil {
		return nil, err
	}
	if !exceeded {
		return firstPage, nil
	}

	// Paging case: stitch multiple pages. For GeoJSON we merge features;
	// for ArcGIS JSON we merge features. Both share the same structure
	// at the Go-map level.
	merged, err := mergePages(firstPage)
	if err != nil {
		return nil, err
	}
	offset := 2000
	for {
		page, exceeded, err := c.fetchPage(ctx, base, where, format, offset, 2000)
		if err != nil {
			return nil, err
		}
		if err := appendFeatures(merged, page); err != nil {
			return nil, err
		}
		if !exceeded {
			break
		}
		offset += 2000
	}
	return json.Marshal(merged)
}

func (c *Client) fetchPage(ctx context.Context, base, where, format string, offset, count int) ([]byte, bool, error) {
	form := url.Values{}
	form.Set("where", where)
	form.Set("outFields", "*")
	form.Set("returnGeometry", "true")
	form.Set("resultOffset", fmt.Sprintf("%d", offset))
	form.Set("resultRecordCount", fmt.Sprintf("%d", count))
	form.Set("f", format)

	req, err := http.NewRequestWithContext(ctx, http.MethodPost, base,
		strings.NewReader(form.Encode()))
	if err != nil {
		return nil, false, err
	}
	req.Header.Set("Content-Type", "application/x-www-form-urlencoded")
	req.Header.Set("User-Agent", userAgent)

	resp, err := c.HTTP.Do(req)
	if err != nil {
		return nil, false, err
	}
	defer resp.Body.Close()
	if resp.StatusCode != http.StatusOK {
		return nil, false, fmt.Errorf("query %s offset=%d: HTTP %d",
			base, offset, resp.StatusCode)
	}
	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, false, err
	}

	// Cheap transfer-limit probe (works for both json and geojson).
	exceeded := strings.Contains(string(body), `"exceededTransferLimit":true`) ||
		strings.Contains(string(body), `"exceededTransferLimit": true`)
	if strings.Contains(string(body), `"error":{`) {
		return nil, false, fmt.Errorf("ArcGIS error: %s", string(body))
	}
	return body, exceeded, nil
}

func mergePages(first []byte) (map[string]interface{}, error) {
	var m map[string]interface{}
	if err := json.Unmarshal(first, &m); err != nil {
		return nil, err
	}
	if _, ok := m["features"]; !ok {
		return nil, errors.New("response has no features array")
	}
	return m, nil
}

func appendFeatures(dst map[string]interface{}, pageBytes []byte) error {
	var page map[string]interface{}
	if err := json.Unmarshal(pageBytes, &page); err != nil {
		return err
	}
	dstFeats, _ := dst["features"].([]interface{})
	pageFeats, _ := page["features"].([]interface{})
	dst["features"] = append(dstFeats, pageFeats...)
	return nil
}

// DownloadCountySWDPDF downloads the per-county Class II SWD records PDF
// to destDir. county is the lowercase slug (e.g. "garfield", "le-flore").
// Returns the output file path.
func (c *Client) DownloadCountySWDPDF(ctx context.Context, county, destDir string) (string, error) {
	if county == "" {
		return "", errors.New("county is required")
	}
	if err := os.MkdirAll(destDir, 0o755); err != nil {
		return "", err
	}
	out := filepath.Join(destDir, county+".pdf")
	u := fmt.Sprintf("%s/%s.pdf", strings.TrimRight(c.SWDBase, "/"), county)
	req, err := http.NewRequestWithContext(ctx, http.MethodGet, u, nil)
	if err != nil {
		return "", err
	}
	req.Header.Set("User-Agent", userAgent)
	resp, err := c.HTTP.Do(req)
	if err != nil {
		return "", err
	}
	defer resp.Body.Close()
	if resp.StatusCode == http.StatusNotFound {
		return "", fmt.Errorf("county SWD PDF not found for %q — verify slug at "+
			"https://oklahoma.gov/occ/divisions/oil-gas/induced-seismicity-and-uic-department/salt-water-disposal-records-by-county.html",
			county)
	}
	if resp.StatusCode != http.StatusOK {
		return "", fmt.Errorf("download %s: HTTP %d", u, resp.StatusCode)
	}
	f, err := os.Create(out)
	if err != nil {
		return "", err
	}
	defer f.Close()
	if _, err := io.Copy(f, resp.Body); err != nil {
		return "", err
	}
	return out, nil
}

// OklahomaBBox returns the conventional Oklahoma statewide bounding box
// used for USGS ComCat queries and GIS filtering.
func OklahomaBBox() (minLat, maxLat, minLon, maxLon float64) {
	return 33.6, 37.0, -103.0, -94.4
}

// AllCounties returns the 77 Oklahoma county PDF slugs. Multi-word
// counties use the slug OCC actually publishes; verify unknown ones
// against the SWD index page before automating.
func AllCounties() []string {
	return []string{
		"adair", "alfalfa", "atoka", "beaver", "beckham", "blaine",
		"bryan", "caddo", "canadian", "carter", "cherokee", "choctaw",
		"cimarron", "cleveland", "coal", "comanche", "cotton", "craig",
		"creek", "custer", "delaware", "dewey", "ellis", "garfield",
		"garvin", "grady", "grant", "greer", "harmon", "harper",
		"haskell", "hughes", "jackson", "jefferson", "johnston", "kay",
		"kingfisher", "kiowa", "latimer", "leflore", "lincoln", "logan",
		"love", "major", "marshall", "mayes", "mcclain", "mccurtain",
		"mcintosh", "murray", "muskogee", "noble", "nowata", "okfuskee",
		"oklahoma", "okmulgee", "osage", "ottawa", "pawnee", "payne",
		"pittsburg", "pontotoc", "pottawatomie", "pushmataha", "rogermills",
		"rogers", "seminole", "sequoyah", "stephens", "texas", "tillman",
		"tulsa", "wagoner", "washington", "washita", "woods", "woodward",
	}
}
