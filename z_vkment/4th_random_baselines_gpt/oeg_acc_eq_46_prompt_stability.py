
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd

# ==========================================
# INPUT FILES
# ==========================================
HUMAN_CSV = Path("oeg_human_eval_data.csv")
JUDGE_CSV = Path("oeg_judge_run2_submission_data.csv")

# ==========================================
# ANALYSIS SETTINGS
# ==========================================
# If True, first compute prompt-level acc_eq separately for each judge model,
# then aggregate those judge-specific acc_eq values into ONE value per prompt.
# This matches the workflow:
#   locale × criterion × prompt  -> one acc_eq value
AGGREGATE_JUDGES_TO_ONE_PROMPT_VALUE = True

# How to aggregate judge-specific prompt acc_eq values into one prompt value.
# Options: "mean", "median", "min", "max"
JUDGE_AGGREGATION_METHOD = "mean"

# Optional filters. Use None to keep all.
FILTER_LOCALES = None           # e.g. ["cs_CZ", "en_US"]
FILTER_CRITERIA = None          # e.g. ["coherence", "naturalness", "instruction_following"]
FILTER_JUDGE_MODELS = None      # e.g. ["GPT-4.1", "Llama-4-Maverick"]

# ==========================================
# OUTPUT FILES
# ==========================================
OUTPUT_JUDGE_PROMPT_CSV = Path("oeg_acc_eq_per_judge_per_prompt.csv")
OUTPUT_PROMPT_CSV = Path("oeg_acc_eq_one_value_per_prompt.csv")
OUTPUT_SUMMARY_CSV = Path("oeg_acc_eq_stability_46_prompts.csv")
OUTPUT_JSON = Path("oeg_acc_eq_stability_46_prompts.json")


def _get_params_from_scores(
    scores_human: np.ndarray,
    scores_judge: np.ndarray,
) -> Tuple[int, int, int, int, int]:
    """
    Same logic as corr_utils.py:
      C   = concordant
      D   = discordant
      T_h = tie in human only
      T_m = tie in judge only
      T_hm= tie in both
    """
    assert len(scores_human) == len(scores_judge), "Score vectors must have same length"

    C = D = T_h = T_m = T_hm = 0
    n = len(scores_human)

    for i in range(n):
        for j in range(i + 1, n):
            h_i, h_j = scores_human[i], scores_human[j]
            m_i, m_j = scores_judge[i], scores_judge[j]

            if h_i < h_j and m_i < m_j:
                C += 1
            elif h_i > h_j and m_i > m_j:
                C += 1
            elif h_i < h_j and m_i > m_j:
                D += 1
            elif h_i > h_j and m_i < m_j:
                D += 1
            elif h_i == h_j and m_i == m_j:
                T_hm += 1
            elif h_i == h_j:
                T_h += 1
            elif m_i == m_j:
                T_m += 1

    return C, D, T_h, T_m, T_hm


def acc_eq_from_scores(scores_human: np.ndarray, scores_judge: np.ndarray) -> float:
    """
    acc_eq = (C + T_hm) / (C + D + T_h + T_m + T_hm)
    """
    C, D, T_h, T_m, T_hm = _get_params_from_scores(scores_human, scores_judge)
    denom = C + D + T_h + T_m + T_hm
    return (C + T_hm) / denom if denom > 0 else 0.0


def load_and_align_data(human_csv: Path, judge_csv: Path) -> Tuple[pd.DataFrame, pd.DataFrame]:
    df_human = pd.read_csv(human_csv)
    df_judge = pd.read_csv(judge_csv)

    df_human["instance_key"] = (
        df_human["original_instance_id"].astype(str) + "_with_" + df_human["locale"].astype(str)
    )
    df_judge["instance_key"] = (
        df_judge["original_instance_id"].astype(str) + "_with_" + df_judge["locale"].astype(str)
    )

    if FILTER_LOCALES is not None:
        df_human = df_human[df_human["locale"].isin(FILTER_LOCALES)]
        df_judge = df_judge[df_judge["locale"].isin(FILTER_LOCALES)]

    if FILTER_CRITERIA is not None:
        df_human = df_human[df_human["criterion"].isin(FILTER_CRITERIA)]
        df_judge = df_judge[df_judge["criterion"].isin(FILTER_CRITERIA)]

    if FILTER_JUDGE_MODELS is not None:
        df_judge = df_judge[df_judge["judge_model_name"].isin(FILTER_JUDGE_MODELS)]

    # Keep only overlapping subsets, same spirit as judge_human_agreement.py
    for key in ["submission_system_name", "criterion", "instance_key"]:
        judge_keys = set(df_judge[key].unique())
        human_keys = set(df_human[key].unique())
        df_judge = df_judge[df_judge[key].isin(human_keys)]
        df_human = df_human[df_human[key].isin(judge_keys)]

    return df_human.copy(), df_judge.copy()


