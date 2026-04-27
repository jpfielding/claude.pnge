# WVDEP Oil and Gas — ArcGIS REST API Reference

## Service Endpoints

### Primary (WVDEP Enterprise)

```
Base URL: https://tagis.dep.wv.gov/arcgis/rest/services/WVDEP_enterprise/oil_gas/MapServer
```

This service uses data from the RBDMS (Risk Based Data Management System) database,
adopted by the WVDEP Office of Oil and Gas in August 2016. ArcGIS Server version 11.5.

### Application Service (OOG Web App)

```
Base URL: https://tagis.dep.wv.gov/arcgis/rest/services/app_services/oog2/MapServer
```

Same layer structure as the enterprise service. Used by the WVDEP OOG interactive map
at https://tagis.dep.wv.gov/oog/.

### Legacy (WVGES — Currently Offline)

```
Base URL: http://atlas.wvgs.wvnet.edu/arcgis/rest/services/OilGas/WVOG/MapServer
```

The WV Geological and Economic Survey server has been intermittently unavailable.
Use the WVDEP enterprise service as the primary endpoint. The WVGES Pipeline
database at https://www.wvgs.wvnet.edu/pipe2/ remains a useful reference for
individual well lookups by county code + permit number.

---

## Layers

| ID | Name | Geometry | Records | Description |
|----|------|----------|---------|-------------|
| 0 | WVDEP Wells, Horizontal Only | Point | 9,406 | Horizontal and Horizontal 6A wells only |
| 1 | WVDEP Wells, Active Status Only | Point | 66,217 | Wells with wellstatus = "Active Well" |
| 2 | WVDEP Wells, Other than Active Status | Point | 37,638 | Non-active wells (plugged, abandoned, shutin, etc.) |
| 3 | WVDEP Wells, Coal Bed Methane | Point | 2,336 | CBM wells only |
| 4 | WVDEP Wells, Plugged | Point | 49,412 | Wells with wellstatus = "Plugged" |
| 5 | Oil and Gas Wells, Not in WVDEP Database | Point | 54,887 | Legacy WVGES wells not yet in RBDMS; extra location fields |
| 6 | Horizontal laterals (simplified) | Polyline | 5,444 | Lateral paths with surface/landing/bottom coordinates |
| 7 | All DEP Wells | Point | 153,267 | **Primary query layer** — all wells in RBDMS, no display scale limits |
| 8 | WVDEP Wells, Brine Disposal | Point | 396 | Brine disposal wells only |
| 10 | Well Pads | Polygon | 1,023 | Well pad boundaries with site metadata |

**Layer 7 is the primary query target.** It has `minScale=0` (no scale restriction)
and contains the full RBDMS dataset. The other layers (0-4, 8) are filtered subsets
of the same data with display scale limits.

**Layer 5 is a separate dataset** — legacy WVGES wells not yet migrated to RBDMS.
It has additional location fields (DMS coordinates, UTM, quad names).

---

## Fields — Layer 7 (All DEP Wells)

| Field | Type | Alias | Description |
|-------|------|-------|-------------|
| objectid | OID | OBJECTID | Server-assigned unique ID |
| pkey | Integer | pkey | Internal database primary key |
| permitid | String(9) | PermitID | County-permit code, e.g., "039-00027" |
| county | String(3) | County | 3-digit WV FIPS county code (zero-padded) |
| permit | String(5) | Permit | 5-digit permit number within county |
| api | String(32) | api | API well number, e.g., "4703900027" (47=WV state code) |
| welltype | String(255) | WellType | Well orientation/type |
| welluse | String(255) | WellUse | Well purpose/use category |
| welldepth | String(255) | WellDepth | Depth category (text, not numeric) |
| wellrig | String(255) | WellRig | Rig information |
| permittype | String(255) | PermitType | Permit action type |
| issuedate | String(11) | IssueDate | Permit issue date as YYYY/MM/DD string |
| compdate | String(11) | CompDate | Completion date as YYYY/MM/DD string |
| respparty | String(100) | RespParty | Responsible party (operator) |
| wellstatus | String(255) | WellStatus | Current well status |
| farmname | String(100) | FarmName | Farm/lease name |
| wellnumber | String(50) | WellNumber | Well number on the lease |
| recdate | String(11) | RecDate | Record date |
| marcellus | String(1) | Marcellus | Marcellus flag: "y"=yes, "n"=no, "u"=unknown |
| formation | String | Formation | Target formation(s), comma-separated if multi-zone |
| link | String | Link | URL link to well record |
| webmap | String | WebMap | Web map reference |
| wellx | Double | WellX | X coordinate (NAD83 UTM Zone 17N, meters) |
| welly | Double | WellY | Y coordinate (NAD83 UTM Zone 17N, meters) |

