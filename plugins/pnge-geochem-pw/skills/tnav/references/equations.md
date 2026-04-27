# Key Equations Reference — tNav Reservoir Simulation Emulator

Complete equation reference for all five modules. Variables use standard
petroleum engineering notation. All equations assume **field units** unless
otherwise noted.

---

## 1. Material Balance

### General Material Balance Equation (Schilthuis)

```
Np*[Bo + (Rp - Rs)*Bg] + Wp*Bw - Wi*Bw - Gi*Bg
  = N*[(Bo - Boi) + (Rsi - Rs)*Bg]
  + N*Boi*[(cw*Swi + cf)/(1-Swi)] * (Pi - P)
  + m*N*Boi*(Bg/Bgi - 1)
  + We
```

**Variable definitions:**

| Symbol | Definition | Unit |
|--------|-----------|------|
| N | Original oil in place (OOIP) | STB |
| Np | Cumulative oil produced | STB |
| Gp | Cumulative gas produced | scf |
| Wp | Cumulative water produced | STB |
| Wi | Cumulative water injected | STB |
| Gi | Cumulative gas injected | scf |
| Rp | Cumulative producing GOR = Gp/Np | scf/STB |
| Bo | Oil formation volume factor at P | RB/STB |
| Boi | Oil FVF at initial pressure Pi | RB/STB |
| Bg | Gas FVF at P | RB/scf |
| Bgi | Gas FVF at Pi | RB/scf |
| Bw | Water FVF | RB/STB |
| Rs | Solution GOR at P | scf/STB |
| Rsi | Solution GOR at Pi | scf/STB |
| Swi | Initial water saturation | fraction |
| cw | Water compressibility | 1/psi |
| cf | Pore compressibility | 1/psi |
| m | Gas cap ratio = GBgi/(NBoi) | dimensionless |
| We | Cumulative water influx | RB |
| Pi | Initial reservoir pressure | psia |
| P | Current reservoir pressure | psia |

### Havlena-Odeh Rearrangement

Define:
```
F  = Np*[Bo + (Rp - Rs)*Bg] + Wp*Bw        (total withdrawal, RB)
Eo = (Bo - Boi) + (Rsi - Rs)*Bg              (oil expansion, RB/STB)
Eg = Boi*(Bg/Bgi - 1)                        (gas cap expansion, RB/STB)
Efw = Boi*[(cw*Swi + cf)/(1-Swi)]*(Pi - P)  (water/pore expansion, RB/STB)
```

Then:
```
F = N*[Eo + m*Eg + Efw] + We
```

**Drive mechanism identification from F vs Et plot:**
- No gas cap, no water influx: F = N*Eo (straight line through origin)
- Gas cap drive: F = N*(Eo + m*Eg), plot F vs (Eo + m*Eg)
- Water drive: F/Eo vs Np — upward trend indicates water influx

### Aquifer Models

**Schilthuis steady-state:**
```
dWe/dt = J * (Pi - P)
We = J * integral(Pi - P) dt
```

**Fetkovich pseudo-steady-state:**
```
We = Wei * (1 - exp(-Jaq*t/Wei)) * (Pi - P_avg)
```

**Van Everdingen-Hurst (unsteady-state):**
```
We = U * SUM[delta_P_j * WD(tD - tDj)]
U = 1.119 * phi * ct * re^2 * h    (aquifer constant, RB/psi)
tD = 0.00634 * k * t / (phi * mu * ct * re^2)
```
WD(tD) from tabulated values or approximation.

---

## 2. PVT Correlations

### Pseudo-Critical Properties (Standing, 1981)

From gas specific gravity (gamma_g, air = 1.0):
```
Tpc = 168 + 325*gamma_g - 12.5*gamma_g^2        (Rankine)
Ppc = 677 + 15.0*gamma_g - 37.5*gamma_g^2        (psia)
```

Pseudo-reduced properties:
```
Tpr = T / Tpc    (T in Rankine = F + 459.67)
Ppr = P / Ppc    (P in psia)
```

**Wichert-Aziz correction** for H2S and CO2:
```
epsilon = 120*(A^0.9 - A^1.6) + 15*(B^0.5 - B^4)
Tpc' = Tpc - epsilon
Ppc' = Ppc * Tpc' / (Tpc + B*(1-B)*epsilon)
```
Where A = yH2S + yCO2, B = yH2S (mole fractions).

### Z-Factor: Dranchuk-Abou-Kassem (DAK) Correlation

The DAK correlation is an 11-coefficient fit to the Standing-Katz chart:

```
Z = 1 + (A1 + A2/Tpr + A3/Tpr^3 + A4/Tpr^4 + A5/Tpr^5) * rho_r
  + (A6 + A7/Tpr + A8/Tpr^2) * rho_r^2
  - A9*(A7/Tpr + A8/Tpr^2) * rho_r^5
  + A10*(1 + A11*rho_r^2) * (rho_r^2/Tpr^3) * exp(-A11*rho_r^2)
```

Where `rho_r = 0.27 * Ppr / (Z * Tpr)` (reduced density).

**DAK coefficients:**
```
A1  =  0.3265
A2  = -1.0700
A3  = -0.5339
A4  =  0.01569
A5  = -0.05165
A6  =  0.5475
A7  = -0.7361
A8  =  0.1844
A9  =  0.1056
A10 =  0.6134
A11 =  0.7210
```

**Solution method:** Newton-Raphson iteration on rho_r.
Define f(rho_r) = Z(rho_r) - 0.27*Ppr/(rho_r*Tpr) = 0.
Initial guess: rho_r = 0.27*Ppr/Tpr (Z=1 initial).
Converge when |f| < 1e-12 or |delta_rho_r| < 1e-10.

**Validity:** 1.0 <= Tpr <= 3.0, 0.2 <= Ppr <= 30.

### Z-Factor: Hall-Yarborough Correlation

Alternative method, also iterative:
```
F(Y) = -A*Ppr + (Y + Y^2 + Y^3 - Y^4)/(1-Y)^3
      - (14.76*t - 9.76*t^2 + 4.58*t^3)*Y^2
      + (90.7*t - 242.2*t^2 + 42.4*t^3)*Y^(2.18+2.82*t)
```
Where t = 1/Tpr, Y = reduced density.
Solve F(Y) = 0 for Y, then Z = A*Ppr/Y.
A = 0.06125*t*exp(-1.2*(1-t)^2).

### Bubble Point Pressure (Standing, 1947)

```
Pb = 18.2 * ((Rs/gamma_g)^0.83 * 10^(0.00091*T - 0.0125*API) - 1.4)
```

| Symbol | Definition | Unit |
|--------|-----------|------|
| Pb | Bubble point pressure | psia |
| Rs | Solution gas-oil ratio | scf/STB |
| gamma_g | Gas specific gravity (air=1) | — |
| T | Temperature | F |
| API | Oil API gravity | degrees |

**Validity:** 130 < Pb < 7000 psia, 100 < T < 258 F.

### Bubble Point Pressure (Vasquez-Beggs, 1980)

```
Pb = (Rs / (C1 * gamma_gs * exp(C2*API / (T+460))))^(1/C3)
```

Coefficients:
| Coeff | API <= 30 | API > 30 |
|-------|-----------|----------|
| C1 | 0.0362 | 0.0178 |
| C2 | 1.0937 | 1.1870 |
| C3 | 25.724 | 23.931 |

gamma_gs = gamma_g * (1 + 5.912e-5 * API * Tsep * log10(Psep/114.7))
Where Tsep = separator temperature (F), Psep = separator pressure (psia).

### Oil Formation Volume Factor (Standing)

Below bubble point:
```
Bo = 0.9759 + 0.000120 * (Rs*(gamma_g/gamma_o)^0.5 + 1.25*T)^1.2
```

Where gamma_o = 141.5/(API + 131.5) (oil specific gravity).

Above bubble point:
```
Bo = Bob * exp(-co * (P - Pb))
```
Where Bob = Bo at bubble point, co = undersaturated oil compressibility:
```
co = (-1433 + 5*Rs + 17.2*T - 1180*gamma_gs + 12.61*API) / (1e5 * P)
```

### Solution Gas-Oil Ratio (Standing)

```
Rs = gamma_g * (P / 18.2 * 10^(0.0125*API - 0.00091*T))^1.2048
```

Above bubble point: Rs = Rsi (constant, = Rs at Pb).

### Gas Formation Volume Factor

```
Bg = 0.02827 * Z * T / P    (RB/scf)
```

Where T in Rankine (F + 459.67), P in psia.

Or in ft3/scf:
```
Bg = 0.005035 * Z * T / P
```

### Water Formation Volume Factor (McCain)

```
Bw = (1 + dVwp) * (1 + dVwt)
dVwp = -1.0001e-2 + 1.33391e-4*T + 5.50654e-7*T^2
dVwt = -1.95301e-9*P*T - 1.72834e-13*P^2*T - 3.58922e-7*P
       - 2.25341e-10*P^2
```

