---
name: aqueous-chemistry-electrochem
description: >
  Solve aqueous chemistry and electrochemistry problems relevant to chemical,
  petroleum, and environmental engineering including pH and pOH, buffers,
  alkalinity and hardness conversions, ionic strength, solubility and
  precipitation screening, Nernst equation, electrochemical cell potentials,
  Faraday law, and corrosion-cell fundamentals. Use when the user asks about
  pH, buffering, acid-base speciation, alkalinity as CaCO3, hardness,
  precipitation risk, redox potential, electrolysis, galvanic cells, or
  electrochemical corrosion. Trigger phrases include aqueous chemistry,
  electrochemistry, pH, alkalinity, hardness, Nernst, Faraday, buffer,
  precipitation, ionic strength, or corrosion cell.
---

# Aqueous Chemistry And Electrochemistry

Tutor skill for water chemistry, acid-base systems, redox, and electrochemical
calculations. Useful for produced-water treatment, corrosion reasoning, and
core chemical engineering coursework.

---

## Module 1 - pH, pOH, And Buffers

```python
def ph_from_h(h_mol_L):
    """pH from hydrogen ion concentration."""
    import math
    if h_mol_L <= 0:
        return None
    return -math.log10(h_mol_L)

def poh_from_oh(oh_mol_L):
    """pOH from hydroxide concentration."""
    import math
    if oh_mol_L <= 0:
        return None
    return -math.log10(oh_mol_L)

def henderson_hasselbalch(pka, acid_conc, base_conc):
    """Buffer relation for conjugate acid/base pair."""
    import math
    if acid_conc <= 0 or base_conc <= 0:
        return None
    return pka + math.log10(base_conc / acid_conc)
```

---

## Module 2 - Alkalinity, Hardness, And Ionic Strength

```python
def mgL_as_caco3(concentration_mgL, equivalent_weight):
    """
    Convert mg/L of species to mg/L as CaCO3.
    """
    if equivalent_weight <= 0:
        return None
    return concentration_mgL * 50.0 / equivalent_weight

def ionic_strength(concentrations_mol_L, charges):
    """
    I = 0.5 * sum(c_i * z_i^2)
    """
    if len(concentrations_mol_L) != len(charges):
        return None
    return 0.5 * sum(c * z**2 for c, z in zip(concentrations_mol_L, charges))
```

**Common equivalent weights**

| Species | Eq. wt. |
|--------|---------|
| Ca2+ | 20.04 |
| Mg2+ | 12.15 |
| HCO3- | 61.0 |
| CO3 2- | 30.0 |

---

## Module 3 - Redox And Electrochemistry

```python
def nernst_potential(E0_V, n_electrons, oxidized_activity, reduced_activity,
                     temperature_K=298.15):
    """
    Nernst equation:
    E = E0 - (RT/nF) ln(Q)
    For Ox + ne- -> Red, Q = a_red / a_ox
    """
    import math
    R = 8.314
    F = 96485.0
    if n_electrons <= 0 or oxidized_activity <= 0 or reduced_activity <= 0:
        return None
    q = reduced_activity / oxidized_activity
    return E0_V - (R * temperature_K / (n_electrons * F)) * math.log(q)

def faraday_mass_deposited(current_A, time_s, molar_mass_g_mol,
                           n_electrons, efficiency=1.0):
    """
    Faraday's law:
    m = I t M eta / (n F)
    """
    F = 96485.0
    if n_electrons <= 0:
        return None
    return current_A * time_s * molar_mass_g_mol * efficiency / (n_electrons * F)
```

---

## Module 4 - Screening Logic

| Problem | What to compute first |
|--------|------------------------|
| Buffer or titration question | Henderson-Hasselbalch or charge balance |
| Scaling or precipitation screen | pH, alkalinity, hardness, ionic strength |
| Electrolysis / plating | Faraday law |
| Corrosion-cell potential | Nernst equation and half-reaction direction |
| Produced-water treatment chemistry | Speciation basis, ionic strength, and CaCO3 conversion |

---

## Output Format

When using this skill, structure the answer as:

1. Species and reaction basis
2. Assumptions about equilibrium or ideality
3. Equation setup
4. Numerical result
5. Interpretation in physical or process terms

---

## Learning Resources

| Resource | Notes |
|---------|-------|
| Sawyer, McCarty, Parkin | Water chemistry / treatment classic |
| Bard and Faulkner | Electrochemistry reference |
| OpenStax Chemistry | Good acid-base and electrochem refreshers |
