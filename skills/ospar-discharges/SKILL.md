---
name: ospar-discharges
description: >
  Access OSPAR Commission data on offshore produced water discharges,
  chemical use, and oil-in-water concentrations from North Sea operations.
  Use when the user asks about international produced water discharge
  standards, North Sea produced water management, OSPAR offshore data,
  U.S. vs European produced water regulations, oil-in-water limits,
  offshore chemical discharge, or produced water treatment benchmarks.
  Trigger phrases: "OSPAR produced water data", "North Sea discharge
  limits", "European offshore produced water", "compare US North Sea
  produced water", "oil in water standards", "international produced
  water benchmarks", "UK offshore produced water volumes", "Norwegian
  produced water treatment", "best available technique produced water",
  "offshore discharge comparison". Produces discharge trend tables and
  narrative analysis with regulatory comparison context.
---

# OSPAR Discharges Skill

Accesses offshore produced water discharge data, chemical use statistics,
and regulatory benchmarks from the OSPAR Commission (Convention for the
Protection of the Marine Environment of the North-East Atlantic). OSPAR
data provides the primary international reference point for comparing U.S.
produced water management practices against North Sea standards.

## API Key Handling

**No API key required.** OSPAR data is publicly accessible through their
data portal and downloadable publications.

> **Important:** OSPAR does not provide a REST API for programmatic queries.
> Data access is through downloadable datasets (CSV/Excel) from the OSPAR
> data portal, and through published annual reports. This skill documents
> the data access workflow and key data structures.

---

## Data Sources

### OSPAR Data and Information Management System (ODIMS)

**Portal URL:** https://odims.ospar.org/

ODIMS is the primary data access point. It provides downloadable datasets
for all OSPAR assessment themes.

**Key data categories for PNGE research:**

| Category | Description | Format |
|----------|-------------|--------|
| Offshore Oil and Gas -- Discharges | Annual produced water discharge volumes and oil-in-water by country | CSV/Excel |
| Offshore Oil and Gas -- Chemical Use | Offshore chemical use and discharge by OSPAR category | CSV/Excel |
| Offshore Oil and Gas -- Spills | Accidental spills from offshore installations | CSV/Excel |

### Data Discovery Workflow

```bash
# ODIMS provides a catalog of datasets. Browse the catalog page:
# https://odims.ospar.org/en/submissions/
# Filter by theme: "Offshore Oil and Gas Industry"

# The OSPAR publications page provides annual reports:
# https://www.ospar.org/work-areas/oic/discharges

# OSPAR assessment documents with downloadable data annexes:
# https://oap.ospar.org/en/ospar-assessments/
```

### Direct Data Access Patterns

ODIMS datasets can be accessed through direct URLs once the dataset ID is
known. The portal uses a CKAN-like interface:

```bash
# Browse available datasets in the offshore theme
# Navigate: https://odims.ospar.org/en/submissions/
# Filter: Theme = "Offshore Oil and Gas Industry"
# Select dataset -> Download CSV/Excel

# Example: Download produced water discharge data
# After finding the dataset URL on ODIMS, use wget/curl:
curl -sL -o ospar_pw_discharges.csv \
  "https://odims.ospar.org/en/submissions/ospar_offshore_pw_discharge/download/"
```

**Note:** Direct download URLs may change. Always verify current URLs through
the ODIMS portal. The above is an example pattern -- the actual file path
depends on the current dataset publication.

### OSPAR Annual Reports (Published PDFs)

OSPAR publishes annual reports on discharges, spills, and chemical use:

```
# Annual Discharges, Spills and Emissions from Offshore Installations
# Published each year for the prior reporting year
# Available at: https://www.ospar.org/work-areas/oic/installations

# These contain summary tables that can be manually extracted or referenced
```

---

## Key Data Fields

### Produced Water Discharge Data

Based on OSPAR reporting requirements, the discharge dataset contains:

