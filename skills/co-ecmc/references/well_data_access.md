# ECMC Well Data Access — Detailed Patterns

Supplementary reference for programmatic well-level data retrieval from
ECMC. Covers COGIS inquiry applications, bulk file schemas, and WebLink
imaged document searches.

---

## 1. Colorado API Number Structure

Colorado API numbers are standard AAPG 12-digit identifiers with the state
prefix dropped on older records:

```
05 - XXX - XXXXX - XX
^    ^     ^       ^
|    |     |       Sidetrack/recompletion suffix (00 = original wellbore)
|    |     5-digit unique sequence within county
|    3-digit county FIPS code
Colorado state code (always 05)
```

**Examples:**
- `05-123-12345` or `0512312345` — a Weld County well, wellbore 00
- `05-045-67890-01` — a Garfield County well, first sidetrack

**County FIPS codes (key producers):**

| FIPS | County |
|------|--------|
| 001 | Adams |
| 005 | Arapahoe |
| 013 | Boulder |
| 014 | Broomfield |
| 045 | Garfield |
| 067 | La Plata |
| 071 | Las Animas |
| 103 | Rio Blanco |
| 123 | Weld |

Full list at:
`https://ecmc.state.co.us/documents/about/COGIS_Help/API_County_codes.pdf`

---

## 2. COGIS Inquiry Applications (ColdFusion Web Apps)

All COGIS tools are ColdFusion-based and return HTML. They accept GET
parameters but in practice require a valid session cookie for most
detail pages. Use a cookie jar in `curl`:

```bash
# Initialize a session:
curl -sL -c cogis_cookies.txt -A "Mozilla/5.0" \
  "https://ecmc.state.co.us/cogis/FacilitySearch.asp" -o /dev/null

# Search by API number:
curl -sL -b cogis_cookies.txt -c cogis_cookies.txt -A "Mozilla/5.0" \
  --data-urlencode "api_county=123" \
  --data-urlencode "api_seq_num=12345" \
  "https://ecmc.state.co.us/cogis/FacilitySearch.asp" \
  -o well_search.html

# Pull the detail page once you have the facility ID:
curl -sL -b cogis_cookies.txt -A "Mozilla/5.0" \
  "https://ecmc.state.co.us/cogis/FacilityDetail.asp?facid=12312345&type=WELL" \
  -o well_detail.html
```

**COGIS inquiry catalog (landing URLs):**

| Tool | URL |
|------|-----|
| Facility (well / tank / pit) Inquiry | `https://ecmc.state.co.us/cogis/FacilitySearch.asp` |
| Production Data Inquiry | `https://ecmc.state.co.us/cogis/ProductionSearch.asp` |
| Inspection/Incident Inquiry | `https://ecmc.state.co.us/cogis/InspectIncident.asp` |
| Operator Inquiry | `https://ecmc.state.co.us/cogis/OperatorSearch.asp` |
| Levy Search | `https://ecmc.state.co.us/cogis/LevySearch.asp` |
| Sample Site Inquiry | `https://ecmc.state.co.us/cogis/SampleSiteSearch.asp` |
| Local Government Info | `https://ecmc.state.co.us/cogis/LGI.asp` |

---

## 3. Bulk Production File Schemas

### `monthly_prod.csv` (current year, updated monthly)

Typical columns (verify header on download):

| Column | Type | Description |
|--------|------|-------------|
| API_COUNTY | int | 3-digit county FIPS |
| API_SEQ_NUM | int | 5-digit within-county sequence |
| SIDE_TRACK_NUM | int | Sidetrack identifier, usually 00 |
| NAME | string | Well or facility name |
| FORMATION | string | Primary producing formation |
| FIRST_PROD_DATE | date | First production date |
| LAST_PROD_DATE | date | Last reported production |
| OIL_PROD | int | Barrels oil this report month |
| GAS_PROD | int | MCF gas this report month |
| WATER_PROD | int | Barrels water this report month |
| OIL_DAYS | int | Producing days oil |
| GAS_DAYS | int | Producing days gas |
| WATER_DAYS | int | Producing days water |
| OIL_DISPOSITION | string | Sold/used/lost code |
| GAS_DISPOSITION | string | Sold/flared/vented code |
| REPORT_YEAR | int | |
| REPORT_MONTH | int | |
| OPERATOR_NUM | int | ECMC operator number |
| OPERATOR_NAME | string | |

### `{YYYY}_prod_reports.csv` (one per calendar year)

Same schema as `monthly_prod.csv` but covering all 12 months of the named
year. File sizes 100-250 MB depending on well count and year.

### Annual Production Summary (Access `.mdb`)

