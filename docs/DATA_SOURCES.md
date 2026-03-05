# PNGE Research Data Sources & Skills/Agents Plan

**Project:** Petroleum Engineering Research — WVU Undergraduate
**Focus Area:** Lithium / Magnesium recovery from produced waters & brines
**Date:** 2026-03-05
**Status:** DRAFT — v0.1

---

## 1. Inventory of Data Sources

Sources are categorized by **access tier** and **domain relevance**. Priority is given to government, open/free, and student-accessible sources.

### Tier 1 — Government APIs (Programmatic, Free, Key-Based)

| # | Source | Agency | API Type | Key? | Li/Mg Relevance | PNGE Relevance |
|---|--------|--------|----------|------|-----------------|----------------|
| 1 | **EIA Open Data API v2** | DOE/EIA | REST/JSON | Yes (free) | Low — energy market context | **High** — production, prices, supply |
| 2 | **USGS ScienceBase** | USGS | REST/JSON | No (public items) | **High** — hosts Produced Waters DB | **High** — geologic data, wells |
| 3 | **USGS National Produced Waters Geochemical Database v3.0** | USGS | Bulk CSV + Tableau viewer | No | **Critical** — Li, Mg, Ba, Br, Cl, Sr in 115k+ samples | **Critical** — produced water chemistry |
| 4 | **USGS Mineral Commodity Summaries** | USGS/NMIC | Bulk CSV/JSON via data.usgs.gov | No | **Critical** — Li & Mg production, reserves, pricing | Medium — market context |
| 5 | **NETL Energy Data eXchange (EDX)** | DOE/NETL | REST (CKAN-based) | Yes (free acct) | **High** — ClaiMM critical minerals platform | **High** — reservoir eng, geothermal, CMM |
| 6 | **EPA Envirofacts** | EPA | REST/JSON | Yes (api.data.gov) | Low | Medium — discharge, compliance, UIC wells |
| 7 | **BOEM Data Center** | DOI/BOEM | Bulk download + ArcGIS REST | No | Low | **High** — OCS production, wells, leases, pipelines |
| 8 | **BSEE Data Center** | DOI/BSEE | Bulk download | No | Low | **High** — safety, incidents, inspections |
| 9 | **USGS Water Data APIs** | USGS/WMA | REST/JSON | No | Medium — water quality | Medium — streamflow, groundwater |
| 10 | **FracFocus Chemical Disclosure** | GWPC/IOGCC | REST API + bulk CSV | No | Medium — frac fluid chemistry | **High** — HF chemical disclosure |

### Tier 2 — State-Level Open Data (WV-Centric + Key States)

| # | Source | Agency | Access Method | Li/Mg Relevance | PNGE Relevance |
|---|--------|--------|---------------|-----------------|----------------|
| 11 | **WVGES Oil & Gas Well Data** | WV Geological Survey | Web scrape + ArcGIS REST | Medium — Appalachian brines | **Critical** — 145k+ WV wells, logs, production |
| 12 | **WVDEP Office of Oil & Gas** | WV DEP | Web query | Low | **High** — permits, production, compliance |
| 13 | **PA DEP Oil & Gas Reports** | PA DEP | Bulk download (CSV/Excel) | **High** — Marcellus Li data | **High** — Marcellus/Utica production |
| 14 | **TX RRC Production Data** | TX Railroad Commission | Bulk download + query | Medium | **High** — largest US producer |
| 15 | **AR Geological Survey** | AR DEEE | Various | **High** — Smackover Li brines | Medium — Smackover formation |

### Tier 3 — Academic & Institutional (Student-Accessible)

| # | Source | Provider | Access Method | Li/Mg Relevance | PNGE Relevance |
|---|--------|----------|---------------|-----------------|----------------|
| 16 | **OnePetro / SPE Papers** | SPE | Web search + WVU library proxy | **High** — Li extraction research | **Critical** — petroleum eng literature |
| 17 | **USGS Publications Warehouse** | USGS | REST API | **High** — Li/Mg reports | **High** — geoscience research |
| 18 | **DOE OSTI (Office of Scientific & Technical Info)** | DOE | REST API | **High** — DOE-funded CMM research | **High** — energy R&D reports |
| 19 | **Enverus/DrillingInfo** | Enverus | Licensed (check WVU access) | Medium | **Critical** — well-level analytics |
| 20 | **IHS Markit / S&P Global** | S&P Global | Licensed (check WVU access) | Medium | **High** — reserves, production analytics |

