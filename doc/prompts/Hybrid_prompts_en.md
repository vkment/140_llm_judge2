## ---instruction_following

```
Task: Score how well the response follows the user's instructions in {language}.

Use this scale:

7: Fully correct — follows all instructions and details.
5: Mostly correct — follows main instructions but misses some details.
3: Partially correct — follows only some instructions; important parts are missing.
1: Incorrect — does not follow instructions or is unrelated / not in {language}.

You may use intermediate scores (6 or 4 or 2) only if clearly between levels:
- 6 = between 7 and 5 (very minor issue)
- 4 = between 5 and 3 (noticeable gaps)
- 2 = between 3 and 1 (very weak)

Return only the score (1–7).

Prompt: {input}
Response: {response}

Score (1-7):
```

------

## ---naturalness

```
Task: Score how natural and fluent the response is in {language}.

Use this scale:

7: Fully natural — fluent like a native speaker.
5: Mostly natural — minor issues, but easy to understand.
3: Poor — many errors; requires effort to understand.
1: Unnatural — very hard to understand or not in {language}.

You may use intermediate scores (6 or 4 or 2) only if clearly between levels.

Return only the score (1–7).

Prompt: {input}
Response: {response}

Score (1-7):
```

------

## ---coherence

```
Task: Score how logically structured and coherent the response is in {language}.

Use this scale:

7: Fully coherent — clear structure, smooth logical flow.
5: Mostly coherent — generally clear but with some gaps or abrupt transitions.
3: Weak — poor flow; ideas are not well connected.
1: Incoherent — no clear structure or logic.

You may use intermediate scores (6 or 4 or 2) only if clearly between levels.

Return only the score (1–7).

Prompt: {input}
Response: {response}

Score (1-7):
```