The `CO {YYYY} Annual Production Summary-xp.zip` files contain Microsoft
Access databases. Extract and query with `mdbtools`:

```bash
curl -sO "https://ecmc.state.co.us/documents/data/downloads/production/CO%202024%20Annual%20Production%20Summary.zip"
unzip "CO 2024 Annual Production Summary.zip"
mdb-tables "CO 2024 Annual Production Summary.mdb"
mdb-export "CO 2024 Annual Production Summary.mdb" Production > prod_2024.csv
```

---

## 4. Well Density and Spatial Context

```bash
# Colorado-wide well density raster (ECMC publishes periodically):
curl -sLO -A "Mozilla/5.0" \
  "https://ecmc.colorado.gov/sites/ecmc/files/WellDensityRaster_20250902.gdb_.zip"

# Field boundaries:
curl -sO "https://ecmc.state.co.us/documents/data/downloads/gis/COGCC_FIELDS_SHP.zip"

# Pits (surface facilities):
curl -sO "https://ecmc.state.co.us/documents/data/downloads/gis/PITS_SHP.zip"

# Rule 317B public water supply buffers:
curl -sO "https://ecmc.state.co.us/documents/data/downloads/gis/Rule317B_Shapefiles.zip"

# Rule 411A surface water:
curl -sO "https://ecmc.state.co.us/documents/data/downloads/gis/Rule411a_SurfaceWater.gdb.zip"
```

Read with GDAL:

```bash
ogrinfo COGCC_FIELDS_SHP.zip
ogr2ogr -f GeoJSON fields.geojson COGCC_FIELDS_SHP.zip -where "FIELD_NAME = 'WATTENBERG'"
```

---

## 5. Imaged Document Search (WebLink)

ECMC's WebLink archive hosts scanned well files — Form 2A APDs, Form 2
drilling permits, Form 5 completion reports, Form 5A stimulation data
(Colorado's equivalent to FracFocus), Form 6 sundry notices, Form 7
operator production reports, MIT records.

**URL:** `https://ecmc.state.co.us/weblink/`

The WebLink UI is JavaScript-heavy and not amenable to direct `curl`
scraping. For automated work, use it to look up individual well document
indexes, then download PDFs directly. Form 5A stimulation data is the most
useful for fracturing research:

- Stage-by-stage fluid volumes
- Proppant loading
- Additive tradenames (with CBI redactions similar to FracFocus)
- Pressures, rates, breakdown gradients

---

## 6. Commission Orders and Hearings

Commission orders (the legal instrument for field designation, spacing,
pooling, Class VI permits) are indexed at:

```
https://ecmc.colorado.gov/hearings/commission-orders
```

Order numbers follow the format `{CAUSE}-{DOCKET}-{ORDER}`. Example:
`1-189` references Cause 1, Order 189.

Rulemaking dockets (including SB19-181 implementation) are at:

```
https://ecmc.colorado.gov/hearings/rulemaking
```

The eFiling system for hearings documents:

```
https://ecmc.colorado.gov/hearings/efiling-system
```

---

## 7. Reference PDFs (Lookup Tables)

These PDFs on the legacy host translate codes to human-readable values:

| PDF | URL | Contents |
|-----|-----|----------|
| API / County Codes | `https://ecmc.state.co.us/documents/about/COGIS_Help/API_County_codes.pdf` | State + county FIPS cross-ref |
| Field List | `https://ecmc.state.co.us/documents/about/COGIS_Help/field_list.pdf` | Field name → field code |
| Formation List | `https://ecmc.state.co.us/documents/about/COGIS_Help/formation_list.pdf` | Formation name → code |
| Status Codes | `https://ecmc.state.co.us/documents/about/COGIS_Help/Status_Codes.pdf` | Well status code definitions |
| Meridian Codes | `https://ecmc.state.co.us/documents/about/COGIS_Help/GIS_HELP/COGCCMeridianCodes.pdf` | PLSS meridian codes |

Pull these on first use and cache them; they rarely change.

---

## 8. Rate Limiting and Scraping Etiquette

- Bulk files — fetch at most once per 24 hours; they're refreshed monthly
- COGIS web apps — keep request rate under ~1/sec; ColdFusion sessions
  are tracked and aggressive scraping gets IPs throttled
- WebLink — treat as interactive only; don't automate document downloads
  beyond a few dozen per hour
- ArcGIS feature layers — standard ESRI throttling applies; respect the
  `maxRecordCount` from the service metadata
- If you need batch well-level data, start with the bulk production CSVs,
  join against field polygons, and only drop to COGIS for records not
  resolvable from bulk files
