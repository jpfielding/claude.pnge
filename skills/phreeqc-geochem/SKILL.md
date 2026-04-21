---
name: phreeqc-geochem
description: >
  Run PHREEQC (USGS geochemical modeling code) to compute aqueous speciation,
  mineral saturation indices, and scaling/precipitation predictions for produced
  waters and oilfield brines. Use this skill whenever the user asks about brine
  chemistry modeling, scaling prediction (barite, calcite, gypsum, celestite,
  halite, anhydrite), saturation index (SI), aqueous speciation, activity
  coefficients, ion interference in direct lithium extraction (DLE), produced
  water treatability, or any question needing thermodynamic equilibrium
  calculations. Trigger phrases: PHREEQC, speciation, saturation index, SI,
  scaling prediction, scaling tendency, barite scaling, calcite scaling, gypsum
  scaling, brine chemistry, aqueous geochemistry, Pitzer model, activity
  coefficient, high-TDS brine, will this brine scale, DLE interference,
  equilibrium speciation, mineral solubility, sulfate scaling, carbonate
  scaling. Selects the right thermodynamic database for the ionic strength,
  builds the input deck, runs PHREEQC, and interprets the SI table.
---

# PHREEQC Aqueous Geochemistry Skill

Runs the USGS PHREEQC (pH-REdox-EQuilibrium in C) geochemical code to compute
speciation, activity coefficients, and mineral saturation indices for produced
waters and high-TDS oilfield brines. This skill is the chemistry complement to
the `usgs-produced-waters` skill: once you know the brine composition, use this
to decide whether it will scale, whether DLE is viable, and which minerals
control Li/Mg recovery.

---

## Credential

**None required.** PHREEQC is free, open-source USGS software. No API key,
no login, no rate limits. The only prerequisite is a local `phreeqc` binary.

```bash
# Template for consistency with other skills; not used here:
# KEY=$(grep '^api_key=' ~/.config/usgs/credentials 2>/dev/null | cut -d= -f2)
```

---

## Install

PHREEQC must be installed locally. This skill does not install it for you —
ask the user to pick one of the methods below.

| Platform | Method | Command |
|----------|--------|---------|
| macOS (Homebrew tap) | `brew` via `geo-smart` or third-party tap | No official `homebrew-core` formula. Build from source or use conda. |
| macOS / Linux (conda) | conda-forge | `conda install -c conda-forge phreeqc` (verify with `conda search phreeqc -c conda-forge`) |
| Linux (apt) | Debian/Ubuntu | `sudo apt install phreeqc` (may lag USGS release) |
| All platforms | Official USGS build | Download from https://www.usgs.gov/software/phreeqc-version-3 |
| Source | Autotools / CMake | `./configure && make && sudo make install` |

**Current version (as of Jan 2025):** PHREEQC 3.8.6 (build 17100), released
January 7, 2025. USGS releases 1-2 builds per year; check the official page
for the latest.

**Verify install:**
```bash
phreeqc --version
# or
phreeqc -v
```

**Find the database directory:**
```bash
# Standard install locations:
ls /usr/local/share/doc/phreeqc/database/   # Linux source build
ls /opt/homebrew/share/phreeqc/database/    # Homebrew ARM
ls $CONDA_PREFIX/share/doc/phreeqc/database/ # conda
ls "C:\Program Files\USGS\phreeqc-3.8.6\database\"  # Windows

# Or search:
find / -name "pitzer.dat" 2>/dev/null | head
```

Set `PHREEQC_DATABASE_DIR` env var (or pass the full path as the second CLI
argument) so input decks don't need to hardcode paths.

---

## Command-Line Interface

PHREEQC is a single binary invoked with up to four positional arguments:

```
phreeqc [input_file] [output_file] [database_file] [screen_output_file]
```

| Position | Meaning | Example |
|----------|---------|---------|
| 1 | Input deck | `marcellus_brine.pqi` |
| 2 | Main output (long) | `marcellus_brine.pqo` |
| 3 | Thermodynamic database | `/opt/homebrew/share/phreeqc/database/pitzer.dat` |
| 4 | Screen log (short) | `marcellus_brine.log` |

**Minimal run:**
```bash
phreeqc input.pqi output.pqo $DB/pitzer.dat
```

Exit code: 0 on success, non-zero on parse or convergence errors. Stderr
captures most diagnostics; parse errors also appear at the top of the output
file.

