---
name: well-test-analysis
description: >
  Pressure transient analysis for oil and gas well testing including drawdown
  and buildup test interpretation. Implements the exponential integral Ei
  solution for radial flow pressure drawdown, Horner plot method for
  permeability and skin calculation from buildup tests, Bourdet pressure
  derivative for flow regime identification, and wellbore storage coefficient
  estimation from unit-slope log-log behavior. Use when the user asks about
  well testing, pressure buildup test, Horner plot, Horner straight line,
  skin factor, wellbore storage, pressure derivative, Bourdet derivative,
  kh product, MDH plot, drawdown test interpretation, permeability from well
  test, or flow regime identification. Resources: Lee Rollins Spivey Pressure
  Transient Testing SPE Vol 9; Earlougher Advances in Well Test Analysis
  SPE Monograph 5; Bourdet Well Test Analysis; Kappa Engineering tech notes.
  Primary courses: PNGE 321 Reservoir Engineering, PNGE 361 Production.
---

# Pressure Transient Analysis

Computational skill for well test design and interpretation covering drawdown,
buildup (Horner), and log-log derivative analysis. Calibrated for Appalachian
gas and oil wells.

**Field units throughout.** Rates in STB/day (oil) or Mscf/day (gas),
pressure in psia, permeability in md, length in ft, viscosity in cp.

---

## Module 1 — Radial Flow: Ei Solution (Drawdown)

```python
import math

def ei_function(x):
    """
    Exponential integral approximation: Ei(-x) for x > 0.
    Valid for small x (|x| < 10).
    Uses Abramowitz and Stegun series approximation.
    Ei(-x) ≈ ln(x) + gamma + x + x^2/4 + ...  (for small x)
    In well testing, Ei approximated as ln(x) + 0.80907 for x < 0.01 (log approx).
    """
    if x <= 0:
        raise ValueError("x must be positive for Ei(-x)")
    if x > 10.0:
        return 0.0  # negligible for large argument
    # Log approximation valid for x < 0.01 (well testing "infinite acting" condition)
    if x < 0.01:
        return -(math.log(x) + 0.57721566)  # = -Ei(-x)  approx ln(1/x) - gamma
    # Numerical integration approximation (Horner's method for Ei)
    # Using the series: Ei(x) = gamma + ln(|x|) + sum(x^n / (n * n!))
    result = math.log(x) + 0.57721566
    term = x
    factorial = 1.0
    for n in range(1, 25):
        factorial *= n
        result += term / (n * factorial)
        term *= x
        if abs(term / (n * factorial)) < 1e-10:
            break
    return result

def drawdown_pressure_psi(p_i, q_bpd, B, mu_cp, k_md, h_ft,
                           phi, ct_psi, r_ft, t_hr):
    """
    Ei solution for constant rate drawdown (infinite-acting radial flow):
      p_wf = p_i - 141.2*q*B*mu/kh * [-Ei(-r^2*phi*mu*ct/(0.000264*k*t))]

    p_i:    initial reservoir pressure (psia)
    q_bpd:  production rate (STB/day for oil; Mscf/day for gas, use q_g*Bg)
    B:      formation volume factor (RB/STB or Rcf/scf)
    mu_cp:  viscosity (cp)
    k_md:   effective permeability (md)
    h_ft:   net pay thickness (ft)
    phi:    porosity (fraction)
    ct_psi: total compressibility (1/psi)
    r_ft:   radius at which pressure is calculated (ft); r_w for wellbore
    t_hr:   elapsed time since start of production (hours)
    Returns: flowing pressure at radius r (psia)
    """
    x = (948.0 * phi * mu_cp * ct_psi * r_ft**2) / (k_md * t_hr)
    if x < 1e-12:
        return p_i
    ei_val = ei_function(x)  # positive value = -Ei(-x)
    delta_p = 141.2 * q_bpd * B * mu_cp / (k_md * h_ft) * ei_val
    return p_i - delta_p

def log_approximation_valid(phi, mu_cp, ct_psi, r_ft, k_md, t_hr):
    """
    Check if log approximation (x < 0.01) is valid.
    Condition: t > 94800 * phi * mu * ct * r^2 / k
    Returns: True if log approximation applies (standard radial flow analysis valid)
    """
    x = (948.0 * phi * mu_cp * ct_psi * r_ft**2) / (k_md * t_hr)
    return x < 0.01
```