| Field | Description | Units |
|-------|-------------|-------|
| Country | Reporting Contracting Party (DK, NL, NO, UK, DE, IE) | ISO code |
| Year | Reporting year | YYYY |
| Installation Name | Name of offshore installation | Text |
| Field Name | Oil/gas field name | Text |
| Produced Water Volume | Total volume discharged to sea | tonnes or m3 |
| Oil in Produced Water | Mass of dispersed oil discharged | tonnes |
| Oil Concentration | Oil-in-water concentration | mg/L |
| Produced Water Reinjected | Volume reinjected | tonnes or m3 |

### Chemical Use and Discharge Data

| Field | Description | Units |
|-------|-------------|-------|
| Country | Reporting Contracting Party | ISO code |
| Year | Reporting year | YYYY |
| Chemical Category | OSPAR classification (PLONOR, HOCNF, etc.) | Category |
| Chemical Name | Substance name | Text |
| Amount Used | Total quantity used offshore | tonnes |
| Amount Discharged | Quantity discharged to sea | tonnes |
| Amount Injected | Quantity injected to formation | tonnes |

---

## OSPAR Regulatory Framework Reference

### Key Standards for Produced Water

| Standard | Value | Context |
|----------|-------|---------|
| Oil-in-water discharge limit | 30 mg/L (monthly average) | OSPAR Recommendation 2001/1 |
| Performance standard target | 15% reduction from 2006 baseline | OSPAR Recommendation 2012/5 |
| Zero harmful discharge goal | For OSPAR List chemicals | OSPAR Strategy |

### Chemical Classification System

| Category | Description | Discharge Status |
|----------|-------------|-----------------|
| PLONOR | Pose Little or No Risk to the environment | May be discharged |
| HOCNF | Harmonised Offshore Chemical Notification Format assessed | Case-by-case |
| OSPAR List | Chemicals for Priority Action | Phase-out target |
| HMCS | Hazardous substances in offshore context | Strict controls |

### Contracting Parties with Offshore Data

| Code | Country | Basin | Notes |
|------|---------|-------|-------|
| NO | Norway | North Sea, Norwegian Sea, Barents | Largest offshore producer |
| UK | United Kingdom | North Sea, West of Shetland | Mature province |
| DK | Denmark | Danish North Sea | Declining production |
| NL | Netherlands | Dutch North Sea | Gas-dominant |
| DE | Germany | German Bight | Small offshore sector |
| IE | Ireland | Celtic Sea, Atlantic Margin | Minimal production |

---

## Workflow

### Step 1 -- Resolve Intent

Map the user's question to the appropriate data source:

| User Wants | Data Source |
|-----------|------------|
| Produced water discharge volumes | ODIMS discharge dataset |
| Oil-in-water concentrations | ODIMS discharge dataset |
| Chemical use/discharge data | ODIMS chemical dataset |
| Regulatory limits/standards | OSPAR Recommendations (reference) |
| Country comparison | ODIMS discharge dataset by country |
| U.S. vs North Sea comparison | OSPAR data + EPA/state data from other skills |
| Best available technique | OSPAR BAT/BEP guidance documents |

### Step 2 -- Access Data

**Option A: ODIMS Portal (interactive)**

1. Navigate to https://odims.ospar.org/
2. Browse submissions or use search
3. Filter by theme: "Offshore Oil and Gas Industry"
4. Select the relevant dataset
5. Download as CSV or Excel
6. Parse locally

**Option B: Direct download (if URL known)**

```bash
# Download and inspect
curl -sL -o /tmp/ospar_data.csv "DATASET_URL_FROM_ODIMS"
head -5 /tmp/ospar_data.csv
```

**Option C: Reference published statistics**

For quick reference without downloading full datasets, use the summary
statistics from OSPAR annual reports:

**Key statistics (approximate, from OSPAR 2023 annual report):**

| Metric | Value | Year |
|--------|-------|------|
| Total PW discharged (OSPAR area) | ~340 million m3 | 2022 |
| Norway PW discharged | ~145 million m3 | 2022 |
| UK PW discharged | ~145 million m3 | 2022 |
| Average oil-in-water (OSPAR area) | ~12-15 mg/L | 2022 |
| Total oil discharged in PW | ~4,500 tonnes | 2022 |
| PW reinjection rate (Norway) | ~30-40% | 2022 |
| PW reinjection rate (UK) | ~10-15% | 2022 |

