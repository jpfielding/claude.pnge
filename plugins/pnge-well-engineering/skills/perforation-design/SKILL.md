---
name: perforation-design
description: >
  Design and evaluate perforation programs for oil and gas wells including
  conventional single-zone and multi-cluster horizontal completions. Covers
  perforation phasing selection for casing stress and flow efficiency, shot
  density optimization, penetration depth correction from API RP 19B Berea
  surface test to in-situ conditions using rock strength and overburden
  adjustment, total perforation skin calculation using the Karakas-Tariq
  equations including phasing skin and wellbore skin components, underbalanced
  versus overbalanced perforating selection criteria and surge flow calculation,
  and limited entry perforation design for multi-cluster horizontal completions
  including friction-based diversion, entry hole velocity, and cluster-to-
  cluster distribution efficiency. Use when selecting gun and charge systems,
  calculating total skin from perforations, designing limited entry completions,
  evaluating perforation cluster efficiency, or optimizing stage design in
  horizontal wells. Trigger phrases include perforation skin, McLeod equation,
  shot density, phasing selection, limited entry design, cluster efficiency,
  underbalanced perforating, entry hole diameter, penetration depth correction,
  or perforation friction diversion.
---

# Perforation Design Calculator

Completions engineering skill covering perforation design for vertical and
horizontal wells, skin calculations, underbalance criteria, and limited entry
design for multi-cluster hydraulic fracturing.

**Important:** Penetration depths and flow efficiencies are gun-and-formation
specific. API RP 19B test results (Berea sandstone) must be corrected for
in-situ conditions. Final design should reference vendor ballistic data.

---

## Module 1 — Phasing and Shot Density Selection

### Phasing Comparison

| Phasing | Casing Stress | Flow Efficiency | Common Use |
|---------|--------------|----------------|-----------|
| 0° (inline) | Highest | Low (one plane) | Avoid except casing limitation |
| 180° | Moderate | Low | Rarely used; two opposing planes |
| 120° | Good | Good | General production, some frac jobs |
| 90° | Best for frac | Very good | Hydraulic fracturing preferred |
| 60° | Moderate | Best for flow | Near-wellbore efficiency maximum |

```python
def phasing_flow_efficiency(phasing_deg):
    """
    Approximate relative flow efficiency vs. open hole (Karakas-Tariq 1991).
    These are directional — actual values are function of shot density and penetration.
    phasing_deg: 60, 90, 120, 180, 360 (0 degrees)
    """
    efficiency = {60: 0.95, 90: 0.92, 120: 0.87, 180: 0.75, 360: 0.65}
    return efficiency.get(phasing_deg, 0.80)
```

### Shot Density Guidelines

| Application | Typical SPF | Notes |
|-------------|------------|-------|
| Gravel pack / unconsolidated | 4–6 | Maximize inflow area |
| Conventional production | 4–8 | Balance skin vs. casing integrity |
| Hydraulic fracturing entry | 2–4 | Control entry, limited entry design |
| Stimulation (matrix acid) | 6–12 | Maximize contact area |
| Horizontal limited entry | 1–3 | Diversion via friction |

---

## Module 2 — Penetration Depth (API RP 19B Correction)

```python
def penetration_depth_insitu(L_berea_in, UCS_berea_psi=6000,
                              UCS_insitu_psi=8000,
                              overburden_psi=6500, pore_psi=3000,
                              cementation_factor=1.0):
    """
    API RP 19B: in-situ penetration correction.
    Step 1: Rock strength correction
      L_rc = L_berea * (UCS_berea / UCS_insitu)^0.36
    Step 2: Effective stress correction (Berea tested at zero confining pressure)
      sigma_eff = overburden - pore_pressure
      correction = (1 - 0.086 * sqrt(sigma_eff / 1000))
    L_insitu = L_rc * correction * cementation_factor
    All lengths in inches; pressures in psi.
    """
    L_rc = L_berea_in * (UCS_berea_psi / UCS_insitu_psi)**0.36
    sigma_eff = overburden_psi - pore_psi
    stress_corr = 1.0 - 0.086 * (sigma_eff / 1000.0)**0.5
    return L_rc * stress_corr * cementation_factor
```

