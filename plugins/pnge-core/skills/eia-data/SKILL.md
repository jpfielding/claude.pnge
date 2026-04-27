---
name: eia-data
description: >
  Query, analyze, and summarize U.S. energy data from the EIA (Energy Information
  Administration) Open Data API v2. Use this skill whenever the user asks about
  electricity prices, generation, demand, petroleum supply, natural gas production,
  storage, prices, or any U.S. energy statistics — even if they don't explicitly
  mention EIA or the API. Trigger for phrases like "how much gas is in storage",
  "electricity prices in Texas", "what's the national average price of gasoline",
  "natural gas production trend", "power generation by fuel type", "crude oil imports",
  "energy data", or any request for current or historical U.S. energy figures.
  Produces trend summaries and raw data tables with narrative analysis.
---

# EIA Open Data Skill

Fetches and analyzes U.S. energy data from the EIA API v2 (api.eia.gov/v2).

## API Key Handling

Resolution order (stop at first success):

1. **`~/.config/eia/credentials`** (default) — parse `api_key=<value>` from this file
2. **`EIA_API_KEY` env var** — fallback if credentials file is absent
3. **User-provided in conversation** — fallback if neither above is set
4. **Prompt the user** — "Please provide your EIA API key. You can get one free at https://www.eia.gov/opendata/ — or store it in `~/.config/eia/credentials` as `api_key=YOUR_KEY` (chmod 600)."

Never hardcode or log the key. Pass it as a query parameter `?api_key=<KEY>`.

**Reading the credentials file (bash):**
```bash
KEY=$(grep '^api_key=' ~/.config/eia/credentials 2>/dev/null | cut -d= -f2)
[ -z "$KEY" ] && KEY="${EIA_API_KEY}"
```

**Reading the credentials file (Go):**
```go
func resolveAPIKey() (string, error) {
    if path, err := os.UserHomeDir(); err == nil {
        creds := filepath.Join(path, ".config", "eia", "credentials")
        if data, err := os.ReadFile(creds); err == nil {
            for _, line := range strings.Split(string(data), "\n") {
                if strings.HasPrefix(line, "api_key=") {
                    return strings.TrimPrefix(line, "api_key="), nil
                }
            }
        }
    }
    if key := os.Getenv("EIA_API_KEY"); key != "" {
        return key, nil
    }
    return "", fmt.Errorf("no EIA API key found; store in ~/.config/eia/credentials")
}
```

---

## API Structure

**Base URL:** `https://api.eia.gov/v2/`

**Self-describing hierarchy** — query any route without `/data` to get its children and available facets:
```
GET /v2/                          → top-level categories
GET /v2/electricity/              → electricity sub-routes
GET /v2/electricity/retail-sales/ → metadata + available facets
GET /v2/electricity/retail-sales/data/ → actual data
```

**Key parameters for data requests:**
| Parameter | Example | Notes |
|-----------|---------|-------|
| `api_key` | `api_key=YOUR_KEY` | Required |
| `frequency` | `frequency=monthly` | annual, quarterly, monthly, weekly, hourly |
| `data[]` | `data[]=price` | which value columns to return |
| `facets[X][]` | `facets[stateid][]=TX` | filter by dimension |
| `start` | `start=2022-01` | inclusive |
| `end` | `end=2024-12` | inclusive |
| `sort[0][column]` | `sort[0][column]=period` | sort field |
| `sort[0][direction]` | `sort[0][direction]=desc` | asc or desc |
| `offset` | `offset=0` | pagination start |
| `length` | `length=5000` | max 5000 per request |

---

## Key Routes by Domain

See `references/routes.md` for full route catalog. High-priority routes:

### Electricity
| Route | Description |
|-------|-------------|
| `electricity/retail-sales/data/` | Retail sales — price, revenue, sales by state + sector |
| `electricity/rto/region-data/data/` | Hourly demand by balancing authority |
| `electricity/rto/fuel-type-data/data/` | Hourly generation by fuel type |
| `electricity/electric-power-operational-data/data/` | Monthly generation by plant type, state |

**Common facets:**
- `stateid`: 2-letter state code (TX, CA, NY…) or US for national
- `sectorid`: RES (residential), COM (commercial), IND (industrial), TRA (transport), ALL
- `fueltypeid`: NG, COL, NUC, SUN, WND, WAT, OIL, OTH

### Petroleum & Natural Gas
| Route | Description |
|-------|-------------|
| `petroleum/pri/gnd/data/` | Weekly gasoline & diesel retail prices |
| `petroleum/sum/sndw/data/` | Weekly petroleum supply summary |
| `petroleum/stoc/wstk/data/` | Weekly crude oil & petroleum product stocks |
| `petroleum/move/imp/data/` | Crude oil imports |
| `natural-gas/pri/sum/data/` | Natural gas prices (citygate, wellhead, retail) |
| `natural-gas/stor/sum/data/` | Weekly natural gas storage |
| `natural-gas/prod/sum/data/` | Monthly dry gas production |

