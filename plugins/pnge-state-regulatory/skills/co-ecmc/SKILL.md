---
name: co-ecmc
description: >
  Query Colorado Energy and Carbon Management Commission (ECMC, formerly COGCC)
  oil, gas, and Class VI carbon-storage data — wells, production, UIC injection
  and disposal permits, spills, flowlines, hearings, and SB19-181 mapping
  layers. Use this skill when the user asks about Colorado oil and gas wells,
  ECMC data, COGCC legacy data, DJ Basin or Wattenberg production, Niobrara or
  Codell completions, Piceance Basin natural gas, Weld County wells, Garfield
  County gas, Colorado produced water volumes, Colorado Class II disposal,
  Colorado SB19-181 maps, COGIS records, or any Colorado upstream regulatory
  data. Critical for high-TDS DJ Basin produced water chemistry and comparison
  case against Marcellus/Utica Appalachian brines. Produces data tables with
  narrative summaries.
---

# Colorado Energy and Carbon Management Commission (ECMC) Data Skill

Queries Colorado oil and gas regulatory data from the ECMC (renamed from the
Colorado Oil and Gas Conservation Commission / COGCC in July 2023 under
SB23-285). Colorado is a top-7 U.S. oil producer and the #5 gas producer, with
production concentrated in two geologic regions: the DJ Basin (Wattenberg
field, Weld County) and the Piceance Basin (Garfield / Rio Blanco / Mesa
counties). SB19-181 (2019) fundamentally reshaped Colorado oil and gas
regulation and is the policy backdrop for ECMC's current permitting rules.

## API Key Handling

**No API key required.** All ECMC public data queries, COGIS record searches,
bulk downloads, and the ArcGIS Online hub are freely accessible without
authentication.

---

## Name Change and URL Churn (Read First)

The agency reorganization in 2023 produced two live URL namespaces that both
serve ECMC content:

| Namespace | Role | Status |
|-----------|------|--------|
| `ecmc.state.co.us` | Legacy application host (COGIS query apps, bulk file downloads) | Active, still serves most data files |
| `ecmc.colorado.gov` | New Drupal-based public-facing site (navigation, documentation, links) | Active, canonical for documentation |
| `cogcc.state.co.us` | Former agency hostname | 301 redirects to `ecmc.state.co.us` |

**Rules of thumb:**
- Bulk data files still live at `ecmc.state.co.us/documents/data/downloads/...`
- Documentation and dataset catalog links live at `ecmc.colorado.gov/...`
- If a URL under `ecmc.colorado.gov` returns 403 to `curl`, send a real
  browser `User-Agent` header — the Drupal front-end blocks empty UAs
- COGIS (the legacy inquiry applications) is still the authoritative
  record-level source and is reached from `ecmc.state.co.us/data.html`

---

## Data Access Architecture

The ECMC provides data through five channels:

1. **COGIS Inquiry Applications** — ColdFusion-based web query tools for
   wells, facilities, production, complaints, levies, operators
2. **Bulk Data Downloads** — monthly/annual CSV and ZIP files under
   `/documents/data/downloads/` on the legacy host
3. **GIS Bulk Downloads** — shapefiles and file geodatabases for fields,
   pits, SB19-181 maps, floodplains, aquatic zones
4. **ArcGIS Online Hub** — hosted feature layers discoverable via the
   ECMC group (ID `280f7c0420604edaa66ed6c0311d31d9`) on ArcGIS Online
5. **Imaged Document Search** — scanned well files, sundry notices,
   completion reports, mechanical integrity tests (MITs)

### Channel 1: COGIS Inquiry Applications

**Base URL:** `https://ecmc.state.co.us/cogis/`

| Query Tool | Path on ecmc.state.co.us |
|-----------|--------------------------|
| Well Inquiry | `cogis/FacilitySearch.asp` |
| Facility Inquiry | `cogis/FacilitySearch.asp` |
| Production Data Inquiry | `cogis/ProductionSearch.asp` |
| Inspection / Incident Inquiry | `cogis/InspectIncident.asp` |
| Operator Inquiry | `cogis/OperatorSearch.asp` |
| Levy Search | `cogis/LevySearch.asp` |
| Sample Site Inquiry | `cogis/SampleSiteSearch.asp` |

