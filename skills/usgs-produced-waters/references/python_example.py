#!/usr/bin/env python3
"""usgs_pwdb.py — Minimal client for the USGS National Produced Waters
Geochemical Database v3.0.

Downloads the database from ScienceBase (as Excel or v2.3 CSV), filters by
formation/state, and computes summary statistics for Li, Mg, and TDS.

Usage:
    python python_example.py

Dependencies: Python 3.9+ stdlib only (csv, urllib, json, statistics).
No pandas, no requests.

Credential: None required. Data is publicly accessible.
    # If a credential were needed, we would resolve it as:
    # KEY = resolve_api_key("service-name", "ENV_VAR_NAME")
"""

from __future__ import annotations

import csv
import io
import json
import os
import statistics
import sys
import urllib.request
from pathlib import Path
from typing import Optional


# ---------------------------------------------------------------------------
# Credential resolution (template — not needed for this service)
# ---------------------------------------------------------------------------

def resolve_api_key(service: str, env_var: str) -> str:
    """Resolve an API key from ~/.config/{service}/credentials or env var.

    Not needed for USGS Produced Waters (no auth required), but included
    as a template for consistency with other skills.
    """
    creds_path = Path.home() / ".config" / service / "credentials"
    if creds_path.exists():
        for line in creds_path.read_text().splitlines():
            line = line.strip()
            if line.startswith("api_key="):
                return line.removeprefix("api_key=")

    key = os.environ.get(env_var, "")
    if key:
        return key

    raise RuntimeError(
        f"No API key found for {service}. "
        f"Store in ~/.config/{service}/credentials as api_key=YOUR_KEY"
    )


# ---------------------------------------------------------------------------
# ScienceBase discovery
# ---------------------------------------------------------------------------

SCIENCEBASE_ITEM_V3 = "64fa1e71d34ed30c2054ea11"
SCIENCEBASE_ITEM_V23 = "59d25d63e4b05fe04cc235f9"


def discover_files(item_id: str) -> list[dict]:
    """Query ScienceBase API to get the file list for a dataset item.

    Returns a list of dicts with keys: name, url, size, contentType.
    """
    url = (
        f"https://www.sciencebase.gov/catalog/item/{item_id}"
        f"?format=json&fields=files,title"
    )
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode("utf-8"))

    files = []
    for f in data.get("files", []):
        files.append({
            "name": f.get("name", ""),
            "url": f.get("downloadUri", f.get("url", "")),
            "size": f.get("size", 0),
            "contentType": f.get("contentType", ""),
        })
    return files


def find_csv_url(item_id: str = SCIENCEBASE_ITEM_V23) -> str:
    """Find the main CSV download URL from ScienceBase.

    v3.0 does not include a CSV — only Excel and shapefile. So we default
    to v2.3 which has CSV files (USGSPWDBv2.3c.csv at ~66 MB).
    For v3.0 data, download the Excel file and convert or use openpyxl.
    """
    files = discover_files(item_id)
    for f in files:
        if f["name"].endswith(".csv") and "Data Dictionary" not in f["name"]:
            # Prefer the 'c' (compiled) version over 'n' (numeric-only)
            if "v2.3c" in f["name"] or "v3" in f["name"]:
                return f["url"]
    # Fallback: return first CSV found
    for f in files:
        if f["name"].endswith(".csv") and "Data Dictionary" not in f["name"]:
            return f["url"]
    raise RuntimeError(f"No CSV file found for ScienceBase item {item_id}")


# ---------------------------------------------------------------------------
# CSV download and parsing
# ---------------------------------------------------------------------------

