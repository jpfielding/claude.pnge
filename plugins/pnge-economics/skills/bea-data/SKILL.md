---
name: bea-data
description: >
  Query GDP, regional income, international trade, and industry economic
  data from the Bureau of Economic Analysis (BEA) API. Use when the user
  asks about GDP by industry for mining or oil and gas, regional personal
  income in energy-producing counties, trade in petroleum or lithium,
  gross output of extraction, value added by mining, or economic impact
  of oil and gas on state economies. Trigger phrases: "GDP from oil and
  gas extraction", "mining share of GDP", "personal income Monongalia
  County WV", "regional economic impact drilling", "trade in lithium",
  "petroleum trade balance", "gross output mining", "value added
  extraction", "natural gas contribution WV economy", "per capita income
  energy counties", "BEA regional data". Produces economic tables and
  narrative analysis with industry and regional context.
---

# BEA Data Skill

Fetches and analyzes U.S. economic accounts data from the Bureau of Economic
Analysis (BEA) API. Covers GDP by industry, regional personal income,
international trade, and input-output accounts. Essential for understanding
the economic context of petroleum-producing regions and the mining/extraction
sector.

## API Key Handling

An API key is required. Free registration.

Resolution order (stop at first success):

1. **`~/.config/bea/credentials`** -- parse `api_key=<value>` from this file
2. **`BEA_API_KEY` env var** -- fallback if credentials file is absent
3. **User-provided in conversation** -- fallback if neither above is set
4. **Prompt the user** -- "Please provide your BEA API key. Get one free at
   https://apps.bea.gov/API/signup/ -- store in `~/.config/bea/credentials`
   as `api_key=YOUR_KEY` (chmod 600)."

Never hardcode or log the key. Pass it as a query parameter `&UserID=<KEY>`.

**Reading the credentials file (bash):**
```bash
KEY=$(grep '^api_key=' ~/.config/bea/credentials 2>/dev/null | cut -d= -f2)
[ -z "$KEY" ] && KEY="${BEA_API_KEY}"
if [ -z "$KEY" ]; then
    echo "No BEA API key found. Get one free at https://apps.bea.gov/API/signup/"
    echo "Store in ~/.config/bea/credentials as api_key=YOUR_KEY"
    exit 1
fi
```

**Reading the credentials file (Go):**
```go
func resolveAPIKey() (string, error) {
    home, _ := os.UserHomeDir()
    creds := filepath.Join(home, ".config", "bea", "credentials")
    if data, err := os.ReadFile(creds); err == nil {
        for _, line := range strings.Split(string(data), "\n") {
            line = strings.TrimSpace(line)
            if strings.HasPrefix(line, "api_key=") {
                return strings.TrimPrefix(line, "api_key="), nil
            }
        }
    }
    if key := os.Getenv("BEA_API_KEY"); key != "" {
        return key, nil
    }
    return "", fmt.Errorf("no BEA API key found; register free at https://apps.bea.gov/API/signup/")
}
```

---

## API Structure

**Base URL:** `https://apps.bea.gov/api/data/`

All requests use GET with query parameters. Every request requires:
- `UserID` -- your API key
- `method` -- the API method to call
- `ResultFormat` -- always use `JSON`

### API Methods

| Method | Purpose |
|--------|---------|
| `GetDataSetList` | List all available datasets |
| `GetParameterList` | List parameters for a dataset |
| `GetParameterValues` | List valid values for a parameter |
| `GetParameterValuesFiltered` | Filtered parameter values |
| `GetData` | Fetch actual data |

### Key Datasets

| DatasetName | Description | Key Use |
|-------------|-------------|---------|
| `GDPByIndustry` | GDP, value added, gross output by NAICS industry | Mining/extraction share of GDP |
| `Regional` | Personal income, employment, GDP by state/county/MSA | Energy county economics |
| `ITA` | International Transactions (trade) | Petroleum/lithium trade flows |
| `IntlServTrade` | International services trade | Oilfield services trade |
| `NIPA` | National Income and Product Accounts | National-level aggregates |
| `InputOutput` | Input-output tables | Industry supply chain analysis |

---

## Key Queries by Domain

### GDP by Industry (Mining/Extraction)

```bash
# GDP by industry -- Mining sector (NAICS 21)
curl -s "https://apps.bea.gov/api/data/?\
UserID=$KEY&\
method=GetData&\
DatasetName=GDPByIndustry&\
TableID=1&\
Frequency=A&\
Year=2018,2019,2020,2021,2022,2023&\
Industry=21&\
ResultFormat=JSON"
```

