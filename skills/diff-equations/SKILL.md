---
name: diff-equations
description: >
  Ordinary differential equations for engineering applications covering
  first-order ODEs, second-order linear ODEs with constant coefficients,
  Laplace transforms, eigenvalue systems, and numerical methods. Implements
  integrating factor, characteristic equation, undetermined coefficients,
  Laplace transform pairs, inverse Laplace via partial fractions, Euler method,
  RK4, eigenvalue method for linear systems, and phase plane classification.
  Use when the user asks about separable ODE, integrating factor, first-order
  linear ODE, second-order ODE, characteristic equation, undetermined
  coefficients, variation of parameters, Laplace transform, inverse Laplace,
  systems of ODEs, Euler method, Runge-Kutta, phase plane, direction field,
  or any ordinary differential equation solution. Resources: Boyce DiPrima
  Elementary Differential Equations 12th ed ISBN 978-1-119-44377-3; Paul
  Online Math Notes free at tutorial.math.lamar.edu; Professor Leonard ODE
  YouTube playlist; MIT OCW 18.03SC; 3Blue1Brown Differential Equations.
  Primary courses: MATH 261 Differential Equations.
---

# Ordinary Differential Equations

Computational skill for MATH 261-level ODE methods including analytical
solutions, Laplace transforms, and numerical methods. Engineering applications
include RC circuits, mechanical vibrations, population dynamics, and reactor
models — all governed by ODEs.

**Notation:** y' = dy/dt; y'' = d^2y/dt^2; IVP = initial value problem.

---

## Module 1 — First-Order ODEs

```python
import math

def solve_separable_check(expr_gy, expr_fx):
    """
    Check if dy/dt = f(t) * g(y) is separable (it always is if written this way).
    Separable form: g(y) dy = f(t) dt  =>  integrate both sides.
    Returns: guide to separation of variables method.
    """
    return {
        "method": "Separation of Variables",
        "steps": [
            "1. Rewrite as: [1/g(y)] dy = f(t) dt",
            "2. Integrate both sides",
            "3. Solve explicitly for y if possible",
            "4. Apply initial condition to find C"
        ],
        "common_integrals": {
            "1/y dy": "ln|y| + C",
            "y^n dy": "y^(n+1)/(n+1) + C",
            "e^(ay) dy": "e^(ay)/a + C",
            "sin(at) dt": "-cos(at)/a + C",
            "cos(at) dt": "sin(at)/a + C",
            "1/(1+t^2) dt": "arctan(t) + C"
        }
    }

def integrating_factor_linear(P_func_of_t_str, Q_func_of_t_str):
    """
    First-order linear ODE: y' + P(t)*y = Q(t)
    Integrating factor: mu(t) = exp(integral of P(t) dt)
    Solution: y = [1/mu(t)] * integral(mu(t)*Q(t) dt) + C/mu(t)
    Returns: methodology guide (symbolic, not automatic)
    """
    return {
        "ODE_form": "y' + P(t)*y = Q(t)",
        "integrating_factor": "mu(t) = exp(integral P(t) dt)",
        "solution": "y = (1/mu) * [integral(mu * Q dt) + C]",
        "key_step": f"P(t) = {P_func_of_t_str}, Q(t) = {Q_func_of_t_str}",
        "common_P_forms": {
            "P = a (constant)": "mu = exp(a*t)",
            "P = a/t":          "mu = t^a",
            "P = 2t":           "mu = exp(t^2)",
        }
    }

def first_order_linear_constant_coeff(a, b, y0, t_values):
    """
    Solve y' + a*y = b (constant coefficients, constant forcing).
    Solution: y(t) = (y0 - b/a)*exp(-a*t) + b/a   (a != 0)
    y0: initial condition y(0) = y0
    t_values: list of time values at which to evaluate y
    Returns: list of (t, y(t)) pairs
    """
    if abs(a) < 1e-12:
        # y' = b  =>  y = y0 + b*t
        return [(t, round(y0 + b*t, 8)) for t in t_values]
    y_eq = b / a  # equilibrium (particular) solution
    C = y0 - y_eq  # integration constant
    return [(t, round(C * math.exp(-a * t) + y_eq, 8)) for t in t_values]
```

