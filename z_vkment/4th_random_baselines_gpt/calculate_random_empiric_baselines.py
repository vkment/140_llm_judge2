import numpy as np
import pandas as pd
from itertools import combinations

# =========================================================
# VSTUPNÍ A VÝSTUPNÍ SOUBORY
# =========================================================
input_file = "oeg_human_eval_data.csv"
output_file = "z_vkment/calculate_random_empiric_baselines_results.txt"

# =========================================================
# PARAMETRY SIMULACE
# =========================================================
n_simulations = 100000
chunk_size = 5000
random_seed = 42

# =========================================================
# POMOCNÉ FUNKCE
# =========================================================
def format_vector(scores_by_system):
    parts = []
    for system_name, score in scores_by_system.items():
        parts.append(f"{system_name}={score}")
    return ", ".join(parts)


def get_pair_indices(n):
    pair_i = []
    pair_j = []
    for i, j in combinations(range(n), 2):
        pair_i.append(i)
        pair_j.append(j)
    return np.array(pair_i, dtype=np.int32), np.array(pair_j, dtype=np.int32)


def get_pair_relations(scores):
    """
    Pro vektor skóre vrátí relace všech párů:
      +1 pokud scores[i] > scores[j]
      -1 pokud scores[i] < scores[j]
       0 pokud tie
    """
    scores = np.asarray(scores, dtype=np.float32)
    pair_i, pair_j = get_pair_indices(len(scores))
    diff = scores[pair_i] - scores[pair_j]
    relations = np.sign(diff).astype(np.int8)
    return relations, pair_i, pair_j


def simulate_expected_random_acc_eq(scores, probs, rng, n_simulations=100000, chunk_size=5000):
    """
    Monte Carlo estimate expected_random_acc_eq pro jeden lidský vektor scores,
    kde random judge losuje každou z 16 hodnot nezávisle z empirické distribuce probs
    příslušné pro dané locale x criterion.

    acc_eq zde lze pro jeden pár chápat jako shodu znaménka relace:
      human: sign(h_i - h_j)
      rand : sign(r_i - r_j)

    Proto pro každý simulovaný 16-vektor:
      acc_eq = mean( sign(rand_i-rand_j) == sign(human_i-human_j) ) přes všech 120 párů
    """
    scores = np.asarray(scores, dtype=np.float32)
    n = len(scores)
    if n != 16:
        raise ValueError(f"Očekáván vektor dimenze 16, ale dostal jsem {n}.")

    human_rel, pair_i, pair_j = get_pair_relations(scores)
    total_pairs = len(human_rel)

    total_acc_sum = 0.0
    sims_done = 0

    score_values = np.arange(1, 8, dtype=np.int8)

    while sims_done < n_simulations:
        current_chunk = min(chunk_size, n_simulations - sims_done)

        # random judge: i.i.d. sampling z empirické distribuce locale x criterion
        random_scores = rng.choice(score_values, size=(current_chunk, n), p=probs)

        rand_diff = random_scores[:, pair_i] - random_scores[:, pair_j]
        rand_rel = np.sign(rand_diff).astype(np.int8)

        # acc_eq pro každý simulovaný vektor = podíl shodných relací přes 120 párů
        acc_vals = (rand_rel == human_rel).mean(axis=1)

        total_acc_sum += acc_vals.sum()
        sims_done += current_chunk

    return total_acc_sum / n_simulations


def empirical_distribution_for_block(block_scores):
    """
    block_scores = všechny human score hodnoty pro jedno locale x criterion
    (mělo by jich být 46 * 16 = 736)
    Vrací pravděpodobnosti pro hodnoty 1..7.
    """
    counts = np.zeros(7, dtype=np.int64)
    for x in block_scores:
        xi = int(round(float(x)))
        if xi < 1 or xi > 7:
            raise ValueError(f"Neočekávané score mimo 1..7: {x}")
        counts[xi - 1] += 1

    probs = counts / counts.sum()

    if not np.isclose(probs.sum(), 1.0):
        raise ValueError("Empirické pravděpodobnosti nedávají součet 1.")

    return counts, probs


def write_line(s, fh=None):
    print(s)
    if fh is not None:
        fh.write(s + "\n")


# =========================================================
# NAČTENÍ DAT
# =========================================================
print(f"[INFO] Načítám vstupní soubor: {input_file}")
df = pd.read_csv(input_file)

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

