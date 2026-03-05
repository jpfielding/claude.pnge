---
name: doe-osti
description: >
  Search DOE Office of Scientific and Technical Information (OSTI) for
  technical reports, journal articles, conference papers, and theses from
  DOE-funded energy research at national labs and universities. Use this
  skill whenever the user asks for DOE technical reports, NETL publications,
  national lab research, OSTI records, or energy research literature. Trigger
  for phrases like "find DOE reports on lithium extraction", "NETL technical
  reports about produced water", "DOE research on critical minerals",
  "search OSTI for direct lithium extraction", "national lab publications
  on brine chemistry", "DOE-funded studies on magnesium recovery",
  "OSTI records about Appalachian basin geochemistry", or any request for
  federally funded energy research publications. Produces publication tables
  with citation links and narrative summaries.
---

# DOE OSTI Technical Reports

Searches the DOE Office of Scientific and Technical Information (OSTI) for
publications from all DOE-funded research, including NETL, national
laboratories, and university contractors. Covers technical reports, journal
articles, conference papers, theses, and patents.

## Credential

None required. The OSTI public search API is open access with no
authentication.

---

## API Structure

**Base URL:** `https://www.osti.gov/api/v1/records`

**Search endpoint:**
```
GET https://www.osti.gov/api/v1/records?{params}
```

**Single record:**
```
GET https://www.osti.gov/api/v1/records/{osti_id}
```

**Key parameters:**

| Parameter      | Example                            | Notes                                    |
|----------------|------------------------------------|------------------------------------------|
| `q`            | `q=lithium+produced+water`         | Full-text keyword search                 |
| `title`        | `title=lithium+extraction`         | Title-only search                        |
| `author`       | `author=Stuckman`                  | Author last name search                  |
| `sponsor_org`  | `sponsor_org=NETL`                 | DOE sponsoring organization              |
| `research_org` | `research_org=National+Energy`     | Performing research organization         |
| `product_type` | `product_type=Technical+Report`    | Publication type filter                  |
| `rows`         | `rows=20`                          | Results per page (default 20)            |
| `page`         | `page=2`                           | Page number (1-indexed)                  |

**Product types:** `Technical Report`, `Journal Article`, `Conference`,
`Thesis/Dissertation`, `Book`, `Patent`, `Program Document`, `Miscellaneous`

**Note:** Date filter parameters (`publication_date_start`, `entry_date_start`,
etc.) are documented but return HTTP 500 errors as of March 2026. Include
year terms in the `q` parameter as a workaround (e.g., `q=lithium+2024`).

---

## Working Examples

### Keyword search
```bash
curl -s "https://www.osti.gov/api/v1/records?q=lithium+produced+water&rows=5" \
  -H "Accept: application/json" | jq '.[0:2] | .[] | {osti_id, title, product_type, publication_date}'
```

### NETL-sponsored technical reports
```bash
curl -s "https://www.osti.gov/api/v1/records?q=critical+minerals&sponsor_org=NETL&product_type=Technical+Report&rows=10" \
  -H "Accept: application/json" | jq '.[] | {osti_id, title, authors: (.authors[:2]), publication_date}'
```

### Author search
```bash
curl -s "https://www.osti.gov/api/v1/records?author=Stuckman&rows=10" \
  -H "Accept: application/json" | jq '.[] | {osti_id, title, product_type}'
```

### Single record by OSTI ID
```bash
curl -s "https://www.osti.gov/api/v1/records/2588655" \
  -H "Accept: application/json" | jq '.[0] | {osti_id, title, authors, doi, links}'
```

### Get total result count (from headers)
```bash
curl -si "https://www.osti.gov/api/v1/records?q=lithium+brine&rows=1" \
  -H "Accept: application/json" 2>&1 | grep "X-Total-Count"
```

### Combine multiple filters
```bash
curl -s "https://www.osti.gov/api/v1/records?q=produced+water+geochemistry&sponsor_org=NETL&product_type=Technical+Report&rows=10" \
  -H "Accept: application/json"
```

---

## Workflow

### Step 1 -- Resolve Intent

Map the user's question to search parameters:

- **General topic search** -- use `q` with keywords
- **Specific title** -- use `title` parameter
- **Author lookup** -- use `author` parameter
- **Lab/program filter** -- combine `q` with `sponsor_org` or `research_org`
- **Publication type** -- add `product_type` filter
- **Specific record** -- use the `/{osti_id}` path

