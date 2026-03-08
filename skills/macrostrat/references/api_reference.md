# Macrostrat API v2 — Reference

Base URL: `https://macrostrat.org/api/v2`

All requests require `format=json` unless you want CSV output.
All responses wrap data in `success.data` (array) or return `error.message`.

---

## Response Envelope

```json
{
  "success": {
    "v": 2,
    "data": [ ... ],
    "refs": { ... }
  }
}
```

On error:
```json
{
  "error": {
    "message": "No results found for your query."
  }
}
```

Always check for the `error` key before accessing `success.data`.

---

## /strat_names

Resolves stratigraphic unit names to canonical IDs and age ranges.
Use this first to get a `strat_name_id` for precise `/units` queries.

**Endpoint:** `GET /strat_names`

### Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `strat_name` | string | Exact name match | `strat_name=Marcellus` |
| `strat_name_like` | string | Substring/fuzzy match | `strat_name_like=marcell` |
| `strat_name_id` | integer | Look up by ID | `strat_name_id=1155` |
| `rank` | string | Filter by rank | `rank=Fm` |
| `concept_id` | integer | Filter by concept | — |
| `format` | string | `json` or `csv` | `format=json` |

**Rank codes:**

| Code | Meaning |
|------|---------|
| `Fm` | Formation |
| `Gp` | Group |
| `Mbr` | Member |
| `Ss` | Supersequence |
| `Bed` | Bed |
| `Sgp` | Supergroup |
| `Sbgp` | Subgroup |
| `Sbfm` | Subfomation |

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `strat_name_id` | int | Stable ID — use in `/units` for exact match |
| `strat_name` | string | Canonical unit name |
| `rank` | string | Rank code (Fm, Gp, Mbr…) |
| `concept_id` | int | Link to Macrostrat concept |
| `b_age` | float | Bottom (older) age in Ma |
| `t_age` | float | Top (younger) age in Ma |
| `b_period` | string | Period name at base |
| `t_period` | string | Period name at top |
| `c_interval` | string | Central time interval name |
| `usage_notes` | string | Compiler notes |
| `ref_id` | int | Source reference ID |

### Examples

```bash
# Exact formation match
curl -s "https://macrostrat.org/api/v2/strat_names?strat_name=Marcellus&rank=Fm&format=json" \
  | jq '.success.data[]'

# Fuzzy search — all units containing "utica"
curl -s "https://macrostrat.org/api/v2/strat_names?strat_name_like=utica&format=json" \
  | jq '.success.data[] | {strat_name_id, strat_name, rank, b_age, t_age}'

# Look up Smackover specifically
curl -s "https://macrostrat.org/api/v2/strat_names?strat_name=Smackover&rank=Fm&format=json" \
  | jq '.success.data'
```

---

## /units

Returns rock unit properties including age, lithology, thickness, environment,
and fossil collections. This is the primary endpoint for formation data.

**Endpoint:** `GET /units`

### Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `strat_name` | string | Match by name (exact) | `strat_name=Marcellus` |
| `strat_name_like` | string | Fuzzy name match | `strat_name_like=marcell` |
| `strat_name_id` | integer | Match by canonical ID (precise) | `strat_name_id=1155` |
| `unit_id` | integer | Single unit by ID | `unit_id=4631` |
| `col_id` | integer | All units in a column | `col_id=187` |
| `section_id` | integer | Units in a section | — |
| `age` | string | Filter by age name | `age=Givetian` |
| `age_top` | float | Top age bound (Ma) | `age_top=380` |
| `age_bottom` | float | Bottom age bound (Ma) | `age_bottom=400` |
| `environ` | string | Filter by environment name | `environ=marine+shelf` |
| `environ_class` | string | Filter by environment class | `environ_class=marine` |
| `lith` | string | Filter by lithology type | `lith=shale` |
| `lith_class` | string | Filter by lith class | `lith_class=sedimentary` |
| `project_id` | integer | Filter by Macrostrat project | — |
| `response` | string | `short` (default) or `long` | `response=long` |
| `order` | string | Sort field | `order=b_age` |
| `format` | string | `json` or `csv` | `format=json` |

**Always use `response=long`** to get `lith` and `environ` arrays.
`response=short` omits lithology, environment, and fossil data.

