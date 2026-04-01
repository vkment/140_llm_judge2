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

"""Task: Score how completely and accurately the response fulfills the user's request in {language}.

Evaluate ONLY instruction adherence — not grammar, style, or language quality.

Score scale:

7: All instructions followed — every explicit requirement and detail addressed.
5: Main instructions followed — minor requirements or edge cases missed.
3: Partial — core task attempted but significant requirements ignored.
1: Fails — off-topic, refuses, or response is not in {language}.

Intermediate scores only when clearly between two levels:
- 6 = very minor omission
- 4 = noticeable gap in requirements
- 2 = most requirements unmet

Return ONLY the score (1–7). No explanation.

Prompt: «{input}»
Response: «{response}»

Score (1–7): """

        ),
    },
    "naturalness": {
        "default": (
"""Task: Score how natural and fluent the response to a prompt is in {language}.

Use this number scale:

7: Fully natural — fluent like a native speaker.
5: Mostly natural — minor issues, but easy to understand.
3: Poor — many errors; requires effort to understand.
1: Unnatural — very hard to understand or not in {language}.

You may use intermediate scores (6 or 4 or 2) only if clearly between levels:
- 6 = between 7 and 5 (very minor awkwardness; slightly non-native phrasing but still smooth)
- 4 = between 5 and 3 (noticeable unnatural phrasing; multiple awkward constructions, but still understandable)
- 2 = between 3 and 1 (very unnatural; frequent errors or phrasing that strongly disrupts readability)

Return only the score number (1–7) and no reasoning in words.

Prompt: «{input}»
Response: «{response}»

Score (1-7): """
        ),
    },
    "coherence": {
        "default": (

"""Task: Score the logical structure and coherence of the response in {language}.

Use this number scale:
7: Fully coherent — clear structure, perfect logical flow and transitions.
5: Mostly coherent — generally clear but with some gaps or abrupt transitions.
3: Weak — poor flow; ideas are not well connected.
1: Incoherent — no clear structure or logic.

Intermediate scores:
- 6 = between 7 and 5 (very minor disruption in flow)
- 4 = between 5 and 3 (noticeable gaps in logic)
- 2 = between 3 and 1 (very weak structure; ideas disconnected)

Return ONLY the score number (1-7).

Prompt: «{input}»
Response: «{response}»

Score (1-7): """

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

