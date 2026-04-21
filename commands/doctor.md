---
name: doctor
description: Plugin health check — probe API credentials and endpoint reachability for every claude-pnge data-access skill, then summarize pass/fail/skipped with remediation hints. Trigger phrases - /doctor, plugin health check, are my api keys working, test pnge skills, check endpoint status.
---

Run a comprehensive health check on the claude-pnge plugin. $ARGUMENTS

The /doctor command verifies three things for every data-access skill:

1. **Credential presence** — for skills that require a key, is a key available either in `~/.config/<service>/credentials` or in the documented environment variable?
2. **Endpoint reachability** — does a lightweight probe URL return an HTTP status indicating the service is up?
3. **Skill inventory** — does each skill directory exist under `skills/`?

Skills that are **purely computational** (no network endpoint) are listed in the inventory but not probed.
Skills whose canonical endpoints are intermittent, geofenced, bot-blocked, or require session cookies are marked **not network-testable** — these must be verified manually in a browser.

---

## Execution

Use the `Bash` tool to run every probe below. Keep the per-request timeout at 5 seconds (`curl -m 5`) so one stalled service cannot freeze the whole check. Follow redirects with `-L`. Send a normal User-Agent so gateways that block `curl/*` UAs don't return false negatives.

Standard probe pattern:

```bash
probe() {
  local name="$1" url="$2"
  local code
  code=$(curl -s -o /dev/null -w "%{http_code}" -m 5 -L \
    -A "Mozilla/5.0 (claude-pnge /doctor)" "$url")
  if [ "$code" = "200" ] || [ "$code" = "400" ] || [ "$code" = "403" ]; then
    echo "PASS  $name  (HTTP $code)"
  else
    echo "FAIL  $name  (HTTP $code — $url)"
  fi
}
```

Why 400/403 count as PASS for *some* probes: endpoints like EIA v2, FRED, and BLS reject un-authenticated requests with 400/403. That response still proves the host is alive and the TLS path is healthy. These are flagged explicitly in the probe tables below with `auth-reject OK`. For every other probe, only HTTP 200 counts.

---

## 1. Credential Preflight

Check the credential file first, then the environment variable. Report each as `FOUND (file)`, `FOUND (env)`, or `MISSING` — and if missing, point to the corresponding section of `docs/TOKENS.md`.

```bash
creds() {
  local service="$1" envvar="$2" file="$HOME/.config/$3/credentials"
  if [ -f "$file" ] && grep -q '^api_key=' "$file" 2>/dev/null; then
    local val
    val=$(grep '^api_key=' "$file" | head -1 | cut -d= -f2)
    if [ -n "$val" ]; then echo "FOUND (file) $service"; return 0; fi
  fi
  if [ -n "${!envvar}" ]; then echo "FOUND (env)  $service  (\$$envvar)"; return 0; fi
  echo "MISSING      $service  (see docs/TOKENS.md#${3})"
  return 1
}

creds "EIA Open Data"        EIA_API_KEY          eia
creds "NETL EDX"             NETL_EDX_API_KEY     netl-edx
creds "EPA api.data.gov"     EPA_API_KEY          epa
creds "FRED (St. Louis Fed)" FRED_API_KEY         fred
creds "BEA"                  BEA_API_KEY          bea
creds "US Census"            CENSUS_API_KEY       census
creds "OpenEI / GDR"         OPENEI_API_KEY       openei
creds "BLS (optional)"       BLS_API_KEY          bls
creds "UN Comtrade (optional)" COMTRADE_API_KEY   comtrade
creds "NASA Earthdata (optional)" EARTHDATA_TOKEN earthdata
```

Required for basic plugin function: EIA, NETL EDX, FRED, BEA, Census, OpenEI.
Optional (public tier works without a key, keys only raise rate limits): EPA, BLS, Comtrade, NASA Earthdata.
No key at all: every other skill.

---

## 2. Endpoint Probes

### 2a. Federal / multi-state data skills

