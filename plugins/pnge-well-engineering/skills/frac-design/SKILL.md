---
name: frac-design
description: >
  Perform hydraulic fracture design and analysis calculations for PNGE 341
  completions engineering. Covers fracture geometry estimation using PKN and
  KGD analytical models, net treating pressure, fluid efficiency, proppant
  transport and settling, Nolte-Smith pressure diagnostics, fracture closure
  pressure from ISIP analysis, step-rate test interpretation, and post-frac
  production analysis. Use this skill when the user needs to estimate fracture
  length or width, analyze treating pressure trends, calculate fluid loss
  coefficient, determine closure pressure, design proppant schedules, evaluate
  net pressure and fracture containment, or work through hydraulic fracturing
  calculations for coursework or research. Trigger for phrases like "fracture
  half-length estimate", "PKN model fracture width", "net treating pressure",
  "fluid efficiency calculation", "closure pressure from ISIP", "Nolte-Smith
  plot", "proppant settling velocity", "G-function analysis", "step-rate test",
  or "hydraulic fracture geometry". Produces design parameter tables,
  step-by-step calculations, and pressure diagnostic interpretations.
---

# Hydraulic Fracture Design Calculator

Completions engineering skill for hydraulic fracture design and analysis.
Covers the analytical fracture mechanics models (PKN, KGD), pressure
diagnostics (Nolte-Smith, G-function, ISIP), fluid and proppant design, and
post-frac evaluation. Calibrated for Appalachian/Marcellus completions.

**Important:** Analytical fracture models are simplified approximations. For
final stage design use a dedicated simulator (GOHFER, MFrac, ResFrac, or
tNavigator fracture module). These calculations are appropriate for scoping,
coursework, and first-pass design screening.

---

## Module 1 — Closure Pressure and Stress State

### Capabilities

- Fracture closure pressure from ISIP (instantaneous shut-in pressure)
- G-function analysis for closure identification
- Net treating pressure calculation
- Fracture gradient from LOT/XLOT interpretation
- Step-rate test interpretation for minimum horizontal stress

### Key Pressure Definitions

| Pressure | Symbol | Definition |
|----------|--------|------------|
| Breakdown pressure | P_bd | Wellbore pressure at which fracture initiates |
| Instantaneous shut-in pressure | ISIP | Wellbore pressure immediately after pumps stop |
| Fracture closure pressure | P_c | Pressure at which fracture faces close on proppant |
| Net pressure | p_net | p_treating - p_closure (excess above closure) |
| Fracture extension pressure | P_ext | Pressure required to propagate open fracture |
| Minimum horizontal stress | S_hmin | Equal to closure pressure (first approximation) |

### ISIP Analysis

The ISIP is measured from pump-off pressure fall-off and provides the best
field estimate of minimum horizontal stress:

```
P_c ≈ ISIP  (first approximation, valid when fluid loss is fast)
```

More precisely, ISIP is slightly above P_c because some net pressure remains
immediately after shut-in. P_c is found from the pressure fall-off inflection.

**Typical Marcellus ISIP/closure gradient:** 0.65 - 0.75 psi/ft TVD

```python
def closure_from_ISIP(ISIP_psi, depth_ft, correction_psi=50):
    """
    Estimate closure pressure from ISIP.
    correction_psi: typical 30-100 psi correction (conservative use 50 psi).
    """
    P_c = ISIP_psi - correction_psi
    gradient = P_c / depth_ft
    print(f"ISIP: {ISIP_psi} psi")
    print(f"Estimated closure pressure: {P_c} psi")
    print(f"Closure gradient: {gradient:.4f} psi/ft ({gradient/0.052:.2f} ppg)")
    return P_c

# Example: Marcellus at 7,500 ft, ISIP = 5,400 psi
P_c = closure_from_ISIP(5400, 7500)
```

### Net Pressure

```
p_net = p_bh_treating - P_c
```

Where p_bh_treating = surface treating pressure + hydrostatic head - friction losses.

**Typical net pressures:**
- Slickwater frac: 100-500 psi (low net pressure, long/thin fracture)
- Cross-linked gel frac: 500-2,000 psi (higher net, more width)
- Refrac: variable, often higher than initial due to elevated stress shadow

### Fracture Gradient from LOT

Leak-off test gives minimum horizontal stress:
```
FG (psi/ft) = P_LOT / depth_TVD
```

