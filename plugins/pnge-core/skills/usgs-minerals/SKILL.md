---
name: usgs-minerals
description: >
  Query, analyze, and summarize USGS Mineral Commodity Summaries data for
  critical minerals including lithium, magnesium, cobalt, and 80+ other
  commodities. Use this skill whenever the user asks about mineral production
  statistics, global reserves, commodity pricing trends, critical mineral
  supply chains, import reliance, or world mine output — even if they do not
  mention USGS or MCS by name. Trigger for phrases like "lithium production
  by country", "magnesium reserves", "critical mineral prices", "U.S. import
  reliance for lithium", "world mine production of cobalt", "mineral commodity
  data", "how much lithium does Australia produce", "battery mineral supply
  chain", or any request for mineral production, trade, or reserve figures.
  Covers MCS 2025/2026 data releases and the World Minerals Outlook to 2029.
  Produces country-level tables with narrative trend analysis.
---

# USGS Mineral Commodity Data Skill

Fetches and analyzes mineral commodity data from USGS ScienceBase — including
Mineral Commodity Summaries (MCS) annual data releases and the World Minerals
Outlook to 2029.

## Credential

None required. All USGS ScienceBase data is public.

---

## Data Sources

| Source | Coverage | Format | Update Cycle |
|--------|----------|--------|--------------|
| MCS 2026 Commodities Data | 80+ minerals, U.S. salient stats + world production + reserves | Single aggregated CSV (3.2 MB) | Annual (January-February) |
| MCS 2025 Per-Commodity Releases | Individual commodity salient CSVs | Small CSV per commodity | Annual |
| World Minerals Outlook 2029 | Li, Mg, Co, Ga, He, Pd, Pt, Ti — world production by country 2018-2029 | CSV (192 KB) | Periodic (latest March 2025) |
| MCS PDF Chapters | Full narrative + tables per commodity | PDF | Annual |

**Preferred data path:** Use MCS 2026 aggregated CSV first (most complete
and current). Fall back to MCS 2025 per-commodity CSVs for detail. Use the
World Minerals Outlook for production projections through 2029.

---

## API Structure

### ScienceBase REST API

**Base URL:** `https://www.sciencebase.gov/catalog/`

ScienceBase is not a traditional query API — it hosts downloadable data files
organized as catalog items. The workflow is: search for items, get file URLs
from item metadata, then download and parse CSV files locally.

**Search items:**
```bash
curl -s "https://www.sciencebase.gov/catalog/items?\
q=mineral+commodity+summaries+2025+lithium\
&format=json&max=5&fields=title,id,files"
```

**Get item details (with file download URLs):**
```bash
curl -s "https://www.sciencebase.gov/catalog/item/6797ff62d34ea8c18376e1cb?\
format=json&fields=title,files"
```

**Download a CSV file:**
```bash
curl -sL "{downloadUri}" -o output.csv
```

### Key ScienceBase Item IDs

| Item | ScienceBase ID | Key File |
|------|----------------|----------|
| MCS 2026 Aggregated | `696a75d5d4be0228872d3bf8` | `MCS2026_Commodities_Data.csv` |
| MCS 2025 Salient (all) | `6793e234d34e72688d6b71e7` | `Salient_Commodity_Data_Release_Grouped.zip` |
| MCS 2025 Lithium | `6797ff62d34ea8c18376e1cb` | `mcs2025-lithium_salient.csv` |
| MCS 2025 Mg Compounds | `6797ffe2d34ea8c18376e1da` | `mcs2025-mgcomp_salient.csv` |
| MCS 2025 Mg Metal | `6797ffffd34ea8c18376e1e5` | `mcs2025-mgmet_salient.csv` |
| World Minerals Outlook 2029 | `67b8b168d34e1a2e835b7e6c` | `Outlook 2025 Data Release 031125.csv` |

### MCS PDF Direct URLs

```
https://pubs.usgs.gov/periodicals/mcs2026/mcs2026-{commodity}.pdf
https://pubs.usgs.gov/periodicals/mcs2025/mcs2025-{commodity}.pdf
```
Commodity slugs: `lithium`, `magnesium-compounds`, `magnesium-metal`, `cobalt`, etc.

---

## CSV Schemas

### MCS 2026 Aggregated CSV (`MCS2026_Commodities_Data.csv`)

