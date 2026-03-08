---
name: pa-tax-minerals
description: >
  Query Pennsylvania parcels near active Marcellus and Utica wells to identify
  potential mineral interest properties. Use this skill when the user asks about
  PA mineral rights, Pennsylvania tax sale minerals, severed mineral estate PA,
  Third Strata Doctrine, oil and gas mineral rights Pennsylvania, parcels near
  Marcellus wells PA, mineral interest parcels in Greene County, Washington
  County mineral properties, delinquent mineral parcels PA, PA property tax
  minerals, county assessment mineral parcels, mineral rights investment PA,
  Pennsylvania oil gas mineral ownership, finding mineral parcels near active
  unconventional wells in Pennsylvania, or SW PA Marcellus mineral screening.
  Covers 4.6M parcels and 223K wells. No statewide delinquent layer exists;
  uses parcel-well spatial correlation and owner name analysis instead.
---

# PA Mineral Interest Parcels Near Active Wells

Queries two public Pennsylvania DEP ArcGIS services to find parcels near active
Marcellus/Utica unconventional wells and identify potential mineral interest
indicators. Unlike West Virginia, Pennsylvania has no statewide delinquent
property GIS layer. Instead, this skill uses spatial correlation between
PA DEP Parcels (4.6M records with owner names and acreage) and PA DEP Oil/Gas
Wells (223K records) to identify parcels overlapping active well pads, then
flags potential mineral interest indicators through owner name patterns and
county assessment cross-reference guidance.

Pennsylvania's Third Strata Doctrine (surface, coal, oil/gas) means mineral
rights are often severed from surface ownership and assessed independently
at the county level. County Tax Claim Bureaus manage delinquent properties
via PDFs and county-specific systems — there is no unified statewide API.

## Credential

**None required.** Both PA DEP ArcGIS REST services are publicly accessible
with no API key or authentication.

---

## Data Sources

### A. PA DEP Parcels

```
https://gis.dep.pa.gov/depgisprd/rest/services/Parcels/PA_Parcels/MapServer/0
```

4,685,585 parcels statewide with owner names, addresses, acreage, and county
information. Point geometry. Max 1,000 records/request. Used to identify
parcels near well locations and analyze ownership patterns.

### B. PASDA Statewide Parcels (Geometry-Only)

```
https://apps.pasda.psu.edu/arcgis/rest/services/PA_Parcels/MapServer/1
```

4,397,928 parcels with polygon geometry but limited attributes (PIN, Source,
Date only). Max 1,000 records/request. Useful for spatial intersection queries
when polygon boundaries are needed.

### C. PA DEP Oil and Gas Wells

```
https://gis.dep.pa.gov/depgisprd/rest/services/OilGas/OilGasAllStrayGasEGSP/MapServer
```

- **Layer 1:** Unconventional wells (15,328) — Marcellus/Utica horizontal wells
- **Layer 2:** Conventional wells (173,452) — vertical conventional wells
- **Layer 3:** All wells (223,664) — **primary query layer**

Max 5,000 records/request. Used for spatial correlation: find active
unconventional wells, then query nearby parcels.

---

## API Structure

All three services use the standard ArcGIS REST query pattern:

```
POST {service_url}/{layerId}/query
```

**Common parameters:**

| Parameter | Required | Description | Example |
|-----------|----------|-------------|---------|
| where | Yes | SQL WHERE clause | `COUNTY_NAME='Greene'` |
| outFields | No | Comma-separated fields | `PARCEL_ID,OWNER_NAME` or `*` |
| f | Yes | Response format | `json` or `geoJSON` |
| resultRecordCount | No | Max records per request | `100` |
| resultOffset | No | Pagination offset | `1000` |
| returnGeometry | No | Include coordinates | `false` |
| returnCountOnly | No | Return count only | `true` |
| geometry | No | Spatial filter | `-80.3,39.8,-80.0,40.0` |
| geometryType | No | Geometry type | `esriGeometryEnvelope` |
| inSR | No | Input spatial reference | `4326` |
| outSR | No | Output spatial reference | `4326` |
| spatialRel | No | Spatial relationship | `esriSpatialRelIntersects` |
| distance | No | Buffer distance (meters) | `1609.34` (1 mile) |
| units | No | Distance units | `esriSRUnit_Meter` |

