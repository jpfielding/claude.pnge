# KGS Well Logs — API Reference

Reference for the Kansas Geological Survey (KGS) ORDS well services API,
LAS 2.0 file format specification, and comprehensive log curve mnemonic
dictionary.

---

## KGS ORDS Well Services API

**Base URL:** `https://chasm.kgs.ku.edu/ords/rgws.kgs_well_srvc.`

All endpoints accept `type=json` to return JSON. Default without this
parameter may return XML or HTML.

### Endpoint Inventory

| Endpoint Suffix | Parameters | Description |
|-----------------|------------|-------------|
| `get_county_wells_sp` | `county_cd` | List wells in a county |
| `get_well_log_sp` | `kid` | Get log runs for a KGS well ID |
| `get_well_by_api_sp` | `api_number` | Find well by 14-digit API number |
| `get_log_details_sp` | `log_id` | Detailed info for one log run |
| `get_county_list_sp` | none | List all KGS counties with FIPS codes |
| `get_well_info_sp` | `kid` | Full well header information |
| `get_log_header_sp` | `log_id` | LAS header metadata without data |

**Note:** The `get_county_list_sp` and some other endpoints may return 404
on older versions of the ORDS deployment. Fall back to known county FIPS
codes from the reference table below.

---

### Kansas County FIPS Codes (All 105 Counties)

```
001 Allen       003 Anderson    005 Atchison    007 Barber
009 Barton      011 Bourbon     013 Brown       015 Butler
017 Chase       019 Chautauqua  021 Cherokee    023 Cheyenne
025 Clark       027 Clay        029 Cloud       031 Coffey
033 Comanche    035 Cowley      037 Crawford    039 Decatur
041 Dickinson   043 Doniphan    045 Douglas     047 Elk
049 Ellis       051 Ellsworth   053 Finney      055 Ford
057 Franklin    059 Geary       061 Gove        063 Graham
065 Grant       067 Gray        069 Greeley     071 Greenwood
073 Hamilton    075 Harper      077 Harvey      079 Haskell
081 Hodgeman    083 Jackson     085 Jefferson   087 Jewell
089 Johnson     091 Kearny      093 Kingman     095 Kiowa
097 Labette     099 Lane        101 Leavenworth 103 Lincoln
105 Linn        107 Logan       109 Lyon        111 McPherson
113 Marion      115 Marshall    117 Meade       119 Miami
121 Mitchell    123 Montgomery  125 Morris      127 Morton
129 Nemaha      131 Neosho      133 Ness        135 Norton
137 Osage       139 Osborne     141 Ottawa      143 Pawnee
145 Phillips    147 Pottawatomie 149 Pratt      151 Rawlins
153 Reno        155 Republic    157 Rice        159 Riley
161 Rooks       163 Rush        165 Russell     167 Saline
169 Scott       171 Sedgwick    173 Seward      175 Shawnee
177 Sheridan    179 Sherman     181 Smith       183 Stafford
185 Stanton     187 Stevens     189 Sumner      191 Thomas
193 Trego       195 Wabaunsee   197 Wallace     199 Washington
201 Wichita     203 Wilson      205 Woodson     207 Wyandotte
```

---

### API Number Format

The 14-digit API (American Petroleum Institute) well number is the universal
unique identifier for U.S. wells:

```
SS-CCC-NNNNN-0000
│   │   │      └── Sidetrack code (4 digits, usually 0000)
│   │   └───────── Unique well number within county (5 digits)
│   └───────────── County FIPS code (3 digits)
└───────────────── State FIPS code (2 digits)

Kansas state FIPS = 20
Example: 20-167-12340-0000 → written as 2016712340000
```

Common state FIPS codes for KGS neighboring states:
- Kansas: 20
- Oklahoma: 40
- Colorado: 08
- Nebraska: 31
- Missouri: 29

---

## LAS 2.0 File Format Reference

### Section Markers

