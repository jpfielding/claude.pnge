---
name: epa-ghgrp-subpartw
description: >
  Query EPA Greenhouse Gas Reporting Program (GHGRP) Subpart W data for
  petroleum and natural gas system methane emissions at U.S. oil and gas
  facilities. Use this skill when the user asks about oilfield methane
  emissions, Subpart W reporting, natural gas system GHG emissions,
  facility-level methane data, emissions by equipment type, basin-level
  methane intensity, venting and flaring emissions, or EPA GHGRP petroleum
  and natural gas data. Trigger for phrases like "methane emissions from
  Marcellus operators", "Subpart W emissions WV", "oilfield GHG intensity",
  "equipment-level methane leaks", "EPA reported methane from gas wells",
  "natural gas methane intensity", "GHGRP Subpart W data", "venting and
  flaring emissions", "emissions per well", or "oilfield emissions by basin".
  Covers facilities reporting under 40 CFR Part 98 Subpart W since 2011.
  Produces facility emissions tables with equipment-type breakdowns.
---

# EPA GHGRP Subpart W Skill

Queries the EPA Envirofacts API for Greenhouse Gas Reporting Program (GHGRP)
Subpart W data covering methane and CO2 emissions from petroleum and natural
gas systems. Covers facilities since 2011 reporting year. No API key required.

---

## No Credential Required

The EPA Envirofacts API is fully public. No API key is needed for this skill.

---

## API Structure

**Base URL:** `https://enviro.epa.gov/enviro/efservice/`

The Envirofacts REST API follows a consistent pattern:
```
GET /enviro/efservice/{TABLE_NAME}/{COLUMN}/{OPERATOR}/{VALUE}/{FORMAT}
GET /enviro/efservice/{TABLE_NAME}/{COLUMN}/{OPERATOR}/{VALUE}/rows/{START}:{END}/{FORMAT}
```

- `FORMAT`: `JSON`, `XML`, or `CSV`
- Row ranges: `rows/0:99` returns rows 0 through 99 (100 rows). Max ~10,000 per request.
- When `OPERATOR` is omitted, `=` is assumed: `COLUMN/VALUE` matches exact equality.

---

### Primary Tables for GHGRP Subpart W

#### PUB_FACTS_SUBPRT_GHG_W — Subpart W Facility Emissions

The main table for petroleum and natural gas system GHG emissions by facility
and reporting year.

```bash
# All Subpart W facilities in West Virginia
curl -s "https://enviro.epa.gov/enviro/efservice/PUB_FACTS_SUBPRT_GHG_W/STATE_CODE/WV/JSON"

# WV facilities for a specific reporting year
curl -s "https://enviro.epa.gov/enviro/efservice/PUB_FACTS_SUBPRT_GHG_W/STATE_CODE/WV/REPORTING_YEAR/2022/JSON"

# Paginate: first 200 rows
curl -s "https://enviro.epa.gov/enviro/efservice/PUB_FACTS_SUBPRT_GHG_W/STATE_CODE/WV/rows/0:199/JSON"

# All Subpart W reporters for a single year (national)
curl -s "https://enviro.epa.gov/enviro/efservice/PUB_FACTS_SUBPRT_GHG_W/REPORTING_YEAR/2022/rows/0:999/JSON"
```

Key fields in `PUB_FACTS_SUBPRT_GHG_W`:
| Field | Description | Example |
|-------|-------------|---------|
| `FACILITY_ID` | EPA GHGRP facility ID | 1000244 |
| `FACILITY_NAME` | Facility name | ANTERO RESOURCES WV |
| `STATE_CODE` | 2-letter state | WV |
| `COUNTY_FIPS` | 5-digit FIPS | 54061 |
| `REPORTING_YEAR` | Calendar year | 2022 |
| `SUBPART_NAME` | Subpart identifier | Subpart W |
| `GHG_QUANTITY` | Total GHG in mtCO2e | 125432.5 |
| `GAS_NAME` | Greenhouse gas name | Methane, CO2, Nitrous Oxide |
| `EMISSION_SOURCE` | Source category | Gathering and Boosting |
| `LATITUDE_MEAS` | Facility latitude | 38.9271 |
| `LONGITUDE_MEAS` | Facility longitude | -80.1234 |

