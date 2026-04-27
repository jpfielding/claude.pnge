---
name: fluid-mechanics
description: >
  Fluid mechanics for chemical and petroleum engineers covering pipe flow,
  Bernoulli equation, Reynolds number, friction factors, and pump sizing.
  Implements Darcy-Weisbach pressure drop, Colebrook-White friction factor
  iterative solution, Blasius smooth-pipe correlation, mechanical energy
  balance with pump work and friction losses, pump power, venturi and orifice
  flow measurement, and hydrostatic pressure calculations. Use when the user
  asks about Reynolds number, laminar or turbulent flow, friction factor,
  Darcy-Weisbach equation, Moody diagram, pipe pressure drop, Bernoulli
  equation, pump head or power, NPSH, flow measurement, continuity equation,
  minor losses, fitting loss coefficients, or any pipe flow calculation.
  Resources: Bird Stewart Lightfoot Transport Phenomena 2nd ed ISBN
  978-0-470-11539-8; Fox McDonald Pritchard 9th ed; LearnChemE YouTube
  fluid mechanics playlist; MIT OCW 1.060. Primary courses: ChBE 311
  Fluid Mechanics, MAE 244 Fluid Dynamics.
---

# Fluid Mechanics Calculator

Computational skill for pipe flow, pump design, and flow measurement.
Covers core ChBE 311 and MAE 244 topics including dimensional analysis,
flow regimes, energy balance, and momentum transfer.

**SI units throughout.** (Pa, m, m/s, kg/m^3, Pa·s). Convert from field
units as needed: 1 psi = 6894.76 Pa; 1 ft = 0.3048 m; 1 gal/min = 6.309e-5 m^3/s.

---

## Module 1 — Flow Regimes and Reynolds Number

```python
def reynolds_number(rho_kg_m3, v_m_s, D_m, mu_Pa_s):
    """
    Reynolds number: Re = rho * v * D / mu
    rho:    fluid density (kg/m^3)
    v:      mean velocity (m/s)
    D:      pipe inner diameter (m)
    mu:     dynamic viscosity (Pa*s = kg/m/s)
    Returns: Re (dimensionless)
    Flow regime: Re < 2100 laminar; 2100-4000 transitional; > 4000 turbulent
    """
    return rho_kg_m3 * v_m_s * D_m / mu_Pa_s

def flow_regime(Re):
    """Classify flow regime by Reynolds number."""
    if Re < 2100:
        return {"regime": "laminar", "f_formula": "f = 64/Re"}
    elif Re < 4000:
        return {"regime": "transitional", "f_formula": "Use turbulent correlation; uncertain"}
    else:
        return {"regime": "turbulent", "f_formula": "Colebrook-White or Moody chart"}

def pipe_velocity(Q_m3_s, D_m):
    """Mean velocity from volumetric flow rate: v = Q / A"""
    import math
    A = math.pi / 4.0 * D_m**2
    return Q_m3_s / A

def hydraulic_diameter(A_m2, P_wetted_m):
    """
    Hydraulic diameter for non-circular ducts: D_h = 4*A / P_wetted
    Use D_h in place of D for Re and pressure drop in non-circular channels.
    """
    return 4.0 * A_m2 / P_wetted_m
```

---

## Module 2 — Friction Factor and Pressure Drop

