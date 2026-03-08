# ODNR Oil and Gas Wells — Service Schema and Query Reference

## Primary Endpoint

```
https://gis.ohiodnr.gov/arcgis/rest/services/DOG_Services/Oilgas_Wells_public/MapServer
```

- **Total records:** 241,949 wells statewide
- **Max per request:** 1,000 records
- **Auth:** None required (public endpoint)
- **Server type:** ArcGIS MapServer

---

## Layer Summary

| ID | Layer Name | Records | Geometry | Use |
|----|-----------|---------|----------|-----|
| 0 | All Wells by Type | 241,949 | Point | Primary query layer |
| 1 | Active Wells | ~65,000 | Point | Filtered: active status only |
| 2 | Inactive Wells | ~45,000 | Point | Filtered: inactive status |
| 3 | Horizontal Wells | ~3,500 | Point | Filtered: horizontal orientation |
| 4 | Vertical Wells | ~230,000 | Point | Filtered: vertical orientation |
| 5 | Directional Wells | ~5,000 | Point | Filtered: directional wells |
| 6 | Permit Wells | ~10,000 | Point | Permitted, not yet drilled |
| 7 | Plugged Wells | ~90,000 | Point | Plugged and abandoned |
| 8 | Injection Wells | ~4,000 | Point | Class II injection wells |
| 9 | Gas Storage Wells | ~3,000 | Point | Storage wells |
| 10 | Monitoring Wells | ~1,000 | Point | Monitoring/observation |
| 11 | Brine Wells | ~500 | Point | Brine production wells |
| 12 | Orphan Wells | ~800 | Point | Orphaned wells (no responsible operator) |

**Layer 0 (All Wells by Type) is the primary query target** — it contains
all well records regardless of status or type. Layers 1-12 are filtered
subsets based on status, orientation, or purpose.

---

## Key Fields (Layer 0)

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| API_WELLNO | String | 14-digit API well number | "34013200010000" |
| MapSymbol_DESC | String | Well type/symbol description | "Gas, Horizontal" |
| WL_STATUS_DESC | String | Current well status | "Producing" |
| WL_CNTY | String | County name | "Belmont" |
| WL_TWP | String | Township name | "Mead" |
| CO_NAME | String | Company/operator name | "ASCENT RESOURCES UTICA LLC" |
| WH_LAT | Double | Wellhead latitude (WGS84) | 39.9854 |
| WH_LONG | Double | Wellhead longitude (WGS84) | -80.8532 |
| ProposedFormation | String | Target formation at permit | "Utica/Pt Pleasant" |
| ProducingFormation1 | String | Primary producing formation | "Utica/Pt Pleasant" |
| ProducingFormation2 | String | Secondary producing formation | "Marcellus" |
| Utica_Shale | String | Utica Shale flag | "Yes" or "No" |
| Marcellus_Shale | String | Marcellus Shale flag | "Yes" or "No" |
| Last_Nonzero_Production_Year | Integer | Most recent year with production | 2023 |
| Last_Production_Quarter | String | Most recent production quarter | "2023Q4" |
| OBJECTID | Integer | Internal row ID | 123456 |

### Additional Fields Available

| Field | Type | Description |
|-------|------|-------------|
| WL_PERMIT_NO | String | ODNR permit number |
| WL_TYPE_DESC | String | Well type description |
| WL_CLASS_DESC | String | Well class description |
| PERMIT_DT | Date | Permit issue date |
| SPUD_DT | Date | Spud date |
| COMPLETION_DT | Date | Completion date |
| PLUG_DT | Date | Plug date (if plugged) |
| TOTAL_DEPTH | Double | Total measured depth (feet) |
| TRUE_VERT_DEPTH | Double | True vertical depth (feet) |
| LATERAL_LENGTH | Double | Horizontal lateral length (feet) |

---

## Key Enumerated Values

### WL_STATUS_DESC (Well Status)

| Value | Description | Relevance |
|-------|-------------|-----------|
| Producing | Currently producing | High — active well near mineral parcel |
| Shut In | Temporarily shut in | Medium — was producing, may restart |
| Permitted | Permitted, not yet drilled | Medium — planned activity |
| Drilling | Currently being drilled | High — active development |
| Completed | Completed, not yet producing | Medium — imminent production |
| Plugged | Plugged and abandoned | Low — no current activity |
| Inactive | Not currently producing | Low — may be dormant |
| Orphan | No responsible operator | Low — potential environmental liability |

### MapSymbol_DESC (Well Type)

| Value | Description |
|-------|-------------|
| Gas, Horizontal | Horizontal gas well (Utica/Marcellus) |
| Gas, Vertical | Vertical gas well |
| Oil, Horizontal | Horizontal oil well |
| Oil, Vertical | Vertical oil well |
| Gas, Directional | Directional gas well |
| Injection Well | Class II disposal/EOR |
| Gas Storage | Underground gas storage |
| Plugged | Plugged well |
| Brine | Brine production |

### Key Formations

| Formation | Well Count | Notes |
|-----------|-----------|-------|
| Utica/Pt Pleasant | ~3,200 | Primary unconventional target |
| Marcellus | ~200 | Less developed than in WV/PA |
| Clinton | ~45,000 | Historic conventional target |
| Berea | ~15,000 | Shallow conventional sandstone |
| Trenton | ~8,000 | Deep carbonate target |
| Knox Dolomite | ~5,000 | Conventional target |
| Oriskany | ~3,000 | Conventional sandstone |
| Devonian Shale | ~2,000 | Shallow gas |

