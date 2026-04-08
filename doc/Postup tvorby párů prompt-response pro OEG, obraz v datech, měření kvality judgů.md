# Postup tvorby párů prompt-response pro OEG, obraz v datech, měření kvality judgů

## 1. Postup tvorby dat podle studie Kocmi

Autoři (WMT 2025) navrhli v angličtině řádově jednu stovku **promptů** (Kocmi, p. 464, odst. *English question creation*) rámcově následných druhů: brainstorming, creative, informational, professional (Kocmi, tab. 3). Všechny přitom spadaly do kategorie OEG, tj. generování s otevřeným koncem.

Prompty mohly obsahovat placeholdery, aby byl jasný překladový záměr, např.: *"Please suggest an idiom in {language}"*. Tyto promptové otázky/instrukce byly přeloženy do dalších jazyků, jež se spojují i s určitými zeměmi a souhrnně jsou v článku označovány jako *locale* (později v datech má locale kód např. *cs_CZ* pro češtinu v ČR, nebo *en_US* pro angličtinu v USA). Pro překlad do každého locale se používala 5 kroková procedura (Kocmi, p. 464-465), důležité je, že v posledním kroku byly podrobeny i lidské korektuře rodilými mluvčími. Cílem bylo, aby prompty byly jazykově bezvadné, bez reziduí ze strojového překladu aj. nedokonalostí. Současně cílem bylo, aby překlad každého promptu *mutatis mutandi* (rozvinutí placehoderů) vyjadřoval stejný požadavek, tedy ve smyslu ideálně srovnatelného požadavku.

Na počátku byl sice pokus o překlad do 19 locales (Kocmi, tab. 3), ale výsledně (Kocmi, posl. věta v odst. 2.5) se z důvodu nedostupnosti lidských soudců pro studii i zpracování využily jen překlady do **10 locales**.

Další krok asi není ve článku pro případ OEG explicitně zmíněn, ale zřejmě se prompty, postupně ve všech locale, vždy předložily sadě OEG-LLM-systémů. Těchto systémů bylo původně 20 (Kocmi, tab. 3), ale z důvodu nevyhovující kvality jich výsledně bylo využito **jen 16**. Tyto systémy vždy vytvořily pro každý takový svůj vstup jeden výstup, tj. odpověď (response). 
Jednalo se o SOTA systémy (Claude-4, GPT-4), blízko SOTA (Qwen3-235B, CommandA, Mistral-Medium, Gemini-2), velké open weight modely (DeepSeek-V3, Llama-4-Maverick), střední open weight (AyaExpanse-32B, Gemma-3-12B) a malé open weight (CommandR7B, AyaExpanse-8B, Qwen2, Mistral-7B, Llama-3). Povědomost o těchto systémech a různosti jejich kvality je užitečná ze dvou důvodů. Jednak výkonnost těchto modelů v různých locale bude velmi různá. Na rozdíl od promptů je příležitostná imperfektnost generované odpovědi žádoucí vlastnost, aby v následující úloze (LLM-as-a-judge) měli soudci co rozlišovat, tj. mohli prokázat, že dokáží odlišit špatné odpovědi od dobrých. Tyto generované odpovědi proto žádnou další jazykovou úpravou neprocházely, zřejmě byly ponechány i včetně formátování (např. HTML tagy atp.). Druhý důvod potřeby povědomosti o těchto systémech je v tom, že pro rozlišování **odpovědí** se používají  řetězce názvů těch systémů, které je vytvořily (dalo by se použít i rozlišování jakékoliv jiné, ale možná s ohledem na stopování zdroje tvorby jsou jako tzv.  `submission_system_name`  **odpovědi** referencovány těmito identifikátory, tedy např. `Claude-4` nebo  `Gemma-3-12B`). 

Takto vytvořená a připravená data budou využita vícenásobně. Hodnocení požadované od soudců bude modifikované do tří verzí: `instruction_following` (plnění pokynů), `naturalness` (jazyková přirozenost) a `coherence` (koherence), podrobně jsou prompty v příloze B (Kocmi, tab. 15, p. 479). Toto rozlišení je zváno v článku *rubric*, v datech pak jako *criterion*. Použité zastřešující šablony opět využívají placeholdery, kromě {language} zejména {input} a {response}. Do input se vkládá prompt v překladu do locale,  response odpověď některého ze submission_system ve stejném locale. Souhrnně lze říci, že každá jedna úloha je z výše uvedených dat jednoznačně určená čtveřicí:

criterion - prompt - locale - response

Z toho criterion je reprezentovaný zastřešující šablonou z přílohy B, locale znamená zúžení jen na některý jazyk, prompt-response jsou k sobě náležející páry textů z daného jazyka. Jelikož na stejný prompt je k dispozici v každém jazyce odpověď ze 16 systémů, bude prompt 16x shodný a se změnami odpovědi. 

Výše uvedenou čtveřici můžeme informaticky přirozeněji potom chápat takto:

criterion - locale - prompt - response

Criterion přitom řídí hlavní zastřešující otázku na soudce. Locale je aktuální jazyk, který se může mírně projevit i v textu criterion (šablona obsahuje např. *"...answer is not in {language}."*) a určuje i jazyk textů pro prompt a response. Prompt i response jsou konkrétní řetězce textů. Zajímavé je, že text šablon criterion se dle článku nepřekládal, tj. soudci si museli poradit s heteronymním textem, kdy zastřešující pokyn je vždy v angličtině, zatímco prompt a response v jazyce daného locale (v 9 ze 10 případů jím není angličtina). 

V průběhu činností s uvedenými texty se zjistilo, že na některé prompty aspoň některé LLM generátory generovaly nevhodné odpovědi (např. příliš dlouhé pro evaluaci malými modely), pročež počet promptů byl zpětně zúžen. Článek v závěru (Kocmi, p. 469) uvádí, i z předaných dat plyne, že **promptů** bylo výsledně využito**pouze 46**.

#### Lidská hodnocení

Pro takto vytvořené úlohy: 

> instrukce_criterion - prompt_v_locale - response_v_locale

lidští soudci provedli svá vlastní lidská hodnocení. 

Jelikož dimenze jsou:

> instruction (3) - locale (10) - prompt (46) - response (16)

3 x 10 x 46 x 16 = **22080 celkem úloh**, tj. na každé *locale* se jednalo o 2208 úloh. Pro češtinu je např. indikována účast tří různých lidských soudců (hodnotitelů, raters). Soudci mají známkovat jak dobře *response* reaguje na *prompt* (obojí v *locale*) vzhledem ke *criterion*, a to na Likertově škále (7-6-5-4-3-2-1), kde 7 je perfektní výkon a 1 úplné selhání. Podrobnosti ke škále jsou vyjádřeny v šablonách (Kocmi, příloha B).

Lidská hodnocení jsou pro studii i jí nabízený benchmark naprosto klíčová, představují "zlatý standard" kvality, vůči nimž se výkon LLM-soudců následně poměřuje.

#### LLM hodnocení

LLM-soudci hodnotí zcela stejné úlohy:

> instrukce_criterion - prompt_v_locale - response_v_locale

nanejvýš je text prompt_v_locale a text response_v_locale vtažen přímo do textu instrukce_criterion (analogie *include*), tj. LLM jako vstup má plně rozvinutou instrukce_criterion_s_prompt_a_response, odpovídá na výstupu zpravidla zejména číselným hodnocením, na stejné Likertově škále (7-6-5-4-3-2-1).

LLM-soudci mohou též hodnotit plnou sadu všech 22080 úloh. Pokud se provádí ladění dílčí funkce, může pro rychlejší běh být smysluplné zúžit se na některou podmnožinu úloh, např. jen na některé locale, na některé criterion, v podstatě jakkoliv, pokud to je účelné.

Dle předaných dat bylo **ve studii** pro **OEG souzení** použito **13 LLM-soudců:**

- Llama-4-Maverick
- DeepSeek-V3
- CommandA
- GPT-4.1
- AyaExpanse-8B
- Llama-3.1-8B
- CommandR7B
- Claude-4
- AyaExpanse-32B
- Mistral-Medium
- Qwen3-235B
- Mistral-7B
- Qwen2.5-7B

Jde spíše záležitost časového souběhu existence těchto LLM systémů, že tytéž systémy se výše používaly i při vytváření response na prompty. Čistě teoreticky by response mohly být vytvořeny jinak, jinými systémy, nebo bez použití systémů vůbec. 

