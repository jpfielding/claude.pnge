---
name: ok-occ
description: >
  Query Oklahoma Corporation Commission (OCC) oil and gas data — wells,
  production, Class II saltwater disposal (SWD), Arbuckle injection volumes,
  directive AOIs (induced seismicity), drilling permits, and completion
  records. Use this skill when the user asks about Oklahoma oil and gas wells,
  Oklahoma, OCC, Oklahoma Corporation Commission, Anadarko Basin production,
  Arkoma Basin, SCOOP/STACK, Mississippi Lime play, Hunton Lime dewatering,
  Arbuckle disposal, Class II disposal Oklahoma, induced seismicity, Oklahoma
  earthquakes, Pawnee earthquake, Prague earthquake, OCC SWD records, RBDMS
  well search, OCC Data Explorer, OCC Well Data Finder, Oklahoma UIC, or any
  Oklahoma upstream regulatory data. Critical for induced seismicity case
  studies, disposal capacity screening, and Li/Mg produced water research in
  Hunton, Arbuckle, and Mississippian brines. Produces data tables with
  narrative summaries, and cross-references with usgs-earthquakes for
  seismicity context.
---

# Oklahoma Corporation Commission (OCC) Data Skill

Queries Oklahoma oil and gas regulatory data from the Oklahoma Corporation
Commission Oil and Gas Conservation Division (OGCD) and related state sources.
Oklahoma is a top-5 oil and gas state and the global type-locality for
wastewater-induced seismicity. OCC data is essential for Arbuckle disposal
capacity studies, Hunton dewatering economics, and for any Li/Mg recovery
project that must evaluate disposal costs and seismic risk.

## API Key Handling

**No API key required.** All OCC public data, the OCC GIS ArcGIS Enterprise
server, the RBDMS Data Explorer, and the per-county SWD PDFs are freely
accessible without authentication. The Oklahoma Geological Survey (OGS)
earthquake catalog is also open.

---

## Data Access Architecture

The OCC exposes data through five channels:

1. **OCC GIS ArcGIS Server** — public MapServer endpoints with JSON query
2. **OCC Well Data Finder / Well Records / RBDMS Search** — web applications
3. **RBDMS Data Explorer (Data Mining)** — production and injection downloads
4. **Salt Water Disposal Records by County** — per-county PDFs of SWD volumes
5. **Oklahoma Geological Survey (OGS)** — earthquake catalog and well logs

### Channel 1: OCC GIS ArcGIS Enterprise Server

**Base URL:** `https://gis.occ.ok.gov/server/rest/services`

This is an ArcGIS Enterprise 11.3 server with a public folder and a public
GIS Open Data Hub (`https://gisdata-occokc.opendata.arcgis.com/`). The
`PUBLIC` folder does not require tokens; the `UIC` and `ISD` folders return
`499 Token Required` and are not publicly queryable over REST.

| Service | URL | Content |
|---------|-----|---------|
| Induced Seismicity | `https://gis.occ.ok.gov/server/rest/services/PUBLIC/INDUCED_SEISMICITY/MapServer` | All directive AOIs, yellow/red light areas, earthquake points referenced in OCC directives |
| Directive AOIs | `https://gis.occ.ok.gov/server/rest/services/PUBLIC/DIRECTIVE_AOIs/MapServer` | Regional + local seismicity directives (2015-present) |
| OCC Districts | `https://gis.occ.ok.gov/server/rest/services/PUBLIC/DISTRICTS/MapServer/190` | OGCD district boundaries (WKID 4326) |
| Base of Treatable Water | `https://gis.occ.ok.gov/server/rest/services/PUBLIC/BASE_OF_TREATABLE_WATER/MapServer` | BTW depths used for casing/disposal design |
| Geology | `https://gis.occ.ok.gov/server/rest/services/PUBLIC/GEOLOGY/MapServer` | Surface geology layers |
| Hydrology | `https://gis.occ.ok.gov/server/rest/services/PUBLIC/HYDROLOGY/MapServer` | Surface water features |
| Public Water Supply | `https://gis.occ.ok.gov/server/rest/services/PUBLIC/PUBLIC_WATER_SUPPLY/MapServer` | PWS wells and service areas |

