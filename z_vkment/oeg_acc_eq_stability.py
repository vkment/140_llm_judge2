
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd

# =========================
# INPUT / OUTPUT SETTINGS
# =========================
HUMAN_CSV = Path("oeg_human_eval_data.csv")
JUDGE_CSV = Path("oeg_judge_run2_submission_data.csv")

OUTPUT_SUMMARY_CSV = Path("oeg_acc_eq_stability_summary.csv")
OUTPUT_PROMPT_LEVEL_CSV = Path("oeg_acc_eq_stability_prompt_level.csv")
OUTPUT_JSON = Path("oeg_acc_eq_stability_summary.json")

FILTER_LOCALES = None           # e.g. ["cs_CZ", "en_US"]
FILTER_CRITERIA = None          # e.g. ["coherence", "naturalness", "instruction_following"]
FILTER_JUDGE_MODELS = None      # e.g. ["Llama-4-Maverick"]

INSTABILITY_THRESHOLD = 0.10


def _get_params_from_scores(
    scores_human: np.ndarray,
    scores_judge: np.ndarray,
) -> Tuple[int, int, int, int, int]:
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
    C, D, T_h, T_m, T_hm = _get_params_from_scores(scores_human, scores_judge)
    denom = C + D + T_h + T_m + T_hm
    return (C + T_hm) / denom if denom > 0 else 0.0


