---
name: pnge-literature
description: >
  Unified literature search across OpenAlex, CrossRef, USGS Publications
  Warehouse, and DOE OSTI. Use whenever the user asks for academic search,
  literature search, journal articles, technical reports, citations, or
  DOI lookups on petroleum engineering, geochemistry, critical minerals,
  produced water, direct lithium extraction, or reservoir topics. Trigger
  for phrases like find papers on direct lithium extraction, literature
  search on Marcellus Shale, look up this DOI, USGS reports on produced
  water, DOE OSTI reports on critical minerals, NETL technical reports,
  OpenAlex search, CrossRef lookup, most cited papers on lithium brine,
  peer-reviewed literature on magnesium recovery, find fact sheets,
  national lab publications, or who wrote this paper. Auto-routes by
  query cues and de-duplicates by DOI. For USGS data DOIs 10.5066 or
  OSTI dataset DOIs point at pnge-core:datacite-doi. Output: unified citation
  table with DOI, year, authors, source, open-access flag, plus narrative.
---

# PNGE Literature Search Skill

A single orchestrated entry point for scholarly discovery across four
complementary sources. The student asks "find papers on X" and the skill
decides which source(s) to query, merges results, de-duplicates by DOI,
and returns a unified citation table.

## Sources (Adapters)

| Adapter    | Index / API                                          | Best For                                                     |
|------------|------------------------------------------------------|--------------------------------------------------------------|
| `openalex` | `https://api.openalex.org/works`                     | Broadest academic coverage, 250M+ works, citations, OA flag  |
| `crossref` | `https://api.crossref.org/works`                     | Publisher-issued DOIs, journal article metadata, funders     |
| `usgs-pw`  | `https://pubs.usgs.gov/pubs-services/publication`    | USGS Professional Papers, Fact Sheets, Open-File Reports     |
| `doe-osti` | `https://www.osti.gov/api/v1/records`                | DOE-funded research: NETL, national labs, university grants  |

A fifth sibling skill, `pnge-core:datacite-doi`, handles research-data DOIs
registered with DataCite (USGS `10.5066`, some OSTI `10.2172`, Zenodo,
Figshare, Dryad). This skill does NOT merge DataCite in — it points at
`pnge-core:datacite-doi` when a CrossRef 404 suggests a DataCite DOI.

---

## Credentials

**None required for any adapter.** All four APIs are fully public.

**Optional OpenAlex + CrossRef polite pool:** providing a contact email
yields faster rate limits and priority routing. Resolution order:

1. `~/.config/pnge-literature/credentials` — parse `mailto=you@example.com`
2. `~/.config/openalex/credentials` or `~/.config/crossref/credentials`
3. `PNGE_MAILTO`, `OPENALEX_MAILTO`, or `CROSSREF_MAILTO` env var
4. Omit — public pool still works, just slower

```bash
MAILTO=$(grep '^mailto=' ~/.config/pnge-literature/credentials 2>/dev/null | cut -d= -f2)
[ -z "$MAILTO" ] && MAILTO="${PNGE_MAILTO:-${CROSSREF_MAILTO:-${OPENALEX_MAILTO}}}"
```

The mailto is a contact address, not a secret. Any valid email works.

---

## Workflow

### Step 1 — Resolve Intent and Route

Parse the user's request, detect a `--source <name>` hint if present, and
otherwise apply the routing matrix below.

**Explicit source override:** if the user says "search OpenAlex",
"search CrossRef", "search USGS Publications Warehouse", or "search OSTI"
use that source only.

**DOI pattern:** if the query contains a DOI (`10.\d{4,9}/\S+`), route
by prefix:

| DOI Prefix         | Adapter                   | Notes                                                         |
|--------------------|---------------------------|---------------------------------------------------------------|
| `10.3133`          | `usgs-pw`                 | USGS Numbered Series — direct indexId lookup                  |
| `10.2172`          | `doe-osti`                | OSTI identifier — may also resolve via `pnge-core:datacite-doi`    |
| `10.5066`          | `pnge-core:datacite-doi`       | USGS data releases — NOT in CrossRef, use DataCite            |
| anything else      | `crossref`                | Publisher DOI — CrossRef is authoritative                     |