**Note:** The service spatial reference is Web Mercator (WKID 3857). The wellx/welly
fields store the original NAD83 UTM Zone 17N coordinates.

---

## Fields — Layer 6 (Horizontal Laterals)

Extra fields beyond the standard set:

| Field | Type | Description |
|-------|------|-------------|
| surface_x | Double | Surface hole X coordinate |
| surface_y | Double | Surface hole Y coordinate |
| landing_x | Double | Lateral landing point X |
| landing_y | Double | Lateral landing point Y |
| bottom_x | Double | Bottomhole X coordinate |
| bottom_y | Double | Bottomhole Y coordinate |
| st_length(shape) | Double | Lateral length in map units |

Geometry type is Polyline — the lateral path from surface to bottomhole.

---

## Fields — Layer 5 (Not in WVDEP Database)

Extra fields beyond the standard set (from WVGES legacy data):

| Field | Type | Description |
|-------|------|-------------|
| cntynm | String | County name |
| txdstnm | String | Tax district name |
| quadnm / squadnm | String | USGS quad name (surface / subsurface) |
| secnm | String | Section name |
| latd, latm, mis | String | Latitude degrees, minutes, seconds |
| lond, lonm, miw | String | Longitude degrees, minutes, seconds |
| latdd, londd | String | Decimal degrees |
| utme, utmn | String | UTM Easting/Northing |
| geosource | String | Geolocation source |
| lateral_ | Integer | Lateral flag |

---

## Fields — Layer 10 (Well Pads)

| Field | Type | Description |
|-------|------|-------------|
| year | Double | Construction year |
| lateral_ | String | Lateral flag |
| welllocat | String | Well location description |
| imageyear | Double | Aerial imagery year |
| sitename | String | Site name |
| modifydate | Date | Last modification date |
| facilityke | Double | Facility key |

Geometry type is Polygon.

---

## Enumerated Values

### wellstatus (Layer 7, 153,267 total)

| Value | Count | Description |
|-------|-------|-------------|
| Active Well | 66,217 | Currently producing or operating |
| Plugged | 49,412 | Permanently sealed |
| Abandoned Well | 17,899 | Abandoned, not plugged |
| Never Drilled | 15,823 | Permitted but never spud |
| Shutin | 1,467 | Temporarily shut in |
| Never Issued | 1,185 | Permit application not issued |
| Permit Issued | 946 | Permitted, not yet drilled |
| Permit Application | 138 | Application in progress |
| Future Use | 119 | Designated for future use |
| Duplicate API | 59 | Duplicate record |
| Under Construction | 2 | Currently being drilled |

### welltype

| Value | Count |
|-------|-------|
| Vertical | 140,983 |
| Horizontal 6A | 6,832 |
| Horizontal | 2,574 |
| Coal Bed Methane Well | 2,336 |
| Not Available | 542 |

**Note:** "Horizontal 6A" refers to wells permitted under WV Code 22-6A
(the Natural Gas Horizontal Well Control Act, effective 2011).

### welluse

