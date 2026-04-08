# Program: calculate_random_empiric_null_distributions.py

## Účel

Program předpočítá nulové distribuce metriky acc_eq pro human hodnocení.

Používá tzv. empiric null model:
- náhodný judge losuje skóre 1–7 podle empirické distribuce daného locale × criterion.

## Vstup

CSV:
oeg_human_eval_data.csv

Obsahuje human hodnocení pro:
- locale
- criterion
- prompt (original_instance_id)
- 16 systémů

## Výstup

JSON obsahující:
- empirické distribuce skóre
- nulové distribuce acc_eq pro každý prompt

## Metoda

Pro každý vektor délky 16:
1. simulace náhodných judge vektorů
2. výpočet acc_eq vůči human
3. vytvoření histogramu přes 121 hodnot

Počet simulací:
1,000,000 na vektor