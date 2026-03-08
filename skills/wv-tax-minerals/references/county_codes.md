# WV County FIPS Codes and Target County Statistics

## All 55 WV Counties — FIPS Code Mapping

| FIPS | County | FIPS | County | FIPS | County |
|------|--------|------|--------|------|--------|
| 001 | Barbour | 021 | Gilmer | 041 | Lewis |
| 003 | Berkeley | 023 | Grant | 043 | Lincoln |
| 005 | Boone | 025 | Greenbrier | 045 | Logan |
| 007 | Braxton | 027 | Hampshire | 047 | McDowell |
| 009 | Brooke | 029 | Hancock | 049 | Marion |
| 011 | Cabell | 031 | Hardy | 051 | Marshall |
| 013 | Calhoun | 033 | Harrison | 053 | Mason |
| 015 | Clay | 035 | Jackson | 055 | Mercer |
| 017 | Doddridge | 037 | Jefferson | 057 | Mineral |
| 019 | Fayette | 039 | Kanawha | 059 | Mingo |
| 061 | Monongalia | 077 | Preston | 093 | Tucker |
| 063 | Monroe | 079 | Putnam | 095 | Tyler |
| 065 | Morgan | 081 | Raleigh | 097 | Upshur |
| 067 | Nicholas | 083 | Randolph | 099 | Wayne |
| 069 | Ohio | 085 | Ritchie | 101 | Webster |
| 071 | Pendleton | 087 | Roane | 103 | Wetzel |
| 073 | Pleasants | 089 | Summers | 105 | Wirt |
| 075 | Pocahontas | 091 | Taylor | 107 | Wood |
|     |          |      |          | 109 | Wyoming |

**State FIPS prefix:** 54 (e.g., Marshall County = 54051)

**API number prefix:** 47 (e.g., a Marshall County well API = 47-049-XXXXX)

---

## 8 Target Counties — Northern WV Marcellus/Utica Play

These counties have significant overlap between active Marcellus/Utica
horizontal drilling and the severed mineral estate system, making them
prime targets for delinquent mineral property analysis.

| FIPS | County | Region | Approx Parcels | Delinquent | Active Wells | Notes |
|------|--------|--------|----------------|------------|--------------|-------|
| 017 | Doddridge | Central | ~15,000 | ~200 | ~1,800 | Major EQT/Antero acreage |
| 033 | Harrison | North-Central | ~45,000 | ~600 | ~2,500 | Most active conventional + unconventional |
| 049 | Marion | North-Central | ~35,000 | ~400 | ~1,200 | Fairmont area, mixed conventional/unconventional |
| 051 | Marshall | Northern Panhandle | ~20,000 | ~300 | ~3,300 | Highest density horizontal wells |
| 069 | Ohio | Northern Panhandle | ~25,000 | ~250 | ~800 | Wheeling area, legacy oil/gas |
| 095 | Tyler | West-Central | ~8,000 | ~150 | ~1,100 | Validated test case county |
| 097 | Upshur | Central | ~14,000 | ~200 | ~900 | Buckhannon area |
| 103 | Wetzel | Northwest | ~12,000 | ~250 | ~1,500 | Active Marcellus play |

**Notes on counts:**
- Parcel counts are approximate and include all property types (surface, mineral, combined)
- Delinquent counts are statewide Delinquent_Properties layer records for that county
- Active well counts are from WVDEP Layer 7 where `wellstatus='Active Well'`
- Counts will vary as data is updated; use live queries for current numbers

---

## County Name Variations

The `county` field in ParcelSummary uses full county names (e.g., "Marshall"),
while Delinquent_Properties also uses full names. The WVDEP wells layer uses
3-digit FIPS codes. When joining across sources, map between these formats.

| Source | Field | Format | Example |
|--------|-------|--------|---------|
| ParcelSummary (Table 11) | `CountyName` | Full name | "Marshall" |
| Delinquent_Properties | `county` | Full name | "Marshall" |
| WVDEP Wells (Layer 7) | `county` | 3-digit FIPS | "051" |
| API Number | positions 3-5 | 3-digit FIPS | "049" (in 47-049-XXXXX) |