| Skill | Probe URL | Expected | Notes |
|-------|-----------|----------|-------|
| pnge:eia-data | `https://api.eia.gov/v2/` | 200 with key, 403 auth-reject without | 403 PASS |
| pnge:usgs-produced-waters | `https://www.sciencebase.gov/catalog/item/64fa1e71d34ed30c2054ea11?format=json` | 200 | v3.0 item (verified live) |
| pnge:usgs-minerals | `https://data.usgs.gov/datacatalog/` | 200 | API endpoint 404s, portal is live |
| pnge:usgs-earthquakes | `https://earthquake.usgs.gov/fdsnws/event/1/count?format=text&minmagnitude=3` | 200 | |
| pnge:usgs-waterdata | `https://waterservices.usgs.gov/nwis/site/?format=rdb&stateCd=wv&siteType=GW&hasDataTypeCd=qw&parameterCd=00095&siteStatus=all` | 200 | |
| pnge:usgs-core-center | `https://www.usgs.gov/core-research-center` | not network-testable | Cloudflare UA challenge — verify manually |
| pnge:usgs-tnm | `https://tnmaccess.nationalmap.gov/api/v1/products?datasets=National+Map` | 200 | |
| pnge:netl-edx | `https://edx.netl.doe.gov/api/3/action/status_show` | 200 | |
| pnge:netl-carbon-storage | `https://edx.netl.doe.gov/group/carbon-storage-open-database` | 200 | |
| pnge:doe-geothermal | `https://gdr.openei.org/` | 200 | GDR root; dataset API needs OpenEI key |
| pnge:epa-regulatory | `https://data.epa.gov/efservice/TRI_FACILITY/rows/0:1/JSON` | 200 | `UIC_WELL` removed — permanently dead |
| pnge:epa-treatability | `https://tdb.epa.gov/tdb/home` | not network-testable | ORD endpoints block `curl` UAs — verify manually |
| pnge:boem-offshore | `https://gis.boem.gov/arcgis/rest/services/BOEM_BSEE/MMC_Layers/MapServer?f=json` | 200 | |
| pnge:blm-mineral-records | `https://glorecords.blm.gov/` | 200 | |
| pnge:fracfocus | `https://www.fracfocusdata.org/DisclosuresSearch/` | 200 | API proper is session-based; portal probe is the canary |
| pnge:nasa-earthdata | `https://cmr.earthdata.nasa.gov/search/health` | 200 | |
| pnge:phreeqc-geochem | — | computational | Skill wraps local PHREEQC; no endpoint |
| pnge:ejscreen-cejst-svi | `https://www.census.gov/programs-surveys/geography.html` | not network-testable | EJScreen/CEJST domains geofence curl — verify manually at https://screeningtool.geoplatform.gov/ |

### 2b. State oil & gas regulator skills

| Skill | Probe URL | Expected | Notes |
|-------|-----------|----------|-------|
| pnge:wvges-wells | `https://tagis.dep.wv.gov/arcgis/rest/services/WVDEP_enterprise/oog/MapServer?f=json` | 200 | Use WVDEP; legacy `atlas.wvgs.wvnet.edu` intermittent |
| pnge:padep-wells | `https://www.pa.gov/agencies/dep/programs-and-services/oil-and-gas/oil-and-gas-mapping.html` | not network-testable | PA DEP GIS endpoints geofence/TLS-block curl — verify at https://www.depgis.state.pa.us/PaOilAndGasMapping/ |
| pnge:odnr-wells | `https://gis.ohiodnr.gov/arcgis/rest/services/OIL_GAS/WellsAndPermits/MapServer?f=json` | 200 | |
| pnge:tx-rrc | `https://www.rrc.texas.gov/resource-center/research/data-sets-available-for-download/` | 200 | RRC has no REST API; bulk downloads only |
| pnge:nm-ocd | `https://wwwapps.emnrd.nm.gov/ocd/ocdpermitting/` | 200 | |
| pnge:nd-dmr | `https://www.dmr.nd.gov/oilgas/` | 200 | |
| pnge:la-sonris | `https://sonris.com/` | 200 | SONRIS Lite (`sonlite.dnr.state.la.us`) returns 401 on root; probe main portal |
| pnge:ar-aogc | `https://www.aogc.state.ar.us/welcome.aspx` | not network-testable | AOGC returns 403 to automated clients — verify manually |
| pnge:ok-occ | `https://www.occ.ok.gov/` | 200 | occeweb.com blocks non-browser UAs |
| pnge:calgem | `https://www.conservation.ca.gov/calgem` | 200 | WellSTAR public lookup has no stable anon URL |
| pnge:co-ecmc | `https://ecmc.state.co.us/` | 200 | ArcGIS subdomain intermittent |
| pnge:appalachia-mineral-parcels | `https://mapwv.gov/parcel/` | 200 | WV only; PA/OH parcels are county-level, not network-testable |

