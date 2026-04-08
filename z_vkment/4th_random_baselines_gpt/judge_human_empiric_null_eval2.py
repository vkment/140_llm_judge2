import json
import math
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd

# =========================================================
# KONFIGURACE
# =========================================================
# judge_input_files = [
#     "oeg_judge_run2_submission_data.csv",
# ]

judge_input_files = [
"z_vkment/llm_eval_copies/oeg_judge_outloc36_2_submission_data_Qwen3.5-35B-A3B_h13.csv",
"z_vkment/llm_eval_copies/oeg_judge_outloc41_3_submission_data_gemma-4-31B-it_h23.csv",
"z_vkment/llm_eval_copies/oeg_judge_outloc45_submission_data_gemma-4-E4B-it_h23.csv",
"z_vkment/llm_eval_copies/oeg_judge_outloc46_1_submission_data_gemma-4-26B-A4B-it_h23.csv",
"z_vkment/llm_eval_copies/oeg_judge_outloc46_8_submission_data_gemma-4-31B-it_hc14.csv",
"z_vkment/llm_eval_copies/oeg_judge_outloc47_1_submission_data_gemma-3-4b-it_h23.csv",
"z_vkment/llm_eval_copies/oeg_judge_outloc48_1_submission_data_gemma-3-12b-it_h23.csv",
"z_vkment/llm_eval_copies/oeg_judge_outloc49_1_submission_data_gemma-3-27b-it_h23.csv",
"z_vkment/llm_eval_copies/oeg_judge_outloc50_1_submission_data_M-Prometheus-7B_h23.csv",
"z_vkment/llm_eval_copies/oeg_judge_outloc50_2_submission_data_M-Prometheus-14B_h23.csv",
"z_vkment/llm_eval_copies/oeg_judge_outloc51_1_submission_data_EuroLLM-9B-Instruct_h23.csv",
"z_vkment/llm_eval_copies/oeg_judge_outloc52_3_submission_data_EuroLLM-22B-Instruct-2512_h23.csv",
"z_vkment/llm_eval_copies/oeg_judge_outloc53_2_submission_data_Magistral-Small-2509_h23.csv",
"z_vkment/llm_eval_copies/oeg_judge_outloc5_submission_data_aya-expanse-8b.csv",
"z_vkment/llm_eval_copies/oeg_judge_outloc7_submission_data_Llama-3.1-8B.csv",
"z_vkment/llm_eval_copies/oeg_judge_out_submission_data4_llama-4-maverick.csv"
]



human_input_file = "oeg_human_eval_data.csv"
null_distributions_file = "z_vkment/calculate_random_empiric_null_distributions.json"

output_json =           "z_vkment/judge_llms_w_empiric_null_results.json"

output_md =             "z_vkment/judge_human_empiric_null_results_written2.md"
output_json_schema_md = "z_vkment/judge_human_empiric_null_results_schema_written2.md"

save_instance_level_details = True
strict_missing_null_vector = True
chance_tolerance = 1e-12


# =========================================================
# METRIKY
# =========================================================
def _get_params_from_ranks(rank_human: List[float], rank_metric: List[float]) -> Tuple[int, int, int, int, int]:
    assert len(rank_human) == len(rank_metric), "Rank lists must be of the same length"

    C = D = T_h = T_m = T_hm = 0
    for i in range(len(rank_human)):
        for j in range(i + 1, len(rank_human)):
            if rank_human[i] < rank_human[j] and rank_metric[i] < rank_metric[j]:
                C += 1
            elif rank_human[i] > rank_human[j] and rank_metric[i] > rank_metric[j]:
                C += 1
            elif rank_human[i] < rank_human[j] and rank_metric[i] > rank_metric[j]:
                D += 1
            elif rank_human[i] > rank_human[j] and rank_metric[i] < rank_metric[j]:
                D += 1
            elif rank_human[i] == rank_human[j] and rank_metric[i] == rank_metric[j]:
                T_hm += 1
            elif rank_human[i] == rank_human[j]:
                T_h += 1
            elif rank_metric[i] == rank_metric[j]:
                T_m += 1

    return C, D, T_h, T_m, T_hm


def my_acc_eq(rank_human: List[float], rank_metric: List[float]) -> float:
    C, D, T_h, T_m, T_hm = _get_params_from_ranks(rank_human, rank_metric)
    denominator = C + D + T_h + T_m + T_hm
    return (C + T_hm) / denominator if denominator > 0 else 0.0


def my_pairwise_acc(rank_human: List[float], rank_metric: List[float]) -> float:
    C, D, _, _, _ = _get_params_from_ranks(rank_human, rank_metric)
    denominator = C + D
    return C / denominator if denominator > 0 else 0.0


