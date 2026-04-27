#!/usr/bin/env python3
"""comtrade_client.py -- Minimal UN Comtrade API v1 client using only stdlib.

Usage:
    python comtrade_client.py

Credential resolution order:
    1. ~/.config/comtrade/credentials  (subscription_key=YOUR_KEY)
    2. COMTRADE_API_KEY env var
    3. Falls back to public preview endpoint (no key needed, limited)
"""

from __future__ import annotations

import json
import os
import time
import urllib.request
import urllib.parse
import urllib.error
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


# ---------------------------------------------------------------------------
# Country code lookup (subset -- PNGE-relevant countries)
# ---------------------------------------------------------------------------

COUNTRY_NAMES: dict[int, str] = {
    0: "World",
    32: "Argentina",
    36: "Australia",
    40: "Austria",
    56: "Belgium",
    68: "Bolivia",
    76: "Brazil",
    124: "Canada",
    152: "Chile",
    156: "China",
    170: "Colombia",
    180: "DR Congo",
    203: "Czechia",
    233: "Estonia",
    246: "Finland",
    251: "France",
    276: "Germany",
    344: "Hong Kong",
    368: "Iraq",
    372: "Ireland",
    376: "Israel",
    380: "Italy",
    392: "Japan",
    410: "Republic of Korea",
    414: "Kuwait",
    428: "Latvia",
    458: "Malaysia",
    484: "Mexico",
    490: "Chinese Taipei",
    528: "Netherlands",
    566: "Nigeria",
    579: "Norway",
    604: "Peru",
    608: "Philippines",
    643: "Russia",
    682: "Saudi Arabia",
    699: "India",
    702: "Singapore",
    710: "South Africa",
    724: "Spain",
    757: "Switzerland",
    764: "Thailand",
    780: "Trinidad and Tobago",
    784: "UAE",
    792: "Turkey",
    826: "United Kingdom",
    842: "United States",
    862: "Venezuela",
    704: "Vietnam",
}


# ---------------------------------------------------------------------------
# Credential resolution
# ---------------------------------------------------------------------------

def resolve_subscription_key() -> Optional[str]:
    """Resolve Comtrade subscription key from credentials file or env var.

    Returns None if no key is found (falls back to public preview).
    """
    creds_path = Path.home() / ".config" / "comtrade" / "credentials"
    if creds_path.exists():
        for line in creds_path.read_text().splitlines():
            line = line.strip()
            if line.startswith("subscription_key="):
                return line.removeprefix("subscription_key=")

    key = os.environ.get("COMTRADE_API_KEY", "")
    if key:
        return key

    return None


# ---------------------------------------------------------------------------
# Query params
# ---------------------------------------------------------------------------

@dataclass
class TradeQuery:
    """Parameters for a Comtrade trade data request.

    Attributes:
        reporter_code:  ISO numeric code of reporting country (842 = US).
        period:         Year as string ("2023") or YYYYMM for monthly.
        cmd_code:       HS commodity code (2/4/6 digit), e.g. "283691".
        flow_code:      "M" (imports), "X" (exports), "RM", "RX".
        partner_code:   Partner country code. None = all partners.
                        0 = World aggregate.
        freq:           "A" (annual) or "M" (monthly).
    """
    reporter_code: int = 842
    period: str = "2023"
    cmd_code: str = "283691"
    flow_code: str = "M"
    partner_code: Optional[int] = None
    freq: str = "A"


# ---------------------------------------------------------------------------
# Client
# ---------------------------------------------------------------------------

PREVIEW_BASE = "https://comtradeapi.un.org/public/v1/preview"
AUTH_BASE = "https://comtradeapi.un.org/data/v1/get"


