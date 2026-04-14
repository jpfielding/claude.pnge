---
name: bls-data
description: >
  Query labor statistics, price indices, and employment data from the Bureau
  of Labor Statistics (BLS) Public Data API v2. Use this skill whenever the
  user asks about producer price index for oil and gas extraction, CPI energy
  component, employment in mining or petroleum, average wages in oil and gas,
  occupational employment statistics for petroleum engineers, workplace injury
  rates in drilling, or any U.S. labor and price index data relevant to energy
  economics. Trigger for phrases like "PPI for oil and gas", "CPI energy
  prices", "mining employment trends", "petroleum engineer salary data",
  "drilling industry wages", "workplace injuries in oil and gas",
  "occupational employment in extraction", "labor cost trends for oilfield
  services", "producer price index crude petroleum", "consumer price index
  gasoline", "inflation adjustment for energy costs", "cost escalation
  factors for feasibility study", or any request for BLS economic series.
  Produces time series tables and narrative analysis with economic context.
---

# BLS Data Skill

Fetches and analyzes U.S. labor statistics, price indices, and employment
data from the Bureau of Labor Statistics (BLS) Public Data API v2. Covers
Producer Price Index (PPI), Consumer Price Index (CPI), employment by
industry, wages, occupational statistics, and workplace safety data.

## API Key Handling

An API key is optional but recommended. Without a key, requests are limited
to 25 per day and 10 years of data. With a free key, limits increase to
500 requests per day and 20 years of data.

Resolution order (stop at first success):

1. **`~/.config/bls/credentials`** -- parse `api_key=<value>` from this file
2. **`BLS_API_KEY` env var** -- fallback if credentials file is absent
3. **No key (unregistered)** -- still works with stricter rate limits
4. **Prompt the user** -- "For higher rate limits, register for a free BLS
   API key at https://data.bls.gov/registrationEngine/ -- store in
   `~/.config/bls/credentials` as `api_key=YOUR_KEY` (chmod 600)."

Never hardcode or log the key. Pass it in the JSON request body as
`registrationkey`.

**Reading the credentials file (bash):**
```bash
KEY=$(grep '^api_key=' ~/.config/bls/credentials 2>/dev/null | cut -d= -f2)
[ -z "$KEY" ] && KEY="${BLS_API_KEY}"
# KEY may be empty -- unregistered requests still work with lower limits
```

**Reading the credentials file (Go):**
```go
func resolveAPIKey() string {
    home, _ := os.UserHomeDir()
    creds := filepath.Join(home, ".config", "bls", "credentials")
    if data, err := os.ReadFile(creds); err == nil {
        for _, line := range strings.Split(string(data), "\n") {
            line = strings.TrimSpace(line)
            if strings.HasPrefix(line, "api_key=") {
                return strings.TrimPrefix(line, "api_key=")
            }
        }
    }
    if key := os.Getenv("BLS_API_KEY"); key != "" {
        return key
    }
    return "" // Empty string = unregistered; API still works
}
```

---

## API Structure

**Base URL:** `https://api.bls.gov/publicAPI/v2/timeseries/data/`

The BLS API v2 uses **POST requests** with a JSON body. This is different
from most government APIs that use GET with query parameters.

**Request format:**
```bash
curl -s -X POST "https://api.bls.gov/publicAPI/v2/timeseries/data/" \
  -H "Content-Type: application/json" \
  -d '{
    "seriesid": ["PCU211111211111"],
    "startyear": "2020",
    "endyear": "2025",
    "registrationkey": "YOUR_KEY",
    "calculations": true,
    "annualaverage": true
  }'
```

**Request body parameters:**

| Parameter | Type | Notes |
|-----------|------|-------|
| `seriesid` | array of strings | Required. Up to 50 series per request (v2 with key), 25 without key |
| `startyear` | string | Required. Four-digit year |
| `endyear` | string | Required. Four-digit year. Max span: 20 years (v2), 10 years (v1) |
| `registrationkey` | string | Optional. Your API key for higher limits |
| `calculations` | boolean | Include net/percent changes (only with key) |
| `annualaverage` | boolean | Include annual average values (only with key) |
| `aspects` | boolean | Include footnotes and aspect data (only with key) |