**Key Industry codes for PNGE:**

| Industry Code | Description |
|---------------|-------------|
| `21` | Mining (includes oil/gas, minerals, coal) |
| `211` | Oil and Gas Extraction |
| `212` | Mining (except oil and gas) -- includes lithium mining |
| `213` | Support Activities for Mining |
| `ALL` | All industries (for computing shares) |

**Table IDs for GDPByIndustry:**

| TableID | Measure |
|---------|---------|
| `1` | Value Added by Industry (nominal) |
| `5` | Value Added by Industry (real, chained dollars) |
| `6` | Value Added by Industry (quantity index) |
| `7` | Gross Output by Industry (nominal) |
| `11` | Gross Output by Industry (real, chained dollars) |
| `25` | Value Added by Industry as % of GDP |

### Regional Data (State/County Level)

```bash
# Per capita personal income for WV counties
curl -s "https://apps.bea.gov/api/data/?\
UserID=$KEY&\
method=GetData&\
DatasetName=Regional&\
TableName=CAINC1&\
GeoFips=COUNTY&\
LineCode=3&\
Year=2022&\
ResultFormat=JSON"
```

**Key Regional tables:**

| TableName | Description |
|-----------|-------------|
| `CAINC1` | Personal Income Summary (county, state, MSA) |
| `CAINC4` | Personal Income and Employment by Major Component |
| `CAINC5N` | Personal Income by Major Component and Earnings by NAICS |
| `CAINC30` | Economic Profile (summary of key indicators) |
| `CAGDP1` | GDP Summary by county (limited industries) |
| `CAGDP2` | GDP by Industry at county level |
| `CAGDP9` | Real GDP by county |
| `SAINC1` | State Personal Income Summary |
| `SAGDP2N` | GDP by State and Industry |

**GeoFips codes:**

| Code | Scope |
|------|-------|
| `STATE` | All states |
| `COUNTY` | All counties |
| `MSA` | All metro/micro areas |
| `54000` | West Virginia (state FIPS) |
| `54061` | Monongalia County, WV |
| `54049` | Marion County, WV |
| `42125` | Washington County, PA |
| `39013` | Belmont County, OH |

**LineCode values for CAINC1:**

| LineCode | Measure |
|----------|---------|
| `1` | Personal income (thousands of dollars) |
| `2` | Population |
| `3` | Per capita personal income (dollars) |

### International Trade (Petroleum and Minerals)

```bash
# International trade in goods -- petroleum category
curl -s "https://apps.bea.gov/api/data/?\
UserID=$KEY&\
method=GetData&\
DatasetName=ITA&\
Indicator=BalGds&\
AreaOrCountry=AllCountries&\
Frequency=A&\
Year=2020,2021,2022,2023&\
ResultFormat=JSON"
```

**Key ITA indicators:**

| Indicator | Description |
|-----------|-------------|
| `ExpGds` | Exports of goods |
| `ImpGds` | Imports of goods |
| `BalGds` | Balance on goods |
| `ExpGdsEndUse` | Exports by end-use category |
| `ImpGdsEndUse` | Imports by end-use category |

---

## Workflow

### Step 1 -- Resolve Intent

Map the user's question to dataset and parameters:

| User Wants | Dataset | Parameters |
|-----------|---------|------------|
| Mining share of GDP | `GDPByIndustry` | Industry=21, TableID=25 |
| Oil/gas extraction GDP | `GDPByIndustry` | Industry=211, TableID=1 |
| WV county income | `Regional` | TableName=CAINC1, GeoFips=54000 or specific county |
| Income in drilling counties | `Regional` | TableName=CAINC5N + mining earnings line |
| Petroleum trade balance | `ITA` | Indicator=BalGds |
| Mining employment by state | `Regional` | TableName=CAEMP25N |

### Step 2 -- Discover Parameters (if needed)

If unsure of valid parameter values, query metadata first:

```bash
# List valid industries for GDPByIndustry
curl -s "https://apps.bea.gov/api/data/?\
UserID=$KEY&\
method=GetParameterValues&\
DatasetName=GDPByIndustry&\
ParameterName=Industry&\
ResultFormat=JSON"

# List valid tables for Regional dataset
curl -s "https://apps.bea.gov/api/data/?\
UserID=$KEY&\
method=GetParameterValues&\
DatasetName=Regional&\
ParameterName=TableName&\
ResultFormat=JSON"
```

