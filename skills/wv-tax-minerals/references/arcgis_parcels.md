# WV Parcels ArcGIS MapServer — ParcelSummary (Table 11)

## Service Endpoint

```
https://services.wvgis.wvu.edu/arcgis/rest/services/Planning_Cadastre/WV_Parcels/MapServer
```

**Web viewer:** https://mapwv.gov/parcel/

**Table 11 (ParcelSummary):** Non-spatial table containing tax assessment data
for all parcels statewide. This is the primary table for mineral property
identification and valuation.

```
https://services.wvgis.wvu.edu/arcgis/rest/services/Planning_Cadastre/WV_Parcels/MapServer/11
```

**Layer 0 (Parcels):** Polygon geometry for mapped parcels. Spatial joins are
possible but mineral parcels often lack mapped boundaries (they overlay surface
parcels).

```
https://services.wvgis.wvu.edu/arcgis/rest/services/Planning_Cadastre/WV_Parcels/MapServer/0
```

**Max records per request:** 2,000

**Authentication:** None required (public service)

---

## ParcelSummary (Table 11) Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| OBJECTID | Integer | Internal ID | 12345 |
| CleanParcelID | String | Standardized parcel identifier (join key) | "05-0001-0001-0000-0000" |
| CountyName | String | County name | "Marshall" |
| District | String | Tax district | "01" |
| Map | String | Tax map number | "0001" |
| Parcel | String | Parcel number | "0001" |
| SubParcel | String | Sub-parcel number | "0000" |
| FullOwnerName | String | Owner name(s) | "SMITH JOHN A & MARY B" |
| FullMailingAddress | String | Mailing address | "123 MAIN ST MOUNDSVILLE WV 26041" |
| FullLegalDescription | String | Legal description (key for mineral ID) | "PT OF 50 AC MINERAL RIGHTS ONLY" |
| TaxClass | String | Tax classification | "II", "III", "IV" |
| PropertyClassCode | String | Property class | "R" (Real Estate), "P" (Personal) |
| LandUseCode | String | Land use category | "100", "200", "500", "800" |
| TotalAppraisal | Double | Total assessed value ($) | 15000.00 |
| TotalLandAppraisal | Double | Land portion of appraisal ($) | 15000.00 |
| TotalBuildingAppraisal | Double | Building portion ($) | 0.00 |
| DeededAcres | Double | Deeded acreage | 50.0 |
| DeedBook | String | Deed book number | "234" |
| DeedPage | String | Deed page number | "567" |

---

## Mineral Property Identification

West Virginia's severed mineral estate means mineral rights are assessed as
separate parcels from surface rights. However, there is no dedicated
`PropertyType` field for "mineral." Instead, mineral parcels are identified
by text patterns in `FullLegalDescription`.

### Primary Keyword Patterns

| Pattern | SQL WHERE | Matches | Notes |
|---------|-----------|---------|-------|
| MINERAL | `FullLegalDescription LIKE '%MINERAL%'` | Broad match | Catches "MINERAL RIGHTS", "MINERAL ONLY", etc. |
| OIL%GAS | `FullLegalDescription LIKE '%OIL%GAS%'` | Oil and gas rights | "OIL AND GAS", "OIL & GAS RIGHTS" |
| OG | `FullLegalDescription LIKE '% OG %'` | Abbreviation | Common shorthand; use word boundaries |
| SUR MIN | `FullLegalDescription LIKE '%SUR MIN%'` | Surface + mineral split | Indicates severed estate |
| COAL | `FullLegalDescription LIKE '%COAL%'` | Coal rights | Often separate from oil/gas minerals |
| ROYALTY | `FullLegalDescription LIKE '%ROYALTY%'` | Royalty interests | Fractional mineral interests |
| LEASE | `FullLegalDescription LIKE '%LEASE%'` | Leasehold interests | Oil and gas leases |

### Combined Mineral Search Query

```sql
FullLegalDescription LIKE '%MINERAL%'
OR FullLegalDescription LIKE '%OIL%GAS%'
OR FullLegalDescription LIKE '%SUR MIN%'
OR FullLegalDescription LIKE '%COAL%'
```

**Statewide hit rate:** The `MINERAL` keyword alone matches approximately 87
delinquent parcels when cross-referenced with the Delinquent_Properties layer.
Adding the additional keywords increases coverage but may also increase false
positives.

### False Positive Risks

- "MINERAL SPRINGS" — geographic name, not mineral rights
- "COAL RIVER" — geographic reference
- "OG" in owner names or addresses

### False Negative Risks

- Many mineral parcels have sparse legal descriptions (e.g., "PT OF 100 AC")
  with no mineral keyword at all
- Some use non-standard abbreviations
- PropertyClassCode is not reliable — most mineral parcels are coded "R" (Real
  Estate), same as surface parcels

