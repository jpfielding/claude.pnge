# claude-pnge

A Claude Code plugin for petroleum engineering research data access, built for WVU PNGE with a focus on lithium/magnesium recovery from produced waters, completions engineering, wellbore stability, and sustainability.

## What's Inside

**34 skills** · **6 agents** · **6 commands**

### Data Access Skills (27)

| # | Skill | Source | Key? |
|---|-------|--------|------|
| 1 | `pnge:eia-data` | EIA Open Data API v2 | Yes (free) |
| 2 | `pnge:usgs-produced-waters` | USGS Produced Waters Geochemical DB v3.0 | No |
| 3 | `pnge:usgs-minerals` | USGS Mineral Commodity Summaries | No |
| 4 | `pnge:netl-edx` | DOE NETL Energy Data eXchange (CKAN) | Yes (free) |
| 5 | `pnge:wvges-wells` | WV Geological & Economic Survey | No |
| 6 | `pnge:padep-wells` | PA DEP Unconventional Well Registry (Socrata) | No |
| 7 | `pnge:boem-offshore` | BOEM Federal Offshore Data | No |
| 8 | `pnge:fracfocus` | FracFocus Chemical Disclosure | No |
| 9 | `pnge:epa-enviro` | EPA Envirofacts & ECHO | No |
| 10 | `pnge:epa-ghg` | EPA GHGRP Facility Emissions | No |
| 11 | `pnge:epa-ghgrp-subpartw` | EPA GHGRP Subpart W Oilfield Methane | No |
| 12 | `pnge:usgs-pubs` | USGS Publications Warehouse | No |
| 13 | `pnge:doe-osti` | DOE OSTI Technical Reports | No |
| 14 | `pnge:netl-carbon-storage` | NETL NATCARB Atlas / CCS Projects | Yes (free, optional) |
| 15 | `pnge:kggs-well-logs` | KGS Wireline Log Repository (LAS 2.0) | No |
| 16 | `pnge:macrostrat` | Macrostrat Formation Stratigraphy | No |
| 17 | `pnge:openalex` | OpenAlex Open-Access Literature | No |
| 18 | `pnge:usgs-earthquakes` | USGS ComCat (FDSN) | No |
| 19 | `pnge:usgs-waterdata` | USGS NWIS + Water Quality Portal | No |
| 20 | `pnge:fred-prices` | Federal Reserve FRED | Yes (free) |
| 21 | `pnge:worldbank-energy` | World Bank Open Data | No |
| 22 | `pnge:comtrade-minerals` | UN Comtrade | Optional (free) |
| 23 | `pnge:doe-geothermal` | DOE GDR / OpenEI | Yes (free) |
| 24 | `pnge:crossref-doi` | CrossRef REST API | No |
| 25 | `pnge:opec-data` | OPEC Production via EIA STEO | Yes (free) |
| 26 | `pnge:iea-open` | IEA Free Datasets | No |
| 27 | `pnge:wri-aqueduct` | WRI Aqueduct Water Risk | No |

### Computational & Simulation Skills (7)

| Skill | Purpose |
|-------|---------|
| `pnge:pnge-mechanics` | Statics, axial/beam stress, Lamé thick-wall cylinders, Mohr's circle |
| `pnge:frac-design` | PKN/KGD fracture models, Nolte-Smith analysis, proppant transport |
| `pnge:wellbore-stability` | Kirsch equations, mud weight window, breakout and fracture prediction |
| `pnge:mass-energy-balance` | Material/energy balances, combustion, flash calculation (Rachford-Rice) |
| `pnge:nist-webbook` | NIST thermodynamic properties for oil/gas fluids |
| `pnge:tnav` | tNavigator-style reservoir simulation emulation (black oil, PVT, decline) |
| `pnge:pnge-visual-explainer` | Generate self-contained HTML visualizations of PNGE concepts and data |

### Agents (6)

| Agent | Purpose |
|-------|---------|
| `li-mg-prospector` | Evaluate Li/Mg recovery potential across multiple data sources |
| `pnge-tutor` | Socratic tutor mapping PNGE/ChBE courses to relevant skills and real data |
| `pnge-pw-treatment` | Produced water treatment pathway assessment (DLE, ZLD, reuse, disposal) |
| `api-well-standards` | API 5CT/5C3 casing design, cementing standards, WV/PA regulatory requirements |
| `pnge-geopolitics` | Energy geopolitics, supply chain risks, and global resource dynamics |
| `pnge-gis-mapper` | Generate interactive Leaflet.js maps for spatial data visualization |