| Column | Description | Example |
|--------|-------------|---------|
| `MCS chapter` | Commodity chapter heading (uppercase) | `LITHIUM` |
| `Section` | Data section within chapter | `World Mine Production and Reserves` |
| `Commodity` | Commodity name (title case) | `Lithium` |
| `Country` | Country or region name | `Australia` |
| `Statistics` | Statistic category | `Production`, `Reserves`, `Import`, `Price` |
| `Statistics_detail` | Specific measure | `Mine production`, `Reserves: rounded` |
| `Unit` | Unit of measurement | `metric tons`, `dollars per metric ton` |
| `Year` | Data year | `2025` |
| `Value` | Numeric value (may contain commas, W for withheld) | `92,000` |
| `Notes` | Qualifiers | `Estimated.` |
| `Is critical mineral 2025` | Critical mineral designation | `Yes` / `No` |

### MCS 2025 Lithium Salient CSV

| Column | Description |
|--------|-------------|
| `DataSource` | Always `MCS2025` |
| `Commodity` | `Lithium` |
| `Year` | 2020-2024 |
| `USprod_t` | U.S. production (metric tons Li content); W = withheld |
| `Imports_t` | Imports for consumption (metric tons) |
| `Exports_t` | Exports (metric tons) |
| `Consump_t` | Apparent consumption (metric tons); W = withheld |
| `Price_dt` | Price, battery-grade Li2CO3 ($/metric ton) |
| `Employment_num` | Mine/mill employment |
| `NIR_pct` | Net import reliance as % of consumption |

### MCS 2025 Magnesium Metal Salient CSV

| Column | Description |
|--------|-------------|
| `USprod_Primary_kt` | U.S. primary production (thousand metric tons) |
| `USprod_Secondary_kt` | U.S. secondary (recycled) production (kt) |
| `Imports_kt` | Imports (kt) |
| `Exports_kt` | Exports (kt) |
| `Consump_Reported_kt` | Reported consumption (kt) |
| `Price_European_dlb` | European free market price ($/lb) |
| `Price_dt` | Price ($/metric ton) |
| `Stocks_kt` | Industry stocks (kt) |
| `NIR_pct` | Net import reliance (%) |

### World Minerals Outlook CSV

| Column | Description |
|--------|-------------|
| `Mineral_Commodity` | Commodity name |
| `Year` | 2018-2029 |
| `Note` | `reported`, `estimated`, `projected` |
| `Quantity` | Numeric production value |
| `Data_type` | `Production` or `Capacity` |
| `Unit_MEAS` | `Metric tons` |
| `Form` | Material form (e.g., `Brine and mine, lithium content`) |
| `Geographic_Region` | Country name |

---

## Key Commodities for PNGE Research

### Lithium

| Data Point | Source | Latest Value |
|------------|--------|--------------|
| World mine production | MCS 2026 | 290,000 t (2025 est.) |
| Top producer | MCS 2026 | Australia — 92,000 t |
| U.S. reserves | MCS 2026 | 4,400,000 t |
| World reserves | MCS 2026 | 37,000,000 t |
| Battery-grade Li2CO3 price | MCS 2025 | $14,000/t (2024) |
| Net import reliance | MCS 2025 | >50% |
| End uses | MCS PDF | Batteries 87%, ceramics/glass 4%, lubricants 3% |
| Critical mineral status | MCS 2026 | Yes |

**Key producing countries (2025 est.):**
Australia (92,000 t), China (62,000 t), Chile (56,000 t), Zimbabwe (28,000 t),
Argentina (23,000 t), Brazil (12,000 t), Mali (9,400 t), Canada (5,600 t)

**Price history (Li2CO3 battery-grade, $/t):**
2020: $10,100 | 2021: $14,200 | 2022: $71,100 | 2023: $41,300 | 2024: $14,000

### Magnesium Metal

| Data Point | Source | Latest Value |
|------------|--------|--------------|
| U.S. primary production | MCS 2025 | 0 (no domestic primary since 2023) |
| U.S. secondary production | MCS 2025 | 110 kt (2024) |
| Price (European free market) | MCS 2025 | $3.50/lb (2024) |
| Net import reliance | MCS 2025 | >75% |

### Magnesium Compounds

| Data Point | Source | Latest Value |
|------------|--------|--------------|
| U.S. production | MCS 2025 | 430 kt (2024) |
| U.S. consumption | MCS 2025 | 890 kt (2024) |
| Net import reliance | MCS 2025 | 52% |

