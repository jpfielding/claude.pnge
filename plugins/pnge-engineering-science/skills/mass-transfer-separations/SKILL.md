---
name: mass-transfer-separations
description: >
  Solve mass-transfer and separation-process problems including molecular
  diffusion, convective mass transfer, absorption and stripping, packed tower
  HTU and NTU methods, distillation stage estimates, extraction, and film
  theory. Use when the user asks about Fick law, diffusion flux, Sherwood
  number, mass-transfer coefficient, absorber sizing, HTU/NTU, stripping
  factor, distillation stages, relative volatility, or separation-process
  design. Trigger phrases include mass transfer, separations, diffusion,
  absorption, stripping, packed tower, distillation, Fenske, HTU, NTU,
  kLa, or film theory.
---

# Mass Transfer And Separations

Engineering-science skill for transport-driven separation problems. It is aimed
at tutoring and first-pass design calculations rather than full process
simulation.

**Units:** SI by default. Keep concentration basis explicit: mole fraction,
partial pressure, mol/m3, or mass fraction.

---

## Module 1 - Diffusion

```python
def fick_flux_1d(diffusivity_m2_s, c1, c2, length_m):
    """
    Fick's first law in 1D:
    N_A = -D * dc/dz
    Returns positive flux from point 1 to point 2 when c1 > c2.
    """
    if length_m <= 0:
        return None
    return diffusivity_m2_s * (c1 - c2) / length_m

def characteristic_diffusion_time(length_m, diffusivity_m2_s):
    """Order-of-magnitude diffusion time scale."""
    if diffusivity_m2_s <= 0:
        return None
    return length_m**2 / diffusivity_m2_s
```

---

## Module 2 - Convective Mass Transfer

```python
def sherwood_number(k_m_s, length_m, diffusivity_m2_s):
    """Sherwood number."""
    if diffusivity_m2_s <= 0:
        return None
    return k_m_s * length_m / diffusivity_m2_s

def mass_transfer_flux(k_overall, area_m2, driving_force):
    """
    Overall mass-transfer rate.
    Rate = K * A * driving force
    Driving force must match the coefficient basis.
    """
    return k_overall * area_m2 * driving_force

def volumetric_mass_transfer_rate(kla_s_inv, volume_m3, c_star, c_bulk):
    """
    Gas-liquid transfer rate with kLa.
    """
    return kla_s_inv * volume_m3 * (c_star - c_bulk)
```

---

## Module 3 - Packed Towers

```python
def htu_ntu_height(htu_m, ntu):
    """Packed height from transfer units."""
    return htu_m * ntu

def absorption_factor(L_over_mV):
    """
    Absorption factor A = L / (m V)
    A > 1 generally favors absorption.
    """
    return L_over_mV

def stripping_factor(mV_over_L):
    """
    Stripping factor S = m V / L
    S > 1 generally favors stripping.
    """
    return mV_over_L
```

**Interpretation**

| Metric | Meaning |
|-------|---------|
| Large HTU | Poor mass-transfer efficiency |
| Large NTU | Difficult separation or tight outlet spec |
| `A > 1` | Absorption usually feasible |
| `S > 1` | Stripping usually feasible |

---

## Module 4 - Distillation Screening

```python
def fenske_min_stages(xd_light, xb_light, alpha_avg):
    """
    Minimum equilibrium stages at total reflux for binary distillation.
    """
    import math
    numerator = xd_light / (1.0 - xd_light)
    denominator = xb_light / (1.0 - xb_light)
    if alpha_avg <= 1.0 or denominator <= 0:
        return None
    return math.log(numerator / denominator) / math.log(alpha_avg)

def relative_volatility(k_light, k_heavy):
    """Relative volatility alpha = K_light / K_heavy."""
    if k_heavy == 0:
        return None
    return k_light / k_heavy
```

Use Fenske for a lower bound only. Actual stages require reflux and efficiency
considerations.

---

## Module 5 - Process Selection Logic

| Problem | Likely separation route |
|--------|--------------------------|
| Remove dissolved gas from liquid | Stripping / flash |
| Remove acid gas from gas stream | Absorption |
| Split close-boiling liquids | Distillation if relative volatility allows |
| Recover dilute solute from liquid | Extraction, adsorption, or membranes |
| Slow species transport through stagnant film | Diffusion-limited process |

---

## Output Format

When using this skill, structure the answer as:

1. Separation target and basis
2. Governing transfer mechanism
3. Equations used and coefficient basis
4. Calculated stages, height, flux, or rate
5. Whether the process looks transfer-limited or equilibrium-limited

---

## Learning Resources

| Resource | Notes |
|---------|-------|
| Geankoplis | Standard transport and separation reference |
| Treybal | Strong absorption / extraction treatment |
| Wankat | Good distillation and separations text |
| LearnChemE separations content | Short worked examples |
