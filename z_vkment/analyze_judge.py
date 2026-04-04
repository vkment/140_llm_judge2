"""
analyze_judge.py
================
Srovnání LLM-as-a-judge vs. lidských hodnotitelů.

Klíčová metrika: podmíněný bias per skóre-úroveň
  → Když LLM řekne X, jaký je průměr lidského skóre?
  → Bias = X − human_mean. Kladný = LLM přestřelil, záporný = podstřelil.

Výstupy:
  1. Konzolové tabulky per (locale × criterion): celkový bias/MAE + per-level tabulka
  2. CSV soubor se souhrnnými statistikami (STATS_CSV)

Použití:
  python analyze_judge.py
  (upravte cesty níže)
"""

# ===========================================================================
# VSTUPY — upravte dle potřeby
# ===========================================================================
LLM_CSV   = "z_vkment/oeg_judge_outloc41_3_submission_data.csv"
HUMAN_CSV = "oeg_human_eval_data.csv"
STATS_CSV = "z_vkment/judge_comparison_stats_41_3.csv"
# ===========================================================================

import csv
import sys
from collections import defaultdict

CRITERIA = ["instruction_following", "naturalness", "coherence"]
ALL_LEVELS = [1, 2, 3, 4, 5, 6, 7]

LOCALE_TO_LANGUAGE = {
    "ar_EG": "Arabic",    "bn_BD": "Bengali",  "cs_CZ": "Czech",
    "de_DE": "German",    "en_US": "English",  "hi_IN": "Hindi",
    "id_ID": "Indonesian","ja_JP": "Japanese", "ru_RU": "Russian",
    "zh_CN": "Chinese",
}

# ---------------------------------------------------------------------------
# Načtení dat
# ---------------------------------------------------------------------------

def load_csv(path: str) -> list[dict]:
    try:
        with open(path, newline="", encoding="utf-8") as fh:
            return list(csv.DictReader(fh))
    except FileNotFoundError:
        print(f"[CHYBA] Soubor nenalezen: {path}", file=sys.stderr)
        sys.exit(1)


def index_rows(rows: list[dict]) -> dict:
    """(criterion, system, doc_id, locale) → score (float)"""
    idx = {}
    for r in rows:
        key = (r["criterion"], r["submission_system_name"],
               r["original_instance_id"], r["locale"])
        try:
            idx[key] = float(r["score"])
        except (ValueError, KeyError):
            pass
    return idx


# ---------------------------------------------------------------------------
# Hlavní analýza
# ---------------------------------------------------------------------------

def analyze(llm_rows: list[dict], human_rows: list[dict]) -> tuple[list[dict], list[dict]]:
    """
    Vrátí:
      summary_records  — jeden záznam per (locale × criterion): celkový bias, MAE, distribuce
      level_records    — jeden záznam per (locale × criterion × llm_level): podmíněný bias
    """
    llm_idx   = index_rows(llm_rows)
    human_idx = index_rows(human_rows)

    llm_locales = sorted({r["locale"] for r in llm_rows})

    summary_records = []
    level_records   = []

    for locale in llm_locales:
        lang = LOCALE_TO_LANGUAGE.get(locale, locale)

        for criterion in CRITERIA:

            # level_human[llm_score] = [human_scores...]
            level_human: dict[int, list[float]] = defaultdict(list)
            llm_all   = []
            human_all = []

            for key, lscore in llm_idx.items():
                crit, system, doc_id, loc = key
                if crit != criterion or loc != locale:
                    continue
                hscore = human_idx.get(key)
                if hscore is None:
                    continue
                llm_all.append(lscore)
                human_all.append(hscore)
                level_human[int(round(lscore))].append(hscore)

            n = len(llm_all)
            if n == 0:
                continue

            # Celkový bias a MAE
            diffs      = [l - h for l, h in zip(llm_all, human_all)]
            bias_total = sum(diffs) / n
            mae_total  = sum(abs(d) for d in diffs) / n
            llm_mean   = sum(llm_all) / n
            hum_mean   = sum(human_all) / n

            # Distribuce: podíl skóre v pásmech
            def dist(scores):
                m = len(scores)
                if m == 0:
                    return 0.0, 0.0, 0.0
                return (
                    sum(1 for s in scores if s <= 3) / m,
                    sum(1 for s in scores if 4 <= s <= 5) / m,
                    sum(1 for s in scores if s >= 6) / m,
                )

            ll, lm, lh = dist(llm_all)
            hl, hm, hh = dist(human_all)

            summary_records.append({
                "locale":      locale,
                "language":    lang,
                "criterion":   criterion,
                "n_pairs":     n,
                "llm_mean":    llm_mean,
                "human_mean":  hum_mean,
                "bias_total":  bias_total,
                "mae_total":   mae_total,
                "llm_low":     ll, "llm_mid": lm, "llm_high": lh,
                "hum_low":     hl, "hum_mid": hm, "hum_high": hh,
            })

            # Per-level podmíněný bias
            for level in ALL_LEVELS:
                hscores = level_human.get(level, [])
                if not hscores:
                    level_records.append({
                        "locale": locale, "language": lang,
                        "criterion": criterion,
                        "llm_level": level,
                        "count": 0,
                        "human_mean": None,
                        "cond_bias": None,
                        "recommendation": "—  (LLM toto skóre nepoužilo)",
                    })
                    continue

                hm_level  = sum(hscores) / len(hscores)
                cond_bias = level - hm_level   # kladný = LLM přestřelil

                if abs(cond_bias) < 0.3:
                    rec = "OK"
                elif cond_bias > 0:
                    rec = f"↓  snížit  (LLM o {cond_bias:+.2f} nad lidmi)"
                else:
                    rec = f"↑  zvýšit  (LLM o {cond_bias:+.2f} pod lidmi)"

                level_records.append({
                    "locale":         locale,
                    "language":       lang,
                    "criterion":      criterion,
                    "llm_level":      level,
                    "count":          len(hscores),
                    "human_mean":     hm_level,
                    "cond_bias":      cond_bias,
                    "recommendation": rec,
                })

    return summary_records, level_records


