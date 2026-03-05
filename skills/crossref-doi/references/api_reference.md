# Crossref REST API Reference

Base URL: `https://api.crossref.org/`

API documentation: https://api.crossref.org/swagger-ui/index.html

## Polite Pool

Add `mailto=your@email.com` as a query parameter to all requests. This routes
you to the polite pool with faster rate limits and priority routing. The email
is not used for authentication -- it is a contact address in case Crossref
needs to reach you about your usage.

Public pool: ~50 requests/second (shared across all anonymous users).
Polite pool: significantly higher limits, dedicated routing.

---

## Endpoints

### GET /works/{doi}

Retrieve metadata for a single DOI.

```bash
curl -s "https://api.crossref.org/works/10.1016/j.hydromet.2023.106070?mailto=user@example.com"
```

Response: `{"status":"ok", "message-type":"work", "message": {...work object...}}`

The DOI in the path should NOT be URL-encoded (slashes are literal path components).
Special characters in the DOI suffix (parentheses, angle brackets, semicolons)
should be percent-encoded.

### GET /works

Search across all works.

```bash
# Basic keyword search
curl -s "https://api.crossref.org/works?query=lithium+extraction+brine&rows=10&mailto=user@example.com"

# Filtered search — journal articles from 2022+ with abstracts
curl -s "https://api.crossref.org/works?\
  query=lithium+produced+water\
  &filter=from-pub-date:2022-01-01,has-abstract:true,type:journal-article\
  &rows=20\
  &mailto=user@example.com"

# Select specific fields to reduce response size
curl -s "https://api.crossref.org/works?\
  query=magnesium+recovery+brine\
  &select=DOI,title,author,type,published-print,container-title,is-referenced-by-count\
  &rows=20\
  &mailto=user@example.com"

# Sort by citation count (most cited first)
curl -s "https://api.crossref.org/works?\
  query=direct+lithium+extraction\
  &sort=is-referenced-by-count&order=desc\
  &rows=10\
  &mailto=user@example.com"

# Bibliographic search (best for matching a citation string)
curl -s "https://api.crossref.org/works?\
  query.bibliographic=Munk+2016+lithium+brine+Smackover\
  &rows=5\
  &mailto=user@example.com"
```

Response: `{"status":"ok", "message-type":"work-list", "message": {"total-results": N, "items": [...], ...}}`

### GET /journals/{issn}

Journal metadata by ISSN.

```bash
curl -s "https://api.crossref.org/journals/0043-1397?mailto=user@example.com"
```

### GET /journals/{issn}/works

Works published in a specific journal.

```bash
# Recent Water Resources Research articles on lithium
curl -s "https://api.crossref.org/journals/0043-1397/works?\
  query=lithium&rows=10&mailto=user@example.com"
```

### GET /funders/{id}/works

Works funded by a specific funder. Useful for finding DOE-funded research.

```bash
# DOE funder DOI: 10.13039/100000015
curl -s "https://api.crossref.org/funders/10.13039/100000015/works?\
  query=lithium+brine&rows=10&mailto=user@example.com"

# NSF funder DOI: 10.13039/100000001
curl -s "https://api.crossref.org/funders/10.13039/100000001/works?\
  query=critical+minerals+brine&rows=10&mailto=user@example.com"
```

### GET /types

List all registered work types.

```bash
curl -s "https://api.crossref.org/types?mailto=user@example.com"
```

---

## Query Parameters (Full Reference)

### Search Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `query` | string | Full-text search across all metadata fields |
| `query.bibliographic` | string | Bibliographic-style search (title + author + year combo) |
| `query.title` | string | Search within title field only |
| `query.author` | string | Search within author names only |
| `query.container-title` | string | Search within journal/proceedings names |
| `query.affiliation` | string | Search within author affiliations |

### Pagination Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `rows` | integer | 20 | Results per page (max 1000) |
| `offset` | integer | 0 | Offset for pagination (max 10000) |
| `cursor` | string | - | Deep paging cursor; use `*` for first request |

### Sort Parameters

| Parameter | Values | Description |
|-----------|--------|-------------|
| `sort` | `relevance`, `published`, `indexed`, `is-referenced-by-count`, `references-count`, `score` | Sort field |
| `order` | `asc`, `desc` | Sort direction (default depends on sort field) |

### Field Selection

| Parameter | Type | Description |
|-----------|------|-------------|
| `select` | comma-separated | Return only listed fields. Reduces payload significantly. |

Selectable fields: `DOI`, `title`, `author`, `type`, `published-print`,
`published-online`, `container-title`, `is-referenced-by-count`, `abstract`,
`subject`, `funder`, `link`, `reference`, `publisher`, `ISSN`, `ISBN`,
`volume`, `issue`, `page`, `language`, `license`, `URL`, `score`

### Filter Parameters

Filters are comma-separated in a single `filter` parameter:
`filter=from-pub-date:2023-01-01,type:journal-article,has-abstract:true`

