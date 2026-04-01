"""
compare_runs.py  –  Compare  aya-expanse-8bjudge results across two evaluation runs.

Usage:
    python compare_runs.py \
        --results_old  2nd_oeg_judge_human_agreement_results_all2024.json \
        --by_crit_old  2nd_oeg_judge_human_agreement_by_criterion_all2024.json \
        --by_crit_new  5th_oeg_judge_human_agreement_by_criterion_ayaexpanse8b.json \
        --results_new  5th_oeg_judge_human_agreement_results_ayaexpanse8b.json \
        --judge        aya-expanse-8b \
        --label_old    "Run 2 (2025)" \
        --label_new    "Run 5 (2026)" \
        --output_dir   ./compare_out_ayaexpanse8b
"""

import argparse
import json
import os
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np

# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

parser = argparse.ArgumentParser(description="Compare LLM judge runs for one model.")
parser.add_argument("--results_old",  default="2nd_oeg_judge_human_agreement_results_all2024.json")
parser.add_argument("--by_crit_old",  default="2nd_oeg_judge_human_agreement_by_criterion_all2024.json")
parser.add_argument("--results_new",  default="5th_oeg_judge_human_agreement_results_ayaexpanse8b.json")
parser.add_argument("--by_crit_new",  default="5th_oeg_judge_human_agreement_by_criterion_ayaexpanse8b.json")
parser.add_argument("--judge",        default="aya-expanse-8b",
                    help="Judge model name to compare (case-insensitive key lookup).")
parser.add_argument("--label_old",    default="Run 2 (2025)")
parser.add_argument("--label_new",    default="Run 5 (2026)")
parser.add_argument("--output_dir",   default="./compare_out_ayaexpanse8b")

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

MODEL_PRINT = "Aya Expanse 8B"

CRITERIA = ["coherence", "naturalness", "instruction_following"]
CRIT_LABELS = {"coherence": "Coherence", "naturalness": "Naturalness",
               "instruction_following": "Instr. Following"}

LOCALE_ORDER = ["ar_EG", "bn_BD", "cs_CZ", "de_DE", "en_US",
                "hi_IN", "id_ID", "ja_JP", "ru_RU", "zh_CN"]

# Mapping from canonical judge name (lowercase) → key used in *old* result files.
# Add entries here whenever the old and new files use different strings for the same model.
JUDGE_OLD_KEY_MAP: dict[str, str] = {
    "aya-expanse-8b": "AyaExpanse-8B",
}

# Slightly academic palette: muted slate-blue for old, warm amber for new
COLOR_OLD = "#4C72B0"
COLOR_NEW = "#DD8452"
ALPHA_FILL = 0.12


def find_judge_key(d: dict, judge: str) -> str | None:
    """Case-insensitive key lookup."""
    for k in d:
        if k.lower() == judge.lower():
            return k
    return None


