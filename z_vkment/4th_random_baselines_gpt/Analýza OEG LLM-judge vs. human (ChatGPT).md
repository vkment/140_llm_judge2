# Analýza OEG LLM-judge vs. human (ChatGPT)

https://chatgpt.com/c/69d24286-a410-838f-ab2f-2ce7e0329d4d

Ano. Tady je kompaktní zadání, které by mělo stačit i v jiném vlákně.

Napiš v Pythonu samostatný skript `oeg_acc_eq_by_judge_46prompt_stats.py`, který analyzuje OEG judge-vs-human agreement nad dvěma CSV soubory:

- `oeg_human_eval_data.csv`
- `oeg_judge_run2_submission_data.csv`

Oba vstupní soubory musí být definovány úplně nahoře v kódu jako konfigurovatelné cesty. Stejně tak nahoře definuj i případné filtry:

- `FILTER_LOCALES = None | list[str]`
- `FILTER_CRITERIA = None | list[str]`
- `FILTER_JUDGE_MODELS = None | list[str]`

Použij tuto metodiku:

1. Oba CSV obsahují sloupce:

   - `judge_model_name`
   - `criterion`
   - `submission_system_name`
   - `original_instance_id`
   - `locale`
   - `score`

2. V human CSV je `judge_model_name = human`.
   V judge CSV jsou různé LLM-judge modely.

3. Nejprve vytvoř unikátní klíč instance:

   - `instance_key = original_instance_id + "_with_" + locale`

4. Zarovnej obě tabulky tak, aby se počítalo jen na společném průniku podle:

   - `submission_system_name`
   - `criterion`
   - `instance_key`

5. Pro každý:

   - `judge_model_name`
   - `criterion`
   - `locale`
   - `instance_key`

   udělej toto:

   - vyber z human dat 16 řádků odpovídajících 16 `submission_system_name`
   - vyber z judge dat odpovídajících 16 řádků
   - obě množiny seřaď podle `submission_system_name`, aby pořadí systémů bylo totožné
   - tím vzniknou dva 16-dimenzionální vektory:
     - `scores_human`
     - `scores_judge`

6. Z těchto dvou vektorů spočti jednu hodnotu `acc_eq` podle metodiky Deutsch/Kocmi, tj. přes všechny neuspořádané dvojice systémů `(i, j)` z 16 systémů:

   - `C` = concordant pairs
   - `D` = discordant pairs
   - `T_h` = tie pouze u human
   - `T_m` = tie pouze u judge
   - `T_hm` = tie u obou

   Vzorec:

   - `acc_eq = (C + T_hm) / (C + D + T_h + T_m + T_hm)`

   Tj. pro každý fixní `judge_model_name × criterion × locale × prompt(instance)` vznikne právě jedna hodnota `acc_eq`.

7. Tímto způsobem pro každý fixní:

   - `judge_model_name`
   - `criterion`
   - `locale`

   získáš 46 hodnot `acc_eq` (jednu pro každý prompt).

8. Z těchto 46 hodnot pro každého judge-modelu, jazyk a kritérium spočti souhrnné statistiky:

   - `n_prompts`
   - `mean`
   - `std` (sample standard deviation, tj. `ddof=1`)
   - `se`
   - `cv = std / mean`
   - `min`
   - `q10`
   - `q25`
   - `median`
   - `q75`
   - `q90`
   - `max`
   - `iqr`
   - `range`

9. Ulož dva výstupy:

   - `oeg_acc_eq_prompt_level_by_judge.csv`
     - jedna řádka = `judge_model_name × criterion × locale × instance_key`
     - obsahuje prompt-level `acc_eq`
   - `oeg_acc_eq_summary_46prompts_by_judge.csv`
     - jedna řádka = `judge_model_name × criterion × locale`
     - obsahuje statistiky přes 46 promptových hodnot

10. Navíc ulož i JSON souhrn:

- `oeg_acc_eq_summary_46prompts_by_judge.json`

1. Kód napiš čistě, přehledně, s komentáři, bez zbytečných závislostí mimo `pandas` a `numpy`.
2. Do výstupu na konzoli vypiš:

- počty načtených a zarovnaných řádků
- počet prompt-level řádků
- cestu k uloženým souborům
- preview prvních řádků summary tabulky

#### Poznámka k interpretaci:

Po výpočtu je rozumné interpretovat každého LLM-judge podle tří hlavních ukazatelů:

- `mean acc_eq` = průměrná shoda s lidským hodnocením
- `std` = stabilita napříč 46 prompty
- `CV` = relativní variabilita vzhledem k průměru

Prakticky:

- vysoké `mean` je dobré
- nízké `std` je dobré
- nízké `CV` je dobré

Tedy dobrý LLM-judge není jen ten, který má vysoký průměr, ale i ten, který je stabilní napříč prompty.

Můžu ti to také přepsat do kratší „produkční“ verze jako čistý prompt bez číslovaných bodů.

---

Vs. co jsem původně chtěl:

Správně jsem měl zadat takto: " Já ale chtěl abys pro každý locale × criterion dělal cyklus přes prompt, v rámci každého nasbíráš 16 odpovědí generovaných nějakými LLM-generátor systémy, pro ně (prompt, criterion, response) zjistíš hodnocení od jednoho LLM-judge, tento vektor 16 hodnocení daného LLM-judge srovnáš s gold lidskými hodnoceními a získáš pro daný locale x criterion (a daný LLM-judge) právě jednu hodnotu acc_eq. Jak budeš procházet dalšími prompty, postupně získáš pro stejného LLM-judge 46 hodnot acc_eq, (platné pro locale x criterion + zvoleného LLM-judge), a jejich statistické hodnoty chci znát, z těchto 46 hodnot, pro každého zvoleného LLM-judge. Následně zvolíš dalšího možného LLM-judge, projdeš jimi všemi. " 



Sorry za zmatky, dává Ti toto smysl? Výsledkem by mělo být, že pro každého LLM-judge (pro každé locale x criterion) bude nejen střední hodnota vůči němu provedených acc_eq, ale i statistické vlastnosti. Dává toto smysl?