# WRI Aqueduct API Reference

Complete reference for the WRI Aqueduct 4.0 ArcGIS REST feature services.

---

## Service Endpoints

### Annual (Primary — use this for most queries)

```
https://services.arcgis.com/LG9Yn2oFqZi5PnO5/arcgis/rest/services/Aqueduct_Annual/FeatureServer/0/query
```

Layer 0 = global watershed polygons with annual risk indicators.

### Monthly (Seasonal detail)

```
https://services.arcgis.com/LG9Yn2oFqZi5PnO5/arcgis/rest/services/Aqueduct_Monthly/FeatureServer/0/query
```

Provides monthly breakdown of baseline water stress and variability. Useful
for understanding seasonal constraints on water availability.

### Flood (Riverine Flood Hazard Detail)

```
https://services.arcgis.com/LG9Yn2oFqZi5PnO5/arcgis/rest/services/Aqueduct_Flood/FeatureServer/0/query
```

More detailed flood risk indicators including urban/rural breakdown and
return period estimates.

### Food/Agriculture (Water risk for agricultural users)

```
https://services.arcgis.com/LG9Yn2oFqZi5PnO5/arcgis/rest/services/Aqueduct_Food/FeatureServer/0/query
```

Crop-level water risk; less relevant for O&G but useful for watershed
context where agriculture is major competing user.

### Service Metadata

```bash
# Get layer definition (all fields, domains, extent)
curl -s "https://services.arcgis.com/LG9Yn2oFqZi5PnO5/arcgis/rest/services/Aqueduct_Annual/FeatureServer/0?f=json" | jq '.fields[] | {name, alias, type}'

# Get all available services
curl -s "https://services.arcgis.com/LG9Yn2oFqZi5PnO5/arcgis/rest/services?f=json" | jq '.services[] | .name'
```

---

## Complete Field Reference — Annual Layer

### Identification Fields

| Field | Type | Description |
|-------|------|-------------|
| OBJECTID | Integer | ArcGIS internal record ID |
| pfaf_id | String | Pfafstetter watershed identifier (6-12 digits) |
| aq_name | String | Aqueduct watershed name |
| name_0 | String | Country name (full official name) |
| name_1 | String | State/Province |
| name_2 | String | County/District (where available) |
| gid_0 | String | Country ISO code |
| gid_1 | String | Province code |

### Risk Indicator Fields

For each indicator prefix below, three fields exist: `{prefix}_cat` (category
integer 0-4 or -1), `{prefix}_label` (text label), and `{prefix}_score`
(continuous score).

| Prefix | Full Name | Data Source |
|--------|-----------|-------------|
| `bws` | Baseline Water Stress | USGS, FAO AQUASTAT water withdrawals / discharge data |
| `bwd` | Baseline Water Depletion | Consumption (no return flow) / discharge |
| `iav` | Interannual Variability | GSCD global streamflow variability |
| `sev` | Seasonal Variability | Within-year coefficient of variation of streamflow |
| `drr` | Drought Risk | PDSI (Palmer Drought Severity Index) frequency/severity |
| `rfr` | Riverine Flood Risk | Global flood model return period analysis |
| `gtd` | Groundwater Table Decline | GRACE satellite gravity anomaly trend |
| `cep` | Coastal Eutrophication Potential | Riverine N+P loads |
| `ucw` | Untreated Connected Wastewater | WHO/UNICEF JMP data |
| `udw` | Unimproved Drinking Water | WHO/UNICEF JMP data |
| `usa` | Unimproved Sanitation | WHO/UNICEF JMP data |
| `rri` | Riverine Flood Risk Integrated | Combines rfr with exposure data |

### Composite Score Fields

| Field | Description |
|-------|-------------|
| `w_awr_def_qan_cat` | Quantity risk composite (bws + bwd + iav + drr + rfr + gtd) |
| `w_awr_def_qal_cat` | Quality risk composite (cep + ucw) |
| `w_awr_def_rrr_cat` | Regulatory and reputational risk composite |
| `w_awr_def_tot_cat` | Overall water risk composite (all pillars combined) |
| `w_awr_def_tot_label` | Overall water risk label |

For most O&G applications, focus on `bws`, `drr`, `rfr`, and `gtd` rather
than the composite scores, as the composites combine indicators that may not
be relevant to industrial water users.

---

## Country Name Reference (Aqueduct country_un values)

Important: Aqueduct uses specific official country name spellings that differ
from common usage. Using the wrong spelling returns an empty feature set.

