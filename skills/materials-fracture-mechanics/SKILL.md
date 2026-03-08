---
name: materials-fracture-mechanics
description: >
  Analyze materials behavior and fracture mechanics problems including elastic
  and plastic response, stress and strain, fracture toughness, stress
  intensity, critical crack size, fatigue crack growth, Goodman screening,
  and brittle versus ductile failure concepts. Use when the user asks about
  fracture toughness, stress intensity factor, crack growth, fatigue life,
  Paris law, material failure, ductile or brittle transition, or how a crack
  in tubing, casing, or structural steel might behave. Trigger phrases include
  fracture mechanics, toughness, crack size, KIC, fatigue, Paris law, Goodman,
  brittle fracture, ductile failure, or materials failure.
---

# Materials And Fracture Mechanics

Tutor and diagnostics skill for how materials fail under load. It complements
the repo's strength-of-materials skills by focusing on defects, crack growth,
and fatigue rather than just nominal stress.

**Important:** Use this skill to screen failure plausibility and teach the
concepts. Real integrity decisions still require metallurgy, NDE, and service
history.

---

## Module 1 - Stress, Strain, And Elastic Screening

```python
def engineering_stress(force_lbf, area_in2):
    """Nominal stress in psi."""
    if area_in2 <= 0:
        return None
    return force_lbf / area_in2

def engineering_strain(delta_length_in, original_length_in):
    """Engineering strain."""
    if original_length_in <= 0:
        return None
    return delta_length_in / original_length_in

def hooke_law_stress(E_psi, strain):
    """Elastic stress from Hooke's law."""
    return E_psi * strain
```

---

## Module 2 - Stress Intensity And Critical Crack Size

```python
def stress_intensity_ksi_sqrtin(stress_ksi, crack_length_in, geometry_factor=1.12):
    """
    Mode-I stress intensity factor:
    K_I = Y * sigma * sqrt(pi * a)
    """
    import math
    if crack_length_in <= 0:
        return None
    return geometry_factor * stress_ksi * math.sqrt(math.pi * crack_length_in)

def critical_crack_size_in(KIC_ksi_sqrtin, stress_ksi, geometry_factor=1.12):
    """
    Solve for crack size at fast fracture: K_I = K_IC
    """
    import math
    if stress_ksi <= 0 or geometry_factor <= 0:
        return None
    return (KIC_ksi_sqrtin / (geometry_factor * stress_ksi))**2 / math.pi

def critical_stress_ksi(KIC_ksi_sqrtin, crack_length_in, geometry_factor=1.12):
    """
    Critical far-field stress for a given crack size.
    """
    import math
    if crack_length_in <= 0 or geometry_factor <= 0:
        return None
    return KIC_ksi_sqrtin / (geometry_factor * math.sqrt(math.pi * crack_length_in))
```

---

## Module 3 - Fatigue Screening

```python
def goodman_utilization(mean_stress_ksi, alternating_stress_ksi,
                        ultimate_strength_ksi, endurance_limit_ksi):
    """
    Goodman relation utilization.
    Values > 1 indicate fatigue failure risk.
    """
    if ultimate_strength_ksi <= 0 or endurance_limit_ksi <= 0:
        return None
    return (mean_stress_ksi / ultimate_strength_ksi +
            alternating_stress_ksi / endurance_limit_ksi)

def paris_cycles(ai_in, af_in, delta_sigma_ksi, C, m, geometry_factor=1.12,
                 steps=1000):
    """
    Numerically integrate Paris law:
    da/dN = C * (Delta K)^m
    """
    import math
    if ai_in <= 0 or af_in <= ai_in or steps <= 0:
        return None
    da = (af_in - ai_in) / steps
    cycles = 0.0
    a = ai_in
    for _ in range(steps):
        delta_k = geometry_factor * delta_sigma_ksi * math.sqrt(math.pi * a)
        dadn = C * delta_k**m
        if dadn <= 0:
            return None
        cycles += da / dadn
        a += da
    return cycles
```

Use Paris law only in the stable crack-growth regime. It does not cover crack
initiation or final unstable fracture.

---

## Module 4 - Failure Logic

| Observation | Likely concern |
|------------|----------------|
| High nominal stress but no flaw evidence | Strength / yielding problem |
| Modest stress with known defect | Fracture toughness problem |
| Repeated cyclic loading | Fatigue crack growth problem |
| Low temperature or sour service | Reduced toughness / embrittlement concern |
| Corrosion pits at stress concentrators | Pit-to-crack transition risk |

---

## Output Format

When using this skill, structure the answer as:

1. Loading mode and material basis
2. Whether the problem is strength-, toughness-, or fatigue-controlled
3. Equation setup and units
4. Crack or life estimate
5. What material data are still missing

---

## Learning Resources

| Resource | Notes |
|---------|-------|
| Callister and Rethwisch | Broad materials foundation |
| Anderson, *Fracture Mechanics* | Standard fracture mechanics text |
| Dowling, *Mechanical Behavior of Materials* | Strong fatigue coverage |
