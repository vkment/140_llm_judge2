## ---instruction_following

```
Úkol: Ohodnoť, jak dobře odpověď dodržuje pokyny (instrukce) uživatele v češtině.

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
Response: {response}

Score (1-7):
```

------

## ---naturalness

```
Úkol: Ohodnoť, jak přirozeně a plynule je odpověď napsaná v češtině.

Jak přirozeně odpověď působí?

7: Zcela přirozeně — plynulé jako u rodilého mluvčího.
5: Většinou přirozeně — drobné nedostatky, ale snadno srozumitelné.
3: Slabě — mnoho chyb; vyžaduje úsilí k pochopení.
1: Nepřirozeně — velmi těžko srozumitelné nebo není v češtině.

Mezihodnoty (6, 4, 2) použij jen tehdy, pokud je výsledek zjevně mezi úrovněmi.

Uveď pouze jedno číslo (1–7) vyjadřující přirozenost.

Prompt: {input}
Response: {response}

Score (1-7):
```

------

## ---coherence

```
Úkol: Ohodnoť, jak logicky uspořádaná a soudržná je odpověď v češtině.

Jak soudržná a logická je odpověď?

7: Zcela soudržná — jasná struktura, plynulý logický tok.
5: Většinou soudržná — celkově jasná, ale s menšími mezerami či skoky.
3: Slabá — špatná návaznost; myšlenky nejsou dobře propojené.
1: Nesoudržná — bez jasné struktury nebo logiky.

Mezihodnoty (6, 4, 2) použij jen tehdy, pokud je výsledek zjevně mezi úrovněmi.

Uveď pouze jedno číslo (1–7) vyjadřující soudržnost.

Prompt: {input}
Response: {response}

Score (1-7):
```