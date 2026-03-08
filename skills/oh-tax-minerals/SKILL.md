---
name: oh-tax-minerals
description: >
  Find tax-delinquent and dormant mineral parcels near active Utica and Marcellus
  wells in Ohio. Use this skill when the user asks about Ohio mineral rights,
  delinquent mineral parcels OH, tax sale minerals Ohio, dormant mineral act ORC
  5301.56, severed mineral estate Ohio, mineral land use codes, OGRIP mineral
  parcels, StateLUC 200-series, oil and gas royalty interests Ohio, coal mineral
  rights Ohio, undervalued mineral rights eastern Ohio, Utica Shale mineral
  parcels, Belmont Harrison Carroll Jefferson Monroe Noble Columbiana Guernsey
  county minerals, ODNR wells near mineral parcels, or Ohio mineral rights
  investment screening. Covers 3,360 mineral-coded parcels and 241,949 wells.
---

# OH Tax-Delinquent and Dormant Mineral Properties

Queries Ohio public ArcGIS services to find mineral-coded parcels near active
Utica/Marcellus wells, with dormant mineral screening under ORC 5301.56.
Ohio has a **major advantage** over West Virginia and Pennsylvania: the OGRIP
statewide parcel dataset uses explicit 200-series `StateLUC` codes for mineral
parcels. No text parsing of legal descriptions is needed — `StateLUC LIKE '2%'`
cleanly identifies all 3,360 mineral-coded parcels statewide.

## Credential

**None required.** All Ohio ArcGIS REST services used by this skill are
publicly accessible with no API key or authentication.

---

## Data Sources

### A. OGRIP Statewide Parcels (Primary)

```
https://services2.arcgis.com/MlJ0G8iWUyC7jAmu/arcgis/rest/services/OhioStatewidePacels_full_view/FeatureServer/0
```

Statewide parcel dataset with 6,313,611 records. The `StateLUC` field uses
200-series codes for mineral parcels — the key data element for this skill.
Native SRS is EPSG:3735 (Ohio State Plane South); always request `outSR=4326`
for WGS84 output. Max 2,000 records/request. No auth required.

**Note:** The URL contains "Pacels" (typo) — this is the actual production URL.

### B. OIT Statewide Parcels 2022 (Owner Enrichment)

```
https://maps.ohio.gov/arcgis/rest/services/Statewide_Parcels_2022/MapServer/0
```

Alternate parcel dataset with `OWNER1`/`OWNER2` fields not available in OGRIP.
Max 2,000 records/request. 2022 vintage. No auth required.

### C. ODNR Oil and Gas Wells

```
https://gis.ohiodnr.gov/arcgis/rest/services/DOG_Services/Oilgas_Wells_public/MapServer
```

241,949 wells with production metadata. Layer 0 = all wells. Includes
`Utica_Shale`/`Marcellus_Shale` flags, `Last_Nonzero_Production_Year`, and
operator names. Max 1,000 records/request. No auth required.

### D. County Delinquent Data (Supplemental)

County-specific services with tax delinquency data. No statewide delinquent
property layer exists for Ohio — this data is fragmented across counties.

**Stark County** (has `CERTIFIED_DELINQUENT_YEAR`, `TOTAL_BILLED`, `TOTAL_PAID`,
`FINAL_BALANCE`):
```
https://scgisa.starkcountyohio.gov/arcgis/rest/services/Auditor/StarkCountyParcels/MapServer/0
```

**Cuyahoga County** (forfeited parcels with `Forfeiture_Status_`, `Date_Acquired`):
```
https://services5.arcgis.com/Xti6g2pFdrO8EjbP/arcgis/rest/services/Opportunity_Zones___State_Forfeiture_WFL1/FeatureServer/0
```

---

## API Structure

All services use the standard ArcGIS REST query pattern:

```
POST {service_url}/{layerId}/query
```

**Common parameters:**

