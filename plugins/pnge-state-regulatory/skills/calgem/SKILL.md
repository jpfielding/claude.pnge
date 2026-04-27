---
name: calgem
description: >
  Query California Geologic Energy Management Division (CalGEM, formerly DOGGR)
  oil, gas, and geothermal well data — wellbore details, operators, fields,
  injection and disposal wells, aquifer exemptions, and geothermal wells in the
  Salton Sea Known Geothermal Resource Area (KGRA). Use this skill when the
  user asks about California wells, CalGEM data, DOGGR records, Salton Sea
  lithium, Hell's Kitchen project, Controlled Thermal Resources, EnergySource,
  BHE Renewables, geothermal lithium, Imperial County geothermal brines,
  Kern County oilfield produced water, San Joaquin Basin wells, Monterey
  Formation, Los Angeles Basin wells, California produced water, California
  Class II injection wells, SB 1281 water reporting, or any California
  upstream regulatory data. Tie-in: USGS Produced Waters database,
  USGS Mineral Commodity Summaries, EPA Envirofacts UIC. Produces data tables
  with narrative summaries.
---

# California CalGEM (DOGGR) Data Skill

Queries oil, gas, and geothermal well data from the California Geologic Energy
Management Division (CalGEM). CalGEM (renamed from DOGGR — Division of Oil, Gas
and Geothermal Resources — on January 1, 2020) is the state agency within the
California Department of Conservation that regulates drilling, operation, and
plugging of wells.

California matters for Li/Mg research for two distinct reasons:

1. **Salton Sea KGRA (Imperial County)** — the single largest known geothermal
   brine lithium resource in the U.S. Active development projects: Hell's
   Kitchen (Controlled Thermal Resources / CTR), EnergySource Minerals (ATLiS),
   and BHE Renewables (Berkshire Hathaway Energy) at the existing geothermal
   power plants.
2. **Kern County (San Joaquin Basin)** — the largest oilfield produced-water
   volume in the United States, with some of the strictest disclosure rules
   (SB 1281, 2014) and the most extensive Class II injection well network in
   the western U.S.

## API Key Handling

**No API key required.** All CalGEM ArcGIS REST services and public portal data
are freely accessible without authentication.

---

## Data Access Architecture

CalGEM exposes data through four channels:

1. **ArcGIS REST services** (preferred for programmatic access) — WellSTAR map
   services return JSON for well locations, attributes, and status.
2. **Well Finder web app** — interactive map UI backed by the same REST services.
3. **Bulk data files** — monthly production/injection reports (PDF/XLS per
   operator) and statewide roll-up files published on the CalGEM website.
4. **File Request system** — PDF well records, logs, and histories by API number.

### Channel 1: ArcGIS REST Services (Preferred)

Root: `https://gis.conservation.ca.gov/server/rest/services/`

Folders: `CalGEM`, `WellSTAR`, plus supporting layers under `Base`, `CGS`,
`DLRP`, `DMR`, `DO`, `MOL`.

| Service | Path | Layers |
|---------|------|--------|
| Wells (WellSTAR) | `WellSTAR/Wells/MapServer` | 0 = Well, 1 = Geothermal Well |
| Facilities | `WellSTAR/Facilities/MapServer` | Surface facilities |
| Notices | `WellSTAR/Notices/MapServer` | Notice of Intention, etc. |
| Incidents | `WellSTAR/Incidents/MapServer` | Spills, leaks, well control events |
| UGS | `WellSTAR/UGS/MapServer` | Underground gas storage |
| WST | `WellSTAR/WST/MapServer` | WellSTAR additional layers |
| Admin Bounds | `CalGEM/Admin_Bounds/MapServer` | District/operator boundaries |
| Districts | `CalGEM/CalGEM_Districts/MapServer` | CalGEM regulatory districts |
| Aquifer Exemptions | `CalGEM/Primacy_Aquifer_Exemptions/MapServer` | SDWA-exempt aquifers for Class II injection |
| Post-Primacy AEs | `CalGEM/Post_Primacy_Aquifer_Exemptions/MapServer` | Aquifer exemptions granted after EPA primacy |
| TR26 Seeps | `CalGEM/TR26_Seep_Service/MapServer` | Surface expression / seep monitoring |

