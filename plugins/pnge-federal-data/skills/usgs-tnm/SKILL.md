---
name: usgs-tnm
description: >
  Access USGS The National Map for elevation data (DEMs), geologic maps,
  topographic maps, hydrography, imagery, and geospatial products via the
  TNM Access API. Use when the user asks about elevation near a well site,
  DEM download, USGS topographic maps, geologic maps, surface slope for
  facility siting, lidar data, 3DEP elevation, National Elevation Dataset,
  ortho imagery, hydrography near a well pad, watershed boundaries, NHD,
  or USGS geospatial products. Trigger phrases: "elevation data near well",
  "download DEM for WV", "topo map Monongalia County", "geologic map
  Appalachian Basin", "lidar data", "terrain analysis", "slope for pad
  siting", "USGS topo map", "3DEP elevation", "NHD hydrography",
  "watershed boundaries", "ortho imagery". Covers NGMDB MapView and
  USGS SGMC. Produces download links and geospatial product metadata.
---

# USGS The National Map (TNM) Skill

Accesses USGS geospatial data products through The National Map API --
elevation (3DEP/NED), topographic maps, hydrography (NHD), imagery (NAIP),
and related datasets. Also covers USGS geologic map services (SGMC, NGMDB).

---

## Credential

**None required.** All TNM services are publicly accessible.

```bash
# No API key needed -- USGS TNM services are open access
```

---

## Data Sources

| Source | Type | URL |
|--------|------|-----|
| TNM Access API | REST API (JSON) | https://tnmaccess.nationalmap.gov/api/v1/ |
| 3DEP Elevation Viewer | Web map | https://apps.nationalmap.gov/3depdem/ |
| NGMDB MapView | Web map (geologic maps) | https://ngmdb.usgs.gov/mapview/ |
| SGMC (State Geologic Map Compilation) | WMS service | https://mrdata.usgs.gov/services/sgmc |
| National Map Download | Web download manager | https://apps.nationalmap.gov/downloader/ |
| USGS Lidar Explorer | Web map (point cloud data) | https://apps.nationalmap.gov/lidar-explorer/ |

---

## API Structure

### TNM Access API

**Base URL:** `https://tnmaccess.nationalmap.gov/api/v1/`

**Endpoints:**

| Endpoint | Description |
|----------|-------------|
| `/products` | Search and download geospatial data products |
| `/datasets` | List available dataset categories |

### Available Datasets (from /datasets)

| Dataset ID | Tag | Description |
|-----------|-----|-------------|
| elevation-products-three-dep | National Elevation Dataset (NED) | 3DEP DEM tiles (1/3, 1, 2 arc-second) |
| elevation-source-data-lidar-isfar | National Elevation Dataset (NED) | Lidar and IfSAR source data |
| us-topo-main | US Topo | Current USGS topographic maps (GeoPDF) |
| historical-topographic-maps | Historical Topographic Maps | Historical 7.5-minute and 15-minute quads |
| hydrography-nhdplushr-nhd-wbd-main | 3D Hydrography Program (3DHP) | NHD flowlines, waterbodies, WBD watersheds |
| imagery-naip-plus | USDA NAIP | 1m to 0.5ft aerial imagery |
| national-boundary-dataset | National Boundary Dataset (NBD) | State, county, congressional district boundaries |
| names-geographic-names-information-system | GNIS | Geographic place names |
| structures-national-structures-dataset | NSD | Schools, hospitals, fire stations, etc. |
| transportation | NTD | Roads, railroads, trails |

### Key Query Parameters for /products

| Parameter | Description | Example |
|-----------|-------------|---------|
| `datasets` | Dataset name (from list above) | `National Elevation Dataset (NED) 1/3 arc-second` |
| `bbox` | Bounding box (minLon,minLat,maxLon,maxLat) | `-80.5,39.5,-79.5,40.0` |
| `polygon` | WKT polygon for spatial filter | (URL-encoded WKT) |
| `q` | Text search across product metadata | `Monongalia` |
| `prodFormats` | File format filter | `GeoTIFF` |
| `max` | Maximum results to return | `10` |
| `offset` | Pagination offset | `0` |
| `outputFormat` | Response format | `JSON` (default) |
| `dateType` | Date filter type | `dateCreated` or `lastUpdated` |
| `start` | Start date for date filter | `2020-01-01` |
| `end` | End date for date filter | `2024-12-31` |

---

## Workflow

### Step 1 -- Resolve Intent

| User asks about... | Dataset | Strategy |
|---------------------|---------|----------|
| Elevation/DEM near a well | elevation-products-three-dep | Bounding box query around coordinates |
| Topographic map of an area | us-topo-main | Bounding box or text search by location name |
| Historical topo map | historical-topographic-maps | Text search + date filter |
| Lidar point cloud data | elevation-source-data-lidar-isfar | Bounding box query |
| Aerial imagery | imagery-naip-plus | Bounding box query |
| Streams/rivers near a site | hydrography-nhdplushr-nhd-wbd-main | Bounding box query |
| Geologic map | NGMDB MapView or SGMC WMS | Web map or WMS GetMap |
| Slope/terrain analysis | elevation-products-three-dep | Download DEM, analyze with GIS tools |

