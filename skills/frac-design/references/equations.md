# Hydraulic Fracture Design — Equation Reference

Complete equation library for the frac-design skill. Includes derivation
context, variable definitions, and field-unit conversions. Organized by module.

---

## Module 1 — Closure Pressure and Stress State

### Key Pressure Definitions

| Symbol | Name | Definition |
|--------|------|------------|
| P_bd | Breakdown pressure | Wellbore pressure at which fracture initiates; exceeds S_hmin + T_0 |
| ISIP | Instantaneous shut-in pressure | Wellbore pressure immediately after pumps stop; closest measurable approximation to P_c |
| P_c | Fracture closure pressure | Pressure at which fracture walls contact proppant; equals S_hmin for a vertical fracture |
| p_net | Net treating pressure | p_bh_treating - P_c; drives fracture propagation |
| S_hmin | Minimum horizontal stress | Fracture closure pressure for a vertical fracture in normal or strike-slip regime |
| T_0 | Tensile strength | Fracture initiation requires P_wf > S_hmin + T_0; T_0 = 100-1,000 psi for rock |

### ISIP to Closure Relationship

ISIP slightly exceeds P_c because net pressure does not instantaneously drop
to zero upon shut-in. The pressure fall-off from ISIP to P_c follows:

```
P_c = ISIP - delta_p_residual
```

Where delta_p_residual = 30-150 psi (typical; depends on fluid viscosity and
fracture geometry). For slickwater: delta_p_residual ≈ 30-80 psi.

For a more precise P_c, use G-function analysis of the pressure fall-off.

### G-Function (Nolte, 1979)

The G-function normalizes shut-in time to remove the injection-duration effect:

```
G(Delta_t_D) = (4/3) * [(1 + Delta_t_D)^(3/2) - Delta_t_D^(3/2) - 1]
```

Where:
- Delta_t_D = Delta_t / t_p (dimensionless shut-in time)
- Delta_t = elapsed time after pump-off (min)
- t_p = pump time (min)

**G-function interpretation:**

On a plot of G * (dP/dG) vs G, the pressure during normal (Carter leakoff) fall-off
follows a straight line through the origin. The closure pressure P_c is identified
as the deviation from this straight line.

The slope m of the straight-line portion gives the fluid loss coefficient:
```
C_L = m * sqrt(pi / (E' * h * t_p * Q))    [consistent units]
```

### Net Pressure

```
p_net = P_bh - P_c
```

Where P_bh = bottomhole treating pressure (BHTP):
```
P_bh = P_surface + P_hydrostatic - P_friction_tubular
P_hydrostatic = gradient * TVD
P_friction_tubular = friction pressure in pipe (from flow rate and fluid rheology)
```

**Typical p_net values:**
- Slickwater fracture (Marcellus): 100-400 psi
- Linear gel fracture: 300-800 psi
- Cross-linked gel fracture: 500-2,000 psi

Higher net pressure drives greater fracture width; lower net pressure gives
longer, narrower fractures.

### Bottomhole Fracturing Pressure

At fracture initiation, the wellbore pressure must overcome the minimum principal
stress plus tensile strength:
```
P_bd = S_hmin + T_0 + some_additional_terms    (for a natural fracture, T_0 = 0)
```

For a virgin (no pre-existing fractures) vertical fracture in a horizontal
minimum stress field:
```
P_bd = 3*S_hmin - S_Hmax - P_p + T_0
```

This is the Hubbert-Willis (1957) breakdown pressure equation.

---

## Module 2 — PKN (Perkins-Kern-Nordgren) Model

### Model Geometry and Validity

The PKN model (Perkins and Kern, 1961; Nordgren, 1972) assumes:
- Vertical fracture with fixed height h
- Elliptical cross-section (vertical plane) at each horizontal position x
- Plane strain condition in the horizontal direction (x-z plane)
- Fracture half-length x_f >> fracture height h

This produces a "blade-like" fracture that is long relative to its height.

### Governing Equations (Nordgren, 1972)

The governing partial differential equation for fracture width w(x,t):
```
dw/dt = E'/(64*mu) * d/dx(w^3 * dw/dx) - 2*C_L/sqrt(t-tau(x))
```

Where tau(x) is the time at which the fracture front arrived at x.

For the simplified case of no fluid loss (C_L = 0, constant injection rate Q):

