#!/usr/bin/env python3
"""
PA Mineral Parcel and Well Correlation Client

Queries PA DEP ArcGIS REST services to find parcels near active unconventional
wells and identify potential mineral interest indicators:
  1. PA DEP Parcels — 4.6M parcels with owner names and acreage
  2. PA DEP Oil/Gas Wells — 223K wells with status and operator data
  3. PASDA Parcels — polygon geometry for spatial queries

Uses only Python stdlib (urllib, json, ssl, argparse) — no third-party packages.

Usage:
    python python_example.py --county Greene                         # Parcels in Greene County
    python python_example.py --county Washington --owner "%EQT%"     # EQT-owned parcels
    python python_example.py --county Greene --near-wells             # Parcels near active unconventional wells
    python python_example.py --wells --county Greene                  # Active unconventional wells in county
    python python_example.py --wells --radius 2 --lat 39.9 --lon -80.2  # Wells within 2 miles of point
    python python_example.py --count --county Washington              # Count parcels in county
    python python_example.py --well-stats --county Greene             # Well counts by status
"""

import argparse
import json
import ssl
import sys
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Optional

# --- Endpoints ---

PA_PARCELS_URL = (
    "https://gis.dep.pa.gov/depgisprd/rest/services"
    "/Parcels/PA_Parcels/MapServer/0"
)

PA_WELLS_URL = (
    "https://gis.dep.pa.gov/depgisprd/rest/services"
    "/OilGas/OilGasAllStrayGasEGSP/MapServer/3"
)

PA_WELLS_UNCONV_URL = (
    "https://gis.dep.pa.gov/depgisprd/rest/services"
    "/OilGas/OilGasAllStrayGasEGSP/MapServer/1"
)

PASDA_PARCELS_URL = (
    "https://apps.pasda.psu.edu/arcgis/rest/services"
    "/PA_Parcels/MapServer/1"
)

# Server record limits
PARCELS_MAX = 1000
WELLS_MAX = 5000

# Default output fields
PARCEL_FIELDS = (
    "PARCEL_ID,OWNER_NAME,OWNER_LAST_NAME,OWNER_FIRST_NAME,"
    "PROPERTY_ADDRESS_1,CITY,COUNTY_NAME,COUNTY_CODE,DISTRICT,ACREAGE"
)

WELL_FIELDS = (
    "PERMIT_NUMBER,WELL_NAME,OPERATOR,WELL_TYPE,WELL_STATUS,"
    "COUNTY,MUNICIPALITY,LATITUDE,LONGITUDE,UNCONVENTIONAL_IND,"
    "WELL_CONFIG_CODE"
)

# SSL context — PA DEP has valid certs
_ssl_ctx = ssl.create_default_context()


def _post_query(
    base_url: str, params: Dict[str, str], ctx: Optional[ssl.SSLContext] = None
) -> Dict[str, Any]:
    """POST a query to an ArcGIS REST endpoint and return parsed JSON."""
    if ctx is None:
        ctx = _ssl_ctx
    params["f"] = "json"
    data = urllib.parse.urlencode(params).encode("utf-8")
    req = urllib.request.Request(base_url + "/query", data=data, method="POST")
    with urllib.request.urlopen(req, context=ctx) as resp:
        body = json.loads(resp.read().decode("utf-8"))
    if "error" in body:
        raise RuntimeError(
            f"ArcGIS error {body['error'].get('code')}: "
            f"{body['error'].get('message')}"
        )
    return body


# ---- Parcels ----


def count_parcels(where: str = "1=1") -> int:
    """Count PA DEP parcels matching WHERE clause."""
    result = _post_query(
        PA_PARCELS_URL, {"where": where, "returnCountOnly": "true"}
    )
    return result.get("count", 0)


