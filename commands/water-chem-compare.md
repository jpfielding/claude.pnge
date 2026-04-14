---
name: water-chem-compare
description: Compare produced water chemistry across formations or basins with QA/QC validation. Trigger: /water-chem-compare Marcellus vs Smackover
---

Compare produced water chemistry for: $ARGUMENTS

If no formations or basins are provided, ask the user to specify at least two
targets to compare (e.g., "Marcellus vs Smackover" or "Marcellus WV vs Marcellus PA").

Use the **water-chem-qaqc** agent and the following skills:

1. **pnge:usgs-produced-waters** — brine geochemistry for each target formation/basin
2. **pnge:macrostrat** — stratigraphic context (age, lithology, depositional environment)
3. **pnge:usgs-pubs** — USGS reports characterizing each formation's water chemistry

For each formation, the water-chem-qaqc agent should:
- Harmonize units to mg/L (with SG correction if needed)
- Flag censored/below-detection values
- Calculate charge balance error and report pass rates
- Normalize formation names to standard nomenclature

Structure the output as:

## Water Chemistry Comparison: [FORMATION A] vs. [FORMATION B]

### Geological Context
Brief comparison of age, depth, lithology, and depositional environment for each formation.

### Sample Inventory
| Formation | State(s) | n (total) | n (with Li) | n (passing CBE) | Date Range |
|-----------|----------|-----------|-------------|-----------------|------------|

### Chemistry Comparison Table
| Parameter | [Formation A] Median | [Formation A] Range | [Formation B] Median | [Formation B] Range | Unit |
|-----------|---------------------|--------------------|--------------------|--------------------|----|
| Li | | | | | mg/L |
| Mg | | | | | mg/L |
| TDS | | | | | mg/L |
| Ca | | | | | mg/L |
| Na | | | | | mg/L |
| Cl | | | | | mg/L |
| Ba | | | | | mg/L |
| Sr | | | | | mg/L |
| pH | | | | | — |

### Li/Mg Recovery Potential Comparison
Which formation has higher Li concentrations, lower interferents, and better data quality for DLE assessment.

### Data Quality Summary
QA/QC pass rates, censoring issues, and data confidence rating for each formation.

### Key Differences
3-5 bullet points highlighting the most significant geochemical differences and their implications for mineral recovery.
