# PNGE Visual Explainer — HTML Templates

Reference templates for generating self-contained HTML visualizations.
Each template is a complete, working HTML file. Copy, customize inline data
and labels, and save.

---

## Shared Base: CSS Variables and Theme Toggle

Every template begins with this shared CSS foundation. Include it in the
`<style>` block of every generated file.

```html
<style>
  /* ===== PNGE Color System ===== */
  :root {
    /* Fluid colors (petroleum industry convention) */
    --oil: #2d5016;
    --oil-light: #4a8c1c;
    --gas: #c0392b;
    --gas-light: #e74c3c;
    --water: #2980b9;
    --water-light: #3498db;

    /* Geology / earth tones */
    --sandstone: #d4a574;
    --shale: #7f8c8d;
    --limestone: #bdc3c7;
    --formation: #8b6914;
    --cap-rock: #5d4e37;

    /* Minerals */
    --lithium: #9b59b6;
    --magnesium: #1abc9c;
    --sodium: #f39c12;
    --calcium: #e67e22;

    /* Chart palette (ordered for multi-series) */
    --chart-1: #3498db;
    --chart-2: #9b59b6;
    --chart-3: #1abc9c;
    --chart-4: #e74c3c;
    --chart-5: #f39c12;
    --chart-6: #2d5016;
    --chart-7: #e67e22;
    --chart-8: #34495e;
  }

  /* ===== Dark Theme (default) ===== */
  [data-theme="dark"] {
    --bg-primary: #0f1419;
    --bg-secondary: #1a1f25;
    --bg-card: #1e2530;
    --text-primary: #e8eaed;
    --text-secondary: #9aa0a6;
    --text-muted: #6b7280;
    --accent: #c8a850;
    --border: #2d333b;
    --shadow: rgba(0, 0, 0, 0.3);
    --grid-line: rgba(255, 255, 255, 0.08);
    --chart-bg: transparent;
  }

  /* ===== Light Theme ===== */
  [data-theme="light"] {
    --bg-primary: #ffffff;
    --bg-secondary: #f8f9fa;
    --bg-card: #ffffff;
    --text-primary: #1a1a2e;
    --text-secondary: #4a5568;
    --text-muted: #9ca3af;
    --accent: #a07c28;
    --border: #dee2e6;
    --shadow: rgba(0, 0, 0, 0.08);
    --grid-line: rgba(0, 0, 0, 0.08);
    --chart-bg: transparent;
  }

  /* ===== Reset and Base ===== */
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

  body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background: var(--bg-primary);
    color: var(--text-primary);
    line-height: 1.6;
    min-height: 100vh;
  }

  /* ===== Layout ===== */
  .container {
    max-width: 1100px;
    margin: 0 auto;
    padding: 2rem 1.5rem;
  }

  header {
    text-align: center;
    margin-bottom: 2rem;
    padding-bottom: 1.5rem;
    border-bottom: 1px solid var(--border);
  }

  header h1 {
    font-size: 1.8rem;
    font-weight: 700;
    color: var(--text-primary);
    margin-bottom: 0.3rem;
  }

  header .subtitle {
    font-size: 1rem;
    color: var(--text-secondary);
  }

  .toolbar {
    display: flex;
    justify-content: flex-end;
    gap: 0.5rem;
    margin-bottom: 1rem;
  }

  .toolbar button {
    background: var(--bg-secondary);
    color: var(--text-secondary);
    border: 1px solid var(--border);
    padding: 0.4rem 0.8rem;
    border-radius: 6px;
    cursor: pointer;
    font-size: 0.85rem;
    transition: all 0.2s;
  }

  .toolbar button:hover {
    background: var(--accent);
    color: #fff;
    border-color: var(--accent);
  }

  /* ===== Chart Container ===== */
  .chart-container {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 2px 8px var(--shadow);
  }

  .chart-container h2 {
    font-size: 1.2rem;
    margin-bottom: 1rem;
    color: var(--text-primary);
  }

  .chart-wrapper {
    position: relative;
    width: 100%;
    max-height: 500px;
  }

  /* ===== Data Table ===== */
  .data-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.9rem;
  }

  .data-table th {
    background: var(--bg-secondary);
    color: var(--text-secondary);
    font-weight: 600;
    text-align: left;
    padding: 0.6rem 0.8rem;
    border-bottom: 2px solid var(--border);
    font-size: 0.8rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  .data-table td {
    padding: 0.5rem 0.8rem;
    border-bottom: 1px solid var(--border);
    color: var(--text-primary);
  }

  .data-table tr:hover td {
    background: var(--bg-secondary);
  }

  /* ===== Callout / Stat Card ===== */
  .stat-row {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
    margin-bottom: 1.5rem;
  }

  .stat-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 1.2rem;
    text-align: center;
  }

  .stat-card .value {
    font-size: 2rem;
    font-weight: 700;
    color: var(--accent);
  }

  .stat-card .label {
    font-size: 0.85rem;
    color: var(--text-secondary);
    margin-top: 0.3rem;
  }

  /* ===== Footer ===== */
  footer {
    margin-top: 2rem;
    padding-top: 1rem;
    border-top: 1px solid var(--border);
    font-size: 0.8rem;
    color: var(--text-muted);
    text-align: center;
  }

  footer a { color: var(--accent); text-decoration: none; }
  footer a:hover { text-decoration: underline; }

  /* ===== Print ===== */
  @media print {
    body { background: #fff; color: #000; }
    .no-print { display: none !important; }
    .chart-container { box-shadow: none; border: 1px solid #ccc; break-inside: avoid; }
    header { border-bottom-color: #ccc; }
    footer { border-top-color: #ccc; color: #666; }
    .stat-card .value { color: #333; }
  }

  /* ===== Responsive ===== */
  @media (max-width: 768px) {
    .container { padding: 1rem; }
    header h1 { font-size: 1.4rem; }
    .stat-row { grid-template-columns: 1fr 1fr; }
  }
</style>
```