| Value | Count | Description |
|-------|-------|-------------|
| Gas Production | 75,557 | Natural gas production |
| Not Available | 45,525 | Use not recorded |
| Unknown | 16,626 | Use unknown |
| Oil Production | 5,460 | Oil production |
| Fluid Injection | 3,212 | Injection well (EOR, disposal) |
| Storage | 2,303 | Gas storage |
| 2R Production Well | 1,524 | Secondary recovery production |
| House Gas | 1,487 | Domestic gas supply |
| Brine Disposal | 396 | Brine disposal (UIC Class II) |
| Observation | 171 | Monitoring/observation |
| CBM - Articulate | 159 | Coal bed methane (articulated) |
| Solution Mining | 126 | Solution mining |
| Vent | 50 | Vent well |
| Solution Mining Production Well | 28 | Solution mining production |
| Production | 8 | Generic production |
| Water Well | 1 | Water supply |

### permittype

| Value | Count |
|-------|-------|
| Other Well | ~860+ |
| Plugging | ~400+ |
| Vertical Well | ~384+ |
| Field Assigned Number | ~154+ |
| Fracture | ~77+ |
| Re-Work | ~19+ |
| UIC Permit | ~19+ |
| Drilling Deeper | ~17+ |
| Horizontal Well | ~17+ |
| Assigned Permit Number | ~15+ |
| Horizontal 6A Well | ~14+ |
| Secondary Recovery Well | ~9+ |
| Coalbed Methane | ~6+ |

### marcellus

| Value | Meaning |
|-------|---------|
| y | Marcellus well (confirmed) |
| n | Not a Marcellus well |
| u | Unknown / not classified |

### Top Formations (where formation is not "NA")

| Formation | Count |
|-----------|-------|
| Marcellus Shale | 7,378 |
| Big Injun (Undifferentiated) | 1,049 |
| Berea Sandstone | 1,048 |
| Gordon | 1,026 |
| Lower Huron | 728 |
| Fifth | 572 |
| Devonian Shale | 370 |
| Pittsburgh Coal | 314 |
| Benson | 293 |
| Point Pleasant | 279 |
| Oriskany | 279 |
| Elk | 226 |
| Weir | 182 |
| Big Lime | 157 |
| Maxton | 124 |
| Salina | 124 |
| Squaw | 105 |

**Note:** Formation field is often "NA" for older wells (~85% of records). Multiple
formations are comma-separated (e.g., "Berea Sandstone,Devonian Shale"). The Utica
and Point Pleasant formations are increasingly common in newer horizontal wells.

---

## WV County FIPS Codes (3-digit, zero-padded)

The `county` field uses the 3-digit FIPS code portion (WV state FIPS = 54, but
the county field uses only the county portion without the state prefix).

| Code | County | Wells | | Code | County | Wells |
|------|--------|-------|-|------|--------|-------|
| 001 | Barbour | 4,077 | | 053 | Mason | 708 |
| 005 | Boone | 3,373 | | 055 | Mercer | 511 |
| 007 | Braxton | 3,338 | | 057 | Mineral | 169 |
| 009 | Brooke | 400 | | 059 | Mingo | 2,814 |
| 011 | Cabell | 1,372 | | 061 | Monongalia | 2,942 |
| 013 | Calhoun | 5,853 | | 063 | Monroe | 23 |
| 015 | Clay | 4,485 | | 065 | Morgan | 13 |
| 017 | Doddridge | 8,289 | | 067 | Nicholas | 1,362 |
| 019 | Fayette | 1,292 | | 069 | Ohio | 434 |
| 021 | Gilmer | 7,074 | | 071 | Pendleton | 39 |
| 023 | Grant | 76 | | 073 | Pleasants | 3,305 |
| 025 | Greenbrier | 83 | | 075 | Pocahontas | 108 |
| 027 | Hampshire | 71 | | 077 | Preston | 836 |
| 029 | Hancock | 293 | | 079 | Putnam | 2,002 |
| 031 | Hardy | 59 | | 081 | Raleigh | 2,134 |
| 033 | Harrison | 8,157 | | 083 | Randolph | 1,522 |
| 035 | Jackson | 4,302 | | 085 | Ritchie | 12,881 |
| 039 | Kanawha | 8,740 | | 087 | Roane | 7,047 |
| 041 | Lewis | 7,362 | | 089 | Summers | 22 |
| 043 | Lincoln | 5,012 | | 091 | Taylor | 1,778 |
| 045 | Logan | 2,961 | | 093 | Tucker | 173 |
| 047 | Marion | 3,290 | | 095 | Tyler | 3,890 |
| 049 | Marshall | 3,355 | | 097 | Upshur | 4,773 |
| 051 | McDowell | 3,775 | | 099 | Wayne | 3,120 |
| | | | | 101 | Webster | 192 |
| | | | | 103 | Wetzel | 5,119 |
| | | | | 105 | Wirt | 2,001 |
| | | | | 107 | Wood | 2,341 |
| | | | | 109 | Wyoming | 3,919 |

