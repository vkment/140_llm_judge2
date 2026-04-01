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

Think step by step about the response quality, then output only the final integer score (1–7) on the last line.

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

You may use intermediate scores (6 or 4 or 2) only if clearly between levels:
- 6 = between 7 and 5 (very minor awkwardness; slightly non-native phrasing but still smooth)
- 4 = between 5 and 3 (noticeable unnatural phrasing; multiple awkward constructions, but still understandable)
- 2 = between 3 and 1 (very unnatural; frequent errors or phrasing that strongly disrupts readability)

Think step by step about the response quality, then output only the final integer score (1–7) on the last line.

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

You may use intermediate scores (6 or 4 or 2) only if clearly between levels:
- 6 = between 7 and 5 (very minor disruption in flow; small transition issues but overall clear)
- 4 = between 5 and 3 (noticeable gaps in logic; some disjointed or loosely connected parts)
- 2 = between 3 and 1 (very weak structure; ideas mostly disconnected or hard to follow)

Think step by step about the response quality, then output only the final integer score (1–7) on the last line.

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
            ""
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
            ""
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
            ""
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

