---
name: wri-aqueduct
description: >
  Query World Resources Institute Aqueduct water risk data for U.S. counties,
  states, and global watershed basins. Provides baseline water stress,
  interannual variability, seasonal variability, drought risk, riverine flood
  risk, and groundwater table decline for any location. Use this skill when the
  user asks about water stress levels in an oil and gas producing region,
  drought risk for produced water management, water availability for hydraulic
  fracturing operations, water risk for a county or basin, WRI Aqueduct scores,
  or environmental water risk context for energy operations. Trigger for phrases
  like "water stress in Monongalia County", "water risk for Permian Basin",
  "drought risk West Virginia", "WRI Aqueduct score", "water availability for
  fracking in Texas", "water stress index", "baseline water stress", "water
  scarcity risk", or "water risk for oil and gas operations". Produces risk
  score tables by location with narrative interpretation.
---

# WRI Aqueduct Water Risk Skill

Queries the World Resources Institute (WRI) Aqueduct 4.0 water risk dataset
via ArcGIS REST FeatureServer. Returns water stress, drought, flood, and
groundwater risk indicators for any country, state/province, or watershed.

**No API key required.** WRI Aqueduct data is publicly accessible through
ArcGIS REST services.

---

## API Structure

**Base URL:**
```
https://services.arcgis.com/LG9Yn2oFqZi5PnO5/arcgis/rest/services/
```

**Primary Service — Aqueduct 4.0 Annual:**
```
https://services.arcgis.com/LG9Yn2oFqZi5PnO5/arcgis/rest/services/Aqueduct_Annual/FeatureServer/0/query
```

This is an ArcGIS FeatureServer endpoint. Use POST requests with
form-encoded parameters for queries with complex WHERE clauses containing
apostrophes.

### Query Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `where` | SQL WHERE clause using field names | `country_un='United States of America' AND name_1='West Virginia'` |
| `outFields` | Comma-separated field names to return | `name_0,name_1,bws_cat,bws_label` |
| `f` | Response format | `json` |
| `resultRecordCount` | Max features to return (server max: 1000) | `200` |
| `returnGeometry` | Include geometry in response | `false` (set false for data-only queries) |
| `orderByFields` | Sort field | `bws_cat DESC` |
| `resultOffset` | Pagination offset | `0`, `200`, `400` |

---

## Key Field Names — Aqueduct 4.0

### Location Fields

| Field | Description | Example Values |
|-------|-------------|----------------|
| `name_0` | Country name | United States of America |
| `name_1` | Province/state name | West Virginia, Texas |
| `name_2` | Sub-province/county name (where available) | Monongalia County |
| `aq_name` | Aqueduct watershed name | Upper Ohio, Cheat River |
| `pfaf_id` | Pfafstetter watershed code | 72100000 |

### Water Risk Indicators

| Field | Full Name | Scale | Interpretation |
|-------|-----------|-------|----------------|
| `bws_cat` | Baseline Water Stress (category) | 0-4, -1 | Primary scarcity indicator |
| `bws_label` | Baseline Water Stress (label) | text | Low/Low-Med/Med-High/High/Ext High |
| `bws_score` | Baseline Water Stress (score) | 0-5 continuous | Higher = more stressed |
| `bwd_cat` | Baseline Water Depletion (category) | 0-4, -1 | Groundwater + surface depletion |
| `bwd_label` | Baseline Water Depletion (label) | text | |
| `iav_cat` | Interannual Variability (category) | 0-4, -1 | Year-to-year flow fluctuation |
| `iav_label` | Interannual Variability (label) | text | |
| `sev_cat` | Seasonal Variability (category) | 0-4, -1 | Within-year flow fluctuation |
| `sev_label` | Seasonal Variability (label) | text | |
| `drr_cat` | Drought Risk (category) | 0-4, -1 | PDSI-based drought frequency and severity |
| `drr_label` | Drought Risk (label) | text | |
| `rfr_cat` | Riverine Flood Risk (category) | 0-4, -1 | Flood inundation return period |
| `rfr_label` | Riverine Flood Risk (label) | text | |
| `gtd_cat` | Groundwater Table Decline (category) | 0-4, -1 | Aquifer depletion trend (GRACE) |
| `gtd_label` | Groundwater Table Decline (label) | text | |
| `cep_cat` | Coastal Eutrophication Potential | 0-4, -1 | Nutrient loading risk |
| `ucw_cat` | Untreated Connected Wastewater | 0-4, -1 | Wastewater treatment coverage |

### Risk Category Scale (All Indicators)