| Common Usage | Aqueduct country_un |
|--------------|---------------------|
| USA / United States | United States of America |
| UK / Britain | United Kingdom |
| Russia | Russian Federation |
| Iran | Iran (Islamic Republic of) |
| Venezuela | Venezuela (Bolivarian Republic of) |
| Bolivia | Bolivia (Plurinational State of) |
| Syria | Syrian Arab Republic |
| North Korea | Dem. People's Republic of Korea |
| South Korea | Republic of Korea |
| Taiwan | — (not listed separately) |
| Congo (DRC) | Democratic Republic of the Congo |
| Congo (Republic) | Republic of Congo |
| Tanzania | United Republic of Tanzania |
| China | China |
| India | India |
| Brazil | Brazil |
| Australia | Australia |
| Canada | Canada |
| Mexico | Mexico |
| Argentina | Argentina |
| Chile | Chile |

To find the exact country_un value for any country, query with a known
state/province name and check the returned `country_un` value:
```bash
curl -s ".../query" --data-urlencode "where=name_1='Texas'" \
  --data-urlencode "outFields=country_un" \
  --data-urlencode "f=json" --data-urlencode "resultRecordCount=1" | jq '.features[0].attributes'
```

---

## U.S. State Names in Aqueduct

All 50 U.S. states use standard full state names in `name_1`:

Alabama, Alaska, Arizona, Arkansas, California, Colorado, Connecticut,
Delaware, Florida, Georgia, Hawaii, Idaho, Illinois, Indiana, Iowa, Kansas,
Kentucky, Louisiana, Maine, Maryland, Massachusetts, Michigan, Minnesota,
Mississippi, Missouri, Montana, Nebraska, Nevada, New Hampshire, New Jersey,
New Mexico, New York, North Carolina, North Dakota, Ohio, Oklahoma, Oregon,
Pennsylvania, Rhode Island, South Carolina, South Dakota, Tennessee, Texas,
Utah, Vermont, Virginia, Washington, West Virginia, Wisconsin, Wyoming

---

## Query URL Construction

### GET Request (simple queries without apostrophes)

```
GET https://services.arcgis.com/LG9Yn2oFqZi5PnO5/arcgis/rest/services/Aqueduct_Annual/FeatureServer/0/query?
  where=name_1%3D%27Texas%27&
  outFields=name_1,aq_name,bws_cat,bws_label&
  returnGeometry=false&
  f=json&
  resultRecordCount=100
```

### POST Request (recommended for all queries with strings)

```bash
curl -s -X POST \
  "https://services.arcgis.com/LG9Yn2oFqZi5PnO5/arcgis/rest/services/Aqueduct_Annual/FeatureServer/0/query" \
  --data-urlencode "where=country_un='United States of America' AND name_1='Texas'" \
  --data-urlencode "outFields=name_1,aq_name,bws_cat,bws_label,drr_cat,drr_label,rfr_cat,rfr_label,gtd_cat,gtd_label" \
  --data-urlencode "returnGeometry=false" \
  --data-urlencode "orderByFields=bws_cat DESC" \
  --data-urlencode "resultRecordCount=100" \
  --data-urlencode "f=json"
```

### Pagination Example

```bash
# Page 1: records 0-199
curl -s -X POST ".../query" \
  --data-urlencode "where=country_un='United States of America'" \
  --data-urlencode "outFields=name_1,aq_name,bws_cat" \
  --data-urlencode "returnGeometry=false" \
  --data-urlencode "resultRecordCount=200" \
  --data-urlencode "resultOffset=0" \
  --data-urlencode "f=json"

# Page 2: records 200-399
# ... same with resultOffset=200
```

---

## Risk Category Descriptions — Engineering Context

### Baseline Water Stress (bws)

Calculated as: annual water withdrawals / annual renewable freshwater supply.
High values mean a large fraction of available water is already committed to
users (municipal, agricultural, industrial, thermoelectric). Scores above 1.0
are possible when groundwater mining supplements surface water.

**Threshold values:**
- bws < 0.1: Low stress (less than 10% of supply withdrawn)
- bws 0.1-0.2: Low-Medium
- bws 0.2-0.4: Medium-High
- bws 0.4-0.8: High
- bws > 0.8: Extremely High

O&G operations are a minor water user in most basins compared to agriculture
(typically >70% of withdrawals in western U.S.). However, completion water
sourcing can trigger regulatory scrutiny even at small volumes in high-stress
basins because of cumulative impact concerns.

### Drought Risk (drr)

Based on PDSI (Palmer Drought Severity Index) analysis of historical climate
records (GPCC precipitation and CRU temperature data). Measures both
frequency and magnitude of historical droughts.

