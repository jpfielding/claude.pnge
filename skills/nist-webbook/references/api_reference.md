# NIST WebBook API Reference

Complete reference for the NIST Chemistry WebBook fluid properties CGI
interface (webbook.nist.gov/cgi/fluid.cgi).

---

## Base URL and Request Format

```
GET https://webbook.nist.gov/cgi/fluid.cgi?{parameters}
```

Response: tab-delimited ASCII text, first line is column headers, subsequent
lines are data rows. Empty lines may appear between phase regions in saturation
tables.

---

## Complete Parameter Reference

| Parameter | Values | Required | Notes |
|-----------|--------|----------|-------|
| `Action` | `Load` | Yes | Always use `Load` |
| `ID` | CXXXXXXx | Yes | Fluid identifier (see table below) |
| `Type` | SatT, SatP, IsoTherm, IsoBar, IsoChor | Yes | Property table type |
| `Digits` | 1-8 | Yes | Significant figures; use 5 for engineering |
| `THigh` | number | Yes (for T types) | Upper temperature |
| `TLow` | number | Yes (for T types) | Lower temperature |
| `TInc` | number | Yes (for T types) | Temperature step; 0 for single point |
| `PHigh` | number | For P types | Upper pressure |
| `PLow` | number | For P types | Lower pressure |
| `PInc` | number | For P types | Pressure step |
| `DHigh` | number | For IsoChor | Upper density |
| `DLow` | number | For IsoChor | Lower density |
| `DInc` | number | For IsoChor | Density step |
| `RefState` | DEF, NBP, IIR, ASHRAE | Yes | Reference state for H and S |
| `TUnit` | K, C, F, R | Yes | Temperature unit |
| `PUnit` | MPa, bar, atm, psia, kPa | Yes | Pressure unit |
| `DUnit` | mol%2FL, kg%2Fm3, g%2FmL | Yes | Density unit |
| `HUnit` | kJ%2Fmol, kJ%2Fkg, BTU%2Flbmol | Yes | Enthalpy/energy unit |
| `WUnit` | m%2Fs, ft%2Fs | Yes | Speed of sound unit |
| `VisUnit` | uPa*s, cP | Yes | Viscosity unit |
| `STUnit` | N%2Fm, dyn%2Fcm | Yes | Surface tension unit |

### Reference State Options

| Code | Description | H=0 at |
|------|-------------|--------|
| `DEF` | NIST default | Varies by fluid; usually NBP or 0 K |
| `NBP` | Normal boiling point | H=0, S=0 at 1 atm saturated liquid |
| `IIR` | IIR standard | H=200 kJ/kg, S=1.0 kJ/(kg-K) at 0 C saturated liquid |
| `ASHRAE` | ASHRAE standard | H=0, S=0 at -40 C saturated liquid |

**Note:** Always use the same RefState when comparing enthalpies. `DEF` is
sufficient for engineering calculations involving enthalpy differences.

---

## Fluid ID Reference — Petroleum Engineering Fluids

### Natural Gas Components

| Fluid | NIST ID | CAS | Tc (K) | Pc (MPa) | Vc (L/mol) | omega |
|-------|---------|-----|--------|----------|------------|-------|
| Methane | C74828 | 74-82-8 | 190.56 | 4.599 | 0.09860 | 0.0114 |
| Ethane | C74840 | 74-84-0 | 305.33 | 4.872 | 0.1455 | 0.0995 |
| Propane | C74986 | 74-98-6 | 369.83 | 4.248 | 0.2000 | 0.1521 |
| n-Butane | C106978 | 106-97-8 | 425.13 | 3.796 | 0.2550 | 0.2003 |
| i-Butane | C75285 | 75-28-5 | 407.82 | 3.629 | 0.2590 | 0.1853 |
| n-Pentane | C109660 | 109-66-0 | 469.70 | 3.370 | 0.3130 | 0.2510 |
| i-Pentane | C78784 | 78-78-4 | 460.35 | 3.378 | 0.3060 | 0.2274 |
| n-Hexane | C110543 | 110-54-3 | 507.82 | 3.034 | 0.3680 | 0.3013 |
| n-Heptane | C142825 | 142-82-5 | 540.13 | 2.736 | 0.4280 | 0.3495 |
| n-Octane | C111659 | 111-65-9 | 569.32 | 2.497 | 0.4860 | 0.3996 |
| Hydrogen sulfide | C7783064 | 7783-06-4 | 373.10 | 8.937 | 0.0985 | 0.0941 |
| Carbon dioxide | C124389 | 124-38-9 | 304.13 | 7.377 | 0.09407 | 0.2239 |
| Nitrogen | C7727379 | 7727-37-9 | 126.19 | 3.396 | 0.08921 | 0.0372 |
| Oxygen | C7782447 | 7782-44-7 | 154.58 | 5.043 | 0.07337 | 0.0222 |
| Hydrogen | C1333740 | 1333-74-0 | 33.19 | 1.296 | 0.06490 | -0.219 |
| Helium | C7440597 | 7440-59-7 | 5.196 | 0.2275 | 0.05740 | -0.385 |

