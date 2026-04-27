# claude-pnge — Data Sources Reference

**Marketplace version:** v1.0.0
**Plugins:** 8 · **Skills:** 76 (43 data access, 33 computational) · **Agents:** 12 · **Commands:** 12
**Date:** 2026-04-27

Invoke each skill as `<plugin>:<skill>` — e.g., `pnge-core:eia-data`, `pnge-state-regulatory:tx-rrc`. See the plugin index below for the owning plugin of every skill.

---

## Plugin Index (which plugin owns each skill)

| Plugin | Skills |
|---|---|
| `pnge-core` | eia-data, usgs-produced-waters, usgs-minerals, pnge-literature, datacite-doi, pnge-visual-explainer |
| `pnge-federal-data` | usgs-earthquakes, usgs-waterdata, usgs-core-center, usgs-tnm, netl-edx, netl-carbon-storage, doe-geothermal, epa-regulatory, epa-treatability, boem-offshore, blm-mineral-records, fracfocus, nasa-earthdata, ejscreen-cejst-svi, wri-aqueduct |
| `pnge-state-regulatory` | wvges-wells, padep-wells, odnr-wells, tx-rrc, nm-ocd, nd-dmr, la-sonris, ar-aogc, ok-occ, calgem, co-ecmc, appalachia-mineral-parcels, ospar-discharges |
| `pnge-economics` | fred-prices, bls-data, bea-data, census-data, worldbank-energy, comtrade-minerals, iea-open |
| `pnge-patents` | patentsview |
| `pnge-well-engineering` | frac-design, wellbore-stability, petrophysics, perforation-design, completion-diagnostics, matrix-acidizing, stage-treatment-analysis, tubing-design, pnge-mechanics, artificial-lift, flow-assurance, surface-facilities, rta-production, well-test-analysis, nodal-analysis-multiphase, production-chemistry, well-integrity-barriers, petroleum-pvt, production-surveillance, pvt-report-review, integrity-log-review, kggs-well-logs, macrostrat |
| `pnge-geochem-pw` | phreeqc-geochem, nist-webbook, mass-energy-balance, tnav |
| `pnge-engineering-science` | fluid-mechanics, reaction-engineering, thermo-eos, heat-transfer, mass-transfer-separations, aqueous-chemistry-electrochem, materials-fracture-mechanics |

Authoritative mapping lives in [`scripts/ownership.tsv`](../scripts/ownership.tsv).

---

## Data Access Skills (43)

### Federal Agency Data (17)

| Skill | Source | URL | Key? | Primary Use |
|-------|--------|-----|------|-------------|
| `eia-data` | EIA Open Data API v2 | https://www.eia.gov/opendata/ | Yes (free) | U.S. energy statistics, gas/oil prices, storage, electricity |
| `usgs-produced-waters` | USGS Produced Waters Geochemical DB v3.0 | https://doi.org/10.5066/P9DSRCZJ | No | 115k+ brine samples with Li, Mg, TDS across U.S. basins |
| `usgs-minerals` | USGS Mineral Commodity Summaries | https://pubs.usgs.gov/periodicals/mcs2025/ | No | Annual production, reserves, pricing for 90+ commodities |
| `usgs-earthquakes` | USGS ComCat (FDSN) | https://earthquake.usgs.gov/fdsnws/event/1/ | No | Earthquake catalog, induced seismicity near injection wells |
| `usgs-waterdata` | USGS NWIS + Water Quality Portal | https://waterdata.usgs.gov/ | No | Streamflow, groundwater levels, water quality samples |
| `usgs-core-center` | USGS Core Research Center | https://www.usgs.gov/core-research-center | No | Physical core and cuttings inventory, ScienceBase holdings |
| `usgs-tnm` | USGS The National Map | https://apps.nationalmap.gov/ | No | DEM, hydrography, geologic maps, base layers |
| `netl-edx` | DOE NETL Energy Data eXchange (CKAN) | https://edx.netl.doe.gov/ | Yes (free) | DOE research datasets, ClaiMM critical minerals, CCS |
| `netl-carbon-storage` | NETL NATCARB Atlas v5 | https://netl.doe.gov/carbon-management/carbon-storage/natcarb-atlas | Yes (free, optional) | CCS storage capacity, sequestration projects |
| `doe-geothermal` | DOE GDR / OpenEI | https://gdr.openei.org/ | Yes (free) | Geothermal well data, temperature gradients, resources |
| `epa-regulatory` | EPA Envirofacts + ECHO + GHGRP (all subparts + Subpart W) | https://www.epa.gov/enviro/ | No (key optional) | UIC wells, permits, compliance, facility GHG, oilfield methane |
| `epa-treatability` | EPA Treatability Database | https://tdb.epa.gov/ | No | Water/wastewater treatment process performance data |
| `boem-offshore` | BOEM Federal Offshore Data | https://www.data.boem.gov/ | No | Federal OCS wells, leases, platforms, production |
| `blm-mineral-records` | BLM Mineral & Land Records (GIS) | https://blm-egis.maps.arcgis.com/ | No | Federal mineral ownership, lease status, land records |
| `fracfocus` | FracFocus Chemical Disclosure | https://fracfocus.org/ | No | HF chemical disclosures, frac fluid composition, proppant |
| `nasa-earthdata` | NASA Earthdata CMR | https://cmr.earthdata.nasa.gov/ | No (login for download) | Landsat, Sentinel, MODIS scene discovery |
| `ejscreen-cejst-svi` | EPA EJScreen + CEQ CEJST + CDC/ATSDR SVI | https://www.epa.gov/ejscreen | No | Environmental justice indicators, community vulnerability |

