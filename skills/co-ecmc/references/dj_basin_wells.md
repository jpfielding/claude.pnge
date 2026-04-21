# DJ Basin / Wattenberg Reference

Detailed reference for Denver-Julesburg (DJ) Basin well data, Niobrara/Codell
stratigraphy, and produced water characteristics. Use in conjunction with
the main SKILL.md.

---

## Geographic Scope

The DJ Basin covers ~70,000 square miles across northeast Colorado, southeast
Wyoming, western Nebraska, and western Kansas. The Colorado portion — and
specifically the Wattenberg field — is the commercially dominant area.

**Wattenberg field boundaries (approximate):**
- North: Weld / Larimer county line
- South: Denver metro (Adams, Broomfield, Boulder counties)
- East: ~104°30' W longitude
- West: Front Range foothills / Dakota Hogback

**Core counties by 2024 well count:**

| County | County Code (FIPS) | Active Wells (approx.) | Primary Phase |
|--------|-------------------|------------------------|---------------|
| Weld | 123 | 20,000+ | Oil + associated gas |
| Adams | 001 | 1,800+ | Oil + gas |
| Broomfield | 014 | 250+ | Oil + gas (SB19-181 focal point) |
| Boulder | 013 | 150+ | Oil + gas (declining, municipal opposition) |
| Arapahoe | 005 | 400+ | Oil (shallow J-Sand legacy) |

---

## Stratigraphy (Top-Down)

| Formation | Age | Typical Depth (ft TVD) | Role |
|-----------|-----|------------------------|------|
| Pierre Shale | Late Cretaceous | 0-5,500 | Seal / overburden |
| Niobrara | Late Cretaceous | 6,500-8,000 | Primary unconventional target |
| — Niobrara A chalk | | 6,500-7,000 | High-quality carbonate-rich bench |
| — Niobrara B chalk | | 7,000-7,500 | Most-drilled bench |
| — Niobrara C chalk | | 7,500-8,000 | Co-developed with B |
| Codell Sandstone | Late Cretaceous | 7,200-8,300 | Primary tight-sand target |
| Carlile Shale | Late Cretaceous | 7,300-8,400 | Thin, not a target |
| Greenhorn Limestone | Late Cretaceous | 7,400-8,500 | Minor target |
| Graneros Shale | Late Cretaceous | 7,500-8,600 | Seal |
| D Sand (Dakota) | Early Cretaceous | 7,700-8,800 | Conventional legacy |
| J Sand (Muddy) | Early Cretaceous | 7,500-8,700 | Conventional legacy; shallow oil in some areas |

**Typical modern horizontal:** 2-mile lateral, Niobrara B + Codell co-developed,
20-50 frac stages, 2,000-3,000 lb/ft proppant loading.

---

## Produced Water Characteristics (Niobrara/Codell)

Representative ranges from published USGS, SPE, and ECMC operator reports.
Substantial well-to-well variation; use the `pnge:usgs-produced-waters`
skill for specific-well values.

| Parameter | Typical Range | Notes |
|-----------|---------------|-------|
| TDS | 80,000 - 200,000 mg/L | Higher in Codell than Niobrara A |
| pH | 6.2 - 7.2 | Slightly acidic at high TDS |
| Density | 1.06 - 1.14 g/mL | |
| Na | 25,000 - 55,000 mg/L | Dominant cation |
| Cl | 55,000 - 130,000 mg/L | Dominant anion |
| Ca | 3,000 - 15,000 mg/L | |
| Mg | 400 - 1,500 mg/L | |
| K | 400 - 1,800 mg/L | |
| Ba | 500 - 3,000 mg/L | BaSO4 scaling risk |
| Sr | 300 - 2,000 mg/L | |
| Fe | 20 - 300 mg/L | |
| Li | 40 - 120 mg/L | Commercially interesting in upper range |
| Br | 400 - 1,200 mg/L | |
| I | 10 - 50 mg/L | |
| SO4 | < 500 mg/L | Low due to Ba scavenging |
| HCO3 | 200 - 800 mg/L | |
| NORM (combined Ra-226 + Ra-228) | 10 - 200 pCi/L | Comparable to Marcellus lower range |

