---
name: mass-energy-balance
description: >
  Perform material balance, energy balance, and reaction stoichiometry
  calculations for chemical and petroleum engineering courses. Covers
  steady-state and transient material balances on single and multiple
  components, energy balances with heat of reaction, heating and cooling,
  phase equilibria basics, combustion calculations for natural gas, separator
  design balances, flash calculations, and reaction extent for refinery and gas
  processing applications. Use this skill when the user needs to solve mass
  balance problems, energy balance problems, stoichiometry, combustion air
  calculations, separator flash calculations, heat duty estimation, or reaction
  engineering calculations for ChBE 211, ChBE 321, or petroleum processing
  coursework. Trigger for phrases like "material balance on separator", "energy
  balance for heater treater", "combustion air for natural gas", "flash
  calculation", "reaction stoichiometry", "heat of combustion methane",
  "steady state mass balance", "recycle stream balance", "excess air
  calculation", or "heat duty for reboiler". Produces step-by-step solutions
  with labeled equations and Python code.
---

# Material and Energy Balance Skill

Computational skill for solving material balance, energy balance, and
reaction stoichiometry problems in chemical and petroleum engineering.
Covers ChBE 211 (Material and Energy Balances), ChBE 321 (Reaction
Engineering), and petroleum processing applications.

**No external API required.** This skill provides equations, worked examples,
and Python (stdlib-only) calculation code.

See `references/equations.md` for thermodynamic data tables, full equation
derivations, and degree of freedom analysis guide.

---

## Module 1 — Steady-State Material Balance

### General Balance Equation

```
Input + Generation = Output + Accumulation
```

At steady state, Accumulation = 0:
```
Input + Generation = Output + Consumption
```

For a non-reactive system (no generation/consumption):
```
SUM(F_in) = SUM(F_out)
```

Where F is molar or mass flow rate (mol/s or kg/s).

### Component Balance (Multi-Component System)

For component i in a non-reactive system:
```
F_in * x_i,in = F_out * x_i,out
```

For N components, write N independent component balances. For a system with
N components and S streams, the total number of independent equations is N.

### Degree of Freedom Analysis

```
DOF = (number of unknowns) - (number of independent equations)
```

The system is **exactly specified** when DOF = 0:
- DOF > 0: underdetermined — need more specifications
- DOF < 0: overdetermined — remove redundant equations or specifications

**Count unknowns:** Stream compositions, flow rates, and process variables
(T, P, split fractions) that are not given.

**Count equations:**
- N independent material balances per unit (non-reactive)
- N-1 independent component balances + 1 total balance (only N-1 are
  independent for non-reactive systems)
- Normalization: SUM(x_i) = 1 for each stream (1 equation per stream)
- Additional specifications (e.g., "stream 3 is 30 mol% methane")

### PNGE Application: Two-Phase Wellhead Separator

A wellhead separator splits a wellstream (F_feed) into gas (F_gas) and liquid
(F_liq) streams. Given feed composition and separator split:

```
F_feed = F_gas + F_liq                          [total balance]
F_feed * z_i = F_gas * y_i + F_liq * x_i        [component balance, i = 1..N]
```

Where z_i = feed mole fraction, y_i = gas composition, x_i = liquid
composition.

### Tie Component Method (Recycle Systems)

For a system with recycle where one component passes through unreacted:
1. Identify the tie component (inert or pass-through species)
2. Write balance on the tie component across the entire system (feed to
   product)
3. Use tie component to calculate overall conversion, then work backwards
   through each unit

**Example: Natural gas plant with N2 tie component**
- Feed: 100 mol/s with 5 mol% N2 (tie), 95 mol% hydrocarbon
- Product specification: 90% N2 removal into vent stream
- Tie balance: N2_in = N2_vent; solve for vent flow rate first, then
  all other streams

### Python — Three-Stream Separator Balance

```python
# Non-reactive steady-state 3-component separator
# Feed splits to overhead and bottoms; given feed composition and split ratio
# Components: methane (1), ethane (2), propane (3)

# Given
F_feed = 100.0          # mol/s
z = [0.70, 0.20, 0.10]  # feed mole fractions [CH4, C2H6, C3H8]
split = [0.95, 0.40, 0.05]  # fraction of each component going to overhead

# Material balance
F_overhead = sum(F_feed * z[i] * split[i] for i in range(3))
F_bottoms = F_feed - F_overhead

comp_overhead = [(F_feed * z[i] * split[i]) / F_overhead for i in range(3)]
comp_bottoms  = [(F_feed * z[i] * (1 - split[i])) / F_bottoms for i in range(3)]

print(f"Overhead: {F_overhead:.2f} mol/s")
print(f"  Compositions: {[f'{x:.3f}' for x in comp_overhead]}")
print(f"Bottoms:  {F_bottoms:.2f} mol/s")
print(f"  Compositions: {[f'{x:.3f}' for x in comp_bottoms]}")
```