### Step 2 -- Query TNM Access API

**Search for elevation data (DEM) near a well site:**

```bash
# 1/3 arc-second DEM tiles covering north-central WV
curl -s "https://tnmaccess.nationalmap.gov/api/v1/products?datasets=National+Elevation+Dataset+(NED)+1/3+arc-second&bbox=-80.5,39.5,-79.5,40.0&max=5" \
  | jq '.items[] | {title, format, sizeInBytes, downloadURL}'
```

**Search for USGS topographic maps:**

```bash
# Current US Topo maps for an area
curl -s "https://tnmaccess.nationalmap.gov/api/v1/products?datasets=US+Topo&bbox=-80.1,39.6,-79.9,39.7&max=5" \
  | jq '.items[] | {title, format, downloadURL}'
```

**Search for historical topographic maps:**

```bash
# Historical 7.5-minute quads
curl -s "https://tnmaccess.nationalmap.gov/api/v1/products?datasets=Historical+Topographic+Maps&bbox=-80.1,39.6,-79.9,39.7&max=5" \
  | jq '.items[] | {title, publicationDate, downloadURL}'
```

**Search for lidar data:**

```bash
# Lidar source data for an area
curl -s "https://tnmaccess.nationalmap.gov/api/v1/products?datasets=Lidar+Point+Cloud+(LPC)&bbox=-80.1,39.6,-79.9,39.7&max=5" \
  | jq '.items[] | {title, format, sizeInBytes, downloadURL}'
```

**Search for NAIP aerial imagery:**

```bash
# NAIP orthoimagery
curl -s "https://tnmaccess.nationalmap.gov/api/v1/products?datasets=USDA+National+Agriculture+Imagery+Program+(NAIP)&bbox=-80.1,39.6,-79.9,39.7&max=5" \
  | jq '.items[] | {title, publicationDate, downloadURL}'
```

**Search for hydrography data:**

```bash
# NHD flowlines and watershed boundaries
curl -s "https://tnmaccess.nationalmap.gov/api/v1/products?datasets=National+Hydrography+Dataset+(NHD)+Best+Resolution&bbox=-80.5,39.5,-79.5,40.0&max=5" \
  | jq '.items[] | {title, format, downloadURL}'
```

### Step 3 -- Access Geologic Maps

**NGMDB MapView (web interface):**

Navigate to https://ngmdb.usgs.gov/mapview/ and zoom to the area of interest.
The MapView application overlays published geologic maps at various scales.

**SGMC WMS (programmatic for geologic map tiles):**

```bash
# USGS State Geologic Map Compilation WMS GetMap request
# Returns a geologic map image for a bounding box
curl -s "https://mrdata.usgs.gov/services/sgmc?service=WMS&version=1.1.1&request=GetMap&layers=sgmc&bbox=-80.5,39.5,-79.5,40.0&width=800&height=600&srs=EPSG:4326&format=image/png" \
  -o /tmp/geologic_map_wv.png
```

```bash
# SGMC WMS GetFeatureInfo -- identify geologic unit at a point
curl -s "https://mrdata.usgs.gov/services/sgmc?service=WMS&version=1.1.1&request=GetFeatureInfo&layers=sgmc&query_layers=sgmc&info_format=text/plain&x=400&y=300&width=800&height=600&bbox=-80.5,39.5,-79.5,40.0&srs=EPSG:4326"
```

### Step 4 -- Parse Response

TNM API response structure:

```json
{
  "total": 18,
  "items": [
    {
      "title": "USGS 1/3 Arc Second n40w080 20210111",
      "sourceId": "60678639d34edc0435c0a5e6",
      "metaUrl": "https://www.sciencebase.gov/catalog/item/60678639d34edc0435c0a5e6",
      "publicationDate": "2021-01-11",
      "lastUpdated": "2021-11-30",
      "sizeInBytes": 468401044,
      "extent": "1 x 1 degree",
      "format": "GeoTIFF",
      "downloadURL": "https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/13/TIFF/...",
      "boundingBox": {"minX": -80.0, "maxX": -79.0, "minY": 39.0, "maxY": 40.0}
    }
  ],
  "messages": ["Retrieved 18 item(s) Retrieved (1 through 5)"]
}
```

### Step 5 -- Produce Output

**Format: Product Listing Table + Download Links + Narrative**

---

## Output Format

### Example 1: DEM Products

