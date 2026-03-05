# USGS Earthquake Hazards Program — ComCat FDSN Event API Reference

**Base URL:** `https://earthquake.usgs.gov/fdsnws/event/1/`

**Standard:** FDSN Web Services (International Federation of Digital Seismograph Networks)

**Authentication:** None required. No API key needed.

**Rate Limits:** No formal rate limit, but USGS requests responsible use. Avoid
more than ~100 requests per minute. Use the `count` endpoint before large queries
to estimate result size.

---

## Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/query` | GET | Search earthquakes, return event data |
| `/count` | GET | Count matching events (same params as query, returns integer) |
| `/application.json` | GET | API metadata: catalogs, contributors, event types, magnitude types |
| `/version` | GET | API version string |

---

## Query Parameters

### Time Filters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `starttime` | ISO 8601 | NOW - 30 days | Start of time window (e.g., `2024-01-01` or `2024-01-01T00:00:00`) |
| `endtime` | ISO 8601 | NOW | End of time window |
| `updatedafter` | ISO 8601 | none | Only events updated after this time |

**Note:** Maximum time range is 30 days when requesting large result sets
without geographic constraints. Use geographic filters or the `limit` parameter
for longer ranges.

### Location Filters — Circle (Radial Search)

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `latitude` | decimal degrees | none | Center latitude (-90 to 90) |
| `longitude` | decimal degrees | none | Center longitude (-180 to 180) |
| `maxradiuskm` | km | 20001.6 | Maximum radius from center point |
| `minradiuskm` | km | 0 | Minimum radius (donut search) |

All four can be combined. `latitude` and `longitude` are required together
if either is specified.

### Location Filters — Rectangle (Bounding Box)

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `minlatitude` | decimal degrees | -90 | Southern boundary |
| `maxlatitude` | decimal degrees | 90 | Northern boundary |
| `minlongitude` | decimal degrees | -180 | Western boundary |
| `maxlongitude` | decimal degrees | 180 | Eastern boundary |

Cannot combine circle and rectangle filters in the same request.

### Magnitude Filters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `minmagnitude` | float | none | Minimum magnitude |
| `maxmagnitude` | float | none | Maximum magnitude |
| `magnitudetype` | string | none | Filter by mag type: `ml`, `mw`, `mww`, `mb`, `md`, etc. |

### Depth Filters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `mindepth` | km | -100 | Minimum depth (negative = above sea level) |
| `maxdepth` | km | 1000 | Maximum depth |

**PNGE note:** Induced seismicity from injection wells is typically shallow
(< 10 km). Use `maxdepth=15` to isolate likely injection-related events.

### Output Controls

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `format` | string | `quakeml` | Output format: `geojson`, `csv`, `xml`, `text`, `quakeml` |
| `limit` | int | 20000 | Maximum events returned (max: 20000) |
| `offset` | int | 1 | Starting record for pagination (1-based) |
| `orderby` | string | `time` | Sort order: `time` (newest first), `time-asc`, `magnitude`, `magnitude-asc` |

### Catalog and Contributor Filters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `catalog` | string | none | Network catalog: `ok` (Oklahoma), `tx` (TexNet), `us` (USGS), `se` (SE US), etc. |
| `contributor` | string | none | Contributing network |

### Event Type Filters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `eventtype` | string | none | Filter by type. Key values for PNGE: `earthquake`, `induced or triggered event`, `quarry blast` |

**Important:** Most induced earthquakes are classified as plain `earthquake`,
not `induced or triggered event`. The `induced or triggered event` type is
only used when USGS has high confidence in the classification. Do NOT rely
on this filter alone to find injection-induced events.

### Other Filters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `alertlevel` | string | none | PAGER alert: `green`, `yellow`, `orange`, `red` |
| `mincdi` | float | none | Min community internet intensity (DYFI) |
| `maxcdi` | float | none | Max community internet intensity |
| `minfelt` | int | none | Min number of felt reports |
| `minmmi` | float | none | Min ShakeMap intensity |
| `maxmmi` | float | none | Max ShakeMap intensity |
| `minsig` | int | none | Min significance (0-1000+) |
| `maxsig` | int | none | Max significance |
| `reviewstatus` | string | none | `automatic` or `reviewed` |
| `eventid` | string | none | Fetch a specific event by ID |

---

## GeoJSON Response Structure

```json
{
  "type": "FeatureCollection",
  "metadata": {
    "generated": 1772732955000,
    "url": "https://earthquake.usgs.gov/fdsnws/event/1/query?...",
    "title": "USGS Earthquakes",
    "status": 200,
    "api": "1.14.1",
    "limit": 20,
    "offset": 1,
    "count": 20
  },
  "features": [
    {
      "type": "Feature",
      "properties": {
        "mag": 5.06,
        "place": "8 km NW of Prague, Oklahoma",
        "time": 1706937868269,
        "updated": 1768769682778,
        "tz": null,
        "url": "https://earthquake.usgs.gov/earthquakes/eventpage/ok2024cish",
        "detail": "https://earthquake.usgs.gov/fdsnws/event/1/query?eventid=ok2024cish&format=geojson",
        "felt": 26480,
        "cdi": 6.9,
        "mmi": 7.167,
        "alert": "green",
        "status": "reviewed",
        "tsunami": 0,
        "sig": 1084,
        "net": "ok",
        "code": "2024cish",
        "ids": ",us7000lwmc,ok2024cish,",
        "sources": ",us,ok,",
        "types": ",dyfi,ground-failure,impact-text,losspager,moment-tensor,origin,phase-data,shakemap,",
        "nst": 64,
        "dmin": 0,
        "rms": 0.25,
        "gap": 98,
        "magType": "mww",
        "type": "earthquake",
        "title": "M 5.1 - 8 km NW of Prague, Oklahoma"
      },
      "geometry": {
        "type": "Point",
        "coordinates": [-96.76383333, 35.53433333, 3]
      },
      "id": "ok2024cish"
    }
  ]
}
```

