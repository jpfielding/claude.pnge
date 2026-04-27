---
name: datacite-doi
description: >
  Search and resolve DataCite DOIs for research data, datasets, software, and
  technical reports published by USGS, DOE OSTI, Zenodo, figshare, Dryad, and
  other repositories. Use this skill whenever the user asks about research
  data DOIs, dataset DOIs, USGS data release DOIs (prefix 10.5066), OSTI DOIs
  (prefix 10.11578), Zenodo DOIs (prefix 10.5281), figshare DOIs (prefix
  10.6084), or any DOI that is NOT a journal article. Trigger for phrases like
  "DataCite", "research data DOI", "USGS DOI", "OSTI DOI", "ScienceBase DOI",
  "Zenodo", "figshare", "dataset DOI", "lithium produced water dataset",
  "find data release on the Marcellus", "resolve data DOI metadata", or any
  request involving scientific data or software publication lookup.
  Complements the crossref-doi skill — DataCite covers research data and
  grey literature; Crossref covers peer-reviewed articles. When uncertain
  which registry a DOI belongs to, try DataCite first for prefixes 10.5066
  (USGS), 10.11578 (OSTI), 10.5281 (Zenodo), 10.6084 (figshare), 10.5061
  (Dryad); Crossref for everything else. No API key required.
---

# DataCite DOI Skill

Searches and resolves DataCite-registered DOIs via the DataCite REST API
(api.datacite.org). Covers 70M+ DOIs for research data, datasets, software,
grey literature, and technical reports from USGS, DOE OSTI, Zenodo,
figshare, Dryad, and 3,000+ other repositories.

## Authentication

**None required** for read operations. Unauthenticated requests are rate
limited to roughly 3,000 requests per 5 minutes per IP. No `mailto` or
polite-pool convention — DataCite treats all reads equally.

Always send `Accept: application/vnd.api+json` — the API follows the
JSON:API specification.

## When to Use DataCite vs Crossref

| Content type                       | Registry  | Prefix examples |
|-----------------------------------|-----------|-----------------|
| Peer-reviewed journal articles     | Crossref  | 10.1016, 10.1021, 10.1029 |
| Conference proceedings             | Crossref  | 10.2118 (SPE), 10.1109 |
| USGS data releases                 | DataCite  | 10.5066 |
| USGS publications (most)           | Crossref  | 10.3133 |
| DOE OSTI technical reports / data  | DataCite  | 10.11578, 10.2172 (mixed) |
| Zenodo datasets / software         | DataCite  | 10.5281 |
| figshare datasets                  | DataCite  | 10.6084 |
| Dryad datasets                     | DataCite  | 10.5061 |

Rule of thumb: if the DOI lands on `sciencebase.gov`, `osti.gov`,
`zenodo.org`, `figshare.com`, or `datadryad.org`, it is a DataCite DOI.

---

## API Structure

**Base URL:** `https://api.datacite.org/`

**Primary endpoints:**

| Endpoint                    | Purpose |
|-----------------------------|---------|
| `GET /dois`                 | Search DOIs by query, client, provider, year, type |
| `GET /dois/{doi}`           | Resolve a single DOI to full metadata |
| `GET /clients`              | List/search data-publishing clients (repositories) |
| `GET /providers`            | List/search data providers (consortia, networks) |
| `GET /resource-types`       | List resource-type vocabulary |

**Key query parameters for `/dois`:**

| Parameter            | Example                             | Notes |
|----------------------|-------------------------------------|-------|
| `query`              | `query=lithium+produced+water`      | Full-text; supports Lucene syntax |
| `client-id`          | `client-id=usgs.prod`               | Lowercase; filter to one repository |
| `provider-id`        | `provider-id=usgs`                  | Broader than client (consortium) |
| `resource-type-id`   | `resource-type-id=dataset`          | dataset, text, software, image, other |
| `publication-year`   | `publication-year=2024`             | Or range via `query=publicationYear:[2020 TO 2024]` |
| `page[number]`       | `page[number]=1`                    | 1-indexed |
| `page[size]`         | `page[size]=25`                     | Max 1000 |
| `sort`               | `sort=-created`                     | `-` for descending |

**Known client IDs relevant to PNGE research** (verified against live API;
always confirm with `/clients?query=…` since IDs drift):

| Client ID        | Publisher                                           | Scope |
|------------------|-----------------------------------------------------|-------|
| `usgs.prod`      | USGS DOI Tool Production (issues 10.5066 prefix)    | USGS data releases (ScienceBase) |
| `doe.osti`       | DOE Office of Scientific & Technical Information    | DOE-funded reports, datasets |
| `cern.zenodo`    | Zenodo (CERN)                                       | General research data + software |
| `pryl.mxfyrs`    | National Geological & Geophysical Data Preservation | NGGDPP drill cores, logs |
| `xaqp.zqnehk`    | SESAR_USGS                                          | USGS sample registry |

