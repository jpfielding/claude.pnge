---
name: tnav-reservoir-sim
description: >
  Emulate tNavigator reservoir simulation workflows for PNGE students.
  Use this skill when asked to build .DATA files, run material balance,
  calculate PVT properties, do decline curve analysis, history matching,
  nodal analysis, VFP tables, IPR curves, kriging, petrophysics, or
  anything involving reservoir simulation, black oil models, compositional
  models, Arps decline, Vogel IPR, Beggs-Brill, Peng-Robinson EOS,
  Z-factor, bubble point, formation volume factor, water saturation,
  Archie equation, or sensitivity studies on reservoir parameters.
  Trigger phrases: "reservoir simulation", "build a DATA file", "PVT calc",
  "decline curve", "material balance", "history match", "nodal analysis",
  "IPR curve", "VFP table", "Z-factor", "bubble point", "Bo calc",
  "kriging", "Archie", "skin factor sensitivity", "recovery factor".
  Educational tool — not a replacement for full tNavigator or Eclipse runs.
---

# tNavigator Reservoir Simulation Emulator

Educational skill for prototyping reservoir simulation workflows, PVT
calculations, decline analysis, history matching, well design, and
petrophysical modeling. Produces calculation results, .DATA file snippets,
and sensitivity plots — all without requiring the full tNav GUI.

**Important:** This is an educational emulation tool. Results are approximate
and use standard petroleum engineering correlations. For production-grade
simulation, use tNavigator, Eclipse, or CMG with validated models.

---

## Module 1 — Black Oil and Compositional Simulation Wrapper

### Capabilities

- Generate and validate .DATA file sections (RUNSPEC, GRID, PROPS, SOLUTION, SCHEDULE)
- Material balance equations (Havlena-Odeh, Schilthuis)
- Sensitivity analysis: Pwf vs recovery factor
- Decline curve analysis (Arps: exponential, hyperbolic, harmonic)

### .DATA File Generation

Generate Eclipse/tNav-format .DATA file sections. The user provides reservoir
parameters and the skill produces formatted keyword blocks.

**Example input:**
```
Build a .DATA file for a 3D black oil model:
- Grid: 20x20x5, dx=dy=200ft, dz varies 10-30ft
- Porosity: 0.15 avg, Perm: 50 md
- Oil API: 35, GOR: 600 scf/STB
- Initial pressure: 4000 psia at 8000ft datum
- One producer, BHP limit 1500 psia
```

**Example .DATA output (partial):**
```
RUNSPEC
TITLE
  Black Oil Model — Educational Example

DIMENS
  20 20 5 /

OIL
WATER
GAS
DISGAS

FIELD

START
  1 JAN 2025 /

TABDIMS
  1 1 40 20 /

WELLDIMS
  2 5 1 2 /

-- ============================================
GRID

DX
  2000*200.0 /
DY
  2000*200.0 /
DZ
  400*10.0 400*15.0 400*20.0 400*25.0 400*30.0 /

TOPS
  400*8000.0 /

PORO
  2000*0.15 /

PERMX
  2000*50.0 /
PERMY
  2000*50.0 /
PERMZ
  2000*5.0 /
```

### Material Balance (Havlena-Odeh)

Generalized form for oil reservoirs with gas cap and water influx:

```
F = N * [Eo + m*Eg + Efw] + We
```

Where:
- F = total fluid withdrawal (underground voidage)
- N = OOIP (STB)
- Eo = oil expansion term
- Eg = gas cap expansion term
- Efw = connate water and pore compressibility term
- We = cumulative water influx
- m = ratio of initial gas cap to oil zone volume

See `references/equations.md` for full definitions.

**Workflow:**
1. User provides: Np, Gp, Wp (cumulative production), PVT data at multiple pressures
2. Calculate F and Et at each pressure step
3. Plot F vs Et — slope = N (OOIP)
4. Assess drive mechanism from plot shape

