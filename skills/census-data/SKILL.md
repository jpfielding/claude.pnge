---
name: census-data
description: >
  Query U.S. Census Bureau API for demographic, economic, and housing data
  at state, county, and tract levels. Use when the user asks about
  population in energy-producing counties, demographics near well sites,
  environmental justice demographics, workforce in petroleum regions,
  housing in drilling areas, economic census mining data, or poverty in
  extraction communities. Trigger phrases: "population Monongalia County",
  "demographics near well pad", "environmental justice census data",
  "workforce mining counties", "housing growth Marcellus Shale",
  "poverty rate drilling counties", "ACS data WV counties", "community
  impact oil and gas", "median household income energy counties",
  "Census tract demographics produced water facility". Produces
  demographic tables and narrative analysis with community context.
---

# Census Data Skill

Fetches and analyzes U.S. demographic, economic, and housing data from the
Census Bureau API. Primary focus on American Community Survey (ACS) 5-year
estimates for county and tract-level data relevant to energy-producing
communities, environmental justice analysis, and workforce assessment.

## API Key Handling

An API key is required. Free, instant registration.

Resolution order (stop at first success):

1. **`~/.config/census/credentials`** -- parse `api_key=<value>` from this file
2. **`CENSUS_API_KEY` env var** -- fallback if credentials file is absent
3. **User-provided in conversation** -- fallback if neither above is set
4. **Prompt the user** -- "Please provide your Census API key. Get one free
   (instant) at https://api.census.gov/data/key_signup.html -- store in
   `~/.config/census/credentials` as `api_key=YOUR_KEY` (chmod 600)."

Never hardcode or log the key. Pass it as a query parameter `&key=<KEY>`.

**Reading the credentials file (bash):**
```bash
KEY=$(grep '^api_key=' ~/.config/census/credentials 2>/dev/null | cut -d= -f2)
[ -z "$KEY" ] && KEY="${CENSUS_API_KEY}"
if [ -z "$KEY" ]; then
    echo "No Census API key found. Get one free at https://api.census.gov/data/key_signup.html"
    echo "Store in ~/.config/census/credentials as api_key=YOUR_KEY"
    exit 1
fi
```

**Reading the credentials file (Go):**
```go
func resolveAPIKey() (string, error) {
    home, _ := os.UserHomeDir()
    creds := filepath.Join(home, ".config", "census", "credentials")
    if data, err := os.ReadFile(creds); err == nil {
        for _, line := range strings.Split(string(data), "\n") {
            line = strings.TrimSpace(line)
            if strings.HasPrefix(line, "api_key=") {
                return strings.TrimPrefix(line, "api_key="), nil
            }
        }
    }
    if key := os.Getenv("CENSUS_API_KEY"); key != "" {
        return key, nil
    }
    return "", fmt.Errorf("no Census API key; register free at https://api.census.gov/data/key_signup.html")
}
```

---

## API Structure

**Base URL pattern:**
```
https://api.census.gov/data/{year}/{dataset}?get={variables}&for={geography}&in={parent_geography}&key={KEY}
```

### Key Datasets

| Dataset Path | Description | Update Cycle |
|-------------|-------------|--------------|
| `acs/acs5` | ACS 5-Year Estimates (Detailed Tables) | Annual (Dec release for prior year) |
| `acs/acs5/profile` | ACS 5-Year Data Profile (pre-computed summaries) | Annual |
| `acs/acs5/subject` | ACS 5-Year Subject Tables | Annual |
| `acs/acs1` | ACS 1-Year Estimates (areas 65k+ pop only) | Annual |
| `dec/pl` | Decennial Census PL 94-171 Redistricting | Every 10 years |
| `cbp` | County Business Patterns | Annual |
| `ecnbasic` | Economic Census (basic) | Every 5 years (2017, 2022) |

**Most common for PNGE research:** `acs/acs5` -- available at tract, county,
state, and national levels for all areas regardless of population.

### Geography Hierarchy

```
us (nation)
  └── state (2-digit FIPS)
      └── county (3-digit FIPS within state)
          └── tract (6-digit within county)
              └── block group (1-digit within tract)
```

**Geography parameter syntax:**

| For | Syntax |
|-----|--------|
| All states | `for=state:*` |
| West Virginia | `for=state:54` |
| All WV counties | `for=county:*&in=state:54` |
| Monongalia County, WV | `for=county:061&in=state:54` |
| All tracts in Monongalia Co | `for=tract:*&in=state:54&in=county:061` |
| Specific tract | `for=tract:010100&in=state:54&in=county:061` |

---

## Key Variables for PNGE Research

### Population and Demographics (ACS 5-Year)

