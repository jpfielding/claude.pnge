---
name: epa-enviro
description: >
  Query EPA Envirofacts and ECHO for environmental facility data, discharge
  permits, toxic release inventories, drinking water systems, compliance and
  enforcement history. Use this skill whenever the user asks about EPA regulated
  facilities, NPDES discharge permits, TRI chemical releases, Safe Drinking
  Water Act systems, RCRA hazardous waste handlers, UIC injection wells,
  environmental compliance, enforcement actions, or facility-level environmental
  data — even if they do not explicitly mention EPA, Envirofacts, or ECHO.
  Trigger for phrases like "EPA facilities in West Virginia",
  "toxic release inventory near Morgantown", "NPDES permits in Monongalia
  County", "drinking water violations", "injection well compliance",
  "who is polluting near this well pad", "environmental compliance for
  oil and gas operators", "TRI data for lithium compounds", or any request
  for U.S. environmental regulatory facility data. Produces facility tables
  and narrative summaries with compliance context.
---

# EPA Envirofacts & ECHO Skill

Fetches and analyzes U.S. environmental regulatory data from two complementary
EPA systems:

- **Envirofacts** (`data.epa.gov/efservice/`) — Direct table-level access to
  TRI, FRS, and legacy PCS/NPDES data
- **ECHO** (`echodata.epa.gov/echo/`) — Compliance, enforcement, and violation
  data across CWA, RCRA, SDW, and CAA programs

## API Key Handling

**No API key is required.** Both Envirofacts and ECHO are publicly accessible
without authentication.

> **Note:** The CLAUDE.md build plan references an api.data.gov key for EPA
> Envirofacts. Testing confirmed this is not needed. The Envirofacts REST API
> and ECHO endpoints all return data without any API key or authentication
> header. If EPA adds key requirements in the future, use the standard
> credential resolution pattern below.

**Contingency credential resolution (if EPA adds key requirements):**

Resolution order (stop at first success):

1. **`~/.config/epa/credentials`** — parse `api_key=<value>` from this file
2. **`EPA_API_KEY` env var** — fallback if credentials file is absent
3. **Prompt the user** — "EPA may now require an API key. Get one free at
   https://api.data.gov/signup/ — store in `~/.config/epa/credentials` as
   `api_key=YOUR_KEY` (chmod 600)."

Never hardcode or log any key. If needed, pass as query parameter `?api_key=<KEY>`.

**Reading the credentials file (bash):**
```bash
KEY=$(grep '^api_key=' ~/.config/epa/credentials 2>/dev/null | cut -d= -f2)
[ -z "$KEY" ] && KEY="${EPA_API_KEY}"
```

---

## API Structure

### Envirofacts REST API

**Base URL:** `https://data.epa.gov/efservice/`

> The legacy `enviro.epa.gov/enviro/efservice/` domain now 301-redirects here.
> Always use `data.epa.gov`.

**URL pattern:**
```
GET https://data.epa.gov/efservice/{TABLE}/{COL1}/{VAL1}/{COL2}/{VAL2}/.../rows/{START}:{END}/{FORMAT}
```

| Component | Description | Example |
|-----------|-------------|---------|
| `TABLE` | Table name (uppercase) | `TRI_FACILITY` |
| `COL/VAL` | Zero or more filter pairs | `STATE_ABBR/WV` |
| `rows/S:E` | Row range (0-based, inclusive) | `rows/0:99` |
| `FORMAT` | Response format | `JSON`, `XML`, `CSV` |

**Comparison operators** (placed after column name):
| Operator | Keyword | Example |
|----------|---------|---------|
| Equals | *(default)* | `STATE_ABBR/WV` |
| Not equal | `!=` | `FAC_CLOSED_IND/!=/1` |
| Greater than | `>` | `FAC_LATITUDE/>/390000` |
| Less than | `<` | `FAC_LATITUDE/</400000` |
| Starts with | `BEGINNING` | `FACILITY_NAME/BEGINNING/PATRIOT` |
| Contains | `CONTAINING` | `FACILITY_NAME/CONTAINING/COAL` |

### ECHO REST API

**Base URL:** `https://echodata.epa.gov/echo/`

ECHO uses a **two-step query pattern**:

1. **Search** — POST search parameters, receive a `QueryID` and row count
2. **Retrieve** — Use `QueryID` to page through actual records

**Service families:**