### Working curl Examples

**Count parcels in Greene County:**
```bash
curl -s "https://gis.dep.pa.gov/depgisprd/rest/services/Parcels/PA_Parcels/MapServer/0/query" \
  --data-urlencode "where=COUNTY_NAME='Greene'" \
  --data-urlencode "returnCountOnly=true" \
  --data-urlencode "f=json"
```

**Fetch parcels with owner details:**
```bash
curl -s "https://gis.dep.pa.gov/depgisprd/rest/services/Parcels/PA_Parcels/MapServer/0/query" \
  --data-urlencode "where=COUNTY_NAME='Greene'" \
  --data-urlencode "outFields=PARCEL_ID,OWNER_NAME,PROPERTY_ADDRESS_1,CITY,DISTRICT,ACREAGE,COUNTY_NAME" \
  --data-urlencode "returnGeometry=false" \
  --data-urlencode "resultRecordCount=50" \
  --data-urlencode "f=json"
```

**Search parcels by owner name pattern (energy company):**
```bash
curl -s "https://gis.dep.pa.gov/depgisprd/rest/services/Parcels/PA_Parcels/MapServer/0/query" \
  --data-urlencode "where=COUNTY_NAME='Washington' AND OWNER_NAME LIKE '%EQT%'" \
  --data-urlencode "outFields=PARCEL_ID,OWNER_NAME,DISTRICT,ACREAGE" \
  --data-urlencode "returnGeometry=true" \
  --data-urlencode "outSR=4326" \
  --data-urlencode "resultRecordCount=100" \
  --data-urlencode "f=json"
```

**Count active unconventional wells in Washington County:**
```bash
curl -s "https://gis.dep.pa.gov/depgisprd/rest/services/OilGas/OilGasAllStrayGasEGSP/MapServer/3/query" \
  --data-urlencode "where=COUNTY='Washington' AND UNCONVENTIONAL_IND='Yes' AND WELL_STATUS='Active'" \
  --data-urlencode "returnCountOnly=true" \
  --data-urlencode "f=json"
```

**Active unconventional wells with coordinates:**
```bash
curl -s "https://gis.dep.pa.gov/depgisprd/rest/services/OilGas/OilGasAllStrayGasEGSP/MapServer/3/query" \
  --data-urlencode "where=COUNTY='Greene' AND UNCONVENTIONAL_IND='Yes' AND WELL_STATUS='Active'" \
  --data-urlencode "outFields=PERMIT_NUMBER,WELL_NAME,OPERATOR,WELL_TYPE,WELL_STATUS,WELL_CONFIG_CODE,LATITUDE,LONGITUDE" \
  --data-urlencode "returnGeometry=false" \
  --data-urlencode "resultRecordCount=50" \
  --data-urlencode "f=json"
```

**Parcels within 1 mile of a point (near a well pad):**
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

**Wells within radius of a point:**
```bash
curl -s "https://gis.dep.pa.gov/depgisprd/rest/services/OilGas/OilGasAllStrayGasEGSP/MapServer/3/query" \
  --data-urlencode "geometry=-80.18,39.90" \
  --data-urlencode "geometryType=esriGeometryPoint" \
  --data-urlencode "inSR=4326" \
  --data-urlencode "spatialRel=esriSpatialRelIntersects" \
  --data-urlencode "distance=1609.34" \
  --data-urlencode "units=esriSRUnit_Meter" \
  --data-urlencode "where=WELL_STATUS='Active' AND UNCONVENTIONAL_IND='Yes'" \
  --data-urlencode "outFields=PERMIT_NUMBER,WELL_NAME,OPERATOR,COUNTY,WELL_CONFIG_CODE,UNCONVENTIONAL_IND" \
  --data-urlencode "returnGeometry=false" \
  --data-urlencode "resultRecordCount=50" \
  --data-urlencode "f=json"
```

