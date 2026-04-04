"""
calibrate_to_1_7.py
───────────────────
Kalibruje LLM skóre (škála 0–100, 5 průchodů) na škálu 1–7 (celá čísla)
pomocí isotonické regrese trénované na párových datech LLM vs. lidský hodnotitel.

Kalibrace probíhá *zvlášť* pro každou kombinaci (locale × criterion).

Výstupy:
  OUTPUT_CSV   – výsledné skóre na škále 1–7, 22 080 řádků
  PARAMS_JSON  – parametry isotonické regrese (breakpointy X→Y) pro každou skupinu
"""

# ---------------------------------------------------------------------------
# CONFIG – měňte zde
# ---------------------------------------------------------------------------

LLM_CSV          = "z_vkment/oeg_judge_100s5p_56_1_submission_data.csv"
HUMAN_CSV        = "oeg_human_eval_data.csv"
OUTPUT_CSV       = "z_vkment/oeg_judge_outloc56_1_submission_data.csv"
PARAMS_JSON      = "z_vkment/oeg_judge_outloc56_1_params.json"

# Název judge modelu ve výstupním CSV
OUTPUT_JUDGE_NAME = "gemma-4-26B-A4B-it_s105_loc"

SCORE_MIN_OUT    = 1      # dolní hranice výstupní škály
SCORE_MAX_OUT    = 7      # horní hranice výstupní škály

# ---------------------------------------------------------------------------
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.isotonic import IsotonicRegression

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

# ---------------------------------------------------------------------------
# Párování LLM ↔ lidská hodnocení
# ---------------------------------------------------------------------------

merged = llm.merge(
    human[JOIN_KEYS + ["score"]],
    on=JOIN_KEYS,
    suffixes=("_llm", "_human"),
    how="inner",
)

n_expected = len(llm)
n_merged   = len(merged)
print(f"Párování: {n_merged:,} / {n_expected:,} řádků spojeno")
if n_merged < n_expected * 0.95:
    print("  VAROVÁNÍ: více než 5 % řádků se nepodařilo spárovat – zkontrolujte klíče.")

# ---------------------------------------------------------------------------
# Isotonická regrese per (locale × criterion)
# ---------------------------------------------------------------------------

LOCALES   = sorted(merged["locale"].unique())
CRITERIA  = sorted(merged["criterion"].unique())

params_all = {}   # slovník pro uložení breakpointů
results    = []   # seznam výsledných řádků

print(f"\nKalibrace pro {len(LOCALES)} lokálů × {len(CRITERIA)} kritérií "
      f"= {len(LOCALES)*len(CRITERIA)} skupin\n")

for locale in LOCALES:
    for criterion in CRITERIA:

        # --- trénovací data pro tuto skupinu ---
        mask_train = (merged["locale"] == locale) & (merged["criterion"] == criterion)
        grp = merged[mask_train]

        if grp.empty:
            print(f"  VAROVÁNÍ: prázdná skupina {locale}/{criterion}, přeskakuji.")
            continue

        X_train = grp["score_llm"].values.astype(float)
        y_train = grp["score_human"].values.astype(float)

        # --- fit isotonické regrese ---
        ir = IsotonicRegression(y_min=SCORE_MIN_OUT, y_max=SCORE_MAX_OUT,
                                out_of_bounds="clip")
        ir.fit(X_train, y_train)

        # Uložení breakpointů (X_thresholds_, y_thresholds_ jsou interní;
        # použijeme X_train seřazené + predikce jako aproximaci)
        x_sorted = np.sort(np.unique(X_train))
        y_pred_sorted = ir.predict(x_sorted)
        params_all[f"{locale}|{criterion}"] = {
            "x_breakpoints": x_sorted.tolist(),
            "y_breakpoints": y_pred_sorted.tolist(),
            "n_train": int(len(grp)),
            "rmse_train": float(np.sqrt(np.mean((ir.predict(X_train) - y_train) ** 2))),
        }

        # --- aplikace na všechny LLM skóre v této skupině ---
        mask_apply = (llm["locale"] == locale) & (llm["criterion"] == criterion)
        grp_apply  = llm[mask_apply].copy()

        raw_pred   = ir.predict(grp_apply["score"].values.astype(float))
        # Zaokrouhlení na celé číslo, ořez na [1, 7]
        rounded    = np.clip(np.round(raw_pred).astype(int), SCORE_MIN_OUT, SCORE_MAX_OUT)

        grp_apply["score_calibrated"] = rounded.astype(float)
        results.append(grp_apply[JOIN_KEYS + ["score_calibrated"]])

        # results.append(grp_apply[JOIN_KEYS + ["submission_system_name",
        #                                        "original_instance_id",
        #                                        "score_calibrated"]])

        print(f"  {locale:8s} / {criterion:25s} | "
              f"n={len(grp):4d} | "
              f"RMSE={params_all[f'{locale}|{criterion}']['rmse_train']:.3f} | "
              f"skóre po kalibraci: "
              f"min={rounded.min()} max={rounded.max()} "
              f"mean={rounded.mean():.2f}")

# ---------------------------------------------------------------------------
# Sestavení výstupního CSV
# ---------------------------------------------------------------------------

out_df = pd.concat(results, ignore_index=True)
out_df.rename(columns={"score_calibrated": "score"}, inplace=True)
out_df.insert(0, "judge_model_name", OUTPUT_JUDGE_NAME)

# Řazení stejné jako vstupní soubory
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


# Nejdřív k metodologii, pak program.

# **Isotonická regrese je správná volba**, ale stojí za to zmínit alternativu: **quantile-quantile mapping** (empirické mapování kvantilů). Rozdíl:

# - **Isotonická regrese** pracuje s *párovými daty* (stejné položky hodnocené oběma) a učí se monotónní funkci LLM→human. Vhodné právě zde, protože máme páry.
# - **Q-Q mapping** mapuje distribuci na distribuci bez ohledu na párování — vhodné pokud páry nemáme nebo jim nevěříme.

# Protože páry *máš* (stejné system+doc_id+locale+criterion v obou souborech), isotonická regrese je vhodná. Implementuji ji.Co program dělá krok po kroku:

# 1. **Průměr přes 5 průchodů** → 22 080 řádků LLM skóre
# 2. **Párování** LLM ↔ human na (criterion, system, doc_id, locale) — 30 skupin (10 lokálů × 3 kritéria)
# 3. **Fit isotonické regrese** per skupina: `IsotonicRegression(y_min=1, y_max=7)` trénovaná na párech (llm_score, human_score)
# 4. **Aplikace** na všechna LLM skóre v dané skupině, zaokrouhlení na celé číslo, ořez na [1,7]
# 5. **Výstup**: CSV ve stejném formátu jako starší soubory + JSON s breakpointy

# V JSON parametrech je pro každou skupinu uloženo: seznam X/Y breakpointů (krok funkce), počet trénovacích příkladů a RMSE na trénovacích datech — z toho uvidíš, jak dobře se regrese přizpůsobila každé skupině.

# Závislost `sklearn` — pokud není nainstalována: `pip install scikit-learn`.