---

## Workflow

### Step 1 — Resolve Intent

Map the user's question to a PHREEQC simulation type:

| User asks about... | PHREEQC block |
|--------------------|---------------|
| "Will this brine scale?" | `SOLUTION` + `EQUILIBRIUM_PHASES` or `SELECTED_OUTPUT` with `-saturation_indices` |
| "What's the SI of barite in sample X?" | `SOLUTION` + `SELECTED_OUTPUT` |
| "Speciation of this produced water" | `SOLUTION` (then read output) |
| "Will calcite precipitate if I raise pH?" | `SOLUTION` + `REACTION` (add NaOH) + `EQUILIBRIUM_PHASES` |
| "What if I dilute this 10:1?" | `SOLUTION` + `MIX` |
| "What happens as I heat this to 90 C?" | `SOLUTION` + `REACTION_TEMPERATURE` |
| "DLE feedstock check" | Compute SI for barite, celestite, calcite, gypsum, halite; report Ca/Li, Mg/Li, SO4/Li ratios |

### Step 2 — Select Database

Critical decision. The wrong database produces nonsense at oilfield ionic
strengths. See `references/thermo_databases.md` for the full matrix.

| Database | TDS range | Best for | Key limitation |
|----------|-----------|----------|----------------|
| `phreeqc.dat` | < 30,000 mg/L | Fresh / brackish water | Davies / extended Debye-Huckel; unreliable above seawater ionic strength |
| `wateq4f.dat` | < 30,000 mg/L | Natural waters with many trace metals | Same activity model limits as phreeqc.dat; more elements |
| `pitzer.dat` | > 30,000 mg/L, up to halite saturation | Produced waters, Smackover, Marcellus, Bakken, seawater evaporites | Limited element set; Li, Sr, Ba parameters incomplete at high T |
| `sit.dat` | Intermediate ionic strength | Mid-salinity, nuclear waste studies | Less mature than Pitzer for Cl brines |
| `llnl.dat` | < 30,000 mg/L but wider T/P | High-temperature geothermal | B-dot activity model; not for hypersaline |
| `minteq.v4.dat` | Dilute | EPA MINTEQA2 port; contamination / sorption | Not for brines |
| `frezchem.dat` | Sub-zero to moderate T | Cryogenic / sea-ice chemistry | Niche |

**Default for produced-water work: `pitzer.dat`.** Produced waters from
Marcellus, Utica, Bakken, and Smackover routinely exceed 100,000 mg/L TDS —
well outside the Debye-Huckel range of `phreeqc.dat`.

### Step 3 — Build the Input Deck

PHREEQC input is block-structured. Each block starts with a keyword. Minimum
useful deck has `SOLUTION`, `SELECTED_OUTPUT`, and `END`.

```
TITLE Marcellus produced water - scaling check
SOLUTION 1
    temp      60         # deg C
    pH        5.8
    pe        4.0
    redox     pe
    units     mg/l
    density   1.12        # optional; Pitzer calculates if omitted
    Na        45000
    K         600
    Ca        12000
    Mg        1200
    Sr        2500
    Ba        2000
    Li        80
    Cl        95000  charge   # balance charge on Cl
    Alkalinity 120 as HCO3
    S(6)      50           # SO4 as sulfate-S(6)
    Br        800
    Fe(2)     30
    B         20
    Si        15
SELECTED_OUTPUT
    -file           marcellus.sel
    -reset          false
    -saturation_indices Barite Calcite Celestite Gypsum Anhydrite Halite \
                        Strontianite Witherite Siderite Dolomite
    -molalities     Li+ Mg+2 Ca+2 Ba+2 Sr+2 SO4-2
    -totals         Li Mg Ca Ba Sr S(6)
    -ionic_strength true
    -temperature    true
    -pH             true
END
```

**Key gotchas in the deck:**

- Units: `mg/L` is per liter of solution; `mg/kgs` is per kg of solution
  (better for hypersaline). `ppm` is ambiguous — avoid.
- Charge balance: append `charge` to one major ion (usually Cl or Na). PHREEQC
  will adjust that concentration to balance.
- Alkalinity: report `as HCO3` or `as CaCO3`; PHREEQC computes the carbonate
  speciation at the input pH.
