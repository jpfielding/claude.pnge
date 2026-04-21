# claude-pnge

A Claude Code plugin for petroleum engineering research data access, built for WVU PNGE with a focus on lithium/magnesium recovery from produced waters, completions engineering, wellbore stability, and sustainability.

## What's Inside

**76 skills** · **12 agents** · **12 commands**

### Data Access Skills (43)

#### Federal Agency Data (17)
| # | Skill | Source | Key? |
|---|-------|--------|------|
| 1 | `pnge:eia-data` | EIA Open Data API v2 | Yes (free) |
| 2 | `pnge:usgs-produced-waters` | USGS Produced Waters Geochemical DB v3.0 | No |
| 3 | `pnge:usgs-minerals` | USGS Mineral Commodity Summaries | No |
| 4 | `pnge:usgs-earthquakes` | USGS ComCat (FDSN) | No |
| 5 | `pnge:usgs-waterdata` | USGS NWIS + Water Quality Portal | No |
| 6 | `pnge:usgs-core-center` | USGS Core Research Center (ScienceBase) | No |
| 7 | `pnge:usgs-tnm` | USGS The National Map (DEM, geologic maps) | No |
| 8 | `pnge:netl-edx` | DOE NETL Energy Data eXchange (CKAN) | Yes (free) |
| 9 | `pnge:netl-carbon-storage` | NETL NATCARB Atlas / CCS Projects | Yes (free, optional) |
| 10 | `pnge:doe-geothermal` | DOE GDR / OpenEI | Yes (free) |
| 11 | `pnge:epa-regulatory` | EPA Envirofacts + ECHO + GHGRP (all subparts + Subpart W) | No (key optional) |
| 12 | `pnge:epa-treatability` | EPA Treatability Database (water treatment) | No |
| 13 | `pnge:boem-offshore` | BOEM Federal Offshore Data | No |
| 14 | `pnge:blm-mineral-records` | BLM Mineral & Land Records (GIS) | No |
| 15 | `pnge:fracfocus` | FracFocus Chemical Disclosure | No |
| 16 | `pnge:nasa-earthdata` | NASA Earthdata CMR (Landsat, Sentinel) | No (login for download) |
| 17 | `pnge:ejscreen-cejst-svi` | EPA EJScreen + CEQ CEJST + CDC/ATSDR SVI | No |

#### State Regulatory Data (12)
| # | Skill | Source | Key? |
|---|-------|--------|------|
| 18 | `pnge:wvges-wells` | WV Geological & Economic Survey | No |
| 19 | `pnge:padep-wells` | PA DEP Unconventional Well Registry (Socrata) | No |
| 20 | `pnge:odnr-wells` | Ohio DNR Oil and Gas Wells (Utica/Point Pleasant) | No |
| 21 | `pnge:tx-rrc` | Texas Railroad Commission (production, injection, permits) | No |
| 22 | `pnge:nm-ocd` | New Mexico Oil Conservation Division | No |
| 23 | `pnge:nd-dmr` | North Dakota Dept of Mineral Resources (Bakken) | No |
| 24 | `pnge:la-sonris` | Louisiana SONRIS (Smackover) | No |
| 25 | `pnge:ar-aogc` | Arkansas Oil and Gas Commission (Smackover DLE) | No |
| 26 | `pnge:ok-occ` | Oklahoma Corporation Commission (SWD, seismicity) | No |
| 27 | `pnge:calgem` | California CalGEM (former DOGGR; Salton Sea, San Joaquin) | No |
| 28 | `pnge:co-ecmc` | Colorado ECMC (former COGCC; DJ Basin / Niobrara) | No |
| 29 | `pnge:appalachia-mineral-parcels` | WV/PA/OH Mineral Parcels (ArcGIS + ODNR + OGRIP) | No |

