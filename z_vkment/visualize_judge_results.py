#!/usr/bin/env python3
"""
Vizualizace acc_eq_mean LLM-as-a-judge běhů po locale.

Loňské výsledky (studie Kocmi) + aktuální nové běhy se načtou z JSON souborů,
pro každý (model, locale) se spočítá průměr přes tři kritéria
(instruction_following, coherence, naturalness) a výsledek se vykreslí do .jpg.
"""

from __future__ import annotations

import json
import os
import re
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt

# ---------------------------------------------------------------------------
# Konfigurace
# ---------------------------------------------------------------------------

KOCMI_BY_CRITERION_FILE = Path("kocmi_oeg_judge_human_agreement_by_criterion.json")
KOCMI_RESULTS_FILE = Path("kocmi_oeg_judge_human_agreement_results.json")  # není pro graf nutný
NEW_RUNS_DIR = Path("z_vkment/llm_eval_copies/JSON_files")

OUTPUT_IMAGE = Path("judge_results_by_locale.jpg")

CRITERIA = ("instruction_following", "coherence", "naturalness")

# Modely z Kocmi studie, které chceme zobrazit
KOCMI_MODELS_TO_SHOW = [
    "Claude-4",
    "GPT-4.1",
    "Qwen3-235B",
    "Llama-4-Maverick",
    "AyaExpanse-8B",
    "Llama-3.1-8B",
]

# Locale řazené od "nejhoršího" po "nejlepší" (dle zadání)
LOCALE_ORDER = [
    ("cs_CZ", "Czech"),
    ("bn_BD", "Bengali"),
    ("id_ID", "Indonesian"),
    ("ja_JP", "Japanese"),
    ("de_DE", "German"),
    ("ru_RU", "Russian"),
    ("ar_EG", "Arabic (Egypt)"),
    ("hi_IN", "Hindi"),
    ("zh_CN", "China (Mainland)"),
    ("en_US", "English (US)"),
]


# ---------------------------------------------------------------------------
# Načítání
# ---------------------------------------------------------------------------

def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def extract_locale_scores(by_criterion_data: dict) -> dict[str, dict[str, dict[str, float]]]:
    """
    Z `criterion_locale_grouped_scores` získá strukturu:
        { model: { locale: { criterion: value } } }
    """
    out: dict[str, dict[str, dict[str, float]]] = defaultdict(lambda: defaultdict(dict))
    root = by_criterion_data.get("criterion_locale_grouped_scores", {}).get("acc_eq", {})
    for criterion, locales in root.items():
        if criterion not in CRITERIA:
            continue
        for locale, models in locales.items():
            for model, value in models.items():
                out[model][locale][criterion] = value
    return out


def compute_acc_eq_mean(
    per_model: dict[str, dict[str, dict[str, float]]]
) -> dict[str, dict[str, float]]:
    """
    Z { model: { locale: { criterion: value } } } vyrobí { model: { locale: mean } }
    (pouze pokud jsou přítomna všechna tři kritéria).
    """
    result: dict[str, dict[str, float]] = {}
    for model, locales in per_model.items():
        result[model] = {}
        for locale, crits in locales.items():
            if all(c in crits for c in CRITERIA):
                result[model][locale] = sum(crits[c] for c in CRITERIA) / len(CRITERIA)
    return result


def find_new_run_pairs(directory: Path) -> list[Path]:
    """
    V adresáři najde `*_by_criterion_*.json` soubory (obsahují per-locale data).
    Párový `_results_` soubor pro graf nepotřebujeme.
    """
    if not directory.is_dir():
        print(f"[warn] Adresář {directory} neexistuje, nové běhy nebudou načteny.")
        return []
    return sorted(directory.glob("*_by_criterion_*.json"))


def model_name_from_by_criterion(data: dict) -> str | None:
    """Vytáhne jméno modelu (předpokládáme vždy jen jeden) z nového běhu."""
    root = data.get("criterion_locale_grouped_scores", {}).get("acc_eq", {})
    for _criterion, locales in root.items():
        for _locale, models in locales.items():
            if models:
                return next(iter(models.keys()))
    return None


# ---------------------------------------------------------------------------
# Hlavní logika
# ---------------------------------------------------------------------------

