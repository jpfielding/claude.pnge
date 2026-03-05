# DOE OSTI API v1 Reference

## Base URL

```
https://www.osti.gov/api/v1/records
```

No API key required for public searches. All DOE-funded research is publicly
accessible.

---

## Search Parameters

| Parameter       | Type   | Example                             | Description                                          |
|-----------------|--------|-------------------------------------|------------------------------------------------------|
| `q`             | string | `q=lithium+produced+water`          | Full-text keyword search across all fields            |
| `title`         | string | `title=lithium+extraction`          | Search within title field only                        |
| `author`        | string | `author=Stuckman`                   | Search by author last name                            |
| `sponsor_org`   | string | `sponsor_org=NETL`                  | Filter by DOE sponsoring organization                 |
| `research_org`  | string | `research_org=National+Energy`      | Filter by performing research organization            |
| `product_type`  | string | `product_type=Technical+Report`     | Filter by publication type (see table below)          |
| `rows`          | int    | `rows=20`                           | Results per page (default: 20, max: not documented)   |
| `page`          | int    | `page=2`                            | Page number for pagination (1-indexed)                |

### Date Parameters (Currently Unreliable)

The following parameters are documented but return HTTP 500 errors as of
March 2026. Use keyword searches with year terms as a workaround:

| Parameter                  | Type   | Description                    |
|----------------------------|--------|--------------------------------|
| `publication_date_start`   | string | Start of publication date range |
| `publication_date_end`     | string | End of publication date range   |
| `entry_date_start`         | string | Start of entry date range       |
| `entry_date_end`           | string | End of entry date range         |

**Workaround:** Include the year in the keyword query, e.g. `q=lithium+2024`.

---

## Single Record Lookup

Retrieve a specific record by OSTI ID in the URL path:

```
GET https://www.osti.gov/api/v1/records/{osti_id}
```

Example:
```bash
curl -s "https://www.osti.gov/api/v1/records/2588655" \
  -H "Accept: application/json"
```

Returns a JSON array with one element (the matching record).

---

## Response Format

### Response Body

The response is a **flat JSON array** of record objects (no wrapper). Example:

```json
[
  {
    "osti_id": "2588655",
    "title": "Producing Dollars from Produced Water: ...",
    "authors": ["Stuckman, Mengling [NETL] (ORCID:0000000349865024)"],
    "publication_date": "2025-09-17T04:00:00Z",
    "product_type": "Conference",
    "doi": "10.2172/2588655",
    "description": "Recent studies have shown...",
    "subjects": ["critical minerals, lithium", "oil & gas"],
    "sponsor_orgs": ["USDOE Office of Fossil Energy and Carbon Management (FECM)"],
    "research_orgs": ["National Energy Technology Laboratory (NETL)..."],
    "links": [
      {"rel": "citation", "href": "https://www.osti.gov/biblio/2588655"},
      {"rel": "fulltext", "href": "https://www.osti.gov/servlets/purl/2588655"}
    ],
    "language": "English",
    "country_publication": "United States",
    "entry_date": "2025-09-18T02:00:11Z",
    "report_number": "None",
    "contract_number": "...",
    "doe_contract_number": "..."
  }
]
```

### Response Headers (Important)

| Header               | Description                                  | Example                |
|----------------------|----------------------------------------------|------------------------|
| `X-Total-Count`      | Total number of matching records             | `35431`                |
| `Link`               | Pagination links (RFC 5988)                  | See below              |
| `X-Rate-Limit-Remaining` | Remaining requests in current window    | `0`                    |

**Link header example:**
```
<https://www.osti.gov/api/v1/records?q=lithium&page=2&rows=20>; rel="next",
<https://www.osti.gov/api/v1/records?q=lithium&page=1772&rows=20>; rel="last"
```

---

## Record Fields

### Core Fields (present on most records)

| Field                | Type     | Description                                      |
|----------------------|----------|--------------------------------------------------|
| `osti_id`            | string   | Unique OSTI identifier                           |
| `title`              | string   | Publication title (may contain HTML tags)         |
| `authors`            | string[] | Author names with affiliations and ORCIDs        |
| `publication_date`   | string   | ISO 8601 timestamp                               |
| `product_type`       | string   | Type of publication (see table below)            |
| `description`        | string   | Abstract or summary (may contain HTML)           |
| `doi`                | string   | Digital Object Identifier                        |
| `subjects`           | string[] | Subject categories and keywords                  |
| `sponsor_orgs`       | string[] | DOE sponsoring organizations                     |
| `research_orgs`      | string[] | Performing research organizations                |
| `links`              | object[] | Citation and fulltext download links             |
| `language`           | string   | Publication language                             |
| `country_publication`| string   | Country of publication                           |
| `entry_date`         | string   | Date record was entered into OSTI                |

### Additional Fields (present on some records)

