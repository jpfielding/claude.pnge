# Brine Recipes — Sample PHREEQC Input Decks by Formation

Ready-to-run PHREEQC input decks for the four most important U.S. Li/Mg-target
formations. Each deck uses typical median or high-Li composition from the
USGS National Produced Waters Geochemical Database (v3.0). Replace the
concentrations with your sample-specific numbers when you have them.

**All decks default to `pitzer.dat`** (required at these ionic strengths).

**All decks use `mg/L`** for input; `charge` is appended to Cl to balance.

**All decks set `redox pe`** with a moderately reducing pe appropriate to
producing-zone conditions.

---

## 1. Smackover Formation (AR / TX / LA — highest U.S. brine Li)

Typical chemistry: Jurassic carbonate reservoir, 2,500-4,000 m depth,
80-120 deg C reservoir T, Na-Ca-Cl brine, 200,000-350,000 mg/L TDS. Li 100-477
mg/L makes it the premier U.S. DLE target (Standard Lithium, ExxonMobil,
TetraLithium projects).

```
TITLE Smackover Fm brine - Columbia Co AR - median high-Li - DLE screen
DATABASE /opt/homebrew/share/phreeqc/database/pitzer.dat
SOLUTION 1
    temp      90
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
    Fe(2)     30
SELECTED_OUTPUT
    -file           smackover.sel
    -reset          false
    -saturation_indices Barite Calcite Celestite Gypsum Anhydrite Halite \
                        Dolomite Strontianite Witherite Siderite
    -molalities     Li+ LiCl Mg+2 MgCl+ Ca+2 CaCl+ Ba+2 Sr+2 SO4-2 HCO3-
    -totals         Li Mg Ca Ba Sr S(6) Cl
    -ionic_strength true
    -temperature    true
    -pH             true
    -water          true
END
```

**Expected trouble spots:**
- Barite SI typically +0.2 to +0.8 (moderate risk — inhibitor required)
- Anhydrite near saturation at reservoir T; gypsum supersaturated after cooling
- Halite SI rises as water is concentrated during DLE

---

## 2. Marcellus Shale (WV / PA / OH — large volumes)

Typical chemistry: Middle Devonian shale, 1,500-2,500 m depth, 50-80 deg C
reservoir T, Na-Ca-Cl-(Br) brine, 100,000-300,000 mg/L TDS. Li 10-200 mg/L
(median ~60, high end in deep WV wells). Large produced-water volumes make
even modest Li content strategically interesting.

```
TITLE Marcellus Shale produced water - WV SW - typical high-Li well
DATABASE /opt/homebrew/share/phreeqc/database/pitzer.dat
SOLUTION 1
    temp      60
    pH        5.8
    pe        2.5
    redox     pe
    units     mg/l
    density   1.12
    Na        45000
    K         600
    Ca        12000
    Mg        1200
    Sr        2500
    Ba        2000
    Li        80
    Cl        95000  charge
    Alkalinity 120 as HCO3
    S(6)      50
    Br        800
    B         20
    Fe(2)     30
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

**Expected trouble spots:**
- Ba 2,000 mg/L + SO4 50 mg/L = severe barite scaling risk; SI typically > 1
- Sr 2,500 mg/L — celestite moderate risk
- Iron from Fe(II) oxidation at surface creates iron carbonate scale
- Low initial SO4 (Marcellus is sulfate-starved) means barite risk emerges
  when mixing with oxidized surface water or scale-inhibitor-carrier sulfate

**Marcellus-specific modeling tip:** add a second `SOLUTION` block for
oxidized surface water and a `MIX` step to test blending scenarios — barite
SI explodes when the two are combined.

---

## 3. Utica / Point Pleasant (OH / WV / PA — deep, hotter, co-produced)

Typical chemistry: Upper Ordovician carbonate-rich organic shale, 2,500-4,000
m depth (deeper than Marcellus), 80-120 deg C reservoir T, Na-Ca-Cl brine,
150,000-300,000 mg/L TDS. Li 20-150 mg/L (median ~80-90 in high-Li plays in
SE Ohio and NE WV).

```
TITLE Utica/Point Pleasant brine - SE Ohio - typical
DATABASE /opt/homebrew/share/phreeqc/database/pitzer.dat
SOLUTION 1
    temp      95
    pH        5.6
    pe        2.0
    redox     pe
    units     mg/l
    density   1.15
    Na        60000
    K         1500
    Ca        20000
    Mg        1800
    Sr        3500
    Ba        800
    Li        95
    Cl        130000  charge
    Alkalinity 80 as HCO3
    S(6)      100
    Br        2000
    B         40
    Fe(2)     20
    Si        18
