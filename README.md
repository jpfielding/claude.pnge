# claude-pnge

A Claude Code plugin for petroleum engineering research data access, built for WVU PNGE with a focus on lithium/magnesium recovery from produced waters and oilfield brines.

## What's Inside

**22 skills** spanning data access, simulation, and visualization:

### Data Access Skills (20)

| # | Skill | Source | Key? | Status |
|---|-------|--------|------|--------|
| 1 | `pnge:eia-data` | EIA Open Data API v2 | Yes (free) | Working |
| 2 | `pnge:usgs-produced-waters` | USGS Produced Waters Geochemical DB v3.0 | No | Working |
| 3 | `pnge:usgs-minerals` | USGS Mineral Commodity Summaries | No | Working |
| 4 | `pnge:netl-edx` | DOE NETL Energy Data eXchange (CKAN) | Yes (free) | Working |
| 5 | `pnge:wvges-wells` | WV Geological & Economic Survey | No | Working |
| 6 | `pnge:boem-offshore` | BOEM Federal Offshore Data | No | Working |
| 7 | `pnge:fracfocus` | FracFocus Chemical Disclosure | No | Working |
| 8 | `pnge:epa-enviro` | EPA Envirofacts & ECHO | No | Working |
| 9 | `pnge:usgs-pubs` | USGS Publications Warehouse | No | Working |
| 10 | `pnge:doe-osti` | DOE OSTI Technical Reports | No | Working |
| 11 | `pnge:usgs-earthquakes` | USGS ComCat (FDSN) | No | Working |
| 12 | `pnge:usgs-waterdata` | USGS NWIS + Water Quality Portal | No | Working |
| 13 | `pnge:fred-prices` | Federal Reserve FRED | Yes (free) | Working |
| 14 | `pnge:epa-ghg` | EPA GHGRP (Subpart W) | No | Working |
| 15 | `pnge:worldbank-energy` | World Bank Open Data | No | Working |
| 16 | `pnge:comtrade-minerals` | UN Comtrade | Optional (free) | Working |
| 17 | `pnge:doe-geothermal` | DOE GDR / OpenEI | Yes (free) | Working |
| 18 | `pnge:crossref-doi` | CrossRef REST API | No | Working |
| 19 | `pnge:opec-data` | OPEC Production via EIA STEO | Yes (free) | Working |
| 20 | `pnge:iea-open` | IEA Free Datasets | No | Working |

### Simulation & Visualization Skills (2)

| Skill | Purpose |
|-------|---------|
| `pnge:tnav-reservoir-sim` | tNavigator-style reservoir simulation emulation (black oil, PVT, AHM, VFP, petrophysics) |
| `pnge:pnge-visual-explainer` | Generate self-contained HTML visualizations of PNGE concepts and data |

### Research Agents (3)

| Agent | Purpose |
|-------|---------|
| `li-mg-prospector` | Evaluate Li/Mg recovery potential across multiple data sources |
| `pnge-geopolitics` | Analyze energy geopolitics, supply chain risks, and global resource dynamics |
| `pnge-gis-mapper` | Generate interactive Leaflet.js maps for spatial data visualization |

### Slash Commands (1)

| Command | Usage |
|---------|-------|
| `/prospect` | `/prospect Marcellus Shale WV` -- run the prospector agent |

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

Only 4 of the 20 data skills require an API key (all free). Two more accept optional keys for higher rate limits. The remaining 14 data skills work with no authentication at all.

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
# Run the prospector agent on a formation
/prospect Marcellus Shale WV

# Or ask naturally -- the skills trigger on relevant queries

# --- Data Access ---
"What is the lithium concentration in Smackover brines?"
"Search NETL EDX for produced water treatment datasets"
"Show me USGS mineral commodity data for lithium production 2020-2024"
"Find BOEM offshore wells in the Gulf of Mexico"
"What UIC injection wells are permitted in Monongalia County WV?"

# --- Pricing & Economics ---
"Plot WTI crude oil prices for 2024"
"What is the current Henry Hub natural gas price?"
"Show lithium trade flows between Chile and the US"

