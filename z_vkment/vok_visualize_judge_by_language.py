"""
visualize_judge_by_language.py
──────────────────────────────
Reads  oeg_judge_human_agreement_by_criterion.json  
made by vok_judge_human_agreement.py
and produces a three-panel figure that shows how well each LLM judge agrees
with human raters across different languages (locales).

Metrics used:  acc_eq  (pairwise accuracy with ties, Deutsch et al. EMNLP 2023).

Output:  judge_language_analysis.png  (saved next to this script).

Usage:
    python visualize_judge_by_language.py [path/to/json]
    # defaults to  oeg_judge_human_agreement_by_criterion.json  in the same dir.
"""

import json
import sys
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.gridspec import GridSpec
from matplotlib.patches import FancyBboxPatch
import matplotlib.patheffects as pe

# ── colour palette (colour-blind-friendly, Okabe–Ito–inspired) ───────────────
JUDGE_COLORS = [
    "#E69F00", "#56B4E9", "#009E73", "#F0E442",
    "#0072B2", "#D55E00", "#CC79A7", "#999999",
    "#44AA99", "#AA4499", "#117733", "#DDCC77", "#332288",
]

LOCALE_NICE = {
    "ar_EG": "Arabic\n(Egypt)",
    "bn_BD": "Bengali\n(Bangladesh)",
    "cs_CZ": "Czech",
    "de_DE": "German",
    "en_US": "English\n(US)",
    "hi_IN": "Hindi",
    "id_ID": "Indonesian",
    "ja_JP": "Japanese",
    "ru_RU": "Russian",
    "zh_CN": "Chinese\n(Mainland)",
}

CRITERION_NICE = {
    "instruction_following": "Instruction following",
    "coherence": "Coherence",
    "naturalness": "Naturalness",
}

CRITERION_STYLES = {
    "instruction_following": dict(color="#0072B2", marker="o", ls="-",  lw=2.2),
    "coherence":             dict(color="#D55E00", marker="s", ls="--", lw=2.2),
    "naturalness":           dict(color="#009E73", marker="^", ls="-.", lw=2.2),
}


# ─────────────────────────────────────────────────────────────────────────────
def load_data(json_path: str) -> dict:
    with open(json_path) as fh:
        return json.load(fh)


def build_matrices(data: dict):
    """
    Returns
    -------
    mat_avg  : ndarray (n_judges × n_locales), averaged over 3 criteria
    mat_crit : dict criterion → ndarray (n_judges × n_locales)
    judges   : list[str]   sorted by descending mean acc_eq (over locales & criteria)
    locales  : list[str]   sorted by descending mean acc_eq (over judges & criteria)
    criteria : list[str]
    """
    locale_scores = data["criterion_locale_grouped_scores"]["acc_eq"]
    criteria = list(locale_scores.keys())

    all_judges = sorted({j for c in criteria for l in locale_scores[c] for j in locale_scores[c][l]})
    all_locales = sorted(locale_scores[criteria[0]].keys())

    # per-criterion matrices
    mat_crit = {}
    for crit in criteria:
        m = np.zeros((len(all_judges), len(all_locales)))
        for li, loc in enumerate(all_locales):
            for ji, jdg in enumerate(all_judges):
                m[ji, li] = locale_scores[crit][loc][jdg]
        mat_crit[crit] = m

    mat_avg = np.mean([mat_crit[c] for c in criteria], axis=0)

    # sort judges by descending row mean
    judge_order = np.argsort(-mat_avg.mean(axis=1))
    judges_sorted = [all_judges[i] for i in judge_order]
    mat_avg = mat_avg[judge_order, :]
    mat_crit = {c: mat_crit[c][judge_order, :] for c in criteria}

    # sort locales by descending column mean
    locale_order = np.argsort(-mat_avg.mean(axis=0))
    locales_sorted = [all_locales[i] for i in locale_order]
    mat_avg = mat_avg[:, locale_order]
    mat_crit = {c: mat_crit[c][:, locale_order] for c in criteria}

    return mat_avg, mat_crit, judges_sorted, locales_sorted, criteria


