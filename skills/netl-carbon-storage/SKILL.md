---
name: netl-carbon-storage
description: >
  Query NETL Carbon Storage Atlas data and DOE-funded CCS datasets for U.S.
  geological CO2 storage capacity, saline aquifer capacity estimates, depleted
  reservoir capacity, active CCS projects, and carbon capture and storage site
  information. Use this skill when the user asks about CO2 storage potential,
  carbon sequestration sites, CCS projects in the Appalachian basin, saline
  aquifer storage capacity, geological carbon storage, Class VI injection wells
  for CO2, or DOE carbon storage research. Trigger for phrases like "CO2
  storage capacity in West Virginia", "carbon storage potential Appalachian
  basin", "CCS projects near Marcellus wells", "saline aquifer storage
  capacity", "depleted reservoir storage", "geological carbon sequestration",
  "DOE carbon storage atlas", "NETL CCS data", or "Class VI injection well
  locations". Covers U.S. storage estimates by basin, formation, and state.
  Produces capacity tables and project summaries.
---

# NETL Carbon Storage Atlas Skill

Queries DOE/NETL Carbon Storage Atlas datasets, ScienceBase geochemical items,
and the EDX carbon storage data catalog to retrieve U.S. CO2 storage capacity
estimates, active CCS project data, and Regional Carbon Sequestration
Partnership (RCSP) results.

---

## Credential Handling

NETL EDX queries require an API key. ScienceBase queries are public and need no key.

Resolution order (stop at first success):

1. **`~/.config/netl-edx/credentials`** — parse `api_key=<value>` from this file
2. **`NETL_EDX_API_KEY` env var** — fallback if credentials file is absent
3. **Skip EDX, use ScienceBase only** — if neither is set, most data is still accessible via ScienceBase

**Reading the credentials file (bash):**
```bash
EDX_KEY=$(grep '^api_key=' ~/.config/netl-edx/credentials 2>/dev/null | cut -d= -f2)
[ -z "$EDX_KEY" ] && EDX_KEY="${NETL_EDX_API_KEY}"
if [ -z "$EDX_KEY" ]; then
    echo "No NETL EDX key found. Falling back to ScienceBase queries (no key required)."
    echo "To access EDX datasets, sign up free at https://edx.netl.doe.gov/"
    echo "Store your key in ~/.config/netl-edx/credentials as api_key=YOUR_KEY"
fi
```

**Reading the credentials file (Go):**
```go
func resolveEDXKey() (string, error) {
    home, _ := os.UserHomeDir()
    creds := filepath.Join(home, ".config", "netl-edx", "credentials")
    if data, err := os.ReadFile(creds); err == nil {
        for _, line := range strings.Split(string(data), "\n") {
            if strings.HasPrefix(line, "api_key=") {
                return strings.TrimPrefix(line, "api_key="), nil
            }
        }
    }
    if key := os.Getenv("NETL_EDX_API_KEY"); key != "" {
        return key, nil
    }
    return "", fmt.Errorf("no NETL EDX key; using ScienceBase fallback")
}
```

---

## API Structure

### Primary: ScienceBase Catalog (no key required)

**Base URL:** `https://www.sciencebase.gov/catalog/`

The Carbon Storage Atlas V is hosted on ScienceBase. Retrieve item metadata
and file download links using the catalog API.

```bash
# Get the Carbon Storage Atlas V main item with file list
curl -s "https://www.sciencebase.gov/catalog/item/5b89436fe4b0702d0e808ba7?format=json&fields=title,summary,files,webLinks"

# Search for carbon storage capacity datasets
curl -s "https://www.sciencebase.gov/catalog/items?q=carbon+storage+capacity&format=json&fields=title,summary,files&max=10"

# Search focused on Appalachian basin
curl -s "https://www.sciencebase.gov/catalog/items?q=carbon+storage+Appalachian+saline&format=json&fields=title,summary,files,webLinks&max=10"

# Regional Carbon Sequestration Partnership data
curl -s "https://www.sciencebase.gov/catalog/items?q=RCSP+carbon+sequestration+partnership&format=json&fields=title,summary,files&max=10"
```