| Parameter | Required | Description | Example |
|-----------|----------|-------------|---------|
| where | Yes | SQL WHERE clause | `County='BELMONT' AND StateLUC LIKE '2%'` |
| outFields | No | Comma-separated fields | `StateParcelID,StateLUC,County` or `*` |
| f | Yes | Response format | `json` or `geoJSON` |
| resultRecordCount | No | Max records per request | `100` |
| resultOffset | No | Pagination offset | `2000` |
| returnGeometry | No | Include coordinates | `false` |
| returnCountOnly | No | Return count only | `true` |
| outSR | No | Output spatial reference | `4326` (required for OGRIP) |
| geometry | No | Spatial filter | `-80.9,39.5,-80.6,39.9` |
| geometryType | No | Geometry type | `esriGeometryEnvelope` |
| inSR | No | Input spatial reference | `4326` |
| spatialRel | No | Spatial relationship | `esriSpatialRelIntersects` |
| distance | No | Buffer distance (meters) | `1609.34` (1 mile) |
| units | No | Distance units | `esriSRUnit_Meter` |

### Working curl Examples

**Count all mineral parcels statewide:**
```bash
curl -s "https://services2.arcgis.com/MlJ0G8iWUyC7jAmu/arcgis/rest/services/OhioStatewidePacels_full_view/FeatureServer/0/query" \
  --data-urlencode "where=StateLUC LIKE '2%'" \
  --data-urlencode "returnCountOnly=true" \
  --data-urlencode "f=json"
```

**Mineral parcels in Belmont County (with WGS84 geometry):**
```bash
curl -s "https://services2.arcgis.com/MlJ0G8iWUyC7jAmu/arcgis/rest/services/OhioStatewidePacels_full_view/FeatureServer/0/query" \
  --data-urlencode "where=County='BELMONT' AND StateLUC LIKE '2%'" \
  --data-urlencode "outFields=StateParcelID,LocalParcelID,County,StateLUC,MailAddressAll,LandArea,CAMADataSite" \
  --data-urlencode "returnGeometry=true" \
  --data-urlencode "outSR=4326" \
  --data-urlencode "resultRecordCount=50" \
  --data-urlencode "f=json"
```

**Oil and gas mineral interests only (StateLUC 240, 250):**
```bash
curl -s "https://services2.arcgis.com/MlJ0G8iWUyC7jAmu/arcgis/rest/services/OhioStatewidePacels_full_view/FeatureServer/0/query" \
  --data-urlencode "where=County='HARRISON' AND StateLUC IN ('240','250')" \
  --data-urlencode "outFields=StateParcelID,LocalParcelID,StateLUC,MailAddressAll,LandArea" \
  --data-urlencode "returnGeometry=true" \
  --data-urlencode "outSR=4326" \
  --data-urlencode "resultRecordCount=100" \
  --data-urlencode "f=json"
```

**Aggregate mineral parcels by county:**
```bash
curl -s "https://services2.arcgis.com/MlJ0G8iWUyC7jAmu/arcgis/rest/services/OhioStatewidePacels_full_view/FeatureServer/0/query" \
  --data-urlencode "where=StateLUC LIKE '2%'" \
  --data-urlencode "groupByFieldsForStatistics=County" \
  --data-urlencode 'outStatistics=[{"statisticType":"count","onStatisticField":"OBJECTID","outStatisticFieldName":"cnt"}]' \
  --data-urlencode "orderByFields=cnt DESC" \
  --data-urlencode "f=json"
```

**Owner names from OIT 2022:**
```bash
curl -s "https://maps.ohio.gov/arcgis/rest/services/Statewide_Parcels_2022/MapServer/0/query" \
  --data-urlencode "where=COUNTY='BELMONT'" \
  --data-urlencode "outFields=PIN,COUNTY,OWNER1,OWNER2,ASSR_ACRES,AUD_LINK" \
  --data-urlencode "returnGeometry=false" \
  --data-urlencode "resultRecordCount=20" \
  --data-urlencode "f=json"
```