### Step 3 -- Fetch Data

Build the URL with appropriate parameters. Default behavior:
- Use `Frequency=A` (annual) unless quarterly data is needed
- Request the last 5-6 years unless the user specifies otherwise
- Use `ResultFormat=JSON` always

```bash
# Value added by oil and gas extraction as % of GDP
curl -s "https://apps.bea.gov/api/data/?\
UserID=$KEY&\
method=GetData&\
DatasetName=GDPByIndustry&\
TableID=25&\
Frequency=A&\
Year=2018,2019,2020,2021,2022,2023&\
Industry=211&\
ResultFormat=JSON"
```

### Step 4 -- Parse Response

**Response structure:**
```json
{
  "BEAAPI": {
    "Request": {
      "RequestParam": [...]
    },
    "Results": {
      "Statistic": "Value Added by Industry as a Percentage of GDP",
      "UTCProductionTime": "2024-11-15T12:30:00.000",
      "Dimensions": [...],
      "Data": [
        {
          "TableID": "25",
          "Frequency": "A",
          "Year": "2023",
          "Quarter": null,
          "Industry": "211",
          "IndustrYDescription": "Oil and gas extraction",
          "DataValue": "1.3",
          "NoteRef": ""
        }
      ],
      "Notes": [...]
    }
  }
}
```

Key fields:
- `BEAAPI.Results.Data[]` -- array of data records
- `DataValue` -- string, parse to float; may be `"(D)"` for suppressed data
- `NoteRef` -- footnote reference code (check `Notes` array)
- `Year`/`Quarter` -- time period

**Special values in DataValue:**
- `"(D)"` -- data suppressed to avoid disclosure of individual firms
- `"(NA)"` -- not available
- `"(NM)"` -- not meaningful
- Numeric strings including negative values

### Step 5 -- Produce Output

**Format: Data Table + Narrative**

Present a markdown table of the most relevant rows (cap at ~20 rows), then
a narrative summary covering:

1. **Current state** -- most recent values
2. **Trend** -- direction and magnitude over the time window
3. **Comparative context** -- how regions or industries compare
4. **Economic significance** -- share of GDP, income growth, trade balance
5. **PNGE relevance** -- connect to oilfield economics, regional development
6. **Units and caveats** -- current vs chained dollars, data suppression

**Example output structure:**
```
## Oil and Gas Extraction -- Value Added as % of GDP (2018-2023)

| Year | Oil/Gas Extraction (% GDP) | All Mining (% GDP) |
|------|----------------------------|--------------------|
| 2023 | 1.3 | 1.9 |
| 2022 | 2.1 | 2.8 |
| 2021 | 1.2 | 1.7 |
| 2020 | 0.7 | 1.1 |
| 2019 | 1.5 | 2.0 |
| 2018 | 1.7 | 2.2 |

**Summary:** Oil and gas extraction contributed 1.3% of U.S. GDP in 2023,
down from its post-COVID rebound peak of 2.1% in 2022 when high commodity
prices inflated the sector's nominal value added. The 2020 trough (0.7%)
reflects the COVID demand destruction. For WV specifically, the mining
sector's GDP share is significantly higher -- use the Regional dataset
(SAGDP2N) for state-level industry breakdown.

*Source: BEA GDP by Industry accounts. Nominal value added.*
```

---

## Pagination

The BEA API does not paginate -- it returns all matching data in a single
response. For large result sets (e.g., all counties), the response may be
large but complete.

If a request returns too many records (e.g., all counties x all years),
narrow the query by specifying GeoFips codes or limiting the year range.

---

## Error Handling

| Condition | Meaning | Action |
|-----------|---------|--------|
| `"Error"` key in response | API error | Read `ErrorDetail.Description` for message |
| `"APIErrorCode": "40"` | Invalid parameter value | Use `GetParameterValues` to find valid options |
| `"APIErrorCode": "36"` | Missing required parameter | Check required params for the dataset |
| `"APIErrorCode": "24"` | Invalid UserID | Verify API key is correct |
| HTTP 503 | Service unavailable | Retry after 5 seconds (max 3 retries) |
| `DataValue: "(D)"` | Suppressed for disclosure | Data exists but cannot be shown; try broader geography |
| `DataValue: "(NA)"` | Not available | Data not produced for this combination |

