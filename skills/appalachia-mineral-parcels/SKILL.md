---
name: appalachia-mineral-parcels
description: >
  Find tax-delinquent, dormant, or severed mineral parcels near active Marcellus
  and Utica wells across WV, PA, and OH via public ArcGIS REST services. Use this
  skill when the user asks about mineral rights, tax-delinquent minerals,
  Appalachian mineral parcels, severed mineral estate, dormant mineral act,
  WV tax minerals, PA mineral parcels, OH OGRIP, mineral leasing target,
  sheriff sale minerals, no-bid mineral parcels, state deed minerals, tax claim
  bureau, Third Strata Doctrine, Dormant Mineral Act ORC 5301.56, PA Dormant
  Minerals Act 58 P.S. 521, StateLUC 200-series, Belmont Harrison Carroll
  Jefferson Monroe Noble Columbiana Guernsey Greene Washington Fayette Tioga
  Bradford Tyler Marshall Doddridge Wetzel minerals, Marcellus mineral
  screening, Utica mineral screening, or undervalued Appalachian mineral
  rights. Unified interface with per-state adapters routing to the correct
  public ArcGIS REST service. No credentials required.
---

# Appalachian Mineral Parcels (WV / PA / OH)

One skill, three state adapters. Finds tax-delinquent, dormant, or severed
mineral parcels near active Marcellus/Utica wells by routing to the
appropriate public ArcGIS REST service for West Virginia, Pennsylvania, or
Ohio. Each state has different data available — WV has a statewide
delinquent-properties layer, OH has explicit 200-series mineral land-use
codes, and PA has neither but supports parcel–well spatial correlation with
owner-name heuristics.

## Credential

**None required.** All ArcGIS REST services in this skill are publicly
accessible with no API key or authentication. WVDEP uses a self-signed SSL
certificate and requires `-k` with curl; WVU GIS, PA DEP, OGRIP, and ODNR
have valid certificates.

---

## State Selector / Intent Routing

Step 1 of every invocation is choosing the adapter. Map the user's request
to one or more states, then follow that adapter's workflow.

| User Cue | Route To | Rationale |
|---|---|---|
| "Tyler County", "Marshall", "Doddridge", "Wetzel" WV, "delinquent mineral" | WV | WV has statewide delinquent layer |
| "Greene County", "Washington County" (PA), "Bradford", "Tioga", "Third Strata" | PA | PA parcels + unconventional wells |
| "Belmont", "Harrison", "Carroll", "Monroe", "Noble", "Guernsey", "Columbiana", "Jefferson" | OH | OGRIP StateLUC 200-series |
| "Marcellus core", "Appalachian play" (no state) | All three, run sequentially | Cross-state scan |
| "Dormant Mineral Act" alone | OH first (ORC 5301.56), then PA (58 P.S. 521) | No WV analogue |
| "Sheriff sale", "no bid", "state deed" | WV | Only WV exposes tax-sale lifecycle in GIS |
| "StateLUC", "OGRIP", "200-series" | OH | OH-specific feature |

**Default target counties** per state, unless the user narrows:

- **WV:** Doddridge (017), Harrison (033), Marion (049), Marshall (051), Ohio (069), Tyler (095), Upshur (097), Wetzel (103)
- **PA (SW Marcellus):** Greene (059), Washington (125), Fayette (051), Westmoreland (129), Allegheny (003), Butler (019), Indiana (063), Tioga (117)
- **OH (Utica core):** Belmont (013), Carroll (019), Columbiana (031), Harrison (067), Jefferson (081), Monroe (103), Noble (111), Guernsey (059)

---

## Data Sources (by State)

### West Virginia

```
Delinquent Properties (32,749 records):
https://services.wvgis.wvu.edu/arcgis/rest/services/Planning_Cadastre/Delinquent_Properties/MapServer
  Layer 0: Point centroids  (primary)
  Layer 1: Polygon boundaries

ParcelSummary (tax assessment enrichment):
https://services.wvgis.wvu.edu/arcgis/rest/services/Planning_Cadastre/WV_Parcels/MapServer/11
  Non-spatial table, join on CleanParcelID

WVDEP Oil and Gas Wells (153,000+):
https://tagis.dep.wv.gov/arcgis/rest/services/WVDEP_enterprise/oil_gas/MapServer/7
  Self-signed cert — use curl -k

Per-well production (HTML, not JSON):
https://tagis.dep.wv.gov/oog/get_production_data_RBDMS.php?api={permitid}
```

