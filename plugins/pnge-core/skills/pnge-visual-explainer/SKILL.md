---
name: pnge-visual-explainer
description: >
  Generate beautiful, self-contained HTML pages that visually explain petroleum
  engineering concepts, data relationships, and system interactions. Use this
  skill whenever the user asks to visualize, chart, diagram, plot, graph, or
  explain PNGE concepts visually — including reservoir diagrams, DLE process
  flows, production decline curves, Li/Mg concentration charts, well schematics,
  treatment trains, supply chain flows, formation comparisons, or any request
  like "show me", "draw a diagram", "make a chart", "plot this data",
  "visualize the process", "create a figure for my report", or "explain this
  visually". Outputs one portable HTML file per visualization — no server, no
  build step, opens in any browser, print-ready for reports.
---

# PNGE Visual Explainer Skill

Generates self-contained HTML visualizations for petroleum engineering research
and education. Every output is a single `.html` file that works offline, is
shareable, and prints cleanly for inclusion in reports and presentations.

---

## Visualization Types

### 1. Concept Diagrams (SVG)
- Reservoir system diagrams (wellbore, formation, aquifer, cap rock)
- DLE (Direct Lithium Extraction) process flow
- Produced water treatment train (separation, filtration, DLE, reinjection)
- Well completion schematics (casing, perforations, tubing, packer)
- CO2 injection / CCS process (injection well, plume, monitoring)
- Geologic cross-sections (formation layers, faults, aquifer contact)

### 2. Data Visualizations (Chart.js)
- **Time series** — production decline curves, commodity price history, storage levels
- **Bar charts** — Li concentration by formation, production by state, reserves by country
- **Scatter plots** — porosity vs. permeability, Li vs. TDS, depth vs. concentration
- **Histograms** — distribution of Li values across samples, well depth distributions
- **Stacked area** — energy mix over time, production by formation
- **Radar/polar** — multi-attribute formation comparison

### 3. Interactive Explanations (JS)
- Animated process flows (click through DLE steps)
- Tabbed views (compare Marcellus vs. Smackover vs. Bakken)
- Hover tooltips with data details and unit conversions
- Collapsible sections for progressive detail levels
- Toggle between chart views (linear/log scale, absolute/normalized)

### 4. System Interaction Diagrams (SVG + CSS)
- Li supply chain: brine extraction, DLE, refining, battery cathode, EV
- Geopolitical mineral dependency maps
- Data source relationship diagrams (which databases feed which analyses)
- Well-to-market value chain for Li from produced water

---

## Technology Stack

All visualizations use a consistent, proven stack:

| Component | Source | Purpose |
|-----------|--------|---------|
| Chart.js 4.x | `https://cdn.jsdelivr.net/npm/chart.js` | Data charts (line, bar, scatter, etc.) |
| SVG | Inline | Custom diagrams, schematics, process flows |
| CSS Grid/Flexbox | Inline | Responsive layout |
| Vanilla JS | Inline | Interactivity (tabs, tooltips, animations) |
| CSS Variables | Inline | Dark/light theme support |
| Print CSS | Inline `@media print` | Report-ready output |

No build step. No npm. No server. One file, open in browser.

---

## Color Palette — Petroleum Engineering Conventions

```css
:root {
  /* Fluid colors (industry standard) */
  --oil: #2d5016;          /* dark green */
  --oil-light: #4a8c1c;   /* lighter green for fills */
  --gas: #c0392b;          /* red */
  --gas-light: #e74c3c;   /* lighter red */
  --water: #2980b9;        /* blue */
  --water-light: #3498db;  /* lighter blue */

  /* Geology / earth tones */
  --sandstone: #d4a574;    /* warm tan */
  --shale: #7f8c8d;        /* gray */
  --limestone: #bdc3c7;    /* light gray */
  --formation: #8b6914;    /* dark gold */
  --cap-rock: #5d4e37;     /* brown */

  /* Minerals */
  --lithium: #9b59b6;      /* purple — Li convention */
  --magnesium: #1abc9c;    /* teal — Mg */
  --sodium: #f39c12;       /* amber — Na */
  --calcium: #e67e22;      /* orange — Ca */

  /* UI chrome */
  --bg-primary: #0f1419;   /* dark background */
  --bg-secondary: #1a1f25; /* card background */
  --text-primary: #e8eaed; /* primary text */
  --text-muted: #9aa0a6;   /* secondary text */
  --accent: #c8a850;       /* gold accent — petroleum industry */
  --border: #2d333b;       /* subtle borders */

  /* Light theme overrides (toggled via JS) */
  --bg-primary-light: #ffffff;
  --bg-secondary-light: #f8f9fa;
  --text-primary-light: #1a1a2e;
  --text-muted-light: #6c757d;
  --border-light: #dee2e6;
}
```

---

## Workflow

### Step 1 — Understand the Request

Determine what the user wants to visualize:

