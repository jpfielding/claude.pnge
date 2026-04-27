# Literature Adapters — API Reference

Full parameter tables, response shapes, and parsing rules for the four
adapters that back `pnge-literature`.

---

## 1. OpenAlex Adapter

**Base URL:** `https://api.openalex.org`

### Endpoints

| Endpoint         | Returns                                                   |
|------------------|-----------------------------------------------------------|
| `/works`         | Scholarly works (articles, books, theses, conference)     |
| `/works/{id}`    | Single work — id is an OpenAlex W-id or a DOI URL         |
| `/authors`       | Author profiles with h-index, affiliations                |
| `/sources`       | Journals, conferences, repositories                       |
| `/concepts`      | Controlled vocabulary topic tags                          |
| `/institutions`  | Institutional affiliations                                |

### Search Parameters (/works)

| Parameter         | Example                                          | Notes                                 |
|-------------------|--------------------------------------------------|---------------------------------------|
| `search`          | `search=direct+lithium+extraction`               | Keyword search across title+abstract  |
| `filter`          | `filter=open_access.is_oa:true,publication_year:>2019` | Comma-separated filter list     |
| `sort`            | `sort=cited_by_count:desc`                       | Also `publication_date:desc`, `relevance_score:desc` |
| `per-page`        | `per-page=25`                                    | 1..200                                |
| `page`            | `page=2`                                         | Offset paging (max page * per-page = 10000) |
| `cursor`          | `cursor=*` then `cursor={next_cursor}`           | Deep paging                           |
| `select`          | `select=id,doi,title,authorships,cited_by_count` | Limit returned fields                 |

### Common Filters

```
open_access.is_oa:true
publication_year:>2019
publication_year:2020-2024
type:article
authorships.author.display_name.search:stringfellow
primary_location.source.issn:0043-1354
institutions.ror:https://ror.org/01r9htc13   # WVU
```

### Example Calls

```bash
MAILTO="research@mail.wvu.edu"
UA="pnge-literature/1.0 (mailto:${MAILTO})"

# Keyword + citation sort
curl -s "https://api.openalex.org/works?search=direct+lithium+extraction+produced+water&per-page=10&sort=cited_by_count:desc" \
  -H "User-Agent: ${UA}"

# OA only, recent
curl -s "https://api.openalex.org/works?search=Marcellus+shale+lithium&filter=open_access.is_oa:true,publication_year:>2019&per-page=10&sort=cited_by_count:desc" \
  -H "User-Agent: ${UA}"

# Single work by DOI URL
curl -s "https://api.openalex.org/works/https://doi.org/10.1016/j.watres.2020.116198" \
  -H "User-Agent: ${UA}"
```

### Response Shape

```json
{
  "meta": {"count": 1247, "page": 1, "per_page": 10, "next_cursor": "..."},
  "results": [
    {
      "id": "https://openalex.org/W2741809807",
      "doi": "https://doi.org/10.1016/j.watres.2020.116198",
      "title": "Lithium recovery from produced water: A review",
      "publication_year": 2020,
      "publication_date": "2020-09-15",
      "type": "article",
      "primary_location": {
        "source": {"display_name": "Water Research", "issn_l": "0043-1354"},
        "pdf_url": "https://..."
      },
      "authorships": [
        {"author": {"display_name": "Jane Smith", "id": "A..."},
         "institutions": [{"display_name": "WVU"}]}
      ],
      "cited_by_count": 312,
      "open_access": {"is_oa": true, "oa_url": "https://..."},
      "abstract_inverted_index": {"Lithium": [0], "recovery": [1]},
      "concepts": [{"display_name": "Lithium", "score": 0.95}]
    }
  ]
}
```

### Abstract Reconstruction

OpenAlex abstracts are stored as `{word: [positions]}`. Reconstruct:

```python
def reconstruct(idx):
    pairs = [(p, w) for w, ps in (idx or {}).items() for p in ps]
    pairs.sort()
    return " ".join(w for _, w in pairs)
```

Go equivalent in `golang_client.go`.

### Rate Limits