def compute_acc_eq_per_judge_per_prompt(
    df_human: pd.DataFrame,
    df_judge: pd.DataFrame,
) -> pd.DataFrame:
    """
    One row = one judge model × one locale × one criterion × one prompt.
    For that row:
      - collect 16 human scores (one per submission system)
      - collect 16 judge scores (same 16 submission systems)
      - compute one acc_eq value
    """
    rows: List[Dict] = []

    judge_models = sorted(df_judge["judge_model_name"].unique())
    criteria = sorted(df_judge["criterion"].unique())
    locales = sorted(df_judge["locale"].unique())

    for criterion in criteria:
        df_human_c = df_human[df_human["criterion"] == criterion]

        for locale in locales:
            df_human_cl = df_human_c[df_human_c["locale"] == locale]
            prompt_keys = sorted(df_human_cl["instance_key"].unique())

            for judge_model_name in judge_models:
                df_judge_j = df_judge[
                    (df_judge["judge_model_name"] == judge_model_name)
                    & (df_judge["criterion"] == criterion)
                    & (df_judge["locale"] == locale)
                ]

                judge_prompt_keys = set(df_judge_j["instance_key"].unique())
                common_prompt_keys = [k for k in prompt_keys if k in judge_prompt_keys]

                for instance_key in common_prompt_keys:
                    h = (
                        df_human_cl[df_human_cl["instance_key"] == instance_key]
                        .sort_values("submission_system_name")
                        .reset_index(drop=True)
                    )
                    j = (
                        df_judge_j[df_judge_j["instance_key"] == instance_key]
                        .sort_values("submission_system_name")
                        .reset_index(drop=True)
                    )

                    systems_h = list(h["submission_system_name"])
                    systems_j = list(j["submission_system_name"])
                    if systems_h != systems_j:
                        raise ValueError(
                            f"System mismatch for judge={judge_model_name}, criterion={criterion}, "
                            f"locale={locale}, prompt={instance_key}"
                        )

                    scores_human = h["score"].to_numpy(dtype=float)
                    scores_judge = j["score"].to_numpy(dtype=float)

                    if len(scores_human) != 16 or len(scores_judge) != 16:
                        raise ValueError(
                            f"Expected 16 submission systems, got {len(scores_human)} human and "
                            f"{len(scores_judge)} judge for prompt={instance_key}"
                        )

                    acc_eq = acc_eq_from_scores(scores_human, scores_judge)

                    rows.append(
                        {
                            "criterion": criterion,
                            "locale": locale,
                            "judge_model_name": judge_model_name,
                            "instance_key": instance_key,
                            "original_instance_id": h["original_instance_id"].iloc[0],
                            "acc_eq": acc_eq,
                        }
                    )

    result = pd.DataFrame(rows).sort_values(
        ["criterion", "locale", "original_instance_id", "judge_model_name"]
    ).reset_index(drop=True)
    return result


def aggregate_to_one_prompt_value(judge_prompt_df: pd.DataFrame) -> pd.DataFrame:
    """
    For each locale × criterion × prompt, aggregate the judge-specific acc_eq values
    into ONE prompt value. This gives exactly 46 values per locale × criterion.
    """
    grouped = judge_prompt_df.groupby(
        ["criterion", "locale", "instance_key", "original_instance_id"], sort=True
    )["acc_eq"]

    if JUDGE_AGGREGATION_METHOD == "mean":
        prompt_df = grouped.mean().reset_index(name="acc_eq_prompt")
    elif JUDGE_AGGREGATION_METHOD == "median":
        prompt_df = grouped.median().reset_index(name="acc_eq_prompt")
    elif JUDGE_AGGREGATION_METHOD == "min":
        prompt_df = grouped.min().reset_index(name="acc_eq_prompt")
    elif JUDGE_AGGREGATION_METHOD == "max":
        prompt_df = grouped.max().reset_index(name="acc_eq_prompt")
    else:
        raise ValueError("JUDGE_AGGREGATION_METHOD must be one of: mean, median, min, max")

    judge_dispersion = judge_prompt_df.groupby(
        ["criterion", "locale", "instance_key", "original_instance_id"], sort=True
    )["acc_eq"].agg(
        judge_mean="mean",
        judge_std="std",
        judge_min="min",
        judge_max="max",
        n_judges="count",
    ).reset_index()

    prompt_df = prompt_df.merge(
        judge_dispersion,
        on=["criterion", "locale", "instance_key", "original_instance_id"],
        how="left",
    )

    return prompt_df.sort_values(
        ["criterion", "locale", "original_instance_id"]
    ).reset_index(drop=True)


