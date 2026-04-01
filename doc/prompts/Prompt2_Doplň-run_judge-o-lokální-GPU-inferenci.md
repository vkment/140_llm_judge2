#### Kontext 

Mám funkční inference skript `run_judge.py` (přiložen) pro projekt Multilingual LLM-as-a-Judge (WMT MIST 2025, OEG track). Skript hodnotí LLM odpovědi na škále 1–7 dle tří kritérií (coherence, naturalness, instruction_following) a ukládá výsledky do CSV kompatibilního s evaluační pipeline. Varianta B (OpenRouter API) je plně funkční. Přikládám aktuální zdrojový kód.

#### Zadání 

Doplň do přiloženého `run_judge.py` variantu A (lokální GPU, vLLM) – nahraď stávající stub `raise NotImplementedError` plnou implementací. Vše musí zůstat v jednom souboru. Neměň variantu B ani sdílenou logiku, pouze doplň tělo funkce `run_local()`. Specifikace varianty A

- Použij vLLM Python API přímo: `from vllm import LLM, SamplingParams`
- Předvýpočet max délky:
  - Sestroj všechny prompty nanečisto pomocí stávající `build_prompt()`
  - Tokenizuj je tokenizérem modelu a zjisti maximum
  - Přičti 50 tokenů rezervu na output
  - Výsledek předej jako `max_model_len=` při inicializaci `LLM(...)`
  - Pozn.: sloupec `response` může obsahovat HTML (`<br>`, `**text**`) – předávej beze změny
- Inicializace modelu:
  - `dtype="auto"` (model preferuje bfloat16, ~16 GB pro 8B)
  - Předpokládej GPU s alespoň 48 GB VRAM
- Výpočet batch size (pokud `args.batch_size` je None):
  - `floor((48 × 0.90 − 16) / (max_model_len × bytes_per_token))`, max 32
  - `bytes_per_token`: 131 072 bytů pro bfloat16/fp16, 262 144 pro fp32
  - Skutečný dtype zjisti přes `llm.llm_engine.model_config.dtype`, při `AttributeError` předpokládej bfloat16
- Inference:
  - `temperature=args.temperature` (typicky 0.0), `max_tokens=10`
  - Batch zpracování přes `llm.generate(batch_of_prompts, sampling_params)`
- Fallback: pokud vLLM selže při inicializaci, fallback na `transformers` pipeline s `model.generate()` a stejnými parametry
- Checkpoint/resume, parsování score, logování průběhu – používej stávající sdílené funkce (`load_checkpoint`, `parse_score`, logování každých 100 řádků s ETA)
- Zápis výstupu – stejný CSV formát jako varianta B, append + flush po každém batchi

Testování

```bash
python run_judge.py --variant local --locale cs_CZ --max_rows 5 \
  --model CohereForAI/aya-expanse-8b --output_csv test_local.csv
```

Výstup 5 × 3 = 15 řádků, ověřitelný ručně.

------

Výstupem je pouze tělo funkce `run_local()` – celý zbytek souboru zůstává beze změny.