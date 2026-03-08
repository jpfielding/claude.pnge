---
name: openalex
description: >
  Search OpenAlex for peer-reviewed academic literature on petroleum engineering,
  geochemistry, critical minerals, produced water treatment, direct lithium
  extraction, hydraulic fracturing, and related topics. Use this skill when the
  user asks to find journal articles, academic papers, citations, or research
  literature on any topic related to petroleum engineering or geoscience. Trigger
  for phrases like "find papers on direct lithium extraction", "academic
  literature on produced water treatment", "citations for Marcellus Shale
  research", "who has published on DLE from brines", "peer-reviewed papers on
  hydraulic fracturing chemicals", "open access articles on critical mineral
  supply chains", "recent publications on wellbore stability", or any request for
  academic or research literature. Covers 250 million-plus works across all
  disciplines with full open-access PDFs where available. Produces citation
  tables with abstracts and DOI links.
---

# OpenAlex Literature Search Skill

Searches OpenAlex — a free, open index of 250M+ scholarly works — for
peer-reviewed publications on petroleum engineering, geochemistry, and
critical minerals topics.

---

## API Key Handling

No API key required. The OpenAlex API is fully public.

**Polite pool (recommended):** Include a `mailto:` address in the User-Agent
header for faster responses and higher rate limits (100k requests/day vs
10/second throttle):

```bash
-H "User-Agent: OpenAlexClient/1.0 (mailto:research@mail.wvu.edu)"
```

---

## Data Sources and API Structure

**Base URL:** `https://api.openalex.org`

### Key Endpoints

| Endpoint | What It Returns |
|----------|----------------|
| `/works` | Publications: articles, books, theses, conference papers |
| `/authors` | Author profiles with publication counts and h-index |
| `/sources` | Journals and repositories |
| `/concepts` | Controlled vocabulary topic tags |
| `/institutions` | Institutional affiliations |

---

## Workflow

### Step 1 — Resolve Search Terms

Map user intent to OpenAlex search parameters:

| User Intent | Query Strategy |
|------------|----------------|
| Topic keyword search | `?search=direct+lithium+extraction` |
| Title-specific search | `?filter=title.search:produced+water` |
| Open access only | Add `filter=open_access.is_oa:true` |
| Recent papers | Add `filter=publication_year:>2019` |
| Specific journal | Add `filter=primary_location.source.display_name:Desalination` |
| By author | `?filter=author.display_name:smith+lithium` |
| Most cited | Add `sort=cited_by_count:desc` |

### Step 2 — Search Works

```bash
# Basic keyword search, sorted by citation count
curl -s "https://api.openalex.org/works?search=direct+lithium+extraction+produced+water&per-page=10&sort=cited_by_count:desc" \
  -H "User-Agent: OpenAlexClient/1.0 (mailto:research@mail.wvu.edu)"

# Filtered: open access papers after 2019
curl -s "https://api.openalex.org/works?search=Marcellus+shale+lithium&filter=open_access.is_oa:true,publication_year:>2019&per-page=10&sort=cited_by_count:desc" \
  -H "User-Agent: OpenAlexClient/1.0 (mailto:research@mail.wvu.edu)"

# Multiple filters with comma separation
curl -s "https://api.openalex.org/works?filter=title.search:produced+water+treatment,publication_year:>2020&per-page=15&sort=publication_date:desc" \
  -H "User-Agent: OpenAlexClient/1.0 (mailto:research@mail.wvu.edu)"
```

### Step 3 — Parse Response

```json
{
  "meta": {"count": 1247, "page": 1, "per_page": 10},
  "results": [
    {
      "id": "https://openalex.org/W2741809807",
      "doi": "https://doi.org/10.1016/j.watres.2020.116198",
      "title": "Lithium recovery from produced water: A review",
      "display_name": "Lithium recovery from produced water: A review",
      "publication_year": 2020,
      "publication_date": "2020-09-15",
      "primary_location": {
        "source": {"display_name": "Water Research", "issn_l": "0043-1354"}
      },
      "authorships": [
        {"author": {"display_name": "Jane Smith"}, "institutions": [{"display_name": "WVU"}]}
      ],
      "cited_by_count": 312,
      "open_access": {"is_oa": true, "oa_url": "https://example.com/paper.pdf"},
      "abstract_inverted_index": {"Lithium": [0], "recovery": [1], "from": [2]},
      "concepts": [{"display_name": "Lithium", "score": 0.95}]
    }
  ]
}
```