# =========================================================
# POMOCNÉ FUNKCE
# =========================================================
def log(message: str) -> None:
    print(f"[INFO] {message}")


class DataConsistencyError(Exception):
    pass


def load_csv_files(paths: List[str], expected_columns: List[str], label: str) -> pd.DataFrame:
    frames = []
    for path in paths:
        log(f"Loading {label} CSV: {path}")
        df = pd.read_csv(path)
        missing = [c for c in expected_columns if c not in df.columns]
        if missing:
            raise DataConsistencyError(f"Missing columns in {path}: {missing}")
        frames.append(df[expected_columns].copy())

    if not frames:
        raise DataConsistencyError(f"No {label} input files specified.")

    combined = pd.concat(frames, ignore_index=True)
    log(f"Loaded {len(combined)} rows for {label}.")
    return combined



def load_null_distributions(path: str) -> Dict[Tuple[str, str, str], dict]:
    log(f"Loading null distributions JSON: {path}")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    vectors = data.get("vectors")
    if vectors is None:
        raise DataConsistencyError("Null distributions JSON does not contain 'vectors'.")

    mapping: Dict[Tuple[str, str, str], dict] = {}
    for record in vectors:
        key = (record["locale"], record["criterion"], record["original_instance_id"])
        pmf_probs = record.get("pmf_probs")
        if pmf_probs is None or len(pmf_probs) != 121:
            raise DataConsistencyError(f"Invalid or missing pmf_probs for key {key}.")
        if not math.isclose(sum(pmf_probs), 1.0, rel_tol=0.0, abs_tol=1e-9):
            raise DataConsistencyError(f"pmf_probs do not sum to 1 for key {key}.")
        mapping[key] = record

    log(f"Loaded {len(mapping)} per-vector null distributions.")
    return mapping



