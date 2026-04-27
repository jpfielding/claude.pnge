# DOE Geothermal API Reference

## 1. OpenEI Semantic MediaWiki API

**Base URL:** `https://openei.org/w/api.php`
**Authentication:** None required
**Format:** JSON (append `format=json` parameter)

### action=ask (Primary query method)

Executes a Semantic MediaWiki inline query. The `query` parameter uses SMW
query syntax with `[[conditions]]` and `|?printouts`.

**Parameters:**
| Parameter | Required | Description |
|-----------|----------|-------------|
| `action` | Yes | Must be `ask` |
| `query` | Yes | SMW query string (URL-encoded) |
| `format` | Yes | `json` for JSON output |

**SMW Query Syntax:**
```
[[Category:Geothermal Resource Areas]]  -- category filter
[[Place::Utah]]                         -- property equality filter
|?Coordinates                           -- request property in output
|?USGSMeanReservoirTemp                 -- request property in output
|limit=50                               -- max results per page
|offset=0                               -- pagination offset
```

**Complete example -- all geothermal areas in Nevada:**
```bash
curl -s "https://openei.org/w/api.php" \
  --data-urlencode "action=ask" \
  --data-urlencode "query=[[Category:Geothermal Resource Areas]][[Place::Nevada]]|?Coordinates|?USGSMeanReservoirTemp|?USGSMeanCapacity|?USGSEstReservoirVol|?GeothermalRegion|limit=100" \
  --data-urlencode "format=json"
```

**Complete example -- all areas with high reservoir temperature:**
```bash
# Fetch all 432+ areas, then filter locally for temp > 423 K (150C)
curl -s "https://openei.org/w/api.php" \
  --data-urlencode "action=ask" \
  --data-urlencode "query=[[Category:Geothermal Resource Areas]]|?Coordinates|?USGSMeanReservoirTemp|?USGSMeanCapacity|?Place|limit=500" \
  --data-urlencode "format=json"
```

**Response structure:**
```json
{
  "query": {
    "printrequests": [
      {"label": "", "key": "", "redi": "", "typeid": "_wpg", "mode": 2},
      {"label": "Coordinates", "key": "Coordinates", "redi": "", "typeid": "_geo", "mode": 1}
    ],
    "results": {
      "Area Name Here": {
        "printouts": {
          "Coordinates": [{"lat": 39.6133, "lon": -112.7283}],
          "USGSMeanReservoirTemp": [363.15],
          "USGSMeanCapacity": ["4 MW"],
          "USGSEstReservoirVol": ["1.20 km\u00b3"],
          "Place": [{"fulltext": "Utah", "fullurl": "https://openei.org/wiki/Utah", "namespace": 0, "exists": "1", "displaytitle": "Utah: Energy Resources"}],
          "GeothermalRegion": [{"fulltext": "Northern Basin and Range Geothermal Region", "fullurl": "..."}]
        },
        "fulltext": "Area Name Here",
        "fullurl": "https://openei.org/wiki/Area_Name_Here",
        "namespace": 0,
        "exists": "1",
        "displaytitle": ""
      }
    },
    "serializer": "SMW\\Serializers\\QueryResultSerializer",
    "version": 2,
    "meta": {
      "hash": "...",
      "count": 3,
      "offset": 0,
      "source": "",
      "time": "0.026834"
    }
  },
  "query-continue-offset": 50
}
```

**Important notes on response parsing:**
- `results` is a **dict** when there are results, or an **empty list `[]`** when there are none
- `USGSMeanReservoirTemp` values are in **Kelvin** -- subtract 273.15 for Celsius
- `USGSMeanCapacity` is a string like `"4 MW"` -- parse the numeric portion
- `Place` values are page references -- use the `fulltext` field for the state name
- If `query-continue-offset` is present, there are more results to fetch

### action=browsebysubject (Detailed single-page query)

Returns all semantic properties for a single wiki page.

```bash
curl -s "https://openei.org/w/api.php" \
  --data-urlencode "action=browsebysubject" \
  --data-urlencode "subject=Cove_Fort_Geothermal_Area" \
  --data-urlencode "format=json"
```

**Response contains:**
```json
{
  "query": {
    "subject": "Cove_Fort_Geothermal_Area#0##",
    "data": [
      {"property": "Coordinates", "dataitem": [{"type": 6, "item": "38.6,-112.55"}]},
      {"property": "USGSMeanReservoirTemp", "dataitem": [{"type": 3, "item": "423.15"}]},
      {"property": "USGSMeanCapacity", "dataitem": [{"type": 2, "item": "26 MW"}]}
    ]
  }
}
```

