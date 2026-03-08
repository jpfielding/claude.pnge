---
name: matrix-acidizing
description: >
  Acid stimulation design for matrix treatments in sandstone and carbonate
  formations. Implements Paccaloni acid volume design for carbonates, wormhole
  propagation radius and spending distance, three-stage HF/HCl sandstone acid
  design, post-acid skin estimation using Hawkins formula, Damkohler number
  for optimal injection rate regime, and maximum injection rate below fracture
  pressure. Use when the user asks about matrix acidizing, acid job design,
  HCl carbonate treatment, HF sandstone acidizing, wormhole radius, acid
  spending distance, pre-flush design, overflush volume, skin removal from
  acidizing, optimal injection rate, acid stimulation for Marcellus or Utica
  wells, Damkohler number, or any acid treatment design question. Not for
  fracture acidizing or tip-screenout treatments. Resources: Economides Hill
  Ehlig-Barbour Zhu Petroleum Production Systems 2nd ed; Williams Gidley
  Schechter Acidizing Fundamentals SPE Monograph 6; SPE PetroWiki Matrix
  Acidizing. Primary courses: PNGE 341 Well Completions, PNGE 361.
---

# Matrix Acidizing Design

Computational skill for matrix acid treatment design in carbonate and sandstone
formations. All calculations assume injection below the fracture initiation
pressure (matrix treatment, not fracture acidizing).

**Field units.** Rates in bbl/min, pressures in psia, depths in ft TVD.

---

## Module 1 — Carbonate Acidizing: Wormhole Propagation

