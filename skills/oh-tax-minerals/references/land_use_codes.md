# Ohio Land Use Codes — Mineral Series and Dormant Mineral Act

## Ohio StateLUC 200-Series — Mineral Land Use Codes

Ohio's statewide parcel dataset (OGRIP) assigns explicit 200-series land use
codes to mineral parcels via the `StateLUC` field. This is a **critical
advantage** over West Virginia and Pennsylvania, where mineral parcels must be
identified by parsing free-text legal descriptions — a method prone to both
false positives and false negatives.

In Ohio, `StateLUC LIKE '2%'` cleanly identifies mineral-coded parcels with
no text parsing required.

### Full 200-Series Code Table

| Code | Description | Category | Notes |
|------|-------------|----------|-------|
| 200 | Min-Custom Code | General Mineral | County-defined mineral classification |
| 210 | Min-Coal Land (surface and rights) | Coal | Combined surface + coal mineral estate |
| 220 | Min-Coal Rights-Working Interest | Coal | Active coal mining/leasing interest |
| 230 | Min-Coal Rights-Separate Royalty Interest | Coal | Passive coal royalty interest |
| 240 | Min-Oil and Gas-Working Interest | Oil & Gas | **Primary target** — active O&G operating interest |
| 250 | Min-Oil and Gas-Separate Royalty Interest | Oil & Gas | **Primary target** — passive O&G royalty interest |
| 260 | Min-Other Minerals | Other | Clay, sand, gravel, limestone, salt, etc. |
| 261 | Min-Custom Code | Other | County-defined mineral classification |
| 270 | Min-Custom Code | General | County-defined mineral classification |

### Targeting Strategy

**Utica/Marcellus investment focus — Oil and Gas interests:**
```sql
StateLUC IN ('240','250')
```

**Broader mineral screen (includes coal and other):**
```sql
StateLUC LIKE '2%'
```

**Coal interests only (relevant for subsurface rights research):**
```sql
StateLUC IN ('210','220','230')
```

### Distribution by Category

| Category | Codes | Approx Count | % of Mineral Parcels |
|----------|-------|-------------|---------------------|
| Oil & Gas | 240, 250 | ~1,300 | ~39% |
| Coal | 210, 220, 230 | ~1,600 | ~48% |
| Other/Custom | 200, 260, 261, 270 | ~460 | ~13% |
| **Total** | All 200-series | **~3,360** | 100% |

---

## Other StateLUC Ranges (Non-Mineral)

For context, the Ohio StateLUC system covers all land use types:

| Range | Category | Examples |
|-------|----------|---------|
| 100-199 | Residential | 100=Vacant Residential, 110=Single Family |
| 300-399 | Agricultural | 300=Vacant Agricultural, 310=Tillable |
| 400-499 | Industrial | 400=Vacant Industrial |
| 500-599 | Commercial | 500=Vacant Commercial |
| 600-699 | Exempt | 600=Exempt (government, church, etc.) |

---

## Ohio Dormant Mineral Act — ORC 5301.56

### Overview

The Ohio Dormant Mineral Act (ORC 5301.56), as amended in 2006, provides a
mechanism for surface owners to reclaim mineral rights that have been
"abandoned" through 20 years of inactivity. This is the primary legal tool
for surface owners to extinguish old severed mineral interests.

### The 20-Year Inactivity Test

A mineral interest is deemed abandoned if, during the preceding 20 years,
NONE of the following "savings events" have occurred:

| Savings Event | Description |
|---------------|-------------|
| **Title transaction** | Recorded transfer, lease, mortgage, or other instrument affecting the mineral interest |
| **Mineral tax filing** | Mineral interest was separately listed on the county tax duplicate (filed a declaration of value) |
| **Mineral use** | Production, mining, or withdrawal of minerals from the property |
| **Mining permit** | Active mining permit, drilling permit, or injection well permit |
| **Unitization** | Property was included in a mandatory pooling or unitization order |
| **Claim to preserve** | Owner filed a notice of preservation (an affidavit preserving the mineral interest) |
| **Known owner** | Surface owner or agent had actual knowledge of the mineral owner's identity |

