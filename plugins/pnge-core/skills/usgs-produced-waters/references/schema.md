# USGS National Produced Waters Geochemical Database v3.0 — Column Schema

Source: `USGS_NPWGDv3_data_dictionary.xlsx` from ScienceBase item `64fa1e71d34ed30c2054ea11`.

All chemistry values are in **mg/L** (v3.0 converted all ppm to mg/L using specific gravity).

---

## Identification

| Column     | Type | Description |
|------------|------|-------------|
| IDUSGS     | ID   | Unique ID in the database (persistent across v2.3 and v3.0) |
| IDORIG     | ID   | ID from the original dataset or publication |
| IDDB       | ID   | Name of the input dataset or database source |

## Well Information

| Column     | Type      | Description |
|------------|-----------|-------------|
| PLAYTYPE   | Category  | Play/reservoir type: Shale, Coal, Sedimentary, Geothermal, Injection (preferred in v3.0) |
| WELLTYPE   | Category  | Legacy well type: Conventional Hydrocarbon, Shale Gas, Tight Oil, Tight Gas, Coal Bed Methane, Geothermal, Groundwater (retained from v2.3) |
| WELLNAME   | Text      | Well name |
| API        | Text      | API well number (14 digits) |
| OPERATOR   | Text      | Well operator |
| WELLCODE   | Text      | Well code |
| PERMIT     | Text      | Well permit holder |
| DATECOMP   | Date      | Date of well completion (YYYY-MM-DD) |
| ELEVATION  | Numeric   | Elevation of well (ft) |
| DEPTHUPPER | Numeric   | Upper perforation depth of sampled interval (ft) |
| DEPTHLOWER | Numeric   | Lower perforation depth of sampled interval (ft) |
| NWIS       | Text      | USGS National Water Information System Site Number |

## Location

| Column     | Type    | Description |
|------------|---------|-------------|
| LATITUDE   | Numeric | Latitude (decimal degrees); may be approximate -- see COORDAPX |
| LONGITUDE  | Numeric | Longitude (decimal degrees); may be approximate -- see COORDAPX |
| COORDAPX   | Text    | Description if lat/lon are approximate |
| COORDNEW   | Text    | How location was updated from v2.3 (orig, new latlon, new county centroid, etc.) |
| STATE      | Text    | U.S. state name, Canadian province, or "Offshore" |
| STATEFIP   | Numeric | State FIPS code |
| COUNTY     | Text    | County name (from GIS analysis, modified for consistency) |
| COUNTYFIP  | Numeric | County FIPS code |
| FIPCODE    | Numeric | Combined 5-digit FIPS code (state + county) |
| COUNTYORIG | Text    | Original county name from source dataset |
| FIELD      | Text    | Oil/gas field name as reported |
| FIELDCODE  | Text    | Field code as reported |
| PROVINCE   | Text    | USGS 1995 National Oil and Gas Assessment Province |
| REGION     | Text    | USGS 1995 National Oil and Gas Assessment Region |
| BASIN      | Text    | Geologic basin (cleaned and standardized) |
| TOWNRANGE  | Text    | Township, Range, Section, Quarter |
| LOC        | Text    | Other location information |

## Geology

| Column     | Type    | Description |
|------------|---------|-------------|
| GROUP      | Text    | Geologic group name |
| FORMATION  | Text    | Geologic formation name as reported (partially standardized) |
| FORMSIMPLE | Text    | Simplified/standardized formation name (new in v3.0) |
| MEMBER     | Text    | Geologic member name |
| ERA        | Text    | Geologic era (cleaned in v3.0) |
| PERIOD     | Text    | Geologic period (cleaned in v3.0) |
| EPOCH      | Text    | Geologic epoch (cleaned in v3.0) |
| LITHOLOGY  | Text    | Lithology description |
| POROSITY   | Numeric | Porosity (%) |

## Time / Sampling

| Column     | Type    | Description |
|------------|---------|-------------|
| TIMESERIES | Numeric | Order of time-series data |
| DAY        | Numeric | Sample day of time-series data |
| DATESAMPLE | Date    | Date of sample collection (YYYY-MM-DD) |
| DATEANALYS | Date    | Date of analysis (YYYY-MM-DD) |
| METHOD     | Text    | Sample method |
| LAB        | Text    | Laboratory that performed analysis |

## Physical Parameters