SELECTED_OUTPUT
    -file           utica.sel
    -reset          false
    -saturation_indices Barite Calcite Celestite Gypsum Anhydrite Halite \
                        Strontianite Witherite Siderite Dolomite Magnesite
    -molalities     Li+ Mg+2 Ca+2 Ba+2 Sr+2 SO4-2 HCO3-
    -totals         Li Mg Ca Ba Sr S(6)
    -ionic_strength true
    -temperature    true
    -pH             true
END
```

**Expected trouble spots:**
- Higher T + higher Ca drives anhydrite / gypsum risk harder than Marcellus
- Calcite-dolomite equilibrium relevant (carbonate-hosted reservoir)
- Sr > Ba here (opposite of Marcellus); celestite dominates over barite as
  scaling concern

---

## 4. Bakken (ND / MT — large volumes, moderate Li)

Typical chemistry: Upper Devonian - Lower Mississippian tight oil, 2,500-3,500
m depth, 100-130 deg C reservoir T, Na-Ca-Cl brine, 150,000-350,000 mg/L TDS.
Li 10-70 mg/L (median ~25-35). Huge produced-water volumes compensate for
moderate Li concentration.

```
TITLE Bakken produced water - Williston Basin ND - typical
DATABASE /opt/homebrew/share/phreeqc/database/pitzer.dat
SOLUTION 1
    temp      110
    pH        5.5
    pe        1.5
    redox     pe
    units     mg/l
    density   1.18
    Na        90000
    K         2500
    Ca        25000
    Mg        2500
    Sr        800
    Ba        60
    Li        35
    Cl        195000  charge
    Alkalinity 40 as HCO3
    S(6)      350
    Br        3000
    B         60
    Fe(2)     40
    Si        20
SELECTED_OUTPUT
    -file           bakken.sel
    -reset          false
    -saturation_indices Barite Calcite Celestite Gypsum Anhydrite Halite \
                        Dolomite Strontianite Siderite Magnesite
    -molalities     Li+ Mg+2 Ca+2 Ba+2 Sr+2 SO4-2
    -totals         Li Mg Ca Ba Sr S(6)
    -ionic_strength true
    -temperature    true
END
```

**Expected trouble spots:**
- High reservoir T + SO4 350 mg/L = anhydrite commonly supersaturated
- Calcium carbonate scale during CO2 flash at surface
- Lower Ba than Appalachian brines, but not zero; barite still a watch item
- Halite SI approaches 0 in the highest-TDS samples; salt drop-out possible
  as brine cools

---

## 5. Generic Template (Unknown Formation)

When the user supplies a brine analysis without naming a formation, start
here and adjust:

```
TITLE Generic high-TDS produced water - user sample
DATABASE /opt/homebrew/share/phreeqc/database/pitzer.dat
SOLUTION 1
    temp      <USER_T_CELSIUS>
    pH        <USER_PH>
    pe        2.0
    redox     pe
    units     mg/l
    density   <USER_SG>
    Na        <USER_NA>
    K         <USER_K>
    Ca        <USER_CA>
    Mg        <USER_MG>
    Sr        <USER_SR>
    Ba        <USER_BA>
    Li        <USER_LI>
    Cl        <USER_CL>  charge
    Alkalinity <USER_HCO3> as HCO3
    S(6)      <USER_SO4>
    Br        <USER_BR>
    Fe(2)     <USER_FE>
SELECTED_OUTPUT
    -file           sample.sel
    -reset          false
    -saturation_indices Barite Calcite Celestite Gypsum Anhydrite Halite \
                        Dolomite Strontianite Witherite Siderite
    -molalities     Li+ Mg+2 Ca+2 Ba+2 Sr+2 SO4-2
    -totals         Li Mg Ca Ba Sr S(6)
    -ionic_strength true
END
```

---

## Add-On Blocks for Common Scenarios

### A. Surface cooling / flash to atmospheric

Cool the reservoir brine to 25 deg C and equilibrate with atmospheric CO2 to
see which scales precipitate on surface:

```
USE SOLUTION 1
REACTION_TEMPERATURE 2
    25
