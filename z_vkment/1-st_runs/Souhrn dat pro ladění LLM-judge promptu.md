## Souhrn dat pro ladění LLM-judge promptu

Na základě programu `analyze_human_eval.py`, který analyzoval data odpovědí lidských judgů ze souboru `oeg_human_eval_data.csv`. Jeho účelem bylo objektivněji posoudit to, že již vstupní dvojice prompt - response mají v různých jazycích jiné rozložení (distribuce). Níže jsou závěr z výstupních tabulek `table_score_freq_pct.csv` a  `table_summary_stats.csv`.

### 1. Globální kontext: jazyk určuje, kde na škále žijí data

Data nejsou rovnoměrně rozložena ani náhodně rozptýlena — každý jazyk má svůj charakteristický „domov" na škále 1–7. To má přímý dopad na to, kde musí být judge prompt citlivý.

------

### 2. Skupiny jazyků podle chování

**Skupina A — Stropový efekt (ceiling): Němčina, Ruština, Angličtina, Čínština**

Toto jsou jazyky, kde valná většina odpovědí skončí na 6–7. Konkrétně:

- Němčina/coherence: průměr 6.58, std pouhých 0.76 — toto je nejužší distribuce v celém datasetu. Skóre pod 5 jsou statistická rarita (< 1 %).
- Ruština/instruction_following: průměr 6.49, std 1.10, modus 7, Q1 i Q3 = 7.
- Angličtina: instruction_following průměr 6.44, std 0.85, skóre ≥ 5 tvoří 97 % všech hodnocení.
- Čínština: naturalness má dokonce 96.3 % skóre ≥ 5.

**Co to znamená pro prompt:** Judge v těchto jazycích musí být extrémně citlivý na rozdíl mezi 5, 6 a 7. Rozdíl mezi „dobré" a „výborné" je to jediné, co se zde opravdu řeší. Pokud prompt tuto granularitu nemá, bude vše paušálně 7 a judge nebude k ničemu. Zároveň — pokud judge přiřadí 4 nebo méně, je to v těchto jazycích silný signál opravdu špatné odpovědi, ne běžná situace.

------

**Skupina B — Střední pásmo s normálním rozptylem: Čeština, Indonéština, Hindština**

- Čeština/coherence: průměr 5.69, std 1.36. Distribuce je rozumně rozložená přes 5–7 (85 % skóre ≥ 5), ale 4 se objevuje v 7.7 % a 3 ve 4.2 % případů.
- Čeština/naturalness: **nejzajímavější případ v celé češtině.** Modus je 6 (ne 7 jako u ostatních kritérií), průměr 5.34, rozložení je 5–6–7 zhruba vyrovnané s tím, že 7 je naopak méně než 5 a 6. To znamená, že „výborné" naturalness je v češtině vzácnější než jen „dobré". Judge prompt musí být schopen věrohodně přiřadit 5 nebo 6 bez tendence skočit rovnou na 7.
- Indonéština je podobná češtině v coherence a naturalness, ale instruction_following má 66.4 % na samotném vrcholu (7) — zde se chová spíše jako skupina A.

**Co to znamená pro prompt:** Tyto jazyky potřebují dobrou citlivost přes celé pásmo 4–7. Prompt musí mít jasné anchor points pro každé skóre, ne jen pro extrémy.

------

**Skupina C — Dolní pásmo: Bengálština**

Toto je jazykově nejodlišnější případ:

- Bengali/coherence: průměr 3.42, modus 4, std 1.45. Téměř 51 % skóre je ≤ 3, jen 19.7 % skóre ≥ 5.
- Bengali/naturalness: průměr 3.66, 41.3 % skóre ≤ 3.
- Bengali/instruction_following: o něco lepší, průměr 4.19, modus 5, ale stále 26.8 % skóre ≤ 3.

**Co to znamená pro prompt:** V bengálštině se judge musí pohybovat v pásmu 2–5. To jsou hodnoty, které jsou v němčině nebo angličtině prakticky neobsazené. Prompt, který je kalibrovaný na angličtinu, bude mít tendenci bengálské odpovědi nadhodnocovat, protože jeho „dobrý příklad" pro skóre 5 bude v bengálském kontextu relativně slušná odpověď. Jsou potřeba bengálsky specifické anchor examples.