### Theme Toggle Script (include at end of every file)

```html
<script>
  function toggleTheme() {
    const html = document.documentElement;
    const current = html.getAttribute('data-theme');
    html.setAttribute('data-theme', current === 'dark' ? 'light' : 'dark');
  }
</script>
```

---

## Template 1: Time Series Chart

Use for: production decline curves, price history, storage levels, any
temporal data.

```html
<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>TITLE — Time Series</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <!-- INSERT shared CSS here -->
</head>
<body>
  <div class="container">
    <header>
      <h1>TITLE</h1>
      <p class="subtitle">SUBTITLE — date range or scope</p>
    </header>

    <div class="toolbar no-print">
      <button onclick="toggleTheme()">Toggle Theme</button>
      <button onclick="window.print()">Print / PDF</button>
    </div>

    <!-- Key stats row -->
    <div class="stat-row">
      <div class="stat-card">
        <div class="value">VALUE</div>
        <div class="label">LABEL (units)</div>
      </div>
      <div class="stat-card">
        <div class="value">VALUE</div>
        <div class="label">LABEL (units)</div>
      </div>
      <div class="stat-card">
        <div class="value">VALUE</div>
        <div class="label">LABEL (units)</div>
      </div>
    </div>

    <!-- Chart -->
    <div class="chart-container">
      <h2>Chart Title (Units)</h2>
      <div class="chart-wrapper">
        <canvas id="timeSeriesChart"></canvas>
      </div>
    </div>

    <footer>
      Generated by PNGE Visual Explainer |
      Data source: SOURCE |
      DATE
    </footer>
  </div>

  <script>
    function toggleTheme() {
      const html = document.documentElement;
      const current = html.getAttribute('data-theme');
      html.setAttribute('data-theme', current === 'dark' ? 'light' : 'dark');
      // Update chart grid colors
      timeSeriesChart.options.scales.x.grid.color = getComputedStyle(document.documentElement).getPropertyValue('--grid-line');
      timeSeriesChart.options.scales.y.grid.color = getComputedStyle(document.documentElement).getPropertyValue('--grid-line');
      timeSeriesChart.options.scales.x.ticks.color = getComputedStyle(document.documentElement).getPropertyValue('--text-secondary');
      timeSeriesChart.options.scales.y.ticks.color = getComputedStyle(document.documentElement).getPropertyValue('--text-secondary');
      timeSeriesChart.update();
    }

    // --- INLINE DATA ---
    const labels = ['2020-01', '2020-02', '2020-03', /* ... */];
    const dataset1 = [100, 95, 91, /* ... */];
    const dataset2 = [80, 77, 74, /* ... */]; // optional second series

    const style = getComputedStyle(document.documentElement);

    const timeSeriesChart = new Chart(document.getElementById('timeSeriesChart'), {
      type: 'line',
      data: {
        labels: labels,
        datasets: [
          {
            label: 'Series 1 (units)',
            data: dataset1,
            borderColor: '#3498db',
            backgroundColor: 'rgba(52, 152, 219, 0.1)',
            fill: true,
            tension: 0.3,
            pointRadius: 2,
            pointHoverRadius: 5,
            borderWidth: 2
          },
          {
            label: 'Series 2 (units)',
            data: dataset2,
            borderColor: '#9b59b6',
            backgroundColor: 'rgba(155, 89, 182, 0.1)',
            fill: true,
            tension: 0.3,
            pointRadius: 2,
            pointHoverRadius: 5,
            borderWidth: 2
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: true,
        interaction: { mode: 'index', intersect: false },
        plugins: {
          legend: {
            labels: { color: style.getPropertyValue('--text-secondary'), font: { size: 12 } }
          },
          tooltip: {
            backgroundColor: 'rgba(0,0,0,0.8)',
            titleFont: { size: 13 },
            bodyFont: { size: 12 },
            padding: 10,
            cornerRadius: 6
          }
        },
        scales: {
          x: {
            grid: { color: style.getPropertyValue('--grid-line') },
            ticks: { color: style.getPropertyValue('--text-secondary'), maxRotation: 45 }
          },
          y: {
            grid: { color: style.getPropertyValue('--grid-line') },
            ticks: { color: style.getPropertyValue('--text-secondary') },
            title: { display: true, text: 'Y-Axis Label (units)', color: style.getPropertyValue('--text-secondary') }
          }
        }
      }
    });
  </script>
</body>
</html>
```

---

## Template 2: Bar Chart Comparison

Use for: Li concentration by formation, production by state, reserves by
country, any categorical comparison.

