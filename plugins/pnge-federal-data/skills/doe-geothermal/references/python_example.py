#!/usr/bin/env python3
"""
DOE Geothermal Data Client -- stdlib only.

Queries the OpenEI Semantic MediaWiki API for geothermal resource areas.
No third-party dependencies required.

Usage:
    python3 python_example.py                     # List all 432+ areas
    python3 python_example.py --state Nevada      # Filter by state
    python3 python_example.py --min-temp 150      # Filter by min temp (Celsius)
    python3 python_example.py --state Utah --min-temp 100
    python3 python_example.py --region "Basin and Range"
    python3 python_example.py --detail "Cove Fort Geothermal Area"
"""

import json
import sys
import urllib.request
import urllib.parse
import argparse
from typing import Optional


SMW_BASE = "https://openei.org/w/api.php"
KELVIN_OFFSET = 273.15


def smw_ask(query: str, limit: int = 500, offset: int = 0) -> dict:
    """Execute a Semantic MediaWiki ask query and return parsed JSON."""
    full_query = f"{query}|limit={limit}|offset={offset}"
    params = urllib.parse.urlencode({
        "action": "ask",
        "query": full_query,
        "format": "json",
    })
    url = f"{SMW_BASE}?{params}"
    req = urllib.request.Request(url)
    req.add_header("User-Agent", "pnge-geothermal-client/1.0")

    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def smw_browse(subject: str) -> dict:
    """Browse all properties of a single wiki page."""
    params = urllib.parse.urlencode({
        "action": "browsebysubject",
        "subject": subject.replace(" ", "_"),
        "format": "json",
    })
    url = f"{SMW_BASE}?{params}"
    req = urllib.request.Request(url)
    req.add_header("User-Agent", "pnge-geothermal-client/1.0")

    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def fetch_all_areas(
    state: Optional[str] = None,
    region_filter: Optional[str] = None,
) -> list:
    """
    Fetch all geothermal resource areas, optionally filtered by state.

    Returns a list of dicts with keys:
        name, lat, lon, temp_k, temp_c, capacity_mw, volume_km3,
        state, region, url
    """
    conditions = "[[Category:Geothermal Resource Areas]]"
    if state:
        conditions += f"[[Place::{state}]]"

    printouts = (
        "|?Coordinates"
        "|?USGSMeanReservoirTemp"
        "|?USGSMeanCapacity"
        "|?USGSEstReservoirVol"
        "|?Place"
        "|?GeothermalRegion"
    )
    query = conditions + printouts

    all_areas = []
    offset = 0
    while True:
        data = smw_ask(query, limit=500, offset=offset)
        results = data.get("query", {}).get("results", {})

        # Empty results come back as [] instead of {}
        if isinstance(results, list):
            break

        for name, info in results.items():
            pouts = info.get("printouts", {})
            area = parse_area(name, info, pouts)

            # Apply region filter if specified
            if region_filter:
                if region_filter.lower() not in area["region"].lower():
                    continue

            all_areas.append(area)

        # Check for pagination
        cont = data.get("query-continue-offset")
        if cont is None:
            break
        offset = cont

    return all_areas


def parse_area(name: str, info: dict, pouts: dict) -> dict:
    """Parse a single geothermal resource area from SMW printouts."""
    # Coordinates
    coords = pouts.get("Coordinates", [])
    lat = coords[0]["lat"] if coords else None
    lon = coords[0]["lon"] if coords else None

    # Temperature (Kelvin -> Celsius)
    temp_vals = pouts.get("USGSMeanReservoirTemp", [])
    temp_k = temp_vals[0] if temp_vals else None
    temp_c = round(temp_k - KELVIN_OFFSET, 1) if temp_k else None

    # Capacity (parse from string like "4 MW")
    cap_vals = pouts.get("USGSMeanCapacity", [])
    capacity_mw = None
    if cap_vals:
        try:
            capacity_mw = float(cap_vals[0].split()[0])
        except (ValueError, IndexError):
            capacity_mw = None

    # Reservoir volume (parse from string like "1.20 km3")
    vol_vals = pouts.get("USGSEstReservoirVol", [])
    volume_km3 = None
    if vol_vals:
        try:
            volume_km3 = float(vol_vals[0].split()[0])
        except (ValueError, IndexError):
            volume_km3 = None

    # State/Place
    place_vals = pouts.get("Place", [])
    place = ""
    if place_vals and isinstance(place_vals[0], dict):
        place = place_vals[0].get("fulltext", "")
    elif place_vals:
        place = str(place_vals[0])

    # Geothermal Region
    region_vals = pouts.get("GeothermalRegion", [])
    region = ""
    if region_vals and isinstance(region_vals[0], dict):
        region = region_vals[0].get("fulltext", "")
    elif region_vals:
        region = str(region_vals[0])

    return {
        "name": name,
        "lat": lat,
        "lon": lon,
        "temp_k": temp_k,
        "temp_c": temp_c,
        "capacity_mw": capacity_mw,
        "volume_km3": volume_km3,
        "state": place,
        "region": region,
        "url": info.get("fullurl", ""),
    }


def browse_area_detail(area_name: str) -> dict:
    """Get all properties for a specific geothermal area."""
    data = smw_browse(area_name)
    items = data.get("query", {}).get("data", [])
    properties = {}
    for item in items:
        prop = item.get("property", "")
        if prop.startswith("_"):
            continue
        vals = item.get("dataitem", [])
        if vals:
            properties[prop] = [d.get("item", "") for d in vals]
    return properties


