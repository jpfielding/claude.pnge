---
name: usgs-waterdata
description: >
  Query real-time and historical water data from the USGS National Water
  Information System (NWIS) and Water Quality Portal. Use this skill when the
  user asks about streamflow, groundwater levels, water quality near oil and
  gas sites, baseline water chemistry, specific conductance, TDS, lithium or
  magnesium concentrations in surface water or groundwater, gage height,
  discharge, water temperature, dissolved oxygen, pH, or any USGS hydrologic
  monitoring data. Trigger for phrases like "streamflow at site", "water
  quality near wells", "lithium in groundwater", "USGS gage data",
  "specific conductance trend", "TDS in produced water area", "baseline
  water chemistry", "NWIS data", "groundwater levels WV", or any request
  for U.S. water monitoring station data. Covers 1.5M+ stations nationwide.
  Also queries the Water Quality Portal for analyte-specific lab results
  including Li, Mg, Ca, Na, Cl, SO4, Fe, Mn, and TDS.
---

# USGS Water Data Skill

Fetches and analyzes U.S. water data from USGS NWIS Water Services
(waterservices.usgs.gov) and the Water Quality Portal (waterqualitydata.us).

## API Key Handling

**No API key required.** All USGS Water Services and Water Quality Portal
endpoints are public and free to use with no authentication.

Rate limits are informal -- USGS asks users to be reasonable. Avoid
rapid-fire requests; batch by site list rather than looping individual sites.

---

## API Structure

Two primary systems serve different data types:

### 1. USGS NWIS Water Services

**Base URL:** `https://waterservices.usgs.gov/nwis/`

| Endpoint | Purpose | Typical Use |
|----------|---------|-------------|
| `iv/`    | Instantaneous values (real-time, 15-min) | Current conditions, last 120 days |
| `dv/`    | Daily values (daily mean/min/max) | Historical time series, long-term trends |
| `site/`  | Site information and metadata | Find monitoring stations by location/type |
| `stat/`  | Daily/monthly/annual statistics | Long-term normals, percentiles |
| `gwlevels/` | Groundwater level measurements | Well water level history |

### 2. Water Quality Portal (WQP)

**Base URL:** `https://www.waterqualitydata.us/data/`

| Endpoint | Purpose |
|----------|---------|
| `Station/search` | Find monitoring locations by analyte, location, org |
| `Result/search`  | Lab analytical results (concentrations, detections) |
| `Activity/search` | Sampling events metadata |

WQP aggregates data from USGS, EPA STORET, and USDA ARS into a single
searchable interface. This is the primary source for water chemistry
lab results (Li, Mg, Ca, TDS, etc.).

---

## Key Parameter Codes (NWIS)

Parameters most relevant to petroleum engineering and produced water research:

### Physical Properties
| Code  | Parameter | Units |
|-------|-----------|-------|
| 00010 | Water temperature | deg C |
| 00060 | Discharge (streamflow) | ft3/s |
| 00065 | Gage height | ft |
| 00095 | Specific conductance | uS/cm @ 25C |
| 00300 | Dissolved oxygen | mg/L |
| 00400 | pH | standard units |

### Major Ions and Key Analytes
| Code  | Parameter | Units |
|-------|-----------|-------|
| 00915 | Calcium, dissolved | mg/L |
| 00925 | Magnesium, dissolved | mg/L |
| 00930 | Sodium, dissolved | mg/L |
| 00935 | Potassium, dissolved | mg/L |
| 00940 | Chloride, dissolved | mg/L |
| 00945 | Sulfate, dissolved | mg/L |
| 00950 | Fluoride, dissolved | mg/L |
| 01130 | Lithium, dissolved | ug/L |
| 01046 | Iron, dissolved | ug/L |
| 01056 | Manganese, dissolved | ug/L |
| 70300 | Total dissolved solids (residue at 180C) | mg/L |

### PNGE Research Notes
- **Lithium (01130):** Reported in ug/L (ppb). Divide by 1000 for mg/L.
  Economic DLE cutoff is ~100-150 mg/L (~100,000-150,000 ug/L).
  Most surface/groundwater Li is 1-100 ug/L; elevated values near O&G
  operations may indicate produced water influence.