**Common search mappings for PNGE research:**

| User Intent                            | Parameters                                                      |
|----------------------------------------|-----------------------------------------------------------------|
| Lithium in produced water              | `q=lithium+produced+water`                                      |
| NETL reports on critical minerals      | `q=critical+minerals&sponsor_org=NETL&product_type=Technical+Report` |
| Direct lithium extraction from brines  | `q=direct+lithium+extraction+brine`                             |
| Magnesium recovery from oilfield water | `q=magnesium+recovery+oilfield+brine`                           |
| Marcellus Shale geochemistry           | `q=Marcellus+Shale+geochemistry+produced+water`                 |
| Appalachian basin brine chemistry      | `q=Appalachian+basin+brine+chemistry`                           |
| DLE technology reviews                 | `q=direct+lithium+extraction+technology+review`                 |

### Step 2 -- Fetch Data

Execute the search. Always include `-H "Accept: application/json"`.

```bash
curl -s "https://www.osti.gov/api/v1/records?q=lithium+produced+water&rows=20" \
  -H "Accept: application/json"
```

Read the `X-Total-Count` response header for total results. If using `curl -s`
(silent), the header is not visible; use `curl -si` to inspect headers when
total count matters.

### Step 3 -- Parse Response

The response is a flat JSON array of record objects (no wrapper envelope).
Each record contains:

- `osti_id` -- unique identifier
- `title` -- may contain HTML tags (strip with `sed` or `jq`)
- `authors` -- array of strings with affiliations and ORCIDs
- `publication_date` -- ISO 8601 timestamp
- `product_type` -- Technical Report, Journal Article, Conference, etc.
- `description` -- abstract (may contain HTML)
- `doi` -- Digital Object Identifier (when available)
- `sponsor_orgs` -- DOE sponsoring organizations
- `research_orgs` -- performing research organizations
- `links` -- array with `citation` and `fulltext` URLs
- `subjects` -- keywords and subject categories

**Parsing author names (strip affiliations):**
```bash
jq '.[] | .authors | .[] | split(" [")[0]'
```

**Extracting fulltext download links:**
```bash
jq '.[] | .links[] | select(.rel=="fulltext") | .href'
```

### Step 4 -- Paginate (if needed)

For large result sets, use the `page` parameter:

```bash
# Page 1 (default)
curl -s "https://www.osti.gov/api/v1/records?q=lithium&rows=20&page=1" \
  -H "Accept: application/json"

# Page 2
curl -s "https://www.osti.gov/api/v1/records?q=lithium&rows=20&page=2" \
  -H "Accept: application/json"
```

The `Link` response header also provides `next` and `last` page URLs.

Warn the user if `X-Total-Count` exceeds 500 and suggest narrower filters.

### Step 5 -- Produce Output

**Format: Publication Table + Narrative**

Present a markdown table of the most relevant records (cap at 15 rows),
then a narrative summary.

---

## Output Format

**Example output structure:**

```
## DOE Research: Lithium Recovery from Produced Water

| # | Title | Authors | Year | Type | OSTI ID | DOI |
|---|-------|---------|------|------|---------|-----|
| 1 | Separation of Li and Mg from Brines... | Choi, H. | 2026 | Technical Report | 3016248 | 10.2172/3016248 |
| 2 | Lithium recovery from U.S. oil and gas... | Gerardo, S.; Song, W. | 2025 | Journal Article | 2500981 | 10.1039/D4EW00422A |
| 3 | Producing Dollars from Produced Water... | Stuckman, M. | 2025 | Conference | 2588655 | 10.2172/2588655 |

**Summary:** Found 35 DOE-funded publications on lithium recovery from produced
water. The most recent work (2025-2026) spans NETL conference presentations,
CRADA technical reports on Li/Mg separation using zwitterionic chromatography,
and peer-reviewed studies assessing U.S. produced water resource quality for
lithium extraction. Key sponsoring programs include FECM (Office of Fossil
Energy and Carbon Management) and EERE (Energy Efficiency and Renewable Energy).

**Access:** Click any OSTI ID link to view the full bibliographic record.
Technical reports often have free full-text PDFs available at:
`https://www.osti.gov/servlets/purl/{osti_id}`

