# Mass and Energy Balance — Equations and Thermodynamic Data Reference

---

## Degree of Freedom Analysis Guide

### Systematic Procedure

1. Draw and label all streams with flow rates (F) and compositions (x_i)
2. Count total unknowns:
   - Each unknown flow rate = 1 unknown
   - Each unknown composition = 1 unknown per component per stream
   - For N-component stream with total flow unknown: N unknowns (N-1 mole
     fractions + 1 total flow)
3. Count independent equations:
   - N_c independent material balances per process unit
   - Normalization constraint: SUM(x_i) = 1 (1 per stream — but if all
     component fracs are specified, this is redundant)
   - Additional specifications given in problem statement
4. DOF = unknowns - equations

### Common DOF Values

| System | Typical DOF | Notes |
|--------|-------------|-------|
| Single-unit, 2 streams, N components | 0 if N+1 variables specified | Feed + total product flow needed |
| Two-stream split (splitter) | 0 if split fraction given | Split fractions must sum to 1 |
| Mixer (2 feeds, 1 product) | 0 if 2 feeds fully specified | Product is calculated |
| Recycle loop | Often 0 with overall + per-unit DOF analysis | Solve overall first |

---

## Shomate Equation for Cp (NIST Format)

```
Cp = A + B*t + C*t^2 + D*t^3 + E/t^2     [J/(mol-K)]
t = T[K] / 1000
```

Enthalpy increment:
```
H(T) - H(298.15) = A*t + B*t^2/2 + C*t^3/3 + D*t^4/4 - E/t + F - H_ref   [kJ/mol]
```

Entropy:
```
S(T) = A*ln(t) + B*t + C*t^2/2 + D*t^3/3 - E/(2*t^2) + G   [J/(mol-K)]
```

### Shomate Coefficients for Key Gases

**Methane (CH4)** — Phase: Gas, T range: 298-1300 K
| A | B | C | D | E | F | G | H_ref |
|---|---|---|---|---|---|---|-------|
| -0.703029 | 108.4773 | -42.52157 | 5.862788 | 0.678565 | -76.84376 | 158.7163 | -74.87310 |

**Carbon Dioxide (CO2)** — Phase: Gas, T range: 298-1200 K
| A | B | C | D | E | F | G | H_ref |
|---|---|---|---|---|---|---|-------|
| 24.99735 | 55.18696 | -33.69137 | 7.948387 | -0.136638 | -403.6075 | 228.2431 | -393.5224 |

**Water vapor (H2O)** — Phase: Gas, T range: 500-1700 K
| A | B | C | D | E | F | G | H_ref |
|---|---|---|---|---|---|---|-------|
| 30.09200 | 6.832514 | 6.793435 | -2.534480 | 0.082139 | -250.8810 | 223.3967 | -241.8264 |

**Nitrogen (N2)** — Phase: Gas, T range: 298-6000 K
| A | B | C | D | E | F | G | H_ref |
|---|---|---|---|---|---|---|-------|
| 26.09200 | 8.218801 | -1.976141 | 0.159274 | 0.044434 | -7.989230 | 221.0200 | 0.000000 |

**Oxygen (O2)** — Phase: Gas, T range: 700-2000 K
| A | B | C | D | E | F | G | H_ref |
|---|---|---|---|---|---|---|-------|
| 30.03235 | 8.772972 | -3.988133 | 0.788313 | -0.741599 | -11.32468 | 236.1663 | 0.000000 |

**Ethane (C2H6)** — Phase: Gas, T range: 298-1200 K
| A | B | C | D | E | F | G | H_ref |
|---|---|---|---|---|---|---|-------|
| -3.03849 | 199.2018 | -84.97074 | 11.00888 | 0.300195 | -90.07598 | 194.1816 | -84.68010 |

**Propane (C3H8)** — Phase: Gas, T range: 298-1200 K
| A | B | C | D | E | F | G | H_ref |
|---|---|---|---|---|---|---|-------|
| -23.17577 | 347.7808 | -158.2099 | 24.94879 | 0.897177 | -127.7260 | 248.3580 | -103.8470 |

