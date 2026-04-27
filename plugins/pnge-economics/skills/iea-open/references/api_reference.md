# IEA Open Data API Reference

The IEA provides several free, open JSON API endpoints at `https://api.iea.org/`.
No API key or authentication is required. Most detailed energy balance and trade
data requires a paid IEA subscription and is not covered here.

---

## Verified Free Endpoints

| Path | Method | Auth | Description |
|------|--------|------|-------------|
| `/evs` | GET | None | Global EV Tracker (sales, stock, charging, projections) |
| `/prices` | GET | None | Energy end-use prices by country, sector, product |
| `/ghg` | GET | None | CO2 and GHG emissions from fuel combustion |
| `/nze` | GET | None | Net Zero Emissions by 2050 scenario data |
| `/ccus` | GET | None | CCUS policies and regulations database |
| `/sdg` | GET | None | SDG 7 energy access indicators |

### Confirmed Non-Working Endpoints (404)

These return HTTP 404 as of March 2026:
`/hydrogen`, `/weo`, `/ogc`, `/critical-minerals`, `/emissions`, `/fuels`,
`/balances`, `/electricity`, `/supply`, `/co2`, `/methane`, `/rte`,
`/indicators`, `/parcc`, `/tcep`, `/tfc`, `/tpes`, `/wbes`,
`/nze/electricity`, `/nze/emissions`

---

## Endpoint 1: Electric Vehicles (`/evs`)

**URL:** `https://api.iea.org/evs`

**Response:** JSON array, ~16,000 records unfiltered.

### Fields

| Field | Type | Description |
|-------|------|-------------|
| `region` | string | Country or region name |
| `category` | string | `Historical` or `Projection-STEPS` |
| `parameter` | string | Metric type |
| `mode` | string | Vehicle type |
| `powertrain` | string | Drive technology |
| `year` | integer | Year (2010-2030) |
| `unit` | string | Unit of measurement |
| `value` | number | Data value |

### Dimension Values

**region (sample):** Africa, Asia Pacific, Australia, Austria, Belgium, Brazil,
Canada, Chile, China, Colombia, Czech Republic, Denmark, EU27, Estonia, Europe,
Finland, France, Germany, Greece, Hungary, Iceland, India, Indonesia, Ireland,
Israel, Italy, Japan, Korea, Latvia, Lithuania, Mexico, Netherlands, New Zealand,
Norway, Other Europe, Poland, Portugal, Romania, Slovakia, Slovenia, South Africa,
Spain, Sweden, Switzerland, Thailand, Turkey, USA, United Kingdom, World

**category:** Historical, Projection-STEPS

**parameter:** Battery demand, EV charging points, EV sales, EV sales share,
EV stock, EV stock share, Electricity demand, Oil displacement Mbd,
Oil displacement million lge

**mode:** 2 and 3 wheelers, Buses, Cars, EV, Trucks, Vans

**powertrain:** BEV, EV, FCEV, PHEV, Publicly available fast, Publicly available slow

### Example Queries

```bash
# All US EV data
curl -s "https://api.iea.org/evs?region=USA"

# Global EV car sales, historical only
curl -s "https://api.iea.org/evs?region=World&category=Historical&parameter=EV+sales&mode=Cars"

# EV stock share trend for China
curl -s "https://api.iea.org/evs?region=China&parameter=EV+stock+share&mode=Cars&powertrain=EV"

# BEV sales in 2023 for all regions
curl -s "https://api.iea.org/evs?year=2023&parameter=EV+sales&powertrain=BEV&mode=Cars"
```

---

## Endpoint 2: Energy Prices (`/prices`)

**URL:** `https://api.iea.org/prices`

**Response:** JSON array, ~41,000 records unfiltered.

### Fields

