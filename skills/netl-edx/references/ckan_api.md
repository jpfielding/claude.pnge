# EDX CKAN v3 API Reference

Base URL: `https://edx.netl.doe.gov/api/3/action/`

## Authentication

**Header options** (any one works):
- `EDX-API-Key: YOUR_KEY`
- `X-CKAN-API-Key: YOUR_KEY`
- `Authorization: YOUR_KEY`

**Auth requirements by action:**

| Action | Read without key? | Notes |
|--------|-------------------|-------|
| `package_search` | Yes | Full search works without auth |
| `package_show` | Yes | Public datasets accessible without auth |
| `resource_search` | Yes | Works without auth |
| `group_list` | Partial | Returns only public groups; `all_fields=true` returns 500 error |
| `group_show` | Yes | Works with `include_datasets=true` |
| `tag_list` | Yes | Full list works without auth |
| `organization_list` | Yes | Returns basic org list without auth |
| Resource download | Yes | Direct URLs (edx.netl.doe.gov/storage/...) return 200 without auth |
| `package_create` | No | Write operations require auth |
| `resource_create` | No | Write operations require auth |

**Summary:** All read-only operations work without a key for public datasets.
A key is needed for write operations, accessing private datasets, and certain
admin-level queries. Always include the key when available to avoid edge cases.

---

## Core Actions

### package_search

Search datasets by keyword, tags, groups, organizations, and custom fields.

**Endpoint:** `GET /api/3/action/package_search`

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `q` | string | Full-text search query (Solr syntax) |
| `fq` | string | Filter query — Solr field:value filters (e.g., `groups:claimm-datasets`) |
| `sort` | string | Sort field and direction (e.g., `metadata_modified desc`, `score desc`) |
| `rows` | int | Max results per page (default: 10, max: 1000) |
| `start` | int | Offset for pagination (default: 0) |
| `facet.field` | JSON array | Fields to facet on (e.g., `["groups","tags"]`) |
| `facet.limit` | int | Max facet values to return (default: 50) |

**Example request:**
```bash
curl -s "https://edx.netl.doe.gov/api/3/action/package_search?q=lithium+produced+water&rows=5"
```

**Example with group filter:**
```bash
curl -s "https://edx.netl.doe.gov/api/3/action/package_search?q=lithium&fq=groups:claimm-datasets&rows=10"
```

**Response structure:**
```json
{
  "success": true,
  "result": {
    "count": 36,
    "results": [
      {
        "id": "e564c03f-...",
        "name": "dataset-slug-name",
        "title": "Human-Readable Dataset Title",
        "notes": "Dataset description / abstract...",
        "num_resources": 19,
        "num_tags": 6,
        "metadata_created": "2024-12-20T16:45:45.451100",
        "metadata_modified": "2025-01-12T18:15:33.648386",
        "state": "active",
        "type": "dataset",
        "extras": [
          {"key": "citation", "value": "..."},
          {"key": "program_or_project", "value": "RIC"},
          {"key": "doi", "value": "10.18141/..."}
        ],
        "groups": [
          {"name": "claimm-datasets", "title": "ClaiMM Datasets"}
        ],
        "resources": [
          {
            "id": "8dc8eb43-...",
            "name": "filename.xlsx",
            "format": "XLSX",
            "size": 217188,
            "url": "https://edx.netl.doe.gov/storage/f/edx/..."
          }
        ],
        "tags": [
          {"name": "Critical Minerals", "display_name": "Critical Minerals"}
        ]
      }
    ],
    "facets": {},
    "search_facets": {}
  }
}
```

---

### package_show

Get full metadata for a single dataset by name or ID.

**Endpoint:** `GET /api/3/action/package_show`

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `id` | string | Dataset name (slug) or UUID |

**Example:**
```bash
curl -s "https://edx.netl.doe.gov/api/3/action/package_show?id=lithium-geochemistry-and-regional-production-decline-curves-of-marcellus-shale-produced-water"
```

**Response:** Same structure as a single result in `package_search`, but with
complete metadata including all resources, extras, and relationships.

---

### resource_search

Search across all resources (files) in the EDX catalog.

**Endpoint:** `GET /api/3/action/resource_search`

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `query` | string | Field:value search (e.g., `format:CSV`, `name:lithium`) |
| `limit` | int | Max results (default: varies) |
| `offset` | int | Pagination offset |

**Example:**
```bash
curl -s "https://edx.netl.doe.gov/api/3/action/resource_search?query=format:CSV&limit=10"
```

**Response:**
```json
{
  "success": true,
  "result": {
    "count": 1219,
    "results": [
      {
        "id": "resource-uuid",
        "name": "filename.csv",
        "format": "CSV",
        "size": 66376,
        "url": "https://edx.netl.doe.gov/storage/f/edx/...",
        "package_id": "parent-dataset-uuid"
      }
    ]
  }
}
```

---

### group_list

List groups (collections) in the EDX catalog.

