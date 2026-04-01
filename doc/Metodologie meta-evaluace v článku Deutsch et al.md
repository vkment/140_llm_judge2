# Metodologie meta-evaluace v článku Deutsch et al.

https://claude.ai/chat/12bce436-06e0-44d0-94b5-497e5bafebc1

---

*Potřebuji vysvětlit článek Deutsch et al v příloze Deutsch-Foster-Freitag_Ties_Matter_Meta-Evaluating_2023.pdf.*

*Zřejmě máme využít pro  úlohu LLM as a judge podle p05_Multilingual_LLM_as_a_judge.md, dále upřesněné v README.md.*

*Podstatou naší úlohy je zřejmě pouze vybrat ten či onen model a s předpřipravenými daty provést jeho inference např. podle šablony  judge_utils2.py. , tj. sebrat data pro:*

- *`judge_it` -> `instruction_following`*
- *`judge_coherence` -> `coherence`*
- *`judge_natural` -> `naturalness`*

*Mám i další soubory v orig_files.txt příloze. V dalších přílohách jsou kousky dat.*

*Než se pustíme do analýzy předpřipravených .py souborů, chci se ale vyznat v samotné metodologii. Vysvětli mi článek podrobně, začni tím jak funguje Pearson a Spearman, později ten Kendall. Z Figure  1 v článku jsem nepobral ani úplné základy. Vysvětluje postupně a když Ti odsouhlasím pochopení, pokračuje dále.*

*Ještě je pak druhý článek od Kocmi et al. , ale ten možná až později?*

*Deutsch et al. (EMNLP 2023): defines meta-evaluation metrics used here (including acc_eq, tau_eq, etc.). https://aclanthology.org/2023.emnlp-main.798.pdf* 
*Kocmi et al. (WMT 2025): defines the WMT MIST 2025 data/task setup used for this project. https://aclanthology.org/2025.wmt-1.23.pdf*

---

# Deutsch et al. – vysvětlení od základů

Začneme úplně od začátku. Celý článek řeší jednu otázku: **jak změřit, jak dobře nějaká automatická metrika (např. LLM-judge) souhlasí s lidskými hodnoceními?**

------

## Krok 1: Co vlastně měříme?

Mějme příklad: 5 překladů, které ohodnotili lidé i automatická metrika:

| Překlad | Lidské skóre (h) | Skóre metriky (m) |
| ------- | ---------------- | ----------------- |
| A       | 1                | 2                 |
| B       | 3                | 3                 |
| C       | 5                | 4                 |
| D       | 7                | 7                 |
| E       | 7                | 6                 |

Otázka: *jak moc se metrika shoduje s lidmi?*

------

## Pearson's r – lineární shoda

Pearson měří, zda jsou dva vektory čísel **lineárně závislé** – tj. když člověk zvýší skóre o 1, zvýší ho metrika taky přibližně o konstantu?

Hodnota r je mezi -1 a +1:

- **r = 1**: perfektní lineární shoda
- **r = 0**: žádná lineární závislost
- **r = -1**: perfektní opačná závislost

**Slabina Pearsona**: je citlivý na odlehlé hodnoty (outliers) a na to, zda je závislost skutečně lineární.

------

## Spearman's ρ – pořadová lineární shoda

Spearman dělá totéž co Pearson, ale **nejprve převede hodnoty na pořadí (ranky)** a pak spočítá Pearsonovo r na těch pořadích.

Takže místo hodnot {1, 3, 5, 7, 7} pracuje Spearman s pořadími {1, 2, 3, 4, 4}.

**Výhoda**: méně citlivý na outliers a nevyžaduje linearitu – zachytí jakoukoliv monotónní závislost.

------

## Figure 1 z článku – klíčové

Teď Figure 1. Jsou tam dvě metriky (metric1 a metric2) oproti lidskému skóre:

**metric2** (čtverečky): skóre jsou přesně 0, 0, 0, 0, 5, 10 – zatímco lidské jsou 0, 2, 4, 6, 8. Metrika metric2 **perfektně seřadí** překlady od nejhoršího po nejlepší, ale nelineárně (je "placatá" dole a pak skočí). Proto má Spearman ρ = 1.00, ale Pearson r = 0.71.

**metric1** (kolečka): skóre jsou rozptýlená kolem přímky – lineárnější, ale s šumem. Proto má Pearson r = 0.94, ale Spearman ρ = 0.94 také.

