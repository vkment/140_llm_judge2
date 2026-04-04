# Qwen 3 problems with reasoning

https://claude.ai/chat/9d5465da-f23f-4835-bebb-01463eb66c55

**PR #37112** (reasoning_budget do vLLM) byl před pár dny v aktivním review — možná je již mergnutý v nejnovější verzi. Po upgradu zkuste:

https://github.com/vllm-project/vllm/pull/37112

###### Closed with unmerged commits - This pull request is closed.



Implementace je **téměř správná, ale jedno místo chybí.**

------

## Chyba: řádek 651 — vLLM SamplingParams nebyl aktualizován

```python
# řádek 651 — STÁLE NA 1024, má být 1280:
max_tokens=1024,  # ← toto zůstalo staré

# má být:
max_tokens=1280,  # konzistentní s MAX_OUT a gen_kwargs
```

`gen_kwargs["max_new_tokens"] = 1280` (transformers, řádek 695) je správně, ale vLLM větev (řádek 651) nebyla změněna. Pokud běžíte přes vLLM (což je primární cesta), thinking se tam pořád ořízne při 1024.

------

## K promptům — jak omezit rozbíhání reasoning?

Ano, prompt design na to má vliv. Qwen3 reasoning se rozbíhá, když má model pocit, že musí věc "důkladně prověřit z více stran". Dvě konkrétní úpravy:

**1. Přidat explicitní instrukci ke stručnosti thinking:**

Na konec každého promptu (před `Score (1-7):`) přidat řádek:

```
Think briefly, then output only the final integer score (1–7) on the last line.
```

Místo současného:

```
Think step by step about the response quality, then output only the final integer score (1–7) on the last line.
```

`Think step by step` je pro reasoning modely spouštěčem dlouhého zkoumání. `Think briefly` ho zkrátí.

**2. Guillemety `« »` kolem Prompt/Response** — dobrý nápad, ale jen částečný efekt. Pomáhají modelu jasně odlišit hranice vstupu od instrukcí, takže méně "přemýšlí o struktuře promptu" a více rovnou hodnotí. Doporučuji. Změna v každé šabloně:

```
Prompt: «{input}»
Response: «{response}»
```

Ale primární fix rozbíhání reasoning je kombinace `thinking_budget` (který už máte) + `Think briefly` místo `Think step by step`.

------

## Shrnutí co opravit

1. **run_judge29.py, řádek 651:** `max_tokens=1024` → `max_tokens=1280`
2. **judge_templates_locales_hybrid_reason7.py:** `Think step by step` → `Think briefly` ve všech třech kritériích
3. Volitelně: `« »` kolem `{input}` a `{response}`

Chcete upravené soubory ke stažení?