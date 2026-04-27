---
name: artificial-lift
description: >
  Design and analyze artificial lift systems for oil and gas wells including
  rod pumping, electric submersible pumps, gas lift, and plunger lift. Covers
  liquid loading prediction using Turner and Coleman critical velocity criteria,
  rod pump design per API RP 11L including polished rod load, gearbox torque,
  pump displacement and fillage, ESP selection and sizing including stage count,
  total dynamic head, motor horsepower and cable losses, gas lift design
  including single-point injection pressure, valve spacing by pressure traverse,
  kickoff requirements, and GLR effect on flowing gradient, and plunger lift
  cycle timing. Use when determining if a well is liquid loading, selecting an
  artificial lift method, sizing an ESP or rod pump, designing a gas lift
  system, or calculating lift performance for PNGE production courses. Trigger
  phrases include liquid loading, Turner criteria, rod pump design, ESP sizing,
  polished rod load, gas lift valve spacing, plunger lift timing, pump-off
  control, artificial lift selection, critical flow rate, or PBHFP calculation.
---

# Artificial Lift Design Calculator

Production engineering skill for sizing and analyzing artificial lift systems.
Covers the full selection-and-design workflow from liquid loading diagnosis
through pump or gas lift sizing.

**Important:** Pump curves and valve trim tables are vendor-specific. Use
these equations for scoping and selection — final design requires vendor
performance curves and software (PIPESIM, PROSPER, or equivalent).

---

## Module 1 — Liquid Loading Diagnosis

### Turner Critical Velocity (1969)

```python
def turner_critical_velocity(sigma_lv, rho_l, rho_g):
    """
    v_crit = 1.593 * sigma_lv^0.25 * (rho_l - rho_g)^0.25 / rho_g^0.5
    sigma_lv: gas-liquid interfacial tension (dynes/cm)  -- ~60 for water/gas
    rho_l:    liquid density (lb/ft3)  -- 62.4 freshwater, 68–72 brine
    rho_g:    gas density at flowing conditions (lb/ft3)
    Returns:  critical velocity (ft/s)
    """
    return 1.593 * sigma_lv**0.25 * (rho_l - rho_g)**0.25 / rho_g**0.5

def gas_density(p_psia, T_f, sg_gas=0.65, z=0.9):
    """Gas density at flowing conditions (lb/ft3)."""
    return (28.97 * sg_gas * p_psia) / (10.73 * (T_f + 459.67) * z)
```

### Critical Flow Rate (Turner)

```python
def critical_flow_rate_mscfd(v_crit, p_psia, T_f, id_in, z=0.9, sg=0.65):
    """
    q_crit (Mscf/d) = 3.067 * P * v_crit * A / (T * Z)
    id_in: tubing ID (inches)
    """
    import math
    A_ft2 = math.pi * (id_in / 24.0)**2   # ft2 (id/2 in feet)
    T_R = T_f + 459.67
    return 3.067 * p_psia * v_crit * A_ft2 / (T_R * z)
```

**Coleman et al. (1991) modification:** multiply Turner velocity by 0.77 for
wells with low liquid-gas ratios or dry gas. More conservative threshold.

**Appalachian Marcellus liquid loading signs:**
- Erratic (slugging) production with liquid fallback
- Casing pressure exceeding tubing pressure at wellhead
- Declining tubing pressure with stable casing pressure
- Onset typically at q_gas < 500–1,000 Mscf/d for 2⅞" tubing

---

## Module 2 — Rod Pump Design (API RP 11L)

### Pump Displacement

```python
def rod_pump_displacement(dp_in, s_in, n_spm, pump_eff=0.80):
    """
    PD = 0.1166 * dp^2 * S * N * eff  (bbl/day)
    dp_in:    plunger diameter (inches): 1.25, 1.5, 1.75, 2.0, 2.25, 2.5
    s_in:     stroke length at pump (inches) -- approximately surface stroke * kr
    n_spm:    strokes per minute
    pump_eff: volumetric efficiency (0.7–0.95 typical)
    """
    return 0.1166 * dp_in**2 * s_in * n_spm * pump_eff
```

### Polished Rod Loads (Simplified API RP 11L)

