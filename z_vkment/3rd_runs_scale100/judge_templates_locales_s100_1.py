# judge_templates_locales.py
#
# Locale-specific judge prompt templates.
# Placeholders that MUST be preserved in every translation:
#   {language}  – název jazyka (např. "Czech", "German")
#   {input}     – původní prompt uživatele
#   {response}  – odpověď pro hodnocení systémem
#
# Přidejte překlad jako nový klíč v každém critériu.
# Pokud locale v tomto souboru chybí, get_judge_template() automaticky
# padne zpět na anglický "default".


# Judge prompt templates
JUDGE_TEMPLATES = {
    "instruction_following": {
        "default": (
"""You are an LLM judge evaluating instruction following. 
Score how well the response follows the user's instructions in {language}.

Use a scale from 0 to 100, where:
  0   = complete failure — ignores instructions entirely, is off-topic or not in {language} 
  100 = flawless — indistinguishable from a perfect response; nothing to improve

Use the full range. Responses that are clearly above average but not perfect
typically fall between 55 and 80. Reserve 85–100 for responses that are
genuinely exceptional.

Prompt: «{input}»
Response: «{response}»

Respond with a single integer from 0 to 100. Nothing else.

Score: """
        ),
    },
    "naturalness": {
        "default": (
"""You are an LLM judge evaluating naturalness and fluency. 
Score how natural and fluent the response reads as {language} text.

Use a scale from 0 to 100, where:
  0   = incomprehensible — so unnatural or malformed that meaning cannot be recovered, or the response is not in {language}
  100 = perfectly natural — indistinguishable from a skilled native speaker; no awkward phrasing or unnatural constructions whatsoever

Use the full range. Responses that are generally fluent but show occasional non-native phrasing
typically fall between 55 and 80. Reserve 85–100 for responses that read
as genuinely native throughout.

Prompt: «{input}»
Response: «{response}»

Respond with a single integer from 0 to 100. Nothing else.

Score: """
        ),
    },
    "coherence": {
        "default": (
"""You are an LLM judge evaluating logical structure and coherence. 
Score how well the response is organized and how clearly its ideas connect in {language}.

Use a scale from 0 to 100, where:
  0   = incoherent — no discernible structure or logical progression; ideas are disconnected or contradictory
  100 = flawless — clear structure, smooth logical flow, and seamless transitions throughout; nothing disrupts the progression

Use the full range. Responses with a recognizable structure but noticeable gaps or abrupt transitions
typically fall between 55 and 80. Reserve 85–100 for responses where
the logical flow is genuinely seamless from start to finish.

Prompt: «{input}»
Response: «{response}»

Respond with a single integer from 0 to 100. Nothing else.

Score: """
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

