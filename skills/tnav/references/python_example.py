#!/usr/bin/env python3
"""
tNavigator Reservoir Simulation Emulator — Python Reference Implementations

Educational implementations of key petroleum engineering calculations.
Uses ONLY Python standard library (math, statistics, random, json, csv).

All correlations use FIELD UNITS unless otherwise noted:
  - Pressure: psia
  - Temperature: Fahrenheit (F) or Rankine (R = F + 459.67)
  - Rate: STB/D (oil), Mscf/D (gas)
  - Length: ft
  - Permeability: md
  - Viscosity: cp
  - FVF: RB/STB (oil), RB/scf (gas)
  - GOR: scf/STB

Author: PNGE Research Plugin (educational use)
"""

import math
import random
import json
import csv
from typing import List, Tuple, Dict, Optional

# =============================================================================
# MODULE 2 — PVT DESIGNER
# =============================================================================

# ---- Pseudo-critical properties (Standing) ----

def pseudo_critical_props(gamma_g: float) -> Tuple[float, float]:
    """
    Calculate pseudo-critical temperature and pressure from gas gravity.

    Args:
        gamma_g: Gas specific gravity (air = 1.0)

    Returns:
        (Tpc, Ppc) in (Rankine, psia)
    """
    Tpc = 168.0 + 325.0 * gamma_g - 12.5 * gamma_g ** 2  # Rankine
    Ppc = 677.0 + 15.0 * gamma_g - 37.5 * gamma_g ** 2   # psia
    return Tpc, Ppc


def pseudo_reduced(T_F: float, P_psia: float, gamma_g: float) -> Tuple[float, float]:
    """
    Calculate pseudo-reduced temperature and pressure.

    Args:
        T_F: Temperature in Fahrenheit
        P_psia: Pressure in psia
        gamma_g: Gas specific gravity (air = 1.0)

    Returns:
        (Tpr, Ppr) dimensionless
    """
    Tpc, Ppc = pseudo_critical_props(gamma_g)
    T_R = T_F + 459.67  # Convert F to Rankine
    Tpr = T_R / Tpc
    Ppr = P_psia / Ppc
    return Tpr, Ppr


# ---- Z-Factor: Dranchuk-Abou-Kassem (DAK) Correlation ----

def z_factor_DAK(Tpr: float, Ppr: float, tol: float = 1e-12,
                 max_iter: int = 200) -> float:
    """
    Calculate gas compressibility factor using the DAK correlation.

    Uses Newton-Raphson iteration to solve for reduced density (rho_r),
    then computes Z from rho_r.

    Args:
        Tpr: Pseudo-reduced temperature (dimensionless)
        Ppr: Pseudo-reduced pressure (dimensionless)
        tol: Convergence tolerance
        max_iter: Maximum iterations

    Returns:
        Z-factor (dimensionless)

    Raises:
        RuntimeError: If iteration does not converge
    """
    # DAK coefficients
    A1 = 0.3265
    A2 = -1.0700
    A3 = -0.5339
    A4 = 0.01569
    A5 = -0.05165
    A6 = 0.5475
    A7 = -0.7361
    A8 = 0.1844
    A9 = 0.1056
    A10 = 0.6134
    A11 = 0.7210

    # Initial guess for reduced density: rho_r = 0.27 * Ppr / Tpr (Z=1)
    rho_r = 0.27 * Ppr / Tpr

    for iteration in range(max_iter):
        # Z as a function of rho_r
        T2 = Tpr * Tpr
        T3 = T2 * Tpr
        T4 = T3 * Tpr
        T5 = T4 * Tpr

        r2 = rho_r * rho_r
        r5 = r2 * r2 * rho_r

        exp_term = math.exp(-A11 * r2)

        Z = (1.0
             + (A1 + A2 / Tpr + A3 / T3 + A4 / T4 + A5 / T5) * rho_r
             + (A6 + A7 / Tpr + A8 / T2) * r2
             - A9 * (A7 / Tpr + A8 / T2) * r5
             + A10 * (1.0 + A11 * r2) * (r2 / T3) * exp_term)

        # Residual: f = Z - 0.27*Ppr/(rho_r*Tpr)
        f = Z - 0.27 * Ppr / (rho_r * Tpr)

        # Derivative df/d(rho_r) for Newton-Raphson
        dZ = (A1 + A2 / Tpr + A3 / T3 + A4 / T4 + A5 / T5
              + 2.0 * (A6 + A7 / Tpr + A8 / T2) * rho_r
              - 5.0 * A9 * (A7 / Tpr + A8 / T2) * rho_r ** 4
              + (A10 / T3) * exp_term
              * (2.0 * rho_r + 2.0 * A11 * rho_r * r2
                 - 2.0 * A11 * rho_r * (1.0 + A11 * r2) * r2
                 + 2.0 * A11 * r2 * rho_r))

        # Simplified derivative (recomputed cleanly)
        dZ_drho = (A1 + A2 / Tpr + A3 / T3 + A4 / T4 + A5 / T5
                   + 2.0 * rho_r * (A6 + A7 / Tpr + A8 / T2)
                   - 5.0 * A9 * (A7 / Tpr + A8 / T2) * rho_r ** 4
                   + (2.0 * A10 * rho_r / T3) * exp_term
                   * (1.0 + 2.0 * A11 * r2 - A11 * r2 * (1.0 + A11 * r2)))

        df = dZ_drho + 0.27 * Ppr / (r2 * Tpr)

        # Newton step
        delta = f / df
        rho_r -= delta

        # Keep rho_r positive
        if rho_r <= 0:
            rho_r = 0.01

        if abs(f) < tol:
            return 0.27 * Ppr / (rho_r * Tpr)

    # Return best estimate even if not fully converged
    return 0.27 * Ppr / (rho_r * Tpr)


def z_factor(T_F: float, P_psia: float, gamma_g: float) -> float:
    """
    Convenience wrapper: Z-factor from T(F), P(psia), and gas gravity.

    Args:
        T_F: Temperature in Fahrenheit
        P_psia: Pressure in psia
        gamma_g: Gas specific gravity (air = 1.0)

    Returns:
        Z-factor (dimensionless)
    """
    Tpr, Ppr = pseudo_reduced(T_F, P_psia, gamma_g)
    return z_factor_DAK(Tpr, Ppr)


# ---- Formation Volume Factors ----

