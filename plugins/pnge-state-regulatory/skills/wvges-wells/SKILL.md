---
name: wvges-wells
description: >
  Query West Virginia oil and gas well data from the WVDEP ArcGIS REST MapServer.
  Use this skill when the user asks about WV wells, Marcellus Shale permits,
  horizontal drilling in West Virginia, well counts by county, brine disposal
  wells, well operators, formation targets, Utica or Point Pleasant wells,
  Appalachian basin well data, WVGES pipeline data, WV oil and gas permits,
  plugged or abandoned wells, coal bed methane wells, or any West Virginia
  petroleum and natural gas well information. Covers 153,000+ wells with records
  back to the 1860s including permit status, operator, formation, well type, and
  coordinates. Produces tabular results with narrative summaries.
---

# WVGES Oil and Gas Well Data

Queries West Virginia oil and gas well records from the WVDEP (West Virginia
Department of Environmental Protection) Office of Oil and Gas ArcGIS REST
MapServer. The database contains 153,000+ wells in the RBDMS (Risk Based Data
Management System) plus 54,000+ legacy WVGES wells, with records dating back
to the 1860s.

## Credential

**None required.** The WVDEP ArcGIS REST service is publicly accessible with
no API key or authentication.

---

## Data Source

**Primary endpoint:**
```
https://tagis.dep.wv.gov/arcgis/rest/services/WVDEP_enterprise/oil_gas/MapServer
```

**Web application:** https://tagis.dep.wv.gov/oog/

**WVGES Pipeline (individual well lookup):** https://www.wvgs.wvnet.edu/pipe2/

**Source database:** RBDMS, adopted by WVDEP Office of Oil and Gas in August
2016. ArcGIS Server version 11.5.

### Layer Summary

| ID | Layer Name | Records | Geometry | Use |
|----|-----------|---------|----------|-----|
| 0 | Horizontal Only | 9,406 | Point | Horizontal and 6A wells |
| 1 | Active Status Only | 66,217 | Point | Currently active wells |
| 2 | Other than Active | 37,638 | Point | Non-active wells |
| 3 | Coal Bed Methane | 2,336 | Point | CBM wells |
| 4 | Plugged | 49,412 | Point | Plugged wells |
| 5 | Not in WVDEP Database | 54,887 | Point | Legacy WVGES wells |
| 6 | Horizontal Laterals | 5,444 | Polyline | Lateral paths with endpoints |
| 7 | **All DEP Wells** | **153,267** | Point | **Primary query layer** |
| 8 | Brine Disposal | 396 | Point | Brine disposal wells |
| 10 | Well Pads | 1,023 | Polygon | Well pad boundaries |

**Layer 7 (All DEP Wells) is the primary query target** — it contains the full
RBDMS dataset with no display scale restrictions. Layers 0-4 and 8 are filtered
subsets. Layer 5 is a separate dataset of legacy WVGES wells not yet in RBDMS.

---

## API Structure

**Query URL pattern:**
```
POST https://tagis.dep.wv.gov/arcgis/rest/services/WVDEP_enterprise/oil_gas/MapServer/{layerId}/query
```

**Key parameters:**

| Parameter | Required | Description | Example |
|-----------|----------|-------------|---------|
| where | Yes | SQL WHERE clause | `county='049'` |
| outFields | No | Comma-separated fields | `permitid,api,wellstatus` or `*` |
| f | Yes | Response format | `json` or `geoJSON` |
| resultRecordCount | No | Max records (server limit: 3000) | `100` |
| resultOffset | No | Pagination offset | `3000` |
| returnGeometry | No | Include coordinates (default: true) | `false` |
| returnCountOnly | No | Return count only | `true` |
| geometry | No | Spatial filter geometry | `-80.2,39.5,-79.8,39.8` |
| geometryType | No | Geometry type | `esriGeometryEnvelope` |
| inSR | No | Input spatial reference | `4326` (WGS84 lat/lon) |
| outSR | No | Output spatial reference | `4326` |
| spatialRel | No | Spatial relationship | `esriSpatialRelIntersects` |
| groupByFieldsForStatistics | No | GROUP BY field | `county` |
| outStatistics | No | Aggregation JSON | See examples below |

