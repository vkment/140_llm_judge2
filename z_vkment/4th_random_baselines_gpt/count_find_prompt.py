import csv

# ====== soubory ======
file_run2 = "oeg_judge_run2_submission_data.csv"
file_human = "oeg_human_eval_data.csv"

# ====== název společného sloupce ======
id_column = "original_instance_id"

# ====== množiny ======
run2_ids = set()
human_ids = set()

# ====== načtení run2 ======
with open(file_run2, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        run2_ids.add(row[id_column])

# ====== načtení human ======
with open(file_human, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        human_ids.add(row[id_column])

# ====== rozdíly ======
only_in_run2 = run2_ids - human_ids
only_in_human = human_ids - run2_ids

# ====== výstup ======
print(f"Počet unikátních ID v {file_run2}: {len(run2_ids)}")
print(f"Počet unikátních ID v {file_human}: {len(human_ids)}")

print("\n=== ID navíc v run2 (chybí v human) ===")
if only_in_run2:
    for x in sorted(only_in_run2):
        print(x)
else:
    print("Žádné")

print("\n=== ID navíc v human (chybí v run2) ===")
if only_in_human:
    for x in sorted(only_in_human):
        print(x)
else:
    print("Žádné")