Catalog page (human-readable nav):
`https://ecmc.colorado.gov/data-maps-reports/cogis-database`

### Channel 2: Bulk Data Downloads (Preferred for Research)

Catalog page:
`https://ecmc.colorado.gov/data-maps-reports/downloadable-data-documents`

**Monthly production (the canonical file for DJ Basin analytics):**

```
https://ecmc.state.co.us/documents/data/downloads/production/monthly_prod.csv
```

This file is refreshed roughly monthly and contains operator-reported monthly
oil, gas, and water volumes by facility (well/lease). It is the fastest way
to get current production data without scraping COGIS.

**Annual production reports (one file per year, 1999-present):**

```
https://ecmc.state.co.us/documents/data/downloads/production/{YYYY}_prod_reports.csv
https://ecmc.state.co.us/documents/data/downloads/production/{YYYY}_prod_reports.zip
```

Example, 2024:
```bash
curl -sO "https://ecmc.state.co.us/documents/data/downloads/production/2024_prod_reports.csv"
curl -sO "https://ecmc.state.co.us/documents/data/downloads/production/2024_prod_reports.zip"
```

**Annual production summary books (PDF/Access, per state fiscal year):**

```
https://ecmc.state.co.us/documents/data/downloads/production/CO%20{YYYY}%20Annual%20Production%20Summary-xp.zip
```

**Dashboard export (operator activity snapshot):**

```
https://ecmc.state.co.us/documents/data/downloads/Dashboard/DAD_Export.zip
```

**Other bulk datasets (listed on `downloadable-data-documents`):**

| Dataset | Landing URL (on ecmc.colorado.gov) |
|---------|-----------------------------------|
| Active wells by county | `/data-maps/downloadable-data-documents/county-active` |
| Producing well download | `/data-maps/downloadable-data-documents/prod-well-download` |
| Water well download | `/data-maps/downloadable-data-documents/water-well-download` |
| Field download | `/data-maps/downloadable-data-documents/field-download` |
| Spacing order download | `/data-maps/downloadable-data-documents/spacing-download` |
| Flowline download | `/data-maps/downloadable-data-documents/flowline-download` |
| Spills download | `/data-maps/downloadable-data-documents/spills-download` |
| Mechanical Integrity Tests | `/data-maps/downloadable-data-documents/mech-integrity` |
| Complaints | `/data-maps/downloadable-data-documents/complaints-data` |
| Notice of Alleged Violation (NOAV) | `/data-maps/downloadable-data-documents/noav` |
| Operator activity | `/data-maps/downloadable-data-documents/operator-activity` |

### Channel 3: GIS Bulk Downloads

All under `https://ecmc.state.co.us/documents/data/downloads/gis/` as ZIP
shapefiles or file geodatabases:

| File | Content |
|------|---------|
| `COGCC_FIELDS_SHP.zip` | Oil and gas fields (polygon) |
| `PITS_SHP.zip` | Pits (point) |
| `Rule317B_Shapefiles.zip` | Rule 317B public water supply buffers |
| `Rule411a_SurfaceWater.gdb.zip` | Rule 411A surface water features |
| `Rule411b_Grid.zip` | Rule 411B grid |
| `FEMA_Floodplain_Colorado_100yr_Effective_2020.zip` | 100-yr floodplain |
| `Aquatic_Zones.zip` | Aquatic life zones |
| `CPWSB181_20221215.zip` | Colorado Parks and Wildlife SB19-181 layers |
| `CPW_HPH_for_309e_1202c_1202d_20211231.zip` | High-Priority Habitat |
| `HPH_ECMC_2024.zip` | ECMC High-Priority Habitat (2024 revision) |
| `COGCC_CAP_CDP.zip` | Comprehensive Area Plan / Cumulative Impact |
| `RoanRimBuffer.zip` | Roan Plateau / Piceance buffer |
| `frldc_brf.zip` | Federal lands designation |

**SB19-181 datasets (on the new host):**