| Field | Type | Description |
|-------|------|-------------|
| `CODE_COUNTRY` | string | Country code (uppercase) |
| `CODE_YEAR` | string | Year or date (format varies: "2022" or "2024-06-01") |
| `CODE_SECTOR` | string | Sector code |
| `CODE_PRODUCT` | string | Product code |
| `CODE_INDICATOR` | string | Indicator type |
| `CODE_UNIT` | string | Unit code |
| `Unit` | string | Human-readable unit |
| `Country` | string | Country name |
| `Product` | string | Product name |
| `Sector` | string | Sector name |
| `Currency` | string | Currency description |
| `Value` | number | Price value |
| `updated_at` | string | ISO timestamp of last update |

### Dimension Values

**CODE_COUNTRY (sample):** AUSTRALIA, AUSTRIA, BELGIUM, BRAZIL, CANADA, CHILE,
CHINA, COLOMBIA, COSTARIC, CZECHREP, DENMARK, ESTONIA, FINLAND, FRANCE, GERMANY,
GREECE, HUNGARY, INDIA, INDONESI, IRELAND, ISRAEL, ITALY, JAPAN, KOREA, LATVIA,
LITHUANI, LUXEMBOU, MEXICO, NETHERLA, NEWZEALA, NORWAY, POLAND, PORTUGAL,
ROMANIA, SLOVAKIA, SLOVENIA, SOUTHAFR, SPAIN, SWEDEN, SWITZERL, TURKEY, UK, USA

**CODE_PRODUCT:** GASOLINE, DIESEL, NATGAS, ELECT, LPG, LIGHTFO, FUELOIL,
STEAMCO, HEATPUM

**CODE_SECTOR:** TRANS, IND, RES, ELEGEN, NA,
Commercial and public services (also appears as full name)

**CODE_INDICATOR:** PRICE, PRICEMONTHLY, PRICE CONVERTED, HEATHOUSE, SHOWER,
COOKING, CARS

**CODE_UNIT:** USDCUR (USD current), NCCUR (national currency), EXTAX
(ex-tax in USD), TAX (tax component in USD), USDPPP (USD PPP)

### Example Queries

```bash
# US gasoline prices
curl -s "https://api.iea.org/prices?CODE_COUNTRY=USA&CODE_PRODUCT=GASOLINE"

# Electricity prices for industry across countries (annual)
curl -s "https://api.iea.org/prices?CODE_PRODUCT=ELECT&CODE_SECTOR=IND&CODE_INDICATOR=PRICE"

# Monthly diesel prices in Germany
curl -s "https://api.iea.org/prices?CODE_COUNTRY=GERMANY&CODE_PRODUCT=DIESEL&CODE_INDICATOR=PRICEMONTHLY"
```

---

## Endpoint 3: GHG Emissions (`/ghg`)

**URL:** `https://api.iea.org/ghg`

**Response:** JSON array, ~207,000 records unfiltered. ALWAYS filter.

### Fields

| Field | Type | Description |
|-------|------|-------------|
| `CODE_COUNTRY` | string | Country code |
| `COUNTRY` | string | Country name |
| `CODE_PRODUCT` | string | Energy product code |
| `PRODUCT` | string | Product name |
| `CODE_TIME` | string | Year as string |
| `TIME` | string | Year as string |
| `CODE_FLOW` | string | Emission flow/metric code |
| `FLOW` | string | Flow description |
| `VALUE` | number | Data value |

### Dimension Values

**CODE_COUNTRY (sample):** USA, CHN, IND, JPN, DEU, GBR, FRA, RUS, BRA, CAN,
KOR, AUS, IDN, MEX, SAU, ZAF, TUR, ARG, IRN, IRQ, and ~150 more

**CODE_PRODUCT:** TOTAL, Biofuels and waste, Coal peat and oil shale, Hydro,
Natural gas, Nuclear, Oil, Other, Solar wind and other renewables