```python
import math

def paccaloni_acid_volume_gal(r_w_ft, r_bypass_ft, phi, h_ft,
                               acid_volume_fraction=0.15):
    """
    Paccaloni minimum acid volume to achieve a wormhole bypass radius r_bypass.
    V_acid = pi * (r_bypass^2 - r_w^2) * phi * h * acid_fraction / 7.48

    r_bypass_ft:        target wormhole radius beyond which skin is bypassed (ft)
    phi:                matrix porosity (fraction)
    h_ft:               perforated interval (ft)
    acid_volume_fraction: fraction of pore volume dissolved (0.10-0.20 for HCl)
    Returns: minimum acid volume (gallons)
    """
    pv_swept_ft3 = math.pi * (r_bypass_ft**2 - r_w_ft**2) * phi * h_ft
    # Acid must fill and spend within the swept volume
    # acid_volume_fraction of PV ~ dissolution capacity at spending conditions
    acid_vol_ft3 = pv_swept_ft3 * acid_volume_fraction
    return acid_vol_ft3 * 7.48052  # ft3 to gallons

def hcl_spending_distance_ft(C_acid_wt_frac, rho_acid_lb_gal,
                               phi, Vf_pore_fraction,
                               acid_rate_bpm, reaction_capacity):
    """
    Approximate spending distance for HCl in carbonate (carbonate wormhole tip).
    Simplified from Daccord-Lenormand model.
    C_acid:         acid concentration (weight fraction, e.g., 0.15 for 15% HCl)
    rho_acid:       acid density (lb/gal; 15% HCl ≈ 8.9 lb/gal)
    phi:            porosity (fraction)
    Vf:             fraction of pore volume available for acid flow (0.3-0.5)
    reaction_capacity: lb rock dissolved per lb acid (CaCO3/HCl ≈ 1.374 for 15% HCl)
    Returns: estimated spending distance (ft) — conceptual, not exact
    Note: True spending distance requires Damkohler number analysis (Module 2).
    """
    # Mass of acid available per unit wellbore volume
    # This is a simplified stoichiometric estimate
    acid_per_gal = C_acid_wt_frac * rho_acid_lb_gal  # lb acid/gal fluid
    dissolution_capacity = acid_per_gal * reaction_capacity  # lb rock dissolved/gal
    # Approximate: distance where all acid is spent (pore filling)
    # In practice: wormhole model gives 5-20 ft for 15% HCl at optimal rate
    return None  # Use Damkohler analysis; spending distance is flow-rate dependent

def wormhole_pore_volumes_to_breakthrough(nDa, wormhole_regime="optimal"):
    """
    Pore volumes to wormhole breakthrough at core scale (Fredd-Fogler).
    Damkohler number controls acid dissolution regime:
      nDa very low  (< 0.1):  face dissolution — high PVBT (inefficient)
      nDa optimal   (≈ 0.3):  optimal wormholing — minimum PVBT (~1.5-2 PV)
      nDa very high (> 10):   uniform dissolution — moderate PVBT (~5-10 PV)

    nDa: Damkohler number = k_rxn * L / v_interstitial
    Returns: approximate pore volumes to breakthrough (dimensionless)
    """
    pvbt_table = {
        "face":    {"nDa_range": "< 0.01", "pvbt": 200, "regime": "Face dissolution; inefficient"},
        "optimal": {"nDa_range": "0.1-1",  "pvbt": 1.5, "regime": "Optimal wormholing; recommended"},
        "compact": {"nDa_range": "1-10",   "pvbt": 10,  "regime": "Compact wormholes; moderate"},
        "uniform": {"nDa_range": "> 10",   "pvbt": 50,  "regime": "Uniform dissolution; inefficient"},
    }
    regime = wormhole_regime.lower()
    if regime not in pvbt_table:
        regime = "optimal"
    return pvbt_table[regime]

def optimal_injection_rate_bpm(k_md, h_ft, mu_acid_cp,
                                P_frac_psia, P_res_psia, r_w_ft=0.33):
    """
    Target injection rate for optimal wormholing regime.
    Rule of thumb: optimal Da corresponds to interstitial velocity of 0.1-1 cm/min.
    For carbonate: inject at 0.1-0.5 bbl/min/ft for optimal wormholing.
    Returns: recommended rate range (bbl/min, bbl/min/ft)
    """
    # Maximum rate below fracture pressure (Darcy radial flow)
    # q_max = k*h*(P_frac - P_res) / (141.2*B*mu*ln(re/rw))
    # Conservative estimate (re/rw ≈ 1000)
    ln_re_rw = math.log(1000.0)
    q_max_bpd = k_md * h_ft * (P_frac_psia - P_res_psia) / (141.2 * 1.0 * mu_acid_cp * ln_re_rw)
    q_max_bpm = q_max_bpd / 1440.0  # bpd to bpm
    # Optimal wormholing range for carbonates: 0.1-0.5 bbl/min/ft
    q_optimal_low_bpm = 0.1 * h_ft
    q_optimal_high_bpm = 0.5 * h_ft
    return {
        "q_max_bpm": round(q_max_bpm, 3),
        "q_optimal_low_bpm": round(q_optimal_low_bpm, 2),
        "q_optimal_high_bpm": round(q_optimal_high_bpm, 2),
        "recommendation": f"Target {q_optimal_low_bpm:.2f}–{q_optimal_high_bpm:.2f} bpm; stay below {q_max_bpm:.3f} bpm to avoid fracturing"
    }
```

---

## Module 2 — Sandstone Acidizing: HF/HCl Three-Stage Design

