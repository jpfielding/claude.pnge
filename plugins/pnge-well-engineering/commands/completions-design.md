---
name: completions-design
description: "Assist with hydraulic fracture completions design for a target formation — stage spacing, fluid selection, proppant, diagnostics, and chemistry context — using FracFocus disclosures, formation data, and engineering calculations. Trigger: /completions-design Marcellus horizontal Monongalia County WV"
---

Assist with completions design for: $ARGUMENTS

If no formation, well type, or location is provided, ask the user to specify.

Use the following skills to gather data and context:

1. **pnge-federal-data:fracfocus** — existing completions chemical disclosures for offset wells in the target area
2. **pnge-state-regulatory:wvges-wells** — well depths, formations, and operators for offset wells
3. **pnge-core:usgs-produced-waters** — formation water chemistry (TDS, hardness, scaling ions Ba/Sr/Ca) that affects fluid selection
4. **pnge-well-engineering:frac-design** — engineering calculations: net pressure, fracture geometry estimates, proppant scheduling
5. **pnge-well-engineering:completion-diagnostics** — DFIT / minifrac / ISIP / closure-pressure context and treatment-pressure interpretation
6. **pnge-well-engineering:production-chemistry** — cleanup, additive compatibility, and DLE-interference screening
7. **pnge-well-engineering:stage-treatment-analysis** — if local stage exports are available, normalize and compare actual treatment execution

Structure the output as:

## Completions Design Context: [FORMATION/AREA]

### Offset Well Summary
From FracFocus: number of nearby disclosures, average water volume (bbl), average proppant mass (lbs), date range.

### Common Fluid Systems
Top fluid systems used by operators in the area (slickwater, hybrid, crosslink). Note dominant additives by purpose.

### Formation Water Chemistry Context
Key scaling concerns (Ba+Sr for barite, Ca for calcite), TDS, water-sensitive minerals to note.

### Engineering Estimates
Using the pnge-well-engineering:frac-design skill:
- Estimated fracture closure pressure from depth and typical gradient
- Recommended stage spacing range based on formation brittleness
- Proppant concentration guidance

### Diagnostic Context
Using `pnge-well-engineering:completion-diagnostics`:
- If available, summarize offset closure pressure / ISIP / step-rate evidence
- Note whether limited-entry assumptions are realistic
- Identify what stage data would materially improve design confidence

### Stage Execution Context
Using `pnge-well-engineering:stage-treatment-analysis` when local files are provided:
- Summarize stage totals, outliers, and likely screenout or execution issues
- Separate data-quality problems from real treatment behavior

### Chemical Considerations for DLE
If produced water mineral recovery is a goal, note which completion chemicals may interfere with DLE sorbents or membranes.

### Chemistry Risks
Using `pnge-well-engineering:production-chemistry`:
- Flag likely emulsion, iron, scale, residual polymer, surfactant, or biocide concerns
- Note compatibility issues for reuse, treatment, or produced-water valorization

### Data Gaps
What site-specific data (ISIP, closure pressure, core data) would improve this design.