---

#### PUB_FACTS_FACILITY_GHG_EMITTER — All GHGRP Facilities

Broader table covering all GHGRP subparts, useful for finding a facility's
ID before querying Subpart W detail.

```bash
# Find facility IDs for WV oil/gas operators
curl -s "https://enviro.epa.gov/enviro/efservice/PUB_FACTS_FACILITY_GHG_EMITTER/STATE_CODE/WV/rows/0:199/JSON" \
  | jq '.[] | {facility_id: .FACILITY_ID, name: .FACILITY_NAME, subpart: .SUBPART_NAME}'

# Find a specific facility by ID
curl -s "https://enviro.epa.gov/enviro/efservice/PUB_FACTS_FACILITY_GHG_EMITTER/FACILITY_ID/1000244/JSON"
```

---

#### PUB_FACTS_FACILITY — Facility Metadata

Facility-level information including address, coordinates, and NAICS code.

```bash
# Get facility metadata by GHGRP ID
curl -s "https://enviro.epa.gov/enviro/efservice/PUB_FACTS_FACILITY/FACILITY_ID/1000244/JSON"
```

Key fields:
| Field | Description |
|-------|-------------|
| `FACILITY_ID` | GHGRP facility ID |
| `FACILITY_NAME` | Facility name |
| `ADDRESS1`, `CITY`, `STATE` | Mailing address |
| `ZIP` | ZIP code |
| `LATITUDE_MEAS`, `LONGITUDE_MEAS` | Coordinates |
| `NAICS_CODE` | Industry code (211120 = crude oil production, 211130 = natural gas extraction) |
| `PARENT_COMPANY` | Parent company name |

---

### FLIGHT Tool (Manual Download)

For bulk analysis, the EPA FLIGHT (Facility Level Information on GreenHouse
Gases Tool) provides downloadable CSVs:
- URL: `https://ghgdata.epa.gov/ghgp/main.do`
- Select: State, Subpart W, year range, Download CSV
- Fields: Facility, state, county, emissions by gas, by emission source category

This is the preferred route for multi-year trend analysis or national comparisons.
The Envirofacts API is better for programmatic single-facility lookups.

Also: EPA GHGRP annual summary Excel files at:
`https://www.epa.gov/ghgreporting/ghg-reporting-program-data-sets`

---

## Workflow

### Step 1 — Resolve Intent

Map the user's question:
- "Methane emissions in [state]" → `PUB_FACTS_SUBPRT_GHG_W/STATE_CODE/{STATE}/REPORTING_YEAR/{YEAR}/JSON`
- "Top methane emitters in [basin]" → query state, parse GHG_QUANTITY, sort descending
- "Emissions from [operator]" → search by FACILITY_ID in `PUB_FACTS_FACILITY_GHG_EMITTER`
- "Emissions by equipment type" → filter on EMISSION_SOURCE field
- "Trend over time" → loop years 2011–2023, aggregate GHG_QUANTITY by year

### Step 2 — Fetch Facility List

```bash
STATE="WV"
YEAR="2022"
curl -s "https://enviro.epa.gov/enviro/efservice/PUB_FACTS_SUBPRT_GHG_W/STATE_CODE/${STATE}/REPORTING_YEAR/${YEAR}/rows/0:499/JSON" \
  | jq 'sort_by(.GHG_QUANTITY | tonumber) | reverse | .[0:20] | .[] | {
      name: .FACILITY_NAME,
      id: .FACILITY_ID,
      ghg_mtco2e: .GHG_QUANTITY,
      gas: .GAS_NAME,
      source: .EMISSION_SOURCE,
      county: .COUNTY_FIPS
    }'
```

