---
name: blm-mineral-records
description: >
  Access Bureau of Land Management mineral lease records, federal land ownership,
  mining claims, and cadastral survey data for federal onshore mineral rights.
  Use this skill when the user asks about BLM mineral leases, federal mineral
  rights, mining claims on public land, lease sale results, federal land
  ownership near well sites, surface management agency data, who owns the
  mineral rights on federal land, BLM lease parcels, oil and gas leases on
  federal land, federal onshore mineral development, siting DLE projects on
  federal land, Public Land Survey System (PLSS) section-township-range, or
  cadastral survey data. Trigger for phrases like "BLM mineral lease",
  "federal land ownership", "mining claims in Nevada", "who owns the minerals",
  "PLSS location", "federal oil and gas lease", "lease sale results", "BLM
  land status". Outputs land ownership tables and spatial query results with
  narrative context on federal mineral rights.
---

# BLM Mineral and Land Records Skill

Queries Bureau of Land Management GIS services and reporting systems for
federal mineral leases, land ownership, mining claims, and cadastral
(Public Land Survey System) data. Essential for determining federal mineral
rights when siting DLE projects on public lands.

---

## Credential

**None required.** All BLM GIS services and public reports are open access.

```bash
# No API key needed — BLM GIS services are public
```

---

## Data Sources

| Source | Type | URL |
|--------|------|-----|
| BLM National SMA (Surface Management Agency) | ArcGIS REST MapServer | https://gis.blm.gov/arcgis/rest/services/lands/ |
| BLM PLSS Cadastral (PLSS) | ArcGIS REST MapServer | https://gis.blm.gov/arcgis/rest/services/Cadastral/ |
| BLM DANL (Mining Claims / Nominated Parcels) | ArcGIS REST MapServer/FeatureServer | https://gis.blm.gov/arcgis/rest/services/DANL/ |
| LR2000 (Legacy Rehost 2000) | Web portal (no REST API) | https://reports.blm.gov/reports/LR2000 |
| BLM National LPAD | ArcGIS REST MapServer | https://gis.blm.gov/arcgis/rest/services/lands/BLM_Natl_LPAD/MapServer |

**Note:** The LR2000 system (case recordation for mineral leases, mining
claims, rights-of-way, and withdrawals) is a web-only reporting application
at https://reports.blm.gov/ under the "LR2000" section. There is no public
REST API for LR2000 — queries must be run through the web interface or via
the BLM GIS services listed above.

---

## API Structure

### BLM GIS Services Folder Structure

```
https://gis.blm.gov/arcgis/rest/services/
  lands/                    # Land ownership, SMA, NLCS, LPAD
  Cadastral/                # PLSS township-range-section grid
  DANL/                     # Mining claims, nominated parcels
  admin_boundaries/         # BLM administrative boundaries
```

### Key Services and Layers

**Surface Management Agency (land ownership):**
```
https://gis.blm.gov/arcgis/rest/services/lands/BLM_Natl_SMA_Cached_without_PriUnk/MapServer
  Layer 1: Surface Management Agency
  Layer 7: Bureau of Land Management (BLM)
  Layer 8: National Park Service (NPS)
  Layer 9: US Forest Service (USFS)
```

Fields: `SMA_ID`, `ADMIN_DEPT_CODE`, `ADMIN_AGENCY_CODE`, `ADMIN_UNIT_NAME`,
`ADMIN_UNIT_TYPE`, `ADMIN_ST`, `HOLD_DEPT_CODE`, `HOLD_AGENCY_CODE`

**PLSS Cadastral Survey:**
```
https://gis.blm.gov/arcgis/rest/services/Cadastral/BLM_Natl_PLSS_CadNSDI/MapServer
```

Provides section-township-range grids for all PLSS states (most of western U.S.).

**DANL (Nominated Parcels / Mining Claims):**
```
https://gis.blm.gov/arcgis/rest/services/DANL/BLM_Natl_DANL_DataCollection_MapService/MapServer
  Layer 0: BLM Natl DANL Newly Nominated Parcels
```

---

## Workflow

### Step 1 -- Resolve Intent