**Service enumeration:**
```bash
# List all public services
curl -s "https://gis.occ.ok.gov/server/rest/services/PUBLIC?f=json" | jq '.services'

# Get capabilities of a MapServer
curl -s "https://gis.occ.ok.gov/server/rest/services/PUBLIC/INDUCED_SEISMICITY/MapServer?f=json" \
  | jq '.layers[] | {id, name, geometryType}'
```

**Open Data Hub (human-friendly front end):**
- `https://gisdata-occokc.opendata.arcgis.com/` — downloadable shapefiles,
  GeoJSON, and CSVs for spills, pipelines, and some seismicity layers.
- `https://gis.occ.ok.gov/portal/apps/experiencebuilder/experience/?id=75bcb0b2c7f943dfa6cec75a50c9205a`
  — OGCD Experience Builder map app.

### Channel 2: Web Applications (Well Search, Imaged Documents)

| Tool | URL | Data |
|------|-----|------|
| OCC Well Data Finder | `https://oklahoma.gov/occ/divisions/oil-gas/database-search-imaged-documents/occ-well-data-finder.html` | Combined well search + imaged documents |
| OCC RBDMS Well Search | `https://oklahoma.gov/occ/divisions/oil-gas/database-search-imaged-documents/occ-rbdms-well-search.html` | Risk-Based Data Management System (RBDMS) well query |
| Aerial Photo Viewer | `https://oklahoma.gov/occ/divisions/oil-gas/database-search-imaged-documents/occ-aerial-photo-viewer.html` | Historical aerials |
| Database & Imaged Documents hub | `https://oklahoma.gov/occ/divisions/oil-gas/database-search-imaged-documents.html` | Landing page with all imaged documents |

These are form-based ASP.NET applications that return HTML. They are not
machine-parseable APIs; use them for single-well lookups or to confirm a
document exists. For bulk work, use Channel 3 or 4.

### Channel 3: RBDMS Data Explorer (Data Mining)

**URL:** `https://occ-de.rbdmsonline.org/DataMining.html`
**Help PDF:** `https://oklahoma.gov/content/dam/ok/en/occ/documents/og/data-explorer-help-file.pdf`

The RBDMS Data Explorer is the OCC's programmatic(ish) bulk data tool. It
lets users build ad-hoc queries against OCC's RBDMS tables and download
results as CSV/Excel. Tables include:

- `WELLS` — well header, API, operator, location, status
- `PRODUCTION_MONTHLY` — monthly oil/gas/water by API (where reported)
- `INJECTION_MONTHLY` — monthly Class II injection volumes by API
- `OPERATORS` — operator directory and bonding status
- `PERMITS` — drilling and UIC permits
- `MECHANICAL_INTEGRITY` — MIT test history for injection wells

The Data Explorer is a JavaScript web app; there is no documented REST API
endpoint. Automate by:
1. Manually building the query once in the UI
2. Saving the export URL/parameters
3. Re-running with `curl` against the export endpoint exposed by the form

Treat it as a bulk-download tool, not a live API.

### Channel 4: Salt Water Disposal Records by County

**URL:** `https://oklahoma.gov/occ/divisions/oil-gas/induced-seismicity-and-uic-department/salt-water-disposal-records-by-county.html`

The OCC's Induced Seismicity & UIC Department publishes per-county PDFs that
list every Class II SWD well, its permitted maximum volume, operator, API,
and historical injection volumes. File pattern:

```
https://oklahoma.gov/content/dam/ok/en/occ/documents/og/salth2o/{county}.pdf
```

Examples tested: `alfalfa.pdf`, `beaver.pdf`, `beckham.pdf`, `blaine.pdf`,
`bryan.pdf`, `caddo.pdf` — follow the same pattern for all 77 Oklahoma
counties (lowercase, hyphens for multi-word names).

These PDFs are the authoritative per-well disposal volume record. For
induced-seismicity analysis, they are typically cross-referenced with OGS
earthquake catalogs and OCC directive AOIs.

