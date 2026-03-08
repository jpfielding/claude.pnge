# PA DEP Well Data — API Reference

Two primary data sources:
1. **PA Open Data Portal (Socrata)** — primary, JSON/CSV, SoQL query language
2. **PA DEP ArcGIS REST MapServer** — spatial queries, GIS format

No API key required for either. App token for Socrata improves rate limits.

---

## Source 1: PA Open Data — Socrata Endpoints

### Endpoints

| Dataset | URL | Coverage |
|---------|-----|----------|
| Unconventional Wells | `https://data.pa.gov/resource/nfax-tpjr.json` | Marcellus, Utica, horizontal wells, 2008–present |
| Conventional Wells | `https://data.pa.gov/resource/e3er-typed.json` | Vertical oil/gas wells, historical |
| Inspection Reports | `https://data.pa.gov/resource/p3vr-3mxx.json` | DEP inspection data |
| Violations | `https://data.pa.gov/resource/h4rb-97ew.json` | Compliance violations |

For CSV output, replace `.json` with `.csv` in the URL.

---

## Socrata SoQL Query Language

Append SoQL parameters to the endpoint URL. All parameters begin with `$`.

### Core Clauses

| Clause | SQL Equivalent | Description | Example |
|--------|---------------|-------------|---------|
| `$where` | WHERE | Filter rows | `$where=county_name='BRADFORD'` |
| `$select` | SELECT | Choose columns, aggregations | `$select=operator_name,count(*)` |
| `$group` | GROUP BY | Aggregate grouping | `$group=county_name` |
| `$order` | ORDER BY | Sort results | `$order=spud_date DESC` |
| `$limit` | LIMIT | Max rows returned (default 1000, max 50000) | `$limit=5000` |
| `$offset` | OFFSET | Pagination start | `$offset=5000` |
| `$q` | Full-text | Full-text search | `$q=EQT+Marcellus` |

### $where Operators

| Operator | Description | Example |
|----------|-------------|---------|
| `=` | Exact match | `county_name='SUSQUEHANNA'` |
| `!=` | Not equal | `well_status!='Plugged'` |
| `>`, `<`, `>=`, `<=` | Comparison | `spud_date>'2022-01-01'` |
| `like '%X%'` | Substring match | `operator_name like '%EQT%'` |
| `IS NULL` | Field is empty | `spud_date IS NULL` |
| `IS NOT NULL` | Field has value | `latitude IS NOT NULL` |
| `AND` | Both conditions | `county_name='BRADFORD' AND well_status='Active'` |
| `OR` | Either condition | `county_name='BRADFORD' OR county_name='TIOGA'` |
| `IN (...)` | Match any | `county_name IN ('BRADFORD','TIOGA','SUSQUEHANNA')` |
| `BETWEEN x AND y` | Range (dates, numbers) | `spud_date BETWEEN '2020-01-01' AND '2023-12-31'` |

**Important:** String values in `$where` require single quotes. County names
are stored UPPERCASE. URL-encode special characters or use `--data-urlencode`.

### Date Format

Use ISO 8601 format: `'2024-01-01T00:00:00'` or just `'2024-01-01'`.

### Aggregation Functions

| Function | Description |
|----------|-------------|
| `count(*)` | Row count |
| `sum(field)` | Sum of numeric field |
| `avg(field)` | Average of numeric field |
| `max(field)` | Maximum value |
| `min(field)` | Minimum value |

Use with `$select` and `$group`:
```
$select=county_name,count(*)&$group=county_name&$order=count+DESC
```

---

## Unconventional Well Dataset (nfax-tpjr)

