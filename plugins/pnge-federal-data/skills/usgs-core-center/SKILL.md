---
name: usgs-core-center
description: >
  Search for core samples, well cuttings, thin sections, and geologic sample
  data from the USGS Core Research Center and related ScienceBase datasets.
  Use this skill when the user asks about core data from specific formations,
  available rock core samples, well cuttings from a state or basin, thin
  section data, core photos, analog core for reservoir characterization, USGS
  sample repositories, drill core from Marcellus or Smackover, available core
  for analysis, geochemical data from core samples, core mineralogy, or any
  request for physical rock sample metadata from U.S. wells. Trigger for
  phrases like "core data from Marcellus", "available core samples in WV",
  "USGS core repository", "well cuttings from Appalachian Basin", "thin
  sections from Smackover", "core photos for reservoir study", "analog core
  for DLE feasibility", "geochemical core analysis data", "drill core
  samples", "CRC well catalog". Outputs core sample inventory tables and
  associated geochemical data with formation and location context.
---

# USGS Core Research Center Skill

Searches the USGS Core Research Center (CRC) Well Catalog and ScienceBase
for core samples, well cuttings, thin sections, and geochemical data from
U.S. wells -- essential for analog studies supporting DLE feasibility
analysis and reservoir characterization.

---

## Credential

**None required.** The CRC Well Catalog and ScienceBase are publicly accessible.

```bash
# No API key needed -- USGS CRC and ScienceBase are open access
```

---

## Data Sources

| Source | Type | URL |
|--------|------|-----|
| CRC Well Catalog | Web application (no REST API) | https://my.usgs.gov/crcwc/ |
| ScienceBase Catalog | REST API (JSON) | https://www.sciencebase.gov/catalog/ |
| USGS Core Research Center (info) | Informational page | https://www.usgs.gov/core-research-center |

### CRC Well Catalog

The CRC at the USGS Denver Federal Center maintains one of the largest
publicly accessible core repositories in the U.S. The Well Catalog at
https://my.usgs.gov/crcwc/ provides searchable metadata for:

- **Cores** -- continuous rock cylinders from drilling
- **Cuttings** -- rock chips from drilling fluid returns
- **Thin sections** -- prepared microscope slides
- **Photos** -- core box photos where available
- **Analyses** -- geochemical and petrophysical analyses performed on samples

**Important:** The CRC Well Catalog is a web-only application. There is no
REST API. Searches must be performed through the web form at
https://my.usgs.gov/crcwc/.

### ScienceBase (Programmatic Access)

ScienceBase provides programmatic access to published datasets that include
core-derived geochemical and mineralogical data. This is the primary
programmatic pathway for core-related data.

---

## CRC Well Catalog -- Web Search

### Search Parameters

The CRC Well Catalog web form accepts these fields (all optional):

| Parameter | Description | Example |
|-----------|-------------|---------|
| State | U.S. state name | West Virginia |
| County | County name | Monongalia |
| API Number | 14-digit API well number | 47-061-00123 |
| CRC Library Number | Internal catalog ID | (numeric) |
| Operator | Well operator name | EQT |
| Well Name | Well name | Smith #1 |
| Field Name | Oil/gas field | — |
| Formation | Target formation | Marcellus |
| Township (range) | Township number range | 5-10 |
| Range (range) | Range number range | 3-8 |
| Sample Type | Core or Cuttings | Core |
| Photos Available | Yes/No filter | Yes |
| Thin Sections | Yes/No filter | Yes |
| Analysis Completed | Yes/No filter | Yes |

**Usage:** Navigate to https://my.usgs.gov/crcwc/ and fill in the relevant
fields. Leaving all fields empty returns the entire catalog.

### To Search for Core from Key DLE Formations

1. Navigate to https://my.usgs.gov/crcwc/
2. Enter formation name (e.g., "Marcellus", "Smackover", "Utica")
3. Optionally filter by state
4. Select "Core" as sample type
5. Check "Photos Available" and/or "Analysis Completed" for richer data

---

## ScienceBase API -- Programmatic Search

### Search for Core-Related Datasets

