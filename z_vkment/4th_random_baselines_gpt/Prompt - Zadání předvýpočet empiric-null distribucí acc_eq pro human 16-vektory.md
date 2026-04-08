# Prompt - Zadání: předvýpočet empiric-null distribucí `acc_eq` pro human 16-vektory

https://chatgpt.com/c/69d39288-4b08-8392-b268-5d15eb1195d3

Vytvoř program, který z input souboru `oeg_human_eval_data.csv` předpočítá nulové distribuce metriky `acc_eq` pro všechny human vektory délky 16, a výsledky uloží do JSON souboru. Součástí dodávky má být i stručná, ale dostatečná dokumentace programu a formátu výstupu.

## Účel

Cílem programu není ještě počítat percentily, p-value ani žádné finální judge-scores.
Cílem je pouze:

1. zjistit empirické distribuce human score na škále 1–7 pro každý blok `locale × criterion`,
2. pro každý konkrétní human vektor `(locale, criterion, original_instance_id)` délky 16 nasimulovat nulové rozdělení `acc_eq`,
3. uložit tyto předpočítané distribuce a jejich četnosti do výstupního JSON tak, aby byly později použitelné dalším softwarem.

## Vstup

Vstupní soubor bude uveden zcela nahoře programu jako proměnná, např.:

```python
input_file = "oeg_human_eval_data.csv"
```

Soubor má strukturu:

- `judge_model_name`
- `criterion`
- `submission_system_name`
- `original_instance_id`
- `locale`
- `score`

Předpokládá se, že:

- `judge_model_name` je všude `human`,
- pro každé `(locale, criterion, original_instance_id)` existuje právě 16 řádků, po jednom pro každý `submission_system_name`,
- `score` je na Likertově škále `1..7`.

Program má obsahovat kontroly konzistence vstupu a při chybě vypsat srozumitelné hlášení.

## Null model

Použij se **empiric null** definovaný takto:

- pro každý blok `locale × criterion` vezmi všech 46 × 16 = 736 human score hodnot,
- z těchto hodnot spočti empirickou diskrétní distribuci na škále `1..7`,
- při simulaci náhodného judge pro konkrétní human vektor délky 16 losuj každou jeho složku i.i.d. z této empirické distribuce příslušného `locale × criterion`.

Nepoužívej uniformní rozdělení `1..7`.

## Co přesně simulovat

Pro každý konkrétní human vektor definovaný trojicí:

- `locale`
- `criterion`
- `original_instance_id`

seřaď 16 složek podle `submission_system_name`, aby bylo pořadí deterministické.

Pak pro tento fixní human vektor:

- proveď velký počet simulací, např. `1_000_000`,
- v každé simulaci vytvoř náhodný 16-vektor dle empirické distribuce daného `locale × criterion`,
- spočti `acc_eq` mezi tímto náhodným vektorem a fixním human vektorem.

## Definice `acc_eq`

Použij stejnou definici jako dosud:

- relace na každém páru systémů je `<`, `>`, nebo `=`,
- `acc_eq` je podíl párů, kde se relace human a simulated-random judge shoduje.

Pro 16 systémů je počet párů:
$$
\binom{16}{2} = 120
$$
Z toho plyne, že `acc_eq` nabývá jen hodnot:
$$
0/120, 1/120, 2/120, ..., 120/120
$$
tedy 121 možných hodnot.

Program nemá ukládat všechny simulace zvlášť, ale má pro každý vektor uložit histogram těchto 121 hodnot.

## Co uložit do výstupního JSON

Výstupní JSON má obsahovat dvě hlavní části.

### 1. Empirické distribuce pro `locale × criterion`

Pro každý blok `locale × criterion` uložit:

- `locale`
- `criterion`
- `values`: `[1,2,3,4,5,6,7]`
- `counts`: četnosti pro 1..7
- `probs`: pravděpodobnosti pro 1..7
- `n_scores`: počet použitých score, očekávaně 736

### 2. Nulové distribuce `acc_eq` pro jednotlivé vektory

Pro každý vektor `(locale, criterion, original_instance_id)` uložit:

- `locale`
- `criterion`
- `original_instance_id`
- `n_systems` = 16
- `n_pairs` = 120
- `n_simulations`
- `systems_order`: seznam 16 `submission_system_name` v použitém pořadí
- `human_scores`: odpovídající human score v tomto pořadí
- `acc_eq_grid`: seznam 121 hodnot od `0/120` do `120/120`
- `pmf_counts`: seznam 121 četností, kolikrát která hodnota `acc_eq` nastala v simulaci
- `pmf_probs`: seznam 121 pravděpodobností, tj. `pmf_counts / n_simulations`

Dále je vhodné uložit i několik souhrnných statistik, minimálně:

- `mean_acc_eq`
- `std_acc_eq`
- `min_acc_eq`
- `max_acc_eq`

## Formát výstupu

Názvy output souborů budou zcela nahoře programu jako proměnné, např.:

```python
output_json = "calculate_random_empiric_null_distributions.json"
output_md = "calculate_random_empiric_null_distributions.md"
```

JSON má být strojově dobře čitelný a zároveň rozumně auditovatelný člověkem.

## Progres a logování

Program má při běhu vypisovat průběžná hlášení na terminál, aby bylo vidět, že se nezacyklil.

Například:

- načtení vstupu,
- zjišťování empirických distribucí,
- počet nalezených vektorů,
- začátek simulace pro každý `locale × criterion`,
- průběh po jednotlivých vektorech,
- dokončení a zápis výstupu.

Tato progress hlášení nemusejí být součástí JSON.

## Výkon a implementace

Použij takovou implementaci, aby byl výpočet rozumně rychlý i pro `1_000_000` simulací na vektor.

Doporučeno:

- NumPy,
- zpracování po chunky,
- žádné ukládání všech simulovaných vektorů do paměti naráz.

Dbej na reprodukovatelnost:

- seed random generátoru má být explicitně nastaven z proměnné na začátku programu.

## Dokumentace

Spolu s programem vytvoř i stručnou dokumentaci.

### Dokumentace programu

Popiš:

- co program dělá,
- jaký je vstup,
- co je empiric null,
- jak se simuluje,
- co je ve výstupu.

### Dokumentace výstupního JSON

Pokud nebude dostatečně přehledná přímo struktura JSON, vytvoř doprovodný `.md` soubor, který vysvětlí:

- strukturu JSON,
- význam jednotlivých polí,
- jak interpretovat `pmf_counts`, `pmf_probs`, `acc_eq_grid`,
- že jde o předpočítané nulové distribuce pro další software.

## Požadovaný výsledek

Výstupem má být:

- Python program pro předvýpočet distribucí,
- JSON soubor s výsledky,
- stručná dokumentace programu,
- stručná dokumentace výstupního JSON.

## Poznámka k interpretaci

Neřeš zatím:

- percentily,
- p-value,
- skill score,
- srovnání judge modelů.

Tento software má pouze připravit podkladová nulová rozdělení `acc_eq` a empirické score distribuce.

Jestli chceš, v dalším kroku to můžu ještě přepsat do stručnější „specifikace pro implementaci“, bez vysvětlujících odstavců.