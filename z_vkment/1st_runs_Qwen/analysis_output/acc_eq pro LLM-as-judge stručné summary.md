## acc_eq pro LLM-as-judge: stručné summary

### Metrika

**acc_eq** (Deutsch, Foster & Freitag, 2023, EMNLP) je pairwise accuracy definovaná jako podíl všech párů, kde metrika buď správně predikuje pořadí, *nebo správně predikuje rovnost*:

> acc_eq = (C + T_hm) / (C + D + T_h + T_m + T_hm)

Klíčový rozdíl oproti klasickým variantám Kendallova τ: rovnosti jsou plnohodnotnou třídou, nikoli ignorovanými nebo penalizovanými případy. Metrika de facto hodnotí judge jako 3-way klasifikátor: „A > B", „A < B", nebo „A = B".

------

### Proč je to relevantní pro váš use case

Autoři empiricky ukazují, že při hodnocení MQM skóre tvořily rovnosti až **53 % všech párů** (en-de). Ve vašem nastavení — celočíselná škála 1–7, kde v praxi judge typicky používá jen 1–3 hodnoty — bude situace analogická nebo ještě extrémnější. To má dvě přímé důsledky:

1. **Klasické τ varianty (τ_b, τ_10) jsou zkreslené.** τ_b nadhodnocuje metriky s mnoha rovnostmi (NaN problém), τ_10 je naopak systematicky penalizuje. acc_eq je vůči tomuto zkreslení robustní.
2. **Tie calibration** (parametr ε) umožňuje spravedlivé srovnání i tehdy, když různí judges používají škálu odlišně husté — ale pro váš případ, kde judge *přímo* produkuje celá čísla, by měl být ε = 0 přirozený výchozí bod.

------

## Požadavky na prompt pro judge

Z hlediska acc_eq jsou pro prompt klíčové dvě věci, nikoli absolutní hodnota skóre:

**1. Konzistentní hierarchie (concordant pairs)** Judge musí spolehlivě rozlišit, že text kvality A je lepší než text kvality B, kdykoli je tento rozdíl skutečný. Prompt by proto měl:

- Jednoznačně definovat, co znamená každé kritérium (instruction_following, naturalness, coherence) a co je jeho porušení.
- Ideálně ukotvit škálu příklady nebo anchor popisy pro krajní hodnoty (1, 4, 7), aby byl gradient konzistentní.

**2. Správná predikce rovností (T_hm)** Toto je pro acc_eq stejně důležité jako správné pořadí. Judge musí být ochoten říct „stejná kvalita" a dělat to konzistentně. Prompt by proto měl:

- Explicitně uvést, že rovnost je legitimní odpověď a kdy ji použít (např. „pokud nelze rozlišit kvalitu na dané škále, přiřaďte stejné číslo").
- **Nepobízet** judge k umělé diferenciaci — formulace jako „vždy zvolte jiné číslo pro každý text" by rovnosti potlačily a zhoršily acc_eq.
- Pokud judge hodnotí texty nezávisle (ne párově), konzistenci rovností zajišťuje opakovatelnost: stejný text musí dostat stejné skóre. To vyžaduje deterministické nastavení (temperature = 0) a stabilní formulaci kritérií.

**3. Škálování (využití rozsahu)** Kolaps na 1–2 hodnoty není nutně problém pro acc_eq, pokud jsou hierarchie a rovnosti správné — ale snižuje rozlišovací sílu metriky. Prompt může škálování podpořit například postupnou definicí: „7 = žádné chyby, 5–6 = drobné chyby, 3–4 = zřetelné chyby, 1–2 = závažné selhání."

------

### Shrnutí

Pro optimalizaci acc_eq je priorita: ***správné pořadí tam, kde rozdíl existuje* + *rovnost tam, kde rozdíl neexistuje*** — nikoli přesná shoda absolutních hodnot se zlatým standardem. Prompt by tedy měl být formulován tak, aby judge nebyl tlačen do zbytečné diferenciace a zároveň měl dostatečně jasná kritéria pro rozlišení, kde rozdíl skutečně je.