### Water and Steam

| Fluid | NIST ID | CAS | Tc (K) | Pc (MPa) | Notes |
|-------|---------|-----|--------|----------|-------|
| Water | C7732185 | 7732-18-5 | 647.10 | 22.064 | IAPWS-IF97 standard |
| Heavy water (D2O) | C7789200 | 7789-20-0 | 643.85 | 21.671 | Isotope tracer studies |

### Solvents and Chemicals

| Fluid | NIST ID | CAS | Tc (K) | Pc (MPa) | Application |
|-------|---------|-----|--------|----------|-------------|
| Toluene | C108883 | 108-88-3 | 591.75 | 4.126 | Solvent, aromatic |
| Benzene | C71432 | 71-43-2 | 562.05 | 4.895 | Aromatic constituent |
| Cyclohexane | C110827 | 110-82-7 | 553.60 | 4.076 | Ring compound |
| Methanol | C67561 | 67-56-1 | 512.64 | 8.215 | Hydrate inhibitor |
| Ethanol | C64175 | 64-17-5 | 514.71 | 6.268 | Solvent |
| Acetone | C67641 | 67-64-1 | 508.10 | 4.700 | Solvent |
| Ammonia | C7664417 | 7664-41-7 | 405.56 | 11.333 | Refrigerant |
| Sulfur dioxide | C7446095 | 7446-09-5 | 430.64 | 7.884 | Acid gas |

### Refrigerants (for ChBE 231 thermodynamics problems)

| Fluid | NIST ID | CAS | Tc (K) | Pc (MPa) | Notes |
|-------|---------|-----|--------|----------|-------|
| R-134a | C811972 | 811-97-2 | 374.21 | 4.059 | HFC, common refrigerant |
| R-22 | C75456 | 75-45-6 | 369.30 | 4.990 | HCFC |
| R-410A | Not single fluid | — | — | — | Use REFPROP for mixtures |
| R-32 | C75105 | 75-10-5 | 351.26 | 5.782 | HFC |
| R-125 | C354336 | 354-33-6 | 339.17 | 3.617 | HFC |

---

## Output Column Reference

Columns returned by NIST depend on the property type. Standard columns for
most queries:

| Column Header (NIST) | Symbol | SI Units | Field Units |
|----------------------|--------|----------|-------------|
| Temperature (K) or (C) or (F) | T | K | F |
| Pressure (MPa) or (psia) | P | MPa | psia |
| Density (kg/m3) | rho | kg/m3 | lb/ft3 |
| Volume (m3/kg) | v | m3/kg | ft3/lb |
| Internal Energy (kJ/kg) | U | kJ/kg | BTU/lb |
| Enthalpy (kJ/kg) | H | kJ/kg | BTU/lb |
| Entropy (J/g*K) | S | kJ/(kg-K) | BTU/(lb-R) |
| Cv (J/g*K) | Cv | kJ/(kg-K) | BTU/(lb-R) |
| Cp (J/g*K) | Cp | kJ/(kg-K) | BTU/(lb-R) |
| Sound Spd. (m/s) | c | m/s | ft/s |
| Joule-Thomson (K/MPa) | mu_JT | K/MPa | F/(psia) |
| Viscosity (uPa*s) or (cP) | mu | uPa*s | cP |
| Therm. Cond. (W/m*K) | k | W/(m-K) | BTU/(hr-ft-F) |
| Phase | — | — | liquid / vapor / supercritical |

For saturation tables (SatT or SatP), two rows appear per temperature/pressure
point: one labeled "liquid" and one "vapor". The surface tension column (St.
Tension) appears only in saturation tables.

---

## Critical Constants and Triple Points

### Key Fluids for PNGE Applications

| Fluid | Tc (C) | Pc (MPa) | Tc (F) | Pc (psia) | Triple Pt T (K) |
|-------|--------|----------|--------|-----------|-----------------|
| Methane | -82.6 | 4.60 | -116.7 | 667.2 | 90.69 |
| Ethane | 32.2 | 4.87 | 89.9 | 706.6 | 90.35 |
| Propane | 96.7 | 4.25 | 206.0 | 616.4 | 85.53 |
| n-Butane | 151.9 | 3.80 | 305.5 | 550.6 | 134.89 |
| CO2 | 31.1 | 7.38 | 87.9 | 1070.1 | 216.59 |
| Water | 374.0 | 22.06 | 705.1 | 3200.1 | 273.16 |
| H2S | 99.9 | 8.94 | 211.9 | 1296.0 | 187.70 |
| N2 | -146.9 | 3.40 | -232.5 | 492.8 | 63.15 |

