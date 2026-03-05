---
name: usgs-pubs
description: >
  Search and retrieve publications from the USGS Publications Warehouse including
  professional papers, fact sheets, scientific investigations reports, open-file
  reports, and data series. Use this skill whenever the user asks about USGS
  reports, geological survey publications, USGS research papers, or needs to find
  government publications on topics like lithium brines, produced water
  geochemistry, critical minerals, groundwater, or any earth science subject
  covered by the U.S. Geological Survey — even if they do not explicitly mention
  USGS or the Publications Warehouse. Trigger for phrases like "find USGS
  reports on lithium", "are there any fact sheets about produced water",
  "USGS publications on critical minerals", "geological survey papers about
  Marcellus Shale", "recent USGS research", or "government reports on brine
  geochemistry". Returns publication metadata, abstracts, author lists, DOIs,
  and direct PDF download links formatted as summary tables with narrative.
---

# USGS Publications Warehouse Skill

Searches and retrieves publications from the USGS Publications Warehouse API
at `pubs.usgs.gov/pubs-services/publication`. Covers all USGS publication
series (Fact Sheets, Scientific Investigations Reports, Professional Papers,
Open-File Reports, Data Series, Circulars, Techniques and Methods) plus
journal articles with USGS-affiliated authors.

## Credential

**None required.** The USGS Publications Warehouse API is fully public and
unauthenticated. No API key, no headers, no signup.

---

## API Structure

**Base URL:** `https://pubs.usgs.gov/pubs-services/publication`

Note: The older hostname `pubs.er.usgs.gov` redirects (301) to `pubs.usgs.gov`.
Always use the canonical base and always follow redirects (`curl -sL`).

**Key search parameters:**

| Parameter            | Example                                  | Notes                                    |
|----------------------|------------------------------------------|------------------------------------------|
| `q`                  | `q=lithium+produced+water`               | Free-text keyword search                 |
| `title`              | `title=critical+minerals`                | Title-only search                        |
| `year`               | `year=2024`                              | Filter by publication year               |
| `typeName`           | `typeName=Report`                        | `Report` or `Article`                    |
| `subtypeName`        | `subtypeName=USGS+Numbered+Series`       | `USGS Numbered Series` or `Journal Article` |
| `contributingOffice` | `contributingOffice=Eastern+Energy+...`  | USGS office/program filter               |
| `pub_x_days`         | `pub_x_days=30`                          | Published in last X days                 |
| `page_size`          | `page_size=25`                           | Results per page                         |
| `page_number`        | `page_number=2`                          | Pagination (1-indexed)                   |

All parameters are AND-joined when combined.

**Get a single publication:**

```
GET https://pubs.usgs.gov/pubs-services/publication/{indexId}
```

Where `indexId` is a string like `fs20243052` or a numeric ID like `70261664`.

---

## Workflow

### Step 1 — Resolve Intent

Map the user's question to search parameters:

- Topic keywords go in `q` (or `title` for title-only searches)
- If user specifies a year, add `year=YYYY`
- If user wants only official USGS reports (not journal articles), add `typeName=Report`
- If user wants recent publications, use `pub_x_days=N`
- If user provides a specific publication ID or DOI, fetch directly by indexId

Common mappings:

| User says...                              | Parameters                                           |
|-------------------------------------------|------------------------------------------------------|
| "USGS reports on lithium"                 | `q=lithium&typeName=Report`                          |
| "recent USGS fact sheets"                 | `pub_x_days=90&subtypeName=USGS+Numbered+Series`    |
| "USGS publications about produced water"  | `q=produced+water`                                   |
| "2024 critical minerals reports"          | `q=critical+minerals&year=2024&typeName=Report`      |
| "find USGS paper fs20243052"              | Direct fetch: `/publication/fs20243052`              |

### Step 2 — Fetch Results

**Search example:**
```bash
curl -sL "https://pubs.usgs.gov/pubs-services/publication?q=lithium+produced+water&typeName=Report&page_size=10"
```

**Single publication example:**
```bash
curl -sL "https://pubs.usgs.gov/pubs-services/publication/fs20243052"
```

**Recent publications (last 30 days):**
```bash
curl -sL "https://pubs.usgs.gov/pubs-services/publication?pub_x_days=30&page_size=25"
```

### Step 3 — Parse Response

**Search response structure:**
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
      "docAbstract": "Lithium-rich brine deposits occur...",
      "contributors": {
        "authors": [
          {"family": "Knierim", "given": "Katherine", "usgs": true},
          {"family": "Masterson", "given": "Andrew", "usgs": true}
        ]
      },
      "links": [
        {"type": {"text": "Document"}, "url": "https://pubs.usgs.gov/.../fs20243052.pdf"}
      ],
      "country": "United States",
      "state": "Arkansas"
    }
  ]
}
```

Key extraction targets per record:

| Field                                 | Use                                      |
|---------------------------------------|------------------------------------------|
| `title`                               | Publication title                        |
| `publicationYear`                     | Year                                     |
| `seriesTitle.text` + `seriesNumber`   | Series name and number (e.g., FS 2024-3052) |
| `doi`                                 | DOI link                                 |
| `docAbstract`                         | Abstract (may contain HTML, strip tags)  |
| `contributors.authors[]`             | Author list (family, given, usgs flag)   |
| `links[]` where type.text="Document"  | PDF download URL                         |
| `state`, `country`                    | Geographic focus                         |
| `usgsCitation`                        | Full USGS citation string                |

### Step 4 — Produce Output

**Format: Publication Table + Narrative Summary**

Present a markdown table of matching publications (cap at ~15 rows), then
a narrative summary covering:

1. **Result count** — total publications found
2. **Key findings** — highlight the most relevant publications to the query
3. **Series breakdown** — how many are Fact Sheets, SIRs, OFRs, etc.
4. **Recency** — note the most recent publications and any trends
5. **Access** — provide direct PDF links for top results
6. **Related data** — note any associated data releases (linked via Data Release link type)

**Example output structure:**
```
## USGS Publications: Lithium in Produced Water

