---
name: production-surveillance
description: >
  Analyze local SCADA, historian, test-separator, and daily production exports
  for well surveillance, anomaly detection, optimization, and candidate
  ranking. Use when the user provides CSV or spreadsheet histories of rates,
  pressures, temperatures, choke settings, lift parameters, compressor data,
  plunger cycles, or test-separator results and asks why a well changed, where
  bottlenecks are, which wells to prioritize, or how to diagnose slugging,
  liquid loading, compression constraints, or lift underperformance. Trigger
  phrases include production surveillance, SCADA export, historian CSV, daily
  well data, test separator, candidate ranking, anomaly detection, rate drop,
  compressor bottleneck, or lift tuning.
---

# Production Surveillance

Operational skill for interpreting local time-series data from production
systems. It is built for engineers who already have the field exports but need
a disciplined workflow to diagnose what changed and rank the next actions.

**Important:** Surveillance starts with event context. Pull known operational
changes first: choke moves, compressor trips, lift changes, shut-ins, chemical
changes, workovers, and separator reroutes.

---

## Preferred Inputs

- Daily or hourly oil, gas, and water rates
- Tubing, casing, and wellhead pressures
- Choke setting, separator pressure, compressor suction/discharge
- Artificial-lift parameters: SPM, current draw, gas-lift rate, plunger cycles
- Well tests, not just allocated rates
- Event log with outages, interventions, setpoint changes, and routing changes

---

## Workflow

1. Build a clean timebase and mark missing or allocated values.
2. Compare rate changes against pressure and operating changes.
3. Separate reservoir decline from facility or lift constraints.
4. Score the wells or periods worth intervention.
5. Recommend the next measurement before recommending a workover.

---

## Module 1 - Basic Derived Metrics

```python
def gor_scf_stb(gas_mscfd, oil_bopd):
    """Gas-oil ratio in scf/STB."""
    if oil_bopd <= 0:
        return None
    return gas_mscfd * 1000.0 / oil_bopd

def water_cut_frac(water_bwpd, oil_bopd):
    """Water cut as a fraction of liquid."""
    liquid = water_bwpd + oil_bopd
    if liquid <= 0:
        return None
    return water_bwpd / liquid

def pressure_normalized_rate(q, p_ref, p_now):
    """
    Simple screening normalization for constrained wells.
    """
    if p_now <= 0:
        return None
    return q * p_ref / p_now
```

---

## Module 2 - Trend And Change Detection

```python
def moving_average(values, window):
    if window <= 0 or len(values) < window:
        return None
    out = []
    for i in range(window - 1, len(values)):
        out.append(sum(values[i - window + 1:i + 1]) / window)
    return out

def percent_change(old, new):
    if old == 0:
        return None
    return 100.0 * (new - old) / old

def simple_decline_rate(q_start, q_end, days):
    if q_start <= 0 or days <= 0:
        return None
    return (q_start - q_end) / q_start / days
```

Look for:

- rate down, pressures up: surface or outflow constraint
- rate down, pressures down: reservoir depletion or loading
- gas up while liquids down: liquid loading or phase behavior change
- strong wellhead pressure sensitivity: compression or separator bottleneck

---

## Module 3 - Candidate Ranking

```python
def candidate_score(rate_loss_pct, pressure_penalty_pct,
                    data_quality=1.0, workover_complexity=1.0):
    """
    Simple ranking score: higher means more attractive candidate.
    workover_complexity > 1 penalizes difficult candidates.
    """
    base = max(rate_loss_pct, 0.0) + max(pressure_penalty_pct, 0.0)
    return data_quality * base / max(workover_complexity, 0.1)

def pressure_penalty(current_whp, target_whp):
    if current_whp <= 0:
        return None
    return 100.0 * max(current_whp - target_whp, 0.0) / current_whp
```

Rank candidates separately for:

- backpressure reduction
- lift optimization
- chemical cleanup
- integrity follow-up
- reservoir-driven underperformance

Mixing those classes into one score usually hides the real action.

---

## Module 4 - Common Surveillance Diagnoses

| Pattern | Likely issue |
|--------|--------------|
| Rate drop after compressor suction pressure rises | Compression bottleneck |
| Rising casing pressure, unstable tubing pressure, intermittent gas | Liquid loading |
| Current draw rises while rate falls on ESP well | Pump wear, gas interference, or intake problem |
| Rod load indicators worsen with falling fillage | Pump-off or gas interference |
| Choke opened but rate does not respond | Reservoir or downstream critical-flow limit |
| Test-separator gains not reflected in allocated data | Allocation issue, not field change |

---

## Output Format

When using this skill, structure the answer as:

1. Data source quality and time resolution
2. Main rate / pressure / operating changes
3. Most likely constraint class
4. Candidate ranking or next-well shortlist
5. Next high-value measurement or field action

---

## Integration Points

- Use `pnge:nodal-analysis-multiphase` for inflow-outflow sensitivity.
- Use `pnge:artificial-lift` for lift-specific tuning.
- Use `pnge:well-integrity-barriers` when annulus or integrity signals appear.
- Use `pnge:rta-production` when the change looks reservoir-driven rather than operational.