All services support standard ArcGIS REST query operations. `maxRecordCount`
is 5000 per request; paginate with `resultOffset` and `resultRecordCount`.

### Channel 2: Well Finder (Interactive)

`https://maps.conservation.ca.gov/doggr/wellfinder/` — ArcGIS Web AppBuilder
frontend over the WellSTAR/Wells service. Useful for human navigation; not an
API but pages will link back to the REST service for bulk downloads.

### Channel 3: Bulk Data Files

CalGEM publishes monthly production and injection reports as PDF/XLS files by
operator and by field, plus annual statewide roll-ups. The index URL changes
across SharePoint redesigns. Current path (verify if 404):

`https://www.conservation.ca.gov/calgem/pubs_stats` (occasionally redirects —
the portal has been reorganized multiple times since the DOGGR→CalGEM rename).

If the pubs_stats path 404s, search the CalGEM site for "Annual Report of the
State Oil and Gas Supervisor" and "monthly production injection".

Historical annual "Publication PR" (PR06) statewide data are archived as PDF
volumes going back to 1915.

### Channel 4: File Request System

`https://filerequest.conservation.ca.gov/` — request well-history PDFs, logs,
cores, cuttings descriptions, and drilling records by API number. Free; may
require account registration for bulk requests.

---

## Query Patterns

### Well Search by County, Operator, or Field

```bash
# All Water Disposal wells in Kern County (sample 10)
curl -s "https://gis.conservation.ca.gov/server/rest/services/WellSTAR/Wells/MapServer/0/query" \
  --data-urlencode "where=CountyName='Kern' AND WellType='Water Disposal'" \
  --data-urlencode "outFields=API,LeaseName,WellNumber,WellStatus,WellType,OperatorName,FieldName,District,CountyName" \
  --data-urlencode "returnGeometry=false" \
  --data-urlencode "resultRecordCount=10" \
  --data-urlencode "f=json"
```

### Geothermal Wells in Imperial County (Salton Sea KGRA)

```bash
# Count geothermal wells in Imperial County
curl -s "https://gis.conservation.ca.gov/server/rest/services/WellSTAR/Wells/MapServer/1/query" \
  --data-urlencode "where=CountyName='Imperial'" \
  --data-urlencode "returnCountOnly=true" \
  --data-urlencode "f=json"
# Returns: {"count":1589}  (as of 2026-04)

# Active geothermal wells — pull operator + field + status
curl -s "https://gis.conservation.ca.gov/server/rest/services/WellSTAR/Wells/MapServer/1/query" \
  --data-urlencode "where=CountyName='Imperial' AND WellStatus='Active'" \
  --data-urlencode "outFields=APINumber,LeaseName,WellNumber,WellStatus,WellType,OperatorName,FieldName,AreaName,Lat83,Long83" \
  --data-urlencode "returnGeometry=false" \
  --data-urlencode "resultRecordCount=50" \
  --data-urlencode "f=json"
```

### Spatial Query — Bounding Box around Salton Sea

```bash
# Envelope covers the Salton Sea KGRA (approx)
curl -s "https://gis.conservation.ca.gov/server/rest/services/WellSTAR/Wells/MapServer/1/query" \
  --data-urlencode "geometry=-115.9,33.05,-115.4,33.55" \
  --data-urlencode "geometryType=esriGeometryEnvelope" \
  --data-urlencode "inSR=4326" \
  --data-urlencode "spatialRel=esriSpatialRelIntersects" \
  --data-urlencode "outFields=APINumber,OperatorName,FieldName,WellStatus" \
  --data-urlencode "returnGeometry=false" \
  --data-urlencode "f=json"
```

### Lookup a Well by API Number

California API numbers are 8 digits (county prefix + sequence). CalGEM strips
the 04- (state) and -0000 (completion sidetrack) portions seen in federal API.

```bash
curl -s "https://gis.conservation.ca.gov/server/rest/services/WellSTAR/Wells/MapServer/0/query" \
  --data-urlencode "where=API='02920123'" \
  --data-urlencode "outFields=*" \
  --data-urlencode "f=json"
```

### Aquifer Exemption Overlap (Class II Injection Context)

