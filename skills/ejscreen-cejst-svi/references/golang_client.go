// Package ejscreencejstsvi is a unified Go client that screens a U.S.
// location against EPA EJScreen (block-group percentiles), CEJST
// (tract-level disadvantaged flag), and CDC/ATSDR SVI (tract-level
// themes). Designed for PNGE siting and permitting workflows.
//
// Usage:
//
//	c, _ := ejscreencejstsvi.New(ejscreencejstsvi.Options{
//	    CEJSTCSVPath: "/Users/you/.cache/ejscreen-cejst-svi/cejst_1.0_communities.csv",
//	})
//	res, err := c.Screen(context.Background(), 39.6295, -79.9559)
//
// No API keys required. All three services are public.
package ejscreencejstsvi

import (
	"context"
	"encoding/csv"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"net/url"
	"os"
	"strconv"
	"strings"
	"time"
)

// Endpoints. These are mirrors; EPA's own ejscreen.epa.gov was removed
// in early 2025. Override via Options if they shift again.
const (
	defaultCensusGeocoderURL = "https://geocoding.geo.census.gov/geocoder/geographies/coordinates"
	defaultEJScreenURL       = "https://services.arcgis.com/cJ9YHowT8TU7DUyn/arcgis/rest/services/EJScreen_2024_Public/FeatureServer/0/query"
	defaultSVIURL            = "https://services3.arcgis.com/1IjeLYkadeVrSHSJ/ArcGIS/rest/services/CDC_ATSDR_SVI_2022_US_tract/FeatureServer/0/query"
	defaultCEJSTCSVURL       = "https://static-data-screeningtool.geoplatform.gov/data-versions/1.0/data/score/downloadable/1.0-communities.csv"
)

// Options configures a Client. All fields are optional.
type Options struct {
	HTTPClient       *http.Client
	CensusGeocoderURL string
	EJScreenURL      string
	SVIURL           string
	CEJSTCSVURL      string
	CEJSTCSVPath     string // local cache; if empty, streams from URL each call (slow)
}

// Client is a unified EJ/vulnerability screening client.
type Client struct {
	http     *http.Client
	geoURL   string
	ejURL    string
	sviURL   string
	cejstURL string
	cejst    map[string]CEJSTRecord // tract GEOID → record; loaded lazily
}

// New returns a Client with sane defaults.
func New(opts Options) (*Client, error) {
	c := &Client{
		http:     opts.HTTPClient,
		geoURL:   firstNonEmpty(opts.CensusGeocoderURL, defaultCensusGeocoderURL),
		ejURL:    firstNonEmpty(opts.EJScreenURL, defaultEJScreenURL),
		sviURL:   firstNonEmpty(opts.SVIURL, defaultSVIURL),
		cejstURL: firstNonEmpty(opts.CEJSTCSVURL, defaultCEJSTCSVURL),
	}
	if c.http == nil {
		c.http = &http.Client{Timeout: 60 * time.Second}
	}
	if opts.CEJSTCSVPath != "" {
		m, err := loadCEJSTCSV(opts.CEJSTCSVPath)
		if err != nil {
			return nil, fmt.Errorf("load CEJST CSV: %w", err)
		}
		c.cejst = m
	}
	return c, nil
}

// ScreenResult is the combined output for a single location.
type ScreenResult struct {
	Lat, Lon      float64
	BlockGroupID  string // 12-digit
	TractID       string // 11-digit
	StateFIPS     string
	CountyName    string
	StateAbbrev   string

	EJScreen *EJScreenRecord
	CEJST    *CEJSTRecord
	SVI      *SVIRecord

	RiskCategory string // LOW / MODERATE / ELEVATED / HIGH
	Reasons      []string
}

