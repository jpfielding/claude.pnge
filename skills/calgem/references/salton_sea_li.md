# Salton Sea KGRA — Geothermal Lithium Reference

The Salton Sea Known Geothermal Resource Area (KGRA) in Imperial County, CA
is the single largest known geothermal brine lithium resource in the United
States. The brine is extracted at ~300 degC from the reservoir, flashed for
power generation, and historically reinjected. Direct lithium extraction (DLE)
projects now aim to recover Li (and potentially Mn, Zn, Cs, Rb) from the spent
brine stream before reinjection — in principle producing lithium with zero
additional water withdrawal and negligible incremental surface footprint.

## Geographic Extent

- **KGRA designation:** Bureau of Land Management Salton Sea KGRA, first
  designated 1974, ~100,000 acres along the southeastern shore of the
  Salton Sea.
- **Active geothermal field:** The producing zone is a narrow belt centered
  near Calipatria and Niland, Imperial County.
- **Bounding box (approximate, for ArcGIS queries):**
  `-115.9, 33.05, -115.4, 33.55` (lon/lat, WGS84)
- **CalGEM district:** D6 (Geothermal).

## Project Operators (2025-2026 status)

| Operator | Project | Stage | Target | Notes |
|----------|---------|-------|--------|-------|
| **Controlled Thermal Resources (CTR)** | Hell's Kitchen | Under construction (Stage 1 permitting + well drilling) | Integrated geothermal power + Li | Stellantis, GM, LG offtake agreements. First Li delivery target ~2027. |
| **EnergySource Minerals** | ATLiS | DLE demonstration completed; commercial build-out underway adjacent to Featherstone geothermal plant | Li from existing brine stream | Ford and LG commercial offtakes |
| **BHE Renewables (Berkshire Hathaway Energy)** | Legacy operator of 10 existing geothermal plants; adding Li extraction | Commercial pilot | Li from existing brine | Joint development with various partners; has the largest footprint of existing wellhead-to-powerplant infrastructure |
| **Lilac Solutions** (via partnerships) | DLE technology vendor | Tech licensing | Li ion-exchange | Not a field operator but the dominant DLE tech on the resource |

## Brine Chemistry Snapshot

Source: USGS Professional Paper 1832 (McKibben & Hardie, 1997, updated 2020);
DOE Salton Sea Resource Assessment (2023); peer-reviewed updates through 2024.

| Parameter | Typical Range | Notes |
|-----------|---------------|-------|
| Temperature (wellhead) | 250-325 degC | Already hot enough for DLE without auxiliary heating |
| pH (in-situ) | 4.5-5.5 | Acidic; requires materials selection for DLE contactors |
| TDS | 200,000-300,000 mg/L | Hypersaline; roughly 10x seawater |
| Lithium (Li) | 150-400 mg/L | Central estimate ~220 mg/L for current production wells |
| Magnesium (Mg) | 50-500 mg/L | Relatively low — a key advantage vs South American salars (Li:Mg ratio favorable) |
| Calcium (Ca) | 20,000-40,000 mg/L | Very high; drives scaling in surface plant |
| Sodium (Na) | 50,000-70,000 mg/L | Main counterion |
| Potassium (K) | 15,000-20,000 mg/L | Recoverable co-product |
| Chloride (Cl) | 150,000-180,000 mg/L | Dominant anion |
| Iron (Fe) | 1,000-2,500 mg/L | Very high — causes scaling; silica co-scale |
| Manganese (Mn) | 800-2,000 mg/L | Potential co-product battery cathode feed |
| Zinc (Zn) | 300-700 mg/L | Co-product target |
| Barium (Ba) | 100-300 mg/L | Drives sulfate scaling |
| Silica (SiO2) | 400-700 mg/L | Major scaling issue at surface |

## Li:Mg Ratio — Why Salton Sea Wins vs Other Brines

Mass ratio Li:Mg is the single most important figure of merit for DLE
economics because Mg removal by precipitation is the dominant cost step in
conventional Li carbonate production.

