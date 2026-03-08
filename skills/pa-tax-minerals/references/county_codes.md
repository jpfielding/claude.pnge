# PA County FIPS Codes and Target County Statistics

## All 67 PA Counties — FIPS Code Mapping

| FIPS | County | FIPS | County | FIPS | County |
|------|--------|------|--------|------|--------|
| 001 | Adams | 025 | Carbon | 049 | Erie |
| 003 | Allegheny | 027 | Centre | 051 | Fayette |
| 005 | Armstrong | 029 | Chester | 053 | Forest |
| 007 | Beaver | 031 | Clarion | 055 | Franklin |
| 009 | Bedford | 033 | Clearfield | 057 | Fulton |
| 011 | Berks | 035 | Clinton | 059 | Greene |
| 013 | Blair | 037 | Columbia | 061 | Huntingdon |
| 015 | Bradford | 039 | Crawford | 063 | Indiana |
| 017 | Bucks | 041 | Cumberland | 065 | Jefferson |
| 019 | Butler | 043 | Dauphin | 067 | Juniata |
| 021 | Cambria | 045 | Delaware | 069 | Lackawanna |
| 023 | Cameron | 047 | Elk | 071 | Lancaster |

| FIPS | County | FIPS | County | FIPS | County |
|------|--------|------|--------|------|--------|
| 073 | Lawrence | 093 | Montour | 113 | Sullivan |
| 075 | Lebanon | 095 | Northampton | 115 | Susquehanna |
| 077 | Lehigh | 097 | Northumberland | 117 | Tioga |
| 079 | Luzerne | 099 | Perry | 119 | Union |
| 081 | Lycoming | 101 | Philadelphia | 121 | Venango |
| 083 | McKean | 103 | Pike | 123 | Warren |
| 085 | Mercer | 105 | Potter | 125 | Washington |
| 087 | Mifflin | 107 | Schuylkill | 127 | Wayne |
| 089 | Monroe | 109 | Snyder | 129 | Westmoreland |
| 091 | Montgomery | 111 | Somerset | 131 | Wyoming |
|     |            |     |          | 133 | York |

**State FIPS prefix:** 42 (e.g., Washington County = 42125)

**API number prefix:** 37 (e.g., a Washington County well API = 37-125-XXXXX)

---

## PA DEP COUNTY_CODE Values

The PA DEP Parcels service uses a `COUNTY_CODE` field that is the 2-digit
county code within PA's own numbering (not FIPS). The `COUNTY_NAME` field
uses mixed case (e.g., "Washington"). In the Oil/Gas wells service, the
`COUNTY` field uses the full county name.

| COUNTY_CODE | COUNTY_NAME | FIPS | COUNTY_CODE | COUNTY_NAME | FIPS |
|-------------|-------------|------|-------------|-------------|------|
| 01 | Adams | 001 | 35 | Lackawanna | 069 |
| 02 | Allegheny | 003 | 36 | Lancaster | 071 |
| 03 | Armstrong | 005 | 37 | Lawrence | 073 |
| 04 | Beaver | 007 | 38 | Lebanon | 075 |
| 05 | Bedford | 009 | 39 | Lehigh | 077 |
| 06 | Berks | 011 | 40 | Luzerne | 079 |
| 07 | Blair | 013 | 41 | Lycoming | 081 |
| 08 | Bradford | 015 | 42 | McKean | 083 |
| 09 | Bucks | 017 | 43 | Mercer | 085 |
| 10 | Butler | 019 | 44 | Mifflin | 087 |
| 11 | Cambria | 021 | 45 | Monroe | 089 |
| 12 | Cameron | 023 | 46 | Montgomery | 091 |
| 13 | Carbon | 025 | 47 | Montour | 093 |
| 14 | Centre | 027 | 48 | Northampton | 095 |
| 15 | Chester | 029 | 49 | Northumberland | 097 |
| 16 | Clarion | 031 | 50 | Perry | 099 |
| 17 | Clearfield | 033 | 51 | Philadelphia | 101 |
| 18 | Clinton | 035 | 52 | Pike | 103 |
| 19 | Columbia | 037 | 53 | Potter | 105 |
| 20 | Crawford | 039 | 54 | Schuylkill | 107 |
| 21 | Cumberland | 041 | 55 | Snyder | 109 |
| 22 | Dauphin | 043 | 56 | Somerset | 111 |
| 23 | Delaware | 045 | 57 | Sullivan | 113 |
| 24 | Elk | 047 | 58 | Susquehanna | 115 |
| 25 | Erie | 049 | 59 | Tioga | 117 |
| 26 | Fayette | 051 | 60 | Union | 119 |
| 27 | Forest | 053 | 61 | Venango | 121 |
| 28 | Franklin | 055 | 62 | Warren | 123 |
| 29 | Fulton | 057 | 63 | Washington | 125 |
| 30 | Greene | 059 | 64 | Wayne | 127 |
| 31 | Huntingdon | 061 | 65 | Westmoreland | 129 |
| 32 | Indiana | 063 | 66 | Wyoming | 131 |
| 33 | Jefferson | 065 | 67 | York | 133 |
| 34 | Juniata | 067 |    |             |      |

