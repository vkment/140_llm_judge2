# `corr_utils.py` — Correlation Utilities

Reference: Deutsch, Foster & Freitag (EMNLP 2023) — *Ties Matter: Meta-Evaluating Modern Metrics with Pairwise Accuracy and Tie Calibration*  
Paper URL: https://aclanthology.org/2023.emnlp-main.798

---

## Purpose

Implements several rank-correlation statistics used for meta-evaluation of automatic metrics.
All statistics compare two sequences of scores (human vs. metric/judge) by examining every pair of items (i, j) and classifying each pair into one of five categories.

---

## Core helper: `_get_params_from_ranks`

```python
_get_params_from_ranks(rank_human, rank_metric) → (C, D, T_h, T_m, T_hm)
```

Iterates over all **n(n-1)/2** unique pairs (i, j) and classifies each pair into exactly one of five mutually exclusive categories:

| Symbol | Meaning |
|--------|---------|
| `C`    | Concordant — both sequences agree on the ordering of the pair |
| `D`    | Discordant — the two sequences disagree on the ordering |
| `T_h`  | Tied only in human scores (metric disagrees or distinguishes) |
| `T_m`  | Tied only in metric/judge scores (human disagrees or distinguishes) |
| `T_hm` | Tied in **both** — a correctly predicted tie |

**Important:** The inputs are treated as raw scores (or ranks), not converted internally.  
Higher values mean "better quality"; comparison uses `<`, `>`, `==` directly.  
Using raw scores or ranks are equivalent for all statistics implemented here (order-preserving monotone transformation does not change pairwise classifications).

**Known minor bug:** No `else` / `raise` guard at the end of the loop. In theory all 9 combinations of {<, =, >} × {<, =, >} are covered by the seven `if/elif` branches, but if floating-point NaNs were present they would fall through silently. In practice, scores are always finite numerics, so this is harmless.

---

## Public functions

### `my_acc_eq` ← **primary metric used in this project**

```
acc_eq = (C + T_hm) / (C + D + T_h + T_m + T_hm)
```

Pairwise accuracy *with* ties. Rewards the metric both for correctly ordering a pair **and** for correctly predicting a tie. Returns a value in [0, 1]; 0.5 is the expected value of a random metric.

### `my_tau_eq`

```
τ_eq = (C + T_hm − D − T_h − T_m) / (C + D + T_h + T_m + T_hm)
```

Closely related to `acc_eq`: `τ_eq = 2 · acc_eq − 1`. Range is [−1, 1].

### `my_pairwise_acc`

```
pair_acc = C / (C + D)
```

Classic pairwise accuracy **excluding all ties** (neither human ties nor metric ties). Used for system-level ranking comparison where the two averaged system scores rarely tie.

### `my_tau_a`

```
τ_a = (C − D) / (C + D + T_h + T_m + T_hm)
```

Original Kendall (1938) τ, penalises all ties equally. Range [−1, 1].

### `my_tau_b`

```
τ_b = (C − D) / sqrt((C + D + T_h) · (C + D + T_m))
```

Kendall τ_b (1945), normalised to reach ±1 when one or both sequences are fully tied. Used in WMT'21–22 metric shared tasks. Range [−1, 1].

### `my_tau_13` ⚠️ **contains a bug — not used in production**

Intended formula (Machácek & Bojar 2013):
```
τ_13 = (C − D) / (C + D)
```

Actual implementation uses `n(n-1)/2` as the denominator instead of `C + D`. This makes it equivalent to `τ_a` only when there are no ties, and gives incorrect values otherwise. **This function is not imported or called anywhere in `judge_human_agreement.py`.**

### `my_tau_c` — not implemented

Raises `NotImplementedError`. Stuart (1953) τ_c. Not needed for current usage.

---

## Usage notes

- All functions accept `List[float]` but NumPy arrays work equally well.
- Inputs must be the same length (asserted).
- All functions return `0.0` when the denominator is zero (e.g., only one item).
- For segment-level group-by-item evaluation: call on the per-item raw score vectors directly; do **not** convert to ranks first.
- For system-level evaluation: pre-compute average scores per system, then convert to ranks with `pandas.Series.rank(method="min", ascending=False)` before calling.
