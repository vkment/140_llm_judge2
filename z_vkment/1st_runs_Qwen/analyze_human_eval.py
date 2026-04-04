# =============================================================================
#  KONFIGURACE  –  upravuj pouze tuto sekci
# =============================================================================

import os

# Skript leží v:  <root>/z_vkment/analyze_human_eval.py
# _ROOT je adresář o úroveň výš (tam leží CSV)
_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)

# Vstupní soubor  (relativně k rootu projektu)
INPUT_CSV = os.path.join(_ROOT, "oeg_human_eval_data.csv")

# Výstupní adresář  (relativně ke skriptu, tj. v z_vkment)
OUTPUT_DIR = os.path.join(_HERE, "analysis_output")

# =============================================================================
#  KONEC KONFIGURACE
# =============================================================================

"""
Human Evaluation Results Analysis
==================================
Analyzuje rozložení skóre (škála 1–7) per kritérium a per jazyk.
Cílem je zjistit, zda jsou vstupní data rovnoměrně rozložena napříč lokály,
nebo zda různé jazyky koncentrují odpovědi v různých pásmech škály –
což je klíčové pro správnou kalibraci LLM-judge promptu.

Spuštění (ze složky z_vkment, nebo odkudkoli):
    python z_vkment/analyze_human_eval.py
"""
import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.gridspec as gridspec
from matplotlib.colors import LinearSegmentedColormap
import seaborn as sns
from scipy import stats

# ── Locale → readable language name ──────────────────────────────────────────
LOCALE_TO_LANGUAGE = {
    "ar_EG": "Arabic",
    "bn_BD": "Bengali",
    "cs_CZ": "Czech",
    "de_DE": "German",
    "en_US": "English",
    "hi_IN": "Hindi",
    "id_ID": "Indonesian",
    "ja_JP": "Japanese",
    "ru_RU": "Russian",
    "zh_CN": "Chinese",
}

CRITERIA = ["coherence", "naturalness", "instruction_following"]
SCORES   = [1, 2, 3, 4, 5, 6, 7]

# ── Visual style ──────────────────────────────────────────────────────────────
PALETTE_LANG    = sns.color_palette("tab10", 10)
PALETTE_CRIT    = {"coherence": "#4C72B0", "naturalness": "#DD8452",
                   "instruction_following": "#55A868"}
SCORE_CMAP      = LinearSegmentedColormap.from_list(
    "score_cmap", ["#d73027", "#fee08b", "#1a9850"], N=7)

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.titlesize": 13,
    "axes.labelsize": 11,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
})


# ═══════════════════════════════════════════════════════════════════════════════
# 1.  DATA LOADING & PREPROCESSING
# ═══════════════════════════════════════════════════════════════════════════════

def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    df.columns = df.columns.str.strip()

    # Keep only human judges
    if "judge_model_name" in df.columns:
        df = df[df["judge_model_name"] == "human"].copy()

    df["score"] = pd.to_numeric(df["score"], errors="coerce")
    df = df.dropna(subset=["score", "criterion", "locale"])
    df["score"] = df["score"].astype(int)

    # Map locale → language
    df["language"] = df["locale"].map(LOCALE_TO_LANGUAGE).fillna(df["locale"])

    # Normalise criterion names (strip whitespace, lowercase)
    df["criterion"] = df["criterion"].str.strip().str.lower()

    print(f"  Loaded {len(df):,} rows | "
          f"criteria: {sorted(df['criterion'].unique())} | "
          f"locales: {sorted(df['locale'].unique())}")
    return df


# ═══════════════════════════════════════════════════════════════════════════════
# 2.  SUMMARY STATISTICS TABLE
# ═══════════════════════════════════════════════════════════════════════════════

