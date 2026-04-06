
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd

# =========================
# INPUT FILES
# =========================
HUMAN_CSV = Path("oeg_human_eval_data.csv")
JUDGE_CSV = Path("oeg_judge_run2_submission_data.csv")

# Optional filters. Use None to keep all.
FILTER_LOCALES = None           # e.g. ["cs_CZ"]
FILTER_CRITERIA = None          # e.g. ["coherence"]
FILTER_JUDGE_MODELS = None      # e.g. ["GPT-4.1", "Llama-4-Maverick"]

# Output files
OUTPUT_PROMPT_LEVEL_CSV = Path("oeg_acc_eq_prompt_level_by_judge.csv")
OUTPUT_SUMMARY_CSV = Path("oeg_acc_eq_summary_46prompts_by_judge.csv")
OUTPUT_JSON = Path("oeg_acc_eq_summary_46prompts_by_judge.json")


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

    # Keep only overlapping subsets
    for key in ["submission_system_name", "criterion", "instance_key"]:
        judge_keys = set(df_judge[key].unique())
        human_keys = set(df_human[key].unique())
        df_judge = df_judge[df_judge[key].isin(human_keys)]
        df_human = df_human[df_human[key].isin(judge_keys)]

    return df_human.copy(), df_judge.copy()


def compute_prompt_level_acc_eq(df_human: pd.DataFrame, df_judge: pd.DataFrame) -> pd.DataFrame:
    """
    One row = one judge_model_name × criterion × locale × prompt(instance).
    acc_eq is computed from the two aligned 16-dimensional score vectors:
      - 16 human scores across submission systems
      - 16 judge scores across submission systems
    """
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

                instance_keys = sorted(set(df_human_cl["instance_key"].unique()))
                judge_instance_keys = set(df_judge_cl["instance_key"].unique())
                instance_keys = [k for k in instance_keys if k in judge_instance_keys]

                for instance_key in instance_keys:
                    h = (
                        df_human_cl[df_human_cl["instance_key"] == instance_key]
                        .sort_values("submission_system_name")
                        .reset_index(drop=True)
                    )
                    j = (
                        df_judge_cl[df_judge_cl["instance_key"] == instance_key]
                        .sort_values("submission_system_name")
                        .reset_index(drop=True)
                    )

                    systems_h = list(h["submission_system_name"])
                    systems_j = list(j["submission_system_name"])
                    if systems_h != systems_j:
                        raise ValueError(
                            f"System mismatch for judge={judge_model_name}, "
                            f"criterion={criterion}, locale={locale}, instance={instance_key}"
                        )

                    scores_human = h["score"].to_numpy(dtype=float)
                    scores_judge = j["score"].to_numpy(dtype=float)

                    if len(scores_human) != 16 or len(scores_judge) != 16:
                        raise ValueError(
                            f"Expected 16 systems, got {len(scores_human)} human and "
                            f"{len(scores_judge)} judge for instance={instance_key}"
                        )

                    rows.append(
                        {
                            "judge_model_name": judge_model_name,
                            "criterion": criterion,
                            "locale": locale,
                            "instance_key": instance_key,
                            "original_instance_id": h["original_instance_id"].iloc[0],
                            "acc_eq_prompt": acc_eq_from_scores(scores_human, scores_judge),
                        }
                    )

    return pd.DataFrame(rows).sort_values(
        ["judge_model_name", "criterion", "locale", "original_instance_id"]
    ).reset_index(drop=True)


def summarize_by_judge_locale_criterion(prompt_df: pd.DataFrame) -> pd.DataFrame:
    """
    For each judge_model_name × criterion × locale:
      summarize the 46 prompt-level acc_eq values.
    """
    rows: List[Dict] = []

    grouped = prompt_df.groupby(["judge_model_name", "criterion", "locale"], sort=True)

    for (judge_model_name, criterion, locale), g in grouped:
        values = g["acc_eq_prompt"].to_numpy(dtype=float)
        n = len(values)

        rows.append(
            {
                "judge_model_name": judge_model_name,
                "criterion": criterion,
                "locale": locale,
                "n_prompts": int(n),
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
            }
        )

    return pd.DataFrame(rows).sort_values(
        ["criterion", "locale", "mean"], ascending=[True, True, False]
    ).reset_index(drop=True)


def main() -> None:
    print("Loading and aligning data...")
    df_human, df_judge = load_and_align_data(HUMAN_CSV, JUDGE_CSV)
    print(f"Human rows after alignment: {len(df_human)}")
    print(f"Judge rows after alignment: {len(df_judge)}")

    print("Computing prompt-level acc_eq for each chosen judge...")
    prompt_df = compute_prompt_level_acc_eq(df_human, df_judge)
    print(f"Prompt-level rows: {len(prompt_df)}")

    print("Summarizing the 46 prompt values for each judge × locale × criterion...")
    summary_df = summarize_by_judge_locale_criterion(prompt_df)

    prompt_df.to_csv(OUTPUT_PROMPT_LEVEL_CSV, index=False)
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
