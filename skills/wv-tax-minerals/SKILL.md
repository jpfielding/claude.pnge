---
name: wv-tax-minerals
description: >
  Query West Virginia delinquent tax properties and severed mineral rights near
  active Marcellus and Utica wells. Use this skill when the user asks about
  delinquent mineral properties, tax sale mineral rights, sheriff sale WV,
  severed mineral estate, tax-delinquent parcels near wells, WV property tax
  minerals, mineral rights investment, no-bid mineral parcels, state deed
  mineral properties, undervalued mineral rights, or finding delinquent mineral
  parcels near active oil and gas production in West Virginia. Covers 32,749
  delinquent properties statewide with parcel enrichment and well correlation.
  Produces tabular results with investment assessment narratives.
---

# WV Delinquent Tax Mineral Properties

Queries three public West Virginia ArcGIS services to find tax-delinquent
mineral parcels near active Marcellus/Utica wells. West Virginia's severed
mineral estate system means mineral rights are often owned separately from
surface rights, assessed independently, and can become tax-delinquent.
Delinquent mineral parcels near active horizontal wells represent potentially
undervalued assets.

## Credential

**None required.** All three ArcGIS REST services are publicly accessible
with no API key or authentication.

---

## Data Sources

### A. WV Parcels ParcelSummary (Table 11)

```
https://services.wvgis.wvu.edu/arcgis/rest/services/Planning_Cadastre/WV_Parcels/MapServer/11
```

Non-spatial table containing tax assessment data for all parcels statewide.
Used to enrich delinquent records with appraisal values, tax class, acreage,
and deed references. Max 2,000 records/request.

### B. Delinquent Properties

```
https://services.wvgis.wvu.edu/arcgis/rest/services/Planning_Cadastre/Delinquent_Properties/MapServer
```

- **Layer 0:** Point centroids (32,749 records) — use for spatial queries
- **Layer 1:** Polygon boundaries (32,749 records) — use for mapping

Geocoded delinquent property records with status tracking through the WV tax
sale lifecycle. Max 2,000 records/request.

### C. WVDEP Oil and Gas Wells

```
https://tagis.dep.wv.gov/arcgis/rest/services/WVDEP_enterprise/oil_gas/MapServer/7
```

All DEP wells (153,000+). Used for spatial correlation: find active wells
within configurable radius of delinquent mineral parcels. Max 3,000
records/request.

**Production data (per-well):**
```
https://tagis.dep.wv.gov/oog/get_production_data_RBDMS.php?api={permitid}
```

---

## API Structure

All three services use the standard ArcGIS REST query pattern:

```
POST {service_url}/{layerId}/query
```

**Common parameters:**

| Parameter | Required | Description | Example |
|-----------|----------|-------------|---------|
| where | Yes | SQL WHERE clause | `county='Tyler'` |
| outFields | No | Comma-separated fields | `CleanParcelID,status` or `*` |
| f | Yes | Response format | `json` or `geoJSON` |
| resultRecordCount | No | Max records per request | `100` |
| resultOffset | No | Pagination offset | `2000` |
| returnGeometry | No | Include coordinates | `false` |
| returnCountOnly | No | Return count only | `true` |
| geometry | No | Spatial filter | `-80.9,39.3,-80.6,39.5` |
| geometryType | No | Geometry type | `esriGeometryEnvelope` |
| inSR | No | Input spatial reference | `4326` |
| outSR | No | Output spatial reference | `4326` |
| spatialRel | No | Spatial relationship | `esriSpatialRelIntersects` |
| distance | No | Buffer distance (meters) | `1609.34` (1 mile) |
| units | No | Distance units | `esriSRUnit_Meter` |

### Working curl Examples

**Count delinquent mineral parcels in Tyler County:**
```bash
curl -s "https://services.wvgis.wvu.edu/arcgis/rest/services/Planning_Cadastre/Delinquent_Properties/MapServer/0/query" \
  --data-urlencode "where=county='Tyler' AND FullLegalDescription LIKE '%MINERAL%'" \
  --data-urlencode "returnCountOnly=true" \
  --data-urlencode "f=json"
```

