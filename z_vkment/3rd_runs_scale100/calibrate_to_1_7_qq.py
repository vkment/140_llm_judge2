"""
calibrate_to_1_7_qq.py
───────────────────────
Kalibruje LLM skóre (škála 0–100, 5 průchodů) na škálu 1–7 (celá čísla)
pomocí Q-Q mapování (empirické zarovnání distribucí).

Pro každou skupinu (locale × criterion):
  - seřadí LLM skóre a přiřadí jim percentily
  - seřadí human skóre a přiřadí jim percentily
  - každé LLM skóre nahradí human hodnotou na stejném percentilu
  - výsledná distribuce má přesně stejný tvar jako human distribuce

Výstupy jsou identické se skriptyem calibrate_to_1_7.py (isotonická regrese).
"""

# ---------------------------------------------------------------------------
# CONFIG – měňte zde
# ---------------------------------------------------------------------------

LLM_CSV           = "z_vkment/oeg_judge_100s5p_56_1_submission_data.csv"
HUMAN_CSV         = "oeg_human_eval_data.csv"
OUTPUT_CSV        = "z_vkment/oeg_judge_outloc56_1_qq_submission_data.csv"
PARAMS_JSON       = "z_vkment/oeg_judge_outloc56_1_qq_params.json"

OUTPUT_JUDGE_NAME = "gemma-4-26B-A4B-it_s105_qq"

SCORE_MIN_OUT     = 1
SCORE_MAX_OUT     = 7

# ---------------------------------------------------------------------------
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Načtení dat
# ---------------------------------------------------------------------------

for p in [LLM_CSV, HUMAN_CSV]:
    if not Path(p).exists():
        sys.exit(f"ERROR: soubor nenalezen: {p}")

print(f"Načítám LLM skóre:    {LLM_CSV}")
llm_raw = pd.read_csv(LLM_CSV)
print(f"  řádků: {len(llm_raw):,}  | sloupce: {list(llm_raw.columns)}")

print(f"Načítám lidská skóre: {HUMAN_CSV}")
human = pd.read_csv(HUMAN_CSV)
print(f"  řádků: {len(human):,}  | sloupce: {list(human.columns)}")

# ---------------------------------------------------------------------------
# Průměr přes průchody → 22 080 řádků
# ---------------------------------------------------------------------------

JOIN_KEYS = ["criterion", "submission_system_name", "original_instance_id", "locale"]

has_pass = "pass_id" in llm_raw.columns
if has_pass:
    llm = (llm_raw
           .groupby(["judge_model_name"] + JOIN_KEYS, as_index=False)["score"]
           .mean())
    print(f"\nZprůměrováno přes průchody → {len(llm):,} řádků")
else:
    llm = llm_raw.copy()
    print(f"\nSingle-pass mód → {len(llm):,} řádků")

n_expected = len(llm)

# ---------------------------------------------------------------------------
# Q-Q mapování per (locale × criterion)
# ---------------------------------------------------------------------------

LOCALES  = sorted(llm["locale"].unique())
CRITERIA = sorted(llm["criterion"].unique())

params_all = {}
results    = []

print(f"\nQ-Q kalibrace pro {len(LOCALES)} lokálů × {len(CRITERIA)} kritérií "
      f"= {len(LOCALES)*len(CRITERIA)} skupin\n")

