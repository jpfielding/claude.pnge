# FRED API Reference

Full documentation: https://fred.stlouisfed.org/docs/api/fred/

Base URL: `https://api.stlouisfed.org/fred/`

All requests require `api_key` and should include `file_type=json`.

---

## Endpoints

### fred/series

Get metadata for a single series.

```
GET /fred/series?series_id=DCOILWTICO&api_key=KEY&file_type=json
```

**Response:**
```json
{
  "seriess": [
    {
      "id": "DCOILWTICO",
      "realtime_start": "2024-01-01",
      "realtime_end": "2024-12-31",
      "title": "Crude Oil Prices: West Texas Intermediate (WTI) - Cushing, Oklahoma",
      "observation_start": "1986-01-02",
      "observation_end": "2024-12-30",
      "frequency": "Daily",
      "frequency_short": "D",
      "units": "Dollars per Barrel",
      "units_short": "$ per Barrel",
      "seasonal_adjustment": "Not Seasonally Adjusted",
      "seasonal_adjustment_short": "NSA",
      "last_updated": "2024-12-31 15:01:06-06",
      "popularity": 95,
      "notes": "Definitions, sources, and explanatory notes..."
    }
  ]
}
```

---

### fred/series/observations

Get data points for a series.

```
GET /fred/series/observations?series_id=DCOILWTICO&api_key=KEY&file_type=json
    &observation_start=2024-01-01
    &observation_end=2024-12-31
    &sort_order=desc
    &limit=20
```

**Parameters:**

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `series_id` | Yes | -- | FRED series identifier |
| `api_key` | Yes | -- | Your FRED API key |
| `file_type` | No | `xml` | Always use `json` |
| `observation_start` | No | `1776-07-04` | Start date (YYYY-MM-DD) |
| `observation_end` | No | `9999-12-31` | End date (YYYY-MM-DD) |
| `frequency` | No | native | Aggregation frequency (see below) |
| `aggregation_method` | No | `avg` | How to aggregate: avg, sum, eop |
| `units` | No | `lin` | Unit transform: lin, chg, ch1, pch, pc1, pca, cch, cca, log |
| `sort_order` | No | `asc` | Sort: asc or desc |
| `limit` | No | `100000` | Max observations to return (max 100000) |
| `offset` | No | `0` | Pagination offset |
| `realtime_start` | No | today | For vintage/revision tracking |
| `realtime_end` | No | today | For vintage/revision tracking |
| `output_type` | No | `1` | 1=realtime, 2=vintage dates, 3=initial release, 4=all vintages |

**Frequency codes:**

| Code | Period |
|------|--------|
| `d` | Daily |
| `w` | Weekly (Friday) |
| `bw` | Biweekly |
| `m` | Monthly |
| `q` | Quarterly |
| `sa` | Semiannual |
| `a` | Annual |
| `wef` | Weekly (ending Friday) |
| `weth` | Weekly (ending Thursday) |
| `wew` | Weekly (ending Wednesday) |
| `wetu` | Weekly (ending Tuesday) |
| `wem` | Weekly (ending Monday) |
| `wesu` | Weekly (ending Sunday) |
| `wesa` | Weekly (ending Saturday) |

**Units transformation codes:**

| Code | Name | Formula |
|------|------|---------|
| `lin` | Levels | No transform |
| `chg` | Change | x(t) - x(t-1) |
| `ch1` | Change from year ago | x(t) - x(t-n) |
| `pch` | Percent change | ((x(t)/x(t-1)) - 1) * 100 |
| `pc1` | Percent change from year ago | ((x(t)/x(t-n)) - 1) * 100 |
| `pca` | Compounded annual rate of change | ((x(t)/x(t-1))^(n) - 1) * 100 |
| `cch` | Continuously compounded rate of change | (ln(x(t)/x(t-1))) * 100 |
| `cca` | Continuously compounded annual rate | (ln(x(t)/x(t-1)) * n) * 100 |
| `log` | Natural log | ln(x(t)) |

**Response:**
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

**Note:** The `value` field is always a string. The special value `"."` indicates
a missing observation (weekend, holiday, or unreported). Always filter these out
before numeric computation.

