#!/usr/bin/env python3
"""crossref_client.py -- Minimal Crossref REST API client using only stdlib.

Usage:
    python crossref_client.py

Polite pool resolution order:
    1. ~/.config/crossref/credentials  (mailto=your@email.com)
    2. CROSSREF_MAILTO env var
    3. Omitted (public pool -- slower rate limits)

No API key required. The mailto parameter is optional but strongly
recommended for faster rate limits via the Crossref polite pool.
"""

from __future__ import annotations

import html
import json
import os
import re
import urllib.request
import urllib.parse
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterator, Optional


# ---------------------------------------------------------------------------
# Polite pool resolution
# ---------------------------------------------------------------------------

def resolve_mailto() -> str:
    """Resolve mailto address for Crossref polite pool."""
    creds_path = Path.home() / ".config" / "crossref" / "credentials"
    if creds_path.exists():
        for line in creds_path.read_text().splitlines():
            line = line.strip()
            if line.startswith("mailto="):
                return line.removeprefix("mailto=")

    return os.environ.get("CROSSREF_MAILTO", "")


# ---------------------------------------------------------------------------
# Query parameters
# ---------------------------------------------------------------------------

@dataclass
class SearchParams:
    """Parameters for a Crossref works search.

    Attributes:
        query:       Full-text search string
        query_bibliographic: Bibliographic-style search (title+author+year)
        query_title: Title-only search
        query_author: Author-only search
        filters:     Dict of filter name -> value
                     e.g. {"from-pub-date": "2023-01-01", "type": "journal-article"}
        select:      List of fields to return (reduces payload)
        rows:        Results per page (default 20, max 1000)
        offset:      Pagination offset (max 10000)
        cursor:      Deep paging cursor (use "*" for first request)
        sort:        Sort field (relevance, published, is-referenced-by-count, etc.)
        order:       Sort direction (asc, desc)
    """
    query: str = ""
    query_bibliographic: str = ""
    query_title: str = ""
    query_author: str = ""
    filters: dict[str, str] = field(default_factory=dict)
    select: list[str] = field(default_factory=list)
    rows: int = 20
    offset: int = 0
    cursor: str = ""
    sort: str = ""
    order: str = ""


# ---------------------------------------------------------------------------
# Client
# ---------------------------------------------------------------------------

BASE_URL = "https://api.crossref.org"


