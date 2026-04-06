import numpy as np
import pandas as pd
from itertools import combinations
import json
from collections import defaultdict

# =========================================================
# KONFIGURACE
# =========================================================
input_file = "oeg_human_eval_data.csv"
output_json = "z_vkment/calculate_random_empiric_null_distributions.json"
#output_md = "z_vkment/calculate_random_empiric_null_distributions.md"

n_simulations = 1_000_000
chunk_size = 5000
random_seed = 42

# =========================================================
# POMOCNÉ FUNKCE
# =========================================================
def get_pair_indices(n):
    pair_i, pair_j = [], []
    for i, j in combinations(range(n), 2):
        pair_i.append(i)
        pair_j.append(j)
    return np.array(pair_i), np.array(pair_j)


def get_relations(scores, pair_i, pair_j):
    diff = scores[pair_i] - scores[pair_j]
    return np.sign(diff).astype(np.int8)


def empirical_distribution(scores):
    counts = np.zeros(7, dtype=int)
    for s in scores:
        counts[int(round(s)) - 1] += 1
    probs = counts / counts.sum()
    return counts.tolist(), probs.tolist()


def simulate_distribution(human_scores, probs, rng):
    n = len(human_scores)
    pair_i, pair_j = get_pair_indices(n)
    human_rel = get_relations(np.array(human_scores), pair_i, pair_j)

    histogram = np.zeros(121, dtype=np.int64)

    sims_done = 0
    values = np.arange(1, 8)

    while sims_done < n_simulations:
        current_chunk = min(chunk_size, n_simulations - sims_done)

        rand = rng.choice(values, size=(current_chunk, n), p=probs)
        rand_rel = np.sign(rand[:, pair_i] - rand[:, pair_j]).astype(np.int8)

        matches = (rand_rel == human_rel).sum(axis=1)
        histogram += np.bincount(matches, minlength=121)

        sims_done += current_chunk

    return histogram


def summarize_histogram(hist):
    probs = hist / hist.sum()
    values = np.arange(121) / 120.0

    mean = float((values * probs).sum())
    std = float(np.sqrt(((values - mean) ** 2 * probs).sum()))

    return {
        "mean": mean,
        "std": std,
        "min": float(values[np.where(hist > 0)[0][0]]),
        "max": float(values[np.where(hist > 0)[0][-1]])
    }


# =========================================================
# MAIN
# =========================================================
print("[INFO] Loading data...")
df = pd.read_csv(input_file)

assert (df["judge_model_name"] == "human").all()

df["score"] = df["score"].astype(float)

# =========================================================
# EMPIRICKÉ DISTRIBUCE
# =========================================================
print("[INFO] Computing empirical distributions...")
empirical = {}

for (locale, criterion), g in df.groupby(["locale", "criterion"]):
    counts, probs = empirical_distribution(g["score"].tolist())

    empirical[(locale, criterion)] = {
        "locale": locale,
        "criterion": criterion,
        "values": [1,2,3,4,5,6,7],
        "counts": counts,
        "probs": probs,
        "n_scores": len(g)
    }

# =========================================================
# VEKTORY
# =========================================================
print("[INFO] Building vectors...")
vectors = []

group_cols = ["locale", "criterion", "original_instance_id"]

for (locale, criterion, oid), g in df.groupby(group_cols):
    g = g.sort_values("submission_system_name")

    systems = g["submission_system_name"].tolist()
    scores = g["score"].tolist()

    assert len(systems) == 16

    vectors.append({
        "locale": locale,
        "criterion": criterion,
        "original_instance_id": oid,
        "systems": systems,
        "scores": scores
    })

print(f"[INFO] Total vectors: {len(vectors)}")

# =========================================================
# SIMULACE
# =========================================================
rng = np.random.default_rng(random_seed)

results = []

for i, v in enumerate(vectors, 1):
    locale = v["locale"]
    criterion = v["criterion"]
    probs = empirical[(locale, criterion)]["probs"]

    print(f"[INFO] {i}/{len(vectors)} | {locale} | {criterion} | {v['original_instance_id']}")

    hist = simulate_distribution(v["scores"], probs, rng)
    summary = summarize_histogram(hist)

    results.append({
        "locale": locale,
        "criterion": criterion,
        "original_instance_id": v["original_instance_id"],
        "n_systems": 16,
        "n_pairs": 120,
        "n_simulations": n_simulations,
        "systems_order": v["systems"],
        "human_scores": v["scores"],
        "acc_eq_grid": [k/120.0 for k in range(121)],
        "pmf_counts": hist.tolist(),
        "pmf_probs": (hist / hist.sum()).tolist(),
        "summary": summary
    })

# =========================================================
# ULOŽENÍ
# =========================================================
print("[INFO] Saving JSON...")

output = {
    "metadata": {
        "n_simulations": n_simulations,
        "chunk_size": chunk_size,
        "random_seed": random_seed,
        "note": "empiric null distributions per vector"
    },
    "empirical_distributions": list(empirical.values()),
    "vectors": results
}

with open(output_json, "w", encoding="utf-8") as f:
    json.dump(output, f, indent=2)

print("[INFO] Done.")