---

## Workflow

### Step 1 — Resolve Intent

Map the user's question to a commodity, data type, and source:

| User asks about... | Commodity filter | Section / Statistic | Source |
|--------------------|-----------------|---------------------|--------|
| "lithium production by country" | `Lithium` | World Mine Production / Production | MCS 2026 |
| "lithium reserves" | `Lithium` | World Mine Production and Reserves / Reserves | MCS 2026 |
| "lithium price trend" | `Lithium` | Salient Statistics / Price | MCS 2025 or 2026 |
| "U.S. lithium imports" | `Lithium` | Salient Statistics / Import | MCS 2025 or 2026 |
| "magnesium supply chain" | `Magnesium Metal` + `Magnesium Compounds` | Multiple | MCS 2025 |
| "critical mineral production forecast" | Multiple | Production | World Minerals Outlook |
| "which countries produce lithium" | `Lithium` | World Mine Production | MCS 2026 |

If the commodity name is ambiguous (e.g., "magnesium"), check both Magnesium
Metal and Magnesium Compounds. If the user asks for projections or forecasts,
use the World Minerals Outlook 2029 dataset.

### Step 2 — Download Data

**Option A: MCS 2026 aggregated CSV (preferred for most queries)**
```bash
# 1. Get the download URL for MCS2026_Commodities_Data.csv
ITEM_ID="696a75d5d4be0228872d3bf8"
FILE_URL=$(curl -s "https://www.sciencebase.gov/catalog/item/${ITEM_ID}?format=json&fields=files" \
  | jq -r '.files[] | select(.name == "MCS2026_Commodities_Data.csv") | .downloadUri')

# 2. Download the CSV
curl -sL "$FILE_URL" -o /tmp/mcs2026_commodities.csv

# 3. Filter for lithium world mine production
python3 -c "
import csv, sys
with open('/tmp/mcs2026_commodities.csv', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row['Commodity'].lower() == 'lithium' and 'World Mine' in row.get('Section','') and row['Statistics'] == 'Production':
            print(f\"{row['Country']:20s} {row['Year']}  {row['Value']:>12s}  {row.get('Notes','')}\")
"
```

**Option B: MCS 2025 per-commodity CSV (simpler for U.S. salient stats)**
```bash
# Download lithium salient stats directly
curl -sL "https://www.sciencebase.gov/catalog/file/get/6797ff62d34ea8c18376e1cb?\
f=__disk__09%2Fc7%2Ffd%2F09c7fd03c205aae28b29fbfb0e6867d652b65488" \
  -o /tmp/mcs2025_lithium.csv
```

**Option C: World Minerals Outlook (for projections)**
```bash
curl -sL "https://www.sciencebase.gov/catalog/file/get/67b8b168d34e1a2e835b7e6c?\
f=__disk__f8%2Ff5%2Fa4%2Ff8f5a4708b3451cd0ffcec730f3debdd5f1bf77d" \
  -o /tmp/outlook_2029.csv
```

**Option D: ScienceBase search (when commodity/year is unknown)**
```bash
curl -s "https://www.sciencebase.gov/catalog/items?\
q=mineral+commodity+summaries+2025+cobalt\
&format=json&max=5&fields=title,id,files" \
  | jq '.items[] | {title, id, files: [.files[]? | select(.name | endswith(".csv")) | .name]}'
```

### Step 3 — Parse Response

CSV files use UTF-8 with BOM (`utf-8-sig`). Parse with any CSV library.

**Special values:**
- `W` = Withheld to avoid disclosing company proprietary data
- `--` = Not available or zero rounds to zero
- Values may contain commas inside quoted fields (e.g., `"92,000"`)
- `>25`, `>50`, `>75` for net import reliance percentages

**Filtering the MCS 2026 aggregated CSV:**
```python
import csv
with open("/tmp/mcs2026_commodities.csv", encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)
    rows = [r for r in reader if r["Commodity"].lower() == "lithium"]

# Split by section
salient = [r for r in rows if "Salient" in r["Section"]]
world_prod = [r for r in rows if "World Mine" in r["Section"] and r["Statistics"] == "Production"]
reserves = [r for r in rows if r["Statistics"] == "Reserves"]
imports = [r for r in rows if "Import Sources" in r["Section"]]
```

### Step 4 — Produce Output

