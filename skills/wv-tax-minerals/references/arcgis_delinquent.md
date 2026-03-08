# WV Delinquent Properties ArcGIS MapServer

## Service Endpoint

```
https://services.wvgis.wvu.edu/arcgis/rest/services/Planning_Cadastre/Delinquent_Properties/MapServer
```

**Layer 0:** Point geometry (parcel centroids) — 32,749 records
**Layer 1:** Polygon geometry (parcel boundaries) — 32,749 records

Both layers contain the same attribute data. Layer 0 (points) is faster to
query and sufficient for spatial correlation with wells. Layer 1 provides
boundary geometry for mapping.

**Max records per request:** 2,000

**Authentication:** None required (public service)

---

## Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| OBJECTID | Integer | Internal ID | 5678 |
| CleanParcelID | String | Standardized parcel ID (join key to ParcelSummary) | "95-0012-0034-0000-0000" |
| county | String | County name | "Tyler" |
| status | String | Delinquent status | "No Bid", "Deed", "Redeemed" |
| certno | String | Certificate number | "2019-00123" |
| FullOwnerName | String | Owner name at time of delinquency | "SMITH JOHN A ETAL" |
| FullLegalDescription | String | Legal description | "36 AC MINERAL ONLY" |
| Acres_C | Double | Calculated acreage | 36.0 |
| SaleYear | String | Year of tax sale | "2019" |
| SaleDate | String | Date of tax sale | "2019/11/15" |
| RedemptionDate | String | Date redeemed (if applicable) | "2020/03/01" or null |
| DeedDate | String | Date state deed issued (if applicable) | "2021/06/15" or null |
| TotalAmtDue | Double | Total taxes owed ($) | 245.67 |

---

## Status Values and Lifecycle

The `status` field tracks where a delinquent property sits in the WV tax
sale lifecycle. Properties move through these stages:

```
Delinquent → Tax Sale → No Bid / Sold → Deed / Redeemed / Dismissed / Suspended
```

| Status | Count | Description | Actionability |
|--------|-------|-------------|---------------|
| No Bid | 10,452 | No buyer at sheriff's sale; held by state | **High** — available at next subsequent sale |
| Deed | 14,444 | State deed issued to Auditor/Land Dept | **High** — state owns; may be available for purchase |
| Redeemed | 6,898 | Owner paid back taxes; property returned | **Low** — no longer delinquent |
| Sold | 469 | Sold at sheriff's sale to third party | **Low** — already purchased |
| Dismissed | 346 | Delinquency dismissed (errors, exemptions) | **None** — not delinquent |
| Suspended | 131 | Sale or process suspended (legal disputes) | **Low** — in limbo |

### Actionable Statuses for Investment

**`No Bid`** — The most actionable status. These properties received no bids at
the sheriff's tax sale. They are held by the state and will be offered again at
subsequent sales, often at significantly reduced prices. Mineral-only parcels
frequently go "No Bid" because bidders don't recognize their value.

**`Deed`** — The state has taken deed to these properties. They may be available
through the WV State Auditor's Office surplus property program. Some require
quiet title actions before mineral rights can be exercised.

### Query for Actionable Properties

```sql
status IN ('No Bid', 'Deed')
```

---

## Join Key: CleanParcelID

The `CleanParcelID` field is the primary join key between Delinquent_Properties
and WV_Parcels ParcelSummary (Table 11). The format is:

```
CC-DDDD-PPPP-SSSS-TTTT
```

Where:
- `CC` = County code (2-digit state system, NOT FIPS)
- `DDDD` = District
- `PPPP` = Map/Parcel
- `SSSS` = Sub-parcel
- `TTTT` = Additional identifier

**Important:** The county code in CleanParcelID uses the WV state numbering
system, not the 3-digit FIPS code. Tyler County = "95" in CleanParcelID but
"095" in FIPS.

### Join Workflow

1. Query Delinquent_Properties for target county and status
2. Extract `CleanParcelID` values from results
3. Batch query ParcelSummary Table 11 using `CleanParcelID IN (...)`
4. Merge the two result sets client-side

**Batch size limit:** Keep `IN (...)` clauses to ~50 IDs per request to stay
within URL length limits. For larger sets, paginate the batch queries.

