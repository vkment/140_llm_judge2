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

Think through your evaluation carefully.
Then write your final score on the very last line — a single whole Arabic number, one of: 1, 2, 3, 4, 5, 6, 7.
Nothing else on that last line. No label, no decimal, no explanation."""
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

Think through your evaluation carefully.
Then write your final score on the very last line — a single whole Arabic number, one of: 1, 2, 3, 4, 5, 6, 7.
Nothing else on that last line. No label, no decimal, no explanation."""
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

Think through your evaluation carefully.
Then write your final score on the very last line — a single whole Arabic number, one of: 1, 2, 3, 4, 5, 6, 7.
Nothing else on that last line. No label, no decimal, no explanation."""
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

