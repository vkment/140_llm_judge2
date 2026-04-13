# Vytvoření VENV pro chat_local.py a run_judge_transf.py  na Metacentru

*Zabere řádově půl hodiny až hodinu. Pro jistotu instalace správných CUDA verzí je instalace prováděna během session na node s GPU, ale s velmi malou GPU.*

*Ukončete session jakmile budete hotovi vč. malého vyzkoušení s chat_local.py.*



#### I. Aktivace modulů pro Python a CUDA

*Pozn.: Python verze 3.11 je ještě nová a přitom konzervativní verze pro celý Machine Learning. CUDA v.12.8 je poslední verze pro Pytorch a proto vhodná či i nutná.*



(BOOKWORM)vok@nympha:~$   **`qsub -l walltime=3:0:0 -q default@pbs-m1.metacentrum.cz -l select=1:ncpus=1:ngpus=1:mem=16gb:gpu_mem=10gb:scratch_local=50gb -I
qsub: waiting for job 18969188.pbs-m1.metacentrum.cz to start`**

qsub: job 18969188.pbs-m1.metacentrum.cz ready
(BOOKWORM)vok@konos3:~$ 
(BOOKWORM)vok@konos3:~$ `module avail python`
---------------------------------------- /packages/run/modules-5/debian12avx ----------------------------------------
python/  python26-modules/  python27-modules/  python34-modules/  python36-modules/  

Key:
modulepath  directory/  
(BOOKWORM)vok@konos3:~$ `module avail python/`
---------------------------------------- /packages/run/modules-5/debian12avx ----------------------------------------
python/2.5                          python/2.7.18-gcc-8.3.0-5wtkh7h    python/3.7.7-gcc-8.3.0-t4loj4a      
python/2.6-kky                      python/3.4.1-gcc                   python/3.7.7-intel-19.0.4-2u4xt35   
python/2.6.2                        python/3.4.1-intel                 python/3.7.7-intel-19.0.4-btjhjhj   
python/2.6.6-gcc                    python/3.5.0-gcc                   python/3.7.7-intel-19.0.4-mgiwa7z   
python/2.6.6-intel                  python/3.6.2-gcc                   python/3.8.0-gcc-rab6t              
python/2.7.5                        python/3.7.4-gcc-yr5ac             python/3.8.10-intel-19.0.4-lxzojgt  
python/2.7.6-gcc                    python/3.7.6-gcc-6.3.0-xxvnrzj     python/3.9.12-gcc-10.2.1-rg2lpmk    
python/2.7.6-intel                  python/3.7.6-intel-19.0.4-joudafb  python/3.10.4-gcc-8.3.0-ovkjwzd     
python/2.7.10-gcc                   python/3.7.6-intel-19.0.4-lzfyqux  python/3.10.4-intel-19.0.4-sc7snnf  
python/2.7.10-intel                 python/3.7.7-aocc-2.2.0-stnlrzs    python/3.11.11-gcc-10.2.1-555dlyc   
python/2.7.16-intel-19.0.4-zuqofq2  python/3.7.7-aocc-2.2.0-u3tfi7t    

