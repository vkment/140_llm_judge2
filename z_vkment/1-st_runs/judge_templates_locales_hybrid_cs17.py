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

Score (1-7): """
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

Score (1-7): """
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

Score (1-7): """
        ),
    },
}




LOCALE_TEMPLATES: dict[str, dict[str, str]] = {
    "instruction_following": {
        # --- cs_CZ ---
        "cs_CZ": (
            # TODO: sem vložte překlad
"""You are an LLM judge evaluating instruction following. Score how well the response follows the user's instructions in Czech.

Important calibration for Czech: scores 6 and 7 are equally common in this language.
Score 6 is the expected top score for a strong, complete response.
Score 7 must be genuinely rare — reserve it only for responses that are truly flawless in every detail.

Anchor scores:

7: Flawless — follows every instruction, every detail, format, and style without exception.
   In Czech evaluation, 7 is rare. When in doubt between 6 and 7, score 6.

6: Strong — follows all main instructions and nearly all details. Only one small omission
   or minor deviation. This is the expected top score for a well-executed response.

5: Good — follows the main instructions. More than one detail, a secondary requirement,
   or a formatting nuance is missing or slightly off. Core request is fully addressed.
   Score 5 (not 6) when more than one thing is missing or imperfect.

4: Uneven — follows the main instructions but with noticeable gaps. Several secondary
   requirements are missing, or one important detail is handled incorrectly.
   Score 4 (not 5) when gaps are clearly noticeable, not just minor.

3: Partial — relevant to the topic but follows only a limited portion of the instructions.
   Important parts are missing or incorrectly handled. Main intent only weakly met.
   Score 5 (not 3) if the main intent is met but details are missing.

1: Fails — ignores the instructions entirely, is off-topic, or is not in Czech.
   Score 3 (not 1) if the response is at least relevant to the topic.

Intermediate scores:
- 2 = between 3 and 1 (very weak; barely relevant)

Prompt: «{input}»
Response: «{response}»

Score (1-7): """

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
"""You are an LLM judge evaluating naturalness and fluency. Score how natural and fluent the response reads as Czech text.

Important calibration for Czech: score 6 is the most common top score, and 7 is less
frequent than either 5 or 6. A response that reads fluently and naturally should receive 6,
not 7. Reserve 7 only for text that is exceptional even among native Czech writing.

Anchor scores:

7: Exceptional — reads like the very best native Czech writing with no issues whatsoever.
   In Czech evaluation, 7 is rare and should not be the default for fluent text.
   When in doubt between 6 and 7, score 6.

6: Natural — reads fluently and naturally as Czech. Only one or two minor awkward
   phrasings or slightly non-native constructions. This is the expected top score.

5: Mostly natural — reads naturally overall but has more than one noticeable awkward
   or non-native phrasing. Fluency issues are present but do not disrupt understanding.
   Score 5 (not 6) when more than one fluency issue is noticeable.

4: Noticeably uneven — multiple awkward constructions throughout. Still understandable
   but requires some effort. Clearly below the level of a natural Czech text.

3: Unnatural — multiple awkward or non-native constructions that require effort to read.
   Meaning is recoverable but fluency is clearly impaired.
   Score 5 (not 3) if only occasional awkwardness is present.

1: Incomprehensible or not in Czech — meaning cannot be recovered, or not written in Czech.
   Score 3 (not 1) if meaning is recoverable despite poor fluency.

Intermediate scores:
- 2 = between 3 and 1 (very unnatural; meaning barely recoverable)

Prompt: «{input}»
Response: «{response}»

Score (1-7): """
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
"""You are an LLM judge evaluating logical structure and coherence. Score how well the response is organized and how clearly its ideas connect in Czech.

Important calibration for Czech: score 7 is somewhat more common than 6, but both
are frequent. Score 7 is appropriate for clearly structured responses; reserve it when
the flow is genuinely seamless. Score 6 when there is any minor disruption.

Anchor scores:

7: Perfect — clear structure, smooth logical flow, seamless transitions throughout.
   Appropriate for well-organized Czech responses where nothing disrupts the flow.
   Any noticeable gap or abrupt transition drops to 6.

6: Almost perfect — well-structured and easy to follow. Only one slightly abrupt
   transition or minor gap in logic.

5: Good — generally clear structure. More than one minor gap or abrupt transition,
   but the overall direction of ideas is easy to follow.
   Score 5 (not 6) when more than one thing disrupts the flow.

4: Uneven — structure is present but with noticeable gaps in logic. The reader must
   make some effort to follow the progression of ideas.

3: Weak — relevant ideas present but poorly connected. Multiple noticeable jumps.
   Score 5 (not 3) if the overall structure is discernible despite weak transitions.

1: Incoherent — no clear structure or logical progression.
   Score 3 (not 1) if relevant ideas are at least present.

Intermediate scores:
- 2 = between 3 and 1 (very weak structure; barely any logical connection)

Prompt: «{input}»
Response: «{response}»

Score (1-7): """

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