def Bo_standing(Rs: float, gamma_g: float, gamma_o: float,
                T_F: float) -> float:
    """
    Oil formation volume factor using Standing correlation (below Pb).

    Args:
        Rs: Solution gas-oil ratio (scf/STB)
        gamma_g: Gas specific gravity (air = 1.0)
        gamma_o: Oil specific gravity (water = 1.0)
        T_F: Temperature (F)

    Returns:
        Bo in RB/STB
    """
    F_term = Rs * math.sqrt(gamma_g / gamma_o) + 1.25 * T_F
    Bo = 0.9759 + 0.000120 * F_term ** 1.2
    return Bo


def Bg_calc(Z: float, T_F: float, P_psia: float) -> float:
    """
    Gas formation volume factor.

    Args:
        Z: Gas compressibility factor
        T_F: Temperature (F)
        P_psia: Pressure (psia)

    Returns:
        Bg in RB/scf
    """
    T_R = T_F + 459.67
    return 0.02827 * Z * T_R / P_psia


# ---- Bubble Point Pressure ----

def Pb_standing(Rs: float, gamma_g: float, T_F: float,
                API: float) -> float:
    """
    Bubble point pressure using Standing correlation.

    Args:
        Rs: Solution GOR at bubble point (scf/STB)
        gamma_g: Gas specific gravity (air = 1.0)
        T_F: Temperature (F)
        API: Oil API gravity (degrees)

    Returns:
        Pb in psia
    """
    exponent = 0.00091 * T_F - 0.0125 * API
    Pb = 18.2 * ((Rs / gamma_g) ** 0.83 * 10 ** exponent - 1.4)
    return Pb


# ---- Solution GOR ----

def Rs_standing(P_psia: float, gamma_g: float, T_F: float,
                API: float) -> float:
    """
    Solution gas-oil ratio using Standing correlation.

    Args:
        P_psia: Pressure (psia)
        gamma_g: Gas specific gravity (air = 1.0)
        T_F: Temperature (F)
        API: Oil API gravity (degrees)

    Returns:
        Rs in scf/STB
    """
    exponent = 0.0125 * API - 0.00091 * T_F
    Rs = gamma_g * (P_psia / 18.2 * 10 ** exponent) ** 1.2048
    return Rs


# ---- Oil Viscosity ----

def dead_oil_viscosity_beggs_robinson(API: float, T_F: float) -> float:
    """
    Dead oil viscosity using Beggs-Robinson correlation.

    Args:
        API: Oil API gravity (degrees)
        T_F: Temperature (F)

    Returns:
        mu_od in cp
    """
    x = 10 ** (3.0324 - 0.02023 * API)
    mu_od = 10 ** (x * T_F ** (-1.163)) - 1.0
    return mu_od


def live_oil_viscosity_beggs_robinson(mu_od: float, Rs: float) -> float:
    """
    Live (saturated) oil viscosity using Beggs-Robinson correlation.

    Args:
        mu_od: Dead oil viscosity (cp)
        Rs: Solution GOR (scf/STB)

    Returns:
        mu_o in cp
    """
    a = 10.715 * (Rs + 100.0) ** (-0.515)
    b = 5.44 * (Rs + 150.0) ** (-0.338)
    mu_o = a * mu_od ** b
    return mu_o


# ---- Gas Viscosity ----

def gas_viscosity_LGE(T_F: float, P_psia: float, Z: float,
                      gamma_g: float) -> float:
    """
    Gas viscosity using Lee-Gonzalez-Eakin correlation.

    Args:
        T_F: Temperature (F)
        P_psia: Pressure (psia)
        Z: Gas compressibility factor
        gamma_g: Gas specific gravity (air = 1.0)

    Returns:
        mu_g in cp
    """
    T_R = T_F + 459.67
    M = 28.97 * gamma_g  # Gas molecular weight

    # Gas density in g/cm3
    # rho_g = P*M / (Z*R*T) where R = 10.73 psia*ft3/(lbmol*R)
    # Convert lb/ft3 to g/cm3: multiply by 0.016018
    rho_g_lb_ft3 = P_psia * M / (Z * 10.73 * T_R)
    rho_g = rho_g_lb_ft3 * 0.016018  # g/cm3

    K = (9.4 + 0.02 * M) * T_R ** 1.5 / (209.0 + 19.0 * M + T_R)
    X = 3.5 + 986.0 / T_R + 0.01 * M
    Y = 2.4 - 0.2 * X

    mu_g = K * math.exp(X * rho_g ** Y) * 1e-4  # cp
    return mu_g


# ---- Comprehensive PVT Report ----

def pvt_report(T_F: float, P_psia: float, API: float, gamma_g: float):
    """
    Generate a full PVT report at given conditions.

    Prints a formatted table of all PVT properties.
    """
    gamma_o = 141.5 / (API + 131.5)

    # Z-factor
    Z = z_factor(T_F, P_psia, gamma_g)

    # Solution GOR
    Rs = Rs_standing(P_psia, gamma_g, T_F, API)

    # Bubble point
    Pb = Pb_standing(Rs, gamma_g, T_F, API)

    # Oil FVF
    Bo = Bo_standing(Rs, gamma_g, gamma_o, T_F)

    # Gas FVF
    Bg = Bg_calc(Z, T_F, P_psia)

    # Oil viscosity
    mu_od = dead_oil_viscosity_beggs_robinson(API, T_F)
    mu_o = live_oil_viscosity_beggs_robinson(mu_od, Rs)

    # Gas viscosity
    mu_g = gas_viscosity_LGE(T_F, P_psia, Z, gamma_g)

    print(f"## PVT Properties at P = {P_psia} psia, T = {T_F} F")
    print(f"##   API = {API}, gamma_g = {gamma_g}")
    print()
    print(f"{'Property':<30} {'Value':>12} {'Unit':<10}")
    print("-" * 55)
    print(f"{'Z-factor':<30} {Z:>12.4f} {'--':<10}")
    print(f"{'Bubble point (Pb)':<30} {Pb:>12.1f} {'psia':<10}")
    print(f"{'Solution GOR (Rs)':<30} {Rs:>12.1f} {'scf/STB':<10}")
    print(f"{'Oil FVF (Bo)':<30} {Bo:>12.4f} {'RB/STB':<10}")
    print(f"{'Gas FVF (Bg)':<30} {Bg:>12.6f} {'RB/scf':<10}")
    print(f"{'Dead oil viscosity':<30} {mu_od:>12.3f} {'cp':<10}")
    print(f"{'Live oil viscosity':<30} {mu_o:>12.3f} {'cp':<10}")
    print(f"{'Gas viscosity':<30} {mu_g:>12.5f} {'cp':<10}")
    print(f"{'Oil specific gravity':<30} {gamma_o:>12.4f} {'--':<10}")
    print()
    if P_psia > Pb:
        print("Note: Pressure is ABOVE bubble point — oil is undersaturated.")
    else:
        print("Note: Pressure is BELOW bubble point — two-phase flow expected.")


