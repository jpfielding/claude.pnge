# PNGE Mechanics — Equation Reference

Complete equation library for the pnge-mechanics skill. Organized by module.
All equations are given in both field units and SI where relevant.

---

## Module 1 — Statics and Force Equilibrium

### Equilibrium Conditions

For a rigid body in static equilibrium, the necessary and sufficient conditions are:

```
Sum of all forces = 0:
  ΣFx = 0
  ΣFy = 0
  ΣFz = 0  (3D problems)

Sum of all moments about any point = 0:
  ΣMx = 0
  ΣMy = 0
  ΣMz = 0  (3D problems)
```

For 2D coplanar problems: ΣFx = 0, ΣFy = 0, and ΣM_A = 0 (any point A).

### Moment of a Force

Moment of force F about point A:
```
M_A = F * d
```
Where d = perpendicular distance from A to the line of action of F.

For force components:
```
M_A = Fx * dy - Fy * dx
```
Where dx, dy are the x and y coordinates of the point of application relative to A.
Sign convention: counterclockwise positive (standard).

### Method of Joints (Trusses)

At each joint, apply two equilibrium equations (2D):
```
ΣFx = 0  (sum of x-components of all forces at joint, including member forces)
ΣFy = 0
```

Member force convention:
- Positive result = tension (member pulls the joint)
- Negative result = compression (member pushes the joint)

### Method of Sections (Trusses)

Pass a cut through at most 3 members. For the isolated portion:
```
ΣFx = 0
ΣFy = 0
ΣM_point = 0   (choose moment center to eliminate 2 unknowns)
```

### Hook Load and Crown Block Forces

Total hook load (HL) includes:
```
HL = W_string_air * BF + W_BHA + W_traveling_block + F_packer
```

Where BF = buoyancy factor (see Module 6).

Force in the deadline (fast line) for n-line string:
```
F_deadline = HL / n + (hook_load_increase per line * mechanical_efficiency)
```

Simplified (frictionless sheaves):
```
F_fast_line = HL / n
```

---

## Module 2 — Axial Stress, Strain, and Deformation

### Normal Stress

```
sigma = P / A    (field units: psi, where P in lb and A in in^2)
                 (SI: Pa = N/m^2)
```

Where:
- sigma = normal stress (psi or Pa)
- P = axial force (lb or N)
- A = cross-sectional area (in^2 or m^2)

Sign convention: positive = tension, negative = compression.

### Normal Strain

```
epsilon = delta / L   (dimensionless)
epsilon = sigma / E   (for linear elastic material)
```

Where:
- delta = elongation (in or m)
- L = original length (in or m)
- E = Young's modulus (psi or Pa)

### Axial Deformation

For a uniform bar under axial load P:
```
delta = P * L / (A * E)    (in, given P in lb, L in in, A in in^2, E in psi)
```

For a bar with varying cross-section or load:
```
delta = integral[P(x) / (A(x) * E) dx]  from 0 to L
```

For a hanging cable/string under its own weight (weight per unit length = w lb/in):
```
delta = w * L^2 / (2 * A * E)
```
This is because the load varies linearly from P=w*L at the top to P=0 at the free end.

### Thermal Deformation

```
delta_T = alpha * delta_T_temperature * L
```

Where:
- alpha = coefficient of thermal expansion (/°F or /°C)
- delta_T_temperature = temperature change (°F or °C)
- L = length (same units as delta_T)

### Combined Loading (Mechanical + Thermal)

For a free body (no constraints):
```
delta_total = P*L/(A*E) + alpha * delta_T * L
```

For a constrained body (no net displacement allowed):
```
0 = P*L/(A*E) + alpha * delta_T * L
=> P = -A * E * alpha * delta_T    (induced thermal force)
=> sigma = -E * alpha * delta_T    (induced thermal stress)
```
Negative sign: heating a constrained bar induces compression.

### Statically Indeterminate Axial Problems

Example: bar fixed at both ends, load P applied at an intermediate point.

