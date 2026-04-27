#!/usr/bin/env python3
"""usgs_earthquake_client.py — Stdlib-only USGS ComCat earthquake query client.

No dependencies beyond Python 3.9+ standard library.
No API key required.

Usage:
    python python_example.py

Examples cover PNGE-relevant induced seismicity regions:
    - Oklahoma (UIC Class II disposal wells)
    - Permian Basin, TX/NM (saltwater disposal)
    - Appalachian Basin, WV/PA/OH (Marcellus/Utica disposal)
"""

from __future__ import annotations

import json
import urllib.request
import urllib.parse
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

BASE_URL = "https://earthquake.usgs.gov/fdsnws/event/1"

# PNGE-relevant region presets
REGIONS = {
    "oklahoma": {
        "description": "Oklahoma induced seismicity zone (200 km around OKC)",
        "latitude": 35.5,
        "longitude": -97.5,
        "maxradiuskm": 200,
    },
    "permian": {
        "description": "Permian Basin / Delaware Basin (TX/NM)",
        "latitude": 31.8,
        "longitude": -103.5,
        "maxradiuskm": 150,
    },
    "appalachian": {
        "description": "Appalachian Basin (WV/PA/OH bounding box)",
        "minlatitude": 37.0,
        "maxlatitude": 40.5,
        "minlongitude": -82.5,
        "maxlongitude": -77.5,
    },
    "eagle_ford": {
        "description": "Eagle Ford Shale (South TX)",
        "latitude": 28.5,
        "longitude": -98.5,
        "maxradiuskm": 150,
    },
    "raton": {
        "description": "Raton Basin (CO/NM border)",
        "latitude": 37.0,
        "longitude": -104.8,
        "maxradiuskm": 50,
    },
}


# ---------------------------------------------------------------------------
# Query parameters
# ---------------------------------------------------------------------------

@dataclass
class QueryParams:
    """Parameters for a ComCat earthquake query.

    Attributes:
        starttime:      ISO 8601 start (e.g., "2024-01-01")
        endtime:        ISO 8601 end (e.g., "2024-12-31")
        minmagnitude:   Minimum magnitude
        maxmagnitude:   Maximum magnitude (optional)
        mindepth:       Minimum depth in km (optional)
        maxdepth:       Maximum depth in km (optional, use 15 for shallow/induced)
        latitude:       Center latitude for radial search
        longitude:      Center longitude for radial search
        maxradiuskm:    Radius in km for radial search
        minlatitude:    Southern boundary for bounding box
        maxlatitude:    Northern boundary for bounding box
        minlongitude:   Western boundary for bounding box
        maxlongitude:   Eastern boundary for bounding box
        format:         Output format: geojson, csv, text, xml
        limit:          Max events to return (max 20000)
        offset:         Pagination offset (1-based)
        orderby:        Sort: time, time-asc, magnitude, magnitude-asc
        eventtype:      Event type filter (e.g., "earthquake")
        reviewstatus:   "automatic" or "reviewed"
    """
    starttime: str = ""
    endtime: str = ""
    minmagnitude: float | None = None
    maxmagnitude: float | None = None
    mindepth: float | None = None
    maxdepth: float | None = None
    latitude: float | None = None
    longitude: float | None = None
    maxradiuskm: float | None = None
    minlatitude: float | None = None
    maxlatitude: float | None = None
    minlongitude: float | None = None
    maxlongitude: float | None = None
    format: str = "geojson"
    limit: int = 200
    offset: int = 1
    orderby: str = "time"
    eventtype: str = ""
    reviewstatus: str = ""

    def to_params(self) -> dict[str, str]:
        """Convert to URL query parameters, omitting unset values."""
        params: dict[str, str] = {"format": self.format}
        if self.starttime:
            params["starttime"] = self.starttime
        if self.endtime:
            params["endtime"] = self.endtime
        if self.minmagnitude is not None:
            params["minmagnitude"] = str(self.minmagnitude)
        if self.maxmagnitude is not None:
            params["maxmagnitude"] = str(self.maxmagnitude)
        if self.mindepth is not None:
            params["mindepth"] = str(self.mindepth)
        if self.maxdepth is not None:
            params["maxdepth"] = str(self.maxdepth)
        if self.latitude is not None:
            params["latitude"] = str(self.latitude)
        if self.longitude is not None:
            params["longitude"] = str(self.longitude)
        if self.maxradiuskm is not None:
            params["maxradiuskm"] = str(self.maxradiuskm)
        if self.minlatitude is not None:
            params["minlatitude"] = str(self.minlatitude)
        if self.maxlatitude is not None:
            params["maxlatitude"] = str(self.maxlatitude)
        if self.minlongitude is not None:
            params["minlongitude"] = str(self.minlongitude)
        if self.maxlongitude is not None:
            params["maxlongitude"] = str(self.maxlongitude)
        if self.limit:
            params["limit"] = str(self.limit)
        if self.offset > 1:
            params["offset"] = str(self.offset)
        if self.orderby:
            params["orderby"] = self.orderby
        if self.eventtype:
            params["eventtype"] = self.eventtype
        if self.reviewstatus:
            params["reviewstatus"] = self.reviewstatus
        return params


