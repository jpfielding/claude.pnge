---
name: production-chemistry
description: >
  Analyze oilfield production chemistry problems including brine and additive
  compatibility, corrosion and scale inhibitor programs, emulsion and solids
  stabilization, asphaltene and paraffin troubleshooting, chemical squeeze
  design, completion-fluid cleanup, and chemistry impacts on produced-water
  reuse or DLE processes. Use when the user asks about emulsions, chemical
  incompatibility, squeeze jobs, corrosion inhibitor dosage, biocide or breaker
  performance, residual polymers, iron control, cleanup after stimulation, or
  why production chemistry is hurting operations. Trigger phrases include
  production chemistry, emulsion, bottle test, squeeze design, incompatibility,
  chemical program, corrosion coupon, demulsifier, residual polymer, filter
  cake cleanup, water reuse, or DLE interference.
---

# Production Chemistry

Production chemistry skill for the wellbore-to-facilities interface. It focuses
on what commonly gets missed between stimulation design, flow assurance, and
water treatment: chemical compatibility, cleanup, and surveillance.

**Important:** Use lab bottle tests, filterability tests, corrosion coupons, and
full water analyses whenever possible. Field chemistry programs are rarely
credible when based on one ion panel and a single day of production.

---

## Data To Request First

- Full produced-water chemistry, not just TDS and chlorides
- Oil and condensate properties, BS&W, solids, iron, and oil-in-water
- Completion fluid recipe, breaker package, biocide, friction reducer, and scale inhibitor history
- Injection or squeeze treatment volumes, active concentration, and return data
- Temperature, pressure, CO2, H2S, oxygen ingress, and metallurgy context
- Bottle test, jar test, coupon, probe, or filterability data if any exist

---

## Workflow

1. Confirm the failure mode: scale, corrosion, emulsion, solids, cleanup, or incompatibility.
2. Normalize concentrations and active ingredient dosage.
3. Check what changed operationally before changing chemistry again.
4. Separate reservoir-fluid issues from treatment-chemical issues.
5. Recommend the minimum useful set of lab tests to confirm the diagnosis.

---

## Module 1 - Mixing And Dosage

```python
def mixed_concentration(c1, q1, c2, q2):
    """
    Mix two streams with concentrations c1 and c2.
    Units may be mg/L, ppm, wt%, etc. as long as both match.
    """
    if (q1 + q2) == 0:
        return None
    return (c1 * q1 + c2 * q2) / (q1 + q2)

def product_injection_gpd(water_rate_bpd, target_ppm_active,
                          product_active_frac=1.0,
                          product_density_lb_gal=8.34):
    """
    Daily product requirement for a continuous chemical program.
    target_ppm_active is ppm active in the produced-water stream.
    """
    if product_active_frac <= 0 or product_density_lb_gal <= 0:
        return None
    water_lb_day = water_rate_bpd * 42.0 * 8.34
    active_lb_day = water_lb_day * target_ppm_active / 1e6
    product_lb_day = active_lb_day / product_active_frac
    return product_lb_day / product_density_lb_gal
```

**Common failure mode:** teams compare product gallons instead of active ppm.
Always normalize to active ingredient.

---

## Module 2 - Squeeze And Near-Wellbore Treatment Volumes

```python
def radial_pore_volume_bbl(rw_ft, re_ft, net_height_ft, porosity,
                           water_saturation=1.0):
    """
    Cylindrical pore volume in reservoir barrels.
    Volume(ft3) = pi * h * (re^2 - rw^2) * phi * Sw
    1 reservoir bbl = 5.615 ft3
    """
    import math
    bulk_ft3 = math.pi * net_height_ft * (re_ft**2 - rw_ft**2)
    pore_ft3 = bulk_ft3 * porosity * water_saturation
    return pore_ft3 / 5.615

def squeeze_slug_bbl(pore_volume_bbl, treated_pv_frac=0.05, overflush_frac=0.25):
    """
    Screening slug and overflush volumes for inhibitor squeeze design.
    """
    slug = pore_volume_bbl * treated_pv_frac
    overflush = slug * overflush_frac
    return {"slug_bbl": slug, "overflush_bbl": overflush,
            "total_bbl": slug + overflush}
```

Use actual adsorption isotherms, rock mineralogy, and target return profile for
final squeeze design. The equations above are screening only.

---

## Module 3 - Corrosion Program Surveillance

```python
def corrosion_rate_mpy(weight_loss_mg, density_g_cm3, area_in2, time_hr):
    """
    Corrosion rate in mils per year from coupon weight loss.
    Standard form: CR(mpy) = 534 * W / (D * A * t)
    """
    if density_g_cm3 <= 0 or area_in2 <= 0 or time_hr <= 0:
        return None
    return 534.0 * weight_loss_mg / (density_g_cm3 * area_in2 * time_hr)

def inhibitor_efficiency(blank_rate, treated_rate):
    """Percent reduction in corrosion rate due to treatment."""
    if blank_rate <= 0:
        return None
    return 100.0 * (blank_rate - treated_rate) / blank_rate
```

**Surveillance hierarchy**

1. Coupon or probe trend
2. Iron trend and solids characterization
3. Failure analysis of retrieved metal
4. Only then chemical program adjustment

---

## Module 4 - Troubleshooting Matrix

| Symptom | Likely chemistry issue | What to test next |
|--------|------------------------|-------------------|
| Tight stable emulsion after rate change | Shear plus wrong demulsifier / solids-stabilized emulsion | Bottle tests across temperature and dose |
| Rising iron with flat CO2/H2S | Oxygen ingress or poor inhibitor partitioning | Dissolved oxygen, residual inhibitor, corrosion coupon |
| High filter plugging after frac flowback | Residual polymer, fines, iron sulfide, broken scale | Filterability, particle sizing, breaker residuals |
| Lost injectivity after mixing waters | Incompatible sulfate, hardness, iron, or bacteria | Jar tests, full ion panels, solids mineralogy |
| DLE or membrane upset after completions | Residual biocide, polymer, surfactant, iron, oil carryover | TOC, residual polymer, surfactant, oil-in-water, iron speciation |

---

## Module 5 - Cleanup And Reuse Checklist

Before concluding that "the chemistry is bad," check:

- Was the breaker system matched to temperature and residence time?
- Did iron control and oxygen scavenging match the actual flowback period?
- Are returned additives still present at concentrations that affect membranes or sorbents?
- Did a change in separator residence time, shear, or heating create the emulsion problem?
- Did mixed waters change barium, strontium, sulfate, or carbonate saturation?

---

## Output Format

When using this skill, structure the answer as:

1. Confirmed or suspected chemistry failure mode
2. Data normalization and active-ingredient basis
3. Most likely root causes
4. Minimal lab or field tests needed to confirm
5. Operational and chemical actions, in that order

---

## Integration Points

- Use `pnge-well-engineering:flow-assurance` for hydrate, corrosion, wax, and scale thermodynamics.
- Use `pnge-well-engineering:matrix-acidizing` for acid cleanup and iron / precipitate risks.
- Use `pnge-core:usgs-produced-waters` and `pnge-federal-data:usgs-waterdata` for water chemistry context.
- Use the `pnge-pw-treatment` agent or DLE workflows when reuse or mineral recovery is the objective.