Step 1: Equilibrium: R_A + R_B = P
Step 2: Compatibility: delta_AC + delta_CB = 0 (total elongation is zero)
```
R_A * L_AC / (A * E) = R_B * L_CB / (A * E)
=> R_A / R_B = L_CB / L_AC
```
Step 3: Solve for R_A and R_B simultaneously.

### Typical Material Properties (Engineering)

| Material | E (ksi) | E (GPa) | G (ksi) | nu | alpha (/°F) | Yield (ksi) |
|----------|---------|---------|---------|-----|-------------|-------------|
| Steel (structural) | 29,000 | 200 | 11,200 | 0.29 | 6.5e-6 | 36-50 |
| Steel (API N-80) | 30,000 | 207 | 11,600 | 0.29 | 6.5e-6 | 80 |
| Steel (API P-110) | 30,000 | 207 | 11,600 | 0.29 | 6.5e-6 | 110 |
| Steel (API Q-125) | 30,000 | 207 | 11,600 | 0.29 | 6.5e-6 | 125 |
| Aluminum (6061-T6) | 10,000 | 69 | 3,800 | 0.33 | 13.1e-6 | 40 |
| Cast iron | 15,000 | 103 | 6,000 | 0.26 | 6.0e-6 | — (brittle) |

### Cross-Sectional Areas — Common Pipe Sizes

For hollow circular section:
```
A = pi * (OD^2 - ID^2) / 4    (in^2, OD and ID in inches)
  = pi * t * (OD - t)         (approximate for thin-walled: t << OD)
```

Where t = wall thickness = (OD - ID) / 2.

---

## Module 3 — Beam Bending

### Euler-Bernoulli Beam Theory Assumptions

1. Plane cross-sections remain plane after bending
2. Material is linearly elastic and isotropic
3. Small deflections (deflection << beam length)
4. Shear deformation is negligible (slender beams, L >> depth)

### Shear Force and Bending Moment Sign Convention

Standard convention (most textbooks):
- Positive shear: forces tend to rotate the element clockwise
- Positive moment: sagging (tension on bottom fiber), concave upward

Distributed load w (lb/ft or lb/in, positive upward):
```
dV/dx = -w(x)     (distributed load decrements shear)
dM/dx = V(x)      (shear is the derivative of moment)
```

Concentrated load P (downward = negative w):
- Shear jumps by -P at the point of application (downward load)
- Reaction R: shear jumps by +R

### Flexure Formula

At any cross-section with bending moment M:
```
sigma(y) = M * y / I    (normal stress at fiber y from neutral axis)
sigma_max = M * c / I   (maximum, at outermost fiber y = c)
```

Where:
- M = bending moment (lb-in or N-m)
- I = second moment of area (in^4 or m^4) about the neutral axis
- c = distance from neutral axis to outermost fiber (in or m)
- sigma = bending stress, positive = tension on the tension side

**Section modulus:**
```
S = I / c    (in^3 or m^3)
sigma_max = M / S
```

### Second Moment of Area (I) — Common Cross-Sections

**Solid circular (diameter d):**
```
I = pi * d^4 / 64
```

**Hollow circular (pipe, OD = d_o, ID = d_i):**
```
I = pi * (d_o^4 - d_i^4) / 64
```

**Rectangular (width b, height h, bending about horizontal axis):**
```
I = b * h^3 / 12
```

**Polar moment of inertia (for torsion):**
```
J = pi * d^4 / 32                    (solid)
J = pi * (d_o^4 - d_i^4) / 32        (hollow)
J = 2 * I                            (circular sections)
```

### Standard Beam Deflection Formulas

**Simply supported, center point load P:**
```
M_max = P * L / 4  (at midspan)
delta_max = P * L^3 / (48 * E * I)  (at midspan, downward)
```

**Simply supported, uniform distributed load w (lb/in):**
```
M_max = w * L^2 / 8  (at midspan)
delta_max = 5 * w * L^4 / (384 * E * I)  (at midspan)
```

**Cantilever, end point load P:**
```
M_max = P * L  (at fixed end)
delta_max = P * L^3 / (3 * E * I)  (at free end)
```