---

### fred/series/search

Search for series by keyword.

```
GET /fred/series/search?search_text=crude+oil+price&api_key=KEY&file_type=json
    &order_by=popularity
    &limit=10
```

**Parameters:**

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `search_text` | Yes | -- | Keywords (space or + separated) |
| `api_key` | Yes | -- | Your FRED API key |
| `file_type` | No | `xml` | Use `json` |
| `search_type` | No | `full_text` | `full_text` or `series_id` |
| `order_by` | No | `search_rank` | search_rank, series_id, title, units, frequency, seasonal_adjustment, realtime_start, realtime_end, last_updated, observation_start, observation_end, popularity, group_popularity |
| `sort_order` | No | `asc` | asc or desc (desc for popularity) |
| `limit` | No | `1000` | Max results (max 1000) |
| `offset` | No | `0` | Pagination offset |
| `filter_variable` | No | -- | Filter field: frequency, units, seasonal_adjustment |
| `filter_value` | No | -- | Filter value (e.g., frequency=Monthly) |
| `tag_names` | No | -- | Semicolon-delimited tag list |

**Response:**
```json
{
  "realtime_start": "...",
  "realtime_end": "...",
  "order_by": "popularity",
  "sort_order": "desc",
  "count": 142,
  "offset": 0,
  "limit": 10,
  "seriess": [
    {
      "id": "DCOILWTICO",
      "title": "Crude Oil Prices: West Texas Intermediate (WTI) - Cushing, Oklahoma",
      "frequency_short": "D",
      "units_short": "$ per Barrel",
      "seasonal_adjustment_short": "NSA",
      "popularity": 95,
      "observation_start": "1986-01-02",
      "observation_end": "2024-12-30",
      "last_updated": "2024-12-31 15:01:06-06",
      "notes": "..."
    }
  ]
}
```

---

### fred/series/categories

Get categories a series belongs to.

```
GET /fred/series/categories?series_id=DCOILWTICO&api_key=KEY&file_type=json
```

---

### fred/category/series

List all series in a category.

```
GET /fred/category/series?category_id=32217&api_key=KEY&file_type=json&limit=20
```

**Useful category IDs for PNGE:**

| Category ID | Name |
|-------------|------|
| `32217` | Spot Prices (Petroleum) |
| `32215` | Prices (Petroleum & Other Liquids) |
| `32208` | Petroleum & Other Liquids |
| `32267` | Prices (Natural Gas) |
| `32263` | Natural Gas |
| `32413` | Producer Price Indexes |

---

### fred/releases

List all FRED data releases.

```
GET /fred/releases?api_key=KEY&file_type=json&limit=20
```

### fred/release/series

List series in a specific release.

```
GET /fred/release/series?release_id=10&api_key=KEY&file_type=json&limit=20
```

**Useful release IDs:**

| Release ID | Name |
|------------|------|
| `10` | U.S. Energy Information Administration (EIA) |
| `46` | Producer Price Index |
| `51` | U.S. Import and Export Prices |

---

## Complete Series Reference for PNGE

### Crude Oil Series

| Series ID | Title | Freq | Units | Source |
|-----------|-------|------|-------|--------|
| `DCOILWTICO` | WTI Cushing Spot Price | D | $/bbl | EIA |
| `DCOILBRENTEU` | Brent Europe Spot Price | D | $/bbl | EIA |
| `MCOILWTICO` | WTI Monthly Average | M | $/bbl | EIA |
| `MCOILBRENTEU` | Brent Monthly Average | M | $/bbl | EIA |
| `WCOILWTICO` | WTI Weekly Average | W | $/bbl | EIA |
| `WCOILBRENTEU` | Brent Weekly Average | W | $/bbl | EIA |
| `PCU211111211111` | PPI: Crude Petroleum | M | Index 1982=100 | BLS |
| `POILWTIUSDM` | WTI Price (IMF) | M | $/bbl | IMF |
| `POILBREUSDM` | Brent Price (IMF) | M | $/bbl | IMF |

### Natural Gas Series

