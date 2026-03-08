---
name: physics-mechanics
description: >
  Classical mechanics for engineers covering kinematics, Newton laws,
  work-energy theorem, momentum, rotational dynamics, and simple harmonic
  motion. Implements constant-acceleration kinematics, projectile motion,
  centripetal acceleration, free body diagram force analysis with friction
  and inclines, work and kinetic and potential energy, conservation of
  mechanical energy, elastic and inelastic collisions, torque, moment of
  inertia for common shapes, and SHM for springs and pendulums. Use when the
  user asks about kinematics equations, Newton second law, projectile motion,
  conservation of energy, momentum collision, circular motion, centripetal
  force, torque, rotational inertia, angular momentum, simple harmonic motion,
  spring constant, oscillation frequency, or any classical mechanics physics
  problem. Resources: Halliday Resnick Walker Fundamentals of Physics 12th ed;
  OpenStax University Physics Vol 1 free at openstax.org; MIT OCW 8.01SC
  Classical Mechanics; Walter Lewin MIT 8.01 YouTube; Khan Academy AP
  Physics 1. Primary courses: PHYS 111 Physics for Engineers I, MAE 201.
---

# Classical Mechanics Calculator

Computational skill for PHYS 111-level classical mechanics covering kinematics,
Newton's laws, energy, momentum, rotation, and oscillations. Built for WVU
engineering students in calculus-based physics.

**SI units throughout.** (m, s, kg, N, J, W). Convert: 1 lb = 4.448 N;
1 ft = 0.3048 m; 1 mile/hr = 0.4470 m/s.

---

## Module 1 — Kinematics (Constant Acceleration)

```python
import math

def kinematics_solve(v0=None, v=None, a=None, t=None, x=None):
    """
    Constant-acceleration kinematics: given any 3 of 5 variables, solve for the other 2.
    Equations:
      v = v0 + a*t
      x = v0*t + 0.5*a*t^2
      v^2 = v0^2 + 2*a*x
      x = 0.5*(v0+v)*t
    Returns: dict with all 5 variables and which were solved.
    """
    known = {"v0": v0, "v": v, "a": a, "t": t, "x": x}
    n_known = sum(1 for val in known.values() if val is not None)
    if n_known < 3:
        return {"error": "Need at least 3 known variables"}

    # Try to solve for unknowns
    solved = dict(known)

    # v = v0 + a*t
    if solved["v"] is None and solved["v0"] is not None and solved["a"] is not None and solved["t"] is not None:
        solved["v"] = solved["v0"] + solved["a"] * solved["t"]
    if solved["t"] is None and solved["v"] is not None and solved["v0"] is not None and solved["a"] is not None:
        if abs(solved["a"]) > 1e-12:
            solved["t"] = (solved["v"] - solved["v0"]) / solved["a"]
    if solved["a"] is None and solved["v"] is not None and solved["v0"] is not None and solved["t"] is not None:
        if abs(solved["t"]) > 1e-12:
            solved["a"] = (solved["v"] - solved["v0"]) / solved["t"]

    # x = v0*t + 0.5*a*t^2
    if solved["x"] is None and solved["v0"] is not None and solved["a"] is not None and solved["t"] is not None:
        solved["x"] = solved["v0"] * solved["t"] + 0.5 * solved["a"] * solved["t"]**2

    # v^2 = v0^2 + 2*a*x
    if solved["v"] is None and solved["v0"] is not None and solved["a"] is not None and solved["x"] is not None:
        v_sq = solved["v0"]**2 + 2.0 * solved["a"] * solved["x"]
        if v_sq >= 0:
            solved["v"] = math.sqrt(v_sq)
    if solved["x"] is None and solved["v"] is not None and solved["v0"] is not None and solved["a"] is not None:
        if abs(solved["a"]) > 1e-12:
            solved["x"] = (solved["v"]**2 - solved["v0"]**2) / (2.0 * solved["a"])

    return {k: round(v, 6) if v is not None else None for k, v in solved.items()}

def projectile_motion(v0_m_s, theta_deg, h0_m=0.0, g=9.81):
    """
    Projectile motion with launch angle theta above horizontal.
    v0:    launch speed (m/s)
    theta: launch angle (degrees above horizontal)
    h0:    initial height above ground (m)
    Returns: range, max height, time of flight, velocity components
    """
    theta_rad = math.radians(theta_deg)
    v0x = v0_m_s * math.cos(theta_rad)
    v0y = v0_m_s * math.sin(theta_rad)

    # Time of flight (land at h=0): h0 + v0y*t - 0.5*g*t^2 = 0
    discriminant = v0y**2 + 2.0 * g * h0_m
    if discriminant < 0:
        return {"error": "Projectile never reaches ground"}
    t_flight = (v0y + math.sqrt(discriminant)) / g

    x_range = v0x * t_flight
    t_peak = v0y / g
    h_max = h0_m + v0y * t_peak - 0.5 * g * t_peak**2 if t_peak > 0 else h0_m

    return {
        "range_m": round(x_range, 4),
        "max_height_m": round(h_max, 4),
        "time_of_flight_s": round(t_flight, 4),
        "v0x_m_s": round(v0x, 4),
        "v0y_m_s": round(v0y, 4),
        "v_impact_m_s": round(math.sqrt(v0x**2 + (v0y - g*t_flight)**2), 4)
    }

def circular_motion(v_m_s=None, r_m=None, omega_rad_s=None, T_s=None):
    """
    Uniform circular motion: v = r*omega, T = 2*pi*r/v = 2*pi/omega
    Centripetal acceleration: a_c = v^2/r = r*omega^2
    Provide any 2 of (v, r, omega, T); returns all quantities.
    """
    if v_m_s and r_m:
        omega = v_m_s / r_m
        T = 2 * math.pi / omega
    elif omega_rad_s and r_m:
        v_m_s = omega_rad_s * r_m
        T = 2 * math.pi / omega_rad_s
        omega = omega_rad_s
    elif T_s and r_m:
        omega = 2 * math.pi / T_s
        v_m_s = omega * r_m
        T = T_s
    else:
        return {"error": "Provide at least 2 of: v, r, omega, T"}
    a_c = v_m_s**2 / r_m
    return {"v_m_s": round(v_m_s, 4), "omega_rad_s": round(omega, 4),
            "T_period_s": round(T, 4), "a_centripetal_m_s2": round(a_c, 4)}
```