**Fracture half-length:**
```
x_f(t) = 0.68 * (E'^3 * Q^3 * t^4 / (mu^3 * h^4))^(1/5)    [SI: m, Pa, m^3/s, Pa-s, m]
```

Alternative simplified form for scoping:
```
x_f ≈ [E' * Q * t / (2 * mu * h^2)]^(1/4)    [approximation, consistent SI units]
```

**Note on the exponent:** The exact Nordgren solution gives x_f ~ t^(4/5), while
the simpler scaling above gives x_f ~ t^(1/4). The Nordgren form is more accurate.

**Maximum width at wellbore (x = 0):**
```
w_0(t) = 2.52 * (mu * Q * x_f / E')^(1/4)    [SI: m]
```

**Average width:**
```
w_avg = (pi/4) * w_0 ≈ 0.785 * w_0
```

**Fracture volume (no fluid loss):**
```
V_frac = (pi/4) * w_0 * 2 * h * x_f = (pi/2) * w_0 * h * x_f
```

This should equal Q * t (material balance check). The discrepancy
indicates fluid loss.

### Plane-Strain Modulus

```
E' = E / (1 - nu^2)
```

Where E = Young's modulus, nu = Poisson's ratio.

For Marcellus shale: E = 20-45 GPa (median ~30 GPa), nu = 0.2-0.28 (median ~0.25).
Thus E' ≈ 31.9 GPa for base-case Marcellus.

### PKN Pressure Distribution

The net pressure along the fracture in a PKN geometry:
```
p_net(x) = p_net(0) * (1 - x/x_f)^(1/4)
```

At the wellbore:
```
p_net(0) = 0.53 * (mu * Q * E'^3 / h^4)^(1/5) * t^(1/5)
```

This gives a Nolte-Smith log-log slope of +1/5 ≈ +0.2 for PKN geometry
during constant-rate injection.

---

## Module 3 — KGD (Khristianovic-Geertsma-de Klerk) Model

### Model Geometry and Validity

The KGD model (Khristianovic and Zheltov, 1955; Geertsma and de Klerk, 1969) assumes:
- Vertical fracture with fixed height h
- Plane strain condition in the vertical direction (x-y plane)
- Fracture width constant along the height at any x position
- Valid for h >> x_f (height >> length, near-wellbore regime)

### Governing Equations

**Fracture half-length:**
```
x_f(t) = 0.48 * (E' * Q^3 * t^3 / (mu * h^2))^(1/6)    [SI]
```

Simplified scaling form:
```
x_f ≈ [E' * Q^3 * t^3 / (16 * mu * h^2)]^(1/6)
```

**Width at wellbore:**
```
w_wb = 2.36 * (mu * Q * x_f / E')^(1/3)    [SI: m]
```

**Average width (uniform along height, elliptical along length):**
```
w_avg = (pi/4) * w_wb
```

**Fracture volume:**
```
V_frac = (pi/4) * w_wb * h * x_f
```

### KGD Net Pressure (at wellbore)

```
p_net_KGD = (E' * w_wb) / (2 * x_f)   [from plane strain relationship]
```

Nolte-Smith log-log slope for KGD: approaches 0 (constant) — similar to PKN
at early time, but tends toward lower values as h/x_f increases.

### PKN vs KGD Comparison

| Feature | PKN | KGD |
|---------|-----|-----|
| Validity | x_f >> h | h >> x_f |
| Fracture tip | Blunt (rounded) | Sharp (crack-like) |
| Width profile | Elliptical cross-section (varying with x) | Uniform along height, elliptical plan view |
| Width scales with | (Q * x_f)^(1/4) | (Q * x_f)^(1/3) |
| Net pressure trend | Increases slowly (slope ~1/5) | Essentially flat |
| Preferred application | Large slickwater stages in shale | Mini-frac diagnostic injections |

---

## Module 4 — Fluid Efficiency and Fluid Loss

### Carter Fluid Loss Model (Howard and Fast, 1957)

The rate of fluid loss per unit fracture face area at time t after the fracture
face was created at time tau:

```
dV_L / dA = C_L / sqrt(t - tau)    [m^3/m^2/s^0.5 or ft^3/ft^2/min^0.5]
```

Total leakoff volume (both faces, no spurt):
```
V_L = 2 * C_L * integral[A(t, tau) / sqrt(t-tau) dA]
```

