---
name: kggs-well-logs
description: >
  Search and retrieve digitized well log data from state geological survey
  repositories, primarily the Kansas Geological Survey (KGS) public database
  and the Digital Well Log Repository (DWLR). Use this skill when the user asks
  about well logs, wireline log data, gamma ray curves, resistivity logs,
  neutron-density crossplots, formation evaluation from logs, log-derived
  porosity or permeability, or needs to access subsurface petrophysical data
  from public repositories. Trigger for phrases like "well logs for Kansas",
  "gamma ray log data", "digital wireline logs", "formation tops from well
  logs", "log-derived porosity", "KGS well data", "petrophysical data from
  public wells", "LAS file download", "resistivity log for formation", or any
  request for digitized borehole log data from public geological survey
  databases. Covers LAS-format digital logs with GR, ILD, NPHI, RHOB, and
  other curves. Produces log curve summaries and download links.
---

# KGS Well Logs Skill

Queries the Kansas Geological Survey (KGS) public well database REST API to
locate digitized wireline well logs, retrieve LAS file metadata, and summarize
log curve availability for formation evaluation. Also documents access patterns
for other state geological survey log repositories.

---

## No Credential Required

The KGS well database REST API is fully public. No API key needed.

---

## API Structure

### Primary: KGS ORDS Well Services API

**Base URL:** `https://chasm.kgs.ku.edu/ords/rgws.kgs_well_srvc.`

The KGS exposes well data through Oracle REST Data Services (ORDS). Endpoints
return JSON and follow a consistent pattern.

#### Get Wells by County

```bash
# county_cd is the 3-digit FIPS code for Kansas counties
# Example: 035 = Cowley County, 177 = Shawnee County (Topeka area)
curl -s "https://chasm.kgs.ku.edu/ords/rgws.kgs_well_srvc.get_county_wells_sp?county_cd=035&type=json"
```

Response fields:
| Field | Description |
|-------|-------------|
| `kid` | KGS internal well ID (use for follow-up queries) |
| `api_number` | 14-digit API well number |
| `well_name` | Well name as reported |
| `operator` | Current operator |
| `county_name` | County name |
| `latitude` | Decimal degrees (NAD83) |
| `longitude` | Decimal degrees (NAD83) |
| `kb_elev` | Kelly bushing elevation (ft) |
| `td` | Total depth (ft) |
| `spud_date` | Spud date |

#### Get Log Availability for a Well

```bash
# kid = KGS well ID from county wells query
curl -s "https://chasm.kgs.ku.edu/ords/rgws.kgs_well_srvc.get_well_log_sp?kid=1050066180&type=json"
```

Response includes log runs with available curve mnemonics, depth ranges,
and LAS file download URLs.

#### Search Wells by API Number

```bash
# Full 14-digit API number
curl -s "https://chasm.kgs.ku.edu/ords/rgws.kgs_well_srvc.get_well_by_api_sp?api_number=15035012340000&type=json"
```

#### Get Well Log Details by Log ID

```bash
curl -s "https://chasm.kgs.ku.edu/ords/rgws.kgs_well_srvc.get_log_details_sp?log_id=LOG_ID&type=json"
```

---

### LAS File Download

LAS files (Log ASCII Standard) are the standard digital format for wireline
log data. The KGS serves LAS 2.0 files directly via HTTP.

```bash
# Download LAS file (URL from get_well_log_sp response)
curl -s "https://www.kgs.ku.edu/WellLogs/logs/LAS/NNNNNN.las" -o well.las

# View first 50 lines to inspect header
head -50 well.las
```

LAS 2.0 file structure:
```
~VERSION INFORMATION
 VERS.   2.0    : CWLS LOG ASCII STANDARD - VERSION 2.0
 WRAP.   NO     : ONE LINE PER DEPTH STEP
~WELL INFORMATION
 STRT.FT    1000.0000 : START DEPTH
 STOP.FT    5432.0000 : STOP DEPTH
 STEP.FT       0.5000 : STEP
 NULL.         -999.25: NULL VALUE
 WELL.   SMITH #1     : WELL NAME
 API .   15035012340000 : API NUMBER
 LAT .   37.8234      : LATITUDE
 LONG.  -98.1123      : LONGITUDE
~CURVE INFORMATION
 DEPT.FT           : 1  DEPTH
 GR  .GAPI         : 2  GAMMA RAY
 ILD .OHMM         : 3  DEEP INDUCTION RESISTIVITY
 NPHI.V/V          : 4  NEUTRON POROSITY
 RHOB.G/C3         : 5  BULK DENSITY
~DATA
 1000.0000  42.3  18.4  0.21  2.38
 1000.5000  45.1  17.9  0.22  2.36
```