Step-rate test: plot injection rate vs surface pressure; slope change indicates
fracture extension. The pressure at the rate/pressure inflection = fracture extension pressure.

```
S_hmin ≈ P_extension - (friction pressure + wellbore hydrostatic correction)
```

### G-Function Analysis (Nolte)

The G-function is a dimensionless time function used to identify fracture
closure from pressure fall-off data:

```
G(Delta_t_D) = (4/3) * [(1 + Delta_t_D)^(3/2) - Delta_t_D^(3/2) - 1]
```

Where Delta_t_D = Delta_t / t_p (ratio of shut-in time to pump time).

**Closure identification on G-dP/dG plot:**
- Straight line through origin on G * dP/dG vs G: normal fluid loss, closure at deviation
- Concave up: fracture tip extension after shut-in (pressure-dependent leakoff)
- Concave down: fracture height recession or complex geometry

```python
import math

def g_function(t_shutin, t_pump):
    """Calculate G-function value at a given shut-in time."""
    dt_D = t_shutin / t_pump
    G = (4/3) * ((1 + dt_D)**1.5 - dt_D**1.5 - 1)
    return G

# Generate G-function table for t_pump = 45 min
t_pump = 45.0  # minutes
print("t_shutin (min) | G-function")
print("-" * 30)
for t in [0, 5, 10, 15, 20, 30, 45, 60, 90, 120]:
    G = g_function(t, t_pump)
    print(f"{t:14.0f} | {G:.4f}")
```

---

## Module 2 — PKN (Perkins-Kern-Nordgren) Model

### Capabilities

- Fracture half-length as a function of injection time and rate
- Maximum and average fracture width at wellbore
- Fracture volume and surface area
- Sensitivity to formation properties and fluid viscosity
- Valid when: fracture half-length x_f >> fracture height h (long, thin fractures)

### PKN Governing Equations

The PKN model assumes a fixed elliptical vertical cross-section and
plane strain in the horizontal direction.

**Plane-strain modulus:**
```
E' = E / (1 - nu^2)
```

**Fracture half-length (PKN, simplified Carter/Kemp form for constant rate Q):**
```
x_f(t) = [E' * Q * t / (2 * mu * h^2)]^(1/4)  [in consistent SI or field units]
```

Note: This is the time-dependent propagation estimate assuming no fluid loss.
With fluid loss (efficiency eta < 1), multiply the injected volume by eta before
computing the fracture volume.

**Maximum wellbore width (at x=0):**
```
w_max = 2.52 * (mu * Q * x_f / E')^(1/4)
```

**Average width:**
```
w_avg = (pi/4) * w_max ≈ 0.785 * w_max
```

**Fracture volume:**
```
V_f = (pi/4) * w_max * 2 * h * x_f  =  pi/2 * w_max * h * x_f
```

### Workflow — PKN Fracture Geometry

1. Inputs: E (Young's modulus), nu (Poisson's ratio), Q (injection rate),
   mu (fluid viscosity), h (fracture height), t (injection time)
2. Compute E' = E/(1-nu^2)
3. Estimate x_f from propagation equation
4. Compute w_max and w_avg
5. Compute V_f; check V_f <= Q*t (material balance)
6. Adjust for fluid efficiency if C_L is known

### Example — Marcellus Slickwater PKN Calculation

**Typical Appalachian/Marcellus inputs for slickwater:**
- E = 30 GPa = 4,351,000 psi (Marcellus shale)
- nu = 0.25
- Q = 50 bbl/min = 3.15 ft^3/s
- mu = 1 cp = 0.001 Pa-s (slickwater ≈ water)
- h = 150 ft = 45.7 m (fracture height, net pay)
- Injection time: 90 min (single stage)

