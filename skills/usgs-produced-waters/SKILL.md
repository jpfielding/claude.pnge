---
name: usgs-produced-waters
description: >
  Query and analyze the USGS National Produced Waters Geochemical Database v3.0
  for produced water and oilfield brine chemistry from U.S. oil and gas wells.
  Use this skill whenever the user asks about produced water composition, brine
  geochemistry, lithium in oilfield brines, magnesium in formation waters, TDS
  or salinity of produced water, mineral recovery potential from co-produced
  fluids, or critical mineral concentrations in subsurface brines. Trigger
  phrases include: produced water chemistry, brine lithium concentration,
  Marcellus water quality, Smackover lithium, formation water analysis, Li in
  produced water, Mg in brine, what formations have high lithium, DLE feedstock,
  produced water TDS by basin, Appalachian brine chemistry. Covers 115,000+
  samples with 150+ analytes across all major U.S. basins. Outputs summary
  statistics tables and narrative analysis with formation-level context.
---

# USGS National Produced Waters Geochemical Database

Fetches and analyzes geochemical data from the USGS National Produced Waters
Geochemical Database v3.0 — the most comprehensive public dataset of produced
water and oilfield brine chemistry in the United States.

---

## Credential

**None required.** All data is publicly accessible through USGS ScienceBase.

```bash
# No API key needed — data is open access
# Template for consistency with other skills:
# KEY=$(grep '^api_key=' ~/.config/usgs/credentials 2>/dev/null | cut -d= -f2)
```

---

## Data Source

| Field | Value |
|-------|-------|
| Dataset | USGS National Produced Waters Geochemical Database (ver. 3.0, December 2023) |
| DOI | https://doi.org/10.5066/P9DSRCZJ |
| ScienceBase Item (v3.0) | `64fa1e71d34ed30c2054ea11` |
| ScienceBase Item (v2.3) | `59d25d63e4b05fe04cc235f9` |
| Records | ~115,000 produced water samples |
| Columns | 150+ (see `references/schema.md`) |
| Formats | v3.0: Excel (.xlsx), Shapefile (.shp); v2.3: CSV, Excel, R data |
| Coverage | All major U.S. oil and gas basins, some Canadian provinces |
| Update frequency | Irregular (v2.3: Jan 2019, v3.0: Dec 2023) |
| Viewer | https://www.usgs.gov/tools/us-geological-survey-national-produced-waters-geochemical-database-viewer |
| Citation | Blondes, M.S., Shelton, J.L., Engle, M.A., et al. (2023) |

**Version notes:** v3.0 introduced the `FORMSIMPLE` (standardized formation names)
and `PLAYTYPE` (geological play classification) columns, added 23 new datasets
focused on high-lithium brines and Appalachian Basin data, converted all ppm
values to mg/L, and improved location data. The `IDUSGS` identifier is
persistent across v2.3 and v3.0.

---

## API Structure

There is no REST query API — the database is a bulk download from ScienceBase.
The workflow is: **discover files via ScienceBase API, download, filter locally.**

### ScienceBase File Discovery

```bash
# List files for v3.0 (Excel + shapefile)
curl -s "https://www.sciencebase.gov/catalog/item/64fa1e71d34ed30c2054ea11?format=json&fields=files,title" \
  | jq '.files[] | {name, size, url: .downloadUri}'
```

**v3.0 files:**
| File | Size | Format |
|------|------|--------|
| `USGS_NPWGDv3_excel.xlsx` | 80 MB | Excel workbook (main data) |
| `USGS_NPWGDv3_data_dictionary.xlsx` | 30 KB | Column definitions |
| `USGS_NPWGDv3_shape.zip` | 24 MB | Shapefile (points with attributes) |
| `version_history.txt` | 6 KB | Version change log |

```bash
# List files for v2.3 (CSV available)
curl -s "https://www.sciencebase.gov/catalog/item/59d25d63e4b05fe04cc235f9?format=json&fields=files" \
  | jq '.files[] | {name, size, url: .downloadUri}'
```

**v2.3 files:**
| File | Size | Format |
|------|------|--------|
| `USGSPWDBv2.3c.csv` | 66 MB | CSV — compiled database (preferred) |
| `USGSPWDBv2.3n.csv` | 63 MB | CSV — numeric-only version |
| `USGSPWDBv2.3c.xlsx` | 29 MB | Excel — compiled database |
| `USGSPWDBv2.3 Data Dictionary.csv` | 7 KB | Column definitions |
| `USGSPWDBv2.3 Data Sources.csv` | 2 KB | Source dataset list |

### Download the CSV (v2.3)