**Null value:** `-999.25` is the universal LAS null sentinel. Exclude from
statistics and analysis.

---

### KGS Web Interface (Non-API Reference)

For users who prefer a browser workflow:
- Well log search: `https://www.kgs.ku.edu/Magellan/well_logs/index.html`
- Individual well lookup by API: `https://www.kgs.ku.edu/Magellan/Cgi-bin/servedata.cgi`
- Stratigraphic picks DB: `https://www.kgs.ku.edu/PRS/Strat/`

---

### Kansas County FIPS Codes (Common Counties)

For petroleum-relevant counties in Kansas:

| County | FIPS | Key Plays |
|--------|------|-----------|
| Butler | 015 | Producing Hugoton, Central KS Uplift |
| Ellis | 051 | Smoky Hills, Niobrara |
| Finney | 057 | Hugoton gas area |
| Grant | 067 | Hugoton |
| Haskell | 081 | Hugoton |
| Reno | 155 | Central KS |
| Rush | 163 | Central KS Uplift |
| Russell | 167 | Central KS Uplift |
| Seward | 175 | Hugoton |

Use `curl -s "https://chasm.kgs.ku.edu/ords/rgws.kgs_well_srvc.get_county_list_sp?type=json"` to get the full county list if the endpoint is available.

---

## Workflow

### Step 1 — Resolve Intent

- User provides county name → look up FIPS code → use `get_county_wells_sp`
- User provides API number → use `get_well_by_api_sp`
- User provides KGS well ID → go directly to `get_well_log_sp`
- User wants logs for a formation → search by county, then filter by TD range

### Step 2 — Find the Well

```bash
# Example: find wells in Russell County (FIPS 167)
curl -s "https://chasm.kgs.ku.edu/ords/rgws.kgs_well_srvc.get_county_wells_sp?county_cd=167&type=json" \
  | jq '.items[] | {kid: .kid, api: .api_number, name: .well_name, td: .td, lat: .latitude, lon: .longitude}'
```

If the county query returns many wells (>100), add filters or ask the user
to specify a smaller area or a well name.

### Step 3 — Check Log Availability

```bash
# For a specific KGS well ID
curl -s "https://chasm.kgs.ku.edu/ords/rgws.kgs_well_srvc.get_well_log_sp?kid=KID_HERE&type=json" \
  | jq '.items[] | {log_id: .log_id, curves: .curves, depth_from: .depth_from, depth_to: .depth_to}'
```

Extract the list of curves available (comma-separated mnemonic string) and
the LAS download URL.

### Step 4 — Download or Describe LAS

If the user wants to analyze curves, download the LAS file and parse the
`~CURVE` section to list available logs, then the `~DATA` section for statistics.

```bash
curl -s "LAS_URL_FROM_RESPONSE" -o /tmp/well.las
# Show curve inventory
awk '/^~C/,/^~/' /tmp/well.las | head -30
```

### Step 5 — Produce Output

Summarize the curve inventory table and provide download link. If the user
wants formation evaluation, use the curve summary to guide interpretation.

---

## Output Format

### Log Availability Query Output

```
## Well Log Summary — [Well Name], [API Number]

**Well Info:**
- Operator: [Operator]
- County: [County], KS
- TD: [depth] ft
- Spud Date: [date]
- Coordinates: [lat], [lon]

### Available Log Runs

| Run | Curves | Top (ft) | Base (ft) | LAS Download |
|-----|--------|----------|-----------|--------------|
| 1   | GR, ILD, NPHI, RHOB, CALI | 500 | 4,200 | [link] |
| 2   | GR, SP, ILD | 200 | 1,100 | [link] |

### Curve Detail (Run 1)

| Mnemonic | Log Type | Unit | Min Value | Max Value | Null Count |
|----------|----------|------|-----------|-----------|------------|
| GR | Gamma Ray | GAPI | 12.3 | 148.7 | 0 |
| ILD | Deep Induction Res | OHMM | 0.8 | 4,250 | 3 |
| NPHI | Neutron Porosity | V/V | 0.03 | 0.42 | 0 |
| RHOB | Bulk Density | G/C3 | 2.10 | 2.71 | 12 |

**Assessment:** Run 1 provides a full suite for formation evaluation including
porosity (NPHI, RHOB) and saturation (ILD). Suitable for neutron-density
crossplot analysis. [n] null values in RHOB suggest minor washout intervals.
```

---

## Common Log Curve Mnemonics

See `references/api_reference.md` for the comprehensive mnemonic table.
Frequently used curves:

| Mnemonic | Full Name | Unit | PE Application |
|----------|-----------|------|----------------|
| GR | Gamma Ray | GAPI | Shale volume, lithology discrimination |
| SP | Spontaneous Potential | MV | Permeability indicator, correlation |
| ILD | Deep Induction Resistivity | OHMM | Fluid saturation (Sw) |
| ILM | Medium Induction Resistivity | OHMM | Invasion profile |
| MSFL | Micro-Spherically Focused Log | OHMM | Flushed zone Rxo |
| NPHI | Neutron Porosity | V/V or % | Porosity, gas identification |
| RHOB | Bulk Density | G/CC | Porosity, lithology |
| DPHI | Density-derived Porosity | V/V | Porosity (from RHOB) |
| DT | Sonic Transit Time | US/FT | Velocity, compaction, Vp |
| CALI | Caliper | IN | Borehole diameter, washout |
| PE | Photoelectric Factor | B/E | Lithology indicator |
| DEPT | Depth track | FT | Depth reference |

---

## Porosity Calculations from Log Data

```
# Density porosity (limestone matrix)
DPHI = (RHOma - RHOB) / (RHOma - RHOfl)
  where RHOma = 2.71 g/cc (limestone), RHOfl = 1.00 g/cc (freshwater)

# Neutron-density crossplot porosity (gas correction)
PHIxp = sqrt((DPHI^2 + NPHI^2) / 2)

# Shale volume from gamma ray (linear)
IGR = (GR - GRmin) / (GRmax - GRmin)
Vsh = IGR  (linear; Clavier: Vsh = 1.7 - sqrt(3.38 - (IGR + 0.7)^2))

# Water saturation (Archie)
Sw = sqrt((a * Rw) / (PHI^m * Rt))
  typical: a=1, m=2, n=2 for clean sandstone
```

---

## Other State Geological Survey Log Repositories

The KGS has the most accessible API. Other states with digital log access:

| State | Agency | Access Method | URL |
|-------|--------|---------------|-----|
| Kansas | KGS | REST API (JSON) | chasm.kgs.ku.edu |
| Oklahoma | OGS | OGS Oil & Gas Portal | https://www.ogs.ou.edu/OGWebNew/ |
| Texas | BEG | Texas Well Finder | https://txwellfinder.beg.utexas.edu/ |
| West Virginia | WVGES | Pipeline data request | https://www.wvgs.wvnet.edu/pipe2/ |
| Colorado | CGS | Well data portal | https://coloradogeologicalsurvey.org/ |
| North Dakota | NDGS | Well completion query | https://www.dmr.nd.gov/oilgas/ |
| Wyoming | WSGS | Oil & Gas portal | https://www.wsgs.wyo.gov/ |

**For WV well logs specifically:** WVGES has digitized logs for some wells
but does not expose a public REST API. Requests go through the Pipeline
web interface at https://www.wvgs.wvnet.edu/pipe2/ or direct contact.

---

## Error Handling

| Condition | Meaning | Action |
|-----------|---------|--------|
| ORDS returns Oracle error ORA-XXXX | Invalid parameter or missing required field | Check county_cd is zero-padded 3 digits; verify kid exists |
| `items` array empty | No wells with logs in that county | Try adjacent counties; not all KGS wells have digitized logs |
| LAS URL returns 404 | File moved or deleted | Check KGS web interface for alternate access |
| LAS data parses as all -999.25 | Depth range mismatch or corrupt run | Check STRT/STOP/STEP in header; verify null value sentinel |
| Mnemonics non-standard (e.g., `RESM`, `GRLOG`) | Older vintage log with aliased names | Cross-reference with standard aliases in references/api_reference.md |
| API number format error | KGS uses 14-digit API; NDIC uses 10-digit | Pad with trailing zeros: 10-digit + "0000" = 14-digit |

---

## Caveats and Data Limitations

- **Coverage:** KGS has digitized roughly 60,000–80,000 logs out of ~100,000+
  drilled Kansas wells. Pre-1970 wells often lack digitized logs; paper logs
  may exist in the KGS core library.
- **Vintage logs:** Pre-1980 logs used older tool generations. Gamma ray
  calibration (GAPI) was not standardized until 1978. Compare same-formation
  values cautiously across vintages.
- **Null value -999.25:** This is the LAS standard null. Always filter before
  statistics. Some older files use 0 or 9999 as nulls — check the `NULL.`
  line in the header.
- **Curve mnemonic aliases:** Resistivity logs especially have dozens of
  mnemonics (ILD, RT, RESD, RDEP, RD, etc.) for the same physical measurement.
  The `references/api_reference.md` lists common aliases.
- **WV log access:** WVGES digitized logs are not on a public API. For Marcellus
  or Utica formation evaluation in WV, check commercial databases (IHS, Enverus)
  or request data directly from WVGES.
