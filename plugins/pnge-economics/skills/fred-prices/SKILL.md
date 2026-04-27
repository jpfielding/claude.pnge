---
name: fred-prices
description: >
  Query commodity prices and economic time series from the Federal Reserve
  Economic Data (FRED) API. Use this skill whenever the user asks about crude
  oil prices, WTI or Brent spot prices, Henry Hub natural gas prices, gasoline
  prices, producer price indices for petroleum or natural gas, lithium pricing
  trends, or any economic indicator relevant to energy commodity markets and
  oilfield economics. Trigger for phrases like "what is the current oil price",
  "WTI crude trend", "Brent vs WTI spread", "Henry Hub gas price", "gasoline
  price history", "PPI crude petroleum", "lithium carbonate price", "commodity
  price forecast inputs", "energy price data for feasibility study", or any
  request for FRED economic time series. Produces trend summaries and raw data
  tables with narrative analysis for petroleum engineering economic evaluation.
---

# FRED Prices Skill

Fetches and analyzes commodity prices and economic time series from the
Federal Reserve Economic Data (FRED) API maintained by the Federal Reserve
Bank of St. Louis.

## API Key Handling

Resolution order (stop at first success):

1. **`~/.config/fred/credentials`** (default) -- parse `api_key=<value>` from this file
2. **`FRED_API_KEY` env var** -- fallback if credentials file is absent
3. **User-provided in conversation** -- fallback if neither above is set
4. **Prompt the user** -- "Please provide your FRED API key. You can get one free at https://fred.stlouisfed.org/docs/api/api_key.html -- or store it in `~/.config/fred/credentials` as `api_key=YOUR_KEY` (chmod 600)."

Never hardcode or log the key. Pass it as a query parameter `&api_key=<KEY>`.

**Reading the credentials file (bash):**
```bash
KEY=$(grep '^api_key=' ~/.config/fred/credentials 2>/dev/null | cut -d= -f2)
[ -z "$KEY" ] && KEY="${FRED_API_KEY}"
if [ -z "$KEY" ]; then
    echo "No FRED API key found. Get one free at https://fred.stlouisfed.org/docs/api/api_key.html"
    echo "Store in ~/.config/fred/credentials as api_key=YOUR_KEY"
    exit 1
fi
```

**Reading the credentials file (Go):**
```go
func resolveAPIKey() (string, error) {
    home, _ := os.UserHomeDir()
    creds := filepath.Join(home, ".config", "fred", "credentials")
    if data, err := os.ReadFile(creds); err == nil {
        for _, line := range strings.Split(string(data), "\n") {
            line = strings.TrimSpace(line)
            if strings.HasPrefix(line, "api_key=") {
                return strings.TrimPrefix(line, "api_key="), nil
            }
        }
    }
    if key := os.Getenv("FRED_API_KEY"); key != "" {
        return key, nil
    }
    return "", fmt.Errorf("no FRED API key found; store in ~/.config/fred/credentials as api_key=YOUR_KEY")
}
```

---

## API Structure

**Base URL:** `https://api.stlouisfed.org/fred/`

FRED is a flat API organized around series IDs rather than a hierarchical tree.
The primary endpoints are:

| Endpoint | Purpose |
|----------|---------|
| `fred/series` | Get metadata for a single series |
| `fred/series/observations` | Get data points for a series |
| `fred/series/search` | Search for series by keyword |
| `fred/series/categories` | Get categories a series belongs to |
| `fred/category/series` | List series in a category |
| `fred/releases` | List data releases |
| `fred/release/series` | List series in a release |

**Common parameters for all endpoints:**

| Parameter | Example | Notes |
|-----------|---------|-------|
| `api_key` | `api_key=YOUR_KEY` | Required on every request |
| `file_type` | `file_type=json` | Always use `json` (default is XML) |

**Parameters for `series/observations`:**

| Parameter | Example | Notes |
|-----------|---------|-------|
| `series_id` | `series_id=DCOILWTICO` | Required -- the FRED series ID |
| `observation_start` | `observation_start=2024-01-01` | YYYY-MM-DD format |
| `observation_end` | `observation_end=2024-12-31` | YYYY-MM-DD format |
| `frequency` | `frequency=m` | Aggregation: d, w, bw, m, q, sa, a |
| `aggregation_method` | `aggregation_method=avg` | avg, sum, eop (end of period) |
| `units` | `units=chg` | lin, chg, ch1, pch, pc1, pca, cch, cca, log |
| `sort_order` | `sort_order=desc` | asc (default) or desc |
| `limit` | `limit=100` | Max 100000, default 100000 |
| `offset` | `offset=0` | Pagination start |