**Typical Appalachian corrections:**
| Formation | UCS (psi) | L_Berea (in) | Correction factor | L_insitu (in) |
|-----------|----------|-------------|-----------------|--------------|
| Marcellus shale | 8,000–14,000 | 12–18 | 0.55–0.75 | 7–14 |
| Utica shale | 10,000–16,000 | 12–18 | 0.50–0.70 | 6–13 |
| Onondaga limestone | 14,000–20,000 | 10–14 | 0.45–0.65 | 5–9 |

---

## Module 3 — Perforation Skin (Karakas and Tariq, 1991)

Total perforation skin: S_perf = S_H + S_V + S_wb

```python
import math

def horizontal_skin_sh(k_h, k_v, L_perf_in, r_perf_in, h_perf_ft,
                        phasing_deg):
    """
    S_H: horizontal component of perforation skin
    Simplified form (Karakas-Tariq Table 1 constants for phasing):
    S_H = ln(r_w / r'_w)  where r'_w = a1 * exp(a2 * Lp/r_w) * r_w
    Uses phasing-dependent a1, a2 constants from K-T Table 1.
    This is the dominant term for standard completions.
    """
    # Constants from Karakas-Tariq (1991) Table 1
    params = {
        360: (0.250, -2.091, 0.0453),   # 0° phasing
        180: (0.500, -2.025, 0.0943),
        120: (0.648, -2.018, 0.0634),
         90: (0.726, -1.905, 0.1038),
         60: (0.813, -1.898, 0.1023),
    }
    a1, a2, a3 = params.get(phasing_deg, params[90])
    r_w_ft = 0.365   # typical wellbore radius (ft)
    L_perf_ft = L_perf_in / 12.0
    r_perf_ft = r_perf_in / 12.0
    # Effective wellbore radius
    r_w_prime = a1 * r_w_ft * math.exp(a2 * r_perf_ft + a3 * L_perf_ft)
    return math.log(r_w_ft / r_w_prime)

def wellbore_skin_swb(r_perf_in, L_perf_in, r_w_in, spf, phasing_deg):
    """
    S_wb: wellbore skin (near-wellbore damage not cleaned by perfs).
    Typically small for underbalanced perforating; significant for OBP.
    Approximate: S_wb = c1 * exp(c2 * r_w) for phasing-dependent c1, c2.
    """
    c1_c2 = {360: (1.6e-1, 2.675), 180: (2.6e-2, 4.532),
             120: (6.6e-3, 5.320),  90: (1.9e-3, 6.155), 60: (3.0e-4, 7.509)}
    c1, c2 = c1_c2.get(phasing_deg, c1_c2[90])
    r_w_ft = r_w_in / 12.0
    return c1 * math.exp(c2 * r_w_ft)

def total_perforation_skin(S_H, S_V=0.0, S_wb=0.0):
    """S_total = S_H + S_V + S_wb"""
    return S_H + S_V + S_wb
```

---

## Module 4 — Underbalanced vs. Overbalanced Perforating

### Underbalance Pressure Recommendation (King, 1989)

```python
def recommended_underbalance(reservoir_psi, k_md, fluid="gas"):
    """
    Recommended underbalance pressure (psi) to clean perforation tunnels.
    King (1989) empirical:
      Gas wells:  UB = 250 + 5500/k for k < 10 mD
      Oil wells:  UB = 1000 - 200*k for k in [0.01, 5] mD
                  UB = 200 psi minimum
    k_md: formation permeability (mD)
    """
    if fluid.lower() == "gas":
        ub = 250 + 5500.0 / max(k_md, 0.1)
    else:
        ub = max(200.0, 1000.0 - 200.0 * k_md)
    # Don't exceed reservoir pressure
    return min(ub, reservoir_psi * 0.85)

def is_underbalanced(wellbore_psi, reservoir_psi):
    """Simple check: wellbore_psi < reservoir_psi -> underbalanced."""
    return wellbore_psi < reservoir_psi
```

**Selection guidance:**
| Condition | Recommended | Notes |
|-----------|-------------|-------|
| k > 50 mD | Either; OBP simpler | Perfs clean up quickly on flow |
| k = 1–50 mD | Underbalanced preferred | Surge removes crushed zone |
| k < 1 mD (tight) | Overbalanced + acid or frac | UBP has limited benefit |
| H2S present | Avoid large UBP | Risk of rapid depressurization |
| Unconsolidated | Balanced or slight OBP | UBP can cause sand influx |

---

## Module 5 — Limited Entry Design (Multi-Cluster Horizontal)

### Friction Pressure at Perforation Entry