**Keyword routing (no DOI):**

| Query Cue                                                  | Adapter(s)                       |
|------------------------------------------------------------|----------------------------------|
| mentions "USGS" / "Fact Sheet" / "Open-File Report" / "SIR" / "Professional Paper" | `usgs-pw`               |
| mentions "DOE" / "NETL" / "Sandia" / "Berkeley Lab" / "Argonne" / "PNNL" / "ORNL" / "INL" / "NREL" / "LANL" / "LLNL" | `doe-osti`              |
| mentions "peer-reviewed" / "journal" / "citations" / "highly cited" | `openalex` + `crossref` |
| generic "find papers on X" / "literature on X"             | `openalex` first, then `crossref` for DOI enrichment |
| asks for open-access PDFs                                   | `openalex` with `is_oa:true`     |
| asks for author's works                                    | `openalex` (author disambiguation is better than CrossRef) |
| asks for a specific DOI's metadata                         | `crossref` — or DataCite if 404  |

**Auto mode:** unless a single source is clearly indicated, run
`openalex` + either `usgs-pw` or `doe-osti` based on topic heuristics
(lithium/produced-water/critical-minerals → add USGS and OSTI; generic
petroleum engineering → OpenAlex alone).

### Step 2 — Build Queries Per Adapter

See `references/adapters.md` for full parameter tables. Quick reference:

**OpenAlex:**
```bash
curl -s "https://api.openalex.org/works?search=direct+lithium+extraction+produced+water&per-page=10&sort=cited_by_count:desc" \
  -H "User-Agent: pnge-literature/1.0 (mailto:${MAILTO})"
```

**CrossRef:**
```bash
curl -s "https://api.crossref.org/works?query=lithium+produced+water&rows=10&sort=is-referenced-by-count&order=desc&select=DOI,title,author,published-print,container-title,is-referenced-by-count,abstract&mailto=${MAILTO}"
```

**USGS Publications Warehouse:**
```bash
curl -sL "https://pubs.usgs.gov/pubs-services/publication?q=lithium+produced+water&typeName=Report&page_size=10"
```

**DOE OSTI:**
```bash
curl -s "https://www.osti.gov/api/v1/records?q=lithium+produced+water&rows=10" \
  -H "Accept: application/json"
```

### Step 3 — Parse, Normalize, Merge

Each adapter returns a different shape. Normalize every hit to a common
record:

```
{
  "doi": "10.xxxx/yyyy",       // or null if none
  "title": "string",           // HTML/JATS stripped
  "authors": ["Last F.", ...],
  "year": 2024,
  "venue": "journal or series name",
  "type": "journal-article|report|fact-sheet|conference|...",
  "abstract": "string or null",
  "citations": int or null,    // only OpenAlex + CrossRef
  "open_access": bool or null, // only OpenAlex
  "pdf_url": "string or null",
  "source": "openalex|crossref|usgs-pw|doe-osti",
  "source_id": "W.../osti_id/indexId"
}
```

Then **de-duplicate by DOI** (case-insensitive). When the same DOI comes
from multiple sources, merge by taking the most-complete field values and
recording all sources in `provenance`. See `references/deduplication.md`
for the exact merge precedence.

### Step 4 — Format Output

**Unified citation table + narrative summary.** Cap at 15 rows.

