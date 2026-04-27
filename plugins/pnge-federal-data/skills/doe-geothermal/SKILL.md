---
name: doe-geothermal
description: >
  Query and analyze U.S. geothermal resource data from the DOE Geothermal Data
  Repository (GDR), OpenEI geothermal resource areas database, and NREL Geothermal
  Prospector. Use this skill when the user asks about geothermal wells, heat flow,
  reservoir temperatures, geothermal capacity, co-production potential from oil and
  gas wells, hot brine resources, lithium recovery from geothermal fluids, direct-use
  geothermal, Enhanced Geothermal Systems (EGS), or geothermal gradient data. Trigger
  for phrases like "geothermal potential in West Virginia", "hot brines for lithium",
  "heat flow measurements", "geothermal co-production from oil wells", "reservoir
  temperature", "geothermal resource assessment", "geothermal capacity by state",
  "EGS resources", or any query about subsurface thermal energy. Produces data tables
  and narrative summaries with coordinates, temperatures, and capacity estimates.
---

# DOE Geothermal Data Skill

Fetches and analyzes U.S. geothermal resource data from multiple DOE/NREL sources:

1. **OpenEI Geothermal Resource Areas** -- Semantic MediaWiki API (432+ resource areas with coordinates, reservoir temperatures, capacities, and regional classifications)
2. **GDR (Geothermal Data Repository)** -- DOE GTO-funded datasets (well logs, temperature profiles, resource assessments, co-production studies)
3. **NREL Geothermal Prospector** -- Interactive maps and GIS layers for geothermal favorability

---

## API Key Handling

### OpenEI REST API (api.openei.org)

Resolution order (stop at first success):

1. **`~/.config/openei/credentials`** (default) -- parse `api_key=<value>` from this file
2. **`OPENEI_API_KEY` env var** -- fallback if credentials file is absent
3. **User-provided in conversation** -- fallback if neither above is set
4. **Prompt the user** -- "Please provide your OpenEI API key. Get one free at https://openei.org/services/api/signup/ -- or store it in `~/.config/openei/credentials` as `api_key=YOUR_KEY` (chmod 600)."

Never hardcode or log the key.

**Reading the credentials file (bash):**
```bash
KEY=$(grep '^api_key=' ~/.config/openei/credentials 2>/dev/null | cut -d= -f2)
[ -z "$KEY" ] && KEY="${OPENEI_API_KEY}"
if [ -z "$KEY" ]; then
    echo "No OpenEI API key found."
    echo "Get one free at https://openei.org/services/api/signup/"
    echo "Store in ~/.config/openei/credentials as api_key=YOUR_KEY"
    exit 1
fi
```

### OpenEI Semantic MediaWiki API (openei.org/w/api.php)

**No API key required.** This is the primary data source for geothermal resource areas. All queries are public and unauthenticated.

### GDR (gdr.openei.org)

**No API key required for browsing.** GDR does not expose a JSON REST API -- dataset discovery uses the web search interface and direct submission pages. Download links are publicly accessible.

---

## Data Sources and API Structure

### Source 1: OpenEI Semantic MediaWiki API (Primary)

**Base URL:** `https://openei.org/w/api.php`

This is the richest structured data source. It exposes 432+ geothermal resource areas as wiki pages with queryable semantic properties.

**Key categories:**
| Category | Description | Approx. Count |
|----------|-------------|---------------|
| `Geothermal Resource Areas` | Named geothermal areas with USGS assessments | 432+ |
| `Geothermal Regions` | Regional groupings (Basin and Range, Cascades, etc.) | ~20 |
| `Geothermal Projects` | DOE-funded project pages | ~100+ |
| `Geothermal Exploration Properties` | Exploration data types | ~50 |
| `Geothermal Low Temperature Direct Use Facilities` | Direct-use installations | ~30 |