| Marker | Section | Required | Description |
|--------|---------|----------|-------------|
| `~V` or `~VERSION` | Version | Yes | LAS version and wrap mode |
| `~W` or `~WELL` | Well | Yes | Well identification info |
| `~C` or `~CURVE` | Curve | Yes | Curve mnemonic definitions |
| `~P` or `~PARAMETER` | Parameter | Optional | Tool/measurement parameters |
| `~O` or `~OTHER` | Other | Optional | Free-form comments |
| `~A` or `~DATA` | ASCII data | Yes | Numeric log data |

### Version Section Fields

| Mnemonic | Description | LAS 2.0 values |
|----------|-------------|----------------|
| `VERS` | LAS version | `2.0` |
| `WRAP` | Wrap mode | `NO` = one depth per line; `YES` = wrapped |

### Well Section Fields

| Mnemonic | Description | Notes |
|----------|-------------|-------|
| `STRT` | Start depth | Units in .FT or .M |
| `STOP` | Stop depth | Must match data |
| `STEP` | Depth increment | Negative = decreasing depth |
| `NULL` | Null value sentinel | Standard = -999.25 |
| `COMP` | Company/operator | |
| `WELL` | Well name | |
| `FLD` | Field name | |
| `LOC` | Location description | |
| `PROV` or `STAT` | Province or state | |
| `CTRY` | Country | |
| `SRVC` | Service company | Log vendor |
| `DATE` | Log date | |
| `UWI` or `API` | Unique well ID or API number | |
| `LAT` | Latitude (decimal degrees) | |
| `LONG` | Longitude (decimal degrees) | |
| `GDAT` | Geodetic datum | e.g. NAD83 |
| `KB` | Kelly bushing elevation (ft) | |
| `GL` | Ground level elevation (ft) | |
| `TD` | Total depth (ft) | |

### Curve Section Format

Each line in `~CURVE`:
```
 MNEMONIC.UNIT  VALUE : DESCRIPTION
```

Example:
```
~CURVE INFORMATION
 DEPT.FT           :  1  DEPTH
 GR  .GAPI         :  2  GAMMA RAY
 ILD .OHMM         :  3  DEEP INDUCTION RESISTIVITY
```

### Data Section

Space-delimited columns in the order defined by `~CURVE`. One row per depth step.
```
~DATA
 1000.0  45.2  18.4  0.215  2.38
 1000.5  47.1  17.9  0.218  2.36
 1001.0  -999.25  18.1  0.221  2.35   <- null GR value
```

---

## Comprehensive Log Curve Mnemonic Dictionary

### Depth and Caliper

| Mnemonic | Aliases | Unit | Description |
|----------|---------|------|-------------|
| DEPT | DEPTH, MD | FT or M | Measured depth |
| CALI | CALS, CAL | IN | Single-arm caliper |
| C1, C2 | CALI1/2 | IN | Multi-arm caliper arms |

### Gamma Ray and Natural Radioactivity

| Mnemonic | Aliases | Unit | Description |
|----------|---------|------|-------------|
| GR | GRN, GRD, GRTO | GAPI | Total gamma ray |
| SGR | — | GAPI | Spectral gamma ray (total) |
| CGR | — | GAPI | Computed gamma ray (U removed) |
| POTA | K | % | Potassium from spectral GR |
| THOR | TH | PPM | Thorium from spectral GR |
| URAN | U | PPM | Uranium from spectral GR |
| SP | SPS | MV | Spontaneous potential |

**GR interpretation guide:**
- Clean sand/carbonate: < 30 GAPI
- Shaly sand: 30–75 GAPI
- Pure shale: > 90 GAPI (varies by basin)

### Resistivity Logs