| Variable | Description |
|----------|-------------|
| `B01003_001E` | Total population |
| `B01002_001E` | Median age |
| `B02001_001E` | Total population (race table) |
| `B02001_002E` | White alone |
| `B02001_003E` | Black or African American alone |
| `B03003_001E` | Total (Hispanic origin table) |
| `B03003_003E` | Hispanic or Latino |
| `B01001_002E` | Male population |
| `B01001_026E` | Female population |

### Income and Poverty

| Variable | Description |
|----------|-------------|
| `B19013_001E` | Median household income |
| `B19301_001E` | Per capita income |
| `B17001_001E` | Total for poverty status determination |
| `B17001_002E` | Below poverty level |
| `B19083_001E` | Gini Index of income inequality |

### Housing

| Variable | Description |
|----------|-------------|
| `B25001_001E` | Total housing units |
| `B25002_002E` | Occupied housing units |
| `B25002_003E` | Vacant housing units |
| `B25077_001E` | Median home value (owner-occupied) |
| `B25064_001E` | Median gross rent |
| `B25003_002E` | Owner-occupied units |
| `B25003_003E` | Renter-occupied units |

### Employment and Workforce

| Variable | Description |
|----------|-------------|
| `B23025_001E` | Total 16+ for employment status |
| `B23025_002E` | In labor force |
| `B23025_005E` | Unemployed (civilian) |
| `B23025_007E` | Not in labor force |
| `C24030_002E` | Male employed in natural resources, construction, maintenance |
| `C24030_029E` | Female employed in natural resources, construction, maintenance |

### Education

| Variable | Description |
|----------|-------------|
| `B15003_001E` | Total 25+ for educational attainment |
| `B15003_022E` | Bachelor's degree |
| `B15003_023E` | Master's degree |
| `B15003_025E` | Doctorate degree |

### Environmental Justice Indicators

| Variable | Description |
|----------|-------------|
| `B02001_001E` | Total population (for % minority calculation) |
| `B02001_002E` | White alone (subtract from total for minority %) |
| `B17001_002E` | Below poverty (for low-income %) |
| `B16004_001E` | Total 5+ (for limited English proficiency) |
| `B09001_001E` | Under 18 (for vulnerable population assessment) |
| `B01001_020E` - `B01001_025E` | Male 65+ (elderly population components) |
| `B01001_044E` - `B01001_049E` | Female 65+ (elderly population components) |

### Data Profile Variables (pre-computed percentages)

| Variable | Description |
|----------|-------------|
| `DP03_0004PE` | Employment rate (%) |
| `DP03_0005PE` | Unemployment rate (%) |
| `DP03_0062E` | Median household income ($) |
| `DP03_0088E` | Percent below poverty (%) |
| `DP05_0001E` | Total population |
| `DP05_0018E` | Median age |
| `DP02_0068PE` | Percent with bachelor's or higher (%) |

---

## Workflow

### Step 1 -- Resolve Intent

Map the user's question to dataset, variables, and geography:

| User Wants | Dataset | Variables | Geography |
|-----------|---------|-----------|-----------|
| County population | `acs/acs5` | `B01003_001E` | `county:*&in=state:XX` |
| Income comparison | `acs/acs5` | `B19013_001E` | Multiple counties |
| EJ demographics | `acs/acs5` | `B02001_*`, `B17001_002E` | Tracts in county |
| Workforce data | `acs/acs5/profile` | `DP03_0004PE,DP03_0005PE` | County |
| Housing boom check | `acs/acs5` | `B25077_001E,B25064_001E` | Counties over time |
| Mining workforce | `cbp` | `EMP,ESTAB` | County with NAICS filter |

### Step 2 -- Fetch Data

Build the URL with appropriate parameters. Default behavior:
- Use `acs/acs5` for county and tract data (most geographically complete)
- Use the most recent available year (typically current year minus 2)
- Request `NAME` variable along with data variables for readable labels
- Limit variable list to 50 per request (API maximum)

```bash
# Basic: Population and income for all WV counties
curl -s "https://api.census.gov/data/2023/acs/acs5?\
get=NAME,B01003_001E,B19013_001E&\
for=county:*&\
in=state:54&\
key=$KEY"
```

```bash
# Environmental justice: Race and poverty at tract level in Monongalia County
curl -s "https://api.census.gov/data/2023/acs/acs5?\
get=NAME,B01003_001E,B02001_002E,B17001_001E,B17001_002E&\
for=tract:*&\
in=state:54&in=county:061&\
key=$KEY"
```

```bash
# County Business Patterns: Mining establishments and employment
curl -s "https://api.census.gov/data/2022/cbp?\
get=NAICS2017,NAICS2017_LABEL,EMP,ESTAB,PAYANN&\
for=county:061&\
in=state:54&\
NAICS2017=21&\
key=$KEY"
```

### Step 3 -- Parse Response

