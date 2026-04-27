# USGS Water Data API Reference

Complete parameter and endpoint documentation for USGS NWIS Water Services
and the Water Quality Portal.

---

## 1. NWIS Water Services

**Base URL:** `https://waterservices.usgs.gov/nwis/`

No authentication required. All responses include comment headers with
query metadata and disclaimers.

### 1.1 Common Parameters (all endpoints)

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `format` | string | Response format: `json`, `rdb` (tab-delimited), `waterml` (XML) | `format=json` |
| `sites` | string | Comma-separated USGS site numbers (zero-padded) | `sites=03058500,03061500` |
| `stateCd` | string | 2-letter state postal code | `stateCd=WV` |
| `countyCd` | string | 5-digit state+county FIPS code; standalone location filter (do NOT combine with stateCd) | `countyCd=54061` |
| `huc` | string | Hydrologic Unit Code (2, 4, 6, or 8 digits) | `huc=05020002` |
| `bBox` | string | Bounding box: west,south,east,north (decimal degrees) | `bBox=-80.5,39.0,-79.5,40.0` |
| `siteType` | string | Site type code(s), comma-separated | `siteType=GW,SP` |
| `siteStatus` | string | `active`, `inactive`, or `all` | `siteStatus=active` |
| `parameterCd` | string | 5-digit USGS parameter code(s), comma-separated | `parameterCd=00060,00065` |

**Location filters** (use exactly one):
- `sites` -- specific site numbers
- `stateCd` -- state (optionally with `countyCd`)
- `huc` -- hydrologic unit code
- `bBox` -- geographic bounding box

### 1.2 Instantaneous Values (`iv/`)

Real-time data at 15-minute intervals. Default returns most recent values.

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `startDT` | date | Start date (YYYY-MM-DD or ISO 8601) | `startDT=2024-06-01` |
| `endDT` | date | End date | `endDT=2024-06-30` |
| `period` | duration | ISO 8601 duration (alternative to start/end) | `period=P7D` (last 7 days) |
| `modifiedSince` | duration | Only data modified in this window | `modifiedSince=PT1H` |

**Limits:** Maximum 120 days of data per request. For longer periods use `dv/`.

**JSON response path:** `$.value.timeSeries[*].values[0].value[*]`

```bash
# Current conditions at a site (most recent reading)
curl -s "https://waterservices.usgs.gov/nwis/iv/?format=json\
&sites=03058500&parameterCd=00060"

# Last 7 days of 15-minute data
curl -s "https://waterservices.usgs.gov/nwis/iv/?format=json\
&sites=03058500&parameterCd=00060&period=P7D"

# Specific date range
curl -s "https://waterservices.usgs.gov/nwis/iv/?format=json\
&sites=03058500&parameterCd=00060,00065\
&startDT=2024-06-01&endDT=2024-06-07"
```

### 1.3 Daily Values (`dv/`)

Daily statistical values (mean, min, max). Available for the full
period of record (some sites back to 1800s).

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `startDT` | date | Start date (YYYY-MM-DD) | `startDT=2020-01-01` |
| `endDT` | date | End date | `endDT=2024-12-31` |
| `period` | duration | ISO 8601 duration | `period=P365D` |
| `statCd` | string | Statistic code: 00001=max, 00002=min, 00003=mean, 00008=median | `statCd=00003` |

**Default statistic:** 00003 (mean) if not specified.

```bash
# Daily mean discharge for a water year
curl -s "https://waterservices.usgs.gov/nwis/dv/?format=json\
&sites=03058500&parameterCd=00060\
&startDT=2023-10-01&endDT=2024-09-30"

# Daily mean specific conductance (proxy for TDS)
curl -s "https://waterservices.usgs.gov/nwis/dv/?format=json\
&sites=03058500&parameterCd=00095\
&startDT=2024-01-01&endDT=2024-12-31"

# Multiple parameters at once
curl -s "https://waterservices.usgs.gov/nwis/dv/?format=json\
&sites=03058500&parameterCd=00060,00065,00095\
&startDT=2024-01-01&endDT=2024-03-31"
```

### 1.4 Site Information (`site/`)