### 2c. Economic / global data skills

| Skill | Probe URL | Expected | Notes |
|-------|-----------|----------|-------|
| pnge:fred-prices | `https://api.stlouisfed.org/fred/series?series_id=GDP&api_key=invalid&file_type=json` | 400 | 400 auth-reject PASS — proves host live |
| pnge:bls-data | `https://api.bls.gov/publicAPI/v2/surveys` | 200 | |
| pnge:bea-data | `https://apps.bea.gov/api/data/?UserID=TEST&method=GetDataSetList&ResultFormat=JSON` | 200 | Returns 200 with an error body for bad UserID |
| pnge:census-data | `https://www.census.gov/data/developers.html` | not network-testable | `api.census.gov` geofences/blocks this test environment — verify manually |
| pnge:worldbank-energy | `https://api.worldbank.org/v2/country/USA/indicator/EG.USE.ELEC.KH.PC?format=json` | 200 | |
| pnge:comtrade-minerals | `https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=842&period=2022&cmdCode=250300&flowCode=X` | 200 | Public tier; rate-limited |
| pnge:iea-open | `https://www.iea.org/data-and-statistics` | 200 | IEA has no public REST API |
| pnge:wri-aqueduct | `https://www.wri.org/applications/aqueduct/water-risk-atlas/` | 200 | |
| pnge:ospar-discharges | `https://odims.ospar.org/` | 200 | Use ODIMS; `odata.ospar.org` is intermittent |

### 2d. Literature / bibliographic skills

| Skill | Probe URL | Expected | Notes |
|-------|-----------|----------|-------|
| pnge:pnge-literature (USGS Pubs adapter) | `https://pubs.er.usgs.gov/pubs-services/publication?q=lithium&page_size=1` | 200 | |
| pnge:pnge-literature (DOE OSTI adapter) | `https://www.osti.gov/api/v1/records?q=lithium&rows=1` | 200 | |
| pnge:pnge-literature (OpenAlex adapter) | `https://api.openalex.org/works?search=lithium&per-page=1` | 200 | |
| pnge:pnge-literature (CrossRef adapter) | `https://api.crossref.org/works?query=lithium&rows=1` | 200 | |
| pnge:datacite-doi | `https://api.datacite.org/heartbeat` | 200 | Official heartbeat endpoint |
| pnge:kggs-well-logs | `https://www.kgs.ku.edu/Magellan/Qualified/index.html` | 200 | |
| pnge:macrostrat | `https://macrostrat.org/api/v2/units?strat_name=Marcellus&response=short` | 200 | |
| pnge:patentsview | `https://search.patentsview.org/` | not network-testable | PatentsView v2 requires API key + header auth; v1 retired (410). Verify manually via signed request |

### 2e. Computational skills (no endpoint)

These skills bundle algorithms, references, or local tooling. They have nothing to probe over the network. Confirm only that the skill directory and `SKILL.md` exist:

- pnge:phreeqc-geochem (wraps local PHREEQC binary)

For each listed skill, run:

```bash
for s in phreeqc-geochem; do
  if [ -f "skills/$s/SKILL.md" ]; then echo "PASS  $s  (SKILL.md present)"
  else echo "FAIL  $s  (SKILL.md missing)"; fi
done
```

---

## 3. Output Format

Render the final report as a single markdown document in this exact structure:

### Plugin Health Check

**Date:** (ISO-8601 timestamp)
**Plugin:** claude-pnge
**Probes run:** N

### Credential Status

| Service | Required? | Source | Status |
|---------|-----------|--------|--------|
| EIA | yes | `~/.config/eia/credentials` or `$EIA_API_KEY` | FOUND / MISSING |
| NETL EDX | yes | `~/.config/netl-edx/credentials` or `$NETL_EDX_API_KEY` | FOUND / MISSING |
| FRED | yes | `~/.config/fred/credentials` or `$FRED_API_KEY` | FOUND / MISSING |
| BEA | yes | `~/.config/bea/credentials` or `$BEA_API_KEY` | FOUND / MISSING |
| Census | yes | `~/.config/census/credentials` or `$CENSUS_API_KEY` | FOUND / MISSING |
| OpenEI / GDR | yes | `~/.config/openei/credentials` or `$OPENEI_API_KEY` | FOUND / MISSING |
| EPA | optional | `~/.config/epa/credentials` or `$EPA_API_KEY` | FOUND / MISSING |
| BLS | optional | `~/.config/bls/credentials` or `$BLS_API_KEY` | FOUND / MISSING |
| Comtrade | optional | `~/.config/comtrade/credentials` or `$COMTRADE_API_KEY` | FOUND / MISSING |
| NASA Earthdata | optional | `~/.config/earthdata/credentials` or `$EARTHDATA_TOKEN` | FOUND / MISSING |

