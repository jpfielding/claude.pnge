---
name: opec-data
description: >
  Query OPEC crude oil production, spare capacity, quotas, and oil price benchmarks
  using EIA STEO and International datasets as the programmatic data source. Use this
  skill whenever the user asks about OPEC production levels, OPEC+ output agreements,
  crude oil spare capacity, Brent or WTI crude oil prices, OPEC member country
  production, oil supply disruptions, or global oil market balances. Trigger for
  phrases like "OPEC production", "OPEC+ output", "spare capacity", "Brent price",
  "WTI price", "Saudi production", "oil quotas", "crude oil supply", "OPEC basket",
  "oil market outlook", or any request about OPEC member petroleum statistics.
  Produces trend summaries and raw data tables with narrative analysis.
---

# OPEC Data Skill

Fetches and analyzes OPEC production, capacity, and oil price data. OPEC does not
provide a public REST API; all its web properties (asb.opec.org, momr.opec.org,
opec.org) are behind Cloudflare browser challenges and block programmatic access.

**Primary data source:** EIA Short-Term Energy Outlook (STEO) API at
`api.eia.gov/v2/steo/data/` which publishes monthly OPEC aggregate production,
capacity, spare capacity, and crude price benchmarks with both historical data and
18-month forecasts.

**Secondary data source:** EIA International dataset at
`api.eia.gov/v2/international/data/` which publishes per-country crude oil
production (annual and monthly) for all OPEC member states.

## API Key Handling

Uses the same EIA API key as the `eia-data` skill.

Resolution order (stop at first success):

1. **`~/.config/eia/credentials`** (default) -- parse `api_key=<value>` from this file
2. **`EIA_API_KEY` env var** -- fallback if credentials file is absent
3. **User-provided in conversation** -- fallback if neither above is set
4. **Prompt the user** -- "Please provide your EIA API key. You can get one free at https://www.eia.gov/opendata/ -- or store it in `~/.config/eia/credentials` as `api_key=YOUR_KEY` (chmod 600)."

Never hardcode or log the key. Pass it as a query parameter `?api_key=<KEY>`.

**Reading the credentials file (bash):**
```bash
KEY=$(grep '^api_key=' ~/.config/eia/credentials 2>/dev/null | cut -d= -f2)
[ -z "$KEY" ] && KEY="${EIA_API_KEY}"
```

---

## API Structure

### STEO Dataset (Aggregates + Forecasts)

**Base URL:** `https://api.eia.gov/v2/steo/data/`

Returns monthly data series by `seriesId`. Each series has historical values and
18-month EIA forecasts.

**Key parameters:**
| Parameter | Example | Notes |
|-----------|---------|-------|
| `api_key` | `api_key=YOUR_KEY` | Required |
| `frequency` | `frequency=monthly` | monthly or annual |
| `facets[seriesId][]` | `facets[seriesId][]=COPR_OPEC` | Filter by series |
| `data[]` | `data[]=value` | Required to get values |
| `start` | `start=2023-01` | Inclusive |
| `end` | `end=2025-12` | Inclusive |
| `sort[0][column]` | `sort[0][column]=period` | Sort field |
| `sort[0][direction]` | `sort[0][direction]=desc` | asc or desc |
| `length` | `length=5000` | Max rows per request |

**Example (OPEC total production, last 12 months):**
```bash
KEY=$(grep '^api_key=' ~/.config/eia/credentials 2>/dev/null | cut -d= -f2)
curl -s -G "https://api.eia.gov/v2/steo/data/" \
  --data-urlencode "api_key=${KEY}" \
  --data-urlencode "frequency=monthly" \
  --data-urlencode "facets[seriesId][]=COPR_OPEC" \
  --data-urlencode "data[]=value" \
  --data-urlencode "sort[0][column]=period" \
  --data-urlencode "sort[0][direction]=desc" \
  --data-urlencode "length=12"
```

### International Dataset (Per-Country)

**Base URL:** `https://api.eia.gov/v2/international/data/`

Returns per-country production, consumption, imports, and exports.

