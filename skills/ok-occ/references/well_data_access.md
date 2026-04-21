# OCC Well, Production, and Disposal Data Access

Cookbook for pulling Oklahoma well-level and aggregated data by county.
Assumes no credentials (all sources are public).

---

## 1. Find Wells and Operators

### Web: OCC Well Data Finder (single-well lookup)

**URL:** `https://oklahoma.gov/occ/divisions/oil-gas/database-search-imaged-documents/occ-well-data-finder.html`

Use this to confirm an API number or pull imaged permit/completion
documents for a specific well. Inputs: API 10-digit, operator name, or
township/range/section. Output is HTML — not a programmatic source.

Oklahoma API format: `35-{county}-{unique}` with county code 001-153
(odd numbers only; Oklahoma counties use odd codes). Example:
`35-047-12345` is a Garfield County (county code 047) well.

### Web: RBDMS Well Search

**URL:** `https://oklahoma.gov/occ/divisions/oil-gas/database-search-imaged-documents/occ-rbdms-well-search.html`

Searches the OCC's RBDMS (Risk-Based Data Management System) well table.
Same fields as the Well Data Finder with additional status and spud-date
filters.

### Bulk: RBDMS Data Explorer

**URL:** `https://occ-de.rbdmsonline.org/DataMining.html`

JavaScript SPA. Manual workflow:

1. Open the Data Explorer.
2. Select table (WELLS, PRODUCTION_MONTHLY, INJECTION_MONTHLY, OPERATORS,
   PERMITS, MECHANICAL_INTEGRITY, etc.).
3. Add filters (county, date range, operator, well type).
4. Run query; download as CSV or Excel.
5. Capture the POST payload via browser devtools if you need to automate.

The help file at
`https://oklahoma.gov/content/dam/ok/en/occ/documents/og/data-explorer-help-file.pdf`
documents the available tables and typical queries.

---

## 2. Production Data

Oklahoma production is **tax-assessed by the Oklahoma Tax Commission**
(OTC), not the OCC. OCC collects permits, completions, and injection.
This is a common source of confusion:

- **Monthly oil/gas production** by lease/well → OTC monthly reports
  (paid data from vendors like Drillinginfo/Enverus, or OTC FOIA).
- **Historical aggregate production** by field/county → OCC RBDMS
  (less granular but free).
- **Injection volumes by API** → OCC RBDMS or per-county SWD PDFs.

For free research-scale production data, the cleanest path is:

1. EIA state-level monthly oil/gas (via the `eia-data` skill).
2. OCC RBDMS field-level aggregates.
3. USGS/state publications for historical field totals.

---

## 3. Class II Saltwater Disposal (SWD) by County

This is the most important dataset for induced-seismicity and disposal
economics work.

**Index page:** `https://oklahoma.gov/occ/divisions/oil-gas/induced-seismicity-and-uic-department/salt-water-disposal-records-by-county.html`

**Per-county PDF pattern:**
```
https://oklahoma.gov/content/dam/ok/en/occ/documents/og/salth2o/{county}.pdf
```

**Verified examples (2025-04):** alfalfa, beaver, beckham, blaine, bryan,
caddo. For all other counties, start from the index page.

### What's in each PDF

Per SWD well:
- API 10-digit
- Operator name
- Well name / number
- Legal description (Sec-Twp-Rng)
- Injection zone / formation
- Permitted maximum BBL/day or BBL/month
- Annual injection volume (typically most recent 5-10 years)
- Permit number and status
- Mechanical integrity test (MIT) dates

### Automation

```bash
# Batch-download all 77 county PDFs
COUNTIES=(adair alfalfa atoka beaver beckham blaine bryan caddo canadian carter \
          cherokee choctaw cimarron cleveland coal comanche cotton craig creek \
          custer delaware dewey ellis garfield garvin grady grant greer harmon \
          harper haskell hughes jackson jefferson johnston kay kingfisher kiowa \
          latimer leflore lincoln logan love major marshall mayes mcclain \
          mccurtain mcintosh murray muskogee noble nowata okfuskee oklahoma \
          okmulgee osage ottawa pawnee payne pittsburg pontotoc pottawatomie \
          pushmataha rogermills rogers seminole sequoyah stephens texas tillman \
          tulsa wagoner washington washita woods woodward)

mkdir -p ok_swd_pdfs
for c in "${COUNTIES[@]}"; do
  curl -sfLo "ok_swd_pdfs/${c}.pdf" \
    "https://oklahoma.gov/content/dam/ok/en/occ/documents/og/salth2o/${c}.pdf" \
    && echo "ok  $c" || echo "miss $c  # verify slug on index page"
done
```

Convert to text:
```bash
for f in ok_swd_pdfs/*.pdf; do
  pdftotext -layout "$f" "${f%.pdf}.txt"
done
```

Parse typical row (regex): the PDFs are fixed-width when extracted with
`-layout`; column positions shift slightly year-to-year. Treat the PDFs
as semi-structured and validate parsers against a sample before running
statewide.

---