**Server limit:** 3,000 records per request. Use `resultOffset` for pagination.
Check `exceededTransferLimit` in the response to know if more records exist.

### Working curl Examples

**Count all wells:**
```bash
curl -sk "https://tagis.dep.wv.gov/arcgis/rest/services/WVDEP_enterprise/oil_gas/MapServer/7/query" \
  --data-urlencode "where=1=1" \
  --data-urlencode "returnCountOnly=true" \
  --data-urlencode "f=json"
```

**Query active Marcellus wells:**
```bash
curl -sk "https://tagis.dep.wv.gov/arcgis/rest/services/WVDEP_enterprise/oil_gas/MapServer/7/query" \
  --data-urlencode "where=marcellus='y' AND wellstatus='Active Well'" \
  --data-urlencode "outFields=permitid,api,county,welltype,welluse,respparty,formation,issuedate" \
  --data-urlencode "returnGeometry=false" \
  --data-urlencode "resultRecordCount=20" \
  --data-urlencode "f=json"
```

**Query wells in a county:**
```bash
curl -sk "https://tagis.dep.wv.gov/arcgis/rest/services/WVDEP_enterprise/oil_gas/MapServer/7/query" \
  --data-urlencode "where=county='049'" \
  --data-urlencode "outFields=permitid,api,welltype,wellstatus,welluse,formation,respparty" \
  --data-urlencode "returnGeometry=false" \
  --data-urlencode "resultRecordCount=50" \
  --data-urlencode "f=json"
```

**Spatial query (bounding box with WGS84 lat/lon):**
```bash
curl -sk "https://tagis.dep.wv.gov/arcgis/rest/services/WVDEP_enterprise/oil_gas/MapServer/7/query" \
  --data-urlencode "geometry=-80.2,39.5,-79.8,39.8" \
  --data-urlencode "geometryType=esriGeometryEnvelope" \
  --data-urlencode "inSR=4326" \
  --data-urlencode "spatialRel=esriSpatialRelIntersects" \
  --data-urlencode "outFields=permitid,api,county,wellstatus,formation" \
  --data-urlencode "resultRecordCount=100" \
  --data-urlencode "f=json"
```

**Aggregate wells by county:**
```bash
curl -sk "https://tagis.dep.wv.gov/arcgis/rest/services/WVDEP_enterprise/oil_gas/MapServer/7/query" \
  --data-urlencode "where=1=1" \
  --data-urlencode "groupByFieldsForStatistics=county" \
  --data-urlencode 'outStatistics=[{"statisticType":"count","onStatisticField":"objectid","outStatisticFieldName":"cnt"}]' \
  --data-urlencode "orderByFields=cnt DESC" \
  --data-urlencode "f=json"
```

**Wells by operator (partial match):**
```bash
curl -sk "https://tagis.dep.wv.gov/arcgis/rest/services/WVDEP_enterprise/oil_gas/MapServer/7/query" \
  --data-urlencode "where=respparty LIKE '%EQT%' AND wellstatus='Active Well'" \
  --data-urlencode "outFields=permitid,api,county,welltype,formation,issuedate" \
  --data-urlencode "returnGeometry=false" \
  --data-urlencode "resultRecordCount=20" \
  --data-urlencode "f=json"
```

**Brine disposal wells (relevant for produced water research):**
```bash
curl -sk "https://tagis.dep.wv.gov/arcgis/rest/services/WVDEP_enterprise/oil_gas/MapServer/8/query" \
  --data-urlencode "where=1=1" \
  --data-urlencode "outFields=*" \
  --data-urlencode "returnGeometry=false" \
  --data-urlencode "f=json"
```

---

## Key Fields (Layer 7)

