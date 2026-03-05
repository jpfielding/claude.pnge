#!/usr/bin/env python3
"""iea_client.py -- Query free IEA open data endpoints.

Uses only the Python standard library. No third-party packages required.
No API key required.

Usage:
    python iea_client.py
"""

from __future__ import annotations

import json
import urllib.parse
import urllib.request


BASE_URL = "https://api.iea.org"


# ---------------------------------------------------------------------------
# Generic fetch
# ---------------------------------------------------------------------------

def fetch_iea(endpoint: str, params: dict[str, str] | None = None,
              timeout: int = 30) -> list[dict]:
    """Fetch data from an IEA open endpoint.

    Args:
        endpoint: API path (e.g., "evs", "prices", "ghg", "nze", "ccus").
        params: Query parameter dict. Keys must match the JSON field names
                returned by the endpoint.
        timeout: Request timeout in seconds.

    Returns:
        List of data row dicts from the API response.
    """
    url = f"{BASE_URL}/{endpoint}"
    if params:
        qs = urllib.parse.urlencode(params, quote_via=urllib.parse.quote)
        url = f"{url}?{qs}"

    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read().decode("utf-8")

    data = json.loads(raw)
    if not isinstance(data, list):
        raise ValueError(f"Expected JSON array, got {type(data).__name__}")
    return data


# ---------------------------------------------------------------------------
# Typed endpoint helpers
# ---------------------------------------------------------------------------

def fetch_evs(
    region: str = "",
    category: str = "",
    parameter: str = "",
    mode: str = "",
    powertrain: str = "",
    year: int | None = None,
) -> list[dict]:
    """Fetch Global EV Tracker data.

    All parameters are optional filters.
    """
    params = {}
    if region:
        params["region"] = region
    if category:
        params["category"] = category
    if parameter:
        params["parameter"] = parameter
    if mode:
        params["mode"] = mode
    if powertrain:
        params["powertrain"] = powertrain
    if year is not None:
        params["year"] = str(year)
    return fetch_iea("evs", params)


def fetch_prices(
    country: str = "",
    product: str = "",
    sector: str = "",
    indicator: str = "",
    unit: str = "",
) -> list[dict]:
    """Fetch energy end-use prices.

    Use CODE_ field values for filtering (e.g., country="USA",
    product="GASOLINE", sector="TRANS").
    """
    params = {}
    if country:
        params["CODE_COUNTRY"] = country
    if product:
        params["CODE_PRODUCT"] = product
    if sector:
        params["CODE_SECTOR"] = sector
    if indicator:
        params["CODE_INDICATOR"] = indicator
    if unit:
        params["CODE_UNIT"] = unit
    return fetch_iea("prices", params)


def fetch_ghg(
    country: str = "",
    product: str = "",
    flow: str = "",
) -> list[dict]:
    """Fetch CO2 and GHG emissions data.

    Use CODE_ field values for filtering (e.g., country="USA",
    product="TOTAL", flow="CO2FUEL").

    WARNING: Unfiltered returns ~207K records. Always filter.
    """
    params = {}
    if country:
        params["CODE_COUNTRY"] = country
    if product:
        params["CODE_PRODUCT"] = product
    if flow:
        params["CODE_FLOW"] = flow
    return fetch_iea("ghg", params, timeout=60)


def fetch_nze(
    year: int | None = None,
    product: str = "",
    flow: str = "",
    category: str = "",
) -> list[dict]:
    """Fetch Net Zero Emissions by 2050 scenario data."""
    params = {}
    if year is not None:
        params["Year"] = str(year)
    if product:
        params["Product"] = product
    if flow:
        params["Flow"] = flow
    if category:
        params["Category"] = category
    return fetch_iea("nze", params)


# ---------------------------------------------------------------------------
# Display helpers
# ---------------------------------------------------------------------------

def print_table(rows: list[dict], cols: list[str], max_rows: int = 20) -> None:
    """Print a fixed-width table from a list of row dicts."""
    display = rows[:max_rows]
    widths = {}
    for c in cols:
        col_vals = [str(r.get(c, "")) for r in display]
        widths[c] = max(len(c), *(len(v) for v in col_vals)) if col_vals else len(c)
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

    # --- Example 1: Global EV car sales trend ---
    print("=== Global EV Car Sales (BEV + PHEV), Historical ===\n")
    rows = fetch_evs(
        region="World",
        category="Historical",
        parameter="EV sales",
        mode="Cars",
    )
    # Sum BEV + PHEV by year (the "EV" aggregate powertrain is not always present)
    by_year: dict[int, float] = {}
    for r in rows:
        if r["powertrain"] in ("BEV", "PHEV"):
            by_year[r["year"]] = by_year.get(r["year"], 0) + r["value"]
    yearly = [{"year": y, "sales": f"{v:,.0f}", "unit": "Vehicles"}
              for y, v in sorted(by_year.items())]
    print_table(yearly, ["year", "sales", "unit"])

    # --- Example 2: US gasoline transport prices ---
    print("\n=== US Gasoline Prices (Transport Sector, Annual) ===\n")
    rows = fetch_prices(
        country="USA",
        product="GASOLINE",
        sector="TRANS",
        indicator="PRICE",
    )
    rows.sort(key=lambda r: r["CODE_YEAR"], reverse=True)
    for r in rows:
        r["price_str"] = f"{r['Value']:.3f}"
    print_table(rows, ["CODE_YEAR", "price_str", "Unit", "Currency"], max_rows=15)

    # --- Example 3: US CO2 emissions from fuel combustion ---
    print("\n=== US Total CO2 from Fuel Combustion ===\n")
    rows = fetch_ghg(country="USA", product="TOTAL", flow="CO2FUEL")
    rows.sort(key=lambda r: r["TIME"], reverse=True)
    for r in rows:
        r["mt_co2"] = f"{r['VALUE']:,.2f}"
    print_table(rows, ["TIME", "mt_co2", "FLOW"], max_rows=10)

    # --- Example 4: NZE scenario -- oil demand trajectory ---
    print("\n=== NZE Scenario: Oil Demand Trajectory ===\n")
    rows = fetch_nze(product="Oil", flow="Total primary energy demand")
    rows.sort(key=lambda r: r["Year"])
    for r in rows:
        r["value_str"] = f"{r['Value']:.1f}"
    print_table(rows, ["Year", "value_str", "Unit", "Category"])


if __name__ == "__main__":
    main()