```python
import math

def friction_factor_laminar(Re):
    """Darcy friction factor for laminar flow: f = 64/Re (Darcy-Weisbach)."""
    if Re <= 0:
        return None
    return 64.0 / Re

def blasius_turbulent(Re):
    """
    Blasius correlation for smooth pipes, turbulent flow (Re 4000–100,000):
    f = 0.316 * Re^(-0.25)  (Darcy friction factor)
    """
    if Re < 4000:
        return None
    return 0.316 * Re**(-0.25)

def colebrook_white(Re, eps_over_D, tol=1e-8, max_iter=50):
    """
    Colebrook-White equation (implicit, solved iteratively):
    1/sqrt(f) = -2.0 * log10(eps/(3.7*D) + 2.51/(Re*sqrt(f)))
    Re:         Reynolds number (turbulent, > 4000)
    eps_over_D: relative roughness (eps/D; steel pipe eps ≈ 0.046 mm)
    Returns: Darcy friction factor
    """
    if Re < 4000:
        return friction_factor_laminar(Re)
    # Initial guess: Swamee-Jain explicit approximation
    eps_D = eps_over_D
    f = (0.25 / (math.log10(eps_D/3.7 + 5.74/Re**0.9))**2)
    for _ in range(max_iter):
        rhs = -2.0 * math.log10(eps_D/3.7 + 2.51/(Re * math.sqrt(f)))
        f_new = 1.0 / rhs**2
        if abs(f_new - f) < tol:
            return f_new
        f = f_new
    return f

def darcy_weisbach_dP(f, rho_kg_m3, v_m_s, L_m, D_m):
    """
    Darcy-Weisbach pressure drop:
    dP = f * (L/D) * (rho*v^2/2)   [Pa]
    f:   Darcy friction factor (NOT Fanning; Darcy = 4 * Fanning)
    Returns: pressure drop (Pa), head loss (m)
    """
    dP = f * (L_m / D_m) * 0.5 * rho_kg_m3 * v_m_s**2
    h_f = dP / (rho_kg_m3 * 9.81)  # head loss in meters
    return {"dP_Pa": round(dP, 2), "dP_psi": round(dP / 6894.76, 4),
            "head_loss_m": round(h_f, 4)}

def minor_loss_dP(K, rho_kg_m3, v_m_s):
    """
    Minor (fitting) pressure loss: dP = K * (rho*v^2/2)
    Common K values:
      Gate valve fully open: K=0.1; half open: K=2.1
      Globe valve:           K=6-10
      90-deg elbow:          K=0.9 (std); K=0.3 (long-radius)
      Tee (flow-through):    K=0.4
      Tee (branch):          K=1.5
      Sudden expansion:      K=(1-A1/A2)^2
      Sudden contraction:    K≈0.5*(1-A2/A1)
    """
    return K * 0.5 * rho_kg_m3 * v_m_s**2

def total_pressure_drop(f, rho_kg_m3, v_m_s, L_m, D_m, K_total=0.0):
    """
    Total pressure drop: pipe friction + minor losses.
    K_total: sum of all fitting K values in the pipe run.
    """
    dP_pipe = f * (L_m / D_m) * 0.5 * rho_kg_m3 * v_m_s**2
    dP_minor = K_total * 0.5 * rho_kg_m3 * v_m_s**2
    return {"dP_pipe_Pa": round(dP_pipe, 2),
            "dP_minor_Pa": round(dP_minor, 2),
            "dP_total_Pa": round(dP_pipe + dP_minor, 2),
            "dP_total_psi": round((dP_pipe + dP_minor) / 6894.76, 4)}
```

---

## Module 3 — Bernoulli and Mechanical Energy Balance

