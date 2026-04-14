---
name: tx-rrc
description: >
  Query Texas Railroad Commission (RRC) oil and gas data — production by lease
  or operator, wellbore details, UIC injection and disposal permits, drilling
  permits, and completion records. Use this skill when the user asks about Texas
  oil and gas wells, Permian Basin production, Eagle Ford output, Smackover East
  Texas brines, Texas injection wells, disposal well volumes, H-10 reports,
  Texas drilling permits, RRC district data, Texas lease production, produced
  water volumes in Texas, or any Texas upstream regulatory data. Covers all 10
  RRC districts. Critical for lithium and magnesium research in the Smackover
  Formation (East Texas) and Permian Basin produced water chemistry. Produces
  data tables with narrative summaries.
---

# Texas Railroad Commission (RRC) Data Skill

Queries Texas oil and gas regulatory data from the Railroad Commission of Texas.
The RRC maintains the most comprehensive state-level oil and gas database in the
U.S., covering 400,000+ wells across 10 regulatory districts.

## API Key Handling

**No API key required.** All RRC public data queries and bulk downloads are
freely accessible without authentication.

**Important:** The RRC warns that automated scraping of their web query tools
may result in session termination. For large-scale data retrieval, use the bulk
download files from the RRC Managed File Transfer (MFT) server instead of
screen-scraping the web applications.

---

## Data Access Architecture

The RRC provides data through three channels:

1. **Web Query Applications** — interactive search forms (not REST APIs)
2. **Bulk Data Downloads** — flat files via MFT server (preferred for research)
3. **GIS Viewer** — spatial data (ESRI-based, no public REST service documented)

### Channel 1: Web Query Applications

These are form-based web apps. Use `curl` with form parameters for programmatic
access, but respect rate limits and the automated-access warning.

| Application | URL | Data |
|-------------|-----|------|
| Production Data Query (PDQ) | `https://webapps.rrc.texas.gov/PDQ/generalReportAction.do` | Statewide production by lease, operator, field, district, county |
| Production Reports (Form PR) | `https://webapps.rrc.texas.gov/PR/publicQueriesMainAction.do` | Operator production report filings |
| Wellbore Query | `https://webapps2.rrc.texas.gov/EWA/wellboreQueryAction.do` | Well construction, completion, status, API number |
| UIC Permit Query | `https://webapps2.rrc.texas.gov/EWA/uicQueryAction.do` | Underground injection control permits |
| H-10 Disposal/Injection Report | `https://webapps.rrc.texas.gov/H10/h10PublicMain.do` | Annual disposal/injection well monitoring |
| Drilling Permit Query | `https://webapps2.rrc.texas.gov/EWA/drillingPermitQueryAction.do` | Drilling permit (W-1) details |

### Channel 2: Bulk Data Downloads (Preferred for Research)

All datasets available at: `https://www.rrc.texas.gov/resource-center/research/data-sets-available-for-download/`

Download via the RRC MFT server (`mft.rrc.texas.gov`). Key datasets:

| Dataset | Format | Update Frequency |
|---------|--------|-----------------|
| Production Data Query Dump | CSV | Monthly (last Saturday) |
| Full Wellbore Database | EBCDIC/ASCII | Weekly |
| Drilling Permits with Coordinates | ASCII | Nightly |
| Completion Data | ASCII (zipped) | Nightly |
| UIC Database | EBCDIC/ASCII | Monthly (3rd workday) |
| Oil Ledger (Districts 1-10) | EBCDIC | Monthly (20th) |
| Gas Ledger (Districts 1-10) | EBCDIC | Monthly (20th) |
| Statewide API Data | ASCII/dBase | Twice weekly |
| Well Layers by County | Shapefile | Twice weekly |
| Pipeline Layers by County | Shapefile | Twice weekly |

### Channel 3: GIS Viewer