**Endpoint:** `GET /api/3/action/group_list`

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| (none required) | | Returns list of group name strings |

Note: `all_fields=true` causes a 500 error on EDX. Use `group_show` to get
full details for a specific group instead.

**Example:**
```bash
curl -s "https://edx.netl.doe.gov/api/3/action/group_list"
```

---

### group_show

Get details for a specific group including its datasets.

**Endpoint:** `GET /api/3/action/group_show`

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `id` | string | Group name (slug) or UUID |
| `include_datasets` | bool | Include dataset list (default: false) |
| `include_dataset_count` | bool | Include total dataset count (default: false) |

**Example:**
```bash
curl -s "https://edx.netl.doe.gov/api/3/action/group_show?id=claimm-datasets&include_datasets=true&include_dataset_count=true"
```

**Response:**
```json
{
  "success": true,
  "result": {
    "name": "claimm-datasets",
    "title": "ClaiMM Datasets",
    "description": "EDX submissions related to the CLAIMM project...",
    "package_count": 188,
    "packages": [
      {"name": "dataset-slug", "title": "Dataset Title", ...}
    ]
  }
}
```

---

### tag_list

List all tags used across EDX datasets.

**Endpoint:** `GET /api/3/action/tag_list`

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `query` | string | Filter tags starting with this string |
| `limit` | int | Max tags to return |

**Example:**
```bash
curl -s "https://edx.netl.doe.gov/api/3/action/tag_list?query=lithium"
```

---

### organization_list

List organizations that publish datasets on EDX.

**Endpoint:** `GET /api/3/action/organization_list`

**Example:**
```bash
curl -s "https://edx.netl.doe.gov/api/3/action/organization_list"
```

---

## Key Groups for PNGE Research

These group slugs can be used in `fq=groups:GROUP_NAME` filters:

| Group Slug | Title | Typical Dataset Count |
|------------|-------|----------------------|
| `claimm-datasets` | ClaiMM Datasets | ~188 |
| `claimm-geochemistry` | ClaiMM - Geochemistry | ~14 |
| `claimm-mine-waste` | ClaiMM - Mine Waste | ~11 |
| `claimm-databases` | ClaiMM - Databases | ~3 |
| `claimm-tools` | ClaiMM Tools | ~2 |
| `claimm-literature-and-presentations` | ClaiMM Literature and Presentations | ~4 |
| `newts` | NEWTS National Energy Water Treatment and Speciation Database | ~12 |
| `onshore-storage` | Onshore Storage | ~22 |
| `offshore-storage` | Offshore Storage | ~3 |
| `appalachian-basin-data-group` | Appalachian Basin Data Group | ~3 |
| `water-data-group` | Water Data Group | ~7 |
| `unconventional-resources` | Unconventional Resources | ~4 |
| `archived-kmd` | Archived KMD | ~630 |
| `lca-unit-process-library` | LCA Unit Process Library | ~12 |

---

## Solr Query Syntax for `q` and `fq`

EDX uses Apache Solr under the hood. Useful patterns:

```
# Boolean operators
q=lithium AND produced water
q=lithium OR magnesium
q=lithium NOT brine

# Phrase search
q="produced water"

# Field-specific search
fq=groups:claimm-datasets
fq=tags:lithium
fq=type:dataset

# Multiple filters (AND logic)
fq=groups:claimm-datasets&fq=tags:"Critical Minerals"

# Date range (metadata_modified is ISO 8601)
fq=metadata_modified:[2024-01-01T00:00:00Z TO *]
```

---

## Resource Download

Resources have direct download URLs in the `url` field. These work without
authentication for public datasets:

```bash
# Direct download — no auth needed for public resources
curl -o output.csv "https://edx.netl.doe.gov/storage/f/edx/2024/01/.../filename.csv"

# With auth header (for private resources)
curl -H "EDX-API-Key: $NETL_EDX_API_KEY" \
  -o output.csv "https://edx.netl.doe.gov/storage/f/edx/2024/01/.../filename.csv"
```

---

## Pagination

For `package_search`, paginate using `start` and `rows`:

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

For `resource_search`, paginate using `offset` and `limit`.

---

## Rate Limits

No documented rate limits for read operations. Be courteous:
- Avoid rapid-fire bulk requests
- Cache results when possible
- Use `rows` / `limit` parameters to fetch only what you need

---

## Common Extras Fields

Datasets often include these in the `extras` array:

| Key | Description |
|-----|-------------|
| `citation` | Full citation string |
| `doi` | DOI identifier |
| `program_or_project` | DOE program (e.g., "RIC") |
| `project_number` | DOE project number |
| `publication_date` | Publication date |
| `point_of_contact` | Contact name |
| `poc_email` | Contact email |
| `netl_product` | Whether this is an NETL product ("yes"/"no") |
| `geospatial` | Whether dataset has geospatial data ("yes"/"no") |
| `aiml_product` | Whether AI/ML related ("yes"/"no") |
| `spatial` | GeoJSON bounding geometry |
