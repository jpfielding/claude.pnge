---
name: tubing-design
description: >
  Perform production tubing string design and force analysis for oil and gas
  wells. Covers the four fundamental forces affecting tubing movement: thermal
  expansion and contraction from temperature change, ballooning from internal
  and external pressure changes, piston effect at packer due to area change,
  and buckling including sinusoidal and helical onset using Lubinski equations
  and neutral point calculation. Analyzes tubing movement for free, anchored,
  and partially anchored completions, calculates required seal assembly stroke
  length, evaluates helical pitch and casing contact lateral force, and sizes
  velocity strings for liquid-loaded gas wells. Also covers API tubing grades
  and dimensions, downhole safety valve setting depth, and packer selection
  criteria. Use when designing production tubing strings, calculating tubing
  movement from stimulation or production temperature and pressure loads,
  evaluating buckling risk, sizing seal assemblies, or working through tubing
  force problems for PNGE completions courses. Trigger phrases include tubing
  movement, buckling analysis, Lubinski equations, piston effect, ballooning,
  neutral point, velocity string, tubing force analysis, packer load, thermal
  tubing expansion, or seal assembly length.
---

# Production Tubing Design and Force Analysis

Completions engineering skill for production tubing string design, force
analysis, and buckling evaluation per Lubinski et al. (1962).

**Important:** Tubing force analysis is sensitive to completion geometry.
Always verify packer type (free, anchored, set-on-tension/compression) before
applying load case equations. For HP/HT wells, use dedicated software
(WellCat, StressCheck, or equivalent).

---

## Module 1 — Tubing Properties

### API Tubing Grades and Common Sizes

| OD (in) | Weight (lb/ft) | ID (in) | Wall (in) | Grade | Yield (psi) |
|---------|---------------|---------|----------|-------|------------|
| 1.900 | 2.90 | 1.610 | 0.145 | J-55 | 55,000 |
| 2⅜ | 4.70 | 1.995 | 0.190 | J-55 | 55,000 |
| 2⅜ | 4.70 | 1.995 | 0.190 | N-80 | 80,000 |
| 2⅞ | 6.50 | 2.441 | 0.217 | J-55 | 55,000 |
| 2⅞ | 6.50 | 2.441 | 0.217 | N-80 | 80,000 |
| 3½ | 9.30 | 2.992 | 0.254 | J-55 | 55,000 |
| 3½ | 9.30 | 2.992 | 0.254 | N-80 | 80,000 |
| 4 | 11.00 | 3.476 | 0.262 | N-80 | 80,000 |

```python
def tubing_cross_section_areas(od_in, id_in):
    """
    Returns pipe body cross-sectional area (steel) and internal area (in²).
    """
    import math
    A_i = math.pi / 4.0 * id_in**2   # internal (fluid) area
    A_o = math.pi / 4.0 * od_in**2   # outer area
    A_s = A_o - A_i                   # steel area
    return {"A_steel_in2": A_s, "A_inner_in2": A_i, "A_outer_in2": A_o}
```

### Material Constants (Steel)

| Property | Value | Units |
|----------|-------|-------|
| Young's modulus (E) | 30 × 10⁶ | psi |
| Thermal expansion (α) | 6.9 × 10⁻⁶ | 1/°F |
| Poisson's ratio (ν) | 0.30 | — |
| Density (steel) | 489.5 | lb/ft³ |

---

## Module 2 — Four Force Effects (Lubinski et al., 1962)

The total force change on a free-moving tubing string equals the sum of four
independent effects. Each produces an axial force change ΔF (positive = tension,
negative = compression).

### Effect 1: Temperature

```python
def delta_F_temperature(delta_T_avg_f, od_in, id_in, E=30e6, alpha=6.9e-6):
    """
    ΔF_T = -E * A_steel * alpha * ΔT
    Positive ΔT (heating during production): compressive force (negative)
    delta_T_avg_f: average temperature change along string (°F)
    Returns: ΔF_T in lbf (negative = compression added)
    """
    import math
    A_s = math.pi / 4.0 * (od_in**2 - id_in**2)
    return -E * A_s * alpha * delta_T_avg_f
```

### Effect 2: Ballooning

```python
def delta_F_ballooning(delta_Pi_psi, delta_Po_psi, od_in, id_in, nu=0.30):
    """
    ΔF_B = -2ν * (ΔPi * Ai - ΔPo * Ao)
    Positive ΔPi (pressure increase inside): compressive (shortens tubing, piston)
    delta_Pi_psi: change in average internal pressure (psi)
    delta_Po_psi: change in average annulus (external) pressure (psi)
    Returns: ΔF_B in lbf
    """
    import math
    Ai = math.pi / 4.0 * id_in**2
    Ao = math.pi / 4.0 * od_in**2
    return -2.0 * nu * (delta_Pi_psi * Ai - delta_Po_psi * Ao)
```

