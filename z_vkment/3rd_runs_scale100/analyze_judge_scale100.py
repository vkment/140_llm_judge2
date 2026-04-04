"""
analyze_judge.py  –  Analysis & plots for LLM-as-a-Judge output CSV.

Supports both formats:
  - without pass_id  (single-pass runs)
  - with    pass_id  (multi-pass runs; scores are averaged per item before analysis)

Usage:
    python analyze_judge.py
    python analyze_judge.py --csv my_other_file.csv
    python analyze_judge.py --csv run56.csv --no-plots
"""

# ---------------------------------------------------------------------------
# CONFIG – change here, not deep in the code
# ---------------------------------------------------------------------------

INPUT_CSV  = "z_vkment/oeg_judge_100s_55_2_submission_data.csv"   # ← default input file
SCORE_MIN  = 0
SCORE_MAX  = 100
BINS       = 20          # histogram bins
FIGSIZE_H  = (14, 4)     # per-row figure width × height
FIGSIZE_V  = (5, 4)      # single-panel figure

# ---------------------------------------------------------------------------
import argparse
import sys
from pathlib import Path

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

parser = argparse.ArgumentParser()
parser.add_argument("--csv",      default=INPUT_CSV,  help="Path to judge output CSV.")
parser.add_argument("--no-plots", action="store_true", help="Skip plot generation.")
args = parser.parse_args([] if "__file__" not in globals() else None)

csv_path = Path(args.csv)
if not csv_path.exists():
    sys.exit(f"ERROR: File not found: {csv_path}")

# ---------------------------------------------------------------------------
# Load
# ---------------------------------------------------------------------------

df = pd.read_csv(csv_path)
print(f"\n{'='*70}")
print(f"  File : {csv_path}")
print(f"  Rows : {len(df):,}")
print(f"  Cols : {list(df.columns)}")
print(f"{'='*70}\n")

HAS_PASS_ID = "pass_id" in df.columns

# ---------------------------------------------------------------------------
# If multi-pass: collapse to per-item mean, keep std as separate column
# ---------------------------------------------------------------------------

GROUP_KEYS = ["judge_model_name", "criterion", "submission_system_name",
              "original_instance_id", "locale"]

if HAS_PASS_ID:
    n_passes = df["pass_id"].nunique()
    print(f"Multi-pass mode detected  ({n_passes} passes per item)\n")
    agg = df.groupby(GROUP_KEYS)["score"].agg(["mean", "std", "count"]).reset_index()
    agg.columns = GROUP_KEYS + ["score", "score_std", "n_passes"]
    df_analysis = agg
    print(f"Pass-level variance summary (score_std across passes):")
    print(df_analysis["score_std"].describe().round(2).to_string(), "\n")
else:
    print("Single-pass mode.\n")
    df_analysis = df.copy()
    df_analysis["score_std"] = np.nan

CRITERIA  = sorted(df_analysis["criterion"].unique())
LOCALES   = sorted(df_analysis["locale"].unique())
SYSTEMS   = sorted(df_analysis["submission_system_name"].unique())
JUDGES    = sorted(df_analysis["judge_model_name"].unique())

# ---------------------------------------------------------------------------
# 1. Overall summary
# ---------------------------------------------------------------------------

print("─" * 70)
print("1. OVERALL SCORE SUMMARY  (all criteria, all locales)")
print("─" * 70)
print(df_analysis["score"].describe().round(2).to_string())
print()

# Value-frequency table – shows rounding bias (multiples of 5/10)
freq = df_analysis["score"].value_counts().sort_index()
top_vals = freq.nlargest(15).sort_index()
print("Top-15 most frequent score values:")
print(top_vals.to_string())
print()

# ---------------------------------------------------------------------------
# 2. Per-criterion summary
# ---------------------------------------------------------------------------

print("─" * 70)
print("2. PER-CRITERION SUMMARY")
print("─" * 70)
crit_stats = (df_analysis.groupby("criterion")["score"]
              .agg(["count", "mean", "std", "median"])
              .round(2))
print(crit_stats.to_string(), "\n")

# ---------------------------------------------------------------------------
# 3. Per-locale summary  (mean ± std for each criterion)
# ---------------------------------------------------------------------------

