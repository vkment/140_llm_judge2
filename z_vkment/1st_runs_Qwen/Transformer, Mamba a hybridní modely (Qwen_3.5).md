# Transformer, Mamba a hybridní modely (Qwen_3.5)

## 1. Klasický Transformer

Transformer je architektura neuronové sítě navržená v roce 2017 (paper *Attention Is All You Need*). Dnes ji používá naprostá většina velkých jazykových modelů — GPT, Llama, Qwen3, Mistral a další.

### Jak funguje

Vstupní text se rozdělí na **tokeny** (přibližně slova nebo části slov). Každý token je reprezentován vektorem čísel — tzv. **embeddingem**.

Klíčový mechanismus je **self-attention**: při zpracování každého tokenu se model podívá na *všechny ostatní tokeny* v kontextu a rozhodne, které jsou pro něj důležité. Výsledkem je, že každý token "ví" o všech ostatních.

Příklad: ve větě *„Banka na řece má vysoké břehy"* se token *„břehy"* přes attention dozví, že *„banka"* zde znamená říční břeh, ne finanční instituci.

### Slabina: kvadratická složitost

Pokud má vstup $n$ tokenů, self-attention musí spočítat vztahy mezi všemi dvojicemi — tedy $n^2$ operací. Pro $n = 10,000$ tokenů je to $100,000,000$ operací jen pro jednu vrstvu. Zpracování velmi dlouhých dokumentů je proto pomalé a paměťově náročné.

------

## 2. State Space Models (SSM) a Mamba

### State Space Models

SSM jsou matematické modely původně z teorie řízení (60. léta). Popisují systém, který má vnitřní **stav** $h$, který se průběžně aktualizuje při příchodu nového vstupu $x$ a produkuje výstup $y$:

$$h_t = A \cdot h_{t-1} + B \cdot x_t$$ $$y_t = C \cdot h_t$$

Celá sekvence je tedy "zhustěna" do jednoho stavového vektoru, který se průběžně přepisuje.

### Mamba (2023)

Mamba (Gu & Dao, 2023) je konkrétní implementace SSM pro jazykové modely s klíčovým vylepšením: matice $A$, $B$, $C$ nejsou pevné, ale **závisí na obsahu vstupu** (*selective SSM*). Model se sám učí, co si zapamatovat a co zapomenout.

### Výhody oproti Transformeru

| Vlastnost                   | Transformer             | Mamba                |
| --------------------------- | ----------------------- | -------------------- |
| Složitost inference         | $O(n^2)$                | $O(n)$               |
| Paměť pro kontext           | KV cache roste s délkou | pevná velikost stavu |
| Dlouhé sekvence             | pomalé a drahé          | efektivní            |
| Kvalita na krátkých textech | výborná                 | srovnatelná          |

### Slabina Mamby

Mamba funguje jako jednosměrný průchod sekvencí (podobně jako RNN). Transformer může při každém tokenu vidět celý kontext najednou. V praxi Mamba na některých úlohách vyžadujících přesné vybavení vzdálených informací zaostává za Transformerem.

------

## 3. Hybridní modely

Hybridní modely kombinují vrstvy obou typů ve střídavém vzoru, například:

```
Vrstva 1:  Attention
Vrstva 2:  Mamba (SSM)
Vrstva 3:  Attention
Vrstva 4:  Mamba (SSM)
...
```

Cílem je získat silné stránky obou: schopnost přesné attention tam, kde je potřeba, a efektivitu Mamby pro zpracování dlouhého kontextu.

### Qwen3.5-9B

Model **Qwen3.5-9B** od Alibaba (2025) je hybridní architektura tohoto typu (`Qwen3_5ForConditionalGeneration`). Přestože označení vypadá podobně jako u čistých transformerů Qwen3 (Qwen3-8B apod.), jde o zásadně odlišnou architekturu.

------

## 4. Praktický dopad na inferenci (vLLM, FlashInfer)

Hybridní architektura klade zvláštní nároky na inferenční framework.

### KV cache vs. SSM state cache

Transformer ukládá při inferenci **KV cache** (klíče a hodnoty attention pro každý token). Mamba ukládá **SSM state** (stavový vektor pevné velikosti). Obě cache musí existovat současně a být koordinovány — vLLM proto musí sladit velikosti stránek pro oba typy paměti:

```
Setting attention block size to 528 tokens to ensure that
attention page size is >= mamba page size.
```

### FlashInfer GDN prefill kernely

Pro efektivní GPU výpočet Mamba vrstev používá vLLM specializované CUDA kernely z knihovny **FlashInfer** — konkrétně tzv. *GDN prefill kernely* (Generalized Dense Network). Tyto kernely jsou kompilované za běhu (JIT) pomocí `nvcc` při prvním použití modelu.

Pro GPU architekturu **SM90a** (NVIDIA H100) kompilace zahrnuje 35 složitých CUDA souborů. Každý z nich vyžaduje spuštění `cicc` (CUDA intermediate compiler), který může spotřebovat 4–8 GB RAM. Pokud cluster tuto paměť procesu nepovolí, `cicc` je zabit signálem 9 (SIGKILL) a kompilace selže.

Pro čisté Transformer modely (Qwen3-8B apod.) tyto kernely vůbec nejsou potřeba — odtud rozdíl v chování při inferenci.

Po úspěšné první kompilaci jsou kernely uloženy do cache (`~/.cache/flashinfer/`) a další spuštění kompilaci přeskakují.

------

## Shrnutí

- **Transformer**: výkonný, ale kvadraticky drahý na dlouhé sekvence.
- **Mamba/SSM**: lineárně škálovatelný, efektivní na dlouhý kontext, ale slabší v přesném vybavení.
- **Hybridní model**: kombinuje oba přístupy; vyžaduje specializovanou infrastrukturu (speciální CUDA kernely, koordinaci dvou typů cache).