---
name: nasa-earthdata
description: >
  Search and discover satellite imagery and Earth observation datasets from
  NASA Earthdata Common Metadata Repository (CMR). Use when the user asks
  about satellite imagery near well sites, remote sensing for oil and gas,
  Landsat or Sentinel data, land use change near drilling pads, thermal
  anomaly mapping near flares or produced water ponds, or any Earth
  observation data for petroleum engineering. Trigger phrases: "Landsat
  imagery for my well site", "satellite data near Morgantown WV",
  "Sentinel-2 Marcellus Shale", "thermal anomaly near flare", "land use
  change drilling pad", "remote sensing produced water", "MODIS thermal
  gas flares", "satellite monitoring well pads", "Earth observation
  oilfield". Produces collection and granule tables with spatial metadata.
---

# NASA Earthdata CMR Skill

Searches and discovers satellite imagery and Earth observation datasets from
NASA's Common Metadata Repository (CMR). CMR indexes metadata for 50,000+
collections across all NASA DAACs (Distributed Active Archive Centers).
Focused on collections relevant to petroleum engineering: Landsat 8/9,
Sentinel-2, MODIS thermal, and land cover datasets.

## API Key Handling

**No API key required for search and discovery.** The CMR search API is
fully public. Downloading actual granule data files requires a free NASA
Earthdata Login account.

**For data download (not search):**

Resolution order (stop at first success):

1. **`~/.netrc`** -- check for `machine urs.earthdata.nasa.gov` entry
2. **`EARTHDATA_USERNAME` + `EARTHDATA_PASSWORD` env vars** -- fallback
3. **Prompt the user** -- "Downloading granule data requires a free NASA
   Earthdata Login. Sign up at https://urs.earthdata.nasa.gov/users/new
   -- then add to `~/.netrc`:
   `machine urs.earthdata.nasa.gov login YOUR_USER password YOUR_PASS`
   (chmod 600)."

Never hardcode or log credentials. For search operations, no auth is needed.

**Checking for Earthdata credentials (bash):**
```bash
# Only needed for downloads, not for CMR search
if grep -q 'machine urs.earthdata.nasa.gov' ~/.netrc 2>/dev/null; then
    echo "Earthdata credentials found in ~/.netrc"
else
    echo "No Earthdata credentials. Sign up free at https://urs.earthdata.nasa.gov/users/new"
    echo "Add to ~/.netrc: machine urs.earthdata.nasa.gov login YOUR_USER password YOUR_PASS"
fi
```

---

## API Structure

**Base URL:** `https://cmr.earthdata.nasa.gov/search/`

CMR provides two main search targets: **collections** (datasets) and
**granules** (individual files/scenes within a collection).

### Endpoints

| Endpoint | Purpose |
|----------|---------|
| `/search/collections.json` | Search dataset collections by keyword, platform, spatial, temporal |
| `/search/granules.json` | Search individual scenes/files within a collection |
| `/search/collections.umm_json` | Collection search with full UMM-C metadata |
| `/search/granules.umm_json` | Granule search with full UMM-G metadata |

### Common Parameters (all endpoints)

| Parameter | Example | Notes |
|-----------|---------|-------|
| `keyword` | `keyword=landsat` | Free-text keyword search |
| `short_name` | `short_name=LANDSAT_OT_C2_L2` | Exact collection short name |
| `platform` | `platform=LANDSAT-8` | Satellite platform filter |
| `instrument` | `instrument=OLI` | Instrument filter |
| `bounding_box` | `bounding_box=-80.5,39.5,-79.5,40.0` | W,S,E,N decimal degrees |
| `point` | `point=-79.9561,39.6295` | Lon,Lat single point |
| `temporal` | `temporal=2024-01-01T00:00:00Z,2024-12-31T23:59:59Z` | ISO 8601 range |
| `cloud_cover` | `cloud_cover=0,20` | Min,max cloud cover percent (granules only) |
| `page_size` | `page_size=20` | Results per page (max 2000) |
| `page_num` | `page_num=1` | Page number (1-indexed) |
| `sort_key` | `sort_key=-start_date` | Sort field; prefix `-` for descending |
| `provider` | `provider=LPCLOUD` | Filter by data provider/DAAC |

### Collection-Specific Parameters

