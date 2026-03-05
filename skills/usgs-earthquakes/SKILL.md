---
name: usgs-earthquakes
description: >
  Query USGS earthquake data from the ComCat catalog (FDSN Web Services) to
  analyze induced seismicity near oil and gas operations. Use this skill
  whenever the user asks about earthquakes near injection wells, induced
  seismicity, Oklahoma earthquakes, Permian Basin seismic activity,
  Appalachian basin tremors, disposal well earthquakes, UIC Class II
  seismicity, wastewater injection earthquakes, earthquake counts by region,
  seismic hazard near drilling operations, or any request involving earthquake
  data correlated with petroleum engineering activity. Produces event tables,
  counts, magnitude statistics, and depth analysis with narrative summaries
  focused on injection-induced seismicity indicators.
---

# USGS Earthquake (ComCat) Skill

Fetches and analyzes earthquake data from the USGS Earthquake Hazards Program
ComCat catalog via the FDSN Event Web Service. Focused on induced seismicity
from UIC Class II saltwater disposal and hydraulic fracturing operations.

## Credential Handling

**No API key required.** The USGS earthquake API is open and free.

No authentication, registration, or rate-limit tokens are needed. USGS
requests responsible use: avoid more than ~100 requests per minute.

---

## API Structure

**Base URL:** `https://earthquake.usgs.gov/fdsnws/event/1/`

**Standard:** FDSN Web Services (International Federation of Digital
Seismograph Networks) — the same protocol used by seismological agencies
worldwide.

**Endpoints:**

| Endpoint | Description |
|----------|-------------|
| `/query` | Search earthquakes — returns event data in GeoJSON, CSV, XML, or text |
| `/count` | Count matching events — returns a plain integer (same params as query) |
| `/application.json` | API metadata: catalogs, event types, magnitude types |
| `/version` | API version string |

**Key parameters:**

| Parameter | Example | Notes |
|-----------|---------|-------|
| `format` | `format=geojson` | `geojson` (preferred), `csv`, `xml`, `text` |
| `starttime` | `starttime=2024-01-01` | ISO 8601 date or datetime |
| `endtime` | `endtime=2024-12-31` | ISO 8601 date or datetime |
| `minmagnitude` | `minmagnitude=2.5` | Minimum magnitude |
| `maxmagnitude` | `maxmagnitude=5.0` | Maximum magnitude |
| `latitude` | `latitude=35.5` | Center point for radial search |
| `longitude` | `longitude=-97.5` | Center point for radial search |
| `maxradiuskm` | `maxradiuskm=200` | Search radius in km |
| `minlatitude` | `minlatitude=37.0` | Bounding box south edge |
| `maxlatitude` | `maxlatitude=40.5` | Bounding box north edge |
| `minlongitude` | `minlongitude=-82.5` | Bounding box west edge |
| `maxlongitude` | `maxlongitude=-77.5` | Bounding box east edge |
| `mindepth` | `mindepth=0` | Minimum depth in km |
| `maxdepth` | `maxdepth=15` | Maximum depth in km (use for shallow/induced) |
| `limit` | `limit=500` | Max events returned (max: 20000) |
| `offset` | `offset=1` | Pagination start (1-based) |
| `orderby` | `orderby=magnitude` | `time`, `time-asc`, `magnitude`, `magnitude-asc` |
| `reviewstatus` | `reviewstatus=reviewed` | `automatic` or `reviewed` |
| `catalog` | `catalog=ok` | Network catalog: `ok`, `tx`, `us`, `se`, etc. |

See `references/api_reference.md` for the full parameter catalog, GeoJSON
response structure, and all network/magnitude type codes.

---

## PNGE-Relevant Region Presets

These are the key regions for petroleum engineering induced seismicity
research. Use these coordinates as starting points.

### Oklahoma Induced Seismicity Zone
Center: 35.5N, 97.5W | Radius: 200 km
```
latitude=35.5&longitude=-97.5&maxradiuskm=200
```
Peak crisis: 2014-2016 (900+ M3+ events/year). Caused by massive Arbuckle
Group saltwater disposal from Mississippian Lime and Woodford Shale plays.
Oklahoma Corporation Commission Traffic Light Protocol reduced disposal
volumes, seismicity declined but remains elevated above historic baseline.

### Permian Basin / Delaware Basin (TX/NM)
Center: 31.8N, 103.5W | Radius: 150 km
```
latitude=31.8&longitude=-103.5&maxradiuskm=150
```
Currently the most active induced seismicity region in the U.S. Over 1,400
M2+ events in 2024 alone. Driven by record-high saltwater disposal volumes
from Permian Basin horizontal wells. Texas Railroad Commission and NM OCD
have implemented seismic response plans.