---

## Module 2 — Combustion Calculations

### General Combustion Reaction for Alkanes

```
CnH(2n+2)  +  [(3n+1)/2] O2  ->  n CO2  +  (n+1) H2O
```

Key reactions:

| Fuel | Reaction | Stoichiometric O2 (mol/mol fuel) |
|------|----------|----------------------------------|
| Methane (CH4) | CH4 + 2 O2 -> CO2 + 2 H2O | 2.0 |
| Ethane (C2H6) | C2H6 + 3.5 O2 -> 2 CO2 + 3 H2O | 3.5 |
| Propane (C3H8) | C3H8 + 5 O2 -> 3 CO2 + 4 H2O | 5.0 |
| n-Butane (C4H10) | C4H10 + 6.5 O2 -> 4 CO2 + 5 H2O | 6.5 |
| Hydrogen (H2) | H2 + 0.5 O2 -> H2O | 0.5 |
| Carbon (C) | C + O2 -> CO2 | 1.0 |

### Theoretical Air

Air is 21 mol% O2 and 79 mol% N2. Molar ratio N2/O2 in air = 79/21 = 3.76.

Theoretical air for complete combustion of methane:
```
CH4 + 2 O2 -> CO2 + 2 H2O

Stoichiometric O2: 2 mol per mol CH4
Stoichiometric air: 2 / 0.21 = 9.524 mol air per mol CH4
                   = 9.524 * 28.97 g/mol / 16.04 g/mol
                   = 17.2 kg air / kg CH4
```

### Percent Excess Air

```
% Excess Air = (actual air - theoretical air) / theoretical air  x  100%
```

**Equivalence ratio (phi):**
```
phi = (actual fuel/air) / (stoichiometric fuel/air)
phi < 1: fuel-lean (excess air)
phi > 1: fuel-rich (deficient air, incomplete combustion possible)
phi = 1: stoichiometric
```

### Flue Gas Composition from Combustion

For methane with A% excess air (A as decimal fraction, e.g., A=0.10 for 10%):

Basis: 1 mol CH4 fed
- O2 supplied = 2 * (1 + A) mol
- N2 supplied = 2 * (1 + A) * 3.76 mol
- Products: CO2 = 1 mol, H2O = 2 mol
- O2 in flue = 2 * A mol (excess not consumed)
- N2 in flue = 2 * (1 + A) * 3.76 mol

Dry flue gas mole fractions (no H2O):
```
total_dry = 1 + 2*A + 2*(1+A)*3.76
CO2 fraction = 1 / total_dry
O2 fraction  = 2*A / total_dry
N2 fraction  = 2*(1+A)*3.76 / total_dry
```

### Heating Values

| Fuel | HHV (kJ/kg) | LHV (kJ/kg) | Difference |
|------|-------------|-------------|------------|
| Methane | 55,530 | 50,050 | 5,480 (water condensed in HHV) |
| Ethane | 51,900 | 47,620 | 4,280 |
| Propane | 50,350 | 46,360 | 3,990 |
| n-Butane | 49,500 | 45,720 | 3,780 |
| Natural gas (avg) | ~53,000 | ~48,000 | Varies with composition |
| Hydrogen | 141,800 | 119,900 | 21,900 |
| Diesel | ~44,800 | ~42,500 | ~2,300 |

**HHV vs LHV:** Higher Heating Value (HHV) includes the enthalpy of
condensation of water in combustion products. Lower Heating Value (LHV) assumes
water leaves as vapor. Boiler efficiencies typically reference HHV; flare
designs typically reference LHV.

### Python — Combustion Air Calculation