- Public pool: 10 req/sec, 100k/day
- Polite pool (with mailto): faster, priority routing, 100k/day
- Header to signal polite pool: `User-Agent: client/ver (mailto:you@x.com)`

---

## 2. CrossRef Adapter

**Base URL:** `https://api.crossref.org`

### Endpoints

| Endpoint                  | Returns                                         |
|---------------------------|-------------------------------------------------|
| `/works/{doi}`            | Full metadata for a DOI                         |
| `/works?query=...`        | Full-text search                                |
| `/works?query.bibliographic=...` | Citation-style search                     |
| `/works?query.title=...`  | Title-only search                               |
| `/works?query.author=...` | Author-only search                              |
| `/journals/{issn}`        | Journal metadata                                |
| `/journals/{issn}/works`  | Works in a journal                              |
| `/funders/{id}/works`     | Works funded by a specific funder               |
| `/types`                  | All work types                                  |

### Query Parameters

| Parameter              | Example                                         | Notes                                    |
|------------------------|-------------------------------------------------|------------------------------------------|
| `query`                | `query=lithium+brine`                           | Full-text across all fields              |
| `query.bibliographic`  | `query.bibliographic=Smith+2023+lithium`        | Best for citation-string matching        |
| `query.title`          | `query.title=direct+lithium+extraction`         | Title-only                               |
| `query.author`         | `query.author=Stringfellow`                     | Author name                              |
| `filter`               | `filter=from-pub-date:2020-01-01,type:journal-article,has-abstract:true` | Comma list |
| `select`               | `select=DOI,title,author,published-print,is-referenced-by-count` | Reduce payload |
| `rows`                 | `rows=20`                                       | 1..1000                                  |
| `offset`               | `offset=20`                                     | Max 10000                                |
| `cursor`               | `cursor=*`                                      | For deep paging                          |
| `sort`                 | `sort=is-referenced-by-count`                   | Also `relevance`, `published`, `indexed` |
| `order`                | `order=desc`                                    |                                          |
| `mailto`               | `mailto=you@example.com`                        | Polite pool                              |

### Filter Grammar

| Filter              | Example                                 |
|---------------------|-----------------------------------------|
| `from-pub-date`     | `from-pub-date:2023-01-01`              |
| `until-pub-date`    | `until-pub-date:2024-12-31`             |
| `type`              | `type:journal-article`                  |
| `has-abstract`      | `has-abstract:true`                     |
| `has-orcid`         | `has-orcid:true`                        |
| `has-references`    | `has-references:true`                   |
| `has-full-text`     | `has-full-text:true`                    |
| `is-update`         | `is-update:false` (exclude corrections) |
| `funder`            | `funder:10.13039/100000015`             |
| `container-title`   | `container-title:Water+Research`        |
| `issn`              | `issn:0043-1397`                        |
| `doi`               | `doi:10.1021/acs.est.2c03513`           |

### Work Types

`journal-article`, `proceedings-article`, `book-chapter`, `dataset`,
`report`, `posted-content` (preprints), `monograph`, `reference-entry`,
`peer-review`.

### Example Calls

```bash
MAILTO="research@mail.wvu.edu"

# Keyword + filter + select
curl -s "https://api.crossref.org/works?query=lithium+produced+water+brine\
&filter=from-pub-date:2020-01-01,has-abstract:true,type:journal-article\
&rows=20\
&select=DOI,title,author,published-print,container-title,is-referenced-by-count,abstract\
&sort=is-referenced-by-count&order=desc\
&mailto=${MAILTO}"

# Single DOI lookup
curl -s "https://api.crossref.org/works/10.1016/j.watres.2020.116198?mailto=${MAILTO}"

# Bibliographic-style (citation matching)
curl -s "https://api.crossref.org/works?query.bibliographic=Stringfellow+2014+lithium+oilfield+brine\
&rows=5&mailto=${MAILTO}"
```

### Response Shape (search)

