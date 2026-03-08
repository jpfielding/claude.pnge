---
name: reaction-engineering
description: >
  Chemical reactor design for ideal reactors including CSTR, PFR, and batch
  reactor. Implements design equations for conversion vs. volume, CSTR space
  time, PFR Levenspiel plot area, Arrhenius rate constant temperature
  dependence, Damkohler number, CSTR in series conversion, adiabatic
  temperature rise, and equilibrium conversion. Use when the user asks about
  CSTR reactor design, PFR sizing, batch reactor time, conversion calculation,
  space time or space velocity, Damkohler number, Arrhenius equation, rate law,
  Levenspiel plot, CSTR in series, adiabatic temperature rise, equilibrium
  conversion, second-order reaction design, or any chemical reactor sizing or
  conversion problem. Resources: Fogler Elements of Chemical Reaction
  Engineering 6th ed free at umich.edu/~elements/6e; Levenspiel Chemical
  Reaction Engineering 3rd ed ISBN 978-0-471-25424-9; LearnChemE YouTube
  CRE playlist; MIT OCW 10.37. Primary courses: ChBE 321 Chemical Reaction
  Engineering.
---

# Chemical Reaction Engineering Calculator

Computational skill for ideal reactor design and kinetic analysis.
Covers CSTR, PFR, and batch reactor mole balance design equations with
rate law, temperature effects, and multiple reactor configurations.

**Sign convention:** For A → products, F_A0 = molar feed rate of A (mol/s),
C_A0 = inlet concentration (mol/L), X = conversion (0 to 1), -r_A = rate of
disappearance of A (mol/L/s, always positive).

---

## Module 1 — Rate Law and Arrhenius Equation

```python
import math

def power_law_rate(k, C_A, n_A, C_B=1.0, n_B=0.0):
    """
    Power law rate expression: -r_A = k * C_A^n_A * C_B^n_B
    k:   rate constant (units depend on order: for 1st order, 1/s; 2nd order, L/mol/s)
    C_A: concentration of species A (mol/L)
    n_A: reaction order with respect to A
    C_B: concentration of B (mol/L); default 1.0 for single-species reactions
    n_B: reaction order with respect to B
    Returns: rate of disappearance of A (mol/L/s)
    """
    if C_A < 0 or C_B < 0:
        return 0.0
    return k * (C_A**n_A) * (C_B**n_B)

def arrhenius_k(A_pre, Ea_J_mol, T_K):
    """
    Arrhenius equation: k(T) = A * exp(-Ea / (R*T))
    A_pre:    pre-exponential factor (same units as k)
    Ea_J_mol: activation energy (J/mol)
    T_K:      temperature (Kelvin)
    R = 8.314 J/mol/K
    Returns: rate constant k at temperature T
    """
    R = 8.314
    return A_pre * math.exp(-Ea_J_mol / (R * T_K))

def rate_ratio_temperatures(k_T1, T1_K, T2_K, Ea_J_mol):
    """
    Rate ratio between two temperatures using Arrhenius:
    k(T2)/k(T1) = exp(-Ea/R * (1/T2 - 1/T1))
    Returns: k_T2 and ratio k_T2/k_T1
    """
    R = 8.314
    ratio = math.exp(-Ea_J_mol / R * (1.0/T2_K - 1.0/T1_K))
    return {"k_T2": k_T1 * ratio, "ratio_k2_k1": round(ratio, 4)}

def activation_energy_from_two_points(k1, T1_K, k2, T2_K):
    """
    Estimate Ea from two rate constants at two temperatures:
    Ea = -R * ln(k2/k1) / (1/T2 - 1/T1)
    """
    R = 8.314
    if k1 <= 0 or k2 <= 0:
        return None
    ln_ratio = math.log(k2 / k1)
    inv_T_diff = 1.0/T2_K - 1.0/T1_K
    if abs(inv_T_diff) < 1e-12:
        return None
    Ea = -R * ln_ratio / inv_T_diff
    return {"Ea_J_mol": round(Ea, 1), "Ea_kJ_mol": round(Ea/1000, 3)}
```

---

## Module 2 — Ideal Reactor Design Equations

