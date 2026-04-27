---
name: la-sonris
description: >
  Query Louisiana SONRIS (Strategic Online Natural Resources Information System)
  for well, production, injection, and permit data from the Louisiana Department
  of Natural Resources. Use this skill when the user asks about Louisiana oil
  and gas wells, Louisiana production, SONRIS data, Smackover Formation
  Louisiana, Haynesville Shale, Louisiana injection wells, LA produced water,
  Louisiana salt dome brines, Louisiana parish production, Louisiana disposal
  wells, South Louisiana production, LA drilling permits, Louisiana brine
  chemistry, or any Louisiana upstream regulatory data. Critical for lithium
  research — the Smackover Formation in north Louisiana (and extending into
  south Arkansas and east Texas) contains the highest-concentration lithium
  brines in the U.S., up to 477 mg/L. Produces data tables with narrative
  summaries.
---

# Louisiana SONRIS Data Skill

Queries Louisiana oil and gas regulatory data from the SONRIS system maintained
by the Louisiana Department of Natural Resources (DNR), Office of Conservation.
Louisiana is a major oil and gas state with production from the Gulf Coast, salt
dome structures, Haynesville Shale, and the critically important Smackover
Formation brine trend.

## API Key Handling

**No API key required.** SONRIS public data queries are freely accessible
without authentication.

**Note:** SONRIS is a legacy Oracle-based web application. URLs use Oracle ORDS
(Oracle REST Data Services) patterns and may redirect between hostnames. Some
pages require session cookies. The system can be slow and occasionally
unavailable.

---

## Data Access Architecture

SONRIS provides data through three channels:

1. **SONRIS Web Application** — well search, production queries, permit data
2. **SONRIS GIS** — spatial data viewer
3. **Bulk Data Downloads** — ASCII data files and report archives

### Channel 1: SONRIS Web Application

**Base URL:** `http://sonlite.dnr.state.la.us/ords/cart_prod/`

The SONRIS system uses Oracle ORDS URL patterns. Key entry points:

| Query Tool | URL | Data |
|-----------|-----|------|
| SONRIS Main Menu | `http://sonlite.dnr.state.la.us/ords/cart_prod/cart_top_html` | Hub for all query tools |
| Well Search | `http://sonlite.dnr.state.la.us/ords/cart_prod/cart_well_srch_sta` | Search wells by serial number, operator, parish, field |
| Production Query | `http://sonlite.dnr.state.la.us/ords/cart_prod/cart_prod_qry` | Production data by well, field, or operator |
| Injection/Disposal Query | `http://sonlite.dnr.state.la.us/ords/cart_prod/cart_inj_qry` | Injection well volumes |
| Permit Query | `http://sonlite.dnr.state.la.us/ords/cart_prod/cart_permit_qry` | Drilling and workover permits |
| Scout Ticket | `http://sonlite.dnr.state.la.us/ords/cart_prod/cart_scout_qry` | Well completion/scout data |

**Well search parameters:**

| Parameter | Description |
|-----------|-------------|
| Well Serial Number | Louisiana unique well identifier |
| API Number | Standard 14-digit API number |
| Operator Name | Current or historical operator |
| Parish | Louisiana parish (equivalent to county) |
| Field | Named field |
| Section/Township/Range | Legal location |
| Well Type | Oil, Gas, Injection, Disposal, etc. |

### Channel 2: SONRIS GIS

**URL:** `https://sonris-www.dnr.state.la.us/gis/agsweb/IE/JSViewer/index.html`

ESRI-based GIS viewer showing:
- Well locations (color-coded by type/status)
- Field boundaries
- Unit boundaries
- Pipeline routes
- Lease/permit boundaries

### Channel 3: Bulk Data and ASCII Downloads

SONRIS provides bulk ASCII data files for download. Access via the SONRIS
main menu:

