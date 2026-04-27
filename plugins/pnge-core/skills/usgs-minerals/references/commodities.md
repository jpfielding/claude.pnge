# USGS Mineral Commodity Data — Endpoint Reference

All data is public. No API key required.

---

## 1. ScienceBase API

Base URL: `https://www.sciencebase.gov/catalog/`

ScienceBase hosts all MCS data releases as downloadable CSV files. Each
commodity has its own ScienceBase item with one or more CSV files attached.

### Search for MCS data releases

```bash
# Search for all MCS 2025 commodity data releases
curl -s "https://www.sciencebase.gov/catalog/items?q=mineral+commodity+summaries+2025&format=json&max=10&fields=title,id"

# Search for a specific commodity
curl -s "https://www.sciencebase.gov/catalog/items?q=mineral+commodity+summaries+2025+lithium&format=json&max=5&fields=title,id,files"
```

### Get item details (including file download URLs)

```bash
curl -s "https://www.sciencebase.gov/catalog/item/{ITEM_ID}?format=json&fields=title,files"
```

### Download a CSV file

```bash
curl -sL "{downloadUri_from_files_array}" -o output.csv
```

### Key parameters

| Parameter | Example | Notes |
|-----------|---------|-------|
| `q` | `mineral+commodity+summaries+2025+lithium` | Full-text search |
| `format` | `json` | Response format |
| `max` | `10` | Max results per page |
| `offset` | `0` | Pagination offset |
| `fields` | `title,id,files` | Comma-separated field list |
| `parentId` | `{parent_item_id}` | Filter by parent collection |

---

## 2. Known ScienceBase Item IDs

### MCS 2026 — Aggregated Commodities Data (LATEST)

| Field | Value |
|-------|-------|
| Title | Mineral Commodity Summaries 2026 Data Release |
| ID | `696a75d5d4be0228872d3bf8` |
| Key file | `MCS2026_Commodities_Data.csv` (3.2 MB, all commodities) |
| Other files | Fig1-Fig13 CSVs, T1-T7 tables, Salient Statistics ZIP |

**MCS2026_Commodities_Data.csv columns:**
```
MCS chapter, Section, Commodity, Country, Statistics, Statistics_detail,
Unit, Year, Value, Notes, Is critical mineral 2025, Other notes
```

**Sections per commodity:**
- `Salient Statistics - United States` (production, imports, exports, consumption, price, employment, net import reliance)
- `World Mine Production and Reserves` (production by country, reserves by country)
- `Import Sources` (source countries and percentages)

### MCS 2025 — Per-Commodity Data Releases

**Lithium:**

| Field | Value |
|-------|-------|
| Title | Mineral Commodity Summaries 2025 - LITHIUM Data Release |
| ID | `6797ff62d34ea8c18376e1cb` |
| CSV file | `mcs2025-lithium_salient.csv` (346 bytes) |

CSV columns: `DataSource, Commodity, Year, USprod_t, Imports_t, Exports_t, Consump_t, Price_dt, Employment_num, NIR_pct`

Sample data (2024): Production=W, Imports=3300 t, Exports=1700 t, Price=$14,000/t, NIR >50%

**Magnesium Compounds:**

| Field | Value |
|-------|-------|
| Title | Mineral Commodity Summaries 2025 - MAGNESIUM COMPOUNDS Data Release |
| ID | `6797ffe2d34ea8c18376e1da` |
| CSV file | `mcs2025-mgcomp_salient.csv` (423 bytes) |

CSV columns: `DataSource, Commodity, Year, USprod_kt, Shipments_kt, Imports_kt, Exports_kt, Consump_kt, Employment_Plant_num, NIR_pct`

Sample data (2024): Production=430 kt, Imports=520 kt, Consumption=890 kt, NIR=52%

**Magnesium Metal:**

| Field | Value |
|-------|-------|
| Title | Mineral Commodity Summaries 2025 - MAGNESIUM METAL Data Release |
| ID | `6797ffffd34ea8c18376e1e5` |
| CSV file | `mcs2025-mgmet_salient.csv` (523 bytes) |

CSV columns: `DataSource, Commodity, Year, USprod_Primary_kt, USprod_Secondary_kt, Imports_kt, Exports_kt, Consump_Reported_kt, Consump_Apparent_kt, Price_European_dlb, Price_dt, Stocks_kt, Employment_num, NIR_pct`

Sample data (2024): Primary production=0, Secondary=110 kt, Imports=90 kt, Price=$2,900/t, NIR >75%

### MCS 2025 — Salient Commodity (Aggregated)

