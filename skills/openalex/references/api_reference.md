# OpenAlex API — Reference

Base URL: `https://api.openalex.org`

No API key required. For polite pool (faster responses, higher rate limits),
include a `mailto:` address in the User-Agent header.

```bash
-H "User-Agent: OpenAlexClient/1.0 (mailto:research@mail.wvu.edu)"
```

---

## Entities Overview

OpenAlex organizes scholarly data into five entity types:

| Entity | Endpoint | Description |
|--------|----------|-------------|
| Works | `/works` | Publications: articles, books, theses, preprints |
| Authors | `/authors` | Researcher profiles with publication metrics |
| Sources | `/sources` | Journals, repositories, conference series |
| Institutions | `/institutions` | Universities, labs, companies |
| Concepts | `/concepts` | Controlled vocabulary topic tags |

---

## /works

The primary endpoint for finding and analyzing publications.

### Query Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `search` | Full-text keyword search across title, abstract, concepts | `search=direct+lithium+extraction` |
| `filter` | Structured field filters (see Filter Syntax below) | `filter=publication_year:>2020` |
| `sort` | Sort field and direction | `sort=cited_by_count:desc` |
| `per-page` | Results per page (max 200) | `per-page=25` |
| `page` | Page number (use with per-page) | `page=2` |
| `cursor` | Cursor for deep pagination | `cursor=*` |
| `select` | Comma-separated fields to return | `select=id,doi,title,cited_by_count` |
| `group-by` | Group results for aggregation | `group-by=publication_year` |

### Filter Syntax

Filters use the format `field:value` and can be combined with commas (AND logic):

```
filter=field1:value1,field2:value2
```

**Common filters for /works:**

| Filter | Description | Example |
|--------|-------------|---------|
| `title.search` | Title contains keyword | `title.search:produced+water` |
| `abstract.search` | Abstract contains keyword | `abstract.search:lithium+recovery` |
| `publication_year` | Year (exact, range, inequality) | `publication_year:2023` or `publication_year:>2019` |
| `open_access.is_oa` | Is open access | `open_access.is_oa:true` |
| `type` | Work type | `type:article` |
| `primary_location.source.issn` | Journal by ISSN | `primary_location.source.issn:1385-8947` |
| `primary_location.source.display_name` | Journal by name | `primary_location.source.display_name:Desalination` |
| `authorships.author.id` | Author by OpenAlex ID | `authorships.author.id:A5023888391` |
| `authorships.author.orcid` | Author by ORCID | `authorships.author.orcid:0000-0002-1234-5678` |
| `authorships.institutions.display_name` | Institution name | `authorships.institutions.display_name:West+Virginia+University` |
| `cited_by_count` | Citation count (inequality) | `cited_by_count:>50` |
| `concepts.id` | Concept by OpenAlex ID | — |
| `concepts.display_name` | Concept by name | `concepts.display_name:Lithium` |
| `doi` | DOI filter | `doi:10.1016/j.watres.2020.116198` |
| `is_paratext` | Exclude editorials etc. | `is_paratext:false` |

**OR logic within a single filter field:** Use pipe `|` separator:

```
filter=publication_year:2021|2022|2023
```

### Sort Options

| Sort field | Description |
|------------|-------------|
| `cited_by_count:desc` | Most cited first (default for relevance) |
| `cited_by_count:asc` | Least cited first |
| `publication_date:desc` | Most recent first |
| `publication_date:asc` | Oldest first |
| `relevance_score:desc` | Best text-search match (requires `search=`) |

### Work Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | OpenAlex URL ID (e.g., `https://openalex.org/W2741809807`) |
| `doi` | string | DOI URL (e.g., `https://doi.org/10.1016/...`) |
| `title` | string | Title |
| `display_name` | string | Same as title |
| `publication_year` | int | Year |
| `publication_date` | string | ISO date (YYYY-MM-DD) |
| `type` | string | `article`, `book-chapter`, `dissertation`, etc. |
| `primary_location` | object | Best source location (journal, URL) |
| `authorships` | array | Authors with institutions |
| `cited_by_count` | int | Total citation count |
| `open_access` | object | OA status and URL |
| `abstract_inverted_index` | object | Abstract as inverted index (reconstruct—see below) |
| `concepts` | array | Topic tags with relevance scores |
| `referenced_works` | array | OpenAlex IDs of cited works |
| `related_works` | array | Related work IDs |
| `counts_by_year` | array | Per-year citation counts |
| `updated_date` | string | Last update timestamp |

### primary_location Object

```json
{
  "is_oa": true,
  "landing_page_url": "https://doi.org/10.1016/...",
  "pdf_url": "https://example.com/paper.pdf",
  "source": {
    "id": "https://openalex.org/S137773608",
    "display_name": "Water Research",
    "issn_l": "0043-1354",
    "type": "journal"
  },
  "version": "publishedVersion",
  "license": "cc-by"
}
```