def query_parcels(
    where: str = "1=1",
    out_fields: str = PARCEL_FIELDS,
    max_records: int = 100,
    return_geometry: bool = False,
) -> List[Dict[str, Any]]:
    """Query PA DEP parcels with pagination."""
    all_features: List[Dict[str, Any]] = []
    offset = 0

    while offset < max_records:
        batch = min(PARCELS_MAX, max_records - offset)
        params: Dict[str, str] = {
            "where": where,
            "outFields": out_fields,
            "returnGeometry": "true" if return_geometry else "false",
            "resultRecordCount": str(batch),
            "resultOffset": str(offset),
        }
        if return_geometry:
            params["outSR"] = "4326"

        result = _post_query(PA_PARCELS_URL, params)
        features = result.get("features", [])
        all_features.extend(features)

        if len(features) < batch or not result.get("exceededTransferLimit"):
            break
        offset += batch

    return all_features


# ---- Wells ----


def count_wells(where: str = "1=1", layer_url: str = PA_WELLS_URL) -> int:
    """Count PA DEP wells matching WHERE clause."""
    result = _post_query(
        layer_url, {"where": where, "returnCountOnly": "true"}
    )
    return result.get("count", 0)


def query_wells(
    where: str = "1=1",
    out_fields: str = WELL_FIELDS,
    max_records: int = 100,
    layer_url: str = PA_WELLS_URL,
    return_geometry: bool = False,
) -> List[Dict[str, Any]]:
    """Query PA DEP wells with pagination."""
    all_features: List[Dict[str, Any]] = []
    offset = 0

    while offset < max_records:
        batch = min(WELLS_MAX, max_records - offset)
        params: Dict[str, str] = {
            "where": where,
            "outFields": out_fields,
            "returnGeometry": "true" if return_geometry else "false",
            "resultRecordCount": str(batch),
            "resultOffset": str(offset),
        }
        if return_geometry:
            params["outSR"] = "4326"

        result = _post_query(layer_url, params)
        features = result.get("features", [])
        all_features.extend(features)

        if len(features) < batch or not result.get("exceededTransferLimit"):
            break
        offset += batch

    return all_features


def find_wells_near_point(
    lon: float, lat: float, radius_miles: float = 1.0,
    where: str = "WELL_STATUS='Active' AND UNCONVENTIONAL_IND='Yes'",
) -> List[Dict[str, Any]]:
    """Find PA DEP wells within radius_miles of a point (WGS84)."""
    params: Dict[str, str] = {
        "geometry": f"{lon},{lat}",
        "geometryType": "esriGeometryPoint",
        "inSR": "4326",
        "spatialRel": "esriSpatialRelIntersects",
        "distance": str(radius_miles * 1609.34),  # miles to meters
        "units": "esriSRUnit_Meter",
        "where": where,
        "outFields": WELL_FIELDS,
        "returnGeometry": "false",
        "resultRecordCount": "50",
    }
    result = _post_query(PA_WELLS_URL, params)
    return [f["attributes"] for f in result.get("features", [])]


def aggregate_wells(
    where: str = "1=1",
    group_by: str = "COUNTY",
    layer_url: str = PA_WELLS_URL,
) -> List[Dict[str, Any]]:
    """Run a GROUP BY aggregation query on wells."""
    stats = json.dumps([{
        "statisticType": "count",
        "onStatisticField": "OBJECTID",
        "outStatisticFieldName": "cnt",
    }])
    params: Dict[str, str] = {
        "where": where,
        "groupByFieldsForStatistics": group_by,
        "outStatistics": stats,
        "orderByFields": "cnt DESC",
    }
    result = _post_query(layer_url, params)
    return [f["attributes"] for f in result.get("features", [])]


# ---- Cross-reference: Parcels Near Wells ----