| Column    | Type    | Unit    | Description |
|-----------|---------|---------|-------------|
| TEMP_R    | Numeric | deg F   | Temperature, reported |
| TEMP      | Numeric | deg F   | Combined temperature (TEMP_R, PHT, CONDT, or RESIST) |
| PRESSURE  | Numeric | psi     | Formation pressure |
| SG        | Numeric | --      | Specific gravity (reported or calculated) |
| SPGRAV    | Numeric | --      | Specific gravity, reported only |
| SPGRAVT   | Numeric | deg F   | Temperature of SG measurement |
| RESIS     | Numeric | Ohm-m   | Resistivity |
| RESIST    | Numeric | deg F   | Temperature of resistivity measurement |
| PH        | Numeric | --      | pH |
| PHT       | Numeric | deg F   | Temperature of pH measurement |
| EHORP     | Numeric | mV      | Eh / Oxidation-Reduction Potential |
| COND      | Numeric | uS/cm   | Conductivity |
| CONDT     | Numeric | deg F   | Temperature of conductivity measurement |
| TURBIDITY | Numeric | --      | Turbidity |
| HEM       | Numeric | --      | Oil and Grease (Hexane Extractable Material) |
| MBAS      | Numeric | --      | Surfactants and Detergents |

## Total Dissolved Solids

| Column   | Type    | Unit | Description |
|----------|---------|------|-------------|
| TDS      | Numeric | mg/L | Best available TDS: measured (1), reported calculated (2), or ion-sum calculated (3) |
| TDSLAB   | Numeric | mg/L | TDS measured in lab, as reported |
| TDSCALC  | Numeric | mg/L | TDS calculated, as reported |
| TDSDESC  | Text    | --   | Method: "reported measured", "reported calculated", or "calculated" |
| TSS      | Numeric | mg/L | Total Suspended Solids |

## Major Ions (mg/L)

| Column | Element/Ion   | Notes |
|--------|---------------|-------|
| Na     | Sodium        | |
| K      | Potassium     | |
| KNa    | Potassium + Sodium | Combined value when not separately reported |
| Ca     | Calcium       | |
| Mg     | Magnesium     | Key for Mg recovery assessment |
| Cl     | Chloride      | |
| SO4    | Sulfate       | |
| HCO3   | Bicarbonate   | |
| CO3    | Carbonate     | |
| Br     | Bromide       | |

## Critical Minerals and Trace Elements (mg/L)

| Column | Element    | Notes |
|--------|------------|-------|
| Li     | Lithium    | Key target for DLE (Direct Lithium Extraction) |
| Ba     | Barium     | |
| Sr     | Strontium  | |
| B      | Boron      | |
| BO3    | Borate     | |
| FeTot  | Iron total | |
| FeII   | Iron 2+    | |
| FeIII  | Iron 3+    | |
| Mn     | Manganese  | |
| Si     | Silica     | |
| I      | Iodine     | |
| F      | Fluoride   | |
| Rb     | Rubidium   | |
| Cs     | Cesium     | |

## Other Trace Elements (mg/L)

| Column | Element     |
|--------|-------------|
| Ag     | Silver      |
| Al     | Aluminum    |
| As     | Arsenic     |
| Au     | Gold        |
| Be     | Beryllium   |
| Bi     | Bismuth     |
| Cd     | Cadmium     |
| Co     | Cobalt      |
| Cr     | Chromium    |
| Cu     | Copper      |
| Ga     | Gallium     |
| Ge     | Germanium   |
| Hf     | Hafnium     |
| Hg     | Mercury     |
| Mo     | Molybdenum  |
| Ni     | Nickel      |
| Pb     | Lead        |
| Rh     | Rhodium     |
| Sb     | Antimony    |
| Sc     | Scandium    |
| Se     | Selenium    |
| Sn     | Tin         |
| Th     | Thorium     |
| Ti     | Titanium    |
| Tl     | Thallium    |
| U      | Uranium     |
| V      | Vanadium    |
| W      | Tungsten    |
| Y      | Yttrium     |
| Zn     | Zinc        |
| Zr     | Zirconium   |

## Rare Earth Elements (mg/L)

| Column | Element         |
|--------|-----------------|
| La     | Lanthanum       |
| Ce     | Cerium          |
| Pr     | Praseodymium    |
| Nd     | Neodymium       |
| Sm     | Samarium        |
| Eu     | Europium        |
| Gd     | Gadolinium      |
| Tb     | Terbium         |
| Dy     | Dysprosium      |
| Ho     | Holmium         |
| Er     | Erbium          |
| Tm     | Thulium         |
| Yb     | Ytterbium       |
| Lu     | Lutetium        |