---

## Module 2 — Newton's Laws and Force Analysis

```python
def normal_force_incline(m_kg, theta_deg, g=9.81):
    """
    Normal force and friction on an inclined plane.
    N = m*g*cos(theta)
    Component along incline = m*g*sin(theta)
    """
    theta = math.radians(theta_deg)
    N = m_kg * g * math.cos(theta)
    F_parallel = m_kg * g * math.sin(theta)
    return {"N_normal_force_N": round(N, 4),
            "F_along_incline_N": round(F_parallel, 4)}

def friction_force(mu, N_newton):
    """f_friction = mu * N  (kinetic or static)"""
    return mu * N_newton

def net_force_and_acceleration(forces_N_list, m_kg):
    """Sum forces and apply Newton's 2nd law: a = F_net / m"""
    F_net = sum(forces_N_list)
    a = F_net / m_kg if m_kg > 0 else None
    return {"F_net_N": round(F_net, 4), "a_m_s2": round(a, 4) if a is not None else None}

def atwood_machine(m1_kg, m2_kg, g=9.81):
    """
    Atwood machine (two masses over frictionless pulley):
    a = (m1 - m2) * g / (m1 + m2)
    T = 2 * m1 * m2 * g / (m1 + m2)
    """
    a = (m1_kg - m2_kg) * g / (m1_kg + m2_kg)
    T = 2.0 * m1_kg * m2_kg * g / (m1_kg + m2_kg)
    return {"a_m_s2": round(a, 4), "T_tension_N": round(T, 4)}
```

---

## Module 3 — Work, Energy, and Power

```python
def work_constant_force(F_N, d_m, theta_deg=0.0):
    """W = F * d * cos(theta); theta = angle between force and displacement."""
    return F_N * d_m * math.cos(math.radians(theta_deg))

def kinetic_energy(m_kg, v_m_s):
    """KE = 0.5 * m * v^2  (Joules)"""
    return 0.5 * m_kg * v_m_s**2

def gravitational_pe(m_kg, h_m, g=9.81):
    """PE = m * g * h  (Joules; h measured from reference level)"""
    return m_kg * g * h_m

def spring_pe(k_N_m, x_m):
    """Elastic PE = 0.5 * k * x^2  (Joules; x = compression/extension)"""
    return 0.5 * k_N_m * x_m**2

def conservation_of_energy(KE1_J, PE1_J, W_nc_J=0.0):
    """
    Conservation of mechanical energy: E1 + W_nc = E2
    W_nc: work by non-conservative forces (negative for friction)
    Returns: total mechanical energy at state 2
    """
    return KE1_J + PE1_J + W_nc_J

def power_watt(W_J, t_s=None, F_N=None, v_m_s=None):
    """
    Power: P = W/t  (J/s = W)  OR  P = F*v (for constant force and velocity)
    """
    if t_s is not None and t_s > 0:
        return {"P_W": round(W_J / t_s, 4), "P_hp": round(W_J / t_s / 745.7, 4)}
    elif F_N is not None and v_m_s is not None:
        P = F_N * v_m_s
        return {"P_W": round(P, 4), "P_hp": round(P / 745.7, 4)}
    return None
```