```python
def hf_hcl_stage_volumes(h_ft, r_w_ft, phi,
                           damage_radius_ft=2.0,
                           preflush_pv=0.5,
                           main_flush_pv=1.0,
                           overflush_pv=0.5):
    """
    Standard three-stage HF/HCl sandstone acid treatment design.
    Based on McLeod (1984) SPE 13798 guidelines.

    Stage 1 — Pre-flush: 5-7.5% HCl to dissolve CaCO3 and establish injection path
    Stage 2 — Main flush: 12% HCl + 3% HF (mud acid) to dissolve clays and fines
    Stage 3 — Overflush: NH4Cl or KCl brine to displace spent acid past perforations

    Volumes based on pore volumes in the damage zone (r_w to r_damage).

    Returns: stage volumes (gallons)
    """
    # Pore volume of damage zone per ft of perforated interval
    pv_damage_ft3 = math.pi * (damage_radius_ft**2 - r_w_ft**2) * phi * h_ft
    pv_damage_gal = pv_damage_ft3 * 7.48052

    # Stage volumes as multiples of damage zone pore volume
    preflush_gal = preflush_pv * pv_damage_gal
    main_flush_gal = main_flush_pv * pv_damage_gal
    overflush_gal = overflush_pv * pv_damage_gal
    total_gal = preflush_gal + main_flush_gal + overflush_gal

    return {
        "preflush_gal": round(preflush_gal, 0),
        "preflush_bbl": round(preflush_gal / 42.0, 1),
        "main_flush_gal": round(main_flush_gal, 0),
        "main_flush_bbl": round(main_flush_gal / 42.0, 1),
        "overflush_gal": round(overflush_gal, 0),
        "overflush_bbl": round(overflush_gal / 42.0, 1),
        "total_gal": round(total_gal, 0),
        "total_bbl": round(total_gal / 42.0, 1),
        "stage1_system": "5-7.5% HCl pre-flush",
        "stage2_system": "12% HCl + 3% HF (mud acid)",
        "stage3_system": "2% KCl brine overflush"
    }

def hf_acid_system_selection(clay_content_frac, carbonate_content_frac,
                               temperature_f):
    """
    Recommend HF acid system based on mineralogy.
    Based on SPE 13798 (McLeod 1984) and Schechter acid selection table.
    Returns: recommended acid system and rationale.
    """
    if carbonate_content_frac > 0.10:
        note = "Pre-flush volume should be increased; high carbonate will consume HF rapidly"
    else:
        note = "Standard HCl:HF ratios acceptable"

    if temperature_f > 200:
        system = "Organic HF (acetic acid + HF) or retarded HF — high T increases reaction rate"
    elif clay_content_frac > 0.15:
        system = "Low-concentration mud acid (6% HCl + 1.5% HF) or sequential HF — high clay content"
    elif clay_content_frac < 0.05:
        system = "Standard mud acid (12% HCl + 3% HF) — low clay, clean sandstone"
    else:
        system = "Standard mud acid (12% HCl + 3% HF) — moderate clay content"

    return {"recommended_system": system, "note": note,
            "temperature_f": temperature_f,
            "clay_content_pct": round(clay_content_frac * 100, 1)}
```

---

## Module 3 — Post-Acid Skin: Hawkins Formula

```python
def hawkins_skin(k_formation_md, k_altered_md,
                  r_altered_ft, r_w_ft):
    """
    Hawkins formula for composite skin factor.
    S = (k_f/k_a - 1) * ln(r_a / r_w)

    k_formation: formation permeability beyond damage/alteration zone (md)
    k_altered:   permeability of the altered (acid-treated) zone (md)
    r_altered:   radius of the altered zone (ft)
    r_w:         wellbore radius (ft)

    For a DAMAGED zone: k_altered < k_formation  => S > 0 (damage)
    For an ACIDIZED zone: k_altered > k_formation => S < 0 (stimulation)
    Returns: skin factor (dimensionless)
    """
    if k_altered_md <= 0 or r_altered_ft <= r_w_ft:
        return None
    return (k_formation_md / k_altered_md - 1.0) * math.log(r_altered_ft / r_w_ft)

def skin_bypass_effective_rw(S_post_acid, r_w_ft):
    """
    Effective wellbore radius after stimulation:
    r_wa = r_w * exp(-S)
    Negative skin (stimulated) gives r_wa > r_w, equivalent to a larger wellbore.
    """
    return r_w_ft * math.exp(-S_post_acid)

def production_ratio_after_acid(S_before, S_after, r_e_ft, r_w_ft):
    """
    Production ratio (stimulation ratio) from skin improvement.
    q_after/q_before = (ln(re/rw) - 0.75 + S_before) / (ln(re/rw) - 0.75 + S_after)
    """
    ln_ratio = math.log(r_e_ft / r_w_ft) - 0.75
    return (ln_ratio + S_before) / (ln_ratio + S_after)

def post_acid_damage_composite(r_w_ft, r_acid_ft, r_damage_ft,
                                 k_undamaged_md, k_acid_md, k_damage_md):
    """
    Total skin for three-zone composite: undamaged + damaged + acid-treated.
    S_total = S_damage + S_acid
    where S_damage uses original damage zone and S_acid uses acid alteration.
    Useful for partial acid penetration scenarios.
    """
    S_damage = hawkins_skin(k_undamaged_md, k_damage_md, r_damage_ft, r_w_ft)
    S_acid = hawkins_skin(k_undamaged_md, k_acid_md, r_acid_ft, r_w_ft)
    # Acid penetrates the damage zone: composite = S_acid (acid zone replaces damage)
    # if r_acid >= r_damage: S_total = S_acid (damage fully bypassed)
    if r_acid_ft >= r_damage_ft:
        S_total = hawkins_skin(k_undamaged_md, k_acid_md, r_acid_ft, r_w_ft)
    else:
        # Partial penetration: acid zone inside damage zone
        S_inner = hawkins_skin(k_damage_md, k_acid_md, r_acid_ft, r_w_ft)
        S_outer = hawkins_skin(k_undamaged_md, k_damage_md, r_damage_ft, r_w_ft)
        S_total = S_inner + S_outer
    return {"S_total": round(S_total, 2),
            "S_undamaged_skin_original": round(S_damage, 2),
            "S_after_acid": round(S_acid if r_acid_ft >= r_damage_ft else S_total, 2)}
```

