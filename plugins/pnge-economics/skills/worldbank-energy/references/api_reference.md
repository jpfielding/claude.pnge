# World Bank Open Data API v2 -- Reference

Full base URL: `https://api.worldbank.org/v2/`

Default response format is XML. Always append `?format=json` for JSON.

No API key required. No authentication needed.

---

## URL Patterns

### Indicator Data (primary use case)

```
GET /v2/country/{country_codes}/indicator/{indicator_id}?format=json&date={range}&per_page={n}
```

**Examples:**

```bash
# Single country, single indicator
curl -s "https://api.worldbank.org/v2/country/US/indicator/EG.USE.PCAP.KG.OE?format=json&date=2015:2022&per_page=50"

# Multiple countries (semicolon-separated)
curl -s "https://api.worldbank.org/v2/country/US;SA;RU;CN/indicator/NY.GDP.PETR.RT.ZS?format=json&date=2015:2022"

# All countries
curl -s "https://api.worldbank.org/v2/country/all/indicator/EG.ELC.FOSL.ZS?format=json&date=2020&per_page=300"

# World aggregate only
curl -s "https://api.worldbank.org/v2/country/WLD/indicator/EG.ELC.NGAS.ZS?format=json&date=2010:2022"
```

### Country Metadata

```bash
# Single country
curl -s "https://api.worldbank.org/v2/country/US?format=json"

# All countries
curl -s "https://api.worldbank.org/v2/country?format=json&per_page=300"
```

### Indicator Discovery

```bash
# List indicators in topic 5 (Energy & Mining) -- 53 indicators
curl -s "https://api.worldbank.org/v2/topic/5/indicator?format=json&per_page=200"

# Get indicator metadata
curl -s "https://api.worldbank.org/v2/indicator/EG.ELC.FOSL.ZS?format=json"
```

---

## Query Parameters

| Parameter   | Example              | Notes                                           |
|-------------|----------------------|-------------------------------------------------|
| `format`    | `format=json`        | Required for JSON (default is XML)              |
| `date`      | `date=2015:2022`     | Year range; single year also valid: `date=2020` |
| `per_page`  | `per_page=100`       | Results per page (default 50, max ~1000)        |
| `page`      | `page=2`             | Page number for pagination (1-indexed)          |
| `source`    | `source=2`           | Data source ID (2 = World Development Indicators) |
| `MRV`       | `MRV=5`              | Most Recent Values -- return last N data points |
| `MRNEV`     | `MRNEV=1`            | Most Recent Non-Empty Value                     |

**Date format:** Always `YYYY` (annual data only for most energy indicators).

**`MRV` vs `date`:** Use `MRV=5` when you want the 5 most recent data points regardless of year. Use `date=2015:2022` for a specific range.

---

## Response Structure

The API returns a JSON array with two elements: `[pagination_meta, data_array]`.

### Pagination Metadata (index 0)

```json
{
  "page": 1,
  "pages": 54,
  "per_page": 5,
  "total": 266,
  "sourceid": "2",
  "lastupdated": "2026-02-24"
}
```

### Data Records (index 1)

```json
[
  {
    "indicator": {
      "id": "NY.GDP.PETR.RT.ZS",
      "value": "Oil rents (% of GDP)"
    },
    "country": {
      "id": "SA",
      "value": "Saudi Arabia"
    },
    "countryiso3code": "SAU",
    "date": "2021",
    "value": 23.6862940574499,
    "unit": "",
    "obs_status": "",
    "decimal": 1
  }
]
```

**Key fields:**
- `indicator.id` / `indicator.value` -- indicator code and human name
- `country.id` -- ISO2 code (or region code for aggregates)
- `countryiso3code` -- ISO3 code
- `date` -- year as string
- `value` -- numeric value or `null` if no data

### Error Response

```json
[
  {
    "message": [
      {
        "id": "175",
        "key": "Invalid format",
        "value": "The indicator was not found. It may have been deleted or archived."
      }
    ]
  }
]
```

