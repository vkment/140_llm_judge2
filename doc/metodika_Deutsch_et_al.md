## Metodika (Deutsch et al., EMNLP 2023)

### Metriky shody

Používáme **acc_eq** (pairwise accuracy s ties):

```
acc_eq = (C + T_hm) / (C + D + T_h + T_m + T_hm)
```

kde pro každý pár systémů (i, j) na stejném promptu:
- **C** = konkordantní páry (metrika i člověk se shodují na pořadí)
- **D** = diskordantní páry (metrika a člověk se neshodují)
- **T_h** = tie jen u lidí
- **T_m** = tie jen u metriky
- **T_hm** = tie u obou → správně predikovaný tie, **odměňován**

Proč acc_eq a ne Kendall τ: existující varianty τ buď ignorují ties, nebo je trestají. Ties jsou přitom časté (LLM judge pracuje se škálou 1–7 → až 70 % párů může být tied) a u kvalitních odpovědí jsou smysluplné.

Dále se počítá **system-level pairwise accuracy** (bez ties):
```
pair_acc = C / (C + D)
```
aplikovaná na průměrná skóre systémů (16 systémů seřazených od nejlepšího).

### Segment-level: Group-by-Item

Pro acc_eq se používá **group-by-item** metoda:
- Pro každý prompt (item) zvlášť: vezmi skóre všech N systémů → spočítej acc_eq
- Průměruj přes všechny prompty

