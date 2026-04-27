# PA Adapter — DEP Parcels + DEP Oil/Gas Wells + Third Strata Context

## Services

```
PA DEP Parcels (4,685,585 records, points):
  https://gis.dep.pa.gov/depgisprd/rest/services/Parcels/PA_Parcels/MapServer/0

PASDA Statewide Parcels (4,397,928, polygons, sparse attributes):
  https://apps.pasda.psu.edu/arcgis/rest/services/PA_Parcels/MapServer/1

PA DEP Oil and Gas Wells (223,664):
  https://gis.dep.pa.gov/depgisprd/rest/services/OilGas/OilGasAllStrayGasEGSP/MapServer
    Layer 1: Unconventional wells (15,328) — Marcellus/Utica horizontals
    Layer 2: Conventional wells (173,452)
    Layer 3: All wells (primary query layer)
```

Record limits: Parcels 1,000 / Wells 5,000. Valid SSL. No `-k` needed.

No API key required for any endpoint.

---

## Why PA Is Different

PA has no statewide delinquent-properties GIS layer — County Tax Claim
Bureaus (TCBs) hold that data as PDFs or county-specific portals. The DEP
Parcels service lacks a `FullLegalDescription` field, so the WV text-parse
trick does not work. Mineral identification relies on:

1. Spatial correlation with active unconventional wells.
2. Owner-name heuristics (HEIRS, ET AL, ENERGY, MINERAL, RESOURCES).
3. Cross-reference to county CAMA assessment sites for stratum-level
   ownership confirmation.

---

## Third Strata Doctrine

PA common law recognizes three mineral strata — surface, coal, and oil/gas
— each potentially owned and assessed separately. A `OWNER_NAME` in the DEP
Parcels layer may represent any one stratum. A parcel owned by "JOHN SMITH"
may have its oil/gas rights held by "EQT PRODUCTION CO" under a separate
tax account. Coding varies across PA's 67 counties; only the county
assessment record can confirm which stratum an owner holds.

## PA Dormant Minerals Act (58 P.S. 521.1–521.8)

If a severed mineral interest has been the subject of **no** title
transaction, mineral lease, or mineral production for 20 years, the surface
owner may petition court to extinguish the mineral interest and have it
revert to the surface estate. The Act is particularly relevant for "HEIRS"
and "ET AL" parcels adjacent to active Marcellus wells — these signal
inherited estates whose mineral owners may be untraceable.

---

## PA DEP Parcels (Layer 0) — Key Fields

| Field | Type | Description | Example |
|---|---|---|---|
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

`COUNTY_CODE` is PA-specific, not FIPS. Use `COUNTY_NAME` for filtering.

---

## PA DEP Wells (Layer 3) — Key Fields

| Field | Type | Description | Example |
|---|---|---|---|
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
| UNCONVENTIONAL_IND | String | "Yes" / "No" | "Yes" |
| WELL_CONFIG_CODE | String | "Horizontal" / "Vertical" / "Deviated" | "Horizontal" |
| COAL_IND | String | Coal presence flag | "Yes", "No" |

### WELL_STATUS values

| Value | Description |
|---|---|
| Active | Currently producing or operating |
| Inactive | Not producing, not plugged |
| Plugged | Permanently sealed |
| Abandoned | Abandoned, unknown plugging status |
| Regulatory Inactive Status | Inactive per DEP regulation |
| Not Drilled | Permitted but never spud |
| Drilling | Currently being drilled |
| Completed | Drilling complete, awaiting production |

### WELL_TYPE values

| Value | Description |
|---|---|
| Gas | Natural gas well |
| Oil | Oil well |
| Gas and Oil | Dual-producing well |
| Dry Hole | Non-productive well |
| Injection | Injection/disposal well |
| Storage | Gas storage well |
| Observation | Monitoring well |

---

## Owner Name Mineral Indicators

| Pattern | SQL | Indicates |
|---|---|---|
| ENERGY | `OWNER_NAME LIKE '%ENERGY%'` | E&P company |
| GAS | `OWNER_NAME LIKE '%GAS%'` | Gas company |
| OIL | `OWNER_NAME LIKE '%OIL%'` | Oil company |
| RESOURCES | `OWNER_NAME LIKE '%RESOURCES%'` | Resource company |
| MINERAL | `OWNER_NAME LIKE '%MINERAL%'` | Mineral trust/interest |
| HEIRS | `OWNER_NAME LIKE '%HEIRS%'` | Inherited estate |
| ET AL | `OWNER_NAME LIKE '%ET AL%'` | Multiple owners |

