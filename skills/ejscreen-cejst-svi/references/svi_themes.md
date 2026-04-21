# CDC/ATSDR Social Vulnerability Index (SVI) Reference

The **Social Vulnerability Index (SVI)** is published by the CDC Agency
for Toxic Substances and Disease Registry. It ranks census tracts (and
counties) on their relative vulnerability to external stressors
(disasters, disease outbreaks, industrial accidents). Four **themes** and
an **overall** index are reported as percentile ranks on a 0–1 scale.

- **Home:** https://www.atsdr.cdc.gov/placeandhealth/svi/
- **Documentation:** https://www.atsdr.cdc.gov/placeandhealth/svi/documentation/SVI_documentation_2022.html
- **Downloads:** https://www.atsdr.cdc.gov/placeandhealth/svi/data_documentation_download.html
- **ArcGIS host:** `services3.arcgis.com/1IjeLYkadeVrSHSJ/ArcGIS/rest/services/`
- **Cadence:** Biennial releases — 2014, 2016, 2018, 2020, 2022. As of
  2026 the most recent is **SVI 2022** (uses ACS 2018–2022 5-year).

Unlike EJScreen and CEJST, SVI remains hosted by CDC/ATSDR and was not
taken down in 2025.

---

## Four themes and 16 variables

### Theme 1 — Socioeconomic status (RPL_THEME1)
| Variable | Description |
|----------|-------------|
| `EP_POV150` | % below 150% federal poverty (replaced EP_POV in 2020) |
| `EP_UNEMP` | % civilian (age 16+) unemployed |
| `EP_HBURD` | % housing cost-burdened (>30% income) |
| `EP_NOHSDP` | % age 25+ no high school diploma |
| `EP_UNINSUR` | % no health insurance |

### Theme 2 — Household characteristics (RPL_THEME2)
| Variable | Description |
|----------|-------------|
| `EP_AGE65` | % age 65 and older |
| `EP_AGE17` | % age 17 and younger |
| `EP_DISABL` | % civilian noninstitutionalized disabled |
| `EP_SNGPNT` | % single-parent households with children under 18 |
| `EP_LIMENG` | % limited-English-speaking, age 5+ |

### Theme 3 — Racial & ethnic minority status (RPL_THEME3)
| Variable | Description |
|----------|-------------|
| `EP_MINRTY` | % racial/ethnic minority (all except non-Hispanic white) |

### Theme 4 — Housing type & transportation (RPL_THEME4)
| Variable | Description |
|----------|-------------|
| `EP_MUNIT` | % housing in structures with ≥10 units |
| `EP_MOBILE` | % mobile homes |
| `EP_CROWD` | % occupied housing units with more people than rooms |
| `EP_NOVEH` | % households with no vehicle available |
| `EP_GROUPQ` | % persons in group quarters |

---

## Field-name conventions

SVI uses prefixes to indicate representation:

| Prefix | Meaning |
|--------|---------|
| `E_` | Estimate (raw count or number) |
| `M_` | Margin of error |
| `EP_` | Estimate percentage |
| `MP_` | Margin of error on percentage |
| `EPL_` | Percentile rank of EP within the theme universe |
| `SPL_THEME{n}` | Sum of EPL values in theme n |
| `RPL_THEME{n}` | Percentile rank of SPL_THEME{n} (0–1, higher = more vulnerable) |
| `F_` | Flag (1 if EPL ≥ 0.90) |
| `F_THEME{n}` | Count of flags within theme n |
| `F_TOTAL` | Sum of all flags across all themes (0–16) |
| `RPL_THEMES` | **Overall SVI percentile** — percentile rank of the sum of SPL_THEME1..4 |

### Missing-data sentinel
`-999` is used for tracts that cannot be ranked (no population, group
quarters dominant, or small-sample ACS suppression). Always check for
-999 before computing.

---

## Interpretation thresholds

