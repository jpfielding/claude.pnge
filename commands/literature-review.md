---
name: literature-review
description: Conduct a structured academic literature review on a petroleum engineering, geochemistry, or critical minerals topic using DOE OSTI, USGS Publications, OpenAlex, and CrossRef. Trigger: /literature-review direct lithium extraction produced water
---

Conduct a structured literature review on: $ARGUMENTS

If no topic is provided, ask the user to specify one.

Use the following skills to gather sources:

1. **pnge:doe-osti** — DOE technical reports and national lab publications on the topic
2. **pnge:usgs-pubs** — USGS professional papers, fact sheets, and data series
3. **pnge:openalex** — peer-reviewed journal articles, theses, conference papers (open access)
4. **pnge:netl-edx** — NETL datasets and research products related to the topic
5. **pnge:crossref-doi** — resolve and verify DOIs; retrieve full citation metadata

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