#### Global & Economic Data (9)
| # | Skill | Source | Key? |
|---|-------|--------|------|
| 30 | `pnge:fred-prices` | Federal Reserve FRED | Yes (free) |
| 31 | `pnge:bls-data` | Bureau of Labor Statistics (PPI, CPI, employment) | Optional (free) |
| 32 | `pnge:bea-data` | Bureau of Economic Analysis (GDP, regional income) | Yes (free) |
| 33 | `pnge:census-data` | U.S. Census Bureau (ACS demographics, EJ) | Yes (free) |
| 34 | `pnge:worldbank-energy` | World Bank Open Data | No |
| 35 | `pnge:comtrade-minerals` | UN Comtrade | Optional (free) |
| 36 | `pnge:iea-open` | IEA Free Datasets | No |
| 37 | `pnge:wri-aqueduct` | WRI Aqueduct Water Risk | No |
| 38 | `pnge:ospar-discharges` | OSPAR Offshore Produced Water Discharges | No |

#### Literature & Patents (5)
| # | Skill | Source | Key? |
|---|-------|--------|------|
| 39 | `pnge:pnge-literature` | OpenAlex + CrossRef + USGS Pubs + DOE OSTI (DOI dedup) | No |
| 40 | `pnge:datacite-doi` | DataCite DOI Registry (datasets, data releases) | No |
| 41 | `pnge:kggs-well-logs` | KGS Wireline Log Repository (LAS 2.0) | No |
| 42 | `pnge:macrostrat` | Macrostrat Formation Stratigraphy | No |
| 43 | `pnge:patentsview` | USPTO / PatentsView (DLE patent landscape) | No |

### Computational & Simulation Skills (33)

#### Production & Completions Engineering (21)
| Skill | Purpose |
|-------|---------|
| `pnge:pnge-mechanics` | Statics, axial/beam stress, Lame thick-wall cylinders, Mohr's circle |
| `pnge:frac-design` | PKN/KGD fracture models, Nolte-Smith analysis, proppant transport |
| `pnge:wellbore-stability` | Kirsch equations, mud weight window, breakout and fracture prediction |
| `pnge:petrophysics` | Log interpretation: Vsh, porosity, Sw (Archie/Simandoux), brittleness index |
| `pnge:artificial-lift` | Rod pump, ESP sizing, gas lift design, plunger lift, liquid loading |
| `pnge:flow-assurance` | Hydrates (Katz/Hammerschmidt), CO2 corrosion, H2S sour service, wax/scale |
| `pnge:tubing-design` | Lubinski four-effect force analysis, buckling, seal assembly, velocity strings |
| `pnge:perforation-design` | Karakas-Tariq skin, phasing, underbalance criteria, limited entry diversion |
| `pnge:surface-facilities` | Separator sizing, TEG dehy, compression HP, backpressure effects |
| `pnge:rta-production` | Arps decline curves, EUR estimation, flowing material balance (Blasingame) |
| `pnge:well-test-analysis` | Horner plot, skin factor, Bourdet derivative, wellbore storage, Ei solution |
| `pnge:matrix-acidizing` | HCl carbonate design, HF/HCl sandstone design, Hawkins skin, Damkohler |
| `pnge:completion-diagnostics` | DFIT/minifrac, ISIP/closure picking, step-rate, cluster efficiency, pressure diagnostics |
| `pnge:nodal-analysis-multiphase` | IPR/VLP matching, tubing/choke sensitivity, compression impact, multiphase nodal analysis |
| `pnge:production-chemistry` | Emulsions, incompatibility, squeeze design, cleanup, corrosion program surveillance |
| `pnge:well-integrity-barriers` | SCP/annulus pressure triage, MIT interpretation, leak-path screening, barrier review |
| `pnge:petroleum-pvt` | Bubble point, Rs, Bo, Bg, separator shrinkage, condensate dropout screening |
| `pnge:stage-treatment-analysis` | Local frac stage export parsing, stage normalization, ISIP/screenout screening, cross-stage comparison |
| `pnge:production-surveillance` | SCADA/historian/test-separator trend analysis, anomaly detection, candidate ranking |
| `pnge:pvt-report-review` | PVT lab report extraction, QC, and black-oil input packaging |
| `pnge:integrity-log-review` | MIT, CBL/VDL, noise, temperature, and annulus report review for leak-path evidence |

#### Simulation & Reference Tools (5)
| Skill | Purpose |
|-------|---------|
| `pnge:mass-energy-balance` | Material/energy balances, combustion, flash calculation (Rachford-Rice) |
| `pnge:nist-webbook` | NIST thermodynamic properties for oil/gas fluids |
| `pnge:tnav` | tNavigator-style reservoir simulation emulation (black oil, PVT, decline) |
| `pnge:pnge-visual-explainer` | Generate self-contained HTML visualizations of PNGE concepts and data |
| `pnge:phreeqc-geochem` | PHREEQC brine speciation, saturation indices, mineral scaling prediction |