```python
# Combustion air calculation for natural gas
# Basis: 1 mol natural gas with known composition

# Natural gas composition (mole fractions)
gas_comp = {
    'CH4': 0.900,
    'C2H6': 0.060,
    'C3H8': 0.025,
    'C4H10': 0.010,
    'N2': 0.005,
}

# Stoichiometric O2 required per mol of each component
stoich_o2 = {'CH4': 2.0, 'C2H6': 3.5, 'C3H8': 5.0,
             'C4H10': 6.5, 'N2': 0.0}

excess_air_pct = 20.0  # 20% excess air

# Stoichiometric O2 for 1 mol gas
o2_stoich = sum(gas_comp[k] * stoich_o2.get(k, 0) for k in gas_comp)
o2_actual = o2_stoich * (1 + excess_air_pct / 100)
air_actual = o2_actual / 0.21  # mol air per mol gas

print(f"Stoichiometric O2:  {o2_stoich:.4f} mol O2/mol gas")
print(f"Actual O2 ({excess_air_pct:.0f}% xs): {o2_actual:.4f} mol O2/mol gas")
print(f"Actual air:         {air_actual:.4f} mol air/mol gas")

# Flue gas composition (1 mol gas basis)
n2_from_air = air_actual * 0.79
co2_out  = sum(gas_comp.get(k,0)*n for k,n in
               [('CH4',1),('C2H6',2),('C3H8',3),('C4H10',4)])
h2o_out  = sum(gas_comp.get(k,0)*n for k,n in
               [('CH4',2),('C2H6',3),('C3H8',4),('C4H10',5)])
o2_out   = o2_actual - o2_stoich
n2_out   = n2_from_air + gas_comp.get('N2', 0)

total_flue = co2_out + h2o_out + o2_out + n2_out
print(f"\nFlue gas (wet):")
print(f"  CO2: {co2_out/total_flue*100:.2f} mol%")
print(f"  H2O: {h2o_out/total_flue*100:.2f} mol%")
print(f"  O2:  {o2_out/total_flue*100:.2f} mol%")
print(f"  N2:  {n2_out/total_flue*100:.2f} mol%")
```

---

## Module 3 — Energy Balance (Non-Reactive)

### General Open System Energy Balance

```
Q_dot - W_dot_shaft = SUM(m_dot_out * h_out) - SUM(m_dot_in * h_in) + dKE + dPE
```

For process equipment (no shaft work, negligible KE/PE changes):
```
Q_dot = SUM(m_dot_out * h_out) - SUM(m_dot_in * h_in)
```

Where h = specific enthalpy (kJ/kg) at stream conditions.

### Sensible Heat (No Phase Change)

For a stream with constant Cp (approximation for small T range):
```
Q = m_dot * Cp * (T_out - T_in)    [kW if m_dot in kg/s, Cp in kJ/(kg-K)]
Q = n_dot * Cp_molar * (T_out - T_in)   [kW if using molar flow, Cp in kJ/(mol-K)]
```

For variable Cp (polynomial Shomate form):
```
Cp(T) = A + B*t + C*t^2 + D*t^3 + E/t^2     [kJ/(mol-K), t = T/1000, T in K]
H(T) - H(298) = A*t + B*t^2/2 + C*t^3/3 + D*t^4/4 - E/t + F - H_ref
```

See `references/equations.md` for Shomate coefficients for key gases.

### Latent Heat (Phase Change)

```
Q = m_dot * lambda           [lambda = latent heat of vaporization, kJ/kg]
```

Water latent heats (for process design):
- At 100 C (0.1013 MPa, boiling): lambda = 2,257 kJ/kg = 970.3 BTU/lb
- At 50 C: lambda = 2,382 kJ/kg
- At 200 C (1.555 MPa): lambda = 1,941 kJ/kg
- At 300 C (8.58 MPa): lambda = 1,405 kJ/kg

Use pnge-geochem-pw:nist-webbook for exact values at any T and P.

### Heat Exchanger Energy Balance

Overall energy balance (no shaft work, adiabatic exchanger):
```
Q = m_hot * Cp_hot * (T_hot,in - T_hot,out) = m_cold * Cp_cold * (T_cold,out - T_cold,in)
```

Design equation:
```
Q = U * A * LMTD
```

Where U = overall heat transfer coefficient [W/(m2-K) or BTU/(hr-ft2-F)],
A = heat transfer area.

### LMTD Calculation

Counter-current flow (preferred — higher driving force):
```
dT1 = T_hot,in  - T_cold,out
dT2 = T_hot,out - T_cold,in
LMTD = (dT1 - dT2) / ln(dT1/dT2)
```

Co-current (parallel) flow:
```
dT1 = T_hot,in  - T_cold,in
dT2 = T_hot,out - T_cold,out
LMTD = (dT1 - dT2) / ln(dT1/dT2)
```

Special case: if dT1 = dT2, then LMTD = dT1 (L'Hopital's rule applies).

