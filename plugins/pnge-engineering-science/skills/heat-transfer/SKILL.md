---
name: heat-transfer
description: >
  Solve engineering heat-transfer problems involving conduction, convection,
  radiation screening, overall heat-transfer coefficients, heat exchangers,
  transient cooling or heating, and boiling or condensation approximations.
  Use when the user asks about Fourier law, Newton cooling, thermal
  resistance, U-value, LMTD, NTU-effectiveness, fin heat loss, transient
  temperature response, or heat duty estimation. Trigger phrases include heat
  transfer, conduction, convection, heat exchanger, LMTD, NTU, overall U,
  thermal resistance, cooling time, heating time, fin efficiency, or Biot
  number.
---

# Heat Transfer

Engineering-science skill for conduction, convection, and heat exchanger
calculations. Built for chemical and petroleum engineering tutoring, equipment
screening, and sanity checks on thermal problems.

**Units:** SI by default. Use K, W, m, s, kg unless the user specifies field
units.

---

## Module 1 - Conduction

```python
def conduction_plane_wall_q(k_W_mK, area_m2, delta_T_K, thickness_m):
    """
    Fourier law for 1D steady conduction through a plane wall.
    q = k A dT / L
    """
    if thickness_m <= 0:
        return None
    return k_W_mK * area_m2 * delta_T_K / thickness_m

def conduction_cylinder_q(k_W_mK, length_m, t_inner_K, t_outer_K,
                          r_inner_m, r_outer_m):
    """
    Radial conduction through a cylinder.
    q = 2*pi*k*L*(Ti-To) / ln(ro/ri)
    """
    import math
    if r_outer_m <= r_inner_m or r_inner_m <= 0:
        return None
    return (2.0 * math.pi * k_W_mK * length_m * (t_inner_K - t_outer_K) /
            math.log(r_outer_m / r_inner_m))

def thermal_resistance_plane(thickness_m, k_W_mK, area_m2):
    """Conduction resistance for a plane wall."""
    if k_W_mK <= 0 or area_m2 <= 0:
        return None
    return thickness_m / (k_W_mK * area_m2)
```

---

## Module 2 - Convection And Overall U

```python
def convection_q(h_W_m2K, area_m2, delta_T_K):
    """
    Newton's law of cooling.
    q = h A dT
    """
    return h_W_m2K * area_m2 * delta_T_K

def convective_resistance(h_W_m2K, area_m2):
    """Convective thermal resistance."""
    if h_W_m2K <= 0 or area_m2 <= 0:
        return None
    return 1.0 / (h_W_m2K * area_m2)

def overall_u_from_resistances(resistances_m2K_W):
    """
    Overall heat-transfer coefficient from resistances on a common area basis.
    U = 1 / sum(R)
    """
    r_total = sum(resistances_m2K_W)
    if r_total <= 0:
        return None
    return 1.0 / r_total
```

**Typical scales**

| Service | Typical h range |
|--------|------------------|
| Free convection gas | 5 to 25 W/m2-K |
| Forced convection liquid | 100 to 5,000 W/m2-K |
| Condensation | 1,000 to 20,000 W/m2-K |
| Boiling | 2,500 to 100,000 W/m2-K |

---

## Module 3 - Heat Exchangers

```python
def lmtd(delta_t1_K, delta_t2_K):
    """
    Log-mean temperature difference.
    """
    import math
    if delta_t1_K <= 0 or delta_t2_K <= 0:
        return None
    if abs(delta_t1_K - delta_t2_K) < 1e-12:
        return delta_t1_K
    return (delta_t1_K - delta_t2_K) / math.log(delta_t1_K / delta_t2_K)

def heat_exchanger_duty(U_W_m2K, area_m2, lmtd_K, correction_factor=1.0):
    """
    Heat exchanger duty.
    q = U A F LMTD
    """
    return U_W_m2K * area_m2 * correction_factor * lmtd_K

def epsilon_ntu_effectiveness(ntu, c_r, flow="counter"):
    """
    Effectiveness for simple counterflow or parallel-flow exchangers.
    """
    import math
    if flow == "parallel":
        return (1.0 - math.exp(-ntu * (1.0 + c_r))) / (1.0 + c_r)
    # counterflow
    if abs(1.0 - c_r) < 1e-12:
        return ntu / (1.0 + ntu)
    return ((1.0 - math.exp(-ntu * (1.0 - c_r))) /
            (1.0 - c_r * math.exp(-ntu * (1.0 - c_r))))
```

---

## Module 4 - Transient Heating And Cooling

```python
def biot_number(h_W_m2K, l_c_m, k_W_mK):
    """Biot number for lumped-capacitance screening."""
    if k_W_mK <= 0:
        return None
    return h_W_m2K * l_c_m / k_W_mK

def lumped_temperature(T_inf, T_initial, h_W_m2K, area_m2,
                       rho_kg_m3, volume_m3, cp_J_kgK, time_s):
    """
    Lumped capacitance temperature response.
    Valid when Bi < 0.1.
    """
    import math
    tau = rho_kg_m3 * volume_m3 * cp_J_kgK / (h_W_m2K * area_m2)
    return T_inf + (T_initial - T_inf) * math.exp(-time_s / tau)
```

**Interpretation**

- `Bi < 0.1`: lumped model usually acceptable
- Large `Bi`: internal gradients matter; do not use lumped capacitance

---

## Output Format

When using this skill, structure the answer as:

1. System and assumptions
2. Governing heat-transfer mode(s)
3. Equations and unit basis
4. Numerical result
5. Physical reasonableness check

---

## Learning Resources

| Resource | Notes |
|---------|-------|
| Incropera, DeWitt, Bergman, Lavine | Standard heat transfer text |
| LearnChemE heat transfer playlist | Worked ChBE-style examples |
| MIT OCW heat transfer notes | Good derivations and dimensionless groups |
