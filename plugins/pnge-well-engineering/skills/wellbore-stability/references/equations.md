# Wellbore Stability — Equation Reference

Complete equation library for the wellbore-stability skill. Includes the full
Kirsch derivation, Mohr-Coulomb and Mogi-Coulomb failure criteria, stress
transformation equations, and Appalachian basin reference data.

---

## 1. Effective Stress Principle

### Terzaghi Effective Stress

For a porous medium (rock with fluid-filled pores):
```
sigma'_ij = sigma_ij - alpha * P_p * delta_ij
```

Where:
- sigma'_ij = effective stress tensor component
- sigma_ij = total stress tensor component
- alpha = Biot coefficient (0 < alpha <= 1)
- P_p = pore pressure
- delta_ij = Kronecker delta (1 if i=j, 0 otherwise)

For Terzaghi's original formulation: alpha = 1.

For most engineering purposes in petroleum geomechanics:
```
sigma' = sigma - P_p   (simplified, alpha = 1)
```

The Biot coefficient depends on rock compressibility:
```
alpha = 1 - K_dry / K_solid
```

Where K_dry = drained bulk modulus, K_solid = mineral grain bulk modulus.

**Typical Biot coefficients:**
- Unconsolidated sand: alpha ≈ 1.0
- Sandstone: alpha ≈ 0.6-0.9
- Shale (Marcellus): alpha ≈ 0.7-0.9
- Tight carbonates: alpha ≈ 0.4-0.7

---

## 2. In-Situ Stress State

### Three Principal Stresses

In a sedimentary basin, the three principal stresses are often aligned with:
- S_v: vertical (overburden) stress — acts vertically
- S_Hmax: maximum horizontal stress — largest horizontal stress
- S_hmin: minimum horizontal stress — smallest horizontal stress

The vertical stress is a principal stress because shear traction on horizontal
planes is zero (symmetry assumption). This is not always true near faults
or in areas of high structural complexity.

### Stress Regime Classification (Anderson, 1951)

| Regime | S1 | S2 | S3 | Fault Type |
|--------|----|----|----|----|
| Normal faulting | S_v | S_Hmax | S_hmin | Normal (extensional) |
| Strike-slip | S_Hmax | S_v | S_hmin | Strike-slip (wrench) |
| Reverse faulting | S_Hmax | S_hmin | S_v | Thrust (compressional) |

The Appalachian basin at Marcellus depth is predominantly strike-slip (S_Hmax > S_v > S_hmin).

### Overburden Stress

```
S_v = integral[rho(z) * g * dz]  from surface to depth z
```

Field units:
```
S_v (psi) = integral[RHOB (g/cc) * 0.4335 * dz (ft)]
```

Where 0.4335 = 0.4335 psi per (g/cc * ft).

### Poroelastic Horizontal Stress Model

Assuming a tectonically passive basin (no tectonic strain) with lateral confinement:
```
S_hmin = [nu/(1-nu)] * (S_v - alpha*P_p) + alpha*P_p
S_Hmax = S_hmin   (isotropic horizontal — only if no tectonic contribution)
```

With tectonic strain terms epsilon_H and epsilon_h (horizontal strains):
```
S_hmin = [nu/(1-nu)] * (S_v - alpha*P_p) + alpha*P_p + E/(1-nu^2) * (epsilon_h + nu*epsilon_H)
S_Hmax = [nu/(1-nu)] * (S_v - alpha*P_p) + alpha*P_p + E/(1-nu^2) * (epsilon_H + nu*epsilon_h)
```

Appalachian tectonic correction: the basin has compressional tectonic stress
from the ancestral Appalachian orogeny and ongoing plate motion. This elevates
both S_Hmax and S_hmin above the poroelastic baseline, with S_Hmax elevated
more (hence strike-slip regime).

---

## 3. Kirsch Equations — Full Derivation

### Problem Setup

A circular borehole of radius r_w is drilled in an infinite elastic medium
subject to far-field stresses S_H (maximum horizontal) and S_h (minimum
horizontal) — here we use S_H and S_h for compactness. The borehole is filled
with fluid at pressure P_w (mud pressure).

Coordinate system: r = radial distance from borehole axis, theta = azimuth
from the S_H direction.

### Kirsch (1898) Solution for Stress Concentration

For a circular hole in a biaxial stress field, the exact elastic solution
(Lame-Kirsch) for stresses at radius r:

**Total radial stress:**
```
sigma_r = (S_H + S_h)/2 * (1 - r_w^2/r^2)
        + (S_H - S_h)/2 * (1 - 4*r_w^2/r^2 + 3*r_w^4/r^4) * cos(2*theta)
        + P_w * r_w^2/r^2
```

