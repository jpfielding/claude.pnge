# CLAUDE.md — claude-pnge Plugin Build Plan

This is a Claude Code plugin for petroleum engineering research data access.
It bundles 10 data-access skills, 1 research agent, and 1 slash command into
a single installable plugin for Claude Code.

**Target user:** WVU PNGE undergraduate researcher focused on lithium/magnesium
recovery from produced waters and oilfield brines.

**Language preferences:** Go (primary), Rust and Bash where appropriate.
Outputs should be precise and structured — balancing human readability with
machine parseability. Include certainty levels and bias notes where relevant.

---

## Project Structure

```
claude-pnge/
├── .claude-plugin/
│   └── plugin.json              # Plugin manifest (EXISTS — review and finalize)
├── skills/                      # 10 data-access skills
│   ├── eia-data/                # EXISTS and COMPLETE — copied from working skill
│   │   ├── SKILL.md
│   │   └── references/
│   ├── usgs-produced-waters/    # BUILD — Priority 1
│   │   ├── SKILL.md
│   │   └── references/
│   │       ├── schema.md        # Column definitions from actual CSV headers
│   │       ├── formations.md    # Key formations table with Li/Mg ranges
│   │       └── golang_client.go # Go example for CSV filtering
│   ├── usgs-minerals/           # BUILD — Priority 1
│   │   ├── SKILL.md
│   │   └── references/
│   │       └── commodities.md   # Li and Mg commodity data endpoints
│   ├── netl-edx/                # BUILD — Priority 1
│   │   ├── SKILL.md
│   │   └── references/
│   │       └── ckan_api.md      # CKAN action reference
│   ├── wvges-wells/             # BUILD — Priority 2
│   │   ├── SKILL.md
│   │   └── references/
│   │       └── arcgis_rest.md   # MapServer query patterns
│   ├── boem-offshore/           # BUILD — Priority 2
│   │   ├── SKILL.md
│   │   └── references/
│   │       └── endpoints.md     # Raw data download URLs
│   ├── fracfocus/               # BUILD — Priority 2
│   │   ├── SKILL.md
│   │   └── references/
│   │       └── api_reference.md
│   ├── epa-enviro/              # BUILD — Priority 2
│   │   ├── SKILL.md
│   │   └── references/
│   │       └── table_reference.md
│   ├── usgs-pubs/               # BUILD — Priority 3
│   │   ├── SKILL.md
│   │   └── references/
│   │       └── api_reference.md
│   └── doe-osti/                # BUILD — Priority 3
│       ├── SKILL.md
│       └── references/
│           └── api_reference.md
├── agents/
│   └── li-mg-prospector.md      # EXISTS — review and finalize
├── commands/
│   └── prospect.md              # EXISTS — review and finalize
├── .env.example                 # EXISTS
├── .gitignore                   # EXISTS
├── README.md                    # EXISTS — update after all skills built
└── docs/
    └── TOKENS.md                # BUILD — credential acquisition guide
```

---

## Build Instructions Per Skill

For EACH skill, follow the EIA skill pattern. Every SKILL.md must have:

1. **YAML frontmatter** with `name` (kebab-case, ≤64 chars) and `description` (≤1024 chars, no angle brackets). Description should be "pushy" — include trigger phrases.
2. **Credential resolution** section (if key needed) following the pattern:
   `~/.config/{service}/credentials` → `ENV_VAR` → prompt user
3. **API structure** section with base URL, parameters, and example requests
4. **Workflow** section: Resolve Intent → Fetch Metadata → Fetch Data → Parse → Output
5. **Output format** section: markdown table + narrative summary (match EIA style)
6. **Error handling** table
7. **Reference files** in `references/` for anything over ~30 lines of detail

Use `bash_tool` with `curl` + `jq` for API calls. Include Go examples in references/.

---

## Skill Specifications

### 1. eia-data (COMPLETE)

Already working. Copied from existing skill. No changes needed.

### 2. usgs-produced-waters (PRIORITY 1)

**What it does:** Query/analyze the USGS National Produced Waters Geochemical DB v3.0.

**Data source details:**
- ScienceBase item ID: `65b6d616d34e46cd33b3690e`
- DOI: https://doi.org/10.5066/P9DSRCZJ
- Format: Large CSV file (~115k rows, 100+ columns)
- No API key required
- Access: Download CSV from ScienceBase, then filter locally

**ScienceBase API for discovery:**
```
GET https://www.sciencebase.gov/catalog/item/65b6d616d34e46cd33b3690e?format=json&fields=files
```
Returns file list with download URLs.

