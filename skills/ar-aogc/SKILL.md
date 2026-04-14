---
name: ar-aogc
description: >
  Access Arkansas Oil and Gas Commission (AOGC) well, production, and permit
  data for Arkansas oil and gas operations. Use this skill when the user asks
  about Arkansas wells, Arkansas oil and gas production, AOGC data, Smackover
  Formation Arkansas, Arkansas lithium brines, Standard Lithium Arkansas,
  Exxon lithium project, Equinor Smackover, DLE direct lithium extraction
  Arkansas, south Arkansas brine production, Fayetteville Shale, Arkansas
  injection wells, AR produced water, Arkansas disposal wells, or any Arkansas
  upstream regulatory data. Critical for lithium research — south Arkansas
  Smackover Formation contains the highest-concentration lithium brines in the
  U.S. (up to 477 mg/L Li), and multiple DLE projects are under active
  development by Standard Lithium, ExxonMobil, and Equinor. Produces data
  tables with narrative summaries.
---

# Arkansas Oil and Gas Commission (AOGC) Data Skill

Accesses Arkansas oil and gas regulatory data from the AOGC. While Arkansas is a
smaller oil and gas producer, it is ground zero for U.S. lithium-from-brine
development. The south Arkansas Smackover Formation hosts the highest known
lithium concentrations in U.S. produced waters and has attracted major DLE
(direct lithium extraction) investments.

## API Key Handling

**No API key required.** AOGC data is publicly accessible. However, the AOGC
has limited online data infrastructure compared to major producing states.

**Important:** The AOGC website (`www.aogc.state.ar.us`) has restricted
automated access (403 responses to standard web crawlers). Manual browser access
or specific data request workflows may be necessary.

---

## Data Access Architecture

The AOGC provides data through three channels:

1. **AOGC Website** — well data, production reports, permit records, orders
2. **B-19 Production Reports** — annual production reporting by operators
3. **Cross-Reference Sources** — USGS databases, academic literature, and
   company filings contain more detailed Smackover brine data than AOGC itself

### Channel 1: AOGC Website

**Base URL:** `https://www.aogc.state.ar.us/`

| Resource | URL/Path | Data |
|----------|----------|------|
| AOGC Home | `https://www.aogc.state.ar.us/` | Main portal with navigation to data |
| Online Services | `https://www.aogc.state.ar.us/onlineservices.htm` | Links to data query tools |
| Well Data | `https://www.aogc.state.ar.us/welldata.htm` | Well records and search |
| Production Reports | `https://www.aogc.state.ar.us/production.htm` | B-19 production data |
| General Rules and Orders | `https://www.aogc.state.ar.us/rules.htm` | Regulatory orders |
| Forms | `https://www.aogc.state.ar.us/forms.htm` | Filing forms (W-2, B-19, etc.) |
| GIS Maps | `https://www.aogc.state.ar.us/gismaps.htm` | Well location maps |

### Channel 2: B-19 Production Reports

Arkansas operators file annual production reports on AOGC Form B-19. These
contain:
- Well identification (API number, well name, operator)
- Annual oil production (barrels)
- Annual gas production (MCF)
- Annual water production (barrels)
- Formation
- Well status

The AOGC may make B-19 data available through their online services portal.
Availability and format may vary.

### Channel 3: Cross-Reference Sources (Critical for Li/Mg Research)

Because AOGC's online data infrastructure is limited, the most useful data for
lithium/brine research comes from cross-referencing AOGC well records with:

| Source | What it provides | How to access |
|--------|-----------------|---------------|
| USGS Produced Waters Geochemical DB | Li, Mg, TDS, full brine chemistry for AR wells | `usgs-produced-waters` skill |
| USGS Mineral Commodity Summaries | National Li production/reserve estimates | `usgs-minerals` skill |
| Standard Lithium SEC Filings | Reserve estimates, DLE performance, pilot results | SEC EDGAR |
| ExxonMobil Lithium Announcements | Magnolia, AR project details | Company press releases |
| Equinor Lithium Project | South AR Smackover lease data | Company announcements |
| Academic Literature (Collins, 1976) | Foundational Smackover brine chemistry data | `usgs-pubs` or `doe-osti` skills |
| NETL EDX | DOE-funded research on Li from produced waters | `netl-edx` skill |

---

## Query Patterns

### Well Data Lookup