### Response Fields (response=long)

| Field | Type | Description |
|-------|------|-------------|
| `unit_id` | int | Unique unit identifier |
| `unit_name` | string | Name as used in this column |
| `strat_name` | string | Canonical stratigraphic name |
| `strat_name_id` | int | Canonical ID |
| `col_id` | int | Column this unit belongs to |
| `col_area` | float | Column area (km²) |
| `section_id` | int | Section within column |
| `project_id` | int | Macrostrat project |
| `t_age` | float | Top age in Ma (younger bound) |
| `b_age` | float | Base age in Ma (older bound) |
| `age` | string | Age stage name (e.g., "Givetian") |
| `max_thick` | float | Max thickness in meters |
| `min_thick` | float | Min thickness in meters |
| `color` | string | Display color (hex) |
| `lith` | array | Lithology objects (see below) |
| `environ` | array | Environment objects (see below) |
| `pbdb_collections` | int | Paleobiology DB fossil collection count |
| `pbdb_occs` | int | Paleobiology DB occurrence count |
| `refs` | array | Source references |
| `notes` | string | Free-text compiler notes |
| `clat` | float | Representative column latitude |
| `clng` | float | Representative column longitude |

### lith Array Object Fields

| Field | Description | Example values |
|-------|-------------|----------------|
| `name` | Rock type name | "black shale", "limestone" |
| `type` | Broad lithology type | "shale", "carbonate", "sandstone" |
| `class` | Lithology class | "sedimentary", "igneous", "metamorphic" |
| `color` | Color description | "black", "gray", "tan" |
| `grain_size` | Grain size | "clay", "silt", "sand", "gravel" |
| `prop` | Proportion (0–1) | 0.8 |
| `lith_id` | Internal lith ID | — |

### environ Array Object Fields

| Field | Description | Example values |
|-------|-------------|----------------|
| `name` | Environment name | "marine shelf", "fluvial", "deltaic" |
| `class` | Broad class | "marine", "non-marine", "transitional" |
| `type` | Sub-type | "shelf", "deepwater", "lacustrine" |
| `environ_id` | Internal ID | — |

### Examples

```bash
# Full long response for Marcellus by name
curl -s "https://macrostrat.org/api/v2/units?strat_name=Marcellus&response=long&format=json" \
  | jq '.success.data[] | {unit_id, unit_name, col_id, t_age, b_age, max_thick, min_thick}'

# Using strat_name_id for precise match (avoid synonyms)
curl -s "https://macrostrat.org/api/v2/units?strat_name_id=1155&response=long&format=json" \
  | jq '.success.data[0]'

# Units in column 187 (Appalachian WV area), sorted by age
curl -s "https://macrostrat.org/api/v2/units?col_id=187&response=long&order=b_age&format=json" \
  | jq '.success.data[] | {unit_name, t_age, b_age, age}'

# Filter to only Devonian units
curl -s "https://macrostrat.org/api/v2/units?col_id=187&age_top=358&age_bottom=419&response=long&format=json" \
  | jq '.success.data[] | {unit_name, b_age, t_age, max_thick}'

# Filter to marine environments only
curl -s "https://macrostrat.org/api/v2/units?col_id=187&environ_class=marine&response=long&format=json"

# All shale units in a column
curl -s "https://macrostrat.org/api/v2/units?col_id=187&lith=shale&response=long&format=json"
```

### Go Example: Filter Units by Age Range

