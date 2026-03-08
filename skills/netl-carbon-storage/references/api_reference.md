# NETL Carbon Storage — API Reference

Reference for ScienceBase Catalog API, NETL EDX CKAN API, and NATCARB Atlas
data patterns used by the `netl-carbon-storage` skill.

---

## ScienceBase Catalog API

**Base URL:** `https://www.sciencebase.gov/catalog/`

### Get a Specific Item

```
GET https://www.sciencebase.gov/catalog/item/{ITEM_ID}?format=json&fields={fields}
```

| Parameter | Description | Example |
|-----------|-------------|---------|
| `format` | Response format | `json` (required to avoid HTML) |
| `fields` | Comma-separated fields to include | `title,summary,files,webLinks,contacts` |

**Always include `format=json`.** Without it, ScienceBase returns HTML.

Example:
```bash
curl -s "https://www.sciencebase.gov/catalog/item/5b89436fe4b0702d0e808ba7?format=json&fields=title,summary,files,webLinks"
```

Response structure:
```json
{
  "id": "5b89436fe4b0702d0e808ba7",
  "title": "National Carbon Sequestration Database...",
  "summary": "NATCARB Atlas V contains storage capacity estimates...",
  "files": [
    {
      "name": "AtlasV_Chapter2_Saline.pdf",
      "url": "https://www.sciencebase.gov/catalog/file/get/...",
      "contentType": "application/pdf",
      "size": 15234567
    }
  ],
  "webLinks": [
    { "title": "NATCARB Web Interface", "uri": "https://natcarb.netl.doe.gov/", "type": "webLink" }
  ]
}
```

---

### Search Items

```
GET https://www.sciencebase.gov/catalog/items?q={query}&format=json&fields={fields}&max={n}
```

| Parameter | Description | Default |
|-----------|-------------|---------|
| `q` | Full-text search query | required |
| `format` | Must be `json` | html |
| `fields` | Fields to return | all |
| `max` | Max results per page | 10 |
| `offset` | Pagination offset | 0 |
| `sort` | Sort field | `lastUpdated` |
| `order` | Sort direction `DESC` or `ASC` | DESC |
| `filter` | Filter expressions | none |

Useful field values for `fields` parameter:
- `title` — item title
- `summary` — abstract/description
- `files` — attached files with download URLs
- `webLinks` — external URL links
- `contacts` — authors/originating offices
- `identifiers` — DOIs, catalog numbers
- `tags` — subject tags

Example — search for MRCSP data:
```bash
curl -s "https://www.sciencebase.gov/catalog/items?q=MRCSP+carbon+sequestration+Appalachian&format=json&fields=title,summary,webLinks&max=10" \
  | jq '.items[] | {title: .title, summary: (.summary // "" | .[0:200])}'
```

Response structure:
```json
{
  "total": 42,
  "items": [ { "id": "...", "title": "...", "summary": "..." } ],
  "selflink": "...",
  "nextlink": "..."  // present if more pages available
}
```

Paginate using `offset`:
```bash
# Page 2 (items 10–19)
curl -s "https://www.sciencebase.gov/catalog/items?q=carbon+storage&format=json&max=10&offset=10"
```

---

### Key Carbon Storage ScienceBase Items

| Title | ScienceBase ID | Notes |
|-------|----------------|-------|
| NATCARB Atlas V (main item) | 5b89436fe4b0702d0e808ba7 | Master entry with chapter PDFs |
| World Minerals Outlook 2029 | 67b8b168d34e1a2e835b7e6c | Includes Li/Mg/CO2 capacity outlook |
| MRCSP Final Report | Search "MRCSP final report" | Appalachian+Midwest RCSP data |
| SECARB Final Report | Search "SECARB carbon storage" | Southeast RCSP |
| WESTCARB | Search "WESTCARB" | Western RCSP |
| PCOR Partnership | Search "PCOR carbon sequestration" | Plains/Northern Rockies RCSP |
| SWP Partnership | Search "Southwest Partnership carbon" | Desert Southwest RCSP |
| Big Sky Partnership | Search "Big Sky Carbon" | Northern Rockies RCSP |
| MGSC (Midwest) | Search "MGSC carbon sequestration" | Illinois basin RCSP |

---

## NETL EDX CKAN API

**Base URL:** `https://edx.netl.doe.gov/api/3/action/`

### Authentication

All EDX endpoints require an API key. The header can be any of:
```
EDX-API-Key: YOUR_KEY
X-CKAN-API-Key: YOUR_KEY
Authorization: YOUR_KEY
```