| Brine | Typical Li:Mg (mass) | Interpretation |
|-------|----------------------|----------------|
| Salar de Atacama (Chile) | 1:6 | Mg removal is the main cost |
| Salar de Uyuni (Bolivia) | 1:20 | Mg removal prohibitive — undeveloped |
| **Salton Sea (CA)** | **1:0.5 to 1:1.5** | Mg removal trivial — a structural advantage |
| Smackover (AR) | 1:15 to 1:30 | Mg removal significant; high Ca also |
| Marcellus flowback | 1:5 to 1:20 | Mg removal significant |

Additionally, Salton Sea brine arrives **at temperature**. Every other major
Li brine resource must be evaporated (salars) or heated (oilfield brines).
This is a structural energy-cost advantage.

## Resource Assessments

- **USGS (2023):** Salton Sea Geothermal Lithium Resources — Preliminary
  Assessment. Report estimates ~4.1 million metric tons Li (recoverable,
  P50) across the KGRA. See https://pubs.usgs.gov/ for the current fact
  sheet citation.
- **DOE (November 2023):** Lawrence Berkeley National Laboratory,
  "Salton Sea Lithium Resource Assessment." Central estimate 18 Mt Li
  (resource), 3.4 Mt (recoverable) from the current production zone under
  techno-economic assumptions. Higher than USGS because LBNL counts the
  deeper (currently unproduced) zones.
- **CEC (2020):** California Energy Commission, "Selective Recovery of
  Critical Materials from Geothermal Brines." Feasibility level.

Use the `pnge:pnge-literature` skill (USGS Pubs + OSTI adapters) to pull the
current versions with full author/DOI metadata.

## Sample Queries

```bash
# Active geothermal wells in Imperial County (Salton Sea KGRA)
curl -s "https://gis.conservation.ca.gov/server/rest/services/WellSTAR/Wells/MapServer/1/query" \
  --data-urlencode "where=CountyName='Imperial' AND WellStatus='Active'" \
  --data-urlencode "outFields=APINumber,LeaseName,WellNumber,OperatorName,FieldName,WellType,SpudDate" \
  --data-urlencode "orderByFields=SpudDate DESC" \
  --data-urlencode "returnGeometry=false" \
  --data-urlencode "resultRecordCount=100" \
  --data-urlencode "f=json"

# Spatial bounding box around the producing zone
curl -s "https://gis.conservation.ca.gov/server/rest/services/WellSTAR/Wells/MapServer/1/query" \
  --data-urlencode "geometry=-115.75,33.10,-115.45,33.45" \
  --data-urlencode "geometryType=esriGeometryEnvelope" \
  --data-urlencode "inSR=4326" \
  --data-urlencode "spatialRel=esriSpatialRelIntersects" \
  --data-urlencode "outFields=APINumber,OperatorName,FieldName,WellStatus,WellType,Lat83,Long83" \
  --data-urlencode "returnGeometry=false" \
  --data-urlencode "f=json"
```

## Caveats

1. **Resource estimates vary by a factor of ~5x** across USGS (conservative),
   DOE/LBNL (mid), and operator-funded assessments (aggressive). Report
   central tendency plus bounds, never a single headline number.
2. **Recovery assumptions matter more than the resource estimate.** DLE
   recovery efficiency at commercial scale is not yet demonstrated at
   target throughput. Pilots have reported 60-95% Li recovery on the bench
   but no commercial plant has run for >18 months continuously as of early
   2026.
3. **Silica and iron scaling are the core engineering risks.** Every
   published DLE pilot has some variant of silica-seeding or acid-injection
   strategy; none has been fully de-risked at scale.
4. **Water accounting:** Salton Sea brine is reinjected 1:1 — this is not a
   consumptive water use. Contrast with salars (fully consumptive
   evaporation) and oilfield brines (typically disposal injection, not
   return to source formation).
5. **Salton Sea itself is a terminal lake in decline.** Geothermal
   operations are hydrologically separate from the lake water body, but the
   surrounding environmental-justice and dust-emission context is politically
   load-bearing for permitting.