def format_table(areas: list) -> str:
    """Format areas as a markdown table."""
    lines = [
        "| Area | State | Lat | Lon | Temp (C) | Capacity (MW) | Volume (km3) | Region |",
        "|------|-------|-----|-----|----------|---------------|--------------|--------|",
    ]
    for a in areas:
        lat_s = f"{a['lat']:.2f}" if a["lat"] else "N/A"
        lon_s = f"{a['lon']:.2f}" if a["lon"] else "N/A"
        temp_s = f"{a['temp_c']:.0f}" if a["temp_c"] else "N/A"
        cap_s = f"{a['capacity_mw']:.0f}" if a["capacity_mw"] else "N/A"
        vol_s = f"{a['volume_km3']:.2f}" if a["volume_km3"] else "N/A"
        region_short = a["region"].replace(" Geothermal Region", "")
        lines.append(
            f"| {a['name'][:40]} | {a['state'][:12]} | {lat_s} | {lon_s} "
            f"| {temp_s} | {cap_s} | {vol_s} | {region_short[:30]} |"
        )
    return "\n".join(lines)


def summarize(areas: list, state: Optional[str] = None) -> str:
    """Generate a narrative summary of the areas."""
    if not areas:
        return "No geothermal resource areas found matching the criteria."

    # Stats
    total = len(areas)
    with_temp = [a for a in areas if a["temp_c"] is not None]
    with_cap = [a for a in areas if a["capacity_mw"] is not None]

    parts = []
    label = f"in {state}" if state else "matching the query"
    parts.append(f"Found {total} geothermal resource areas {label}.")

    if with_temp:
        temps = [a["temp_c"] for a in with_temp]
        parts.append(
            f"Reservoir temperatures range from {min(temps):.0f}C to "
            f"{max(temps):.0f}C (mean {sum(temps)/len(temps):.0f}C)."
        )

    if with_cap:
        caps = [a["capacity_mw"] for a in with_cap]
        total_cap = sum(caps)
        parts.append(
            f"Total estimated capacity: {total_cap:.0f} MW across "
            f"{len(with_cap)} assessed areas."
        )

    # Count by region
    regions = {}
    for a in areas:
        r = a["region"] or "Unknown"
        regions[r] = regions.get(r, 0) + 1
    if len(regions) > 1:
        top_regions = sorted(regions.items(), key=lambda x: -x[1])[:3]
        region_strs = [f"{r} ({n})" for r, n in top_regions]
        parts.append(f"Top regions: {', '.join(region_strs)}.")

    # Li/co-production note for high-temp areas
    hot_areas = [a for a in areas if a["temp_c"] and a["temp_c"] >= 100]
    if hot_areas:
        parts.append(
            f"{len(hot_areas)} areas exceed 100C, potentially viable for "
            f"geothermal power generation and/or lithium co-extraction from "
            f"hot brines."
        )

    return " ".join(parts)


def main():
    parser = argparse.ArgumentParser(
        description="Query OpenEI for geothermal resource areas."
    )
    parser.add_argument(
        "--state",
        type=str,
        default=None,
        help="Filter by state name (e.g., 'Nevada', 'Utah', 'California')",
    )
    parser.add_argument(
        "--min-temp",
        type=float,
        default=None,
        help="Minimum reservoir temperature in Celsius",
    )
    parser.add_argument(
        "--region",
        type=str,
        default=None,
        help="Filter by region name substring (e.g., 'Basin and Range')",
    )
    parser.add_argument(
        "--detail",
        type=str,
        default=None,
        help="Show all properties for a specific area name",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output raw JSON instead of formatted table",
    )
    args = parser.parse_args()

    # Detail mode: browse a single area
    if args.detail:
        props = browse_area_detail(args.detail)
        if not props:
            print(f"No properties found for: {args.detail}")
            print("Try using the full name, e.g., 'Cove Fort Geothermal Area'")
            sys.exit(1)
        print(f"\n## Properties for: {args.detail}\n")
        for prop, vals in sorted(props.items()):
            print(f"  {prop}: {', '.join(str(v) for v in vals)}")
        sys.exit(0)

    # Fetch areas
    print(f"Fetching geothermal resource areas...", file=sys.stderr)
    areas = fetch_all_areas(state=args.state, region_filter=args.region)

    # Apply temperature filter
    if args.min_temp is not None:
        areas = [
            a for a in areas
            if a["temp_c"] is not None and a["temp_c"] >= args.min_temp
        ]

    # Sort by temperature descending (None values last)
    areas.sort(key=lambda a: a["temp_c"] if a["temp_c"] is not None else -999, reverse=True)

    if args.json:
        print(json.dumps(areas, indent=2))
    else:
        title = "Geothermal Resource Areas"
        if args.state:
            title += f" in {args.state}"
        if args.min_temp:
            title += f" (>= {args.min_temp}C)"
        if args.region:
            title += f" ({args.region})"

        print(f"\n## {title}\n")
        print(format_table(areas))
        print(f"\n**Summary:** {summarize(areas, state=args.state)}")
        print(f"\n_Data source: OpenEI / USGS Geothermal Resource Assessment_")
        print(f"_Temperatures are USGS mean reservoir estimates (Kelvin converted to Celsius)_")


if __name__ == "__main__":
    main()