### Channel 5: Oklahoma Geological Survey (OGS)

**Landing page:** `https://www.ou.edu/ogs`
**Earthquake catalog:** `https://wichita.ogs.ou.edu/staff/earthquake/events.html`
**Well logs (OGS pilot):** `http://web-pilot.ogs.ou.edu/wells/`
**Recent earthquakes:** `https://www.ou.edu/ogs/research/earthquakes/recentearthquakes.html`

OGS maintains the authoritative Oklahoma earthquake catalog used by
researchers. For programmatic earthquake access, the **usgs-earthquakes**
skill is preferred (USGS ComCat covers Oklahoma events and is pure REST).
OGS is the reference for Oklahoma-specific event metadata and locally
relocated hypocenters.

---

## Query Patterns

### Enumerate Induced Seismicity Layers

```bash
curl -s "https://gis.occ.ok.gov/server/rest/services/PUBLIC/INDUCED_SEISMICITY/MapServer?f=json" \
  | jq '.layers[] | {id, name, type, geometryType}' | head -40
```

### Query OCC Districts (Polygon)

```bash
# Pull all OGCD district polygons as GeoJSON
curl -s "https://gis.occ.ok.gov/server/rest/services/PUBLIC/DISTRICTS/MapServer/190/query" \
  --data-urlencode "where=1=1" \
  --data-urlencode "outFields=*" \
  --data-urlencode "f=geojson"
```

### Query a Seismicity Directive AOI

```bash
# List all layers in the DIRECTIVE_AOIs service, then query a specific one
curl -s "https://gis.occ.ok.gov/server/rest/services/PUBLIC/DIRECTIVE_AOIs/MapServer?f=json" \
  | jq '.layers[] | select(.type=="Feature Layer") | {id, name}'

# Example: query layer 2 (AOI_20150318 regional directive polygon)
curl -s "https://gis.occ.ok.gov/server/rest/services/PUBLIC/DIRECTIVE_AOIs/MapServer/2/query" \
  --data-urlencode "where=1=1" \
  --data-urlencode "outFields=*" \
  --data-urlencode "returnGeometry=true" \
  --data-urlencode "f=geojson"
```

### Download a County SWD PDF

```bash
COUNTY=garfield
curl -sLO "https://oklahoma.gov/content/dam/ok/en/occ/documents/og/salth2o/${COUNTY}.pdf"
# Parse with pdftotext for plain-text tables:
pdftotext -layout "${COUNTY}.pdf" - | head -80
```

### Cross-reference with USGS Earthquakes

```bash
# Use the usgs-earthquakes skill for programmatic event retrieval.
# Example (direct ComCat call, bounding box covers Oklahoma):
curl -s "https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&starttime=2011-01-01&endtime=2017-12-31&minmagnitude=3.0&minlatitude=33.6&maxlatitude=37.0&minlongitude=-103.0&maxlongitude=-94.4" \
  | jq '.features | length'
# Then spatially join against OCC directive AOIs from Channel 1.
```

---

## Workflow

### Step 1 — Resolve Intent

| User wants... | Best channel |
|--------------|-------------|
| Induced-seismicity directive polygons | GIS `PUBLIC/INDUCED_SEISMICITY` or `PUBLIC/DIRECTIVE_AOIs` |
| Class II SWD volumes by county | Per-county PDF in `salth2o/` |
| Per-well monthly injection history | RBDMS Data Explorer (export) |
| Well header / API lookup | OCC Well Data Finder (web) |
| Mechanical integrity tests | RBDMS Data Explorer, table `MECHANICAL_INTEGRITY` |
| District boundaries | GIS `PUBLIC/DISTRICTS` layer 190 |
| Base of treatable water | GIS `PUBLIC/BASE_OF_TREATABLE_WATER` |
| Production by operator/county | RBDMS Data Explorer (export) |
| Oklahoma earthquake catalog | **usgs-earthquakes** skill (primary), OGS (secondary) |
| Shapefiles / bulk GIS | OCC Open Data Hub (`gisdata-occokc.opendata.arcgis.com`) |

