---
name: flow-assurance
description: >
  Predict and mitigate flow assurance problems in oil and gas wellbores and
  pipelines including hydrate formation, CO2 and H2S corrosion, wax deposition,
  and carbonate and sulfate scale. Covers hydrate prediction using the Katz
  chart gravity method and Hammerschmidt inhibitor dosage equation for methanol
  and glycol injection, CO2 partial pressure calculation and corrosion rate
  using the de Waard-Milliams equation, H2S partial pressure and NACE MR0175
  ISO 15156 sour service threshold determination, wax appearance temperature
  estimation and inhibition strategies, downhole carbonate scale LSI calculation
  and BaSO4 sulfate scale ion product, and chemical inhibitor selection and
  injection rate sizing. Use when evaluating hydrate risk in gas wells or
  pipelines, sizing methanol or glycol injection systems, assessing CO2
  corrosion and material selection, checking H2S sour service requirements,
  predicting wax or scale problems, or selecting production chemicals. Trigger
  phrases include hydrate prediction, methanol injection rate, CO2 corrosion
  rate, H2S sour service, wax appearance temperature, scale inhibitor, NACE
  MR0175, Hammerschmidt equation, flow assurance, or production chemistry.
---

# Flow Assurance and Production Chemistry

Wellbore and pipeline flow assurance skill covering hydrate prediction,
corrosion assessment, wax and scale risk, and chemical inhibitor design.

**Important:** Flow assurance problems are highly system-specific. Field
measurements (fluid samples, corrosion coupons, pigging data) are essential
for calibration. Use these equations for risk screening and initial sizing.

---

## Module 1 — Hydrate Prediction

### Hydrate Formation Temperature (Approximate Correlations)

```python
def hydrate_temp_katz(pressure_psia, gas_sg=0.65):
    """
    Approximate hydrate formation temperature using Katz (1945) gravity chart.
    Curve-fit to Katz chart for SG = 0.55–0.80:
    T_hyd (°F) ≈ a + b * ln(P)
    Coefficients for SG = 0.65 (representative Marcellus gas):
      a = -16.5, b = 13.0  (approximate, use chart for design)
    Returns hydrate temperature (°F) at given pressure.
    """
    import math
    # Curve-fit coefficients (SG-dependent; calibrate to actual composition)
    coeffs = {
        0.55: (-22.0, 13.5),
        0.60: (-19.5, 13.2),
        0.65: (-16.5, 13.0),
        0.70: (-13.0, 12.8),
        0.75: (-9.5,  12.5),
        0.80: (-6.0,  12.2),
    }
    # Find nearest SG
    sg_keys = sorted(coeffs.keys())
    sg_use = min(sg_keys, key=lambda s: abs(s - gas_sg))
    a, b = coeffs[sg_use]
    return a + b * math.log(pressure_psia)
```

### Hydrate Subcooling (Driving Force)

```python
def hydrate_subcooling(T_fluid_f, T_hyd_f):
    """
    Subcooling = T_hyd - T_fluid
    Positive subcooling = hydrate formation is thermodynamically favorable.
    > 5°F subcooling: moderate risk
    > 15°F subcooling: high risk — inhibition required
    """
    return T_hyd_f - T_fluid_f
```

### Hammerschmidt Inhibitor Dosage

```python
def hammerschmidt_inhibitor(delta_T_f, inhibitor="methanol"):
    """
    Hammerschmidt (1934): w = delta_T * Mi / (K + delta_T * Mi)
    delta_T_f: required hydrate depression (°F)
    w: weight fraction of inhibitor in aqueous phase
    K: 2335 for methanol, 4000 for ethylene glycol (MEG)
    Mi: molecular weight — 32 for methanol, 62 for MEG
    Returns: weight fraction of inhibitor needed in water phase
    """
    params = {
        "methanol": (2335, 32),
        "meg":      (4000, 62),
        "deg":      (4000, 62),   # approx same as MEG
    }
    K, Mi = params[inhibitor.lower()]
    return (delta_T_f * Mi) / (K + delta_T_f * Mi)

def methanol_injection_rate_gpd(w_inhibitor, water_rate_bpd):
    """
    Volume of methanol to inject per day.
    w_inhibitor: weight fraction from Hammerschmidt
    water_rate_bpd: free water production (bbl/day)
    Returns: methanol injection (gal/day)
    """
    water_mass_lb_day = water_rate_bpd * 42 * 8.34   # gal->lb at ~8.34 lb/gal
    methanol_mass_lb_day = w_inhibitor / (1 - w_inhibitor) * water_mass_lb_day
    return methanol_mass_lb_day / 6.59   # methanol density ~6.59 lb/gal
```

**Hydrate risk conditions — Appalachian Marcellus:**
- Wellhead pressure: 1,000–3,000 psia; Temperature: 40–70°F in winter
- Typical hydrate temperature at 1,500 psia, SG 0.65: ~68°F
- Risk highest during early production (high pressure + cold surface equipment)
- Mitigation: methanol injection at Christmas tree or wellhead heating

