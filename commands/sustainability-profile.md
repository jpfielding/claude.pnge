---
name: sustainability-profile
description: Generate a sustainability and environmental impact profile for an oil/gas operator, formation, or basin — water stress, GHG emissions, seismicity risk, compliance history, and critical mineral recovery potential. Trigger: /sustainability-profile Marcellus operators WV
---

Generate a sustainability profile for: $ARGUMENTS

If no operator, formation, or location is provided, ask the user to specify.

Use the following skills to build the profile:

1. **pnge:wri-aqueduct** — water stress index for the operating area
2. **pnge:epa-ghg** — reported GHG emissions from facilities in the area (GHGRP)
3. **pnge:epa-ghgrp-subpartw** — Subpart W oilfield methane emissions (equipment-level detail)
4. **pnge:epa-enviro** — UIC well permits, NPDES discharges, TRI releases, compliance history
5. **pnge:usgs-earthquakes** — induced seismicity events near disposal wells in the area
6. **pnge:usgs-produced-waters** — produced water volumes and Li/Mg concentrations (circular economy angle)

Structure the output as:

## Sustainability Profile: [SUBJECT]

### Water Stress Context
Baseline water stress category for the operating area. Annual produced water volumes.
Injection disposal vs. reuse breakdown if known.

### GHG and Methane Emissions
Total reported Scope 1 emissions (CO2e). Subpart W methane breakdown by equipment type.
Emission intensity (tonnes CO2e / MMcfe production) if calculable.

### Environmental Compliance
UIC permit status, any violations. NPDES discharge permits. TRI chemical releases.
Note any significant enforcement actions.

### Seismicity Risk
Number of M2.0+ events within 30 km of disposal wells in the last 5 years.
Risk level: LOW / MEDIUM / HIGH with criteria.

### Critical Mineral Recovery Opportunity
From produced water chemistry: estimated Li/Mg concentrations.
Frame as sustainability co-benefit: converting a waste stream (produced water)
into a domestic critical mineral feedstock.

### ESG Summary Table
| Dimension | Score | Basis |
|-----------|-------|-------|
| Water stress | HIGH/MED/LOW | WRI Aqueduct category |
| GHG intensity | HIGH/MED/LOW | vs. basin average |
| Seismicity risk | HIGH/MED/LOW | event frequency |
| Compliance | GOOD/FAIR/POOR | violation history |
| Mineral recovery potential | HIGH/MED/LOW | Li concentration |
