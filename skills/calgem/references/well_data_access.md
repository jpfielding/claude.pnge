# CalGEM Well Data Access — Detailed Reference

Operational reference for querying the CalGEM/WellSTAR ArcGIS REST API,
understanding field vocabularies, and knowing when to fall back to bulk files.

## REST Endpoint Map

Root: `https://gis.conservation.ca.gov/server/rest/services/`

### WellSTAR folder (well-level data)

| Service | URL | Purpose |
|---------|-----|---------|
| Wells | `WellSTAR/Wells/MapServer` | Oil/gas + geothermal wells (2 layers) |
| Facilities | `WellSTAR/Facilities/MapServer` | Tank batteries, compressors, plants |
| Incidents | `WellSTAR/Incidents/MapServer` | Spills, leaks, well control events |
| Notices | `WellSTAR/Notices/MapServer` | Notice of Intention (NOI) filings |
| UGS | `WellSTAR/UGS/MapServer` | Underground gas storage fields |
| WST | `WellSTAR/WST/MapServer` | Additional WellSTAR layers |

### CalGEM folder (administrative and environmental overlays)

| Service | URL | Purpose |
|---------|-----|---------|
| Admin_Bounds | `CalGEM/Admin_Bounds/MapServer` | Administrative boundaries |
| CalGEM_Districts | `CalGEM/CalGEM_Districts/MapServer` | D1-D6 district polygons |
| Places | `CalGEM/Places/MapServer` | Oil/gas field polygons |
| Places_County | `CalGEM/Places_County/MapServer` | Field polygons clipped to counties |
| Primacy_Aquifer_Exemptions | `CalGEM/Primacy_Aquifer_Exemptions/MapServer` | Pre-1983 EPA aquifer exemptions |
| Post_Primacy_Aquifer_Exemptions | `CalGEM/Post_Primacy_Aquifer_Exemptions/MapServer` | Post-1983 AEs |
| DOMS_Admin_Bounds | `CalGEM/DOMS_Admin_Bounds/FeatureServer` | DOMS (Designated Operator Monitoring System) |
| TR26_Seep_Service | `CalGEM/TR26_Seep_Service/MapServer` | Testing and Regulation 26 seep monitoring |

## Standard Query Parameters (ArcGIS REST)

| Parameter | Default | Notes |
|-----------|---------|-------|
| `where` | `1=1` | SQL WHERE clause; fields are case-sensitive |
| `outFields` | `*` | Comma-separated field names or `*` |
| `returnGeometry` | `true` | Set `false` for tabular output (faster) |
| `geometry` | | Spatial filter; `minX,minY,maxX,maxY` for envelope |
| `geometryType` | `esriGeometryEnvelope` | Also: Point, Polygon, Polyline |
| `inSR` | map SR | Input spatial reference (e.g. `4326` for WGS84) |
| `outSR` | map SR | Output SR |
| `spatialRel` | `esriSpatialRelIntersects` | Also Contains, Within, Crosses |
| `resultRecordCount` | up to 5000 | Page size |
| `resultOffset` | 0 | For pagination |
| `orderByFields` | none | e.g., `SpudDate DESC` |
| `returnCountOnly` | false | Just return the count |
| `f` | `html` | Use `json`, `geojson`, or `pbf` for machine output |

## Pagination Pattern

```bash
#!/usr/bin/env bash
set -euo pipefail

BASE="https://gis.conservation.ca.gov/server/rest/services/WellSTAR/Wells/MapServer/0/query"
WHERE="CountyName='Kern' AND WellType='Water Disposal'"

OFFSET=0
PAGE=5000
TOTAL=$(curl -s "$BASE" \
  --data-urlencode "where=$WHERE" \
  --data-urlencode "returnCountOnly=true" \
  --data-urlencode "f=json" | jq -r .count)

echo "Total matching: $TOTAL"

while [ "$OFFSET" -lt "$TOTAL" ]; do
  echo "Fetching offset=$OFFSET"
  curl -s "$BASE" \
    --data-urlencode "where=$WHERE" \
    --data-urlencode "outFields=*" \
    --data-urlencode "returnGeometry=false" \
    --data-urlencode "resultOffset=$OFFSET" \
    --data-urlencode "resultRecordCount=$PAGE" \
    --data-urlencode "orderByFields=API" \
    --data-urlencode "f=json" >> kern_disposal.ndjson
  OFFSET=$((OFFSET + PAGE))
done
```