- **Specific conductance (00095):** Quick proxy for TDS. Approximate
  TDS (mg/L) = SC (uS/cm) x 0.55-0.75 depending on ionic composition.
- **Chloride (00940):** Elevated Cl is a primary indicator of brine
  contamination in fresh water systems.

---

## Site Type Codes

| Code | Description | Relevance |
|------|-------------|-----------|
| ST   | Stream | Surface water baseline monitoring |
| GW   | Groundwater (well) | Aquifer monitoring near O&G sites |
| SP   | Spring | Natural discharge points, may show deep formation influence |
| LK   | Lake/reservoir | Surface water storage |
| AT   | Atmosphere | Precipitation chemistry |
| OC   | Ocean/estuary | Offshore/coastal monitoring |

---

## Workflow

### Step 1 -- Resolve Intent

Map the user's question to the right endpoint and parameters:

| User Intent | Endpoint | Key Params |
|-------------|----------|------------|
| "Current streamflow at site X" | `iv/` | sites, parameterCd=00060 |
| "Historical daily flow" | `dv/` | sites, parameterCd=00060, startDT, endDT |
| "Find groundwater wells in county" | `site/` | countyCd (5-digit FIPS), siteType=GW |
| "Water quality / chemistry" | WQP `Result/search` | characteristicName, statecode |
| "Lithium in groundwater near X" | WQP `Result/search` | characteristicName=Lithium, statecode |
| "Long-term flow statistics" | `stat/` | sites, parameterCd, statReportType |
| "Groundwater levels" | `gwlevels/` | sites or stateCd, startDT, endDT |

### Step 2 -- Find Sites (when needed)

If the user does not provide a site number, find relevant sites first:

```bash
# Find all active groundwater sites in Monongalia County, WV
# countyCd uses full 5-digit FIPS (state+county) as a standalone location filter
curl -s "https://waterservices.usgs.gov/nwis/site/?format=rdb\
&countyCd=54061&siteType=GW&siteStatus=active"

# Find sites with specific conductance data in WV
curl -s "https://waterservices.usgs.gov/nwis/site/?format=rdb\
&stateCd=WV&parameterCd=00095&siteType=GW&hasDataTypeCd=dv"

# Find sites within a bounding box (lon/lat: west,south,east,north)
curl -s "https://waterservices.usgs.gov/nwis/site/?format=rdb\
&bBox=-80.5,39.0,-79.5,40.0&siteType=GW&siteStatus=active"
```

**County FIPS codes** (WV examples, use 5-digit state+county for NWIS `countyCd`):
Monongalia=54061, Marion=54049, Wetzel=54103, Tyler=54095,
Doddridge=54017, Harrison=54033, Marshall=54051.
Full list: https://www.census.gov/library/reference/code-lists/ansi.html

### Step 3 -- Fetch Data

**NWIS Daily Values (JSON):**
```bash
curl -s "https://waterservices.usgs.gov/nwis/dv/?format=json\
&sites=03058500\
&parameterCd=00060\
&startDT=2024-01-01\
&endDT=2024-12-31"
```

**NWIS Instantaneous Values (JSON):**
```bash
# Most recent readings (default: last ~4 hours)
curl -s "https://waterservices.usgs.gov/nwis/iv/?format=json\
&sites=03058500\
&parameterCd=00060,00065"
```

**NWIS Site Info (RDB):**
```bash
curl -s "https://waterservices.usgs.gov/nwis/site/?format=rdb\
&sites=03058500\
&siteOutput=expanded"
```

**NWIS Statistics (RDB):**
```bash
curl -s "https://waterservices.usgs.gov/nwis/stat/?format=rdb\
&sites=03058500\
&parameterCd=00060\
&statReportType=daily\
&statTypeCd=mean"
```