if not (df["judge_model_name"] == "human").all():
    raise ValueError("Soubor obsahuje i jiné judge_model_name než 'human'.")

df["score"] = df["score"].astype(float)

# =========================================================
# EMPIRICKÉ DISTRIBUCE PRO locale x criterion
# =========================================================
print("[INFO] Zjišťuji empirické distribuce pro každý locale x criterion...")

locale_criterion_to_distribution = {}

for (locale, criterion), block in sorted(df.groupby(["locale", "criterion"]), key=lambda x: x[0]):
    block_scores = block["score"].tolist()
    counts, probs = empirical_distribution_for_block(block_scores)

    locale_criterion_to_distribution[(locale, criterion)] = {
        "counts": counts,
        "probs": probs,
        "n_scores": len(block_scores),
    }

    print(
        f"[INFO] Empirická distribuce pro locale={locale}, criterion={criterion}: "
        f"n_scores={len(block_scores)}, counts={counts.tolist()}, probs={[round(p, 6) for p in probs.tolist()]}"
    )

# =========================================================
# KONSTRUKCE VEKTORŮ
# =========================================================
print("[INFO] Konstruuji 16-dimenzionální lidské vektory po (locale, criterion, original_instance_id)...")

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

    if len(set(systems)) != 16:
        raise ValueError(
            f"Duplicita submission_system_name pro "
            f"locale={locale}, criterion={criterion}, original_instance_id={original_instance_id}"
        )

    scores_by_system = dict(zip(systems, scores))

    record = {
        "locale": locale,
        "criterion": criterion,
        "original_instance_id": original_instance_id,
        "systems": systems,
        "scores": scores,
        "scores_by_system": scores_by_system,
    }
    vectors.append(record)
    locale_to_vectors.setdefault(locale, []).append(record)

print(f"[INFO] Celkem nalezeno vektorů: {len(vectors)}")

# =========================================================
# SIMULACE EMPIRIC NULL
# =========================================================
print("[INFO] Spouštím Monte Carlo simulace empiric null...")
rng = np.random.default_rng(random_seed)

for locale in sorted(locale_to_vectors.keys()):
    locale_vectors = sorted(
        locale_to_vectors[locale],
        key=lambda x: (x["criterion"], x["original_instance_id"])
    )

    print(f"[INFO] Locale {locale}: {len(locale_vectors)} vektorů")

    for idx, record in enumerate(locale_vectors, start=1):
        criterion = record["criterion"]
        original_instance_id = record["original_instance_id"]
        probs = locale_criterion_to_distribution[(locale, criterion)]["probs"]

        print(
            f"[INFO] Simuluji locale={locale}, criterion={criterion}, "
            f"vector={idx}/{len(locale_vectors)}, original_instance_id={original_instance_id}"
        )

        expected_random_acc_eq = simulate_expected_random_acc_eq(
            scores=record["scores"],
            probs=probs,
            rng=rng,
            n_simulations=n_simulations,
            chunk_size=chunk_size,
        )

        record["expected_random_acc_eq"] = expected_random_acc_eq

        locale_to_baselines.setdefault(locale, []).append(expected_random_acc_eq)
        locale_criterion_to_baselines.setdefault((locale, criterion), []).append(expected_random_acc_eq)

print("[INFO] Simulace dokončeny.")