### Step 3 -- Parse and Analyze

If CSV data is downloaded:

```bash
# Count records by country
awk -F',' '{print $1}' /tmp/ospar_data.csv | sort | uniq -c | sort -rn

# Filter for a specific country (e.g., Norway)
grep "^NO," /tmp/ospar_data.csv | head -20

# Calculate average oil-in-water concentration
awk -F',' '$1=="NO" {sum+=$7; n++} END {print sum/n}' /tmp/ospar_data.csv
```

### Step 4 -- Produce Output

**Format: Data Table + Narrative with Comparison Context**

Present a markdown table of the most relevant rows (cap at ~20 rows), then
a narrative summary covering:

1. **Key findings** -- discharge volumes, oil-in-water trends
2. **Country comparison** -- Norway vs UK vs others
3. **Trend** -- direction over the time window
4. **Regulatory context** -- how values compare to 30 mg/L limit
5. **U.S. comparison** -- relate to NPDES discharge permits, EPA standards
6. **PNGE relevance** -- implications for produced water treatment technology
   selection, especially for Li/Mg recovery pre-treatment requirements

**Example output structure:**
```
## OSPAR Produced Water Discharges -- North Sea (2018-2022)

| Country | Year | PW Volume (M m3) | Oil Discharged (t) | Avg OIW (mg/L) |
|---------|------|-------------------|---------------------|-----------------|
| Norway  | 2022 | 145               | 1,850               | 12.8            |
| UK      | 2022 | 145               | 2,100               | 14.5            |
| Denmark | 2022 | 22                | 280                 | 12.7            |
| Neth.   | 2022 | 8                 | 95                  | 11.9            |

**Summary:** Total OSPAR-area produced water discharge was ~340 million m3
in 2022, dominated equally by Norway and the UK. Average oil-in-water
concentrations (12-15 mg/L) are well below the 30 mg/L regulatory limit,
reflecting decades of BAT investment. Norway reinjects 30-40% of PW,
significantly higher than the UK (10-15%).

**U.S. comparison:** The NPDES general permit for offshore platforms (EPA
Region 6) sets a 29 mg/L monthly average OIW limit (42 mg/L daily max),
comparable to OSPAR's 30 mg/L. However, OSPAR countries additionally track
and regulate specific hazardous substances in PW (BTEX, PAH, heavy metals,
naturally occurring radioactive materials), while U.S. regulation focuses
primarily on OIW and toxicity.

**Li/Mg context:** North Sea produced waters typically have lower TDS and
Li concentrations than Appalachian or Smackover brines, making them less
attractive for Li recovery. However, OSPAR treatment infrastructure
(hydrocyclones, flotation, membranes) represents the state of the art for
pre-treatment that would precede DLE in a Li recovery flowsheet.
```

---

## Error Handling

| Condition | Meaning | Action |
|-----------|---------|--------|
| ODIMS portal unavailable | Server maintenance | Retry after 30 minutes; use cached data or published reports |
| Download URL changed | Dataset republished | Navigate ODIMS portal to find current URL |
| CSV encoding issues | Non-UTF8 encoding | Try `iconv -f ISO-8859-1 -t UTF-8` on downloaded file |
| Missing years in data | Reporting lag or gap | Check OSPAR annual report for the latest available year |
| Empty/null fields | Not reported by that country | Note as N/A; not all parties report all fields |

---

## Comparing U.S. and OSPAR Standards

### Produced Water Discharge Limits

| Parameter | OSPAR | U.S. Offshore (NPDES) | U.S. Onshore |
|-----------|-------|-----------------------|--------------|
| Oil-in-water (monthly avg) | 30 mg/L | 29 mg/L | Zero discharge (most states) |
| Oil-in-water (daily max) | -- | 42 mg/L | Zero discharge |
| Chemical screening | HOCNF required | No equivalent | No equivalent |
| Hazardous substance tracking | Yes (OSPAR List) | Limited (TRI only if threshold met) | Varies by state |
| Reinjection incentive | Yes (OSPAR Rec.) | Economic only | Required in many states |