def download_csv_rows(
    url: str,
    max_rows: Optional[int] = None,
) -> tuple[list[str], list[dict]]:
    """Download a CSV from a URL and return (headers, rows_as_dicts).

    If max_rows is set, stops after that many data rows (useful for testing).
    The full v2.3c CSV is ~66 MB / ~115k rows — be patient on first download.
    """
    print(f"Downloading CSV from: {url[:80]}...")
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=300) as resp:
        raw = resp.read().decode("utf-8", errors="replace")

    reader = csv.DictReader(io.StringIO(raw))
    headers = reader.fieldnames or []
    rows = []
    for i, row in enumerate(reader):
        if max_rows is not None and i >= max_rows:
            break
        rows.append(row)
    print(f"Loaded {len(rows)} rows with {len(headers)} columns.")
    return headers, rows


def download_csv_to_file(url: str, dest: str) -> str:
    """Download CSV to a local file for repeated use. Returns file path."""
    print(f"Downloading CSV to {dest}...")
    urllib.request.urlretrieve(url, dest)
    size_mb = os.path.getsize(dest) / 1_048_576
    print(f"Saved {size_mb:.1f} MB to {dest}")
    return dest


def load_csv_from_file(
    filepath: str,
    max_rows: Optional[int] = None,
) -> tuple[list[str], list[dict]]:
    """Load a previously downloaded CSV file."""
    rows = []
    with open(filepath, newline="", encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames or []
        for i, row in enumerate(reader):
            if max_rows is not None and i >= max_rows:
                break
            rows.append(row)
    return headers, rows


# ---------------------------------------------------------------------------
# Filtering
# ---------------------------------------------------------------------------

def filter_rows(
    rows: list[dict],
    state: Optional[str] = None,
    formation: Optional[str] = None,
    basin: Optional[str] = None,
    min_li: Optional[float] = None,
    min_tds: Optional[float] = None,
    playtype: Optional[str] = None,
) -> list[dict]:
    """Filter rows by one or more criteria. All filters are case-insensitive
    substring matches except numeric thresholds.
    """
    result = []
    for row in rows:
        if state and state.lower() not in row.get("STATE", "").lower():
            continue
        # Use FORMSIMPLE if available (v3.0), fall back to FORMATION (v2.3)
        form_val = row.get("FORMSIMPLE", row.get("FORMATION", ""))
        if formation and formation.lower() not in form_val.lower():
            continue
        if basin and basin.lower() not in row.get("BASIN", "").lower():
            continue
        if playtype and playtype.lower() not in row.get("PLAYTYPE", row.get("WELLTYPE", "")).lower():
            continue
        if min_li is not None:
            try:
                li_val = float(row.get("Li", "") or "nan")
            except (ValueError, TypeError):
                continue
            if li_val < min_li:
                continue
        if min_tds is not None:
            try:
                tds_val = float(row.get("TDS", "") or "nan")
            except (ValueError, TypeError):
                continue
            if tds_val < min_tds:
                continue
        result.append(row)
    return result


# ---------------------------------------------------------------------------
# Statistics
# ---------------------------------------------------------------------------

def safe_floats(rows: list[dict], column: str) -> list[float]:
    """Extract numeric values from a column, skipping blanks and non-numeric."""
    vals = []
    for row in rows:
        raw = row.get(column, "")
        if not raw or raw.strip() in ("", "-9999", "NA", "NaN"):
            continue
        try:
            vals.append(float(raw))
        except (ValueError, TypeError):
            continue
    return vals


def summary_stats(values: list[float]) -> dict:
    """Compute summary statistics for a list of floats."""
    if not values:
        return {"n": 0}
    return {
        "n": len(values),
        "min": min(values),
        "max": max(values),
        "mean": statistics.mean(values),
        "median": statistics.median(values),
        "stdev": statistics.stdev(values) if len(values) > 1 else 0.0,
        "p25": statistics.quantiles(values, n=4)[0] if len(values) >= 2 else values[0],
        "p75": statistics.quantiles(values, n=4)[2] if len(values) >= 2 else values[0],
    }


# ---------------------------------------------------------------------------
# Output formatting
# ---------------------------------------------------------------------------

def print_stats_table(
    label: str,
    rows: list[dict],
    columns: list[str],
) -> None:
    """Print a summary statistics table for the given columns."""
    print(f"\n{'='*60}")
    print(f"  {label}")
    print(f"  {len(rows)} samples")
    print(f"{'='*60}")
    print(f"{'Column':<10} {'N':>6} {'Min':>10} {'P25':>10} {'Median':>10} {'Mean':>10} {'P75':>10} {'Max':>10}")
    print("-" * 76)
    for col in columns:
        vals = safe_floats(rows, col)
        s = summary_stats(vals)
        if s["n"] == 0:
            print(f"{col:<10} {'0':>6} {'--':>10} {'--':>10} {'--':>10} {'--':>10} {'--':>10} {'--':>10}")
        else:
            print(
                f"{col:<10} {s['n']:>6} {s['min']:>10.1f} {s['p25']:>10.1f} "
                f"{s['median']:>10.1f} {s['mean']:>10.1f} {s['p75']:>10.1f} {s['max']:>10.1f}"
            )


def print_top_li_samples(rows: list[dict], n: int = 15) -> None:
    """Print the top N samples by lithium concentration."""
    li_rows = [(row, float(row.get("Li", "0") or "0")) for row in rows]
    li_rows.sort(key=lambda x: x[1], reverse=True)
    li_rows = [(r, v) for r, v in li_rows if v > 0]

    print(f"\n--- Top {n} samples by Li concentration ---")
    print(f"{'Li mg/L':>10} {'TDS mg/L':>12} {'State':<8} {'Formation':<20} {'Basin':<20}")
    print("-" * 72)
    for row, li_val in li_rows[:n]:
        tds = row.get("TDS", "--")
        state = row.get("STATE", "--")
        form = row.get("FORMSIMPLE", row.get("FORMATION", "--"))[:20]
        basin = row.get("BASIN", "--")[:20]
        print(f"{li_val:>10.1f} {tds:>12} {state:<8} {form:<20} {basin:<20}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    # Use v2.3 CSV (v3.0 is Excel-only; for v3.0 you would use openpyxl).
    # For a quick demo, download only the first 5000 rows.
    csv_url = find_csv_url(SCIENCEBASE_ITEM_V23)

    # Check for a local cached copy first
    cache_path = Path("/tmp/USGSPWDBv2.3c.csv")
    if cache_path.exists():
        print(f"Using cached file: {cache_path}")
        headers, rows = load_csv_from_file(str(cache_path), max_rows=5000)
    else:
        print("Downloading from ScienceBase (this may take a minute)...")
        headers, rows = download_csv_rows(csv_url, max_rows=5000)

    # Show available columns
    print(f"\nColumns ({len(headers)}):")
    for i in range(0, len(headers), 8):
        print("  " + ", ".join(headers[i : i + 8]))

    # Example 1: Marcellus Shale samples — Li, Mg, TDS statistics
    marcellus = filter_rows(rows, formation="marcellus")
    if marcellus:
        print_stats_table(
            "Marcellus Shale — Key Analytes",
            marcellus,
            ["Li", "Mg", "Ca", "Na", "Cl", "Ba", "Sr", "Br", "TDS"],
        )
    else:
        print("\nNo Marcellus samples found in this subset.")

    # Example 2: West Virginia samples
    wv = filter_rows(rows, state="West Virginia")
    if wv:
        print_stats_table(
            "West Virginia — All Formations",
            wv,
            ["Li", "Mg", "TDS"],
        )

    # Example 3: High-Li samples (above 100 mg/L)
    high_li = filter_rows(rows, min_li=100.0)
    if high_li:
        print(f"\nSamples with Li >= 100 mg/L: {len(high_li)}")
        print_stats_table(
            "High Lithium Samples (Li >= 100 mg/L)",
            high_li,
            ["Li", "Mg", "TDS"],
        )
        print_top_li_samples(high_li, n=10)
    else:
        print("\nNo samples with Li >= 100 mg/L in this subset (try full dataset).")

    # Example 4: Top Li samples across all data
    print_top_li_samples(rows, n=15)


if __name__ == "__main__":
    main()