print("─" * 70)
print("3. PER-LOCALE × CRITERION  (mean score)")
print("─" * 70)
locale_crit = (df_analysis.groupby(["locale", "criterion"])["score"]
               .mean().round(2).unstack("criterion"))
print(locale_crit.to_string(), "\n")

# ---------------------------------------------------------------------------
# 4. Per-system summary
# ---------------------------------------------------------------------------

print("─" * 70)
print("4. PER-SYSTEM  (mean score across all criteria & locales)")
print("─" * 70)
sys_stats = (df_analysis.groupby("submission_system_name")["score"]
             .agg(["count", "mean", "std", "median"])
             .sort_values("mean", ascending=False)
             .round(2))
print(sys_stats.to_string(), "\n")

# Per-system × criterion
print("Per-system × criterion:")
sys_crit = (df_analysis.groupby(["submission_system_name", "criterion"])["score"]
            .mean().round(2).unstack("criterion"))
print(sys_crit.to_string(), "\n")

# ---------------------------------------------------------------------------
# 5. Missing / unexpected scores
# ---------------------------------------------------------------------------

out_of_range = df_analysis[(df_analysis["score"] < SCORE_MIN) |
                            (df_analysis["score"] > SCORE_MAX)]
print(f"Out-of-range scores [{SCORE_MIN}–{SCORE_MAX}]: {len(out_of_range)}")
if not out_of_range.empty:
    print(out_of_range[["locale", "criterion", "submission_system_name",
                         "original_instance_id", "score"]].to_string())
print()

# ---------------------------------------------------------------------------
# PLOTS
# ---------------------------------------------------------------------------

if args.no_plots:
    print("Plots skipped (--no-plots).")
    sys.exit(0)

out_dir = Path("judge_analysis_plots")
out_dir.mkdir(exist_ok=True)


