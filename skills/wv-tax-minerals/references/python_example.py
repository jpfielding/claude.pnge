#!/usr/bin/env python3
"""
WV Delinquent Mineral Property Query Client

Queries three WV ArcGIS REST services to find delinquent mineral parcels
near active oil and gas wells:
  1. Delinquent_Properties — tax-delinquent parcels
  2. WV_Parcels ParcelSummary (Table 11) — tax assessment data
  3. WVDEP oil_gas (Layer 7) — active wells for spatial correlation

Uses only Python stdlib (urllib, json) — no third-party packages required.

Usage:
    python python_example.py --county Tyler                     # Delinquent minerals in Tyler County
    python python_example.py --county Tyler --status "No Bid"   # Only No Bid parcels
    python python_example.py --county Marshall --enrich         # Enrich with ParcelSummary data
    python python_example.py --county Tyler --wells --radius 1  # Find wells within 1 mile
    python python_example.py --statewide --count                # Statewide delinquent mineral count
    python python_example.py --count --county Tyler             # County count only
"""

import argparse
import json
import math
import ssl
import sys
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Optional

# --- Endpoints ---

DELINQUENT_URL = (
    "https://services.wvgis.wvu.edu/arcgis/rest/services"
    "/Planning_Cadastre/Delinquent_Properties/MapServer/0"
)

PARCEL_SUMMARY_URL = (
    "https://services.wvgis.wvu.edu/arcgis/rest/services"
    "/Planning_Cadastre/WV_Parcels/MapServer/11"
)

WVDEP_WELLS_URL = (
    "https://tagis.dep.wv.gov/arcgis/rest/services"
    "/WVDEP_enterprise/oil_gas/MapServer/7"
)

PRODUCTION_URL = (
    "https://tagis.dep.wv.gov/oog/get_production_data_RBDMS.php?api={permitid}"
)

# Server record limits
DELINQUENT_MAX = 2000
PARCEL_MAX = 2000
WELLS_MAX = 3000

# Mineral keyword SQL fragment
MINERAL_WHERE = (
    "(FullLegalDescription LIKE '%MINERAL%'"
    " OR FullLegalDescription LIKE '%OIL%GAS%'"
    " OR FullLegalDescription LIKE '%SUR MIN%'"
    " OR FullLegalDescription LIKE '%COAL%')"
)

# SSL contexts
_wvgis_ctx = ssl.create_default_context()  # WVU GIS has valid certs

_wvdep_ctx = ssl.create_default_context()
_wvdep_ctx.check_hostname = False
_wvdep_ctx.verify_mode = ssl.CERT_NONE  # WVDEP cert may not validate


def _post_query(
    base_url: str, params: Dict[str, str], ctx: ssl.SSLContext
) -> Dict[str, Any]:
    """POST a query to an ArcGIS REST endpoint and return parsed JSON."""
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


# ---- Delinquent Properties ----


def count_delinquent(where: str = "1=1") -> int:
    """Count delinquent properties matching WHERE clause."""
    result = _post_query(
        DELINQUENT_URL, {"where": where, "returnCountOnly": "true"}, _wvgis_ctx
    )
    return result.get("count", 0)


def query_delinquent(
    where: str = "1=1",
    max_records: int = 100,
    return_geometry: bool = False,
) -> List[Dict[str, Any]]:
    """Query delinquent properties with pagination."""
    fields = (
        "CleanParcelID,county,status,FullOwnerName,"
        "FullLegalDescription,Acres_C,certno,TotalAmtDue"
    )
    all_features: List[Dict[str, Any]] = []
    offset = 0

    while offset < max_records:
        batch = min(DELINQUENT_MAX, max_records - offset)
        params: Dict[str, str] = {
            "where": where,
            "outFields": fields,
            "returnGeometry": "true" if return_geometry else "false",
            "resultRecordCount": str(batch),
            "resultOffset": str(offset),
        }
        if return_geometry:
            params["outSR"] = "4326"

        result = _post_query(DELINQUENT_URL, params, _wvgis_ctx)
        features = result.get("features", [])
        all_features.extend(features)

        if len(features) < batch or not result.get("exceededTransferLimit"):
            break
        offset += batch

    return all_features


# ---- ParcelSummary Enrichment ----


def enrich_parcels(parcel_ids: List[str]) -> Dict[str, Dict[str, Any]]:
    """Batch-query ParcelSummary Table 11 for a list of CleanParcelIDs."""
    fields = (
        "CleanParcelID,CountyName,FullOwnerName,FullLegalDescription,"
        "TaxClass,PropertyClassCode,LandUseCode,TotalAppraisal,"
        "TotalLandAppraisal,DeededAcres,DeedBook,DeedPage"
    )
    enriched: Dict[str, Dict[str, Any]] = {}

    # Batch in groups of 50 to stay within URL limits
    for i in range(0, len(parcel_ids), 50):
        batch = parcel_ids[i : i + 50]
        id_list = ",".join(f"'{pid}'" for pid in batch)
        where = f"CleanParcelID IN ({id_list})"

        result = _post_query(
            PARCEL_SUMMARY_URL,
            {"where": where, "outFields": fields, "resultRecordCount": "2000"},
            _wvgis_ctx,
        )
        for feat in result.get("features", []):
            attrs = feat["attributes"]
            pid = attrs.get("CleanParcelID")
            if pid:
                enriched[pid] = attrs

    return enriched


