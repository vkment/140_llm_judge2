# Claude: Změny z non-reasoning local modelu na reasoning

https://claude.ai/chat/073a81ed-5f8a-4ba7-bf3f-cb281ac19fab



Přečetl jsem celý kód. Oproti run_judge14.py jsou v run_judge24.py klíčové rozdíly v: apply_chat_template s `enable_thinking=False`, tokenizer=False v pipe, MAX_OUT=10, a zakomentovaný reasoning blok v API payloadu.

Potřebné změny jsou čtyři:

------

### Změna 1 — název šablony (řádek 26)

```python
# PŮVODNÍ:
TEMPLATE_FILENAME = "judge_templates_locales_hybrid5"

# NOVÉ:
TEMPLATE_FILENAME = "judge_templates_locales_hybrid_reason7"
```

------

### Změna 2 — parse_score (řádky 260–277)

```python
# PŮVODNÍ:
def parse_score(raw: str, context: str = "") -> tuple[float, bool]:
    """
    Extract the first number from raw model output.
    Returns (score, used_fallback).
    Score is clipped to [1.0, 7.0].
    """
    match = re.search(r"\d+\.?\d*", raw.strip())
    if match:
        score = float(match.group())
        score = max(min(score, 7.0), 1.0)
        return score, False
    # Fallback
    score = float(random.randint(1, 7))
    logger.warning(
        "Score parsing FAILED for output %r (context: %s). Using random fallback %g.",
        raw[:80], context, score,
    )
    return score, True

# NOVÉ:
def parse_score(raw: str, context: str = "") -> tuple[float, bool]:
    """
    Extract score from raw model output.
    With reasoning models: looks for score after </think> tag.
    Falls back to searching full output if </think> missing (truncated).
    Score is clipped to [1.0, 7.0].
    Returns (score, used_fallback).
    """
    think_end = raw.find("</think>")
    search_text = raw[think_end + len("</think>"):] if think_end != -1 else raw
    match = re.search(r"\b([1-7])\b", search_text.strip())
    if match:
        return float(match.group(1)), False
    # Fallback: hledej v celém raw (thinking mohl být oříznut)
    match = re.search(r"\b([1-7])\b", raw.strip())
    if match:
        logger.warning(
            "Score found in thinking block (</think> missing?) for %s.", context
        )
        return float(match.group(1)), True
    score = float(random.randint(1, 7))
    logger.warning(
        "Score parsing FAILED for output %r (context: %s). Using random fallback %g.",
        raw[:80], context, score,
    )
    return score, True
```

------

### Změna 3 — Variant A (local): tři místa v run_local

**Řádek 437** — zapnutí reasoning v apply_chat_template:

```python
# PŮVODNÍ:
            enable_thinking=False,  # suppress <think>...</think>

# NOVÉ:
            enable_thinking=True,   # allow <think>...</think>
```

**Řádek 447** — rezerva tokenů pro generování:

```python
# PŮVODNÍ:
    MAX_OUT = 10  # tokens reserved for generation (= max_tokens)

# NOVÉ:
    MAX_OUT = 1024  # tokens reserved for generation (reasoning model needs space)
```

**Řádek 598** — SamplingParams:

```python
# PŮVODNÍ:
            sampling_params = SamplingParams(
                temperature=args.temperature,
                max_tokens=10,
            )

# NOVÉ:
            sampling_params = SamplingParams(
                temperature=args.temperature,
                max_tokens=1024,
            )
```

**Řádek 641** — transformers pipeline gen_kwargs:

```python
# PŮVODNÍ:
            gen_kwargs: dict = {
                "max_new_tokens": 10,

# NOVÉ:
            gen_kwargs: dict = {
                "max_new_tokens": 1024,
```

**Řádek 656** — odstranit `tokenizer=False` z pipe volání:

```python
# PŮVODNÍ:
                pipe_outputs = pipe(batch_prompts, **gen_kwargs, tokenizer=False)   #with reasoning suppression 

# NOVÉ:
                pipe_outputs = pipe(batch_prompts, **gen_kwargs)
```

------

### Změna 4 — Variant B (API): max_tokens (řádek 715)

```python
# PŮVODNÍ:
        "max_tokens": 10,

# NOVÉ:
        "max_tokens": 1024,
```

Zakomentovaný řádek 717 (`# "reasoning": {"exclude": True}`) nechte jak je — je správně zakomentován, nepotřebuje změnu.

------

Volitelně doporučuji také změnit suffix na řádku 38, abyste v CSV odlišil tento běh od předchozích:

```python
parser.add_argument("--model_name_suffix", default="_reason7", ...)
```