```bash
# The AOGC website restricts automated access (may return 403).
# For well data access:

# Option 1: Browser-based access
# Navigate to: https://www.aogc.state.ar.us/welldata.htm
# Search by API number, operator, county, or formation

# Option 2: AOGC GIS Maps
# Navigate to: https://www.aogc.state.ar.us/gismaps.htm
# Interactive map with well locations

# Option 3: Direct data request
# Contact AOGC directly:
#   Phone: (501) 683-5814
#   Email: aogc@aogc.state.ar.us
#   Address: 301 Natural Resources Drive, Suite 300, Little Rock, AR 72205
```

### Production Data

```bash
# B-19 annual production data access:
# Navigate to: https://www.aogc.state.ar.us/production.htm
# or: https://www.aogc.state.ar.us/onlineservices.htm

# Production data fields:
# - API Number
# - Well Name and Number
# - Operator
# - County
# - Formation
# - Annual Oil (BBL)
# - Annual Gas (MCF)
# - Annual Water (BBL)
# - Well Status
```

### Cross-Reference Workflow for Li/Mg Research

```bash
# The most effective workflow for Arkansas Smackover lithium research:

# Step 1: Get Smackover well locations from AOGC
# Browse AOGC well data or GIS maps for south AR Smackover wells
# Key counties: Columbia, Union, Lafayette, Miller, Hempstead, Nevada, Ouachita

# Step 2: Get brine chemistry from USGS
# Use the usgs-produced-waters skill to query the USGS Produced Waters
# Geochemical Database, filtering for:
#   STATE = "Arkansas"
#   FORMATION contains "Smackover"
# This returns Li, Mg, Ca, Na, Cl, TDS, pH, etc.

# Step 3: Get DLE project details from company filings
# Standard Lithium (NYSE: SLI) — SEC filings at:
curl -s "https://efts.sec.gov/LATEST/search-index?q=%22standard+lithium%22&dateRange=custom&startdt=2024-01-01&enddt=2025-12-31" \
  -H "Accept: application/json"

# Step 4: Get DOE research from NETL EDX
# Use the netl-edx skill to search for lithium extraction research
```

---

## Workflow

### Step 1 — Resolve Intent

| User wants... | Best channel |
|--------------|-------------|
| Specific well details | AOGC Well Data page (browser) |
| Production by well/county | AOGC B-19 Production Reports |
| Well locations on map | AOGC GIS Maps |
| Smackover brine chemistry | USGS Produced Waters DB (cross-reference) |
| DLE project status | Company SEC filings and press releases |
| Research literature | USGS Pubs, DOE OSTI, NETL EDX |
| Regulatory orders (spacing, pooling) | AOGC Rules and Orders page |

### Step 2 — Fetch Data

Due to AOGC's limited API infrastructure:
1. For well/production data: Use browser access to AOGC or request data directly
2. For brine chemistry: Use the `usgs-produced-waters` skill
3. For DLE project details: Query SEC EDGAR or company websites
4. For research: Use `usgs-pubs`, `doe-osti`, or `netl-edx` skills

### Step 3 — Parse and Integrate

The key value of this skill is integrating data across multiple sources:
- AOGC provides well locations, operators, and production volumes
- USGS provides brine geochemistry (Li, Mg, TDS)
- Company filings provide DLE economics and project timelines
- Academic literature provides formation characterization

### Step 4 — Produce Output

**Format: Raw Data Table + Narrative**

```
## South Arkansas Smackover Formation — Lithium Brine Summary

| County    | Wells | Avg Li (mg/L) | Max Li (mg/L) | Avg TDS (mg/L) | Key Operators        |
|-----------|-------|---------------|---------------|-----------------|---------------------|
| Columbia  | 45    | 285           | 410           | 290,000         | Standard Lithium    |
| Union     | 38    | 310           | 477           | 310,000         | ExxonMobil, Equinor |
| Lafayette | 22    | 240           | 350           | 275,000         | Standard Lithium    |
| Miller    | 15    | 180           | 290           | 250,000         | Various             |

**Summary:** The south Arkansas Smackover trend contains the highest-concentration
lithium brines in the United States. Union County wells average 310 mg/L Li, peaking
at 477 mg/L — well above the 100-150 mg/L economic threshold for DLE. Three major
companies have announced projects: Standard Lithium (SWA Lithium, Lanxess partnership),
ExxonMobil (Magnolia project, targeting 2027 production), and Equinor (Smackover
leases). Brine chemistry data from USGS Produced Waters Geochemical DB; well
counts from AOGC records.
```

---

## Arkansas Geographic Reference