Metadata about monitoring stations. Best used with RDB format.

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `siteOutput` | string | `basic` or `expanded` (more columns) | `siteOutput=expanded` |
| `hasDataTypeCd` | string | Only sites with this data type: `iv`, `dv`, `gw`, `qw`, `pk`, `sv` | `hasDataTypeCd=dv` |
| `aquiferCd` | string | National aquifer code | `aquiferCd=S300PCMBCM` |
| `wellDepthMin` | number | Minimum well depth in feet | `wellDepthMin=100` |
| `wellDepthMax` | number | Maximum well depth in feet | `wellDepthMax=500` |

```bash
# All active groundwater sites in WV
curl -s "https://waterservices.usgs.gov/nwis/site/?format=rdb\
&stateCd=WV&siteType=GW&siteStatus=active"

# Sites with daily value discharge data in Monongalia County, WV
# countyCd uses the full 5-digit FIPS and is a standalone location filter
curl -s "https://waterservices.usgs.gov/nwis/site/?format=rdb\
&countyCd=54061&hasDataTypeCd=dv&parameterCd=00060"

# Expanded info for a specific site
curl -s "https://waterservices.usgs.gov/nwis/site/?format=rdb\
&sites=03058500&siteOutput=expanded"

# Sites within bounding box with water quality data
curl -s "https://waterservices.usgs.gov/nwis/site/?format=rdb\
&bBox=-80.5,39.0,-79.5,40.0&siteType=GW&hasDataTypeCd=qw"
```

**RDB output columns (basic):**
`agency_cd`, `site_no`, `station_nm`, `site_tp_cd`, `dec_lat_va`,
`dec_long_va`, `coord_acy_cd`, `dec_coord_datum_cd`, `alt_va`,
`alt_acy_va`, `alt_datum_cd`, `huc_cd`

**RDB output columns (expanded, additional):**
`drain_area_va`, `contrib_drain_area_va`, `tz_cd`, `local_time_fg`,
`well_depth_va`, `hole_depth_va`, `reliability_cd`, `gw_file_cd`,
`nat_aqfr_cd`, `aqfr_cd`, `aqfr_type_cd`, `construction_dt`

### 1.5 Statistics (`stat/`)

Pre-computed daily, monthly, or annual statistics. Only available in
RDB format.

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `statReportType` | string | `daily`, `monthly`, or `annual` | `statReportType=daily` |
| `statTypeCd` | string | Statistic(s): `mean`, `min`, `max`, `median`, `all` | `statTypeCd=all` |

```bash
# Daily statistics (366 rows: one per day-of-year)
curl -s "https://waterservices.usgs.gov/nwis/stat/?format=rdb\
&sites=03058500&parameterCd=00060\
&statReportType=daily&statTypeCd=all"

# Monthly statistics
curl -s "https://waterservices.usgs.gov/nwis/stat/?format=rdb\
&sites=03058500&parameterCd=00060\
&statReportType=monthly&statTypeCd=mean"

# Annual statistics
curl -s "https://waterservices.usgs.gov/nwis/stat/?format=rdb\
&sites=03058500&parameterCd=00060\
&statReportType=annual&statTypeCd=mean"
```

**Daily stat RDB columns:**
`agency_cd`, `site_no`, `parameter_cd`, `ts_id`, `loc_web_ds`,
`month_nu`, `day_nu`, `begin_yr`, `end_yr`, `count_nu`, `mean_va`,
`p05_va`, `p10_va`, `p20_va`, `p25_va`, `p50_va`, `p75_va`, `p80_va`,
`p90_va`, `p95_va`

### 1.6 Groundwater Levels (`gwlevels/`)

Discrete groundwater level measurements.

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `startDT` | date | Start date | `startDT=2020-01-01` |
| `endDT` | date | End date | `endDT=2024-12-31` |

```bash
# Groundwater levels at a well
curl -s "https://waterservices.usgs.gov/nwis/gwlevels/?format=rdb\
&sites=372322081241501\
&startDT=2020-01-01&endDT=2024-12-31"

# All GW level sites in a county
curl -s "https://waterservices.usgs.gov/nwis/gwlevels/?format=rdb\
&stateCd=WV&countyCd=061\
&startDT=2023-01-01&endDT=2024-12-31"
```

