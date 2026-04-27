---
name: nm-ocd
description: >
  Query New Mexico Oil Conservation Division (OCD) well, production, injection,
  and disposal data. Use this skill when the user asks about New Mexico oil and
  gas wells, Permian Basin New Mexico, Delaware Basin production, Lea County
  wells, Eddy County production, New Mexico injection wells, NM produced water
  volumes, NM disposal wells, OCD well search, New Mexico drilling permits, NM
  oil and gas statistics, or any New Mexico upstream regulatory data. Covers the
  New Mexico portion of the Permian Basin (Delaware Basin), San Juan Basin, and
  all NM producing areas. Critical for produced water volume research in the
  Delaware Basin. Produces data tables with narrative summaries.
---

# New Mexico Oil Conservation Division (OCD) Data Skill

Queries New Mexico oil and gas regulatory data from the OCD under the Energy,
Minerals and Natural Resources Department (EMNRD). New Mexico is the #2 oil
producing state and a major produced water generator, particularly in the
Delaware Basin portion of the Permian.

## API Key Handling

**No API key required.** All OCD public data queries, statistics downloads, and
the Geospatial Hub are freely accessible without authentication.

---

## Data Access Architecture

The OCD provides data through four channels:

1. **OCD Permitting Web App** — well search, operator lookup, permit queries
2. **OCD Statistics Portal** — downloadable reports and production summaries
3. **OCD Geospatial Hub** — ArcGIS-based spatial data and feature services
4. **OCD FTP Server** — bulk document and data file downloads

### Channel 1: OCD Permitting Web Application

**Base URL:** `https://wwwapps.emnrd.nm.gov/OCD/OCDPermitting/`

| Query Tool | URL | Data |
|-----------|-----|------|
| Well Search | `https://wwwapps.emnrd.nm.gov/OCD/OCDPermitting/Data/Wells.aspx` | Well records by API, operator, location |
| Well Details | `https://wwwapps.emnrd.nm.gov/OCD/OCDPermitting/Data/WellDetails.aspx?api=API_NUMBER` | Individual well detail page |
| Operator Search | `https://wwwapps.emnrd.nm.gov/OCD/OCDPermitting/Data/Operators.aspx` | Operator records and associated wells |
| Facility Search | `https://wwwapps.emnrd.nm.gov/OCD/OCDPermitting/Data/Facilities.aspx` | Facility records |
| Incident Search | `https://wwwapps.emnrd.nm.gov/OCD/OCDPermitting/Data/Incidents.aspx` | Spills, incidents |
| Pit Search | `https://wwwapps.emnrd.nm.gov/OCD/OCDPermitting/Data/Pits.aspx` | Pits and containments |

**Well Detail Fields** (available per well via WellDetails.aspx):
- API Number, Well Name, Operator, Well Type, Status
- Location (Township, Range, Section, Quarter)
- County, Pool/Formation, Depth
- Production history, injection volumes
- Permit information, completion data

### Channel 2: OCD Statistics Portal

**URL:** `https://www.emnrd.nm.gov/ocd/ocd-data/statistics/`

Downloadable reports and datasets:

| Dataset | Format | Coverage |
|---------|--------|----------|
| County Production and Injection by Month | Varies | Current |
| Statewide Natural Gas and Oil Production Summary | Varies | Monthly (includes produced water and injection) |
| C-115 Produced Water by District by Year | Varies | 2014-current |
| C-115 Produced Water by Operator by Year | Varies | 2014-current |
| C-115 Flaring and Venting by District | Varies | Current |
| C-115 Flaring and Venting by Operator | Varies | Current |
| Annual Operator Production Report | Varies | Annual |
| C-115 Operator Details (Monthly) | Varies | Monthly |
| APDs Issued by Type/Year | Varies | Annual |
| Plugged and Abandoned Wells | Varies | Annual |
| Well Inspections by District/Type | Varies | Monthly |
| Stripper/Marginal Wells (Oil and Gas) | Varies | Current |
| Oil and Gas Sales by Volume | Varies | 2003-current |

### Channel 3: OCD Geospatial Hub

**URL:** `https://ocd-hub-nm-emnrd.hub.arcgis.com/`

ArcGIS Hub with spatial data layers. Typical ArcGIS REST query patterns apply:

```bash
# Discover available feature layers on the Hub
# Browse: https://ocd-hub-nm-emnrd.hub.arcgis.com/
# Look for Feature Server endpoints for wells, facilities, permits

# Standard ArcGIS REST query pattern (once you identify a service URL):
curl -s "SERVICE_URL/query" \
  --data-urlencode "where=COUNTY='LEA'" \
  --data-urlencode "outFields=*" \
  --data-urlencode "resultRecordCount=10" \
  --data-urlencode "f=json"
```

### Channel 4: OCD FTP Server

**Access:** Anonymous FTP connection (Port 21)
- Hostname shown on the OCD FTP page (image-based, not machine-readable)
- URL: `https://www.emnrd.nm.gov/ocd/ocd-data/ftp-server/`
- Contains publicly available OCD documents and data files
- Requires an FTP client (FileZilla, WinSCP, or command-line `ftp`)

---

## Query Patterns

### Well Lookup by API Number

```bash
# Look up a specific well by API number (web application, returns HTML):
curl -s "https://wwwapps.emnrd.nm.gov/OCD/OCDPermitting/Data/WellDetails.aspx?api=3001520100"
# Response is HTML. Parse for well details, production history, and injection data.

# For programmatic access, the Geospatial Hub feature services return JSON.
# Browse the Hub to find the current well layer service URL.
```

### County Production Summary