Key:
modulepath  default-version  
(BOOKWORM)vok@konos3:~$ 
(BOOKWORM)vok@konos3:~$ **`module load python/3.11.11-gcc-10.2.1-555dlyc`**
Loading python/3.11.11-gcc-10.2.1-555dlyc
  Loading requirement: bzip2/1.0.8-gcc-10.2.1-ydytecx expat/2.4.8-gcc-10.2.1-46kpooz gdbm/1.19-gcc-10.2.1-qavlyzh
    gettext/0.21-gcc-10.2.1-tm75xz5 libffi/3.4.2-gcc-10.2.1-hrcl4md ncurses/6.2-gcc-10.2.1-h3werp5
    zlib/1.2.12-gcc-10.2.1-7qmmk4c openssl/1.1.1o-gcc-10.2.1-k5zobqv readline/8.1-gcc-10.2.1-6rg3hny
    sqlite/3.38.5-gcc-10.2.1-azsem56 tcl/8.6.12-gcc-10.2.1-c47mx2q tix/8.4.3-gcc-10.2.1-lxwtcwj
    inputproto/2.3.2-gcc-10.2.1-umyzwhu kbproto/1.0.7-gcc-10.2.1-sr6qksu libxcb/1.14-gcc-10.2.1-tq27v2s
    xextproto/7.3.0-gcc-10.2.1-xmvpp75 xproto/7.0.31-gcc-10.2.1-jfxlkup xtrans/1.3.5-gcc-10.2.1-kekp66m
    libx11/1.7.0-gcc-10.2.1-h76k4xh font-util/1.3.2-gcc-10.2.1-ecfhf54 freetype/2.11.1-gcc-10.2.1-ukjspcj
    libxml2/2.9.13-gcc-10.2.1-ov3wk3g util-linux-uuid/2.37.4-gcc-10.2.1-3nziyzx fontconfig/2.13.94-gcc-10.2.1-siir4e7
    renderproto/0.11.1-gcc-10.2.1-zwxitml libxrender/0.9.10-gcc-10.2.1-zweyjfr libxft/2.3.2-gcc-10.2.1-vmpa6bv
    libxext/1.3.3-gcc-10.2.1-zmhyr7d scrnsaverproto/1.2.2-gcc-10.2.1-c5t362p libxscrnsaver/1.2.2-gcc-10.2.1-cmc2qsc
    tk/8.6.11-gcc-10.2.1-egeivzq xz/5.2.5-gcc-10.2.1-fteagxc
(BOOKWORM)vok@konos3:~$ 
(BOOKWORM)vok@konos3:~$ `python --version`
Python 3.11.11
(BOOKWORM)vok@konos3:~$ `which python`
/cvmfs/software.metacentrum.cz/spack18/software/linux-debian11-x86_64_v2/gcc-10.2.1/python-3.11.11-555dlyctrqxciw5mnnebm2fzyawa7i3s/bin/python
(BOOKWORM)vok@konos3:~$ 
(BOOKWORM)vok@konos3:~$ `module avail cuda`   
---------------------------------------- /packages/run/modules-5/debian12avx ----------------------------------------
cuda/  

Key:
modulepath  directory/  
(BOOKWORM)vok@konos3:~$ `module avail cuda/`
---------------------------------------- /packages/run/modules-5/debian12avx ----------------------------------------
cuda/3.2-kky  cuda/7.0                 cuda/10.2.89-aocc-2.2.0-eluzh4v    cuda/11.1.0-intel-19.0.4-j4dpull  
cuda/4.0      cuda/7.5                 cuda/10.2.89-gcc-6.3.0-34gtciz     cuda/11.2.0-intel-19.0.4-igl6q5g  
cuda/4.2      cuda/8.0                 cuda/10.2.89-gcc-9.2.0-pkvguz3     cuda/11.2.0-intel-19.0.4-tn4edsz  
cuda/5.0      cuda/9.0                 cuda/10.2.89-intel-19.0.4-2akgdzy  cuda/11.6.2-gcc-10.2.1-nwpmxyy    
cuda/5.5      cuda/10.0                cuda/10.2.89-intel-19.0.4-xwpg2ro  cuda/12.6.1-gcc-10.2.1-hplxoqp    
cuda/6.0      cuda/10.0.130-gcc-wwf2g  cuda/10.2.89-intel-20.0.0-gfsaihx  
cuda/6.5      cuda/10.1                cuda/11.1.0-gcc-8.3.0-g47kwyz      

Key:
modulepath  
(BOOKWORM)vok@konos3:~$ **`module load cuda/12.6.1-gcc-10.2.1-hplxoqp`**
(BOOKWORM)vok@konos3:~$ 
(BOOKWORM)vok@konos3:~$ 

