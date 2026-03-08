---
name: pnge-mechanics
description: >
  Perform statics, mechanics of materials, and fluid statics calculations
  relevant to petroleum engineering. Covers force equilibrium, free body
  diagrams, truss analysis, beam bending and shear, axial stress and strain,
  torsion, pressure vessel theory, Mohr circle for stress transformation, fluid
  pressure at depth, buoyancy, and pipe loading analysis. Use this skill when
  the user needs to solve statics problems, calculate stress or strain in casing
  or tubing, analyze beam loading for derrick structures, compute wellbore
  pressure profiles, evaluate thick-walled cylinder stress for casing design, or
  work through mechanics problems for MAE 201, MAE 243, or PNGE courses. Trigger
  for phrases like "casing stress under axial load", "thick-walled cylinder
  pressure", "beam bending in derrick", "Mohr circle", "torsional shear stress",
  "buoyancy force on casing string", "free body diagram", "wellbore fluid
  pressure gradient", "yield criterion for tubulars", or any mechanics of
  materials or statics calculation. Produces step-by-step solutions with
  diagrams described in text.
---

# PNGE Mechanics Calculator

Engineering mechanics skill for petroleum engineering applications. Covers
statics (MAE 201), mechanics of materials (MAE 243), and fluid statics — with
worked examples for wellbore design, casing loading, derrick structures, and
tubular analysis.

**Important:** Results are based on classical analytical solutions and standard
engineering correlations. For final design decisions, verify against API
standards (API 5C3, API RP 7G) and perform full finite-element analysis where
required. Always apply appropriate safety factors.

---

## Module 1 — Statics and Force Equilibrium

### Capabilities

- Sum of forces and moments for 2D and 3D systems
- Free body diagram construction (described with ASCII art where useful)
- Support reactions for beams (pin, roller, fixed)
- Truss analysis: method of joints and method of sections
- PNGE applications: crown block loads, derrick leg loading, hook load, traveling block

### Equilibrium Equations

For a body in static equilibrium, all forces and moments sum to zero:

```
ΣFx = 0    ΣFy = 0    ΣFz = 0
ΣMx = 0    ΣMy = 0    ΣMz = 0
```

For 2D problems only ΣFx, ΣFy, and ΣM_point = 0 are needed.

### Beam Support Reactions

| Support Type | Reactions Provided |
|--------------|-------------------|
| Roller | 1 force (normal to surface) |
| Pin (hinge) | 2 forces (Rx, Ry) |
| Fixed (cantilever) | 2 forces + 1 moment (Rx, Ry, M) |

### Workflow — Support Reactions

1. Draw the free body diagram; replace each support with its reaction forces/moments
2. Label all known loads (magnitudes, directions, positions)
3. Write the three equilibrium equations
4. Solve the system of equations for unknowns
5. Verify: sum all forces and moments independently

### Derrick Hook Load Example

**Problem:** A crown block is mounted at the top of a derrick mast. The hoisting
cable makes a 5-degree angle from vertical due to offset. Hook load = 400,000 lb
(including traveling block weight).

**Free body diagram (ASCII):**
```
          [Crown block]
         /|
      T / | Vertical component
       /  |
      /5° |
     /    v
  [Cable] ----> Horizontal component
```

**Solution:**
```
T_vertical = 400,000 * cos(5°) = 400,000 * 0.9962 = 398,480 lb
T_horizontal = 400,000 * sin(5°) = 400,000 * 0.0872 = 34,880 lb
```

The crown block must resist both components. Horizontal component creates
a bending moment on the mast structure.

### Truss Analysis — Method of Joints

1. Find all external reactions using global equilibrium
2. Isolate each joint; draw FBD with all member forces as unknowns
3. At each joint: ΣFx = 0 and ΣFy = 0
4. Solve for two unknowns per joint; proceed joint by joint
5. Positive result = tension; negative = compression

### Truss Analysis — Method of Sections

Use when only a few member forces are needed:
1. Pass an imaginary cut through no more than 3 members
2. Isolate one side; draw FBD with cut member forces as unknowns
3. Apply three equilibrium equations to solve for the three unknowns
4. Choose moment centers to reduce simultaneous equations

### Example Python — Truss Joint

