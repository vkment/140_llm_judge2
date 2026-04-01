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
"""Task: Score how well the response follows the user's instructions in {language}.

Use this scale:

7: Fully correct — follows all instructions and details.
5: Mostly correct — follows main instructions but misses some details.
3: Partially correct — follows only some instructions; important parts are missing.
1: Incorrect — does not follow instructions or is unrelated / not in {language}.

You may use intermediate scores (6 or 4 or 2) only if clearly between levels:
- 6 = between 7 and 5 (very minor issue)
- 4 = between 5 and 3 (noticeable gaps)
- 2 = between 3 and 1 (very weak)

Return only the score (1–7).

Prompt: {input}
Response: {response}

Score (1-7):"""
        ),
    },
    "naturalness": {
        "default": (
"""Task: Score how natural and fluent the response is in {language}.

Use this scale:

7: Fully natural — fluent like a native speaker.
5: Mostly natural — minor issues, but easy to understand.
3: Poor — many errors; requires effort to understand.
1: Unnatural — very hard to understand or not in {language}.

You may use intermediate scores (6 or 4 or 2) only if clearly between levels.

Return only the score (1–7).

Prompt: {input}
Response: {response}

Score (1-7):"""
        ),
    },
    "coherence": {
        "default": (
"""Task: Score how logically structured and coherent the response is in {language}.

Use this scale:

7: Fully coherent — clear structure, smooth logical flow.
5: Mostly coherent — generally clear but with some gaps or abrupt transitions.
3: Weak — poor flow; ideas are not well connected.
1: Incoherent — no clear structure or logic.

You may use intermediate scores (6 or 4 or 2) only if clearly between levels.

Return only the score (1–7).

Prompt: {input}
Response: {response}

Score (1-7):"""
        ),
    },
}




LOCALE_TEMPLATES: dict[str, dict[str, str]] = {
    "instruction_following": {
        # --- cs_CZ ---
        "cs_CZ": (
            # TODO: sem vložte překlad
            
"""Úkol: Ohodnoť, jak dobře odpověď dodržuje pokyny (instruction following) uživatele v češtině.

Jak dobře odpověď dodržuje zadání?

7: Zcela správně — dodržuje všechny pokyny i detaily.
5: Většinou správně — dodržuje hlavní pokyny, ale některé detaily chybí.
3: Částečně správně — dodržuje jen některé pokyny; důležité části chybí.
1: Nesprávně — nedodržuje pokyny nebo nesouvisí / není v češtině.

Mezihodnoty (6, 4, 2) použij jen tehdy, pokud je výsledek zjevně mezi úrovněmi:
- 6 = mezi 7 a 5 (velmi drobný nedostatek)
- 4 = mezi 5 a 3 (znatelné mezery)
- 2 = mezi 3 a 1 (velmi slabé)

Uveď pouze jedno číslo (1–7) vyjadřující správnost.

Prompt: {input}
Odpověď: {response}

Score (1-7):"""
        ),
        # --- de_DE ---
        "de_DE": (
"""Aufgabe: Bewerten Sie, wie gut die Antwort die Anweisungen (instruction following) des Nutzers auf Deutsch befolgt.

Inwieweit wurden die Anweisungen befolgt?

7: Vollständig — alle Anweisungen und Details wurden eingehalten.
5: Größtenteils — die wichtigsten Anweisungen wurden befolgt, aber einige Details fehlen.
3: Teilweise — nur ein Teil der Anweisungen wurde umgesetzt; wichtige Punkte fehlen.
1: Nicht — die Anweisungen wurden nicht befolgt oder die Antwort ist unpassend / nicht auf Deutsch.

Zwischenwerte (6, 4, 2) nur verwenden, wenn eindeutig zwischen zwei Stufen:
- 6 = zwischen 7 und 5 (sehr kleine Abweichung)
- 4 = zwischen 5 und 3 (spürbare Lücken)
- 2 = zwischen 3 und 1 (sehr schwach)

Geben Sie nur eine Zahl (1–7) für die Korrektheit an.

Prompt: {input}
Antwort: {response}

Score (1-7):"""

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
"""Úkol: Ohodnoť, jak přirozeně a plynule je odpověď napsaná v češtině.

Jak přirozeně (naturalness) odpověď působí?

7: Zcela přirozeně — plynulé jako u rodilého mluvčího.
5: Většinou přirozeně — drobné nedostatky, ale snadno srozumitelné.
3: Slabě — mnoho chyb; vyžaduje úsilí k pochopení.
1: Nepřirozeně — velmi těžko srozumitelné nebo není v češtině.

Mezihodnoty (6, 4, 2) použij jen tehdy, pokud je výsledek zjevně mezi úrovněmi.

Uveď pouze jedno číslo (1–7) vyjadřující přirozenost.

Prompt: {input}
Odpověď: {response}

Score (1-7):"""
        ),
        # --- de_DE ---
        "de_DE": (
"""Aufgabe: Bewerten Sie, wie natürlich und flüssig die Antwort auf Deutsch klingt.

Wie natürlich (naturalness) wirkt die Antwort?

7: Völlig natürlich — flüssig wie von einem Muttersprachler.
5: Überwiegend natürlich — kleine Schwächen, aber gut verständlich.
3: Wenig natürlich — viele Fehler; das Verständnis erfordert Mühe.
1: Unnatürlich — sehr schwer verständlich oder nicht auf Deutsch.

Zwischenwerte (6, 4, 2) nur verwenden, wenn eindeutig zwischen zwei Stufen.

Geben Sie nur eine Zahl (1–7) für die Natürlichkeit an.

Prompt: {input}
Antwort: {response}

Score (1-7):"""
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
"""Úkol: Ohodnoť, jak logicky uspořádaná a soudržná (coherence) je odpověď v češtině.

Jak soudržná a logická je odpověď?

7: Zcela soudržná — jasná struktura, plynulý logický tok.
5: Většinou soudržná — celkově jasná, ale s menšími mezerami či skoky.
3: Slabá — špatná návaznost; myšlenky nejsou dobře propojené.
1: Nesoudržná — bez jasné struktury nebo logiky.

Mezihodnoty (6, 4, 2) použij jen tehdy, pokud je výsledek zjevně mezi úrovněmi.

Uveď pouze jedno číslo (1–7) vyjadřující soudržnost.

Prompt: {input}
Odpověď: {response}

Score (1-7):"""
        ),
        # --- de_DE ---
        "de_DE": (
"""Aufgabe: Bewerten Sie, wie logisch aufgebaut und zusammenhängend (coherence) die Antwort auf Deutsch ist.

Wie stimmig und klar strukturiert ist die Antwort?

7: Vollständig schlüssig — klare Struktur, flüssiger Gedankengang.
5: Überwiegend schlüssig — insgesamt klar, aber mit kleineren Brüchen oder Sprüngen.
3: Schwach — schlechter Zusammenhang; Gedanken sind kaum verknüpft.
1: Unzusammenhängend — keine erkennbare Struktur oder Logik.

Zwischenwerte (6, 4, 2) nur verwenden, wenn eindeutig zwischen zwei Stufen.

Geben Sie nur eine Zahl (1–7) für die Kohärenz an.

Prompt: {input}
Antwort: {response}

Score (1-7):"""
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