**Top 5 counties by well count:** Ritchie (12,881), Kanawha (8,740),
Doddridge (8,289), Harrison (8,157), Lewis (7,362).

---

## ArcGIS REST Query Syntax

### Base Query URL

```
POST https://tagis.dep.wv.gov/arcgis/rest/services/WVDEP_enterprise/oil_gas/MapServer/{layerId}/query
```

### Query Parameters

| Parameter | Required | Description | Example |
|-----------|----------|-------------|---------|
| where | Yes | SQL WHERE clause | `county='049'` |
| outFields | No | Comma-separated field list (default: none) | `permitid,api,wellstatus` or `*` |
| f | Yes | Response format | `json`, `geoJSON`, `PBF` |
| resultRecordCount | No | Max records to return (server max: 3000) | `100` |
| resultOffset | No | Pagination offset | `3000` |
| returnGeometry | No | Include geometry (default: true) | `false` |
| returnCountOnly | No | Return only the count | `true` |
| geometry | No | Geometry filter (envelope, point, polygon) | See spatial query examples |
| geometryType | No | Geometry type | `esriGeometryEnvelope` |
| inSR | No | Input spatial reference WKID | `4326` (for lat/lon) |
| outSR | No | Output spatial reference WKID | `4326` (for lat/lon) |
| spatialRel | No | Spatial relationship | `esriSpatialRelIntersects` |
| orderByFields | No | Sort fields | `issuedate DESC` |
| groupByFieldsForStatistics | No | GROUP BY fields | `county` |
| outStatistics | No | Aggregate statistics JSON | See statistics examples |

**Server limit:** maxRecordCount = 3000 per request. Use resultOffset for pagination.

### WHERE Clause Examples

```sql
-- All wells in Marshall County
county = '049'

-- Active Marcellus wells
wellstatus = 'Active Well' AND marcellus = 'y'

-- Horizontal wells targeting Marcellus Shale
welltype IN ('Horizontal', 'Horizontal 6A') AND formation LIKE '%Marcellus%'

-- Wells permitted after 2020
issuedate >= '2020/01/01'

-- Brine disposal wells
welluse = 'Brine Disposal'

-- Wells by operator (case-sensitive)
respparty LIKE '%EQT%'

-- All wells (no filter)
1=1
```

### Spatial Query Examples

**Bounding box with WGS84 lat/lon:**
```bash
curl -s "https://tagis.dep.wv.gov/arcgis/rest/services/WVDEP_enterprise/oil_gas/MapServer/7/query" \
  --data-urlencode "geometry=-80.2,39.5,-79.8,39.8" \
  --data-urlencode "geometryType=esriGeometryEnvelope" \
  --data-urlencode "inSR=4326" \
  --data-urlencode "spatialRel=esriSpatialRelIntersects" \
  --data-urlencode "outFields=permitid,api,county,wellstatus,formation" \
  --data-urlencode "resultRecordCount=100" \
  --data-urlencode "f=json"
```

