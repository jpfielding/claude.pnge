# PNGE Plugin — Data Sources Reference

**Plugin version:** v0.4.0
**Skills:** 50 (28 data access, 22 computational)
**Agents:** 6
**Commands:** 6
**Date:** 2026-03-08

---

## Data Access Skills (28)

### U.S. Federal — Energy & Production

| Skill | Source | Key? | Primary Use |
|-------|--------|------|-------------|
| `eia-data` | EIA Open Data API v2 | Yes (free) | U.S. energy statistics, gas/oil prices, storage, electricity |
| `opec-data` | OPEC production via EIA STEO | Yes (EIA key) | OPEC+ production quotas and actual output |
| `boem-offshore` | BOEM/BSEE Data Center | No | Federal OCS wells, leases, platforms, production |
| `netl-edx` | NETL Energy Data eXchange (CKAN) | Yes (free) | DOE research datasets, ClaiMM critical minerals, CCS |
| `netl-carbon-storage` | NATCARB Atlas v5 | Yes (free, optional) | CCS storage capacity, sequestration projects |
| `doe-geothermal` | DOE GDR / OpenEI | Yes (free) | Geothermal well data, temperature gradients, resources |
| `doe-osti` | DOE OSTI Technical Reports | No | DOE-funded research publications, national lab reports |

### U.S. Federal — Geology & Water

| Skill | Source | Key? | Primary Use |
|-------|--------|------|-------------|
| `usgs-produced-waters` | USGS Produced Waters Geochemical DB v3.0 | No | 115k+ brine samples with Li, Mg, TDS; all major U.S. basins |
| `usgs-minerals` | USGS Mineral Commodity Summaries | No | Annual production, reserves, pricing for 90+ commodities |
| `usgs-pubs` | USGS Publications Warehouse | No | USGS professional papers, open-file reports, fact sheets |
| `usgs-earthquakes` | USGS ComCat (FDSN) | No | Earthquake catalog, induced seismicity near injection wells |
| `usgs-waterdata` | USGS NWIS + Water Quality Portal | No | Streamflow, groundwater levels, water quality samples |
| `kggs-well-logs` | KGS Wireline Log Repository | No | LAS 2.0 wireline logs, digital formation evaluation |
| `macrostrat` | Macrostrat Formation Stratigraphy | No | Formation ages, lithologies, stratigraphic columns |

### U.S. Federal — Environmental

| Skill | Source | Key? | Primary Use |
|-------|--------|------|-------------|
| `epa-enviro` | EPA Envirofacts & ECHO | No (key optional) | UIC wells, NPDES permits, TRI facility data, compliance |
| `epa-ghg` | EPA GHGRP Facility Emissions | No | Facility-level GHG reporting across all subparts |
| `epa-ghgrp-subpartw` | EPA GHGRP Subpart W | No | Oilfield methane emissions specifically |
| `fracfocus` | FracFocus Chemical Disclosure | No | HF chemical disclosures, frac fluid composition, proppant |

### U.S. State-Level

| Skill | Source | Key? | Primary Use |
|-------|--------|------|-------------|
| `wvges-wells` | WV Geological & Economic Survey | No | 153k+ WV wells, completions, formation tops, production |
| `padep-wells` | PA DEP Unconventional Well Registry (Socrata) | No | Marcellus/Utica permits, production, fracking disclosures |
| `odnr-wells` | Ohio DNR Oil and Gas Wells | No | Utica/Point Pleasant well data, permits, production |

### Global & Economic

| Skill | Source | Key? | Primary Use |
|-------|--------|------|-------------|
| `fred-prices` | Federal Reserve FRED | Yes (free) | WTI/Brent crude, Henry Hub gas, commodity price history |
| `worldbank-energy` | World Bank Open Data | No | 200+ energy indicators by country, renewable capacity |
| `comtrade-minerals` | UN Comtrade | Optional (free) | Li/Mg/Co trade flows, import/export by country |
| `iea-open` | IEA Free Datasets | No | EV tracker, energy prices, NZE scenarios, CCUS, SDG7 |
| `wri-aqueduct` | WRI Aqueduct Water Risk | No | Water stress scores by basin, corporate water risk |

### Literature & Research

| Skill | Source | Key? | Primary Use |
|-------|--------|------|-------------|
| `openalex` | OpenAlex Open-Access Literature | No | 250M+ research works, citations, author disambiguation |
| `crossref-doi` | CrossRef REST API | No | DOI resolution, citation metadata, journal info |

---

## Computational & Simulation Skills (22)

### Production & Completions Engineering (12)

| Skill | Key Capabilities | Primary WVU Courses |
|-------|-----------------|---------------------|
| `pnge-mechanics` | Statics, axial/beam stress, Lamé thick-wall cylinders, Mohr's circle | PNGE 351, MAE 243 |
| `frac-design` | PKN/KGD fracture geometry, Nolte-Smith analysis, proppant transport | PNGE 341 |
| `wellbore-stability` | Kirsch equations, mud weight window, breakout and fracture prediction | PNGE 351, PNGE 341 |
| `petrophysics` | Log interpretation: Vsh, porosity, Sw (Archie/Simandoux), brittleness | PNGE 331, PNGE 341 |
| `artificial-lift` | Rod pump, ESP sizing, gas lift design, plunger lift, liquid loading | PNGE 361, PNGE 411 |
| `flow-assurance` | Hydrates (Katz/Hammerschmidt), CO2 corrosion, H2S sour service, scale | PNGE 341, PNGE 361 |
| `tubing-design` | Lubinski four-effect force analysis, buckling, seal assembly | PNGE 341, PNGE 351 |
| `perforation-design` | Karakas-Tariq skin, phasing, underbalance criteria, limited entry | PNGE 341 |
| `surface-facilities` | Separator sizing, TEG dehydration, compression HP, backpressure | PNGE 361, ChBE 311 |
| `rta-production` | Arps DCA (hyperbolic/exponential/harmonic), EUR, Blasingame FMB | PNGE 321, PNGE 411 |
| `well-test-analysis` | Horner plot, skin factor, Bourdet derivative, wellbore storage, Ei | PNGE 321, PNGE 361 |
| `matrix-acidizing` | HCl carbonate design, HF/HCl sandstone (McLeod), Hawkins skin, Da | PNGE 341, PNGE 361 |