### All Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `api_number` | string | API well identifier | `37-115-20001-00-00` |
| `permit_number` | string | PA DEP permit number | `115-20001` |
| `well_name` | string | Well name | `SMITH 1H` |
| `operator_name` | string | Operator company name | `CABOT OIL AND GAS CORP` |
| `county_name` | string | County (UPPERCASE) | `SUSQUEHANNA` |
| `county_code` | string | 2-3 digit code | `115` |
| `municipality_name` | string | Township or borough | `AUBURN TOWNSHIP` |
| `municipality_type` | string | Township/Borough/City | `Township` |
| `latitude` | float | Surface location latitude | `41.8712` |
| `longitude` | float | Surface location longitude | `-76.1234` |
| `spud_date` | date | Date drilling began | `2022-03-15` |
| `permit_issue_date` | date | Permit issue date | `2022-01-10` |
| `permit_expiration_date` | date | Permit expiration | `2024-01-10` |
| `well_status` | string | Current status | `Active` |
| `well_type` | string | Type descriptor | `Unconventional` |
| `unconventional_well_ind` | string | Y/N flag | `Y` |
| `primary_target_formation` | string | Target formation | `MARCELLUS` |
| `tvd` | float | True vertical depth (ft) | `7200.0` |
| `total_depth` | float | Measured total depth (ft) | `12500.0` |
| `horizontal_length` | float | Lateral length (ft) | `5200.0` |
| `surface_longitude` | float | Same as longitude | — |
| `surface_latitude` | float | Same as latitude | — |
| `operator_id` | string | Operator DEP ID | — |
| `township_code` | string | Internal code | — |

### Well Status Values

| Status | Description |
|--------|-------------|
| `Active` | Currently producing |
| `Inactive` | Not producing but not plugged |
| `Abandoned` | Abandoned (not formally plugged) |
| `Plugged` | Plugged and abandoned |
| `Permitted` | Permitted but not yet spud |
| `Drilling` | Actively drilling |
| `Completed` | Drilled and completed |

### Primary Target Formation Values (Common)

| Value | Formation |
|-------|-----------|
| `MARCELLUS` | Marcellus Shale |
| `UTICA` | Utica Shale |
| `POINT PLEASANT` | Point Pleasant Fm |
| `UPPER DEVONIAN` | Upper Devonian shales |
| `LOCKPORT` | Lockport Dolomite |
| `ONONDAGA` | Onondaga Limestone |

---

## Conventional Well Dataset (e3er-typed)

### Key Fields (Partial — schema differs from unconventional)

| Field | Description |
|-------|-------------|
| `api_number` | API well number |
| `permit_number` | DEP permit number |
| `well_name` | Well name |
| `operator_name` | Operator |
| `county_name` | County (UPPERCASE) |
| `municipality_name` | Township |
| `latitude` | Latitude |
| `longitude` | Longitude |
| `spud_date` | Spud date |
| `well_status` | Status |
| `primary_target_formation` | Target formation |
| `well_type` | Oil / Gas / Dry Hole / etc. |

Note: Many historical conventional wells (pre-1990) may lack coordinates,
spud dates, and formation data.

---

## SoQL Query Examples

```bash
# All active unconventional wells in Bradford County
curl -s "https://data.pa.gov/resource/nfax-tpjr.json?\$where=county_name='BRADFORD'+AND+well_status='Active'&\$limit=200&\$order=spud_date+DESC"

# Count wells by county statewide
curl -s "https://data.pa.gov/resource/nfax-tpjr.json?\$select=county_name,count(*)&\$group=county_name&\$order=count+DESC&\$limit=67"

# Top 10 operators by permit count
curl -s "https://data.pa.gov/resource/nfax-tpjr.json?\$select=operator_name,count(*)&\$group=operator_name&\$order=count+DESC&\$limit=10"

# Permits issued in 2024
curl -s "https://data.pa.gov/resource/nfax-tpjr.json?\$where=permit_issue_date>='2024-01-01T00:00:00'&\$order=permit_issue_date+DESC&\$limit=500"

# Utica wells with coordinates
curl -s "https://data.pa.gov/resource/nfax-tpjr.json?\$where=primary_target_formation='UTICA'+AND+latitude+IS+NOT+NULL&\$select=api_number,well_name,operator_name,county_name,latitude,longitude,spud_date&\$limit=200"

# Operator substring match (e.g., all Range Resources variants)
curl -s "https://data.pa.gov/resource/nfax-tpjr.json?\$where=operator_name+like+'%25RANGE%25'&\$limit=200&\$order=spud_date+DESC"

# Wells between two dates in multiple counties
curl -s "https://data.pa.gov/resource/nfax-tpjr.json?\$where=county_name+IN+('SUSQUEHANNA','BRADFORD')+AND+spud_date+BETWEEN+'2020-01-01'+AND+'2023-12-31'&\$limit=500"

# Pagination — second page of 1000 results
curl -s "https://data.pa.gov/resource/nfax-tpjr.json?\$where=well_status='Active'&\$limit=1000&\$offset=1000&\$order=api_number+ASC"

# Total count without data (use $select and $limit=1)
curl -s "https://data.pa.gov/resource/nfax-tpjr.json?\$select=count(*)&\$where=county_name='SUSQUEHANNA'"
```