### Key Counties for Oil and Gas / Lithium

| County | Region | Key Formations | Li/Mg Relevance |
|--------|--------|---------------|-----------------|
| Columbia | S AR | Smackover | Highest Li well count; Standard Lithium SWA project |
| Union | S AR | Smackover | Highest Li concentrations (up to 477 mg/L); ExxonMobil Magnolia |
| Lafayette | S AR | Smackover | Standard Lithium/Lanxess partnership area |
| Miller | SW AR | Smackover | Extension of Smackover trend |
| Hempstead | SW AR | Smackover | Western extent of Smackover Li zone |
| Nevada | S-central AR | Smackover | Moderate Li concentrations |
| Ouachita | S-central AR | Smackover | Northern boundary of Li-rich zone |
| Conway | Central AR | Fayetteville Shale | Gas production (low Li relevance) |
| Van Buren | N-central AR | Fayetteville Shale | Gas production (low Li relevance) |
| Cleburne | N-central AR | Fayetteville Shale | Gas production (low Li relevance) |

### The Smackover Formation in Arkansas

The Smackover Formation (Upper Jurassic) is a carbonate-evaporite sequence
deposited in a restricted marine basin. In south Arkansas, it produces from:

- **Depth:** 8,000-10,500 ft
- **Lithology:** Oolitic limestone grading to anhydrite
- **Brine characteristics:**
  - TDS: 200,000-350,000+ mg/L
  - Li: 100-477 mg/L (highest in U.S.)
  - Mg: 1,000-5,000+ mg/L
  - Br: 3,000-6,000 mg/L
  - Ca: 30,000-60,000 mg/L
  - Na: 60,000-90,000 mg/L
  - Cl: 150,000-200,000 mg/L
  - pH: 4.5-6.0 (acidic)
  - Temperature: 250-300 F at depth

### Active DLE Projects in Arkansas

| Company | Project | Location | Status | Target |
|---------|---------|----------|--------|--------|
| Standard Lithium | SWA Lithium (with Equinor) | Columbia/Lafayette counties | Pilot demonstrated; DFS in progress | 2026-2027 production |
| ExxonMobil | Magnolia Lithium | Union County (Magnolia area) | Leasing and development | 2027 first production |
| Equinor | AR Smackover (JV with SLI) | Columbia/Lafayette counties | Investment and development | 2026-2027 |
| Albemarle | Magnolia Bromine (brine operator) | Union/Columbia counties | Existing brine operations | Potential Li co-production |

---

## Error Handling

| Condition | Meaning | Action |
|-----------|---------|--------|
| 403 Forbidden | AOGC website blocks automated access | Use browser access; do not scrape |
| Page not found | URL structure changed | Check AOGC homepage for updated navigation |
| No data returned | Limited online data for older wells | Contact AOGC directly for historical records |
| GIS map not loading | Viewer compatibility issue | Try different browser; AOGC GIS may require specific browser support |
| Production data missing | Not all wells report annually | B-19 is annual; monthly data not available online |

---

## Caveats and Data Limitations

1. **Very limited API/online data:** The AOGC has the most limited online data
   infrastructure of any major lithium-relevant state. There is no REST API, and
   even web-based queries are limited compared to TX, NM, ND, or LA.
2. **403 blocks on automated access:** The AOGC website returns 403 errors for
   many automated requests, preventing programmatic data gathering.
3. **Annual production only:** Arkansas production reporting (B-19) is annual,
   not monthly. This limits time-series analysis granularity.
4. **No brine chemistry in AOGC data:** The AOGC does not track brine
   geochemistry. For Li/Mg/TDS data, the USGS Produced Waters Geochemical
   Database is essential.
5. **Small conventional O&G base:** Arkansas is a minor oil and gas state by
   volume. Its significance is almost entirely due to the Smackover lithium
   brine opportunity.
6. **Brine production vs. O&G production:** Some Smackover brine production
   in Arkansas is permitted as mineral extraction (for bromine by Albemarle/
   Lanxess) rather than oil and gas production. These wells may not appear in
   standard AOGC oil and gas databases.
7. **Rapidly evolving landscape:** The Arkansas Smackover lithium space is
   changing fast (2024-2026). Company projects, lease positions, and regulatory
   frameworks are in flux. Cross-reference with recent company filings for
   current status.
8. **Data request option:** For comprehensive well and production data, the
   AOGC accepts direct data requests. Contact: aogc@aogc.state.ar.us or
   (501) 683-5814.
