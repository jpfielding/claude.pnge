---
name: tea-dle
description: "Quick techno-economic screening for DLE from a target brine source. Trigger: /tea-dle Marcellus WV 150 mg/L Li"
---

Run a techno-economic screening for DLE from: $ARGUMENTS

If no formation, location, or Li concentration is provided, ask the user to
specify at minimum a formation and state. Li concentration can be looked up
from USGS data if not provided.

Use the **tea-lca-analyst** agent to orchestrate:

1. **pnge-core:usgs-produced-waters** — brine chemistry (Li, Mg, TDS, interferents) for the target formation
2. **pnge-economics:fred-prices** — current Li carbonate, Li hydroxide, and Mg prices
3. **pnge-core:usgs-minerals** — Li/Mg production stats, reserves, demand context
4. **pnge-core:eia-data** — produced water volumes, electricity and gas prices by state
5. **pnge-economics:worldbank-energy** — global energy context and EV adoption trends
6. **pnge-economics:iea-open** — IEA EV tracker for Li demand projections
7. **pnge-economics:comtrade-minerals** — U.S. Li import reliance and trade flows
8. **pnge-federal-data:wri-aqueduct** — water stress (affects freshwater cost and social license)
9. **pnge-federal-data:epa-regulatory** (Subpart W mode) — baseline GHG emissions context

Structure the output as:

## TEA Screening: DLE from [FORMATION], [STATE]

### Brine Characterization
Li (mg/L), Mg (mg/L), TDS (mg/L), key interferents (Ba, Sr, Fe, SiO2). Sample count and data source.

### Revenue Estimate
| Product | Concentration | kg/bbl | Price ($/kg) | Revenue ($/bbl) |
|---------|--------------|--------|-------------|----------------|
| Li2CO3 (LCE) | | | | |
| MgO (co-product) | | | | |
| **Total** | | | | |

### Technology Screening
Candidate DLE technologies for this brine condition. Ranked by suitability.

### Cost Estimate
| Component | Low ($/bbl) | Base ($/bbl) | High ($/bbl) |
|-----------|------------|-------------|-------------|
| Pretreatment | | | |
| DLE extraction | | | |
| Polishing/precipitation | | | |
| Utilities | | | |
| Labor + maintenance | | | |
| CAPEX amortization | | | |
| **Total** | | | |

### Margin Analysis
| Scenario | Li Price | Revenue ($/bbl) | Cost ($/bbl) | Margin ($/bbl) |
|----------|---------|----------------|-------------|----------------|
| Bear | | | | |
| Base | | | | |
| Bull | | | | |

### Sensitivity Table
Key variables and their impact on margin at +/- 30-50% variation.

### Carbon Intensity
Estimated t CO2 per t LCE vs. salar and hard rock benchmarks.

### Go/No-Go Assessment
Recommendation with confidence level, key uncertainties, and what data would change the conclusion.

### Accuracy Disclaimer
AACE Class 4-5 estimate (+/- 50%). Not a bankable feasibility study.
