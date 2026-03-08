---
name: petroleum-pvt
description: >
  Perform petroleum fluid PVT screening and black-oil property estimation
  including bubble point, solution GOR, oil formation volume factor, gas
  pseudocritical properties, gas formation volume factor, separator shrinkage,
  condensate dropout screening, and lab-report quality checks. Use when the
  user asks about black-oil PVT, reservoir fluid properties, bubble point,
  solution gas ratio, oil shrinkage, gas z-factor screening, condensate
  banking risk, separator flashes, or how to interpret a PVT report. Trigger
  phrases include PVT, bubble point, Rs, Bo, Bg, black oil, CCE, CVD, DL test,
  separator test, shrinkage, condensate dropout, dewpoint, or fluid report.
---

# Petroleum PVT

Black-oil and screening-PVT skill for production and reservoir engineering.
Use it when lab data are incomplete, when you need a quick consistency check,
or when you need to translate a fluid report into inputs for nodal, PTA, or
decline work.

**Important:** Correlations are for screening. If a compositional lab exists,
honor the lab unless it clearly fails sanity checks. For rigorous EOS work, use
`pnge:thermo-eos`.

---

## Data To Request First

- Reservoir pressure and temperature
- API gravity, gas specific gravity, separator conditions
- Bubble point or dewpoint if measured
- Test oil, gas, and water rates with separator stages
- PVT report type: differential liberation, CCE, CVD, separator test, swelling
- Full composition if available

---

## Workflow

1. Decide whether the fluid is best treated as black oil, volatile oil, gas condensate, or lean gas.
2. Prefer lab values when present; use correlations only to fill gaps or QC the report.
3. Carry units consistently in field units unless the user specifies SI.
4. State whether the result is lab-based, correlation-based, or a hybrid.

---

## Module 1 - Core Black-Oil Correlations

```python
def oil_specific_gravity(api):
    """Oil specific gravity from API gravity."""
    return 141.5 / (api + 131.5)

def standing_bubble_point_psia(rs_scf_stb, gas_sg, temp_f, api):
    """
    Standing bubble point correlation.
    """
    term = (rs_scf_stb / gas_sg) ** 0.83 * 10 ** (0.00091 * temp_f - 0.0125 * api)
    return 18.2 * term - 1.4

def standing_rs_scf_stb(p_psia, gas_sg, temp_f, api):
    """
    Standing solution GOR below bubble point.
    """
    term = (p_psia / 18.2 + 1.4) * 10 ** (0.0125 * api - 0.00091 * temp_f)
    return gas_sg * term ** (1.0 / 0.83)

def standing_bo_rb_stb(rs_scf_stb, gas_sg, temp_f, api):
    """
    Standing oil formation volume factor at or below bubble point.
    """
    gamma_o = oil_specific_gravity(api)
    term = rs_scf_stb * (gas_sg / gamma_o) ** 0.5 + 1.25 * temp_f
    return 0.9759 + 0.00012 * term ** 1.2
```

**Use guidance**

| Property | Typical use |
|---------|-------------|
| `Pb` | Determine if oil is saturated at reservoir pressure |
| `Rs` | Convert between oil and liberated gas behavior |
| `Bo` | Material balance, nodal, and reserve calculations |

---

## Module 2 - Gas Screening Properties

```python
def sutton_pseudocritical(gas_sg):
    """
    Sutton pseudocritical properties for sweet natural gas.
    Returns Tpc in Rankine and Ppc in psia.
    """
    tpc_r = 169.2 + 349.5 * gas_sg - 74.0 * gas_sg**2
    ppc_psia = 756.8 - 131.0 * gas_sg - 3.6 * gas_sg**2
    return {"Tpc_R": tpc_r, "Ppc_psia": ppc_psia}

def pseudoreduced_props(p_psia, temp_f, gas_sg):
    """Ppr and Tpr for z-factor chart or correlation lookup."""
    pc = sutton_pseudocritical(gas_sg)
    t_r = temp_f + 459.67
    return {"Ppr": p_psia / pc["Ppc_psia"], "Tpr": t_r / pc["Tpc_R"]}

def gas_fvf_rb_scf(p_psia, temp_f, z):
    """
    Gas formation volume factor in reservoir bbl/scf.
    Bg = 0.00504 * z * T(R) / P(psia)
    """
    t_r = temp_f + 459.67
    return 0.00504 * z * t_r / p_psia
```

If gas composition is available or CO2 / H2S is significant, use a real EOS or
corrected pseudocritical method instead of sweet-gas screening correlations.

---

## Module 3 - Separator And Shrinkage Checks

```python
def separator_shrinkage(stock_tank_stb, separator_liquid_bbl):
    """
    Stock tank barrels per separator barrel.
    """
    if separator_liquid_bbl <= 0:
        return None
    return stock_tank_stb / separator_liquid_bbl

def dewpoint_margin_psia(reservoir_pressure_psia, dewpoint_psia):
    """
    Positive margin means reservoir pressure is above dewpoint.
    Negative means condensate dropout is likely in the reservoir.
    """
    return reservoir_pressure_psia - dewpoint_psia
```

**Interpretation**

| Result | Meaning |
|-------|---------|
| Shrinkage close to 1.0 | Stable oil / little flash shrinkage |
| Large shrinkage loss | Volatile oil or condensate-rich liquid |
| Negative dewpoint margin | In-reservoir condensate dropout risk |

---

## Module 4 - Lab QC Checklist

Before trusting a lab report, check:

- Are `Rs`, `Bo`, and viscosity trends monotonic where they should be?
- Does reported bubble point or dewpoint match the reservoir fluid description?
- Do separator test yields reconcile with field separator conditions?
- Are gas specific gravity and flashed gas composition directionally consistent?
- Do black-oil tables imply impossible densities or negative shrinkage?

If the lab fails these checks, state that explicitly and fall back to bounded
correlation estimates.

---

## Module 5 - Fluid-Type Decision Guide

| Fluid type | Signs |
|-----------|------|
| Black oil | Moderate GOR, clear bubble point, small shrinkage |
| Volatile oil | High GOR, large shrinkage, strong separator sensitivity |
| Gas condensate | Dewpoint-controlled behavior, condensate dropout risk |
| Lean gas | Low condensate yield, gas properties dominate |

---

## Output Format

When using this skill, structure the answer as:

1. Fluid classification and data quality
2. Key PVT properties used or estimated
3. Lab-versus-correlation comparison
4. Operational implication for nodal, PTA, RTA, or facilities
5. Biggest missing PVT data item

---

## Integration Points

- Use `pnge:nodal-analysis-multiphase` for production system optimization.
- Use `pnge:well-test-analysis` and `pnge:rta-production` when fluid properties drive interpretation.
- Use `pnge:surface-facilities` for separator and compression implications.
- Use `pnge:thermo-eos` for compositional EOS calculations and rigorous phase behavior.
