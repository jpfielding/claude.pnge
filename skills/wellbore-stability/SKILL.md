---
name: wellbore-stability
description: >
  Perform wellbore stability analysis and geomechanics calculations for
  drilling and completions engineering. Covers in-situ principal stress
  estimation, pore pressure gradient, overburden stress from density logs,
  minimum and maximum horizontal stress estimation, mud weight window
  calculation, shear failure using Mohr-Coulomb and Mogi-Coulomb criteria,
  tensile fracture initiation pressure, borehole breakout analysis, and safe
  drilling window design for vertical and deviated wells. Use this skill when
  the user needs to determine safe mud weight window, assess wellbore stability
  risk, calculate principal stresses at depth, evaluate breakout width, design
  casing seat depth based on fracture gradient, or work through geomechanics
  problems for PNGE or formation evaluation courses. Trigger for phrases like
  "mud weight window", "wellbore stability analysis", "breakout width
  calculation", "Mohr-Coulomb failure criterion", "minimum horizontal stress
  estimate", "safe mud density", "fracture gradient from logs", "borehole
  stability", "in-situ stress state", or "UCS from log data". Produces stress
  state tables and drilling window plots described in text.
---

# Wellbore Stability and Geomechanics Calculator

Geomechanics skill for wellbore stability analysis, drilling window design, and
in-situ stress characterization. Covers the full workflow from log-derived
overburden stress through Kirsch borehole wall stresses to safe mud weight
selection. Calibrated for Appalachian/Marcellus conditions.

**Important:** Wellbore stability analysis requires calibration to local well
data. The Appalachian reference parameters provided here are representative but
basin conditions vary significantly. Always calibrate against offset well data
(formation tests, mud logs, caliper, image logs) before applying to a new
well. Consult a geomechanics specialist for HPHT or complex well paths.

---

## Module 1 — Vertical (Overburden) Stress

### Capabilities

- Overburden stress from density log integration
- Simplified overburden estimation from average density assumption
- Effective overburden stress using Biot coefficient
- PNGE applications: input to horizontal stress models, pore pressure prediction,
  fracture gradient calculation

### Overburden Stress Definition

The vertical (overburden) stress S_v is the weight of all rock and fluid above
the point of interest:

```
S_v = integral[rho(z) * g * dz]  from 0 to z
```

In field units (psi), with depth z in feet and density RHOB in g/cc:
```
S_v(psi) = integral[RHOB(z) * 0.4335 * dz]
```

Where 0.4335 converts g/cc * ft to psi (= 0.4335 psi per ft per g/cc).

**Simplified (average density):**
```
S_v = rho_avg * 0.4335 * z    (psi, z in ft, rho in g/cc)
```

### Typical Overburden Gradients by Depth

| Depth Range | Typical Gradient | Notes |
|-------------|-----------------|-------|
| 0-3,000 ft | 0.85-0.95 psi/ft | Shallow, lower density sediments |
| 3,000-7,000 ft | 0.95-1.05 psi/ft | Normal compaction |
| 7,000-12,000 ft | 1.0-1.1 psi/ft | Fully compacted, higher density |
| Appalachian (Marcellus depth) | ~1.0-1.05 psi/ft | At 6,000-8,500 ft |

### Log-Based Overburden Calculation

```python
import math

def overburden_from_log(depths_ft, rhob_gcc):
    """
    Calculate overburden stress from density log.
    depths_ft: list of depth values (measured from surface, ft)
    rhob_gcc: list of bulk density values at each depth (g/cc)
    Returns: list of S_v values in psi at each depth
    """
    conv = 0.4335  # psi/(ft * g/cc)
    Sv = [0.0]
    for i in range(1, len(depths_ft)):
        dz = depths_ft[i] - depths_ft[i-1]
        rho_avg = (rhob_gcc[i] + rhob_gcc[i-1]) / 2
        Sv.append(Sv[-1] + rho_avg * conv * dz)
    return Sv

# Example: 3-layer overburden for 8,000 ft well
depths = [0, 2000, 5000, 8000]
rhob   = [2.10, 2.45, 2.60, 2.65]  # g/cc (increases with compaction)

Sv = overburden_from_log(depths, rhob)
print("Depth (ft) | Sv (psi) | Sv gradient (psi/ft)")
print("-" * 50)
for i, (d, sv) in enumerate(zip(depths, Sv)):
    grad = sv / d if d > 0 else 0
    print(f"{d:10,} | {sv:8,.0f} | {grad:.4f}")
```

