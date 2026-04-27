#!/usr/bin/env python3
"""usgs_minerals_client.py — Minimal USGS Mineral Commodity data client.

Searches ScienceBase for MCS data releases, downloads CSV files, and
parses commodity statistics. Uses only Python stdlib (no pip installs).

Usage:
    python python_example.py

No API key required — all USGS ScienceBase data is public.
"""

from __future__ import annotations

import csv
import io
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from typing import Any


# ---------------------------------------------------------------------------
# ScienceBase API helpers
# ---------------------------------------------------------------------------

SCIENCEBASE_API = "https://www.sciencebase.gov/catalog"


def sb_search(query: str, max_results: int = 10) -> list[dict[str, Any]]:
    """Search ScienceBase items by keyword.

    Returns a list of item dicts with 'id', 'title', and 'files' fields.
    """
    params = urllib.parse.urlencode({
        "q": query,
        "format": "json",
        "max": max_results,
        "fields": "title,id,files",
    })
    url = f"{SCIENCEBASE_API}/items?{params}"
    with urllib.request.urlopen(url, timeout=30) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return data.get("items", [])


def sb_get_item(item_id: str) -> dict[str, Any]:
    """Get a single ScienceBase item by ID, including file metadata."""
    url = f"{SCIENCEBASE_API}/item/{item_id}?format=json&fields=title,files"
    with urllib.request.urlopen(url, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def sb_download_csv(download_uri: str) -> list[dict[str, str]]:
    """Download a CSV from ScienceBase and return rows as list of dicts."""
    with urllib.request.urlopen(download_uri, timeout=60) as resp:
        raw = resp.read()
    # Handle BOM if present
    text = raw.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text))
    return list(reader)


# ---------------------------------------------------------------------------
# MCS data access
# ---------------------------------------------------------------------------

# Known ScienceBase item IDs for key commodities (MCS 2025)
MCS_2025_ITEMS = {
    "lithium":              "6797ff62d34ea8c18376e1cb",
    "magnesium_compounds":  "6797ffe2d34ea8c18376e1da",
    "magnesium_metal":      "6797ffffd34ea8c18376e1e5",
}

# MCS 2026 aggregated data (all commodities in one CSV)
MCS_2026_ITEM = "696a75d5d4be0228872d3bf8"

# World Minerals Outlook 2029 (Li, Mg, Co, Ga, He, Pd, Pt, Ti)
OUTLOOK_2029_ITEM = "67b8b168d34e1a2e835b7e6c"


def get_mcs2025_salient(commodity: str) -> list[dict[str, str]]:
    """Download MCS 2025 salient statistics CSV for a known commodity.

    Args:
        commodity: One of 'lithium', 'magnesium_compounds', 'magnesium_metal'

    Returns:
        List of row dicts from the salient CSV.
    """
    item_id = MCS_2025_ITEMS.get(commodity)
    if not item_id:
        raise ValueError(
            f"Unknown commodity '{commodity}'. "
            f"Known: {', '.join(MCS_2025_ITEMS.keys())}"
        )
    item = sb_get_item(item_id)
    csv_files = [f for f in item.get("files", [])
                 if f["name"].endswith(".csv")]
    if not csv_files:
        raise RuntimeError(f"No CSV files found for {commodity}")
    return sb_download_csv(csv_files[0]["downloadUri"])


def search_mcs2026(commodity: str) -> list[dict[str, str]]:
    """Download MCS 2026 aggregated CSV and filter by commodity name.

    Args:
        commodity: Commodity name to filter (case-insensitive substring match).

    Returns:
        List of row dicts matching the commodity.
    """
    item = sb_get_item(MCS_2026_ITEM)
    csv_file = None
    for f in item.get("files", []):
        if f["name"] == "MCS2026_Commodities_Data.csv":
            csv_file = f
            break
    if not csv_file:
        raise RuntimeError("MCS2026_Commodities_Data.csv not found")

    rows = sb_download_csv(csv_file["downloadUri"])
    needle = commodity.lower()
    return [r for r in rows if needle in r.get("Commodity", "").lower()]