**Závěr z Figure 1**: Pearson preferuje metriku která je *globálně lineární* (metric1), zatímco Spearman/Kendall preferuje metriku která *správně řadí* páry (metric2). **Proto jsou tyto statistiky komplementární.**

------

Rozumíš zatím tomuto rozdílu – lineární shoda (Pearson) vs. pořadová shoda (Spearman)? Pak přejdeme na Kendall's τ, kde se věci začnou komplikovat právě kvůli tzv. **ties** (shodám ve skóre).

---

*Chápu toho Pearson v principu. Ne jak se počítá, ale chápu princip. U Spearman mi to dává smysl, pokud je vzorků (překladů) relativně málo. Pokud mám třeba 30 překladů a škálu 1..7, tak je dost pravděpodobné, že budu mít celou škálu vyčerpánu, tj. nevidím pak podstatný rozdíl, aspoň na první pohled.*

*Z Figure 1 nechápu proč je na ose Y Metric Score a na ose X Human Score. Navíc s různými měřítky? Ideálně by tam pak měla být přímka, možná má směrnici podle poměrů škál?*

*Zkus mi uvedené ještě dovysvětlit.*

---

## Figure 1 – osy a měřítka

### Proč X = Human, Y = Metric?

Lidské hodnocení bereme jako **zlatý standard** (ground truth). Automatická metrika se ho snaží napodobit. Proto:

- **X osa = co chceme** (lidé řekli)
- **Y osa = co metrika předpověděla**

Je to stejná logika jako u jakéhokoliv modelu: na X je "správná odpověď", na Y je "co model říká".

------

### Různá měřítka – proč?

Metrika nemusí používat stejnou škálu jako lidé. Lidé hodnotili 0–8, metrika může interně produkovat 0–15. **To nevadí** – Pearson ani Spearman nezávisí na absolutních hodnotách, jen na tvaru závislosti.

------

### Jak by vypadala "ideální" metrika?

Nemusela by to být přímka se směrnicí 1. Stačí **jakákoliv přímka** – třeba y = 2x (metrika prostě škáluje jinak). Pearson r = 1 by nastal i pro y = 2x + 5.

```
Metric
Score
 15|              ✦  ideální: přímka (libovolná směrnice)
   |          ✦
   |      ✦
   |  ✦
  0|________________
   0              8   Human Score
```

------

### Zpět k Figure 1 – co tam vidíme

**metric1** (kolečka): body leží *přibližně* na přímce, ale s šumem → Pearson r = 0.94

**metric2** (čtverečky): hodnoty jsou podle článku zhruba:

| Human | metric2 |
| ----- | ------- |
| 0     | 0       |
| 2     | 0       |
| 4     | 0       |
| 6     | 5       |
| 8     | 10      |

Tedy metric2 je "placatá" pro nízká skóre a pak skočí nahoru – **není to přímka**, proto Pearson r = 0.71. Ale pořadí zachovává perfektně → Spearman ρ = 1.00.

------

### Tvá poznámka o 30 překladech a škále 1–7

Máš pravdu – při více vzorcích a hrubší škále vznikají **ties** (shody ve skóre). Právě to je jádro celého článku! Kendall's τ s tím má problém, a to je to, co Deutsch et al. řeší.

Chceš teď přejít na Kendall's τ a co jsou ties?

---

*Nyní stručně vysvětli Kendall. Za 2.2 až později.*

---

## Kendall's τ – základní myšlenka

Místo měření lineární závislosti Kendall **prochází všechny možné páry** překladů a ptá se: *shoduje se metrika s lidmi na tom, který překlad je lepší?*

------

### Konkordantní vs. diskordantní páry

Vezmi dva překlady A a B:

- Člověk říká: A > B, metrika říká: A > B → **konkordantní pár (C)**
- Člověk říká: A > B, metrika říká: A < B → **diskordantní pár (D)**

Kendall's τ pak jednoduše:
$$
\tau = \frac{C - D}{C + D + \text{(ties)}}
$$
Hodnota je mezi -1 a +1, stejně jako Pearson/Spearman.

------

### Proč je to intuitivnější než Pearson?

Hodnota τ = 0.7 znamená doslova: *"ze všech párů překladů metrika správně seřadila 70 % více párů, než jich seřadila špatně."*

------

### A kde je problém?

Právě ve jmenovateli – **co dělat s ties?** Tedy když člověk řekne A = B (stejné skóre), nebo metrika řekne A = B?

Různé varianty τ (τ_a, τ_b, τ_10, τ_13...) se liší **právě jen v tom, jak zacházejí s ties**. A to je celý článek.