### open_access Object

```json
{
  "is_oa": true,
  "oa_status": "gold",
  "oa_url": "https://example.com/open-paper.pdf",
  "any_repository_has_fulltext": true
}
```

OA status values: `gold`, `green`, `hybrid`, `bronze`, `closed`

### Reconstructing Abstract from Inverted Index

OpenAlex stores abstracts as `{word: [position_list]}` to avoid copyright issues.
Reconstruct by reversing the index:

```python
def reconstruct_abstract(inverted_index: dict) -> str:
    """Reconstruct abstract string from OpenAlex inverted index."""
    if not inverted_index:
        return "(abstract not available)"
    positions = []
    for word, pos_list in inverted_index.items():
        for pos in pos_list:
            positions.append((pos, word))
    positions.sort(key=lambda x: x[0])
    return " ".join(word for _, word in positions)
```

Go version:

```go
func reconstructAbstract(invertedIndex map[string][]int) string {
    if len(invertedIndex) == 0 {
        return "(abstract not available)"
    }
    // Find max position
    maxPos := 0
    for _, positions := range invertedIndex {
        for _, p := range positions {
            if p > maxPos {
                maxPos = p
            }
        }
    }
    words := make([]string, maxPos+1)
    for word, positions := range invertedIndex {
        for _, p := range positions {
            words[p] = word
        }
    }
    result := make([]string, 0, len(words))
    for _, w := range words {
        if w != "" {
            result = append(result, w)
        }
    }
    return strings.Join(result, " ")
}
```

### Examples

```bash
# Keyword search, sorted by citation count, 10 results
curl -s "https://api.openalex.org/works?search=direct+lithium+extraction&per-page=10&sort=cited_by_count:desc" \
  -H "User-Agent: OpenAlexClient/1.0 (mailto:research@mail.wvu.edu)" \
  | jq '.results[] | {title, publication_year, cited_by_count, doi}'

# Open access papers on produced water treatment since 2019
curl -s "https://api.openalex.org/works?search=produced+water+treatment&filter=open_access.is_oa:true,publication_year:>2019&per-page=10&sort=cited_by_count:desc" \
  -H "User-Agent: OpenAlexClient/1.0 (mailto:research@mail.wvu.edu)"

# WVU-affiliated publications on Marcellus
curl -s "https://api.openalex.org/works?search=Marcellus+shale&filter=authorships.institutions.display_name:West+Virginia+University&sort=publication_date:desc&per-page=10" \
  -H "User-Agent: OpenAlexClient/1.0 (mailto:research@mail.wvu.edu)"

# Get a single work by DOI
curl -s "https://api.openalex.org/works/doi:10.1016/j.watres.2020.116198" \
  -H "User-Agent: OpenAlexClient/1.0 (mailto:research@mail.wvu.edu)"

# Title-only search (more precise than full-text)
curl -s "https://api.openalex.org/works?filter=title.search:direct+lithium+extraction+brine&per-page=10&sort=cited_by_count:desc" \
  -H "User-Agent: OpenAlexClient/1.0 (mailto:research@mail.wvu.edu)"

# Papers citing a specific work
curl -s "https://api.openalex.org/works?filter=cites:W2741809807&per-page=10&sort=publication_date:desc" \
  -H "User-Agent: OpenAlexClient/1.0 (mailto:research@mail.wvu.edu)"

# Group results by year to see publication trend
curl -s "https://api.openalex.org/works?search=lithium+brine&group-by=publication_year" \
  -H "User-Agent: OpenAlexClient/1.0 (mailto:research@mail.wvu.edu)" \
  | jq '.group_by[] | {key, count}'
```

---

## /authors

Search author profiles with publication counts, citation metrics, and affiliations.

### Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `search` | Full-text name search | `search=Jane+Smith` |
| `filter` | Structured filters | `filter=works_count:>20` |
| `sort` | Sort order | `sort=cited_by_count:desc` |
| `per-page` | Results per page | `per-page=10` |

### Author Filters

| Filter | Example |
|--------|---------|
| `display_name.search` | `display_name.search:smith` |
| `last_known_institution.display_name` | `last_known_institution.display_name:WVU` |
| `works_count` | `works_count:>10` |
| `cited_by_count` | `cited_by_count:>500` |
| `orcid` | `orcid:0000-0002-1234-5678` |

### Author Response Fields

| Field | Description |
|-------|-------------|
| `id` | OpenAlex author ID |
| `display_name` | Author name |
| `orcid` | ORCID URL |
| `works_count` | Total publication count |
| `cited_by_count` | Total citations |
| `h_index` | h-index |
| `last_known_institution` | Most recent institution |
| `counts_by_year` | Per-year works and citation counts |

### Examples