Error IDs:
- `120` -- Invalid parameter value
- `175` -- Indicator not found / archived
- `170` -- Country not found

---

## Pagination

Check `pages` field in metadata. If `pages > 1`, loop through pages:

```python
page = 1
all_data = []
while page <= total_pages:
    # fetch with &page={page}
    all_data.extend(response[1])
    page += 1
```

For `country/all` queries, expect 266 records per year (all countries + aggregates).

---

## Country Codes

### Major Oil & Gas Producers (ISO2)

| Code | Country            | Code | Country         |
|------|--------------------|------|-----------------|
| `US` | United States      | `SA` | Saudi Arabia    |
| `RU` | Russian Federation | `CN` | China           |
| `CA` | Canada             | `IR` | Iran            |
| `IQ` | Iraq               | `AE` | UAE             |
| `KW` | Kuwait             | `BR` | Brazil          |
| `NO` | Norway             | `QA` | Qatar           |
| `NG` | Nigeria            | `AO` | Angola          |
| `DZ` | Algeria            | `MX` | Mexico          |
| `KZ` | Kazakhstan         | `LY` | Libya           |
| `GB` | United Kingdom     | `VE` | Venezuela       |
| `ID` | Indonesia          | `MY` | Malaysia        |
| `AU` | Australia          | `IN` | India           |
| `AR` | Argentina          | `CO` | Colombia        |

### Aggregate / Region Codes

| Code  | Description                           |
|-------|---------------------------------------|
| `WLD` | World (returns as `1W`)               |
| `OED` | OECD members (returns as `OE`)        |
| `EAS` | East Asia & Pacific (returns as `Z4`) |
| `ECS` | Europe & Central Asia                 |
| `LCN` | Latin America & Caribbean             |
| `MEA` | Middle East & North Africa            |
| `NAC` | North America                         |
| `SAS` | South Asia                            |
| `SSF` | Sub-Saharan Africa (returns as `ZG`)  |
| `HIC` | High income countries                 |
| `LIC` | Low income countries                  |
| `LMC` | Lower middle income                   |
| `UMC` | Upper middle income                   |

**Note:** Request codes (left) differ from response codes (right) for some
aggregates. The response `country.id` uses internal codes like `1W`, `OE`,
`Z4`, `ZG`.

---

## Energy & PNGE Indicators (Verified Working)

All indicators below are from Source 2 (World Development Indicators) and
return data as of 2026-02-24.

### Electricity Generation Mix

| Indicator ID       | Description                                              | Unit                 | Latest Year |
|--------------------|----------------------------------------------------------|----------------------|-------------|
| `EG.ELC.FOSL.ZS`  | Electricity from oil, gas, and coal (% of total)         | %                    | 2022        |
| `EG.ELC.NGAS.ZS`  | Electricity from natural gas (% of total)                | %                    | 2022        |
| `EG.ELC.COAL.ZS`  | Electricity from coal (% of total)                       | %                    | 2022        |
| `EG.ELC.PETR.ZS`  | Electricity from oil (% of total)                        | %                    | 2022        |
| `EG.ELC.NUCL.ZS`  | Electricity from nuclear (% of total)                    | %                    | 2022        |
| `EG.ELC.HYRO.ZS`  | Electricity from hydroelectric (% of total)              | %                    | 2022        |
| `EG.ELC.RNEW.ZS`  | Renewable electricity output (% of total)                | %                    | 2021        |
| `EG.ELC.RNWX.ZS`  | Renewable electricity excl. hydro (% of total)           | %                    | 2021        |
| `EG.ELC.RNWX.KH`  | Renewable electricity excl. hydro (kWh)                  | kWh                  | 2021        |

### Energy Consumption & Intensity