```python
def bernoulli_exit_velocity(P1_Pa, rho1, v1, z1_m,
                              P2_Pa, rho2, z2_m, g=9.81):
    """
    Bernoulli equation (no friction, incompressible):
    P1/rho + v1^2/2 + g*z1 = P2/rho + v2^2/2 + g*z2
    Solve for v2 (exit velocity).
    Returns: v2 (m/s) or None if energy not sufficient
    """
    rho = 0.5 * (rho1 + rho2)  # approximate; use consistent density
    v2_sq = v1**2 + 2.0*((P1_Pa - P2_Pa)/rho + g*(z1_m - z2_m))
    if v2_sq < 0:
        return None  # No solution — check inputs
    return math.sqrt(v2_sq)

def mechanical_energy_balance(P1_Pa, rho, v1, z1_m,
                                P2_Pa, v2, z2_m,
                                eta_pump=0.75, g=9.81):
    """
    Mechanical energy balance with pump work and friction loss:
    W_pump (per unit mass) = (P2-P1)/rho + (v2^2-v1^2)/2 + g*(z2-z1) + h_f
    Returns: required pump work per unit mass (J/kg), pump head (m)
    """
    delta_p_term = (P2_Pa - P1_Pa) / rho
    delta_ke = 0.5 * (v2**2 - v1**2)
    delta_pe = g * (z2_m - z1_m)
    W_shaft = delta_p_term + delta_ke + delta_pe  # net fluid work (no friction yet)
    # Include friction if h_f (head loss in m) is provided separately
    return {"W_shaft_J_kg": round(W_shaft, 2),
            "pump_head_m": round(W_shaft / g, 3),
            "note": "Add friction loss h_f (m) to pump_head_m for actual pump head required"}

def pump_power_kW(Q_m3_s, delta_P_Pa, eta=0.75):
    """
    Pump shaft power: P_shaft = Q * delta_P / eta
    Q:       volumetric flow rate (m^3/s)
    delta_P: total pressure rise across pump (Pa)
    eta:     overall pump efficiency (0.60-0.80 typical)
    Returns: shaft power (kW), fluid power (kW)
    """
    P_fluid_kW = Q_m3_s * delta_P_Pa / 1000.0
    P_shaft_kW = P_fluid_kW / eta
    return {"P_fluid_kW": round(P_fluid_kW, 3),
            "P_shaft_kW": round(P_shaft_kW, 3),
            "P_shaft_hp": round(P_shaft_kW / 0.7457, 2)}
```

---

## Module 4 — Flow Measurement

```python
def venturi_flow_rate(Cd, A1_m2, A2_m2, delta_P_Pa, rho_kg_m3):
    """
    Venturi meter volumetric flow rate:
    Q = Cd * A2 * sqrt(2*delta_P / (rho*(1-(A2/A1)^2)))
    Cd: discharge coefficient (0.95-0.99 for well-designed venturis)
    A1: upstream pipe area (m^2)
    A2: throat area (m^2)
    delta_P: pressure differential (Pa)
    Returns: Q (m^3/s), velocity at throat (m/s)
    """
    beta_sq = (A2_m2 / A1_m2)**2
    Q = Cd * A2_m2 * math.sqrt(2.0 * delta_P_Pa / (rho_kg_m3 * (1.0 - beta_sq)))
    v_throat = Q / A2_m2
    return {"Q_m3_s": round(Q, 6), "Q_gpm": round(Q * 15850.3, 2),
            "v_throat_m_s": round(v_throat, 3)}

def orifice_flow_rate(Cd, A_orifice_m2, delta_P_Pa, rho_kg_m3):
    """
    Orifice meter flow rate: Q = Cd * A_o * sqrt(2*delta_P/rho)
    Cd: discharge coefficient (0.60-0.65 for standard sharp-edged orifice)
    Returns: Q (m^3/s)
    """
    Q = Cd * A_orifice_m2 * math.sqrt(2.0 * delta_P_Pa / rho_kg_m3)
    return {"Q_m3_s": round(Q, 6), "Q_gpm": round(Q * 15850.3, 2)}

def rotameter_correction(Q_cal, rho_cal, rho_fluid, mu_cal, mu_fluid):
    """
    Correct rotameter reading for different fluid properties.
    Q_actual = Q_cal * sqrt(rho_cal/rho_fluid) * (mu_fluid/mu_cal)^n
    n ≈ 0 for turbulent float; n ≈ 0.5 for laminar (viscous) float
    Conservative: use n=0 (turbulent) for most process rotameters.
    """
    return Q_cal * math.sqrt(rho_cal / rho_fluid)
```

---

## Learning Resources

### Textbooks

| Author(s) | Title | Edition | ISBN |
|-----------|-------|---------|------|
| Bird, Stewart & Lightfoot | *Transport Phenomena* | 2nd ed. (2007) | 978-0-470-11539-8 |
| Fox, McDonald & Pritchard | *Introduction to Fluid Mechanics* | 9th ed. (2015) | 978-1-118-01297-1 |
| White, F.M. | *Fluid Mechanics* | 8th ed. (2015) | 978-0-07-339827-3 |
| Munson, Okiishi, Huebsch & Rothmayer | *Fundamentals of Fluid Mechanics* | 8th ed. (2016) | 978-1-119-08070-1 |

