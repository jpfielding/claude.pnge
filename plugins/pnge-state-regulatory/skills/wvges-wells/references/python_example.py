#!/usr/bin/env python3
"""
WVDEP Oil and Gas Well Query Client

Queries the WVDEP ArcGIS REST MapServer for WV oil and gas well data.
Uses only Python stdlib (urllib, json) — no third-party packages required.

Usage:
    python python_example.py --county 049              # Wells in Marshall County
    python python_example.py --status "Active Well"    # Active wells statewide
    python python_example.py --formation "Marcellus"   # Marcellus wells
    python python_example.py --operator "EQT"          # Wells by operator
    python python_example.py --bbox -80.2,39.5,-79.8,39.8  # Spatial bounding box (lon,lat)
    python python_example.py --where "marcellus='y' AND wellstatus='Active Well'"
    python python_example.py --count --county 085      # Count only
    python python_example.py --stats county             # Aggregate by county
"""

import argparse
import json
import sys
import ssl
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Optional

BASE_URL = (
    "https://tagis.dep.wv.gov/arcgis/rest/services"
    "/WVDEP_enterprise/oil_gas/MapServer"
)
LAYER_ALL_WELLS = 7
MAX_RECORDS = 3000  # Server-enforced limit per request

# Default fields to return (omit geometry-related and internal fields)
DEFAULT_FIELDS = (
    "permitid,api,county,welltype,welluse,welldepth,permittype,"
    "issuedate,compdate,respparty,wellstatus,farmname,wellnumber,"
    "formation,marcellus"
)

# SSL context that accepts the WVDEP certificate
_ssl_ctx = ssl.create_default_context()
_ssl_ctx.check_hostname = False
_ssl_ctx.verify_mode = ssl.CERT_NONE


def _post_query(layer_id: int, params: Dict[str, str]) -> Dict[str, Any]:
    """POST a query to the ArcGIS REST MapServer and return parsed JSON."""
    url = f"{BASE_URL}/{layer_id}/query"
    params["f"] = "json"
    data = urllib.parse.urlencode(params).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST")
    with urllib.request.urlopen(req, context=_ssl_ctx) as resp:
        body = json.loads(resp.read().decode("utf-8"))
    if "error" in body:
        raise RuntimeError(
            f"ArcGIS error {body['error'].get('code')}: "
            f"{body['error'].get('message')}"
        )
    return body


def count_wells(where: str = "1=1", layer_id: int = LAYER_ALL_WELLS) -> int:
    """Return the total number of features matching the WHERE clause."""
    result = _post_query(layer_id, {"where": where, "returnCountOnly": "true"})
    return result.get("count", 0)


def query_wells(
    where: str = "1=1",
    out_fields: str = DEFAULT_FIELDS,
    max_records: int = 100,
    layer_id: int = LAYER_ALL_WELLS,
    bbox: Optional[str] = None,
    return_geometry: bool = False,
) -> List[Dict[str, Any]]:
    """
    Query wells and return a list of attribute dictionaries.

    Handles pagination automatically if max_records > MAX_RECORDS.
    """
    all_features: List[Dict[str, Any]] = []
    offset = 0

    while offset < max_records:
        batch_size = min(MAX_RECORDS, max_records - offset)
        params: Dict[str, str] = {
            "where": where,
            "outFields": out_fields,
            "returnGeometry": "true" if return_geometry else "false",
            "resultRecordCount": str(batch_size),
            "resultOffset": str(offset),
        }
        if bbox:
            params["geometry"] = bbox
            params["geometryType"] = "esriGeometryEnvelope"
            params["inSR"] = "4326"
            params["spatialRel"] = "esriSpatialRelIntersects"

        result = _post_query(layer_id, params)
        features = result.get("features", [])
        all_features.extend(features)

        if len(features) < batch_size:
            break  # No more records
        if not result.get("exceededTransferLimit", False):
            break

        offset += batch_size

    return all_features


