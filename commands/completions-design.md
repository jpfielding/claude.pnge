---
name: completions-design
description: Assist with hydraulic fracture completions design for a target formation — stage spacing, fluid selection, proppant, and chemical context — using FracFocus disclosures, formation data, and engineering calculations. Trigger: /completions-design Marcellus horizontal Monongalia County WV
---

Assist with completions design for: $ARGUMENTS

If no formation, well type, or location is provided, ask the user to specify.

Use the following skills to gather data and context:

1. **pnge:fracfocus** — existing completions chemical disclosures for offset wells in the target area
2. **pnge:wvges-wells** — well depths, formations, and operators for offset wells
3. **pnge:usgs-produced-waters** — formation water chemistry (TDS, hardness, scaling ions Ba/Sr/Ca) that affects fluid selection
4. **pnge:frac-design** — engineering calculations: net pressure, fracture geometry estimates, proppant scheduling

Structure the output as:

## Completions Design Context: [FORMATION/AREA]

### Offset Well Summary
From FracFocus: number of nearby disclosures, average water volume (bbl), average proppant mass (lbs), date range.

### Common Fluid Systems
Top fluid systems used by operators in the area (slickwater, hybrid, crosslink). Note dominant additives by purpose.

### Formation Water Chemistry Context
Key scaling concerns (Ba+Sr for barite, Ca for calcite), TDS, water-sensitive minerals to note.

### Engineering Estimates
Using the pnge:frac-design skill:
- Estimated fracture closure pressure from depth and typical gradient
- Recommended stage spacing range based on formation brittleness
- Proppant concentration guidance

### Chemical Considerations for DLE
If produced water mineral recovery is a goal, note which completion chemicals may interfere with DLE sorbents or membranes.

### Data Gaps
What site-specific data (ISIP, closure pressure, core data) would improve this design.
