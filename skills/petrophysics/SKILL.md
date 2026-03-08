---
name: petrophysics
description: >
  Perform petrophysical log interpretation and formation evaluation for oil and
  gas wells. Covers shale volume from gamma ray using linear and Larionov
  methods, porosity from density log, sonic Wyllie time-average, and
  neutron-density crossplot, water saturation using Archie equation, Simandoux,
  and Indonesian equation for shaly sands, irreducible water saturation from
  Buckles number, moveable hydrocarbon index, net pay zone cutoffs, and
  brittleness index from compressional and shear slowness for completion quality
  assessment in unconventional reservoirs. Use when interpreting wireline logs,
  calculating formation properties, evaluating pay zones, estimating reservoir
  quality, or working through log analysis for PNGE courses. Trigger phrases
  include shale volume from GR, Archie water saturation, neutron density
  crossplot, sonic porosity, log interpretation, net pay cutoff, completion
  quality from logs, brittleness index, Sw calculation, Vshale, formation
  evaluation, petrophysical analysis, or Marcellus log interpretation.
---

# Petrophysics and Formation Evaluation

Log interpretation and formation evaluation skill covering the full workflow
from raw log curves to reservoir properties. Calibrated for Appalachian
unconventionals (Marcellus, Utica) with general applicability.

**Important:** Results depend on accurate matrix and fluid parameters. Always
calibrate to core data where available. Equations assume clean sand/carbonate
matrix unless shale corrections are explicitly applied.

---

## Module 1 — Shale Volume (Vsh)

### Gamma Ray Index

```python
def gr_index(gr, gr_clean, gr_shale):
    """
    IGR = (GR - GR_clean) / (GR_shale - GR_clean)
    gr, gr_clean, gr_shale: gamma ray in API units
    Returns IGR clamped to [0, 1]
    """
    igr = (gr - gr_clean) / (gr_shale - gr_clean)
    return max(0.0, min(1.0, igr))
```

### Vsh Equations

| Method | Formula | Use When |
|--------|---------|----------|
| Linear | Vsh = IGR | Quick estimate; overestimates Vsh |
| Larionov (older rock) | Vsh = 0.33 × (2^(2·IGR) - 1) | Paleozoic — Appalachian default |
| Larionov (Tertiary clastic) | Vsh = 0.083 × (2^(3.7·IGR) - 1) | Younger clastics |
| Steiber | Vsh = IGR / (3 - 2·IGR) | Consolidated formations |

```python
def vshale(igr, method="larionov_older"):
    if method == "linear":
        return igr
    elif method == "larionov_older":
        return 0.33 * (2**(2.0 * igr) - 1)
    elif method == "larionov_clastic":
        return 0.083 * (2**(3.7 * igr) - 1)
    elif method == "steiber":
        return igr / (3.0 - 2.0 * igr)
    else:
        raise ValueError(f"Unknown method: {method}")
```

**Appalachian guidance:**
- Marcellus Shale: use `larionov_older` (Devonian). GR_clean ≈ 20 API
  (Onondaga limestone), GR_shale ≈ 200–280 API
- Utica/Point Pleasant: GR_clean ≈ 15–25, GR_shale ≈ 150–200 API

---

## Module 2 — Porosity

### Density Porosity

```python
def phi_density(rhob, rho_matrix=2.65, rho_fluid=1.0):
    """
    phi_D = (rho_matrix - rhob) / (rho_matrix - rho_fluid)
    rhob: bulk density from RHOB log (g/cc)
    rho_matrix: 2.65 sandstone, 2.71 limestone, 2.87 dolomite
    rho_fluid: 1.0 freshwater mud, 1.1 saltwater mud
    """
    return (rho_matrix - rhob) / (rho_matrix - rho_fluid)
```

### Sonic Porosity (Wyllie Time-Average)

```python
def phi_sonic(dt, dt_matrix=55.5, dt_fluid=189.0, cp=1.0):
    """
    phi_S = cp * (dt - dt_matrix) / (dt_fluid - dt_matrix)
    dt: interval transit time from DT log (us/ft)
    dt_matrix: 55.5 sandstone, 47.5 limestone, 43.5 dolomite
    dt_fluid: 189 freshwater, 185 saltwater
    cp: compaction correction (1.0 normally consolidated)
    """
    return cp * (dt - dt_matrix) / (dt_fluid - dt_matrix)

def cp_correction(dt_shale, dt_shale_normal=100.0):
    """Hilchie compaction correction: cp = dt_shale / 100"""
    return dt_shale / dt_shale_normal
```

### Neutron-Density Crossplot Porosity

```python
import math

def phi_nd(phi_n, phi_d):
    """
    Gaymard-Poupon crossplot: phi_ND = sqrt((phi_N^2 + phi_D^2) / 2)
    phi_n: neutron porosity (decimal, NPHI log)
    phi_d: density porosity (decimal)
    In gas zones: phi_N decreases, phi_D increases — crossplot minimizes bias.
    """
    return math.sqrt((phi_n**2 + phi_d**2) / 2.0)
```