def save(fig, name):
    p = out_dir / name
    fig.savefig(p, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {p}")


print("─" * 70)
print("GENERATING PLOTS …")
print("─" * 70)

# ── A. Score distribution per criterion (one panel each) ──────────────────
fig, axes = plt.subplots(1, len(CRITERIA), figsize=FIGSIZE_H, sharey=False)
if len(CRITERIA) == 1:
    axes = [axes]
for ax, crit in zip(axes, CRITERIA):
    data = df_analysis.loc[df_analysis["criterion"] == crit, "score"].dropna()
    ax.hist(data, bins=BINS, range=(SCORE_MIN, SCORE_MAX),
            color="#4C72B0", edgecolor="white", linewidth=0.5)
    ax.set_title(crit, fontsize=11)
    ax.set_xlabel("Score")
    ax.set_ylabel("Count" if ax == axes[0] else "")
    ax.xaxis.set_major_locator(mticker.MultipleLocator(10))
    mu = data.mean(); med = data.median()
    ax.axvline(mu,  color="red",    linestyle="--", linewidth=1.2, label=f"mean {mu:.1f}")
    ax.axvline(med, color="orange", linestyle=":",  linewidth=1.2, label=f"median {med:.1f}")
    ax.legend(fontsize=8)
fig.suptitle("Score distributions per criterion", fontsize=13, y=1.02)
fig.tight_layout()
save(fig, "A_hist_by_criterion.png")

# ── B. Score distribution per locale (rows) × criterion (cols) ────────────
fig, axes = plt.subplots(len(LOCALES), len(CRITERIA),
                          figsize=(len(CRITERIA)*4, len(LOCALES)*2.5),
                          sharex=True, sharey=False)
for r, locale in enumerate(LOCALES):
    for c, crit in enumerate(CRITERIA):
        ax = axes[r][c] if len(LOCALES) > 1 else axes[c]
        data = df_analysis.loc[
            (df_analysis["locale"] == locale) &
            (df_analysis["criterion"] == crit), "score"].dropna()
        ax.hist(data, bins=BINS, range=(SCORE_MIN, SCORE_MAX),
                color="#55A868", edgecolor="white", linewidth=0.4)
        if r == 0:
            ax.set_title(crit, fontsize=9)
        if c == 0:
            ax.set_ylabel(locale, fontsize=8)
        ax.xaxis.set_major_locator(mticker.MultipleLocator(20))
        ax.tick_params(labelsize=7)
fig.suptitle("Score distributions: locale × criterion", fontsize=13, y=1.01)
fig.tight_layout()
save(fig, "B_hist_locale_x_criterion.png")

# ── C. Boxplot: systems × criterion ───────────────────────────────────────
fig, axes = plt.subplots(1, len(CRITERIA), figsize=FIGSIZE_H, sharey=True)
if len(CRITERIA) == 1:
    axes = [axes]
for ax, crit in zip(axes, CRITERIA):
    groups = [df_analysis.loc[
                  (df_analysis["criterion"] == crit) &
                  (df_analysis["submission_system_name"] == s), "score"].dropna()
              for s in SYSTEMS]
    ax.boxplot(groups, labels=SYSTEMS, vert=True)
    ax.set_title(crit, fontsize=11)
    ax.set_xlabel("")
    ax.tick_params(axis="x", labelsize=7, rotation=30)
    ax.set_ylim(SCORE_MIN - 2, SCORE_MAX + 2)
axes[0].set_ylabel("Score")
fig.suptitle("Score distributions per system × criterion", fontsize=13, y=1.02)
fig.tight_layout()
save(fig, "C_boxplot_systems.png")

# ── D. Heatmap: locale × system (mean score, averaged over criteria) ───────
pivot = (df_analysis.groupby(["locale", "submission_system_name"])["score"]
         .mean().unstack("submission_system_name"))
fig, ax = plt.subplots(figsize=(max(6, len(SYSTEMS)*1.4), max(4, len(LOCALES)*0.7)))
im = ax.imshow(pivot.values, aspect="auto", cmap="RdYlGn",
               vmin=SCORE_MIN, vmax=SCORE_MAX)
ax.set_xticks(range(len(pivot.columns))); ax.set_xticklabels(pivot.columns, rotation=35, ha="right", fontsize=8)
ax.set_yticks(range(len(pivot.index)));   ax.set_yticklabels(pivot.index, fontsize=8)
for i in range(len(pivot.index)):
    for j in range(len(pivot.columns)):
        v = pivot.values[i, j]
        if not np.isnan(v):
            ax.text(j, i, f"{v:.0f}", ha="center", va="center", fontsize=7,
                    color="black" if 30 < v < 75 else "white")
plt.colorbar(im, ax=ax, label="Mean score")
ax.set_title("Mean score: locale × system  (all criteria)", fontsize=12)
fig.tight_layout()
save(fig, "D_heatmap_locale_system.png")

# ── E. Multi-pass variance (only if HAS_PASS_ID) ──────────────────────────
if HAS_PASS_ID:
    fig, axes = plt.subplots(1, len(CRITERIA), figsize=FIGSIZE_H, sharey=False)
    if len(CRITERIA) == 1:
        axes = [axes]
    for ax, crit in zip(axes, CRITERIA):
        data = df_analysis.loc[df_analysis["criterion"] == crit, "score_std"].dropna()
        ax.hist(data, bins=BINS, color="#C44E52", edgecolor="white", linewidth=0.5)
        ax.set_title(crit, fontsize=11)
        ax.set_xlabel("Std across passes")
        ax.set_ylabel("Count" if ax == axes[0] else "")
        ax.axvline(data.mean(), color="black", linestyle="--", linewidth=1.2,
                   label=f"mean {data.mean():.2f}")
        ax.legend(fontsize=8)
    fig.suptitle("Pass-level score variance (std) per criterion", fontsize=13, y=1.02)
    fig.tight_layout()
    save(fig, "E_pass_variance.png")

# ── F. Score rounding bias – spike chart ──────────────────────────────────
fig, ax = plt.subplots(figsize=FIGSIZE_V)
all_scores = df_analysis["score"].dropna()
counts = all_scores.value_counts().sort_index()
colors = ["#C44E52" if (v % 10 == 0) else
          "#DD8452" if (v % 5  == 0) else "#4C72B0"
          for v in counts.index]
ax.bar(counts.index, counts.values, width=0.8, color=colors)
ax.set_xlabel("Score value")
ax.set_ylabel("Count")
ax.set_title("Score value frequency\n(red = mult of 10, orange = mult of 5)")
ax.xaxis.set_major_locator(mticker.MultipleLocator(10))
fig.tight_layout()
save(fig, "F_rounding_bias.png")

print(f"\nAll plots saved to: {out_dir.resolve()}\n")