class ComtradeClient:
    """Thin wrapper around the UN Comtrade API v1 using only stdlib."""

    def __init__(self, subscription_key: Optional[str] = None) -> None:
        if subscription_key is None:
            subscription_key = resolve_subscription_key()
        self.subscription_key = subscription_key
        self.use_preview = subscription_key is None

    @property
    def base_url(self) -> str:
        return PREVIEW_BASE if self.use_preview else AUTH_BASE

    def _build_url(self, q: TradeQuery) -> str:
        """Build the full request URL from query parameters."""
        path = f"{self.base_url}/C/{q.freq}/HS"
        params: dict[str, str] = {
            "reporterCode": str(q.reporter_code),
            "period": q.period,
            "cmdCode": q.cmd_code,
            "flowCode": q.flow_code,
        }
        if q.partner_code is not None:
            params["partnerCode"] = str(q.partner_code)
        if self.subscription_key:
            params["subscription-key"] = self.subscription_key
        return f"{path}?{urllib.parse.urlencode(params)}"

    def fetch(self, q: TradeQuery) -> dict:
        """Fetch trade data for a single query.

        Returns the full JSON response as a dict with keys:
            elapsedTime, count, data, error
        """
        url = self._build_url(q)
        req = urllib.request.Request(url)
        req.add_header("Accept", "application/json")
        req.add_header("User-Agent", "comtrade-pnge-skill/1.0")

        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                body = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8", errors="replace")
            raise RuntimeError(
                f"Comtrade API returned HTTP {e.code}: {error_body}"
            ) from e
        except urllib.error.URLError as e:
            raise RuntimeError(f"Network error: {e.reason}") from e

        if body.get("error"):
            raise RuntimeError(f"Comtrade API error: {body['error']}")

        return body

    def fetch_trade_data(self, q: TradeQuery) -> list[dict]:
        """Fetch and return just the data array."""
        body = self.fetch(q)
        return body.get("data", [])

    def fetch_time_series(
        self,
        q: TradeQuery,
        years: list[str],
        delay: float = 1.0,
    ) -> list[dict]:
        """Fetch data across multiple years (public preview workaround).

        The public preview endpoint only allows 1 period per request.
        This method loops over years with a polite delay.
        """
        all_data: list[dict] = []
        for i, year in enumerate(years):
            q.period = year
            rows = self.fetch_trade_data(q)
            all_data.extend(rows)
            if i < len(years) - 1:
                time.sleep(delay)
        return all_data


# ---------------------------------------------------------------------------
# Output formatting
# ---------------------------------------------------------------------------

def country_name(code: int) -> str:
    """Look up country name from numeric code."""
    return COUNTRY_NAMES.get(code, f"Code {code}")


def format_usd(value: float) -> str:
    """Format a USD value with commas."""
    if value >= 1_000_000_000:
        return f"${value / 1_000_000_000:.2f}B"
    if value >= 1_000_000:
        return f"${value / 1_000_000:.1f}M"
    if value >= 1_000:
        return f"${value / 1_000:.1f}K"
    return f"${value:.0f}"


def format_weight(kg: float) -> str:
    """Format weight in kg to metric tons if large."""
    if kg >= 1_000_000:
        return f"{kg / 1_000:.0f} t"
    if kg >= 1_000:
        return f"{kg / 1_000:.1f} t"
    return f"{kg:.0f} kg"


