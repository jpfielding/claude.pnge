# API Token Acquisition Guide

This guide covers every credential needed by the claude-pnge plugin.
Three of the ten data skills require API keys. The remaining seven use
public endpoints with no authentication.

---

## Table of Contents

- [Quick Setup](#quick-setup)
- [1. EIA Open Data API](#1-eia-open-data-api)
- [2. NETL Energy Data eXchange (EDX)](#2-netl-energy-data-exchange-edx)
- [3. EPA api.data.gov](#3-epa-apidatagov)
- [Services With No Key Required](#services-with-no-key-required)
- [Verification](#verification)
- [Troubleshooting](#troubleshooting)

---

## Quick Setup

After obtaining all three keys, run this block to store them. Replace
each `YOUR_*_KEY` placeholder with the actual key value.

```bash
# Create all credential directories
mkdir -p ~/.config/eia ~/.config/netl-edx ~/.config/epa
chmod 700 ~/.config/eia ~/.config/netl-edx ~/.config/epa

# Store keys (replace YOUR_KEY_HERE with actual values)
echo "api_key=YOUR_EIA_KEY" > ~/.config/eia/credentials
echo "api_key=YOUR_NETL_KEY" > ~/.config/netl-edx/credentials
echo "api_key=YOUR_EPA_KEY" > ~/.config/epa/credentials
chmod 600 ~/.config/eia/credentials ~/.config/netl-edx/credentials ~/.config/epa/credentials
```

Each skill resolves credentials in this order:

1. `~/.config/{service}/credentials` file (preferred)
2. Environment variable (fallback)
3. Prompt with signup URL (if neither found)

---

## 1. EIA Open Data API

**Skill:** `eia-data`
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

## 3. EPA api.data.gov

**Skill:** `epa-enviro`
**Cost:** Free, rate limited to 1000 requests/hour by default

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
that gateway. However, testing shows that Envirofacts (`enviro.epa.gov`)
and ECHO (`echodata.epa.gov`) both work without a key as of early 2026.
The skill will still attempt to send the key if available, but queries
should succeed either way.

---

## Services With No Key Required

Seven of the ten skills access public data with no authentication.

| Service | Skill Name | Access Method | Notes |
|---------|-----------|---------------|-------|
| USGS Produced Waters DB | `usgs-produced-waters` | ScienceBase public download | CSV from ScienceBase item `65b6d616d34e46cd33b3690e` |
| USGS Mineral Commodities | `usgs-minerals` | data.usgs.gov / ScienceBase | CSV/Excel per commodity per year |
| WVGES Well Data | `wvges-wells` | ArcGIS REST public MapServer | 145,000+ wells, no auth |
| BOEM Offshore Data | `boem-offshore` | data.boem.gov public downloads | Bulk delimited text + ArcGIS REST |
| FracFocus | `fracfocus` | Public API + bulk CSV download | 200k+ disclosures, no auth |
| USGS Publications | `usgs-pubs` | pubs.er.usgs.gov REST API | Covers all USGS report series |
| DOE OSTI | `doe-osti` | osti.gov REST API | Public DOE-funded research records |

No setup is needed for these skills. They work immediately after plugin
installation.

---

## Verification

Run these commands to confirm each key is working. All three should
produce valid JSON output.

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

### Test EPA key (may work without key)

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

**EPA rate limit exceeded (HTTP 429)**
- The default limit is 1000 requests per hour. Wait and retry, or request
  a higher rate limit at <https://api.data.gov/signup/> by contacting
  their support.
