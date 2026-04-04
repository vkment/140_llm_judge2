# judge_templates_locales.py
#
# Locale-specific judge prompt templates.
# Placeholders that MUST be preserved in every translation:
#   {language}  – název jazyka (např. "Czech", "German")
#   {input}     – původní prompt uživatele
#   {response}  – hodnocená odpověď systému
#
# Přidejte překlad jako nový klíč v každém critériu.
# Pokud locale v tomto souboru chybí, get_judge_template() automaticky
# padne zpět na anglický "default".

JUDGE_TEMPLATES = {
    "instruction_following": {
        "default": (
"""You are an LLM judge evaluating instruction following. Score how well the response follows the user's instructions in {language}.

Anchor scores:

7: Flawless — all instructions, details, format, and style followed exactly as requested.
   This score is intentionally rare. Reserve it only for responses a skilled native speaker
   would consider completely indistinguishable from ideal. Any perceivable imperfection
   drops to 6 — do not round up.

6: Very good — main instructions and most details followed. Only the most minor,
   easily overlooked imperfections present. When uncertain between 6 and 7, choose 6.
   This is the appropriate score for responses that are clearly above average but fall
   short of flawless.

5: Good — follows the main instructions. Minor details, formatting nuances, or secondary
   requirements may be missing or slightly off, but the core request is fully addressed.

3: Partial — the response is relevant to the topic but follows only a limited portion of
   the instructions. Important parts are missing or incorrectly handled. The main intent
   is only weakly met.
   Note: if the main intent is met but details are missing, score 5, not 3.

1: Fails — the response ignores the instructions entirely, is off-topic, or is not
   in {language}. Poor quality or missing details alone do not justify score 1.

Intermediate scores (use only when clearly between two anchors):
- 6 = between 7 and 5 (very minor, easily overlooked imperfection)
- 4 = between 5 and 3 (noticeable gaps, but more than partial)
- 2 = between 3 and 1 (very weak; barely relevant)

When uncertain between two candidate scores, choose the lower one.

Prompt: «{input}»
Response: «{response}»

Respond with a single digit only — one of: 1, 2, 3, 4, 5, 6, 7.
Do not add any label, prefix, explanation, or justification.

Score: """
        ),
    },
    "naturalness": {
        "default": (
"""You are an LLM judge evaluating naturalness and fluency. Score how natural and fluent the response reads as {language} text.

Anchor scores:

7: Perfectly natural — fluent throughout like a skilled native speaker.
   This score is intentionally rare. Reserve it only for responses with no awkward
   phrasing, unnatural constructions, or fluency issues of any kind. Any noticeable
   non-native phrasing drops to 6 — do not round up.

6: Very natural — reads naturally overall with only one or two minor non-native
   phrasings that a careful reader might notice. When uncertain between 6 and 7,
   choose 6. This is the appropriate score for responses that are clearly fluent
   but fall short of native-speaker level.

5: Mostly natural — reads naturally overall. Some minor awkward phrasing or
   slightly non-native constructions, but these do not disrupt understanding.

3: Noticeably unnatural — multiple awkward or non-native constructions that require
   some effort to read. The meaning is still recoverable but fluency is clearly impaired.
   Note: if only occasional awkwardness is present, score 5, not 3.

1: Incomprehensible or not in {language} — so unnatural or malformed that the meaning
   cannot be recovered, or the response is not written in {language}.
   Low fluency or frequent errors alone do not justify score 1.

Intermediate scores (use only when clearly between two anchors):
- 6 = between 7 and 5 (one or two minor non-native phrasings; still reads smoothly overall)
- 4 = between 5 and 3 (noticeable unnatural phrasing throughout, but still understandable)
- 2 = between 3 and 1 (very unnatural; meaning barely recoverable)

When uncertain between two candidate scores, choose the lower one.

Prompt: «{input}»
Response: «{response}»

Respond with a single digit only — one of: 1, 2, 3, 4, 5, 6, 7.
Do not add any label, prefix, explanation, or justification.

Score: """
        ),
    },
    "coherence": {
        "default": (
"""You are an LLM judge evaluating logical structure and coherence. Score how well the response is organized and how clearly its ideas connect in {language}.

Anchor scores:

7: Perfect — clear structure, smooth logical flow, seamless transitions throughout.
   This score is intentionally rare. Reserve it only for responses where nothing
   disrupts the flow and a skilled reader would find nothing to improve structurally.
   Any noticeable gap or abrupt transition drops to 6 — do not round up.

6: Very good — well-structured and easy to follow, with only the most minor gaps
   or slightly abrupt transitions. When uncertain between 6 and 7, choose 6.
   This is the appropriate score for responses that are clearly coherent but fall
   short of seamless.

5: Good — generally well-structured and easy to follow. Some minor gaps or slightly
   abrupt transitions, but the overall progression of ideas is clear.
   Note: if ideas are connected but flow is imperfect, score 5, not 3.

3: Weak — relevant ideas are present but poorly connected. The response lacks overall
   flow; multiple noticeable jumps between topics. The reader must make an effort
   to follow the logic.
   Note: if the overall structure is discernible despite weak transitions, score 5, not 3.

1: Incoherent — no clear structure or logical progression. Ideas are disconnected or
   contradictory. Very difficult to identify what the response is trying to convey.
   Poor flow or weak transitions alone do not justify score 1.

Intermediate scores (use only when clearly between two anchors):
- 6 = between 7 and 5 (very minor disruption; one slightly abrupt transition)
- 4 = between 5 and 3 (noticeable gaps in logic, but more than just weak)
- 2 = between 3 and 1 (very weak structure; barely any logical connection)

When uncertain between two candidate scores, choose the lower one.

Prompt: «{input}»
Response: «{response}»

Respond with a single digit only — one of: 1, 2, 3, 4, 5, 6, 7.
Do not add any label, prefix, explanation, or justification.

Score: """
        ),
    },
}