------

**Skupina D — Bimodální/nestandardní: Arabština**

Arabština je statisticky nejpodivnější případ v datasetu a zaslouží zvláštní pozornost:

- Arabic/coherence a instruction_following: chování jako skupina A. Průměry 5.59 a 5.81, velká koncentrace na 7 (48 % resp. 56 %). Zdánlivě normální.
- Arabic/**naturalness**: naprostý outlier. Průměr 3.16, std 2.35 (nejvyšší v celém datasetu), modus **1** s 48.51 % všech skóre. Zároveň 15 % skóre je 5, 10 % je 6, 12.5 % je 7. Distribuce je **silně bimodální** — buď odpověď dostane 1, nebo dostane 5–7. Střední pásmo 2–4 je téměř prázdné (celkem jen ~13 %).

**Co to znamená pro prompt:** Arabská naturalness odráží reálný fenomén: buď je přirozená arabská formulace výborná, nebo je to přeložená/strojová arabština, která zní cize a dostává 1. Judge prompt musí být schopen tuto dichotomii zachytit, nikoliv „průměrovat" ke středu škály. Prompt kalibrovaný na plynulé přechody mezi hodnotami bude na arabské naturalness selhávat systematicky — bude přiřazovat 3–4 tam, kde správná odpověď je 1 nebo 6.

------

**Japonština — specifický případ s dlouhým ocasem:**

- Japanese/naturalness: průměr 5.62, ale std 1.79 — nejvyšší rozptyl ze skupiny „normálních" jazyků. 3.53 % skóre je 1, 5.3 % skóre je 2. Japonština tedy má sice těžiště nahoře, ale s nenulovou pravděpodobností velmi nízkých skóre, což ostatní „vysoké" jazyky nemají. To může signalizovat, že hodnotitelé trestali specifické chyby ostřeji.

------

### 3. Critérium-specifická pozorování

Across všech jazyků platí konzistentně:

**Naturalness je systémově nejtěžší kritérium** — má nejnižší průměry a nejvyšší rozptyly ve všech jazykových skupinách. Toto naznačuje, že lidé mají vyšší nároky nebo větší neshodu v tom, co je „přirozené" než v tom, co je „koherentní" nebo „following instructions". Judge prompt pro naturalness potřebuje nejpečlivější kalibraci a nejkonkrétnější anchor examples.

**Instruction_following je nejkonzistentnější kritérium** — nejnižší std v angličtině (0.85) a češtině (1.27). Hodnotitelé se nejvíce shodují. Prompt pro toto kritérium bude mít pravděpodobně nejlepší transfer mezi jazyky.

------

### 4. Praktická doporučení pro ladění promptu

Za prvé — **nespoléhej na jeden společný prompt.** Data jasně ukazují, že angličtina a bengálština žijí na opačných koncích škály. Prompt, který dobře rozlišuje 5 od 7 v angličtině, nemá žádnou citlivost tam, kde bengálština potřebuje rozlišovat 2 od 4.

Za druhé — **anchor examples musí být jazykově specifické, nebo alespoň skupinově specifické.** Pro skupinu A (DE, RU, EN, ZH) potřebuješ příklady rozlišující 5 vs 6 vs 7. Pro skupinu C (Bengali) potřebuješ příklady rozlišující 2 vs 3 vs 4 vs 5.

Za třetí — **arabská naturalness potřebuje speciální treatment.** Bimodální distribuce (1 nebo 5–7, nic mezi tím) naznačuje, že tam existuje binární signál (přirozená arabština vs. přeložená arabština), nikoliv spojitá škála. Prompt by měl explicitně rozlišovat tento jev, jinak bude systematicky chybovat.

Za čtvrté — **češtinu v naturalness netlač k 7.** Data ukazují, že 7 je v českém naturalness vzácnější než 6 nebo 5. Pokud prompt implicitně předpokládá, že „bez chyb = 7", bude českou naturalness nadhodnocovat oproti tomu, co lidé skutečně hodnotili.

Za páté — **validuj prompty jazykově separovaně, ne agregovaně.** Celková korelace s human ground truth může být slušná i s nevhodným promptem, pokud angličtina táhne průměr nahoru. Sleduj korelaci per jazyk a per kritérium.