**Water Quality Portal -- Lab Results (CSV):**
```bash
# Lithium results in West Virginia
curl -s "https://www.waterqualitydata.us/data/Result/search?\
statecode=US:54\
&characteristicName=Lithium\
&mimeType=csv\
&zip=no\
&dataProfile=narrowResult"

# Chloride at a specific USGS site
curl -s "https://www.waterqualitydata.us/data/Result/search?\
siteid=USGS-03058500\
&characteristicName=Chloride\
&mimeType=csv\
&zip=no\
&dataProfile=narrowResult"
```

**Water Quality Portal -- Stations (CSV):**
```bash
# Stations with lithium data in WV
curl -s "https://www.waterqualitydata.us/data/Station/search?\
statecode=US:54\
&characteristicName=Lithium\
&mimeType=csv\
&zip=no"
```

### Step 4 -- Parse Response

**NWIS JSON response structure (iv/ and dv/):**
```
{
  "value": {
    "queryInfo": { ... },
    "timeSeries": [
      {
        "sourceInfo": {
          "siteName": "WEST FORK RIVER AT BUTCHERVILLE, WV",
          "siteCode": [{"value": "03058500", "agencyCode": "USGS"}],
          "geoLocation": { "geogLocation": {"latitude": 39.09, "longitude": -80.47} }
        },
        "variable": {
          "variableCode": [{"value": "00060"}],
          "variableName": "Streamflow, ft3/s",
          "unit": {"unitCode": "ft3/s"}
        },
        "values": [
          {
            "value": [
              {"value": "255", "dateTime": "2024-01-01T00:00:00.000", "qualifiers": ["A"]}
            ],
            "qualifier": [
              {"qualifierCode": "A", "qualifierDescription": "Approved for publication"}
            ]
          }
        ]
      }
    ]
  }
}
```

**NWIS RDB format (site/, stat/):**
Tab-delimited text with comment lines starting with `#`. Two header rows:
1. Column names
2. Column widths/types (e.g., `5s`, `15s`, `16n`)

Skip lines starting with `#` and the second header row when parsing.

**WQP CSV format:**
Standard CSV with header row. Key columns for Result/search narrowResult:
- `MonitoringLocationIdentifier` -- site ID (e.g., USGS-03058500)
- `ActivityStartDate` -- sample collection date
- `CharacteristicName` -- analyte name (e.g., Lithium)
- `ResultMeasureValue` -- measured concentration
- `ResultMeasure/MeasureUnitCode` -- units (mg/L, ug/L, etc.)
- `ResultSampleFractionText` -- Dissolved, Total, etc.
- `ResultStatusIdentifier` -- Historical, Accepted, Preliminary

**Qualifier codes (NWIS):**
| Code | Meaning |
|------|---------|
| A    | Approved for publication |
| P    | Provisional (subject to revision) |
| e    | Estimated value |
| <    | Below detection limit |
| >    | Above quantitation limit |

### Step 5 -- Produce Output

**Format: Raw Data Table + Narrative**

Present a markdown table of the most relevant rows (cap at ~20 rows for
readability), then a narrative summary covering:

1. **Current state** -- most recent value(s), site name, and date
2. **Trend** -- direction and magnitude over the time window
3. **Notable features** -- peaks, troughs, seasonal patterns
4. **Water quality context** -- how values compare to drinking water
   standards or baseline ranges
5. **Units and caveats** -- always state units; note provisional data

**Example output structure:**
```
## West Fork River at Butcherville, WV -- Daily Mean Discharge (2024)

| Date       | Discharge (ft3/s) | Qualifier |
|------------|-------------------|-----------|
| 2024-01-31 | 802               | A         |
| 2024-01-30 | 927               | A         |
| ...        | ...               | ...       |

**Summary:** Mean daily discharge at USGS 03058500 (West Fork River at
Butcherville, WV) ranged from 147 to 1,400 ft3/s during January 2024.
Peak flow of 1,400 ft3/s occurred Jan 28 following a regional rain event.
Baseflow conditions (~200-250 ft3/s) prevailed in early January. All
values are approved (qualifier A). Drainage area is approximately X sq mi.
```

