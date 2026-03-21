# Forecast signals — trace report (Accelerating vs Emerging)

Generated from on-disk artifacts (forecast CSV + parquets + raw epoch-3 CSVs).

## How to read this

- Matches **`GET /api/v1/forecast/tropes`** / dashboard: **Accelerating** = `baseline_count > 50`, first 10 rows in **forecast CSV order** within that filter; **Emerging** = `baseline_count <= 50`, first 10 in that slice.
- **Epoch 1 (baseline)** parquet: `181,839` books (`data/processed/epoch_1_baseline.parquet`).
- **Epoch 3 (forecast modern)** parquet: `275` books (`data/processed/epoch_3_forecast.parquet`).
- **Lift math** (matches `engine/03_calculate_lift.py`): if `baseline_count == 0`, denominator uses `1 / 2,360,000`; else true baseline share. Then `trend_lift` is **clipped to 999.99**. `weighted_score = trend_lift * log1p(epoch3_count)`.

## Accelerating trends (`baseline_count` > 50)

### 1. `FORCED_PROXIMITY`

#### Snapshot from `forecast_report.csv`

| Field | Value |
| --- | --- |
| trend_lift (exported, capped) | 179.86 |
| weighted_score | 761.53 |
| epoch3_count | 68 |
| baseline_count | 250 |
| epoch3_share (%, in CSV) | 24.73 |
| baseline_share (%, in CSV) | 0.14 |

#### Recomputed from parquets (sanity check)

| Quantity | Value |
| --- | --- |
| Books with trope in baseline | **250** / 181,839 |
| Books with trope in epoch 3 | **68** / 275 |
| Baseline share (fraction) | `0.001374842581` |
| Epoch 3 share (fraction) | `0.2472727273` |
| Pseudo baseline share (denominator) | `0.001374842581` (true baseline share) |
| Raw lift (before cap) | `179.9` |
| Lift after cap | `179.86` |
| log1p(epoch3_count) | `4.234107` |
| weighted_score (recomputed) | `761.53` |

#### Why this rank (plain language)

- Lift **179.86×** from epoch-3 share **24.7273%** vs baseline share **0.1375%**.
- **Weighted score** (global ranking): `179.86 * log1p(68)` ≈ **761.5**.

#### Taxonomy shelves mapped to this trope

- `forced-proximity`
- `forced proximity`
- `only one bed`
- `one bed`
- `stuck together`
- `trapped together`
- `snowed in`
- `stranded together`
- `roommates`
- `roommate romance`

#### Raw epoch-3 `*_processed.csv` attribution (re-count from JSON shelves)

- **Sum of per-file book hits:** 68 (parquet modern count was **68**; small mismatches can happen if parquet was built from a different file set or duplicates were collapsed.)

- `2024_mf_processed.csv`: **42** books with a shelf mapping to `FORCED_PROXIMITY`
- `2025_mf_broad_processed.csv`: **26** books with a shelf mapping to `FORCED_PROXIMITY`

---

### 2. `FAKE_DATING`

#### Snapshot from `forecast_report.csv`

| Field | Value |
| --- | --- |
| trend_lift (exported, capped) | 158.12 |
| weighted_score | 495.79 |
| epoch3_count | 22 |
| baseline_count | 92 |
| epoch3_share (%, in CSV) | 8.0 |
| baseline_share (%, in CSV) | 0.05 |

#### Recomputed from parquets (sanity check)

| Quantity | Value |
| --- | --- |
| Books with trope in baseline | **92** / 181,839 |
| Books with trope in epoch 3 | **22** / 275 |
| Baseline share (fraction) | `0.0005059420696` |
| Epoch 3 share (fraction) | `0.08` |
| Pseudo baseline share (denominator) | `0.0005059420696` (true baseline share) |
| Raw lift (before cap) | `158.1` |
| Lift after cap | `158.12` |
| log1p(epoch3_count) | `3.135494` |
| weighted_score (recomputed) | `495.79` |

