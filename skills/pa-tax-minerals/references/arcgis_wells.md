# PA DEP Oil & Gas Wells ArcGIS MapServer

## Service Endpoint

```
https://gis.dep.pa.gov/depgisprd/rest/services/OilGas/OilGasAllStrayGasEGSP/MapServer
```

This service provides Pennsylvania DEP oil and gas well locations including
conventional, unconventional (Marcellus/Utica), and historical wells. The
service covers 223,664 total wells with records spanning from the 1800s to
present.

**Authentication:** None required (public service)

---

## Layers

| ID | Name | Records | Geometry | Use |
|----|------|---------|----------|-----|
| 1 | Unconventional Wells | 15,328 | Point | Marcellus/Utica horizontal wells |
| 2 | Conventional Wells | 173,452 | Point | Vertical conventional wells |
| 3 | All Wells | 223,664 | Point | **Primary query layer** |

**Layer 3 (All Wells) is the primary query target** for comprehensive well
searches. Use Layer 1 for Marcellus/Utica-specific queries.

**Max records per request:** 5,000

---

## Fields — Layer 3 (All Wells)

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| OBJECTID | Integer | Internal ID | 12345 |
| PERMIT_NUMBER | String | PA DEP permit number | "125-28575" |
| WELL_NAME | String | Well name | "SMITH 1H" |
| OPERATOR | String | Current operator | "EQT PRODUCTION COMPANY" |
| WELL_TYPE | String | Well type | "Gas", "Oil", "Gas and Oil" |
| WELL_STATUS | String | Current status | "Active", "Plugged", "Inactive" |
| PERMIT_DATE | Date | Permit issue date (epoch ms) | 1577836800000 |
| SPUD_DATE | Date | Spud date (epoch ms) | 1580515200000 |
| COUNTY | String | County name | "Washington" |
| MUNICIPALITY | String | Municipality/township | "AMWELL TWP" |
| LATITUDE | Double | WGS84 latitude | 40.0123 |
| LONGITUDE | Double | WGS84 longitude | -80.2456 |
| UNCONVENTIONAL_IND | String | Unconventional flag | "Yes", "No" |
| WELL_CONFIG_CODE | String | Configuration | "Horizontal", "Vertical", "Deviated" |
| COAL_IND | String | Coal presence indicator | "Yes", "No" |
| DATE_PLUGGED | Date | Date plugged (epoch ms) | 1609459200000 |
| UIC_ID | String | UIC well identifier | "PAD000123456" |
| UIC_TYPE_DESCRIPTION | String | UIC type | "Class II Disposal" |

### Date Handling

Dates are returned as epoch milliseconds (Unix timestamp * 1000). Convert to
human-readable format:

```python
import datetime
epoch_ms = 1577836800000
dt = datetime.datetime.fromtimestamp(epoch_ms / 1000)
# 2020-01-01 00:00:00
```

In jq: `.PERMIT_DATE / 1000 | strftime("%Y-%m-%d")`

**Null dates** appear as `null` in JSON responses.

---

## Fields — Layer 1 (Unconventional Wells)

Same fields as Layer 3 but filtered to `UNCONVENTIONAL_IND='Yes'` only.
All unconventional wells are also in Layer 3.

---

## Key Enumerated Values

### WELL_STATUS

| Value | Description |
|-------|-------------|
| Active | Currently producing or operating |
| Inactive | Not currently producing but not plugged |
| Plugged | Permanently sealed |
| Abandoned | Abandoned, unknown plugging status |
| Regulatory Inactive Status | Inactive per DEP regulation |
| Not Drilled | Permitted but never spud |
| Drilling | Currently being drilled |
| Completed | Drilling complete, awaiting production |

### WELL_TYPE

| Value | Description |
|-------|-------------|
| Gas | Natural gas well |
| Oil | Oil well |
| Gas and Oil | Dual-producing well |
| Dry Hole | Non-productive well |
| Injection | Injection well (disposal, EOR) |
| Storage | Gas storage well |
| Observation | Monitoring well |
| Other | Other well type |