### Endpoint Status (federal)

| Skill | HTTP | Status |
|-------|------|--------|
| pnge:eia-data | 403 | PASS (auth-reject; key checked separately) |
| pnge:usgs-produced-waters | 200 | PASS |
| pnge:usgs-minerals | 200 | PASS |
| pnge:usgs-earthquakes | 200 | PASS |
| pnge:usgs-waterdata | 200 | PASS |
| pnge:usgs-core-center | — | SKIP (not network-testable) |
| pnge:usgs-tnm | 200 | PASS |
| pnge:netl-edx | 200 | PASS |
| pnge:netl-carbon-storage | 200 | PASS |
| pnge:doe-geothermal | 200 | PASS |
| pnge:epa-regulatory | 200 | PASS |
| pnge:epa-treatability | — | SKIP (not network-testable) |
| pnge:boem-offshore | 200 | PASS |
| pnge:blm-mineral-records | 200 | PASS |
| pnge:fracfocus | 200 | PASS |
| pnge:nasa-earthdata | 200 | PASS |
| pnge:ejscreen-cejst-svi | — | SKIP (not network-testable) |
| pnge:phreeqc-geochem | — | SKIP (computational, no endpoint) |

### Endpoint Status (state)

| Skill | HTTP | Status |
|-------|------|--------|
| pnge:wvges-wells | 200 | PASS |
| pnge:padep-wells | — | SKIP (not network-testable) |
| pnge:odnr-wells | 200 | PASS |
| pnge:tx-rrc | 200 | PASS |
| pnge:nm-ocd | 200 | PASS |
| pnge:nd-dmr | 200 | PASS |
| pnge:la-sonris | 200 | PASS |
| pnge:ar-aogc | — | SKIP (not network-testable) |
| pnge:ok-occ | 200 | PASS |
| pnge:calgem | 200 | PASS |
| pnge:co-ecmc | 200 | PASS |
| pnge:appalachia-mineral-parcels | 200 | PASS |

### Endpoint Status (economic / global)

| Skill | HTTP | Status |
|-------|------|--------|
| pnge:fred-prices | 400 | PASS (auth-reject) |
| pnge:bls-data | 200 | PASS |
| pnge:bea-data | 200 | PASS |
| pnge:census-data | — | SKIP (not network-testable) |
| pnge:worldbank-energy | 200 | PASS |
| pnge:comtrade-minerals | 200 | PASS |
| pnge:iea-open | 200 | PASS |
| pnge:wri-aqueduct | 200 | PASS |
| pnge:ospar-discharges | 200 | PASS |

### Endpoint Status (literature)

| Skill | HTTP | Status |
|-------|------|--------|
| pnge:pnge-literature (USGS Pubs) | 200 | PASS |
| pnge:pnge-literature (DOE OSTI) | 200 | PASS |
| pnge:pnge-literature (OpenAlex) | 200 | PASS |
| pnge:pnge-literature (CrossRef) | 200 | PASS |
| pnge:datacite-doi | 200 | PASS |
| pnge:kggs-well-logs | 200 | PASS |
| pnge:macrostrat | 200 | PASS |
| pnge:patentsview | — | SKIP (not network-testable) |

### Summary

- **Probes passing:** X of N
- **Probes failing:** list with URL and HTTP code
- **Probes skipped (not network-testable):** list
- **Credentials missing:** list of services
- **Overall plugin status:** one of HEALTHY / DEGRADED / CRITICAL
  - HEALTHY   = no failing probes, no required credentials missing
  - DEGRADED  = one or more optional items missing, core skills still usable
  - CRITICAL  = one or more required credentials missing OR ≥ 3 probes failing

---

## 4. Remediation Hints

