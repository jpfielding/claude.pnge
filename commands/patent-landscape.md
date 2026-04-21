---
name: patent-landscape
description: Generate a DLE patent landscape for a technology class, company, or keyword. Trigger: /patent-landscape sorbent DLE lithium
---

Generate a DLE patent landscape analysis for: $ARGUMENTS

If no technology class, company, or keyword is provided, ask the user to specify
a focus area. Examples:
- Technology: "sorbent DLE", "membrane lithium extraction", "electrochemical DLE"
- Company: "Standard Lithium patents", "Exxon lithium extraction"
- Broad: "direct lithium extraction produced water"

Use the **dle-patent-scout** agent to orchestrate:

1. **pnge:patentsview** — USPTO patent search by CPC class, keyword, and assignee
2. **pnge:pnge-literature** — unified search for academic publications
   by the same inventors or on the same technology (OpenAlex for author
   disambiguation, CrossRef for DOI verification, USGS Publications
   Warehouse, and DOE OSTI for national lab research)
3. **pnge:usgs-minerals** — Li commodity context driving patent activity

Structure the output as:

## DLE Patent Landscape: [FOCUS AREA]

### Search Parameters
Technology class, CPC codes searched, keywords, date range, assignee filters applied.

### Patent Inventory
| Patent No | Title | Assignee | Filed | Granted | CPC | Tech Class |
|-----------|-------|----------|-------|---------|-----|------------|

### Assignee Map
| Assignee | Patent Count | Primary Technology | Earliest | Latest |
|----------|-------------|-------------------|----------|--------|

### Technology Classification
| Technology | Patent Count | Key Assignees | Filing Trend (up/flat/down) |
|------------|-------------|---------------|---------------------------|

### Academic Crossover
Publications by patent inventors or on closely related technology. Cross-reference between patent claims and published research.

### White Space Analysis
Technology gaps, brine sources not well covered, process integration opportunities, and areas where WVU research could contribute novel IP.

### Market Context
Current Li pricing, demand growth, and how market conditions are driving (or suppressing) DLE patent activity.

### Limitations
PatentsView lag, USPTO-only coverage, classification ambiguity.