```bash
# Search ScienceBase for core geochemical data
curl -s "https://www.sciencebase.gov/catalog/items?q=core+geochemical+data&format=json&max=10&fields=title,id,summary" \
  | jq '.items[] | {id, title}'

# Search for formation-specific core data
curl -s "https://www.sciencebase.gov/catalog/items?q=Marcellus+core+geochemistry&format=json&max=10&fields=title,id" \
  | jq '.items[] | {id, title}'

# Search for Smackover formation core data
curl -s "https://www.sciencebase.gov/catalog/items?q=Smackover+core+samples&format=json&max=10&fields=title,id" \
  | jq '.items[] | {id, title}'

# Search broadly for core and cuttings data
curl -s "https://www.sciencebase.gov/catalog/items?q=drill+core+cuttings+geochemistry&format=json&max=10&fields=title,id,summary" \
  | jq '.items[] | {id, title}'
```

### Get Dataset Details and Files

```bash
# Get full metadata for a ScienceBase item
curl -s "https://www.sciencebase.gov/catalog/item/ITEM_ID?format=json&fields=title,summary,files,contacts,dates" \
  | jq '{title, summary: .summary, files: [.files[] | {name, size, url: .downloadUri}]}'

# Example: Green River Formation core geochemistry
curl -s "https://www.sciencebase.gov/catalog/item/6841b179d4be024662c8e3f6?format=json&fields=title,files" \
  | jq '{title, files: [.files[] | {name, size, url: .downloadUri}]}'
```

### Search by Spatial Extent

```bash
# Search ScienceBase for core data within a bounding box
curl -s "https://www.sciencebase.gov/catalog/items?q=core+geochemistry&format=json&max=10&fields=title,id&filter=spatialQuery={\"wkt\":\"POLYGON((-81 38,-79 38,-79 40,-81 40,-81 38))\",\"relation\":\"intersects\"}" \
  | jq '.items[] | {id, title}'
```

---

## Key ScienceBase Datasets for DLE Research

| ScienceBase ID | Title | Relevance |
|----------------|-------|-----------|
| 6841b179d4be024662c8e3f6 | Geochemical/mineralogical data, Green River Fm core, Uinta Basin | Analog for evaporite-hosted Li |
| 67d3043ed34e1acf3979cd24 | Geochemical data, Greenhorn Fm, Portland Core, CO | Methodology example |
| 65cbbefdd34ef4b119cb37de | Zircon U-Pb geochronology, drill core, MT/NE/NV/WY | Geochronology methods |

**Discovery strategy:** Search ScienceBase for formation names relevant to
DLE (Smackover, Marcellus, Utica, Bakken, Wolfcamp) combined with terms
like "core", "geochemistry", "mineralogy", "brine", "lithium".

---

## Workflow

### Step 1 -- Resolve Intent

| User asks about... | Strategy |
|---------------------|----------|
| Available core from a formation | CRC Well Catalog web search by formation |
| Core geochemical data (published) | ScienceBase API search |
| Core photos | CRC Well Catalog with "Photos Available" filter |
| Analog core for reservoir study | CRC by formation + state; ScienceBase for published data |
| Thin section / petrographic data | CRC with "Thin Sections" filter |
| Specific well core | CRC by API number or well name |

### Step 2 -- Search

**For CRC inventory (what core exists):**
Direct the user to https://my.usgs.gov/crcwc/ with specific search parameters.

**For published core data (geochemistry, mineralogy):**
Use ScienceBase API:

```bash
# Formation-specific search
curl -s "https://www.sciencebase.gov/catalog/items?q=Marcellus+Shale+core+geochemistry&format=json&max=10&fields=title,id,summary" \
  | jq '.items[] | {id, title, summary: (.summary // "No summary")}'
```

### Step 3 -- Download and Analyze Data

```bash
# Get file list from a dataset
ITEM_ID="6841b179d4be024662c8e3f6"
curl -s "https://www.sciencebase.gov/catalog/item/${ITEM_ID}?format=json&fields=files" \
  | jq '.files[] | {name, size, url: .downloadUri}'

# Download a specific file
curl -L -o /tmp/core_geochem_data.csv \
  "https://www.sciencebase.gov/catalog/file/get/${ITEM_ID}?f=__disk__HASH"
```

### Step 4 -- Produce Output

**Format: Core Inventory Table + Data Summary**

---

## Output Format

### Example 1: Core Inventory Search

