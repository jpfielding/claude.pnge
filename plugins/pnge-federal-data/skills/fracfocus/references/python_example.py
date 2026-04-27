#!/usr/bin/env python3
"""FracFocus Public API Client

Query hydraulic fracturing chemical disclosure data from the FracFocus
registry. Uses only the Python standard library.

Usage:
    python3 python_example.py --state "West Virginia" --well "Country South"
    python3 python_example.py --api 47033060270000
    python3 python_example.py --bounds 39.5 39.0 -79.5 -80.5
    python3 python_example.py --download-csv /tmp/fracfocus
"""

import argparse
import json
import os
import ssl
import sys
import urllib.parse
import urllib.request

BASE_URL = "https://fracfocus.org/api/api"

# FracFocus uses a certificate chain that may require relaxed verification
# in some environments. In production, use proper CA bundles.
SSL_CTX = ssl.create_default_context()
SSL_CTX.check_hostname = False
SSL_CTX.verify_mode = ssl.CERT_NONE


def api_get(path, params=None):
    """Make a GET request to the FracFocus API and return parsed JSON."""
    url = BASE_URL + path
    if params:
        query = urllib.parse.urlencode(
            {k: v for k, v in params.items() if v is not None}
        )
        url = url + "?" + query

    req = urllib.request.Request(url)
    req.add_header("Accept", "application/json")

    with urllib.request.urlopen(req, context=SSL_CTX) as resp:
        raw = resp.read().decode("utf-8")

    # Handle double-encoded JSON (API sometimes wraps JSON in a string)
    data = json.loads(raw)
    if isinstance(data, str):
        data = json.loads(data)
    return data


def search_wells(state_name=None, county_code=None, operator_name=None,
                 well_name=None, api_number=None, cas_number=None,
                 start_date=None, end_date=None, page=1, pagesize=200):
    """Search FracFocus disclosures by various criteria.

    Returns dict with keys: Count, Page, PageSize, Wells (list or None).
    Wells may be None for very large result sets -- narrow your search.
    """
    params = {
        "state_name": state_name,
        "county_code": county_code,
        "operator_name": operator_name,
        "well_name": well_name,
        "api_number": api_number,
        "cas_number": cas_number,
        "start_date": start_date,
        "end_date": end_date,
        "page": str(page),
        "pagesize": str(pagesize),
    }
    return api_get("/fracfocus/search", params)


def get_well_by_api(api14):
    """Fetch a single well disclosure by 14-digit API number.

    Returns the well record with populated Ingredients array.
    """
    if len(api14) != 14:
        raise ValueError(f"API number must be 14 digits, got {len(api14)}")
    data = api_get("/FracFocus/WellByApiNumber", {"api14": api14})
    if isinstance(data, dict) and "Wells" in data:
        wells = data["Wells"]
        return wells[0] if wells else None
    return data


def get_wells_in_bounds(north, south, east, west, page=1, pagesize=200):
    """Search wells within a geographic bounding box.

    All coordinates in decimal degrees (WGS84).
    """
    params = {
        "north": str(north),
        "south": str(south),
        "east": str(east),
        "west": str(west),
        "page": str(page),
        "pagesize": str(pagesize),
        "orderby": "WellName",
    }
    return api_get("/fracfocus/wellsinbounds", params)


def get_states():
    """Return list of all states with State_No and Code."""
    return api_get("/state/states")


def get_counties(state_no):
    """Return list of counties for a state (use numeric State_No)."""
    return api_get("/state/countiesbystateid", {"stateid": str(state_no)})


def get_operators():
    """Return list of all operator names."""
    return api_get("/operator/operators")


def download_bulk_csv(output_dir):
    """Download the FracFocus bulk CSV zip file.

    WARNING: The file is approximately 430 MB.
    """
    url = "https://www.fracfocusdata.org/digitaldownload/FracFocusCSV.zip"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "FracFocusCSV.zip")

    print(f"Downloading FracFocus CSV bulk data (~430 MB)...")
    print(f"  Source: {url}")
    print(f"  Target: {output_path}")

    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, context=SSL_CTX) as resp:
        total = int(resp.headers.get("Content-Length", 0))
        downloaded = 0
        chunk_size = 1024 * 1024  # 1 MB chunks

        with open(output_path, "wb") as f:
            while True:
                chunk = resp.read(chunk_size)
                if not chunk:
                    break
                f.write(chunk)
                downloaded += len(chunk)
                if total:
                    pct = (downloaded / total) * 100
                    print(f"\r  Progress: {downloaded:,} / {total:,} bytes "
                          f"({pct:.1f}%)", end="", flush=True)
    print(f"\n  Done: {output_path}")
    return output_path