**Parameters for `series/search`:**

| Parameter | Example | Notes |
|-----------|---------|-------|
| `search_text` | `search_text=lithium+price` | Keyword search |
| `search_type` | `search_type=full_text` | full_text or series_id |
| `order_by` | `order_by=popularity` | popularity, search_rank, series_id, title, etc. |
| `limit` | `limit=20` | Max 1000, default 1000 |

---

## Key Series for Petroleum and Energy Economics

### Crude Oil

| Series ID | Title | Frequency | Units |
|-----------|-------|-----------|-------|
| `DCOILWTICO` | WTI Crude Oil Spot Price | Daily | $/bbl |
| `DCOILBRENTEU` | Brent Crude Oil Spot Price (Europe) | Daily | $/bbl |
| `MCOILWTICO` | WTI Crude Oil Monthly Average | Monthly | $/bbl |
| `MCOILBRENTEU` | Brent Crude Oil Monthly Average | Monthly | $/bbl |
| `PCU211111211111` | PPI: Crude Petroleum | Monthly | Index |

### Natural Gas

| Series ID | Title | Frequency | Units |
|-----------|-------|-----------|-------|
| `DHHNGSP` | Henry Hub Natural Gas Spot Price | Daily | $/MMBtu |
| `MHHNGSP` | Henry Hub Natural Gas Monthly Average | Monthly | $/MMBtu |
| `WPU0573` | PPI: Natural Gas | Monthly | Index |

### Gasoline and Refined Products

| Series ID | Title | Frequency | Units |
|-----------|-------|-----------|-------|
| `GASREGW` | US Regular Gasoline Weekly Price | Weekly | $/gal |
| `GASREGCOVW` | US Regular Gasoline Conventional Weekly | Weekly | $/gal |
| `GASDIESELW` | US Diesel Weekly Price | Weekly | $/gal |

### Macro Indicators Relevant to PNGE

| Series ID | Title | Frequency | Units |
|-----------|-------|-----------|-------|
| `CPIAUCSL` | CPI (All Urban Consumers) | Monthly | Index |
| `DFF` | Federal Funds Effective Rate | Daily | % |
| `DEXUSEU` | USD/EUR Exchange Rate | Daily | $/EUR |
| `DEXCHUS` | CNY/USD Exchange Rate | Daily | CNY/$ |

### Lithium and Critical Minerals

FRED does not carry a dedicated lithium carbonate spot price series.
Use `series/search` to check for new additions:
```bash
curl -s "https://api.stlouisfed.org/fred/series/search?search_text=lithium&api_key=KEY&file_type=json&limit=10"
```

For lithium pricing, the USGS Mineral Commodity Summaries and Fastmarkets/Benchmark
Minerals are the authoritative sources. FRED may index derived series or PPI
sub-indices that correlate. Search with keywords: `lithium`, `critical mineral`,
`battery material`.

---

## Workflow

### Step 1 -- Resolve Intent

Map the user's question to one or more FRED series IDs. Common mappings:

| User says | Series ID(s) |
|-----------|-------------|
| "oil price" / "crude price" / "WTI" | `DCOILWTICO` (daily) or `MCOILWTICO` (monthly) |
| "Brent crude" | `DCOILBRENTEU` or `MCOILBRENTEU` |
| "WTI vs Brent" / "crude spread" | Both `DCOILWTICO` + `DCOILBRENTEU` |
| "gas price" / "natural gas" / "Henry Hub" | `DHHNGSP` or `MHHNGSP` |
| "gasoline price" | `GASREGW` |
| "diesel price" | `GASDIESELW` |
| "crude PPI" / "petroleum index" | `PCU211111211111` |
| "natural gas PPI" | `WPU0573` |
| "lithium price" | Search first, then explain FRED coverage gaps |

If the user mentions a series by name but not ID, use `series/search` to find
the best match.

### Step 2 -- Fetch Series Metadata (when needed)

```bash
curl -s "https://api.stlouisfed.org/fred/series?series_id=DCOILWTICO&api_key=$KEY&file_type=json" \
  | jq '.seriess[0] | {id, title, frequency_short, units_short, observation_start, observation_end, last_updated}'
```

Returns: title, frequency, units, date range, last update timestamp.
Use this to confirm the series exists and to report units correctly.

### Step 3 -- Fetch Observations

Build the URL with appropriate date range. Default behavior:
- Use the series' native frequency unless the user requests aggregation
- Default time window: last 12 months for daily series, last 5 years for monthly
- Sort ascending (chronological) for trend analysis
- Request up to 10000 observations; paginate if needed

