// Package ecmc provides helpers for fetching and parsing Colorado Energy and
// Carbon Management Commission (ECMC, formerly COGCC) public data.
//
// No API key is required. The canonical access path is bulk file download
// from https://ecmc.state.co.us/documents/data/downloads/ — COGIS inquiry
// web applications return HTML and are not used here.
//
// Build:
//
//	go build -o ecmc-client ./golang_client.go
//
// Run examples:
//
//	./ecmc-client monthly --county 123 --year 2024 --month 6
//	./ecmc-client annual --year 2024 --out 2024_dj.csv
//	./ecmc-client fields --out fields.zip
//
// Tested with Go 1.22+.
package main

import (
	"encoding/csv"
	"flag"
	"fmt"
	"io"
	"net/http"
	"os"
	"path/filepath"
	"strconv"
	"strings"
	"time"
)

const (
	defaultUA  = "Mozilla/5.0 (co-ecmc-client)"
	bulkBase   = "https://ecmc.state.co.us/documents/data/downloads"
	gisBase    = "https://ecmc.state.co.us/documents/data/downloads/gis"
	prodBase   = "https://ecmc.state.co.us/documents/data/downloads/production"
	newHostURL = "https://ecmc.colorado.gov"
)

// Core Colorado producing counties (FIPS 3-digit) for quick filtering.
var coreCounties = map[string]string{
	"001": "Adams",
	"013": "Boulder",
	"014": "Broomfield",
	"045": "Garfield",
	"067": "La Plata",
	"071": "Las Animas",
	"103": "Rio Blanco",
	"123": "Weld",
}

// ProductionRow represents one monthly production record as published by
// ECMC in monthly_prod.csv and {YYYY}_prod_reports.csv. Column order in the
// published CSV changes occasionally — always read the header row and map
// by name, not position.
type ProductionRow struct {
	APICounty     string
	APISeqNum     string
	SideTrackNum  string
	Name          string
	Formation     string
	FirstProdDate string
	LastProdDate  string
	OilProd       int
	GasProd       int
	WaterProd     int
	OilDays       int
	GasDays       int
	WaterDays     int
	ReportYear    int
	ReportMonth   int
	OperatorNum   string
	OperatorName  string
}

// HTTPClient is the http.Client used for all ECMC fetches. ECMC rejects
// requests with an empty User-Agent from the new host (ecmc.colorado.gov)
// and will rate-limit aggressive callers on either host.
var HTTPClient = &http.Client{Timeout: 5 * time.Minute}

// fetch performs a GET with a real User-Agent and returns the body.
func fetch(url string) ([]byte, error) {
	req, err := http.NewRequest("GET", url, nil)
	if err != nil {
		return nil, err
	}
	req.Header.Set("User-Agent", defaultUA)
	req.Header.Set("Accept", "*/*")
	resp, err := HTTPClient.Do(req)
	if err != nil {
		return nil, fmt.Errorf("GET %s: %w", url, err)
	}
	defer resp.Body.Close()
	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("GET %s: HTTP %d", url, resp.StatusCode)
	}
	return io.ReadAll(resp.Body)
}

// downloadTo streams a URL to a local file path, with a real User-Agent.
// Use this for large ZIP / CSV files (production, GIS).
func downloadTo(url, dest string) (int64, error) {
	req, err := http.NewRequest("GET", url, nil)
	if err != nil {
		return 0, err
	}
	req.Header.Set("User-Agent", defaultUA)
	resp, err := HTTPClient.Do(req)
	if err != nil {
		return 0, err
	}
	defer resp.Body.Close()
	if resp.StatusCode != http.StatusOK {
		return 0, fmt.Errorf("GET %s: HTTP %d", url, resp.StatusCode)
	}
	if err := os.MkdirAll(filepath.Dir(dest), 0o755); err != nil {
		return 0, err
	}
	out, err := os.Create(dest)
	if err != nil {
		return 0, err
	}
	defer out.Close()
	return io.Copy(out, resp.Body)
}

// MonthlyProdURL returns the canonical URL for the current monthly
// production CSV. The file is refreshed ~monthly and contains the most
// recent reporting months.
func MonthlyProdURL() string {
	return prodBase + "/monthly_prod.csv"
}

// AnnualProdURL returns the URL for a per-year production CSV.
// Valid years run from 1999 to the current year.
func AnnualProdURL(year int) string {
	return fmt.Sprintf("%s/%d_prod_reports.csv", prodBase, year)
}

// FieldsShapefileURL returns the URL for the COGCC fields shapefile zip.
func FieldsShapefileURL() string {
	return gisBase + "/COGCC_FIELDS_SHP.zip"
}