### PNGE Application: Heater-Treater Heat Duty

A heater-treater heats oil-water emulsion to improve separation.
Typical conditions:
- Inlet: 50 F wellstream
- Treatment: 110-140 F (light oil), 140-180 F (heavy/paraffinic oil)
- Heat duty: Q = (m_oil * Cp_oil + m_water * Cp_water) * delta_T

Typical Cp values for petroleum engineering:
- Crude oil: 0.45-0.50 BTU/(lb-F) [1.88-2.09 kJ/(kg-K)]
- Produced water: 0.98 BTU/(lb-F) [4.10 kJ/(kg-K)]
- Natural gas at 100 F, 100 psia: 0.58 BTU/(lb-F)

Typical U values for heat exchanger selection:
| Service | U [BTU/(hr-ft2-F)] | U [W/(m2-K)] |
|---------|-------------------|--------------|
| Oil-oil | 30-60 | 170-340 |
| Oil-water | 50-80 | 285-455 |
| Gas-gas (high P) | 10-25 | 57-142 |
| Steam condenser | 200-400 | 1135-2270 |

### Python — Heat Exchanger Design

```python
import math

# Shell-and-tube heat exchanger sizing
# Hot side: crude oil cooling from 250 F to 120 F
# Cold side: produced water heating from 60 F to 180 F

T_hot_in  = 250.0   # F
T_hot_out = 120.0   # F
T_cold_in  = 60.0   # F
T_cold_out = 180.0  # F

m_hot  = 1000.0     # lb/hr crude oil
Cp_hot = 0.47       # BTU/(lb-F) crude oil

Q = m_hot * Cp_hot * (T_hot_in - T_hot_out)  # BTU/hr

Cp_cold = 0.98  # BTU/(lb-F) produced water
m_cold = Q / (Cp_cold * (T_cold_out - T_cold_in))

# LMTD counter-current
dT1 = T_hot_in  - T_cold_out
dT2 = T_hot_out - T_cold_in
LMTD = (dT1 - dT2) / math.log(dT1 / dT2)

U = 50.0    # BTU/(hr-ft2-F) typical oil-water
A = Q / (U * LMTD)

print(f"Heat duty:        {Q:,.0f} BTU/hr  ({Q*0.000293:.1f} kW)")
print(f"Cold side flow:   {m_cold:,.0f} lb/hr")
print(f"LMTD:             {LMTD:.1f} F")
print(f"Area required:    {A:.1f} ft2  ({A*0.0929:.1f} m2)")
```

---

## Module 4 — Energy Balance with Reaction

### Reactive Energy Balance (Isothermal Reactor at 298 K)

```
Q = -DeltaH_rxn * xi     [positive Q = heat removed for exothermic reaction]
```

For a non-isothermal reactor:
```
Q = DeltaH_rxn * xi + SUM(n_out_i * Cp_i * T_out) - SUM(n_in_i * Cp_i * T_in)
```

### Extent of Reaction

```
xi = (N_i - N_i0) / nu_i
```

Where:
- xi = extent of reaction (mol)
- N_i = moles of species i at end
- N_i0 = initial moles of species i
- nu_i = stoichiometric coefficient (positive for products, negative for
  reactants)

All species give the same xi — use this to check stoichiometric consistency.

### Standard Heats of Formation (Hess's Law)

```
DeltaH_rxn = SUM(nu_i * DeltaH_f,i)
```

Sign convention: positive nu_i for products, negative for reactants.
DeltaH_rxn < 0: exothermic; DeltaH_rxn > 0: endothermic.

**Common standard heats of formation at 298 K (kJ/mol):**

| Species | DeltaH_f (kJ/mol) |
|---------|-------------------|
| CH4(g)  | -74.87 |
| C2H6(g) | -84.68 |
| C3H8(g) | -103.8 |
| CO2(g)  | -393.5 |
| H2O(g)  | -241.8 |
| H2O(l)  | -285.8 |
| CO(g)   | -110.5 |
| H2(g)   | 0.0 |
| C(graphite) | 0.0 |
| O2(g)   | 0.0 |
| N2(g)   | 0.0 |

**Combustion of methane example:**
```
CH4 + 2 O2 -> CO2 + 2 H2O(g)

DeltaH_rxn = [1*(-393.5) + 2*(-241.8)] - [1*(-74.87) + 2*(0)]
           = [-877.1] - [-74.87]
           = -802.2 kJ/mol CH4   (LHV basis, water as vapor)
```