| User says... | Visualization type | Template |
|--------------|--------------------|----------|
| "chart", "plot", "graph", "trend" | Data chart (Chart.js) | Time series, bar, scatter |
| "diagram", "schematic", "draw" | Concept diagram (SVG) | Well schematic, process flow |
| "compare", "side by side" | Interactive comparison | Tabbed view, grouped bars |
| "explain", "how does X work" | Interactive explainer | Animated flow with steps |
| "flow", "process", "chain" | System diagram (SVG) | Process flow, supply chain |
| "distribution", "histogram" | Statistical chart | Histogram, box plot |

### Step 2 — Gather Data or Define Content

- If the user provides data (CSV, table, inline values): parse and embed directly
- If referencing a PNGE data source: fetch via the appropriate skill first, then visualize
- If explaining a concept: define the components, relationships, and flow steps
- If comparing items: structure as parallel datasets with shared axes

### Step 3 — Select and Populate Template

Choose from the templates in `references/templates.md`. Key decisions:

1. **Chart type** — match data shape to chart type (see table above)
2. **Color mapping** — apply PNGE conventions (oil=green, gas=red, water=blue, Li=purple)
3. **Axis labels and units** — always include units (mg/L, bbl/d, $/ton, ft, psi)
4. **Data density** — if more than 50 data points, consider aggregation or zoom controls
5. **Annotations** — mark significant events (regulation changes, price spikes, discoveries)

### Step 4 — Generate Self-Contained HTML

Build a single HTML file following this structure:

```
<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>[Descriptive Title]</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>  <!-- only if charts used -->
  <style>
    /* CSS variables, layout, theme, print styles */
  </style>
</head>
<body>
  <header>Title + subtitle + theme toggle</header>
  <main>Visualization content</main>
  <footer>Attribution + data source + generation date</footer>
  <script>
    /* Chart initialization, interactivity, theme toggle */
  </script>
</body>
</html>
```

### Step 5 — Save and Report

Save the HTML file to the user's working directory:

```bash
# Default location: current directory
OUTFILE="./pnge-viz-$(date +%Y%m%d-%H%M%S).html"

# Or user-specified name
OUTFILE="./li-concentration-by-formation.html"
```

Report to the user:
1. File path saved
2. How to open: `open $OUTFILE` (macOS) or `xdg-open $OUTFILE` (Linux)
3. Brief description of what the visualization shows
4. Data source attribution

---

## Output Format

Every generated HTML file includes:

### Header Section
- Title describing the visualization
- Subtitle with date range or scope
- Theme toggle button (dark/light)
- Print button

### Main Content
- The visualization itself (chart, diagram, or interactive)
- Legend with PNGE color conventions
- Axis labels with units
- Hover tooltips with precise values

### Footer
- "Generated by PNGE Visual Explainer"
- Data source attribution (e.g., "Data: USGS National Produced Waters DB v3.0")
- Generation timestamp
- Caveats or data quality notes if applicable

### Print Stylesheet
```css
@media print {
  body { background: white; color: black; }
  .no-print { display: none; }    /* hides theme toggle, buttons */
  .chart-container { break-inside: avoid; }
  footer { font-size: 0.8em; }
}
```

---

## Error Handling

| Situation | Action |
|-----------|--------|
| No data provided and no source specified | Ask user: "What data should I visualize? Provide inline data, a CSV path, or tell me which PNGE data skill to query." |
| Data has fewer than 2 points | Warn that a chart may not be meaningful; suggest a table or single-value callout instead |
| CDN unreachable (Chart.js) | Fall back to an inline SVG bar chart or table rendering |
| File write fails | Report the error; offer to output the HTML to stdout instead |
| Data contains mixed units | Normalize to a single unit and note the conversion in the footer |
| Extremely large dataset (1000+ points) | Downsample or aggregate; add note about sampling method |

---

## Template Reference

See `references/templates.md` for complete HTML templates covering:

1. **Time Series Chart** — production curves, price history, storage trends
2. **Bar Chart Comparison** — formation Li concentrations, state production rankings
3. **Process Flow Diagram** — DLE process, treatment train, well lifecycle
4. **Well Schematic** — completion diagram with casing, perforations, zones
5. **Interactive Tabbed View** — formation comparison, scenario analysis
6. **Concept Explainer** — step-by-step animated explanation with callouts

## Python Example

See `references/python_example.py` for a standalone Python (stdlib-only) script
that generates example HTML visualizations demonstrating Chart.js time series,
bar charts, and scatter plots with the PNGE color palette.

---

## Caveats

- **CDN dependency**: Chart.js loads from jsdelivr CDN. If the user is offline,
  provide a note that charts will not render without the library. SVG diagrams
  work fully offline.
- **Browser compatibility**: Tested patterns work in Chrome, Firefox, Safari,
  Edge (all modern versions). IE11 is not supported.
- **Data accuracy**: The skill visualizes data as provided. It does not validate
  scientific accuracy of the data itself. Always attribute the data source.
- **File size**: Most visualizations produce files under 50 KB. Extremely large
  inline datasets (10,000+ points) may produce files over 1 MB — consider
  linking to external data in that case.
- **Accessibility**: Charts include `aria-label` attributes and alt text.
  Color choices maintain WCAG AA contrast ratios against their backgrounds.
