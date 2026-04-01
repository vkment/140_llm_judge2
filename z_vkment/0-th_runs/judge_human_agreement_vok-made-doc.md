# `judge_human_agreement.py` — LLM-as-a-Judge vs. Human Agreement

## Purpose

Computes how well each LLM judge agrees with human annotators on the Open-Ended Generation (OEG) track.
Uses the **group-by-item pairwise accuracy with ties** (`acc_eq`) from Deutsch et al. (EMNLP 2023) as the primary metric.
Outputs two JSON files with structured results.

---

## Data model

Both input DataFrames share the same six-column schema:

| Column | Description |
|--------|-------------|
| `judge_model_name` | `"human"` or an LLM name (e.g. `"Llama-4-Maverick"`) |
| `criterion` | `"coherence"`, `"naturalness"`, or `"instruction_following"` |
| `submission_system_name` | Name of the evaluated system (16 systems) |
| `original_instance_id` | MD5 hex ID of the source prompt (46 prompts) |
| `locale` | BCP-47-style locale code, e.g. `"en_US"` (10 locales) |
| `score` | Numeric score in [1, 7] |

A derived column `original_instance_id_with_locale` (= `original_instance_id + "_with_" + locale`) uniquely identifies a (prompt, language) pair. It is used to group data for the group-by-item computation.

---

## Input data sources

### `oeg_human_eval_data.csv`
Aggregated human judgements. Loaded directly if the file exists; otherwise reconstructed from per-locale raw CSV files in `./oeg_human_eval_raw_data/` via `gather_oeg_human_eval_data()`.

- 10 locales × 46 prompts × 16 systems × 3 criteria = **22 080 rows**
- Scores represent human ratings (one aggregated score per cell; raw data had 3 raters)

### `oeg_judge_run2_submission_data.csv`
LLM judge scores from the competition's run 2. Loaded directly if the file exists; otherwise built from JSON submission files in `../submissions_oeg_judge_run2/` via `gather_oeg_judge_submission_data()`.

- 13 judge models × 3 criteria × 10 locales × 46 prompts × 16 systems = **287 040 rows**

---

## Pre-processing (`__main__` block)

1. **Load** both DataFrames (from CSV cache or from raw files).
2. **Create** `original_instance_id_with_locale` in both.
3. **Filter** to the intersection of values in `submission_system_name`, `criterion`, and `original_instance_id_with_locale` across both DataFrames. This ensures all subsequent computations use exactly the same set of data points.

---

## Functions

### `parse_score_from_answer(answer)`

Parses a judge's raw text output into a float score in [1, 7].

- Trims to the first line.
- `"FAILED"` → random integer in [1, 7] (fallback for server/parsing failures).
- Otherwise `float(answer)`.
- Clamps result to [1.0, 7.0].

### `gather_oeg_judge_submission_data(output_csv=None)`

Reads all `.json` files from `../submissions_oeg_judge_run2/`, normalises criterion names and locale codes, and returns a unified DataFrame. Optionally writes to CSV.

Locale decoding: the task ID encodes a numeric language ID (`language_id // 100`) that is looked up in `ID_TO_LOCALE_dict`.

Criterion mapping:
| Raw | Normalised |
|-----|-----------|
| `judge_it` | `instruction_following` |
| `judge_coherence` | `coherence` |
| `judge_natural` | `naturalness` |

### `gather_oeg_human_eval_data(output_csv=None)`

Reads all `data_<locale>.csv` files from `./oeg_human_eval_raw_data/`, melts the three criterion columns into rows, and returns a unified DataFrame. Optionally writes to CSV.

### `perform_EDA(df_judge_submission, df_human_eval, verbose=True)`

Sanity-checks (assertions) and optional descriptive statistics.

Expected sizes after filtering:
- Judge DataFrame: 287 040 rows, 13 unique judge models.
- Human DataFrame: 22 080 rows, 1 unique judge model.

### `get_system_level_score(df_human_eval, df_judge_submission, metric_fn)`

Computes a **system-level** agreement score between each LLM judge and humans.

1. Average each system's scores across all criteria and locales (both for human and for each judge).
2. Rank systems by average score (rank 1 = best; ties get the same minimum rank).
3. Call `metric_fn(rank_human, rank_judge)` to get the agreement score.

Returns `{judge_model_name: score}`.

Used in `__main__` with `metric_fn = my_pairwise_acc` (ties excluded, as system-level ties are rare).

> **Note:** Averaging across criteria before ranking is a pragmatic choice. An alternative would be to compute per-criterion system rankings and average the resulting scores.

### `get_score_by_criterion(df_human_eval, df_judge_submission, metric_fn)`

Computes **segment-level (group-by-item)** agreement per criterion.

For each criterion:
  - For each unique `original_instance_id_with_locale` (i.e., each prompt in each language):
    - Extract the 16 system scores from the judge and from humans, aligned by system name.
    - Call `metric_fn(scores_human, scores_judge)` → one scalar.
  - Average the scalars across all instances.

Returns `{criterion: {judge_model_name: avg_score}}`.

> Raw scores are passed directly to `metric_fn`, not converted to ranks.  
> For `acc_eq`/`tau_eq`, raw scores and ranks are equivalent (order-preserving). ✓

### `get_criterion_grouped_scores(df_human_eval, df_judge_submission, include_additional_metrics=False)`

Thin wrapper that calls `get_score_by_criterion` for `acc_eq` and optionally `tau_eq` and `tau_b`.

Returns `{metric_name: {criterion: {judge_model_name: score}}}`.

---

## Output files

### `oeg_judge_human_agreement_results.json`

```
{
  "ranking_accuracy":         {judge_model_name: float},   // system-level pair_acc (no ties)
  "acc_eq_by_<criterion>":    {judge_model_name: float},   // segment-level acc_eq per criterion
  "acc_eq_average":           {judge_model_name: float},   // mean of acc_eq across 3 criteria
  "criterion_grouped_scores": {metric_name: {criterion: {judge_model_name: float}}}
}
```

### `oeg_judge_human_agreement_by_criterion.json`

```
{
  "criterion_grouped_scores": {metric_name: {criterion: {judge_model_name: float}}}
}
```

---

## Methodological notes

| Concern | How it is handled |
|---------|-------------------|
| Ties in scores | `acc_eq` rewards correctly predicted ties (T_hm in numerator) |
| Segment-level grouping | Group-by-item: one acc_eq value per prompt, then averaged |
| System-level grouping | Average scores → rank → pairwise_acc (ties excluded) |
| Missing data | Intersection filter in pre-processing ensures all sets match |
| FAILED judge outputs | Random score in [1, 7]; logged implicitly via `parse_score_from_answer` |
