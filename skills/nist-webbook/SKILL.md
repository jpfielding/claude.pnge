---
name: nist-webbook
description: >
  Query NIST WebBook for thermodynamic and transport properties of pure fluids
  including natural gas components, CO2, water, and hydrocarbon solvents.
  Provides vapor pressure, density, viscosity, thermal conductivity, heat
  capacity, enthalpy, entropy, and phase equilibrium data. Use this skill when
  the user asks about thermodynamic properties of a fluid, vapor pressure at a
  given temperature, density of methane at reservoir conditions, viscosity of
  CO2 for injection design, heat capacity of natural gas components, steam
  tables, equation of state properties, or any physical property of a pure
  substance. Trigger for phrases like "viscosity of methane at 200F and 3000
  psi", "density of CO2 at reservoir conditions", "vapor pressure of water at
  150C", "heat capacity of ethane", "enthalpy of methane at wellhead
  conditions", "steam table properties", "natural gas component properties",
  "thermodynamic properties of propane", or any pure fluid property query.
  Returns tabulated saturation or single-phase properties with units.
---

# NIST WebBook Thermodynamic Properties Skill

Fetches thermodynamic and transport properties of pure fluids from the NIST
Chemistry WebBook (webbook.nist.gov) using the fluid properties CGI interface.
Covers natural gas components, CO2, water/steam, and common solvents relevant
to petroleum and chemical engineering.

**No API key required.** NIST WebBook is a free public resource.

---

## API Structure

**Base URL:** `https://webbook.nist.gov/cgi/fluid.cgi`

The NIST fluid properties interface returns tab-delimited ASCII text with a
header row. All property data is in the requested unit system.

### Core Parameters

| Parameter | Description | Example Values |
|-----------|-------------|----------------|
| `Action` | Request type | `Load` |
| `ID` | Fluid identifier (CAS-based, e.g. C74828) | See fluid table below |
| `Type` | Property table type | `SatT`, `SatP`, `IsoTherm`, `IsoBar`, `IsoChor` |
| `Digits` | Significant figures | `5` (recommended) |
| `THigh` | Upper temperature bound | `300` |
| `TLow` | Lower temperature bound | `100` |
| `TInc` | Temperature increment | `10` |
| `PHigh` | Upper pressure bound (for IsoTherm) | `10` |
| `PLow` | Lower pressure bound | `1` |
| `PInc` | Pressure increment | `1` |
| `RefState` | Reference state | `DEF` (default), `NBP`, `IIR`, `ASHRAE` |

### Unit Parameters

| Parameter | Options |
|-----------|---------|
| `TUnit` | `K`, `C`, `F`, `R` |
| `PUnit` | `MPa`, `bar`, `atm`, `psia`, `kPa` |
| `DUnit` | `mol%2FL` (mol/L), `kg%2Fm3` (kg/m3), `g%2FmL` (g/mL) |
| `HUnit` | `kJ%2Fmol`, `kJ%2Fkg`, `BTU%2Flbmol` |
| `WUnit` | `m%2Fs` (m/s), `ft%2Fs` (ft/s) |
| `VisUnit` | `uPa*s` (microPa-s), `cP` (centipoise) |
| `STUnit` | `N%2Fm` (N/m), `dyn%2Fcm` |

### Type Parameter Reference

| Type | Description | Required Params |
|------|-------------|-----------------|
| `SatT` | Saturation properties vs temperature | THigh, TLow, TInc |
| `SatP` | Saturation properties vs pressure | PHigh, PLow, PInc |
| `IsoTherm` | Isothermal P scan at fixed T | THigh=TLow=T, PHigh, PLow, PInc |
| `IsoBar` | Isobaric T scan at fixed P | PHigh=PLow=P, THigh, TLow, TInc |
| `IsoChor` | Isochoric (constant volume) | DHigh, DLow, DInc |

---

## Fluid ID Reference

See `references/api_reference.md` for the complete fluid list. Key fluids
for petroleum and chemical engineering:

| Fluid | NIST ID | CAS Number | Notes |
|-------|---------|------------|-------|
| Methane | C74828 | 74-82-8 | Primary natural gas component |
| Ethane | C74840 | 74-84-0 | NGL component |
| Propane | C74986 | 74-98-6 | NGL, LPG |
| n-Butane | C106978 | 106-97-8 | NGL |
| i-Butane | C75285 | 75-28-5 | NGL |
| n-Pentane | C109660 | 109-66-0 | NGL |
| n-Hexane | C110543 | 110-54-3 | Solvent, NGL |
| n-Heptane | C142825 | 142-82-5 | Solvent |
| n-Octane | C111659 | 111-65-9 | Solvent |
| Carbon dioxide | C124389 | 124-38-9 | EOR, injection design |
| Water | C7732185 | 7732-18-5 | Steam tables, reservoir |
| Nitrogen | C7727379 | 7727-37-9 | Injection gas |
| Hydrogen sulfide | C7783064 | 7783-06-4 | Sour gas |
| Hydrogen | C1333740 | 1333-74-0 | Hydrogen applications |
| Oxygen | C7782447 | 7782-44-7 | Combustion |
| Argon | C7440371 | 7440-37-1 | Inert gas |
| Helium | C7440597 | 7440-59-7 | Tracer |
| Ammonia | C7664417 | 7664-41-7 | Refrigerant |
| R-134a (HFC) | C811972 | 811-97-2 | Refrigerant |

