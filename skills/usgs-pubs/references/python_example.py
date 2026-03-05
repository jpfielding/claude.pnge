#!/usr/bin/env python3
"""usgs_pubs_client.py — Minimal USGS Publications Warehouse API client.

Uses only Python standard library (urllib, json). No API key required.

Usage:
    python python_example.py
"""

from __future__ import annotations

import json
import sys
import urllib.request
import urllib.parse
from dataclasses import dataclass, field
from typing import Any, Optional
import html


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

BASE_URL = "https://pubs.usgs.gov/pubs-services/publication"


# ---------------------------------------------------------------------------
# Query params
# ---------------------------------------------------------------------------

@dataclass
class SearchParams:
    """Parameters for a USGS Publications Warehouse search.

    Attributes:
        q:                  Free-text keyword search.
        title:              Search within titles only.
        year:               Filter by publication year.
        type_name:          Filter by publication type (Report, Article).
        subtype_name:       Filter by subtype (USGS Numbered Series, Journal Article).
        contributing_office: Filter by USGS office name.
        pub_x_days:         Publications released in last X days.
        page_size:          Results per page (default 25).
        page_number:        Page number, 1-indexed (default 1).
    """
    q: str = ""
    title: str = ""
    year: str = ""
    type_name: str = ""
    subtype_name: str = ""
    contributing_office: str = ""
    pub_x_days: int = 0
    page_size: int = 25
    page_number: int = 1

    def to_query_string(self) -> str:
        """Build URL query string from non-empty parameters."""
        params: dict[str, str] = {}
        if self.q:
            params["q"] = self.q
        if self.title:
            params["title"] = self.title
        if self.year:
            params["year"] = self.year
        if self.type_name:
            params["typeName"] = self.type_name
        if self.subtype_name:
            params["subtypeName"] = self.subtype_name
        if self.contributing_office:
            params["contributingOffice"] = self.contributing_office
        if self.pub_x_days > 0:
            params["pub_x_days"] = str(self.pub_x_days)
        params["page_size"] = str(self.page_size)
        params["page_number"] = str(self.page_number)
        return urllib.parse.urlencode(params)


# ---------------------------------------------------------------------------
# Client
# ---------------------------------------------------------------------------

class USGSPubsClient:
    """Client for the USGS Publications Warehouse API."""

    def __init__(self) -> None:
        self.base_url = BASE_URL

    def _get_json(self, url: str) -> Any:
        """Fetch a URL and parse the JSON response."""
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode("utf-8"))

    def search(self, params: SearchParams) -> tuple[list[dict], int]:
        """Search publications.

        Returns:
            (records, total_count)
        """
        url = f"{self.base_url}?{params.to_query_string()}"
        data = self._get_json(url)
        records = data.get("records", [])
        total = data.get("recordCount", 0)
        return records, total

    def get_publication(self, pub_id: str) -> dict:
        """Get a single publication by indexId or numeric ID.

        Args:
            pub_id: The publication identifier, e.g. "fs20243052" or "70261664".
        """
        url = f"{self.base_url}/{pub_id}"
        return self._get_json(url)

    def search_all(self, params: SearchParams) -> list[dict]:
        """Search and paginate through all results.

        Warning: may make many requests for large result sets.
        """
        all_records: list[dict] = []
        params.page_number = 1

        while True:
            records, total = self.search(params)
            all_records.extend(records)
            if len(all_records) >= total or len(records) == 0:
                break
            params.page_number += 1

        return all_records


# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------

def strip_html(text: str) -> str:
    """Remove HTML tags and decode entities from a string."""
    import re
    clean = re.sub(r"<[^>]+>", "", text)
    return html.unescape(clean).strip()


