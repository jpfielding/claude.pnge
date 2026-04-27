#!/usr/bin/env python3
"""
PNGE Visual Explainer — Python HTML Generator (stdlib only)

Generates self-contained HTML visualization files using Chart.js from CDN.
Demonstrates three chart types:
  1. Time series (production decline curve)
  2. Bar chart (Li concentration by formation)
  3. Scatter plot (Li vs. TDS relationship)

Usage:
    python python_example.py                  # generates all three demos
    python python_example.py --type timeseries
    python python_example.py --type bar
    python python_example.py --type scatter
    python python_example.py --output my_chart.html --type bar

All output is a single self-contained HTML file. No dependencies beyond
Python 3.6+ standard library.
"""

import argparse
import json
import os
import sys
import textwrap
from datetime import datetime


# ---------------------------------------------------------------------------
# PNGE Color Palette
# ---------------------------------------------------------------------------
COLORS = {
    "oil": "#2d5016",
    "gas": "#c0392b",
    "water": "#2980b9",
    "lithium": "#9b59b6",
    "magnesium": "#1abc9c",
    "sodium": "#f39c12",
    "calcium": "#e67e22",
    "accent": "#c8a850",
    "chart": [
        "#3498db", "#9b59b6", "#1abc9c", "#e74c3c",
        "#f39c12", "#2d5016", "#e67e22", "#34495e",
    ],
}


# ---------------------------------------------------------------------------
# Shared CSS (dark/light theme, responsive, print-friendly)
# ---------------------------------------------------------------------------
SHARED_CSS = """\
:root {
  --oil: #2d5016; --gas: #c0392b; --water: #2980b9;
  --lithium: #9b59b6; --magnesium: #1abc9c;
  --accent: #c8a850;
}
[data-theme="dark"] {
  --bg-primary: #0f1419; --bg-secondary: #1a1f25; --bg-card: #1e2530;
  --text-primary: #e8eaed; --text-secondary: #9aa0a6; --text-muted: #6b7280;
  --border: #2d333b; --shadow: rgba(0,0,0,0.3);
  --grid-line: rgba(255,255,255,0.08);
}
[data-theme="light"] {
  --bg-primary: #ffffff; --bg-secondary: #f8f9fa; --bg-card: #ffffff;
  --text-primary: #1a1a2e; --text-secondary: #4a5568; --text-muted: #9ca3af;
  --border: #dee2e6; --shadow: rgba(0,0,0,0.08);
  --grid-line: rgba(0,0,0,0.08);
}
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background: var(--bg-primary); color: var(--text-primary);
  line-height: 1.6; min-height: 100vh;
}
.container { max-width: 1000px; margin: 0 auto; padding: 2rem 1.5rem; }
header {
  text-align: center; margin-bottom: 2rem;
  padding-bottom: 1.5rem; border-bottom: 1px solid var(--border);
}
header h1 { font-size: 1.8rem; font-weight: 700; margin-bottom: 0.3rem; }
header .subtitle { font-size: 1rem; color: var(--text-secondary); }
.toolbar {
  display: flex; justify-content: flex-end; gap: 0.5rem; margin-bottom: 1rem;
}
.toolbar button {
  background: var(--bg-secondary); color: var(--text-secondary);
  border: 1px solid var(--border); padding: 0.4rem 0.8rem;
  border-radius: 6px; cursor: pointer; font-size: 0.85rem; transition: all 0.2s;
}
.toolbar button:hover {
  background: var(--accent); color: #fff; border-color: var(--accent);
}
.chart-container {
  background: var(--bg-card); border: 1px solid var(--border);
  border-radius: 12px; padding: 1.5rem; margin-bottom: 1.5rem;
  box-shadow: 0 2px 8px var(--shadow);
}
.chart-container h2 { font-size: 1.2rem; margin-bottom: 1rem; }
.stat-row {
  display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 1rem; margin-bottom: 1.5rem;
}
.stat-card {
  background: var(--bg-card); border: 1px solid var(--border);
  border-radius: 10px; padding: 1.2rem; text-align: center;
}
.stat-card .value { font-size: 2rem; font-weight: 700; color: var(--accent); }
.stat-card .label { font-size: 0.85rem; color: var(--text-secondary); margin-top: 0.3rem; }
footer {
  margin-top: 2rem; padding-top: 1rem; border-top: 1px solid var(--border);
  font-size: 0.8rem; color: var(--text-muted); text-align: center;
}
@media print {
  body { background: #fff; color: #000; }
  .no-print { display: none !important; }
  .chart-container { box-shadow: none; border: 1px solid #ccc; break-inside: avoid; }
  .stat-card .value { color: #333; }
}
@media (max-width: 768px) {
  .container { padding: 1rem; }
  header h1 { font-size: 1.4rem; }
}
"""