#### Why this rank (plain language)

- Lift **158.12×** from epoch-3 share **8.0000%** vs baseline share **0.0506%**.
- **Weighted score** (global ranking): `158.12 * log1p(22)` ≈ **495.8**.

#### Taxonomy shelves mapped to this trope

- `fake-dating`
- `fake dating`
- `fake relationship`
- `pretend relationship`
- `fake engagement`
- `contract relationship`

#### Raw epoch-3 `*_processed.csv` attribution (re-count from JSON shelves)

- **Sum of per-file book hits:** 22 (parquet modern count was **22**; small mismatches can happen if parquet was built from a different file set or duplicates were collapsed.)

- `2024_mf_processed.csv`: **13** books with a shelf mapping to `FAKE_DATING`
- `2025_mf_broad_processed.csv`: **9** books with a shelf mapping to `FAKE_DATING`

---

### 3. `SPORTS_HOCKEY`

#### Snapshot from `forecast_report.csv`

| Field | Value |
| --- | --- |
| trend_lift (exported, capped) | 13.16 |
| weighted_score | 40.06 |
| epoch3_count | 20 |
| baseline_count | 1005 |
| epoch3_share (%, in CSV) | 7.27 |
| baseline_share (%, in CSV) | 0.55 |

#### Recomputed from parquets (sanity check)

| Quantity | Value |
| --- | --- |
| Books with trope in baseline | **1,005** / 181,839 |
| Books with trope in epoch 3 | **20** / 275 |
| Baseline share (fraction) | `0.005526867174` |
| Epoch 3 share (fraction) | `0.07272727273` |
| Pseudo baseline share (denominator) | `0.005526867174` (true baseline share) |
| Raw lift (before cap) | `13.16` |
| Lift after cap | `13.16` |
| log1p(epoch3_count) | `3.044522` |
| weighted_score (recomputed) | `40.06` |

#### Why this rank (plain language)

- Lift **13.16×** from epoch-3 share **7.2727%** vs baseline share **0.5527%**.
- **Weighted score** (global ranking): `13.16 * log1p(20)` ≈ **40.1**.

#### Taxonomy shelves mapped to this trope

- `hockey`
- `hockey romance`
- `ice hockey`
- `nhl`

#### Raw epoch-3 `*_processed.csv` attribution (re-count from JSON shelves)

- **Sum of per-file book hits:** 20 (parquet modern count was **20**; small mismatches can happen if parquet was built from a different file set or duplicates were collapsed.)

- `2024_mf_processed.csv`: **14** books with a shelf mapping to `SPORTS_HOCKEY`
- `2025_mf_broad_processed.csv`: **6** books with a shelf mapping to `SPORTS_HOCKEY`

---

### 4. `SLOW_BURN`

#### Snapshot from `forecast_report.csv`

| Field | Value |
| --- | --- |
| trend_lift (exported, capped) | 8.36 |
| weighted_score | 26.57 |
| epoch3_count | 23 |
| baseline_count | 1819 |
| epoch3_share (%, in CSV) | 8.36 |
| baseline_share (%, in CSV) | 1.0 |

#### Recomputed from parquets (sanity check)

| Quantity | Value |
| --- | --- |
| Books with trope in baseline | **1,819** / 181,839 |
| Books with trope in epoch 3 | **23** / 275 |
| Baseline share (fraction) | `0.01000335462` |
| Epoch 3 share (fraction) | `0.08363636364` |
| Pseudo baseline share (denominator) | `0.01000335462` (true baseline share) |
| Raw lift (before cap) | `8.361` |
| Lift after cap | `8.36` |
| log1p(epoch3_count) | `3.178054` |
| weighted_score (recomputed) | `26.57` |

#### Why this rank (plain language)

- Lift **8.36×** from epoch-3 share **8.3636%** vs baseline share **1.0003%**.
- **Weighted score** (global ranking): `8.36 * log1p(23)` ≈ **26.6**.

