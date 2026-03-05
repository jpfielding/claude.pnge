---
name: epa-ghg
description: >
  Query and analyze EPA Greenhouse Gas Reporting Program (GHGRP) facility
  emissions data from the Envirofacts API. Use this skill when the user asks
  about greenhouse gas emissions from oil and gas facilities, Subpart W
  petroleum and natural gas systems, refinery emissions, CO2 injection for
  EOR or carbon storage, methane leakage, flaring, venting, or any facility-
  level GHG data reported to EPA. Trigger phrases: "GHG emissions from gas
  plants", "methane emissions Appalachian basin", "Subpart W reporting",
  "oil and gas emissions in West Virginia", "CO2 injection wells GHGRP",
  "top emitters in Permian", "refinery carbon footprint", "EPA FLIGHT data",
  "greenhouse gas reporting for pipelines", "GHGRP facility lookup",
  "carbon intensity of produced water operations". Produces ranked facility
  tables with gas breakdown and narrative trend analysis.
---

# EPA Greenhouse Gas Reporting Program (GHGRP) Skill

Fetches and analyzes facility-level greenhouse gas emissions from the EPA
GHGRP via the Envirofacts REST API (`data.epa.gov/efservice/`).

## Credential

**None required.** The Envirofacts GHGRP views are fully public with no
API key or authentication.

---

## API Structure

**Base URL:** `https://data.epa.gov/efservice/`

**Query pattern:** Path-based filters chained in the URL:
```
https://data.epa.gov/efservice/{TABLE}/{COLUMN}/{VALUE}/.../{rows/M:N}/{FORMAT}
```

**Primary table:** `V_GHG_EMITTER_SUBPART` — facility emissions by subpart,
gas, and year. This is the most detailed table available via the API.

**Secondary table:** `V_GHG_EMITTER_GAS` — facility emissions by gas only
(no subpart breakdown). Useful for total facility emissions.

**Key parameters:**

| Component | Description | Example |
|-----------|-------------|---------|
| `TABLE` | View name | `V_GHG_EMITTER_SUBPART` |
| `COLUMN/VALUE` | Exact match filter | `STATE/WV`, `YEAR/2022` |
| `COLUMN/CONTAINING/VALUE` | Substring match | `FACILITY_NAME/CONTAINING/EQT` |
| `rows/M:N` | Row range (0-indexed, inclusive) | `rows/0:99` |
| `count/JSON` | Record count only | Appended instead of rows |
| Format suffix | `JSON`, `CSV`, or `XML` | Appended last |

Multiple filters chain left to right:
```
/V_GHG_EMITTER_SUBPART/SUBPART_NAME/W/STATE/WV/YEAR/2022/rows/0:99/JSON
```

See `references/api_reference.md` for full column reference, all subpart
codes, gas codes, and additional query patterns.

---

## Key Subparts for PNGE

| Subpart | Category | Use Case |
|---------|----------|----------|
| **W** | Petroleum and Natural Gas Systems | Onshore/offshore production, processing, transmission, storage, LNG, distribution. **Primary for O&G.** |
| **C** | Stationary Combustion | Boilers, turbines, engines at any large facility. |
| **Y** | Petroleum Refining | Process emissions from catalytic cracking, coking, etc. |
| **UU** | Injection of CO2 | EOR and carbon storage injection quantities. |
| **PP** | Suppliers of CO2 | CO2 capture and supply facilities. |
| **MM** | Suppliers of Petroleum Products | Upstream supply-side accounting for refiners/importers. |
| **RR** | Geologic Sequestration of CO2 | Facilities with EPA-approved CO2 sequestration monitoring. |

---

## Workflow

### Step 1 — Resolve Intent

Map the user's question to query parameters:

