# FracFocus API Reference

FracFocus provides two data access methods: a public REST API used by the
"Find a Well" search at fracfocus.org, and bulk CSV/SQL downloads of the
full disclosure database. No API key is required for either method.

---

## 1. Public Search API

**Base URL:** `https://fracfocus.org/api/api`

All responses are JSON. Some endpoints return double-encoded JSON (a JSON
string containing JSON) -- parse accordingly.

### Reference Data Endpoints (GET)

| Endpoint | Description |
|----------|-------------|
| `/state/states` | All 51 states with State_No, Code, bounding box |
| `/state/countiesbystateid?stateid={State_No}` | Counties for a state (use numeric State_No, not abbreviation) |
| `/state/citiesbystateid?stateid={State_No}` | Cities for a state |
| `/operator/operators` | All ~2,000 operator names |
| `/fracfocus/ingredients` | All ~22,000 ingredient names |
| `/fracfocus/wellfinderstates` | States with active well finder data |

**State_No values (selected):**
| State | State_No | Code |
|-------|----------|------|
| West Virginia | 47 | WV |
| Pennsylvania | 37 | PA |
| Ohio | 34 | OH |
| Texas | 42 | TX |
| North Dakota | 33 | ND |
| Oklahoma | 35 | OK |
| Colorado | 5 | CO |
| New Mexico | 30 | NM |
| Wyoming | 49 | WY |
| Louisiana | 17 | LA |
| Arkansas | 3 | AR |

### Well Search Endpoint (GET)

```
GET /fracfocus/search?{params}
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `state_name` | string | Full state name (e.g., "West Virginia") |
| `state_code` | int | Numeric State_No from states endpoint |
| `county_code` | int | Numeric county code from counties endpoint |
| `operator_name` | string | Operator name (exact or partial) |
| `well_name` | string | Well name (partial match) |
| `api_number` | string | 14-digit API number |
| `start_date` | string | Job start date (YYYY-MM-DD) |
| `end_date` | string | Job end date (YYYY-MM-DD) |
| `cas_number` | string | CAS registry number |
| `ingredient_name` | string | Ingredient names, `$`-delimited for multiple |
| `page` | int | Page number (1-based) |
| `pagesize` | int | Results per page (default 200, max 200) |

**Response:**
```json
{
  "Count": 244236,
  "Page": 1,
  "PageSize": 200,
  "Wells": [
    {
      "pKey": "uuid-string",
      "WellName": "Country South 6MH",
      "PermitId": null,
      "JobStartDate": null,
      "APINumber": "47033060270000",
      "APINumber10": "4703306027",
      "OperatorClean": "Diversified Production LLC",
      "StateName": "West Virginia",
      "CountyName": "Harrison",
      "JobEndDate": "5/28/2025 12:00:00 AM",
      "Latitude": 39.3501,
      "Longitude": -80.2101,
      "FederalWell": "false",
      "IndianWell": "false",
      "WellType": null,
      "TotalBaseWaterVolume": 36954775.0,
      "TotalBaseNonWaterVolume": 0.0,
      "TVD": 7301.0,
      "Purposes": null,
      "Ingredients": null
    }
  ]
}
```

**Important:** When the result set is very large (e.g., all wells in a state),
the API may return `Wells: null` with only the `Count`. Narrow the search
with additional filters (date range, county, operator, well name) to get
actual well records.

### Well Lookup by API Number (GET)

```
GET /FracFocus/WellByApiNumber?api14={14_digit_api}
```

Returns full disclosure including chemical ingredients. The API number must
be exactly 14 characters (zero-padded). Example: `47033060270000`.

**Response includes all search fields plus populated `Ingredients` array.**

### Wells in Bounding Box (GET)

```
GET /fracfocus/wellsinbounds?north={lat}&south={lat}&east={lon}&west={lon}&page=1&pagesize=200&orderby=WellName
```

**Required parameters:** `north`, `south`, `east`, `west`, `page`, `pagesize`, `orderby`

**orderby values:** `WellName` (others may work but WellName is confirmed)

### Well Type Lookup (GET)

```
GET /FracFocus/WellTypeByApiNumber?api14={14_digit_api}
```

Returns `{ "wellType": "Oil" | "Gas" | "GEO" | "CVI" | ... }`.

---

## 2. Ingredient Data Schema

Each well disclosure contains an `Ingredients` array. Each ingredient record:

| Field | Type | Description |
|-------|------|-------------|
| `pKeyPurpose` | string (UUID) | Links ingredient to its purpose category |
| `pKey` | string | Record key |
| `Ingredient` | string | Combined "Name -- CAS" display string |
| `IngredientName` | string | Chemical name |
| `CASNumber` | string | CAS Registry Number (e.g., "7732-18-5") |
| `PercentHighAdditive` | float | Percent of additive (max reported) |
| `PercentHFJob` | float | Percent of total HF job fluid |
| `PercentHFJobString` | string | String representation of PercentHFJob |
| `IngredientComment` | string | Operator comments on ingredient |
| `roundedPercentHFJobString` | string | Rounded percent display |
| `IngredientMSDS` | bool | Whether MSDS data is available |
| `ThirdPartyCalc` | bool | Whether mass was calculated by third party |
| `MassIngredient` | float | Mass of ingredient in pounds (nullable) |
| `ClaimantCompany` | string | Company claiming trade secret (if CBI) |
| `ClaimantFirstName` | string | CBI claimant first name |
| `ClaimantLastName` | string | CBI claimant last name |
| `ClaimantEmail` | string | CBI claimant email |
| `ClaimantPhone` | string | CBI claimant phone |

**Common ingredients in hydraulic fracturing fluid:**
- Water (CAS 7732-18-5) -- typically 86-97% of HF fluid
- Crystalline silica / quartz (CAS 14808-60-7) -- proppant, 2-13%
- Hydrochloric acid (CAS 7647-01-0) -- acid stage
- Polyacrylamide (CAS 9003-05-8) -- friction reducer
- Guar gum (CAS 9000-30-0) -- gelling agent
- Ethylene glycol (CAS 107-21-1) -- scale inhibitor

---

## 3. Bulk Data Downloads

Full disclosure database available at:

| File | Format | URL |
|------|--------|-----|
| O&G SQL backup | MS SQL Server 2019 | `https://www.fracfocusdata.org/digitaldownload/fracfocusdata.zip` |
| Non-O&G SQL backup | MS SQL Server 2019 | `https://www.fracfocusdata.org/digitaldownload/FracFocusNoOGData.zip` |
| O&G CSV | CSV | `https://www.fracfocusdata.org/digitaldownload/FracFocusCSV.zip` |
| Non-O&G CSV | CSV | `https://www.fracfocusdata.org/digitaldownload/FracFocusNoOGCSV.zip` |