**Cantilever, uniform distributed load w (lb/in):**
```
M_max = w * L^2 / 2  (at fixed end)
delta_max = w * L^4 / (8 * E * I)  (at free end)
```

**Simply supported, off-center point load P at distance a from left support (b = L-a):**
```
M_max = P * a * b / L  (at point of load application)
delta_at_load = P * a^2 * b^2 / (3 * E * I * L)
delta_max = P * b * (L^2 - b^2)^(3/2) / (9 * sqrt(3) * E * I * L)  if a > b
```

### Transverse Shear Stress (V-Q/Ib Formula)

Average shear stress at a cross-sectional cut:
```
tau = V * Q / (I * b)
```

Where:
- V = shear force at section (lb)
- Q = first moment of area above (or below) the cut about the neutral axis (in^3)
- I = second moment of area of entire cross-section (in^4)
- b = width of the cross-section at the cut (in)

For a hollow circular pipe, maximum shear stress occurs at the neutral axis:
```
Q = (d_o^3 - d_i^3) / 12    (for hollow circle)
tau_max = 2*V / (pi * (d_o^2 - d_i^2) / 4)  (simplified, thin wall)
```

---

## Module 4 — Thick-Walled Cylinder (Lame Equations)

### Derivation Basis

The Lame equations are the exact analytical solution for a long thick-walled
cylinder under internal pressure p_i at r = r_i and external pressure p_e at r = r_e.
Assumptions: linear elastic, isotropic, plane strain or generalized plane stress.

### Lame Constants

```
A = (p_i * r_i^2 - p_e * r_e^2) / (r_e^2 - r_i^2)
B = (p_i - p_e) * r_i^2 * r_e^2 / (r_e^2 - r_i^2)
```

### Stress Distribution

At any radius r_i <= r <= r_e:
```
sigma_r(r) = A - B / r^2      (radial stress)
sigma_theta(r) = A + B / r^2  (hoop stress, circumferential)
sigma_z = A  (for closed-end cylinder, axial stress, constant through wall)
        = 0  (for open-ended or free axial condition)
```

Boundary conditions check:
```
sigma_r(r_i) = A - B/r_i^2 = -p_i  (compressive at inner wall under internal pressure)
sigma_r(r_e) = A - B/r_e^2 = -p_e  (compressive at outer wall under external pressure)
```

Note: in the sign convention where tensile = positive, sigma_r = -p at the wall.

### Special Case: Internal Pressure Only (p_e = 0)

```
A = p_i * r_i^2 / (r_e^2 - r_i^2)
B = p_i * r_i^2 * r_e^2 / (r_e^2 - r_i^2)

sigma_r = (p_i * r_i^2 / (r_e^2 - r_i^2)) * (1 - r_e^2/r^2)
sigma_theta = (p_i * r_i^2 / (r_e^2 - r_i^2)) * (1 + r_e^2/r^2)
```

Maximum hoop stress is at r = r_i:
```
sigma_theta_max = p_i * (r_i^2 + r_e^2) / (r_e^2 - r_i^2)
```

For a thin-walled cylinder (t = r_e - r_i << r_i):
```
sigma_theta_max ≈ p_i * r_i / t    (thin-wall approximation)
```

### Special Case: External Pressure Only (p_i = 0)

Maximum hoop stress is now compressive, at r = r_i:
```
sigma_theta_collapse = -2 * p_e * r_e^2 / (r_e^2 - r_i^2)
```

This governs casing collapse design.

### Von Mises Yield Criterion

For a general triaxial stress state (sigma_1, sigma_2, sigma_3):
```
sigma_vm = (1/sqrt(2)) * sqrt((sigma_1 - sigma_2)^2 + (sigma_2 - sigma_3)^2 + (sigma_1 - sigma_3)^2)
```

For biaxial (sigma_r, sigma_theta, sigma_z = 0 or = A):
```
sigma_vm = sqrt(sigma_r^2 + sigma_theta^2 - sigma_r * sigma_theta)  (sigma_z = 0)
```

Yield when: sigma_vm >= sigma_yield.

### API Burst Rating (Barlow Formula Approximation)