**Public GIS Viewer:** `https://gis.rrc.texas.gov/GISViewer/`
- Well locations, pipeline routes, survey data, lease boundaries
- Search by API number, lease ID, pipeline T-4 permit
- ESRI-based; no documented public ArcGIS REST endpoint

---

## Query Patterns

### Production Data Query (PDQ)

The PDQ web form accepts these parameters:

| Parameter | Values | Notes |
|-----------|--------|-------|
| View by | Lease, Operator, Field, District, County | Choose one perspective |
| Date range | Jan 1993 - present | Month/year selectors |
| Resource type | Both, Oil Leases, Gas Wells | Filter by commodity |
| District | Statewide, 01-10, 6E, 7B, 7C, 8A | RRC regulatory district |
| County | Any of 254 Texas counties | Optional geographic filter |
| Operator | Operator name | Optional filter |
| Field | Field name | Optional filter |

**Example — Query Permian Basin production (District 8):**
```bash
# Note: This is a form-based application. For bulk research, download the
# Production Data Query Dump CSV from the MFT server instead.
# The web form URL for interactive queries:
# https://webapps.rrc.texas.gov/PDQ/generalReportAction.do

# For bulk download (preferred), get the monthly CSV dump:
# Visit: https://www.rrc.texas.gov/resource-center/research/data-sets-available-for-download/
# Download: "Production Data Query Dump" (CSV, updated last Saturday each month)
```

### Wellbore Query

Search parameters:

| Parameter | Values |
|-----------|--------|
| Well Classification | Oil Wells, Gas Wells, Both |
| District | 01-10 (including 6E, 7B, 7C, 8A) |
| County | 254 Texas counties |
| API Unique No. | 42-XXX-XXXXX format |
| Drilling Permit Number | Numeric |
| Lease/Gas Well ID | Numeric |
| Type Well | PRODUCING, SHUT IN, ABANDONED, INJECTION, etc. |
| Operator | Operator name |
| Field | Field name |
| Records | Current, Historical, Both |

**Example — Look up a well by API number:**
```bash
# Wellbore query is form-based. Construct the POST request:
curl -s "https://webapps2.rrc.texas.gov/EWA/wellboreQueryAction.do" \
  --data-urlencode "methodToCall=submit" \
  --data-urlencode "searchArgs.apiNoArg=42-383-30000" \
  --data-urlencode "searchArgs.recordType=BOTH"
# Note: Response is HTML, not JSON. Parse with appropriate tools.
# For bulk data, download the Full Wellbore Database instead.
```

### UIC Injection/Disposal Permit Query

```bash
# Query injection permits by county (form-based):
curl -s "https://webapps2.rrc.texas.gov/EWA/uicQueryAction.do" \
  --data-urlencode "methodToCall=submit" \
  --data-urlencode "searchArgs.countyCodeArg=383" \
  --data-urlencode "searchArgs.typeWellArg=DW"
# typeWellArg: DW=Disposal, EOR=Enhanced Oil Recovery, GS=Gas Storage
# For bulk research, download the UIC Database from MFT server.
```

---

## Workflow

### Step 1 — Resolve Intent

Map the user's question to the appropriate data channel:

| User wants... | Best channel |
|--------------|-------------|
| Specific well details | Wellbore Query or bulk Wellbore DB |
| Production for a lease/operator | PDQ or bulk Production CSV dump |
| Injection/disposal well data | UIC Query or bulk UIC DB |
| Drilling permit status | Drilling Permit Query or bulk permits file |
| Spatial analysis / mapping | GIS Viewer or bulk Shapefile downloads |
| Large-scale data analysis | Always use bulk downloads |

### Step 2 — Fetch Data

For individual lookups, use the web query applications with form POST requests.
For research-scale analysis, direct the user to download bulk files.

### Step 3 — Parse Response

Web query responses are HTML pages, not JSON. For bulk files:
- CSV files can be parsed directly
- EBCDIC files require conversion (common in mainframe-era RRC data)
- ASCII files are pipe-delimited or fixed-width (check file documentation)