def format_trade_table(
    rows: list[dict],
    title: str = "Trade Data",
    max_rows: int = 20,
) -> str:
    """Format trade data rows as a markdown table with narrative.

    Sorts by primaryValue descending and computes partner shares.
    """
    if not rows:
        return f"## {title}\n\nNo data returned.\n"

    # Separate world total from partner rows
    world_row = None
    partner_rows = []
    for r in rows:
        if r.get("partnerCode") == 0:
            world_row = r
        else:
            partner_rows.append(r)

    # Sort partners by value descending
    partner_rows.sort(key=lambda r: r.get("primaryValue", 0), reverse=True)

    # Compute world total from aggregate or sum of partners
    if world_row:
        total_value = world_row.get("primaryValue", 0)
        total_weight = world_row.get("netWgt", 0)
    else:
        total_value = sum(r.get("primaryValue", 0) for r in partner_rows)
        total_weight = sum(r.get("netWgt", 0) for r in partner_rows)

    lines = [f"## {title}", ""]

    # Table header
    lines.append(
        "| Partner | Value (USD) | Net Weight (kg) | $/kg | Share |"
    )
    lines.append(
        "|---------|-------------|-----------------|------|-------|"
    )

    # World total row
    if world_row:
        unit_price = (
            total_value / total_weight if total_weight > 0 else 0
        )
        lines.append(
            f"| **World Total** | {format_usd(total_value)} "
            f"| {format_weight(total_weight)} "
            f"| {unit_price:.2f} | 100% |"
        )

    # Partner rows
    display_rows = partner_rows[:max_rows]
    for r in display_rows:
        name = country_name(r.get("partnerCode", -1))
        value = r.get("primaryValue", 0)
        weight = r.get("netWgt", 0)
        unit_price = value / weight if weight > 0 else 0
        share = (value / total_value * 100) if total_value > 0 else 0
        lines.append(
            f"| {name} | {format_usd(value)} "
            f"| {format_weight(weight)} "
            f"| {unit_price:.2f} | {share:.1f}% |"
        )

    if len(partner_rows) > max_rows:
        lines.append(f"| ... ({len(partner_rows) - max_rows} more) | | | | |")

    lines.append("")

    # Narrative summary
    flow_label = "imported" if rows[0].get("flowCode") == "M" else "exported"
    period = rows[0].get("period", "?")
    reporter = country_name(rows[0].get("reporterCode", 0))

    lines.append(
        f"**Summary:** {reporter} {flow_label} {format_usd(total_value)} "
        f"of HS {rows[0].get('cmdCode', '?')} in {period} "
        f"({format_weight(total_weight)} net weight)."
    )

    if len(partner_rows) >= 3:
        top3_value = sum(
            r.get("primaryValue", 0) for r in partner_rows[:3]
        )
        top3_share = (
            top3_value / total_value * 100 if total_value > 0 else 0
        )
        top3_names = ", ".join(
            country_name(r.get("partnerCode", -1))
            for r in partner_rows[:3]
        )
        lines.append(
            f"Top-3 concentration ({top3_names}): {top3_share:.1f}% of value."
        )

    # Data quality notes
    estimated = [r for r in rows if r.get("isQtyEstimated")]
    if estimated:
        lines.append(
            f"Note: {len(estimated)} record(s) have estimated quantities."
        )

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Example usage
# ---------------------------------------------------------------------------

def main() -> None:
    client = ComtradeClient()
    mode = "preview (no key)" if client.use_preview else "authenticated"
    print(f"Using Comtrade API in {mode} mode.\n")

    # Example 1: US imports of lithium carbonate (HS 283691), 2023
    print("=" * 60)
    print("Example 1: US Lithium Carbonate Imports (HS 283691), 2023")
    print("=" * 60)

    rows = client.fetch_trade_data(TradeQuery(
        reporter_code=842,
        period="2023",
        cmd_code="283691",
        flow_code="M",
    ))
    print(f"Records returned: {len(rows)}\n")
    print(format_trade_table(
        rows,
        title="US Imports of Lithium Carbonate (HS 283691), 2023",
    ))

    print()
    time.sleep(1)  # polite delay between requests

    # Example 2: US imports of magnesium metal (HS 8104), 2023
    print("=" * 60)
    print("Example 2: US Magnesium Metal Imports (HS 8104), 2023")
    print("=" * 60)

    rows = client.fetch_trade_data(TradeQuery(
        reporter_code=842,
        period="2023",
        cmd_code="8104",
        flow_code="M",
    ))
    print(f"Records returned: {len(rows)}\n")
    print(format_trade_table(
        rows,
        title="US Imports of Magnesium and Articles (HS 8104), 2023",
    ))

    print()
    time.sleep(1)

    # Example 3: Time series -- US lithium carbonate imports, world total
    print("=" * 60)
    print("Example 3: US Lithium Carbonate Imports Time Series (World Total)")
    print("=" * 60)

    years = ["2019", "2020", "2021", "2022", "2023"]
    all_rows = client.fetch_time_series(
        TradeQuery(
            reporter_code=842,
            cmd_code="283691",
            flow_code="M",
            partner_code=0,  # world total only
        ),
        years=years,
        delay=1.0,
    )

    print(f"\nRecords returned: {len(all_rows)}\n")
    print("| Year | Value (USD) | Net Weight (kg) | $/kg |")
    print("|------|-------------|-----------------|------|")
    # Sort by period ascending for time series
    all_rows.sort(key=lambda r: r.get("period", ""))
    for r in all_rows:
        value = r.get("primaryValue", 0)
        weight = r.get("netWgt", 0)
        unit_price = value / weight if weight > 0 else 0
        print(
            f"| {r.get('period', '?')} "
            f"| {format_usd(value)} "
            f"| {format_weight(weight)} "
            f"| {unit_price:.2f} |"
        )


if __name__ == "__main__":
    main()