### State Regulatory Data (12)

| Skill | Source | URL | Key? | Primary Use |
|-------|--------|-----|------|-------------|
| `wvges-wells` | WV Geological & Economic Survey | http://www.wvgs.wvnet.edu/ | No | 153k+ WV wells, completions, formation tops, production |
| `padep-wells` | PA DEP Unconventional Well Registry (Socrata) | https://data.pa.gov/ | No | Marcellus/Utica permits, production, fracking disclosures |
| `odnr-wells` | Ohio DNR Oil and Gas Wells | https://ohiodnr.gov/oilandgas | No | Utica/Point Pleasant well data, permits, production |
| `tx-rrc` | Texas Railroad Commission | https://www.rrc.texas.gov/ | No | TX production, injection, permits, operator records |
| `nm-ocd` | New Mexico Oil Conservation Division | https://www.emnrd.nm.gov/ocd/ | No | NM Permian well, injection, and completion data |
| `nd-dmr` | North Dakota Dept of Mineral Resources | https://www.dmr.nd.gov/oilgas/ | No | Bakken well status, production, confidential well tracker |
| `la-sonris` | Louisiana SONRIS | https://sonris.com/ | No | LA Smackover wells, production, plugging records |
| `ar-aogc` | Arkansas Oil and Gas Commission | https://aogc.state.ar.us/ | No | Arkansas Smackover DLE activity and brine producers |
| `ok-occ` | Oklahoma Corporation Commission | https://oklahoma.gov/occ.html | No | Oklahoma wells, SWD disposal, induced-seismicity triggers |
| `calgem` | California CalGEM (former DOGGR) | https://www.conservation.ca.gov/calgem | No | CA oil/gas wells, San Joaquin/LA Basin, UIC status |
| `co-ecmc` | Colorado ECMC (former COGCC) | https://ecmc.state.co.us/ | No | CO DJ Basin wells, permits, spills, inspections |
| `appalachia-mineral-parcels` | WV/PA/OH Mineral Parcels (ArcGIS + ODNR + OGRIP) | (state ArcGIS services) | No | Tax-delinquent and dormant mineral parcel screening across WV, PA, OH |

### Global & Economic Data (9)

| Skill | Source | URL | Key? | Primary Use |
|-------|--------|-----|------|-------------|
| `fred-prices` | Federal Reserve FRED | https://fred.stlouisfed.org/ | Yes (free) | WTI/Brent crude, Henry Hub gas, commodity price history |
| `bls-data` | Bureau of Labor Statistics | https://www.bls.gov/developers/ | Optional (free) | PPI, CPI, oil/gas employment, wage series |
| `bea-data` | Bureau of Economic Analysis | https://apps.bea.gov/API/ | Yes (free) | GDP, regional income, county-level economic accounts |
| `census-data` | U.S. Census Bureau | https://api.census.gov/ | Yes (free) | ACS demographics, EJ context, county-level population |
| `worldbank-energy` | World Bank Open Data | https://data.worldbank.org/ | No | 200+ energy indicators by country, renewable capacity |
| `comtrade-minerals` | UN Comtrade | https://comtradeapi.un.org/ | Optional (free) | Li/Mg/Co trade flows, import/export by country |
| `iea-open` | IEA Free Datasets | https://www.iea.org/data-and-statistics | No | EV tracker, energy prices, NZE scenarios, CCUS, SDG7 |
| `wri-aqueduct` | WRI Aqueduct Water Risk | https://www.wri.org/aqueduct | No | Water stress scores by basin, corporate water risk |
| `ospar-discharges` | OSPAR Offshore Produced Water Discharges | https://www.ospar.org/ | No | North Sea produced water discharge benchmarks |