**Fetch actionable delinquent mineral parcels:**
```bash
curl -s "https://services.wvgis.wvu.edu/arcgis/rest/services/Planning_Cadastre/Delinquent_Properties/MapServer/0/query" \
  --data-urlencode "where=county='Tyler' AND status IN ('No Bid','Deed') AND FullLegalDescription LIKE '%MINERAL%'" \
  --data-urlencode "outFields=CleanParcelID,county,status,FullOwnerName,FullLegalDescription,Acres_C,certno,TotalAmtDue" \
  --data-urlencode "returnGeometry=true" \
  --data-urlencode "outSR=4326" \
  --data-urlencode "resultRecordCount=100" \
  --data-urlencode "f=json"
```

**Enrich with ParcelSummary tax data (batch by CleanParcelID):**
```bash
curl -s "https://services.wvgis.wvu.edu/arcgis/rest/services/Planning_Cadastre/WV_Parcels/MapServer/11/query" \
  --data-urlencode "where=CleanParcelID IN ('95-0012-0034-0000-0000','95-0015-0021-0000-0000')" \
  --data-urlencode "outFields=CleanParcelID,FullOwnerName,FullLegalDescription,TaxClass,TotalAppraisal,DeededAcres,DeedBook,DeedPage" \
  --data-urlencode "f=json"
```

**Find active wells near a delinquent parcel (1-mile radius):**
```bash
curl -sk "https://tagis.dep.wv.gov/arcgis/rest/services/WVDEP_enterprise/oil_gas/MapServer/7/query" \
  --data-urlencode "geometry=-80.85,39.40" \
  --data-urlencode "geometryType=esriGeometryPoint" \
  --data-urlencode "inSR=4326" \
  --data-urlencode "spatialRel=esriSpatialRelIntersects" \
  --data-urlencode "distance=1609.34" \
  --data-urlencode "units=esriSRUnit_Meter" \
  --data-urlencode "where=wellstatus='Active Well'" \
  --data-urlencode "outFields=permitid,api,county,welltype,formation,respparty" \
  --data-urlencode "returnGeometry=false" \
  --data-urlencode "resultRecordCount=50" \
  --data-urlencode "f=json"
```

**Statewide mineral delinquent count:**
```bash
curl -s "https://services.wvgis.wvu.edu/arcgis/rest/services/Planning_Cadastre/Delinquent_Properties/MapServer/0/query" \
  --data-urlencode "where=FullLegalDescription LIKE '%MINERAL%'" \
  --data-urlencode "returnCountOnly=true" \
  --data-urlencode "f=json"
```

**Aggregate delinquent properties by status:**
```bash
curl -s "https://services.wvgis.wvu.edu/arcgis/rest/services/Planning_Cadastre/Delinquent_Properties/MapServer/0/query" \
  --data-urlencode "where=county='Tyler'" \
  --data-urlencode "groupByFieldsForStatistics=status" \
  --data-urlencode 'outStatistics=[{"statisticType":"count","onStatisticField":"OBJECTID","outStatisticFieldName":"cnt"}]' \
  --data-urlencode "orderByFields=cnt DESC" \
  --data-urlencode "f=json"
```

---

## Key Fields

### Delinquent_Properties (Layer 0)

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| CleanParcelID | String | Join key to ParcelSummary | "95-0012-0034-0000-0000" |
| county | String | County name | "Tyler" |
| status | String | Delinquent status | "No Bid", "Deed" |
| FullOwnerName | String | Owner at time of delinquency | "SMITH JOHN A ETAL" |
| FullLegalDescription | String | Legal description | "36 AC MINERAL ONLY" |
| Acres_C | Double | Calculated acreage | 36.0 |
| certno | String | Certificate number | "2019-00123" |
| TotalAmtDue | Double | Taxes owed ($) | 245.67 |
| SaleYear | String | Tax sale year | "2019" |