Jdeme na ties?

---

*Brát všechny páry, jak to přesně funguje?*

*Ve Figure 1 máme hodnoty 0, 1, 2, ..., 8, 9 na ose x (Human Score), tedy 10 hodnot, pro metric1 i pro metric2.* 

*To bychom tedy vytvářeli všechny páry z 10 hodnot, s výjimkou sebe sama?*

---

Přesně tak. Pro n = 10 bodů vytvoříme všechny dvojice (bez opakování a bez pořadí), tedy:

$$
\binom{10}{2} = \frac{10 \cdot 9}{2} = 45 \text{ párů}
$$
Pro každý pár (i, j) se pak ptáme: **shoduje se směr rozdílu u člověka i u metriky?**

| Pár          | Human   | metric2 | Shodují se?    |
| ------------ | ------- | ------- | -------------- |
| (bod1, bod2) | h1 < h2 | m1 < m2 | ✓ konkordantní |
| (bod1, bod6) | h1 < h6 | m1 = m6 | tie v metrice  |
| ...          | ...     | ...     | ...            |

Při 30 překladech by to bylo $\binom{30}{2} = 435 $ párů – stále zvládnutelné.

---

*Ve 2.2 - co se myslí "system" level resp. "segment" level? A pak ty možnosti No-Grouping, Group-by-Item, Group-by-System?*

*Prostě vysvětli mi nyní část 2.2 článku*

---

## 2.2 – System vs. Segment level

### Základní setup

Máme:

- **N systémů** (různé MT modely, např. Google Translate, DeepL, ...)
- **M zdrojových vět** (věty k překladu)
- Pro každou kombinaci (systém × věta) máme jeden překlad → celkem **N × M překladů**

------

### System-level

Každý systém dostane **jedno agregované skóre** (průměr přes všech M vět). Pak porovnáváme N čísel – lidské pořadí systémů vs. pořadí podle metriky.

*Příklad: Google Translate dostane od lidí průměr 6.2, od metriky 6.5. DeepL dostane 5.8 vs. 5.6. Shodují se v pořadí?*

Je to hrubé, ale stabilní.

------

### Segment-level

Porovnáváme skóre na úrovni **jednotlivých překladů** – tedy N × M hodnot. Jemnější, ale více šumu.

Tři způsoby jak to počítat:

**No-Grouping**: vezmi všech N × M překladů najednou, spočítej jednu korelaci.

**Group-by-Item**: pro každou zdrojovou větu j zvlášť porovnej N překladů (od různých systémů). Průměruj přes všech M vět. → *"Jak dobře metrika porovná systémy na konkrétní větě?"*

**Group-by-System**: pro každý systém i zvlášť porovnej jeho M překladů. Průměruj přes N systémů. → *"Jak dobře metrika hodnotí různé věty v rámci jednoho systému?"*

------

### Proč je to důležité?

WMT historicky používalo **Group-by-Item** pro segment-level. A právě tady ties způsobují největší problémy – protože ve skupině je jen N ≈ 15 systémů, takže shody ve skóre jsou velmi časté. To je základ problému v článku.

Jdeme na ties a jejich varianty?

---

*K **System-level***

 *'System-level correlations are calculated between the N metric and human scores per system, typically calculated by averaging over the M segment scores.'*

*Chápu to, že se srovnává N-th metric vs. human score, a nějak průměruje. Je to tak, nebo nějak jinak?*

*Jen toto rozmysli a vysvětli, stručně*

---

Přesně tak. Pro každý systém i:

- **Lidské skóre systému** = průměr lidských hodnocení přes všech M vět
- **Skóre metriky** = průměr skóre metriky přes všech M vět

Pak máme **N dvojic** (human_avg, metric_avg) – jedna za každý systém – a na těchto N dvojicích spočítáme korelaci (Pearson nebo Kendall).

```
Systém        Human avg    Metric avg
Google            6.2          6.5
DeepL             5.8          5.6
GPT-4             7.1          6.9
...
```

Korelace těchto N dvojic = system-level korelace.

---

*Dobře, a jak teď funguje segment-level?*

*" Segment-level correlations evaluate metric scores on individual translations rather than aggregated system scores. They can be calculated in several different ways (see Appendix A for equation definitions):* 
*• No-Grouping: Calculate the correlation between the N × M translation scores* 
*• Group-by-Item: Calculate the average correlation between the N translation scores grouped by source segment3* 
*• Group-by-System: Calculate the average correlation between the M translation scores grouped by system*