For every MISSING credential or FAIL probe, emit a concrete one-liner. Template:

- **EIA key missing** → sign up free at https://www.eia.gov/opendata/register.php, store as `~/.config/eia/credentials` with `api_key=...`. See docs/TOKENS.md#eia.
- **NETL EDX key missing** → sign up at https://edx.netl.doe.gov/, reveal key from user profile, store as `~/.config/netl-edx/credentials`. See docs/TOKENS.md#netl-edx.
- **EPA key missing** → sign up at https://api.data.gov/signup/, store as `~/.config/epa/credentials`. See docs/TOKENS.md#epa.
- **FRED key missing** → sign up at https://fred.stlouisfed.org/docs/api/api_key.html. See docs/TOKENS.md#fred.
- **BEA key missing** → sign up at https://apps.bea.gov/API/signup/. See docs/TOKENS.md#bea.
- **Census key missing** → request at https://api.census.gov/data/key_signup.html. See docs/TOKENS.md#census.
- **OpenEI key missing** → sign up at https://openei.org/services/api/signup/. See docs/TOKENS.md#openei.
- **BLS key missing (optional)** → https://data.bls.gov/registrationEngine/. See docs/TOKENS.md#bls.
- **Comtrade key missing (optional)** → https://comtradeplus.un.org/. See docs/TOKENS.md#comtrade.
- **NASA Earthdata token missing (optional)** → https://urs.earthdata.nasa.gov/. See docs/TOKENS.md#earthdata.
- **Endpoint 4xx / 5xx** → most federal APIs experience brief outages during weekday morning ETL windows (07:00–09:00 ET). Re-run /doctor in 15 minutes before filing a bug.
- **Endpoint HTTP 000** → DNS lookup or TLS handshake failed. Usually a local network / proxy / VPN issue; confirm `curl -v` from the same shell.
- **Endpoint SKIPPED (not network-testable)** → open the URL in a browser. If the page renders, consider the skill healthy. Cloudflare/Incapsula shields and geofences on several US state / federal sites return valid responses to real browsers but reject `curl`-style clients.

---

## 5. Reference: Go implementation

For callers who prefer a compiled probe runner, the logic collapses to ~80 lines of stdlib Go. The skill `skills/` directory holds the catalog; the script reads it, issues the probes in parallel, and prints the same markdown tables shown above.