### Effective Overburden Stress

The effective overburden (Terzaghi effective stress principle):
```
sigma_v = S_v - alpha * P_p
```

Where alpha = Biot coefficient (0.6-1.0 for porous rock; 1.0 is conservative).

For Marcellus shale: alpha = 0.7-0.9 (lower than clean sandstone due to low porosity).

---

## Module 2 — Pore Pressure

### Capabilities

- Hydrostatic pore pressure for normal-pressured formations
- Eaton method for pore pressure from sonic or resistivity logs
- Equivalent mud weight (EMW) conversion
- PNGE applications: effective stress calculation, mud weight floor, cap rock integrity

### Normal Pore Pressure Gradients

| Fluid Type | Gradient (psi/ft) | Gradient (ppg equivalent) |
|------------|-----------------|--------------------------|
| Fresh water | 0.433 | 8.33 |
| Seawater | 0.442 | 8.5 |
| Formation brine (typical) | 0.452-0.465 | 8.7-8.9 |
| Marcellus brine (high salinity) | 0.462-0.480 | 8.9-9.2 |

**Marcellus shale context (WV):** The Marcellus at 6,000-8,500 ft TVD in
West Virginia is generally normally pressured or slightly overpressured in
the core of the basin. Use 0.46-0.47 psi/ft as a reasonable default.

### Eaton Method (Resistivity-Based)

Overpressure from compaction disequilibrium can be detected from resistivity
log trends:

```
P_p = S_v - (S_v - P_p_normal) * (Ro/Rn)^1.2
```

Where:
- Ro = observed resistivity at depth of interest (ohm-m)
- Rn = normal (expected) resistivity at same depth from trend line (ohm-m)
- Exponent 1.2 is Eaton's empirical value (commonly used; range 0.6-2.0)

**Sonic (interval transit time) version:**
```
P_p = S_v - (S_v - P_p_normal) * (DTCn/DTC)^3.0
```

Where DTC = observed transit time, DTCn = normal trend transit time.

```python
def eaton_resistivity(Sv_psi, Pp_normal_psi, Ro, Rn, n=1.2):
    """
    Eaton pore pressure from resistivity log.
    Sv_psi: overburden stress (psi)
    Pp_normal_psi: normal pore pressure at this depth (psi)
    Ro: observed resistivity (ohm-m)
    Rn: normal trend resistivity (ohm-m)
    n: Eaton exponent (default 1.2)
    """
    Pp = Sv_psi - (Sv_psi - Pp_normal_psi) * (Ro / Rn)**n
    return Pp

# Example: 7,500 ft depth
Sv = 7875
Pp_n = 7500 * 0.46
Ro = 8.0   # observed resistivity
Rn = 12.0  # normal trend (higher = more compacted = normal)

Pp_calc = eaton_resistivity(Sv, Pp_n, Ro, Rn)
EMW = Pp_calc / (7500 * 0.052)
print(f"Eaton pore pressure: {Pp_calc:.0f} psi")
print(f"Equivalent mud weight: {EMW:.2f} ppg")
```

### Equivalent Mud Weight (EMW)

Convert any pressure to equivalent mud weight at a given depth:
```
EMW (ppg) = P (psi) / (0.052 * depth_ft)
```

---

## Module 3 — Horizontal Stress Estimation

### Capabilities

- Minimum horizontal stress (S_hmin) from poroelastic model
- Maximum horizontal stress (S_Hmax) from stress polygon (Zoback frictional limit)
- Stress regime classification
- Appalachian reference stress gradients and stress orientation
- PNGE applications: hydraulic fracture orientation, wellbore stability design

