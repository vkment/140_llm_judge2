# Experimenty s LLM-as-a-Judge (Gemma-4-26B-A4B-it) - škála 0-100 - temperature 0.5 -  5 průchodů - rekalibrace

## Kontext

Hodnocení kvality odpovědí 16 systémů na 46 promptech v 10 jazycích, 3 kritéria (instruction_following, naturalness, coherence). Referenční jsou lidská hodnocení na škále 1–7. Metrika shody: acc_eq (Deutsch et al., EMNLP 2023).

## Co jsme zkoušeli

**Škála 0–100 vs. 1–7** Judge na škále 0–100 vykazuje silný bias k násobkům 5 a zejména k hodnotám 95, 98, 100 (~68 % všech skórů). Efektivně používá jen 8–10 diskrétních hodnot. Přímé hodnocení na škále 1–7 dává acc_eq průměr 0.568, škála 0–100 po kalibraci 0.575 — prakticky ekvivalentní.

**Hyperparametry inference: temperature 0.5, 5 průchodů** Multi-pass běh ukázal, že medián std přes 5 průchodů = 0.0. Model je při temperature 0.5 stále téměř deterministický — zakotvení na konkrétních hodnotách (95, 98...) je silnější než vliv samplingu. Multi-pass tedy nepřinesl užitečnou informaci o nejistotě judge.

**Post-hoc kalibrace** Zkoušeli jsme dvě metody per (locale × criterion):

- Isotonická regrese (párová LLM→human) — marginální zlepšení
- Q-Q mapování (distribuce→distribuce) — horší než isotonická regrese

Obě metody jsou pro acc_eq principiálně nevhodné: acc_eq měří relativní pořadí systémů v rámci promptu, ne absolutní shodu skóre. Kalibrace absolutních hodnot pořadí neovlivní pokud judge přiřadí stejné skóre všem systémům.

Nicméně vysvětluje, proč nepomáhaly ani předchozí snahy o zpřísnění-ulehčení promptů, potíž je zřejmě ve vlastnostech samotných judgů a nikoliv ve tvaru či podobě distribucí hodnocení.

**Analýza acc_eq per prompt** acc_eq má velký rozptyl přes 46 promptů (std ~0.18), rozsah 0.13–1.0. Judge neselhává rovnoměrně — na některých promptech funguje výborně, na jiných zcela. Naturalness je konzistentně nejslabší kriterium. cs_CZ je nejslabší jazyk (acc_eq ~0.49–0.53), en_US nejsilnější (0.62–0.74). Prompty sdílené přes jazyky (překlady) mají velkou varianci acc_eq přes lokály — problém je jazykově specifický, ne obsahový.

## Závěr

Bottleneck je v judge modelu samotném. Pokud judge přiřazuje stejné skóre systémům různé kvality, žádná post-hoc transformace ani úprava promptu nebo inference hyperparametrů tuto informaci nevytvoří zpětně. Pro zlepšení acc_eq je třeba změnit judge model.