### Matrix Parameters Reference

| Lithology | RHOB (g/cc) | DT (us/ft) |
|-----------|-------------|------------|
| Quartz sandstone | 2.65 | 55.5 |
| Calcite limestone | 2.71 | 47.5 |
| Dolomite | 2.87 | 43.5 |
| Marcellus mixed | 2.68–2.72 | 48–52 |
| Shale | 2.45–2.65 | 70–120 |

---

## Module 3 — Water Saturation

### Archie Equation (clean formations)

```python
def sw_archie(rt, phi, rw, a=1.0, m=2.0, n=2.0):
    """
    Sw^n = a * Rw / (phi^m * Rt)
    rt:  true resistivity (ohm-m) from deep log
    phi: porosity (decimal)
    rw:  formation water resistivity (ohm-m)
    a=1.0, m=2.0, n=2.0: tortuosity, cementation, saturation exponents
    """
    return (a * rw / (phi**m * rt))**(1.0 / n)

def rw_from_salinity(salinity_ppm, temp_f):
    """Approximate Rw from NaCl-equivalent salinity and temperature (Arps)."""
    rw_75 = (400000.0 / salinity_ppm)**0.88
    return rw_75 * (75.0 + 6.77) / (temp_f + 6.77)
```

### Simandoux (shaly sand)

```python
def sw_simandoux(rt, phi, rw, vsh, rsh, m=2.0):
    """
    Solves: phi^m * Sw^2 / (0.4*Rw) + Vsh*Sw / Rsh = 1 / Rt
    rsh: shale resistivity (ohm-m)
    vsh: shale volume (decimal)
    Returns the lower root (Sw solution).
    """
    A = phi**m / (0.4 * rw)
    B = vsh / rsh
    C = 1.0 / rt
    discriminant = B**2 + 4 * A * C
    return (-B + discriminant**0.5) / (2.0 * A)
```

### Appalachian Formation Water Resistivity Reference

| Formation | Rw (ohm-m) | TDS equiv. (ppm) | Temp (°F) |
|-----------|-----------|-----------------|----------|
| Marcellus | 0.02–0.05 | 150,000–250,000 | 180–220 |
| Utica / Point Pleasant | 0.01–0.03 | 200,000–300,000 | 200–240 |
| Clinton Sandstone | 0.03–0.08 | 100,000–200,000 | 140–180 |
| Oriskany | 0.02–0.06 | 120,000–220,000 | 160–200 |

---

## Module 4 — Irreducible Sw and Moveable Hydrocarbons

### Bulk Volume Water (Buckles Plot)

```python
def bvw(sw, phi):
    """
    BVW = Sw * phi
    Constant BVW with depth -> formation at irreducible Sw (no water production).
    Varying BVW -> transition zone, expect water production.
    """
    return sw * phi
```

### Timur Equation (permeability from porosity and Swirr)

```python
def permeability_timur(phi, swirr):
    """
    Timur (1968): k = 0.136 * phi^4.4 / swirr^2  (mD)
    Rearranged for Swirr: swirr = sqrt(0.136 * phi^4.4 / k)
    """
    return 0.136 * phi**4.4 / swirr**2

def swirr_timur(phi, k):
    """Irreducible water saturation from porosity and permeability."""
    return (0.136 * phi**4.4 / k)**0.5
```

### Moveable Hydrocarbon Index

```python
def mhi(sw, sxo):
    """
    MHI = Sw / Sxo
    sxo: flushed zone saturation from shallow resistivity (Rxo)
    MHI < 0.7: good mobility   MHI > 0.9: tight, little movability
    """
    return sw / sxo
```

---

## Module 5 — Brittleness Index (Completion Quality)

### Rickman et al. (2008) Brittleness

```python
def brittleness_rickman(ym_gpa, pr,
                         ym_brit=70.0, ym_duct=15.0,
                         pr_brit=0.15, pr_duct=0.40):
    """
    Brittleness (%) = 50 * (YM_norm + PR_norm) * 100
    ym_gpa: dynamic Young's modulus (GPa) from sonic
    pr: Poisson's ratio from sonic
    High brittleness (>40%): good frac candidate
    Low brittleness (<20%): ductile, poor frac response
    """
    ym_n = max(0.0, min(1.0, (ym_gpa - ym_duct) / (ym_brit - ym_duct)))
    pr_n = max(0.0, min(1.0, (pr - pr_duct) / (pr_brit - pr_duct)))
    return 0.5 * (ym_n + pr_n) * 100.0
```

### Dynamic Elastic Moduli from Logs

