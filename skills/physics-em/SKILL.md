---
name: physics-em
description: >
  Electricity and magnetism for engineers covering electrostatics, electric
  circuits, capacitors, magnetic forces, and electromagnetic induction.
  Implements Coulomb law, electric field and potential from point charges,
  parallel plate capacitor energy, Ohm law, series and parallel resistors,
  power dissipation, Kirchhoff voltage and current laws, RC time constant,
  Lorentz force, magnetic field from long wire, Faraday law for induced EMF,
  RL time constant, inductor energy, and LC oscillation frequency. Use when
  the user asks about Coulomb law, electric field, Gauss law, electric
  potential, capacitor energy, RC circuit, Kirchhoff laws, Ohm law, magnetic
  force, Faraday induction, RL circuit, LC resonance, electromagnetic
  induction, or any electricity and magnetism physics problem. Resources:
  Halliday Resnick Walker Fundamentals of Physics 12th ed; OpenStax University
  Physics Vol 2 free at openstax.org; MIT OCW 8.02SC; Walter Lewin MIT 8.02
  YouTube; Khan Academy AP Physics 2. Primary courses: PHYS 112 Physics for
  Engineers II.
---

# Electricity and Magnetism Calculator

Computational skill for PHYS 112-level electricity and magnetism covering
electrostatics, electric circuits, magnetic forces, and electromagnetic
induction. Built for WVU engineering students.

**SI units.** (C, V, A, Omega, F, H, T, Wb). Constants: k_e = 8.988e9 N*m^2/C^2;
mu_0 = 4*pi*1e-7 T*m/A; epsilon_0 = 8.854e-12 C^2/N/m^2.

---

## Module 1 — Electrostatics

```python
import math

k_e = 8.988e9     # N*m^2/C^2 (Coulomb's constant = 1/(4*pi*eps0))
eps_0 = 8.854e-12  # C^2/(N*m^2) = F/m
mu_0 = 4.0 * math.pi * 1e-7  # T*m/A

def coulombs_force(q1_C, q2_C, r_m):
    """
    Coulomb's law: F = k_e * |q1 * q2| / r^2
    q1, q2: charges (Coulombs; positive or negative)
    r:      separation distance (m)
    Returns: force magnitude (N); positive = repulsive, negative = attractive
    """
    F_mag = k_e * abs(q1_C * q2_C) / r_m**2
    F_sign = 1.0 if q1_C * q2_C > 0 else -1.0  # repulsive or attractive
    return {"F_N": round(F_mag, 6), "type": "repulsive" if F_sign > 0 else "attractive",
            "F_signed_N": round(F_sign * F_mag, 6)}

def electric_field_point_charge(q_C, r_m):
    """
    Electric field magnitude from a point charge: E = k_e * q / r^2
    Direction: away from q if q > 0, toward q if q < 0.
    Returns: E (N/C = V/m)
    """
    return {"E_N_per_C": round(k_e * abs(q_C) / r_m**2, 6),
            "direction": "radially outward" if q_C > 0 else "radially inward"}

def electric_potential_point_charge(q_C, r_m):
    """
    Electric potential from a point charge: V = k_e * q / r
    (Scalar; reference V=0 at r=infinity)
    Returns: V (Volts)
    """
    return k_e * q_C / r_m

def electric_potential_superposition(charges_C, positions_m, r_field_m):
    """
    Electric potential from multiple point charges (superposition):
    V_total = sum(k_e * q_i / |r - r_i|)
    charges_C:   list of charge values (C)
    positions_m: list of (x, y) positions of charges (m)
    r_field_m:   (x, y) position where V is evaluated (m)
    Returns: total potential (V)
    """
    V_total = 0.0
    for q, pos in zip(charges_C, positions_m):
        r = math.sqrt((r_field_m[0]-pos[0])**2 + (r_field_m[1]-pos[1])**2)
        if r < 1e-12:
            return float('inf')
        V_total += k_e * q / r
    return round(V_total, 6)

def work_by_electric_field(q_C, V1_V, V2_V):
    """
    Work done by electric field moving charge from V1 to V2:
    W = q * (V1 - V2)  (Joules)
    W > 0: field does positive work (charge moves in direction of field force)
    """
    return q_C * (V1_V - V2_V)
```

---

## Module 2 — Capacitors and Electric Energy