### Tier 4 — International & Supplementary

| # | Source | Provider | Access Method | Li/Mg Relevance | PNGE Relevance |
|---|--------|----------|---------------|-----------------|----------------|
| 21 | **UN Comtrade** | UN | REST API (free key) | **High** — Li/Mg trade flows | Low |
| 22 | **World Bank Commodities** | World Bank | REST API | Medium — pricing | Low |
| 23 | **NOAA Climate Data** | NOAA | REST API | Low | Low-Medium — environmental context |
| 24 | **OpenStreetMap / Overpass** | OSM | REST API | Low | Low — infrastructure mapping |

---

## 2. Architecture Decision: Skill vs. Agent

Before building, we need to clarify the distinction and decide per-source.

### Definitions (as used in this project)

```
SKILL:
  - A static instruction set (SKILL.md + reference files)
  - Claude reads it, then executes API calls using bash/code tools
  - Stateless between invocations
  - Best for: well-documented REST APIs with predictable patterns
  - Current example: eia-data skill

AGENT:
  - A long-running process with decision loops
  - Can chain multiple API calls, branch on results, retry on failure
  - Maintains state across a workflow
  - Best for: multi-step research tasks, cross-source correlation
  - Example: "Find all WV wells with Li > 100 mg/L, pull production
    history, cross-reference with EIA pricing, generate report"
```

### Recommendation Matrix

| Source | Build As | Rationale |
|--------|----------|-----------|
| EIA Open Data | **Skill** (exists) | Well-structured REST API, single-query pattern |
| USGS Produced Waters | **Skill** | Bulk data + targeted queries, predictable schema |
| USGS Mineral Commodities | **Skill** | Structured CSV endpoints, annual cadence |
| NETL EDX | **Skill** | CKAN REST API, search + download pattern |
| USGS ScienceBase | **Skill** | REST API, item-based queries |
| EPA Envirofacts | **Skill** | REST API, table-based queries |
| BOEM/BSEE Data | **Skill** | Bulk download + structured queries |
| FracFocus | **Skill** | API + bulk CSV, structured disclosure records |
| WVGES Well Data | **Skill** | ArcGIS REST + web scraping, well-by-well |
| USGS Publications | **Skill** | REST search API |
| DOE OSTI | **Skill** | REST search API |
| Cross-Source Research | **Agent** | Orchestrates multiple skills, decision logic |
| Li/Mg Prospect Evaluator | **Agent** | Multi-source correlation, scoring, reporting |

**Conclusion:** The EIA skill pattern is correct — each data source gets a **skill**. We then build 1–2 **agents** that orchestrate skills for complex research workflows. The agent concept maps to a higher-order skill that calls sub-skills.

---

## 3. Skill Development Plan

### Phase 1 — Core Data Skills (High Priority)

These directly serve Li/Mg + PNGE research.

#### 1.1 `usgs-produced-waters` — **CRITICAL PATH**

```yaml
name: usgs-produced-waters
trigger_phrases:
  - "produced water chemistry"
  - "brine geochemistry"
  - "lithium in produced water"
  - "formation water composition"
  - "oilfield brine"
data_source: USGS National Produced Waters Geochemical Database v3.0
access_method: Bulk CSV from ScienceBase (doi:10.5066/P9DSRCZJ)
api_key: none
output: Filtered data tables + geochemical summaries
credential_path: null
notes: |
  - 115k+ samples, 40+ constituent columns including Li, Mg, Ba, Br, Ca, Cl, K, Na, Sr
  - Version 3.0 (Dec 2023) added 23 datasets focused on high-Li brines
  - Appalachian Basin (Marcellus, Utica), Smackover, Williston, Permian coverage
  - Key for cross-referencing with WVGES well data by API number
  - Tableau viewer available but skill should work with raw CSV
certainty: HIGH — well-documented, publicly available, actively maintained
```