```html
<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>TITLE — Bar Comparison</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <!-- INSERT shared CSS here -->
</head>
<body>
  <div class="container">
    <header>
      <h1>TITLE</h1>
      <p class="subtitle">SUBTITLE</p>
    </header>

    <div class="toolbar no-print">
      <button onclick="toggleTheme()">Toggle Theme</button>
      <button onclick="window.print()">Print / PDF</button>
    </div>

    <div class="chart-container">
      <h2>Chart Title</h2>
      <div class="chart-wrapper">
        <canvas id="barChart"></canvas>
      </div>
    </div>

    <!-- Optional data table below chart -->
    <div class="chart-container">
      <h2>Data Summary</h2>
      <table class="data-table">
        <thead>
          <tr>
            <th>Category</th>
            <th>Value 1</th>
            <th>Value 2</th>
          </tr>
        </thead>
        <tbody>
          <!-- Rows populated by JS or inline -->
          <tr><td>Item A</td><td>123</td><td>456</td></tr>
        </tbody>
      </table>
    </div>

    <footer>
      Generated by PNGE Visual Explainer |
      Data source: SOURCE |
      DATE
    </footer>
  </div>

  <script>
    function toggleTheme() {
      const html = document.documentElement;
      html.setAttribute('data-theme',
        html.getAttribute('data-theme') === 'dark' ? 'light' : 'dark');
    }

    // --- INLINE DATA ---
    const categories = ['Smackover', 'Marcellus', 'Utica', 'Bakken', 'Permian'];
    const values = [477, 200, 150, 70, 45];

    // Color bars by value intensity (Li purple gradient)
    const maxVal = Math.max(...values);
    const barColors = values.map(v => {
      const intensity = 0.3 + 0.7 * (v / maxVal);
      return `rgba(155, 89, 182, ${intensity})`;
    });

    new Chart(document.getElementById('barChart'), {
      type: 'bar',
      data: {
        labels: categories,
        datasets: [{
          label: 'Li Concentration (mg/L)',
          data: values,
          backgroundColor: barColors,
          borderColor: '#9b59b6',
          borderWidth: 1,
          borderRadius: 4
        }]
      },
      options: {
        responsive: true,
        indexAxis: 'y', // horizontal bars — good for long category names
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: function(ctx) {
                return `${ctx.parsed.x} mg/L`;
              }
            }
          }
        },
        scales: {
          x: {
            grid: { color: 'rgba(255,255,255,0.08)' },
            ticks: { color: '#9aa0a6' },
            title: { display: true, text: 'Concentration (mg/L)', color: '#9aa0a6' }
          },
          y: {
            grid: { display: false },
            ticks: { color: '#e8eaed', font: { size: 13 } }
          }
        }
      }
    });
  </script>
</body>
</html>
```

---

## Template 3: Process Flow Diagram (SVG)

Use for: DLE process flow, produced water treatment train, well lifecycle,
CO2 injection process.

