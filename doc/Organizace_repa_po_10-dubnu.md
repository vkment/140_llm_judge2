### Hlavní program pro běh inference modelu:

**run_judge*.py**

**'*'** rozlišuje číslo běhu (5, 12, 46 ...), stoupající sekvence, vyšší čísla jsou pozdější, někdy i rozvoj "do strany", např.  ...46_6_.py atp.

*POZOR - při prvním rozběhu run_judge\*.py v režimu local se kompiluje vLMM model - toto trvá - klidně desítky minut - použijte poprvé nějaký malý 8B model apod. POZOR2: pokud bezprostředně příště spustíte na **stejném node**, použije se výsledek nacacheovaný na scratch adresáři (export TMPDIR=$SCRATCHDIR) a rozběh je již znatelně rychlejší. Budete-li při příštím přihlášení spouštět na **jiném node** /v metacentrum pravidlo/, scratch se nenajde a vše se bude kompilovat znovu (v principu je možné si na závěr sezení zkopírovat si soubory ze scratch disku někam k sobě a před spuštěním je od sebe nakopírovat na scratch disk node, který jste dostali, ovšem i to trvá /více desítek GB na model/, byť přeci jen méně). Jak na AIC netuším. Jakmile se model zkompiluje, běží 4-5x rychleji než by běžel v transformers, většinou se režie rozběhu bohatě vyplatí. Asi též doporučeníhodné boookovat si dostatek místa pro scratch (tak 120% velikost paměti GPU či více, ukládají se i jiné věci než jen model, chcete-li spustit více modelů po sobě, každý zabere místo zvlášť, takže pak 120% součtu všech modelů) , ovšem pak ho i na závěr uvolnit.*

např. konkrétně jeden program pro jeden běh:

**run_judge41_3.py** 

používá vstupy:

- `.env` - Vaše tokeny pro HuggingFace nebo OpenRouter, dáte jen jednou, dejte si ale do .gitignore
- **`judge_templates_locales_hybrid23.py`** - soubor se šablonou zastřešujících promptů, 
  definuje se v konstantě **`TEMPLATE_FILENAME`** za importy, musí se využívat a být uveden, zkrátil jsem hlavní program, aby zde texty šablon vůbec nebyly; 
  v odkázaném souboru musí být vyplněno `JUDGE_TEMPLATES` jako defaultní hodnoty, nemusí ale být vyplněny jazykové verze `LOCALE_TEMPLATES`, jsou-li ponechány jako `""`, program bere default, 
- `oeg_human_eval_raw_data/*.csv` - páry *prompt-response* pro různá *locale* (je stejné pro zcela všechny běhy, tuto option ani neměnit), tato data jsme obdrželi od Mgr. Schmidtové ze studie Kocmi, tyto páry program předává LLM modelu a sbírá hodnotící skóre, která zapisuje do výstupu.

vytváří výstupní soubor:

- **`oeg_judge_outloc41_3_submission_data.csv`** - záznam výstupů z modelu (název byl v options) (má stejnou strukturu jako `oeg_judge_run2_submission_data.csv` od Mgr. Schmidtové)

Výstupní soubor lze proto zpracovávat programy od Mgr. Schmidtové, tj. v `judge_human_agreement.py`. Též výhoda, že jsou bezprostředně zachyceny jen výsledky běhu, tj. bez toho, aby se podrobovaly analýze. Následná analýza proto může být libovolná, průběžně se zlepšovat její přesnost, měnit metodika atp.

Běžně jsem výsledky vyhodnocoval touto malou modifikací uvedeného programu:

**vok_judge_human_agreement3.py**
(počítá navíc i *acc_eq* po locale, zaměřit se na slabou češtinu mi přišlo vhodné):

požívá vstup:

- `*.csv` - vstupní soubor se definuje konstantou JUDGE_SUBMISSION_CSV na počátku programu
  např. **`JUDGE_SUBMISSION_CSV = "oeg_judge_outloc41_3_submission_data.csv"`**

vytváří tyto výstupy (mají vždy shodný název, přejmenovávám je pak ručně):

- **`oeg_judge_human_agreement_by_criterion.json`**
- **`oeg_judge_human_agreement_results.json`**

Moje hlavní orientace se ve výsledcích běhu je v těchto dvou souborech výše "ručně", náhledem. 

Zajímají mne zpravidla hodnoty *acc_eq* pro nějaké verze *locale* či *criterion*, občas i souhrnnější hodnoty.

Vizualizace až když mám výsledků více, chci někomu něco prezentovat atp.

---

#### Zajímavé výborně funkční šablony (zastřešující prompty)

`z_vkment/1st_runs_Qwen/` **`judge_templates_locales_hybrid13.py`** - pro Qwen 3.5 35B, ale asi by fungovalo pro všechny běhy do čísla 39, byť pro nižší čísla běhů jsem používal i jiné šablony.

`z_vkment/2nd-runs_Gemma_etc/` **`judge_templates_locales_hybrid23.py`** - Gemma 4 potřebovala tuto změnu  závěru promptu vůči `...hybrid13.py`, vše podstatné je ale shodné jako v šabloně výše.

Všechny pozdější verze run_judge\*.py fungují tak, že vždy berou své prompty z externího souboru, ale nevadí jim `""` pro locale, berou pak implicitní anglické znění.

---

#### Úklid - reorganizace repa

Přesunul jsem mnoho z root jinam. Tj. každý vč. mne bude plnit hlavně svůj podadresář `z_*`.