*"*

---

## Segment-level – tři způsoby

Máme N × M překladů, každý s lidským skóre a skóre metriky.

------

### No-Grouping

Jednoduše vezmi všech N × M dvojic (human, metric) a spočítej **jednu korelaci** na celém souboru.

```
(Google, věta1): human=7, metric=6
(Google, věta2): human=5, metric=5
(DeepL, věta1):  human=6, metric=7
...  → jedna korelace přes vše
```

------

### Group-by-Item

Pro každou větu j vezmi **N překladů** (od různých systémů) a spočítej korelaci. Opakuj pro všech M vět, pak průměruj.

```
věta1: [(Google,7,6), (DeepL,6,7), (GPT,7,7), ...] → korelace_1
věta2: [(Google,5,5), (DeepL,4,5), (GPT,6,6), ...] → korelace_2
...
výsledek = průměr(korelace_1, korelace_2, ...)
```

*Otázka: "Umí metrika seřadit systémy na konkrétní větě?"*

------

### Group-by-System

Pro každý systém i vezmi **M překladů** a spočítej korelaci. Průměruj přes N systémů.

```
Google: [(věta1,7,6), (věta2,5,5), ...] → korelace_Google
DeepL:  [(věta1,6,7), (věta2,4,5), ...] → korelace_DeepL
...
výsledek = průměr(korelace_Google, korelace_DeepL, ...)
```

*Otázka: "Umí metrika rozlišit těžké a lehké věty v rámci jednoho systému?"*

------

Klíčový rozdíl: Group-by-Item pracuje se skupinami velikosti **N ≈ 15** (málo systémů), což je důvod proč tam ties způsobují největší problémy. Jdeme na ties?

---

*Dobře, nyní vysvětli 2.3, pokud je k vysvětlení více než výše ty C vs D vs Tie.*

---

## 2.3 – Varianty Kendall's τ

Jediné nové oproti C a D jsou **tři typy ties** (Table 2):

| Symbol   | Význam                                          |
| -------- | ----------------------------------------------- |
| **T_h**  | pár shodný jen u lidí (h1 = h2, ale m1 ≠ m2)    |
| **T_m**  | pár shodný jen u metriky (m1 = m2, ale h1 ≠ h2) |
| **T_hm** | pár shodný u obou (h1 = h2 a m1 = m2)           |

------

### Jak se varianty liší?

Všechny varianty (τ_a, τ_b, τ_10, τ_13, τ_14) mají **stejný čitatel C − D**, liší se jen **jmenovatelem** – tedy tím, které ties zahrnují do "celkového počtu párů".

Například:

- **τ_13** = C − D / (C + D) → ties úplně ignoruje, jako by neexistovaly
- **τ_10** = ties v metrice penalizuje jako diskordantní páry
- **τ_b** = standardní statistická varianta, ties "normalizuje" ale neodměňuje

------

### Klíčový problém

**Žádná varianta přímo neodměňuje metriku za správně předpovězený tie** (T_hm). Tedy pokud člověk řekne A = B a metrika také řekne A = B, žádná existující τ za to metriku nepochválí.

To je přesně to, co autoři navrhují opravit přes **acc_eq**. Jdeme na to?

---

*Dobře. Nyní k části 3 Analysis Setup.* 

*Stručně, výstižně, co budu potřebovat na další pochopení.*

---

## 3 – Analysis Setup

Pouze dva důležité body:

------

### Data: MQM skóre

Místo běžných lidských hodnocení (Direct Assessment, DA) používají **MQM skóre** – hodnocení od expertních překladatelů, kteří označují konkrétní chyby.

Důležitá vlastnost MQM: **skóre jsou celá čísla** (počty chyb), proto vzniká **mnoho ties** – zejména **skóre 0** (bezchybný překlad).

Tři jazykové páry: en→de, zh→en, en→ru.

------

### Metriky: dva typy

**Regresní metriky** (Metric-X, COMET-22, BLEURT): produkují **desetinná čísla** → ties téměř nikdy.

**LLM/klasifikační metriky** (GEMBA-GPT4, MaTESe): produkují **malou množinu hodnot** → ties velmi často (až 70 % párů, viz Table 4).

------

### Proč to je důležité?

Tyto dva typy metrik jsou **nespravedlivě porovnávány** existujícími variantami τ – jedny jsou za ties trestány, druhé ne. To je přesně co článek řeší.

