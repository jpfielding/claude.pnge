#!/usr/bin/env python3
"""
BOEM Offshore Data — Python client (stdlib only).

Queries the BOEM ArcGIS REST MapServer and downloads bulk data files.
No third-party packages required.

Usage:
    python3 python_example.py wells --status PA --limit 10
    python3 python_example.py platforms --limit 5
    python3 python_example.py leases --status PROD --limit 5
    python3 python_example.py wells --bbox "-91,28,-89,29" --limit 10
    python3 python_example.py count wells
    python3 python_example.py download ogoradelimit.zip
"""

import json
import sys
import urllib.request
import urllib.parse
import urllib.error
import os
from typing import Optional


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

GIS_BASE = (
    "https://gis.boem.gov/arcgis/rest/services/BOEM_BSEE"
    "/MMC_Layers/MapServer"
)

DATA_BASE = "https://www.data.boem.gov"

LAYERS = {
    "platforms": 0,
    "wells": 1,
    "pipelines": 2,
    "leases": 15,
    "planning_areas": 20,
}

# Default fields per layer (subset for readability)
DEFAULT_FIELDS = {
    "platforms": "COMPLEX_ID_NUM,INSTALL_DATE,REMOVAL_DATE",
    "wells": (
        "API_NUMBER,OPERATOR,WELL_NAME,SPUD_DATE,"
        "TYPE_CODE_DESC,STATUS,STATUS_DESCRIPTION,DEPTH"
    ),
    "pipelines": "SEGMENT_NUM",
    "leases": (
        "LEASE_NUMBER,LEASE_STATUS_CD,LEASE_EFF_DATE,"
        "SALE_NUMBER,ROYALTY_RATE"
    ),
    "planning_areas": "*",
}


# ---------------------------------------------------------------------------
# GIS query helpers
# ---------------------------------------------------------------------------