**Active Utica wells in Belmont County:**
```bash
curl -s "https://gis.ohiodnr.gov/arcgis/rest/services/DOG_Services/Oilgas_Wells_public/MapServer/0/query" \
  --data-urlencode "where=WL_CNTY='Belmont' AND Utica_Shale='Yes' AND WL_STATUS_DESC='Producing'" \
  --data-urlencode "outFields=API_WELLNO,MapSymbol_DESC,CO_NAME,ProducingFormation1,WH_LAT,WH_LONG,Last_Nonzero_Production_Year" \
  --data-urlencode "returnGeometry=false" \
  --data-urlencode "resultRecordCount=50" \
  --data-urlencode "f=json"
```

**Find producing wells within 1 mile of a mineral parcel:**
```bash
curl -s "https://gis.ohiodnr.gov/arcgis/rest/services/DOG_Services/Oilgas_Wells_public/MapServer/0/query" \
  --data-urlencode "geometry=-80.85,39.95" \
  --data-urlencode "geometryType=esriGeometryPoint" \
  --data-urlencode "inSR=4326" \
  --data-urlencode "spatialRel=esriSpatialRelIntersects" \
  --data-urlencode "distance=1609.34" \
  --data-urlencode "units=esriSRUnit_Meter" \
  --data-urlencode "where=WL_STATUS_DESC='Producing'" \
  --data-urlencode "outFields=API_WELLNO,MapSymbol_DESC,CO_NAME,ProducingFormation1,Utica_Shale,Last_Nonzero_Production_Year" \
  --data-urlencode "returnGeometry=false" \
  --data-urlencode "resultRecordCount=50" \
  --data-urlencode "f=json"
```

**Stark County delinquent parcels:**
```bash
curl -s "https://scgisa.starkcountyohio.gov/arcgis/rest/services/Auditor/StarkCountyParcels/MapServer/0/query" \
  --data-urlencode "where=CERTIFIED_DELINQUENT_YEAR IS NOT NULL AND CERTIFIED_DELINQUENT_YEAR > 0" \
  --data-urlencode "outFields=PARCELNO,CERTIFIED_DELINQUENT_YEAR,TOTAL_BILLED,TOTAL_PAID,FINAL_BALANCE" \
  --data-urlencode "returnGeometry=false" \
  --data-urlencode "resultRecordCount=20" \
  --data-urlencode "f=json"
```

---

## Key Fields

### OGRIP Parcels (FeatureServer/0)

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| StateParcelID | String | Statewide unique ID | "0100100001" |
| LocalParcelID | String | County parcel number | "01-0010-0001.000" |
| County | String | County name (uppercase) | "BELMONT" |
| StateLUC | String | State Land Use Code | "240" |
| SitusAddressAll | String | Property address | "123 MAIN ST" |
| MailAddressAll | String | Owner mailing address | "PO BOX 456 WHEELING WV" |
| LandArea | Double | Land area (sq ft) | 1568160.0 |
| CAMADataSite | String | County auditor CAMA URL | "https://..." |
| GlobalID | String | UUID for CAMA table join | "{ABC12345-...}" |

### OIT Parcels 2022 (MapServer/0)

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| PIN | String | Parcel ID number | "01-0010-0001.000" |
| COUNTY | String | County name | "BELMONT" |
| OWNER1 | String | Primary owner | "SMITH JOHN A" |
| OWNER2 | String | Secondary owner | "& SMITH MARY B" |
| ASSR_ACRES | Double | Assessed acreage | 36.0 |
| AUD_LINK | String | Auditor website link | "https://..." |