Mé běhy (vše k nim) nyní hledejte u mne v `z_vkment/*`, jsou tam porůzny i soubory šablon.

Běhy mám dále rozděleny po etapách činností 0th..., 1st..., 2nd..., 3rd, 4th..., etapa bývá více běhů, nebo nějaké jiné spolu související činnosti, které ale etapa ohraničuje (pro mne smysluplně). 

Je to úklid, mnohé programy předpokládaly běh z rootu, nebo aspoň z nového `z_vkment/` 

Nechal jsem některé dokumentační adresáře, zejména `/doc` v rootu, jakož i `/compare...` 

---

### Výsledky nějak zajímavých běhů

Mnoho běhů nemělo zajímavé výsledky. Hlavní zajímavé jsem zkopíroval (zůstaly i kde byly) sem:

**`/z_vkment/good_runs_results_copies/`**

- **`*.csv`** - přímo výstupní soubory csv z run_judge*.py

- **`JSON_Files/*.json`** - analýzy výsledků - první co bych četl, pokud mne zajímají výsledky modelu

Rozlišující suffixy jsem připojil ručně pro orientaci se. Počátečním číslem najdete běh, ze kterého programu vznikly, suffix vám ukazuje jaký model a v jaké modifikaci běžel. Rozhodné jsou ale názvy uvnitř.

---

#### Zajímavé soubory



##### Shrnutí pochopení dat, programů a literatury předaných nám od Mgr. Schmidtové:

**`doc/Postup tvorby párů prompt-response pro OEG, obraz v datech, měření kvality judgů.md`**

`doc/Postup tvorby párů prompt-response pro OEG, obraz v datech, měření kvality judgů.pdf`

- 1. Postup tvorby dat podle studie Kocmi

- 2. Obraz součástí v předaných datech

- 3. Metody měření kvality LLM-soudců

     

##### Vizualizace výsledků našich zajímavých experimentů - běhů (10. 4.)

**`results_visualisation/judge_results_by_locale.jpg`** - výsledky nových judgů

výsledek běhu `z_vkment/visualize_judge_results.py` dne 10. 4. v 15:55

Byly tam zahrnuty všechny  `z_vkment/good_runs_results_copies/*.csv` a z Kocmi jen 6 nej-něco  běhů.



##### Vizualizace běhů z dřívější studie Kocmi (prováděná okolo 20. 3.)

`compare_all_2025_(previous-year)/vok_panel2_last-year-results.jpg` - Language difficulty

`compare_all_2025_(previous-year)/vok_panel3_last-year-results.jpg` - Per criterion breakup by language



##### Prompt pro generaci první verze (OpenRouter) run_judge.py (okolo 20. 3.)

`doc/prompts/Prompt1_Implementuj-inference-skript-run_judge.md`

`doc/new_thread_prompt12.md`

`doc/first_lines_of_data_cs_CZ.csv.txt`

`doc/first-csv-lines_of_human-vs-llm-judge_evals.txt`



##### Prompt pro generaci druhé verze (local - vLLM) run_judge.py (okolo 20. 3.)

`doc/prompts/Prompt2_Doplň-run_judge-o-lokální-GPU-inferenci.md`



---

##### Konfigurace Python virtual environment na Metacentrum (8. 4. 2026)

Dokumentace tvorby venv na node metacentra, které ověřeně funguje

**`doc/venv_on_metacentrum/Vytvoření_venv_pro_nody_metacentrum.md`** - příkazy pro instalaci balíčků

`doc/venv_on_metacentrum/` - adresář se soubory dokumentujícími konfiguraci venv



##### Jaké GPU jsou na výpočetních uzlech v metacentrum k dispozici

`doc/Metacentrum GPU nodes March2026.txt`



##### `.gitignore`

`copy_of_.gitignore` - minimální vhodný .gitignore



##### Příklad kopírování ze scratche do zálohy k sobě

Přechod do adresáře scratch (po skončení Python programu)

```
cd $SCRATCHDIR
```

Vytvoření adresáře:

```
mkdir -p /auto/vestec1-elixir/home/vok/py26/llm_judge/scratchd
```

Nemá smysl si kopírovat úplně všechno, ale třeba takto to dopadlo pro 2 modely a nějaké příslušenství:

```
rsync -avh /scratch.ssd/vok/job_18819644.pbs-m1/huggingface \
           /scratch.ssd/vok/job_18819644.pbs-m1/models--Qwen--Qwen3.5-35B-A3B \
           /scratch.ssd/vok/job_18819644.pbs-m1/models--google--gemma-4-31B-it \
           /scratch.ssd/vok/job_18819644.pbs-m1/vllm \
           /scratch.ssd/vok/job_18819644.pbs-m1/pip \
           /scratch.ssd/vok/job_18819644.pbs-m1/virtualenv \
           /scratch.ssd/vok/job_18819644.pbs-m1/torchinductor_vok \
           /auto/vestec1-elixir/home/vok/py26/llm_judge/scratchd/
```

a trvá to. Není vysloveně nutné, vytvoří se v nejhorším opět znova.

Pozor - llm_judge ve vestci nemám napojený na git, dávám tam soubory FileZillou, takže v něm záloha z node ničemu nevadí.

Pak scratch uvolním a skončím: 

```
clean_scratch
...
exit
```



##### Organizace repa po 10. dubnu 2026

`doc/Organizace_repa_po_10-dubnu.md` - Tento dokument