### Effect 3: Piston Effect

```python
def delta_F_piston(delta_Pi_psi, delta_Po_psi, od_in, id_in):
    """
    ΔF_P = ΔPo * Ao - ΔPi * Ai   (force at packer / area change)
    Occurs at any cross-section change: packer bore, tubing end, plug
    delta_Pi_psi: change in tubing pressure at packer
    delta_Po_psi: change in annulus pressure at packer
    Returns: ΔF_P in lbf (positive = tension)
    """
    import math
    Ai = math.pi / 4.0 * id_in**2
    Ao = math.pi / 4.0 * od_in**2
    return delta_Po_psi * Ao - delta_Pi_psi * Ai
```

### Effect 4: Total Force Change and Buckling Check

```python
def total_force_change(dF_T, dF_B, dF_P):
    """Returns total ΔF = ΔF_T + ΔF_B + ΔF_P (lbf)."""
    return dF_T + dF_B + dF_P

def buckling_check(F_initial_lbf, dF_total_lbf, W_buoyed_lb_ft, depth_ft):
    """
    Neutral point depth = (F_effective) / W_buoyed
    Below neutral point: compression -> buckling risk
    F_initial: initial tubing weight in fluid at packer (lbf, typically tension)
    """
    F_final = F_initial_lbf + dF_total_lbf
    neutral_point_ft = F_final / W_buoyed_lb_ft if W_buoyed_lb_ft > 0 else 0
    buckled_length = depth_ft - neutral_point_ft
    return {
        "F_final_lbf": F_final,
        "neutral_point_ft": neutral_point_ft,
        "buckled_length_ft": max(0.0, buckled_length),
        "buckling": buckled_length > 0
    }
```

---

## Module 3 — Buckling Analysis (Lubinski)

### Critical Buckling Loads

```python
def sinusoidal_buckling_force(w_e_lb_ft, r_c_in, EI_lbf_in2):
    """
    Sinusoidal buckling onset:
    F_cr_sin = 2 * sqrt(E*I * w_e / r_c)
    w_e_lb_ft: buoyed weight per unit length (lb/ft)
    r_c_in:    radial clearance between tubing OD and casing ID (inches)
    EI_lbf_in2: flexural rigidity = E * I
    Returns: F_cr_sin in lbf (compressive force to initiate sinusoidal buckling)
    """
    w_e_in = w_e_lb_ft / 12.0   # convert to lb/in
    r_c_ft = r_c_in / 12.0
    import math
    return 2.0 * math.sqrt(EI_lbf_in2 * w_e_in / r_c_in)

def helical_buckling_force(w_e_lb_ft, r_c_in, EI_lbf_in2):
    """Helical onset ≈ 2.83 * F_cr_sin (Dawson-Paslay, 1984)."""
    return 2.83 * sinusoidal_buckling_force(w_e_lb_ft, r_c_in, EI_lbf_in2)

def moment_of_inertia(od_in, id_in):
    """I = pi/64 * (OD^4 - ID^4) (in^4)"""
    import math
    return math.pi / 64.0 * (od_in**4 - id_in**4)
```

### Helical Pitch and Lateral Force

```python
def helical_pitch(F_comp_lbf, EI_lbf_in2, r_c_in):
    """
    Pitch of helix (in): p = 2*pi * sqrt(2*E*I / (F * r_c))
    Shorter pitch = tighter helix = more casing wear
    """
    import math
    return 2.0 * math.pi * math.sqrt(2.0 * EI_lbf_in2 / (F_comp_lbf * r_c_in))

def lateral_contact_force(w_e_lb_ft, r_c_in, p_in):
    """
    Lateral contact force per unit length (lb/ft):
    w_n = (4*pi^2 * w_e * r_c) / p^2
    """
    import math
    return (4 * math.pi**2 * w_e_lb_ft * r_c_in) / (p_in**2)
```

---

## Module 4 — Seal Assembly Stroke

```python
def seal_assembly_stroke(total_movement_in, safety_factor=1.5):
    """
    Required seal assembly stroke = total tubing movement * SF
    total_movement_in: calculated free-end movement (inches)
    Return: minimum seal assembly length (in)
    """
    return abs(total_movement_in) * safety_factor

def tubing_movement_temperature(L_ft, delta_T_avg_f, alpha=6.9e-6):
    """
    Free thermal movement (in): delta_L = alpha * L * delta_T * 12
    Positive ΔT (heating): tubing elongates (moves up at surface, pushes down at packer)
    """
    return alpha * L_ft * delta_T_avg_f * 12.0
```