### Simulation & Reference Tools (4)

| Skill | Key Capabilities |
|-------|-----------------|
| `mass-energy-balance` | Material/energy balances, combustion, flash calculation (Rachford-Rice) |
| `nist-webbook` | NIST thermodynamic properties for methane, CO2, water, and light HCs |
| `tnav` | tNavigator-style reservoir simulation (black oil, PVT, decline, nodal) |
| `pnge-visual-explainer` | Generate self-contained HTML visualizations of PNGE concepts and data |

### Engineering Science Tutoring (6)

| Skill | Key Capabilities | WVU Course |
|-------|-----------------|-----------|
| `fluid-mechanics` | Colebrook-White, Darcy-Weisbach, Bernoulli, venturi, pump power | ChBE 311 |
| `reaction-engineering` | CSTR/PFR/batch design, Arrhenius, Levenspiel plot, adiabatic T rise | ChBE 321 |
| `thermo-eos` | Peng-Robinson/SRK EOS, Z-factor, fugacity, VLE, Rachford-Rice flash | ChBE 231 |
| `physics-mechanics` | Kinematics, Newton laws, energy, momentum, rotation, SHM | PHYS 111 |
| `physics-em` | Coulomb law, circuits, RC/RL/LC, Faraday induction, magnetic force | PHYS 112 |
| `diff-equations` | 1st/2nd order ODEs, Laplace transforms, eigenvalue systems, RK4 | MATH 261 |

---

## Agents (6)

| Agent | Orchestrates | Purpose |
|-------|-------------|---------|
| `li-mg-prospector` | usgs-produced-waters, usgs-minerals, eia-data, usgs-pubs, doe-osti, wvges-wells | Evaluate Li/Mg recovery potential from produced waters |
| `pnge-tutor` | All 22 computational skills + 6 data skills | Socratic tutor for PNGE/ChBE coursework |
| `pnge-pw-treatment` | usgs-produced-waters, epa-enviro, usgs-minerals, wri-aqueduct | Produced water treatment pathway assessment |
| `api-well-standards` | pnge-mechanics, wellbore-stability, wvges-wells, padep-wells | API 5CT/5C3 casing design, WV/PA regulatory requirements |
| `pnge-geopolitics` | usgs-minerals, comtrade-minerals, worldbank-energy, fred-prices, iea-open | Energy geopolitics, supply chains, resource dynamics |
| `pnge-gis-mapper` | Any spatial data skill | Generate interactive Leaflet.js HTML maps |

---

## Slash Commands (6)

| Command | Agent(s) Invoked | Typical Skills Used |
|---------|-----------------|---------------------|
| `/prospect` | `li-mg-prospector` | usgs-produced-waters, usgs-minerals, eia-data |
| `/formation-profile` | `li-mg-prospector` + `pnge-tutor` | usgs-produced-waters, macrostrat, wvges-wells |
| `/literature-review` | General research | openalex, usgs-pubs, doe-osti, crossref-doi |
| `/well-economics` | `pnge-tutor` + `li-mg-prospector` | rta-production, eia-data, fred-prices, usgs-minerals |
| `/completions-design` | `pnge-tutor` | frac-design, wellbore-stability, padep-wells, fracfocus |
| `/sustainability-profile` | `pnge-geopolitics` + `pnge-pw-treatment` | epa-ghgrp-subpartw, epa-enviro, wri-aqueduct, boem-offshore |

---

## API Key Summary

| Category | Count | Services |
|----------|-------|---------|
| Required keys (free) | 4 | EIA, NETL EDX, FRED, OpenEI |
| Optional keys (rate limits) | 2 | EPA api.data.gov, UN Comtrade |
| No key required | 22 | All other data skills |

See [`TOKENS.md`](TOKENS.md) for step-by-step key acquisition instructions.

---

## Data Quality and Bias Notes

| Dimension | Assessment |
|-----------|------------|
| **Brine geochemistry** | USGS Produced Waters DB v3.0 is the authoritative source. Coverage is excellent for Appalachian and Gulf Coast; sparser for Rocky Mountain and West Coast formations. |
| **Li/Mg economics** | USGS MCS data is authoritative but updated annually. Spot prices lag real-time markets; use FRED for current commodity pricing. |
| **State well data** | WVGES, PA DEP, and ODNR cover the Appalachian Basin. TX RRC and OK data are not currently in scope. |
| **Emissions data** | EPA GHGRP Subpart W covers facilities > 25,000 MTCO2e/yr; smaller operations are not captured. Self-reported; verification gaps exist. |
| **Industry self-reported** | FracFocus disclosures are self-reported. CBI exemptions mask some chemical identities. Open-FF (FracTracker) provides a cleaned research version. |
| **Geographic emphasis** | Appalachian Basin (WV/PA/OH) has the deepest coverage, reflecting WVU's research focus and data availability. |
| **Commercial data gap** | Enverus/DrillingInfo and IHS Markit are industry-standard but paywalled. Check WVU PNGE department for institutional licenses. |
| **Computational skills** | Equations are standard industry/academic formulations. Correlations (Standing, Beggs-Robinson, Hammerschmidt) have stated validity ranges — always verify inputs are within range. |
