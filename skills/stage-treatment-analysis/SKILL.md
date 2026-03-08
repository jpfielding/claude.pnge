---
name: stage-treatment-analysis
description: >
  Analyze local stage-by-stage hydraulic fracturing treatment data from CSV,
  TSV, Excel, PDF, or report exports including pressure, rate, slurry,
  proppant, and shut-in records. Use when the user provides a stage report,
  pumping data export, frac van spreadsheet, pressure-rate chart, or asks to
  diagnose a screenout, estimate ISIP, compare stages, normalize stage metrics,
  or extract useful diagnostics from treatment data files. Trigger phrases
  include stage treatment data, frac van export, pumping schedule, rate and
  pressure CSV, stage report, slurry concentration, screenout, treating
  pressure chart, treatment summary, or stage-by-stage frac analysis.
---

# Stage Treatment Analysis

Operational skill for working with real treatment data exports rather than only
summary tables. It complements `pnge:completion-diagnostics` by focusing on
data intake, normalization, stage segmentation, and derived metrics from local
files.

**Important:** Field exports often mix units, reuse column names, and drift in
timestamp alignment across rate, pressure, and proppant channels. Fix schema and
timebase issues before interpreting the physics.

---

## Inputs To Prefer

- Timestamped treating pressure and rate
- Slurry concentration and total proppant
- Fluid totals, stage boundaries, and shut-in timestamps
- Perforation depth, cluster count, and perf design
- Step-down or minifrac segments if present

Common file patterns:

- Frac van or vendor CSV/TSV exports
- Excel stage summaries plus raw time series
- PDF stage reports with tables and charts
- Image or screenshot captures of pressure-rate plots

---

## Workflow

1. Identify the file schema and normalize units.
2. Align timestamps and label each stage segment.
3. Compute stage totals and rate-weighted averages.
4. Extract operational diagnostics: ISIP, screenout signature, friction trends.
5. Compare stages on a like-for-like basis: normalized by rate, fluid, and cluster count.

---

## Module 1 - Unit And Schema Normalization

```python
def psi_from_kpa(p_kpa):
    return p_kpa * 0.145038

def bpm_from_m3min(q_m3_min):
    return q_m3_min * 6.28981

def lb_from_kg(m_kg):
    return m_kg * 2.20462

def guess_column_role(name):
    """
    Map messy field names to canonical roles.
    """
    n = name.strip().lower()
    if "press" in n:
        return "pressure"
    if "rate" in n or "bpm" in n or "flow" in n:
        return "rate"
    if "slurry" in n or "prop conc" in n or "ppa" in n:
        return "slurry_conc"
    if "prop" in n and ("total" in n or "cum" in n):
        return "cum_proppant"
    if "time" in n or "date" in n:
        return "timestamp"
    return "unknown"
```

Before analysis, document:

- pressure basis: surface, corrected surface, or bottomhole estimate
- rate basis: clean fluid or slurry rate
- proppant basis: lb/gal, ppa, or cumulative mass
- time zone and stage start/shut-in definitions

---

## Module 2 - Stage Totals And Weighted Metrics

```python
def trapezoid_integral(x, y):
    """
    Integrate y over x using the trapezoid rule.
    x is typically minutes; y may be bpm, lb/min, etc.
    """
    if len(x) != len(y) or len(x) < 2:
        return None
    total = 0.0
    for i in range(1, len(x)):
        dx = x[i] - x[i - 1]
        total += 0.5 * (y[i] + y[i - 1]) * dx
    return total

def weighted_average(values, weights):
    if len(values) != len(weights) or not values:
        return None
    w_sum = sum(weights)
    if w_sum == 0:
        return None
    return sum(v * w for v, w in zip(values, weights)) / w_sum

def fluid_total_bbl(time_min, rate_bpm):
    """Total slurry or clean fluid pumped in barrels."""
    return trapezoid_integral(time_min, rate_bpm)
```

Typical outputs per stage:

- pumped fluid total
- total proppant
- average and peak rate
- average and peak treating pressure
- average slurry concentration
- pad duration, slurry duration, flush duration, shut-in time

---

## Module 3 - Shut-In And Screenout Screening

```python
def isip_from_first_falloff_points(time_sec, pressure_psi, n_points=8):
    """
    First-pass ISIP estimate by extrapolating pressure versus sqrt(time)
    immediately after shut-in.
    """
    import math
    n = min(len(time_sec), len(pressure_psi), n_points)
    if n < 2:
        return None
    x = [math.sqrt(max(t, 0.0)) for t in time_sec[:n]]
    y = pressure_psi[:n]
    xb = sum(x) / n
    yb = sum(y) / n
    sxx = sum((xi - xb) ** 2 for xi in x)
    if sxx == 0:
        return None
    sxy = sum((xi - xb) * (yi - yb) for xi, yi in zip(x, y))
    slope = sxy / sxx
    return yb - slope * xb

def screenout_indicator(pressure_psi, rate_bpm, slurry_conc, lookback=5):
    """
    Flag likely near-screenout behavior.
    High risk when pressure rises sharply while rate stalls or drops during
    late slurry at elevated concentration.
    """
    if min(len(pressure_psi), len(rate_bpm), len(slurry_conc)) < lookback + 1:
        return None
    dp = pressure_psi[-1] - pressure_psi[-1 - lookback]
    dq = rate_bpm[-1] - rate_bpm[-1 - lookback]
    dc = slurry_conc[-1] - slurry_conc[-1 - lookback]
    return {"pressure_rise": dp > 300, "rate_softening": dq <= 0, "sand_ramp": dc > 0}
```

---

## Module 4 - Stage Comparison

```python
def pressure_per_cluster(avg_pressure_psi, cluster_count):
    if cluster_count <= 0:
        return None
    return avg_pressure_psi / cluster_count

def fluid_per_cluster(total_fluid_bbl, cluster_count):
    if cluster_count <= 0:
        return None
    return total_fluid_bbl / cluster_count

def proppant_per_ft(total_prop_lb, treated_length_ft):
    if treated_length_ft <= 0:
        return None
    return total_prop_lb / treated_length_ft
```

Compare stages using normalized metrics, not only raw totals. The highest-rate
stage is not necessarily the most effective stage.

---

## Output Format

When using this skill, structure the answer as:

1. File schema and unit assumptions
2. Per-stage summary table
3. Shut-in or screenout diagnostics
4. Cross-stage comparisons and outliers
5. Which file or channel quality issues limit confidence

---

## Integration Points

- Use `pnge:completion-diagnostics` for deeper closure and pressure interpretation.
- Use `pnge:perforation-design` when limited-entry and cluster balance matter.
- Use `pnge:production-chemistry` when slurry chemistry or cleanup affects the stage response.
