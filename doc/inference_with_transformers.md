# Zadání pro tvorbu programu: run_judge_transf.py charakteru LLM-as-a-judge

Cílem je napsat **program v Pythonu pro inference LLM**, který pro jeden zvolený model-judge načte existující páry prompt-response, zabalí je do některé zastřešující šablony vstupu, provede inferenci vstupu a získá výstupní skóre, získaný výstup uloží ve formátu kompatibilním s existující pipeline.

Podrobnosti níže.

## Zastřešující šablony pro formaci vstupu LLM

Text zastřešujících šablon je v souboru:

`judge_templates_locales_hybrid13.py` - externí soubor, jehož obsah se bude načítat na počátku běhu programu.

Na počátku tvořeného programu (za importy) bude tento soubor určen konstantou:

`TEMPLATE_FILENAME = "judge_templates_locales_h_cs_27"`    

V souboru jsou `JUDGE_TEMPLATES`, které jsou vždy vyplněny texty tří znění anglické defaultní šablony, a to pro tři *criterion* (instruction_following, naturalness, coherence). Dále jsou `LOCALE_TEMPLATES`, jejichž hodnoty jsou nyni prázdné řetězce "". Chování programu bude, že pokud je pro dané locale a criterion neprázdný řetězec, použije se tento řetězec, ale je-li řetězec prázdný, použije se defaultní anglický řetězec z `JUDGE_TEMPLATES`.

Šablony mohou uvnitř sebe mít tyto placeholdery:

- {language} - nahrazuje se například za Czech, Arabic, atp.

- {input} - nahrazuje se zněním prompt ze vstupních dat

- {response} - nahrazuje se zněním response ze vstupních dat

#### Mapování mezi třemi reprezentacemi locale

Použij následující, jsou-li třeba

```python
# locale (judge CSV)  →  {language} v šabloně
LOCALE_TO_LANGUAGE = {
    "ar_EG": "Arabic",
    "bn_BD": "Bengali",
    "cs_CZ": "Czech",
    "de_DE": "German",
    "en_US": "English",
    "hi_IN": "Hindi",
    "id_ID": "Indonesian",
    "ja_JP": "Japanese",
    "ru_RU": "Russian",
    "zh_CN": "Chinese",
}

# language_locale (human CSV) → locale (judge output CSV)
LANGUAGE_LOCALE_TO_LOCALE = {
    "Egyptian Arabic":           "ar_EG",
    "Bangla (Bangladesh)":       "bn_BD",
    "Czech (Czechia)":           "cs_CZ",
    "German (Germany)":          "de_DE",
    "English (United States)":   "en_US",
    "Hindi (India)":             "hi_IN",
    "Indonesian (Indonesia)":    "id_ID",
    "Japanese (Japan)":          "ja_JP",
    "Russian (Russia)":          "ru_RU",
    "Simplified Chinese (China)":"zh_CN",
}
```

Pozn.: locale judge ve výstupním CSV je vždy ve formátu `ss_CC` (např. `cs_CZ`, `ja_JP`),
odvozeno z názvu souboru `data_ss_CC.csv` nebo přes výše uvedené mapování.

---

## Datové struktury vstupů a výstupů

### Vstupní human eval data (`oeg_human_eval_raw_data/data_<locale>.csv`)

```
system, prompt, response, doc_id, language_locale, coherence, naturalness, instruction_following, mean_score, rater
```

- 10 locale: ar_EG, bn_BD, cs_CZ, de_DE, en_US, hi_IN, id_ID, ja_JP, ru_RU, zh_CN
- 46 promptů × 16 systémů = 736 řádků na locale, celkem 7 360 řádků

Soubor obsahuje záznamy o lidském hodnocení dvojice *prompt*-*response* v daném *language_locale*, a to pro tři druhy criterion, která provedl některý lidský rater. 

Pro naši úlohu využijeme pouze hodnoty páru *prompt* a *reponse* při znalosti *language_locale*. Program poté postupně ze tří druh zastřešujících šablon (*instruction_following*, *naturalness*, *coherence*) vytvoří vždy vstup, který bude LLM předán pro funkci LLM-as-a-judge pro získání jeho skóre.

Vstupní soubory by měly být tyto:

```
(.vsbenv) vojta@deb:~/projects/llm_judge2/oeg_human_eval_raw_data$ ls -1
data_ar_EG.csv
data_bn_BD.csv
data_cs_CZ.csv
data_de_DE.csv
data_en_US.csv
data_hi_IN.csv
data_id_ID.csv
data_ja_JP.csv
data_ru_RU.csv
data_zh_CN.csv
rankingInfo.json
```

Čti je však jako obsah adresáře, jehož cesta bude určena v konstantě

`INPUT_FILES_DIRECTORY = "oeg_human_eval_raw_data"`    

na počátku souboru. 

Podle `--locale` CLI argumentu při  `["all"]` budeš číst všechny vstupní soubory *.csv, při seznamu  (např. `["cs_CZ", "en_US"]`) jen uvedená locale a v daném pořadí.

### Výstupní formát judge dat (`oeg_judge_outloc_submission_data.csv`)

Pro výstupní formát použijeme tuto strukturu, protože se již používá jinými programy pro následné analýzy výsledků.

```csv
judge_model_name, criterion, submission_system_name, original_instance_id, locale, score
Llama-4-Maverick, instruction_following, Gemma-3-27B, 34ff7b0c7d..., en_US, 7.0
...
```

Jeden řádek = jeden (judge, kritérium, systém, prompt, lokál) → skóre 1–7.

**Celkem řádků**: 13 judges × 3 kritéria × 16 systémů × 46 promptů × 10 lokálů = 287 040

*Pozn.: system ve vstupu resp. submission_system_name ve výstupu označuje řetězec názvu LLM, který vygeneroval danou response na daný prompt. Jeho název tedy slouží jako jednoznačné rozlišení a identifikátor dané response, která byla ve volání LLM použita.*  

`judge_model_name` se konstruuje z části za lomítkem v CLI argumentu`--model`, ke kterému se concatenuje `--model_name_suffix`, též z CLI argumentů.

#### Mapování sloupců vstup → výstup

- `doc_id`  →  `original_instance_id`
- `system`  →  `submission_system_name`
- `locale` →  `language_locale`

#### Kontrola

Zkontroluj doporučení ze sekce *Implikovaná rámcová vhodná implementace LLM inference* v souboru `"Postup tvorby párů prompt-response pro OEG, obraz v datech, měření kvality judgů.md"`

---

## Škálování a náklady (cca)

- Celkem **22 080 LLM volání** (7 360 řádků × 3 kritéria) na jeden judge model při všech locale
- Průměrná délka inputu (prompt+response+template): ~2 600 znaků → ~650 tokenů
- Template overhead: ~30-50 % celkového inputu (šablony mohou být proměnlivé)
- Celkový input: ~57M znaků → ~14M tokenů pro všechny lokály dohromady
- Output tokeny: zanedbatelné (jediná číslice 1–7)

---

## Zadání - hlavní řídící cyklus

Napiš **inference skript** `run_judge_transf.py`, který:

1. Načte všechny `data_<locale>.csv` soubory z `oeg_human_eval_raw_data/`
2. Pro každý řádek (system, prompt, response, locale) a každé ze 3 kritérií zavolá LLM judge
3. Výsledky uloží do CSV ve formátu `oeg_judge_outloc_submission_data.csv` (viz výše)
4. Podporuje **checkpoint/resume** – přeskočí již hotové řádky při restartu
5. Loguje průběh (kolik hotovo, odhad zbývajícího času)



### Běh s lokální GPU
- Použij asi pouze knihovnu `transformers` (tj. ne vLLM nebo něco podobného), potřebuje-li další, tak směrem k frameworku *PyTorch*, můžeš použít *NumPy*, pokud se hodí.
- Tj. použij `transformers` pipeline s parametry níže
- Hodí-li se to, sestroj všechny prompty nejprve nanečisto a zjisti max. délku v tokenizéru
  - plus přičti `TOKENS_RESERVE`  (běžně 50 tokenů) rezervu na output; 
    - výsledek předej jako `max_model_len=` při inicializaci LLM, je-li třeba, 
    Pozn.: sloupec `reponse` může obsahovat HTML formátování (`<br>`, `**text**`).
    Skript je předává do šablony tak jak jsou – bez stripování, může prodlužovat vstupní prompty.