---

## Example API Calls

### Saturation Properties — Methane from 100 K to 200 K

```bash
curl -s "https://webbook.nist.gov/cgi/fluid.cgi?Action=Load&ID=C74828&Type=SatT&Digits=5&THigh=200&TLow=100&TInc=10&RefState=DEF&TUnit=K&PUnit=MPa&DUnit=mol%2FL&HUnit=kJ%2Fmol&WUnit=m%2Fs&VisUnit=uPa*s&STUnit=N%2Fm"
```

### Saturation Properties — Water from 100 C to 374 C (steam tables)

```bash
curl -s "https://webbook.nist.gov/cgi/fluid.cgi?Action=Load&ID=C7732185&Type=SatT&Digits=5&THigh=374&TLow=100&TInc=10&RefState=DEF&TUnit=C&PUnit=MPa&DUnit=kg%2Fm3&HUnit=kJ%2Fkg&WUnit=m%2Fs&VisUnit=uPa*s&STUnit=N%2Fm"
```

### Isothermal Properties — CO2 at 50 C from 1 to 20 MPa

```bash
curl -s "https://webbook.nist.gov/cgi/fluid.cgi?Action=Load&ID=C124389&Type=IsoTherm&Digits=5&THigh=50&TLow=50&TInc=0&PHigh=20&PLow=1&PInc=1&RefState=DEF&TUnit=C&PUnit=MPa&DUnit=kg%2Fm3&HUnit=kJ%2Fkg&WUnit=m%2Fs&VisUnit=uPa*s&STUnit=N%2Fm"
```

### Isobaric Properties — Methane at 3000 psia from 200 F to 400 F

```bash
curl -s "https://webbook.nist.gov/cgi/fluid.cgi?Action=Load&ID=C74828&Type=IsoBar&Digits=5&THigh=400&TLow=200&TInc=10&PHigh=3000&PLow=3000&PInc=0&RefState=DEF&TUnit=F&PUnit=psia&DUnit=kg%2Fm3&HUnit=kJ%2Fkg&WUnit=m%2Fs&VisUnit=uPa*s&STUnit=N%2Fm"
```

### Parse Tab-Delimited Response (bash + awk)

```bash
curl -s "https://webbook.nist.gov/cgi/fluid.cgi?..." \
  | awk -F'\t' 'NR==1{print; next} /^\s*$/{next} {print}' \
  | column -t -s $'\t'
```

---

## Workflow

### Step 1 — Identify Fluid

Map the user's fluid description to a NIST fluid ID. Use the table above or
the extended reference in `references/api_reference.md`. If the user specifies
a mixture (e.g., "natural gas"), note that NIST WebBook covers pure components
only — compute mixture properties by combining component data using mixing
rules, or advise using NIST REFPROP for rigorous mixture calculations.

### Step 2 — Identify Property Type and Conditions

Determine the appropriate query type:
- **Saturation curve** (vapor pressure, boiling point, latent heat): use `SatT` or `SatP`
- **Single-phase P-v-T** at fixed temperature: use `IsoTherm`
- **Single-phase H-S at fixed pressure** (process design): use `IsoBar`
- **Specific P-T point**: use `IsoTherm` with PHigh=PLow and small pressure range

Convert user units to NIST parameter values. Common conversions:
- 200 F = 93.3 C = 366.5 K
- 3000 psia = 20.68 MPa
- 1 cp = 1000 uPa*s

### Step 3 — Build URL and Fetch

Construct the URL using the base URL and parameters above. Execute with curl.
Check that the response starts with column headers (Temperature, Pressure,
etc.) — if it starts with "Error" or "Not Found", the fluid ID or range is
invalid.

### Step 4 — Parse Response

The response is tab-delimited text. Key output columns:

| Column | Description | Typical Units |
|--------|-------------|---------------|
| Temperature | T | K or C or F |
| Pressure | P | MPa or psia |
| Density | rho | kg/m3 |
| Volume | v | m3/kg |
| Internal Energy | U | kJ/kg |
| Enthalpy | H | kJ/kg |
| Entropy | S | kJ/(kg-K) |
| Cv | Isochoric heat capacity | kJ/(kg-K) |
| Cp | Isobaric heat capacity | kJ/(kg-K) |
| Sound Spd. | Speed of sound | m/s |
| Joule-Thomson | J-T coefficient | K/MPa |
| Viscosity | Dynamic viscosity | uPa*s |
| Therm. Cond. | Thermal conductivity | W/(m-K) |
| Phase | Phase label | liquid / vapor / supercritical |