| Dataset | Description |
|---------|-------------|
| Well Header Data | Basic well information (serial number, API, operator, location, status) |
| Production Data | Monthly production volumes by well |
| Injection Data | Monthly injection/disposal volumes by well |
| Completion Data | Formation, perforations, initial potential |
| Permit Data | Drilling and workover permits |
| Plug and Abandon Data | P&A records |

---

## Query Patterns

### Well Search

```bash
# SONRIS well queries use Oracle ORDS URL patterns.
# The web forms submit POST requests with Oracle-specific parameters.

# Look up a well by serial number:
curl -s "http://sonlite.dnr.state.la.us/ords/cart_prod/cart_well_dtl" \
  --data-urlencode "p_wsn=SERIAL_NUMBER"
# Response is HTML with well detail page.

# Search wells by parish and field:
# Navigate to the well search page and submit the form with parish/field criteria.
# The exact form parameters depend on the SONRIS page structure.
# URL: http://sonlite.dnr.state.la.us/ords/cart_prod/cart_well_srch_sta
```

### Production Query

```bash
# Query production for a specific well:
# Navigate to production query and enter well serial number.
# URL: http://sonlite.dnr.state.la.us/ords/cart_prod/cart_prod_qry

# Production data includes:
# - Monthly oil production (BBL)
# - Monthly gas production (MCF)
# - Monthly water production (BBL)
# - Condensate production (BBL)
# - Days on production
```

### Injection/Disposal Query

```bash
# Query injection volumes for disposal wells:
# URL: http://sonlite.dnr.state.la.us/ords/cart_prod/cart_inj_qry
# Enter well serial number or search by operator/parish.
# Returns monthly injection volumes, pressures, and fluid types.
```

### Manual Workflow for Research

For systematic data gathering, the recommended approach is:

1. **Identify target wells:** Use SONRIS Well Search by parish and formation
   to find wells in the Smackover or other target formations
2. **Get well serial numbers:** Record the Louisiana serial numbers from search
   results
3. **Pull production data:** Query production for each well serial number
4. **Pull injection data:** Query injection volumes for disposal wells in the
   area to estimate produced water volumes
5. **Cross-reference with USGS:** Match wells to the USGS Produced Waters
   Geochemical Database for brine chemistry (Li, Mg, TDS)

---

## Workflow

### Step 1 — Resolve Intent

| User wants... | Best channel |
|--------------|-------------|
| Specific well details | SONRIS Well Search by serial number or API |
| Production by well | SONRIS Production Query |
| Injection/disposal volumes | SONRIS Injection Query |
| Well locations on map | SONRIS GIS Viewer |
| Parish-level summaries | SONRIS Production Query by parish |
| Bulk data for analysis | ASCII data downloads from SONRIS |
| Smackover brine chemistry | Cross-reference SONRIS wells with USGS Produced Waters DB |

### Step 2 — Fetch Data

SONRIS is a session-based web application. For individual lookups:
1. Navigate to the appropriate query page
2. Submit the search form with parameters
3. Parse the HTML response

For bulk analysis, download the ASCII data files.

### Step 3 — Parse Response

- All SONRIS web responses are HTML (Oracle ORDS-generated pages)
- ASCII bulk files are typically pipe-delimited or fixed-width
- GIS viewer is interactive only (no documented REST endpoint for public use)

### Step 4 — Produce Output

**Format: Raw Data Table + Narrative**

```
## Smackover Formation Wells — Union Parish, Louisiana

| Serial No. | API Number      | Operator           | Status    | Formation  | Depth (ft) |
|------------|----------------|--------------------|-----------|------------|------------|
| 123456     | 42-111-12345   | Standard Lithium   | Active    | Smackover  | 9,500      |
| 123457     | 42-111-12346   | Equinor            | Active    | Smackover  | 9,800      |
| ...        | ...            | ...                | ...       | ...        | ...        |

**Summary:** Union Parish has 15 active Smackover wells operated by companies
involved in lithium extraction research. The Smackover Formation in this area
produces brine at depths of 9,000-10,500 ft with TDS of 200,000-350,000 mg/L
and Li concentrations of 150-400 mg/L — well above the ~100 mg/L economic
threshold for direct lithium extraction (DLE).
```

