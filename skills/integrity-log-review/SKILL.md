---
name: integrity-log-review
description: >
  Review local well-integrity reports, MIT test sheets, cement evaluation
  reports, noise logs, temperature logs, corrosion inspection summaries, and
  annulus pressure records to identify barrier issues and likely leak paths.
  Use when the user provides integrity documents and asks what failed, whether
  a barrier looks credible, how to interpret a pressure test or log response,
  or which follow-up diagnostic is most justified. Trigger phrases include MIT
  review, CBL/VDL report, noise log, temperature log, corrosion log, annulus
  pressure chart, leak-path review, integrity report, or barrier log review.
---

# Integrity Log Review

Document-review skill for the evidence layer beneath `pnge:well-integrity-barriers`.
It is designed for reports and test sheets that an engineer already has locally,
not for public data sources.

**Important:** Do not collapse multiple report types into one conclusion too
early. A failed pressure test, weak CBL response, and temperature anomaly each
support different hypotheses and have different uncertainty.

---

## Preferred Inputs

- MIT pressure test sheet with acceptance criterion
- Annulus pressure history or bleedoff / rebuild plots
- Cement evaluation logs: CBL/VDL, ultrasonic, bond summary
- Noise or temperature log report around suspected leak interval
- Corrosion / caliper inspection notes and workover history
- Current well schematic with depth references

---

## Workflow

1. Normalize all depths and pressures to a common reference.
2. Separate evidence by report type.
3. Ask what each report can rule out, not just what it suggests.
4. Build a leak-path evidence matrix.
5. Recommend the next diagnostic only where the evidence is still ambiguous.

---

## Module 1 - Pressure Test Review

```python
def pressure_change_rate(p_start, p_end, hours):
    if hours <= 0:
        return None
    return (p_end - p_start) / hours

def percent_pressure_loss(p_start, p_end):
    if p_start == 0:
        return None
    return 100.0 * (p_start - p_end) / p_start
```

For each pressure test, document:

- test volume and fluid type
- hold period
- acceptance threshold
- temperature correction applied or not
- whether the reported pass/fail criterion was objective or narrative only

---

## Module 2 - Evidence Matrix

```python
def evidence_vote(*flags):
    """
    Count positive indicators across report types.
    """
    return sum(1 for f in flags if bool(f))
```

Use a matrix like this:

| Evidence source | Supports tubing leak | Supports packer leak | Supports behind-pipe leak |
|----------------|----------------------|----------------------|---------------------------|
| MIT result | yes/no | yes/no | weak |
| Noise log | yes/no | yes/no | yes/no |
| Temperature anomaly | yes/no | yes/no | yes/no |
| Annulus rebuild | yes/no | yes/no | yes/no |
| CBL / ultrasonic | weak | weak | yes/no |

One positive indicator is usually not enough for a confident call.

---

## Module 3 - Report-Type Guidance

| Report type | Best use |
|------------|----------|
| MIT sheet | Confirm containment over the tested volume and duration |
| CBL/VDL | Screen for cement quality and zonal isolation concerns |
| Ultrasonic imaging | Better pipe and cement interface detail |
| Noise log | Locate active fluid movement |
| Temperature log | Identify active flow or injection anomalies |
| Corrosion inspection | Support failure-mechanism diagnosis |

---

## Module 4 - Common Review Findings

| Finding | Typical interpretation |
|--------|------------------------|
| Pressure test failed but no depth-localizing evidence | Containment issue exists, source still unresolved |
| Annulus rebuilds quickly after bleedoff | Active communication likely |
| CBL suggests poor bond but no active pressure behavior | Potential barrier weakness, not necessarily active leak |
| Noise and temperature coincide at same depth | Strong leak-path candidate |
| Corrosion or pitting aligns with pressure behavior | Failure mechanism more credible |

---

## Output Format

When using this skill, structure the answer as:

1. Documents reviewed and reference depth basis
2. What each document actually proves
3. Leak-path evidence matrix
4. Most likely interpretation with uncertainty
5. Best next log, test, or workover discriminator

---

## Integration Points

- Use `pnge:well-integrity-barriers` for the barrier and pressure framework.
- Use `api-well-standards` for casing and cement design context.
- Use `pnge:materials-fracture-mechanics` when crack growth or fatigue is implicated.