### Shell-Safe URL Encoding

When using `$` characters in shell, escape them or use `--data-urlencode`:

```bash
# Option 1: Escape $ signs
curl -s "https://data.pa.gov/resource/nfax-tpjr.json?\$where=county_name='BRADFORD'"

# Option 2: Use --get and --data-urlencode
curl -s --get "https://data.pa.gov/resource/nfax-tpjr.json" \
  --data-urlencode "\$where=county_name='BRADFORD'" \
  --data-urlencode "\$limit=100" \
  --data-urlencode "\$order=spud_date DESC"
```

---

## Socrata App Token (Optional)

Register a free app token at https://data.pa.gov/ to avoid throttling.
Pass as a header:

```bash
curl -s "https://data.pa.gov/resource/nfax-tpjr.json?..." \
  -H "X-App-Token: YOUR_APP_TOKEN"
```

Without an app token: ~2 requests/second.
With an app token: higher limits (officially 1000/hour, often more in practice).

---

## Source 2: PA DEP ArcGIS REST MapServer

Use for spatial (bounding box) queries and when you need GIS-native data.

**Base URL:** `https://gis.dep.pa.gov/arcgis/rest/services/DEP_Public/OilGas/MapServer`

### Get Layer List

```bash
curl -s "https://gis.dep.pa.gov/arcgis/rest/services/DEP_Public/OilGas/MapServer?f=json" \
  | jq '.layers[] | {id, name}'
```

### ArcGIS REST Query Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `where` | SQL WHERE clause | `where=COUNTY_CODE='115'` |
| `geometry` | Bounding box (minx,miny,maxx,maxy) | `geometry=-76.5,41.5,-76.0,42.0` |
| `geometryType` | Geometry type | `geometryType=esriGeometryEnvelope` |
| `spatialRel` | Spatial relationship | `spatialRel=esriSpatialRelIntersects` |
| `outFields` | Fields to return | `outFields=*` or `outFields=WELL_NAME,OPERATOR` |
| `resultRecordCount` | Max records | `resultRecordCount=1000` |
| `resultOffset` | Pagination offset | `resultOffset=1000` |
| `f` | Response format | `f=json` or `f=geojson` |

### Bounding Box Spatial Query Examples

```bash
# Wells in southwestern PA (Washington + Greene counties area)
# Bbox: west=-80.5, south=39.7, east=-79.5, north=40.2
curl -s "https://gis.dep.pa.gov/arcgis/rest/services/DEP_Public/OilGas/MapServer/0/query" \
  --data-urlencode "geometry=-80.5,39.7,-79.5,40.2" \
  --data-urlencode "geometryType=esriGeometryEnvelope" \
  --data-urlencode "spatialRel=esriSpatialRelIntersects" \
  --data-urlencode "outFields=*" \
  --data-urlencode "resultRecordCount=200" \
  --data-urlencode "f=json" \
  | jq '.features[].attributes | {WELL_NAME, OPERATOR_NAME, COUNTY, SPUD_DATE}'

# Attribute-only query (no spatial filter)
curl -s "https://gis.dep.pa.gov/arcgis/rest/services/DEP_Public/OilGas/MapServer/0/query" \
  --data-urlencode "where=COUNTY_CODE='115'" \
  --data-urlencode "outFields=WELL_NAME,OPERATOR_NAME,SPUD_DATE,WELL_STATUS" \
  --data-urlencode "resultRecordCount=100" \
  --data-urlencode "f=json"

# GeoJSON output (includes geometry for mapping)
curl -s "https://gis.dep.pa.gov/arcgis/rest/services/DEP_Public/OilGas/MapServer/0/query" \
  --data-urlencode "where=WELL_STATUS='Active'" \
  --data-urlencode "outFields=WELL_NAME,OPERATOR_NAME" \
  --data-urlencode "resultRecordCount=50" \
  --data-urlencode "f=geojson"
```

---