```go
package main

import (
    "context"
    "fmt"
    "net/http"
    "os"
    "path/filepath"
    "strings"
    "sync"
    "time"
)

type probe struct {
    skill, url string
    // passCodes lists HTTP status codes that count as PASS. Most probes
    // are {200}; auth-reject probes are {200, 400, 403}.
    passCodes []int
    skip      string // non-empty = not network-testable, explain why
}

var catalog = []probe{
    {skill: "pnge:eia-data", url: "https://api.eia.gov/v2/", passCodes: []int{200, 403}},
    {skill: "pnge:usgs-produced-waters", url: "https://www.sciencebase.gov/catalog/item/64fa1e71d34ed30c2054ea11?format=json", passCodes: []int{200}},
    {skill: "pnge:usgs-minerals", url: "https://data.usgs.gov/datacatalog/", passCodes: []int{200}},
    {skill: "pnge:usgs-earthquakes", url: "https://earthquake.usgs.gov/fdsnws/event/1/count?format=text&minmagnitude=3", passCodes: []int{200}},
    {skill: "pnge:usgs-waterdata", url: "https://waterservices.usgs.gov/nwis/site/?format=rdb&stateCd=wv&siteType=GW&hasDataTypeCd=qw&parameterCd=00095&siteStatus=all", passCodes: []int{200}},
    {skill: "pnge:usgs-tnm", url: "https://tnmaccess.nationalmap.gov/api/v1/products?datasets=National+Map", passCodes: []int{200}},
    {skill: "pnge:netl-edx", url: "https://edx.netl.doe.gov/api/3/action/status_show", passCodes: []int{200}},
    {skill: "pnge:netl-carbon-storage", url: "https://edx.netl.doe.gov/group/carbon-storage-open-database", passCodes: []int{200}},
    {skill: "pnge:doe-geothermal", url: "https://gdr.openei.org/", passCodes: []int{200}},
    {skill: "pnge:epa-regulatory", url: "https://data.epa.gov/efservice/TRI_FACILITY/rows/0:1/JSON", passCodes: []int{200}},
    {skill: "pnge:boem-offshore", url: "https://gis.boem.gov/arcgis/rest/services/BOEM_BSEE/MMC_Layers/MapServer?f=json", passCodes: []int{200}},
    {skill: "pnge:blm-mineral-records", url: "https://glorecords.blm.gov/", passCodes: []int{200}},
    {skill: "pnge:fracfocus", url: "https://www.fracfocusdata.org/DisclosuresSearch/", passCodes: []int{200}},
    {skill: "pnge:nasa-earthdata", url: "https://cmr.earthdata.nasa.gov/search/health", passCodes: []int{200}},
    {skill: "pnge:wvges-wells", url: "https://tagis.dep.wv.gov/arcgis/rest/services/WVDEP_enterprise/oog/MapServer?f=json", passCodes: []int{200}},
    {skill: "pnge:odnr-wells", url: "https://gis.ohiodnr.gov/arcgis/rest/services/OIL_GAS/WellsAndPermits/MapServer?f=json", passCodes: []int{200}},
    {skill: "pnge:tx-rrc", url: "https://www.rrc.texas.gov/resource-center/research/data-sets-available-for-download/", passCodes: []int{200}},
    {skill: "pnge:nm-ocd", url: "https://wwwapps.emnrd.nm.gov/ocd/ocdpermitting/", passCodes: []int{200}},
    {skill: "pnge:nd-dmr", url: "https://www.dmr.nd.gov/oilgas/", passCodes: []int{200}},
    {skill: "pnge:la-sonris", url: "https://sonris.com/", passCodes: []int{200}},
    {skill: "pnge:ok-occ", url: "https://www.occ.ok.gov/", passCodes: []int{200}},
    {skill: "pnge:calgem", url: "https://www.conservation.ca.gov/calgem", passCodes: []int{200}},
    {skill: "pnge:co-ecmc", url: "https://ecmc.state.co.us/", passCodes: []int{200}},
    {skill: "pnge:appalachia-mineral-parcels", url: "https://mapwv.gov/parcel/", passCodes: []int{200}},
    {skill: "pnge:fred-prices", url: "https://api.stlouisfed.org/fred/series?series_id=GDP&api_key=invalid&file_type=json", passCodes: []int{200, 400}},
    {skill: "pnge:bls-data", url: "https://api.bls.gov/publicAPI/v2/surveys", passCodes: []int{200}},
    {skill: "pnge:bea-data", url: "https://apps.bea.gov/api/data/?UserID=TEST&method=GetDataSetList&ResultFormat=JSON", passCodes: []int{200}},
    {skill: "pnge:worldbank-energy", url: "https://api.worldbank.org/v2/country/USA/indicator/EG.USE.ELEC.KH.PC?format=json", passCodes: []int{200}},
    {skill: "pnge:comtrade-minerals", url: "https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=842&period=2022&cmdCode=250300&flowCode=X", passCodes: []int{200}},
    {skill: "pnge:iea-open", url: "https://www.iea.org/data-and-statistics", passCodes: []int{200}},
    {skill: "pnge:wri-aqueduct", url: "https://www.wri.org/applications/aqueduct/water-risk-atlas/", passCodes: []int{200}},
    {skill: "pnge:ospar-discharges", url: "https://odims.ospar.org/", passCodes: []int{200}},
    {skill: "pnge:pnge-literature (USGS Pubs)", url: "https://pubs.er.usgs.gov/pubs-services/publication?q=lithium&page_size=1", passCodes: []int{200}},
    {skill: "pnge:pnge-literature (DOE OSTI)", url: "https://www.osti.gov/api/v1/records?q=lithium&rows=1", passCodes: []int{200}},
    {skill: "pnge:pnge-literature (OpenAlex)", url: "https://api.openalex.org/works?search=lithium&per-page=1", passCodes: []int{200}},
    {skill: "pnge:pnge-literature (CrossRef)", url: "https://api.crossref.org/works?query=lithium&rows=1", passCodes: []int{200}},
    {skill: "pnge:datacite-doi", url: "https://api.datacite.org/heartbeat", passCodes: []int{200}},
    {skill: "pnge:kggs-well-logs", url: "https://www.kgs.ku.edu/Magellan/Qualified/index.html", passCodes: []int{200}},
    {skill: "pnge:macrostrat", url: "https://macrostrat.org/api/v2/units?strat_name=Marcellus&response=short", passCodes: []int{200}},
    {skill: "pnge:usgs-core-center", skip: "Cloudflare UA challenge"},
    {skill: "pnge:epa-treatability", skip: "ORD UA block"},
    {skill: "pnge:ejscreen-cejst-svi", skip: "EJScreen/CEJST geofenced"},
    {skill: "pnge:padep-wells", skip: "PA DEP GIS UA/TLS block"},
    {skill: "pnge:ar-aogc", skip: "AOGC UA block"},
    {skill: "pnge:census-data", skip: "api.census.gov intermittently geofenced"},
    {skill: "pnge:patentsview", skip: "Requires API key + header auth"},
    {skill: "pnge:phreeqc-geochem", skip: "Computational skill; no endpoint"},
}

func main() {
    client := &http.Client{Timeout: 5 * time.Second}
    var wg sync.WaitGroup
    results := make([]string, len(catalog))
    for i, p := range catalog {
        if p.skip != "" {
            results[i] = fmt.Sprintf("SKIP  %s  (%s)", p.skill, p.skip)
            continue
        }
        wg.Add(1)
        go func(i int, p probe) {
            defer wg.Done()
            ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
            defer cancel()
            req, err := http.NewRequestWithContext(ctx, "GET", p.url, nil)
            if err != nil {
                results[i] = fmt.Sprintf("FAIL  %s  (bad url: %v)", p.skill, err)
                return
            }
            req.Header.Set("User-Agent", "Mozilla/5.0 (claude-pnge /doctor)")
            resp, err := client.Do(req)
            if err != nil {
                results[i] = fmt.Sprintf("FAIL  %s  (request error: %v)", p.skill, err)
                return
            }
            defer resp.Body.Close()
            for _, c := range p.passCodes {
                if resp.StatusCode == c {
                    results[i] = fmt.Sprintf("PASS  %s  (HTTP %d)", p.skill, resp.StatusCode)
                    return
                }
            }
            results[i] = fmt.Sprintf("FAIL  %s  (HTTP %d — %s)", p.skill, resp.StatusCode, p.url)
        }(i, p)
    }
    wg.Wait()
    for _, r := range results { fmt.Println(r) }

    // Also verify each skill directory exists.
    pluginRoot, _ := os.Getwd()
    entries, _ := os.ReadDir(filepath.Join(pluginRoot, "skills"))
    fmt.Printf("\nSkill directories present: %d\n", len(entries))
    for _, e := range entries {
        if !e.IsDir() { continue }
        skillMd := filepath.Join(pluginRoot, "skills", e.Name(), "SKILL.md")
        if _, err := os.Stat(skillMd); err != nil {
            fmt.Printf("  MISSING SKILL.md: %s\n", e.Name())
        }
    }

    _ = strings.TrimSpace // silence lint if unused
}
```

