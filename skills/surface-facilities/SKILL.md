---
name: surface-facilities
description: >
  Design and size surface production facilities for oil and gas operations
  including separators, glycol dehydration units, and compression systems.
  Covers two-phase and three-phase separator sizing using Souders-Brown gas
  capacity equation and liquid retention time criteria, operating pressure
  selection for stage separation and hydrocarbon recovery optimization, glycol
  dehydration design using TEG absorption including circulation rate, reboiler
  duty, and dew point depression, and compression system design including
  pressure ratio selection, adiabatic horsepower, intercooling requirements,
  and multistage staging strategy. Also covers wellhead backpressure effects
  on inflow performance and production rates. Use when sizing a test separator,
  designing a field dehydration unit, selecting compression for gathering
  systems, calculating glycol circulation rates, or evaluating how surface
  backpressure affects well deliverability. Trigger phrases include separator
  sizing, two-phase separator, three-phase separator design, glycol dehydration,
  TEG circulation rate, reboiler duty, compression horsepower, stage separation,
  dew point depression, wellhead backpressure, or surface facility design.
---

# Surface Facilities Design Calculator

Production facilities skill for sizing separators, glycol dehydration systems,
and compression equipment. Calibrated for Appalachian gas and oil production.

**Important:** These are preliminary sizing equations for scoping and
conceptual design. Final equipment sizing requires detailed process simulation
(HYSYS, ProMax, or equivalent) with full fluid compositions and phase behavior.

---

## Module 1 — Separator Sizing

### Gas Capacity (Modified Souders-Brown)

```python
import math

def separator_gas_capacity_mmscfd(D_ft, L_eff_ft, P_psia, T_f,
                                   gas_sg=0.65, z=0.9,
                                   Ks=0.25, separator_type="vertical"):
    """
    Gas handling capacity based on droplet settling (Souders-Brown).
    Ks = 0.25 ft/s vertical, 0.40 ft/s horizontal (typical gas-liquid)
    D_ft:    vessel internal diameter (ft)
    L_eff_ft: effective vessel length (ft)  -- use D for vertical
    P_psia:  operating pressure
    T_f:     operating temperature (°F)
    Returns: gas capacity (MMscf/day)
    """
    T_R = T_f + 459.67
    # Gas density at operating conditions
    rho_g = (28.97 * gas_sg * P_psia) / (10.73 * T_R * z)  # lb/ft3
    # Water density ~62.4; oil ~50–55; use water as conservative
    rho_l = 62.4
    # Terminal droplet velocity
    v_t = Ks * math.sqrt((rho_l - rho_g) / rho_g)  # ft/s
    # Cross-sectional area for gas flow
    if separator_type.lower() == "vertical":
        A_g_ft2 = math.pi / 4.0 * D_ft**2
    else:
        # Horizontal: assume gas occupies top half
        A_g_ft2 = math.pi / 8.0 * D_ft**2
    # Gas flow at operating conditions (ft3/s)
    Q_op_ft3_s = v_t * A_g_ft2
    # Convert to MMscfd (standard conditions: 14.7 psia, 60°F)
    Q_scf_s = Q_op_ft3_s * (P_psia / 14.7) * (520.0 / T_R) * z
    return Q_scf_s * 86400.0 / 1e6
```

### Liquid Retention Time (Two-Phase)

```python
def separator_liquid_volume_bbl(q_liquid_bpd, retention_time_min=1.5):
    """
    Required liquid volume for retention time.
    retention_time_min: 1–2 min two-phase; 3–5 min three-phase (oil-water sep)
    Returns: liquid volume needed (bbl)
    """
    return q_liquid_bpd * retention_time_min / (24.0 * 60.0)

def separator_diameter_from_liquid(V_liquid_bbl, L_D_ratio=3.0,
                                    liquid_fill_frac=0.5):
    """
    For horizontal separators: V_vessel = pi/4 * D^2 * L
    L = L_D_ratio * D;  V_liquid = liquid_fill_frac * V_vessel
    Returns: D (ft), L (ft)
    """
    V_ft3 = V_liquid_bbl * 5.615
    V_vessel_ft3 = V_ft3 / liquid_fill_frac
    # V = pi/4 * D^2 * L_D * D = pi/4 * L_D * D^3
    D_ft = (V_vessel_ft3 / (math.pi / 4.0 * L_D_ratio))**(1.0/3.0)
    L_ft = L_D_ratio * D_ft
    return {"D_ft": D_ft, "L_ft": L_ft, "D_in": D_ft * 12.0}
```