class CrossrefClient:
    """Thin wrapper around the Crossref REST API (stdlib only)."""

    def __init__(self, mailto: str = "") -> None:
        self.mailto = mailto or resolve_mailto()

    def _build_url(self, path: str, params: Optional[dict[str, str]] = None) -> str:
        """Build a full URL with query parameters."""
        if params is None:
            params = {}
        if self.mailto:
            params["mailto"] = self.mailto
        qs = urllib.parse.urlencode(params, doseq=True)
        url = f"{BASE_URL}/{path.lstrip('/')}"
        if qs:
            url = f"{url}?{qs}"
        return url

    def _get(self, url: str) -> dict[str, Any]:
        """Perform a GET request and return parsed JSON."""
        req = urllib.request.Request(url, headers={
            "User-Agent": f"CrossrefClient/1.0 (mailto:{self.mailto})"
                          if self.mailto
                          else "CrossrefClient/1.0",
        })
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))

    # -- Single DOI lookup ---------------------------------------------------

    def get_work(self, doi: str) -> dict[str, Any]:
        """Retrieve metadata for a single DOI.

        Args:
            doi: The DOI string (e.g. "10.1016/j.hydromet.2023.106070")

        Returns:
            The work object (message field from API response).
        """
        params: dict[str, str] = {}
        if self.mailto:
            params["mailto"] = self.mailto
        url = self._build_url(f"works/{doi}", params)
        body = self._get(url)
        return body["message"]

    # -- Search --------------------------------------------------------------

    def _search_params(self, p: SearchParams) -> dict[str, str]:
        """Convert SearchParams to URL query parameters."""
        params: dict[str, str] = {}
        if p.query:
            params["query"] = p.query
        if p.query_bibliographic:
            params["query.bibliographic"] = p.query_bibliographic
        if p.query_title:
            params["query.title"] = p.query_title
        if p.query_author:
            params["query.author"] = p.query_author
        if p.filters:
            params["filter"] = ",".join(f"{k}:{v}" for k, v in p.filters.items())
        if p.select:
            params["select"] = ",".join(p.select)
        params["rows"] = str(p.rows)
        if p.cursor:
            params["cursor"] = p.cursor
        elif p.offset:
            params["offset"] = str(p.offset)
        if p.sort:
            params["sort"] = p.sort
        if p.order:
            params["order"] = p.order
        return params

    def search(self, p: SearchParams) -> tuple[list[dict], int, str]:
        """Search works and return one page.

        Returns:
            (items, total_results, next_cursor)
            next_cursor is empty string if not using cursor pagination.
        """
        params = self._search_params(p)
        url = self._build_url("works", params)
        body = self._get(url)
        msg = body["message"]
        items = msg.get("items", [])
        total = msg.get("total-results", 0)
        next_cursor = msg.get("next-cursor", "")
        return items, total, next_cursor

    def search_all(self, p: SearchParams, max_results: int = 1000) -> list[dict]:
        """Search works and paginate through all results (up to max_results).

        Uses cursor-based pagination for reliability.
        """
        all_items: list[dict] = []
        p.cursor = "*"
        p.rows = min(100, max_results)

        while len(all_items) < max_results:
            items, total, next_cursor = self.search(p)
            if not items:
                break
            all_items.extend(items)
            if not next_cursor or len(all_items) >= total:
                break
            p.cursor = next_cursor

        return all_items[:max_results]

    def paginate(self, p: SearchParams) -> Iterator[list[dict]]:
        """Yield one page of results at a time using cursor pagination."""
        p.cursor = "*"

        while True:
            items, total, next_cursor = self.search(p)
            if not items:
                break
            yield items
            if not next_cursor:
                break
            p.cursor = next_cursor


# ---------------------------------------------------------------------------
# Utility functions
# ---------------------------------------------------------------------------

def format_date(date_obj: Optional[dict]) -> str:
    """Format a Crossref date-parts object to a human-readable string.

    Handles variable-length date-parts:
        [[2024, 3, 15]] -> "2024-03-15"
        [[2024, 3]]     -> "2024-03"
        [[2024]]        -> "2024"
    """
    if not date_obj or "date-parts" not in date_obj:
        return "n/a"
    parts = date_obj["date-parts"]
    if not parts or not parts[0]:
        return "n/a"
    dp = parts[0]
    if len(dp) >= 3:
        return f"{dp[0]}-{dp[1]:02d}-{dp[2]:02d}"
    elif len(dp) == 2:
        return f"{dp[0]}-{dp[1]:02d}"
    else:
        return str(dp[0])


def format_authors(authors: list[dict], max_authors: int = 3) -> str:
    """Format an author list to a compact string.

    Returns "Family1 GI, Family2 GI, ... et al." if truncated.
    """
    if not authors:
        return "n/a"
    names = []
    for a in authors[:max_authors]:
        if "family" in a:
            given = a.get("given", "")
            initials = "".join(w[0] for w in given.split() if w) if given else ""
            names.append(f"{a['family']} {initials}".strip())
        elif "name" in a:
            names.append(a["name"])
    result = ", ".join(names)
    if len(authors) > max_authors:
        result += f" et al. ({len(authors)} authors)"
    return result


def strip_jats(text: str) -> str:
    """Strip JATS XML tags and decode HTML entities from abstract text."""
    text = re.sub(r"<[^>]+>", "", text)
    text = html.unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def doi_url(doi: str) -> str:
    """Return the canonical DOI URL."""
    return f"https://doi.org/{doi}"


# ---------------------------------------------------------------------------
# Display helpers
# ---------------------------------------------------------------------------