For a simplified constant fracture area A (late-time approximation):
```
V_L = 2 * A * C_L * 2 * sqrt(t/pi)    [Carter simplified]
```

### Carter Leakoff Coefficient (Three-Mechanism Model)

Three mechanisms contribute to C_L in series (Howard and Fast):
```
1/C_L = 1/C_I + 1/C_II + 1/C_III
```

**Mechanism I — Wall-building filter cake:**
```
C_I = k_fc^0.5 * Delta_p_fc^0.5 / (mu_fc * phi)^0.5
```

**Mechanism II — Filtrate viscosity in formation:**
```
C_II = (k * phi * mu_c * Delta_p_total / (pi * mu_f))^0.5 / (2 * (phi * mu_c / mu_f)^0.5)
```

**Mechanism III — Reservoir compressibility:**
```
C_III = (phi * k * c_t / (pi * mu_f))^0.5 * Delta_p^0.5
```

In practice, C_L is estimated from mini-frac/step-rate test analysis, not
directly from the three-mechanism formula.

**Typical C_L values:**
- Tight shale (Marcellus): 0.0001-0.0005 ft/min^0.5
- Moderate shale: 0.0005-0.002 ft/min^0.5
- Tight gas sand: 0.001-0.005 ft/min^0.5
- Moderate permeability reservoir: 0.005-0.02 ft/min^0.5

### Spurt Loss

Spurt loss S_p (volume per unit fracture face area) occurs instantly when a
new fracture face is created, before the filter cake builds:
```
V_spurt = S_p * A_frac    [m^3 or ft^3]
```

For slickwater in tight shale: S_p ≈ 0 (negligible).
For cross-linked gel in higher-perm formation: S_p ≈ 0.01-0.05 gal/ft^2.

### Fluid Efficiency

```
eta = V_frac / V_injected
```

Where V_frac includes both fracture volume and spurt loss:
```
V_injected = V_frac + V_leakoff + V_spurt
```

**Nolte's pad volume equation:**
The fraction of total job volume that must be pad (to achieve target efficiency):
```
V_pad / V_total = (1 - eta_target) / (1 + eta_target)
```