### action=query (MediaWiki category listing)

List all geothermal categories:
```bash
curl -s "https://openei.org/w/api.php?action=query&list=allcategories&acprefix=Geothermal&format=json&aclimit=50"
```

Search wiki pages by text:
```bash
curl -s "https://openei.org/w/api.php?action=query&list=search&srsearch=lithium+geothermal&format=json&srlimit=10"
```

---

## 2. OpenEI REST API (api.openei.org)

**Base URL:** `https://api.openei.org/`
**Authentication:** API key required (query parameter `api_key`)
**Key signup:** https://openei.org/services/api/signup/

This API is primarily for utility rate data but may provide supplementary
energy data. The geothermal-specific data is better accessed through the
Semantic MediaWiki API above.

```bash
# Example: utility rates query (requires key)
curl -s "https://api.openei.org/utility_rates?version=8&format=json&limit=5&api_key=$OPENEI_API_KEY"
```

---

## 3. GDR (Geothermal Data Repository)

**Base URL:** `https://gdr.openei.org/`
**Authentication:** None required for public access
**API:** No JSON REST API available -- HTML web interface only

### Search

```bash
# Returns HTML page with search results
curl -sL "https://gdr.openei.org/search?q=produced+water+geothermal"
```

Parse the response HTML for submission links matching `/submissions/\d+`.

### Submission pages

```bash
# Returns HTML page with dataset metadata and download links
curl -sL "https://gdr.openei.org/submissions/1383"
```

### File downloads

Download links are found within submission pages. They typically point to
CSV, ZIP, or Excel files hosted on the GDR server.

### Known high-value GDR submissions for Li/geothermal research

Search terms to find relevant datasets:
- `co-production oil gas geothermal`
- `temperature depth well log`
- `lithium brine geothermal`
- `heat flow continental United States`
- `EGS reservoir stimulation`
- `produced water chemistry`

---

## 4. NREL Geothermal Prospector

**URL:** `https://maps.nrel.gov/geothermal-prospector/`
**API:** No public REST API -- web-based GIS viewer only

Available map layers:
- Temperature at depth (3.5 km, 4.5 km, 6.5 km, 10 km)
- Heat flow measurements
- Geothermal favorability (EGS, hydrothermal)
- Known geothermal sites and power plants
- Sedimentary geothermal potential
- Deep direct-use potential

Direct users to this tool for map-based exploration. Not queryable via API.

---

## Verified Geothermal Resource Area Properties

These properties were verified against live OpenEI data (March 2025):

| Property | Data Type | Notes |
|----------|-----------|-------|
| `Coordinates` | Geographic (lat/lon object) | Present for most areas |
| `BoundingCoordinatesNE` | String "lat,lon" | Bounding box northeast corner |
| `BoundingCoordinatesSW` | String "lat,lon" | Bounding box southwest corner |
| `USGSMeanReservoirTemp` | Number (Kelvin) | From USGS 2008 assessment |
| `USGSMeanCapacity` | String with "MW" | Estimated mean capacity |
| `USGSEstReservoirVol` | String with "km3" | Estimated reservoir volume |
| `GrossProdCapacity` | Number | Currently installed gross capacity |
| `NetProdCapacity` | Number | Currently installed net capacity |
| `Place` | Page reference | State or country |
| `GeothermalRegion` | Page reference | USGS geothermal region |
| `Name` | String | Full area name |
| `CSC-Status` | String | Case study status |
| `CSC-Priority` | String | Case study priority level |

---

## Pagination

OpenEI SMW queries support pagination through the query string:

```
|limit=50|offset=0     (first 50 results)
|limit=50|offset=50    (next 50 results)
|limit=50|offset=100   (next 50 results)
```

The response includes `query-continue-offset` when more results are available.
Maximum `limit` is 500 per request. The full geothermal resource areas dataset
(432+ areas) can be retrieved in a single request with `limit=500`.

---

## Rate Limits

- **OpenEI SMW API:** No documented rate limits, but be respectful (1-2 req/sec)
- **OpenEI REST API:** Depends on API key tier (default is reasonable for research)
- **GDR:** Standard web server limits; no aggressive scraping