### ODNR Wells (MapServer/0)

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| API_WELLNO | String | 14-digit API number | "34013200010000" |
| MapSymbol_DESC | String | Well type/symbol | "Gas, Horizontal" |
| WL_STATUS_DESC | String | Current status | "Producing" |
| WL_CNTY | String | County name | "Belmont" |
| CO_NAME | String | Operator name | "ASCENT RESOURCES UTICA LLC" |
| ProducingFormation1 | String | Primary formation | "Utica/Pt Pleasant" |
| Utica_Shale | String | Utica flag | "Yes" or "No" |
| Marcellus_Shale | String | Marcellus flag | "Yes" or "No" |
| Last_Nonzero_Production_Year | Integer | Last year with production | 2023 |
| WH_LAT | Double | Wellhead latitude | 39.9854 |
| WH_LONG | Double | Wellhead longitude | -80.8532 |

---

## Key Enumerated Values

### StateLUC Mineral Codes (200-Series)

| Code | Description | Category | Target? |
|------|-------------|----------|---------|
| 200 | Min-Custom Code | General | Yes |
| 210 | Min-Coal Land (surface and rights) | Coal | Secondary |
| 220 | Min-Coal Rights-Working Interest | Coal | Secondary |
| 230 | Min-Coal Rights-Separate Royalty Interest | Coal | Secondary |
| 240 | Min-Oil and Gas-Working Interest | Oil & Gas | **Primary** |
| 250 | Min-Oil and Gas-Separate Royalty Interest | Oil & Gas | **Primary** |
| 260 | Min-Other Minerals | Other | Secondary |
| 261 | Min-Custom Code | Other | Yes |
| 270 | Min-Custom Code | General | Yes |

**Primary filter:** `StateLUC IN ('240','250')` for oil and gas interests.
**Broad filter:** `StateLUC LIKE '2%'` for all mineral types.

### ODNR Well Status (WL_STATUS_DESC)

| Value | Description | Relevance |
|-------|-------------|-----------|
| Producing | Currently producing | **High** — active development |
| Shut In | Temporarily shut in | Medium — was producing |
| Permitted | Permitted, not drilled | Medium — planned activity |
| Drilling | Currently drilling | High — imminent production |
| Plugged | Plugged and abandoned | Low — no activity |
| Inactive | Not producing | Low — may be dormant |
| Orphan | No responsible operator | Low — environmental liability |

### ODNR Well Types (MapSymbol_DESC)

| Value | Description |
|-------|-------------|
| Gas, Horizontal | Horizontal gas well (primary Utica/Marcellus target) |
| Gas, Vertical | Vertical gas well |
| Oil, Horizontal | Horizontal oil well |
| Oil, Vertical | Vertical oil well |
| Injection Well | Class II disposal/EOR |
| Plugged | Plugged well |

### Dormant Mineral Act Triggers (ORC 5301.56)

A mineral interest may be deemed abandoned if, during the preceding **20 years**,
NONE of the following "savings events" have occurred:

| Savings Event | Data Indicator |
|---------------|---------------|
| Title transaction | County recorder records (manual check) |
| Mineral tax filing | County auditor records (via CAMADataSite) |
| Mineral production | ODNR `Last_Nonzero_Production_Year` < current year - 20 |
| Mining/drilling permit | ODNR `WL_STATUS_DESC` = 'Permitted' or 'Drilling' nearby |
| Unitization order | ODNR records (manual check) |
| Preservation notice | County recorder records (manual check) |

---

## Target Counties

Eight eastern Ohio counties in the core Utica/Marcellus Shale play:

| FIPS | County | Mineral Parcels | Utica Wells | Key Operators | Notes |
|------|--------|----------------|-------------|---------------|-------|
| 013 | Belmont | ~600 | ~800 | Ascent, Gulfport, Rice | Major Utica wet/dry gas window |
| 019 | Carroll | ~400 | ~500 | Encino, Rex, Chesapeake | First Utica discoveries (2011) |
| 031 | Columbiana | ~200 | ~200 | Hilcorp, Encino | Northern play edge |
| 067 | Harrison | ~500 | ~600 | Ascent, Gulfport, Eclipse | Active drilling, condensate window |
| 081 | Jefferson | ~300 | ~300 | Ascent, Gulfport, EAP Ohio | Eastern play border |
| 103 | Monroe | ~350 | ~400 | Ascent, Eclipse, SWN | Southern Utica/Pt Pleasant extension |
| 111 | Noble | ~250 | ~300 | Ascent, Gulfport, Rex | Active Utica/Point Pleasant |
| 059 | Guernsey | ~150 | ~200 | Antero, Eclipse | Western productive edge |