### Step 4 — Produce Output

**Format: Raw Data Table + Narrative**

```
## Permian Basin Oil Production — District 8A (Monthly, 2023-2024)

| Period   | Lease Count | Oil (BBL)    | Gas (MCF)     |
|----------|-------------|--------------|---------------|
| 2024-06  | 45,231      | 58,420,000   | 195,600,000   |
| 2024-05  | 45,105      | 57,890,000   | 193,200,000   |
| ...      | ...         | ...          | ...           |

**Summary:** District 8A (Permian Basin — Midland/Delaware) produced 58.4 million
barrels of oil in June 2024, up 0.9% month-over-month. The district accounts for
approximately 40% of total Texas oil production. Data is preliminary for the most
recent 2-3 months due to late operator filings.
```

---

## RRC District Reference

| District | Region | Key Formations |
|----------|--------|---------------|
| 01 | Southwest TX | Eagle Ford (oil window) |
| 02 | South TX | Eagle Ford (gas/condensate) |
| 03 | Gulf Coast | Frio, Vicksburg |
| 04 | Deep South TX | Wilcox |
| 05 | East Central TX | Woodbine, Austin Chalk |
| 06 | East TX | Smackover, Haynesville |
| 6E | East TX (extension) | Smackover, Cotton Valley |
| 07B | West Central TX | Strawn, Bend |
| 7C | West Central TX | Cisco, Canyon |
| 08 | West TX (Midland) | Permian — Spraberry, Wolfcamp |
| 8A | West TX (Pecos) | Permian — Delaware, Bone Spring |
| 09 | North TX | Barnett Shale |
| 10 | Panhandle | Panhandle, Morrow, Granite Wash |

### Districts Critical for Li/Mg Research

- **District 06/6E (East Texas):** Smackover Formation brines — Li up to 477 mg/L in
  the AR/TX/LA Smackover trend. East Texas salt dome region has some of the highest
  lithium concentrations in U.S. produced waters.
- **District 08/8A (Permian Basin):** Massive produced water volumes (10+ million
  barrels/day statewide, ~60% from Permian). Even at lower Li concentrations
  (5-50 mg/L), the sheer volume makes this significant for Li recovery economics.

---

## Error Handling

| Condition | Meaning | Action |
|-----------|---------|--------|
| HTML error page returned | Invalid form parameters | Check parameter names and values; verify district/county codes |
| Session terminated | Automated access detected | Switch to bulk data downloads; reduce request frequency |
| Empty result set | No matching records | Broaden search criteria; check spelling of operator/field names |
| 500 Server Error | RRC server issue | Retry after delay; check RRC system status page |
| EBCDIC file encoding | Legacy mainframe format | Convert with `dd conv=ascii` or use an EBCDIC-to-ASCII tool |
| Stale data | Monthly update cycle | Check dataset update schedule; most recent 2-3 months are preliminary |

---

## Caveats and Data Limitations

1. **No REST API:** The RRC does not offer a modern REST/JSON API. All web queries
   return HTML. Bulk downloads are the preferred programmatic access method.
2. **Automated access restrictions:** The RRC actively monitors for scraping and will
   terminate sessions. Use bulk files for research-scale work.
3. **EBCDIC encoding:** Many legacy datasets use EBCDIC format from the RRC's
   mainframe systems. These require conversion before analysis.
4. **Data lag:** Production data lags 2-3 months. Operators have filing deadlines,
   and late filings are common. Preliminary data is revised.
5. **District numbering:** Districts 6E, 7B, 7C, and 8A are sub-districts with
   different geographic coverage than the parent numbers suggest.
6. **Produced water volumes:** The RRC tracks injection/disposal volumes via H-10
   reports, but these reflect disposal volumes, not total produced water (some water
   is recycled or discharged under permit).
7. **Historical data gaps:** Digital records vary by dataset. Production goes back to
   1993 in the PDQ system; older data requires the historical ledger files.