Note: legacy documentation sometimes cites IDs like `USGS.SCIENCEBASE`,
`OSTI.ETDEWEB`, `ZENODO.ZENODO`, `FIGSHARE.ARS` — these forms return
zero results against the live v2 API. Use the lowercase forms above.

---

## Workflow

### Step 1 — Resolve Intent

Classify the request:

- **Lookup** — user gave a DOI → `GET /dois/{doi}`
- **Topic search** — user asked for datasets on a topic → `GET /dois?query=…`
- **Repository filter** — user wants USGS or OSTI output only → add `client-id`
- **Recency filter** — user wants recent data → add `publication-year` or sort by `-created`

If uncertain whether a DOI is DataCite or Crossref, try `GET /dois/{doi}`
first; a 404 means it is not in DataCite and you should fall back to
Crossref.

### Step 2 — Build the Query

Combine full-text search with facet filters. URL-encode brackets in
`page[size]` as `%5B` / `%5D`.

Common patterns:

```
# Topic search across all DataCite
query=lithium+produced+water&page[size]=25

# USGS data releases only on a topic
query=lithium+brine&client-id=usgs.prod

# OSTI datasets from 2023–2024
query=produced+water&client-id=doe.osti&publication-year=2024

# Recent Marcellus data releases, any repository
query=Marcellus+Shale&resource-type-id=dataset&sort=-created
```

### Step 3 — Fetch

```bash
curl -s -H "Accept: application/vnd.api+json" \
  "https://api.datacite.org/dois?query=lithium+brine&client-id=usgs.prod&page%5Bsize%5D=10"
```

### Step 4 — Parse Response

JSON:API envelope:

```json
{
  "data": [
    {
      "id": "10.5066/p9zkrwqf",
      "type": "dois",
      "attributes": {
        "doi": "10.5066/P9ZKRWQF",
        "titles": [{"title": "Lithium Deposits in the United States"}],
        "creators": [{"name": "Bradley, D.C.", "nameType": "Personal"}],
        "publisher": "U.S. Geological Survey",
        "publicationYear": 2019,
        "types": {"resourceTypeGeneral": "Dataset", "resourceType": "Data Release"},
        "descriptions": [{"description": "This data release provides...", "descriptionType": "Abstract"}],
        "url": "https://www.sciencebase.gov/catalog/item/5d0baffce4b0e3d31162044c",
        "subjects": [{"subject": "lithium"}],
        "container": {"identifier": "..."},
        "rightsList": [{"rights": "Public Domain"}]
      }
    }
  ],
  "meta": {"total": 7, "totalPages": 1, "page": 1},
  "links": {"self": "...", "next": "..."}
}
```

Primary fields to extract:

- `attributes.doi` — canonical DOI (upper/lowercase vary; normalize)
- `attributes.titles[0].title`
- `attributes.creators[].name` — join first 3, then "et al."
- `attributes.publisher` — repository / issuing body
- `attributes.publicationYear`
- `attributes.types.resourceTypeGeneral` — Dataset, Text, Software, etc.
- `attributes.descriptions[]` where `descriptionType == "Abstract"`
- `attributes.url` — landing page (always use this to verify data still exists)

### Step 5 — Produce Output

Two blocks: a markdown table of hits (cap at ~15 rows) and a narrative
summary. Match the EIA skill style — precise, structured, with units
and caveats.

**Example output structure:**

```
## DataCite: "lithium produced water" (USGS client = usgs.prod)

| DOI                 | Year | Type    | Title (truncated)                        |
|---------------------|------|---------|------------------------------------------|
| 10.5066/p9zkrwqf    | 2019 | Dataset | Lithium Deposits in the United States    |
| 10.5066/p9dsrczj    | 2024 | Dataset | USGS National Produced Waters v3.0       |
| ...                 | ...  | ...     | ...                                      |

**Summary:** 7 USGS data releases match "lithium brine". The most recent
(2024) is the National Produced Waters Geochemical Database v3.0, which
is the primary nationwide source for produced-water Li concentrations.
The 2019 Lithium Deposits release enumerates ~20 U.S. occurrences with
descriptive metadata but no brine chemistry. No 10.5066-prefix data
release specifically targets Appalachian Basin Li recovery — for that,
fall back to DOE OSTI (`client-id=doe.osti`) or NETL EDX.

**Caveats:** DataCite metadata quality varies. Some records have empty
abstracts, missing publication years, or inconsistent resource types.
Always open the `url` to verify the dataset is still hosted and current.
```

---

## Working curl Examples

**1. Search for lithium produced-water data releases at USGS:**

```bash
curl -s -H "Accept: application/vnd.api+json" \
  "https://api.datacite.org/dois?query=lithium+produced+water&client-id=usgs.prod&page%5Bsize%5D=10" \
  | jq -r '.data[] | "\(.id)\t\(.attributes.publicationYear)\t\(.attributes.titles[0].title)"'
```

**2. Resolve a single DOI:**