```
https://ecmc.colorado.gov/sites/ecmc/files/SB181DataFinal_2026_Proposed.gdb_.zip
https://ecmc.state.co.us/documents/data/downloads/gis/SB181DataFinal_20241209.gdb.zip
https://ecmc.colorado.gov/sites/ecmc/files/WellDensityRaster_20250902.gdb_.zip
```

### Channel 4: ArcGIS Online Hub

**ECMC group on ArcGIS Online:**
```
https://www.arcgis.com/home/group.html?id=280f7c0420604edaa66ed6c0311d31d9
```

Hosted feature layers for interactive mapping. Browse the group to find
current layer names, then query their REST endpoints with standard ArcGIS
`f=json` parameters. Layer URLs change when the hub is refreshed, so don't
hardcode them — discover them at query time.

### Channel 5: Imaged Document Search

**URL:** `https://ecmc.state.co.us/weblink/`

Searchable archive of scanned well files: Form 2A location assessments,
Form 2 APDs, Form 5 completion reports, Form 5A stimulation data (Colorado's
equivalent to FracFocus disclosures), Form 6 sundry notices, mechanical
integrity test (MIT) records. The WebLink interface is not an API — use the
form-based search. For individual well files, query by API number.

---

## Query Patterns

### Pull the Monthly Production CSV

```bash
# The fastest way to current Colorado production. ~25 MB CSV.
curl -sO "https://ecmc.state.co.us/documents/data/downloads/production/monthly_prod.csv"

# Peek at header and first Weld County rows:
head -1 monthly_prod.csv
awk -F, '$X=="123"' monthly_prod.csv | head -5
# Weld County FIPS is 123. Column positions vary by year — always
# read the header row first.
```

### Download and Extract Annual Production

```bash
curl -sO "https://ecmc.state.co.us/documents/data/downloads/production/2024_prod_reports.csv"
# 2024 file is ~200 MB. For the zipped equivalent:
curl -sO "https://ecmc.state.co.us/documents/data/downloads/production/2024_prod_reports.zip"
unzip -l 2024_prod_reports.zip
```

### Fetch COGCC Fields Shapefile

```bash
curl -sO "https://ecmc.state.co.us/documents/data/downloads/gis/COGCC_FIELDS_SHP.zip"
unzip -l COGCC_FIELDS_SHP.zip
# Contains COGCC_FIELDS.shp / .dbf / .shx / .prj (NAD83 UTM Zone 13N)
```

### Look Up a Well by API (COGIS)

```bash
# Colorado API numbers are 10 digits: 05-{county-code}-{5-digit-sequence}
# e.g., 05-123-12345 = Weld County. COGIS FacilitySearch accepts the
# 10-digit form. This is a ColdFusion web app — response is HTML.

curl -sL -A "Mozilla/5.0" \
  "https://ecmc.state.co.us/cogis/FacilityDetail.asp?facid=12312345&type=WELL" \
  -o well.html
# Parse well.html for operator, status, TD, formation, production history.
```

### Query the ECMC ArcGIS Online Group

```bash
# List items in the ECMC ArcGIS group:
curl -s "https://www.arcgis.com/sharing/rest/content/groups/280f7c0420604edaa66ed6c0311d31d9?f=json&num=100" \
  | jq '.items[] | {title, type, url}'
# Then query a feature layer with the usual ArcGIS pattern:
curl -s "FEATURE_LAYER_URL/query" \
  --data-urlencode "where=COUNTY='WELD'" \
  --data-urlencode "outFields=*" \
  --data-urlencode "resultRecordCount=10" \
  --data-urlencode "f=json"
```

### SB19-181 Mapping Layers

```bash
# Pull the 2024-12-09 SB181 file geodatabase (polygon layers for
# proximity, disproportionately impacted communities, HPH, etc.):
curl -sO "https://ecmc.state.co.us/documents/data/downloads/gis/SB181DataFinal_20241209.gdb.zip"
# For the 2026 proposed update:
curl -sLO -A "Mozilla/5.0" \
  "https://ecmc.colorado.gov/sites/ecmc/files/SB181DataFinal_2026_Proposed.gdb_.zip"
unzip -l SB181DataFinal_20241209.gdb.zip
# Read with ogr2ogr / GDAL / pyogrio / QGIS.
```

