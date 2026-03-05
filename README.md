# claude-pnge

A Claude Code plugin for petroleum engineering research data access, built for WVU PNGE with a focus on lithium/magnesium recovery from produced waters and oilfield brines.

## What's Inside

**10 data skills** connecting to government and open data sources:

| Skill | Source | Key? | Status |
|-------|--------|------|--------|
| `pnge:eia-data` | EIA Open Data API v2 | Yes (free) | ✅ Working |
| `pnge:usgs-produced-waters` | USGS Produced Waters Geochemical DB v3.0 | No | ✅ Working |
| `pnge:usgs-minerals` | USGS Mineral Commodity Summaries | No | ✅ Working |
| `pnge:netl-edx` | DOE NETL Energy Data eXchange (CKAN) | Yes (free) | ✅ Working |
| `pnge:wvges-wells` | WV Geological & Economic Survey | No | ✅ Working |
| `pnge:boem-offshore` | BOEM Federal Offshore Data | No | ✅ Working |
| `pnge:fracfocus` | FracFocus Chemical Disclosure | No | ✅ Working |
| `pnge:epa-enviro` | EPA Envirofacts | Yes (free) | ✅ Working |
| `pnge:usgs-pubs` | USGS Publications Warehouse | No | ✅ Working |
| `pnge:doe-osti` | DOE OSTI Technical Reports | No | ✅ Working |

**1 research agent** for cross-source synthesis:

| Agent | Purpose |
|-------|---------|
| `li-mg-prospector` | Evaluate Li/Mg recovery potential across multiple data sources |

**1 slash command:**

| Command | Usage |
|---------|-------|
| `/prospect` | `/prospect Marcellus Shale WV` -- run the prospector agent |

## Install

### Claude Code (recommended)

```bash
# Direct from GitHub
claude plugin install pnge@OWNER/claude-pnge

# Or clone and install locally
git clone https://github.com/OWNER/claude-pnge.git
claude --plugin-dir ./claude-pnge
```

### Claude.ai

Each skill can be packaged as a `.skill` ZIP and uploaded individually:
Settings > Customize > Skills > Upload

## Setup

### API Keys

Only 3 of the 10 skills require an API key (all free). Seven skills work with no authentication at all.

See [`docs/TOKENS.md`](docs/TOKENS.md) for detailed step-by-step signup instructions for each service.

Quick setup using credential files (preferred):

```bash
# EIA -- https://www.eia.gov/opendata/
mkdir -p ~/.config/eia && chmod 700 ~/.config/eia
echo "api_key=YOUR_KEY" > ~/.config/eia/credentials && chmod 600 ~/.config/eia/credentials

# NETL EDX -- https://edx.netl.doe.gov/
mkdir -p ~/.config/netl-edx && chmod 700 ~/.config/netl-edx
echo "api_key=YOUR_KEY" > ~/.config/netl-edx/credentials && chmod 600 ~/.config/netl-edx/credentials

# EPA -- https://api.data.gov/signup/
mkdir -p ~/.config/epa && chmod 700 ~/.config/epa
echo "api_key=YOUR_KEY" > ~/.config/epa/credentials && chmod 600 ~/.config/epa/credentials
```

Or set environment variables (`EIA_API_KEY`, `NETL_EDX_API_KEY`, `EPA_API_KEY`). Credential files take priority over environment variables.

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
"What is the lithium concentration in Smackover brines?"
"Search NETL EDX for produced water treatment datasets"
"Show me USGS mineral commodity data for lithium production 2020-2024"
"Find BOEM offshore wells in the Gulf of Mexico"
"What UIC injection wells are permitted in Monongalia County WV?"
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
├── skills/                      # 10 data-access skills
│   ├── eia-data/
│   │   ├── SKILL.md
│   │   └── references/
│   ├── usgs-produced-waters/
│   │   ├── SKILL.md
│   │   └── references/
│   ├── usgs-minerals/
│   │   ├── SKILL.md
│   │   └── references/
│   ├── netl-edx/
│   │   ├── SKILL.md
│   │   └── references/
│   ├── wvges-wells/
│   │   ├── SKILL.md
│   │   └── references/
│   ├── boem-offshore/
│   │   ├── SKILL.md
│   │   └── references/
│   ├── fracfocus/
│   │   ├── SKILL.md
│   │   └── references/
│   ├── epa-enviro/
│   │   ├── SKILL.md
│   │   └── references/
│   ├── usgs-pubs/
│   │   ├── SKILL.md
│   │   └── references/
│   └── doe-osti/
│       ├── SKILL.md
│       └── references/
├── agents/                      # Cross-source research agents
│   └── li-mg-prospector.md
├── commands/                    # Slash commands
│   └── prospect.md
├── docs/                        # Extended documentation
│   ├── TOKENS.md                # API key acquisition guide
│   ├── DATA_SOURCES.md
│   └── PACKAGING.md
└── scripts/                     # Utility scripts
```

## License

Apache-2.0
