#!/usr/bin/env python3
"""fred_client.py -- Minimal FRED API client using only the Python standard library.

Usage:
    python fred_client.py

Credential resolution order:
    1. ~/.config/fred/credentials  (api_key=YOUR_KEY)
    2. FRED_API_KEY env var
    3. Raises RuntimeError with setup instructions

No third-party dependencies required.
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterator


# ---------------------------------------------------------------------------
# Credential resolution
# ---------------------------------------------------------------------------

def resolve_api_key() -> str:
    """Resolve FRED API key from credentials file or env var."""
    creds_path = Path.home() / ".config" / "fred" / "credentials"
    if creds_path.exists():
        for line in creds_path.read_text().splitlines():
            line = line.strip()
            if line.startswith("api_key="):
                return line.removeprefix("api_key=")

    key = os.environ.get("FRED_API_KEY", "")
    if key:
        return key

    raise RuntimeError(
        "No FRED API key found. Store it in ~/.config/fred/credentials as:\n"
        "  api_key=YOUR_KEY\n"
        "Or set the FRED_API_KEY environment variable.\n"
        "Get a free key at https://fred.stlouisfed.org/docs/api/api_key.html"
    )


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class Observation:
    """A single FRED observation (date + value)."""
    date: str
    value: str  # String because FRED returns "." for missing values

    @property
    def is_missing(self) -> bool:
        return self.value == "."

    @property
    def numeric(self) -> float:
        """Return value as float. Raises ValueError if missing."""
        if self.is_missing:
            raise ValueError(f"Missing observation on {self.date}")
        return float(self.value)


@dataclass
class SeriesInfo:
    """Metadata for a FRED series."""
    id: str
    title: str
    frequency: str
    units: str
    observation_start: str
    observation_end: str
    last_updated: str
    popularity: int
    notes: str = ""


@dataclass
class ObservationParams:
    """Parameters for a series/observations request.

    Attributes:
        series_id:          FRED series identifier (e.g., "DCOILWTICO")
        observation_start:  Start date YYYY-MM-DD (default: 1 year ago)
        observation_end:    End date YYYY-MM-DD (default: today)
        frequency:          Aggregation: d, w, bw, m, q, sa, a (default: native)
        aggregation_method: avg, sum, eop (default: avg)
        units:              lin, chg, ch1, pch, pc1, pca, cch, cca, log
        sort_order:         asc or desc (default: asc)
        limit:              Max observations (max 100000, default 100000)
        offset:             Pagination offset (default 0)
    """
    series_id: str
    observation_start: str = ""
    observation_end: str = ""
    frequency: str = ""
    aggregation_method: str = ""
    units: str = ""
    sort_order: str = "asc"
    limit: int = 100000
    offset: int = 0


# ---------------------------------------------------------------------------
# Client
# ---------------------------------------------------------------------------

BASE_URL = "https://api.stlouisfed.org/fred"


class FREDClient:
    """Thin wrapper around the FRED API using only urllib."""

    def __init__(self, api_key: str = "") -> None:
        self.api_key = api_key or resolve_api_key()

    def _get(self, endpoint: str, params: dict[str, Any]) -> dict:
        """Execute a GET request and return parsed JSON."""
        params["api_key"] = self.api_key
        params["file_type"] = "json"

        # Remove empty string values
        params = {k: v for k, v in params.items() if v != ""}

        url = f"{BASE_URL}/{endpoint}?{urllib.parse.urlencode(params)}"

        req = urllib.request.Request(url)
        req.add_header("User-Agent", "fred-skill-client/1.0")

        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                body = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8", errors="replace")
            raise RuntimeError(
                f"FRED API returned HTTP {e.code}: {error_body}"
            ) from e
        except urllib.error.URLError as e:
            raise RuntimeError(f"Network error: {e.reason}") from e

        # Check for API-level errors
        if "error_code" in body:
            raise RuntimeError(
                f"FRED API error {body['error_code']}: {body.get('error_message', '')}"
            )

        return body

    def series_info(self, series_id: str) -> SeriesInfo:
        """Get metadata for a single series."""
        body = self._get("series", {"series_id": series_id})
        s = body["seriess"][0]
        return SeriesInfo(
            id=s["id"],
            title=s["title"],
            frequency=s.get("frequency_short", s.get("frequency", "")),
            units=s.get("units_short", s.get("units", "")),
            observation_start=s.get("observation_start", ""),
            observation_end=s.get("observation_end", ""),
            last_updated=s.get("last_updated", ""),
            popularity=s.get("popularity", 0),
            notes=s.get("notes", ""),
        )

    def observations(self, p: ObservationParams) -> tuple[list[Observation], int]:
        """Fetch observations for a series.

        Returns:
            (observations, total_count)
        """
        params: dict[str, Any] = {
            "series_id": p.series_id,
            "observation_start": p.observation_start,
            "observation_end": p.observation_end,
            "frequency": p.frequency,
            "aggregation_method": p.aggregation_method,
            "units": p.units,
            "sort_order": p.sort_order,
            "limit": p.limit,
            "offset": p.offset,
        }

        body = self._get("series/observations", params)

        obs = [
            Observation(date=o["date"], value=o["value"])
            for o in body.get("observations", [])
        ]

        count = body.get("count", len(obs))
        return obs, count

    def observations_numeric(self, p: ObservationParams) -> list[tuple[str, float]]:
        """Fetch observations, filtering out missing values and converting to float.

        Returns:
            List of (date, value) tuples with only valid numeric observations.
        """
        obs, _ = self.observations(p)
        return [(o.date, o.numeric) for o in obs if not o.is_missing]

    def fetch_all(self, p: ObservationParams) -> list[Observation]:
        """Fetch all pages of observations, returning a flat list."""
        all_obs: list[Observation] = []
        p.offset = 0
        p.limit = 100000

        while True:
            obs, count = self.observations(p)
            all_obs.extend(obs)
            p.offset += len(obs)
            if p.offset >= count:
                break

        return all_obs

    def paginate(self, p: ObservationParams) -> Iterator[list[Observation]]:
        """Yield one page of observations at a time (lazy)."""
        p.offset = 0
        p.limit = 100000

        while True:
            obs, count = self.observations(p)
            yield obs
            p.offset += len(obs)
            if p.offset >= count:
                break

    def search(
        self,
        search_text: str,
        order_by: str = "popularity",
        limit: int = 10,
    ) -> list[SeriesInfo]:
        """Search for series by keyword."""
        body = self._get("series/search", {
            "search_text": search_text,
            "order_by": order_by,
            "sort_order": "desc",
            "limit": limit,
        })

        results = []
        for s in body.get("seriess", []):
            results.append(SeriesInfo(
                id=s["id"],
                title=s["title"],
                frequency=s.get("frequency_short", ""),
                units=s.get("units_short", ""),
                observation_start=s.get("observation_start", ""),
                observation_end=s.get("observation_end", ""),
                last_updated=s.get("last_updated", ""),
                popularity=s.get("popularity", 0),
                notes=s.get("notes", ""),
            ))

        return results


# ---------------------------------------------------------------------------
# Display helpers
# ---------------------------------------------------------------------------

def print_table(
    rows: list[tuple[str, ...]],
    headers: tuple[str, ...],
    max_rows: int = 20,
) -> None:
    """Print a fixed-width table."""
    all_rows = [headers] + rows[:max_rows]
    widths = [
        max(len(str(row[i])) for row in all_rows)
        for i in range(len(headers))
    ]

    header_line = "  ".join(h.ljust(w) for h, w in zip(headers, widths))
    print(header_line)
    print("-" * len(header_line))
    for row in rows[:max_rows]:
        print("  ".join(str(v).ljust(w) for v, w in zip(row, widths)))
    if len(rows) > max_rows:
        print(f"... ({len(rows) - max_rows} more rows)")


def summary_stats(values: list[float]) -> dict[str, float]:
    """Compute basic summary statistics from a list of floats."""
    if not values:
        return {}
    n = len(values)
    mean = sum(values) / n
    sorted_vals = sorted(values)
    median = sorted_vals[n // 2] if n % 2 else (sorted_vals[n // 2 - 1] + sorted_vals[n // 2]) / 2
    return {
        "count": n,
        "min": min(values),
        "max": max(values),
        "mean": round(mean, 2),
        "median": round(median, 2),
        "first": values[0],
        "last": values[-1],
        "change": round(values[-1] - values[0], 2),
        "pct_change": round(((values[-1] / values[0]) - 1) * 100, 2) if values[0] != 0 else 0,
    }


# ---------------------------------------------------------------------------
# Example usage
# ---------------------------------------------------------------------------

def main() -> None:
    client = FREDClient()

    # Example 1: WTI crude oil -- last 20 trading days
    print("=== WTI Crude Oil Spot Price (recent) ===\n")
    info = client.series_info("DCOILWTICO")
    print(f"Series: {info.id} -- {info.title}")
    print(f"Units: {info.units}  |  Frequency: {info.frequency}")
    print(f"Last updated: {info.last_updated}\n")

    data = client.observations_numeric(ObservationParams(
        series_id="DCOILWTICO",
        sort_order="desc",
        limit=20,
    ))

    rows = [(d, f"{v:.2f}") for d, v in data]
    print_table(rows, ("Date", "Price ($/bbl)"))

    values = [v for _, v in data]
    if values:
        stats = summary_stats(list(reversed(values)))  # chronological for stats
        print(f"\nRange: ${stats['min']:.2f} - ${stats['max']:.2f}")
        print(f"Average: ${stats['mean']:.2f}")
        print(f"Change over period: ${stats['change']:.2f} ({stats['pct_change']:.1f}%)")

    print()

    # Example 2: Henry Hub natural gas -- last 20 trading days
    print("=== Henry Hub Natural Gas Spot Price (recent) ===\n")
    data = client.observations_numeric(ObservationParams(
        series_id="DHHNGSP",
        sort_order="desc",
        limit=20,
    ))

    rows = [(d, f"{v:.2f}") for d, v in data]
    print_table(rows, ("Date", "Price ($/MMBtu)"))

    print()

    # Example 3: WTI monthly averages for the past 12 months
    print("=== WTI Monthly Averages (last 12 months) ===\n")
    data = client.observations_numeric(ObservationParams(
        series_id="DCOILWTICO",
        frequency="m",
        aggregation_method="avg",
        sort_order="desc",
        limit=12,
    ))

    rows = [(d, f"{v:.2f}") for d, v in data]
    print_table(rows, ("Month", "Avg Price ($/bbl)"))

    print()

    # Example 4: Search for lithium-related series
    print("=== FRED Series Search: 'lithium' ===\n")
    results = client.search("lithium", limit=5)
    if results:
        search_rows = [
            (r.id, r.title[:60], r.frequency, r.units)
            for r in results
        ]
        print_table(search_rows, ("ID", "Title", "Freq", "Units"))
    else:
        print("No series found matching 'lithium'.")

    print()

    # Example 5: WTI year-over-year percent change (monthly)
    print("=== WTI Year-over-Year % Change (monthly, last 12) ===\n")
    data = client.observations_numeric(ObservationParams(
        series_id="MCOILWTICO",
        units="pc1",
        sort_order="desc",
        limit=12,
    ))

    rows = [(d, f"{v:+.1f}%") for d, v in data]
    print_table(rows, ("Month", "YoY Change"))


if __name__ == "__main__":
    main()