```bash
# Download v2.3 compiled CSV (~66 MB)
curl -L -o /tmp/USGSPWDBv2.3c.csv \
  "https://www.sciencebase.gov/catalog/file/get/59d25d63e4b05fe04cc235f9?f=__disk__11%2F1e%2F8e%2F111e8e3952b1637289254fd398af95a81f937389"
```

### Download the Excel file (v3.0)

```bash
# Download v3.0 Excel workbook (~80 MB)
curl -L -o /tmp/USGS_NPWGDv3_excel.xlsx \
  "https://www.sciencebase.gov/catalog/file/get/64fa1e71d34ed30c2054ea11?f=__disk__e7%2Fef%2F17%2Fe7ef17fcb71c49e2241da4139ed775f8e328bdab"
```

### Search ScienceBase for Related Datasets

```bash
# Search for other produced water datasets
curl -s "https://www.sciencebase.gov/catalog/items?q=produced+water+geochemical&format=json&max=10" \
  | jq '.items[] | {id, title}'
```

---

## Key Columns

Full schema is in `references/schema.md`. The most important columns for
lithium/magnesium research are:

### Identification and Location
- **IDUSGS** — unique sample ID (persistent across versions)
- **STATE**, **COUNTY**, **BASIN** — geographic location
- **LATITUDE**, **LONGITUDE** — coordinates (some approximate; check COORDAPX)
- **FIPCODE** — 5-digit FIPS code for state+county

### Geology
- **FORMSIMPLE** — standardized formation name (v3.0; use for filtering)
- **FORMATION** — formation name as reported (partially standardized)
- **PLAYTYPE** — play classification: Shale, Coal, Sedimentary, Geothermal, Injection (v3.0)
- **BASIN** — geologic basin (cleaned in v3.0)
- **ERA**, **PERIOD**, **EPOCH** — geologic age
- **DEPTHUPPER**, **DEPTHLOWER** — perforation interval (ft)

### Chemistry (all in mg/L)
- **Li** — Lithium (key target for DLE)
- **Mg** — Magnesium (co-recovery target)
- **TDS** — Total dissolved solids (best available: measured, reported-calculated, or ion-sum)
- **Na**, **Ca**, **K**, **Cl**, **SO4**, **HCO3** — major ions
- **Ba**, **Sr**, **Br**, **Fe** (FeTot), **Mn**, **Si**, **B** — minor/trace
- **d7Li** — lithium isotope ratio (per mil)

### Physical Properties
- **PH** — pH
- **TEMP** — temperature (deg F)
- **SG** — specific gravity (reported or calculated)
- **PRESSURE** — formation pressure (psi)

---

## Key Formations

Detailed formation data is in `references/formations.md`. Summary of
highest-priority formations for Li/Mg research:

| Formation | Basin | States | Li (mg/L) | Mg (mg/L) | Economic Potential |
|-----------|-------|--------|-----------|-----------|-------------------|
| Smackover | Gulf Coast | AR, TX, LA | 50-477 | 1,000-5,000+ | Highest U.S. brine Li; active DLE projects |
| Marcellus | Appalachian | WV, PA, OH | 10-200+ | 500-3,000 | Large water volumes; Li correlates with TDS |
| Utica / Pt. Pleasant | Appalachian | OH, WV, PA | 20-150 | 500-2,500 | Co-produced with Marcellus |
| Bakken | Williston | ND, MT | 10-70 | 500-4,000 | High volumes; moderate Li |
| Wolfcamp | Permian | TX, NM | 5-50 | 300-3,000 | Massive volumes; lower Li |

**Economic threshold for DLE:** approximately 100-150 mg/L Li depending on
technology and brine volume. Emerging technologies may lower this to ~50 mg/L.

**FORMSIMPLE values** for filtering: `Smackover`, `Marcellus`, `Utica`,
`Point Pleasant`, `Bakken`, `Wolfcamp`, `Eagle Ford`, `Oriskany`, `Clinton`,
`Devonian Shale`, `Tuscaloosa`.

---

## Workflow

### Step 1 — Resolve Intent

Map the user's question to a filtering strategy:

| User asks about... | Filter by... |
|---------------------|-------------|
| A specific formation | `FORMSIMPLE` or `FORMATION` |
| A state or region | `STATE`, `COUNTY`, or `BASIN` |
| Lithium potential | `Li` column with minimum threshold |
| A type of play | `PLAYTYPE` (Shale, Sedimentary, Coal, etc.) |
| Specific wells | `API` number or `WELLNAME` |
| High-TDS brines | `TDS` with minimum threshold |
| Specific analyte | Any chemistry column (see `references/schema.md`) |

### Step 2 — Discover and Download Data