| User asks about... | Strategy |
|---------------------|----------|
| Land ownership at a location | Spatial query on SMA layer with point or bounding box |
| Whether land is BLM-managed | Query SMA layer, filter by ADMIN_AGENCY_CODE |
| PLSS section-township-range | Query Cadastral service with spatial or attribute filter |
| Mining claims in an area | Query DANL service with spatial extent |
| Federal oil and gas leases | Direct user to LR2000 web portal with search guidance |
| Lease sale results | Direct user to LR2000 or BLM lease sale page |

### Step 2 -- Query GIS Services

**Spatial query -- land ownership at a point (lon, lat):**

```bash
# Who manages the surface at a given coordinate?
curl -s "https://gis.blm.gov/arcgis/rest/services/lands/BLM_Natl_SMA_Cached_without_PriUnk/MapServer/1/query" \
  --data-urlencode "geometry=-107.5,38.5" \
  --data-urlencode "geometryType=esriGeometryPoint" \
  --data-urlencode "spatialRel=esriSpatialRelIntersects" \
  --data-urlencode "outFields=ADMIN_DEPT_CODE,ADMIN_AGENCY_CODE,ADMIN_UNIT_NAME,ADMIN_UNIT_TYPE,ADMIN_ST" \
  --data-urlencode "f=json"
```

**Bounding box query -- all BLM land in an area:**

```bash
# Land ownership within a bounding box (minLon,minLat,maxLon,maxLat)
curl -s "https://gis.blm.gov/arcgis/rest/services/lands/BLM_Natl_SMA_Cached_without_PriUnk/MapServer/1/query" \
  --data-urlencode "geometry=-108.0,38.0,-107.0,39.0" \
  --data-urlencode "geometryType=esriGeometryEnvelope" \
  --data-urlencode "spatialRel=esriSpatialRelIntersects" \
  --data-urlencode "outFields=*" \
  --data-urlencode "resultRecordCount=50" \
  --data-urlencode "f=json"
```

**PLSS query -- find section-township-range:**

```bash
# PLSS grid at a coordinate
curl -s "https://gis.blm.gov/arcgis/rest/services/Cadastral/BLM_Natl_PLSS_CadNSDI/MapServer/1/query" \
  --data-urlencode "geometry=-107.5,38.5" \
  --data-urlencode "geometryType=esriGeometryPoint" \
  --data-urlencode "spatialRel=esriSpatialRelIntersects" \
  --data-urlencode "outFields=*" \
  --data-urlencode "f=json"
```

**Nominated parcels / mining claims:**

```bash
# Recently nominated parcels
curl -s "https://gis.blm.gov/arcgis/rest/services/DANL/BLM_Natl_DANL_DataCollection_MapService/MapServer/0/query" \
  --data-urlencode "where=1=1" \
  --data-urlencode "outFields=*" \
  --data-urlencode "resultRecordCount=10" \
  --data-urlencode "f=json"
```

### Step 3 -- Parse Response

ArcGIS REST responses follow this structure:

```json
{
  "features": [
    {
      "attributes": {
        "ADMIN_AGENCY_CODE": "BLM",
        "ADMIN_UNIT_NAME": "Colorado",
        "ADMIN_ST": "CO"
      },
      "geometry": { "rings": [...] }
    }
  ]
}
```

### Step 4 -- Produce Output

**Format: Land Status Table + Narrative**

Present results as a markdown table (capped at ~20 rows), followed by a
narrative covering:

1. **Land status** -- which agency manages the surface (BLM, USFS, NPS, etc.)
2. **Mineral rights context** -- federal surface does not always equal federal minerals; split estate is common
3. **PLSS reference** -- section, township, range, and meridian
4. **DLE siting implications** -- whether federal mineral lease would be needed

---

## Output Format