Silný překryv má ten důsledek, že narazí-li se v článku nebo v datech na název systému, je třeba zhodnotit, zda jde o výskyt systému při vytváření dat v počáteční fázi tvorby response (jednorázová činnost), anebo o cílové hodnocení LLM-soudce (pro každý hodnotící systém se provádí znovu). 

Každý zmíněný LLM-soudce tedy vytvořil hodnocení pro stejných **22080 úloh**.

## 2. Obraz součástí v předaných datech

Čtyři hlavní součásti konstrukce zadání mají v předaných datech následující označení:

- kritérium, rubrika - **`criterion`** (`instruction_following`, `naturalness`, `coherence`)
  - samotný text šablon je v příloze B článku, jakož i v souboru `judge_utils.py`

- prompt - **`original_instance_id`** nebo **`doc_id`** (haš hodnota, 32 hexa znaků)☨
  - samotný text promptu v locale -  **`prompt`**
- response - **`submission_system_name`**
  - samotný text response v locale - **`response`**
- jazyk + země - **`locale`**

☨ *haš-hodnota odkazuje abstraktně k původnímu promptu v angličtině, tj. i po překladu do všech locale bude v rámci těchto hodnot jediná původní haš jako jednoznačné pojítko napříč locales.*

#### Lidská hodnocení

Jsou především obsažena v souboru:

**`oeg_human_eval_data.csv`**

- `judge_model_name`: vždy "human", zde pouze lidská hodnocení
- `criterion`: zastřešující úloha hodnocení (`instruction_following`, `naturalness`, `coherence`)
- `submission_system_name`: identifikace **response** názvem toho systému, který response vytvářel 
- `original_instance_id`: identifikace **promptu** (haš hodnota)
- `locale`: jazyk a země (`ja_JP`, `de_DE`, `id_ID`, `ru_RU`, `en_US`, `hi_IN`, `zh_CN`,  `cs_CZ`, `ar_EG`, `bn_BD`)
- `score`: lidské **hodnocení** na Likertově škále `7.0`, `6.0`, `5.0`, `4.0`, `3.0`, `2.0` nebo `1.0`

Datových záznamů je **22080**. (3 x 10 x 46 x 16)

*Pozn.: Lidská hodnocení jsou zřejmě redundantně i v souborech `oeg_human_eval_raw_data/*.csv`.*

#### Hodnocení od LLM-soudců (ve studii dle článku Kocmi)

**`oeg_judge_run2_submission_data.csv`**

- `judge_model_name`: název LLM-soudce (např. Llama-4-Maverick nebo DeepSeek-V3)
- `criterion`: zastřešující úloha hodnocení (`instruction_following`, `naturalness`, `coherence`)
- `submission_system_name`: identifikace **response** názvem toho systému, který response vytvářel 
- `original_instance_id`: identifikace **promptu** (haš hodnota)
- `locale`: jazyk a země (`ja_JP`, `de_DE`, `id_ID`, `ru_RU`, `en_US`, `hi_IN`, `zh_CN`,  `cs_CZ`, `ar_EG`, `bn_BD`)
- `score`: **hodnocení** na Likertově škále od toho LLM-soudce, který je určen v poli `judge_model_name` výše, hodnota jedna z:   `7.0`, `6.0`, `5.0`, `4.0`, `3.0`, `2.0` nebo `1.0`

Datových záznamů je **293280**. Toto číslo je vytvořeno:

criterion (3) - locale (10) - prompt (**47**) - response (16) - judge_model_name (13) 

= 3 * 10 * 47 * 16 * 13 = **293280**.

*Pozn.: v tomto souboru jsou oproti souboru s lidskými hodnoceními záznamy i pro jeden prompt (s haší `41195c6e58c3dc54bd51d9462c2a1a35`) navíc. Při vyhodnocování je třeba tyto záznamy ignorovat, což se v předaném programu `judge_human_agreement.py` i děje. Obsahuje explicitní filtr, který záznamy zúží jen na ty, kterou jsou v obou souborech. Všechny ostatní záznamy mají sobě přesně odpovídajících **46 promptů**.*

#### Texty promptů a odpovědí v locales

v souborech **`oeg_human_eval_raw_data/*.csv`**.