Record limits: Delinquent 2,000; ParcelSummary 2,000; WVDEP Wells 3,000.

### Pennsylvania

```
PA DEP Parcels (4.6M records, points):
https://gis.dep.pa.gov/depgisprd/rest/services/Parcels/PA_Parcels/MapServer/0

PASDA Statewide Parcels (4.4M, polygon geometry, sparse attributes):
https://apps.pasda.psu.edu/arcgis/rest/services/PA_Parcels/MapServer/1

PA DEP Oil and Gas Wells (223,664):
https://gis.dep.pa.gov/depgisprd/rest/services/OilGas/OilGasAllStrayGasEGSP/MapServer
  Layer 1: Unconventional (15,328) — Marcellus/Utica horizontals
  Layer 2: Conventional (173,452)
  Layer 3: All wells  (primary query layer)
```

Record limits: Parcels 1,000; Wells 5,000. Valid SSL — do NOT use `-k`.

### Ohio

```
OGRIP Statewide Parcels (6.3M; primary mineral-coded source):
https://services2.arcgis.com/MlJ0G8iWUyC7jAmu/arcgis/rest/services/OhioStatewidePacels_full_view/FeatureServer/0
  Note: URL contains typo "Pacels" — this IS the production URL
  Native SRS EPSG:3735 — always request outSR=4326

OIT Statewide Parcels 2022 (owner-name enrichment):
https://maps.ohio.gov/arcgis/rest/services/Statewide_Parcels_2022/MapServer/0

ODNR Oil and Gas Wells (241,949):
https://gis.ohiodnr.gov/arcgis/rest/services/DOG_Services/Oilgas_Wells_public/MapServer/0

County-specific delinquent layers (supplemental):
  Stark:    https://scgisa.starkcountyohio.gov/arcgis/rest/services/Auditor/StarkCountyParcels/MapServer/0
  Cuyahoga: https://services5.arcgis.com/Xti6g2pFdrO8EjbP/arcgis/rest/services/Opportunity_Zones___State_Forfeiture_WFL1/FeatureServer/0
```

Record limits: OGRIP 2,000; OIT 2,000; ODNR 1,000. Valid SSL.

---

## Common ArcGIS Query Parameters

All adapters use the same ArcGIS REST query pattern:

```
POST {service_url}/{layerId}/query
```

| Parameter | Description | Example |
|---|---|---|
| where | SQL WHERE clause | `county='Tyler'` |
| outFields | Comma-separated fields | `*` or `CleanParcelID,status` |
| f | Response format | `json` or `geoJSON` |
| resultRecordCount | Max per request | `100` |
| resultOffset | Pagination offset | `2000` |
| returnGeometry | Include coordinates | `false` |
| returnCountOnly | Return count only | `true` |
| outSR | Output spatial reference | `4326` (REQUIRED for OGRIP) |
| geometry | Spatial filter | `-80.85,39.40` |
| geometryType | Geometry type | `esriGeometryPoint` / `esriGeometryEnvelope` |
| inSR | Input spatial reference | `4326` |
| spatialRel | Spatial relationship | `esriSpatialRelIntersects` |
| distance | Buffer distance | `1609.34` (meters = 1 mile) |
| units | Distance units | `esriSRUnit_Meter` |

---

## WV Adapter: Delinquent + Severed Mineral Estate

WV is the only state of the three with a unified delinquent-properties GIS
layer (32,749 records statewide). Severed mineral estates are common under
WV law and routinely become tax-delinquent when mineral owners lose track of
inherited interests.

### Actionable statuses

| Value | Count | Meaning | Actionable? |
|---|---|---|---|
| No Bid | 10,452 | No buyer at sheriff's tax sale | **Yes** |
| Deed | 14,444 | State deed issued | **Yes** |
| Redeemed | 6,898 | Owner paid back taxes | No |
| Sold | 469 | Purchased at sheriff's sale | No |
| Dismissed | 346 | Delinquency dismissed | No |
| Suspended | 131 | In legal limbo | No |

