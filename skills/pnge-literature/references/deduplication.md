# Deduplication Rules for pnge-literature

When the same paper is indexed by more than one source (common case:
OpenAlex + CrossRef both index a journal article; USGS Fact Sheet also
appears in OpenAlex; DOE OSTI journal article is also in CrossRef),
merge the records so the student sees one row per paper with the
richest metadata from each source.

---

## Key: DOI-First, Title-Fallback

**Primary join key:** normalized DOI.

**Fallback key:** normalized title (for records missing a DOI — rare
in OpenAlex, common in OSTI presentations and older USGS OFRs).

---

## DOI Normalization

```
doi_raw:  "https://doi.org/10.1016/j.watres.2020.116198"
doi_raw:  "DOI:10.1016/J.WATRES.2020.116198"
doi_raw:  "10.1016/j.watres.2020.116198"
---------------------------------------------------------
normalized:  10.1016/j.watres.2020.116198    # lowercase, no URL prefix
```

Regex to extract + normalize:
```
m := regexp.MustCompile(`10\.\d{4,9}/\S+`).FindString(raw)
doi := strings.ToLower(m)
```

Reject anything outside `/^10\.\d{4,9}\//`.

---

## Title Normalization (for no-DOI records)

1. Lowercase
2. Strip HTML/JATS tags: `<[^>]*>` → ``
3. Replace punctuation and whitespace runs with single space
4. Trim

Then compare two titles with Levenshtein ratio:
```
ratio = 1 - (levenshtein(a, b) / max(len(a), len(b)))
```

**Match threshold: ratio >= 0.92.** Higher is safer; lower produces
false positives for review articles with similar titles.

---

## Merge Precedence (per field)

When two records share a normalized DOI (or title), build the merged
record field-by-field using this precedence:

| Field        | Rule                                                         |
|--------------|--------------------------------------------------------------|
| `doi`        | Identical by join construction                               |
| `title`      | Longest non-empty string after markup stripping              |
| `authors`    | Longest list. If tie, prefer OpenAlex (disambiguated)        |
| `year`       | If mismatched, prefer CrossRef published-print, then OpenAlex `publication_year` |
| `venue`      | Non-empty. Prefer CrossRef `container-title` > OpenAlex `primary_location.source.display_name` > USGS `seriesTitle + seriesNumber` > OSTI `research_orgs[0]` |
| `type`       | Prefer CrossRef type (canonical) > OpenAlex `type` > USGS/OSTI |
| `abstract`   | Longest non-empty string                                     |
| `citations`  | `max()` across sources (never sum — they overlap)            |
| `open_access`| `true` if ANY source says true                               |
| `pdf_url`    | First non-empty in order: OpenAlex `oa_url` > OSTI `fulltext` > USGS `links[Document]` > CrossRef `link[0].URL` |
| `source`     | Comma-joined alphabetical: `"crossref,openalex"`             |
| `source_id`  | Map per source: `{"openalex": "W...", "crossref": "DOI", "usgs-pw": "fs20243052", "doe-osti": "3027695"}` |
| `provenance` | Ordered list of sources that contributed data                 |

---

## Tie-Breakers for Year Mismatch

CrossRef `published-print` and OpenAlex `publication_year` occasionally
differ (online-first vs print). The policy:

1. If any source's year differs by more than 1, prefer the earliest
   reported year and record a note `year_conflict: true`.
2. If within 1 year, use CrossRef `published-print.date-parts[0][0]`
   when available, else OpenAlex.

---

## Group-and-Fold Algorithm (Pseudocode)

```go
func Deduplicate(records []Record) []Record {
    byDOI := map[string][]Record{}
    noDOI := []Record{}

    for _, r := range records {
        if r.DOI != "" {
            k := normalizeDOI(r.DOI)
            byDOI[k] = append(byDOI[k], r)
        } else {
            noDOI = append(noDOI, r)
        }
    }

    var merged []Record
    for _, group := range byDOI {
        merged = append(merged, mergeGroup(group))
    }

    // Title-fallback pass for records without DOI
    for _, r := range noDOI {
        placed := false
        for i, m := range merged {
            if titleMatch(r.Title, m.Title) {
                merged[i] = mergeGroup([]Record{m, r})
                placed = true
                break
            }
        }
        if !placed {
            for i, other := range noDOI {
                if other.SourceID == r.SourceID { continue }
                if titleMatch(r.Title, other.Title) {
                    // handled in outer pass
                }
            }
            merged = append(merged, r)
        }
    }

    sort.Slice(merged, func(i, j int) bool {
        if merged[i].Citations != merged[j].Citations {
            return merged[i].Citations > merged[j].Citations
        }
        return merged[i].Year > merged[j].Year
    })
    return merged
}
```

---

## Worked Example

Four raw hits for a DLE review paper:

| Raw from   | DOI                               | Title                                  | Authors      | Cites | OA   |
|------------|-----------------------------------|----------------------------------------|--------------|-------|------|
| openalex   | 10.1016/j.watres.2020.116198      | Lithium recovery from produced water: A review | Smith,Doe,Lee | 312 | true |
| crossref   | 10.1016/j.watres.2020.116198      | Lithium recovery from produced water: A review | Smith,Doe    | 287 | null |
| doe-osti   | (no DOI, same title)              | Lithium recovery from produced water — A review | Smith (NREL) | —   | true |
| usgs-pw    | —                                 | —                                      | —            | —    | —    |

Merged record:

```json
{
  "doi": "10.1016/j.watres.2020.116198",
  "title": "Lithium recovery from produced water: A review",
  "authors": ["Smith", "Doe", "Lee"],
  "year": 2020,
  "venue": "Water Research",
  "type": "journal-article",
  "citations": 312,
  "open_access": true,
  "pdf_url": "https://.../water-research/oa.pdf",
  "source": "crossref,doe-osti,openalex",
  "provenance": ["openalex", "crossref", "doe-osti"]
}
```

The OSTI record was folded into the DOI cluster via title match
(Levenshtein ratio 0.96 on the normalized title) even though OSTI
omitted the DOI.

---

## Edge Cases

### Case: Same DOI, different titles

Happens when one source mis-titles (e.g. includes subtitle, missing
colon). Take the longer title. Do NOT treat as conflict.

### Case: DOI registered twice (rare)

Some retracted papers get a second DOI. Treat each DOI as a distinct
record. Students can see both and investigate.

### Case: CrossRef 404 on `10.5066` or `10.25338`

USGS data DOIs live in DataCite. Don't count a 404 as "paper doesn't
exist" — annotate the record with a suggestion to run
`pnge:datacite-doi` for full metadata.

### Case: OSTI journal article with embargo

Fulltext link may be present but return 403 until embargo lifts.
Record the fact, keep the DOI link.

### Case: Multiple OA sources for the same DOI

Prefer Unpaywall-resolved `oa_url` from OpenAlex — it follows
link rot better than publisher-hosted URLs.

### Case: Title-only match across unrelated papers

Mitigate by requiring Levenshtein ratio >= 0.92 AND at least one
matching author surname (if both records have authors). If neither
has author data, fall back to 0.95 threshold.