**Common facets:**
- `duoarea`: National (NUS), PADD regions (R10=PADD1, R20=PADD2…), state codes
- `product`: EPD2D (diesel), EPM0 (regular gasoline), EPM0R (reformulated)
- `process`: PRS (retail sales), PRW (wellhead), PRI (imports)

---

## Workflow

### Step 1 — Resolve Intent
Map the user's question to a route. If uncertain:
- Query the parent route (no `/data/`) to inspect available sub-routes
- Check `references/routes.md` for common mappings

### Step 2 — Fetch Metadata First (when needed)
```bash
curl "https://api.eia.gov/v2/<route>/?api_key=<KEY>"
```
Returns: available `facets`, `frequency` options, `data` columns, `startPeriod`, `endPeriod`.
Use this to validate facet values before data fetch.

### Step 3 — Fetch Data
Build the URL with appropriate filters. Default behavior:
- Use `frequency=monthly` unless user asks for hourly/weekly/annual
- Sort by `period desc` to get most recent first
- Request `length=5000` (max); paginate if response warns of truncation
- Default time window: last 24 months unless user specifies

```bash
curl "https://api.eia.gov/v2/electricity/retail-sales/data/?api_key=<KEY>\
  &frequency=monthly\
  &data[]=price\
  &facets[stateid][]=TX\
  &facets[sectorid][]=RES\
  &sort[0][column]=period\
  &sort[0][direction]=desc\
  &length=24"
```

### Step 4 — Parse Response
Response structure:
```json
{
  "response": {
    "total": 123,
    "dateFormat": "YYYY-MM",
    "frequency": "monthly",
    "data": [ { "period": "2024-11", "stateid": "TX", "price": 11.23, "price-units": "cents per kilowatthour" } ]
  },
  "request": { ... },
  "apiVersion": "2.1.9"
}
```

Always check `response.total` vs returned row count — paginate if `total > length`.

### Step 5 — Produce Output

**Format: Raw Data Table + Narrative**

Present a markdown table of the most relevant rows (cap at ~20 rows for readability), then a narrative summary covering:

1. **Current state** — most recent value(s) and date
2. **Trend** — direction and magnitude over the time window (use % change)
3. **Notable features** — peaks, troughs, inflection points
4. **Geographic or sector context** if applicable
5. **Units and caveats** — always state units; note if data is preliminary

**Example output structure:**
```
## Texas Residential Electricity Prices (Monthly, 2023–2024)

| Period   | Price (¢/kWh) |
|----------|---------------|
| 2024-11  | 11.23         |
| 2024-10  | 11.45         |
| ...      | ...           |

**Summary:** Texas residential electricity averaged 11.23¢/kWh in November 2024,
down 1.9% from the prior month and 3.2% year-over-year. Prices peaked at 14.1¢/kWh
in August 2023 driven by summer demand, then declined through winter. Data is
preliminary for the most recent 2 months (EIA revision cycle).
```

---

## Pagination

If `response.total > length`, paginate:
```python
offset = 0
all_data = []
while offset < total:
    # fetch with &offset=<offset>&length=5000
    all_data.extend(response["response"]["data"])
    offset += 5000
```
Warn the user if dataset is very large (>20k rows) and ask if they want a filtered subset.

## Error Handling

| HTTP Code | Meaning | Action |
|-----------|---------|--------|
| 400 | Bad parameter | Log error body; fix facet/frequency and retry |
| 403 | Invalid API key | Prompt user to verify key |
| 404 | Route not found | Query parent route for valid children |
| 200 + warning | Partial result / row cap | Paginate or narrow filters |

---

## Geo Reference

**PADD Regions** (Petroleum Administration for Defense Districts):
- PADD 1: East Coast (R10)
- PADD 2: Midwest (R20)
- PADD 3: Gulf Coast (R30)
- PADD 4: Rocky Mountain (R40)
- PADD 5: West Coast (R50)

**RTO/ISO Balancing Authorities** (electricity):
- CISO = CAISO (California)
- ERCO = ERCOT (Texas)
- MISO = Midcontinent ISO
- PJM = PJM Interconnection
- NYIS = NYISO
- ISNE = ISO New England
- SWPP = Southwest Power Pool
- US48 = Contiguous US aggregate

---

## Implementation Notes

- **Prefer `bash_tool` or `python` in Claude's computer** to make actual HTTP requests
- **Use `jq` for JSON parsing** in bash pipelines when available
- **Golang client** — see `references/golang_example.go` (`EIAClient`, `QueryParams`, `FetchAll`)
- **Python client** — see `references/python_example.py` (`EIAClient`, `QueryParams`, `fetch_all`, `paginate`)
- Response `dateFormat` field tells you the exact format for the `period` field — don't assume
- EIA updates: weekly data Wednesdays, monthly data ~6 weeks after period end
- Preliminary flag: most recent 1–2 months are often marked preliminary and subject to revision