```bash
# All aquifer exemptions in Kern County
curl -s "https://gis.conservation.ca.gov/server/rest/services/CalGEM/Primacy_Aquifer_Exemptions/MapServer/0/query" \
  --data-urlencode "where=1=1" \
  --data-urlencode "outFields=*" \
  --data-urlencode "returnGeometry=false" \
  --data-urlencode "resultRecordCount=10" \
  --data-urlencode "f=json"
```

---

## Layer 0 (Oil and Gas Wells) — Key Fields

| Field | Description |
|-------|-------------|
| `API` | 8-digit California API number (county code + sequence) |
| `LeaseName` | Operator's name for the lease/pad |
| `WellNumber` | Well number within the lease |
| `WellDesignation` | Designation code |
| `WellStatus` | Active, Idle, Plugged, New, Cancelled, Buried |
| `WellType` | Oil & Gas, Dry Gas, Water Disposal, Steamflood, Waterflood, Observation, etc. |
| `WellTypeLabel` | Human-readable type |
| `OperatorName` | Current operator |
| `FieldName` | Oil/gas field (e.g., Midway-Sunset, Kern River, Lost Hills) |
| `AreaName` | Sub-area within field |
| `District` | CalGEM district (D1–D6) |
| `CountyName` | California county |
| `Latitude` / `Longitude` | WGS84 coordinates |
| `SpudDate` | Drilling start |
| `isDirectionallyDrilled` | Y/N |
| `inHPZ` | In High Priority Zone (methane monitoring) |

## Layer 1 (Geothermal Wells) — Key Fields

Extra fields beyond Layer 0: `GeoDistrict` (geothermal-specific district
numbering), `WellStatusDescription`, `ABDdate` (abandonment date), `CompDate`
(completion), `Lat83`/`Long83` (NAD83 coordinates), `DatumCode`.

---

## Workflow

### Step 1 — Resolve Intent

| User wants... | Best channel |
|---------------|--------------|
| Specific well details | WellSTAR/Wells REST query by API |
| Wells in a county/field/operator | WellSTAR/Wells REST with `where` clause |
| Geothermal/Salton Sea wells | WellSTAR/Wells Layer 1 |
| Class II injection / disposal wells | WellSTAR/Wells with `WellType='Water Disposal'` or `'Steamflood'`/`'Waterflood'` + cross-ref aquifer exemption layers |
| Production/injection volumes | Bulk monthly reports from CalGEM website (not in REST) |
| Well records / logs / cores | File Request system by API |
| Aquifer exemption context | CalGEM/Primacy_Aquifer_Exemptions |

### Step 2 — Source Pick (Well Finder vs CalWIMS vs bulk)

- **Well Finder** (`maps.conservation.ca.gov/doggr/wellfinder/`) — for humans;
  use only as a visual sanity check.
- **WellSTAR REST** — the machine-readable source of truth for well locations
  and attributes. Use for all programmatic queries.
- **CalWIMS** (`wims.conservation.ca.gov`) — legacy Well Information Management
  System. The domain redirects as of 2026-04 and its functions have largely
  migrated into WellSTAR. If the user names CalWIMS, explain the migration and
  fall back to WellSTAR.
- **Bulk monthly reports** — for production/injection volumes per operator per
  field. Must be downloaded from the CalGEM site; not in the REST API.

### Step 3 — Fetch Data

Use `curl` with `--data-urlencode` for REST queries. Respect `maxRecordCount`
(5000). Paginate with `resultOffset` for large sets. Use `returnCountOnly=true`
first for large filters to estimate pagination.

### Step 4 — Parse Response

JSON. Each feature has `attributes` (the fields) and optionally `geometry`.
For tabular research use `returnGeometry=false`.

### Step 5 — Produce Output

**Format: Raw Data Table + Narrative**