```html
<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>TITLE — Process Flow</title>
  <!-- INSERT shared CSS here -->
  <style>
    /* Process flow specific styles */
    .flow-container {
      overflow-x: auto;
      padding: 1rem 0;
    }

    .flow-svg {
      display: block;
      margin: 0 auto;
    }

    .flow-step {
      cursor: pointer;
      transition: transform 0.2s, filter 0.2s;
    }

    .flow-step:hover {
      filter: brightness(1.2);
    }

    .flow-step.active rect,
    .flow-step.active ellipse {
      stroke-width: 3;
      stroke: var(--accent);
    }

    .step-detail {
      background: var(--bg-card);
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 1.2rem;
      margin-top: 1rem;
      display: none;
    }

    .step-detail.visible {
      display: block;
    }

    .step-detail h3 {
      color: var(--accent);
      margin-bottom: 0.5rem;
    }

    .step-detail p {
      color: var(--text-secondary);
      line-height: 1.6;
    }
  </style>
</head>
<body>
  <div class="container">
    <header>
      <h1>Direct Lithium Extraction (DLE) Process Flow</h1>
      <p class="subtitle">Click each step to see details</p>
    </header>

    <div class="toolbar no-print">
      <button onclick="toggleTheme()">Toggle Theme</button>
      <button onclick="window.print()">Print / PDF</button>
    </div>

    <div class="chart-container">
      <div class="flow-container">
        <svg class="flow-svg" viewBox="0 0 900 200" xmlns="http://www.w3.org/2000/svg"
             aria-label="DLE Process Flow Diagram">

          <!-- Step 1: Produced Water -->
          <g class="flow-step" data-step="1" onclick="showStep(1)">
            <rect x="10" y="60" width="140" height="80" rx="10"
                  fill="#2980b9" stroke="#3498db" stroke-width="2" />
            <text x="80" y="95" text-anchor="middle" fill="#fff"
                  font-size="13" font-weight="600">Produced</text>
            <text x="80" y="115" text-anchor="middle" fill="#fff"
                  font-size="13" font-weight="600">Water</text>
          </g>

          <!-- Arrow 1-2 -->
          <line x1="150" y1="100" x2="190" y2="100"
                stroke="#c8a850" stroke-width="2" marker-end="url(#arrow)" />

          <!-- Step 2: Pre-Treatment -->
          <g class="flow-step" data-step="2" onclick="showStep(2)">
            <rect x="190" y="60" width="140" height="80" rx="10"
                  fill="#7f8c8d" stroke="#95a5a6" stroke-width="2" />
            <text x="260" y="95" text-anchor="middle" fill="#fff"
                  font-size="13" font-weight="600">Pre-Treatment</text>
            <text x="260" y="115" text-anchor="middle" fill="#fff"
                  font-size="11">(Filtration, pH)</text>
          </g>

          <!-- Arrow 2-3 -->
          <line x1="330" y1="100" x2="370" y2="100"
                stroke="#c8a850" stroke-width="2" marker-end="url(#arrow)" />

          <!-- Step 3: DLE Unit -->
          <g class="flow-step" data-step="3" onclick="showStep(3)">
            <rect x="370" y="50" width="160" height="100" rx="12"
                  fill="#9b59b6" stroke="#a86cc1" stroke-width="2.5" />
            <text x="450" y="90" text-anchor="middle" fill="#fff"
                  font-size="14" font-weight="700">DLE Unit</text>
            <text x="450" y="112" text-anchor="middle" fill="#ddd"
                  font-size="11">(Adsorption / Ion Exchange)</text>
          </g>

          <!-- Arrow 3-4 -->
          <line x1="530" y1="100" x2="570" y2="100"
                stroke="#c8a850" stroke-width="2" marker-end="url(#arrow)" />

          <!-- Step 4: Concentration -->
          <g class="flow-step" data-step="4" onclick="showStep(4)">
            <rect x="570" y="60" width="140" height="80" rx="10"
                  fill="#1abc9c" stroke="#16a085" stroke-width="2" />
            <text x="640" y="95" text-anchor="middle" fill="#fff"
                  font-size="13" font-weight="600">Concentration</text>
            <text x="640" y="115" text-anchor="middle" fill="#fff"
                  font-size="11">(Evaporation)</text>
          </g>

          <!-- Arrow 4-5 -->
          <line x1="710" y1="100" x2="750" y2="100"
                stroke="#c8a850" stroke-width="2" marker-end="url(#arrow)" />

          <!-- Step 5: Li Product -->
          <g class="flow-step" data-step="5" onclick="showStep(5)">
            <rect x="750" y="60" width="140" height="80" rx="10"
                  fill="#c8a850" stroke="#d4b96a" stroke-width="2" />
            <text x="820" y="90" text-anchor="middle" fill="#1a1a2e"
                  font-size="13" font-weight="700">Li2CO3 /</text>
            <text x="820" y="110" text-anchor="middle" fill="#1a1a2e"
                  font-size="13" font-weight="700">LiOH</text>
          </g>

          <!-- Arrow marker definition -->
          <defs>
            <marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5"
                    markerWidth="8" markerHeight="8" orient="auto-start-auto">
              <path d="M 0 0 L 10 5 L 0 10 z" fill="#c8a850" />
            </marker>
          </defs>
        </svg>
      </div>

      <!-- Step detail panels -->
      <div id="detail-1" class="step-detail">
        <h3>Step 1: Produced Water Intake</h3>
        <p>Raw produced water from oil/gas operations, typically containing 1,000-300,000 mg/L TDS.
        Key Li-bearing formations: Smackover (up to 477 mg/L Li), Marcellus (10-200 mg/L),
        Utica/Point Pleasant (20-150 mg/L). Water arrives at surface temperature and pressure.</p>
      </div>
      <div id="detail-2" class="step-detail">
        <h3>Step 2: Pre-Treatment</h3>
        <p>Remove suspended solids, adjust pH, and reduce interfering ions (Fe, Mn, Ca, Mg).
        Methods: coagulation/flocculation, media filtration, softening. Target: clear feed
        that won't foul the DLE sorbent/membrane. Mg removal is critical as it competes
        with Li in most DLE processes.</p>
      </div>
      <div id="detail-3" class="step-detail">
        <h3>Step 3: Direct Lithium Extraction</h3>
        <p>Selective extraction of Li from the brine using adsorption (LiMnO sorbent),
        ion exchange, or solvent extraction. DLE achieves 80-95% Li recovery from brines
        with Li:Mg ratios as low as 1:100. Key advantage over evaporation ponds:
        hours vs. months, works in any climate, smaller footprint.</p>
      </div>
      <div id="detail-4" class="step-detail">
        <h3>Step 4: Concentration</h3>
        <p>The dilute Li eluate (500-5,000 mg/L Li) is concentrated via reverse osmosis
        or mechanical vapor recompression to reach precipitation-ready concentrations
        (20,000-40,000 mg/L Li). Energy is the primary cost driver at this stage.</p>
      </div>
      <div id="detail-5" class="step-detail">
        <h3>Step 5: Lithium Product</h3>
        <p>Precipitation of battery-grade lithium carbonate (Li2CO3, 99.5%+) or
        lithium hydroxide monohydrate (LiOH-H2O). Product choice depends on
        cathode chemistry: LFP uses Li2CO3, NMC/NCA uses LiOH. Current pricing:
        ~$10,000-15,000/ton Li2CO3 equivalent.</p>
      </div>
    </div>

    <footer>
      Generated by PNGE Visual Explainer |
      Reference: USGS National Produced Waters DB v3.0 |
      DATE
    </footer>
  </div>

  <script>
    function toggleTheme() {
      const html = document.documentElement;
      html.setAttribute('data-theme',
        html.getAttribute('data-theme') === 'dark' ? 'light' : 'dark');
    }

    function showStep(n) {
      document.querySelectorAll('.step-detail').forEach(d => d.classList.remove('visible'));
      document.querySelectorAll('.flow-step').forEach(s => s.classList.remove('active'));
      document.getElementById('detail-' + n).classList.add('visible');
      document.querySelector('[data-step="' + n + '"]').classList.add('active');
    }
  </script>
</body>
</html>
```

---

## Template 4: Well Schematic (SVG)

Use for: well completion diagrams, casing programs, perforation intervals.