### Appalachian Basin (WV/PA/OH)
Bounding box: 37.0-40.5N, 82.5-77.5W
```
minlatitude=37.0&maxlatitude=40.5&minlongitude=-82.5&maxlongitude=-77.5
```
Lower seismicity rate but critical for WV PNGE research. Marcellus/Utica
disposal wells in Ohio have triggered felt events (e.g., Youngstown 2011-2012,
Poland Township). WV/PA have fewer events but increasing monitoring.

### Eagle Ford Shale (South TX)
Center: 28.5N, 98.5W | Radius: 150 km
```
latitude=28.5&longitude=-98.5&maxradiuskm=150
```

### Raton Basin (CO/NM)
Center: 37.0N, 104.8W | Radius: 50 km
```
latitude=37.0&longitude=-104.8&maxradiuskm=50
```
Classic case study — coalbed methane wastewater injection caused Trinidad, CO
earthquake swarm (2001-2011).

---

## Workflow

### Step 1 — Resolve Intent

Map the user's question to a query type:

| User intent | Query approach |
|-------------|----------------|
| "Earthquakes near [location]" | Radial search with lat/lon + radius |
| "Earthquakes in [state/region]" | Bounding box or region preset |
| "How many earthquakes in Oklahoma" | Use `/count` endpoint first |
| "Largest earthquakes near Permian Basin" | Query with `orderby=magnitude` |
| "Recent seismicity near injection wells" | Radial search + short time window |
| "Earthquake trend over time" | Multi-year query, aggregate by year/month |
| "Shallow earthquakes near [area]" | Add `maxdepth=10` or `maxdepth=15` |

### Step 2 — Get Count First

Always query the `/count` endpoint before fetching data to gauge result size:

```bash
curl -s "https://earthquake.usgs.gov/fdsnws/event/1/count?starttime=2024-01-01&endtime=2024-12-31&minmagnitude=2.0&latitude=35.5&longitude=-97.5&maxradiuskm=200"
```

Returns a plain integer (e.g., `1750`). If the count exceeds 500, consider:
- Narrowing the time window
- Increasing the minimum magnitude
- Reducing the search radius
- Paginating with `limit` and `offset`

### Step 3 — Fetch Data

Build the query URL with appropriate filters. Use GeoJSON format for
structured parsing.

**Oklahoma M2.5+ events in 2024 (top 20 by magnitude):**
```bash
curl -s "https://earthquake.usgs.gov/fdsnws/event/1/query?\
format=geojson&\
starttime=2024-01-01&\
endtime=2024-12-31&\
minmagnitude=2.5&\
latitude=35.5&\
longitude=-97.5&\
maxradiuskm=200&\
limit=20&\
orderby=magnitude" | jq '.features[] | {mag: .properties.mag, place: .properties.place, time: (.properties.time/1000 | todate), depth: .geometry.coordinates[2]}'
```

**Permian Basin M2.0+ events in 2024:**
```bash
curl -s "https://earthquake.usgs.gov/fdsnws/event/1/query?\
format=geojson&\
starttime=2024-01-01&\
endtime=2024-12-31&\
minmagnitude=2.0&\
latitude=31.8&\
longitude=-103.5&\
maxradiuskm=150&\
limit=20&\
orderby=magnitude" | jq '.features[] | {mag: .properties.mag, place: .properties.place, depth: .geometry.coordinates[2]}'
```

**Appalachian Basin M1.0+ events (2020-2024):**
```bash
curl -s "https://earthquake.usgs.gov/fdsnws/event/1/query?\
format=geojson&\
starttime=2020-01-01&\
endtime=2024-12-31&\
minmagnitude=1.0&\
minlatitude=37.0&\
maxlatitude=40.5&\
minlongitude=-82.5&\
maxlongitude=-77.5&\
limit=20&\
orderby=magnitude" | jq '.features[] | {mag: .properties.mag, place: .properties.place, depth: .geometry.coordinates[2]}'
```

**Shallow events only (depth < 10 km — likely injection-induced):**
```bash
curl -s "https://earthquake.usgs.gov/fdsnws/event/1/query?\
format=geojson&\
starttime=2024-01-01&\
endtime=2024-12-31&\
minmagnitude=3.0&\
latitude=35.5&\
longitude=-97.5&\
maxradiuskm=200&\
maxdepth=10&\
limit=20&\
orderby=magnitude"
```

**CSV format (useful for spreadsheet analysis):**
```bash
curl -s "https://earthquake.usgs.gov/fdsnws/event/1/query?\
format=csv&\
starttime=2024-01-01&\
endtime=2024-12-31&\
minmagnitude=2.5&\
latitude=35.5&\
longitude=-97.5&\
maxradiuskm=200&\
orderby=time"
```

