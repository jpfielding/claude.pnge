# OGRIP Statewide Parcel Data — Schema and Query Reference

## Primary Endpoint

```
https://services2.arcgis.com/MlJ0G8iWUyC7jAmu/arcgis/rest/services/OhioStatewidePacels_full_view/FeatureServer/0
```

**Note:** The URL contains a typo — "Pacels" (not "Parcels"). This is the
actual production URL. Do not "correct" it.

- **Records:** 6,313,611 total parcels statewide
- **Max per request:** 2,000 records
- **Native SRS:** EPSG:3735 (Ohio State Plane South, US feet)
- **Auth:** None required (public endpoint)
- **Server type:** ArcGIS FeatureServer (supports advanced queries)

### CAMA Related Table (Table 1)

```
https://services2.arcgis.com/MlJ0G8iWUyC7jAmu/arcgis/rest/services/OhioStatewidePacels_full_view/FeatureServer/1
```

Contains property assessment data linked via `GlobalID`. Not all parcels have
CAMA records.

---

## Alternate Endpoint: OIT Statewide Parcels 2022

```
https://maps.ohio.gov/arcgis/rest/services/Statewide_Parcels_2022/MapServer/0
```

- **Max per request:** 2,000 records
- **Key advantage:** Has `OWNER1` and `OWNER2` fields (not in OGRIP)
- **Key fields:** PIN, COUNTY, STATEWIDE_PIN, ASSR_ACRES, CALC_ACRES, OWNER1, OWNER2, AUD_LINK
- **Limitation:** 2022 vintage, may lag current OGRIP data

---

## OGRIP Parcel Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| StateParcelID | String | Statewide unique ID | "0100100001" |
| LocalParcelID | String | County-assigned parcel number | "01-0010-0001.000" |
| County | String | County name (uppercase) | "BELMONT" |
| StateLUC | String | State Land Use Code | "240" |
| SitusAddressAll | String | Property street address | "123 MAIN ST" |
| MailAddressAll | String | Full mailing address | "PO BOX 456 WHEELING WV" |
| MailNumber | String | Mail address house number | "456" |
| MailStreetName | String | Mail address street | "MAIN ST" |
| MailCity | String | Mail address city | "WHEELING" |
| MailZip | String | Mail address ZIP | "26003" |
| MailState | String | Mail address state | "WV" |
| LandArea | Double | Land area (square feet) | 1568160.0 |
| CAMADataSite | String | URL to county auditor CAMA data | "https://..." |
| GlobalID | String | UUID for CAMA table join | "{ABC12345-...}" |
| OBJECTID | Integer | Internal row ID | 12345 |

### Fields Available in OIT 2022 (Not in OGRIP)

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| OWNER1 | String | Primary owner name | "SMITH JOHN A" |
| OWNER2 | String | Secondary owner | "& SMITH MARY B" |
| ASSR_ACRES | Double | Assessed acreage | 36.0 |
| CALC_ACRES | Double | Calculated acreage | 35.8 |
| AUD_LINK | String | County auditor website link | "https://..." |
| PIN | String | Parcel identification number | "01-0010-0001.000" |

---

## Mineral-Coded Parcels (200-Series StateLUC)

Ohio's OGRIP dataset uses explicit 200-series land use codes for mineral
parcels. This is a **major advantage** over WV and PA, where mineral parcels
must be identified by parsing legal descriptions.

### Mineral Query Pattern

```sql
-- All mineral parcels
StateLUC LIKE '2%'

-- Specific mineral types
StateLUC IN ('200','210','220','230','240','250','260','261','270')

-- Oil and gas mineral interests only
StateLUC IN ('240','250')

-- Coal interests only
StateLUC IN ('210','220','230')
```

### Mineral Parcel Statistics

| StateLUC | Description | Approx Count |
|----------|-------------|-------------|
| 200 | Min-Custom Code | ~50 |
| 210 | Min-Coal Land (surface and rights) | ~800 |
| 220 | Min-Coal Rights-Working Interest | ~600 |
| 230 | Min-Coal Rights-Separate Royalty Interest | ~200 |
| 240 | Min-Oil and Gas-Working Interest | ~900 |
| 250 | Min-Oil and Gas-Separate Royalty Interest | ~400 |
| 260 | Min-Other Minerals | ~250 |
| 261 | Min-Custom Code | ~60 |
| 270 | Min-Custom Code | ~100 |
| **Total** | **All mineral-coded parcels** | **~3,360** |

### Working curl Examples