This assumes eta stays roughly constant through the job (Nolte's simplification).

### G-Function Fluid Loss Coefficient

From G-function analysis of pressure fall-off:
```
C_L = -m * (pi / (16 * E'))^0.5 * sqrt(h * t_p * Q)^(-1)
```

Or equivalently:
```
C_L = -m / (2 * E' * sqrt(t_p) * (pi * h / Q)^0.5)
```

Where m = slope of straight-line portion of G * dP/dG vs G plot.

---

## Module 5 — Proppant Transport and Pack Design

### Stokes Settling Velocity (Single Particle)

For a spherical proppant grain in a viscous fluid at low Reynolds number (Re < 1):

**SI form:**
```
v_s = d_p^2 * (rho_p - rho_f) * g / (18 * mu)    [m/s]
```

**Field unit form:**
```
v_s (ft/s) = d_p^2 (in^2) * (SG_p - SG_f) * 32.2 / (18 * mu (lb-s/ft^2))
```

Simplified field unit approximation:
```
v_s (ft/min) ≈ 0.892 * d_p (in)^2 * (SG_p - SG_f) / mu (cp)
```

### Reynolds Number Check

The Stokes law is valid for Re < 1. For larger particles, use corrections:
```
Re = rho_f * v_s * d_p / mu
```

If Re > 1 but < 1000, use the intermediate law:
```
v_s = (d_p^1.14 * (rho_p - rho_f)^0.714 * g^0.714) / (13.9 * rho_f^0.286 * mu^0.428)
```

For 20/40 Ottawa sand (d_p = 0.033 in = 0.84 mm) in 1 cp water:
- Stokes: Re ~ 0.5 → Stokes law approximately valid
- In 50 cp gel: Re << 1 → Stokes law valid

### Hindered Settling (Richardson-Zaki Correlation)

For proppant volume fractions phi_p > 0.05 (concentrated slurry):
```
v_hindered = v_s * (1 - phi_p)^n
```

Where n (Richardson-Zaki exponent):
- n ≈ 4.65 for Re < 0.2 (Stokes regime)
- n ≈ 4.35 for Re ≈ 1
- n ≈ 2.39 for Re > 500

### Proppant Volume Fraction from Concentration

Field proppant concentration is typically given as pounds of proppant per
gallon of fluid (ppg). Volume fraction:
```
phi_p = C_ppg / (SG_p * 8.33 + C_ppg)    (approximate)
```

Where SG_p = proppant specific gravity, C_ppg = concentration in lb/gal.

At 2 ppg 20/40 sand (SG = 2.65) in water:
```
phi_p = 2 / (2.65 * 8.33 + 2) = 2 / (22.08 + 2) = 0.083 = 8.3%
```

At 4 ppg: phi_p ≈ 15%. At 6 ppg: phi_p ≈ 21%.

### Kozeny-Carman Permeability of Proppant Pack

For an idealized spherical-grain pack:
```
k = d_p^2 * phi_p^3 / (180 * (1 - phi_p)^2)    [SI: m^2, d_p in m]
```

Convert to md: 1 m^2 = 1.013e15 md.

For a typical 20/40 Ottawa sand pack (d_p = 0.84 mm, phi_p = 0.35):
```
k ≈ (8.4e-4)^2 * 0.35^3 / (180 * (0.65)^2) ≈ 2.6e-9 m^2 ≈ 2.6e6 md
```

Actual lab values are 150,000-400,000 md at low stress — much lower due to
packing irregularity, fines, and particle size distribution.

### Propped Fracture Conductivity

```
F_cd = k_f * w_f    [md-ft or md-in]
```

**Proppant pack width under closure stress:**
The propped width decreases from the open-fracture width due to:
- Proppant embedment into formation (soft rock: up to 50% width loss)
- Proppant crushing at high stress
- Diagenetic cementation

Rough estimate for 1.5 lb/ft^2 (= 1.5 lbm/ft^2 areal density) 20/40 sand pack:
```
w_f = (1.5 lb/ft^2) / (SG_p * 62.4 lb/ft^3 * (1-phi_p))
    = 1.5 / (2.65 * 62.4 * 0.65) ≈ 0.014 ft ≈ 0.17 in
```

### Dimensionless Fracture Conductivity

```
F_cd = k_f * w_f / (k * x_f)
```

Cinco-Ley and Samaniego (1981) showed that:
- F_cd = 1.6 gives the optimum for a given propped volume (maximum production)
  when volume of proppant is the constraint
- F_cd ≥ 10 gives behavior close to infinite conductivity fracture (IFC)
- F_cd < 0.1 is severely conductivity-limited

For Marcellus shale (k ≈ 0.0005 md, x_f ≈ 800 ft):
```
F_cd = k_f * w_f / (0.0005 * 800) = k_f * w_f / 0.4
```

To achieve F_cd = 10: k_f * w_f = 4 md-ft (easily achieved with any proppant).
In ultralow-perm shale, fracture conductivity is rarely the limiting factor.

---

## Module 6 — Nolte-Smith Pressure Diagnostics

### Nolte-Smith Log-Log Analysis (1981)

Nolte and Smith proposed plotting log(p_net) vs log(t) during injection. The
slope of this plot (d log p_net / d log t) reveals fracture behavior:

**Derivation for PKN geometry (no fluid loss):**
From Module 2, p_net ∝ t^(1/5) → log-log slope = 1/5 ≈ 0.2

But this is rarely observed. In practice, the slope reflects:

| Slope | Physical Mechanism |
|-------|-------------------|
| -1 | Unrestricted height growth (h grows without bound; p_net drops with area increase) |
| -1/4 to 0 | Height recession (T-shaped fracture; p_net decreases as fracture deflates) |
| 0 | Normal fracture extension (Nolte's ideal PKN-like behavior) |
| +1/8 to +1/4 | Restricted fracture extension (tip effect, tortuosity, near-wellbore complexity) |
| +1 | Tip screen-out (TSO) or restricted height growth with continued width increase |
| Sudden spike, slope > 1 | Near-wellbore screen-out or bridging at perforations |

### Bottomhole Treating Pressure (BHTP) Calculation

For pressure measurement at surface:
```
P_bh = P_surface + P_hydrostatic - P_friction_pipe
```

Where:
```
P_hydrostatic = 0.052 * mud_weight (ppg) * TVD (ft)
```

Pipe friction pressure (power-law model):
```
dP/dL (psi/ft) = (0.2 * K * v^n) / (144 * (d/12)^(n+1))
```

For slickwater in field units (approximate):
```
dP/dL ≈ 0.0007 * Q^0.8 / d_i^4.8   (turbulent flow, psi/ft)
```

Where Q in bbl/min, d_i in inches.

### Step-Rate Test Interpretation

Plot injection rate Q vs surface pressure P_surface at the end of each rate step.

**Extension pressure (fracture reopening):** The pressure at which the slope
of the P vs Q plot increases (from linear to less-than-linear or zero slope).

```
S_hmin ≈ P_extension - P_hydrostatic + P_friction
```

**Falloff after shut-in:** ISIP = pressure at shut-in; closure pressure from
fall-off analysis (straight line on Horner plot, or G-function analysis).

---

## Field-Unit Equation Forms

### PKN Width (Field Units)

Consistent field unit form of the maximum wellbore width (in inches):
```
w_max (in) = 0.36 * (Q (bbl/min) * mu (cp) * x_f (ft) / E' (psi))^(1/4)
```

(This is the field-unit form of w_max = 2.52 * (mu * Q * x_f / E')^(1/4) in SI.)

### PKN Length (Field Units, Simplified)

```
x_f (ft) = 3.14 * (E' (psi) * Q (bbl/min) * t (min) / (mu (cp) * h (ft)^2))^(1/4)
```

Where 3.14 is an approximate conversion constant absorbing unit conversions.

**Note:** These field-unit conversion constants vary across textbooks and
references. Always verify unit consistency. For design work, perform
calculations in consistent SI and convert final answers.

### Proppant Settling (Field Units)

```
v_s (ft/min) = 0.892 * d_p^2 (in) * (SG_p - SG_f) / mu (cp)
```

For 20/40 Ottawa sand (d_p = 0.033 in, SG_p = 2.65) in 1 cp water:
```
v_s = 0.892 * (0.033)^2 * (2.65 - 1.0) / 1.0 = 0.0016 ft/min ≈ 0.1 ft/hr
```

In 50 cp linear gel:
```
v_s = 0.0016 / 50 = 3.2e-5 ft/min = 0.002 ft/hr  (essentially negligible)
```

---

## Unit Conversion Reference

| Quantity | Field Unit | SI Unit | Conversion |
|----------|-----------|---------|------------|
| Pressure | psi | Pa | 1 psi = 6,894.76 Pa |
| Modulus | psi | Pa | 1e6 psi = 6.895e9 Pa |
| Rate | bbl/min | m^3/s | 1 bbl/min = 2.649e-3 m^3/s |
| Viscosity | cp | Pa-s | 1 cp = 0.001 Pa-s |
| Length | ft | m | 1 ft = 0.3048 m |
| Width | in | m | 1 in = 0.0254 m |
| Permeability | md | m^2 | 1 md = 9.869e-16 m^2 |
| Conductivity | md-ft | md-m | 1 md-ft = 0.3048 md-m |
| Concentration | ppg | kg/m^3 | 1 ppg = 119.83 kg/m^3 |
| C_L | ft/min^0.5 | m/s^0.5 | 1 ft/min^0.5 = 0.00508 m/s^0.5 |
| Areal density | lb/ft^2 | kg/m^2 | 1 lb/ft^2 = 4.882 kg/m^2 |

---

## Key References

- Perkins, T.K. and Kern, L.R. (1961): "Widths of hydraulic fractures,"
  JPT, September, 937-949. [Original PKN width equations]

- Nordgren, R.P. (1972): "Propagation of a vertical hydraulic fracture,"
  SPEJ, August, 306-314. [Nordgren extension — closed-form time solution]

- Geertsma, J. and de Klerk, F. (1969): "A rapid method of predicting width
  and extent of hydraulically induced fractures," JPT, December, 1571-1581. [KGD]

- Nolte, K.G. (1979): "Determination of fracture parameters from fracturing
  pressure decline," SPE 8341. [G-function derivation]

- Nolte, K.G. and Smith, M.B. (1981): "Interpretation of fracturing pressures,"
  JPT, September, 1767-1775. [Nolte-Smith log-log diagnostic]

- Cinco-Ley, H. and Samaniego, F. (1981): "Transient pressure analysis for
  fractured wells," JPT, September, 1749-1766. [Dimensionless conductivity optimization]

- Howard, G.C. and Fast, C.R. (1957): "Optimum fluid characteristics for
  fracture extension," API Drilling and Production Practice, 261-270. [Carter fluid loss]