---

## Module 5 — Velocity String Sizing

```python
def velocity_string_recommendation(q_gas_mscfd, p_wellhead_psi, T_wellhead_f,
                                   sigma=60.0, rho_l=62.4):
    """
    For a liquid-loading gas well, find the largest tubing ID that keeps
    gas velocity above Turner critical velocity.
    Returns: max ID (inches) for unloading.
    """
    import math
    T_R = T_wellhead_f + 459.67
    rho_g = (28.97 * 0.65 * p_wellhead_psi) / (10.73 * T_R * 0.9)
    v_crit = 1.593 * sigma**0.25 * (rho_l - rho_g)**0.25 / rho_g**0.5
    # q_gas (scf/day) = v_crit (ft/s) * A (ft2) * 86400 * (P/14.7) * (520/T_R)
    # Solve for A_max
    scfd = q_gas_mscfd * 1000.0
    A_max_ft2 = scfd / (v_crit * 86400.0 * (p_wellhead_psi / 14.7) * (520.0 / T_R))
    id_max_in = math.sqrt(4.0 * A_max_ft2 / math.pi) * 12.0
    return {"v_crit_ft_s": v_crit, "A_max_ft2": A_max_ft2, "ID_max_in": id_max_in}
```

---

## Module 6 — Packer Selection and DHSV

### Packer Type Selection

| Situation | Packer Type | Notes |
|-----------|------------|-------|
| Permanent (stimulation) | Permanent set, milled to retrieve | Best isolation; costly retrieval |
| Workover anticipated | Retrievable (slip, hydraulic) | Release with string manipulation |
| High-pressure differential | Permanent or production packer | Higher pressure rating |
| Multiple zones | Retrievable straddle or permanent | Zone-specific stimulation |
| ESP completion | Bagpipe / tandem seal | Accommodates ESP motor below |

### DHSV Setting Depth

```python
def dhsv_minimum_depth_ft(wellhead_shut_in_psi, fluid_grad_psi_ft=0.433):
    """
    DHSV must be set deep enough that casing burst is protected if tubing fails.
    Minimum depth: DHSV setting depth > P_wellhead / fluid_gradient
    Regulation: typically 100–200 ft below surface casing shoe or as specified.
    Returns: minimum TVD for DHSV (ft)
    """
    return wellhead_shut_in_psi / fluid_grad_psi_ft
```

---

## Output Format

```
## Tubing String Design — [Well Name / API]
**String:** X-in OD, Grade N-80 / P-110 | **Set depth:** X,XXX ft
**Packer:** [Free / Anchored / Semi-anchored]

### Force Analysis Summary
| Load Case | ΔF_T (klbf) | ΔF_B (klbf) | ΔF_P (klbf) | ΔF_Total (klbf) |
|-----------|------------|------------|------------|----------------|
| Installation → Stimulation | | | | |
| Installation → Production | | | | |
| Production → Workover | | | | |

### Buckling Assessment
| Load Case | F_final (klbf) | Neutral Point (ft) | Buckled Length (ft) | Risk |
|-----------|---------------|-------------------|---------------------|------|
| | | | | |

### Movement and Seal Assembly
| Load Case | Free Movement (in) | Required Stroke (in) |
|-----------|-------------------|---------------------|
| | | |

### Velocity String Check (if applicable)
Required ID max: X.XX in | Selected: X-in OD, X.XXX ID
```

---

## Error Handling

| Condition | Cause | Action |
|-----------|-------|--------|
| Neutral point above packer | Large compressive load | Verify packer type; increase set weight |
| Buckled length > tubing length | Extreme load case | Use anchored packer; check stimulation pressure |
| Movement exceeds seal stroke | Underdimensioned seal assembly | Specify longer seal; consider anchored completion |
| Negative torque on helix | Tension everywhere | No buckling; helix equations don't apply |

---

## Caveats

- Lubinski four-effect analysis assumes straight wellbore and uniform
  temperature gradient. For deviated wells, contact forces and friction modify
  the analysis significantly — use dedicated software.
- Free-tubing analysis gives maximum movement; anchored packer absorbs
  movement and transfers force to the wellhead. Semi-anchored falls between.
- The Lubinski (1962) sinusoidal and helical buckling onset loads assume
  uniform tubing properties and no friction. Deviated wells have lower onset
  buckling loads due to gravity components.
- Thermal effects dominate in steam injection and high-GOR wells. Ensure
  temperature profile is accurately modeled for these cases.
- API RP 5C3 burst and collapse ratings apply; always check that tubing
  survives stimulation (frac) and production pressure differentials.
