# Struktura JSON

## metadata
Globální informace o simulaci

## empirical_distributions
Distribuce skóre pro každý locale × criterion

- values: [1..7]
- counts: četnosti
- probs: pravděpodobnosti

## vectors
Každý záznam odpovídá jednomu promptu

Obsahuje:

- locale
- criterion
- original_instance_id
- systems_order
- human_scores

### acc_eq_grid
121 hodnot od 0 do 1 (kroky 1/120)

### pmf_counts
četnosti pro každou hodnotu acc_eq

### pmf_probs
pravděpodobnosti

### summary
- mean
- std
- min
- max

## Interpretace

pmf představuje nulové rozdělení:
"jak by dopadl náhodný judge v daném locale × criterion"