#!/usr/bin/env python3
"""edx_client.py — Minimal NETL EDX (CKAN v3) client using only stdlib.

Usage:
    python python_example.py

Credential resolution order:
    1. ~/.config/netl-edx/credentials  (api_key=YOUR_KEY)
    2. NETL_EDX_API_KEY env var
    3. Raises RuntimeError with setup instructions

Note: Most read-only operations work without a key for public datasets.
A key is recommended for reliable access and required for private data.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any, Optional
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


# ---------------------------------------------------------------------------
# Credential resolution
# ---------------------------------------------------------------------------

def resolve_api_key() -> Optional[str]:
    """Resolve NETL EDX API key from credentials file or env var.

    Returns None if no key found (read-only public access still works).
    """
    creds_path = Path.home() / ".config" / "netl-edx" / "credentials"
    if creds_path.exists():
        for line in creds_path.read_text().splitlines():
            line = line.strip()
            if line.startswith("api_key="):
                return line.removeprefix("api_key=")

    key = os.environ.get("NETL_EDX_API_KEY", "")
    if key:
        return key

    return None


def require_api_key() -> str:
    """Resolve API key or raise with setup instructions."""
    key = resolve_api_key()
    if key:
        return key
    raise RuntimeError(
        "No NETL EDX API key found. Store it in ~/.config/netl-edx/credentials as:\n"
        "  api_key=YOUR_KEY\n"
        "Or set the NETL_EDX_API_KEY environment variable.\n"
        "Get a free key at https://edx.netl.doe.gov/ -> Sign up -> Profile -> API Key"
    )


# ---------------------------------------------------------------------------
# Client
# ---------------------------------------------------------------------------

BASE_URL = "https://edx.netl.doe.gov/api/3/action"


class EDXClient:
    """Thin wrapper around the NETL EDX CKAN v3 API (stdlib only)."""

    def __init__(self, api_key: Optional[str] = None) -> None:
        self.api_key = api_key or resolve_api_key()

    def _request(self, action: str, params: Optional[dict[str, Any]] = None) -> dict:
        """Make a GET request to a CKAN action endpoint."""
        url = f"{BASE_URL}/{action}"
        if params:
            url = f"{url}?{urlencode(params, doseq=True)}"

        req = Request(url)
        if self.api_key:
            req.add_header("EDX-API-Key", self.api_key)

        try:
            with urlopen(req, timeout=30) as resp:
                body = json.loads(resp.read().decode())
        except HTTPError as e:
            body_text = e.read().decode() if e.fp else ""
            raise RuntimeError(
                f"EDX API error: HTTP {e.code} on {action}\n{body_text}"
            ) from e

        if not body.get("success"):
            error = body.get("error", {})
            raise RuntimeError(f"EDX API error on {action}: {error}")

        return body["result"]

    # --- Search ---

    def search_datasets(
        self,
        query: str,
        rows: int = 10,
        start: int = 0,
        fq: Optional[str] = None,
        sort: str = "score desc",
    ) -> dict:
        """Search datasets by keyword.

        Returns dict with 'count' (total matches) and 'results' (list of datasets).
        """
        params: dict[str, Any] = {
            "q": query,
            "rows": rows,
            "start": start,
            "sort": sort,
        }
        if fq:
            params["fq"] = fq
        return self._request("package_search", params)

    def search_resources(
        self, query: str, limit: int = 10, offset: int = 0
    ) -> dict:
        """Search resources (files) across all datasets.

        query format: 'field:value' (e.g., 'format:CSV', 'name:lithium')
        Returns dict with 'count' and 'results'.
        """
        return self._request(
            "resource_search",
            {"query": query, "limit": limit, "offset": offset},
        )

    # --- Details ---

    def get_dataset(self, name_or_id: str) -> dict:
        """Get full metadata for a dataset by slug name or UUID."""
        return self._request("package_show", {"id": name_or_id})

    def get_group(
        self,
        name_or_id: str,
        include_datasets: bool = False,
    ) -> dict:
        """Get group details, optionally including its datasets."""
        params: dict[str, Any] = {
            "id": name_or_id,
            "include_dataset_count": True,
        }
        if include_datasets:
            params["include_datasets"] = True
        return self._request("group_show", params)

    # --- Listing ---

    def list_groups(self) -> list[str]:
        """List all group names (slugs)."""
        return self._request("group_list")

    def list_tags(self, query: str = "") -> list[str]:
        """List tags, optionally filtered by prefix."""
        params = {}
        if query:
            params["query"] = query
        return self._request("tag_list", params)

    # --- Download ---

    def download_resource(self, url: str, dest: str) -> int:
        """Download a resource file to a local path.

        Returns the number of bytes written.
        """
        req = Request(url)
        if self.api_key:
            req.add_header("EDX-API-Key", self.api_key)

        with urlopen(req, timeout=120) as resp:
            data = resp.read()

        Path(dest).write_bytes(data)
        return len(data)


# ---------------------------------------------------------------------------
# Helper: print a summary table
# ---------------------------------------------------------------------------

def print_dataset_table(datasets: list[dict], max_rows: int = 20) -> None:
    """Print a formatted table of dataset search results."""
    cols = {
        "name": 50,
        "num_resources": 5,
        "metadata_modified": 20,
    }
    header = f"{'Dataset Name':<50}  {'Res':>5}  {'Last Modified':<20}"
    print(header)
    print("-" * len(header))
    for ds in datasets[:max_rows]:
        name = ds.get("name", "")[:50]
        nres = ds.get("num_resources", 0)
        mod = ds.get("metadata_modified", "")[:10]
        print(f"{name:<50}  {nres:>5}  {mod:<20}")
    total = len(datasets)
    if total > max_rows:
        print(f"... ({total - max_rows} more datasets)")


# ---------------------------------------------------------------------------
# Example usage
# ---------------------------------------------------------------------------

def main() -> None:
    client = EDXClient()  # key is optional for public reads

    # Example 1: Search for lithium-related datasets
    print("=== EDX: Lithium Datasets ===\n")
    results = client.search_datasets("lithium", rows=10)
    print(f"Total matches: {results['count']}\n")
    print_dataset_table(results["results"])

    print()

    # Example 2: Search within ClaiMM group
    print("=== EDX: ClaiMM Critical Minerals Datasets ===\n")
    results = client.search_datasets(
        "critical minerals",
        fq="groups:claimm-datasets",
        rows=5,
        sort="metadata_modified desc",
    )
    print(f"Total matches: {results['count']}\n")
    print_dataset_table(results["results"])

    print()

    # Example 3: Get details for a specific dataset
    print("=== EDX: Dataset Details ===\n")
    ds = client.get_dataset(
        "lithium-geochemistry-and-regional-production-decline-curves-"
        "of-marcellus-shale-produced-water"
    )
    print(f"Title: {ds['title']}")
    print(f"Description: {ds['notes'][:200]}...")
    print(f"Resources ({len(ds.get('resources', []))}):")
    for r in ds.get("resources", []):
        size_kb = r.get("size", 0) / 1024
        print(f"  - {r['name']} ({r['format']}, {size_kb:.0f} KB)")
        print(f"    URL: {r['url']}")

    print()

    # Example 4: List tags matching a prefix
    print("=== EDX: Tags starting with 'lithium' ===\n")
    tags = client.list_tags("lithium")
    for t in tags:
        print(f"  {t}")

    print()

    # Example 5: Search for CSV resources
    print("=== EDX: CSV Resources (first 5) ===\n")
    res = client.search_resources("format:CSV", limit=5)
    print(f"Total CSV resources: {res['count']}\n")
    for r in res["results"]:
        print(f"  {r['name']} ({r.get('size', 0)} bytes)")


if __name__ == "__main__":
    main()