```python
def parallel_plate_capacitance(eps_r, A_m2, d_m):
    """
    Parallel plate capacitor: C = eps_r * eps_0 * A / d
    eps_r: relative permittivity (dielectric constant; 1 for vacuum/air)
    A:     plate area (m^2)
    d:     plate separation (m)
    Returns: C (Farads)
    Common dielectrics: air=1.0, glass=4-10, mica=3-6, water=80
    """
    return eps_r * eps_0 * A_m2 / d_m

def energy_stored_capacitor(C_F, V_volt):
    """
    Energy stored in capacitor: U = 0.5 * C * V^2 = Q^2/(2C) = Q*V/2
    Returns: U (Joules)
    """
    return 0.5 * C_F * V_volt**2

def capacitors_series(*C_values_F):
    """
    Series: 1/C_eq = sum(1/C_i)
    Returns: C_eq (F)
    """
    if any(c <= 0 for c in C_values_F):
        return None
    return 1.0 / sum(1.0/c for c in C_values_F)

def capacitors_parallel(*C_values_F):
    """Parallel: C_eq = sum(C_i)"""
    return sum(C_values_F)

def rc_time_constant(R_ohm, C_F):
    """tau = R * C  (seconds)"""
    return R_ohm * C_F

def rc_charging_voltage(V0_V, R_ohm, C_F, t_s):
    """
    RC charging: V(t) = V0 * (1 - exp(-t/RC))
    V0: supply voltage; V_C(0) = 0
    Returns: V_C at time t, charge Q, current I
    """
    tau = R_ohm * C_F
    V_C = V0_V * (1.0 - math.exp(-t_s / tau))
    Q = C_F * V_C
    I = (V0_V / R_ohm) * math.exp(-t_s / tau)
    return {"V_C_V": round(V_C, 6), "Q_C": round(Q, 9), "I_A": round(I, 9),
            "tau_s": round(tau, 6), "t_over_tau": round(t_s/tau, 4)}

def rc_discharging_voltage(V0_V, R_ohm, C_F, t_s):
    """
    RC discharging: V(t) = V0 * exp(-t/RC)
    V0: initial capacitor voltage
    """
    tau = R_ohm * C_F
    V_C = V0_V * math.exp(-t_s / tau)
    I = (V0_V / R_ohm) * math.exp(-t_s / tau)
    return {"V_C_V": round(V_C, 6), "I_A": round(I, 9), "tau_s": round(tau, 6)}
```

---

## Module 3 — DC Circuits

```python
def ohms_law(V_V=None, I_A=None, R_ohm=None):
    """V = I * R; solve for the missing variable."""
    if V_V is None and I_A is not None and R_ohm is not None:
        return {"V_V": round(I_A * R_ohm, 6)}
    elif I_A is None and V_V is not None and R_ohm is not None:
        return {"I_A": round(V_V / R_ohm, 9) if R_ohm > 0 else None}
    elif R_ohm is None and V_V is not None and I_A is not None:
        return {"R_ohm": round(V_V / I_A, 6) if I_A > 0 else None}
    return {"error": "Provide exactly 2 of: V, I, R"}

def resistors_series(*R_values_ohm):
    """R_eq = sum(R_i)  [series]"""
    return sum(R_values_ohm)

def resistors_parallel(*R_values_ohm):
    """1/R_eq = sum(1/R_i)  [parallel]"""
    if any(r <= 0 for r in R_values_ohm):
        return None
    return 1.0 / sum(1.0/r for r in R_values_ohm)

def power_dissipated(I_A=None, V_V=None, R_ohm=None):
    """P = I^2*R = V^2/R = I*V  (Watts)"""
    if I_A is not None and R_ohm is not None:
        return round(I_A**2 * R_ohm, 9)
    elif V_V is not None and R_ohm is not None:
        return round(V_V**2 / R_ohm, 9) if R_ohm > 0 else None
    elif I_A is not None and V_V is not None:
        return round(I_A * V_V, 9)
    return None

def voltage_divider(V_total_V, R1_ohm, R2_ohm):
    """
    Voltage divider: V_out = V_total * R2 / (R1 + R2)
    V_out is across R2 (the lower resistor in series).
    """
    R_total = R1_ohm + R2_ohm
    V_out = V_total_V * R2_ohm / R_total
    I = V_total_V / R_total
    return {"V_out_V": round(V_out, 6), "I_A": round(I, 9)}

def kirchhoff_two_loop_example():
    """
    Kirchhoff's Laws reminder:
    KVL (Voltage): sum of voltage drops around any closed loop = 0
      (+) for EMF sources in direction of current traversal
      (-) for resistors in direction of current traversal
    KCL (Current): sum of currents into any node = 0
      Assign unknown currents, write KVL equations, solve system.
    Returns: methodology guide
    """
    return {
        "KVL": "sum(EMF) - sum(I*R) = 0 for each closed loop",
        "KCL": "sum(I_in) = sum(I_out) at each node",
        "steps": [
            "1. Assign current directions (arbitrary; negative result = actual direction reversed)",
            "2. Write KCL equations for each independent node",
            "3. Write KVL equations for each independent loop",
            "4. Solve the linear system (N equations, N unknowns)"
        ]
    }
```