# =============================================================================
# MODULE 4 — WELL PERFORMANCE
# =============================================================================

# ---- Vogel IPR ----

def vogel_ipr(Pr: float, Pwf_test: float, q_test: float,
              n_points: int = 20) -> List[Tuple[float, float]]:
    """
    Generate Vogel IPR curve for a two-phase oil well below bubble point.

    Args:
        Pr: Average reservoir pressure (psia)
        Pwf_test: Test flowing BHP (psia)
        q_test: Test oil rate (STB/D)
        n_points: Number of points on the curve

    Returns:
        List of (Pwf, q) tuples from Pwf=Pr down to Pwf=0
    """
    # Calculate qmax (AOF) from the test point
    ratio = Pwf_test / Pr
    qmax = q_test / (1.0 - 0.2 * ratio - 0.8 * ratio ** 2)

    curve = []
    for i in range(n_points + 1):
        Pwf = Pr * (1.0 - i / n_points)
        r = Pwf / Pr
        q = qmax * (1.0 - 0.2 * r - 0.8 * r ** 2)
        curve.append((Pwf, q))

    return curve


def print_ipr_curve(Pr: float, Pwf_test: float, q_test: float):
    """Print a formatted Vogel IPR table."""
    curve = vogel_ipr(Pr, Pwf_test, q_test)
    ratio = Pwf_test / Pr
    qmax = q_test / (1.0 - 0.2 * ratio - 0.8 * ratio ** 2)

    print(f"## Vogel IPR Curve")
    print(f"## Pr = {Pr} psia, qmax (AOF) = {qmax:.0f} STB/D")
    print()
    print(f"{'Pwf (psia)':>12} {'q (STB/D)':>12}")
    print("-" * 26)
    for Pwf, q in curve:
        print(f"{Pwf:>12.0f} {q:>12.0f}")


# ---- Beggs and Brill Pressure Drop (Simplified) ----

def beggs_brill_dp_segment(
    P_psia: float, T_F: float,
    q_oil_STBD: float, q_gas_MscfD: float, q_water_STBD: float,
    d_inches: float, dL_ft: float, angle_deg: float,
    API: float, gamma_g: float, gamma_w: float = 1.07
) -> float:
    """
    Calculate pressure drop over one tubing segment using simplified
    Beggs and Brill correlation.

    This is a simplified version suitable for educational purposes.
    It computes elevation and friction terms but uses approximate
    holdup and friction factor calculations.

    Args:
        P_psia: Pressure at segment inlet (psia)
        T_F: Temperature at segment midpoint (F)
        q_oil_STBD: Oil rate (STB/D)
        q_gas_MscfD: Gas rate (Mscf/D)
        q_water_STBD: Water rate (STB/D)
        d_inches: Tubing inner diameter (inches)
        dL_ft: Segment length (ft)
        angle_deg: Angle from horizontal (90 = vertical)
        API: Oil API gravity
        gamma_g: Gas specific gravity
        gamma_w: Water specific gravity (default 1.07)

    Returns:
        Pressure drop over segment (psi), positive = pressure loss going up
    """
    gamma_o = 141.5 / (API + 131.5)
    d_ft = d_inches / 12.0
    A_ft2 = math.pi * d_ft ** 2 / 4.0  # Cross-sectional area

    # PVT at segment conditions
    Rs = Rs_standing(P_psia, gamma_g, T_F, API)
    Bo = Bo_standing(Rs, gamma_g, gamma_o, T_F)
    Z = z_factor(T_F, P_psia, gamma_g)
    Bg = Bg_calc(Z, T_F, P_psia)

    # In-situ volumetric flow rates (ft3/s)
    q_oil_insitu = q_oil_STBD * Bo * 5.615 / 86400.0        # ft3/s
    q_water_insitu = q_water_STBD * 1.0 * 5.615 / 86400.0   # ft3/s (Bw ~ 1)
    q_gas_free = (q_gas_MscfD * 1000.0 - q_oil_STBD * Rs)   # free gas scf/D
    if q_gas_free < 0:
        q_gas_free = 0.0
    q_gas_insitu = q_gas_free * Bg * 5.615 / 86400.0         # ft3/s

    q_liquid = q_oil_insitu + q_water_insitu
    q_total = q_liquid + q_gas_insitu

    if q_total < 1e-10:
        return 0.0

    # Superficial velocities (ft/s)
    v_sL = q_liquid / A_ft2
    v_sg = q_gas_insitu / A_ft2
    v_m = v_sL + v_sg

    if v_m < 1e-10:
        return 0.0

    # No-slip liquid fraction
    lambda_L = v_sL / v_m if v_m > 0 else 1.0

    # Liquid density (lb/ft3)
    f_oil = q_oil_insitu / q_liquid if q_liquid > 0 else 1.0
    rho_oil = (gamma_o * 62.4 + Rs * gamma_g * 0.0764) / Bo  # approximate
    rho_water = gamma_w * 62.4
    rho_L = f_oil * rho_oil + (1.0 - f_oil) * rho_water

    # Gas density (lb/ft3)
    T_R = T_F + 459.67
    M_gas = 28.97 * gamma_g
    rho_g = P_psia * M_gas / (Z * 10.73 * T_R)  # lb/ft3

    # Simplified liquid holdup estimate
    # Use Beggs-Brill intermittent flow pattern coefficients as default
    NFr = v_m ** 2 / (32.174 * d_ft) if d_ft > 0 else 1.0
    H_L_horizontal = 0.845 * lambda_L ** 0.5351 / max(NFr, 0.001) ** 0.0173
    H_L_horizontal = max(min(H_L_horizontal, 1.0), lambda_L)

    # Inclination correction (simplified)
    theta_rad = math.radians(angle_deg)
    sin_theta = math.sin(theta_rad)
    # Simplified psi correction — for vertical upflow, holdup increases
    C_corr = max(0.0, (1.0 - lambda_L) * 0.3)
    psi = 1.0 + C_corr * (sin_theta - 0.333 * sin_theta ** 3)
    H_L = H_L_horizontal * psi
    H_L = max(min(H_L, 1.0), 0.0)

    # Mixture density
    rho_m = rho_L * H_L + rho_g * (1.0 - H_L)

    # Friction factor (Moody, simplified)
    rho_ns = rho_L * lambda_L + rho_g * (1.0 - lambda_L)
    mu_L = 1.0  # cp, approximate
    mu_ns = mu_L * lambda_L + 0.015 * (1.0 - lambda_L)  # cp
    NRe = 1488.0 * rho_ns * v_m * d_ft / mu_ns if mu_ns > 0 else 1e6
    NRe = max(NRe, 1.0)

    # Colebrook approximation for friction factor
    epsilon = 0.0006  # relative roughness for new tubing
    f_factor = (1.0 / (-2.0 * math.log10(
        epsilon / 3.7 + 2.51 / (NRe * max(0.01, math.sqrt(0.02)))
    ))) ** 2
    f_factor = max(f_factor, 0.005)
    f_factor = min(f_factor, 0.1)

    # Pressure gradient components (psi/ft)
    g = 32.174  # ft/s2
    gc = 32.174  # lbm*ft/(lbf*s2)

    dp_elev = rho_m * sin_theta / 144.0          # psi/ft
    dp_fric = f_factor * rho_ns * v_m ** 2 / (2.0 * gc * d_ft * 144.0)  # psi/ft

    # Acceleration term (usually small, included for completeness)
    dp_acc = 0.0
    if P_psia > 0:
        dp_acc = rho_m * v_m * v_sg / (gc * P_psia * 144.0)

    dp_total = (dp_elev + dp_fric) / (1.0 - dp_acc) * dL_ft

    return dp_total


