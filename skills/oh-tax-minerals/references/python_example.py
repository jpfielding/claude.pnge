#!/usr/bin/env python3
"""
Ohio Tax-Delinquent and Dormant Mineral Parcel Query Client

Queries Ohio ArcGIS REST services to find mineral-coded parcels near
active Utica/Marcellus wells, with optional dormant mineral screening:
  1. OGRIP Statewide Parcels — mineral parcels via StateLUC 200-series
  2. OIT Statewide Parcels 2022 — owner name enrichment
  3. ODNR Oil & Gas Wells — active well spatial correlation
  4. County Delinquent Data — tax delinquency (Stark County example)

Uses only Python stdlib (urllib, json, ssl, argparse) — no third-party
packages required.

Ohio's MAJOR ADVANTAGE: The StateLUC field explicitly codes mineral parcels
with 200-series values. No text parsing of legal descriptions needed (unlike
WV/PA).

Usage:
    python python_example.py --county BELMONT                          # Mineral parcels in Belmont County
    python python_example.py --county HARRISON --luc 240,250           # Oil & gas interests only
    python python_example.py --county BELMONT --wells --radius 1       # Find wells within 1 mile
    python python_example.py --county CARROLL --owners                 # Enrich with owner names
    python python_example.py --statewide --count                       # Statewide mineral parcel count
    python python_example.py --county BELMONT --dormant-screen         # Screen for dormant minerals
    python python_example.py --count --county HARRISON                 # County count only
"""

import argparse
import json
import ssl
import sys
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Optional

# --- Endpoints ---

OGRIP_PARCELS_URL = (
    "https://services2.arcgis.com/MlJ0G8iWUyC7jAmu/arcgis/rest/services"
    "/OhioStatewidePacels_full_view/FeatureServer/0"
)

OIT_PARCELS_URL = (
    "https://maps.ohio.gov/arcgis/rest/services"
    "/Statewide_Parcels_2022/MapServer/0"
)

ODNR_WELLS_URL = (
    "https://gis.ohiodnr.gov/arcgis/rest/services"
    "/DOG_Services/Oilgas_Wells_public/MapServer/0"
)

# County delinquent data (Stark County example — has CERTIFIED_DELINQUENT_YEAR)
STARK_PARCELS_URL = (
    "https://scgisa.starkcountyohio.gov/arcgis/rest/services"
    "/Auditor/StarkCountyParcels/MapServer/0"
)

# Server record limits
OGRIP_MAX = 2000
OIT_MAX = 2000
ODNR_MAX = 1000

# Default SSL context — all Ohio endpoints have valid certificates
_ssl_ctx = ssl.create_default_context()

# Ohio mineral land use codes
MINERAL_LUC_ALL = ("200", "210", "220", "230", "240", "250", "260", "261", "270")
MINERAL_LUC_OIL_GAS = ("240", "250")
MINERAL_LUC_COAL = ("210", "220", "230")

# 8 Target counties (Eastern OH Utica/Marcellus play)
TARGET_COUNTIES = [
    "BELMONT", "CARROLL", "COLUMBIANA", "HARRISON",
    "JEFFERSON", "MONROE", "NOBLE", "GUERNSEY",
]

# Current year for dormant mineral screening (20-year lookback)
import datetime
CURRENT_YEAR = datetime.datetime.now().year
DORMANT_CUTOFF_YEAR = CURRENT_YEAR - 20


def _post_query(
    base_url: str, params: Dict[str, str], ctx: Optional[ssl.SSLContext] = None
) -> Dict[str, Any]:
    """POST a query to an ArcGIS REST endpoint and return parsed JSON."""
    if ctx is None:
        ctx = _ssl_ctx
    params["f"] = "json"
    data = urllib.parse.urlencode(params).encode("utf-8")
    req = urllib.request.Request(base_url + "/query", data=data, method="POST")
    with urllib.request.urlopen(req, context=ctx, timeout=60) as resp:
        body = json.loads(resp.read().decode("utf-8"))
    if "error" in body:
        raise RuntimeError(
            f"ArcGIS error {body['error'].get('code')}: "
            f"{body['error'].get('message')}"
        )
    return body


# ---- OGRIP Mineral Parcels ----


def count_mineral_parcels(county: Optional[str] = None, luc_codes: Optional[List[str]] = None) -> int:
    """Count mineral-coded parcels in OGRIP."""
    where = _build_mineral_where(county, luc_codes)
    result = _post_query(OGRIP_PARCELS_URL, {"where": where, "returnCountOnly": "true"})
    return result.get("count", 0)


