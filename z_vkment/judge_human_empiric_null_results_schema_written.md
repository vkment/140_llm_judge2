# Struktura výstupního JSON

## Root keys

- `metadata` — informace o vstupních souborech a nastavení programu
- `warnings` — případná upozornění
- `judge_models` — seznam všech zpracovaných `judge_model_name`
- `legacy_metrics` — historické metriky kompatibilní s dřívějším vyhodnocením
- `empiric_null_overall` — agregace přes všechny instance
- `empiric_null_by_criterion` — agregace po criterion
- `empiric_null_by_locale` — agregace po locale
- `empiric_null_by_locale_and_criterion` — agregace po locale x criterion
- `instance_level_details` — volitelně detailní záznamy po jednotlivých instancích

## legacy_metrics

Obsahuje:
- `ranking_accuracy`
- `acc_eq_average`
- `acc_eq_by_criterion`

## Agregační záznam

Každý agregační záznam obsahuje:
- `n_instances`
- `mean_acc_eq`
- `mean_percentile`
- `mean_centered_skill`
- `std_centered_skill`
- `median_centered_skill`
- `n_above_chance`
- `n_below_chance`
- `n_equal_chance`

## instance_level_details

Každý detailní záznam obsahuje:
- `judge_model_name`
- `locale`
- `criterion`
- `original_instance_id`
- `acc_eq`
- `acc_eq_index`
- `percentile`
- `percentile_percent`
- `centered_skill`
- `centered_skill_percent`

## Interpretace nových metrik

### percentile
Mid-percentil v nulovém rozdělení pro daný konkrétní human vektor:
`P(X < x) + 0.5 * P(X = x)`

### centered_skill
Přemapování percentilu na škálu s nulou pro náhodu:
`2 * percentile - 1`

- `0` = náhoda
- `+1` = maximálně vysoko nad náhodou
- `-1` = horší než náhoda
