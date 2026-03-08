---
name: well-economics
description: Run a quick-look economic analysis for an oil/gas well or formation play, incorporating current commodity prices, production data, and mineral revenue uplift from produced water. Trigger: /well-economics Marcellus horizontal well WV
---

Run a quick-look economic analysis for: $ARGUMENTS

If no well type, formation, or location is provided, ask the user to specify.

Use the following skills to gather inputs:

1. **pnge:eia-data** — current natural gas and oil prices, regional production volumes, wellhead prices
2. **pnge:fred-prices** — spot commodity prices (Henry Hub gas, WTI crude, Li carbonate)
3. **pnge:usgs-minerals** — Li and Mg commodity pricing and demand outlook
4. **pnge:usgs-produced-waters** — produced water Li/Mg concentrations for revenue uplift estimate

Structure the output as:

## Well Economics: [DESCRIPTION]

### Current Commodity Prices
| Commodity | Price | Unit | Date | Source |
|-----------|-------|------|------|--------|

### Production Assumptions
State the assumed IP rate, decline curve type, EUR, and well cost (with source or assumption basis).

### Revenue Projections
Simple cash flow table: Year 1–5 production volumes × price = gross revenue.

### Produced Water Mineral Uplift
If Li or Mg concentrations are available for the formation:
- Estimated produced water volume (bbl/year)
- Li concentration (mg/L) → potential Li carbonate revenue at current price
- Note this is pre-extraction-cost gross potential, not net revenue

### Breakeven Analysis
At what commodity price does the well break even on assumed capex?

### Caveats
List all major assumptions and their uncertainty.

Note: This is a screening-level analysis only. Do not use for investment decisions.