**Key ScienceBase item IDs:**
| Item | ScienceBase ID |
|------|----------------|
| Carbon Storage Atlas V (main) | 5b89436fe4b0702d0e808ba7 |
| World Minerals Outlook 2029 | 67b8b168d34e1a2e835b7e6c |

ScienceBase item JSON structure:
```json
{
  "id": "5b89436fe4b0702d0e808ba7",
  "title": "National Carbon Sequestration Database and Geographic Information System (NATCARB) Atlas Version V",
  "summary": "...",
  "files": [
    { "name": "AtlasV_Chapter2_Saline.pdf", "url": "https://...", "size": 12345678 }
  ],
  "webLinks": [
    { "title": "Data download", "uri": "https://..." }
  ]
}
```

---

### Secondary: NETL EDX CKAN API (API key required)

**Base URL:** `https://edx.netl.doe.gov/api/3/action/`

```bash
# Search EDX for carbon storage datasets
curl -s "https://edx.netl.doe.gov/api/3/action/package_search?q=carbon+storage+saline+aquifer&rows=10" \
  -H "EDX-API-Key: $NETL_EDX_API_KEY"

# Search for CCS project data
curl -s "https://edx.netl.doe.gov/api/3/action/package_search?q=CCS+project+CO2+injection&rows=10" \
  -H "EDX-API-Key: $NETL_EDX_API_KEY"

# Get specific dataset details by ID
curl -s "https://edx.netl.doe.gov/api/3/action/package_show?id=DATASET_ID" \
  -H "EDX-API-Key: $NETL_EDX_API_KEY"

# Search resources (files) by name
curl -s "https://edx.netl.doe.gov/api/3/action/resource_search?query=name:carbon+storage+capacity" \
  -H "EDX-API-Key: $NETL_EDX_API_KEY"
```

---

### NATCARB Atlas Reference Data

The NETL NATCARB Atlas V (2015) provides the canonical U.S. storage capacity
estimates. Key figures by reservoir type:

**Estimated U.S. CO2 Storage Capacity (Atlas V):**
| Reservoir Type | Capacity (GtCO2) | Notes |
|----------------|------------------|-------|
| Saline aquifers (total) | 2,379–21,633 | P10–P90 range |
| Saline aquifers (best estimate) | ~8,000 | P50 |
| Oil and gas reservoirs | ~208 | Depleted + EOR |
| Unmineable coal seams | ~54–113 | P10–P90 |
| **Total (best estimate)** | **~8,000+** | Saline dominates |

**Appalachian Basin specifically:**
| State | Primary Formation | Estimated Capacity | Notes |
|-------|------------------|--------------------|-------|
| WV | Oriskany Sandstone | Moderate (saline) | MRCSP target |
| WV | Rose Run Sandstone | Moderate | Deep saline |
| PA | Oriskany | Moderate | Under study |
| OH | Mount Simon | Large | Saline aquifer |
| KY | Multiple | Moderate | MRCSP studies |

See `references/api_reference.md` for capacity unit conversions and regional
breakdown tables.

---

## Workflow

### Step 1 — Resolve Intent

Map the user query to a data type:
- "Storage capacity" → ScienceBase Atlas V data
- "Active CCS project" → EDX project datasets or NATCARB facility list
- "Class VI injection wells" → EPA UIC (see `epa-enviro` skill for UIC_WELL table)
- "Appalachian basin" → MRCSP partnership data (search "MRCSP" in ScienceBase)
- "Saline aquifer" → Chapter 2 of Atlas V
- "Depleted reservoir" → Chapter 3 of Atlas V

### Step 2 — Fetch Metadata

```bash
# Discover available files in the Atlas V item
curl -s "https://www.sciencebase.gov/catalog/item/5b89436fe4b0702d0e808ba7?format=json&fields=title,summary,files" \
  | jq '.files[] | {name: .name, url: .url, size: .size}'
```

Identify which chapter PDFs or data files are relevant to the user's question.

### Step 3 — Fetch Data

For specific basin data, search by region name:
```bash
curl -s "https://www.sciencebase.gov/catalog/items?q=MRCSP+carbon+storage+Appalachian&format=json&fields=title,summary,webLinks&max=10" \
  | jq '.items[] | {title: .title, summary: .summary}'
```

