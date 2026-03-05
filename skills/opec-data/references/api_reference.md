# OPEC Data API Reference

OPEC does not offer a public REST API. All OPEC websites (asb.opec.org,
momr.opec.org, opec.org) are protected by Cloudflare browser challenges
and return HTTP 403 to all programmatic clients including curl and Python.

This skill sources OPEC data from the **EIA (Energy Information Administration)**
API v2, which publishes comprehensive OPEC production, capacity, pricing, and
supply data as part of its Short-Term Energy Outlook (STEO) and International
datasets.

---

## Data Source 1: EIA STEO

**Base URL:** `https://api.eia.gov/v2/steo/data/`

STEO provides monthly aggregate data for OPEC, OPEC+, and non-OPEC groups,
plus benchmark crude oil prices. Includes historical data and 18-month EIA
forecasts.

### Authentication

Requires a free EIA API key. Sign up at https://www.eia.gov/opendata/

### Request Format

All requests use HTTP GET with URL-encoded query parameters:

```bash
curl -s -G "https://api.eia.gov/v2/steo/data/" \
  --data-urlencode "api_key=YOUR_KEY" \
  --data-urlencode "frequency=monthly" \
  --data-urlencode "facets[seriesId][]=SERIES_ID" \
  --data-urlencode "data[]=value" \
  --data-urlencode "sort[0][column]=period" \
  --data-urlencode "sort[0][direction]=desc" \
  --data-urlencode "length=24"
```

### Response Format

```json
{
  "response": {
    "total": 420,
    "dateFormat": "YYYY-MM",
    "frequency": "monthly",
    "data": [
      {
        "period": "2025-01",
        "seriesId": "COPR_OPEC",
        "seriesDescription": "Crude Oil Production, OPEC Total",
        "value": 27.123,
        "unit": "million barrels per day"
      }
    ]
  },
  "request": { ... },
  "apiVersion": "2.1.12"
}
```

### Complete OPEC-Related Series Catalog

#### Production

| Series ID | Description |
|-----------|-------------|
| `COPR_OPEC` | Crude Oil Production, OPEC Total |
| `COPR_OPECPLUS` | OPEC+ Total |
| `COPR_OPECPLUS_OPEC` | OPEC members subject to OPEC+ agreements |
| `COPR_OPECPLUS_OTHER` | OPEC+ Other Participants Total |
| `COPR_NONOPEC` | Non-OPEC Crude Oil Production |
| `COPR_NONOPECPLUS_XUS` | Non-OPEC+ excl. US Crude Oil Production |
| `PAPR_OPEC` | Total OPEC Petroleum Supply (all liquids) |
| `PAPR_OPECPLUS` | Total OPEC+ Petroleum Supply (all liquids) |
| `PAPR_OPECPLUS_OPEC` | OPEC+ Liquids from OPEC Members |
| `PAPR_OPECPLUS_OTHER` | OPEC+ Liquids from Other Participants |
| `PAPR_NONOPEC` | Total non-OPEC Liquids Production |
| `PAPR_NONOPECPLUS` | Non-OPEC Liquids from non-OPEC+ |
| `PAPR_NONOPECPLUS_XUS` | Non-OPEC Liquids from non-OPEC+ excl. US |
| `PAPR_NONOPEC_I_OPECNC` | Non-OPEC + OPEC non-crude Production |
| `OPEC_NC` | OPEC non-Crude Oil Liquids Production |
| `NONOPEC_NC` | Non-OPEC non-Crude Oil Liquids Production |

#### Capacity and Spare Capacity

| Series ID | Description |
|-----------|-------------|
| `COPC_OPEC` | OPEC Total Crude Oil Production Capacity |
| `COPC_OPEC_R05` | OPEC Middle East Capacity |
| `COPC_OPEC_ROT` | OPEC Other (non-Middle East) Capacity |
| `COPS_OPEC` | OPEC Total Spare Crude Oil Production Capacity |
| `COPS_OPEC_R05` | OPEC Middle East Spare Capacity |
| `COPS_OPEC_ROT` | OPEC Other Spare Capacity |

#### Supply Disruptions

| Series ID | Description |
|-----------|-------------|
| `PADI_OPEC` | Unplanned crude oil disruptions, OPEC |
| `PADI_NONOPEC` | Unplanned liquid fuel disruptions, non-OPEC |

#### Benchmark Prices

| Series ID | Description | Units |
|-----------|-------------|-------|
| `BREPUUS` | Brent crude oil spot price | $/barrel |
| `WTIPUUS` | West Texas Intermediate crude oil price | $/barrel |
| `RAIMUUS` | Imported crude oil price (US avg) | $/barrel |

---

## Data Source 2: EIA International

**Base URL:** `https://api.eia.gov/v2/international/data/`

Provides per-country data for all OPEC member states.

### Key Facets

| Facet | Description | Common Values |
|-------|-------------|---------------|
| `countryRegionId` | ISO country code | SAU, IRQ, ARE, IRN, etc. |
| `productId` | Energy product | 57 = crude oil incl. lease condensate |
| `activityId` | Activity type | 1 = production |
| `unit` | Measurement unit | TBPD = thousand bbl/d |
| `countryRegionTypeId` | Entity type | c = country |

