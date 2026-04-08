import csv
from collections import Counter

# ====== soubory ======
input_file = "oeg_human_eval_data.csv"
output_file = "z_vkment/all_column_counts_from_human.csv"

# ====== sloupce ======
columns = [
    "judge_model_name",
    "criterion",
    "submission_system_name",
    "original_instance_id",
    "locale",
    "score"
]

# ====== struktura ======
counters = {col: Counter() for col in columns}

# ====== načtení a počítání ======
with open(input_file, newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        for col in columns:
            counters[col][row[col]] += 1

# ====== zápis do jednoho souboru ======
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