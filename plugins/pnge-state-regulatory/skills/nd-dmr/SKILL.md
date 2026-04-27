---
name: nd-dmr
description: >
  Query North Dakota Department of Mineral Resources (DMR) oil and gas data —
  well search, production by well or field, injection volumes, drilling rig
  activity, and formation-level statistics. Use this skill when the user asks
  about North Dakota wells, Bakken production, Bakken lithium, Three Forks
  wells, Williston Basin data, ND oil production, North Dakota injection wells,
  ND produced water, McKenzie County production, NDIC well search, North Dakota
  drilling rigs, ND monthly production reports, Director's Cut, or any North
  Dakota upstream regulatory data. Critical for lithium research — Bakken
  produced waters contain 10-70 mg/L Li. Produces data tables with narrative
  summaries.
---

# North Dakota Department of Mineral Resources (DMR) Data Skill

Queries North Dakota oil and gas regulatory data from the DMR (formerly NDIC Oil
and Gas Division). North Dakota is the #3 oil producing state, dominated by
Bakken/Three Forks production in the Williston Basin.

## API Key Handling

**No API key required.** All DMR public data queries, production reports, well
searches, and GIS services are freely accessible without authentication.

---

## Data Access Architecture

The DMR provides data through four channels:

1. **Web Query Applications** — well search, production reports, activity reports
2. **GIS Map Server** — spatial data with ArcGIS REST services
3. **Statistics Portal** — downloadable production summaries and historical data
4. **Monthly/Daily Reports** — PDF reports with production and drilling data

### Channel 1: Web Query Applications

| Application | URL | Data |
|-------------|-----|------|
| Well Search | `https://www.dmr.nd.gov/oilgas/findwellsvw.asp` | Search by operator, field, section/township/range |
| Daily Activity Reports | `https://www.dmr.nd.gov/oilgas/dailyindex.asp` | Daily drilling and completion activity |
| Active Drilling Rigs | `https://www.dmr.nd.gov/oilgas/riglist.asp` | Current rig count and locations |
| Monthly Production Reports | `https://www.dmr.nd.gov/oilgas/mprindex.asp` | Searchable PDFs, 2003-present |
| Hearing Dockets | `https://www.dmr.nd.gov/oilgas/docketindex.asp` | Regulatory hearing records |

### Channel 2: GIS Map Server

**URL:** `https://gis.dmr.nd.gov`

The DMR GIS Map Server provides spatial data for wells, fields, units, and
infrastructure. Standard ArcGIS REST query patterns apply.

```bash
# Discover available map services:
curl -s "https://gis.dmr.nd.gov/arcgis/rest/services?f=json" | jq '.services[] | {name, type}'

# Query a well layer (example — identify the service and layer index first):
curl -s "https://gis.dmr.nd.gov/arcgis/rest/services/OilGas/OilGas_Wells/MapServer/0/query" \
  --data-urlencode "where=1=1" \
  --data-urlencode "outFields=*" \
  --data-urlencode "resultRecordCount=5" \
  --data-urlencode "f=json"

# Note: Service names and layer indexes may change. Always discover first by
# querying the services directory and then the specific service layers.
```

### Channel 3: Statistics Portal

**URL:** `https://www.dmr.nd.gov/oilgas/stats/statisticsvw.asp`

Comprehensive downloadable statistics:

| Dataset | Format | Coverage |
|---------|--------|----------|
| Monthly Oil Production by County | PDF | 1980-present |
| Oil Production by Formation | Spreadsheet | 1998-present |
| Gas Production by Formation | Spreadsheet | 1998-present |
| Cumulative Oil Production by Formation | Spreadsheet | Cumulative totals |
| Historical Annual Production | PDF | Full history |
| County Oil Production Charts | Charts/PDF | 17 producing counties |
| Gas Production and Sales | Spreadsheet | Current |
| Historical Drilling Statistics | Varies | Full history |

### Channel 4: Director's Cut and Monthly Reports

The DMR Director's Cut is a monthly briefing with key statistics:

```bash
# Monthly Production Reports (PDF, searchable):
# https://www.dmr.nd.gov/oilgas/mprindex.asp
# Select year (2003-2026) to access monthly PDFs

# Director's Cut — monthly summary with commentary:
# Published ~45 days after production month
# Subscribe via email at: https://www.dmr.nd.gov/oilgas/mprindex.asp
```