| Category | Label | Percentile | Meaning |
|----------|-------|------------|---------|
| -1 | Arid and Low Water Use | — | Arid region; water withdrawal so low relative to availability that stress ratio is undefined; does NOT mean safe |
| 0 | Low | < 10th | Low risk |
| 1 | Low-Medium | 10-37th | Moderate risk |
| 2 | Medium-High | 37-67th | Elevated risk |
| 3 | High | 67-90th | High risk |
| 4 | Extremely High | > 90th | Highest risk globally |

---

## Example API Calls

### Query West Virginia Water Risk Data

```bash
curl -s "https://services.arcgis.com/LG9Yn2oFqZi5PnO5/arcgis/rest/services/Aqueduct_Annual/FeatureServer/0/query" \
  --data-urlencode "where=country_un='United States of America' AND name_1='West Virginia'" \
  --data-urlencode "outFields=name_0,name_1,aq_name,bws_cat,bws_label,bwd_cat,bwd_label,drr_cat,drr_label,rfr_cat,rfr_label,gtd_cat,gtd_label,iav_cat,iav_label" \
  --data-urlencode "returnGeometry=false" \
  --data-urlencode "f=json" \
  --data-urlencode "resultRecordCount=50"
```

### Query Texas (Permian Basin context), sorted by stress

```bash
curl -s "https://services.arcgis.com/LG9Yn2oFqZi5PnO5/arcgis/rest/services/Aqueduct_Annual/FeatureServer/0/query" \
  --data-urlencode "where=country_un='United States of America' AND name_1='Texas'" \
  --data-urlencode "outFields=name_0,name_1,aq_name,bws_cat,bws_label,bwd_cat,bwd_label,drr_cat,drr_label,gtd_cat,gtd_label" \
  --data-urlencode "returnGeometry=false" \
  --data-urlencode "orderByFields=bws_cat DESC" \
  --data-urlencode "f=json" \
  --data-urlencode "resultRecordCount=100"
```

### Query Extremely High Stress Watersheds in U.S.

```bash
curl -s "https://services.arcgis.com/LG9Yn2oFqZi5PnO5/arcgis/rest/services/Aqueduct_Annual/FeatureServer/0/query" \
  --data-urlencode "where=country_un='United States of America' AND bws_cat=4" \
  --data-urlencode "outFields=name_0,name_1,aq_name,bws_cat,bws_label" \
  --data-urlencode "returnGeometry=false" \
  --data-urlencode "f=json" \
  --data-urlencode "resultRecordCount=200"
```

### Parse JSON Response (bash + jq)

```bash
curl -s "..." | jq '[.features[].attributes |
  {name_1, aq_name, bws_label, drr_label, rfr_label, gtd_label}]'
```

---

## Workflow

### Step 1 — Identify Location

Map the user's location query to Aqueduct field values:
- **Country name:** Use `country_un` with official Aqueduct spellings (see
  table in `references/api_reference.md`)
- **State/Province:** Use `name_1` exactly as stored
- **Watershed basin:** Use `aq_name` if user specifies a basin name
- **County level:** Not directly available — query at state level and identify
  watershed(s) covering the target county by name or geography

**Key country name mappings:**
| User says | Aqueduct country_un |
|-----------|---------------------|
| USA / US / United States | United States of America |
| UK / Britain | United Kingdom |
| Russia | Russian Federation |
| Iran | Iran (Islamic Republic of) |
| Venezuela | Venezuela (Bolivarian Republic of) |

### Step 2 — Query ArcGIS FeatureServer

Execute the query with appropriate WHERE clause. Start with state/province
level. If the response has many features, sort by `bws_cat DESC` and report
the highest-stress watersheds first. If the response is empty, check country
name spelling — try without the state filter.

Retrieve at minimum: bws_cat, bws_label, drr_cat, drr_label, rfr_cat,
rfr_label, gtd_cat, gtd_label, iav_cat for each watershed.

### Step 3 — Aggregate Results

