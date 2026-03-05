---
name: worldbank-energy
description: >
  Query and analyze global energy data from the World Bank Open Data API v2.
  Use this skill whenever the user asks about international energy statistics,
  global electricity generation mix, oil or gas rents as percent of GDP,
  energy use per capita across countries, fossil fuel dependency by nation,
  renewable energy adoption worldwide, fuel exports and imports as share of
  trade, or any cross-country energy comparison. Trigger for phrases like
  "compare energy use across countries", "oil rents as percent of GDP",
  "which countries depend most on petroleum", "global electricity from natural
  gas", "renewable energy share by country", "energy intensity comparison",
  "OPEC nations oil dependency", "fuel exports as share of trade", or any
  request for international energy figures and country-level energy indicators.
  Produces ranked tables and narrative analysis with global context.
---

# World Bank Open Data -- Energy Skill

Fetches and analyzes global energy indicators from the World Bank Indicators
API v2 (api.worldbank.org/v2). Covers 200+ countries and aggregates, annual
data from 1960-present for many indicators. Focused on electricity generation
mix, resource rents, energy consumption, and fuel trade metrics relevant to
petroleum engineering.

## API Key Handling

No API key required. The World Bank Open Data API is fully public.

---

## API Structure

**Base URL:** `https://api.worldbank.org/v2/`

**Response format:** Default is XML. Always append `?format=json`.

**Primary endpoint pattern:**
```
GET /v2/country/{country_codes}/indicator/{indicator_id}?format=json&date={range}&per_page={n}
```

**Key parameters:**
| Parameter  | Example                | Notes                                      |
|------------|------------------------|--------------------------------------------|
| `format`   | `format=json`          | Required for JSON output                   |
| `date`     | `date=2015:2022`       | Year range; single year: `date=2020`       |
| `per_page` | `per_page=100`         | Results per page (default 50, max ~1000)   |
| `page`     | `page=2`               | Pagination (1-indexed)                     |
| `MRV`      | `MRV=5`                | Most Recent Values (last N data points)    |
| `MRNEV`    | `MRNEV=1`              | Most Recent Non-Empty Value                |

**Country codes:** ISO2 codes separated by semicolons, or `all` for all
countries, or `WLD` for world aggregate only.

---

## Key Indicators by Domain

See `references/api_reference.md` for the full verified indicator catalog.

### Electricity Generation Mix
| Indicator ID      | Description                                    |
|-------------------|------------------------------------------------|
| `EG.ELC.FOSL.ZS`  | Electricity from oil, gas, and coal (% total) |
| `EG.ELC.NGAS.ZS`  | Electricity from natural gas (% total)        |
| `EG.ELC.COAL.ZS`  | Electricity from coal (% total)               |
| `EG.ELC.PETR.ZS`  | Electricity from oil (% total)                |
| `EG.ELC.NUCL.ZS`  | Electricity from nuclear (% total)            |
| `EG.ELC.HYRO.ZS`  | Electricity from hydroelectric (% total)      |
| `EG.ELC.RNEW.ZS`  | Renewable electricity output (% total)        |
| `EG.ELC.RNWX.ZS`  | Renewables excl. hydro (% total)              |

### Energy Consumption and Intensity
| Indicator ID           | Description                                  |
|------------------------|----------------------------------------------|
| `EG.USE.PCAP.KG.OE`   | Energy use per capita (kg oil equiv)         |
| `EG.USE.ELEC.KH.PC`   | Electric power consumption (kWh/capita)      |
| `EG.USE.COMM.FO.ZS`   | Fossil fuel consumption (% of total)         |
| `EG.FEC.RNEW.ZS`      | Renewable consumption (% of final energy)    |
| `EG.EGY.PRIM.PP.KD`   | Energy intensity (MJ/$2021 PPP GDP)          |
| `EG.IMP.CONS.ZS`      | Net energy imports (% of energy use)         |

### Petroleum and Gas Economics
| Indicator ID         | Description                                   |
|----------------------|-----------------------------------------------|
| `NY.GDP.PETR.RT.ZS`  | Oil rents (% of GDP)                         |
| `NY.GDP.NGAS.RT.ZS`  | Natural gas rents (% of GDP)                 |
| `NY.GDP.TOTL.RT.ZS`  | Total natural resources rents (% of GDP)     |
| `NY.GDP.MINR.RT.ZS`  | Mineral rents (% of GDP)                     |
| `TX.VAL.FUEL.ZS.UN`  | Fuel exports (% of merchandise exports)      |
| `TM.VAL.FUEL.ZS.UN`  | Fuel imports (% of merchandise imports)       |