For HHV basis with liquid water: DeltaH_rxn = -890.3 kJ/mol CH4.

### Kirchhoff's Law — Heat of Reaction at Temperature T

```
DeltaH_rxn(T) = DeltaH_rxn(298 K) + INTEGRAL[DeltaCp dT from 298 to T]

DeltaCp = SUM(nu_i * Cp_i(T))
```

For small temperature ranges or approximate calculations with constant Cp:
```
DeltaH_rxn(T) approx DeltaH_rxn(298) + DeltaCp_avg * (T - 298)
```

### PNGE Application: Natural Gas Flare

Flare combustion of methane at 600 F inlet (fuel + air mix):
- DeltaH_rxn at 25 C = -802.2 kJ/mol CH4 (LHV)
- Kirchhoff correction from 25 C to 316 C (600 F) is small (~5%)
- Radiation fraction of heat released: 25-35% (API 521 method)
- Stack exit T estimated from product Cp integrals

---

## Module 5 — Flash Calculation (Vapor-Liquid Equilibrium)

### Raoult's Law (Ideal VLE)

For an ideal liquid-vapor system:
```
y_i * P = x_i * P_i_sat(T)
```

Where y_i = vapor mole fraction, x_i = liquid mole fraction,
P = total pressure, P_i_sat = pure-component vapor pressure at T.

K-value (volatility ratio):
```
K_i = y_i / x_i = P_i_sat(T) / P
```

Components with K_i >> 1 prefer vapor; K_i << 1 prefer liquid.

### Rachford-Rice Equation

For a flash with feed z_i and vapor fraction V/F:
```
SUM_i [ z_i * (K_i - 1) / (1 + (V/F) * (K_i - 1)) ] = 0
```

Solve iteratively for V/F. Once V/F is found:
```
x_i = z_i / (1 + (V/F) * (K_i - 1))
y_i = K_i * x_i
```

Valid range: -1/(K_max - 1) < V/F < 1/(1 - K_min)

### Bubble and Dew Point

**Bubble point** (first bubble forms from liquid feed):
```
SUM_i (K_i * z_i) = 1.0
```

**Dew point** (first drop forms from vapor feed):
```
SUM_i (z_i / K_i) = 1.0
```

### Antoine Equation for Vapor Pressure

```
log10(P_sat) = A - B / (T + C)
```

Common constants (P in mmHg, T in C) — see `references/equations.md` for
full table. Use pnge-geochem-pw:nist-webbook for precise P_sat at any temperature.

### Python — Multi-Component Flash

```python
import math

def rachford_rice(V_F, z, K):
    """Rachford-Rice residual."""
    return sum(z[i] * (K[i] - 1.0) / (1.0 + V_F * (K[i] - 1.0))
               for i in range(len(z)))

def flash_calc(z, K, tol=1e-8, max_iter=100):
    """Solve Rachford-Rice for vapor fraction V/F by bisection.

    Returns: V_F, x (liquid mole fractions), y (vapor mole fractions)
    """
    # Bounds
    lo = -1.0 / (max(K) - 1.0) + 1e-10
    hi =  1.0 / (1.0 - min(K)) - 1e-10

    # Single-phase checks
    if rachford_rice(0.0, z, K) <= 0:
        return 0.0, list(z), [K[i]*z[i] for i in range(len(z))]
    if rachford_rice(1.0, z, K) >= 0:
        return 1.0, [z[i]/K[i] for i in range(len(z))], list(z)

    # Bisection
    for _ in range(max_iter):
        mid = (lo + hi) / 2.0
        f = rachford_rice(mid, z, K)
        if abs(f) < tol:
            break
        if f > 0:
            lo = mid
        else:
            hi = mid

    V_F = (lo + hi) / 2.0
    x = [z[i] / (1.0 + V_F * (K[i] - 1.0)) for i in range(len(z))]
    y = [K[i] * x[i] for i in range(len(z))]
    return V_F, x, y

# Example: C1/C3 separator flash at 50 psia, 100 F
# K-values approximated from DePriester chart (use NIST WebBook for precision)
K = [8.5, 0.25]          # K_methane, K_propane at these conditions
z = [0.40, 0.60]         # feed: 40 mol% methane, 60 mol% propane

V_F, x, y = flash_calc(z, K)

print(f"Vapor fraction V/F: {V_F:.4f}")
print(f"Liquid: x_CH4={x[0]:.4f}, x_C3H8={x[1]:.4f}  (sum={sum(x):.6f})")
print(f"Vapor:  y_CH4={y[0]:.4f}, y_C3H8={y[1]:.4f}  (sum={sum(y):.6f})")
```

