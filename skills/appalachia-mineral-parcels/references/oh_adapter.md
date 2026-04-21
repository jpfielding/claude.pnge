# OH Adapter — OGRIP StateLUC 200-Series + ODNR Wells + Dormant Mineral Act

## Services

```
OGRIP Statewide Parcels (6,313,611; primary mineral-coded source):
  https://services2.arcgis.com/MlJ0G8iWUyC7jAmu/arcgis/rest/services/OhioStatewidePacels_full_view/FeatureServer/0
    Note: URL has typo ("Pacels") — this IS the production URL
    Native SRS: EPSG:3735 (Ohio State Plane South, US feet)
    ALWAYS include outSR=4326 when requesting geometry

OIT Statewide Parcels 2022 (owner-name enrichment):
  https://maps.ohio.gov/arcgis/rest/services/Statewide_Parcels_2022/MapServer/0

ODNR Oil and Gas Wells (241,949):
  https://gis.ohiodnr.gov/arcgis/rest/services/DOG_Services/Oilgas_Wells_public/MapServer/0

County-specific delinquent layers (supplemental):
  Stark:    https://scgisa.starkcountyohio.gov/arcgis/rest/services/Auditor/StarkCountyParcels/MapServer/0
  Cuyahoga: https://services5.arcgis.com/Xti6g2pFdrO8EjbP/arcgis/rest/services/Opportunity_Zones___State_Forfeiture_WFL1/FeatureServer/0
```

Record limits: OGRIP 2,000 / OIT 2,000 / ODNR 1,000. Valid SSL throughout.

No API key required for any endpoint.

---

## OGRIP's Key Advantage: Explicit LUC Codes

OGRIP tags mineral parcels with `StateLUC` codes in the 200-series. No text
parsing needed — `StateLUC LIKE '2%'` cleanly identifies all ~3,360
mineral-coded parcels statewide. This is the single biggest data advantage
of OH over WV and PA, where mineral identification requires error-prone
text parsing.

### Full 200-Series Catalog

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

### Filter patterns

```sql
-- Oil and gas only
StateLUC IN ('240','250')

-- All mineral types (broad screen)
StateLUC LIKE '2%'

-- Coal only
StateLUC IN ('210','220','230')
```

### Distribution by Category

| Category | Codes | Approx Count | % of Mineral Parcels |
|---|---|---|---|
| Oil & Gas | 240, 250 | ~1,300 | ~39% |
| Coal | 210, 220, 230 | ~1,600 | ~48% |
| Other/Custom | 200, 260, 261, 270 | ~460 | ~13% |
| Total | All 200-series | **~3,360** | 100% |

---

## OGRIP (FeatureServer/0) — Key Fields

| Field | Type | Description | Example |
|---|---|---|---|
| StateParcelID | String | Statewide unique ID | "0100100001" |
| LocalParcelID | String | County parcel number | "01-0010-0001.000" |
| County | String | County name (UPPERCASE) | "BELMONT" |
| StateLUC | String | State Land Use Code | "240" |
| SitusAddressAll | String | Property address | "123 MAIN ST" |
| MailAddressAll | String | Owner mailing address | "PO BOX 456 WHEELING WV" |
| LandArea | Double | Land area (sq ft) | 1568160.0 |
| CAMADataSite | String | County auditor CAMA URL | "https://..." |
| GlobalID | String | UUID for CAMA table joins | "{ABC12345-...}" |

OGRIP does NOT have owner names — use OIT 2022 for that.

`LandArea` is in square feet; divide by 43,560 for acres.

---

## OIT Parcels 2022 (MapServer/0) — Key Fields

| Field | Type | Description | Example |
|---|---|---|---|
| PIN | String | Parcel ID number | "01-0010-0001.000" |
| COUNTY | String | County name | "BELMONT" |
| OWNER1 | String | Primary owner | "SMITH JOHN A" |
| OWNER2 | String | Secondary owner | "& SMITH MARY B" |
| ASSR_ACRES | Double | Assessed acreage | 36.0 |
| AUD_LINK | String | Auditor website link | "https://..." |

Join to OGRIP: `OIT.PIN = OGRIP.LocalParcelID`.

---

## ODNR Wells (MapServer/0) — Key Fields

