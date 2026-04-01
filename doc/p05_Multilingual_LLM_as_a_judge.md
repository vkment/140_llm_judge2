# 5 - Multilingual LLM as a judge [p1]

[TA: Schmidtová (email)]

LLM as a judge is not equally reliable in all languages, yet we treat it as if it was.

Is the text written in fluent Czech? Score it on a scale from 1 to 7.

7: The response represents fluent **Czech** text that might have been written by a native human speaker.

[...]

1: The response is incomprehensible, or is not in **Czech**.

*Tadyt, że restauracja jest bardzo popularna. Właściciele są mili i uśmiechnięci, a to sprawia, że czujesz się mile widziany.[...]*

Human judgment: 1
LLM judgments: 5

# 5 - Multilingual LLM as a judge [p2]

- Scores across languages might differ due to cultural differences, however, we need to know how much or how little we can trust the LLM judges for a particular language.
- Possible questions to answer:
  1. How do LLM judgments differ from the human ones?
  2. Does translating the input data to English lead to a better agreement?
  3. What are the limitations and pitfalls of prompting?

vs.

Will finetuning on a text in a specific language improve at least that language?