#### Engineering Science Tutoring (7)
| Skill | Purpose | WVU Course |
|-------|---------|-----------|
| `pnge:fluid-mechanics` | Reynolds number, Darcy-Weisbach, Bernoulli, Colebrook-White, pump sizing | ChBE 311 |
| `pnge:reaction-engineering` | CSTR/PFR/batch design, Arrhenius, Levenspiel plot, adiabatic T rise | ChBE 321 |
| `pnge:thermo-eos` | Peng-Robinson/SRK EOS, Z-factor, fugacity, VLE, Rachford-Rice flash | ChBE 231 |
| `pnge:heat-transfer` | Conduction, convection, overall U, LMTD, NTU, transient heating/cooling | ChBE transport / heat transfer |
| `pnge:mass-transfer-separations` | Diffusion, mass-transfer coefficients, HTU/NTU, absorption, distillation screening | ChBE separations |
| `pnge:aqueous-chemistry-electrochem` | pH, buffers, alkalinity, hardness, Nernst, Faraday, water chemistry | ChBE / water treatment |
| `pnge:materials-fracture-mechanics` | Stress intensity, fracture toughness, fatigue, Paris law, failure screening | MAE materials / integrity |

### Agents (12)

| Agent | Purpose |
|-------|---------|
| `li-mg-prospector` | Evaluate Li/Mg recovery potential across multiple data sources |
| `pnge-tutor` | Socratic tutor mapping PNGE/ChBE courses to relevant skills and real data |
| `pnge-pw-treatment` | Produced water treatment pathway assessment (DLE, ZLD, reuse, disposal) |
| `api-well-standards` | API 5CT/5C3 casing design, cementing standards, WV/PA regulatory requirements |
| `pnge-geopolitics` | Energy geopolitics, supply chain risks, and global resource dynamics |
| `pnge-gis-mapper` | Generate interactive Leaflet.js maps for spatial data visualization |
| `regulatory-disposal-analyst` | Cross-state UIC disposal analysis, seismicity, MIT compliance |
| `dle-patent-scout` | DLE patent landscape by technology class, assignee tracking, white space |
| `water-chem-qaqc` | Unit harmonization, charge balance, censored values, formation normalization |
| `tea-lca-analyst` | Techno-economic screening and life cycle analysis for DLE projects |
| `lab-method-planner` | Sampling plans, ICP-OES/ICP-MS method selection, QA/QC design |
| `research-synthesis-writer` | Citation-ready tables, SPE/ACS formatting, poster figure packages |

### Slash Commands (12)

| Command | Usage |
|---------|-------|
| `/prospect` | `/prospect Marcellus Shale WV` -- run the Li/Mg prospector agent |
| `/formation-profile` | `/formation-profile Utica OH` -- geological + geochemical profile |
| `/literature-review` | `/literature-review direct lithium extraction brines` -- multi-source lit search |
| `/well-economics` | `/well-economics Marcellus WV 2024` -- quick-look well economics with Li/Mg uplift |
| `/completions-design` | `/completions-design Marcellus Monongalia WV` -- completions context and frac data |
| `/sustainability-profile` | `/sustainability-profile Permian Basin TX` -- ESG / water / emissions summary |
| `/regulatory-screen` | `/regulatory-screen Marcellus WV` -- cross-state regulatory and disposal screening |
| `/water-chem-compare` | `/water-chem-compare Marcellus vs Smackover` -- compare brine chemistry |
| `/disposal-screen` | `/disposal-screen Tyler County WV` -- disposal well capacity and seismicity risk |
| `/patent-landscape` | `/patent-landscape sorbent DLE lithium` -- DLE patent landscape analysis |
| `/tea-dle` | `/tea-dle Marcellus WV 150 mg/L Li` -- techno-economic DLE screening |
| `/doctor` | `/doctor` -- plugin health check (API keys, endpoint reachability, skill status) |

## Install

### Claude Code (recommended)