### Step 2 — Fetch Data

- GIS services: standard ArcGIS REST `query` endpoints with `f=json` or
  `f=geojson`. Use `where=1=1` for full-layer pulls; add
  `resultRecordCount` and `resultOffset` for paging past the 2,000-row
  default cap.
- County PDFs: direct GET to the `salth2o/{county}.pdf` URL.
- RBDMS Data Explorer: build query in UI, capture export URL, then re-run
  with `curl`.
- Web apps: avoid at scale; use for single-well confirmation only.

### Step 3 — Parse Response

| Source | Parse strategy |
|--------|----------------|
| GIS `f=json` | `jq '.features[].attributes'` |
| GIS `f=geojson` | any GeoJSON library |
| County SWD PDF | `pdftotext -layout` → regex rows |
| RBDMS CSV export | standard CSV library |
| Web app HTML | HTML scraping (last resort) |

### Step 4 — Produce Output

**Format: Markdown Table + Narrative Summary**

```
## Oklahoma Class II SWD — Garfield County (Arbuckle Disposal)

| API        | Operator            | Zone     | Permit BBL/mo | 2016 BBL  | 2023 BBL  |
|------------|---------------------|----------|---------------|-----------|-----------|
| 35-047-... | Operator A          | Arbuckle | 60,000        | 720,000   | 360,000   |
| 35-047-... | Operator B          | Arbuckle | 45,000        | 540,000   | 180,000   |

**Summary:** Garfield County sits at the northern edge of OCC's 2015
regional seismicity directive AOI. Combined Arbuckle disposal volumes
dropped ~50% from 2016 to 2023 following OCC Directive-2 volume
reductions, consistent with the statewide M3+ event rate decline from
~900/yr in 2015 to ~50/yr in 2023. Source: OCC salth2o PDF + usgs-earthquakes
skill. Volumes are operator-reported and may lag 60-90 days.
```

---

## Oklahoma Geographic and Play Reference

### Major Basins and Plays

| Basin / Play | Counties | Key Formations | Relevance |
|--------------|----------|----------------|-----------|
| Anadarko Basin | Grady, Canadian, Caddo, Blaine, Custer, Dewey | Woodford, Hunton, Springer, Cana, Tonkawa | Deep gas; Hunton dewatering; major SWD region |
| SCOOP | Grady, Stephens, Garvin, Carter | Woodford, Springer, Sycamore | High water-cut horizontal play |
| STACK | Kingfisher, Blaine, Canadian, Major | Meramec, Osage, Woodford | Mississippian-Woodford stack; high produced water |
| Arkoma Basin | Pittsburg, Hughes, Latimer, LeFlore, Coal | Woodford, Caney, Atoka | Gas-dominated; less SWD |
| Mississippi Lime / "Miss Lime" | Alfalfa, Grant, Woods, Kay, Garfield, Noble | Mississippian limestone | Extremely high water-oil ratios (10-30:1); driver of 2010-2015 Arbuckle disposal surge |
| Hugoton / Panhandle | Texas, Beaver, Cimarron | Chase, Council Grove | Mature gas |

### OCC Districts

Five OGCD districts (boundaries in GIS `PUBLIC/DISTRICTS/190`):
1. Northwest, 2. Northeast, 3. Central, 4. Southwest, 5. Southeast.
Districts govern inspection, permitting workflow, and directive scope.

### Formations Critical for Li/Mg and Disposal Research

- **Arbuckle Group (Cambrian-Ordovician carbonate):** Primary Class II
  disposal reservoir statewide. Highly porous, regionally extensive, sits
  directly on Precambrian basement — the hydraulic connection that
  triggered the 2011-2016 induced-seismicity sequence. See
  `references/arbuckle_disposal.md`.
- **Hunton Group (Silurian-Devonian carbonate):** Dewatering plays in
  central Oklahoma produce massive water volumes (100+ BBL water per BBL
  oil in some fields). Water chemistry is understudied for Li but has
  TDS 100k-200k mg/L and elevated Br, Ca, Mg — candidate for DLE + Mg
  co-recovery.