def print_well_summary(well):
    """Print a formatted summary of a well disclosure."""
    print(f"\n{'='*70}")
    print(f"Well: {well.get('WellName', 'N/A')}")
    print(f"API:  {well.get('APINumber', 'N/A')}")
    print(f"Operator: {well.get('OperatorClean', 'N/A')}")
    print(f"Location: {well.get('CountyName', 'N/A')}, "
          f"{well.get('StateName', 'N/A')}")
    print(f"Lat/Lon: {well.get('Latitude', 'N/A')}, "
          f"{well.get('Longitude', 'N/A')}")
    print(f"Job End: {well.get('JobEndDate', 'N/A')}")
    print(f"TVD: {well.get('TVD', 'N/A')} ft")

    tbwv = well.get("TotalBaseWaterVolume")
    if tbwv is not None:
        print(f"Total Base Water Volume: {tbwv:,.0f} gal")

    ingredients = well.get("Ingredients")
    if ingredients:
        print(f"\nChemical Ingredients ({len(ingredients)} records):")
        print(f"{'Ingredient':<40} {'CAS':<15} {'% HF Job':>10}")
        print(f"{'-'*40} {'-'*15} {'-'*10}")
        for ing in sorted(ingredients,
                          key=lambda x: x.get("PercentHFJob") or 0,
                          reverse=True):
            name = (ing.get("IngredientName") or "Unknown")[:40]
            cas = ing.get("CASNumber") or "N/A"
            pct = ing.get("PercentHFJob")
            pct_str = f"{pct:.5f}" if pct is not None else "N/A"
            print(f"{name:<40} {cas:<15} {pct_str:>10}")
    else:
        print("\n  No ingredient data available for this disclosure.")


def main():
    parser = argparse.ArgumentParser(
        description="Query FracFocus chemical disclosure data"
    )
    parser.add_argument("--state", help="State name (e.g., 'West Virginia')")
    parser.add_argument("--county", help="County code (numeric)")
    parser.add_argument("--operator", help="Operator name")
    parser.add_argument("--well", help="Well name (partial match)")
    parser.add_argument("--api", help="14-digit API number")
    parser.add_argument("--cas", help="CAS registry number")
    parser.add_argument("--start-date", help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end-date", help="End date (YYYY-MM-DD)")
    parser.add_argument("--bounds", nargs=4, type=float,
                        metavar=("N", "S", "E", "W"),
                        help="Bounding box: north south east west")
    parser.add_argument("--page", type=int, default=1, help="Page number")
    parser.add_argument("--pagesize", type=int, default=10,
                        help="Results per page (max 200)")
    parser.add_argument("--download-csv", metavar="DIR",
                        help="Download bulk CSV to directory")
    parser.add_argument("--list-states", action="store_true",
                        help="List all states with codes")
    parser.add_argument("--list-operators", action="store_true",
                        help="List all operators")
    parser.add_argument("--json", action="store_true",
                        help="Output raw JSON instead of formatted text")

    args = parser.parse_args()

    if args.list_states:
        states = get_states()
        for s in states:
            print(f"  {s['State_No']:>3}  {s['Code']:<4} {s['StateName']}")
        return

    if args.list_operators:
        operators = get_operators()
        for op in operators:
            print(f"  {op['OperatorName']}")
        print(f"\nTotal: {len(operators)} operators")
        return

    if args.download_csv:
        download_bulk_csv(args.download_csv)
        return

    if args.api:
        well = get_well_by_api(args.api)
        if well:
            if args.json:
                print(json.dumps(well, indent=2, default=str))
            else:
                print_well_summary(well)
        else:
            print(f"No well found for API number: {args.api}")
        return

    if args.bounds:
        n, s, e, w = args.bounds
        result = get_wells_in_bounds(n, s, e, w, args.page, args.pagesize)
    elif any([args.state, args.county, args.operator, args.well,
              args.cas, args.start_date, args.end_date]):
        result = search_wells(
            state_name=args.state,
            county_code=args.county,
            operator_name=args.operator,
            well_name=args.well,
            cas_number=args.cas,
            start_date=args.start_date,
            end_date=args.end_date,
            page=args.page,
            pagesize=args.pagesize,
        )
    else:
        parser.print_help()
        return

    if args.json:
        print(json.dumps(result, indent=2, default=str))
        return

    count = result.get("Count", 0)
    wells = result.get("Wells")
    print(f"\nFracFocus Search Results: {count} total disclosures")

    if wells:
        print(f"Showing {len(wells)} on page {args.page}:\n")
        print(f"{'Well Name':<30} {'Operator':<25} {'API Number':<16} "
              f"{'County':<15} {'State':<5}")
        print(f"{'-'*30} {'-'*25} {'-'*16} {'-'*15} {'-'*5}")
        for w in wells:
            name = (w.get("WellName") or "N/A")[:30]
            oper = (w.get("OperatorClean") or "N/A")[:25]
            api = w.get("APINumber") or "N/A"
            county = (w.get("CountyName") or "N/A")[:15]
            state = (w.get("StateName") or "N/A")[:5]
            print(f"{name:<30} {oper:<25} {api:<16} {county:<15} {state:<5}")
    elif count > 0:
        print("\nToo many results to return well details.")
        print("Narrow your search with additional filters:")
        print("  --state, --county, --operator, --well, --start-date, "
              "--end-date")


if __name__ == "__main__":
    main()