```
## Geothermal Wells — Imperial County (Salton Sea KGRA)

| API       | Operator                          | Field          | Status  | Type        |
|-----------|-----------------------------------|----------------|---------|-------------|
| 02500123  | BHE Renewables                    | Salton Sea     | Active  | Geothermal  |
| 02500456  | EnergySource Minerals (ATLiS)     | Salton Sea     | Active  | Geothermal  |
| 02500789  | Controlled Thermal Resources      | Hell's Kitchen | Drilling| Geothermal  |
...

Summary: 1,589 geothermal wells recorded in Imperial County across the Salton
Sea KGRA. Three operators dominate the active lithium-relevant development:
BHE Renewables (legacy geothermal power), EnergySource Minerals (ATLiS DLE
pilot), and Controlled Thermal Resources (Hell's Kitchen integrated geothermal
+ Li project). Salton Sea brines carry ~200-400 mg/L Li at ~250,000-300,000
mg/L TDS — roughly the same Li range as the Smackover Formation (Arkansas)
but with the critical advantage of arriving at surface at ~300 degC, already
hot enough for direct lithium extraction (DLE) without supplementary heating.
```

---

## CalGEM District Reference

| District | Office | Counties / Basins |
|----------|--------|-------------------|
| D1 | Cypress | Los Angeles Basin, Orange County, Ventura, LA County fields (Wilmington, Inglewood, Beverly Hills) |
| D2 | Ventura | Coastal Ventura, northern LA County, offshore state waters |
| D3 | Santa Maria | Central Coast, Santa Barbara, San Luis Obispo, Monterey |
| D4 | Bakersfield | Kern, Kings, Tulare, Fresno — the San Joaquin Basin workhorse (Midway-Sunset, Kern River, Elk Hills, Belridge, Lost Hills, Cymric, Buena Vista) |
| D5 | Coalinga | Western Fresno, western Merced, western San Benito |
| D6 | Cypress (Geothermal) | Imperial (Salton Sea KGRA), The Geysers (Sonoma/Lake), Long Valley, Coso, Mammoth |

### Districts Critical for Li/Mg Research

- **District 4 (Bakersfield / Kern County):** 70,000+ producing wells, >75%
  of California's oil output, ~85% of the state's produced water. Monterey
  Formation and overlying diatomite reservoirs yield 8-10 barrels of water per
  barrel of oil in mature heavy-oil fields. Li concentrations in California
  oilfield waters are **much lower** than Smackover (typically <10-30 mg/L),
  but volumes are enormous. SB 1281 (2014) forces monthly disclosure of
  injected and produced water by source and destination — one of the richest
  water-accounting datasets in the U.S.
- **District 6 (Imperial / Salton Sea):** 11 operating geothermal power plants
  on the southeastern shore of the Salton Sea. The hypersaline brine (~25-28
  wt% TDS, ~300 degC) carries ~200-400 mg/L Li — economically recoverable by
  DLE. Hell's Kitchen, ATLiS, and BHE's integrated lithium projects target
  this resource. See `references/salton_sea_li.md`.

---

## Li/Mg Quick-Reference: California vs Other Basins

| Basin / Brine Source       | Li (mg/L)  | Mg (mg/L)  | TDS (mg/L)   | Notes |
|----------------------------|------------|------------|--------------|-------|
| **Salton Sea (CA)**        | 200-400    | 50-500     | 250,000+     | Geothermal, 300 degC at wellhead — DLE economically attractive |
| **Smackover (AR/TX/LA)**   | 150-477    | 2,000-6,000| 150,000-300,000 | Oilfield, needs heating for DLE |
| **Marcellus (PA/WV/OH)**   | 10-200     | 500-2,500  | 150,000-350,000 | Frac flowback + produced; enormous volumes |
| **Kern County (CA)**       | 5-30       | 50-500     | 5,000-40,000 | Very large volumes, low Li; Mg recovery may be more viable |
| **Permian (TX/NM)**        | 5-50       | 500-2,000  | 100,000-250,000 | Volume story; Li low but sheer scale |
| **Bakken (ND/MT)**         | 10-70      | 500-2,000  | 150,000-350,000 | Moderate Li, cold climate |

The key California contrast: **Salton Sea wins on grade and heat; Kern loses
on grade but wins on volume and regulatory data quality (SB 1281).**

---

## Error Handling