// EJScreenRecord is a subset of the EJScreen 2024 block-group fields we
// surface by default. Extend as needed.
type EJScreenRecord struct {
	GEOID     string  `json:"ID"`
	TotalPop  int     `json:"ACSTOTPOP"`
	MinorPct  float64 `json:"MINORPCT"`
	LowIncPct float64 `json:"LOWINCPCT"`

	// Raw environmental indicators
	PM25   float64 `json:"PM25"`
	Ozone  float64 `json:"OZONE"`
	DslPM  float64 `json:"DSLPM"`
	Cancer float64 `json:"CANCER"`
	Resp   float64 `json:"RESP"`
	Ptraf  float64 `json:"PTRAF"`
	Lead   float64 `json:"PRE1960PCT"`
	Pnpl   float64 `json:"PNPL"`
	Prmp   float64 `json:"PRMP"`
	Ptsdf  float64 `json:"PTSDF"`
	Pwdis  float64 `json:"PWDIS"`
	UST    float64 `json:"UST"`

	// State percentiles for the EJ Indexes. Higher = more burdened
	// relative to the state.
	EJIndexPctl map[string]float64 `json:"-"`
}

// CEJSTRecord is a subset of the v1.0 communities CSV.
type CEJSTRecord struct {
	TractGEOID   string // 11-digit
	State        string
	County       string
	Disadvantaged bool

	Climate       bool
	Energy        bool
	Health        bool
	Housing       bool
	LegacyPoll    bool
	Transport     bool
	WaterWW       bool
	Workforce     bool
}

// SVIRecord is the tract-level SVI 2022 summary.
type SVIRecord struct {
	FIPS         string  // 11-digit tract
	Location     string
	TotalPop     int
	RPLThemes    float64 // overall
	RPLTheme1    float64 // socioeconomic
	RPLTheme2    float64 // household characteristics
	RPLTheme3    float64 // minority / language
	RPLTheme4    float64 // housing / transportation
	FTotal       int     // count of 90th-pctl flags (0–16)
}

// Screen runs the full pipeline for a single lat/lon.
func (c *Client) Screen(ctx context.Context, lat, lon float64) (*ScreenResult, error) {
	res := &ScreenResult{Lat: lat, Lon: lon}

	// 1. Resolve geography via Census Geocoder
	bgID, tractID, state, county, err := c.resolveGeography(ctx, lat, lon)
	if err != nil {
		return nil, fmt.Errorf("resolve geography: %w", err)
	}
	res.BlockGroupID = bgID
	res.TractID = tractID
	res.StateAbbrev = state
	res.CountyName = county

	// 2. EJScreen (tolerant — mirrors occasionally flaky)
	if ej, err := c.fetchEJScreen(ctx, bgID, lat, lon); err == nil {
		res.EJScreen = ej
	}

	// 3. CEJST (lazy-load the CSV on first call if not pre-loaded)
	if c.cejst == nil && c.cejstURL != "" {
		if err := c.downloadCEJST(ctx); err != nil {
			// non-fatal
			fmt.Fprintf(os.Stderr, "cejst download failed: %v\n", err)
		}
	}
	if rec, ok := c.cejst[tractID]; ok {
		res.CEJST = &rec
	}

	// 4. SVI
	if svi, err := c.fetchSVI(ctx, tractID, lat, lon); err == nil {
		res.SVI = svi
	}

	// 5. Classify
	res.RiskCategory, res.Reasons = classify(res)

	return res, nil
}

// --------------------------- Geography ---------------------------

type censusGeoResp struct {
	Result struct {
		Geographies map[string][]map[string]interface{} `json:"geographies"`
	} `json:"result"`
}

func (c *Client) resolveGeography(ctx context.Context, lat, lon float64) (bg, tract, state, county string, err error) {
	q := url.Values{}
	q.Set("x", strconv.FormatFloat(lon, 'f', 6, 64))
	q.Set("y", strconv.FormatFloat(lat, 'f', 6, 64))
	q.Set("benchmark", "Public_AR_Current")
	q.Set("vintage", "Current_Current")
	q.Set("layers", "Census Block Groups,Census Tracts,Counties,States")
	q.Set("format", "json")

	req, _ := http.NewRequestWithContext(ctx, "GET", c.geoURL+"?"+q.Encode(), nil)
	resp, err := c.http.Do(req)
	if err != nil {
		return "", "", "", "", err
	}
	defer resp.Body.Close()
	if resp.StatusCode != 200 {
		return "", "", "", "", fmt.Errorf("geocoder HTTP %d", resp.StatusCode)
	}

	var cr censusGeoResp
	if err := json.NewDecoder(resp.Body).Decode(&cr); err != nil {
		return "", "", "", "", err
	}
	pick := func(layer string) map[string]interface{} {
		if xs := cr.Result.Geographies[layer]; len(xs) > 0 {
			return xs[0]
		}
		return nil
	}
	if m := pick("Census Block Groups"); m != nil {
		bg = asString(m["GEOID"])
	}
	if m := pick("Census Tracts"); m != nil {
		tract = asString(m["GEOID"])
	}
	if m := pick("Counties"); m != nil {
		county = asString(m["NAME"])
	}
	if m := pick("States"); m != nil {
		state = asString(m["STUSAB"])
	}
	if bg == "" || tract == "" {
		return "", "", "", "", fmt.Errorf("no census geography for lat=%.5f lon=%.5f (outside US?)", lat, lon)
	}
	return bg, tract, state, county, nil
}