The Census API returns a JSON array of arrays. The first row is the header:

```json
[
  ["NAME", "B01003_001E", "B19013_001E", "state", "county"],
  ["Monongalia County, West Virginia", "106612", "50321", "54", "061"],
  ["Marion County, West Virginia", "55515", "44286", "54", "049"],
  ["Marshall County, West Virginia", "30900", "48750", "54", "051"]
]
```

Key parsing rules:
- Row 0 = headers, rows 1+ = data
- All values are strings -- parse numeric values to int or float
- `-666666666` indicates the estimate is not available
- Margin of error variables end in `M` instead of `E` (e.g., `B01003_001M`)
- `null` values indicate data not applicable or suppressed

### Step 4 -- Compute Derived Metrics

For environmental justice analysis, compute:
```
% Minority = 100 * (1 - White_Alone / Total_Population)
% Below Poverty = 100 * (Below_Poverty / Total_Poverty_Universe)
% Unemployed = 100 * (Unemployed / In_Labor_Force)
```

For workforce analysis:
```
Labor Force Participation = 100 * (In_Labor_Force / Total_16_Plus)
Employment Rate = 100 * (Employed / Total_16_Plus)
```

### Step 5 -- Produce Output

**Format: Data Table + Narrative**

Present a markdown table of the most relevant rows (cap at ~20 rows), then
a narrative summary covering:

1. **Key findings** -- most notable demographics or disparities
2. **Comparison** -- how areas compare to state and national benchmarks
3. **Trend context** -- reference prior years if time series was requested
4. **EJ implications** -- flag tracts with high minority % or poverty %
5. **PNGE relevance** -- connect demographics to community impact of drilling
6. **Margin of error note** -- ACS estimates have MOEs, especially at tract level

**Example output structure:**
```
## Monongalia County, WV -- Key Demographics (ACS 2023 5-Year)

| Metric | Monongalia Co. | WV State | U.S. |
|--------|---------------|----------|------|
| Population | 106,612 | 1,775,156 | 331,449,281 |
| Median HH Income | $50,321 | $51,615 | $75,149 |
| Poverty Rate | 23.1% | 17.4% | 12.6% |
| Bachelor's+ | 42.8% | 22.2% | 33.7% |
| Median Age | 28.4 | 42.8 | 38.9 |

**Summary:** Monongalia County's elevated poverty rate (23.1%) alongside
high educational attainment (42.8% bachelor's+) reflects the university
student population (WVU). The young median age (28.4) is also student-driven.
For produced water facility siting analysis, tract-level data shows the
northern tracts (near industrial areas along the Monongahela River) have
higher minority populations (8-12%) compared to southern residential tracts
(3-5%). Mining-sector employment data from County Business Patterns shows
54 mining establishments employing approximately 1,200 workers.

*Source: U.S. Census Bureau, ACS 2019-2023 5-Year Estimates. Margins of
error apply to all ACS estimates and are wider at tract level.*
```

---

## Pagination

The Census API does not paginate. It returns all matching records in a single
response. However, it limits requests to 50 variables per call.

For more than 50 variables, make multiple requests and join on geography
codes:

```bash
# Request 1: demographics
curl -s "...?get=NAME,B01003_001E,B02001_002E,...&for=county:*&in=state:54&key=$KEY"

# Request 2: economic variables
curl -s "...?get=B19013_001E,B23025_002E,...&for=county:*&in=state:54&key=$KEY"

# Join on state + county columns
```

---

## Error Handling

| Condition | Meaning | Action |
|-----------|---------|--------|
| HTTP 200 + `"error"` key | Invalid variable, geography, or year | Read error message; check variable names |
| HTTP 204 (No Content) | No data for this combination | Check year availability; try broader geography |
| HTTP 400 | Malformed request | Check URL encoding; verify parameter syntax |
| HTTP 403 | Invalid or missing API key | Verify key; re-register if needed |
| HTTP 500 | Server error | Retry after 5 seconds (max 3 retries) |
| Value `-666666666` | Estimate not available | Report as N/A; try larger geography |
| Value `null` | Not applicable or suppressed | Report as N/A |

**Common mistakes:**
- Variable names are case-sensitive (uppercase)
- County FIPS is 3 digits within state (not 5-digit national FIPS)
- Tract codes are 6 digits (e.g., `010100`), not the dotted format (101.00)
- `in=state:54` uses FIPS code, not state abbreviation
- ACS 5-year data is published ~December for the prior year (e.g., 2023 data
  available Dec 2024)

---

## Available ACS Years

| Dataset | Latest Year | Geography |
|---------|------------|-----------|
| ACS 5-Year | 2023 | All geographies (nation to block group) |
| ACS 1-Year | 2023 | Areas with 65,000+ population only |

