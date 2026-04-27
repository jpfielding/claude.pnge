---
name: thermo-eos
description: >
  Equations of state and phase equilibrium thermodynamics for pure fluids and
  mixtures. Implements van der Waals, Peng-Robinson, and Soave-Redlich-Kwong
  cubic equations of state, fugacity coefficient from PR EOS, Z-factor cubic
  root solution, departure functions for enthalpy and entropy, Raoult law VLE,
  K-value flash, and Rachford-Rice bubble and dew point calculation. Use when
  the user asks about Peng-Robinson equation of state, fugacity coefficient,
  compressibility factor Z, van der Waals EOS, SRK equation, acentric factor,
  vapor-liquid equilibrium, K-value, bubble point pressure, dew point
  temperature, Rachford-Rice flash, enthalpy departure, entropy departure, or
  any EOS thermodynamics calculation. Resources: Smith Van Ness Abbott
  Introduction to Chemical Engineering Thermodynamics 9th ed ISBN
  978-1-260-57775-6; LearnChemE YouTube thermodynamics playlist; MIT OCW
  10.40 Chemical Engineering Thermodynamics. Primary courses: ChBE 231
  Thermodynamics, ChBE 311.
---

# Equations of State and Phase Equilibrium

Computational skill for cubic equations of state (vdW, PR, SRK), fugacity
calculations, departure functions, and vapor-liquid equilibrium. Calibrated
for oil and gas reservoir fluid thermodynamics.

**Units:** SI unless noted. T in Kelvin, P in bar (1 bar = 14.504 psi = 100 kPa),
V in L/mol. R = 0.08314 L·bar/mol·K.

---

## Module 1 — Cubic Equations of State