def print_work(work: dict) -> None:
    """Print a single work as a formatted metadata block."""
    title = work.get("title", ["(no title)"])[0]
    authors = format_authors(work.get("author", []))
    journal = (work.get("container-title") or ["n/a"])[0]
    date = format_date(work.get("published-print") or work.get("published-online"))
    wtype = work.get("type", "unknown")
    citations = work.get("is-referenced-by-count", 0)
    doi = work.get("DOI", "n/a")

    print(f"  Title:     {title}")
    print(f"  Authors:   {authors}")
    print(f"  Journal:   {journal}")
    print(f"  Date:      {date}")
    print(f"  Type:      {wtype}")
    print(f"  Citations: {citations}")
    print(f"  DOI:       {doi}")
    print(f"  URL:       {doi_url(doi)}")

    abstract = work.get("abstract", "")
    if abstract:
        clean = strip_jats(abstract)
        if len(clean) > 300:
            clean = clean[:297] + "..."
        print(f"  Abstract:  {clean}")
    print()


def print_table(items: list[dict], max_rows: int = 20) -> None:
    """Print search results as a fixed-width table."""
    header = f"{'#':>3}  {'Year':<6} {'Citations':>9}  {'Type':<20} {'Title'}"
    print(header)
    print("-" * min(len(header) + 40, 120))

    for i, item in enumerate(items[:max_rows], 1):
        title = (item.get("title") or ["(no title)"])[0]
        if len(title) > 60:
            title = title[:57] + "..."
        date = format_date(item.get("published-print") or item.get("published-online"))
        year = date[:4] if date != "n/a" else "n/a"
        citations = item.get("is-referenced-by-count", 0)
        wtype = item.get("type", "unknown")
        if len(wtype) > 18:
            wtype = wtype[:18]
        print(f"{i:>3}  {year:<6} {citations:>9}  {wtype:<20} {title}")

    if len(items) > max_rows:
        print(f"... ({len(items) - max_rows} more results)")


# ---------------------------------------------------------------------------
# Example usage
# ---------------------------------------------------------------------------

def main() -> None:
    client = CrossrefClient()

    # Example 1: Look up a specific DOI
    print("=" * 70)
    print("Example 1: DOI Lookup")
    print("=" * 70)
    print()
    try:
        work = client.get_work("10.2118/1011-0046-jpt")
        print_work(work)
    except Exception as e:
        print(f"  Error: {e}\n")

    # Example 2: Search for lithium extraction from produced water
    print("=" * 70)
    print("Example 2: Search — lithium extraction produced water (2020+, journal articles)")
    print("=" * 70)
    print()
    items, total, _ = client.search(SearchParams(
        query="lithium extraction produced water oilfield brine",
        filters={
            "from-pub-date": "2020-01-01",
            "type": "journal-article",
            "has-abstract": "true",
        },
        select=[
            "DOI", "title", "author", "type",
            "published-print", "container-title",
            "is-referenced-by-count",
        ],
        sort="is-referenced-by-count",
        order="desc",
        rows=10,
    ))
    print(f"Total results: {total}  |  Showing: {len(items)}\n")
    print_table(items)
    print()

    # Example 3: Bibliographic search (matching a known citation)
    print("=" * 70)
    print("Example 3: Bibliographic Search")
    print("=" * 70)
    print()
    items, total, _ = client.search(SearchParams(
        query_bibliographic="Munk 2016 lithium brine Smackover",
        select=["DOI", "title", "author", "published-print", "container-title"],
        rows=3,
    ))
    print(f"Total results: {total}  |  Showing: {len(items)}\n")
    for item in items:
        print_work(item)

    # Example 4: DOE-funded lithium research
    print("=" * 70)
    print("Example 4: DOE-funded lithium research (funder filter)")
    print("=" * 70)
    print()
    items, total, _ = client.search(SearchParams(
        query="lithium brine extraction",
        filters={
            "funder": "10.13039/100000015",
            "from-pub-date": "2020-01-01",
        },
        select=[
            "DOI", "title", "author", "type",
            "published-print", "container-title",
            "is-referenced-by-count",
        ],
        sort="is-referenced-by-count",
        order="desc",
        rows=10,
    ))
    print(f"Total DOE-funded results: {total}  |  Showing: {len(items)}\n")
    print_table(items)


if __name__ == "__main__":
    main()