```bash
# Direct from GitHub
claude plugin install pnge@jpfielding/claude.pnge

# Or clone and install locally
git clone https://github.com/jpfielding/claude.pnge.git
claude --plugin-dir ./claude-pnge
```

### Claude.ai

Each skill can be packaged as a `.skill` ZIP and uploaded individually:
Settings > Customize > Skills > Upload

## Setup

### API Keys

Only 6 of the 43 data skills require an API key (all free). Three more accept optional keys for higher rate limits. The remaining 34 data skills work with no authentication at all.

See [`docs/TOKENS.md`](docs/TOKENS.md) for detailed step-by-step signup instructions for each service.

Quick setup using credential files (preferred):

```bash
# EIA -- https://www.eia.gov/opendata/
mkdir -p ~/.config/eia && chmod 700 ~/.config/eia
echo "api_key=YOUR_KEY" > ~/.config/eia/credentials && chmod 600 ~/.config/eia/credentials

# NETL EDX -- https://edx.netl.doe.gov/
mkdir -p ~/.config/netl-edx && chmod 700 ~/.config/netl-edx
echo "api_key=YOUR_KEY" > ~/.config/netl-edx/credentials && chmod 600 ~/.config/netl-edx/credentials

# FRED -- https://fred.stlouisfed.org/docs/api/api_key.html
mkdir -p ~/.config/fred && chmod 700 ~/.config/fred
echo "api_key=YOUR_KEY" > ~/.config/fred/credentials && chmod 600 ~/.config/fred/credentials

# OpenEI (for DOE GDR geothermal) -- https://openei.org/services/api/signup/
mkdir -p ~/.config/openei && chmod 700 ~/.config/openei
echo "api_key=YOUR_KEY" > ~/.config/openei/credentials && chmod 600 ~/.config/openei/credentials

# BEA -- https://apps.bea.gov/API/signup/
mkdir -p ~/.config/bea && chmod 700 ~/.config/bea
echo "api_key=YOUR_KEY" > ~/.config/bea/credentials && chmod 600 ~/.config/bea/credentials

# Census -- https://api.census.gov/data/key_signup.html
mkdir -p ~/.config/census && chmod 700 ~/.config/census
echo "api_key=YOUR_KEY" > ~/.config/census/credentials && chmod 600 ~/.config/census/credentials
```

Or set environment variables (`EIA_API_KEY`, `NETL_EDX_API_KEY`, `FRED_API_KEY`, `OPENEI_API_KEY`, `BEA_API_KEY`, `CENSUS_API_KEY`). Credential files take priority over environment variables.

### Optional Keys (higher rate limits)

```bash
# EPA -- https://api.data.gov/signup/ (works without key, key raises rate limit)
mkdir -p ~/.config/epa && chmod 700 ~/.config/epa
echo "api_key=YOUR_KEY" > ~/.config/epa/credentials && chmod 600 ~/.config/epa/credentials

# UN Comtrade -- https://comtradeapi.un.org/ (500 req/day without key)
mkdir -p ~/.config/comtrade && chmod 700 ~/.config/comtrade
echo "api_key=YOUR_KEY" > ~/.config/comtrade/credentials && chmod 600 ~/.config/comtrade/credentials

# BLS -- https://data.bls.gov/registrationEngine/ (works without key, key raises rate limit)
mkdir -p ~/.config/bls && chmod 700 ~/.config/bls
echo "api_key=YOUR_KEY" > ~/.config/bls/credentials && chmod 600 ~/.config/bls/credentials
```

### Preflight Check

Run `/doctor` after installation to verify API keys, endpoint reachability, and skill status.

### WVU-Specific

Check with your PNGE department for access to:
- **Enverus/DrillingInfo** -- WVU may have an institutional license
- **IHS Markit / S&P Global** -- check library databases
- **OnePetro** -- available through WVU Library proxy

## Usage