### Step 3 — Aggregate CH4 by Facility

A single facility-year appears in multiple rows (one per gas per emission
source). Aggregate CH4 specifically:

```bash
curl -s "https://enviro.epa.gov/enviro/efservice/PUB_FACTS_SUBPRT_GHG_W/STATE_CODE/WV/REPORTING_YEAR/2022/GAS_NAME/Methane/rows/0:499/JSON" \
  | jq '
    group_by(.FACILITY_ID) |
    map({
      facility: .[0].FACILITY_NAME,
      total_ch4_mtco2e: (map(.GHG_QUANTITY | tonumber) | add)
    }) |
    sort_by(.total_ch4_mtco2e) | reverse | .[0:15]
  '
```

### Step 4 — Equipment Type Breakdown

The `EMISSION_SOURCE` field contains segment-level categories. Filter for
one facility to see breakdown:

```bash
curl -s "https://enviro.epa.gov/enviro/efservice/PUB_FACTS_SUBPRT_GHG_W/FACILITY_ID/1000244/REPORTING_YEAR/2022/JSON" \
  | jq 'group_by(.EMISSION_SOURCE) | map({
      source: .[0].EMISSION_SOURCE,
      gas: .[0].GAS_NAME,
      total_mtco2e: (map(.GHG_QUANTITY | tonumber) | add)
    }) | sort_by(.total_mtco2e) | reverse'
```

### Step 5 — Produce Output

Format a ranked facility table and equipment breakdown. Add CH4 mass
conversion and basin-level context.

---

## Output Format

### Facility Emissions Table

```
## EPA GHGRP Subpart W — Methane Emissions, WV (2022)

Top Reporting Facilities (CH4, tCO2e at AR4 GWP=25):

| Rank | Facility | County | CH4 (tCO2e) | CH4 (tonnes) | Primary Source | ID |
|------|----------|--------|-------------|--------------|----------------|----|
| 1 | ANTERO WV OPERATIONS | Doddridge | 485,230 | 19,409 | Gathering/Boosting | 1000244 |
| 2 | EQT PRODUCTION | Wetzel | 312,450 | 12,498 | Production | 1001876 |
| ... | ... | ... | ... | ... | ... | ... |

**Total WV Subpart W CH4 (2022):** X,XXX,XXX tCO2e (~X,XXX t CH4)

**Equipment Source Breakdown (WV, 2022, all gases):**

| Emission Source | CH4 (tCO2e) | % of State Total |
|----------------|-------------|-----------------|
| Gathering and Boosting | XXX,XXX | XX% |
| Production | XXX,XXX | XX% |
| Processing | XXX,XXX | XX% |
| Transmission Pipelines | XXX,XXX | XX% |

**Summary:** [narrative on basin-level emissions trends, top contributors,
year-over-year changes, comparison to national Subpart W totals, and any
notable equipment-type drivers]

**Data Caveats:** GHGRP captures facilities above 25,000 tCO2e/yr only.
Subpart W uses engineering calculations per 40 CFR Part 98 Subpart W, not
direct measurement. Actual emissions may differ. Latest available year is
typically the prior calendar year (data released ~9–18 months after year end).
```

---

## Subpart W Emission Source Categories

Subpart W covers six industry segments under 40 CFR Part 98 Subpart W:

| Segment | Abbreviation | Key Equipment Sources |
|---------|--------------|----------------------|
| Production | W-P | Pneumatic controllers, wellhead equipment, completions, workovers, storage tanks |
| Gathering and Boosting | W-GB | Compressors, separators, dehydrators, pneumatics, pipeline leaks |
| Processing | W-PR | Compressors, dehydrators, acid gas removal, flaring |
| Transmission Pipelines | W-T | Compressors, metering stations, pipeline blowdowns |
| Distribution | W-D | City gate stations, distribution mains, service connections |
| Underground Storage | W-S | Compressors, well venting, flaring |
| LNG Storage | W-LNG | Liquefaction equipment, vaporizers |