```python
def cstr_volume(F_A0_mol_s, X, neg_r_A_exit_mol_L_s, C_A0=None):
    """
    CSTR mole balance (perfectly mixed):
    V = F_A0 * X / (-r_A_exit)    [liters if F_A0 in mol/s and r_A in mol/L/s]
    F_A0:      molar feed rate of A (mol/s)
    X:         desired conversion (0-1)
    neg_r_A_exit: rate of disappearance at EXIT conditions (mol/L/s)
    Returns: CSTR volume (L) and space time tau (s) if C_A0 given
    """
    if neg_r_A_exit <= 0:
        return None
    V_L = F_A0_mol_s * X / neg_r_A_exit
    result = {"V_liters": round(V_L, 4), "V_m3": round(V_L / 1000.0, 6)}
    if C_A0 is not None and C_A0 > 0:
        v0 = F_A0_mol_s / C_A0  # volumetric flow rate (L/s)
        tau = V_L / v0  # space time (s)
        result["tau_s"] = round(tau, 4)
        result["space_velocity_1_s"] = round(1.0/tau, 6) if tau > 0 else None
    return result

def pfr_volume_numerical(F_A0_mol_s, X_target, rate_function,
                          C_A0_mol_L, n_steps=200):
    """
    PFR mole balance (plug flow):
    V = F_A0 * integral(dX / (-r_A(X))) from 0 to X_target
    Evaluated numerically using trapezoidal integration (Levenspiel plot area).
    rate_function: callable f(X) -> (-r_A) at conversion X; must handle X in [0, X_target]
    Returns: PFR volume (L)
    """
    dX = X_target / n_steps
    total = 0.0
    for i in range(n_steps):
        X1 = i * dX
        X2 = (i + 1) * dX
        r1 = rate_function(X1)
        r2 = rate_function(X2)
        if r1 <= 0 or r2 <= 0:
            break
        total += 0.5 * (1.0/r1 + 1.0/r2) * dX  # trapezoidal
    V_L = F_A0_mol_s * total
    return {"V_liters": round(V_L, 4), "V_m3": round(V_L/1000.0, 6)}

def batch_time(C_A0_mol_L, X_target, rate_function, n_steps=200):
    """
    Batch reactor design equation:
    t = C_A0 * integral(dX / (-r_A(X))) from 0 to X_target
    Same Levenspiel integral as PFR but gives time (s) rather than volume.
    rate_function: callable f(X) -> (-r_A) in mol/L/s
    Returns: batch reaction time (s)
    """
    dX = X_target / n_steps
    total = 0.0
    for i in range(n_steps):
        X1 = i * dX
        X2 = (i + 1) * dX
        r1 = rate_function(X1)
        r2 = rate_function(X2)
        if r1 <= 0 or r2 <= 0:
            break
        total += 0.5 * (1.0/r1 + 1.0/r2) * dX
    return {"t_s": round(C_A0_mol_L * total, 4),
            "t_min": round(C_A0_mol_L * total / 60.0, 4)}

def pfr_vs_cstr_comparison(F_A0, X, rate_function, C_A0):
    """
    Compare PFR and CSTR volumes for the same conversion.
    PFR is always smaller or equal to CSTR for a single monotonically decreasing rate.
    """
    # CSTR uses exit rate
    r_exit = rate_function(X)
    V_cstr = cstr_volume(F_A0, X, r_exit, C_A0)
    V_pfr = pfr_volume_numerical(F_A0, X, rate_function, C_A0)
    if V_cstr and V_pfr:
        ratio = V_cstr["V_liters"] / V_pfr["V_liters"] if V_pfr["V_liters"] > 0 else None
        return {"V_pfr_L": V_pfr["V_liters"], "V_cstr_L": V_cstr["V_liters"],
                "V_cstr_over_V_pfr": round(ratio, 3) if ratio else None,
                "note": "CSTR larger for positive-order reactions with decreasing rate"}
    return None
```

---

## Module 3 — Multiple Reactors and CSTR in Series