def query_mineral_parcels(
    county: Optional[str] = None,
    luc_codes: Optional[List[str]] = None,
    max_records: int = 200,
    return_geometry: bool = False,
) -> List[Dict[str, Any]]:
    """Query OGRIP mineral parcels with pagination."""
    where = _build_mineral_where(county, luc_codes)
    fields = (
        "StateParcelID,LocalParcelID,County,StateLUC,"
        "SitusAddressAll,MailAddressAll,LandArea,CAMADataSite"
    )
    all_features: List[Dict[str, Any]] = []
    offset = 0

    while offset < max_records:
        batch = min(OGRIP_MAX, max_records - offset)
        params: Dict[str, str] = {
            "where": where,
            "outFields": fields,
            "returnGeometry": "true" if return_geometry else "false",
            "resultRecordCount": str(batch),
            "resultOffset": str(offset),
        }
        if return_geometry:
            params["outSR"] = "4326"  # OGRIP native is EPSG:3735; must request WGS84

        result = _post_query(OGRIP_PARCELS_URL, params)
        features = result.get("features", [])
        all_features.extend(features)

        if len(features) < batch or not result.get("exceededTransferLimit"):
            break
        offset += batch

    return all_features


def _build_mineral_where(county: Optional[str], luc_codes: Optional[List[str]]) -> str:
    """Build WHERE clause for mineral parcel queries."""
    clauses = []
    if county:
        clauses.append(f"County='{county.upper()}'")
    if luc_codes:
        code_list = ",".join(f"'{c}'" for c in luc_codes)
        clauses.append(f"StateLUC IN ({code_list})")
    else:
        clauses.append("StateLUC LIKE '2%'")
    return " AND ".join(clauses)


# ---- OIT Owner Enrichment ----


def enrich_with_owners(parcel_ids: List[str], county: str) -> Dict[str, Dict[str, Any]]:
    """
    Query OIT Statewide Parcels 2022 for owner names.
    Matches on county + PIN pattern. OIT uses PIN field.
    """
    enriched: Dict[str, Dict[str, Any]] = {}
    fields = "PIN,COUNTY,OWNER1,OWNER2,ASSR_ACRES,CALC_ACRES,AUD_LINK"

    # Batch in groups of 50 to stay within URL limits
    for i in range(0, len(parcel_ids), 50):
        batch = parcel_ids[i:i + 50]
        id_list = ",".join(f"'{pid}'" for pid in batch)
        where = f"COUNTY='{county.upper()}' AND PIN IN ({id_list})"

        try:
            result = _post_query(OIT_PARCELS_URL, {
                "where": where,
                "outFields": fields,
                "resultRecordCount": "2000",
            })
            for feat in result.get("features", []):
                attrs = feat["attributes"]
                pin = attrs.get("PIN")
                if pin:
                    enriched[pin] = attrs
        except RuntimeError:
            # OIT service may not match all parcels; continue
            pass

    return enriched


# ---- ODNR Well Spatial Correlation ----


def find_nearby_wells(
    lon: float, lat: float, radius_miles: float = 1.0,
    status_filter: str = "Producing",
) -> List[Dict[str, Any]]:
    """Find ODNR wells within radius_miles of a point (WGS84)."""
    params: Dict[str, str] = {
        "geometry": f"{lon},{lat}",
        "geometryType": "esriGeometryPoint",
        "inSR": "4326",
        "spatialRel": "esriSpatialRelIntersects",
        "distance": str(radius_miles * 1609.34),  # meters
        "units": "esriSRUnit_Meter",
        "where": f"WL_STATUS_DESC='{status_filter}'",
        "outFields": (
            "API_WELLNO,MapSymbol_DESC,WL_STATUS_DESC,WL_CNTY,"
            "CO_NAME,ProducingFormation1,Utica_Shale,Marcellus_Shale,"
            "Last_Nonzero_Production_Year"
        ),
        "returnGeometry": "false",
        "resultRecordCount": "50",
    }

    result = _post_query(ODNR_WELLS_URL, params)
    return [f["attributes"] for f in result.get("features", [])]