| Program | Search Endpoint | Retrieve Endpoint |
|---------|-----------------|-------------------|
| CWA (Clean Water Act) | `cwa_rest_services.get_facilities` | `cwa_rest_services.get_qid` |
| RCRA (Haz. Waste) | `rcra_rest_services.get_facilities` | `rcra_rest_services.get_qid` |
| SDW (Drinking Water) | `sdw_rest_services.get_systems` | `sdw_rest_services.get_qid` |
| CAA (Clean Air Act) | `air_rest_services.get_facilities` | `air_rest_services.get_qid` |

**Common ECHO search parameters:**

| Parameter | Description | Example |
|-----------|-------------|---------|
| `output` | Response format (always `JSON`) | `JSON` |
| `p_st` | State code | `WV` |
| `p_co` | County name | `MONONGALIA` |
| `p_zip` | ZIP code | `26505` |
| `p_sic` | SIC industry code | `1311` |
| `p_act` | Active status | `Y` |
| `p_maj` | Major facility flag | `Y` |
| `p_qiv` | Quarters in violation | `GT1` |

---

## Key Tables and Endpoints

See `references/table_reference.md` for complete column listings.

### Envirofacts Tables (verified available)

| Table | Filter Column | Description |
|-------|--------------|-------------|
| `TRI_FACILITY` | `STATE_ABBR` | TRI facility locations and contacts |
| `TRI_REPORTING_FORM` | `STATE_ABBR` | Per-chemical annual TRI reports |
| `TRI_RELEASE_QTY` | *(via doc_ctrl_num)* | Release quantities by medium |
| `FRS_FACILITY_SITE` | `STATE_CODE` | Master facility registry |
| `FRS_PROGRAM_FACILITY` | `STATE_CODE` | Cross-references to all EPA programs |
| `PCS_PERMIT_FACILITY` | `LOCATION_STATE` | Legacy NPDES permits |
| `PCS_INSPECTION` | `LOCATION_STATE` | Legacy NPDES inspections |

### Envirofacts Tables (unavailable — use ECHO instead)

| Table | Status | ECHO Alternative |
|-------|--------|------------------|
| `UIC_WELL` | 404 | ECHO CWA or state UIC databases |
| `UIC_VIOLATION` | 404 | ECHO enforcement data |
| `SDWIS_WATER_SYSTEM` | 404 | ECHO SDW (`sdw_rest_services`) |
| `RCRA_FACILITY` | 404 | ECHO RCRA (`rcra_rest_services`) |
| `CERCLIS_SITE` | 404 | ECHO or EPA SEMS database |

### ECHO Endpoints

| Endpoint | What it Returns |
|----------|-----------------|
| `cwa_rest_services` | NPDES permit holders, discharge data, CWA violations |
| `rcra_rest_services` | Hazardous waste generators/handlers, RCRA violations |
| `sdw_rest_services` | Public water systems, SDWA violations, source water info |
| `air_rest_services` | CAA facilities, air permit data, CAA violations |

---

## Workflow

### Step 1 — Resolve Intent

Map the user's question to the right data source:

| User Wants | Use |
|-----------|-----|
| Facility by name, SIC, or location | `TRI_FACILITY` or ECHO search |
| Chemical release data | `TRI_REPORTING_FORM` + `TRI_RELEASE_QTY` |
| Cross-reference across EPA programs | `FRS_PROGRAM_FACILITY` |
| NPDES discharge permit info | ECHO CWA (`cwa_rest_services`) |
| Drinking water system data | ECHO SDW (`sdw_rest_services`) |
| Hazardous waste facility data | ECHO RCRA (`rcra_rest_services`) |
| Compliance/enforcement history | ECHO (any program, check violation flags) |
| Environmental justice context | ECHO (includes EJ demographics in results) |

### Step 2 — Fetch Data (Envirofacts)

Build the URL with appropriate filters:

```bash
# TRI facilities in Monongalia County, WV
curl -sL "https://data.epa.gov/efservice/TRI_FACILITY/STATE_ABBR/WV/COUNTY_NAME/MONONGALIA/rows/0:50/JSON"

# All EPA program links for a specific facility (by registry ID)
curl -sL "https://data.epa.gov/efservice/FRS_PROGRAM_FACILITY/REGISTRY_ID/110000344896/rows/0:20/JSON"

# TRI reports for WV in 2022
curl -sL "https://data.epa.gov/efservice/TRI_REPORTING_FORM/STATE_ABBR/WV/REPORTING_YEAR/2022/rows/0:50/JSON"
```

Default behavior:
- Request up to 100 rows per query (`rows/0:99`)
- If result set is large, paginate by incrementing the row range
- Parse JSON response — returns a flat array of row objects

