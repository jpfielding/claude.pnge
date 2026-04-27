---
name: odnr-wells
description: >
  Query Ohio oil and gas well data from the Ohio Department of Natural
  Resources Division of Oil and Gas Resources Management via the ODNR ArcGIS
  REST MapServer and public data downloads. Covers Utica Shale, Point Pleasant,
  Clinton Sandstone, Knox Dolomite, and other Ohio formations with well permits,
  operator data, completion status, well type, and location data. Includes
  100,000 plus wells with Appalachian basin context for comparison to West
  Virginia and Pennsylvania production. Use when the user asks about Ohio wells,
  Utica Shale drilling activity, Point Pleasant completions, Ohio oil and gas
  operators, well counts by county, horizontal drilling in Ohio, or ODNR well
  data for Appalachian basin research. Trigger phrases include Ohio Utica wells,
  Point Pleasant Ohio, ODNR well data, Ohio horizontal drilling, oil and gas
  wells in Ohio, Utica production Ohio, Knox formation Ohio, Clinton sandstone
  wells, Columbiana County wells, Guernsey County Ohio wells, Carroll County
  Utica, Ohio well permits, or Appalachian basin Ohio well comparison.
---

# Ohio DNR Oil and Gas Well Data

Data access skill for the Ohio Department of Natural Resources Division of
Oil and Gas Resources Management well database. Ohio is a key Appalachian
basin state for Utica Shale and Point Pleasant formation research.

**Data coverage:** 100,000+ wells, records from 1860s to present. Includes
conventional (Clinton, Knox) and unconventional (Utica, Point Pleasant)
wells, CBM, saltwater disposal, and injection wells.

---

## Credential Resolution

No API key required. ODNR ArcGIS REST services are publicly accessible.

---

## API Structure

### Primary Endpoint: ODNR ArcGIS REST MapServer

```
Base URL: https://gis.ohiodnr.gov/arcgis/rest/services/OGS/OilGasWells/MapServer
```

Get layer list:
```bash
curl -s "https://gis.ohiodnr.gov/arcgis/rest/services/OGS/OilGasWells/MapServer?f=json" \
  | python3 -c "import json,sys; d=json.load(sys.stdin); [print(l['id'], l['name']) for l in d.get('layers',[])]"
```

### Layer Reference (verify against live service)

| Layer ID | Name | Notes |
|----------|------|-------|
| 0 | All Wells | Full well inventory |
| 1 | Utica/Point Pleasant | Horizontal unconventional |
| 2 | Active Wells | Producing wells |
| 3 | Plugged Wells | P&A records |

---

## Workflow

### Step 1 — Resolve Intent

Identify the query target:
- Formation: Utica, Point Pleasant, Clinton, Knox, Berea, Medina, Oriskany
- Geography: county, bounding box, or named field
- Filter: well type (oil, gas, SWD), permit status, operator

### Step 2 — Query Wells by County

```bash
# Query wells in Carroll County (FIPS 019), Utica targets
curl -s "https://gis.ohiodnr.gov/arcgis/rest/services/OGS/OilGasWells/MapServer/0/query" \
  --data-urlencode "where=COUNTY_CODE='019'" \
  --data-urlencode "outFields=PERM_NUM,WELL_NAME,OPERATOR,FORMATION,LATITUDE,LONGITUDE,WELL_TYPE,STATUS" \
  --data-urlencode "resultRecordCount=100" \
  --data-urlencode "f=json"
```

```bash
# Query Utica/Point Pleasant wells statewide (status = Active or Producing)
curl -s "https://gis.ohiodnr.gov/arcgis/rest/services/OGS/OilGasWells/MapServer/0/query" \
  --data-urlencode "where=FORMATION LIKE '%UTICA%' OR FORMATION LIKE '%POINT PLEASANT%'" \
  --data-urlencode "outFields=PERM_NUM,WELL_NAME,OPERATOR,FORMATION,COUNTY_CODE,WELL_TYPE,STATUS,LATITUDE,LONGITUDE" \
  --data-urlencode "resultRecordCount=200" \
  --data-urlencode "orderByFields=PERM_NUM DESC" \
  --data-urlencode "f=json"
```

### Step 3 — Spatial (Bounding Box) Query

```bash
# Wells within bounding box (SW and NE corners: lon_min,lat_min,lon_max,lat_max)
# Example: Carroll/Columbiana county area
curl -s "https://gis.ohiodnr.gov/arcgis/rest/services/OGS/OilGasWells/MapServer/0/query" \
  --data-urlencode "geometry=-81.3,40.5,-80.5,41.0" \
  --data-urlencode "geometryType=esriGeometryEnvelope" \
  --data-urlencode "spatialRel=esriSpatialRelIntersects" \
  --data-urlencode "inSR=4326" \
  --data-urlencode "outFields=PERM_NUM,WELL_NAME,OPERATOR,FORMATION,WELL_TYPE,STATUS" \
  --data-urlencode "resultRecordCount=200" \
  --data-urlencode "f=json"
```

### Step 4 — Parse Results

```bash
# Extract key fields from query response
curl -s "https://gis.ohiodnr.gov/arcgis/rest/services/OGS/OilGasWells/MapServer/0/query" \
  --data-urlencode "where=FORMATION LIKE '%UTICA%'" \
  --data-urlencode "outFields=PERM_NUM,WELL_NAME,OPERATOR,COUNTY_CODE,STATUS" \
  --data-urlencode "resultRecordCount=50" \
  --data-urlencode "f=json" \
  | python3 -c "
import json, sys
data = json.load(sys.stdin)
features = data.get('features', [])
print(f'Total records: {len(features)}')
print(f'{'Permit':<12} {'Operator':<25} {'Formation':<20} {'Status':<15}')
print('-' * 75)
for f in features[:20]:
    a = f['attributes']
    print(f\"{a.get('PERM_NUM',''):<12} {str(a.get('OPERATOR',''))[:24]:<25} {str(a.get('FORMATION',''))[:19]:<20} {str(a.get('STATUS',''))[:14]:<15}\")
"
```