```html
<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Well Completion Schematic</title>
  <!-- INSERT shared CSS here -->
  <style>
    .schematic-wrapper {
      display: flex;
      gap: 2rem;
      align-items: flex-start;
    }
    .schematic-svg { flex: 0 0 300px; }
    .schematic-legend { flex: 1; }
    .legend-item {
      display: flex;
      align-items: center;
      gap: 0.8rem;
      padding: 0.6rem 0;
      border-bottom: 1px solid var(--border);
    }
    .legend-swatch {
      width: 24px;
      height: 24px;
      border-radius: 4px;
      flex-shrink: 0;
    }
    .legend-label { font-weight: 600; color: var(--text-primary); }
    .legend-desc { font-size: 0.85rem; color: var(--text-secondary); }

    @media (max-width: 768px) {
      .schematic-wrapper { flex-direction: column; }
      .schematic-svg { flex: none; width: 100%; max-width: 300px; margin: 0 auto; }
    }
  </style>
</head>
<body>
  <div class="container">
    <header>
      <h1>Well Completion Schematic</h1>
      <p class="subtitle">Marcellus Shale Horizontal Well — Monongalia County, WV</p>
    </header>

    <div class="toolbar no-print">
      <button onclick="toggleTheme()">Toggle Theme</button>
      <button onclick="window.print()">Print / PDF</button>
    </div>

    <div class="chart-container">
      <div class="schematic-wrapper">
        <svg class="schematic-svg" viewBox="0 0 260 600" xmlns="http://www.w3.org/2000/svg"
             aria-label="Well completion schematic showing casing, tubing, and formations">

          <!-- Surface -->
          <rect x="0" y="0" width="260" height="30" fill="#5d4e37" />
          <text x="130" y="20" text-anchor="middle" fill="#fff" font-size="11">Surface</text>

          <!-- Conductor casing -->
          <rect x="70" y="30" width="120" height="60" fill="none"
                stroke="#95a5a6" stroke-width="4" />
          <text x="200" y="65" fill="#95a5a6" font-size="9">20" Conductor</text>

          <!-- Surface casing -->
          <rect x="80" y="30" width="100" height="150" fill="none"
                stroke="#3498db" stroke-width="3" />
          <text x="200" y="110" fill="#3498db" font-size="9">13-3/8" Surface</text>

          <!-- Formation layers -->
          <rect x="0" y="90" width="70" height="80" fill="#d4a574" opacity="0.6" />
          <text x="35" y="135" text-anchor="middle" fill="#fff" font-size="9">Sandstone</text>

          <rect x="0" y="170" width="70" height="80" fill="#bdc3c7" opacity="0.6" />
          <text x="35" y="215" text-anchor="middle" fill="#333" font-size="9">Limestone</text>

          <!-- Intermediate casing -->
          <rect x="90" y="30" width="80" height="300" fill="none"
                stroke="#2ecc71" stroke-width="3" />
          <text x="200" y="200" fill="#2ecc71" font-size="9">9-5/8" Intermediate</text>

          <!-- Shale target -->
          <rect x="0" y="250" width="70" height="100" fill="#7f8c8d" opacity="0.8" />
          <text x="35" y="305" text-anchor="middle" fill="#fff" font-size="9">Marcellus</text>
          <text x="35" y="318" text-anchor="middle" fill="#ddd" font-size="8">Shale</text>

          <!-- Production casing -->
          <rect x="100" y="30" width="60" height="400" fill="none"
                stroke="#e74c3c" stroke-width="2.5" />
          <text x="200" y="340" fill="#e74c3c" font-size="9">5-1/2" Production</text>

          <!-- Horizontal section -->
          <path d="M 130 400 Q 130 450, 180 460 L 260 460"
                fill="none" stroke="#e74c3c" stroke-width="2.5" />

          <!-- Perforations (frac stages) -->
          <g fill="#f39c12">
            <rect x="190" y="455" width="3" height="10" />
            <rect x="193" y="452" width="3" height="16" />
            <rect x="210" y="455" width="3" height="10" />
            <rect x="213" y="452" width="3" height="16" />
            <rect x="230" y="455" width="3" height="10" />
            <rect x="233" y="452" width="3" height="16" />
            <rect x="250" y="455" width="3" height="10" />
            <rect x="253" y="452" width="3" height="16" />
          </g>
          <text x="225" y="490" text-anchor="middle" fill="#f39c12" font-size="9">Frac Stages</text>

          <!-- Tubing -->
          <line x1="125" y1="35" x2="125" y2="395" stroke="#c8a850" stroke-width="2" />
          <line x1="135" y1="35" x2="135" y2="395" stroke="#c8a850" stroke-width="2" />
          <text x="200" y="55" fill="#c8a850" font-size="9">Tubing</text>

          <!-- Packer -->
          <rect x="100" y="370" width="60" height="10" fill="#c8a850" rx="2" />
          <text x="200" y="380" fill="#c8a850" font-size="9">Packer</text>

          <!-- Depth labels -->
          <text x="10" y="95" fill="#aaa" font-size="8">500'</text>
          <text x="10" y="175" fill="#aaa" font-size="8">2,000'</text>
          <text x="10" y="255" fill="#aaa" font-size="8">5,500'</text>
          <text x="10" y="355" fill="#aaa" font-size="8">7,500'</text>
        </svg>

        <div class="schematic-legend">
          <h2>Components</h2>
          <div class="legend-item">
            <div class="legend-swatch" style="background: #95a5a6"></div>
            <div>
              <div class="legend-label">Conductor Casing (20")</div>
              <div class="legend-desc">Set to ~60 ft. Prevents surface collapse.</div>
            </div>
          </div>
          <div class="legend-item">
            <div class="legend-swatch" style="background: #3498db"></div>
            <div>
              <div class="legend-label">Surface Casing (13-3/8")</div>
              <div class="legend-desc">Set to ~500 ft. Protects fresh water aquifers. Cemented to surface.</div>
            </div>
          </div>
          <div class="legend-item">
            <div class="legend-swatch" style="background: #2ecc71"></div>
            <div>
              <div class="legend-label">Intermediate Casing (9-5/8")</div>
              <div class="legend-desc">Set to ~5,500 ft. Isolates problem zones and overpressured intervals.</div>
            </div>
          </div>
          <div class="legend-item">
            <div class="legend-swatch" style="background: #e74c3c"></div>
            <div>
              <div class="legend-label">Production Casing (5-1/2")</div>
              <div class="legend-desc">Set through horizontal lateral. Cemented across target formation.</div>
            </div>
          </div>
          <div class="legend-item">
            <div class="legend-swatch" style="background: #c8a850"></div>
            <div>
              <div class="legend-label">Production Tubing + Packer</div>
              <div class="legend-desc">Tubing string sealed at packer. Production flows up tubing annulus.</div>
            </div>
          </div>
          <div class="legend-item">
            <div class="legend-swatch" style="background: #f39c12"></div>
            <div>
              <div class="legend-label">Frac Stages (Perforations)</div>
              <div class="legend-desc">Plug-and-perf completion. 20-40 stages typical for Marcellus horizontal.</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <footer>
      Generated by PNGE Visual Explainer |
      Reference: WV Geological Survey Well Data |
      DATE
    </footer>
  </div>

  <script>
    function toggleTheme() {
      const html = document.documentElement;
      html.setAttribute('data-theme',
        html.getAttribute('data-theme') === 'dark' ? 'light' : 'dark');
    }
  </script>
</body>
</html>
```