### Feature Properties (Key Fields)

| Field | Type | Description |
|-------|------|-------------|
| `mag` | float | Magnitude value |
| `place` | string | Human-readable location description |
| `time` | long | Unix timestamp in milliseconds |
| `updated` | long | Last update timestamp in milliseconds |
| `url` | string | Link to USGS event page |
| `detail` | string | GeoJSON detail URL for this event |
| `felt` | int/null | Number of DYFI felt reports |
| `cdi` | float/null | Community Decimal Intensity (DYFI max) |
| `mmi` | float/null | ShakeMap max instrumental intensity |
| `alert` | string/null | PAGER alert level |
| `status` | string | `automatic` or `reviewed` |
| `tsunami` | int | 1 if tsunami warning issued |
| `sig` | int | Significance score (0-1000+) — function of mag, felt reports, damage |
| `net` | string | Preferred network code (`ok`, `tx`, `us`, `se`) |
| `code` | string | Event code within network |
| `ids` | string | Comma-delimited list of all event IDs from all networks |
| `sources` | string | Comma-delimited contributing network codes |
| `types` | string | Comma-delimited available product types |
| `nst` | int/null | Number of stations used |
| `dmin` | float/null | Distance to nearest station (degrees) |
| `rms` | float/null | RMS travel time residual (seconds) |
| `gap` | float/null | Azimuthal gap (degrees) — smaller = better constrained |
| `magType` | string | Magnitude type: `ml`, `mw`, `mww`, `mb`, `md`, etc. |
| `type` | string | Event type: `earthquake`, `quarry blast`, etc. |
| `title` | string | Formatted title: "M X.X - Location" |

### Geometry

Coordinates array: `[longitude, latitude, depth_km]`

- Longitude: decimal degrees (-180 to 180)
- Latitude: decimal degrees (-90 to 90)
- Depth: kilometers below surface (positive = below)

---

## CSV Response Columns

When `format=csv`, the response includes these columns:

```
time, latitude, longitude, depth, mag, magType, nst, gap, dmin, rms,
net, id, updated, place, type, horizontalError, depthError, magError,
magNst, status, locationSource, magSource
```

---

## PNGE-Relevant Presets

### Oklahoma Induced Seismicity (200 km around OKC)
```
latitude=35.5&longitude=-97.5&maxradiuskm=200&minmagnitude=2.0
```

### Permian Basin / Delaware Basin (TX/NM)
```
latitude=31.8&longitude=-103.5&maxradiuskm=150&minmagnitude=2.0
```

### Appalachian Basin (WV/PA/OH bounding box)
```
minlatitude=37.0&maxlatitude=40.5&minlongitude=-82.5&maxlongitude=-77.5
```

### Eagle Ford Shale (South TX)
```
latitude=28.5&longitude=-98.5&maxradiuskm=150&minmagnitude=2.0
```

### Raton Basin (CO/NM)
```
latitude=37.0&longitude=-104.8&maxradiuskm=50&minmagnitude=2.0
```

### Shallow Events Only (likely injection-related)
```
maxdepth=15
```

---

## Pagination

The API uses 1-based `offset` pagination with a maximum `limit` of 20000.

```
# First page
/query?format=geojson&limit=1000&offset=1&...

# Second page
/query?format=geojson&limit=1000&offset=1001&...
```

Use the `/count` endpoint first to determine total results before paginating.
The `metadata.count` field in the response tells you how many events were
returned in the current page.

---

## Network Codes (Key for PNGE)

| Code | Network | Coverage |
|------|---------|----------|
| `ok` | Oklahoma Geological Survey | Oklahoma — densest induced seismicity monitoring |
| `tx` | TexNet (U. Texas) | Texas — Permian Basin focus |
| `us` | USGS National | Nationwide M2.5+, worldwide M4.5+ |
| `se` | SE US Network | Appalachian/Southeast states |
| `nm` | New Mexico Tech | New Mexico — Delaware Basin |
| `ismpkansas` | Kansas Geological Survey | Kansas induced seismicity |

---

## Magnitude Types

| Type | Name | Use Case |
|------|------|----------|
| `ml` | Local (Richter) | Most common for small/regional events |
| `mw` | Moment magnitude | Standard for M3.5+ |
| `mww` | W-phase moment | Large events (M5+) |
| `mb` | Body-wave | Teleseismic |
| `md` | Duration | Small local events |
| `mb_lg` | Lg-wave | Regional (used by CEUS networks) |

---

## Data Quality Notes

1. **Automatic vs. reviewed:** Events are first posted with `automatic` status
   (within minutes), then upgraded to `reviewed` after analyst inspection
   (hours to days). Use `reviewstatus=reviewed` for research-grade data.

2. **Magnitude revisions:** Initial magnitudes can shift 0.2-0.5 units after
   review. For significant events, check the `updated` timestamp.

3. **Completeness:** Detection threshold varies by region:
   - Oklahoma: complete to ~M1.0 (dense monitoring)
   - Permian Basin: complete to ~M1.5-2.0
   - Appalachian Basin: complete to ~M2.0-2.5
   - Rural areas: complete to ~M2.5-3.0

4. **Induced vs. tectonic:** The API does not reliably distinguish induced from
   tectonic events. Use location, depth (< 10 km), and proximity to injection
   wells as indicators. Cross-reference with UIC Class II well locations from
   the `pnge:epa-enviro` skill.