#### II. Tvorba prázdného VENV, přechod do něj a kontrola

Vytvářím `140envb` v podadresáři `pyenv`. Můžete použít jiné a zejména své adresáře.

(BOOKWORM)vok@konos3:~$ 
(BOOKWORM)vok@konos3:~$ **`python -m venv /auto/vestec1-elixir/home/vok/pyenv/140envb`**  
(BOOKWORM)vok@konos3:~$ 
(BOOKWORM)vok@konos3:~$ **`source /auto/vestec1-elixir/home/vok/pyenv/140envb/bin/activate`**
(140envb) (BOOKWORM)vok@konos3:~$ 
(140envb) (BOOKWORM)vok@konos3:~$ 

(140envb) (BOOKWORM)vok@konos3:~$ `which python`
/auto/vestec1-elixir/home/vok/pyenv/140envb/bin/python
(140envb) (BOOKWORM)vok@konos3:~$ 
(140envb) (BOOKWORM)vok@konos3:~$ `python --version`
Python 3.11.11

#### III. Instalace CUDA 12.8 do env

Nastavení TMPDIR je kriticky důležité, jinak při instalaci nemá dostatek místa. Postupně se instaluje torch (pro verzi CUDA 12.4), numpy a pak další balíčky.

(140envb) (BOOKWORM)vok@konos3:~$ **`export TMPDIR=$SCRATCHDIR`**
(140envb) (BOOKWORM)vok@konos3:~$
(140envb) (BOOKWORM)vok@konos3:~$ **`pip install torch --index-url https://download.pytorch.org/whl/cu128`**

Looking in indexes: https://download.pytorch.org/whl/cu124
Collecting torch
  Using cached https://download-r2.pytorch.org/whl/cu124/torch-2.6.0%2Bcu124-cp311-cp311-linux_x86_64.whl.metadata (28 kB)

...

cu12-0.6.2 nvidia-nccl-cu12-2.21.5 nvidia-nvjitlink-cu12-12.4.127 nvidia-nvtx-cu12-12.4.127 sympy-1.13.1 torch-2.6.0+cu124 triton-3.2.0 typing-extensions-4.15.0
(140envb) (BOOKWORM)vok@konos2:~$ 
(140envb) (BOOKWORM)vok@konos2:~$ **`pip install numpy`**
Collecting numpy
  Downloading numpy-2.4.4-cp311-cp311-manylinux_2_27_x86_64.manylinux_2_28_x86_64.whl.metadata (6.6 kB)