```bash
# --- Slash Commands ---
/prospect Marcellus Shale WV
/formation-profile Utica OH
/literature-review direct lithium extraction produced water
/well-economics Marcellus Monongalia WV 2024
/completions-design Marcellus Monongalia WV
/sustainability-profile Permian Basin TX
/regulatory-screen Smackover AR
/water-chem-compare Marcellus vs Smackover
/disposal-screen Tyler County WV
/patent-landscape sorbent DLE lithium
/tea-dle Marcellus WV 150 mg/L Li
/doctor

# --- Li/Mg Prospecting ---
"What is the lithium concentration in Smackover brines?"
"Evaluate DLE potential for Marcellus produced water in WV"
"Compare Li concentrations across Smackover, Marcellus, and Bakken"

# --- State Regulatory Data ---
"Show Texas RRC production data for the Permian Basin"
"Find injection wells in New Mexico Lea County"
"What is the Bakken production trend from North Dakota DMR?"
"Search Louisiana SONRIS for Smackover wells in Union Parish"
"What DLE projects are active in the Arkansas Smackover?"
"Oklahoma SWD wells near recent M3+ earthquakes in the Arbuckle"
"California Salton Sea Known Geothermal Resource Area Li activity"
"Colorado DJ Basin / Niobrara horizontal well permits"

# --- Completions & Well Engineering ---
"What casing grade should I use for a 9,000 ft Marcellus well?"
"Design a frac job for a Utica well with 3,000 ft lateral"
"Estimate closure pressure and net pressure from this DFIT falloff"
"Run a nodal analysis for a 7,500 ft gas well with 900 psi WHP"
"Diagnose sustained casing pressure on the A-annulus"

# --- DLE Patent & Economics ---
"What patents does Standard Lithium hold for sorbent DLE?"
"Run a techno-economic screen for DLE from Marcellus brine at 150 mg/L Li"
"Compare DLE technology classes: sorbent vs membrane vs electrochemical"

# --- Water Chemistry & Lab Planning ---
"Compare Marcellus and Smackover brine chemistry side by side"
"Run PHREEQC speciation and scaling prediction for a Smackover brine"
"Design a sampling plan for produced water characterization"
"Check charge balance on these water analyses"

# --- Research Output ---
"Generate a citation table for DLE papers since 2020 in SPE format"
"Create a poster figure package for Marcellus Li concentrations"

# --- Environmental & Sustainability ---
"Show earthquakes near Oklahoma injection wells since 2020"
"What is the water stress index for the Permian Basin?"
"What is the CO2 storage capacity in the Appalachian basin?"
"How does U.S. produced water management compare to OSPAR standards?"
"Pull EJScreen + CEJST + SVI indicators for Appalachian energy counties"

# --- Economic Context ---
"Plot WTI crude oil prices and Henry Hub gas prices for 2024"
"What is the PPI trend for crude petroleum extraction?"
"Show county-level income data for Appalachian energy counties"
```

## Development

```bash
# Test locally without installing
claude --plugin-dir ./claude-pnge

# Validate all skills
claude plugin validate .

# Preflight check
/doctor

# After changes, restart Claude Code to pick up updates
```

## Project Structure