### Arps Decline Curve Analysis

Three decline models:

| Type | b value | Equation |
|------|---------|----------|
| Exponential | b = 0 | q(t) = qi * exp(-Di * t) |
| Hyperbolic | 0 < b < 1 | q(t) = qi / (1 + b*Di*t)^(1/b) |
| Harmonic | b = 1 | q(t) = qi / (1 + Di*t) |

**Workflow:**
1. User provides production history (time, rate pairs)
2. Fit exponential first (log q vs t — look for straight line)
3. If not straight, fit hyperbolic (optimize b and Di)
4. Report: qi, Di, b, EUR, remaining reserves at economic limit

### Sensitivity: Pwf vs Recovery Factor

Vary bottom-hole flowing pressure and compute recovery factor using
material balance or decline analysis:

1. Define Pwf range (e.g., 500 to 3000 psia in 250 psi steps)
2. At each Pwf, compute IPR rate, then cumulative production to abandonment
3. Report RF = Np/N at each Pwf
4. Output table and recommended operating Pwf

---

## Module 2 — PVT Designer

### Capabilities

- Z-factor: Standing-Katz (chart), Hall-Yarborough, Dranchuk-Abou-Kassem (DAK)
- Bubble point pressure: Standing, Vasquez-Beggs
- Oil FVF (Bo): Standing correlation
- Gas FVF (Bg): from Z-factor and P-T
- Water FVF (Bw): McCain correlation
- Solution GOR (Rs): Standing correlation
- Oil viscosity: Beggs-Robinson (dead oil), Vasquez-Beggs (live oil)
- Gas viscosity: Lee-Gonzalez-Eakin
- Equations of state: Peng-Robinson, SRK (for compositional work)

### Z-Factor Calculation (DAK Correlation)

The Dranchuk-Abou-Kassem correlation solves iteratively:

```
Input: Tpr (pseudo-reduced temperature), Ppr (pseudo-reduced pressure)
Output: Z-factor
```

Pseudo-critical properties from gas gravity (Standing correlations):
```
Tpc = 168 + 325*gamma_g - 12.5*gamma_g^2  (R)
Ppc = 677 + 15*gamma_g - 37.5*gamma_g^2   (psia)
Tpr = T / Tpc
Ppr = P / Ppc
```

DAK uses 11 coefficients (A1-A11) — see `references/equations.md`.

**Workflow:**
1. User provides: T (F or R), P (psia), gamma_g (gas gravity, air=1)
2. Calculate Tpc, Ppc, Tpr, Ppr
3. Iterate DAK equation for Z
4. Report Z, Bg, gas density

### Bubble Point Pressure (Standing)

```
Pb = 18.2 * ((Rs/gamma_g)^0.83 * 10^(0.00091*T - 0.0125*API) - 1.4)
```

**Workflow:**
1. User provides: Rs (scf/STB), gamma_g, T (F), API gravity
2. Calculate Pb
3. Also calculate Bo at Pb using Standing FVF correlation

### Oil Formation Volume Factor (Standing)

Below bubble point:
```
Bo = 0.9759 + 0.00012 * (Rs*(gamma_g/gamma_o)^0.5 + 1.25*T)^1.2
```

### Solution GOR (Standing)

```
Rs = gamma_g * (P/18.2 * 10^(0.0125*API - 0.00091*T))^1.2048
```

### Oil Viscosity

**Dead oil (Beggs-Robinson):**
```
mu_od = 10^(10^(3.0324 - 0.02023*API) * T^(-1.163)) - 1
```

**Live oil (Beggs-Robinson):**
```
a = 10.715 * (Rs + 100)^(-0.515)
b = 5.44 * (Rs + 150)^(-0.338)
mu_o = a * mu_od^b
```

### Gas Viscosity (Lee-Gonzalez-Eakin)