---

## Working curl Examples

**Count all wells:**
```bash
curl -s "https://gis.ohiodnr.gov/arcgis/rest/services/DOG_Services/Oilgas_Wells_public/MapServer/0/query" \
  --data-urlencode "where=1=1" \
  --data-urlencode "returnCountOnly=true" \
  --data-urlencode "f=json"
```

**Active Utica wells in Belmont County:**
```bash
curl -s "https://gis.ohiodnr.gov/arcgis/rest/services/DOG_Services/Oilgas_Wells_public/MapServer/0/query" \
  --data-urlencode "where=WL_CNTY='Belmont' AND Utica_Shale='Yes' AND WL_STATUS_DESC='Producing'" \
  --data-urlencode "outFields=API_WELLNO,MapSymbol_DESC,WL_STATUS_DESC,CO_NAME,ProducingFormation1,WH_LAT,WH_LONG,Last_Nonzero_Production_Year" \
  --data-urlencode "returnGeometry=false" \
  --data-urlencode "resultRecordCount=50" \
  --data-urlencode "f=json"
```

**Find wells within 1 mile of a point (spatial query):**
```bash
curl -s "https://gis.ohiodnr.gov/arcgis/rest/services/DOG_Services/Oilgas_Wells_public/MapServer/0/query" \
  --data-urlencode "geometry=-80.85,39.95" \
  --data-urlencode "geometryType=esriGeometryPoint" \
  --data-urlencode "inSR=4326" \
  --data-urlencode "spatialRel=esriSpatialRelIntersects" \
  --data-urlencode "distance=1609.34" \
  --data-urlencode "units=esriSRUnit_Meter" \
  --data-urlencode "where=WL_STATUS_DESC='Producing'" \
  --data-urlencode "outFields=API_WELLNO,MapSymbol_DESC,CO_NAME,ProducingFormation1,WH_LAT,WH_LONG" \
  --data-urlencode "returnGeometry=false" \
  --data-urlencode "resultRecordCount=50" \
  --data-urlencode "f=json"
```

**Horizontal wells in target counties:**
```bash
curl -s "https://gis.ohiodnr.gov/arcgis/rest/services/DOG_Services/Oilgas_Wells_public/MapServer/3/query" \
  --data-urlencode "where=WL_CNTY IN ('Belmont','Carroll','Harrison','Jefferson','Monroe','Noble','Columbiana','Guernsey')" \
  --data-urlencode "outFields=API_WELLNO,WL_CNTY,CO_NAME,ProducingFormation1,WL_STATUS_DESC,Last_Nonzero_Production_Year" \
  --data-urlencode "returnGeometry=false" \
  --data-urlencode "resultRecordCount=100" \
  --data-urlencode "f=json"
```

**Aggregate wells by county:**
```bash
curl -s "https://gis.ohiodnr.gov/arcgis/rest/services/DOG_Services/Oilgas_Wells_public/MapServer/0/query" \
  --data-urlencode "where=1=1" \
  --data-urlencode "groupByFieldsForStatistics=WL_CNTY" \
  --data-urlencode 'outStatistics=[{"statisticType":"count","onStatisticField":"OBJECTID","outStatisticFieldName":"cnt"}]' \
  --data-urlencode "orderByFields=cnt DESC" \
  --data-urlencode "f=json"
```

**Aggregate Utica wells by operator:**
```bash
curl -s "https://gis.ohiodnr.gov/arcgis/rest/services/DOG_Services/Oilgas_Wells_public/MapServer/0/query" \
  --data-urlencode "where=Utica_Shale='Yes' AND WL_STATUS_DESC='Producing'" \
  --data-urlencode "groupByFieldsForStatistics=CO_NAME" \
  --data-urlencode 'outStatistics=[{"statisticType":"count","onStatisticField":"OBJECTID","outStatisticFieldName":"cnt"}]' \
  --data-urlencode "orderByFields=cnt DESC" \
  --data-urlencode "resultRecordCount=20" \
  --data-urlencode "f=json"
```

---

## Production Data Context

The ODNR well service includes `Last_Nonzero_Production_Year` and
`Last_Production_Quarter` fields that indicate whether a well has recent
production. These fields are critical for:

1. **Dormant Mineral Act screening** — if a well on or near a mineral parcel
   has not produced in 20+ years, the mineral rights may be subject to
   reversion under ORC 5301.56
2. **Investment value assessment** — recent production near a mineral parcel
   indicates active development and potential lease value
3. **Operator activity** — the `CO_NAME` field reveals which operators are
   active in the area, relevant for lease negotiations

Full production volume data (BBL, MCF) is available through the ODNR Division
of Oil and Gas Resources production reporting system, but is not included in
this MapServer layer.

---

## Pagination

The ODNR MapServer returns a maximum of **1,000 records per request**.
This is lower than the OGRIP limit (2,000). Use `resultOffset` for pagination:

```python
offset = 0
all_records = []
while True:
    # Query with resultOffset=offset, resultRecordCount=1000
    features = response["features"]
    all_records.extend(features)
    if len(features) < 1000 or not response.get("exceededTransferLimit"):
        break
    offset += 1000
```

For county-level queries in the 8 target counties, expect 200-800 wells
per county when filtered by Utica/Marcellus — usually fits in a single request.
Statewide queries (241,949 wells) require extensive pagination; prefer
statistics queries or county-level filtering.