## Layer 0 (Well) — Field Vocabularies

### `WellStatus` values
- `Active` — producing / injecting currently
- `Idle` — inactive but not plugged
- `Plugged` — permanently plugged and abandoned
- `New` — permitted/drilling not yet producing
- `Cancelled` — permit cancelled without drilling
- `Buried` — plugged and surface-abandoned (historic)

### `WellType` values (common)
- `Oil & Gas` — dual-phase production
- `Dry Gas` — gas-only
- `Liquid Gas`
- `Water Disposal` — Class II disposal
- `Waterflood` — Class II EOR injection (water)
- `Steamflood` — Class II EOR injection (steam, heavy-oil recovery)
- `Observation` — monitoring well
- `Pressure Maintenance`
- `Cyclic Steam` — huff-n-puff steam injection
- `Fuel Gas Storage`
- `Air Injection`
- `Water Source`
- `Geothermal` (Layer 1 only)

### `District` values
`D1` through `D6`, sometimes also returned as the integer `1`-`6` depending
on which layer you query.

## Layer 1 (Geothermal Well) — Differences from Layer 0

- Uses `APINumber` (not `API`)
- `WellStatusDescription` adds human-readable status
- `GeoDistrict` separates geothermal district numbering
- Coordinates in `Lat83`/`Long83` (NAD83) rather than `Latitude`/`Longitude`
- `ABDdate` and `CompDate` fields present (abandonment and completion dates)

## CalWIMS → WellSTAR Migration

As of 2026-04, the `wims.conservation.ca.gov` domain redirects to the CalGEM
portal. CalWIMS (the California Well Information Management System) was the
pre-2018 public interface. Its functions are now served by:

- **Well data** → WellSTAR/Wells REST layers
- **Production queries** → bulk monthly operator reports at
  `conservation.ca.gov/calgem` (path changes; search the site)
- **Well records / PDFs** → File Request system at
  `filerequest.conservation.ca.gov`

If a user requests "CalWIMS data" explicitly, acknowledge the migration and
serve the request from WellSTAR plus file requests as needed.

## Cross-referencing with Other Data

### USGS Produced Waters Database (v3.0)

Join on `API` (CalGEM Layer 0) to `API_NUMBER` (USGS DB). California API
numbers in USGS may be prefixed `04-` (state FIPS) — strip the prefix for
joins.

### EPA Envirofacts UIC_WELL

Join via API or by operator + field. California is a Class II primacy state,
so CalGEM is the primary regulator and EPA records are secondary. Expect
incomplete EPA coverage.

### SB 1281 Produced Water Reporting

SB 1281 data is published separately from WellSTAR — look for
"SB 1281 quarterly report" XLS files on the CalGEM website. Use case for
`pnge:epa-regulatory` cross-check.

## County Code Reference (California API first 3 digits)

| Code | County | Notes |
|------|--------|-------|
| 001 | Alameda | |
| 025 | Imperial | **Salton Sea KGRA** |
| 029 | Kern | **Largest oilfield district** |
| 031 | Kings | |
| 037 | Los Angeles | Historic Wilmington, Inglewood, etc. |
| 039 | Madera | |
| 053 | Monterey | |
| 073 | San Diego | |
| 079 | San Luis Obispo | |
| 081 | San Mateo | |
| 083 | Santa Barbara | Ellwood, offshore state |
| 087 | Santa Cruz | |
| 097 | Sonoma | **The Geysers geothermal** |
| 099 | Stanislaus | |
| 107 | Tulare | |
| 111 | Ventura | |

## Rate Limits and Best Practices

- No documented rate limit, but respect `maxRecordCount=5000`
- Always use `returnCountOnly=true` before large pulls
- Add `returnGeometry=false` when you do not need coordinates
- Cache locally when running repeated analyses
- Identify your client with a `User-Agent` header for etiquette
- If you see 503 / 504, back off and retry with jitter