**Common error response:**
```json
{
  "BEAAPI": {
    "Request": {...},
    "Results": {
      "Error": {
        "APIErrorCode": "40",
        "APIErrorDescription": "The parameter value '999' is not valid..."
      }
    }
  }
}
```

---

## PNGE-Relevant Query Patterns

### Compare Energy County Incomes

```bash
# Per capita income for key Marcellus/Utica counties
# Monongalia WV, Marion WV, Washington PA, Belmont OH
curl -s "https://apps.bea.gov/api/data/?\
UserID=$KEY&\
method=GetData&\
DatasetName=Regional&\
TableName=CAINC1&\
GeoFips=54061,54049,42125,39013&\
LineCode=3&\
Year=2018,2019,2020,2021,2022&\
ResultFormat=JSON"
```

### Mining Earnings as Share of County Income

```bash
# Earnings by NAICS industry for WV counties
curl -s "https://apps.bea.gov/api/data/?\
UserID=$KEY&\
method=GetData&\
DatasetName=Regional&\
TableName=CAINC5N&\
GeoFips=54061&\
LineCode=200&\
Year=2022&\
ResultFormat=JSON"
```

LineCode 200 = Mining, quarrying, and oil and gas extraction earnings.

### WV State GDP by Industry

```bash
# GDP by industry for West Virginia
curl -s "https://apps.bea.gov/api/data/?\
UserID=$KEY&\
method=GetData&\
DatasetName=Regional&\
TableName=SAGDP2N&\
GeoFips=54000&\
LineCode=6&\
Year=2022&\
ResultFormat=JSON"
```

LineCode 6 = Mining, quarrying, and oil and gas extraction.

---

## FIPS Code Reference for Appalachian Energy Counties

| FIPS | County | State | Notes |
|------|--------|-------|-------|
| 54061 | Monongalia | WV | Marcellus core, university town |
| 54049 | Marion | WV | Marcellus core, coal heritage |
| 54051 | Marshall | WV | Marcellus core, Ohio River |
| 54009 | Brooke | WV | Northern panhandle |
| 54029 | Hancock | WV | Northern panhandle |
| 54103 | Wetzel | WV | Major Marcellus producer |
| 42125 | Washington | PA | SW PA Marcellus core |
| 42059 | Greene | PA | Major Marcellus producer |
| 39013 | Belmont | OH | Utica core |
| 39111 | Monroe | OH | Utica core |

---

## Caveats and Data Quality

- **Publication lag:** GDP by industry released annually (~6 months after
  year end). Regional county data lags ~18 months. Advance estimates may
  be revised for up to 3 years.
- **Data suppression:** County-level data for small industries is frequently
  suppressed `(D)` to protect individual firm confidentiality. Mining data
  is especially prone to this in counties with few operators.
- **NAICS aggregation:** "Mining" (NAICS 21) includes oil/gas extraction
  (211), non-oil/gas mining (212, includes lithium), and support activities
  (213). Finer breakdowns are often suppressed at the county level.
- **Current vs real dollars:** GDP tables with "nominal" or "current dollar"
  values reflect both price and quantity changes. Use "chained dollar" or
  "real" tables (TableID 5, 11) for volume trends. Do not compare nominal
  values across years without deflating.
- **Regional data coverage:** County-level GDP data (CAGDP series) began in
  2017 and covers fewer industries than state-level data. Personal income
  data goes back to 1969 for most counties.
- **API rate limits:** BEA does not publish explicit rate limits, but
  excessive requests may trigger throttling. Add 200ms delay between
  sequential calls.

---

## Implementation Notes

- **Use `bash` with `curl` + `jq`** for API calls
- **GET requests only** -- all BEA API calls are GET with query parameters
- **DataValue is always a string** -- parse to float, handle special values
  `(D)`, `(NA)`, `(NM)` as missing data
- **Year parameter:** Comma-separated list of years or `ALL` for all
  available years. `LAST5` returns the last 5 years.
- **GeoFips:** State codes are `XX000` (e.g., `54000` for WV). County codes
  are 5-digit FIPS. Use `STATE`, `COUNTY`, or `MSA` for all entities of
  that type.
- **Multiple industries:** Use `Industry=ALL` or comma-separated codes.
  At the county level, only broad industry groups are available.
- **BEA API documentation:** Full reference at
  https://apps.bea.gov/api/_pdf/bea_web_service_api_user_guide.pdf