**Total hoop (tangential) stress:**
```
sigma_theta = (S_H + S_h)/2 * (1 + r_w^2/r^2)
            - (S_H - S_h)/2 * (1 + 3*r_w^4/r^4) * cos(2*theta)
            - P_w * r_w^2/r^2
```

**Total shear stress:**
```
tau_r_theta = -(S_H - S_h)/2 * (1 + 2*r_w^2/r^2 - 3*r_w^4/r^4) * sin(2*theta)
```

### At the Borehole Wall (r = r_w)

Setting r = r_w, the solution simplifies to:

**Radial stress:**
```
sigma_r = P_w    (boundary condition: borehole wall supports pressure P_w)
```

**Hoop stress:**
```
sigma_theta = (S_H + S_h) - 2*(S_H - S_h)*cos(2*theta) - P_w
```

**Shear stress:**
```
tau_r_theta = 0    (principal stress at borehole wall)
```

### Critical Azimuths

At **theta = 0 degrees** (S_H direction — minimum compressive hoop stress):
```
sigma_theta_min = (S_H + S_h) - 2*(S_H - S_h)*cos(0) - P_w
                = (S_H + S_h) - 2*(S_H - S_h) - P_w
                = 3*S_h - S_H - P_w
```

This is the location of **minimum compressive hoop stress** — tensile fractures
initiate here when sigma_theta_min becomes tensile.

At **theta = 90 degrees** (S_h direction — maximum compressive hoop stress):
```
sigma_theta_max = (S_H + S_h) - 2*(S_H - S_h)*cos(180) - P_w
                = (S_H + S_h) + 2*(S_H - S_h) - P_w
                = 3*S_H - S_h - P_w
```

This is the location of **maximum compressive hoop stress** — borehole breakout
(shear failure) initiates here.

### Effective Stresses at the Borehole Wall

For a permeable formation (pore pressure acts on effective stress):
```
sigma_theta_eff = sigma_theta - alpha * P_p
sigma_r_eff = P_w - alpha * P_p
```

At the breakout azimuth (theta = 90 degrees):
```
sigma_theta_eff(90) = 3*S_H - S_h - P_w - alpha*P_p
sigma_r_eff(90) = P_w - alpha*P_p
```

At the tensile fracture azimuth (theta = 0 degrees):
```
sigma_theta_eff(0) = 3*S_h - S_H - P_w - alpha*P_p
sigma_r_eff(0) = P_w - alpha*P_p
```

### Axial Stress (Vertical Stress at Borehole Wall)

For a vertical borehole, the axial stress sigma_z at the borehole wall is:
```
sigma_z = S_v - 2*nu*(S_H - S_h)*cos(2*theta) - alpha*P_p
```

At theta = 0 and theta = 90:
```
sigma_z(0)  = S_v - 2*nu*(S_H - S_h) - alpha*P_p
sigma_z(90) = S_v + 2*nu*(S_H - S_h) - alpha*P_p
```

The axial stress modifies the three-dimensional effective stress state used
in the Von Mises or Mogi-Coulomb criterion.

---

## 4. Failure Criteria

### Mohr-Coulomb Failure Criterion

The most commonly used criterion in wellbore stability analysis:

```
tau_f = C_0 + sigma_n * tan(phi)
```

Or equivalently, in terms of principal stresses:
```
sigma_1 = UCS + q * sigma_3
```

Where:
- tau_f = shear stress at failure (psi or MPa)
- C_0 = cohesion (psi or MPa)
- sigma_n = normal stress on failure plane (psi or MPa)
- phi = internal friction angle (degrees)
- q = (1 + sin(phi)) / (1 - sin(phi)) = Mohr-Coulomb slope parameter
- UCS = unconfined compressive strength = 2*C_0*cos(phi)/(1-sin(phi))
- sigma_1, sigma_3 = maximum and minimum principal effective stresses

**Converting between C_0, phi, UCS, and q:**
```
UCS = 2*C_0*cos(phi) / (1 - sin(phi))
C_0 = UCS * (1 - sin(phi)) / (2*cos(phi))
q = (1 + sin(phi)) / (1 - sin(phi))
phi = arcsin((q-1)/(q+1))
```

**At the borehole wall (sigma_3 = sigma_r_eff = P_w - alpha*P_p):**

Breakout initiates when sigma_theta_eff >= UCS + (q-1)*sigma_r_eff

For impermeable borehole wall (sigma_r_eff = 0 free surface, or when alpha*P_p = P_w):
```
Breakout: sigma_theta_eff >= UCS
=> 3*S_H - S_h - P_w - alpha*P_p >= UCS
=> P_w <= 3*S_H - S_h - alpha*P_p - UCS   (breakout occurs if Pmud too low)
```