```python
import math

# ---- SI UNITS THROUGHOUT ----
E_pa = 30e9         # Pa
nu = 0.25
Q_m3s = 50 * 0.1590 / 60  # bbl/min -> m^3/s   (1 bbl = 0.1590 m^3)
mu_pas = 0.001      # Pa-s (slickwater)
h_m = 150 * 0.3048  # ft -> m
t_s = 90 * 60       # minutes -> seconds

# Plane-strain modulus
E_prime = E_pa / (1 - nu**2)
print(f"E' (plane-strain modulus): {E_prime/1e9:.2f} GPa")

# PKN fracture half-length (no fluid loss assumed)
# From Nordgren (1972): x_f = [E'*Q*t / (2*mu*h^2)]^(1/4)
x_f_m = (E_prime * Q_m3s * t_s / (2 * mu_pas * h_m**2))**0.25
x_f_ft = x_f_m / 0.3048
print(f"\nFracture half-length: {x_f_m:.1f} m = {x_f_ft:.0f} ft")

# Maximum wellbore width
w_max_m = 2.52 * (mu_pas * Q_m3s * x_f_m / E_prime)**0.25
w_max_in = w_max_m / 0.0254
print(f"Max wellbore width (w_max): {w_max_m*1000:.2f} mm = {w_max_in:.3f} in")

# Average width
w_avg_m = (math.pi / 4) * w_max_m
w_avg_in = w_avg_m / 0.0254
print(f"Average fracture width: {w_avg_m*1000:.2f} mm = {w_avg_in:.4f} in")

# Fracture volume
V_f_m3 = (math.pi / 2) * w_max_m * h_m * x_f_m
V_f_bbl = V_f_m3 / 0.1590
V_injected_bbl = Q_m3s / 0.1590 * 60 * t_s / 60  # Q in bbl/min * time in min
print(f"\nFracture volume: {V_f_m3:.1f} m^3 = {V_f_bbl:.0f} bbl")
print(f"Total injected volume: {V_injected_bbl:.0f} bbl")
fluid_eff = V_f_bbl / V_injected_bbl
print(f"Implied fluid efficiency: {fluid_eff:.0%}")
print("(>100% is non-physical — need to include fluid loss in propagation model)")
```

### PKN Sensitivity Table

Typical PKN output for Marcellus slickwater at 90-min injection:

| Parameter | Low | Base | High |
|-----------|-----|------|------|
| E (GPa) | 20 | 30 | 40 |
| Q (bbl/min) | 30 | 50 | 80 |
| h (ft) | 100 | 150 | 200 |
| mu (cp) | 0.5 | 1 | 5 |
| x_f result (ft) | 500 | 800 | 1,400 |
| w_max result (in) | 0.04 | 0.07 | 0.15 |

---

## Module 3 — KGD (Khristianovic-Geertsma-de Klerk) Model

### Capabilities

- Fracture geometry for near-wellbore, height-dominated fractures
- Compares to PKN for model selection
- Valid when: fracture height h >> fracture half-length x_f

### KGD Governing Equations

The KGD model assumes plane strain in the vertical direction and a rectangular
cross-section that is constant along the fracture length.

**Fracture half-length (KGD):**
```
x_f(t) = [E' * Q^3 * t^3 / (16 * mu * h^2)]^(1/6)
```

**Maximum fracture width at wellbore:**
```
w_wb = 2.36 * (mu * Q * x_f / E')^(1/3)
```

**Average width:**
```
w_avg = (pi/4) * w_wb
```

### Model Selection Guide

| Condition | Preferred Model |
|-----------|----------------|
| x_f >> h (long, thin fracture) | PKN |
| h >> x_f (short, height-dominated) | KGD |
| x_f ~ h (transitional) | Neither is rigorous; use numerical |
| All cases for design | Numerical simulator (preferred) |

**Appalachian Marcellus context:** Large slickwater stages (50-90 bbl/min,
1,500+ bbl/stage) tend toward PKN geometry. Mini-fracs and diagnostic injections
may be better represented by KGD early in treatment.

```python
import math

def kgd_geometry(E_pa, nu, Q_m3s, mu_pas, h_m, t_s):
    """KGD fracture geometry. SI units throughout."""
    E_prime = E_pa / (1 - nu**2)
    x_f = (E_prime * Q_m3s**3 * t_s**3 / (16 * mu_pas * h_m**2))**(1/6)
    w_wb = 2.36 * (mu_pas * Q_m3s * x_f / E_prime)**(1/3)
    w_avg = (math.pi / 4) * w_wb
    return x_f, w_wb, w_avg

# KGD near-wellbore diagnostic injection (5 bbl/min, 10 min, h=150 ft)
E_pa = 30e9; nu = 0.25
Q_m3s = 5 * 0.1590 / 60   # 5 bbl/min
mu_pas = 0.001
h_m = 150 * 0.3048
t_s = 10 * 60

x_f, w_wb, w_avg = kgd_geometry(E_pa, nu, Q_m3s, mu_pas, h_m, t_s)
print(f"KGD model:")
print(f"  x_f = {x_f/0.3048:.0f} ft, w_wb = {w_wb*1000:.2f} mm = {w_wb/0.0254:.4f} in")
print(f"  w_avg = {w_avg*1000:.2f} mm")
print(f"  h/x_f ratio = {h_m/x_f:.2f} {'(KGD valid: h>>x_f)' if h_m/x_f > 2 else '(PKN may be more appropriate)'}")
```

