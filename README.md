# claude-pnge

A **Claude Code marketplace** of petroleum-engineering research plugins for WVU PNGE, focused on lithium/magnesium recovery from produced waters, state and federal oil-and-gas data, well completions and production engineering, water geochemistry, and ChBE engineering-science tutoring.

**Marketplace version:** v1.0.0 · **Plugins:** 8 · **Skills:** 76 · **Agents:** 12 · **Commands:** 12

> If you were previously running `pnge@jpfielding/claude.pnge` (v0.9.x), see [`CHANGELOG.md`](CHANGELOG.md) for the short migration.

## Install

```bash
# Point Claude Code at the marketplace
claude plugin marketplace add jpfielding/claude.pnge

# Install only what you need (list below)
claude plugin install pnge-core@claude-pnge
```

For local development:

```bash
git clone https://github.com/jpfielding/claude.pnge.git
claude plugin marketplace add ./claude.pnge
claude plugin install pnge-core@claude-pnge
```

## The 8 plugins

| Plugin | Purpose | Skills | Agents | Commands |
|---|---|---|---|---|
| [`pnge-core`](plugins/pnge-core/) | Flagship Li/Mg workflow: EIA + USGS produced waters/minerals + federated literature + DataCite DOIs + shared HTML visualizer + `/doctor`. **Install first.** | 6 | 1 | 4 |
| [`pnge-federal-data`](plugins/pnge-federal-data/) | Non-regulatory federal datasets (USGS, NETL, EPA regulatory stack, BOEM, BLM, FracFocus, NASA Earthdata, EJScreen/CEJST/SVI, WRI Aqueduct) + GIS mapper + research synthesis writer. | 15 | 2 | 1 |
| [`pnge-state-regulatory`](plugins/pnge-state-regulatory/) | State O&G regulators for WV/PA/OH/TX/NM/ND/LA/AR/OK/CA/CO + Appalachian mineral parcels + OSPAR offshore discharge standards + regulatory-disposal-analyst. | 13 | 1 | 2 |
| [`pnge-economics`](plugins/pnge-economics/) | FRED, BLS, BEA, Census, World Bank, UN Comtrade, IEA + pnge-geopolitics + tea-lca-analyst. | 7 | 2 | 2 |
| [`pnge-patents`](plugins/pnge-patents/) | USPTO / PatentsView DLE patent landscape + dle-patent-scout + `/patent-landscape`. | 1 | 1 | 1 |
| [`pnge-well-engineering`](plugins/pnge-well-engineering/) | Completions + production wellwork as one workflow (frac design, petrophysics, DFIT, tubing/lift, flow assurance, nodal analysis, RTA/DCA, well-test, production chemistry, integrity, PVT) + KGS well-logs + Macrostrat. | 23 | 1 | 1 |
| [`pnge-geochem-pw`](plugins/pnge-geochem-pw/) | Produced-water geochemistry and treatment: PHREEQC + NIST + mass/energy balance + tNavigator-style reservoir-fluid tools, water-chem-qaqc, lab-method-planner, pnge-pw-treatment. | 4 | 3 | 1 |
| [`pnge-engineering-science`](plugins/pnge-engineering-science/) | ChBE/MAE tutoring mapped to WVU courses: fluid mechanics, reaction engineering, thermo + EOS, heat transfer, mass transfer, aqueous chemistry / electrochem, materials / fracture mechanics + pnge-tutor agent. | 7 | 1 | 0 |

Full skill-by-skill listing: [`docs/DATA_SOURCES.md`](docs/DATA_SOURCES.md).

## Common install recipes

```bash
# Everything (old monolith behavior)
for p in pnge-core pnge-federal-data pnge-state-regulatory pnge-economics \
         pnge-patents pnge-well-engineering pnge-geochem-pw pnge-engineering-science; do
  claude plugin install $p@claude-pnge
done

# Li/Mg prospecting (most common)
claude plugin install pnge-core@claude-pnge
claude plugin install pnge-state-regulatory@claude-pnge
claude plugin install pnge-geochem-pw@claude-pnge

# Field / well engineering
claude plugin install pnge-core@claude-pnge
claude plugin install pnge-state-regulatory@claude-pnge
claude plugin install pnge-well-engineering@claude-pnge

# ChBE coursework only
claude plugin install pnge-engineering-science@claude-pnge

# TEA / LCA + supply chain
claude plugin install pnge-core@claude-pnge
claude plugin install pnge-economics@claude-pnge
claude plugin install pnge-patents@claude-pnge
```