def tubing_pressure_drop(
    Pwh_psia: float, T_wh_F: float, T_bh_F: float,
    depth_ft: float, q_oil_STBD: float, GOR_scfSTB: float,
    WC: float, d_inches: float, API: float, gamma_g: float,
    n_segments: int = 50
) -> float:
    """
    Calculate bottomhole pressure from wellhead pressure by marching
    down the tubing (top to bottom).

    Args:
        Pwh_psia: Wellhead pressure (psia)
        T_wh_F: Wellhead temperature (F)
        T_bh_F: Bottomhole temperature (F)
        depth_ft: True vertical depth (ft)
        q_oil_STBD: Oil rate (STB/D)
        GOR_scfSTB: Producing gas-oil ratio (scf/STB)
        WC: Water cut (fraction, 0-1)
        d_inches: Tubing ID (inches)
        API: Oil API gravity
        gamma_g: Gas specific gravity
        n_segments: Number of segments for numerical integration

    Returns:
        Pwf (bottomhole flowing pressure) in psia
    """
    dL = depth_ft / n_segments
    P = Pwh_psia

    q_water = q_oil_STBD * WC / (1.0 - WC) if WC < 1.0 else 0.0
    q_gas = q_oil_STBD * GOR_scfSTB / 1000.0  # Mscf/D

    for i in range(n_segments):
        # Linear temperature profile
        frac = (i + 0.5) / n_segments
        T_seg = T_wh_F + frac * (T_bh_F - T_wh_F)

        dp = beggs_brill_dp_segment(
            P_psia=P, T_F=T_seg,
            q_oil_STBD=q_oil_STBD, q_gas_MscfD=q_gas,
            q_water_STBD=q_water,
            d_inches=d_inches, dL_ft=dL, angle_deg=90.0,
            API=API, gamma_g=gamma_g
        )
        P += dp  # Pressure increases going down

    return P


def nodal_analysis(
    Pr: float, Pwf_test: float, q_test: float,
    Pwh_psia: float, T_wh_F: float, T_bh_F: float,
    depth_ft: float, GOR_scfSTB: float, WC: float,
    d_inches: float, API: float, gamma_g: float,
    n_rate_points: int = 15
) -> Tuple[float, float]:
    """
    Find operating point by intersecting IPR and VFP (tubing) curves.

    Args:
        Pr: Reservoir pressure (psia)
        Pwf_test: Test point BHP (psia)
        q_test: Test point rate (STB/D)
        Pwh_psia: Wellhead pressure (psia)
        T_wh_F, T_bh_F: Wellhead and bottomhole temperature (F)
        depth_ft: TVD (ft)
        GOR_scfSTB: Producing GOR (scf/STB)
        WC: Water cut (fraction)
        d_inches: Tubing ID (inches)
        API: Oil API gravity
        gamma_g: Gas specific gravity
        n_rate_points: Number of rate points for curve generation

    Returns:
        (q_operating, Pwf_operating) — the operating point
    """
    # Generate IPR curve
    ipr = vogel_ipr(Pr, Pwf_test, q_test, n_points=n_rate_points)
    ratio = Pwf_test / Pr
    qmax = q_test / (1.0 - 0.2 * ratio - 0.8 * ratio ** 2)

    # Generate VFP curve at same rates
    # VFP: for a given q, compute Pwf required at bottom of tubing
    # to deliver that q at wellhead pressure Pwh
    best_diff = float('inf')
    best_q = 0.0
    best_Pwf = 0.0

    for i in range(1, n_rate_points + 1):
        q = qmax * i / n_rate_points
        if q < 10:
            continue

        # IPR: Pwf at this rate
        # q/qmax = 1 - 0.2*(Pwf/Pr) - 0.8*(Pwf/Pr)^2
        # Solve quadratic: 0.8*r^2 + 0.2*r + (q/qmax - 1) = 0
        discriminant = 0.04 + 3.2 * (1.0 - q / qmax)
        if discriminant < 0:
            continue
        r = (-0.2 + math.sqrt(discriminant)) / 1.6
        Pwf_ipr = r * Pr

        # VFP: Pwf from tubing calculation
        Pwf_vfp = tubing_pressure_drop(
            Pwh_psia, T_wh_F, T_bh_F, depth_ft,
            q, GOR_scfSTB, WC, d_inches, API, gamma_g,
            n_segments=30
        )

        diff = abs(Pwf_ipr - Pwf_vfp)
        if diff < best_diff:
            best_diff = diff
            best_q = q
            best_Pwf = (Pwf_ipr + Pwf_vfp) / 2.0

    return best_q, best_Pwf


# =============================================================================
# MODULE 1 — DECLINE CURVE ANALYSIS (Arps)
# =============================================================================