def add_instance_key(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["original_instance_id_with_locale"] = (
        df["original_instance_id"].astype(str) + "_with_" + df["locale"].astype(str)
    )
    return df



def filter_to_common_subset(df_judge: pd.DataFrame, df_human: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    for filter_key in ["submission_system_name", "criterion", "original_instance_id_with_locale"]:
        judge_keys = set(df_judge[filter_key].unique())
        human_keys = set(df_human[filter_key].unique())
        df_judge = df_judge[df_judge[filter_key].isin(human_keys)]
        df_human = df_human[df_human[filter_key].isin(judge_keys)]
    return df_judge, df_human



def group_vectors(df: pd.DataFrame, score_label: str) -> Dict[Tuple[str, str, str, str], dict]:
    result: Dict[Tuple[str, str, str, str], dict] = {}
    group_cols = ["judge_model_name", "locale", "criterion", "original_instance_id"]
    for key, g in df.groupby(group_cols):
        g = g.sort_values("submission_system_name")
        systems = g["submission_system_name"].tolist()
        scores = g[score_label].astype(float).tolist()
        if len(systems) != 16:
            raise DataConsistencyError(
                f"Expected 16 systems for {key}, got {len(systems)}."
            )
        if len(set(systems)) != 16:
            raise DataConsistencyError(f"Duplicate submission_system_name for {key}.")
        result[key] = {
            "systems_order": systems,
            "scores": scores,
        }
    return result



def build_human_lookup(df_human: pd.DataFrame) -> Dict[Tuple[str, str, str], dict]:
    result: Dict[Tuple[str, str, str], dict] = {}
    for key, g in df_human.groupby(["locale", "criterion", "original_instance_id"]):
        g = g.sort_values("submission_system_name")
        systems = g["submission_system_name"].tolist()
        scores = g["score"].astype(float).tolist()
        if len(systems) != 16:
            raise DataConsistencyError(
                f"Expected 16 human systems for {key}, got {len(systems)}."
            )
        if len(set(systems)) != 16:
            raise DataConsistencyError(f"Duplicate human submission_system_name for {key}.")
        result[key] = {
            "systems_order": systems,
            "scores": scores,
        }
    return result



def acc_eq_to_index(acc_eq: float) -> int:
    k = int(round(acc_eq * 120))
    if k < 0 or k > 120:
        raise DataConsistencyError(f"acc_eq index out of range: acc_eq={acc_eq}, k={k}")
    if not math.isclose(acc_eq, k / 120.0, abs_tol=1e-9, rel_tol=0.0):
        raise DataConsistencyError(f"acc_eq does not lie on 1/120 grid: acc_eq={acc_eq}, k={k}")
    return k



def percentile_from_pmf(pmf_probs: List[float], k: int) -> float:
    if k == 0:
        return 0.5 * pmf_probs[0]
    return float(sum(pmf_probs[:k]) + 0.5 * pmf_probs[k])



def aggregate_records(records: List[dict]) -> dict:
    if not records:
        return {
            "n_instances": 0,
            "mean_acc_eq": None,
            "mean_percentile": None,
            "mean_centered_skill": None,
            "std_centered_skill": None,
            "median_centered_skill": None,
            "n_above_chance": 0,
            "n_below_chance": 0,
            "n_equal_chance": 0,
        }

    acc_vals = np.array([r["acc_eq"] for r in records], dtype=float)
    percentile_vals = np.array([r["percentile"] for r in records], dtype=float)
    skill_vals = np.array([r["centered_skill"] for r in records], dtype=float)

    n_above = int(np.sum(skill_vals > chance_tolerance))
    n_below = int(np.sum(skill_vals < -chance_tolerance))
    n_equal = int(len(skill_vals) - n_above - n_below)

    return {
        "n_instances": int(len(records)),
        "mean_acc_eq": float(np.mean(acc_vals)),
        "mean_percentile": float(np.mean(percentile_vals)),
        "mean_centered_skill": float(np.mean(skill_vals)),
        "std_centered_skill": float(np.std(skill_vals, ddof=0)),
        "median_centered_skill": float(np.median(skill_vals)),
        "n_above_chance": n_above,
        "n_below_chance": n_below,
        "n_equal_chance": n_equal,
    }



def compute_system_level_ranking_accuracy(df_human: pd.DataFrame, df_judge: pd.DataFrame) -> Dict[str, float]:
    system_rank_by_human = (
        df_human.groupby("submission_system_name")["score"].mean().rank(method="min", ascending=False)
    )
    system_names_human = list(system_rank_by_human.index)
    rank_human = system_rank_by_human.values

    results = {}
    for judge_model_name in sorted(df_judge["judge_model_name"].unique()):
        df_subset = df_judge[df_judge["judge_model_name"] == judge_model_name]
        system_rank_by_judge = (
            df_subset.groupby("submission_system_name")["score"].mean().rank(method="min", ascending=False)
        )
        system_names_judge = list(system_rank_by_judge.index)
        rank_judge = system_rank_by_judge.values

        if system_names_human != system_names_judge:
            raise DataConsistencyError(
                f"System names mismatch for judge_model_name={judge_model_name}."
            )
        results[judge_model_name] = float(my_pairwise_acc(rank_human, rank_judge))
    return results



def nested_defaultdict_list():
    return defaultdict(list)


# =========================================================
# MAIN
# =========================================================
expected_columns = [
    "judge_model_name",
    "criterion",
    "submission_system_name",
    "original_instance_id",
    "locale",
    "score",
]

log("Starting evaluation.")
df_judge = load_csv_files(judge_input_files, expected_columns, label="judge")
df_human = load_csv_files([human_input_file], expected_columns, label="human")
null_lookup = load_null_distributions(null_distributions_file)

if not (df_human["judge_model_name"] == "human").all():
    raise DataConsistencyError("Human input file contains non-human judge_model_name values.")

df_judge["score"] = df_judge["score"].astype(float)
df_human["score"] = df_human["score"].astype(float)

df_judge = add_instance_key(df_judge)
df_human = add_instance_key(df_human)

log("Filtering judge and human data to common subset.")
df_judge, df_human = filter_to_common_subset(df_judge, df_human)
log(f"Rows after filtering: judge={len(df_judge)}, human={len(df_human)}")

judge_models = sorted(df_judge["judge_model_name"].unique())
log(f"Judge models found: {judge_models}")

human_lookup = build_human_lookup(df_human)
judge_vector_lookup = group_vectors(df_judge, score_label="score")

warnings: List[str] = []
instance_details: List[dict] = []

records_by_judge: Dict[str, List[dict]] = defaultdict(list)
records_by_judge_criterion: Dict[str, Dict[str, List[dict]]] = defaultdict(nested_defaultdict_list)
records_by_judge_locale: Dict[str, Dict[str, List[dict]]] = defaultdict(nested_defaultdict_list)
records_by_judge_locale_criterion: Dict[str, Dict[str, Dict[str, List[dict]]]] = defaultdict(lambda: defaultdict(nested_defaultdict_list))

log("Computing instance-level acc_eq, percentile, and centered skill.")
for judge_model_name in judge_models:
    judge_keys = [k for k in judge_vector_lookup.keys() if k[0] == judge_model_name]
    log(f"Processing judge_model_name={judge_model_name} with {len(judge_keys)} vectors.")
    for judge_key in sorted(judge_keys, key=lambda x: (x[1], x[2], x[3])):
        _, locale, criterion, original_instance_id = judge_key
        human_key = (locale, criterion, original_instance_id)
        if human_key not in human_lookup:
            warning = f"Missing human vector for {judge_key}; skipping."
            warnings.append(warning)
            if strict_missing_null_vector:
                raise DataConsistencyError(warning)
            continue
        if human_key not in null_lookup:
            warning = f"Missing null distribution for {judge_key}; skipping."
            warnings.append(warning)
            if strict_missing_null_vector:
                raise DataConsistencyError(warning)
            continue

        human_vector = human_lookup[human_key]
        judge_vector = judge_vector_lookup[judge_key]

        if human_vector["systems_order"] != judge_vector["systems_order"]:
            raise DataConsistencyError(
                f"System order mismatch for {judge_key}."
            )

        scores_human = human_vector["scores"]
        scores_judge = judge_vector["scores"]
        acc_eq = float(my_acc_eq(scores_human, scores_judge))
        k = acc_eq_to_index(acc_eq)

        pmf_probs = null_lookup[human_key]["pmf_probs"]
        percentile = percentile_from_pmf(pmf_probs, k)
        centered_skill = 2.0 * percentile - 1.0

        rec = {
            "judge_model_name": judge_model_name,
            "locale": locale,
            "criterion": criterion,
            "original_instance_id": original_instance_id,
            "acc_eq": acc_eq,
            "acc_eq_index": k,
            "percentile": float(percentile),
            "percentile_percent": float(percentile * 100.0),
            "centered_skill": float(centered_skill),
            "centered_skill_percent": float(centered_skill * 100.0),
        }
        instance_details.append(rec)
        records_by_judge[judge_model_name].append(rec)
        records_by_judge_criterion[judge_model_name][criterion].append(rec)
        records_by_judge_locale[judge_model_name][locale].append(rec)
        records_by_judge_locale_criterion[judge_model_name][locale][criterion].append(rec)

log("Computing legacy metrics (ranking_accuracy and classical acc_eq aggregates).")
ranking_accuracy = compute_system_level_ranking_accuracy(df_human, df_judge)

legacy_acc_eq_by_criterion: Dict[str, Dict[str, float]] = defaultdict(dict)
legacy_acc_eq_average: Dict[str, float] = {}
for judge_model_name in judge_models:
    criterion_means = {}
    for criterion in sorted(records_by_judge_criterion[judge_model_name].keys()):
        vals = [r["acc_eq"] for r in records_by_judge_criterion[judge_model_name][criterion]]
        criterion_means[criterion] = float(np.mean(vals))
    legacy_acc_eq_by_criterion[judge_model_name] = criterion_means
    legacy_acc_eq_average[judge_model_name] = float(np.mean(list(criterion_means.values()))) if criterion_means else None

log("Aggregating empiric-null calibrated metrics.")
empiric_null_overall = {}
empiric_null_by_criterion = {}
empiric_null_by_locale = {}
empiric_null_by_locale_and_criterion = {}

for judge_model_name in judge_models:
    empiric_null_overall[judge_model_name] = aggregate_records(records_by_judge[judge_model_name])

    empiric_null_by_criterion[judge_model_name] = {}
    for criterion in sorted(records_by_judge_criterion[judge_model_name].keys()):
        empiric_null_by_criterion[judge_model_name][criterion] = aggregate_records(
            records_by_judge_criterion[judge_model_name][criterion]
        )

    empiric_null_by_locale[judge_model_name] = {}
    for locale in sorted(records_by_judge_locale[judge_model_name].keys()):
        empiric_null_by_locale[judge_model_name][locale] = aggregate_records(
            records_by_judge_locale[judge_model_name][locale]
        )

    empiric_null_by_locale_and_criterion[judge_model_name] = {}
    for locale in sorted(records_by_judge_locale_criterion[judge_model_name].keys()):
        empiric_null_by_locale_and_criterion[judge_model_name][locale] = {}
        for criterion in sorted(records_by_judge_locale_criterion[judge_model_name][locale].keys()):
            empiric_null_by_locale_and_criterion[judge_model_name][locale][criterion] = aggregate_records(
                records_by_judge_locale_criterion[judge_model_name][locale][criterion]
            )

results = {
    "metadata": {
        "judge_input_files": judge_input_files,
        "human_input_file": human_input_file,
        "null_distributions_file": null_distributions_file,
        "save_instance_level_details": save_instance_level_details,
        "strict_missing_null_vector": strict_missing_null_vector,
        "chance_tolerance": chance_tolerance,
    },
    "warnings": warnings,
    "judge_models": judge_models,
    "legacy_metrics": {
        "ranking_accuracy": ranking_accuracy,
        "acc_eq_average": legacy_acc_eq_average,
        "acc_eq_by_criterion": legacy_acc_eq_by_criterion,
    },
    "empiric_null_overall": empiric_null_overall,
    "empiric_null_by_criterion": empiric_null_by_criterion,
    "empiric_null_by_locale": empiric_null_by_locale,
    "empiric_null_by_locale_and_criterion": empiric_null_by_locale_and_criterion,
}
if save_instance_level_details:
    results["instance_level_details"] = instance_details

log(f"Writing JSON results to {output_json}")
with open(output_json, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2)

program_md = f"""# Program: judge_human_empiric_null_eval.py

## Účel

Program vyhodnocuje LLM-judge proti human hodnocení.

Vedle původního `acc_eq` a `ranking_accuracy` počítá i nové metriky kalibrované vůči předpočítaným empiric-null distribucím z `{null_distributions_file}`.

## Vstupy

- judge CSV soubory: `{judge_input_files}`
- human CSV soubor: `{human_input_file}`
- JSON s per-vector null distribucemi: `{null_distributions_file}`

## Jednotka vyhodnocení

Jedna instance je určena trojicí:
- `locale`
- `criterion`
- `original_instance_id`

Pro každou instanci se vezme 16 systémů (`submission_system_name`), human i judge skóre se seřadí podle `submission_system_name` a spočte se `acc_eq`.

## Nové metriky

Pro každé pozorované `acc_eq` se podle per-vector PMF spočte:

- `percentile = P(X < x) + 0.5 * P(X = x)`
- `centered_skill = 2 * percentile - 1`

Interpretace:
- `percentile ~= 0.5` znamená úroveň náhody
- `centered_skill = 0` znamená úroveň náhody
- `centered_skill > 0` znamená lepší než náhoda
- `centered_skill < 0` znamená horší než náhoda

## Agregace

Program vytváří agregace:
- overall
- by criterion
- by locale
- by locale x criterion

Pro každou agregaci ukládá:
- `mean_acc_eq`
- `mean_percentile`
- `mean_centered_skill`
- `std_centered_skill`
- `median_centered_skill`
- `n_above_chance`
- `n_below_chance`
- `n_equal_chance`

## Poznámka

Program sám nepřepočítává null distribuce. Pouze čte již předpočítané JSON rozdělení a používá jej jako lookup tabulku pro převod `acc_eq -> percentile -> centered_skill`.
"""

schema_md = f"""# Struktura výstupního JSON

## Root keys

- `metadata` — informace o vstupních souborech a nastavení programu
- `warnings` — případná upozornění
- `judge_models` — seznam všech zpracovaných `judge_model_name`
- `legacy_metrics` — historické metriky kompatibilní s dřívějším vyhodnocením
- `empiric_null_overall` — agregace přes všechny instance
- `empiric_null_by_criterion` — agregace po criterion
- `empiric_null_by_locale` — agregace po locale
- `empiric_null_by_locale_and_criterion` — agregace po locale x criterion
- `instance_level_details` — volitelně detailní záznamy po jednotlivých instancích

## legacy_metrics

Obsahuje:
- `ranking_accuracy`
- `acc_eq_average`
- `acc_eq_by_criterion`

## Agregační záznam

Každý agregační záznam obsahuje:
- `n_instances`
- `mean_acc_eq`
- `mean_percentile`
- `mean_centered_skill`
- `std_centered_skill`
- `median_centered_skill`
- `n_above_chance`
- `n_below_chance`
- `n_equal_chance`

## instance_level_details

Každý detailní záznam obsahuje:
- `judge_model_name`
- `locale`
- `criterion`
- `original_instance_id`
- `acc_eq`
- `acc_eq_index`
- `percentile`
- `percentile_percent`
- `centered_skill`
- `centered_skill_percent`

## Interpretace nových metrik

### percentile
Mid-percentil v nulovém rozdělení pro daný konkrétní human vektor:
`P(X < x) + 0.5 * P(X = x)`

### centered_skill
Přemapování percentilu na škálu s nulou pro náhodu:
`2 * percentile - 1`

- `0` = náhoda
- `+1` = maximálně vysoko nad náhodou
- `-1` = horší než náhoda
"""

Path(output_md).write_text(program_md, encoding="utf-8")
Path(output_json_schema_md).write_text(schema_md, encoding="utf-8")

log(f"Wrote documentation to {output_md} and {output_json_schema_md}")
log("Done.")
