---
name: literature-review
description: Conduct a structured academic literature review on a petroleum engineering, geochemistry, or critical minerals topic using the unified pnge-literature skill (OpenAlex, CrossRef, USGS Publications, DOE OSTI). Trigger: /literature-review direct lithium extraction produced water
---

Conduct a structured literature review on: $ARGUMENTS

If no topic is provided, ask the user to specify one.

Use the following skills to gather sources:

1. **pnge:pnge-literature** — unified academic search across OpenAlex
   (peer-reviewed), CrossRef (DOI metadata), USGS Publications Warehouse
   (Fact Sheets, Professional Papers, Open-File Reports), and DOE OSTI
   (national lab technical reports). Auto-routes by query cues and
   de-duplicates by DOI. Use `--source openalex|crossref|usgs-pw|doe-osti`
   to force a single adapter.
2. **pnge:netl-edx** — NETL datasets and research products related to the topic
3. **pnge:datacite-doi** — research-data DOIs (`10.5066` USGS data releases,
   `10.5281` Zenodo, Figshare) that CrossRef does not cover

Structure the output as:

## Literature Review: [TOPIC]

### Key Themes
2–3 paragraph synthesis of main research directions, consensus findings, and open questions.

### Core Publications Table
| Title | Authors | Year | Source | DOI | Key Finding |
|-------|---------|------|--------|-----|-------------|

Sort by relevance. Include at least 8–12 sources if available.

### Research Gaps
Bulleted list of what is not yet well studied.

### Recommended Reading Order
For a student new to the topic, suggest 3–5 papers to read first and why.

### Data Sources Consulted
List each skill invoked and the number of records returned.
