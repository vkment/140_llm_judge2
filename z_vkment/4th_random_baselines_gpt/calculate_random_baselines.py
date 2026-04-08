import math
import pandas as pd
from itertools import combinations

# =========================================================
# VSTUPNÍ SOUBOR
# =========================================================
input_file = "oeg_human_eval_data.csv"

# =========================================================
# PARAMETRY
# =========================================================
score_values = [1, 2, 3, 4, 5, 6, 7]   # Likert 1-7
expected_random_strict_match = 3 / 7   # P(random pair agrees with strict human ordering)
expected_random_tie_match = 1 / 7      # P(random pair is tie when human pair is tie)

# =========================================================
# POMOCNÉ FUNKCE
# =========================================================
def expected_random_acc_eq_for_vector(scores):
    """
    Exaktní expected value acc_eq pro JEDEN vektor lidských hodnocení.

    scores = seznam 16 lidských skóre pro dané:
        (locale, criterion, original_instance_id)
    kde pořadí odpovídá různým submission_system_name.

    acc_eq = (C + T_hm) / (C + D + T_h + T_m + T_hm)

    Pro náhodný model s nezávislými uniformními skóre z {1,...,7}:
      - pokud je lidský pár striktní, expected contribution = 3/7
      - pokud je lidský pár tie,      expected contribution = 1/7

    Je-li:
      S = počet strict pairs v human
      T = počet tied pairs v human
      N = S + T = n choose 2

    pak
      E[acc_eq] = (S*(3/7) + T*(1/7)) / N
                = (3S + T) / (7N)
    """
    n = len(scores)
    total_pairs = n * (n - 1) // 2

    strict_pairs = 0
    tied_pairs = 0

    for i, j in combinations(range(n), 2):
        if scores[i] == scores[j]:
            tied_pairs += 1
        else:
            strict_pairs += 1

    expected_acc_eq = (
        strict_pairs * expected_random_strict_match
        + tied_pairs * expected_random_tie_match
    ) / total_pairs

    return {
        "n_systems": n,
        "total_pairs": total_pairs,
        "strict_pairs": strict_pairs,
        "tied_pairs": tied_pairs,
        "expected_random_acc_eq": expected_acc_eq,
    }


def format_vector(scores_by_system):
    """
    Hezký tisk vektoru ve formátu:
    system1=7.0, system2=5.0, ...
    """
    parts = []
    for system_name, score in scores_by_system.items():
        parts.append(f"{system_name}={score}")
    return ", ".join(parts)


# =========================================================
# NAČTENÍ DAT
# =========================================================
df = pd.read_csv(input_file)

# Bezpečnostní kontroly
required_columns = [
    "judge_model_name",
    "criterion",
    "submission_system_name",
    "original_instance_id",
    "locale",
    "score",
]
missing_cols = [c for c in required_columns if c not in df.columns]
if missing_cols:
    raise ValueError(f"Ve vstupu chybí sloupce: {missing_cols}")

# Očekáváme human data
if not (df["judge_model_name"] == "human").all():
    raise ValueError("Soubor obsahuje i jiné judge_model_name než 'human'.")

# Pro jistotu převedeme score na float
df["score"] = df["score"].astype(float)

# =========================================================
# KONSTRUKCE VEKTORŮ
# =========================================================
# Jeden vektor odpovídá:
#   (locale, criterion, original_instance_id)
# a jeho 16 složek odpovídá submission_system_name

group_cols = ["locale", "criterion", "original_instance_id"]

vectors = []
locale_to_vectors = {}
locale_criterion_to_baselines = {}
locale_to_baselines = {}

for (locale, criterion, original_instance_id), group in df.groupby(group_cols):
    group_sorted = group.sort_values("submission_system_name")

    systems = group_sorted["submission_system_name"].tolist()
    scores = group_sorted["score"].tolist()

    if len(systems) != 16:
        raise ValueError(
            f"Neočekávaný počet systémů pro "
            f"locale={locale}, criterion={criterion}, original_instance_id={original_instance_id}: "
            f"{len(systems)} místo 16"
        )

    # kontrola uniqueness systémů ve vektoru
    if len(set(systems)) != 16:
        raise ValueError(
            f"Duplicita submission_system_name pro "
            f"locale={locale}, criterion={criterion}, original_instance_id={original_instance_id}"
        )

    scores_by_system = dict(zip(systems, scores))
    baseline_info = expected_random_acc_eq_for_vector(scores)

    record = {
        "locale": locale,
        "criterion": criterion,
        "original_instance_id": original_instance_id,
        "systems": systems,
        "scores": scores,
        "scores_by_system": scores_by_system,
        **baseline_info,
    }
    vectors.append(record)

    locale_to_vectors.setdefault(locale, []).append(record)
    locale_to_baselines.setdefault(locale, []).append(baseline_info["expected_random_acc_eq"])
    locale_criterion_to_baselines.setdefault((locale, criterion), []).append(
        baseline_info["expected_random_acc_eq"]
    )