---

## Module 4 — Fluid Efficiency and Fluid Loss

### Capabilities

- Fluid efficiency calculation from injection and fracture volumes
- Carter fluid loss coefficient C_L
- Pad volume requirement for target efficiency
- G-function spurt loss estimation
- PNGE 341 fluid loss coefficient derivation

### Fluid Efficiency

```
eta = V_fracture / V_injected
```

| Efficiency Range | Interpretation |
|-----------------|----------------|
| eta > 0.7 | Low leakoff (tight shale, minimal fluid loss) |
| eta = 0.4-0.7 | Moderate leakoff (typical Marcellus slickwater) |
| eta < 0.4 | High leakoff (high-perm or naturally fractured rock) |

**For Marcellus slickwater:** eta ≈ 0.4-0.6 is typical due to reactivation
of natural fractures and interaction with adjacent shale laminae.

### Carter Fluid Loss

The Carter model describes fluid loss through the fracture face as a function
of leakoff area and time:

```
dV_L/dA = C_L / sqrt(t - tau)
```

Integrated: total leakoff volume:
```
V_L = 2 * A_frac * C_L * sqrt(t)    (simplified, no spurt)
```

With spurt loss S_p (volume per unit area lost instantly when new fracture area is created):
```
V_L = 2 * A_frac * C_L * sqrt(t) + S_p * A_frac
```

**Typical C_L values (slickwater in shale):**
- 0.0001 - 0.001 ft/sqrt(min): low leakoff shale (Marcellus, Utica)
- 0.001 - 0.005 ft/sqrt(min): moderate leakoff
- 0.005 - 0.01 ft/sqrt(min): high leakoff (carbonates, highly fractured)

### Pad Volume Design

To achieve target efficiency eta_target, the pad fraction (fraction of total
volume that is pad fluid) is:

```
V_pad / V_total = (1 - eta_target) / (1 + eta_target)    (Nolte's equation)
```

```python
def pad_fraction(eta_target):
    """
    Calculate required pad fraction for a target fluid efficiency.
    eta_target: desired efficiency at end of job (0-1)
    """
    f_pad = (1 - eta_target) / (1 + eta_target)
    return f_pad

# Design table: pad fraction vs target efficiency
print("Target Efficiency | Pad Fraction | Pad % of Total Volume")
print("-" * 55)
for eta in [0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]:
    fp = pad_fraction(eta)
    print(f"{eta:17.1%} | {fp:12.3f} | {fp:20.1%}")
```

### Nolte G-Function for Fluid Loss

From G-function analysis (Module 1), the slope of the straight-line portion
on G * dP/dG vs G gives the fluid loss coefficient:

```
C_L = -slope_GPDG * sqrt(pi * Q / (16 * E' * h * t_p))  [consistent SI]
```

This is computed during post-frac analysis from the actual pressure fall-off data.

---

## Module 5 — Proppant Transport and Pack Design

### Capabilities

- Stokes settling velocity for proppant in fracturing fluid
- Hindered settling correction for proppant concentration
- Propped fracture conductivity (k_f * w_f)
- Dimensionless fracture conductivity F_cd and optimization
- Proppant schedule design (ramped concentration)

### Stokes Settling Velocity

For a single proppant grain in fluid at low Reynolds number:

```
v_s = d_p^2 * (rho_p - rho_f) * g / (18 * mu)   [SI: m/s]
```

Where:
- d_p = particle diameter (m)
- rho_p = proppant density (kg/m^3)
- rho_f = fluid density (kg/m^3)
- g = 9.81 m/s^2
- mu = fluid viscosity (Pa-s)

**Field unit version (v_s in ft/s):**
```
v_s = 0.000267 * d_p_in^2 * (SG_p - SG_f) / mu_cp
```

Where d_p_in is proppant diameter in inches, SG is specific gravity.

### Typical Proppant Properties

