# EJScreen Indicators Reference

EJScreen is EPA's environmental justice screening tool, published annually
through 2024 (v2.32). It computes, for every census block group in the
United States and territories, a set of **environmental indicators**,
**socioeconomic indicators**, and their combination as **EJ Indexes** and
**Supplemental Indexes**. All are reported as raw values plus state and
national percentiles.

Canonical data dictionary (2024 release):
`https://gaftp.epa.gov/EJScreen/2024/2.32_August_UseMe/2024_EJScreen_columns-explained.xlsx`

---

## Geographic fields

| Field | Description |
|-------|-------------|
| `ID` | 12-digit block-group GEOID (STATE+COUNTY+TRACT+BG) |
| `STATE_NAME` | State name |
| `ST_ABBREV` | Two-letter state |
| `REGION` | EPA Region (1–10) |
| `ACSTOTPOP` | ACS total population, block group |
| `ACSIPOVBAS` | ACS population for which poverty status is determined |
| `ACSEDUCBAS` | ACS population over 25 with education reported |
| `ACSTOTHH` | ACS total households |
| `NUM_BGS_IN_BUFFER` | For buffer reports, count of BGs partially inside |

---

## Environmental indicators (12)

Each is reported as: raw value (`{name}`), national percentile (`P_{name}`),
and state percentile (`P_{name}_st`). The EJ Index versions are listed
further down.

| Field | Units | Description |
|-------|-------|-------------|
| `PM25` | ug/m3 | Annual average PM2.5 (EPA OAQPS fused surface, 2019) |
| `OZONE` | ppb | Summer ozone (8-hr max, 3-yr average) |
| `DSLPM` | ug/m3 | Diesel particulate matter (NATA-style model) |
| `CANCER` | per million | Air toxics cancer risk (AirToxScreen 2019) |
| `RESP` | index | Air toxics respiratory hazard index |
| `PTRAF` | count × AADT / km | Traffic proximity (within 500 m) |
| `PRE1960PCT` | fraction | Lead paint indicator (% housing built pre-1960) |
| `PNPL` | site-score / km | Proximity to Superfund/NPL sites (within 5 km) |
| `PRMP` | facility-count / km | Proximity to Risk Management Plan facilities |
| `PTSDF` | facility-count / km | Proximity to Treatment, Storage, & Disposal Facilities |
| `PWDIS` | toxic-weighted / m³ | Wastewater discharge hazard (downstream) |
| `UST` | count | Underground storage tank density (within 1500 ft) |

Two additional environmental fields added in v2.3 (2023+):
| Field | Description |
|-------|-------------|
| `D2_PM25` | PM2.5 drinking-water intake disparities (experimental) |
| `NO2` | Annual NO2 (2020 TROPOMI-derived, supplemental) |

---

## Socioeconomic / demographic indicators (7)

These are **not** risk variables. EJScreen pairs them with environmental
indicators to produce the EJ Index.

| Field | Description |
|-------|-------------|
| `MINORPCT` | % people of color (non–white, non-Hispanic) |
| `LOWINCPCT` | % low-income (household income < 2× poverty level) |
| `LESSHSPCT` | % less than high school education (age 25+) |
| `LINGISOPCT` | % limited-English-speaking households |
| `UNDER5PCT` | % population under age 5 |
| `OVER64PCT` | % population over age 64 |
| `UNEMPPCT` | % unemployed (civilian labor force age 16+) |

**Demographic Index** (`DEMOGIDX_2`): simple average of MINORPCT and
LOWINCPCT, used as the demographic weight in EJ Index calculations.

**Supplemental Demographic Index** (`DEMOGIDX_5`): average of LOWINCPCT,
UNEMPPCT, LIFEEXPPCT, LESSHSPCT, LINGISOPCT. Used in the Supplemental
Indexes.

---

## EJ Indexes (13)

**Formula:** `EJINDEX_{x} = (env_indicator_{x}) × (DEMOGIDX_2 – national_mean_DEMOGIDX_2)`

Results are right-skewed. Block groups with both elevated environmental
burden **and** elevated demographic index will score high. Reported as
percentiles within state and nation.