**Aggregate wells by county (unconventional only):**
```bash
curl -s "https://gis.dep.pa.gov/depgisprd/rest/services/OilGas/OilGasAllStrayGasEGSP/MapServer/3/query" \
  --data-urlencode "where=UNCONVENTIONAL_IND='Yes'" \
  --data-urlencode "groupByFieldsForStatistics=COUNTY" \
  --data-urlencode 'outStatistics=[{"statisticType":"count","onStatisticField":"OBJECTID","outStatisticFieldName":"cnt"}]' \
  --data-urlencode "orderByFields=cnt DESC" \
  --data-urlencode "f=json"
```

---

## Key Fields

### PA DEP Parcels (Layer 0)

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| PARCEL_ID | String | Parcel identifier | "30-9-89" |
| OWNER_LAST_NAME | String | Owner last name | "SMITH" |
| OWNER_FIRST_NAME | String | Owner first name | "JOHN A" |
| OWNER_NAME | String | Full owner name | "SMITH JOHN A" |
| PROPERTY_ADDRESS_1 | String | Property address | "123 MAIN ST" |
| CITY | String | City | "WAYNESBURG" |
| STATE | String | State abbreviation | "PA" |
| ZIP | String | ZIP code | "15370" |
| COUNTY_NAME | String | County name (mixed case) | "Greene" |
| COUNTY_CODE | String | 2-digit PA county code | "30" |
| DISTRICT | String | Tax district/municipality | "CENTER TWP" |
| ACREAGE | Double | Calculated acreage | 50.0 |
| ACCOUNT | String | Tax account number | "30-9-89" |
| ACRES | Double | Reported acreage | 50.0 |

### PA DEP Wells (Layer 3)

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| PERMIT_NUMBER | String | PA DEP permit number | "125-28575" |
| WELL_NAME | String | Well name | "SMITH 1H" |
| OPERATOR | String | Current operator | "EQT PRODUCTION COMPANY" |
| WELL_TYPE | String | Well type | "Gas", "Oil" |
| WELL_STATUS | String | Current status | "Active", "Plugged" |
| PERMIT_DATE | Date | Permit date (epoch ms) | 1577836800000 |
| SPUD_DATE | Date | Spud date (epoch ms) | 1580515200000 |
| COUNTY | String | County name (mixed case) | "Washington" |
| MUNICIPALITY | String | Township | "AMWELL TWP" |
| LATITUDE | Double | WGS84 latitude | 40.0123 |
| LONGITUDE | Double | WGS84 longitude | -80.2456 |
| UNCONVENTIONAL_IND | String | Unconventional flag | "Yes", "No" |
| WELL_CONFIG_CODE | String | Configuration | "Horizontal", "Vertical" |
| COAL_IND | String | Coal presence flag | "Yes", "No" |

---

## Key Enumerated Values

### WELL_STATUS (Wells)

| Value | Description |
|-------|-------------|
| Active | Currently producing or operating |
| Inactive | Not producing, not plugged |
| Plugged | Permanently sealed |
| Abandoned | Abandoned, unknown plugging status |
| Regulatory Inactive Status | Inactive per DEP regulation |
| Not Drilled | Permitted but never spud |
| Drilling | Currently being drilled |
| Completed | Drilling complete, awaiting production |

### WELL_TYPE (Wells)

| Value | Description |
|-------|-------------|
| Gas | Natural gas well |
| Oil | Oil well |
| Gas and Oil | Dual-producing well |
| Dry Hole | Non-productive well |
| Injection | Injection/disposal well |
| Storage | Gas storage well |
| Observation | Monitoring well |

### UNCONVENTIONAL_IND (Wells)

| Value | Description |
|-------|-------------|
| Yes | Unconventional (horizontal Marcellus/Utica) |
| No | Conventional (vertical) |

### WELL_CONFIG_CODE (Wells)