### ParcelSummary (Table 11)

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| CleanParcelID | String | Join key | "95-0012-0034-0000-0000" |
| CountyName | String | County name | "Tyler" |
| FullOwnerName | String | Current owner | "SMITH JOHN A & MARY B" |
| FullLegalDescription | String | Legal description | "PT OF 50 AC MINERAL RIGHTS ONLY" |
| TaxClass | String | Tax classification | "III" |
| PropertyClassCode | String | Property class | "R" |
| LandUseCode | String | Land use category | "800" |
| TotalAppraisal | Double | Assessed value ($) | 15000.00 |
| DeededAcres | Double | Deeded acreage | 50.0 |
| DeedBook | String | Deed book number | "234" |
| DeedPage | String | Deed page number | "567" |

### Mineral Keyword Patterns

| Pattern | SQL | Matches |
|---------|-----|---------|
| MINERAL | `LIKE '%MINERAL%'` | "MINERAL RIGHTS", "MINERAL ONLY" |
| OIL%GAS | `LIKE '%OIL%GAS%'` | "OIL AND GAS", "OIL & GAS RIGHTS" |
| SUR MIN | `LIKE '%SUR MIN%'` | Surface + mineral split |
| COAL | `LIKE '%COAL%'` | Coal rights (separate from O&G) |
| ROYALTY | `LIKE '%ROYALTY%'` | Fractional mineral interests |

The primary keyword `MINERAL` catches ~87 delinquent mineral parcels statewide.
Adding `OIL%GAS`, `SUR MIN`, and `COAL` increases coverage but may introduce
false positives (e.g., "COAL RIVER" as a geographic name).

---

## Key Enumerated Values

### Delinquent Status

| Value | Count | Description | Actionability |
|-------|-------|-------------|---------------|
| No Bid | 10,452 | No buyer at sheriff's sale | **High** — available at next sale |
| Deed | 14,444 | State deed issued | **High** — state owns; may be purchasable |
| Redeemed | 6,898 | Owner paid back taxes | Low — no longer delinquent |
| Sold | 469 | Purchased at sheriff's sale | Low — already acquired |
| Dismissed | 346 | Delinquency dismissed | None |
| Suspended | 131 | Process suspended | Low — in legal limbo |

**Actionable statuses:** `No Bid` and `Deed` are the primary targets.

### TaxClass

| Class | Description | Mineral Relevance |
|-------|-------------|------------------|
| I | Owner-occupied residential | Low |
| II | Non-owner-occupied residential | Medium |
| III | Business/industrial, non-owner mineral | **High** — most severed minerals |
| IV | Personal property | Low |

### PropertyClassCode

| Code | Description |
|------|-------------|
| R | Real Estate (surface and mineral) |
| P | Personal Property |

**Note:** Both surface and mineral parcels use "R". This field cannot
distinguish between them.

### LandUseCode (Selected)

| Code | Description | Mineral Relevance |
|------|-------------|------------------|
| 600 | Mineral Rights | **High** — but rarely used |
| 800 | Vacant/Undeveloped | Medium — mineral-only parcels often coded here |
| 400 | Agricultural | Medium — large tracts with severed minerals |
| 100 | Residential | Low — but mineral rights exist under residential |

---

## Target Counties

Eight northern WV counties with significant overlap between active
Marcellus/Utica drilling and severed mineral estates:

| FIPS | County | Wells | Delinquent | Key Operators |
|------|--------|-------|------------|---------------|
| 017 | Doddridge | ~1,800 | ~200 | EQT, Antero |
| 033 | Harrison | ~2,500 | ~600 | Antero, EQT, Southwestern |
| 049 | Marion | ~1,200 | ~400 | EQT, Southwestern |
| 051 | Marshall | ~3,300 | ~300 | EQT, Southwestern, SWN |
| 069 | Ohio | ~800 | ~250 | Legacy operators |
| 095 | Tyler | ~1,100 | ~150 | EQT, Antero |
| 097 | Upshur | ~900 | ~200 | EQT |
| 103 | Wetzel | ~1,500 | ~250 | EQT, Southwestern |