// SB181GDBURL returns the URL for the SB19-181 file geodatabase zip. The
// tag must match a published version — e.g. "20241209" for the 2024-12-09
// final, or "2026_Proposed" for the pending 2026 update.
func SB181GDBURL(tag string) string {
	if strings.Contains(tag, "Proposed") {
		return fmt.Sprintf("%s/sites/ecmc/files/SB181DataFinal_%s.gdb_.zip", newHostURL, tag)
	}
	return fmt.Sprintf("%s/SB181DataFinal_%s.gdb.zip", gisBase, tag)
}

// StreamProductionCSV reads a production CSV from an HTTP response and
// invokes the callback for each ProductionRow. It handles header-based
// column mapping so that column-order changes in the published file do
// not break the parse.
//
// Pass filter = nil to yield every row.
func StreamProductionCSV(url string, filter func(ProductionRow) bool, out func(ProductionRow) error) error {
	req, err := http.NewRequest("GET", url, nil)
	if err != nil {
		return err
	}
	req.Header.Set("User-Agent", defaultUA)
	resp, err := HTTPClient.Do(req)
	if err != nil {
		return err
	}
	defer resp.Body.Close()
	if resp.StatusCode != http.StatusOK {
		return fmt.Errorf("GET %s: HTTP %d", url, resp.StatusCode)
	}
	return parseProdCSV(resp.Body, filter, out)
}

func parseProdCSV(r io.Reader, filter func(ProductionRow) bool, out func(ProductionRow) error) error {
	rdr := csv.NewReader(r)
	rdr.FieldsPerRecord = -1 // tolerate occasional ragged rows
	header, err := rdr.Read()
	if err != nil {
		return fmt.Errorf("read header: %w", err)
	}
	idx := map[string]int{}
	for i, col := range header {
		idx[strings.ToUpper(strings.TrimSpace(col))] = i
	}
	get := func(rec []string, name string) string {
		j, ok := idx[name]
		if !ok || j >= len(rec) {
			return ""
		}
		return strings.TrimSpace(rec[j])
	}
	atoi := func(s string) int {
		n, _ := strconv.Atoi(strings.ReplaceAll(s, ",", ""))
		return n
	}
	for {
		rec, err := rdr.Read()
		if err == io.EOF {
			return nil
		}
		if err != nil {
			return fmt.Errorf("csv read: %w", err)
		}
		row := ProductionRow{
			APICounty:     get(rec, "API_COUNTY"),
			APISeqNum:     get(rec, "API_SEQ_NUM"),
			SideTrackNum:  get(rec, "SIDE_TRACK_NUM"),
			Name:          get(rec, "NAME"),
			Formation:     get(rec, "FORMATION"),
			FirstProdDate: get(rec, "FIRST_PROD_DATE"),
			LastProdDate:  get(rec, "LAST_PROD_DATE"),
			OilProd:       atoi(get(rec, "OIL_PROD")),
			GasProd:       atoi(get(rec, "GAS_PROD")),
			WaterProd:     atoi(get(rec, "WATER_PROD")),
			OilDays:       atoi(get(rec, "OIL_DAYS")),
			GasDays:       atoi(get(rec, "GAS_DAYS")),
			WaterDays:     atoi(get(rec, "WATER_DAYS")),
			ReportYear:    atoi(get(rec, "REPORT_YEAR")),
			ReportMonth:   atoi(get(rec, "REPORT_MONTH")),
			OperatorNum:   get(rec, "OPERATOR_NUM"),
			OperatorName:  get(rec, "OPERATOR_NAME"),
		}
		if filter != nil && !filter(row) {
			continue
		}
		if err := out(row); err != nil {
			return err
		}
	}
}

// CountySummary accumulates oil/gas/water volumes for a (county, year, month)
// tuple. Useful for producing the table+narrative output format described
// in SKILL.md.
type CountySummary struct {
	County  string
	Year    int
	Month   int
	Wells   int
	OilBBL  int64
	GasMCF  int64
	WaterBB int64
}

