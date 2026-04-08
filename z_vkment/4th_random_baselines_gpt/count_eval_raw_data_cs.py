import csv
from collections import Counter

# ====== soubory ======
input_file = "oeg_human_eval_raw_data/data_cs_CZ.csv"
output_file = "z_vkment/human_eval_counts_cs_CZ.csv"

# ====== sledované sloupce ======
columns = [
    "system",
    "doc_id",
    "language_locale",
    "rater"
]

# ====== struktura ======
counters = {col: Counter() for col in columns}

# ====== načtení a počítání ======
with open(input_file, newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        for col in columns:
            counters[col][row[col]] += 1

# ====== zápis ======
with open(output_file, "w", newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(["column_name", "value", "count"])
    
    for col in columns:
        for value, count in counters[col].items():
            writer.writerow([col, value, count])

# ====== tisk ======
print("column_name,value,count")
for col in columns:
    for value, count in counters[col].items():
        print(f"{col},{value},{count}")