- `system`: reference odpovědi názvem systému LLM, který ji vytvořil
- `prompt`: text promptu v jazyce dle language_locale
- `response`: text response v jazyce dle language_locale 
- `doc_id`: haš na originální prompt
- `language_locale`: jazyk a země (dáno duplicitně i názvem souboru *.csv)
- `coherence`: skóre 1.0 až 7.0 pro criterion=coherence, asi lidského soudce rater 
- `naturalness`: skóre 1.0 až 7.0  pro criterion=naturalness, asi lidského soudce rater 
- `instruction_following`: skóre  1.0 až 7.0 pro criterion=instruction_following, asi lidského soudce rater 
- `mean_score`: průměr tří skóre výše, desetinné číslo
- `rater`: identifikátor lidského hodnotitele, např. 'rater3_de_DE'

Počet datových záznamů v každém souboru je **736** (46 x 16), tři locale jsou předpokládány implicitně.

#### Implikovaná rámcová vhodná implementace LLM inference

Vhodná implementace LLM-soudce pro nový LLM-systém zřejmě projde cyklem soubory **`oeg_human_eval_raw_data/*.csv`**, použije zastřešující šablony z přílohy B pro různé *criterion*, a z každého řádku pro daný `language_locale` získá text `prompt` a text `response`.

Výsledek hodnocení LLM-soudcem se ideálně zapíše do souboru stejné struktury jako má soubor **`oeg_judge_run2_submission_data.csv`**, kde budou vždy po sobě 3 různé řádky (pro 3 různá *criterion*) pro jeden řádek dle struktury souboru výše, kde:

- `judge_model_name`: název LLM-soudce, jehož inference se právě provádí
- `criterion`: právě provedená úloha hodnocení (`instruction_following`, `naturalness`, `coherence`)
- `submission_system_name`: identifikace **response** názvem toho systému, který response vytvářel, přebere se z pole `system` 
- `original_instance_id`: identifikace **promptu** (haš hodnota), přebere se z pole `doc_id`.
- `locale`: jazyk a země, přebere se z pole `language_locale`
- `score`: skóre 1.0 až 7.0 poskytnuté LLM-soudcem, vlastní výsledek inference

Udržení této struktury je výhodné z hlediska udržení přehlednosti, jakož i možnosti využít poskytnutý software pro výpočty kvality LLM-soudců.

## 3. Metody měření kvality LLM-soudců

Článek Kocmi se metodikami zabývá v odst. 4.5 (p. 471-472) a volí dvě metriky:

- ***pairwise accuracy***
- ***group-by-item pairwise accuracy with ties*** $acc_{eq}$

Obě metriky jsou podrobněji popsány v článku Deutsch et al (2023). 

### $acc_{eq}$

V Kocmi se považuje za významnější zřejmě druhá metrika, která spočívá především na tom nápadě, že se nepoměřují absolutní skóre LLM-soudce vůči absolutnímu skóre lidského soudce, ale že:

- data se rozřežou na menší vzájemně disjunktní skupiny, každá seskupená jako group-by-item
- uvnitř skupiny existuje pro každý exemplář jak skóre LLM-soudce, tak referenční skóre lidského soudce, 
- z exemplářů uvnitř skupiny se vytvoří všechny možné kombinace (dle kombinatoriky) párů exemplářů, pro každý pár se pak:
  - hodnotí se zda hodnoty lidské jsou stejně uspořádané jako hodnoty daného LLM-soudce,
  - za správné se považují i remízy, pokud nastávají u lidských hodnocení i u LLM-soudce současně.

Formálněji zapsáno, projdou se všechny dvojice pozic `i < j` z 16 systémů (tj. všechny páry kombinace) referencující odpovědi a počítají se:

- `C` = concordant pairs

- `D` = discordant pairs

- `T_h` = tie jen u human

- `T_m` = tie jen u judge

- `T_hm` = tie u obou

Pak se spočte
$$
acc\_eq = \frac{C + T_{hm}}{C + D + T_h + T_m + T_{hm}}
$$
tj:

- správně je i shoda (*concordance*) v pořadí,
- i shoda v remíze (*tie*, je-li ovšem u lidského soudce i u LLM-soudce současně)

Takto pojatá metrika má **mnohé příznivé vlastnosti**:

- invariantní na monotónní transformace (odolnost proti ofsetům), dokud jsou zachovány relace `<`, `>`, `=`,
- přirozené započtení remíz, zejména hrubé škály (1-7) je mají časté,
- lokální hodnocení po jednotlivých itemech, průměruje se až poté, omezuje vliv globálních posunů mezi locale či criterion,
- soustřeďuje se na „rozlišit lepší vs. horší odpovědi v rámci stejného promptu“ - klíčová vlastnost judge,
- dobrá granularita ze 120 párů exemplářů z 16-exemplářové skupinu, krok 1/120; při agregaci průměrováním ze 46 promptů se citlivost zvyšuje až k $\Delta = \frac{1}{46 \cdot 120} = \frac{1}{5520} \approx 0.000181$
- symetrie člověk - LLM, může tedy zmírnit dopad neideální "kalibrace" i lidského soudce, dokud stejný hodnotí celou skupinu; rozhoduje pouze relativní uspořádání odpovědí v rámci stejné skupiny.

Pro pochopení je klíčové vyložit, že enigmatická formulace *«an “item” refers to an input prompt requiring an output in a specific language»* (Kocmi, p. 472) znamená, že jedna group-by-item představuje ve studii Kocmi 16-dimenzionální vektor, jehož hodnoty jsou skóre.

Přitom hodnocení jsou sesbírána ze skóre pro úlohy dané vždy kombinací **pevně třemi základními částmi** (tj. '*an item*' je tvořená z):

- criterion - locale - prompt 

  a **se 16 proměnlivými odpověďmi** (pocházejícími ze systémů, které je i identifikují)

  - response 0 : skóre 1-7 na pozici 0,
  - response 1 : skóre 1-7 na pozici 1,
  - ...
  - response 15: skóre 1-7 na pozici 15,

z nichž každá od LLM-soudce obdrží vlastní skóre 1-7 (v rámci daného criterion + locale + promptu a dané odpovědi).

Odpovědi  ve vektoru musí být seřazeny vždy shodně podle svých původců (`submission_system_name`), zejména proto, aby byla srovnávána skóre stejných odpovědí u lidských i LLM soudců.

Shlukovat hodnocení právě takto má dobrý smysl, neboť se jedná o totožnou úlohu (danou *criterion*, a dále vyjádřenou stejným *promptem* v daném jednom *locale*), pro níž se pouze proměňuje *response* (též v daném *locale*). Uvedené představuje koncentraci různosti právě a jen na různost odpovědí pro jinak zcela shodné podmínky. Různým odpovědím pochopitelně může odpovídat různost hodnocení skórem.

Výše uvedená interpretace se však nejeví jako snadná jen ze znění studie Kocmi, ani z článku Deutsch et al. 

Interpretace byla získána zpětným inženýrstvím souboru **`judge_human_agreement.py`** a dobrý smysl byl shledán až následně. Soubor tímto programem vytvořený, `oeg_judge_human_agreement_results.json` má až na pořadí položek shodný obsah jako soubor `/wmt-mist/data/humeval_aggregated/judge_oeg.json` z githubu studie Kocmi ([github.com/wmt-conference/wmt-mist]()). Tato rovnost umožňuje dovodit, že i ve studii Kocmi pracovali se stejným pojetím *item* a zřejmě i používali shodný algoritmus výpočtu nebo jeho realizace v Pythonu.

Metrika acc_eq může teoreticky nabývat hodnot v intervalu ⟨0, 1⟩. Za pozornost stojí, že v článcích Deutsch et al ani ve studii Kocmi (2025) se nestuduje problematika toho, zda a jaká úroveň acc_eq odpovídá náhodnému soudci, jaká by byla jeho baseline. Oba články implicitně předpokládají, že vyšší acc_eq je lepší, ale nezkoumá se, jak daleko je od náhody.

### pairwise accuracy

V  **`judge_human_agreement.py`** je vedena pod označením **`ranking_accuracy`**. Jde o první hlavní výstup. Metrika nepracuje po jednotlivých promptech, ale na systémové úrovni. Program:

- pro soudce *human* spočte průměrné skóre každého `submission_system_name` přes celý dataset,
  - z toho vytvoří pořadí 16 systémů, které vytvářely odpovědi, tedy jak kvalitní se odpovědi (a potažmo systémy je vytvářející) jevily lidským soudcům, 
