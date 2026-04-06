# Program: judge_human_empiric_null_eval.py

## Účel
Program vyhodnocuje LLM-judge modely vůči human hodnocení pomocí metriky acc_eq a její kalibrace vůči empiric-null distribucím.

## Vstupy
- CSV soubory s judge výsledky
- CSV soubor s human výsledky
- JSON soubor s empiric-null distribucemi

## Výpočty
Pro každý (locale, criterion, original_instance_id):
- spočte acc_eq
- převede na percentil vůči null distribuci
- spočte centered skill = 2*percentil - 1

## Agregace
Pro každého judge:
- mean centered skill
- std centered skill
- median centered skill
- počet případů nad/pod náhodou

## Výstup
JSON soubor s výsledky.