```
mu_g = K * exp(X * rho_g^Y) * 1e-4   (cp)
K = (9.4 + 0.02*M)*T^1.5 / (209 + 19*M + T)
X = 3.5 + 986/T + 0.01*M
Y = 2.4 - 0.2*X
```

Where M = gas molecular weight, T in Rankine, rho_g in g/cm3.

### Example PVT Output

```
## PVT Properties at P = 3000 psia, T = 200F

| Property | Value | Units |
|----------|-------|-------|
| Z-factor | 0.842 | — |
| Bubble point (Pb) | 2850 | psia |
| Bo | 1.354 | RB/STB |
| Bg | 0.00523 | RB/scf |
| Rs | 580 | scf/STB |
| Oil viscosity (mu_o) | 0.65 | cp |
| Gas viscosity (mu_g) | 0.018 | cp |
| Oil density | 46.2 | lb/ft3 |

**Note:** Above bubble point — oil is undersaturated. Bo calculated
using above-Pb compressibility correction. Values are from Standing
and Beggs-Robinson correlations (field units).
```

---

## Module 3 — Automated Assisted History Matching (AHM)

### Capabilities

- Latin Hypercube Sampling (LHS) for parameter space exploration
- Particle Swarm Optimization (PSO) for history matching
- Mismatch objective functions (RMS, normalized RMS)
- Simplified proxy model for quick screening

### Parameter Space

Typical matching parameters with default ranges:

| Parameter | Symbol | Unit | Default Range |
|-----------|--------|------|---------------|
| Horizontal permeability | kh | md | 1 - 500 |
| Vertical permeability | kv | md | 0.1 - 50 |
| Porosity | phi | fraction | 0.05 - 0.30 |
| Skin factor | S | — | -3 to +20 |
| Aquifer strength | Jaq | STB/D/psi | 0 - 100 |
| Aquifer volume | Vaq | MMSTB | 1 - 100 |
| Rel perm exponent (oil) | no | — | 1.5 - 4.0 |
| Rel perm exponent (water) | nw | — | 1.5 - 4.0 |

### LHS Workflow

1. User defines: parameters, ranges, number of samples (N)
2. Generate N samples using Latin Hypercube (stratified random)
3. For each sample: run proxy model or simplified material balance
4. Compute mismatch (objective function) against observed data
5. Rank samples by mismatch, report top 10

### Objective Function

```
RMS = sqrt( (1/n) * SUM[(q_sim_i - q_obs_i)^2] )
NRMS = RMS / (q_obs_max - q_obs_min)
```

Good match: NRMS < 0.10 (10% normalized error).

### PSO Workflow

1. Initialize swarm (20-50 particles) from LHS best results
2. Each particle = set of matching parameters
3. Evaluate objective function for each particle
4. Update velocity and position using personal best and global best
5. Iterate 50-200 generations
6. Report: best-fit parameters, convergence history, final mismatch

**PSO update equations:**
```
v_i(t+1) = w*v_i(t) + c1*r1*(pbest_i - x_i) + c2*r2*(gbest - x_i)
x_i(t+1) = x_i(t) + v_i(t+1)
```
Where w=0.7 (inertia), c1=c2=1.5 (cognitive/social), r1,r2 ~ U(0,1).

### Example AHM Output

```
## History Match Results — Well PRD-01

### Best-Fit Parameters
| Parameter | Value | Unit | Range |
|-----------|-------|------|-------|
| kh | 125 | md | 1-500 |
| phi | 0.18 | frac | 0.05-0.30 |
| Skin | 2.5 | — | -3 to 20 |
| Aquifer Jaq | 35 | STB/D/psi | 0-100 |

NRMS = 0.062 (good match)
Iterations: 150, Swarm size: 30

**Note:** History matching is non-unique. Multiple parameter sets may
yield similar mismatch. Always validate against additional data (BHP,
water cut, GOR) before using for forecasting.
```

---

## Module 4 — Well Designer and VFP Tables