### Step 4 — Reconstruct Abstract

OpenAlex stores abstracts as an inverted index `{word: [positions]}`.
Reconstruct by sorting positions:

```python
import json

def reconstruct_abstract(inverted_index):
    if not inverted_index:
        return "(abstract not available)"
    word_positions = []
    for word, positions in inverted_index.items():
        for pos in positions:
            word_positions.append((pos, word))
    word_positions.sort(key=lambda x: x[0])
    return " ".join(w for _, w in word_positions)
```

### Step 5 — Output

Format as citation table with narrative summary.

---

## Output Format

```
## Literature Search Results: Direct Lithium Extraction from Produced Water

**Search query:** "direct lithium extraction produced water"
**Total results in OpenAlex:** 1,247
**Showing:** Top 10 by citation count

| Title | Authors | Year | Journal | Citations | OA |
|-------|---------|------|---------|-----------|-----|
| Lithium recovery from produced water: A review | Smith et al. | 2020 | Water Research | 312 | Yes |
| DLE sorbent performance in high-TDS brines | Jones & Liu | 2021 | Desalination | 187 | No |

**Key Themes:** Research on DLE from produced water clusters around three
themes: (1) sorbent material development (H₂TiO₃, Al-based), (2) economic
viability at sub-100 mg/L Li concentrations, and (3) Appalachian basin
brine characterization for resource estimation.

**Data source:** OpenAlex (https://openalex.org). Coverage: 250M+ works.
Open access links where available via Unpaywall integration.
```

---

## Pagination

OpenAlex supports cursor-based pagination for large result sets:

```bash
# First page — get cursor from response meta.next_cursor
curl -s "https://api.openalex.org/works?search=lithium+brine&per-page=200&cursor=*" \
  -H "User-Agent: OpenAlexClient/1.0 (mailto:research@mail.wvu.edu)"

# Subsequent pages using next_cursor value
curl -s "https://api.openalex.org/works?search=lithium+brine&per-page=200&cursor=CURSOR_VALUE" \
  -H "User-Agent: OpenAlexClient/1.0 (mailto:research@mail.wvu.edu)"
```

---

## Error Handling

| Condition | Meaning | Action |
|-----------|---------|--------|
| HTTP 429 | Rate limit exceeded | Add `mailto:` User-Agent for polite pool; wait 1s |
| `meta.count` = 0 | No results | Broaden search terms, remove filters |
| `abstract_inverted_index` null | No abstract available | Note "(abstract restricted by publisher)" |
| `open_access.oa_url` null but `is_oa: true` | OA version not indexed | Check publisher DOI directly |
| Very large count (>10,000) | Too broad | Add year filter or concept filter |
| DOI resolves to paywall | Publisher restriction | Note in output; suggest interlibrary loan |

---

## Filter Reference

Common filter combinations for PNGE research:

```bash
# Appalachian basin shale research, last 5 years, open access
filter=title.search:Marcellus+shale,publication_year:>2019,open_access.is_oa:true

# DLE technology papers, highly cited
filter=title.search:direct+lithium+extraction&sort=cited_by_count:desc

# WVU-affiliated publications
filter=institutions.display_name:West+Virginia+University

# Papers in specific journal
filter=primary_location.source.issn:1385-8947
```

---

## Caveats

- OpenAlex coverage is strong for journal articles (>2000 onward) and
  weaker for conference papers and technical reports. For DOE reports,
  use `pnge:doe-osti` instead.
- Abstract reconstruction from the inverted index may have minor
  formatting artifacts (no punctuation in some cases).
- Citation counts are updated periodically, not in real-time.
- Some publisher abstracts are not available due to licensing restrictions.
- For USGS publications, `pnge:usgs-pubs` provides better coverage than
  OpenAlex.