def parcels_near_active_wells(
    county: str,
    radius_miles: float = 1.0,
    max_wells: int = 20,
    max_parcels_per_well: int = 50,
) -> List[Dict[str, Any]]:
    """
    Find parcels near active unconventional wells in a county.

    Workflow:
    1. Query active unconventional wells in the county (with coordinates)
    2. For each well, query nearby parcels
    3. Deduplicate parcels and annotate with nearest well info
    """
    # Step 1: Get active unconventional wells with coordinates
    well_where = (
        f"COUNTY='{county}' AND WELL_STATUS='Active' "
        f"AND UNCONVENTIONAL_IND='Yes'"
    )
    well_features = query_wells(
        where=well_where,
        out_fields=WELL_FIELDS,
        max_records=max_wells,
        return_geometry=False,
    )
    wells = [f["attributes"] for f in well_features]

    if not wells:
        print(f"No active unconventional wells found in {county} County.")
        return []

    print(f"Found {len(wells)} active unconventional wells in {county} County.")
    print(f"Searching for parcels within {radius_miles} mile(s) of each well...\n")

    # Step 2: For each well, find nearby parcels
    seen_parcels: Dict[str, Dict[str, Any]] = {}
    radius_m = radius_miles * 1609.34

    for well in wells:
        lon = well.get("LONGITUDE")
        lat = well.get("LATITUDE")
        if lon is None or lat is None:
            continue

        params: Dict[str, str] = {
            "geometry": f"{lon},{lat}",
            "geometryType": "esriGeometryPoint",
            "inSR": "4326",
            "spatialRel": "esriSpatialRelIntersects",
            "distance": str(radius_m),
            "units": "esriSRUnit_Meter",
            "where": f"COUNTY_NAME='{county}'",
            "outFields": PARCEL_FIELDS,
            "returnGeometry": "false",
            "resultRecordCount": str(max_parcels_per_well),
        }
        result = _post_query(PA_PARCELS_URL, params)
        for feat in result.get("features", []):
            attrs = feat["attributes"]
            pid = attrs.get("PARCEL_ID", "")
            if pid and pid not in seen_parcels:
                attrs["_nearest_well"] = well.get("PERMIT_NUMBER", "")
                attrs["_well_operator"] = well.get("OPERATOR", "")
                attrs["_well_name"] = well.get("WELL_NAME", "")
                seen_parcels[pid] = attrs

    return list(seen_parcels.values())


# ---- Output ----