# =========================================================
# TISK VŠECH VEKTORŮ SEPARÁTNĚ PODLE LOCALE
# =========================================================
print("=" * 80)
print("VEKTORY LIDSKÝCH HODNOCENÍ")
print("=" * 80)
print()
print(
    "Každý vektor odpovídá jedné trojici "
    "(locale, criterion, original_instance_id) a má dimenzi 16.\n"
    "Složky vektoru jsou seřazeny podle submission_system_name.\n"
)

for locale in sorted(locale_to_vectors.keys()):
    print("#" * 80)
    print(f"LOCALE: {locale}")
    print("#" * 80)

    locale_vectors = sorted(
        locale_to_vectors[locale],
        key=lambda x: (x["criterion"], x["original_instance_id"])
    )

    current_criterion = None
    vector_count = 0

    for record in locale_vectors:
        criterion = record["criterion"]
        original_instance_id = record["original_instance_id"]

        if criterion != current_criterion:
            current_criterion = criterion
            print()
            print(f"--- CRITERION: {criterion} ---")
            print()

        vector_count += 1
        print(f"[{vector_count}] original_instance_id = {original_instance_id}")
        print(f"vector = [{format_vector(record['scores_by_system'])}]")
        print(
            f"pairs={record['total_pairs']}, "
            f"strict_pairs={record['strict_pairs']}, "
            f"tied_pairs={record['tied_pairs']}, "
            f"expected_random_acc_eq={record['expected_random_acc_eq']:.6f}"
        )
        print()

    print()

# =========================================================
# DOKUMENTACE VÝPOČTU RANDOM BASELINE
# =========================================================
print("=" * 80)
print("DOKUMENTACE VÝPOČTU RANDOM BASELINE PRO acc_eq")
print("=" * 80)
print()
print("Likertova škála: 1 až 7")
print("Předpoklad baseline: náhodný LLM-judge přiřadí každému systému skóre")
print("nezávisle a rovnoměrně z množiny {1,2,3,4,5,6,7}.")
print()
print("Pro libovolný pár systémů (i, j):")
print("  P(X < Y) = 3/7")
print("  P(X > Y) = 3/7")
print("  P(X = Y) = 1/7")
print()
print("Proto pro jeden pár:")
print("  - má-li human striktní pořadí, expected contribution do acc_eq je 3/7")
print("  - má-li human tie,             expected contribution do acc_eq je 1/7")
print()
print("Je-li ve vektoru:")
print("  S = počet strict pairs")
print("  T = počet tied pairs")
print("  N = S + T = C(16,2) = 120")
print()
print("Pak exaktně:")
print("  E[random acc_eq for this vector] = (S*(3/7) + T*(1/7)) / N")
print("                                  = (3S + T) / (7N)")
print()

# =========================================================
# BASELINE PO LOCALE × CRITERION
# =========================================================
print("=" * 80)
print("RANDOM BASELINE PO LOCALE × CRITERION")
print("=" * 80)
print()

for (locale, criterion) in sorted(locale_criterion_to_baselines.keys()):
    vals = locale_criterion_to_baselines[(locale, criterion)]
    avg_val = sum(vals) / len(vals)
    print(
        f"locale={locale}, criterion={criterion}, "
        f"n_vectors={len(vals)}, expected_random_acc_eq_mean={avg_val:.6f}"
    )

print()

# =========================================================
# BASELINE PO LOCALE
# =========================================================
print("=" * 80)
print("RANDOM BASELINE PO LOCALE")
print("=" * 80)
print()

for locale in sorted(locale_to_baselines.keys()):
    vals = locale_to_baselines[locale]
    avg_val = sum(vals) / len(vals)
    print(
        f"locale={locale}, "
        f"n_vectors={len(vals)}, "
        f"expected_random_acc_eq_mean={avg_val:.6f}"
    )

print()

# =========================================================
# GLOBÁLNÍ SHRNUTÍ
# =========================================================
all_baselines = [r["expected_random_acc_eq"] for r in vectors]
print("=" * 80)
print("GLOBÁLNÍ SHRNUTÍ")
print("=" * 80)
print(f"Počet všech vektorů: {len(vectors)}")
print(f"Minimum vector baseline: {min(all_baselines):.6f}")
print(f"Maximum vector baseline: {max(all_baselines):.6f}")
print(f"Průměrný baseline přes všechny vektory: {sum(all_baselines) / len(all_baselines):.6f}")