Default filter: `status IN ('No Bid','Deed')`.

### Mineral keyword patterns (Delinquent_Properties.FullLegalDescription)

```sql
FullLegalDescription LIKE '%MINERAL%'   -- primary, ~87 statewide
FullLegalDescription LIKE '%OIL%GAS%'   -- broaden
FullLegalDescription LIKE '%SUR MIN%'   -- split surface/mineral
FullLegalDescription LIKE '%COAL%'      -- coal rights (beware "COAL RIVER")
```

### Count delinquent mineral parcels in Tyler County

```bash
curl -s "https://services.wvgis.wvu.edu/arcgis/rest/services/Planning_Cadastre/Delinquent_Properties/MapServer/0/query" \
  --data-urlencode "where=county='Tyler' AND FullLegalDescription LIKE '%MINERAL%'" \
  --data-urlencode "returnCountOnly=true" \
  --data-urlencode "f=json"
```

### Fetch actionable delinquent mineral parcels with geometry

```bash
curl -s "https://services.wvgis.wvu.edu/arcgis/rest/services/Planning_Cadastre/Delinquent_Properties/MapServer/0/query" \
  --data-urlencode "where=county='Tyler' AND status IN ('No Bid','Deed') AND FullLegalDescription LIKE '%MINERAL%'" \
  --data-urlencode "outFields=CleanParcelID,county,status,FullOwnerName,FullLegalDescription,Acres_C,certno,TotalAmtDue" \
  --data-urlencode "returnGeometry=true" \
  --data-urlencode "outSR=4326" \
  --data-urlencode "resultRecordCount=100" \
  --data-urlencode "f=json"
```

### Enrich with ParcelSummary tax data (batch by CleanParcelID, 50 IDs/batch)

```bash
curl -s "https://services.wvgis.wvu.edu/arcgis/rest/services/Planning_Cadastre/WV_Parcels/MapServer/11/query" \
  --data-urlencode "where=CleanParcelID IN ('95-0012-0034-0000-0000','95-0015-0021-0000-0000')" \
  --data-urlencode "outFields=CleanParcelID,FullOwnerName,FullLegalDescription,TaxClass,TotalAppraisal,DeededAcres,DeedBook,DeedPage,LandUseCode" \
  --data-urlencode "f=json"
```

### Find active WVDEP wells within 1 mile of a parcel

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

See `references/wv_adapter.md` for field catalogs, TaxClass/PropertyClassCode/LandUseCode
enumerations, mineral keyword coverage, dormant-mineral statute notes (WV has
no dedicated dormant-mineral act — use the tax-delinquent path instead), and
the full workflow.

---

## PA Adapter: Parcel–Well Spatial Correlation

PA has no statewide delinquent-properties GIS layer. County Tax Claim Bureaus
hold that data as PDFs or county-specific portals. Instead, this adapter
spatially correlates PA DEP Parcels (4.6M) with PA DEP Oil/Gas Wells (223K),
filters to active unconventional wells, and flags mineral-interest indicators
through owner-name patterns.

### Third Strata Doctrine

PA law recognizes three mineral strata — surface, coal, and oil/gas — which
can each have different owners and different tax assessments. An `OWNER_NAME`
in the DEP Parcels layer may represent any one of the three. Coding is not
standardized across PA's 67 counties, so county assessment records are the
only authoritative source for stratum-level ownership.

### PA Dormant Minerals Act (58 P.S. 521.1–521.8)

If a severed mineral interest has seen no title transaction, lease, or
production in 20 years, the surface owner may petition to extinguish it.
This is especially relevant for "HEIRS" and "ET AL" parcels near active wells.

### Owner-name mineral indicators

