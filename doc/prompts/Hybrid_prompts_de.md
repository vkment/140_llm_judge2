## ---instruction_following

```
Aufgabe: Bewerte, wie gut die Antwort den Anweisungen des Nutzers in {language} folgt.

Verwende diese Skala:

7: Vollständig korrekt — folgt allen Anweisungen und Details.
5: Größtenteils korrekt — folgt den Hauptanweisungen, verpasst aber einige Details.
3: Teilweise korrekt — folgt nur einigen Anweisungen; wichtige Teile fehlen.
1: Falsch — folgt den Anweisungen nicht oder ist unzusammenhängend / nicht in {language}.

Du darfst Zwischenwerte (6 oder 4 oder 2) nur verwenden, wenn sie klar zwischen den Stufen liegen:
- 6 = zwischen 7 und 5 (sehr kleines Problem)
- 4 = zwischen 5 und 3 (erkennbare Lücken)
- 2 = zwischen 3 und 1 (sehr schwach)

Gib nur die Punktzahl (1–7) zurück.

Prompt: {input}
Antwort: {response}

Punktzahl (1-7):
```

------

## ---naturalness

```
Aufgabe: Bewerte, wie natürlich und flüssig die Antwort in {language} ist.

Verwende diese Skala:

7: Vollständig natürlich — flüssig wie ein Muttersprachler.
5: Größtenteils natürlich — kleine Probleme, aber gut verständlich.
3: Schwach — viele Fehler; erfordert Mühe, um es zu verstehen.
1: Unnatürlich — sehr schwer verständlich oder nicht in {language}.

Du darfst Zwischenwerte (6 oder 4 oder 2) nur verwenden, wenn sie klar zwischen den Stufen liegen.

Gib nur die Punktzahl (1–7) zurück.

Prompt: {input}
Antwort: {response}

Punktzahl (1-7):
```

------

## ---coherence

```
Aufgabe: Bewerte, wie logisch strukturiert und kohärent die Antwort in {language} ist.

Verwende diese Skala:

7: Vollständig kohärent — klare Struktur, flüssiger logischer Ablauf.
5: Größtenteils kohärent — im Allgemeinen klar, aber mit einigen Lücken oder abrupten Übergängen.
3: Schwach — schlechter Fluss; Ideen sind nicht gut verbunden.
1: Inkohärent — keine klare Struktur oder Logik.

Du darfst Zwischenwerte (6 oder 4 oder 2) nur verwenden, wenn sie klar zwischen den Stufen liegen.

Gib nur die Punktzahl (1–7) zurück.

Prompt: {input}
Antwort: {response}

Punktzahl (1-7):
```