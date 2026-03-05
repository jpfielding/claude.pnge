#!/usr/bin/env python3
"""osti_client.py — Minimal DOE OSTI API v1 client using only Python stdlib.

Usage:
    python python_example.py

No API key required. Searches DOE OSTI for technical reports, journal
articles, and research data from DOE-funded energy research.
"""

from __future__ import annotations

import json
import re
import textwrap
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from typing import Any


BASE_URL = "https://www.osti.gov/api/v1/records"


# ---------------------------------------------------------------------------
# Query params
# ---------------------------------------------------------------------------

@dataclass
class SearchParams:
    """Parameters for an OSTI search request.

    Attributes:
        q:             Full-text keyword search across all fields.
        title:         Search within title field only.
        author:        Search by author name.
        sponsor_org:   Filter by DOE sponsoring organization (e.g. "NETL").
        research_org:  Filter by performing research organization.
        product_type:  Filter by publication type
                       (e.g. "Technical Report", "Journal Article").
        rows:          Results per page (default 20).
        page:          Page number, 1-indexed (default 1).
    """
    q: str = ""
    title: str = ""
    author: str = ""
    sponsor_org: str = ""
    research_org: str = ""
    product_type: str = ""
    rows: int = 20
    page: int = 1


# ---------------------------------------------------------------------------
# Client
# ---------------------------------------------------------------------------

class OSTIClient:
    """Thin wrapper around the DOE OSTI API v1."""

    def __init__(self) -> None:
        pass

    @staticmethod
    def _build_url(params: SearchParams) -> str:
        """Build the query URL from search parameters."""
        query: dict[str, Any] = {}

        if params.q:
            query["q"] = params.q
        if params.title:
            query["title"] = params.title
        if params.author:
            query["author"] = params.author
        if params.sponsor_org:
            query["sponsor_org"] = params.sponsor_org
        if params.research_org:
            query["research_org"] = params.research_org
        if params.product_type:
            query["product_type"] = params.product_type

        query["rows"] = params.rows
        query["page"] = params.page

        return f"{BASE_URL}?{urllib.parse.urlencode(query)}"

    def search(self, params: SearchParams) -> tuple[list[dict], int]:
        """Search OSTI and return (records, total_count).

        The total count comes from the X-Total-Count response header.
        Records are returned as a list of dicts.
        """
        url = self._build_url(params)
        req = urllib.request.Request(url, headers={"Accept": "application/json"})

        with urllib.request.urlopen(req) as resp:
            total = int(resp.headers.get("X-Total-Count", "0"))
            body = json.loads(resp.read().decode("utf-8"))

        return body, total

    def get_record(self, osti_id: str) -> dict | None:
        """Fetch a single record by OSTI ID.

        Returns the record dict, or None if not found.
        """
        url = f"{BASE_URL}/{osti_id}"
        req = urllib.request.Request(url, headers={"Accept": "application/json"})

        try:
            with urllib.request.urlopen(req) as resp:
                body = json.loads(resp.read().decode("utf-8"))
            if body:
                return body[0]
            return None
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            raise

    def search_all(self, params: SearchParams) -> list[dict]:
        """Fetch all pages of results for a search query.

        Warning: may be slow for large result sets. Consider using
        search() with pagination for better control.
        """
        all_records: list[dict] = []
        params.page = 1

        while True:
            records, total = self.search(params)
            all_records.extend(records)
            if len(all_records) >= total or not records:
                break
            params.page += 1

        return all_records


# ---------------------------------------------------------------------------
# Display helpers
# ---------------------------------------------------------------------------

def strip_html(text: str) -> str:
    """Remove HTML tags from a string."""
    return re.sub(r"<[^>]+>", "", text)


def format_record(rec: dict, index: int = 0) -> str:
    """Format a single OSTI record for terminal display."""
    title = strip_html(rec.get("title", "Untitled"))
    authors = rec.get("authors", [])
    author_str = "; ".join(a.split(" [")[0] for a in authors[:3])
    if len(authors) > 3:
        author_str += f" et al. ({len(authors)} authors)"

    pub_date = rec.get("publication_date", "Unknown")[:10]
    product_type = rec.get("product_type", "Unknown")
    osti_id = rec.get("osti_id", "?")
    doi = rec.get("doi", "")

    abstract = strip_html(rec.get("description", ""))
    if len(abstract) > 200:
        abstract = abstract[:197] + "..."

    sponsors = rec.get("sponsor_orgs", [])
    sponsor_str = "; ".join(sponsors[:2])
    if len(sponsors) > 2:
        sponsor_str += f" (+{len(sponsors) - 2} more)"

    lines = [
        f"  [{index}] {title}",
        f"      Authors:  {author_str}" if author_str else "",
        f"      Date:     {pub_date}  |  Type: {product_type}",
        f"      OSTI ID:  {osti_id}" + (f"  |  DOI: {doi}" if doi else ""),
        f"      Sponsor:  {sponsor_str}" if sponsor_str else "",
        f"      Abstract: {abstract}" if abstract else "",
    ]
    return "\n".join(line for line in lines if line)


def print_results(records: list[dict], total: int, query_desc: str) -> None:
    """Print formatted search results."""
    print(f"\n{'=' * 72}")
    print(f"  {query_desc}")
    print(f"  Total results: {total}  |  Showing: {len(records)}")
    print(f"{'=' * 72}\n")

    for i, rec in enumerate(records, 1):
        print(format_record(rec, i))
        print()


# ---------------------------------------------------------------------------
# Example usage
# ---------------------------------------------------------------------------

def main() -> None:
    client = OSTIClient()

    # Example 1: Search for lithium in produced water research
    print("\n--- Example 1: Keyword search ---")
    records, total = client.search(SearchParams(
        q="lithium produced water",
        rows=5,
    ))
    print_results(records, total, "Search: 'lithium produced water'")

    # Example 2: NETL-sponsored technical reports on critical minerals
    print("\n--- Example 2: NETL technical reports ---")
    records, total = client.search(SearchParams(
        q="critical minerals",
        sponsor_org="NETL",
        product_type="Technical Report",
        rows=5,
    ))
    print_results(records, total, "NETL Technical Reports: 'critical minerals'")

    # Example 3: Look up a specific record by OSTI ID
    print("\n--- Example 3: Single record lookup ---")
    rec = client.get_record("2588655")
    if rec:
        print(f"\n{'=' * 72}")
        print(f"  Record OSTI ID: 2588655")
        print(f"{'=' * 72}\n")
        print(format_record(rec, 1))

        # Show all links
        links = rec.get("links", [])
        if links:
            print("\n      Links:")
            for link in links:
                print(f"        [{link['rel']}] {link['href']}")
    else:
        print("  Record not found.")

    # Example 4: Author search
    print("\n\n--- Example 4: Author search ---")
    records, total = client.search(SearchParams(
        author="Stuckman",
        rows=5,
    ))
    print_results(records, total, "Author search: 'Stuckman'")


if __name__ == "__main__":
    main()
