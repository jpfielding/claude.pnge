---
name: patentsview
description: >
  Search U.S. patent data for direct lithium extraction technology, sorbent
  materials, membrane separation, electrochemical extraction, and critical
  mineral recovery patents via the USPTO Open Data Portal. Use when the user
  asks about DLE patents, lithium extraction from brines, ion exchange
  sorbents, lithium manganese oxide, membrane separation for produced water,
  electrochemical lithium recovery, patent landscaping for brine processing,
  DLE patent assignees, CPC classification for lithium recovery, or U.S.
  patent search for mineral processing. Trigger phrases: "DLE patents",
  "lithium extraction patent search", "who patented sorbent technology",
  "patent landscape brine lithium", "CPC class C22B26", "recent patents
  membrane separation", "USPTO search lithium brine". Outputs patent tables
  with titles, dates, assignees, and CPC codes.
---

# PatentsView / USPTO Patent Search Skill

Searches U.S. patent data for technology relevant to direct lithium extraction
(DLE), produced water treatment, membrane separation, and critical mineral
recovery.

---

## Credential

**None required.** The USPTO Open Data Portal is publicly accessible.

```bash
# No API key needed -- USPTO patent data is public domain
```

---

## Data Source

| Field | Value |
|-------|-------|
| Primary source | USPTO Open Data Portal (ODP) |
| Portal URL | https://data.uspto.gov/ |
| Legacy system | PatentsView (patentsview.org) -- migrated to ODP |
| Coverage | All U.S. patents and published applications (1790-present) |
| Update frequency | Weekly (Tuesday patent grants, Thursday applications) |
| Formats | Web search, bulk data downloads (CSV, JSON) |

**Important migration note (as of 2025):** PatentsView has migrated to the
USPTO Open Data Portal at https://data.uspto.gov/. The legacy PatentsView API
at `search.patentsview.org/api/v1/` and `api.patentsview.org` returns
`{"error":true, "message":"PatentsView is migrating to the USPTO Open Data Portal"}`.
Use the ODP web interface or bulk data downloads instead.

**Transition guidance:** https://data.uspto.gov/support/transition-guidance/patentsview

---

## Access Patterns

### USPTO Open Data Portal (Primary)

The ODP at https://data.uspto.gov/ provides a web-based search interface.
As of the migration, programmatic API access should be verified through the
ODP documentation. The portal supports:

- Full-text search across patent titles, abstracts, and claims
- Filtering by CPC/USPC classification, date range, assignee, inventor
- Export of search results

### USPTO Full-Text Search (PatFT / AppFT)

The traditional USPTO full-text search remains available:

```bash
# Search granted patents (PatFT) -- returns HTML, not JSON
# Use for keyword + classification queries
curl -s "https://patft.uspto.gov/netacgi/nph-Parser?Sect1=PTO2&Sect2=HITOFF&u=%2Fnetahtml%2FPTO%2Fsearch-adv.htm&r=0&p=1&f=S&l=50&Query=TTL%2Flithium+AND+ABST%2Fbrine+AND+ISD%2F1%2F1%2F2020-%3E&d=PTXT"
```

### USPTO Bulk Data (Programmatic Access)

For patent landscaping, the bulk data downloads are the most reliable
programmatic option:

```bash
# USPTO bulk data catalog
# https://bulkdata.uspto.gov/
# Weekly XML files of patent grants and applications

# PatentsView bulk data (research datasets, still hosted)
# https://patentsview.org/download/data-download-tables
# Pre-processed CSV/TSV tables: patents, claims, CPC, assignees, inventors
```

### Google Patents (Supplementary)

Google Patents provides a free searchable interface with CPC classification:

```
https://patents.google.com/?q=lithium+extraction+brine&oq=lithium+extraction+brine
```

### Lens.org (Supplementary, API Available)

Lens.org provides a patent search API with free academic access:

```bash
# Lens.org API (requires free API key for academic use)
curl -s "https://api.lens.org/patent/search" \
  -H "Authorization: Bearer $LENS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "query": {"bool": {"must": [
      {"match": {"abstract": "lithium extraction brine"}}
    ]}},
    "size": 10,
    "sort": [{"date_published": "desc"}]
  }'
```