Default to these 8 counties unless the user specifies otherwise.

See `references/county_codes.md` for all 88 Ohio counties.

---

## Workflow

### Step 1 — Resolve Intent

Map the user's question to a query mode:

| User Request | Query Mode | Key Parameters |
|-------------|------------|----------------|
| "Mineral parcels in Belmont County" | County mineral query | `County='BELMONT' AND StateLUC LIKE '2%'` |
| "Oil and gas minerals in Harrison" | Filtered mineral query | `County='HARRISON' AND StateLUC IN ('240','250')` |
| "All mineral parcels statewide" | Statewide query | `StateLUC LIKE '2%'` |
| "How many mineral parcels in OH?" | Count query | `returnCountOnly=true` |
| "Mineral parcels by county" | Aggregate query | `groupByFieldsForStatistics=County` |
| "Dormant minerals near wells" | Dormant screening | Mineral query + well correlation + 20-year test |
| "Delinquent minerals in Stark County" | County delinquent | Stark County endpoint + StateLUC filter |
| "Mineral parcels near permit 34013..." | Well-centric search | Spatial query around well location |

Default status filter for wells: `WL_STATUS_DESC='Producing'` (active only).
Default mineral filter: `StateLUC LIKE '2%'` (all mineral types).
Narrow to `StateLUC IN ('240','250')` when the user asks specifically about
oil and gas interests.

### Step 2 — Query OGRIP Mineral Parcels

First, check the count to inform the user:

```bash
curl -s "https://services2.arcgis.com/MlJ0G8iWUyC7jAmu/arcgis/rest/services/OhioStatewidePacels_full_view/FeatureServer/0/query" \
  --data-urlencode "where=County='BELMONT' AND StateLUC LIKE '2%'" \
  --data-urlencode "returnCountOnly=true" \
  --data-urlencode "f=json"
```

Then fetch the parcel data with geometry for well correlation:

```bash
curl -s "https://services2.arcgis.com/MlJ0G8iWUyC7jAmu/arcgis/rest/services/OhioStatewidePacels_full_view/FeatureServer/0/query" \
  --data-urlencode "where=County='BELMONT' AND StateLUC LIKE '2%'" \
  --data-urlencode "outFields=StateParcelID,LocalParcelID,County,StateLUC,MailAddressAll,LandArea,CAMADataSite" \
  --data-urlencode "returnGeometry=true" \
  --data-urlencode "outSR=4326" \
  --data-urlencode "resultRecordCount=100" \
  --data-urlencode "f=json"
```

**Always include `outSR=4326`** when requesting geometry. Without it, OGRIP
returns coordinates in EPSG:3735 (Ohio State Plane South, US feet), which
cannot be used directly for spatial well correlation.

### Step 3 — Cross-reference County Data

For owner names (not in OGRIP), query OIT Parcels 2022:

```bash
curl -s "https://maps.ohio.gov/arcgis/rest/services/Statewide_Parcels_2022/MapServer/0/query" \
  --data-urlencode "where=COUNTY='BELMONT' AND PIN='01-0010-0001.000'" \
  --data-urlencode "outFields=PIN,OWNER1,OWNER2,ASSR_ACRES,AUD_LINK" \
  --data-urlencode "returnGeometry=false" \
  --data-urlencode "f=json"
```

For tax delinquency in counties with GIS data (e.g., Stark County):

