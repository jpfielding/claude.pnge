---
name: padep-wells
description: >
  Query Pennsylvania DEP oil and gas well permit and production data covering
  the Marcellus Shale, Utica Shale, and conventional formations in Pennsylvania.
  Use this skill when the user asks about Pennsylvania oil and gas wells,
  Marcellus Shale permits in PA, well counts by county, unconventional vs
  conventional wells in Pennsylvania, PA well spud dates, operators in
  Pennsylvania, PA DEP well data, or any Pennsylvania petroleum and natural gas
  well information. Trigger for phrases like "Marcellus wells in Susquehanna
  County", "PA unconventional well permits", "operators drilling in
  Pennsylvania", "how many wells in Bradford County PA", "Pennsylvania Utica
  wells", "PA DEP well data", or "Appalachian basin wells in Pennsylvania".
  Covers 350,000-plus wells including active, inactive, and abandoned. Produces
  tabular results with operator, formation, permit date, and location data.
---

# PA DEP Oil and Gas Well Data Skill

Queries Pennsylvania DEP unconventional and conventional oil and gas well
data via the PA Open Data portal (Socrata) and the PA DEP GIS REST services.

---

## API Key Handling

No API key required for basic queries. For high-volume requests, register
a free app token at https://data.pa.gov/ to avoid throttling.

Optional app token header:
```bash
-H "X-App-Token: YOUR_APP_TOKEN"
```

---

## Data Sources and API Structure

### Source 1: PA Open Data — Unconventional Wells (Primary)

**Endpoint:** `https://data.pa.gov/resource/nfax-tpjr.json`

Covers Marcellus, Utica, and other unconventional (horizontal) wells.
~30,000+ permits since 2008.

### Source 2: PA Open Data — Conventional Wells

**Endpoint:** `https://data.pa.gov/resource/e3er-typed.json`

Covers vertical conventional oil and gas wells. 300,000+ historical records.

### Source 3: PA DEP ArcGIS REST (Spatial Queries)

**Endpoint:** `https://gis.dep.pa.gov/arcgis/rest/services/DEP_Public/OilGas/MapServer`

Use for bounding-box spatial queries.

---

## Workflow

### Step 1 — Resolve Intent

| User Intent | Source | Query Pattern |
|------------|--------|---------------|
| Unconventional wells by county | Socrata nfax-tpjr | `county_name='SUSQUEHANNA'` |
| Count by operator | Socrata nfax-tpjr | `$select=operator_name,count(*)&$group=operator_name` |
| Recent permits | Socrata nfax-tpjr | `$order=permit_issue_date DESC` |
| Conventional historical | Socrata e3er-typed | Different schema |
| Spatial bounding box | ArcGIS REST | `geometry=bbox&geometryType=envelope` |

### Step 2 — Fetch Data (Unconventional)

```bash
# Wells in Susquehanna County
curl -s "https://data.pa.gov/resource/nfax-tpjr.json?\$where=county_name='SUSQUEHANNA'&\$limit=100&\$order=spud_date+DESC" \
  -H "Accept: application/json"

# Count wells by county statewide
curl -s "https://data.pa.gov/resource/nfax-tpjr.json?\$select=county_name,count(*)&\$group=county_name&\$order=count+DESC&\$limit=67"

# Filter by operator
curl -s "https://data.pa.gov/resource/nfax-tpjr.json?\$where=operator_name+like+'%25EQT%25'&\$limit=50"

# Active Marcellus wells with coordinates
curl -s "https://data.pa.gov/resource/nfax-tpjr.json?\$where=well_status='Active'&\$select=api_number,well_name,operator_name,county_name,municipality_name,latitude,longitude,spud_date,primary_target_formation&\$limit=200"

# Permits issued in last year
curl -s "https://data.pa.gov/resource/nfax-tpjr.json?\$where=permit_issue_date>'2024-01-01'&\$order=permit_issue_date+DESC&\$limit=100"
```

### Step 3 — Fetch Data (ArcGIS REST)

```bash
# Get layer list
curl -s "https://gis.dep.pa.gov/arcgis/rest/services/DEP_Public/OilGas/MapServer?f=json" \
  | jq '.layers[] | {id, name}'

# Spatial query — wells within bounding box (southwestern PA)
curl -s "https://gis.dep.pa.gov/arcgis/rest/services/DEP_Public/OilGas/MapServer/0/query" \
  --data-urlencode "geometry=-80.5,39.7,-79.5,40.2" \
  --data-urlencode "geometryType=esriGeometryEnvelope" \
  --data-urlencode "spatialRel=esriSpatialRelIntersects" \
  --data-urlencode "outFields=*" \
  --data-urlencode "resultRecordCount=50" \
  --data-urlencode "f=json"
```