### Step 4 — Parse Response

GeoJSON response structure:
```json
{
  "type": "FeatureCollection",
  "metadata": {
    "generated": 1772732955000,
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
        "felt": 26480,
        "cdi": 6.9,
        "mmi": 7.167,
        "alert": "green",
        "status": "reviewed",
        "sig": 1084,
        "net": "ok",
        "magType": "mww",
        "type": "earthquake",
        "title": "M 5.1 - 8 km NW of Prague, Oklahoma"
      },
      "geometry": {
        "type": "Point",
        "coordinates": [-96.764, 35.534, 3.0]
      },
      "id": "ok2024cish"
    }
  ]
}
```

**Key fields for PNGE analysis:**

| Field | Path | Significance |
|-------|------|--------------|
| Magnitude | `properties.mag` | Event size — M3+ felt, M4+ potential damage |
| Depth (km) | `geometry.coordinates[2]` | Shallow (< 10 km) = likely induced |
| Location | `geometry.coordinates[0,1]` | Proximity to injection wells |
| Network | `properties.net` | `ok` and `tx` have dense induced-seismicity monitoring |
| Felt reports | `properties.felt` | Community impact indicator |
| CDI | `properties.cdi` | Community Decimal Intensity (1-10 scale) |
| MMI | `properties.mmi` | ShakeMap instrumental intensity |
| Status | `properties.status` | `reviewed` = analyst-verified |

**Converting time:** The `time` field is Unix milliseconds. In jq:
```bash
jq '.properties.time / 1000 | todate'
```
In Python:
```python
from datetime import datetime, timezone
dt = datetime.fromtimestamp(time_ms / 1000, tz=timezone.utc)
```

### Step 5 — Produce Output

**Format: Data Table + Narrative Summary + PNGE Context**

Present a markdown table of results (cap at ~20 rows), then a narrative
summary with induced seismicity context.