---

## Query Patterns

### Well Search

The well search form accepts these parameters:

| Parameter | Values | Notes |
|-----------|--------|-------|
| Operator | Dropdown of all active/historical operators | e.g., "CONTINENTAL RESOURCES" |
| Field | Dropdown of all fields | e.g., "BAKKEN", "ALEXANDER" |
| Section | 1-36 | Township subdivision |
| Township | 129-164 | North-south coordinate |
| Range | 47-107 | East-west coordinate |

```bash
# Well search is form-based. Example POST:
curl -s "https://www.dmr.nd.gov/oilgas/findwellsvw.asp" \
  --data-urlencode "TEFLD=BAKKEN" \
  --data-urlencode "Submit=Submit"
# Response is HTML with well list. Parse for file numbers, API numbers,
# well names, operators, locations, and status.

# Individual well data by file number:
# https://www.dmr.nd.gov/oilgas/feeservices/getwellprod.asp?fiession=XXXXX
# (URL pattern may vary; check current DMR site)
```

### GIS Map Server Queries

```bash
# Step 1: List available services
curl -s "https://gis.dmr.nd.gov/arcgis/rest/services?f=json" \
  | jq '.services[] | {name, type}'

# Step 2: Inspect a specific service (e.g., OilGas wells)
curl -s "https://gis.dmr.nd.gov/arcgis/rest/services/OilGas/OilGas_Wells/MapServer?f=json" \
  | jq '.layers[] | {id, name}'

# Step 3: Query wells in McKenzie County
curl -s "https://gis.dmr.nd.gov/arcgis/rest/services/OilGas/OilGas_Wells/MapServer/0/query" \
  --data-urlencode "where=COUNTY='MCKENZIE'" \
  --data-urlencode "outFields=*" \
  --data-urlencode "resultRecordCount=10" \
  --data-urlencode "f=json"

# Step 4: Spatial query — wells within a bounding box
curl -s "https://gis.dmr.nd.gov/arcgis/rest/services/OilGas/OilGas_Wells/MapServer/0/query" \
  --data-urlencode "geometry=-104.0,47.5,-103.0,48.5" \
  --data-urlencode "geometryType=esriGeometryEnvelope" \
  --data-urlencode "spatialRel=esriSpatialRelIntersects" \
  --data-urlencode "outFields=*" \
  --data-urlencode "resultRecordCount=10" \
  --data-urlencode "f=json"
```

### Production by Formation

```bash
# Download production-by-formation spreadsheets from the Statistics portal:
# https://www.dmr.nd.gov/oilgas/stats/statisticsvw.asp
# Available: Oil Production by Formation (1998-2025), Gas Production by Formation

# Key formations tracked:
# BAKKEN (dominant), THREE FORKS, MADISON, MISSION CANYON, DUPEROW,
# SPEARFISH, LODGEPOLE, RED RIVER, TYLER, RATCLIFFE
```

---

## Workflow

### Step 1 — Resolve Intent

| User wants... | Best channel |
|--------------|-------------|
| Specific well details | Well Search or GIS Map Server |
| Production by formation | Statistics Portal spreadsheets |
| County production totals | Monthly Production Reports (PDF) or Statistics |
| Current drilling activity | Active Drilling Rigs / Daily Activity Reports |
| Spatial analysis / mapping | GIS Map Server (ArcGIS REST) |
| State-level summary | Director's Cut monthly report |
| Bakken vs. Three Forks comparison | Production by Formation spreadsheets |

### Step 2 — Fetch Data

For individual wells, use the Well Search form or GIS Map Server query.
For formation-level or county-level analysis, download Statistics portal files.
For spatial queries, use the GIS Map Server REST endpoint with JSON output.

### Step 3 — Parse Response

- Well Search returns HTML (parse for well records)
- GIS Map Server returns JSON with `f=json` parameter
- Statistics files are spreadsheets (Excel/CSV) or PDF
- Monthly Production Reports are searchable PDFs

### Step 4 — Produce Output

**Format: Raw Data Table + Narrative**