# ---- Well Spatial Correlation ----


def find_nearby_wells(
    lon: float, lat: float, radius_miles: float = 1.0
) -> List[Dict[str, Any]]:
    """Find active WVDEP wells within radius_miles of a point (WGS84)."""
    # Convert miles to approximate degrees (1 degree lat ~ 69 miles)
    radius_deg = radius_miles / 69.0

    params: Dict[str, str] = {
        "geometry": f"{lon},{lat}",
        "geometryType": "esriGeometryPoint",
        "inSR": "4326",
        "spatialRel": "esriSpatialRelIntersects",
        "distance": str(radius_miles * 1609.34),  # meters
        "units": "esriSRUnit_Meter",
        "where": "wellstatus='Active Well'",
        "outFields": "permitid,api,county,welltype,formation,respparty,wellstatus",
        "returnGeometry": "false",
        "resultRecordCount": "50",
    }

    result = _post_query(WVDEP_WELLS_URL, params, _wvdep_ctx)
    return [f["attributes"] for f in result.get("features", [])]


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
        description="Query WV delinquent mineral properties near active wells"
    )
    parser.add_argument("--county", help="County name (e.g., Tyler, Marshall)")
    parser.add_argument(
        "--status",
        help="Delinquent status filter (e.g., 'No Bid', 'Deed')",
    )
    parser.add_argument(
        "--statewide",
        action="store_true",
        help="Search all counties (default: requires --county)",
    )
    parser.add_argument(
        "--count", action="store_true", help="Return count only"
    )
    parser.add_argument(
        "--enrich",
        action="store_true",
        help="Enrich with ParcelSummary tax data",
    )
    parser.add_argument(
        "--wells",
        action="store_true",
        help="Find nearby active wells for each parcel",
    )
    parser.add_argument(
        "--radius",
        type=float,
        default=1.0,
        help="Well search radius in miles (default: 1.0)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=100,
        help="Max delinquent records (default: 100)",
    )
    parser.add_argument(
        "--json-output", action="store_true", help="Output raw JSON"
    )
    parser.add_argument(
        "--keyword",
        default="MINERAL",
        help="Legal description keyword (default: MINERAL)",
    )

    args = parser.parse_args()

    if not args.county and not args.statewide:
        parser.error("Specify --county or --statewide")

    # Build WHERE clause
    clauses = [f"FullLegalDescription LIKE '%{args.keyword}%'"]
    if args.county:
        clauses.append(f"county='{args.county}'")
    if args.status:
        clauses.append(f"status='{args.status}'")
    else:
        clauses.append("status IN ('No Bid','Deed')")

    where = " AND ".join(clauses)

    # Count mode
    if args.count:
        total = count_delinquent(where)
        print(f"Matching delinquent mineral parcels: {total:,}")
        return

    # Query delinquent parcels
    need_geom = args.wells  # Need geometry for spatial well correlation
    features = query_delinquent(
        where=where, max_records=args.limit, return_geometry=need_geom
    )
    records = []
    for f in features:
        rec = dict(f["attributes"])
        if need_geom and f.get("geometry"):
            rec["_lon"] = f["geometry"].get("x")
            rec["_lat"] = f["geometry"].get("y")
        records.append(rec)

    if not records:
        print(f"No delinquent mineral parcels found (where: {where})")
        return

    total = count_delinquent(where)
    print(
        f"\nShowing {len(records)} of {total:,} delinquent mineral parcels"
        f" (where: {where}):\n"
    )

    # Enrich with ParcelSummary
    if args.enrich:
        parcel_ids = [r["CleanParcelID"] for r in records if r.get("CleanParcelID")]
        enriched = enrich_parcels(parcel_ids)
        for rec in records:
            pid = rec.get("CleanParcelID")
            if pid and pid in enriched:
                tax = enriched[pid]
                rec["TaxClass"] = tax.get("TaxClass", "")
                rec["TotalAppraisal"] = tax.get("TotalAppraisal", "")
                rec["DeededAcres"] = tax.get("DeededAcres", "")

    # Find nearby wells
    if args.wells:
        for rec in records:
            lon = rec.pop("_lon", None)
            lat = rec.pop("_lat", None)
            if lon is not None and lat is not None:
                wells = find_nearby_wells(lon, lat, args.radius)
                rec["NearbyWells"] = len(wells)
                if wells:
                    rec["NearestWell"] = wells[0].get("permitid", "")
                    rec["WellFormation"] = wells[0].get("formation", "")
            else:
                rec["NearbyWells"] = "N/A"
    else:
        # Remove geometry fields if present
        for rec in records:
            rec.pop("_lon", None)
            rec.pop("_lat", None)

    if args.json_output:
        json.dump(records, sys.stdout, indent=2)
        print()
    else:
        print_table(records)


if __name__ == "__main__":
    main()