def load_json(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def extract_overall(results: dict, judge: str, judge_old: str | None = None) -> dict:
    """Return {metric: value} for the given judge from a *_results.json.

    judge_old – alternative key to try first (for old files that used a different
                string for the same model, e.g. 'AyaExpanse-8B' vs 'aya-expanse-8b').
    """
    lookup = judge_old if judge_old is not None else judge
    key = find_judge_key(results.get("ranking_accuracy", {}), lookup)
    if key is None and judge_old is not None:
        # Fall back to the canonical name in case the old file was already updated.
        key = find_judge_key(results.get("ranking_accuracy", {}), judge)
    if key is None:
        tried = f"'{lookup}'" + (f" / '{judge}'" if judge_old else "")
        raise KeyError(f"Judge {tried} not found in results file.")
    return {
        "ranking_accuracy":      results["ranking_accuracy"][key],
        "acc_eq_by_coherence":   results["acc_eq_by_coherence"][key],
        "acc_eq_by_naturalness": results["acc_eq_by_naturalness"][key],
        "acc_eq_by_instruction_following": results["acc_eq_by_instruction_following"][key],
        "acc_eq_average":        results["acc_eq_average"][key],
    }


def extract_per_locale(by_crit: dict, judge: str,
                       judge_old: str | None = None) -> dict[str, dict[str, float]]:
    """Return {criterion: {locale: score}} from a *_by_criterion.json.

    judge_old – alternative key to try first (same semantics as in extract_overall).
    """
    locale_scores = by_crit["criterion_locale_grouped_scores"]["acc_eq"]
    out = {}
    for crit in CRITERIA:
        out[crit] = {}
        for locale, judge_dict in locale_scores.get(crit, {}).items():
            key = None
            if judge_old is not None:
                key = find_judge_key(judge_dict, judge_old)
            if key is None:
                key = find_judge_key(judge_dict, judge)
            if key is not None:
                out[crit][locale] = judge_dict[key]
    return out


# ---------------------------------------------------------------------------
# Plot helpers
# ---------------------------------------------------------------------------

def set_spine_style(ax, light=True):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    if light:
        ax.spines["left"].set_color("#cccccc")
        ax.spines["bottom"].set_color("#cccccc")
        ax.tick_params(colors="#555555")
        ax.yaxis.label.set_color("#444444")
        ax.xaxis.label.set_color("#444444")
        ax.title.set_color("#222222")


def save(fig, path):
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    print(f"  → saved: {path}")
    plt.close(fig)


# ---------------------------------------------------------------------------
# Figure 1: Overall summary bar chart
# ---------------------------------------------------------------------------

def plot_overall_summary(old: dict, new: dict, label_old: str, label_new: str, outdir: Path):
    metrics = [
        ("ranking_accuracy",              "Ranking\nAccuracy"),
        ("acc_eq_by_coherence",           "acc_eq\nCoherence"),
        ("acc_eq_by_naturalness",         "acc_eq\nNaturalness"),
        ("acc_eq_by_instruction_following","acc_eq\nInstr.Follow."),
        ("acc_eq_average",                "acc_eq\nAverage"),
    ]
    labels   = [m[1] for m in metrics]
    vals_old = [old[m[0]] for m in metrics]
    vals_new = [new[m[0]] for m in metrics]

    x = np.arange(len(metrics))
    w = 0.35

    fig, ax = plt.subplots(figsize=(9, 4.5), facecolor="#fafafa")
    ax.set_facecolor("#fafafa")

    bars_old = ax.bar(x - w/2, vals_old, w, color=COLOR_OLD, alpha=0.85, label=label_old, zorder=3)
    bars_new = ax.bar(x + w/2, vals_new, w, color=COLOR_NEW, alpha=0.85, label=label_new, zorder=3)

    # value labels
    for bar in list(bars_old) + list(bars_new):
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, h + 0.008, f"{h:.3f}",
                ha="center", va="bottom", fontsize=7.5, color="#333333")

    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=9)
    ax.set_ylim(0, 1.05)
    ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.2f"))
    ax.set_ylabel("Score", fontsize=10)
    ax.set_title(f"Overall metrics – {MODEL_PRINT}\n{label_old}  vs  {label_new}", fontsize=11, pad=10)
    ax.legend(fontsize=9, framealpha=0.5)
    ax.grid(axis="y", color="#dddddd", zorder=0)
    set_spine_style(ax)

    save(fig, outdir / "fig1_overall_summary.png")


# ---------------------------------------------------------------------------
# Figure 2: Per-criterion, per-locale comparison (sorted by new-run score)
# ---------------------------------------------------------------------------

def plot_per_locale(old_locale: dict, new_locale: dict,
                    label_old: str, label_new: str, outdir: Path):
    fig, axes = plt.subplots(1, 3, figsize=(15, 5), facecolor="#fafafa")
    fig.suptitle(f"acc_eq per locale – {MODEL_PRINT}\n{label_old}  vs  {label_new}",
                 fontsize=12, y=1.01)

    for ax, crit in zip(axes, CRITERIA):
        new_scores = new_locale.get(crit, {})
        old_scores = old_locale.get(crit, {})

        # sort locales by new-run score descending
        locales_sorted = sorted(new_scores.keys(), key=lambda l: new_scores[l], reverse=True)
        n = len(locales_sorted)
        x = np.arange(n)
        w = 0.35

        v_old = [old_scores.get(l, float("nan")) for l in locales_sorted]
        v_new = [new_scores[l] for l in locales_sorted]

        ax.set_facecolor("#fafafa")
        bars_old = ax.bar(x - w/2, v_old, w, color=COLOR_OLD, alpha=0.85, label=label_old, zorder=3)
        bars_new = ax.bar(x + w/2, v_new, w, color=COLOR_NEW, alpha=0.85, label=label_new, zorder=3)

        # difference annotation (new − old) above each locale pair
        for i, (vo, vn) in enumerate(zip(v_old, v_new)):
            if not np.isnan(vo):
                diff = vn - vo
                sign = "+" if diff >= 0 else "−"
                color = "#2a7a2a" if diff >= 0 else "#c0392b"
                ax.text(i, max(vo, vn) + 0.025, f"{sign}{abs(diff):.3f}",
                        ha="center", va="bottom", fontsize=7, color=color, fontweight="bold")

        ax.set_xticks(x)
        ax.set_xticklabels(locales_sorted, rotation=35, ha="right", fontsize=8)
        ax.set_ylim(0, 1.05)
        ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.2f"))
        ax.set_title(CRIT_LABELS[crit], fontsize=10, pad=6)
        ax.set_ylabel("acc_eq" if crit == CRITERIA[0] else "", fontsize=9)
        ax.grid(axis="y", color="#dddddd", zorder=0)
        ax.legend(fontsize=8, framealpha=0.5)
        set_spine_style(ax)

    fig.tight_layout()
    save(fig, outdir / "fig2_per_locale_by_criterion.png")


