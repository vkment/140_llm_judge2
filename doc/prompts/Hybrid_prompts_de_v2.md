## ---instruction_following

```
Aufgabe: Bewerten Sie, wie gut die Antwort die Anweisungen (Instruktionen) des Nutzers auf Deutsch befolgt.

Inwieweit wurden die Anweisungen befolgt?

7: Vollständig — alle Anweisungen und Details wurden eingehalten.
5: Größtenteils — die wichtigsten Anweisungen wurden befolgt, aber einige Details fehlen.
3: Teilweise — nur ein Teil der Anweisungen wurde umgesetzt; wichtige Punkte fehlen.
1: Nicht — die Anweisungen wurden nicht befolgt oder die Antwort ist unpassend / nicht auf Deutsch.

Zwischenwerte (6, 4, 2) nur verwenden, wenn eindeutig zwischen zwei Stufen:
- 6 = zwischen 7 und 5 (sehr kleine Abweichung)
- 4 = zwischen 5 und 3 (spürbare Lücken)
- 2 = zwischen 3 und 1 (sehr schwach)

Geben Sie nur eine Zahl (1–7) für die Korrektheit an.

Prompt: {input}
Response: {response}

Score (1-7):
```

------

## ---naturalness

```
Aufgabe: Bewerten Sie, wie natürlich und flüssig die Antwort auf Deutsch klingt.

Wie natürlich wirkt die Antwort?

7: Völlig natürlich — flüssig wie von einem Muttersprachler.
5: Überwiegend natürlich — kleine Schwächen, aber gut verständlich.
3: Wenig natürlich — viele Fehler; das Verständnis erfordert Mühe.
1: Unnatürlich — sehr schwer verständlich oder nicht auf Deutsch.

Zwischenwerte (6, 4, 2) nur verwenden, wenn eindeutig zwischen zwei Stufen.

Geben Sie nur eine Zahl (1–7) für die Natürlichkeit an.

Prompt: {input}
Response: {response}

Score (1-7):
```

------

## ---coherence

```
Aufgabe: Bewerten Sie, wie logisch aufgebaut und zusammenhängend die Antwort auf Deutsch ist.

Wie stimmig und klar strukturiert ist die Antwort?

7: Vollständig schlüssig — klare Struktur, flüssiger Gedankengang.
5: Überwiegend schlüssig — insgesamt klar, aber mit kleineren Brüchen oder Sprüngen.
3: Schwach — schlechter Zusammenhang; Gedanken sind kaum verknüpft.
1: Unzusammenhängend — keine erkennbare Struktur oder Logik.

Zwischenwerte (6, 4, 2) nur verwenden, wenn eindeutig zwischen zwei Stufen.

Geben Sie nur eine Zahl (1–7) für die Kohärenz an.

Prompt: {input}
Response: {response}

Score (1-7):
```