**Key properties (verified against actual data):**
| Property | Type | Example Value |
|----------|------|---------------|
| `Coordinates` | Geographic | `{"lat": 39.6133, "lon": -112.7283}` |
| `USGSMeanReservoirTemp` | Number (Kelvin) | `363.15` (90C) |
| `USGSMeanCapacity` | String with unit | `"4 MW"` |
| `USGSEstReservoirVol` | String with unit | `"1.20 km3"` |
| `Place` | Wiki page ref | `"Utah"` |
| `GeothermalRegion` | Wiki page ref | `"Northern Basin and Range Geothermal Region"` |
| `GrossProdCapacity` | Number | `0` (most areas undeveloped) |
| `NetProdCapacity` | Number | `0` |
| `CSC-Status` | String | `"Available"` |
| `Name` | String | `"Abraham Hot Springs Geothermal Area"` |
| `BoundingCoordinatesNE` | String | `"39.8133,-112.5283"` |
| `BoundingCoordinatesSW` | String | `"39.4133,-112.9283"` |

**SMW Query syntax:**
```
action=ask
query=[[Category:Geothermal Resource Areas]][[Place::<STATE>]]
  |?Coordinates
  |?USGSMeanReservoirTemp
  |?USGSMeanCapacity
  |?USGSEstReservoirVol
  |?Place
  |?GeothermalRegion
  |limit=50
format=json
```

### Source 2: GDR (Geothermal Data Repository)

**Base URL:** `https://gdr.openei.org/`

The GDR stores DOE GTO-funded datasets. It does **not** have a public JSON API. Access patterns:

- **Search:** `https://gdr.openei.org/search?q=<QUERY>` (returns HTML)
- **Submission page:** `https://gdr.openei.org/submissions/<ID>` (returns HTML with download links)
- **File download:** Links within submission pages point to downloadable CSV/ZIP/Excel files

**Useful GDR searches for Li/Mg co-production research:**
- `co-production produced water`
- `lithium geothermal brine`
- `temperature depth well`
- `heat flow`
- `EGS stimulation`

### Source 3: NREL Geothermal Prospector

**Base URL:** `https://maps.nrel.gov/geothermal-prospector/`

Interactive GIS tool. No public REST API, but provides:
- Geothermal favorability maps (EGS, hydrothermal, low-temp)
- Temperature-at-depth layers (3.5 km, 4.5 km, 6.5 km, 10 km)
- Heat flow data overlays
- Existing plant and well locations

Use as a reference/visualization tool. Direct the user to the web interface for map exploration.

---

## Workflow

### Step 1 -- Resolve Intent

Map the user's question to a data source and query:

| User Intent | Source | Query Pattern |
|------------|--------|---------------|
| Geothermal areas in a state | OpenEI SMW | `[[Place::<State>]]` filter |
| Reservoir temperatures | OpenEI SMW | `?USGSMeanReservoirTemp` property |
| Capacity estimates | OpenEI SMW | `?USGSMeanCapacity` property |
| Dataset search (well logs, etc.) | GDR | Web search `gdr.openei.org/search?q=...` |
| Co-production from O&G wells | GDR + literature | Search for co-production datasets |
| Li from geothermal brines | GDR + OpenEI | Cross-reference with produced waters |
| Heat flow / gradient | OpenEI SMW + GDR | Exploration properties + datasets |
| Geothermal map visualization | NREL Prospector | Direct user to web tool |

### Step 2 -- Fetch Data (OpenEI SMW)

**Query all geothermal resource areas in a state:**
```bash
curl -s "https://openei.org/w/api.php" \
  --data-urlencode "action=ask" \
  --data-urlencode "query=[[Category:Geothermal Resource Areas]][[Place::West Virginia]]|?Coordinates|?USGSMeanReservoirTemp|?USGSMeanCapacity|?USGSEstReservoirVol|?GeothermalRegion|limit=50" \
  --data-urlencode "format=json"
```

**Query high-temperature resources (filter in post-processing):**
```bash
curl -s "https://openei.org/w/api.php" \
  --data-urlencode "action=ask" \
  --data-urlencode "query=[[Category:Geothermal Resource Areas]]|?Coordinates|?USGSMeanReservoirTemp|?USGSMeanCapacity|?Place|?GeothermalRegion|limit=500" \
  --data-urlencode "format=json"
```
Then filter locally for `USGSMeanReservoirTemp > threshold`.