LOCALE_TEMPLATES: dict[str, dict[str, str]] = {
    "instruction_following": {
        "cs_CZ": (
"""Jsi LLM judge hodnotící, jak dobře odpověď splňuje pokyny uživatele. Ohodnoť, nakolik odpověď dodržuje zadané instrukce v češtině.

Kotvové body:

7: Bezchybné — splněn obsah, detaily, formát i styl přesně dle zadání.
   Toto skóre je záměrně vzácné. Vyhraď ho výhradně pro odpovědi, kde zkušený
   rodilý mluvčí nenajde vůbec nic ke zlepšení. Jakékoli vnímatelné pochybení
   snižuje hodnocení na 6 — neskóruj nahoru.

6: Velmi dobré — hlavní instrukce i většina detailů splněna. Přítomny jsou jen
   zcela drobné, snadno přehlédnutelné nedostatky. Při pochybnostech mezi 6 a 7
   zvol 6. Toto je odpovídající skóre pro odpovědi, které jsou zřetelně nadprůměrné,
   ale nedosahují bezchybnosti.

5: Dobré — hlavní požadavek splněn. Drobné detaily, formátovací nuance nebo vedlejší
   požadavky mohou být vynechány nebo mírně odchylné, ale jádro zadání je pokryto.

3: Částečné — odpověď je relevantní k tématu, ale splňuje jen omezenou část instrukcí.
   Důležité části chybějí nebo jsou špatně zpracovány. Hlavní záměr je jen slabě naplněn.
   Pozor: pokud je hlavní záměr splněn a chybějí jen detaily, hodnoť 5, ne 3.

1: Selhání — odpověď ignoruje instrukce, je mimo téma nebo není v češtině.
   Samotná nízká kvalita ani chybějící detaily neodůvodňují skóre 1.

Přechodná skóre (použij jen tehdy, když jde jednoznačně o mezipolohu):
- 6 = mezi 7 a 5 (velmi drobné, snadno přehlédnutelné pochybení)
- 4 = mezi 5 a 3 (výrazné mezery, ale více než jen částečné splnění)
- 2 = mezi 3 a 1 (stěží relevantní)

Při pochybnostech mezi dvěma kandidátními skóre zvol nižší.

Prompt: «{input}»
Odpověď: «{response}»

Odpověz jediným číslicí — jednou z: 1, 2, 3, 4, 5, 6, 7.
Nepřidávej žádný popis, předponu, vysvětlení ani odůvodnění.

Skóre: """
        ),
        # ostatní lokály zatím prázdné — fallback na default
        "de_DE": (""),
        "ar_EG": (""),
        "bn_BD": (""),
        "hi_IN": (""),
        "id_ID": (""),
        "ja_JP": (""),
        "ru_RU": (""),
        "zh_CN": (""),
    },
    "naturalness": {
        "cs_CZ": (
"""Jsi LLM judge hodnotící přirozenost a plynulost textu. Ohodnoť, jak přirozeně a plynně odpověď zní jako český text.

Kotvové body:

7: Dokonale přirozené — plynné po celou dobu, jako by text napsal zkušený rodilý mluvčí.
   Toto skóre je záměrně vzácné. Vyhraď ho výhradně pro odpovědi zcela prosté
   neobratných formulací nebo nepřirozených konstrukcí. Jakákoli znatelná
   nepřirozenost snižuje hodnocení na 6 — neskóruj nahoru.

6: Velmi přirozené — celkově přirozené, jen jedna nebo dvě drobné neobratné formulace,
   kterých by si pozorný čtenář mohl povšimnout. Při pochybnostech mezi 6 a 7 zvol 6.
   Toto je odpovídající skóre pro odpovědi, které jsou zřetelně plynné, ale nedosahují
   úrovně rodilého mluvčího.

5: Převážně přirozené — celkově působí přirozeně. Vyskytuje se několik drobně
   neobratných nebo mírně nepřirozených formulací, které však nenarušují porozumění.

3: Znatelně nepřirozené — více neobratných nebo nepřirozených konstrukcí, jejichž
   čtení vyžaduje určité úsilí. Smysl je stále srozumitelný, ale plynulost je
   zřetelně narušena.
   Pozor: pokud jde jen o příležitostnou neobratnost, hodnoť 5, ne 3.

1: Nesrozumitelné nebo není v češtině — natolik nepřirozené nebo deformované, že smysl
   nelze vyčíst, nebo odpověď není napsána česky.
   Samotná nízká plynulost ani časté chyby neodůvodňují skóre 1.

Přechodná skóre (použij jen tehdy, když jde jednoznačně o mezipolohu):
- 6 = mezi 7 a 5 (jedna nebo dvě drobné nepřirozené formulace; celkově stále plynné)
- 4 = mezi 5 a 3 (nepřirozené formulace prostupují celým textem, ale stále srozumitelné)
- 2 = mezi 3 a 1 (velmi nepřirozené; smysl stěží dešifrovatelný)

Při pochybnostech mezi dvěma kandidátními skóre zvol nižší.

Prompt: «{input}»
Odpověď: «{response}»

Odpověz jediným číslicí — jednou z: 1, 2, 3, 4, 5, 6, 7.
Nepřidávej žádný popis, předponu, vysvětlení ani odůvodnění.

Skóre: """
        ),
        "de_DE": (""),
        "ar_EG": (""),
        "bn_BD": (""),
        "hi_IN": (""),
        "id_ID": (""),
        "ja_JP": (""),
        "ru_RU": (""),
        "zh_CN": (""),
    },
    "coherence": {
        "cs_CZ": (
"""Jsi LLM judge hodnotící logickou strukturu a koherenci textu. Ohodnoť, jak dobře je odpověď organizována a jak jasně na sebe myšlenky navazují v češtině.

Kotvové body:

7: Dokonalé — jasná struktura, hladký logický tok, bezešvé přechody po celou dobu.
   Toto skóre je záměrně vzácné. Vyhraď ho výhradně pro odpovědi, kde nic nepřerušuje
   tok myšlenek a zkušený čtenář by nenašel žádné strukturální výhrady. Jakákoli
   znatelná mezera nebo náhlý přechod snižuje hodnocení na 6 — neskóruj nahoru.

6: Velmi dobré — dobře strukturované a snadno sledovatelné, jen s naprosto drobnými
   mezerami nebo mírně náhlými přechody. Při pochybnostech mezi 6 a 7 zvol 6.
   Toto je odpovídající skóre pro odpovědi, které jsou zřetelně koherentní,
   ale nedosahují bezešvé plynulosti.

5: Dobré — celkově dobře strukturované a srozumitelné. Drobné mezery nebo mírně
   náhlé přechody se mohou vyskytnout, ale celkový průběh myšlenek je zřetelný.
   Pozor: pokud jsou myšlenky propojeny, jen tok není dokonalý, hodnoť 5, ne 3.

3: Slabé — relevantní myšlenky jsou přítomny, ale špatně propojeny. Odpověď postrádá
   celkový tok; více znatelných skoků mezi tématy. Čtenář musí vynaložit úsilí,
   aby logiku sledoval.
   Pozor: pokud je celková struktura přes slabé přechody rozpoznatelná, hodnoť 5, ne 3.

1: Nekoherentní — žádná zřetelná struktura ani logická posloupnost. Myšlenky jsou
   odpojené nebo si odporují. Velmi obtížné určit, co odpověď vůbec sděluje.
   Samotný slabý tok nebo slabé přechody neodůvodňují skóre 1.

Přechodná skóre (použij jen tehdy, když jde jednoznačně o mezipolohu):
- 6 = mezi 7 a 5 (velmi drobné narušení; jeden mírně náhlý přechod)
- 4 = mezi 5 a 3 (znatelné logické mezery, ale více než jen slabé propojení)
- 2 = mezi 3 a 1 (velmi slabá struktura; stěží jakékoli logické spojení)

Při pochybnostech mezi dvěma kandidátními skóre zvol nižší.

Prompt: «{input}»
Odpověď: «{response}»

Odpověz jediným číslicí — jednou z: 1, 2, 3, 4, 5, 6, 7.
Nepřidávej žádný popis, předponu, vysvětlení ani odůvodnění.

Skóre: """
        ),
        "de_DE": (""),
        "ar_EG": (""),
        "bn_BD": (""),
        "hi_IN": (""),
        "id_ID": (""),
        "ja_JP": (""),
        "ru_RU": (""),
        "zh_CN": (""),
    },
}