def gis_query(
    layer_name: str,
    where: str = "1=1",
    out_fields: Optional[str] = None,
    bbox: Optional[str] = None,
    limit: int = 10,
    offset: int = 0,
    count_only: bool = False,
) -> dict:
    """Query a BOEM GIS MapServer layer and return the JSON response."""

    layer_id = LAYERS.get(layer_name)
    if layer_id is None:
        raise ValueError(
            f"Unknown layer '{layer_name}'. "
            f"Choose from: {', '.join(LAYERS)}"
        )

    if out_fields is None:
        out_fields = DEFAULT_FIELDS.get(layer_name, "*")

    params = {
        "where": where,
        "outFields": out_fields,
        "resultRecordCount": str(limit),
        "resultOffset": str(offset),
        "f": "json",
    }

    if count_only:
        params["returnCountOnly"] = "true"

    if bbox:
        parts = [x.strip() for x in bbox.split(",")]
        if len(parts) != 4:
            raise ValueError(
                "Bounding box must be 4 comma-separated values: "
                "xmin,ymin,xmax,ymax"
            )
        params["geometry"] = bbox
        params["geometryType"] = "esriGeometryEnvelope"
        params["spatialRel"] = "esriSpatialRelIntersects"

    url = f"{GIS_BASE}/{layer_id}/query?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url)
    req.add_header("User-Agent", "boem-skill/1.0")

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        print(f"HTTP {exc.code}: {exc.reason}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as exc:
        print(f"Connection error: {exc.reason}", file=sys.stderr)
        sys.exit(1)


def get_count(layer_name: str, where: str = "1=1") -> int:
    """Return the total feature count for a layer."""
    data = gis_query(layer_name, where=where, count_only=True)
    return data.get("count", 0)


def paginate_all(
    layer_name: str,
    where: str = "1=1",
    out_fields: Optional[str] = None,
    bbox: Optional[str] = None,
    page_size: int = 1000,
    max_records: int = 10000,
) -> list:
    """Fetch all features from a layer with automatic pagination."""
    all_features = []
    offset = 0

    while offset < max_records:
        batch_size = min(page_size, max_records - offset)
        data = gis_query(
            layer_name,
            where=where,
            out_fields=out_fields,
            bbox=bbox,
            limit=batch_size,
            offset=offset,
        )
        features = data.get("features", [])
        if not features:
            break
        all_features.extend(features)
        offset += len(features)
        if len(features) < batch_size:
            break

    return all_features


# ---------------------------------------------------------------------------
# Bulk download helper
# ---------------------------------------------------------------------------

# Common download paths (filename -> URL path)
DOWNLOAD_FILES = {
    "ogoradelimit.zip": "/Production/Files/ogoradelimit.zip",
    "ogora2024delimit.zip": "/Production/Files/ogora2024delimit.zip",
    "BoreholeRawData.zip": "/Well/Files/BoreholeRawData.zip",
    "OCSProdRawData.zip": "/Production/Files/OCSProdRawData.zip",
    "LeaseOwnerRawData.zip": "/Leasing/Files/LeaseOwnerRawData.zip",
    "PlatStrucRawData.zip": "/Platform/Files/PlatStrucRawData.zip",
    "PipeLocRawData.zip": "/Pipeline/Files/PipeLocRawData.zip",
    "CompanyRawData.zip": "/Company/Files/CompanyRawData.zip",
    "APDRawData.zip": "/Well/Files/APDRawData.zip",
    "ProductionRawData.zip": "/Production/Files/ProductionRawData.zip",
}


def download_file(filename: str, dest_dir: str = ".") -> str:
    """Download a BOEM bulk data file to dest_dir."""
    url_path = DOWNLOAD_FILES.get(filename)
    if url_path is None:
        raise ValueError(
            f"Unknown file '{filename}'. "
            f"Known files: {', '.join(sorted(DOWNLOAD_FILES))}"
        )

    url = f"{DATA_BASE}{url_path}"
    dest = os.path.join(dest_dir, filename)

    print(f"Downloading {url} -> {dest} ...")
    req = urllib.request.Request(url)
    req.add_header("User-Agent", "boem-skill/1.0")

    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            with open(dest, "wb") as fout:
                while True:
                    chunk = resp.read(65536)
                    if not chunk:
                        break
                    fout.write(chunk)
    except urllib.error.HTTPError as exc:
        print(f"HTTP {exc.code}: {exc.reason}", file=sys.stderr)
        sys.exit(1)

    size_mb = os.path.getsize(dest) / (1024 * 1024)
    print(f"Done. {size_mb:.1f} MB written to {dest}")
    return dest


# ---------------------------------------------------------------------------
# Output formatting
# ---------------------------------------------------------------------------


def print_features(features: list, layer_name: str) -> None:
    """Print features as a readable table."""
    if not features:
        print("No features returned.")
        return

    # Extract field names from first feature
    fields = list(features[0]["attributes"].keys())

    # Header
    header = " | ".join(f"{f:20s}" for f in fields)
    print(header)
    print("-" * len(header))

    # Rows
    for feat in features:
        attrs = feat["attributes"]
        row = " | ".join(f"{str(attrs.get(f, '')):20s}" for f in fields)
        print(row)

    print(f"\n({len(features)} records)")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> None:
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)

    cmd = sys.argv[1]

    # Parse optional flags
    args = sys.argv[2:]
    status = None
    bbox = None
    limit = 10

    i = 0
    while i < len(args):
        if args[i] == "--status" and i + 1 < len(args):
            status = args[i + 1]
            i += 2
        elif args[i] == "--bbox" and i + 1 < len(args):
            bbox = args[i + 1]
            i += 2
        elif args[i] == "--limit" and i + 1 < len(args):
            limit = int(args[i + 1])
            i += 2
        else:
            i += 1

    if cmd == "count":
        layer_name = args[0] if args else "wells"
        count = get_count(layer_name)
        print(f"{layer_name}: {count:,} features")

    elif cmd == "download":
        filename = args[0] if args else "ogoradelimit.zip"
        download_file(filename)

    elif cmd in LAYERS:
        where = "1=1"
        if status:
            if cmd == "wells":
                where = f"STATUS='{status}'"
            elif cmd == "leases":
                where = f"LEASE_STATUS_CD='{status}'"

        data = gis_query(cmd, where=where, bbox=bbox, limit=limit)
        features = data.get("features", [])
        print_features(features, cmd)

    else:
        print(f"Unknown command: {cmd}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
