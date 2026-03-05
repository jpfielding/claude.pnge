---
name: comtrade-minerals
description: >
  Query and analyze international trade data for critical minerals, petroleum,
  and energy commodities from the UN Comtrade database. Use this skill whenever
  the user asks about lithium trade flows, magnesium imports or exports, barite
  trade, petroleum trade between countries, critical mineral supply chains,
  global commodity trade volumes, import/export statistics by country, HS code
  lookups, or any question about which countries trade minerals and energy
  products. Trigger phrases: "lithium imports by country", "who exports
  magnesium to the US", "petroleum trade flows", "critical mineral supply
  chain", "trade data for barite", "UN Comtrade", "HS code trade data",
  "commodity imports from China", "nickel trade statistics", "uranium trade".
  Produces trade flow tables with value and quantity breakdowns by partner
  country, plus narrative analysis of supply chain concentration.
---

# UN Comtrade Minerals Trade Data Skill

Fetches and analyzes international commodity trade data from the UN Comtrade
API. Covers 200+ reporter countries, HS commodity codes at 2/4/6-digit
granularity, annual and monthly frequencies.

## API Key Handling

The Comtrade API has two tiers:

- **Public preview** (no key): 500 requests/day, 1 period per query, limited
  result counts, no partner/commodity descriptions in response
- **Authenticated** (subscription key): Higher rate limits, multi-period
  queries, full metadata in responses

Resolution order (stop at first success):

1. **`~/.config/comtrade/credentials`** (default) -- parse
   `subscription_key=<value>` from this file
2. **`COMTRADE_API_KEY` env var** -- fallback if credentials file is absent
3. **Fall back to public preview endpoint** -- works without any key, with
   limitations noted above
4. **Prompt the user** -- "For higher rate limits and multi-period queries,
   register for a free Comtrade subscription key at
   https://comtradeplus.un.org/ and store it in
   `~/.config/comtrade/credentials` as `subscription_key=YOUR_KEY`
   (chmod 600)."

Never hardcode or log the key. Pass it via the `subscription-key` query
parameter (authenticated endpoint) or omit it (public preview).

**Reading the credentials file (bash):**
```bash
KEY=$(grep '^subscription_key=' ~/.config/comtrade/credentials 2>/dev/null | cut -d= -f2)
[ -z "$KEY" ] && KEY="${COMTRADE_API_KEY}"
```

**Reading the credentials file (Go):**
```go
func resolveSubscriptionKey() (string, error) {
    home, _ := os.UserHomeDir()
    creds := filepath.Join(home, ".config", "comtrade", "credentials")
    if data, err := os.ReadFile(creds); err == nil {
        for _, line := range strings.Split(string(data), "\n") {
            line = strings.TrimSpace(line)
            if strings.HasPrefix(line, "subscription_key=") {
                return strings.TrimPrefix(line, "subscription_key="), nil
            }
        }
    }
    if key := os.Getenv("COMTRADE_API_KEY"); key != "" {
        return key, nil
    }
    return "", fmt.Errorf("no Comtrade subscription key found")
}
```

---

## API Structure

**Two endpoints depending on authentication state:**

| Endpoint | Auth | Limits |
|----------|------|--------|
| `https://comtradeapi.un.org/public/v1/preview/C/{freq}/HS` | None | 500 req/day, 1 period, no descriptions |
| `https://comtradeapi.un.org/data/v1/get/C/{freq}/HS` | `subscription-key` param | Higher limits, multi-period, full metadata |

The legacy endpoint `https://comtrade.un.org/api/get` redirects and is no
longer functional. Always use the v1 API.

**URL path structure:**
```
/C/{freq}/HS
 |   |     |
 |   |     +-- classification (HS = Harmonized System)
 |   +-------- frequency: A = annual, M = monthly
 +------------ type: C = commodities, S = services
```

**Key query parameters:**

| Parameter | Example | Notes |
|-----------|---------|-------|
| `reporterCode` | `842` | ISO numeric country code of reporting country |
| `partnerCode` | `156` | Trade partner (0 = World aggregate) |
| `cmdCode` | `2825` | HS commodity code (2/4/6 digit) |
| `flowCode` | `M` | M = imports, X = exports, RX = re-exports, RM = re-imports |
| `period` | `2023` | Year (annual) or YYYYMM (monthly); comma-separated for multi (auth only) |
| `subscription-key` | `YOUR_KEY` | Required for authenticated endpoint only |

---

## Key HS Commodity Codes for PNGE Research

See `references/api_reference.md` for full tables. Priority codes:

### Lithium
| HS Code | Description |
|---------|-------------|
| 2825 | Hydrazine, hydroxylamine; lithium oxide and hydroxide |
| 283691 | Lithium carbonate |

### Magnesium
| HS Code | Description |
|---------|-------------|
| 2519 | Natural magnesium carbonate (magnesite) |
| 8104 | Magnesium and articles thereof |