---

## Workflow

### Step 1 — Resolve Intent

| User wants... | Best channel |
|--------------|-------------|
| Specific well details | COGIS FacilitySearch or Imaged Document WebLink |
| Monthly production volumes (current) | `monthly_prod.csv` bulk file |
| Full-year production history | `{YYYY}_prod_reports.csv` per year |
| Field polygons / boundaries | `COGCC_FIELDS_SHP.zip` |
| UIC Class II / disposal wells | COGIS FacilitySearch filtered by `facility type = DW/IW` |
| SB19-181 proximity / cumulative impact | `SB181DataFinal_*.gdb.zip` |
| Class VI carbon storage permits | ECMC UIC Class VI program page + hearings |
| Spills, complaints, NOAVs | Respective bulk-download pages under `/data-maps/downloadable-data-documents/` |
| Flowline routes | `flowline-download` page |
| Spatial analytics (web) | ArcGIS Online group feature layers |

### Step 2 — Fetch Data

For record-level questions, COGIS and WebLink are authoritative but return
HTML. For anything research-scale (trends, basin comparisons, operator
benchmarking), always go to the bulk files — they update on a fixed cadence
and don't trip the scraping alarms.

### Step 3 — Parse Response

- Monthly/annual production CSVs — parse with `csv` module or `awk`
- Annual Summary ZIPs — contain Access `.mdb` files; open with `mdbtools`
  (`mdb-export`) or Python `pyodbc`
- SHP/GDB archives — open with GDAL (`ogr2ogr`), `geopandas`, or QGIS
- COGIS HTML — regex or BeautifulSoup; the pages are simple tables
- ArcGIS REST — JSON responses; treat like any Esri service

### Step 4 — Produce Output

**Format: Raw Data Table + Narrative**

```
## DJ Basin Monthly Production — Weld County (2024)

| Period   | Wells Reporting | Oil (BBL)   | Gas (MCF)   | Water (BBL) |
|----------|-----------------|-------------|-------------|-------------|
| 2024-06  | 27,350          | 14,200,000  | 48,900,000  | 18,400,000  |
| 2024-05  | 27,240          | 14,050,000  | 48,100,000  | 18,100,000  |
| ...      | ...             | ...         | ...         | ...         |

**Summary:** Weld County (county code 123) is the dominant DJ Basin producer,
generating ~85% of Colorado oil and ~45% of Colorado gas. Produced water
runs roughly 1.3x oil volume at Wattenberg — substantially lower than
Permian ratios (5-10x) but with higher TDS (100,000-200,000 mg/L) due to
deeper Niobrara/Codell source formations. Lithium concentrations in DJ Basin
brines typically fall in the 40-120 mg/L range, lower than the Smackover
trend (up to 477 mg/L) but well within the Appalachian Marcellus/Utica range.
Data pulled from monthly_prod.csv (refreshed ~monthly); recent 2-3 months
are preliminary until operator Form 7 reports are finalized.
```

---

## Colorado Basin and County Reference

### Key Basins

| Basin | Primary Counties | Formations | Phase |
|-------|------------------|-----------|-------|
| DJ Basin (Wattenberg) | Weld, Adams, Broomfield, Boulder | Niobrara, Codell, J-Sand, D-Sand | Oil + associated gas |
| Piceance Basin | Garfield, Rio Blanco, Mesa | Williams Fork, Mancos, Mesaverde | Natural gas (dry/wet) |
| Raton Basin | Las Animas, Huerfano | Vermejo, Raton coals | Coalbed methane |
| Paradox Basin | Montezuma, Dolores, San Miguel | Paradox, Cane Creek | Oil, gas, helium |
| San Juan Basin (CO portion) | La Plata, Archuleta | Fruitland coal, Dakota | CBM + gas |
| Sand Wash Basin | Moffat, Routt | Various | Minor |

### Top Producing Counties (2024, oil+gas combined)