- Redox: for produced water, `pe 4` or lower is realistic; highly reducing
  formations may need `pe -2` to `0`. The skill should ask if the user cares
  about Fe/sulfide redox.
- Barium + sulfate: report both even if SO4 is low; barite supersaturation is
  a common surprise.
- Element lists in `-molalities` and `-saturation_indices` are
  whitespace-separated; use `\` for line continuation.

### Step 4 — Run PHREEQC

```bash
DB=/opt/homebrew/share/phreeqc/database   # adjust for your install
phreeqc marcellus.pqi marcellus.pqo $DB/pitzer.dat marcellus.log

# Check exit code
if [ $? -ne 0 ]; then
  grep -i 'error\|warning' marcellus.pqo | head -20
fi
```

### Step 5 — Parse Output

Two output streams:

1. **Main output** (`marcellus.pqo`): human-readable, contains every block
   executed. Big but browsable. Look for the `Saturation indices` table and
   the `Distribution of species` table.
2. **Selected output** (`marcellus.sel`): tab-delimited; one row per
   simulation. Easy to pipe into awk, pandas, or Go.

**Extracting SI values from `marcellus.sel`:**
```bash
# Header row has si_<mineral> columns
head -1 marcellus.sel | tr '\t' '\n' | grep -n '^si_'
awk -F'\t' 'NR==1 || NR==2' marcellus.sel | cut -f $(header_cols)
```

**Go wrapper** — see `references/golang_wrapper.go` — shells out, captures
both output files, parses the SELECTED_OUTPUT TSV, and returns a `SIReport`
struct with SI values keyed by mineral name.

### Step 6 — Interpret Saturation Indices

The saturation index is:
```
SI = log10(IAP / Ksp)
```
where IAP is the ion activity product and Ksp is the solubility product at
the given T and P.

| SI range | Interpretation | Action in produced-water context |
|----------|----------------|----------------------------------|
| SI > 1   | Strongly supersaturated | Likely already precipitating; scale forming downhole or at surface |
| 0 < SI < 1 | Supersaturated | Will precipitate given nucleation sites / time; add scale inhibitor |
| -0.3 < SI < 0 | Near equilibrium | Watch on T/P/pH change; borderline |
| SI < -0.3 | Undersaturated | Dissolution if mineral present; safe from that scale |

**Practical thresholds from oilfield experience:**
- Barite (`Barite`, BaSO4): SI > 0.5 = real scaling risk; inhibitor required
- Calcite (`Calcite`, CaCO3): SI > 0.5 triggers scale with CO2 loss
- Gypsum / Anhydrite: SI > 0 with high temperature often means scaling
- Halite (`Halite`, NaCl): SI ~ 0 means brine is at salt saturation; rare but
  seen in some evaporite-hosted produced waters
- Celestite (`Celestite`, SrSO4): track when Sr > 500 mg/L and SO4 detectable

**For DLE assessment:**
- Mg/Li molar ratio > 40 is hard to treat with most DLE resins
- Ca/Li > 100 is a treatment burden but manageable
- Any barite supersaturation + SO4 in produced water = barite scaling during
  sorbent regeneration
- Li speciation: in Cl brines, Li is ~90-100% free Li+; LiCl0 pair is minor

---

## Complete Working Example

**Input (`smackover_example.pqi`):**
```
TITLE Smackover Formation brine - Columbia County, AR - DLE screening
SOLUTION 1
    temp      80
    pH        5.5
    pe        2.0
    redox     pe
    units     mg/l
    density   1.20
    Na        85000
    K         3500
    Ca        40000
    Mg        3000
    Sr        1500
    Ba        50
    Li        400
    Cl        180000  charge
    Alkalinity 50 as HCO3
    S(6)      200
    Br        5000
    B         200
SELECTED_OUTPUT
    -file           smackover.sel
    -reset          false
    -saturation_indices Barite Calcite Celestite Gypsum Anhydrite Halite \
                        Dolomite Strontianite Witherite
    -molalities     Li+ LiCl Mg+2 MgCl+ Ca+2 CaCl+ Ba+2 Sr+2 SO4-2
    -totals         Li Mg Ca Ba Sr S(6) Cl
    -ionic_strength true
