# BOEM Offshore Data — Endpoint Reference

Two primary access methods: (1) ArcGIS REST MapServer for spatial/attribute
queries, and (2) bulk ASCII/CSV downloads from the Data Center.

No API keys are required for any BOEM endpoint.

---

## 1. ArcGIS REST MapServer (GIS Queries)

Base URL: `https://gis.boem.gov/arcgis/rest/services/BOEM_BSEE/`

### National-Level Service (MMC_Layers)

MapServer URL:
```
https://gis.boem.gov/arcgis/rest/services/BOEM_BSEE/MMC_Layers/MapServer
```

| Layer ID | Name                                            | Geometry  | Record Count |
|----------|-------------------------------------------------|-----------|--------------|
| 0        | OCS Drilling Platforms                          | Point     | ~1,354       |
| 1        | OCS Oil and Natural Gas Wells                   | Point     | ~56,363      |
| 2        | OCS Oil & Gas Pipelines                         | Polyline  | varies       |
| 4        | Unofficial State Lateral Boundaries             | Polyline  | —            |
| 5        | BOEM OCS Administrative Boundaries              | Polyline  | —            |
| 7        | BOEM Limit of OCSLA 8(g) zone                   | Polyline  | —            |
| 8        | Submerged Lands Act Boundary                    | Polyline  | —            |
| 10       | BOEM OCS Protraction Diagrams & Leasing Maps    | Polygon   | —            |
| 11       | BOEM OCS Lease Blocks                           | Polygon   | —            |
| 12       | BOEM Block Aliquots                             | Polygon   | —            |
| 15       | BOEM Oil and Gas Leases                         | Polygon   | ~1,994       |
| 19       | Proposed Final OCS Leasing Program 2012-2017    | Polygon   | —            |
| 20       | BOEM Oil and Gas Planning Areas                 | Polygon   | —            |
| 21       | Outer Continental Shelf Lands Act               | Polygon   | —            |
| 22       | 2010 Vessel Traffic (AIS)                       | Polygon   | —            |
| 23       | 2009 Vessel Traffic (AIS)                       | Polygon   | —            |

### Regional Services

| Service                  | URL Suffix         | Coverage                |
|--------------------------|--------------------|-------------------------|
| Gulf of America          | GOA_Layers         | GOM deepwater/shelf     |
| Atlantic                 | ATL_Layers         | Atlantic OCS            |
| Pacific                  | POC_Layers         | Pacific OCS             |
| Alaska                   | AK_Layers          | Alaska OCS              |

GOA_Layers has additional layers including Seismic Anomalies (layer 9) and
Lease Points (layer 11) not present in the national service.

### Key Fields Per Layer

**Layer 0 — OCS Drilling Platforms:**
- COMPLEX_ID_NUM (Integer) — Platform complex identifier
- INSTALL_DATE (Date) — Installation date
- REMOVAL_DATE (Date) — Removal date (null if still active)

**Layer 1 — OCS Oil and Natural Gas Wells:**
- API_NUMBER (String) — 12-digit API well number
- OPERATOR (String) — Operator company number
- WELL_NAME (String) — Well name/designation
- SPUD_DATE (String) — Date drilling began
- TYPE_CODE (String) — Well type code
- TYPE_CODE_DESC (String) — Well type description (Development, Exploratory, etc.)
- STATUS (String) — Current well status code
- STATUS_DESCRIPTION (String) — Status text (Permanently Abandoned, Producing, etc.)
- DEPTH (String) — Total depth in feet
- X, Y (Double) — Longitude, Latitude (NAD83)

**Layer 15 — BOEM Oil and Gas Leases:**
- LEASE_NUMBER (String) — OCS lease serial number
- LEASE_STATUS_CD (String) — Status code (PROD=producing, active leases)
- LEASE_EFF_DATE (Date) — Lease effective date
- LEASE_EXPIR_DATE (Date) — Expiration date
- SALE_NUMBER (String) — Lease sale number
- ROYALTY_RATE (Double) — Royalty rate (fraction, e.g. 0.1667)
- MINERAL_TYPE_CD (String) — Mineral type code
- CURRENT_AREA (Double) — Current lease area
- INITIAL_AREA (Double) — Original lease area