**Browse a specific geothermal area's properties:**
```bash
curl -s "https://openei.org/w/api.php" \
  --data-urlencode "action=browsebysubject" \
  --data-urlencode "subject=Cove_Fort_Geothermal_Area" \
  --data-urlencode "format=json"
```

**List all geothermal categories:**
```bash
curl -s "https://openei.org/w/api.php?action=query&list=allcategories&acprefix=Geothermal&format=json&aclimit=50"
```

### Step 3 -- Fetch Data (GDR)

GDR dataset discovery requires scraping the search page or navigating directly to known submission IDs.

```bash
# Search for datasets (returns HTML -- parse for submission IDs and titles)
curl -sL "https://gdr.openei.org/search?q=lithium+geothermal+brine"

# Access a specific submission page
curl -sL "https://gdr.openei.org/submissions/1383"
```

Parse the HTML for:
- Submission title (in `<title>` tag)
- Download links (file URLs within the page)
- Tags/keywords (in labeled spans)

### Step 4 -- Parse Response (OpenEI SMW)

Response structure for `action=ask`:
```json
{
  "query": {
    "printrequests": [...],
    "results": {
      "Area Name": {
        "printouts": {
          "Coordinates": [{"lat": 39.6133, "lon": -112.7283}],
          "USGSMeanReservoirTemp": [363.15],
          "USGSMeanCapacity": ["4 MW"],
          "USGSEstReservoirVol": ["1.20 km3"],
          "Place": [{"fulltext": "Utah", "fullurl": "..."}],
          "GeothermalRegion": [{"fulltext": "Northern Basin and Range...", "fullurl": "..."}]
        },
        "fulltext": "Area Name",
        "fullurl": "https://openei.org/wiki/Area_Name"
      }
    },
    "serializer": "SMW\\Serializers\\QueryResultSerializer",
    "version": 2,
    "meta": {
      "count": 5,
      "offset": 0,
      "time": "0.026834"
    }
  },
  "query-continue-offset": 50
}
```

**Temperature note:** `USGSMeanReservoirTemp` is in **Kelvin**. Convert: `C = K - 273.15`.

**Pagination:** If `query-continue-offset` is present, issue another request with `|offset=<value>` appended to the query string.

### Step 5 -- Produce Output

**Format: Raw Data Table + Narrative**

Present a markdown table of relevant resource areas, then a narrative summary.

**Example output:**
```
## Geothermal Resource Areas in Utah

| Area | Lat | Lon | Reservoir Temp (C) | Capacity (MW) | Region |
|------|-----|-----|--------------------|---------------|--------|
| Cove Fort | 38.60 | -112.55 | 150.0 | 26 | Northern Basin and Range |
| Abraham Hot Springs | 39.61 | -112.73 | 90.0 | 4 | Northern Basin and Range |
| Joseph Hot Springs | 38.61 | -112.20 | 90.0 | 5 | Northern Basin and Range |

**Summary:** Utah has 3 identified geothermal resource areas in the USGS
assessment database, all located in the Northern Basin and Range region. Cove
Fort is the most significant with an estimated mean capacity of 26 MW and a
reservoir temperature of 150C (423 K), well above the threshold for
conventional flash-steam generation. Abraham Hot Springs and Joseph Hot Springs
are lower-temperature resources (90C) suitable for binary-cycle power or
direct-use applications.

**Co-production note:** For lithium recovery from geothermal brines, reservoir
temperatures above 100C are favorable as they correlate with higher TDS and
dissolved mineral concentrations. Cross-reference with USGS Produced Waters DB
for brine chemistry data.
```

---

## Pagination

OpenEI SMW supports pagination via `offset` in the query string:
```
|limit=50|offset=0     (first page)
|limit=50|offset=50    (second page)
```

Check for `query-continue-offset` in the response. If present, fetch the next page. Maximum limit per request is 500.

---

## Error Handling

