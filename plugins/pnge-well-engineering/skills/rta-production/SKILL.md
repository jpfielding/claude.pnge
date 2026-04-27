---
name: rta-production
description: >
  Rate transient analysis and production decline curve analysis for oil and gas
  wells. Implements Arps exponential, hyperbolic, and harmonic decline with EUR
  estimation, b-factor analysis, hyperbolic-to-exponential terminal switch,
  loss-ratio method, and Blasingame flowing material balance for OOIP/OGIP
  estimation. Supports monthly production forecasting with economic limit cutoff.
  Use when the user asks about decline curve analysis, Arps decline, EUR estimate,
  b-factor, hyperbolic decline, terminal decline rate, production forecast,
  reserves estimation, rate transient analysis, flowing material balance,
  loss-ratio, material balance time, or fitting production history for Marcellus,
  Utica, Bakken, or other wells. Resources: Lee and Wattenbarger Gas Reservoir
  Engineering SPE Vol 5; Blasingame and Lee flowing material balance; SPE
  PetroWiki Rate Transient Analysis. Primary courses: PNGE 321 Reservoir
  Engineering, PNGE 411 Petroleum Economics.
---

# Rate Transient Analysis and Production Decline

Computational skill for decline curve analysis (DCA) and rate transient
analysis (RTA) of oil and gas wells. Calibrated for Appalachian unconventional
wells (Marcellus, Utica) but applicable to any reservoir.

**Key distinction:** Arps DCA (empirical, boundary-dominated flow, EUR/reserves)
vs. RTA (analytical, combines transient + BDF, estimates k, S, OGIP from
flowing data). Both are implemented here.

---

## Module 1 — Arps Decline Curves

```python
import math

def arps_rate(q_i, d_i, b, t):
    """
    Arps hyperbolic decline rate.
      q(t) = q_i / (1 + b*d_i*t)^(1/b)    (0 < b < 2, hyperbolic)
      q(t) = q_i * exp(-d_i * t)            (b = 0, exponential)
      q(t) = q_i / (1 + d_i * t)            (b = 1, harmonic)

    q_i: initial rate (any unit; d_i and t must share same time base)
    d_i: initial nominal decline rate (fraction/time, e.g. 1/yr)
    b:   hyperbolic exponent (0=exp, 1=harmonic; shale typically 1.0-2.0 early)
    t:   time since start of decline (years if d_i in 1/yr)
    Returns: rate at time t
    """
    if b < 1e-6:
        return q_i * math.exp(-d_i * t)
    elif abs(b - 1.0) < 1e-6:
        return q_i / (1.0 + d_i * t)
    else:
        return q_i / (1.0 + b * d_i * t) ** (1.0 / b)

def arps_cumulative(q_i, d_i, b, t):
    """
    Arps cumulative production from t=0 to t.
      Exponential: Np = (q_i / d_i) * (1 - exp(-d_i*t))
      Harmonic:    Np = (q_i / d_i) * ln(1 + d_i*t)
      Hyperbolic:  Np = q_i^b / ((1-b)*d_i) * (q_i^(1-b) - q_t^(1-b))
    Returns: cumulative production (same unit as q_i * time)
    """
    if b < 1e-6:
        return (q_i / d_i) * (1.0 - math.exp(-d_i * t))
    elif abs(b - 1.0) < 1e-6:
        return (q_i / d_i) * math.log(1.0 + d_i * t)
    else:
        q_t = arps_rate(q_i, d_i, b, t)
        return q_i**b / ((1.0 - b) * d_i) * (q_i**(1.0 - b) - q_t**(1.0 - b))

def eur_with_terminal_switch(q_i, d_i, b, d_min, q_aban=0.0):
    """
    EUR for hyperbolic decline switching to exponential at d_min.
    Industry practice: shale wells start hyperbolic (b=1.2-1.8),
    switch to exponential at d_min = 0.05-0.10 / yr to prevent infinite EUR.

    d_min:  terminal exponential decline rate (1/yr)
    q_aban: abandonment rate (same unit as q_i); 0 means decline to d_min only
    Returns: total EUR (same unit as q_i * years)
    """
    if b < 1e-6:  # already exponential
        if q_aban > 0:
            t_aban = -math.log(q_aban / q_i) / d_i
            return arps_cumulative(q_i, d_i, 0, t_aban)
        return q_i / d_i

    # Time when instantaneous decline rate reaches d_min
    # d_inst(t) = d_i / (1 + b*d_i*t)  =>  set = d_min => t_switch
    t_switch = (d_i / d_min - 1.0) / (b * d_i)
    q_switch = arps_rate(q_i, d_i, b, t_switch)
    np_hyp = arps_cumulative(q_i, d_i, b, t_switch)

    # Exponential tail at d_min from q_switch
    if q_aban > 0 and q_aban < q_switch:
        np_exp = (q_switch / d_min) * (1.0 - q_aban / q_switch)
    else:
        np_exp = q_switch / d_min  # decline to zero (economic limit separately)
    return np_hyp + np_exp
```