---

## Key CPC Classifications for DLE Research

| CPC Class | Description | Relevance |
|-----------|-------------|-----------|
| C22B26/12 | Obtaining lithium | Core DLE technology patents |
| C01D15/00 | Lithium compounds | Lithium carbonate/hydroxide production |
| C22B3/00 | Extraction of metals by wet processes | Hydrometallurgy (includes brine) |
| C22B3/04 | By leaching | Acid/base leaching of ores and brines |
| B01D61/00 | Processes using semipermeable membranes | Membrane separation (NF, RO, ED) |
| B01D61/42 | Electrodialysis | ED for brine concentration |
| B01J20/00 | Solid sorbent compositions | Ion exchange / adsorption sorbents |
| B01J39/00 | Cation exchangers | Lithium-selective ion exchange |
| C02F1/00 | Treatment of water / wastewater | Produced water treatment |
| C02F1/469 | Electrochemical treatment | Electrochemical Li recovery |
| C25C1/02 | Electrolysis - alkali metals | Electrolytic lithium production |
| E21B43/00 | Methods for obtaining oil/gas/water | Well production methods |

### CPC Query Syntax for USPTO Search

```
# PatFT advanced search syntax:
# CPC/C22B26/12    -- lithium recovery
# CPC/C01D15$      -- lithium compounds ($ = all subclasses)
# CPC/B01D61$      -- membrane processes
# Combine: CPC/C22B26/12 AND ABST/brine
```

---

## Workflow

### Step 1 -- Resolve Intent

| User asks about... | Search strategy |
|---------------------|----------------|
| DLE technology patents | CPC C22B26/12 + keywords "brine" "extraction" |
| Sorbent / adsorbent patents | CPC B01J20 or B01J39 + "lithium" "selective" |
| Membrane separation patents | CPC B01D61 + "lithium" "brine" "produced water" |
| Electrochemical Li recovery | CPC C02F1/469 or C25C1/02 + "lithium" |
| Specific company patents | Assignee name + lithium/DLE keywords |
| Recent patents only | Add date filter ISD/1/1/2023-> |
| Patent landscape overview | Broad CPC search + count by assignee/year |

### Step 2 -- Search Patents

**Option A: USPTO ODP web search (recommended for interactive use):**

Direct the user to https://data.uspto.gov/ with a pre-formed query.

**Option B: Google Patents programmatic (for quick results):**

```bash
# Google Patents search URL (opens in browser, not a REST API)
# Useful for generating a search link for the user
echo "https://patents.google.com/?q=(lithium+extraction+brine+produced+water)&oq=lithium+extraction+brine&type=PATENT&status=GRANT&country=US&after=priority:20200101"
```

**Option C: PatentsView bulk data analysis (for patent landscaping):**

```bash
# Download PatentsView CPC classification table
curl -L -o /tmp/g_cpc_current.tsv.zip \
  "https://s3.amazonaws.com/data.patentsview.org/download/g_cpc_current.tsv.zip"

# After unzipping, filter for lithium CPC classes
zcat /tmp/g_cpc_current.tsv.zip | head -1
# patent_id  cpc_section  cpc_class  cpc_subclass  cpc_group  cpc_subgroup  cpc_category  cpc_sequence

# Count patents in lithium recovery class
zcat /tmp/g_cpc_current.tsv.zip | awk -F'\t' '$5=="C22B26" && $6~/12/' | wc -l
```

### Step 3 -- Parse and Analyze

For patent landscaping, compute:
- Patent count by year (filing date and grant date)
- Top assignees by patent count
- CPC co-classification patterns (what other tech areas appear?)
- Geographic distribution of inventors

### Step 4 -- Produce Output

**Format: Patent Results Table + Landscape Summary**

---

## Output Format

### Example 1: Patent Search Results