## API keys

Only 6 of the 43 data skills require a free API key. See [`docs/TOKENS.md`](docs/TOKENS.md) for signup steps. Quick setup:

```bash
# Required
mkdir -p ~/.config/{eia,netl-edx,fred,openei,bea,census} && chmod 700 ~/.config/{eia,netl-edx,fred,openei,bea,census}
echo "api_key=YOUR_KEY" > ~/.config/eia/credentials        && chmod 600 ~/.config/eia/credentials
echo "api_key=YOUR_KEY" > ~/.config/netl-edx/credentials   && chmod 600 ~/.config/netl-edx/credentials
echo "api_key=YOUR_KEY" > ~/.config/fred/credentials       && chmod 600 ~/.config/fred/credentials
echo "api_key=YOUR_KEY" > ~/.config/openei/credentials     && chmod 600 ~/.config/openei/credentials
echo "api_key=YOUR_KEY" > ~/.config/bea/credentials        && chmod 600 ~/.config/bea/credentials
echo "api_key=YOUR_KEY" > ~/.config/census/credentials     && chmod 600 ~/.config/census/credentials

# Optional (raise rate limits)
mkdir -p ~/.config/{epa,bls,comtrade} && chmod 700 ~/.config/{epa,bls,comtrade}
# ... same pattern ...
```

After install, run `/doctor` (ships with `pnge-core`) to verify credentials and endpoint reachability across the marketplace.

## Usage

```bash
/prospect Marcellus Shale WV
/formation-profile Utica OH
/literature-review direct lithium extraction produced water
/regulatory-screen Smackover AR
/disposal-screen Tyler County WV
/well-economics Marcellus Monongalia WV 2024
/completions-design Marcellus Monongalia WV
/sustainability-profile Permian Basin TX
/water-chem-compare Marcellus vs Smackover
/patent-landscape sorbent DLE lithium
/tea-dle Marcellus WV 150 mg/L Li
/doctor
```

Cross-plugin agents (`li-mg-prospector`, `regulatory-disposal-analyst`, etc.) reference skills owned by sibling plugins. Each agent's markdown now ships a **Required Companion Plugins** table — if a companion isn't installed, the agent notes which pathway is unavailable and continues on the remaining data.

## Repository layout

```
claude.pnge/
├── .claude-plugin/marketplace.json       # Catalog of the 8 plugins
├── plugins/
│   ├── pnge-core/                        # 6 skills, 1 agent, 4 commands
│   ├── pnge-federal-data/                # 15 skills, 2 agents, 1 command
│   ├── pnge-state-regulatory/            # 13 skills, 1 agent, 2 commands
│   ├── pnge-economics/                   # 7 skills, 2 agents, 2 commands
│   ├── pnge-patents/                     # 1 skill, 1 agent, 1 command
│   ├── pnge-well-engineering/            # 23 skills, 1 agent, 1 command
│   ├── pnge-geochem-pw/                  # 4 skills, 3 agents, 1 command
│   └── pnge-engineering-science/         # 7 skills, 1 agent
├── scripts/                              # Ownership map + migration tools
├── docs/
│   ├── TOKENS.md                         # API key acquisition guide
│   ├── DATA_SOURCES.md                   # Per-skill data source reference
│   └── PACKAGING.md                      # Packaging, distribution, adding skills
├── CHANGELOG.md
├── README.md
└── LICENSE
```

## Development

```bash
# Validate every plugin manifest
for p in plugins/*/; do claude plugin validate "$p" || exit 1; done

# Verify the namespace sweep (no legacy pnge: refs; every skill points to its owner)
bash scripts/verify-namespaces.sh

# Re-annotate companion-plugin tables on agents (idempotent)
bash scripts/annotate-companions.sh
```

When adding a new skill: update `scripts/ownership.tsv` first, then create the skill directory under its owning plugin, then rerun `bash scripts/ownership.sh selftest` to confirm counts.

## License

Apache-2.0