---

## Workflow

### Step 1 — Identify Module

| Problem Type | Module |
|--------------|--------|
| Component flow rates, separator balance, recycle | Module 1 |
| Combustion air, flue gas, HHV/LHV, flare | Module 2 |
| Heat duty, heat exchanger sizing, LMTD, Cp | Module 3 |
| Reaction enthalpy, extent, adiabatic temperature | Module 4 |
| Flash calculation, VLE, K-values, phase split | Module 5 |

### Step 2 — Gather Inputs

Collect required parameters. Confirm:
- **Basis** — per 1 mol feed, per 1 kg/s, per hour
- **Basis unit** ��� mole or mass (be consistent throughout)
- **T and P** for phase equilibrium problems
- **Component identities** and feed compositions (must sum to 1.0)
- **Stream specifications** — any known flow rates, compositions, T, P

State all assumptions explicitly before calculating.

### Step 3 — Degree of Freedom Check

Before solving, verify DOF = 0. List unknowns and equations. If DOF > 0,
identify what specifications are missing and ask the user.

### Step 4 — Calculate and Show Work

1. Equation setup with variable labels
2. Substitution of known values with units at each step
3. Final answer with units
4. Dimensional analysis check (units cancel correctly)

### Step 5 — Produce Output

```
## [Problem Description]

### Given (Basis: [state basis])
| Variable | Value | Unit | Source |
|----------|-------|------|--------|

### DOF Check
Unknowns: N   Equations: N   DOF: 0 (exactly specified)

### Equations Applied
1. [equation name and form]
2. [equation name and form]

### Solution
[step-by-step with units]

### Results
| Variable | Value | Unit |
|----------|-------|------|

**Check:** [balances close to ±0.1%, answer is physically reasonable]

**Assumptions:**
- [list all assumptions made]

**Caveats:**
- [validity ranges, when to use more rigorous methods]

**Check your understanding:** [one question to test conceptual grasp]
```

---

## Error Handling

| Condition | Action |
|-----------|--------|
| Compositions do not sum to 1.0 | Flag error; ask user to verify or normalize |
| DOF != 0 | Report DOF, list which variables are over- or under-specified |
| Negative flow rate or composition | Indicates over-specification or inconsistency; recheck stream specifications |
| Flash V/F outside [0, 1] | System is all vapor (V/F=1) or all liquid (V/F=0); state which and verify K-values |
| Very large K-value range (K>>10 or K<<0.01) | Simple Raoult's law may be unreliable; recommend EOS (PR or SRK) via process simulator |
| Adiabatic flame temperature iteration not converging | Check DeltaH_rxn sign; verify Cp data source for products |
| Units inconsistent in energy balance | Identify the unit mismatch and provide conversion factor |

---

## Caveats and Data Limitations

- **Raoult's law assumes ideal solutions.** For polar compounds, mixtures with
  strong interactions (alcohol-water, acid gases), or high pressures, use
  modified Raoult's law with activity coefficients (UNIFAC, NRTL, Wilson) or
  an EOS approach.
- **Antoine constants have limited T ranges.** Extrapolating outside the stated
  T range gives unreliable vapor pressures. Use pnge-geochem-pw:nist-webbook for
  accurate P_sat at any temperature.
- **Constant Cp approximation** is adequate for small T ranges (±50 K) but can
  introduce >5% error for combustion calculations. Use Shomate polynomial form.
- **This skill covers ideal and near-ideal systems.** For rigorous VLE with
  non-ideal mixtures, high pressures, or near-critical conditions, recommend
  using a process simulator (Aspen HYSYS, DWSIM) with a proper EOS.
- **Heats of formation at 298 K, 1 atm standard state.** Kirchhoff correction
  is required for reactions at other temperatures.

---

## Implementation Notes

- **Use Python (stdlib only)** — math, itertools, statistics modules only
- Full thermodynamic data tables (Shomate Cp polynomials, Antoine constants,
  heats of formation) are in `references/equations.md`
- For precise fluid properties (steam tables, Cp of CH4 at pressure), invoke
  pnge-geochem-pw:nist-webbook rather than using tabulated approximations
- Always show units at each step — unit errors are the most common mistake
  in material and energy balance problems
- This skill integrates with pnge-geochem-pw:tnav for process calculations
  that feed into reservoir simulation models
