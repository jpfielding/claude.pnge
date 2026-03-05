---
name: boem-offshore
description: >
  Query and analyze federal Outer Continental Shelf (OCS) offshore oil and gas
  data from the Bureau of Ocean Energy Management (BOEM) and Bureau of Safety
  and Environmental Enforcement (BSEE). Use this skill whenever the user asks
  about offshore wells, Gulf of Mexico production, OCS lease data, offshore
  platforms, deepwater drilling, federal offshore energy statistics, OCS
  pipeline infrastructure, or any BOEM/BSEE data — even if they do not
  explicitly mention BOEM. Trigger for phrases like "offshore wells in the
  Gulf", "OCS lease status", "how many platforms are in the Gulf of Mexico",
  "deepwater production", "offshore pipeline map", "federal offshore oil
  production", "BOEM well data", or "OCS drilling activity". Produces spatial
  query results, summary tables, and narrative analysis of offshore energy data.
---

# BOEM Offshore Data Skill

Fetches and analyzes federal OCS offshore oil and gas data from the BOEM/BSEE
ArcGIS REST MapServer and BOEM Data Center bulk downloads.

## API Key Handling

**No API key is required.** All BOEM and BSEE data services are public and
freely accessible without authentication.

---

## Data Sources

BOEM provides two primary access methods:

1. **ArcGIS REST MapServer** — real-time spatial and attribute queries against
   national and regional GIS layers (wells, platforms, leases, pipelines,
   boundaries)
2. **Bulk ASCII Downloads** — zipped delimited text files from the BOEM Data
   Center containing full database exports (production, borehole, lease owner,
   etc.)

See `references/endpoints.md` for the complete endpoint catalog.

---

## API Structure

### GIS MapServer (Primary Query Interface)

**Base URL:** `https://gis.boem.gov/arcgis/rest/services/BOEM_BSEE/MMC_Layers/MapServer`

**Key Layers:**

| Layer ID | Name                          | Geometry | Approx Records |
|----------|-------------------------------|----------|----------------|
| 0        | OCS Drilling Platforms        | Point    | ~1,354         |
| 1        | OCS Oil and Natural Gas Wells | Point    | ~56,363        |
| 2        | OCS Oil & Gas Pipelines       | Polyline | varies         |
| 15       | BOEM Oil and Gas Leases       | Polygon  | ~1,994         |
| 20       | BOEM Oil and Gas Planning Areas | Polygon | —             |

**Query parameters for `{MapServer}/{LayerID}/query`:**

| Parameter         | Example                              | Notes                            |
|-------------------|--------------------------------------|----------------------------------|
| where             | where=STATUS='PA'                    | SQL WHERE clause                 |
| outFields         | outFields=API_NUMBER,OPERATOR,DEPTH  | Comma-separated field list       |
| geometry          | geometry=-91,28,-89,29               | Bounding box xmin,ymin,xmax,ymax |
| geometryType      | geometryType=esriGeometryEnvelope    | Envelope, Point, Polygon         |
| spatialRel        | spatialRel=esriSpatialRelIntersects  | Spatial relationship             |
| resultRecordCount | resultRecordCount=100                | Max rows per request             |
| resultOffset      | resultOffset=100                     | Pagination offset                |
| returnCountOnly   | returnCountOnly=true                 | Count without data               |
| orderByFields     | orderByFields=DEPTH DESC             | Sort order                       |
| f                 | f=json                               | Response format (json, geojson)  |

### Bulk Data Downloads

**Base URL:** `https://www.data.boem.gov/`

Key download files (all zip archives of delimited text):

| Data Type                | URL Path                                    |
|--------------------------|---------------------------------------------|
| OGOR-A Production        | /Production/Files/ogoradelimit.zip          |
| OGOR-A by Year           | /Production/Files/ogora{YYYY}delimit.zip    |
| OCS Production Summary   | /Production/Files/OCSProdRawData.zip        |
| Borehole Data            | /Well/Files/BoreholeRawData.zip             |
| Lease Owner              | /Leasing/Files/LeaseOwnerRawData.zip        |
| Platform Structures      | /Platform/Files/PlatStrucRawData.zip        |
| Pipeline Locations       | /Pipeline/Files/PipeLocRawData.zip          |
| Company Data             | /Company/Files/CompanyRawData.zip           |

---

## Key Fields by Layer