| Pattern | Indicates |
|---|---|
| `OWNER_NAME LIKE '%ENERGY%'` | E&P company |
| `OWNER_NAME LIKE '%GAS%'` | Gas company |
| `OWNER_NAME LIKE '%OIL%'` | Oil company |
| `OWNER_NAME LIKE '%RESOURCES%'` | Resource company |
| `OWNER_NAME LIKE '%MINERAL%'` | Mineral trust |
| `OWNER_NAME LIKE '%HEIRS%'` | Inherited estate (possible severed) |
| `OWNER_NAME LIKE '%ET AL%'` | Multiple owners (common in mineral) |

### Get active unconventional wells in Greene County

```bash
curl -s "https://gis.dep.pa.gov/depgisprd/rest/services/OilGas/OilGasAllStrayGasEGSP/MapServer/3/query" \
  --data-urlencode "where=COUNTY='Greene' AND UNCONVENTIONAL_IND='Yes' AND WELL_STATUS='Active'" \
  --data-urlencode "outFields=PERMIT_NUMBER,WELL_NAME,OPERATOR,LATITUDE,LONGITUDE" \
  --data-urlencode "returnGeometry=false" \
  --data-urlencode "resultRecordCount=50" \
  --data-urlencode "f=json"
```

### Parcels within 1 mile of a well (owner-name buffer query)

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

### Direct owner-pattern parcel search

```bash
curl -s "https://gis.dep.pa.gov/depgisprd/rest/services/Parcels/PA_Parcels/MapServer/0/query" \
  --data-urlencode "where=COUNTY_NAME='Washington' AND OWNER_NAME LIKE '%EQT%'" \
  --data-urlencode "outFields=PARCEL_ID,OWNER_NAME,DISTRICT,ACREAGE" \
  --data-urlencode "returnGeometry=true" \
  --data-urlencode "outSR=4326" \
  --data-urlencode "resultRecordCount=100" \
  --data-urlencode "f=json"
```

After spatial correlation and owner-name flagging, direct users to:
- County CAMADataSite portals (see `references/pa_adapter.md`)
- County Tax Claim Bureau phone numbers for delinquent lists

See `references/pa_adapter.md` for full PA DEP Parcels schema (PARCEL_ID,
OWNER_NAME, ACREAGE, DISTRICT, etc.), wells schema (PERMIT_NUMBER, OPERATOR,
UNCONVENTIONAL_IND, WELL_STATUS), CAMA URLs, Tax Claim Bureau phone numbers,
and the Third Strata Doctrine context.

---

## OH Adapter: OGRIP StateLUC 200-Series

Ohio is the easiest of the three states because OGRIP parcels carry explicit
200-series `StateLUC` codes for mineral parcels. No text parsing needed.

### 200-Series StateLUC Catalog

| Code | Description | Category | Target? |
|---|---|---|---|
| 200 | Min-Custom Code | General | Yes |
| 210 | Min-Coal Land (surface + rights) | Coal | Secondary |
| 220 | Min-Coal Rights-Working Interest | Coal | Secondary |
| 230 | Min-Coal Rights-Separate Royalty Interest | Coal | Secondary |
| 240 | Min-Oil and Gas-Working Interest | Oil & Gas | **Primary** |
| 250 | Min-Oil and Gas-Separate Royalty Interest | Oil & Gas | **Primary** |
| 260 | Min-Other Minerals | Other | Secondary |
| 261 | Min-Custom Code | Other | Yes |
| 270 | Min-Custom Code | General | Yes |

Filter patterns:
- Oil and gas only: `StateLUC IN ('240','250')`
- All mineral types: `StateLUC LIKE '2%'`
- Coal only: `StateLUC IN ('210','220','230')`

### Ohio Dormant Mineral Act (ORC 5301.56)

A mineral interest may be deemed abandoned if, during the preceding 20 years,
NONE of the following "savings events" have occurred: title transaction,
mineral tax filing, mineral production, mining/drilling permit, unitization
order, claim to preserve, or known-owner identification.

Use `ODNR.Last_Nonzero_Production_Year` as the data-side indicator. If the
value is 20+ years ago and no active/permitted wells exist within 2 miles,
flag the parcel for title examination.

### Count statewide mineral parcels