### Step 3 — Fetch Data (ECHO)

Use the two-step pattern:

```bash
# Step 1: Search
RESULT=$(curl -sL "https://echodata.epa.gov/echo/cwa_rest_services.get_facilities?output=JSON&p_st=WV&p_co=MONONGALIA")
QID=$(echo "$RESULT" | jq -r '.Results.QueryID')
TOTAL=$(echo "$RESULT" | jq -r '.Results.QueryRows')
echo "QueryID: $QID, Total: $TOTAL"

# Step 2: Retrieve records
curl -sL "https://echodata.epa.gov/echo/cwa_rest_services.get_qid?output=JSON&qid=$QID&pageno=1&pagesize=20"
```

For ECHO, always:
- Check `.Results.Message` for "Success" or "Working" (both indicate valid results)
- Check `.Results.Error.ErrorMessage` if present
- Use `pageno` and `pagesize` to page through large result sets
- Note summary statistics in step 1 (SVRows, CVRows = significant/current violators)

### Step 4 — Parse Response

**Envirofacts response:** JSON array of row objects at root level.
```json
[
  {"tri_facility_id": "26504PTRTM1090C", "facility_name": "PATRIOT MINING CO INC OSAGE MINE", ...},
  {"tri_facility_id": "26504PTRTM12MIA", "facility_name": "PATRIOT MINING CO INC DENTS RUN MINE", ...}
]
```

**ECHO response:** Nested JSON with Results wrapper.
```json
{
  "Results": {
    "Message": "Working",
    "QueryRows": "2153",
    "QueryID": "357",
    "PageNo": "1",
    "Facilities": [
      {"CWPName": "FACILITY NAME", "SourceID": "WV0045233", ...}
    ]
  }
}
```

### Step 5 — Produce Output

**Format: Facility Table + Narrative Summary**

Present a markdown table of the most relevant records (cap at ~20 rows), then
a narrative summary covering:

1. **Result count** — how many facilities/systems matched
2. **Key findings** — notable compliance issues, major dischargers, violators
3. **Geographic context** — county, region, proximity to areas of interest
4. **Compliance summary** — violation counts, enforcement actions, SNC status
5. **Cross-reference note** — other EPA programs the facility appears in
6. **Caveats** — data currency, self-reported vs measured, legacy PCS vs ICIS

**Example output structure:**
```
## TRI Facilities — Monongalia County, WV

| Facility Name | TRI ID | City | Status | Parent Company |
|---------------|--------|------|--------|----------------|
| PATRIOT MINING CO INC OSAGE MINE | 26504PTRTM1090C | Star City | Active | ANKER GROUP INC |
| PATRIOT MINING CO INC DENTS RUN MINE | 26504PTRTM12MIA | Star City | Active | ANKER GROUP INC |
| ... | ... | ... | ... | ... |

**Summary:** 4 TRI-reporting facilities were found in Monongalia County, WV
(EPA Region 03). Two are coal mining operations (PATRIOT MINING) that report
zinc compounds and other releases. All facilities are currently active.
Cross-reference via FRS to check CWA discharge permits and RCRA status.

**Caveats:** TRI data is industry self-reported annually. Release quantities
may be estimated (code E), measured (M), or calculated (C). Reporting
thresholds apply — small-quantity releases may not appear.
```

---

## Pagination

### Envirofacts

If results might exceed your row range, paginate by incrementing the range:

```python
all_rows = []
start = 0
page_size = 100
while True:
    rows = fetch_envirofacts(table, filters, start, start + page_size - 1)
    all_rows.extend(rows)
    if len(rows) < page_size:
        break  # last page
    start += page_size
```

Warn the user if the result set is very large (over 1000 rows) and suggest
adding filters (county, year, SIC code) to narrow results.

### ECHO

Use `pageno` and `pagesize` parameters on the `get_qid` endpoint:

```python
page = 1
while page * pagesize <= total:
    records = echo_retrieve(program, qid, page=page, pagesize=20)
    # process records
    page += 1
```

---

## Error Handling

| Condition | Meaning | Action |
|-----------|---------|--------|
| HTTP 404 + "table is not available" | Envirofacts table removed/retired | Use ECHO alternative (see table above) |
| HTTP 404 (no JSON body) | Bad URL path | Check table name, column name spelling |
| HTTP 500 from ECHO | Invalid parameter combination | Check parameter names/values against docs |
| ECHO `Error.ErrorMessage` | Query rejected | Read message, fix parameters, retry |
| Empty array `[]` from Envirofacts | No matching rows | Broaden filters or check column/value |
| ECHO `QueryRows: "0"` | No matching facilities | Broaden search area or parameters |
| Large result set (>5000 rows) | Performance concern | Add geographic or temporal filters |

