---
name: ejscreen-cejst-svi
description: >
  Combined environmental justice and community vulnerability screening for a
  U.S. location (lat/lon, tract, or block group). Integrates EPA EJScreen
  (block-group environmental and demographic percentiles), CEJST (tract-level
  disadvantaged-community flag), and CDC/ATSDR SVI (tract-level vulnerability
  themes). Use whenever the user asks about environmental justice, EJ,
  EJScreen, CEJST, disadvantaged community, social vulnerability, SVI,
  community impact, permitting screening, Title VI risk, cumulative impacts,
  or NEPA screening. Especially useful for PNGE siting work: Class II UIC
  disposal-well siting, direct-lithium-extraction plant screening, frac-water
  sourcing impact analysis, and pipeline routing. Produces a unified table
  with EJScreen percentiles, CEJST flag and burden categories, and SVI theme
  percentiles for the covering census geographies, plus a narrative flagging
  elevated-risk indicators and likely permitting friction.
---

# Environmental Justice & Community Vulnerability Screening Skill

Unified EJ/vulnerability screen combining **EPA EJScreen**, **CEJST**, and
**CDC/ATSDR SVI** for a single U.S. location. Designed for petroleum &
natural-gas engineering siting and permitting workflows — Class II disposal
wells, direct-lithium-extraction (DLE) plants, frac-water withdrawal points,
and associated midstream infrastructure.

No credentials required. All three datasets are publicly downloadable or
queryable via open REST services.

---

## Dataset Overview

| Dataset | Geography | Level | Cadence | Format |
|---------|-----------|-------|---------|--------|
| EPA EJScreen | Block group (~600–3,000 people) | 13 env indicators, 7 socioeconomic, 13 EJ indexes, 13 supplemental indexes | Annual (last official v2.3, 2024) | ArcGIS REST + bulk CSV/GDB |
| CEJST | Census tract (~4,000 people) | Binary "disadvantaged" flag + 8 burden categories | v1.0 (Nov 2022), v2.0 staged Jan 2025 (rescinded) | Bulk CSV, GeoJSON |
| CDC/ATSDR SVI | Census tract (also county) | 4 themes + overall percentile, 16 variables | Every 2 yrs (2014, 2016, 2018, 2020, 2022) | Bulk CSV, ArcGIS REST |

**Important status note (2025):** EPA removed the live EJScreen tool and
`ejscreen.epa.gov` domain in early 2025. The underlying data remains
available via:
- GitHub mirror: `https://github.com/usepa/ejscreen` (data + methodology)
- Public Environmental Data Partnership: `https://screening-tools.com/epa-ejscreen`
- EPA FTP archive of 2024 release: `https://gaftp.epa.gov/EJScreen/2024/`
- Several state agencies and universities host the ArcGIS services
  (e.g., Screening Tools, ESRI Living Atlas). The skill defaults to
  Screening Tools mirror and falls back to the bulk CSV.

CEJST was likewise taken down in early 2025 (`screeningtool.geoplatform.gov`
returns a placeholder), but the v1.0 bulk CSV remains mirrored on
`catalog.data.gov` and GitHub (`usds/justice40-tool`).

SVI remains hosted by CDC/ATSDR and has not been removed.

---

## Workflow (happy path)

### Step 1 — Resolve Intent
Parse the user's input to one of:
- **Lat/lon** (e.g., `39.6295, -79.9559`)
- **Address** (geocode first — use Census Geocoder: `https://geocoding.geo.census.gov/geocoder/`)
- **FIPS** — 11-digit census tract or 12-digit block group
- **Project type** — disposal well, DLE plant, frac-water intake, pipeline centerline

### Step 2 — Resolve Geography
Given lat/lon, retrieve the containing block group (12-digit GEOID) and
census tract (11-digit GEOID) via the Census Bureau Geocoder:

```bash
curl -s "https://geocoding.geo.census.gov/geocoder/geographies/coordinates\
?x=-79.9559&y=39.6295&benchmark=Public_AR_Current&vintage=Current_Current\
&layers=Census%20Block%20Groups,Census%20Tracts&format=json" \
  | jq '.result.geographies'
```
The block-group GEOID = STATE(2)+COUNTY(3)+TRACT(6)+BG(1) = 12 digits.
The tract GEOID = STATE(2)+COUNTY(3)+TRACT(6) = 11 digits.