### UNCONVENTIONAL_IND

| Value | Description |
|-------|-------------|
| Yes | Unconventional well (horizontal, Marcellus/Utica) |
| No | Conventional well (vertical) |

### WELL_CONFIG_CODE

| Value | Description |
|-------|-------------|
| Horizontal | Horizontal well bore |
| Vertical | Vertical well bore |
| Deviated | Deviated/directional well bore |

---

## Query Examples

### Count all wells statewide

```bash
curl -s "https://gis.dep.pa.gov/depgisprd/rest/services/OilGas/OilGasAllStrayGasEGSP/MapServer/3/query" \
  --data-urlencode "where=1=1" \
  --data-urlencode "returnCountOnly=true" \
  --data-urlencode "f=json"
```

### Count unconventional wells by county

```bash
curl -s "https://gis.dep.pa.gov/depgisprd/rest/services/OilGas/OilGasAllStrayGasEGSP/MapServer/3/query" \
  --data-urlencode "where=UNCONVENTIONAL_IND='Yes'" \
  --data-urlencode "groupByFieldsForStatistics=COUNTY" \
  --data-urlencode 'outStatistics=[{"statisticType":"count","onStatisticField":"OBJECTID","outStatisticFieldName":"cnt"}]' \
  --data-urlencode "orderByFields=cnt DESC" \
  --data-urlencode "f=json"
```

### Active unconventional wells in Washington County

```bash
curl -s "https://gis.dep.pa.gov/depgisprd/rest/services/OilGas/OilGasAllStrayGasEGSP/MapServer/3/query" \
  --data-urlencode "where=COUNTY='Washington' AND UNCONVENTIONAL_IND='Yes' AND WELL_STATUS='Active'" \
  --data-urlencode "outFields=PERMIT_NUMBER,WELL_NAME,OPERATOR,WELL_TYPE,WELL_STATUS,WELL_CONFIG_CODE,LATITUDE,LONGITUDE" \
  --data-urlencode "returnGeometry=false" \
  --data-urlencode "resultRecordCount=50" \
  --data-urlencode "f=json"
```

### Wells by operator

```bash
curl -s "https://gis.dep.pa.gov/depgisprd/rest/services/OilGas/OilGasAllStrayGasEGSP/MapServer/3/query" \
  --data-urlencode "where=OPERATOR LIKE '%EQT%' AND WELL_STATUS='Active'" \
  --data-urlencode "outFields=PERMIT_NUMBER,WELL_NAME,COUNTY,WELL_CONFIG_CODE,LATITUDE,LONGITUDE" \
  --data-urlencode "returnGeometry=false" \
  --data-urlencode "resultRecordCount=50" \
  --data-urlencode "f=json"
```

### Spatial query — wells within bounding box (SW PA)

```bash
curl -s "https://gis.dep.pa.gov/depgisprd/rest/services/OilGas/OilGasAllStrayGasEGSP/MapServer/3/query" \
  --data-urlencode "geometry=-80.5,39.7,-79.8,40.2" \
  --data-urlencode "geometryType=esriGeometryEnvelope" \
  --data-urlencode "inSR=4326" \
  --data-urlencode "spatialRel=esriSpatialRelIntersects" \
  --data-urlencode "where=UNCONVENTIONAL_IND='Yes' AND WELL_STATUS='Active'" \
  --data-urlencode "outFields=PERMIT_NUMBER,WELL_NAME,OPERATOR,COUNTY,WELL_CONFIG_CODE" \
  --data-urlencode "returnGeometry=true" \
  --data-urlencode "outSR=4326" \
  --data-urlencode "resultRecordCount=100" \
  --data-urlencode "f=json"
```

### Wells within radius of a point

