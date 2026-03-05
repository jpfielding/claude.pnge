# API Token Acquisition Guide

This guide covers every credential needed by the claude-pnge plugin.
Four of the twenty data skills require API keys. Two more accept optional
keys for higher rate limits. The remaining fourteen use public endpoints
with no authentication.

---

## Table of Contents

- [Quick Setup](#quick-setup)
- [1. EIA Open Data API](#1-eia-open-data-api)
- [2. NETL Energy Data eXchange (EDX)](#2-netl-energy-data-exchange-edx)
- [3. FRED (Federal Reserve Economic Data)](#3-fred-federal-reserve-economic-data)
- [4. OpenEI (DOE Geothermal Data Repository)](#4-openei-doe-geothermal-data-repository)
- [5. EPA api.data.gov (optional)](#5-epa-apidatagov-optional)
- [6. UN Comtrade (optional)](#6-un-comtrade-optional)
- [Services With No Key Required](#services-with-no-key-required)
- [Verification](#verification)
- [Troubleshooting](#troubleshooting)

---

## Quick Setup

After obtaining all keys, run this block to store them. Replace
each `YOUR_*_KEY` placeholder with the actual key value.

```bash
# Create all credential directories
mkdir -p ~/.config/eia ~/.config/netl-edx ~/.config/fred ~/.config/openei
chmod 700 ~/.config/eia ~/.config/netl-edx ~/.config/fred ~/.config/openei

# Store required keys (replace YOUR_KEY_HERE with actual values)
echo "api_key=YOUR_EIA_KEY" > ~/.config/eia/credentials
echo "api_key=YOUR_NETL_KEY" > ~/.config/netl-edx/credentials
echo "api_key=YOUR_FRED_KEY" > ~/.config/fred/credentials
echo "api_key=YOUR_OPENEI_KEY" > ~/.config/openei/credentials
chmod 600 ~/.config/eia/credentials ~/.config/netl-edx/credentials \
         ~/.config/fred/credentials ~/.config/openei/credentials

# Optional keys (higher rate limits)
mkdir -p ~/.config/epa ~/.config/comtrade
chmod 700 ~/.config/epa ~/.config/comtrade
echo "api_key=YOUR_EPA_KEY" > ~/.config/epa/credentials
echo "api_key=YOUR_COMTRADE_KEY" > ~/.config/comtrade/credentials
chmod 600 ~/.config/epa/credentials ~/.config/comtrade/credentials
```

Each skill resolves credentials in this order:

1. `~/.config/{service}/credentials` file (preferred)
2. Environment variable (fallback)
3. Prompt with signup URL (if neither found)

---

## 1. EIA Open Data API

**Skill:** `eia-data`, `opec-data`
**Cost:** Free, no limits on non-commercial use

### Get the key

1. Go to <https://www.eia.gov/opendata/>
2. Click **Register**
3. Enter your name and email address
4. Submit the form -- the key is emailed immediately

### Store the key

```bash
mkdir -p ~/.config/eia
chmod 700 ~/.config/eia
echo "api_key=YOUR_EIA_KEY" > ~/.config/eia/credentials
chmod 600 ~/.config/eia/credentials
```

**Environment variable (alternative):** `EIA_API_KEY`

```bash
export EIA_API_KEY="YOUR_EIA_KEY"
```

**Note:** The `opec-data` skill also uses this key since it sources
OPEC production data through the EIA STEO API.

---

## 2. NETL Energy Data eXchange (EDX)

**Skill:** `netl-edx`
**Cost:** Free, requires justification (use "academic research" or "student")

### Get the key

1. Go to <https://edx.netl.doe.gov/>
2. Click **Sign up**
3. Fill out the registration form: name, email, organization, and reason
   for access. For reason, "academic research" or "student" is sufficient.
4. Check your email and verify the account
5. Log in
6. Click your username in the top-right corner to open your user profile
7. On the profile page, find the text **Hover to reveal API Key**
8. Hover over it, then click to copy the key

### Store the key

```bash
mkdir -p ~/.config/netl-edx
chmod 700 ~/.config/netl-edx
echo "api_key=YOUR_NETL_KEY" > ~/.config/netl-edx/credentials
chmod 600 ~/.config/netl-edx/credentials
```

**Environment variable (alternative):** `NETL_EDX_API_KEY`

```bash
export NETL_EDX_API_KEY="YOUR_NETL_KEY"
```

**Note on request headers:** The EDX CKAN API accepts the key under any of
these header names:

- `EDX-API-Key`
- `X-CKAN-API-Key`
- `Authorization`

The `netl-edx` skill uses `EDX-API-Key` by default.

---

## 3. FRED (Federal Reserve Economic Data)

**Skill:** `fred-prices`
**Cost:** Free, 120 requests per minute

### Get the key

1. Go to <https://fred.stlouisfed.org/docs/api/api_key.html>
2. Click **Request API Key** (you will need to create a FRED account first)
3. Provide your name, email, organization, and reason (use "academic research")
4. The key is displayed on screen immediately

### Store the key

```bash
mkdir -p ~/.config/fred
chmod 700 ~/.config/fred
echo "api_key=YOUR_FRED_KEY" > ~/.config/fred/credentials
chmod 600 ~/.config/fred/credentials
```

**Environment variable (alternative):** `FRED_API_KEY`

```bash
export FRED_API_KEY="YOUR_FRED_KEY"
```

**Key FRED series for PNGE research:**

| Series ID | Description |
|-----------|-------------|
| `DCOILWTICO` | WTI Crude Oil Price (daily) |
| `DCOILBRENTEU` | Brent Crude Oil Price (daily) |
| `DHHNGSP` | Henry Hub Natural Gas Spot Price (daily) |
| `PNGASEUUSDM` | Natural Gas Price, EU (monthly) |
| `GASREGW` | US Regular Gasoline Price (weekly) |
| `PCU211111211111` | PPI Crude Petroleum (monthly) |

---

## 4. OpenEI (DOE Geothermal Data Repository)

**Skill:** `doe-geothermal`
**Cost:** Free

### Get the key

1. Go to <https://openei.org/services/api/signup/>
2. Create an OpenEI account (or log in with an existing one)
3. Request an API key -- it is displayed on screen immediately

### Store the key

```bash
mkdir -p ~/.config/openei
chmod 700 ~/.config/openei
echo "api_key=YOUR_OPENEI_KEY" > ~/.config/openei/credentials
chmod 600 ~/.config/openei/credentials
```

**Environment variable (alternative):** `OPENEI_API_KEY`

```bash
export OPENEI_API_KEY="YOUR_OPENEI_KEY"
```

---

## 5. EPA api.data.gov (optional)

**Skills:** `epa-enviro`, `epa-ghg`
**Cost:** Free, rate limited to 1000 requests/hour by default
**Required:** No -- both skills work without a key as of early 2026

### Get the key

1. Go to <https://api.data.gov/signup/>
2. Enter your name and email address
3. The key is displayed on screen immediately and also sent by email

### Store the key

```bash
mkdir -p ~/.config/epa
chmod 700 ~/.config/epa
echo "api_key=YOUR_EPA_KEY" > ~/.config/epa/credentials
chmod 600 ~/.config/epa/credentials
```

**Environment variable (alternative):** `EPA_API_KEY`

```bash
export EPA_API_KEY="YOUR_EPA_KEY"
```

**Note:** The same api.data.gov key works for all EPA APIs routed through
that gateway. Testing shows that Envirofacts (`data.epa.gov/efservice`)
and ECHO (`echodata.epa.gov`) both work without a key as of early 2026.
The skill will still attempt to send the key if available, but queries
should succeed either way. Having a key raises the rate limit.

---

## 6. UN Comtrade (optional)

**Skill:** `comtrade-minerals`
**Cost:** Free, 500 requests/day without key
**Required:** No -- the public preview API works without a key

### Get the key

1. Go to <https://comtradeapi.un.org/>
2. Click **Subscribe** to create a free account
3. After account creation, find your subscription key in your profile

### Store the key

```bash
mkdir -p ~/.config/comtrade
chmod 700 ~/.config/comtrade
echo "api_key=YOUR_COMTRADE_KEY" > ~/.config/comtrade/credentials
chmod 600 ~/.config/comtrade/credentials
```

**Environment variable (alternative):** `COMTRADE_API_KEY`

```bash
export COMTRADE_API_KEY="YOUR_COMTRADE_KEY"
```

**Note:** Without a key, the public preview endpoint works with a limit of
500 requests per day, which is sufficient for research queries.

---

## Services With No Key Required

Fourteen of the twenty data skills access public data with no authentication.

| Service | Skill Name | Access Method | Notes |
|---------|-----------|---------------|-------|
| USGS Produced Waters DB | `usgs-produced-waters` | ScienceBase public download | CSV from ScienceBase item `64fa1e71d34ed30c2054ea11` |
| USGS Mineral Commodities | `usgs-minerals` | data.usgs.gov / ScienceBase | CSV/Excel per commodity per year |
| WVGES Well Data | `wvges-wells` | ArcGIS REST public MapServer | 145,000+ wells via WVDEP, no auth |
| BOEM Offshore Data | `boem-offshore` | data.boem.gov public downloads | Bulk delimited text + ArcGIS REST |
| FracFocus | `fracfocus` | Public API + bulk CSV download | 200k+ disclosures, no auth |
| USGS Publications | `usgs-pubs` | pubs.usgs.gov REST API | Covers all USGS report series |
| DOE OSTI | `doe-osti` | osti.gov REST API | Public DOE-funded research records |
| USGS Earthquakes | `usgs-earthquakes` | earthquake.usgs.gov FDSN API | ComCat catalog, GeoJSON output |
| USGS Water Data | `usgs-waterdata` | waterservices.usgs.gov + WQP | NWIS instantaneous/daily + Water Quality Portal |
| EPA GHG Reporting | `epa-ghg` | data.epa.gov/efservice | GHGRP Subpart W (petroleum & NG) |
| World Bank Energy | `worldbank-energy` | api.worldbank.org/v2 | 200+ energy indicators by country |
| CrossRef DOI | `crossref-doi` | api.crossref.org | DOI resolution + citation metadata |
| IEA Open Data | `iea-open` | api.iea.org (free subset) | EV tracker, energy prices, GHG, NZE, CCUS, SDG7 |
| EPA Envirofacts | `epa-enviro` | data.epa.gov + ECHO | Works without key (key optional for rate limits) |

No setup is needed for these skills. They work immediately after plugin
installation.

---

## Verification

Run these commands to confirm each required key is working.

### Test EIA key

```bash
curl -s "https://api.eia.gov/v2/?api_key=$(grep '^api_key=' ~/.config/eia/credentials | cut -d= -f2)" \
  | jq .response.routes
```

Expected: a JSON array listing available EIA API route categories
(petroleum, electricity, natural-gas, etc.).

### Test NETL EDX key

```bash
curl -s "https://edx.netl.doe.gov/api/3/action/package_search?q=test&rows=1" \
  -H "EDX-API-Key: $(grep '^api_key=' ~/.config/netl-edx/credentials | cut -d= -f2)" \
  | jq .success
```

Expected: `true`

### Test FRED key

```bash
curl -s "https://api.stlouisfed.org/fred/series?series_id=DCOILWTICO&api_key=$(grep '^api_key=' ~/.config/fred/credentials | cut -d= -f2)&file_type=json" \
  | jq '.seriess[0].title'
```

Expected: `"Crude Oil Prices: West Texas Intermediate (WTI) - Cushing, Oklahoma"`

### Test OpenEI key

```bash
curl -s "https://openei.org/w/api.php?action=ask&query=[[Category:Geothermal%20Resource%20Area]]&format=json&api_key=$(grep '^api_key=' ~/.config/openei/credentials | cut -d= -f2)" \
  | jq '.query.meta.count'
```

Expected: a number (count of geothermal resource area pages).

### Test EPA key (optional, may work without key)

```bash
curl -s "https://data.epa.gov/efservice/TRI_FACILITY/STATE_ABBR/WV/rows/0:1/JSON" \
  | jq length
```

Expected: `1` (one facility record returned).

---

## Troubleshooting

**"No API key found" error from a skill**
The skill checked `~/.config/{service}/credentials` and the environment
variable, and found neither. Re-run the storage commands above and make
sure the file contains `api_key=` with no extra whitespace.

**Permission denied reading credentials file**
Check ownership and permissions:

```bash
ls -la ~/.config/eia/credentials
# Should show: -rw------- 1 YOUR_USER ...
```

If not, fix with:

```bash
chmod 600 ~/.config/eia/credentials
```

**EDX returns 403 or "Not Authorized"**
- Confirm the key is correct by logging into <https://edx.netl.doe.gov/>
  and checking your profile page.
- Try a different header name. Some EDX endpoints prefer `X-CKAN-API-Key`
  over `EDX-API-Key`.

**EIA returns `"error": "API_KEY_MISSING"`**
- Verify the credentials file has no trailing newline or whitespace after
  the key value.
- Test the key directly:

```bash
curl -s "https://api.eia.gov/v2/?api_key=PASTE_KEY_HERE" | jq .response
```

**FRED returns `"error_code": 1`**
- FRED error code 1 means "Bad request: invalid API key". Verify the key
  value in your credentials file matches what FRED issued.
- Check that the file has no leading/trailing whitespace around the key.

**OpenEI returns empty results**
- The Semantic MediaWiki API sometimes returns empty for malformed queries.
  Test with a simple category query first (see verification above).
- Ensure your key is valid by checking your OpenEI profile.

**EPA rate limit exceeded (HTTP 429)**
- The default limit is 1000 requests per hour. Wait and retry, or request
  a higher rate limit at <https://api.data.gov/signup/> by contacting
  their support.

**Comtrade returns HTTP 403**
- Without a key, you are limited to 500 requests per day on the public
  preview endpoint. If you hit the limit, wait 24 hours or register for
  a free key.