---

## Module 4 — Momentum and Collisions

```python
def momentum(m_kg, v_m_s):
    """p = m * v  (kg*m/s)"""
    return m_kg * v_m_s

def impulse(F_avg_N, delta_t_s):
    """J = F * delta_t = delta_p  (kg*m/s)"""
    return F_avg_N * delta_t_s

def elastic_collision_1d(m1_kg, v1i_m_s, m2_kg, v2i_m_s):
    """
    1D elastic collision: conserves both momentum and kinetic energy.
    v1f = ((m1-m2)*v1i + 2*m2*v2i) / (m1+m2)
    v2f = ((m2-m1)*v2i + 2*m1*v1i) / (m1+m2)
    """
    M = m1_kg + m2_kg
    v1f = ((m1_kg - m2_kg) * v1i_m_s + 2 * m2_kg * v2i_m_s) / M
    v2f = ((m2_kg - m1_kg) * v2i_m_s + 2 * m1_kg * v1i_m_s) / M
    KE_i = 0.5*m1_kg*v1i_m_s**2 + 0.5*m2_kg*v2i_m_s**2
    KE_f = 0.5*m1_kg*v1f**2 + 0.5*m2_kg*v2f**2
    return {"v1f_m_s": round(v1f, 5), "v2f_m_s": round(v2f, 5),
            "KE_conserved": abs(KE_f - KE_i) < 1e-8 * KE_i}

def perfectly_inelastic_collision_1d(m1_kg, v1i_m_s, m2_kg, v2i_m_s):
    """
    Perfectly inelastic: objects stick together after collision.
    vf = (m1*v1i + m2*v2i) / (m1+m2)
    """
    vf = (m1_kg * v1i_m_s + m2_kg * v2i_m_s) / (m1_kg + m2_kg)
    KE_i = 0.5*m1_kg*v1i_m_s**2 + 0.5*m2_kg*v2i_m_s**2
    KE_f = 0.5*(m1_kg + m2_kg)*vf**2
    KE_lost = KE_i - KE_f
    return {"vf_m_s": round(vf, 5),
            "KE_lost_J": round(KE_lost, 5),
            "fraction_KE_lost": round(KE_lost / KE_i, 4) if KE_i > 0 else 0.0}
```

---

## Module 5 — Rotational Motion and SHM

```python
def torque(F_N, r_m, theta_deg=90.0):
    """tau = r * F * sin(theta)  (N*m); theta = angle between r and F vectors."""
    return r_m * F_N * math.sin(math.radians(theta_deg))

def moment_of_inertia(shape, m_kg, R_m=None, L_m=None):
    """
    Moment of inertia about axis through center of mass:
    solid_sphere:   I = 0.4 * m * R^2
    hollow_sphere:  I = 0.667 * m * R^2
    solid_disk:     I = 0.5 * m * R^2  (about axis through center, perpendicular to disk)
    hollow_hoop:    I = m * R^2
    thin_rod_center: I = m * L^2 / 12  (axis through center, perpendicular to rod)
    thin_rod_end:   I = m * L^2 / 3   (axis through end)
    """
    s = shape.lower().replace("-", "_")
    if s == "solid_sphere":
        return 0.4 * m_kg * R_m**2
    elif s in ("hollow_sphere", "spherical_shell"):
        return (2.0/3.0) * m_kg * R_m**2
    elif s in ("solid_disk", "cylinder"):
        return 0.5 * m_kg * R_m**2
    elif s in ("hollow_hoop", "thin_ring", "hoop"):
        return m_kg * R_m**2
    elif s == "thin_rod_center":
        return m_kg * L_m**2 / 12.0
    elif s == "thin_rod_end":
        return m_kg * L_m**2 / 3.0
    else:
        return None

def angular_momentum(I_kg_m2, omega_rad_s):
    """L = I * omega  (kg*m^2/s)"""
    return I_kg_m2 * omega_rad_s

def rotational_ke(I_kg_m2, omega_rad_s):
    """KE_rot = 0.5 * I * omega^2  (Joules)"""
    return 0.5 * I_kg_m2 * omega_rad_s**2

def shm_spring(m_kg, k_N_m):
    """
    Simple harmonic motion — mass-spring system:
    omega = sqrt(k/m)  (rad/s)
    T = 2*pi*sqrt(m/k)  (s)
    f = 1/T  (Hz)
    """
    omega = math.sqrt(k_N_m / m_kg)
    T = 2.0 * math.pi / omega
    return {"omega_rad_s": round(omega, 5), "T_s": round(T, 5),
            "f_Hz": round(1.0/T, 5)}

def shm_pendulum(L_m, g=9.81):
    """
    Simple pendulum (small angle approximation):
    T = 2*pi*sqrt(L/g)
    Valid for theta_max < ~15 degrees
    """
    omega = math.sqrt(g / L_m)
    T = 2.0 * math.pi / omega
    return {"omega_rad_s": round(omega, 5), "T_s": round(T, 5),
            "f_Hz": round(1.0/T, 5)}

def shm_displacement(A_m, omega_rad_s, t_s, phi_rad=0.0):
    """
    SHM position: x(t) = A * cos(omega*t + phi)
    v(t) = -A*omega * sin(omega*t + phi)
    a(t) = -A*omega^2 * cos(omega*t + phi)
    """
    x = A_m * math.cos(omega_rad_s * t_s + phi_rad)
    v = -A_m * omega_rad_s * math.sin(omega_rad_s * t_s + phi_rad)
    a = -A_m * omega_rad_s**2 * math.cos(omega_rad_s * t_s + phi_rad)
    return {"x_m": round(x, 6), "v_m_s": round(v, 6), "a_m_s2": round(a, 6)}
```