| Series ID | Title | Freq | Units | Source |
|-----------|-------|------|-------|--------|
| `DHHNGSP` | Henry Hub Natural Gas Spot Price | D | $/MMBtu | EIA |
| `MHHNGSP` | Henry Hub Monthly Average | M | $/MMBtu | EIA |
| `WPU0573` | PPI: Natural Gas | M | Index 1982=100 | BLS |

### Gasoline and Diesel Series

| Series ID | Title | Freq | Units | Source |
|-----------|-------|------|-------|--------|
| `GASREGW` | US Regular Gasoline, All Areas | W | $/gal | EIA |
| `GASREGCOVW` | US Regular Gasoline, Conventional | W | $/gal | EIA |
| `GASDIESELW` | US No. 2 Diesel Retail | W | $/gal | EIA |

### Macro/Exchange Rate Series

| Series ID | Title | Freq | Units | Source |
|-----------|-------|------|-------|--------|
| `CPIAUCSL` | Consumer Price Index (All Urban) | M | Index 1982-84=100 | BLS |
| `DFF` | Federal Funds Effective Rate | D | % | Fed |
| `DEXUSEU` | USD/EUR Exchange Rate | D | $/EUR | Fed |
| `DEXCHUS` | China Yuan/USD Exchange Rate | D | CNY/$ | Fed |
| `DTWEXBGS` | Trade Weighted USD Index (Broad) | D | Index Jan 2006=100 | Fed |

---

## Practical Examples

### Example 1: WTI last 10 trading days
```bash
KEY=$(grep '^api_key=' ~/.config/fred/credentials 2>/dev/null | cut -d= -f2)
[ -z "$KEY" ] && KEY="${FRED_API_KEY}"

curl -s "https://api.stlouisfed.org/fred/series/observations?\
series_id=DCOILWTICO&\
api_key=$KEY&\
file_type=json&\
sort_order=desc&\
limit=10" | jq -r '.observations[] | select(.value != ".") | "\(.date)\t\(.value)"'
```

### Example 2: WTI monthly average for 2024
```bash
curl -s "https://api.stlouisfed.org/fred/series/observations?\
series_id=DCOILWTICO&\
api_key=$KEY&\
file_type=json&\
frequency=m&\
aggregation_method=avg&\
observation_start=2024-01-01&\
observation_end=2024-12-31" | jq -r '.observations[] | "\(.date)\t\(.value)"'
```

### Example 3: WTI year-over-year percent change (monthly)
```bash
curl -s "https://api.stlouisfed.org/fred/series/observations?\
series_id=MCOILWTICO&\
api_key=$KEY&\
file_type=json&\
units=pc1&\
observation_start=2020-01-01" | jq -r '.observations[] | select(.value != ".") | "\(.date)\t\(.value)%"'
```

### Example 4: Search for lithium-related series
```bash
curl -s "https://api.stlouisfed.org/fred/series/search?\
search_text=lithium&\
api_key=$KEY&\
file_type=json&\
order_by=popularity&\
sort_order=desc&\
limit=10" | jq '.seriess[] | {id, title, frequency_short, units_short, popularity}'
```

### Example 5: Compare WTI and Henry Hub (last 5 observations)
```bash
echo "=== WTI Crude Oil ==="
curl -s "https://api.stlouisfed.org/fred/series/observations?\
series_id=DCOILWTICO&api_key=$KEY&file_type=json&sort_order=desc&limit=5" \
  | jq -r '.observations[] | select(.value != ".") | "\(.date)  $\(.value)/bbl"'

echo ""
echo "=== Henry Hub Natural Gas ==="
curl -s "https://api.stlouisfed.org/fred/series/observations?\
series_id=DHHNGSP&api_key=$KEY&file_type=json&sort_order=desc&limit=5" \
  | jq -r '.observations[] | select(.value != ".") | "\(.date)  $\(.value)/MMBtu"'
```

---

## Error Response Format

```json
{
  "error_code": 400,
  "error_message": "Bad Request. The series_id value 'INVALID' is not a valid series identifier."
}
```

Error codes in the JSON body may differ from the HTTP status code. Always check
for the `error_code` field in the response.