THEME_TOGGLE_JS = """\
function toggleTheme() {
  const html = document.documentElement;
  const next = html.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
  html.setAttribute('data-theme', next);
}
"""


# ---------------------------------------------------------------------------
# HTML Builder Helpers
# ---------------------------------------------------------------------------

def _wrap_html(title: str, subtitle: str, source: str, body: str,
               chart_js: str, use_chartjs: bool = True) -> str:
    """Wrap body content in the full HTML shell."""
    chartjs_tag = (
        '<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>'
        if use_chartjs else ""
    )
    today = datetime.now().strftime("%Y-%m-%d")
    return textwrap.dedent(f"""\
    <!DOCTYPE html>
    <html lang="en" data-theme="dark">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>{title}</title>
      {chartjs_tag}
      <style>
    {SHARED_CSS}
      </style>
    </head>
    <body>
      <div class="container">
        <header>
          <h1>{title}</h1>
          <p class="subtitle">{subtitle}</p>
        </header>
        <div class="toolbar no-print">
          <button onclick="toggleTheme()">Toggle Theme</button>
          <button onclick="window.print()">Print / PDF</button>
        </div>
    {body}
        <footer>
          Generated by PNGE Visual Explainer |
          Data source: {source} |
          {today}
        </footer>
      </div>
      <script>
    {THEME_TOGGLE_JS}
    {chart_js}
      </script>
    </body>
    </html>
    """)


# ---------------------------------------------------------------------------
# Chart 1: Time Series — Production Decline Curve
# ---------------------------------------------------------------------------

def generate_timeseries() -> str:
    """Generate a production decline curve (Arps exponential)."""

    # Simulated monthly production data (bbl/d) — exponential decline
    months = []
    oil_prod = []
    gas_prod = []
    qi_oil = 800.0   # initial oil rate bbl/d
    qi_gas = 4500.0   # initial gas rate Mcf/d
    di = 0.06          # nominal monthly decline rate

    for m in range(36):
        year = 2022 + m // 12
        month = 1 + m % 12
        months.append(f"{year}-{month:02d}")
        oil_prod.append(round(qi_oil * ((1 - di) ** m), 1))
        gas_prod.append(round(qi_gas * ((1 - di) ** m), 1))

    labels_json = json.dumps(months)
    oil_json = json.dumps(oil_prod)
    gas_json = json.dumps(gas_prod)

    body = textwrap.dedent("""\
        <div class="stat-row">
          <div class="stat-card">
            <div class="value">800</div>
            <div class="label">Initial Oil Rate (bbl/d)</div>
          </div>
          <div class="stat-card">
            <div class="value">4,500</div>
            <div class="label">Initial Gas Rate (Mcf/d)</div>
          </div>
          <div class="stat-card">
            <div class="value">6.0%</div>
            <div class="label">Monthly Decline Rate</div>
          </div>
        </div>
        <div class="chart-container">
          <h2>Production Decline — Oil (bbl/d) and Gas (Mcf/d)</h2>
          <canvas id="declineChart"></canvas>
        </div>
    """)

    chart_js = textwrap.dedent(f"""\
    const style = getComputedStyle(document.documentElement);
    new Chart(document.getElementById('declineChart'), {{
      type: 'line',
      data: {{
        labels: {labels_json},
        datasets: [
          {{
            label: 'Oil (bbl/d)',
            data: {oil_json},
            borderColor: '#4a8c1c',
            backgroundColor: 'rgba(74, 140, 28, 0.1)',
            fill: true, tension: 0.3, pointRadius: 2, borderWidth: 2,
            yAxisID: 'y'
          }},
          {{
            label: 'Gas (Mcf/d)',
            data: {gas_json},
            borderColor: '#e74c3c',
            backgroundColor: 'rgba(231, 76, 60, 0.1)',
            fill: true, tension: 0.3, pointRadius: 2, borderWidth: 2,
            yAxisID: 'y1'
          }}
        ]
      }},
      options: {{
        responsive: true,
        interaction: {{ mode: 'index', intersect: false }},
        plugins: {{
          legend: {{ labels: {{ color: '#9aa0a6' }} }},
          tooltip: {{
            backgroundColor: 'rgba(0,0,0,0.85)', cornerRadius: 6, padding: 10
          }}
        }},
        scales: {{
          x: {{
            grid: {{ color: 'rgba(255,255,255,0.08)' }},
            ticks: {{ color: '#9aa0a6', maxRotation: 45 }}
          }},
          y: {{
            type: 'linear', position: 'left',
            title: {{ display: true, text: 'Oil (bbl/d)', color: '#4a8c1c' }},
            grid: {{ color: 'rgba(255,255,255,0.08)' }},
            ticks: {{ color: '#4a8c1c' }}
          }},
          y1: {{
            type: 'linear', position: 'right',
            title: {{ display: true, text: 'Gas (Mcf/d)', color: '#e74c3c' }},
            grid: {{ drawOnChartArea: false }},
            ticks: {{ color: '#e74c3c' }}
          }}
        }}
      }}
    }});
    """)

    return _wrap_html(
        title="Production Decline Curve — Marcellus Shale Well",
        subtitle="Exponential decline model, 36-month forecast (Di = 6%/month)",
        source="Simulated Arps decline data",
        body=body,
        chart_js=chart_js,
    )