#### Taxonomy shelves mapped to this trope

- `slow-burn`
- `slow burn`
- `slowburn`

#### Raw epoch-3 `*_processed.csv` attribution (re-count from JSON shelves)

- **Sum of per-file book hits:** 23 (parquet modern count was **23**; small mismatches can happen if parquet was built from a different file set or duplicates were collapsed.)

- `2024_mf_processed.csv`: **18** books with a shelf mapping to `SLOW_BURN`
- `2025_mf_broad_processed.csv`: **5** books with a shelf mapping to `SLOW_BURN`

---

### 5. `SPORTS_BASEBALL`

#### Snapshot from `forecast_report.csv`

| Field | Value |
| --- | --- |
| trend_lift (exported, capped) | 11.0 |
| weighted_score | 25.33 |
| epoch3_count | 9 |
| baseline_count | 541 |
| epoch3_share (%, in CSV) | 3.27 |
| baseline_share (%, in CSV) | 0.3 |

#### Recomputed from parquets (sanity check)

| Quantity | Value |
| --- | --- |
| Books with trope in baseline | **541** / 181,839 |
| Books with trope in epoch 3 | **9** / 275 |
| Baseline share (fraction) | `0.002975159344` |
| Epoch 3 share (fraction) | `0.03272727273` |
| Pseudo baseline share (denominator) | `0.002975159344` (true baseline share) |
| Raw lift (before cap) | `11` |
| Lift after cap | `11.00` |
| log1p(epoch3_count) | `2.302585` |
| weighted_score (recomputed) | `25.33` |

#### Why this rank (plain language)

- Lift **11.00×** from epoch-3 share **3.2727%** vs baseline share **0.2975%**.
- **Weighted score** (global ranking): `11.00 * log1p(9)` ≈ **25.3**.

#### Taxonomy shelves mapped to this trope

- `baseball`

#### Raw epoch-3 `*_processed.csv` attribution (re-count from JSON shelves)

- **Sum of per-file book hits:** 9 (parquet modern count was **9**; small mismatches can happen if parquet was built from a different file set or duplicates were collapsed.)

- `2024_mf_processed.csv`: **8** books with a shelf mapping to `SPORTS_BASEBALL`
- `2025_mf_broad_processed.csv`: **1** books with a shelf mapping to `SPORTS_BASEBALL`

---

### 6. `ENEMIES_TO_LOVERS`

#### Snapshot from `forecast_report.csv`

| Field | Value |
| --- | --- |
| trend_lift (exported, capped) | 5.22 |
| weighted_score | 21.54 |
| epoch3_count | 61 |
| baseline_count | 7730 |
| epoch3_share (%, in CSV) | 22.18 |
| baseline_share (%, in CSV) | 4.25 |

#### Recomputed from parquets (sanity check)

| Quantity | Value |
| --- | --- |
| Books with trope in baseline | **7,730** / 181,839 |
| Books with trope in epoch 3 | **61** / 275 |
| Baseline share (fraction) | `0.04251013259` |
| Epoch 3 share (fraction) | `0.2218181818` |
| Pseudo baseline share (denominator) | `0.04251013259` (true baseline share) |
| Raw lift (before cap) | `5.218` |
| Lift after cap | `5.22` |
| log1p(epoch3_count) | `4.127134` |
| weighted_score (recomputed) | `21.54` |

#### Why this rank (plain language)

- Lift **5.22×** from epoch-3 share **22.1818%** vs baseline share **4.2510%**.
- **Weighted score** (global ranking): `5.22 * log1p(61)` ≈ **21.5**.

#### Taxonomy shelves mapped to this trope

- `enemies-to-lovers`
- `enemies to lovers`
- `enemy to lovers`
- `enemies2lovers`
- `hate-to-love`
- `hate to love`
- `rivals-to-lovers`
- `rivals to lovers`
- `frenemies to lovers`