---

## Module 4 — Magnetic Forces and Fields

```python
def magnetic_force_on_charge(q_C, v_m_s, B_T, theta_deg=90.0):
    """
    Lorentz force: F = q * v * B * sin(theta)
    theta: angle between velocity vector and magnetic field B
    F is perpendicular to both v and B (use right-hand rule for direction)
    """
    return abs(q_C) * v_m_s * B_T * math.sin(math.radians(theta_deg))

def magnetic_force_on_wire(I_A, L_m, B_T, theta_deg=90.0):
    """
    Force on current-carrying wire: F = I * L * B * sin(theta)
    theta: angle between wire direction and B field
    """
    return I_A * L_m * B_T * math.sin(math.radians(theta_deg))

def magnetic_field_long_wire(I_A, r_m):
    """
    Magnetic field from infinite straight wire (Biot-Savart / Ampere's law):
    B = mu_0 * I / (2 * pi * r)
    Direction: right-hand rule (curl fingers in direction of B around wire)
    Returns: B (Tesla)
    """
    return mu_0 * I_A / (2.0 * math.pi * r_m)

def magnetic_field_solenoid(n_turns_per_m, I_A):
    """
    Magnetic field inside a long solenoid: B = mu_0 * n * I
    n_turns_per_m: turns per meter (n = N/L)
    Returns: B (Tesla)
    """
    return mu_0 * n_turns_per_m * I_A

def cyclotron_radius(m_kg, v_m_s, q_C, B_T):
    """
    Radius of circular motion of charged particle in magnetic field:
    r = m*v / (|q|*B)
    Cyclotron period: T = 2*pi*m / (|q|*B)  (independent of speed!)
    """
    r = m_kg * v_m_s / (abs(q_C) * B_T)
    T = 2.0 * math.pi * m_kg / (abs(q_C) * B_T)
    return {"r_m": round(r, 9), "T_period_s": round(T, 12)}
```

---

## Module 5 — Electromagnetic Induction

```python
def faraday_emf(N_turns, d_flux_Wb, d_t_s):
    """
    Faraday's law: emf = -N * dPhi_B/dt
    N:      number of turns in coil
    dPhi_B: change in magnetic flux (Wb = T*m^2)
    dt:     time interval (s)
    Returns: induced EMF (V); magnitude given (sign from Lenz's law)
    """
    return abs(N_turns * d_flux_Wb / d_t_s)

def magnetic_flux(B_T, A_m2, theta_deg=0.0):
    """
    Magnetic flux: Phi = B * A * cos(theta)
    theta: angle between B vector and the normal to the area A
    theta=0 means B is perpendicular to the loop (maximum flux)
    Returns: Phi (Weber = T*m^2)
    """
    return B_T * A_m2 * math.cos(math.radians(theta_deg))

def rl_time_constant(R_ohm, L_H):
    """tau_L = L / R  (seconds)"""
    return L_H / R_ohm

def rl_current_buildup(I_max_A, R_ohm, L_H, t_s):
    """
    RL current buildup: I(t) = I_max * (1 - exp(-R*t/L)) = I_max*(1 - exp(-t/tau))
    I_max = V_source / R
    Returns: I at time t, stored energy in inductor
    """
    tau = L_H / R_ohm
    I = I_max_A * (1.0 - math.exp(-t_s / tau))
    U_L = 0.5 * L_H * I**2
    return {"I_A": round(I, 9), "U_inductor_J": round(U_L, 9),
            "tau_s": round(tau, 6), "t_over_tau": round(t_s/tau, 4)}

def energy_stored_inductor(L_H, I_A):
    """U_L = 0.5 * L * I^2  (Joules)"""
    return 0.5 * L_H * I_A**2

def lc_oscillation(L_H, C_F):
    """
    LC circuit oscillation frequency:
    omega_0 = 1/sqrt(L*C)  (rad/s)
    T = 2*pi*sqrt(L*C)     (s)
    f = 1/(2*pi*sqrt(L*C)) (Hz)
    Analogy: L <-> m (mass), C <-> 1/k (spring compliance), I <-> v, Q <-> x
    """
    omega_0 = 1.0 / math.sqrt(L_H * C_F)
    T = 2.0 * math.pi * math.sqrt(L_H * C_F)
    return {"omega_0_rad_s": round(omega_0, 6), "T_s": round(T, 9),
            "f_Hz": round(1.0/T, 6)}

def rlc_resonance(R_ohm, L_H, C_F):
    """
    RLC series circuit:
    Resonance frequency: f_0 = 1/(2*pi*sqrt(L*C))
    Quality factor: Q = (1/R)*sqrt(L/C)
    Bandwidth: delta_f = R / (2*pi*L) = f_0 / Q
    """
    omega_0 = 1.0 / math.sqrt(L_H * C_F)
    f_0 = omega_0 / (2.0 * math.pi)
    Q = (1.0/R_ohm) * math.sqrt(L_H / C_F)
    bandwidth = f_0 / Q
    return {"f_resonance_Hz": round(f_0, 6), "Q_factor": round(Q, 4),
            "bandwidth_Hz": round(bandwidth, 6),
            "Z_at_resonance_ohm": R_ohm}
```