```bash
# Download county-level production and injection data from the Statistics portal:
# Visit: https://www.emnrd.nm.gov/ocd/ocd-data/statistics/
# Download: "County Production and Injection by month"
# This provides monthly oil, gas, and water volumes by county.
```

### Produced Water Data (C-115 Reports)

```bash
# The C-115 produced water reports are key for Li/Mg research.
# Available from: https://www.emnrd.nm.gov/ocd/ocd-data/statistics/
# Downloads:
#   - C-115 Produced Water by District by Year (2014-current)
#   - C-115 Produced Water by Operator by Year (2014-current)
# These contain operator-reported produced water volumes per well/lease.
```

### Saltwater Disposal Well Map

```bash
# The OCD Statistics page includes an "SWD Applications Map"
# showing saltwater disposal well locations and permit status.
# Access from: https://www.emnrd.nm.gov/ocd/ocd-data/statistics/
```

---

## Workflow

### Step 1 — Resolve Intent

| User wants... | Best channel |
|--------------|-------------|
| Specific well details | OCD Permitting Web App (WellDetails.aspx) |
| Production by county/operator | Statistics Portal downloads |
| Produced water volumes | C-115 reports from Statistics Portal |
| Spatial analysis / mapping | Geospatial Hub (ArcGIS) |
| Bulk data files | FTP Server |
| Operator information | OCD Permitting (Operators.aspx) |
| Injection/disposal wells | Statistics Portal + Well Search filtered by type |

### Step 2 — Fetch Data

For individual well lookups, query the Permitting web app by API number.
For county/operator-level analysis, download summary reports from Statistics.
For spatial queries, use the Geospatial Hub ArcGIS services.

### Step 3 — Parse Response

- Web app responses are HTML (parse with appropriate tools)
- Statistics downloads are typically Excel/CSV
- ArcGIS Hub returns JSON when queried with `f=json`
- FTP files vary by dataset

### Step 4 — Produce Output

**Format: Raw Data Table + Narrative**

```
## New Mexico Delaware Basin Produced Water — Lea and Eddy Counties (Monthly)

| Period   | County | Oil (BBL)    | Gas (MCF)     | Water (BBL)   |
|----------|--------|--------------|---------------|---------------|
| 2024-06  | Lea    | 22,100,000   | 85,300,000    | 45,600,000    |
| 2024-06  | Eddy   | 18,400,000   | 72,100,000    | 38,900,000    |
| ...      | ...    | ...          | ...           | ...           |

**Summary:** Lea and Eddy counties dominate NM oil production, together
accounting for 95%+ of state output. Combined produced water exceeds 84 million
barrels/month (2.8 million BBL/day), making the NM Delaware Basin one of the
highest produced-water-volume areas in the U.S. Data from OCD C-115 reports;
volumes are preliminary for recent months.
```

---

## New Mexico Geographic Reference

### Key Counties for Oil and Gas

| County | Basin | Notes |
|--------|-------|-------|
| Lea | Permian (Delaware/Central Basin Platform) | #1 NM oil county |
| Eddy | Permian (Delaware Basin) | #2 NM oil county, Carlsbad area |
| Chaves | Permian (eastern edge) | Moderate production |
| San Juan | San Juan Basin | Major gas production, coalbed methane |
| Rio Arriba | San Juan Basin (southern) | Gas production |

### OCD Districts

The OCD divides NM into regulatory districts. District boundaries and numbers
are available on the Statistics page and Geospatial Hub.

### Formations Critical for Li/Mg Research

- **Delaware Basin (Lea/Eddy Counties):** Wolfcamp, Bone Spring, and deeper
  formations produce massive water volumes. Li concentrations generally 5-30 mg/L,
  but the volume (millions of BBL/day) makes this area significant for DLE
  economics at scale.
- **Abo Reef (Chaves/Eddy):** Older produced waters with higher TDS; some elevated
  Li/Mg relative to shallower Permian zones.

---

## Error Handling

| Condition | Meaning | Action |
|-----------|---------|--------|
| HTML error / CAPTCHA | Bot detection on Permitting app | Reduce request frequency; switch to Statistics downloads or Geospatial Hub |
| Empty result set | No matching records | Verify API number format (10-digit NM format); check operator spelling |
| 500 Server Error | OCD server issue | Retry after delay |
| FTP connection refused | Server maintenance | Try again later; check OCD announcements |
| Missing C-115 data pre-2014 | Data not digitized for earlier years | Use USGS Produced Waters DB for historical water chemistry |
| Geospatial Hub layer unavailable | Service being updated | Check Hub page for current available layers |

---

## Caveats and Data Limitations

1. **No REST API:** The OCD Permitting system is a web application returning HTML,
   not a REST API. The Geospatial Hub ArcGIS services do support JSON queries but
   layer URLs change as the Hub is updated.
2. **C-115 produced water data starts 2014:** Operator-reported water volumes via
   C-115 forms are only available from 2014 onward. Pre-2014 water data is sparse.
3. **Produced water vs. injection volumes:** C-115 reports track produced water at
   the wellhead. Disposal/injection volumes are tracked separately and may differ
   due to recycling, evaporation, or surface discharge.
4. **Data lag:** Monthly production data typically lags 2-3 months. Operators have
   45 days to file C-115 reports after the production month.
5. **Water chemistry not included:** OCD tracks water volumes but not water chemistry
   (Li, Mg, TDS, etc.). For geochemical data, cross-reference with the USGS
   Produced Waters Geochemical Database.
6. **FTP server access:** The FTP hostname is displayed as an image on the OCD
   website (not selectable text), likely to reduce automated access.
7. **Permian Basin dominance:** 95%+ of NM production comes from the Permian Basin
   (Lea and Eddy counties). San Juan Basin gas production is significant but
   declining. Other counties have minimal activity.
