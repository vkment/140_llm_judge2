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


# Judge prompt templates
JUDGE_TEMPLATES = {
    "instruction_following": {
        "default": (
"""You are an LLM judge evaluating instruction following. Score how well the response follows the user's instructions in {language}.

Anchor scores:

7: Perfect — follows all instructions, all details, format, and style as requested.
   Reserve 7 for responses with nothing to improve. Any minor omission or deviation drops to 6.

5: Good — follows the main instructions. Minor details, formatting nuances, or secondary
   requirements may be missing or slightly off, but the core request is fully addressed.

3: Partial — the response is relevant to the topic but follows only a limited portion of
   the instructions. Important parts are missing or incorrectly handled. The main intent
   is only weakly met.
   Note: if the main intent is met but details are missing, score 5, not 3.

1: Fails — the response ignores the instructions entirely, is off-topic, or is not
   in {language}. Poor quality or missing details alone do not justify score 1.

Intermediate scores (use only when clearly between two anchors):
- 6 = between 7 and 5 (very minor omission or deviation)
- 4 = between 5 and 3 (noticeable gaps, but more than partial)
- 2 = between 3 and 1 (very weak; barely relevant)

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

7: Perfectly natural — fluent like a skilled native speaker throughout.
   Reserve 7 for responses with no awkward phrasing, unnatural constructions, or
   fluency issues of any kind. Any noticeable non-native phrasing drops to 6.

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
   Reserve 7 for responses where nothing disrupts the flow. Any noticeable gap or
   abrupt transition drops to 6.

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
        # --- cs_CZ ---
        "cs_CZ": (
            # TODO: sem vložte překlad
"""Jsi LLM soudce hodnotící plnění pokynů. Ohodnoť, jak dobře odpověď dodržuje instrukce uživatele v češtině.

Kotvy pro hodnocení:

7: Perfektní — splňuje všechny pokyny, detaily, formát i styl. 
   Tuto známku dej jen odpovědím, kterým nelze nic vytknout. Jakékoli drobné opomenutí znamená pokles na 6.

5: Dobré — plní hlavní pokyny. Vedlejší detaily nebo nuance formátování 
   mohou chybět, ale jádro požadavku je plně vyřešeno.

3: Částečné — odpověď je k tématu, ale plní jen omezenou část pokynů. 
   Důležité části chybí nebo jsou špatně. Hlavní záměr je splněn jen slabě.
   Poznámka: pokud je hlavní záměr splněn, ale chybí detaily, dej 5, ne 3.

1: Selhání — odpověď ignoruje instrukce, jde mimo téma nebo není 
   v češtině. Samotná nízká kvalita nebo chybějící detaily nestačí pro skóre 1.

Mezistupně (použij jen při stavu jasně mezi kotvami):
- 6 = mezi 7 a 5 (velmi drobné opomenutí)
- 4 = mezi 5 a 3 (znatelné mezery, ale víc než částečné)
- 2 = mezi 3 a 1 (velmi slabé; sotva relevantní)

Prompt: «{input}»
Response: «{response}»

Odpověz pouze jednou číslicí: 1, 2, 3, 4, 5, 6, 7.
Nepřidávej žádné vysvětlení ani okecávání.

Skóre: """
        ),
        # --- de_DE ---
        "de_DE": (
            ""
        ),
        # --- ar_EG ---
        "ar_EG": (
            ""
        ),
        # --- bn_BD ---
        "bn_BD": (
            ""
        ),
        # --- hi_IN ---
        "hi_IN": (
            ""
        ),
        # --- id_ID ---
        "id_ID": (
            ""
        ),
        # --- ja_JP ---
        "ja_JP": (
            ""
        ),
        # --- ru_RU ---
        "ru_RU": (
            ""
        ),
        # --- zh_CN ---
        "zh_CN": (
            ""
        ),
    },
    "naturalness": {
        # --- cs_CZ ---
        "cs_CZ": (
            # TODO: sem vložte překlad
"""Jsi LLM soudce hodnotící přirozenost a plynulost vyjádření. Ohodnoť, jak přirozeně a plynule zní text odpovědi v češtině.

Kotvy pro hodnocení:

7: Zcela přirozené — text zní celou dobu plynule jako od rodilého mluvčího. 
   Rezervuj pro odpovědi bez krkolomných vazeb a nepřirozených konstrukcí. 
   Jakýkoli náznak "strojovosti" znamená pokles na 6.

5: Většinou přirozené — celkově působí přirozeně. Objevují se drobné neobratnosti, 
   které ale nenarušují srozumitelnost.

3: Zřetelně nepřirozené — více neobratných nebo cizorodých konstrukcí, které vyžadují 
   úsilí při čtení. Význam lze pochopit, ale plynulost je jasně narušena.
   Poznámka: pokud je neobratnost jen občasná, dej 5, ne 3.

1: Nesrozumitelné nebo není v češtině — tak zkomolené, že nelze pochopit význam. 
   Samotná nízká plynulost nebo časté chyby nestačí pro skóre 1.

Mezistupně (použij jen při stavu jasně mezi kotvami):
- 6 = mezi 7 a 5 (jedna nebo dvě drobné chyby; stále působí plynule)
- 4 = mezi 5 a 3 (znatelně nepřirozené v celém textu, ale srozumitelné)
- 2 = mezi 3 a 1 (velmi nepřirozené; význam je sotva zachytitelný)

Prompt: «{input}»
Response: «{response}»

Odpověz pouze jednou číslicí: 1, 2, 3, 4, 5, 6, 7.
Nepřidávej žádné vysvětlení ani okecávání.

Skóre: """
        ),
        # --- de_DE ---
        "de_DE": (
            ""
        ),
        # --- ar_EG ---
        "ar_EG": (
            ""
        ),
        # --- bn_BD ---
        "bn_BD": (
            ""
        ),
        # --- hi_IN ---
        "hi_IN": (
            ""
        ),
        # --- id_ID ---
        "id_ID": (
            ""
        ),
        # --- ja_JP ---
        "ja_JP": (
            ""
        ),
        # --- ru_RU ---
        "ru_RU": (
            ""
        ),
        # --- zh_CN ---
        "zh_CN": (
            ""
        ),    
    },
    "coherence": {
        # --- cs_CZ ---
        "cs_CZ": (
            # TODO: sem vložte překlad
"""Jsi LLM soudce hodnotící logickou strukturu a koherenci. Ohodnoť, jak dobře je odpověď organizovaná a jak jasně na sebe myšlenky navazují, v jazyce češtiny.

Kotvy pro hodnocení:

7: Perfektní — jasná struktura, hladký logický tok, bezproblémové přechody. 
   Rezervuj pro odpovědi, kde nic nenarušuje návaznost. Jakákoli znatelná mezera 
   nebo náhlý přechod znamená pokles na 6.

5: Dobré — obecně dobře strukturované a snadno sledovatelné. Objevují se drobné mezery, 
   ale celkový vývoj myšlenek je jasný.
   Poznámka: pokud myšlenky navazují, ale tok není dokonalý, dej 5, ne 3.

3: Slabé — myšlenky tam jsou, ale špatně propojené. Odpověď postrádá tah na branku; 
   znatelné skoky mezi tématy. Čtenář musí nad logikou přemýšlet.
   Poznámka: pokud je celková struktura patrná i přes slabé přechody, dej 5, ne 3.

1: Nekoherentní — chybí jasná struktura nebo logický postup. Myšlenky jsou nesouvislé 
   nebo si odporují. Je velmi těžké určit, co tím chtěl básník říci.
   Samotný špatný tok nebo slabé přechody nestačí pro skóre 1.

Mezistupně (použij jen při stavu jasně mezi kotvami):
- 6 = mezi 7 a 5 (velmi drobné narušení; jeden mírně náhlý přechod)
- 4 = mezi 5 a 3 (znatelné logické mezery, ale víc než jen slabé propojení)
- 2 = mezi 3 a 1 (velmi slabá struktura; téměř žádná logická souvislost)

Prompt: «{input}»
Response: «{response}»

Odpověz pouze jednou číslicí: 1, 2, 3, 4, 5, 6, 7.
Nepřidávej žádné vysvětlení ani okecávání.

Skóre: """
        ),
        # --- de_DE ---
        "de_DE": (
            ""
        ),
        # --- ar_EG ---
        "ar_EG": (
            ""
        ),
        # --- bn_BD ---
        "bn_BD": (
            ""
        ),
        # --- hi_IN ---
        "hi_IN": (
            ""
        ),
        # --- id_ID ---
        "id_ID": (
            ""
        ),
        # --- ja_JP ---
        "ja_JP": (
            ""
        ),
        # --- ru_RU ---
        "ru_RU": (
            ""
        ),
        # --- zh_CN ---
        "zh_CN": (
            ""
        ),
    },
}