```
## U.S. Patents: Direct Lithium Extraction from Brines (CPC C22B26/12)

**Search:** CPC C22B26/12 AND abstract contains "brine"
**Total results:** ~340 granted patents
**Showing:** 10 most recent

| Patent No. | Title | Grant Date | Assignee | Key CPC |
|------------|-------|------------|----------|---------|
| US 11,834,xxx | Method for selective lithium extraction using ... | 2023-12-05 | Lilac Solutions | C22B26/12 |
| US 11,802,xxx | Electrochemical lithium recovery from ... | 2023-10-31 | EnergyX | C22B26/12, C25C1/02 |
| ... | ... | ... | ... | ... |

**Landscape Summary:** DLE patent filings have accelerated sharply since 2018,
with ~120 of 340 total patents filed in 2020-2023. Top assignees include Lilac
Solutions (18 patents), Standard Lithium (12), EnergyX (9), and Schlumberger/SLB
(8). Technology focus areas: lithium manganese oxide sorbents (35%), lithium
titanate sorbents (15%), membrane-based separation (20%), and electrochemical
methods (15%). The remaining 15% cover solvent extraction and hybrid approaches.
```

### Example 2: Technology-Specific Search

```
## Patent Search: Lithium-Selective Ion Exchange Sorbents

**Search:** CPC B01J39 AND "lithium" AND "manganese oxide"
**Results:** ~85 granted patents

| Patent No. | Title | Filing Date | Assignee |
|------------|-------|-------------|----------|
| ... | ... | ... | ... |

**Key finding:** Lithium manganese oxide (LMO) sorbent patents dominate the
selective extraction space. Most patents claim specific Mn:Li ratios, dopants
(Al, Fe, Ti), and granulation methods. Freedom-to-operate analysis should
focus on the specific sorbent composition and regeneration chemistry.
```

---

## Error Handling

| Issue | Cause | Action |
|-------|-------|--------|
| PatentsView API returns migration error | API deprecated, moved to ODP | Use USPTO ODP web search, Google Patents, or bulk data |
| USPTO bulk data download fails | Large file size (GB+) | Download specific tables only (CPC, patent, assignee) |
| Too many results | Broad query | Add CPC class filter or date range |
| Zero results | Overly narrow query | Remove date filter; broaden keywords; check CPC class |
| CPC class not found | Incorrect class notation | Verify at https://www.cooperativepatentclassification.org/ |
| Google Patents rate limiting | Too many automated requests | Space requests; use bulk data for large analyses |

---

## Caveats

1. **PatentsView API is deprecated.** As of 2025, PatentsView has migrated to
   the USPTO Open Data Portal (data.uspto.gov). The legacy API endpoints
   return error messages. Use the ODP web interface, bulk data downloads,
   or supplementary sources (Google Patents, Lens.org).

2. **Patent does not equal commercial product.** Many DLE patents describe
   lab-scale processes that have not been commercialized. Patent claims may
   be broader than actual demonstrated capability.

3. **International coverage.** This skill focuses on U.S. patents (USPTO).
   Major DLE patent activity also exists in China (CNIPA), Australia (IP
   Australia), and via PCT (WIPO). For international coverage, use Lens.org
   or Google Patents (which indexes multiple jurisdictions).

4. **Patent classification lag.** CPC codes are assigned during examination
   and may take 12-18 months after filing to appear. Very recent applications
   may not have full CPC assignments.

5. **Published applications vs. granted patents.** Patent applications
   (published 18 months after filing) represent claimed inventions that may
   not be granted. Distinguish between published applications and granted
   patents in landscape analysis.

6. **Freedom-to-operate is not patent search.** Finding patents in a
   technology area does not constitute a freedom-to-operate analysis. FTO
   requires claim-by-claim analysis by a patent attorney. This skill provides
   landscape awareness, not legal advice.

7. **Bulk data size.** PatentsView bulk data tables can be multiple GB.
   Download only the specific tables needed (CPC, patent, assignee) rather
   than the full dataset.

---

## Implementation Notes

- Primary access is now through the USPTO ODP web interface or bulk data
- For interactive searches, generate a search URL and present to the user
- For patent landscaping, download PatentsView bulk CSV/TSV tables and analyze locally
- Use `jq`, `awk`, or Python for bulk data filtering
- CPC classification browser: https://www.cooperativepatentclassification.org/
- For academic research, Lens.org (https://www.lens.org/) offers a free API with registration
- Combine patent data with `pnge:pnge-literature` for citing literature analysis