---

## Module 2 — Second-Order Linear ODEs (Constant Coefficients)

```python
def characteristic_roots(a_coef, b_coef, c_coef):
    """
    Characteristic equation for a*y'' + b*y' + c*y = 0:
    ar^2 + br + c = 0  =>  r = (-b +/- sqrt(b^2 - 4ac)) / (2a)

    Discriminant determines solution form:
      D > 0: Two real distinct roots r1, r2
             y_h = C1*exp(r1*t) + C2*exp(r2*t)
      D = 0: Repeated root r = -b/(2a)
             y_h = (C1 + C2*t)*exp(r*t)
      D < 0: Complex conjugate roots alpha +/- i*beta
             y_h = exp(alpha*t) * (C1*cos(beta*t) + C2*sin(beta*t))
    """
    D = b_coef**2 - 4.0 * a_coef * c_coef

    if D > 1e-12:  # Two real distinct roots
        r1 = (-b_coef + math.sqrt(D)) / (2.0 * a_coef)
        r2 = (-b_coef - math.sqrt(D)) / (2.0 * a_coef)
        return {
            "discriminant": round(D, 8),
            "root_type": "real distinct",
            "r1": round(r1, 8), "r2": round(r2, 8),
            "y_h": "C1*exp({:.4f}*t) + C2*exp({:.4f}*t)".format(r1, r2),
            "behavior": "overdamped" if r1 < 0 and r2 < 0 else "unstable" if r1 > 0 or r2 > 0 else "mixed"
        }
    elif abs(D) <= 1e-12:  # Repeated root
        r = -b_coef / (2.0 * a_coef)
        return {
            "discriminant": 0.0,
            "root_type": "repeated real",
            "r": round(r, 8),
            "y_h": "(C1 + C2*t)*exp({:.4f}*t)".format(r),
            "behavior": "critically damped" if r < 0 else "linear growth"
        }
    else:  # Complex roots
        alpha = -b_coef / (2.0 * a_coef)
        beta = math.sqrt(-D) / (2.0 * a_coef)
        return {
            "discriminant": round(D, 8),
            "root_type": "complex conjugate",
            "alpha": round(alpha, 8), "beta": round(beta, 8),
            "y_h": "exp({:.4f}*t) * (C1*cos({:.4f}*t) + C2*sin({:.4f}*t))".format(alpha, beta, beta),
            "omega_n": round(beta, 8),
            "behavior": "underdamped oscillation" if alpha < 0 else ("undamped" if abs(alpha) < 1e-10 else "oscillatory growth")
        }

def undetermined_coefficients_guess(forcing_type, coefficients=None):
    """
    Undetermined coefficients method: guess form for y_p based on right-hand side.
    forcing_type: 'polynomial', 'exponential', 'sinusoidal', 'poly_exp', 'poly_sin'
    Returns: guess form for particular solution
    """
    table = {
        "polynomial_n": "y_p = A_n*t^n + A_{n-1}*t^(n-1) + ... + A_1*t + A_0",
        "exponential":  "y_p = A*exp(alpha*t)  [if alpha is NOT a root of char. eq.]",
        "exponential_resonance": "y_p = A*t*exp(alpha*t)  [if alpha IS a root]",
        "sinusoidal":   "y_p = A*cos(omega*t) + B*sin(omega*t)  [both terms always]",
        "sin_resonance": "y_p = t*(A*cos(omega*t) + B*sin(omega*t))  [if omega matches char. freq.]",
        "poly_exp":     "y_p = (A_n*t^n + ... + A_0) * exp(alpha*t)",
        "poly_sin":     "y_p = (A_n*t^n + ... + A_0)*cos(omega*t) + (B_n*t^n + ...)*sin(omega*t)"
    }
    return table.get(forcing_type, {k: v for k, v in table.items()})

def second_order_constant_coeff_ivp(a, b, c, f_type, f_params,
                                     y0, dy0, t_values):
    """
    Solve a*y'' + b*y' + c*y = 0 numerically using RK4 for general IVP.
    Converts to system: y1 = y, y2 = y'
      y1' = y2
      y2' = (f(t) - b*y2 - c*y1) / a
    f_type: 'zero' (homogeneous), 'const', 'sin', 'exp'
    f_params: dict with 'F' (amplitude), 'omega', 'alpha' as needed
    Returns: list of (t, y, y') values
    """
    def forcing(t):
        if f_type == 'zero':
            return 0.0
        elif f_type == 'const':
            return f_params.get('F', 0.0)
        elif f_type == 'sin':
            return f_params.get('F', 1.0) * math.sin(f_params.get('omega', 1.0) * t)
        elif f_type == 'cos':
            return f_params.get('F', 1.0) * math.cos(f_params.get('omega', 1.0) * t)
        elif f_type == 'exp':
            return f_params.get('F', 1.0) * math.exp(f_params.get('alpha', -1.0) * t)
        return 0.0

    def rhs(t, Y):
        y1, y2 = Y
        return [y2, (forcing(t) - b*y2 - c*y1) / a]

    result = [(t_values[0], y0, dy0)]
    Y = [y0, dy0]

    for i in range(1, len(t_values)):
        h = t_values[i] - t_values[i-1]
        t = t_values[i-1]
        k1 = rhs(t, Y)
        k2 = rhs(t + h/2, [Y[j] + h/2*k1[j] for j in range(2)])
        k3 = rhs(t + h/2, [Y[j] + h/2*k2[j] for j in range(2)])
        k4 = rhs(t + h, [Y[j] + h*k3[j] for j in range(2)])
        Y = [Y[j] + h/6*(k1[j]+2*k2[j]+2*k3[j]+k4[j]) for j in range(2)]
        result.append((round(t_values[i], 8), round(Y[0], 8), round(Y[1], 8)))

    return result
```