**Point buffer (wells within radius):**
```bash
curl -s "https://tagis.dep.wv.gov/arcgis/rest/services/WVDEP_enterprise/oil_gas/MapServer/7/query" \
  --data-urlencode "geometry={\"x\":-80.0,\"y\":39.6,\"spatialReference\":{\"wkid\":4326}}" \
  --data-urlencode "geometryType=esriGeometryPoint" \
  --data-urlencode "inSR=4326" \
  --data-urlencode "spatialRel=esriSpatialRelIntersects" \
  --data-urlencode "distance=5" \
  --data-urlencode "units=esriSRUnit_StatuteMile" \
  --data-urlencode "outFields=*" \
  --data-urlencode "f=json"
```

### Statistics Examples

**Count wells by county:**
```bash
curl -s "https://tagis.dep.wv.gov/arcgis/rest/services/WVDEP_enterprise/oil_gas/MapServer/7/query" \
  --data-urlencode "where=1=1" \
  --data-urlencode "groupByFieldsForStatistics=county" \
  --data-urlencode 'outStatistics=[{"statisticType":"count","onStatisticField":"objectid","outStatisticFieldName":"cnt"}]' \
  --data-urlencode "orderByFields=cnt DESC" \
  --data-urlencode "f=json"
```

**Count active Marcellus wells by formation:**
```bash
curl -s "https://tagis.dep.wv.gov/arcgis/rest/services/WVDEP_enterprise/oil_gas/MapServer/7/query" \
  --data-urlencode "where=wellstatus='Active Well' AND formation <> 'NA'" \
  --data-urlencode "groupByFieldsForStatistics=formation" \
  --data-urlencode 'outStatistics=[{"statisticType":"count","onStatisticField":"objectid","outStatisticFieldName":"cnt"}]' \
  --data-urlencode "orderByFields=cnt DESC" \
  --data-urlencode "resultRecordCount=20" \
  --data-urlencode "f=json"
```

### Pagination

The server returns a maximum of 3,000 records per request. Use `resultOffset`
to paginate:

```bash
# Page 1: records 0-2999
curl -s ".../MapServer/7/query" \
  --data-urlencode "where=county='085'" \
  --data-urlencode "outFields=*" \
  --data-urlencode "resultRecordCount=3000" \
  --data-urlencode "resultOffset=0" \
  --data-urlencode "f=json"

# Page 2: records 3000-5999
curl -s ".../MapServer/7/query" \
  --data-urlencode "where=county='085'" \
  --data-urlencode "outFields=*" \
  --data-urlencode "resultRecordCount=3000" \
  --data-urlencode "resultOffset=3000" \
  --data-urlencode "f=json"
```

Check `exceededTransferLimit` in the response — if `true`, more records exist.

---

## Common Curl Patterns

### Get total count

```bash
curl -s "https://tagis.dep.wv.gov/arcgis/rest/services/WVDEP_enterprise/oil_gas/MapServer/7/query" \
  --data-urlencode "where=1=1" \
  --data-urlencode "returnCountOnly=true" \
  --data-urlencode "f=json"
```

### Get records without geometry (faster)

```bash
curl -s "https://tagis.dep.wv.gov/arcgis/rest/services/WVDEP_enterprise/oil_gas/MapServer/7/query" \
  --data-urlencode "where=wellstatus='Active Well' AND county='049'" \
  --data-urlencode "outFields=permitid,api,welltype,welluse,formation,respparty,issuedate" \
  --data-urlencode "returnGeometry=false" \
  --data-urlencode "resultRecordCount=100" \
  --data-urlencode "f=json"
```

### Get GeoJSON for mapping

```bash
curl -s "https://tagis.dep.wv.gov/arcgis/rest/services/WVDEP_enterprise/oil_gas/MapServer/7/query" \
  --data-urlencode "where=marcellus='y' AND wellstatus='Active Well'" \
  --data-urlencode "outFields=permitid,api,respparty,formation" \
  --data-urlencode "outSR=4326" \
  --data-urlencode "f=geoJSON"
```