```python
import math

def solve_joint_2member(F_ext_x, F_ext_y, theta1_deg, theta2_deg):
    """
    Solve for forces in two members meeting at a joint.
    theta = angle from positive x-axis (degrees).
    Returns (F1, F2); positive = tension.
    """
    t1 = math.radians(theta1_deg)
    t2 = math.radians(theta2_deg)
    # [cos(t1) cos(t2)] [F1]   [-F_ext_x]
    # [sin(t1) sin(t2)] [F2] = [-F_ext_y]
    det = math.cos(t1)*math.sin(t2) - math.cos(t2)*math.sin(t1)
    if abs(det) < 1e-10:
        raise ValueError("Members are parallel — joint is unstable")
    F1 = (-F_ext_x * math.sin(t2) + F_ext_y * math.cos(t2)) / det
    F2 = ( F_ext_x * math.sin(t1) - F_ext_y * math.cos(t1)) / det
    return F1, F2

# Example: vertical load 50,000 lb downward at joint
# Member 1 at 135°, Member 2 at 45°
F1, F2 = solve_joint_2member(0, -50000, 135, 45)
print(f"F1 = {F1:,.0f} lb, F2 = {F2:,.0f} lb")
# Positive = tension, negative = compression
```

---

## Module 2 — Axial Stress, Strain, and Deformation

### Capabilities

- Normal stress and strain in rods, casing, tubing, and drill pipe
- Axial deformation under mechanical and thermal loads
- Statically indeterminate axial systems
- PNGE applications: casing string tension analysis, tubing elongation, packerless completions

### Core Equations

See `references/equations.md` for full derivations and variable definitions.

**Normal stress:**
```
sigma = P / A   (psi or MPa)
```

**Strain and deformation:**
```
epsilon = delta / L = sigma / E
delta = P * L / (A * E)
```

**Thermal expansion:**
```
delta_T = alpha * delta_T * L
```

For combined mechanical and thermal loading:
```
delta_total = P*L/(A*E) + alpha * delta_T * L
```

For statically indeterminate problems, compatibility (geometry of deformation)
adds the equation needed beyond equilibrium alone.

### Typical Material Properties

| Material | E (psi) | E (GPa) | alpha (/°F) | Yield (ksi) |
|----------|---------|---------|-------------|-------------|
| Steel (API N-80) | 30,000,000 | 207 | 6.5e-6 | 80 |
| Steel (API P-110) | 30,000,000 | 207 | 6.5e-6 | 110 |
| Steel (API Q-125) | 30,000,000 | 207 | 6.5e-6 | 125 |
| Aluminum drill pipe | 10,000,000 | 69 | 13.1e-6 | 60 |

### Workflow — Casing Axial Load Analysis

1. Identify all axial loads: buoyancy-corrected string weight, hook load, packer loads, pressure-induced forces
2. Calculate cross-sectional area A = pi*(OD^2 - ID^2)/4
3. Compute stress: sigma = P/A; compare to yield strength with safety factor
4. Compute elongation (or contraction) for each load case
5. Check against API rating and required safety factor (typically 1.6 for tension)

### Example — Casing String Elongation Under Tension

**Problem:** 7-inch OD, 26 lb/ft casing (ID = 6.276 in), 8,000 ft in air.
Calculate axial stress and elongation at surface due to string weight.

```python
import math

# Casing geometry
OD_in = 7.0        # inches
ID_in = 6.276      # inches
L_ft = 8000.0      # feet
weight_lbft = 26.0 # lb/ft (in air)
E_psi = 30e6       # psi

# Area
A = math.pi / 4 * (OD_in**2 - ID_in**2)  # in^2
print(f"Cross-sectional area: {A:.3f} in^2")

# Total weight (load at top of string)
P_total = weight_lbft * L_ft  # lb
print(f"Total string weight: {P_total:,.0f} lb")

# Axial stress at top (maximum)
sigma = P_total / A  # psi
print(f"Axial stress at surface: {sigma:,.0f} psi = {sigma/1000:.1f} ksi")

# Elongation
L_in = L_ft * 12  # convert to inches
delta = P_total * L_in / (2 * A * E_psi)  # average load is half
# More precisely: integrate along length
# delta = integral(W(z)/A/E dz) from 0 to L
# where W(z) = weight_lbft * z * 12 (lb) at depth z
# delta = weight_lbft * 12 * L^2 / (2*A*E) — units: lb/in * in^2 / (in^2 * psi) = in
delta_in = weight_lbft * 12 * (L_ft**2) / (2 * A * E_psi)
print(f"Elongation: {delta_in:.2f} in = {delta_in/12:.3f} ft")

# Safety factor check vs N-80 yield
yield_psi = 80000  # psi
SF = yield_psi / sigma
print(f"Safety factor vs yield: {SF:.2f}x")
```