### Slash Commands (6)

| Command | Usage |
|---------|-------|
| `/prospect` | `/prospect Marcellus Shale WV` — run the Li/Mg prospector agent |
| `/formation-profile` | `/formation-profile Utica OH` — geological + geochemical profile |
| `/literature-review` | `/literature-review direct lithium extraction brines` — multi-source lit search |
| `/well-economics` | `/well-economics Marcellus WV 2024` — quick-look well economics with Li/Mg uplift |
| `/completions-design` | `/completions-design Marcellus Monongalia WV` — completions context and frac data |
| `/sustainability-profile` | `/sustainability-profile Permian Basin TX` — ESG / water / emissions summary |

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

Only 4 of the 27 data skills require an API key (all free). Two more accept optional keys for higher rate limits. The remaining 21 data skills work with no authentication at all.

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
```

Or set environment variables (`EIA_API_KEY`, `NETL_EDX_API_KEY`, `FRED_API_KEY`, `OPENEI_API_KEY`). Credential files take priority over environment variables.

### Optional Keys (higher rate limits)

```bash
# EPA -- https://api.data.gov/signup/ (works without key, key raises rate limit)
mkdir -p ~/.config/epa && chmod 700 ~/.config/epa
echo "api_key=YOUR_KEY" > ~/.config/epa/credentials && chmod 600 ~/.config/epa/credentials

# UN Comtrade -- https://comtradeapi.un.org/ (500 req/day without key)
mkdir -p ~/.config/comtrade && chmod 700 ~/.config/comtrade
echo "api_key=YOUR_KEY" > ~/.config/comtrade/credentials && chmod 600 ~/.config/comtrade/credentials
```

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

# --- Li/Mg Prospecting ---
"What is the lithium concentration in Smackover brines?"
"Evaluate DLE potential for Marcellus produced water in WV"
"Compare Li concentrations across Smackover, Marcellus, and Bakken"

# --- Completions & Well Engineering ---
"What casing grade should I use for a 9,000 ft Marcellus well?"
"Design a frac job for a Utica well with 3,000 ft lateral"
"What is the mud weight window for a Marcellus vertical well at 7,500 ft?"
"Calculate burst pressure for 4.5 in P-110 casing at 8,000 psi"

# --- Produced Water Treatment ---
"Evaluate treatment options for Marcellus brine with 180,000 mg/L TDS"
"Is DLE economically viable for a Marcellus water disposal operation?"
"What are the scale risks for mixing Marcellus PW with sulfate-rich water?"

# --- Engineering Calculations ---
"Calculate the stress on a rod with 50 kips axial load and 2 in diameter"
"What is the bending stress at midspan of a 20 ft beam with 10 kip load?"
"Flash a gas at 1000 psia, 150°F using given component compositions"
"What are the thermodynamic properties of CO2 at 2000 psia and 120°F?"

# --- Data Access ---
"Search NETL EDX for produced water treatment datasets"
"Show me USGS mineral commodity data for lithium production 2020-2024"
"Find PA DEP unconventional wells in Washington County with Marcellus permits"
"What are the Subpart W methane emissions for WV oil and gas facilities?"

# --- Environmental & Sustainability ---
"Show earthquakes near Oklahoma injection wells since 2020"
"What is the water stress index for the Permian Basin?"
"What is the CO2 storage capacity in the Appalachian basin?"

# --- Literature & Research ---
"Find DOE reports on direct lithium extraction from produced water"
"Search OpenAlex for papers on Marcellus Shale brine geochemistry since 2020"
"What does the USGS say about lithium in the Smackover Formation?"

# --- Geopolitics & Markets ---
"How do China's lithium refining dominance and DRC cobalt affect US supply chains?"
"Plot WTI crude oil prices and Henry Hub gas prices for 2024"
```

## Development

```bash
# Test locally without installing
claude --plugin-dir ./claude-pnge

# Validate all skills
claude plugin validate .

# After changes, restart Claude Code to pick up updates
```

## Project Structure