| Value | Description |
|-------|-------------|
| Horizontal | Horizontal well bore |
| Vertical | Vertical well bore |
| Deviated | Deviated/directional well bore |

### Owner Name Patterns (Parcels — Mineral Indicators)

| Pattern | SQL LIKE | Indicates |
|---------|----------|-----------|
| ENERGY | `OWNER_NAME LIKE '%ENERGY%'` | E&P company |
| GAS | `OWNER_NAME LIKE '%GAS%'` | Gas company ownership |
| OIL | `OWNER_NAME LIKE '%OIL%'` | Oil company ownership |
| RESOURCES | `OWNER_NAME LIKE '%RESOURCES%'` | Resource company |
| MINERAL | `OWNER_NAME LIKE '%MINERAL%'` | Mineral trust/interest |
| HEIRS | `OWNER_NAME LIKE '%HEIRS%'` | Inherited estate (possible severed) |
| ET AL | `OWNER_NAME LIKE '%ET AL%'` | Multiple owners (common in mineral) |

---

## Target Counties

### SW PA Marcellus/Utica Play (Primary)

| FIPS | County | PA Code | Unconv Wells | Key Operators |
|------|--------|---------|-------------|---------------|
| 059 | Greene | 30 | ~1,800 | EQT, CNX, Rice (now EQT) |
| 125 | Washington | 63 | ~2,500 | EQT, Range Resources, CNX |
| 051 | Fayette | 26 | ~200 | Mixed operators |
| 129 | Westmoreland | 65 | ~300 | Eastern edge of play |
| 003 | Allegheny | 02 | ~150 | Urban/suburban edge |
| 019 | Butler | 10 | ~400 | Rex Energy (now PennEnergy), XTO |
| 063 | Indiana | 32 | ~200 | Central PA edge |
| 117 | Tioga | 59 | ~1,100 | Seneca Resources, SWEPI |

### NE PA Marcellus (Secondary)

| FIPS | County | PA Code | Unconv Wells | Key Operators |
|------|--------|---------|-------------|---------------|
| 015 | Bradford | 08 | ~1,800 | Southwestern, Chesapeake |
| 115 | Susquehanna | 58 | ~1,200 | Cabot Oil & Gas |
| 131 | Wyoming | 66 | ~200 | Cabot, SWN |
| 081 | Lycoming | 41 | ~800 | Anadarko/Oxy, SWEPI |

See `references/county_codes.md` for full 67-county FIPS mapping and
county assessment data access links.

---

## Workflow

### Step 1 — Resolve Intent

Map the user's question to a query mode:

| User Request | Query Mode | Approach |
|-------------|------------|----------|
| "Parcels near Marcellus wells in Greene County" | Parcel-well correlation | Wells query + parcel buffer |
| "Who owns land near EQT wells in Washington County?" | Owner analysis | Wells query + parcel buffer + owner name |
| "Energy company parcels in Greene County" | Owner pattern search | Parcels LIKE '%ENERGY%' |
| "Active unconventional wells by county" | Well aggregation | Statistics query on wells |
| "Mineral parcels in SW PA" | Multi-county search | Iterate target counties |
| "Parcels owned by HEIRS in Washington County" | Owner pattern | Parcels LIKE '%HEIRS%' |
| "How many parcels in Greene County?" | Count | returnCountOnly |

Default to the 8 SW PA target counties unless the user specifies otherwise.
Default well filter is `WELL_STATUS='Active' AND UNCONVENTIONAL_IND='Yes'`.

### Step 2 — Query Parcels Near Wells

The core workflow spatially correlates parcels with active unconventional wells:

**2a. Get active unconventional wells in the target county:**
```bash
curl -s "https://gis.dep.pa.gov/depgisprd/rest/services/OilGas/OilGasAllStrayGasEGSP/MapServer/3/query" \
  --data-urlencode "where=COUNTY='Greene' AND UNCONVENTIONAL_IND='Yes' AND WELL_STATUS='Active'" \
  --data-urlencode "outFields=PERMIT_NUMBER,WELL_NAME,OPERATOR,LATITUDE,LONGITUDE" \
  --data-urlencode "returnGeometry=false" \
  --data-urlencode "resultRecordCount=50" \
  --data-urlencode "f=json"
```