| Filter | Format | Description |
|--------|--------|-------------|
| `from-pub-date` | YYYY-MM-DD | Published on or after |
| `until-pub-date` | YYYY-MM-DD | Published on or before |
| `from-index-date` | YYYY-MM-DD | Indexed on or after |
| `until-index-date` | YYYY-MM-DD | Indexed on or before |
| `type` | string | Work type (journal-article, proceedings-article, etc.) |
| `has-abstract` | true/false | Only works with abstracts |
| `has-references` | true/false | Only works with deposited references |
| `has-full-text` | true/false | Only works with full-text links |
| `has-orcid` | true/false | Authors with ORCID IDs |
| `has-funder` | true/false | Works with funder information |
| `has-license` | true/false | Works with license metadata |
| `funder` | DOI | Funder DOI (e.g., 10.13039/100000015 for DOE) |
| `doi` | DOI | Exact DOI match |
| `issn` | ISSN | Filter by journal ISSN |
| `isbn` | ISBN | Filter by book ISBN |
| `container-title` | string | Filter by journal/proceedings title |
| `publisher-name` | string | Filter by publisher name |
| `member` | integer | Filter by Crossref member ID |
| `prefix` | DOI prefix | Filter by DOI prefix (e.g., 10.1021 for ACS) |
| `is-update` | true/false | Include/exclude corrections and errata |
| `type-name` | string | Full type name (alternative to `type`) |

---

## Work Object Fields

A work object returned by the API contains these fields:

### Identification
- `DOI` (string) — The DOI
- `URL` (string) — Canonical URL (usually `https://doi.org/{DOI}`)
- `title` (array of strings) — Work title(s)
- `subtitle` (array of strings) — Subtitle(s)
- `short-title` (array of strings) — Abbreviated title(s)

### Classification
- `type` (string) — Work type
- `subtype` (string) — Work subtype
- `subject` (array of strings) — Subject categories
- `group-title` (string) — Group/section title

### Authorship
- `author` (array) — Each element:
  - `given` (string) — First name
  - `family` (string) — Last name
  - `name` (string) — For organizational authors
  - `ORCID` (string) — ORCID URL if available
  - `affiliation` (array) — Each: `{name: "Institution Name"}`
  - `sequence` (string) — `first` or `additional`

### Publication
- `publisher` (string) — Publisher name
- `container-title` (array of strings) — Journal/proceedings name
- `short-container-title` (array of strings) — Abbreviated journal name
- `volume` (string) — Volume number
- `issue` (string) — Issue number
- `page` (string) — Page range (e.g., "1234-1245")
- `article-number` (string) — Article/paper number

### Dates
- `published-print` — Print publication: `{date-parts: [[year, month, day]]}`
- `published-online` — Online publication: same format
- `created` — Record creation: `{date-parts: [...], date-time: "...", timestamp: N}`
- `deposited` — Last deposit: same format as created
- `indexed` — Last indexed: same format as created

### Metrics
- `is-referenced-by-count` (integer) — Times cited (Crossref-tracked)
- `references-count` (integer) — Number of references in bibliography
- `score` (float) — Crossref relevance score (search results only)

### Content
- `abstract` (string) — Abstract text (may contain JATS XML markup)
- `reference` (array) — Bibliography entries
- `link` (array) — Full-text links: `{URL, content-type, intended-application}`
- `license` (array) — License information

### Funding
- `funder` (array) — Each:
  - `name` (string) — Funder name
  - `DOI` (string) — Funder DOI
  - `award` (array of strings) — Grant/award numbers

---

## Pagination Strategies

### Offset-based (simple, limited to 10000)

```
Page 1: &offset=0&rows=100
Page 2: &offset=100&rows=100
...
Max:    &offset=10000&rows=100
```

### Cursor-based (for large result sets)

```bash
# First request — use cursor=*
RESP=$(curl -s "https://api.crossref.org/works?query=lithium&cursor=*&rows=100&mailto=user@example.com")

# Extract next cursor
NEXT=$(echo "$RESP" | jq -r '.message["next-cursor"]')

# Subsequent requests
curl -s "https://api.crossref.org/works?query=lithium&cursor=${NEXT}&rows=100&mailto=user@example.com"
```

Continue until `items` array is empty. The `next-cursor` field is present in
every response when using cursor pagination.

---

## Common DOI Prefixes for PNGE Research

| Prefix | Publisher/Registrar |
|--------|---------------------|
| `10.1021` | American Chemical Society (ACS) |
| `10.1016` | Elsevier |
| `10.1039` | Royal Society of Chemistry |
| `10.1007` | Springer Nature |
| `10.1029` | AGU (Wiley) — Water Resources Research, GRL, JGR |
| `10.2118` | Society of Petroleum Engineers (SPE) |
| `10.15530` | European Association of Geoscientists and Engineers |
| `10.3390` | MDPI (Minerals, Water, Energies) |
| `10.1002` | Wiley |
| `10.1038` | Nature Publishing |
| `10.5066` | USGS ScienceBase (DataCite, NOT Crossref) |
| `10.2172` | DOE OSTI (DataCite, NOT Crossref) |
| `10.13039` | Funder DOIs (for funder filter) |

---

## Rate Limits and Etiquette

- Always include `mailto` for polite pool access
- Cache DOI lookups — metadata changes infrequently
- Use `select` to reduce response size
- Prefer `rows=100` over `rows=1000` unless you need large batches
- For bulk operations, use cursor pagination with modest batch sizes
- Respect 429 responses — back off exponentially
- The `X-Rate-Limit-Limit` and `X-Rate-Limit-Interval` response headers
  indicate your current rate limit allocation

---

## Key Funder DOIs for Energy Research

| Funder | DOI |
|--------|-----|
| U.S. Department of Energy (DOE) | 10.13039/100000015 |
| National Science Foundation (NSF) | 10.13039/100000001 |
| DOE Office of Science | 10.13039/100000015 (same) |
| ARPA-E | 10.13039/100006133 |
| National Energy Technology Laboratory | 10.13039/100013165 |
| USGS | 10.13039/100000203 |
| EPA | 10.13039/100000139 |