```python
def rod_string_weight(rod_sizes, rod_lengths):
    """
    Rod unit weights (lb/ft): #75=1.63, #86=1.99, #97=2.56, #108=3.05, #119=3.60
    rod_sizes:   list of tuples (size_code, lb_per_ft)
    rod_lengths: corresponding lengths (ft)
    Returns: buoyed weight in fluid (SG_fluid=1.0 default)
    """
    w_air = sum(w * L for (_, w), L in zip(rod_sizes, rod_lengths))
    return w_air

def peak_polished_rod_load(w_rod_buoyed, fo, wf):
    """
    PPRL = W_rf + Fo + WF   (simplified)
    w_rod_buoyed: buoyed rod weight (lb)
    fo:           fluid load = 0.340 * dp_in^2 * net_lift_ft  (lb) for fresh water
    wf:           dynamic load factor (typically 0.25–0.40 * w_rod_buoyed)
    """
    return w_rod_buoyed + fo + wf

def fluid_load(dp_in, net_lift_ft, fluid_sg=1.0):
    """Fo = 0.340 * dp^2 * H * SG  (lb)"""
    return 0.340 * dp_in**2 * net_lift_ft * fluid_sg
```

### API Rod Grades Reference

| Grade | Min Yield (psi) | Min UTS (psi) | Service |
|-------|----------------|--------------|---------|
| C (Grade C) | 60,000 | 90,000 | Non-corrosive |
| D (Grade D) | 115,000 | 140,000 | Non-corrosive deep wells |
| K (Grade K) | 55,000 | 90,000 | Corrosive (H2S) |
| API D mod. | 115,000 | 140,000 | Sucker rod steel standard |

---

## Module 3 — ESP Design

### Total Dynamic Head

```python
def esp_tdh(pump_depth_ft, wellhead_pressure_psi, intake_pressure_psi,
            fluid_sg=1.0):
    """
    TDH (ft) = net_lift + friction_loss + wellhead_head
    net_lift = pump_depth - (intake_pressure * 2.31 / sg)
    Simplified: TDH = (pump_depth * sg / 2.31) + (Pwh - Pintake) * 2.31/sg
    Returns TDH in feet of fluid.
    """
    lift = pump_depth_ft - intake_pressure_psi * 2.31 / fluid_sg
    wh_head = wellhead_pressure_psi * 2.31 / fluid_sg
    return max(0.0, lift + wh_head)
```

### Motor Sizing

```python
def esp_motor_hp(q_bpd, tdh_ft, fluid_sg=1.0,
                 pump_eff=0.65, motor_eff=0.93, cable_loss_frac=0.05):
    """
    HP = Q(gpm) * TDH(ft) * SG / (3960 * pump_eff * motor_eff * (1-cable_loss))
    q_bpd: flow rate (bbl/day)
    """
    q_gpm = q_bpd * 0.02917   # bbl/day to gpm
    return (q_gpm * tdh_ft * fluid_sg /
            (3960 * pump_eff * motor_eff * (1 - cable_loss_frac)))

def esp_stage_count(tdh_ft, head_per_stage_ft):
    """Number of stages needed to achieve TDH."""
    import math
    return math.ceil(tdh_ft / head_per_stage_ft)
```

**ESP selection notes:**
- Determine operating flow rate from IPR/VLP intersection
- Select pump series based on casing ID and flow rate range
- Head per stage from vendor curve at operating point
- Downthrust vs. upthrust: ensure operating point avoids runout

---

## Module 4 — Gas Lift Design

### Flowing Gradient with Injection

```python
def glr_gradient(glr_scf_per_bbl, p_psi, T_f, oil_api=35, wc=0.0):
    """
    Approximate flowing gradient (psi/ft) for a given GLR.
    Uses simplified mixture density approach.
    glr_scf_per_bbl: producing gas-liquid ratio
    Returns: approximate gradient (psi/ft)
    Note: use Beggs-Brill or Hagedorn-Brown for rigorous calculation.
    """
    rho_oil = (141.5 / (oil_api + 131.5)) * 62.4   # lb/ft3
    rho_water = 64.0   # lb/ft3 (brine ~67)
    rho_liquid = (1 - wc) * rho_oil + wc * rho_water
    # Approximate in-situ gas volume fraction
    gas_vol_frac = glr_scf_per_bbl / (5.615 * (p_psi / 14.7))
    rho_mix = rho_liquid * (1 - gas_vol_frac) + 0.05 * gas_vol_frac
    return rho_mix / 144.0   # psi/ft
```

### Single-Point Injection Operating Pressure

```python
def gas_lift_injection_pressure(depth_ft, surface_injection_psi,
                                 gas_sg=0.65, T_avg_f=150.0):
    """
    Approximate bottomhole injection pressure.
    P_inj_BH = P_inj_surface + gradient * depth
    Gas gradient approx: 0.0085 * SG * depth / 1000  (psi/ft * ft)
    """
    gas_grad_psi_per_ft = 0.433 * gas_sg * (14.7 / (14.7 + surface_injection_psi / 2))
    return surface_injection_psi + gas_grad_psi_per_ft * depth_ft
```