Source: NIST WebBook Shomate equation database. Verify against NIST for
most recent values — updates occur when new experimental data are published.

---

## Antoine Constants for Vapor Pressure

```
log10(P_sat) = A - B / (T + C)
```

**Important:** Units vary by source. These constants use P in mmHg, T in C.
To convert P_sat from mmHg to kPa: multiply by 0.133322.
To convert P_sat from mmHg to psia: multiply by 0.019337.

| Component | A | B | C | T_min (C) | T_max (C) |
|-----------|---|---|---|-----------|-----------|
| Methane | 6.82718 | 405.42 | 267.78 | -183 | -93 |
| Ethane | 6.82486 | 663.70 | 256.68 | -142 | -75 |
| Propane | 6.82973 | 803.81 | 246.99 | -108 | -25 |
| i-Butane | 6.82650 | 882.80 | 240.00 | -84 | 8 |
| n-Butane | 6.82707 | 935.09 | 238.73 | -73 | 19 |
| n-Pentane | 6.85221 | 1064.63 | 232.00 | -50 | 58 |
| n-Hexane | 6.87601 | 1171.17 | 224.41 | -25 | 92 |
| Benzene | 6.90565 | 1211.03 | 220.79 | 8 | 103 |
| Toluene | 6.95464 | 1344.80 | 219.48 | 6 | 137 |
| Water | 8.10765 | 1750.29 | 235.00 | 60 | 150 |
| Methanol | 7.87863 | 1473.11 | 230.00 | -14 | 65 |
| Ethanol | 8.04494 | 1554.30 | 222.65 | -2 | 100 |

**For higher accuracy or out-of-range T:** Use pnge-geochem-pw:nist-webbook to query
P_sat directly from the equation of state.

---

## Standard Heats of Formation and Combustion at 298 K, 1 atm

### Heats of Formation (DeltaH_f, kJ/mol)

| Species | State | DeltaH_f (kJ/mol) |
|---------|-------|-------------------|
| H2 | g | 0.000 |
| O2 | g | 0.000 |
| N2 | g | 0.000 |
| C | graphite | 0.000 |
| CO | g | -110.53 |
| CO2 | g | -393.51 |
| H2O | g | -241.82 |
| H2O | l | -285.83 |
| CH4 | g | -74.87 |
| C2H2 | g | +226.73 |
| C2H4 | g | +52.47 |
| C2H6 | g | -84.68 |
| C3H8 | g | -103.85 |
| n-C4H10 | g | -126.15 |
| n-C5H12 | g | -146.44 |
| n-C6H14 | g | -166.92 |
| Benzene | g | +82.93 |
| Toluene | g | +50.17 |
| Methanol | l | -238.66 |
| Ethanol | l | -277.69 |
| H2S | g | -20.17 |
| SO2 | g | -296.83 |
| NH3 | g | -46.11 |

### Heats of Combustion (DeltaH_comb, kJ/mol, products H2O(l), CO2(g))

| Fuel | DeltaH_comb (kJ/mol) | DeltaH_comb (kJ/kg) | Notes |
|------|---------------------|---------------------|-------|
| H2(g) | -285.8 | -141,800 | HHV, H2O liquid |
| CH4(g) | -890.3 | -55,530 | HHV, water condensed |
| C2H6(g) | -1,559.7 | -51,900 | HHV |
| C3H8(g) | -2,219.2 | -50,350 | HHV |
| n-C4H10(g) | -2,877.1 | -49,500 | HHV |
| n-C5H12(g) | -3,536.1 | -48,990 | HHV |
| Methanol(l) | -726.5 | -22,675 | HHV |
| Ethanol(l) | -1,366.8 | -29,670 | HHV |
| Carbon(s) | -393.5 | -32,780 | Complete to CO2 |

---