**Appalachian DCA Reference:**

| Formation | Typical b | d_i (1/yr) | d_min (1/yr) | Notes |
|-----------|-----------|------------|--------------|-------|
| Marcellus (dry gas) | 1.2–1.8 | 1.5–3.0 | 0.05–0.10 | BDF transition ~2–4 yr |
| Utica/PP (wet gas) | 1.0–1.5 | 1.2–2.5 | 0.06–0.12 | Higher initial rates |
| Bakken (oil) | 1.0–1.3 | 0.8–1.5 | 0.05–0.08 | |

---

## Module 2 — Loss-Ratio and b-Factor from Production History

```python
def instantaneous_decline_rate(q1, q2, dt):
    """
    D = -(1/q) * (dq/dt) ≈ -(q2 - q1) / (q_avg * dt)
    Used to estimate current decline rate from consecutive rate measurements.
    q1, q2: rates at times t1, t2 (any consistent unit)
    dt:     time interval (years)
    Returns: instantaneous decline rate (1/yr)
    """
    q_avg = 0.5 * (q1 + q2)
    dq = q2 - q1
    return -dq / (q_avg * dt)

def estimate_b_factor(rates, times):
    """
    Estimate b-factor from rate history using loss-ratio method.
    b = d(1/D)/dt  (constant for Arps decline)
    rates: list of production rates (consistent units)
    times: list of corresponding times (years)
    Returns: estimated b-factor and list of instantaneous D values
    """
    D_list = []
    for i in range(len(rates) - 1):
        D = instantaneous_decline_rate(rates[i], rates[i+1],
                                        times[i+1] - times[i])
        D_list.append((times[i], D))

    # b from slope of 1/D vs. time
    if len(D_list) < 2:
        return None, D_list
    # Linear regression on 1/D vs t
    x_vals = [d[0] for d in D_list]
    y_vals = [1.0/d[1] for d in D_list if d[1] > 1e-9]
    n = len(y_vals)
    if n < 2:
        return None, D_list
    x_mean = sum(x_vals[:n]) / n
    y_mean = sum(y_vals) / n
    num = sum((x_vals[i] - x_mean) * (y_vals[i] - y_mean) for i in range(n))
    den = sum((x_vals[i] - x_mean)**2 for i in range(n))
    b = num / den if den > 1e-12 else 0.0
    return b, D_list
```

---

## Module 3 — Blasingame Flowing Material Balance (FMB)

```python
def material_balance_time(Np_cumulative, q_current):
    """
    Blasingame material balance pseudo-time: tc = Np / q
    Normalizes transient and boundary-dominated flow data onto one straight line
    when q/(Pi-Pwf) is plotted vs. tc.

    For gas: tc = Gp [Mscf] / q_g [Mscf/day]  (days)
    For oil: tc = Np [bbl] / q_o [bbl/day]     (days)
    Returns: material balance time (same units as Np/q)
    """
    if q_current <= 0:
        return None
    return Np_cumulative / q_current

def fmb_normalized_rate(q, delta_p):
    """
    Normalized rate for FMB plot: q / delta_p
    For gas (low P approximation): delta_p = P_avg - P_wf  (using P^2/muZ for real gas)
    For oil: delta_p = P_res - P_wf (BHP)
    Plot q/delta_p vs. tc:
      - Straight line intercept at q/delta_p = 0 gives tc = Gp or Np (OGIP/OOIP)
      - Slope gives (1/J) where J is productivity index
    Returns: normalized rate (unit/psi)
    """
    if delta_p <= 0:
        return None
    return q / delta_p

def fmb_ogip_from_intercept(q_over_dp_initial, slope_fmb):
    """
    From the FMB straight line: q/delta_p = intercept - slope * tc
    x-intercept (q/delta_p = 0) occurs at tc = intercept/slope = OGIP (or OOIP).
    Returns: OGIP estimate (same units as cumulative production)
    """
    if abs(slope_fmb) < 1e-12:
        return None
    return q_over_dp_initial / slope_fmb
```

---

## Module 4 — Production Forecast Schedule

```python
def production_forecast(q_i, d_i, b, t_max_months,
                         d_min=0.0, q_aban=0.0):
    """
    Monthly production forecast using Arps decline with optional terminal switch.
    q_i:         initial rate (Mscf/day or bbl/day)
    d_i:         initial nominal decline (1/yr)
    b:           hyperbolic exponent
    t_max_months: forecast horizon (months)
    d_min:       terminal exponential decline (1/yr); 0 = no switch
    q_aban:      economic abandonment rate; 0 = forecast all months
    Returns: list of (month, rate, cumulative) — rate and cum in same unit*yr
    """
    forecast = []
    dt_yr = 1.0 / 12.0
    np_cum = 0.0
    in_terminal = False
    t_switch_yr = None
    q_switch = None

    if d_min > 0 and b > 1e-6:
        t_switch_yr = (d_i / d_min - 1.0) / (b * d_i)
        q_switch = arps_rate(q_i, d_i, b, t_switch_yr)

    for month in range(1, t_max_months + 1):
        t_yr = month * dt_yr

        if not in_terminal and t_switch_yr and t_yr >= t_switch_yr:
            in_terminal = True

        if in_terminal and q_switch is not None:
            t_since = t_yr - t_switch_yr
            q = q_switch * math.exp(-d_min * t_since)
        else:
            q = arps_rate(q_i, d_i, b, t_yr)

        if q_aban > 0 and q <= q_aban:
            break

        np_cum += q * dt_yr
        forecast.append((month, round(q, 2), round(np_cum, 2)))

    return forecast
```