| Field | Value |
|-------|-------|
| Title | Mineral Commodity Summaries 2025 - Salient Commodity Data Release |
| ID | `6793e234d34e72688d6b71e7` |
| Key file | `Salient_Commodity_Data_Release_Grouped.zip` (400 KB) |

---

## 3. World Minerals Outlook 2029

| Field | Value |
|-------|-------|
| Title | World minerals outlook to 2029 — Cobalt, gallium, helium, lithium, magnesium, palladium, platinum, and titanium data |
| ID | `67b8b168d34e1a2e835b7e6c` |
| CSV file | `Outlook 2025 Data Release 031125.csv` (192 KB) |

CSV columns: `Mineral_Commodity, Year, Note, Quantity, Data_type, Unit_MEAS, Form, Geographic_Region, Figure_Use, Data Sources`

**Commodities covered:** Cobalt, Gallium, Helium, Lithium, Magnesium metal, Palladium, Platinum, Titanium

**Data scope:** World production by country, 2018-2029 (with projections for 2025-2029)

**Lithium rows:** ~90 rows covering production by country (metric tons Li content)
**Magnesium rows:** ~85 rows covering primary metal production by country

---

## 4. MCS PDF Publications

Individual commodity chapters are published as PDF fact sheets:

| Year | URL Pattern |
|------|-------------|
| MCS 2026 | `https://pubs.usgs.gov/periodicals/mcs2026/mcs2026-{commodity}.pdf` |
| MCS 2025 | `https://pubs.usgs.gov/periodicals/mcs2025/mcs2025-{commodity}.pdf` |
| MCS 2024 | `https://pubs.usgs.gov/periodicals/mcs2024/mcs2024-{commodity}.pdf` |

Commodity slug examples: `lithium`, `magnesium-compounds`, `magnesium-metal`

```bash
# Download lithium MCS 2025 chapter PDF
curl -sL "https://pubs.usgs.gov/periodicals/mcs2025/mcs2025-lithium.pdf" -o mcs2025-lithium.pdf
```

---

## 5. Key Data Points by Commodity

### Lithium

| Data Point | Where to Find | Latest (MCS 2026) |
|------------|---------------|---------------------|
| U.S. mine production | Salient Statistics | W (withheld) |
| U.S. imports | Salient Statistics | 3,300 t (2025 est.) |
| Battery-grade Li2CO3 price | Salient Statistics | $11,700/t (2025 est.) |
| World mine production | World Mine Production | 290,000 t (2025 est.) |
| World reserves | Reserves | 37,000,000 t |
| Top producer | World Mine Production | Australia (92,000 t) |
| Net import reliance | Salient Statistics | >25% |
| End uses | MCS PDF chapter | Batteries 87%, ceramics/glass 4% |

### Magnesium Compounds

| Data Point | Where to Find | Latest (MCS 2025) |
|------------|---------------|---------------------|
| U.S. production | Salient Statistics | 430 kt |
| U.S. imports | Salient Statistics | 520 kt |
| U.S. consumption | Salient Statistics | 890 kt |
| Net import reliance | Salient Statistics | 52% |

### Magnesium Metal

| Data Point | Where to Find | Latest (MCS 2025) |
|------------|---------------|---------------------|
| U.S. primary production | Salient Statistics | 0 (none since 2023) |
| U.S. secondary production | Salient Statistics | 110 kt |
| Price (European free market) | Salient Statistics | $3.50/lb ($2,900/t) |
| Net import reliance | Salient Statistics | >75% |

---

## 6. Searching for Other Commodities

The MCS 2025 data releases follow a naming convention on ScienceBase. To find
any commodity, search with:

```bash
curl -s "https://www.sciencebase.gov/catalog/items?q=mineral+commodity+summaries+2025+{COMMODITY}&format=json&max=5&fields=title,id,files"
```

For MCS 2026, the aggregated `MCS2026_Commodities_Data.csv` contains all
commodities in a single file. Filter by the `Commodity` column.

Known critical minerals in MCS: Aluminum, Antimony, Arsenic, Barite, Beryllium,
Bismuth, Boron, Cadmium, Cesium, Chromium, Cobalt, Copper, Fluorspar, Gallium,
Germanium, Gold, Graphite, Hafnium, Helium, Indium, Iodine, Iron and Steel,
Lead, Lithium, Magnesium Compounds, Magnesium Metal, Manganese, Mercury,
Molybdenum, Nickel, Niobium, Palladium, Peat, Phosphate Rock, Platinum,
Potash, Rare Earths, Rhenium, Rubidium, Ruthenium, Scandium, Selenium,
Silicon, Silver, Strontium, Sulfur, Tantalum, Tellurium, Thallium, Thorium,
Tin, Titanium, Tungsten, Uranium, Vanadium, Zinc, Zirconium
