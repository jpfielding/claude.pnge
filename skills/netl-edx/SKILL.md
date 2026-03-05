---
name: netl-edx
description: >
  Search, discover, and retrieve datasets from the DOE NETL Energy Data eXchange
  (EDX), a CKAN-based repository of energy research data products. Covers the
  ClaiMM critical minerals and materials platform, NEWTS produced water
  geochemistry, carbon storage, unconventional resources, reservoir engineering,
  and all NETL-funded research data. Use this skill when the user asks about NETL
  datasets, DOE energy research data, critical minerals characterization, ClaiMM,
  produced water geochemistry from DOE labs, carbon capture and storage datasets,
  geothermal research data, or fossil energy R&D data products. Trigger phrases
  include "NETL data", "EDX dataset", "ClaiMM", "critical minerals data from DOE",
  "NETL produced water", "energy data exchange", "DOE research dataset", "FECM
  data", "carbon storage data NETL", "NEWTS database". Produces dataset summaries,
  resource listings, and download URLs with narrative analysis.
---

# NETL Energy Data eXchange (EDX)

Searches and retrieves datasets from the DOE NETL Energy Data eXchange (EDX)
using its CKAN v3 REST API at `https://edx.netl.doe.gov/api/3/`.

EDX hosts thousands of datasets from NETL and DOE-funded research including
critical minerals characterization (ClaiMM), produced water geochemistry (NEWTS),
carbon storage, unconventional resources, and more.

## API Key Handling

Resolution order (stop at first success):

1. **`~/.config/netl-edx/credentials`** (default) -- parse `api_key=VALUE` from this file
2. **`NETL_EDX_API_KEY` env var** -- fallback if credentials file is absent
3. **User-provided in conversation** -- fallback if neither above is set
4. **Prompt the user** -- "Please provide your NETL EDX API key. Get one free at https://edx.netl.doe.gov/ -- sign up, then go to your profile page and hover to reveal your API key. Store it in `~/.config/netl-edx/credentials` as `api_key=YOUR_KEY` (chmod 600)."

Never hardcode or log the key. Pass it as a request header.

**Note on auth:** Most read-only operations (package_search, package_show,
resource_search, tag_list, resource downloads) work without a key for public
datasets. A key is required for write operations and private datasets. Always
include the key when available to avoid edge cases.

**Reading the credentials file (bash):**
```bash
KEY=$(grep '^api_key=' ~/.config/netl-edx/credentials 2>/dev/null | cut -d= -f2)
[ -z "$KEY" ] && KEY="${NETL_EDX_API_KEY}"
```

**Reading the credentials file (Python):**
```python
from pathlib import Path
import os

def resolve_edx_key() -> str | None:
    creds = Path.home() / ".config" / "netl-edx" / "credentials"
    if creds.exists():
        for line in creds.read_text().splitlines():
            if line.strip().startswith("api_key="):
                return line.strip().removeprefix("api_key=")
    return os.environ.get("NETL_EDX_API_KEY")
```

**Key header options** (any one works):
- `EDX-API-Key: YOUR_KEY`
- `X-CKAN-API-Key: YOUR_KEY`
- `Authorization: YOUR_KEY`

---

## API Structure

**Base URL:** `https://edx.netl.doe.gov/api/3/action/`

EDX runs a CKAN v3 instance. All responses are JSON with this envelope:
```json
{
  "success": true,
  "result": { ... }
}
```

On error:
```json
{
  "success": false,
  "error": { "__type": "Not Found Error", "message": "..." }
}
```

**Key actions:**

| Action | Method | Description |
|--------|--------|-------------|
| `package_search` | GET | Search datasets by keyword, tags, groups |
| `package_show` | GET | Get full metadata for a single dataset |
| `resource_search` | GET | Search resources (files) across all datasets |
| `group_list` | GET | List available groups/collections |
| `group_show` | GET | Get group details with its datasets |
| `tag_list` | GET | List all tags or filter by prefix |
| `organization_list` | GET | List publishing organizations |

See `references/ckan_api.md` for full parameter reference and response examples.

### package_search Parameters

| Parameter | Example | Notes |
|-----------|---------|-------|
| `q` | `q=lithium+produced+water` | Full-text Solr query |
| `fq` | `fq=groups:claimm-datasets` | Filter query (Solr field:value) |
| `rows` | `rows=20` | Results per page (default 10, max 1000) |
| `start` | `start=0` | Pagination offset |
| `sort` | `sort=metadata_modified+desc` | Sort field + direction |
| `facet.field` | `facet.field=["groups"]` | Facet on groups, tags, etc. |

### Solr Query Syntax