```
## North Dakota Bakken Formation Production (Monthly, 2023-2024)

| Period   | Oil (BBL)    | Gas (MCF)      | Wells  |
|----------|--------------|----------------|--------|
| 2024-06  | 35,200,000   | 105,400,000    | 12,450 |
| 2024-05  | 34,800,000   | 103,900,000    | 12,380 |
| ...      | ...          | ...            | ...    |

**Summary:** Bakken production averaged 35.2 million barrels/month (1.17 million
BOPD) in June 2024 from 12,450 producing wells. The Bakken accounts for ~93% of
ND oil production. Three Forks adds another ~5%. Peak ND production was 1.52
million BOPD in November 2019. Data from DMR monthly production reports;
preliminary for most recent 2 months.
```

---

## North Dakota Geographic Reference

### Key Producing Counties

| County | Location | Notes |
|--------|----------|-------|
| McKenzie | NW ND | #1 oil county, heart of Bakken |
| Mountrail | NW ND | #2 oil county, Parshall Field |
| Williams | NW ND | Williston area |
| Dunn | W-central ND | Killdeer area |
| Divide | NW corner | Border county |
| Burke | N-central ND | Northern Bakken extent |
| Stark | SW ND | Dickinson area |
| Bowman | SW ND | Southern Williston Basin |

### Formations Critical for Li/Mg Research

- **Bakken Formation:** The primary target. Bakken produced waters contain
  10-70 mg/L lithium with high TDS (200,000-350,000 mg/L). The Three Forks
  (underlying the Bakken) has similar chemistry. At ~1.1 million BOPD with
  water cuts increasing as the play matures, significant produced water volumes
  are available.
- **Madison Group (Mississippian):** Deeper, older formation with higher TDS
  and potentially higher Li concentrations. Less production volume than Bakken.
- **Red River Formation (Ordovician):** Very high TDS brines (300,000+ mg/L)
  with elevated lithium. Limited modern production but historically significant.

### Lithium in Bakken Context

- Li concentration: 10-70 mg/L (most wells 20-50 mg/L)
- Economic DLE threshold: ~100-150 mg/L
- Bakken Li is sub-economic at current DLE costs but could become viable with:
  - Technology improvements reducing DLE costs
  - Co-production with other valuable elements (Mg, Br, I)
  - Volume-based processing (1+ million BBL/day available)
- USGS Produced Waters DB has 100+ Bakken brine analyses with Li data

---

## Error Handling

| Condition | Meaning | Action |
|-----------|---------|--------|
| Well Search returns empty | No matching wells for criteria | Verify operator name spelling; try broader field search |
| GIS Map Server 404 | Service name changed | Re-discover services at base URL; DMR updates service names periodically |
| GIS query returns error JSON | Invalid field name or query syntax | Query the service metadata first to get valid field names |
| PDF not loading | Monthly report not yet published | Reports publish ~45 days after production month; check earlier month |
| Statistics spreadsheet unavailable | File being updated | Retry; check if year is available (formation data starts 1998) |
| "Data is updating hourly" notice | Real-time refresh in progress | Data should be current; this is a status message, not an error |

---

## Caveats and Data Limitations

1. **Well Search is form-based:** The DMR well search returns HTML, not JSON.
   For JSON output, use the GIS Map Server REST endpoints.
2. **GIS service names may change:** The DMR periodically updates its GIS
   services. Always discover available services at the base URL before querying.
3. **Production data is PDF-primary:** Monthly production reports are published
   as searchable PDFs, not machine-readable formats. The Statistics portal
   spreadsheets are more useful for programmatic analysis.
4. **No Excel for monthly reports:** The DMR explicitly does not provide Excel
   versions of monthly production reports due to amendment discrepancies.
5. **Data lag:** Production data lags ~45 days. The Director's Cut provides
   preliminary estimates sooner but revises frequently.
6. **Water production not separately reported:** Unlike some states, ND does not
   require separate produced water volume reporting at the well level. Water
   volumes must be inferred from injection/disposal reports or estimated.
7. **Bakken water cut increasing:** As the Bakken play matures, water cuts are
   rising (now 50-70% in older wells), increasing produced water availability
   but also increasing disposal costs — a driver for beneficial reuse including
   mineral extraction.