### Step 3 — Query EJScreen
**Option A — ArcGIS REST (Screening Tools mirror):**
```bash
# EJScreen 2024 block-group layer, state-percentile view
curl -s "https://services.arcgis.com/cJ9YHowT8TU7DUyn/arcgis/rest/services/\
EJScreen_2024_Public/FeatureServer/0/query" \
  --data-urlencode "where=ID='540619606003'" \
  --data-urlencode "outFields=*" \
  --data-urlencode "f=json"
```

**Option B — Point-in-polygon via spatial query:**
```bash
curl -s "https://services.arcgis.com/cJ9YHowT8TU7DUyn/arcgis/rest/services/\
EJScreen_2024_Public/FeatureServer/0/query" \
  --data-urlencode "geometry=-79.9559,39.6295" \
  --data-urlencode "geometryType=esriGeometryPoint" \
  --data-urlencode "inSR=4326" \
  --data-urlencode "spatialRel=esriSpatialRelIntersects" \
  --data-urlencode "outFields=ID,ACSTOTPOP,MINORPCT,LOWINCPCT,PM25,OZONE,DSLPM,\
CANCER,RESP,PTRAF,PRE1960PCT,PNPL,PRMP,PTSDF,PWDIS,UST,LEAD,EJINDEX_PM25,\
EJINDEX_DSLPM,EJINDEX_CANCER,EJINDEX_RESP,EJINDEX_PTRAF,EJINDEX_LEAD,\
EJINDEX_PNPL,EJINDEX_PRMP,EJINDEX_PTSDF,EJINDEX_OZONE,EJINDEX_PWDIS,\
EJINDEX_UST,EJINDEX_PRE1960PCT" \
  --data-urlencode "f=json"
```

**Option C — Bulk CSV fallback** (≈200 MB, block-group granularity):
```bash
# 2024 national block-group file
wget "https://gaftp.epa.gov/EJScreen/2024/2.32_August_UseMe/\
EJSCREEN_2024_BG_StatePct_with_AS_CNMI_GU_VI.csv.zip"
# Filter locally:
unzip -p EJSCREEN_2024_BG_StatePct_with_AS_CNMI_GU_VI.csv.zip \
  | awk -F',' 'NR==1 || $2=="540619606003"'
```

See `references/ejscreen_indicators.md` for the full field catalog and
percentile definitions.

### Step 4 — Query CEJST
CEJST has no REST API. Pull the bulk CSV once, cache, then lookup by
11-digit tract GEOID:
```bash
# Primary source (if still live):
curl -s "https://static-data-screeningtool.geoplatform.gov/data-versions/\
1.0/data/score/downloadable/1.0-communities.csv" -o cejst_1.0_communities.csv

# Backup mirror (GitHub):
curl -sL "https://raw.githubusercontent.com/usds/justice40-tool/main/\
data/data-pipeline/data_pipeline/files/cejst_communities.csv" \
  -o cejst_1.0_communities.csv

# Lookup a tract:
awk -F',' 'NR==1 || $1=="54061960600"' cejst_1.0_communities.csv
```
Key fields: `Census tract 2010 ID`, `Identified as disadvantaged`
(1/0), plus the 8 burden category flags (climate, energy, health,
housing, legacy pollution, transportation, water/wastewater, workforce).
See `references/cejst_methodology.md` for the threshold logic.

### Step 5 — Query SVI
**Option A — ArcGIS REST (CDC-hosted):**
```bash
curl -s "https://services3.arcgis.com/1IjeLYkadeVrSHSJ/ArcGIS/rest/services/\
CDC_ATSDR_SVI_2022_US_tract/FeatureServer/0/query" \
  --data-urlencode "where=FIPS='54061960600'" \
  --data-urlencode "outFields=FIPS,LOCATION,RPL_THEMES,RPL_THEME1,\
RPL_THEME2,RPL_THEME3,RPL_THEME4,E_TOTPOP,E_POV150,E_UNEMP,E_NOHSDP,\
E_AGE65,E_AGE17,E_DISABL,E_MINRTY,E_MUNIT,E_MOBILE,E_CROWD,E_NOVEH,E_GROUPQ" \
  --data-urlencode "f=json"
```

**Option B — Bulk CSV:**
```bash
# 2022 U.S. tract-level
curl -sL "https://svi.cdc.gov/Documents/Data/2022/csv/\
SVI_2022_US.csv" -o svi_2022_us.csv
awk -F',' 'NR==1 || $5=="54061960600"' svi_2022_us.csv
```
Four theme percentiles plus overall; see `references/svi_themes.md`.

