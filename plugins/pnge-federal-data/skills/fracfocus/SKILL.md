---
name: fracfocus
description: >
  Query and analyze hydraulic fracturing chemical disclosure data from the
  FracFocus Chemical Disclosure Registry. Use this skill whenever the user asks
  about frac fluid composition, hydraulic fracturing chemicals, chemical
  disclosure for a well, FracFocus data, what chemicals were used in a frac job,
  HF fluid ingredients, proppant volumes, base water volume, or any question
  about chemicals pumped downhole during stimulation -- even if they don't
  explicitly mention FracFocus. Trigger for phrases like "what chemicals were
  used", "frac fluid composition", "hydraulic fracturing disclosure",
  "FracFocus lookup", "HF chemical data", "frac job chemicals in West Virginia",
  "well stimulation chemicals", "CAS number lookup for fracking", or "proppant
  used in Marcellus wells". Produces well-level chemical tables with narrative
  analysis and data quality notes.
---

# FracFocus Chemical Disclosure Skill

Searches and retrieves hydraulic fracturing chemical disclosure records from
the FracFocus registry (fracfocus.org). Covers 200k+ disclosures across 34
states from 2011 to present.

## API Key Handling

**No API key required.** FracFocus public data is freely accessible.

---

## Data Access Methods

FracFocus provides two access methods:

1. **Public Search API** -- real-time queries by state, county, operator,
   well name, API number, CAS number, date range, or bounding box
2. **Bulk CSV/SQL Download** -- full database dump (~430 MB zip), updated
   5 days per week

Use the API for targeted lookups. Use bulk download for large-scale analysis.

---

## API Structure

**Base URL:** `https://fracfocus.org/api/api`

### Reference Endpoints (GET, no parameters)

| Endpoint | Returns |
|----------|---------|
| `/state/states` | All states with numeric State_No and 2-letter Code |
| `/operator/operators` | All ~2,000 operator names |
| `/fracfocus/ingredients` | All ~22,000 ingredient names with CAS numbers |

### County Lookup (GET)

```
/state/countiesbystateid?stateid={State_No}
```

Uses numeric State_No (not abbreviation). Key values: WV=47, PA=37, OH=34,
TX=42, ND=33, OK=35, CO=5, NM=30, WY=49, LA=17, AR=3.

### Well Search (GET)

```
/fracfocus/search?{params}
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `state_name` | string | Full state name (e.g., "West Virginia") |
| `state_code` | int | Numeric State_No |
| `county_code` | int | Numeric county code |
| `operator_name` | string | Operator name (partial match) |
| `well_name` | string | Well name (partial match) |
| `api_number` | string | 14-digit API number (no dashes) |
| `start_date` | string | Job start date YYYY-MM-DD |
| `end_date` | string | Job end date YYYY-MM-DD |
| `cas_number` | string | CAS registry number |
| `ingredient_name` | string | Ingredient names (`$`-delimited for multiple) |
| `page` | int | Page number (1-based) |
| `pagesize` | int | Results per page (max 200) |

### Well Lookup by API Number (GET)

```
/FracFocus/WellByApiNumber?api14={14_digit_api}
```

Returns full disclosure with chemical ingredient data. API number must be
exactly 14 digits, zero-padded, no dashes. Example: `47033060270000`.

### Spatial Search (GET)

```
/fracfocus/wellsinbounds?north={lat}&south={lat}&east={lon}&west={lon}&page=1&pagesize=200&orderby=WellName
```

All parameters required. Coordinates in decimal degrees WGS84.

---

## Workflow

### Step 1 -- Resolve Intent

Map the user's question to the right query approach:

| User asks about... | Use this endpoint |
|---------------------|-------------------|
| Chemicals in a specific well | `/FracFocus/WellByApiNumber` |
| Wells in a state/county | `/fracfocus/search` with state_name + county_code |
| Wells by operator | `/fracfocus/search` with operator_name |
| Wells containing a chemical | `/fracfocus/search` with cas_number or ingredient_name |
| Wells near a location | `/fracfocus/wellsinbounds` |
| Wells in a date range | `/fracfocus/search` with start_date + end_date |
| Bulk analysis or statistics | Bulk CSV download |

If uncertain about state codes or county codes, query `/state/states` or
`/state/countiesbystateid` first.

### Step 2 -- Fetch Reference Data (when needed)

```bash
# Get state list to find State_No
curl -sk "https://fracfocus.org/api/api/state/states" | jq '.[] | select(.Code=="WV")'