#### 1.2 `usgs-minerals` — Commodity Market Context

```yaml
name: usgs-minerals
trigger_phrases:
  - "lithium production"
  - "magnesium reserves"
  - "mineral commodity"
  - "critical minerals supply"
data_source: USGS Mineral Commodity Summaries + World Minerals Outlook
access_method: CSV/JSON from data.usgs.gov + ScienceBase
api_key: none
output: Production stats, reserve estimates, pricing trends
notes: |
  - Annual summaries for 90+ commodities including Li and Mg
  - World Minerals Outlook (2024-2029) covers Li & Mg capacity projections
  - Data releases as structured CSV on data.usgs.gov
  - Companion to produced waters skill for economic viability analysis
certainty: HIGH — authoritative government source, annual publication cycle
```

#### 1.3 `netl-edx` — DOE Research Data

```yaml
name: netl-edx
trigger_phrases:
  - "NETL data"
  - "EDX dataset"
  - "fossil energy research"
  - "ClaiMM critical minerals"
  - "carbon storage"
  - "geothermal data"
data_source: NETL Energy Data eXchange
access_method: CKAN REST API
api_key: Yes — free EDX account required
base_url: https://edx.netl.doe.gov/api/3/
credential_path: ~/.config/netl-edx/credentials
output: Dataset metadata, resource downloads, search results
notes: |
  - CKAN-based platform, standard CKAN API actions
  - Hosts ClaiMM (Critical Minerals and Materials) datasets
  - Key datasets: CMM characterization, reservoir models, produced water studies
  - NETL is in Morgantown, WV — potential for direct collaboration
  - Supports resource_search, package_search, package_show actions
certainty: HIGH — documented API, CKAN standard well understood
bias: DOE-funded research emphasis; may underrepresent private-sector data
```

### Phase 2 — Regulatory & Production Skills

#### 2.1 `wvges-wells` — West Virginia Well Data

```yaml
name: wvges-wells
trigger_phrases:
  - "West Virginia wells"
  - "WV oil gas well"
  - "Marcellus well WV"
  - "well log West Virginia"
  - "WV production data"
data_source: WVGES Oil & Gas Well Data System
access_method: ArcGIS REST MapServer + Pipeline web app
base_url: http://atlas.wvgs.wvnet.edu/arcgis/rest/services/OilGas/WVOG/MapServer
credential_path: null
output: Well locations, completions, production, formation tops
notes: |
  - 145k+ wells dating back 150 years
  - 8 data types: locations, completions, pays/shows, stratigraphy,
    production, plug, mechanical log catalog, samples/cores
  - ArcGIS REST services support query, identify, find operations
  - Pipeline/Pipeline-Plus web apps for individual well lookup by API number
  - Production data generally available from 1979 onward
  - Coordinate system: NAD83 UTM Zone 17
certainty: MEDIUM — ArcGIS REST is reliable; web scraping Pipeline is fragile
bias: WV-only; data quality varies for pre-1980 wells
```

#### 2.2 `boem-offshore` — Federal Offshore Data

```yaml
name: boem-offshore
trigger_phrases:
  - "offshore production"
  - "Gulf of Mexico wells"
  - "OCS lease"
  - "offshore platform"
  - "BOEM data"
data_source: BOEM Data Center
access_method: Bulk download (CSV/ZIP) + ArcGIS REST
base_url: https://www.data.boem.gov/
gis_url: https://gis.boem.gov/arcgis/rest/services/BOEM_BSEE/
output: Production volumes, well data, lease info, platform structures
notes: |
  - Covers all federal OCS operations (GoM, Pacific, Alaska, Atlantic)
  - Production data by lease, well (API), or operator
  - Raw data downloads available as delimited text files
  - ArcGIS REST services for spatial queries
  - Complements onshore state data
certainty: HIGH — well-structured government data center
```

#### 2.3 `fracfocus` — Hydraulic Fracturing Chemistry

