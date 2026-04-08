

# Prompt - Zadání: vyhodnocení LLM-judge proti human s využitím předpočítaných empiric-null distribucí `acc_eq` 

https://chatgpt.com/c/69d39288-4b08-8392-b268-5d15eb1195d3

Vytvoř program, který vyhodnotí jeden nebo více vstupních CSV souborů s výsledky LLM-judge hodnocení ve formátu jako `oeg_judge_run2_submission_data.csv` a porovná je proti human hodnocení pomocí metriky `acc_eq`, nově rozšířené o kalibraci vůči předpočítaným empiric-null distribucím uloženým v `z_vkment/calculate_random_empiric_null_distributions.json`.

Program má navázat na dosavadní logiku v `judge_human_agreement.py` a `corr_utils.py`, kde se `acc_eq` počítá po jednotlivých instancích jako shoda relací mezi 16 systémy pro stejnou kombinaci `criterion × original_instance_id × locale`, seřazených podle `submission_system_name`.

## Účel

Cílem programu je pro každého `judge_model_name` spočítat:

- původní `acc_eq`,
- percentil vzhledem k empiric-null distribuci,
- mean centered skill,
- standard deviation centered skill,
- median centered skill,
- počet promptů nad náhodou,
- počet promptů pod náhodou.

To vše:

- celkově,
- po `criterion`,
- po `locale`,
- a po `locale × criterion`.

Program nemá počítat nové null distribuce. Ty jsou již předpočítané v JSON souboru.

## Vstupy

Na začátku programu budou explicitně uvedeny vstupní soubory, např.:

```python
judge_input_files = [
    "oeg_judge_run2_submission_data.csv",
]
human_input_file = "oeg_human_eval_data.csv"
null_distributions_file = "z_vkment/calculate_random_empiric_null_distributions.json"
```

Je třeba umožnit i více souborů LLM-judge dat, které se spojí do jedné tabulky.

### Formát judge CSV

Každý řádek obsahuje:

- `judge_model_name`
- `criterion`
- `submission_system_name`
- `original_instance_id`
- `locale`
- `score`

### Formát human CSV

Stejná struktura jako dosud:

- `judge_model_name`
- `criterion`
- `submission_system_name`
- `original_instance_id`
- `locale`
- `score`

Human data mají `judge_model_name = "human"`.

### Formát null JSON

Použij předpočítané distribuce z `calculate_random_empiric_null_distributions.json`, zejména část `vectors`, kde je pro každý `(locale, criterion, original_instance_id)` k dispozici:

- `acc_eq_grid`
- `pmf_counts`
- `pmf_probs`

Tento JSON byl vytvořen zvlášť a definuje empiric-null distribuci `acc_eq` pro každý konkrétní human vektor.

## Předzpracování a filtrování

Stejně jako v dosavadním `judge_human_agreement.py` je nutné nejprve zajistit, aby judge i human data byly porovnávány jen na společném průniku instancí. Dosud se to dělalo filtrováním podle:

- `submission_system_name`
- `criterion`
- `original_instance_id_with_locale`

kde `original_instance_id_with_locale = original_instance_id + "_with_" + locale`.

Nový program má postupovat analogicky.

Navíc musí ověřit, že pro každou porovnávanou instanci existuje odpovídající záznam v null JSON.

Pokud některá instance nemá odpovídající nulové rozdělení, program má:

- buď ji přeskočit a zapsat warning,
- nebo skončit s chybou,
  podle explicitního nastavení na začátku programu.

## Jednotka vyhodnocení

Základní jednotka vyhodnocení je jeden vektor definovaný trojicí:

- `locale`
- `criterion`
- `original_instance_id`

Pro tuto jednotku:

- vyber 16 řádků human,
- vyber 16 řádků daného `judge_model_name`,
- seřaď obě sady podle `submission_system_name`,
- získej dva 16-prvkové vektory skóre,
- spočti `acc_eq` přes stejnou funkci/logiku jako dosud. `acc_eq` je definováno jako ((C + T_{hm}) / (C + D + T_h + T_m + T_{hm})).

## Nové metriky vůči empiric null

Pro každou jednotlivou instanci `(locale, criterion, original_instance_id)` a pro každý `judge_model_name`:

1. Spočti pozorované `acc_eq`.
2. Převeď je na index:
   [
   k = \text{round}(120 \cdot acc_eq)
   ]
   protože `acc_eq` leží na mřížce `0/120, 1/120, ..., 120/120`.
3. V příslušném null rozdělení pro tento vektor vezmi `pmf_probs[k]`.
4. Z `pmf_probs` spočti kumulativní distribuci `cdf`.
5. Definuj percentil jako mid-percentil:
   [
   percentile = P(X < x) + 0.5 \cdot P(X = x)
   ]
   tj.
   [
   percentile_k = cdf[k-1] + 0.5 \cdot pmf_probs[k]
   ]
   s tím, že pro `k=0` je první člen nula.

Tento percentil bude uložen jak v rozsahu `0..1`, tak případně i v procentech `0..100`.

### Centered skill

Pro každou instanci dále spočti:

[
centered_skill = 2 \cdot percentile - 1
]

tedy:

- `0` = úroveň náhody,
- `> 0` = lepší než náhoda,
- `< 0` = horší než náhoda.