### Wells (Layer 1)
- `API_NUMBER` — 12-digit API well number
- `OPERATOR` — Operator company number (cross-ref with Company data)
- `WELL_NAME` — Well name/designation
- `SPUD_DATE` — Date drilling commenced
- `TYPE_CODE_DESC` — Well type (Development, Exploratory)
- `STATUS` / `STATUS_DESCRIPTION` — Current status (PA=Permanently Abandoned, COM=Completed, DRL=Drilling, etc.)
- `DEPTH` — Total depth (feet)
- `X`, `Y` — Longitude, Latitude (NAD83)

### Platforms (Layer 0)
- `COMPLEX_ID_NUM` — Platform complex identifier
- `INSTALL_DATE` — Installation date
- `REMOVAL_DATE` — Removal date (null = still active)

### Leases (Layer 15)
- `LEASE_NUMBER` — OCS lease serial number
- `LEASE_STATUS_CD` — Status (PROD, EXPR, RELD, TERM, SOP, SOO)
- `LEASE_EFF_DATE` / `LEASE_EXPIR_DATE` — Effective and expiration dates
- `SALE_NUMBER` — Lease sale number
- `ROYALTY_RATE` — Royalty rate (fraction)
- `MINERAL_TYPE_CD` — Mineral type code
- `CURRENT_AREA` / `INITIAL_AREA` — Lease area

---

## Workflow

### Step 1 — Resolve Intent

Map the user's question to the appropriate layer and query type:

| User Intent                     | Layer       | Query Type      |
|---------------------------------|-------------|-----------------|
| Offshore wells, drilling        | wells (1)   | Attribute/Spatial |
| Platforms, structures           | platforms (0)| Attribute/Spatial |
| Lease status, sales             | leases (15) | Attribute       |
| Pipeline infrastructure         | pipelines (2)| Spatial         |
| Production volumes, OGOR data   | —           | Bulk download   |
| Planning areas, boundaries      | planning (20)| Attribute      |

If uncertain which layer to query, start by checking the MapServer root to
list available layers:
```bash
curl -s "https://gis.boem.gov/arcgis/rest/services/BOEM_BSEE/MMC_Layers/MapServer?f=json" \
  | jq '.layers[] | {id, name}'
```

### Step 2 — Build the Query

**Attribute query (e.g., wells by status):**
```bash
curl -s "https://gis.boem.gov/arcgis/rest/services/BOEM_BSEE/MMC_Layers/MapServer/1/query" \
  --data-urlencode "where=STATUS='PA'" \
  --data-urlencode "outFields=API_NUMBER,OPERATOR,WELL_NAME,STATUS_DESCRIPTION,DEPTH,TYPE_CODE_DESC,SPUD_DATE" \
  --data-urlencode "resultRecordCount=20" \
  --data-urlencode "f=json"
```

**Spatial query (e.g., wells within a bounding box):**
```bash
curl -s "https://gis.boem.gov/arcgis/rest/services/BOEM_BSEE/MMC_Layers/MapServer/1/query" \
  --data-urlencode "geometry=-91,28,-89,29" \
  --data-urlencode "geometryType=esriGeometryEnvelope" \
  --data-urlencode "spatialRel=esriSpatialRelIntersects" \
  --data-urlencode "outFields=API_NUMBER,OPERATOR,WELL_NAME,STATUS_DESCRIPTION,DEPTH" \
  --data-urlencode "resultRecordCount=20" \
  --data-urlencode "f=json"
```

**Count query (e.g., how many wells total):**
```bash
curl -s "https://gis.boem.gov/arcgis/rest/services/BOEM_BSEE/MMC_Layers/MapServer/1/query?where=1%3D1&returnCountOnly=true&f=json"
```

**Platform query (active platforms only):**
```bash
curl -s "https://gis.boem.gov/arcgis/rest/services/BOEM_BSEE/MMC_Layers/MapServer/0/query" \
  --data-urlencode "where=REMOVAL_DATE IS NULL" \
  --data-urlencode "outFields=COMPLEX_ID_NUM,INSTALL_DATE" \
  --data-urlencode "resultRecordCount=10" \
  --data-urlencode "f=json"
```

