# Arbuckle Group Disposal and Induced Seismicity

The Arbuckle Group is the single most important injection reservoir in
Oklahoma and the central case study in U.S. induced seismicity. Any Li/Mg
recovery project that generates produced water in Oklahoma must address
Arbuckle disposal capacity and the regulatory overlay that governs it.

---

## Geology

- **Age / lithology:** Cambrian-Ordovician carbonate sequence (dolomite with
  subordinate limestone and sandstone interbeds). Regionally extensive
  across Oklahoma and into Kansas.
- **Depth:** Typically 3,000-9,000 ft below ground surface, depending on
  basin position. Deepest in the Anadarko Basin, shallower on the
  northern shelf.
- **Porosity / permeability:** Highly variable. Karst-affected intervals
  have very high injectivity; tight dolomite intervals are not used for
  disposal. Typical bulk porosity 5-15%, permeability 10-1,000 mD in
  karst-enhanced zones.
- **Structural setting:** Directly overlies Precambrian crystalline
  basement across most of Oklahoma. The **direct hydraulic contact
  between Arbuckle porosity and basement faults** is the physical
  mechanism for induced seismicity — injected fluids raise pore pressure
  on pre-stressed basement faults.

## Disposal Role

- **~90% of Oklahoma Class II saltwater disposal (SWD) volume** goes into
  the Arbuckle, based on OCC-reported volumes 2014-2023.
- Used because:
  1. Massive storage capacity (thick, porous, regionally extensive)
  2. Below the base of treatable water
  3. Isolated from commercial oil/gas pay zones
  4. Low injection pressures (often gravity feed or low pump head)
- **Injection volume peaked in 2014-2015** at ~1.6 billion BBL/yr
  statewide. Drivers: Mississippi Lime horizontal boom (2010-2014) and
  SCOOP/STACK ramp (2013-2016), both with high water-oil ratios.
- **2016-2023 decline** to ~700-900 million BBL/yr following OCC
  directive-driven volume reductions and the oil-price-driven slowdown
  in Miss Lime drilling.

## Induced Seismicity Timeline

| Year | M3+ events (statewide) | Key regulatory / scientific event |
|------|------------------------|-----------------------------------|
| 2008 | ~2 | Background rate; pre-boom baseline |
| 2009 | ~20 | Miss Lime drilling begins |
| 2011 | ~70 | **Prague M5.7** (Nov 6) — largest U.S. induced event at the time; Keranen et al. link to Wilzetta SWD wells |
| 2013 | ~110 | Arbuckle injection rising; OCC begins "traffic light" approach |
| 2014 | ~580 | Peak Arbuckle injection (~1.6 Bbbl/yr) |
| 2015 | ~890 | Peak M3+ rate; OCC issues first regional directives (March, June, July) |
| 2016 | ~620 | **Pawnee M5.8** (Sep 3) — largest recorded OK event; OCC mandates volume cuts across 700+ wells |
| 2017 | ~300 | Directive volume reductions biting; Miss Lime activity collapsed |
| 2018 | ~200 | Continued decline |
| 2020 | ~70 | COVID oil-price crash further reduces disposal |
| 2023 | ~50-70 | Stabilized; sporadic M3+ clusters near remaining high-volume wells |

Event counts are approximate and drawn from USGS ComCat + OGS relocated
catalog; use **usgs-earthquakes** skill for precise queries.

## Key OCC Directives

All AOIs are available as polygon layers under
`https://gis.occ.ok.gov/server/rest/services/PUBLIC/DIRECTIVE_AOIs/MapServer`
and `PUBLIC/INDUCED_SEISMICITY/MapServer`.

| Directive | Date | Scope | Action |
|-----------|------|-------|--------|
| Regional AOI #1 | 2015-03-18 | ~6,000 mi² NW/central OK | Operators required to prove well depth below Arbuckle or reduce volume |
| Regional AOI #2 | 2015-06-24 | Expanded AOI | Volume reductions phased in |
| Regional AOI #3 | 2015-07-02 | Further expansion | Plug-back requirements |
| 2016 Area of Interest | 2016-03-07 | ~10,000 mi² | 40% volume reduction across 245 wells |
| Central AOI expansion | 2016-03-25 | +5,281 mi² | Additional 245 wells to 40% reduction |
| Pawnee response | 2016-09-03 | 725 mi² around M5.8 | 37 wells shut in |
| Ongoing "Directive Traffic Light" | 2016-present | Statewide | Yellow (review) / red (shut-in) thresholds tied to M-rate per AOI |

## Key Peer-Reviewed References

- **Ellsworth (2013)** — "Injection-Induced Earthquakes," *Science*
  341:1225942. Framework paper linking deep injection to fault
  reactivation.
- **Keranen, Savage, Abers, Cochran (2013)** — "Potentially induced
  earthquakes in Oklahoma, USA: Links between wastewater injection and
  the 2011 Mw 5.7 earthquake sequence," *Geology* 41(6):699-702.
- **Keranen, Weingarten, Abers, Bekins, Ge (2014)** — "Sharp increase in
  central Oklahoma seismicity since 2008 induced by massive wastewater
  injection," *Science* 345:448-451. Foundational paper on statewide link.
- **Langenbruch & Zoback (2016)** — "How will induced seismicity in
  Oklahoma respond to decreased saltwater injection rates?" *Science
  Advances* 2(11):e1601542. Predictive pore-pressure model.
- **Walsh & Zoback (2015)** — "Oklahoma's recent earthquakes and
  saltwater disposal," *Science Advances* 1(5):e1500195.

## Implications for Li/Mg Recovery Projects

1. **Disposal cost and capacity are not guaranteed.** In AOI polygons,
   new or increased Arbuckle volumes require OCC review and may be
   denied. Model projects in AOI-free counties first.
2. **Volume-linked tariffs.** Commercial SWD tariffs in AOI zones have
   risen (typical range $0.50-$2.50/BBL 2023; higher in constrained
   zones) — affects DLE economics when brine is disposed after Li
   extraction.
3. **Residual stream chemistry matters.** Post-DLE brine that has been
   concentrated or acidified may be rejected by commercial SWD operators
   or require pre-treatment. OCC permits specify injection fluid limits.
4. **Mechanical integrity and monitoring.** Seismic monitoring clauses
   are standard in post-2016 permits. A DLE facility feeding an SWD
   should budget for real-time pressure and seismic telemetry.
5. **Alternative zones.** Some operators have shifted to shallower
   injection zones (e.g. Chester, Hunton) or to deeper granite-wash
   zones to avoid Arbuckle-basement hydraulic connection. These have
   smaller capacity and higher injectivity variability.

## Data to Pull for an Arbuckle Screening

1. **County SWD volumes** — `salth2o/{county}.pdf` for your target
   counties.
2. **AOI polygons** — `PUBLIC/DIRECTIVE_AOIs/MapServer` as GeoJSON.
3. **Historic earthquakes** — `usgs-earthquakes` skill, bounding box +
   M≥2.5, 2009-present.
4. **Base of treatable water** — `PUBLIC/BASE_OF_TREATABLE_WATER` for
   casing design constraints.
5. **Produced water chemistry** — `usgs-produced-waters` skill filtered
   on `FORMATION LIKE 'ARBUCKLE'` or `'HUNTON'` or `'MISSISSIPPIAN'`.