for locale in LOCALES:
    for criterion in CRITERIA:

        # --- LLM skóre pro tuto skupinu ---
        mask_llm = (llm["locale"] == locale) & (llm["criterion"] == criterion)
        grp_llm  = llm[mask_llm].copy()

        # --- human skóre pro tuto skupinu ---
        mask_h = (human["locale"] == locale) & (human["criterion"] == criterion)
        grp_h  = human[mask_h].copy()

        if grp_llm.empty or grp_h.empty:
            print(f"  VAROVÁNÍ: prázdná skupina {locale}/{criterion}, přeskakuji.")
            continue

        n_llm   = len(grp_llm)
        n_human = len(grp_h)

        # Seřazené human skóre = cílová distribuce
        human_sorted = np.sort(grp_h["score"].values.astype(float))

        # Percentily LLM položek (rank / n, midpoint convention)
        llm_scores = grp_llm["score"].values.astype(float)
        ranks = np.argsort(np.argsort(llm_scores, kind="stable"), kind="stable")
        # Percentil každé LLM položky v [0, 1)
        percentiles = ranks / n_llm

        # Mapování percentilu → human skóre interpolací přes human_sorted
        # np.interp: x v [0,1], xp = rovnoměrné body v [0,1] přes human_sorted
        xp = np.linspace(0, 1, n_human)
        mapped = np.interp(percentiles, xp, human_sorted)

        # Zaokrouhlení + ořez
        rounded = np.clip(np.round(mapped).astype(int), SCORE_MIN_OUT, SCORE_MAX_OUT)

        grp_llm["score_calibrated"] = rounded.astype(float)
        results.append(grp_llm[JOIN_KEYS + ["score_calibrated"]])

        # Parametry: přenosová funkce (unikátní LLM skóre → výsledná hodnota)
        unique_llm = np.sort(np.unique(llm_scores))
        unique_mapped = np.interp(
            np.searchsorted(np.sort(llm_scores), unique_llm) / n_llm,
            xp, human_sorted
        )
        params_all[f"{locale}|{criterion}"] = {
            "method": "quantile-quantile",
            "n_llm": int(n_llm),
            "n_human": int(n_human),
            "human_distribution": {
                str(int(v)): int(np.sum(human_sorted == v))
                for v in np.unique(human_sorted)
            },
            "llm_to_calibrated_examples": {
                str(round(float(x), 2)): int(np.clip(round(y), SCORE_MIN_OUT, SCORE_MAX_OUT))
                for x, y in zip(unique_llm[:10], unique_mapped[:10])
            },
        }

        print(f"  {locale:8s} / {criterion:25s} | "
              f"n_llm={n_llm:4d} n_human={n_human:4d} | "
              f"skóre po kalibraci: "
              f"min={rounded.min()} max={rounded.max()} "
              f"mean={rounded.mean():.2f}")

# ---------------------------------------------------------------------------
# Sestavení výstupního CSV
# ---------------------------------------------------------------------------

out_df = pd.concat(results, ignore_index=True)
out_df.rename(columns={"score_calibrated": "score"}, inplace=True)
out_df.insert(0, "judge_model_name", OUTPUT_JUDGE_NAME)

out_df = out_df.sort_values(
    ["locale", "criterion", "submission_system_name", "original_instance_id"]
).reset_index(drop=True)

OUTPUT_FIELDNAMES = [
    "judge_model_name", "criterion", "submission_system_name",
    "original_instance_id", "locale", "score",
]
out_df = out_df[OUTPUT_FIELDNAMES]

print(f"\nVýstupní CSV: {len(out_df):,} řádků")
assert len(out_df) == n_expected, \
    f"CHYBA: očekáváno {n_expected} řádků, získáno {len(out_df)}"

out_df.to_csv(OUTPUT_CSV, index=False)
print(f"Uloženo: {OUTPUT_CSV}")

# ---------------------------------------------------------------------------
# Uložení parametrů
# ---------------------------------------------------------------------------

with open(PARAMS_JSON, "w", encoding="utf-8") as fh:
    json.dump(params_all, fh, indent=2, ensure_ascii=False)
print(f"Parametry: {PARAMS_JSON}")

# ---------------------------------------------------------------------------
# Rychlý přehled výsledku
# ---------------------------------------------------------------------------

print("\n─── Distribuce výstupních skóre (přes všechny skupiny) ───")
print(out_df["score"].value_counts().sort_index().to_string())
print(f"\nPrůměr: {out_df['score'].mean():.3f}  |  Medián: {out_df['score'].median():.1f}")
print("\nHotovo.")