---

## Module 2 — Horner Plot: Buildup Test Interpretation

```python
def horner_time_ratio(t_p_hr, delta_t_hr):
    """
    Horner time ratio: HTR = (t_p + delta_t) / delta_t
    t_p_hr:      producing time before shut-in (hours)
    delta_t_hr:  shut-in time (hours)
    Returns: Horner time ratio (dimensionless, plot on x-axis, log scale)
    """
    return (t_p_hr + delta_t_hr) / delta_t_hr

def horner_p_star(m_slope, p_1hr, HTR_at_1hr=None):
    """
    Extrapolate Horner straight line to HTR=1 to get P* (false pressure).
    The semi-log straight line: P_ws = P* - m * log(HTR)
    At HTR=1 (infinite shut-in): P_ws = P*
    m_slope: slope of P_ws vs. log(HTR) plot (psi/cycle); NEGATIVE for buildup
    p_at_x:  P_ws at a known log(HTR) value on the straight line
    """
    # P* is the y-intercept at log(HTR)=0 -> HTR=1
    # Usually read directly from the semi-log plot extrapolation
    # If we know P_1hr (P_ws at delta_t = 1 hr on MTR line):
    # P* = P_1hr - m * log(t_p + 1) + m*log(t_p) for large t_p:
    # P* ≈ P_1hr (when t_p >> 1 hr)
    # Return a note that P* requires graphical extrapolation
    return {"note": "P* is the y-intercept of Horner semi-log straight line at HTR=1",
            "P_1hr_approx": p_1hr}

def permeability_from_horner(q_bpd, B, mu_cp, m_psi_per_cycle, h_ft):
    """
    Permeability from Horner MTR slope.
    k = 162.6 * q * B * mu / (m * h)
    m_psi_per_cycle: magnitude of slope (positive value; slope is negative for buildup)
    Returns: effective permeability (md)
    """
    return 162.6 * q_bpd * B * mu_cp / (m_psi_per_cycle * h_ft)

def skin_factor_horner(P_1hr_psia, P_wf_psia, m_psi_per_cycle,
                        k_md, phi, mu_cp, ct_psi, r_w_ft):
    """
    Skin factor from Horner plot.
    S = 1.1513 * [(P_1hr - P_wf) / m - log(k / (phi*mu*ct*r_w^2)) + 3.2275]

    P_1hr_psia: pressure on the MTR straight line at delta_t = 1 hr
    P_wf_psia:  flowing wellbore pressure just before shut-in
    m:          Horner slope (magnitude, psi/log cycle)
    Returns: skin factor (dimensionless; positive = damage, negative = stimulation)
    """
    log_term = math.log10(k_md / (phi * mu_cp * ct_psi * r_w_ft**2))
    S = 1.1513 * ((P_1hr_psia - P_wf_psia) / m_psi_per_cycle - log_term + 3.2275)
    return S

def flow_efficiency(S, P_avg_psia, P_wf_psia, r_e_ft, r_w_ft):
    """
    Flow efficiency: FE = (ideal drawdown) / (actual drawdown)
    FE = (P_avg - P_wf - ΔP_skin) / (P_avg - P_wf)
    where ΔP_skin = 0.87 * m * S
    FE > 1: stimulated well; FE < 1: damaged well
    """
    # Need m to compute ΔP_skin = 0.87 * m * S, but we can express as:
    # Ideal: Darcy radial flow with S=0
    # FE expressed via ln(re/rw):
    ln_ratio = math.log(r_e_ft / r_w_ft) - 0.75
    FE = (ln_ratio) / (ln_ratio + S)
    actual_drawdown = P_avg_psia - P_wf_psia
    delta_p_skin = actual_drawdown * (1.0 - FE)
    return {"FE": round(FE, 3),
            "delta_p_skin_psi": round(delta_p_skin, 1),
            "interpretation": "stimulated" if FE > 1.0 else ("damaged" if FE < 1.0 else "undamaged")}
```

---

## Module 3 — Bourdet Pressure Derivative