```bash
curl -s "https://scgisa.starkcountyohio.gov/arcgis/rest/services/Auditor/StarkCountyParcels/MapServer/0/query" \
  --data-urlencode "where=CERTIFIED_DELINQUENT_YEAR IS NOT NULL" \
  --data-urlencode "outFields=PARCELNO,CERTIFIED_DELINQUENT_YEAR,TOTAL_BILLED,TOTAL_PAID,FINAL_BALANCE" \
  --data-urlencode "resultRecordCount=50" \
  --data-urlencode "f=json"
```

For the 8 target counties that lack GIS delinquent data, use the `CAMADataSite`
link from OGRIP to direct users to the county auditor website for manual
delinquency checks.

### Step 4 — Spatial Well Correlation

For each mineral parcel with geometry, query ODNR wells within a configurable
radius (default: 1 mile = 1,609.34 meters):

```bash
curl -s "https://gis.ohiodnr.gov/arcgis/rest/services/DOG_Services/Oilgas_Wells_public/MapServer/0/query" \
  --data-urlencode "geometry={lon},{lat}" \
  --data-urlencode "geometryType=esriGeometryPoint" \
  --data-urlencode "inSR=4326" \
  --data-urlencode "spatialRel=esriSpatialRelIntersects" \
  --data-urlencode "distance=1609.34" \
  --data-urlencode "units=esriSRUnit_Meter" \
  --data-urlencode "where=WL_STATUS_DESC='Producing'" \
  --data-urlencode "outFields=API_WELLNO,MapSymbol_DESC,CO_NAME,ProducingFormation1,Utica_Shale,Last_Nonzero_Production_Year" \
  --data-urlencode "returnGeometry=false" \
  --data-urlencode "resultRecordCount=50" \
  --data-urlencode "f=json"
```

**Rate limit consideration:** If many mineral parcels match, limit spatial
correlation to the most promising candidates (oil/gas LUC codes 240/250,
largest land area) to avoid excessive API calls.

For dormant mineral screening, expand the radius to 2 miles and query ALL
wells (not just producing) to check `Last_Nonzero_Production_Year` against
the 20-year dormancy threshold.

### Step 5 — Output

Present results as a markdown table followed by a narrative assessment that
includes:
- Mineral parcel counts by StateLUC code
- Nearby well counts and formations (Utica, Marcellus, conventional)
- Dormant Mineral Act screening results (if requested)
- County auditor links for further research
- Operator names and activity levels in the area

---

## Output Format

**Format: Raw Data Table + Narrative with Dormant Mineral Assessment**

### Example Table

```
## Mineral-Coded Parcels — Belmont County, OH

| Parcel ID | StateLUC | Description | Land Area (sf) | Nearby Wells | Utica Wells | Operator | Last Prod Year |
|-----------|----------|-------------|----------------|--------------|-------------|----------|----------------|
| 01-0010-0001 | 240 | Oil & Gas-Working Interest | 1,568,160 | 5 | 4 | ASCENT RESOURCES | 2023 |
| 01-0025-0012 | 250 | Oil & Gas-Royalty Interest | 871,200 | 3 | 2 | GULFPORT ENERGY | 2023 |
| 01-0040-0003 | 220 | Coal Rights-Working Interest | 2,178,000 | 1 | 0 | None | 1998 |
| ... | ... | ... | ... | ... | ... | ... | ... |
```

### Example Narrative