def arps_exponential(qi: float, Di: float, t: float) -> float:
    """
    Exponential decline rate.

    Args:
        qi: Initial rate (STB/D)
        Di: Nominal decline rate (1/time)
        t: Time (same unit as Di)

    Returns:
        Rate at time t
    """
    return qi * math.exp(-Di * t)


def arps_hyperbolic(qi: float, Di: float, b: float, t: float) -> float:
    """
    Hyperbolic decline rate.

    Args:
        qi: Initial rate (STB/D)
        Di: Initial nominal decline rate (1/time)
        b: Decline exponent (0 < b < 1)
        t: Time

    Returns:
        Rate at time t
    """
    return qi / (1.0 + b * Di * t) ** (1.0 / b)


def arps_harmonic(qi: float, Di: float, t: float) -> float:
    """
    Harmonic decline rate (b=1 case).

    Args:
        qi: Initial rate (STB/D)
        Di: Nominal decline rate (1/time)
        t: Time

    Returns:
        Rate at time t
    """
    return qi / (1.0 + Di * t)


def arps_cumulative(qi: float, Di: float, b: float, t: float) -> float:
    """
    Cumulative production for general Arps decline.

    Args:
        qi: Initial rate (STB/D or Mscf/D)
        Di: Initial decline rate (1/month or 1/year)
        b: Decline exponent
        t: Time (matching Di units)

    Returns:
        Cumulative production (rate_unit * time_unit)
    """
    if abs(b) < 1e-6:
        # Exponential
        return (qi - qi * math.exp(-Di * t)) / Di
    elif abs(b - 1.0) < 1e-6:
        # Harmonic
        return qi / Di * math.log(1.0 + Di * t)
    else:
        # Hyperbolic
        q_t = arps_hyperbolic(qi, Di, b, t)
        return qi ** b / (Di * (1.0 - b)) * (qi ** (1.0 - b) - q_t ** (1.0 - b))


def fit_exponential_decline(times: List[float],
                            rates: List[float]) -> Tuple[float, float]:
    """
    Fit exponential decline to production data using least-squares
    on log(q) vs t.

    Args:
        times: List of time values
        rates: List of corresponding rate values (must be > 0)

    Returns:
        (qi, Di) — initial rate and nominal decline rate
    """
    n = len(times)
    if n < 2:
        raise ValueError("Need at least 2 data points")

    # Fit ln(q) = ln(qi) - Di*t  (linear regression)
    log_rates = [math.log(r) for r in rates if r > 0]
    valid_times = [t for t, r in zip(times, rates) if r > 0]
    n = len(log_rates)

    sum_t = sum(valid_times)
    sum_lnq = sum(log_rates)
    sum_t2 = sum(t ** 2 for t in valid_times)
    sum_t_lnq = sum(t * lnq for t, lnq in zip(valid_times, log_rates))

    # Linear regression: lnq = a + b*t, where a=ln(qi), b=-Di
    denom = n * sum_t2 - sum_t ** 2
    if abs(denom) < 1e-20:
        raise ValueError("Degenerate data — all times identical")

    slope = (n * sum_t_lnq - sum_t * sum_lnq) / denom
    intercept = (sum_lnq - slope * sum_t) / n

    qi = math.exp(intercept)
    Di = -slope  # slope is negative for decline

    return qi, Di


def decline_forecast(qi: float, Di: float, b: float,
                     t_max: float, dt: float,
                     q_econ: float = 10.0) -> List[Dict]:
    """
    Generate a decline forecast table.

    Args:
        qi: Initial rate (STB/D)
        Di: Decline rate (1/month)
        b: Decline exponent
        t_max: Maximum forecast time (months)
        dt: Time step (months)
        q_econ: Economic limit rate (STB/D)

    Returns:
        List of dicts with keys: time, rate, cumulative
    """
    results = []
    t = 0.0
    while t <= t_max:
        if abs(b) < 1e-6:
            q = arps_exponential(qi, Di, t)
        elif abs(b - 1.0) < 1e-6:
            q = arps_harmonic(qi, Di, t)
        else:
            q = arps_hyperbolic(qi, Di, b, t)

        Np = arps_cumulative(qi, Di, b, t)

        if q < q_econ:
            # Interpolate to find exact economic limit time
            results.append({
                "time_months": round(t, 1),
                "rate_STBD": round(q, 1),
                "cumulative_MSTB": round(Np * 30.4375 / 1000.0, 1),
                "note": "Below economic limit"
            })
            break

        results.append({
            "time_months": round(t, 1),
            "rate_STBD": round(q, 1),
            "cumulative_MSTB": round(Np * 30.4375 / 1000.0, 1),
            "note": ""
        })
        t += dt

    return results


# =============================================================================
# MODULE 1 — MATERIAL BALANCE
# =============================================================================

def material_balance_oil(
    N: float,
    pressures: List[float],
    Np_list: List[float],
    Bo_list: List[float],
    Rs_list: List[float],
    Bg_list: List[float],
    Rp_list: List[float],
    Boi: float, Rsi: float, Bgi: float,
    Swi: float = 0.25, cw: float = 3e-6, cf: float = 5e-6,
    Pi: float = 4000.0
) -> List[Dict]:
    """
    Havlena-Odeh material balance calculation for oil reservoir.

    Computes F and Et at each pressure step for drive mechanism analysis.

    Args:
        N: OOIP estimate (STB) — used only for comparison
        pressures: List of reservoir pressures (psia)
        Np_list: Cumulative oil produced at each pressure (STB)
        Bo_list: Oil FVF at each pressure (RB/STB)
        Rs_list: Solution GOR at each pressure (scf/STB)
        Bg_list: Gas FVF at each pressure (RB/scf)
        Rp_list: Cumulative producing GOR at each pressure (scf/STB)
        Boi: Initial oil FVF (RB/STB)
        Rsi: Initial solution GOR (scf/STB)
        Bgi: Initial gas FVF (RB/scf)
        Swi: Initial water saturation (fraction)
        cw: Water compressibility (1/psi)
        cf: Pore compressibility (1/psi)
        Pi: Initial pressure (psia)

    Returns:
        List of dicts with F, Eo, Efw, Et, N_apparent for each step
    """
    results = []
    for i in range(len(pressures)):
        P = pressures[i]
        Np = Np_list[i]
        Bo = Bo_list[i]
        Rs = Rs_list[i]
        Bg = Bg_list[i]
        Rp = Rp_list[i]

        # Total withdrawal (F)
        F = Np * (Bo + (Rp - Rs) * Bg)

        # Oil expansion term
        Eo = (Bo - Boi) + (Rsi - Rs) * Bg

        # Connate water and pore compressibility term
        Efw = Boi * (cw * Swi + cf) / (1.0 - Swi) * (Pi - P)

        # Total expansion (no gas cap, m=0)
        Et = Eo + Efw

        # Apparent N from this data point
        N_apparent = F / Et if abs(Et) > 1e-12 else 0.0

        results.append({
            "P_psia": P,
            "Np_STB": Np,
            "F_RB": round(F, 0),
            "Eo_RB_STB": round(Eo, 6),
            "Efw_RB_STB": round(Efw, 6),
            "Et_RB_STB": round(Et, 6),
            "N_apparent_STB": round(N_apparent, 0),
        })

    return results