Minimum mud weight to prevent breakout:
```
P_w_min = 3*S_H - S_h - alpha*P_p - UCS
```

### Tensile Failure Criterion

Tensile fracture initiates when the minimum effective principal stress reaches
the negative tensile strength:
```
sigma_theta_eff(0) <= -T_0
3*S_h - S_H - P_w - alpha*P_p <= -T_0
P_w >= 3*S_h - S_H - alpha*P_p + T_0
```

Maximum mud weight to prevent tensile fracture:
```
P_w_max = 3*S_h - S_H - alpha*P_p + T_0
```

Conservative (no tensile strength credit):
```
P_w_max_conservative = 3*S_h - S_H - alpha*P_p
```

And the hard physical upper limit (fracture reopening):
```
P_w_limit = S_hmin    (minimum principal stress = fracture extension pressure)
```

### Mogi-Coulomb Failure Criterion

Mogi (1971) showed that intermediate principal stress sigma_2 affects failure.
The Mogi-Coulomb criterion (Al-Ajmi and Zimmerman, 2005):

```
tau_oct = a + b * sigma_m2
```

Where:
- tau_oct = octahedral shear stress = (1/3) * sqrt[(sigma_1-sigma_2)^2 + (sigma_2-sigma_3)^2 + (sigma_1-sigma_3)^2]
- sigma_m2 = (sigma_1 + sigma_3) / 2   (mean of maximum and minimum)
- a = 2*sqrt(2)/3 * C_0
- b = 2*sqrt(2)/3 * sin(phi)

**Mogi-Coulomb vs Mohr-Coulomb:** The Mogi-Coulomb criterion predicts higher
strength when sigma_2 > sigma_3, which occurs at the borehole wall where
sigma_theta is often much larger than sigma_r. This means Mogi-Coulomb gives
a less conservative (lower) minimum mud weight estimate. The Mohr-Coulomb
criterion (conservative) is more commonly used for design.

### Von Mises Failure Criterion (for ductile rock)

Less common for brittle rock but applicable for soft formations:
```
sigma_vm = (1/sqrt(2)) * sqrt((sigma_1-sigma_2)^2 + (sigma_2-sigma_3)^2 + (sigma_1-sigma_3)^2) >= UCS
```

---

## 5. Breakout Width Equations

### Angular Extent of Breakout

Breakout occurs at all angles theta where sigma_theta_eff exceeds the rock
strength. The boundary angles theta_BO satisfy:

```
sigma_theta_eff(theta_BO) = UCS   (Mohr-Coulomb with sigma_r = 0)
(S_H + S_h) - 2*(S_H - S_h)*cos(2*theta_BO) - P_w - alpha*P_p = UCS
cos(2*theta_BO) = [(S_H + S_h) - P_w - alpha*P_p - UCS] / [2*(S_H - S_h)]
```

Let RHS = X:
- If X > 1: no breakout at any angle (rock is stronger than stress concentration)
- If X < -1: entire borehole wall has failed (complete instability)
- Otherwise: theta_BO = arccos(X) / 2

The breakout zone extends from (90 - theta_BO) to (90 + theta_BO) degrees
measured from the S_H direction (i.e., the breakout is centered on the S_h
azimuth). The total breakout width (WBO) is:

```
WBO = 2 * (90 - theta_BO)   [degrees]
```

### Breakout Depth (Radial Extent)

The failed zone extends radially outward to r_BO where stresses return below UCS.
For simple Mohr-Coulomb with no far-field perturbation (approximate):

```
r_BO / r_w = [2*(S_H + S_h) / UCS]^(1/2)   (approximate)
```

This is only valid for the specific case of hydrostatic far-field stress and
zero mud pressure. For the general case, solve numerically.

---

## 6. UCS from Log Correlations

### McNally (1987) — Shales and Mudstones

```
UCS (MPa) = 1200 * exp(-0.036 * DTC (us/ft))
```

| DTC (us/ft) | UCS (MPa) | UCS (psi) |
|-------------|-----------|-----------|
| 50 | 168 | 24,400 |
| 55 | 141 | 20,400 |
| 60 | 118 | 17,100 |
| 65 | 99 | 14,400 |
| 70 | 83 | 12,000 |
| 75 | 70 | 10,100 |
| 80 | 58 | 8,400 |
| 90 | 41 | 5,900 |

Marcellus DTC typical range: 55-75 us/ft → UCS = 10,000-20,000 psi.

### Militzer and Stoll (1973) — Sandstones