---

## Query Examples

### Count all delinquent properties in a county

```bash
curl -s "https://services.wvgis.wvu.edu/arcgis/rest/services/Planning_Cadastre/Delinquent_Properties/MapServer/0/query" \
  --data-urlencode "where=county='Tyler'" \
  --data-urlencode "returnCountOnly=true" \
  --data-urlencode "f=json"
```

### Actionable delinquent properties with mineral keywords

```bash
curl -s "https://services.wvgis.wvu.edu/arcgis/rest/services/Planning_Cadastre/Delinquent_Properties/MapServer/0/query" \
  --data-urlencode "where=county='Tyler' AND status IN ('No Bid','Deed') AND FullLegalDescription LIKE '%MINERAL%'" \
  --data-urlencode "outFields=CleanParcelID,county,status,FullOwnerName,FullLegalDescription,Acres_C,certno,TotalAmtDue" \
  --data-urlencode "resultRecordCount=100" \
  --data-urlencode "f=json"
```

### Statewide mineral delinquent count

```bash
curl -s "https://services.wvgis.wvu.edu/arcgis/rest/services/Planning_Cadastre/Delinquent_Properties/MapServer/0/query" \
  --data-urlencode "where=FullLegalDescription LIKE '%MINERAL%'" \
  --data-urlencode "returnCountOnly=true" \
  --data-urlencode "f=json"
```

### Aggregate delinquent properties by county and status

```bash
curl -s "https://services.wvgis.wvu.edu/arcgis/rest/services/Planning_Cadastre/Delinquent_Properties/MapServer/0/query" \
  --data-urlencode "where=1=1" \
  --data-urlencode "groupByFieldsForStatistics=county,status" \
  --data-urlencode 'outStatistics=[{"statisticType":"count","onStatisticField":"OBJECTID","outStatisticFieldName":"cnt"}]' \
  --data-urlencode "orderByFields=county,cnt DESC" \
  --data-urlencode "f=json"
```

### Spatial query — delinquent parcels within bounding box

```bash
curl -s "https://services.wvgis.wvu.edu/arcgis/rest/services/Planning_Cadastre/Delinquent_Properties/MapServer/0/query" \
  --data-urlencode "geometry=-80.9,39.3,-80.6,39.5" \
  --data-urlencode "geometryType=esriGeometryEnvelope" \
  --data-urlencode "inSR=4326" \
  --data-urlencode "spatialRel=esriSpatialRelIntersects" \
  --data-urlencode "where=FullLegalDescription LIKE '%MINERAL%'" \
  --data-urlencode "outFields=CleanParcelID,county,status,FullOwnerName,FullLegalDescription,Acres_C" \
  --data-urlencode "returnGeometry=true" \
  --data-urlencode "outSR=4326" \
  --data-urlencode "f=json"
```

---

## Spatial Reference

- **Native SRS:** Web Mercator (WKID 3857)
- **Input/Output:** Use `inSR=4326` and `outSR=4326` for WGS84 lat/lon
- **Centroid accuracy:** Layer 0 points are parcel centroids derived from
  boundary geometry. For mineral-only parcels, the centroid represents the
  surface tract from which minerals were severed, which may not exactly
  coincide with the subsurface mineral estate boundary.

---

## Data Quality Notes

1. **Not all delinquent properties are in this layer.** Some counties may have
   additional delinquent properties not yet geocoded into the GIS service.
   Cross-reference with county-level tax records for completeness.

2. **Status may lag reality.** A property shown as "No Bid" may have been
   redeemed or sold since the last data update. Verify with the county
   sheriff's office or WV State Auditor before taking action.

3. **TotalAmtDue may be stale.** Interest and penalties accrue. The actual
   amount due at time of redemption or sale may be higher than shown.

4. **Mineral identification is text-based.** The same limitations described
   in `arcgis_parcels.md` apply — not all mineral parcels contain "MINERAL"
   in their legal description.

5. **Duplicate parcels.** A single physical property may appear multiple times
   if delinquent in multiple tax years.

6. **32,749 total records** — this is the full statewide dataset as of the
   last service update. Records span multiple tax sale years.
