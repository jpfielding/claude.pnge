#!/usr/bin/env python3
"""opec_client.py -- Query OPEC data via EIA STEO and International APIs.

Uses only the Python standard library. No third-party packages required.

Usage:
    python opec_client.py

Credential resolution order:
    1. ~/.config/eia/credentials  (api_key=YOUR_KEY)
    2. EIA_API_KEY env var
    3. Raises RuntimeError with setup instructions
"""

from __future__ import annotations

import json
import os
import urllib.parse
import urllib.request
from pathlib import Path


# ---------------------------------------------------------------------------
# Credential resolution
# ---------------------------------------------------------------------------

def resolve_api_key() -> str:
    """Resolve EIA API key from credentials file or env var."""
    creds_path = Path.home() / ".config" / "eia" / "credentials"
    if creds_path.exists():
        for line in creds_path.read_text().splitlines():
            line = line.strip()
            if line.startswith("api_key="):
                return line.removeprefix("api_key=")

    key = os.environ.get("EIA_API_KEY", "")
    if key:
        return key

    raise RuntimeError(
        "No EIA API key found. Store it in ~/.config/eia/credentials as:\n"
        "  api_key=YOUR_KEY\n"
        "Or set the EIA_API_KEY environment variable.\n"
        "Get a free key at https://www.eia.gov/opendata/"
    )


# ---------------------------------------------------------------------------
# STEO client (OPEC aggregates, prices, forecasts)
# ---------------------------------------------------------------------------

STEO_URL = "https://api.eia.gov/v2/steo/data/"
INTL_URL = "https://api.eia.gov/v2/international/data/"


def fetch_steo_series(
    api_key: str,
    series_ids: list[str],
    frequency: str = "monthly",
    start: str = "",
    end: str = "",
    length: int = 120,
) -> list[dict]:
    """Fetch one or more STEO series.

    Args:
        api_key: EIA API key.
        series_ids: List of STEO series IDs (e.g. ["COPR_OPEC", "COPS_OPEC"]).
        frequency: "monthly" or "annual".
        start: Inclusive start period (e.g. "2023-01").
        end: Inclusive end period (e.g. "2025-12").
        length: Max rows to return (default 120 = 10 years monthly).

    Returns:
        List of data row dicts from the API response.
    """
    params: list[tuple[str, str]] = [
        ("api_key", api_key),
        ("frequency", frequency),
        ("data[]", "value"),
        ("sort[0][column]", "period"),
        ("sort[0][direction]", "desc"),
        ("length", str(length)),
    ]
    for sid in series_ids:
        params.append(("facets[seriesId][]", sid))
    if start:
        params.append(("start", start))
    if end:
        params.append(("end", end))

    url = STEO_URL + "?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(url, timeout=30) as resp:
        body = json.loads(resp.read().decode())

    data = body["response"]["data"]
    total = body["response"]["total"]
    if int(total) > length:
        print(f"Warning: {total} rows available, only {length} returned. "
              f"Increase length or narrow date range.")
    return data


def fetch_country_production(
    api_key: str,
    country_codes: list[str],
    frequency: str = "annual",
    start: str = "",
    length: int = 500,
) -> list[dict]:
    """Fetch crude oil production for specific countries from EIA International.

    Args:
        api_key: EIA API key.
        country_codes: List of ISO country codes (e.g. ["SAU", "IRQ", "ARE"]).
        frequency: "annual" or "monthly".
        start: Inclusive start year (e.g. "2015").
        length: Max rows to return.

    Returns:
        List of data row dicts.
    """
    params: list[tuple[str, str]] = [
        ("api_key", api_key),
        ("frequency", frequency),
        ("facets[productId][]", "57"),       # crude oil incl. lease condensate
        ("facets[activityId][]", "1"),        # production
        ("facets[unit][]", "TBPD"),           # thousand barrels per day
        ("data[]", "value"),
        ("sort[0][column]", "period"),
        ("sort[0][direction]", "desc"),
        ("length", str(length)),
    ]
    for code in country_codes:
        params.append(("facets[countryRegionId][]", code))
    if start:
        params.append(("start", start))

    url = INTL_URL + "?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(url, timeout=30) as resp:
        body = json.loads(resp.read().decode())

    return body["response"]["data"]