### Common Country Codes for PNGE
| Code | Country           | Code | Country          |
|------|-------------------|------|------------------|
| `US` | United States     | `SA` | Saudi Arabia     |
| `RU` | Russia            | `CN` | China            |
| `CA` | Canada            | `IQ` | Iraq             |
| `AE` | UAE               | `NO` | Norway           |
| `QA` | Qatar             | `NG` | Nigeria          |
| `IR` | Iran              | `DZ` | Algeria          |
| `BR` | Brazil            | `MX` | Mexico           |
| `KW` | Kuwait            | `AU` | Australia        |

### Aggregate Codes
| Code  | Region/Group                  |
|-------|-------------------------------|
| `WLD` | World                         |
| `OED` | OECD members                  |
| `EAS` | East Asia and Pacific         |
| `MEA` | Middle East and North Africa  |
| `NAC` | North America                 |
| `SSF` | Sub-Saharan Africa            |
| `HIC` | High income countries         |

---

## Workflow

### Step 1 -- Resolve Intent

Map the user's question to one or more indicator IDs. If the question involves:
- **Country comparison** -> select indicator + multiple country codes
- **Time trend** -> select indicator + single country + date range
- **Global ranking** -> select indicator + `all` countries + `MRV=1`
- **Generation mix** -> fetch multiple EG.ELC.* indicators for one country

If unsure which indicator matches, check `references/api_reference.md` or
query the indicator metadata:
```bash
curl -s "https://api.worldbank.org/v2/topic/5/indicator?format=json&per_page=200" \
  | python3 -c "
import sys, json
data = json.load(sys.stdin)
for ind in data[1]:
    print(f'{ind[\"id\"]}: {ind[\"name\"]}')
"
```

### Step 2 -- Fetch Data

Build the URL with appropriate filters. Default behavior:
- Use `date=2015:2022` unless the user specifies a different range
- Use `per_page=1000` to minimize pagination
- For rankings, use `MRV=1` to get the most recent value per country

**Single country time series:**
```bash
curl -s "https://api.worldbank.org/v2/country/US/indicator/EG.ELC.NGAS.ZS?format=json&date=2010:2022&per_page=50"
```

**Multi-country comparison:**
```bash
curl -s "https://api.worldbank.org/v2/country/US;SA;RU;CN;IQ;AE;NO;CA/indicator/NY.GDP.PETR.RT.ZS?format=json&date=2015:2021&per_page=200"
```

**Global ranking (all countries, most recent value):**
```bash
curl -s "https://api.worldbank.org/v2/country/all/indicator/NY.GDP.PETR.RT.ZS?format=json&MRV=1&per_page=300"
```

### Step 3 -- Parse Response

Response is a JSON array: `[pagination_meta, data_records]`.

```python
import json, urllib.request

url = "https://api.worldbank.org/v2/country/US/indicator/EG.ELC.NGAS.ZS?format=json&date=2015:2022"
with urllib.request.urlopen(url) as resp:
    data = json.loads(resp.read())

meta = data[0]      # {"page": 1, "pages": 1, "per_page": 50, "total": 8, ...}
records = data[1]   # [{"indicator": {...}, "country": {...}, "date": "2022", "value": 38.72}, ...]
```

Always check:
- `meta["pages"]` -- if greater than 1, paginate with `&page=2`, `&page=3`, etc.
- `record["value"]` -- can be `null` if no data for that country/year
- `meta["total"]` -- total records across all pages

### Step 4 -- Filter and Sort

For rankings, filter out:
- Records where `value` is `null`
- Aggregate/region entries (ISO3 codes with digits or that are not 3 alpha chars)

```python
# Filter to real countries with non-null values
valid = [
    r for r in records
    if r["value"] is not None
    and len(r.get("countryiso3code", "")) == 3
    and r["countryiso3code"].isalpha()
]
# Sort descending by value for rankings
ranked = sorted(valid, key=lambda r: r["value"], reverse=True)
```

### Step 5 -- Produce Output

**Format: Raw Data Table + Narrative**

Present a markdown table of the most relevant rows (cap at ~20 rows for
readability), then a narrative summary covering:

1. **Current state** -- most recent values and date for the queried countries
2. **Trend** -- direction and magnitude over the time window (use % change)
3. **Comparative context** -- how countries rank relative to each other
4. **PNGE relevance** -- what the data means for petroleum engineering
   (e.g., petrostate dependency, energy transition pace, gas market structure)
5. **Units and caveats** -- always state units; note data lag and limitations

