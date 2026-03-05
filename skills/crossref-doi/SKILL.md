---
name: crossref-doi
description: >
  Resolve DOIs and search scholarly metadata via the Crossref REST API.
  Use this skill whenever the user asks to look up a DOI, find citation metadata,
  search for journal articles or conference papers, retrieve author lists,
  citation counts, publication dates, or abstracts for academic works. Trigger
  for phrases like "look up this DOI", "find papers about lithium extraction",
  "who wrote this paper", "citation count for DOI", "search Crossref for
  produced water brine", "journal articles on DLE", "recent publications on
  magnesium recovery", "resolve DOI metadata", or any request involving
  scholarly publication lookup. Pairs with usgs-pubs and doe-osti skills
  to resolve DOIs returned by those sources. Covers 140M+ DOI-registered
  works across all disciplines. No API key required — uses the Crossref
  polite pool via mailto parameter for faster rate limits.
---

# Crossref DOI Skill

Resolves DOIs and searches scholarly publication metadata via the Crossref
REST API (api.crossref.org). Covers 140M+ DOI-registered works including
journal articles, conference proceedings, books, datasets, and reports.

## Authentication

No API key required. Add `mailto=user@example.com` to all requests
for access to the **polite pool** (faster rate limits, priority routing).

Resolution order for the mailto address:

1. **`~/.config/crossref/credentials`** — parse `mailto=user@example.com`
2. **`CROSSREF_MAILTO` env var** — fallback
3. **Omit** — still works but hits the public pool (slower, rate-limited)

**Reading the credentials file (bash):**
```bash
MAILTO=$(grep '^mailto=' ~/.config/crossref/credentials 2>/dev/null | cut -d= -f2)
[ -z "$MAILTO" ] && MAILTO="${CROSSREF_MAILTO}"
```

This is not a secret credential — it is a contact email sent in the clear
so Crossref can reach you if your usage is problematic. Any valid email works.

---

## API Structure

**Base URL:** `https://api.crossref.org/`

### Core Endpoints

| Endpoint | Description |
|----------|-------------|
| `works/{doi}` | Get metadata for a specific DOI |
| `works?query=...` | Full-text search across all metadata fields |
| `works?query.bibliographic=...` | Bibliographic-style search (title + author + year) |
| `works?query.title=...` | Title-only search |
| `works?query.author=...` | Author-only search |
| `types` | List all work types (journal-article, proceedings-article, etc.) |
| `journals/{issn}` | Journal metadata by ISSN |
| `journals/{issn}/works` | Works published in a specific journal |
| `prefixes/{prefix}` | Publisher info by DOI prefix |
| `members/{id}` | Publisher/member metadata |
| `funders/{id}` | Funder metadata |
| `funders/{id}/works` | Works funded by a specific funder |

### Query Parameters

| Parameter | Example | Notes |
|-----------|---------|-------|
| `query` | `query=lithium+brine` | Full-text search across all fields |
| `query.bibliographic` | `query.bibliographic=Smith+2023+lithium` | Simulates bibliographic lookup |
| `query.title` | `query.title=direct+lithium+extraction` | Title search only |
| `query.author` | `query.author=Stringfellow` | Author name search |
| `filter` | `filter=from-pub-date:2023-01-01` | Comma-separated filter list |
| `select` | `select=DOI,title,author,type` | Return only specified fields (reduces payload) |
| `rows` | `rows=20` | Results per page (default 20, max 1000) |
| `offset` | `offset=20` | Pagination offset (max 10000) |
| `cursor` | `cursor=*` | Deep paging cursor (use for offset beyond 10000) |
| `sort` | `sort=relevance` | Sort field |
| `order` | `order=desc` | Sort direction |
| `mailto` | `mailto=you@example.com` | Polite pool access (faster rate limits) |

### Filter Parameters

Filters are passed as a comma-separated list in the `filter` parameter:

| Filter | Example | Description |
|--------|---------|-------------|
| `from-pub-date` | `from-pub-date:2023-01-01` | Published on or after date |
| `until-pub-date` | `until-pub-date:2024-12-31` | Published on or before date |
| `type` | `type:journal-article` | Work type |
| `has-abstract` | `has-abstract:true` | Only works with abstracts |
| `has-orcid` | `has-orcid:true` | Authors with ORCID IDs |
| `has-references` | `has-references:true` | Works with reference lists |
| `has-full-text` | `has-full-text:true` | Works with full-text links |
| `is-update` | `is-update:false` | Exclude corrections/errata |
| `funder` | `funder:10.13039/100000015` | DOE funder ID |
| `container-title` | `container-title:Water+Resources+Research` | Journal name |
| `doi` | `doi:10.1021/acs.est.2c03513` | Exact DOI match |
| `issn` | `issn:0043-1397` | Filter by journal ISSN |

### Common Work Types

| Type | Description |
|------|-------------|
| `journal-article` | Peer-reviewed journal article |
| `proceedings-article` | Conference paper |
| `book-chapter` | Chapter in an edited volume |
| `dataset` | Data publication |
| `report` | Technical report |
| `posted-content` | Preprint |
| `monograph` | Book/monograph |

### Sort Fields

| Sort | Description |
|------|-------------|
| `relevance` | Default — Crossref relevance score |
| `published` | Publication date |
| `indexed` | Date indexed in Crossref |
| `is-referenced-by-count` | Citation count (descending = most cited) |
| `references-count` | Number of references in bibliography |
| `score` | Internal relevance score |

---

## Workflow

### Step 1 -- Resolve Intent

Determine the operation type:

| User Intent | Endpoint | Key Parameters |
|-------------|----------|----------------|
| "Look up DOI 10.xxxx/yyyy" | `works/{doi}` | Direct DOI lookup |
| "Find papers about X" | `works?query=X` | Keyword search |
| "Papers by Author on X" | `works?query=X&query.author=Author` | Combined search |
| "Recent journal articles on X" | `works?query=X&filter=type:journal-article,from-pub-date:YYYY` | Filtered search |
| "Most cited papers on X" | `works?query=X&sort=is-referenced-by-count&order=desc` | Sorted search |
| "Resolve DOI from USGS/OSTI" | `works/{doi}` | Cross-skill DOI resolution |

### Step 2 -- Build and Execute Request

**Single DOI lookup:**
```bash
DOI="10.2118/1011-0046-jpt"
MAILTO="user@example.com"
curl -s "https://api.crossref.org/works/${DOI}?mailto=${MAILTO}"
```

**Keyword search with filters:**
```bash
curl -s "https://api.crossref.org/works?query=lithium+produced+water+brine\
  &filter=from-pub-date:2020-01-01,has-abstract:true,type:journal-article\
  &rows=20\
  &select=DOI,title,author,type,published-print,container-title,is-referenced-by-count,abstract\
  &sort=relevance\
  &mailto=user@example.com"
```

**Bibliographic search (best for matching a citation string):**
```bash
curl -s "https://api.crossref.org/works?query.bibliographic=Stringfellow+2014+lithium+oilfield+brine\
  &rows=5\
  &select=DOI,title,author,published-print,container-title\
  &mailto=user@example.com"
```

### Step 3 -- Parse Response

**Single work response (`works/{doi}`):**
```json
{
  "status": "ok",
  "message-type": "work",
  "message": {
    "DOI": "10.2118/1011-0046-jpt",
    "title": ["Brine Management: Produced Water and Frac Flowback Brine"],
    "author": [{"given": "David", "family": "Burnett", "affiliation": [...]}],
    "container-title": ["Journal of Petroleum Technology"],
    "type": "journal-article",
    "published-print": {"date-parts": [[2011, 10, 1]]},
    "is-referenced-by-count": 1,
    "abstract": "...",
    "link": [{"URL": "...", "content-type": "...", "intended-application": "..."}]
  }
}
```

**Search response (`works?query=...`):**
```json
{
  "status": "ok",
  "message-type": "work-list",
  "message": {
    "total-results": 2171593,
    "items-per-page": 20,
    "query": {"start-index": 0, "search-terms": "lithium produced water brine"},
    "items": [
      { "DOI": "...", "title": [...], "author": [...], ... }
    ],
    "next-cursor": "AoJ/..."
  }
}
```