```bash
curl -s "https://services2.arcgis.com/MlJ0G8iWUyC7jAmu/arcgis/rest/services/OhioStatewidePacels_full_view/FeatureServer/0/query" \
  --data-urlencode "where=StateLUC LIKE '2%'" \
  --data-urlencode "returnCountOnly=true" \
  --data-urlencode "f=json"
```

### Mineral parcels in Belmont County (WGS84 output)

```bash
curl -s "https://services2.arcgis.com/MlJ0G8iWUyC7jAmu/arcgis/rest/services/OhioStatewidePacels_full_view/FeatureServer/0/query" \
  --data-urlencode "where=County='BELMONT' AND StateLUC LIKE '2%'" \
  --data-urlencode "outFields=StateParcelID,LocalParcelID,County,StateLUC,MailAddressAll,LandArea,CAMADataSite" \
  --data-urlencode "returnGeometry=true" \
  --data-urlencode "outSR=4326" \
  --data-urlencode "resultRecordCount=50" \
  --data-urlencode "f=json"
```

**Always include `outSR=4326`.** OGRIP's native SRS is EPSG:3735 (Ohio State
Plane South, US feet) and the coordinates are unusable for spatial well
correlation without reprojection.

### Owner enrichment from OIT 2022

```bash
curl -s "https://maps.ohio.gov/arcgis/rest/services/Statewide_Parcels_2022/MapServer/0/query" \
  --data-urlencode "where=COUNTY='BELMONT' AND PIN='01-0010-0001.000'" \
  --data-urlencode "outFields=PIN,OWNER1,OWNER2,ASSR_ACRES,AUD_LINK" \
  --data-urlencode "returnGeometry=false" \
  --data-urlencode "f=json"
```

### Producing ODNR wells within 1 mile of a mineral parcel

```bash
curl -s "https://gis.ohiodnr.gov/arcgis/rest/services/DOG_Services/Oilgas_Wells_public/MapServer/0/query" \
  --data-urlencode "geometry=-80.85,39.95" \
  --data-urlencode "geometryType=esriGeometryPoint" \
  --data-urlencode "inSR=4326" \
  --data-urlencode "spatialRel=esriSpatialRelIntersects" \
  --data-urlencode "distance=1609.34" \
  --data-urlencode "units=esriSRUnit_Meter" \
  --data-urlencode "where=WL_STATUS_DESC='Producing'" \
  --data-urlencode "outFields=API_WELLNO,MapSymbol_DESC,CO_NAME,ProducingFormation1,Utica_Shale,Last_Nonzero_Production_Year" \
  --data-urlencode "returnGeometry=false" \
  --data-urlencode "resultRecordCount=50" \
  --data-urlencode "f=json"
```

See `references/oh_adapter.md` for the full OGRIP/OIT/ODNR schema catalog,
county-variation notes on LUC coverage, Dormant Mineral Act savings events,
county-level delinquent supplements (Stark, Cuyahoga), and all 88 Ohio
counties.

---

## Unified Workflow

Regardless of state, every run follows five steps.

### Step 1 — Resolve Intent (state + mode)

- Pick state(s) from the routing table above.
- Pick mode: count, parcel fetch, well correlation, dormant screening, or multi-state scan.
- Pick default target counties unless the user narrows.

### Step 2 — Fetch Mineral / Delinquent Parcels

Run the state-appropriate parcel query with geometry (`returnGeometry=true`,
`outSR=4326`) so Step 4 can do spatial correlation.

- **WV:** `Delinquent_Properties/0` with `FullLegalDescription LIKE '%MINERAL%'` + status filter.
- **PA:** `PA_Parcels/0` filtered by `COUNTY_NAME` — geometry + owner name.
- **OH:** `OhioStatewidePacels_full_view/0` with `StateLUC LIKE '2%'` or `StateLUC IN ('240','250')`.

Always check count first. Warn the user if the result set exceeds the
service's record limit.

### Step 3 — Enrich (owners, tax, assessment)

- **WV:** join `Delinquent_Properties` to `ParcelSummary` Table 11 on
  `CleanParcelID` in batches of 50 IDs.
- **PA:** flag owner-name patterns (HEIRS, ET AL, ENERGY, MINERAL,
  RESOURCES); link county CAMA site for stratum-level assessment.
