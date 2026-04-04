"""
analyze_acc_eq_within.py
────────────────────────
Studuje distribuci acc_eq přes 46 promptů uvnitř každé (locale × criterion) skupiny.

Vstup:
  JUDGE_CSV  – soubor s LLM judge skóre (22 080 řádků)
  HUMAN_CSV  – soubor s lidskými hodnoceními (22 080 řádků)

Výstupy:
  - textová analýza do stdout
  - grafy do složky acc_eq_within_plots/
"""

# ---------------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------------

JUDGE_CSV  = "z_vkment/2nd-runs/oeg_judge_outloc46_1_submission_data.csv"
HUMAN_CSV  = "oeg_human_eval_data.csv"

# ---------------------------------------------------------------------------
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ---------------------------------------------------------------------------
# acc_eq implementace (per Deutsch et al.)
# ---------------------------------------------------------------------------

def acc_eq(scores_human, scores_judge):
    C = D = T_h = T_m = T_hm = 0
    n = len(scores_human)
    for i in range(n):
        for j in range(i + 1, n):
            h_i, h_j = scores_human[i], scores_human[j]
            m_i, m_j = scores_judge[i], scores_judge[j]
            if h_i == h_j and m_i == m_j:
                T_hm += 1
            elif h_i == h_j:
                T_h += 1
            elif m_i == m_j:
                T_m += 1
            elif (h_i < h_j and m_i < m_j) or (h_i > h_j and m_i > m_j):
                C += 1
            else:
                D += 1
    denom = C + D + T_h + T_m + T_hm
    return (C + T_hm) / denom if denom > 0 else 0.0

# ---------------------------------------------------------------------------
# Načtení dat
# ---------------------------------------------------------------------------

for p in [JUDGE_CSV, HUMAN_CSV]:
    if not Path(p).exists():
        sys.exit(f"ERROR: soubor nenalezen: {p}")

judge = pd.read_csv(JUDGE_CSV)
human = pd.read_csv(HUMAN_CSV)

print(f"Judge: {len(judge):,} řádků | Human: {len(human):,} řádků")

# Kombinovaný klíč pro instance
for df in [judge, human]:
    df["instance_key"] = df["original_instance_id"] + "_" + df["locale"]

LOCALES   = sorted(judge["locale"].unique())
CRITERIA  = sorted(judge["criterion"].unique())
JUDGES    = sorted(judge["judge_model_name"].unique())

# ---------------------------------------------------------------------------
# Výpočet acc_eq per prompt pro každou (locale × criterion) skupinu
# ---------------------------------------------------------------------------

records = []  # jeden řádek = jeden prompt v jedné skupině

for locale in LOCALES:
    for criterion in CRITERIA:
        jlc = judge[(judge["locale"] == locale) & (judge["criterion"] == criterion)]
        hlc = human[(human["locale"] == locale) & (human["criterion"] == criterion)]

        instances = sorted(jlc["instance_key"].unique())

        for inst in instances:
            j_inst = jlc[jlc["instance_key"] == inst].sort_values("submission_system_name")
            h_inst = hlc[hlc["instance_key"] == inst].sort_values("submission_system_name")

            if len(j_inst) != len(h_inst) or len(j_inst) == 0:
                continue

            sj = j_inst["score"].values.astype(float)
            sh = h_inst["score"].values.astype(float)

            aeq = acc_eq(sh, sj)

            # Vlastnosti tohoto promptu
            human_std  = float(np.std(sh))
            human_mean = float(np.mean(sh))
            judge_std  = float(np.std(sj))
            judge_mean = float(np.mean(sj))
            n_human_ties = sum(
                1 for i in range(len(sh)) for j in range(i+1, len(sh)) if sh[i] == sh[j]
            )
            n_judge_ties = sum(
                1 in range(len(sj)) for i in range(len(sj)) for j in range(i+1, len(sj)) if sj[i] == sj[j]
            )

            records.append({
                "locale": locale,
                "criterion": criterion,
                "instance_key": inst,
                "original_instance_id": inst.rsplit("_", 2)[0],
                "acc_eq": aeq,
                "human_mean": human_mean,
                "human_std": human_std,
                "judge_mean": judge_mean,
                "judge_std": judge_std,
            })

df = pd.DataFrame(records)
print(f"Celkem záznamů: {len(df):,}  (očekáváno {len(LOCALES)*len(CRITERIA)*46})\n")

# ---------------------------------------------------------------------------
# 1. Celkový přehled
# ---------------------------------------------------------------------------

print("═" * 70)
print("1. CELKOVÝ PŘEHLED acc_eq přes všechny (locale × criterion) skupiny")
print("═" * 70)
print(df["acc_eq"].describe().round(4).to_string())
print()

for thr in [0.3, 0.4, 0.5, 0.6, 0.7]:
    n = (df["acc_eq"] < thr).sum()
    print(f"  Promptů s acc_eq < {thr}: {n:4d} / {len(df)}  ({100*n/len(df):.1f}%)")
print()

# ---------------------------------------------------------------------------
# 2. Průměr a std per (locale × criterion)
# ---------------------------------------------------------------------------