## County Reference (All PA Counties)

County names must be UPPERCASE in Socrata $where clauses.

### Major Marcellus/Utica Counties

| County | FIPS Code | Socrata Name | Notes |
|--------|-----------|--------------|-------|
| Susquehanna | 115 | `SUSQUEHANNA` | Highest unconventional well count |
| Bradford | 015 | `BRADFORD` | Major Marcellus area, northern tier |
| Tioga | 117 | `TIOGA` | Northern Marcellus |
| Lycoming | 081 | `LYCOMING` | Active Marcellus area |
| Clinton | 035 | `CLINTON` | Marcellus activity |
| Centre | 027 | `CENTRE` | Central PA, Marcellus |
| Clearfield | 033 | `CLEARFIELD` | Marcellus |
| Washington | 125 | `WASHINGTON` | SW PA, Marcellus + Utica |
| Greene | 059 | `GREENE` | SW PA, deep Utica target |
| Westmoreland | 129 | `WESTMORELAND` | SW PA transition |
| Fayette | 051 | `FAYETTE` | SW PA |
| Butler | 019 | `BUTLER` | SW PA |
| Beaver | 007 | `BEAVER` | SW PA |
| Lawrence | 073 | `LAWRENCE` | SW PA corner |
| Mercer | 085 | `MERCER` | NW PA |
| Venango | 121 | `VENANGO` | NW PA, historic oil |
| McKean | 083 | `MCKEAN` | NW PA |
| Warren | 123 | `WARREN` | NW PA |
| Forest | 053 | `FOREST` | NW PA |

### Querying Multiple Counties

```bash
# Susquehanna + Bradford combined
curl -s "https://data.pa.gov/resource/nfax-tpjr.json?\$where=county_name+IN+('SUSQUEHANNA','BRADFORD')&\$limit=500"
```

---

## Operator Name Patterns

Operators are stored as submitted to DEP and may include corporate variants.
Use `like '%TERM%'` for robust matching:

| Operator Group | Search Pattern |
|----------------|---------------|
| EQT | `like '%EQT%'` |
| Cabot / Coterra | `like '%CABOT%'` or `like '%COTERRA%'` |
| Southwestern Energy | `like '%SOUTHWESTERN%'` |
| Range Resources | `like '%RANGE%'` |
| Chesapeake Energy | `like '%CHESAPEAKE%'` |
| CNX Gas | `like '%CNX%'` |
| Repsol | `like '%REPSOL%'` |
| Seneca Resources | `like '%SENECA%'` |
| WPX Energy (now Devon) | `like '%WPX%'` |
| Chief Oil and Gas | `like '%CHIEF%'` |

---

## Go Example: Query Unconventional Wells

