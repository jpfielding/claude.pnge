// Package main — unified CLI for appalachia-mineral-parcels
//
// Queries public ArcGIS REST services in WV, PA, and OH to find
// tax-delinquent, dormant, or severed mineral parcels near active
// Marcellus/Utica wells. State selected via --state wv|pa|oh.
//
// Stdlib only (net/http, encoding/json, flag, crypto/tls).
//
// Usage:
//
//	go run golang_client.go --state wv --county Tyler --limit 20
//	go run golang_client.go --state wv --county Marshall --wells --radius 1
//	go run golang_client.go --state pa --county Greene --wells
//	go run golang_client.go --state oh --county BELMONT --luc 240,250
//	go run golang_client.go --state oh --county HARRISON --luc 2% --dormant
//
// No credentials required. Uses `curl -k`-equivalent (InsecureSkipVerify)
// ONLY for WVDEP (tagis.dep.wv.gov); all other endpoints use valid TLS.
package main

import (
	"crypto/tls"
	"encoding/json"
	"flag"
	"fmt"
	"io"
	"net/http"
	"net/url"
	"os"
	"strings"
	"time"
)

// --- Endpoints --------------------------------------------------------------

const (
	wvDelinquentURL    = "https://services.wvgis.wvu.edu/arcgis/rest/services/Planning_Cadastre/Delinquent_Properties/MapServer/0"
	wvParcelSummaryURL = "https://services.wvgis.wvu.edu/arcgis/rest/services/Planning_Cadastre/WV_Parcels/MapServer/11"
	wvWellsURL         = "https://tagis.dep.wv.gov/arcgis/rest/services/WVDEP_enterprise/oil_gas/MapServer/7"

	paParcelsURL = "https://gis.dep.pa.gov/depgisprd/rest/services/Parcels/PA_Parcels/MapServer/0"
	paWellsURL   = "https://gis.dep.pa.gov/depgisprd/rest/services/OilGas/OilGasAllStrayGasEGSP/MapServer/3"

	ohOgripURL = "https://services2.arcgis.com/MlJ0G8iWUyC7jAmu/arcgis/rest/services/OhioStatewidePacels_full_view/FeatureServer/0"
	ohOitURL   = "https://maps.ohio.gov/arcgis/rest/services/Statewide_Parcels_2022/MapServer/0"
	ohOdnrURL  = "https://gis.ohiodnr.gov/arcgis/rest/services/DOG_Services/Oilgas_Wells_public/MapServer/0"
)

// --- HTTP clients -----------------------------------------------------------

// Standard client for valid-cert endpoints.
var stdClient = &http.Client{Timeout: 60 * time.Second}

// WVDEP uses a self-signed cert; skip verification.
var wvDepClient = &http.Client{
	Timeout: 60 * time.Second,
	Transport: &http.Transport{
		TLSClientConfig: &tls.Config{InsecureSkipVerify: true},
	},
}

// --- Response model ---------------------------------------------------------

type ArcGISResponse struct {
	Features []struct {
		Attributes map[string]any `json:"attributes"`
		Geometry   *struct {
			X float64 `json:"x"`
			Y float64 `json:"y"`
		} `json:"geometry,omitempty"`
	} `json:"features"`
	Count                 int  `json:"count"`
	ExceededTransferLimit bool `json:"exceededTransferLimit"`
	Error                 *struct {
		Code    int    `json:"code"`
		Message string `json:"message"`
	} `json:"error,omitempty"`
}

// postQuery POSTs the params to {base}/query and parses the response.
func postQuery(client *http.Client, base string, params url.Values) (*ArcGISResponse, error) {
	params.Set("f", "json")
	resp, err := client.PostForm(base+"/query", params)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()
	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, err
	}
	var out ArcGISResponse
	if err := json.Unmarshal(body, &out); err != nil {
		return nil, fmt.Errorf("decode: %w (body: %s)", err, string(body))
	}
	if out.Error != nil {
		return nil, fmt.Errorf("arcgis %d: %s", out.Error.Code, out.Error.Message)
	}
	return &out, nil
}

// --- WV adapter -------------------------------------------------------------

