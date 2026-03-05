#!/usr/bin/env python3
"""usgs_water_client.py -- Minimal USGS Water Data client using only stdlib.

Queries USGS NWIS Water Services and the Water Quality Portal.
No API key required. No third-party dependencies.

Usage:
    python python_example.py

Examples demonstrated:
    1. Fetch daily mean discharge for a site
    2. Fetch site metadata
    3. Query the Water Quality Portal for lithium results
    4. Parse RDB (tab-delimited) format
"""

from __future__ import annotations

import csv
import io
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from typing import Any, Iterator


# ---------------------------------------------------------------------------
# NWIS Water Services client
# ---------------------------------------------------------------------------

NWIS_BASE = "https://waterservices.usgs.gov/nwis"
WQP_BASE = "https://www.waterqualitydata.us/data"


def _get(url: str, timeout: int = 60) -> str:
    """Issue a GET request and return the response body as text."""
    req = urllib.request.Request(url, headers={"User-Agent": "usgs-water-client/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            charset = resp.headers.get_content_charset() or "utf-8"
            return resp.read().decode(charset)
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(
            f"HTTP {exc.code} from {url}\n{body[:500]}"
        ) from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Connection error: {exc.reason}") from exc


def _get_json(url: str, timeout: int = 60) -> dict[str, Any]:
    """GET a URL and parse the response as JSON."""
    return json.loads(_get(url, timeout))


# ---------------------------------------------------------------------------
# RDB parser (NWIS tab-delimited format)
# ---------------------------------------------------------------------------

def parse_rdb(text: str) -> list[dict[str, str]]:
    """Parse USGS RDB format into a list of dicts.

    Skips comment lines (starting with #) and the second header row
    (column width/type specifiers like '5s', '15n').
    """
    lines = text.splitlines()
    data_lines: list[str] = []
    for line in lines:
        if line.startswith("#") or not line.strip():
            continue
        data_lines.append(line)

    if len(data_lines) < 2:
        return []

    headers = data_lines[0].split("\t")
    # data_lines[1] is the width/type row -- skip it
    rows: list[dict[str, str]] = []
    for line in data_lines[2:]:
        values = line.split("\t")
        row = {h: v.strip() for h, v in zip(headers, values)}
        rows.append(row)
    return rows


# ---------------------------------------------------------------------------
# NWIS queries
# ---------------------------------------------------------------------------

@dataclass
class NWISParams:
    """Parameters for an NWIS Water Services request.

    Attributes:
        endpoint:       iv, dv, site, stat, or gwlevels
        sites:          Comma-separated USGS site numbers
        state_cd:       2-letter state postal code
        county_cd:      3-digit county FIPS code
        huc:            Hydrologic unit code
        bbox:           Bounding box "west,south,east,north"
        site_type:      Site type code(s) comma-separated
        site_status:    active, inactive, or all
        parameter_cd:   5-digit parameter code(s) comma-separated
        start_dt:       Start date YYYY-MM-DD
        end_dt:         End date YYYY-MM-DD
        period:         ISO 8601 duration (e.g., P7D)
        stat_cd:        Statistic code for dv (00003=mean)
        stat_report:    For stat/: daily, monthly, annual
        stat_type:      For stat/: mean, min, max, median, all
        response_fmt:   json or rdb
        site_output:    basic or expanded (for site/)
        has_data_type:  iv, dv, gw, qw, pk, sv (for site/)
    """
    endpoint: str = "dv"
    sites: str = ""
    state_cd: str = ""
    county_cd: str = ""
    huc: str = ""
    bbox: str = ""
    site_type: str = ""
    site_status: str = ""
    parameter_cd: str = ""
    start_dt: str = ""
    end_dt: str = ""
    period: str = ""
    stat_cd: str = ""
    stat_report: str = ""
    stat_type: str = ""
    response_fmt: str = "json"
    site_output: str = ""
    has_data_type: str = ""


class NWISClient:
    """Client for USGS NWIS Water Services API."""

    def __init__(self, base_url: str = NWIS_BASE, timeout: int = 60) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def _build_url(self, p: NWISParams) -> str:
        """Construct the full request URL from parameters."""
        params: dict[str, str] = {"format": p.response_fmt}

        if p.sites:
            params["sites"] = p.sites
        if p.state_cd:
            params["stateCd"] = p.state_cd
        if p.county_cd:
            params["countyCd"] = p.county_cd
        if p.huc:
            params["huc"] = p.huc
        if p.bbox:
            params["bBox"] = p.bbox
        if p.site_type:
            params["siteType"] = p.site_type
        if p.site_status:
            params["siteStatus"] = p.site_status
        if p.parameter_cd:
            params["parameterCd"] = p.parameter_cd
        if p.start_dt:
            params["startDT"] = p.start_dt
        if p.end_dt:
            params["endDT"] = p.end_dt
        if p.period:
            params["period"] = p.period
        if p.stat_cd:
            params["statCd"] = p.stat_cd
        if p.stat_report:
            params["statReportType"] = p.stat_report
        if p.stat_type:
            params["statTypeCd"] = p.stat_type
        if p.site_output:
            params["siteOutput"] = p.site_output
        if p.has_data_type:
            params["hasDataTypeCd"] = p.has_data_type

        query = urllib.parse.urlencode(params)
        return f"{self.base_url}/{p.endpoint}/?{query}"

    def fetch_json(self, p: NWISParams) -> dict[str, Any]:
        """Fetch NWIS data as parsed JSON. Use for iv/ and dv/ endpoints."""
        p.response_fmt = "json"
        url = self._build_url(p)
        return _get_json(url, self.timeout)

    def fetch_rdb(self, p: NWISParams) -> list[dict[str, str]]:
        """Fetch NWIS data as parsed RDB rows. Use for site/, stat/, gwlevels/."""
        p.response_fmt = "rdb"
        url = self._build_url(p)
        text = _get(url, self.timeout)
        return parse_rdb(text)

    def extract_timeseries(self, data: dict[str, Any]) -> list[dict[str, Any]]:
        """Extract time series records from NWIS JSON response.

        Returns a flat list of dicts with keys:
            site_no, site_name, latitude, longitude,
            parameter_cd, parameter_name, unit,
            datetime, value, qualifiers
        """
        records: list[dict[str, Any]] = []
        ts_list = data.get("value", {}).get("timeSeries", [])

        for ts in ts_list:
            src = ts.get("sourceInfo", {})
            site_no = src.get("siteCode", [{}])[0].get("value", "")
            site_name = src.get("siteName", "")
            geo = src.get("geoLocation", {}).get("geogLocation", {})
            lat = geo.get("latitude", "")
            lon = geo.get("longitude", "")

            var = ts.get("variable", {})
            param_cd = var.get("variableCode", [{}])[0].get("value", "")
            param_name = var.get("variableName", "")
            unit = var.get("unit", {}).get("unitCode", "")
            no_data = var.get("noDataValue", -999999.0)

            for val_set in ts.get("values", []):
                for v in val_set.get("value", []):
                    raw = v.get("value", "")
                    try:
                        num = float(raw)
                        if num == no_data:
                            continue
                    except (ValueError, TypeError):
                        continue

                    records.append({
                        "site_no": site_no,
                        "site_name": site_name,
                        "latitude": lat,
                        "longitude": lon,
                        "parameter_cd": param_cd,
                        "parameter_name": param_name,
                        "unit": unit,
                        "datetime": v.get("dateTime", ""),
                        "value": raw,
                        "qualifiers": ",".join(v.get("qualifiers", [])),
                    })

        return records


# ---------------------------------------------------------------------------
# Water Quality Portal client
# ---------------------------------------------------------------------------

@dataclass
class WQPParams:
    """Parameters for a Water Quality Portal search.

    Attributes:
        endpoint:           Result/search or Station/search
        statecode:          State FIPS with US: prefix (e.g., US:54)
        countycode:         County FIPS as US:SS:CCC (e.g., US:54:061)
        siteid:             Monitoring location ID (e.g., USGS-03058500)
        huc:                HUC-8 code
        characteristic:     Analyte name (case-sensitive, e.g., Lithium)
        char_type:          Analyte group
        site_type:          WQP site type (Well, Stream, Spring, etc.)
        start_date_lo:      Earliest sample MM-DD-YYYY
        start_date_hi:      Latest sample MM-DD-YYYY
        providers:          NWIS, STORET, STEWARDS
        data_profile:       narrowResult, basicPhysChem, fullPhysChem
        mime_type:          csv, tsv, xlsx
        zip_response:       yes or no
    """
    endpoint: str = "Result/search"
    statecode: str = ""
    countycode: str = ""
    siteid: str = ""
    huc: str = ""
    characteristic: str = ""
    char_type: str = ""
    site_type: str = ""
    start_date_lo: str = ""
    start_date_hi: str = ""
    providers: str = ""
    data_profile: str = "narrowResult"
    mime_type: str = "csv"
    zip_response: str = "no"


class WQPClient:
    """Client for the Water Quality Portal (waterqualitydata.us)."""

    def __init__(self, base_url: str = WQP_BASE, timeout: int = 120) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def _build_url(self, p: WQPParams) -> str:
        params: dict[str, str] = {
            "mimeType": p.mime_type,
            "zip": p.zip_response,
        }
        if p.data_profile:
            params["dataProfile"] = p.data_profile
        if p.statecode:
            params["statecode"] = p.statecode
        if p.countycode:
            params["countycode"] = p.countycode
        if p.siteid:
            params["siteid"] = p.siteid
        if p.huc:
            params["huc"] = p.huc
        if p.characteristic:
            params["characteristicName"] = p.characteristic
        if p.char_type:
            params["characteristicType"] = p.char_type
        if p.site_type:
            params["siteType"] = p.site_type
        if p.start_date_lo:
            params["startDateLo"] = p.start_date_lo
        if p.start_date_hi:
            params["startDateHi"] = p.start_date_hi
        if p.providers:
            params["providers"] = p.providers

        query = urllib.parse.urlencode(params)
        return f"{self.base_url}/{p.endpoint}?{query}"

    def fetch_csv(self, p: WQPParams) -> list[dict[str, str]]:
        """Fetch WQP data and parse CSV into list of dicts."""
        p.mime_type = "csv"
        p.zip_response = "no"
        url = self._build_url(p)
        text = _get(url, self.timeout)

        # Handle UTF-8 BOM if present
        if text.startswith("\ufeff"):
            text = text[1:]

        reader = csv.DictReader(io.StringIO(text))
        return list(reader)

    def fetch_results(self, p: WQPParams) -> list[dict[str, str]]:
        """Fetch analyte results. Convenience wrapper setting endpoint."""
        p.endpoint = "Result/search"
        return self.fetch_csv(p)

    def fetch_stations(self, p: WQPParams) -> list[dict[str, str]]:
        """Fetch station metadata. Convenience wrapper setting endpoint."""
        p.endpoint = "Station/search"
        p.data_profile = ""  # Station search does not use dataProfile
        return self.fetch_csv(p)


# ---------------------------------------------------------------------------
# Display helpers
# ---------------------------------------------------------------------------

def print_table(
    rows: list[dict[str, Any]],
    cols: list[str],
    max_rows: int = 20,
    col_width: int = 18,
) -> None:
    """Print a fixed-width table from a list of dicts."""
    if not rows:
        print("(no data)")
        return

    widths = {}
    for c in cols:
        w = len(c)
        for row in rows[:max_rows]:
            w = max(w, len(str(row.get(c, ""))))
        widths[c] = min(w, col_width)

    header = "  ".join(c.ljust(widths[c])[:widths[c]] for c in cols)
    print(header)
    print("-" * len(header))
    for row in rows[:max_rows]:
        print("  ".join(
            str(row.get(c, "")).ljust(widths[c])[:widths[c]] for c in cols
        ))
    if len(rows) > max_rows:
        print(f"... ({len(rows) - max_rows} more rows)")


# ---------------------------------------------------------------------------
# Example usage
# ---------------------------------------------------------------------------

def example_daily_discharge() -> None:
    """Fetch daily mean discharge for West Fork River, WV."""
    print("=" * 70)
    print("Example 1: Daily Mean Discharge -- USGS 03058500")
    print("           West Fork River at Butcherville, WV")
    print("           January 2024")
    print("=" * 70)

    client = NWISClient()
    data = client.fetch_json(NWISParams(
        endpoint="dv",
        sites="03058500",
        parameter_cd="00060",
        start_dt="2024-01-01",
        end_dt="2024-01-31",
    ))

    records = client.extract_timeseries(data)
    print(f"\nRecords returned: {len(records)}\n")
    print_table(
        records,
        ["datetime", "value", "unit", "qualifiers"],
        max_rows=10,
    )
    print()


def example_site_info() -> None:
    """Fetch active groundwater sites in Monongalia County, WV."""
    print("=" * 70)
    print("Example 2: Active Groundwater Sites")
    print("           Monongalia County, WV (FIPS 54061)")
    print("=" * 70)

    # NOTE: countyCd uses the full 5-digit state+county FIPS code and is a
    # standalone location filter (do NOT combine with stateCd).
    client = NWISClient()
    rows = client.fetch_rdb(NWISParams(
        endpoint="site",
        county_cd="54061",
        site_type="GW",
        site_status="active",
    ))

    print(f"\nSites returned: {len(rows)}\n")
    print_table(
        rows,
        ["site_no", "station_nm", "dec_lat_va", "dec_long_va", "alt_va"],
        max_rows=10,
    )
    print()


def example_wqp_lithium() -> None:
    """Query Water Quality Portal for lithium in WV groundwater."""
    print("=" * 70)
    print("Example 3: Lithium in WV Waters (Water Quality Portal)")
    print("=" * 70)

    client = WQPClient()
    rows = client.fetch_results(WQPParams(
        statecode="US:54",
        characteristic="Lithium",
        providers="NWIS",
    ))

    print(f"\nResults returned: {len(rows)}\n")

    # Show a subset of columns
    display_cols = [
        "MonitoringLocationIdentifier",
        "ActivityStartDate",
        "ResultMeasureValue",
        "ResultMeasure/MeasureUnitCode",
        "ResultSampleFractionText",
    ]
    print_table(rows, display_cols, max_rows=15, col_width=26)

    # Summary statistics
    values: list[float] = []
    for row in rows:
        try:
            v = float(row.get("ResultMeasureValue", ""))
            values.append(v)
        except (ValueError, TypeError):
            pass

    if values:
        unit = rows[0].get("ResultMeasure/MeasureUnitCode", "?")
        print(f"\nDetected values: {len(values)}")
        print(f"  Min:    {min(values):.1f} {unit}")
        print(f"  Max:    {max(values):.1f} {unit}")
        print(f"  Median: {sorted(values)[len(values) // 2]:.1f} {unit}")
    print()


def example_wqp_stations() -> None:
    """Find stations with lithium data in WV."""
    print("=" * 70)
    print("Example 4: Stations with Lithium Data in WV")
    print("=" * 70)

    client = WQPClient()
    rows = client.fetch_stations(WQPParams(
        statecode="US:54",
        characteristic="Lithium",
        providers="NWIS",
    ))

    print(f"\nStations returned: {len(rows)}\n")
    print_table(
        rows,
        [
            "MonitoringLocationIdentifier",
            "MonitoringLocationName",
            "MonitoringLocationTypeName",
            "LatitudeMeasure",
            "LongitudeMeasure",
        ],
        max_rows=15,
        col_width=30,
    )
    print()


def main() -> None:
    """Run all examples."""
    example_daily_discharge()
    example_site_info()
    example_wqp_lithium()
    example_wqp_stations()


if __name__ == "__main__":
    main()