**Largest Subpart W source nationally:** Pneumatic devices (~35–40% of
Subpart W reported CH4), followed by gathering compressors and storage tanks.

---

## CH4 Global Warming Potential Reference

Envirofacts reports emissions in metric tonnes CO2-equivalent (mtCO2e).
To convert to physical methane mass:

```
CH4 mass (t) = CH4 (tCO2e) / GWP
```

| GWP basis | CH4 GWP value | Context |
|-----------|---------------|---------|
| AR4 (100-yr) | 25 | EPA GHGRP regulatory basis |
| AR5 (100-yr) | 28 | IPCC Fifth Assessment |
| AR6 (100-yr) | 27.9 | IPCC Sixth Assessment |
| AR4 (20-yr) | 72 | Short-term climate impact |
| AR6 (20-yr) | 81.2 | Short-term climate impact |

**Example:** 100,000 tCO2e CH4 at AR4 = 100,000 / 25 = 4,000 metric tonnes CH4

---

## Error Handling

| Condition | Meaning | Action |
|-----------|---------|--------|
| Empty JSON array `[]` | No matching records | Try broader filter (remove year or state constraint); verify table name spelling |
| HTTP 500 | Server error or malformed URL | Check table name case (must be UPPERCASE); verify column name exists |
| Rows appear duplicated | One row per gas per emission source | Aggregate by FACILITY_ID; filter `GAS_NAME/Methane` for CH4 only |
| GHG_QUANTITY is a string | Envirofacts returns all values as strings | Cast with `tonumber` in jq or `float()` in Python |
| Large result truncated | Envirofacts row limit | Use `rows/0:N` with pagination; try up to `rows/0:9999` |
| FACILITY_NAME mismatch | Exact match required for name filter | Use FACILITY_ID instead; find ID via FLIGHT tool CSV |
| Old data only | API lags 1–2 years behind current year | Note latest available year; for 2026 context, expect 2023 data |

---

## National Context and Benchmarks

| Metric | Value | Notes |
|--------|-------|-------|
| Total U.S. GHGRP Subpart W | ~175 MtCO2e/yr | ~2022 reported total |
| Subpart W as % of U.S. GHG | ~2.5–3.5% | EPA GHG Inventory |
| Production segment share | ~35–40% of Subpart W | EPA analysis |
| Gathering & Boosting share | ~30–35% of Subpart W | EPA analysis |
| GHGRP reporting threshold | 25,000 tCO2e/yr | 1,000 t CH4/yr at GWP 25 |
| Appalachian basin states (WV+PA+OH) | ~12–20 MtCO2e/yr combined | Marcellus/Utica plays |

---

## Caveats and Data Limitations

- **Reporting threshold:** Only facilities emitting ≥25,000 tCO2e/yr must
  report. Small well pads, gathering lines, and marginal producers are exempt,
  creating significant under-coverage of distributed methane sources.
- **Engineering calculations, not measurement:** Subpart W allows facilities
  to calculate emissions using emission factors and throughput data rather than
  direct measurement. Independent atmospheric studies suggest actual emissions
  are 1.5–3x higher for some equipment categories.
- **2024 EPA methane rule (40 CFR Part 98 revisions, effective 2025):** Expands
  monitoring requirements and revises emission factors. Reported values for
  2025+ may show step-change increases reflecting improved methodology rather
  than actual emission increases.
- **GWP basis:** GHGRP uses AR4 GWP (CH4 = 25) for regulatory compliance.
  State and corporate inventories may use AR5 or AR6. Be explicit about which
  GWP is used when comparing values.
- **Data lag:** GHGRP data for year Y is typically released in fall of Y+1.
  As of March 2026, the most recent complete data is 2023.
- **Offshore facilities:** Subpart W covers OCS offshore platforms but they
  report differently. Use `boem-offshore` skill for offshore production context.