### Request Format

```bash
curl -s -G "https://api.eia.gov/v2/international/data/" \
  --data-urlencode "api_key=YOUR_KEY" \
  --data-urlencode "frequency=annual" \
  --data-urlencode "facets[countryRegionId][]=SAU" \
  --data-urlencode "facets[productId][]=57" \
  --data-urlencode "facets[activityId][]=1" \
  --data-urlencode "facets[unit][]=TBPD" \
  --data-urlencode "data[]=value" \
  --data-urlencode "sort[0][column]=period" \
  --data-urlencode "sort[0][direction]=desc" \
  --data-urlencode "length=10"
```

### OPEC Member Country Codes

| Country | countryRegionId |
|---------|-----------------|
| Algeria | DZA |
| Congo (Brazzaville) | COG |
| Equatorial Guinea | GNQ |
| Gabon | GAB |
| Iran | IRN |
| Iraq | IRQ |
| Kuwait | KWT |
| Libya | LBY |
| Nigeria | NGA |
| Saudi Arabia | SAU |
| UAE | ARE |
| Venezuela | VEN |

### Key OPEC+ Non-OPEC Partners

| Country | countryRegionId |
|---------|-----------------|
| Russia | RUS |
| Kazakhstan | KAZ |
| Mexico | MEX |
| Oman | OMN |
| Azerbaijan | AZE |
| Malaysia | MYS |
| Bahrain | BHR |
| Brunei | BRN |

---

## Common Query Patterns

### OPEC production + spare capacity (side-by-side)

Fetch multiple series by repeating the `facets[seriesId][]` parameter:

```bash
curl -s -G "https://api.eia.gov/v2/steo/data/" \
  --data-urlencode "api_key=${KEY}" \
  --data-urlencode "frequency=monthly" \
  --data-urlencode "facets[seriesId][]=COPR_OPEC" \
  --data-urlencode "facets[seriesId][]=COPS_OPEC" \
  --data-urlencode "facets[seriesId][]=COPC_OPEC" \
  --data-urlencode "data[]=value" \
  --data-urlencode "sort[0][column]=period" \
  --data-urlencode "sort[0][direction]=desc" \
  --data-urlencode "length=72"
```

### Brent and WTI comparison

```bash
curl -s -G "https://api.eia.gov/v2/steo/data/" \
  --data-urlencode "api_key=${KEY}" \
  --data-urlencode "frequency=monthly" \
  --data-urlencode "facets[seriesId][]=BREPUUS" \
  --data-urlencode "facets[seriesId][]=WTIPUUS" \
  --data-urlencode "data[]=value" \
  --data-urlencode "sort[0][column]=period" \
  --data-urlencode "sort[0][direction]=desc" \
  --data-urlencode "length=48"
```

### All OPEC member countries in one query

```bash
curl -s -G "https://api.eia.gov/v2/international/data/" \
  --data-urlencode "api_key=${KEY}" \
  --data-urlencode "frequency=annual" \
  --data-urlencode "facets[countryRegionId][]=SAU" \
  --data-urlencode "facets[countryRegionId][]=IRQ" \
  --data-urlencode "facets[countryRegionId][]=ARE" \
  --data-urlencode "facets[countryRegionId][]=KWT" \
  --data-urlencode "facets[countryRegionId][]=IRN" \
  --data-urlencode "facets[countryRegionId][]=NGA" \
  --data-urlencode "facets[countryRegionId][]=LBY" \
  --data-urlencode "facets[countryRegionId][]=DZA" \
  --data-urlencode "facets[countryRegionId][]=VEN" \
  --data-urlencode "facets[countryRegionId][]=GAB" \
  --data-urlencode "facets[countryRegionId][]=COG" \
  --data-urlencode "facets[countryRegionId][]=GNQ" \
  --data-urlencode "facets[productId][]=57" \
  --data-urlencode "facets[activityId][]=1" \
  --data-urlencode "facets[unit][]=TBPD" \
  --data-urlencode "data[]=value" \
  --data-urlencode "sort[0][column]=period" \
  --data-urlencode "sort[0][direction]=desc" \
  --data-urlencode "start=2020" \
  --data-urlencode "length=500"
```

---

## Why Not Direct OPEC Access?

OPEC publishes data through several web portals:

- **Annual Statistical Bulletin (ASB):** https://asb.opec.org/ -- production,
  reserves, exports, refining, tanker fleet, and more. Interactive charts with
  CSV/Excel download capability via the browser.
- **Monthly Oil Market Report (MOMR):** https://momr.opec.org/ -- supply/demand
  balance, price analysis, production by member. Published as a PDF.
- **OPEC Basket Price:** Daily weighted average of member crude grades. Published
  on opec.org but not accessible programmatically.

All of these require JavaScript rendering and Cloudflare challenge completion.
They cannot be accessed via `curl`, `wget`, or Python `requests`.

**EIA as proxy:** The U.S. EIA independently tracks and publishes OPEC data
as part of its STEO and International datasets. EIA data closely aligns with
OPEC secondary-source figures and is considered a reliable reference by industry
and academia.