### How the Act Works

1. **Surface owner serves notice** — The surface owner publishes notice in a
   local newspaper and sends notice by registered mail to the last known
   address of the mineral owner
2. **60-day response period** — The mineral owner has 60 days to file a
   claim to preserve their interest
3. **If no response** — The surface owner files an affidavit with the county
   recorder, and the mineral interest merges back into the surface estate
4. **If response filed** — The mineral interest is preserved for another
   20-year period

### Dormant Mineral Act Screening Criteria

When evaluating an Ohio mineral parcel for potential Dormant Mineral Act
applicability, check:

| Factor | Where to Find | Dormancy Indicator |
|--------|--------------|-------------------|
| Last production year | ODNR `Last_Nonzero_Production_Year` | No production in 20+ years |
| Active well permits | ODNR `WL_STATUS_DESC` | No active/permitted wells nearby |
| Tax filing status | County auditor records (via `CAMADataSite`) | No recent tax payments |
| Mineral deed date | County recorder records | Old deed with no subsequent transfers |
| Operator activity | ODNR `CO_NAME` | No known operator |

**Note on the 2006 amendment:** Prior to the 2006 amendment, the Act was more
easily applied. The 2006 version added the "savings events" framework, which
gives mineral owners more ways to preserve their interests. Courts have also
imposed strict notice requirements. Legal counsel should always be consulted.

### Relevance to This Skill

The Dormant Mineral Act is relevant when:
- A mineral parcel (StateLUC 200-series) shows no nearby active wells
- The `Last_Nonzero_Production_Year` on nearby ODNR wells is 20+ years ago
- The parcel appears on county delinquent tax lists
- The mineral deed is old (pre-2000) with no recorded transfers

**This skill does NOT determine whether a mineral interest qualifies for
abandonment under ORC 5301.56.** It provides data screening to identify
parcels that may warrant further investigation by a title examiner and
legal counsel.

---

## County-Level Variation in StateLUC Coding

Not all 88 Ohio counties consistently code mineral parcels with 200-series
StateLUC values. Coverage varies:

| Coverage Level | Counties | Notes |
|---------------|----------|-------|
| **Good** (consistent 200-series coding) | Belmont, Harrison, Jefferson, Monroe, Carroll | Eastern coal/gas counties with long mineral history |
| **Moderate** (partial coding) | Noble, Guernsey, Columbiana | Some mineral parcels may use non-200 codes |
| **Low** (minimal mineral coding) | Western/central OH counties | Few severed mineral estates, less coding attention |

For the 8 target counties in the eastern Utica/Marcellus play, mineral
coding is generally good because these counties have deep histories of coal
and oil/gas mineral severances that predate OGRIP.

### Potential Undercounting

The 3,360 mineral-coded parcels in OGRIP represent a **lower bound**. Some
mineral parcels may be coded with non-200 codes (e.g., 100-series if the
mineral parcel was assessed as part of the surface tract). Cross-referencing
with county auditor data (`CAMADataSite`) can reveal additional mineral
interests not captured by the StateLUC code.

---

## Comparison with WV and PA

| Factor | Ohio | West Virginia | Pennsylvania |
|--------|------|--------------|-------------|
| Mineral identification | **Explicit StateLUC 200-series** | Text parsing of `FullLegalDescription` (LIKE '%MINERAL%') | Text parsing of `USE_DESC` field (LIKE '%mineral%') |
| Reliability | **High** — coded at data entry | Medium — depends on description text | Medium — depends on description text |
| False positive rate | **Very low** | Moderate (geographic names like "COAL RIVER") | Moderate (similar text ambiguities) |
| False negative rate | **Low to moderate** | High (sparse descriptions, missing keywords) | High (same parsing limitations) |
| Delinquent data | County-level only, fragmented | **Statewide layer** (32,749 records) | County-level only, fragmented |
| Dormant mineral law | ORC 5301.56 (20-year test) | N/A (no equivalent statute) | 68 P.S. 891 (similar dormant act) |
