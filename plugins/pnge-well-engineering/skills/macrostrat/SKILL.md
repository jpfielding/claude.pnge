---
name: macrostrat
description: >
  Query the Macrostrat geological database for stratigraphic columns, formation
  ages, lithology, thickness ranges, and depositional environment context. Use
  this skill when the user asks about the geological age of a formation,
  stratigraphic position, rock types, formation thickness, depositional setting,
  or needs to place a formation in its stratigraphic context. Trigger for phrases
  like "what age is the Marcellus Shale", "stratigraphy of the Appalachian basin",
  "what formations are above the Utica", "depositional environment of the
  Smackover", "formation thickness in West Virginia", "stratigraphic column for
  Ohio", or any request for geological formation context, rock unit properties,
  or basin stratigraphy. Covers all named geological units in North America and
  globally. Produces formatted stratigraphic tables with age, lithology,
  thickness, and environment data.
---

# Macrostrat Geological Database Skill

Fetches stratigraphic, lithological, and age data from Macrostrat — a
compilation of geological map and literature data maintained by the
University of Wisconsin-Madison (Shanan Peters et al.).

---

## API Key Handling

No API key required. The Macrostrat API v2 is fully public.

---

## Data Sources and API Structure

**Base URL:** `https://macrostrat.org/api/v2`

### Key Endpoints

| Endpoint | What It Returns |
|----------|----------------|
| `/strat_names` | Canonical stratigraphic unit names and ranks |
| `/units` | Rock unit properties: age, lithology, thickness, environment |
| `/columns` | Stratigraphic columns by location or region |
| `/fossils` | Paleobiology database collections within a unit |
| `/sections` | Package/section data within a column |
| `/intervals` | Geologic time interval definitions |

---

## Workflow

### Step 1 — Resolve Intent

| User Intent | Endpoint | Key Parameters |
|------------|----------|----------------|
| Formation age/properties by name | `/units` + `/strat_names` | `strat_name=Marcellus`, `response=long` |
| Fuzzy name search | `/units` | `strat_name_like=marcellus` |
| Stratigraphic column at a location | `/columns` | `lat=39.5&lng=-80.0` |
| Formations above/below a unit | `/units` | cross-reference `t_age`/`b_age` |
| Depositional environment | `/units` | `environ_class=marine` filter |

### Step 2 — Fetch Stratigraphic Names

First resolve the canonical strat name and its ID:

```bash
curl -s "https://macrostrat.org/api/v2/strat_names?strat_name=Marcellus&rank=Fm&format=json" \
  | jq '.success.data[] | {strat_name_id, strat_name, rank, b_age, t_age}'
```

Response fields:
- `strat_name_id` — use this in /units queries for precise matching
- `rank` — Fm (Formation), Gp (Group), Mbr (Member), Ss (Supersequence)
- `b_age`, `t_age` — bottom and top age in Ma

### Step 3 — Fetch Unit Properties

```bash
# By exact strat_name_id (most precise)
curl -s "https://macrostrat.org/api/v2/units?strat_name_id=XXXX&response=long&format=json"

# By name (may return multiple matching units in different basins)
curl -s "https://macrostrat.org/api/v2/units?strat_name=Marcellus&response=long&format=json" \
  | jq '.success.data[]'

# Fuzzy search across all units containing "marcellus"
curl -s "https://macrostrat.org/api/v2/units?strat_name_like=marcellus&format=json"
```

**Response fields (response=long):**
```json
{
  "unit_id": 4631,
  "unit_name": "Marcellus Shale",
  "strat_name": "Marcellus",
  "strat_name_id": 1155,
  "col_id": 187,
  "col_area": 43215.2,
  "t_age": 385.3,
  "b_age": 391.9,
  "age": "Givetian",
  "max_thick": 200,
  "min_thick": 0,
  "color": "#9C6D57",
  "lith": [
    {"type": "shale", "class": "sedimentary", "color": "black", "grain_size": "clay"}
  ],
  "environ": [
    {"name": "marine shelf", "class": "marine", "type": "shelf"}
  ],
  "pbdb_collections": 47,
  "refs": [{"ref_id": 123, "pub_yr": 2012}]
}
```

### Step 4 — Stratigraphic Column by Location