# ---------------------------------------------------------------------------
# Chart 2: Bar Chart — Li Concentration by Formation
# ---------------------------------------------------------------------------

def generate_bar() -> str:
    """Generate horizontal bar chart of Li concentration by formation."""

    formations = [
        "Smackover (AR/TX/LA)",
        "Marcellus (WV/PA/OH)",
        "Utica (OH/WV/PA)",
        "Bakken (ND/MT)",
        "Permian Basin (TX/NM)",
        "Fayetteville (AR)",
        "Haynesville (LA/TX)",
    ]
    max_li = [477, 200, 150, 70, 45, 30, 25]
    avg_li = [250, 85, 65, 35, 22, 15, 12]
    threshold = 100  # economic DLE threshold

    formations_json = json.dumps(formations)
    max_json = json.dumps(max_li)
    avg_json = json.dumps(avg_li)

    body = textwrap.dedent(f"""\
        <div class="stat-row">
          <div class="stat-card">
            <div class="value" style="color: #9b59b6">477</div>
            <div class="label">Highest Li (mg/L) — Smackover</div>
          </div>
          <div class="stat-card">
            <div class="value" style="color: #c8a850">{threshold}</div>
            <div class="label">DLE Economic Threshold (mg/L)</div>
          </div>
          <div class="stat-card">
            <div class="value">7</div>
            <div class="label">Formations Compared</div>
          </div>
        </div>
        <div class="chart-container">
          <h2>Lithium in U.S. Produced Water by Formation</h2>
          <canvas id="barChart"></canvas>
        </div>
    """)

    chart_js = textwrap.dedent(f"""\
    new Chart(document.getElementById('barChart'), {{
      type: 'bar',
      data: {{
        labels: {formations_json},
        datasets: [
          {{
            label: 'Max Li (mg/L)',
            data: {max_json},
            backgroundColor: 'rgba(155, 89, 182, 0.7)',
            borderColor: '#9b59b6',
            borderWidth: 1, borderRadius: 4
          }},
          {{
            label: 'Avg Li (mg/L)',
            data: {avg_json},
            backgroundColor: 'rgba(155, 89, 182, 0.3)',
            borderColor: '#9b59b6',
            borderWidth: 1, borderRadius: 4
          }}
        ]
      }},
      options: {{
        responsive: true,
        indexAxis: 'y',
        plugins: {{
          legend: {{ labels: {{ color: '#9aa0a6' }} }},
          tooltip: {{
            callbacks: {{
              label: function(ctx) {{ return ctx.dataset.label + ': ' + ctx.parsed.x + ' mg/L'; }}
            }}
          }},
          annotation: {{
            annotations: {{
              threshold: {{
                type: 'line',
                xMin: {threshold}, xMax: {threshold},
                borderColor: '#c8a850', borderWidth: 2,
                borderDash: [6, 4],
                label: {{
                  display: true, content: 'DLE Threshold',
                  position: 'start', color: '#c8a850',
                  font: {{ size: 11 }}
                }}
              }}
            }}
          }}
        }},
        scales: {{
          x: {{
            grid: {{ color: 'rgba(255,255,255,0.08)' }},
            ticks: {{ color: '#9aa0a6' }},
            title: {{ display: true, text: 'Li Concentration (mg/L)', color: '#9aa0a6' }}
          }},
          y: {{
            grid: {{ display: false }},
            ticks: {{ color: '#e8eaed', font: {{ size: 12 }} }}
          }}
        }}
      }}
    }});
    """)

    return _wrap_html(
        title="Lithium Concentration by U.S. Formation",
        subtitle="Max and average Li in produced water — USGS PWGDB v3.0",
        source="USGS National Produced Waters Geochemical Database v3.0",
        body=body,
        chart_js=chart_js,
    )


# ---------------------------------------------------------------------------
# Chart 3: Scatter Plot — Li vs. TDS
# ---------------------------------------------------------------------------