```bash
# Find authors publishing on lithium recovery
curl -s "https://api.openalex.org/authors?search=lithium+brine+recovery&per-page=10&sort=cited_by_count:desc" \
  -H "User-Agent: OpenAlexClient/1.0 (mailto:research@mail.wvu.edu)" \
  | jq '.results[] | {display_name, works_count, cited_by_count, last_known_institution}'
```

---

## /concepts

OpenAlex controlled vocabulary for topics. Use to find concept IDs for
precise filtering.

### Examples

```bash
# Find concept ID for "Lithium"
curl -s "https://api.openalex.org/concepts?search=lithium+extraction&per-page=5" \
  -H "User-Agent: OpenAlexClient/1.0 (mailto:research@mail.wvu.edu)" \
  | jq '.results[] | {id, display_name, level, works_count}'

# Get concept details and related concepts
curl -s "https://api.openalex.org/concepts/C76729985" \
  -H "User-Agent: OpenAlexClient/1.0 (mailto:research@mail.wvu.edu)"
```

---

## Pagination

### Page-Based (for small result sets, max 10,000 results)

```bash
# Page 1
curl -s "https://api.openalex.org/works?search=produced+water&per-page=200&page=1" ...

# Page 2
curl -s "https://api.openalex.org/works?search=produced+water&per-page=200&page=2" ...
```

### Cursor-Based (for large result sets, unlimited depth)

```bash
# Step 1: Start with cursor=* to get first page and next cursor
RESPONSE=$(curl -s "https://api.openalex.org/works?search=produced+water&per-page=200&cursor=*" \
  -H "User-Agent: OpenAlexClient/1.0 (mailto:research@mail.wvu.edu)")

# Extract next cursor
NEXT_CURSOR=$(echo $RESPONSE | jq -r '.meta.next_cursor')

# Step 2: Use next_cursor for subsequent pages
curl -s "https://api.openalex.org/works?search=produced+water&per-page=200&cursor=${NEXT_CURSOR}" \
  -H "User-Agent: OpenAlexClient/1.0 (mailto:research@mail.wvu.edu)"
```

Cursor pagination terminates when `meta.next_cursor` is `null`.

### Pagination Response Metadata

```json
{
  "meta": {
    "count": 15423,
    "db_response_time_ms": 87,
    "page": 1,
    "per_page": 200,
    "next_cursor": "IlsxOTk5MTIzNDU2XSI="
  },
  "results": [ ... ]
}
```

---

## Group-By Aggregation

Use `group-by` to aggregate result counts without fetching all records:

```bash
# Publication count by year for a search query
curl -s "https://api.openalex.org/works?search=hydraulic+fracturing+water&group-by=publication_year" \
  -H "User-Agent: OpenAlexClient/1.0 (mailto:research@mail.wvu.edu)" \
  | jq '.group_by | sort_by(.key) | .[] | {year: .key, count}'

# OA breakdown
curl -s "https://api.openalex.org/works?search=produced+water+treatment&group-by=open_access.oa_status" \
  -H "User-Agent: OpenAlexClient/1.0 (mailto:research@mail.wvu.edu)" \
  | jq '.group_by[]'

# Top journals for a topic
curl -s "https://api.openalex.org/works?search=direct+lithium+extraction&group-by=primary_location.source.display_name&per-page=20" \
  -H "User-Agent: OpenAlexClient/1.0 (mailto:research@mail.wvu.edu)" \
  | jq '.group_by | sort_by(-.count) | .[0:10]'
```

`group-by` response structure:
```json
{
  "meta": {"count": 4521},
  "group_by": [
    {"key": "2023", "key_display_name": "2023", "count": 412},
    {"key": "2022", "key_display_name": "2022", "count": 387}
  ]
}
```

---

## Select (Partial Response)

Use `select` to return only specific fields, reducing response size:

```bash
# Return only title, DOI, year, and citation count
curl -s "https://api.openalex.org/works?search=Marcellus+lithium&per-page=50&sort=cited_by_count:desc&select=id,doi,title,publication_year,cited_by_count,open_access" \
  -H "User-Agent: OpenAlexClient/1.0 (mailto:research@mail.wvu.edu)"
```

---

## Rate Limits

| Pool | Condition | Rate |
|------|-----------|------|
| Polite pool | `mailto:` in User-Agent | 100,000 requests/day, no per-second limit |
| Anonymous pool | No User-Agent | 10 requests/second |

Always use the polite pool by including `mailto:` in the User-Agent header.

---

## Work Type Values

| Type | Description |
|------|-------------|
| `article` | Journal article |
| `book-chapter` | Book chapter |
| `dissertation` | PhD/MS thesis |
| `book` | Monograph |
| `dataset` | Dataset |
| `preprint` | Preprint (arXiv, ESSOAr, etc.) |
| `review` | Review article |
| `report` | Technical report |
| `standard` | Industry standard |
| `editorial` | Editorial |
| `letter` | Letter |
| `erratum` | Correction |