**Count all mineral parcels statewide:**
```bash
curl -s "https://services2.arcgis.com/MlJ0G8iWUyC7jAmu/arcgis/rest/services/OhioStatewidePacels_full_view/FeatureServer/0/query" \
  --data-urlencode "where=StateLUC LIKE '2%'" \
  --data-urlencode "returnCountOnly=true" \
  --data-urlencode "f=json"
```

**Query mineral parcels in Belmont County:**
```bash
curl -s "https://services2.arcgis.com/MlJ0G8iWUyC7jAmu/arcgis/rest/services/OhioStatewidePacels_full_view/FeatureServer/0/query" \
  --data-urlencode "where=County='BELMONT' AND StateLUC LIKE '2%'" \
  --data-urlencode "outFields=StateParcelID,LocalParcelID,County,StateLUC,MailAddressAll,LandArea,CAMADataSite" \
  --data-urlencode "returnGeometry=true" \
  --data-urlencode "outSR=4326" \
  --data-urlencode "resultRecordCount=50" \
  --data-urlencode "f=json"
```

**Oil and gas mineral parcels only:**
```bash
curl -s "https://services2.arcgis.com/MlJ0G8iWUyC7jAmu/arcgis/rest/services/OhioStatewidePacels_full_view/FeatureServer/0/query" \
  --data-urlencode "where=County='HARRISON' AND StateLUC IN ('240','250')" \
  --data-urlencode "outFields=StateParcelID,LocalParcelID,StateLUC,MailAddressAll,LandArea" \
  --data-urlencode "returnGeometry=true" \
  --data-urlencode "outSR=4326" \
  --data-urlencode "resultRecordCount=100" \
  --data-urlencode "f=json"
```

**Aggregate mineral parcels by county:**
```bash
curl -s "https://services2.arcgis.com/MlJ0G8iWUyC7jAmu/arcgis/rest/services/OhioStatewidePacels_full_view/FeatureServer/0/query" \
  --data-urlencode "where=StateLUC LIKE '2%'" \
  --data-urlencode "groupByFieldsForStatistics=County" \
  --data-urlencode 'outStatistics=[{"statisticType":"count","onStatisticField":"OBJECTID","outStatisticFieldName":"cnt"}]' \
  --data-urlencode "orderByFields=cnt DESC" \
  --data-urlencode "f=json"
```

**Aggregate mineral parcels by land use code:**
```bash
curl -s "https://services2.arcgis.com/MlJ0G8iWUyC7jAmu/arcgis/rest/services/OhioStatewidePacels_full_view/FeatureServer/0/query" \
  --data-urlencode "where=StateLUC LIKE '2%'" \
  --data-urlencode "groupByFieldsForStatistics=StateLUC" \
  --data-urlencode 'outStatistics=[{"statisticType":"count","onStatisticField":"OBJECTID","outStatisticFieldName":"cnt"}]' \
  --data-urlencode "orderByFields=cnt DESC" \
  --data-urlencode "f=json"
```

---

## Coordinate System Notes

The OGRIP dataset is natively stored in **EPSG:3735** (Ohio State Plane
South, NAD83, US feet). This is a projected coordinate system specific to
Ohio.

**Always include `outSR=4326`** in queries where you need WGS84 latitude/
longitude output for spatial correlation with ODNR wells or any other
WGS84-based dataset.

Without `outSR=4326`, geometry values will be returned in Ohio State Plane
coordinates (very large numbers in US feet), not degrees.

Example of native EPSG:3735 coordinates (not useful without transformation):
```json
{"x": 2243145.67, "y": 567890.12}
```

Same point with `outSR=4326`:
```json
{"x": -80.85, "y": 39.95}
```

---

## CAMA Data and County Auditor Links

The `CAMADataSite` field contains URLs to county auditor websites where
detailed property assessment data (Computer-Assisted Mass Appraisal) is
available. This is the best source for:

- Appraised/assessed values
- Tax payment status and delinquency
- Owner name and mailing address
- Sale history and transfer records
- Building/improvement details

Not all counties participate in OGRIP or provide CAMA links. Coverage varies.

The `AUD_LINK` field in the OIT 2022 dataset serves a similar purpose.

---

## Pagination

The server returns a maximum of 2,000 records per request. Use `resultOffset`
for pagination:

```python
offset = 0
all_records = []
while True:
    # Query with resultOffset=offset, resultRecordCount=2000
    features = response["features"]
    all_records.extend(features)
    if len(features) < 2000 or not response.get("exceededTransferLimit"):
        break
    offset += 2000
```

For the 8 target counties, mineral parcel counts are small enough (typically
under 600 per county) that pagination is rarely needed. For statewide mineral
queries (~3,360 total), two pages will suffice.
