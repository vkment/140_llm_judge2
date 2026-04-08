# Reverzní inženýrství judge_human_agreement.py

##### **`judge_human_agreement.py`**  - zastřešující skript pro výpočet hodnocení LLM judgů 

- načítá lidská hodnocení z `oeg_human_eval_data.csv`, není-li soubor dostupný, tak je rekonstruuje ze souborů `oeg_human_eval_raw_data/*.csv`

- načítá LLM hodnocení z `oeg_judge_run2_submission_data.csv`, není-li soubor dostupný, čte pro LLM-soudce z JSON submission souborů, a to funkcí  `gather_oeg_judge_submission_data()`: rozparsuje JSON submission soubory, z `taskid` vytáhne criterion, prompt-id, locale a systém, a výsledné hodnocení převede na číslo 1–7.

- Dataframes `df_judge_submission` i `df_human_eval` se tak vždy sjednotí na společný formát:

  - `judge_model_name`
  - `criterion`
  - `submission_system_name`
  - `original_instance_id`
  - `locale`
  - `score`

- 0. krok filtruje dva dataframes na stejný subset záznamů

  Program vytvoří pomocný klíč:

  - `original_instance_id_with_locale =` **`original_instance_id + "_with_" + locale`**

  

- Funkce **`perform_EDA()`** provádí zejména sadu kontrol konzistence:

  - že judge tabulka má po filtraci **287040 řádků**,
  - že human tabulka má **22080 řádků**,
  - že je 13 judge modelů,
  - 3 kritéria,
  - 16 systémů,
  - 46 promptů,
  - 10 locale. 

  Umí tisknout i různé souhrnné statistiky, ale v hlavním běhu je volaná s `verbose=False`, tj. zde funguje hlavně jako sada kontrol

- Spočte **`ranking_accuracy`**

  To je první hlavní výstup.

  Tahle metrika nepracuje po jednotlivých promptech, ale na systémové úrovni. Program:

  - u *human* spočte průměrné skóre každého `submission_system_name` přes celý dataset,
    - z toho vytvoří pořadí 16 systémů, které vytvářely odpovědi, tedy jak kvalitní se odpovědi (a potažmo systémy je vytvářející) jevily lidským soudcům, 
  - totéž udělá pro každého *judge_model_name* (zde jsou LLM jako soudci),
    - a pak porovná obě pořadí metrikou `my_pairwise_acc`., tj.:

  > jak dobře se shoduje globální pořadí 16 systémů podle **LLM-soudce** s globálním pořadím 16 systémů podle lidí. 

  

- Výpočet  **`acc_eq` po kritériích**

  Tady se dostáváme k tvému „an item“.

  Funkce **`get_score_by_criterion()`** vezme jedno criterion, třeba `instruction_following`, a pak:

  - najde pro něj všechny unikátní **`original_instance_id_with_locale`**,
    - pro každou takovou instanci vezme 16 lidských skóre a 16 judge skóre,
    - seřadí je podle `submission_system_name`,
    - tím dostane dva 16-prvkové vektory,
    - a na ty aplikuje funkci metriky, zde `my_acc_eq`. 

  Takže ano:

  > jedna instance = jeden 16-dimenzionální vektor pro pevné `criterion × locale × prompt`.

  Program pak spočte `acc_eq` pro každou takovou instanci zvlášť a následně tyto hodnoty zprůměruje přes všechny instance daného kritéria a daného judge modelu. 

- agregace výsledků a uložení do JSON, na závěr:

  - uloží `ranking_accuracy`,

  - uloží `acc_eq_by_criterion`,

  - spočte i `acc_eq_average`, což je prostý průměr přes tři kritéria pro každý judge model,

  - a vše zapíše do JSON souborů. 





##### **`corr_utils.py`** - výpočty různých metrik

- rank_human, rank_metric - jsou seznamy hodnocení lidského vs. hodnocení LLM-soudce, 
- názvy jsou matoucí, hodnoty v seznamech mají být skóre na Lickertově škále, nikoliv rank
- seznamy musí být vzájemně seřazeny stejně tak, aby skóre na indexu vždy odpovídalo shodné odpovědi, jež je skórem hodnocená

​	Co přesně dělá např. **`my_acc_eq`**

- Funkce projde všechny dvojice pozic `i < j` z 16 systémů (tj. všechny páry kombinace) a počítá:

  - `C` = concordant pairs

  - `D` = discordant pairs

  - `T_h` = tie jen u human

  - `T_m` = tie jen u judge

  - `T_hm` = tie u obou

Pak spočte
$$
acc\_eq = \frac{C + T_{hm}}{C + D + T_h + T_m + T_{hm}}
$$
čili:

- správně je i shoda (*concordance*) v pořadí,
- i shoda v remíze (*tie*, je-li ovšem u human i u judge současně)



<Tato část není dotvořená - dopsaná>







#### Je invariantní na monotónní transformace

- nezáleží na absolutních hodnotách (1–7), na shodě mezi nimi,
- záleží jen na **pořadí a rovnostech skóre mezi exempláři**

Tj. model může být „přísnější“ nebo „mírnější“ a přesto může dosáhnout stejný `acc_eq`, dokud zachovává relace podobně. Jinak řečeno, každý soudce může mít částečně jinak nakalibrovánu svou citlivostí. 

#### 2. Přirozeně pracuje s remízami (ties)

Pokud má lidský soudce stejné skóre pro oba exempláře a LLM-soudce rovněž stejné skóre pro oba exempláře (byť třeba jiné než dal lidský soudce), počítá se uvedené za zcela správný případ, není ignorováno. Metrika je proto stabilní i při pro LLM-soudce běžné hrubé Likert škále 1–7 (nebo 1-5 apod.).

#### 3. Lokální hodnocení na "item-level"

- počítá se ve skupinách **po jednotlivých itemech (zde vektorech 16 hodnot)**,
- a až pak se průměruje.

Důsledkem je, že acc_eq:

- není ovlivněn globálními posuny mezi jazyky (locale) nebo kritérii,

- je soustředěn na hodnocení výsledné schopnosti:

  > „rozlišit lepší vs. horší odpovědi v rámci stejného promptu“

Ačkoliv soudce vždy hodnotí jednotlivě, uvedená výsledná schopnost je **klíčová pro úlohu judge**. Schopnost srovnávat naznačuje, že se judge drží své vnitřní metodologie a je schopen ji reprodukovat.  

#### 4. Poměrně jemná granularita (120 párů)

Pro 16 systémů - zdrojů odpovědí:
$$
\binom{16}{2} = 120 \text{ párů exemplářů.}
$$
Metrika má jemnější rozlišení (krok 1/120), než by poskytovaly hrubší metriky, např. jen srovnání, nebo jen top-1 accuracy apod.

#### 5. Symetrie vůči human a judge

Metrika zachází symetricky s relacemi lidskými i relacemi od LLM.

Důsledkem je, že dokáže překlenout nejen různost kalibrace LLM-judge, ale případně i subjektivní "kalibrace" lidského soudce, který poskytoval hodnocení. Aspoň tehdy, dokud jeden lidský soudce hodnotí všechny exempláře z dané jedné skupiny, je koncentrovaný a uvažuje konzistentně, jak jen je schopen.  

Výsledně žádná strana není apriori privilegovaná strukturou metriky, cení se potřebná schopnost judge docházet ke konzistentním hodnocením, které výsledně dobře srovnávají.