```python
import math

R = 0.08314  # L*bar / (mol*K)

def van_der_waals_pressure(T_K, V_m_L_mol, a_L2_bar_mol2, b_L_mol):
    """
    van der Waals EOS: P = R*T/(V-b) - a/V^2
    a: attraction parameter (L^2*bar/mol^2)
    b: excluded volume parameter (L/mol)
    Returns: pressure (bar)
    Common vdW parameters:
      CO2: a=3.658, b=0.04286
      H2O: a=5.537, b=0.03049
      CH4: a=2.300, b=0.04301
      N2:  a=1.370, b=0.03870
    """
    if V_m_L_mol <= b_L_mol:
        raise ValueError("V must be greater than b (excluded volume)")
    return R * T_K / (V_m_L_mol - b_L_mol) - a_L2_bar_mol2 / V_m_L_mol**2

def peng_robinson_parameters(Tc_K, Pc_bar, omega):
    """
    Peng-Robinson EOS parameters at a given temperature.
    Returns: a, b, alpha, A, B coefficients for PR EOS.
    PR: P = R*T/(V-b) - a*alpha/(V*(V+b) + b*(V-b))
    kappa = 0.37464 + 1.54226*omega - 0.26992*omega^2
    alpha(T) = (1 + kappa*(1 - sqrt(T/Tc)))^2
    a_c = 0.45724 * R^2 * Tc^2 / Pc
    b   = 0.07780 * R * Tc / Pc
    """
    kappa = 0.37464 + 1.54226 * omega - 0.26992 * omega**2
    a_c = 0.45724 * R**2 * Tc_K**2 / Pc_bar
    b = 0.07780 * R * Tc_K / Pc_bar
    return {"kappa": kappa, "a_c": a_c, "b": b}

def peng_robinson_Z(T_K, P_bar, Tc_K, Pc_bar, omega):
    """
    Solve PR EOS for compressibility factor Z.
    Z^3 + (B-1)*Z^2 + (A-3B^2-2B)*Z + (B^3+B^2-AB) = 0
    A = a*alpha*P/(R*T)^2,  B = b*P/(R*T)
    Returns: list of real positive Z roots (largest = vapor, smallest = liquid)
    """
    params = peng_robinson_parameters(Tc_K, Pc_bar, omega)
    kappa = params["kappa"]
    a_c = params["a_c"]
    b = params["b"]

    alpha = (1.0 + kappa * (1.0 - math.sqrt(T_K / Tc_K)))**2
    a = a_c * alpha

    A = a * P_bar / (R * T_K)**2
    B = b * P_bar / (R * T_K)

    # Cubic: Z^3 + p*Z^2 + q*Z + r = 0
    p_coef = B - 1.0
    q_coef = A - 3.0*B**2 - 2.0*B
    r_coef = B**3 + B**2 - A*B

    # Solve cubic using analytical method (Cardano/depressed cubic)
    # Substitution Z = t - p/3
    a2 = p_coef
    a1 = q_coef
    a0 = r_coef
    f = a1 - a2**2 / 3.0
    g = 2.0*a2**3/27.0 - a2*a1/3.0 + a0
    h = g**2/4.0 + f**3/27.0

    roots = []
    if h > 1e-10:  # one real root
        sqrt_h = math.sqrt(h)
        S = (-g/2.0 + sqrt_h)
        U = (-g/2.0 - sqrt_h)
        S3 = math.copysign(abs(S)**(1.0/3.0), S)
        U3 = math.copysign(abs(U)**(1.0/3.0), U)
        z1 = S3 + U3 - a2/3.0
        roots = [z1]
    else:  # three real roots
        i2 = math.sqrt(g**2/4.0 - h)
        j = math.copysign(abs(i2)**(1.0/3.0), i2)
        k2 = math.acos(-g / (2.0*j)) if abs(j) > 1e-12 else 0.0
        m2 = math.cos(k2/3.0)
        n2 = math.sqrt(3.0) * math.sin(k2/3.0)
        z1 = 2.0*j*math.cos(k2/3.0) - a2/3.0
        z2 = -j*(m2 + n2) - a2/3.0
        z3 = -j*(m2 - n2) - a2/3.0
        roots = sorted([z1, z2, z3])

    # Return only roots > B (physically meaningful)
    valid = [z for z in roots if z > B]
    return {"Z_roots": [round(z, 6) for z in valid],
            "Z_vapor": round(max(valid), 6) if valid else None,
            "Z_liquid": round(min(valid), 6) if valid else None,
            "A": round(A, 6), "B": round(B, 6)}

def srk_parameters(Tc_K, Pc_bar, omega):
    """
    Soave-Redlich-Kwong EOS parameters.
    SRK: P = R*T/(V-b) - a*alpha / (V*(V+b))
    m = 0.480 + 1.574*omega - 0.176*omega^2
    a_c = 0.42748 * R^2 * Tc^2 / Pc
    b   = 0.08664 * R * Tc / Pc
    """
    m = 0.480 + 1.574*omega - 0.176*omega**2
    a_c = 0.42748 * R**2 * Tc_K**2 / Pc_bar
    b = 0.08664 * R * Tc_K / Pc_bar
    return {"m": m, "a_c": a_c, "b": b}
```

**Critical property reference (common reservoir fluids):**

| Component | Tc (K) | Pc (bar) | omega | Notes |
|-----------|--------|----------|-------|-------|
| CH4 (methane) | 190.6 | 46.0 | 0.011 | Main gas component |
| C2H6 (ethane) | 305.3 | 48.7 | 0.099 | |
| C3H8 (propane) | 369.8 | 42.5 | 0.153 | |
| n-C4 (butane) | 425.1 | 37.96 | 0.200 | |
| n-C7 (heptane) | 540.2 | 27.4 | 0.351 | |
| CO2 | 304.1 | 73.8 | 0.239 | EOR, CCS |
| H2O | 647.1 | 220.6 | 0.345 | |
| N2 | 126.2 | 33.9 | 0.039 | |

---

## Module 2 — Fugacity from PR EOS