# ---------------------------------------------------------------------------
# Výpis na konzolu
# ---------------------------------------------------------------------------

def print_report(summary: list[dict], levels: list[dict]) -> None:
    locales = sorted({r["locale"] for r in summary})

    for locale in locales:
        lang = LOCALE_TO_LANGUAGE.get(locale, locale)
        s_rows = [r for r in summary if r["locale"] == locale]
        l_rows = [r for r in levels  if r["locale"] == locale]

        print()
        print("=" * 74)
        print(f"  {locale}  ({lang})")
        print("=" * 74)

        for criterion in CRITERIA:
            s = next((r for r in s_rows if r["criterion"] == criterion), None)
            if s is None:
                continue

            print()
            print(f"  ── {criterion}")
            print(f"     n={s['n_pairs']}  "
                  f"LLM mean={s['llm_mean']:.2f}  "
                  f"Hum mean={s['human_mean']:.2f}  "
                  f"bias={s['bias_total']:+.3f}  MAE={s['mae_total']:.3f}")
            print(f"     Distribuce:  "
                  f"LLM  low={s['llm_low']*100:4.1f}% "
                  f"mid={s['llm_mid']*100:4.1f}% "
                  f"high={s['llm_high']*100:4.1f}%  │  "
                  f"Hum  low={s['hum_low']*100:4.1f}% "
                  f"mid={s['hum_mid']*100:4.1f}% "
                  f"high={s['hum_high']*100:4.1f}%")

            # Per-level tabulka
            print(f"     {'LLM':>5}  {'N':>5}  {'Hum mean':>9}  {'Bias':>7}  Doporučení")
            print(f"     {'─'*5}  {'─'*5}  {'─'*9}  {'─'*7}  {'─'*38}")
            for lr in sorted(
                [r for r in l_rows if r["criterion"] == criterion],
                key=lambda x: x["llm_level"]
            ):
                if lr["count"] == 0:
                    print(f"     {lr['llm_level']:>5}  {'─':>5}")
                    continue
                print(f"     {lr['llm_level']:>5}  {lr['count']:>5}  "
                      f"{lr['human_mean']:>9.3f}  "
                      f"{lr['cond_bias']:>+7.3f}  {lr['recommendation']}")

    # Globální přehled — největší podmíněné biasy
    print()
    print("=" * 74)
    print("  GLOBÁLNÍ PŘEHLED — největší podmíněné biasy  (|bias| ≥ 0.5)")
    print("  Priorita pro úpravu anchor definic v promptech")
    print("=" * 74)
    valid = [r for r in levels
             if r["cond_bias"] is not None and abs(r["cond_bias"]) >= 0.5]
    valid.sort(key=lambda x: abs(x["cond_bias"]), reverse=True)

    if not valid:
        print("  (žádný podmíněný bias ≥ 0.5)")
    else:
        print(f"  {'Locale':8}  {'Criterion':24}  {'LLM':>4}  {'N':>5}  "
              f"{'Hum mean':>9}  {'Bias':>7}  Doporučení")
        print(f"  {'─'*8}  {'─'*24}  {'─'*4}  {'─'*5}  {'─'*9}  {'─'*7}  {'─'*38}")
        for r in valid[:25]:
            print(f"  {r['locale']:8}  {r['criterion']:24}  {r['llm_level']:>4}  "
                  f"{r['count']:>5}  {r['human_mean']:>9.3f}  "
                  f"{r['cond_bias']:>+7.3f}  {r['recommendation']}")


# ---------------------------------------------------------------------------
# Uložení CSV
# ---------------------------------------------------------------------------

def save_csv(summary: list[dict], levels: list[dict], path: str) -> None:
    if not summary and not levels:
        return
    with open(path, "w", newline="", encoding="utf-8") as fh:
        if summary:
            fh.write("# SUMMARY (per locale x criterion)\n")
            w = csv.DictWriter(fh, fieldnames=list(summary[0].keys()))
            w.writeheader()
            for r in summary:
                w.writerow({k: (f"{v:.4f}" if isinstance(v, float) else v)
                            for k, v in r.items()})
        fh.write("\n")
        if levels:
            fh.write("# LEVEL DETAIL (per locale x criterion x llm_level)\n")
            w2 = csv.DictWriter(fh, fieldnames=list(levels[0].keys()))
            w2.writeheader()
            for r in levels:
                w2.writerow({k: (f"{v:.4f}" if isinstance(v, float) else
                                 ("" if v is None else v))
                             for k, v in r.items()})
    print(f"\n  → Statistiky uloženy do: {path}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print(f"Načítám LLM data:   {LLM_CSV}")
    print(f"Načítám Human data: {HUMAN_CSV}")
    llm_rows   = load_csv(LLM_CSV)
    human_rows = load_csv(HUMAN_CSV)
    print(f"  LLM:   {len(llm_rows):,} řádků")
    print(f"  Human: {len(human_rows):,} řádků")

    summary, levels = analyze(llm_rows, human_rows)

    if not summary:
        print("[CHYBA] Žádné sdílené záznamy nenalezeny.")
        print("        Zkontrolujte, zda oba CSV sdílí stejné doc_id, system a locale.")
        sys.exit(1)

    print_report(summary, levels)
    save_csv(summary, levels, STATS_CSV)