def print_table(
    records: List[Dict[str, Any]], fields: Optional[List[str]] = None
) -> None:
    """Print records as a formatted text table."""
    if not records:
        print("No records found.")
        return

    if fields is None:
        fields = list(records[0].keys())
    # Remove internal fields from display
    fields = [f for f in fields if not f.startswith("_")]

    widths = {f: len(f) for f in fields}
    for rec in records:
        for f in fields:
            val = str(rec.get(f, ""))
            widths[f] = max(widths[f], min(len(val), 40))

    header = " | ".join(f.ljust(widths[f]) for f in fields)
    print(header)
    print("-+-".join("-" * widths[f] for f in fields))

    for rec in records:
        row = " | ".join(
            str(rec.get(f, ""))[:40].ljust(widths[f]) for f in fields
        )
        print(row)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Query PA parcels and wells for mineral interest analysis"
    )

    # Parcel options
    parser.add_argument("--county", help="County name (e.g., Greene, Washington)")
    parser.add_argument("--owner", help="Owner name pattern (SQL LIKE, e.g., '%%EQT%%')")

    # Well options
    parser.add_argument("--wells", action="store_true", help="Query wells instead of parcels")
    parser.add_argument("--well-stats", action="store_true", help="Well count by status/county")
    parser.add_argument("--lat", type=float, help="Latitude for radius search")
    parser.add_argument("--lon", type=float, help="Longitude for radius search")
    parser.add_argument("--radius", type=float, default=1.0, help="Search radius in miles (default: 1.0)")

    # Cross-reference
    parser.add_argument("--near-wells", action="store_true", help="Find parcels near active unconventional wells")

    # General options
    parser.add_argument("--count", action="store_true", help="Return count only")
    parser.add_argument("--limit", type=int, default=100, help="Max records (default: 100)")
    parser.add_argument("--json-output", action="store_true", help="Output raw JSON")
    parser.add_argument("--where", help="Raw SQL WHERE clause (overrides filters)")

    args = parser.parse_args()

    # --- Well statistics ---
    if args.well_stats:
        group_by = "WELL_STATUS"
        where = "1=1"
        if args.county:
            where = f"COUNTY='{args.county}'"
        results = aggregate_wells(where=where, group_by=group_by)
        if args.json_output:
            json.dump(results, sys.stdout, indent=2)
            print()
        else:
            label = f" in {args.county} County" if args.county else " statewide"
            print(f"\nWell counts by {group_by}{label}:\n")
            print_table(results)
            total = sum(r["cnt"] for r in results)
            print(f"\nTotal: {total:,}")
        return

    # --- Well queries ---
    if args.wells:
        # Radius search around a point
        if args.lat is not None and args.lon is not None:
            wells = find_wells_near_point(
                args.lon, args.lat, args.radius,
                where="WELL_STATUS='Active' AND UNCONVENTIONAL_IND='Yes'",
            )
            if args.json_output:
                json.dump(wells, sys.stdout, indent=2)
                print()
            else:
                print(
                    f"\nActive unconventional wells within {args.radius} mile(s) "
                    f"of ({args.lat}, {args.lon}):\n"
                )
                print_table(wells)
            return

        # County-based well query
        if not args.county and not args.where:
            parser.error("--wells requires --county, --where, or --lat/--lon")

        if args.where:
            where = args.where
        else:
            where = f"COUNTY='{args.county}' AND WELL_STATUS='Active'"

        if args.count:
            total = count_wells(where)
            print(f"Matching wells: {total:,}")
            return

        features = query_wells(
            where=where, max_records=args.limit, return_geometry=False
        )
        records = [f["attributes"] for f in features]
        total = count_wells(where)

        if args.json_output:
            json.dump(records, sys.stdout, indent=2)
            print()
        else:
            print(f"\nShowing {len(records)} of {total:,} matching wells:\n")
            print_table(records)
        return

    # --- Parcels near active wells ---
    if args.near_wells:
        if not args.county:
            parser.error("--near-wells requires --county")

        parcels = parcels_near_active_wells(
            county=args.county,
            radius_miles=args.radius,
            max_wells=min(args.limit, 20),
        )
        if args.json_output:
            json.dump(parcels, sys.stdout, indent=2)
            print()
        else:
            print(
                f"\n{len(parcels)} unique parcels within {args.radius} mile(s) "
                f"of active unconventional wells in {args.county} County:\n"
            )
            print_table(parcels)
            # Print well association summary
            if parcels:
                print(f"\nNote: Parcels annotated with nearest well permit number.")
                print("Use county assessment records to determine mineral ownership.")
        return

    # --- Parcel queries ---
    if not args.county and not args.where:
        parser.error("Specify --county, --where, --wells, or --near-wells")

    # Build WHERE clause
    if args.where:
        where = args.where
    else:
        clauses = []
        if args.county:
            clauses.append(f"COUNTY_NAME='{args.county}'")
        if args.owner:
            clauses.append(f"OWNER_NAME LIKE '{args.owner}'")
        where = " AND ".join(clauses) if clauses else "1=1"

    # Count mode
    if args.count:
        total = count_parcels(where)
        print(f"Matching parcels: {total:,}")
        return

    # Standard parcel query
    features = query_parcels(
        where=where, max_records=args.limit, return_geometry=False
    )
    records = [f["attributes"] for f in features]
    total = count_parcels(where)

    if args.json_output:
        json.dump(records, sys.stdout, indent=2)
        print()
    else:
        print(f"\nShowing {len(records)} of {total:,} matching parcels (where: {where}):\n")
        display_fields = PARCEL_FIELDS.split(",")
        print_table(records, fields=display_fields)


if __name__ == "__main__":
    main()