Key fields to extract per work:

| Field | Type | Notes |
|-------|------|-------|
| `DOI` | string | The DOI |
| `title` | array of strings | Usually one element |
| `author` | array of objects | Each has `given`, `family`, `affiliation`, optional `ORCID` |
| `container-title` | array of strings | Journal or proceedings name |
| `type` | string | `journal-article`, `proceedings-article`, etc. |
| `published-print` | object | `date-parts: [[year, month, day]]` |
| `published-online` | object | Same structure as published-print |
| `is-referenced-by-count` | integer | Citation count (Crossref-tracked) |
| `abstract` | string | May contain JATS XML markup |
| `link` | array of objects | Full-text links with content-type |
| `reference` | array of objects | Bibliography entries (if `has-references`) |
| `funder` | array of objects | Funding sources with `name`, `DOI`, `award` |
| `subject` | array of strings | Subject categories |

### Step 4 -- Format Dates

The `date-parts` field uses variable-length arrays:
- `[[2024, 3, 15]]` = March 15, 2024
- `[[2024, 3]]` = March 2024
- `[[2024]]` = 2024

Handle all three cases. Use the most specific date available.

### Step 5 -- Clean Abstract Text

Abstracts may contain JATS XML tags (`<jats:p>`, `<jats:italic>`, etc.).
Strip XML tags before display:
```bash
echo "$ABSTRACT" | sed 's/<[^>]*>//g'
```

### Step 6 -- Produce Output

**Format: Metadata Table + Narrative**

For a single DOI lookup:
```
## DOI: 10.2118/1011-0046-jpt

| Field | Value |
|-------|-------|
| Title | Brine Management: Produced Water and Frac Flowback Brine |
| Authors | David Burnett (Texas A&M University) |
| Journal | Journal of Petroleum Technology |
| Date | October 2011 |
| Type | journal-article |
| Citations | 1 |
| DOI Link | https://doi.org/10.2118/1011-0046-jpt |

**Abstract:** R&D Grand Challenges - This is the third in a series...
```

For a search:
```
## Crossref Search: "lithium produced water brine" (2020--present, journal articles)

Found 847 results. Showing top 10 by relevance:

| # | Year | Title | Journal | Citations | DOI |
|---|------|-------|---------|-----------|-----|
| 1 | 2023 | Direct Lithium Extraction from... | Minerals | 8 | 10.3390/... |
| 2 | 2024 | Effect of buffer on direct... | New J Chem | 3 | 10.1039/... |
| ... | ... | ... | ... | ... | ... |

**Summary:** Search returned 847 journal articles published since 2020
matching "lithium produced water brine". The most-cited result (8 citations)
covers DLE technology assessment for seawater brine. Results span journals
including Minerals, Water Research, and ACS ES&T...
```

---

## Pagination

**Offset-based (for small result sets, offset max 10000):**
```
&offset=0&rows=20   (page 1)
&offset=20&rows=20  (page 2)
```

**Cursor-based (for deep paging beyond 10000):**
1. First request: `&cursor=*&rows=100`
2. Response includes `next-cursor` in message
3. Subsequent request: `&cursor=<next-cursor-value>&rows=100`
4. Continue until `items` is empty

Warn the user if total results exceed 1000 and suggest narrowing filters.

## Error Handling

| HTTP Code | Meaning | Action |
|-----------|---------|--------|
| 200 | Success | Parse normally |
| 404 | DOI not found | Report DOI not in Crossref; suggest checking doi.org directly |
| 400 | Bad request | Check filter syntax, invalid field names |
| 429 | Rate limited | Wait and retry; suggest adding mailto for polite pool |
| 503 | Service unavailable | Retry after 5 seconds |

**Common issues:**
- DOI contains special characters: URL-encode the DOI (`/` stays as-is in path)
- USGS data DOIs (e.g., `10.5066/...`) may not be in Crossref — they use DataCite.
  If a `10.5066` DOI returns 404, suggest querying `https://api.datacite.org/dois/{doi}` instead.