### Dead Oil Viscosity (Beggs-Robinson)

```
mu_od = 10^(10^(3.0324 - 0.02023*API) * T^(-1.163)) - 1    (cp)
```

**Validity:** 16 < API < 58, 70 < T < 295 F.

### Live Oil Viscosity (Beggs-Robinson)

Below bubble point:
```
a = 10.715 * (Rs + 100)^(-0.515)
b = 5.44 * (Rs + 150)^(-0.338)
mu_o = a * mu_od^b    (cp)
```

Above bubble point:
```
mu_o = mu_ob * (P/Pb)^m
m = 2.6 * P^1.187 * exp(-11.513 - 8.98e-5*P)
```

### Gas Viscosity (Lee-Gonzalez-Eakin, 1966)

```
mu_g = K * exp(X * rho_g^Y) * 1e-4    (cp)

K = (9.4 + 0.02*M) * T^1.5 / (209 + 19*M + T)
X = 3.5 + 986/T + 0.01*M
Y = 2.4 - 0.2*X

rho_g = P*M / (Z*R*T)    (g/cm3)
```

Where M = gas molecular weight (28.97*gamma_g), T in Rankine,
R = 10.73 psia-ft3/(lbmol-R), convert rho_g to g/cm3.

**Validity:** 100 < P < 8000 psia, 100 < T < 340 F.

### Peng-Robinson Equation of State

```
P = RT/(V-b) - a*alpha/(V^2 + 2bV - b^2)

a = 0.45724 * R^2 * Tc^2 / Pc
b = 0.07780 * R * Tc / Pc
alpha = (1 + kappa*(1 - sqrt(T/Tc)))^2
kappa = 0.37464 + 1.54226*omega - 0.26992*omega^2
```

Where Tc = critical temperature, Pc = critical pressure,
omega = acentric factor.

Cubic form in Z:
```
Z^3 - (1-B)*Z^2 + (A - 3B^2 - 2B)*Z - (AB - B^2 - B^3) = 0
A = a*alpha*P / (R*T)^2
B = b*P / (R*T)
```

### SRK Equation of State

```
P = RT/(V-b) - a*alpha/(V*(V+b))

a = 0.42748 * R^2 * Tc^2 / Pc
b = 0.08664 * R * Tc / Pc
alpha = (1 + m_srk*(1 - sqrt(T/Tc)))^2
m_srk = 0.48 + 1.574*omega - 0.176*omega^2
```

---

## 3. Decline Curve Analysis (Arps)

### General Arps Equation

```
q(t) = qi / (1 + b*Di*t)^(1/b)
```

| b value | Decline Type | Rate Equation | Cumulative (Np) |
|---------|-------------|---------------|-----------------|
| b = 0 | Exponential | q = qi * exp(-Di*t) | Np = (qi - q) / Di |
| 0 < b < 1 | Hyperbolic | q = qi / (1+b*Di*t)^(1/b) | Np = qi^b/(Di*(1-b)) * (qi^(1-b) - q^(1-b)) |
| b = 1 | Harmonic | q = qi / (1+Di*t) | Np = (qi/Di) * ln(qi/q) |

| Symbol | Definition | Unit |
|--------|-----------|------|
| q(t) | Rate at time t | STB/D or Mscf/D |
| qi | Initial rate | STB/D or Mscf/D |
| Di | Initial nominal decline rate | 1/time |
| b | Decline exponent | — |
| t | Time | months or years |
| Np | Cumulative production | STB or Mscf |

**EUR (Estimated Ultimate Recovery):**
```
EUR = Np(t -> infinity) or Np at economic limit (q_econ)
```

For exponential: EUR = qi / Di (infinite time)
For hyperbolic: solve q(t_aband) = q_econ for t_aband, then compute Np(t_aband).

**Effective vs nominal decline rate:**
```
De = 1 - (1 + b*Di*dt)^(-1/b)    (effective decline per period dt)
```

For exponential: De = 1 - exp(-Di*dt).

---

## 4. Well Performance

### Vogel IPR (Below Bubble Point)

```
q/qmax = 1 - 0.2*(Pwf/Pr) - 0.8*(Pwf/Pr)^2
```

Rearranged:
```
qmax = q_test / (1 - 0.2*(Pwf_test/Pr) - 0.8*(Pwf_test/Pr)^2)
```