def get_outlook_data(commodity: str) -> list[dict[str, str]]:
    """Download World Minerals Outlook CSV and filter by commodity.

    Args:
        commodity: e.g. 'Lithium', 'Magnesium metal'

    Returns:
        List of row dicts for that commodity.
    """
    item = sb_get_item(OUTLOOK_2029_ITEM)
    csv_file = None
    for f in item.get("files", []):
        if f["name"].endswith(".csv") and "Data Release" in f["name"]:
            csv_file = f
            break
    if not csv_file:
        raise RuntimeError("Outlook CSV not found")

    rows = sb_download_csv(csv_file["downloadUri"])
    needle = commodity.lower()
    return [r for r in rows
            if needle in r.get("Mineral_Commodity", "").lower()]


# ---------------------------------------------------------------------------
# Display helpers
# ---------------------------------------------------------------------------

def print_table(rows: list[dict[str, str]], cols: list[str],
                max_rows: int = 20) -> None:
    """Print a fixed-width table from a list of row dicts."""
    if not rows:
        print("(no data)")
        return
    display = rows[:max_rows]
    widths = {}
    for c in cols:
        w = len(c)
        for r in display:
            w = max(w, len(str(r.get(c, ""))))
        widths[c] = min(w, 40)  # cap column width

    header = "  ".join(c.ljust(widths[c]) for c in cols)
    print(header)
    print("-" * len(header))
    for row in display:
        vals = []
        for c in cols:
            v = str(row.get(c, ""))
            if len(v) > 40:
                v = v[:37] + "..."
            vals.append(v.ljust(widths[c]))
        print("  ".join(vals))
    if len(rows) > max_rows:
        print(f"... ({len(rows) - max_rows} more rows)")


# ---------------------------------------------------------------------------
# Example usage
# ---------------------------------------------------------------------------

def main() -> None:
    print("=" * 60)
    print("Example 1: MCS 2025 Lithium Salient Statistics")
    print("=" * 60)
    try:
        rows = get_mcs2025_salient("lithium")
        print(f"\nRecords: {len(rows)}\n")
        cols = ["Year", "USprod_t", "Imports_t", "Exports_t",
                "Price_dt", "NIR_pct"]
        print_table(rows, cols)
    except Exception as e:
        print(f"Error: {e}")

    print()
    print("=" * 60)
    print("Example 2: MCS 2025 Magnesium Metal Salient Statistics")
    print("=" * 60)
    try:
        rows = get_mcs2025_salient("magnesium_metal")
        print(f"\nRecords: {len(rows)}\n")
        cols = ["Year", "USprod_Primary_kt", "USprod_Secondary_kt",
                "Imports_kt", "Price_dt", "NIR_pct"]
        print_table(rows, cols)
    except Exception as e:
        print(f"Error: {e}")

    print()
    print("=" * 60)
    print("Example 3: MCS 2026 Lithium — World Mine Production")
    print("=" * 60)
    try:
        rows = search_mcs2026("lithium")
        # Filter to world mine production section
        prod_rows = [r for r in rows
                     if "World Mine" in r.get("Section", "")
                     and r.get("Statistics") == "Production"]
        print(f"\nRecords: {len(prod_rows)}\n")
        cols = ["Country", "Year", "Value", "Unit"]
        print_table(prod_rows, cols)
    except Exception as e:
        print(f"Error: {e}")

    print()
    print("=" * 60)
    print("Example 4: ScienceBase Search for Commodity Data")
    print("=" * 60)
    try:
        items = sb_search("mineral commodity summaries 2025 lithium", max_results=3)
        for item in items:
            print(f"\n  ID: {item['id']}")
            print(f"  Title: {item['title']}")
            for f in item.get("files", []):
                if f["name"].endswith(".csv"):
                    print(f"  CSV: {f['name']} ({f.get('size', '?')} bytes)")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