---

## 8 Target Counties — SW PA Marcellus/Utica Play

These counties have the highest concentration of unconventional Marcellus and
Utica well activity in southwestern Pennsylvania. PA's Third Strata Doctrine
(surface, coal, oil/gas) makes mineral identification more complex than WV.

| FIPS | County | COUNTY_CODE | Unconv Wells | Conv Wells | Notes |
|------|--------|-------------|-------------|------------|-------|
| 059 | Greene | 30 | ~1,800 | ~500 | Major Marcellus, EQT/CNX territory |
| 125 | Washington | 63 | ~2,500 | ~1,200 | Highest density unconventional |
| 051 | Fayette | 26 | ~200 | ~800 | Mixed conventional/unconventional |
| 129 | Westmoreland | 65 | ~300 | ~600 | Eastern edge of play |
| 003 | Allegheny | 02 | ~150 | ~400 | Urban/suburban edge |
| 019 | Butler | 10 | ~400 | ~1,000 | Northern play extension |
| 063 | Indiana | 32 | ~200 | ~500 | Central PA edge |
| 117 | Tioga | 59 | ~1,100 | ~2,000 | Northern tier major county |

## Additional NE PA Target Counties

| FIPS | County | COUNTY_CODE | Unconv Wells | Conv Wells | Notes |
|------|--------|-------------|-------------|------------|-------|
| 015 | Bradford | 08 | ~1,800 | ~3,000 | NE tier, Cabot/Southwestern territory |
| 115 | Susquehanna | 58 | ~1,200 | ~500 | NE tier, Cabot stronghold |
| 131 | Wyoming | 66 | ~200 | ~100 | NE tier, limited development |
| 081 | Lycoming | 41 | ~800 | ~2,500 | Central, Anadarko/SWEPI territory |

---

## Key Operators in PA Marcellus/Utica

| Operator | Primary Counties | Well Count |
|----------|-----------------|------------|
| EQT PRODUCTION COMPANY | Greene, Washington | ~2,000+ |
| RANGE RESOURCES | Washington, Greene | ~1,500+ |
| CNX GAS COMPANY LLC | Greene, Washington, Allegheny | ~800+ |
| CABOT OIL & GAS CORPORATION | Susquehanna | ~900+ |
| SOUTHWESTERN ENERGY | Bradford, Susquehanna, Tioga | ~1,200+ |
| SENECA RESOURCES COMPANY LLC | Tioga, McKean | ~500+ |
| CHESAPEAKE ENERGY | Bradford, Wyoming | ~400+ |
| RICE ENERGY (now EQT) | Washington, Greene | Legacy permits |

---

## County Tax Claim Bureau Contacts (Target Counties)

PA has no statewide delinquent property GIS layer. Tax delinquency data is
managed by each county's Tax Claim Bureau. For mineral parcel research, contact
the relevant county TCB directly.

| County | Phone | Website/Notes |
|--------|-------|---------------|
| Greene | (724) 852-5289 | County courthouse, Waynesburg |
| Washington | (724) 228-6770 | County courthouse, Washington |
| Fayette | (724) 430-1210 | County courthouse, Uniontown |
| Westmoreland | (724) 830-3429 | County courthouse, Greensburg |
| Allegheny | (412) 350-4100 | County Office Building, Pittsburgh |
| Butler | (724) 284-5320 | County Government Center, Butler |
| Indiana | (724) 465-3805 | County courthouse, Indiana |
| Tioga | (570) 724-9120 | County courthouse, Wellsboro |
| Bradford | (570) 265-1722 | County courthouse, Towanda |
| Susquehanna | (570) 278-4600 x1240 | County courthouse, Montrose |

---

## County Assessment Data Access

County assessment records are the primary means of identifying mineral parcels
in PA. Most counties participate in the CAMADataSite program or have their own
online assessment search tools.

| County | Assessment Access | URL |
|--------|------------------|-----|
| Greene | CAMADataSite | https://greene.camadatasites.com/ |
| Washington | CAMADataSite | https://washington.camadatasites.com/ |
| Fayette | CAMADataSite | https://fayette.camadatasites.com/ |
| Westmoreland | CAMADataSite | https://westmoreland.camadatasites.com/ |
| Allegheny | County Portal | https://www2.alleghenycounty.us/RealEstate/ |
| Butler | CAMADataSite | https://butler.camadatasites.com/ |
| Indiana | CAMADataSite | https://indiana.camadatasites.com/ |
| Tioga | CAMADataSite | https://tioga.camadatasites.com/ |

**Note:** CAMADataSite provides owner name, legal description, assessment value,
and property classification. Look for property class codes containing "MINERAL",
"SUBSURFACE", or "OIL AND GAS" in the legal description or use class fields.
Each county's classification system is different.