```python
def pr_fugacity_coefficient(Z, A, B):
    """
    Fugacity coefficient from PR EOS:
    ln(phi) = (Z-1) - ln(Z-B) - A/(2*sqrt(2)*B) * ln((Z+(1+sqrt(2))*B)/(Z+(1-sqrt(2))*B))
    Z: compressibility factor (vapor or liquid root)
    A, B: PR parameters from peng_robinson_Z output
    Returns: fugacity coefficient phi (dimensionless)
    """
    sqrt2 = math.sqrt(2.0)
    if Z <= B or Z <= 0:
        return None
    arg_ln1 = Z - B
    if arg_ln1 <= 0:
        return None
    arg_ln2_num = Z + (1.0 + sqrt2) * B
    arg_ln2_den = Z + (1.0 - sqrt2) * B
    if arg_ln2_den <= 0 or arg_ln2_num <= 0:
        return None
    ln_phi = (Z - 1.0) - math.log(arg_ln1) - A / (2.0 * sqrt2 * B) * math.log(arg_ln2_num / arg_ln2_den)
    return {"ln_phi": round(ln_phi, 6), "phi": round(math.exp(ln_phi), 6)}

def fugacity(phi, y_mole_frac, P_bar):
    """
    Fugacity of component i: f_i = phi_i * y_i * P
    phi:       fugacity coefficient
    y_mole_frac: mole fraction
    P_bar:     total pressure (bar)
    Returns: fugacity (bar)
    """
    return phi * y_mole_frac * P_bar

def vle_equilibrium_condition(phi_L, phi_V, x_i, y_i, P_bar):
    """
    VLE equilibrium: f_i^L = f_i^V  =>  phi_i^L * x_i * P = phi_i^V * y_i * P
    K-value: K_i = y_i / x_i = phi_i^L / phi_i^V
    Returns: K_i and deviation from equilibrium (should be 1.0 at equilibrium)
    """
    K_i = phi_L / phi_V
    ratio = (phi_L * x_i) / (phi_V * y_i) if phi_V * y_i > 0 else None
    return {"K_i": round(K_i, 5), "equilibrium_check": round(ratio, 5) if ratio else None}
```

---

## Module 3 — Departure Functions (Residual Properties)

```python
def pr_enthalpy_departure(T_K, Tc_K, Pc_bar, omega, Z, A, B):
    """
    Enthalpy departure from PR EOS:
    (H - H_ig) / (R*T) = Z - 1 - A/(2*sqrt(2)*B) * (1 + kappa*sqrt(T/Tc)/sqrt(alpha)) * ln(...)
    Returns: (H - H^ig) in J/mol (residual enthalpy)
    """
    sqrt2 = math.sqrt(2.0)
    kappa = 0.37464 + 1.54226 * omega - 0.26992 * omega**2
    Tr = T_K / Tc_K
    alpha = (1.0 + kappa * (1.0 - math.sqrt(Tr)))**2
    d_alpha_dT = -kappa / math.sqrt(T_K * Tc_K) * (1.0 + kappa * (1.0 - math.sqrt(Tr)))

    a_c = 0.45724 * R**2 * Tc_K**2 / Pc_bar
    b = 0.07780 * R * Tc_K / Pc_bar
    T_da_dT = T_K * a_c * d_alpha_dT  # T * da/dT

    arg_num = Z + (1.0 + sqrt2) * B
    arg_den = Z + (1.0 - sqrt2) * B
    if arg_den <= 0 or arg_num <= 0 or Z <= 0:
        return None

    H_dep = R * T_K * (Z - 1.0) + (T_da_dT * alpha / (a_c) - a_c * alpha) / (2.0 * sqrt2 * b) * math.log(arg_num / arg_den)
    # Simplified version: use A*R*T factor
    H_dep_RT = Z - 1.0 - A / (2.0*sqrt2*B) * (1.0 + kappa*math.sqrt(Tr)/math.sqrt(alpha)) * math.log(arg_num/arg_den)
    return {"H_dep_J_mol": round(H_dep_RT * R * T_K * 1000.0, 2),
            "H_dep_kJ_mol": round(H_dep_RT * R * T_K, 4)}

def pr_entropy_departure(T_K, Tc_K, Pc_bar, omega, Z, A, B, P_bar, P_ref_bar=1.0):
    """
    Entropy departure from PR EOS (simplified):
    (S - S_ig) / R = ln(Z - B) - A/(2*sqrt(2)*B) * (kappa*sqrt(Tr/alpha)) * ln(...) - ln(P/P_ref)
    Returns: (S - S^ig) in J/mol/K
    """
    sqrt2 = math.sqrt(2.0)
    kappa = 0.37464 + 1.54226 * omega - 0.26992 * omega**2
    Tr = T_K / Tc_K
    alpha = (1.0 + kappa * (1.0 - math.sqrt(Tr)))**2

    arg_num = Z + (1.0 + sqrt2) * B
    arg_den = Z + (1.0 - sqrt2) * B
    if arg_den <= 0 or Z <= B or arg_num <= 0:
        return None

    S_dep_R = math.log(Z - B) - A / (2.0*sqrt2*B) * kappa * math.sqrt(Tr/alpha) * math.log(arg_num/arg_den) - math.log(P_bar/P_ref_bar)
    return {"S_dep_J_mol_K": round(S_dep_R * R * 1000.0, 3)}
```