### Literature & Patents (5)

| Skill | Source | URL | Key? | Primary Use |
|-------|--------|-----|------|-------------|
| `pnge-literature` | OpenAlex + CrossRef + USGS Pubs + DOE OSTI (DOI dedup) | (federated) | No | Unified literature search across 4 adapters with DOI deduplication |
| `datacite-doi` | DataCite DOI Registry | https://api.datacite.org/ | No | Dataset and data-release DOIs (USGS, OSTI, Zenodo) |
| `kggs-well-logs` | KGS Wireline Log Repository | https://www.kgs.ku.edu/Magellan/Logs/ | No | LAS 2.0 wireline logs, digital formation evaluation |
| `macrostrat` | Macrostrat Formation Stratigraphy | https://macrostrat.org/ | No | Formation ages, lithologies, stratigraphic columns |
| `patentsview` | USPTO / PatentsView | https://patentsview.org/ | No | DLE patent landscape, assignee tracking, white-space analysis |

---

## Computational & Simulation Skills (33)

### Production & Completions Engineering (21)

| Skill | Key Capabilities | Primary WVU Courses |
|-------|-----------------|---------------------|
| `pnge-mechanics` | Statics, axial/beam stress, Lame thick-wall cylinders, Mohr's circle | PNGE 351, MAE 243 |
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
| `completion-diagnostics` | DFIT/minifrac, ISIP/closure, step-rate, cluster efficiency | PNGE 341 |
| `nodal-analysis-multiphase` | IPR/VLP matching, tubing/choke sensitivity, multiphase nodal | PNGE 361 |
| `production-chemistry` | Emulsions, incompatibility, squeeze design, cleanup, corrosion | PNGE 361 |
| `well-integrity-barriers` | SCP/annulus pressure triage, MIT interpretation, barrier review | PNGE 351 |
| `petroleum-pvt` | Bubble point, Rs, Bo, Bg, separator shrinkage, dropout screening | PNGE 321, PNGE 361 |
| `stage-treatment-analysis` | Stage CSV parsing, ISIP/screenout screening, cross-stage comparison | PNGE 341 |
| `production-surveillance` | SCADA/historian trend analysis, anomaly detection, candidate ranking | PNGE 361, PNGE 411 |
| `pvt-report-review` | PVT lab report extraction, QC, and black-oil input packaging | PNGE 321 |
| `integrity-log-review` | MIT, CBL/VDL, noise, temperature, annulus report review | PNGE 351 |

### Simulation & Reference Tools (5)

| Skill | Key Capabilities |
|-------|-----------------|
| `mass-energy-balance` | Material/energy balances, combustion, flash calculation (Rachford-Rice) |
| `nist-webbook` | NIST thermodynamic properties for methane, CO2, water, and light HCs |
| `tnav` | tNavigator-style reservoir simulation (black oil, PVT, decline, nodal) |
| `pnge-visual-explainer` | Generate self-contained HTML visualizations of PNGE concepts and data |
| `phreeqc-geochem` | PHREEQC brine speciation, saturation indices, mineral scaling prediction |

### Engineering Science Tutoring (7)

| Skill | Key Capabilities | WVU Course |
|-------|-----------------|-----------|
| `fluid-mechanics` | Colebrook-White, Darcy-Weisbach, Bernoulli, venturi, pump power | ChBE 311 |
| `reaction-engineering` | CSTR/PFR/batch design, Arrhenius, Levenspiel plot, adiabatic T rise | ChBE 321 |
| `thermo-eos` | Peng-Robinson/SRK EOS, Z-factor, fugacity, VLE, Rachford-Rice flash | ChBE 231 |
| `heat-transfer` | Conduction, convection, overall U, LMTD, NTU, transient heating/cooling | ChBE transport |
| `mass-transfer-separations` | Diffusion, mass-transfer coefficients, HTU/NTU, absorption, distillation | ChBE separations |
| `aqueous-chemistry-electrochem` | pH, buffers, alkalinity, hardness, Nernst, Faraday, water chemistry | ChBE / water |
| `materials-fracture-mechanics` | Stress intensity, fracture toughness, fatigue, Paris law, failure | MAE materials |

---

## API Key Summary

