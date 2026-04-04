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
"""You are LLM as judge for instruction following task. Score how well the response follows the user's instructions in {language}.

Use this number scale:

7: Fully correct — follows all instructions and their details.
5: Mostly correct — main instructions are followed but misses some details.
3: Partially correct — follows only some instructions or important parts are missing.
1: Incorrect — does not follow instructions or is unrelated / not in {language}.

You may use intermediate scores (6 or 4 or 2) only if clearly between levels:
- 6 = between 7 and 5 (very minor lack)
- 4 = between 5 and 3 (noticeable gaps)
- 2 = between 3 and 1 (very weak)

Prompt: «{input}»
Response: «{response}»

Before scoring, write exactly 4 sentences of reasoning:
S1: Describe what the response does or fails to do with respect to the instructions.
S2: State which anchor score (7, 5, 3, or 1) fits best and why.
S3: Decide whether this is exactly that anchor level or falls between two adjacent levels.
S4: Confirm your final score and the single most decisive reason.
 
Then output ONLY the final integer score (1–7) on a new last line.

Reasoning and score (1–7): """
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

Prompt: «{input}»
Response: «{response}»

Before scoring, write exactly 4 sentences of reasoning:
S1: Describe the overall fluency and any specific language issues observed in the response.
S2: State which anchor score (7, 5, 3, or 1) fits best and why.
S3: Decide whether this is exactly that anchor level or falls between two adjacent levels.
S4: Confirm your final score and the single most decisive reason.

Then output ONLY the final integer score (1–7) on a new last line.

Reasoning and score (1–7): """
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

You may use intermediate scores (6 or 4 or 2) only if clearly between levels:
- 6 = between 7 and 5 (very minor disruption in flow)
- 4 = between 5 and 3 (noticeable gaps in logic)
- 2 = between 3 and 1 (very weak structure; ideas disconnected)

Prompt: «{input}»
Response: «{response}»

Before scoring, write exactly 4 sentences of reasoning:
S1: Describe the overall structure of the response and how well its ideas connect.
S2: State which anchor score (7, 5, 3, or 1) fits best and why.
S3: Decide whether this is exactly that anchor level or falls between two adjacent levels.
S4: Confirm your final score and the single most decisive reason.

Then output ONLY the final integer score (1–7) on a new last line.

Reasoning and score (1–7): """

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