### Thermal Expansion of Tubing

**Problem:** 9,500 ft of 2-7/8 inch tubing (alpha = 6.5e-6 /°F). Temperature
increases from 70°F to 220°F after production begins.

```python
alpha = 6.5e-6   # /°F, steel
dT = 220 - 70    # 150°F temperature increase
L = 9500 * 12    # inches

delta_thermal = alpha * dT * L
print(f"Free thermal expansion: {delta_thermal:.2f} in = {delta_thermal/12:.2f} ft")
# If tubing is constrained by packer, this thermal expansion induces
# compressive stress: sigma = -E * alpha * dT
sigma_thermal = -30e6 * alpha * dT
print(f"Induced compressive stress (if constrained): {sigma_thermal:,.0f} psi")
```

---

## Module 3 — Beam Bending

### Capabilities

- Shear force and bending moment diagrams for standard loading cases
- Flexure formula for bending stress in pipe and hollow sections
- Second moment of area for circular and hollow circular sections
- Beam deflection formulas (cantilever, simply supported, overhanging)
- PNGE applications: drill collar bending analysis, derrick beam sizing, casing in curved wellbore

### Core Equations

**Flexure formula:**
```
sigma_max = M * c / I
```

**Second moment of area — hollow circular (pipe):**
```
I = pi * (d_o^4 - d_i^4) / 64
```

**Section modulus:**
```
S = I / c = I / (d_o/2)
```

### Standard Beam Formulas

| Loading | Max Moment | Max Deflection |
|---------|-----------|----------------|
| Simply supported, center point load P | M = P*L/4 (at center) | delta = P*L^3/(48*E*I) (at center) |
| Simply supported, UDL w (lb/in) | M = w*L^2/8 (at center) | delta = 5*w*L^4/(384*E*I) (at center) |
| Cantilever, end point load P | M = P*L (at wall) | delta = P*L^3/(3*E*I) (at free end) |
| Cantilever, UDL w (lb/in) | M = w*L^2/2 (at wall) | delta = w*L^4/(8*E*I) (at free end) |

### Workflow — Shear and Moment Diagrams

1. Find reactions at supports using equilibrium
2. Starting from the left: shear V(x) changes by +R at reactions (upward) and -P at point loads
3. Shear is constant between loads; moment M(x) = integral of V(x)
4. Bending moment is maximum where shear = 0 (changes sign)
5. Compute sigma_max from M_max, c, and I

### Example — Drill Collar Bending

**Problem:** A 6.75-inch OD, 2.25-inch ID drill collar (9.625 in OD housing
excluded) spans 30 ft between stabilizers in a horizontal section. Formation
side-load = 500 lb/ft distributed. Calculate maximum bending stress.

```python
import math

# Drill collar geometry
OD_in = 6.75    # inches
ID_in = 2.25    # inches
L_ft = 30.0     # feet between stabilizers
w_lbft = 500.0  # distributed side load, lb/ft

# Convert to inch units
L = L_ft * 12   # inches
w = w_lbft / 12 # lb/in

# Second moment of area
I = math.pi * (OD_in**4 - ID_in**4) / 64
print(f"I = {I:.2f} in^4")

# Outer fiber distance
c = OD_in / 2
print(f"c = {c:.3f} in")

# Simply-supported assumption (stabilizers act as pins)
M_max = w * L**2 / 8  # lb-in
print(f"M_max = {M_max:,.0f} lb-in = {M_max/12000:.1f} kip-ft")

# Maximum bending stress
sigma_b = M_max * c / I
print(f"Bending stress: {sigma_b:,.0f} psi = {sigma_b/1000:.1f} ksi")

# Deflection at center
E = 30e6  # psi, steel
delta_max = 5 * w * L**4 / (384 * E * I)
print(f"Max deflection: {delta_max:.3f} in")
```

