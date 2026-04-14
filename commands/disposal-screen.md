---
name: disposal-screen
description: Screen disposal well capacity and seismicity risk near a target area. Trigger: /disposal-screen Tyler County WV
---

Screen disposal well capacity and seismicity risk for: $ARGUMENTS

If no county, state, or location is provided, ask the user to specify a target area.

Use the following skills to build the disposal screening:

1. **pnge:wvges-wells** — disposal wells in WV (if Appalachian target)
2. **pnge:padep-wells** — disposal wells in PA (if Appalachian target)
3. **pnge:odnr-wells** — injection wells in OH (if Appalachian target)
4. **pnge:tx-rrc** — disposal wells in TX (if Permian/Eagle Ford target)
5. **pnge:epa-enviro** — UIC Class II permits and violations near the target
6. **pnge:usgs-earthquakes** — earthquake catalog within 10-25 km of the target area, 2009-present
7. **pnge:eia-data** — produced water volumes for the target area
8. **pnge:wri-aqueduct** — water stress context (high stress areas favor reuse over disposal)

Select state well skills based on the target location. Use only the relevant
state(s) rather than querying all states.

Structure the output as:

## Disposal Screening: [TARGET AREA]

### Produced Water Context
Estimated daily produced water volume in the target area. Number of producing wells.

### Disposal Well Map
List of active UIC Class II disposal wells within 25 miles of the target:

| Well ID | Operator | Distance (mi) | Injection Zone | Status | Permitted Rate (bbl/day) |
|---------|----------|---------------|---------------|--------|-------------------------|

### Capacity Assessment
Total permitted disposal capacity vs. estimated produced water volume. Is there a surplus or deficit?

### Seismicity Assessment
| Metric | Value |
|--------|-------|
| Earthquakes within 10 km (2009-present) | |
| Max magnitude | |
| Events M >= 3.0 | |
| Depth distribution | |
| Proximity to nearest disposal well | |
| Seismicity risk rating | HIGH / MEDIUM / LOW |

### UIC Compliance
Violations at nearby disposal wells (if any). MIT test status.

### Water Stress Context
WRI Aqueduct water stress rating for the target area. If HIGH stress, note that reuse may be more economically attractive than disposal.

### Recommendation
Disposal feasible / constrained / recommend reuse. Justification based on capacity, seismicity, and cost.