### Poroelastic Model for S_hmin

The minimum horizontal stress from poroelastic theory (for a laterally
constrained basin with no tectonic strain):

```
S_hmin = [nu/(1-nu)] * (S_v - alpha*P_p) + alpha*P_p + S_tect
```

Where:
- nu = Poisson's ratio of the rock
- alpha = Biot coefficient
- P_p = pore pressure
- S_tect = tectonic stress component (can be positive or negative)

For a basin with no active tectonic loading (S_tect = 0):
```
S_hmin = [nu/(1-nu)] * (S_v - alpha*P_p) + alpha*P_p
```

### Frictional Equilibrium (Zoback Stress Polygon)

The maximum horizontal stress is bounded by the frictional strength of
pre-existing faults. For coefficient of friction mu_f:

```
(S1/S3)_max = [(mu_f^2 + 1)^0.5 + mu_f]^2
```

Typical rock friction coefficient: mu_f = 0.6-0.8 (Byerlee's law).

### Appalachian/Marcellus Reference Stress State

The Appalachian basin is in a **strike-slip faulting regime** in the deep
Devonian/Mississippian section where the Marcellus resides:
```
S_Hmax > S_v > S_hmin
```

**Appalachian reference stress gradients (TVD depth range 6,000-9,000 ft):**

| Stress Component | Gradient (psi/ft) | Gradient (ppg) | Notes |
|-----------------|------------------|----------------|-------|
| S_v (overburden) | 1.00-1.05 | 19.2-20.2 | From density log |
| P_p (pore pressure) | 0.46-0.47 | 8.85-9.04 | Normal-pressured WV |
| S_hmin | 0.65-0.75 | 12.5-14.4 | From ISIP/closure data |
| S_Hmax | 0.80-0.95 | 15.4-18.3 | From image logs, LOT |
| S_Hmax orientation | N60-80E | — | ENE-WSW, consistent regionally |

**Source:** Multiple published studies on Appalachian/Marcellus geomechanics
(Lash and Engelder, 2011; Gale et al., 2014; Zoback et al., various).

```python
def horizontal_stress_poroelastic(Sv, Pp, nu, alpha, S_tect=0):
    """
    Estimate minimum horizontal stress using poroelastic model.
    All pressures in psi, same depth.
    S_tect: tectonic stress additive term (psi). Positive = compression.
    """
    sigma_v_eff = Sv - alpha * Pp
    Shmin = (nu / (1 - nu)) * sigma_v_eff + alpha * Pp + S_tect
    return Shmin

# Marcellus at 7,500 ft TVD
depth = 7500
Sv = depth * 1.02
Pp = depth * 0.465
nu = 0.25
alpha = 0.8

Shmin_pe = horizontal_stress_poroelastic(Sv, Pp, nu, alpha)
Shmin_ref_lo = depth * 0.65
Shmin_ref_hi = depth * 0.75
Shmax_est = depth * 0.87

print(f"Depth: {depth} ft")
print(f"S_v:   {Sv:,.0f} psi  ({Sv/depth:.3f} psi/ft)")
print(f"P_p:   {Pp:,.0f} psi  ({Pp/depth:.3f} psi/ft)")
print(f"\nPoroelastic S_hmin (no tectonic): {Shmin_pe:,.0f} psi ({Shmin_pe/depth:.3f} psi/ft)")
print(f"Appalachian reference range:      {Shmin_ref_lo:,.0f}-{Shmin_ref_hi:,.0f} psi")
print(f"Estimated S_Hmax:                 {Shmax_est:,.0f} psi ({Shmax_est/depth:.3f} psi/ft)")

if Sv > Shmax_est > Shmin_pe:
    regime = "NORMAL FAULTING (S_v > S_Hmax > S_hmin)"
elif Shmax_est > Sv > Shmin_pe:
    regime = "STRIKE-SLIP (S_Hmax > S_v > S_hmin)"
elif Shmax_est > Shmin_pe > Sv:
    regime = "REVERSE FAULTING (S_Hmax > S_hmin > S_v)"
else:
    regime = "INDETERMINATE"
print(f"Stress regime: {regime}")
```

---

## Module 4 — Mud Weight Window (Kirsch Equations)

### Capabilities

- Kirsch equations for stress concentration at borehole wall
- Minimum mud weight to prevent shear failure (borehole breakout)
- Maximum mud weight to prevent tensile fracture initiation
- Complete mud weight window calculation with risk classification
- PNGE applications: MW selection, casing seat design, well planning

### Kirsch Equations for Vertical Borehole

For a vertical borehole in a biaxial far-field stress (S_Hmax, S_hmin), the
total stresses at the borehole wall (r = r_w) at azimuth theta from S_Hmax:

**Total hoop (tangential) stress:**
```
sigma_theta = (S_Hmax + S_hmin) - 2*(S_Hmax - S_hmin)*cos(2*theta) - P_mud
```

**Total radial stress (at borehole wall):**
```
sigma_r = P_mud    (boundary condition — support pressure equals mud pressure)
```

**Effective stresses** (subtract pore pressure where formation is permeable):
```
sigma_theta_eff = sigma_theta - P_p
sigma_r_eff = sigma_r - P_p = P_mud - P_p
```

### Critical Azimuths

**At theta = 90 degrees (S_hmin direction — breakout location):**
The hoop stress is maximum compressive here:
```
sigma_theta_max = 3*S_Hmax - S_hmin - P_mud
sigma_theta_eff(breakout) = 3*S_Hmax - S_hmin - P_mud - P_p
```

**At theta = 0 degrees (S_Hmax direction — tensile fracture location):**
The hoop stress is minimum here:
```
sigma_theta_min = 3*S_hmin - S_Hmax - P_mud
sigma_theta_eff(frac) = 3*S_hmin - S_Hmax - P_mud - P_p
```

### Failure Criteria

**Shear failure (breakout) — Mohr-Coulomb:**

Breakout initiates when the effective hoop stress exceeds the rock strength.
With sigma_r_eff = 0 at the borehole wall (free surface approximation):

```
Breakout when: sigma_theta_eff(breakout) > UCS
i.e., 3*S_Hmax - S_hmin - P_mud - P_p > UCS
```

Solving for minimum mud weight to prevent breakout:
```
P_mud_min(shear) = 3*S_Hmax - S_hmin - P_p - UCS
```

**Tensile fracture initiation:**

Tensile fracture initiates when effective hoop stress at theta=0 goes
sufficiently tensile to overcome the rock's tensile strength T_0:

```
Frac initiates when: sigma_theta_eff(frac) < -T_0
i.e., 3*S_hmin - S_Hmax - P_mud - P_p < -T_0
```

Solving for maximum mud weight:
```
P_mud_max = 3*S_hmin - S_Hmax - P_p + T_0
```

**Conservative upper bound** (zero tensile strength):
```
P_mud_max_conservative = 3*S_hmin - S_Hmax - P_p
```

And the ultimate upper limit is always S_hmin (fractures extend when
wellbore pressure equals the minimum principal stress):
```
P_mud_upper_limit = S_hmin  (absolute maximum — reopens existing fractures)
```

In practice: use min(3*S_hmin - S_Hmax - P_p + T_0, S_hmin).

### Full Mud Weight Window Calculation

```python
import math

def mud_weight_window(depth_ft, Sv_grad, Shmin_grad, SHmax_grad, Pp_grad,
                      UCS_psi, phi_deg=30, T0_psi=None, alpha=1.0):
    """
    Calculate safe mud weight window for a vertical borehole.
    All gradient inputs in psi/ft.
    Returns a dict with MW limits in psi and ppg.
    """
    Sv    = Sv_grad    * depth_ft
    Shmin = Shmin_grad * depth_ft
    SHmax = SHmax_grad * depth_ft
    Pp    = Pp_grad    * depth_ft
    T0    = T0_psi if T0_psi is not None else 0.1 * UCS_psi

    # Mohr-Coulomb friction
    phi = math.radians(phi_deg)
    q = (1 + math.sin(phi)) / (1 - math.sin(phi))

    # Minimum MW: prevent shear failure at breakout azimuth
    MW_min_shear = 3 * SHmax - Shmin - Pp - UCS_psi

    # Minimum MW: prevent kick (must exceed pore pressure)
    MW_min_kick = Pp

    MW_min = max(MW_min_shear, MW_min_kick)

    # Maximum MW: prevent tensile fracture
    MW_max_kirsch = 3 * Shmin - SHmax - Pp + T0
    MW_max_absolute = Shmin  # hard upper limit
    MW_max = min(MW_max_kirsch, MW_max_absolute)

    def ppg(P): return P / (0.052 * depth_ft) if depth_ft > 0 else 0

    window_psi = MW_max - MW_min
    window_ppg = ppg(MW_max) - ppg(MW_min)

    return {
        "depth_ft": depth_ft,
        "Sv_psi": Sv, "Shmin_psi": Shmin, "SHmax_psi": SHmax, "Pp_psi": Pp,
        "UCS_psi": UCS_psi, "T0_psi": T0,
        "MW_min_psi": MW_min, "MW_max_psi": MW_max,
        "MW_min_ppg": ppg(MW_min), "MW_max_ppg": ppg(MW_max),
        "MW_min_kick_psi": MW_min_kick, "MW_min_kick_ppg": ppg(MW_min_kick),
        "MW_min_shear_psi": MW_min_shear, "MW_min_shear_ppg": ppg(max(MW_min_shear, 0)),
        "window_psi": window_psi, "window_ppg": window_ppg,
    }

# Marcellus at 7,500 ft TVD (WV) — base case
res = mud_weight_window(
    depth_ft=7500,
    Sv_grad=1.02,
    Shmin_grad=0.70,
    SHmax_grad=0.87,
    Pp_grad=0.465,
    UCS_psi=10000,
    phi_deg=30,
    alpha=0.8
)

print(f"{'='*60}")
print(f"WELLBORE STABILITY — {res['depth_ft']:,} ft TVD")
print(f"{'='*60}")
print(f"S_v:    {res['Sv_psi']:6,.0f} psi  |  {res['Sv_psi']/res['depth_ft']:.3f} psi/ft")
print(f"S_Hmax: {res['SHmax_psi']:6,.0f} psi  |  {res['SHmax_psi']/res['depth_ft']:.3f} psi/ft")
print(f"S_hmin: {res['Shmin_psi']:6,.0f} psi  |  {res['Shmin_psi']/res['depth_ft']:.3f} psi/ft")
print(f"P_p:    {res['Pp_psi']:6,.0f} psi  |  {res['Pp_psi']/res['depth_ft']:.3f} psi/ft")
print()
print(f"MW min (kick):   {res['MW_min_kick_ppg']:.2f} ppg")
print(f"MW min (shear):  {res['MW_min_shear_ppg']:.2f} ppg  <- CONTROLS")
print(f"MW max (frac):   {res['MW_max_ppg']:.2f} ppg")
print(f"Window:          {res['window_ppg']:.2f} ppg")
risk = "LOW" if res['window_ppg'] > 1.5 else ("MODERATE" if res['window_ppg'] > 0.5 else "HIGH")
print(f"Risk:            {risk}")
```

---

## Module 5 — Breakout Analysis and UCS from Logs

### Capabilities

- Breakout angular half-width from Mohr-Coulomb criterion
- UCS estimation from sonic log (McNally, Militzer correlations)
- Breakout depth (radial extent) estimation
- PNGE applications: caliper interpretation, image log analysis, strength calibration

### Breakout Angular Width

The angular half-width of borehole breakout is the angle from the S_hmin
azimuth to the edge of the failed zone. Beyond this angle, the borehole
wall is intact:

Breakout occurs at azimuth theta where sigma_theta_eff > UCS. Setting
sigma_theta_eff(theta) = UCS and solving:

```
cos(2*theta_BO) = [(S_Hmax + S_hmin) - P_mud - P_p - UCS] / [2*(S_Hmax - S_hmin)]
```

- If RHS > 1: no breakout (stable at this MW)
- If RHS < -1: entire wall fails (highly unstable)
- Otherwise: theta_BO is measured from S_Hmax direction; breakout half-width
  from S_hmin direction = 90 - theta_BO

Total breakout width = 2 * halfwidth.

### UCS from Sonic Log

When no core data is available, estimate UCS from the sonic log DTC
(interval transit time, us/ft):

**McNally (1987) — shales and mudstones:**
```
UCS_MPa = 1200 * exp(-0.036 * DTC_usft)
```

**Militzer and Stoll (1973) — sandstones:**
```
UCS_MPa = (7682 / DTC_usft)^1.82
```

**Typical Marcellus DTC range:** 55-75 us/ft, giving UCS = 8,000-18,000 psi.

```python
import math

def ucs_from_dtc_shale(dtc_usft):
    """McNally (1987) UCS for shales from sonic log DTC."""
    UCS_MPa = 1200 * math.exp(-0.036 * dtc_usft)
    UCS_psi = UCS_MPa * 145.04
    return UCS_MPa, UCS_psi

def breakout_halfwidth_deg(SHmax, Shmin, Pp, Pmud, UCS_psi):
    """
    Breakout half-width from S_hmin azimuth (degrees).
    Returns 0 if no breakout, 90 if entire wall fails.
    All inputs in psi.
    """
    num = (SHmax + Shmin) - Pmud - Pp - UCS_psi
    den = 2 * (SHmax - Shmin)
    if abs(den) < 1e-6:
        return 0.0
    cos_2theta = num / den
    if cos_2theta > 1.0:
        return 0.0   # no breakout
    if cos_2theta < -1.0:
        return 90.0  # entire wall fails
    theta_from_SHmax = math.degrees(math.acos(cos_2theta)) / 2
    halfwidth = 90.0 - theta_from_SHmax
    return max(0.0, halfwidth)

# Marcellus sensitivity: MW=9.5 ppg at 7,500 ft
depth = 7500
SHmax = 0.87 * depth
Shmin = 0.70 * depth
Pp = 0.465 * depth
Pmud = 9.5 * 0.052 * depth

print("UCS and Breakout Width Sensitivity (MW = 9.5 ppg, 7,500 ft)")
print("-" * 65)
print(f"{'DTC (us/ft)':>12} | {'UCS (psi)':>10} | {'UCS (MPa)':>9} | {'Breakout HW (deg)':>17} | {'Total (deg)':>11}")
print("-" * 65)
for dtc in [55, 60, 65, 70, 75]:
    ucs_MPa, ucs_psi = ucs_from_dtc_shale(dtc)
    hw = breakout_halfwidth_deg(SHmax, Shmin, Pp, Pmud, ucs_psi)
    print(f"{dtc:12.0f} | {ucs_psi:10,.0f} | {ucs_MPa:9.0f} | {hw:17.1f} | {2*hw:11.1f}")
```

---

## Module 6 — Wellbore Stability Risk Classification

### Risk Classification Framework

| Window (ppg) | Risk Level | Typical Field Response |
|-------------|-----------|----------------------|
| > 2.0 | VERY LOW | Standard practices, monitor caliper |
| 1.0-2.0 | LOW | Standard + caliper log every string |
| 0.5-1.0 | MODERATE | Enhanced monitoring, ECD management, real-time PWD |
| 0.25-0.5 | HIGH | Managed pressure drilling, careful ECD control |
| < 0.25 | CRITICAL | MPD required, smaller MW increments, review casing architecture |

### Risk Factors Narrowing the Window

| Risk Factor | Effect | Mitigation |
|-------------|--------|------------|
| Natural fractures | Reduces effective rock strength | Lower max MW limit; use weakened UCS |
| Swelling clays (illite/smectite) | Time-dependent weakening | Inhibitive mud (KCl), minimize exposure time |
| Laminated shale | Bedding-parallel failure | Check well azimuth relative to bedding dip |
| High tectonic stress (SHmax/Shmin > 1.5) | Wide anisotropy, larger breakout zone | Increase MW; evaluate deviated azimuth |
| Abnormal pore pressure | Shifts both bounds | Accurate Pp prediction is critical |
| High ECD during drilling | Effective MW increase | Optimize flow rate and pipe rotation |

### Deviated Well Stability

For deviated or horizontal wells, the effective stress concentration at the
borehole wall depends on wellbore inclination and azimuth relative to all
three principal stresses. Key points for Marcellus horizontal wells:

- **NW-SE azimuth wells** (perpendicular to ENE S_Hmax): Generally the most
  stable orientation. S_Hmax acts axially along the borehole, reducing stress
  concentration at the borehole wall.
- **ENE-WSW azimuth wells** (parallel to S_Hmax): Higher stress concentration;
  avoid for horizontal wells if possible.
- For a full 3D stability analysis use the Aadnoy and Ong (2003) formulation
  or a dedicated geomechanics tool. This skill covers the vertical well case.

### Stability Profile With Depth

```python
def stability_profile(depths_ft, Sv_grad, Shmin_grad, SHmax_grad,
                       Pp_grad, UCS_psi, T0_psi=None):
    """
    Print stability summary at multiple depths.
    """
    T0 = T0_psi if T0_psi else 0.1 * UCS_psi
    print(f"{'Depth':>7} | {'MW_min':>7} | {'MW_max':>7} | {'Window':>7} | {'Risk'}")
    print(f"{'(ft)':>7} | {'(ppg)':>7} | {'(ppg)':>7} | {'(ppg)':>7} | ")
    print("-" * 55)
    for d in depths_ft:
        res = mud_weight_window(
            depth_ft=d, Sv_grad=Sv_grad, Shmin_grad=Shmin_grad,
            SHmax_grad=SHmax_grad, Pp_grad=Pp_grad,
            UCS_psi=UCS_psi, T0_psi=T0
        )
        risk = "LOW" if res['window_ppg'] > 1.5 else ("MOD" if res['window_ppg'] > 0.5 else "HIGH")
        print(f"{d:7,} | {res['MW_min_ppg']:7.2f} | {res['MW_max_ppg']:7.2f} | {res['window_ppg']:7.2f} | {risk}")

# Marcellus well depth profile
stability_profile(
    depths_ft=[4000, 5000, 6000, 7000, 7500, 8000, 8500],
    Sv_grad=1.02, Shmin_grad=0.70, SHmax_grad=0.87, Pp_grad=0.465,
    UCS_psi=10000
)
```

---

## Workflow Summary

### Step 1 — Identify Calculation

| User Request | Module |
|--------------|--------|
| Overburden gradient, density log integration | Module 1 |
| Pore pressure, EMW, Eaton method | Module 2 |
| Horizontal stress, stress regime, S_hmin/S_Hmax | Module 3 |
| Mud weight window, breakout limit, fracture limit | Module 4 |
| Breakout width, UCS from logs, image log | Module 5 |
| Risk classification, deviated well, stability profile | Module 6 |

### Step 2 — Gather Inputs

**Minimum required:**
- Depth (TVD, ft)
- At least one of: density log, average density, or Sv gradient
- Pore pressure (or assume hydrostatic)

**For full window calculation, also needed:**
- S_hmin (from ISIP, XLOT, or estimated gradient)
- S_Hmax (from image log, stress polygon, or estimated gradient)
- UCS (from core, DTC log, or published range for formation)

If user lacks specific data, apply Appalachian reference gradients and state
clearly that results are reference estimates pending calibration.

### Step 3 — Calculate

Follow the module sequence: S_v → P_p → effective stresses → S_hmin → S_Hmax
→ Kirsch equations → MW window → risk classification. Use Python (stdlib:
math, statistics). Show each step with units and intermediate values.

### Step 4 — Output

1. **Input parameters table** — all values with units and source (user/default)
2. **In-situ stress state table** — S_v, S_Hmax, S_hmin, P_p in psi, psi/ft, ppg
3. **Kirsch hoop stress at critical azimuths**
4. **Mud weight window table** — min/max in psi and ppg, controlling constraint
5. **Risk classification** — window width and risk level
6. **Recommendations** — operating MW, ECD limit, monitoring requirements
7. **Caveats** — data quality, calibration needs, simplifying assumptions

---

## Output Format

```
## Wellbore Stability Analysis — [Well or Depth]

### In-Situ Stress State
| Stress | psi | MPa | psi/ft | ppg |
|--------|-----|-----|--------|-----|
| S_v | ... | ... | ... | ... |
| S_Hmax | ... | ... | ... | ... |
| S_hmin | ... | ... | ... | ... |
| P_p | ... | ... | ... | ... |

Stress regime: [NORMAL / STRIKE-SLIP / REVERSE FAULTING]

### Mud Weight Window
| Limit | psi | ppg | Controlling Factor |
|-------|-----|-----|--------------------|
| MW min (kick prevention) | ... | ... | Pore pressure balance |
| MW min (shear failure) | ... | ... | Kirsch + Mohr-Coulomb |
| MW max (fracture initiation) | ... | ... | Kirsch + tensile criterion |
| Window width | — | ... | MW_max - MW_min |

**Risk Level:** [LOW / MODERATE / HIGH / CRITICAL]
**Recommended Operating MW:** [X.X ppg]
**Maximum ECD:** [X.X ppg (= MW_max - 0.3 ppg safety margin)]

**Summary:** [2-3 sentences on stability outlook and recommendation]

**Caveats:**
- [Data source: "Appalachian reference gradients used — calibrate to offset wells"]
- [Assumptions: "Vertical borehole assumed — deviated well requires 3D analysis"]
- [Rock strength: "UCS from log correlation — validate against core if available"]
```

---

## Error Handling

| Condition | Action |
|-----------|--------|
| MW_min > MW_max (no safe window) | Report zero window; recommend MPD, review casing architecture |
| MW_min_shear < 0 (very strong rock) | Kick prevention governs; breakout will not occur |
| UCS not provided | Use Marcellus range 8,000-18,000 psi; report sensitivity at low/mid/high |
| Only S_hmin available (not S_Hmax) | Use stress polygon upper bound; label as bounding analysis |
| Depth given as measured depth (MD) | Request TVD; use inclination to estimate TVD if available |
| Pore pressure given in ppg | Convert: Pp_psi = ppg * 0.052 * depth_ft; confirm with user |
| Deviated well request | Perform vertical-well analysis; note 3D extension is needed for deviated |

---

## Units Reference

| Quantity | Field Unit | SI Unit | Conversion |
|----------|-----------|---------|------------|
| Stress/Pressure | psi | MPa | 1 psi = 0.006895 MPa |
| Depth | ft | m | 1 ft = 0.3048 m |
| Density | g/cc | kg/m^3 | 1 g/cc = 1,000 kg/m^3 |
| Mud weight | ppg | kg/m^3 | 1 ppg = 119.8 kg/m^3 |
| Pressure gradient | psi/ft | kPa/m | 1 psi/ft = 22.62 kPa/m |
| EMW conversion | ppg | — | EMW(ppg) = P(psi) / (0.052 * depth_ft) |
| UCS | psi | MPa | 1,000 psi = 6.895 MPa |
| Sonic log | us/ft | us/m | 1 us/ft = 3.281 us/m |
| Angle | degrees | radians | 1 deg = pi/180 rad |

See `references/equations.md` for the complete Kirsch derivation, full
Mohr-Coulomb and Mogi-Coulomb failure criteria, and Appalachian basin
reference stress gradient table.