Jdeme na sekci 4 a 5 – proč jsou ties důležité a jak existující τ selhávají?

---

*Dobře, projdi nyní sekci 4 článku.*

---

## 4 – Why Ties are Important

Tři důvody proč ties nelze ignorovat:

------

### 1) MQM ties jsou důvěryhodné

Starší DA hodnocení byla crowdsourcovaná – shoda dvou překladů mohla být náhoda. MQM hodnotí ***experti*** → **tie skutečně znamená, že oba překlady jsou stejně dobré**. Nelze to hodit pod stůl.

------

### 2) Ties jsou velmi časté

Z Table 3 – pro en→de:

- **53 % všech párů** má shodné MQM skóre
- **40 % párů** má oba překlady bezchybné (MQM = 0)

A jak se MT systémy zlepšují, bezchybných překladů přibývá → ties budou ještě častější.

------

### 3) LLM metriky produkují mnoho ties

Z Table 4 – procento párů kde metrika predikuje tie:

| Metrika     | en→de      |
| ----------- | ---------- |
| COMET-22    | 1.3 %      |
| GEMBA-GPT-4 | **69.6 %** |
| MaTESe      | **71.9 %** |

Regresní metriky (COMET) ties téměř nepredikují. LLM metriky ano – protože pracují s diskrétní škálou (1–7 apod.).

------

**Závěr**: Ties jsou časté v lidských hodnoceních i v LLM metrikách, jsou důvěryhodné, a přesto je žádná existující τ správně nezohledňuje. Jdeme na sekci 5?

---

*Dobře, projdi nyní sekci 5 článku.*

---

## 5 – Shortcomings of Kendall's Variants

### 5.1 – Motivační příklad (Figure 2)

Mějme lidské skóre a dvě metriky:

```
h  = [0, 0, 0, 0, 1, 2]
m1 = [0, 0, 0, 0, 2, 1]
m2 = [0, 1, 2, 3, 4, 5]
```

**m1** se mýlí jen v 1 páru z 15 (prohodila 1 a 2 na konci), ale správně predikuje všechny ties.

**m2** se mýlí v 6 párech – vůbec nepredikuje ties, přestože 4 ze 6 hodnot u lidí jsou shodné (0).

Intuitivně je m1 lepší. Ale existující τ to **nevidí** – považují m1 a m2 za přibližně stejné, nebo dokonce preferují m2.

------

### 5.2 – NaN problém

Pokud jsou v nějaké skupině (Group-by-Item) **všechny skóre metriky stejné** (constant vector), τ není definované → **NaN**.

NaN skupiny se pak **vyhazují z průměru** → metrika se hodnotí na snazší podmnožině dat → umělé zlepšení korelace.

Autoři ukázali, že tohoto šlo zneužít: stačí zaokrouhlit skóre Metric-X do malého počtu košů (buckets) → vzniknou NaN skupiny → korelace τ_b se dramaticky zlepší, ale metrika ve skutečnosti není lepší.

------

**Závěr sekce 5**: Existující τ jsou slepé vůči ties a lze je zneužít. Proto autoři navrhují acc_eq. Jdeme na sekci 6?

---

*Ano, vysvětli sekci 6 článku.*

---

## 6 – Evaluating with Pairwise Accuracy (acc_eq)

### Základní myšlenka

Místo τ navrhují autoři **acc_eq** – prostý podíl správně zodpovězených párů, včetně ties:
$$
\text{acc}_{eq} = \frac{C + T_{hm}}{C + D + T_h + T_m + T_{hm}}
$$
Čitatel: správně seřazené páry **+** správně predikované ties. Jmenovatel: **všechny páry** bez výjimky.

------

### Proč je to lepší?

**Acc_eq je nikdy NaN** – jmenovatel je vždy nenulový (všechny páry).

**Odměňuje T_hm** – pokud člověk řekne A = B a metrika také řekne A = B, acc_eq to považuje za správnou odpověď.

**Interpretace je přímočará**: hodnota 0.7 znamená doslova *"metrika správně zodpověděla 70 % všech párů"*. τ takovou přímou interpretaci nemá.

------

### 6.1 – Precision a Recall pro ties

Acc_eq lze dále rozložit (Table 5):

| Metrika                | Význam                                                       |
| ---------------------- | ------------------------------------------------------------ |
| ties_precision         | z párů kde metrika predikovala tie, kolik jich bylo skutečně tie u lidí? |
| ties_recall            | z párů kde lidé dali tie, kolik jich metrika správně predikovala? |
| correct-rank_precision | z párů kde metrika predikovala pořadí, kolik bylo správně?   |
| correct-rank_recall    | z párů kde lidé dali pořadí, kolik metrika správně seřadila? |

