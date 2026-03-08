# PA DEP Parcels ArcGIS MapServer

## Service Endpoint

```
https://gis.dep.pa.gov/depgisprd/rest/services/Parcels/PA_Parcels/MapServer
```

**Layer 0 (PA Parcels):** Point geometry with full owner and property data.
4,685,585 records statewide.

```
https://gis.dep.pa.gov/depgisprd/rest/services/Parcels/PA_Parcels/MapServer/0
```

**Max records per request:** 1,000

**Authentication:** None required (public service)

---

## Alternative: PASDA Statewide Parcels (Geometry-Only)

```
https://apps.pasda.psu.edu/arcgis/rest/services/PA_Parcels/MapServer
```

**Layer 1 (Parcels):** Polygon geometry for mapped parcels. 4,397,928 records.
Fields are limited to PIN, Source, and Date — useful for spatial queries only.

```
https://apps.pasda.psu.edu/arcgis/rest/services/PA_Parcels/MapServer/1
```

**Max records per request:** 1,000

**Authentication:** None required

**Use case:** When you need polygon boundaries for spatial intersection with
well locations. The PA DEP Parcels service (Layer 0) has points only but
richer attributes. Use PASDA when you need geometry-based spatial joins.

---

## PA DEP Parcels (Layer 0) Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| OBJECTID | Integer | Internal ID | 12345 |
| PARCEL_ID | String | Parcel identifier | "30-9-89" |
| OWNER_LAST_NAME | String | Owner last name | "SMITH" |
| OWNER_FIRST_NAME | String | Owner first name | "JOHN A" |
| OWNER_NAME | String | Full owner name | "SMITH JOHN A" |
| PROPERTY_ADDRESS_1 | String | Property address line 1 | "123 MAIN ST" |
| PROPERTY_ADDRESS_2 | String | Property address line 2 | "" |
| CITY | String | City | "WAYNESBURG" |
| STATE | String | State | "PA" |
| ZIP | String | ZIP code | "15370" |
| COUNTY_NAME | String | County name | "Greene" |
| COUNTY_CODE | String | 2-digit county code | "30" |
| DISTRICT | String | Tax district/municipality | "CENTER TWP" |
| ACREAGE | Double | Acreage (calculated) | 50.0 |
| ACCOUNT | String | Account number | "30-9-89" |
| ACRES | Double | Acreage (reported) | 50.0 |

**Note:** This service does NOT have a `FullLegalDescription` field like WV.
Mineral identification must rely on owner name patterns, county assessment
cross-reference, or spatial correlation with wells.

---

## Mineral Property Identification in PA

Unlike WV, PA's DEP Parcels service lacks legal description fields that would
directly indicate mineral ownership. PA mineral parcels must be identified
through a combination of approaches.

### Approach 1: Owner Name Pattern Matching

Certain owner name patterns suggest mineral rights holders, mineral trusts,
or oil and gas companies:

| Pattern | SQL WHERE | Matches |
|---------|-----------|---------|
| Energy companies | `OWNER_NAME LIKE '%ENERGY%'` | "EQT ENERGY", "RANGE ENERGY" |
| Gas companies | `OWNER_NAME LIKE '%GAS%'` | "CNX GAS COMPANY" |
| Oil companies | `OWNER_NAME LIKE '%OIL%'` | "CABOT OIL & GAS" |
| Resources | `OWNER_NAME LIKE '%RESOURCES%'` | "SENECA RESOURCES" |
| Mineral trusts | `OWNER_NAME LIKE '%MINERAL%'` | "MINERAL RIGHTS TRUST" |
| Heirs/Estate | `OWNER_NAME LIKE '%HEIRS%'` | "SMITH HEIRS" — possible fractional mineral |
| Et Al | `OWNER_NAME LIKE '%ET AL%'` | Multiple owners, common in severed estates |

**False positive risk:** High. Not all parcels owned by energy companies are
mineral-only parcels. Cross-reference with county assessment data for
confirmation.

### Approach 2: Spatial Correlation with Wells

Parcels spatially overlapping or near active unconventional well pads are
more likely to involve mineral interests. Query parcels within a buffer of
active wells and then investigate ownership.

### Approach 3: County Assessment Cross-Reference

The most reliable method. County assessment records (via CAMADataSite or county
portals) contain property classification codes that distinguish surface, mineral,
and combined estates. However, these require per-county web lookups and are not
available through a single statewide API.

---

## PA's Third Strata Doctrine

Pennsylvania recognizes three distinct property strata under the Dunham Rule
(Dunham & Shortt v. Kirkpatrick, 1882) and subsequent case law:

1. **Surface rights** — ownership of the land surface
2. **Coal rights** — ownership of coal seams (historically severed in PA)
3. **Oil and gas rights** — ownership of petroleum and natural gas

Each stratum can be separately owned, assessed, and taxed. A single surface
parcel may have three different owners for surface, coal, and oil/gas.

**Implications for this skill:**
- A parcel in PA DEP Parcels may represent surface-only, mineral-only, or
  combined ownership
- The `OWNER_NAME` field may show the surface owner, not the mineral owner
- County assessment records are needed to determine which strata an owner holds
- Mineral estates can become tax-delinquent independently of the surface estate

---

## Query Examples

### Count parcels in a county

```bash
curl -s "https://gis.dep.pa.gov/depgisprd/rest/services/Parcels/PA_Parcels/MapServer/0/query" \
  --data-urlencode "where=COUNTY_NAME='Greene'" \
  --data-urlencode "returnCountOnly=true" \
  --data-urlencode "f=json"
```

