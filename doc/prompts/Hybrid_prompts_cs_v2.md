## ---instruction_following

```
Úkol: Ohodnoť, nakolik odpověď splňuje pokyny (instrukce) uživatele v českém jazyce.

Jak přesně odpověď splňuje pokyny:

7: Zcela správně — splňuje všechny pokyny a detaily.
5: Převážně správně — splňuje hlavní pokyny, ale některé detaily chybí.
3: Částečně správně — splňuje jen některé pokyny; důležité části chybí.
1: Nesprávně — pokyny nesplňuje, odpověď nesouvisí se zadáním nebo není v češtině.

Přechodné hodnoty (6, 4 nebo 2) použij jen tehdy, pokud hodnocení jasně leží mezi dvěma úrovněmi:
- 6 = mezi 7 a 5 (velmi drobný nedostatek)
- 4 = mezi 5 a 3 (znatelné mezery)
- 2 = mezi 3 a 1 (velmi slabé)

Správnost ohodnoť jediným číslem (1–7).

Prompt: {input}
Response: {response}

Score (1-7):
```

------

## ---naturalness

```
Úkol: Ohodnoť, jak přirozená a plynulá je odpověď v českém jazyce.

Jak přirozeně a plynule odpověď působí:

7: Zcela přirozeně — plynulé jako od rodilého mluvčího.
5: Převážně přirozeně — drobné nedostatky, ale snadno srozumitelné.
3: Slabě — mnoho chyb; odpověď je těžko srozumitelná.
1: Nepřirozeně — velmi obtížně srozumitelné nebo není v češtině.

Přechodné hodnoty (6, 4 nebo 2) použij jen tehdy, pokud hodnocení jasně leží mezi dvěma úrovněmi.

Přirozenost ohodnoť jediným číslem (1–7).

Prompt: {input}
Response: {response}

Score (1-7):
```

------

## ---coherence

```
Úkol: Ohodnoť, jak logicky strukturovaná a soudržná je odpověď v českém jazyce.

Jak soudržně a logicky odpověď působí:

7: Zcela soudržně — jasná struktura, plynulý logický tok.
5: Převážně soudržně — celkově srozumitelné, ale s občasnými mezerami či neplynulými přechody.
3: Slabě — špatný tok; myšlenky na sebe nenavazují.
1: Nesoudržně — žádná jasná struktura ani logika.

Přechodné hodnoty (6, 4 nebo 2) použij jen tehdy, pokud hodnocení jasně leží mezi dvěma úrovněmi.

Soudržnost ohodnoť jediným číslem (1–7).

Prompt: {input}
Response: {response}

Score (1-7):
```