```python
def bourdet_derivative(delta_t_list, delta_p_list):
    """
    Bourdet pressure derivative: delta_p' = delta_t * d(delta_p)/d(delta_t)
    In log-log coordinates: derivative = d(delta_p)/d(ln delta_t)

    Uses symmetric three-point numerical differentiation where possible.
    Input lists should be in chronological order (increasing delta_t).
    Returns: list of (delta_t, delta_p, derivative) tuples

    Flow regime signatures (log-log plot):
      Wellbore storage: unit slope (delta_p' = 0.5 * delta_p on unit slope line)
      Radial flow: flat derivative (delta_p' = m/2.303; m = 162.6*qBmu/kh)
      Linear flow: half-slope (delta_p' proportional to sqrt(delta_t))
      Bilinear flow: quarter-slope
      Closed boundary: derivative rises above radial value
    """
    n = len(delta_t_list)
    result = []
    for i in range(n):
        t = delta_t_list[i]
        p = delta_p_list[i]
        # Forward difference (first point)
        if i == 0:
            if n > 1:
                ln_dt = math.log(delta_t_list[1] / delta_t_list[0])
                dp = delta_p_list[1] - delta_p_list[0]
                deriv = dp / ln_dt if ln_dt > 1e-12 else 0.0
            else:
                deriv = 0.0
        # Backward difference (last point)
        elif i == n - 1:
            ln_dt = math.log(delta_t_list[i] / delta_t_list[i-1])
            dp = delta_p_list[i] - delta_p_list[i-1]
            deriv = dp / ln_dt if ln_dt > 1e-12 else 0.0
        # Symmetric (interior points, preferred)
        else:
            ln1 = math.log(delta_t_list[i] / delta_t_list[i-1])
            ln2 = math.log(delta_t_list[i+1] / delta_t_list[i])
            dp1 = (delta_p_list[i] - delta_p_list[i-1]) / ln1 if ln1 > 1e-12 else 0.0
            dp2 = (delta_p_list[i+1] - delta_p_list[i]) / ln2 if ln2 > 1e-12 else 0.0
            deriv = (dp1 * ln2 + dp2 * ln1) / (ln1 + ln2)
        result.append((t, p, round(deriv, 4)))
    return result

def identify_radial_flow_window(derivatives):
    """
    Identify the MTR (middle time region) where the Bourdet derivative is flat.
    Looks for consecutive points where derivative stabilizes within 10% of median.
    Returns: (t_start, t_end, mean_derivative) or None if no flat region found
    """
    if len(derivatives) < 3:
        return None
    deriv_vals = [d[2] for d in derivatives]
    med = sorted(deriv_vals)[len(deriv_vals)//2]
    flat = [(d[0], d[2]) for d in derivatives if abs(d[2] - med)/med < 0.10]
    if len(flat) < 2:
        return None
    return {"t_start_hr": flat[0][0], "t_end_hr": flat[-1][0],
            "mean_derivative": round(sum(f[1] for f in flat) / len(flat), 4)}
```

---

## Module 4 — Wellbore Storage Coefficient

```python
def wellbore_storage_from_unit_slope(q_bpd, B, delta_t_hr, delta_p_psi):
    """
    WBS coefficient from unit-slope log-log behavior (early time).
    On unit slope: delta_p = (q*B / 24*C) * delta_t  =>
    C = q*B*delta_t / (24*delta_p)
    q_bpd: production rate (STB/day)
    B:     formation volume factor (RB/STB)
    Returns: C (bbl/psi)
    """
    return q_bpd * B * delta_t_hr / (24.0 * delta_p_psi)

def wellbore_storage_from_volume(V_wellbore_bbl, c_wellbore_psi):
    """
    WBS from wellbore compressibility:
    C = V_wb * c_wb
    V_wellbore_bbl: wellbore fluid volume from perforations to surface (bbl)
    c_wellbore_psi: compressibility of wellbore fluid (1/psi)
       - Single-phase liquid: ~3e-6 to 15e-6 /psi
       - Gas/liquid mix: much higher
    Returns: C (bbl/psi)
    """
    return V_wellbore_bbl * c_wellbore_psi

def wellbore_storage_end_time(C_bbl_psi, phi, ct_psi, h_ft, r_w_ft, S=0.0):
    """
    Approximate end of wellbore storage distortion.
    t_wbs_end ≈ 200,000 * C * exp(0.14*S) / (phi * ct * h * r_w^2)  [hours]
    After this time, the MTR (radial flow) should be identifiable.
    """
    numerator = 200000.0 * C_bbl_psi * math.exp(0.14 * S)
    denominator = phi * ct_psi * h_ft * r_w_ft**2
    return numerator / denominator
```