```python
def perforation_friction_pressure(q_bpm, n_perfs, d_perf_in,
                                   fluid_sg=1.0, Cd=0.9):
    """
    dP_perf = 0.2369 * (rho / Cd^2) * (q / n / d^2)^2
    q_bpm:    total injection rate (bbl/min)
    n_perfs:  total number of perforations in cluster
    d_perf_in: entry hole diameter (inches)
    fluid_sg: fluid specific gravity
    Cd:       discharge coefficient (0.85–0.95 typical)
    Returns: friction pressure (psi) across perforations
    """
    rho_ppg = fluid_sg * 8.34   # lb/gal
    q_per_perf_bpm = q_bpm / n_perfs
    return 0.2369 * (rho_ppg / Cd**2) * (q_per_perf_bpm / d_perf_in**2)**2
```

### Diversion Efficiency (Limited Entry)

```python
def limited_entry_diversion(q_total_bpm, n_clusters, spf_per_cluster,
                              d_perf_in, delta_stress_psi, fluid_sg=1.0,
                              Cd=0.9):
    """
    Equal entry when dP_perf >> delta_stress between clusters.
    Rule of thumb: dP_perf per cluster > 2 × stress contrast to ensure
    >80% of clusters accept fluid.
    Returns: dP_perf for a single cluster and diversion ratio estimate.
    """
    n_perfs_cluster = spf_per_cluster
    q_per_cluster_bpm = q_total_bpm / n_clusters
    dp = perforation_friction_pressure(q_per_cluster_bpm,
                                        n_perfs_cluster, d_perf_in,
                                        fluid_sg, Cd)
    ratio = dp / delta_stress_psi if delta_stress_psi > 0 else float("inf")
    efficiency = min(1.0, 0.5 + 0.5 * min(ratio / 2.0, 1.0))
    return {"dP_perf_psi": dp, "diversion_ratio": ratio,
            "estimated_cluster_efficiency": efficiency}
```

**Appalachian limited entry parameters:**
- Typical stress contrast between clusters: 200–800 psi
- Target dP_perf: 500–1,500 psi for adequate diversion
- Entry hole diameter: 0.38"–0.50" for most perforating charges at 2–4 SPF

---

## Output Format

```
## Perforation Design — [Well / Zone]
**Formation:** [Name] | **Depth:** X,XXX–X,XXX ft | **k:** X.X mD

### Gun/Charge Selection
| Parameter | Value |
|-----------|-------|
| Charge type | [API RP 19B class] |
| Berea penetration (in) | |
| In-situ penetration (in) | [corrected] |
| Entry hole diameter (in) | |
| Shot density (SPF) | |
| Phasing | |

### Perforation Skin Summary
| Component | Value |
|-----------|-------|
| S_H (horizontal) | |
| S_V (vertical) | |
| S_wb (wellbore) | |
| S_perf (total) | |

### Underbalance Assessment
| Recommended UB (psi) | Achievable UB (psi) | Method |
|---------------------|--------------------|----|
| | | UBP / OBP + acid |

### Limited Entry (Horizontal)
| Cluster spacing (ft) | SPF/cluster | dP_perf (psi) | Stress contrast (psi) | Efficiency |
|---------------------|------------|--------------|----------------------|------------|
| | | | | |
```

---

## Error Handling

| Condition | Cause | Action |
|-----------|-------|--------|
| S_H very negative | Perfs longer than wellbore radius | Check input units (in vs ft) |
| dP_perf < stress contrast | Too many perfs or large holes | Reduce SPF or entry diameter |
| In-situ penetration < 2 in | Very hard rock + deep wells | Consider larger gun OD or jet perforating |
| UB exceeds reservoir pressure | Calculation error | Cap at 85% of reservoir pressure |

---

## Caveats

- Karakas-Tariq skin equations are analytical and assume uniform perforation
  tunnel penetration. In reality, tunnels vary due to rock heterogeneity and
  gun eccentricity.
- API RP 19B Berea strength correction is an empirical approximation. Lab
  testing of actual formation core is more accurate for penetration prediction.
- Limited entry diversion efficiency assumes uniform stress contrast across
  clusters. Natural fractures and local heterogeneity can override designed
  diversion.
- Perforation friction pressure equations assume Newtonian fluid. For
  viscoelastic frac fluids, apparent viscosity at perforation velocity is
  typically much higher — dP_perf will be larger (better diversion).
- Near-wellbore tortuosity (not captured here) can dominate treating pressure
  in tight formations; evaluate with step-down test after perforating.