---

## Module 4 — Thick-Walled Cylinder (Lame Equations)

### Capabilities

- Radial and hoop stress distribution through cylinder wall (Lame)
- Maximum stress at inner radius for internal pressure loading
- Maximum stress at outer radius for external pressure loading
- Von Mises yield criterion for biaxial stress state
- API casing burst and collapse pressure estimation
- PNGE applications: casing design, tubing burst/collapse, wellhead pressure ratings

### Lame Equations

For a thick-walled cylinder under internal pressure p_i and external pressure p_e:

**Constants A and B:**
```
A = (p_i * r_i^2 - p_e * r_e^2) / (r_e^2 - r_i^2)
B = (p_i - p_e) * r_i^2 * r_e^2 / (r_e^2 - r_i^2)
```

**Stress at any radius r:**
```
sigma_r = A - B/r^2      (radial stress, compressive at inner wall)
sigma_theta = A + B/r^2  (hoop/circumferential stress)
```

**At inner radius (critical for burst):**
```
sigma_theta_max = (p_i * (r_i^2 + r_e^2) - 2*p_e*r_e^2) / (r_e^2 - r_i^2)
```

**At outer radius (critical for collapse):**
```
sigma_theta_outer = (2*p_i*r_i^2 - p_e*(r_i^2 + r_e^2)) / (r_e^2 - r_i^2)
```

### Von Mises Yield Criterion (Plane Stress)

For biaxial stress state (sigma_r, sigma_theta) at any point:
```
sigma_vm = sqrt(sigma_r^2 - sigma_r*sigma_theta + sigma_theta^2) <= sigma_yield
```

With axial stress sigma_z included (triaxial):
```
sigma_vm = (1/sqrt(2)) * sqrt((s1-s2)^2 + (s2-s3)^2 + (s1-s3)^2)
```

### Workflow — Casing Burst Check

1. Identify: OD, ID (or wall thickness t), internal pressure p_i, external (mud or cement) pressure p_e
2. Compute r_i = ID/2, r_e = OD/2
3. Compute A and B
4. Find sigma_theta at r_i (maximum hoop stress, controlling for burst)
5. Compute Von Mises effective stress
6. Compare to yield strength with safety factor (API minimum = 1.0; design often 1.25)

### Example — API 7-inch Casing Burst Check

**Problem:** 7-inch OD, 23 lb/ft casing (ID = 6.366 inch, t = 0.317 inch),
N-80 steel (80,000 psi yield). Internal pressure = 5,000 psi, external
(mud) pressure = 3,000 psi at the point of interest.

```python
import math

# Casing geometry
OD_in = 7.000   # inches
ID_in = 6.366   # inches
r_i = ID_in / 2
r_e = OD_in / 2

# Pressures
p_i = 5000.0    # psi, internal
p_e = 3000.0    # psi, external (mud column)

# Lame constants
A = (p_i * r_i**2 - p_e * r_e**2) / (r_e**2 - r_i**2)
B = (p_i - p_e) * r_i**2 * r_e**2 / (r_e**2 - r_i**2)
print(f"Lame constants: A = {A:.1f} psi, B = {B:.1f} psi-in^2")

# Stresses at inner radius (burst-critical)
sigma_r_inner = A - B / r_i**2   # should equal -p_i (BC check)
sigma_t_inner = A + B / r_i**2   # max hoop stress
print(f"\nAt inner wall (r = {r_i:.3f} in):")
print(f"  sigma_r = {sigma_r_inner:.0f} psi (check: should be -{p_i})")
print(f"  sigma_theta = {sigma_t_inner:.0f} psi")

# Stresses at outer radius
sigma_r_outer = A - B / r_e**2   # should equal -p_e
sigma_t_outer = A + B / r_e**2
print(f"\nAt outer wall (r = {r_e:.3f} in):")
print(f"  sigma_r = {sigma_r_outer:.0f} psi (check: should be -{p_e})")
print(f"  sigma_theta = {sigma_t_outer:.0f} psi")

# Von Mises at inner wall (biaxial: assume sigma_z = axial/2 for capped ends)
# For open-ended or free tube, sigma_z ~ A (Lame axial)
sigma_z = A  # Lame plane strain approximation
sigma_vm = math.sqrt(
    sigma_t_inner**2 - sigma_t_inner * sigma_z + sigma_z**2
    - sigma_r_inner * (sigma_t_inner + sigma_z - sigma_r_inner)
)
# Simplified Von Mises for sigma_r, sigma_theta only:
sigma_vm_2d = math.sqrt(
    sigma_r_inner**2 - sigma_r_inner * sigma_t_inner + sigma_t_inner**2
)
print(f"\nVon Mises (biaxial): {sigma_vm_2d:.0f} psi")

yield_psi = 80000
SF = yield_psi / sigma_vm_2d
print(f"Safety factor vs N-80 yield: {SF:.2f}x")

# Net internal pressure approach (API simplified)
p_net = p_i - p_e
burst_approx = 0.875 * 2 * yield_psi * (r_e - r_i) / OD_in
print(f"\nAPI simplified burst rating: {burst_approx:.0f} psi")
print(f"Net pressure: {p_net} psi — {'PASS' if p_net < burst_approx else 'FAIL'}")
```