**Example output structure:**
```
## Oil Rents as % of GDP -- Major Producers (2021)

| Country       | Oil Rents (% GDP) |
|---------------|-------------------|
| Iraq          | 42.79             |
| Saudi Arabia  | 23.69             |
| UAE           | 15.67             |
| Russia        | 9.67              |
| Norway        | 6.06              |
| Canada        | 2.83              |
| United States | 0.61              |
| China         | 0.31              |

**Summary:** Iraq derives the highest share of GDP from oil rents at 42.8% (2021),
followed by Saudi Arabia at 23.7%. The US, despite being the world's largest
crude producer, shows only 0.6% oil rent/GDP due to its highly diversified
economy. Oil rents dropped sharply across all producers in 2020 (COVID demand
shock) before rebounding in 2021. Data for 2022 is not yet available for this
indicator. Units are oil rents as defined by the World Bank: the difference
between the value of crude oil production at world prices and total costs of
production, expressed as a share of GDP.
```

---

## Pagination

If `meta["pages"] > 1`, paginate:
```python
import json, urllib.request

all_records = []
page = 1
while page <= total_pages:
    url = f"...&page={page}&per_page=1000"
    with urllib.request.urlopen(url) as resp:
        data = json.loads(resp.read())
    meta = data[0]
    total_pages = meta["pages"]
    all_records.extend(data[1] or [])
    page += 1
```

For `country/all` queries, expect ~266 records per year (countries + aggregates).
A 10-year range for all countries produces ~2660 records across ~3 pages.

## Error Handling

| HTTP Code | Meaning                    | Action                                        |
|-----------|----------------------------|-----------------------------------------------|
| 200       | Success                    | Parse normally                                |
| 200 + msg | Indicator archived/invalid | Check indicator ID; see archived list below   |
| 200 + null data | No data for filters | Widen date range or try different countries   |
| 400       | Malformed request          | Check URL encoding and parameter names        |
| 503       | Service unavailable        | Retry after 5 seconds (max 3 retries)         |

**API error response (HTTP 200 with error body):**
```json
[{"message": [{"id": "175", "key": "Invalid format", "value": "The indicator was not found."}]}]
```

Always check if `data[0]` contains a `"message"` key before accessing `data[1]`.

---

## Archived Indicators

These indicators are frequently referenced but no longer available in the live
WDI (Source 2). They were moved to Source 57 (WDI Database Archives) and do
not return data:

| Indicator ID         | Description                    | Replacement                       |
|----------------------|--------------------------------|-----------------------------------|
| `EN.ATM.CO2E.KT`    | CO2 emissions (kt)             | Use Climate Watch via climatewatchdata.org |
| `EN.ATM.CO2E.LF.KT` | CO2 from liquid fuel (kt)      | Use Climate Watch                 |
| `EN.ATM.CO2E.GF.ZS` | CO2 from gaseous fuel (%)      | Use Climate Watch                 |
| `EP.PMP.SGAS.CD`    | Gasoline pump price ($/liter)  | Use GIZ data directly             |
| `EP.PMP.DESL.CD`    | Diesel pump price ($/liter)    | Use GIZ data directly             |
| `EG.ELC.PROD.KH`    | Electricity production (kWh)   | Use EG.ELC.RNWX.KH for renewables |

---

## Data Quality and Caveats

- **Annual resolution only** -- no monthly, weekly, or daily data available.
  For high-frequency energy data, use the EIA skill instead.
- **1-2 year data lag** -- most energy indicators report through 2022 as of
  2026. Resource rent indicators often lag an additional year (latest: 2021).
- **Null values are common** -- many developing countries have gaps in energy
  data. Always filter nulls before ranking or computing averages.
- **Aggregate codes in rankings** -- when querying `all` countries, the response
  includes regional aggregates (World, OECD, Sub-Saharan Africa, etc.) alongside
  individual countries. Filter by ISO3 code length and alpha-only characters.
- **Methodology changes** -- WDI definitions can change between releases. Check
  `indicator.sourceNote` in the indicator metadata for current methodology.
- **Source organizations vary** -- electricity data comes from IEA, rent data
  from World Bank estimates, trade data from COMTRADE. Methodological
  differences may cause slight inconsistencies across indicators.

---

## Implementation Notes

- **Use `python3` (stdlib only)** for all API calls and data processing
- **Use `urllib.request` and `json`** -- no external dependencies needed
- **Python client** -- see `references/python_example.py` for a complete
  stdlib-only client with `WorldBankClient`, `QueryParams`, ranking helpers,
  and formatted table output
- **Response parsing** -- always access `data[0]` for pagination metadata and
  `data[1]` for records; check for `"message"` key in `data[0]` for errors
- **Filtering aggregates** -- when building country rankings, exclude records
  where `countryiso3code` contains digits or is not exactly 3 alpha characters
- **Rate limiting** -- add 100ms delay between paginated requests; no hard limit
  published but the API is shared infrastructure