---

## Cross-Reference Strategy

EPA maintains facility IDs across multiple regulatory programs. The **FRS
Registry ID** is the master cross-reference key:

```
FRS Registry ID (e.g., 110000344896)
  |-- TRI:   tri_facility_id  (via epa_registry_id in TRI_FACILITY)
  |-- NPDES: permit ID         (via FRS_PROGRAM_FACILITY, pgm_sys_acrnm=ICIS)
  |-- RCRA:  handler ID        (via FRS_PROGRAM_FACILITY, pgm_sys_acrnm=RCRAINFO)
  |-- SDWA:  PWS ID            (via FRS_PROGRAM_FACILITY, pgm_sys_acrnm=SDWIS)
  |-- ECHO:  DfrUrl            (uses registry_id as fid parameter)
```

**Workflow to link a facility across programs:**
1. Find the facility in any table and get its FRS Registry ID
2. Query `FRS_PROGRAM_FACILITY` with that registry ID
3. Use the returned program IDs to query specific tables or ECHO endpoints

---

## PNGE-Relevant Query Patterns

### Find Oil & Gas Facilities by SIC Code

```bash
# SIC 1311 = Crude Petroleum and Natural Gas
# SIC 1381 = Drilling Oil and Gas Wells
curl -sL "https://echodata.epa.gov/echo/cwa_rest_services.get_facilities?output=JSON&p_st=WV&p_sic=1311"
```

### TRI Releases for Specific Chemicals

```bash
# Search TRI reporting forms for a specific chemical (by CAS name)
curl -sL "https://data.epa.gov/efservice/TRI_REPORTING_FORM/STATE_ABBR/WV/CAS_CHEM_NAME/CONTAINING/BARIUM/rows/0:20/JSON"
```

### Drinking Water Systems Near a Site

```bash
# Community water systems in a county
curl -sL "https://echodata.epa.gov/echo/sdw_rest_services.get_systems?output=JSON&p_st=WV&p_co=MONONGALIA&p_pswsid_code_type=community"
```

### Environmental Justice Context

ECHO search results include demographic data fields:
- `PercentPeopleOfColor` — percent people of color in surrounding area
- `FacPopDen` — population density around facility
- `AcsPopulationDensity` — ACS population density

These can be used to flag potential environmental justice concerns near
produced water disposal sites or processing facilities.

---

## EPA Region Reference

West Virginia is in **EPA Region 03** (with DC, DE, MD, PA, VA).

Key Appalachian-basin states by region:
- **Region 03:** WV, PA, VA
- **Region 04:** KY
- **Region 05:** OH

---

## SIC Codes for PNGE Research

| SIC | Description |
|-----|-------------|
| 1311 | Crude Petroleum and Natural Gas |
| 1321 | Natural Gas Liquids |
| 1381 | Drilling Oil and Gas Wells |
| 1382 | Oil and Gas Field Services, NEC |
| 1389 | Services Allied to Oil and Gas Extraction |
| 2819 | Industrial Inorganic Chemicals, NEC (Li compounds) |
| 4923 | Natural Gas Transmission and Distribution |

---

## Implementation Notes

- **Prefer `bash` with `curl` + `jq`** for API calls in Claude's environment
- **Python stdlib client** — see `references/python_example.py` for Envirofacts
  and ECHO client classes using only `urllib` and `json`
- **Envirofacts returns flat JSON arrays** — no wrapper object, no pagination
  metadata; rely on returned row count vs requested range to detect more pages
- **ECHO returns nested JSON** — always navigate to `.Results` and check for
  `.Error` before processing data
- **TRI latitude/longitude** — `fac_latitude` and `fac_longitude` are in DDMMSS
  integer format (e.g., 393800 = 39d 38m 00s). Use `pref_latitude`/`pref_longitude`
  (decimal degrees) when available
- **PCS is legacy** — the Permit Compliance System has been replaced by
  ICIS-NPDES for current data. Use ECHO CWA endpoints for current permit and
  compliance information
- **Data currency** — TRI data lags ~18 months (2024 data available mid-2025);
  ECHO compliance data is updated quarterly
- **Self-reported data** — TRI releases are industry self-reported with
  estimation methods; verify with ECHO inspection/enforcement data where possible