def screen_dormant_minerals(
    lon: float, lat: float, radius_miles: float = 2.0
) -> Dict[str, Any]:
    """
    Screen a mineral parcel location for Dormant Mineral Act indicators.

    Returns a dict with:
      - nearby_producing: count of producing wells within radius
      - last_production_year: most recent production year among nearby wells
      - dormant_flag: True if no production in 20+ years (potential DMA candidate)
      - wells: list of nearby well records
    """
    # Query ALL wells nearby (not just producing)
    params: Dict[str, str] = {
        "geometry": f"{lon},{lat}",
        "geometryType": "esriGeometryPoint",
        "inSR": "4326",
        "spatialRel": "esriSpatialRelIntersects",
        "distance": str(radius_miles * 1609.34),
        "units": "esriSRUnit_Meter",
        "where": "1=1",
        "outFields": (
            "API_WELLNO,WL_STATUS_DESC,CO_NAME,ProducingFormation1,"
            "Last_Nonzero_Production_Year,Utica_Shale"
        ),
        "returnGeometry": "false",
        "resultRecordCount": "100",
    }

    result = _post_query(ODNR_WELLS_URL, params)
    wells = [f["attributes"] for f in result.get("features", [])]

    producing = [w for w in wells if w.get("WL_STATUS_DESC") == "Producing"]
    last_years = [
        w["Last_Nonzero_Production_Year"]
        for w in wells
        if w.get("Last_Nonzero_Production_Year") and w["Last_Nonzero_Production_Year"] > 0
    ]
    last_year = max(last_years) if last_years else 0

    return {
        "nearby_wells_total": len(wells),
        "nearby_producing": len(producing),
        "last_production_year": last_year,
        "dormant_flag": last_year > 0 and last_year < DORMANT_CUTOFF_YEAR,
        "no_wells_flag": len(wells) == 0,
        "wells": wells,
    }


# ---- County Auditor CAMA Link ----


def build_auditor_link(parcel: Dict[str, Any]) -> Optional[str]:
    """Extract or construct a county auditor link from parcel data."""
    cama = parcel.get("CAMADataSite")
    if cama and cama.strip():
        return cama.strip()
    return None


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


