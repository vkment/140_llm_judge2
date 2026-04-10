### Virtuální prostředí Python k běhu modelů (vLLM, transformers) pro NPFL140 (9. 4. 2026) na node v metacentrum

Níže je postup pro tvorbu ověřené běžící konfigurace. Tato instalace zabrala řádově 2-3 hodiny, proto ji asi provádějte na nějakém node s malou GPU. Možná můžete zkusit provést jen na node s CPU, nejsem si ale jist, zda cuda věci se nějak při instalaci nedívají na to, zda GPU jest fyzicky k dispozici. Pro instalaci ovšem musíte být v interaktivním režimu, tj. být na některém node (např. konos\* /11GB/, fer\*, fau\* /16GB/ - malé GPU).

Postup je třeba aspoň mírně sledovat.

Modely Gemma 4 (vydané 2. dubna 2026) vyžadují zcela nové vLLM verze 19. Současně mají požadavek na starší verzi transformers (<5), kterou běžně nelze splnit. Pro běh všech dřívějších modelů dost možná takto striktní instalace jako je tato níže není však třeba.

Původně jsem používal svůj 139env z loňského roku, do kterého jsem doinstalovával balíčky, které mi run_judge\*.py hlásil jako chybějící. Tento přístup dlouho fungoval, a pak přestal. Můj 139env se dostal do beznadějně zaseknutého stavu , jehož opravu jsem nakonec vzdal. 

##### Resolver konflikt

> `pip`  říká:
>
> - `vllm 0.19.0` chce metadata-wise `transformers >=4.56,<5`
> - ale ty pro jiné účely chceš `transformers >=5.5.0`
> - čistý resolver to odmítne vyřešit
>
> A to odpovídá i tomu, že starý `139env` byl už nekonzistentní. V jeho `pip list` je současně `vllm 0.19.0` i `transformers 5.5.0`.

Postup níže uvedený vede k tomu, že se navzdory uvedenému nainstalují všechny balíčky jak je třeba.

##### 0. Tvorba nového venv 

Pokud instalujete venv vůbec poprvé, musíte postupovat nějak jinak. Já zde zneužil starý venv aspoň pro přenos Pythonu z něj, ale bohužel tento postup nemám sám přesně zarchivován.

Výsledkem snahy by mělo být, že máte čerstvý prázdný venv bez balíčků. Ten můj se jmenuje **`140env`**.



##### 1. Zde je stav nového prázdného prostředí, nejprve se aktivuje:

(BOOKWORM)vok@...:
/storage/vestec1-elixir/home/vok/py26/llm_judge$ **`source /auto/vestec1-elixir/home/vok/pyenv/140env/bin/activate`**



##### 2. Kontroly pro jistotu:

(140env) (BOOKWORM)vok@...:
/storage/vestec1-elixir/home/vok/py26/llm_judge$ **`python -m pip install -U pip setuptools wheel`**

...
(140env) (BOOKWORM)vok@...:/storage/vestec1-elixir/home/vok/py26/llm_judge$ **`which python`**
`/auto/vestec1-elixir/home/vok/pyenv/140env/bin/python`

(140env) (BOOKWORM)vok@...:
/storage/vestec1-elixir/home/vok/py26/llm_judge$ **`python -m pip --version`**

`pip 26.0.1 from /auto/vestec1-elixir/home/vok/pyenv/140env/lib/python3.11/site-packages/pip (python 3.11)`



##### 3. Instalace vLLM explicitní verze do venv:

(140env) (BOOKWORM)vok@...:
/storage/vestec1-elixir/home/vok/py26/llm_judge$ **`pip install vllm==0.19.0`**

Collecting vllm==0.19.0
  Using cached vllm-0.19.0-cp38-abi3-manylinux_2_31_x86_64.whl.metadata (10.0 kB)
Collecting regex (from vllm==0.19.0)

...