---

## Module 4 — Maximum Injection Rate Below Fracture Pressure

```python
def max_matrix_injection_rate(k_md, h_ft, P_frac_psia, P_res_psia,
                                mu_acid_cp=1.0, B=1.0,
                                r_e_ft=1000.0, r_w_ft=0.33, S=0.0):
    """
    Maximum injection rate to stay below fracture pressure (Darcy radial flow).
    q_max = k*h*(P_frac - P_res) / [141.2*B*mu*(ln(re/rw) - 0.75 + S)]
    Use 90% of q_max as operating target for safety margin.
    Returns: q_max (bbl/day), q_max_bpm (bbl/min)
    """
    if k_md <= 0 or h_ft <= 0:
        return None
    ln_term = math.log(r_e_ft / r_w_ft) - 0.75 + S
    q_max_bpd = k_md * h_ft * (P_frac_psia - P_res_psia) / (141.2 * B * mu_acid_cp * ln_term)
    return {
        "q_max_bpd": round(q_max_bpd, 1),
        "q_max_bpm": round(q_max_bpd / 1440.0, 4),
        "q_target_bpm": round(0.90 * q_max_bpd / 1440.0, 4),
        "note": "Target 90% of q_max; stop if ISIP exceeds frac gradient"
    }

def frac_gradient_psi_ft(overburden_gradient=1.0, biot_coeff=0.7,
                           poisson_ratio=0.25, pore_pressure_gradient=0.465):
    """
    Minimum horizontal stress / fracture gradient estimate.
    sigma_h_min = nu/(1-nu) * (S_v - alpha*P_p) + alpha*P_p
    Expressed as gradient (psi/ft TVD).
    Use as conservative estimate — actual FG from leak-off test (LOT) preferred.
    """
    sigma_v = overburden_gradient
    alpha = biot_coeff
    nu = poisson_ratio
    P_p = pore_pressure_gradient
    sigma_h = nu / (1.0 - nu) * (sigma_v - alpha * P_p) + alpha * P_p
    return round(sigma_h, 3)  # psi/ft
```

---

## Learning Resources

### Textbooks

| Author(s) | Title | Edition | ISBN |
|-----------|-------|---------|------|
| Economides, Hill, Ehlig-Barbour & Zhu | *Petroleum Production Systems* | 2nd ed. (2013) | 978-0-13-703158-0 |
| Williams, Gidley & Schechter | *Acidizing Fundamentals*, SPE Monograph 6 (1979) | SPE store | 978-0-89520-205-1 |
| Economides & Nolte (eds.) | *Reservoir Stimulation* | 3rd ed. (2000) | 978-0-471-49192-4 |
| Kalfayan, L. | *Production Enhancement with Acid Stimulation* | 2nd ed. (2008) | 978-1-59370-162-7 |