| RPL_THEMES | Category (CDC convention) |
|-----------|---------------------------|
| 0.00 – 0.25 | Low vulnerability |
| 0.25 – 0.50 | Low-moderate |
| 0.50 – 0.75 | Moderate-high |
| 0.75 – 1.00 | High vulnerability |

A common "hot-spot" criterion: RPL_THEMES ≥ 0.75 AND F_TOTAL ≥ 6.

---

## Geographies

| Level | File | Notes |
|-------|------|-------|
| Census tract | `SVI_{year}_US.csv` | ~84,000 rows (national) |
| Census tract by state | `SVI_{year}_{STATE}.csv` | e.g., `SVI_2022_WestVirginia.csv` |
| County | `SVI_{year}_US_county.csv` | ~3,200 rows |
| Shapefile / GDB | `SVI_{year}_US_tract.gdb.zip` | With geometry |

FIPS column is `FIPS` (11-digit for tracts, 5-digit for counties).
CDC uses 2010 tracts for SVI 2016 and earlier, 2020 tracts from SVI 2020
onward.

---

## ArcGIS REST services

| Service | URL |
|---------|-----|
| SVI 2022 tracts | `services3.arcgis.com/1IjeLYkadeVrSHSJ/ArcGIS/rest/services/CDC_ATSDR_SVI_2022_US_tract/FeatureServer/0` |
| SVI 2022 counties | `.../CDC_ATSDR_SVI_2022_US_county/FeatureServer/0` |
| SVI 2020 tracts | `.../CDC_ATSDR_SVI_2020_US_tract/FeatureServer/0` |

Query pattern (tract lookup):
```bash
curl -s "https://services3.arcgis.com/1IjeLYkadeVrSHSJ/ArcGIS/rest/services/\
CDC_ATSDR_SVI_2022_US_tract/FeatureServer/0/query" \
  --data-urlencode "where=FIPS='54061960600'" \
  --data-urlencode "outFields=FIPS,LOCATION,RPL_THEMES,RPL_THEME1,RPL_THEME2,RPL_THEME3,RPL_THEME4,F_TOTAL,E_TOTPOP" \
  --data-urlencode "f=json"
```

Query pattern (point-in-polygon):
```bash
curl -s "https://services3.arcgis.com/1IjeLYkadeVrSHSJ/ArcGIS/rest/services/\
CDC_ATSDR_SVI_2022_US_tract/FeatureServer/0/query" \
  --data-urlencode "geometry=-79.9559,39.6295" \
  --data-urlencode "geometryType=esriGeometryPoint" \
  --data-urlencode "inSR=4326" \
  --data-urlencode "spatialRel=esriSpatialRelIntersects" \
  --data-urlencode "outFields=*" \
  --data-urlencode "f=json"
```

---

## Differences from EJScreen

| Attribute | SVI | EJScreen |
|-----------|-----|----------|
| Scale | Census tract | Census block group |
| Vintage | Biennial | Annual |
| Contains env indicators? | No | Yes (12) |
| Contains demographic? | Yes | Yes |
| Output | 4 themes + overall | 12 indicators × 3 percentiles × 2 index flavors |
| Intended use | Disaster response, public-health planning | Environmental-justice screening |
| Regulatory status | Used in FEMA/HHS planning | EPA/permitting, advisory |

SVI complements EJScreen rather than replaces it: **SVI tells you who is
vulnerable; EJScreen tells you what they are exposed to.**

---

## Common gotchas

- **2010 vs 2020 tracts** — SVI 2020 and later use 2020 TIGER tracts.
  SVI 2018 and earlier use 2010 tracts. Pairing with CEJST v1.0 (2010
  tracts) requires a crosswalk.
- **-999 values** — filter out before computing averages.
- **Percentiles are relative to the U.S. population of tracts each
  release** — do not compare numeric RPL values across releases as if
  they were absolute.
- **Theme 3 is a single variable** — its RPL_THEME3 is just the
  national percentile rank of EP_MINRTY. Low theme-3 scores in
  homogeneous rural areas do NOT mean the community is not vulnerable
  overall; check RPL_THEMES.