| Mnemonic | Aliases | Unit | Tool Type | Investigation Depth |
|----------|---------|------|-----------|---------------------|
| RT | RESD, RD, ILD, HDRS | OHMM | Induction deep | Deep (uninvaded) |
| RMED | ILM, RM, HMRS | OHMM | Induction medium | Medium |
| RSHAL | ILS, RS, SFLU, MSFL | OHMM | Laterolog shallow / MSFL | Flushed zone |
| RXLD | LLD, RD | OHMM | Dual Laterolog deep | Deep (salt water) |
| RXLS | LLS, RS | OHMM | Dual Laterolog shallow | Shallow |
| RILD | ILD | OHMM | Induction deep (older) | Deep |
| RILM | ILM | OHMM | Induction medium (older) | Medium |
| RXO | RSXO, RFOC, MSFL | OHMM | Microresistivity | Flushed zone |
| AT10 | — | OHMM | Array induction 10 in | Shallow |
| AT20 | — | OHMM | Array induction 20 in | Medium-shallow |
| AT60 | — | OHMM | Array induction 60 in | Medium-deep |
| AT90 | — | OHMM | Array induction 90 in | Deep |

### Density Logs

| Mnemonic | Aliases | Unit | Description |
|----------|---------|------|-------------|
| RHOB | DEN, RHOZ | G/CC | Bulk density |
| DRHO | DDRHO, ZCOR | G/CC | Density correction |
| DPHI | — | V/V | Density-derived porosity |
| PE | PEF, PEL | B/E | Photoelectric factor |

**Matrix density reference:**
| Lithology | RHOma (g/cc) |
|-----------|-------------|
| Sandstone | 2.65 |
| Limestone | 2.71 |
| Dolomite | 2.87 |
| Anhydrite | 2.98 |
| Salt | 2.04 |
| Shale | 2.30–2.65 |

### Neutron Logs

| Mnemonic | Aliases | Unit | Description |
|----------|---------|------|-------------|
| NPHI | NEU, CN, TNPH | V/V or % | Thermal neutron porosity (limestone units) |
| TNPH | — | V/V | Compensated neutron thermal (Baker Atlas) |
| CNPH | — | V/V | CNT-G neutron porosity |
| DPHI | — | V/V | Density porosity (listed here for crossplot use) |

**Limestone matrix reference:** NPHI logged in limestone matrix units.
For sandstone correction: PHIss = NPHI - 0.04 (approx)

### Sonic / Acoustic Logs

| Mnemonic | Aliases | Unit | Description |
|----------|---------|------|-------------|
| DT | AC, DTC, DTCO | US/FT | Compressional sonic transit time |
| DTS | DTSH, DTSM | US/FT | Shear sonic transit time |
| DTL | — | US/FT | Long-spaced sonic |
| VPVS | — | dimensionless | Vp/Vs ratio |
| PHIN | — | V/V | Sonic-derived porosity |

**Wyllie time-average porosity:**
```
PHI_sonic = (DT - DTma) / (DTfl - DTma)
DTma: sandstone=55.5, limestone=47.5, dolomite=43.5 (us/ft)
DTfl: 189 us/ft (freshwater), 185 us/ft (saltwater)
```

### Nuclear Magnetic Resonance (NMR) — Modern Logs

| Mnemonic | Unit | Description |
|----------|------|-------------|
| CMRP | V/V | CMR total porosity |
| CMFF | V/V | CMR free fluid porosity |
| BFV | V/V | Bound fluid volume |
| T2LM | MS | Log-mean T2 relaxation time |

### Formation Evaluation Computed Curves

| Mnemonic | Unit | Description |
|----------|------|-------------|
| VSH | V/V or % | Shale volume (computed) |
| PHIE | V/V | Effective porosity |
| PHIT | V/V | Total porosity |
| SW | V/V or % | Water saturation (Archie) |
| SXO | V/V | Flushed-zone water saturation |
| BVW | V/V | Bulk volume water = PHIE × SW |
| PERM | MD | Permeability estimate |

---

## Go Example: Parse LAS File