// --------------------------- EJScreen ---------------------------

type arcGISResp struct {
	Features []struct {
		Attributes map[string]interface{} `json:"attributes"`
	} `json:"features"`
	Error *struct {
		Code    int    `json:"code"`
		Message string `json:"message"`
	} `json:"error"`
}

func (c *Client) fetchEJScreen(ctx context.Context, bgID string, lat, lon float64) (*EJScreenRecord, error) {
	// Try attribute query first, fall back to spatial.
	attrs, err := arcGISAttrQuery(ctx, c.http, c.ejURL, fmt.Sprintf("ID='%s'", bgID), "*")
	if err != nil || attrs == nil {
		attrs, err = arcGISPointQuery(ctx, c.http, c.ejURL, lat, lon, "*")
		if err != nil {
			return nil, err
		}
	}
	if attrs == nil {
		return nil, fmt.Errorf("no EJScreen feature for bg=%s", bgID)
	}

	ej := &EJScreenRecord{
		GEOID:       asString(attrs["ID"]),
		TotalPop:    int(asFloat(attrs["ACSTOTPOP"])),
		MinorPct:    asFloat(attrs["MINORPCT"]),
		LowIncPct:   asFloat(attrs["LOWINCPCT"]),
		PM25:        asFloat(attrs["PM25"]),
		Ozone:       asFloat(attrs["OZONE"]),
		DslPM:       asFloat(attrs["DSLPM"]),
		Cancer:      asFloat(attrs["CANCER"]),
		Resp:        asFloat(attrs["RESP"]),
		Ptraf:       asFloat(attrs["PTRAF"]),
		Lead:        asFloat(attrs["PRE1960PCT"]),
		Pnpl:        asFloat(attrs["PNPL"]),
		Prmp:        asFloat(attrs["PRMP"]),
		Ptsdf:       asFloat(attrs["PTSDF"]),
		Pwdis:       asFloat(attrs["PWDIS"]),
		UST:         asFloat(attrs["UST"]),
		EJIndexPctl: map[string]float64{},
	}
	for _, k := range []string{"EJINDEX_PM25", "EJINDEX_OZONE", "EJINDEX_DSLPM",
		"EJINDEX_CANCER", "EJINDEX_RESP", "EJINDEX_PTRAF", "EJINDEX_LEAD",
		"EJINDEX_PNPL", "EJINDEX_PRMP", "EJINDEX_PTSDF", "EJINDEX_PWDIS", "EJINDEX_UST"} {
		// State-percentile variants are sometimes exposed with a P_ or _ST suffix
		for _, candidate := range []string{"P_" + k + "_ST", k + "_ST", "P_" + k, k} {
			if v, ok := attrs[candidate]; ok && v != nil {
				ej.EJIndexPctl[k] = asFloat(v)
				break
			}
		}
	}
	return ej, nil
}

// --------------------------- SVI ---------------------------