### ArcGIS REST Query Syntax

All layers support standard ArcGIS REST query parameters:

```
GET {MapServer}/{LayerID}/query
```

| Parameter           | Example                                 | Notes                           |
|---------------------|-----------------------------------------|---------------------------------|
| where               | where=STATUS='PA'                       | SQL WHERE clause                |
| outFields           | outFields=API_NUMBER,OPERATOR,DEPTH     | Comma-separated field names     |
| geometry            | geometry=-91,28,-89,29                  | Bounding box (xmin,ymin,xmax,ymax) |
| geometryType        | geometryType=esriGeometryEnvelope       | Envelope, Point, Polygon        |
| spatialRel          | spatialRel=esriSpatialRelIntersects     | Intersects, Contains, Within    |
| resultRecordCount   | resultRecordCount=100                   | Max rows to return              |
| resultOffset        | resultOffset=100                        | Pagination offset               |
| returnCountOnly     | returnCountOnly=true                    | Return only the count           |
| returnDistinctValues| returnDistinctValues=true               | Unique values only              |
| orderByFields       | orderByFields=DEPTH DESC               | Sort order                      |
| f                   | f=json                                  | Response format (json, geojson) |

Spatial reference is NAD83 (WKID 4269) for all national layers.

---

## 2. Bulk ASCII Data Downloads

Base URL: `https://www.data.boem.gov/`

These are zipped delimited text files (pipe-delimited or comma-delimited)
containing the full database tables. Updated periodically.

### Well Data
| File                          | URL Path                                  |
|-------------------------------|-------------------------------------------|
| Borehole data                 | /Well/Files/BoreholeRawData.zip           |
| APD (Application to Drill)    | /Well/Files/APDRawData.zip                |
| API Number Lookup             | /Well/Files/APIRawData.zip                |
| API Number Changes            | /Well/Files/APIChangesRawData.zip         |
| Bottomhole Pressure Surveys   | /Well/Files/BHPSRawData.zip               |
| eWell APD Submissions         | /Well/Files/eWellAPDRawData.zip           |
| eWell APM Submissions         | /Well/Files/eWellAPMRawData.zip           |
| eWell EOR Submissions         | /Well/Files/eWellEORRawData.zip           |
| eWell WAR Submissions         | /Well/Files/eWellWARRawData.zip           |

### Production Data
| File                          | URL Path                                  |
|-------------------------------|-------------------------------------------|
| OGOR-A (production by lease)  | /Production/Files/ogoradelimit.zip        |
| OGOR-A by year (e.g. 2024)   | /Production/Files/ogora2024delimit.zip    |
| OCS Production summary        | /Production/Files/OCSProdRawData.zip      |
| Production by Planning Area   | /Production/Files/ProdPlanAreaRawData.zip |
| Production by Platform        | /Production/Files/ProdByPlatformRawData.zip|
| Production Data (general)     | /Production/Files/ProductionRawData.zip   |
| FMP (Facility Meas. Points)   | /Production/Files/FMPRawData.zip          |
| FMP Meters                    | /Production/Files/FMPMetersRawData.zip    |
| MCP Flow Reports              | /Production/Files/MCPFlowRawData.zip      |
| Offshore Stats by Water Depth | /Production/Files/OffshoreStatsRawData.zip|

### Leasing Data
| File                          | URL Path                                  |
|-------------------------------|-------------------------------------------|
| Lease Owner                   | /Leasing/Files/LeaseOwnerRawData.zip      |
| Assignments                   | /Leasing/Files/AssignmentsRawData.zip     |
| Decommissioning Cost Estimates| /Leasing/Files/DecomCostEstRawData.zip    |
| Lease Area Block Lookup       | /Leasing/Files/LABRawData.zip             |
| Non-Required Documents        | /Leasing/Files/NonReqRawData.zip          |
| Offshore Stats by Field       | /Leasing/Files/OSFRRawData.zip            |
| Serial Register Page          | /Leasing/Files/SerialRegRawData.zip       |