# ---------------------------------------------------------------------------
# Figure 3: Line chart – profile across locales for each criterion
# ---------------------------------------------------------------------------

def plot_locale_profiles(old_locale: dict, new_locale: dict,
                         label_old: str, label_new: str, outdir: Path):
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.5), facecolor="#fafafa")
    fig.suptitle(f"acc_eq locale profile – {MODEL_PRINT}\n{label_old}  vs  {label_new}",
                 fontsize=12, y=1.01)

    for ax, crit in zip(axes, CRITERIA):
        new_scores = new_locale.get(crit, {})
        old_scores = old_locale.get(crit, {})

        # sort locales by new score
        locales_sorted = sorted(new_scores.keys(), key=lambda l: new_scores[l], reverse=True)

        v_old = [old_scores.get(l, float("nan")) for l in locales_sorted]
        v_new = [new_scores[l] for l in locales_sorted]
        x = np.arange(len(locales_sorted))

        ax.set_facecolor("#fafafa")
        ax.plot(x, v_old, "o-", color=COLOR_OLD, linewidth=1.8, markersize=6,
                label=label_old, zorder=3)
        ax.fill_between(x, v_old, alpha=ALPHA_FILL, color=COLOR_OLD)
        ax.plot(x, v_new, "s-", color=COLOR_NEW, linewidth=1.8, markersize=6,
                label=label_new, zorder=3)
        ax.fill_between(x, v_new, alpha=ALPHA_FILL, color=COLOR_NEW)

        # overall mean lines
        mean_old = np.nanmean(v_old)
        mean_new = np.nanmean(v_new)
        ax.axhline(mean_old, color=COLOR_OLD, linewidth=0.9, linestyle="--", alpha=0.6)
        ax.axhline(mean_new, color=COLOR_NEW, linewidth=0.9, linestyle="--", alpha=0.6)
        ax.text(len(x) - 0.05, mean_old + 0.012, f"μ={mean_old:.3f}",
                ha="right", fontsize=7.5, color=COLOR_OLD)
        ax.text(len(x) - 0.05, mean_new - 0.022, f"μ={mean_new:.3f}",
                ha="right", fontsize=7.5, color=COLOR_NEW)

        ax.set_xticks(x)
        ax.set_xticklabels(locales_sorted, rotation=35, ha="right", fontsize=8)
        ax.set_ylim(0.3, 0.85)
        ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.2f"))
        ax.set_title(CRIT_LABELS[crit], fontsize=10, pad=6)
        ax.set_ylabel("acc_eq" if crit == CRITERIA[0] else "", fontsize=9)
        ax.grid(axis="y", color="#dddddd", zorder=0)
        ax.legend(fontsize=8, framealpha=0.5)
        set_spine_style(ax)

    fig.tight_layout()
    save(fig, outdir / "fig3_locale_profiles.png")


# ---------------------------------------------------------------------------
# Figure 4: Delta heatmap  (new − old)  locales × criteria
# ---------------------------------------------------------------------------

def plot_delta_heatmap(old_locale: dict, new_locale: dict,
                       label_old: str, label_new: str, outdir: Path):
    # collect all locales present in new data
    all_locales = sorted(
        set(l for crit in CRITERIA for l in new_locale.get(crit, {})),
        key=lambda l: LOCALE_ORDER.index(l) if l in LOCALE_ORDER else 99,
    )

    matrix = np.full((len(CRITERIA), len(all_locales)), np.nan)
    for ci, crit in enumerate(CRITERIA):
        for li, loc in enumerate(all_locales):
            v_new = new_locale.get(crit, {}).get(loc, float("nan"))
            v_old = old_locale.get(crit, {}).get(loc, float("nan"))
            if not (np.isnan(v_new) or np.isnan(v_old)):
                matrix[ci, li] = v_new - v_old

    fig, ax = plt.subplots(figsize=(11, 3.2), facecolor="#fafafa")
    ax.set_facecolor("#fafafa")

    vmax = np.nanmax(np.abs(matrix))
    im = ax.imshow(matrix, cmap="RdYlGn", vmin=-vmax, vmax=vmax, aspect="auto")

    ax.set_xticks(range(len(all_locales)))
    ax.set_xticklabels(all_locales, fontsize=9)
    ax.set_yticks(range(len(CRITERIA)))
    ax.set_yticklabels([CRIT_LABELS[c] for c in CRITERIA], fontsize=9)

    # cell annotations
    for ci in range(len(CRITERIA)):
        for li in range(len(all_locales)):
            v = matrix[ci, li]
            if not np.isnan(v):
                sign = "+" if v >= 0 else ""
                ax.text(li, ci, f"{sign}{v:.3f}",
                        ha="center", va="center", fontsize=8,
                        color="black" if abs(v) < 0.04 else "white", fontweight="bold")

    cbar = fig.colorbar(im, ax=ax, fraction=0.03, pad=0.02)
    cbar.set_label("Δ acc_eq  (new − old)", fontsize=9)
    ax.set_title(f"Delta heatmap – {MODEL_PRINT}  ({label_new} − {label_old})",
                 fontsize=11, pad=8)
    fig.tight_layout()
    save(fig, outdir / "fig4_delta_heatmap.png")