## Nitrogen Species (mg/L)

| Column | Description          |
|--------|----------------------|
| N      | Nitrogen, total      |
| NO2    | Nitrite              |
| NO3    | Nitrate              |
| NO3NO2 | Nitrate + Nitrite   |
| NH4    | Ammonium             |
| TKN    | Kjeldahl Nitrogen    |

## Phosphorus (mg/L)

| Column | Description |
|--------|-------------|
| P      | Phosphorus  |
| PO4    | Phosphate   |

## Sulfur Species (mg/L)

| Column | Description |
|--------|-------------|
| S      | Sulfide     |
| SO3    | Sulfite     |
| SO4    | Sulfate     |
| HS     | Bisulfide   |
| FeS    | Iron Sulfide|

## Iron + Aluminum Combined

| Column  | Unit | Description |
|---------|------|-------------|
| FeAl    | mg/L | Iron + Aluminum, reported as elements |
| FeAl2O3 | mg/L | Iron + Aluminum, reported as oxides |

## Alkalinity / Acidity / Carbon

| Column    | Unit | Description |
|-----------|------|-------------|
| ALKALINITY| mg/L | Alkalinity as HCO3 |
| ACIDITY   | mg/L | Acidity as CaCO3 |
| DIC       | mg/L | Dissolved Inorganic Carbon |
| OH        | mg/L | Hydroxide |

## Organic Chemistry (mg/L)

| Column     | Description |
|------------|-------------|
| DOC        | Dissolved Organic Carbon |
| TOC        | Total Organic Carbon |
| CYANIDE    | Cyanide |
| BOD        | Biochemical Oxygen Demand |
| COD        | Chemical Oxygen Demand |
| BENZENE    | Benzene (VOC) |
| ETHYLBENZ  | Ethylbenzene (VOC) |
| NAPHTH     | Naphthalene (aromatic) |
| PERC       | Tetrachloroethylene (VOC) |
| TOLUENE    | Toluene (VOC) |
| XYLENE     | Xylene (VOC) |
| PHENOLS    | Phenols |

## Organic Acid Anions (mg/L)

| Column     | Description |
|------------|-------------|
| ACETATE    | Acetate     |
| BUTYRATE   | Butyrate    |
| FORMATE    | Formate     |
| LACTATE    | Lactate     |
| PROPIONATE | Propionate  |
| PYRUVATE   | Pyruvate    |
| VALERATE   | Valerate    |
| ORGACIDS   | Total Organic Acids |

## Dissolved Gases (mg/L)

| Column | Gas               |
|--------|-------------------|
| Ar     | Argon             |
| CH4    | Methane           |
| C2H6   | Ethane            |
| CO2    | Carbon Dioxide    |
| H2     | Hydrogen          |
| H2S    | Hydrogen Sulfide  |
| He     | Helium            |
| N2     | Nitrogen          |
| NH3    | Ammonia           |
| O2     | Oxygen            |

## Isotopes

| Column    | Unit        | Description |
|-----------|-------------|-------------|
| dD        | per mil     | delta-2H (deuterium) |
| H3        | TU          | Tritium |
| d7Li      | per mil     | delta-7Li |
| d11B      | per mil     | delta-11B |
| d13C      | per mil     | delta-13C |
| C14       | pCi/L       | Carbon-14 |
| d18O      | per mil     | delta-18O |
| d34S      | per mil     | delta-34S |
| d37Cl     | per mil     | delta-37Cl |
| K40       | pCi/L       | Potassium-40 |
| d81Br     | --          | delta-81Br |
| Sr87Sr86  | ratio       | 87Sr/86Sr |
| I129      | ppq         | 129I/I ratio |
| Rn222     | pCi/L       | Radon-222 |
| Ra226     | pCi/L       | Radium-226 |
| Ra228     | pCi/L       | Radium-228 |
| ALPHA     | pCi/L       | Alpha particles |
| BETA      | pCi/L       | Beta particles |

## Microbial Data

| Column   | Description |
|----------|-------------|
| MICROBES | Link to associated genomic/microbial datasets (new in v3.0) |

## Data Quality

| Column    | Unit | Description |
|-----------|------|-------------|
| CHARGEBAL | %    | Charge balance of major ions |

## Metadata / Provenance

| Column    | Description |
|-----------|-------------|
| UNITSORIG | Original reported units (mg/L or ppm) |
| REMARKS   | Remarks or comments |
| SOURCE    | Source database or compilation paper |
| REFERENCE | First-level source publication or dataset |