## 4. Spatial Data via OCC GIS

**Server root:** `https://gis.occ.ok.gov/server/rest/services`
**Public folder:** `https://gis.occ.ok.gov/server/rest/services/PUBLIC`
**Open Data Hub:** `https://gisdata-occokc.opendata.arcgis.com/`

### Districts polygon

```bash
curl -s "https://gis.occ.ok.gov/server/rest/services/PUBLIC/DISTRICTS/MapServer/190/query" \
  --data-urlencode "where=1=1" \
  --data-urlencode "outFields=*" \
  --data-urlencode "f=geojson" \
  -o ok_districts.geojson
```

### Induced seismicity AOI (all layers)

```bash
# Enumerate
curl -s "https://gis.occ.ok.gov/server/rest/services/PUBLIC/INDUCED_SEISMICITY/MapServer?f=json" \
  | jq '.layers[] | select(.type=="Feature Layer") | {id, name}'

# Pull a specific AOI layer as GeoJSON (example: layer 320 = AOI_20150318)
curl -s "https://gis.occ.ok.gov/server/rest/services/PUBLIC/INDUCED_SEISMICITY/MapServer/320/query" \
  --data-urlencode "where=1=1" \
  --data-urlencode "outFields=*" \
  --data-urlencode "returnGeometry=true" \
  --data-urlencode "f=geojson"
```

### Base of Treatable Water

```bash
curl -s "https://gis.occ.ok.gov/server/rest/services/PUBLIC/BASE_OF_TREATABLE_WATER/MapServer?f=json" \
  | jq '.layers[] | {id, name}'
```

### Paging past the 2,000-row limit

All MapServer layers cap results at 2,000 features per request. Page with
`resultOffset`:

```bash
OFFSET=0
while true; do
  curl -s "$LAYER_URL/query" \
    --data-urlencode "where=1=1" \
    --data-urlencode "outFields=*" \
    --data-urlencode "resultOffset=$OFFSET" \
    --data-urlencode "resultRecordCount=2000" \
    --data-urlencode "f=json" > "page_${OFFSET}.json"
  COUNT=$(jq '.features | length' "page_${OFFSET}.json")
  [ "$COUNT" -lt 2000 ] && break
  OFFSET=$((OFFSET + 2000))
done
```

---

## 5. Earthquake Cross-Reference

**Primary:** use the `usgs-earthquakes` skill (USGS ComCat FDSN-event
service). Oklahoma bounding box:

- minlat=33.6 maxlat=37.0 minlon=-103.0 maxlon=-94.4

**Example — M≥3 events within the 2015 regional AOI, 2015-2017:**

```bash
# 1. Pull the AOI polygon from OCC
curl -s "https://gis.occ.ok.gov/server/rest/services/PUBLIC/DIRECTIVE_AOIs/MapServer/2/query" \
  --data-urlencode "where=1=1" \
  --data-urlencode "outFields=*" \
  --data-urlencode "returnGeometry=true" \
  --data-urlencode "f=geojson" > aoi_2015.geojson

# 2. Pull statewide OK events from USGS (or use usgs-earthquakes skill)
curl -s "https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&starttime=2015-01-01&endtime=2017-12-31&minmagnitude=3.0&minlatitude=33.6&maxlatitude=37.0&minlongitude=-103.0&maxlongitude=-94.4" \
  > ok_eqs_2015_2017.geojson

# 3. Spatial join (GeoPandas or similar) to count events inside the AOI.
```

**Secondary:** OGS catalog at
`https://wichita.ogs.ou.edu/staff/earthquake/events.html` — static HTML
tables; use for relocated hypocenters, not bulk queries.

---

## 6. Typical Workflow for a Project Screening

1. Identify target county/counties and formation.
2. Pull the county SWD PDF(s) → parse per-well Arbuckle volumes.
3. Pull OCC directive AOIs as GeoJSON → check whether target is inside
   any AOI.
4. Pull 10-year earthquake catalog (M≥2.5) via `usgs-earthquakes` →
   count events within 5 mi of candidate disposal wells.
5. Pull `usgs-produced-waters` chemistry filtered on target formation in
   target counties → Li/Mg/TDS summary.
6. Compare Arbuckle BTW depth (`PUBLIC/BASE_OF_TREATABLE_WATER`) with
   target disposal depth.
7. Output: markdown table (per-well volumes, AOI overlay, nearby M3+
   count, produced-water chemistry) + narrative.

---

## 7. What OCC Does *Not* Publish Easily

- Well-level production without OTC/vendor data.
- Real-time injection pressure telemetry (collected for monitoring wells
  but not on the public web).
- Detailed fault maps (use OGS separately).
- Economic/bonding data per operator beyond the RBDMS Operators table.
- Pipeline flow data (separate PIPELINE GIS folder, partially public).

When a field is not on the OCC site, check:
- **OGS** for geology and faults
- **EIA** for state aggregates
- **FracFocus** for completion fluid chemistry
- **USGS** for produced water chemistry and earthquakes
- **EPA UIC** for federal cross-reference