| Year | Series        | Title                                                    | DOI                          |
|------|---------------|----------------------------------------------------------|------------------------------|
| 2024 | Fact Sheet    | Lithium resource in the Smackover Formation brines of... | 10.3133/fs20243052           |
| 2024 | Journal       | Machine learning approaches to identify lithium...       | 10.1007/s13563-024-00442-3   |
| 2022 | SIR           | Potential effects of energy development on...             | 10.3133/sir20175070C         |
| ...  | ...           | ...                                                      | ...                          |

**Summary:** Found 50 publications matching "lithium produced water" in the
USGS Publications Warehouse. The most recent is a 2024 Fact Sheet (FS 2024-3052)
on lithium resources in Smackover Formation brines of southern Arkansas, which
includes a companion data release. Several Scientific Investigations Reports
address produced water geochemistry in the Appalachian Basin. PDF downloads
are freely available for all USGS Numbered Series publications.
```

---

## Pagination

If `recordCount` exceeds `page_size`, paginate by incrementing `page_number`:

```python
page = 1
all_records = []
while True:
    # fetch with page_number=page, page_size=25
    all_records.extend(records)
    if len(all_records) >= record_count:
        break
    page += 1
```

For large result sets (100+ records), ask the user if they want all results
or prefer a filtered subset.

---

## Error Handling

| HTTP Code | Meaning            | Action                                                 |
|-----------|--------------------|--------------------------------------------------------|
| 200       | Success            | Parse JSON response normally                           |
| 301       | Redirect           | Follow redirect (use `curl -sL`); update base URL      |
| 400       | Bad request        | Check parameter names and values; review API reference |
| 404       | Not found          | Publication ID does not exist; verify the indexId       |
| 500       | Server error       | Retry after a few seconds; USGS servers occasionally timeout |
| Timeout   | No response        | Retry; consider smaller page_size                      |

If a search returns `recordCount: 0`, suggest:
- Broadening the query (fewer keywords)
- Removing year or type filters
- Trying alternative terms (e.g., "brine" instead of "produced water")

---

## USGS Series Quick Reference

| Code | Full Name                          | Typical Use                            |
|------|------------------------------------|----------------------------------------|
| FS   | Fact Sheet                         | 2-6 page public summaries              |
| SIR  | Scientific Investigations Report   | Detailed scientific studies             |
| OFR  | Open-File Report                   | Preliminary data and methods            |
| PP   | Professional Paper                 | Major research monographs              |
| DS   | Data Series                        | Data compilations with documentation   |
| CIR  | Circular                           | General-audience science summaries     |
| TM   | Techniques and Methods             | Methodological guides                  |

---

## Caveats and Data Limitations

- **Coverage:** Only publications with USGS-affiliated authors or published
  through USGS series. Does not include DOE, EPA, or other agency publications
  (use `doe-osti` or `epa-enviro` skills for those).
- **Abstracts contain HTML:** The `docAbstract` field often includes HTML tags
  (`<p>`, `<span>`, `<sup>`, etc.). Strip HTML before displaying.
- **Journal articles:** The Warehouse indexes journal articles with USGS
  co-authors, but the full text may be behind a publisher paywall. PDF links
  point to the publisher page, not a free download. USGS Numbered Series
  publications are always freely available.
- **Search relevance:** The `q` parameter performs broad full-text search.
  Results are ranked by relevance but not always perfectly ordered. Combining
  `q` with `typeName` or `year` improves precision.
- **Metadata completeness:** Older publications (pre-2000) may have sparse
  metadata — missing abstracts, DOIs, or geographic fields.
- **Update frequency:** New publications appear as they are approved. There is
  no fixed release schedule. Use `pub_x_days` to track recent releases.
- **Geographic fields:** The `state` and `country` fields reflect the study
  area, not the author location. Not all records have geographic metadata.

---

## Implementation Notes

- **Use `bash_tool` with `curl -sL` + `jq`** for API calls (always follow redirects)
- **Python client** — see `references/python_example.py` (stdlib only, no dependencies)
- **API reference** — see `references/api_reference.md` for full parameter and
  response documentation
- **Strip HTML from abstracts** before presenting to user: pipe through
  `sed 's/<[^>]*>//g'` in bash or use `re.sub(r'<[^>]+>', '', text)` in Python
- **DOI links:** Format as `https://doi.org/{doi}` for clickable URLs
- **PDF links:** Look for `links[]` where `type.text == "Document"` — these
  are direct PDF downloads for USGS series publications