### Key Differences

1. **Chemical regulation:** OSPAR requires pre-screening of all offshore
   chemicals through HOCNF before use. The U.S. has no equivalent
   pre-approval system for oilfield chemicals.

2. **Produced water composition reporting:** OSPAR requires annual reporting
   of dispersed oil, dissolved oil, BTEX, PAH, heavy metals, and
   radionuclides in PW. U.S. NPDES primarily requires OIW monitoring.

3. **Zero harmful discharge:** OSPAR has a long-term goal of zero discharge
   of hazardous substances. The U.S. offshore permit system focuses on
   technology-based effluent limits.

4. **Onshore vs offshore:** In the U.S., most onshore produced water is
   reinjected via Class II UIC wells, not discharged. OSPAR only covers
   offshore operations.

---

## PNGE Applications

### Produced Water Treatment Technology Benchmarking

OSPAR BAT (Best Available Technique) guidance provides technology benchmarks
for produced water treatment:
- Hydrocyclones: reduce OIW from ~100-500 mg/L to ~20-40 mg/L
- Gas flotation: reduce to ~10-20 mg/L
- Membrane filtration: reduce to less than 5 mg/L
- These technologies would serve as pre-treatment before DLE for Li recovery

### International Context for Research Proposals

When writing proposals for produced water valorization (Li/Mg recovery),
OSPAR data provides:
- Volume benchmarks for produced water generation rates
- Water quality context (what contaminants must be managed)
- Regulatory precedent for treatment technology requirements
- Comparison point for U.S. regulatory development

### Environmental Impact Assessment

For facilities that process produced water (including Li recovery plants),
OSPAR monitoring methodologies provide:
- Standard methods for OIW measurement
- Effluent toxicity testing protocols (CHARM model)
- Environmental monitoring best practices
- Risk-based approach to chemical discharge assessment

---

## Caveats and Data Quality

- **No REST API.** OSPAR data is accessed via downloads, not programmatic
  API queries. Data availability depends on portal uptime and publication
  schedule.
- **Annual reporting lag.** Data is typically published 12-18 months after
  the reporting year. The most recent data available in 2026 is likely for
  2024 or 2023.
- **Country coverage varies.** Norway and the UK provide the most detailed
  data. Smaller producers (Ireland, Germany) may have incomplete records.
- **Self-reported by operators.** Like U.S. TRI data, OSPAR discharge data
  is reported by the operating companies and verified by national regulators.
  Measurement methods and quality vary.
- **Different units.** Some datasets report volumes in tonnes (using
  produced water density ~1.01-1.15 kg/L depending on TDS), others in
  cubic meters. Always check units.
- **Scope is offshore only.** OSPAR covers the North-East Atlantic maritime
  area. It does not cover onshore operations, Mediterranean, or other
  regions.
- **Published statistics are approximate.** Summary figures from annual
  reports are rounded and may not match precisely with downloadable
  installation-level data due to rounding and late reporting corrections.
- **Data format inconsistency.** CSV downloads from different years may
  have different column orders or names. Always check headers before
  parsing.

---

## Implementation Notes

- **Download-first workflow.** Unlike API-based skills, this skill requires
  downloading files, then parsing locally. Use `curl` to download, then
  `awk`/`jq`/`python3` to parse.
- **Cache downloaded data.** OSPAR data changes infrequently (annual
  updates). Download once and cache in `/tmp/` or a working directory.
- **For quick reference,** use the summary statistics table in this skill
  file rather than downloading the full dataset.
- **Python parsing** for Excel files (if downloaded as .xlsx):
  ```python
  # stdlib approach -- use csv module on exported CSV
  import csv
  with open('/tmp/ospar_data.csv') as f:
      reader = csv.DictReader(f)
      for row in reader:
          if row['Country'] == 'NO':
              print(row)
  ```
- **Cross-reference with other skills:** Use `epa-regulatory` for U.S. NPDES
  data, `boem-offshore` for U.S. OCS production data, and `fracfocus` for
  U.S. chemical disclosure data to build comparative analyses.