------

**Závěr**: acc_eq je jednoduchá, interpretovatelná, nikdy NaN, a spravedlivě zachází s ties. Ale má jeden problém – ***penalizuje*** regresní metriky které ***ties vůbec nepredikují***. To řeší sekce 7 (Tie Calibration). Jdeme na ni?

---

*Ano, vysvětli sekci 7 článku.*

---

## 7 – Tie Calibration

### Problém

Regresní metriky (COMET, BLEURT) produkují desetinná čísla → **nikdy nepredikují tie**. Acc_eq je pak penalizuje, i když jsou jinak dobré. Není to fér.

------

### Základní myšlenka

Intuice: pokud metrika dá překladu A skóre **0.712** a překladu B skóre **0.714**, rozdíl je tak malý, že to **prakticky znamená tie**.

Tie calibration hledá práh **ε** takový, že:

> pokud |m_i - m_j| ≤ ε → považuj to za tie

------

### Jak se ε hledá?

Algoritmus (Algorithm 1) prochází všechny možné hodnoty ε (jsou to přesně všechny rozdíly mezi páry) a vybere ten, který **maximalizuje acc_eq**.

Složitost: O(n² log n) – bottleneck je seřazení všech párů.

------

### Výsledek

| Metrika     | ε*   |
| ----------- | ---- |
| COMET-22    | 0.11 |
| GEMBA-GPT-4 | 4.00 |
| MaTESe      | 0.00 |

GEMBA má ε* = 4.00 protože už sama predikuje ties (škála 1–7), takže velký práh nic nemění. COMET potřebuje ε = 0.11 aby férově soutěžil.

------

### Notace

Výsledná statistika se pak značí $acc_{eq}^*$ (s hvězdičkou) = acc_eq s tie calibration.

------

**Závěr**: Tie calibration umožňuje **férové srovnání** regresních metrik (které ties nepredikují) s LLM metrikami (které ties predikují přirozeně). Jdeme na sekci 8?

---

*Jdeme na sekci 8.*

---

## 8 – Analysis

### 8.1 – Jak volba statistiky mění pořadí metrik (Table 6)

Podívejme se na dva extrémní případy – MaTESe a GEMBA (metriky s mnoha ties):

| Metrika     | τ_b          | τ_10      | acc*_eq      |
| ----------- | ------------ | --------- | ------------ |
| GEMBA-GPT-4 | **1. místo** | 15. místo | 6. místo     |
| MaTESe      | 2. místo     | 16. místo | 4. místo     |
| Metric-X    | 4. místo     | 1. místo  | **1. místo** |

- **τ_b** favorizuje metriky s ties (kvůli NaN problému – hodnotí je na snazší podmnožině)
- **τ_10** naopak metriky s ties brutálně trestá
- **acc\*_eq** dává nejférovější výsledek

------

### 8.2 – Generalizuje ε* napříč datasety?

Klíčová otázka: lze ε* natrénované na jednom datasetu použít na jiném?

- **en→de**: ano, ε* se změní jen o 0.03, acc_eq se změní o 2 % → stabilní
- **zh→en**: ne – WMT'21 má 23 % ties, WMT'22 má 41 % ties → ε* se nepřenáší

**Závěr**: ε* je lepší chápat jako **latentní proměnnou kalibrovanou na aktuálním datasetu**, ne jako univerzální konstantu.

------

### 8.3 – Kde se ties zavádějí?

Ties se nezavádějí rovnoměrně přes celou škálu – ale **převážně pro vysoké skóre** (bezchybné překlady). To dává smysl: Metric-X dává podobná vysoká skóre překladům které jsou oba bezchybné.

------

### 8.4 – Class-specific statistiky (Figure 6)

Pro COMET-22 na en→de:

- **ties F1** je výrazně vyšší než **correct-rank F1**

Tedy metrika je **lepší v predikci ties než v seřazení ne-tied párů**. Opět díky tomu, že většina ties jsou bezchybné překlady s vysokým skóre.

------

**Celkový závěr článku**: acc*_eq je nejférovější meta-evaluační statistika – není NaN, odměňuje správné ties, a tie calibration umožňuje férové srovnání všech typů metrik. Máš otázky, nebo přejdeme k praktické části projektu?

---