# =========================================================
# ZÁPIS VÝSLEDKŮ NA TERMINÁL I DO SOUBORU
# =========================================================
with open(output_file, "w", encoding="utf-8") as fh:
    write_line("=" * 80, fh)
    write_line("VEKTORY LIDSKÝCH HODNOCENÍ + EMPIRIC NULL BASELINE", fh)
    write_line("=" * 80, fh)
    write_line("", fh)
    write_line(
        "Každý vektor odpovídá jedné trojici "
        "(locale, criterion, original_instance_id) a má dimenzi 16.", fh
    )
    write_line("Složky vektoru jsou seřazeny podle submission_system_name.", fh)
    write_line("", fh)

    for locale in sorted(locale_to_vectors.keys()):
        write_line("#" * 80, fh)
        write_line(f"LOCALE: {locale}", fh)
        write_line("#" * 80, fh)

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
                write_line("", fh)
                write_line(f"--- CRITERION: {criterion} ---", fh)
                write_line("", fh)

            vector_count += 1
            write_line(f"[{vector_count}] original_instance_id = {original_instance_id}", fh)
            write_line(f"vector = [{format_vector(record['scores_by_system'])}]", fh)
            write_line(
                f"expected_random_acc_eq_empiric_null={record['expected_random_acc_eq']:.6f}",
                fh
            )
            write_line("", fh)

        write_line("", fh)

    write_line("=" * 80, fh)
    write_line("DOKUMENTACE VÝPOČTU EMPIRIC NULL BASELINE PRO acc_eq", fh)
    write_line("=" * 80, fh)
    write_line("", fh)
    write_line("Likertova škála: 1 až 7", fh)
    write_line(
        "Pro každý blok (locale, criterion) se nejprve spočte empirická distribuce "
        "human score hodnot z celého bloku.", fh
    )
    write_line(
        "To je 46 promptů × 16 systémů = 736 hodnot pro každé locale x criterion.", fh
    )
    write_line("", fh)
    write_line(
        "Potom se pro každý konkrétní 16-dimenzionální human vektor "
        "(original_instance_id uvnitř daného locale x criterion) simuluje random judge:", fh
    )
    write_line(
        "- každá ze 16 hodnot random judge se losuje nezávisle z empirické distribuce "
        "příslušného locale x criterion,", fh
    )
    write_line(
        f"- počet simulací pro každý vektor: {n_simulations}", fh
    )
    write_line(
        f"- simulace se provádí po blocích velikosti chunk_size={chunk_size}", fh
    )
    write_line("", fh)
    write_line(
        "Pro každý simulovaný 16-vektor se spočte acc_eq vůči danému human vektoru, "
        "a jejich průměr je expected_random_acc_eq.", fh
    )
    write_line("", fh)

    write_line("=" * 80, fh)
    write_line("EMPIRICKÉ DISTRIBUCE PO LOCALE × CRITERION", fh)
    write_line("=" * 80, fh)
    write_line("", fh)

    for (locale, criterion) in sorted(locale_criterion_to_baselines.keys()):
        dist_info = locale_criterion_to_distribution[(locale, criterion)]
        counts = dist_info["counts"]
        probs = dist_info["probs"]

        write_line(
            f"locale={locale}, criterion={criterion}, n_scores={dist_info['n_scores']}, "
            f"counts={counts.tolist()}, probs={[round(p, 6) for p in probs.tolist()]}",
            fh
        )

    write_line("", fh)
    write_line("=" * 80, fh)
    write_line("EMPIRIC NULL BASELINE PO LOCALE × CRITERION", fh)
    write_line("=" * 80, fh)
    write_line("", fh)

    for (locale, criterion) in sorted(locale_criterion_to_baselines.keys()):
        vals = locale_criterion_to_baselines[(locale, criterion)]
        avg_val = sum(vals) / len(vals)
        write_line(
            f"locale={locale}, criterion={criterion}, "
            f"n_vectors={len(vals)}, expected_random_acc_eq_mean={avg_val:.6f}",
            fh
        )

    write_line("", fh)
    write_line("=" * 80, fh)
    write_line("EMPIRIC NULL BASELINE PO LOCALE", fh)
    write_line("=" * 80, fh)
    write_line("", fh)

    for locale in sorted(locale_to_baselines.keys()):
        vals = locale_to_baselines[locale]
        avg_val = sum(vals) / len(vals)
        write_line(
            f"locale={locale}, "
            f"n_vectors={len(vals)}, "
            f"expected_random_acc_eq_mean={avg_val:.6f}",
            fh
        )

    write_line("", fh)
    write_line("=" * 80, fh)
    write_line("GLOBÁLNÍ SHRNUTÍ", fh)
    write_line("=" * 80, fh)

    all_baselines = [r["expected_random_acc_eq"] for r in vectors]
    write_line(f"Počet všech vektorů: {len(vectors)}", fh)
    write_line(f"Minimum vector baseline: {min(all_baselines):.6f}", fh)
    write_line(f"Maximum vector baseline: {max(all_baselines):.6f}", fh)
    write_line(
        f"Průměrný baseline přes všechny vektory: {sum(all_baselines) / len(all_baselines):.6f}",
        fh
    )

print(f"[INFO] Hotovo. Výsledky zapsány do: {output_file}")