```bash
curl -s "https://api.stlouisfed.org/fred/series/observations?\
series_id=DCOILWTICO&\
api_key=$KEY&\
file_type=json&\
observation_start=2024-01-01&\
observation_end=2024-12-31&\
sort_order=desc&\
limit=20"
```

### Step 4 -- Parse Response

Response structure for observations:
```json
{
  "realtime_start": "2024-01-01",
  "realtime_end": "2024-12-31",
  "observation_start": "2024-01-01",
  "observation_end": "2024-12-31",
  "units": "Dollars per Barrel",
  "output_type": 1,
  "file_type": "json",
  "order_by": "observation_date",
  "sort_order": "desc",
  "count": 250,
  "offset": 0,
  "limit": 20,
  "observations": [
    {
      "realtime_start": "2024-12-31",
      "realtime_end": "2024-12-31",
      "date": "2024-12-30",
      "value": "71.23"
    }
  ]
}
```

**Important:** Values are returned as strings, including the special value `"."` for
missing/unreported observations. Always filter out `"."` before numeric analysis.

Check `count` vs `limit` -- if `count > limit`, paginate using `offset`.

### Step 5 -- Produce Output

**Format: Raw Data Table + Narrative**

Present a markdown table of the most relevant data points (cap at ~20 rows for
readability), then a narrative summary covering:

1. **Current state** -- most recent value(s) and date
2. **Trend** -- direction and magnitude over the time window (use % change)
3. **Notable features** -- peaks, troughs, inflection points
4. **Spread analysis** -- when comparing two series (e.g., WTI vs Brent)
5. **Units and caveats** -- always state units; note reporting delays
6. **PNGE context** -- relate to oilfield economics where relevant (e.g., breakeven
   prices, DLE feasibility thresholds, operating cost impacts)

**Example output structure:**
```
## WTI Crude Oil Spot Price (Daily, Jan-Dec 2024)

| Date       | Price ($/bbl) |
|------------|---------------|
| 2024-12-30 | 71.23         |
| 2024-12-27 | 70.60         |
| ...        | ...           |

**Summary:** WTI crude averaged $77.54/bbl in 2024, closing at $71.23 on
December 30 -- down 5.2% year-over-year. Prices peaked at $86.91 in April
driven by OPEC+ production cuts, then declined through Q4 on demand
concerns. The current price sits above the $60-65/bbl breakeven for most
Permian Basin operators but below the $80/bbl threshold where Appalachian
Basin produced water volumes typically increase (more drilling activity =
more produced water for potential Li recovery).

*Source: Federal Reserve Bank of St. Louis (FRED), series DCOILWTICO.
Values may lag 1-2 business days from actual trading.*
```

---

## Multi-Series Comparison

When the user asks to compare series (e.g., WTI vs Brent, oil vs gas):

1. Fetch both series for the same date range
2. Align on common dates (daily series may have different trading holidays)
3. Present side-by-side in one table
4. Calculate the spread (difference) where meaningful
5. Note correlation and divergence periods

```bash
# Fetch WTI
curl -s "https://api.stlouisfed.org/fred/series/observations?series_id=DCOILWTICO&api_key=$KEY&file_type=json&observation_start=2024-01-01&limit=20&sort_order=desc"

# Fetch Brent
curl -s "https://api.stlouisfed.org/fred/series/observations?series_id=DCOILBRENTEU&api_key=$KEY&file_type=json&observation_start=2024-01-01&limit=20&sort_order=desc"
```

---

## Series Search

When the user asks about a topic and no known series ID matches:

```bash
curl -s "https://api.stlouisfed.org/fred/series/search?\
search_text=lithium+price&\
api_key=$KEY&\
file_type=json&\
order_by=popularity&\
limit=10" | jq '.seriess[] | {id, title, frequency_short, units_short, popularity}'
```

Report what FRED has available. If FRED lacks the series (common for niche
commodities like lithium), suggest alternatives:
- USGS Mineral Commodity Summaries (via `usgs-minerals` skill)
- EIA data (via `eia-data` skill)
- Fastmarkets / Benchmark Minerals Intelligence (subscription services)

---

## Frequency Aggregation

FRED can aggregate higher-frequency data to lower frequencies on the fly:

| `frequency` | Meaning |
|-------------|---------|
| `d` | Daily (native for spot prices) |
| `w` | Weekly |
| `bw` | Biweekly |
| `m` | Monthly |
| `q` | Quarterly |
| `sa` | Semiannual |
| `a` | Annual |

**Aggregation methods (`aggregation_method`):**

