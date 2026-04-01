## ---instruction_following

```
Úkol: Ohodnoť, jak dobře odpověď dodržuje pokyny uživatele v {language}.

Použij tuto škálu:

7: Plně správné — dodržuje všechny pokyny a detaily.
5: Většinou správné — dodržuje hlavní pokyny, ale některé detaily chybí.
3: Částečně správné — dodržuje jen některé pokyny; důležité části chybí.
1: Nesprávné — nedodržuje pokyny nebo nesouvisí / není v {language}.

Můžeš použít mezilehlé hodnoty (6 nebo 4 nebo 2) jen pokud jsou jasně mezi úrovněmi:
- 6 = mezi 7 a 5 (velmi drobný problém)
- 4 = mezi 5 a 3 (znatelné mezery)
- 2 = mezi 3 a 1 (velmi slabé)

Vrať pouze skóre (1–7).

Prompt: {input}
Response: {response}

Score (1-7):
```

------

## ---naturalness

```
Úkol: Ohodnoť, jak přirozená a plynulá je odpověď v {language}.

Použij tuto škálu:

7: Plně přirozené — plynulé jako u rodilého mluvčího.
5: Většinou přirozené — drobné nedostatky, ale snadno srozumitelné.
3: Slabé — mnoho chyb; vyžaduje úsilí k porozumění.
1: Nepřirozené — velmi obtížně srozumitelné nebo není v {language}.

Můžeš použít mezilehlé hodnoty (6 nebo 4 nebo 2) jen pokud jsou jasně mezi úrovněmi.

Vrať pouze skóre (1–7).

Prompt: {input}
Response: {response}

Score (1-7):
```

------

## ---coherence

```
Úkol: Ohodnoť, jak logicky strukturovaná a soudržná je odpověď v {language}.

Použij tuto škálu:

7: Plně soudržné — jasná struktura, plynulý logický tok.
5: Většinou soudržné — obecně jasné, ale s některými mezerami nebo náhlými přechody.
3: Slabé — špatný tok; myšlenky nejsou dobře propojené.
1: Nesoudržné — žádná jasná struktura ani logika.

Můžeš použít mezilehlé hodnoty (6 nebo 4 nebo 2) jen pokud jsou jasně mezi úrovněmi.

Vrať pouze skóre (1–7).

Prompt: {input}
Response: {response}

Score (1-7):
```