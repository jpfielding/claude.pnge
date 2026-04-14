---
name: doctor
description: Plugin health check — test API keys, endpoint reachability, and skill status for all pnge data skills. Trigger: /doctor
---

Run a health check on all pnge plugin components. $ARGUMENTS

Test each skill category and report operational status.

## Credential Checks

Test that API keys exist and are non-empty for services that require them:

1. **EIA Open Data** — check `~/.config/eia/credentials` for `api_key=` line, then `$EIA_API_KEY` env var
2. **NETL EDX** — check `~/.config/netl-edx/credentials` for `api_key=` line, then `$NETL_EDX_API_KEY` env var
3. **EPA api.data.gov** — check `~/.config/epa/credentials` for `api_key=` line, then `$EPA_API_KEY` env var

For each, report: FOUND (file), FOUND (env), or MISSING with signup URL.

## Endpoint Reachability

Test that each data API responds to a lightweight probe request using `curl -s -o /dev/null -w "%{http_code}"`:

| Skill | Probe URL | Expected |
|-------|-----------|----------|
| pnge:eia-data | `https://api.eia.gov/v2/?api_key=KEY` | 200 |
| pnge:usgs-produced-waters | `https://www.sciencebase.gov/catalog/item/65b6d616d34e46cd33b3690e?format=json` | 200 |
| pnge:usgs-minerals | `https://data.usgs.gov/datacatalog/api/3/action/status_show` | 200 |
| pnge:netl-edx | `https://edx.netl.doe.gov/api/3/action/status_show` | 200 |
| pnge:wvges-wells | `http://atlas.wvgs.wvnet.edu/arcgis/rest/services/OilGas/WVOG/MapServer?f=json` | 200 |
| pnge:boem-offshore | `https://gis.boem.gov/arcgis/rest/services/BOEM_BSEE/MMC_Layers/MapServer?f=json` | 200 |
| pnge:epa-enviro | `https://enviro.epa.gov/enviro/efservice/UIC_WELL/STATE_CODE/WV/rows/0:1/JSON` | 200 |
| pnge:usgs-pubs | `https://pubs.er.usgs.gov/pubs-services/publication?q=lithium&page_size=1` | 200 |
| pnge:doe-osti | `https://www.osti.gov/api/v1/records?q=lithium&rows=1` | 200 |
| pnge:usgs-earthquakes | `https://earthquake.usgs.gov/fdsnws/event/1/count?format=text&minmagnitude=3` | 200 |
| pnge:fred-prices | `https://api.stlouisfed.org/fred/series?series_id=GDP&file_type=json&api_key=KEY` | 200 |
| pnge:openalex | `https://api.openalex.org/works?search=lithium&per_page=1` | 200 |
| pnge:crossref-doi | `https://api.crossref.org/works?query=lithium&rows=1` | 200 |
| pnge:macrostrat | `https://macrostrat.org/api/v2/units?strat_name=Marcellus&response=short` | 200 |
| pnge:usgs-waterdata | `https://waterservices.usgs.gov/nwis/site/?format=rdb&stateCd=wv&siteType=GW&hasDataTypeCd=qw&parameterCd=00095&recCount=1` | 200 |

## Status Report

Structure the output as:

## Plugin Health Check

**Date:** [current date and time]

### Credential Status
| Service | Location | Status | Action |
|---------|----------|--------|--------|
| EIA | ~/.config/eia/credentials | OK / MISSING | [signup URL if missing] |
| NETL EDX | ~/.config/netl-edx/credentials | OK / MISSING | |
| EPA | ~/.config/epa/credentials | OK / MISSING | |

### Endpoint Status
| Skill | HTTP Status | Latency (ms) | Status |
|-------|-------------|-------------|--------|
| pnge:eia-data | 200 | 342 | OK |
| pnge:usgs-produced-waters | 200 | 567 | OK |
| ... | | | |

### Summary
- **Fully operational:** X of Y skills
- **Degraded (missing key):** list
- **Unreachable:** list
- **Overall plugin status:** HEALTHY / DEGRADED / CRITICAL

### Remediation
For each non-OK skill, provide the specific fix:
- Missing credential: signup URL and storage path
- Unreachable endpoint: suggest checking network, note if the service has known downtime
- Unexpected HTTP status: interpret the status code and suggest action
