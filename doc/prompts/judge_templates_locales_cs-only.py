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

LOCALE_TEMPLATES: dict[str, dict[str, str]] = {
    "instruction_following": {
        # --- cs_CZ ---
        "cs_CZ": (
            # TODO: sem vložte překlad
            
"""Ohodnoť odpověď vygenerovanou systémem na požadavek uživatele v {language} na Likertově škále od 1 do 7. Úrovně kvality přiřazené k číselným hodnotám jsou uvedeny níže:

7: Odpověď plně dodržuje všechny instrukce, které uživatel poskytl.
5: Chatbot většinou dodržel instrukce, odpovídá hlavním bodům požadavku, ale některé detaily chybí.
3: Chatbot dodržel pouze malou část instrukcí nebo opomenul důležité body.
1: Chatbot zcela ignoroval instrukce; odpověď se zdá být nesouvisející s požadavkem uživatele nebo není v {language}.

Vrať pouze skóre a nic dalšího.

Prompt: {input}
Response: {response}

Score (1-7):"""
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
"""Ohodnoť odpověď vygenerovanou systémem na požadavek uživatele v {language} na Likertově škále od 1 do 7. Úrovně kvality přiřazené k číselným hodnotám jsou uvedeny níže:

7: Odpověď představuje plynulý text v {language}, který by mohl být napsán rodilým mluvčím.
5: Odpověď obsahuje určité neplynulosti, které jsou patrné, ale významně nebrání porozumění.
3: Odpověď je výrazně neplynulá. Obsahuje několik gramatických chyb. Většinu významu lze určit, ale pouze s vědomým úsilím.
1: Odpověď je nesrozumitelná nebo není v {language}.

Vrať pouze skóre a nic dalšího.

Prompt: {input}
Response: {response}

Score (1-7):"""
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
"""Ohodnoť odpověď vygenerovanou systémem na požadavek uživatele v {language} na Likertově škále od 1 do 7. Úrovně kvality přiřazené k číselným hodnotám jsou uvedeny níže:

7: Odpověď je logicky správná a vhodně strukturovaná, s jasnou posloupností dobře propojených myšlenek a témat bez skoků v uvažování.
5: Odpověď je obecně dobře strukturovaná a má poměrně jasný celkový sled myšlenek, ale obsahuje několik logických mezer nebo náhle mění téma bez vhodného přechodu.
3: Odpověď postrádá celkovou soudržnost a/nebo obsahuje více zřetelných skoků mezi tématy. Lze rozpoznat některé relevantní myšlenky, ale celkový smysl odpovědi je nesouvislý.
1: Odpověď nemá žádnou celkovou strukturu, není logicky správná a/nebo ji lze rozdělit na mnoho převážně nesouvisejících částí. Je obtížné určit, jaké myšlenky se text snaží sdělit.

Vrať pouze skóre a nic dalšího.

Prompt: {input}
Response: {response}

Score (1-7):"""
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