| Field | Type | Description | Example |
|---|---|---|---|
| API_WELLNO | String | 14-digit API number | "34013200010000" |
| MapSymbol_DESC | String | Well type/symbol | "Gas, Horizontal" |
| WL_STATUS_DESC | String | Current status | "Producing" |
| WL_CNTY | String | County name (mixed case) | "Belmont" |
| CO_NAME | String | Operator name | "ASCENT RESOURCES UTICA LLC" |
| ProducingFormation1 | String | Primary formation | "Utica/Pt Pleasant" |
| Utica_Shale | String | Utica flag | "Yes" / "No" |
| Marcellus_Shale | String | Marcellus flag | "Yes" / "No" |
| Last_Nonzero_Production_Year | Integer | Last year with production | 2023 |
| WH_LAT | Double | Wellhead latitude | 39.9854 |
| WH_LONG | Double | Wellhead longitude | -80.8532 |

### WL_STATUS_DESC values

| Value | Description | Relevance |
|---|---|---|
| Producing | Currently producing | **High** |
| Shut In | Temporarily shut in | Medium |
| Permitted | Permitted, not drilled | Medium |
| Drilling | Currently drilling | High |
| Plugged | Plugged and abandoned | Low |
| Inactive | Not producing | Low |
| Orphan | No responsible operator | Low |

### MapSymbol_DESC values

| Value | Description |
|---|---|
| Gas, Horizontal | Horizontal gas (primary Utica/Marcellus target) |
| Gas, Vertical | Vertical gas |
| Oil, Horizontal | Horizontal oil |
| Oil, Vertical | Vertical oil |
| Injection Well | Class II disposal/EOR |
| Plugged | Plugged well |

---

## Ohio Dormant Mineral Act (ORC 5301.56)

### Overview

The Ohio Dormant Mineral Act, amended 2006, lets a surface owner reclaim
mineral rights abandoned through 20 years of inactivity. Primary legal
tool for extinguishing old severed mineral interests in OH.

### 20-Year Savings-Event Test

A mineral interest is deemed abandoned if, during the preceding 20 years,
NONE of the following savings events have occurred:

| Savings Event | Data Indicator |
|---|---|
| Title transaction | County recorder records (manual) |
| Mineral tax filing | County auditor records (via CAMADataSite) |
| Mineral production | ODNR `Last_Nonzero_Production_Year` < current − 20 |
| Mining/drilling permit | ODNR `WL_STATUS_DESC` = Permitted / Drilling nearby |
| Unitization order | ODNR records (manual) |
| Preservation notice | County recorder records (manual) |
| Known owner | Actual knowledge of mineral owner's identity |

### How the Act Works

1. Surface owner publishes notice in local newspaper + sends registered mail.
2. Mineral owner has 60 days to file a preservation claim.
3. No response → surface owner files affidavit → interest merges into surface.
4. Response filed → interest preserved for another 20-year period.

### Screening (what this skill does)

The skill flags OH mineral parcels where:

- No producing wells within 2 miles, AND
- `Last_Nonzero_Production_Year` on any nearby well is 20+ years ago.

**This skill does not determine abandonment.** It flags candidates for
title examination and legal review.

---

## Target Counties

| FIPS | County | Mineral Parcels | Utica Wells | Key Operators | Notes |
|---|---|---|---|---|---|
| 013 | Belmont | ~600 | ~800 | Ascent, Gulfport, Rice | Major wet/dry gas window |
| 019 | Carroll | ~400 | ~500 | Encino, Rex, Chesapeake | First Utica discoveries (2011) |
| 031 | Columbiana | ~200 | ~200 | Hilcorp, Encino | Northern play edge |
| 067 | Harrison | ~500 | ~600 | Ascent, Gulfport, Eclipse | Active condensate window |
| 081 | Jefferson | ~300 | ~300 | Ascent, Gulfport, EAP Ohio | Eastern play border |
| 103 | Monroe | ~350 | ~400 | Ascent, Eclipse, SWN | Southern Utica/Pt Pleasant |
| 111 | Noble | ~250 | ~300 | Ascent, Gulfport, Rex | Active Utica/Point Pleasant |
| 059 | Guernsey | ~150 | ~200 | Antero, Eclipse | Western productive edge |

OGRIP uses UPPERCASE county names ("BELMONT"). ODNR uses mixed case
("Belmont"). OIT 2022 uses UPPERCASE.

---

## Workflow (Detailed)

### Step 1 — Count first

```bash
curl -s "https://services2.arcgis.com/MlJ0G8iWUyC7jAmu/arcgis/rest/services/OhioStatewidePacels_full_view/FeatureServer/0/query" \
  --data-urlencode "where=County='BELMONT' AND StateLUC LIKE '2%'" \
  --data-urlencode "returnCountOnly=true" \
  --data-urlencode "f=json"
```

### Step 2 — Fetch mineral parcels (WGS84 geometry)