| Proppant Type | SG | d_p (in) | Crush Strength |
|---------------|-----|----------|----------------|
| Ottawa 20/40 sand | 2.65 | 0.0331 | 4,000 psi |
| Resin-coated sand | 2.65 | 0.0331 | 6,000 psi |
| Lightweight ceramic | 2.71 | 0.025 | 10,000 psi |
| Intermediate ceramic | 3.27 | 0.025 | 14,000 psi |
| Bauxite | 3.6 | 0.020 | 20,000 psi |

### Settling Velocity Example

```python
import math

def stokes_settling_field(d_p_in, SG_p, SG_f, mu_cp):
    """
    Stokes settling velocity in field units.
    d_p_in: proppant diameter in inches
    SG_p, SG_f: specific gravity of proppant and fluid
    mu_cp: fluid viscosity in cp
    Returns: v_s in ft/min
    """
    # Convert to SI
    d_p_m = d_p_in * 0.0254
    rho_p = SG_p * 1000  # kg/m^3
    rho_f = SG_f * 1000
    mu_pas = mu_cp * 0.001
    g = 9.81

    v_s_ms = d_p_m**2 * (rho_p - rho_f) * g / (18 * mu_pas)
    v_s_ftmin = v_s_ms * 3.281 * 60  # m/s to ft/min
    return v_s_ms, v_s_ftmin

# Proppant comparison in slickwater vs cross-linked gel
print("Proppant Settling Velocity Comparison")
print("-" * 65)
fluids = [("Slickwater", 1.0, 1.0), ("Linear gel", 50, 1.01), ("X-link gel", 500, 1.02)]
proppants = [("20/40 Ottawa sand", 0.0331, 2.65), ("20/40 Ceramic", 0.025, 3.27)]

for p_name, d_p, SG_p in proppants:
    print(f"\n{p_name}:")
    for f_name, mu_cp, SG_f in fluids:
        v_ms, v_ftmin = stokes_settling_field(d_p, SG_p, SG_f, mu_cp)
        print(f"  {f_name:15s} (mu={mu_cp:4.0f} cp): {v_ftmin:.3f} ft/min = {v_ms*1000:.2f} mm/s")
```

### Hindered Settling (Richardson-Zaki)

At proppant volume concentrations above ~5%, grains interfere:

```
v_hindered = v_s * (1 - phi_p)^n
```

Where phi_p = proppant volume fraction, n ≈ 4.65 for Re < 0.2 (Stokes regime).

### Propped Fracture Conductivity

Conductivity of the proppant pack:
```
F_c = k_f * w_f    (md-ft or md-in, depending on convention)
```

Where k_f = proppant pack permeability (md), w_f = propped fracture width (in).

**Kozeny-Carman permeability for proppant pack:**
```
k_f = d_p^2 * phi_p^3 / (180 * (1 - phi_p)^2)   [m^2, d_p in m]
```

Convert: 1 m^2 = 1.013e15 md.

Typical proppant pack k_f values (at low stress):
- Ottawa 20/40 sand: 200,000 - 400,000 md
- Ceramic 20/40: 300,000 - 500,000 md
- At 7,000 psi closure: Ottawa sand drops to ~50,000-150,000 md (embedment/crush)

### Dimensionless Fracture Conductivity

The dimensionless fracture conductivity determines whether the fracture is
effectively infinite-conductivity (IFC) or finite-conductivity:

```
F_cd = k_f * w_f / (k * x_f)
```

Where k = formation permeability (md), x_f = fracture half-length (ft).

| F_cd Value | Fracture Performance | Recommendation |
|------------|---------------------|----------------|
| F_cd < 1 | Severely limited by fracture conductivity | Increase proppant concentration or use higher-k proppant |
| F_cd = 1-10 | Finite conductivity — production limited by fracture | Optimize; increase conductivity if economic |
| F_cd ≈ 10 | Near-optimal for many cases (Cinco-Ley) | Good design target |
| F_cd > 100 | Effectively infinite conductivity | Formation permeability is the limit |

**Marcellus context:** With k ≈ 0.0001-0.001 md, x_f ≈ 500-1,000 ft, and
k_f*w_f ≈ 500-2,000 md-ft, F_cd ranges from 500-20,000 — effectively
infinite conductivity. Conductivity is rarely the limiting factor in ultralow-perm shale.