API uses a modified Barlow formula with a 12.5% wall thickness tolerance reduction:
```
p_burst = 0.875 * 2 * sigma_yield * t / OD
```

Where t = nominal wall thickness, OD = outer diameter.
This is a simplified formula; actual API ratings per API 5C3.

### API Collapse Rating

Collapse rating depends on the D/t ratio (diameter/thickness):
- D/t < 15: plastic collapse
- D/t 15-24: transition collapse
- D/t 24-32: elastic-plastic collapse
- D/t > 32: elastic collapse (Lame governs)

For elastic collapse:
```
p_collapse = 2*E*(1 - (r_i/r_e)^2) / ((1-nu^2) * ((r_e/r_i)^2 - 1)^2 * (r_e/r_i))
           ≈ 2*E / (1 - nu^2) * (t/OD)^3  (thin-wall limit)
```

---

## Module 5 — Stress Transformation and Mohr's Circle

### 2D Stress Transformation Equations

For a stress state (sigma_x, sigma_y, tau_xy) in the x-y coordinate frame,
the stresses on a plane inclined at angle theta (from x-axis to the normal of the plane):

```
sigma_n(theta) = (sigma_x + sigma_y)/2 + (sigma_x - sigma_y)/2 * cos(2*theta) + tau_xy * sin(2*theta)
tau(theta) = -(sigma_x - sigma_y)/2 * sin(2*theta) + tau_xy * cos(2*theta)
```

### Principal Stresses

The principal stresses (maximum and minimum normal stress, with zero shear) are:
```
sigma_1 = (sigma_x + sigma_y)/2 + sqrt[((sigma_x - sigma_y)/2)^2 + tau_xy^2]
sigma_2 = (sigma_x + sigma_y)/2 - sqrt[((sigma_x - sigma_y)/2)^2 + tau_xy^2]
```

Orientation of principal planes (angle theta_p from x-axis):
```
tan(2*theta_p) = 2*tau_xy / (sigma_x - sigma_y)
```

### Maximum Shear Stress

```
tau_max = sqrt[((sigma_x - sigma_y)/2)^2 + tau_xy^2]
        = (sigma_1 - sigma_2) / 2
```

The maximum shear stress planes are at 45 degrees to the principal planes.

### Mohr's Circle Construction Steps

Given stress state (sigma_x, sigma_y, tau_xy):

1. Plot point A = (sigma_x, -tau_xy)  [note sign: tau on the x-face plots negative]
2. Plot point B = (sigma_y, +tau_xy)  [tau on the y-face plots positive]
3. Center C = ((sigma_x + sigma_y)/2, 0)  [midpoint of AB on sigma-axis]
4. Radius R = sqrt[((sigma_x - sigma_y)/2)^2 + tau_xy^2]  = tau_max
5. Principal stresses: sigma_1 = C + R, sigma_2 = C - R
6. Angle 2*theta_p on circle = angle from CA to C-sigma1 axis (positive counterclockwise)

To find stress on a plane at angle theta from the x-axis:
- Rotate 2*theta counterclockwise from point A on the circle
- Read off (sigma_n, -tau) at the new point

### Torsion of Circular Shafts

Shear stress at radius r in a shaft under torque T:
```
tau(r) = T * r / J
```

Maximum shear stress at outer surface:
```
tau_max = T * c / J = T * d_o / (2 * J)
```

Where c = outer radius, J = polar moment of inertia.

Angle of twist over length L:
```
phi = T * L / (G * J)    (radians)
```

Where G = shear modulus:
```
G = E / (2 * (1 + nu))
```

For steel: G ≈ 11.5 x 10^6 psi (11.5 Mpsi) = 79.3 GPa.

Torsional stiffness:
```
k_T = T / phi = G * J / L    (lb-in/rad)
```

### Maximum Shear Stress Failure Criterion (Tresca)

Material yields when the maximum shear stress reaches the shear yield strength:
```
tau_max >= tau_yield = sigma_yield / 2
```

### Von Mises Failure Criterion (Distortion Energy)

More accurate than Tresca for ductile materials:
```
sigma_vm = sqrt(sigma_1^2 - sigma_1*sigma_2 + sigma_2^2) >= sigma_yield   [2D]
```