| Indicator ID            | Description                                         | Unit                      | Latest Year |
|-------------------------|-----------------------------------------------------|---------------------------|-------------|
| `EG.USE.PCAP.KG.OE`    | Energy use per capita                               | kg oil equivalent/capita  | 2022        |
| `EG.USE.ELEC.KH.PC`    | Electric power consumption per capita               | kWh/capita                | 2022        |
| `EG.USE.COMM.FO.ZS`    | Fossil fuel energy consumption (% of total)         | %                         | 2022        |
| `EG.FEC.RNEW.ZS`       | Renewable energy consumption (% of total final)     | %                         | 2021        |
| `EG.EGY.PRIM.PP.KD`    | Energy intensity (primary energy)                   | MJ/$2021 PPP GDP          | 2022        |
| `EG.GDP.PUSE.KO.PP.KD` | GDP per unit of energy use                          | const 2021 PPP $/kg OE    | 2022        |
| `EG.IMP.CONS.ZS`       | Net energy imports (% of energy use)                | %                         | 2022        |
| `EG.ELC.LOSS.ZS`       | Transmission & distribution losses (% of output)    | %                         | 2022        |

### Petroleum & Gas Economics

| Indicator ID          | Description                                 | Unit       | Latest Year |
|-----------------------|---------------------------------------------|------------|-------------|
| `NY.GDP.PETR.RT.ZS`  | Oil rents (% of GDP)                        | %          | 2021        |
| `NY.GDP.NGAS.RT.ZS`  | Natural gas rents (% of GDP)                | %          | 2021        |
| `NY.GDP.TOTL.RT.ZS`  | Total natural resources rents (% of GDP)    | %          | 2021        |
| `NY.GDP.MINR.RT.ZS`  | Mineral rents (% of GDP)                    | %          | 2021        |
| `NY.ADJ.DNGY.GN.ZS`  | Energy depletion (% of GNI)                 | %          | 2021        |
| `TX.VAL.FUEL.ZS.UN`  | Fuel exports (% of merchandise exports)     | %          | 2022        |
| `TM.VAL.FUEL.ZS.UN`  | Fuel imports (% of merchandise imports)     | %          | 2022        |

### Electricity Access

| Indicator ID         | Description                                       | Unit  | Latest Year |
|----------------------|---------------------------------------------------|-------|-------------|
| `EG.ELC.ACCS.ZS`    | Access to electricity (% of population)           | %     | 2022        |
| `EG.ELC.ACCS.RU.ZS` | Access to electricity, rural (% of rural pop)     | %     | 2022        |
| `EG.ELC.ACCS.UR.ZS` | Access to electricity, urban (% of urban pop)     | %     | 2022        |

---

## Archived / Unavailable Indicators

These indicators appear in topic 5 metadata but are in Source 57 (WDI Archives)
and no longer return data from the live API:

| Indicator ID        | Description                                  | Status   |
|---------------------|----------------------------------------------|----------|
| `EN.ATM.CO2E.KT`   | CO2 emissions (kt)                           | Archived |
| `EN.ATM.CO2E.LF.KT`| CO2 emissions from liquid fuel (kt)          | Archived |
| `EN.ATM.CO2E.GF.ZS`| CO2 emissions from gaseous fuel (%)          | Archived |
| `EP.PMP.SGAS.CD`   | Pump price for gasoline ($/liter)            | Archived |
| `EP.PMP.DESL.CD`   | Pump price for diesel ($/liter)              | Archived |
| `EG.ELC.PROD.KH`   | Electricity production (kWh)                 | Archived |

---

## Data Freshness

- WDI database last updated: check `lastupdated` field in response metadata
- Most indicators have a 1-2 year lag (e.g., latest data in 2026 is for 2022)
- Resource rent indicators (`NY.GDP.*RT*`) often lag an additional year
- Renewable energy indicators sometimes lag one year behind fossil fuel data
- Data is annual only -- no monthly or weekly resolution

---

## Rate Limits

No published rate limit, but the API is shared infrastructure:
- Use `per_page` up to 1000 to minimize round trips
- Add 100ms delay between requests in loops
- Cache responses when running repeated queries
- For bulk downloads, use the World Bank Data Catalog bulk files instead