```
claude-pnge/
├── .claude-plugin/
│   └── plugin.json              # Plugin manifest (name: pnge, v0.9.0)
├── skills/                      # 76 skills total
│   │
│   ├── -- Federal Data (17) --
│   ├── eia-data/                # EIA Open Data API v2
│   ├── usgs-produced-waters/    # USGS Produced Waters Geochemical DB v3.0
│   ├── usgs-minerals/           # USGS Mineral Commodity Summaries
│   ├── usgs-earthquakes/        # USGS ComCat Earthquake Catalog
│   ├── usgs-waterdata/          # USGS NWIS + Water Quality Portal
│   ├── usgs-core-center/        # USGS Core Research Center
│   ├── usgs-tnm/                # USGS The National Map (DEM, geologic maps)
│   ├── netl-edx/                # DOE NETL Energy Data eXchange
│   ├── netl-carbon-storage/     # NATCARB Atlas v5 CCS capacity
│   ├── doe-geothermal/          # DOE GDR / OpenEI Geothermal
│   ├── epa-regulatory/          # EPA Envirofacts + ECHO + GHGRP (incl. Subpart W)
│   ├── epa-treatability/        # EPA Treatability Database
│   ├── boem-offshore/           # BOEM Federal Offshore Data
│   ├── blm-mineral-records/     # BLM Mineral & Land Records
│   ├── fracfocus/               # FracFocus Chemical Disclosure
│   ├── nasa-earthdata/          # NASA Earthdata CMR (Landsat, Sentinel)
│   ├── ejscreen-cejst-svi/      # EPA EJScreen + CEJST + CDC/ATSDR SVI
│   │
│   ├── -- State Regulatory (12) --
│   ├── wvges-wells/             # WV Geological & Economic Survey
│   ├── padep-wells/             # PA DEP Unconventional Well Registry
│   ├── odnr-wells/              # Ohio DNR Wells (Utica/Point Pleasant)
│   ├── tx-rrc/                  # Texas Railroad Commission
│   ├── nm-ocd/                  # New Mexico Oil Conservation Division
│   ├── nd-dmr/                  # North Dakota Dept of Mineral Resources
│   ├── la-sonris/               # Louisiana SONRIS
│   ├── ar-aogc/                 # Arkansas Oil and Gas Commission
│   ├── ok-occ/                  # Oklahoma Corporation Commission (SWD/seismicity)
│   ├── calgem/                  # California CalGEM (former DOGGR)
│   ├── co-ecmc/                 # Colorado ECMC (former COGCC; DJ/Niobrara)
│   ├── appalachia-mineral-parcels/ # WV/PA/OH mineral parcel consolidation
│   │
│   ├── -- Global & Economic (9) --
│   ├── fred-prices/             # Federal Reserve FRED
│   ├── bls-data/                # Bureau of Labor Statistics
│   ├── bea-data/                # Bureau of Economic Analysis
│   ├── census-data/             # U.S. Census Bureau
│   ├── worldbank-energy/        # World Bank Open Data
│   ├── comtrade-minerals/       # UN Comtrade Trade Data
│   ├── iea-open/                # IEA Free Datasets
│   ├── wri-aqueduct/            # WRI Aqueduct Water Risk
│   ├── ospar-discharges/        # OSPAR Offshore Produced Water
│   │
│   ├── -- Literature & Patents (5) --
│   ├── pnge-literature/         # Federated OpenAlex + CrossRef + USGS Pubs + OSTI
│   ├── datacite-doi/            # DataCite DOI Registry (dataset DOIs)
│   ├── kggs-well-logs/          # KGS Wireline Logs (LAS 2.0)
│   ├── macrostrat/              # Macrostrat Formation Stratigraphy
│   ├── patentsview/             # USPTO / PatentsView DLE Patents
│   │
│   └── -- Computational (33) --
│       ├── pnge-mechanics/      # Statics, Lame cylinders, Mohr's circle
│       ├── frac-design/         # PKN/KGD fracture models, proppant transport
│       ├── wellbore-stability/  # Kirsch equations, mud weight window
│       ├── petrophysics/        # Log interpretation, Archie, brittleness
│       ├── artificial-lift/     # Rod pump, ESP, gas lift, plunger lift
│       ├── flow-assurance/      # Hydrates, CO2 corrosion, H2S, wax/scale
│       ├── tubing-design/       # Lubinski four-effect, buckling, seal assy
│       ├── perforation-design/  # Karakas-Tariq skin, limited entry
│       ├── surface-facilities/  # Separator, TEG dehy, compression
│       ├── rta-production/      # Arps DCA, EUR, flowing material balance
│       ├── well-test-analysis/  # Horner plot, skin, Bourdet derivative
│       ├── matrix-acidizing/    # HCl/HF design, Hawkins skin, Damkohler
│       ├── completion-diagnostics/ # DFIT, ISIP, closure, step-rate
│       ├── nodal-analysis-multiphase/ # IPR/VLP, tubing/choke sensitivity
│       ├── production-chemistry/ # Emulsions, squeeze jobs, cleanup
│       ├── well-integrity-barriers/ # SCP, MIT, barrier diagnostics
│       ├── petroleum-pvt/       # Bubble point, Rs, Bo, Bg, shrinkage
│       ├── stage-treatment-analysis/ # Stage CSV parsing and diagnostics
│       ├── production-surveillance/ # SCADA/test-separator surveillance
│       ├── pvt-report-review/   # PVT lab report extraction and QC
│       ├── integrity-log-review/ # MIT/log package review
│       ├── mass-energy-balance/ # Material/energy balance, flash calc
│       ├── nist-webbook/        # NIST thermodynamic properties
│       ├── tnav/                # Reservoir simulation emulation
│       ├── pnge-visual-explainer/ # HTML visualization generator
│       ├── phreeqc-geochem/     # PHREEQC brine speciation, scaling prediction
│       ├── fluid-mechanics/     # Reynolds, Darcy-Weisbach (ChBE 311)
│       ├── reaction-engineering/ # CSTR/PFR/batch, Arrhenius (ChBE 321)
│       ├── thermo-eos/          # PR/SRK EOS, fugacity, VLE (ChBE 231)
│       ├── heat-transfer/       # Conduction, convection, exchangers
│       ├── mass-transfer-separations/ # Diffusion, HTU/NTU, distillation
│       ├── aqueous-chemistry-electrochem/ # pH, alkalinity, Nernst, Faraday
│       └── materials-fracture-mechanics/ # KIC, Paris law, fatigue
│
├── agents/                      # 12 research and engineering agents
│   ├── li-mg-prospector.md      # Li/Mg recovery assessment
│   ├── pnge-tutor.md            # Socratic PNGE tutor
│   ├── pnge-pw-treatment.md     # Produced water treatment assessment
│   ├── api-well-standards.md    # API casing/cementing standards
│   ├── pnge-geopolitics.md      # Energy geopolitics analysis
│   ├── pnge-gis-mapper.md       # Interactive map generation
│   ├── regulatory-disposal-analyst.md  # Cross-state disposal/UIC analysis
│   ├── dle-patent-scout.md      # DLE patent landscape analysis
│   ├── water-chem-qaqc.md       # Water chemistry QA/QC
│   ├── tea-lca-analyst.md       # Techno-economic / LCA screening
│   ├── lab-method-planner.md    # Sampling plans and analytical methods
│   └── research-synthesis-writer.md    # Citation tables, poster figures
│
├── commands/                    # 12 slash commands
│   ├── prospect.md
│   ├── formation-profile.md
│   ├── literature-review.md
│   ├── well-economics.md
│   ├── completions-design.md
│   ├── sustainability-profile.md
│   ├── regulatory-screen.md
│   ├── water-chem-compare.md
│   ├── disposal-screen.md
│   ├── patent-landscape.md
│   ├── tea-dle.md
│   └── doctor.md
│
└── docs/
    ├── TOKENS.md                # API key acquisition guide
    ├── DATA_SOURCES.md          # Data source reference
    └── PACKAGING.md             # Plugin packaging guide
```