---

## Module 4 — Phase Equilibrium (VLE)

```python
def raoult_law_bubble_pressure(x_list, P_sat_list):
    """
    Bubble point pressure (Raoult's law for ideal mixtures):
    P_bubble = sum(x_i * P_sat_i)
    x_list:     liquid mole fractions [x1, x2, ...]
    P_sat_list: pure component saturation pressures [P_sat1, P_sat2, ...]
    Returns: bubble point pressure and vapor compositions y_i = x_i * P_sat_i / P
    """
    P_bubble = sum(x * Ps for x, Ps in zip(x_list, P_sat_list))
    y_list = [x * Ps / P_bubble for x, Ps in zip(x_list, P_sat_list)]
    return {"P_bubble": round(P_bubble, 4),
            "y_vapor": [round(y, 5) for y in y_list],
            "sum_y": round(sum(y_list), 6)}

def rachford_rice_flash(z_list, K_list, tol=1e-8, max_iter=100):
    """
    Rachford-Rice equation for isothermal flash:
    g(psi) = sum(z_i*(K_i - 1) / (1 + psi*(K_i - 1))) = 0
    psi: vapor mole fraction (V/F)
    z_list: overall mole fractions
    K_list: K-values (K_i = y_i/x_i = phi_i_L/phi_i_V)
    Returns: psi (vapor fraction), x (liquid), y (vapor) compositions
    """
    # Bounds for psi
    K_min = min(K_list)
    K_max = max(K_list)
    psi_min = 1.0 / (1.0 - K_max) + 1e-6
    psi_max = 1.0 / (1.0 - K_min) - 1e-6
    psi_min = max(0.0, psi_min)
    psi_max = min(1.0, psi_max)

    if psi_max <= psi_min:
        # All vapor or all liquid
        sum_zK = sum(z * K for z, K in zip(z_list, K_list))
        if sum_zK <= 1.0:
            return {"psi": 0.0, "phase": "all liquid", "x": z_list, "y": K_list}
        sum_z_over_K = sum(z / K for z, K in zip(z_list, K_list))
        if sum_z_over_K <= 1.0:
            return {"psi": 1.0, "phase": "all vapor", "x": z_list, "y": z_list}

    # Bisection method
    psi = 0.5 * (psi_min + psi_max)
    for _ in range(max_iter):
        g = sum(z * (K - 1.0) / (1.0 + psi * (K - 1.0))
                for z, K in zip(z_list, K_list))
        if abs(g) < tol:
            break
        if g > 0:
            psi_min = psi
        else:
            psi_max = psi
        psi = 0.5 * (psi_min + psi_max)

    # Compositions
    x_list = [z / (1.0 + psi * (K - 1.0)) for z, K in zip(z_list, K_list)]
    y_list = [K * x for K, x in zip(K_list, x_list)]
    return {"psi_vapor_frac": round(psi, 6),
            "x_liquid": [round(x, 6) for x in x_list],
            "y_vapor": [round(y, 6) for y in y_list],
            "sum_x": round(sum(x_list), 6),
            "sum_y": round(sum(y_list), 6)}

def wilson_K_value(Tc_K, Pc_bar, omega, T_K, P_bar):
    """
    Wilson correlation for initial K-value estimate:
    K_i = (Pc_i/P) * exp(5.373*(1+omega_i)*(1 - Tc_i/T))
    Good starting point for iterative VLE calculations.
    """
    return (Pc_bar / P_bar) * math.exp(5.373 * (1.0 + omega) * (1.0 - Tc_K / T_K))
```

