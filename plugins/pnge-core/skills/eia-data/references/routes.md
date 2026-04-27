# EIA API v2 — Route Reference

Full base URL: `https://api.eia.gov/v2/<route>`

## Electricity

| Route | Frequency | Key Data Columns | Key Facets |
|-------|-----------|-----------------|------------|
| `electricity/retail-sales/data/` | monthly, annual | price, revenue, sales, customers | stateid, sectorid |
| `electricity/electric-power-operational-data/data/` | monthly, annual | generation, consumption, stocks | stateid, sectorid, fueltypeid, plantid |
| `electricity/rto/region-data/data/` | hourly, daily | value (demand MWh) | respondent (BA code), type |
| `electricity/rto/fuel-type-data/data/` | hourly | value (MWh) | respondent (BA code), fueltype |
| `electricity/rto/region-sub-ba-data/data/` | hourly | value (MWh) | parent (BA), subba |
| `electricity/rto/interchange-data/data/` | hourly | value (MWh) | fromba, toba |
| `electricity/operating-generator-capacity/data/` | monthly | nameplate-capacity-mw, net-summer-capacity-mw | stateid, energy_source_code, sector |
| `electricity/state-electricity-profiles/source-disposition/data/` | annual | sales, receipts, generation | stateid |

### Sector IDs (sectorid)
- `RES` = Residential
- `COM` = Commercial
- `IND` = Industrial
- `TRA` = Transportation
- `OTH` = Other
- `ALL` = All sectors

### Fuel Type IDs (fueltypeid / fueltype)
- `NG` = Natural Gas
- `COL` = Coal
- `NUC` = Nuclear
- `SUN` = Solar
- `WND` = Wind
- `WAT` = Hydroelectric
- `OIL` = Petroleum
- `OTH` = Other

---

## Petroleum

| Route | Frequency | Key Data Columns | Key Facets |
|-------|-----------|-----------------|------------|
| `petroleum/pri/gnd/data/` | weekly | value ($/gal) | duoarea, product, process |
| `petroleum/pri/spt/data/` | daily, weekly, monthly | value ($/bbl) | duoarea, product, series |
| `petroleum/sum/sndw/data/` | weekly | value | duoarea, product, process |
| `petroleum/stoc/wstk/data/` | weekly | value (Mbbl) | duoarea, product, process |
| `petroleum/move/imp/data/` | monthly, annual | value (Mbbl) | originact, process, duoarea |
| `petroleum/move/exp/data/` | monthly, annual | value (Mbbl) | duoarea, product, process |
| `petroleum/cons/psup/data/` | monthly, annual | value | duoarea, product, process |
| `petroleum/crd/crpdn/data/` | monthly, annual | value (Mbbl/d) | duoarea, product, process |

### duoarea values
- `NUS` = National US
- `R10` = PADD 1 (East Coast)
- `R20` = PADD 2 (Midwest)
- `R30` = PADD 3 (Gulf Coast)
- `R40` = PADD 4 (Rocky Mountain)
- `R50` = PADD 5 (West Coast)
- `S{XX}` = State (e.g., `STX` = Texas, `SCA` = California)

### Common product codes
- `EPD2D` = No. 2 Diesel
- `EPM0` = Regular Motor Gasoline (all grades)
- `EPM0R` = Regular Reformulated Gasoline
- `EPC0` = Conventional Motor Gasoline
- `EPMR` = Regular Conventional Gas
- `EP00` = Crude Oil

---

## Natural Gas

| Route | Frequency | Key Data Columns | Key Facets |
|-------|-----------|-----------------|------------|
| `natural-gas/stor/sum/data/` | weekly | value (Bcf) | duoarea, process |
| `natural-gas/pri/sum/data/` | monthly, annual | value ($/Mcf or $/MMBtu) | duoarea, product, process |
| `natural-gas/prod/sum/data/` | monthly, annual | value (MMcf) | duoarea, process |
| `natural-gas/cons/sum/data/` | monthly, annual | value (MMcf) | duoarea, product, process |
| `natural-gas/move/imp/data/` | monthly, annual | value (MMcf) | duoarea, process |
| `natural-gas/move/exp/data/` | monthly, annual | value (MMcf) | duoarea, process |

### Natural Gas process codes (prices)
- `PRS` = Retail/Residential sales
- `PCI` = Commercial/Industrial sales
- `PRW` = Wellhead
- `PCG` = Citygate
- `PEU` = Electric Power sector

### Storage regions (duoarea for storage)
- `NUS` = US Total
- `R10` = East Region
- `R20` = Midwest Region  
- `R30` = South Central Region (incl. salt & nonsalt)
- `R40` = Mountain Region
- `R50` = Pacific Region

---

## Other Useful Routes

| Route | Description |
|-------|-------------|
| `total-energy/data/` | Monthly Energy Review — cross-sector totals |
| `seds/data/` | State Energy Data System — annual state-level all-fuel |
| `steo/data/` | Short Term Energy Outlook — 18-month forecasts |
| `co2-emissions/co2-emissions-aggregates/data/` | State CO2 emissions by sector |
| `crude-oil-imports/data/` | Monthly crude imports by country of origin |
| `aeo/data/` | Annual Energy Outlook — long-term projections |

---

## Discovery Pattern

When a route is unknown, walk the tree:
```bash
# List top-level categories
curl "https://api.eia.gov/v2/?api_key=<KEY>" | jq '.response.routes[].id'

# Drill into a category
curl "https://api.eia.gov/v2/petroleum/?api_key=<KEY>" | jq '.response.routes[].id'

# Get metadata for a specific dataset
curl "https://api.eia.gov/v2/petroleum/pri/gnd/?api_key=<KEY>" | jq '.response'
```