```bash
curl -s -H "Accept: application/vnd.api+json" \
  "https://api.datacite.org/dois/10.5066/p9zkrwqf" \
  | jq '.data.attributes | {doi, title: .titles[0].title, year: .publicationYear, url, abstract: .descriptions[0].description}'
```

**3. OSTI lithium reports, 2024 only:**

```bash
curl -s -H "Accept: application/vnd.api+json" \
  "https://api.datacite.org/dois?query=lithium&client-id=doe.osti&publication-year=2024&page%5Bsize%5D=10" \
  | jq '.meta.total, (.data[] | "\(.id) | \(.attributes.titles[0].title)")'
```

**4. Find the publishing client for a prefix:**

```bash
curl -s -H "Accept: application/vnd.api+json" \
  "https://api.datacite.org/clients?query=usgs&page%5Bsize%5D=10" \
  | jq -r '.data[] | "\(.id)\t\(.attributes.name)"'
```

All four examples have been run against the live API and return non-empty
results as of the skill build date.

---

## Pagination

DataCite uses 1-indexed pages. Request `page[size]` up to 1000 and walk
`page[number]` until `meta.totalPages` is reached, or follow the
`links.next` URL when present.

```bash
PAGE=1
while :; do
  resp=$(curl -s -H "Accept: application/vnd.api+json" \
    "https://api.datacite.org/dois?query=lithium+brine&page%5Bsize%5D=100&page%5Bnumber%5D=$PAGE")
  echo "$resp" | jq -r '.data[].id'
  last=$(echo "$resp" | jq -r '.meta.totalPages')
  [ "$PAGE" -ge "$last" ] && break
  PAGE=$((PAGE+1))
done
```

Warn the user and request filtering if `meta.total` exceeds ~2,000 rows —
DataCite has soft caps on deep pagination and wide scans.

---

## Error Handling

| HTTP Code | Meaning                    | Action |
|-----------|----------------------------|--------|
| 200       | OK (may be empty `data[]`) | Check `meta.total`; narrow or broaden query |
| 400       | Bad query syntax           | Escape Lucene special chars, verify facet names |
| 404       | DOI not in DataCite        | Fall back to crossref-doi skill |
| 406       | Wrong Accept header        | Set `Accept: application/vnd.api+json` |
| 429       | Rate limited               | Back off ~30s; batch by prefix instead of broad scan |
| 503       | DataCite transient         | Retry with exponential backoff, max 3 tries |

Never follow `links.next` blindly in a loop — always cap iterations.

---

## Caveats and Bias Notes

- **Metadata quality varies by client.** USGS (`usgs.prod`) and Zenodo
  (`cern.zenodo`) generally have complete titles, creators, abstracts,
  and resource types. Some smaller university repositories publish
  DOIs with empty abstracts or miscategorized resource types.
- **`resourceTypeGeneral` is a controlled vocabulary** (Dataset, Text,
  Software, Image, Audiovisual, Collection, Model, Service, Workflow,
  PhysicalObject, Other) but `resourceType` (the free-text subtype) is
  author-supplied and inconsistent across providers. Do not filter on
  `resourceType` — filter on `resource-type-id` (maps to
  `resourceTypeGeneral`) instead.
- **Versioning is opaque.** A single dataset may have multiple DOIs
  (one per version) with no cross-linking in the base metadata; check
  `relatedIdentifiers` for `IsVersionOf` / `HasVersion` relationships.
- **Abstract may be absent.** Many pre-2018 DataCite records lack
  descriptions entirely. If `descriptions[]` is empty, fetch the
  `attributes.url` landing page for a human-readable summary — do not
  fabricate an abstract.
- **Not all USGS DOIs live under `usgs.prod`.** Some sample-registry
  and data-preservation DOIs use sibling clients (`xaqp.zqnehk`,
  `pryl.mxfyrs`). For broad USGS scans, prefer `provider-id=usgs` over
  a single `client-id`.
- **Client IDs drift.** DataCite has renamed clients multiple times.
  Verify with `GET /clients?query=…` before hardcoding an ID in a
  production script.
- **Duplicate with Crossref is rare but possible.** A few USGS
  publications have both a DataCite and Crossref record. When in doubt,
  prefer Crossref's record for citation metadata (it has richer author
  affiliations and license info).

---

## Implementation Notes

- **Prefer `bash_tool` with `curl` + `jq`** for ad-hoc queries.
- **Go client** — see `references/golang_client.go` for a paginating
  client (`DataCiteClient`, `SearchDOIs`, `ResolveDOI`, pretty-printer).
- **Detailed API reference** — see `references/api_reference.md` for
  the full JSON:API schema, Lucene query syntax, and client-ID lookup.
- Always URL-encode `page[size]` and `page[number]` as `page%5Bsize%5D`
  and `page%5Bnumber%5D`.
- DataCite honors `If-None-Match` / `ETag` for conditional GETs — use
  this when polling for new records.
- The `random=true` query parameter returns a random sample — useful
  for spot-checking metadata quality but never for reproducible output.
