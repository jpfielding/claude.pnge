# PHREEQC Thermodynamic Databases — Reference

PHREEQC ships with ~20 thermodynamic database files. Choosing the right one
for a given problem is the single biggest decision in PHREEQC modeling —
wrong database, wrong answer. This file is the decision table for
produced-water / brine work.

Standard databases distributed with PHREEQC 3.x (from `usgs-coupled/iphreeqc`
`database/` directory):

```
Amm.dat           ColdChem.dat     Concrete_PHR.dat    Concrete_PZ.dat
Kinec.v2.dat      Kinec_v3.dat     Kinec_v3_4.dat      PHREEQC_ThermoddemV1.10_15Dec2020.dat
Tipping_Hurley.dat core10.dat      frezchem.dat        iso.dat
llnl.dat          minimum.dat      minteq.dat          minteq.v4.dat
phreeqc.dat       phreeqc_rates.dat pitzer.dat          sit.dat
stimela.dat       wateq4f.dat
```

---

## Decision Matrix for Produced-Water / Brine Work

| Database | Activity Model | Ionic Strength Ceiling | Temperature Range | Best Use | Pitfalls |
|----------|----------------|-----------------------:|------------------:|----------|----------|
| `phreeqc.dat` | Davies + WATEQ Debye-Huckel | ~0.5-1 mol/kgw (~30 k mg/L TDS) | 0-100 deg C (some species to 200) | Dilute waters, fresh groundwater, rainwater, river water | Breaks above seawater I; Li interactions modest; redox with many couples supported |
| `wateq4f.dat` | Davies / B-dot | ~0.5-1 mol/kgw | 0-100 deg C | Trace-metal-rich natural waters; expanded element coverage vs phreeqc.dat | Same I ceiling as phreeqc.dat; preferred when you need more transition metals |
| `pitzer.dat` | Pitzer ion-interaction | Up to halite saturation (~6.5 mol/kgw) | 0-200 deg C for major system | **Produced water, oilfield brine, hypersaline, seawater evaporites, geothermal brine** | Limited elements (majors + some trace); Li parameters sparse at high T; no Al / Si above trace |
| `sit.dat` | Specific Ion Interaction Theory | Intermediate (< ~3 mol/kgw typical) | 25 deg C emphasis | Nuclear-waste repository work; actinide chemistry | Fewer fit parameters than Pitzer in Cl brines; less mature for produced water |
| `llnl.dat` | B-dot (extended Debye-Huckel) | ~1 mol/kgw | 0-300 deg C | High-temperature geothermal, hydrothermal, ore-forming fluids | B-dot model unreliable in Cl brines above ~1 mol/kgw; wide element coverage |
| `minteq.dat` / `minteq.v4.dat` | Davies | Dilute | 0-100 deg C | EPA MINTEQA2-style contamination modeling, soil / sediment porewaters | Not intended for brines; sorption-focused |
| `frezchem.dat` | Pitzer (cryogenic) | High I with low T | -60 deg C to +25 deg C | Sea-ice chemistry, sub-zero brine, planetary ice analogs | Niche; do not use above 25 deg C |
| `ColdChem.dat` | Pitzer (low-T) | High I at low T | Sub-zero focus | Cold-climate brines | As above; specialized |
| `core10.dat` | B-dot | ~1 mol/kgw | Wider T | THEREDA-compatible modeling | Less mature; verify coverage |
| `PHREEQC_ThermoddemV1.10_15Dec2020.dat` | Davies | Dilute-to-moderate | 0-100 deg C | BRGM Thermoddem port; many clay / cement phases | Not a brine database |
| `Concrete_PHR.dat` / `Concrete_PZ.dat` | Davies / Pitzer | Variable | Variable | Cement and concrete chemistry | Not for produced water |
| `iso.dat` | N/A | Dilute | 25 deg C | Stable isotope fractionation (1H, 18O, 13C, 34S, 87Sr) | Use alongside another database for chemistry |
| `Amm.dat` | Davies | Dilute | 0-100 deg C | Ammonia / ammonium redox chemistry add-on | Specialized |
| `Tipping_Hurley.dat` | WHAM-style | Dilute | 0-100 deg C | Humic / fulvic binding of metals | Specialized |

---

## Rule of Thumb for Produced Waters

Compute **ionic strength** first (can be estimated from TDS):

```
I ~= TDS (mg/L) * 2 * 10^-5    (very rough, for NaCl-dominated brines)
```

| TDS (mg/L) | Approx I (mol/kgw) | Recommended DB |
|-----------:|-------------------:|----------------|
| < 10,000 | < 0.2 | `phreeqc.dat` or `wateq4f.dat` |
| 10,000 - 30,000 | 0.2 - 0.6 | `phreeqc.dat` (borderline); `pitzer.dat` if Ca/Mg/SO4 high |
| 30,000 - 100,000 | 0.6 - 2 | `pitzer.dat` |
| 100,000 - 250,000 | 2 - 5 | `pitzer.dat` (only sensible choice) |
| > 250,000 | > 5 | `pitzer.dat`; close to halite saturation; verify output |

Produced waters from Marcellus, Utica, Bakken, and Smackover almost always
fall in the 100,000 - 300,000 mg/L TDS range — **Pitzer is mandatory**.

---

## Pitzer-Specific Notes

### Element coverage in `pitzer.dat` (PHREEQC 3.8)

Present with full Pitzer parameterization:
- Major ions: Na, K, Ca, Mg, Sr, Ba, Fe(II), Mn
- Major anions: Cl, SO4, HCO3 / CO3, Br, OH, F
- Acid/base system: H+, OH-, CO2(aq), H2S
- Trace that works: Li, Cs, Rb (limited T range)