```python
def cstr_series_conversion_1st_order(n, k, tau_each):
    """
    Conversion from n equal CSTRs in series (1st order, A -> products):
    X_n = 1 - 1/(1 + k*tau)^n
    k:       first-order rate constant (1/s)
    tau_each: space time of EACH CSTR (s)
    Returns: overall conversion and individual stage conversions
    """
    stages = []
    C_ratio = 1.0  # C_A / C_A0 exiting each stage
    for i in range(1, n + 1):
        C_ratio = C_ratio / (1.0 + k * tau_each)
        X_i = 1.0 - C_ratio
        stages.append({"stage": i, "X": round(X_i, 5), "C_A_over_C_A0": round(C_ratio, 5)})
    return {"stages": stages, "X_final": round(stages[-1]["X"], 5),
            "note": f"{n} CSTRs approach PFR performance as n increases"}

def damkohler_number(k, tau, order=1):
    """
    Damkohler number for CSTR: Da = k * tau  (1st order: Da = k*tau)
    For nth order: Da = k * C_A0^(n-1) * tau
    Da < 1: kinetics-limited (low conversion per reactor)
    Da >> 1: equilibrium-limited (high conversion possible)
    Returns: Da value and interpretation
    """
    Da = k * tau
    if Da < 0.1:
        interp = "Kinetics-limited: low conversion per reactor; use larger tau or T"
    elif Da < 10:
        interp = "Moderate Da: good operating range for process design"
    else:
        interp = "Large Da: reaction nearly complete; may be mass-transfer limited"
    return {"Da": round(Da, 4), "interpretation": interp}

def levenspiel_plot_points(X_values, rate_values):
    """
    Generate Levenspiel plot data: 1/(-r_A) vs. X
    Area under curve = PFR volume parameter (integral F_A0 * dX / (-r_A))
    Lowest point on curve = optimal CSTR operating point.
    X_values:    list of conversion values (0 to X_max)
    rate_values: list of corresponding (-r_A) values (mol/L/s)
    Returns: list of (X, 1/r_A) pairs for plotting
    """
    return [(X, 1.0/r if r > 0 else None) for X, r in zip(X_values, rate_values)]
```

---

## Module 4 — Temperature Effects

```python
def adiabatic_temperature_rise(X, delta_H_rxn_J_mol,
                                 C_A0_mol_L, rho_kg_L, Cp_J_kg_K):
    """
    Adiabatic temperature rise for exothermic reaction:
    T = T0 + (-delta_H_rxn) * C_A0 * X / (rho * Cp)
    delta_H_rxn: heat of reaction at inlet conditions (J/mol_A; negative for exothermic)
    rho:         density of reaction mixture (kg/L)
    Cp:          heat capacity (J/kg/K)
    Returns: temperature rise for given conversion X
    """
    delta_T = (-delta_H_rxn_J_mol) * C_A0_mol_L * X / (rho_kg_L * Cp_J_kg_K)
    return {"delta_T_K": round(delta_T, 2),
            "note": "Positive delta_T means exothermic (heat released)"}

def adiabatic_equilibrium_conversion(k0, Ea_J_mol, K_eq_at_T0, T0_K,
                                      delta_H_rxn_J_mol, C_A0_mol_L,
                                      rho_kg_L, Cp_J_kg_K,
                                      n_points=50):
    """
    Find adiabatic equilibrium conversion by intersection of:
      1. Adiabatic line: T = T0 + delta_T_adiabatic * X
      2. Equilibrium curve: K_eq(T) determines X_eq(T)
    Returns: approximate adiabatic equilibrium conversion and temperature.
    Note: For reversible reaction A <=> B (equimolar), X_eq = K_eq / (1 + K_eq).
    """
    R = 8.314
    # Adiabatic temperature coefficient
    alpha = (-delta_H_rxn_J_mol) * C_A0_mol_L / (rho_kg_L * Cp_J_kg_K)

    results = []
    for i in range(n_points + 1):
        X = i / n_points
        T_ad = T0_K + alpha * X
        if T_ad <= 0:
            break
        # Equilibrium constant at T_ad (van't Hoff approximation)
        K_eq_T = K_eq_at_T0 * math.exp(-delta_H_rxn_J_mol / R * (1.0/T_ad - 1.0/T0_K))
        X_eq = K_eq_T / (1.0 + K_eq_T)  # for A <=> B equimolar
        results.append((X, T_ad, X_eq))

    # Find intersection: where X ≈ X_eq
    best = None
    best_diff = float('inf')
    for X, T_ad, X_eq in results:
        diff = abs(X - X_eq)
        if diff < best_diff:
            best_diff = diff
            best = (X, T_ad, X_eq)
    if best:
        return {"X_adiabatic_eq": round(best[0], 3),
                "T_adiabatic_eq_K": round(best[1], 1),
                "T_adiabatic_eq_C": round(best[1] - 273.15, 1)}
    return None
```

