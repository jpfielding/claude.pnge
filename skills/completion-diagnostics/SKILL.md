---
name: completion-diagnostics
description: >
  Interpret hydraulic fracturing diagnostics and stage execution data including
  DFIT and minifrac closure analysis, step-rate test interpretation, ISIP
  estimation, net pressure decomposition, cluster efficiency screening, and
  treatment-pressure troubleshooting. Use when the user asks about closure
  pressure, fracture gradient, G-function or square-root-time plots, step-rate
  breakdown pressure, screenout diagnosis, treating pressure analysis, cluster
  imbalance, frac calibration tests, or stage-by-stage completion performance.
  Trigger phrases include DFIT, minifrac, ISIP, closure pressure, step-rate,
  net pressure, treatment pressure matching, cluster efficiency, screenout,
  pressure signature, tortuosity, or diagnostic fracture injection test.
---

# Completion Diagnostics

Diagnostic skill for interpreting frac calibration tests and stage execution
data. Best results come from raw pressure, rate, slurry concentration, and
proppant time series rather than only stage summaries.

**Important:** Completion diagnostics fail most often from bad normalization,
not bad physics. Before interpreting closure or cluster efficiency, verify time
alignment, gauge units, hydrostatic assumptions, pipe friction assumptions, and
perforation depth.

---

## Data To Request First

- Measured treating pressure and rate versus time
- Slurry concentration and proppant schedule versus time
- Shut-in timestamp and first few minutes of pressure falloff
- TVD to perforations and fluid density during treatment
- Surface iron / pipe friction estimate and perforation scheme
- Stage length, cluster count, shots per foot, and entry-hole diameter
- Offset DFIT, minifrac, microseismic, tracer, DAS, or fiber diagnostics if available

If only summary data are available, provide ranges and uncertainty bands rather
than a single precise answer.

---

## Workflow

1. Normalize pressure to perforation depth.
2. Separate hydrostatic, pipe friction, perforation friction, and fracture components.
3. Estimate ISIP from the first shut-in points and bracket closure pressure.
4. Compare net pressure and perforation friction across stages or clusters.
5. Diagnose anomalies from pressure shape, rate response, and slurry behavior.

---

## Module 1 - Pressure Normalization

```python
def bhp_at_perfs(surface_pressure_psi, tvd_ft, fluid_ppg,
                 pipe_friction_psi=0.0, perf_friction_psi=0.0):
    """
    Bottomhole treating pressure at perforations.
    BHTP = P_surface + hydrostatic + pipe friction + perf friction
    hydrostatic = 0.052 * MW(ppg) * TVD(ft)
    """
    hydrostatic = 0.052 * fluid_ppg * tvd_ft
    return surface_pressure_psi + hydrostatic + pipe_friction_psi + perf_friction_psi

def net_treating_pressure(bhtp_psi, closure_pressure_psi):
    """
    Net pressure above closure / minimum stress.
    For screening, use closure pressure from DFIT or minifrac.
    """
    return bhtp_psi - closure_pressure_psi

def fracture_gradient(pressure_psi, tvd_ft):
    """Pressure gradient in psi/ft."""
    if tvd_ft <= 0:
        return None
    return pressure_psi / tvd_ft
```

**Interpretation ranges**

| Metric | Typical meaning |
|--------|-----------------|
| Closure gradient 0.65 to 0.85 psi/ft | Common unconventional stress range |
| Net pressure 200 to 800 psi | Reasonable range for many slickwater stages |
| Rapid net pressure escalation at constant rate | Near-wellbore restriction, sand loading, or height growth change |

---

## Module 2 - ISIP and Closure Screening

```python
def isip_from_sqrt_time(time_sec, pressure_psi, n_points=8):
    """
    Estimate ISIP by fitting pressure versus sqrt(time) over the first
    post-shut-in points and extrapolating to time = 0.
    """
    import math

    n = min(len(time_sec), len(pressure_psi), n_points)
    if n < 2:
        return None

    x = [math.sqrt(max(t, 0.0)) for t in time_sec[:n]]
    y = pressure_psi[:n]

    x_bar = sum(x) / n
    y_bar = sum(y) / n
    sxx = sum((xi - x_bar) ** 2 for xi in x)
    if sxx == 0:
        return None
    sxy = sum((xi - x_bar) * (yi - y_bar) for xi, yi in zip(x, y))
    slope = sxy / sxx
    intercept = y_bar - slope * x_bar
    return intercept

def closure_pressure_range(isip_psi, pressure_at_slope_change_psi,
                           uncertainty_psi=100.0):
    """
    Return a closure bracket rather than a single number when only simple
    diagnostics are available.
    """
    low = min(isip_psi, pressure_at_slope_change_psi) - uncertainty_psi
    high = max(isip_psi, pressure_at_slope_change_psi) + uncertainty_psi
    return {"low_psi": low, "high_psi": high}
```

**Closure picking hierarchy**