| Field | Type | Description | Example Values |
|-------|------|-------------|----------------|
| permitid | String | County-permit code | "049-01310" |
| api | String | API well number (47=WV) | "4704901310" |
| county | String | 3-digit FIPS county code | "049" (Marshall) |
| welltype | String | Well orientation | Vertical, Horizontal, Horizontal 6A, Coal Bed Methane Well |
| welluse | String | Well purpose | Gas Production, Oil Production, Brine Disposal, Storage |
| welldepth | String | Depth category (text) | "Shallow less than 3,000 feet", "Deep" |
| permittype | String | Permit action type | Vertical Well, Horizontal Well, Plugging, Re-Work |
| issuedate | String | Permit issue date | "2020/01/15" (YYYY/MM/DD format) |
| compdate | String | Completion date | "2020/06/30" or "None" |
| respparty | String | Operator name | "EQT PRODUCTION COMPANY" |
| wellstatus | String | Current status | Active Well, Plugged, Abandoned Well, Shutin |
| farmname | String | Farm/lease name | "SMITH, JOHN" |
| wellnumber | String | Well number on lease | "1A" |
| formation | String | Target formation(s) | "Marcellus Shale", "NA", "Berea Sandstone,Gordon" |
| marcellus | String | Marcellus flag | "y"=yes, "n"=no, "u"=unknown |
| wellx | Double | UTM Easting (NAD83 Zone 17N) | 457059.1 |
| welly | Double | UTM Northing (NAD83 Zone 17N) | 4229604.4 |

See `references/arcgis_rest.md` for full field definitions, layer-specific fields,
enumerated values, and county FIPS code mapping.

---

## Key Enumerated Values

### wellstatus

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
| Point Pleasant | 279 |
| Oriskany | 279 |
| Utica | 25 |

---

## Workflow

### Step 1 — Resolve Intent

Map the user's question to query parameters:

| User Request | WHERE Clause | Layer |
|-------------|-------------|-------|
| "Marcellus wells in WV" | `marcellus='y'` | 7 |
| "Wells in Marshall County" | `county='049'` | 7 |
| "Active horizontal wells" | `wellstatus='Active Well' AND welltype IN ('Horizontal','Horizontal 6A')` | 7 |
| "EQT wells" | `respparty LIKE '%EQT%'` | 7 |
| "Brine disposal wells" | `welluse='Brine Disposal'` | 7 or 8 |
| "Wells near Morgantown" | Spatial query with bbox around 39.63,-79.96 | 7 |
| "How many wells per county?" | Statistics query grouping by `county` | 7 |
| "Utica/Point Pleasant wells" | `formation LIKE '%Point Pleasant%' OR formation LIKE '%Utica%'` | 7 |
| "Wells permitted since 2020" | `issuedate >= '2020/01/01'` | 7 |

For county lookups, convert county names to 3-digit FIPS codes using the
reference table in `references/arcgis_rest.md`.

### Step 2 — Fetch Count

Always check the total count first to inform the user and decide on pagination:

```bash
curl -sk "https://tagis.dep.wv.gov/arcgis/rest/services/WVDEP_enterprise/oil_gas/MapServer/7/query" \
  --data-urlencode "where=<WHERE_CLAUSE>" \
  --data-urlencode "returnCountOnly=true" \
  --data-urlencode "f=json"
```

If count exceeds 3,000, inform the user and either:
- Paginate using `resultOffset` (for full extraction)
- Add filters to narrow the result set
- Use statistics queries for aggregate analysis

### Step 3 — Fetch Data

Build the query with appropriate filters. Default behavior:
- Use Layer 7 unless the question specifically targets laterals (6), pads (10),
  or legacy wells (5)
- Set `returnGeometry=false` unless coordinates are needed
- Request `resultRecordCount=100` by default, increase for bulk queries
- Include the most relevant fields rather than `*` to reduce response size