**Format: Raw Data Table + Narrative**

Present a markdown table of the most relevant rows (cap at ~20 rows for
readability), then a narrative summary covering:

1. **Current state** — most recent production/price/reserve figures with year
2. **Trend** — direction and magnitude (use % change for prices, absolute for production)
3. **Geographic concentration** — top 3-5 producers and their share of world total
4. **U.S. position** — domestic production, import reliance, and strategic implications
5. **Units and caveats** — always state units; note estimated vs. reported vs. withheld

**Example output structure:**
```
## Lithium — World Mine Production (MCS 2026)

| Country        | 2024 (t) | 2025 est. (t) | Share of World |
|----------------|----------|----------------|----------------|
| Australia      | 82,700   | 92,000         | 31.7%          |
| China          | 41,400   | 62,000         | 21.4%          |
| Chile          | 48,900   | 56,000         | 19.3%          |
| Zimbabwe       | 20,000   | 28,000         | 9.7%           |
| Argentina      | 13,800   | 23,000         | 7.9%           |
| ...            | ...      | ...            | ...            |
| World total    | 222,000  | 290,000        | 100%           |

**Summary:** Global lithium mine production reached an estimated 290,000 metric
tons (Li content) in 2025, up 31% from 222,000 t in 2024. Australia remains the
dominant producer at 92,000 t (32% of world output), followed by China (62,000 t)
and Chile (56,000 t). U.S. production is withheld (W) but the country holds
4.4 million tons of reserves. Battery-grade lithium carbonate prices averaged
$14,000/t in 2024, down 66% from the 2022 peak of $71,100/t. Net U.S. import
reliance exceeds 50%. Data is from MCS 2026; values marked "Estimated" carry
higher uncertainty than "Reported" figures.
```

---

## Error Handling

| Condition | Symptom | Action |
|-----------|---------|--------|
| ScienceBase down | HTTP 503, timeout | Retry after 30s; fall back to cached CSV if available |
| Item not found | HTTP 404 or empty `items` | Verify item ID; search by keyword instead |
| CSV encoding issue | Garbled first column | Use `utf-8-sig` encoding to strip BOM |
| Value = W | Withheld data | Note in output: "W = withheld to protect proprietary data" |
| Value = -- | Not available | Omit from calculations; note as "not available" |
| Commodity not in MCS | Zero search results | Suggest alternative data source or check spelling |
| Large CSV download slow | Timeout on 3+ MB file | Download to temp file; process locally |

---

## Caveats and Data Quality

- **Annual publication cycle:** MCS data is published once per year (January-February). The most recent year is typically estimated, not final. Previous years may be revised.
- **Withheld data (W):** U.S. lithium production has been withheld for years to protect company proprietary data (only one primary producer). This creates gaps in domestic supply analysis.
- **Country-level aggregation:** MCS reports production at the country level. Sub-national data (e.g., by mine, by basin) requires other sources.
- **Estimated vs. reported:** Values marked "Estimated" in the Notes column are USGS estimates, not official government statistics. Reliability varies by country.
- **Price data:** MCS prices are annual averages and may not reflect current spot prices. Lithium prices are particularly volatile — the 2022 peak was 7x the 2020 level.
- **Reserves vs. resources:** MCS reports only reserves (economically extractable at current prices/technology), not total resources. Resource estimates are much larger.
- **World Minerals Outlook projections:** The 2025-2029 production projections are capacity-based estimates, not guaranteed output. Actual production depends on market conditions.
- **Net import reliance:** NIR percentages use apparent consumption (production + imports - exports +/- stock changes). When production is withheld, NIR is approximate.

---

## Implementation Notes

- **Prefer `bash_tool`** to make HTTP requests with `curl` and parse with `jq` or `python3`
- **Python client** — see `references/python_example.py` (`sb_search`, `get_mcs2025_salient`, `search_mcs2026`, `get_outlook_data`)
- **Endpoint reference** — see `references/commodities.md` for all known ScienceBase item IDs and CSV schemas
- **Cache CSVs locally** when answering multiple questions about the same commodity — the MCS 2026 aggregated file is 3.2 MB
- **Handle BOM encoding** — all USGS CSVs use UTF-8 with BOM; open with `utf-8-sig`
- **MCS PDF chapters** provide narrative context (end-use breakdown, recycling, substitutes, world resources) not available in the CSV data — reference the PDF URL when deeper context is needed
