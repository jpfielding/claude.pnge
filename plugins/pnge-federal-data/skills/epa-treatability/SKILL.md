---
name: epa-treatability
description: >
  Access EPA Drinking Water Treatability Database for treatment technology
  effectiveness data, contaminant removal efficiency, and process selection.
  Use when the user asks about treatment technology for produced water,
  contaminant removal, what process removes lithium or magnesium from water,
  reverse osmosis TDS removal, ion exchange for brine treatment, membrane
  effectiveness, treatment technology comparison, best available technology,
  PFAS treatment, removal efficiency, or percent removal by process.
  Trigger phrases: "treatment technology produced water", "removal efficiency
  reverse osmosis", "what removes lithium from water", "process comparison",
  "EPA treatability data", "BAT for TDS", "ion exchange performance",
  "membrane filtration effectiveness". Produces treatment technology
  comparison tables with removal efficiency and references.
---

# EPA Drinking Water Treatability Database Skill

Accesses the EPA Treatability Database (TDB) for referenced treatment
technology effectiveness data. Covers 30+ treatment processes and 120+
contaminants with removal efficiency data from peer-reviewed sources.

---

## Credential

**None required.** The EPA TDB is publicly accessible.

```bash
# No API key needed -- EPA TDB is open access
```

---

## Data Source

| Field | Value |
|-------|-------|
| Database | EPA Drinking Water Treatability Database (TDB) |
| URL | https://tdb.epa.gov/ |
| Coverage | 30+ treatment processes, 120+ contaminants (including 26 PFAS) |
| Data sources | Peer-reviewed journals, conferences, research reports, dissertations |
| Target audience | Water utilities, treatment designers, researchers |
| API | **No REST API** -- web interface only |
| Update frequency | Periodic (not real-time) |

**Important:** The EPA TDB does not have a public REST API. Data access is
through the web interface at https://tdb.epa.gov/. This skill documents the
manual access workflow and provides reference data for common treatment
processes relevant to produced water and brine treatment.

---

## Access Workflow (Web Interface)

### Search by Contaminant

1. Navigate to https://tdb.epa.gov/
2. Click "Find a Contaminant" or use the search bar
3. Select the contaminant of interest (e.g., "Total Dissolved Solids", "Barium", "Strontium")
4. View applicable treatment processes with removal efficiency data
5. Each entry includes: reference citation, percent removal or log removal, water quality conditions, operational parameters

### Search by Treatment Process

1. Navigate to https://tdb.epa.gov/
2. Click "Find Treatment Process"
3. Select the process (e.g., "Reverse Osmosis", "Ion Exchange", "Electrodialysis")
4. View all contaminants treated by that process with effectiveness data

---

## Key Treatment Processes for Produced Water / Brine

The following treatment processes are most relevant to produced water
treatment and lithium/magnesium recovery:

### Membrane Processes

| Process | Mechanism | TDS Range | Key Application |
|---------|-----------|-----------|-----------------|
| Reverse Osmosis (RO) | Pressure-driven membrane rejection | Feed up to ~70,000 mg/L TDS | Desalination, TDS reduction, pre-concentration |
| Nanofiltration (NF) | Selective membrane rejection | Feed up to ~40,000 mg/L TDS | Divalent ion removal (Mg, Ca, Ba, Sr) |
| Electrodialysis (ED) | Electrically driven ion transport | Feed up to ~100,000+ mg/L TDS | Selective ion removal, brine concentration |
| Electrodialysis Reversal (EDR) | ED with polarity reversal | Feed up to ~15,000 mg/L TDS | Scale-resistant ED variant |
| Membrane Distillation (MD) | Thermally driven vapor transport | Any TDS (vapor phase) | Zero-liquid discharge, high-TDS brines |

### Sorption / Ion Exchange

| Process | Mechanism | Key Application |
|---------|-----------|-----------------|
| Ion Exchange (IX) | Selective ion exchange resin | Targeted ion removal (Li, Ba, Ra) |
| Activated Alumina | Adsorption on alumina surface | Fluoride, arsenic removal |
| Granular Activated Carbon (GAC) | Adsorption on carbon | Organics, BTEX, some metals |

### Chemical / Physical