**Supercritical conditions in petroleum engineering:**
- CO2 for EOR injection: Tc=31.1 C, Pc=7.38 MPa — most injection depths
  (>600m) will be supercritical
- Methane in deep reservoirs: T > -82.6 C always in reservoirs; check if
  P > 4.60 MPa (667 psia) — yes for most reservoirs; methane is always
  supercritical in typical reservoirs

---

## Common Engineering Queries and URL Templates

### 1. Steam Tables (Water Saturation)

Temperature range 0-374 C, saturation properties:
```
https://webbook.nist.gov/cgi/fluid.cgi?Action=Load&ID=C7732185&Type=SatT&Digits=5&THigh=374&TLow=0&TInc=10&RefState=DEF&TUnit=C&PUnit=MPa&DUnit=kg%2Fm3&HUnit=kJ%2Fkg&WUnit=m%2Fs&VisUnit=uPa*s&STUnit=N%2Fm
```

### 2. Methane PVT at Reservoir Conditions

200-400 F isothermal, 500-5000 psia:
```
https://webbook.nist.gov/cgi/fluid.cgi?Action=Load&ID=C74828&Type=IsoTherm&Digits=5&THigh=300&TLow=300&TInc=0&PHigh=5000&PLow=500&PInc=250&RefState=DEF&TUnit=F&PUnit=psia&DUnit=kg%2Fm3&HUnit=kJ%2Fkg&WUnit=m%2Fs&VisUnit=uPa*s&STUnit=N%2Fm
```

### 3. CO2 Properties for EOR Injection Design

Single-phase CO2 above critical point:
```
https://webbook.nist.gov/cgi/fluid.cgi?Action=Load&ID=C124389&Type=IsoTherm&Digits=5&THigh=50&TLow=50&TInc=0&PHigh=25&PLow=7.5&PInc=0.5&RefState=DEF&TUnit=C&PUnit=MPa&DUnit=kg%2Fm3&HUnit=kJ%2Fkg&WUnit=m%2Fs&VisUnit=uPa*s&STUnit=N%2Fm
```

### 4. Propane Saturation Curve (NGL Processing)

```
https://webbook.nist.gov/cgi/fluid.cgi?Action=Load&ID=C74986&Type=SatT&Digits=5&THigh=96&TLow=-42&TInc=5&RefState=NBP&TUnit=C&PUnit=MPa&DUnit=kg%2Fm3&HUnit=kJ%2Fkg&WUnit=m%2Fs&VisUnit=uPa*s&STUnit=N%2Fm
```

### 5. H2S Properties for Sour Gas Wells

```
https://webbook.nist.gov/cgi/fluid.cgi?Action=Load&ID=C7783064&Type=IsoTherm&Digits=5&THigh=250&TLow=250&TInc=0&PHigh=15000&PLow=1000&PInc=500&RefState=DEF&TUnit=F&PUnit=psia&DUnit=kg%2Fm3&HUnit=kJ%2Fkg&WUnit=m%2Fs&VisUnit=uPa*s&STUnit=N%2Fm
```

---

## Go Client Example

