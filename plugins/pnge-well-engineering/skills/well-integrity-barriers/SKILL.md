---
name: well-integrity-barriers
description: >
  Diagnose and manage well integrity and barrier problems including sustained
  casing pressure, annular pressure buildup, tubing or casing leak triage,
  mechanical integrity test interpretation, barrier envelope review, cement
  isolation concerns, and failure-mode screening for production and injection
  wells. Use when the user asks about SCP, annulus pressure, MIT results,
  barrier diagrams, tubing leaks, casing leaks, communication behind pipe,
  pressure bleedoff or buildup, corrosion-related failures, or how to assess
  whether a well still has two independent barriers. Trigger phrases include
  sustained casing pressure, annular pressure, integrity test, tubing leak,
  casing leak, barrier envelope, MIT, bleeddown, communication behind pipe,
  barrier failure, or well integrity.
---

# Well Integrity And Barrier Diagnostics

Integrity skill for production, injection, and workover decision support. Use it
to frame the problem, screen likely leak paths, and identify which logs or
pressure tests are worth running next.

**Important:** Barrier questions are high-consequence. Do not overstate certainty
from a single bleeddown test. Always distinguish between screening diagnosis and
formal well-integrity signoff.

---

## Data To Request First

- Current well schematic: casing, tubing, packer, perforations, and barrier status
- Pressure history for each annulus and tubing
- Bleedoff volume, pressure rebuild, and test timing
- Cement tops, squeeze history, and cement evaluation logs if available
- MIT or pressure test results, leakoff details, and acceptance criteria used
- Corrosion history, caliper data, retrieved tubular inspection, and workover history

---

## Workflow

1. Identify the barrier envelope that should exist.
2. Classify the pressure behavior: thermal, trapped pressure, SCP, or active communication.
3. Estimate gas volume or leak severity from bleeddown and rebuild behavior.
4. Screen the most likely leak path.
5. Recommend the next discriminating diagnostic, not every possible test.

---

## Module 1 - Annulus Gas Inventory And Bleeddown

```python
def annulus_gas_inventory_scf(pressure_psia, annulus_volume_bbl,
                              temperature_f=100.0, z=1.0):
    """
    Approximate free-gas inventory in standard cubic feet.
    Uses PV/ZT scaling from actual annulus conditions to standard conditions.
    """
    if pressure_psia <= 0 or annulus_volume_bbl <= 0 or z <= 0:
        return None
    v_ft3 = annulus_volume_bbl * 5.615
    t_r = temperature_f + 459.67
    scf = pressure_psia * v_ft3 * 520.0 / (14.7 * z * t_r)
    return scf

def bleeddown_volume_scf(p_initial_psia, p_final_psia, annulus_volume_bbl,
                         temperature_f=100.0, z=1.0):
    """Gas volume released between two annulus pressures."""
    q1 = annulus_gas_inventory_scf(p_initial_psia, annulus_volume_bbl, temperature_f, z)
    q2 = annulus_gas_inventory_scf(p_final_psia, annulus_volume_bbl, temperature_f, z)
    if q1 is None or q2 is None:
        return None
    return max(0.0, q1 - q2)

def pressure_rebuild_rate(p_start_psia, p_end_psia, days):
    """Average annulus pressure rebuild rate."""
    if days <= 0:
        return None
    return (p_end_psia - p_start_psia) / days
```

**Interpretation**

| Pressure behavior | Likely meaning |
|------------------|----------------|
| Pressure bleeds to zero and stays there | Trapped pressure, low active communication |
| Pressure bleeds to zero and rebuilds repeatedly | SCP or leak path communication |
| Pressure tracks temperature / production cycles | Thermal annulus behavior likely |
| Large bleedoff gas volume from small annulus | Real gas source, not just thermal expansion |

---

## Module 2 - Pressure Limits And Barrier Envelope

```python
def maasp_from_shoe(shoe_tvd_ft, fracture_gradient_psi_ft, annulus_fluid_ppg):
    """
    Screening maximum allowable annulus surface pressure from the shoe.
    MAASP = (FG - fluid gradient) * TVD
    fluid gradient = 0.052 * MW(ppg)
    """
    fluid_grad = 0.052 * annulus_fluid_ppg
    return (fracture_gradient_psi_ft - fluid_grad) * shoe_tvd_ft

def safety_factor_to_limit(current_pressure_psi, allowable_pressure_psi):
    """Fraction of pressure limit currently consumed."""
    if allowable_pressure_psi <= 0:
        return None
    return current_pressure_psi / allowable_pressure_psi
```

Barrier review should answer:

- What are the intended primary and secondary barriers right now?
- Which annulus is supposed to be isolated?
- What is the governing pressure limit: packer, casing, connection, or shoe?
- Is the observed pressure inside or outside the design envelope?

---

## Module 3 - Leak Path Screening

| Symptom | Likely leak path | Best next discriminator |
|--------|------------------|-------------------------|
| SCP on A-annulus with stable tubing | Tubing leak or packer leak | Tubing pressure test, noise / temperature log |
| Multi-annulus pressure communication | Behind-pipe or connection issue | Cement evaluation, pressure communication matrix |
| Pressure tied to production shut-ins | Tubing-to-annulus communication | Shut-in sequence and gradient comparison |
| Pressure tied to injection cycles | Injection string or packer leak | Injection falloff and annulus monitoring |
| Iron, scale, or solids in annulus bleedoff | Corrosion breach or produced-fluid communication | Sample the bleedoff, inspect metallurgy |

---

## Module 4 - MIT Interpretation

Use MIT results to answer three separate questions:

1. Did the pressure test hold according to the stated acceptance criterion?
2. Does the pressure-hold behavior fit the expected compressibility of the test volume?
3. If the test failed, does the failure implicate the string, packer, or behind-pipe isolation?

**Do not** treat "failed MIT" as a full diagnosis. It only narrows the suspect set.

---

## Module 5 - Escalation Logic

Escalate the integrity concern when any of these are true:

- Annulus pressure rebuilds rapidly after full bleeddown
- Current pressure approaches the controlling MAASP or tubular rating
- Two independent barriers cannot be clearly identified
- Sampled annulus fluid shows hydrocarbons, produced water, or corrosion solids unexpectedly
- Pressure communication spans multiple annuli or changes with nearby operations

---

## Output Format

When using this skill, structure the answer as:

1. Intended barrier envelope
2. Pressure behavior classification
3. Most likely leak path or failure mode
4. Pressure limit comparison
5. Highest-value next diagnostic or workover action

---

## Integration Points

- Use `api-well-standards` for casing, tubing, and cement design context.
- Use `pnge-well-engineering:tubing-design` for tubing movement, seal assembly, and packer force effects.
- Use `pnge-well-engineering:flow-assurance` and `pnge-well-engineering:production-chemistry` when corrosion or deposits are implicated.
- Use `pnge-engineering-science:materials-fracture-mechanics` when crack growth or fatigue is part of the failure hypothesis.
