// Package main is a minimal Go client for the CalGEM WellSTAR ArcGIS REST
// service. It queries the Wells MapServer (Layer 0 = oil/gas, Layer 1 =
// geothermal), paginates over large result sets, and emits CSV to stdout.
//
// Build:   go build -o calgem-well-query ./golang_client.go
// Example: ./calgem-well-query -layer 1 -county Imperial -status Active
//          ./calgem-well-query -layer 0 -county Kern -type "Water Disposal"
//
// No API key required. CalGEM data is public.
//
// The client is intentionally dependency-free (stdlib only) to keep the
// plugin lightweight. For research-scale joins, write the CSV to disk then
// load into duckdb, pandas, or Arrow.
package main

import (
	"encoding/csv"
	"encoding/json"
	"flag"
	"fmt"
	"log"
	"net/http"
	"net/url"
	"os"
	"strconv"
	"strings"
	"time"
)

const (
	restRoot     = "https://gis.conservation.ca.gov/server/rest/services/WellSTAR/Wells/MapServer"
	pageSize     = 5000
	httpTimeout  = 60 * time.Second
	userAgentStr = "claude-pnge/calgem-client (github.com/wvu-pnge)"
)

// queryResponse is the subset of the ArcGIS query response we care about.
type queryResponse struct {
	ExceededTransferLimit bool              `json:"exceededTransferLimit"`
	Features              []json.RawMessage `json:"features"`
	Fields                []struct {
		Name string `json:"name"`
		Type string `json:"type"`
	} `json:"fields"`
	Error *struct {
		Code    int      `json:"code"`
		Message string   `json:"message"`
		Details []string `json:"details"`
	} `json:"error"`
}

type countResponse struct {
	Count int `json:"count"`
	Error *struct {
		Code    int    `json:"code"`
		Message string `json:"message"`
	} `json:"error"`
}

// feature is a relaxed shape for decoding a single ArcGIS feature.
type feature struct {
	Attributes map[string]any `json:"attributes"`
}

func main() {
	var (
		layer        = flag.Int("layer", 0, "MapServer layer: 0=oil/gas well, 1=geothermal well")
		county       = flag.String("county", "", "County name filter (e.g. Kern, Imperial)")
		wellType     = flag.String("type", "", "WellType filter (e.g. 'Water Disposal', 'Steamflood', 'Geothermal')")
		status       = flag.String("status", "", "WellStatus filter (e.g. Active, Idle, Plugged)")
		operator     = flag.String("operator", "", "OperatorName substring (case-insensitive LIKE)")
		field        = flag.String("field", "", "FieldName substring")
		whereExtra   = flag.String("where", "", "Raw extra WHERE clause (AND-joined)")
		outFields    = flag.String("outFields", "*", "Comma-separated outFields")
		countOnly    = flag.Bool("count", false, "Print count and exit")
		maxRecords   = flag.Int("max", 0, "Max records to fetch (0 = all)")
		includeGeom  = flag.Bool("geom", false, "Include geometry columns")
		outPath      = flag.String("out", "-", "Output CSV path (- = stdout)")
	)
	flag.Parse()

	where := buildWhere(*layer, *county, *wellType, *status, *operator, *field, *whereExtra)

	if *countOnly {
		n, err := fetchCount(*layer, where)
		if err != nil {
			log.Fatalf("count: %v", err)
		}
		fmt.Println(n)
		return
	}

	total, err := fetchCount(*layer, where)
	if err != nil {
		log.Fatalf("count: %v", err)
	}
	log.Printf("matched %d records (layer %d)", total, *layer)
	if *maxRecords > 0 && *maxRecords < total {
		total = *maxRecords
	}

	w, closeFn, err := openCSV(*outPath)
	if err != nil {
		log.Fatalf("open: %v", err)
	}
	defer closeFn()

	var headerWritten bool
	var headerCols []string

	for offset := 0; offset < total; offset += pageSize {
		take := pageSize
		if remaining := total - offset; remaining < take {
			take = remaining
		}
		feats, err := fetchPage(*layer, where, *outFields, offset, take, *includeGeom)
		if err != nil {
			log.Fatalf("fetch page %d: %v", offset, err)
		}
		if len(feats) == 0 {
			break
		}
		if !headerWritten {
			headerCols = collectHeader(feats[0])
			if err := w.Write(headerCols); err != nil {
				log.Fatalf("write header: %v", err)
			}
			headerWritten = true
		}
		for _, f := range feats {
			row := make([]string, len(headerCols))
			for i, col := range headerCols {
				row[i] = stringify(f.Attributes[col])
			}
			if err := w.Write(row); err != nil {
				log.Fatalf("write row: %v", err)
			}
		}
		w.Flush()
		log.Printf("  wrote %d rows (offset %d)", len(feats), offset)
	}
}

// buildWhere composes an ArcGIS SQL WHERE from CLI filters. Quoting assumes
// the user-supplied values do not contain single quotes; if they do, escape
// them by doubling.
func buildWhere(layer int, county, wellType, status, operator, field, extra string) string {
	var clauses []string
	if county != "" {
		clauses = append(clauses, fmt.Sprintf("CountyName='%s'", escape(county)))
	}
	if wellType != "" {
		clauses = append(clauses, fmt.Sprintf("WellType='%s'", escape(wellType)))
	}
	if status != "" {
		clauses = append(clauses, fmt.Sprintf("WellStatus='%s'", escape(status)))
	}
	if operator != "" {
		clauses = append(clauses, fmt.Sprintf("UPPER(OperatorName) LIKE '%%%s%%'", strings.ToUpper(escape(operator))))
	}
	if field != "" {
		clauses = append(clauses, fmt.Sprintf("UPPER(FieldName) LIKE '%%%s%%'", strings.ToUpper(escape(field))))
	}
	if extra != "" {
		clauses = append(clauses, "("+extra+")")
	}
	if len(clauses) == 0 {
		return "1=1"
	}
	return strings.Join(clauses, " AND ")
}

