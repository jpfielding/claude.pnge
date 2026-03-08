---
name: nodal-analysis-multiphase
description: >
  Perform production system nodal analysis with multiphase flow screening
  including inflow performance relationships, vertical lift performance,
  tubing and choke sensitivity, compression impact, and artificial-lift tuning.
  Use when the user asks for IPR and VLP matching, nodal analysis, well
  deliverability, flowing bottomhole pressure, tubing size sensitivity, choke
  optimization, wellhead pressure effects, compression debottlenecking, gas
  lift response, or production optimization. Trigger phrases include nodal
  analysis, IPR, VLP, tubing sensitivity, choke size, outflow curve,
  multiphase lift, production system optimization, deliverability, or
  wellhead backpressure.
---

# Nodal Analysis And Multiphase Production Optimization

Production systems skill for matching reservoir inflow with wellbore and
surface outflow. Use it for screening and sensitivity analysis; final design
should still be checked with calibrated multiphase correlations or a field
simulator.

**Important:** Nodal answers are only as good as the PVT, test separator, and
pressure data behind them. If PVT is weak, couple this skill with
`pnge:petroleum-pvt`.

---

## Data To Request First

- Reservoir pressure or latest static / build-up estimate
- Test rate, flowing bottomhole pressure, and flowing wellhead pressure
- Oil rate, gas rate, water rate, GOR, water cut, and fluid gravities
- Tubing ID, setting depth, deviation profile, and choke size
- Flowline and separator pressure constraints
- Temperature profile or average flowing temperature
- Artificial lift status, compression status, and separator conditions

---

## Workflow

1. Select an inflow model consistent with fluid type and available data.
2. Build an outflow approximation from wellhead pressure back to perforations.
3. Solve for the intersection between IPR and VLP.
4. Run sensitivities on choke, tubing, lift gas, or compression.
5. State which lever moves the inflow curve and which lever moves the outflow curve.

---

## Module 1 - Inflow Performance

```python
def productivity_index(q_bpd, pr_psia, pwf_psia):
    """Linear PI for undersaturated oil or small drawdown cases."""
    dp = pr_psia - pwf_psia
    if dp <= 0:
        return None
    return q_bpd / dp

def vogel_qmax(q_test_bpd, pr_psia, pwf_test_psia):
    """
    Vogel inflow for solution-gas drive oil wells.
    q/ qmax = 1 - 0.2*(pwf/pr) - 0.8*(pwf/pr)^2
    """
    r = pwf_test_psia / pr_psia
    denom = 1.0 - 0.2 * r - 0.8 * r**2
    if denom <= 0:
        return None
    return q_test_bpd / denom

def vogel_rate(pr_psia, pwf_psia, qmax_bpd):
    """Oil rate from Vogel IPR."""
    r = pwf_psia / pr_psia
    return qmax_bpd * (1.0 - 0.2 * r - 0.8 * r**2)

def gas_deliverability_rate(pr_psia, pwf_psia, C, n):
    """
    Rawlins-Schellhardt backpressure equation in pressure-squared form.
    q = C * (pr^2 - pwf^2)^n
    """
    term = pr_psia**2 - pwf_psia**2
    if term <= 0:
        return 0.0
    return C * term**n

def gas_C_from_test(q_mscfd, pr_psia, pwf_psia, n):
    """Calibrate gas deliverability constant from one test point."""
    term = pr_psia**2 - pwf_psia**2
    if term <= 0:
        return None
    return q_mscfd / (term**n)
```

**Model selection**

| Fluid system | Preferred screening IPR |
|-------------|--------------------------|
| Oil above bubble point | Linear PI |
| Solution-gas drive oil | Vogel |
| Dry gas / gas condensate | Backpressure deliverability |
| Tight gas with non-Darcy effects | Deliverability plus turbulence correction |

---

## Module 2 - Outflow / Vertical Lift Screening