```
## Literature Search: Direct Lithium Extraction from Produced Water

**Query:** direct lithium extraction produced water
**Sources queried:** OpenAlex, CrossRef, DOE OSTI
**Raw hits:** 47  |  **After dedup:** 32  |  **Shown:** top 15 by citations

| # | Year | Title                                                | Authors           | Venue / Series         | Cites | OA  | DOI                    | Source   |
|---|------|------------------------------------------------------|-------------------|------------------------|-------|-----|------------------------|----------|
| 1 | 2020 | Lithium recovery from produced water: a review      | Smith et al.      | Water Research         | 312   | Yes | 10.1016/j.watres.2020… | OA + CR  |
| 2 | 2025 | Separation of Li and Mg from brines via ZIC         | Choi H. et al.    | NETL Tech Report       | 4     | Yes | 10.2172/3016248        | OSTI     |
| 3 | 2024 | Lithium resource in Smackover Formation brines      | Knierim & Masters | USGS Fact Sheet 2024-… | 12    | Yes | 10.3133/fs20243052     | USGS-PW  |
| … | …    | …                                                    | …                 | …                      | …     | …   | …                      | …        |

**Summary:** Dominant themes are (1) DLE sorbent development (H2TiO3, Al-based),
(2) field-scale pilots in Smackover and Marcellus, and (3) techno-economic
analyses sub-100 mg/L Li feed. Most cited: Smith 2020 review (312). Most
recent DOE work: NETL zwitterionic chromatography (2025). USGS fact sheet
2024-3052 is the authoritative resource estimate for Smackover.

**Access:** OA = open access PDF available. USGS series always freely
downloadable. OSTI fulltext at `https://www.osti.gov/servlets/purl/{osti_id}`.
```

---

## Adapter Quick Reference

Full API details and pagination in `references/adapters.md`. Condensed:

### openalex
- Base: `https://api.openalex.org/works`
- Per-page: `per-page=1..200`, cursor-based deep paging
- Key filter: `filter=open_access.is_oa:true,publication_year:>2019`
- Sort: `sort=cited_by_count:desc` or `publication_date:desc`
- Abstract format: **inverted index** — reconstruct by sorting positions
- Header: `User-Agent: pnge-literature/1.0 (mailto:${MAILTO})`

### crossref
- Base: `https://api.crossref.org/works`
- Per-page: `rows=1..1000`, offset max 10000, cursor `*` for deeper paging
- Key filter: `filter=from-pub-date:2020-01-01,type:journal-article,has-abstract:true`
- Sort: `sort=is-referenced-by-count&order=desc` or `sort=relevance`
- Abstract format: **JATS XML** — strip tags before display
- Query param: `mailto=${MAILTO}`
- Note: USGS data DOIs (`10.5066`) will 404 — point at `pnge-core:datacite-doi`

### usgs-pw
- Base: `https://pubs.usgs.gov/pubs-services/publication` (use `curl -sL`)
- Page size: `page_size=1..100`, `page_number` 1-indexed
- Key params: `typeName=Report|Article`, `year=YYYY`, `pub_x_days=N`
- Single item: `/publication/{indexId}` e.g. `fs20243052` or numeric `70261664`
- Abstract format: HTML tags — strip before display
- Series codes: FS, SIR, OFR, PP, DS, CIR, TM
- No credentials, no User-Agent required

### doe-osti
- Base: `https://www.osti.gov/api/v1/records`
- Page size: `rows=1..100`, `page` 1-indexed
- Total count: **`X-Total-Count` response header** (use `curl -si`)
- Key params: `sponsor_org=NETL`, `research_org=...`, `product_type=Technical+Report`
- Product types: `Technical Report`, `Journal Article`, `Conference`, `Thesis/Dissertation`, `Patent`
- Response shape: **flat JSON array**, no wrapper
- Header required: `Accept: application/json` (otherwise XML)
- Date filter params broken (HTTP 500) — encode year in `q` string
- Fulltext URL pattern: `https://www.osti.gov/servlets/purl/{osti_id}`

---

## Intent Routing Examples

| User says...                                       | Route                                              |
|----------------------------------------------------|----------------------------------------------------|
| "find papers on DLE from produced water"           | openalex + crossref (dedup by DOI)                 |
| "USGS fact sheets on lithium"                      | usgs-pw only                                       |
| "most cited papers on Marcellus geochemistry"      | openalex (sort by citations)                       |
| "DOE reports on critical minerals"                 | doe-osti only                                      |
| "NETL work on direct lithium extraction"           | doe-osti with `sponsor_org=NETL`                   |
| "look up DOI 10.1016/j.watres.2020.116198"         | crossref single-DOI                                |
| "look up DOI 10.3133/fs20243052"                   | usgs-pw single indexId                             |
| "look up DOI 10.5066/P9DSRCZJ"                     | point at `pnge-core:datacite-doi` (not CrossRef)        |
| "papers by Stringfellow on lithium"                | openalex author filter, then crossref for DOIs     |
| "recent literature on produced water treatment"    | openalex with `publication_year:>2023`             |
| "Appalachian basin brine chemistry research"       | openalex + doe-osti + usgs-pw (topical triad)      |
| "open access papers on magnesium recovery"         | openalex with `filter=open_access.is_oa:true`      |