END
```

**Run:**
```bash
DB=/opt/homebrew/share/phreeqc/database
phreeqc smackover_example.pqi smackover.pqo $DB/pitzer.dat
```

**Expected output highlights (`smackover.pqo`):**
```
Saturation indices
--------------------
    Phase               SI**    log IAP   log K(T,  P)

    Anhydrite          -0.12    -4.54     -4.42   CaSO4
    Barite              0.34    -9.63     -9.97   BaSO4
    Calcite            -0.45   -10.00     -9.55   CaCO3
    Celestite          -0.72    -7.22     -6.50   SrSO4
    Dolomite           -1.10   -18.10    -17.00   CaMg(CO3)2
    Gypsum             -0.01    -4.59     -4.58   CaSO4:2H2O
    Halite             -0.85    -2.43     -1.58   NaCl
    Strontianite       -1.40   -10.50     -9.10   SrCO3
    Witherite          -2.90   -11.50     -8.60   BaCO3

Ionic strength        = 5.9 mol/kgw
Density               = 1.198 g/cm3
```

**Interpretation:** This Smackover brine is slightly supersaturated with
respect to barite (SI = 0.34) — mild scaling risk, manageable with inhibitor.
Gypsum is at equilibrium (SI ~ 0) — any cooling or CO2 loss will push it
over. Calcite is undersaturated, so CO2 loss / pH rise from atmospheric
exposure would flip it positive. Ionic strength of 5.9 mol/kgw is firmly in
Pitzer territory — `phreeqc.dat` would have been wrong by 0.5-1.5 log units
on most SIs.

---

## Output Format

Present PHREEQC results as **SI table + narrative + action items**:

```
## Smackover Brine — Speciation and Scaling Analysis (Pitzer, 80 deg C)

Inputs: TDS ~320,000 mg/L; Ca 40,000; Mg 3,000; Li 400; Ba 50; SO4 200 mg/L.
Database: pitzer.dat (ionic strength 5.9 mol/kgw — Pitzer required).

| Mineral      | SI    | Status              | Action                          |
|--------------|-------|---------------------|---------------------------------|
| Barite       | +0.34 | Supersaturated      | Inhibitor (phosphonate) needed  |
| Gypsum       | -0.01 | At equilibrium      | Monitor; any cooling precipitates |
| Anhydrite    | -0.12 | Near saturation     | Scaling risk if T rises         |
| Calcite      | -0.45 | Undersaturated      | Watch pH / CO2 degassing        |
| Celestite    | -0.72 | Undersaturated      | OK                              |
| Halite       | -0.85 | Undersaturated      | OK (no evaporation concentration) |

**Speciation:** Li+ free ion fraction = 97%; LiCl0 ion pair = 3%. Mg/Li
molar ratio = 29 — manageable for modern DLE sorbents (<40 threshold).
Ca/Li = 173 — high but tolerable for lithium-ion-sieve or solvent
extraction processes.