---

## 2. Water Quality Portal (WQP)

**Base URL:** `https://www.waterqualitydata.us/data/`

No authentication required. Returns CSV, TSV, or Excel. Aggregates data
from USGS NWIS, EPA STORET/WQX, and USDA ARS.

### 2.1 Common Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `statecode` | string | State FIPS with `US:` prefix | `statecode=US:54` (WV) |
| `countycode` | string | County FIPS with `US:SS:CCC` format | `countycode=US:54:061` |
| `siteid` | string | Monitoring location ID | `siteid=USGS-03058500` |
| `huc` | string | HUC code (8-digit) | `huc=05020002` |
| `characteristicName` | string | Analyte name (case-sensitive) | `characteristicName=Lithium` |
| `characteristicType` | string | Analyte group | `characteristicType=Inorganics, Major, Metals` |
| `siteType` | string | WQP site type | `siteType=Well` |
| `startDateLo` | date | Earliest sample date (MM-DD-YYYY) | `startDateLo=01-01-2020` |
| `startDateHi` | date | Latest sample date (MM-DD-YYYY) | `startDateHi=12-31-2024` |
| `mimeType` | string | `csv`, `tsv`, `xlsx` | `mimeType=csv` |
| `zip` | string | `yes` or `no` (compress response) | `zip=no` |
| `dataProfile` | string | Column set: `narrowResult`, `basicPhysChem`, `fullPhysChem` | `dataProfile=narrowResult` |
| `providers` | string | Data source: `NWIS`, `STORET`, `STEWARDS` | `providers=NWIS` |

**WQP date format is MM-DD-YYYY** (not YYYY-MM-DD like NWIS).

### 2.2 Result Search (Lab Data)

```bash
# Lithium results in WV (narrow profile -- fewer columns, faster)
curl -s "https://www.waterqualitydata.us/data/Result/search?\
statecode=US:54\
&characteristicName=Lithium\
&mimeType=csv&zip=no\
&dataProfile=narrowResult"

# Chloride in a specific HUC basin, 2020+
curl -s "https://www.waterqualitydata.us/data/Result/search?\
huc=05020002\
&characteristicName=Chloride\
&startDateLo=01-01-2020\
&mimeType=csv&zip=no\
&dataProfile=narrowResult"

# Multiple analytes at a site
curl -s "https://www.waterqualitydata.us/data/Result/search?\
siteid=USGS-03058500\
&characteristicName=Chloride\
&characteristicName=Sulfate\
&mimeType=csv&zip=no\
&dataProfile=narrowResult"

# TDS from groundwater wells in WV
curl -s "https://www.waterqualitydata.us/data/Result/search?\
statecode=US:54\
&characteristicName=Total%20dissolved%20solids\
&siteType=Well\
&mimeType=csv&zip=no\
&dataProfile=narrowResult"
```

**narrowResult key columns:**
| Column | Description |
|--------|-------------|
| `OrganizationIdentifier` | Reporting org (e.g., USGS-WV) |
| `MonitoringLocationIdentifier` | Site ID (e.g., USGS-393138080225801) |
| `ActivityStartDate` | Sample collection date (YYYY-MM-DD) |
| `CharacteristicName` | Analyte name |
| `ResultSampleFractionText` | Dissolved, Total, Suspended, etc. |
| `ResultMeasureValue` | Measured concentration |
| `ResultMeasure/MeasureUnitCode` | Units (mg/L, ug/L, etc.) |
| `ResultStatusIdentifier` | Historical, Accepted, Preliminary |
| `ResultDetectionConditionText` | Blank if detected; "Not Detected" if below DL |
| `USGSPCode` | USGS parameter code (e.g., 01130 for Li) |

### 2.3 Station Search

```bash
# Stations with lithium data in WV
curl -s "https://www.waterqualitydata.us/data/Station/search?\
statecode=US:54\
&characteristicName=Lithium\
&mimeType=csv&zip=no"

# Groundwater stations in a county
curl -s "https://www.waterqualitydata.us/data/Station/search?\
countycode=US:54:061\
&siteType=Well\
&mimeType=csv&zip=no"
```