def compute_summary_tables(df: pd.DataFrame, out_dir: str):
    rows = []
    for lang in sorted(df["language"].unique()):
        for crit in CRITERIA:
            sub = df[(df["language"] == lang) & (df["criterion"] == crit)]["score"]
            if sub.empty:
                continue
            row = {
                "Language": lang,
                "Criterion": crit,
                "N": len(sub),
                "Mean": round(sub.mean(), 3),
                "Median": sub.median(),
                "Std": round(sub.std(), 3),
                "Q1": sub.quantile(0.25),
                "Q3": sub.quantile(0.75),
                "% score≤3": round(100 * (sub <= 3).mean(), 1),
                "% score≥5": round(100 * (sub >= 5).mean(), 1),
                "Mode": int(sub.mode().iloc[0]),
            }
            rows.append(row)

    summary = pd.DataFrame(rows)
    summary.to_csv(os.path.join(out_dir, "table_summary_stats.csv"), index=False)
    print("  ✓ table_summary_stats.csv")

    # Pivot: mean score per language × criterion
    pivot_mean = summary.pivot(index="Language", columns="Criterion", values="Mean")
    pivot_mean.to_csv(os.path.join(out_dir, "table_mean_score_pivot.csv"))
    print("  ✓ table_mean_score_pivot.csv")

    # Distribution frequencies
    freq_rows = []
    for lang in sorted(df["language"].unique()):
        for crit in CRITERIA:
            sub = df[(df["language"] == lang) & (df["criterion"] == crit)]["score"]
            if sub.empty:
                continue
            total = len(sub)
            freq = {s: round(100 * (sub == s).sum() / total, 2) for s in SCORES}
            freq_rows.append({"Language": lang, "Criterion": crit, **freq})

    freq_df = pd.DataFrame(freq_rows)
    freq_df.to_csv(os.path.join(out_dir, "table_score_freq_pct.csv"), index=False)
    print("  ✓ table_score_freq_pct.csv")

    return summary, freq_df


# ═══════════════════════════════════════════════════════════════════════════════
# 3.  FIGURE 1  –  Overall score distributions per criterion
# ═══════════════════════════════════════════════════════════════════════════════