For saturation queries, NIST returns two rows per temperature: one for the
liquid phase and one for the vapor phase.

### Step 5 — Identify Phase and Produce Output

Note the phase from the Phase column. Flag if conditions are:
- **Supercritical:** T > Tc and P > Pc (CO2: Tc=31.1 C, Pc=7.38 MPa;
  CH4: Tc=-82.6 C, Pc=4.60 MPa; H2O: Tc=374.0 C, Pc=22.06 MPa)
- **Two-phase:** user requested single-phase type but conditions cross the
  saturation curve — split into separate saturation query plus single-phase
  queries above and below

Include a brief note on engineering relevance (viscosity for wellbore flow,
density for hydrostatic head, Cp for heat duty calculations).

---

## Output Format

Present results as a markdown table capped at ~25 rows for readability. Always
state temperature, pressure, and fluid name in the table title. Then provide a
narrative summary.

```
## Methane Properties — Isothermal at 300 K, 1-20 MPa

| P (MPa) | Density (kg/m3) | Enthalpy (kJ/kg) | Viscosity (uPa-s) | Phase |
|---------|-----------------|------------------|-------------------|-------|
| 1.0     | 6.33            | 864.2            | 11.2              | vapor |
| 5.0     | 34.0            | 836.8            | 12.4              | vapor |
| 10.0    | 76.3            | 793.1            | 14.9              | vapor |
| 15.0    | 131.2           | 737.6            | 19.1              | vapor |
| 20.0    | 194.4           | 672.3            | 25.8              | supercritical |

**Summary:** Methane at 300 K transitions from dilute gas behavior at low
pressure to a dense, increasingly liquid-like fluid above ~15 MPa.
Density increases 30x from 1 to 20 MPa. Viscosity increases only 2.3x
over the same range — important for reservoir flow models, which are
sensitive to viscosity but less so at these values (methane remains low
viscosity even at reservoir conditions). At 300 K, methane is above its
critical temperature (190.6 K) at all pressures shown — no phase change
occurs. For WVU Appalachian wells at ~2000-4000 psia (14-28 MPa) and
200-300 F (93-149 C), methane is always supercritical.
```

---

## Error Handling

| Condition | Action |
|-----------|--------|
| Response contains "Error" text | Invalid fluid ID or out-of-range T/P; check ID against reference table and verify T/P within fluid's valid range |
| Response is empty after header | Temperature or pressure outside the fluid's valid range; adjust bounds |
| Phase boundary crossed in IsoTherm | Two-phase region encountered; switch to SatT query for that range, then IsoTherm above and below saturation |
| Fluid ID not in table | Search NIST WebBook manually at webbook.nist.gov/cgi/cbook.cgi?Name=FLUID&Units=SI and copy the fluid ID from the "Fluid Properties" link URL |
| Mixture requested (e.g., natural gas) | NIST WebBook covers pure components only; compute mixture properties by component fraction weighting, or recommend NIST REFPROP for rigorous mixture EOS |
| Very large T/P range returns too many rows | Increase TInc or PInc to reduce row count |

---

## Caveats and Data Limitations

- **Pure components only.** NIST WebBook does not calculate mixture properties.
  For mixtures (natural gas, reservoir fluids), use component-level data with
  appropriate mixing rules or advise the user to use REFPROP or a process
  simulator.
- **Reference state matters for enthalpy and entropy.** Values are relative to
  the chosen reference state (DEF = NIST default, usually 0 K or NBP). Do not
  mix enthalpies from different reference states.
- **Data accuracy varies by fluid.** Equation of state accuracy is highest for
  well-studied fluids (methane, water, CO2, propane). Less common fluids may
  have higher uncertainty, especially near the critical point.
- **Near-critical region is difficult.** Within ~10% of Tc and Pc, properties
  diverge rapidly (infinite Cp at Tc, Pc). Use smaller increments near the
  critical point.
- **Engineering correlations vs. NIST.** The tNav/tnav-reservoir-sim skill uses
  Standing, Beggs-Robinson, and similar empirical correlations calibrated to
  specific fluid types. NIST WebBook is more accurate for pure components. Use
  NIST for precise single-component property lookups, and correlations for
  reservoir fluid mixtures where compositional data is unavailable.

---

## Implementation Notes

- Use `bash_tool` with `curl` to make requests; pipe through `awk` or `python`
  to parse the tab-delimited output
- For unit conversion: multiply uPa*s by 0.001 to get cp (centipoise);
  multiply kJ/kg by 0.4299 to get BTU/lb
- See `references/api_reference.md` for the complete fluid ID table (50+
  fluids), all unit codes, and worked examples in Go
- Critical constants for key fluids are in `references/api_reference.md`