#### Raw epoch-3 `*_processed.csv` attribution (re-count from JSON shelves)

- **Sum of per-file book hits:** 61 (parquet modern count was **61**; small mismatches can happen if parquet was built from a different file set or duplicates were collapsed.)

- `2024_mf_processed.csv`: **41** books with a shelf mapping to `ENEMIES_TO_LOVERS`
- `2025_mf_broad_processed.csv`: **20** books with a shelf mapping to `ENEMIES_TO_LOVERS`

---

### 7. `SMALL_TOWN`

#### Snapshot from `forecast_report.csv`

| Field | Value |
| --- | --- |
| trend_lift (exported, capped) | 4.48 |
| weighted_score | 17.61 |
| epoch3_count | 50 |
| baseline_count | 7381 |
| epoch3_share (%, in CSV) | 18.18 |
| baseline_share (%, in CSV) | 4.06 |

#### Recomputed from parquets (sanity check)

| Quantity | Value |
| --- | --- |
| Books with trope in baseline | **7,381** / 181,839 |
| Books with trope in epoch 3 | **50** / 275 |
| Baseline share (fraction) | `0.04059085235` |
| Epoch 3 share (fraction) | `0.1818181818` |
| Pseudo baseline share (denominator) | `0.04059085235` (true baseline share) |
| Raw lift (before cap) | `4.479` |
| Lift after cap | `4.48` |
| log1p(epoch3_count) | `3.931826` |
| weighted_score (recomputed) | `17.61` |

#### Why this rank (plain language)

- Lift **4.48×** from epoch-3 share **18.1818%** vs baseline share **4.0591%**.
- **Weighted score** (global ranking): `4.48 * log1p(50)` ≈ **17.6**.

#### Taxonomy shelves mapped to this trope

- `small town`
- `small-town`
- `small town romance`
- `return to hometown`
- `hometown romance`

#### Raw epoch-3 `*_processed.csv` attribution (re-count from JSON shelves)

- **Sum of per-file book hits:** 50 (parquet modern count was **50**; small mismatches can happen if parquet was built from a different file set or duplicates were collapsed.)

- `2024_mf_processed.csv`: **40** books with a shelf mapping to `SMALL_TOWN`
- `2025_mf_broad_processed.csv`: **10** books with a shelf mapping to `SMALL_TOWN`

---

### 8. `SPORTS_GENERAL`

#### Snapshot from `forecast_report.csv`

| Field | Value |
| --- | --- |
| trend_lift (exported, capped) | 4.11 |
| weighted_score | 15.83 |
| epoch3_count | 46 |
| baseline_count | 7396 |
| epoch3_share (%, in CSV) | 16.73 |
| baseline_share (%, in CSV) | 4.07 |

#### Recomputed from parquets (sanity check)

| Quantity | Value |
| --- | --- |
| Books with trope in baseline | **7,396** / 181,839 |
| Books with trope in epoch 3 | **46** / 275 |
| Baseline share (fraction) | `0.0406733429` |
| Epoch 3 share (fraction) | `0.1672727273` |
| Pseudo baseline share (denominator) | `0.0406733429` (true baseline share) |
| Raw lift (before cap) | `4.113` |
| Lift after cap | `4.11` |
| log1p(epoch3_count) | `3.850148` |
| weighted_score (recomputed) | `15.83` |

#### Why this rank (plain language)

- Lift **4.11×** from epoch-3 share **16.7273%** vs baseline share **4.0673%**.
- **Weighted score** (global ranking): `4.11 * log1p(46)` ≈ **15.8**.

#### Taxonomy shelves mapped to this trope

- `sports`
- `sports romance`
- `sports story`

#### Raw epoch-3 `*_processed.csv` attribution (re-count from JSON shelves)

- **Sum of per-file book hits:** 46 (parquet modern count was **46**; small mismatches can happen if parquet was built from a different file set or duplicates were collapsed.)