---

## Deduplication Rules

Full spec in `references/deduplication.md`. Short version:

1. Group records by **normalized DOI** (lowercase, strip URL prefix).
2. Within each DOI group, **merge fields** using this precedence:
   - `title`: longest non-HTML string
   - `authors`: longest list (OpenAlex typically wins)
   - `abstract`: longest non-empty after stripping markup
   - `citations`: max across sources
   - `open_access`: true if any source says true, else false
   - `pdf_url`: prefer OA url > OSTI purl > USGS links[] > CrossRef link
   - `source`: comma-joined list of all contributing adapters
3. For **records without DOI**, attempt title-similarity merge: lowercase,
   strip punctuation, compare with Levenshtein ratio > 0.92. On a match,
   merge as above. On no match, keep separate.
4. Sort merged list by citations desc, then year desc.

---

## Pagination Strategy

For each adapter, fetch one page and stop unless the user asks "all" or
"more". Warn before fetching >500 records across sources.

| Adapter   | Signal total              | Page mechanism                                           |
|-----------|---------------------------|----------------------------------------------------------|
| openalex  | `meta.count` in body      | `cursor=*` then use `meta.next_cursor`                   |
| crossref  | `message.total-results`   | `offset` up to 10000, else `cursor=*` then `next-cursor` |
| usgs-pw   | `recordCount` in body     | `page_number` 1-indexed                                  |
| doe-osti  | `X-Total-Count` header    | `page` 1-indexed                                         |

When parallel-running adapters, limit each to `per-page=25` in auto mode
to keep total time under ~3 seconds.

---

## Error Handling

| Condition                               | Source    | Action                                                               |
|-----------------------------------------|-----------|----------------------------------------------------------------------|
| HTTP 200 + empty results                | any       | Report "no hits on {source}"; try adjacent adapter or broaden query  |
| HTTP 404 on DOI lookup                  | crossref  | Fall back to DataCite via `pnge-core:datacite-doi` for prefixes 10.5066, 10.2172, 10.25338 |
| HTTP 400                                | any       | Echo error body; fix parameter names and retry                       |
| HTTP 429 rate limit                     | openalex / crossref | Add `mailto` polite-pool address; backoff 1s                |
| HTTP 500 on date filter                 | doe-osti  | Documented bug — move year into keyword `q` and retry                |
| HTTP 301 redirect                       | usgs-pw   | Always `curl -sL` to follow; `pubs.er.usgs.gov` → `pubs.usgs.gov`    |
| X-Rate-Limit-Remaining = 0              | doe-osti  | Wait 60s and retry; reduce page size                                 |
| HTML/JATS in title or abstract          | any       | Strip with `sed 's/<[^>]*>//g'` before display                       |
| Citation count = 0                      | crossref  | Crossref undercounts; cross-check OpenAlex `cited_by_count`          |
| OA flag true but no oa_url              | openalex  | Note "(OA version not indexed)" and emit DOI link only               |
| Adapter timeout                          | any       | Skip that source, annotate output, continue with remaining adapters  |

---

## Output Format (Strict)

Every response MUST include:

1. **Header** — query, sources queried, raw/dedup/shown counts
2. **Unified citation table** — 8 columns: `# | Year | Title | Authors | Venue | Cites | OA | DOI | Source`
3. **Narrative summary** — 2-5 sentences on themes, most-cited, most-recent,
   and notable series or sponsoring org
4. **Access notes** — where PDFs are free (OA flag, USGS always free, OSTI purl)
5. **Suggested refinements** — narrower filters or alternative adapters

Shorten titles to ~60 chars with ellipsis. Use "Last F." for first author
plus "et al." when 3+. Always include the DOI column even if null ("—").

---

## Go CLI

A reference Go client is in `references/golang_client.go`. Single binary:

