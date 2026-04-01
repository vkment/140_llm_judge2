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
"""Bewerte die von einem System generierte Antwort auf eine Anfrage eines Nutzers in {language} auf einer Likert-Skala von 1 bis 7. Die den numerischen Werten zugeordneten Qualitätsstufen sind unten angegeben:

7: Die Antwort hält sich vollständig an alle Anweisungen, die der Nutzer gegeben hat.
5: Der Chatbot hat die Anweisungen größtenteils befolgt, entspricht den Hauptpunkten der Anfrage, lässt jedoch einige Details aus.
3: Der Chatbot hat nur einen kleinen Teil der Anweisungen befolgt oder wichtige Punkte ausgelassen.
1: Der Chatbot hat die Anweisungen vollständig ignoriert; die Antwort scheint keinen Bezug zur Anfrage des Nutzers zu haben oder ist nicht in {language}.

Gib nur die Punktzahl zurück und nichts anderes.

Prompt: {input}
Response: {response}

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
"""Bewerte die von einem System generierte Antwort auf eine Anfrage eines Nutzers in {language} auf einer Likert-Skala von 1 bis 7. Die den numerischen Werten zugeordneten Qualitätsstufen sind unten angegeben:

7: Die Antwort stellt einen flüssigen Text in {language} dar, der von einem menschlichen Muttersprachler verfasst worden sein könnte.
5: Die Antwort enthält einige Unflüssigkeiten, die auffallen, das Verständnis jedoch nicht wesentlich beeinträchtigen.
3: Die Antwort ist stark unflüssig. Es gibt mehrere grammatikalische Fehler. Der Großteil der Bedeutung kann erschlossen werden, jedoch nur mit bewusstem Aufwand.
1: Die Antwort ist unverständlich oder nicht in {language}.

Gib nur die Punktzahl zurück und nichts anderes.

Prompt: {input}
Response: {response}

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
"""Bewerte die von einem System generierte Antwort auf eine Anfrage eines Nutzers in {language} auf einer Likert-Skala von 1 bis 7. Die den numerischen Werten zugeordneten Qualitätsstufen sind unten angegeben:

7: Die Antwort ist logisch schlüssig und angemessen strukturiert, mit einer klaren Abfolge gut miteinander verbundener Ideen und Themen ohne Sprünge im Gedankengang.
5: Die Antwort ist im Allgemeinen gut strukturiert und weist einen insgesamt klaren Gedankengang auf, enthält jedoch einige logische Lücken oder wechselt plötzlich das Thema ohne angemessenen Übergang.
3: Der Antwort fehlt ein durchgängiger roter Faden und/oder sie enthält mehrere deutlich erkennbare Themensprünge. Einige relevante Ideen sind erkennbar, aber der Gesamtzweck der Antwort ist inkohärent.
1: Die Antwort hat keine erkennbare Gesamtstruktur, ist in keiner Weise logisch schlüssig und/oder lässt sich in viele überwiegend unzusammenhängende Abschnitte unterteilen. Es ist schwierig zu erkennen, welche Punkte der Text vermitteln möchte.

Gib nur die Punktzahl zurück und nichts anderes.

Prompt: {input}
Response: {response}

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


# Note that this using version 10b uses following value for JUDGE_TEMPLATES, not from here

# # Judge prompt templates
# JUDGE_TEMPLATES = {
#     "instruction_following": {
#         "default": (
#             "Score the response generated by a system to a user's request in {language} "
#             "on a likert scale from 1 to 7. The quality levels associated with numerical "
#             "scores are provided below:\n\n"
#             "7: The response fully adheres to all instructions that the user provided.\n"
#             "5: The chatbot mostly followed the instructions, conforming to the main points "
#             "of the request but missing some details.\n"
#             "3: The chatbot followed only a small portion of the instructions or missed "
#             "important points.\n"
#             "1: The chatbot entirely disregarded the instructions; the response appears to "
#             "have no relation to the user's request or is not in {language}.\n\n"
#             "Return only the score and nothing else.\n\n"
#             "Prompt: {input}\n"
#             "Response: {response}\n\n"
#             "Score (1-7):"
#         ),
#     },
#     "naturalness": {
#         "default": (
#             "Score the response generated by a system to a user's request in {language} "
#             "on a likert scale from 1 to 7. The quality levels associated with numerical "
#             "scores are provided below:\n\n"
#             "7: The response represents fluent {language} text that might have been written "
#             "by a native human speaker.\n"
#             "5: The response has some disfluencies that are noticeable but don't significantly "
#             "hinder understanding the response.\n"
#             "3: The response is highly disfluent. There are several grammatical errors. Most "
#             "of the meaning can be determined, but only with conscious effort.\n"
#             "1: The response is incomprehensible or is not in {language}.\n\n"
#             "Return only the score and nothing else.\n\n"
#             "Prompt: {input}\n"
#             "Response: {response}\n\n"
#             "Score (1-7):"
#         ),
#     },
#     "coherence": {
#         "default": (
#             "Score the response generated by a system to a user's request in {language} "
#             "on a likert scale from 1 to 7. The quality levels associated with numerical "
#             "scores are provided below:\n\n"
#             "7: The response is logically sound and appropriately structured with a clear "
#             "sequence of nicely connected ideas and topics with no leaps in reasoning.\n"
#             "5: The response is generally well-structured and has a generally clear overall "
#             "progression of ideas, but introduces a few logical gaps, or suddenly switches "
#             "topics without an appropriate transition.\n"
#             "3: The response lacks an overall flow, and/or has multiple noticeable jumps "
#             "between topics. It is possible to discern some relevant ideas, but the overall "
#             "purpose of the response is incoherent.\n"
#             "1: The response has no overall structure, is in no way logically sound, and/or "
#             "can be divided into many mostly-unrelated sections. It is difficult to identify "
#             "any points the text is trying to make.\n\n"
#             "Return only the score and nothing else.\n\n"
#             "Prompt: {input}\n"
#             "Response: {response}\n\n"
#             "Score (1-7):"
#         ),
#     },
# }