def summarize_46_prompt_values(prompt_df: pd.DataFrame) -> pd.DataFrame:
    """
    For each locale × criterion:
      take the 46 prompt values
      compute their descriptive statistics
    """
    rows: List[Dict] = []

    grouped = prompt_df.groupby(["criterion", "locale"], sort=True)

    for (criterion, locale), g in grouped:
        values = g["acc_eq_prompt"].to_numpy(dtype=float)
        n = len(values)

        if n == 0:
            continue

        rows.append(
            {
                "criterion": criterion,
                "locale": locale,
                "n_prompts": int(n),
                "judge_aggregation_method": JUDGE_AGGREGATION_METHOD if AGGREGATE_JUDGES_TO_ONE_PROMPT_VALUE else "none",
                "mean": float(values.mean()),
                "std": float(values.std(ddof=1)) if n > 1 else 0.0,
                "se": float(values.std(ddof=1) / np.sqrt(n)) if n > 1 else 0.0,
                "cv": float(values.std(ddof=1) / values.mean()) if n > 1 and values.mean() != 0 else np.nan,
                "min": float(values.min()),
                "q10": float(np.quantile(values, 0.10)),
                "q25": float(np.quantile(values, 0.25)),
                "median": float(np.quantile(values, 0.50)),
                "q75": float(np.quantile(values, 0.75)),
                "q90": float(np.quantile(values, 0.90)),
                "max": float(values.max()),
                "iqr": float(np.quantile(values, 0.75) - np.quantile(values, 0.25)),
                "range": float(values.max() - values.min()),
                "avg_judge_std_within_prompt": float(g["judge_std"].fillna(0).mean()),
                "avg_judge_range_within_prompt": float((g["judge_max"] - g["judge_min"]).mean()),
            }
        )

    return pd.DataFrame(rows).sort_values(["criterion", "locale"]).reset_index(drop=True)


def main() -> None:
    print("Loading and aligning data...")
    df_human, df_judge = load_and_align_data(HUMAN_CSV, JUDGE_CSV)
    print(f"Human rows after alignment: {len(df_human)}")
    print(f"Judge rows after alignment: {len(df_judge)}")

    print("Computing acc_eq for each judge × prompt × locale × criterion...")
    judge_prompt_df = compute_acc_eq_per_judge_per_prompt(df_human, df_judge)
    print(f"Rows at judge×prompt level: {len(judge_prompt_df)}")

    judge_prompt_df.to_csv(OUTPUT_JUDGE_PROMPT_CSV, index=False)

    if AGGREGATE_JUDGES_TO_ONE_PROMPT_VALUE:
        print(f"Aggregating judge-specific prompt acc_eq values using: {JUDGE_AGGREGATION_METHOD}")
        prompt_df = aggregate_to_one_prompt_value(judge_prompt_df)
    else:
        # Fallback: keep one row per judge×prompt; not the requested default behavior
        prompt_df = judge_prompt_df.rename(columns={"acc_eq": "acc_eq_prompt"}).copy()
        prompt_df["judge_mean"] = prompt_df["acc_eq_prompt"]
        prompt_df["judge_std"] = 0.0
        prompt_df["judge_min"] = prompt_df["acc_eq_prompt"]
        prompt_df["judge_max"] = prompt_df["acc_eq_prompt"]
        prompt_df["n_judges"] = 1

    prompt_df.to_csv(OUTPUT_PROMPT_CSV, index=False)
    print(f"Rows at one-value-per-prompt level: {len(prompt_df)}")

    print("Summarizing the 46 prompt values for each locale × criterion...")
    summary_df = summarize_46_prompt_values(prompt_df)
    summary_df.to_csv(OUTPUT_SUMMARY_CSV, index=False)

    OUTPUT_JSON.write_text(
        json.dumps(
            {
                "settings": {
                    "human_csv": str(HUMAN_CSV),
                    "judge_csv": str(JUDGE_CSV),
                    "aggregate_judges_to_one_prompt_value": AGGREGATE_JUDGES_TO_ONE_PROMPT_VALUE,
                    "judge_aggregation_method": JUDGE_AGGREGATION_METHOD,
                    "filter_locales": FILTER_LOCALES,
                    "filter_criteria": FILTER_CRITERIA,
                    "filter_judge_models": FILTER_JUDGE_MODELS,
                },
                "summary_rows": summary_df.to_dict(orient="records"),
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print()
    print("Saved:")
    print(f"  per-judge-per-prompt CSV: {OUTPUT_JUDGE_PROMPT_CSV}")
    print(f"  one-value-per-prompt CSV: {OUTPUT_PROMPT_CSV}")
    print(f"  summary CSV:              {OUTPUT_SUMMARY_CSV}")
    print(f"  summary JSON:             {OUTPUT_JSON}")
    print()
    print(summary_df.to_string(index=False))


if __name__ == "__main__":
    main()