---

## Key Enumerated Values

### TaxClass

WV uses a 4-class property tax system. Mineral properties typically fall under
Class II, III, or IV depending on the owner's relationship to the property.

| Class | Description | Tax Rate Multiplier |
|-------|-------------|-------------------|
| I | Owner-occupied residential, farm | 60% of appraised value |
| II | Non-owner-occupied residential | 60% of appraised value |
| III | Business/industrial, non-owner mineral | 60% of appraised value |
| IV | Personal property | 60% of appraised value |

Most severed mineral parcels are **Class III** (owner does not live on the
property and it is not agricultural).

### PropertyClassCode

| Code | Description |
|------|-------------|
| R | Real Estate (surface and mineral) |
| P | Personal Property |

**Note:** "R" is used for both surface and mineral parcels. This field alone
cannot distinguish mineral from surface properties.

### LandUseCode (Relevant Codes)

| Code | Description | Mineral Relevance |
|------|-------------|------------------|
| 100 | Residential | Low — but mineral rights under residential land exist |
| 200 | Commercial | Low |
| 300 | Industrial | Medium — may include mineral extraction |
| 400 | Agricultural | Medium — large tracts may have severed minerals |
| 500 | Exempt | Low |
| 600 | Mineral Rights | **High** — dedicated mineral code (rarely used) |
| 700 | Public Utility | Low |
| 800 | Vacant/Undeveloped | Medium — mineral-only parcels may be coded here |

**LandUseCode 600 is rare.** Most mineral parcels are coded 100, 400, or 800.
Do not rely on this field alone for mineral identification.

---

## Query Examples

### Count mineral parcels in a county

```bash
curl -s "https://services.wvgis.wvu.edu/arcgis/rest/services/Planning_Cadastre/WV_Parcels/MapServer/11/query" \
  --data-urlencode "where=CountyName='Tyler' AND FullLegalDescription LIKE '%MINERAL%'" \
  --data-urlencode "returnCountOnly=true" \
  --data-urlencode "f=json"
```

### Fetch mineral parcels with details

```bash
curl -s "https://services.wvgis.wvu.edu/arcgis/rest/services/Planning_Cadastre/WV_Parcels/MapServer/11/query" \
  --data-urlencode "where=CountyName='Tyler' AND FullLegalDescription LIKE '%MINERAL%'" \
  --data-urlencode "outFields=CleanParcelID,CountyName,FullOwnerName,FullLegalDescription,TaxClass,TotalAppraisal,DeededAcres,DeedBook,DeedPage" \
  --data-urlencode "resultRecordCount=50" \
  --data-urlencode "f=json"
```

### Batch lookup by CleanParcelID (for join from Delinquent data)

```bash
curl -s "https://services.wvgis.wvu.edu/arcgis/rest/services/Planning_Cadastre/WV_Parcels/MapServer/11/query" \
  --data-urlencode "where=CleanParcelID IN ('95-0001-0001-0000-0000','95-0001-0002-0000-0000')" \
  --data-urlencode "outFields=CleanParcelID,FullOwnerName,FullLegalDescription,TaxClass,TotalAppraisal,DeededAcres" \
  --data-urlencode "f=json"
```

---

## Pagination

Max records per request: **2,000**. Use `resultOffset` for pagination:

```bash
curl -s "https://services.wvgis.wvu.edu/arcgis/rest/services/Planning_Cadastre/WV_Parcels/MapServer/11/query" \
  --data-urlencode "where=CountyName='Marshall'" \
  --data-urlencode "outFields=CleanParcelID,FullOwnerName,TotalAppraisal" \
  --data-urlencode "resultRecordCount=2000" \
  --data-urlencode "resultOffset=0" \
  --data-urlencode "f=json"
```

Check `exceededTransferLimit` in the response. If `true`, increment
`resultOffset` by 2000 and fetch the next page.

---

## Data Quality Notes

1. **$0 appraisals are common** for mineral parcels. Many severed mineral
   interests have `TotalAppraisal=0` because the county assessor has not
   separately valued the mineral estate. This does not mean the minerals
   are worthless.

2. **Legal descriptions vary wildly** in format, detail, and accuracy.
   Some are brief ("100 AC") while others are multi-line metes and bounds.
   Text parsing is inherently imprecise.

3. **CleanParcelID format** is county-specific. The prefix is typically the
   2-digit county code within the state system (not the FIPS code). Example:
   Tyler County uses "95" prefix (FIPS 095 = state code 95).

4. **Acreage inconsistencies.** `DeededAcres` may not match the legal
   description. For mineral parcels, the acreage may represent the surface
   tract from which minerals were severed, not the actual mineral interest.

5. **Owner names** may be outdated. Property transfers may not be reflected
   until the next tax assessment cycle.