### Three-Phase Separator (Water-Oil Retention)

```python
def three_phase_retention_check(q_oil_bpd, q_water_bpd,
                                 api_oil=35, T_f=80.0,
                                 retention_oil_min=5.0,
                                 retention_water_min=10.0):
    """
    Stokes' law settling time for water droplets in oil.
    Minimum retention for adequate oil-water separation.
    Higher API or temperature = lower viscosity = faster settling = less time needed.
    Returns: required liquid volumes (bbl).
    """
    V_oil_bbl = q_oil_bpd * retention_oil_min / (24.0 * 60.0)
    V_water_bbl = q_water_bpd * retention_water_min / (24.0 * 60.0)
    return {"V_oil_bbl": V_oil_bbl, "V_water_bbl": V_water_bbl,
            "V_total_liquid_bbl": V_oil_bbl + V_water_bbl}
```

---

## Module 2 — Stage Separation Pressure Optimization

```python
def stage_separation_pressures(P_wellhead_psia, n_stages=3,
                                 P_final_psia=25.0):
    """
    Optimal intermediate separator pressures for maximum liquid recovery.
    Equal pressure ratios: r = (P_wellhead / P_final)^(1/n_stages)
    P_wellhead_psia: first separator operating pressure
    P_final_psia:   stock tank or sales line pressure
    Returns: list of separator pressures (psia)
    """
    ratio = (P_wellhead_psia / P_final_psia)**(1.0 / n_stages)
    pressures = []
    P = P_wellhead_psia
    for i in range(n_stages):
        pressures.append(round(P, 0))
        P = P / ratio
    return pressures

# Example: 1200 psia wellhead, 3 stages, 25 psia stock tank
# Pressures: [1200, 195, 32, 25] (approx equal ratios ~6.2x each stage)
```

**Stage separation benefits:**
- Maximizes liquid recovery by staged pressure reduction
- Reduces vapor losses from flash at stock tank
- Typical Appalachian: 2–3 stages (wellhead, low-pressure, sales)

---

## Module 3 — Glycol Dehydration (TEG)

### Dew Point Depression

```python
def teg_dew_point_depression(contact_temp_f, circulation_rate_gal_lb,
                               teg_concentration_wt_frac=0.995):
    """
    Approximate dew point depression from TEG contactor.
    Uses Worley (1967) correlation: delta_T ~ f(TEG concentration, L/G ratio)
    contact_temp_f: contactor temperature (°F)  -- typically 80–100°F
    circulation_rate_gal_lb: TEG circulation (gal TEG / lb H2O absorbed)
       typical range: 1.0–1.5 gal/lb for delta_T depression of 40–80°F
    teg_concentration_wt_frac: 0.995–0.999 (99.5–99.9% TEG by weight)
    Returns: approximate dew point depression (°F)
    """
    # Simplified linear approximation to Worley chart
    # At L/G = 1.0 gal/lb and 99.5% TEG: depression ~ 50°F
    # At L/G = 1.5 gal/lb: ~ 70°F
    base_depression = 50.0
    lg_factor = (circulation_rate_gal_lb - 1.0) * 40.0
    conc_factor = (teg_concentration_wt_frac - 0.995) * 2000.0
    return base_depression + lg_factor + conc_factor
```

### TEG Circulation Rate