See `references/county_codes.md` for full 55-county FIPS mapping.

---

## Workflow

### Step 1 — Resolve Intent

Map the user's question to a query mode:

| User Request | Query Mode | WHERE Clause |
|-------------|------------|--------------|
| "Delinquent minerals in Tyler County" | County mineral search | `county='Tyler' AND status IN ('No Bid','Deed') AND FullLegalDescription LIKE '%MINERAL%'` |
| "All delinquent mineral parcels statewide" | Statewide search | `FullLegalDescription LIKE '%MINERAL%'` |
| "No-bid mineral parcels near wells" | County + well correlation | County mineral + spatial well query |
| "How many delinquent minerals in WV?" | Count query | `returnCountOnly=true` |
| "Delinquent parcels by county" | Aggregate query | `groupByFieldsForStatistics=county` |
| "Tax value of delinquent minerals" | Enriched query | Delinquent + ParcelSummary join |
| "Mineral parcels near permit 095-02096" | Well-centric search | Spatial query around well location |

Default to the 8 target counties unless the user specifies otherwise.
Default status filter is `IN ('No Bid','Deed')` (actionable only).

### Step 2 — Fetch Delinquent/Parcel Data

Query the Delinquent_Properties layer for the target county with mineral
keyword filtering on `FullLegalDescription`:

```bash
curl -s "https://services.wvgis.wvu.edu/arcgis/rest/services/Planning_Cadastre/Delinquent_Properties/MapServer/0/query" \
  --data-urlencode "where=county='Tyler' AND status IN ('No Bid','Deed') AND FullLegalDescription LIKE '%MINERAL%'" \
  --data-urlencode "outFields=CleanParcelID,county,status,FullOwnerName,FullLegalDescription,Acres_C,certno,TotalAmtDue" \
  --data-urlencode "returnGeometry=true" \
  --data-urlencode "outSR=4326" \
  --data-urlencode "resultRecordCount=100" \
  --data-urlencode "f=json"
```

Always check count first. If zero results with `MINERAL`, try the broader
keyword set: `OIL%GAS`, `SUR MIN`, `COAL`.

If `returnGeometry=true`, save the coordinates for well correlation in Step 4.

### Step 3 — Enrich with Tax Data

For each delinquent parcel, query ParcelSummary Table 11 using the
`CleanParcelID` join key to get tax assessment details:

```bash
curl -s "https://services.wvgis.wvu.edu/arcgis/rest/services/Planning_Cadastre/WV_Parcels/MapServer/11/query" \
  --data-urlencode "where=CleanParcelID IN ('95-0012-0034-0000-0000','95-0015-0021-0000-0000')" \
  --data-urlencode "outFields=CleanParcelID,TaxClass,TotalAppraisal,DeededAcres,DeedBook,DeedPage,LandUseCode" \
  --data-urlencode "f=json"
```

**Batch in groups of 50 IDs** to stay within URL length limits. No server-side
join exists between these two services — this must be done client-side.

Merge the enrichment data into the delinquent results by matching on
`CleanParcelID`.

### Step 4 — Spatial Well Correlation

For each delinquent mineral parcel with geometry, query WVDEP wells within a
configurable radius (default: 1 mile = 1,609.34 meters):

```bash
curl -sk "https://tagis.dep.wv.gov/arcgis/rest/services/WVDEP_enterprise/oil_gas/MapServer/7/query" \
  --data-urlencode "geometry={lon},{lat}" \
  --data-urlencode "geometryType=esriGeometryPoint" \
  --data-urlencode "inSR=4326" \
  --data-urlencode "spatialRel=esriSpatialRelIntersects" \
  --data-urlencode "distance=1609.34" \
  --data-urlencode "units=esriSRUnit_Meter" \
  --data-urlencode "where=wellstatus='Active Well'" \
  --data-urlencode "outFields=permitid,api,county,welltype,formation,respparty" \
  --data-urlencode "returnGeometry=false" \
  --data-urlencode "resultRecordCount=50" \
  --data-urlencode "f=json"
```