func (c *Client) fetchSVI(ctx context.Context, tractID string, lat, lon float64) (*SVIRecord, error) {
	attrs, err := arcGISAttrQuery(ctx, c.http, c.sviURL, fmt.Sprintf("FIPS='%s'", tractID), "*")
	if err != nil || attrs == nil {
		attrs, err = arcGISPointQuery(ctx, c.http, c.sviURL, lat, lon, "*")
		if err != nil {
			return nil, err
		}
	}
	if attrs == nil {
		return nil, fmt.Errorf("no SVI feature for tract=%s", tractID)
	}
	return &SVIRecord{
		FIPS:      asString(attrs["FIPS"]),
		Location:  asString(attrs["LOCATION"]),
		TotalPop:  int(asFloat(attrs["E_TOTPOP"])),
		RPLThemes: asFloat(attrs["RPL_THEMES"]),
		RPLTheme1: asFloat(attrs["RPL_THEME1"]),
		RPLTheme2: asFloat(attrs["RPL_THEME2"]),
		RPLTheme3: asFloat(attrs["RPL_THEME3"]),
		RPLTheme4: asFloat(attrs["RPL_THEME4"]),
		FTotal:    int(asFloat(attrs["F_TOTAL"])),
	}, nil
}

// --------------------------- CEJST ---------------------------

func (c *Client) downloadCEJST(ctx context.Context) error {
	req, _ := http.NewRequestWithContext(ctx, "GET", c.cejstURL, nil)
	resp, err := c.http.Do(req)
	if err != nil {
		return err
	}
	defer resp.Body.Close()
	if resp.StatusCode != 200 {
		return fmt.Errorf("CEJST HTTP %d", resp.StatusCode)
	}
	return c.parseCEJST(resp.Body)
}

func loadCEJSTCSV(path string) (map[string]CEJSTRecord, error) {
	f, err := os.Open(path)
	if err != nil {
		return nil, err
	}
	defer f.Close()
	c := &Client{}
	if err := c.parseCEJST(f); err != nil {
		return nil, err
	}
	return c.cejst, nil
}

func (c *Client) parseCEJST(r io.Reader) error {
	cr := csv.NewReader(r)
	cr.FieldsPerRecord = -1
	header, err := cr.Read()
	if err != nil {
		return err
	}
	idx := indexByName(header, map[string]string{
		"tract":  "Census tract 2010 ID",
		"state":  "State/Territory",
		"county": "County Name",
		"disadv": "Identified as disadvantaged",
		"clim":   "Greater than or equal to the 90th percentile for expected agriculture loss rate and is low income?",
		"ener":   "Greater than or equal to the 90th percentile for energy burden and is low income?",
		"heal":   "Greater than or equal to the 90th percentile for asthma and is low income?",
		"hous":   "Greater than or equal to the 90th percentile for housing burden and is low income?",
		"lega":   "Greater than or equal to the 90th percentile for proximity to hazardous waste facilities and is low income?",
		"tran":   "Greater than or equal to the 90th percentile for diesel particulate matter and is low income?",
		"wate":   "Greater than or equal to the 90th percentile for wastewater discharge and is low income?",
		"work":   "Linguistic isolation and low median income?",
	})
	m := map[string]CEJSTRecord{}
	for {
		row, err := cr.Read()
		if err == io.EOF {
			break
		}
		if err != nil {
			return err
		}
		rec := CEJSTRecord{
			TractGEOID:    get(row, idx["tract"]),
			State:         get(row, idx["state"]),
			County:        get(row, idx["county"]),
			Disadvantaged: truthy(get(row, idx["disadv"])),
			Climate:       truthy(get(row, idx["clim"])),
			Energy:        truthy(get(row, idx["ener"])),
			Health:        truthy(get(row, idx["heal"])),
			Housing:       truthy(get(row, idx["hous"])),
			LegacyPoll:    truthy(get(row, idx["lega"])),
			Transport:     truthy(get(row, idx["tran"])),
			WaterWW:       truthy(get(row, idx["wate"])),
			Workforce:     truthy(get(row, idx["work"])),
		}
		if rec.TractGEOID != "" {
			// Normalize to 11-digit string with leading zeros.
			if len(rec.TractGEOID) == 10 {
				rec.TractGEOID = "0" + rec.TractGEOID
			}
			m[rec.TractGEOID] = rec
		}
	}
	c.cejst = m
	return nil
}

// --------------------------- Classification ---------------------------