1. Check if a local copy exists (cached from prior use):
   ```bash
   ls -la /tmp/USGSPWDBv2.3c.csv 2>/dev/null || ls -la /tmp/USGS_NPWGDv3_excel.xlsx 2>/dev/null
   ```

2. If not cached, download from ScienceBase:
   ```bash
   # Prefer v2.3 CSV for scripted analysis (v3.0 requires openpyxl for Excel)
   curl -L -o /tmp/USGSPWDBv2.3c.csv \
     "https://www.sciencebase.gov/catalog/file/get/59d25d63e4b05fe04cc235f9?f=__disk__11%2F1e%2F8e%2F111e8e3952b1637289254fd398af95a81f937389"
   ```

3. Warn the user about file size (~66 MB for v2.3 CSV, ~80 MB for v3.0 Excel).

### Step 3 — Filter and Analyze

Use Python (or bash with awk/csvtool) to filter and compute statistics:

```python
import csv, statistics

# Load CSV
with open("/tmp/USGSPWDBv2.3c.csv") as f:
    reader = csv.DictReader(f)
    rows = [r for r in reader if "marcellus" in r.get("FORMATION", "").lower()]

# Extract Li values
li_vals = [float(r["Li"]) for r in rows if r.get("Li") and r["Li"] not in ("", "-9999")]

# Statistics
print(f"Marcellus Li: n={len(li_vals)}, "
      f"median={statistics.median(li_vals):.1f}, "
      f"mean={statistics.mean(li_vals):.1f}, "
      f"max={max(li_vals):.1f} mg/L")
```

For common queries, use the ready-made client in `references/python_example.py`
which provides `filter_rows()`, `summary_stats()`, and formatted output
functions.

**Common filtering patterns:**

```bash
# Count samples by state (bash + awk on CSV)
awk -F',' 'NR==1{for(i=1;i<=NF;i++) if($i=="STATE") col=i}
           NR>1{count[$col]++}
           END{for(s in count) print count[s], s}' \
  /tmp/USGSPWDBv2.3c.csv | sort -rn | head -20

# Extract high-Li samples (Python one-liner)
python3 -c "
import csv
with open('/tmp/USGSPWDBv2.3c.csv') as f:
    r = csv.DictReader(f)
    hits = [row for row in r if row.get('Li') and float(row['Li'] or 0) > 100]
print(f'{len(hits)} samples with Li > 100 mg/L')
for h in sorted(hits, key=lambda x: float(x.get('Li',0)), reverse=True)[:10]:
    print(f\"  Li={h['Li']} mg/L  State={h.get('STATE','')}  Fm={h.get('FORMATION','')}\")
"
```

### Step 4 — Produce Output

**Format: Summary Statistics Table + Narrative**

Present results as a markdown table (capped at ~20 rows for readability),
followed by a narrative summary covering:

1. **Dataset scope** — how many samples matched the filter, from how many states/formations
2. **Key statistics** — median, mean, min, max, P25/P75 for the target analytes
3. **Notable findings** — highest-concentration samples, formation-level patterns
4. **Economic context** — comparison to DLE thresholds, co-production potential
5. **Caveats** — data quality notes, sampling bias, version differences

---

## Output Format

### Example 1: Formation Query

```
## Marcellus Shale — Produced Water Lithium Analysis

| Statistic | Li (mg/L) | Mg (mg/L) | TDS (mg/L) |
|-----------|-----------|-----------|------------|
| N         | 847       | 1,023     | 1,156      |
| Min       | 0.1       | 12        | 1,200      |
| P25       | 28        | 580       | 85,000     |
| Median    | 62        | 1,250     | 145,000    |
| Mean      | 75        | 1,380     | 155,000    |
| P75       | 105       | 2,100     | 210,000    |
| Max       | 235       | 3,200     | 345,000    |

**Summary:** The Marcellus Shale produced water database contains 1,156
samples across WV, PA, OH, and NY. Lithium concentrations (n=847) have a
median of 62 mg/L with 25% of samples exceeding 105 mg/L — above or near
the DLE economic threshold of 100-150 mg/L. The highest Li value (235 mg/L)
was reported from a well in WV. Mg averages 1,380 mg/L, making co-recovery
viable in high-TDS wells. Note: Li data coverage is incomplete (73% of
samples have Li measured). Sampling is biased toward PA and WV where
Marcellus production is highest.
```

### Example 2: State Query