# =============================================================================
# MODULE 3 — HISTORY MATCHING (LHS + PSO)
# =============================================================================

def latin_hypercube_sample(
    param_ranges: Dict[str, Tuple[float, float]],
    n_samples: int,
    seed: Optional[int] = None
) -> List[Dict[str, float]]:
    """
    Generate Latin Hypercube Samples for parameter space exploration.

    Each parameter range is divided into n_samples equal strata, and
    one sample is drawn from each stratum. Strata are then randomly
    shuffled across parameters to ensure good coverage.

    Args:
        param_ranges: Dict of {param_name: (min_value, max_value)}
        n_samples: Number of samples to generate
        seed: Random seed for reproducibility

    Returns:
        List of dicts, each dict is one sample with param_name: value
    """
    if seed is not None:
        random.seed(seed)

    param_names = list(param_ranges.keys())
    n_params = len(param_names)

    # Generate stratified samples for each parameter
    param_samples = {}
    for name in param_names:
        lo, hi = param_ranges[name]
        # Create one random value per stratum
        samples = []
        for i in range(n_samples):
            stratum_lo = lo + (hi - lo) * i / n_samples
            stratum_hi = lo + (hi - lo) * (i + 1) / n_samples
            samples.append(random.uniform(stratum_lo, stratum_hi))
        # Shuffle to destroy correlation between parameters
        random.shuffle(samples)
        param_samples[name] = samples

    # Assemble into list of dicts
    result = []
    for i in range(n_samples):
        sample = {}
        for name in param_names:
            sample[name] = param_samples[name][i]
        result.append(sample)

    return result


def objective_function_rms(
    observed: List[float], simulated: List[float]
) -> float:
    """
    Root Mean Square mismatch between observed and simulated data.

    Args:
        observed: List of observed values
        simulated: List of simulated values (same length)

    Returns:
        RMS error
    """
    n = len(observed)
    if n == 0:
        return 0.0
    ss = sum((o - s) ** 2 for o, s in zip(observed, simulated))
    return math.sqrt(ss / n)


def objective_function_nrms(
    observed: List[float], simulated: List[float]
) -> float:
    """
    Normalized RMS mismatch (RMS divided by observed data range).

    Args:
        observed: List of observed values
        simulated: List of simulated values

    Returns:
        NRMS (dimensionless, 0 = perfect match)
    """
    rms = objective_function_rms(observed, simulated)
    obs_range = max(observed) - min(observed)
    if obs_range < 1e-12:
        return 0.0
    return rms / obs_range


def pso_optimize(
    param_ranges: Dict[str, Tuple[float, float]],
    objective_fn,
    n_particles: int = 30,
    n_iterations: int = 100,
    w: float = 0.7,
    c1: float = 1.5,
    c2: float = 1.5,
    seed: Optional[int] = None
) -> Tuple[Dict[str, float], float, List[float]]:
    """
    Particle Swarm Optimization for history matching.

    Args:
        param_ranges: Dict of {param_name: (min, max)}
        objective_fn: Callable that takes a param dict and returns mismatch
        n_particles: Swarm size
        n_iterations: Number of iterations
        w: Inertia weight
        c1: Cognitive coefficient
        c2: Social coefficient
        seed: Random seed

    Returns:
        (best_params, best_objective, convergence_history)
    """
    if seed is not None:
        random.seed(seed)

    param_names = list(param_ranges.keys())

    # Initialize particles using LHS for good initial coverage
    particles = latin_hypercube_sample(param_ranges, n_particles, seed)

    # Initialize velocities to zero
    velocities = [{name: 0.0 for name in param_names} for _ in range(n_particles)]

    # Evaluate initial positions
    pbest = [dict(p) for p in particles]  # Personal best positions
    pbest_obj = [objective_fn(p) for p in particles]

    # Global best
    gbest_idx = min(range(n_particles), key=lambda i: pbest_obj[i])
    gbest = dict(pbest[gbest_idx])
    gbest_obj = pbest_obj[gbest_idx]

    convergence = [gbest_obj]

    for iteration in range(n_iterations):
        for i in range(n_particles):
            for name in param_names:
                lo, hi = param_ranges[name]

                r1 = random.random()
                r2 = random.random()

                # Update velocity
                velocities[i][name] = (
                    w * velocities[i][name]
                    + c1 * r1 * (pbest[i][name] - particles[i][name])
                    + c2 * r2 * (gbest[name] - particles[i][name])
                )

                # Update position
                particles[i][name] += velocities[i][name]

                # Clamp to bounds
                particles[i][name] = max(lo, min(hi, particles[i][name]))

            # Evaluate
            obj = objective_fn(particles[i])

            # Update personal best
            if obj < pbest_obj[i]:
                pbest[i] = dict(particles[i])
                pbest_obj[i] = obj

                # Update global best
                if obj < gbest_obj:
                    gbest = dict(particles[i])
                    gbest_obj = obj

        convergence.append(gbest_obj)

    return gbest, gbest_obj, convergence


# =============================================================================
# MODULE 5 — PETROPHYSICS AND GEOSTATISTICS
# =============================================================================

def archie_sw(phi: float, Rt: float, Rw: float,
              a: float = 0.62, m: float = 2.15,
              n: float = 2.0) -> float:
    """
    Water saturation from Archie's equation.

    Args:
        phi: Porosity (fraction)
        Rt: True formation resistivity (ohm-m)
        Rw: Formation water resistivity (ohm-m)
        a: Tortuosity factor (default 0.62 for sandstone)
        m: Cementation exponent (default 2.15)
        n: Saturation exponent (default 2.0)

    Returns:
        Sw (water saturation, fraction)
    """
    if phi <= 0 or Rt <= 0 or Rw <= 0:
        raise ValueError("phi, Rt, and Rw must all be positive")

    Sw_n = a * Rw / (phi ** m * Rt)
    Sw = Sw_n ** (1.0 / n)
    return min(Sw, 1.0)


