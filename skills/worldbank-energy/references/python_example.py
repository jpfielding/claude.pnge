#!/usr/bin/env python3
"""worldbank_energy.py -- Minimal World Bank Open Data API client (stdlib only).

Usage:
    python worldbank_energy.py

No API key required. All data is publicly accessible.

Queries the World Bank Indicators API v2 for global energy data relevant
to petroleum engineering: generation mix, resource rents, energy intensity,
and fuel trade metrics.
"""

from __future__ import annotations

import json
import time
import urllib.request
import urllib.parse
from dataclasses import dataclass, field


# ---------------------------------------------------------------------------
# Query params
# ---------------------------------------------------------------------------

BASE_URL = "https://api.worldbank.org/v2"


@dataclass
class QueryParams:
    """Parameters for a World Bank indicator data request.

    Attributes:
        indicator:    WDI indicator code, e.g. "NY.GDP.PETR.RT.ZS"
        countries:    Semicolon-separated ISO2 codes or "all" / "WLD"
                      e.g. "US;SA;RU;CN" or "all"
        date_range:   Year range as "YYYY:YYYY", or single year "YYYY",
                      or empty string for all available years.
        per_page:     Results per page (default 1000, max ~1000)
        mrv:          Most Recent Values -- return last N data points.
                      Set to 0 to use date_range instead.
        mrnev:        Most Recent Non-Empty Value (1 = enabled, 0 = disabled).
    """
    indicator: str
    countries: str = "all"
    date_range: str = ""
    per_page: int = 1000
    mrv: int = 0
    mrnev: int = 0


# ---------------------------------------------------------------------------
# Client
# ---------------------------------------------------------------------------

class WorldBankClient:
    """Thin wrapper around the World Bank Indicators API v2 (stdlib only)."""

    def __init__(self, delay: float = 0.1) -> None:
        self.delay = delay  # seconds between paginated requests

    def _build_url(self, p: QueryParams, page: int = 1) -> str:
        """Build the full request URL from query params."""
        path = f"{BASE_URL}/country/{p.countries}/indicator/{p.indicator}"
        params: dict[str, str] = {
            "format": "json",
            "per_page": str(p.per_page),
            "page": str(page),
        }
        if p.date_range:
            params["date"] = p.date_range
        if p.mrv > 0:
            params["MRV"] = str(p.mrv)
        if p.mrnev > 0:
            params["MRNEV"] = str(p.mrnev)
        return f"{path}?{urllib.parse.urlencode(params)}"

    def _get_json(self, url: str) -> list:
        """Fetch URL and parse JSON response."""
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))

    def fetch(self, p: QueryParams) -> tuple[list[dict], dict]:
        """Fetch one page of indicator data.

        Returns:
            (records, pagination_meta)
        """
        url = self._build_url(p)
        data = self._get_json(url)

        # Check for error response
        if isinstance(data, list) and len(data) > 0:
            if isinstance(data[0], dict) and "message" in data[0]:
                msgs = data[0]["message"]
                err = "; ".join(m.get("value", str(m)) for m in msgs)
                raise ValueError(f"API error: {err}")

        meta = data[0] if len(data) > 0 else {}
        records = data[1] if len(data) > 1 and data[1] is not None else []
        return records, meta

    def fetch_all(self, p: QueryParams) -> list[dict]:
        """Fetch all pages and return a flat list of records."""
        all_records: list[dict] = []
        page = 1

        while True:
            url = self._build_url(p, page=page)
            data = self._get_json(url)

            if isinstance(data[0], dict) and "message" in data[0]:
                msgs = data[0]["message"]
                err = "; ".join(m.get("value", str(m)) for m in msgs)
                raise ValueError(f"API error: {err}")

            meta = data[0]
            records = data[1] if data[1] is not None else []
            all_records.extend(records)

            total_pages = meta.get("pages", 1)
            if page >= total_pages:
                break
            page += 1
            time.sleep(self.delay)

        return all_records

    def indicator_metadata(self, indicator_id: str) -> dict:
        """Fetch metadata for a single indicator."""
        url = f"{BASE_URL}/indicator/{indicator_id}?format=json"
        data = self._get_json(url)
        if data[1]:
            return data[1][0]
        return {}

    def country_metadata(self, country_code: str) -> dict:
        """Fetch metadata for a single country."""
        url = f"{BASE_URL}/country/{country_code}?format=json"
        data = self._get_json(url)
        if data[1]:
            return data[1][0]
        return {}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def filter_non_null(records: list[dict]) -> list[dict]:
    """Remove records where value is None."""
    return [r for r in records if r.get("value") is not None]


def sort_by_date_desc(records: list[dict]) -> list[dict]:
    """Sort records by date descending."""
    return sorted(records, key=lambda r: r.get("date", ""), reverse=True)


def sort_by_value_desc(records: list[dict]) -> list[dict]:
    """Sort records by value descending (for rankings)."""
    return sorted(records, key=lambda r: r.get("value", 0) or 0, reverse=True)