```
claude-pnge/
├── .claude-plugin/
│   └── plugin.json              # Plugin manifest (name: pnge, v0.2.0)
├── skills/                      # 34 skills total
│   │
│   ├── -- Data Access (27) --
│   ├── eia-data/                # EIA Open Data API v2
│   ├── usgs-produced-waters/    # USGS Produced Waters Geochemical DB v3.0
│   ├── usgs-minerals/           # USGS Mineral Commodity Summaries
│   ├── netl-edx/                # DOE NETL Energy Data eXchange
│   ├── netl-carbon-storage/     # NATCARB Atlas v5 CCS capacity
│   ├── wvges-wells/             # WV Geological & Economic Survey
│   ├── padep-wells/             # PA DEP Unconventional Well Registry
│   ├── boem-offshore/           # BOEM Federal Offshore Data
│   ├── fracfocus/               # FracFocus Chemical Disclosure
│   ├── epa-enviro/              # EPA Envirofacts & ECHO
│   ├── epa-ghg/                 # EPA GHGRP Facility Emissions
│   ├── epa-ghgrp-subpartw/      # Subpart W Oilfield Methane
│   ├── usgs-pubs/               # USGS Publications Warehouse
│   ├── doe-osti/                # DOE OSTI Technical Reports
│   ├── kggs-well-logs/          # KGS Wireline Logs (LAS 2.0)
│   ├── macrostrat/              # Macrostrat Formation Stratigraphy
│   ├── openalex/                # OpenAlex Open-Access Literature
│   ├── usgs-earthquakes/        # USGS ComCat Earthquake Catalog
│   ├── usgs-waterdata/          # USGS NWIS + Water Quality Portal
│   ├── fred-prices/             # Federal Reserve FRED
│   ├── worldbank-energy/        # World Bank Open Data
│   ├── comtrade-minerals/       # UN Comtrade Trade Data
│   ├── doe-geothermal/          # DOE GDR / OpenEI Geothermal
│   ├── crossref-doi/            # CrossRef DOI/Citation API
│   ├── opec-data/               # OPEC Production via EIA STEO
│   ├── iea-open/                # IEA Free Datasets
│   ├── wri-aqueduct/            # WRI Aqueduct Water Risk
│   │
│   └── -- Computational (7) --
│       ├── pnge-mechanics/      # Statics, Lamé cylinders, Mohr's circle
│       ├── frac-design/         # PKN/KGD fracture models, proppant transport
│       ├── wellbore-stability/  # Kirsch equations, mud weight window
│       ├── mass-energy-balance/ # Material/energy balance, flash calc
│       ├── nist-webbook/        # NIST thermodynamic properties
│       ├── tnav/                # Reservoir simulation emulation
│       └── pnge-visual-explainer/ # HTML visualization generator
│
├── agents/                      # 6 research and engineering agents
│   ├── li-mg-prospector.md      # Li/Mg recovery assessment
│   ├── pnge-tutor.md            # Socratic PNGE tutor
│   ├── pnge-pw-treatment.md     # Produced water treatment assessment
│   ├── api-well-standards.md    # API casing/cementing standards
│   ├── pnge-geopolitics.md      # Energy geopolitics analysis
│   └── pnge-gis-mapper.md       # Interactive map generation
│
├── commands/                    # 6 slash commands
│   ├── prospect.md
│   ├── formation-profile.md
│   ├── literature-review.md
│   ├── well-economics.md
│   ├── completions-design.md
│   └── sustainability-profile.md
│
└── docs/
    └── TOKENS.md                # API key acquisition guide
```

## Data Source Coverage

```
                    ┌──────────────────────────────────────────┐
                    │          claude-pnge Plugin v0.2.0       │
                    │   34 Skills · 6 Agents · 6 Commands      │
                    └─────────────────┬────────────────────────┘
                                      │
        ┌─────────────────────────────┼──────────────────────────┐
        │                             │                          │
   U.S. Federal                 Global Sources          Engineering Tools
   ─────────────                ──────────────          ─────────────────
   · EIA                        · World Bank             · Wellbore Stability
   · USGS (5 skills)            · UN Comtrade            · Frac Design
   · DOE NETL / OSTI / GDR     · IEA Open               · Mechanics/Statics
   · EPA (3 skills)             · OPEC (via EIA)         · Mass/Energy Balance
   · BOEM / BSEE               · CrossRef / OpenAlex    · NIST Thermodynamics
   · FracFocus                  · FRED                   · tNavigator Sim
   · WVGES / PA DEP             · WRI Aqueduct           · Visual Explainer
   · Macrostrat                 · Comtrade               · 6 Agents
   · KGS Well Logs                                       · 6 Commands
```

## License

Apache-2.0