## Data Source Coverage

```
                    ┌──────────────────────────────────────────┐
                    │          claude-pnge Plugin v0.9.0       │
                    │   76 Skills · 12 Agents · 12 Commands    │
                    └─────────────────┬────────────────────────┘
                                      │
        ┌─────────────────────────────┼──────────────────────────┐
        │                             │                          │
   U.S. Federal                State Regulatory          Engineering Tools
   ─────────────               ────────────────          ─────────────────
   · EIA                       · WV (WVGES)              · Wellbore Stability
   · USGS (6 skills)           · PA (DEP)                · Frac Design
   · DOE NETL / GDR            · OH (ODNR)               · Mechanics/Statics
   · EPA Regulatory            · TX (RRC)                · Mass/Energy Balance
   · EPA Treatability          · NM (OCD)                · NIST Thermodynamics
   · BOEM / BSEE               · ND (DMR)                · tNavigator Sim
   · BLM                       · LA (SONRIS)             · PHREEQC Geochem
   · FracFocus                 · AR (AOGC)               · Petrophysics
   · NASA Earthdata            · OK (OCC)                · Artificial Lift
   · EJScreen/CEJST/SVI        · CA (CalGEM)             · Flow Assurance
                               · CO (ECMC)               · Tubing Design
   Global/Economic             · Appalachia mineral      · Perf Design
   ──────────────                parcels (WV/PA/OH)      · Surface Facilities
   · World Bank                                          · RTA / Decline Curves
   · UN Comtrade             Research Tools              · Well Test Analysis
   · IEA Open                ──────────────              · Matrix Acidizing
   · FRED                    · pnge-literature           · Completion Diagnostics
   · BLS / BEA / Census      · datacite-doi              · Nodal Analysis
   · WRI Aqueduct            · PatentsView               · Production Chemistry
   · OSPAR                   · KGS Well Logs             · Well Integrity
                             · Macrostrat                 · PVT + 7 Tutoring
```

## License

Apache-2.0