def main() -> None:
    # --- Kocmi (loňské) výsledky ---
    if not KOCMI_BY_CRITERION_FILE.exists():
        raise SystemExit(f"Chybí soubor: {KOCMI_BY_CRITERION_FILE}")

    kocmi_raw = extract_locale_scores(load_json(KOCMI_BY_CRITERION_FILE))
    kocmi_mean = compute_acc_eq_mean(kocmi_raw)

    missing = [m for m in KOCMI_MODELS_TO_SHOW if m not in kocmi_mean]
    if missing:
        print(f"[warn] V Kocmi datech chybí modely: {missing}")

    kocmi_selected = {m: kocmi_mean[m] for m in KOCMI_MODELS_TO_SHOW if m in kocmi_mean}

    # --- Nové běhy ---
    new_mean: dict[str, dict[str, float]] = {}
    for path in find_new_run_pairs(NEW_RUNS_DIR):
        data = load_json(path)
        model = model_name_from_by_criterion(data)
        if model is None:
            print(f"[warn] {path.name}: nepodařilo se zjistit jméno modelu, přeskakuji.")
            continue
        per_model = extract_locale_scores(data)
        mean = compute_acc_eq_mean(per_model)
        if model in mean:
            # Pokud by stejný model byl ve více souborech, rozliš podle souboru
            key = model
            if key in new_mean:
                key = f"{model} ({path.stem})"
            new_mean[key] = mean[model]

    print(f"Načteno Kocmi modelů (vybráno k zobrazení): {len(kocmi_selected)}")
    print(f"Načteno nových modelů: {len(new_mean)}")

    # --- Vykreslení ---
    plot(kocmi_selected, new_mean)


def plot(
    kocmi_selected: dict[str, dict[str, float]],
    new_models: dict[str, dict[str, float]],
) -> None:
    locale_codes = [code for code, _ in LOCALE_ORDER]
    locale_labels = [label for _, label in LOCALE_ORDER]
    x_positions = list(range(len(locale_codes)))

    # Průměr přes všechny zobrazené modely (Kocmi vybraní + noví) pro každou locale
    all_shown = {**kocmi_selected, **new_models}
    bar_heights: list[float] = []
    for loc in locale_codes:
        vals = [m[loc] for m in all_shown.values() if loc in m]
        bar_heights.append(sum(vals) / len(vals) if vals else 0.0)

    fig, ax = plt.subplots(figsize=(14, 8))

    # Světle šedé sloupce = průměr přes zobrazené modely
    ax.bar(
        x_positions,
        bar_heights,
        width=0.8,
        color="#e8e8e8",
        edgecolor="#bfbfbf",
        linewidth=0.7,
        zorder=1,
        label="Mean of shown models",
    )

    # Barvy pro modely — unikátní
    all_model_names = list(kocmi_selected.keys()) + list(new_models.keys())
    cmap = plt.get_cmap("tab20")
    colors = {name: cmap(i % 20) for i, name in enumerate(all_model_names)}

    # Malý horizontální jitter, aby se značky nepřekrývaly
    def jittered(i: int, total: int, spread: float = 0.55) -> float:
        if total <= 1:
            return 0.0
        return (i / (total - 1) - 0.5) * spread

    # Kocmi modely — křížky
    total_k = len(kocmi_selected)
    for i, (model, scores) in enumerate(kocmi_selected.items()):
        xs, ys = [], []
        for xi, loc in enumerate(locale_codes):
            if loc in scores:
                xs.append(xi + jittered(i, total_k))
                ys.append(scores[loc])
        ax.scatter(
            xs, ys,
            marker="x", s=70, linewidths=2.0,
            color=colors[model], label=f"[Kocmi] {model}",
            zorder=3,
        )

    # Nové modely — kolečka
    total_n = len(new_models)
    for i, (model, scores) in enumerate(new_models.items()):
        xs, ys = [], []
        for xi, loc in enumerate(locale_codes):
            if loc in scores:
                xs.append(xi + jittered(i, total_n))
                ys.append(scores[loc])
        ax.scatter(
            xs, ys,
            marker="o", s=55, linewidths=0.8,
            facecolor=colors[model], edgecolor="black",
            label=f"[new] {model}",
            zorder=3,
        )

    ax.set_xticks(x_positions)
    ax.set_xticklabels(locale_labels, rotation=25, ha="right")
    ax.set_ylabel("acc_eq (mean of 3 criteria)")
    ax.set_title("LLM-as-a-judge — acc_eq_mean per locale")
    ax.set_axisbelow(True)
    ax.grid(axis="y", linestyle="--", alpha=0.4, zorder=0)

    # Rozumný rozsah y — kolem dat
    all_vals = bar_heights + [
        v
        for m in all_shown.values()
        for v in m.values()
    ]
    if all_vals:
        lo = max(0.0, min(all_vals) - 0.05)
        hi = min(1.0, max(all_vals) + 0.05)
        ax.set_ylim(lo, hi)

    ax.legend(
        loc="center left",
        bbox_to_anchor=(1.01, 0.5),
        fontsize=8,
        frameon=False,
    )

    fig.tight_layout()
    fig.savefig(OUTPUT_IMAGE, dpi=150, bbox_inches="tight")
    print(f"Hotovo -> {OUTPUT_IMAGE.resolve()}")


if __name__ == "__main__":
    main()