Downloading numpy-2.4.4-cp311-cp311-manylinux_2_27_x86_64.manylinux_2_28_x86_64.whl (16.9 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 16.9/16.9 MB 48.3 MB/s  0:00:00
Installing collected packages: numpy
Successfully installed numpy-2.4.4
(140envb) (BOOKWORM)vok@konos2:~$ 

##### Ověření správnosti verze CUDA

(140envb) (BOOKWORM)vok@konos2:~$ **`python -c "import torch; print(torch.version.cuda)"`**
12.4
(140envb) (BOOKWORM)vok@konos2:~$ 

#### IV. Instalace dalších balíčků do env

(140envb) (BOOKWORM)vok@konos2:~$ **`pip install transformers accelerate python-dotenv`**
Collecting transformers
  Downloading transformers-5.5.3-py3-none-any.whl.metadata (32 kB)
Collecting accelerate
**...**
Installing collected packages: tqdm, shellingham, safetensors, regex, pyyaml, python-dotenv, pygments, psutil, packaging, mdurl, idna, hf-xet, h11, click, certifi, annotated-doc, markdown-it-py, httpcore, anyio, rich, httpx, typer, huggingface-hub, tokenizers, accelerate, transformers
Successfully installed accelerate-1.13.0 annotated-doc-0.0.4 anyio-4.13.0 certifi-2026.2.25 click-8.3.2 h11-0.16.0 hf-xet-1.4.3 httpcore-1.0.9 httpx-0.28.1 huggingface-hub-1.10.1 idna-3.11 markdown-it-py-4.0.0 mdurl-0.1.2 packaging-26.0 psutil-7.2.2 pygments-2.20.0 python-dotenv-1.2.2 pyyaml-6.0.3 regex-2026.4.4 rich-15.0.0 safetensors-0.7.0 shellingham-1.5.4 tokenizers-0.22.2 tqdm-4.67.3 transformers-5.5.3 typer-0.24.1
(140envb) (BOOKWORM)vok@konos2:~$ 

#### V. Spuštění programů v Pythonu

Měním adresář za svůj ve Vestci, vy použijte svůj adresář se zdrojovými soubory

(140envb) (BOOKWORM)vok@konos2:~$ **`cd /storage/vestec1-elixir/home/vok/py26/llm_judge`**



Všechny následující tři programy mají v argumentech implicitně model **`Qwen2.5-3B-Instruct`**, který dokáže běžet i jen na GPU s 10GB. Vzhledem k velmi malé velikosti je jeho funkce poněkud dřevní, což ale pro prvé testovací účely není na škodu. Stářím se jedná o model ze září 2024 (1.5 rok starý), poslední model Qwen před nástupem reasoning modelů (absence reasoning je opět pro demo spíše účelná).

Programy pochopitelně můžete vyzkoušet i s jinými modely, přičemž věnovat byste se měli výsledně zejména poslednímu, inferenčnímu LLM-as-a-judge.



##### V.1 Spuštění chatovacího programu

(140envb) ... ~$ **`python chat_local.py`**

Dokumentuje způsob volání LLM na GPU ve známém způsobu "chatbotové" komunikace s LLM. Program má podrobnou dokumentaci zejména v oblasti volání modelu - jeho ***účel je též edukativní***.

Program též umožňuje se na vlastní oči seznámit s tím, jak přesně program komunikuje, jak bude reagovat na vstupy mu předané.



##### V.2 Spuštění fancy chatovacího programu (s postupným doplňováním výstupů z LLM)

(140envb) ... ~$ **`python chat_local_fancy.py`**

Stejný druh činnosti jako v V.1 až na to, že výstup z chatbota je poskytován průběžně. Kvůli použité 



##### V.3 Spuštění inferenčního LLM-as-a-judge programu v režimu `transformers`

(140envb) ... ~$ **`python run_judge_transf66.py`**

Příklad spuštění inference LLM v roli LLM-judge na našich vstupních datech a poskytující náš výstup. Jde o extenzi V.1 s tím, že zesložitěním je formace vstupních dat do batchů, zjednodušením v tom, že se nevedou žádné historie konverzace, nepoužívá se systémový prompt atd.

Oproti `run_judge*.py` je program významně zjednodušen tím, že nezahrnuje podporu pro:

- vLLM, - jeho knihovny tím pádem není třeba vůbec instalovat, 
- OpenRouter.

Program se tak podařilo zkrátit jen na cca 400 řádek kódu, zbytek jsou komentáře, v oblasti volání LLM velmi podrobné a opět edukativní.

Tento program tedy běží pouze a jen prostřednictvím knihovny **`transformers`**, tj. hlavní historické možnosti jak bylo i transformery možné spouštět.

Jeho výhodou též je, že po počátečním natažení, byť se napoprvé provádí mírně déle, se poté ihned rozběhne.

Jeho použití je zcela v pořádku když se teprve se spouštěním jazykových modelů seznamujete, nebo i např. pro běh jen jednoho či dvou locale.

Při běhu se všemi 10 locale doporučuji přejít na plnou verzi `run_judge*.py` , která využívá *vLLM*, a po překonání poměrně značné počáteční doby první kompilace, je v jádru inferenční činnosti cca 4-5x rychlejší. Jde však o mohutnější a složitější program, v němž orientace není tak jednoduchá, jako zde.



---