```yaml
name: fracfocus
trigger_phrases:
  - "frac fluid"
  - "hydraulic fracturing chemicals"
  - "FracFocus"
  - "frac chemical disclosure"
  - "what chemicals were used"
data_source: FracFocus Chemical Disclosure Registry
access_method: REST API + bulk CSV download
base_url: https://api.fracfocus.org/
output: Chemical disclosures by well, operator, state
notes: |
  - 200k+ disclosures with chemical records
  - Data from 2011-present, 34 states
  - CAS numbers, trade names, supplier, purpose, concentrations
  - Bulk download available for research (2014+)
  - Open-FF project provides cleaned research-friendly version
  - Known data quality issues (see FracTracker analysis)
certainty: MEDIUM — API access confirmed; data completeness varies
bias: Industry self-reported; CBI exemptions hide some chemical identities
```

#### 2.4 `epa-enviro` — Environmental Compliance

```yaml
name: epa-enviro
trigger_phrases:
  - "EPA facility"
  - "environmental compliance"
  - "UIC injection well"
  - "discharge permit"
  - "NPDES"
  - "EPA data"
data_source: EPA Envirofacts + ECHO
access_method: REST API
base_url: https://enviro.epa.gov/enviro/efservice/
api_key: Yes (api.data.gov, free)
credential_path: ~/.config/epa/credentials
output: Facility info, compliance records, permit data
notes: |
  - Covers ICIS-AIR, RCRA, SDWIS, TRI, and more
  - UIC well data relevant to produced water disposal
  - Can query by facility, ZIP, county, or geographic area
  - ECHO system provides enforcement and compliance history
certainty: HIGH — well-documented REST API
```

### Phase 3 — Literature & Research Skills

#### 3.1 `usgs-pubs` — USGS Publications Warehouse

```yaml
name: usgs-pubs
trigger_phrases:
  - "USGS publication"
  - "USGS report"
  - "geological survey paper"
data_source: USGS Publications Warehouse
access_method: REST API
base_url: https://pubs.er.usgs.gov/pubs-services/
output: Publication metadata, abstracts, download links
certainty: HIGH
```

#### 3.2 `doe-osti` — DOE Technical Reports

```yaml
name: doe-osti
trigger_phrases:
  - "DOE report"
  - "technical report energy"
  - "OSTI"
data_source: DOE Office of Scientific & Technical Information
access_method: REST API
base_url: https://www.osti.gov/api/v1/
output: Report metadata, abstracts, full-text links
certainty: HIGH
```

### Phase 4 — Orchestration Agents

#### 4.1 `li-mg-prospector` — Cross-Source Research Agent

```yaml
name: li-mg-prospector
type: agent (orchestrates skills)
trigger_phrases:
  - "evaluate lithium potential"
  - "lithium in Appalachian brines"
  - "magnesium recovery feasibility"
  - "which formations have high lithium"
workflow:
  1. Query usgs-produced-waters for target formation/basin
  2. Filter for Li > threshold (e.g., 100 mg/L) or Mg targets
  3. Cross-reference well API numbers with wvges-wells for production context
  4. Pull commodity pricing from usgs-minerals
  5. Check EIA for regional energy market context
  6. Search usgs-pubs and doe-osti for relevant research
  7. Synthesize into structured report with maps and tables
output: Research report with geochemical analysis, economic context, citations
```

#### 4.2 `pnge-research-assistant` — General Research Agent

```yaml
name: pnge-research-assistant
type: agent (orchestrates skills)
trigger_phrases:
  - "research [topic] for my paper"
  - "find data about [formation/basin/process]"
  - "what does the data say about"
workflow:
  1. Classify query domain (production, geochemistry, regulation, economics)
  2. Select relevant skills
  3. Execute queries in parallel where possible
  4. Synthesize results with source attribution
  5. Flag data quality issues and certainty levels
output: Structured research summary with citations and data tables
```

---

## 4. Implementation Roadmap

### Credential Management Pattern (Shared)

All skills follow the EIA skill's credential resolution pattern:

```
~/.config/{service}/credentials  →  ENV_VAR  →  prompt user
```

Services requiring keys: EIA, NETL EDX, EPA (api.data.gov).
Services with no key: USGS (ScienceBase, Produced Waters, Pubs, Water), BOEM, BSEE, WVGES.