Prefer `EDX-API-Key`. If that fails, try `X-CKAN-API-Key`.

### CKAN Actions

#### package_search — Search Datasets

```bash
curl -s "https://edx.netl.doe.gov/api/3/action/package_search?q=QUERY&rows=N&start=OFFSET" \
  -H "EDX-API-Key: $NETL_EDX_API_KEY"
```

| Parameter | Description | Default |
|-----------|-------------|---------|
| `q` | Free-text search | `*:*` (all) |
| `rows` | Results per page | 10 |
| `start` | Offset for pagination | 0 |
| `fq` | Filter query (SOLR syntax) | none |
| `sort` | Sort field + direction | `score desc` |

Useful filter queries (`fq`):
- `fq=groups:claimm` — only ClaiMM (critical minerals) datasets
- `fq=tags:carbon` — datasets tagged "carbon"
- `fq=organization:netl` — NETL-published datasets

Response:
```json
{
  "success": true,
  "result": {
    "count": 42,
    "results": [
      {
        "id": "abc-123",
        "name": "dataset-slug",
        "title": "Carbon Storage Formation Characterization Data",
        "notes": "Dataset description...",
        "tags": [{"name": "carbon"}, {"name": "saline-aquifer"}],
        "resources": [
          {
            "id": "resource-uuid",
            "name": "data.csv",
            "format": "CSV",
            "url": "https://edx.netl.doe.gov/dataset/..."
          }
        ]
      }
    ]
  }
}
```

#### package_show — Get Dataset Details

```bash
curl -s "https://edx.netl.doe.gov/api/3/action/package_show?id=DATASET_ID_OR_SLUG" \
  -H "EDX-API-Key: $NETL_EDX_API_KEY"
```

#### resource_search — Search Files

```bash
curl -s "https://edx.netl.doe.gov/api/3/action/resource_search?query=name:carbon+storage&limit=10" \
  -H "EDX-API-Key: $NETL_EDX_API_KEY"
```

#### Download a Resource

```bash
wget --header="EDX-API-Key: $NETL_EDX_API_KEY" \
  "https://edx.netl.doe.gov/dataset/DATASET_SLUG/resource_download/RESOURCE_UUID" \
  -O output_file.csv
```

---

## Carbon Storage Capacity Units and Conversions

| Unit | Symbol | Equivalent |
|------|--------|------------|
| Gigatonne CO2 | GtCO2 | 1 × 10^9 metric tonnes |
| Megatonne CO2 | MtCO2 | 1 × 10^6 metric tonnes |
| Kilotonne CO2 | ktCO2 | 1 × 10^3 metric tonnes |
| Short ton CO2 | stCO2 | 0.907 metric tonnes |
| Million short tons | MMST | 0.907 MtCO2 |

**Conversion formulas:**
```
GtCO2 = MtCO2 / 1000
MtCO2 = GtCO2 × 1000
metric tonnes = short tons × 0.9072
short tons = metric tonnes × 1.1023
```

**Scale reference:**
| Quantity | Approximate Value |
|----------|-------------------|
| U.S. CO2 emissions (2023) | ~5.0 GtCO2/yr |
| Global CO2 emissions (2023) | ~37 GtCO2/yr |
| U.S. saline aquifer capacity (Atlas V P50) | ~8,000 GtCO2 |
| Mt. Simon Sandstone (Illinois basin) | ~11–150 GtCO2 |
| Oriskany Sandstone (Appalachian) | Tens to hundreds of GtCO2 |
| Typical large CCS project | 1–5 MtCO2/yr |

---

## NATCARB Atlas V Chapter Structure

| Chapter | Topic | Reservoir Type |
|---------|-------|----------------|
| 1 | Introduction and Methodology | All |
| 2 | Deep Saline Formations | Saline aquifers |
| 3 | Oil and Gas Reservoirs | Depleted O&G fields + EOR |
| 4 | Unmineable Coal Seams | ECBM |
| 5 | Basalt Formations | Mafic rocks |
| 6 | Organic-Rich Shales | Shale |
| 7 | GIS Data Layers | Spatial data |

All chapters available as PDF downloads from the ScienceBase item
`5b89436fe4b0702d0e808ba7`.

---

## Regional Carbon Sequestration Partnerships (RCSPs)

Seven DOE-funded partnerships conducted geologic characterization studies
from 2003–2017. Data is on ScienceBase and EDX.

