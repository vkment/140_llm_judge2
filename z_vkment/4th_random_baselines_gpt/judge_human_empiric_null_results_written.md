# Program: judge_human_empiric_null_eval.py

## Účel

Program vyhodnocuje LLM-judge proti human hodnocení.

Vedle původního `acc_eq` a `ranking_accuracy` počítá i nové metriky kalibrované vůči předpočítaným empiric-null distribucím z `z_vkment/calculate_random_empiric_null_distributions.json`.

## Vstupy

- judge CSV soubory: `['oeg_judge_run2_submission_data.csv']`
- human CSV soubor: `oeg_human_eval_data.csv`
- JSON s per-vector null distribucemi: `z_vkment/calculate_random_empiric_null_distributions.json`

## Jednotka vyhodnocení

Jedna instance je určena trojicí:
- `locale`
- `criterion`
- `original_instance_id`

Pro každou instanci se vezme 16 systémů (`submission_system_name`), human i judge skóre se seřadí podle `submission_system_name` a spočte se `acc_eq`.

## Nové metriky

Pro každé pozorované `acc_eq` se podle per-vector PMF spočte:

- `percentile = P(X < x) + 0.5 * P(X = x)`
- `centered_skill = 2 * percentile - 1`

Interpretace:
- `percentile ~= 0.5` znamená úroveň náhody
- `centered_skill = 0` znamená úroveň náhody
- `centered_skill > 0` znamená lepší než náhoda
- `centered_skill < 0` znamená horší než náhoda

## Agregace

Program vytváří agregace:
- overall
- by criterion
- by locale
- by locale x criterion

Pro každou agregaci ukládá:
- `mean_acc_eq`
- `mean_percentile`
- `mean_centered_skill`
- `std_centered_skill`
- `median_centered_skill`
- `n_above_chance`
- `n_below_chance`
- `n_equal_chance`

## Poznámka

Program sám nepřepočítává null distribuce. Pouze čte již předpočítané JSON rozdělení a používá jej jako lookup tabulku pro převod `acc_eq -> percentile -> centered_skill`.