func escape(s string) string { return strings.ReplaceAll(s, "'", "''") }

func fetchCount(layer int, where string) (int, error) {
	u := fmt.Sprintf("%s/%d/query", restRoot, layer)
	body, err := postForm(u, map[string]string{
		"where":           where,
		"returnCountOnly": "true",
		"f":               "json",
	})
	if err != nil {
		return 0, err
	}
	var cr countResponse
	if err := json.Unmarshal(body, &cr); err != nil {
		return 0, fmt.Errorf("decode count: %w (body=%s)", err, truncate(body))
	}
	if cr.Error != nil {
		return 0, fmt.Errorf("ArcGIS error %d: %s", cr.Error.Code, cr.Error.Message)
	}
	return cr.Count, nil
}

func fetchPage(layer int, where, outFields string, offset, count int, includeGeom bool) ([]feature, error) {
	u := fmt.Sprintf("%s/%d/query", restRoot, layer)
	form := map[string]string{
		"where":              where,
		"outFields":          outFields,
		"returnGeometry":     strconv.FormatBool(includeGeom),
		"resultOffset":       strconv.Itoa(offset),
		"resultRecordCount":  strconv.Itoa(count),
		"orderByFields":      primaryKeyFor(layer),
		"f":                  "json",
	}
	body, err := postForm(u, form)
	if err != nil {
		return nil, err
	}
	var qr queryResponse
	if err := json.Unmarshal(body, &qr); err != nil {
		return nil, fmt.Errorf("decode page: %w (body=%s)", err, truncate(body))
	}
	if qr.Error != nil {
		return nil, fmt.Errorf("ArcGIS error %d: %s", qr.Error.Code, qr.Error.Message)
	}
	out := make([]feature, 0, len(qr.Features))
	for _, raw := range qr.Features {
		var f feature
		if err := json.Unmarshal(raw, &f); err != nil {
			return nil, fmt.Errorf("decode feature: %w", err)
		}
		out = append(out, f)
	}
	return out, nil
}

func primaryKeyFor(layer int) string {
	if layer == 1 {
		return "APINumber"
	}
	return "API"
}

func postForm(target string, form map[string]string) ([]byte, error) {
	vals := url.Values{}
	for k, v := range form {
		vals.Set(k, v)
	}
	client := &http.Client{Timeout: httpTimeout}
	req, err := http.NewRequest("POST", target, strings.NewReader(vals.Encode()))
	if err != nil {
		return nil, err
	}
	req.Header.Set("Content-Type", "application/x-www-form-urlencoded")
	req.Header.Set("User-Agent", userAgentStr)
	resp, err := client.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()
	if resp.StatusCode != 200 {
		return nil, fmt.Errorf("http %d from %s", resp.StatusCode, target)
	}
	buf := make([]byte, 0, 32*1024)
	chunk := make([]byte, 32*1024)
	for {
		n, err := resp.Body.Read(chunk)
		if n > 0 {
			buf = append(buf, chunk[:n]...)
		}
		if err != nil {
			break
		}
	}
	return buf, nil
}

func collectHeader(f feature) []string {
	keys := make([]string, 0, len(f.Attributes))
	for k := range f.Attributes {
		keys = append(keys, k)
	}
	// Stable order: primary identification columns first, then alphabetical.
	preferred := []string{"API", "APINumber", "LeaseName", "WellNumber",
		"OperatorName", "FieldName", "AreaName", "WellType", "WellStatus",
		"District", "CountyName", "Lat83", "Long83", "Latitude", "Longitude"}
	seen := map[string]bool{}
	ordered := make([]string, 0, len(keys))
	for _, p := range preferred {
		for _, k := range keys {
			if k == p {
				ordered = append(ordered, k)
				seen[k] = true
			}
		}
	}
	for _, k := range keys {
		if !seen[k] {
			ordered = append(ordered, k)
		}
	}
	return ordered
}

func stringify(v any) string {
	switch t := v.(type) {
	case nil:
		return ""
	case string:
		return t
	case float64:
		// ArcGIS returns integers as float64; render without ".0" when whole.
		if t == float64(int64(t)) {
			return strconv.FormatInt(int64(t), 10)
		}
		return strconv.FormatFloat(t, 'f', -1, 64)
	case bool:
		return strconv.FormatBool(t)
	default:
		b, _ := json.Marshal(t)
		return string(b)
	}
}

func openCSV(path string) (*csv.Writer, func(), error) {
	if path == "-" {
		w := csv.NewWriter(os.Stdout)
		return w, func() { w.Flush() }, nil
	}
	f, err := os.Create(path)
	if err != nil {
		return nil, nil, err
	}
	w := csv.NewWriter(f)
	return w, func() { w.Flush(); f.Close() }, nil
}

func truncate(b []byte) string {
	const n = 500
	if len(b) <= n {
		return string(b)
	}
	return string(b[:n]) + "...<truncated>"
}