| Process | Mechanism | Key Application |
|---------|-----------|-----------------|
| Chemical Precipitation | Insoluble salt formation | Ba, Sr, Ra removal; lime softening for Ca, Mg |
| Coagulation/Flocculation | Charge neutralization + aggregation | Suspended solids, oil and grease |
| Electrocoagulation | Electrically generated coagulant | Oil removal from produced water |
| Oxidation (chemical) | Redox reactions | Iron, manganese, H2S removal |
| Air Stripping | Mass transfer to gas phase | VOCs, BTEX, dissolved gases |

### Thermal

| Process | Mechanism | Key Application |
|---------|-----------|-----------------|
| Evaporation / Crystallization | Thermal concentration to solid | ZLD, very high TDS brines |
| Multi-Effect Distillation (MED) | Multi-stage thermal distillation | Desalination of high-TDS streams |
| Mechanical Vapor Recompression (MVR) | Energy-efficient evaporation | Mid-to-high TDS concentration |

---

## Reference Removal Efficiency Data

These values are representative ranges compiled from EPA TDB, peer-reviewed
literature, and produced water treatment references. Actual performance depends
on feed water chemistry, temperature, and operating conditions.

### Removal Efficiency by Process (Produced Water Context)

| Contaminant | RO | NF | ED/EDR | IX | Chem. Precip. | GAC |
|------------|-----|-----|--------|-----|---------------|------|
| TDS | 95-99% | 50-90% | 50-95% | Variable | 20-60% | Minimal |
| Chloride | 95-99% | 20-50% | 50-95% | Variable | Minimal | Minimal |
| Calcium | 95-99% | 80-95% | 50-90% | 90-99% | 80-95% | Minimal |
| Magnesium | 95-99% | 85-97% | 50-90% | 90-99% | 80-95% | Minimal |
| Barium | 95-99% | 85-97% | 50-90% | 90-99% | 95-99% | Minimal |
| Strontium | 95-99% | 80-95% | 50-90% | 90-99% | 80-95% | Minimal |
| Iron | 95-99% | 80-95% | 40-80% | 80-99% | 95-99% | 30-70% |
| Lithium (as Li+) | 90-95% | 10-30% | 30-70% | 50-99%* | Minimal | Minimal |
| Oil and Grease | 95-99%** | 90-99%** | Low | Minimal | 60-90% | 80-95% |
| BTEX | 95-99% | 50-80% | Low | Minimal | Minimal | 90-99% |

*Li removal by IX depends entirely on sorbent selectivity. Li-selective
sorbents (LMO, LTO) achieve 90-99% Li extraction from brine; conventional
cation exchange is less selective.

**Membranes require pre-treatment to remove oil/grease to prevent fouling.

### Selective Lithium Recovery Technologies

These are not in the EPA TDB but are the primary DLE treatment approaches:

| Technology | Selectivity | Li Recovery | Feed TDS | Status |
|-----------|-------------|-------------|----------|--------|
| LMO sorbent (H2MnO3) | Li vs. Na, Ca, Mg | 85-95% | Up to 200,000+ mg/L | Pilot/commercial |
| LTO sorbent (H2TiO3) | Li vs. Na, Ca, Mg | 80-90% | Up to 200,000+ mg/L | Pilot |
| Solvent extraction (TBP/DEHPA) | Li vs. other cations | 80-95% | Up to 300,000+ mg/L | Commercial (Salar) |
| Electrochemical (LiFePO4) | Li vs. Na | 70-90% | Up to 100,000 mg/L | Lab/pilot |
| Alumina-based sorbent | Li vs. Mg | 70-85% | Up to 100,000 mg/L | Lab/pilot |

---

## Workflow

### Step 1 -- Resolve Intent

| User asks about... | Strategy |
|---------------------|----------|
| Treatment for a contaminant | Search TDB by contaminant name |
| Process comparison | Compare multiple processes for the target contaminant |
| Produced water treatment train | Recommend multi-step process based on feed chemistry |
| Removal efficiency data | Look up TDB + supplement with literature values |
| DLE technology performance | Use reference data table above (not in TDB) |
| Regulatory BAT | Cross-reference TDB with 40 CFR 435 (O&G effluent guidelines) |

### Step 2 -- Access EPA TDB

Since there is no REST API, access the web interface:

```bash
# Direct the user to the TDB search
echo "Navigate to https://tdb.epa.gov/ and search for your contaminant."
echo "Example: Search 'barium' to see treatment process effectiveness."
```

For programmatic use, provide the reference data tables above as inline data.

### Step 3 -- Supplement with EPA Envirofacts (if needed)

For regulatory data on treatment facilities:

```bash
# EPA SDWIS -- treatment techniques at public water systems
curl -s "https://enviro.epa.gov/enviro/efservice/TREATMENT/STATE_CODE/WV/rows/0:10/JSON"
```

### Step 4 -- Produce Output

**Format: Treatment Technology Comparison Table + Narrative**

---

## Output Format

```
## Treatment Technology Comparison: Produced Water from Marcellus Shale

**Feed characteristics (typical):**
- TDS: 100,000-250,000 mg/L
- Li: 50-200 mg/L
- Mg: 500-3,000 mg/L
- Ba: 500-15,000 mg/L
- Oil and Grease: 50-500 mg/L

**Recommended treatment train:**

| Step | Process | Target | Expected Removal |
|------|---------|--------|------------------|
| 1 | Oil/water separation + electrocoag | O&G, TSS | 95-99% O&G |
| 2 | Chemical precipitation (BaSO4) | Ba, Sr, Ra | 95-99% Ba |
| 3 | Li-selective IX (LMO sorbent) | Li recovery | 85-95% Li |
| 4 | NF or softening | Mg, Ca recovery | 85-97% Mg |
| 5 | Evaporation / crystallization | Brine concentration | ZLD |

**Summary:** Marcellus produced water requires a multi-step treatment train
due to extreme TDS (often exceeding 200,000 mg/L) and high barium. Oil
removal must precede any membrane step. Selective lithium recovery via DLE
sorbents should occur before bulk desalination to avoid diluting the Li
stream. Magnesium co-recovery via nanofiltration or selective precipitation
adds economic value.

**Data sources:** EPA Treatability Database (tdb.epa.gov), published DLE
pilot data, SPE produced water treatment literature.
```

---

## Error Handling

| Issue | Cause | Action |
|-------|-------|--------|
| TDB website unavailable | EPA site maintenance | Use reference data tables in this skill as fallback |
| Contaminant not found in TDB | TDB covers 120+ contaminants but not all | Search by chemical name, CAS number, or related compound |
| No data for specific treatment + contaminant pair | Not all combinations are in TDB | Note gap; supplement with peer-reviewed literature |
| DLE technologies not in TDB | TDB focuses on drinking water, not DLE | Use the DLE reference table above; cite primary literature |
| EPA Envirofacts API error | See `pnge-federal-data:epa-regulatory` skill for detailed troubleshooting | Check endpoint and parameters |

---

## Caveats

1. **No REST API.** The EPA TDB is a web-only application. Programmatic bulk
   data extraction is not supported. The reference tables in this skill
   provide commonly needed values for offline use.

2. **Drinking water focus.** The TDB was designed for drinking water treatment,
   not produced water or industrial brine. Feed water TDS in TDB studies is
   typically under 5,000 mg/L. Produced water TDS can exceed 300,000 mg/L.
   Removal efficiency at high TDS may differ significantly.

3. **DLE is not covered.** Direct lithium extraction technologies (LMO/LTO
   sorbents, electrochemical methods) are not in the EPA TDB because they
   are mineral recovery processes, not water treatment. The DLE reference
   data in this skill comes from published research and pilot studies.

4. **Performance depends on feed chemistry.** Removal efficiency values are
   ranges from multiple studies. Actual performance depends on feed water
   composition, temperature, pH, competing ions, membrane type, resin
   selection, and operating conditions.

5. **Not a design tool.** The TDB provides screening-level data for technology
   selection. Equipment sizing, cost estimation, and process design require
   detailed engineering analysis with site-specific feed water data.

6. **Regulatory context.** EPA 40 CFR 435 sets effluent limitations for the
   oil and gas extraction industry. Onshore unconventional wells generally
   have zero discharge requirements. The TDB supports technology selection
   but does not replace regulatory compliance analysis.

7. **PFAS coverage.** The TDB includes 26 PFAS chemicals as of the latest
   update. PFAS treatment data is actively expanding but may lag behind
   current research for newer PFAS compounds.

---

## Implementation Notes

- Since there is no API, use the inline reference tables for programmatic responses
- Direct users to https://tdb.epa.gov/ for detailed TDB lookups
- For treatment facility data, use the `pnge-federal-data:epa-regulatory` skill (Envirofacts + ECHO + GHGRP)
- Combine with `pnge-core:usgs-produced-waters` for feed water characterization
- For DLE technology details, cross-reference with `pnge-patents:patentsview` and `pnge-core:pnge-literature`
- Key literature: "Produced Water Treatment" (SPE Monograph), Fakhru'l-Razi et al. (2009) review