| Condition | Meaning | Action |
|-----------|---------|--------|
| HTTP 200, empty results list | No matching areas for query | Broaden state/region filter or check spelling |
| HTTP 200, results is `[]` not `{}` | Zero results (SMW returns empty list) | Report no data found; suggest alternative query |
| HTTP 500 from openei.org | Server error | Retry once after 5 seconds |
| `query-continue-offset` present | More results available | Paginate with offset parameter |
| Property values empty `[]` | Data not available for this area | Note as "not assessed" in output |
| GDR returns HTML for API path | GDR has no JSON API | Use web search + parse HTML |
| OpenEI API key missing (for api.openei.org) | No key configured | Prompt user with signup URL |
| Timeout on openei.org | Server slow | Retry with smaller limit value |

---

## Temperature Conversion Reference

USGS reservoir temperatures in OpenEI are stored in **Kelvin**.

| Kelvin | Celsius | Fahrenheit | Significance |
|--------|---------|------------|-------------|
| 323.15 | 50 | 122 | Low-temp direct use threshold |
| 373.15 | 100 | 212 | Binary cycle power minimum |
| 423.15 | 150 | 302 | Flash steam viable |
| 473.15 | 200 | 392 | High-temp conventional |
| 523.15 | 250 | 482 | Excellent resource |
| 573.15 | 300 | 572 | Supercritical potential |

---

## Co-Production and Lithium Context

**Geothermal co-production** extracts energy from hot brines already flowing from oil and gas wells. Relevant connections:

- **Hot produced water** from deep O&G wells (particularly those below 3 km) often exceeds 100C
- **Direct Lithium Extraction (DLE)** is being piloted at geothermal plants (e.g., Salton Sea, CA)
- **Appalachian Basin** deep wells (Marcellus/Utica) produce waters at 50-90C -- marginal for power but viable for direct-use heating
- **Gulf Coast sedimentary basins** have geopressured brines at 150-200C with elevated Li concentrations

Cross-reference geothermal resource areas with:
1. `usgs-produced-waters` skill -- for brine chemistry (Li, Mg, TDS)
2. `wvges-wells` skill -- for WV well depths and formations
3. `eia-data` skill -- for current geothermal power generation statistics

---

## Geothermal Regions Reference

Major U.S. geothermal regions in the OpenEI database:

| Region | States | Characteristics |
|--------|--------|----------------|
| Northern Basin and Range | NV, UT, OR, ID | Extensional tectonics, high heat flow |
| Southern Basin and Range | AZ, NM, TX | Lower heat flow, some hot springs |
| Cascades | WA, OR, CA | Volcanic arc, high temp resources |
| Alaska | AK | Volcanic, remote, high potential |
| Great Basin | NV, UT | Highest concentration of resources |
| Imperial Valley / Salton Trough | CA | Extremely high temp, active Li extraction |
| Rio Grande Rift | NM, CO | Extensional, moderate resources |
| Snake River Plain | ID | Volcanic, moderate-high temp |
| Appalachian Basin | WV, PA, OH, NY | Low-temp, co-production potential only |

---

## Implementation Notes

- **Prefer `bash_tool` with `curl`** for OpenEI SMW queries -- no key needed, fast responses
- **URL-encode SMW queries** -- the `[[` and `]]` brackets must be encoded as `%5B%5B` and `%5D%5D`
- **Use `--data-urlencode` with curl** to handle encoding automatically
- **Python client** -- see `references/python_example.py` for a complete client with pagination
- **Temperature conversion** -- always convert Kelvin to Celsius in output tables
- **GDR is HTML-only** -- for dataset searches, parse the HTML or direct the user to the GDR web interface
- **Capacity values are strings** -- parse the numeric portion from values like `"26 MW"`
- **Place property is a page reference** -- extract `fulltext` field for the state/country name
- **OpenEI data is USGS 2008 assessment** -- note this in output as data may not reflect current conditions
- **Geothermal Prospector** at `https://maps.nrel.gov/geothermal-prospector/` is the best visualization tool -- direct users there for map-based exploration