# ---------------------------------------------------------------------------
# Text summary
# ---------------------------------------------------------------------------

def print_summary(old: dict, new: dict, old_loc: dict, new_loc: dict,
                  label_old: str, label_new: str):
    print("\n" + "="*64)
    print(f"  {MODEL_PRINT}  |  {label_old}  vs  {label_new}")
    print("="*64)
    metrics = [
        ("ranking_accuracy",              "Ranking accuracy    "),
        ("acc_eq_by_coherence",           "acc_eq coherence    "),
        ("acc_eq_by_naturalness",         "acc_eq naturalness  "),
        ("acc_eq_by_instruction_following","acc_eq instr.follow."),
        ("acc_eq_average",                "acc_eq average      "),
    ]
    for key, label in metrics:
        vo, vn = old[key], new[key]
        diff = vn - vo
        sign = "▲" if diff > 0.0005 else ("▼" if diff < -0.0005 else "≈")
        print(f"  {label}  {vo:.4f}  →  {vn:.4f}   {sign} {diff:+.4f}")
    print()
    for crit in CRITERIA:
        print(f"  {CRIT_LABELS[crit]} per locale (new − old):")
        ns = new_loc.get(crit, {})
        os_ = old_loc.get(crit, {})
        for loc in sorted(ns, key=lambda l: ns[l] - os_.get(l, ns[l]), reverse=True):
            vo = os_.get(loc, float("nan"))
            vn = ns[loc]
            diff = vn - vo if not np.isnan(vo) else float("nan")
            diff_str = f"{diff:+.4f}" if not np.isnan(diff) else "   n/a"
            print(f"    {loc:8s}  {vn:.4f}  {diff_str}")
        print()
    print("="*64)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main(args):
    outdir = Path(args.output_dir)
    outdir.mkdir(parents=True, exist_ok=True)

    print(f"Loading: {args.results_old}")
    results_old = load_json(args.results_old)
    print(f"Loading: {args.results_new}")
    results_new = load_json(args.results_new)
    print(f"Loading: {args.by_crit_new}")
    by_crit_new = load_json(args.by_crit_new)

    judge = args.judge
    # Key used in *old* result files (may differ from the canonical judge name).
    judge_old = JUDGE_OLD_KEY_MAP.get(judge.lower())

    overall_old = extract_overall(results_old, judge, judge_old=judge_old)
    overall_new = extract_overall(results_new, judge)

    # Load per-locale old scores from --by_crit_old if the file exists, with graceful fallback.
    if args.by_crit_old and os.path.exists(args.by_crit_old):
        print(f"Loading: {args.by_crit_old}")
        by_crit_old = load_json(args.by_crit_old)
        locale_old = extract_per_locale(by_crit_old, judge, judge_old=judge_old)
    elif "criterion_locale_grouped_scores" in results_old:
        locale_old = extract_per_locale(results_old, judge, judge_old=judge_old)
    else:
        print("  ⚠  No per-locale breakdown for old run (--by_crit_old not found). Delta charts will show n/a.")
        locale_old = {crit: {} for crit in CRITERIA}

    locale_new = extract_per_locale(by_crit_new, judge)

    print_summary(overall_old, overall_new, locale_old, locale_new,
                  args.label_old, args.label_new)

    print("\nGenerating figures...")
    plot_overall_summary(overall_old, overall_new, args.label_old, args.label_new, outdir)
    plot_per_locale(locale_old, locale_new, args.label_old, args.label_new, outdir)
    plot_locale_profiles(locale_old, locale_new, args.label_old, args.label_new, outdir)
    plot_delta_heatmap(locale_old, locale_new, args.label_old, args.label_new, outdir)
    print("\nDone. All figures saved to:", outdir.resolve())


if __name__ == "__main__":
    main_args = parser.parse_args([] if "__file__" not in globals() else None)
    main(main_args)