### API Casing Rating Quick Reference

| Grade | Min Yield (psi) | Use Case |
|-------|----------------|----------|
| J-55 | 55,000 | Surface casing, low pressure |
| K-55 | 55,000 | Similar to J-55, better weldability |
| N-80 | 80,000 | Intermediate casing, common |
| L-80 | 80,000 | Sour service (H2S) |
| P-110 | 110,000 | Production casing, high pressure |
| Q-125 | 125,000 | HPHT applications |

---

## Module 5 — Mohr's Circle and Stress Transformation

### Capabilities

- Transform stress components from one coordinate system to another
- Find principal stresses (maximum and minimum normal stress)
- Find maximum shear stress
- Mohr's circle construction and reading
- PNGE applications: in-situ stress analysis, failure analysis of tubulars, borehole wall stress state

### Stress Transformation Equations

For a 2D stress state (sigma_x, sigma_y, tau_xy), the stress on a plane
rotated by angle theta from the x-axis:

```
sigma_n = (sigma_x + sigma_y)/2 + (sigma_x - sigma_y)/2 * cos(2*theta) + tau_xy * sin(2*theta)
tau = -(sigma_x - sigma_y)/2 * sin(2*theta) + tau_xy * cos(2*theta)
```

### Principal Stresses

```
sigma_1,2 = (sigma_x + sigma_y)/2  ±  sqrt[((sigma_x - sigma_y)/2)^2 + tau_xy^2]
```

The angle to the principal plane:
```
tan(2*theta_p) = 2*tau_xy / (sigma_x - sigma_y)
```

### Maximum Shear Stress

```
tau_max = sqrt[((sigma_x - sigma_y)/2)^2 + tau_xy^2]
        = (sigma_1 - sigma_2) / 2
```

Occurs at 45° from the principal planes.

### Mohr's Circle Construction