### Platform / Pipeline / Other
| File                          | URL Path                                  |
|-------------------------------|-------------------------------------------|
| Platform Structures           | /Platform/Files/PlatStrucRawData.zip      |
| Pipeline Locations            | /Pipeline/Files/PipeLocRawData.zip        |
| Pipeline Permits              | /Pipeline/Files/PipePermRawData.zip       |
| ROW Descriptions              | /Pipeline/Files/RowDescRawData.zip        |
| Company data                  | /Company/Files/CompanyRawData.zip         |
| Company Approvals             | /Company/Files/ApprovalsRawData.zip       |
| INCs (Non-Compliance)         | /Company/Files/INCSRawData.zip            |
| Plans (Exploration/Dev)       | /Plans/Files/PlansRawData.zip             |
| Scanned Documents index       | /Other/Files/ScannedDocsRawData.zip       |
| Concrete Anchors              | /Other/Files/Anchors.zip                  |
| Deepwater Qualified Fields    | /Other/Files/DeepQualRawData.zip          |
| Permanent Deepwater Strucs    | /Other/Files/PermStrucRawData.zip         |
| Incident/Investigation        | /Other/Files/IncInvRawData.zip            |
| FRS Well Data                 | /Other/Files/FRSWellDataRawData.zip       |
| Royalty Reference             | /Other/Files/RoyaltyRefRawData.zip        |

---

## 3. BOEM Data Center Online Query Pages

The Data Center at `https://www.data.boem.gov/` provides interactive
DevExpress-based query builders. These are web-only (not API-accessible)
but useful for ad-hoc exploration:

| Domain      | URL                                                    |
|-------------|--------------------------------------------------------|
| Well        | https://www.data.boem.gov/Main/Well.aspx               |
| Production  | https://www.data.boem.gov/Main/Production.aspx         |
| Leasing     | https://www.data.boem.gov/Main/Leasing.aspx            |
| Platform    | https://www.data.boem.gov/Main/Platform.aspx           |
| Pipeline    | https://www.data.boem.gov/Main/Pipeline.aspx           |
| Company     | https://www.data.boem.gov/Main/Company.aspx            |
| Plans       | https://www.data.boem.gov/Main/Plans.aspx              |
| Raw Data    | https://www.data.boem.gov/Main/RawData.aspx            |

These pages do not expose a REST/JSON API. For programmatic access, use
the GIS MapServer queries or bulk ASCII downloads above.

---

## 4. OCS Planning Areas Reference

| Code  | Planning Area                  | Region       |
|-------|--------------------------------|--------------|
| CPA   | Central Planning Area          | Gulf of America |
| WPA   | Western Planning Area          | Gulf of America |
| EPA   | Eastern Planning Area          | Gulf of America |
| MDA   | Mid-Atlantic                   | Atlantic     |
| SAA   | South Atlantic                 | Atlantic     |
| NAA   | North Atlantic                 | Atlantic     |
| WCA   | Washington/Oregon              | Pacific      |
| CCA   | Central California             | Pacific      |
| SCA   | Southern California            | Pacific      |
| BFS   | Beaufort Sea                   | Alaska       |
| CHS   | Chukchi Sea                    | Alaska       |
| NAS   | North Aleutian Basin           | Alaska       |
| CKS   | Cook Inlet                     | Alaska       |
| GOS   | Gulf of Alaska                 | Alaska       |

---

## 5. Well Status Codes Reference

| Code | Description              |
|------|--------------------------|
| PA   | Permanently Abandoned    |
| TA   | Temporarily Abandoned    |
| COM  | Completed                |
| DSI  | Drilling Suspended       |
| DRL  | Drilling                 |
| ST   | Sidetrack                |
| CNL  | Cancelled                |

## 6. Lease Status Codes Reference

| Code | Description              |
|------|--------------------------|
| PROD | Producing                |
| EXPR | Expired                  |
| RELD | Relinquished             |
| TERM | Terminated               |
| DSPS | Disposed                 |
| SOP  | Suspension of Production |
| SOO  | Suspension of Operations |