# ---------------------------------------------------------------------------
# Display helpers
# ---------------------------------------------------------------------------

def print_table(rows: list[dict], cols: list[str], max_rows: int = 20) -> None:
    """Print a fixed-width table from a list of row dicts."""
    display = rows[:max_rows]
    widths = {}
    for c in cols:
        col_vals = [str(r.get(c, "")) for r in display]
        widths[c] = max(len(c), *(len(v) for v in col_vals))
    header = "  ".join(c.ljust(widths[c]) for c in cols)
    print(header)
    print("-" * len(header))
    for row in display:
        print("  ".join(str(row.get(c, "")).ljust(widths[c]) for c in cols))
    if len(rows) > max_rows:
        print(f"... ({len(rows) - max_rows} more rows)")


# ---------------------------------------------------------------------------
# Example usage
# ---------------------------------------------------------------------------

def main() -> None:
    api_key = resolve_api_key()

    # --- Example 1: OPEC production + spare capacity ---
    print("=== OPEC Production and Spare Capacity (last 12 months) ===\n")
    rows = fetch_steo_series(
        api_key,
        series_ids=["COPR_OPEC", "COPS_OPEC", "COPC_OPEC"],
        start="2024-01",
        length=72,
    )

    # Pivot by period
    by_period: dict[str, dict[str, str]] = {}
    for row in rows:
        p = row["period"]
        sid = row["seriesId"]
        val = f"{float(row['value']):.2f}"
        if p not in by_period:
            by_period[p] = {"period": p}
        if sid == "COPR_OPEC":
            by_period[p]["production"] = val
        elif sid == "COPS_OPEC":
            by_period[p]["spare"] = val
        elif sid == "COPC_OPEC":
            by_period[p]["capacity"] = val

    sorted_periods = sorted(by_period.keys(), reverse=True)[:12]
    pivoted = [by_period[p] for p in sorted_periods]
    print_table(pivoted, ["period", "production", "capacity", "spare"])

    # --- Example 2: Brent and WTI prices ---
    print("\n=== Brent vs WTI Crude Oil Prices (last 12 months) ===\n")
    rows = fetch_steo_series(
        api_key,
        series_ids=["BREPUUS", "WTIPUUS"],
        start="2024-01",
        length=48,
    )

    by_period2: dict[str, dict[str, str]] = {}
    for row in rows:
        p = row["period"]
        sid = row["seriesId"]
        val = f"${float(row['value']):.2f}"
        if p not in by_period2:
            by_period2[p] = {"period": p}
        if sid == "BREPUUS":
            by_period2[p]["brent"] = val
        elif sid == "WTIPUUS":
            by_period2[p]["wti"] = val

    sorted_p2 = sorted(by_period2.keys(), reverse=True)[:12]
    pivoted2 = [by_period2[p] for p in sorted_p2]
    print_table(pivoted2, ["period", "brent", "wti"])

    # --- Example 3: Per-country production (top 5 OPEC producers) ---
    print("\n=== Top OPEC Members Crude Oil Production (annual, last 5 years) ===\n")
    rows = fetch_country_production(
        api_key,
        country_codes=["SAU", "IRQ", "ARE", "KWT", "IRN"],
        frequency="annual",
        start="2019",
    )

    # Print as flat table
    flat = []
    for row in rows:
        flat.append({
            "year": row["period"],
            "country": row["countryRegionName"],
            "production_kbpd": f"{float(row['value']):.0f}",
        })
    # Sort by year desc, then country
    flat.sort(key=lambda r: (-int(r["year"]), r["country"]))
    print_table(flat, ["year", "country", "production_kbpd"], max_rows=25)


if __name__ == "__main__":
    main()