Tresca is more conservative (fails 13% earlier than Von Mises for pure shear).
API tubular design often uses Von Mises.

---

## Module 6 — Fluid Statics and Wellbore Pressure

### Hydrostatic Pressure

Pressure at depth h in a static fluid of density rho:
```
P = P_0 + rho * g * h    (SI: Pa, rho in kg/m^3, h in m)
P = P_0 + gamma * h      (where gamma = specific weight = rho*g)
```

In field units:
```
P (psi) = P_surface (psi) + gradient (psi/ft) * depth (ft)
gradient (psi/ft) = mud_weight (ppg) * 0.052
gradient (psi/ft) = density (g/cc) * 0.4335
```

Conversion factors:
- 1 ppg = 0.052 psi/ft
- 1 g/cc = 0.4335 psi/ft
- 1 g/cc = 8.33 ppg
- Freshwater: 8.33 ppg = 0.433 psi/ft
- Saltwater (typical): 8.6-8.9 ppg = 0.447-0.463 psi/ft

### Buoyancy Force (Archimedes Principle)

Buoyant force on a submerged object:
```
F_buoy = rho_fluid * g * V_displaced    (SI: N)
F_buoy = gamma_fluid * V_displaced      (SI: N, gamma = specific weight)
```

For a casing string in fluid:
```
W_buoyant = W_air - F_buoy = W_air * (1 - rho_fluid / rho_steel)
```

Buoyancy factor (BF):
```
BF = 1 - rho_fluid / rho_steel
   = 1 - mud_weight_ppg / 65.4    (steel density = 65.4 ppg)
```

For 10.0 ppg mud in steel casing:
```
BF = 1 - 10.0/65.4 = 0.847
```

### Multi-Fluid Wellbore Pressure

For a wellbore with different fluids in successive depth intervals:
```
P(z) = P_surface + SUM[gradient_i * (z_i_bottom - z_i_top)]    for each fluid i
```

### Equivalent Circulating Density (ECD)

During drilling circulation, annular pressure losses add to the hydrostatic:
```
ECD (ppg) = mud_weight (ppg) + annular_pressure_loss (psi) / (0.052 * TVD_ft)
```

The annular pressure loss (simplified Bingham plastic model):
```
dP/dL = (2 * mu_p * v_a / (d_a^2)) + (tau_y / (d_a / 1000))   (field units, approximate)
```

Where mu_p = plastic viscosity (cp), v_a = annular velocity (ft/min),
d_a = hydraulic diameter of annulus (in), tau_y = yield point (lb/100ft^2).

---

## Unit Conversion Quick Reference

### Stress and Pressure

| From | To | Multiply by |
|------|----|-------------|
| psi | MPa | 0.006895 |
| MPa | psi | 145.04 |
| psi | kPa | 6.895 |
| psi/ft | MPa/m | 0.02262 |
| psi/ft | kPa/m | 22.62 |
| ppg | psi/ft | * 0.052 |
| ppg | kPa/m | * 1.175 |
| g/cc | psi/ft | * 0.4335 |
| atm | psi | 14.696 |
| bar | psi | 14.504 |

### Force

| From | To | Multiply by |
|------|----|-------------|
| lb | N | 4.4482 |
| kip | kN | 4.4482 |
| lb | kgf | 0.4536 |
| ton (short) | lb | 2,000 |
| ton (metric) | lb | 2,205 |

### Length

| From | To | Multiply by |
|------|----|-------------|
| ft | m | 0.3048 |
| in | mm | 25.4 |
| in | cm | 2.54 |

### Density

| From | To | Multiply by |
|------|----|-------------|
| g/cc | kg/m^3 | 1,000 |
| ppg | kg/m^3 | 119.83 |
| lb/ft^3 | kg/m^3 | 16.018 |
| g/cc | ppg | 8.345 |

### Temperature

```
°F = °C * 9/5 + 32
°C = (°F - 32) * 5/9
R = °F + 459.67    (Rankine)
K = °C + 273.15    (Kelvin)
```