func runWV(county string, status string, keyword string, limit int, wantWells bool, radiusMi float64) error {
	clauses := []string{}
	if county != "" {
		clauses = append(clauses, fmt.Sprintf("county='%s'", county))
	}
	if status == "" {
		status = "No Bid','Deed" // default actionable set
	}
	clauses = append(clauses, fmt.Sprintf("status IN ('%s')", status))
	clauses = append(clauses, fmt.Sprintf("FullLegalDescription LIKE '%%%s%%'", strings.ToUpper(keyword)))
	where := strings.Join(clauses, " AND ")

	// Fetch delinquent parcels
	p := url.Values{}
	p.Set("where", where)
	p.Set("outFields", "CleanParcelID,county,status,FullOwnerName,FullLegalDescription,Acres_C,certno,TotalAmtDue")
	p.Set("resultRecordCount", fmt.Sprintf("%d", limit))
	p.Set("returnGeometry", boolStr(wantWells))
	if wantWells {
		p.Set("outSR", "4326")
	}
	r, err := postQuery(stdClient, wvDelinquentURL, p)
	if err != nil {
		return err
	}

	fmt.Printf("\n[WV] %d parcels (where: %s)\n", len(r.Features), where)
	printHeader([]string{"ParcelID", "Status", "Owner", "Acres", "Due", "Wells"})
	for _, f := range r.Features {
		a := f.Attributes
		wells := "-"
		if wantWells && f.Geometry != nil {
			n, _ := wvNearbyWells(f.Geometry.X, f.Geometry.Y, radiusMi)
			wells = fmt.Sprintf("%d", n)
		}
		printRow([]string{
			asStr(a["CleanParcelID"]),
			asStr(a["status"]),
			asStr(a["FullOwnerName"]),
			asStr(a["Acres_C"]),
			asStr(a["TotalAmtDue"]),
			wells,
		})
	}
	return nil
}

func wvNearbyWells(lon, lat, radiusMi float64) (int, error) {
	p := url.Values{}
	p.Set("geometry", fmt.Sprintf("%f,%f", lon, lat))
	p.Set("geometryType", "esriGeometryPoint")
	p.Set("inSR", "4326")
	p.Set("spatialRel", "esriSpatialRelIntersects")
	p.Set("distance", fmt.Sprintf("%f", radiusMi*1609.34))
	p.Set("units", "esriSRUnit_Meter")
	p.Set("where", "wellstatus='Active Well'")
	p.Set("outFields", "permitid,formation,respparty")
	p.Set("returnGeometry", "false")
	p.Set("resultRecordCount", "50")
	r, err := postQuery(wvDepClient, wvWellsURL, p)
	if err != nil {
		return 0, err
	}
	return len(r.Features), nil
}

// --- PA adapter -------------------------------------------------------------