```
**Summary:** Belmont County has 587 mineral-coded parcels in OGRIP, of which
312 are oil and gas interests (StateLUC 240/250), 198 are coal interests
(210/220/230), and 77 are other/custom mineral codes. Shown above are the
top 20 parcels by nearby well density.

**Well Proximity:** Of 312 oil and gas mineral parcels, 245 (79%) have at
least one producing well within 1 mile. The most active area is Mead Township,
where parcel 01-0010-0001 (a 36-acre working interest) has 5 producing wells
within 1 mile, including 4 Utica horizontal wells operated by Ascent Resources.
The most recent production year among nearby wells is 2023.

**Dormant Mineral Screening (ORC 5301.56):** 23 mineral parcels have NO
producing wells within 2 miles and nearby wells show Last_Nonzero_Production_Year
before 2006 (20+ years ago). These parcels are potential candidates for
Dormant Mineral Act proceedings, subject to title examination confirming no
savings events have occurred. The 23 dormant candidates include 8 coal
interests, 11 oil/gas interests, and 4 custom mineral codes.

**Tax Delinquency:** Ohio lacks a statewide delinquent property GIS layer.
For Belmont County, use the county auditor links (CAMADataSite) to check
individual parcel tax status: [link]. Counties with GIS delinquent data
include Stark and Cuyahoga (outside the Utica play area).

**Operator Context:** The dominant operators near mineral parcels in Belmont
County are Ascent Resources (65% of nearby wells), Gulfport Energy (20%),
and Rice/EQT (10%). Active Utica horizontal drilling continues, with 12
wells permitted in 2024-2025.

**Caveats:** Mineral parcel identification relies on StateLUC 200-series
coding, which has good but not perfect coverage in Belmont County. Some
mineral interests may be coded with non-200 codes. Dormant mineral screening
is a DATA SCREEN only — actual applicability of ORC 5301.56 requires title
examination, notice procedures, and legal review.
```

---

## Pagination

**OGRIP Parcels:** Max 2,000 records/request.
**OIT Parcels 2022:** Max 2,000 records/request.
**ODNR Wells:** Max 1,000 records/request.

Use `resultOffset` for pagination. Check `exceededTransferLimit` in the
response:

```python
offset = 0
all_records = []
while True:
    # fetch with resultOffset=offset, resultRecordCount=2000 (or 1000 for ODNR)
    features = response["features"]
    all_records.extend(features)
    if len(features) < limit or not response.get("exceededTransferLimit"):
        break
    offset += limit
```

For the 8 target counties, mineral parcel counts per county (150-600) fit
within a single OGRIP request. Statewide mineral queries (~3,360 total)
need two pages. ODNR well queries for a single county generally fit in one
request when filtered by Utica/producing status.

---

## Error Handling

| HTTP / Error | Meaning | Action |
|-------------|---------|--------|
| 200 + `error` in JSON | Bad query syntax (invalid field, malformed WHERE) | Check field names; verify StateLUC values are quoted strings |
| 200 + `exceededTransferLimit: true` | More records than limit | Paginate with `resultOffset` or narrow filters |
| 200 + empty `features` array | No matching records | Verify county name is uppercase for OGRIP; check StateLUC codes |
| 400 | Malformed request | Check parameter encoding, especially `outStatistics` JSON |
| 500 | Server error | Retry; OGRIP/ODNR services are generally reliable |
| Timeout | Large result set or server load | Reduce `resultRecordCount`; use `returnGeometry=false` |
| Geometry in EPSG:3735 | Missing `outSR=4326` | Add `outSR=4326` to OGRIP queries; ODNR returns WGS84 by default |
| County service unavailable | County GIS server down | Fall back to OGRIP `CAMADataSite` link for auditor website |

---

## Caveats and Data Quality Notes

1. **StateLUC coverage varies by county.** While the 200-series coding
   system is consistent, not all counties fully populate StateLUC for every
   mineral parcel. The 8 target counties in eastern Ohio generally have good
   coverage due to long mineral severance histories, but some mineral
   interests may use non-200 codes. The 3,360 statewide count is a lower
   bound.

2. **No statewide delinquent property layer.** Unlike West Virginia (which
   has a statewide Delinquent_Properties layer), Ohio's tax delinquent data
   is fragmented across county auditor systems. Only a few counties (Stark,
   Cuyahoga, Lucas, Lorain, Mahoning) publish GIS-accessible delinquent
   data. For the 8 target Utica counties, delinquency must be checked
   through county auditor websites via the `CAMADataSite` field.