**2b. For each well, query parcels within buffer (default 1 mile):**
```bash
curl -s "https://gis.dep.pa.gov/depgisprd/rest/services/Parcels/PA_Parcels/MapServer/0/query" \
  --data-urlencode "geometry={longitude},{latitude}" \
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

**Rate limit consideration:** If there are many wells, sample a representative
subset (e.g., 20 wells per county) to avoid excessive API calls. Deduplicate
parcels across wells by `PARCEL_ID`.

### Step 3 — Identify Mineral Indicators

Analyze the returned parcels for mineral interest indicators:

1. **Owner name patterns:** Flag parcels owned by energy companies, mineral
   trusts, or entities with "HEIRS", "ET AL", "MINERAL", "OIL", "GAS",
   "RESOURCES", or "ENERGY" in the owner name.

2. **Large acreage with non-resident owners:** Parcels with significant
   acreage where the owner's mailing address is out-of-state may indicate
   severed mineral interests held by absentee owners.

3. **Multiple parcels same owner:** If the same owner name appears on many
   parcels in a producing area, they may hold mineral interests across the
   play.

**Important:** These are indicators, not confirmation. PA DEP Parcels does
not have a legal description field or property classification that
definitively identifies mineral-only parcels. County assessment records are
the authoritative source.

### Step 4 — Cross-reference Tax Claim Data

For high-priority parcels identified in Steps 2-3, guide the user to
county-level data:

1. **County Assessment Records:** Look up the PARCEL_ID on the county's
   CAMADataSite portal (see `references/county_codes.md` for URLs). The
   county assessment record will show whether the parcel represents surface,
   mineral, or combined ownership.

2. **Tax Claim Bureau:** Contact the county TCB for delinquent property lists.
   PA TCBs publish delinquent lists as PDFs or via their own web portals.
   There is no statewide API.

3. **PA Dormant Minerals Act (58 P.S. 521.1-521.8):** If a mineral interest
   owner cannot be located after 20 years of severed mineral estate inactivity,
   the surface owner may petition to have the mineral rights revert. This is
   relevant for "HEIRS" and "ET AL" parcels near active wells.

### Step 5 — Output

Present results as a markdown table followed by a narrative assessment.
Include guidance on next steps for county-level verification.

---

## Output Format

**Format: Raw Data Table + Assessment Narrative + County Verification Guidance**

### Example Table

```
## Parcels Near Active Unconventional Wells — Greene County, PA

| Parcel ID | Owner | District | Acreage | Nearest Well | Operator | Mineral Indicator |
|-----------|-------|----------|---------|-------------|----------|-------------------|
| 30-9-89 | SMITH JOHN A ET AL | CENTER TWP | 120.0 | 059-28575 | EQT PRODUCTION CO | ET AL (possible severed) |
| 30-12-45 | CONSOL ENERGY INC | JEFFERSON TWP | 500.0 | 059-28600 | EQT PRODUCTION CO | ENERGY (corporate owner) |
| 30-8-112 | JONES MARY B HEIRS | FRANKLIN TWP | 80.0 | 059-28590 | CNX GAS COMPANY | HEIRS (inherited estate) |
| 30-15-3 | WILLIAMS ROBERT | WHITELEY TWP | 45.0 | 059-28610 | RANGE RESOURCES | None detected |
```

### Example Narrative

```
**Summary:** Greene County has approximately 1,800 active unconventional wells,
primarily operated by EQT Production Company and CNX Gas Company. A 1-mile
buffer search around 20 sampled well locations identified 342 unique parcels.

**Mineral Indicators:** Of the 342 parcels, 47 have owner name patterns
suggesting potential mineral interests:
- 12 parcels owned by energy companies (CONSOL ENERGY, CNX GAS, etc.)
- 18 parcels with "HEIRS" or "ET AL" designations
- 8 parcels with "MINERAL" in the owner name
- 9 parcels with out-of-state owner addresses on large acreage