---

## Module 3 — Laplace Transforms

```python
def laplace_table():
    """
    Standard Laplace transform pairs L{f(t)} = F(s).
    All pairs valid for t >= 0.
    """
    return {
        "1":           "1/s",
        "t":           "1/s^2",
        "t^n":         "n! / s^(n+1)",
        "e^(at)":      "1/(s-a)   [s > a]",
        "t*e^(at)":    "1/(s-a)^2",
        "t^n*e^(at)":  "n!/(s-a)^(n+1)",
        "sin(bt)":     "b/(s^2+b^2)",
        "cos(bt)":     "s/(s^2+b^2)",
        "e^(at)*sin(bt)": "b/((s-a)^2+b^2)",
        "e^(at)*cos(bt)": "(s-a)/((s-a)^2+b^2)",
        "t*sin(bt)":   "2bs/(s^2+b^2)^2",
        "t*cos(bt)":   "(s^2-b^2)/(s^2+b^2)^2",
        "u(t-c)":      "e^(-cs)/s   [unit step at t=c]",
        "delta(t-c)":  "e^(-cs)   [Dirac delta at t=c]",
        "f'(t)":       "s*F(s) - f(0)   [derivative property]",
        "f''(t)":      "s^2*F(s) - s*f(0) - f'(0)   [2nd derivative]",
    }

def laplace_derivative_property(s, F_s_expr, y0, dy0=None, order=1):
    """
    Laplace transform of derivatives:
    L{y'} = s*Y(s) - y(0)
    L{y''} = s^2*Y(s) - s*y(0) - y'(0)
    Returns: transformed expression (symbolic guidance)
    """
    if order == 1:
        return {"L_y_prime": f"s*Y(s) - {y0}"}
    elif order == 2:
        return {"L_y_double_prime": f"s^2*Y(s) - {y0}*s - {dy0}"}
    return None

def inverse_laplace_partial_fractions(numerator_str, denominator_str):
    """
    Guide for partial fraction decomposition before inverse Laplace.
    Denominator root forms and their inverse transforms:
    """
    return {
        "method": "Partial Fraction Decomposition",
        "forms": {
            "A/(s-a)":             "A*e^(a*t)",
            "A/(s-a)^2":           "A*t*e^(a*t)",
            "A/(s-a)^n":           "A/(n-1)! * t^(n-1)*e^(a*t)",
            "(As+B)/(s^2+b^2)":    "A*cos(bt) + (B/b)*sin(bt)",
            "(As+B)/(s^2+2as+a^2+b^2)": "e^(-at)*[A*cos(bt) + C*sin(bt)]",
        },
        "steps": [
            "1. Factor denominator completely into linear and irreducible quadratic factors",
            "2. Write partial fraction expansion with unknown numerators",
            "3. Multiply through and match coefficients (or use Heaviside cover-up for simple poles)",
            "4. Look up each term in Laplace table",
        ],
        "tip": "Complete the square for quadratics: s^2+bs+c = (s+b/2)^2 + (c - b^2/4)"
    }
```

