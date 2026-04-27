# UN Comtrade API v1 Reference

## Endpoints

### Public Preview (No Key Required)
```
GET https://comtradeapi.un.org/public/v1/preview/C/{freq}/HS?{params}
```
- Rate limit: 500 requests/day
- Restrictions: 1 period per query, descriptions returned as null
- Best for: Single-period, single-commodity lookups

### Authenticated (Subscription Key Required)
```
GET https://comtradeapi.un.org/data/v1/get/C/{freq}/HS?{params}&subscription-key={KEY}
```
- Rate limit: Higher (varies by subscription tier)
- Features: Multi-period queries, full descriptions in response
- Registration: https://comtradeplus.un.org/

### Legacy (Deprecated -- Redirects)
```
GET https://comtrade.un.org/api/get   # DO NOT USE -- redirects to comtradeplus.un.org
```

---

## URL Path Components

```
/{typeCode}/{freqCode}/{classificationCode}
```

| Component | Values | Description |
|-----------|--------|-------------|
| typeCode | `C` | Commodities (goods trade) |
| typeCode | `S` | Services trade |
| freqCode | `A` | Annual |
| freqCode | `M` | Monthly |
| classificationCode | `HS` | Harmonized System (most common) |
| classificationCode | `S3` | SITC Rev.3 |
| classificationCode | `S4` | SITC Rev.4 |
| classificationCode | `BEC` | Broad Economic Categories |

---

## Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `reporterCode` | int | Yes | ISO 3166-1 numeric code of reporting country |
| `period` | string | Yes | Year (annual) or YYYYMM (monthly). Comma-separated for auth endpoint |
| `cmdCode` | string | Yes | HS commodity code (2/4/6 digit). Comma-separated for multiple |
| `flowCode` | string | Yes | Trade flow direction |
| `partnerCode` | int | No | Partner country code. 0 = World. Omit for all partners |
| `partner2Code` | int | No | Second partner (mode of transport partner) |
| `subscription-key` | string | Auth only | Subscription key for authenticated endpoint |
| `customsCode` | string | No | Customs procedure code |
| `motCode` | int | No | Mode of transport code |

### Flow Codes

| Code | Description |
|------|-------------|
| `M` | Imports |
| `X` | Exports |
| `RM` | Re-imports |
| `RX` | Re-exports |

---

## HS Commodity Codes for PNGE Research

### Lithium Compounds and Products

| HS Code | Description | Notes |
|---------|-------------|-------|
| 2825 | Hydrazine, hydroxylamine and their inorganic salts; other inorganic bases; other metal oxides, hydroxides and peroxides | Includes lithium oxide and hydroxide but also non-lithium products |
| 282520 | Lithium oxide and hydroxide | 6-digit, lithium-specific (availability varies by reporter) |
| 2836 | Carbonates; peroxocarbonates (percarbonates) | Parent heading |
| 283691 | Lithium carbonate | Key lithium compound, battery-grade feedstock |
| 283699 | Other carbonates, peroxocarbonates | May contain some lithium compounds |
| 2827 | Chlorides | Includes lithium chloride (282790) |
| 282790 | Other chlorides | Includes lithium chloride |

### Magnesium

| HS Code | Description | Notes |
|---------|-------------|-------|
| 2519 | Natural magnesium carbonate (magnesite); fused magnesia; dead-burned magnesia | Raw material |
| 251910 | Natural magnesium carbonate (magnesite) | Unprocessed |
| 251990 | Fused magnesia; dead-burned (sintered) magnesia | Processed |
| 8104 | Magnesium and articles thereof | Metal form |
| 810411 | Unwrought magnesium, containing at least 99.8% by weight of magnesium | High-purity |
| 810419 | Other unwrought magnesium | Alloys and lower purity |
| 810420 | Magnesium waste and scrap | Recycling |
| 810430 | Magnesium raspings, turnings and granules | Processed forms |
| 810490 | Other magnesium articles | Fabricated products |

### Petroleum and Natural Gas

| HS Code | Description | Notes |
|---------|-------------|-------|
| 2709 | Petroleum oils and oils from bituminous minerals, crude | Crude oil |
| 270900 | Crude petroleum | Main crude code |
| 2710 | Petroleum oils, not crude; preparations thereof | Refined products |
| 271012 | Light oils and preparations (gasoline, naphtha) | Motor fuels |
| 271019 | Medium/heavy oils (kerosene, diesel, fuel oil) | Industrial fuels |
| 2711 | Petroleum gases and other gaseous hydrocarbons | LNG, LPG, natural gas |
| 271111 | Natural gas, liquefied (LNG) | Liquefied natural gas |
| 271121 | Natural gas in gaseous state | Pipeline gas |

### Oilfield Minerals and Chemicals

