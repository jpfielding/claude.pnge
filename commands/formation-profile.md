---
name: formation-profile
description: Generate a comprehensive geological and geochemical profile for a target formation or basin — stratigraphy, depth, lithology, produced water chemistry, and research literature. Trigger: /formation-profile Marcellus WV
---

Generate a comprehensive formation profile for: $ARGUMENTS

If no formation or location is provided, ask the user to specify one.

Use the following skills to build the profile:

1. **pnge:macrostrat** — stratigraphic column, age, lithology, thickness, depositional environment for the target formation
2. **pnge:usgs-produced-waters** — brine geochemistry (Li, Mg, TDS, major ions) from the formation
3. **pnge:wvges-wells** — well penetrations and depths in WV (if Appalachian target)
4. **pnge:usgs-pubs** — USGS reports and geological surveys on the formation
5. **pnge:doe-osti** — DOE research on the formation's reservoir and fluid properties

Structure the output as:

## Formation Profile: [NAME]

### Stratigraphy
Age, system, series, thickness range, depth range, depositional environment.

### Lithology
Primary rock types, mineralogy, key diagenetic features relevant to porosity/permeability.

### Produced Water Chemistry
Summary table: Li, Mg, TDS, Ca, Na, Cl, Ba, Sr concentrations (mg/L). Note sample count.

### Well Data
Number of permitted/producing wells, primary counties/states, depth distribution.

### Key Literature
Top 5 publications with DOIs.

### Data Confidence
Rate each section HIGH / MEDIUM / LOW with brief justification.