def format_record(rec: dict) -> str:
    """Format a publication record as a readable text block."""
    lines = []

    title = rec.get("title", "Untitled")
    year = rec.get("publicationYear", "n.d.")
    pub_type = rec.get("publicationType", {}).get("text", "")
    subtype = rec.get("publicationSubtype", {}).get("text", "")
    series = rec.get("seriesTitle", {}).get("text", "")
    series_num = rec.get("seriesNumber", "")
    doi = rec.get("doi", "")
    index_id = rec.get("indexId", str(rec.get("id", "")))

    # Authors
    authors_list = rec.get("contributors", {}).get("authors", [])
    if authors_list:
        author_names = []
        for a in authors_list[:5]:
            name = f"{a.get('family', '')}, {a.get('given', '')}"
            author_names.append(name.strip(", "))
        if len(authors_list) > 5:
            author_names.append(f"et al. ({len(authors_list)} total)")
        authors_str = "; ".join(author_names)
    else:
        authors_str = "Unknown"

    lines.append(f"  Title:   {title}")
    lines.append(f"  Authors: {authors_str}")
    lines.append(f"  Year:    {year}")

    type_str = f"{pub_type}"
    if subtype:
        type_str += f" / {subtype}"
    if series:
        type_str += f" / {series}"
    if series_num:
        type_str += f" {series_num}"
    lines.append(f"  Type:    {type_str}")

    if doi:
        lines.append(f"  DOI:     https://doi.org/{doi}")
    lines.append(f"  ID:      {index_id}")

    # PDF link
    for link in rec.get("links", []):
        link_type = link.get("type", {}).get("text", "")
        if link_type == "Document":
            lines.append(f"  PDF:     {link.get('url', '')}")
            break

    # Abstract snippet
    abstract = rec.get("docAbstract", "")
    if abstract:
        clean = strip_html(abstract)
        if len(clean) > 200:
            clean = clean[:200] + "..."
        lines.append(f"  Abstract: {clean}")

    return "\n".join(lines)


def print_table(records: list[dict], max_rows: int = 20) -> None:
    """Print a summary table of publication records."""
    rows = []
    for rec in records[:max_rows]:
        year = rec.get("publicationYear", "")
        title = rec.get("title", "Untitled")
        if len(title) > 70:
            title = title[:67] + "..."
        series = rec.get("seriesTitle", {}).get("text", "")
        pub_type = rec.get("publicationType", {}).get("text", "")
        label = series if series else pub_type
        index_id = rec.get("indexId", str(rec.get("id", "")))
        rows.append((year, label[:20], title, index_id))

    if not rows:
        print("  (no results)")
        return

    # Column widths
    headers = ("Year", "Series/Type", "Title", "ID")
    widths = [
        max(len(headers[i]), *(len(str(r[i])) for r in rows))
        for i in range(len(headers))
    ]

    header_line = "  ".join(h.ljust(w) for h, w in zip(headers, widths))
    print(header_line)
    print("-" * len(header_line))
    for row in rows:
        print("  ".join(str(v).ljust(w) for v, w in zip(row, widths)))
    if len(records) > max_rows:
        print(f"  ... ({len(records) - max_rows} more records)")


# ---------------------------------------------------------------------------
# Example usage
# ---------------------------------------------------------------------------

def main() -> None:
    client = USGSPubsClient()

    # Example 1: Search for lithium + produced water publications
    print("=" * 72)
    print("Example 1: Keyword search — lithium produced water")
    print("=" * 72)
    records, total = client.search(SearchParams(
        q="lithium produced water",
        page_size=10,
    ))
    print(f"Total results: {total}  |  Showing: {len(records)}\n")
    print_table(records)

    print()

    # Example 2: USGS Reports only, year 2024
    print("=" * 72)
    print("Example 2: USGS reports about lithium, year 2024")
    print("=" * 72)
    records, total = client.search(SearchParams(
        q="lithium",
        type_name="Report",
        year="2024",
        page_size=10,
    ))
    print(f"Total results: {total}  |  Showing: {len(records)}\n")
    print_table(records)

    print()

    # Example 3: Get a specific publication by indexId
    print("=" * 72)
    print("Example 3: Get specific publication — fs20243052")
    print("=" * 72)
    pub = client.get_publication("fs20243052")
    print(format_record(pub))

    print()

    # Example 4: Recent publications (last 30 days)
    print("=" * 72)
    print("Example 4: Publications released in the last 30 days")
    print("=" * 72)
    records, total = client.search(SearchParams(
        pub_x_days=30,
        page_size=10,
    ))
    print(f"Total results: {total}  |  Showing: {len(records)}\n")
    print_table(records)


if __name__ == "__main__":
    main()