---

## Learning Resources

### Textbooks

| Author(s) | Title | Edition | Access |
|-----------|-------|---------|--------|
| Fogler, H.S. | *Elements of Chemical Reaction Engineering* | 6th ed. (2020), ISBN 978-0-13-548622-4 | **FREE** at umich.edu/~elements/6e/ |
| Levenspiel, O. | *Chemical Reaction Engineering* | 3rd ed. (1999), ISBN 978-0-471-25424-9 | Standard library |
| Davis, M.E. & Davis, R.J. | *Fundamentals of Chemical Reaction Engineering* | Caltech, 2003 | **FREE PDF** — search "Davis Davis CRE Caltech" |

### Free Online Resources

| Resource | URL | Notes |
|----------|-----|-------|
| Fogler 6th ed. FREE | umich.edu/~elements/6e/ | Full interactive text, Polymath problems |
| LearnChemE CRE YouTube | youtube.com/playlist?list=PL4xAk5aclnUhb5BU5QHpBWPdDVg3k0aMF | Prof. Liberatore, CSM; 100+ videos |
| MIT OCW 10.37 | ocw.mit.edu/courses/10-37-chemical-and-biological-reaction-engineering-spring-2007/ | Full course, lecture notes, problems |
| Davis & Davis Free PDF | Caltech (search: "Davis Fundamentals Chemical Reaction Engineering 2003") | Free PDF textbook |

### WVU Courses

- **ChBE 321** Chemical Reaction Engineering — primary course
- **PNGE 341** Well Completions — Damkohler number in wormhole acidizing context

---

## Output Format

```
## Reactor Design — [Reaction / System]

### Reaction System
| Parameter | Value | Units |
|-----------|-------|-------|
| Reaction | A + B -> C | |
| Rate law | -r_A = k * C_A^n | |
| k at T | mol/L/s or 1/s | |
| Ea | kJ/mol | |
| C_A0 | mol/L | |
| Target conversion X | | |

### Reactor Sizing
| Reactor Type | Volume (L) | tau (s) | Da |
|-------------|-----------|---------|-----|
| CSTR | | | |
| PFR | | | |
| Batch | — | t_rxn (s): | — |

### Multiple Reactors (if applicable)
| Config | Total Volume | Notes |
|--------|-------------|-------|
| n CSTRs in series | | |
| CSTR + PFR | | |

### Temperature Sensitivity
| T (K) | k | Conversion (CSTR) |
|-------|---|------------------|
| | | |

**Levenspiel Plot:** Plot 1/(-r_A) vs. X — area = PFR parameter; lowest point = optimal CSTR X

**Certainty:** HIGH for ideal reactors | Actual performance depends on mixing, RTD, heat transfer
```

---

## Error Handling

| Condition | Cause | Action |
|-----------|-------|--------|
| CSTR volume infinite | r_A at exit is zero (equilibrium or very low k) | Reduce X target or increase T to raise k |
| PFR integral diverges near X_target | Rate approaches zero (equilibrium) | Cannot reach X_target without recycle or temperature change |
| Negative delta_T_adiabatic | Endothermic reaction | Reactor temperature drops; may need heating |
| Da >> 1000 | Extremely fast reaction | Mass-transfer-limited; external/internal diffusion must be checked |

---

## Caveats

- **Ideal reactor assumptions:** Perfect mixing in CSTR, no axial dispersion in PFR.
  Real reactors show RTD (residence time distribution) effects — use Fogler Ch. 16-17
  for non-ideal reactors.
- **Isothermal assumption:** Modules 1-3 assume constant temperature. For exothermic
  reactions in PFR, the energy balance must be coupled with the mole balance (Fogler Ch. 8).
- **Constant-density liquid phase assumed.** For gas-phase reactions with changing
  moles, the volumetric flow rate changes with conversion (epsilon effect); see Fogler Ch. 5.
- **nth-order rate laws** are approximations. Langmuir-Hinshelwood and Michaelis-Menten
  kinetics (heterogeneous and enzymatic) require different design equation integration.