### Fetch parcels with owner details

```bash
curl -s "https://gis.dep.pa.gov/depgisprd/rest/services/Parcels/PA_Parcels/MapServer/0/query" \
  --data-urlencode "where=COUNTY_NAME='Greene'" \
  --data-urlencode "outFields=PARCEL_ID,OWNER_NAME,PROPERTY_ADDRESS_1,CITY,DISTRICT,ACREAGE,COUNTY_NAME" \
  --data-urlencode "returnGeometry=false" \
  --data-urlencode "resultRecordCount=50" \
  --data-urlencode "f=json"
```

### Search by owner name pattern (energy companies)

```bash
curl -s "https://gis.dep.pa.gov/depgisprd/rest/services/Parcels/PA_Parcels/MapServer/0/query" \
  --data-urlencode "where=COUNTY_NAME='Washington' AND OWNER_NAME LIKE '%EQT%'" \
  --data-urlencode "outFields=PARCEL_ID,OWNER_NAME,DISTRICT,ACREAGE" \
  --data-urlencode "returnGeometry=true" \
  --data-urlencode "outSR=4326" \
  --data-urlencode "resultRecordCount=100" \
  --data-urlencode "f=json"
```

### Spatial query — parcels within bounding box

```bash
curl -s "https://gis.dep.pa.gov/depgisprd/rest/services/Parcels/PA_Parcels/MapServer/0/query" \
  --data-urlencode "geometry=-80.3,39.8,-80.0,40.0" \
  --data-urlencode "geometryType=esriGeometryEnvelope" \
  --data-urlencode "inSR=4326" \
  --data-urlencode "spatialRel=esriSpatialRelIntersects" \
  --data-urlencode "outFields=PARCEL_ID,OWNER_NAME,COUNTY_NAME,DISTRICT,ACREAGE" \
  --data-urlencode "returnGeometry=true" \
  --data-urlencode "outSR=4326" \
  --data-urlencode "resultRecordCount=100" \
  --data-urlencode "f=json"
```

### Aggregate parcels by county

```bash
curl -s "https://gis.dep.pa.gov/depgisprd/rest/services/Parcels/PA_Parcels/MapServer/0/query" \
  --data-urlencode "where=1=1" \
  --data-urlencode "groupByFieldsForStatistics=COUNTY_NAME" \
  --data-urlencode 'outStatistics=[{"statisticType":"count","onStatisticField":"OBJECTID","outStatisticFieldName":"cnt"}]' \
  --data-urlencode "orderByFields=cnt DESC" \
  --data-urlencode "f=json"
```

### Spatial query — parcels near a point (1-mile buffer)

```bash
curl -s "https://gis.dep.pa.gov/depgisprd/rest/services/Parcels/PA_Parcels/MapServer/0/query" \
  --data-urlencode "geometry=-80.18,39.90" \
  --data-urlencode "geometryType=esriGeometryPoint" \
  --data-urlencode "inSR=4326" \
  --data-urlencode "spatialRel=esriSpatialRelIntersects" \
  --data-urlencode "distance=1609.34" \
  --data-urlencode "units=esriSRUnit_Meter" \
  --data-urlencode "outFields=PARCEL_ID,OWNER_NAME,ACREAGE,COUNTY_NAME,DISTRICT" \
  --data-urlencode "returnGeometry=true" \
  --data-urlencode "outSR=4326" \
  --data-urlencode "resultRecordCount=200" \
  --data-urlencode "f=json"
```

---

## Pagination

Max records per request: **1,000**. Use `resultOffset` for pagination:

```bash
# Page 1
curl -s "https://gis.dep.pa.gov/depgisprd/rest/services/Parcels/PA_Parcels/MapServer/0/query" \
  --data-urlencode "where=COUNTY_NAME='Greene'" \
  --data-urlencode "outFields=PARCEL_ID,OWNER_NAME,ACREAGE" \
  --data-urlencode "resultRecordCount=1000" \
  --data-urlencode "resultOffset=0" \
  --data-urlencode "f=json"

# Page 2
curl -s "https://gis.dep.pa.gov/depgisprd/rest/services/Parcels/PA_Parcels/MapServer/0/query" \
  --data-urlencode "where=COUNTY_NAME='Greene'" \
  --data-urlencode "outFields=PARCEL_ID,OWNER_NAME,ACREAGE" \
  --data-urlencode "resultRecordCount=1000" \
  --data-urlencode "resultOffset=1000" \
  --data-urlencode "f=json"
```

Check `exceededTransferLimit` in the response. If `true`, increment
`resultOffset` by 1000 and fetch the next page.

---

## Data Quality Notes

1. **No legal description field.** Unlike WV's ParcelSummary, PA DEP Parcels
   does not include `FullLegalDescription`. Mineral identification requires
   external data (county assessment records).

2. **Owner name may be surface owner.** For severed estates, the DEP Parcels
   service may only list the surface owner. The mineral owner may be a
   different entity entirely.

3. **Point geometry only.** Layer 0 provides parcel centroid points. For
   polygon boundaries, use the PASDA service (limited attributes).

4. **4.6 million records.** Statewide queries without county filters will
   return massive result sets. Always filter by `COUNTY_NAME` or spatial
   extent.

5. **ACREAGE vs ACRES.** Both fields exist and may contain different values.
   `ACREAGE` is typically the calculated value; `ACRES` is the reported value.

6. **COUNTY_CODE is not FIPS.** PA uses its own 2-digit county numbering
   system. See `county_codes.md` for the mapping.