### Capabilities

- VFP table generation (tNav VFPPROD keyword format)
- Beggs and Brill multiphase flow correlation
- Tubing pressure drop calculations
- IPR curves (Vogel for two-phase, Fetkovich for gas wells)
- Nodal analysis (IPR-VFP intersection)
- Sensitivity: tubing ID, GLR, water cut

### Vogel IPR (Two-Phase Oil Wells)

Below bubble point:
```
q/qmax = 1 - 0.2*(Pwf/Pr) - 0.8*(Pwf/Pr)^2
```

Where:
- q = oil rate at Pwf (STB/D)
- qmax = AOF (absolute open flow) at Pwf=0
- Pr = average reservoir pressure (psia)
- Pwf = flowing bottomhole pressure (psia)

Determine qmax from one test point (q_test, Pwf_test):
```
qmax = q_test / (1 - 0.2*(Pwf_test/Pr) - 0.8*(Pwf_test/Pr)^2)
```

### Fetkovich IPR (Gas Wells)

```
q = C * (Pr^2 - Pwf^2)^n
```
Where C = deliverability coefficient, n = exponent (0.5-1.0).

### Beggs and Brill Pressure Drop

Simplified approach for tubing pressure gradient:

```
(dP/dL) = (rho_m * g * sin(theta) + f * rho_m * v_m^2 / (2*d)) / (1 - rho_m*v_m*v_sg/P)
```

**Flow pattern map** (Beggs-Brill):
1. Segregated (stratified, annular)
2. Intermittent (plug, slug)
3. Distributed (bubble, mist)

Determine flow pattern from Froude number and liquid content (lambda_L),
then compute liquid holdup correction.

**Workflow:**
1. User provides: tubing ID, depth, surface/BH temperature, fluid properties
2. Divide tubing into segments (50-100 ft each)
3. March from bottom to top (or top to bottom), computing dP per segment
4. Sum pressure drops for total tubing loss
5. Build VFP table: Pwh vs q at various GLR and water cut

### VFP Table Format (tNav VFPPROD)

```
VFPPROD
-- Table  Datum   Rate    WFR     GFR     THP     ALQ
--  No.   Depth   Type    Type    Type    Type    Type
     1    8000.0  OIL     WCT     GOR     THP     ' '  /
-- Rate values (STB/D)
  100 500 1000 2000 3000 5000 /
-- THP values (psia)
  100 200 300 400 500 /
-- WCT values (fraction)
  0.0 0.2 0.5 0.8 /
-- GOR values (scf/STB)
  200 400 600 800 1000 /
-- ALQ values
  0 /
-- BHP data (psia) — one value per (Rate, THP, WCT, GOR, ALQ) combination
  1200 1350 1500 ...
/
```

### Nodal Analysis

Find the operating point where IPR and VFP (tubing performance) intersect:

1. Generate IPR curve: q vs Pwf (Vogel or Fetkovich)
2. Generate VFP curve: q vs Pwf (Beggs-Brill from wellhead to bottomhole)
3. Plot both on same axes (Pwf vs q)
4. Intersection = operating point (q_op, Pwf_op)
5. Sensitivity: overlay curves at different tubing sizes, GLR, Pwh

### Example Nodal Analysis Output

```
## Nodal Analysis — Well PRD-01

### Operating Conditions
| Parameter | Value | Unit |
|-----------|-------|------|
| Reservoir pressure (Pr) | 3500 | psia |
| Wellhead pressure (Pwh) | 200 | psia |
| Tubing ID | 2.992 | inches |
| Depth (TVD) | 8000 | ft |
| GOR | 600 | scf/STB |
| Water cut | 0.20 | fraction |

### Operating Point
| Parameter | Value | Unit |
|-----------|-------|------|
| Oil rate (q_op) | 1850 | STB/D |
| BHP (Pwf_op) | 2200 | psia |
| Drawdown | 1300 | psi |

### Tubing Size Sensitivity
| Tubing ID (in) | q_op (STB/D) | Pwf_op (psia) |
|-----------------|--------------|----------------|
| 2.441 | 1520 | 2450 |
| 2.992 | 1850 | 2200 |
| 3.500 | 2050 | 2050 |

**Note:** Increasing tubing from 2.441" to 2.992" gains 330 STB/D.
Further increase to 3.5" gains only 200 STB/D — diminishing returns.
Validate against actual well test data before sizing.
```