- **Mississippian limestone ("Miss Lime"):** 2010-2014 horizontal boom in
  northern OK drove disposal volumes 3-5x; became the epicenter of
  wastewater-induced seismicity. Produced waters are high-TDS brines with
  moderate Li (sparse data, 10-80 mg/L range).
- **Woodford Shale:** Primary source rock; produced waters from
  Woodford-targeted wells in SCOOP/STACK have volumes and chemistry
  intermediate between shale and carbonate-brine end members.

---

## Error Handling

| Condition | Meaning | Action |
|-----------|---------|--------|
| `499 Token Required` from UIC/ISD folders | Folder is not public | Use `PUBLIC` folder layers or county PDFs instead |
| ArcGIS `exceededTransferLimit: true` | >2,000-row page | Add `resultOffset` paging; or add spatial/where filter |
| County PDF 404 | Wrong county slug | Use lowercase, hyphenate multi-word (e.g. `le-flore.pdf` — verify via the SWD records index page) |
| RBDMS Data Explorer timeout | Query too broad | Add date range or county filter; export in chunks |
| Web app CAPTCHA / session drop | Bot detection | Slow requests; prefer GIS services and county PDFs |
| 404 on `oklahoma.gov/occ/documents-data/oil-gas.html` | Portal path changed | Start from `https://oklahoma.gov/occ/divisions/oil-gas.html` — OCC has reorganized twice since 2020 |
| OGS catalog link broken | OGS site churn | Fall back to **usgs-earthquakes** skill (USGS ComCat is stable) |

---

## Cross-Skill References

- **usgs-earthquakes** — primary source for Oklahoma earthquake events.
  Use OCC AOIs to define the polygon, then query ComCat for magnitude and
  hypocenter data. OGS is an editorial reference, not a REST source.
- **usgs-produced-waters** — geochemistry for Hunton, Arbuckle, and
  Mississippian samples. Cross-reference OCC disposal volumes with USGS
  sample chemistry.
- **fracfocus** — completion fluid disclosures for SCOOP/STACK wells.
- **epa-regulatory** — UIC federal overlay; Oklahoma is a Class II primacy
  state but EPA data provides national consistency checks.

---

## Caveats and Data Limitations

1. **Portal churn.** OCC has reorganized its data portal multiple times
   since 2020. URLs under `oklahoma.gov/occ/divisions/oil-gas/...` are
   valid as of the date in `CLAUDE.md`'s `currentDate` — if a link 404s,
   start at `https://oklahoma.gov/occ/divisions/oil-gas.html` and navigate
   from the division landing page.
2. **No documented REST API for well/production data.** The RBDMS Data
   Explorer is the closest thing to a bulk interface but is UI-driven.
   Shapefile/GeoJSON exports are cleaner than web-scraped HTML.
3. **UIC and ISD ArcGIS folders are locked.** Only the `PUBLIC` folder
   responds without a token. The `UIC` folder that would contain
   per-well injection layers returns `499`. Use the county SWD PDFs as
   the authoritative public source for per-well volumes.
4. **PDF-encoded SWD data.** The per-county SWD records are PDFs, not
   machine-readable tables. `pdftotext -layout` works for most counties
   but column alignment is inconsistent across years.
5. **Data lag.** Monthly injection data through RBDMS typically lags
   60-90 days. Operator reporting completeness varies; historical data
   pre-2010 is sparse for smaller operators.
6. **Induced-seismicity attribution is not causal proof.** OCC directive
   AOIs are regulatory boundaries, not physical fault models. For causal
   analyses, use the OGS relocated catalog alongside OCC volumes and
   published pore-pressure modeling (Keranen et al. 2014;
   Langenbruch & Zoback 2016).
7. **OGS earthquake catalog is editorial.** Prefer USGS ComCat (via
   **usgs-earthquakes**) for reproducible queries. Cite OGS for
   Oklahoma-specific relocations and network metadata.
8. **County name slugs.** Most PDFs follow `{lowercase-county}.pdf`.
   Multi-word counties may use hyphens or concatenation — verify from
   the SWD records index page rather than guessing.