def kozeny_carman_perm(phi: float, d_grain_mm: float,
                       tau: float = 1.5) -> float:
    """
    Permeability from Kozeny-Carman equation.

    Args:
        phi: Porosity (fraction)
        d_grain_mm: Grain diameter (mm)
        tau: Tortuosity (default 1.5)

    Returns:
        Permeability in md
    """
    d_cm = d_grain_mm / 10.0  # mm to cm
    # k in cm2, then convert to darcy (1 darcy = 9.869e-9 cm2)
    k_cm2 = (phi ** 3 * d_cm ** 2) / (72.0 * tau ** 2 * (1.0 - phi) ** 2)
    k_darcy = k_cm2 / 9.869e-9
    k_md = k_darcy * 1000.0
    return k_md


def spherical_variogram(h: float, C0: float, C: float, a: float) -> float:
    """
    Spherical variogram model.

    Args:
        h: Lag distance
        C0: Nugget
        C: Sill - Nugget (structured variance)
        a: Range

    Returns:
        gamma(h)
    """
    if h <= 0:
        return 0.0
    if h >= a:
        return C0 + C
    ratio = h / a
    return C0 + C * (1.5 * ratio - 0.5 * ratio ** 3)


def covariance_from_variogram(h: float, C0: float, C: float,
                               a: float) -> float:
    """
    Covariance function derived from spherical variogram.

    C(h) = sill - gamma(h)
    """
    sill = C0 + C
    return sill - spherical_variogram(h, C0, C, a)


def distance_2d(x1: float, y1: float, x2: float, y2: float) -> float:
    """Euclidean distance between two 2D points."""
    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)


def simple_kriging_2d(
    known_points: List[Tuple[float, float, float]],
    target_x: float, target_y: float,
    mean: float,
    C0: float, C: float, a: float
) -> Tuple[float, float]:
    """
    Simple kriging estimate at a single target point in 2D.

    Args:
        known_points: List of (x, y, value) tuples
        target_x, target_y: Coordinates of estimation point
        mean: Known/assumed mean of the variable
        C0: Nugget
        C: Sill - Nugget
        a: Range

    Returns:
        (estimated_value, kriging_variance)
    """
    n = len(known_points)
    if n == 0:
        return mean, C0 + C

    # Build covariance matrix between known points
    # Using simple list-of-lists instead of numpy
    K = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            h = distance_2d(known_points[i][0], known_points[i][1],
                            known_points[j][0], known_points[j][1])
            K[i][j] = covariance_from_variogram(h, C0, C, a)

    # Build covariance vector between known points and target
    k = [0.0] * n
    for i in range(n):
        h = distance_2d(known_points[i][0], known_points[i][1],
                        target_x, target_y)
        k[i] = covariance_from_variogram(h, C0, C, a)

    # Solve K * lambda = k using Gaussian elimination
    # Augmented matrix [K | k]
    aug = [row[:] + [k[i]] for i, row in enumerate(K)]

    # Forward elimination with partial pivoting
    for col in range(n):
        # Find pivot
        max_row = col
        max_val = abs(aug[col][col])
        for row in range(col + 1, n):
            if abs(aug[row][col]) > max_val:
                max_val = abs(aug[row][col])
                max_row = row
        aug[col], aug[max_row] = aug[max_row], aug[col]

        pivot = aug[col][col]
        if abs(pivot) < 1e-12:
            # Singular or near-singular — add small nugget
            aug[col][col] += 1e-6
            pivot = aug[col][col]

        for row in range(col + 1, n):
            factor = aug[row][col] / pivot
            for j in range(col, n + 1):
                aug[row][j] -= factor * aug[col][j]

    # Back substitution
    lambdas = [0.0] * n
    for i in range(n - 1, -1, -1):
        s = aug[i][n]
        for j in range(i + 1, n):
            s -= aug[i][j] * lambdas[j]
        lambdas[i] = s / aug[i][i] if abs(aug[i][i]) > 1e-12 else 0.0

    # Kriging estimate
    z_star = mean
    for i in range(n):
        z_star += lambdas[i] * (known_points[i][2] - mean)

    # Kriging variance
    C00 = covariance_from_variogram(0, C0, C, a)
    variance = C00 - sum(lambdas[i] * k[i] for i in range(n))
    variance = max(variance, 0.0)

    return z_star, variance


def krige_grid_2d(
    known_points: List[Tuple[float, float, float]],
    nx: int, ny: int,
    xmin: float, xmax: float,
    ymin: float, ymax: float,
    mean: float,
    C0: float, C: float, a: float
) -> Tuple[List[List[float]], List[List[float]]]:
    """
    Krige an entire 2D grid using simple kriging.

    Args:
        known_points: List of (x, y, value) tuples
        nx, ny: Grid dimensions
        xmin, xmax, ymin, ymax: Grid extent
        mean: Known mean
        C0, C, a: Variogram parameters (nugget, sill-nugget, range)

    Returns:
        (grid_values, grid_variance) as 2D lists [row][col]
    """
    dx = (xmax - xmin) / max(nx - 1, 1)
    dy = (ymax - ymin) / max(ny - 1, 1)

    grid_values = [[0.0] * nx for _ in range(ny)]
    grid_variance = [[0.0] * nx for _ in range(ny)]

    for j in range(ny):
        y = ymin + j * dy
        for i in range(nx):
            x = xmin + i * dx
            val, var = simple_kriging_2d(
                known_points, x, y, mean, C0, C, a
            )
            grid_values[j][i] = round(val, 4)
            grid_variance[j][i] = round(var, 4)

    return grid_values, grid_variance


# =============================================================================
# DEMO — MINI SENSITIVITY STUDY
# =============================================================================