def fig_overall_distributions(df: pd.DataFrame, out_dir: str):
    fig, axes = plt.subplots(1, 3, figsize=(16, 5), sharey=False)
    fig.suptitle("Overall Score Distributions per Criterion (all languages combined)",
                 fontsize=14, fontweight="bold", y=1.01)

    for ax, crit in zip(axes, CRITERIA):
        sub = df[df["criterion"] == crit]["score"]
        counts = sub.value_counts().reindex(SCORES, fill_value=0)
        pct    = counts / counts.sum() * 100

        bars = ax.bar(SCORES, pct, color=[SCORE_CMAP(s / 7) for s in SCORES],
                      edgecolor="white", linewidth=0.8)
        for bar, p in zip(bars, pct):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.4,
                    f"{p:.1f}%", ha="center", va="bottom", fontsize=8)

        ax.set_title(crit.replace("_", " ").title())
        ax.set_xlabel("Score")
        ax.set_ylabel("% of responses")
        ax.set_xticks(SCORES)
        ax.axvline(sub.mean(), color="navy", linestyle="--", linewidth=1.2,
                   label=f"Mean={sub.mean():.2f}")
        ax.axvline(sub.median(), color="crimson", linestyle=":", linewidth=1.2,
                   label=f"Median={sub.median():.1f}")
        ax.legend(fontsize=8)

    plt.tight_layout()
    path = os.path.join(out_dir, "fig1_overall_distributions.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print("  ✓ fig1_overall_distributions.png")


# ═══════════════════════════════════════════════════════════════════════════════
# 4.  FIGURE 2  –  Score distribution per language × criterion (small multiples)
# ═══════════════════════════════════════════════════════════════════════════════

def fig_per_language_per_criterion(df: pd.DataFrame, out_dir: str):
    languages = sorted(df["language"].unique())
    n_lang = len(languages)
    n_crit = len(CRITERIA)

    fig, axes = plt.subplots(n_lang, n_crit,
                             figsize=(5 * n_crit, 3.2 * n_lang),
                             sharex=True)
    fig.suptitle("Score Distributions: Language × Criterion",
                 fontsize=15, fontweight="bold", y=1.005)

    for i, lang in enumerate(languages):
        for j, crit in enumerate(CRITERIA):
            ax = axes[i][j]
            sub = df[(df["language"] == lang) & (df["criterion"] == crit)]["score"]

            if sub.empty:
                ax.text(0.5, 0.5, "no data", ha="center", va="center",
                        transform=ax.transAxes, color="gray")
                continue

            pct = sub.value_counts().reindex(SCORES, fill_value=0) / len(sub) * 100
            ax.bar(SCORES, pct, color=[SCORE_CMAP(s / 7) for s in SCORES],
                   edgecolor="white", linewidth=0.6)

            ax.axvline(sub.mean(), color="navy",   linestyle="--", linewidth=1.1)
            ax.axvline(sub.median(), color="crimson", linestyle=":", linewidth=1.1)
            ax.set_ylim(0, max(pct.max() * 1.25, 10))
            ax.set_xticks(SCORES)

            # Labels on edges only
            if i == 0:
                ax.set_title(crit.replace("_", " ").title(), fontsize=11,
                             fontweight="bold", pad=6)
            if j == 0:
                ax.set_ylabel(f"{lang}\n% responses", fontsize=9)
            else:
                ax.set_ylabel("")

            # Annotate mean inside bar
            ax.text(0.97, 0.92, f"μ={sub.mean():.2f}\nmd={sub.median():.1f}",
                    transform=ax.transAxes, ha="right", va="top",
                    fontsize=7.5, color="navy",
                    bbox=dict(boxstyle="round,pad=0.2", fc="white", alpha=0.7))

    plt.tight_layout()
    path = os.path.join(out_dir, "fig2_per_language_per_criterion.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print("  ✓ fig2_per_language_per_criterion.png")


# ═══════════════════════════════════════════════════════════════════════════════
# 5.  FIGURE 3  –  Mean score heatmap (language × criterion)
# ═══════════════════════════════════════════════════════════════════════════════

def fig_mean_heatmap(df: pd.DataFrame, out_dir: str):
    languages = sorted(df["language"].unique())
    matrix = pd.DataFrame(index=languages, columns=CRITERIA, dtype=float)
    for lang in languages:
        for crit in CRITERIA:
            sub = df[(df["language"] == lang) & (df["criterion"] == crit)]["score"]
            matrix.loc[lang, crit] = sub.mean() if not sub.empty else np.nan

    matrix.columns = [c.replace("_", "\n").title() for c in CRITERIA]

    fig, ax = plt.subplots(figsize=(8, 6))
    sns.heatmap(matrix.astype(float), annot=True, fmt=".2f", cmap="RdYlGn",
                vmin=1, vmax=7, linewidths=0.5, ax=ax, cbar_kws={"label": "Mean score"})
    ax.set_title("Mean Human Score: Language × Criterion", fontsize=13,
                 fontweight="bold", pad=12)
    ax.set_xlabel("")
    ax.set_ylabel("")
    plt.tight_layout()
    path = os.path.join(out_dir, "fig3_mean_heatmap.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print("  ✓ fig3_mean_heatmap.png")


# ═══════════════════════════════════════════════════════════════════════════════
# 6.  FIGURE 4  –  Stacked % bar chart (score buckets per language)
# ═══════════════════════════════════════════════════════════════════════════════

def fig_stacked_buckets(df: pd.DataFrame, out_dir: str):
    """
    Bucket scores into Low (1–3), Mid (4), High (5–7) per language & criterion.
    Useful to immediately see where each language's responses concentrate.
    """
    buckets = {
        "Low (1–3)": lambda s: s <= 3,
        "Mid (4)":   lambda s: s == 4,
        "High (5–7)": lambda s: s >= 5,
    }
    bucket_colors = ["#d73027", "#fee08b", "#1a9850"]

    languages = sorted(df["language"].unique())
    fig, axes = plt.subplots(1, 3, figsize=(17, 6), sharey=True)
    fig.suptitle("Score Bucket Distribution per Language & Criterion\n"
                 "(Low 1–3 | Mid 4 | High 5–7)",
                 fontsize=13, fontweight="bold")

    for ax, crit in zip(axes, CRITERIA):
        data = {b: [] for b in buckets}
        for lang in languages:
            sub = df[(df["language"] == lang) & (df["criterion"] == crit)]["score"]
            total = len(sub) if len(sub) > 0 else 1
            for b, fn in buckets.items():
                data[b].append(100 * fn(sub).sum() / total)

        bottom = np.zeros(len(languages))
        for (b, vals), color in zip(data.items(), bucket_colors):
            bars = ax.barh(languages, vals, left=bottom, color=color,
                           label=b, edgecolor="white", linewidth=0.5)
            # label segments > 8 %
            for bar, v, bot in zip(bars, vals, bottom):
                if v > 8:
                    ax.text(bot + v / 2, bar.get_y() + bar.get_height() / 2,
                            f"{v:.0f}%", ha="center", va="center",
                            fontsize=8, color="black")
            bottom += np.array(vals)

        ax.set_title(crit.replace("_", " ").title(), fontweight="bold")
        ax.set_xlabel("% of responses")
        ax.set_xlim(0, 100)
        if ax == axes[0]:
            ax.legend(loc="lower right", fontsize=8)

    plt.tight_layout()
    path = os.path.join(out_dir, "fig4_stacked_buckets.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print("  ✓ fig4_stacked_buckets.png")


# ═══════════════════════════════════════════════════════════════════════════════
# 7.  FIGURE 5  –  Boxplots: score spread per language, faceted by criterion
# ═══════════════════════════════════════════════════════════════════════════════

def fig_boxplots(df: pd.DataFrame, out_dir: str):
    languages = sorted(df["language"].unique())
    lang_colors = {l: c for l, c in zip(languages, PALETTE_LANG)}

    fig, axes = plt.subplots(1, 3, figsize=(17, 6), sharey=True)
    fig.suptitle("Score Spread per Language (Boxplots)", fontsize=13,
                 fontweight="bold")

    for ax, crit in zip(axes, CRITERIA):
        data   = [df[(df["language"] == l) & (df["criterion"] == crit)]["score"].values
                  for l in languages]
        colors = [lang_colors[l] for l in languages]

        bp = ax.boxplot(data, patch_artist=True, vert=True,
                        medianprops=dict(color="black", linewidth=2),
                        whiskerprops=dict(linewidth=1.2),
                        capprops=dict(linewidth=1.2),
                        flierprops=dict(marker=".", markersize=3, alpha=0.4))
        for patch, color in zip(bp["boxes"], colors):
            patch.set_facecolor(color)
            patch.set_alpha(0.75)

        ax.set_title(crit.replace("_", " ").title(), fontweight="bold")
        ax.set_xticks(range(1, len(languages) + 1))
        ax.set_xticklabels(languages, rotation=35, ha="right", fontsize=9)
        ax.set_ylabel("Score" if ax == axes[0] else "")
        ax.set_yticks(SCORES)
        ax.yaxis.grid(True, linestyle="--", alpha=0.5)

    plt.tight_layout()
    path = os.path.join(out_dir, "fig5_boxplots.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print("  ✓ fig5_boxplots.png")


# ═══════════════════════════════════════════════════════════════════════════════
# 8.  FIGURE 6  –  KDE curves (density) per language, one plot per criterion
# ═══════════════════════════════════════════════════════════════════════════════

def fig_kde(df: pd.DataFrame, out_dir: str):
    languages = sorted(df["language"].unique())
    lang_colors = {l: c for l, c in zip(languages, PALETTE_LANG)}

    fig, axes = plt.subplots(1, 3, figsize=(17, 5), sharey=False)
    fig.suptitle("Score Density (KDE) per Language & Criterion",
                 fontsize=13, fontweight="bold")

    for ax, crit in zip(axes, CRITERIA):
        for lang in languages:
            sub = df[(df["language"] == lang) & (df["criterion"] == crit)]["score"]
            if len(sub) < 5:
                continue
            # KDE on jittered data so integer scores get proper bandwidth
            jitter = sub + np.random.uniform(-0.3, 0.3, size=len(sub))
            kde = stats.gaussian_kde(jitter, bw_method=0.4)
            xs  = np.linspace(0.5, 7.5, 300)
            ax.plot(xs, kde(xs), label=lang, color=lang_colors[lang], linewidth=1.8)

        ax.set_title(crit.replace("_", " ").title(), fontweight="bold")
        ax.set_xlabel("Score")
        ax.set_ylabel("Density" if ax == axes[0] else "")
        ax.set_xticks(SCORES)
        ax.set_xlim(0.5, 7.5)
        ax.yaxis.grid(True, linestyle="--", alpha=0.4)
        if ax == axes[2]:
            ax.legend(fontsize=8, bbox_to_anchor=(1.01, 1), loc="upper left")

    plt.tight_layout()
    path = os.path.join(out_dir, "fig6_kde_per_language.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print("  ✓ fig6_kde_per_language.png")


# ═══════════════════════════════════════════════════════════════════════════════
# 9.  FIGURE 7  –  % High scores (≥5) heatmap  — the "LLM judge sensitivity" map
# ═══════════════════════════════════════════════════════════════════════════════

def fig_high_score_heatmap(df: pd.DataFrame, out_dir: str):
    """
    Shows what fraction of responses score ≥5 per language × criterion.
    This is arguably the most actionable chart for prompt calibration:
    languages with high % of ≥5 scores need good discrimination in the
    upper range; languages with low % need it in the lower range.
    """
    languages = sorted(df["language"].unique())
    pct_high  = pd.DataFrame(index=languages, columns=CRITERIA, dtype=float)
    pct_low   = pd.DataFrame(index=languages, columns=CRITERIA, dtype=float)

    for lang in languages:
        for crit in CRITERIA:
            sub = df[(df["language"] == lang) & (df["criterion"] == crit)]["score"]
            if sub.empty:
                pct_high.loc[lang, crit] = np.nan
                pct_low.loc[lang, crit]  = np.nan
            else:
                pct_high.loc[lang, crit] = 100 * (sub >= 5).mean()
                pct_low.loc[lang, crit]  = 100 * (sub <= 3).mean()

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    for ax, matrix, title, cmap in zip(
        axes,
        [pct_high, pct_low],
        ["% responses with score ≥ 5  (High zone)",
         "% responses with score ≤ 3  (Low zone)"],
        ["YlGn", "YlOrRd"]
    ):
        matrix.columns = [c.replace("_", "\n").title() for c in CRITERIA]
        sns.heatmap(matrix.astype(float), annot=True, fmt=".1f", cmap=cmap,
                    vmin=0, vmax=100, linewidths=0.5, ax=ax,
                    cbar_kws={"label": "%"})
        ax.set_title(title, fontsize=11, fontweight="bold", pad=10)
        ax.set_xlabel("")
        ax.set_ylabel("")

    fig.suptitle("LLM Judge Sensitivity Map\n"
                 "Where does each language need good score discrimination?",
                 fontsize=13, fontweight="bold")
    plt.tight_layout()
    path = os.path.join(out_dir, "fig7_sensitivity_heatmap.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print("  ✓ fig7_sensitivity_heatmap.png")


# ═══════════════════════════════════════════════════════════════════════════════
# 10.  FIGURE 8  –  Per-language score frequency heatmaps (one per criterion)
# ═══════════════════════════════════════════════════════════════════════════════

def fig_freq_heatmaps(df: pd.DataFrame, out_dir: str):
    """
    Language × Score-value frequency tables, one per criterion.
    Shows exactly at which score values each language concentrates.
    """
    languages = sorted(df["language"].unique())

    fig, axes = plt.subplots(1, 3, figsize=(17, 6))
    fig.suptitle("Score Frequency (%) per Language – per Criterion",
                 fontsize=13, fontweight="bold")

    for ax, crit in zip(axes, CRITERIA):
        matrix = pd.DataFrame(index=languages, columns=SCORES, dtype=float)
        for lang in languages:
            sub = df[(df["language"] == lang) & (df["criterion"] == crit)]["score"]
            total = len(sub) if len(sub) > 0 else 1
            for s in SCORES:
                matrix.loc[lang, s] = round(100 * (sub == s).sum() / total, 1)

        sns.heatmap(matrix.astype(float), annot=True, fmt=".1f",
                    cmap="Blues", vmin=0, vmax=60,
                    linewidths=0.5, ax=ax,
                    cbar_kws={"label": "%"})
        ax.set_title(crit.replace("_", " ").title(), fontweight="bold")
        ax.set_xlabel("Score value")
        ax.set_ylabel("Language" if ax == axes[0] else "")

    plt.tight_layout()
    path = os.path.join(out_dir, "fig8_freq_heatmaps.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print("  ✓ fig8_freq_heatmaps.png")


# ═══════════════════════════════════════════════════════════════════════════════
# 11.  STATISTICAL COMPARISON TABLE  (Kruskal-Wallis + pairwise Mann-Whitney)
# ═══════════════════════════════════════════════════════════════════════════════

def stat_tests(df: pd.DataFrame, out_dir: str):
    rows_kw = []
    for crit in CRITERIA:
        groups = [df[(df["language"] == l) & (df["criterion"] == crit)]["score"].values
                  for l in sorted(df["language"].unique())]
        groups = [g for g in groups if len(g) > 0]
        if len(groups) < 2:
            continue
        stat, p = stats.kruskal(*groups)
        rows_kw.append({"Criterion": crit, "Kruskal-Wallis H": round(stat, 2),
                         "p-value": f"{p:.2e}",
                         "Significant (p<0.05)": "YES" if p < 0.05 else "NO"})

    kw_df = pd.DataFrame(rows_kw)
    kw_df.to_csv(os.path.join(out_dir, "table_kruskal_wallis.csv"), index=False)
    print("  ✓ table_kruskal_wallis.csv")
    return kw_df


# ═══════════════════════════════════════════════════════════════════════════════
# 12.  PRINT CONSOLE SUMMARY
# ═══════════════════════════════════════════════════════════════════════════════

def print_console_summary(df: pd.DataFrame, summary: pd.DataFrame, kw_df: pd.DataFrame):
    print("\n" + "═" * 70)
    print("  ANALYSIS SUMMARY")
    print("═" * 70)
    print(f"  Total rows analysed : {len(df):,}")
    print(f"  Criteria            : {CRITERIA}")
    print(f"  Languages           : {sorted(df['language'].unique())}")

    print("\n── Mean scores per language × criterion ──")
    pivot = summary.pivot(index="Language", columns="Criterion", values="Mean")
    print(pivot.to_string())

    print("\n── % scores ≥ 5 (High zone) ──")
    pivot_hi = summary.pivot(index="Language", columns="Criterion", values="% score≥5")
    print(pivot_hi.to_string())

    print("\n── % scores ≤ 3 (Low zone) ──")
    pivot_lo = summary.pivot(index="Language", columns="Criterion", values="% score≤3")
    print(pivot_lo.to_string())

    print("\n── Kruskal-Wallis test (are languages significantly different?) ──")
    print(kw_df.to_string(index=False))
    print("═" * 70 + "\n")


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"\n{chr(0x2550)*60}")
    print(f"  Human Eval Analysis")
    print(f"  Input : {INPUT_CSV}")
    print(f"  Output: {OUTPUT_DIR}")
    print(f"{chr(0x2550)*60}\n")

    print("[1/5] Loading data …")
    df = load_data(INPUT_CSV)

    print("\n[2/5] Computing summary tables …")
    summary, freq_df = compute_summary_tables(df, OUTPUT_DIR)

    print("\n[3/5] Running statistical tests …")
    kw_df = stat_tests(df, OUTPUT_DIR)

    print("\n[4/5] Generating figures …")
    fig_overall_distributions(df, OUTPUT_DIR)
    fig_per_language_per_criterion(df, OUTPUT_DIR)
    fig_mean_heatmap(df, OUTPUT_DIR)
    fig_stacked_buckets(df, OUTPUT_DIR)
    fig_boxplots(df, OUTPUT_DIR)
    fig_kde(df, OUTPUT_DIR)
    fig_high_score_heatmap(df, OUTPUT_DIR)
    fig_freq_heatmaps(df, OUTPUT_DIR)

    print("\n[5/5] Console summary …")
    print_console_summary(df, summary, kw_df)

    print(f"All outputs saved to: {OUTPUT_DIR}/")
    print("Done ✓\n")


if __name__ == "__main__":
    main()