print("═" * 70)
print("2. acc_eq per (locale × criterion)  — mean | std | min | max")
print("═" * 70)
grp = df.groupby(["locale", "criterion"])["acc_eq"].agg(["mean","std","min","max"]).round(4)
print(grp.to_string())
print()

# Pivot: mean
pivot_mean = grp["mean"].unstack("criterion")
print("Pivot — mean acc_eq:")
print(pivot_mean.round(4).to_string())
print()

# Pivot: std
pivot_std = grp["std"].unstack("criterion")
print("Pivot — std acc_eq (rozptyl přes 46 promptů):")
print(pivot_std.round(4).to_string())
print()

# ---------------------------------------------------------------------------
# 3. Top-15 nejhorších promptů (per locale × criterion)
# ---------------------------------------------------------------------------

print("═" * 70)
print("3. TOP-20 promptů s nejnižší acc_eq")
print("═" * 70)
worst = df.nsmallest(20, "acc_eq")[
    ["locale","criterion","original_instance_id","acc_eq","human_std","judge_std"]
].reset_index(drop=True)
print(worst.to_string())
print()

# ---------------------------------------------------------------------------
# 4. Top-15 nejlepších promptů
# ---------------------------------------------------------------------------

print("═" * 70)
print("4. TOP-20 promptů s nejvyšší acc_eq")
print("═" * 70)
best = df.nlargest(20, "acc_eq")[
    ["locale","criterion","original_instance_id","acc_eq","human_std","judge_std"]
].reset_index(drop=True)
print(best.to_string())
print()

# ---------------------------------------------------------------------------
# 5. Korelace: human_std vs. acc_eq
# ---------------------------------------------------------------------------

print("═" * 70)
print("5. KORELACE: human_std vs. acc_eq")
print("   (vyšší human_std = lidé více rozlišují systémy = snazší pro judge?)")
print("═" * 70)
overall_corr = df[["human_std","judge_std","acc_eq"]].corr().round(4)
print(overall_corr.to_string())
print()

print("Per (locale × criterion):")
corr_rows = []
for (locale, criterion), g in df.groupby(["locale","criterion"]):
    c = g["human_std"].corr(g["acc_eq"])
    corr_rows.append({"locale": locale, "criterion": criterion, "corr_human_std_acceq": round(c, 4)})
corr_df = pd.DataFrame(corr_rows).set_index(["locale","criterion"])
print(corr_df.unstack("criterion").round(4).to_string())
print()

# ---------------------------------------------------------------------------
# 6. Prompty sdílené přes jazyky (stejné original_instance_id)
# ---------------------------------------------------------------------------

print("═" * 70)
print("6. SDÍLENÉ PROMPTY — acc_eq pro stejný original_instance_id přes lokály")
print("   (prompty vzniklé překladem by měly mít podobnou acc_eq)")
print("═" * 70)
shared_ids = df.groupby("original_instance_id")["locale"].nunique()
shared_ids = shared_ids[shared_ids > 1].index

shared = df[df["original_instance_id"].isin(shared_ids)].copy()
pivot_shared = shared.groupby(["original_instance_id","locale"])["acc_eq"].mean().unstack("locale")

# Přidáme variance přes lokály (jak moc se liší acc_eq pro stejný prompt v různých jazycích)
pivot_shared["std_across_locales"] = pivot_shared.std(axis=1)

print(f"Promptů sdílených přes více lokálů: {len(shared_ids)}")
print(f"\nTop-15 promptů s nejvyšší variancí acc_eq přes lokály:")
print(pivot_shared.nlargest(15, "std_across_locales")[["std_across_locales"] + LOCALES[:5]].round(4).to_string())
print()
print(f"\nTop-15 promptů s nejnižší variancí (konzistentní přes lokály):")
print(pivot_shared.nsmallest(15, "std_across_locales")[["std_across_locales"] + LOCALES[:5]].round(4).to_string())
print()

# ---------------------------------------------------------------------------
# GRAFY
# ---------------------------------------------------------------------------

out_dir = Path("acc_eq_within_plots")
out_dir.mkdir(exist_ok=True)