**Key Difference from WV:** Pennsylvania has no statewide delinquent property
GIS layer. Tax delinquency data is maintained by each county's Tax Claim
Bureau. To determine whether any of these 47 parcels are tax-delinquent:
1. Contact the Greene County Tax Claim Bureau at (724) 852-5289
2. Look up parcel IDs on the Greene County assessment portal:
   https://greene.camadatasites.com/
3. Request the annual delinquent property list (published as PDF)

**Third Strata Context:** Under PA's Third Strata Doctrine, the surface
owner listed in DEP Parcels may not own the oil/gas rights. The 18 "HEIRS"
parcels are particularly noteworthy — inherited mineral estates near active
Marcellus wells may be candidates for acquisition, especially if the mineral
interest has been dormant for 20+ years (PA Dormant Minerals Act).

**Caveats:** Owner name patterns are heuristic, not definitive. A parcel
owned by "CONSOL ENERGY" could be surface land, coal rights, or oil/gas
rights. County assessment records are the only way to confirm which strata
an owner holds.
```

---

## Pagination

**PA DEP Parcels:** Max 1,000 records/request. Use `resultOffset` for
pagination. Check `exceededTransferLimit` in the response.

**PA DEP Wells:** Max 5,000 records/request. Use `resultOffset` for
pagination. Check `exceededTransferLimit` in the response.

```python
offset = 0
all_records = []
while True:
    # Parcels: resultOffset=offset, resultRecordCount=1000
    # Wells:   resultOffset=offset, resultRecordCount=5000
    features = response["features"]
    all_records.extend(features)
    if len(features) < page_size or not response.get("exceededTransferLimit"):
        break
    offset += page_size