```
## West Virginia — Produced Water Chemistry by Formation

| Formation | N | Li Median (mg/L) | Li Max (mg/L) | TDS Median (mg/L) |
|-----------|---|-------------------|----------------|---------------------|
| Marcellus | 312 | 78 | 235 | 165,000 |
| Utica | 45 | 92 | 148 | 195,000 |
| Oriskany | 28 | 35 | 88 | 120,000 |
| Clinton | 19 | 22 | 41 | 95,000 |
| Devonian Shale | 67 | 18 | 52 | 68,000 |

**Summary:** West Virginia produced waters span multiple Appalachian Basin
formations. The Marcellus and Utica formations show the highest lithium
potential, with median Li of 78 and 92 mg/L respectively. The top Utica
samples approach DLE-economic concentrations (148 mg/L max). TDS correlates
with Li across all formations. Data availability is strongest for the
Marcellus (n=312) reflecting modern shale gas development.
```

---

## Error Handling

| Issue | Cause | Action |
|-------|-------|--------|
| ScienceBase item 404 / "not found" | Item ID changed or item secured | Search by title: `q=National+Produced+Waters+Geochemical+Database` |
| Download timeout | Large file (~66-80 MB) | Increase timeout; suggest download to local file first |
| CSV parsing errors | Encoding issues, embedded commas | Use `errors="replace"` encoding; check for quoted fields |
| Column not found | v2.3 vs v3.0 schema difference | v3.0 has FORMSIMPLE, PLAYTYPE; v2.3 uses FORMATION, WELLTYPE |
| Empty results for filter | Misspelled formation or state | Use FORMSIMPLE values from `references/formations.md`; STATE uses full names not abbreviations |
| -9999 values | Missing data sentinel | Exclude -9999 from all numeric calculations |
| Li/Mg column all blank | Analyte not measured for those samples | Report coverage (N with data / N total); note sparse coverage for trace elements |
| Excel file (v3.0) cannot be parsed | No openpyxl installed | Fall back to v2.3 CSV; or `pip install openpyxl` |

---

## Caveats

1. **Sampling bias.** The database is a compilation from published sources, not
   a statistically designed survey. Some formations and states are heavily
   overrepresented (Appalachian Basin, Texas) while others have few samples.
   Sample density does not reflect production volumes.

2. **Temporal coverage.** Samples span from the 1930s to 2020s. Older samples
   may use different analytical methods with lower precision. Comparison across
   eras requires caution.

3. **Incomplete analyte coverage.** Not all samples have all analytes measured.
   Lithium coverage is notably sparse in older datasets. Always report the
   N (number of non-null values) alongside statistics.

4. **Approximate locations.** Many samples have approximate coordinates
   (county centroid, field centroid, or state centroid). Check the `COORDAPX`
   column before using lat/lon for spatial analysis.

5. **Units.** All chemistry in v3.0 is mg/L (v3.0 converted all ppm using
   specific gravity). In v2.3, the `UNITSORIG` column indicates whether the
   original was mg/L or ppm.

6. **TDS calculation.** The `TDS` column is a "best available" value using
   measured TDS first, then reported-calculated TDS, then ion-sum-calculated
   TDS. Check `TDSDESC` for the method.

7. **Formation name inconsistency.** Use `FORMSIMPLE` (v3.0) for reliable
   formation-level grouping. The `FORMATION` column has many spelling variants
   and qualifiers that make grouping unreliable without normalization.

8. **v2.3 vs v3.0 differences.** v3.0 added 23 new datasets (especially
   high-Li brines), fixed location errors, and standardized formation names.
   For lithium research, v3.0 is strongly preferred. However, v3.0 is only
   available as Excel (not CSV), requiring openpyxl or similar to parse
   programmatically.

9. **Self-reported industry data.** Some source datasets are from industry
   reports. Quality control varies by source. The `CHARGEBAL` column (charge
   balance) can be used as a data quality indicator — values far from 0%
   suggest analytical errors.

10. **Not a reserves estimate.** Concentration data alone does not determine
    economic viability. Recovery depends on water volume, flow rates,
    brine chemistry complexity, infrastructure, and DLE technology efficiency.

---

## Implementation Notes

- **Prefer `bash_tool` or `python`** in Claude's environment to download and analyze
- **Use v2.3 CSV** for scripted analysis (no dependencies beyond stdlib)
- **Use v3.0 Excel** when `openpyxl` is available and you need FORMSIMPLE/PLAYTYPE columns
- **Cache downloads** to `/tmp/` to avoid re-downloading the 66-80 MB file
- **Python client** — see `references/python_example.py` for ready-made filtering and statistics
- **Full column schema** — see `references/schema.md` for all 150+ column definitions
- **Formation reference** — see `references/formations.md` for Li/Mg ranges by formation
- STATE uses full names (e.g., "West Virginia", not "WV")
- Missing data is represented as empty string or `-9999` — always exclude from calculations