```bash
go run references/golang_client.go \
  --source auto \
  --query "direct lithium extraction produced water" \
  --limit 10 \
  --mailto research@mail.wvu.edu
```

Flags:
- `--source openalex|crossref|usgs|osti|auto` (default: auto)
- `--query STRING` (required unless `--doi` given)
- `--doi STRING` (single-DOI lookup; routes by prefix)
- `--limit N` (default 10, max 50)
- `--year-from YYYY`, `--year-to YYYY`
- `--mailto EMAIL` (polite pool for OpenAlex + CrossRef)
- `--json` (emit unified records as JSON instead of a table)

The client implements the normalization, de-duplication, and merge
precedence described above.

---

## Cross-Skill Integration

| Companion Skill       | Use Together When...                                                       |
|-----------------------|----------------------------------------------------------------------------|
| `pnge-core:datacite-doi`   | DOI is `10.5066` (USGS data) or CrossRef returns 404 on a research-data DOI |
| `pnge-patents:patentsview`    | User wants patents alongside peer-reviewed literature (DLE tech scans)     |
| `pnge-federal-data:netl-edx`       | User needs the underlying dataset cited in an OSTI or USGS report           |
| `pnge-core:usgs-minerals`  | Commodity summaries complement USGS publication searches on Li/Mg          |
| `pnge-core:usgs-produced-waters` | Literature on produced-water chemistry pairs with the geochem database |

---

## Caveats and Data Limitations

- **OpenAlex coverage** is strong for post-2000 journal articles, weaker
  for conference papers, technical reports, and theses. For DOE reports
  use `doe-osti`; for USGS series use `usgs-pw`.
- **CrossRef citation counts** (`is-referenced-by-count`) include only
  references deposited by participating publishers via Crossref Cited-by.
  Expect undercounts vs OpenAlex or Google Scholar.
- **USGS Publications Warehouse** indexes journal articles with USGS
  co-authors, but full text may be behind a publisher paywall. USGS
  Numbered Series (FS, SIR, OFR, PP, DS) are always freely downloadable.
- **DOE OSTI** indexes DOE-funded research only. NSF, USDA, DoD, and
  international research are excluded.
- **Date filters broken** on OSTI (HTTP 500 as of 2026). Embed years in
  the keyword query as a workaround.
- **Abstract markup**: OpenAlex uses an inverted index; CrossRef emits
  JATS XML; USGS and OSTI embed HTML. Each adapter strips markup
  differently — `references/adapters.md` documents the rules.
- **DOI coverage**: USGS data releases (`10.5066/*`) and some OSTI
  dataset DOIs (`10.2172/*` data releases) are registered with DataCite,
  not CrossRef. A 404 from CrossRef on these prefixes is expected — use
  `pnge-core:datacite-doi` to resolve them.
- **Author disambiguation**: OpenAlex disambiguates authors (each author
  has a unique `A...` ID); CrossRef does not. For "who has published on
  X" queries, prefer OpenAlex.
- **Open Access flag**: OpenAlex uses Unpaywall data. Some publishers
  declare "is_oa: true" while the hosted PDF is still paywalled — the
  `oa_url` field is the reliable signal.
- **Embargoes**: some OSTI records appear in search before their 12-month
  public-release embargo expires; metadata is visible but fulltext is
  not yet downloadable.

---

## Implementation Notes

- Prefer `bash_tool` with `curl` + `jq` for interactive queries.
- Go client in `references/golang_client.go` for bulk or scripted use.
- Always include `Accept: application/json` for OSTI (otherwise XML).
- Always `curl -sL` for USGS Publications Warehouse (301 redirect on
  the legacy `pubs.er.usgs.gov` host).
- Strip HTML/JATS from titles and abstracts before displaying.
- OpenAlex inverted-index abstract reconstruction: sort word-position
  tuples by position and join with spaces. Expect minor punctuation
  artifacts.
- Normalize DOIs by lowercasing and stripping any `https://doi.org/`
  prefix before de-duplicating.
- For DOI prefix routing, use a single regex:
  `^10\.(3133|2172|5066|\d{4,9})/`
- In `auto` mode, run the chosen adapters in parallel (goroutines or
  `curl &`) and join before dedup.