**Rate limits:**

| Feature | Unregistered (v2) | Registered (v2) |
|---------|-------------------|-----------------|
| Daily requests | 25 | 500 |
| Series per request | 25 | 50 |
| Years per request | 10 | 20 |
| Calculations | No | Yes |
| Annual averages | No | Yes |

---

## Key Series for Petroleum Engineering

### Producer Price Index (PPI) -- Oil and Gas

| Series ID | Title | Frequency |
|-----------|-------|-----------|
| `PCU211111211111` | PPI: Crude Petroleum | Monthly |
| `PCU211112211112` | PPI: Natural Gas | Monthly |
| `PCU21111121111101` | PPI: Crude Petroleum, Domestic Production | Monthly |
| `PCU213111213111` | PPI: Drilling Oil and Gas Wells | Monthly |
| `PCU213112213112` | PPI: Support Activities for Oil and Gas | Monthly |
| `PCU324110324110` | PPI: Petroleum Refineries | Monthly |

**PPI series ID structure:** `PCU` + 6-digit NAICS + 6-digit product code.
NAICS 211111 = Crude Petroleum and Natural Gas Extraction.

### Consumer Price Index (CPI) -- Energy

| Series ID | Title | Frequency |
|-----------|-------|-----------|
| `CUUR0000SEHE` | CPI-U: Energy (all urban, not seasonally adjusted) | Monthly |
| `CUSR0000SEHE` | CPI-U: Energy (all urban, seasonally adjusted) | Monthly |
| `CUUR0000SEHE01` | CPI-U: Gasoline (all types) | Monthly |
| `CUUR0000SEHE02` | CPI-U: Fuel Oil and Other Fuels | Monthly |
| `CUUR0000SEHF01` | CPI-U: Electricity | Monthly |
| `CUUR0000SEHF02` | CPI-U: Utility (piped) Gas Service | Monthly |

**CPI series ID structure:** `CU` + `U`(unadjusted)/`S`(seasonal) +
`R`(revised)/`S`(current) + area code + item code.

### Employment -- Mining and Extraction

| Series ID | Title | Frequency |
|-----------|-------|-----------|
| `CES1021000001` | All Employees, Mining and Logging (thousands) | Monthly |
| `CES1021100001` | All Employees, Oil and Gas Extraction (thousands) | Monthly |
| `CES1021300001` | All Employees, Support Activities for Mining (thousands) | Monthly |
| `CES1021100011` | Average Weekly Earnings, Oil and Gas Extraction | Monthly |
| `CES1021100003` | Average Hourly Earnings, Oil and Gas Extraction | Monthly |
| `CES1021100006` | Average Weekly Hours, Oil and Gas Extraction | Monthly |

**CES series ID structure:** `CES` + supersector code + industry code +
data type code. Mining = supersector 10, Oil/Gas Extraction = 2110.

### Occupational Employment and Wages (OES/OEWS)

| Series ID | Title | Notes |
|-----------|-------|-------|
| `OEUM000000017-2171` | Petroleum Engineers, National | Annual May survey |
| `OEUM000000047-5012` | Rotary Drill Operators, Oil/Gas | Annual |
| `OEUM000000047-5013` | Service Unit Operators, Oil/Gas/Mining | Annual |
| `OEUM000000017-2011` | Chemical Engineers, National | Annual (relevant for DLE) |

**Note:** OES data is annual (May survey), published in March of the following
year. Series IDs use the format: `OEUM` + area + occupation SOC code.

### Workplace Injuries and Fatalities

| Series ID | Title | Notes |
|-----------|-------|-------|
| `IIU00X21100X0XX00X08` | Injury rate, Oil and Gas Extraction | Annual |
| `FWU00X2110000008` | Fatal injuries, Oil and Gas Extraction | Annual |

---

## Workflow

### Step 1 -- Resolve Intent

Map the user's question to one or more BLS series IDs:

| User Says | Series ID(s) |
|-----------|-------------|
| "PPI for crude oil" / "producer price petroleum" | `PCU211111211111` |
| "PPI for natural gas" | `PCU211112211112` |
| "CPI energy" / "energy inflation" | `CUUR0000SEHE` |
| "gasoline CPI" / "gas price index" | `CUUR0000SEHE01` |
| "oil and gas employment" / "oilfield jobs" | `CES1021100001` |
| "mining employment" | `CES1021000001` |
| "drilling industry wages" | `CES1021100011` |
| "petroleum engineer salary" | `OEUM000000017-2171` |
| "drilling rig injuries" / "oilfield safety" | `IIU00X21100X0XX00X08` |
| "cost escalation factor" | PPI series for the relevant industry |

If the user requests a series by topic but not ID, search the BLS series
finder at https://data.bls.gov/dataFinder/ for guidance on constructing
the series ID.

### Step 2 -- Fetch Data

Build the POST request with appropriate date range. Default behavior:
- Use the last 10 years (works without API key)
- Include `calculations: true` and `annualaverage: true` if key is available
- Request up to 5 related series in one call for comparison

```bash
KEY=$(grep '^api_key=' ~/.config/bls/credentials 2>/dev/null | cut -d= -f2)
[ -z "$KEY" ] && KEY="${BLS_API_KEY}"

# Build JSON body
if [ -n "$KEY" ]; then
    BODY='{
        "seriesid": ["PCU211111211111", "PCU211112211112"],
        "startyear": "2020",
        "endyear": "2025",
        "registrationkey": "'"$KEY"'",
        "calculations": true,
        "annualaverage": true
    }'
else
    BODY='{
        "seriesid": ["PCU211111211111", "PCU211112211112"],
        "startyear": "2020",
        "endyear": "2025"
    }'
fi

curl -s -X POST "https://api.bls.gov/publicAPI/v2/timeseries/data/" \
  -H "Content-Type: application/json" \
  -d "$BODY"
```

### Step 3 -- Parse Response

**Response structure:**
```json
{
  "status": "REQUEST_SUCCEEDED",
  "responseTime": 128,
  "message": [],
  "Results": {
    "series": [
      {
        "seriesID": "PCU211111211111",
        "data": [
          {
            "year": "2024",
            "period": "M12",
            "periodName": "December",
            "latest": "true",
            "value": "186.7",
            "footnotes": [{}],
            "calculations": {
              "net_changes": {"1": "-2.3", "3": "5.1", "6": "-8.9", "12": "-15.2"},
              "pct_changes": {"1": "-1.2", "3": "2.8", "6": "-4.5", "12": "-7.5"}
            }
          }
        ]
      }
    ]
  }
}
```

Key fields:
- `status` -- `REQUEST_SUCCEEDED` or `REQUEST_FAILED`
- `message` -- array of warning/error messages
- `Results.series[].data[]` -- observations sorted most recent first
- `period` -- `M01`-`M12` for monthly, `M13` for annual average, `Q01`-`Q05` for quarterly
- `value` -- string, parse to float
- `calculations.pct_changes` -- percent change over 1, 3, 6, 12 months (if requested)
- `latest` -- `"true"` on the most recent observation

### Step 4 -- Produce Output

**Format: Data Table + Narrative**

Present a markdown table of the most relevant data points (cap at ~20 rows),
then a narrative summary covering:

1. **Current state** -- most recent value and date
2. **Trend** -- direction and magnitude using the calculations fields
3. **Year-over-year change** -- use `pct_changes["12"]` when available
4. **Historical context** -- where current value sits relative to the range
5. **Units and index base** -- PPI base is typically 1982=100 or Dec 2003=100
6. **PNGE relevance** -- connect to oilfield economics, cost estimation

**Example output structure:**
```
## PPI: Crude Petroleum (Monthly, 2020-2025)

| Year | Month | Index Value | 12-Mo % Change |
|------|-------|-------------|----------------|
| 2024 | December | 186.7 | -7.5% |
| 2024 | November | 189.0 | -5.2% |
| 2024 | October | 183.9 | -8.1% |

**Summary:** The Producer Price Index for crude petroleum stood at 186.7 in
December 2024, down 7.5% year-over-year. The index peaked at 268.4 in June
2022 during the post-invasion price shock and has since declined 30%. For
PNGE feasibility studies, the PPI trend suggests input cost deflation for
petroleum-based chemicals used in well treatment, while the falling index
also signals reduced drilling activity and consequently lower produced water
volumes available for Li recovery.

*Source: BLS, series PCU211111211111. Index base: June 1985 = 100.*
```