# Get counties for WV (State_No = 47)
curl -sk "https://fracfocus.org/api/api/state/countiesbystateid?stateid=47" | jq '.'
```

### Step 3 -- Fetch Data

Build the query URL. Default behavior:
- Use `pagesize=200` (max allowed)
- Start with `page=1`; paginate if Count exceeds pagesize
- For specific well lookups, use the API number endpoint (returns ingredients)
- For broad searches, narrow with multiple filters to avoid null Wells response

**Search example:**
```bash
curl -sk "https://fracfocus.org/api/api/fracfocus/search?\
state_name=West+Virginia&\
well_name=Country+South&\
page=1&pagesize=10"
```

**Single well with ingredients:**
```bash
curl -sk "https://fracfocus.org/api/api/FracFocus/WellByApiNumber?\
api14=47033060270000"
```

**Spatial search:**
```bash
curl -sk "https://fracfocus.org/api/api/fracfocus/wellsinbounds?\
north=39.5&south=39.0&east=-79.5&west=-80.5&\
page=1&pagesize=200&orderby=WellName"
```

### Step 4 -- Parse Response

Well search response:
```json
{
  "Count": 5,
  "Page": 1,
  "PageSize": 10,
  "Wells": [
    {
      "WellName": "Country South 6MH",
      "APINumber": "47033060270000",
      "OperatorClean": "Diversified Production LLC",
      "StateName": "West Virginia",
      "CountyName": "Harrison",
      "JobEndDate": "5/28/2025 12:00:00 AM",
      "Latitude": 39.3501,
      "Longitude": -80.2101,
      "TVD": 7301.0,
      "TotalBaseWaterVolume": 36954775.0,
      "WellType": null,
      "Ingredients": [
        {
          "IngredientName": "Water",
          "CASNumber": "7732-18-5",
          "PercentHFJob": 86.57467,
          "MassIngredient": null
        }
      ]
    }
  ]
}
```

**Important parsing notes:**
- The API sometimes returns double-encoded JSON (a string containing JSON).
  Always check if the response is a string and parse again if needed.
- `Wells` may be `null` when the result set is very large. Narrow the search
  with additional filters.
- `Ingredients` is populated only on the WellByApiNumber endpoint, not on
  the search endpoint.
- Date formats vary: `"5/28/2025 12:00:00 AM"` (US format with time).
- `TotalBaseWaterVolume` is in gallons.
- `TVD` (True Vertical Depth) is in feet.

### Step 5 -- Produce Output

**Format: Well Summary Table + Chemical Table + Narrative**

Present well header data in a summary table, then chemical ingredients sorted
by percent of HF job (descending), then a narrative summary.

**Example output structure:**
```
## FracFocus Disclosure: Country South 6MH

| Field | Value |
|-------|-------|
| API Number | 47-033-06027-00-00 |
| Operator | Diversified Production LLC |
| County, State | Harrison, West Virginia |
| Coordinates | 39.3501, -80.2101 |
| Job Completed | 5/28/2025 |
| True Vertical Depth | 7,301 ft |
| Total Base Water Volume | 36,954,775 gal |

### Chemical Ingredients (21 records)

| Ingredient | CAS Number | % HF Job |
|------------|------------|----------|
| Water | 7732-18-5 | 86.575 |
| Crystalline silica, quartz | 14808-60-7 | 13.163 |
| Hydrochloric acid | 7647-01-0 | 0.117 |
| ... | ... | ... |

**Summary:** This Marcellus Shale well in Harrison County, WV used a
slickwater frac fluid composed of 86.6% water and 13.2% proppant (quartz
sand). The remaining 0.26% consists of friction reducers, scale inhibitors,
biocides, and clay stabilizers. Total water volume of 36.9 million gallons
indicates a large multi-stage horizontal completion at 7,301 ft TVD.