---

## Module 2 — CO2 Corrosion

### CO2 Partial Pressure

```python
def co2_partial_pressure(total_pressure_psia, co2_mol_frac):
    """
    pCO2 (bar) = y_CO2 * P_total (bar)
    Corrosion risk by pCO2:
      < 7 psia  (0.5 bar): low risk
      7–30 psia (0.5–2 bar): moderate risk
      > 30 psia (2 bar): high risk — corrosion inhibitor required
    """
    p_bar = total_pressure_psia * 0.06895
    return co2_mol_frac * p_bar
```

### de Waard-Milliams Corrosion Rate (1991)

```python
def co2_corrosion_rate(pco2_bar, T_C):
    """
    log10(CR) = 5.8 - 1710/T_K + 0.67 * log10(pCO2)
    T_C:       temperature (Celsius)
    pco2_bar:  CO2 partial pressure (bar)
    Returns:   corrosion rate (mm/year) — bare steel, no inhibitor
    """
    import math
    T_K = T_C + 273.15
    log_cr = 5.8 - 1710.0 / T_K + 0.67 * math.log10(pco2_bar)
    return 10**log_cr

def T_C_from_F(T_f):
    return (T_f - 32.0) / 1.8
```

**Material selection guidance:**
| CO2 Rate (mm/yr) | Assessment | Typical Response |
|-----------------|------------|-----------------|
| < 0.1 | Low | Carbon steel acceptable |
| 0.1–0.5 | Moderate | Corrosion inhibitor or CRA liner |
| > 0.5 | High | 13Cr or duplex stainless; inhibitor |
| > 1.0 | Severe | CRA tubing; aggressive monitoring |

---

## Module 3 — H2S Sour Service

### H2S Partial Pressure

```python
def h2s_partial_pressure(total_pressure_psia, h2s_ppm_mole):
    """
    pH2S (psia) = (h2s_ppm_mole / 1e6) * P_total
    NACE MR0175 / ISO 15156 sour service threshold: pH2S > 0.05 psia
    Region 1 (SSC): pH2S > 0.05 psia AND P_total > 65 psia
    """
    return (h2s_ppm_mole / 1e6) * total_pressure_psia

def is_sour_service(p_h2s_psia, p_total_psia):
    """
    Returns NACE MR0175 sour service classification.
    Region 0: Not sour
    Region 1: Sour — SSC risk for susceptible steels
    Region 2: Sour — HIC/SOHIC risk
    """
    if p_h2s_psia < 0.05:
        return "Region 0 — Not sour"
    elif p_h2s_psia >= 0.05 and p_total_psia >= 65:
        return "Region 1 — Sour: SSC risk (use L-80, C-90, or inhibitor)"
    else:
        return "Region 2 — Monitor; low SSC risk but H2S present"
```

**Steel grade restrictions in sour service (NACE MR0175):**
| Condition | Acceptable | Avoid |
|-----------|-----------|-------|
| pH2S > 0.05 psia | L-80, C-90, C-95, 13Cr | P-110, Q-125 |
| pH2S > 1.5 psia | L-80 type 1, 13Cr alloys | All high-strength grades |
| Produced water pH < 4 | CRA liners, coatings | All carbon steel |

---

## Module 4 — Wax

### Wax Appearance Temperature (Approximate)

```python
def wax_appearance_temp_estimate(api_gravity):
    """
    Rough WAT estimate from oil gravity (Dead oil, no dissolved gas).
    WAT correlates with paraffin content and oil API gravity.
    High-paraffin crudes (paraffinic): API 30–45
    WAT typically 70–130°F for Appalachian crude oils
    Use pour point data or laboratory WAT measurement for design.
    Returns: approximate WAT range (°F)
    """
    if api_gravity < 25:
        return (50, 90, "Low WAT, but high viscosity")
    elif api_gravity < 35:
        return (70, 110, "Moderate WAT risk")
    elif api_gravity < 45:
        return (90, 130, "High WAT risk — common Appalachian range")
    else:
        return (40, 80, "Light oil — lower paraffin content")
```

### Wax Inhibition Strategies

| Method | Application | Notes |
|--------|------------|-------|
| Chemical (PPD/WI) | Continuous injection | Modifies wax crystal structure |
| Pigging | Gathering system | Mechanical removal |
| Insulation / heat tracing | Subsea, cold climate | Keeps T > WAT |
| Hot-oil treatment | Remediation | Dissolves wax deposits |
| Coiled tubing cleanout | Well intervention | Mechanical removal |

---

## Module 5 — Scale Prediction

### Langelier Saturation Index (CaCO3)