---

## Learning Resources

### Textbooks

| Author(s) | Title | ISBN | Notes |
|-----------|-------|------|-------|
| Lee, Rollins & Spivey | *Pressure Transient Testing*, SPE Vol. 9 (2003) | 978-1-55563-099-6 | Best undergrad reference |
| Horne, R.N. | *Modern Well Test Analysis*, 2nd ed. (1995) | 978-0-9626992-1-7 | Stanford course text; beginner-friendly |
| Bourdet, D. | *Well Test Analysis* (2002) | 978-0-444-50968-2 | Derivative analysis bible |
| Earlougher, R.C. | *Advances in Well Test Analysis*, SPE Monograph 5 (1977) | 978-0-89520-204-4 | Foundational monograph |

### Free Online Resources

| Resource | URL | Content |
|----------|-----|---------|
| SPE PetroWiki — Well Testing | petrowiki.spe.org/Well_testing | Equations, flow regimes, free |
| Kappa Engineering tech notes | kappaeng.com/papers | Rigorous PTA theory, free PDFs |
| Stanford ERE 272 materials | pangea.stanford.edu/ERE | Roland Horne course materials |
| WVU research repository | researchrepository.wvu.edu | Marcellus well test M.S. theses |

### WVU Courses

- **PNGE 321** — Darcy radial flow, skin concept, material balance
- **PNGE 361** — Production engineering context for well test design

---

## Output Format

```
## Well Test Analysis — [Well Name / API]

### Test Design
| Parameter | Value | Notes |
|-----------|-------|-------|
| Test type | Buildup / Drawdown / DST | |
| Producing time (t_p) | hrs | Before shut-in |
| Shut-in duration | hrs | |
| Rate before shut-in | STB/d or Mscf/d | |

### Horner Analysis (MTR)
| Parameter | Value | Units |
|-----------|-------|-------|
| Slope (m) | psi/cycle | |
| P* (extrapolated) | psia | |
| k | md | |
| kh | md-ft | |
| Skin (S) | dimensionless | |
| Flow efficiency (FE) | dimensionless | |
| Apparent wellbore radius (r_wa) | ft | r_wa = r_w * exp(-S) |

### Log-Log Derivative Diagnosis
[Flow regime identification from derivative plot]
- Wellbore storage period: [t range]
- Radial flow (MTR): [t range], derivative ≈ [value] psi
- Boundary effects: [none / closed boundary / linear / etc.]

**Certainty:** HIGH if MTR clearly identified | MEDIUM if WBS masks MTR
**Bias:** Single-layer radial flow assumed; multilayer/dual-porosity systems require type curve matching
```

---

## Error Handling

| Condition | Cause | Action |
|-----------|-------|--------|
| No flat derivative region | WBS too large or test too short | Extend shut-in; check test duration vs. WBS end time |
| Negative skin | Stimulated well (fracture) | Use fracture type curves (Cinco-Ley, uniform flux) |
| k unreasonably high (>100 md) | Wrong h or rate unit | Check input units; verify net pay |
| P* below P_res | Boundary or depletion effects | Not infinite-acting; use bounded reservoir analysis |

---

## Caveats

- **Single-layer infinite-acting radial flow assumed.** Multilayer, dual-porosity,
  or naturally fractured reservoirs require specialized type curves.
- **Gas wells require pseudo-pressure.** Ei and Horner equations above apply
  strictly to liquid; for gas, replace p with real-gas pseudo-pressure m(p) for
  rigorous analysis at high pressure variation.
- **Skin includes all near-wellbore damage.** Perforation skin, partial
  penetration, phase-relative permeability reduction, and mechanical damage
  all combine into the single skin value from Horner analysis.
- **MDH plot** (Miller-Dyes-Hutchinson) is used when t_p is very long;
  uses log(delta_t) instead of Horner ratio.
- Production data before shut-in must be at constant rate for Horner analysis.
  Variable rate history requires superposition or specialized methods.