```go
package main

import (
    "encoding/json"
    "fmt"
    "io"
    "net/http"
    "net/url"
    "strconv"
)

type LithEntry struct {
    Name      string  `json:"name"`
    Type      string  `json:"type"`
    Class     string  `json:"class"`
    Color     string  `json:"color"`
    GrainSize string  `json:"grain_size"`
    Prop      float64 `json:"prop"`
}

type EnvironEntry struct {
    Name    string `json:"name"`
    Class   string `json:"class"`
    Type    string `json:"type"`
}

type Unit struct {
    UnitID      int            `json:"unit_id"`
    UnitName    string         `json:"unit_name"`
    StratName   string         `json:"strat_name"`
    ColID       int            `json:"col_id"`
    TAGe        float64        `json:"t_age"`
    BAge        float64        `json:"b_age"`
    Age         string         `json:"age"`
    MaxThick    float64        `json:"max_thick"`
    MinThick    float64        `json:"min_thick"`
    Lith        []LithEntry    `json:"lith"`
    Environ     []EnvironEntry `json:"environ"`
    PBDBColls   int            `json:"pbdb_collections"`
    Notes       string         `json:"notes"`
}

type MacrostratResponse struct {
    Success struct {
        Data []Unit `json:"data"`
    } `json:"success"`
    Error *struct {
        Message string `json:"message"`
    } `json:"error"`
}

func fetchUnits(colID int, ageTop, ageBottom float64) ([]Unit, error) {
    params := url.Values{}
    params.Set("col_id", strconv.Itoa(colID))
    params.Set("age_top", fmt.Sprintf("%.1f", ageTop))
    params.Set("age_bottom", fmt.Sprintf("%.1f", ageBottom))
    params.Set("response", "long")
    params.Set("format", "json")

    apiURL := "https://macrostrat.org/api/v2/units?" + params.Encode()

    resp, err := http.Get(apiURL)
    if err != nil {
        return nil, fmt.Errorf("HTTP request failed: %w", err)
    }
    defer resp.Body.Close()

    body, err := io.ReadAll(resp.Body)
    if err != nil {
        return nil, fmt.Errorf("reading response: %w", err)
    }

    var result MacrostratResponse
    if err := json.Unmarshal(body, &result); err != nil {
        return nil, fmt.Errorf("parsing JSON: %w", err)
    }

    if result.Error != nil {
        return nil, fmt.Errorf("Macrostrat error: %s", result.Error.Message)
    }

    return result.Success.Data, nil
}

func main() {
    // Devonian units (419.2–358.9 Ma) in column 187
    units, err := fetchUnits(187, 358.9, 419.2)
    if err != nil {
        fmt.Printf("Error: %v\n", err)
        return
    }

    fmt.Printf("%-30s %8s %8s %8s %8s  %-20s\n",
        "Unit Name", "T_Age", "B_Age", "MaxThk", "MinThk", "Environment")
    fmt.Println(fmt.Sprintf("%s", "--------------------------------------------------------------------------------"))

    for _, u := range units {
        env := "unknown"
        if len(u.Environ) > 0 {
            env = u.Environ[0].Name
        }
        fmt.Printf("%-30s %8.1f %8.1f %8.0f %8.0f  %-20s\n",
            u.UnitName, u.TAGe, u.BAge, u.MaxThick, u.MinThick, env)
    }
}
```

---

## /columns

Returns stratigraphic column metadata. Use to find column IDs near a location,
then use the `col_id` in `/units` queries.

**Endpoint:** `GET /columns`

### Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `lat` | float | Latitude (decimal degrees) | `lat=39.63` |
| `lng` | float | Longitude (decimal degrees) | `lng=-79.95` |
| `adjacent` | boolean | Include adjacent columns | `adjacent=true` |
| `col_id` | integer | Single column by ID | `col_id=187` |
| `col_group_id` | integer | Columns in a group | — |
| `project_id` | integer | Columns in a project | — |
| `status_code` | string | `active` or `in process` | `status_code=active` |
| `format` | string | `json` or `csv` | `format=json` |

### Response Fields

| Field | Description |
|-------|-------------|
| `col_id` | Column identifier |
| `col_name` | Column name |
| `lat` | Representative latitude |
| `lng` | Representative longitude |
| `col_area` | Column area (km²) |
| `max_thick` | Maximum stratigraphic thickness (m) |
| `min_thick` | Minimum thickness (m) |
| `pbdb_collections` | Total PBDB collections |
| `t_age` | Youngest age in column (Ma) |
| `b_age` | Oldest age in column (Ma) |
| `col_group` | Group name |
| `col_group_id` | Group ID |
| `project_id` | Project ID |
| `status_code` | active / in process |

### Examples

```bash
# Find columns near Morgantown WV
curl -s "https://macrostrat.org/api/v2/columns?lat=39.63&lng=-79.95&format=json" \
  | jq '.success.data[] | {col_id, col_name, lat, lng, col_area}'

# Find columns including adjacent ones
curl -s "https://macrostrat.org/api/v2/columns?lat=39.63&lng=-79.95&adjacent=true&format=json" \
  | jq '.success.data[] | {col_id, col_name}'

# Get full column metadata for a specific column
curl -s "https://macrostrat.org/api/v2/columns?col_id=187&format=json"
```

