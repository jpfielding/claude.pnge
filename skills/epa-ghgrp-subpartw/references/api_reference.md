# EPA GHGRP Subpart W — API Reference

Reference for the EPA Envirofacts REST API, GHGRP table inventory, Subpart W
data methodology, and equipment-level emission source detail.

---

## Envirofacts REST API Patterns

**Base URL:** `https://enviro.epa.gov/enviro/efservice/`

### URL Structure

```
BASE/{TABLE}/{COLUMN}/{VALUE}/{FORMAT}
BASE/{TABLE}/{COLUMN}/{VALUE}/rows/{START}:{END}/{FORMAT}
BASE/{TABLE}/{COLUMN1}/{VALUE1}/{COLUMN2}/{VALUE2}/{FORMAT}
```

Rules:
- Table names and column names are **UPPERCASE**
- `FORMAT` must be `JSON`, `XML`, or `CSV`
- Default returns all matching rows (no implicit limit — can be slow)
- Always specify `rows/0:N` for large tables
- Multiple column/value pairs are AND-joined
- No partial/wildcard matching support — exact values only
- Operators like `>`, `<`, `CONTAINS` are not supported in basic REST syntax
  (use the JSON-based query builder at https://enviro.epa.gov/ for complex filters)

### Row Pagination

```bash
# First 100 rows
curl -s ".../TABLE/COLUMN/VALUE/rows/0:99/JSON"

# Rows 100-199
curl -s ".../TABLE/COLUMN/VALUE/rows/100:199/JSON"

# Maximum practical batch: 9,999 rows (some tables may error above ~5,000)
curl -s ".../TABLE/COLUMN/VALUE/rows/0:4999/JSON"
```

---

## GHGRP Tables Inventory

All GHGRP tables in Envirofacts follow the prefix `PUB_FACTS_` or `V_PUB_FACTS_`.

### Core Tables Used by This Skill

| Table Name | Description | Key Filters |
|------------|-------------|-------------|
| `PUB_FACTS_SUBPRT_GHG_W` | Subpart W facility emissions by gas and source | STATE_CODE, REPORTING_YEAR, FACILITY_ID, GAS_NAME |
| `PUB_FACTS_FACILITY_GHG_EMITTER` | All GHGRP reporting facilities by subpart | STATE_CODE, FACILITY_ID, SUBPART_NAME |
| `PUB_FACTS_FACILITY` | Facility metadata (address, coords, NAICS) | FACILITY_ID, STATE_CODE |

### Additional GHGRP Tables

| Table Name | Description |
|------------|-------------|
| `PUB_FACTS_SUBPRT_GHG_C` | Subpart C — General Stationary Combustion |
| `PUB_FACTS_SUBPRT_GHG_D` | Subpart D — Electricity Generation |
| `PUB_FACTS_SUBPRT_GHG_I` | Subpart I — Electronics Manufacturing |
| `PUB_FACTS_SUBPRT_GHG_N` | Subpart N — Glass Production |
| `PUB_FACTS_SUBPRT_GHG_P` | Subpart P — Hydrogen Production |
| `PUB_FACTS_SUBPRT_GHG_Q` | Subpart Q — Iron and Steel |
| `PUB_FACTS_SUBPRT_GHG_U` | Subpart U — Misc. Uses of Carbonate |
| `PUB_FACTS_SUBPRT_GHG_X` | Subpart X — Petrochemical Production |
| `PUB_FACTS_SUBPRT_GHG_Y` | Subpart Y — Petroleum Refining |
| `PUB_FACTS_SUBPRT_GHG_Z` | Subpart Z — Phosphoric Acid Production |
| `PUB_FACTS_SUBPRT_GHG_HH` | Subpart HH — Municipal Solid Waste Landfills |
| `PUB_FACTS_SUBPRT_GHG_OO` | Subpart OO — Suppliers of Industrial Greenhouse Gases |
| `PUB_FACTS_SUBPRT_GHG_PP` | Subpart PP — Suppliers of CO2 |
| `PUB_FACTS_SUBPRT_GHG_QQ` | Subpart QQ — Importers and Exporters of Fluorinated GHGs |
| `PUB_FACTS_SUBPRT_GHG_W2` | Subpart W supplemental equipment-level data |

### Column Inventory: PUB_FACTS_SUBPRT_GHG_W

```bash
# Inspect column names by fetching one row
curl -s "https://enviro.epa.gov/enviro/efservice/PUB_FACTS_SUBPRT_GHG_W/STATE_CODE/WV/rows/0:0/JSON" \
  | jq '.[0] | keys'
```

Expected columns (may vary by API version):
```
FACILITY_ID          FACILITY_NAME        STATE_CODE
COUNTY_FIPS          REPORTING_YEAR       GHG_QUANTITY
GHG_QUANTITY_CO2E    GAS_NAME             GAS_CODE
SUBPART_NAME         SUBPART_CODE         EMISSION_SOURCE
EMISSION_SOURCE_CODE LATITUDE_MEAS        LONGITUDE_MEAS
CITY                 ZIP                  PRIMARY_NAICS_CODE
```

---

## Complete curl Examples

```bash
# 1. All WV Subpart W CH4 reporters, 2022 — sort by emissions
curl -s "https://enviro.epa.gov/enviro/efservice/PUB_FACTS_SUBPRT_GHG_W/STATE_CODE/WV/REPORTING_YEAR/2022/GAS_NAME/Methane/rows/0:499/JSON" \
  | jq 'sort_by(.GHG_QUANTITY | tonumber) | reverse | .[0:15] | .[] | {
      name: .FACILITY_NAME,
      ghg_tco2e: (.GHG_QUANTITY | tonumber),
      source: .EMISSION_SOURCE,
      county: .COUNTY_FIPS
    }'

# 2. Total CH4 for WV 2022 (sum all facilities and sources)
curl -s "https://enviro.epa.gov/enviro/efservice/PUB_FACTS_SUBPRT_GHG_W/STATE_CODE/WV/REPORTING_YEAR/2022/GAS_NAME/Methane/rows/0:999/JSON" \
  | jq '[.[].GHG_QUANTITY | tonumber] | add'

# 3. Facility-level breakdown for one operator
FACILITY_ID="1000244"
curl -s "https://enviro.epa.gov/enviro/efservice/PUB_FACTS_SUBPRT_GHG_W/FACILITY_ID/${FACILITY_ID}/REPORTING_YEAR/2022/JSON" \
  | jq 'group_by(.EMISSION_SOURCE) | map({
      source: .[0].EMISSION_SOURCE,
      gas: .[0].GAS_NAME,
      total_tco2e: (map(.GHG_QUANTITY | tonumber) | add)
    }) | sort_by(.total_tco2e) | reverse'

# 4. Multi-year trend for a state (loop 2015–2022)
for YEAR in 2015 2016 2017 2018 2019 2020 2021 2022; do
  TOTAL=$(curl -s "https://enviro.epa.gov/enviro/efservice/PUB_FACTS_SUBPRT_GHG_W/STATE_CODE/WV/REPORTING_YEAR/${YEAR}/GAS_NAME/Methane/rows/0:999/JSON" \
    | jq '[.[].GHG_QUANTITY | tonumber] | add')
  echo "$YEAR: $TOTAL tCO2e CH4"
done

# 5. Find facilities by NAICS code (natural gas extraction = 211130)
curl -s "https://enviro.epa.gov/enviro/efservice/PUB_FACTS_FACILITY/PRIMARY_NAICS_CODE/211130/STATE_CODE/WV/rows/0:99/JSON" \
  | jq '.[] | {id: .FACILITY_ID, name: .FACILITY_NAME, county: .COUNTY_NAME}'
```

---

## Subpart W Methodology Notes (40 CFR Part 98 Subpart W)

EPA GHGRP Subpart W emissions are calculated using one of several methods:

| Method | Applicability | Approach |
|--------|--------------|----------|
| Equipment-level emission factors | Pneumatic controllers, pumps | Throughput × emission factor from lookup table |
| Engineering calculations | Venting events, blowdowns | Gas volume × composition analysis |
| Continuous emissions monitoring (CEMS) | Large sources (compressors) | Direct measurement |
| Population emission factors | Distributed equipment (valves, flanges) | Count × average leak rate |

**Key regulatory thresholds:**
- Facilities must report if total facility GHG ≥ 25,000 tCO2e/yr
- Offshore facilities on OCS are included under Subpart W if they meet threshold
- 2024 final rule revisions (effective reporting year 2025) require direct measurement for more source categories

---

## Equipment-Level Emission Sources (Subpart W)

The `EMISSION_SOURCE` values in the database map to specific equipment types:

### Production Segment Sources
| EMISSION_SOURCE value | Equipment | Notes |
|----------------------|-----------|-------|
| Production | All production equipment aggregate | May be further split |
| Onshore Production - Combustion | Flares, engines | CO2 primary |
| Onshore Production - Venting | Pneumatics, tanks, completions | CH4 primary |
| Onshore Production - Fugitives | Valve/connector leaks | CH4 primary |
| Liquids Unloading | Well venting for deliquification | CH4 primary |
| Completions and Workovers | Venting at new/reworked wells | CH4 primary |
| Storage Tanks | Atmospheric venting from production tanks | CH4 + VOC |

### Gathering and Boosting Sources
| EMISSION_SOURCE value | Equipment | Notes |
|----------------------|-----------|-------|
| Gathering and Boosting | Aggregate gathering segment | |
| Gathering Compressors | Rod pump, centrifugal compressors | CH4 from seals |
| Gathering Pipelines | Fugitives from gathering lines | |
| Separators | Flash gas from separator venting | |

### Processing Sources
| EMISSION_SOURCE value | Equipment | Notes |
|----------------------|-----------|-------|
| Processing | Aggregate processing segment | |
| Processing Compressors | Centrifugal, reciprocating | |
| Acid Gas Removal | CO2 vented from amine units | CO2 primary |
| Dehydrators | Glycol dehydration venting | CH4 primary |
| Flaring | Combustion of waste gas | CO2, CH4 (incomplete combustion) |

---

## NAICS Codes for Oil and Gas (Subpart W Relevant)

| NAICS Code | Description |
|------------|-------------|
| 211120 | Crude petroleum extraction |
| 211130 | Natural gas extraction |
| 211140 | Natural gas liquid (NGL) extraction |
| 213111 | Drilling oil and gas wells |
| 213112 | Support activities for oil and gas operations |
| 486110 | Pipeline transportation of crude oil |
| 486210 | Pipeline transportation of natural gas |
| 493190 | Other warehousing and storage (gas storage) |
| 221210 | Natural gas distribution |

---

## Go Example: GHGRP Subpart W Query

```go
package main

import (
    "encoding/json"
    "fmt"
    "io"
    "net/http"
    "os"
    "sort"
    "strconv"
)

type SubpartWRecord struct {
    FacilityID     string `json:"FACILITY_ID"`
    FacilityName   string `json:"FACILITY_NAME"`
    StateCode      string `json:"STATE_CODE"`
    CountyFIPS     string `json:"COUNTY_FIPS"`
    ReportingYear  string `json:"REPORTING_YEAR"`
    GHGQuantity    string `json:"GHG_QUANTITY"`
    GasName        string `json:"GAS_NAME"`
    EmissionSource string `json:"EMISSION_SOURCE"`
    Latitude       string `json:"LATITUDE_MEAS"`
    Longitude      string `json:"LONGITUDE_MEAS"`
}

type FacilityAggregate struct {
    FacilityID   string
    FacilityName string
    TotalCO2e    float64
    CH4_tonnes   float64
}

const ch4GWP = 25.0 // AR4 100-year GWP for methane

func querySubpartW(state, year string, maxRows int) ([]SubpartWRecord, error) {
    url := fmt.Sprintf(
        "https://enviro.epa.gov/enviro/efservice/PUB_FACTS_SUBPRT_GHG_W/STATE_CODE/%s/REPORTING_YEAR/%s/GAS_NAME/Methane/rows/0:%d/JSON",
        state, year, maxRows-1,
    )
    resp, err := http.Get(url)
    if err != nil {
        return nil, fmt.Errorf("HTTP GET: %w", err)
    }
    defer resp.Body.Close()

    body, err := io.ReadAll(resp.Body)
    if err != nil {
        return nil, fmt.Errorf("reading body: %w", err)
    }

    var records []SubpartWRecord
    if err := json.Unmarshal(body, &records); err != nil {
        return nil, fmt.Errorf("JSON parse: %w", err)
    }
    return records, nil
}

func aggregateByFacility(records []SubpartWRecord) []FacilityAggregate {
    totals := map[string]*FacilityAggregate{}

    for _, r := range records {
        qty, err := strconv.ParseFloat(r.GHGQuantity, 64)
        if err != nil {
            continue
        }
        if agg, exists := totals[r.FacilityID]; exists {
            agg.TotalCO2e += qty
        } else {
            totals[r.FacilityID] = &FacilityAggregate{
                FacilityID:   r.FacilityID,
                FacilityName: r.FacilityName,
                TotalCO2e:    qty,
            }
        }
    }

    result := make([]FacilityAggregate, 0, len(totals))
    for _, agg := range totals {
        agg.CH4_tonnes = agg.TotalCO2e / ch4GWP
        result = append(result, *agg)
    }

    // Sort descending by total CO2e
    sort.Slice(result, func(i, j int) bool {
        return result[i].TotalCO2e > result[j].TotalCO2e
    })
    return result
}

func main() {
    state := "WV"
    year := "2022"
    if len(os.Args) >= 3 {
        state = os.Args[1]
        year = os.Args[2]
    }

    fmt.Printf("Fetching Subpart W CH4 for %s, %s...\n\n", state, year)
    records, err := querySubpartW(state, year, 1000)
    if err != nil {
        fmt.Fprintf(os.Stderr, "error: %v\n", err)
        os.Exit(1)
    }

    agg := aggregateByFacility(records)

    var stateTotal float64
    fmt.Printf("%-45s %15s %12s\n", "Facility", "CH4 (tCO2e)", "CH4 (tonnes)")
    fmt.Println("---")
    for i, a := range agg {
        if i >= 15 {
            break
        }
        fmt.Printf("%-45s %15.0f %12.0f\n", a.FacilityName, a.TotalCO2e, a.CH4_tonnes)
        stateTotal += a.TotalCO2e
    }
    fmt.Printf("\nState total (CH4, tCO2e): %.0f\n", stateTotal)
    fmt.Printf("State total (CH4 mass):   %.0f tonnes\n", stateTotal/ch4GWP)
    fmt.Printf("\nData source: EPA Envirofacts GHGRP Subpart W\n")
    fmt.Printf("Note: GHGRP threshold 25,000 tCO2e/yr; small operators exempt\n")
}
```

---

## Useful External Links

| Resource | URL |
|----------|-----|
| EPA FLIGHT Tool (download CSVs) | https://ghgdata.epa.gov/ghgp/main.do |
| GHGRP Data Sets (annual Excel) | https://www.epa.gov/ghgreporting/ghg-reporting-program-data-sets |
| Subpart W regulation text | https://www.ecfr.gov/current/title-40/chapter-I/subchapter-C/part-98/subpart-W |
| 2024 EPA Methane Rule | https://www.epa.gov/stationary-sources-air-pollution/2024-standards-performance-new-revised-and-existing-sources |
| Envirofacts Table Browser | https://enviro.epa.gov/enviro/ef_metadata_html.ef_metadata_table.simple_query |
| EDF Methane Tracker | https://www.edf.org/climate/methane-studies |
| EPA GHG Inventory (national totals) | https://www.epa.gov/ghgemissions/inventory-us-greenhouse-gas-emissions-and-sinks |