**Station key columns:**
| Column | Description |
|--------|-------------|
| `MonitoringLocationIdentifier` | Site ID |
| `MonitoringLocationName` | Site name |
| `MonitoringLocationTypeName` | Well, Stream, Spring, etc. |
| `LatitudeMeasure` | Decimal latitude |
| `LongitudeMeasure` | Decimal longitude |
| `HUCEightDigitCode` | HUC-8 code |
| `WellDepthMeasure/MeasureValue` | Well depth (if applicable) |
| `AquiferName` | National aquifer name |

---

## 3. Characteristic Names for WQP (Common)

These are the exact case-sensitive names to use with `characteristicName`:

| Name | Description | USGS PCode |
|------|-------------|------------|
| `Lithium` | Li dissolved/total | 01130 |
| `Magnesium` | Mg dissolved/total | 00925 |
| `Calcium` | Ca dissolved/total | 00915 |
| `Sodium` | Na dissolved/total | 00930 |
| `Potassium` | K dissolved/total | 00935 |
| `Chloride` | Cl dissolved | 00940 |
| `Sulfate` | SO4 dissolved | 00945 |
| `Fluoride` | F dissolved | 00950 |
| `Iron` | Fe dissolved/total | 01046 |
| `Manganese` | Mn dissolved/total | 01056 |
| `Total dissolved solids` | TDS (residue at 180C) | 70300 |
| `Specific conductance` | SC at 25C | 00095 |
| `pH` | pH in standard units | 00400 |
| `Temperature, water` | Water temperature | 00010 |
| `Barium` | Ba dissolved/total | 01005 |
| `Strontium` | Sr dissolved/total | 01080 |
| `Bromide` | Br dissolved | 71870 |
| `Boron` | B dissolved | 01020 |

---

## 4. State FIPS Codes (Appalachian Basin)

| State | Postal | FIPS | WQP Format |
|-------|--------|------|------------|
| West Virginia | WV | 54 | US:54 |
| Pennsylvania | PA | 42 | US:42 |
| Ohio | OH | 39 | US:39 |
| Virginia | VA | 51 | US:51 |
| Kentucky | KY | 21 | US:21 |
| New York | NY | 36 | US:36 |
| Maryland | MD | 24 | US:24 |

---

## 5. Response Format Details

### 5.1 NWIS JSON Structure (iv/ and dv/)

```
Root
  .value
    .queryInfo              -- query metadata
      .queryURL             -- reconstructed request URL
      .criteria             -- parsed query parameters
      .note[]               -- server notes, disclaimers
    .timeSeries[]           -- array of time series (one per site+param+stat)
      .sourceInfo           -- site metadata
        .siteName           -- human-readable site name
        .siteCode[0].value  -- USGS site number
        .geoLocation.geogLocation
          .latitude         -- decimal latitude
          .longitude        -- decimal longitude
        .siteProperty[]     -- siteTypeCd, hucCd, stateCd, countyCd
      .variable             -- parameter metadata
        .variableCode[0].value  -- parameter code (e.g., "00060")
        .variableName       -- human name (e.g., "Streamflow, ft3/s")
        .unit.unitCode      -- units (e.g., "ft3/s")
        .noDataValue        -- sentinel for missing data (typically -999999.0)
      .values[0]            -- data array wrapper
        .value[]            -- the actual measurements
          .value            -- measured value (string)
          .dateTime         -- ISO 8601 timestamp
          .qualifiers[]     -- qualifier codes (A, P, e, etc.)
        .qualifier[]        -- qualifier code definitions
        .method[]           -- measurement method metadata
```

### 5.2 NWIS RDB Format

```
# Comment lines (metadata, disclaimers)
# ...
column1<TAB>column2<TAB>column3
5s<TAB>15s<TAB>8n          <-- width/type specifiers (skip this row)
data1<TAB>data2<TAB>data3
data4<TAB>data5<TAB>data6
```

Type suffixes: `s` = string, `n` = numeric, `d` = date.

### 5.3 WQP CSV Format

Standard RFC 4180 CSV with header row. No comment lines. Fields may
contain commas within double-quoted values. Large result sets may
include UTF-8 BOM.