**Rate limit consideration:** If there are many delinquent parcels, limit the
well correlation to the most promising candidates (highest acreage, actionable
status) to avoid excessive API calls.

For high-value targets, optionally fetch production data:
```bash
curl -sk "https://tagis.dep.wv.gov/oog/get_production_data_RBDMS.php?api=095-02096"
```

### Step 5 — Output

Present results as a markdown table followed by a narrative assessment.

---

## Output Format

**Format: Raw Data Table + Investment Assessment Narrative**

### Example Table

```
## Delinquent Mineral Properties — Tyler County, WV

| Parcel ID | Owner | Status | Legal Description | Acres | Appraisal | Taxes Due | Nearby Wells | Formation |
|-----------|-------|--------|-------------------|-------|-----------|-----------|--------------|-----------|
| 95-0012-0034 | SMITH JOHN A ETAL | No Bid | 36 AC MINERAL ONLY | 36.0 | $0 | $245.67 | 3 | Marcellus Shale |
| 95-0015-0021 | JONES MARY B HEIRS | Deed | MIN RIGHTS 100 AC | 100.0 | $1,500 | $312.45 | 1 | Marcellus Shale |
| ... | ... | ... | ... | ... | ... | ... | ... | ... |
```

### Example Narrative

```
**Summary:** Tyler County has 4 delinquent mineral parcels matching the
"MINERAL" keyword with actionable status (No Bid or Deed). These parcels
total 236 acres and have combined back taxes of $1,203.

**Well Proximity:** 3 of 4 parcels are within 1 mile of active wells. The
most notable is the 36-acre SMITH parcel (95-0012-0034), which has 3 active
Marcellus horizontal wells within 1 mile, including permit 095-02096 operated
by EQT Production Company. That well produced over 1,000,000 MCF in its most
recent reported year.

**Valuation Context:** All 4 parcels have $0 county appraisals, which is
typical for severed mineral interests in WV — the county assessor often does
not separately value mineral estates. The actual value of the underlying
mineral rights depends on the producing formation, lease status, and royalty
terms.

**Actionability:**
- **No Bid parcels** (2) will be offered at the next sheriff's tax sale.
  Back taxes range from $150 to $312 — these can potentially be acquired
  for the cost of back taxes plus fees.
- **Deed parcels** (2) are held by the state. Contact the WV State Auditor's
  Office for availability. A quiet title action may be required.

**Caveats:** Mineral identification is based on text parsing of legal
descriptions. Some mineral parcels may not contain the keyword "MINERAL."
Parcel centroids are approximate — the subsurface mineral estate may not
align exactly with the mapped centroid. Verify all information with county
records before taking investment action.
```

---

## Pagination

**Delinquent_Properties and ParcelSummary:** Max 2,000 records/request.
**WVDEP Wells:** Max 3,000 records/request.

Use `resultOffset` for pagination. Check `exceededTransferLimit` in the
response:

```python
offset = 0
all_records = []
while True:
    # fetch with resultOffset=offset and resultRecordCount=2000
    features = response["features"]
    all_records.extend(features)
    if len(features) < 2000 or not response.get("exceededTransferLimit"):
        break
    offset += 2000
```

Warn the user if a county has more than 2,000 mineral parcels and suggest
narrowing filters.

---

## Error Handling