1. Plot point X = (sigma_x, -tau_xy) and point Y = (sigma_y, +tau_xy)
2. The center C is at ((sigma_x + sigma_y)/2, 0)
3. The radius R = tau_max = sqrt[((sigma_x-sigma_y)/2)^2 + tau_xy^2]
4. Principal stresses: sigma_1 = C + R (rightmost), sigma_2 = C - R (leftmost)
5. The angle XC to the sigma axis = 2*theta_p (counterclockwise on Mohr's circle = counterclockwise on element)

### Example — In-Situ Stress Analysis

**Problem:** At a depth of 7,000 ft in the Marcellus, the in-situ stress state in
the horizontal plane is: S_Hmax = 6,500 psi, S_hmin = 4,800 psi. A borehole is
drilled at 30° to the S_Hmax direction. Find the normal and shear stress on the
borehole axis.

```python
import math

# In-situ stresses (horizontal plane, compressive positive convention)
S_Hmax = 6500  # psi
S_hmin = 4800  # psi
tau_xy = 0     # principal stresses, so no shear in original frame

theta_deg = 30   # borehole axis angle from S_Hmax
theta = math.radians(theta_deg)

# Stress transformation
sigma_n = (S_Hmax + S_hmin)/2 + (S_Hmax - S_hmin)/2 * math.cos(2*theta) + tau_xy * math.sin(2*theta)
tau_nt  = -(S_Hmax - S_hmin)/2 * math.sin(2*theta) + tau_xy * math.cos(2*theta)

print(f"Normal stress on plane perpendicular to borehole axis: {sigma_n:.0f} psi")
print(f"Shear stress on that plane: {tau_nt:.0f} psi")

# Principal stresses (these are already principal since tau_xy=0)
sigma_1 = S_Hmax
sigma_2 = S_hmin
tau_max = (sigma_1 - sigma_2) / 2

print(f"\nPrincipal stresses: sigma_1 = {sigma_1} psi, sigma_2 = {sigma_2} psi")
print(f"Maximum shear stress: {tau_max:.0f} psi")
print(f"Center of Mohr's circle: {(sigma_1+sigma_2)/2:.0f} psi")
print(f"Radius of Mohr's circle: {tau_max:.0f} psi")
```

### Torsional Shear Stress

For circular shaft or drill string under torque T:

```
tau = T * r / J
```

Where J = polar moment of inertia:
```
J = pi * (d_o^4 - d_i^4) / 32 = 2 * I
```

Maximum shear stress at outer radius r = d_o/2:
```
tau_max = T * (d_o/2) / J = 2*T / (pi * (d_o^4 - d_i^4) / 16)
```

Angle of twist:
```
phi = T * L / (G * J)
```

Where G = shear modulus = E / (2*(1+nu)) ≈ 11.5e6 psi for steel.

---

## Module 6 — Fluid Statics and Wellbore Pressure

### Capabilities

- Hydrostatic pressure at depth for single and multi-fluid columns
- Wellbore pressure profiles with changing mud weights
- Buoyancy force on casing string in fluid
- ECD (equivalent circulating density) estimates
- PNGE applications: mud weight selection, casing design pressure loads, kick detection

### Hydrostatic Pressure

**Single fluid:**
```
P = rho * g * h   (SI: Pa)
P = gradient * depth   (field: psi, where gradient in psi/ft)
```

**Pressure gradient conversion:**
```
gradient (psi/ft) = mud_weight (ppg) * 0.052
gradient (psi/ft) = density (g/cc) * 0.4335
```

**Multi-fluid column:**
```
P_bottom = P_surface + sum[gradient_i * depth_i]
```

### Buoyancy Force on Casing String

The buoyant weight of a casing string in fluid (Archimedes principle):
```
W_buoyant = W_air - W_fluid_displaced
W_buoyant = W_air * (1 - rho_fluid / rho_steel)
```

For a steel casing string (rho_steel = 65.4 lb/gal = 7,850 kg/m^3) in
10.5 ppg mud:
```
buoyancy_factor = 1 - 10.5/65.4 = 0.8394
```

### Workflow — Wellbore Pressure Profile

1. Identify all fluid columns in the annulus (water, mud, cement, spacer)
2. Starting from surface (known pressure or atmospheric), add gradient * depth for each section
3. At each casing shoe, record the pressure
4. Compare to formation pore pressure (must exceed) and fracture gradient (must be below)
5. Plot: depth vs pressure with pore pressure and fracture gradient lines

### Example — Wellbore Pressure Profile

**Problem:** 10,000 ft well. Mud weight = 9.8 ppg from surface to 10,000 ft.
Surface pressure = 0 psi. Calculate pressure profile and buoyancy factor.

```python
# Wellbore pressure profile
mw_ppg = 9.8          # mud weight, ppg
depth_ft = 10000      # total depth, ft
surf_P = 0            # surface pressure, psi

# Pressure gradient
grad_psi_ft = mw_ppg * 0.052
print(f"Mud gradient: {grad_psi_ft:.4f} psi/ft")

# Pressure at various depths
depths = [0, 2000, 4000, 6000, 8000, 10000]
print("\nDepth (ft) | Pressure (psi) | Pressure (ppg equiv)")
print("-" * 55)
for d in depths:
    P = surf_P + grad_psi_ft * d
    P_ppg = P / (0.052 * d) if d > 0 else mw_ppg
    print(f"{d:10,} | {P:14,.0f} | {P_ppg:.2f}")

# Buoyancy factor for steel casing
rho_steel_ppg = 65.4
BF = 1 - mw_ppg / rho_steel_ppg
print(f"\nBuoyancy factor: {BF:.4f}")
print(f"7-inch 26 lb/ft casing string: air weight = {26*10000:,} lb")
print(f"Buoyant weight = {26*10000*BF:,.0f} lb")
```

---

## Workflow Summary

### Step 1 — Identify Module

| User Request | Module |
|--------------|--------|
| Force equilibrium, reactions, truss, derrick loads | Module 1 — Statics |
| Axial stress, strain, elongation, thermal, casing tension | Module 2 — Axial |
| Bending moment, shear diagram, deflection | Module 3 — Beams |
| Casing burst/collapse, thick-walled cylinder, hoop stress | Module 4 — Thick-Walled Cylinder |
| Mohr's circle, principal stresses, transformation, torsion | Module 5 — Mohr's Circle |
| Mud pressure, hydrostatic, buoyancy, ECD | Module 6 — Fluid Statics |

### Step 2 — Gather Inputs

Collect required parameters. Always confirm units. Provide sensible defaults
from the typical Appalachian/Marcellus parameter set if user omits values.

### Step 3 — Calculate

Perform step-by-step arithmetic, showing each equation and substitution.
Include Python code using only `math` and `statistics` (stdlib). Label all
intermediate results with units.

### Step 4 — Output

Format as:

1. **Input summary table** — echo back all parameters and assumptions
2. **Equations used** — state the governing equations before substituting
3. **Step-by-step solution** — each calculation step with units
4. **Results table** — final computed values in both field and SI units
5. **Interpretation** — is the design adequate? What is the safety factor?
6. **Caveats** — assumptions, limits of validity, what to check next

---

## Output Format

```
## [Calculation Title]

### Problem Statement
[Restate what is being solved and why it matters]

### Input Parameters
| Parameter | Symbol | Value | Unit |
|-----------|--------|-------|------|
| ... | ... | ... | ... |

### Governing Equations
[State equations explicitly before substituting numbers]

### Solution
Step 1: [calculation with units]
Step 2: [calculation with units]
...

### Results
| Result | Value | Unit |
|--------|-------|------|
| ... | ... | ... |

**Summary:** [1-3 sentences on adequacy, safety factor, recommendation]

**Caveats:**
- [Key assumptions, e.g., "assumes purely axial loading — bending neglected"]
- [Validity range of any correlations used]
- [Recommend API standard or full analysis for design decisions]
```

---

## Error Handling

| Condition | Action |
|-----------|--------|
| Missing geometry (OD, ID, length) | Request from user; provide common API casing tables as reference |
| Pressure exceeds yield with SF less than 1 | Flag FAIL clearly; suggest next heavier weight or higher grade |
| Division by zero (zero area, zero moment arm) | Report degenerate geometry; ask user to verify |
| Value outside typical range | Warn with typical range; calculate anyway with disclaimer |
| Statically indeterminate without deformation data | Request E, A, or geometry for compatibility equation |

---

## Units Reference

All calculations default to **field units**. Present final answers in both field and SI.

| Quantity | Field Unit | SI Unit | Conversion |
|----------|-----------|---------|------------|
| Force | lb | N | 1 lb = 4.448 N |
| Pressure/Stress | psi | MPa | 1 psi = 0.006895 MPa |
| Length | ft or in | m | 1 ft = 0.3048 m; 1 in = 0.0254 m |
| Moment | lb-ft or lb-in | N-m | 1 lb-ft = 1.356 N-m |
| Young's modulus | psi | GPa | 30e6 psi = 207 GPa (steel) |
| Density | ppg | kg/m3 | 1 ppg = 119.8 kg/m3 |
| Mud gradient | psi/ft | kPa/m | 1 psi/ft = 22.62 kPa/m |
| Temperature | °F | °C | °C = (°F - 32) * 5/9 |

See `references/equations.md` for the complete equation library with derivations.