### Step 6 — Merge and Produce Output
Join EJScreen (BG) → CEJST (tract, same 11 digits as BG prefix) →
SVI (tract). Present the unified screen as the output below.

---

## Output Format

### Unified EJ Screen — {lat,lon or address}

**Geography resolved**
- Block Group: 540619606003 (West Virginia, Monongalia County)
- Census Tract: 54061960600
- ACS population (block group): 1,187
- ACS population (tract): 4,512

### EJScreen environmental indicators (block group 540619606003)

| Indicator | Value | US Pctl | State Pctl | EJ Index Pctl (state) |
|-----------|------:|-------:|----------:|---------------------:|
| PM2.5 (ug/m3) | 8.1 | 42 | 61 | 58 |
| Ozone (ppb) | 62.4 | 55 | 44 | 47 |
| Diesel PM (ug/m3) | 0.32 | 47 | 65 | 68 |
| Air toxics cancer risk | 30 | 41 | 52 | 55 |
| Air toxics respiratory HI | 0.38 | 38 | 49 | 51 |
| Traffic proximity | 210 | 51 | 62 | 63 |
| Lead paint indicator | 0.43 | 77 | 82 | 85 |
| Superfund proximity | 0.09 | 36 | 51 | 54 |
| RMP proximity | 0.41 | 58 | 66 | 69 |
| TSDF proximity | 0.12 | 42 | 53 | 57 |
| Wastewater discharge | 1.9e-4 | 48 | 55 | 59 |
| UST density | 3.2 | 61 | 70 | 72 |

**Demographic (for context — not risk):**
- % minority: 6.2 (state pctl 8)
- % low-income: 38.4 (state pctl 71)
- % linguistically isolated: 0.0
- % less than HS education: 12.1 (state pctl 58)
- % under age 5: 5.3
- % over age 64: 17.4

### CEJST (census tract 54061960600, v1.0)

| Field | Value |
|-------|-------|
| Identified as disadvantaged | **YES** |
| Climate change burden | no |
| Energy burden | **yes** |
| Health burden | no |
| Housing burden | no |
| Legacy pollution burden | **yes** |
| Transportation burden | no |
| Water & wastewater burden | no |
| Workforce development burden | **yes** |

### CDC/ATSDR SVI 2022 (census tract 54061960600)

| Theme | Percentile |
|-------|-----------:|
| Overall (RPL_THEMES) | 0.81 |
| 1. Socioeconomic status | 0.78 |
| 2. Household characteristics | 0.65 |
| 3. Racial & ethnic minority | 0.22 |
| 4. Housing type & transportation | 0.74 |

**High-vulnerability flag:** Overall SVI ≥ 0.75 → YES

### Narrative summary (required)

1. **CEJST disadvantaged status** (single most important permitting signal)
2. **EJScreen percentiles ≥ 80** — list each with its EJ Index
3. **SVI overall ≥ 0.75** — note theme drivers
4. **Combined risk category** — LOW / MODERATE / ELEVATED / HIGH based on the
   rubric in the next section
5. **Permitting implications** for the project type (e.g., Class II UIC in
   WV — DEP public notice, EPA Region 3 Title VI petition risk)

---

## Combined Risk Rubric

| Condition | Category |
|-----------|----------|
| CEJST disadvantaged AND SVI overall ≥ 0.75 AND ≥3 EJScreen indexes ≥ 80 | **HIGH** |
| CEJST disadvantaged AND (SVI ≥ 0.75 OR ≥2 EJScreen indexes ≥ 80) | **ELEVATED** |
| CEJST NOT disadvantaged BUT SVI ≥ 0.75 OR ≥2 EJScreen indexes ≥ 80 | **MODERATE** |
| Otherwise | **LOW** |

This rubric is heuristic, not regulatory. Agencies (EPA, state DEPs) have
their own screening thresholds — EPA historically flagged the 80th
percentile on any EJ Index as a review trigger.

---

## Use Cases (PNGE-specific)

### 1. Class II UIC disposal-well siting
Run screen on proposed surface location before WV DEP UIC application.
Flags ELEVATED or HIGH trigger:
- Expanded public notice radius (EPA Region 3 practice)
- Title VI / civil rights complaint risk
- Enhanced groundwater monitoring plan
- NEPA environmental assessment instead of categorical exclusion