```
## Land Ownership Query: Gunnison County, CO Area

| Feature | Agency | Unit Name | Unit Type | State |
|---------|--------|-----------|-----------|-------|
| 1 | BLM | Colorado | Field Office | CO |
| 2 | USFS | Grand Mesa NF | National Forest | CO |
| 3 | NPS | Black Canyon | National Park | CO |

**Summary:** The queried area (-108.0 to -107.0 lon, 38.0 to 39.0 lat) in
western Colorado contains a mix of BLM-managed public land, US Forest Service
(Grand Mesa NF), and NPS (Black Canyon of the Gunnison). BLM-managed parcels
would require a federal mineral lease under the Mineral Leasing Act for any
DLE brine extraction operations. Contact the BLM Colorado State Office or
use LR2000 to check existing lease status.

**Note:** Surface management agency does not determine subsurface mineral
ownership. Split estate conditions (federal surface / private minerals or
vice versa) are common in the western U.S. Confirm mineral rights through
the BLM's LR2000 system or county recorder records.
```

---

## LR2000 Web Portal Guide

The LR2000 system at https://reports.blm.gov/ provides case-level detail
on mineral leases, mining claims, rights-of-way, and land withdrawals.
There is no REST API -- use the web interface.

**Key report categories (from the BLM Reporting Application):**

| Category | Content |
|----------|---------|
| MLRS (Mineral and Land Records System) | Active mineral leases, mining claims, serial register pages |
| LR2000 | Legacy case records -- oil/gas leases, coal leases, mining claims by state/county |

**To search for oil and gas leases in LR2000:**
1. Navigate to https://reports.blm.gov/
2. Select "LR2000" from the Applications menu
3. Choose the report type (e.g., "Oil and Gas Leases")
4. Filter by state, county, or serial number
5. Export results as needed

---

## Error Handling

| Issue | Cause | Action |
|-------|-------|--------|
| Empty features array | No federal land at queried location (private/state land) | Expand search area or note that location is non-federal |
| ArcGIS 400 error | Malformed geometry or invalid spatial reference | Verify coordinate format (lon,lat for WGS84) and geometry type |
| Service timeout | Large spatial query returning too many features | Add `resultRecordCount` limit; narrow bounding box |
| "Layer not found" | Service restructured | Check parent service URL for current layer IDs |
| No PLSS data | Location outside PLSS states (original 13 colonies, TX, HI) | Note that PLSS does not cover eastern states; use metes-and-bounds references |
| LR2000 web portal unavailable | Federal site maintenance | Try BLM GIS services as alternative; check https://www.blm.gov/lr2000 |

---

## Caveats

1. **Surface management does not equal mineral ownership.** The SMA layer shows
   who manages the surface. Subsurface mineral rights may be held by a different
   entity (split estate). The LR2000 case records are the authoritative source
   for federal mineral lease status.

2. **PLSS coverage.** The Public Land Survey System covers most states west of
   the Ohio River, but does not cover the original 13 colonies, Kentucky,
   Tennessee, West Virginia, Texas, or Hawaii. For Appalachian Basin research
   (WV, PA, OH), PLSS coverage varies -- OH uses PLSS but WV does not.

3. **BLM data currency.** GIS layers are updated periodically, not in real-time.
   For active lease negotiations or current claim status, verify through the
   BLM state office or LR2000.

4. **No REST API for LR2000.** The most detailed mineral lease case data is
   only available through the LR2000 web interface. Bulk data extraction is
   not supported.

5. **Western U.S. focus.** BLM manages ~245 million acres, primarily in 12
   western states plus Alaska. BLM-managed land in eastern states is minimal.
   For Appalachian Basin DLE siting, state mineral rights agencies are more
   relevant than BLM.

6. **Federal vs. state vs. private.** On federal land, a mineral lease from BLM
   is required for extraction. On state land, contact the state land board. On
   private land, negotiate directly with mineral rights holders. The SMA layer
   helps determine which regime applies.

---

## Implementation Notes

- Use `bash_tool` with `curl` for ArcGIS REST queries
- Parse JSON responses with `jq` or `python`
- For spatial queries, coordinates must be in WGS84 (EPSG:4326) decimal degrees
- ArcGIS REST default spatial reference is Web Mercator (102100); specify `inSR=4326` if needed
- `resultRecordCount` caps at service-defined max (typically 1000-2000); paginate with `resultOffset`
- For DLE project siting, combine this skill with `pnge:wvges-wells` or `pnge:boem-offshore` for well data overlay