| HS Code | Description | Notes |
|---------|-------------|-------|
| 2511 | Natural barium sulfate (barite); natural barium carbonate (witherite) | Drilling mud weighting agent |
| 251110 | Natural barium sulfate (barite) | Primary drilling mineral |
| 251120 | Natural barium carbonate (witherite) | Less common |
| 2524 | Asbestos | Legacy oilfield use |
| 2529 | Feldspar; leucite; nepheline and nepheline syenite; fluorspar | Fluorspar for HF production |
| 252921 | Fluorspar, containing by weight 97% or more of calcium fluoride | Acid-grade |
| 252922 | Fluorspar, containing by weight more than 97% of calcium fluoride | Metallurgical grade |

### Other Critical Minerals

| HS Code | Description | Notes |
|---------|-------------|-------|
| 2602 | Manganese ores and concentrates | Battery cathode material |
| 2603 | Copper ores and concentrates | Electrical applications |
| 2605 | Cobalt ores and concentrates | Battery material |
| 2606 | Aluminium ores and concentrates (bauxite) | Aluminum production |
| 2607 | Lead ores and concentrates | Batteries |
| 2608 | Zinc ores and concentrates | Galvanizing |
| 2610 | Chromium ores and concentrates | Stainless steel |
| 2611 | Tungsten ores and concentrates | Hard metals |
| 2612 | Uranium or thorium ores and concentrates | Nuclear fuel |
| 2844 | Radioactive chemical elements and isotopes | Enriched uranium |
| 7501 | Nickel mattes | Intermediate product |
| 7502 | Unwrought nickel | Primary metal |
| 7504 | Nickel powders and flakes | Battery-grade |
| 7505 | Nickel bars, rods, profiles and wire | Fabricated |
| 7506 | Nickel plates, sheets, strip and foil | Fabricated |
| 7508 | Other nickel articles | Misc |
| 8112 | Beryllium, chromium, germanium, vanadium, gallium, hafnium, indium, niobium, rhenium, thallium | Assorted critical minerals |

---

## Country Codes (ISO 3166-1 Numeric)

### Major Reporters / PNGE-Relevant

| Code | ISO Alpha | Country | Trade Relevance |
|------|-----------|---------|-----------------|
| 0 | -- | World (aggregate) | Total trade flow |
| 842 | USA | United States | Primary reporter for US trade analysis |
| 156 | CHN | China | Top Li/Mg producer and exporter |
| 152 | CHL | Chile | Top lithium producer (Atacama brines) |
| 36 | AUS | Australia | Top lithium producer (spodumene) |
| 32 | ARG | Argentina | Lithium brine triangle |
| 68 | BOL | Bolivia | Emerging lithium brine |
| 76 | BRA | Brazil | Lithium, magnesium, barite |
| 124 | CAN | Canada | Nickel, petroleum, critical minerals |
| 643 | RUS | Russia | Nickel, petroleum, uranium |
| 710 | ZAF | South Africa | Manganese, chromium |
| 180 | COD | Dem. Rep. Congo | Cobalt |

### Major Trade Partners / Consumers

| Code | ISO Alpha | Country |
|------|-----------|---------|
| 392 | JPN | Japan |
| 410 | KOR | Republic of Korea |
| 276 | DEU | Germany |
| 826 | GBR | United Kingdom |
| 251 | FRA | France |
| 380 | ITA | Italy |
| 724 | ESP | Spain |
| 56 | BEL | Belgium (transshipment hub) |
| 528 | NLD | Netherlands (transshipment hub) |
| 702 | SGP | Singapore (transshipment hub) |
| 344 | HKG | Hong Kong (transshipment hub) |

### OPEC / Petroleum Exporters

| Code | ISO Alpha | Country |
|------|-----------|---------|
| 682 | SAU | Saudi Arabia |
| 784 | ARE | United Arab Emirates |
| 368 | IRQ | Iraq |
| 414 | KWT | Kuwait |
| 566 | NGA | Nigeria |
| 862 | VEN | Venezuela |

---

## Response Format

### Top-Level Envelope

```json
{
  "elapsedTime": "0.14 secs",
  "count": 14,
  "data": [ ... ],
  "error": ""
}
```

| Field | Type | Description |
|-------|------|-------------|
| `elapsedTime` | string | Server processing time |
| `count` | int | Number of records returned. -1 indicates query error |
| `data` | array | Array of trade record objects |
| `error` | string | Error message if any. Empty string on success |

### Data Record Fields