```bash
curl -sk "https://tagis.dep.wv.gov/arcgis/rest/services/WVDEP_enterprise/oil_gas/MapServer/7/query" \
  --data-urlencode "where=<WHERE_CLAUSE>" \
  --data-urlencode "outFields=permitid,api,county,welltype,welluse,wellstatus,formation,respparty,issuedate" \
  --data-urlencode "returnGeometry=false" \
  --data-urlencode "resultRecordCount=100" \
  --data-urlencode "f=json"
```

For statistics/aggregations:
```bash
curl -sk "https://tagis.dep.wv.gov/arcgis/rest/services/WVDEP_enterprise/oil_gas/MapServer/7/query" \
  --data-urlencode "where=<WHERE_CLAUSE>" \
  --data-urlencode "groupByFieldsForStatistics=<FIELD>" \
  --data-urlencode 'outStatistics=[{"statisticType":"count","onStatisticField":"objectid","outStatisticFieldName":"cnt"}]' \
  --data-urlencode "orderByFields=cnt DESC" \
  --data-urlencode "f=json"
```

### Step 4 — Parse and Output

Response structure:
```json
{
  "displayFieldName": "farmname",
  "fieldAliases": { "permitid": "PermitID" },
  "geometryType": "esriGeometryPoint",
  "spatialReference": { "wkid": 102100, "latestWkid": 3857 },
  "features": [
    {
      "attributes": {
        "permitid": "049-01310",
        "api": "4704901310",
        "county": "049",
        "welltype": "Vertical",
        "wellstatus": "Active Well"
      },
      "geometry": { "x": -8905123.45, "y": 4832567.89 }
    }
  ],
  "exceededTransferLimit": false
}
```

Extract the `features[].attributes` for tabular display. If
`exceededTransferLimit` is `true`, paginate by incrementing `resultOffset`.

---

## Output Format

**Format: Raw Data Table + Narrative Summary**

Present results as a markdown table (cap at ~20 rows), then a narrative summary.

**Example output:**

```
## Active Marcellus Wells in Marshall County

| Permit ID | API | Well Type | Status | Operator | Formation | Issued |
|-----------|-----|-----------|--------|----------|-----------|--------|
| 049-02100 | 4704902100 | Horizontal 6A | Active Well | EQT PRODUCTION CO | Marcellus Shale | 2018/03/15 |
| 049-02050 | 4704902050 | Horizontal | Active Well | SOUTHWESTERN ENERGY | Marcellus Shale | 2016/11/22 |
| ... | ... | ... | ... | ... | ... | ... |

**Summary:** Marshall County (FIPS 049) has 3,355 total wells, of which 900
are active. Among active wells, 45 target the Marcellus Shale, predominantly
Horizontal 6A wells permitted under WV Code 22-6A. The top operators are EQT
Production Company and Southwestern Energy. Most Marcellus permits were issued
between 2010 and 2020. Note: the formation field is "NA" for approximately 85%
of records, especially older vertical wells — actual Marcellus well counts may
be higher than reported.
```

For aggregate queries, present a summary table with counts and a brief analysis
of the distribution.

---

## Pagination

The server returns a maximum of 3,000 records per request. To retrieve larger
datasets, paginate using `resultOffset`:

```python
offset = 0
all_records = []
while True:
    # fetch with resultOffset=offset and resultRecordCount=3000
    features = response["features"]
    all_records.extend(features)
    if len(features) < 3000 or not response.get("exceededTransferLimit"):
        break
    offset += 3000
```

Warn the user if the dataset exceeds ~10,000 records and suggest narrowing
filters or using statistics queries instead.

---

## Error Handling

| HTTP / Error | Meaning | Action |
|-------------|---------|--------|
| 200 + `error` in JSON | Bad query syntax (invalid field name, malformed WHERE) | Check field names against Layer 7 schema; fix WHERE clause |
| 200 + `exceededTransferLimit: true` | More records than `resultRecordCount` | Paginate with `resultOffset` or narrow filters |
| 200 + empty `features` array | No matching records | Verify filter values (check case sensitivity, FIPS codes) |
| 400 | Malformed request | Check parameter encoding, especially `outStatistics` JSON |
| 500 | Server error or service unavailable | Retry after brief wait; if persistent, note the WVDEP server may be down |
| SSL certificate error | Self-signed certificate | Use `-k` flag with curl or disable SSL verification |
| Timeout | Large result set or server load | Reduce `resultRecordCount`, add filters, or use `returnGeometry=false` |