**CODE_FLOW (key metrics):**
| Code | Description |
|------|-------------|
| `CO2FUEL` | Total CO2 emissions from fuel combustion (kt CO2) |
| `GHGFUEL` | Total GHG emissions from fuel combustion (tCO2eq) |
| `GHGENRG` | Total GHG emissions from energy (tCO2eq) |
| `GHGFUGI` | Total GHG emissions from fugitive |
| `CO2GDP` | CO2/GDP (kgCO2 per 2015 USD) |
| `CO2GDPPP` | CO2/GDP PPP (kgCO2 per 2015 USD) |
| `CO2POP` | CO2/population (tCO2 per capita) |
| `CO2TES` | CO2/TES (tCO2 per TJ) |
| `ELYHTPR` | Electricity and heat producers |
| `TRANSP` | Transport Sector (used via FLOW field) |
| `INDUST` | Industry Sector |
| `BUILD` | Buildings |
| `OTHERS` | Others |
| `TES` | Total Energy Supply |

**Time range:** 1971 to 2024

### Example Queries

```bash
# US total CO2 from fuel combustion
curl -s "https://api.iea.org/ghg?CODE_COUNTRY=USA&CODE_PRODUCT=TOTAL&CODE_FLOW=CO2FUEL"

# China CO2 per capita
curl -s "https://api.iea.org/ghg?CODE_COUNTRY=CHN&CODE_FLOW=CO2POP"

# Global CO2 emissions from coal
curl -s "https://api.iea.org/ghg?CODE_COUNTRY=WORLD&CODE_PRODUCT=Coal%2C+peat+and+oil+shale&CODE_FLOW=CO2FUEL"
```

---

## Endpoint 4: Net Zero Emissions (`/nze`)

**URL:** `https://api.iea.org/nze`

**Response:** JSON array, ~6,700 records unfiltered.

### Fields

| Field | Type | Description |
|-------|------|-------------|
| `Year` | integer | Scenario year (2019-2050) |
| `Product` | string | Energy product/technology |
| `Flow` | string | Activity or end-use category |
| `Unit` | string | Unit of measurement |
| `Category` | string | Broad classification |
| `Value` | number | Scenario value |

### Dimension Values

**Year:** 2019, 2020, 2021, 2022, 2025, 2030, 2035, 2040, 2050

**Product (sample):** Total, Oil, Coal, Natural gas, Nuclear, Solar PV, Wind,
Bioenergy, Hydrogen, Ammonia, Electricity, Battery storage total,
Concentrating solar power, District heat, Biomethane, and more

**Category:** Activity of stock, CO2 combustion and processes emissions,
CO2 combustion processes removal, CO2 removal, Capacity, Economic indicators,
Energy, Energy intensity, Industrial production, Population indicators,
CO2 emissions intensity

**Flow (sample):** Total primary energy demand, Electricity generation,
Power sector, Buildings, Transport, Industry, Agriculture, Aviation,
Cement, Chemical and petrochemical, Crude steel, Biofuels production,
GDP per capita, Installed total power capacity, and more

### Example Queries

```bash
# Oil demand trajectory in NZE
curl -s "https://api.iea.org/nze?Product=Oil&Flow=Total+primary+energy+demand"

# All electricity generation sources in 2050
curl -s "https://api.iea.org/nze?Year=2050&Flow=Electricity+generation"

# CO2 emissions trajectory
curl -s "https://api.iea.org/nze?Category=CO2+combustion+and+processes+emissions&Flow=Total+CO2"
```

---

## Endpoint 5: CCUS Policies (`/ccus`)

**URL:** `https://api.iea.org/ccus`

**Response:** JSON array, ~90 records. Small dataset, no filtering needed.

Each record contains a nested `Base legislation` object with policy metadata
plus fields for `Region`, `Description`, `Link`, `Issue`, and
`Regulation or law`.

---

## Endpoint 6: SDG 7 (`/sdg`)

**URL:** `https://api.iea.org/sdg`

**Response:** Very large JSON array. Use with caution and apply a timeout.

---

## Rate Limits and Performance

- No documented rate limits on the free endpoints
- Unfiltered `/ghg` returns ~15MB of JSON; always filter
- Unfiltered `/prices` returns ~5MB of JSON
- Unfiltered `/evs` returns ~2MB of JSON
- Use `--max-time 30` with curl to handle slow responses
- Very large responses may truncate (invalid JSON); add filters to reduce size