| Field | Type | Description |
|-------|------|-------------|
| `typeCode` | string | "C" for commodities |
| `freqCode` | string | "A" (annual) or "M" (monthly) |
| `refPeriodId` | int | Reference period as YYYYMMDD |
| `refYear` | int | Reference year |
| `refMonth` | int | Reference month (52 = annual aggregate) |
| `period` | string | Period as string ("2023" or "202301") |
| `reporterCode` | int | Reporter country code |
| `reporterISO` | string/null | Reporter ISO alpha-3 (null in preview) |
| `reporterDesc` | string/null | Reporter name (null in preview) |
| `flowCode` | string | "M", "X", "RM", or "RX" |
| `flowDesc` | string/null | Flow description (null in preview) |
| `partnerCode` | int | Partner country code |
| `partnerISO` | string/null | Partner ISO alpha-3 (null in preview) |
| `partnerDesc` | string/null | Partner name (null in preview) |
| `partner2Code` | int | Second partner code |
| `cmdCode` | string | HS commodity code |
| `cmdDesc` | string/null | Commodity description (null in preview) |
| `qtyUnitCode` | int | Quantity unit (8=kg, 1=no qty) |
| `qtyUnitAbbr` | string/null | Unit abbreviation (null in preview) |
| `qty` | float | Quantity in reported units |
| `isQtyEstimated` | bool | Whether quantity is estimated |
| `altQtyUnitCode` | int | Alternate quantity unit |
| `altQty` | float | Alternate quantity |
| `netWgt` | float | Net weight in kilograms |
| `isNetWgtEstimated` | bool | Whether net weight is estimated |
| `grossWgt` | float | Gross weight in kilograms |
| `cifvalue` | float | CIF value in USD (imports) |
| `fobvalue` | float | FOB value in USD (exports) |
| `primaryValue` | float | CIF for imports, FOB for exports |
| `legacyEstimationFlag` | int | 0=reported, 2=estimated qty, 4=estimated value, 6=both |
| `isReported` | bool | Whether directly reported by the country |
| `isAggregate` | bool | Whether this is an aggregate record |
| `customsCode` | string | Customs procedure code |
| `mosCode` | string | Mode of supply code |
| `motCode` | int | Mode of transport code |

### Quantity Unit Codes

| Code | Unit |
|------|------|
| -1 | Not applicable |
| 1 | No quantity |
| 2 | Area in square meters |
| 3 | Electrical energy in kWh |
| 4 | Length in meters |
| 5 | Number of items |
| 6 | Number of pairs |
| 7 | Volume in liters |
| 8 | Weight in kilograms |
| 9 | Thousands of items |
| 10 | Number of packages |
| 11 | Dozen |
| 12 | Volume in cubic meters |
| 13 | Carat |

---

## Example Requests

### US imports of lithium carbonate, all partners, 2023 (public preview)
```bash
curl -s "https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=842&period=2023&cmdCode=283691&flowCode=M"
```

### US imports of magnesium metal, all partners, 2023 (public preview)
```bash
curl -s "https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=842&period=2023&cmdCode=8104&flowCode=M"
```

### US imports of crude petroleum, all partners, 2023 (public preview)
```bash
curl -s "https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=842&period=2023&cmdCode=2709&flowCode=M"
```

### US imports of barite, all partners, 2023 (public preview)
```bash
curl -s "https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=842&period=2023&cmdCode=2511&flowCode=M"
```

### China exports of lithium carbonate, 2022-2023 (authenticated, multi-period)
```bash
curl -s "https://comtradeapi.un.org/data/v1/get/C/A/HS?reporterCode=156&period=2022,2023&cmdCode=283691&flowCode=X&subscription-key=$KEY"
```

### Monthly US lithium carbonate imports, January-June 2023 (authenticated)
```bash
curl -s "https://comtradeapi.un.org/data/v1/get/C/M/HS?reporterCode=842&period=202301,202302,202303,202304,202305,202306&cmdCode=283691&flowCode=M&subscription-key=$KEY"
```

### Multiple commodities in one query (authenticated)
```bash
curl -s "https://comtradeapi.un.org/data/v1/get/C/A/HS?reporterCode=842&period=2023&cmdCode=283691,2825,8104&flowCode=M&subscription-key=$KEY"
```

---

## Common Patterns

### Building a Time Series (Public Preview)
Since the preview endpoint limits to 1 period, loop over years:
```bash
for YEAR in 2019 2020 2021 2022 2023; do
    curl -s "https://comtradeapi.un.org/public/v1/preview/C/A/HS?\
reporterCode=842&period=${YEAR}&cmdCode=283691&flowCode=M&partnerCode=0"
    sleep 1
done
```

### Comparing Import Sources
Omit `partnerCode` to get all partners, then sort by `primaryValue`:
```bash
curl -s "https://comtradeapi.un.org/public/v1/preview/C/A/HS?\
reporterCode=842&period=2023&cmdCode=283691&flowCode=M" \
  | jq '.data | sort_by(-.primaryValue) | .[:10]'
```

### Calculating Supply Concentration
Use the World total (partnerCode=0) and individual partners to compute shares:
```bash
WORLD=$(curl -s "...&partnerCode=0" | jq '.data[0].primaryValue')
ALL=$(curl -s "..." | jq '[.data[] | select(.partnerCode != 0)] | sort_by(-.primaryValue)')
# Top-3 share = sum of top 3 values / WORLD * 100
```