```
q=lithium AND "produced water"     # Boolean + phrase
q=lithium OR magnesium             # OR logic
fq=groups:claimm-datasets          # Filter by group
fq=tags:"Critical Minerals"        # Filter by tag
fq=metadata_modified:[2024-01-01T00:00:00Z TO *]  # Date range
```

---

## Key Collections

EDX organizes datasets into groups. These are the most relevant for PNGE research:

### ClaiMM (Critical Minerals and Materials)

The ClaiMM platform is the primary collection for critical minerals data on EDX.

| Group | Slug | Datasets | Focus |
|-------|------|----------|-------|
| ClaiMM Datasets | `claimm-datasets` | ~188 | All critical minerals datasets |
| ClaiMM Geochemistry | `claimm-geochemistry` | ~14 | Brine/water geochemistry |
| ClaiMM Mine Waste | `claimm-mine-waste` | ~11 | Produced waters, tailings, coal ash |
| ClaiMM Databases | `claimm-databases` | ~3 | Large compiled databases |
| ClaiMM Tools | `claimm-tools` | ~2 | Software tools (e.g., CM3 Matchmaker) |

**Example -- search ClaiMM for lithium data:**
```bash
curl -s "https://edx.netl.doe.gov/api/3/action/package_search?q=lithium&fq=groups:claimm-datasets&rows=10" \
  -H "EDX-API-Key: $NETL_EDX_API_KEY"
```

### NEWTS (National Energy Water Treatment and Speciation)

Water quality data from energy processes -- produced water, flowback, AMD.

| Group | Slug | Datasets | Focus |
|-------|------|----------|-------|
| NEWTS Database | `newts` | ~12 | Produced water geochemistry, treatment data |

### Other Relevant Groups

| Group | Slug | Datasets |
|-------|------|----------|
| Onshore Storage | `onshore-storage` | ~22 |
| Offshore Storage | `offshore-storage` | ~3 |
| Appalachian Basin | `appalachian-basin-data-group` | ~3 |
| Water Data | `water-data-group` | ~7 |
| Unconventional Resources | `unconventional-resources` | ~4 |
| LCA Unit Process Library | `lca-unit-process-library` | ~12 |
| Archived KMD | `archived-kmd` | ~630 |

---

## Workflow

### Step 1 -- Resolve Intent

Map the user's question to:
- A **search query** (`q=` keyword terms)
- An optional **group filter** (`fq=groups:GROUP_SLUG`)
- Whether they want to **discover** datasets, get **details** for a known dataset, or **download** a resource

Common intent mappings:

| User says | Action | Parameters |
|-----------|--------|------------|
| "Find NETL lithium data" | `package_search` | `q=lithium` |
| "ClaiMM produced water datasets" | `package_search` | `q=produced+water&fq=groups:claimm-datasets` |
| "What's in dataset X?" | `package_show` | `id=dataset-slug` |
| "Download the CSV from that dataset" | Get resource URL from `package_show` | Direct download |
| "NEWTS geochemistry data" | `package_search` | `q=geochemistry&fq=groups:newts` |
| "Critical minerals datasets from DOE" | `package_search` | `q=critical+minerals&fq=groups:claimm-datasets` |
| "What groups exist on EDX?" | `group_list` | (no params) |

### Step 2 -- Search Datasets

```bash
# Search with keyword
curl -s "https://edx.netl.doe.gov/api/3/action/package_search?q=lithium+produced+water&rows=10" \
  -H "EDX-API-Key: $NETL_EDX_API_KEY"
```

Parse the response:
- `result.count` -- total matching datasets
- `result.results[]` -- array of dataset objects
- Each dataset has: `name`, `title`, `notes` (description), `num_resources`, `resources[]`, `tags[]`, `groups[]`, `extras[]`

### Step 3 -- Get Dataset Details

For a specific dataset, use `package_show` to get full metadata including all resources:

```bash
curl -s "https://edx.netl.doe.gov/api/3/action/package_show?id=DATASET_SLUG" \
  -H "EDX-API-Key: $NETL_EDX_API_KEY"
```

Key fields in the response:
- `title` -- human-readable name
- `notes` -- full description / abstract
- `resources[]` -- list of files with `name`, `format`, `size`, `url`
- `extras[]` -- key-value pairs including `citation`, `doi`, `program_or_project`
- `tags[]` -- subject tags
- `groups[]` -- collection memberships

### Step 4 -- Download Resources

Resources have direct download URLs in `resources[].url`:

```bash
# Direct download (public resources work without auth)
curl -o output.csv "https://edx.netl.doe.gov/storage/f/edx/2024/.../filename.csv"

# With auth header (for private resources or reliability)
curl -H "EDX-API-Key: $NETL_EDX_API_KEY" \
  -o output.csv "https://edx.netl.doe.gov/storage/f/edx/2024/.../filename.csv"
```

**Large file warning:** Some datasets contain files over 100 MB. Check `resources[].size`
before downloading and warn the user.

### Step 5 -- Produce Output

**Format: Dataset Table + Resource Details + Narrative**

Present a markdown table of matching datasets (cap at ~15 rows), then detail the
most relevant dataset's resources, followed by a narrative summary.

**Example output structure:**
```
## EDX: Lithium in Produced Water Datasets (36 matches)

| Dataset | Resources | Modified | Groups |
|---------|-----------|----------|--------|
| PA DEP 26r Produced Water Compositions | 19 | 2025-01-12 | ClaiMM, NEWTS |
| Lithium Geochemistry Marcellus PW | 4 | 2024-05-31 | ClaiMM, NEWTS |
| ... | ... | ... | ... |

### Top Result: PA DEP 26r Produced Water Compositions

19 resources (CSV, XLSX, PDF):
| File | Format | Size |
|------|--------|------|
| PA_DEP_26r_processed.csv | CSV | 648 KB |
| PA_OLI_processed_reordered.xlsx | XLSX | 212 KB |
| README_PA_DEP_26r_Produced_Water.pdf | PDF | 187 KB |
| ... | ... | ... |

**Summary:** Found 36 datasets matching "lithium produced water" on NETL EDX.
The most relevant is the PA DEP 26r dataset containing geochemical compositions
of 1000+ produced water streams from Marcellus wells in Pennsylvania, formatted
for OLI Studio and Geochemist Workbench modeling. Data covers mid-2012 to
early-2020. Additional ML-predicted values are included via CoDaRT software.

**Citation:** Mackey et al., DOI: 10.18141/2483335

**Download:** Files can be accessed directly at the URLs above.
No API key required for public resources.
```

---

## Pagination

For large result sets, paginate using `start` and `rows`:

```python
start = 0
rows = 100
all_results = []
while True:
    data = search(q="lithium", start=start, rows=rows)
    all_results.extend(data["result"]["results"])
    start += rows
    if start >= data["result"]["count"]:
        break
```

Warn the user if the result count exceeds 100 and ask if they want to narrow
the search or paginate through all results.

## Error Handling

| HTTP Code | CKAN Error | Action |
|-----------|------------|--------|
| 200 + `success: false` | Validation Error | Check parameter names and values; fix and retry |
| 200 + `success: false` | Not Found Error | Dataset or group slug is wrong; search for correct name |
| 403 | Authorization Error | API key missing or invalid; prompt user to verify key |
| 404 | Not Found | Action endpoint does not exist; check CKAN action name |
| 500 | Internal Server Error | Server-side issue; retry once, then try simpler query |
| Connection error | Timeout / DNS | EDX may be down; wait and retry |

**Known quirks:**
- `group_list` with `all_fields=true` returns a 500 error on EDX. Use `group_show`
  with `include_datasets=true` instead to get group details.
- Some dataset slugs are very long; use the `id` (UUID) as an alternative.
- The `resource_search` `query` parameter uses `field:value` syntax, not free text.

---

## Caveats

- **API key recommended:** While most reads work without auth, some edge cases
  (rate limiting, private datasets) require a key. Always include it when available.
- **Data formats vary:** Resources include CSV, XLSX, PDF, GeoJSON, shapefiles,
  netCDF, and custom formats. Not all are machine-parseable.
- **Large files:** Some datasets contain multi-gigabyte files. Always check
  `resources[].size` before downloading.
- **No real-time data:** EDX is a repository of research data products, not
  a live data feed. Datasets are published and occasionally updated.
- **Quality varies:** Data quality depends on the submitting research team.
  Check the README/documentation resources within each dataset.
- **Citation required:** Most datasets have citation requirements in the
  `extras` array. Always surface the citation when presenting data.
- **ClaiMM focus:** The ClaiMM platform is actively maintained and growing.
  Dataset counts are approximate and increase over time.

---

## Implementation Notes

- **Prefer `bash_tool` with `curl` + `jq`** for API calls in Claude's environment
- **Python client** -- see `references/python_example.py` (stdlib only: `urllib`, `json`, `pathlib`)
- **CKAN API reference** -- see `references/ckan_api.md` for full action/parameter documentation
- All responses are JSON; use `jq` for bash or `json` module for Python
- Resource download URLs are stable and can be shared directly with users
- EDX does not have a formal rate limit, but be courteous with request volume