- `2024_mf_processed.csv`: **35** books with a shelf mapping to `SPORTS_GENERAL`
- `2025_mf_broad_processed.csv`: **11** books with a shelf mapping to `SPORTS_GENERAL`

---

### 9. `WORKPLACE`

#### Snapshot from `forecast_report.csv`

| Field | Value |
| --- | --- |
| trend_lift (exported, capped) | 4.9 |
| weighted_score | 15.35 |
| epoch3_count | 22 |
| baseline_count | 2971 |
| epoch3_share (%, in CSV) | 8.0 |
| baseline_share (%, in CSV) | 1.63 |

#### Recomputed from parquets (sanity check)

| Quantity | Value |
| --- | --- |
| Books with trope in baseline | **2,971** / 181,839 |
| Books with trope in epoch 3 | **22** / 275 |
| Baseline share (fraction) | `0.01633862923` |
| Epoch 3 share (fraction) | `0.08` |
| Pseudo baseline share (denominator) | `0.01633862923` (true baseline share) |
| Raw lift (before cap) | `4.896` |
| Lift after cap | `4.90` |
| log1p(epoch3_count) | `3.135494` |
| weighted_score (recomputed) | `15.35` |

#### Why this rank (plain language)

- Lift **4.90×** from epoch-3 share **8.0000%** vs baseline share **1.6339%**.
- **Weighted score** (global ranking): `4.90 * log1p(22)` ≈ **15.4**.

#### Taxonomy shelves mapped to this trope

- `workplace`
- `workplace romance`
- `office romance`
- `office-romance`
- `coworkers`
- `co-worker`
- `boss employee`
- `boss/employee`
- `sleeping with the boss`
- `construction`

#### Raw epoch-3 `*_processed.csv` attribution (re-count from JSON shelves)

- **Sum of per-file book hits:** 22 (parquet modern count was **22**; small mismatches can happen if parquet was built from a different file set or duplicates were collapsed.)

- `2024_mf_processed.csv`: **18** books with a shelf mapping to `WORKPLACE`
- `2025_mf_broad_processed.csv`: **4** books with a shelf mapping to `WORKPLACE`

---

### 10. `COWBOY_WESTERN`

#### Snapshot from `forecast_report.csv`

| Field | Value |
| --- | --- |
| trend_lift (exported, capped) | 5.21 |
| weighted_score | 13.36 |
| epoch3_count | 12 |
| baseline_count | 1523 |
| epoch3_share (%, in CSV) | 4.36 |
| baseline_share (%, in CSV) | 0.84 |

#### Recomputed from parquets (sanity check)

| Quantity | Value |
| --- | --- |
| Books with trope in baseline | **1,523** / 181,839 |
| Books with trope in epoch 3 | **12** / 275 |
| Baseline share (fraction) | `0.008375541001` |
| Epoch 3 share (fraction) | `0.04363636364` |
| Pseudo baseline share (denominator) | `0.008375541001` (true baseline share) |
| Raw lift (before cap) | `5.21` |
| Lift after cap | `5.21` |
| log1p(epoch3_count) | `2.564949` |
| weighted_score (recomputed) | `13.36` |

#### Why this rank (plain language)

- Lift **5.21×** from epoch-3 share **4.3636%** vs baseline share **0.8376%**.
- **Weighted score** (global ranking): `5.21 * log1p(12)` ≈ **13.4**.

#### Taxonomy shelves mapped to this trope

- `cowboy romance`
- `westerns`
- `western romance`

#### Raw epoch-3 `*_processed.csv` attribution (re-count from JSON shelves)

- **Sum of per-file book hits:** 12 (parquet modern count was **12**; small mismatches can happen if parquet was built from a different file set or duplicates were collapsed.)

- `2024_mf_processed.csv`: **11** books with a shelf mapping to `COWBOY_WESTERN`
- `2025_mf_broad_processed.csv`: **1** books with a shelf mapping to `COWBOY_WESTERN`

