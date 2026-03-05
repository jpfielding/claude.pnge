---
name: iea-open
description: >
  Query free open data from the International Energy Agency (IEA) API covering
  electric vehicles, energy prices, CO2 and greenhouse gas emissions, Net Zero
  Emissions scenario projections, CCUS policies, and SDG energy access. Use this
  skill whenever the user asks about global EV sales or stock, energy price
  comparisons across countries, carbon emissions by country or sector, Net Zero
  2050 pathways, CCUS regulations, or SDG 7 energy access metrics. Trigger for
  phrases like "EV sales in China", "gasoline price in Europe", "CO2 emissions
  by country", "net zero scenario", "IEA data", "global EV stock share",
  "electricity price comparison", "carbon intensity trend", "CCUS policy",
  "energy access", or any request for international energy statistics beyond
  U.S.-only EIA data. Produces trend summaries and raw data tables.
---

# IEA Open Data Skill

Fetches and analyzes international energy data from the IEA free API endpoints
at `api.iea.org`. No API key is required for these endpoints.

**Important limitation:** The IEA paywalls most of its detailed energy balance,
supply, and demand data behind a subscription. This skill covers only the
**free, open endpoints** that return JSON data without authentication.

## Free Endpoints (Verified Working)

| Endpoint | Description | Records |
|----------|-------------|---------|
| `/evs` | Global EV Tracker -- sales, stock, charging, projections | ~16,000 |
| `/prices` | Energy end-use prices by country, sector, product | ~41,000 |
| `/ghg` | CO2 and GHG emissions from fuel combustion by country | ~207,000 |
| `/nze` | Net Zero Emissions by 2050 scenario data | ~6,700 |
| `/ccus` | CCUS policies and regulations database | ~90 |
| `/sdg` | SDG 7 energy access indicators (large dataset) | varies |

## No API Key Required

All endpoints are open. No authentication header needed. Simply:
```bash
curl -s "https://api.iea.org/evs"
```

---

## API Structure

**Base URL:** `https://api.iea.org/`

All endpoints return JSON arrays of objects. Filter by appending query parameters
that match field names in the response objects.

**General query pattern:**
```
GET https://api.iea.org/{endpoint}?{field1}={value1}&{field2}={value2}
```

Parameters use the exact field names from the response JSON. Some endpoints use
human-readable names (e.g., `region`, `year`), others use CODE_ prefixed fields
(e.g., `CODE_COUNTRY`, `CODE_PRODUCT`).

---

## Endpoint Details

### 1. Electric Vehicles (`/evs`)

Global EV Tracker data: sales, stock, charging infrastructure, and STEPS
projections.

**Fields:** `region`, `category`, `parameter`, `mode`, `powertrain`, `year`,
`unit`, `value`

**Query parameters (case-sensitive, use exact values):**
| Parameter | Example Values |
|-----------|---------------|
| `region` | `USA`, `China`, `Europe`, `World`, `Norway`, `Germany`, etc. |
| `category` | `Historical`, `Projection-STEPS` |
| `parameter` | `EV sales`, `EV stock`, `EV sales share`, `EV stock share`, `EV charging points`, `Electricity demand`, `Battery demand`, `Oil displacement Mbd` |
| `mode` | `Cars`, `Vans`, `Buses`, `Trucks`, `2 and 3 wheelers`, `EV` |
| `powertrain` | `BEV`, `PHEV`, `FCEV`, `EV` |
| `year` | `2010` through `2030` |

**Example:**
```bash
# US EV car sales in 2023
curl -s "https://api.iea.org/evs?region=USA&category=Historical&parameter=EV+sales&mode=Cars&year=2023"

# Global EV stock share trend
curl -s "https://api.iea.org/evs?region=World&category=Historical&parameter=EV+stock+share&mode=Cars&powertrain=EV"
```

### 2. Energy Prices (`/prices`)

End-use energy prices by country, sector, product, with annual and monthly data.

**Fields:** `CODE_COUNTRY`, `CODE_YEAR`, `CODE_SECTOR`, `CODE_PRODUCT`,
`CODE_INDICATOR`, `CODE_UNIT`, `Unit`, `Country`, `Product`, `Sector`,
`Currency`, `Value`, `updated_at`

**Query parameters (use CODE_ fields for filtering):**
| Parameter | Example Values |
|-----------|---------------|
| `CODE_COUNTRY` | `USA`, `FRANCE`, `GERMANY`, `JAPAN`, `CHINA`, `BELGIUM`, etc. |
| `CODE_SECTOR` | `TRANS`, `IND`, `RES`, `ELEGEN`, `NA` |
| `CODE_PRODUCT` | `GASOLINE`, `DIESEL`, `NATGAS`, `ELECT`, `LPG`, `LIGHTFO`, `FUELOIL`, `STEAMCO`, `HEATPUM` |
| `CODE_INDICATOR` | `PRICE`, `PRICEMONTHLY`, `PRICE CONVERTED`, `HEATHOUSE`, `SHOWER`, `COOKING`, `CARS` |
| `CODE_UNIT` | `USDCUR`, `NCCUR`, `EXTAX`, `TAX`, `USDPPP` |