```python
def dynamic_moduli(dtc, dts, rhob):
    """
    dtc: compressional slowness (us/ft)
    dts: shear slowness (us/ft)
    rhob: bulk density (g/cc)
    Returns: (E_gpa, nu) dynamic Young's modulus and Poisson's ratio
    """
    vp = 304800.0 / dtc   # ft/s
    vs = 304800.0 / dts   # ft/s
    rho = rhob * 1000.0   # kg/m3
    vp_m = vp * 0.3048    # m/s
    vs_m = vs * 0.3048    # m/s
    mu = rho * vs_m**2    # shear modulus (Pa)
    r2 = (vp_m / vs_m)**2
    E = mu * (3*r2 - 4) / (r2 - 1) / 1e9   # GPa
    nu = (r2 - 2.0) / (2.0 * (r2 - 1.0))
    return E, nu
```

**Note:** Dynamic-to-static correction: E_static ≈ 0.4–0.7 × E_dynamic for
shales. Use core measurements to calibrate before geomechanical modeling.

**Marcellus brittleness reference:**
| Interval | E (GPa) | PR | Brittleness (%) |
|----------|---------|-----|----------------|
| Upper Marcellus | 20–35 | 0.22–0.30 | 25–45 |
| Lower Marcellus | 30–50 | 0.18–0.25 | 40–60 |
| Union Springs | 35–55 | 0.20–0.28 | 40–60 |
| Onondaga Limestone | 50–70 | 0.25–0.30 | 55–75 |

---

## Module 6 — Net Pay Cutoffs

```python
def net_pay(depths, vsh_log, phi_log, sw_log,
            vsh_cut=0.35, phi_cut=0.05, sw_cut=0.60,
            dz=0.5):
    """
    Returns gross thickness, net pay thickness, and N/G ratio.
    dz: sample interval (ft) — default 0.5 ft for digital logs
    """
    gross = len(depths) * dz
    pay_intervals = [(d, vsh, phi, sw)
                     for d, vsh, phi, sw
                     in zip(depths, vsh_log, phi_log, sw_log)
                     if vsh <= vsh_cut and phi >= phi_cut and sw <= sw_cut]
    net = len(pay_intervals) * dz
    return {
        "gross_ft": gross,
        "net_ft": net,
        "net_gross": net / gross if gross > 0 else 0,
        "pay_intervals": pay_intervals
    }
```

**Typical Appalachian cutoffs:**
| Parameter | Conventional gas | Marcellus | Utica/PP |
|-----------|-----------------|-----------|---------|
| Vsh max | 0.35 | 0.50 | 0.60 |
| Porosity min | 0.06 | 0.04 | 0.04 |
| Sw max | 0.60 | 0.75 | 0.70 |

---

## Output Format

```
## Formation Evaluation — [Formation], [Well Name/API]
**Interval:** X,XXX – X,XXX ft MD | **Logged:** [curves available]

### Log Quality Check
| Curve | Min | Max | Mean | Issues |
|-------|-----|-----|------|--------|
| GR (API) | | | | |
| RHOB (g/cc) | | | | |
| NPHI (frac) | | | | |
| RT (ohm-m) | | | | |

### Petrophysical Summary (Net Pay)
| Property | Value | Method |
|----------|-------|--------|
| Net pay (ft) | | Vsh/phi/Sw cutoffs |
| Average phi_ND | | N-D crossplot |
| Average Sw | | Archie |
| Swirr estimate | | Buckles / Timur |
| Brittleness avg (%) | | Rickman |

### Parameter Assumptions
- GR_clean / GR_shale: XX / XX API
- Matrix: [sandstone / limestone / mixed]
- Rw: X.XX ohm-m (source: [DST / database / salinity gradient])
- a / m / n: 1.0 / 2.0 / 2.0 (note if shaly-sand correction applied)

### Confidence: [HIGH / MEDIUM / LOW]
[Note any data quality issues, missing curves, or calibration gaps]
```

---

## Error Handling

| Condition | Cause | Action |
|-----------|-------|--------|
| phi_D < 0 | RHOB > rho_matrix (heavy mineral or bad hole) | Check caliper; flag washout |
| Sw > 1.0 | Rw too low or Rt too high | Verify Rw; check invasion |
| Sw < 0 | Negative discriminant (Simandoux) | Use Archie or Indonesian equation |
| Highly variable BVW | Transition zone | Flag water production risk |
| Brittleness > 100% | Moduli out of range | Check DTS/DTC data quality |

---

## Caveats

- Archie's equation assumes shale-free formation. In organic shales (Marcellus,
  Utica), TOC contributes independent conductivity — Archie Sw is unreliable.
  Use as a relative indicator only; calibrate to core.
- Dynamic Young's modulus from sonic logs exceeds static lab values by 20–100%.
  Apply dynamic-to-static correction before using in geomechanical or frac models.
- Larionov corrections reduce IGR-to-Vsh conversion; linear method overestimates
  shale content and underestimates net pay.
- All cutoff values are formation-specific. Values here are starting points —
  always calibrate to production data and core measurements.
- Log quality in horizontal wells can be poor due to invasion, tool standoff,
  and borehole geometry; evaluate LQC before interpretation.