```
UCS (MPa) = (7682 / DTC (us/ft))^1.82
```

### Chang et al. (2006) — General Correlation Set

For shales:
```
UCS (MPa) = 0.77 * (304.8 / DTC (us/m))^2.93
```

Note: DTC in us/m = DTC in us/ft * 3.2808.

### Tensile Strength Estimate

Rock tensile strength T_0 is approximately:
```
T_0 ≈ UCS / 10   (empirical rule of thumb for sedimentary rock)
T_0 range: 100-2,000 psi for typical formations
```

For Marcellus (UCS ~ 10,000 psi): T_0 ≈ 1,000 psi.

---

## 7. Eaton Pore Pressure Methods

### Resistivity Method (Eaton, 1975)

```
P_p = S_v - (S_v - P_p_normal) * (Ro/Rn)^1.2
```

Variable definitions:
- P_p = predicted pore pressure at depth z (psi)
- S_v = overburden stress at depth z (psi)
- P_p_normal = normal hydrostatic pore pressure at depth z (psi)
- Ro = observed (log) resistivity at depth z (ohm-m)
- Rn = "normal" (trend) resistivity at depth z from the regional resistivity baseline (ohm-m)
- 1.2 = Eaton's empirically derived exponent (range 0.6-2.0 depending on basin)

The normal resistivity trend Rn is constructed by fitting a line through
shallower data where pore pressure is known to be hydrostatic, then extrapolating.
In normally compacted shales, resistivity increases with depth.

### Sonic Method (Eaton, 1975)

```
P_p = S_v - (S_v - P_p_normal) * (DTCn/DTC)^3.0
```

Variable definitions:
- DTC = observed interval transit time at depth z (us/ft or us/m)
- DTCn = normal (trend) interval transit time at depth z (us/ft or us/m)
- 3.0 = Eaton's exponent for sonic (range 1.0-5.0 depending on calibration)

Normal compaction trend for shales: DTC decreases with depth as porosity
decreases under overburden load. Overpressured zones show higher DTC than
expected (abnormally slow) because pore pressure supports the grain framework.

---

## 8. Appalachian Basin Reference Stress Table

### Marcellus/Devonian Section — West Virginia

Representative stress gradient values based on published literature and
publicly available formation pressure/ISIP data from Appalachian operators.
These values are for 6,000-9,000 ft TVD in West Virginia.