For a state query returning multiple watersheds:
- Report the range (min to max category) for each indicator
- Identify the specific high-stress watersheds by name
- Note if results are heterogeneous (e.g., "western Texas watersheds are
  Extremely High stress while eastern Texas watersheds are Medium-High")

### Step 4 — Apply Petroleum Operations Implications

Use the standard implications table below to interpret each risk category.

### Step 5 — Produce Output

Format as a risk score table followed by narrative summary.

---

## Output Format

### Risk Score Table

```
## Water Risk Assessment — [Location]
Source: WRI Aqueduct 4.0 Annual Data

| Indicator | Category | Label | O&G Operations Implication |
|-----------|----------|-------|---------------------------|
| Baseline Water Stress | [0-4] | [label] | [see implications table] |
| Baseline Water Depletion | [0-4] | [label] | [see implications table] |
| Drought Risk | [0-4] | [label] | [see implications table] |
| Riverine Flood Risk | [0-4] | [label] | [see implications table] |
| Groundwater Decline | [0-4] | [label] | [see implications table] |
| Interannual Variability | [0-4] | [label] | [see implications table] |
```

### Standard Implications by Indicator and Category

**Baseline Water Stress (bws):**
- 0-1 (Low/Low-Medium): Freshwater sourcing feasible; regulatory burden moderate; surface water permits available
- 2 (Medium-High): Monitor permitted withdrawals carefully; report water use; consider produced water reuse as partial alternative
- 3-4 (High/Extremely High): Surface and groundwater sourcing severely constrained; produced water reuse strongly preferred or required; water procurement plans needed before permit approval

**Baseline Water Depletion (bwd):**
- 0-1: Groundwater replenishment adequate; aquifer availability stable
- 2: Aquifer drawdown concerns; model seasonal and long-term impacts before new groundwater withdrawals
- 3-4: Aquifer at risk of permanent depletion; avoid new groundwater wells for completion fluid sourcing; subsidence risk

**Drought Risk (drr):**
- 0-1: Freshwater availability reliable; drought unlikely to interrupt operations
- 2: Plan for periodic shortages (1-in-5 to 1-in-10 year events); maintain water storage buffer
- 3-4: Chronic shortage risk; operations dependent on surface water should have contingency plans including produced water reuse or trucked-in water

**Riverine Flood Risk (rfr):**
- 0-1: Minimal flood hazard to surface facilities; standard drainage design adequate
- 2: Locate pits and tanks above 25-year flood stage; check FEMA flood maps for pad siting
- 3-4: High infrastructure exposure; pad siting, secondary containment design, and emergency response plans must explicitly account for 100-year flood inundation; saltwater containment failure during floods is a major regulatory liability

**Groundwater Table Decline (gtd):**
- 0-1: Aquifer stable; long-term groundwater availability reasonable
- 2: Declining trend; produced water disposal via UIC Class II wells preferred over new freshwater withdrawals
- 3-4: Active aquifer depletion (GRACE satellite data confirms); competing use conflicts likely; water disposal to saline zones may face increasing regulatory scrutiny

**Interannual Variability (iav):**
- 0-1: Consistent water availability year to year; minimal planning burden
- 2: Variability manageable with modest on-site storage or diversified supply
- 3-4: High year-to-year swings; water sourcing agreements and reuse infrastructure are critical for operational continuity

### Narrative Summary Structure

1. Location context and which O&G producing formation this covers
2. Key finding — the highest-category indicator and its significance
3. Operations relevance — which specific operations are most affected
4. Produced water reuse value — higher stress = higher economic and
   regulatory value of produced water reuse over freshwater sourcing
5. Regulatory signal — high stress regions attract more water withdrawal
   scrutiny from state regulators
6. Comparison to major O&G basins for context

### Example Output

```
## Water Risk Assessment — West Virginia (Appalachian Basin / Marcellus)
Source: WRI Aqueduct 4.0 Annual Data

| Indicator | Category | Label | O&G Implication |
|-----------|----------|-------|-----------------|
| Baseline Water Stress | 0-1 | Low to Low-Medium | Freshwater sourcing feasible; Ohio/Monongahela systems available |
| Baseline Water Depletion | 0 | Low | Aquifer replenishment adequate |
| Drought Risk | 1 | Low-Medium | Occasional dry periods; not chronic |
| Riverine Flood Risk | 2-3 | Medium-High to High | Pad siting and pit location need flood staging assessment |
| Groundwater Decline | 0 | Low | Appalachian aquifers not under extraction pressure |
| Interannual Variability | 1 | Low-Medium | Reasonably consistent year-to-year precipitation |

**Summary:** West Virginia sits in the water-abundant Appalachian region.
Baseline water stress is low compared to major U.S. O&G basins — the
Permian Basin in West Texas typically scores Extremely High, Bakken
in North Dakota typically Medium-High. The primary water risk for Marcellus
operations in WV is riverine flood exposure along the Monongahela and
Kanawha corridors, affecting pad siting and produced water pit design.
Freshwater sourcing for hydraulic fracturing is generally feasible with
appropriate WVDEP permits. Produced water reuse is economically driven by
disposal cost reduction rather than water scarcity here. [Certainty: MEDIUM —
Aqueduct data at watershed scale; site conditions may differ]
```

---

## Error Handling

| Condition | Action |
|-----------|--------|
| ArcGIS returns 200 with empty features array | Country_un name mismatch most likely; try country-only WHERE clause; check alternate name spellings in references/api_reference.md |
| HTTP 400 Bad Request | Malformed WHERE clause; check for unescaped apostrophes (use doubled single quote: O''Brien), verify field name spelling, ensure strings are quoted |
| HTTP 499 or 500 | ArcGIS service temporarily unavailable; retry after 30 seconds; suggest WRI Aqueduct web tool https://www.wri.org/aqueduct as fallback |
| More than 100 features returned | Summarize by range and modal category; identify top-5 highest-stress watersheds by aq_name |
| Category = -1 returned | Arid and Low Water Use classification; explain this does NOT mean low risk — it means so arid that stress ratio is undefined; note extreme absolute scarcity |
| User asks for county-level data | Aqueduct data is at HydroSHEDS watershed scale; identify overlapping watersheds by aq_name; note that county boundaries do not align with watershed boundaries |

---

## Regional Context for U.S. O&G Basins

Pre-loaded context to interpret results against major producing regions:

| Basin | State(s) | Typical BWS Category | Typical GTD | Operations Context |
|-------|----------|---------------------|-------------|--------------------|
| Permian (Delaware/Midland) | TX, NM | 4 (Extremely High) | 3-4 | Severe scarcity; PW reuse economically compelling and increasingly required |
| Bakken | ND, MT | 2-3 (Med-High/High) | 1-2 | Semi-arid; seasonal constraints on surface water; moderate PW reuse activity |
| Marcellus | WV, PA | 0-1 (Low/Low-Med) | 0-1 | Water-abundant; flood risk is primary concern not scarcity |
| Utica | OH, WV, PA | 0-1 (Low/Low-Med) | 0-1 | Similar to Marcellus; Great Lakes basin protection regs relevant in OH |
| Eagle Ford | TX (South) | 3 (High) | 2-3 | High stress; significant PW volumes support reuse economics |
| Haynesville | LA, TX | 1-2 (Low-Med) | 0-1 | Lower stress; Gulf Coast flooding is primary surface risk |
| DJ Basin | CO, WY | 2-3 (Med-High/High) | 2 | Front Range water competition; strict state water use regulations |
| Anadarko | OK | 2 (Med-High) | 1-2 | Moderate; induced seismicity near disposal wells adds complexity |

---

## Caveats and Data Limitations

- **Watershed scale, not point scale.** Aqueduct data represents hydrological
  watershed units (HydroSHEDS level 6, averaging ~50,000 km2). Site-specific
  conditions within a watershed can vary substantially.
- **Historical baseline.** Aqueduct 4.0 uses long-term averages (1979-2019).
  It does not reflect real-time drought. For current conditions, use USGS
  WaterWatch or the U.S. Drought Monitor.
- **Demand-side uncertainty.** Baseline Water Stress is calculated as total
  withdrawals divided by total renewable supply. Agricultural withdrawal data
  (USGS, FAO) has significant uncertainty and may understate or overstate
  actual consumption in specific watersheds.
- **GRACE groundwater resolution.** Groundwater Table Decline uses GRACE
  satellite gravity anomaly data at ~300 km resolution — lower spatial detail
  than other indicators.
- **Produced water not separately accounted.** Aqueduct does not model
  produced water reuse, which can significantly offset freshwater demand in
  active O&G basins. Stress scores therefore overstate true freshwater demand
  where reuse programs are active.
- **Quality vs. quantity.** Aqueduct covers water quantity risk. For water
  quality context near O&G operations, use pnge-federal-data:usgs-waterdata (streamflow
  and water quality gauges) and pnge-federal-data:epa-regulatory (NPDES, UIC permits).

---

## Implementation Notes

- Use `curl` with POST form encoding (`--data-urlencode`) for queries with
  apostrophes in country/state names — GET URLs will fail on apostrophes
- Parse response: `response.features[].attributes` contains the field data
- ArcGIS server max recordCount is typically 1000; paginate with
  `resultOffset` if needed for national-scale queries
- Service metadata (layer definition, field aliases): append `?f=json` to the
  FeatureServer/0 URL (without `/query`)
- See `references/api_reference.md` for all available Aqueduct service
  layers (monthly, food-water-energy, flood module), complete field list,
  and all country name spellings used by the Aqueduct database