### Free Online Resources

| Resource | URL | Notes |
|----------|-----|-------|
| LearnChemE — Fluid Mechanics YouTube | youtube.com/playlist?list=PL4xAk5aclnUi83lMy9KFvYrSbqU8QopBO | Prof. Liberatore, CSM; 60+ videos ChBE 311 level |
| MIT OCW 1.060 | ocw.mit.edu/courses/1-060-engineering-mechanics-ii | Fluid statics, pipe flow, open channel |
| NPTEL Fluid Mechanics | nptel.ac.in (search "Chemical Engineering Fluid Mechanics") | IIT Kharagpur; Chakraborty |
| HyperPhysics Fluids | hyperphysics.phy-astr.gsu.edu/hbase/fluid.html | Quick reference |
| Engineering Toolbox | engineeringtoolbox.com | Pipe roughness, viscosity tables |

### WVU Courses

- **ChBE 311** Fluid Mechanics — core ChBE curriculum
- **MAE 244** Fluid Dynamics — mechanical engineering perspective
- **PNGE 361** Production Engineering — pipe flow applied to tubing and surface lines

---

## Roughness Reference

| Material | Roughness eps (mm) | eps/D for 2" pipe |
|----------|-------------------|-------------------|
| Drawn tubing (smooth) | 0.0015 | 0.00003 |
| Commercial steel | 0.046 | 0.0009 |
| Galvanized iron | 0.15 | 0.003 |
| Cast iron | 0.26 | 0.005 |
| Concrete | 0.3–3 | 0.006–0.06 |

---

## Output Format

```
## Pipe Flow Analysis — [System Description]

### Input Summary
| Parameter | Value | Units |
|-----------|-------|-------|
| Flow rate (Q) | | m^3/s or gpm |
| Pipe ID (D) | | m or in |
| Fluid density | | kg/m^3 |
| Fluid viscosity | | Pa*s or cP |
| Pipe length | | m or ft |
| Pipe roughness (eps/D) | | dimensionless |

### Flow Regime
| Parameter | Value |
|-----------|-------|
| Mean velocity | m/s |
| Reynolds number | |
| Flow regime | Laminar / Turbulent |
| Friction factor (f, Darcy) | |
| Method | Laminar / Blasius / Colebrook-White |

### Pressure Drop
| Component | dP (Pa) | dP (psi) |
|-----------|---------|---------|
| Pipe friction | | |
| Minor losses | | |
| **Total** | | |

**Reasonableness:** Compare dP to available pump head; check v < 3 m/s for most liquids
```

---

## Error Handling

| Condition | Cause | Action |
|-----------|-------|--------|
| Re in transition zone (2100-4000) | Slug/intermittent flow | Use turbulent correlation; note uncertainty |
| v > 5 m/s in liquid line | Excessive velocity, erosion risk | Increase pipe diameter |
| Colebrook-White not converging | Very low Re or extreme eps/D | Check inputs; use explicit Swamee-Jain |
| Negative v2 from Bernoulli | Insufficient energy at inlet | Check pressures and elevations; system needs pump |

---

## Caveats

- **Darcy vs. Fanning:** The Darcy friction factor (f_D = 4 * f_F) is used here and
  in the Darcy-Weisbach equation. Many ChBE textbooks (including BSL) use the Fanning
  friction factor. Verify which convention your textbook uses before substituting.
- **Incompressible flow assumed.** For gas flow, use compressible flow equations
  or break into segments with average properties. Valid for liquids and low-velocity
  gas (Ma < 0.3).
- **Colebrook-White is implicit.** Must be solved iteratively. The Swamee-Jain
  explicit approximation (used as initial guess above) is accurate to ±2%.
- **Minor loss K values** are approximations. Use manufacturer data for control
  valves and other precision-critical fittings.