3. **Dormant Mineral Act is a screening tool, not a determination.** The
   `Last_Nonzero_Production_Year` field and well proximity data provide
   indicators, not legal conclusions. ORC 5301.56 requires examining all
   savings events (title transactions, tax filings, preservation notices,
   unitization orders) — most of which are not available through GIS
   services. Legal counsel is required.

4. **OGRIP coordinates are EPSG:3735 natively.** Always include `outSR=4326`
   when requesting geometry from OGRIP. Without it, coordinates are in Ohio
   State Plane South (US feet) — large numbers that cannot be used for
   spatial correlation with ODNR wells (which use WGS84). This is a common
   mistake.

5. **OGRIP lacks owner names.** The primary OGRIP endpoint does not include
   owner names. Use the OIT Statewide Parcels 2022 endpoint for `OWNER1`/
   `OWNER2` fields, but note it is 2022 vintage and may not reflect recent
   transfers. County auditor websites (via `CAMADataSite`) have current data.

6. **County name format differences.** OGRIP uses uppercase county names
   (e.g., "BELMONT"). ODNR uses mixed case (e.g., "Belmont"). Normalize
   case when joining across sources. See `references/county_codes.md` for
   the mapping.

7. **Mineral parcel acreage.** OGRIP provides `LandArea` in square feet,
   not acres. Divide by 43,560 to convert. The OIT 2022 dataset provides
   `ASSR_ACRES` directly.

8. **ODNR production data scope.** The `Last_Nonzero_Production_Year` field
   indicates when a well last produced, but full production volumes (MCF,
   BBL) are not in the MapServer layer. Full production data is available
   through the ODNR Division of Oil and Gas Resources production reporting
   system separately.

9. **1-mile radius is a starting point.** Utica horizontal wells have
   laterals extending 5,000-15,000+ feet. A 1-mile radius catches most
   nearby wellheads, but the subsurface lateral may extend further. Increase
   to 2 miles for more comprehensive results; use 0.5 miles for tighter
   correlation.

10. **2006 Dormant Mineral Act amendment.** The 2006 amendment to ORC 5301.56
    strengthened mineral owner protections by expanding the list of savings
    events and imposing stricter notice requirements. Pre-2006 cases may
    have different precedent. Ohio courts have also applied the Act
    inconsistently, particularly regarding the "known owner" savings event.

---

## Implementation Notes

- **Prefer `bash_tool` with `curl` + `jq`** for API calls in Claude's
  environment
- **Use `curl -s`** (not `-sk`) for all Ohio endpoints — OGRIP, OIT, and
  ODNR all have valid SSL certificates (unlike WVDEP in West Virginia)
- **Always include `outSR=4326`** in OGRIP queries requesting geometry;
  the native SRS is EPSG:3735 (Ohio State Plane South, US feet)
- **ODNR max is 1,000** (lower than OGRIP's 2,000) — adjust pagination
  accordingly
- **Python example** — see `references/python_example.py` (stdlib only:
  urllib, json, ssl, argparse) with dormant mineral screening
- **OGRIP parcel reference** — see `references/ogrip_parcels.md` for full
  schema, mineral LUC codes, and coordinate system details
- **ODNR well reference** — see `references/odnr_wells.md` for layer listing,
  field definitions, and well type/status enumerations
- **Land use codes** — see `references/land_use_codes.md` for full 200-series
  breakdown, Dormant Mineral Act summary, and OH vs WV/PA comparison
- **County codes** — see `references/county_codes.md` for all 88 Ohio
  counties and 8 target county statistics
- The OGRIP endpoint URL has a typo ("Pacels" not "Parcels") — this is the
  actual production URL, do not change it
- `outStatistics` must be valid JSON — use single quotes around the curl
  argument and double quotes inside the JSON
- For high-value targets, use `pnge-gis-mapper` to create an interactive
  map showing mineral parcels colored by StateLUC code with nearby well
  locations