| User asks about | Subpart | Gas filter | Notes |
|-----------------|---------|------------|-------|
| O&G facility emissions | W | (all) | Default for most PNGE queries |
| Methane leaks, venting | W | CH4 | Methane is the key Subpart W concern |
| Refinery emissions | Y | (all) | Texas, Louisiana dominate |
| CO2 injection / EOR | UU | (all) | Supplier-type, reports injection volumes |
| Carbon storage | RR | (all) | Sequestration monitoring |
| Total facility emissions | (all or omit) | (all) | Use V_GHG_EMITTER_GAS for aggregate |
| Specific operator | use CONTAINING filter | (all) | e.g., FACILITY_NAME/CONTAINING/EQT |

**State mapping:** Use 2-letter postal codes (WV, TX, PA, OH, ND, NM, etc.)

**Year range:** Data available 2010-present. Most recent complete year is
typically current year minus 2 (data for 2023 published ~October 2024).

### Step 2 — Get Record Count (when total is uncertain)

Before fetching potentially large result sets, check the count:
```bash
curl -s "https://data.epa.gov/efservice/V_GHG_EMITTER_SUBPART/SUBPART_NAME/W/YEAR/2022/count/JSON"
```
Returns: `[{"TOTALQUERYRESULTS": 5782}]`

If count exceeds 1000, warn the user and paginate or narrow filters.

### Step 3 — Fetch Data

Build the URL with appropriate filters. Default behavior:
- Use `V_GHG_EMITTER_SUBPART` as the primary table
- Filter by `SUBPART_NAME/W` for O&G queries unless user specifies otherwise
- Include `YEAR/{latest}` — default to most recent available year
- Add `STATE/{code}` when user specifies geography
- Limit with `rows/0:99` for initial fetch; expand if needed
- Use `JSON` output format

**Example — Subpart W facilities in West Virginia for 2022:**
```bash
curl -s "https://data.epa.gov/efservice/V_GHG_EMITTER_SUBPART/SUBPART_NAME/W/STATE/WV/YEAR/2022/JSON" \
  | python3 -m json.tool
```

**Example — Search by operator name:**
```bash
curl -s "https://data.epa.gov/efservice/V_GHG_EMITTER_SUBPART/FACILITY_NAME/CONTAINING/EQT/SUBPART_NAME/W/YEAR/2022/JSON"
```

**Example — Methane-only emissions in a state:**
```bash
curl -s "https://data.epa.gov/efservice/V_GHG_EMITTER_SUBPART/SUBPART_NAME/W/STATE/PA/YEAR/2022/GAS_CODE/CH4/rows/0:99/JSON"
```

**Example — Top emitters nationally (first page):**
```bash
curl -s "https://data.epa.gov/efservice/V_GHG_EMITTER_SUBPART/SUBPART_NAME/W/YEAR/2022/rows/0:99/JSON"
```

### Step 4 — Parse Response

Response is a flat JSON array. Each element is one row:
```json
[
  {
    "facility_id": 1003461,
    "facility_name": "Dominion Energy Transmission - Cornwell Station",
    "state": "WV",
    "county": "KANAWHA COUNTY",
    "latitude": 38.48558,
    "longitude": -81.27167,
    "year": 2022,
    "subpart_name": "W",
    "subpart_category": "Petroleum and Natural Gas Systems",
    "co2e_emission": 4.6,
    "ghg_quantity": 4.6,
    "gas_code": "CO2",
    "gas_name": "Carbon Dioxide"
  }
]
```

**Key fields:**
- `co2e_emission` — CO2-equivalent metric tons (GWP-weighted). Use this for
  comparisons and totals.
- `ghg_quantity` — Raw mass in metric tons of the specific gas. Use this when
  analyzing gas composition (e.g., "how many tons of methane leaked").
- Each facility appears as multiple rows (one per gas type per subpart).
  Aggregate by `facility_id` or `facility_name` for total facility emissions.

**Aggregation logic (in bash with jq):**
```bash
# Total CO2e by facility
curl -s "URL" | jq '[group_by(.facility_name)[] |
  {facility: .[0].facility_name, state: .[0].state,
   total_co2e: ([.[].co2e_emission] | add)}] |
  sort_by(-.total_co2e) | .[:10]'
```

### Step 5 — Produce Output

**Format: Ranked Facility Table + Gas Breakdown + Narrative**