```
## Available Core: Marcellus Shale, West Virginia

**Source:** USGS Core Research Center Well Catalog (https://my.usgs.gov/crcwc/)
**Search:** Formation = "Marcellus", State = "West Virginia", Sample Type = "Core"

| CRC Library # | Operator | Well Name | County | Formation | Depth (ft) | Photos | Analysis |
|---------------|----------|-----------|--------|-----------|------------|--------|----------|
| 12345 | EQT Corp | Smith #1 | Monongalia | Marcellus | 7,200-7,350 | Yes | Yes |
| 12346 | Antero | Jones Unit | Doddridge | Marcellus | 7,500-7,680 | Yes | No |
| ... | ... | ... | ... | ... | ... | ... | ... |

**Summary:** The CRC holds [N] Marcellus Shale core entries from West
Virginia. [X] have photos available and [Y] have completed analyses.
Core depths range from ~6,800 to 8,200 ft, consistent with Marcellus
depths in north-central WV. Contact the CRC (crc@usgs.gov) to arrange
core viewing or sampling.
```

### Example 2: Published Core Geochemistry

```
## ScienceBase Datasets: Core Geochemistry for Appalachian Basin

| ScienceBase ID | Title | Files | Format |
|----------------|-------|-------|--------|
| abc123 | Marcellus Shale core geochemistry, WV | 3 | CSV, Excel |
| def456 | Utica/Point Pleasant core mineralogy, OH | 2 | CSV |

**Data summary:** Found [N] published datasets with core-derived
geochemical data for Appalachian Basin formations. Key analytes
include major/trace elements (XRF), mineralogy (XRD), and organic
geochemistry (TOC, Rock-Eval). Lithium data availability in core
datasets is limited -- most core geochemistry focuses on major
elements and reservoir properties rather than brine chemistry.
```

---

## Error Handling

| Issue | Cause | Action |
|-------|-------|--------|
| CRC Well Catalog unavailable | USGS web app maintenance | Use ScienceBase API as alternative for published data |
| ScienceBase search returns no results | Too narrow query | Broaden search terms; try formation name alone |
| ScienceBase item 404 | Item ID changed or removed | Search by title keywords instead |
| Download timeout on large files | Network/file size | Download to /tmp/ with curl -L; increase timeout |
| No core data for target formation | CRC may not hold core from that formation | Check state geological surveys (e.g., WVGES, PA DCNR) |
| "Not Found Error" on CRC search URL | Incorrect URL pattern | CRC does not support direct URL queries; use web form |

---

## Caveats

1. **No REST API for CRC Well Catalog.** The CRC Well Catalog is web-form-only.
   Programmatic bulk access to the CRC inventory is not available. For
   published data, use ScienceBase.

2. **CRC is an inventory, not a dataset.** The CRC catalog tells you what
   core exists and where it is stored. To access the actual core material,
   you must contact the CRC (crc@usgs.gov) and arrange a visit or sampling
   request. There are fees for core sampling and thin section preparation.

3. **Limited lithium data in core datasets.** Most published core geochemistry
   datasets focus on major elements, mineralogy, and reservoir properties.
   Lithium concentration data from core is sparse compared to produced water
   data. For Li concentrations, the `pnge-core:usgs-produced-waters` skill
   (brine chemistry) is typically more useful than core data.

4. **State geological survey repositories.** The USGS CRC is one of several
   core repositories. State geological surveys also maintain core collections:
   - West Virginia: WVGES core library (Morgantown)
   - Pennsylvania: PA DCNR core repository
   - Ohio: ODNR core library
   - Kansas: KGS well log and core repository
   For Appalachian Basin research, state repositories may have more relevant
   core than the federal CRC.

5. **ScienceBase data quality varies.** Published datasets on ScienceBase range
   from raw lab data to processed/interpreted results. Always check the data
   dictionary and methodology description before using values.

6. **Core depth vs. formation assignment.** Core intervals may span multiple
   formations. The "formation" field in the CRC catalog reflects the primary
   target but may not represent the entire cored interval. Verify formation
   tops against well logs.

7. **Physical access required for detailed study.** Core photos and published
   data provide screening information. Detailed petrographic, mineralogical,
   or geochemical analysis requires physical access to the core material at
   the CRC facility in Lakewood, CO.

---

## Implementation Notes

- CRC contact: crc@usgs.gov, phone: (303) 236-1005, Lakewood, CO
- CRC visits: Schedule in advance; standard business hours
- ScienceBase API base: https://www.sciencebase.gov/catalog/
- ScienceBase search supports: `q` (keyword), `filter` (spatial, tag), `fields`, `max`, `offset`
- For spatial searches, use WKT POLYGON format with WGS84 coordinates
- Combine with `pnge-core:usgs-produced-waters` for brine chemistry from the same formations
- Combine with `pnge-state-regulatory:wvges-wells` for West Virginia well data overlay
- For Kansas-specific core/log data, see `pnge-well-engineering:kggs-well-logs`