# ─────────────────────────────────────────────────────────────────────────────
def plot(json_path: str, out_path: str) -> None:
    data = load_data(json_path)
    mat_avg, mat_crit, judges, locales, criteria = build_matrices(data)

    n_judges  = len(judges)
    n_locales = len(locales)

    # ── figure layout ─────────────────────────────────────────────────────────
    fig = plt.figure(figsize=(22, 17), facecolor="#F7F6F2")
    gs = GridSpec(
        2, 2,
        figure=fig,
        left=0.07, right=0.97,
        top=0.91, bottom=0.08,
        wspace=0.35, hspace=0.48,
    )

    ax_heat  = fig.add_subplot(gs[0, :])   # top row: full-width heatmap
    ax_strip = fig.add_subplot(gs[1, 0])   # bottom-left: strip / dot plot
    ax_line  = fig.add_subplot(gs[1, 1])   # bottom-right: per-criterion lines

    # ── global title ──────────────────────────────────────────────────────────
    fig.text(
        0.5, 0.96,
        "LLM-as-a-Judge  ×  Human Agreement  by  Language",
        ha="center", va="top", fontsize=18, fontweight="bold",
        color="#1A1A2E",
    )
    fig.text(
        0.5, 0.93,
        "Metric: acc_eq (pairwise accuracy with ties, Deutsch et al. EMNLP 2023) · "
        "averaged over instruction_following, coherence, naturalness",
        ha="center", va="top", fontsize=10, color="#555577",
    )

    locale_labels = [LOCALE_NICE.get(l, l) for l in locales]

    # ══════════════════════════════════════════════════════════════════════════
    # PANEL 1 · Heatmap   (judges × locales)
    # ══════════════════════════════════════════════════════════════════════════
    vmin, vmax = 0.32, 0.70
    cmap = matplotlib.colormaps["YlOrRd"]

    im = ax_heat.imshow(
        mat_avg, aspect="auto", cmap=cmap,
        vmin=vmin, vmax=vmax, interpolation="nearest",
    )

    # cell text
    for ji in range(n_judges):
        for li in range(n_locales):
            v = mat_avg[ji, li]
            brightness = (v - vmin) / (vmax - vmin)
            txt_color = "#1A1A1A" if brightness < 0.6 else "#F5F5F5"
            ax_heat.text(
                li, ji, f"{v:.2f}",
                ha="center", va="center",
                fontsize=8.5, color=txt_color, fontweight="semibold",
            )

    ax_heat.set_xticks(range(n_locales))
    ax_heat.set_xticklabels(locale_labels, fontsize=10, ha="center")
    ax_heat.set_yticks(range(n_judges))
    ax_heat.set_yticklabels(judges, fontsize=10)
    ax_heat.set_title(
        "Panel 1 · acc_eq per judge × language  (avg over 3 criteria)",
        fontsize=12, fontweight="bold", color="#2C2C54", pad=8,
    )

    # row marginal — mean per judge (right side)
    ax_heat_r = ax_heat.twinx()
    ax_heat_r.set_ylim(ax_heat.get_ylim())
    row_means = mat_avg.mean(axis=1)
    ax_heat_r.set_yticks(range(n_judges))
    ax_heat_r.set_yticklabels(
        [f"  {v:.3f}" for v in row_means],
        fontsize=9, color="#666",
    )
    ax_heat_r.tick_params(right=False)
    ax_heat_r.set_ylabel("← mean over all languages", fontsize=9, color="#666", labelpad=4)

    # column marginal — mean per locale (below)
    col_means = mat_avg.mean(axis=0)
    for li, cm in enumerate(col_means):
        ax_heat.text(
            li, n_judges - 0.05,
            f"μ={cm:.2f}",
            ha="center", va="bottom",
            fontsize=8.5, color="#333",
            transform=ax_heat.get_xaxis_transform(),
        )

    cb = fig.colorbar(im, ax=ax_heat, fraction=0.012, pad=0.13, aspect=25)
    cb.set_label("acc_eq", fontsize=9)
    cb.ax.tick_params(labelsize=8)

    ax_heat.set_facecolor("#F7F6F2")

    # ══════════════════════════════════════════════════════════════════════════
    # PANEL 2 · Strip plot — locale difficulty
    # ══════════════════════════════════════════════════════════════════════════
    judge_color_map = {j: JUDGE_COLORS[i % len(JUDGE_COLORS)] for i, j in enumerate(judges)}

    # locales already sorted by descending mean (left = easiest, right = hardest)
    # we want hardest on left for a "league table" feel → reverse
    loc_rev = list(reversed(locales))
    mat_rev = mat_avg[:, ::-1]   # match column order

    col_mean_rev = mat_rev.mean(axis=0)
    col_std_rev  = mat_rev.std(axis=0)

    jitter_rng = np.random.default_rng(42)

    for li, loc in enumerate(loc_rev):
        col_idx = locales.index(loc)      # column in mat_avg
        vals = mat_avg[:, col_idx]         # all judges for this locale

        jitter = jitter_rng.uniform(-0.22, 0.22, size=len(judges))
        for ji, (jdg, v) in enumerate(zip(judges, vals)):
            ax_strip.scatter(
                li + jitter[ji], v,
                color=judge_color_map[jdg],
                s=52, zorder=4, alpha=0.88,
                linewidths=0.5, edgecolors="white",
            )

    # mean bars
    ax_strip.bar(
        range(n_locales), col_mean_rev,
        width=0.6, alpha=0.18, color="#2C2C54", zorder=1,
    )
    ax_strip.errorbar(
        range(n_locales), col_mean_rev, yerr=col_std_rev,
        fmt="none", color="#2C2C54", capsize=4, lw=1.8, zorder=5,
    )

    ax_strip.axhline(0.5, color="#999", lw=1, ls="--", label="acc_eq = 0.50 (chance)")
    ax_strip.set_xticks(range(n_locales))
    ax_strip.set_xticklabels(
        [LOCALE_NICE.get(l, l) for l in loc_rev],
        fontsize=9.5, ha="center",
    )
    ax_strip.set_ylabel("acc_eq", fontsize=10)
    ax_strip.set_ylim(0.28, 0.72)
    ax_strip.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.2f"))
    ax_strip.set_title(
        "Panel 2 · Language difficulty\n(dots = individual judges, bar = mean ± std)",
        fontsize=11, fontweight="bold", color="#2C2C54",
    )
    ax_strip.set_facecolor("#FAFAF8")
    ax_strip.spines[["top", "right"]].set_visible(False)

    # legend for judges (2 columns, small font)
    from matplotlib.lines import Line2D
    legend_handles = [
        Line2D([0], [0], marker="o", color="w",
               markerfacecolor=judge_color_map[j], markersize=8, label=j)
        for j in judges
    ]
    ax_strip.legend(
        handles=legend_handles,
        title="Judge model", title_fontsize=8,
        fontsize=7.5, ncols=2,
        loc="upper left", framealpha=0.85,
        borderpad=0.6, labelspacing=0.35,
    )

    # ══════════════════════════════════════════════════════════════════════════
    # PANEL 3 · Per-criterion lines  (avg over judges)
    # ══════════════════════════════════════════════════════════════════════════
    # locales sorted by overall mean (same as heatmap, best→worst)
    for crit in criteria:
        m = mat_crit[crit]          # judges × locales (sorted)
        crit_means = m.mean(axis=0)
        crit_stds  = m.std(axis=0)
        style = CRITERION_STYLES[crit]

        ax_line.plot(
            range(n_locales), crit_means,
            color=style["color"], marker=style["marker"],
            ls=style["ls"], lw=style["lw"],
            markersize=7, zorder=4,
            label=CRITERION_NICE[crit],
        )
        ax_line.fill_between(
            range(n_locales),
            crit_means - crit_stds,
            crit_means + crit_stds,
            color=style["color"], alpha=0.10, zorder=2,
        )

    ax_line.axhline(0.5, color="#999", lw=1, ls="--")
    ax_line.set_xticks(range(n_locales))
    ax_line.set_xticklabels(
        [LOCALE_NICE.get(l, l) for l in locales],
        fontsize=9.5, ha="center",
    )
    ax_line.set_ylabel("acc_eq (mean over judges ± 1 std)", fontsize=10)
    ax_line.set_ylim(0.28, 0.72)
    ax_line.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.2f"))
    ax_line.set_title(
        "Panel 3 · Per-criterion breakdown by language\n(shaded = ±1 std across judges)",
        fontsize=11, fontweight="bold", color="#2C2C54",
    )
    ax_line.legend(fontsize=9, loc="upper right", framealpha=0.85)
    ax_line.set_facecolor("#FAFAF8")
    ax_line.spines[["top", "right"]].set_visible(False)

    # x-axis label: indicate sort order
    ax_line.set_xlabel("← harder languages          easier languages →", fontsize=9, color="#555")
    ax_strip.set_xlabel("← harder languages          easier languages →", fontsize=9, color="#555")

    # ── save ──────────────────────────────────────────────────────────────────
    fig.savefig(out_path, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    print(f"Saved: {out_path}")


# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    json_path = sys.argv[1] if len(sys.argv) > 1 else "oeg_judge_human_agreement_by_criterion.json"
    # output always goes next to this script (or cwd if no arg given)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    out_path   = os.path.join(script_dir, "judge_language_analysis.png")
    plot(json_path, out_path)