### Minimum GLR for Unloading (Poettmann-Carpenter rule of thumb)

```python
def minimum_glr_for_lift(depth_ft, target_bfpd, api=35):
    """
    Rough minimum GLR (scf/bbl) to lift fluid to surface.
    ~200 scf/bbl per 1000 ft of lift as a starting approximation.
    """
    return 200 * depth_ft / 1000.0
```

---

## Module 5 — Plunger Lift

### Minimum GLR (Foss and Gaul, 1965)

```python
def plunger_minimum_glr(depth_ft, liquid_per_cycle_bbl=1.0):
    """
    Minimum casing GLR needed:
    GLR_min = (A + B * depth_ft) * liquid_per_cycle
    A = 30, B = 0.12 (typical constants)
    Returns: min GLR in scf/bbl
    """
    A, B = 30.0, 0.12
    return (A + B * depth_ft) * liquid_per_cycle_bbl

def plunger_rise_velocity(p_casing_psi, p_tubing_psi, plunger_weight_lb=10.0,
                           id_in=2.441):
    """
    Approximate plunger rise velocity (ft/min).
    Driving force = (P_cas - P_tub) * A_tubing - W_plunger - W_fluid
    Rough empirical: v_rise = k * (P_cas - P_min)  where k ~ 1.5 ft/min per psi
    """
    dp = p_casing_psi - p_tubing_psi
    k = 1.5   # ft/min per psi of differential
    return max(0.0, k * dp)
```

**Plunger lift selection criteria:**
- GOR > 400 scf/bbl at operating depth
- Liquid rate < 150 bbl/day (low volume, intermittent producers)
- Tubing ID 1.90"–3.5" with smooth bore
- Common in late-life Appalachian shallow gas wells

---

## Lift Method Selection Matrix

| Condition | Preferred Lift | Notes |
|-----------|---------------|-------|
| Liquid loading gas well, low volume | Plunger lift | Low cost, no power |
| Liquid loading gas well, moderate volume | Velocity string | Reduce tubing ID |
| Oil well, < 2,000 bbl/day, < 8,000 ft | Rod pump | Most common onshore |
| Oil well, high rate, deep, deviated | ESP | High rate, limited run life |
| Oil well, multiple zones | Gas lift | Flexible, no downhole equipment |
| CO2 flood or gassy well | Gas lift (avoid ESP) | Gas handling advantage |

---

## Output Format

```
## Artificial Lift Assessment — [Well Name / API]
**Formation:** [Name] | **Depth:** X,XXX ft | **Current Rate:** XXX bbl/day gas/oil

### Liquid Loading Check (Gas Wells)
| Tubing ID (in) | Critical Velocity (ft/s) | Critical Rate (Mscf/d) | Current Rate | Loading? |
|----------------|--------------------------|------------------------|--------------|---------|
| 2.441 | | | | YES/NO |

### Recommended Lift Method: [Rod Pump / ESP / Gas Lift / Plunger]
**Rationale:** [brief justification]

### Design Summary
| Parameter | Value | Units |
|-----------|-------|-------|
| Pump displacement | | bbl/day |
| Motor HP (ESP) | | HP |
| Stages needed | | count |
| PPRL (rod pump) | | lb |
| Injection pressure (gas lift) | | psia |

### Confidence: [HIGH / MEDIUM / LOW]
```

---

## Error Handling

| Condition | Cause | Action |
|-----------|-------|--------|
| Critical velocity > actual velocity | Normal production | No lift needed yet |
| TDH negative | Intake pressure > hydrostatic + wellhead | Check input pressures |
| Stage count > 300 | Very deep or high TDH | Consider multistage or smaller pump series |
| GLR below minimum | Insufficient gas for gas lift | Consider ESP or rod pump |

---

## Caveats

- Turner critical velocity is derived for vertical wells. For deviated or
  horizontal sections, liquid holdup models (Beggs-Brill) are required.
- ESP motor HP calculations assume constant SG and efficiency. Actual
  performance varies with free gas, temperature, and viscosity. Always use
  vendor pump curves for final selection.
- Gas lift valve spacing requires full pressure traverse software. Single-point
  injection equations here are simplified for scoping only.
- Rod pump loads include acceleration forces that are SPM-dependent and
  significant at high pump speeds; use API RP 11L tables for final design.
- Plunger lift efficiency depends heavily on casing-tubing annulus volume and
  shut-in time; cycle optimization requires field testing.