func classify(r *ScreenResult) (string, []string) {
	var reasons []string
	disadvantaged := r.CEJST != nil && r.CEJST.Disadvantaged
	if disadvantaged {
		reasons = append(reasons, "CEJST: census tract flagged as disadvantaged (v1.0)")
	}
	highSVI := r.SVI != nil && r.SVI.RPLThemes >= 0.75
	if highSVI {
		reasons = append(reasons, fmt.Sprintf("SVI: overall percentile %.2f (>=0.75)", r.SVI.RPLThemes))
	}
	ejHits := 0
	if r.EJScreen != nil {
		for k, v := range r.EJScreen.EJIndexPctl {
			if v >= 80 {
				ejHits++
				reasons = append(reasons, fmt.Sprintf("EJScreen: %s state percentile %.0f (>=80)", k, v))
			}
		}
	}
	switch {
	case disadvantaged && highSVI && ejHits >= 3:
		return "HIGH", reasons
	case disadvantaged && (highSVI || ejHits >= 2):
		return "ELEVATED", reasons
	case !disadvantaged && (highSVI || ejHits >= 2):
		return "MODERATE", reasons
	default:
		return "LOW", reasons
	}
}

// --------------------------- Helpers ---------------------------

func arcGISAttrQuery(ctx context.Context, hc *http.Client, endpoint, where, outFields string) (map[string]interface{}, error) {
	q := url.Values{}
	q.Set("where", where)
	q.Set("outFields", outFields)
	q.Set("returnGeometry", "false")
	q.Set("f", "json")
	return arcGIS(ctx, hc, endpoint, q)
}

func arcGISPointQuery(ctx context.Context, hc *http.Client, endpoint string, lat, lon float64, outFields string) (map[string]interface{}, error) {
	q := url.Values{}
	q.Set("geometry", fmt.Sprintf("%f,%f", lon, lat))
	q.Set("geometryType", "esriGeometryPoint")
	q.Set("inSR", "4326")
	q.Set("spatialRel", "esriSpatialRelIntersects")
	q.Set("outFields", outFields)
	q.Set("returnGeometry", "false")
	q.Set("f", "json")
	return arcGIS(ctx, hc, endpoint, q)
}

func arcGIS(ctx context.Context, hc *http.Client, endpoint string, q url.Values) (map[string]interface{}, error) {
	req, _ := http.NewRequestWithContext(ctx, "GET", endpoint+"?"+q.Encode(), nil)
	resp, err := hc.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()
	if resp.StatusCode != 200 {
		return nil, fmt.Errorf("HTTP %d", resp.StatusCode)
	}
	var ar arcGISResp
	if err := json.NewDecoder(resp.Body).Decode(&ar); err != nil {
		return nil, err
	}
	if ar.Error != nil {
		return nil, fmt.Errorf("ArcGIS error %d: %s", ar.Error.Code, ar.Error.Message)
	}
	if len(ar.Features) == 0 {
		return nil, nil
	}
	return ar.Features[0].Attributes, nil
}

func indexByName(header []string, want map[string]string) map[string]int {
	out := map[string]int{}
	for k, name := range want {
		out[k] = -1
		for i, h := range header {
			if strings.EqualFold(strings.TrimSpace(h), strings.TrimSpace(name)) {
				out[k] = i
				break
			}
		}
	}
	return out
}

func get(row []string, i int) string {
	if i < 0 || i >= len(row) {
		return ""
	}
	return row[i]
}

func truthy(s string) bool {
	switch strings.ToLower(strings.TrimSpace(s)) {
	case "true", "1", "yes", "y", "t":
		return true
	}
	return false
}

func asString(v interface{}) string {
	if v == nil {
		return ""
	}
	switch x := v.(type) {
	case string:
		return x
	case float64:
		return strconv.FormatFloat(x, 'f', -1, 64)
	}
	return fmt.Sprintf("%v", v)
}

func asFloat(v interface{}) float64 {
	switch x := v.(type) {
	case nil:
		return 0
	case float64:
		return x
	case string:
		f, _ := strconv.ParseFloat(x, 64)
		return f
	}
	return 0
}

func firstNonEmpty(vals ...string) string {
	for _, v := range vals {
		if v != "" {
			return v
		}
	}
	return ""
}