**Search for related items:**
```
GET https://www.sciencebase.gov/catalog/items?q=produced+water+geochemical&format=json&max=10
```

**Key columns (verify against actual CSV headers after download):**
- Identification: SOURCE_ID, API_NUMBER, STATE, COUNTY, LATITUDE, LONGITUDE
- Geology: BASIN, FORMATION, FORMATION_AGE, DEPTH_FT
- Key analytes (mg/L): Li, Mg, Ba, Br, Ca, Cl, Fe, K, Mn, Na, Si, SO4, Sr
- Physical: TDS, pH, SPECIFIC_GRAVITY, TEMPERATURE_C

**Important formations for Li/Mg:**
- Smackover (AR/TX/LA) — Li up to 477 mg/L, highest known U.S. brine Li
- Marcellus (WV/PA/OH) — Li 10-200+ mg/L, large volumes
- Utica/Point Pleasant (OH/WV/PA) — Li 20-150 mg/L
- Bakken (ND/MT) — Li 10-70 mg/L
- Economic Li cutoff for DLE: ~100-150 mg/L

**Build approach:** Download the actual CSV, inspect the real column names,
then write the skill with verified schema. Create references/schema.md from
the actual headers. Write a Go example that reads/filters the CSV.

**Credential:** None needed.

### 3. usgs-minerals (PRIORITY 1)

**What it does:** Access USGS Mineral Commodity Summaries data for Li, Mg,
and other critical minerals — production stats, reserves, pricing.

**Data source details:**
- MCS 2025: https://pubs.usgs.gov/periodicals/mcs2025/
- Data releases on ScienceBase/data.usgs.gov:
  - Li MCS 2025 data: https://data.usgs.gov/datacatalog/data/USGS:6797ff62d34ea8c18376e1cb
  - Mg data releases: search data.usgs.gov for "magnesium mineral commodity"
  - World Minerals Outlook 2029 (Li+Mg capacity): ScienceBase ID `67b8b168d34e1a2e835b7e6c`
- Format: CSV/Excel files per commodity per year
- No API key required

**Access patterns:**
```bash
# Search the USGS Science Data Catalog
curl -s "https://data.usgs.gov/datacatalog/api/3/action/package_search?q=lithium+mineral+commodity&rows=10"

# Get a specific data release
curl -s "https://www.sciencebase.gov/catalog/item/67b8b168d34e1a2e835b7e6c?format=json"
```

**Key data points to surface:**
- Annual world mine production by country (tons Li content)
- U.S. import sources and percentages
- Reserve estimates by country
- Price trends (lithium carbonate, lithium hydroxide, spodumene)
- End-use breakdown (batteries, ceramics, greases, etc.)
- Same for Mg compounds and Mg metal

**Credential:** None needed.

### 4. netl-edx (PRIORITY 1)

**What it does:** Search/retrieve datasets from DOE NETL Energy Data eXchange.