def aggregate_wells(
    where: str = "1=1",
    group_by: str = "county",
    layer_id: int = LAYER_ALL_WELLS,
) -> List[Dict[str, Any]]:
    """Run a GROUP BY aggregation query and return sorted results."""
    stats = json.dumps([{
        "statisticType": "count",
        "onStatisticField": "objectid",
        "outStatisticFieldName": "cnt",
    }])
    params: Dict[str, str] = {
        "where": where,
        "groupByFieldsForStatistics": group_by,
        "outStatistics": stats,
        "orderByFields": "cnt DESC",
    }
    result = _post_query(layer_id, params)
    return [f["attributes"] for f in result.get("features", [])]


def print_table(records: List[Dict[str, Any]], fields: Optional[List[str]] = None) -> None:
    """Print records as a formatted text table."""
    if not records:
        print("No records found.")
        return

    if fields is None:
        fields = list(records[0].keys())

    # Calculate column widths
    widths = {f: len(f) for f in fields}
    for rec in records:
        for f in fields:
            val = str(rec.get(f, ""))
            widths[f] = max(widths[f], len(val))

    # Header
    header = " | ".join(f.ljust(widths[f]) for f in fields)
    print(header)
    print("-+-".join("-" * widths[f] for f in fields))

    # Rows
    for rec in records:
        row = " | ".join(str(rec.get(f, "")).ljust(widths[f]) for f in fields)
        print(row)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Query WVDEP Oil and Gas well data via ArcGIS REST API"
    )
    parser.add_argument("--county", help="3-digit FIPS county code (e.g., 049)")
    parser.add_argument("--status", help="Well status filter (e.g., 'Active Well')")
    parser.add_argument("--formation", help="Formation name (partial match)")
    parser.add_argument("--operator", help="Operator/responsible party (partial match)")
    parser.add_argument("--marcellus", choices=["y", "n", "u"], help="Marcellus flag")
    parser.add_argument("--welltype", help="Well type (e.g., Horizontal)")
    parser.add_argument("--where", help="Raw SQL WHERE clause (overrides other filters)")
    parser.add_argument("--bbox", help="Bounding box as lon1,lat1,lon2,lat2 (WGS84)")
    parser.add_argument("--limit", type=int, default=100, help="Max records (default: 100)")
    parser.add_argument("--count", action="store_true", help="Return count only")
    parser.add_argument("--stats", metavar="FIELD", help="Aggregate by field (e.g., county)")
    parser.add_argument("--fields", help="Comma-separated output fields")
    parser.add_argument("--json-output", action="store_true", help="Output raw JSON")

    args = parser.parse_args()

    # Build WHERE clause
    if args.where:
        where = args.where
    else:
        clauses = []
        if args.county:
            clauses.append(f"county='{args.county}'")
        if args.status:
            clauses.append(f"wellstatus='{args.status}'")
        if args.formation:
            clauses.append(f"formation LIKE '%{args.formation}%'")
        if args.operator:
            clauses.append(f"respparty LIKE '%{args.operator}%'")
        if args.marcellus:
            clauses.append(f"marcellus='{args.marcellus}'")
        if args.welltype:
            clauses.append(f"welltype='{args.welltype}'")
        where = " AND ".join(clauses) if clauses else "1=1"

    # Count only
    if args.count:
        total = count_wells(where)
        print(f"Total matching wells: {total:,}")
        return

    # Statistics/aggregation
    if args.stats:
        results = aggregate_wells(where, group_by=args.stats)
        if args.json_output:
            json.dump(results, sys.stdout, indent=2)
            print()
        else:
            print(f"\nWell counts by {args.stats} (where: {where}):\n")
            print_table(results)
            total = sum(r["cnt"] for r in results)
            print(f"\nTotal: {total:,}")
        return

    # Standard query
    out_fields = args.fields if args.fields else DEFAULT_FIELDS
    features = query_wells(
        where=where,
        out_fields=out_fields,
        max_records=args.limit,
        bbox=args.bbox,
    )

    records = [f["attributes"] for f in features]

    if args.json_output:
        json.dump(records, sys.stdout, indent=2)
        print()
    else:
        total = count_wells(where)
        print(f"\nShowing {len(records)} of {total:,} matching wells (where: {where}):\n")
        display_fields = out_fields.split(",") if "," in out_fields else None
        print_table(records, fields=display_fields)


if __name__ == "__main__":
    main()
