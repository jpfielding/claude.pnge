# CEJST Methodology Reference

The **Climate and Economic Justice Screening Tool (CEJST)** is the federal
government's official definition of a "disadvantaged community" for
Justice40 implementation under Executive Order 14008 and OMB Memorandum
M-22-13. The tool and its binary flag identify **census tracts** (not
block groups, not counties) that are disadvantaged.

- **v1.0** — released November 2022, used through the end of the Biden
  administration, uses **2010 census tracts**.
- **v2.0** — staged briefly January 2025, then rescinded following the
  January 2025 executive orders. v1.0 remains the canonical version for
  any grant or project still required to implement Justice40.
- **Host status (2025):** `screeningtool.geoplatform.gov` was taken down.
  The bulk CSV remains on `catalog.data.gov` and the
  `usds/justice40-tool` GitHub repository.

---

## Core data file

**v1.0 communities CSV**
`https://static-data-screeningtool.geoplatform.gov/data-versions/1.0/data/score/downloadable/1.0-communities.csv`

Backup mirror:
`https://raw.githubusercontent.com/usds/justice40-tool/main/data/data-pipeline/data_pipeline/files/cejst_communities.csv`

**Archived documentation:**
- Methodology v1.0: `https://screeningtool.geoplatform.gov/en/methodology`
  (mirrored at `https://github.com/usds/justice40-tool/blob/main/docs/methodology-v1.0.pdf`)
- Shapefile / GeoJSON: `1.0-shapefile.zip`, `1.0-communities.geojson`

---

## Schema (key fields)

| Column | Description |
|--------|-------------|
| `Census tract 2010 ID` | 11-digit FIPS tract GEOID (leading zero preserved) |
| `State/Territory` | e.g., "West Virginia" |
| `County Name` | |
| `Identified as disadvantaged` | Boolean (True/False) — **the flag** |
| `Total threshold criteria exceeded` | Count 0–8 of burden categories met |
| `Total categories exceeded` | Same, aggregated |
| `Is low income (imputed and adjusted)?` | Low-income gate indicator |
| `Percentage of individuals < 100% Federal Poverty Line` | |
| `Percentage of individuals < 200% Federal Poverty Line` | |

### The 8 burden categories

Each category has its own column `{Category} (has related burden)?` and
`Is {category} burdened and is low income?`. A tract is flagged
disadvantaged if **any** category is burdened AND the low-income gate is
met, OR if the tract meets special exceptions (tribal lands, some
territories, or surrounded-by-disadvantaged rule).

| Category | Burden indicators (80th-percentile thresholds on a national basis) |
|----------|-------------------------------------------------------------------|
| 1. Climate change | Expected agricultural loss rate; expected building loss rate; expected population loss rate; projected flood risk (FEMA NRI); projected wildfire risk |
| 2. Energy | Energy cost burden (% income); PM2.5 concentration |
| 3. Health | Asthma; diabetes; heart disease; low life expectancy |
| 4. Housing | Historic underinvestment (HOLC grade D tracts); housing cost burden (>30% income); lack of green space; lack of indoor plumbing; lead paint exposure |
| 5. Legacy pollution | Proximity to hazardous waste facilities; proximity to Superfund sites; proximity to RMP facilities; abandoned mine lands; former defense sites |
| 6. Transportation | Diesel particulate matter; transportation barriers / access; traffic proximity |
| 7. Water and wastewater | Leaky underground storage tanks; wastewater discharge hazard |
| 8. Workforce development | Linguistic isolation; low median income; % unemployed; % adults without HS diploma |

### The "low-income" gate

For categories 1–7, the tract additionally must have ≥65th-percentile
low-income population (low income = household income < 200% federal
poverty, imputed with an adjustment for college-student tracts).

For the workforce-development category only, the gate is instead an
education threshold: ≥10% of the adult population lacks a high school
diploma.

### Tribal override

Tracts that include Federally Recognized Tribal land are automatically
flagged disadvantaged regardless of burden-gate logic.

### Territorial handling

American Samoa, Guam, CNMI, and the U.S. Virgin Islands use a simplified
rule (unemployment + poverty) because the full Census ACS is not
available there.

### Surrounded-by-disadvantaged rule

A tract that fails burden gates but is completely surrounded by
disadvantaged tracts (and is partially in low-income gate) is also
flagged. This primarily affects small rural tracts.

---

## Using CEJST for PNGE permitting

1. **Federal funding Justice40** — Projects using DOE, EPA, Interior, or
   DOT funds must report the % of benefits flowing to CEJST-disadvantaged
   tracts. DLE pilot awards under DOE FOA-0002930 and successors fall in
   this category.
2. **Non-funded projects** — CEJST has no direct regulatory authority
   outside Justice40, but it is frequently cited in:
   - FERC pipeline EJ analysis
   - State DEP permitting comment letters
   - Title VI civil-rights complaints to EPA OECR
3. **Cumulative impact screens** — Pair CEJST flag with EJScreen
   percentiles; a CEJST-disadvantaged tract with multiple 80-pctl
   EJScreen indexes is a cumulative-impact signal.

---

## v1.0 → v2.0 differences (archived, for reference)

v2.0 (Jan 2025, rescinded) made these changes:
- Added health-related burden: low birth weight
- Added housing burden: residential energy burden (relocated from
  Energy category)
- Reweighted the linguistic-isolation gate
- Re-expressed thresholds against 2020 tracts instead of 2010

Because v2.0 was rescinded, **use v1.0 and the 2010 tract geography.**

---

## Common gotchas

- **Leading zeros in tract GEOID** — the CSV preserves them; load as
  string, never as integer.
- **10 vs 11 digits** — The CSV sometimes labels tracts with 11 digits
  including leading state zero. Always normalize to 11 digits.
- **Tracts with population < 1000** — Many are marked "not rated" — do
  not interpret missing flag as "not disadvantaged."
- **Island territories** have limited columns populated.
- **2010 vs 2020 geometry** — CEJST uses 2010 tracts. If pairing with
  EJScreen 2024 (2020 BG geography), use the Census Bureau 2010-to-2020
  tract relationship file:
  `https://www.census.gov/geographies/reference-files/2020/geo/relationship-files.html`