---

## Learning Resources

### Textbooks

| Author(s) | Title | Edition | Access |
|-----------|-------|---------|--------|
| Halliday, Resnick & Walker | *Fundamentals of Physics* | 12th ed. (2021) | ISBN 978-1-119-80114-6 |
| Serway & Jewett | *Physics for Scientists & Engineers* Vol. 2 | 10th ed. (2018) | ISBN 978-1-337-55358-2 |
| OpenStax | *University Physics Vol. 2* | Free | openstax.org/details/books/university-physics-volume-2 |
| Griffiths, D.J. | *Introduction to Electrodynamics* | 4th ed. (2017) | ISBN 978-0-321-85656-2 (deeper theory) |

### Free Online Resources

| Resource | URL | Notes |
|----------|-----|-------|
| Walter Lewin MIT 8.02 YouTube | youtube.com/playlist?list=PLyQSN7X0ro2314mKyUiOILaOC2hk6Pc3j | 36 lectures; legendary demos |
| MIT OCW 8.02SC | ocw.mit.edu/courses/8-02sc-physics-ii-electricity-and-magnetism-fall-2010/ | Structured Scholar version with recitation videos |
| Khan Academy AP Physics 2 | khanacademy.org/science/ap-physics-2 | Full E&M unit + practice |
| OpenStax Physics Vol. 2 | openstax.org/details/books/university-physics-volume-2 | Free complete textbook |
| PhET Simulations | phet.colorado.edu/en/simulations/filter?subjects=electricity-magnets-and-circuits | Interactive circuit/field sims |
| Michel van Biezen E&M | youtube.com/@MichelvanBiezen | Thousands of worked problems |

### WVU Courses

- **PHYS 112** General Physics II — E&M, optics, modern physics (calculus-based)
- **ECE 211** Circuit Analysis I — Kirchhoff's laws, AC circuits (deeper coverage)

---

## Output Format

```
## E&M Problem — [Topic]: [Problem Description]

### Given
| Variable | Symbol | Value | Units |
|----------|--------|-------|-------|
| | | | |

### Equations Applied
1. [name]: [formula with units]
2. [name]: [formula]

### Solution
Step 1 — [step name]:
[calculation] = [answer] [units]

Step 2:
[calculation] = [answer] [units]

### Result
| Quantity | Value | Units |
|----------|-------|-------|
| | | |

**Unit check:** [confirm unit analysis]
**Reasonableness:** [typical field strengths / voltages / currents comparison]

### Check Your Understanding
[One follow-up conceptual question]
```

---

## Error Handling

| Condition | Cause | Action |
|-----------|-------|--------|
| V_C > V_source in RC charging | Wrong formula (use charging, not discharging) | Swap to rc_charging_voltage |
| Negative capacitance from series | Calculation error | Sum reciprocals first, then invert |
| B = 0 at wire location | r = 0 input | Field inside conductor requires Ampere's law with enclosed current |
| LC frequency very high or low | Unit mismatch | Verify L in Henries, C in Farads |

---

## Caveats

- **Gauss's Law** is conceptual in this skill. For Gauss's law calculations (E from
  symmetric charge distributions — sphere, infinite line, infinite plane), use
  the integral form Phi_E = Q_enc / epsilon_0 directly.
- **Right-hand rule** for magnetic force direction is not computable as a scalar;
  always apply RHR manually: point fingers in v direction, curl toward B, thumb
  points in F direction for positive charge.
- **AC circuits** (impedance, phasors, power factor) are not covered here.
  For AC analysis, use Z_C = 1/(j*omega*C), Z_L = j*omega*L.
- **Displacement current** (Maxwell's addition to Ampere's law) is not implemented.
  For radiation and electromagnetic wave problems, refer to Griffiths Ch. 9-10.
- RC and RL time constants assume ideal (lossless) components. Real capacitors
  have leakage resistance; real inductors have resistance.
