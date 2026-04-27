#!/usr/bin/env python3
"""eia_client.py — Minimal EIA API v2 client in Python.

Usage:
    python eia_client.py

Credential resolution order:
    1. ~/.config/eia/credentials  (api_key=YOUR_KEY)
    2. EIA_API_KEY env var
    3. Raises RuntimeError with setup instructions
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterator

import requests


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
# Query params
# ---------------------------------------------------------------------------

@dataclass
class QueryParams:
    """Parameters for an EIA v2 data request.

    Attributes:
        route:      API path after /v2/ — must end with /data/
                    e.g. "electricity/retail-sales/data/"
        data_cols:  Value columns to return, e.g. ["price", "sales"]
        facets:     Filters as {facet_name: value},
                    e.g. {"stateid": "TX", "sectorid": "RES"}
        frequency:  "monthly" | "weekly" | "annual" | "hourly" | "quarterly"
        start:      Inclusive start period, e.g. "2023-01"
        end:        Inclusive end period, e.g. "2024-12"
        sort_col:   Column to sort by (default: "period")
        sort_dir:   "asc" | "desc" (default: "desc")
        length:     Rows per page, max 5000 (default: 5000)
        offset:     Pagination offset (default: 0)
    """
    route: str
    data_cols: list[str] = field(default_factory=list)
    facets: dict[str, str] = field(default_factory=dict)
    frequency: str = "monthly"
    start: str = ""
    end: str = ""
    sort_col: str = "period"
    sort_dir: str = "desc"
    length: int = 5000
    offset: int = 0


# ---------------------------------------------------------------------------
# Client
# ---------------------------------------------------------------------------

BASE_URL = "https://api.eia.gov/v2"


class EIAClient:
    """Thin wrapper around the EIA API v2."""

    def __init__(self, api_key: str = "") -> None:
        self.api_key = api_key or resolve_api_key()
        self.session = requests.Session()

    def _build_params(self, p: QueryParams) -> dict[str, Any]:
        params: dict[str, Any] = {
            "api_key": self.api_key,
            "frequency": p.frequency,
            "sort[0][column]": p.sort_col,
            "sort[0][direction]": p.sort_dir,
            "offset": p.offset,
            "length": p.length,
        }
        for col in p.data_cols:
            params.setdefault("data[]", []).append(col)
        for facet, val in p.facets.items():
            params[f"facets[{facet}][]"] = val
        if p.start:
            params["start"] = p.start
        if p.end:
            params["end"] = p.end
        return params

    def fetch(self, p: QueryParams) -> tuple[list[dict], int]:
        """Fetch one page of data.

        Returns:
            (rows, total) where total is the full result count server-side.
        """
        url = f"{BASE_URL}/{p.route.lstrip('/')}"
        resp = self.session.get(url, params=self._build_params(p))
        resp.raise_for_status()

        body = resp.json()
        data = body["response"]

        if warning := data.get("warning"):
            print(f"EIA WARNING: {warning}")

        return data["data"], data["total"]

    def fetch_all(self, p: QueryParams) -> list[dict]:
        """Fetch all pages, returning a flat list of rows."""
        all_rows: list[dict] = []
        p.offset = 0
        p.length = 5000

        while True:
            rows, total = self.fetch(p)
            all_rows.extend(rows)
            p.offset += len(rows)
            if p.offset >= total:
                break

        return all_rows

    def paginate(self, p: QueryParams) -> Iterator[list[dict]]:
        """Yield one page of rows at a time (lazy / memory-efficient)."""
        p.offset = 0
        p.length = 5000

        while True:
            rows, total = self.fetch(p)
            yield rows
            p.offset += len(rows)
            if p.offset >= total:
                break

    def metadata(self, route: str) -> dict:
        """Fetch route metadata (facets, frequencies, date range, child routes)."""
        url = f"{BASE_URL}/{route.rstrip('/').removesuffix('/data')}"
        resp = self.session.get(url, params={"api_key": self.api_key})
        resp.raise_for_status()
        return resp.json()["response"]


# ---------------------------------------------------------------------------
# Example usage
# ---------------------------------------------------------------------------

def print_table(rows: list[dict], cols: list[str], max_rows: int = 20) -> None:
    """Print a fixed-width table from a list of row dicts."""
    widths = {c: max(len(c), *(len(str(r.get(c, ""))) for r in rows[:max_rows])) for c in cols}
    header = "  ".join(c.ljust(widths[c]) for c in cols)
    print(header)
    print("-" * len(header))
    for row in rows[:max_rows]:
        print("  ".join(str(row.get(c, "")).ljust(widths[c]) for c in cols))
    if len(rows) > max_rows:
        print(f"... ({len(rows) - max_rows} more rows)")


def main() -> None:
    client = EIAClient()

    # Example 1: Texas residential electricity prices, last 24 months
    print("=== Texas Residential Electricity Prices (monthly) ===\n")
    rows, total = client.fetch(QueryParams(
        route="electricity/retail-sales/data/",
        data_cols=["price"],
        facets={"stateid": "TX", "sectorid": "RES"},
        frequency="monthly",
        length=24,
    ))
    print(f"Records available: {total}  |  Fetched: {len(rows)}\n")
    print_table(rows, ["period", "price", "price-units"])

    print()

    # Example 2: US weekly natural gas storage (most recent 8 weeks)
    print("=== US Natural Gas Storage (weekly) ===\n")
    rows, total = client.fetch(QueryParams(
        route="natural-gas/stor/sum/data/",
        data_cols=["value"],
        facets={"duoarea": "NUS"},
        frequency="weekly",
        length=8,
    ))
    print(f"Records available: {total}  |  Fetched: {len(rows)}\n")
    print_table(rows, ["period", "value", "value-units"])


if __name__ == "__main__":
    main()