## Liquid Cp Values for Process Design

Approximate constant Cp values for process design (moderate T range):

| Fluid | Cp [kJ/(kg-K)] | Cp [BTU/(lb-F)] | Notes |
|-------|----------------|-----------------|-------|
| Water (25 C) | 4.18 | 0.998 | Standard reference |
| Seawater (produced water approx) | 3.93-4.05 | 0.94-0.97 | Depends on salinity |
| Crude oil (light, 35 API) | 1.97-2.09 | 0.47-0.50 | Temperature-dependent |
| Crude oil (heavy, 20 API) | 1.76-1.88 | 0.42-0.45 | Higher density, lower Cp |
| Methanol (liquid) | 2.51 | 0.600 | Hydrate inhibitor |
| Ethylene glycol (MEG, 50%) | 3.48 | 0.831 | Pipeline injection |
| Brine (10% NaCl) | 3.81 | 0.910 | Produced water approximation |
| Glycol solution (75% TEG) | 2.10 | 0.502 | Gas dehydration |

---

## Gas Cp Values at 1 atm (Constant Cp Approximation)

Approximate values for small T ranges around 25 C:

| Gas | Cp [J/(mol-K)] | Cp [kJ/(kg-K)] | Cp [BTU/(lb-F)] |
|-----|----------------|----------------|-----------------|
| H2 | 28.8 | 14.32 | 3.42 |
| N2 | 29.1 | 1.04 | 0.248 |
| O2 | 29.4 | 0.919 | 0.219 |
| CO | 29.1 | 1.04 | 0.248 |
| CO2 | 37.1 | 0.844 | 0.201 |
| H2O(g) | 33.6 | 1.86 | 0.445 |
| CH4 | 35.7 | 2.23 | 0.532 |
| C2H6 | 52.5 | 1.75 | 0.418 |
| C3H8 | 73.6 | 1.67 | 0.399 |
| Air | 29.1 | 1.00 | 0.240 |

For temperatures above ~300 C, use Shomate polynomials — Cp increases
significantly with T for polyatomic gases.

---

## Psychrometric / Humidity Data

For combustion and drying calculations involving humid air:

Humid air specific humidity (omega, kg water/kg dry air):
```
omega = 0.622 * P_w / (P_total - P_w)
```

Where P_w = partial pressure of water vapor.

Humid air specific enthalpy:
```
h_humid = Cp_dry * T + omega * (2501 + 1.805 * T)    [kJ/kg dry air, T in C]
```

At 25 C, 50% RH: omega = 0.0099 kg/kg, h = 50.1 kJ/kg dry air.
Effect on combustion: humid air reduces O2 partial pressure by ~1-2% at
typical conditions — usually neglected in engineering calculations.

---

## Heater-Treater Sizing Reference

Typical heat duty benchmarks for produced water/oil treatment:

| Wellstream Composition | dT Required (F) | Cp_mix [BTU/(lb-F)] | Q estimate |
|------------------------|-----------------|---------------------|------------|
| High water cut (>80%) | 40-80 | ~0.92 | Q = m_total * 0.92 * dT |
| Moderate water cut (~50%) | 60-100 | ~0.72 | Q = m_total * 0.72 * dT |
| Low water cut (<20%) | 80-120 | ~0.49 | Q = m_total * 0.49 * dT |
| Heavy crude/emulsion | 100-150 | ~0.65 | Q = m_total * 0.65 * dT |

Rule of thumb: 1 MMBtu/hr heater-treater capacity handles ~300-600 BPD
of wellstream depending on composition and temperature requirement.

---

## Flash Calculation Reference

### DePriester Chart K-values (approximate, for quick estimates)

K-values for natural gas components at selected T and P (equilibrium
K = y_i/x_i from DePriester nomograph):