---

## Template 5: Interactive Tabbed View

Use for: comparing formations, scenarios, or multi-entity data side by side.

```html
<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>TITLE — Comparison</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <!-- INSERT shared CSS here -->
  <style>
    .tabs {
      display: flex;
      gap: 0;
      border-bottom: 2px solid var(--border);
      margin-bottom: 1.5rem;
    }
    .tab-btn {
      background: none;
      border: none;
      padding: 0.8rem 1.5rem;
      color: var(--text-secondary);
      font-size: 0.95rem;
      font-weight: 500;
      cursor: pointer;
      border-bottom: 3px solid transparent;
      margin-bottom: -2px;
      transition: all 0.2s;
    }
    .tab-btn:hover { color: var(--text-primary); }
    .tab-btn.active {
      color: var(--accent);
      border-bottom-color: var(--accent);
      font-weight: 600;
    }
    .tab-panel { display: none; }
    .tab-panel.active { display: block; }

    .prop-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 0.8rem;
    }
    .prop-item {
      background: var(--bg-secondary);
      padding: 0.8rem;
      border-radius: 8px;
      border: 1px solid var(--border);
    }
    .prop-item .prop-label {
      font-size: 0.8rem;
      color: var(--text-muted);
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }
    .prop-item .prop-value {
      font-size: 1.3rem;
      font-weight: 600;
      color: var(--text-primary);
      margin-top: 0.2rem;
    }
  </style>
</head>
<body>
  <div class="container">
    <header>
      <h1>Formation Comparison: Li-Bearing Brines</h1>
      <p class="subtitle">Key U.S. formations for lithium from produced water</p>
    </header>

    <div class="toolbar no-print">
      <button onclick="toggleTheme()">Toggle Theme</button>
      <button onclick="window.print()">Print / PDF</button>
    </div>

    <div class="chart-container">
      <div class="tabs no-print">
        <button class="tab-btn active" onclick="switchTab('smackover')">Smackover</button>
        <button class="tab-btn" onclick="switchTab('marcellus')">Marcellus</button>
        <button class="tab-btn" onclick="switchTab('utica')">Utica</button>
        <button class="tab-btn" onclick="switchTab('bakken')">Bakken</button>
      </div>

      <div id="tab-smackover" class="tab-panel active">
        <div class="stat-row">
          <div class="stat-card">
            <div class="value" style="color: #9b59b6">477</div>
            <div class="label">Max Li (mg/L)</div>
          </div>
          <div class="stat-card">
            <div class="value">AR, TX, LA</div>
            <div class="label">States</div>
          </div>
        </div>
        <div class="prop-grid">
          <div class="prop-item">
            <div class="prop-label">Depth Range</div>
            <div class="prop-value">8,000-12,000 ft</div>
          </div>
          <div class="prop-item">
            <div class="prop-label">TDS Range</div>
            <div class="prop-value">200,000-300,000 mg/L</div>
          </div>
          <div class="prop-item">
            <div class="prop-label">Li Range</div>
            <div class="prop-value">50-477 mg/L</div>
          </div>
          <div class="prop-item">
            <div class="prop-label">DLE Viability</div>
            <div class="prop-value" style="color: #2ecc71">Excellent</div>
          </div>
        </div>
      </div>

      <!-- Additional tab panels follow same structure -->
      <div id="tab-marcellus" class="tab-panel">
        <div class="stat-row">
          <div class="stat-card">
            <div class="value" style="color: #9b59b6">200+</div>
            <div class="label">Max Li (mg/L)</div>
          </div>
          <div class="stat-card">
            <div class="value">WV, PA, OH</div>
            <div class="label">States</div>
          </div>
        </div>
        <div class="prop-grid">
          <div class="prop-item">
            <div class="prop-label">Depth Range</div>
            <div class="prop-value">5,000-9,000 ft</div>
          </div>
          <div class="prop-item">
            <div class="prop-label">TDS Range</div>
            <div class="prop-value">100,000-300,000 mg/L</div>
          </div>
          <div class="prop-item">
            <div class="prop-label">Li Range</div>
            <div class="prop-value">10-200+ mg/L</div>
          </div>
          <div class="prop-item">
            <div class="prop-label">DLE Viability</div>
            <div class="prop-value" style="color: #2ecc71">Good (high volume)</div>
          </div>
        </div>
      </div>

      <div id="tab-utica" class="tab-panel">
        <div class="stat-row">
          <div class="stat-card">
            <div class="value" style="color: #9b59b6">150</div>
            <div class="label">Max Li (mg/L)</div>
          </div>
          <div class="stat-card">
            <div class="value">OH, WV, PA</div>
            <div class="label">States</div>
          </div>
        </div>
        <div class="prop-grid">
          <div class="prop-item">
            <div class="prop-label">Depth Range</div>
            <div class="prop-value">6,000-12,000 ft</div>
          </div>
          <div class="prop-item">
            <div class="prop-label">TDS Range</div>
            <div class="prop-value">150,000-350,000 mg/L</div>
          </div>
          <div class="prop-item">
            <div class="prop-label">Li Range</div>
            <div class="prop-value">20-150 mg/L</div>
          </div>
          <div class="prop-item">
            <div class="prop-label">DLE Viability</div>
            <div class="prop-value" style="color: #f39c12">Moderate</div>
          </div>
        </div>
      </div>

      <div id="tab-bakken" class="tab-panel">
        <div class="stat-row">
          <div class="stat-card">
            <div class="value" style="color: #9b59b6">70</div>
            <div class="label">Max Li (mg/L)</div>
          </div>
          <div class="stat-card">
            <div class="value">ND, MT</div>
            <div class="label">States</div>
          </div>
        </div>
        <div class="prop-grid">
          <div class="prop-item">
            <div class="prop-label">Depth Range</div>
            <div class="prop-value">9,000-11,000 ft</div>
          </div>
          <div class="prop-item">
            <div class="prop-label">TDS Range</div>
            <div class="prop-value">200,000-350,000 mg/L</div>
          </div>
          <div class="prop-item">
            <div class="prop-label">Li Range</div>
            <div class="prop-value">10-70 mg/L</div>
          </div>
          <div class="prop-item">
            <div class="prop-label">DLE Viability</div>
            <div class="prop-value" style="color: #e74c3c">Below economic threshold</div>
          </div>
        </div>
      </div>
    </div>

    <footer>
      Generated by PNGE Visual Explainer |
      Data: USGS National Produced Waters Geochemical DB v3.0 |
      DATE
    </footer>
  </div>

  <script>
    function toggleTheme() {
      const html = document.documentElement;
      html.setAttribute('data-theme',
        html.getAttribute('data-theme') === 'dark' ? 'light' : 'dark');
    }

    function switchTab(name) {
      document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
      document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
      document.getElementById('tab-' + name).classList.add('active');
      event.target.classList.add('active');
    }
  </script>
</body>
</html>
```