**Example:**
```bash
# US gasoline prices in transport sector
curl -s "https://api.iea.org/prices?CODE_COUNTRY=USA&CODE_PRODUCT=GASOLINE&CODE_SECTOR=TRANS"

# Natural gas residential prices across OECD
curl -s "https://api.iea.org/prices?CODE_PRODUCT=NATGAS&CODE_SECTOR=RES&CODE_INDICATOR=PRICE"
```

### 3. GHG Emissions (`/ghg`)

CO2 and GHG emissions from fuel combustion, by country, product, and flow type.
Historical data from 1971 to most recent year.

**Fields:** `CODE_COUNTRY`, `COUNTRY`, `CODE_PRODUCT`, `PRODUCT`, `CODE_TIME`,
`TIME`, `CODE_FLOW`, `FLOW`, `VALUE`

**Query parameters (use CODE_ fields):**
| Parameter | Example Values |
|-----------|---------------|
| `CODE_COUNTRY` | `USA`, `CHN`, `IND`, `DEU`, `JPN`, `WORLD`, etc. (OECD-style codes) |
| `CODE_PRODUCT` | `TOTAL`, `COAL`, `OIL`, `NATGAS`, `BIOWASTE`, `HYDRO`, `NUCLEAR`, `SOLWIND`, `OTHER` |
| `CODE_FLOW` | `CO2FUEL` (total CO2 from fuel combustion), `CO2GDP` (CO2/GDP), `CO2POP` (CO2/capita), `GHGFUEL` (total GHG), `ELYIND` (electricity industry), `TRANSP` (transport), `INDUST` (industry), `BUILD` (buildings) |

**Example:**
```bash
# US total CO2 from fuel combustion
curl -s "https://api.iea.org/ghg?CODE_COUNTRY=USA&CODE_PRODUCT=TOTAL&CODE_FLOW=CO2FUEL"

# CO2 intensity (per GDP) for major emitters
curl -s "https://api.iea.org/ghg?CODE_PRODUCT=TOTAL&CODE_FLOW=CO2GDP"
```

**Note:** Without filters, this endpoint returns ~207K records. Always filter by
at least `CODE_COUNTRY` or `CODE_FLOW` to keep response sizes manageable.

### 4. Net Zero Emissions Scenario (`/nze`)

IEA Net Zero Emissions by 2050 (NZE) scenario data -- energy supply, demand,
capacity, emissions projections from 2019 to 2050.

**Fields:** `Year`, `Product`, `Flow`, `Unit`, `Category`, `Value`

**Query parameters:**
| Parameter | Example Values |
|-----------|---------------|
| `Year` | `2019`, `2025`, `2030`, `2035`, `2040`, `2050` |
| `Product` | `Total`, `Oil`, `Coal`, `Natural gas`, `Nuclear`, `Solar PV`, `Wind`, `Bioenergy`, `Hydrogen`, `Electricity`, etc. |
| `Flow` | `Total primary energy demand`, `Electricity generation`, `Power sector`, `Buildings`, `Transport`, `Industry`, etc. |
| `Category` | `Energy`, `CO2 combustion and processes emissions`, `CO2 removal`, `Capacity`, `Economic indicators`, `Population indicators`, etc. |

**Example:**
```bash
# Oil demand in NZE scenario for milestone years
curl -s "https://api.iea.org/nze?Product=Oil&Flow=Total+primary+energy+demand"

# Electricity generation by source in 2050
curl -s "https://api.iea.org/nze?Year=2050&Flow=Electricity+generation"
```

### 5. CCUS Policies (`/ccus`)

Database of carbon capture, utilization and storage policies and regulations
worldwide.

**Fields:** `Base legislation` (nested object with Policy ID, Title, Year,
Jurisdiction, Region, Description, Status, Link), `Region`, `Description`,
`Link`, `Issue`, `Regulation or law`

**Example:**
```bash
# All CCUS policies (small dataset, ~90 records)
curl -s "https://api.iea.org/ccus"
```

### 6. SDG 7 (`/sdg`)

SDG 7 energy access indicators. This is a large dataset; filter to avoid
timeouts.

**Example:**
```bash
curl -s "https://api.iea.org/sdg" --max-time 30
```

---

## Workflow