**Water-oil ratio (WOR):**
- Early production (first 6 mo): 0.3 - 0.8
- Mid-life (1-5 yr): 0.8 - 2.0
- Late life (5+ yr): 2.0 - 5.0+
- Lifetime average: ~1.2 - 1.5x (substantially lower than Permian's 5-10x)

**Li economic cutoff check:**
- Upper end (120 mg/L) is at or above the DLE economic threshold (~100 mg/L)
  for current-generation direct lithium extraction
- Combined with modest volumes (~0.5 MMBBL/day basin-wide water), the
  theoretical Li resource is ~25-75 tonnes/day Li — enough for pilot-scale
  but probably not utility-scale without multi-operator aggregation

---

## Key Operators in Wattenberg (2024)

| Operator | Market Share (approx.) | Notes |
|----------|-----------------------|-------|
| Civitas Resources | ~30% | Merger of Extraction + Bonanza Creek + Crestone |
| Chevron | ~20% | Acquired Noble Energy in 2020 |
| PDC Energy / Oxy | ~15% | Oxy acquired PDC in 2023 |
| Kerr-McGee / Oxy | (rolled into above) | |
| Bayswater E&P | <5% | Private |
| Great Western Petroleum | <5% | |
| Verdad Resources | <5% | |

Operator consolidation matters for produced-water pilot deals — three
operators control ~65% of Wattenberg production, so engagement with
Civitas, Chevron, and Oxy covers most of the resource.

---

## ECMC Data Access for DJ Basin

**Monthly production filtered to DJ Basin:**

```bash
# Pull the CSV and filter to Weld + Adams + Broomfield (DJ core):
curl -sO "https://ecmc.state.co.us/documents/data/downloads/production/monthly_prod.csv"

# Column structure as of 2024-2025 (verify header — ECMC occasionally
# reorders):
# API_COUNTY, API_SEQ_NUM, SIDE_TRACK_NUM, NAME, FORMATION,
# FIRST_PROD_DATE, LAST_PROD_DATE, OIL_PROD, GAS_PROD, WATER_PROD,
# OIL_DAYS, GAS_DAYS, WATER_DAYS, OIL_DISPOSITION, GAS_DISPOSITION,
# REPORT_YEAR, REPORT_MONTH, OPERATOR_NUM, OPERATOR_NAME

awk -F, 'NR==1 || $1=="123" || $1=="001" || $1=="014"' monthly_prod.csv > dj_basin.csv
```

**Annual production with more fields:**

```bash
curl -sO "https://ecmc.state.co.us/documents/data/downloads/production/2024_prod_reports.csv"
```

**Well header data (locations, TD, spud dates):**

Use the producing-well download landing page:
```
https://ecmc.colorado.gov/data-maps/downloadable-data-documents/prod-well-download
```
The actual file link on that page changes periodically; fetch the HTML and
follow the current download button.

**Spatial context (field polygons):**

```bash
curl -sO "https://ecmc.state.co.us/documents/data/downloads/gis/COGCC_FIELDS_SHP.zip"
# Wattenberg field is named "WATTENBERG" in the FIELD_NAME attribute.
```

**SB19-181 proximity for Wattenberg wells:**

The urban-edge location of Wattenberg puts hundreds of wells within
reverse-setback distances of homes, schools, and municipal boundaries.
Pull the SB181 layers to flag any well inside DI or proximity polygons:

```bash
curl -sO "https://ecmc.state.co.us/documents/data/downloads/gis/SB181DataFinal_20241209.gdb.zip"
unzip SB181DataFinal_20241209.gdb.zip
ogrinfo SB181DataFinal_20241209.gdb
```

---

## Cross-Reference Skills

- `pnge:usgs-produced-waters` — well-level brine chemistry (Li/Mg/TDS)
- `pnge:epa-regulatory` — UIC Class II federal records (UIC intent mode)
- `pnge:fracfocus` — Wattenberg stimulation fluid disclosures
- `pnge:frac-design` — engineering analysis of Niobrara/Codell fracs
- `pnge:regulatory-disposal-analyst` — state-federal disposal overlay
- `pnge:netl-carbon-storage` — Class VI context for DJ Basin CCS pilots
- `pnge:aqueous-chemistry-electrochem` — DLE process design for Niobrara
  brines