---

## Learning Resources

### Textbooks

| Author(s) | Title | Edition | ISBN |
|-----------|-------|---------|------|
| Halliday, Resnick & Walker | *Fundamentals of Physics* | 12th ed. (2021) | 978-1-119-80114-6 |
| Serway & Jewett | *Physics for Scientists and Engineers* | 10th ed. (2018) | 978-1-337-55329-2 |
| OpenStax | *University Physics Vol. 1* | Free at openstax.org | 978-1-947172-20-3 |

### Free Online Resources

| Resource | URL | Notes |
|----------|-----|-------|
| Walter Lewin MIT 8.01 YouTube | youtube.com/playlist?list=PLyQSN7X0ro203puVhQsmCj9qhlFQ-As8e | 35 lectures; legendary demonstrations |
| MIT OCW 8.01SC | ocw.mit.edu/courses/8-01sc-classical-mechanics-fall-2016/ | Structured self-study with recitation videos |
| Khan Academy AP Physics 1 | khanacademy.org/science/ap-physics-1 | Full unit coverage + practice |
| OpenStax Physics Vol. 1 | openstax.org/details/books/university-physics-volume-1 | Free complete textbook |
| HyperPhysics Mechanics | hyperphysics.phy-astr.gsu.edu/hbase/hph.html | Formula reference |
| Michel van Biezen (ilectureonline) | youtube.com/@MichelvanBiezen | Thousands of worked examples |

### WVU Courses

- **PHYS 111** General Physics I — mechanics, waves, heat (calculus-based)
- **MAE 201** Engineering Statics — Newton's laws applied to rigid body equilibrium
- **MAE 243** Mechanics of Materials — stress/strain (see also `pnge:pnge-mechanics`)

---

## Output Format

```
## Classical Mechanics — [Topic]: [Problem Description]

### Given
| Variable | Symbol | Value | Units |
|----------|--------|-------|-------|
| | | | |

### Equations Applied
1. [equation name]: [formula]
2. [equation name]: [formula]

### Solution
Step 1 — [step name]:
[calculation] = [answer] [units]

Step 2:
[calculation] = [answer] [units]

### Result
| Quantity | Value | Units |
|----------|-------|-------|
| | | |

**Unit check:** [confirm units cancel correctly]
**Reasonableness:** [Is this physically sensible? Compare to everyday experience]

### Check Your Understanding
[One follow-up question testing the underlying concept]
```

---

## Error Handling

| Condition | Cause | Action |
|-----------|-------|--------|
| Negative discriminant in projectile | Not enough energy to reach ground from given height | Check if h0 < 0 or v0 too small for given angle |
| v^2 negative in kinematics | Object decelerates to stop before given distance | Confirm direction of acceleration; object may not travel that far |
| I = None returned | Shape name not recognized | Check spelling; available: solid_sphere, solid_disk, hoop, thin_rod_center, thin_rod_end |
| Zero division in circular motion | r = 0 | Radius must be non-zero |

---

## Caveats

- **Small-angle approximation for pendulum.** T = 2*pi*sqrt(L/g) is exact only for
  theta = 0; for theta_max = 15 deg, error is ~0.5%; for 30 deg, error is ~1.7%.
- **Point mass assumed** for translational kinematics. Rotational inertia requires
  the object's moment of inertia about the rotation axis.
- **Elastic collision assumes 1D.** For 2D collisions, use vector components and
  conserve both x and y momentum separately.
- **Rolling without slipping:** For a rolling object, total KE = KE_trans + KE_rot =
  0.5*m*v^2 + 0.5*I*omega^2 = 0.5*m*v^2*(1 + I/(m*R^2)).
- **g varies with altitude and latitude.** g = 9.81 m/s^2 is standard sea level.
  At WVU (elevation ~975 ft), g ≈ 9.803 m/s^2.