```python
def langelier_saturation_index(pH, Ca_ppm, TDS_ppm, T_f, alk_ppm):
    """
    LSI = pH - pHs   where pHs is saturation pH for CaCO3
    pHs = pK2 - pKsp + pCa + pAlk  (Langelier method)
    LSI > 0: scaling tendency   LSI < 0: dissolving tendency
    Simplified correlation (Carrier 1965):
    pHs = (9.3 + A + B) - (C + D)
    A = log(TDS) - 1
    B = -13.12*log(T_C+273) + 34.55
    C = log(Ca) - 0.4
    D = log(Alk)
    """
    import math
    T_C = (T_f - 32) / 1.8
    A = math.log10(TDS_ppm) - 1.0
    B = -13.12 * math.log10(T_C + 273.15) + 34.55
    C = math.log10(Ca_ppm) - 0.4
    D = math.log10(alk_ppm)
    pHs = (9.3 + A + B) - (C + D)
    return pH - pHs
```

### BaSO4 Ion Product

```python
def baso4_ion_product(Ba_ppm, SO4_ppm):
    """
    IP = [Ba2+][SO42-]  (mol/L)^2
    Ksp(BaSO4) = 1.1e-10 at 25°C
    IP > Ksp -> precipitation risk
    Ba_ppm, SO4_ppm: concentrations (mg/L)
    """
    Ba_mol = Ba_ppm / 137340.0    # mg/L to mol/L
    SO4_mol = SO4_ppm / 96060.0   # mg/L to mol/L
    IP = Ba_mol * SO4_mol
    Ksp = 1.1e-10
    return {"IP": IP, "Ksp": Ksp, "saturation_ratio": IP / Ksp,
            "risk": "HIGH" if IP > Ksp else "LOW"}
```

---

## Module 6 — Chemical Inhibitor Selection

| Problem | Chemical Type | Typical Dosage | Injection Point |
|---------|--------------|---------------|-----------------|
| Hydrate | Methanol (MeOH) | 0.1–0.3 gal/Mscf | Wellhead / Christmas tree |
| Hydrate | MEG | 10–30% vol in water | Wellhead / subsea umbilical |
| CO2 corrosion | Imidazoline-based | 5–30 ppm continuous | Downhole via capillary |
| H2S corrosion | Triazine scavenger | 0.1–1 ppm H2S | Wellhead |
| CaCO3 scale | Phosphonate | 5–50 ppm | Downhole squeeze or continuous |
| BaSO4 scale | Phosphonate / DTPMPA | 5–20 ppm | Downhole squeeze |
| Wax | PPD / wax inhibitor | 200–1,000 ppm | Continuous tubing |

---

## Output Format

```
## Flow Assurance Risk Assessment — [Field / Well / Pipeline]
**P (psia):** XXXX | **T range (°F):** XX–XX | **Fluid:** Gas/Oil/Multiphase

### Hydrate Risk
| Location | P (psia) | T (°F) | T_hyd (°F) | Subcooling (°F) | Risk |
|----------|---------|------|------------|----------------|------|
| Wellhead | | | | | |
| Pipeline | | | | | |

**Inhibitor required:** YES/NO | MeOH dose: X gal/Mscf | Water rate: XXX bbl/day

### Corrosion Assessment
| pCO2 (bar) | CR (mm/yr) | pH2S (psia) | Sour? | Recommendation |
|-----------|-----------|-----------|-------|----------------|
| | | | | |

### Scale Risk
| Scale | Ion Product | Ksp | Ratio | Risk Level |
|-------|------------|-----|-------|-----------|
| CaCO3 | LSI: | — | — | |
| BaSO4 | | 1.1e-10 | | |

### Wax Risk: [LOW / MODERATE / HIGH]
WAT estimate: XX–XX°F | Flowing temp at well: XX°F

### Chemical Injection Summary
| Chemical | Dose | Injection Rate | Injection Point |
|---------|------|---------------|----------------|
| | | | |
```

---

## Error Handling

| Condition | Cause | Action |
|-----------|-------|--------|
| T_hyd negative | Very low pressure or light gas | Verify pressure input |
| Hammerschmidt w > 0.5 | Very large subcooling | Verify subcooling; consider heating |
| CR > 5 mm/yr | High pCO2 + high temperature | CRA tubulars required; inhibitor alone insufficient |
| BaSO4 ratio >> 1 | Mixing sulfate and barium water | Segregate source waters; squeeze inhibitor |
| LSI < -2 | Corrosive water (dissolving tendency) | CO2 corrosion likely dominant |

---

## Caveats

- Hydrate temperature from Katz chart is a gas-gravity approximation. CO2,
  H2S, and heavy components shift the hydrate curve — use NGAS, CSMHYD, or
  PVTsim for compositional fluids. CO2 forms hydrates at lower temperatures
  than methane.
- de Waard-Milliams gives bare steel corrosion rate. Protective FeCO3 scale at
  temperatures above ~140°F can reduce actual rates significantly. The
  Norsok M-506 model is more rigorous.
- Hammerschmidt equation is valid for w < 0.25 (weight fraction). For higher
  doses or kinetic inhibitors, use thermodynamic software.
- Scale prediction assumes equilibrium chemistry. Supersaturated conditions
  can persist kinetically, especially for BaSO4 (very slow nucleation).
- H2S sour service thresholds are for steel selection only. NACE MR0175 / ISO
  15156 should be reviewed in full for complete material qualification.