```json
{
  "status": "ok",
  "message-type": "work-list",
  "message": {
    "total-results": 2171593,
    "items-per-page": 20,
    "next-cursor": "AoJ/...",
    "items": [
      {
        "DOI": "10.1016/j.watres.2020.116198",
        "title": ["Lithium recovery from produced water: A review"],
        "author": [
          {"given": "Jane", "family": "Smith", "ORCID": "http://orcid.org/..."},
          {"given": "John", "family": "Doe"}
        ],
        "container-title": ["Water Research"],
        "type": "journal-article",
        "published-print": {"date-parts": [[2020, 9, 15]]},
        "is-referenced-by-count": 312,
        "abstract": "<jats:p>Lithium brines are ...</jats:p>",
        "link": [{"URL": "...", "content-type": "text/xml"}],
        "funder": [{"name": "US DOE", "DOI": "10.13039/100000015", "award": ["..."]}]
      }
    ]
  }
}
```

### Date Parts

`date-parts: [[y, m, d]]` may have 1-3 elements:
- `[[2024, 3, 15]]` = March 15, 2024
- `[[2024, 3]]` = March 2024
- `[[2024]]` = 2024

Use the most-specific available. Prefer `published-print`, fall back to
`published-online`, then `issued`.

### Abstract Cleaning

CrossRef abstracts contain JATS XML:
```bash
echo "$ABS" | sed 's/<[^>]*>//g'
```

### 404 on `10.5066` or `10.25338` DOIs

These are DataCite-registered. CrossRef returns 404. Route to
`pnge-core:datacite-doi` instead.

---

## 3. USGS Publications Warehouse Adapter

**Base URL:** `https://pubs.usgs.gov/pubs-services/publication` (use `-L`)

Legacy hostname `pubs.er.usgs.gov` still works but redirects (301).

### Endpoints

| Endpoint                  | Returns                                        |
|---------------------------|------------------------------------------------|
| `/publication`            | Search                                         |
| `/publication/{indexId}`  | Single publication (e.g. `fs20243052`)         |
| `/publication/{numericId}` | Single publication by numeric id (e.g. `70261664`) |

### Search Parameters

| Parameter            | Example                                     | Notes                                  |
|----------------------|---------------------------------------------|----------------------------------------|
| `q`                  | `q=lithium+produced+water`                  | Full-text keyword                      |
| `title`              | `title=critical+minerals`                   | Title-only                             |
| `year`               | `year=2024`                                 | Filter by publication year             |
| `typeName`           | `typeName=Report`                           | `Report` or `Article`                  |
| `subtypeName`        | `subtypeName=USGS+Numbered+Series`          | `USGS Numbered Series` or `Journal Article` |
| `contributingOffice` | `contributingOffice=Eastern+Energy+Resources+Science+Center` | Office filter |
| `pub_x_days`         | `pub_x_days=30`                             | Published in last N days               |
| `page_size`          | `page_size=25`                              | 1..100                                 |
| `page_number`        | `page_number=2`                             | 1-indexed                              |

Parameters combine with AND.

### USGS Series Codes

| Code | Full Name                        | Use                                   |
|------|----------------------------------|---------------------------------------|
| FS   | Fact Sheet                       | 2-6 page public summaries             |
| SIR  | Scientific Investigations Report | Detailed scientific studies            |
| OFR  | Open-File Report                 | Preliminary data and methods           |
| PP   | Professional Paper               | Major research monographs             |
| DS   | Data Series                      | Data compilations with documentation  |
| CIR  | Circular                         | General-audience science summaries    |
| TM   | Techniques and Methods           | Methodological guides                 |

### Example Calls

```bash
# Search
curl -sL "https://pubs.usgs.gov/pubs-services/publication?q=lithium+produced+water&typeName=Report&page_size=10"

# Single publication
curl -sL "https://pubs.usgs.gov/pubs-services/publication/fs20243052"

# Last 30 days of USGS Numbered Series
curl -sL "https://pubs.usgs.gov/pubs-services/publication?pub_x_days=30&subtypeName=USGS+Numbered+Series&page_size=25"
```

### Response Shape