```python
def dimensionless_conductivity(k_f_md, w_f_in, k_md, x_f_ft):
    """Calculate dimensionless fracture conductivity."""
    w_f_ft = w_f_in / 12
    F_cd = (k_f_md * w_f_ft) / (k_md * x_f_ft)
    if F_cd < 1:
        assess = "POOR — fracture conductivity limiting"
    elif F_cd < 10:
        assess = "FINITE conductivity — optimize"
    elif F_cd < 100:
        assess = "NEAR-OPTIMAL"
    else:
        assess = "EFFECTIVELY infinite conductivity"
    return F_cd, assess

# Marcellus example
F_cd, note = dimensionless_conductivity(
    k_f_md=100000, w_f_in=0.2, k_md=0.0005, x_f_ft=800
)
print(f"F_cd = {F_cd:.0f}: {note}")
```

### Proppant Schedule Design

A ramped proppant schedule (starting with pad, then increasing concentration)
maintains transport efficiency and prevents premature screen-out:

**Typical Marcellus slickwater schedule (1,500 bbl total):**

| Stage | Volume (bbl) | Proppant Conc. (ppg) | Proppant (lb) |
|-------|-------------|---------------------|---------------|
| Pad (slickwater) | 500 | 0 | 0 |
| 0.25 ppg | 200 | 0.25 | 10,500 |
| 0.50 ppg | 200 | 0.50 | 21,000 |
| 0.75 ppg | 200 | 0.75 | 31,500 |
| 1.0 ppg | 150 | 1.00 | 25,200 |
| Flush | 150 | 0 | 0 |
| **Total** | **1,400** | — | **88,200** |

Where ppg = pounds of proppant per gallon of fluid.

---

## Module 6 — Nolte-Smith Pressure Diagnostics

### Capabilities

- Log-log treating pressure plot construction and interpretation
- Pressure derivative analysis for fracture mode identification
- Fracture containment assessment
- Extension vs. height growth diagnosis

### Nolte-Smith Log-Log Plot

Plot log(p_net) vs log(time) during injection to diagnose fracture behavior:

| Log-Log Slope | Fracture Behavior | Interpretation |
|--------------|-------------------|----------------|
| Slope = 0 | Constant net pressure | Normal fracture extension (PKN-like) |
| Slope = +1/8 to +1/4 | Gently increasing | Slightly restricted tip extension |
| Slope = +1 | Rapidly increasing | Restricted height growth, tip screenout, or high fluid loss |
| Slope = -1/4 to -1/2 | Decreasing | Height growth without length (T-shaped fracture) |
| Slope = -1 | Rapidly decreasing | Unrestricted fracture height growth out of zone |
| Abrupt spike | Sharp increase | Near-wellbore screen-out or perforation plugging |

**Procedure:**
1. Calculate bottomhole treating pressure (BHTP) at each time step:
   BHTP = surface treating pressure + hydrostatic head - friction losses
2. Calculate net pressure: p_net = BHTP - P_c (use ISIP-estimated closure)
3. Plot log(p_net) vs log(injection time)
4. Compute log-log slope over rolling window; identify trend

```python
import math

def nolte_smith_slope(times, p_net_values):
    """
    Compute log-log slope between consecutive points on Nolte-Smith plot.
    times: list of injection times (min)
    p_net_values: list of net pressures (psi)
    Returns: list of (time_mid, slope) tuples
    """
    slopes = []
    for i in range(1, len(times)):
        if times[i] > 0 and times[i-1] > 0 and p_net_values[i] > 0 and p_net_values[i-1] > 0:
            d_log_t = math.log10(times[i]) - math.log10(times[i-1])
            d_log_p = math.log10(p_net_values[i]) - math.log10(p_net_values[i-1])
            if abs(d_log_t) > 1e-10:
                slope = d_log_p / d_log_t
                t_mid = math.sqrt(times[i] * times[i-1])  # geometric mean
                slopes.append((t_mid, slope))
    return slopes

# Example treating pressure data (synthetic Marcellus stage)
times_min = [1, 5, 10, 20, 30, 45, 60, 75, 90]
p_net_psi  = [200, 250, 300, 320, 340, 350, 380, 450, 700]

slopes = nolte_smith_slope(times_min, p_net_psi)
print("t_mid (min) | Log-Log Slope | Interpretation")
print("-" * 55)
for t, s in slopes:
    if s < -0.5:
        interp = "Height growth (out of zone)"
    elif s < 0:
        interp = "Height recession or T-shape"
    elif s < 0.125:
        interp = "Normal PKN extension"
    elif s < 0.5:
        interp = "Restricted extension"
    else:
        interp = "Restricted / near screen-out"
    print(f"{t:11.1f} | {s:13.3f} | {interp}")
```