| Field | Pairs with |
|-------|-----------|
| `EJINDEX_PM25` | PM2.5 |
| `EJINDEX_OZONE` | Ozone |
| `EJINDEX_DSLPM` | Diesel PM |
| `EJINDEX_CANCER` | Air toxics cancer risk |
| `EJINDEX_RESP` | Air toxics respiratory HI |
| `EJINDEX_PTRAF` | Traffic proximity |
| `EJINDEX_LEAD` | Lead paint indicator (PRE1960PCT) |
| `EJINDEX_PNPL` | Superfund proximity |
| `EJINDEX_PRMP` | RMP proximity |
| `EJINDEX_PTSDF` | TSDF proximity |
| `EJINDEX_PWDIS` | Wastewater discharge |
| `EJINDEX_UST` | UST density |
| `EJINDEX_D2_PM25` | Drinking-water PM2.5 disparity (experimental) |

---

## Supplemental Indexes (13)

Same as EJ Indexes but use the 5-variable **DEMOGIDX_5** in place of the
2-variable DEMOGIDX_2. These were added in v2.0 (2022) to respond to
criticism that the original EJ Index under-weighted education, language
access, and life expectancy.

Field names mirror the EJ Indexes but with `SUPPINDEX_` prefix:
`SUPPINDEX_PM25`, `SUPPINDEX_OZONE`, ..., `SUPPINDEX_UST`.

---

## Percentile mechanics

EJScreen reports three percentile views:

| Field suffix | Population |
|--------------|-----------|
| `P_{name}` | National percentile (all US block groups) |
| `P_{name}_st` | State percentile (BGs in the same state) |
| `P_{name}_r{N}` | EPA Region N percentile |

**Common screening thresholds** (EPA guidance, historical):
- **≥ 80** on any EJ Index → flag for enhanced review
- **≥ 90** → strong signal; often triggers expanded public engagement
- **≥ 95** → top-5% burden; Title VI complaint risk elevated

---

## File formats

### Block-group CSV (national, 2024)
`EJSCREEN_2024_BG_StatePct_with_AS_CNMI_GU_VI.csv.zip` (~200 MB unzipped).
Row per block group. Includes raw values + state percentiles.

`EJSCREEN_2024_BG_Percentiles.csv.zip` — same rows, national percentiles.

### Block-group GDB
Same data in ArcGIS File Geodatabase with block-group geometry.

### 1-km and 3-mile buffer summaries
`EJSCREEN_2024_BG_StatePct_Buffer1km.csv.zip` precomputed for each BG's
1-km and 3-mile buffer; useful for well-site screens without running your
own spatial joins.

---

## ArcGIS REST services (2024 mirrors)

The EPA host went dark in 2025. The following are known functional
mirrors (verify before heavy use):

| Host | Service |
|------|---------|
| ESRI Living Atlas | `services.arcgis.com/cJ9YHowT8TU7DUyn/.../EJScreen_2024_Public/FeatureServer/0` |
| Screening Tools PEDP | `screening-tools.com/arcgis/rest/services/EJScreen/...` |
| University mirrors (varies) | State universities occasionally expose the GDB |

Layer index in the canonical service:
| Layer | Geometry | Content |
|-------|----------|---------|
| 0 | Polygon | Block groups with full indicator set |
| 1 | Point | Block-group centroids (faster point-in-poly) |

Query params commonly used:
- `where=ID='{12-digit GEOID}'`
- `geometry={lon},{lat}` with `geometryType=esriGeometryPoint`, `inSR=4326`, `spatialRel=esriSpatialRelIntersects`
- `outFields=*` (or a comma-separated subset for speed)
- `f=json`

---

## Version history (for reproducibility)

| Version | Year | ACS vintage | Notable changes |
|---------|------|-------------|-----------------|
| 1.0 | 2015 | 2009–2013 | Initial public release |
| 2.0 | 2020 | 2014–2018 | Added SUPPINDEX, DEMOGIDX_5 |
| 2.1 | 2022 | 2016–2020 | AirToxScreen replaces NATA |
| 2.2 | 2023 | 2017–2021 | 2020 TIGER block groups |
| 2.3 | 2024 | 2018–2022 | D2_PM25 experimental field added |
| 2.32 | Aug 2024 | 2018–2022 | Last EPA-published release before 2025 takedown |

When citing EJScreen results in an EIS, FEIS, or permit application,
always cite the version and release date.