---

## Learning Resources

### Textbooks

| Author(s) | Title | Edition | ISBN |
|-----------|-------|---------|------|
| Smith, Van Ness & Abbott | *Introduction to ChE Thermodynamics* | 9th ed. (2022) | 978-1-260-57775-6 |
| Matsoukas, T. | *Fundamentals of ChE Thermodynamics* | (2013) | 978-0-13-285388-1 |
| Sandler, S.I. | *Chemical Engineering Thermodynamics* | 5th ed. (2017) | 978-1-118-76594-0 |
| Prausnitz, Lichtenthaler & Azevedo | *Molecular Thermodynamics of Fluid-Phase Equilibria* | 3rd ed. | 978-0-13-977745-5 |

### Free Online Resources

| Resource | URL | Notes |
|----------|-----|-------|
| LearnChemE Thermo YouTube | youtube.com/playlist?list=PL4xAk5aclnUjG24pHjFBRb1l2jY1v2r_c | Prof. Liberatore, CSM; covers PR EOS, VLE |
| MIT OCW 10.40 | ocw.mit.edu/courses/10-40-chemical-engineering-thermodynamics-fall-2003/ | Full course, lecture notes |
| NIST WebBook | webbook.nist.gov/chemistry/fluid/ | Reference EOS data for validation |
| Knovel (via WVU Library) | knovel.com | Perry's Chemical Engineers' Handbook |

### WVU Courses

- **ChBE 231** Chemical Engineering Thermodynamics I — EOS, departure functions, VLE
- **ChBE 311** Fluid Mechanics and Thermodynamics II — applied phase equilibrium
- **PNGE (mass-energy-balance skill)** — reservoir fluid flash calculations

---

## Output Format

```
## EOS Calculation — [Fluid / Mixture]

### EOS Parameters
| Component | Tc (K) | Pc (bar) | omega | a | b |
|-----------|--------|----------|-------|---|---|
| | | | | | |

### Compressibility Factor (PR EOS)
| Phase | Z | Molar Volume (L/mol) | Density (kg/m^3) |
|-------|---|---------------------|----------------|
| Vapor | | | |
| Liquid | | | |

### Fugacity / VLE
| Component | phi_L | phi_V | K_i | x_i | y_i |
|-----------|-------|-------|-----|-----|-----|
| | | | | | |

**Flash result:** psi = [vapor fraction] at T = [K], P = [bar]

**Departure Functions:**
| Property | Value | Units |
|----------|-------|-------|
| H_dep | | kJ/mol |
| S_dep | | J/mol/K |

**Certainty:** HIGH for light hydrocarbons | MEDIUM for polar/associating fluids (use CPA/SAFT)
```

---

## Error Handling

| Condition | Cause | Action |
|-----------|-------|--------|
| No real Z roots > B | Inputs outside EOS validity | Check T, P, Tc, Pc; verify units (bar not psi) |
| Rachford-Rice no convergence | K-values inconsistent with stability | Run Michelsen stability test; consider two-phase check |
| Z negative | Numerical error in cubic solver | Check A and B values; increase precision |
| phi > 100 | Conditions near spinodal | Near phase boundary; use smaller pressure step |

---

## Caveats

- **PR EOS is not suitable for highly polar fluids** (water, alcohols, acids).
  Use CPA (Cubic Plus Association) or SAFT for polar systems.
- **Mixing rules:** This skill uses van der Waals one-fluid mixing rules (no
  binary interaction parameters k_ij). For accurate mixture calculations,
  k_ij values from literature or regression are needed.
- **Three roots of the cubic:** The middle root is always unphysical
  (spinodal region). Select the largest Z for vapor phase, smallest for liquid.
- **Wilson K-values** are a good starting estimate but can diverge for
  near-critical mixtures. Always verify convergence of VLE iterations.
- For reservoir gas calculations, the `pnge-geochem-pw:mass-energy-balance` skill and
  `pnge-geochem-pw:nist-webbook` skill provide validated property lookup alongside EOS.