---

## Pagination

BLS API v2 does not paginate -- it returns all data points for the
requested year range in a single response. The constraint is on the year
span (max 10 or 20 years depending on registration).

For longer time series, make multiple requests with non-overlapping year
ranges and concatenate the results.

---

## Error Handling

| Condition | Meaning | Action |
|-----------|---------|--------|
| `status: "REQUEST_FAILED"` | Invalid parameters | Check `message` array for details |
| `message` contains "not a valid series" | Bad series ID | Verify series ID format and existence |
| `message` contains "exceeded the maximum" | Too many series or years | Reduce series count or narrow year range |
| HTTP 429 | Rate limit exceeded | Wait until next day (daily limit) or register for key |
| HTTP 502/503 | BLS server error | Retry after 5 seconds (max 3 retries) |
| Empty `data` array | No data for requested period | Widen year range or check if series is discontinued |
| `status: "REQUEST_SUCCEEDED"` with warnings | Partial success | Check `message` for which series failed |

**Common issues:**
- Series IDs are case-sensitive and must be exact
- Year values must be strings, not integers, in the JSON body
- Annual series (OES, injuries) only have data for years with surveys
- Some PPI series are discontinued when NAICS codes change

---

## Using BLS Data for PNGE Cost Estimation

### PPI as Cost Escalation Factor

To escalate historical costs to current dollars using PPI:

```
Current_Cost = Historical_Cost * (Current_PPI / Historical_PPI)
```

Example: A well completion cost $2M in 2019 when PPI for drilling
(PCU213111213111) was at 108.2. If PPI is now 135.6:

```
Current_Cost = $2,000,000 * (135.6 / 108.2) = $2,506,470
```

### CPI for Inflation Adjustment

Use CPI-U (CUUR0000SA0) to adjust general costs to real dollars.
Use CPI Energy (CUUR0000SEHE) specifically for energy cost adjustments.

### Employment Data for Market Analysis

Oil and gas extraction employment (CES1021100001) is a leading indicator
of industry activity. Employment typically lags price changes by 3-6 months.
Plot against WTI price (from FRED skill) for correlation analysis.

---

## Caveats and Data Quality

- **Publication schedule:** PPI and CPI released monthly (~2 weeks after
  reference month). Employment data released first Friday of following month.
  OES data released annually in March for prior May survey.
- **Revisions:** CPI is generally not revised. PPI can be revised for up
  to 4 months. Employment data revised twice (preliminary, final).
- **Seasonal adjustment:** Series with `S` in position 3 are seasonally
  adjusted; `U` is unadjusted. Use unadjusted for precise month values,
  adjusted for trend analysis.
- **Index base periods vary:** PPI crude petroleum uses June 1985=100.
  CPI uses 1982-84=100. Always report the base period with index values.
- **Industry reclassification:** NAICS codes change periodically. Some
  older PPI series are discontinued and replaced with new series IDs.
  Check BLS announcements if a series suddenly stops.
- **OES wage data:** Reports mean and percentile wages but does not include
  benefits. Total compensation is higher (use Employment Cost Index for
  benefits data).
- **Injury rate methodology changed in 2002.** Pre-2002 and post-2002 rates
  are not directly comparable.

---

## Implementation Notes

- **Use `bash` with `curl` + `jq`** for API calls
- **POST, not GET:** The BLS v2 API requires POST requests with JSON body.
  This is unusual among government APIs. GET requests return an error.
- **Values are strings** -- always parse to float for analysis
- **Period codes:** `M01`-`M12` = Jan-Dec, `M13` = annual average,
  `Q01`-`Q05` = quarterly (Q05 = annual), `A01` = annual
- **Multiple series:** Request up to 50 series in one call (with key)
  to minimize API calls. Useful for comparing PPI across sub-industries.
- **No text search:** BLS API does not have a search endpoint. Use the
  series ID tables above or the BLS Data Finder web tool to identify
  series IDs before querying.