**Important:** The WVDEP ArcGIS server uses a certificate that may not be
in all trust stores. Curl commands should include `-k` (or `--insecure`) if
certificate errors occur. In Python, use a custom SSL context with verification
disabled.

---

## Caveats and Data Quality Notes

1. **Formation data is sparse.** Approximately 85% of well records have
   `formation='NA'`, primarily older vertical wells. Formation data is more
   complete for wells permitted after ~2010, especially horizontal Marcellus
   and Utica wells.

2. **Dates are strings, not date types.** The `issuedate` and `compdate` fields
   are stored as strings in `YYYY/MM/DD` format. Many records have `"None"` for
   completion date. Date comparisons in WHERE clauses work as string comparisons.

3. **County codes are FIPS, not names.** The `county` field uses 3-digit
   zero-padded FIPS county codes (e.g., "049" for Marshall, "061" for
   Monongalia). See `references/arcgis_rest.md` for the full mapping.

4. **Legacy data quality.** Wells from the 1800s and early 1900s may have
   imprecise locations, missing operators, and "Not Available" for many fields.
   Over 15,000 wells are marked "Never Drilled" (permitted but never spud).

5. **Layer 5 is separate.** The 54,887 wells in Layer 5 (Not in WVDEP Database)
   are legacy WVGES records not yet migrated to RBDMS. They have a different
   field schema with additional location fields but may overlap or conflict
   with Layer 7 records.

6. **Coordinate systems.** The service returns geometry in Web Mercator
   (WKID 3857). Use `inSR=4326` for WGS84 lat/lon input and `outSR=4326`
   for WGS84 output. The `wellx`/`welly` attribute fields contain NAD83 UTM
   Zone 17N coordinates.

7. **No production data in this service.** The ArcGIS MapServer provides well
   metadata (permits, status, operator, formation) but does not include
   production volumes. Production data is available through the WVGES Pipeline
   web app (https://www.wvgs.wvnet.edu/pipe2/) on a per-well basis only.

8. **Marcellus flag limitations.** The `marcellus` field is "u" (unknown) for
   most older wells. Wells targeting the Marcellus as one of multiple zones
   may have `marcellus='y'` even if it is not the primary target. Cross-check
   with the `formation` field when precision matters.

9. **"Horizontal 6A" vs "Horizontal."** "Horizontal 6A" wells (6,832 records)
   are permitted under WV Code 22-6A (Natural Gas Horizontal Well Control Act,
   effective 2011), which has stricter surface disturbance and setback rules.
   "Horizontal" wells (2,574 records) predate this regulation or are governed
   by different statutes.

10. **Server availability.** The legacy WVGES ArcGIS server at
    `atlas.wvgs.wvnet.edu` is intermittently offline. The WVDEP server at
    `tagis.dep.wv.gov` is the reliable primary endpoint.

---

## Implementation Notes

- **Prefer `bash_tool` with `curl` + `jq`** for API calls in Claude's environment
- **Use `-k` flag** with curl to handle the WVDEP SSL certificate
- **Python example** — see `references/python_example.py` (stdlib only: urllib, json)
- **ArcGIS REST reference** — see `references/arcgis_rest.md` for full layer
  schema, enumerated values, county codes, and query syntax
- The service supports `f=geoJSON` for direct GeoJSON output suitable for
  mapping tools
- `outStatistics` must be valid JSON — use single quotes around the curl
  argument and double quotes inside the JSON
- Date filtering uses string comparison: `issuedate >= '2020/01/01'` works
  correctly because dates are stored in `YYYY/MM/DD` format