// SummarizeByCounty groups production rows by (county, year, month) and
// returns a sorted summary slice. Useful for DJ Basin (county 123, 001,
// 014) aggregations.
func SummarizeByCounty(url string, wantCounties []string, year, month int) ([]CountySummary, error) {
	want := map[string]bool{}
	for _, c := range wantCounties {
		want[c] = true
	}
	agg := map[string]*CountySummary{}
	filter := func(r ProductionRow) bool {
		if len(want) > 0 && !want[r.APICounty] {
			return false
		}
		if year > 0 && r.ReportYear != year {
			return false
		}
		if month > 0 && r.ReportMonth != month {
			return false
		}
		return true
	}
	emit := func(r ProductionRow) error {
		key := fmt.Sprintf("%s-%04d-%02d", r.APICounty, r.ReportYear, r.ReportMonth)
		s, ok := agg[key]
		if !ok {
			s = &CountySummary{
				County: r.APICounty,
				Year:   r.ReportYear,
				Month:  r.ReportMonth,
			}
			agg[key] = s
		}
		s.Wells++
		s.OilBBL += int64(r.OilProd)
		s.GasMCF += int64(r.GasProd)
		s.WaterBB += int64(r.WaterProd)
		return nil
	}
	if err := StreamProductionCSV(url, filter, emit); err != nil {
		return nil, err
	}
	out := make([]CountySummary, 0, len(agg))
	for _, s := range agg {
		out = append(out, *s)
	}
	return out, nil
}

// main provides a minimal CLI for common tasks.
func main() {
	if len(os.Args) < 2 {
		printUsage()
		os.Exit(2)
	}
	cmd := os.Args[1]
	fs := flag.NewFlagSet(cmd, flag.ExitOnError)
	switch cmd {
	case "monthly":
		county := fs.String("county", "", "3-digit FIPS (e.g. 123 for Weld). Blank = all.")
		year := fs.Int("year", 0, "Filter report year.")
		month := fs.Int("month", 0, "Filter report month (1-12).")
		_ = fs.Parse(os.Args[2:])
		counties := []string{}
		if *county != "" {
			counties = append(counties, *county)
		}
		rows, err := SummarizeByCounty(MonthlyProdURL(), counties, *year, *month)
		if err != nil {
			fmt.Fprintln(os.Stderr, err)
			os.Exit(1)
		}
		fmt.Println("county,countyName,year,month,wells,oil_bbl,gas_mcf,water_bbl")
		for _, r := range rows {
			fmt.Printf("%s,%s,%04d,%02d,%d,%d,%d,%d\n",
				r.County, coreCounties[r.County], r.Year, r.Month,
				r.Wells, r.OilBBL, r.GasMCF, r.WaterBB)
		}
	case "annual":
		year := fs.Int("year", 0, "Year (1999-present).")
		out := fs.String("out", "", "Output file path (required).")
		_ = fs.Parse(os.Args[2:])
		if *year == 0 || *out == "" {
			fmt.Fprintln(os.Stderr, "annual requires --year and --out")
			os.Exit(2)
		}
		n, err := downloadTo(AnnualProdURL(*year), *out)
		if err != nil {
			fmt.Fprintln(os.Stderr, err)
			os.Exit(1)
		}
		fmt.Printf("wrote %s (%d bytes)\n", *out, n)
	case "fields":
		out := fs.String("out", "COGCC_FIELDS_SHP.zip", "Output file path.")
		_ = fs.Parse(os.Args[2:])
		n, err := downloadTo(FieldsShapefileURL(), *out)
		if err != nil {
			fmt.Fprintln(os.Stderr, err)
			os.Exit(1)
		}
		fmt.Printf("wrote %s (%d bytes)\n", *out, n)
	case "sb181":
		tag := fs.String("tag", "20241209", "SB181 version tag (e.g. 20241209 or 2026_Proposed).")
		out := fs.String("out", "", "Output file path (default derived from tag).")
		_ = fs.Parse(os.Args[2:])
		dest := *out
		if dest == "" {
			dest = fmt.Sprintf("SB181DataFinal_%s.gdb.zip", *tag)
		}
		n, err := downloadTo(SB181GDBURL(*tag), dest)
		if err != nil {
			fmt.Fprintln(os.Stderr, err)
			os.Exit(1)
		}
		fmt.Printf("wrote %s (%d bytes)\n", dest, n)
	default:
		printUsage()
		os.Exit(2)
	}
}

func printUsage() {
	fmt.Fprintln(os.Stderr, `Usage:
  ecmc-client monthly [--county 123] [--year YYYY] [--month 1-12]
      Stream monthly_prod.csv and emit a county/year/month rollup.

  ecmc-client annual --year YYYY --out FILE.csv
      Download {YYYY}_prod_reports.csv.

  ecmc-client fields [--out FILE.zip]
      Download COGCC_FIELDS_SHP.zip (oil and gas field polygons).

  ecmc-client sb181 [--tag 20241209|2026_Proposed] [--out FILE.zip]
      Download an SB19-181 file geodatabase.

Notes:
  - No API key required.
  - ECMC rejects empty User-Agents on ecmc.colorado.gov; this client
    always sends one.
  - Bulk files are refreshed ~monthly; treat the most recent 2-3 months
    of production as preliminary.`)
}