def print_table(
    records: list[dict],
    cols: list[tuple[str, str]],
    max_rows: int = 20,
    value_fmt: str = ".2f",
) -> None:
    """Print a formatted table from records.

    Args:
        records:   List of API response records.
        cols:      List of (key_path, header_label) tuples.
                   key_path supports dot notation: "country.value" -> record["country"]["value"]
        max_rows:  Maximum rows to display.
        value_fmt: Format spec for numeric values.
    """
    def get_val(record: dict, key: str) -> str:
        parts = key.split(".")
        obj = record
        for part in parts:
            if isinstance(obj, dict):
                obj = obj.get(part, "")
            else:
                return ""
        if isinstance(obj, float):
            return format(obj, value_fmt)
        return str(obj) if obj is not None else ""

    headers = [label for _, label in cols]
    rows_str = []
    for rec in records[:max_rows]:
        rows_str.append([get_val(rec, key) for key, _ in cols])

    # Calculate column widths
    widths = [len(h) for h in headers]
    for row in rows_str:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(cell))

    # Print
    header_line = "  ".join(h.ljust(widths[i]) for i, h in enumerate(headers))
    print(header_line)
    print("-" * len(header_line))
    for row in rows_str:
        print("  ".join(cell.ljust(widths[i]) for i, cell in enumerate(row)))
    if len(records) > max_rows:
        print(f"... ({len(records) - max_rows} more rows)")


# ---------------------------------------------------------------------------
# Example usage
# ---------------------------------------------------------------------------

def main() -> None:
    client = WorldBankClient()

    # Example 1: Oil rents as % of GDP for major producers (2015-2021)
    print("=== Oil Rents (% of GDP) -- Major Producers, 2015-2021 ===\n")
    records, meta = client.fetch(QueryParams(
        indicator="NY.GDP.PETR.RT.ZS",
        countries="US;SA;RU;CN;CA;IQ;AE;NO",
        date_range="2015:2021",
        per_page=1000,
    ))
    records = filter_non_null(records)
    # Show most recent year per country
    latest: dict[str, dict] = {}
    for r in sort_by_date_desc(records):
        cid = r["country"]["id"]
        if cid not in latest:
            latest[cid] = r
    ranked = sort_by_value_desc(list(latest.values()))
    print(f"Records: {meta.get('total', '?')}  |  Last updated: {meta.get('lastupdated', '?')}\n")
    print_table(ranked, [
        ("country.value", "Country"),
        ("date", "Year"),
        ("value", "Oil Rents (% GDP)"),
    ])

    print()

    # Example 2: US electricity generation mix over time
    print("=== US Electricity Generation Mix (% of total), 2015-2022 ===\n")
    indicators = {
        "EG.ELC.NGAS.ZS": "Natural Gas",
        "EG.ELC.COAL.ZS": "Coal",
        "EG.ELC.NUCL.ZS": "Nuclear",
        "EG.ELC.PETR.ZS": "Oil",
        "EG.ELC.HYRO.ZS": "Hydro",
        "EG.ELC.RNWX.ZS": "Renewables (excl. hydro)",
    }
    mix_by_year: dict[str, dict[str, float]] = {}
    for ind_id, label in indicators.items():
        records, _ = client.fetch(QueryParams(
            indicator=ind_id,
            countries="US",
            date_range="2015:2022",
        ))
        for r in records:
            if r["value"] is not None:
                yr = r["date"]
                mix_by_year.setdefault(yr, {})[label] = r["value"]
        time.sleep(0.1)

    # Print as table
    fuels = list(indicators.values())
    header = f"{'Year':<6}" + "".join(f"{f:>16}" for f in fuels)
    print(header)
    print("-" * len(header))
    for yr in sorted(mix_by_year.keys(), reverse=True):
        row = f"{yr:<6}"
        for fuel in fuels:
            val = mix_by_year[yr].get(fuel)
            row += f"{val:>15.1f}%" if val is not None else f"{'N/A':>16}"
        print(row)

    print()

    # Example 3: Energy use per capita -- top 10 countries (most recent)
    print("=== Energy Use Per Capita (kg oil equiv) -- Top 10 Countries ===\n")
    all_records = client.fetch_all(QueryParams(
        indicator="EG.USE.PCAP.KG.OE",
        countries="all",
        mrv=1,
    ))
    # Filter to actual countries (exclude aggregates: codes with numbers or length != 3 iso3)
    countries_only = [
        r for r in filter_non_null(all_records)
        if len(r.get("countryiso3code", "")) == 3
        and r["countryiso3code"].isalpha()
    ]
    top10 = sort_by_value_desc(countries_only)[:10]
    print_table(top10, [
        ("country.value", "Country"),
        ("countryiso3code", "ISO3"),
        ("date", "Year"),
        ("value", "kg OE / capita"),
    ], value_fmt=".0f")

    print()

    # Example 4: Natural gas rents -- OPEC+ comparison
    print("=== Natural Gas Rents (% of GDP) -- Key Gas Exporters ===\n")
    records, meta = client.fetch(QueryParams(
        indicator="NY.GDP.NGAS.RT.ZS",
        countries="QA;RU;IR;US;NO;DZ;AU;SA;CA;MY",
        date_range="2019:2021",
    ))
    records = filter_non_null(records)
    latest = {}
    for r in sort_by_date_desc(records):
        cid = r["country"]["id"]
        if cid not in latest:
            latest[cid] = r
    ranked = sort_by_value_desc(list(latest.values()))
    print_table(ranked, [
        ("country.value", "Country"),
        ("date", "Year"),
        ("value", "Gas Rents (% GDP)"),
    ])


if __name__ == "__main__":
    main()