At 100 F (38 C):
| Component | 50 psia | 100 psia | 200 psia | 400 psia | 600 psia |
|-----------|---------|----------|----------|----------|----------|
| CH4 | 35.0 | 17.5 | 8.8 | 4.4 | 2.9 |
| C2H6 | 5.2 | 2.6 | 1.3 | 0.65 | 0.43 |
| C3H8 | 1.2 | 0.60 | 0.30 | 0.15 | 0.10 |
| n-C4H10 | 0.37 | 0.19 | 0.093 | 0.047 | 0.031 |
| n-C5H12 | 0.12 | 0.062 | 0.031 | 0.016 | 0.010 |

**Note:** These are rough estimates from DePriester nomograph. For
engineering calculations, use NIST REFPROP or a process simulator (HYSYS,
DWSIM) with Peng-Robinson EOS for rigorous K-values. DePriester K-values
are useful for quick screening and classroom examples only.

---

## Python Utilities — Shomate Cp Integration

```python
def cp_shomate(T_K, A, B, C, D, E):
    """Calculate Cp at temperature T using Shomate equation.

    Args:
        T_K: temperature in K
        A, B, C, D, E: Shomate coefficients
    Returns:
        Cp in J/(mol-K)
    """
    t = T_K / 1000.0
    return A + B*t + C*t**2 + D*t**3 + E/t**2

def delta_h_shomate(T1_K, T2_K, A, B, C, D, E, F, H_ref):
    """Calculate H(T2) - H(T1) using Shomate equation.

    Args:
        T1_K, T2_K: temperatures in K
        Coefficients from NIST Shomate table
    Returns:
        Enthalpy difference in kJ/mol
    """
    def h_shomate(T_K):
        t = T_K / 1000.0
        return A*t + B*t**2/2 + C*t**3/3 + D*t**4/4 - E/t + F - H_ref
    return h_shomate(T2_K) - h_shomate(T1_K)

# Methane Shomate coefficients (298-1300 K)
CH4_shomate = dict(A=-0.703029, B=108.4773, C=-42.52157,
                   D=5.862788, E=0.678565, F=-76.84376, H_ref=-74.87310)

# Example: Cp and enthalpy increment for methane at 800 K vs 298 K
T1 = 298.15  # K
T2 = 800.0   # K
cp_T2 = cp_shomate(T2, **{k: v for k,v in CH4_shomate.items() if k != 'F' and k != 'H_ref'})
dh = delta_h_shomate(T1, T2, **CH4_shomate)
print(f"Cp(CH4, 800K) = {cp_T2:.2f} J/(mol-K)")
print(f"H(800K) - H(298K) = {dh:.3f} kJ/mol")
```

---

## Unit Conversion Reference

| Quantity | From | To | Factor |
|----------|------|----|--------|
| Energy | kJ | BTU | 0.9478 |
| Energy | BTU | kJ | 1.0551 |
| Energy | kJ/mol | BTU/lbmol | 430.2 |
| Energy | BTU/lbmol | kJ/mol | 0.002326 |
| Specific energy | kJ/kg | BTU/lb | 0.4299 |
| Specific energy | BTU/lb | kJ/kg | 2.3260 |
| Power | kW | BTU/hr | 3412 |
| Power | MMBtu/hr | kW | 293.1 |
| Cp | kJ/(kg-K) | BTU/(lb-F) | 0.2388 |
| Cp | BTU/(lb-F) | kJ/(kg-K) | 4.187 |
| Cp | J/(mol-K) | BTU/(lbmol-R) | 0.2390 |
| Flow | kg/s | lb/hr | 7936.6 |
| Flow | lb/hr | kg/s | 0.0001260 |
| Flow | MMscf/d | mol/s | 327.4 (at 60F, 14.73 psia) |
| Temp | C to K | C + 273.15 | — |
| Temp | F to R | F + 459.67 | — |
| Temp | F to C | (F-32)*5/9 | — |
| Pressure | MPa | psia | 145.04 |
| Pressure | psia | MPa | 0.006895 |
| Pressure | bar | MPa | 0.1 |
| Pressure | atm | MPa | 0.10133 |