- Počítej, že GPU bude mít dostatek paměti, ale nijak jí neplýtvej
- Použij `--batch_size` z CLI argumentů
- Použiji `--temperature` z CLI argumentů 
- **Přehlednost, srozumitelnost, edukativnost**: kód kolem volání LLM na GPU se snaž napsat maximálně přehledně, edukativně, aby byla jasná core funkcionalita, s čím a jak se LLM volá,
  - tuto část kód komentuj nadprůměrně podrobně,
  - smyslem je, aby tato část sloužila i jako edukativní, pro studenty,
  - též učiň zcela názorné, že do případného logovacího souboru (podle `--llm_log` CLI argumentu ) se zapisuje přesně to, co se skutečně předává do LLM na vstupu i co přesně se získává z něj na výstupu.


### Další požadavky:
- Použij CLI argument `--output_csv` pro výstupní soubor
- Parsování score: použij funkci `parse_score` přesně níže uvedenou (je odladěná), jí vrácený fallback loguj jako WARNING (pro pozdější audit) a do počítadla selhání celkem
- Score oříznutí: `max(min(score, 7.0), 1.0)` - bezpečnostní omezení
- Checkpoint klíč: `(judge_model_name, criterion, submission_system_name, original_instance_id, locale)`
- Při startu načti existující output CSV a přeskoč řádky kde tento klíč již existuje
- `--model` – název/cesta modelu, přebráno z HuggingFace
- `judge_model_name` v output CSV = část za posledním `/` v `--model`:
  `args.model.split("/")[-1]`
  → `"meta-llama/llama-4-maverick"` dá `"llama-4-maverick"`,
     `"CohereForAI/aya-expanse-8b"` dá `"aya-expanse-8b"`

### Kód pro určení skóre z výstupu LLM

Použij přesně následující kód, je již odladěn pro různé druhy a chování modelů:

```python
# Translation of native numbers → Arabian ASCII (ie. English)
_DIGIT_MAP = str.maketrans(
    "০১২৩৪৫৬৭৮৯"   # Bangla    (bn_BD)
    "٠١٢٣٤٥٦٧٨٩"   # Arabian in Arab scripts (ar_EG)
    "०१२३४५६७८९",  # Devangar (hi_IN)
    "0123456789"
    "0123456789"
    "0123456789",
)

def parse_score(raw: str, context: str = "") -> tuple[float, bool]:
    """
    Extract score from hybrid CoT or plain output.
    1. Translate native numbers (Bangla, Arab, Devangar) to ASCII.
    2. Search after </think> tag, or </thought> when present.
    3. Search number 1–7 on the last non-empty raw.
    4. Fallback: previous last occurrance 1–7 in the whole text.
    5. Fallback: random score.
    Output:
    float - the score
    bool  - is it the case of any fallback?
    """
    # 1. Translate native numbers
    text = raw.translate(_DIGIT_MAP)

    # 2. Cut-off <think> bloc (Qwen) when present, or </thought> for Gemma
    _think_idx   = text.find("</think>")        #for Qwen
    _thought_idx = text.find("</thought>")      #for Gemma

    if _think_idx != -1 and (_thought_idx == -1 or _think_idx >= _thought_idx):
        search_text = text[_think_idx + len("</think>"):]
    elif _thought_idx != -1:
        search_text = text[_thought_idx + len("</thought>"):]
    else:
        search_text = text

    # 3. Last non-empty raw
    lines = [l.strip() for l in search_text.splitlines() if l.strip()]
    if lines:
        m = re.search(r"\b([1-7])\b", lines[-1])
        if m:
            return float(m.group(1)), False

    # 4. Previous last occurrance 1–7 in search_text
    all_matches = list(re.finditer(r"\b([1-7])\b", search_text))
    if all_matches:
        logger.warning(
            "Score not on last line — using last occurrence in text (context: %s).", context
        )
        return float(all_matches[-1].group(1)), True

    # 5. Fallback into the whole raw text (thinking part could have been cutted off)
    all_matches = list(re.finditer(r"\b([1-7])\b", text))
    if all_matches:
        logger.warning(
            "Score found only in thinking block (</think> missing?) for %s.", context
        )
        return float(all_matches[-1].group(1)), True

    # 6. Random score
    score = float(random.randint(1, 7))
    logger.warning(
        "Score parsing FAILED for output %r (context: %s). Using random fallback %g.",
        raw[:120], context, score,
    )
    return score, True
```

### Význam CLI argumentů pro vývoj a testování:

- `--max_rows N` – zpracuj pouze prvních N řádků z každého lokálu (default: None = vše)
- `--locale cs_CZ` (nebo více: `--locale cs_CZ de_DE` nebo `all`) – omez na jeden nebo více lokálů, default všechny

Důvod: plný běh = 22 080 LLM volání. Pro smoke test stačí např.:
```bash
python run_judge_trans.py --locale cs_CZ --max_rows 10 --output_csv test_out.csv
```
To vygeneruje 10 × 3 = 30 volání, výstup lze ihned ověřit ručně a porovnat
s hodnotami v `oeg_judge_out_submission_data.csv` pro stejné instance.

Výstupní CSV musí mít správný formát i pro částečný běh – aby bylo
kompatibilní s `judge_human_agreement.py` (ten si sám zarovná overlapping instance).

### .env

Předpokládej, že ve stejném adresáři je soubor .env s autentizačním tokenem uživatele do HuggingFace

```
HF_TOKEN=hf_n...some-value-here-...CPT
```

### CLI argumenty

Použij CLI argumenty přesně dle tohoto příkladu a implementuj vhodně všechny jimi zavedené funkce:

```python
parser = argparse.ArgumentParser(description="Run LLM-as-a-Judge evaluation on OEG human eval data.")
parser.add_argument("--model", default="Qwen/Qwen3.5-9B", type=str,
    help='Model name. Eg. "Qwen/Qwen3.5-9B"'
         'It is usually taken from the left top corner of model page on HuggingFace'
         'Part after "/" program uses as judge_model_name in output CSV.',)
parser.add_argument("--model_name_suffix", default="_h13", type=str,
    help='Suffix appended to base model name in judge_model_name column. E.g. "_h13". Empty = no suffix.'
         "Suffix is a label that you use to distinguishing the run's subvariant parameters of given model"
         'Eg. "Qwen3.5-9B_h13" would be indicated in the output CSV'
         'Can be empty, or use something short and/or guiding yourself what the run was about',)
parser.add_argument("--batch_size", default=8, type=int,
    help="Batch size for local inference",)
parser.add_argument("--max_rows", default=None, type=int,
    help="Process only first N rows per locale. None means: all.",)
parser.add_argument("--locale", default=["cs_CZ", "en_US"], nargs="+",
    help='Locale(s) to process, e.g. ["cs_CZ", "en_US"], or ["all"].'
         'It allows to narrow the inference just for few chosen languages (and their order, too)',)
parser.add_argument("--temperature", default=0.0, type=float,
    help="Temperature for model. Given him as the parameter",)
parser.add_argument("--output_csv", default="oeg_judge_outloc_submission_data.csv", type=str,
    help="Path to output CSV file.",)
parser.add_argument("--llm_log", default="run_judge_transf61.log", type=str,
    help='File for LLM I/O logging (exact prompt + raw response). Eg. "run_judge_transf61.log". None = off.',)
```

### Styl kódu – struktura skriptu

Drž se následující struktury (inspirováno akademickým stylem):

1. **importy** na úplném vrcholu
2. **`parser` a všechny `parser.add_argument`** ihned po importech,
   v root bloku (ne uvnitř funkce), například:
```python
parser = argparse.ArgumentParser(description="Run LLM-as-a-Judge evaluation on OEG human eval data.")
parser.add_argument("--model", default="google/gemma-4-31B-it", type=str,
    help='Model name. Eg. "Qwen/Qwen3-8B" (A) or "meta-llama/llama-4-maverick" (B)'
         'It is usually taken from the left top corner of model page on HuggingFace'

... podle zadání výše
```
3. **konstanty a helper funkce** (šablony, mapování, parsování score atd.)
4. **`def main(args)`** – veškerá hlavní logika
5. **na úplném konci**:
```python
if __name__ == "__main__":
    main_args = parser.parse_args([] if "__file__" not in globals() else None)
    main(main_args)
```

Důvod pro `[] if "__file__" not in globals() else None`:
umožňuje volat skript i z Jupyter notebooku bez úprav.

### Komentáře v angličtině

Komentuj sebou vytvořený kód stručně a v angličtině. 

Jen kód kolem volání LLM na GPU komentuj podrobněji a drž se edukativnosti zmíněné již výše, i tam ale komentuj jen v angličtině.