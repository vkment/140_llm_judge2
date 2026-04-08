# Struktura výstupního JSON

## metadata
Informace o běhu programu

## judges
Seznam výsledků pro jednotlivé judge modely

Každý obsahuje:
- overall
- by_locale
- by_criterion
- by_locale_and_criterion

## metriky
- acc_eq
- percentile
- centered_skill

## interpretace
- percentile: poloha vůči nulovému rozdělení
- centered_skill: 0 = náhoda, >0 lepší než náhoda