def demo_sensitivity_study():
    """
    Run a mini sensitivity study demonstrating multiple modules.

    Scenario: Evaluate how reservoir properties affect production
    for a conceptual Marcellus Shale well in WV.
    """
    print("=" * 70)
    print("MINI SENSITIVITY STUDY — Conceptual Marcellus Shale Well (WV)")
    print("=" * 70)
    print()

    # --- 1. PVT Report at initial conditions ---
    print("--- STEP 1: PVT Properties at Initial Conditions ---")
    print()
    T_res = 180.0       # F (reservoir temperature)
    P_init = 4500.0     # psia (initial reservoir pressure)
    API = 50.0           # condensate-rich gas
    gamma_g = 0.70       # gas gravity
    pvt_report(T_res, P_init, API, gamma_g)
    print()

    # --- 2. Vogel IPR at different reservoir pressures ---
    print("--- STEP 2: IPR Sensitivity to Reservoir Pressure ---")
    print()
    q_test = 800.0       # STB/D from a well test
    Pwf_test = 2500.0    # psia at that rate

    for Pr in [4500, 3500, 2500]:
        ratio = Pwf_test / Pr if Pwf_test < Pr else 0.99
        if ratio >= 1.0:
            print(f"  Pr={Pr} psia: Pwf_test >= Pr, skipping")
            continue
        qmax = q_test / (1.0 - 0.2 * ratio - 0.8 * ratio ** 2)
        print(f"  Pr = {Pr} psia -> AOF (qmax) = {qmax:.0f} STB/D")
    print()

    # --- 3. Decline Curve Forecast ---
    print("--- STEP 3: Decline Curve Forecast (Hyperbolic, b=0.8) ---")
    print()
    qi = 1200.0  # STB/D initial rate
    Di = 0.15    # 1/month nominal decline
    b = 0.8      # typical for shale

    forecast = decline_forecast(qi, Di, b, t_max=120, dt=12, q_econ=20)
    print(f"{'Time (mo)':>10} {'Rate (STB/D)':>14} {'Cum (MSTB)':>12}")
    print("-" * 38)
    for row in forecast:
        print(f"{row['time_months']:>10.0f} {row['rate_STBD']:>14.1f}"
              f" {row['cumulative_MSTB']:>12.1f}")
    print()

    # --- 4. Archie Water Saturation ---
    print("--- STEP 4: Archie Water Saturation (Petrophysics) ---")
    print()
    phi_values = [0.05, 0.08, 0.10, 0.15, 0.20]
    Rt = 50.0   # ohm-m
    Rw = 0.03   # ohm-m (saline formation water)

    print(f"  Rt = {Rt} ohm-m, Rw = {Rw} ohm-m")
    print(f"  {'Porosity':>10} {'Sw':>10} {'So (1-Sw)':>10}")
    print("  " + "-" * 32)
    for phi in phi_values:
        Sw = archie_sw(phi, Rt, Rw, a=0.62, m=2.15, n=2.0)
        print(f"  {phi:>10.2f} {Sw:>10.3f} {1-Sw:>10.3f}")
    print()

    # --- 5. LHS Parameter Sampling ---
    print("--- STEP 5: LHS Parameter Samples for History Matching ---")
    print()
    param_ranges = {
        "kh_md": (10.0, 200.0),
        "phi": (0.05, 0.15),
        "skin": (-2.0, 10.0),
        "aquifer_J": (0.0, 50.0),
    }
    samples = latin_hypercube_sample(param_ranges, n_samples=8, seed=42)
    print(f"  {'Sample':>6} {'kh (md)':>10} {'phi':>8} {'Skin':>8}"
          f" {'Jaq':>10}")
    print("  " + "-" * 44)
    for i, s in enumerate(samples):
        print(f"  {i+1:>6} {s['kh_md']:>10.1f} {s['phi']:>8.3f}"
              f" {s['skin']:>8.1f} {s['aquifer_J']:>10.1f}")
    print()

    # --- 6. Simple Kriging on a small grid ---
    print("--- STEP 6: Simple Kriging — Porosity Map (10x10 grid) ---")
    print()
    # Known porosity measurements (x_ft, y_ft, porosity)
    known = [
        (0, 0, 0.12),
        (500, 0, 0.15),
        (1000, 0, 0.10),
        (0, 500, 0.14),
        (500, 500, 0.18),
        (1000, 500, 0.13),
        (0, 1000, 0.11),
        (500, 1000, 0.16),
        (1000, 1000, 0.09),
    ]
    mean_poro = sum(p[2] for p in known) / len(known)

    # Variogram: nugget=0.0005, sill-nugget=0.001, range=600ft
    grid_vals, grid_var = krige_grid_2d(
        known, nx=10, ny=10,
        xmin=0, xmax=1000, ymin=0, ymax=1000,
        mean=mean_poro, C0=0.0005, C=0.001, a=600
    )

    print(f"  Mean porosity from data: {mean_poro:.4f}")
    print(f"  Variogram: nugget=0.0005, C=0.001, range=600 ft")
    print()
    print("  Kriged porosity grid (rows = Y, cols = X):")
    for row in grid_vals:
        print("  " + " ".join(f"{v:.3f}" for v in row))
    print()
    print("  Kriging variance grid:")
    for row in grid_var:
        print("  " + " ".join(f"{v:.4f}" for v in row))
    print()

    # --- 7. Nodal Analysis ---
    print("--- STEP 7: Nodal Analysis (IPR-VFP Intersection) ---")
    print()
    q_op, Pwf_op = nodal_analysis(
        Pr=3500, Pwf_test=2000, q_test=1000,
        Pwh_psia=200, T_wh_F=100, T_bh_F=180,
        depth_ft=8000, GOR_scfSTB=600, WC=0.20,
        d_inches=2.992, API=35, gamma_g=0.70
    )
    print(f"  Operating point: q = {q_op:.0f} STB/D, Pwf = {Pwf_op:.0f} psia")
    print()

    # --- Summary ---
    print("=" * 70)
    print("SENSITIVITY STUDY COMPLETE")
    print()
    print("Key findings:")
    print(f"  - Z-factor at {P_init} psia, {T_res} F: "
          f"{z_factor(T_res, P_init, gamma_g):.4f}")
    print(f"  - Decline from {qi} STB/D (b={b}): "
          f"EUR ~ {forecast[-1]['cumulative_MSTB']:.0f} MSTB "
          f"at {forecast[-1]['time_months']:.0f} months")
    print(f"  - Sw range at phi=0.05-0.20: "
          f"{archie_sw(0.20, Rt, Rw):.2f} - {archie_sw(0.05, Rt, Rw):.2f}")
    print(f"  - Nodal analysis: {q_op:.0f} STB/D at {Pwf_op:.0f} psia BHP")
    print()
    print("DISCLAIMER: This is an educational tool. Results use standard")
    print("correlations and simplified models. Always validate against")
    print("lab data and full simulation for production decisions.")
    print("=" * 70)


# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    demo_sensitivity_study()
