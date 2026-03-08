# Ohio County FIPS Codes and Target County Statistics

## All 88 Ohio Counties — FIPS Code Mapping

Ohio State FIPS prefix: **39** (e.g., Belmont County = 39013)

| FIPS | County | FIPS | County | FIPS | County |
|------|--------|------|--------|------|--------|
| 001 | Adams | 031 | Columbiana | 061 | Hamilton |
| 003 | Allen | 033 | Coshocton | 063 | Hancock |
| 005 | Ashland | 035 | Crawford | 065 | Hardin |
| 007 | Ashtabula | 037 | Cuyahoga | 067 | Harrison |
| 009 | Athens | 039 | Darke | 069 | Henry |
| 011 | Auglaize | 041 | Defiance | 071 | Highland |
| 013 | Belmont | 043 | Delaware | 073 | Hocking |
| 015 | Brown | 045 | Erie | 075 | Holmes |
| 017 | Butler | 047 | Fairfield | 077 | Huron |
| 019 | Carroll | 049 | Fayette | 079 | Jackson |
| 021 | Champaign | 051 | Franklin | 081 | Jefferson |
| 023 | Clark | 053 | Fulton | 083 | Knox |
| 025 | Clermont | 055 | Gallia | 085 | Lake |
| 027 | Clinton | 057 | Geauga | 087 | Lawrence |
| 029 | Columbiana | 059 | Guernsey | 089 | Licking |
| 031 | Columbiana | 061 | Hamilton | 091 | Logan |
| 093 | Lorain | 117 | Morrow | 141 | Ross |
| 095 | Lucas | 119 | Muskingum | 143 | Sandusky |
| 097 | Madison | 121 | Noble | 145 | Scioto |
| 099 | Mahoning | 123 | Ottawa | 147 | Seneca |
| 101 | Marion | 125 | Paulding | 149 | Shelby |
| 103 | Monroe | 127 | Perry | 151 | Stark |
| 105 | Medina | 129 | Pickaway | 153 | Summit |
| 107 | Meigs | 131 | Pike | 155 | Trumbull |
| 109 | Mercer | 133 | Portage | 157 | Tuscarawas |
| 111 | Monroe | 135 | Preble | 159 | Union |
| 113 | Montgomery | 137 | Putnam | 161 | Van Wert |
| 115 | Morgan | 139 | Richland | 163 | Vinton |
| 165 | Warren | 171 | Williams |      |          |
| 167 | Washington | 173 | Wood |      |          |
| 169 | Wayne | 175 | Wyandot |      |          |

**Note:** The OGRIP `County` field uses county names (e.g., "BELMONT"), not
FIPS codes. The ODNR wells layer uses `WL_CNTY` for county name and `CO_NAME`
for the full county name. County names should be matched case-insensitively.

---

## 8 Target Counties — Eastern OH Utica/Marcellus Play

These counties lie within the core of the Ohio Utica/Marcellus Shale play,
with the highest concentrations of horizontal shale wells and significant
mineral-coded parcel inventories in the OGRIP dataset.

| FIPS | County | Mineral Parcels | Utica Wells | Key Operators | Notes |
|------|--------|----------------|-------------|---------------|-------|
| 013 | Belmont | ~600 | ~800 | Ascent, Gulfport, Rice | Major Utica wet/dry gas window |
| 019 | Carroll | ~400 | ~500 | Encino, Rex, Chesapeake | First major Utica discoveries (2011) |
| 031 | Columbiana | ~200 | ~200 | Hilcorp, Encino | Northern Utica play edge |
| 067 | Harrison | ~500 | ~600 | Ascent, Gulfport, Eclipse | Active Utica drilling, condensate window |
| 081 | Jefferson | ~300 | ~300 | Ascent, Gulfport, EAP Ohio | Eastern play border |
| 103 | Monroe | ~350 | ~400 | Ascent, Eclipse, SWN | Southern Utica/Point Pleasant extension |
| 111 | Noble | ~250 | ~300 | Ascent, Gulfport, Rex | Active Utica/Point Pleasant play |
| 059 | Guernsey | ~150 | ~200 | Antero, Eclipse | Western edge of productive play |

**Notes on counts:**
- Mineral parcel counts are approximate OGRIP records with `StateLUC LIKE '2%'`
- Utica well counts are approximate from ODNR active horizontal wells
- Operator names reflect major lease holders in each county
- Counts will vary as data is updated; use live queries for current numbers

---

## County Name Formats Across Sources

| Source | Field | Format | Example |
|--------|-------|--------|---------|
| OGRIP Parcels | `County` | Full name, uppercase | "BELMONT" |
| OIT Parcels 2022 | `COUNTY` | Full name, uppercase | "BELMONT" |
| ODNR Wells | `WL_CNTY` | Full name, mixed case | "Belmont" |
| ODNR Wells | `CO_NAME` | Full name, mixed case | "Belmont" |
| Stark County GIS | `CNTY_NAME` | Full name | "STARK" |

When querying across sources, use case-insensitive comparisons or normalize
county names. The OGRIP `County` field is the most consistent reference.

---

## Ohio Dormant Mineral Act Context

Under ORC 5301.56, mineral rights can be deemed abandoned after 20 years of
inactivity if no "savings events" have occurred. The relevant counties are
those with older mineral severances — particularly in eastern Ohio where
coal and oil/gas mineral rights were severed in the late 1800s and early 1900s.

Counties with the highest density of historical mineral severances and
potential Dormant Mineral Act applicability:

| County | Historical Context |
|--------|--------------------|
| Belmont | Extensive coal mining history, many pre-1900 mineral severances |
| Harrison | Oil/gas production since 1800s, layered mineral ownership |
| Jefferson | Coal belt, significant mineral estate complexity |
| Monroe | Deep gas history, many pre-1950 mineral deeds |
| Carroll | Oil boom history, some severed estates from 1800s |
| Columbiana | Coal mining legacy, mineral-surface splits |
| Noble | Oil/gas since early 1900s, scattered mineral parcels |
| Guernsey | Coal and oil history, mixed surface/mineral ownership |