**Lease query (producing leases):**
```bash
curl -s "https://gis.boem.gov/arcgis/rest/services/BOEM_BSEE/MMC_Layers/MapServer/15/query" \
  --data-urlencode "where=LEASE_STATUS_CD='PROD'" \
  --data-urlencode "outFields=LEASE_NUMBER,LEASE_STATUS_CD,LEASE_EFF_DATE,SALE_NUMBER,ROYALTY_RATE" \
  --data-urlencode "resultRecordCount=10" \
  --data-urlencode "f=json"
```

**Bulk production download:**
```bash
# Download all OGOR-A production data (pipe-delimited, ~1.3 MB compressed)
curl -sO "https://www.data.boem.gov/Production/Files/ogoradelimit.zip"

# Or a single year
curl -sO "https://www.data.boem.gov/Production/Files/ogora2024delimit.zip"
```

### Step 3 — Parse Response

GIS query responses follow this structure:
```json
{
  "displayFieldName": "API_Number",
  "fieldAliases": { "API_NUMBER": "API_NUMBER", ... },
  "geometryType": "esriGeometryPoint",
  "spatialReference": { "wkid": 4269 },
  "fields": [ { "name": "API_NUMBER", "type": "esriFieldTypeString", ... } ],
  "features": [
    {
      "attributes": {
        "API_NUMBER": "608104006000",
        "OPERATOR": "00250",
        "WELL_NAME": "  001",
        "STATUS_DESCRIPTION": "Permanently Abandoned",
        "DEPTH": "12500",
        "TYPE_CODE_DESC": "Development"
      },
      "geometry": { "x": -90.123, "y": 28.456 }
    }
  ]
}
```

Key parsing notes:
- Feature data is in `features[].attributes`
- Coordinates are in `features[].geometry` (NAD83, lon/lat)
- Date fields are millisecond epoch timestamps (divide by 1000 for Unix time)
- The `OPERATOR` field is a company number, not a name — cross-reference with
  Company bulk data for operator names

### Step 4 — Produce Output

**Format: Raw Data Table + Narrative**

Present a markdown table of the most relevant rows (cap at ~20 rows for
readability), then a narrative summary covering:

1. **Current state** — count of features, geographic scope
2. **Key statistics** — depth ranges, status breakdowns, temporal coverage
3. **Geographic context** — planning area, water depth zone if applicable
4. **Data quality notes** — operator codes vs names, date format caveats

**Example output structure:**
```
## OCS Wells — Central Gulf of Mexico (28-29N, 89-91W)

| API Number      | Operator | Well Name | Status              | Depth (ft) | Type        |
|-----------------|----------|-----------|---------------------|------------|-------------|
| 608104006000    | 00250    | 001       | Permanently Abandoned| 12,500     | Development |
| 608174002101    | 02481    | A001      | Completed           | 18,200     | Exploratory |
| ...             | ...      | ...       | ...                 | ...        | ...         |

**Summary:** Query returned 247 wells within the bounding box -91,28 to -89,29
in the central Gulf of Mexico. Of these, 68% are permanently abandoned, 22% are
completed, and 10% are in other statuses. Well depths range from 2,100 to
31,400 ft, with a median of 14,800 ft. The area spans portions of the Central
Planning Area (CPA) and includes both shelf and deepwater wells. Operator codes
shown — use the Company bulk download for operator name lookup.
```

---

## Pagination

The ArcGIS REST API limits results per request (typically 1,000-2,000 features
depending on server configuration). Use `resultRecordCount` and `resultOffset`
to paginate:

```python
import json
import urllib.request
import urllib.parse

offset = 0
page_size = 1000
all_features = []

while True:
    params = urllib.parse.urlencode({
        "where": "1=1",
        "outFields": "API_NUMBER,OPERATOR,STATUS",
        "resultRecordCount": str(page_size),
        "resultOffset": str(offset),
        "f": "json",
    })
    url = f"https://gis.boem.gov/arcgis/rest/services/BOEM_BSEE/MMC_Layers/MapServer/1/query?{params}"
    with urllib.request.urlopen(url) as resp:
        data = json.loads(resp.read())
    features = data.get("features", [])
    if not features:
        break
    all_features.extend(features)
    offset += len(features)
    if len(features) < page_size:
        break

print(f"Total features: {len(all_features)}")
```

Warn the user if a dataset exceeds ~10,000 features and suggest spatial or
attribute filters to narrow results.

---

## Error Handling