1. Use raw DFIT falloff with G-function and square-root-time plots.
2. Cross-check derivative behavior against after-closure linear flow.
3. If only treatment shut-in data exist, give a bounded closure range.
4. Do not present single-psi precision unless the raw falloff quality supports it.

**Diagnostic cues**

| Plot cue | Likely interpretation |
|---------|-----------------------|
| Early steep drop immediately after shut-in | Pipe / near-wellbore friction bleeding off |
| Clear slope change on sqrt-time | Candidate closure point |
| G-function derivative minimum then rise | Candidate closure region |
| No clean break | Multiple closures, complexity, poor shut-in data, or height growth |

---

## Module 3 - Step-Rate And Breakdown

```python
def step_rate_slopes(rate_bpm, pressure_psi):
    """
    Piecewise slope dP/dQ between adjacent rate steps.
    In a clean step-rate test, fracture initiation often appears as a
    sustained reduction in slope (injectivity increase).
    """
    slopes = []
    for i in range(1, min(len(rate_bpm), len(pressure_psi))):
        dq = rate_bpm[i] - rate_bpm[i - 1]
        if dq == 0:
            slopes.append(None)
        else:
            slopes.append((pressure_psi[i] - pressure_psi[i - 1]) / dq)
    return slopes

def fracture_initiation_step(rate_bpm, pressure_psi, slope_drop_frac=0.25):
    """
    Identify the first rate step where slope drops materially relative to the
    previous step. This is a screening indicator, not a final picked pressure.
    """
    slopes = step_rate_slopes(rate_bpm, pressure_psi)
    for i in range(1, len(slopes)):
        if slopes[i - 1] and slopes[i] and slopes[i] < (1 - slope_drop_frac) * slopes[i - 1]:
            return {"step_index": i + 1, "pressure_psi": pressure_psi[i + 1]}
    return None
```

**Use cases**

- Breakdown pressure: first clear fracture initiation point
- Reopening pressure: later cycle pressure where fracture reopens
- Step-down test: separate surface friction, pipe friction, and perforation friction after treatment

---

## Module 4 - Cluster Efficiency And Perforation Friction

```python
def perforation_friction_psi(rate_bpm, fluid_ppg, shot_count,
                             entry_diameter_in, discharge_coeff=0.8):
    """
    Limited-entry perforation friction estimate.
    Common field-units screening form:
    dP = 0.2369 * q^2 * rho / (Cd^2 * N^2 * d^4)
    q in bbl/min, rho in ppg, N total effective open holes, d in inches.
    """
    if shot_count <= 0 or entry_diameter_in <= 0 or discharge_coeff <= 0:
        return None
    numerator = 0.2369 * rate_bpm**2 * fluid_ppg
    denominator = discharge_coeff**2 * shot_count**2 * entry_diameter_in**4
    return numerator / denominator

def cluster_efficiency_from_rate_split(cluster_rates_bpm):
    """
    Simple rate-balance metric.
    1.0 means perfectly even distribution.
    """
    if not cluster_rates_bpm:
        return None
    avg_q = sum(cluster_rates_bpm) / len(cluster_rates_bpm)
    if avg_q == 0:
        return None
    return min(cluster_rates_bpm) / avg_q
```

**Rule-of-thumb guidance**

| Indicator | Screening guidance |
|----------|--------------------|
| Perforation friction < 200 psi | Often too low for robust limited entry |
| Perforation friction 300 to 800 psi | Common design target range |
| Cluster efficiency < 0.6 | Large imbalance likely |
| Rising treating pressure with falling rate allocation quality | Near-wellbore restriction or dominant cluster growth |

For rigorous cluster allocation, combine this skill with
`pnge:perforation-design` and any available tracer or DAS data.

---

## Module 5 - Pressure Signature Diagnosis

| Pressure behavior | Likely cause | What to check next |
|------------------|-------------|--------------------|
| Sharp pressure rise at constant rate near tail-in | Screenout or near-screenout | Slurry concentration, sand ramp, blender behavior, heel cluster restriction |
| High pressure from start of stage | Tortuosity / near-wellbore complexity | Step-down, perf friction, gun phasing, limited-entry sizing |
| Pressure falls while rate also falls unexpectedly | Surface equipment issue | Pump schedule, iron restriction, data QA |
| Lower-than-offset pressure with poor response | Out-of-zone growth or stress shadow difference | Geology, stage spacing, offset diagnostics |
| Oscillatory pressure during proppant pumping | Sand slugs or unstable blender hydration | Slurry density, chemical loading, hydration time |

---

## Output Format

When using this skill, structure the answer as:

1. Pressure normalization assumptions
2. ISIP and closure range
3. Net pressure and fracture gradient interpretation
4. Cluster efficiency / perforation friction findings
5. Most likely operational diagnosis
6. What additional data would materially reduce uncertainty

---

## Integration Points

- Use `pnge:frac-design` for geometry and stress context.
- Use `pnge:perforation-design` for limited-entry and perf friction detail.
- Use `pnge:wellbore-stability` for stress and fracture containment context.
- Use `pnge:production-chemistry` when slurry chemistry or breaker cleanup is implicated.
