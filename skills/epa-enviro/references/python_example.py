#!/usr/bin/env python3
"""epa_client.py -- Minimal EPA Envirofacts + ECHO client using only stdlib.

Usage:
    python epa_client.py

No API key required. Both Envirofacts and ECHO are publicly accessible.

This client demonstrates:
    1. Querying Envirofacts REST API (TRI facilities, release data)
    2. Querying ECHO two-step search (CWA, RCRA, SDW)
    3. Cross-referencing facilities via FRS registry ID
"""

from __future__ import annotations

import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from typing import Any


# ---------------------------------------------------------------------------
# HTTP helper (stdlib only)
# ---------------------------------------------------------------------------

def http_get(url: str, params: dict[str, str] | None = None) -> Any:
    """Perform an HTTP GET and return parsed JSON.

    Raises RuntimeError on HTTP errors with the status code and body.
    """
    if params:
        url = url + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url)
    req.add_header("Accept", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode("utf-8")
            return json.loads(raw)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {e.code}: {body[:500]}") from e


# ---------------------------------------------------------------------------
# Envirofacts client
# ---------------------------------------------------------------------------

EFSERVICE_BASE = "https://data.epa.gov/efservice"


@dataclass
class EnvirofactsQuery:
    """Parameters for an Envirofacts REST query.

    Attributes:
        table:      Table name (e.g. TRI_FACILITY, FRS_FACILITY_SITE)
        filters:    Column/value pairs for filtering,
                    e.g. [("STATE_ABBR", "WV"), ("COUNTY_NAME", "MONONGALIA")]
        row_start:  Starting row (0-based)
        row_end:    Ending row (inclusive)
        fmt:        Response format (JSON, XML, CSV)
    """
    table: str
    filters: list[tuple[str, str]] = field(default_factory=list)
    row_start: int = 0
    row_end: int = 99
    fmt: str = "JSON"


def envirofacts_url(q: EnvirofactsQuery) -> str:
    """Build the Envirofacts REST URL from query parameters."""
    parts = [EFSERVICE_BASE, q.table]
    for col, val in q.filters:
        parts.append(col)
        parts.append(urllib.parse.quote(val, safe=""))
    parts.append(f"rows/{q.row_start}:{q.row_end}")
    parts.append(q.fmt)
    return "/".join(parts)


def envirofacts_fetch(q: EnvirofactsQuery) -> list[dict]:
    """Fetch rows from Envirofacts. Returns a list of row dicts."""
    url = envirofacts_url(q)
    data = http_get(url)
    if isinstance(data, dict) and "error" in data:
        raise RuntimeError(f"Envirofacts error: {data['error']}")
    return data


# ---------------------------------------------------------------------------
# ECHO client
# ---------------------------------------------------------------------------

ECHO_BASE = "https://echodata.epa.gov/echo"


@dataclass
class EchoSearch:
    """Parameters for an ECHO two-step search.

    Attributes:
        program:    Program family (cwa, rcra, sdw, air)
        params:     Search parameters (p_st, p_co, p_sic, etc.)
        pagesize:   Records per page for retrieval
    """
    program: str
    params: dict[str, str] = field(default_factory=dict)
    pagesize: int = 20


def echo_search(s: EchoSearch) -> tuple[str, int]:
    """Execute ECHO search step 1. Returns (query_id, total_rows)."""
    # Determine the service name based on program
    svc_map = {
        "cwa": "cwa_rest_services",
        "rcra": "rcra_rest_services",
        "sdw": "sdw_rest_services",
        "air": "air_rest_services",
    }
    svc = svc_map.get(s.program)
    if not svc:
        raise ValueError(f"Unknown ECHO program: {s.program}")

    # SDW uses get_systems, others use get_facilities
    action = "get_systems" if s.program == "sdw" else "get_facilities"

    all_params = {"output": "JSON"}
    all_params.update(s.params)

    url = f"{ECHO_BASE}/{svc}.{action}"
    data = http_get(url, all_params)

    results = data.get("Results", {})
    if "Error" in results:
        raise RuntimeError(f"ECHO error: {results['Error']['ErrorMessage']}")

    qid = results["QueryID"]
    total = int(results["QueryRows"])
    return qid, total


def echo_retrieve(
    program: str, query_id: str, page: int = 1, pagesize: int = 20
) -> list[dict]:
    """Execute ECHO search step 2. Returns list of facility/system dicts."""
    svc_map = {
        "cwa": "cwa_rest_services",
        "rcra": "rcra_rest_services",
        "sdw": "sdw_rest_services",
        "air": "air_rest_services",
    }
    svc = svc_map[program]
    url = f"{ECHO_BASE}/{svc}.get_qid"
    params = {
        "output": "JSON",
        "qid": query_id,
        "pageno": str(page),
        "pagesize": str(pagesize),
    }
    data = http_get(url, params)
    results = data.get("Results", {})

    # Response key differs by program
    key_map = {
        "cwa": "Facilities",
        "rcra": "Facilities",
        "sdw": "WaterSystems",
        "air": "Facilities",
    }
    return results.get(key_map[program], [])


# ---------------------------------------------------------------------------
# Display helpers
# ---------------------------------------------------------------------------

def print_table(rows: list[dict], cols: list[str], max_rows: int = 20) -> None:
    """Print a fixed-width table from a list of row dicts."""
    if not rows:
        print("(no results)")
        return
    display = rows[:max_rows]
    widths = {}
    for c in cols:
        vals = [str(r.get(c, "") or "") for r in display]
        widths[c] = max(len(c), *(len(v) for v in vals))
    header = " | ".join(c.ljust(widths[c]) for c in cols)
    sep = "-+-".join("-" * widths[c] for c in cols)
    print(header)
    print(sep)
    for row in display:
        print(" | ".join(str(row.get(c, "") or "").ljust(widths[c]) for c in cols))
    if len(rows) > max_rows:
        print(f"... ({len(rows) - max_rows} more rows)")


# ---------------------------------------------------------------------------
# Example usage
# ---------------------------------------------------------------------------

def example_tri_facilities() -> None:
    """Example: Find TRI facilities in Monongalia County, WV."""
    print("=" * 60)
    print("Example 1: TRI Facilities — Monongalia County, WV")
    print("=" * 60)

    rows = envirofacts_fetch(EnvirofactsQuery(
        table="TRI_FACILITY",
        filters=[("STATE_ABBR", "WV"), ("COUNTY_NAME", "MONONGALIA")],
        row_start=0,
        row_end=9,
    ))
    print(f"\nFetched {len(rows)} TRI facilities\n")
    print_table(rows, ["tri_facility_id", "facility_name", "city_name", "fac_closed_ind"])


def example_frs_cross_reference() -> None:
    """Example: Find all EPA program links for WV facilities."""
    print("\n" + "=" * 60)
    print("Example 2: FRS Program Cross-References — WV (first 10)")
    print("=" * 60)

    rows = envirofacts_fetch(EnvirofactsQuery(
        table="FRS_PROGRAM_FACILITY",
        filters=[("STATE_CODE", "WV")],
        row_start=0,
        row_end=9,
    ))
    print(f"\nFetched {len(rows)} FRS program links\n")
    print_table(rows, ["registry_id", "primary_name", "pgm_sys_acrnm", "pgm_sys_id"])


def example_echo_cwa() -> None:
    """Example: Search ECHO for CWA facilities in Monongalia County."""
    print("\n" + "=" * 60)
    print("Example 3: ECHO CWA Facilities — Monongalia County, WV")
    print("=" * 60)

    search = EchoSearch(
        program="cwa",
        params={"p_st": "WV", "p_co": "MONONGALIA"},
        pagesize=5,
    )
    qid, total = echo_search(search)
    print(f"\nQuery ID: {qid}  |  Total facilities: {total}\n")

    facilities = echo_retrieve("cwa", qid, page=1, pagesize=5)
    print_table(
        facilities,
        ["CWPName", "SourceID", "CWPCity", "CWPPermitStatusDesc"],
    )


def example_echo_sdw() -> None:
    """Example: Search ECHO for drinking water systems in Monongalia County."""
    print("\n" + "=" * 60)
    print("Example 4: ECHO SDW — Drinking Water Systems, Monongalia Co., WV")
    print("=" * 60)

    search = EchoSearch(
        program="sdw",
        params={"p_st": "WV", "p_co": "MONONGALIA"},
        pagesize=5,
    )
    qid, total = echo_search(search)
    print(f"\nQuery ID: {qid}  |  Total systems: {total}\n")

    systems = echo_retrieve("sdw", qid, page=1, pagesize=5)
    print_table(
        systems,
        ["PWSName", "PWSId", "PWSTypeDesc", "PrimarySourceDesc", "PopulationServedCount"],
    )


def main() -> None:
    try:
        example_tri_facilities()
        example_frs_cross_reference()
        example_echo_cwa()
        example_echo_sdw()
    except RuntimeError as e:
        print(f"\nError: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