### Petroleum and Gas
| HS Code | Description |
|---------|-------------|
| 2709 | Crude petroleum oils |
| 2710 | Petroleum oils, not crude (refined products) |
| 2711 | Petroleum gases (LNG, LPG, natural gas) |

### Other Critical Minerals
| HS Code | Description |
|---------|-------------|
| 2511 | Natural barium sulfate (barite) -- used in drilling muds |
| 2606 | Aluminium ores and concentrates |
| 2844 | Radioactive chemical elements (uranium) |
| 7501-7508 | Nickel and nickel articles |
| 2529 | Feldspar, fluorspar |

---

## Key Country Codes (ISO 3166-1 Numeric)

| Code | Country | Relevance |
|------|---------|-----------|
| 0 | World (aggregate) | Total trade |
| 842 | United States | Reporter for US trade analysis |
| 156 | China | Major Li/Mg producer and exporter |
| 152 | Chile | Top lithium producer (brines) |
| 36 | Australia | Top lithium producer (spodumene) |
| 32 | Argentina | Lithium brine triangle |
| 76 | Brazil | Lithium, Mg, barite |
| 124 | Canada | Nickel, petroleum, critical minerals |
| 643 | Russia | Nickel, petroleum, uranium |
| 710 | South Africa | Manganese, chromium |
| 392 | Japan | Major Li consumer (batteries) |
| 410 | Republic of Korea | Major Li consumer (batteries) |
| 276 | Germany | Industrial chemicals |
| 826 | United Kingdom | Trade hub |
| 68 | Bolivia | Lithium brine resources |

---

## Workflow

### Step 1 -- Resolve Intent

Map the user's question to parameters:
- **Commodity**: Map natural language to HS code(s). Check
  `references/api_reference.md` for code lookups.
- **Reporter**: Default to USA (842) unless user specifies another country.
- **Partner**: Default to World (0) for aggregate, or specific country code.
- **Flow**: Default to imports (M) unless user asks about exports (X).
- **Period**: Default to most recent available year. Annual data typically
  lags 1-2 years (e.g., in 2026, most recent complete year may be 2024).
- **Frequency**: Default to annual (A) unless user asks for monthly.

### Step 2 -- Resolve Credentials and Select Endpoint

```bash
KEY=$(grep '^subscription_key=' ~/.config/comtrade/credentials 2>/dev/null | cut -d= -f2)
[ -z "$KEY" ] && KEY="${COMTRADE_API_KEY}"

if [ -n "$KEY" ]; then
    BASE="https://comtradeapi.un.org/data/v1/get/C/A/HS"
    AUTH="&subscription-key=$KEY"
else
    BASE="https://comtradeapi.un.org/public/v1/preview/C/A/HS"
    AUTH=""
fi
```

### Step 3 -- Fetch Data

Build the URL with appropriate filters:

```bash
# Example: US imports of lithium carbonate from all partners, 2023
curl -s "${BASE}?reporterCode=842&period=2023&cmdCode=283691&flowCode=M${AUTH}"
```

**For public preview endpoint**, one period at a time. Loop over years if
the user needs a time series:

```bash
for YEAR in 2021 2022 2023; do
    curl -s "${BASE}?reporterCode=842&period=${YEAR}&cmdCode=283691&flowCode=M"
    sleep 1  # be respectful of rate limits
done
```

### Step 4 -- Parse Response

Response structure (JSON):
```json
{
  "elapsedTime": "0.14 secs",
  "count": 14,
  "data": [
    {
      "typeCode": "C",
      "freqCode": "A",
      "refYear": 2023,
      "period": "2023",
      "reporterCode": 842,
      "flowCode": "M",
      "partnerCode": 156,
      "cmdCode": "283691",
      "qtyUnitCode": 8,
      "qty": 5267952.0,
      "netWgt": 5267952.0,
      "cifvalue": 250584381.0,
      "fobvalue": 242860584.0,
      "primaryValue": 250584381.0,
      "isQtyEstimated": false,
      "isReported": false,
      "isAggregate": true
    }
  ],
  "error": ""
}
```

**Key response fields:**

| Field | Meaning |
|-------|---------|
| `partnerCode` | Trade partner (0 = World total) |
| `qty` | Quantity in units specified by `qtyUnitCode` |
| `netWgt` | Net weight in kilograms |
| `cifvalue` | CIF value in USD (cost + insurance + freight) -- import side |
| `fobvalue` | FOB value in USD (free on board) -- export side |
| `primaryValue` | CIF for imports, FOB for exports (the "natural" valuation) |
| `qtyUnitCode` | 8 = kg, 1 = no quantity, others vary |
| `isQtyEstimated` | Whether quantity was estimated (data quality flag) |
| `isReported` | Whether this was directly reported vs mirror/estimated |