Check available years:
```bash
curl -s "https://api.census.gov/data.json" | jq '.dataset[] | select(.c_vintage) | {title: .title, year: .c_vintage}' | head -50
```

---

## PNGE-Relevant Query Patterns

### Environmental Justice Screening

For new facility siting or permit applications, EPA requires EJ analysis.
Census tract-level data provides the demographic foundation:

```bash
# Tract-level EJ indicators for a county
curl -s "https://api.census.gov/data/2023/acs/acs5?\
get=NAME,B01003_001E,B02001_002E,B17001_001E,B17001_002E,B01001_020E,B01001_021E,B01001_022E,B01001_023E,B01001_024E,B01001_025E&\
for=tract:*&\
in=state:54&in=county:061&\
key=$KEY"
```

Then compute:
- `% Minority = 100 * (1 - B02001_002E / B01003_001E)`
- `% Below Poverty = 100 * (B17001_002E / B17001_001E)`
- Flag tracts exceeding state or national thresholds

### Community Impact of Drilling Boom

Track housing, income, and population changes in drilling counties by
comparing ACS vintages:

```bash
# 2018 data for baseline
curl -s "https://api.census.gov/data/2018/acs/acs5?get=NAME,B01003_001E,B19013_001E,B25077_001E&for=county:061&in=state:54&key=$KEY"

# 2023 data for current
curl -s "https://api.census.gov/data/2023/acs/acs5?get=NAME,B01003_001E,B19013_001E,B25077_001E&for=county:061&in=state:54&key=$KEY"
```

### Mining Workforce Assessment

County Business Patterns provides establishment and employment counts by
NAICS industry:

```bash
# Mining establishments in WV counties
curl -s "https://api.census.gov/data/2022/cbp?\
get=NAICS2017,NAICS2017_LABEL,EMP,ESTAB,PAYANN&\
for=county:*&\
in=state:54&\
NAICS2017=211&\
key=$KEY"
```

---

## FIPS Code Reference

| FIPS | Geography |
|------|-----------|
| 54 | West Virginia (state) |
| 54061 | Monongalia County, WV |
| 54049 | Marion County, WV |
| 54051 | Marshall County, WV |
| 54103 | Wetzel County, WV |
| 42125 | Washington County, PA |
| 42059 | Greene County, PA |
| 39013 | Belmont County, OH |
| 39111 | Monroe County, OH |

Note: In Census API calls, state is 2 digits and county is the trailing 3
digits. For tract queries, use `in=state:54&in=county:061`.

---

## Caveats and Data Quality

- **ACS is estimates, not counts.** Every ACS value has a margin of error
  (MOE). At tract level, MOEs can be very large (30-50% of estimate for
  small populations). Always request and report MOE variables alongside
  estimates for tract-level analysis.
- **5-year vs 1-year.** ACS 5-year pools 60 months of data for reliability
  at small geographies. It reflects conditions over the entire period, not
  a single point in time. ACS 1-year is more current but only available for
  65k+ population areas.
- **Reference period.** ACS 2023 5-year covers 2019-2023. Major economic
  disruptions (COVID, drilling booms/busts) within that window affect the
  estimates.
- **Census tract boundaries.** Tracts are redrawn each decennial census.
  2020 tract boundaries differ from 2010. Ensure tract-level comparisons
  use the same vintage boundaries.
- **Suppression.** Very small populations or cells may be suppressed. The
  Census Bureau also applies disclosure avoidance (differential privacy
  for 2020 Decennial).
- **CBP limitations.** County Business Patterns suppresses employment data
  for industries with few establishments to protect firm confidentiality.
  Suppressed cells show employment range codes instead of exact counts.
- **University towns.** Counties with large universities (Monongalia/WVU,
  Athens/Ohio U) have distorted poverty and age statistics due to student
  populations. Note this in analysis.

---

## Implementation Notes

- **Use `bash` with `curl` + `jq`** for API calls
- **GET requests** -- all Census API calls are GET with query parameters
- **Response is array-of-arrays** -- first row is headers, not objects.
  Parse accordingly.
- **50-variable limit per request.** Plan variable lists carefully; split
  into multiple requests and join on geography codes if needed.
- **Variable discovery:** Browse variables at
  `https://api.census.gov/data/2023/acs/acs5/variables.json` or use the
  Census Data Explorer at https://data.census.gov/
- **Rate limits:** Census does not publish hard limits, but respect the
  service -- add 100ms delay between sequential calls
- **URL encoding:** Variable lists are comma-separated, no URL encoding
  needed for commas in the `get` parameter
- **Vintage year in URL:** The year in the URL path (e.g., `/2023/acs/acs5`)
  refers to the data vintage, not a filter. You get the full dataset for
  that vintage and filter by geography.