```
## Elevation Data: North-Central West Virginia (39.5N-40.0N, 79.5W-80.5W)

**Dataset:** 3DEP 1/3 Arc Second (~10 meter resolution)
**Total tiles:** 18
**Showing:** 5 most recent

| Title | Date | Size (MB) | Format | Resolution |
|-------|------|-----------|--------|------------|
| USGS 1/3 Arc Second n40w080 20210630 | 2021-11-16 | 444 | GeoTIFF | ~10 m |
| USGS 1/3 Arc Second n40w080 20210111 | 2021-01-11 | 447 | GeoTIFF | ~10 m |
| USGS 1/3 Arc Second n40w081 20201015 | 2020-10-15 | 435 | GeoTIFF | ~10 m |

**Download (most recent):**
https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/13/TIFF/historical/n40w080/USGS_13_n40w080_20210630.tif

**Summary:** 3DEP 1/3 arc-second DEM data is available for the north-central
WV area at ~10 meter horizontal resolution. Multiple vintages available; the
2021 version incorporates the latest WV lidar-derived DEMs. For well pad
siting and terrain analysis, this resolution is suitable for slope analysis,
drainage delineation, and visibility studies. For finer resolution, check
lidar source data (1-2 meter resolution where available).

**Usage with GIS:** Load the GeoTIFF in QGIS, ArcGIS, or Python (rasterio)
for slope, aspect, and viewshed analysis.
```

### Example 2: Geologic Map

```
## Geologic Map: Monongalia County, WV Area

**Source:** USGS State Geologic Map Compilation (SGMC) via WMS
**Map image saved to:** /tmp/geologic_map_wv.png

The SGMC WMS provides generalized geologic units from published state
geologic maps. For detailed formation contacts and structure, consult
the NGMDB MapView at https://ngmdb.usgs.gov/mapview/ which overlays
original published maps at their native scale.

**Key formations in view:** Pennsylvanian and Permian clastics (sandstone,
shale, coal) at surface. Marcellus Shale and deeper Appalachian Basin
targets are not exposed at surface in this area -- subsurface structure
must be inferred from well data (see `pnge-state-regulatory:wvges-wells`).
```

---

## Error Handling

| Issue | Cause | Action |
|-------|-------|--------|
| Empty items array | No products match the query for that bbox/dataset | Expand bounding box; verify dataset name spelling |
| TNM API 403 | Rate limiting or temporary block | Wait and retry; reduce request frequency |
| Download URL 404 | Product moved or deprecated | Use metaUrl to get current ScienceBase item |
| Very large file sizes (GB+) | Lidar point clouds, high-res imagery | Warn user about size; suggest TNM Download Manager |
| SGMC WMS returns "received wms with no service" | Missing or incorrect service parameter | Verify service=WMS and request=GetMap in query string |
| Dataset name not recognized | Exact dataset name required | Use /datasets endpoint to list valid names |
| Bounding box too large | Too many products returned | Narrow the bbox; increase max parameter |

---

## Caveats

1. **File sizes can be very large.** DEM GeoTIFFs are 400-500 MB per 1x1
   degree tile. Lidar point clouds can be multiple GB. Aerial imagery is
   similarly large. Warn users before initiating downloads.

2. **Resolution varies by location.** 3DEP provides 1/3 arc-second (~10m)
   nationally for the conterminous U.S. Higher resolution (1m from lidar)
   is available in many areas but not everywhere. Alaska has 2 arc-second
   in most areas.

3. **Geologic maps are generalized.** The SGMC WMS provides compiled state
   geologic maps that may not show detailed formation contacts needed for
   subsurface analysis. For detailed geologic mapping, use the NGMDB
   MapView to find original published maps at appropriate scales.

4. **Surface geology vs. subsurface targets.** In the Appalachian Basin,
   DLE target formations (Marcellus, Utica, Smackover) are deep subsurface
   units not visible in surface geologic maps. Surface geologic maps are
   useful for understanding regional structure but subsurface analysis
   requires well data and seismic.

5. **Elevation data datum.** 3DEP data use NAD83 horizontal datum and
   NAVD88 vertical datum (meters) for the conterminous U.S. Alaska uses
   varying vertical references. Verify datum before combining with other
   spatial data.

6. **Historical topo maps.** Historical USGS topographic maps are scanned
   images (GeoPDF), not georeferenced rasters. They provide visual reference
   but are not directly usable for GIS analysis without georeferencing.

7. **TNM API pagination.** The API returns results in pages. Use `max` and
   `offset` parameters for pagination. The `total` field shows the complete
   count.

---

## Implementation Notes

- Use `bash_tool` with `curl` for TNM API queries and downloads
- Parse JSON responses with `jq`
- For large downloads, save to `/tmp/` and warn user about file sizes
- TNM Download Manager (web): https://apps.nationalmap.gov/downloader/ for batch downloads
- For DEM analysis in Python: `rasterio`, `elevation`, or `richdem` packages
- For geologic map WMS in Python: `owslib` package for WMS client
- Combine elevation data with `pnge-state-regulatory:wvges-wells` well locations for terrain context
- Combine with `pnge-federal-data:blm-mineral-records` for land ownership overlay
- The TNM API query results include ScienceBase `metaUrl` links for additional metadata
- SGMC WMS supports GetCapabilities, GetMap, and GetFeatureInfo operations