| HTTP Code / Condition        | Meaning                     | Action                                   |
|------------------------------|-----------------------------|------------------------------------------|
| 200 + empty features[]       | No matching records         | Adjust WHERE clause or spatial filter     |
| 200 + error in JSON          | Invalid query syntax        | Check SQL WHERE syntax, field names       |
| 400                          | Bad request parameters      | Verify field names exist on the layer     |
| 403                          | Access denied               | Should not occur (public data)            |
| 404                          | Layer or service not found  | Verify layer ID exists; check service URL |
| 500                          | Server error                | Retry after brief delay                   |
| Timeout                      | Large result set            | Add spatial filter or reduce record count |
| Bulk download returns HTML   | File URL changed            | Check /Main/RawData.aspx for current URLs |

---

## Regional GIS Services

In addition to the national MMC_Layers, BOEM provides regional MapServers
with additional detail:

| Region           | Service URL                                          |
|------------------|------------------------------------------------------|
| Gulf of America  | .../BOEM_BSEE/GOA_Layers/MapServer                  |
| Atlantic         | .../BOEM_BSEE/ATL_Layers/MapServer                  |
| Pacific          | .../BOEM_BSEE/POC_Layers/MapServer                  |
| Alaska           | .../BOEM_BSEE/AK_Layers/MapServer                   |

The GOA (Gulf of America) service includes additional layers such as Seismic
Anomalies (layer 9) and Lease Points (layer 11).

---

## OCS Planning Areas Reference

| Code | Area                          | Region          |
|------|-------------------------------|-----------------|
| CPA  | Central Planning Area         | Gulf of America |
| WPA  | Western Planning Area         | Gulf of America |
| EPA  | Eastern Planning Area         | Gulf of America |
| MDA  | Mid-Atlantic                  | Atlantic        |
| SAA  | South Atlantic                | Atlantic        |
| NAA  | North Atlantic                | Atlantic        |

---

## Geo Reference

**Coordinate System:** All national GIS layers use NAD83 (WKID 4269).
Coordinates are geographic (longitude, latitude in decimal degrees).

**Key geographic bounding boxes for common queries:**

| Area                    | Bounding Box (xmin,ymin,xmax,ymax) |
|-------------------------|-------------------------------------|
| Entire Gulf of Mexico   | -98,24,-81,31                       |
| Central GOM (deepwater) | -92,26,-87,29                       |
| Western GOM             | -98,26,-92,30                       |
| Eastern GOM             | -87,25,-81,30                       |
| Southern California     | -121,33,-117,35                     |
| Cook Inlet, Alaska      | -154,59,-149,62                     |

---

## Caveats and Data Quality

- **Operator codes, not names:** The GIS well layer returns numeric operator
  codes (e.g., "00250"). Cross-reference with the Company bulk download for
  actual operator names.
- **Date formats vary:** GIS date fields are millisecond epoch timestamps.
  The SPUD_DATE field on wells is a string (MM/DD/YYYY). Bulk downloads use
  various date formats per file.
- **GIS vs. official records:** Per BOEM notice, GIS layers should not be
  used for legal or official purposes due to re-projection artifacts. The
  official records are in BOEM's internal database.
- **Production data lag:** OGOR-A production data typically lags 2-3 months
  behind current date. The most recent months may show incomplete volumes.
- **Water depth not in GIS:** The well GIS layer does not include water depth.
  For water depth analysis, use the Offshore Statistics bulk download or the
  borehole raw data files.
- **Bulk download availability:** Some bulk download URLs change periodically.
  If a URL returns an HTML page instead of a zip file, check the Raw Data page
  at https://www.data.boem.gov/Main/RawData.aspx for current links.

---

## Implementation Notes

- **Prefer `bash_tool` with `curl`** for GIS queries — the REST API returns
  clean JSON that `jq` handles well
- **Use `python3`** for bulk data processing — see `references/python_example.py`
  for a stdlib-only client with pagination, spatial queries, and downloads
- **Spatial reference:** Always NAD83 (WKID 4269) for national layers
- **Record limits:** Default server limit is ~2,000 features per request;
  paginate with `resultOffset` for larger result sets
- **GeoJSON output:** Add `f=geojson` instead of `f=json` for GeoJSON-format
  responses compatible with mapping tools
- **BOEM Data Center updates:** Well and lease data are updated frequently
  (weekly to monthly). Production data is updated quarterly.