# ---------------------------------------------------------------------------
# Client
# ---------------------------------------------------------------------------

class ComCatClient:
    """Stdlib-only client for USGS ComCat earthquake API."""

    def __init__(self, timeout: int = 30) -> None:
        self.timeout = timeout

    def _get_json(self, endpoint: str, params: dict[str, str]) -> Any:
        """Make a GET request and parse JSON response."""
        qs = urllib.parse.urlencode(params)
        url = f"{BASE_URL}/{endpoint}?{qs}"
        req = urllib.request.Request(url)
        req.add_header("Accept", "application/json")
        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))

    def _get_text(self, endpoint: str, params: dict[str, str]) -> str:
        """Make a GET request and return raw text."""
        qs = urllib.parse.urlencode(params)
        url = f"{BASE_URL}/{endpoint}?{qs}"
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            return resp.read().decode("utf-8")

    def query(self, params: QueryParams) -> dict:
        """Query earthquakes. Returns GeoJSON FeatureCollection."""
        return self._get_json("query", params.to_params())

    def count(self, params: QueryParams) -> int:
        """Count matching earthquakes. Returns integer."""
        p = params.to_params()
        p.pop("format", None)
        p.pop("limit", None)
        p.pop("offset", None)
        p.pop("orderby", None)
        text = self._get_text("count", p)
        return int(text.strip())

    def query_all(self, params: QueryParams, page_size: int = 5000) -> list[dict]:
        """Fetch all matching events with automatic pagination.

        Returns a flat list of GeoJSON feature dicts.
        """
        total = self.count(params)
        if total == 0:
            return []

        all_features: list[dict] = []
        params.limit = min(page_size, 20000)
        params.offset = 1

        while params.offset <= total:
            data = self.query(params)
            features = data.get("features", [])
            all_features.extend(features)
            if len(features) < params.limit:
                break
            params.offset += len(features)

        return all_features

    def query_region(self, region_name: str, starttime: str, endtime: str,
                     minmagnitude: float = 2.0, **kwargs: Any) -> dict:
        """Query a named PNGE region preset.

        Args:
            region_name: Key from REGIONS dict (oklahoma, permian, appalachian, etc.)
            starttime:   ISO date string
            endtime:     ISO date string
            minmagnitude: Minimum magnitude (default 2.0)
            **kwargs:    Additional QueryParams fields to override.

        Returns:
            GeoJSON FeatureCollection.
        """
        if region_name not in REGIONS:
            raise ValueError(
                f"Unknown region '{region_name}'. "
                f"Available: {', '.join(REGIONS.keys())}"
            )
        region = REGIONS[region_name]
        p = QueryParams(
            starttime=starttime,
            endtime=endtime,
            minmagnitude=minmagnitude,
            **{k: v for k, v in region.items() if k != "description"},
            **kwargs,
        )
        return self.query(p)