**Important:** The public preview endpoint returns `null` for
`reporterISO`, `reporterDesc`, `partnerDesc`, `flowDesc`, `cmdDesc`,
`qtyUnitAbbr`. You must map codes to names locally. See the country and HS
code tables in `references/api_reference.md`.

### Step 5 -- Produce Output

**Format: Raw Data Table + Narrative**

Present a markdown table of trade flows sorted by value (descending), then
a narrative summary covering:

1. **Total trade** -- aggregate value and quantity for the period
2. **Top partners** -- top 5 countries by value with share percentages
3. **Supply concentration** -- HHI or top-3 share as proxy for supply risk
4. **Quantity vs value** -- implied unit price (value / netWgt) to flag
   pricing trends
5. **Units and caveats** -- always state USD and kg; note estimated values;
   note that HS 2825 includes non-lithium products (hydrazine, hydroxylamine)

**Example output structure:**
```
## US Imports of Lithium Carbonate (HS 283691), 2023

| Partner       | Value (USD)    | Net Weight (kg) | $/kg  | Share |
|---------------|----------------|-----------------|-------|-------|
| World Total   | 250,584,381    | 16,189,607      | 15.48 | 100%  |
| Chile         | 216,996,017    | 5,267,952       | 41.19 | 86.6% |
| China         |  12,443,422    | 381,004         | 32.66 |  5.0% |
| Argentina     |  11,643,717    | 1,180,000       |  9.87 |  4.6% |
| ...           | ...            | ...             | ...   | ...   |

**Summary:** The US imported $250.6M of lithium carbonate in 2023 (16,190
metric tons net weight). Chile dominates supply at 86.6% of import value,
reflecting the country's Atacama brine operations. The top-3 concentration
(Chile + China + Argentina) accounts for 96.2% of value, indicating high
supply chain concentration risk. Implied $/kg varies significantly by
origin, suggesting different product grades or contract pricing structures.
Data is from customs declarations aggregated by the UN Statistics Division;
some partner breakdowns may be estimated.
```

---

## Pagination

The public preview endpoint caps results (typically 500 rows). For the
authenticated endpoint, check `count` in the response -- if it equals the
maximum, there may be more data. Use the `offset` parameter (authenticated
only) to paginate if needed. In practice, single-country single-commodity
queries rarely exceed 50-100 rows.

## Error Handling

| HTTP Code | Meaning | Action |
|-----------|---------|--------|
| 200 + `error` field non-empty | API-level error | Read error message; common: "Maximum number of periods is 1" on preview endpoint |
| 200 + `count` = 0 | No data | Widen filters (try broader HS code or different year) |
| 200 + `count` = -1 | Query error | Check parameters; usually malformed codes |
| 401 | Missing/invalid subscription key | Fall back to public preview or prompt user for key |
| 403 | Access denied | Rate limit exceeded; wait and retry or use preview endpoint |
| 404 | Endpoint not found | Verify URL path structure |
| 429 | Too many requests | Back off; respect rate limits (500/day preview, more with key) |
| 5xx | Server error | Retry after delay; Comtrade has occasional downtime |

---

## Data Quality and Caveats

- **Reporting lag**: Annual data for year Y typically available by mid-Y+1.
  Monthly data lags 2-4 months.
- **Mirror statistics**: If a reporter country has not submitted data, the UN
  may "mirror" the trade by using partner-reported data (imports from A
  approximated from B's exports to A). The `isReported` flag indicates this.
- **HS code breadth**: HS 2825 includes hydrazine and hydroxylamine in
  addition to lithium compounds. For lithium-specific analysis, prefer
  283691 (lithium carbonate) and 282520 (lithium oxide/hydroxide) when
  available at 6-digit granularity.
- **Confidential data**: Some countries suppress trade in strategic minerals.
  Gaps in partner-level data may reflect confidentiality rather than zero trade.
- **Valuation**: Import values are CIF (cost + insurance + freight), export
  values are FOB (free on board). Comparing import and export values for the
  same flow will show a CIF-FOB gap.
- **Re-exports**: Entrepot trade (e.g., through Belgium, Netherlands, Singapore)
  can inflate bilateral flows. Check for unusually large values from known
  transshipment hubs.
- **Quantity units**: Most mineral/chemical commodities report in kg
  (`qtyUnitCode` = 8). Some codes use supplementary units. Always check units.

---

## Implementation Notes

- **Prefer `bash_tool` with `curl` + `jq`** for API calls
- **Python stdlib client** -- see `references/python_example.py`
  (`ComtradeClient`, `fetch_trade_data`, `format_trade_table`)
- **Public preview is sufficient for most single-period queries** --
  only push users toward registration when they need multi-period or
  high-volume access
- **Map partner codes to country names** using the lookup table in
  `references/api_reference.md`; the preview endpoint does not return
  country names
- **Rate limiting**: Add 1-second delay between requests when looping
  over multiple years or commodities
- Comtrade data updates vary by country; major reporters (US, EU, China,
  Japan) typically update within 6 months of period end