- Abstract contains XML: strip JATS tags before display

---

## Cross-Skill Integration

This skill complements other PNGE data skills:

| Source Skill | How to Use Crossref |
|--------------|---------------------|
| `usgs-produced-waters` | Resolve the dataset DOI (10.5066/P9DSRCZJ) — note: USGS DOIs may be DataCite |
| `usgs-minerals` | Look up publication DOIs from MCS data releases |
| `usgs-pubs` | Resolve DOIs returned by USGS Publications Warehouse |
| `doe-osti` | Resolve DOIs from OSTI technical report records |
| `netl-edx` | Resolve DOIs linked in EDX dataset metadata |

**Workflow for DOI resolution from other skills:**
1. Extract DOI from the source API response
2. Call `works/{doi}` to get full citation metadata
3. If 404 and DOI prefix is `10.5066` or `10.2172`, try DataCite instead
4. Present unified citation with DOI link

---

## PNGE Research Queries

Pre-built searches for common lithium/magnesium research topics:

**Lithium from produced water:**
```bash
curl -s "https://api.crossref.org/works?\
  query=lithium+extraction+produced+water+oilfield+brine\
  &filter=from-pub-date:2020-01-01,has-abstract:true,type:journal-article\
  &rows=20&sort=is-referenced-by-count&order=desc\
  &select=DOI,title,author,published-print,container-title,is-referenced-by-count\
  &mailto=user@example.com"
```

**Direct lithium extraction (DLE) technology:**
```bash
curl -s "https://api.crossref.org/works?\
  query=direct+lithium+extraction+DLE+brine\
  &filter=from-pub-date:2020-01-01,type:journal-article\
  &rows=20&sort=is-referenced-by-count&order=desc\
  &select=DOI,title,author,published-print,container-title,is-referenced-by-count\
  &mailto=user@example.com"
```

**Magnesium recovery from brine:**
```bash
curl -s "https://api.crossref.org/works?\
  query=magnesium+recovery+brine+produced+water\
  &filter=from-pub-date:2018-01-01,type:journal-article\
  &rows=20&sort=is-referenced-by-count&order=desc\
  &select=DOI,title,author,published-print,container-title,is-referenced-by-count\
  &mailto=user@example.com"
```

**Appalachian Basin produced water geochemistry:**
```bash
curl -s "https://api.crossref.org/works?\
  query=Appalachian+Marcellus+produced+water+geochemistry\
  &filter=from-pub-date:2015-01-01,type:journal-article\
  &rows=20&sort=is-referenced-by-count&order=desc\
  &select=DOI,title,author,published-print,container-title,is-referenced-by-count\
  &mailto=user@example.com"
```

---

## Caveats and Limitations

- **Citation counts** (`is-referenced-by-count`) are Crossref-tracked only. They
  undercount compared to Google Scholar or Scopus because they only include
  references deposited by publishers who participate in Crossref Cited-by.
- **Coverage gaps:** Not all publishers deposit abstracts or references. Some
  older works have minimal metadata. Conference papers vary widely in coverage.
- **USGS/DOE data DOIs** (prefixes `10.5066`, `10.2172`) are registered with
  DataCite, not Crossref. A 404 for these prefixes is expected — use DataCite API.
- **Relevance ranking** is opaque. For precise results, use `query.bibliographic`
  with specific author + year + title fragments rather than broad `query`.
- **Rate limits:** Public pool = ~50 req/sec shared. Polite pool (with mailto) =
  significantly faster. Always include `mailto` in production use.
- **Abstract XML:** Raw abstracts contain JATS markup. Always strip tags.

---

## Implementation Notes

- Use `bash_tool` with `curl` + `jq` for API calls
- Always include `mailto` parameter for polite pool access
- Use `select` to minimize payload size when you only need specific fields
- Default to `rows=20` for search results; increase to `rows=100` if user needs more
- For DOI lookups, URL-encode the DOI but keep `/` as-is in the path
- See `references/api_reference.md` for full endpoint documentation
- See `references/python_example.py` for a stdlib-only Python client