- totéž provede pro každého jednoho *LLM-soudce* (`judge_model_name`), tedy zjistí pořadí stejných `submission_system_name` přes celý dataset.

Výsledně se obě pořadí srovnají metrikou `my_pairwise_acc`., tj.:

> jak dobře se shoduje globální pořadí 16 systémů (poskytnuvších odpovědi) podle **LLM-soudce** s globálním pořadím 16 systémů (poskytnuvších odpovědi) podle **lidských soudců**. 

V „pořadí“ jsou fakticky neprve **oba prvky současně**:

1. názvy systémů (`submission_system_name`),
2. jejich **průměrná skóre přes celý dataset**.

Názvy slouží jako nosič identity, průměrná skóre jsou to, dle čeho se pořadí vytvoří. 

Ve výsledném pořadí již skóre nevystupuje, ale jde o přiřazení pořadí/ranků ke jménům systémů.  Kocmi et al přitom předpokládají, že v takto počítaných skóre za celý dataset nebudou prakticky žádné remízy (p. 471), tudíž metrika pro pořadí může problematiku remíz ignorovat.

Funkce`my_pairwise_acc` poté obdrží dvě stejně dlouhá pole ranků (zde se jedná o ranky, ne skóre):

- `rank_human`
- `rank_metric` 

Každá pozice v obou polích odpovídá stejnému systému, protože program předtím kontroluje, že pořadí jmen systémů v obou seznamech souhlasí.

Pak funkce projde opět všechny páry systémů `(i, j)` [opět jen kombinace, tj. s $i < j$] a dívá se, zda relativní pořadí mezi nimi je stejné:

- když human i LLM-soudce říkají „i je lepší než j“, jde o **concordant pair** → `C += 1`
- když human i LLM-soudce říkají „j je lepší než i“, také **concordant** → `C += 1`
- když jdou směry proti sobě, jde o **discordant pair** → `D += 1` 

Pak `my_pairwise_acc` vrátí
$$
\text{pairwise\_acc} = \frac{C}{C+D}
$$
tedy:

> z párů, kde bylo možné porovnat pořadí, jaký podíl párů měl judge ve stejném směru jako human.

*Poznámka: pokud jsou dva systémy v tie (ať u lidského soudce nebo u LLM-soudce, nebo u obou), tak takový pár se do `my_pairwise_acc` vůbec nezapočítá, nevznikne ani `C`, ani `D`. Jelikož remízy mají být vzácné, vynechání nebude činit ani valnou výpočetní nepřesnost.*

Metrika se tedy liší od výše uvedené acc_eq ve více aspektech. Ignoruje remízy, počítá se z ranků a nikoliv ze skóre, a ranky vzešly z průměrného skóre přes celý dataset. Proto se jedná o metriku „system-level“, která nepracuje s drobnými skupinami vzniklými na úrovni jednotlivých promptů (s *locale* a *criterion*), ale s jedním globálním leaderboardem 16 systémů. Těchto 16 systémů vytvořilo "odpovědní LLM soustavy" v datasetu a metrika informuje o tom, jak dalece se lidské hodnocení různých odpovědních LLM soustav shoduje s hodnocením stejných soustav u konkrétního LLM-soudce. 

U  **`ranking_accuracy`** není přesně dána jemnost kroku, závisí na počtu remíz. V nejjemnějším případě, který ale může být běžný, bude mít krok 1/120. Metrika `ranking_accuracy` má pro náhodného soudce očekávanou hodnotu přibližně 0.5, protože u každé porovnávané dvojice systémů je pravděpodobnost správného určení pořadí rovna 50 % (Kocmi, p. 472). Teoreticky sice může nabývat hodnot v intervalu ⟨0, 1⟩, reálné systémy LLM-soudců by ale měly poskytovat výsledky zhruba od ~0.5 do 1.0, kdy spodní baseline odpovídá náhodě.

## Reference

- Deutsch et al. (EMNLP 2023): defines meta-evaluation metrics used here (including `acc_eq`, `tau_eq`, etc.).
    - https://aclanthology.org/2023.emnlp-main.798.pdf
- Kocmi et al. (WMT 2025): defines the WMT MIST 2025 data/task setup used for this project.
    - https://aclanthology.org/2025.wmt-1.23.pdf