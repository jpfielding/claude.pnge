# USGS Publications Warehouse API Reference

## Base URL

```
https://pubs.usgs.gov/pubs-services/publication
```

Note: The older hostname `pubs.er.usgs.gov` redirects (301) to `pubs.usgs.gov`.
Always use the canonical `pubs.usgs.gov` base.

No API key is required. No authentication headers needed.

---

## Endpoints

### Search Publications

```
GET https://pubs.usgs.gov/pubs-services/publication?{params}
```

Returns a paginated list of publications matching the query.

### Get Single Publication

```
GET https://pubs.usgs.gov/pubs-services/publication/{indexId}
```

Returns the full record for a single publication. The `indexId` is a string
identifier like `fs20243052`, `sir20245102`, or a numeric ID like `70261664`.

---

## Search Parameters

| Parameter            | Type   | Description                                                      | Example                                    |
|----------------------|--------|------------------------------------------------------------------|--------------------------------------------|
| `q`                  | string | Free-text keyword search (title, abstract, authors, etc.)        | `q=lithium+produced+water`                 |
| `title`              | string | Search within title only                                         | `title=critical+minerals`                  |
| `year`               | string | Filter by publication year                                       | `year=2024`                                |
| `typeName`           | string | Filter by publication type                                       | `typeName=Report`                          |
| `subtypeName`        | string | Filter by publication subtype                                    | `subtypeName=USGS+Numbered+Series`         |
| `contributingOffice` | string | Filter by USGS cost center or office                             | `contributingOffice=Eastern+Energy+Resources+Science+Center` |
| `pub_x_days`         | int    | Publications released in the last X days                         | `pub_x_days=30`                            |
| `page_size`          | int    | Results per page (default varies, max ~100)                      | `page_size=25`                             |
| `page_number`        | int    | Page number for pagination (1-indexed)                           | `page_number=2`                            |

### Combining Parameters

Parameters are combined with `&`. All filters are AND-joined:

```
?q=lithium&typeName=Report&year=2024&page_size=10
```

---

## Publication Types

Values for the `typeName` parameter:

| typeName    | Description                                |
|-------------|--------------------------------------------|
| `Report`    | USGS reports (Fact Sheets, SIRs, OFRs, etc.) |
| `Article`   | Journal articles with USGS authors          |

## Publication Subtypes

Values for the `subtypeName` parameter:

| subtypeName            | Description                                            |
|------------------------|--------------------------------------------------------|
| `USGS Numbered Series` | Official USGS series (FS, SIR, OFR, PP, DS, etc.)     |
| `Journal Article`      | Peer-reviewed journal publications with USGS authors   |

## USGS Numbered Series Titles

Within `USGS Numbered Series`, the `seriesTitle.text` field identifies the
specific series:

| Series Title                    | Code | Description                                     |
|---------------------------------|------|-------------------------------------------------|
| Fact Sheet                      | FS   | Short (2-6 page) summaries for general audience |
| Scientific Investigations Report| SIR  | Detailed scientific studies                      |
| Open-File Report                | OFR  | Preliminary or specialized data/reports          |
| Professional Paper              | PP   | Comprehensive scientific investigations          |
| Data Series                     | DS   | Data compilations and releases                   |
| Circular                        | CIR  | General interest science summaries               |
| Techniques and Methods          | TM   | Methodological documentation                     |
| Water-Resources Investigations Report | WRIR | (Historical) Water resources studies        |

---

## Response Format

### Search Response (list)

```json
{
  "pageNumber": "1",
  "pageRowStart": "0",
  "pageSize": "25",
  "recordCount": 50,
  "records": [ ... ]
}
```

| Field          | Type   | Description                                |
|----------------|--------|--------------------------------------------|
| `pageNumber`   | string | Current page (1-indexed)                   |
| `pageRowStart` | string | Zero-based index of first record on page   |
| `pageSize`     | string | Requested page size                        |
| `recordCount`  | int    | Total matching records across all pages     |
| `records`      | array  | Array of publication record objects          |

### Single Publication Record

Key fields in each record object:

| Field                | Type   | Description                                           |
|----------------------|--------|-------------------------------------------------------|
| `id`                 | int    | Numeric publication ID                                |
| `indexId`            | string | String identifier (e.g., `fs20243052`)                |
| `title`              | string | Publication title                                     |
| `displayTitle`       | string | Title with proper capitalization                      |
| `docAbstract`        | string | Abstract (may contain HTML markup)                    |
| `publicationType`    | object | `{id, text}` — e.g., `"Report"` or `"Article"`       |
| `publicationSubtype` | object | `{id, text}` — e.g., `"USGS Numbered Series"`        |
| `seriesTitle`        | object | `{id, text, code}` — e.g., `{text: "Fact Sheet", code: "FS"}` |
| `seriesNumber`       | string | Series number (e.g., `"2024-3052"`)                   |
| `publicationYear`    | string | Year of publication                                   |
| `publicationDate`    | string | Full date `YYYY-MM-DD`                                |
| `doi`                | string | DOI (e.g., `10.3133/fs20243052`)                      |
| `language`           | string | Language (usually `"English"`)                        |
| `publisher`          | string | Publisher name                                        |
| `publisherLocation`  | string | Publisher city/state                                  |
| `usgsCitation`       | string | Full USGS-formatted citation string                   |
| `productDescription` | string | Brief description (e.g., `"Report: 4 p."`)           |
| `numberOfPages`      | string | Page count                                            |
| `country`            | string | Geographic focus country                              |
| `state`              | string | Geographic focus state(s), comma-separated            |
| `geographicExtents`  | string | GeoJSON string of geographic bounding polygon         |
| `costCenters`        | array  | USGS offices/programs, each `{id, text}`              |
| `contributors`       | object | `{authors: [{family, given, orcid, usgs, ...}]}`     |
| `links`              | array  | Download/access links (see below)                     |
| `lastModifiedDate`   | string | ISO 8601 timestamp of last update                     |
| `displayToPublicDate`| string | ISO 8601 timestamp when made public                   |
| `ipdsId`             | string | Internal USGS tracking ID                             |

### Links Array

Each link object:

```json
{
  "id": 499937,
  "rank": 0,
  "type": {"id": 11, "text": "Document"},
  "url": "https://pubs.usgs.gov/fs/2024/3052/fs20243052.pdf",
  "text": ""
}
```

Common link types:

| type.text                       | Description                            |
|---------------------------------|----------------------------------------|
| `Document`                      | PDF download of the publication        |
| `HTML Document`                 | Full-text HTML version                 |
| `Thumbnail`                     | Cover image thumbnail                  |
| `Data Release`                  | Associated data release (DOI link)     |
| `Related Work`                  | Related publications                   |
| `Open Access Publisher Index Page` | External journal publisher page     |
| `NGMDB Index Page`              | National Geologic Map Database entry   |
| `Publication XML`               | XML version of the publication         |
| `Image Folder`                  | Directory of publication images        |

---

## Pagination

Results are paginated. Use `page_size` and `page_number` together:

```bash
# Page 1 (default)
curl -sL "https://pubs.usgs.gov/pubs-services/publication?q=lithium&page_size=25"

# Page 2
curl -sL "https://pubs.usgs.gov/pubs-services/publication?q=lithium&page_size=25&page_number=2"
```

Check `recordCount` in the response to determine total pages:
`total_pages = ceil(recordCount / page_size)`

---

## Example Requests

### Keyword search
```bash
curl -sL "https://pubs.usgs.gov/pubs-services/publication?q=lithium+produced+water&page_size=10"
```

### Reports only, filtered by year
```bash
curl -sL "https://pubs.usgs.gov/pubs-services/publication?q=lithium&typeName=Report&year=2024&page_size=10"
```

### USGS Numbered Series only
```bash
curl -sL "https://pubs.usgs.gov/pubs-services/publication?q=critical+minerals&subtypeName=USGS+Numbered+Series&page_size=10"
```

### Recent publications (last 30 days)
```bash
curl -sL "https://pubs.usgs.gov/pubs-services/publication?pub_x_days=30&page_size=25"
```

### Title search
```bash
curl -sL "https://pubs.usgs.gov/pubs-services/publication?title=produced+water+geochemistry&page_size=10"
```

### Get specific publication by indexId
```bash
curl -sL "https://pubs.usgs.gov/pubs-services/publication/fs20243052"
```

### Get specific publication by numeric ID
```bash
curl -sL "https://pubs.usgs.gov/pubs-services/publication/70261664"
```

### By contributing office
```bash
curl -sL "https://pubs.usgs.gov/pubs-services/publication?q=lithium&contributingOffice=Eastern+Energy+Resources+Science+Center&page_size=10"
```

---

## Rate Limits

No published rate limits. The API is public and unauthenticated. Use reasonable
request rates (no more than a few requests per second) to avoid being blocked.

## Data Currency

The Publications Warehouse is updated continuously as USGS publications are
approved and released. Use `pub_x_days` to find the most recently released
publications. The `lastModifiedDate` field on each record shows when metadata
was last updated.