---

## Module 4 — Numerical Methods (Euler and RK4)

```python
def euler_method(f, t0, y0, h, n_steps):
    """
    Euler's method: y_{n+1} = y_n + h * f(t_n, y_n)
    f:       callable f(t, y) -> dy/dt
    t0, y0:  initial conditions
    h:       step size
    n_steps: number of steps
    Returns: list of (t, y) pairs
    First-order, O(h) global error — use RK4 for better accuracy.
    """
    result = [(t0, y0)]
    t, y = t0, y0
    for _ in range(n_steps):
        y = y + h * f(t, y)
        t = t + h
        result.append((round(t, 10), round(y, 10)))
    return result

def rk4_method(f, t0, y0, h, n_steps):
    """
    4th-order Runge-Kutta: O(h^4) global error, much more accurate than Euler.
    k1 = h*f(t, y)
    k2 = h*f(t+h/2, y+k1/2)
    k3 = h*f(t+h/2, y+k2/2)
    k4 = h*f(t+h, y+k3)
    y_{n+1} = y_n + (k1 + 2k2 + 2k3 + k4)/6
    f:       callable f(t, y) -> dy/dt
    Returns: list of (t, y) pairs
    """
    result = [(t0, y0)]
    t, y = t0, y0
    for _ in range(n_steps):
        k1 = h * f(t, y)
        k2 = h * f(t + h/2.0, y + k1/2.0)
        k3 = h * f(t + h/2.0, y + k2/2.0)
        k4 = h * f(t + h, y + k3)
        y = y + (k1 + 2.0*k2 + 2.0*k3 + k4) / 6.0
        t = t + h
        result.append((round(t, 10), round(y, 10)))
    return result

def rk4_system(f_list, t0, y0_list, h, n_steps):
    """
    RK4 for a system of ODEs: dy_i/dt = f_i(t, y_1, ..., y_n)
    f_list:   list of callables [f1, f2, ..., fn] where f_i(t, y_list) -> dy_i/dt
    y0_list:  list of initial conditions [y1(0), y2(0), ..., yn(0)]
    Returns: list of (t, y_1, y_2, ..., y_n) tuples
    """
    n = len(f_list)
    result = [(t0,) + tuple(y0_list)]
    t = t0
    Y = list(y0_list)

    for _ in range(n_steps):
        k1 = [h * f_list[i](t, Y) for i in range(n)]
        Y2 = [Y[i] + k1[i]/2.0 for i in range(n)]
        k2 = [h * f_list[i](t + h/2.0, Y2) for i in range(n)]
        Y3 = [Y[i] + k2[i]/2.0 for i in range(n)]
        k3 = [h * f_list[i](t + h/2.0, Y3) for i in range(n)]
        Y4 = [Y[i] + k3[i] for i in range(n)]
        k4 = [h * f_list[i](t + h, Y4) for i in range(n)]
        Y = [Y[i] + (k1[i] + 2.0*k2[i] + 2.0*k3[i] + k4[i])/6.0 for i in range(n)]
        t = t + h
        result.append((round(t, 8),) + tuple(round(y, 8) for y in Y))

    return result
```

---

## Module 5 — Systems of ODEs and Phase Plane