**Example output structure:**
```
## Oklahoma Induced Seismicity — M2.5+ Events (2024)

| Date (UTC) | Mag | Depth (km) | Location | ID |
|------------|-----|------------|----------|----|
| 2024-02-03 | 5.1 | 3.0 | 8 km NW of Prague, OK | ok2024cish |
| 2024-01-13 | 4.3 | 6.7 | 6 km W of Arcadia, OK | ok2024awfn |
| 2024-01-13 | 4.1 | 6.6 | 6 km ENE of Edmond, OK | ok2024awva |
| ... | ... | ... | ... | ... |

**Summary:** 65 earthquakes of M2.5+ occurred within 200 km of Oklahoma City
in 2024, including a M5.1 event near Prague on Feb 3 — the largest Oklahoma
earthquake since the 2016 Pawnee M5.8. The Prague event had a shallow depth
of 3.0 km and 26,480 felt reports, consistent with injection-induced
seismicity in the Arbuckle Group disposal zone.

93% of events were shallower than 10 km, a key indicator of induced origin.
Magnitudes ranged from M2.5 to M5.1 with a mean of M3.0.

**Induced seismicity context:** Oklahoma seismicity peaked in 2015 with 900+
M3+ events/year, driven by Arbuckle Group saltwater disposal from
Mississippian Lime horizontal wells. Disposal volume reductions mandated by
the Oklahoma Corporation Commission have reduced event rates, but the region
remains seismically active above pre-2009 baseline levels.

*Cross-reference with `pnge:epa-enviro` (UIC Class II well locations) and
`pnge:eia-data` (disposal volumes) for injection-seismicity correlation.*

**Data quality:** Events are analyst-reviewed. USGS ComCat detection
threshold in Oklahoma is ~M1.0 due to dense OGS monitoring network. Data
is from the USGS Earthquake Hazards Program ComCat catalog.
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

Always use the `/count` endpoint first to determine total results:
```bash
COUNT=$(curl -s "https://earthquake.usgs.gov/fdsnws/event/1/count?starttime=2024-01-01&endtime=2024-12-31&minmagnitude=2.0&latitude=35.5&longitude=-97.5&maxradiuskm=200")
echo "Total events: $COUNT"
```

If count exceeds 5000, warn the user and ask if they want a filtered subset
or full paginated download.

---

## Error Handling

| HTTP Code | Meaning | Action |
|-----------|---------|--------|
| 200 | Success | Parse response normally |
| 204 | No content | No events match — widen filters or check parameters |
| 400 | Bad request | Invalid parameter — check error message, fix query |
| 404 | Not found | Endpoint typo — verify URL path |
| 409 | Conflict | Contradictory params (e.g., circle + rectangle) — use one location method |
| 429 | Rate limited | Too many requests — wait 60 seconds and retry |
| 503 | Service unavailable | USGS maintenance — retry after delay |

**Common mistakes:**
- Combining circle (lat/lon/radius) and rectangle (minlat/maxlat/minlon/maxlon)
  parameters — use one or the other, not both
- Requesting more than 20000 events without pagination
- Using `starttime` after `endtime`
- Omitting `format=geojson` (default is quakeml XML)

---

## Induced Seismicity Reference

### Key Indicators of Injection-Induced Earthquakes

1. **Shallow depth** — Induced events are typically < 10 km deep (often 2-8 km),
   corresponding to injection depth in disposal formations (Arbuckle, Ellenburger,
   basal clastics)
2. **Proximity to injection wells** — Events cluster within 5-15 km of high-volume
   disposal wells
3. **Temporal correlation** — Seismicity rate increases following increased injection
   volume with a lag of weeks to months
4. **Magnitude distribution** — Induced sequences often show b-values near 1.0 and
   can produce M4-5+ events
5. **Absence of pre-existing seismicity** — Many induced zones had no historical
   earthquake record before injection began

### Major U.S. Induced Seismicity Cases

| Region | Peak Period | Max Mag | Cause |
|--------|-------------|---------|-------|
| Oklahoma (Arbuckle) | 2014-2016 | M5.8 (Pawnee, 2016) | Mississippian Lime SWD |
| Permian Basin (TX/NM) | 2020-present | M5.3 (Mentone, 2020) | Permian horizontal SWD |
| Youngstown, OH | 2011-2012 | M4.0 | Marcellus SWD into Precambrian |
| Prague, OK | 2011 | M5.7 | Wilzetta Fault SWD |
| Trinidad, CO | 2001-2011 | M5.3 | CBM wastewater injection |
| Dallas-Fort Worth | 2008-2015 | M3.6 | Barnett Shale SWD |
| Guy-Greenbrier, AR | 2010-2011 | M4.7 | Fayetteville Shale SWD |

### Cross-References to Other Skills

- **`pnge:epa-enviro`** — UIC Class II injection well locations and permits.
  Query `UIC_WELL` table for disposal wells near earthquake clusters.
- **`pnge:eia-data`** — Disposal volume data. Route
  `petroleum/move/imp/data/` and state-level production data can provide
  injection volume context.
- **`pnge:fracfocus`** — Hydraulic fracturing disclosures. Correlate
  completion dates with seismicity onset.
- **`pnge:wvges-wells`** — WV well locations. Cross-reference with
  Appalachian earthquake locations.
- **`pnge:boem-offshore`** — Offshore production data for Gulf Coast
  disposal volume context.

---

## Caveats and Data Limitations

1. **Induced vs. tectonic classification:** The API does not reliably
   distinguish induced from tectonic events. The `eventtype` value
   `"induced or triggered event"` is rarely applied. Spatial proximity to
   injection wells and shallow depth are the primary indicators.

2. **Detection completeness varies by region:**
   - Oklahoma: complete to ~M1.0 (OGS dense network)
   - Permian Basin: complete to ~M1.5-2.0 (TexNet expanding)
   - Appalachian Basin: complete to ~M2.0-2.5
   - Rural/offshore: complete to ~M2.5-3.0

3. **Magnitude revisions:** Initial automatic magnitudes can shift 0.2-0.5
   units after analyst review. Use `reviewstatus=reviewed` for research data.

4. **Location accuracy:** Horizontal error is typically 1-5 km for
   well-monitored regions (OK, TX), 5-20 km elsewhere. Depth is the
   least constrained parameter — fixed-depth solutions (e.g., 5.0 km)
   indicate the depth was assumed, not computed.

5. **Temporal bias:** Monitoring networks have expanded significantly since
   2010. Pre-2010 catalogs undercount small events, making long-term trend
   comparisons unreliable below M3.0.

6. **Reporting lag:** Automatic locations appear within minutes; reviewed
   solutions may take hours to days. Very recent events may have
   preliminary magnitudes and locations.

---

## Implementation Notes

- **Prefer `bash_tool`** with `curl` + `jq` for API calls.
  Use `python3` (stdlib only: `urllib`, `json`) for complex analysis.
- **Python client** — see `references/python_example.py` for a full stdlib-only
  implementation with region presets, pagination, and formatted output.
- **GeoJSON coordinates** are `[longitude, latitude, depth]` — note the
  lon-before-lat order (GeoJSON standard, opposite of many mapping tools).
- **Time field** is Unix milliseconds, not seconds. Divide by 1000 for
  standard epoch conversion.
- **Count before query** — always hit `/count` first to gauge result size
  and avoid requesting unnecessarily large datasets.
- USGS updates: events appear within minutes (automatic), reviewed within
  hours to days. No scheduled bulk update cycle.