**Key parameters:**
| Parameter | Example | Notes |
|-----------|---------|-------|
| `facets[countryRegionId][]` | `facets[countryRegionId][]=SAU` | ISO country code |
| `facets[productId][]` | `facets[productId][]=57` | 57 = crude oil incl. lease condensate |
| `facets[activityId][]` | `facets[activityId][]=1` | 1 = production |
| `facets[unit][]` | `facets[unit][]=TBPD` | TBPD = thousand barrels per day |

**Example (Saudi Arabia crude production, annual):**
```bash
curl -s -G "https://api.eia.gov/v2/international/data/" \
  --data-urlencode "api_key=${KEY}" \
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

---

## Key STEO Series IDs

### OPEC Production
| Series ID | Description | Units |
|-----------|-------------|-------|
| `COPR_OPEC` | Crude Oil Production, OPEC Total | million bbl/d |
| `COPR_OPECPLUS` | OPEC+ Total | million bbl/d |
| `COPR_OPECPLUS_OPEC` | OPEC members subject to OPEC+ agreements | million bbl/d |
| `COPR_OPECPLUS_OTHER` | OPEC+ Other Participants Total | million bbl/d |
| `COPR_NONOPEC` | Non-OPEC Crude Oil Production | million bbl/d |
| `COPR_NONOPECPLUS_XUS` | Non-OPEC+ excl. US Crude Oil Production | million bbl/d |

### OPEC Capacity and Spare
| Series ID | Description | Units |
|-----------|-------------|-------|
| `COPC_OPEC` | OPEC Total Crude Oil Production Capacity | million bbl/d |
| `COPC_OPEC_R05` | OPEC Middle East Capacity | million bbl/d |
| `COPC_OPEC_ROT` | OPEC Other Capacity | million bbl/d |
| `COPS_OPEC` | OPEC Total Spare Crude Oil Production Capacity | million bbl/d |
| `COPS_OPEC_R05` | OPEC Middle East Spare Capacity | million bbl/d |
| `COPS_OPEC_ROT` | OPEC Other Spare Capacity | million bbl/d |

### OPEC Liquids (incl. NGLs and condensate)
| Series ID | Description | Units |
|-----------|-------------|-------|
| `PAPR_OPEC` | Total OPEC Petroleum Supply | million bbl/d |
| `PAPR_OPECPLUS` | Total OPEC+ Petroleum Supply | million bbl/d |
| `OPEC_NC` | OPEC non-Crude Oil Liquids Production | million bbl/d |
| `NONOPEC_NC` | Non-OPEC non-Crude Oil Liquids Production | million bbl/d |

### Supply Disruptions
| Series ID | Description | Units |
|-----------|-------------|-------|
| `PADI_OPEC` | Unplanned crude oil production disruptions, OPEC | million bbl/d |
| `PADI_NONOPEC` | Unplanned liquid fuel production disruptions, non-OPEC | million bbl/d |

### Benchmark Crude Prices
| Series ID | Description | Units |
|-----------|-------------|-------|
| `BREPUUS` | Brent crude oil spot price | $/barrel |
| `WTIPUUS` | West Texas Intermediate crude oil price | $/barrel |
| `RAIMUUS` | Imported crude oil price (avg) | $/barrel |

---

## OPEC Member Countries

Current OPEC members (13) and their EIA International `countryRegionId` codes:

| Country | Code | Region |
|---------|------|--------|
| Algeria | DZA | Africa |
| Congo (Brazzaville) | COG | Africa |
| Equatorial Guinea | GNQ | Africa |
| Gabon | GAB | Africa |
| Iran | IRN | Middle East |
| Iraq | IRQ | Middle East |
| Kuwait | KWT | Middle East |
| Libya | LBY | Africa |
| Nigeria | NGA | Africa |
| Saudi Arabia | SAU | Middle East |
| UAE | ARE | Middle East |
| Venezuela | VEN | South America |

OPEC+ non-OPEC participants include Russia (RUS), Kazakhstan (KAZ), Mexico (MEX),
Oman (OMN), Azerbaijan (AZE), Malaysia (MYS), Bahrain (BHR), Brunei (BRN),
Sudan (SDN), South Sudan (SSD).

---

## Workflow

### Step 1 -- Resolve Intent

Map the user's question to the appropriate dataset:

| User Intent | Dataset | Series / Facets |
|-------------|---------|-----------------|
| OPEC total production | STEO | `COPR_OPEC` |
| OPEC+ total production | STEO | `COPR_OPECPLUS` |
| OPEC spare capacity | STEO | `COPS_OPEC` |
| Brent/WTI price | STEO | `BREPUUS` / `WTIPUUS` |
| Specific country production | International | `countryRegionId` + `productId=57` |
| OPEC supply disruptions | STEO | `PADI_OPEC` |
| OPEC vs non-OPEC | STEO | `COPR_OPEC` + `COPR_NONOPEC` |

### Step 2 -- Fetch Data

Build the URL with appropriate filters. Default behavior:
- Use `frequency=monthly` unless user asks for annual
- Sort by `period desc` to get most recent first
- Request 24 months of data by default
- STEO includes forecast data (future months) -- note which values are forecasts

### Step 3 -- Parse Response

Response structure:
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
  }
}
```