# ---------------------------------------------------------------------------
# Output formatting
# ---------------------------------------------------------------------------

def ms_to_iso(ms: int) -> str:
    """Convert millisecond Unix timestamp to ISO 8601 string."""
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc).strftime(
        "%Y-%m-%d %H:%M:%S UTC"
    )


def print_earthquake_table(features: list[dict], max_rows: int = 20) -> None:
    """Print a formatted table from GeoJSON features."""
    if not features:
        print("  (no events found)")
        return

    # Table header
    header = f"{'Time (UTC)':<22} {'Mag':>4} {'Depth':>6} {'Place':<45} {'ID':<16}"
    print(header)
    print("-" * len(header))

    for feat in features[:max_rows]:
        props = feat["properties"]
        coords = feat["geometry"]["coordinates"]
        time_str = ms_to_iso(props["time"])[:19]
        mag = f"{props['mag']:.1f}" if props["mag"] is not None else "?"
        depth = f"{coords[2]:.1f}" if len(coords) > 2 else "?"
        place = (props.get("place") or "Unknown")[:45]
        eid = feat.get("id", "?")[:16]
        print(f"{time_str:<22} {mag:>4} {depth:>6} {place:<45} {eid:<16}")

    if len(features) > max_rows:
        print(f"  ... ({len(features) - max_rows} more events)")


def print_summary(features: list[dict], region: str, starttime: str, endtime: str) -> None:
    """Print a narrative summary of earthquake results."""
    if not features:
        print(f"\nNo earthquakes found in {region} from {starttime} to {endtime}.")
        return

    mags = [f["properties"]["mag"] for f in features if f["properties"]["mag"] is not None]
    depths = [f["geometry"]["coordinates"][2] for f in features
              if len(f["geometry"]["coordinates"]) > 2]

    print(f"\n  Region: {region}")
    print(f"  Period: {starttime} to {endtime}")
    print(f"  Total events: {len(features)}")
    if mags:
        print(f"  Magnitude range: M{min(mags):.1f} to M{max(mags):.1f}")
        print(f"  Mean magnitude: M{sum(mags)/len(mags):.2f}")
    if depths:
        print(f"  Depth range: {min(depths):.1f} to {max(depths):.1f} km")
        shallow = sum(1 for d in depths if d < 10)
        print(f"  Shallow events (< 10 km): {shallow} ({100*shallow/len(depths):.0f}%)")


# ---------------------------------------------------------------------------
# Example usage
# ---------------------------------------------------------------------------