| Parameter | Example | Notes |
|-----------|---------|-------|
| `science_keywords` | `science_keywords=LAND+SURFACE` | NASA GCMD keyword hierarchy |
| `processing_level_id` | `processing_level_id=2` | Processing level (1, 2, 3, etc.) |
| `has_granules` | `has_granules=true` | Only collections with data |

### Granule-Specific Parameters

| Parameter | Example | Notes |
|-----------|---------|-------|
| `collection_concept_id` | `collection_concept_id=C2021957657-LPCLOUD` | Required: parent collection |
| `day_night_flag` | `day_night_flag=day` | Day, night, or both |
| `cloud_cover` | `cloud_cover=0,30` | Cloud cover range percent |
| `readable_granule_name` | `readable_granule_name=*039032*` | Wildcard match on granule name |

---

## Key Collections for PNGE Research

### Landsat (Surface Reflectance + Thermal)

| Short Name | Collection | Resolution | Revisit |
|------------|-----------|------------|---------|
| `LANDSAT_OT_C2_L2` | Landsat 8/9 OLI/TIRS C2 L2 | 30m (optical), 100m (thermal) | 8 days |
| `LANDSAT_OT_C2_L1` | Landsat 8/9 OLI/TIRS C2 L1 | 30m / 100m | 8 days |
| `LANDSAT_ETM_C2_L2` | Landsat 7 ETM+ C2 L2 | 30m | 16 days |

**Use for:** Land use change detection near well pads, vegetation stress
(NDVI), thermal mapping of produced water impoundments and flare stacks.

### Sentinel-2 (via LPCLOUD)

| Short Name | Collection | Resolution | Revisit |
|------------|-----------|------------|---------|
| `HLSS30` | Harmonized Landsat Sentinel-2 (HLS S30) | 30m | 2-3 days |
| `HLSL30` | Harmonized Landsat Sentinel-2 (HLS L30) | 30m | 2-3 days |

**Use for:** Higher temporal resolution monitoring of well pad construction,
pipeline right-of-way clearing, reclamation progress.

### MODIS Thermal

| Short Name | Collection | Resolution | Revisit |
|------------|-----------|------------|---------|
| `MOD14` | MODIS/Terra Thermal Anomalies/Fire | 1km | Daily |
| `MYD14` | MODIS/Aqua Thermal Anomalies/Fire | 1km | Daily |
| `MOD11A1` | MODIS/Terra Land Surface Temp Daily | 1km | Daily |
| `VNP14IMG` | VIIRS/NPP Thermal Anomalies/Fire | 375m | Daily |

**Use for:** Gas flare detection, thermal anomaly mapping near surface
facilities, produced water pond temperature monitoring.

### Land Cover and Change

| Short Name | Collection | Resolution | Update |
|------------|-----------|------------|--------|
| `MCD12Q1` | MODIS Land Cover Type | 500m | Annual |
| `MCD64A1` | MODIS Burned Area | 500m | Monthly |

---

## Workflow

### Step 1 -- Resolve Intent

Map the user's question to search strategy:

| User Wants | Strategy |
|-----------|----------|
| Find imagery for a location | Collection search with bounding_box, then granule search |
| Browse available datasets | Collection search with keyword |
| Specific scenes with low cloud cover | Granule search with cloud_cover + temporal |
| Thermal anomaly data | Search MOD14/VNP14IMG collections, then granules |
| Land use change | Search Landsat/HLS collections for time series |

Determine the bounding box from the user's area of interest. For well-site
monitoring, use a small box (0.1-0.5 degrees). For basin-scale analysis,
use a larger box (1-3 degrees).

**Common Appalachian Basin bounding boxes:**
- Monongalia County, WV: `-80.1,39.5,-79.6,39.8`
- Northern WV Marcellus: `-80.8,39.2,-79.5,40.0`
- Entire Marcellus Shale play: `-82.0,37.5,-74.5,42.5`

### Step 2 -- Search Collections

Find relevant collections for the user's area and time of interest:

```bash
# Find Landsat collections with granules in northern WV
curl -s "https://cmr.earthdata.nasa.gov/search/collections.json?\
keyword=landsat+level-2&\
bounding_box=-80.5,39.5,-79.5,40.0&\
has_granules=true&\
page_size=10"
```

Parse the response to get `concept_id` values for granule search.

### Step 3 -- Search Granules

Use the collection concept_id to find specific scenes:

```bash
# Find recent low-cloud Landsat scenes over Morgantown area
curl -s "https://cmr.earthdata.nasa.gov/search/granules.json?\
collection_concept_id=C2021957657-LPCLOUD&\
bounding_box=-80.1,39.5,-79.6,39.8&\
temporal=2024-06-01T00:00:00Z,2024-09-30T23:59:59Z&\
cloud_cover=0,20&\
sort_key=-start_date&\
page_size=10"
```

```bash
# Find MODIS thermal anomalies near a well pad
curl -s "https://cmr.earthdata.nasa.gov/search/granules.json?\
short_name=MOD14&\
bounding_box=-80.0,39.6,-79.8,39.7&\
temporal=2024-01-01T00:00:00Z,2024-12-31T23:59:59Z&\
page_size=10"
```

### Step 4 -- Parse Response

**Collection search response (`.json` format):**
```json
{
  "feed": {
    "entry": [
      {
        "id": "C2021957657-LPCLOUD",
        "title": "Landsat 8-9 OLI/TIRS Collection 2 Level-2 Science Products",
        "short_name": "LANDSAT_OT_C2_L2",
        "time_start": "2013-03-18T00:00:00.000Z",
        "time_end": null,
        "summary": "...",
        "data_center": "LPCLOUD",
        "links": [{"href": "...", "rel": "..."}]
      }
    ]
  }
}
```

**Granule search response (`.json` format):**
```json
{
  "feed": {
    "entry": [
      {
        "id": "G2345678901-LPCLOUD",
        "title": "LC09_L2SP_017032_20240715_20240716_02_T1",
        "time_start": "2024-07-15T15:45:23.000Z",
        "time_end": "2024-07-15T15:45:47.000Z",
        "cloud_cover": "12.5",
        "granule_size": "423.7",
        "links": [
          {"href": "https://...", "rel": "http://esipfed.org/ns/fedsearch/1.1/data#", "type": "application/x-tar"}
        ],
        "boxes": ["39.5 -80.1 40.0 -79.5"]
      }
    ]
  }
}
```

Key fields to extract:
- `id` -- CMR concept ID
- `title` -- scene identifier (contains path/row, date, processing info)
- `time_start`/`time_end` -- acquisition time
- `cloud_cover` -- percent cloud cover (string, parse to float)
- `links` -- data download URLs (require Earthdata login)
- `boxes` -- spatial extent [S W N E]

### Step 5 -- Produce Output

**Format: Results Table + Narrative**

Present a markdown table of the most relevant results (cap at ~15 rows for
readability), then a narrative summary covering:

1. **Search results** -- how many collections/granules matched
2. **Best candidates** -- lowest cloud cover, most recent, best spatial coverage
3. **Temporal coverage** -- date range of available data
4. **Spatial note** -- confirm the results overlap the area of interest
5. **Download instructions** -- how to access the actual data files
6. **PNGE application** -- what analysis the data supports

**Example output structure:**
```
## Landsat 8/9 Scenes -- Monongalia County, WV (Summer 2024)

| Scene ID | Date | Cloud (%) | Path/Row |
|----------|------|-----------|----------|
| LC09_L2SP_017032_20240715_... | 2024-07-15 | 12.5 | 017/032 |
| LC08_L2SP_017032_20240707_... | 2024-07-07 | 8.2 | 017/032 |
| LC09_L2SP_017032_20240629_... | 2024-06-29 | 22.1 | 017/032 |

**Summary:** 7 Landsat 8/9 Level-2 scenes found over the Monongalia County
area for June-September 2024, with cloud cover under 20%. The July 7 scene
(8.2% cloud) offers the clearest view for NDVI analysis of well pad
vegetation recovery. Path 017, Row 032 covers the core Marcellus drilling
area in northern WV.

**To download:** Requires free NASA Earthdata Login
(https://urs.earthdata.nasa.gov/users/new). Use wget with .netrc auth or
the Earthdata Search portal (https://search.earthdata.nasa.gov/).
```

---

## Pagination

CMR returns `page_size` results per request (default 10, max 2000). Use
`page_num` to paginate:

```bash
# Page 1
curl -s "...&page_size=100&page_num=1"

# Page 2
curl -s "...&page_size=100&page_num=2"
```

Check the `CMR-Hits` response header for the total number of matching
results. If not available in the JSON body, add `-D -` to curl to capture
headers.

---

## Error Handling