---

## Learning Resources

### Textbooks

| Author(s) | Title | Notes |
|-----------|-------|-------|
| Lee & Wattenbarger | *Gas Reservoir Engineering*, SPE Vol. 5 (1996) | ISBN 978-1-55563-059-0 — foundational RTA theory |
| Craft, Hawkins & Terry | *Applied Petroleum Reservoir Engineering*, 3rd ed. (2015) | ISBN 978-0-13-315558-7 — reservoir theory underpinning RTA |
| Ahmed & McKinney | *Advanced Reservoir Engineering* (2005) | ISBN 978-0-7506-7733-4 — includes DCA chapter |

### Key SPE References

| Paper | Title | Why It Matters |
|-------|-------|----------------|
| SPE 116731 (Ilk et al., 2008) | Exponential vs. Hyperbolic Decline in Tight Gas | b-factor debate for shale |
| SPE 107967 (Clarkson, 2007) | Dynamic Flowing Material Balance for CBM | FMB methodology |
| Blasingame & Lee (1993) | "Analysis of Variable Rate Well Test Pressure Data" | Original FMB derivation |

### Free Online Resources

| Resource | URL | Content |
|----------|-----|---------|
| SPE PetroWiki — RTA | petrowiki.spe.org/Rate_transient_analysis | Equations, references, free |
| Texas A&M Blasingame group | petroleum.tamu.edu/facultystaff/blasingame-thomas | Course notes PETE 663 |
| Fekete tech white papers | ihsenergy.com (archived) | "Practical Guide to DCA" PDF |
| SPE student membership | spe.org/en/membership/student | $25/yr unlocks all SPE papers |

### WVU Courses

- **PNGE 321** Reservoir Engineering I — material balance, Darcy flow, DCA intro
- **PNGE 411** Petroleum Economics — reserves classification, EUR-based economics

---

## Output Format

```
## Production Decline Analysis — [Well / Formation]

### Decline Parameters
| Parameter | Value | Units |
|-----------|-------|-------|
| Initial rate (q_i) | | Mscf/d or bbl/d |
| Initial decline (d_i) | | 1/yr |
| b-factor | | dimensionless |
| Terminal decline (d_min) | | 1/yr |
| Abandonment rate | | Mscf/d or bbl/d |

### EUR Estimate
| Metric | Value | Units |
|--------|-------|-------|
| Hyperbolic EUR (to d_min) | | Bcf or MBbl |
| EUR to abandonment | | Bcf or MBbl |
| Switch to exponential at | | years |

### 5-Year Forecast (Annual)
| Year | Rate (Mscf/d or bbl/d) | Annual Prod | Cumulative |
|------|----------------------|-------------|------------|
| 1 | | | |
...

**Appalachian Context:** [Compare to typical Marcellus or Utica well EUR if applicable]

**Certainty:** MEDIUM — empirical fit; b-factor uncertainty dominates EUR range
**Bias:** Hyperbolic extrapolation overestimates EUR if b > 1 applied to BDF without terminal switch
```

---

## Error Handling

| Condition | Cause | Action |
|-----------|-------|--------|
| b > 2 | Numerically unstable; infinite EUR | Cap at b=2; note in output |
| d_i very low (less than 0.1/yr) | May be in transient, not BDF | Note: RTA more appropriate than DCA |
| EUR exceeds 10x analogs | b too high, no terminal switch | Apply d_min = 0.05-0.10/yr terminal switch |
| Negative rates returned | Abandonment rate exceeds initial | Check q_aban vs. q_i |

---

## Caveats

- **Arps DCA assumes boundary-dominated flow.** Shale wells can remain in
  transient (linear or bilinear flow) for years. Applying Arps to transient
  data gives inflated EUR. RTA/FMB is more rigorous for early-life data.
- **b > 1 is theoretically invalid in BDF** for single-layer reservoirs.
  In practice, b > 1 in shale reflects superposition of multiple transient
  flow regimes, not a true BDF hyperbolic. Always apply terminal switch.
- **EUR ≠ Reserves.** Reserves require economic conditions and regulatory
  definitions (SEC 5-year drilling rule for proved undeveloped).
- **FMB requires average reservoir pressure estimation.** Without P/Z plots
  or material balance, FMB is approximate.
- Decline curve fitting is non-unique: many (q_i, d_i, b) combinations can fit
  the same data. Report a range of EUR scenarios (P10/P50/P90).