| HTTP / Error | Meaning | Action |
|-------------|---------|--------|
| 200 + `error` in JSON | Bad query syntax (invalid field, malformed WHERE) | Check field names; verify LIKE syntax uses single quotes |
| 200 + `exceededTransferLimit: true` | More records than limit | Paginate with `resultOffset` or narrow filters |
| 200 + empty `features` array | No matching records | Try broader keywords; verify county name spelling |
| 400 | Malformed request | Check parameter encoding, especially `outStatistics` JSON |
| 500 | Server error | Retry; WVU GIS services are generally reliable |
| SSL error on WVU GIS | Unexpected — WVU certs are valid | Retry; fall back to `-k` if persistent |
| SSL error on WVDEP | Expected — self-signed certificate | Use `-k` flag with curl; disable verification in Python |
| Timeout | Large result set or server load | Reduce `resultRecordCount`; use `returnGeometry=false` |

---

## Caveats and Data Quality Notes

1. **Mineral identification is text-based.** The `FullLegalDescription LIKE
   '%MINERAL%'` approach catches most but not all mineral parcels. Some
   mineral parcels have sparse legal descriptions with no mineral keyword.
   `PropertyClassCode` is unreliable — most mineral parcels are coded "R"
   (same as surface). Expect false negatives.

2. **$0 appraisals are common and expected.** Many severed mineral interests
   have `TotalAppraisal=0` because WV county assessors often do not separately
   value the mineral estate. This does not mean the minerals are worthless.

3. **Centroid accuracy.** Delinquent_Properties Layer 0 uses parcel centroids.
   For mineral-only parcels, the centroid represents the surface tract from
   which minerals were severed. The subsurface mineral boundary may differ.
   Well correlation results are approximate.

4. **Data freshness.** Delinquent status, tax amounts, and well production
   data reflect the last service update. A "No Bid" parcel may have been
   redeemed or sold since the update. Verify with county records before
   taking action.

5. **No server-side join.** Delinquent_Properties and ParcelSummary are
   separate services with no built-in join. The `CleanParcelID` field is
   the key for client-side joins. Not all delinquent parcels will have a
   matching ParcelSummary record.

6. **County name format.** Delinquent_Properties and ParcelSummary use full
   county names (e.g., "Tyler"). WVDEP wells use 3-digit FIPS codes (e.g.,
   "095"). See `references/county_codes.md` for mapping.

7. **Legal vs. investment advice.** This skill provides data for research and
   screening purposes. It does not constitute legal or investment advice.
   Title searches, quiet title actions, and legal review are required before
   any mineral rights acquisition.

8. **Duplicate parcels.** A property may appear in multiple tax sale years in
   the Delinquent_Properties layer. Deduplicate on `CleanParcelID` when
   aggregating results.

9. **1-mile radius is a starting point.** Horizontal Marcellus wells have
   laterals extending 5,000-10,000+ feet. A 1-mile radius catches most
   nearby wells, but the actual subsurface well path may extend further.
   Increase radius to 2 miles for more comprehensive results.

10. **WVDEP production data** is per-well and returns HTML, not JSON. Parse
    carefully. Production volumes are annual (MCF for gas, BBL for oil).

---

## Implementation Notes

- **Prefer `bash_tool` with `curl` + `jq`** for API calls in Claude's
  environment
- **Use `-k` flag** only for WVDEP (`tagis.dep.wv.gov`) to handle its SSL
  certificate. WVU GIS (`services.wvgis.wvu.edu`) has valid certificates.
- **Python example** — see `references/python_example.py` (stdlib only:
  urllib, json, ssl, argparse)
- **ArcGIS Parcels reference** — see `references/arcgis_parcels.md` for
  ParcelSummary schema, mineral keyword patterns, and tax class details
- **Delinquent reference** — see `references/arcgis_delinquent.md` for
  status lifecycle, join keys, and spatial query examples
- **County codes** — see `references/county_codes.md` for all 55 WV
  counties plus the 8 target county statistics
- The Delinquent_Properties service supports `f=geoJSON` for direct GeoJSON
  output suitable for mapping with `pnge-gis-mapper`
- Batch `CleanParcelID IN (...)` queries to ParcelSummary should use groups
  of ~50 IDs to stay within URL length limits
- For high-value targets, use `pnge-gis-mapper` to create an interactive
  map showing delinquent mineral parcels colored by status with nearby
  well locations