| HTTP Code | Meaning | Action |
|-----------|---------|--------|
| 200 | Success | Parse normally |
| 400 | Bad parameter (invalid bbox, date format) | Check parameter format; bbox is W,S,E,N |
| 404 | Invalid endpoint | Check URL path |
| 503 | Service temporarily unavailable | Retry after 5 seconds (max 3 retries) |
| 200 + empty feed | No results match filters | Widen temporal range, increase cloud_cover, or expand bounding_box |

**Common mistakes:**
- Bounding box order is **W,S,E,N** (not N,W,S,E)
- Temporal range requires full ISO 8601 with timezone: `2024-01-01T00:00:00Z`
- `collection_concept_id` is required for granule search (unless using `short_name`)
- Cloud cover filter is `min,max` -- use `0,100` to get all scenes

---

## PNGE Applications

### Well Pad Monitoring
Use Landsat/HLS time series to track:
- Initial land clearing for pad construction
- Active drilling period (equipment visible at 30m in some cases)
- Post-drilling reclamation and revegetation (NDVI recovery curves)

### Produced Water Impoundment Detection
- Thermal bands (Landsat Band 10, MODIS LST) can detect warm produced water
  ponds against cooler surrounding landscape
- Surface reflectance changes when ponds fill or drain

### Gas Flare Detection
- MODIS/VIIRS thermal anomaly products (MOD14, VNP14IMG) detect active
  flares at sub-pixel level
- Cross-reference with state well permit data to identify flaring wells

### Environmental Baseline Studies
- Pre-drilling vegetation and land cover baseline using MCD12Q1
- Water quality proxy via turbidity in nearby streams (requires
  atmospherically corrected surface reflectance)

### Pipeline Route Assessment
- Land cover analysis along proposed pipeline corridors
- Change detection before/after pipeline construction

---

## Data Access Methods

CMR search provides metadata and download URLs. Actual data access methods:

1. **Earthdata Search Portal** -- interactive web interface at
   https://search.earthdata.nasa.gov/ (easiest for ad-hoc exploration)
2. **Direct download** -- wget/curl with ~/.netrc Earthdata credentials
3. **NASA AppEEARS** -- subsetting and reformatting service at
   https://appeears.earthdatacloud.nasa.gov/ (good for time series extracts)
4. **Cloud access** -- many collections are in AWS us-west-2; use
   S3 direct access with Earthdata token for large-scale analysis

---

## Caveats and Data Quality

- **Search vs download:** CMR search is free and unauthenticated. Downloading
  actual data files requires a free Earthdata Login account.
- **Cloud cover:** The `cloud_cover` metadata is scene-level and may not
  reflect conditions at your specific point of interest. A scene reported
  at 15% cloud may have clouds directly over your well site.
- **Spatial resolution limits:** Landsat at 30m cannot resolve individual
  wellheads or small equipment. It can detect pad-scale clearing (typically
  1-5 acres) and large impoundments. MODIS at 1km is useful only for
  regional thermal patterns.
- **Temporal gaps:** Cloud cover, especially in Appalachia, limits usable
  scenes. Expect only 20-40% of Landsat passes to be usable in WV during
  summer months, fewer in winter.
- **Processing levels:** Level-2 products (surface reflectance, surface
  temperature) are analysis-ready. Level-1 products require atmospheric
  correction before quantitative analysis.
- **Latency:** Standard Landsat products available within 12-24 hours of
  acquisition. MODIS near-real-time products within 3 hours.
- **Coordinate system:** CMR uses decimal degrees (WGS84/EPSG:4326).
  Bounding box order is W,S,E,N -- different from some GIS conventions.

---

## Implementation Notes

- **Use `bash` with `curl` + `jq`** for API calls
- Response format `.json` returns Atom feed format; `.umm_json` returns full
  UMM metadata (more verbose but includes all fields)
- Collection `concept_id` values are stable and can be hardcoded for known
  collections (e.g., `C2021957657-LPCLOUD` for Landsat 8/9 L2)
- For Landsat scene IDs: `LC09_L2SP_PPPRRR_YYYYMMDD_...` where PPP=path,
  RRR=row, YYYYMMDD=acquisition date
- CMR rate limits are generous (no published limit for search) but add
  100ms delay between paginated requests as courtesy
- The `CMR-Hits` response header gives total result count without fetching
  all pages -- useful for checking result set size before paginating