| Field                   | Type   | Description                                    |
|-------------------------|--------|------------------------------------------------|
| `report_number`         | string | DOE report number                              |
| `contract_number`       | string | Contract or grant number                       |
| `doe_contract_number`   | string | DOE-specific contract number                   |
| `doe_funded_flag`       | string | "Y" if DOE-funded                              |
| `journal_name`          | string | Journal name (for journal articles)            |
| `journal_volume`        | string | Journal volume                                 |
| `journal_issue`         | string | Journal issue                                  |
| `journal_issn`          | string | Journal ISSN                                   |
| `article_type`          | string | Article subtype                                |
| `relation`              | string | Journal citation metadata                      |
| `identifier`            | string | Additional identifiers                         |
| `other_number`          | string | Other reference numbers                        |
| `nondoe_contract_number`| string | Non-DOE funding source numbers                 |
| `publisher`             | string | Publisher name                                 |

---

## Product Types

| Product Type          | Description                                              |
|-----------------------|----------------------------------------------------------|
| `Technical Report`    | DOE-funded technical reports from labs and contractors    |
| `Journal Article`     | Peer-reviewed journal articles acknowledging DOE funding |
| `Conference`          | Conference papers and presentations                      |
| `Thesis/Dissertation` | Graduate theses funded by DOE                            |
| `Book`                | Books or book chapters                                   |
| `Patent`              | DOE-related patents                                      |
| `Program Document`    | Program plans and management documents                   |
| `Miscellaneous`       | Other publication types                                  |

---

## Links Object

Each record has a `links` array with one or more entries:

| `rel` Value        | Description                                           |
|---------------------|------------------------------------------------------|
| `citation`          | OSTI bibliographic page (`/biblio/{osti_id}`)        |
| `fulltext`          | Full-text download if available (`/servlets/purl/`)  |
| `citation_doe_pages`| DOE PAGES journal article citation                   |

---

## Common Sponsor Organizations

| Short Name | Full Name                                                          |
|------------|--------------------------------------------------------------------|
| NETL       | USDOE National Energy Technology Laboratory (NETL)                 |
| FECM       | USDOE Office of Fossil Energy and Carbon Management (FECM)        |
| EERE       | USDOE Office of Energy Efficiency and Renewable Energy (EERE)      |
| AMMTO      | EERE Advanced Manufacturing and Materials Technologies Office      |
| BES        | USDOE Office of Science, Basic Energy Sciences (BES)               |
| NNSA       | USDOE National Nuclear Security Administration (NNSA)              |

---

## Rate Limiting

The API includes rate limiting via the `X-Rate-Limit-Remaining` header.
When exhausted, wait and retry. No documentation on specific limits, but
moderate query rates (a few requests per second) are generally fine.

---

## Error Responses

Error responses are JSON objects (not arrays):

```json
{
  "statusCode": 500,
  "statusMessage": "Internal Server Error",
  "errorDescription": "There was an internal error processing your request..."
}
```

| HTTP Code | Meaning              | Common Cause                              |
|-----------|----------------------|-------------------------------------------|
| 200       | Success              | Results returned as JSON array            |
| 400       | Bad Request          | Malformed query parameter                 |
| 404       | Not Found            | Invalid OSTI ID in path                   |
| 500       | Internal Server Error| Date filter parameters, server-side bugs  |

---

## Example Curl Commands

```bash
# Keyword search
curl -s "https://www.osti.gov/api/v1/records?q=lithium+produced+water&rows=10" \
  -H "Accept: application/json"

# Title search
curl -s "https://www.osti.gov/api/v1/records?title=direct+lithium+extraction&rows=10" \
  -H "Accept: application/json"

# Author search
curl -s "https://www.osti.gov/api/v1/records?author=Stuckman&rows=10" \
  -H "Accept: application/json"

# Filter by NETL sponsor
curl -s "https://www.osti.gov/api/v1/records?q=lithium&sponsor_org=NETL&rows=10" \
  -H "Accept: application/json"

# Filter by product type
curl -s "https://www.osti.gov/api/v1/records?q=lithium&product_type=Technical+Report&rows=10" \
  -H "Accept: application/json"

# Single record by OSTI ID
curl -s "https://www.osti.gov/api/v1/records/2588655" \
  -H "Accept: application/json"

# Pagination (page 2, 20 results per page)
curl -s "https://www.osti.gov/api/v1/records?q=lithium+brine&rows=20&page=2" \
  -H "Accept: application/json"

# Combine multiple filters
curl -s "https://www.osti.gov/api/v1/records?q=critical+minerals+produced+water&sponsor_org=NETL&product_type=Technical+Report&rows=10" \
  -H "Accept: application/json"

# Get total count from headers
curl -si "https://www.osti.gov/api/v1/records?q=lithium+produced+water&rows=1" \
  -H "Accept: application/json" 2>&1 | grep "X-Total-Count"
```