```go
package main

import (
    "bufio"
    "fmt"
    "os"
    "strconv"
    "strings"
)

type LASHeader struct {
    Well     string
    API      string
    Lat      float64
    Lon      float64
    StartFt  float64
    StopFt   float64
    StepFt   float64
    NullVal  float64
    Curves   []LASCurve
}

type LASCurve struct {
    Mnemonic string
    Unit     string
    Desc     string
    Index    int
}

type LASFile struct {
    Header LASHeader
    Data   [][]float64
}

func parseLAS(filename string) (*LASFile, error) {
    f, err := os.Open(filename)
    if err != nil {
        return nil, err
    }
    defer f.Close()

    las := &LASFile{}
    las.Header.NullVal = -999.25 // default

    scanner := bufio.NewScanner(f)
    section := ""
    curveIdx := 0

    for scanner.Scan() {
        line := strings.TrimSpace(scanner.Text())

        // Skip comments
        if strings.HasPrefix(line, "#") || line == "" {
            continue
        }

        // Section markers
        if strings.HasPrefix(line, "~") {
            upper := strings.ToUpper(line)
            switch {
            case strings.HasPrefix(upper, "~V"):
                section = "version"
            case strings.HasPrefix(upper, "~W"):
                section = "well"
            case strings.HasPrefix(upper, "~C"):
                section = "curve"
            case strings.HasPrefix(upper, "~A"):
                section = "data"
            default:
                section = "other"
            }
            continue
        }

        switch section {
        case "well":
            mnem, val := parseLASLine(line)
            switch mnem {
            case "WELL":
                las.Header.Well = val
            case "API", "UWI":
                las.Header.API = val
            case "STRT":
                las.Header.StartFt, _ = strconv.ParseFloat(val, 64)
            case "STOP":
                las.Header.StopFt, _ = strconv.ParseFloat(val, 64)
            case "STEP":
                las.Header.StepFt, _ = strconv.ParseFloat(val, 64)
            case "NULL":
                las.Header.NullVal, _ = strconv.ParseFloat(val, 64)
            case "LAT":
                las.Header.Lat, _ = strconv.ParseFloat(val, 64)
            case "LONG":
                las.Header.Lon, _ = strconv.ParseFloat(val, 64)
            }

        case "curve":
            mnem, desc := parseLASLine(line)
            if mnem != "" {
                parts := strings.SplitN(mnem, ".", 2)
                curveMnem := parts[0]
                curveUnit := ""
                if len(parts) > 1 {
                    curveUnit = parts[1]
                }
                las.Header.Curves = append(las.Header.Curves, LASCurve{
                    Mnemonic: curveMnem,
                    Unit:     curveUnit,
                    Desc:     desc,
                    Index:    curveIdx,
                })
                curveIdx++
            }

        case "data":
            fields := strings.Fields(line)
            row := make([]float64, len(fields))
            for i, f := range fields {
                v, _ := strconv.ParseFloat(f, 64)
                row[i] = v
            }
            if len(row) > 0 {
                las.Data = append(las.Data, row)
            }
        }
    }

    return las, scanner.Err()
}

// parseLASLine parses "MNEM.UNIT  VALUE : DESCRIPTION"
func parseLASLine(line string) (mnemUnit, valueOrDesc string) {
    // Split on first colon
    parts := strings.SplitN(line, ":", 2)
    desc := ""
    if len(parts) > 1 {
        desc = strings.TrimSpace(parts[1])
    }
    // Left of colon: "MNEM.UNIT  VALUE"
    left := strings.TrimSpace(parts[0])
    // Mnem.Unit is before first whitespace run
    tokens := strings.Fields(left)
    if len(tokens) == 0 {
        return "", ""
    }
    return tokens[0], desc
}

// CurveStats returns min/max/null count for a named curve
func (las *LASFile) CurveStats(mnemonic string) (min, max float64, nullCount int) {
    idx := -1
    for _, c := range las.Header.Curves {
        if strings.EqualFold(c.Mnemonic, mnemonic) {
            idx = c.Index
            break
        }
    }
    if idx < 0 {
        return 0, 0, -1
    }

    null := las.Header.NullVal
    min, max = 1e18, -1e18
    for _, row := range las.Data {
        if idx >= len(row) {
            continue
        }
        v := row[idx]
        if v == null {
            nullCount++
            continue
        }
        if v < min {
            min = v
        }
        if v > max {
            max = v
        }
    }
    return min, max, nullCount
}

func main() {
    if len(os.Args) < 2 {
        fmt.Fprintln(os.Stderr, "Usage: las_parse <file.las>")
        os.Exit(1)
    }
    las, err := parseLAS(os.Args[1])
    if err != nil {
        fmt.Fprintf(os.Stderr, "error: %v\n", err)
        os.Exit(1)
    }

    fmt.Printf("Well:  %s\n", las.Header.Well)
    fmt.Printf("API:   %s\n", las.Header.API)
    fmt.Printf("Depth: %.1f – %.1f ft (step %.3f ft)\n",
        las.Header.StartFt, las.Header.StopFt, las.Header.StepFt)
    fmt.Printf("Rows:  %d\n\n", len(las.Data))

    fmt.Printf("%-8s %-8s %12s %12s %8s\n", "Curve", "Unit", "Min", "Max", "Nulls")
    fmt.Println(strings.Repeat("-", 56))
    for _, c := range las.Header.Curves {
        if strings.EqualFold(c.Mnemonic, "DEPT") || strings.EqualFold(c.Mnemonic, "DEPTH") {
            continue
        }
        min, max, nulls := las.CurveStats(c.Mnemonic)
        if nulls < 0 {
            continue
        }
        fmt.Printf("%-8s %-8s %12.3f %12.3f %8d\n",
            c.Mnemonic, c.Unit, min, max, nulls)
    }
}
```