**Suggested narrowing:** Add `sponsor_org=NETL` to focus on NETL-funded
work, or `product_type=Technical+Report` to exclude journal articles.
```

**Key formatting rules:**
1. Shorten titles to ~60 characters with ellipsis if needed
2. Show only first author's last name + initial; add "et al." for 3+ authors
3. Extract year from `publication_date` (first 4 characters)
4. Always include OSTI ID and DOI for citation
5. Provide the fulltext download URL pattern in the summary
6. Suggest narrower filters when result count is large

---

## Pagination

The API paginates via `rows` and `page` parameters. Total count is in the
`X-Total-Count` response header.

```python
import json
import urllib.request
import urllib.parse

def fetch_all(query: str, max_pages: int = 10) -> list[dict]:
    """Fetch all pages of results up to max_pages."""
    all_records = []
    page = 1
    while page <= max_pages:
        url = f"https://www.osti.gov/api/v1/records?{urllib.parse.urlencode({'q': query, 'rows': 20, 'page': page})}"
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req) as resp:
            total = int(resp.headers.get("X-Total-Count", "0"))
            records = json.loads(resp.read().decode("utf-8"))
        all_records.extend(records)
        if len(all_records) >= total or not records:
            break
        page += 1
    return all_records
```

---

## Error Handling

| HTTP Code | Meaning               | Action                                               |
|-----------|-----------------------|------------------------------------------------------|
| 200       | Success               | Parse JSON array from response body                  |
| 200 + `[]`| No results            | Report "no records found"; suggest broader keywords   |
| 400       | Bad request           | Check parameter names and values; retry               |
| 404       | OSTI ID not found     | Verify ID; suggest searching by keyword instead       |
| 500       | Internal server error | Likely caused by date filters; remove date params and retry using keyword year terms |
| 503       | Service unavailable   | Wait 30 seconds and retry; OSTI may be under maintenance |

**Rate limiting:** The `X-Rate-Limit-Remaining` header tracks remaining
requests. If exhausted, wait 60 seconds before retrying.

---

## Caveats and Data Limitations

1. **Coverage scope.** OSTI indexes DOE-funded research only. Non-DOE federal
   research (NSF, USDA, DoD) is not included. For broader literature searches,
   combine with USGS Pubs and general academic databases.

2. **Date filters broken.** As of March 2026, the `publication_date_start`,
   `publication_date_end`, `entry_date_start`, and `entry_date_end` parameters
   return HTTP 500 errors. Use year terms in keyword queries as a workaround.

3. **HTML in fields.** The `title` and `description` fields may contain HTML
   tags (`<em>`, `<p>`, `<title>`, etc.). Strip HTML before displaying.

4. **Author format inconsistency.** Author strings vary in format:
   - `"Stuckman, Mengling [NETL] (ORCID:...)"`
   - `"Gerardo, Sheila [UT Austin]"`
   - `"McCandless, Kevin"` (no affiliation)
   Parse by splitting on ` [` to extract the name portion.

5. **Fulltext availability.** Not all records have downloadable full text.
   Check the `links` array for a `rel=fulltext` entry. Some journal articles
   link to publisher paywalls via DOI rather than free DOE copies.

6. **Relevance ranking.** Results are ranked by relevance to the query terms,
   not by date. The most relevant result may not be the most recent. Sort
   is not controllable via API parameters for the v1 endpoint.

7. **Embargo periods.** Some technical reports have a 12-month embargo before
   public release. Records may appear in search results before the full text
   is accessible.

8. **Search scope of `q` parameter.** The `q` parameter searches across all
   indexed fields (title, abstract, authors, subjects, etc.), which can
   return broad results. Use `title` for more precise matches.

---

## Reference Files

- `references/api_reference.md` -- Full API parameter and response documentation
- `references/python_example.py` -- Python stdlib client with search, pagination,
  and formatted output (no dependencies beyond urllib and json)

---

## Implementation Notes

- **Use `bash_tool` with `curl` + `jq`** for quick API queries
- **Always set** `-H "Accept: application/json"` -- the API defaults to XML
- **Python client** in `references/python_example.py` uses only stdlib
  (`urllib`, `json`) for portability
- **Strip HTML** from `title` and `description` before display
- **Response is a flat array** -- no wrapper object or metadata envelope
- **Pagination metadata** is in HTTP headers, not the response body
- OSTI updates continuously as new DOE reports are submitted
- For PNGE research, combine `q=lithium+produced+water` with
  `sponsor_org=NETL` to focus on the most relevant DOE program
