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

"""Task: Act as a strict quality auditor. Score how precisely the response follows the user's instructions in {language}.
Focus specifically on linguistic nuances and constraints unique to {language}.

7: Perfect — 100% instructions met, including tone, format, and grammar.
5: Good — Core intent met, but missed minor constraints or formatting.
3: Weak — Only partially follows instructions; significant parts are missing.
1: Fail — Completely off-topic or not in {language}.

Intermediate levels (6, 4, 2):
- 6: Near perfect (only one trivial oversight).
- 4: Notable gaps (met main goal but failed multiple secondary constraints).
- 2: Very poor (barely related to the prompt).

Output ONLY the number. No words.

Prompt: «{input}»
Response: «{response}»

Score (1-7): """
        ),
    },
    "naturalness": {
        "default": (
"""Task: Act as a native speaker of {language}. Score how natural and fluent the response is.
Ignore the content's accuracy; focus only on phrasing, style, and linguistic flow.

7: Fully natural — Flawless. Sounds like a high-quality text written by a native speaker.
5: Mostly natural — Easy to understand, but contains minor non-native-like phrasing.
3: Poor — Many errors or heavy "translationese" (awkward syntax/word choice).
1: Unnatural — Incomprehensible, or not in {language} at all.

Refined Scale (6, 4, 2):
- 6: Near perfect (only one slightly stiff or formal phrase, otherwise smooth).
- 4: Noticeable awkwardness (phrases that a native would never use, but the meaning is clear).
- 2: Very weak (disruptive errors, robotic phrasing, or frequent grammatical slips).

Output ONLY the score number (1–7). No reasoning.

Prompt: «{input}»
Response: «{response}»

Score (1-7): """
        ),
    },
    "coherence": {
        "default": (
"""Task: Act as a logical analyst. Score the structural coherence and logical flow of the response in {language}.
Assess how well the ideas are connected and if the overall organization makes sense.

7: Fully coherent — Flawless structure. Logic flows naturally from one point to the next with perfect transitions.
5: Mostly coherent — Generally logical and easy to follow, but has minor gaps or slightly abrupt transitions.
3: Weak — Poor flow. Ideas are disjointed, making it difficult to follow the overall argument or narrative.
1: Incoherent — No logical structure. Ideas are scattered, contradictory, or completely disorganized.

Refined Scale (6, 4, 2):
- 6: High coherence (very minor transition issue; logic is solid but could be slightly tighter).
- 4: Noticeable gaps (the main point is clear, but several sections feel disconnected or out of order).
- 2: Very weak (only small clusters of logic exist; most of the response feels like a random collection of sentences).

Output ONLY the score number (1–7). No reasoning.

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