---

## Module 5 — Geology and Property Modeling (Petrophysics)

### Capabilities

- Kriging (simple, ordinary) for spatial interpolation
- Sequential Gaussian Simulation (SGS) concepts
- Synthetic 2D grid from porosity/permeability distributions
- Archie's equation for water saturation
- Permeability-porosity transforms (Kozeny-Carman, empirical)

### Archie's Equation

```
Sw = (a / (phi^m * Rt) * Rw)^(1/n)
```

Where:
- Sw = water saturation (fraction)
- phi = porosity (fraction)
- Rt = true formation resistivity (ohm-m)
- Rw = formation water resistivity (ohm-m)
- a = tortuosity factor (typ. 0.62-1.0)
- m = cementation exponent (typ. 1.8-2.5)
- n = saturation exponent (typ. 1.8-2.2)

**Typical Archie parameters:**

| Rock Type | a | m | n |
|-----------|---|---|---|
| Sandstone (clean) | 0.62 | 2.15 | 2.0 |
| Sandstone (shaly) | 0.81 | 2.0 | 2.0 |
| Carbonate | 1.0 | 2.0 | 2.0 |
| Unconsolidated | 0.62 | 1.8 | 1.8 |

### Permeability-Porosity Transforms

**Kozeny-Carman:**
```
k = (phi^3 * d^2) / (72 * tau^2 * (1-phi)^2)
```
Where d = grain diameter (cm), tau = tortuosity.

**Empirical (semi-log):**
```
log(k) = a + b * phi
```
Fit a and b from core data (log-linear regression).

### Kriging (Simple and Ordinary)

Kriging provides the Best Linear Unbiased Estimate (BLUE) of a spatial variable.

**Variogram model (spherical):**
```
gamma(h) = C0 + C * [1.5*(h/a) - 0.5*(h/a)^3]   for h <= a
gamma(h) = C0 + C                                  for h > a
```
Where C0 = nugget, C = sill - nugget, a = range, h = lag distance.

**Simple kriging:**
```
Z*(x0) = mu + SUM[lambda_i * (Z(xi) - mu)]
```
Weights lambda_i from solving the kriging system using the variogram.

**Workflow:**
1. User provides: known data points (x, y, value), variogram parameters
2. Build variogram matrix for known points
3. For each unknown grid node, solve kriging system for weights
4. Estimate value and kriging variance at each node
5. Output: interpolated grid + variance grid

### SGS (Sequential Gaussian Simulation)

Produces multiple equiprobable realizations:
1. Transform data to normal distribution
2. Define a random path through all grid nodes
3. At each node: krige from nearby data + previously simulated nodes
4. Draw from conditional distribution (kriged mean + kriged variance)
5. Back-transform to original units
6. Repeat for multiple realizations

**Note:** Full SGS requires significant computation. This skill provides
the methodology and can generate simplified 2D examples.

### Example Petrophysics Output

```
## Water Saturation — Archie's Equation

### Input
| Parameter | Value |
|-----------|-------|
| Porosity (phi) | 0.18 |
| Rt (formation resistivity) | 25 ohm-m |
| Rw (water resistivity) | 0.04 ohm-m |
| a (tortuosity) | 0.62 |
| m (cementation) | 2.15 |
| n (saturation) | 2.0 |

### Result
| Property | Value |
|----------|-------|
| Sw | 0.23 (23%) |
| So (1-Sw) | 0.77 (77%) |

Hydrocarbon saturation of 77% indicates a productive zone.
Validate with capillary pressure data and log analysis.
```