```python
def teg_circulation_rate(water_content_in_lb_mmscf,
                          water_content_out_lb_mmscf,
                          gas_rate_mmscfd,
                          lg_ratio_gal_per_lb=1.2):
    """
    Water absorbed = (Win - Wout) * gas_rate  (lb/day)
    TEG rate = water_absorbed * L/G ratio  (gal/day)
    water_content: lb H2O per MMscf of gas (from water content chart or calc)
    lg_ratio: typically 1.0–1.5 gal TEG / lb H2O
    """
    water_removed_lb_day = (water_content_in_lb_mmscf - water_content_out_lb_mmscf) * gas_rate_mmscfd
    teg_rate_gpd = water_removed_lb_day * lg_ratio_gal_per_lb
    return {"water_removed_lb_day": water_removed_lb_day,
            "teg_rate_gpd": teg_rate_gpd,
            "teg_rate_gph": teg_rate_gpd / 24.0}
```

### Reboiler Duty

```python
def teg_reboiler_duty_mmbtu_day(teg_rate_gpd, duty_per_gal=800.0):
    """
    Approximate reboiler heat duty.
    duty_per_gal: BTU per gallon of TEG circulated
      Typical: 600–1200 BTU/gal (lower for efficient contactors)
    Returns: reboiler duty (MMBtu/day)
    """
    return teg_rate_gpd * duty_per_gal / 1e6
```

**TEG system reference:**
| Parameter | Typical Value | Notes |
|-----------|--------------|-------|
| TEG purity (lean) | 99.0–99.95 wt% | Higher = better depression |
| Reboiler temp | 375–400°F | Max 400°F to avoid TEG degradation |
| Contactor stages | 3–8 trays or 1–2 packing beds | More stages = better contact |
| L/G ratio | 1.0–1.5 gal/lb | Minimum 1.0; diminishing returns above 2.0 |

---

## Module 4 — Compression

### Adiabatic Horsepower

```python
def compression_horsepower(Q_mmscfd, T_suction_f, P_suction_psia,
                             P_discharge_psia, k=1.27, z=0.9, eff=0.75):
    """
    Adiabatic (isentropic) compression horsepower.
    HP = (k / (k-1)) * (Z*T_s/528) * (P_d/P_s)^((k-1)/k) - 1) * Q * C
    C = 0.0857 for Q in MMscfd, T in °R, P in psia -> HP in bhp
    k = Cp/Cv: 1.27 natural gas (approx), 1.28–1.35 rich gas
    eff: overall isentropic efficiency (0.70–0.80 typical reciprocating)
    """
    T_R = T_suction_f + 459.67
    r = P_discharge_psia / P_suction_psia
    exponent = (k - 1.0) / k
    HP_ideal = 0.0857 * (k / (k - 1.0)) * (z * T_R / 520.0) * (r**exponent - 1.0) * Q_mmscfd
    return HP_ideal / eff

def compression_ratio(P_suction_psia, P_discharge_psia):
    """r = P_d / P_s  -- keep < 4.0 per stage (< 3.5 for reciprocating)"""
    return P_discharge_psia / P_suction_psia

def compression_stages_needed(P_suction_psia, P_discharge_psia,
                                max_ratio_per_stage=3.5):
    """Minimum stages for given overall ratio and max ratio per stage."""
    import math
    total_ratio = P_discharge_psia / P_suction_psia
    return math.ceil(math.log(total_ratio) / math.log(max_ratio_per_stage))
```

### Discharge Temperature

```python
def discharge_temperature(T_suction_f, P_suction_psia, P_discharge_psia,
                            k=1.27, z=0.9):
    """
    T_d = T_s * (P_d/P_s)^((k-1)/k)  (isentropic, ideal gas)
    Returns: discharge temperature (°F)
    For reciprocating: actual T_d ~20–30°F higher due to heat of compression.
    Intercooling required when T_d > 300°F (typical limit).
    """
    T_R = T_suction_f + 459.67
    r = P_discharge_psia / P_suction_psia
    T_d_R = T_R * r**((k - 1.0) / k)
    return T_d_R - 459.67
```