| Parameter | Low | Median | High | Unit | Notes |
|-----------|-----|--------|------|------|-------|
| S_v gradient | 1.00 | 1.02 | 1.05 | psi/ft | From density logs |
| P_p gradient (Marcellus) | 0.45 | 0.465 | 0.48 | psi/ft | Near-normal pressure WV |
| S_hmin gradient | 0.63 | 0.70 | 0.77 | psi/ft | From ISIP, best data |
| S_Hmax gradient | 0.78 | 0.87 | 0.98 | psi/ft | From image logs, LOT |
| S_Hmax orientation | N55E | N70E | N85E | — | ENE-WSW (horizontal compression) |
| UCS (Marcellus) | 8,000 | 10,000 | 18,000 | psi | From core and sonic |
| phi (friction angle) | 25 | 30 | 35 | degrees | From triaxial tests |
| nu (Poisson's ratio) | 0.20 | 0.25 | 0.28 | — | From acoustic logs |
| E (Young's modulus) | 20 | 30 | 45 | GPa | From acoustic logs/core |
| Biot alpha | 0.65 | 0.80 | 0.90 | — | Estimated from K_dry/K_grain |

### Stress Orientation

The maximum horizontal stress in the Appalachian basin is oriented
approximately ENE-WSW (N60-80E), consistent with the North American plate
stress field driven by Mid-Atlantic ridge push and residual effects of the
Appalachian orogeny.

This orientation means:
- Hydraulic fractures propagate ENE-WSW (perpendicular to S_hmin, which is NNW-SSE)
- Horizontal wells drilled NNW-SSE (perpendicular to SHmax) are well-oriented
  for fracture stimulation in the Marcellus

### Fracture Gradient Practical Estimates

For preliminary well planning (before offset data available):

| Depth Range | S_hmin Gradient | S_Hmax Gradient | P_p Gradient |
|-------------|----------------|----------------|--------------|
| 4,000-6,000 ft | 0.62-0.70 psi/ft | 0.75-0.88 psi/ft | 0.43-0.47 psi/ft |
| 6,000-8,000 ft | 0.65-0.75 psi/ft | 0.80-0.95 psi/ft | 0.46-0.47 psi/ft |
| 8,000-10,000 ft | 0.68-0.78 psi/ft | 0.83-0.98 psi/ft | 0.46-0.48 psi/ft |

---

## 9. Frictional Equilibrium (Zoback Stress Polygon)

### Byerlee's Law

For most rocks, the coefficient of sliding friction mu_s obeys Byerlee's law:
```
mu_s ≈ 0.6-0.85   (for most rocks, independent of rock type for sigma_n < 200 MPa)
```

### Stress Polygon (Zoback et al., 2003)

The stress polygon bounds S_Hmax as a function of S_hmin, S_v, and P_p by
requiring that no fault with any orientation is critically stressed (about to slip):

For **normal faulting** (S_v = S1, S_hmin = S3):
```
(S_v - alpha*P_p) / (S_hmin - alpha*P_p) <= [(mu_s^2 + 1)^0.5 + mu_s]^2
```

For **strike-slip faulting** (S_Hmax = S1, S_hmin = S3):
```
(S_Hmax - alpha*P_p) / (S_hmin - alpha*P_p) <= [(mu_s^2 + 1)^0.5 + mu_s]^2
```

For **reverse faulting** (S_Hmax = S1, S_v = S3):
```
(S_Hmax - alpha*P_p) / (S_v - alpha*P_p) <= [(mu_s^2 + 1)^0.5 + mu_s]^2
```

For mu_s = 0.65:
```
[(0.65^2 + 1)^0.5 + 0.65]^2 = [1.193 + 0.65]^2 = 1.843^2 = 3.40
```

So the maximum ratio of maximum to minimum effective principal stress
consistent with Byerlee's law is approximately 3.4 (for mu = 0.65).

---

## 10. Full 3D Stress Transformation for Deviated Wells

### General Problem

For a wellbore inclined at azimuth alpha_w (from North) and inclination i_w
(from vertical), the far-field principal stresses (S_v, S_Hmax, S_hmin) must
be rotated into the wellbore coordinate system.

**Step 1:** Rotate principal stress tensor into geographic (x=E, y=N, z=up) frame.

**Step 2:** Rotate geographic frame into wellbore frame using two rotations:
- R1: rotation by azimuth alpha_w about z-axis
- R2: rotation by inclination i_w about new y-axis

```
sigma_borehole = R * sigma_geo * R^T
```

Where R = R2 * R1.

**Step 3:** Extract the normal and shear stresses acting on the borehole
wall at any azimuth around the wellbore circumference.

**Step 4:** Apply failure criterion as before using the transformed stresses.

For a vertical well (i_w = 0): sigma_borehole = sigma_geo and the Kirsch
equations in Module 4 of the SKILL.md apply directly.

For a horizontal well parallel to S_Hmax (i_w = 90, alpha_w = S_Hmax direction):
The effective far-field "horizontal" stresses acting in the plane perpendicular
to the wellbore axis are S_v and S_hmin (S_Hmax now acts axially).

The borehole hoop stress at the azimuth of S_v direction (most compressive):
```
sigma_theta_max_hw = 3*S_v - S_hmin - P_w   (for horizontal well // S_Hmax)
```

This is typically much lower than in a vertical well where sigma_theta_max = 3*S_Hmax - S_hmin - P_w.
This explains why Marcellus horizontal wells drilled parallel to S_Hmax are
generally more stable than vertical wells at the same depth.

---

## Key References

- Kirsch, G. (1898): "Die Theorie der Elastizitat und die Bedurfnisse der
  Festigkeitslehre," Zeitschrift des Vereines Deutscher Ingenieure, 42, 797-807.
  [Original Kirsch stress concentration solution]

- Anderson, E.M. (1951): "The Dynamics of Faulting," Oliver and Boyd, Edinburgh.
  [Stress regime classification]

- Eaton, B.A. (1975): "The equation for geopressure prediction from well logs,"
  SPE 5544. [Eaton pore pressure methods]

- Zoback, M.D. (2007): "Reservoir Geomechanics," Cambridge University Press.
  [Comprehensive textbook; stress polygon; wellbore stability]

- Al-Ajmi, A.M. and Zimmerman, R.W. (2005): "Relation between the Mogi and
  Coulomb failure criteria," Int. J. Rock Mech. Min. Sci., 42, 431-439.
  [Mogi-Coulomb criterion]

- Lash, G.G. and Engelder, T. (2011): "Thickness trends and sequence stratigraphy
  of the Middle Devonian Marcellus Formation," AAPG Bulletin, 95, 61-103.
  [Appalachian stress orientation reference]

- McNally, G.H. (1987): "Estimation of coal measures rock strength using sonic
  and neutron logs," Geoexploration, 24, 381-395. [UCS-DTC correlation]