**For water quality results:**
```
## Lithium Concentrations in WV Groundwater (USGS/WQP)

| Site ID          | Site Name           | Date       | Li (ug/L) | Fraction  |
|------------------|---------------------|------------|-----------|-----------|
| USGS-393138...   | Mcd-0204            | 1955-12-13 | 1600      | Dissolved |
| USGS-394315...   | ...                 | 1955-12-03 | 8200      | Dissolved |

**Summary:** Lithium concentrations in WV groundwater samples range from
non-detect to 8,200 ug/L (8.2 mg/L). The highest values are associated
with deep formation brines. For context, typical fresh groundwater contains
1-50 ug/L Li; values above 100 ug/L may indicate interaction with
formation waters or produced water influence. The economic DLE threshold
is approximately 100-150 mg/L (100,000-150,000 ug/L).
```

---

## Pagination and Large Datasets

**NWIS:** No explicit pagination. Results are returned in full for the
query parameters. For very large requests:
- Limit date ranges (startDT/endDT)
- Query specific sites rather than statewide
- Use `siteStatus=active` to reduce site counts

**WQP:** Large result sets may time out. Mitigate with:
- Use `zip=yes` for large downloads (returns .zip)
- Narrow by date: `startDateLo=2020-01-01&startDateHi=2024-12-31`
- Use `dataProfile=narrowResult` to reduce columns
- Limit by `characteristicName` or `siteid`

If a statewide WQP query returns more than ~10,000 rows, warn the user
and suggest narrowing filters or downloading the CSV for local analysis.

---

## Error Handling

| HTTP Code | Meaning | Action |
|-----------|---------|--------|
| 400 | Bad request (invalid param) | Check parameter codes, date format (YYYY-MM-DD), state codes |
| 404 | Endpoint not found | Verify base URL and endpoint path |
| 503 | Service unavailable | Retry after 30 seconds; NWIS has maintenance windows |
| 200 + empty timeSeries | No data for query | Broaden date range, check site has the requested parameter |
| Timeout | Large query | Narrow filters: fewer sites, shorter date range, specific params |

**Common mistakes to avoid:**
- Date format must be `YYYY-MM-DD` (not `YYYY-MM`)
- State codes are 2-letter postal (WV, PA, OH), not FIPS for NWIS;
  WQP uses `US:54` format (US: + 2-digit FIPS)
- Site numbers must be zero-padded (e.g., `03058500` not `3058500`)
- Parameter codes are 5-digit strings (e.g., `00060` not `60`)
- WQP `characteristicName` is case-sensitive (use `Lithium` not `lithium`)

---

## Geo Reference

**WV County FIPS codes** (most relevant for Marcellus/Utica O&G):
| County | FIPS | O&G Activity |
|--------|------|-------------|
| Monongalia | 061 | Active Marcellus |
| Marion | 049 | Active Marcellus |
| Harrison | 033 | Active Marcellus |
| Doddridge | 017 | Active Marcellus |
| Wetzel | 103 | Active Marcellus |
| Tyler | 095 | Active Marcellus |
| Marshall | 051 | Active Marcellus |
| Ritchie | 085 | Active Marcellus |
| Lewis | 041 | Moderate Marcellus |

**Hydrologic Unit Codes (HUC)** for WV major basins:
- 05020001 -- Tygart Valley River
- 05020002 -- West Fork River
- 05020003 -- Monongahela River (middle)
- 05020004 -- Cheat River
- 05050002 -- Greenbrier River
- 05050008 -- Kanawha River

---

## Implementation Notes

- **Prefer `bash_tool`** with `curl` + `jq` for JSON (NWIS) or direct
  CSV parsing for WQP results
- **Python client** -- see `references/python_example.py` (stdlib-only,
  no third-party packages)
- **RDB parsing** -- skip lines starting with `#` and the second header
  row (width specifiers), then split on tabs
- **JSON path for time series values:**
  `$.value.timeSeries[*].values[0].value[*]`
- **NWIS updates:** Instantaneous values every 15 minutes; daily values
  posted next day; approved data may lag 6-12 months
- **WQP updates:** Quarterly data loads from contributing agencies;
  historical data back to 1900s for some sites
- **Provisional data disclaimer:** USGS provisional data are subject to
  revision. Always note qualifier codes in output.
- See `references/api_reference.md` for complete parameter documentation