Present a markdown table of the top facilities ranked by CO2e, then a gas
breakdown, then narrative analysis.

**Example output structure:**
```
## Subpart W Emissions — West Virginia (2022)

### Top Facilities by Total CO2e

| Rank | Facility | County | Total CO2e (MT) |
|------|----------|--------|-----------------|
| 1 | DTM Appalachia Gathering, LLC | Doddridge | 183,921.6 |
| 2 | HG Energy II Appalachia, LLC | Ritchie | 172,815.1 |
| 3 | Mountaineer Gas Company | Kanawha | 127,178.6 |
| ... | ... | ... | ... |

### Gas Breakdown (all WV Subpart W facilities combined)

| Gas | CO2e (MT) | % of Total |
|-----|-----------|------------|
| Carbon Dioxide | 601,604.8 | 53.7% |
| Methane | 518,635.5 | 46.3% |
| Nitrous Oxide | 593.0 | <0.1% |

**Summary:** West Virginia Subpart W (Petroleum and Natural Gas Systems)
facilities reported 1,120,833 MT CO2e in 2022 across 43 reporting facilities.
Methane accounts for 46% of CO2e despite being a small fraction by mass —
this reflects methane's 25x global warming potential. The top 3 facilities
(DTM Appalachia, HG Energy II, Mountaineer Gas) account for 43% of the
state's total Subpart W emissions. Gathering and processing operations
dominate, consistent with WV's role as a major Marcellus/Utica gas
production state.

**Units:** Metric tons CO2-equivalent (MT CO2e). Reporting threshold:
25,000 MT CO2e/year (facility-wide, not per-subpart).
**Data vintage:** 2022 final. Most recent available as of early 2025.
```

---

## Pagination

Use `rows/M:N` for pagination (0-indexed, inclusive on both ends).

```bash
# Get count first
COUNT=$(curl -s "https://data.epa.gov/efservice/V_GHG_EMITTER_SUBPART/SUBPART_NAME/W/YEAR/2022/count/JSON" \
  | python3 -c "import json,sys; print(json.load(sys.stdin)[0]['TOTALQUERYRESULTS'])")

# Page through results
PAGE=0
PAGE_SIZE=500
while [ $PAGE -lt $COUNT ]; do
  END=$((PAGE + PAGE_SIZE - 1))
  curl -s "https://data.epa.gov/efservice/V_GHG_EMITTER_SUBPART/SUBPART_NAME/W/YEAR/2022/rows/${PAGE}:${END}/JSON"
  PAGE=$((PAGE + PAGE_SIZE))
done
```

Warn the user if dataset exceeds 5,000 rows and suggest narrowing by state,
year, gas, or subpart.

---

## Error Handling

| Condition | Response Pattern | Action |
|-----------|-----------------|--------|
| Table not available | `{"error": "TABLE/...: The table is not available."}` | Use `V_GHG_EMITTER_SUBPART` instead. `V_GHG_EMITTER_FACILITIES` and `V_GHG_EMITTER_SECTOR` are not served by this endpoint. |
| Empty result `[]` | Valid JSON, no records | Verify filter values. Check that year has data (latest may not be published yet). Try removing one filter to broaden. |
| Timeout / slow response | No response within 30s | Narrow filters (add STATE, reduce row range). National full-year queries can be very large. |
| Invalid column name | Server error or empty result | Check column names in `references/api_reference.md`. Column names in URL are case-insensitive. |
| Row range too large | Slow response or incomplete data | Keep page size at 500-1000 rows. Use count first to plan pagination. |

---

## Multi-Year Trend Analysis

The API does not support year ranges in a single request. To build a
time series, issue one request per year and merge results:

