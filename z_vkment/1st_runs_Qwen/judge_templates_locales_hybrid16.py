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

7: Flawless — follows every instruction, every detail, format, and style requirement
   without exception. Reserve 7 only for responses where a native speaker would find
   nothing to correct or add. In practice, 7 should be rare yet possible.

6: Almost perfect — follows all main instructions and nearly all details. Only one
   small omission or minor deviation. This is the expected score for a strong,
   complete response. When in doubt between 6 and 7, score 6.

5: Good — follows the main instructions. More than one detail, a formatting requirement,
   or a secondary instruction is missing or slightly off. This is the expected score for
   a solid response that addresses the core request but is not nearly flawless.
   Score 5 (not 6) when more than one thing is missing or imperfect.

3: Partial — the response is relevant to the topic but follows only a limited portion
   of the instructions. Important parts are missing or incorrectly handled.
   Score 5 (not 3) if the main intent is met but details are missing.
   
1: Fails — the response is completely off-topic, is pure gibberish, or is not
   written in {language} at all.
   Reserve 1 only for responses with zero relevance to the prompt.
   If the response attempts to address the topic in any way, score 3 or higher.
   
Intermediate scores:
- 4 = between 5 and 3 (noticeable gaps, but more than partial)
- 2 = between 3 and 1 (very weak; barely relevant)

Prompt: «{input}»
Response: «{response}»

Use Arabic numerals only (1, 2, 3, 4, 5, 6, 7) for your score.

Score (1-7): """
        ),
    },
    "naturalness": {
        "default": (
"""You are an LLM judge evaluating naturalness and fluency. Score how natural
and fluent the response reads as {language} text.

Anchor scores:

7: Perfectly natural — fluent like a skilled native speaker throughout.
   Reserve 7 only for responses with no awkward phrasing, unnatural constructions,
   or fluency issues of any kind whatsoever.

6: Almost perfectly natural — reads smoothly overall with only one or two minor
   non-native phrasings or slightly awkward constructions. Score 6, not 7, when
   anything sounds even slightly unnatural.

5: Mostly natural — reads naturally in general but has more than one noticeable
   awkward or non-native phrasing. Fluency issues are present but do not disrupt
   understanding. This is the expected score for a fluent response that is not
   nearly flawless.
   Score 5 (not 6) when more than one fluency issue is noticeable.

3: Noticeably unnatural — multiple awkward or non-native constructions throughout;
   the reader must make some effort to follow the text. Meaning is still recoverable.
   Score 5 (not 3) if only occasional awkwardness is present.

1: Incomprehensible or not in {language} — so unnatural or malformed that meaning
   cannot be recovered, or the response is not written in {language}.
   Score 3 (not 1) if meaning is recoverable despite poor fluency.

Intermediate scores:
- 4 = between 5 and 3 (noticeable unnatural phrasing throughout, but still understandable)
- 2 = between 3 and 1 (very unnatural; meaning barely recoverable)

Prompt: «{input}»
Response: «{response}»

Use Arabic numerals only (1, 2, 3, 4, 5, 6, 7) for your score.

Score (1-7): """
        ),
    },
    "coherence": {
        "default": (
"""You are an LLM judge evaluating logical structure and coherence. Score how well the response is organized and how clearly its ideas connect in {language}.

Anchor scores:

7: Perfect — clear structure, smooth logical flow, seamless transitions throughout.
   Reserve 7 only for responses where nothing disrupts the flow whatsoever.

6: Almost perfect — well-structured and easy to follow throughout. Only one slightly
   abrupt transition or minor gap in logic. Score 6, not 7, when anything disrupts
   the flow, even slightly.

5: Good — generally clear structure and logical progression. More than one minor gap
   or abrupt transition, but the overall direction of ideas is easy to follow.
   This is the expected score for a well-organized response that is not nearly flawless.
   Score 5 (not 6) when more than one thing disrupts the flow.

3: Weak — relevant ideas are present but poorly connected. Multiple noticeable jumps
   between topics; the reader must make an effort to follow the logic.
   Score 5 (not 3) if the overall structure is discernible despite imperfect transitions.

1: Incoherent — the response is pure gibberish with no discernible meaning
   or intent whatsoever.
   Reserve 1 only for completely meaningless text.
   If any relevant ideas are present at all, score 3 or higher.   

Intermediate scores:
- 4 = between 5 and 3 (noticeable gaps in logic, but more than just weak)
- 2 = between 3 and 1 (very weak structure; barely any logical connection)

Prompt: «{input}»
Response: «{response}»

Use Arabic numerals only (1, 2, 3, 4, 5, 6, 7) for your score.

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

