---
name: regulatory-screen
description: Cross-state regulatory and disposal screening for a target area. Trigger: /regulatory-screen Marcellus WV
---

Perform a cross-state regulatory and disposal screening for: $ARGUMENTS

If no formation, basin, or state is provided, ask the user to specify one.

Use the **regulatory-disposal-analyst** agent to orchestrate:

1. **pnge:wvges-wells** — WV disposal wells and UIC permits
2. **pnge:padep-wells** — PA disposal wells and permits
3. **pnge:odnr-wells** — OH injection wells (post-Youngstown seismicity rules)
4. **pnge:tx-rrc** — TX disposal well data and H-10 injection reports
5. **pnge:nm-ocd** — NM disposal well permits
6. **pnge:nd-dmr** — ND disposal wells (Bakken context)
7. **pnge:la-sonris** — LA saltwater disposal wells
8. **pnge:ar-aogc** — AR disposal wells (Smackover context)
9. **pnge:epa-regulatory** — ECHO compliance, Envirofacts (NPDES/TRI/FRS), GHGRP, and Subpart W methane emissions at nearby facilities. UIC Class II well-level records come from the state regulator skills above.
11. **pnge:usgs-earthquakes** — seismicity catalog within 10 km of disposal wells
12. **pnge:eia-data** — produced water volumes and production context

Focus the analysis on states relevant to the user's target area. For an
Appalachian target (Marcellus, Utica), prioritize WV, PA, and OH. For a
Gulf Coast target (Smackover), prioritize AR, LA, and TX.

Structure the output as:

## Regulatory Disposal Screening: [TARGET AREA]

### Produced Water Volume Context
Estimated produced water volume in the target area from EIA data.

### Disposal Well Inventory
Count of active, permitted, and plugged disposal wells within 50 miles of the target area, by state.

### Injection Limit Comparison
Table of max injection pressure, max rate, max cumulative volume, MIT frequency, and monitoring requirements by state.

### Seismicity Risk Assessment
Earthquake count and max magnitude within 10 km of disposal wells, 2009-present. Risk rating (HIGH/MEDIUM/LOW).

### Environmental Compliance
UIC violations, NPDES permits, Subpart W reporting status for facilities in the target area.

### Cross-State Disposal Cost Estimate
Comparative table of disposal cost components (disposal fee, trucking, pipeline, permit, compliance) by state.

### Recommendation
Dispose in-state vs. out-of-state vs. reuse/treatment recommendation with justification.

### Data Gaps
What regulatory data is unavailable or incomplete for the target states.