```bash
curl -s "https://services2.arcgis.com/MlJ0G8iWUyC7jAmu/arcgis/rest/services/OhioStatewidePacels_full_view/FeatureServer/0/query" \
  --data-urlencode "where=County='BELMONT' AND StateLUC LIKE '2%'" \
  --data-urlencode "outFields=StateParcelID,LocalParcelID,County,StateLUC,MailAddressAll,LandArea,CAMADataSite" \
  --data-urlencode "returnGeometry=true" \
  --data-urlencode "outSR=4326" \
  --data-urlencode "resultRecordCount=100" \
  --data-urlencode "f=json"
```

**Without `outSR=4326`, coordinates come back in EPSG:3735 (Ohio State
Plane South, US feet) — large numbers unusable for ODNR spatial joins.**

### Step 3 — Owner enrichment from OIT 2022

```bash
curl -s "https://maps.ohio.gov/arcgis/rest/services/Statewide_Parcels_2022/MapServer/0/query" \
  --data-urlencode "where=COUNTY='BELMONT' AND PIN='01-0010-0001.000'" \
  --data-urlencode "outFields=PIN,OWNER1,OWNER2,ASSR_ACRES,AUD_LINK" \
  --data-urlencode "returnGeometry=false" \
  --data-urlencode "f=json"
```

Join OIT.PIN ↔ OGRIP.LocalParcelID. Batch 50 PINs per WHERE.

### Step 4 — Well correlation

```bash
curl -s "https://gis.ohiodnr.gov/arcgis/rest/services/DOG_Services/Oilgas_Wells_public/MapServer/0/query" \
  --data-urlencode "geometry={lon},{lat}" \
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

For dormant-mineral screening, expand to 2 miles and drop `WL_STATUS_DESC`
filter so you can inspect `Last_Nonzero_Production_Year` across all nearby
wells.

### Step 5 — Optional county delinquent supplement

Stark County example (has CERTIFIED_DELINQUENT_YEAR, TOTAL_BILLED, etc.):

```bash
curl -s "https://scgisa.starkcountyohio.gov/arcgis/rest/services/Auditor/StarkCountyParcels/MapServer/0/query" \
  --data-urlencode "where=CERTIFIED_DELINQUENT_YEAR IS NOT NULL AND CERTIFIED_DELINQUENT_YEAR > 0" \
  --data-urlencode "outFields=PARCELNO,CERTIFIED_DELINQUENT_YEAR,TOTAL_BILLED,TOTAL_PAID,FINAL_BALANCE" \
  --data-urlencode "returnGeometry=false" \
  --data-urlencode "resultRecordCount=20" \
  --data-urlencode "f=json"
```

For the 8 target Utica counties (none have GIS delinquent data), surface
the `CAMADataSite` URL to direct users to the county auditor site.

---

## Output Columns for OH Rows

`state=OH`, `Parcel ID`=LocalParcelID, `Owner`=OWNER1+OWNER2 (from OIT)
or MailAddressAll (OGRIP fallback), `Status/LUC`=StateLUC with description
(e.g., "240 (O&G WI)"), `Legal/District`=County or SitusAddressAll,
`Acres`=LandArea/43560 or ASSR_ACRES, `Tax Status`=dormant-screen result
or `(via CAMA)`, `Nearby Wells`=count, `Formation`=ProducingFormation1
(most common nearby), `Operator`=CO_NAME (most common nearby),
`Last Prod`=max(Last_Nonzero_Production_Year) across nearby wells.

---

## County-Level LUC Coverage

StateLUC coverage varies by county. The 8 target Utica counties have good
coding. Western/central OH counties with few severed minerals have low
coding. The 3,360 statewide count is a lower bound.

| Coverage | Counties | Notes |
|---|---|---|
| Good | Belmont, Harrison, Jefferson, Monroe, Carroll | Eastern coal/gas counties |
| Moderate | Noble, Guernsey, Columbiana | Some minerals use non-200 codes |
| Low | Western/central OH | Few severed minerals |

---

## Pitfalls

- URL has typo `OhioStatewidePacels_full_view` — this IS correct.
- Native SRS is EPSG:3735 — coordinates are in US feet without `outSR=4326`.
- OGRIP has no owner names; use OIT 2022 (2022 vintage, may be stale).
- County name case: OGRIP = UPPER, ODNR = mixed, OIT = UPPER.
- `Last_Nonzero_Production_Year` is the dormancy proxy but does NOT include
  title transactions, tax filings, unitization orders, or preservation
  notices — those are off-GIS.
- `LandArea` is square feet, not acres.
- Utica horizontal laterals can exceed 15,000 ft — a 1-mile buffer may miss
  subsurface overlap.