Filter to only journal articles: `filter=type:article`

---

## Useful Concept IDs for PNGE Research

Find concept IDs via `/concepts?search=TERM`. Common ones:

| Concept | Notes |
|---------|-------|
| Lithium | Search `concepts?search=lithium` for ID |
| Produced water | May appear as "produced water" or "formation water" |
| Hydraulic fracturing | Major concept with many sub-concepts |
| Geochemistry | Broad concept covering brine chemistry |
| Direct lithium extraction | Emerging concept; may have limited coverage |
| Shale gas | Covers Marcellus, Utica research |

---

## Go Example: Search and Display Citations

```go
package main

import (
    "encoding/json"
    "fmt"
    "io"
    "net/http"
    "net/url"
    "strings"
)

type Work struct {
    ID              string `json:"id"`
    DOI             string `json:"doi"`
    Title           string `json:"title"`
    PublicationYear int    `json:"publication_year"`
    CitedByCount    int    `json:"cited_by_count"`
    PrimaryLocation struct {
        Source struct {
            DisplayName string `json:"display_name"`
        } `json:"source"`
    } `json:"primary_location"`
    Authorships []struct {
        Author struct {
            DisplayName string `json:"display_name"`
        } `json:"author"`
    } `json:"authorships"`
    OpenAccess struct {
        IsOA  bool   `json:"is_oa"`
        OAURL string `json:"oa_url"`
    } `json:"open_access"`
    AbstractInvertedIndex map[string][]int `json:"abstract_inverted_index"`
}

type OpenAlexResponse struct {
    Meta struct {
        Count      int    `json:"count"`
        Page       int    `json:"page"`
        PerPage    int    `json:"per_page"`
        NextCursor string `json:"next_cursor"`
    } `json:"meta"`
    Results []Work `json:"results"`
}

func reconstructAbstract(idx map[string][]int) string {
    if len(idx) == 0 {
        return "(abstract not available)"
    }
    maxPos := 0
    for _, positions := range idx {
        for _, p := range positions {
            if p > maxPos {
                maxPos = p
            }
        }
    }
    words := make([]string, maxPos+1)
    for word, positions := range idx {
        for _, p := range positions {
            words[p] = word
        }
    }
    result := make([]string, 0)
    for _, w := range words {
        if w != "" {
            result = append(result, w)
        }
    }
    return strings.Join(result, " ")
}

func searchWorks(query string, perPage int) ([]Work, int, error) {
    params := url.Values{}
    params.Set("search", query)
    params.Set("per-page", fmt.Sprintf("%d", perPage))
    params.Set("sort", "cited_by_count:desc")

    req, err := http.NewRequest("GET",
        "https://api.openalex.org/works?"+params.Encode(), nil)
    if err != nil {
        return nil, 0, err
    }
    req.Header.Set("User-Agent", "OpenAlexClient/1.0 (mailto:research@mail.wvu.edu)")

    client := &http.Client{}
    resp, err := client.Do(req)
    if err != nil {
        return nil, 0, fmt.Errorf("HTTP request failed: %w", err)
    }
    defer resp.Body.Close()

    body, _ := io.ReadAll(resp.Body)
    var result OpenAlexResponse
    if err := json.Unmarshal(body, &result); err != nil {
        return nil, 0, fmt.Errorf("parsing JSON: %w", err)
    }

    return result.Results, result.Meta.Count, nil
}

func firstAuthors(work Work, n int) string {
    names := make([]string, 0)
    for i, a := range work.Authorships {
        if i >= n {
            names = append(names, "et al.")
            break
        }
        // Last name only for brevity
        parts := strings.Fields(a.Author.DisplayName)
        if len(parts) > 0 {
            names = append(names, parts[len(parts)-1])
        }
    }
    return strings.Join(names, ", ")
}

func main() {
    works, total, err := searchWorks("direct lithium extraction produced water", 10)
    if err != nil {
        fmt.Printf("Error: %v\n", err)
        return
    }

    fmt.Printf("Total results: %d (showing top 10 by citation count)\n\n", total)
    fmt.Printf("%-55s %-20s %4s %6s  %s\n",
        "Title", "Authors", "Year", "Cites", "OA")
    fmt.Println(strings.Repeat("-", 100))

    for _, w := range works {
        title := w.Title
        if len(title) > 53 {
            title = title[:50] + "..."
        }
        oa := "No"
        if w.OpenAccess.IsOA {
            oa = "Yes"
        }
        fmt.Printf("%-55s %-20s %4d %6d  %s\n",
            title, firstAuthors(w, 2), w.PublicationYear, w.CitedByCount, oa)
    }
}
```