---

## Module 5 — Wellhead Backpressure Effect

```python
def backpressure_deliverability_ratio(P_res_psia, P_wf_orig_psia,
                                        P_wf_new_psia, n=0.8):
    """
    Simplified backpressure equation for gas wells:
    q2/q1 = (P_res^2 - P_wf2^2)^n / (P_res^2 - P_wf1^2)^n
    n: backpressure exponent (0.5 turbulent to 1.0 laminar)
    Returns: ratio of new rate to original rate
    """
    num = (P_res_psia**2 - P_wf_new_psia**2)**n
    den = (P_res_psia**2 - P_wf_orig_psia**2)**n
    return num / den

def production_loss_from_backpressure(q_orig_mscfd, P_res_psia,
                                        P_surface_orig_psia,
                                        P_surface_new_psia,
                                        tubing_gradient_psi_ft=0.1,
                                        depth_ft=7500.0, n=0.8):
    """
    Estimate production rate change when surface pressure changes.
    Converts surface backpressure to flowing BHP change.
    """
    P_wf_orig = P_surface_orig_psia + tubing_gradient_psi_ft * depth_ft
    P_wf_new = P_surface_new_psia + tubing_gradient_psi_ft * depth_ft
    ratio = backpressure_deliverability_ratio(P_res_psia, P_wf_orig, P_wf_new, n)
    return {"q_new_mscfd": q_orig_mscfd * ratio, "ratio": ratio,
            "delta_q_mscfd": q_orig_mscfd * (ratio - 1.0)}
```

---

## Output Format

```
## Surface Facilities Design — [Field / Well Pad]
**Gas rate:** X.X MMscfd | **Liquid rate:** XXX bbl/day | **WOR:** X.X

### Separator Sizing
| Vessel | Type | Size | Operating P (psia) | Gas cap. (MMscfd) | Liquid vol (bbl) |
|--------|------|------|-------------------|-------------------|-----------------|
| First stage | H/V | XX" x XX'-0" | | | |
| Second stage | | | | | |

### Dehydration System
| Parameter | Value |
|-----------|-------|
| Water content in (lb/MMscf) | |
| Water content out (lb/MMscf) | |
| TEG rate (gal/hr) | |
| Reboiler duty (MMBtu/day) | |
| Expected dew point depression (°F) | |

### Compression
| Stage | Suction P (psia) | Discharge P (psia) | Ratio | HP (bhp) | T_d (°F) |
|-------|-----------------|-------------------|-------|---------|---------|
| 1 | | | | | |
| 2 | | | | | |

### Backpressure Sensitivity
| Wellhead P (psia) | Rate (Mscf/d) | Change vs. base |
|-------------------|--------------|----------------|
| | | |
```

---

## Error Handling

| Condition | Cause | Action |
|-----------|-------|--------|
| Separator undersized | Gas rate > capacity | Increase D or use horizontal vessel |
| TEG rate very high | Low L/G or wet gas | Verify water content; check inlet separator |
| Discharge T > 300°F | High ratio, hot suction | Add intercooler; split into more stages |
| Production loss > 20% | High backpressure relative to reservoir P | Evaluate compression or larger gathering pipe |

---

## Caveats

- Souders-Brown Ks values are general guidance. Foaming fluids (surfactants,
  condensate) require lower Ks (0.10–0.15); use defoamer injection.
- TEG dew point depression depends strongly on inlet gas composition and
  tray efficiency. Use BTEX emissions regulations (EPA MACT standards) for
  reboiler operation > 225°F.
- Compression horsepower assumes constant k and Z. In reality, both vary with
  pressure and temperature — compressor vendors calculate based on actual EOS.
- Stage separation pressure optimization minimizes vapor losses at stock tank.
  Actual optimum may differ based on sales gas specifications and liquid value.
- Wellhead backpressure effects are stronger at low reservoir pressure (late
  life). Early in well life, large ΔP drives are less sensitive to backpressure.