| Category | Count | Services |
|----------|-------|---------|
| Required keys (free) | 6 | EIA, NETL EDX, FRED, OpenEI (DOE GDR), BEA, Census |
| Optional keys (rate limits) | 4 | EPA api.data.gov, UN Comtrade, BLS, NETL Carbon Storage |
| No key required | 33 | All other data skills |

See [`TOKENS.md`](TOKENS.md) for step-by-step key acquisition instructions.

---

## Changes in v1.0.0 (marketplace restructure)

The monolithic `pnge` plugin was split into 8 themed plugins. No skills were added, removed, or renamed. `pnge-production` merged into `pnge-well-engineering`; `kggs-well-logs` and `macrostrat` moved from literature to well-engineering; `wri-aqueduct` moved to federal-data; `ospar-discharges` moved to state-regulatory. See [`CHANGELOG.md`](../CHANGELOG.md) for the full migration story.

---

## Changes Since v0.7.0

**Cut (4 skills):** `physics-mechanics`, `physics-em`, `diff-equations`, `opec-data` — removed as non-core to the plugin's PNGE + DLE focus.

**Merged (3 consolidations, 10 skills collapsed to 3):**
- `epa-regulatory` replaces `epa-enviro` + `epa-ghg` + `epa-ghgrp-subpartw` (4 intent modes: facility, UIC, compliance, emissions)
- `pnge-literature` replaces `usgs-pubs` + `doe-osti` + `openalex` + `crossref-doi` (4 adapters with DOI deduplication)
- `appalachia-mineral-parcels` replaces `wv-tax-minerals` + `pa-tax-minerals` + `oh-tax-minerals`

**Added (6 new skills):**
- `phreeqc-geochem` — PHREEQC brine speciation and mineral scaling prediction
- `datacite-doi` — DataCite DOI registry (complements `pnge-literature` for dataset DOIs)
- `ejscreen-cejst-svi` — EPA EJScreen + CEJST + CDC/ATSDR SVI for environmental justice context
- `ok-occ` — Oklahoma Corporation Commission (SWD disposal, seismicity)
- `calgem` — California CalGEM (former DOGGR)
- `co-ecmc` — Colorado ECMC (former COGCC)

Net: 66 skills -> 76 skills (+10).

---

## Data Quality and Bias Notes

| Dimension | Assessment |
|-----------|------------|
| **Brine geochemistry** | USGS Produced Waters DB v3.0 is the authoritative source. Coverage is excellent for Appalachian and Gulf Coast; sparser for Rocky Mountain and West Coast formations. |
| **Li/Mg economics** | USGS MCS data is authoritative but updated annually. Spot prices lag real-time markets; use FRED for current commodity pricing. |
| **State well data** | Eleven state regulators now covered (WV, PA, OH, TX, NM, ND, LA, AR, OK, CA, CO). Appalachian coverage remains deepest; `appalachia-mineral-parcels` consolidates WV/PA/OH mineral-parcel screening. |
| **Emissions data** | EPA GHGRP (via `epa-regulatory`) covers facilities > 25,000 MTCO2e/yr; smaller operations are not captured. Self-reported; verification gaps exist. |
| **Industry self-reported** | FracFocus disclosures are self-reported. CBI exemptions mask some chemical identities. Open-FF (FracTracker) provides a cleaned research version. |
| **Geochemical modeling** | `phreeqc-geochem` wraps PHREEQC with the default phreeqc.dat / pitzer.dat databases. For high-ionic-strength brines (Smackover, evaporite-hosted), prefer Pitzer; activity model choice materially changes saturation indices. |
| **Environmental justice** | `ejscreen-cejst-svi` aggregates three indicator systems with different methodologies; treat as screening-only, not definitive impact assessment. |
| **Literature dedup** | `pnge-literature` deduplicates across OpenAlex, CrossRef, USGS Pubs, and OSTI by DOI; records lacking a DOI (older USGS/OSTI reports) may appear in multiple adapters. |
| **Geographic emphasis** | Appalachian Basin (WV/PA/OH) retains the deepest coverage, reflecting WVU's research focus; the new state skills (OK, CA, CO) extend to the full Lower 48 onshore. |
| **Commercial data gap** | Enverus/DrillingInfo and IHS Markit are industry-standard but paywalled. Check WVU PNGE department for institutional licenses. |
| **Computational skills** | Equations are standard industry/academic formulations. Correlations (Standing, Beggs-Robinson, Hammerschmidt) have stated validity ranges — always verify inputs are within range. |