---

## Workflow Summary

### Step 1 — Identify Calculation Type

| User Request | Module |
|--------------|--------|
| Closure pressure, ISIP, net pressure, stress gradient | Module 1 — Closure |
| Fracture length, width (PKN) | Module 2 — PKN |
| Near-wellbore fracture geometry (KGD) | Module 3 — KGD |
| Fluid efficiency, fluid loss, pad design | Module 4 — Fluid Efficiency |
| Proppant settling, conductivity, F_cd, schedule | Module 5 — Proppant |
| Treating pressure analysis, log-log slope | Module 6 — Nolte-Smith |

### Step 2 — Gather Inputs

Collect required parameters. Default to Marcellus/Appalachian typical values
when user omits inputs. Always state assumptions explicitly.

**Default Marcellus/Appalachian parameters:**

| Parameter | Symbol | Typical Value | Unit |
|-----------|--------|---------------|------|
| Young's modulus | E | 30 | GPa |
| Poisson's ratio | nu | 0.25 | — |
| Fracture height | h | 150 | ft |
| Injection rate | Q | 50 | bbl/min |
| Fluid viscosity (slickwater) | mu | 1 | cp |
| Closure pressure gradient | p_c/z | 0.70 | psi/ft |
| Formation permeability | k | 0.0005 | md |
| Depth (Marcellus, WV) | TVD | 7,000-8,500 | ft |

### Step 3 — Calculate

Use Python (stdlib: math, statistics). Work in SI for calculations, then
convert final answers to both field and SI units. Show every step.

### Step 4 — Output

1. **Input parameters table** — all values with units and source (user/default)
2. **Step-by-step calculation** — equations, substitutions, intermediate results
3. **Results table** — computed values in field and SI units
4. **Design interpretation** — is the design adequate? What controls performance?
5. **Caveats** — model validity range, simplifying assumptions, when to use full simulator

---

## Output Format

```
## [Calculation Title]

### Input Parameters
| Parameter | Symbol | Value | Unit | Source |
|-----------|--------|-------|------|--------|
| ... | ... | ... | ... | User / Marcellus default |

### Governing Model: [PKN / KGD / Nolte-Smith / etc.]
[State why this model applies and its validity conditions]

### Calculations
Step 1: [equation name and formula]
  [substituted values with units -> result with units]

### Results
| Property | Value (Field) | Value (SI) |
|----------|--------------|------------|
| ... | ... | ... |

**Summary:** [2-3 sentences on fracture geometry and design adequacy]

**Caveats:**
- [Model validity: e.g., "PKN valid only when x_f >> h"]
- [Key assumption: e.g., "No fluid loss assumed — actual x_f will be shorter"]
- [Recommend numerical simulation for final stage design]
```

---

## Error Handling

| Condition | Action |
|-----------|--------|
| Fluid efficiency > 1 | Non-physical; check if fluid loss is excluded — warn and restate |
| x_f ~ h (PKN/KGD boundary) | Warn that neither model is rigorous; recommend Penny-shaped or numerical |
| F_cd < 1 | Flag as conductivity-limited design; suggest higher proppant or rate |
| Settling velocity > fracture propagation velocity | Warn of possible proppant bridging; suggest higher viscosity fluid |
| Missing formation properties | List missing values; use documented Marcellus/Appalachian ranges |

---

## Units Reference

| Quantity | Field Unit | SI Unit | Conversion |
|----------|-----------|---------|------------|
| Pressure | psi | MPa | 1 psi = 0.006895 MPa |
| Modulus | psi | GPa | 1e6 psi = 6.895 GPa |
| Rate | bbl/min | m^3/s | 1 bbl/min = 2.65e-3 m^3/s |
| Viscosity | cp | Pa-s | 1 cp = 0.001 Pa-s |
| Length | ft | m | 1 ft = 0.3048 m |
| Width | in or mm | m | 1 in = 0.0254 m |
| Permeability | md | m^2 | 1 md = 9.869e-16 m^2 |
| Conductivity | md-ft | md-m | 1 md-ft = 0.3048 md-m |
| Proppant conc. | ppg | kg/m^3 | 1 ppg = 119.8 kg/m^3 |
| C_L | ft/sqrt(min) | m/sqrt(s) | 1 ft/min^0.5 = 0.0548 m/s^0.5 |

See `references/equations.md` for full derivation context and field-unit forms.