- **OH:** join to OIT 2022 on `PIN ↔ LocalParcelID` for `OWNER1`/`OWNER2`,
  and surface `CAMADataSite` URL for the county auditor.

### Step 4 — Spatial Well Correlation

For each parcel with geometry, buffer (1 mile default, 2 miles for dormant
screening) and query the state's well layer:

- **WV:** WVDEP Layer 7, `wellstatus='Active Well'` (use `curl -k`).
- **PA:** DEP Wells Layer 3, `UNCONVENTIONAL_IND='Yes' AND WELL_STATUS='Active'`.
- **OH:** ODNR Layer 0, `WL_STATUS_DESC='Producing'`; for dormant screening
  drop the status filter and inspect `Last_Nonzero_Production_Year`.

Deduplicate wells across parcels. Cap well queries to the most promising
parcels (largest acreage, actionable status) to avoid rate-limit issues.

### Step 5 — Unified Output

One table, one narrative, regardless of state. Include a `state` column so
multi-state runs stay legible.

---

## Unified Output Format

```
## Appalachian Mineral Parcels — {county, state}

| State | Parcel ID | Owner | Status / LUC | Legal / District | Acres | Tax Status | Nearby Wells | Formation | Operator | Last Prod |
|---|---|---|---|---|---|---|---|---|---|---|
| WV | 95-0012-0034 | SMITH JOHN A ETAL | No Bid | 36 AC MINERAL ONLY | 36.0 | $245 due | 3 | Marcellus | EQT | 2023 |
| PA | 30-9-89 | JONES MARY B HEIRS | HEIRS flag | FRANKLIN TWP | 80.0 | (check TCB) | 1 | Marcellus | CNX | 2023 |
| OH | 01-0010-0001 | (via OIT) | StateLUC 240 (O&G WI) | BELMONT | 36.0 | (via CAMA) | 4 | Utica/Pt Pleasant | ASCENT | 2023 |
```

Narrative sections:

- **Summary** — total parcels matched, actionable count, state-by-state split.
- **Well Proximity** — how many parcels are within 1 mile of active/producing wells; operator concentration; most recent production year.
- **Tax / Dormancy Status** — WV: $ owed and status; PA: pointer to county TCB; OH: dormant-mineral screening result (Last_Nonzero_Production_Year vs. 20-year threshold).
- **Actionability** — WV No Bid/Deed parcels available at next sheriff sale; PA parcels flagged for TCB follow-up + Dormant Minerals Act (58 P.S. 521); OH parcels flagged for Dormant Mineral Act (ORC 5301.56) title exam.
- **Caveats** — data-freshness, text-parse false positives (WV/PA), missing LUC coding (OH), point-centroid vs polygon ambiguity, 1-mile buffer vs. multi-mile lateral reach.

---

## Pagination

| Service | Max/Request | Notes |
|---|---|---|
| WV Delinquent_Properties | 2,000 | Use `resultOffset` |
| WV ParcelSummary | 2,000 | Batch 50 CleanParcelIDs per WHERE |
| WVDEP Wells | 3,000 | Use `resultOffset` |
| PA DEP Parcels | 1,000 | Filter by `COUNTY_NAME` |
| PA DEP Wells | 5,000 | Filter by `COUNTY` + unconv flag |
| OGRIP Parcels | 2,000 | Always `outSR=4326` |
| OIT Parcels 2022 | 2,000 | Enrichment only |
| ODNR Wells | 1,000 | Lower than OGRIP |

Always check `exceededTransferLimit` in the response. If true, paginate with
`resultOffset` or narrow filters.

---

## Error Handling

| Symptom | Meaning | Action |
|---|---|---|
| 200 + `error` in JSON | Bad WHERE syntax / field name | Verify field name, quoting |
| 200 + `exceededTransferLimit: true` | Paged result | Paginate with `resultOffset` |
| 200 + empty `features` | No matches | Check county case (OGRIP=UPPER, others mixed); try broader keyword |
| 400 | Malformed request | URL-encode `outStatistics` JSON carefully |
| 500 | Server error | Retry; services are generally stable |
| Timeout | Large result set | Reduce `resultRecordCount`; set `returnGeometry=false` |
| SSL error on WVDEP | Self-signed cert | Add `-k` flag; valid on WVU/PA/OGRIP/ODNR |
| Huge OGRIP coordinates (10^6+) | Missing `outSR=4326` | Re-run with `outSR=4326`; native EPSG:3735 is in US feet |
| PA county returns 0 parcels | Mixed-case `COUNTY_NAME` mismatch | PA uses Title Case ("Greene"), not upper |