### Step 5 — Bulk Download (Production Data)

ODNR publishes bulk CSV downloads for production and permit data:

```bash
# Current bulk download page (verify current URLs at ohiodnr.gov)
# Unconventional well list (Utica/Point Pleasant):
curl -L "https://ohiodnr.gov/static/documents/oil-gas/Well-Permit-Data-Unconventional.xlsx" \
  -o odnr_unconventional_wells.xlsx

# Production data (annual):
curl -L "https://ohiodnr.gov/static/documents/oil-gas/Annual-Production-Data.xlsx" \
  -o odnr_production.xlsx
```

---

## Key Ohio Formation Reference

| Formation | Type | Depth (ft TVD) | Target Area | Notes |
|-----------|------|---------------|------------|-------|
| Utica Shale | Unconventional gas/oil | 6,000–12,000 | E/SE Ohio | Overlies Point Pleasant |
| Point Pleasant | Unconventional gas/condensate | 6,500–12,500 | SE Ohio | Primary Appalachian Utica target |
| Clinton Sandstone | Conventional gas/oil | 1,500–5,000 | C/E Ohio | Prolific historical producer |
| Knox Dolomite | Conventional oil | 2,000–6,000 | C/N Ohio | Major conventional play |
| Medina (Berea) | Conventional gas | 1,000–4,000 | NE Ohio | Shallow gas |
| Oriskany Sandstone | Conventional gas | 3,000–6,000 | SE Ohio | Appalachian analog to WV |
| Trenton-Black River | Conventional (deep) | 5,000–7,000 | NW Ohio | Carbonate |

---

## Ohio County Reference (Key Utica/PP Counties)

| County | FIPS | Notes |
|--------|------|-------|
| Carroll | 019 | Highest Utica density; Carroll County core |
| Columbiana | 029 | Active Utica development |
| Guernsey | 059 | Utica and Clinton |
| Harrison | 067 | Major Utica/PP production |
| Holmes | 075 | Utica fringe area |
| Jefferson | 081 | Utica development |
| Mahoning | 099 | Utica fringe |
| Medina | 103 | Conventional + some Utica |
| Noble | 121 | Utica and Devonian |
| Tuscarawas | 157 | Utica transition |
| Wayne | 169 | Conventional |

---

## Appalachian Basin Comparison

| Parameter | Marcellus WV | Utica/PP OH | Utica WV/PA |
|-----------|-------------|------------|------------|
| Depth (ft TVD) | 5,000–9,000 | 6,500–12,500 | 8,000–14,000 |
| Lateral length (ft) | 6,000–12,000 | 6,000–11,000 | 6,000–10,000 |
| Gas API | 0.58–0.68 | 0.60–0.72 | 0.60–0.70 |
| GOR (scf/bbl) | Dry–10,000 | 2,000–wet | Dry–8,000 |
| Data source | WVGES + pnge-state-regulatory:wvges-wells | ODNR + pnge-state-regulatory:odnr-wells | PADEP + pnge-state-regulatory:padep-wells |

---

## ODNR Supplemental Resources

| Resource | URL Pattern | Notes |
|----------|-------------|-------|
| Well viewer (web app) | ohiodnr.gov/discover-and-learn/safety-conservation/about-ODNR/oil-gas | Interactive map |
| Permit data portal | ohiodnr.gov (Oil and Gas → Permits) | Searchable online |
| Production reports | ohiodnr.gov → Annual Reports | PDF summary tables |
| Spud reports | ODNR quarterly | New horizontal wells spudded |

---

## Output Format

```
## Ohio Well Query Results
**Query:** [formation / county / operator filter]
**Records returned:** N

| Permit # | Well Name | Operator | Formation | County | Type | Status |
|---------|----------|----------|-----------|--------|------|--------|
| | | | | | | |

**Summary:**
- Total wells returned: N
- Top operators: [list top 3–5]
- Formation breakdown: Utica: N, Point Pleasant: N, Clinton: N, Other: N
- Status breakdown: Producing: N, Plugged: N, Permit: N

**Data source:** ODNR Division of Oil and Gas Resources Management
**Certainty:** HIGH (official regulatory database) | **Bias:** Only permitted/reported wells
```

---

## Error Handling

| HTTP Code | Cause | Action |
|-----------|-------|--------|
| 400 Bad Request | Invalid WHERE syntax | Use UPPERCASE field names; check field list |
| 404 Not Found | Layer ID changed | Re-query MapServer root for current layer list |
| 500 Server Error | ODNR service unavailable | Try bulk download instead |
| Empty features [] | No records match filter | Broaden query; check formation name spelling |

---

## Caveats

- ODNR well database includes permitted but not-yet-drilled wells; filter by
  STATUS for producing wells when estimating active inventory.
- Formation names in ODNR data use various spellings — use LIKE with wildcards
  (e.g., `%UTICA%`, `%POINT PLEASANT%`, `%CLINTON%`).
- Production data for Utica/Point Pleasant wells may be reported under operator
  rather than individual wellbore; verify against permit number.
- Horizontal well counts are best obtained from the unconventional well bulk
  download, which is more consistently maintained than the ArcGIS service.
- For cross-basin comparison with WV and PA, use `pnge-state-regulatory:wvges-wells` and
  `pnge-state-regulatory:padep-wells` alongside this skill.