| Symbol | Definition | Unit |
|--------|-----------|------|
| q | Oil flow rate | STB/D |
| qmax | Absolute open flow (AOF) at Pwf=0 | STB/D |
| Pwf | Flowing bottomhole pressure | psia |
| Pr | Average reservoir pressure | psia |

### Composite IPR (Above and Below Pb)

If Pr > Pb:
```
For Pwf >= Pb:  q = J * (Pr - Pwf)           (single-phase)
For Pwf < Pb:   q = J*(Pr - Pb) + J*Pb/(1.8) * [1 - 0.2*(Pwf/Pb) - 0.8*(Pwf/Pb)^2]
```
Where J = productivity index (STB/D/psi).

### Fetkovich IPR (Gas Wells)

```
q = C * (Pr^2 - Pwf^2)^n

AOF = C * Pr^(2n)
```

C and n determined from multi-rate test (log-log plot of q vs (Pr^2 - Pwf^2)).

### Beggs and Brill Multiphase Pressure Gradient

Total pressure gradient:
```
(dP/dL)_total = (dP/dL)_elev + (dP/dL)_fric + (dP/dL)_acc

(dP/dL)_elev = rho_m * g * sin(theta) / 144
(dP/dL)_fric = f * rho_m * v_m^2 / (2 * g_c * d)
(dP/dL)_acc  = rho_m * v_m * v_sg / (g_c * P)    (usually small)
```

**Mixture properties:**
```
rho_m = rho_L * H_L + rho_g * (1 - H_L)
v_m   = v_sL + v_sg
v_sL  = q_L / A_pipe
v_sg  = q_g / A_pipe
```

Where H_L = liquid holdup (fraction of pipe occupied by liquid).

**Flow pattern determination (Beggs-Brill):**
```
lambda_L = v_sL / v_m    (no-slip liquid fraction)
NFr = v_m^2 / (g * d)    (Froude number)
```

Boundaries:
```
L1 = 316 * lambda_L^0.302
L2 = 0.0009252 * lambda_L^(-2.4684)
L3 = 0.10 * lambda_L^(-1.4516)
L4 = 0.5 * lambda_L^(-6.738)
```

| Condition | Flow Pattern |
|-----------|-------------|
| lambda_L < 0.01 and NFr < L1 | Segregated |
| lambda_L >= 0.01 and NFr < L2 | Segregated |
| lambda_L >= 0.01 and L2 <= NFr <= L3 | Transition |
| 0.01 <= lambda_L < 0.4 and L3 < NFr <= L1 | Intermittent |
| lambda_L >= 0.4 and L3 < NFr <= L4 | Intermittent |
| lambda_L < 0.4 and NFr >= L1 | Distributed |
| lambda_L >= 0.4 and NFr > L4 | Distributed |

**Liquid holdup (horizontal, then corrected for inclination):**
```
H_L(0) = a_hl * lambda_L^b_hl / NFr^c_hl
```

Coefficients by flow pattern:
| Pattern | a_hl | b_hl | c_hl |
|---------|------|------|------|
| Segregated | 0.980 | 0.4846 | 0.0868 |
| Intermittent | 0.845 | 0.5351 | 0.0173 |
| Distributed | 1.065 | 0.5824 | 0.0609 |

Inclination correction:
```
H_L(theta) = H_L(0) * psi
psi = 1 + C_bb * [sin(1.8*theta) - 0.333*sin(1.8*theta)^3]
C_bb = (1 - lambda_L) * ln(d_bb * lambda_L^e_bb * NLv^f_bb * NFr^g_bb)
```

(d_bb, e_bb, f_bb, g_bb depend on flow pattern — see Beggs & Brill tables.)

NLv = 1.938 * v_sL * (rho_L / sigma_L)^0.25 (liquid velocity number)

**Friction factor:**
```
f_n = 1 / (2*log10(NRe / (4.5223*log10(NRe) - 3.8215)))^2
f_tp = f_n * exp(S_bb)
S_bb = ln(y) / (-0.0523 + 3.182*ln(y) - 0.8725*(ln(y))^2 + 0.01853*(ln(y))^4)
y = lambda_L / H_L(theta)^2
```

### Tubing Pressure Drop Integration

Divide tubing into N segments. For each segment j from bottom to top:
```
P(j+1) = P(j) - (dP/dL)_j * dL_j
```

Recalculate fluid properties at each segment's average pressure and temperature.
Temperature profile (linear):
```
T(L) = T_bh - (T_bh - T_wh) * L / L_total
```

---

## 5. Petrophysics and Geostatistics

### Archie's Equation