```go
package main

import (
    "encoding/csv"
    "fmt"
    "io"
    "net/http"
    "net/url"
    "os"
    "strings"
)

// NISTQuery holds parameters for a NIST WebBook fluid properties query.
type NISTQuery struct {
    FluidID  string  // e.g. "C74828" for methane
    PropType string  // "SatT", "SatP", "IsoTherm", "IsoBar"
    THigh    float64 // upper temperature
    TLow     float64 // lower temperature
    TInc     float64 // temperature step
    PHigh    float64 // upper pressure (IsoTherm)
    PLow     float64 // lower pressure (IsoTherm)
    PInc     float64 // pressure step (IsoTherm)
    TUnit    string  // "K", "C", "F", "R"
    PUnit    string  // "MPa", "psia", "bar"
    DUnit    string  // "kg/m3", "mol/L"
    HUnit    string  // "kJ/kg", "kJ/mol"
}

// DefaultQuery returns a NISTQuery with sensible engineering defaults.
func DefaultQuery(fluidID string) NISTQuery {
    return NISTQuery{
        FluidID:  fluidID,
        PropType: "SatT",
        TUnit:    "K",
        PUnit:    "MPa",
        DUnit:    "kg/m3",
        HUnit:    "kJ/kg",
    }
}

// URL builds the complete NIST WebBook URL.
func (q NISTQuery) URL() string {
    base := "https://webbook.nist.gov/cgi/fluid.cgi"
    v := url.Values{}
    v.Set("Action", "Load")
    v.Set("ID", q.FluidID)
    v.Set("Type", q.PropType)
    v.Set("Digits", "5")
    v.Set("THigh", fmt.Sprintf("%g", q.THigh))
    v.Set("TLow", fmt.Sprintf("%g", q.TLow))
    v.Set("TInc", fmt.Sprintf("%g", q.TInc))
    if q.PropType == "IsoTherm" || q.PropType == "IsoBar" {
        v.Set("PHigh", fmt.Sprintf("%g", q.PHigh))
        v.Set("PLow", fmt.Sprintf("%g", q.PLow))
        v.Set("PInc", fmt.Sprintf("%g", q.PInc))
    }
    v.Set("RefState", "DEF")
    v.Set("TUnit", q.TUnit)
    v.Set("PUnit", q.PUnit)
    v.Set("DUnit", url.QueryEscape(q.DUnit))
    v.Set("HUnit", url.QueryEscape(q.HUnit))
    v.Set("WUnit", url.QueryEscape("m/s"))
    v.Set("VisUnit", "uPa*s")
    v.Set("STUnit", url.QueryEscape("N/m"))
    return base + "?" + v.Encode()
}

// Fetch retrieves tab-delimited data from NIST and returns headers + rows.
func Fetch(q NISTQuery) (headers []string, rows [][]string, err error) {
    resp, err := http.Get(q.URL())
    if err != nil {
        return nil, nil, fmt.Errorf("http get: %w", err)
    }
    defer resp.Body.Close()

    body, err := io.ReadAll(resp.Body)
    if err != nil {
        return nil, nil, fmt.Errorf("read body: %w", err)
    }

    // Check for error response
    bodyStr := string(body)
    if strings.Contains(bodyStr, "Error") || strings.Contains(bodyStr, "Not Found") {
        return nil, nil, fmt.Errorf("NIST returned error: %s", strings.TrimSpace(bodyStr[:200]))
    }

    r := csv.NewReader(strings.NewReader(bodyStr))
    r.Comma = '\t'
    r.LazyQuotes = true

    allRows, err := r.ReadAll()
    if err != nil {
        return nil, nil, fmt.Errorf("parse tsv: %w", err)
    }

    if len(allRows) < 2 {
        return nil, nil, fmt.Errorf("no data rows returned")
    }

    return allRows[0], allRows[1:], nil
}

func main() {
    // Example: methane saturation properties 100-200 K
    q := DefaultQuery("C74828")
    q.PropType = "SatT"
    q.TLow = 100
    q.THigh = 200
    q.TInc = 10

    headers, rows, err := Fetch(q)
    if err != nil {
        fmt.Fprintf(os.Stderr, "error: %v\n", err)
        os.Exit(1)
    }

    // Print header
    fmt.Println(strings.Join(headers, "\t"))
    for _, row := range rows {
        fmt.Println(strings.Join(row, "\t"))
    }
}
```

---

## Unit Conversion Reference

| From | To | Multiply by |
|------|----|-------------|
| uPa*s (microPascal-second) | cP (centipoise) | 0.001 |
| cP | uPa*s | 1000 |
| kJ/kg | BTU/lb | 0.4299 |
| BTU/lb | kJ/kg | 2.3260 |
| kJ/(kg-K) | BTU/(lb-R) | 0.2388 |
| MPa | psia | 145.04 |
| psia | MPa | 0.006895 |
| kg/m3 | lb/ft3 | 0.06243 |
| lb/ft3 | kg/m3 | 16.018 |
| W/(m-K) | BTU/(hr-ft-F) | 0.5779 |
| K | R | 1.8 |
| C to F | (C * 9/5) + 32 | — |
| F to C | (F - 32) * 5/9 | — |

---

## Valid T-P Ranges for Key Fluids

| Fluid | T_min (K) | T_max (K) | P_max (MPa) | EOS Used |
|-------|-----------|-----------|-------------|----------|
| Methane | 90.7 | 625 | 1000 | Setzmann & Wagner (1991) |
| Ethane | 90.4 | 675 | 900 | Buecker & Wagner (2006) |
| Propane | 85.5 | 650 | 1000 | Lemmon et al. (2009) |
| n-Butane | 134.9 | 575 | 69 | Buecker & Span (2006) |
| CO2 | 216.6 | 1100 | 800 | Span & Wagner (1996) |
| Water | 273.2 | 2000 | 1000 | IAPWS-IF97 / IAPWS-95 |
| H2S | 187.7 | 760 | 170 | Lemmon & Span (2006) |
| N2 | 63.2 | 2000 | 2200 | Span et al. (2000) |