### Directory Structure

```
/mnt/skills/user/
├── eia-data/              # EXISTS — Phase 0
│   ├── SKILL.md
│   └── references/
├── usgs-produced-waters/  # Phase 1 — FIRST BUILD
│   ├── SKILL.md
│   └── references/
│       ├── schema.md
│       ├── sample_query.go
│       └── formations.md
├── usgs-minerals/         # Phase 1
│   ├── SKILL.md
│   └── references/
├── netl-edx/              # Phase 1
│   ├── SKILL.md
│   └── references/
├── wvges-wells/           # Phase 2
│   ├── SKILL.md
│   └── references/
├── boem-offshore/         # Phase 2
│   ├── SKILL.md
│   └── references/
├── fracfocus/             # Phase 2
│   ├── SKILL.md
│   └── references/
├── epa-enviro/            # Phase 2
│   ├── SKILL.md
│   └── references/
├── usgs-pubs/             # Phase 3
│   ├── SKILL.md
│   └── references/
├── doe-osti/              # Phase 3
│   ├── SKILL.md
│   └── references/
├── li-mg-prospector/      # Phase 4
│   ├── SKILL.md
│   └── references/
└── pnge-research-assistant/ # Phase 4
    ├── SKILL.md
    └── references/
```

### Build Order & Estimated Effort

| Phase | Skill | Priority | Effort | Dependencies |
|-------|-------|----------|--------|--------------|
| 0 | eia-data | Done | — | — |
| 1a | usgs-produced-waters | **P0** | Medium | Download + parse CSV schema |
| 1b | usgs-minerals | P1 | Low | Structured CSV endpoints |
| 1c | netl-edx | P1 | Medium | CKAN API, needs account |
| 2a | wvges-wells | P1 | High | ArcGIS REST reverse-eng |
| 2b | boem-offshore | P2 | Medium | Bulk file parsing |
| 2c | fracfocus | P2 | Medium | API docs + bulk CSV |
| 2d | epa-enviro | P2 | Low | Well-documented REST |
| 3a | usgs-pubs | P2 | Low | Standard REST |
| 3b | doe-osti | P2 | Low | Standard REST |
| 4a | li-mg-prospector | P1 | High | Phase 1 + 2a |
| 4b | pnge-research-assistant | P3 | High | All skills |

---

## 5. Certainty & Bias Notes

| Dimension | Assessment |
|-----------|------------|
| **Source availability** | HIGH certainty — all government APIs verified as active (March 2026) |
| **API stability** | MEDIUM — government APIs can change without notice; CKAN and ArcGIS REST are mature standards |
| **Data completeness** | VARIES — USGS Produced Waters is the gold standard for brine chemistry; state data quality varies significantly |
| **Li/Mg focus bias** | This plan is intentionally weighted toward Li/Mg in produced waters, which aligns with current DOE/USGS research priorities. Other PNGE topics (drilling optimization, reservoir simulation, EOR) are underserved by this plan. |
| **Geographic bias** | Appalachian Basin emphasis (WV/PA) due to WVU location and Marcellus/Utica relevance. Smackover (AR), Williston (ND), and Permian (TX/NM) are secondary. |
| **Temporal bias** | Most production data starts ~1979; geochemical data spans 1900–present but is sparse before 1960 |
| **Commercial data gap** | Enverus and IHS Markit are industry-standard but paywalled. Check if WVU PNGE department has institutional licenses. |

---

## 6. Next Steps

1. **Validate WVU access** — Check which commercial data sources (Enverus, IHS) the PNGE department already has
2. **Build `usgs-produced-waters` skill first** — Highest Li/Mg impact, well-documented data
3. **Register for free API keys** — NETL EDX, EPA api.data.gov
4. **Download and profile the Produced Waters v3.0 dataset** — Understand schema, coverage, quality
5. **Prototype the `li-mg-prospector` agent** — Even with partial skills, this validates the orchestration pattern

---

*This document is machine-parseable YAML within markdown. Skill definitions can be extracted programmatically for automated skill scaffolding.*