High drr_cat means the region experiences frequent, severe droughts that can
substantially reduce surface water availability for months at a time. This
affects not just freshwater sourcing but also produced water evaporation pond
permitting (hot/dry conditions create more evaporation room) and cooling water
availability for production facilities.

### Groundwater Table Decline (gtd)

Based on GRACE/GRACE-FO satellite gravity measurement trends (2002-2023). The
GRACE satellites detect changes in total water storage (including groundwater)
by measuring gravitational field anomalies at ~300 km spatial resolution.

Positive gtd_cat (High/Extremely High) means groundwater storage is declining
over time — indicating that withdrawals persistently exceed recharge. This is
directly relevant to:
1. Sourcing completion water from fresh aquifers (accelerates depletion)
2. Disposal wells: regulators in declining aquifer areas may restrict
   injection zones or require monitoring of fresh/saline water interfaces
3. Subsidence risk: major groundwater extraction can cause surface subsidence
   that affects well casing integrity

### Riverine Flood Risk (rfr)

Based on JRC Global Surface Water model and FATHOM Global Flood Hazard. Gives
probability of flood inundation for 1-in-100 and 1-in-500 year return periods.

High rfr_cat means the watershed has frequent flood events with significant
inundation extent. For O&G:
- Produced water containment failure during floods can result in large
  saltwater spills — a major regulatory liability
- Access roads and pipeline river crossings need flood-design standards
- Emergency response plans must include flood scenarios

---

## Go Example — Query and Parse Aqueduct Data

```go
package main

import (
    "encoding/json"
    "fmt"
    "io"
    "net/http"
    "net/url"
    "os"
    "strings"
)

type AqueductResponse struct {
    Features []struct {
        Attributes map[string]interface{} `json:"attributes"`
    } `json:"features"`
    ExceededTransferLimit bool `json:"exceededTransferLimit"`
}

func QueryAqueduct(where, outFields string, maxRecords int) (*AqueductResponse, error) {
    endpoint := "https://services.arcgis.com/LG9Yn2oFqZi5PnO5/arcgis/rest/services/Aqueduct_Annual/FeatureServer/0/query"

    data := url.Values{}
    data.Set("where", where)
    data.Set("outFields", outFields)
    data.Set("returnGeometry", "false")
    data.Set("f", "json")
    data.Set("resultRecordCount", fmt.Sprintf("%d", maxRecords))
    data.Set("orderByFields", "bws_cat DESC")

    resp, err := http.Post(endpoint, "application/x-www-form-urlencoded",
        strings.NewReader(data.Encode()))
    if err != nil {
        return nil, fmt.Errorf("http post: %w", err)
    }
    defer resp.Body.Close()

    body, err := io.ReadAll(resp.Body)
    if err != nil {
        return nil, fmt.Errorf("read body: %w", err)
    }

    var result AqueductResponse
    if err := json.Unmarshal(body, &result); err != nil {
        return nil, fmt.Errorf("parse json: %w", err)
    }
    return &result, nil
}

func main() {
    where := "country_un='United States of America' AND name_1='West Virginia'"
    fields := "name_1,aq_name,bws_cat,bws_label,drr_cat,drr_label,rfr_cat,rfr_label,gtd_cat,gtd_label"

    result, err := QueryAqueduct(where, fields, 50)
    if err != nil {
        fmt.Fprintf(os.Stderr, "error: %v\n", err)
        os.Exit(1)
    }

    fmt.Printf("Found %d watersheds\n", len(result.Features))
    for _, f := range result.Features {
        a := f.Attributes
        fmt.Printf("%-25s BWS=%-12v Drought=%-12v Flood=%-12v GW=%-12v\n",
            a["aq_name"], a["bws_label"], a["drr_label"],
            a["rfr_label"], a["gtd_label"])
    }

    if result.ExceededTransferLimit {
        fmt.Println("Warning: result set was truncated. Use pagination.")
    }
}
```

---

## Aqueduct Version History

| Version | Year | Key Changes |
|---------|------|-------------|
| Aqueduct 4.0 | 2023 | Current; updated GRACE data to 2023; revised flood model; added coastal indicators |
| Aqueduct 3.0 | 2019 | Added food, water quality, regulatory indicators |
| Aqueduct 2.1 | 2015 | Added groundwater stress indicator |
| Aqueduct 2.0 | 2014 | First version with global coverage |

Data download (for local analysis):
- GeoPackage format: https://datasets.wri.org/dataset/aqueduct40
- Full documentation: https://www.wri.org/research/aqueduct-40-updated-decision-relevant-global-water-risk-indicators