func runPA(county string, limit int, wantWells bool, radiusMi float64) error {
	// Step 1: find active unconventional wells in the county
	p := url.Values{}
	p.Set("where", fmt.Sprintf("COUNTY='%s' AND UNCONVENTIONAL_IND='Yes' AND WELL_STATUS='Active'", county))
	p.Set("outFields", "PERMIT_NUMBER,WELL_NAME,OPERATOR,LATITUDE,LONGITUDE")
	p.Set("returnGeometry", "false")
	p.Set("resultRecordCount", "50")
	wells, err := postQuery(stdClient, paWellsURL, p)
	if err != nil {
		return err
	}
	fmt.Printf("\n[PA] %d active unconventional wells in %s\n", len(wells.Features), county)

	// Step 2: for up to 20 wells, find parcels within buffer
	seen := map[string]bool{}
	parcels := []map[string]any{}
	for i, w := range wells.Features {
		if i >= 20 {
			break
		}
		lon := asFloat(w.Attributes["LONGITUDE"])
		lat := asFloat(w.Attributes["LATITUDE"])
		if lon == 0 || lat == 0 {
			continue
		}
		pq := url.Values{}
		pq.Set("geometry", fmt.Sprintf("%f,%f", lon, lat))
		pq.Set("geometryType", "esriGeometryPoint")
		pq.Set("inSR", "4326")
		pq.Set("spatialRel", "esriSpatialRelIntersects")
		pq.Set("distance", fmt.Sprintf("%f", radiusMi*1609.34))
		pq.Set("units", "esriSRUnit_Meter")
		pq.Set("outFields", "PARCEL_ID,OWNER_NAME,ACREAGE,COUNTY_NAME,DISTRICT")
		pq.Set("returnGeometry", "false")
		pq.Set("resultRecordCount", "200")
		pr, err := postQuery(stdClient, paParcelsURL, pq)
		if err != nil {
			continue
		}
		for _, f := range pr.Features {
			pid := asStr(f.Attributes["PARCEL_ID"])
			if pid == "" || seen[pid] {
				continue
			}
			seen[pid] = true
			parcels = append(parcels, f.Attributes)
			if len(parcels) >= limit {
				break
			}
		}
		if len(parcels) >= limit {
			break
		}
	}

	fmt.Printf("\n[PA] %d unique parcels within %.1f mi of sampled wells\n", len(parcels), radiusMi)
	printHeader([]string{"ParcelID", "Owner", "District", "Acres", "Flag"})
	for _, a := range parcels {
		printRow([]string{
			asStr(a["PARCEL_ID"]),
			asStr(a["OWNER_NAME"]),
			asStr(a["DISTRICT"]),
			asStr(a["ACREAGE"]),
			mineralFlag(asStr(a["OWNER_NAME"])),
		})
	}
	return nil
}

// mineralFlag returns the first matching owner-pattern flag.
func mineralFlag(owner string) string {
	o := strings.ToUpper(owner)
	patterns := []string{"HEIRS", "ET AL", "ENERGY", "MINERAL", "RESOURCES", "OIL", "GAS"}
	for _, p := range patterns {
		if strings.Contains(o, p) {
			return p
		}
	}
	return "-"
}

// --- OH adapter -------------------------------------------------------------

func runOH(county string, luc string, limit int, wantWells bool, radiusMi float64, dormant bool) error {
	// Build LUC clause
	var lucClause string
	if strings.Contains(luc, ",") {
		list := strings.Split(luc, ",")
		quoted := make([]string, 0, len(list))
		for _, c := range list {
			quoted = append(quoted, fmt.Sprintf("'%s'", strings.TrimSpace(c)))
		}
		lucClause = fmt.Sprintf("StateLUC IN (%s)", strings.Join(quoted, ","))
	} else {
		lucClause = fmt.Sprintf("StateLUC LIKE '%s'", luc)
	}

	where := fmt.Sprintf("County='%s' AND %s", strings.ToUpper(county), lucClause)

	p := url.Values{}
	p.Set("where", where)
	p.Set("outFields", "StateParcelID,LocalParcelID,County,StateLUC,MailAddressAll,LandArea,CAMADataSite")
	p.Set("resultRecordCount", fmt.Sprintf("%d", limit))
	p.Set("returnGeometry", boolStr(wantWells || dormant))
	if wantWells || dormant {
		p.Set("outSR", "4326")
	}
	r, err := postQuery(stdClient, ohOgripURL, p)
	if err != nil {
		return err
	}

	fmt.Printf("\n[OH] %d parcels (where: %s)\n", len(r.Features), where)
	printHeader([]string{"ParcelID", "LUC", "Acres", "Mail", "Wells", "LastProd"})

	for _, f := range r.Features {
		a := f.Attributes
		acres := asFloat(a["LandArea"]) / 43560.0
		wellCount := "-"
		lastProd := "-"
		if (wantWells || dormant) && f.Geometry != nil {
			n, lp, _ := ohNearbyWells(f.Geometry.X, f.Geometry.Y, radiusMi, dormant)
			wellCount = fmt.Sprintf("%d", n)
			if lp > 0 {
				lastProd = fmt.Sprintf("%d", lp)
			}
		}
		printRow([]string{
			asStr(a["LocalParcelID"]),
			asStr(a["StateLUC"]),
			fmt.Sprintf("%.1f", acres),
			asStr(a["MailAddressAll"]),
			wellCount,
			lastProd,
		})
	}
	return nil
}