```bash
for YEAR in 2018 2019 2020 2021 2022; do
  curl -s "https://data.epa.gov/efservice/V_GHG_EMITTER_SUBPART/SUBPART_NAME/W/STATE/WV/YEAR/${YEAR}/JSON"
done | python3 -c "
import json, sys
# Merge JSON arrays from multiple requests
all_data = []
for line in sys.stdin:
    line = line.strip()
    if line:
        all_data.extend(json.loads(line))
# Aggregate by year
by_year = {}
for r in all_data:
    y = r['year']
    by_year[y] = by_year.get(y, 0) + r['co2e_emission']
for y in sorted(by_year):
    print(f'{y}: {by_year[y]:,.0f} MT CO2e')
"
```

---

## PNGE Research Context

### Carbon Intensity of Produced Water Operations

Subpart W covers emissions from produced water handling — separators,
tanks, pneumatic devices, and flares at well sites. When analyzing carbon
intensity of produced water treatment for lithium/magnesium recovery:

1. Query Subpart W for the target basin/state to establish baseline O&G
   emissions per facility
2. Compare against proposed DLE (Direct Lithium Extraction) energy inputs
3. Consider that co-producing Li/Mg from existing brine handling may add
   minimal incremental emissions vs. standalone mining operations

### Methane as the Key Concern

For petroleum and natural gas systems (Subpart W), methane typically
accounts for 40-60% of CO2e despite being a small fraction by mass.
This is because EPA uses a GWP of 25 for CH4 (AR4 basis, 100-year).

Key methane emission sources in Subpart W:
- Pneumatic controllers and pumps
- Equipment leaks (fugitive emissions)
- Associated gas venting and flaring
- Liquids unloading
- Gathering and boosting compressor stations
- Produced water tanks (flash emissions)

### Cross-Referencing with Other Skills

- **usgs-produced-waters:** Match GHGRP facility locations with produced
  water chemistry to correlate brine Li/Mg content with emissions profiles.
- **wvges-wells:** Link GHGRP facilities to specific well permits via
  operator name and county.
- **fracfocus:** Cross-reference GHGRP reporting facilities with hydraulic
  fracturing chemical disclosures.
- **eia-data:** Compare GHGRP-reported emissions against EIA production
  volumes to calculate emissions intensity (MT CO2e per barrel or per Mcf).

---

## Caveats and Data Limitations

1. **Reporting threshold:** Only facilities emitting 25,000+ MT CO2e/year
   (facility-wide) are required to report. Thousands of smaller O&G
   facilities fall below this threshold and are not in the dataset.
2. **Self-reported:** Data is submitted by facility operators. EPA conducts
   verification but errors and underreporting occur.
3. **Subpart W segment detail:** The Envirofacts API returns subpart-level
   totals. Segment-level breakdowns (e.g., onshore production vs.
   transmission compression within Subpart W) are only available via
   EPA FLIGHT bulk downloads (https://ghgdata.epa.gov/ghgp/).
4. **GWP values:** CO2e calculations use IPCC AR4 GWP values (CH4 = 25).
   Some current policy uses AR5 (CH4 = 28) or AR6 (CH4 = 29.8). Results
   are not directly comparable across GWP bases.
5. **Publication lag:** Data for reporting year N is typically published
   October of year N+1. The most recent complete year is usually
   current year minus 2.
6. **Double counting risk:** Facilities may report under multiple subparts
   (e.g., Subpart C combustion + Subpart W process). Summing across
   subparts can overcount if not careful about emission source boundaries.
7. **Supplier vs. emitter:** Subparts UU, PP, MM are supplier-type
   (subpart_type = "S"). These report quantities entering commerce, not
   direct atmospheric emissions. Do not add supplier and emitter subpart
   totals together for facility emissions.

---

## Implementation Notes

- **Use `bash_tool` with `curl` + `jq`** for API queries and JSON parsing
- **Python client** — see `references/python_example.py` (stdlib only, no
  dependencies). Includes `GHGClient`, `GHGQuery`, pagination, and
  aggregation helpers.
- Default to most recent available year unless user specifies
- Always aggregate by `facility_id` or `facility_name` before ranking —
  raw rows contain one record per gas per subpart per year
- Cap output tables at 20 rows for readability; note total count
- Always include units (MT CO2e) and data year in output
- Note when a query returns facility-wide vs. subpart-specific results