def load_and_align_data(human_csv: Path, judge_csv: Path) -> Tuple[pd.DataFrame, pd.DataFrame]:
    df_human = pd.read_csv(human_csv)
    df_judge = pd.read_csv(judge_csv)

    df_human["original_instance_id_with_locale"] = (
        df_human["original_instance_id"].astype(str) + "_with_" + df_human["locale"].astype(str)
    )
    df_judge["original_instance_id_with_locale"] = (
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

    for filter_key in ["submission_system_name", "criterion", "original_instance_id_with_locale"]:
        judge_keys = set(df_judge[filter_key].unique())
        human_keys = set(df_human[filter_key].unique())
        df_judge = df_judge[df_judge[filter_key].isin(human_keys)]
        df_human = df_human[df_human[filter_key].isin(judge_keys)]

    return df_human.copy(), df_judge.copy()


def compute_prompt_level_acc_eq(
    df_human: pd.DataFrame,
    df_judge: pd.DataFrame,
) -> pd.DataFrame:
    rows: List[Dict] = []

    judge_models = sorted(df_judge["judge_model_name"].unique())
    criteria = sorted(df_judge["criterion"].unique())
    locales = sorted(df_judge["locale"].unique())

    for judge_model_name in judge_models:
        df_judge_model = df_judge[df_judge["judge_model_name"] == judge_model_name]

        for criterion in criteria:
            df_human_c = df_human[df_human["criterion"] == criterion]
            df_judge_c = df_judge_model[df_judge_model["criterion"] == criterion]

            for locale in locales:
                df_human_cl = df_human_c[df_human_c["locale"] == locale]
                df_judge_cl = df_judge_c[df_judge_c["locale"] == locale]

                instances = sorted(set(df_human_cl["original_instance_id_with_locale"].unique()))
                judge_instances = set(df_judge_cl["original_instance_id_with_locale"].unique())
                instances = [inst for inst in instances if inst in judge_instances]

                for instance in instances:
                    h = df_human_cl[df_human_cl["original_instance_id_with_locale"] == instance]
                    j = df_judge_cl[df_judge_cl["original_instance_id_with_locale"] == instance]

                    h = h.sort_values("submission_system_name")
                    j = j.sort_values("submission_system_name")

                    systems_h = list(h["submission_system_name"])
                    systems_j = list(j["submission_system_name"])
                    if systems_h != systems_j:
                        raise ValueError(
                            f"System mismatch for judge={judge_model_name}, "
                            f"criterion={criterion}, locale={locale}, instance={instance}"
                        )

                    scores_human = h["score"].to_numpy(dtype=float)
                    scores_judge = j["score"].to_numpy(dtype=float)

                    if len(scores_human) != 16 or len(scores_judge) != 16:
                        raise ValueError(
                            f"Expected 16 systems, got {len(scores_human)} human and "
                            f"{len(scores_judge)} judge for instance={instance}"
                        )

                    value = acc_eq_from_scores(scores_human, scores_judge)

                    rows.append(
                        {
                            "judge_model_name": judge_model_name,
                            "criterion": criterion,
                            "locale": locale,
                            "original_instance_id_with_locale": instance,
                            "original_instance_id": instance.split("_with_")[0],
                            "acc_eq_prompt": value,
                        }
                    )

    result = pd.DataFrame(rows)
    return result.sort_values(
        ["judge_model_name", "criterion", "locale", "original_instance_id_with_locale"]
    ).reset_index(drop=True)


def add_prompt_deviation_columns(prompt_level_df: pd.DataFrame) -> pd.DataFrame:
    df = prompt_level_df.copy()
    means = (
        df.groupby(["judge_model_name", "criterion", "locale"])["acc_eq_prompt"]
        .mean()
        .rename("group_mean")
        .reset_index()
    )
    df = df.merge(means, on=["judge_model_name", "criterion", "locale"], how="left")
    df["abs_deviation_from_group_mean"] = (df["acc_eq_prompt"] - df["group_mean"]).abs()
    df["is_unstable_abs_dev_gt_threshold"] = df["abs_deviation_from_group_mean"] > INSTABILITY_THRESHOLD
    return df


def summarize_stability(prompt_level_df: pd.DataFrame) -> pd.DataFrame:
    out_rows: List[Dict] = []

    grouped = prompt_level_df.groupby(["judge_model_name", "criterion", "locale"], sort=True)

    for (judge_model_name, criterion, locale), group in grouped:
        values = group["acc_eq_prompt"].to_numpy(dtype=float)
        n = len(values)

        mean = float(values.mean()) if n else np.nan
        std = float(values.std(ddof=1)) if n > 1 else 0.0
        se = float(std / np.sqrt(n)) if n > 1 else 0.0
        min_v = float(values.min()) if n else np.nan
        max_v = float(values.max()) if n else np.nan
        q10 = float(np.quantile(values, 0.10)) if n else np.nan
        q25 = float(np.quantile(values, 0.25)) if n else np.nan
        q50 = float(np.quantile(values, 0.50)) if n else np.nan
        q75 = float(np.quantile(values, 0.75)) if n else np.nan
        q90 = float(np.quantile(values, 0.90)) if n else np.nan
        iqr = q75 - q25 if n else np.nan
        cv = float(std / mean) if n > 1 and mean != 0 else np.nan

        deviations = np.abs(values - mean)
        unstable_count = int((deviations > INSTABILITY_THRESHOLD).sum()) if n else 0
        unstable_share = float(unstable_count / n) if n else np.nan

        out_rows.append(
            {
                "judge_model_name": judge_model_name,
                "criterion": criterion,
                "locale": locale,
                "n_prompts": int(n),
                "mean": mean,
                "std": std,
                "se": se,
                "cv": cv,
                "min": min_v,
                "q10": q10,
                "q25": q25,
                "median": q50,
                "q75": q75,
                "q90": q90,
                "max": max_v,
                "iqr": iqr,
                "range": max_v - min_v if n else np.nan,
                f"unstable_count_abs_dev_gt_{INSTABILITY_THRESHOLD:.2f}": unstable_count,
                f"unstable_share_abs_dev_gt_{INSTABILITY_THRESHOLD:.2f}": unstable_share,
            }
        )

    return pd.DataFrame(out_rows).sort_values(
        ["criterion", "locale", "std"], ascending=[True, True, False]
    ).reset_index(drop=True)


def main() -> None:
    print("Loading and aligning data...")
    df_human, df_judge = load_and_align_data(HUMAN_CSV, JUDGE_CSV)

    print(f"Human rows after alignment: {len(df_human)}")
    print(f"Judge rows after alignment: {len(df_judge)}")

    print("Computing prompt-level acc_eq values...")
    prompt_level_df = compute_prompt_level_acc_eq(df_human, df_judge)
    prompt_level_df = add_prompt_deviation_columns(prompt_level_df)

    print(f"Prompt-level rows: {len(prompt_level_df)}")

    print("Summarizing stability...")
    summary_df = summarize_stability(prompt_level_df)

    prompt_level_df.to_csv(OUTPUT_PROMPT_LEVEL_CSV, index=False)
    summary_df.to_csv(OUTPUT_SUMMARY_CSV, index=False)

    OUTPUT_JSON.write_text(
        json.dumps(
            {
                "settings": {
                    "human_csv": str(HUMAN_CSV),
                    "judge_csv": str(JUDGE_CSV),
                    "filter_locales": FILTER_LOCALES,
                    "filter_criteria": FILTER_CRITERIA,
                    "filter_judge_models": FILTER_JUDGE_MODELS,
                    "instability_threshold": INSTABILITY_THRESHOLD,
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
    print(f"  prompt-level CSV: {OUTPUT_PROMPT_LEVEL_CSV}")
    print(f"  summary CSV:      {OUTPUT_SUMMARY_CSV}")
    print(f"  summary JSON:     {OUTPUT_JSON}")
    print()
    print(summary_df.head(20).to_string(index=False))


if __name__ == "__main__":
    main()
