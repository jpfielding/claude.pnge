# WV Adapter — Delinquent Properties + ParcelSummary + WVDEP Wells

## Services

```
Delinquent_Properties (32,749 records, statewide):
  https://services.wvgis.wvu.edu/arcgis/rest/services/Planning_Cadastre/Delinquent_Properties/MapServer
    Layer 0: Point centroids  (primary — use for spatial queries)
    Layer 1: Polygon boundaries (use for mapping)

ParcelSummary (tax enrichment, non-spatial):
  https://services.wvgis.wvu.edu/arcgis/rest/services/Planning_Cadastre/WV_Parcels/MapServer/11

WVDEP Oil and Gas Wells (153,000+):
  https://tagis.dep.wv.gov/arcgis/rest/services/WVDEP_enterprise/oil_gas/MapServer/7
    Self-signed SSL — use `-k` with curl

Per-well production (HTML output):
  https://tagis.dep.wv.gov/oog/get_production_data_RBDMS.php?api={permitid}
```

Record limits: Delinquent 2,000 / ParcelSummary 2,000 / WVDEP Wells 3,000.

No API key required for any endpoint.

---

## Delinquent_Properties (Layer 0) — Key Fields

| Field | Type | Description | Example |
|---|---|---|---|
| CleanParcelID | String | Join key to ParcelSummary | "95-0012-0034-0000-0000" |
| county | String | County name (mixed case) | "Tyler" |
| status | String | Delinquent status | "No Bid", "Deed" |
| FullOwnerName | String | Owner at time of delinquency | "SMITH JOHN A ETAL" |
| FullLegalDescription | String | Legal description | "36 AC MINERAL ONLY" |
| Acres_C | Double | Calculated acreage | 36.0 |
| certno | String | Certificate number | "2019-00123" |
| TotalAmtDue | Double | Taxes owed ($) | 245.67 |
| SaleYear | String | Tax sale year | "2019" |

### Delinquent Status Counts (statewide)

| Value | Count | Description | Actionability |
|---|---|---|---|
| No Bid | 10,452 | No buyer at sheriff's sale | **High** — available at next sale |
| Deed | 14,444 | State deed issued | **High** — state owns; may be purchasable |
| Redeemed | 6,898 | Owner paid back taxes | Low |
| Sold | 469 | Purchased at sheriff's sale | Low |
| Dismissed | 346 | Delinquency dismissed | None |
| Suspended | 131 | Process suspended | Low |

Default filter: `status IN ('No Bid','Deed')`.

---

## ParcelSummary (Table 11) — Key Fields

| Field | Type | Description | Example |
|---|---|---|---|
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

### TaxClass

| Class | Description | Mineral Relevance |
|---|---|---|
| I | Owner-occupied residential | Low |
| II | Non-owner-occupied residential | Medium |
| III | Business/industrial, non-owner mineral | **High** |
| IV | Personal property | Low |

### PropertyClassCode

Both surface and mineral parcels use `R` (Real Estate). This field cannot
distinguish between them.

### LandUseCode (mineral relevance)

| Code | Description | Notes |
|---|---|---|
| 600 | Mineral Rights | High — but rarely used in practice |
| 800 | Vacant/Undeveloped | Medium — mineral-only often coded here |
| 400 | Agricultural | Medium — large tracts with severed minerals |
| 100 | Residential | Low — but minerals exist underneath |

---

## WVDEP Wells (Layer 7) — Key Fields

| Field | Type | Description |
|---|---|---|
| permitid | String | WV permit ID (e.g., "095-02096") |
| api | String | API number |
| county | String | 3-digit FIPS (e.g., "095") |
| welltype | String | Gas, Oil, Injection, etc. |
| formation | String | Target formation (e.g., "Marcellus Shale") |
| respparty | String | Responsible party / operator |
| wellstatus | String | "Active Well", "Plugged", etc. |

Spatial query: `geometryType=esriGeometryPoint`, `distance=1609.34`,
`units=esriSRUnit_Meter` for 1-mile buffer.

---

## Mineral Keyword Patterns

Text-parse `FullLegalDescription` in the Delinquent_Properties or
ParcelSummary layer.

| Pattern | SQL | Matches | Notes |
|---|---|---|---|
| MINERAL | `LIKE '%MINERAL%'` | "MINERAL RIGHTS", "MINERAL ONLY" | Primary, ~87 statewide |
| OIL%GAS | `LIKE '%OIL%GAS%'` | "OIL AND GAS" | Broaden |
| SUR MIN | `LIKE '%SUR MIN%'` | Surface + mineral split | Broaden |
| COAL | `LIKE '%COAL%'` | Coal rights | Beware "COAL RIVER" geographic names |
| ROYALTY | `LIKE '%ROYALTY%'` | Fractional mineral interest | Broaden |

---

## Target Counties

Eight northern WV counties with high Marcellus/Utica activity overlap with
severed mineral estates:

| FIPS | County | Wells | Delinquent | Key Operators |
|---|---|---|---|---|
| 017 | Doddridge | ~1,800 | ~200 | EQT, Antero |
| 033 | Harrison | ~2,500 | ~600 | Antero, EQT, Southwestern |
| 049 | Marion | ~1,200 | ~400 | EQT, Southwestern |
| 051 | Marshall | ~3,300 | ~300 | EQT, Southwestern, SWN |
| 069 | Ohio | ~800 | ~250 | Legacy operators |
| 095 | Tyler | ~1,100 | ~150 | EQT, Antero |
| 097 | Upshur | ~900 | ~200 | EQT |
| 103 | Wetzel | ~1,500 | ~250 | EQT, Southwestern |

Delinquent_Properties and ParcelSummary use full county names (e.g., "Tyler").
WVDEP wells use 3-digit FIPS codes (e.g., "095").

---

## Dormant Mineral Statute Context

**West Virginia has no dedicated dormant-mineral act** analogous to Ohio's
ORC 5301.56 or Pennsylvania's 58 P.S. 521. WV's path to recovering
abandoned mineral estates runs through:

1. **Tax delinquency and sheriff sale** — this is why the Delinquent_Properties
   layer exists and is the primary tool in this adapter.
2. **Quiet title action** — judicial process to clear clouds on title,
   typically needed after a state-deed acquisition.
3. **Abandoned property statute (W. Va. Code §36-6A-1 et seq.)** — applies
   narrowly to coal-bed methane rights and does not create a general
   dormant-mineral framework.

The practical result: WV surface owners cannot easily extinguish severed
minerals administratively. They must wait for the mineral owner to stop
paying taxes, then acquire through the tax sale.

---

## Workflow (Detailed)

### Step 1 — Resolve

- Pick county/counties. Default to the 8 target counties.
- Pick status filter. Default `status IN ('No Bid','Deed')`.
- Pick keyword. Default `MINERAL`. Fall back to broader set
  (`OIL%GAS`, `SUR MIN`, `COAL`) if zero results.

### Step 2 — Fetch Delinquent Parcels

```bash
curl -s "https://services.wvgis.wvu.edu/arcgis/rest/services/Planning_Cadastre/Delinquent_Properties/MapServer/0/query" \
  --data-urlencode "where=county='Tyler' AND status IN ('No Bid','Deed') AND FullLegalDescription LIKE '%MINERAL%'" \
  --data-urlencode "outFields=CleanParcelID,county,status,FullOwnerName,FullLegalDescription,Acres_C,certno,TotalAmtDue" \
  --data-urlencode "returnGeometry=true" \
  --data-urlencode "outSR=4326" \
  --data-urlencode "resultRecordCount=100" \
  --data-urlencode "f=json"
```

### Step 3 — Enrich with ParcelSummary

Batch `CleanParcelID IN (...)` in groups of ~50 to stay within URL limits.
No server-side join exists — merge client-side on `CleanParcelID`.

```bash
curl -s "https://services.wvgis.wvu.edu/arcgis/rest/services/Planning_Cadastre/WV_Parcels/MapServer/11/query" \
  --data-urlencode "where=CleanParcelID IN ('95-0012-0034-0000-0000','95-0015-0021-0000-0000')" \
  --data-urlencode "outFields=CleanParcelID,TaxClass,TotalAppraisal,DeededAcres,DeedBook,DeedPage,LandUseCode" \
  --data-urlencode "f=json"
```

### Step 4 — Spatial Well Correlation

For each parcel with geometry, buffer 1 mile (1,609.34 m) and query WVDEP.

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

Cap the well query to high-priority parcels (largest acreage, actionable
status) to avoid rate-limit exhaustion.

### Step 5 — Optional per-well production

```bash
curl -sk "https://tagis.dep.wv.gov/oog/get_production_data_RBDMS.php?api=095-02096"
```

Returns HTML, not JSON. Parse with care.

---

## Output Columns for WV Rows

`state=WV`, `Parcel ID`=CleanParcelID, `Owner`=FullOwnerName,
`Status/LUC`=status, `Legal/District`=FullLegalDescription,
`Acres`=Acres_C, `Tax Status`=TotalAmtDue ("$X.XX due"),
`Nearby Wells`=count from WVDEP buffer, `Formation`=formation from nearest
well, `Operator`=respparty, `Last Prod`=from WVDEP production HTML
(if retrieved).

---

## Pitfalls

- WVDEP has a self-signed cert; always use `curl -k`. WVU GIS certs are valid.
- Duplicate parcels can appear across sale years — deduplicate on `CleanParcelID`.
- A `No Bid` parcel may have been redeemed since the last refresh — verify
  with the county before acting.
- `TotalAppraisal=0` is common and expected for severed mineral interests.
- Centroids represent the surface tract from which minerals were severed;
  subsurface boundaries may differ.
- `f=geoJSON` is supported for direct GeoJSON output if downstream mapping
  needs it.
