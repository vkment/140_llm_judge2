import csv
import os

# ====== vstupy ======
input_dir = "oeg_human_eval_raw_data"
target_doc_id = "41195c6e58c3dc54bd51d9462c2a1a35"

# ====== počítání ======
total_count = 0
file_counts = {}

for filename in os.listdir(input_dir):
    if filename.endswith(".csv"):
        filepath = os.path.join(input_dir, filename)
        count = 0
        
        with open(filepath, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["doc_id"] == target_doc_id:
                    count += 1
        
        file_counts[filename] = count
        total_count += count

# ====== výstup ======
print(f"Hledané doc_id: {target_doc_id}\n")

print("Počty po souborech:")
for fname, cnt in sorted(file_counts.items()):
    print(f"{fname}: {cnt}")

print(f"\nCelkový počet výskytů: {total_count}")