---

## Emerging terminology (`baseline_count` ≤ 50)

### 1. `HE_FALLS_FIRST`

#### Snapshot from `forecast_report.csv`

| Field | Value |
| --- | --- |
| trend_lift (exported, capped) | 999.99 |
| weighted_score | 2995.7 |
| epoch3_count | 19 |
| baseline_count | 2 |
| epoch3_share (%, in CSV) | 6.91 |
| baseline_share (%, in CSV) | 0.0 |

#### Recomputed from parquets (sanity check)

| Quantity | Value |
| --- | --- |
| Books with trope in baseline | **2** / 181,839 |
| Books with trope in epoch 3 | **19** / 275 |
| Baseline share (fraction) | `1.099874064e-05` |
| Epoch 3 share (fraction) | `0.06909090909` |
| Pseudo baseline share (denominator) | `1.099874064e-05` (true baseline share) |
| Raw lift (before cap) | `6282` |
| Lift after cap | `999.99` |
| log1p(epoch3_count) | `2.995732` |
| weighted_score (recomputed) | `2995.70` |

#### Why this rank (plain language)

- **Lift hit the 999.99× UI cap.** Uncapped lift was ~**6282×**, driven by epoch-3 share **6.9091%** vs a very small baseline share (natural denominator).
- **Weighted score** (global ranking): `999.99 * log1p(19)` ≈ **2995.7**.

#### Taxonomy shelves mapped to this trope

- `he falls first`
- `he-falls-first`
- `he fell first`
- `boy obsessed`

#### Raw epoch-3 `*_processed.csv` attribution (re-count from JSON shelves)

- **Sum of per-file book hits:** 19 (parquet modern count was **19**; small mismatches can happen if parquet was built from a different file set or duplicates were collapsed.)

- `2024_mf_processed.csv`: **17** books with a shelf mapping to `HE_FALLS_FIRST`
- `2025_mf_broad_processed.csv`: **2** books with a shelf mapping to `HE_FALLS_FIRST`

---

### 2. `ACCIDENTAL_PREGNANCY`

#### Snapshot from `forecast_report.csv`

| Field | Value |
| --- | --- |
| trend_lift (exported, capped) | 999.99 |
| weighted_score | 2079.42 |
| epoch3_count | 7 |
| baseline_count | 0 |
| epoch3_share (%, in CSV) | 2.55 |
| baseline_share (%, in CSV) | 0.0 |

#### Recomputed from parquets (sanity check)

| Quantity | Value |
| --- | --- |
| Books with trope in baseline | **0** / 181,839 |
| Books with trope in epoch 3 | **7** / 275 |
| Baseline share (fraction) | `0` |
| Epoch 3 share (fraction) | `0.02545454545` |
| Pseudo baseline share (denominator) | `4.237288136e-07` (smoothed 1/2.36M) |
| Raw lift (before cap) | `6.007e+04` |
| Lift after cap | `999.99` |
| log1p(epoch3_count) | `2.079442` |
| weighted_score (recomputed) | `2079.42` |

#### Why this rank (plain language)

- **Lift hit the 999.99× UI cap.** Uncapped lift was ~**6.007e+04×**, driven by epoch-3 share **2.5455%** vs a very small baseline share (smoothed denominator).
- **Weighted score** (global ranking): `999.99 * log1p(7)` ≈ **2079.4**.

#### Taxonomy shelves mapped to this trope

- `accidental pregnancy`
- `surprise pregnancy`
- `knocked up`

#### Raw epoch-3 `*_processed.csv` attribution (re-count from JSON shelves)

- **Sum of per-file book hits:** 7 (parquet modern count was **7**; small mismatches can happen if parquet was built from a different file set or duplicates were collapsed.)

- `2024_mf_processed.csv`: **7** books with a shelf mapping to `ACCIDENTAL_PREGNANCY`

---