| Condition | Meaning | Action |
|-----------|---------|--------|
| `"error":{"code":400}` | Bad query parameter | Check field names against layer definition; fields are case-sensitive |
| `exceededTransferLimit:true` | Over 5000 records | Paginate with `resultOffset` and `resultRecordCount` |
| Empty `features:[]` | No matches | Broaden `where`; check county spelling (capitalized, no "County" suffix) |
| 404 on CalGEM page | Portal redesign | Try archived URL or search site for topic; use REST service instead |
| CalWIMS domain redirect | Legacy system migrated | Use WellSTAR REST instead |
| 403/session errors | Rate limiting | Throttle; add user-agent; space requests |
| Coordinate in web-mercator | `wkid:102100` default | Set `outSR=4326` to get lat/long back |

---

## Caveats and Data Limitations

1. **Portal redesigns:** CalGEM's website (pubs_stats, WellReports.aspx,
   calwims subdomain) has been reorganized multiple times since the 2020
   DOGGR → CalGEM rename. Many older links 404. The ArcGIS REST services at
   `gis.conservation.ca.gov` are stable; prefer them.
2. **SB 1281 data quality:** SB 1281 (2014) requires monthly reporting of
   water injected and produced volumes by source and destination for oilfield
   operators. Reporting is robust for volumes but has known gaps in water
   **chemistry** — operators are not compelled to report TDS or full ion
   suites unless specifically required by a RWQCB order. See CCST 2020
   report for a critique of SB 1281 data completeness.
3. **Geothermal vs oilfield distinction:** CalGEM regulates both, but they
   are governed by different sections of the Public Resources Code. Layer 0
   (Well) covers oil & gas; Layer 1 (Geothermal Well) covers geothermal.
   These share `WellStatus` and `WellType` vocabularies but not field names
   or operators. Do not conflate them in analysis.
4. **API number format:** California uses 8-digit API, distinct from the
   14-digit federal API. The county code (first 3 digits) maps to California
   county FIPS. Cross-basin joins with USGS produced-waters DB require care.
5. **Confidential wells:** `isConfidential='Y'` / `Confidential='Y'` means
   the well is within the 24-month confidentiality window after spud — some
   attributes may be redacted.
6. **Offshore state waters:** California state waters offshore (within 3
   nautical miles) are in CalGEM jurisdiction; federal OCS is in BOEM/BSEE
   jurisdiction. The South Ellwood and Platform Holly fields straddle this
   boundary.
7. **Geothermal well counts are historical totals.** Only a subset are
   currently producing. Filter on `WellStatus='Active'` for current operations.
8. **Production/injection volumes are NOT in the REST API.** They live in
   operator-level monthly reports (PDF/XLS) downloaded from the CalGEM
   website. Automated retrieval requires scraping or working from archive.org
   snapshots of the pubs_stats index.

---

## Related Skills (Plugin Tie-ins)

- **`pnge-core:usgs-produced-waters`** — pull California subset of the USGS
  Produced Waters DB for geochemistry; cross-reference wells by API against
  CalGEM Layer 0 for operator/field context.
- **`pnge-core:usgs-minerals`** — Li and Mg commodity data, including the Salton
  Sea resource assessment in USGS Mineral Commodity Summaries 2025.
- **`pnge-federal-data:epa-regulatory`** — Envirofacts UIC_WELL cross-reference for Class II
  injection well compliance; California has EPA primacy for Class II programs
  so CalGEM is the primary regulator but EPA retains oversight.
- **`pnge-federal-data:netl-edx`** — DOE NETL critical-minerals datasets; search for
  "Salton Sea" and "geothermal lithium" to find integrated techno-economic
  models.
- **`pnge-core:pnge-literature`** — federated literature search (OpenAlex + CrossRef
  + USGS Pubs + DOE OSTI adapters) for technical reports from Berkeley Lab,
  Sandia, and PNNL on Salton Sea Li resource assessment, DLE chemistry, and
  CCS pilot integration with geothermal lithium extraction.

---

## Reference Files

- `references/salton_sea_li.md` — KGRA boundaries, Li project operators,
  brine chemistry snapshot, and links to USGS and DOE resource assessments.
- `references/well_data_access.md` — detailed query recipes, field vocabularies,
  pagination patterns, and the CalWIMS → WellSTAR migration notes.
- `references/golang_client.go` — minimal Go client for WellSTAR queries with
  pagination, county/field filters, and CSV output.