Program má ukládat centered skill jak v rozsahu `-1..1`, tak případně i v procentech `-100..100`.

## Agregace přes 46 promptů

Pro každého `judge_model_name` a každou sledovanou skupinu agregace spočti přes jednotlivé instance:

- `mean_acc_eq`
- `mean_percentile`
- `mean_centered_skill`
- `std_centered_skill`
- `median_centered_skill`
- `n_instances`
- `n_above_chance` = počet instancí s `centered_skill > 0`
- `n_below_chance` = počet instancí s `centered_skill < 0`
- `n_equal_chance` = počet instancí s `centered_skill == 0` nebo numericky velmi blízko nule podle tolerance

Agregace mají být minimálně pro:

1. **overall** — přes všechny instance daného judge
2. **by_criterion**
3. **by_locale**
4. **by_locale_and_criterion**

## Zachování dosavadních metrik

Program má kromě nové metodiky stále spočítat i původní metriky používané v `judge_human_agreement.py`, alespoň:

- `ranking_accuracy` = system-level pairwise accuracy bez ties, přes průměrná skóre systémů napříč datasetem, stejně jako dosud přes `my_pairwise_acc`.
- původní průměrné `acc_eq` po `criterion`
- původní průměrné `acc_eq` overall

Je vhodné tyto metriky reportovat vedle nových, aby bylo možné výsledky porovnat s historickými JSON výstupy typu `oeg_judge_human_agreement_results.json`.

## Výstupy

Na začátku programu budou explicitně uvedeny výstupní soubory, např.:

```python
output_json = "judge_human_empiric_null_results.json"
output_md = "judge_human_empiric_null_results.md"
```

### Výstupní JSON

Výstupní JSON má obsahovat minimálně:

- metadata o vstupních souborech,
- seznam zpracovaných `judge_model_name`,
- případná warning hlášení o přeskočených instancích,
- tradiční metriky (`ranking_accuracy`, `acc_eq_average`, `acc_eq_by_criterion`, případně další),
- nové agregace:
  - `empiric_null_overall`
  - `empiric_null_by_criterion`
  - `empiric_null_by_locale`
  - `empiric_null_by_locale_and_criterion`

Každý agregovaný záznam má obsahovat výše uvedené statistiky.

### Volitelně detailní instance-level výstup

Je vhodné umožnit přepínačem na začátku programu, zda se do JSON uloží i detailní řádky pro každou jednotlivou instanci:

- `judge_model_name`
- `locale`
- `criterion`
- `original_instance_id`
- `acc_eq`
- `percentile`
- `centered_skill`

To může být užitečné pro další analýzu, ale může to zvětšit JSON.

## Progress hlášení

Program má vypisovat průběžná hlášení na terminál, aby bylo vidět, co dělá, například:

- načítání judge dat,
- načítání human dat,
- načítání null JSON,
- filtrování na průnik,
- počet judge modelů,
- zpracování jednotlivých judge modelů,
- zpracování jednotlivých bloků `locale × criterion`,
- dokončení zápisu.

Tato hlášení nemusejí být součástí výstupního JSON.

## Kontroly konzistence

Program má obsahovat kontroly:

- že pro každou porovnávanou instanci je přesně 16 systémů u human i judge,
- že množiny `submission_system_name` souhlasí mezi human a judge,
- že `acc_eq` skutečně padá na mřížku `k/120`,
- že null JSON obsahuje odpovídající vektor pro každou porovnávanou instanci,
- že `pmf_probs` dávají součet 1 s rozumnou numerickou tolerancí.

Při chybě má program vypsat srozumitelné chybové hlášení.

## Dokumentace

Součástí dodávky má být i stručná dokumentace programu a výstupního JSON.

### Dokumentace programu

Má vysvětlit:

- co program dělá,
- jaké vstupy očekává,
- jak se počítá `acc_eq`,
- jak se z null rozdělení počítá percentil,
- jak se definuje centered skill,
- jaké agregace program vytváří.

### Dokumentace výstupního JSON

Má vysvětlit:

- strukturu JSON,
- význam jednotlivých polí,
- rozdíl mezi tradičními a novými metrikami,
- interpretaci `percentile` a `centered_skill`.

## Poznámky k metodice

Tento program má používat:

- **empiric-null distribuci po jednotlivých vektorech**, již předpočítanou,
- nikoli jen průměrný baseline po `locale` nebo `locale × criterion`.

Důvod je, že tvar nulového rozdělení `acc_eq` závisí nejen na `locale × criterion`, ale i na konkrétním human vektoru, zejména na struktuře ties a ordered párů.

Program zatím nemá řešit:

- jiné transformace skill na čisté `0–100`,
- p-value,
- confidence intervals,
- inferenční statistiku mezi judge modely.

Teď jde čistě o výpočet a agregaci:

- `acc_eq`
- `percentile`
- `centered skill`

## Požadovaný výsledek

Výstupem má být:

- Python program,
- JSON s výsledky,
- doprovodná dokumentace programu,
- doprovodná dokumentace výstupního JSON.

Jestli chceš, v dalším kroku to můžu zkrátit do tvrdé implementační specifikace bod po bodu, bez vysvětlovacích pasáží.