EQUILIBRIUM_PHASES 2
    CO2(g)    -3.5   10    # log P_CO2 = -3.5 atm (atmospheric)
    Calcite   0      0     # precipitate only if SI > 0
    Barite    0      0
    Celestite 0      0
    Gypsum    0      0
SAVE SOLUTION 2
END
```

### B. Dilution with fresh water

```
SOLUTION 2
    temp 20
    pH 7.5
    units mg/l
    Ca 20
    Mg 5
    Na 10
    Cl 15
    Alkalinity 50 as HCO3
MIX 3
    1   0.5    # 50% reservoir brine
    2   0.5    # 50% fresh water
SAVE SOLUTION 3
END
```

### C. Acid addition (DLE pre-treatment)

```
USE SOLUTION 1
REACTION 4
    HCl 1.0
    0.1 moles in 10 steps
SAVE SOLUTION 4
END
```

### D. pH adjustment to precipitate Mg (common DLE pre-treatment)

Raise pH to 10.5 with NaOH to drop out brucite Mg(OH)2 before lithium
extraction:

```
USE SOLUTION 1
REACTION 5
    NaOH 1.0
    0.05 moles in 20 steps
EQUILIBRIUM_PHASES 5
    Brucite   0   0
    Calcite   0   0
    Mg(OH)2   0   0
SAVE SOLUTION 5
END
```

### E. Evaporative concentration

Remove 90% of the water (common in evaporation-pond scenarios):

```
USE SOLUTION 1
REACTION 6
    H2O   -1
    50 moles
EQUILIBRIUM_PHASES 6
    Halite    0   0
    Sylvite   0   0
    Gypsum    0   0
    Calcite   0   0
    Barite    0   0
SAVE SOLUTION 6
END
```

---

## Concentration Reference Ranges (from USGS NPWGD v3.0)

Typical medians and 90th percentiles for the top four formations (mg/L
unless noted):

| Species | Smackover | Marcellus | Utica | Bakken |
|---------|----------:|----------:|------:|-------:|
| TDS | 250,000 / 350,000 | 145,000 / 250,000 | 170,000 / 270,000 | 200,000 / 320,000 |
| Na | 70,000 / 100,000 | 40,000 / 70,000 | 50,000 / 80,000 | 80,000 / 110,000 |
| Ca | 35,000 / 60,000 | 10,000 / 25,000 | 18,000 / 32,000 | 20,000 / 40,000 |
| Mg | 2,500 / 5,000 | 1,250 / 2,500 | 1,500 / 3,000 | 2,000 / 4,000 |
| K | 3,000 / 6,000 | 500 / 1,200 | 1,200 / 2,500 | 2,000 / 4,500 |
| Sr | 1,200 / 3,000 | 2,100 / 4,500 | 3,000 / 5,500 | 700 / 1,800 |
| Ba | 30 / 150 | 1,500 / 4,000 | 600 / 1,800 | 50 / 200 |
| Cl | 160,000 / 220,000 | 90,000 / 160,000 | 110,000 / 180,000 | 160,000 / 230,000 |
| SO4 | 150 / 600 | 30 / 150 | 80 / 300 | 300 / 900 |
| HCO3 | 40 / 150 | 100 / 300 | 70 / 200 | 30 / 120 |
| Br | 4,500 / 7,000 | 700 / 1,800 | 1,800 / 3,500 | 2,500 / 5,000 |
| Li | 200 / 400 | 60 / 150 | 85 / 140 | 30 / 65 |

Format: `median / P90`.

Source: summary statistics from USGS NPWGD v3.0; see `usgs-produced-waters`
skill for direct queries. These are ranges for guidance — actual wells vary
by 2-3x in either direction.

---

## Running All Recipes in Batch

```bash
#!/usr/bin/env bash
DB=/opt/homebrew/share/phreeqc/database/pitzer.dat
for deck in smackover marcellus utica bakken; do
  phreeqc ${deck}.pqi ${deck}.pqo $DB ${deck}.log
  echo "==== $deck ===="
  awk -F'\t' 'NR==1{for(i=1;i<=NF;i++) h[i]=$i}
              NR==2{for(i=1;i<=NF;i++) if(h[i]~/^si_/) printf "%-12s %+.2f\n", h[i], $i}' \
    ${deck}.sel
done
```

This gives you a quick SI summary across all four formations for comparison.