---

## Formation Depth Reference for Kansas

Common pay zones encountered in KGS wells:

| Formation | Age | Avg Depth (ft) | Basin Area | Key Log Character |
|-----------|-----|----------------|------------|-------------------|
| Morrow Sandstone | Pennsylvanian | 4,000–7,500 | Anadarko | Clean GR <30, high Res |
| Lansing-Kansas City | Pennsylvanian | 2,500–5,000 | Central KS | Carbonate: low GR, high RHOB |
| Mississippian Lime | Mississippian | 3,500–7,000 | Central KS / Anadarko | Cherty: erratic NPHI |
| Hunton Group | Silurian/Devonian | 5,500–8,000 | Anadarko | Carbonate: low NPHI |
| Viola Limestone | Ordovician | 5,500–8,500 | Anadarko | Dense: RHOB > 2.7 |
| Simpson Group | Ordovician | 7,000–9,000 | Deep Anadarko | Sandstone |
| Arbuckle | Cambro-Ordovician | 9,000–12,000 | Anadarko | Dolomite: RHOB ~2.87 |
| Hugoton (Chase Group) | Permian | 2,000–3,000 | Hugoton Embayment | Gas: NPHI-RHOB separation |

---

## Useful External Links

| Resource | URL |
|----------|-----|
| KGS Well Log Browser | https://www.kgs.ku.edu/Magellan/well_logs/index.html |
| KGS Oil & Gas Portal | https://www.kgs.ku.edu/Magellan/wwc5/ |
| KGS Stratigraphic Database | https://www.kgs.ku.edu/PRS/Strat/ |
| CWLS LAS Standard | https://www.cwls.org/products/ |
| LAS 2.0 Specification PDF | https://www.cwls.org/wp-content/uploads/2014/09/LAS_20_Update_Jan2014.pdf |
| USGS NDWLR (national) | https://certmapper.cr.usgs.gov/data/apps/ndwlr/ |
| Enverus (commercial) | https://www.enverus.com/ |
| IHS Markit / S&P (commercial) | https://ihsmarkit.com/products/oil-gas.html |