def generate_scatter() -> str:
    """Generate scatter plot of Li concentration vs. TDS."""

    import random
    random.seed(42)

    # Simulated data points by formation
    formations = {
        "Smackover": {"color": "#e74c3c", "n": 30, "tds_range": (180000, 310000), "li_range": (50, 477)},
        "Marcellus": {"color": "#3498db", "n": 50, "tds_range": (80000, 300000), "li_range": (5, 210)},
        "Utica": {"color": "#1abc9c", "n": 25, "tds_range": (140000, 350000), "li_range": (15, 155)},
        "Bakken": {"color": "#f39c12", "n": 20, "tds_range": (180000, 360000), "li_range": (8, 72)},
    }

    datasets_js_parts = []
    for name, cfg in formations.items():
        points = []
        for _ in range(cfg["n"]):
            tds = random.randint(*cfg["tds_range"])
            li = round(random.uniform(*cfg["li_range"]), 1)
            points.append({"x": tds, "y": li})

        points_json = json.dumps(points)
        datasets_js_parts.append(textwrap.dedent(f"""\
          {{
            label: '{name}',
            data: {points_json},
            backgroundColor: '{cfg["color"]}',
            pointRadius: 4,
            pointHoverRadius: 7
          }}"""))

    datasets_js = ",\n".join(datasets_js_parts)

    body = textwrap.dedent("""\
        <div class="stat-row">
          <div class="stat-card">
            <div class="value">125</div>
            <div class="label">Total Samples</div>
          </div>
          <div class="stat-card">
            <div class="value">4</div>
            <div class="label">Formations</div>
          </div>
          <div class="stat-card">
            <div class="value" style="color: #9b59b6">477</div>
            <div class="label">Max Li (mg/L)</div>
          </div>
        </div>
        <div class="chart-container">
          <h2>Lithium vs. Total Dissolved Solids by Formation</h2>
          <canvas id="scatterChart"></canvas>
        </div>
    """)

    chart_js = textwrap.dedent(f"""\
    new Chart(document.getElementById('scatterChart'), {{
      type: 'scatter',
      data: {{
        datasets: [
    {datasets_js}
        ]
      }},
      options: {{
        responsive: true,
        plugins: {{
          legend: {{ labels: {{ color: '#9aa0a6', usePointStyle: true }} }},
          tooltip: {{
            callbacks: {{
              label: function(ctx) {{
                return ctx.dataset.label +
                  ': TDS=' + ctx.parsed.x.toLocaleString() + ' mg/L' +
                  ', Li=' + ctx.parsed.y + ' mg/L';
              }}
            }}
          }}
        }},
        scales: {{
          x: {{
            grid: {{ color: 'rgba(255,255,255,0.08)' }},
            ticks: {{
              color: '#9aa0a6',
              callback: function(v) {{ return (v / 1000) + 'k'; }}
            }},
            title: {{ display: true, text: 'TDS (mg/L)', color: '#9aa0a6' }}
          }},
          y: {{
            grid: {{ color: 'rgba(255,255,255,0.08)' }},
            ticks: {{ color: '#9aa0a6' }},
            title: {{ display: true, text: 'Li Concentration (mg/L)', color: '#9aa0a6' }}
          }}
        }}
      }}
    }});
    """)

    return _wrap_html(
        title="Li vs. TDS — U.S. Produced Water Samples",
        subtitle="Scatter plot across four major Li-bearing formations",
        source="USGS National Produced Waters Geochemical Database v3.0 (simulated subset)",
        body=body,
        chart_js=chart_js,
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

GENERATORS = {
    "timeseries": generate_timeseries,
    "bar": generate_bar,
    "scatter": generate_scatter,
}


def main():
    parser = argparse.ArgumentParser(
        description="Generate PNGE HTML visualizations (stdlib only)."
    )
    parser.add_argument(
        "--type", choices=list(GENERATORS.keys()),
        help="Chart type to generate. Omit to generate all three.",
    )
    parser.add_argument(
        "--output", "-o",
        help="Output filename. Defaults to pnge-{type}-YYYYMMDD.html",
    )
    args = parser.parse_args()

    today = datetime.now().strftime("%Y%m%d")

    if args.type:
        types_to_gen = [args.type]
    else:
        types_to_gen = list(GENERATORS.keys())

    for chart_type in types_to_gen:
        html = GENERATORS[chart_type]()

        if args.output and len(types_to_gen) == 1:
            outpath = args.output
        else:
            outpath = f"pnge-{chart_type}-{today}.html"

        with open(outpath, "w", encoding="utf-8") as f:
            f.write(html)

        size_kb = os.path.getsize(outpath) / 1024
        print(f"[OK] {outpath} ({size_kb:.1f} KB)")
        print(f"     Open: {'open' if sys.platform == 'darwin' else 'xdg-open'} {outpath}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