### 2. Direct-lithium-extraction plant site
Before acquiring land for a DLE brine processing facility:
- Screen plant footprint AND all truck-route census tracts
- Elevated PM2.5, diesel PM, or traffic proximity at ≥80 pctl suggests
  cumulative-impact community — stakeholder engagement needed early
- Coupled with high SVI: local workforce hiring and community benefits
  agreement become near-mandatory for permit defensibility

### 3. Frac-water sourcing impact analysis
Screen each withdrawal-point census tract plus all tracts downstream to the
next major confluence:
- Water & wastewater burden (CEJST) indicates existing stress
- Housing theme (SVI theme 4) + well-water reliance from ACS/USGS data
  flags vulnerability to perceived or actual water quality impacts

### 4. Pipeline routing / midstream
For a centerline, intersect with all block groups & tracts it crosses;
summarize the worst-case values. High-SVI corridors face the highest
opposition risk and likely FERC Section 106 consultation complexity.

---

## Caveats & Bias

- **EJScreen is a screening tool, not a determination.** EPA explicitly
  warns against using it to declare an area "impacted" or "not impacted."
- **Block-group granularity matters.** A 500-m disposal well AOR can
  span multiple block groups; screen all that intersect.
- **CEJST v1.0 is retained as the canonical federal definition** (per
  OMB M-22-13/Justice40) despite the 2025 takedown. CEJST v2.0 existed
  briefly in Jan 2025 but was rescinded.
- **SVI is ACS-based** and lags reality by 2–4 years for the 5-year
  estimates it uses.
- **Demographic indicators are descriptive, not causal.** EJScreen's own
  methodology documentation makes this clear.
- **Dataset takedowns (2025):** EJScreen and CEJST live hosts were
  removed; rely on the mirrors listed above. The Public Environmental
  Data Partnership (`screening-tools.com`) is the most reliable
  functional replacement for EJScreen.

---

## Error Handling

| HTTP / Condition | Meaning | Action |
|------------------|---------|--------|
| 000 / NXDOMAIN on `ejscreen.epa.gov` | Host removed | Use Screening Tools mirror or bulk CSV |
| 404 on CEJST CSV URL | Host removed | Use GitHub mirror (`usds/justice40-tool`) |
| 200 + empty features | Lat/lon outside U.S. | Reject; EJ datasets only cover U.S. + territories |
| Tract GEOID present in SVI but missing CEJST row | Tract below pop threshold | Note "not rated by CEJST" — do not infer disadvantaged=no |
| ArcGIS query returns >1 feature | Point on BG boundary | Use first feature; note ambiguity |
| Block group GEOID mismatch between years | 2010 vs 2020 TIGER | EJScreen 2024 uses 2020 TIGER; CEJST v1.0 uses 2010 tracts — convert with Census Relationship File if needed |

---

## Implementation Notes

- **Prefer Go** — see `references/golang_client.go` for a unified client
  (`Screen(lat, lon)` returns a merged struct).
- **Cache** the CEJST and SVI bulk CSVs in `~/.cache/ejscreen-cejst-svi/`
  — both are stable and rarely reissued.
- **Address → lat/lon** use Census Geocoder (no key, no rate limit within
  reason). Nominatim and Google Maps are alternates but require attribution
  or keys.
- **2010 → 2020 tract crosswalk** — CEJST v1.0 is on 2010 tracts; EJScreen
  2024 is on 2020 block groups. When they diverge, prefer the 2010 tract
  result for CEJST (it is the regulatory definition) and note the vintage.
- **For pipeline/linear projects** intersect the centerline with the BG
  and tract polygons; do not snap to a single point.

---

## Reference Files

- `references/ejscreen_indicators.md` — Full EJScreen field catalog
  (12 environmental indicators, 7 demographic, 13 EJ indexes, 13
  supplemental indexes, state/national percentile mechanics).
- `references/cejst_methodology.md` — How the disadvantaged flag is
  computed (8 burden categories, tract thresholds, population exclusions).
- `references/svi_themes.md` — The 4 SVI themes, 16 underlying variables,
  RPL_* percentile methodology, flag_* count variables.
- `references/golang_client.go` — Unified Go client: `Screen(lat, lon)`
  orchestrates Census Geocoder + EJScreen ArcGIS + CEJST CSV + SVI
  ArcGIS and returns a merged `ScreenResult`.