```bash
# Get columns near Morgantown WV (lat 39.63, lon -79.96)
curl -s "https://macrostrat.org/api/v2/columns?lat=39.63&lng=-79.96&format=json" \
  | jq '.success.data[]'

# Get all units in a specific column (col_id from above)
curl -s "https://macrostrat.org/api/v2/units?col_id=187&response=long&format=json"
```

### Step 5 — Parse and Output

Extract from the `lith` array (may have multiple lithologies):
- `type` — primary rock type (shale, limestone, sandstone, etc.)
- `class` — sedimentary / igneous / metamorphic
- `color` — described color
- `grain_size` — clay/silt/sand/gravel

Extract from `environ` array:
- `name` — named environment (e.g., "marine shelf", "deltaic")
- `class` — marine / non-marine / transitional
- `type` — sub-classification

---

## Output Format

### Formation Properties Table

```
## Stratigraphic Profile: Marcellus Shale

| Property | Value |
|----------|-------|
| Canonical Name | Marcellus Formation |
| Rank | Formation (Fm) |
| Age Range | Givetian (391.9 – 385.3 Ma) |
| Period | Devonian (Middle) |
| Max Thickness | 200 m |
| Min Thickness | 0 m |
| Primary Lithology | Black shale (clay-grade) |
| Depositional Environment | Marine shelf |
| PBDB Collections | 47 |

**Narrative:** The Marcellus Shale is a Middle Devonian (Givetian stage,
~391–385 Ma) organic-rich black shale deposited in a restricted marine shelf
environment in the Appalachian foreland basin. Thickness ranges from 0 at its
western pinchout to >200 m in Pennsylvania. It is the primary natural gas
reservoir in the Appalachian basin, producing from the Morgantown and
Pittsburgh super-platforms.

**Data source:** Macrostrat v2 (Peters et al., UW-Madison).
Data reflects published literature compilations; site-specific measurements
may differ from these compiled ranges.
```

---

## Error Handling

| Condition | Meaning | Action |
|-----------|---------|--------|
| `success.data` is empty array | No units match the query | Try `strat_name_like` for fuzzy match |
| HTTP 404 | Endpoint not found | Check base URL and endpoint spelling |
| HTTP 429 | Rate limited | Wait 5 seconds and retry with smaller limit |
| `lith` array empty | Lithology not characterized | Report "lithology not yet assigned in Macrostrat" |
| `environ` array empty | Environment not characterized | Report "depositional environment not catalogued" |
| Multiple units returned | Formation spans multiple columns | Present all results grouped by `col_id`/region |
| `max_thick` = 0 and `min_thick` = 0 | Thickness not reported | Report "thickness data not available for this unit" |

---

## Age Reference for Common PNGE Formations

| Formation | Age | Period | Basin |
|-----------|-----|--------|-------|
| Marcellus | Givetian (~391–385 Ma) | Devonian | Appalachian |
| Utica | Katian (~455–445 Ma) | Ordovician | Appalachian |
| Point Pleasant | Katian (~455–445 Ma) | Ordovician | Appalachian |
| Smackover | Oxfordian (~163–157 Ma) | Jurassic | Gulf Coast |
| Bakken | Famennian (~372–359 Ma) | Devonian | Williston |
| Eagle Ford | Cenomanian–Turonian (~99–89 Ma) | Cretaceous | Gulf Coast |
| Wolfcamp | Wolfcampian (~299–272 Ma) | Permian | Permian Basin |
| Tuscaloosa Marine | Cenomanian (~100–94 Ma) | Cretaceous | Gulf Coast |

---

## Caveats

- Macrostrat thickness values are compiled from the published literature
  and geological map databases. They represent regional ranges, not
  site-specific measurements.
- Age assignments reflect the International Chronostratigraphic Chart
  as calibrated in Macrostrat; small discrepancies vs. other sources are
  possible due to different time scale versions.
- Not all formations have complete lithology and environment data — older
  or less-studied units may have sparse properties.
- The database is continuously updated; query results may change over time
  as new literature is incorporated.
- For site-specific subsurface properties, cross-reference with
  `pnge-state-regulatory:wvges-wells` or `pnge-core:usgs-produced-waters` data.