---

## Workflow Summary

### Step 1 — Identify Module
Map user request to one of the 5 modules:
- .DATA file, material balance, decline curve -> Module 1
- PVT, Z-factor, Bo, Rs, viscosity, EOS -> Module 2
- History matching, LHS, PSO, parameter fitting -> Module 3
- VFP, IPR, nodal analysis, tubing, wellhead -> Module 4
- Kriging, Archie, petrophysics, grid, porosity-perm -> Module 5

### Step 2 — Gather Inputs
Collect required parameters from the user. Provide sensible defaults
(with field units) if user omits values. Always state assumptions.

### Step 3 — Calculate
Use Python (stdlib only) or analytical formulas. Reference
`references/python_example.py` for implementations.
Reference `references/equations.md` for equation details.

### Step 4 — Output
Format as:
1. **Input summary table** — echo back all parameters and assumptions
2. **Results table** — computed values with units
3. **Narrative** — interpretation, trends, recommendations
4. **Caveats** — correlation validity ranges, assumptions, limitations

### Step 5 — .DATA Snippet (if applicable)
If the calculation feeds into a simulation model, provide the relevant
Eclipse/tNav keyword block ready for copy-paste.

---

## Output Format

All outputs follow this pattern:

```
## [Calculation Title]

### Input Parameters
| Parameter | Value | Unit | Source |
|-----------|-------|------|--------|
| ... | ... | ... | User / Default |

### Results
| Property | Value | Unit |
|----------|-------|------|
| ... | ... | ... |

**Summary:** [1-3 sentence interpretation of results]

**Caveats:**
- [Correlation validity range]
- [Assumptions made]
- [When to use full simulation instead]
```

---

## Error Handling

| Condition | Action |
|-----------|--------|
| Missing required input | List missing parameters with typical ranges |
| Value outside correlation range | Warn user, compute anyway with disclaimer |
| Negative or non-physical result | Flag as error, suggest input corrections |
| Convergence failure (Z-factor, PSO) | Report iteration count, last estimate, suggest relaxed tolerance |
| Grid too large for inline calculation | Suggest subset or coarser grid |

---

## Units Reference

All correlations use **field units** by default:

| Quantity | Field Unit | SI Unit | Conversion |
|----------|-----------|---------|------------|
| Pressure | psia | kPa | 1 psia = 6.895 kPa |
| Temperature | F (Fahrenheit) | C | F = C*9/5 + 32 |
| Length/Depth | ft | m | 1 ft = 0.3048 m |
| Rate (oil) | STB/D | m3/d | 1 STB = 0.1590 m3 |
| Rate (gas) | Mscf/D | m3/d | 1 Mscf = 28.317 m3 |
| Permeability | md | m2 | 1 md = 9.869e-16 m2 |
| Viscosity | cp | Pa-s | 1 cp = 0.001 Pa-s |
| FVF (oil) | RB/STB | Rm3/Sm3 | same ratio |
| FVF (gas) | RB/scf | Rm3/Sm3 | same ratio |
| GOR | scf/STB | Sm3/Sm3 | 1 scf/STB = 0.1781 Sm3/Sm3 |

If user provides SI inputs, convert to field units before calculation,
then present results in both unit systems.

---

## Implementation Notes

- **Use Python (stdlib only)** for calculations — math, statistics, random, json, csv
- Reference implementations in `references/python_example.py`
- Equation derivations and variable definitions in `references/equations.md`
- For .DATA file generation, follow Eclipse 100/tNavigator keyword syntax
- All iterative solvers (Z-factor, PSO) should have max iteration limits
- Correlation validity ranges should be checked and warned about
- This is an educational tool — always recommend validation against lab data
  and full simulation for production decisions
