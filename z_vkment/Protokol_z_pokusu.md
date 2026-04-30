#### (74_2) nvidia/Gemma-4-31B-IT-NVFP4_h23, 15th Apr 2026

NVFP4 kvantizace od nvidia, má jen 32.7 GB (namísto 62.6 GB pro BF16). Lze proto spustit na nodech s 40+GB VRAM, tj. reálně na L40s (běžel), možná L40. Pochopitelně na H100, pointa ale je ji nepotřebovat.

Model překvapil, protože dosáhl zcela stejné výkonnosti jako plná Gemma 4 31B v BF16.

NVFP4 vyžaduje pro běh Blackwell GPU, jakáž v metacentrum vůbec není. Náhradně dokáže běžet při implementací Marlin, což jsou uvedené L40s, L40 nebo H100, ale ne na Ampere platformě, např. A40 ne. Marlin dekvantizuje menší bloky vah a provádí výpočty v plné BF16 nebo FP16, což ale 

Pozn.: GGUF kvantizace v vLMM neběží, vLLM je nepodporuje.

#### (75_2) Gemma-4-31B-IT-NVFP4, 15th Apr 2026

Běh s defaultní template (tj.). Ukázal, že kromě češtiny (a japonštiny) ostatní jazyky vč. zejména angličtiny jsou na tom s touto tempp



#### (77_4) nvidia/NVIDIA-Nemotron-3-Super-120B-A12B-NVFP4, Mar 2026

Mate počtem 120b, s použitou kvantizací 80.4 GB však je spustitelný na H100, běžel s batch_size 6 rychlostí asi 8 rows/s, obsadil 89780MiB/95830MiB. Kvantizace přímo od NVidia. Reasoning bylo možné potlačit.

Katastrofální výkon pro češtinu (0.36, 0.32, 0.32) /pod úrovní 8B modelů/, ale v zásadě i pro angličtinu (0.51, 0.48, 0.42). Model těžce zklamal. Pravděpodobně si nvidia dává pozor, aby nevytvářela konkurenci pro komerční modely, ale i pro open weight modely. Nvidia tvrdí, že open source jsou i tréninková data a postupy, možná i proto výkonnost kulhá. Při své velikosti a čerstvosti měl dávat výsledky úplně jiné.

#### (80_11) openai/gpt-oss-120b_h34, Aug 2025

Model mate počtem 120b, používá ale MXFP4 quantization (provedena přímo od openai), podle huggingface lze spustit na H100 s 80G VRAM (součet files dává asi 65GiB). Při batch_size 32 obsadí 92229MiB /  95830MiB na H100. Tam běží s minimem reasoningu na 6-8 rows/s.

Jde o reasoning model, kde reasoning bohužel nelze hyperparemetry vypnout, lze jej jen mít co nejmenší pomocí `reasoning_effort="low"` v `apply_chat_template(...)`.

Nutné mít zcela zvláštní `parse_score`, které číslici skóre vybere za závěrečným řetězcem `final`, kde je bez oddělovače. Obecně je v 80_* několikero přizpůsobení jen pro gpt-oss-120b.

Lavírování s template (verze _h33, _h43, _h34). Výsledky pro češtinu (0.484, 0.536, 0.492) , při běhu 80_11ale čeština lepší (0.502, 0.543, 0.483), není jasné proč (pouze batch size snížen), pro angličtinu (0.734, 0.623, 0.536)

těsně pod Gemma 4, pro naturalness možná nejlepší.

Jde o model z loňského léta, zatímco Gemma 4 a Qwen 3.6 jsou z posledního měsíce. Velikostí je však výrazně nad nimi, proto výkon trochu zklamání.

#### (79_3) Qwen/Qwen3.6-35B-A3B, Apr 2026

Použit kód pro běh Qwen 3.5 (36_2) jen se změnou modelu, v BF16 má files 71.9 GB. 

Qwen 3.6 je druh modelu, jenž zřejmě byl spíš optimalizován (vůči verzi 3.5), aby zlepšil chování v angličtině. Pro češtinu je naopak mírně horší.