---

## /fossils

Returns Paleobiology Database fossil collections associated with a stratigraphic unit.

**Endpoint:** `GET /fossils`

### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `strat_name` | string | Formation name |
| `strat_name_id` | integer | Canonical ID |
| `col_id` | integer | Column filter |
| `age_top` | float | Age filter (Ma) |
| `age_bottom` | float | Age filter (Ma) |
| `format` | string | `json` |

### Examples

```bash
# Fossil collections in the Marcellus
curl -s "https://macrostrat.org/api/v2/fossils?strat_name=Marcellus&format=json" \
  | jq '.success.data[] | {cltn_id, cltn_name, lat, lng, n_occs}'
```

---

## /sections

Returns package/section groupings within a column. Sections represent
unconformity-bounded sequences.

**Endpoint:** `GET /sections`

### Parameters

| Parameter | Description |
|-----------|-------------|
| `col_id` | Column ID |
| `section_id` | Specific section |
| `format` | `json` |

### Examples

```bash
# All sections in a column
curl -s "https://macrostrat.org/api/v2/sections?col_id=187&format=json" \
  | jq '.success.data[] | {section_id, col_id, t_age, b_age, max_thick}'
```

---

## /intervals

Returns geologic time interval definitions from the International
Chronostratigraphic Chart.

**Endpoint:** `GET /intervals`

### Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `name` | Interval name | `name=Devonian` |
| `timescale_id` | Timescale filter | — |
| `age_top` | Top age (Ma) | — |
| `age_bottom` | Bottom age (Ma) | — |
| `format` | `json` | — |

### Examples

```bash
# Get age bounds for the Devonian period
curl -s "https://macrostrat.org/api/v2/intervals?name=Devonian&format=json" \
  | jq '.success.data[] | {int_id, name, t_age, b_age, color}'

# List all Devonian stages
curl -s "https://macrostrat.org/api/v2/intervals?age_top=358.9&age_bottom=419.2&format=json" \
  | jq '.success.data[] | {name, t_age, b_age}'
```

---

## Pagination

Macrostrat API v2 does not use cursor-based pagination. Results are returned
in a single response. For very large column queries, use `age_top`/`age_bottom`
to narrow the window, or filter by `lith_class` or `environ_class`.

There is no `limit` or `offset` parameter on most endpoints. If you need
a subset, filter client-side from the full response.

---

## Rate Limits and Polite Use

- No API key required
- No documented rate limit, but avoid hammering the API
- If you receive HTTP 429, wait 10 seconds before retrying
- For batch queries (e.g., many column IDs), space requests 200ms apart
- The API is maintained by an academic research group; be a considerate user

---

## Common Column IDs (Appalachian/PNGE Context)

These column IDs are illustrative; always verify with a `/columns?lat=&lng=` query:

| Region | Approx col_id | Notes |
|--------|--------------|-------|
| Central WV (Morgantown area) | 187 | Primary Marcellus study area |
| SW PA (Pittsburgh area) | varies | Marcellus, Utica |
| Northern Appalachian | varies | Deep Ordovician targets |

Use the `/columns` endpoint with actual lat/lng for authoritative column IDs.

---

## Geologic Time Scale Reference (Selected Periods)

| Period | Top Age (Ma) | Base Age (Ma) |
|--------|-------------|--------------|
| Quaternary | 0 | 2.58 |
| Neogene | 2.58 | 23.03 |
| Paleogene | 23.03 | 66.0 |
| Cretaceous | 66.0 | 145.0 |
| Jurassic | 145.0 | 201.4 |
| Triassic | 201.4 | 251.9 |
| Permian | 251.9 | 298.9 |
| Carboniferous | 298.9 | 358.9 |
| Devonian | 358.9 | 419.2 |
| Silurian | 419.2 | 443.8 |
| Ordovician | 443.8 | 485.4 |
| Cambrian | 485.4 | 538.8 |

Use these bounds with `age_top`/`age_bottom` parameters to filter by period.