def save(fig, name):
    p = out_dir / name
    fig.savefig(p, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Uloženo: {p}")

print("─" * 70)
print("GRAFY …")

# ── A. Histogramy acc_eq per locale (řádky) × criterion (sloupce) ─────────
fig, axes = plt.subplots(len(LOCALES), len(CRITERIA),
                          figsize=(len(CRITERIA)*4, len(LOCALES)*2.2),
                          sharex=True, sharey=False)
for r, locale in enumerate(LOCALES):
    for c, criterion in enumerate(CRITERIA):
        ax = axes[r][c]
        data = df[(df["locale"]==locale) & (df["criterion"]==criterion)]["acc_eq"]
        ax.hist(data, bins=15, range=(0,1), color="#4C72B0", edgecolor="white", lw=0.5)
        mu = data.mean()
        ax.axvline(mu, color="red", lw=1.2, linestyle="--", label=f"μ={mu:.2f}")
        ax.legend(fontsize=7)
        if r == 0: ax.set_title(criterion, fontsize=9)
        if c == 0: ax.set_ylabel(locale, fontsize=8)
        ax.tick_params(labelsize=7)
fig.suptitle("Distribuce acc_eq přes 46 promptů: locale × criterion", fontsize=13, y=1.01)
fig.tight_layout()
save(fig, "A_hist_acc_eq_locale_criterion.png")

# ── B. Boxploty per locale (agregováno přes criteria) ─────────────────────
fig, ax = plt.subplots(figsize=(12, 4))
data_by_locale = [df[df["locale"]==loc]["acc_eq"].values for loc in LOCALES]
bp = ax.boxplot(data_by_locale, labels=LOCALES, patch_artist=True)
for patch in bp["boxes"]:
    patch.set_facecolor("#4C72B0")
    patch.set_alpha(0.6)
ax.axhline(0.5, color="gray", linestyle=":", lw=1)
ax.set_ylabel("acc_eq")
ax.set_title("Distribuce acc_eq per locale (všechna kritéria)")
ax.tick_params(axis="x", rotation=20)
fig.tight_layout()
save(fig, "B_boxplot_by_locale.png")

# ── C. Boxploty per criterion ──────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(7, 4))
data_by_crit = [df[df["criterion"]==c]["acc_eq"].values for c in CRITERIA]
bp = ax.boxplot(data_by_crit, labels=CRITERIA, patch_artist=True)
for patch in bp["boxes"]:
    patch.set_facecolor("#55A868")
    patch.set_alpha(0.6)
ax.axhline(0.5, color="gray", linestyle=":", lw=1)
ax.set_ylabel("acc_eq")
ax.set_title("Distribuce acc_eq per criterion (všechny lokály)")
fig.tight_layout()
save(fig, "C_boxplot_by_criterion.png")

# ── D. Scatter: human_std vs. acc_eq per locale ────────────────────────────
fig, axes = plt.subplots(2, 5, figsize=(16, 6), sharey=True, sharex=False)
axes = axes.flatten()
for ax, locale in zip(axes, LOCALES):
    sub = df[df["locale"]==locale]
    ax.scatter(sub["human_std"], sub["acc_eq"], alpha=0.4, s=10, c="#C44E52")
    ax.set_title(locale, fontsize=9)
    ax.set_xlabel("human std", fontsize=8)
    ax.set_ylabel("acc_eq" if ax == axes[0] else "", fontsize=8)
    ax.tick_params(labelsize=7)
    # Trendová linie
    if len(sub) > 2:
        z = np.polyfit(sub["human_std"], sub["acc_eq"], 1)
        p = np.poly1d(z)
        xs = np.linspace(sub["human_std"].min(), sub["human_std"].max(), 50)
        ax.plot(xs, p(xs), "k--", lw=1)
fig.suptitle("human_std vs. acc_eq per locale\n(vyšší human_std = lidé více rozlišují = snazší pro judge?)", fontsize=12)
fig.tight_layout()
save(fig, "D_scatter_human_std_vs_acceq.png")

# ── E. Heatmapa mean acc_eq: locale × criterion ────────────────────────────
fig, ax = plt.subplots(figsize=(6, 5))
mat = pivot_mean.values
im = ax.imshow(mat, aspect="auto", cmap="RdYlGn", vmin=0.3, vmax=0.8)
ax.set_xticks(range(len(pivot_mean.columns)))
ax.set_xticklabels(pivot_mean.columns, rotation=20, ha="right", fontsize=9)
ax.set_yticks(range(len(pivot_mean.index)))
ax.set_yticklabels(pivot_mean.index, fontsize=9)
for i in range(mat.shape[0]):
    for j in range(mat.shape[1]):
        ax.text(j, i, f"{mat[i,j]:.3f}", ha="center", va="center", fontsize=8)
plt.colorbar(im, ax=ax, label="mean acc_eq")
ax.set_title("Mean acc_eq: locale × criterion", fontsize=11)
fig.tight_layout()
save(fig, "E_heatmap_mean_acceq.png")

# ── F. Heatmapa std acc_eq: locale × criterion (nestabilita) ──────────────
fig, ax = plt.subplots(figsize=(6, 5))
mat_std = pivot_std.values
im = ax.imshow(mat_std, aspect="auto", cmap="YlOrRd", vmin=0)
ax.set_xticks(range(len(pivot_std.columns)))
ax.set_xticklabels(pivot_std.columns, rotation=20, ha="right", fontsize=9)
ax.set_yticks(range(len(pivot_std.index)))
ax.set_yticklabels(pivot_std.index, fontsize=9)
for i in range(mat_std.shape[0]):
    for j in range(mat_std.shape[1]):
        ax.text(j, i, f"{mat_std[i,j]:.3f}", ha="center", va="center", fontsize=8)
plt.colorbar(im, ax=ax, label="std acc_eq")
ax.set_title("Std acc_eq přes 46 promptů: locale × criterion\n(vyšší = nestabilnější výkon judge)", fontsize=11)
fig.tight_layout()
save(fig, "F_heatmap_std_acceq.png")

print(f"\nVšechny grafy uloženy do: {out_dir.resolve()}")
print("Hotovo.")
