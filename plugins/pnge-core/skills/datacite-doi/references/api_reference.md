# DataCite REST API Reference

**Base URL:** `https://api.datacite.org/`
**Spec:** JSON:API 1.0 — always send `Accept: application/vnd.api+json`
**Auth:** None required for read endpoints.

## Endpoints

### `GET /dois`

List / search DOIs. Full-text search plus facet filters.

**Query parameters:**

| Name               | Type    | Notes |
|--------------------|---------|-------|
| `query`            | string  | Lucene syntax. Spaces → AND by default. |
| `client-id`        | string  | Lowercase symbolic ID (e.g. `usgs.prod`). |
| `provider-id`      | string  | Consortium ID (e.g. `usgs`). |
| `resource-type-id` | string  | `dataset`, `text`, `software`, `image`, `audiovisual`, `collection`, `model`, `service`, `workflow`, `physicalobject`, `other` |
| `publication-year` | int     | Single year. For ranges use `query=publicationYear:[2020 TO 2024]` |
| `affiliation-id`   | string  | ROR ID of an author affiliation |
| `subject`          | string  | Controlled subject term |
| `schema-version`   | string  | `3`, `4`, or `4.5` |
| `page[number]`     | int     | 1-indexed. URL-encode brackets. |
| `page[size]`       | int     | Default 25, max 1000. |
| `sort`             | string  | `created`, `-created`, `updated`, `-updated`, `title`, etc. |
| `random`           | bool    | `true` returns a random sample (non-reproducible). |

**Lucene cheatsheet** (applied to `query=`):