tiktoken-0.12.0 tokenizers-0.22.2 torch-2.10.0 torch-c-dlpack-ext-0.1.5 torchaudio-2.10.0 torchvision-0.25.0 tqdm-4.67.3 transformers-4.57.6 triton-3.6.0 typer-0.24.1 typing-inspection-0.4.2 typing_extensions-4.15.0 urllib3-2.6.3 uvicorn-0.44.0 uvloop-0.22.1 vllm-0.19.0 watchfiles-1.1.1 websockets-16.0 xgrammar-0.1.33 yarl-1.23.0 zipp-3.23.0

... ***instaluje se hodinu, možná dvě ?!*** Dole běží počítač balíčků jak se instalují.

(140env) (BOOKWORM)vok@...:/storage/vestec1-elixir/home/vok/py26/llm_judge$ 



##### 4. Instalace ostatních explicitně určených balíčků do venv:

(140env) (BOOKWORM)vok@...:
/storage/vestec1-elixir/home/vok/py26/llm_judge$ **`pip install -U --no-deps \
  transformers==5.5.0 \
  tokenizers==0.22.2 \
  huggingface_hub==1.9.0 \
  safetensors==0.7.0 \
  sentencepiece==0.2.1 \
  accelerate==1.13.0 \
  python-dotenv==1.2.2 \
  httpx==0.28.1`**

Collecting transformers==5.5.0
  Using cached transformers-5.5.0-py3-none-any.whl.metadata (32 kB)
Requirement already satisfied: tokenizers==0.22.2 in /auto/vestec1-elixir/home/vok/pyenv/140env/lib/python3.11/site-packages (0.22.2)
Collecting huggingface_hub==1.9.0
...
Successfully installed accelerate-1.13.0 huggingface_hub-1.9.0 transformers-5.5.0

(140env) (BOOKWORM)vok@...:/storage/vestec1-elixir/home/vok/py26/llm_judge$ 



##### 5. Rychlé kontroly po instalaci

(140env) (BOOKWORM)vok@...:/storage/vestec1-elixir/home/vok/py26/llm_judge$ **`python -c "from transformers import AutoTokenizer; print('ok')"`**

**ok**
(140env) (BOOKWORM)vok@...:/storage/vestec1-elixir/home/vok/py26/llm_judge$ 
(140env) (BOOKWORM)vok@...:/storage/vestec1-elixir/home/vok/py26/llm_judge$ **`python -c "import vllm; print('vllm ok')"`**

**vllm ok**
(140env) (BOOKWORM)vok@...:/storage/vestec1-elixir/home/vok/py26/llm_judge$ 
(140env) (BOOKWORM)vok@...:/storage/vestec1-elixir/home/vok/py26/llm_judge$ **`python -c "import torch; print(torch.__version__)"`**

**2.10.0+cu128**
(140env) (BOOKWORM)vok@bee3:/storage/vestec1-elixir/home/vok/py26/llm_judge$ 

(140env) (BOOKWORM)vok@...:/storage/vestec1-elixir/home/vok/py26/llm_judge$ **`python --version`**
**Python 3.11.11**

(140env) (BOOKWORM)vok@...:/storage/vestec1-elixir/home/vok/py26/llm_judge$ **`which python`**
**/auto/vestec1-elixir/home/vok/pyenv/140env/bin/python**



##### 6. Spuštění svého programu

(140env) (BOOKWORM)vok@...:/storage/vestec1-elixir/home/vok/py26/llm_judge$ **`python run_judge60.py`**



##### 7. Jaké balíčky se nainstalovaly? - opravdu hodně!

Všech 170+ balíčků po instalaci pomocí **pip freeze** máte v **requirements**:
`doc/venv_on_metacentrum/requirements_140env_working260409.txt`

nebo v **pip list** výsledku:
`doc/venv_on_metacentrum/pip_list_metacentrum260409.txt`



*VoK*, 10. 4. 2026