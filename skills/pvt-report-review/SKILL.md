---
name: pvt-report-review
description: >
  Review and extract engineering value from local PVT laboratory reports,
  spreadsheets, PDFs, and table exports including CCE, CVD, differential
  liberation, separator tests, viscosity tables, and black-oil summaries. Use
  when the user provides a PVT report and asks to extract bubble point, Rs, Bo,
  Bg, shrinkage, dewpoint, condensate dropout behavior, lab quality issues, or
  black-oil inputs for simulation and nodal analysis. Trigger phrases include
  PVT report, lab report review, CCE, CVD, differential liberation, separator
  test, black-oil table, fluid report, extract PVT data, or QC this lab report.
---

# PVT Report Review

File-review skill for turning lab reports into usable engineering inputs. It is
paired with `pnge:petroleum-pvt`, which provides the actual screening
correlations and property calculations.

**Important:** Many PVT reports are internally consistent only within a single
test type. Do not mix separator-test values, differential-liberation values, and
CCE/CVD values without stating the intended use.

---

## Preferred Inputs

- PDF or spreadsheet PVT report
- Test type labels: CCE, CVD, differential liberation, separator test, swelling
- Reservoir temperature and reference pressure
- Fluid composition if available
- Any black-oil table already exported by the lab

---

## Workflow

1. Inventory what test types are actually present.
2. Extract the core fluid descriptors and reference conditions.
3. Check tables for monotonicity and obvious unit errors.
4. Separate values suitable for reservoir use from separator-use values.
5. Output a compact property package and list the unresolved issues.

---

## Module 1 - Report Inventory

Use this checklist first:

- fluid type statement: black oil, volatile oil, gas condensate, lean gas
- reservoir temperature
- bubble point or dewpoint
- stock-tank oil gravity and gas gravity
- test tables present and missing
- black-oil summary table present or absent
- separator conditions and stage count

If the report lacks the reference conditions, stop and flag that before doing
any extraction.

---

## Module 2 - Table QC Helpers

```python
def monotonic_direction(values):
    """
    Return 'increasing', 'decreasing', 'mixed', or 'flat' for a series.
    """
    diffs = [values[i] - values[i - 1] for i in range(1, len(values))]
    pos = any(d > 0 for d in diffs)
    neg = any(d < 0 for d in diffs)
    if pos and neg:
        return "mixed"
    if pos:
        return "increasing"
    if neg:
        return "decreasing"
    return "flat"

def linear_interpolate(x1, y1, x2, y2, x_target):
    if x2 == x1:
        return None
    return y1 + (y2 - y1) * (x_target - x1) / (x2 - x1)
```

Expected broad trends:

| Table | Trend to sanity-check |
|------|------------------------|
| Oil viscosity vs pressure below bubble point | Often decreases as pressure increases toward bubble point |
| Rs below bubble point | Increases with pressure |
| Relative volume in CCE above saturation | Changes smoothly, not erratically |
| Condensate dropout in CVD | Peaks then may partially recover with depletion |

---

## Module 3 - Black-Oil Extraction Targets

For most engineering workflows, extract:

- bubble point or dewpoint
- `Rs`, `Bo`, and oil viscosity versus pressure
- gas `z`, `Bg`, and gas viscosity versus pressure
- separator shrinkage and yields
- stock-tank and reservoir fluid descriptors

If the report already contains black-oil tables, prefer those over manual
reconstruction from raw tests.

---

## Module 4 - PVT Use Mapping

| Need | Best report section |
|-----|----------------------|
| Reservoir simulation black-oil table | Lab black-oil summary or reconstructed DL/CVD results |
| Nodal analysis screening | Saturation pressure, `Rs`, `Bo`, viscosities, separator shrinkage |
| Facility flash / separator behavior | Separator test tables |
| Condensate banking risk | Dewpoint plus CVD dropout behavior |

---

## Module 5 - Common Report Problems

| Problem | What to flag |
|--------|---------------|
| Missing reservoir temperature | Entire report is hard to use |
| Units inconsistent across tables | Do not merge tables blindly |
| Bubble point conflicts between summary and test pages | Cite both and state discrepancy |
| Viscosity tables without pressure basis | Not safe to use in nodal or simulation |
| No composition and no pseudocomponents | EOS reuse will be limited |

---

## Output Format

When using this skill, structure the answer as:

1. Report inventory
2. Extracted key properties and conditions
3. QC findings and discrepancies
4. Recommended values for nodal / PTA / simulation use
5. Missing items to request from the lab

---

## Integration Points

- Use `pnge:petroleum-pvt` for screening correlations and gap filling.
- Use `pnge:nodal-analysis-multiphase` for production system use.
- Use `pnge:thermo-eos` if the report includes compositional EOS data.