**Update frequency:** Updated 5 days per week with latest disclosures.

**Size:** The O&G CSV zip is approximately 430 MB.

**Limitations:**
- Disclosures from FracFocus 1.0 (Jan 2011 - May 2013) contain only header
  data (no chemical records).
- FracFocus 2.0-4.0 disclosures (Nov 2012 - present) contain both header
  and chemical data.
- Overlap period Nov 2012 - May 2013 has both 1.0 and 2.0 format submissions.

**SQL Database Tables:**
- **Registry** -- Header: well location, treatment date, base fluid volume
- **RegistryPurpose** -- Purpose categories for each additive
- **RegistryIngredient** -- Individual chemicals per purpose per disclosure
- **RegistryWaterSource** -- Water source information

---

## 4. Open-FF (Research Alternative)

Open-FF is an independent project that cleans and curates FracFocus bulk data
for research use.

**Repositories:**
- Build: https://github.com/gwallison/openFF-build
- Raw data: https://github.com/gwallison/openFF-raw
- Catalog: https://github.com/gwallison/openFF-catalog

**Online browser:** https://frackingchemicaldisclosure.wordpress.com/data-navigator/

**Key features over raw FracFocus data:**
- Calculates actual mass of chemicals used (where data permits)
- Flags and removes duplicate/problematic records
- Consolidates operator/supplier name variants
- Adds location quality flags
- Cross-references EPA chemical lists (CompTox, PFAS, IRIS)

**Records:** Over 6,000,000 chemical records across 175,000+ fracking events.

---

## 5. Well Types

| Code | Description |
|------|-------------|
| `Oil` | Oil well |
| `Gas` | Gas well |
| `BR` | Brine well |
| `CVI` | Class VI (CCUS) |
| `EPS` | Energy Pressure Storage |
| `GEO` | Geothermal |
| `H2` | Hydrogen Storage |

---

## 6. API Number Format

FracFocus uses the 14-digit API well number format:

```
SS-CCC-NNNNN-SS-SS
47-033-06027-00-00

SS    = State FIPS code (2 digits)
CCC   = County FIPS code (3 digits)
NNNNN = Unique well number (5 digits)
SS    = Sidetrack number (2 digits)
SS    = Completion number (2 digits)
```

The `APINumber10` field uses the first 10 digits (state + county + well).
The full `APINumber` field includes all 14 digits with dashes or zero-padded.

For API queries, use the 14-digit format without dashes: `47033060270000`.