```json
{
  "pageNumber": "1",
  "pageRowStart": "0",
  "pageSize": "25",
  "recordCount": 50,
  "records": [
    {
      "id": 70261664,
      "indexId": "fs20243052",
      "title": "Lithium resource in the Smackover Formation brines...",
      "publicationType": {"id": 18, "text": "Report"},
      "publicationSubtype": {"id": 5, "text": "USGS Numbered Series"},
      "seriesTitle": {"id": 313, "text": "Fact Sheet", "code": "FS"},
      "seriesNumber": "2024-3052",
      "publicationYear": "2024",
      "doi": "10.3133/fs20243052",
      "docAbstract": "<p>Lithium-rich brine deposits occur...</p>",
      "contributors": {
        "authors": [
          {"family": "Knierim", "given": "Katherine", "usgs": true}
        ]
      },
      "links": [
        {"type": {"text": "Document"}, "url": "https://pubs.usgs.gov/.../fs20243052.pdf"},
        {"type": {"text": "Index Page"}, "url": "..."}
      ],
      "country": "United States",
      "state": "Arkansas",
      "usgsCitation": "Knierim, K., ..., 2024, Lithium resource..."
    }
  ]
}
```

### Field Extraction

- **Title**: `title` (HTML-stripped)
- **Authors**: `contributors.authors[].family + given` (or `.corporations[]`)
- **Year**: `publicationYear`
- **Series ref**: `seriesTitle.text + " " + seriesNumber` (e.g. `Fact Sheet 2024-3052`)
- **DOI**: `doi` (always `10.3133/*` for USGS series)
- **PDF**: `links[]` where `type.text == "Document"`
- **Abstract**: `docAbstract` (strip `<[^>]*>`)

### Pagination

```python
page = 1
all_records = []
while True:
    r = fetch(page_number=page, page_size=25)
    all_records.extend(r["records"])
    if len(all_records) >= r["recordCount"]:
        break
    page += 1
```

---

## 4. DOE OSTI Adapter

**Base URL:** `https://www.osti.gov/api/v1/records`

### Endpoints

| Endpoint                  | Returns                                     |
|---------------------------|---------------------------------------------|
| `/records`                | Search                                      |
| `/records/{osti_id}`      | Single record                               |

### Parameters

| Parameter      | Example                             | Notes                                  |
|----------------|-------------------------------------|----------------------------------------|
| `q`            | `q=lithium+produced+water`          | Full-text                              |
| `title`        | `title=lithium+extraction`          | Title-only                             |
| `author`       | `author=Stuckman`                   | Author last name                       |
| `sponsor_org`  | `sponsor_org=NETL`                  | DOE sponsoring organization            |
| `research_org` | `research_org=National+Energy+Technology+Laboratory` | Performing org      |
| `product_type` | `product_type=Technical+Report`     | See product types below                |
| `rows`         | `rows=20`                           | 1..100                                 |
| `page`         | `page=2`                            | 1-indexed                              |

### Product Types

`Technical Report`, `Journal Article`, `Conference`, `Thesis/Dissertation`,
`Book`, `Patent`, `Program Document`, `Miscellaneous`

### Known Bug

Date filter parameters (`publication_date_start`, `publication_date_end`,
`entry_date_start`, `entry_date_end`) return HTTP 500 as of April 2026.
**Workaround:** embed year terms in the `q` parameter.

### Example Calls

```bash
# Keyword
curl -s "https://www.osti.gov/api/v1/records?q=lithium+produced+water&rows=10" \
  -H "Accept: application/json"

# NETL + Technical Report
curl -s "https://www.osti.gov/api/v1/records?q=critical+minerals&sponsor_org=NETL&product_type=Technical+Report&rows=10" \
  -H "Accept: application/json"

# Single record
curl -s "https://www.osti.gov/api/v1/records/2588655" \
  -H "Accept: application/json"

# Total count (header)
curl -si "https://www.osti.gov/api/v1/records?q=lithium&rows=1" \
  -H "Accept: application/json" | grep -i "X-Total-Count"
```

### Response Shape

Flat JSON array — **no wrapper**. Total count lives in the
`X-Total-Count` HTTP response header.