| Partnership | Abbreviation | States Covered | Key Formations |
|-------------|--------------|----------------|----------------|
| Midwest Regional | MRCSP | OH, WV, KY, MI, IN, PA, NY | Oriskany, Mt. Simon, Rose Run |
| Southeast Regional | SECARB | AL, GA, FL, LA, MS, AR, TN, NC, SC, TX | Tuscaloosa, Frio |
| Southwest Regional | SWP | CO, UT, AZ, NM, NV, CA | Morrison, Entrada |
| Plains CO2 Reduction | PCOR | ND, SD, MN, WI, WY, MT, IA, NE, KS, MO | Madison, Minnelusa |
| Big Sky | BSCSP | MT, ID, WY, OR, WA, SD | Morrison, Phosphoria |
| West Coast | WESTCARB | CA, OR, WA, AK, HI | Great Valley, offshore |
| Midwest Geologic Seq. | MGSC | IL, IN, KY | Mt. Simon, Eau Claire |

---

## Go Example: ScienceBase Search

```go
package main

import (
    "encoding/json"
    "fmt"
    "io"
    "net/http"
    "net/url"
    "os"
)

type SBItem struct {
    ID      string `json:"id"`
    Title   string `json:"title"`
    Summary string `json:"summary"`
    Files   []struct {
        Name string `json:"name"`
        URL  string `json:"url"`
        Size int64  `json:"size"`
    } `json:"files"`
    WebLinks []struct {
        Title string `json:"title"`
        URI   string `json:"uri"`
    } `json:"webLinks"`
}

type SBSearchResponse struct {
    Total    int      `json:"total"`
    Items    []SBItem `json:"items"`
    NextLink string   `json:"nextlink"`
}

func searchScienceBase(query string, maxResults int) (*SBSearchResponse, error) {
    params := url.Values{}
    params.Set("q", query)
    params.Set("format", "json")
    params.Set("fields", "title,summary,files,webLinks")
    params.Set("max", fmt.Sprintf("%d", maxResults))

    endpoint := "https://www.sciencebase.gov/catalog/items?" + params.Encode()
    resp, err := http.Get(endpoint)
    if err != nil {
        return nil, fmt.Errorf("HTTP GET failed: %w", err)
    }
    defer resp.Body.Close()

    body, err := io.ReadAll(resp.Body)
    if err != nil {
        return nil, fmt.Errorf("reading body: %w", err)
    }

    var result SBSearchResponse
    if err := json.Unmarshal(body, &result); err != nil {
        return nil, fmt.Errorf("JSON parse failed: %w", err)
    }
    return &result, nil
}

func getItemByID(itemID string) (*SBItem, error) {
    endpoint := fmt.Sprintf(
        "https://www.sciencebase.gov/catalog/item/%s?format=json&fields=title,summary,files,webLinks",
        itemID,
    )
    resp, err := http.Get(endpoint)
    if err != nil {
        return nil, err
    }
    defer resp.Body.Close()

    var item SBItem
    if err := json.NewDecoder(resp.Body).Decode(&item); err != nil {
        return nil, err
    }
    return &item, nil
}

func main() {
    results, err := searchScienceBase("carbon storage Appalachian saline aquifer", 10)
    if err != nil {
        fmt.Fprintf(os.Stderr, "error: %v\n", err)
        os.Exit(1)
    }
    fmt.Printf("Found %d results\n\n", results.Total)
    for _, item := range results.Items {
        fmt.Printf("Title: %s\n", item.Title)
        fmt.Printf("ID:    %s\n", item.ID)
        fmt.Printf("Files: %d\n\n", len(item.Files))
    }
}
```

---

## Useful NATCARB / NETL Web Endpoints

| Resource | URL | Notes |
|----------|-----|-------|
| NATCARB Atlas V home | https://www.netl.doe.gov/coal/carbon-storage/atlasv | Overview + download links |
| NATCARB interactive map | https://www.netl.doe.gov/coal/carbon-storage/natcarb-atlas | Web GIS (no API) |
| CarbonSAFE program info | https://www.netl.doe.gov/coal/carbon-storage/carbon-storage-fep/storage-infrastructure | Large-scale storage projects |
| ClaiMM program (EDX) | https://edx.netl.doe.gov/sites/claimm/ | Critical minerals + CCS datasets |
| EPA Class VI permits (UIC) | https://www.epa.gov/uic/class-vi-wells | CO2 injection well permits |
| Global CCS Institute tracker | https://co2re.co/FacilityData | Active/planned CCS facilities |