---

## Template 6: Concept Explainer with Animations

Use for: step-by-step educational explanations of PNGE concepts with
animated progression.

```html
<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>TITLE — Concept Explainer</title>
  <!-- INSERT shared CSS here -->
  <style>
    .explainer-steps {
      display: flex;
      flex-direction: column;
      gap: 1.5rem;
    }

    .step {
      display: grid;
      grid-template-columns: 60px 1fr;
      gap: 1rem;
      opacity: 0.4;
      transform: translateY(10px);
      transition: all 0.4s ease;
    }

    .step.revealed {
      opacity: 1;
      transform: translateY(0);
    }

    .step-number {
      width: 48px;
      height: 48px;
      border-radius: 50%;
      background: var(--bg-secondary);
      border: 2px solid var(--border);
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 700;
      font-size: 1.2rem;
      color: var(--text-muted);
      transition: all 0.3s;
    }

    .step.revealed .step-number {
      background: var(--accent);
      border-color: var(--accent);
      color: #1a1a2e;
    }

    .step-content {
      background: var(--bg-card);
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 1.2rem;
    }

    .step-content h3 {
      font-size: 1.1rem;
      margin-bottom: 0.5rem;
      color: var(--text-primary);
    }

    .step-content p {
      color: var(--text-secondary);
      line-height: 1.7;
    }

    .step-content .key-values {
      display: flex;
      gap: 1rem;
      margin-top: 0.8rem;
      flex-wrap: wrap;
    }

    .key-value {
      background: var(--bg-secondary);
      padding: 0.4rem 0.8rem;
      border-radius: 6px;
      font-size: 0.85rem;
    }

    .key-value .kv-label { color: var(--text-muted); }
    .key-value .kv-val { color: var(--accent); font-weight: 600; }

    .controls {
      display: flex;
      justify-content: center;
      gap: 1rem;
      margin-top: 1.5rem;
    }

    .controls button {
      background: var(--accent);
      color: #1a1a2e;
      border: none;
      padding: 0.6rem 1.5rem;
      border-radius: 8px;
      font-weight: 600;
      cursor: pointer;
      font-size: 0.95rem;
      transition: opacity 0.2s;
    }

    .controls button:hover { opacity: 0.85; }
    .controls button:disabled { opacity: 0.3; cursor: not-allowed; }

    .progress-bar {
      width: 100%;
      height: 4px;
      background: var(--border);
      border-radius: 2px;
      margin-top: 1rem;
      overflow: hidden;
    }

    .progress-fill {
      height: 100%;
      background: var(--accent);
      transition: width 0.4s ease;
      border-radius: 2px;
    }
  </style>
</head>
<body>
  <div class="container">
    <header>
      <h1>How Direct Lithium Extraction Works</h1>
      <p class="subtitle">A step-by-step guide to recovering lithium from produced water</p>
    </header>

    <div class="toolbar no-print">
      <button onclick="toggleTheme()">Toggle Theme</button>
      <button onclick="window.print()">Print / PDF</button>
    </div>

    <div class="chart-container">
      <div class="progress-bar no-print">
        <div class="progress-fill" id="progressFill" style="width: 0%"></div>
      </div>

      <div class="explainer-steps" id="steps">
        <div class="step" data-step="1">
          <div class="step-number">1</div>
          <div class="step-content">
            <h3>Brine Source Identification</h3>
            <p>Identify produced water streams with economically viable lithium
            concentrations. The economic threshold for DLE is approximately
            100-150 mg/L Li, though this depends on brine volume and co-product value.</p>
            <div class="key-values">
              <div class="key-value">
                <span class="kv-label">Threshold: </span>
                <span class="kv-val">100-150 mg/L</span>
              </div>
              <div class="key-value">
                <span class="kv-label">Best U.S. source: </span>
                <span class="kv-val">Smackover (477 mg/L)</span>
              </div>
            </div>
          </div>
        </div>

        <div class="step" data-step="2">
          <div class="step-number">2</div>
          <div class="step-content">
            <h3>Pre-Treatment and Conditioning</h3>
            <p>Remove suspended solids, iron, manganese, and scale-forming ions.
            Adjust pH to the optimal range for the chosen DLE sorbent (typically pH 5-7).
            Critical: reduce Mg/Li ratio to improve selectivity.</p>
            <div class="key-values">
              <div class="key-value">
                <span class="kv-label">Target pH: </span>
                <span class="kv-val">5.0-7.0</span>
              </div>
              <div class="key-value">
                <span class="kv-label">TSS target: </span>
                <span class="kv-val">below 5 mg/L</span>
              </div>
            </div>
          </div>
        </div>

        <div class="step" data-step="3">
          <div class="step-number">3</div>
          <div class="step-content">
            <h3>Selective Lithium Extraction</h3>
            <p>Pass conditioned brine through DLE columns containing lithium-selective
            sorbent (typically lithium manganese oxide, Li-Al LDH, or lithium titanate).
            Li is adsorbed while Na, K, Ca, Mg pass through. The loaded sorbent is then
            washed with fresh water or dilute acid to release a concentrated Li eluate.</p>
            <div class="key-values">
              <div class="key-value">
                <span class="kv-label">Recovery: </span>
                <span class="kv-val">80-95%</span>
              </div>
              <div class="key-value">
                <span class="kv-label">Cycle time: </span>
                <span class="kv-val">2-6 hours</span>
              </div>
            </div>
          </div>
        </div>

        <div class="step" data-step="4">
          <div class="step-number">4</div>
          <div class="step-content">
            <h3>Concentration and Purification</h3>
            <p>The dilute Li eluate is concentrated using reverse osmosis, nanofiltration,
            or evaporation to reach precipitation-ready levels. Polishing steps remove
            trace contaminants (boron, silica) to meet battery-grade specifications.</p>
            <div class="key-values">
              <div class="key-value">
                <span class="kv-label">Input Li: </span>
                <span class="kv-val">500-5,000 mg/L</span>
              </div>
              <div class="key-value">
                <span class="kv-label">Output Li: </span>
                <span class="kv-val">20,000-40,000 mg/L</span>
              </div>
            </div>
          </div>
        </div>

        <div class="step" data-step="5">
          <div class="step-number">5</div>
          <div class="step-content">
            <h3>Product Precipitation</h3>
            <p>Add soda ash (Na2CO3) to precipitate lithium carbonate, or use NaOH
            for lithium hydroxide. Filter, wash, dry, and package. Battery-grade
            requires 99.5%+ purity with strict limits on Na, K, Ca, Fe, and Si.</p>
            <div class="key-values">
              <div class="key-value">
                <span class="kv-label">Li2CO3 purity: </span>
                <span class="kv-val">99.5%+</span>
              </div>
              <div class="key-value">
                <span class="kv-label">Price (2024): </span>
                <span class="kv-val">~$12,000/ton LCE</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="controls no-print">
        <button id="prevBtn" onclick="prevStep()" disabled>Previous</button>
        <button id="nextBtn" onclick="nextStep()">Next Step</button>
        <button onclick="revealAll()">Show All</button>
      </div>
    </div>

    <footer>
      Generated by PNGE Visual Explainer |
      DATE
    </footer>
  </div>

  <script>
    function toggleTheme() {
      const html = document.documentElement;
      html.setAttribute('data-theme',
        html.getAttribute('data-theme') === 'dark' ? 'light' : 'dark');
    }

    let currentStep = 0;
    const totalSteps = document.querySelectorAll('.step').length;

    function updateProgress() {
      const pct = (currentStep / totalSteps) * 100;
      document.getElementById('progressFill').style.width = pct + '%';
      document.getElementById('prevBtn').disabled = currentStep === 0;
      document.getElementById('nextBtn').disabled = currentStep >= totalSteps;
    }

    function nextStep() {
      if (currentStep < totalSteps) {
        currentStep++;
        document.querySelector('[data-step="' + currentStep + '"]').classList.add('revealed');
        updateProgress();
      }
    }

    function prevStep() {
      if (currentStep > 0) {
        document.querySelector('[data-step="' + currentStep + '"]').classList.remove('revealed');
        currentStep--;
        updateProgress();
      }
    }

    function revealAll() {
      document.querySelectorAll('.step').forEach(s => s.classList.add('revealed'));
      currentStep = totalSteps;
      updateProgress();
    }

    updateProgress();
  </script>
</body>
</html>
```