def luc_description(code: str) -> str:
    """Return human-readable description for a StateLUC code."""
    descriptions = {
        "200": "Min-Custom Code",
        "210": "Min-Coal Land (surface+rights)",
        "220": "Min-Coal Rights-Working Interest",
        "230": "Min-Coal Rights-Royalty Interest",
        "240": "Min-Oil & Gas-Working Interest",
        "250": "Min-Oil & Gas-Royalty Interest",
        "260": "Min-Other Minerals",
        "261": "Min-Custom Code",
        "270": "Min-Custom Code",
    }
    return descriptions.get(code, f"Unknown ({code})")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Query Ohio mineral parcels near active Utica/Marcellus wells"
    )
    parser.add_argument(
        "--county",
        help="County name, uppercase (e.g., BELMONT, HARRISON)",
    )
    parser.add_argument(
        "--luc",
        help="Comma-separated StateLUC codes (default: all 200-series). "
             "Example: 240,250 for oil & gas only",
    )
    parser.add_argument(
        "--statewide",
        action="store_true",
        help="Search all counties (default: requires --county)",
    )
    parser.add_argument(
        "--count",
        action="store_true",
        help="Return count only",
    )
    parser.add_argument(
        "--owners",
        action="store_true",
        help="Enrich with owner names from OIT Parcels 2022",
    )
    parser.add_argument(
        "--wells",
        action="store_true",
        help="Find nearby active wells for each parcel",
    )
    parser.add_argument(
        "--dormant-screen",
        action="store_true",
        help="Screen parcels for Dormant Mineral Act indicators (20-year test)",
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
        default=200,
        help="Max parcel records to fetch (default: 200)",
    )
    parser.add_argument(
        "--json-output",
        action="store_true",
        help="Output raw JSON instead of table",
    )

    args = parser.parse_args()

    if not args.county and not args.statewide:
        parser.error("Specify --county or --statewide")

    # Parse LUC codes
    luc_codes = None
    if args.luc:
        luc_codes = [c.strip() for c in args.luc.split(",")]

    county = args.county.upper() if args.county else None

    # Count mode
    if args.count:
        total = count_mineral_parcels(county=county, luc_codes=luc_codes)
        scope = county if county else "statewide"
        luc_desc = f"LUC {','.join(luc_codes)}" if luc_codes else "all 200-series"
        print(f"Mineral-coded parcels ({luc_desc}) in {scope}: {total:,}")
        return

    # Query mineral parcels
    need_geom = args.wells or args.dormant_screen
    features = query_mineral_parcels(
        county=county,
        luc_codes=luc_codes,
        max_records=args.limit,
        return_geometry=need_geom,
    )

    records = []
    for f in features:
        rec = dict(f["attributes"])
        rec["LUC_Desc"] = luc_description(rec.get("StateLUC", ""))
        if need_geom and f.get("geometry"):
            rec["_lon"] = f["geometry"].get("x")
            rec["_lat"] = f["geometry"].get("y")
        # Build auditor link
        auditor = build_auditor_link(rec)
        if auditor:
            rec["AuditorLink"] = auditor
        records.append(rec)

    if not records:
        where_desc = _build_mineral_where(county, luc_codes)
        print(f"No mineral parcels found (where: {where_desc})")
        return

    total = count_mineral_parcels(county=county, luc_codes=luc_codes)
    scope = county if county else "statewide"
    print(f"\nShowing {len(records)} of {total:,} mineral parcels in {scope}:\n")

    # Enrich with owner names
    if args.owners and county:
        local_ids = [r["LocalParcelID"] for r in records if r.get("LocalParcelID")]
        owners = enrich_with_owners(local_ids, county)
        for rec in records:
            lid = rec.get("LocalParcelID")
            if lid and lid in owners:
                owner_data = owners[lid]
                rec["Owner1"] = owner_data.get("OWNER1", "")
                rec["Owner2"] = owner_data.get("OWNER2", "")

    # Find nearby wells
    if args.wells and not args.dormant_screen:
        for rec in records:
            lon = rec.get("_lon")
            lat = rec.get("_lat")
            if lon is not None and lat is not None:
                wells = find_nearby_wells(lon, lat, args.radius)
                rec["NearbyWells"] = len(wells)
                if wells:
                    rec["NearestOperator"] = wells[0].get("CO_NAME", "")
                    rec["NearestFormation"] = wells[0].get("ProducingFormation1", "")
                    utica_count = sum(1 for w in wells if w.get("Utica_Shale") == "Yes")
                    rec["UticaWells"] = utica_count
            else:
                rec["NearbyWells"] = "N/A"

    # Dormant mineral screening
    if args.dormant_screen:
        print(f"Screening for Dormant Mineral Act indicators "
              f"(cutoff year: {DORMANT_CUTOFF_YEAR})...\n")
        for rec in records:
            lon = rec.get("_lon")
            lat = rec.get("_lat")
            if lon is not None and lat is not None:
                screen = screen_dormant_minerals(lon, lat, args.radius * 2)
                rec["TotalNearbyWells"] = screen["nearby_wells_total"]
                rec["ProducingWells"] = screen["nearby_producing"]
                rec["LastProdYear"] = screen["last_production_year"]
                rec["DormantFlag"] = "YES" if screen["dormant_flag"] else "NO"
                rec["NoWells"] = "YES" if screen["no_wells_flag"] else "NO"
            else:
                rec["DormantFlag"] = "N/A"

    # Clean up internal geometry fields
    for rec in records:
        rec.pop("_lon", None)
        rec.pop("_lat", None)

    if args.json_output:
        json.dump(records, sys.stdout, indent=2)
        print()
    else:
        # Select display fields based on mode
        if args.dormant_screen:
            display_fields = [
                "LocalParcelID", "County", "StateLUC", "LUC_Desc",
                "LandArea", "TotalNearbyWells", "ProducingWells",
                "LastProdYear", "DormantFlag",
            ]
        elif args.wells:
            display_fields = [
                "LocalParcelID", "County", "StateLUC", "LUC_Desc",
                "LandArea", "NearbyWells", "UticaWells",
                "NearestOperator", "NearestFormation",
            ]
        elif args.owners:
            display_fields = [
                "LocalParcelID", "County", "StateLUC", "LUC_Desc",
                "Owner1", "LandArea", "MailAddressAll",
            ]
        else:
            display_fields = [
                "LocalParcelID", "County", "StateLUC", "LUC_Desc",
                "LandArea", "MailAddressAll", "CAMADataSite",
            ]
        print_table(records, display_fields)

        # Print summary
        print(f"\n--- Summary ---")
        print(f"Total mineral parcels shown: {len(records)} of {total:,}")
        if county:
            print(f"County: {county}")
        luc_counts: Dict[str, int] = {}
        for rec in records:
            code = rec.get("StateLUC", "Unknown")
            luc_counts[code] = luc_counts.get(code, 0) + 1
        print("By StateLUC code:")
        for code, cnt in sorted(luc_counts.items()):
            print(f"  {code} ({luc_description(code)}): {cnt}")

        if args.dormant_screen:
            dormant = sum(1 for r in records if r.get("DormantFlag") == "YES")
            no_wells = sum(1 for r in records if r.get("NoWells") == "YES")
            print(f"\nDormant Mineral Act screening (cutoff: {DORMANT_CUTOFF_YEAR}):")
            print(f"  Potential dormant (no production in 20+ years): {dormant}")
            print(f"  No nearby wells at all: {no_wells}")
            print(f"  Note: This is a DATA SCREEN only. Actual DMA applicability")
            print(f"  requires title examination and legal review under ORC 5301.56.")


if __name__ == "__main__":
    main()