Marginal or absent:
- Al — present as simple species; reliable only below I ~ 0.5
- Si — only as H4SiO4 neutral; Pitzer params limited
- Fe(III) — incomplete; redox treatment poor at high I
- Heavy metals (Pb, Zn, Cd, Cu) — absent from Pitzer; use another DB

### Li at high ionic strength and temperature

PHREEQC's `pitzer.dat` Li-Cl interaction parameters are calibrated by
Harvie-Moller-Weare (1984) and Pitzer & Mayorga (1973) at 25 deg C. Extension
to 90-110 deg C (reservoir T for Smackover) uses temperature-dependence terms
that become less reliable above 75 deg C. Practical implication:

- Speciation of Li at reservoir T has ~5-10% uncertainty in free-Li fraction
- SI for Li-bearing minerals (cryptomelane, jadarite, etc.) is not trustworthy
- The ratio Li / (Na + K) is robust; the absolute LiCl0 ion pair fraction is
  less so

For production-critical decisions at reservoir T, benchmark PHREEQC against
OLI MSE or ChemApp / FactSage.

### Temperature handling

Pitzer.dat parameters are validated:
- Major-ion system (Na-K-Ca-Mg-Cl-SO4-CO3): 0-200 deg C
- Ba, Sr in SO4 system: 25-150 deg C robust
- Above 200 deg C: switch to `llnl.dat` and accept the ionic-strength hit, or
  use a commercial code

### Density calculation

`pitzer.dat` includes density calculation from Pitzer volume parameters
(Monnin 1989, 1994). Output density is typically within 1-2% of measured for
Na-Ca-Cl brines up to 5 mol/kgw. Always compare the PHREEQC `Density =` line
to the measured specific gravity of the sample — large disagreement signals a
bad analysis or a missing major ion.

---

## When to Use SIT vs Pitzer

- **SIT (`sit.dat`)**: preferred for actinides (U, Th, Np, Am) because the
  OECD-NEA thermodynamic database is SIT-based. Reliable up to
  ~3 mol/kgw for those systems.
- **Pitzer (`pitzer.dat`)**: preferred for oilfield / evaporite / seawater
  brines because the Harvie-Moller-Weare and subsequent parameterizations
  cover the Na-K-Ca-Mg-Cl-SO4-CO3 system extensively.

For produced water with trace uranium (e.g., Bakken, some Marcellus), there
is no perfect choice — run both and compare.

---

## Known Limitations Across All Databases

1. Kinetics are not built in; every database assumes equilibrium. For slow
   reactions (dolomite precipitation, silicate weathering), the SI > 0
   result does not mean precipitation occurs on operational time scales.

2. Solid solutions (Ba-Sr-SO4, Ca-Mg-CO3, clays) are crudely handled. PHREEQC
   has a `SOLID_SOLUTION` keyword but few databases define good end-member
   models for produced-water-relevant phases.

3. Organic acids (acetate, propionate) present in many produced waters are
   absent from Pitzer-based databases. If the water has high TOC (> 500 mg/L),
   Pitzer results on calcite / carbonate SIs may be biased.

4. Trace sulfide speciation (H2S / HS-) is covered in `phreeqc.dat` and
   `wateq4f.dat` but with simpler activity models; `pitzer.dat` treats it
   more rigorously but with fewer metal-sulfide pairs.

---

## Custom and Extended Databases

Beyond the distribution, several community databases are useful:

| Source | Scope | Notes |
|--------|-------|-------|
| THEREDA | High-salt, nuclear waste | Distributed via therenda.de; more parameters than pitzer.dat for some systems |
| ThermoChimie | ANDRA / French nuclear | Wide coverage; PHREEQC-format available |
| CEMDATA | Cement chemistry | Specialized; not for oilfield work |
| YAMM (Yucca Mountain) | High-I specific | Historical |

For most PNGE produced-water work, the distributed `pitzer.dat` is
sufficient. If a specific problem demands better parameterization (e.g.,
Li-Mg-Cl at 120 deg C), cite the THEREDA or Thermoddem versions and document
the swap in the input deck `TITLE`.

---

## Cross-Checks

When the choice of database matters (ionic strength borderline, or a critical
decision):

1. Run the same input with `pitzer.dat` AND `phreeqc.dat` (or `llnl.dat`)
2. Compare SI values; differences > 0.5 log units signal a database-dependent
   answer — trust Pitzer at high I
3. If Pitzer says SI = 0 and Debye-Huckel says SI = +1 for barite, Pitzer is
   right (activity coefficient for Ba2+ is well below 1 in a concentrated
   brine)
4. Report both results in the narrative; explain which you trust

---

## References

- Parkhurst, D.L., and Appelo, C.A.J., 2013, Description of input and
  examples for PHREEQC version 3 — a computer program for speciation,
  batch-reaction, one-dimensional transport, and inverse geochemical
  calculations: U.S. Geological Survey Techniques and Methods, book 6, chap.
  A43, 497 p., https://pubs.usgs.gov/tm/06/a43/
- Harvie, C.E., Moller, N., and Weare, J.H., 1984, The prediction of mineral
  solubilities in natural waters — The Na-K-Mg-Ca-H-Cl-SO4-OH-HCO3-CO3-CO2-H2O
  system to high ionic strengths at 25 deg C: Geochimica et Cosmochimica
  Acta, v. 48, p. 723-751.
- Pitzer, K.S., 1991, Activity Coefficients in Electrolyte Solutions, 2nd
  ed.: CRC Press.
- USGS PHREEQC software page: https://www.usgs.gov/software/phreeqc-version-3