**Data source details:**
- Platform: https://edx.netl.doe.gov/
- API: CKAN-based REST (https://edx.netl.doe.gov/api/3/)
- ClaiMM (Critical Minerals and Materials): https://edx.netl.doe.gov/sites/claimm/
- API key required (free account)

**CKAN API actions (standard CKAN v3):**
```bash
# Search datasets
curl -s "https://edx.netl.doe.gov/api/3/action/package_search?q=lithium+produced+water" \
  -H "EDX-API-Key: $NETL_EDX_API_KEY"

# Get dataset details
curl -s "https://edx.netl.doe.gov/api/3/action/package_show?id=DATASET_NAME" \
  -H "EDX-API-Key: $NETL_EDX_API_KEY"

# Search resources within datasets
curl -s "https://edx.netl.doe.gov/api/3/action/resource_search?query=name:lithium" \
  -H "EDX-API-Key: $NETL_EDX_API_KEY"

# List all datasets in a group/organization
curl -s "https://edx.netl.doe.gov/api/3/action/group_list" \
  -H "EDX-API-Key: $NETL_EDX_API_KEY"
```

**Key header names:** The API key header can be any of:
`X-CKAN-API-Key`, `EDX-API-Key`, or `Authorization`

**Download a resource:**
```bash
wget --header="EDX-API-Key:$KEY" \
  "https://edx.netl.doe.gov/dataset/SUBMISSION/resource_download/RESOURCE_ID"
```

**Credential:**
- Key name: `NETL_EDX_API_KEY`
- File: `~/.config/netl-edx/credentials` → `api_key=YOUR_KEY`
- Signup: https://edx.netl.doe.gov/ → click "Sign up" → free account
- After login, go to user profile → hover "Hover to reveal API Key" → copy

### 5. wvges-wells (PRIORITY 2)

**What it does:** Query WV Geological & Economic Survey oil and gas well data.

**Data source details:**
- ArcGIS REST MapServer: http://atlas.wvgs.wvnet.edu/arcgis/rest/services/OilGas/WVOG/MapServer
- Pipeline web app: https://www.wvgs.wvnet.edu/pipe2/
- WVDEP Office of Oil & Gas: https://tagis.dep.wv.gov/oog/
- 145,000+ wells, data back to 1860s
- No API key required

**ArcGIS REST API query pattern:**
```bash
# Query wells in a county (Monongalia = county code specific to WVGES)
# Layer 0 = Oil Wells, Layer 5 = Gas Wells (check MapServer for layer list)
curl -s "http://atlas.wvgs.wvnet.edu/arcgis/rest/services/OilGas/WVOG/MapServer/0/query" \
  --data-urlencode "where=1=1" \
  --data-urlencode "outFields=*" \
  --data-urlencode "resultRecordCount=10" \
  --data-urlencode "f=json"

# Spatial query — wells within a bounding box
curl -s "http://atlas.wvgs.wvnet.edu/arcgis/rest/services/OilGas/WVOG/MapServer/0/query" \
  --data-urlencode "geometry=-80.5,39.5,-79.5,40.0" \
  --data-urlencode "geometryType=esriGeometryEnvelope" \
  --data-urlencode "spatialRel=esriSpatialRelIntersects" \
  --data-urlencode "outFields=*" \
  --data-urlencode "f=json"

# Get MapServer layer list
curl -s "http://atlas.wvgs.wvnet.edu/arcgis/rest/services/OilGas/WVOG/MapServer?f=json" | jq '.layers'
```

**Data types in the system (8 tables, keyed by county code + permit number):**
LOCATIONS, COMPLETIONS/OWNERS, PAYS/SHOWS/WATER, STRATIGRAPHY,
PRODUCTION, PLUG, MECHANICAL LOG CATALOG, WELL SAMPLES AND CORES

**Pipeline web lookup (not API, but useful reference):**
Individual well data by county code + permit number at:
https://www.wvgs.wvnet.edu/pipe2/OGDataSearch.aspx

**Credential:** None needed.

### 6. boem-offshore (PRIORITY 2)

**What it does:** Access federal OCS offshore production, wells, leases, platforms.

**Data source details:**
- Data Center: https://www.data.boem.gov/
- Raw data downloads: https://www.data.boem.gov/Main/RawData.aspx
- GIS REST services: https://gis.boem.gov/arcgis/rest/services/BOEM_BSEE/
- Production data: https://www.data.boem.gov/Main/Production.aspx
- No API key required

**Access patterns:**
```bash
# Production data — bulk download as delimited text
# Files available: production by lease, by well (API), by operator
# Check the Raw Data page for current file URLs

# ArcGIS REST for spatial queries
curl -s "https://gis.boem.gov/arcgis/rest/services/BOEM_BSEE/MMC_Layers/MapServer?f=json" \
  | jq '.layers[] | {id, name}'

# Query a specific layer (e.g., OCS Oil and Gas Wells)
curl -s "https://gis.boem.gov/arcgis/rest/services/BOEM_BSEE/MMC_Layers/MapServer/2/query" \
  --data-urlencode "where=1=1" \
  --data-urlencode "outFields=*" \
  --data-urlencode "resultRecordCount=5" \
  --data-urlencode "f=json"
```

**Credential:** None needed.

### 7. fracfocus (PRIORITY 2)

**What it does:** Query hydraulic fracturing chemical disclosure data.

**Data source details:**
- Registry: https://fracfocus.org/
- Data portal: https://www.fracfocusdata.org/
- API: https://api.fracfocus.org/ (confirm current endpoint)
- Bulk CSV download available for research
- Open-FF (cleaned research version): https://github.com/FracTracker/Open-FF
- ~200k+ disclosures, 34 states, 2011-present
- No API key required

**Access patterns:**
```bash
# The FracFocus API provides well-level disclosure data
# Bulk download is preferred for research — CSV from fracfocus.org data download page

# API endpoint (verify — may require checking current docs):
curl -s "https://api.fracfocus.org/DisclosureSearch/GetSearchResults" \
  -H "Content-Type: application/json" \
  -d '{"state":"WV","county":"","operator":"","wellName":"","apiNumber":"","startDate":"2020-01-01","endDate":"2024-12-31"}'
```

**Key data fields per disclosure:**
APINumber, JobStartDate, JobEndDate, StateName, CountyName, OperatorName,
WellName, Latitude, Longitude, TVD, TotalBaseWaterVolume, TotalBaseNonWaterVolume,
TradeName, Supplier, Purpose, CASNumber, IngredientName, PercentHFJob, PercentHighAdditive

**Data quality note:** Industry self-reported. CBI (Confidential Business
Information) exemptions hide some chemical identities. See FracTracker analysis
for known data gaps.

**Credential:** None needed.

### 8. epa-enviro (PRIORITY 2)

**What it does:** Query EPA Envirofacts for facility data, UIC wells, permits.

**Data source details:**
- Envirofacts API v1: https://enviro.epa.gov/enviro/efservice/
- ECHO (enforcement/compliance): https://echo.epa.gov/tools/data-downloads
- API key: Required, free from api.data.gov
- API key signup: https://api.data.gov/signup/

**Envirofacts REST API pattern:**
```
GET https://enviro.epa.gov/enviro/efservice/{TABLE_NAME}/{COLUMN}/{OPERATOR}/{VALUE}/JSON

# Example: UIC injection wells in West Virginia
GET https://enviro.epa.gov/enviro/efservice/UIC_WELL/STATE_CODE/WV/JSON

# With row limits
GET https://enviro.epa.gov/enviro/efservice/UIC_WELL/STATE_CODE/WV/rows/0:100/JSON
```

**Key tables for PNGE research:**
- `UIC_WELL` — Underground Injection Control wells (Class II = oilfield disposal/EOR)
- `UIC_VIOLATION` — UIC violations
- `SDWIS_WATER_SYSTEM` — Public water systems
- `TRI_FACILITY` — Toxic Release Inventory facilities
- `FRS_FACILITY_SITE` — Facility Registry (cross-references other systems)

**ECHO API (for compliance data):**
```bash
curl -s "https://echodata.epa.gov/echo/dfr_rest_services.get_facility_info?p_id=FACILITY_ID&output=JSON"
```

**Credential:**
- Key name: `EPA_API_KEY`
- File: `~/.config/epa/credentials` → `api_key=YOUR_KEY`
- Signup: https://api.data.gov/signup/ — enter email, get key instantly
- Pass as query param: `?api_key=YOUR_KEY`

### 9. usgs-pubs (PRIORITY 3)

**What it does:** Search USGS Publications Warehouse for reports and papers.

**Data source details:**
- API base: https://pubs.er.usgs.gov/pubs-services/publication
- No API key required
- Covers: Professional Papers, Fact Sheets, Open-File Reports, Data Series, etc.

**API patterns:**
```bash
# Search by keyword
curl -s "https://pubs.er.usgs.gov/pubs-services/publication?q=lithium+produced+water&page_size=10"

# Search by series and year
curl -s "https://pubs.er.usgs.gov/pubs-services/publication?typeName=Report&year=2024&q=lithium"

# Get a specific publication
curl -s "https://pubs.er.usgs.gov/pubs-services/publication/fs20243052"

# Search parameters: q, title, year, typeName, subtypeName, contributingOffice,
#   page_size, page_number, pub_x_days (published in last X days)
```

**Response format:** JSON with fields: id, title, docAbstract, publicationType,
publicationSubtype, seriesTitle, seriesNumber, publicationYear, doi, links[]

**Credential:** None needed.

### 10. doe-osti (PRIORITY 3)

**What it does:** Search DOE OSTI for technical reports from national labs.

**Data source details:**
- API base: https://www.osti.gov/api/v1/records
- No API key required for public searches
- Covers all DOE-funded research including NETL, national labs

**API patterns:**
```bash
# Search by keyword
curl -s "https://www.osti.gov/api/v1/records?q=lithium+produced+water&rows=10" \
  -H "Accept: application/json"

# Filter by DOE program, date range, etc.
curl -s "https://www.osti.gov/api/v1/records?q=lithium+brine&publication_date_start=2020-01-01&rows=20" \
  -H "Accept: application/json"

# Search parameters: q, title, author, publication_date_start/end,
#   entry_date_start/end, site_ownership_code, rows, page
```

**Response format:** JSON array of records with: osti_id, title, authors,
publication_date, doe_contract_number, product_type, abstract, doi, links

**Credential:** None needed.

---

## Credential Acquisition Guide (for docs/TOKENS.md)

Build a `docs/TOKENS.md` file with step-by-step instructions for each service
that needs a key. Include screenshots descriptions. Here is the content:

### Services Requiring API Keys (3 of 10)

**1. EIA Open Data API**
- URL: https://www.eia.gov/opendata/
- Steps: Click "Register" → enter name + email → key emailed immediately
- Cost: Free, no limits on non-commercial use
- Store: `~/.config/eia/credentials` as `api_key=YOUR_KEY`
- Env var: `EIA_API_KEY`

**2. NETL Energy Data eXchange (EDX)**
- URL: https://edx.netl.doe.gov/
- Steps: Click "Sign up" → fill form (name, email, org, reason) → verify email
  → login → click your username (top right) → user profile page → hover over
  "Hover to reveal API Key" → click to copy
- Cost: Free, requires justification (use "academic research" or "student")
- Store: `~/.config/netl-edx/credentials` as `api_key=YOUR_KEY`
- Env var: `NETL_EDX_API_KEY`
- Note: Key header can be `EDX-API-Key`, `X-CKAN-API-Key`, or `Authorization`

**3. EPA api.data.gov**
- URL: https://api.data.gov/signup/
- Steps: Enter name + email → key displayed on screen AND emailed
- Cost: Free, rate limited (1000 requests/hour default)
- Store: `~/.config/epa/credentials` as `api_key=YOUR_KEY`
- Env var: `EPA_API_KEY`
- Note: Same key works for all EPA APIs through api.data.gov

### Services With No Key Required (7 of 10)

| Service | Access | Notes |
|---------|--------|-------|
| USGS Produced Waters DB | ScienceBase public download | No auth needed |
| USGS Mineral Commodities | data.usgs.gov / ScienceBase | No auth needed |
| WVGES Well Data | ArcGIS REST public | No auth needed |
| BOEM Offshore Data | data.boem.gov public | No auth needed |
| FracFocus | Public API + bulk download | No auth needed |
| USGS Publications | pubs.er.usgs.gov API | No auth needed |
| DOE OSTI | osti.gov API | No auth for public records |

---

## Shared Credential Resolution Pattern

Every skill that needs a key should use this pattern (from the EIA skill):

```bash
# Bash
KEY=$(grep '^api_key=' ~/.config/{service}/credentials 2>/dev/null | cut -d= -f2)
[ -z "$KEY" ] && KEY="${SERVICE_ENV_VAR}"
if [ -z "$KEY" ]; then
    echo "No API key found. Get one free at {signup_url}"
    echo "Store in ~/.config/{service}/credentials as api_key=YOUR_KEY"
    exit 1
fi
```

```go
// Go
func resolveAPIKey(service, envVar string) (string, error) {
    home, _ := os.UserHomeDir()
    creds := filepath.Join(home, ".config", service, "credentials")
    if data, err := os.ReadFile(creds); err == nil {
        for _, line := range strings.Split(string(data), "\n") {
            if strings.HasPrefix(line, "api_key=") {
                return strings.TrimPrefix(line, "api_key="), nil
            }
        }
    }
    if key := os.Getenv(envVar); key != "" {
        return key, nil
    }
    return "", fmt.Errorf("no API key for %s", service)
}
```

---

## Quality Standards

Each completed skill should include:

- [ ] Valid YAML frontmatter passing `claude plugin validate`
- [ ] Description with trigger phrases (≤1024 chars, no `<` or `>`)
- [ ] Working curl example that can be copy-pasted and run
- [ ] Output format matching the EIA skill pattern (table + narrative)
- [ ] Error handling table (HTTP codes → actions)
- [ ] At least one Go example in references/
- [ ] Caveats/bias section noting data limitations
- [ ] Credential section (if needed) with signup URL

## Build Order

1. Finish `usgs-produced-waters` — download the actual CSV, verify columns, write complete skill
2. Finish `usgs-minerals` — verify data.usgs.gov endpoints, write skill
3. Finish `netl-edx` — test CKAN API actions, write skill
4. Finish `wvges-wells` — query the ArcGIS REST MapServer, verify layers, write skill
5. Finish `boem-offshore` — verify download URLs and GIS layers, write skill
6. Finish `fracfocus` — verify API endpoint or document bulk download, write skill
7. Finish `epa-enviro` — test Envirofacts endpoints, write skill
8. Finish `usgs-pubs` — test pubs-services API, write skill
9. Finish `doe-osti` — test OSTI API, write skill
10. Build `docs/TOKENS.md` from the credential guide above
11. Finalize `agents/li-mg-prospector.md` — verify skill names match namespace
12. Update `README.md` with final status
13. `git add . && git commit && git push`

---

## Plugin Validation

After building, run:
```bash
claude plugin validate .
```

All skills should have valid frontmatter. Test locally with:
```bash
claude --plugin-dir ./claude-pnge
```

Then try: `/prospect Marcellus Shale WV` to exercise the agent.