```

Warn the user if a county query exceeds 10,000 parcels and suggest narrowing
filters (e.g., add owner name pattern or spatial extent).

---

## Error Handling

| HTTP / Error | Meaning | Action |
|-------------|---------|--------|
| 200 + `error` in JSON | Bad query syntax (invalid field, malformed WHERE) | Check field names against schema; verify LIKE syntax |
| 200 + `exceededTransferLimit: true` | More records than limit | Paginate with `resultOffset` or narrow filters |
| 200 + empty `features` array | No matching records | Verify county name spelling (mixed case); check filters |
| 400 | Malformed request | Check parameter encoding, especially `outStatistics` JSON |
| 500 | Server error | Retry; PA DEP GIS services are generally reliable |
| Timeout | Large result set or server load | Reduce `resultRecordCount`; use `returnGeometry=false`; add county filter |

**Note:** PA DEP endpoints use valid SSL certificates. Do not use `-k` with
curl. If SSL errors occur, it indicates a network issue, not a certificate
problem.

---

## Caveats and Data Quality Notes

1. **No statewide delinquent property layer.** This is the fundamental
   difference from WV. PA has 67 county Tax Claim Bureaus that each maintain
   their own delinquent property lists, typically as PDFs or county-specific
   web portals. There is no unified ArcGIS service for delinquent properties
   in PA.

2. **No legal description field in PA DEP Parcels.** Unlike WV's
   ParcelSummary, the PA DEP Parcels service does not include a
   `FullLegalDescription` field. This means the `LIKE '%MINERAL%'` approach
   used in WV cannot be applied here. Mineral identification relies on owner
   name patterns and county assessment cross-reference.

3. **Owner name is not definitive for mineral ownership.** Under PA's Third
   Strata Doctrine, the surface, coal, and oil/gas estates can each have
   different owners. The `OWNER_NAME` in PA DEP Parcels may represent the
   surface owner, not the mineral owner. A parcel owned by "JOHN SMITH" may
   have its oil/gas rights held by "EQT PRODUCTION CO" under a separate
   assessment account.

4. **County assessment systems vary.** Each PA county uses its own property
   classification codes. There is no standard statewide code for mineral-only
   parcels. Greene County may classify minerals differently than Washington
   County.

5. **PA Dormant Minerals Act (58 P.S. 521.1-521.8).** If a severed mineral
   interest has not been the subject of any title transaction, mineral lease,
   or production for 20 years, the surface owner may petition court to
   extinguish the mineral interest and have it revert to the surface estate.
   This affects the value and actionability of identified mineral parcels.

6. **Point geometry only.** PA DEP Parcels Layer 0 provides centroid points,
   not polygon boundaries. For spatial overlap analysis requiring polygons,
   use the PASDA service (limited attributes) or county GIS data.

7. **4.6 million records.** Unfiltered statewide queries will hit pagination
   limits. Always filter by `COUNTY_NAME`, spatial extent, or owner name
   pattern to keep result sets manageable.

8. **Well coordinates are surface locations.** The `LATITUDE`/`LONGITUDE`
   fields represent the well pad surface location, not the bottomhole target.
   Horizontal Marcellus laterals extend 5,000-15,000+ feet from the surface
   location. A 1-mile buffer catches most nearby parcels, but the subsurface
   well path may extend further.

9. **COUNTY_CODE is PA-specific, not FIPS.** The PA DEP Parcels `COUNTY_CODE`
   field uses PA's own 2-digit numbering (e.g., Greene = "30"). The
   `COUNTY_NAME` field is more reliable for filtering. See
   `references/county_codes.md` for the full mapping.

10. **Data freshness.** Parcel ownership, well status, and tax delinquency
    status change over time. PA DEP services are updated periodically but
    may lag current records. Verify critical information with county offices.

---

## Implementation Notes

- **Prefer `bash_tool` with `curl` + `jq`** for API calls in Claude's
  environment
- **Use `curl -s`** (not `-sk`) for PA DEP endpoints — they have valid SSL
  certificates
- **Python example** — see `references/python_example.py` (stdlib only:
  urllib, json, ssl, argparse). Covers parcel queries, well queries, and
  the parcel-near-wells cross-reference workflow.
- **ArcGIS Parcels reference** — see `references/arcgis_parcels.md` for
  full PA DEP Parcels schema, mineral identification approaches, and
  Third Strata Doctrine context
- **ArcGIS Wells reference** — see `references/arcgis_wells.md` for PA DEP
  Oil/Gas well layer schema, enumerated values, and spatial query examples
- **County codes** — see `references/county_codes.md` for all 67 PA counties
  with FIPS codes, PA county codes, target county statistics, TCB phone
  numbers, and CAMADataSite URLs
- The PA DEP services support `f=geoJSON` for direct GeoJSON output suitable
  for mapping with `pnge-gis-mapper`
- Date fields in the wells service are epoch milliseconds — convert with
  `jq` using `.PERMIT_DATE / 1000 | strftime("%Y-%m-%d")`
- For county assessment lookups, the key target sites are:
  - Greene: https://greene.camadatasites.com/
  - Washington: https://washington.camadatasites.com/
  - Fayette: https://fayette.camadatasites.com/
  - Allegheny: https://www2.alleghenycounty.us/RealEstate/

### County Tax Claim Bureau Phone Numbers (Target Counties)

| County | TCB Phone | Notes |
|--------|-----------|-------|
| Greene | (724) 852-5289 | Waynesburg courthouse |
| Washington | (724) 228-6770 | Washington courthouse |
| Fayette | (724) 430-1210 | Uniontown courthouse |
| Westmoreland | (724) 830-3429 | Greensburg courthouse |
| Allegheny | (412) 350-4100 | Pittsburgh, County Office Building |
| Butler | (724) 284-5320 | Butler Government Center |
| Indiana | (724) 465-3805 | Indiana courthouse |
| Tioga | (570) 724-9120 | Wellsboro courthouse |
| Bradford | (570) 265-1722 | Towanda courthouse |
| Susquehanna | (570) 278-4600 x1240 | Montrose courthouse |