---

## Template Customization Guide

When generating a visualization, follow these substitution rules:

| Placeholder | Replace with |
|-------------|-------------|
| `TITLE` | Descriptive title for the visualization |
| `SUBTITLE` | Date range, scope, or context |
| `SOURCE` | Data source name and version |
| `DATE` | Generation date (`YYYY-MM-DD`) |
| `labels` array | Actual data labels (dates, categories) |
| `dataset` arrays | Actual data values |
| Color references | PNGE convention colors from the palette |
| Step content | Domain-specific descriptions |
| Unit labels | Actual units (mg/L, bbl/d, psi, ft, $/ton) |

### Chart Type Selection Guide

| Data shape | Recommended chart | Template |
|------------|-------------------|----------|
| Value over time (1-3 series) | Line chart | Template 1 |
| Value over time (4+ series) | Stacked area | Template 1 (modified) |
| Compare categories | Horizontal bar | Template 2 |
| Two variables relationship | Scatter plot | Template 1 (type: 'scatter') |
| Distribution of values | Histogram | Template 2 (vertical bars, computed bins) |
| Part of whole | Doughnut chart | Template 2 (type: 'doughnut') |
| Multi-attribute comparison | Radar chart | Template 2 (type: 'radar') |
| Process or workflow | SVG flow diagram | Template 3 |
| Physical system | SVG schematic | Template 4 |
| Side-by-side entities | Tabbed view | Template 5 |
| Educational walkthrough | Animated explainer | Template 6 |