- `titles.title:"produced water"` — phrase match in title
- `creators.name:Bradley` — author surname
- `publicationYear:[2020 TO 2024]` — range
- `types.resourceTypeGeneral:Dataset` — exact vocabulary match
- `subjects.subject:lithium OR subjects.subject:brine` — boolean
- Escape `: ( ) [ ] { } " \` with backslashes.

### `GET /dois/{doi}`

Resolve a single DOI. Case-insensitive. Returns 404 if not in DataCite.

### `GET /clients`

Search repositories (data-publishing clients). Use to discover the
symbolic `client-id` to filter `/dois` by.

| Param         | Notes |
|---------------|-------|
| `query`       | Free text; matches name, description, URL |
| `provider-id` | Filter to a provider's clients |
| `page[size]`  | Default 25, max 1000 |

Returns records like:

```json
{"id": "usgs.prod", "attributes": {"name": "USGS DOI Tool Production Environment", "year": 2012, "contactEmail": "...", "repositoryUrl": "..."}}
```

### `GET /providers`

Search provider organizations (funders, consortia). Examples: `usgs`,
`doe`, `cern`, `crossref`.

### `GET /resource-types`

Enumerate the controlled vocabulary for `resourceTypeGeneral`.

---

## Response Envelope

Every list endpoint returns:

```json
{
  "data": [ /* array of resource objects */ ],
  "meta": {
    "total": 1234,
    "totalPages": 50,
    "page": 1,
    "states": [ /* facet counts */ ],
    "resourceTypes": [ /* facet counts */ ],
    "years": [ /* facet counts by publicationYear */ ]
  },
  "links": {
    "self": "...",
    "next": "...",
    "last": "..."
  }
}
```

`meta` includes aggregated facets — useful for follow-up queries without
a second round-trip.

---

## DOI Resource Shape

```json
{
  "id": "10.5066/p9zkrwqf",
  "type": "dois",
  "attributes": {
    "doi": "10.5066/P9ZKRWQF",
    "prefix": "10.5066",
    "suffix": "P9ZKRWQF",
    "identifiers": [],
    "alternateIdentifiers": [],
    "creators": [
      {
        "name": "Bradley, Dwight C.",
        "nameType": "Personal",
        "givenName": "Dwight C.",
        "familyName": "Bradley",
        "affiliation": [{"name": "U.S. Geological Survey"}],
        "nameIdentifiers": [{"schemeUri": "https://orcid.org", "nameIdentifier": "..."}]
      }
    ],
    "titles": [{"title": "Lithium Deposits in the United States", "titleType": null, "lang": "en"}],
    "publisher": "U.S. Geological Survey",
    "publicationYear": 2019,
    "subjects": [{"subject": "lithium", "schemeUri": null}],
    "contributors": [],
    "dates": [{"date": "2019-06-24", "dateType": "Issued"}],
    "language": "en",
    "types": {
      "ris": "DATA",
      "bibtex": "misc",
      "citeproc": "dataset",
      "schemaOrg": "Dataset",
      "resourceType": "Data Release",
      "resourceTypeGeneral": "Dataset"
    },
    "relatedIdentifiers": [
      {"relatedIdentifier": "10.3133/ofr20191137", "relatedIdentifierType": "DOI", "relationType": "IsSupplementTo"}
    ],
    "sizes": ["1 digital dataset"],
    "formats": ["CSV", "SHP"],
    "version": "1.0",
    "rightsList": [{"rights": "Public Domain", "rightsUri": "..."}],
    "descriptions": [
      {"description": "This data release provides...", "descriptionType": "Abstract", "lang": "en"}
    ],
    "geoLocations": [
      {"geoLocationBox": {"westBoundLongitude": -125, "eastBoundLongitude": -66, "southBoundLatitude": 24, "northBoundLatitude": 49}}
    ],
    "fundingReferences": [],
    "url": "https://www.sciencebase.gov/catalog/item/5d0baffce4b0e3d31162044c",
    "contentUrl": null,
    "metadataVersion": 3,
    "schemaVersion": "http://datacite.org/schema/kernel-4",
    "source": "api",
    "isActive": true,
    "state": "findable",
    "reason": null,
    "viewCount": 0,
    "downloadCount": 0,
    "citationCount": 0,
    "created": "2019-06-24T00:00:00.000Z",
    "registered": "2019-06-24T00:00:00.000Z",
    "published": "2019",
    "updated": "2024-03-15T12:00:00.000Z"
  },
  "relationships": {
    "client": {"data": {"id": "usgs.prod", "type": "clients"}},
    "provider": {"data": {"id": "usgs", "type": "providers"}},
    "media": {"data": [...]}
  }
}
```

---

## Key Clients for PNGE Research

Verified against the live API (date of last check embedded in skill build).
If any lookup fails, refresh with `GET /clients?query=<repository-name>`.

| client-id       | Name                                                | Notes |
|-----------------|-----------------------------------------------------|-------|
| `usgs.prod`     | USGS DOI Tool Production                             | All 10.5066 data releases |
| `xaqp.zqnehk`   | SESAR_USGS                                          | USGS sample registry |
| `pryl.mxfyrs`   | NGGDPP                                              | Drill cores, well logs |
| `doe.osti`      | DOE Office of Scientific & Technical Information    | OSTI reports and datasets |
| `cern.zenodo`   | Zenodo                                              | General research data + software |

Figshare, Dryad, and provider-level USGS queries each require a fresh
client-id lookup — the symbolic IDs change whenever a repository
re-registers.

---

## Rate Limits

- Unauthenticated: ~3,000 requests per 5 minutes per IP.
- Deep pagination (`page[number] > 200`) may 429 even well under the
  window; use filters to narrow instead of walking the tail.
- `Retry-After` header is populated on 429 responses.

---

## Common Query Recipes

```
# All USGS data releases mentioning "brine" since 2020
?query=brine+publicationYear:[2020 TO *]&client-id=usgs.prod&page%5Bsize%5D=100

# Datasets (any repo) with DOE funding about produced water
?query=produced+water+AND+fundingReferences.funderName:DOE&resource-type-id=dataset

# Recently updated records in a given prefix
?query=prefix:10.11578&sort=-updated&page%5Bsize%5D=25

# Zenodo software releases tagged "lithium extraction"
?query=lithium+extraction&client-id=cern.zenodo&resource-type-id=software
```