```python
def eigenvalue_2x2(a11, a12, a21, a22):
    """
    Eigenvalues of 2x2 matrix [[a11, a12], [a21, a22]]:
    lambda^2 - trace*lambda + det = 0
    trace = a11 + a22,  det = a11*a22 - a12*a21
    Returns: eigenvalues, eigenvector hints, phase plane type
    """
    trace = a11 + a22
    det = a11*a22 - a12*a21
    discriminant = trace**2 - 4.0*det

    if discriminant > 1e-10:
        l1 = (trace + math.sqrt(discriminant)) / 2.0
        l2 = (trace - math.sqrt(discriminant)) / 2.0
        eigenvalues = [round(l1, 8), round(l2, 8)]
    elif abs(discriminant) <= 1e-10:
        l = trace / 2.0
        eigenvalues = [round(l, 8), round(l, 8)]
    else:
        alpha = trace / 2.0
        beta = math.sqrt(-discriminant) / 2.0
        eigenvalues = [f"{round(alpha,5)} + {round(beta,5)}i",
                       f"{round(alpha,5)} - {round(beta,5)}i"]
        alpha_val = alpha
        beta_val = beta

    result = {"trace": round(trace, 6), "det": round(det, 6),
              "eigenvalues": eigenvalues}
    result.update(phase_plane_type(trace, det, discriminant))
    return result

def phase_plane_type(trace, det, discriminant=None):
    """
    Classify the equilibrium point for a linear 2D system x' = Ax.
    Based on trace and determinant of A:
    """
    if det < 0:
        return {"equilibrium_type": "saddle point", "stability": "unstable",
                "behavior": "Solutions diverge along one eigenvector, converge along other"}
    elif det == 0:
        return {"equilibrium_type": "degenerate (line of equilibria)"}
    elif discriminant is not None and discriminant > 0:
        if trace < 0:
            return {"equilibrium_type": "stable node (nodal sink)",
                    "stability": "asymptotically stable",
                    "behavior": "All trajectories approach origin as t->inf"}
        elif trace > 0:
            return {"equilibrium_type": "unstable node (nodal source)",
                    "stability": "unstable",
                    "behavior": "All trajectories diverge from origin"}
        else:
            return {"equilibrium_type": "center (star node)", "stability": "neutral"}
    elif discriminant is not None and discriminant < 0:
        if trace < 0:
            return {"equilibrium_type": "stable spiral (spiral sink)",
                    "stability": "asymptotically stable",
                    "behavior": "Spirals inward to origin; damped oscillation"}
        elif trace > 0:
            return {"equilibrium_type": "unstable spiral (spiral source)",
                    "stability": "unstable"}
        else:
            return {"equilibrium_type": "center",
                    "stability": "neutrally stable (periodic orbits)"}
    return {"equilibrium_type": "complex or degenerate; check manually"}
```

---

## Learning Resources

### Textbooks

| Author(s) | Title | Edition | ISBN |
|-----------|-------|---------|------|
| Boyce & DiPrima | *Elementary Differential Equations* | 12th ed. (2021) | 978-1-119-44377-3 |
| Zill, D.G. | *A First Course in Differential Equations* | 11th ed. (2017) | 978-1-305-96572-0 |
| Tenenbaum & Pollard | *Ordinary Differential Equations* | Dover (cheap!) | 978-0-486-64940-5 |

### Free Online Resources (All Verified High-Quality)

| Resource | URL | Notes |
|----------|-----|-------|
| **Paul's Online Math Notes — DE** | tutorial.math.lamar.edu/Classes/DE/DE.aspx | The best free ODE reference; covers everything in MATH 261 |
| **Professor Leonard ODE YouTube** | youtube.com/playlist?list=PLDesaqWTN6EQ2J4vgsN1HyBeRADEh4Cw- | Complete semester course, 1-3 hr lectures; #1 recommended |
| **MIT OCW 18.03SC** | ocw.mit.edu/courses/18-03sc-differential-equations-fall-2011/ | Scholar version; recitation videos + mathlets |
| **MIT OCW 18.03** | ocw.mit.edu/courses/18-03-differential-equations-spring-2010/ | Mattuck/Miller lectures; original course materials |
| **3Blue1Brown DE playlist** | youtube.com/playlist?list=PLZHQObOWTQDNPOjrT6KVlfJuKtYTftqH6 | Visual intuition for ODE geometry; 8 videos |
| **Khan Academy DE** | khanacademy.org/math/differential-equations | Good for targeted topic review |
| **Dr. Trefor Bazett DE** | youtube.com/playlist?list=PLHXZ9OQGMqxde-SlgmWlCmNHroIWtujBw | Modern, well-produced ODE series |
| **Paul's Cheat Sheets** | tutorial.math.lamar.edu/cheat-tables/differential-equations.aspx | Printable formula reference |
| **LibreTexts ODE** | math.libretexts.org/Bookshelves/Differential_Equations | Free open-source ODE textbook |