| Value | Meaning | Use case |
|-------|---------|----------|
| `avg` | Average of observations in period | Default, good for prices |
| `sum` | Sum | Production volumes |
| `eop` | End of period | Closing price snapshots |

**Units transformation (`units`):**

| Value | Meaning | Use case |
|-------|---------|----------|
| `lin` | Levels (no transform) | Default, raw values |
| `chg` | Change from prior period | Period-over-period delta |
| `pch` | Percent change from prior period | Trend analysis |
| `pc1` | Percent change from year ago | Year-over-year comparison |
| `pca` | Compounded annual rate of change | Annualized trends |
| `log` | Natural log | Econometric modeling |

---

## Pagination

If `count > limit`, paginate:
```bash
# Page 1
curl -s "...&limit=10000&offset=0"

# Page 2
curl -s "...&limit=10000&offset=10000"
```

Default limit is 100000 which covers most single-series requests. For very long
daily series (e.g., DCOILWTICO has 10000+ observations), narrow the date range
or aggregate to monthly.

---

## Error Handling

| HTTP Code | Meaning | Action |
|-----------|---------|--------|
| 400 | Bad request (invalid series ID, bad date format) | Check series ID; verify YYYY-MM-DD dates |
| 403 | Invalid or missing API key | Prompt user to verify key |
| 429 | Rate limit exceeded (120 requests/minute) | Wait 60 seconds and retry |
| 500 | FRED server error | Retry after brief delay |
| 200 + `"error_code"` in JSON | API-level error | Read `error_message` field and report |

**Common API-level errors:**
- `"bad_request"` with `"The series does not exist"` -- invalid series_id
- `"bad_request"` with `"Bad value for parameter"` -- check date format or frequency code

---

## Rate Limits

FRED allows 120 requests per minute per API key. For batch operations
(fetching many series), add a brief delay between calls:

```bash
for sid in DCOILWTICO DCOILBRENTEU DHHNGSP GASREGW; do
    curl -s "https://api.stlouisfed.org/fred/series/observations?series_id=$sid&api_key=$KEY&file_type=json&observation_start=2024-01-01&limit=5"
    sleep 0.5
done
```

---

## PNGE Context and Relevance

### Oil Price and Produced Water Economics

Crude oil prices directly affect:
- **Drilling activity** -- higher prices = more wells drilled = more produced water
- **Produced water volumes** -- Appalachian Basin produced water peaks when WTI
  is above ~$70-80/bbl (drilling incentive threshold)
- **DLE feasibility** -- lithium extraction from brines becomes more attractive when
  operators are already handling large produced water volumes
- **Disposal costs** -- Class II injection well disposal costs correlate with
  produced water volumes, creating incentive for value-added treatment

### Natural Gas Price Context

Henry Hub gas prices affect:
- Marcellus/Utica drilling economics (primary gas plays with Li-bearing brines)
- Energy costs for DLE processing (thermal and electrical)
- Produced water chemistry (gas wells vs oil wells have different brine profiles)

### Using FRED Data in Feasibility Studies

For Li/Mg recovery economic analysis:
1. Fetch WTI and Henry Hub price histories to establish commodity price scenarios
2. Use PPI indices for cost escalation factors
3. Use exchange rates for international market comparisons (Li is priced globally)
4. Cross-reference with EIA production data for volume projections

---

## Caveats and Data Quality

- **Reporting lag:** Daily spot prices lag 1-2 business days. Monthly series
  lag 2-4 weeks after period end.
- **Missing values:** The string `"."` indicates no observation for that date
  (weekends, holidays, reporting gaps). Always filter these out.
- **Revisions:** Some series (especially PPI) are subject to revision. The
  `realtime_start`/`realtime_end` fields track vintage. Default requests
  return the latest revision.
- **FRED vs primary source:** FRED aggregates data from other agencies (EIA, BLS,
  Census). For authoritative values, check the primary source. FRED series metadata
  includes the source agency.
- **Lithium coverage gap:** FRED does not carry a dedicated lithium spot price
  series as of early 2026. Lithium carbonate and hydroxide prices are primarily
  tracked by private data providers (Fastmarkets, Benchmark Minerals, S&P Global).

---

## Implementation Notes

- **Prefer `bash_tool`** with `curl` + `jq` for API calls in Claude's environment
- **Python client** -- see `references/python_example.py` (stdlib-only, no dependencies)
- **API reference** -- see `references/api_reference.md` for full endpoint documentation
- Response values are always strings -- parse to float, filtering `"."` as missing
- FRED updates: daily series by ~6pm ET same day, monthly indices ~2 weeks after month end
- The `file_type=json` parameter is required on every request (default is XML)
- Series IDs are case-sensitive -- always use uppercase