```go
package main

import (
    "encoding/json"
    "fmt"
    "io"
    "net/http"
    "net/url"
    "strings"
    "time"
)

const socrataBase = "https://data.pa.gov/resource/nfax-tpjr.json"

type UnconventionalWell struct {
    APINumber              string `json:"api_number"`
    PermitNumber           string `json:"permit_number"`
    WellName               string `json:"well_name"`
    OperatorName           string `json:"operator_name"`
    CountyName             string `json:"county_name"`
    MunicipalityName       string `json:"municipality_name"`
    Latitude               string `json:"latitude"`
    Longitude              string `json:"longitude"`
    SpudDate               string `json:"spud_date"`
    PermitIssueDate        string `json:"permit_issue_date"`
    WellStatus             string `json:"well_status"`
    PrimaryTargetFormation string `json:"primary_target_formation"`
    TVD                    string `json:"tvd"`
    HorizontalLength       string `json:"horizontal_length"`
}

type QueryOpts struct {
    County    string
    Operator  string
    Formation string
    Status    string
    After     time.Time
    Limit     int
    Offset    int
}

func buildWhere(opts QueryOpts) string {
    clauses := []string{}

    if opts.County != "" {
        clauses = append(clauses,
            fmt.Sprintf("county_name='%s'", strings.ToUpper(opts.County)))
    }
    if opts.Operator != "" {
        clauses = append(clauses,
            fmt.Sprintf("operator_name like '%%%s%%'", strings.ToUpper(opts.Operator)))
    }
    if opts.Formation != "" {
        clauses = append(clauses,
            fmt.Sprintf("primary_target_formation='%s'", strings.ToUpper(opts.Formation)))
    }
    if opts.Status != "" {
        clauses = append(clauses,
            fmt.Sprintf("well_status='%s'", opts.Status))
    }
    if !opts.After.IsZero() {
        clauses = append(clauses,
            fmt.Sprintf("spud_date>'%s'", opts.After.Format("2006-01-02")))
    }

    if len(clauses) == 0 {
        return "1=1"
    }
    return strings.Join(clauses, " AND ")
}

func queryWells(opts QueryOpts) ([]UnconventionalWell, error) {
    limit := opts.Limit
    if limit == 0 {
        limit = 100
    }

    params := url.Values{}
    params.Set("$where", buildWhere(opts))
    params.Set("$limit", fmt.Sprintf("%d", limit))
    params.Set("$order", "spud_date DESC")
    if opts.Offset > 0 {
        params.Set("$offset", fmt.Sprintf("%d", opts.Offset))
    }

    apiURL := socrataBase + "?" + params.Encode()

    resp, err := http.Get(apiURL)
    if err != nil {
        return nil, fmt.Errorf("HTTP request failed: %w", err)
    }
    defer resp.Body.Close()

    if resp.StatusCode != http.StatusOK {
        body, _ := io.ReadAll(resp.Body)
        return nil, fmt.Errorf("HTTP %d: %s", resp.StatusCode, string(body))
    }

    body, err := io.ReadAll(resp.Body)
    if err != nil {
        return nil, fmt.Errorf("reading response: %w", err)
    }

    var wells []UnconventionalWell
    if err := json.Unmarshal(body, &wells); err != nil {
        return nil, fmt.Errorf("parsing JSON: %w", err)
    }

    return wells, nil
}

func main() {
    // Query: Active Marcellus wells in Susquehanna County
    wells, err := queryWells(QueryOpts{
        County:    "SUSQUEHANNA",
        Formation: "MARCELLUS",
        Status:    "Active",
        Limit:     50,
    })
    if err != nil {
        fmt.Printf("Error: %v\n", err)
        return
    }

    fmt.Printf("Found %d wells\n\n", len(wells))
    fmt.Printf("%-20s %-30s %-15s %-12s %-10s\n",
        "API Number", "Operator", "Municipality", "Spud Date", "Status")
    fmt.Println(strings.Repeat("-", 90))

    for _, w := range wells {
        spud := w.SpudDate
        if len(spud) > 10 {
            spud = spud[:10]
        }
        muni := w.MunicipalityName
        if len(muni) > 14 {
            muni = muni[:11] + "..."
        }
        op := w.OperatorName
        if len(op) > 29 {
            op = op[:26] + "..."
        }
        fmt.Printf("%-20s %-30s %-15s %-12s %-10s\n",
            w.APINumber, op, muni, spud, w.WellStatus)
    }
}
```

---

## Pagination Strategy

The Socrata API returns up to 50,000 rows per request. For large result sets,
paginate with `$offset`:

```bash
# Page 1 (rows 0–999)
curl -s "https://data.pa.gov/resource/nfax-tpjr.json?\$where=county_name='BRADFORD'&\$limit=1000&\$offset=0&\$order=api_number+ASC"

# Page 2 (rows 1000–1999)
curl -s "https://data.pa.gov/resource/nfax-tpjr.json?\$where=county_name='BRADFORD'&\$limit=1000&\$offset=1000&\$order=api_number+ASC"
```

Always include `$order` when paginating to ensure consistent row ordering.
Get total count first with `$select=count(*)` to know how many pages to fetch.

---

## Related PA DEP Resources

| Resource | URL | Notes |
|----------|-----|-------|
| DEP PADEP eFACTS | https://efacts.dep.pa.gov/ | Well file lookup by API/permit |
| PADEP Well Inspector | https://www.depgis.state.pa.us/efacts/ | Web-based well data viewer |
| PA Geological Survey | https://www.dcnr.pa.gov/Conservation/GeologicalSurvey/ | Formation data |
| SRBC (Susquehanna River Basin Commission) | https://www.srbc.net/ | Water withdrawal permits |
| PA DCNR eBird/eMap | https://www.dcnr.pa.gov/ | Surface ownership, state lands |