**Summary:** DLE-viable feedstock. Primary concern is barite scaling during
sorbent regeneration when SO4 concentrates. Gypsum is the second-priority
scale if the process includes any evaporative step. Ionic strength is high
enough that only Pitzer-based models should be trusted for plant design;
re-run in OLI or equivalent commercial code before final engineering.
```

---

## Error Handling

| Issue | Cause | Action |
|-------|-------|--------|
| `phreeqc: command not found` | Binary not installed or not in PATH | See Install section; run `which phreeqc` |
| `ERROR: Could not open database file` | Wrong path or missing .dat file | `find / -name "pitzer.dat"`; set `PHREEQC_DATABASE_DIR` or pass full path as 3rd arg |
| `ERROR: Unknown element` | Element not in selected database | Switch database (e.g., Li is in pitzer.dat but limited in sit.dat); check `references/thermo_databases.md` |
| `WARNING: Charge imbalance > 5%` | Input analysis not electroneutral | Append `charge` to Cl or Na concentration; check for missing major ion |
| `ERROR: Numerical method failed` | Convergence failure; often from contradictory constraints | Remove `charge` flag from multiple ions; relax pe constraint; check for negative concentrations |
| SI values wildly different from expected | Wrong database for ionic strength | Recheck: hypersaline needs pitzer.dat; phreeqc.dat fails above ~1 mol/kg |
| No SI for a mineral | Mineral not defined in database | Check `PHASES` block in the .dat file; some minerals (e.g., specific Li minerals) exist only in llnl.dat or require manual definition |
| `pe` and `redox` contradict | Both specified incorrectly | Use `redox pe` with a `pe` value, or use a redox couple like `redox O(0)/O(-2)` with dissolved O2 |
| Output file contains only echo of input | Parse error stopped execution | Look for first `ERROR` in `.pqo`; usually a syntax error in one block |

---

## Caveats and Bias

1. **Pitzer parameter gaps for Li at high T and I.** The Pitzer interaction
   coefficients for Li-Cl, Li-SO4, and Li-HCO3 in `pitzer.dat` are
   well-calibrated at 25 deg C but extrapolate with larger uncertainty above
   80-100 deg C and ionic strengths above 6 mol/kgw. For Smackover-style
   brines at reservoir temperature (90-110 deg C), SI values on
   Li-bearing minerals carry ~0.3-0.5 log unit uncertainty.

2. **Limited element set in `pitzer.dat`.** Not every element is parameterized.
   Notably weak/absent: Al, Si, Fe(III), trace metals beyond the majors.
   If those matter, run parallel `phreeqc.dat` for comparison (accepting the
   ionic strength caveat) or switch to `llnl.dat` (accepting its limits at
   high I).

3. **Temperature limits.** `pitzer.dat` is solid up to ~200 deg C for the
   major-ion system; extrapolation above that is unreliable without
   independent validation.

4. **Equilibrium != kinetics.** An SI > 0 says a mineral can precipitate,
   not that it will quickly. Barite nucleates fast; calcite and dolomite
   often do not. Field-observed scale is biased toward fast-kinetic phases
   even when slower phases are more supersaturated. Report SI alongside
   known-kinetic notes; do not substitute for reactive-transport modeling.

5. **Input data quality drives output quality.** A produced-water analysis
   with 10% charge imbalance produces SI values that look precise but rest on
   a badly constrained solution. Always report the charge balance from the
   `SOLUTION` echo. Treat SI differences < 0.3 log units as noise.

6. **pH measurement on hot brines.** Wellhead pH is often measured after
   cooling and depressurization, at which point CO2 has degassed and Fe(II)
   has partially oxidized. The measured pH is not the reservoir pH. For
   reservoir-condition modeling, adjust pH upward ~0.5-1 unit and re-run.

7. **CBI / self-reported chemistry.** If the brine composition comes from
   industry disclosures (FracFocus, operator reports), sulfate and bicarbonate
   are frequently reported as "< detection limit" without the limit value.
   PHREEQC treats these as exactly the numeric value given; set a realistic
   detection-limit value rather than zero.

8. **No coupled flow.** This skill runs batch equilibrium. Real produced
   water changes composition as it flows through pipe, heat exchangers, and
   tanks. For design work, couple to a reactive-transport code (PhreeqcRM,
   PHT3D) or commercial OLI / Multiflash.

9. **Commercial-software comparison.** OLI Studio and Multiflash use
   proprietary parameter sets that can disagree with PHREEQC Pitzer by 0.2-0.5
   log units on SI at hypersaline conditions. Use PHREEQC for screening and
   open-science work; expect a commercial cross-check before capex decisions.

---

## Implementation Notes

- **Prefer `bash_tool`** to shell out to `phreeqc`; parse the TSV
  SELECTED_OUTPUT rather than the long `.pqo` for machine use.
- **Go wrapper** — see `references/golang_wrapper.go` for a reference
  implementation: runs the binary, reads the `.sel` file, returns a typed
  struct with SIs and key molalities.
- **Database reference** — see `references/thermo_databases.md` for the full
  matrix of which database to use at which ionic strength, element coverage,
  and known limitations.
- **Ready-made brine decks** — see `references/brine_recipes.md` for sample
  input decks for Smackover, Marcellus, Utica/Point Pleasant, and Bakken
  chemistries with typical Li/Mg/Ca/Sr/Ba/Cl/SO4 values. Use these as
  starting points and overwrite with sample-specific numbers.
- **Cache binary location** — once located, write the path to
  `~/.config/phreeqc/config` so repeated runs skip the `find` step.
- **Default database:** if the user does not specify and TDS > 30,000 mg/L
  (or ionic strength can be estimated > 0.7 mol/kg), default to `pitzer.dat`;
  otherwise default to `phreeqc.dat`.
- **Never** hardcode `Windows`-style paths; resolve via env var or shell
  find.
- PHREEQC is a local compute skill — nothing is sent to a remote API. All
  inputs and outputs stay on the user's machine.