```
Sw^n = a * Rw / (phi^m * Rt)

Sw = (a * Rw / (phi^m * Rt))^(1/n)
```

| Symbol | Definition | Unit | Typical Range |
|--------|-----------|------|---------------|
| Sw | Water saturation | fraction | 0-1 |
| phi | Porosity | fraction | 0.05-0.35 |
| Rt | True formation resistivity | ohm-m | 1-1000 |
| Rw | Formation water resistivity | ohm-m | 0.01-1 |
| a | Tortuosity factor | — | 0.62-1.0 |
| m | Cementation exponent | — | 1.8-2.5 |
| n | Saturation exponent | — | 1.8-2.2 |

**Hydrocarbon saturation:**
```
So = 1 - Sw       (oil zone, no free gas)
Sg = 1 - Sw - So  (three-phase)
```

### Kozeny-Carman Permeability

```
k = (phi^3 * d_grain^2) / (72 * tau^2 * (1-phi)^2)    (darcy)
```

Simplified (Timur, 1968):
```
k = 8581 * phi^4.4 / Swi^2    (md)
```

### Empirical Perm-Poro Transform

```
log10(k) = a + b * phi

k = 10^(a + b*phi)    (md)
```

Typical values: a = -1 to +1, b = 10 to 30 (formation-specific).
Fit from core data using least-squares regression.

### Variogram Models

**Experimental variogram:**
```
gamma(h) = (1/2N(h)) * SUM[(Z(xi) - Z(xi + h))^2]
```
Where N(h) = number of pairs at lag distance h.

**Spherical model:**
```
gamma(h) = C0 + C * [1.5*(h/a) - 0.5*(h/a)^3]    for 0 < h <= a
gamma(h) = C0 + C                                   for h > a
gamma(0) = 0
```

**Exponential model:**
```
gamma(h) = C0 + C * [1 - exp(-3*h/a)]
```

**Gaussian model:**
```
gamma(h) = C0 + C * [1 - exp(-3*(h/a)^2)]
```

| Symbol | Definition |
|--------|-----------|
| C0 | Nugget (discontinuity at origin) |
| C | Sill - Nugget (structured variance) |
| C0 + C | Sill (total variance at large h) |
| a | Range (distance at which sill is reached) |
| h | Lag distance |

### Simple Kriging

Estimate Z*(x0) at unsampled location x0:
```
Z*(x0) = mu + SUM[lambda_i * (Z(xi) - mu)]
```

Where mu = known (or assumed) mean, lambda_i = kriging weights.

**Kriging system (simple):**
```
[C(x1,x1) ... C(x1,xn)] [lambda_1]   [C(x1,x0)]
[  ...     ...   ...   ] [  ...   ] = [  ...    ]
[C(xn,x1) ... C(xn,xn)] [lambda_n]   [C(xn,x0)]
```

Where C(xi,xj) = covariance = (C0+C) - gamma(|xi-xj|).

**Kriging variance:**
```
sigma_SK^2 = C(x0,x0) - SUM[lambda_i * C(xi,x0)]
```

### Ordinary Kriging

Does not require known mean:
```
Z*(x0) = SUM[lambda_i * Z(xi)]    with SUM[lambda_i] = 1
```

**Kriging system (ordinary):**
```
[C(x1,x1) ... C(x1,xn) 1] [lambda_1]   [C(x1,x0)]
[  ...     ...   ...    .] [  ...   ] = [  ...    ]
[C(xn,x1) ... C(xn,xn) 1] [lambda_n]   [C(xn,x0)]
[   1      ...    1     0] [  mu_L  ]   [    1    ]
```

Where mu_L = Lagrange multiplier.

**Kriging variance (ordinary):**
```
sigma_OK^2 = C(x0,x0) - SUM[lambda_i * C(xi,x0)] - mu_L
```

### Sequential Gaussian Simulation (SGS)

Algorithm:
1. Transform all data Z(xi) to standard normal Y(xi) using quantile transform
2. Define random visitation path over all grid nodes
3. For each node x0 in the path:
   a. Collect nearby conditioning data (original + previously simulated)
   b. Simple krige to get mean (mu_SK) and variance (sigma_SK^2)
   c. Draw Y*(x0) ~ N(mu_SK, sigma_SK^2)
   d. Add Y*(x0) to conditioning data set
4. Back-transform all Y* to original units using inverse quantile transform
5. Repeat steps 2-4 for multiple realizations

**Key property:** Each realization honors:
- The data values at known locations
- The histogram of the original data
- The spatial correlation (variogram) model