func ohNearbyWells(lon, lat, radiusMi float64, dormant bool) (int, int, error) {
	p := url.Values{}
	p.Set("geometry", fmt.Sprintf("%f,%f", lon, lat))
	p.Set("geometryType", "esriGeometryPoint")
	p.Set("inSR", "4326")
	p.Set("spatialRel", "esriSpatialRelIntersects")
	radius := radiusMi
	if dormant && radius < 2.0 {
		radius = 2.0
	}
	p.Set("distance", fmt.Sprintf("%f", radius*1609.34))
	p.Set("units", "esriSRUnit_Meter")
	if !dormant {
		p.Set("where", "WL_STATUS_DESC='Producing'")
	}
	p.Set("outFields", "API_WELLNO,WL_STATUS_DESC,CO_NAME,ProducingFormation1,Last_Nonzero_Production_Year")
	p.Set("returnGeometry", "false")
	p.Set("resultRecordCount", "50")
	r, err := postQuery(stdClient, ohOdnrURL, p)
	if err != nil {
		return 0, 0, err
	}
	maxYear := 0
	for _, f := range r.Features {
		if y := int(asFloat(f.Attributes["Last_Nonzero_Production_Year"])); y > maxYear {
			maxYear = y
		}
	}
	return len(r.Features), maxYear, nil
}

// --- Helpers ----------------------------------------------------------------

func boolStr(b bool) string {
	if b {
		return "true"
	}
	return "false"
}

func asStr(v any) string {
	if v == nil {
		return ""
	}
	switch t := v.(type) {
	case string:
		return t
	case float64:
		if t == float64(int64(t)) {
			return fmt.Sprintf("%d", int64(t))
		}
		return fmt.Sprintf("%.2f", t)
	default:
		return fmt.Sprintf("%v", v)
	}
}

func asFloat(v any) float64 {
	switch t := v.(type) {
	case float64:
		return t
	case int:
		return float64(t)
	case int64:
		return float64(t)
	default:
		return 0
	}
}

func printHeader(cols []string) {
	fmt.Println(strings.Join(cols, " | "))
	sep := make([]string, len(cols))
	for i, c := range cols {
		sep[i] = strings.Repeat("-", len(c))
	}
	fmt.Println(strings.Join(sep, "-+-"))
}

func printRow(cols []string) {
	trimmed := make([]string, len(cols))
	for i, c := range cols {
		if len(c) > 40 {
			c = c[:40]
		}
		trimmed[i] = c
	}
	fmt.Println(strings.Join(trimmed, " | "))
}

// --- Main -------------------------------------------------------------------

func main() {
	state := flag.String("state", "", "State adapter: wv | pa | oh")
	county := flag.String("county", "", "County name (WV: 'Tyler', PA: 'Greene', OH: 'BELMONT')")
	status := flag.String("status", "", "[WV] Delinquent status filter (default: No Bid and Deed)")
	keyword := flag.String("keyword", "MINERAL", "[WV] Legal description keyword (default MINERAL)")
	luc := flag.String("luc", "2%", "[OH] StateLUC filter: '240,250' or '2%' (default 2%)")
	limit := flag.Int("limit", 20, "Max parcels to return")
	wells := flag.Bool("wells", false, "Enable spatial well correlation")
	radius := flag.Float64("radius", 1.0, "Well search radius in miles (default 1.0)")
	dormant := flag.Bool("dormant", false, "[OH] Run dormant-mineral screen (2-mile buffer, all statuses)")
	flag.Parse()

	if *state == "" {
		fmt.Fprintln(os.Stderr, "usage: --state wv|pa|oh --county <name> [options]")
		os.Exit(2)
	}

	var err error
	switch strings.ToLower(*state) {
	case "wv":
		err = runWV(*county, *status, *keyword, *limit, *wells, *radius)
	case "pa":
		err = runPA(*county, *limit, *wells, *radius)
	case "oh":
		err = runOH(*county, *luc, *limit, *wells, *radius, *dormant)
	default:
		err = fmt.Errorf("unknown state %q (expected wv|pa|oh)", *state)
	}
	if err != nil {
		fmt.Fprintf(os.Stderr, "error: %v\n", err)
		os.Exit(1)
	}
}