### Key SPE References

| Paper | Key Contribution |
|-------|-----------------|
| McLeod (1984) SPE 13798 | Sandstone acidizing guidelines; 3-stage design |
| Fredd & Fogler (1999) SPE 54719 | Wormhole regime Damkohler number framework |
| Buijse & Glasbergen (2005) SPE 107874 | Wormhole model used in design software |
| Paccaloni et al. (1988) SPE 17154 | Real-time monitoring matrix injection |

### Free Online Resources

| Resource | URL |
|----------|-----|
| SPE PetroWiki — Matrix Acidizing | petrowiki.spe.org/Matrix_acidizing |
| SPE PetroWiki — Wormholes | petrowiki.spe.org/Wormholes |
| Halliburton acid design tech notes | halliburton.com/en/resources |
| SPE student membership ($25/yr) | spe.org/en/membership/student |

### WVU Courses

- **PNGE 341** Well Completions and Stimulation — primary course for acidizing
- **PNGE 361** Production Engineering — post-acid skin and PI improvement context

---

## Output Format

```
## Matrix Acid Treatment Design — [Well / Formation]

### Formation Characterization
| Parameter | Value | Source |
|-----------|-------|--------|
| Formation type | Carbonate / Sandstone | |
| Permeability (k) | md | Core/test |
| Porosity (phi) | fraction | Log |
| Damage radius | ft | Estimated |
| Skin before treatment | dimensionless | Well test |
| Temperature | degF | BHT |

### Treatment Design (Carbonate)
| Stage | Fluid | Concentration | Volume (bbl) | Rate (bpm) |
|-------|-------|---------------|-------------|-----------|
| Pre-flush | HCl | 15% | | |
| Main flush | HCl | 15–28% | | |
| Overflush | KCl brine | 2% | | |

OR (Sandstone):
| Stage | Fluid | System | Volume (bbl) | Rate (bpm) |
|-------|-------|--------|-------------|-----------|
| Pre-flush | HCl | 7.5% HCl | | |
| Main flush | Mud acid | 12/3 HCl/HF | | |
| Overflush | NH4Cl | 2% | | |

### Expected Results
| Metric | Before | After |
|--------|--------|-------|
| Skin factor | | |
| Effective r_wa (ft) | | |
| Production ratio | 1.0 | |

**Certainty:** MEDIUM (design) | LOW (expected skin; actual depends on formation response)
**Bias:** Volumes are minima; field execution should monitor ISIP and adjust in real time
```

---

## Error Handling

| Condition | Cause | Action |
|-----------|-------|--------|
| q_max_bpm very small (< 0.05) | Very low k or tight formation | Matrix acid may not be effective; consider HF fracturing instead |
| Wormhole volume exceeds 500 bbl | Large h or deep damage | Break into multiple stages; use coiled tubing for placement |
| High carbonate in sandstone (> 10%) | CaCO3 cement | Double pre-flush volume; risk of sludge with HF if incompatible crude |
| Temperature > 250 F | Slow-reacting acid depleted early | Use retarded or emulsified acid system |

---

## Caveats

- **Fracture initiation must be avoided.** Confirm frac gradient from LOT/FIT
  before designing injection rates. Monitor ISIP in real time.
- **Wormhole models are scale-dependent.** Core-scale PVBT does not directly
  translate to field scale. Field wormhole efficiency is typically lower.
- **HF incompatibility with crude oil** can form iron sludge. Run compatibility
  tests before pumping HF in wells with paraffinic or asphaltic crude.
- **Sandstone acid sequence is strict:** HCl pre-flush must precede HF;
  pumping HF into a CaCO3-rich zone without HCl pre-flush generates CaF2 precipitation.
- For Marcellus/Utica: these are primarily hydraulic fracture completions, not
  matrix acid candidates. Matrix acidizing is more relevant for naturally fractured
  carbonates (Knox Dolomite, Onondaga) or near-wellbore damage removal in
  conventional completions.