---

## Caveats and Data Quality Notes

1. **Mineral identification is not uniform across states.** WV and PA rely
   on text parsing of legal descriptions or owner names (false positives
   from geographic names like "COAL RIVER"). OH uses explicit StateLUC
   200-series codes but coverage is uneven in non-Utica counties. Treat all
   results as candidates, not confirmations.

2. **Delinquent-data availability is asymmetric.** WV has a statewide GIS
   layer. PA has 67 county Tax Claim Bureaus with no unified API. OH has
   fragmented county-level data; Stark and Cuyahoga expose GIS, but the
   eight Utica-core counties don't.

3. **$0 appraisals are normal for severed minerals.** Many mineral estates
   are not separately assessed. `TotalAppraisal=0` in WV or empty values in
   OH do not mean the rights are worthless.

4. **Centroid vs. polygon.** WV Delinquent Layer 0 and PA DEP Parcels provide
   point centroids. The subsurface mineral boundary may not align. For
   polygon geometry use WV Delinquent Layer 1, PASDA for PA, or OGRIP
   (polygon-capable).

5. **Horizontal laterals extend beyond 1-mile buffers.** Marcellus/Utica
   laterals run 5,000–15,000+ feet from the surface pad. Use 2-mile buffers
   when comprehensive capture is needed.

6. **Dormant mineral statutes vary.** OH's ORC 5301.56 (amended 2006) and
   PA's 58 P.S. 521.1–521.8 have different savings-event rules and notice
   requirements. WV has no dedicated dormant-mineral act — use the
   tax-delinquent pathway instead.

7. **County name format differs across sources.** OGRIP uses uppercase
   ("BELMONT"), ODNR mixed case ("Belmont"), WV Delinquent mixed case
   ("Tyler"), WVDEP wells 3-digit FIPS ("095"), PA DEP Parcels and Wells
   mixed case. Normalize before cross-joining.

8. **Owner-name heuristics are heuristics.** "CONSOL ENERGY" on a PA parcel
   might be surface, coal, or oil/gas — the Third Strata Doctrine means any
   of the three. County assessment records are the only authoritative source.

9. **Data freshness varies.** WVDEP production data reflects last update;
   OIT is 2022 vintage; delinquent statuses can change between sheriff
   sales. Always verify critical records with the originating county.

10. **Legal vs. research use.** This skill provides screening data for
    research. It does not constitute legal or investment advice. Title
    search, quiet title actions, Dormant Mineral Act proceedings, and
    county-level due diligence require licensed counsel.

---

## Implementation Notes

- Prefer `bash_tool` with `curl` + `jq` for API calls.
- `curl -k` ONLY for WVDEP (`tagis.dep.wv.gov`). All others have valid certs.
- `outSR=4326` REQUIRED for OGRIP geometry; optional but recommended elsewhere.
- Batch `CleanParcelID IN (...)` queries to WV ParcelSummary in groups of ~50.
- Go example: `references/golang_client.go` — unified CLI with
  `--state wv|pa|oh` flag (stdlib only: `net/http`, `encoding/json`,
  `flag`).
- See `references/wv_adapter.md`, `references/pa_adapter.md`, and
  `references/oh_adapter.md` for per-state schema catalogs, enumerated
  values, county lists, and deeper workflow detail.
- The `CAMADataSite` URL embedded in OGRIP rows lets users jump directly to
  the county auditor site — surface this in output tables when present.
- Date fields in PA DEP Wells are epoch milliseconds — convert with
  `jq '(.PERMIT_DATE / 1000) | strftime("%Y-%m-%d")'`.
- WVDEP per-well production returns HTML, not JSON — parse with care.