```json
[
  {
    "osti_id": "3027695",
    "title": "Novel Zwitterionic Chromatography to Separate Lithium...",
    "authors": [
      "Choi, Hoon [NREL] (ORCID:0000000227913788)",
      "Li, Daniel [NREL]"
    ],
    "publication_date": "2026-03-31T00:00:00Z",
    "product_type": "Conference",
    "description": "Since lithium is a key element for clean energy...",
    "doi": "10.2172/3027695",
    "sponsor_orgs": ["USDOE Office of Energy Efficiency..."],
    "research_orgs": ["National Renewable Energy Laboratory..."],
    "subjects": ["09 BIOMASS FUELS", "lithium extraction"],
    "links": [
      {"rel": "citation", "href": "https://www.osti.gov/biblio/3027695"},
      {"rel": "fulltext", "href": "https://www.osti.gov/servlets/purl/3027695"}
    ],
    "language": "English",
    "report_number": "NLR/PR-2800-97665"
  }
]
```

### Author Parsing

Author strings vary:
- `"Stuckman, Mengling [NETL] (ORCID:...)"`
- `"Gerardo, Sheila [UT Austin]"`
- `"McCandless, Kevin"` (no affiliation)

Split on ` [` to extract the name, then format `Last, F.`

### Fulltext URL

Always: `https://www.osti.gov/servlets/purl/{osti_id}` — check
`links[].rel == "fulltext"` for the canonical link.

### Rate Limits

Response headers include:
- `X-Rate-Limit-Remaining` — remaining calls in the window
- `X-Total-Count` — total matching records

If `X-Rate-Limit-Remaining` is 0, wait 60s before retrying.

---

## Unified Normalization Contract

Every adapter output maps to this canonical struct:

```go
type Record struct {
    DOI         string   `json:"doi,omitempty"`
    Title       string   `json:"title"`
    Authors     []string `json:"authors"`
    Year        int      `json:"year,omitempty"`
    Venue       string   `json:"venue,omitempty"`
    Type        string   `json:"type,omitempty"`
    Abstract    string   `json:"abstract,omitempty"`
    Citations   int      `json:"citations,omitempty"`
    OpenAccess  *bool    `json:"open_access,omitempty"`
    PdfURL      string   `json:"pdf_url,omitempty"`
    Source      string   `json:"source"`
    SourceID    string   `json:"source_id"`
    Provenance  []string `json:"provenance,omitempty"`
}
```

| Field       | openalex                                   | crossref                              | usgs-pw                                 | doe-osti                                |
|-------------|--------------------------------------------|---------------------------------------|-----------------------------------------|-----------------------------------------|
| DOI         | `doi` (strip URL)                          | `DOI`                                 | `doi`                                   | `doi`                                   |
| Title       | `display_name`                             | `title[0]` (strip JATS)               | `title` (strip HTML)                    | `title` (strip HTML)                    |
| Authors     | `authorships[].author.display_name`        | `author[].given + family`             | `contributors.authors[].given + family` | split `authors[]` on ` [`               |
| Year        | `publication_year`                         | `published-print.date-parts[0][0]`    | `publicationYear`                       | `publication_date[:4]`                  |
| Venue       | `primary_location.source.display_name`     | `container-title[0]`                  | `seriesTitle.text + " " + seriesNumber` | `research_orgs[0]` or `sponsor_orgs[0]` |
| Type        | `type`                                     | `type`                                | `publicationType.text`                  | `product_type`                          |
| Abstract    | reconstruct `abstract_inverted_index`      | `abstract` (strip JATS)               | `docAbstract` (strip HTML)              | `description` (strip HTML)              |
| Citations   | `cited_by_count`                           | `is-referenced-by-count`              | nil                                     | nil                                     |
| OpenAccess  | `open_access.is_oa`                        | `license[]` present?                  | true (USGS series always free)          | fulltext link present?                  |
| PdfURL      | `open_access.oa_url` or `primary_location.pdf_url` | `link[0].URL`                   | `links[] where type.text==Document`     | `links[] where rel==fulltext`           |
| SourceID    | W-id from `id`                             | `DOI`                                 | `indexId`                               | `osti_id`                               |