### Step 1 -- Resolve Intent

Map the user's question to an endpoint:

| User Intent | Endpoint | Key Filters |
|-------------|----------|-------------|
| EV sales, stock, charging | `/evs` | region, year, parameter |
| Energy prices by country | `/prices` | CODE_COUNTRY, CODE_PRODUCT |
| CO2 emissions trends | `/ghg` | CODE_COUNTRY, CODE_FLOW |
| Net zero scenario | `/nze` | Year, Product, Flow |
| CCUS policies | `/ccus` | (small dataset, no filters needed) |
| Energy access | `/sdg` | (filter carefully) |

### Step 2 -- Fetch Data

Use `curl` to query the appropriate endpoint with filters:
```bash
curl -s "https://api.iea.org/{endpoint}?{filters}" --max-time 30
```

Default behavior:
- Always apply at least one filter on large endpoints (ghg, prices, evs)
- Use `--max-time 30` since some endpoints are slow for unfiltered queries
- Parse JSON response with `jq` or `python3 -c "import json..."`

### Step 3 -- Parse Response

All responses are flat JSON arrays:
```json
[
  {"region": "USA", "category": "Historical", "parameter": "EV sales", "mode": "Cars", "powertrain": "BEV", "year": 2023, "unit": "Vehicles", "value": 1100000},
  ...
]
```

No pagination. The full dataset is returned in a single response (which is why
filtering is important for large endpoints).

### Step 4 -- Produce Output

**Format: Raw Data Table + Narrative**

Present a markdown table of the most relevant rows (cap at ~20 rows), then a
narrative summary covering:

1. **Current state** -- most recent value(s) and year
2. **Trend** -- direction and magnitude over time (% change)
3. **Cross-country comparison** if applicable
4. **Context** -- relate to global energy transition goals
5. **Units and caveats** -- always state units; note data vintage

**Example output structure:**
```
## Global EV Car Sales by Region (2019-2023)

| Year | China     | Europe    | USA       | World     |
|------|-----------|-----------|-----------|-----------|
| 2023 | 8,100,000 | 3,200,000 | 1,400,000 | 14,200,000|
| 2022 | 6,900,000 | 2,700,000 | 990,000   | 10,500,000|
| ...  | ...       | ...       | ...       | ...       |

**Summary:** Global EV car sales reached 14.2 million in 2023, up 35% YoY.
China dominated with 57% share. BEVs accounted for ~70% of sales globally.
The IEA STEPS projection estimates 20+ million annual sales by 2030.
Data: IEA Global EV Tracker (api.iea.org/evs).
```

---

## Error Handling

| HTTP Code | Meaning | Action |
|-----------|---------|--------|
| 200 + empty array | No matching data | Broaden filters or check field values |
| 404 | Endpoint not found | Verify endpoint name from the list above |
| 500 | Server error | Retry; IEA API can be intermittent |
| Timeout | Response too large | Add more filters to reduce dataset size |
| JSON parse error | Response truncated | Add filters; unfiltered large endpoints may truncate |

---

## Caveats and Data Limitations

- **Free tier only:** Most IEA detailed energy balance, supply, demand, and
  trade data requires a paid subscription. This skill covers only the 6 free
  endpoints listed above.
- **No API key or auth:** These endpoints are open but not officially documented
  as a stable API. Endpoints may change without notice.
- **Large responses:** The `/ghg` endpoint returns 207K+ records unfiltered.
  Always apply at least one filter. The `/sdg` endpoint can also be very large.
- **Query parameters are case-sensitive:** Use exact field values as shown in
  the response data (e.g., `USA` not `usa`, `GASOLINE` not `gasoline`).
- **No pagination:** Full datasets are returned in a single response. This means
  very large unfiltered queries may time out or return truncated JSON.
- **Data vintage:** Prices and GHG data are typically 1-2 years behind current.
  Check the `updated_at` field (prices) or max year (ghg) for data currency.
- **STEPS projections (EVs):** The `category=Projection-STEPS` data in the EVs
  endpoint reflects IEA Stated Policies Scenario, not a forecast.
- **Country codes vary:** The `/ghg` endpoint uses OECD-style codes (USA, CHN,
  DEU), while `/prices` uses longer names (FRANCE, GERMANY). Check the actual
  response data for the correct code format per endpoint.

---

## Implementation Notes

- Use `curl` with `--max-time 30` for all IEA requests (some endpoints are slow)
- For cross-endpoint queries, make separate requests and merge client-side
- URL-encode spaces as `+` in query parameters (e.g., `EV+sales`)
- All timestamps are in UTC; prices include an `updated_at` field
- See `references/api_reference.md` for the complete field value catalogs
- See `references/python_example.py` for a stdlib-only client example