For EDX project data (if key available):
```bash
curl -s "https://edx.netl.doe.gov/api/3/action/package_search?q=CCS+injection+Appalachian&rows=5" \
  -H "EDX-API-Key: $NETL_EDX_API_KEY" \
  | jq '.result.results[] | {title: .title, notes: .notes, resources: (.resources | length)}'
```

### Step 4 — Parse Response

ScienceBase returns JSON with `items` array. Each item has `title`, `summary`,
`files[]`, and `webLinks[]`. Extract relevant fields:
```bash
curl -s "https://www.sciencebase.gov/catalog/items?q=carbon+storage+saline&format=json&max=5" \
  | jq '.items[] | {
      title: .title,
      summary: (.summary // "no summary"),
      files: [.files[]? | {name: .name, url: .url}]
    }'
```

EDX CKAN returns `result.results` array with standard CKAN package metadata.

### Step 5 — Produce Output

**For capacity queries:** Table format + narrative
**For project queries:** Project list table + narrative

---

## Output Format

### Storage Capacity Query Output

```
## U.S. CO2 Geological Storage Capacity — [Region/Basin]

| State / Formation | Type | Capacity Low (GtCO2) | Capacity High (GtCO2) | Confidence | Source |
|-------------------|------|---------------------|-----------------------|------------|--------|
| WV / Oriskany Fm  | Saline | 0.5 | 4.2 | Moderate | NATCARB Atlas V |
| ...               | ...  | ... | ... | ...        | ...    |

**Summary:** [narrative covering current best estimates, confidence range,
key uncertainty factors, and relevance to CCUS deployment]

**Data Note:** Capacity estimates from NETL Atlas V (2015). Values represent
theoretical pore space, not economic or accessible capacity. Injectivity and
regulatory constraints will reduce realizable capacity.
```

### CCS Project Query Output

```
## Active/Planned CCS Projects — [Region]

| Project Name | Type | State | Operator | Status | Annual CO2 (Mt/yr) | Source |
|--------------|------|-------|----------|--------|--------------------|--------|
| ...          | ...  | ...   | ...      | ...    | ...                | ...    |

**Summary:** [narrative on project status, DOE funding context, and injection targets]
```

---

## Error Handling

| Condition | Meaning | Action |
|-----------|---------|--------|
| ScienceBase returns HTML | CDN routing issue | Retry with `?format=json` explicit in URL |
| EDX returns `{"success": false}` | Auth or bad parameter | Check API key header name; try `X-CKAN-API-Key` or `Authorization` |
| EDX returns empty `results` list | No matching packages | Broaden search; try single keyword like "carbon" or "CO2" |
| ScienceBase `items` array empty | No matching items | Try shorter search term; check spelling of formation names |
| Capacity values in Mt instead of Gt | Unit mismatch | Convert: 1 Gt = 1,000 Mt = 1e9 metric tonnes CO2 |
| File URL returns 403 | Restricted file | Note restriction; link to ScienceBase item page instead |

---

## Unit Conversion Reference

| Unit | Equals |
|------|--------|
| 1 Gt CO2 | 1 × 10^9 metric tonnes CO2 |
| 1 Gt CO2 | 1,000 Mt CO2 |
| 1 Mt CO2 | 1 × 10^6 metric tonnes CO2 |
| 1 Mt CO2 | 1,000 kt CO2 |
| 1 tonne CO2 | 44/12 = 3.67 tonnes CO2 per tonne C |

**Annual U.S. CO2 emissions context:** ~5 Gt CO2/year (2023). The 8,000 GtCO2
saline aquifer estimate represents ~1,600 years of current U.S. emissions.

---

## Caveats and Data Limitations

- **Atlas V is from 2015.** Site-specific feasibility studies may update these
  estimates significantly. Check EDX for post-2015 characterization data.
- **Capacity ≠ injectivity.** High estimated pore volume does not guarantee
  injectability — permeability, pressure, and brine chemistry matter.
- **Class VI permitting** is handled by EPA (primary) or state programs
  (Louisiana, North Dakota, Wyoming, Montana). Use `epa-enviro` skill for
  UIC well locations.
- **MRCSP** (Midwest Regional Carbon Sequestration Partnership) covers the
  Appalachian basin. Their final reports are on ScienceBase and EDX.
- Offshore saline aquifer capacity is not included in the Atlas V state totals.
