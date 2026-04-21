#### Evaluation of Generated Poetry

*Rudolf Rosa*

Nobody has chosen the project. 



jak zřel amor, malé dítě,

tiše dřímat těžký sen

na prahu již čekal na tě

ne, on z jizby vyšel ven



metre (trochee)   Rhyme-scheme like ABBACCDEDDDE

CoT

EduPo project: generating poems - CoT

number of syllables - reduplicant (rhyming part)





Czech poetry is very different than the English one



Rate adherence to Czech peotry

Unexisting words ... less a problem in poetry

100 Czech poems



### Tokenization

113k NLP papers in 2016-2025

regex  token sub-?word  segment

to 9k papers

Llama 3.3 70B:

... based on the title and content provided, determine whether the paper proposes a novel tokenization method or not

- slow 1 day

answer only with the list of tasks and metrics used as '* {task}: {metric1} {metric2} ...'

Most LLMs use BPE - subwords

But researchers work on other methods, too

**subwords**

**characters**

**words**

**morhpemes**

**bytes**

**pixels**

**phonemes**

**sentences**

**patches**

**syllables**

end of list



...

The Smallest unit? ...

Using words is less popular

Character gained popularity after introducting BPE/ULM



Many languages

- 7000 languages
- most frequent languages have standard otrhography and are national languages

English

Chinese

German



...

Summar

A lot of paperrrs

Tokenization is a design choice

BPE default, but many choices

Multilinguality, often English and other langauges

---

### Evaluating LLMs for Music: Harder than it looks

*Tomáš Sourada*

Novel task? ... evaluating it ... very difficult question

Can AI transcribe this audio recording to a sheet music

Can AI convert scanned sheet music into a MuseSore ...

can they?

Reality

how to know whether the output is correct?

(friend)el cann

Ok, then GPT sucks

-

Other models?

Look for existing benchmarks

Qwen-Audio 

Muchomusic: ... paper

The trap of benchmarks: text only LLMs solve the benchmark without listening to the audio

Question: Which genre best described the musical style of the given audio?



Evaluating it yourself:

- transcription is too complex ... automatically is an unsolved problem
- the pivot: if the model cannot



Manual evaluation is time consuming.



MCQ format (multiple choice question)

a, b, c, d ---



Gemini-3, GPT-5-Audio, ...

- answering "Is AI good at task A" requires hard work
- do not trust existing benchmarks necessarily
- simplifying the task often reveals fundamental model flaws before complex task come in

---

### LLMs for Dialogue & Data to text

***Ondřej Dušek*** - slušné představení

Fulfill user requests ... book a hotel etc. 

- need to connect to external DB + provide correct info

Tasks requiring reasoning

Reasoning in isolation

with task oriented dialogue



LLM work worse in multi-turn setting

LLM work worse with a dialogue assistant role



In Czech

Qwen 3.5 and Gemma 4 fairly good in Czech

- another issue: speed - tradeoff



LLMs for Rephrasing:

- simply ask LLMs to paraphrase stuff
- P-MultiWOZ: "generation-specific" responses for MultiWOZ
- Diet coaching chatbot: more variable responses



Generate Python rules to generate text

LLMs with code generation

   Software Engineer

Test Engineer

​    Evaluator

​       Code Analyst

nlg.py result



---

**Is your LLM a grammar snob?**

Patricia Schmidtová

How important is "Perfect" English for Machine translation prompts?

Has the grammar impact ? ... ? 

7 ways to corrupt



Uniform

Orthographic

Phrasal / L2

Phonetic

Register

Lazy user

Trying more prompts more important then perfect prompt at first

--

Evaluating 

### OpenEuroLLM -- Hajic

Many partners

Cíl: otevřený, mnohojazyčný, evropský, generativní, základní jazykový model

Moderate the hype

Open source, plně, vč. přístupných dat

32+ jazyků, European ones

Vysoká kvalita a efektivnost

Vyhovující EU regulacím

Jednoduchý pro aplikace a použití

---



Kocmi Tom, .... Reality of multi-lingual Machine Translation



Observation 58: Multilingual ... systems strenghten our reliance on 



Transfer Learning 

How thousand seem smart

# How thousands of ‘overworked, underpaid’ humans train Google’s AI to seem smart

https://www.theguardian.com/technology/2025/sep/11/google-gemini-ai-training-humans