### Step 4 -- Produce Output

**Format: Raw Data Table + Narrative**

Present a markdown table of the most relevant rows (cap at ~20 rows), then a
narrative summary covering:

1. **Current state** -- most recent actual value(s) and date
2. **Trend** -- direction and magnitude over the time window (use delta in mbd)
3. **Capacity and spare** -- if relevant, show how much headroom OPEC has
4. **OPEC+ context** -- note quota compliance if discussing production levels
5. **Forecast** -- clearly label EIA forecast values vs historical actuals
6. **Units and caveats** -- always state units; note STEO forecast uncertainty

**Example output structure:**
```
## OPEC Crude Oil Production (Monthly, 2023-2025)

| Period  | Production (million bbl/d) | Type     |
|---------|---------------------------|----------|
| 2025-06 | 28.10                     | Forecast |
| 2025-05 | 27.95                     | Forecast |
| 2025-01 | 27.12                     | Actual   |
| 2024-12 | 27.05                     | Actual   |
| ...     | ...                       | ...      |

**Summary:** OPEC produced 27.12 million bbl/d in January 2025, down 0.3 mbd
from the prior year. EIA forecasts a recovery to 28.1 mbd by mid-2025 as
voluntary cuts are gradually unwound. Spare capacity stands at 4.2 mbd (Jan 2025),
concentrated in Saudi Arabia and the UAE. Data: EIA Short-Term Energy Outlook.
```

---

## Error Handling

| HTTP Code | Meaning | Action |
|-----------|---------|--------|
| 400 | Bad parameter | Check seriesId or facet values; fix and retry |
| 403 | Invalid API key | Prompt user to verify EIA key |
| 404 | Route not found | Verify base URL path |
| 200 + empty data | No matching series | List available OPEC series and ask user to clarify |
| 200 + warning | Row cap hit | Paginate or narrow date range |

---

## Caveats and Data Limitations

- **No direct OPEC API:** All OPEC web properties (opec.org, asb.opec.org,
  momr.opec.org) are behind Cloudflare challenges. This skill uses EIA as a
  high-quality secondary source for OPEC data.
- **OPEC basket price:** The OPEC Reference Basket price is not available in EIA.
  Use Brent (`BREPUUS`) as the closest proxy. The actual OPEC basket tracks a
  weighted average of member crude grades.
- **Quota compliance:** EIA does not publish OPEC quota targets or compliance
  ratios. Production data can be compared against publicly announced targets.
- **Forecast vs actual:** STEO data includes EIA forecasts for future months.
  Always distinguish forecasts from actuals. Forecasts are updated monthly.
- **Revisions:** Recent months (1-2 most recent) may be revised.
- **Country-level lag:** EIA International annual data may lag 1-2 years behind
  current. Monthly STEO aggregates are more current.

---

## Implementation Notes

- Use `curl` with `--data-urlencode` for all bracket-containing parameters
  to avoid shell escaping issues.
- STEO data is updated monthly, typically in the first week of each month.
- For multi-series comparisons (e.g., OPEC production vs spare capacity),
  make parallel requests for each series and merge on the `period` field.
- See `references/api_reference.md` for the full series catalog.
- See `references/python_example.py` for a stdlib-only client example.