### WVU Courses

- **MATH 261** Applied Differential Equations — first/second order ODEs, systems, Laplace
- **MATH 441** Applied Math / PDEs — partial differential equations (graduate level)
- Related: ChBE 311/321 use ODE models; PNGE 321 uses material balance ODEs

---

## Quick Method Reference

| ODE Type | Method | Key Step |
|----------|--------|----------|
| y' = f(t)*g(y) | Separation of variables | Rearrange to g(y)^{-1} dy = f(t) dt |
| y' + P(t)*y = Q(t) | Integrating factor | mu = exp(integral P dt) |
| y' + ay = b (const) | Direct (or IF) | y = (y0 - b/a)*e^{-at} + b/a |
| ay'' + by' + cy = 0 | Characteristic equation | ar^2+br+c = 0; classify D |
| ay'' + by' + cy = g(t) | Undetermined coefficients / Var. of parameters | Guess y_p from form of g(t) |
| Any IVP | Numerical (RK4) | Convert to y' = f(t,y); step forward |
| y'' + p(x)y' + q(x)y = 0 | Laplace transform | Apply L{} to both sides; solve for Y(s) |
| System x' = Ax | Eigenvalue method | det(A - lambda*I) = 0; find eigenvectors |

---

## Output Format

```
## ODE Solution — [Type]: [Problem Description]

### ODE Classification
Type: [1st order linear / 2nd order constant-coeff / system / etc.]
Method: [separation / integrating factor / char. eq. / Laplace / RK4]

### Solution Steps
Step 1 — [Identify form]:
[write ODE in standard form]

Step 2 — [Apply method]:
[show calculation]

Step 3 — [General solution]:
y_h = [homogeneous solution]
y_p = [particular solution, if applicable]
y = y_h + y_p = [general solution]

Step 4 — [Apply IVP if given]:
y(0) = [value] => C1 = [value]
y'(0) = [value] => C2 = [value]

### Final Solution
y(t) = [explicit formula]

### Numerical Check (RK4, if analytical verification needed)
| t | y (analytical) | y (RK4) | error |
|---|---------------|---------|-------|

**Behavior:** [stable/unstable/oscillatory/growing — describe physical interpretation]
```

---

## Error Handling

| Condition | Cause | Action |
|-----------|-------|--------|
| Characteristic roots not found | Complex discriminant computation | Use eigenvalue_2x2 for systems; recheck coefficients |
| RK4 diverges | Step size too large or stiff ODE | Reduce h by factor of 10; use implicit method for stiff systems |
| Laplace gives Y(s) not in table | Partial fractions needed | Factor denominator; complete the square for quadratics |
| IVP underdetermined | Only 1 IC for 2nd order ODE | Need both y(0) and y'(0) for unique solution |

---

## Caveats

- **Numerical stability (stiff ODEs):** If the ODE has eigenvalues with vastly
  different magnitudes (e.g., fast chemical reactions with slow temperature change),
  explicit methods (Euler, RK4) require very small h. Use implicit methods or
  scipy.integrate.solve_ivp with method='Radau' or 'BDF' in practice.
- **Phase plane analysis** is for LINEAR systems only (or linearized near equilibrium).
  Nonlinear systems can have limit cycles and other features not predicted by
  linearization.
- **Undetermined coefficients vs. Variation of Parameters:** UndCoeff works only
  when g(t) is a polynomial, exponential, sine/cosine, or product of these.
  Variation of Parameters (Fogler) is more general but more tedious.
- **Laplace transform requires zero initial conditions for standard tables.**
  If y(0) != 0 or y'(0) != 0, include the extra s*y(0) and y'(0) terms from
  the derivative property.
- For PDEs (heat equation, wave equation, Laplace equation) — which appear in
  ChBE and PNGE transport problems — MATH 261 introduces the separation of
  variables technique; MATH 441 covers this in depth.