```python
def liquid_density_lbft3(oil_api=40.0, water_cut=0.0, water_density_lbft3=62.4):
    """No-slip bulk liquid density from oil and water fractions."""
    oil_density = 141.5 / (oil_api + 131.5) * 62.4
    return (1.0 - water_cut) * oil_density + water_cut * water_density_lbft3

def hydrostatic_gradient_psi_ft(mixture_density_lbft3):
    """Hydrostatic gradient from density."""
    return mixture_density_lbft3 / 144.0

def pwf_from_whp(whp_psia, tvd_ft, mixture_gradient_psi_ft,
                 friction_loss_psi=0.0):
    """
    Approximate flowing bottomhole pressure from wellhead conditions.
    """
    return whp_psia + mixture_gradient_psi_ft * tvd_ft + friction_loss_psi

def flowline_backpressure(separator_pressure_psi, line_loss_psi=0.0):
    """Backpressure seen by the tree from downstream constraints."""
    return separator_pressure_psi + line_loss_psi
```

**Use with caution**

- Homogeneous mixture gradients are screening tools only.
- Deviated wells, slug flow, and high GLR often need Beggs-Brill, Hagedorn-Brown, or field-calibrated lift tables.
- If the answer changes materially with a small gradient change, report that sensitivity explicitly.

---

## Module 3 - Choke And Surface Constraint Screening

```python
def choke_dp(p_upstream_psia, p_downstream_psia):
    """Simple choke differential pressure."""
    return max(0.0, p_upstream_psia - p_downstream_psia)

def compression_ratio(p_suction_psia, p_discharge_psia):
    """Compressor pressure ratio."""
    if p_suction_psia <= 0:
        return None
    return p_discharge_psia / p_suction_psia

def rate_gain_pct(q_old, q_new):
    """Percent production gain from an optimization change."""
    if q_old == 0:
        return None
    return 100.0 * (q_new - q_old) / q_old
```

**Operational levers**

| Lever | Moves mostly | Typical effect |
|------|--------------|----------------|
| Lower wellhead / separator pressure | Outflow curve down | Higher rate |
| Larger tubing ID | Outflow curve down | Less friction, more rate |
| Larger choke | Outflow restriction down | Higher rate until another bottleneck takes over |
| Gas lift / lower liquid holdup | Outflow curve down | More drawdown, less gradient |
| Stimulation / reduced skin | Inflow curve up | Higher rate at same pwf |

---

## Module 4 - Nodal Matching

```python
def nodal_mismatch(q_ipr, q_vlp):
    """Positive value means inflow exceeds outflow at the tested point."""
    return q_ipr - q_vlp

def choose_best_candidate(candidates):
    """
    candidates: list of dicts with keys q_ipr, q_vlp, and any metadata.
    Returns the candidate with the smallest absolute mismatch.
    """
    if not candidates:
        return None
    return min(candidates, key=lambda c: abs(c["q_ipr"] - c["q_vlp"]))
```

In practice, scan a range of candidate rates and select the rate where inflow
and outflow are closest. Then pressure-match that solution against measured
flowing bottomhole or wellhead data.

---

## Module 5 - Diagnostic Patterns

| Observation | Likely bottleneck |
|------------|-------------------|
| Reservoir pressure healthy, high wellhead pressure sensitivity | Surface or flowline backpressure |
| Weak response to choke opening | Reservoir inflow limited or already critical flow |
| Rate rises strongly with larger tubing | Tubing friction dominated |
| Large rate gain from lower separator pressure | Compression / facility bottleneck |
| Gas lift only helps at high liquid loading | Gradient dominated outflow problem |

---

## Output Format

When using this skill, structure the answer as:

1. Inflow model chosen and why
2. Outflow assumptions and gradient sensitivity
3. Estimated operating point
4. Sensitivity ranking of choke, tubing, compression, or lift changes
5. Recommended next measurement or field action

---

## Integration Points

- Use `pnge:petroleum-pvt` for black-oil and gas property inputs.
- Use `pnge:artificial-lift` for gas lift, rod pump, ESP, or plunger-lift optimization.
- Use `pnge:surface-facilities` for separator and compression constraints.
- Use `pnge:rta-production` or `pnge:well-test-analysis` when inflow uncertainty dominates.