def main() -> None:
    client = ComCatClient()

    # --- Example 1: Oklahoma radial search ---
    print("=" * 80)
    print("EXAMPLE 1: Oklahoma Induced Seismicity (M2.5+, 2024)")
    print("  Radial search: 200 km around Oklahoma City")
    print("=" * 80)
    print()

    ok_count = client.count(QueryParams(
        starttime="2024-01-01",
        endtime="2024-12-31",
        minmagnitude=2.5,
        latitude=35.5,
        longitude=-97.5,
        maxradiuskm=200,
    ))
    print(f"  Total M2.5+ events in 2024: {ok_count}")
    print()

    ok_data = client.query(QueryParams(
        starttime="2024-01-01",
        endtime="2024-12-31",
        minmagnitude=2.5,
        latitude=35.5,
        longitude=-97.5,
        maxradiuskm=200,
        limit=15,
        orderby="magnitude",
    ))
    print("  Top 15 by magnitude:")
    print_earthquake_table(ok_data.get("features", []), max_rows=15)
    print_summary(ok_data.get("features", []), "Oklahoma (200 km)", "2024-01-01", "2024-12-31")

    print("\n")

    # --- Example 2: Permian Basin radial search ---
    print("=" * 80)
    print("EXAMPLE 2: Permian Basin Induced Seismicity (M2.0+, 2024)")
    print("  Radial search: 150 km around Pecos, TX")
    print("=" * 80)
    print()

    permian_count = client.count(QueryParams(
        starttime="2024-01-01",
        endtime="2024-12-31",
        minmagnitude=2.0,
        latitude=31.8,
        longitude=-103.5,
        maxradiuskm=150,
    ))
    print(f"  Total M2.0+ events in 2024: {permian_count}")
    print()

    permian_data = client.query(QueryParams(
        starttime="2024-01-01",
        endtime="2024-12-31",
        minmagnitude=2.0,
        latitude=31.8,
        longitude=-103.5,
        maxradiuskm=150,
        limit=10,
        orderby="magnitude",
    ))
    print("  Top 10 by magnitude:")
    print_earthquake_table(permian_data.get("features", []), max_rows=10)
    print_summary(
        permian_data.get("features", []), "Permian Basin (150 km)", "2024-01-01", "2024-12-31"
    )

    print("\n")

    # --- Example 3: Appalachian Basin bounding box ---
    print("=" * 80)
    print("EXAMPLE 3: Appalachian Basin (WV/PA/OH, M1.0+, 2020-2024)")
    print("  Bounding box: 37.0-40.5N, 82.5-77.5W")
    print("=" * 80)
    print()

    app_count = client.count(QueryParams(
        starttime="2020-01-01",
        endtime="2024-12-31",
        minmagnitude=1.0,
        minlatitude=37.0,
        maxlatitude=40.5,
        minlongitude=-82.5,
        maxlongitude=-77.5,
    ))
    print(f"  Total M1.0+ events (2020-2024): {app_count}")
    print()

    app_data = client.query(QueryParams(
        starttime="2020-01-01",
        endtime="2024-12-31",
        minmagnitude=1.0,
        minlatitude=37.0,
        maxlatitude=40.5,
        minlongitude=-82.5,
        maxlongitude=-77.5,
        limit=20,
        orderby="magnitude",
    ))
    print("  Top 20 by magnitude:")
    print_earthquake_table(app_data.get("features", []), max_rows=20)
    print_summary(
        app_data.get("features", []), "Appalachian Basin (WV/PA/OH)", "2020-01-01", "2024-12-31"
    )

    print("\n")

    # --- Example 4: Using region presets ---
    print("=" * 80)
    print("EXAMPLE 4: Region Preset — Eagle Ford Shale (M2.0+, 2023-2024)")
    print("=" * 80)
    print()

    ef_data = client.query_region(
        "eagle_ford",
        starttime="2023-01-01",
        endtime="2024-12-31",
        minmagnitude=2.0,
        limit=10,
    )
    print("  Most recent 10 events:")
    print_earthquake_table(ef_data.get("features", []), max_rows=10)
    print_summary(
        ef_data.get("features", []), "Eagle Ford Shale (150 km)", "2023-01-01", "2024-12-31"
    )

    print("\n")

    # --- Example 5: Shallow events filter (likely injection-induced) ---
    print("=" * 80)
    print("EXAMPLE 5: Shallow Events Only (depth < 10 km) — Oklahoma 2024")
    print("  Shallow depth is a key indicator of injection-induced seismicity")
    print("=" * 80)
    print()

    shallow_data = client.query(QueryParams(
        starttime="2024-01-01",
        endtime="2024-12-31",
        minmagnitude=3.0,
        latitude=35.5,
        longitude=-97.5,
        maxradiuskm=200,
        maxdepth=10,
        limit=20,
        orderby="magnitude",
    ))
    print("  Shallow M3.0+ events (depth < 10 km):")
    print_earthquake_table(shallow_data.get("features", []), max_rows=20)
    print_summary(
        shallow_data.get("features", []),
        "Oklahoma shallow (< 10 km)", "2024-01-01", "2024-12-31"
    )


if __name__ == "__main__":
    main()