| County | County Code | Basin | Notes |
|--------|-------------|-------|-------|
| Weld | 123 | DJ Basin | #1 oil county in CO; Wattenberg core |
| Garfield | 045 | Piceance | #1 gas county; Mamm Creek / Parachute |
| La Plata | 067 | San Juan | Mature CBM |
| Rio Blanco | 103 | Piceance | Williams Fork tight gas |
| Las Animas | 071 | Raton | CBM decline |
| Adams | 001 | DJ Basin | Wattenberg south edge |
| Broomfield | 014 | DJ Basin | SB19-181 focal point (urban proximity) |

### Formations Critical for Li/Mg and Produced Water Research

- **Niobrara (DJ Basin):** Late Cretaceous carbonate-rich shale, 6,500-8,500
  ft TVD in Wattenberg. Produced water TDS 100-180k mg/L. Li typically
  40-120 mg/L, Mg 400-1,500 mg/L, Ba elevated (500-3,000 mg/L). Water-oil
  ratio relatively favorable (0.8-1.5x) compared to Permian.
- **Codell (DJ Basin):** Cretaceous sandstone directly below Niobrara.
  Commingled with Niobrara in most Wattenberg wells. Similar chemistry.
- **J-Sand / D-Sand (DJ Basin):** Shallower conventional reservoirs, lower
  TDS, lower Li.
- **Williams Fork (Piceance):** Tight gas sands. Relatively fresh produced
  water (TDS 5-30k mg/L) — not a Li target but relevant for beneficial
  reuse and discharge studies.
- **Mancos (Piceance):** Source rock shale, deeper and hotter. Limited
  produced-water dataset; emerging interest for geothermal co-production.

**Comparison to Appalachian plays:** DJ Basin brines fall between Marcellus
(Li 10-200 mg/L, TDS 150-300k mg/L) and Smackover (Li up to 477 mg/L, TDS
200-300k mg/L). The DJ's combination of moderate Li, moderate volumes, and
SB19-181-driven disposal constraints makes it one of the more
policy-relevant plays for produced-water mineral recovery pilots.

---

## SB19-181 and the Regulatory Context

Senate Bill 19-181 (April 2019) shifted Colorado's oil and gas regulatory
mission from "fostering" development to "regulating" it, with explicit
mandates around:

- Minimizing adverse impacts to public health, safety, welfare, the
  environment, and wildlife resources
- Local government authority (counties/municipalities can impose stricter
  siting than the state)
- Cumulative impact analysis (Rule 314)
- Disproportionately Impacted (DI) community protections (Rule 318)
- Comprehensive Area Plans (CAPs) for multi-pad development

**Data implications:** ECMC publishes SB19-181 mapping layers (`SB181Data*`)
that codify which parcels trigger enhanced review. These layers are
essential for any siting study. The 2026 proposed update and 2024-12-09
final are both linked from the bulk download page above.

---

## UIC Class II Disposal Context

Colorado's UIC Class II program is delegated to ECMC under EPA primacy.
Class II wells fall into two categories:

- **Class II-D (Disposal):** Saltwater disposal wells receiving produced
  water. Concentrated in Weld County (DJ Basin) and the Piceance.
- **Class II-R (Enhanced Recovery):** Injection for waterflood/EOR.
  Modest inventory compared to Kansas, Oklahoma, Texas.

For compliance history, MITs, and permit detail, cross-reference:
- COGIS FacilitySearch with `facility type = DW/IW`
- EPA UIC database (via the `pnge-federal-data:epa-regulatory` skill, UIC intent mode — `UIC_WELL` table)
- The `pnge-state-regulatory:regulatory-disposal-analyst` agent for integrated analysis
  across federal (EPA) and state (ECMC) layers

Colorado is notably more restrictive than most western states on induced
seismicity. ECMC has a Rule 325 framework for seismic monitoring and
stop-light permit conditions — critical context when comparing Colorado
disposal volumes against Oklahoma, Texas, or Kansas patterns.

---

## Class VI Carbon Storage

ECMC is pursuing EPA primacy for Class VI (CO2 geologic sequestration) and
has several pending and approved Class VI permits. See:

```
https://ecmc.colorado.gov/programs/underground-injection-control/class-vi/program-overview
https://ecmc.colorado.gov/programs/underground-injection-control
```

This is a live regulatory area — cross-reference with the
`pnge-federal-data:netl-carbon-storage` skill for national context and the
`pnge-federal-data:epa-regulatory` skill (Subpart W mode) for reported GHG inventories.

---

## Error Handling

| Condition | Meaning | Action |
|-----------|---------|--------|
| 403 from `ecmc.colorado.gov` | Drupal blocking empty UA | Send a real browser `User-Agent` header (e.g., `Mozilla/5.0 ...`) |
| 500 from `/documents/data/downloads/` directory listing | Directory browsing disabled | Fetch the specific file URL directly, not the index |
| 404 on a legacy `cogcc.state.co.us/...` path | URL rebased to ECMC | Swap hostname to `ecmc.state.co.us` or check the new `ecmc.colorado.gov` catalog |
| Stale CSV (no recent months) | Monthly refresh pending | Check `Last-Modified` header via `curl -I`; expect updates around the end of each month |
| Zero-row `monthly_prod.csv` | Temporary regeneration window | Retry after a few hours; the file is rebuilt in place |
| COGIS ColdFusion error | Session timeout or invalid params | Start a fresh session (new cookies); verify 10-digit API format |
| ArcGIS feature layer 404 | Layer URL rotated | Rediscover from the ECMC ArcGIS group |
| `.mdb` won't open on Linux/Mac | Needs Jet driver | Use `mdbtools` (`mdb-tables`, `mdb-export`) |

---

## Caveats and Data Limitations

1. **Two live hostnames:** `ecmc.state.co.us` (applications and bulk files)
   and `ecmc.colorado.gov` (navigation and documentation) both serve ECMC
   content. Don't assume one supersedes the other — they are complementary.
2. **COGCC → ECMC rename (July 2023):** Older citations, academic papers,
   and USGS reports reference COGCC. The data lineage is continuous; only
   the agency name and primary URL changed. SB23-285 formalized the
   carbon-management expansion.
3. **No modern REST API:** The legacy COGIS inquiry apps are ColdFusion
   (`.asp` / `.cfm`) and return HTML. There is no documented public REST
   or JSON API for individual records. Bulk files are the programmatic
   path.
4. **Production data lag:** Monthly production lags 2-3 months. Form 7
   operator reports have filing deadlines plus revision windows. The most
   recent 2-3 months in `monthly_prod.csv` should be treated as preliminary.
5. **Water volumes (Form 7) vs. injection volumes (Form 7 / UIC):** The
   production CSV tracks water produced at the wellhead. Disposal volumes
   are tracked separately under UIC reporting and may differ due to
   recycling, surface discharge (where permitted under CDPHE), or
   inter-operator water transfers.
6. **Water chemistry not in production files:** ECMC tracks volumes, not
   composition. For Li/Mg/TDS/ions, cross-reference with USGS Produced
   Waters DB (`pnge-core:usgs-produced-waters`) or operator-reported Form 5A
   (Imaged Document Search / WebLink) where available.
7. **SB19-181 layer versioning:** The SB181 geodatabase is updated as
   rules evolve. Always check the filename date suffix (`_20241209`,
   `_2026_Proposed`) and pull the version that matches your analysis
   period. The 2026 proposed version may change before finalization.
8. **API number format:** Colorado uses `05-XXX-XXXXX` (state code 05 +
   3-digit county + 5-digit sequence). COGIS accepts the 10-digit
   concatenated form (`05XXXXXXXX`) and the dashed form interchangeably
   in most fields — but be consistent in bulk-file joins.
9. **Field polygon updates:** `COGCC_FIELDS_SHP.zip` is republished when
   field boundaries are adjusted by commission order. Check
   `Last-Modified` and track against hearing orders if field geometry
   matters to your analysis.
10. **Piceance gas decline:** The Piceance Basin peaked around 2012 and
    has been in long decline. Analyses using pre-2015 Piceance data to
    size current produced-water streams will overstate volumes — always
    pull recent-year files for current-state conclusions.