### Step 4 — Parse Response

Key fields for unconventional wells (Socrata nfax-tpjr):

| Field | Description | Example |
|-------|-------------|---------|
| `api_number` | API well number | 37-115-2XXXXX |
| `permit_number` | PA DEP permit | 115-XXXXX |
| `well_name` | Well name | SMITH 1H |
| `operator_name` | Operator company | EQT PRODUCTION CO |
| `county_name` | County (uppercase) | SUSQUEHANNA |
| `municipality_name` | Township/borough | AUBURN TOWNSHIP |
| `latitude` / `longitude` | WGS84 coordinates | 41.87 / -76.12 |
| `spud_date` | Spud date (ISO) | 2022-03-15 |
| `permit_issue_date` | Permit date (ISO) | 2022-01-10 |
| `well_status` | Active/Inactive/Abandoned/Plugged | Active |
| `primary_target_formation` | Target formation | MARCELLUS |
| `unconventional_well_ind` | Y/N flag | Y |

### Step 5 — Output

```
## PA DEP Well Query Results

**Query:** Unconventional wells in Susquehanna County, PA
**Records returned:** 847

### Top Operators (by well count)
| Operator | Wells |
|----------|-------|
| CABOT OIL AND GAS | 312 |
| SOUTHWESTERN ENERGY | 198 |
| WPX ENERGY | 87 |

### Well Summary Table (most recent 10)
| Well Name | Operator | Municipality | Spud Date | Status |
|-----------|----------|-------------|-----------|--------|
| SMITH 1H | CABOT | AUBURN TWP | 2023-05-12 | Active |
...

**Data source:** PA DEP via data.pa.gov (Socrata). Unconventional well
dataset covers permits issued 2008–present. Well status as of last update.
```

---

## Socrata SoQL Reference

SoQL (Socrata Query Language) supports standard SQL-like syntax:

```
$where    — filter clause (SQL WHERE)
$select   — column selection and aggregation
$group    — GROUP BY for aggregations
$order    — ORDER BY (field ASC/DESC)
$limit    — result limit (max 50,000)
$offset   — pagination offset
$q        — full-text search
```

Operators in `$where`:
- `=`, `!=`, `<`, `>`, `<=`, `>=`
- `like '%TERM%'` — substring match
- `IS NULL`, `IS NOT NULL`
- `AND`, `OR`

Date comparison: use ISO format `'2024-01-01T00:00:00'` or `'2024-01-01'`

---

## Error Handling

| Condition | Meaning | Action |
|-----------|---------|--------|
| HTTP 400 with "Invalid SoQL" | Malformed WHERE clause | Check quoting: strings need single quotes |
| Empty array `[]` | No records match | Broaden filter or check county name spelling (UPPERCASE) |
| HTTP 429 | Throttled | Add X-App-Token header (free registration at data.pa.gov) |
| Missing field for some records | Field null for older wells | Note that older conventional records may lack lat/lon |
| ArcGIS HTTP 499 | Spatial service timeout | Reduce bounding box or use Socrata instead |

---

## County Name Reference (Marcellus Counties)

PA county names in this dataset are stored **uppercase**:

| County | Code | Notes |
|--------|------|-------|
| SUSQUEHANNA | 115 | Highest Marcellus well count |
| BRADFORD | 015 | Major Marcellus area |
| TIOGA | 117 | Northern Marcellus |
| LYCOMING | 081 | Active Marcellus area |
| WASHINGTON | 125 | SW PA, Marcellus + Utica |
| GREENE | 059 | SW PA, deep Utica target |
| WESTMORELAND | 129 | SW PA transition zone |

---

## Caveats

- Data reflects PA DEP permit records; production volumes are not included
  in this dataset. For production data, contact PA DEP directly or use EIA.
- Spud dates may be null for permits that were issued but never drilled.
- Operator names are reported as-of permit; corporate mergers may cause
  the same physical operator to appear under multiple names.
- Coordinates are well pad surface locations, not bottomhole targets.
- For WV wells, use `pnge-state-regulatory:wvges-wells` instead.