# --- Environmental & Seismicity ---
"Show earthquakes near Oklahoma injection wells since 2020"
"What are the GHG emissions from petroleum facilities in WV?"
"Find USGS water quality monitoring stations near Morgantown"

# --- Global Context ---
"Compare OPEC production quotas vs actual output"
"What is global lithium demand by end-use sector?"
"Show World Bank energy access indicators for developing countries"

# --- Simulation ---
"Build a black oil simulation deck for a Marcellus well"
"Calculate PVT properties for a 0.7 SG gas at 4000 psia"
"Run Arps decline analysis on this production data"

# --- Geopolitics ---
"How do China's lithium refining dominance and DRC cobalt affect US supply chains?"
"Analyze the impact of OPEC+ production cuts on US shale economics"

# --- Mapping ---
"Map all Marcellus Shale wells in WV colored by lithium concentration"
"Create a heatmap of earthquake frequency near disposal wells in Oklahoma"

# --- Visualization ---
"Explain how Direct Lithium Extraction works with a visual diagram"
"Create an interactive chart comparing brine Li concentrations across US basins"
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
│   └── plugin.json              # Plugin manifest (name: pnge)
├── skills/                      # 22 skills total
│   ├── eia-data/                # EIA Open Data API v2
│   ├── usgs-produced-waters/    # USGS Produced Waters Geochemical DB
│   ├── usgs-minerals/           # USGS Mineral Commodity Summaries
│   ├── netl-edx/                # DOE NETL Energy Data eXchange
│   ├── wvges-wells/             # WV Geological & Economic Survey
│   ├── boem-offshore/           # BOEM Federal Offshore Data
│   ├── fracfocus/               # FracFocus Chemical Disclosure
│   ├── epa-enviro/              # EPA Envirofacts & ECHO
│   ├── usgs-pubs/               # USGS Publications Warehouse
│   ├── doe-osti/                # DOE OSTI Technical Reports
│   ├── usgs-earthquakes/        # USGS ComCat Earthquake Catalog
│   ├── usgs-waterdata/          # USGS NWIS + Water Quality Portal
│   ├── fred-prices/             # Federal Reserve FRED
│   ├── epa-ghg/                 # EPA GHGRP Emissions
│   ├── worldbank-energy/        # World Bank Open Data
│   ├── comtrade-minerals/       # UN Comtrade Trade Data
│   ├── doe-geothermal/          # DOE GDR / OpenEI Geothermal
│   ├── crossref-doi/            # CrossRef DOI/Citation API
│   ├── opec-data/               # OPEC Production via EIA STEO
│   ├── iea-open/                # IEA Free Datasets
│   ├── tnav/                    # tNavigator Simulation Emulation
│   └── pnge-visual-explainer/   # HTML Visualization Generator
├── agents/                      # Cross-source research agents
│   ├── li-mg-prospector.md      # Li/Mg recovery assessment
│   ├── pnge-geopolitics.md      # Energy geopolitics analysis
│   └── pnge-gis-mapper.md       # Interactive map generation
├── commands/                    # Slash commands
│   └── prospect.md
├── docs/                        # Extended documentation
│   ├── TOKENS.md                # API key acquisition guide
│   ├── DATA_SOURCES.md
│   └── PACKAGING.md
└── scripts/                     # Utility scripts
```

## Data Source Coverage

```
                    ┌─────────────────────────────────────┐
                    │        claude-pnge Plugin           │
                    │      22 Skills · 3 Agents           │
                    └──────────────┬──────────────────────┘
                                   │
        ┌──────────────────────────┼──────────────────────────┐
        │                          │                          │
   U.S. Federal                Global Sources           Tools & Agents
   ─────────────               ──────────────           ──────────────
   · EIA                       · World Bank              · tNavigator Sim
   · USGS (4 skills)           · UN Comtrade             · Visual Explainer
   · DOE NETL / OSTI / GDR    · IEA Open                · Li/Mg Prospector
   · EPA (2 skills)            · OPEC (via EIA)          · Geopolitics Agent
   · BOEM / BSEE              · CrossRef                 · GIS Mapper Agent
   · FracFocus                 · FRED                     · /prospect command
   · WVGES
```

## License

Apache-2.0