```bash
curl -s "https://gis.dep.pa.gov/depgisprd/rest/services/OilGas/OilGasAllStrayGasEGSP/MapServer/3/query" \
  --data-urlencode "geometry=-80.18,39.90" \
  --data-urlencode "geometryType=esriGeometryPoint" \
  --data-urlencode "inSR=4326" \
  --data-urlencode "spatialRel=esriSpatialRelIntersects" \
  --data-urlencode "distance=1609.34" \
  --data-urlencode "units=esriSRUnit_Meter" \
  --data-urlencode "where=WELL_STATUS='Active'" \
  --data-urlencode "outFields=PERMIT_NUMBER,WELL_NAME,OPERATOR,COUNTY,WELL_TYPE,WELL_CONFIG_CODE,UNCONVENTIONAL_IND" \
  --data-urlencode "returnGeometry=false" \
  --data-urlencode "resultRecordCount=50" \
  --data-urlencode "f=json"
```

### Aggregate wells by status

```bash
curl -s "https://gis.dep.pa.gov/depgisprd/rest/services/OilGas/OilGasAllStrayGasEGSP/MapServer/3/query" \
  --data-urlencode "where=COUNTY='Greene'" \
  --data-urlencode "groupByFieldsForStatistics=WELL_STATUS" \
  --data-urlencode 'outStatistics=[{"statisticType":"count","onStatisticField":"OBJECTID","outStatisticFieldName":"cnt"}]' \
  --data-urlencode "orderByFields=cnt DESC" \
  --data-urlencode "f=json"
```

---

## Pagination

Max records per request: **5,000**. Use `resultOffset` for pagination:

```bash
# Page 1
curl -s "https://gis.dep.pa.gov/depgisprd/rest/services/OilGas/OilGasAllStrayGasEGSP/MapServer/3/query" \
  --data-urlencode "where=COUNTY='Washington'" \
  --data-urlencode "outFields=PERMIT_NUMBER,WELL_NAME,OPERATOR,WELL_STATUS" \
  --data-urlencode "resultRecordCount=5000" \
  --data-urlencode "resultOffset=0" \
  --data-urlencode "f=json"

# Page 2
curl -s "https://gis.dep.pa.gov/depgisprd/rest/services/OilGas/OilGasAllStrayGasEGSP/MapServer/3/query" \
  --data-urlencode "where=COUNTY='Washington'" \
  --data-urlencode "outFields=PERMIT_NUMBER,WELL_NAME,OPERATOR,WELL_STATUS" \
  --data-urlencode "resultRecordCount=5000" \
  --data-urlencode "resultOffset=5000" \
  --data-urlencode "f=json"
```

Check `exceededTransferLimit` in the response. If `true`, increment
`resultOffset` by 5000 and fetch the next page.

---

## Spatial Reference

- **Native SRS:** Web Mercator (WKID 3857 / 102100)
- **Input/Output:** Use `inSR=4326` and `outSR=4326` for WGS84 lat/lon
- The `LATITUDE` and `LONGITUDE` attribute fields contain WGS84 coordinates
  directly, so `returnGeometry=false` with these fields is often sufficient

---

## Data Quality Notes

1. **Dates are epoch milliseconds.** `PERMIT_DATE`, `SPUD_DATE`, and
   `DATE_PLUGGED` are returned as Unix epoch * 1000. Null dates appear as
   `null`. Date comparisons in WHERE clauses should use date functions or
   epoch values.

2. **County names are mixed case.** The `COUNTY` field uses proper case
   (e.g., "Washington", "Greene"), unlike the Socrata datasets which use
   uppercase.

3. **No production data.** This service provides well metadata only. For
   production volumes, use the PA DEP Production Reports or the PA Open
   Data portal.

4. **Legacy well locations.** Wells from the 1800s and early 1900s may have
   imprecise coordinates. Treat these locations as approximate.

5. **Operator name variations.** Corporate mergers and acquisitions mean the
   same physical operator may appear under multiple names (e.g., Rice Energy
   wells now show as EQT).

6. **Layer 3 includes all wells.** Layers 1 and 2 are filtered subsets.
   Use Layer 3 for comprehensive queries; use Layer 1 when targeting only
   unconventional wells.