Compile and run:

```bash
go run ./scripts/doctor/main.go
```

The shell version in §1–2 and the Go runner in §5 produce the same tables; pick whichever fits the workflow.

---

## 6. Notes on Probe Design

- Every probe URL in §2 was verified live at plugin build time. If a probe flips to failing after release, **fix the URL — do not suppress the failure**. The point of /doctor is to catch upstream drift.
- Probes deliberately request the smallest payload each API supports (`rows=1`, `max=1`, `page_size=1`, `count` endpoints, `status_show` heartbeats). No probe should transfer more than a few KB.
- 400/403 as PASS is only acceptable for probes annotated `auth-reject OK`. Do not generalize this to other probes — a 403 from `data.epa.gov` is a real failure, not an auth rejection.
- When adding a new data-access skill to the plugin, add its probe here first, confirm the URL returns 200 with `curl`, and only then ship the skill. Skills without a probe entry count as untested.
- Skills marked *not network-testable* are not second-class citizens; they just require an in-browser sanity check. The doctor report treats them as SKIPPED, not FAILED.
- ScienceBase note: the previously-documented item id `65b6d616d34e46cd33b3690e` is **404 at the time of writing**. Current USGS Produced Waters v3 item ids verified live: `64fa1e71d34ed30c2054ea11` (v3.0) and `59d25d63e4b05fe04cc235f9` (v2 legacy). The probe uses the v3.0 id.