**Data quality:** Industry self-reported. 2 ingredients list CBI (trade
secret) claims.
```

---

## Bulk Data Download

For large-scale analysis (all wells in a basin, chemical usage trends, etc.),
download the full CSV:

```bash
# Download O&G CSV bulk data (~430 MB zip)
curl -Lk -o FracFocusCSV.zip \
  "https://www.fracfocusdata.org/digitaldownload/FracFocusCSV.zip"

# Non-O&G disclosures (geothermal, CCUS, hydrogen, etc.)
curl -Lk -o FracFocusNoOGCSV.zip \
  "https://www.fracfocusdata.org/digitaldownload/FracFocusNoOGCSV.zip"
```

Warn the user if they need bulk data -- the download is large and the
CSV requires local processing. For research-grade cleaned data, recommend
Open-FF (see Caveats section).

---

## Pagination

If `Count > pagesize`, paginate:

```python
page = 1
all_wells = []
while page * pagesize < total_count:
    result = search_wells(state_name="West Virginia", page=page, pagesize=200)
    if result["Wells"]:
        all_wells.extend(result["Wells"])
    page += 1
```

Warn the user if the dataset is very large (Count > 5000) and suggest
narrowing with additional filters.

---

## Error Handling

| HTTP Code | Meaning | Action |
|-----------|---------|--------|
| 200 + Wells=null | Result set too large | Narrow search with more filters |
| 400 | Bad parameter | Check parameter names and types; use numeric State_No for counties |
| 400 + validation error | Missing required field | Check required params (e.g., orderby for wellsinbounds) |
| 403 | Forbidden | Endpoint requires authentication (operator portal only) |
| 404 | Not found | Verify endpoint path; check API number is 14 digits |
| 500 | Server error | Check date format (YYYY-MM-DD); avoid state_code with date params |

---

## Caveats and Data Quality

### Industry Self-Reported Data

FracFocus data is **voluntarily disclosed by operators**. Key limitations:

1. **CBI Exemptions** -- Companies may claim Confidential Business Information
   (trade secret) to withhold chemical identities. CBI-claimed ingredients
   appear with `ClaimantCompany` populated but `CASNumber` may be absent.

2. **No Independent Verification** -- Chemical identities and concentrations
   are as-reported with no third-party lab confirmation.

3. **Incomplete Early Records** -- FracFocus 1.0 disclosures (Jan 2011 -
   May 2013) contain only header data, no chemical records.

4. **Data Corrections Without Audit Trail** -- Operators can update disclosures
   after submission. Changes are approved by state agencies but there is no
   public changelog.

5. **Voluntary in Most States** -- While many states require FracFocus
   reporting, the level of completeness varies by jurisdiction.

6. **PercentHFJob Precision** -- Reported percentages are often calculated from
   MSDS data, not direct measurement. Values below 0.001% may be unreliable.

### Research Alternatives

For peer-reviewed analysis, consider these cleaned versions of FracFocus data:

- **Open-FF** (https://github.com/gwallison/openFF-build) -- Calculates
  chemical mass, flags duplicates, consolidates name variants, cross-references
  EPA chemical lists. Best option for systematic analysis.

- **EPA Analysis** -- EPA has published multiple analyses of FracFocus data;
  search the EPA publications catalog for "hydraulic fracturing" reports.

### Coverage by State

Major producing states with the most disclosures: TX, CO, OK, ND, WY, NM,
PA, WV, OH, LA. Coverage varies -- check state-specific regulations for
reporting requirements.

---

## Implementation Notes

- **Use `bash_tool` with `curl -sk`** to make API requests (the `-k` flag is
  needed because FracFocus uses a certificate chain that may not be in all
  trust stores)
- **Use `jq` for JSON parsing** in bash pipelines
- **Python client** -- see `references/python_example.py` for a complete
  stdlib-only client with search, lookup, and bulk download
- **Double-encoded JSON** -- always check if the parsed response is a string
  and parse again; some endpoints wrap the JSON payload in quotes
- **API number format** -- always use 14 digits, no dashes, zero-padded
  (e.g., `47033060270000` not `47-033-06027`)
- **Large result sets** -- the search endpoint returns `Wells: null` when
  there are too many matches; this is by design, not an error; narrow the
  query
- **TotalBaseWaterVolume** is in gallons; divide by 42 for barrels
- **TVD** is in feet
- Updates: bulk data refreshed 5x/week; API reflects latest submissions