---

## Louisiana Geographic Reference

### Key Parishes for Oil and Gas

| Parish | Region | Key Formations |
|--------|--------|---------------|
| Plaquemines | Deep South LA | Gulf Coast, deepwater staging |
| Lafourche | South LA | Gulf Coast, shallow shelf |
| Terrebonne | South LA | Coastal production |
| Caddo | NW LA | Haynesville Shale |
| De Soto | NW LA | Haynesville Shale |
| Red River | NW LA | Haynesville Shale |
| Union | N LA | Smackover Formation |
| Columbia | N LA | Smackover Formation |
| Claiborne | NW LA | Smackover, Cotton Valley |
| Webster | NW LA | Smackover, Cotton Valley |
| Bienville | N-central LA | Smackover |

### Formations Critical for Li/Mg Research

- **Smackover Formation (Upper Jurassic):** The most important formation for
  U.S. lithium-from-brine research. North Louisiana Smackover wells produce
  brines with 150-477 mg/L lithium — the highest known concentrations in U.S.
  produced waters. The formation extends across south AR, north LA, and east TX.
  - Depth: 8,000-11,000 ft
  - TDS: 200,000-350,000+ mg/L
  - Li: 100-477 mg/L (commonly 150-300 mg/L)
  - Mg: 1,000-5,000+ mg/L
  - Also rich in Br, Ca, Na, and other valuable solutes
  - Active DLE projects: Standard Lithium (south AR), Equinor, ExxonMobil

- **Cotton Valley (Upper Jurassic):** Overlies the Smackover. Brines have
  lower Li (10-100 mg/L) but are produced in larger volumes.

- **Haynesville Shale (Upper Jurassic):** Major gas play in NW Louisiana.
  Produced water volumes relatively low (gas wells) but brine chemistry similar
  to Cotton Valley. Li typically 10-50 mg/L.

---

## Error Handling

| Condition | Meaning | Action |
|-----------|---------|--------|
| 401 Unauthorized | Session expired or SONRIS access issue | Clear cookies; start a new session from the main menu |
| 302 Redirect loop | SONRIS URL migration (sundown to sonlite) | Follow redirects; use sonlite.dnr.state.la.us base URL |
| Blank page / timeout | SONRIS server overloaded | Retry after several minutes; SONRIS has limited server capacity |
| "No data found" | No matching records for criteria | Verify serial number format; check parish/field spelling |
| Oracle error displayed | Backend database issue | Retry; report persistent errors to DNR |
| URL pattern changed | SONRIS migration from sundown to ORDS | Try both old (sundown) and new (ORDS) URL patterns |

---

## Caveats and Data Limitations

1. **Legacy system:** SONRIS is an aging Oracle-based system. Performance can be
   poor, and the interface is dated. URLs may change as DNR migrates from the
   old "sundown" paths to Oracle ORDS.
2. **No REST API:** SONRIS does not offer a modern REST/JSON API. All queries
   return HTML pages generated by Oracle ORDS.
3. **Session-based access:** SONRIS uses server-side sessions. Automated access
   is difficult — cookies must be maintained between requests.
4. **URL instability:** SONRIS has undergone multiple URL migrations:
   - Old: `sonris-www.dnr.state.la.us/sundown/cart_prod/...`
   - Current: `sonlite.dnr.state.la.us/ords/cart_prod/...`
   - Redirects are in place but not always reliable.
5. **Water chemistry not in SONRIS:** SONRIS tracks production and injection
   volumes but not brine geochemistry. For Li/Mg concentrations, use the USGS
   Produced Waters Geochemical Database and cross-reference by API number.
6. **Smackover data coverage:** Not all Smackover wells report to SONRIS.
   Some brine production is permitted under mineral extraction rather than
   oil and gas, which may be tracked differently.
7. **Parish vs. County:** Louisiana uses "parishes" instead of "counties."
   There are 64 parishes in Louisiana.