Heuristic only. "CONSOL ENERGY" could be surface, coal, or oil/gas owner.

---

## Target Counties

### SW PA Marcellus/Utica Play (Primary)

| FIPS | County | PA Code | Unconv Wells | Key Operators |
|---|---|---|---|---|
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
|---|---|---|---|---|
| 015 | Bradford | 08 | ~1,800 | Southwestern, Chesapeake |
| 115 | Susquehanna | 58 | ~1,200 | Cabot Oil & Gas |
| 131 | Wyoming | 66 | ~200 | Cabot, SWN |
| 081 | Lycoming | 41 | ~800 | Anadarko/Oxy, SWEPI |

---

## Workflow (Detailed)

### Step 1 — Wells in target county

```bash
curl -s "https://gis.dep.pa.gov/depgisprd/rest/services/OilGas/OilGasAllStrayGasEGSP/MapServer/3/query" \
  --data-urlencode "where=COUNTY='Greene' AND UNCONVENTIONAL_IND='Yes' AND WELL_STATUS='Active'" \
  --data-urlencode "outFields=PERMIT_NUMBER,WELL_NAME,OPERATOR,LATITUDE,LONGITUDE" \
  --data-urlencode "returnGeometry=false" \
  --data-urlencode "resultRecordCount=50" \
  --data-urlencode "f=json"
```

### Step 2 — Parcels within 1-mile buffer of each well

```bash
curl -s "https://gis.dep.pa.gov/depgisprd/rest/services/Parcels/PA_Parcels/MapServer/0/query" \
  --data-urlencode "geometry={LONGITUDE},{LATITUDE}" \
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

Sample 20 wells per county if more wells exist. Deduplicate parcels by
`PARCEL_ID` across wells.

### Step 3 — Owner-pattern flagging

After the buffer returns parcels, flag those matching the owner-pattern
table. Emit a `Mineral Indicator` column in output.

### Step 4 — Direct owner-pattern search (optional)

```bash
curl -s "https://gis.dep.pa.gov/depgisprd/rest/services/Parcels/PA_Parcels/MapServer/0/query" \
  --data-urlencode "where=COUNTY_NAME='Washington' AND OWNER_NAME LIKE '%EQT%'" \
  --data-urlencode "outFields=PARCEL_ID,OWNER_NAME,DISTRICT,ACREAGE" \
  --data-urlencode "returnGeometry=true" \
  --data-urlencode "outSR=4326" \
  --data-urlencode "resultRecordCount=100" \
  --data-urlencode "f=json"
```

### Step 5 — County CAMA / TCB pointer

Direct user to the county CAMA portal for stratum confirmation and to the
County Tax Claim Bureau for delinquency status.

---

## County CAMADataSite URLs

| County | URL |
|---|---|
| Greene | https://greene.camadatasites.com/ |
| Washington | https://washington.camadatasites.com/ |
| Fayette | https://fayette.camadatasites.com/ |
| Allegheny | https://www2.alleghenycounty.us/RealEstate/ |

## County Tax Claim Bureau Phone Numbers

| County | TCB Phone | Notes |
|---|---|---|
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

---

## Output Columns for PA Rows

`state=PA`, `Parcel ID`=PARCEL_ID, `Owner`=OWNER_NAME,
`Status/LUC`=flagged indicator (e.g., "HEIRS", "ET AL", "ENERGY"),
`Legal/District`=DISTRICT, `Acres`=ACREAGE,
`Tax Status`="(check TCB)" plus phone number,
`Nearby Wells`=count from well-first correlation,
`Formation`=(Marcellus or Utica from operator context),
`Operator`=OPERATOR, `Last Prod`=n/a (PA DEP does not expose last-production
year in the well layer).

---

## Pitfalls

- PA uses Title Case county names ("Greene", not "GREENE"). Queries against
  uppercase return zero results.
- Well coordinates are surface locations; horizontal laterals extend
  5,000–15,000+ feet from the pad. Buffer radius is an approximation.
- Owner patterns are heuristic — "CONSOL ENERGY" might be surface, coal, or
  oil/gas ownership. County CAMA is authoritative.
- Point geometry only from PA DEP Parcels Layer 0. Use PASDA Layer 1 for
  polygons if spatial overlap needs boundaries.
- `PERMIT_DATE` and `SPUD_DATE` are epoch milliseconds; convert with
  `(value / 1000) | strftime("%Y-%m-%d")`.
- 4.6M parcels — always filter by `COUNTY_NAME` or spatial extent.
