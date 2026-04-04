"""
run_judge.py – LLM-as-a-Judge inference script for MFF 202 OEG track.

Variant A (local): vLLM – stub only (raises NotImplementedError).
Variant B (api):   OpenRouter via openai-compatible client + asyncio.
"""

#v7... change of GPU numbering - see Remap CUDA_VISIBLE_DEVICES below
# 
#https://huggingface.co/meta-llama/Llama-3.1-8B

import argparse
import asyncio
import csv
import logging
import os
import random
import re
import time
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()  # načte .env do os.environ
from transformers import AutoTokenizer as _TplTok #for stage 2 below

#no reasoning
#from vllm.config import ReasoningConfig #reading ReasoningConfig 

#return REASONING into this:
#  gemma-4-26B-A4B-it

import httpx
import importlib    #used to import TEMPLATE_FILENAME later below
TEMPLATE_FILENAME = "judge_templates_locales_hybrid23"    #here LOCALE_TEMPLATES, JUDGE_TEMPLATES are defined, suffix .py ommited  

#  Qwen/Qwen3.5-35B-A3B  + judge_templates_locales_hybrid_cs18.py


# ---------------------------------------------------------------------------
# Argument parser (root-level, notebook-compatible)
# ---------------------------------------------------------------------------

parser = argparse.ArgumentParser(description="Run LLM-as-a-Judge evaluation on OEG human eval data.")
parser.add_argument("--variant", default="local", type=str,
    help='Inference variant - A: "local" (vLLM), or variant B: "api" (OpenRouter).',)
parser.add_argument("--model", default="google/gemma-4-26B-A4B-it", type=str,
    help='Model name. Eg. "Qwen/Qwen3-8B" (A) or "meta-llama/llama-4-maverick" (B)'
         'Part after "/" is also used as judge_model_name in output CSV.',)
parser.add_argument("--model_name_suffix", default="_h23", type=str,
    help='Suffix appended to base model name in judge_model_name column. E.g. "_p_csde". Empty = no suffix.'
         "Suffix is a label that you use to distinguishing the run's subvariant parameters of given model"
         'Eg. "lama-4-maverick_pcsde" would be indicated in the output CSV'
         'Can be empty, or use something short and/or guiding yourself what the run was about',)
parser.add_argument("--concurrency", default=32, type=int,
    help="Number of concurrent API requests (variant B only).",)
parser.add_argument("--batch_size", default=8, type=int,
    help="Batch size for local inference (variant A only). Computed from VRAM if None.",)
parser.add_argument("--max_rows", default=10, type=int,
    help="Process only first N rows per locale. None means: all.",)
parser.add_argument("--locale", default=["cs_CZ", "en_US"], nargs="+",
    help='Locale(s) to process, e.g. ["cs_CZ", "en_US"], or ["all"].'
         'It allows to narrow the inference just for few chosen languages (and their order, too)',)
parser.add_argument("--temperature", default=0.0, type=float,
    help="Temperature for model.",)
parser.add_argument("--output_csv", default="oeg_judge_outloc46_2_submission_data.csv", type=str,
    help="Path to output CSV file.",)
parser.add_argument("--data_dir", default="oeg_human_eval_raw_data", type=str,
    help="Directory with data_<locale>.csv files. Should not be changed, normally",)
parser.add_argument("--template_variant", default="per_locale", type=str,
    help='Template variant: "default" (one English templates for all languages) or '
         '"per_locale" (locale-specific templates, if available, if not, English template is used).',)
parser.add_argument("--llm_log", default="run_judge46_2.log", type=str,
    help='File for LLM I/O logging (exact prompt + raw response). Eg. "run_judge15.log". None = off.',)

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

#LLM's logging
_llm_log_fh = None  # otevírá se v main()

def _log_llm_io(prompt: str, raw_response: str) -> None:
    if _llm_log_fh is None:
        return
    _llm_log_fh.write(
        f"\n{'='*80}\n"
        f">>> PROMPT:\n{prompt}\n"
        f"{'─'*80}\n"
        f"<<< RESPONSE:\n{raw_response}\n"
    )
    _llm_log_fh.flush()

# Remap CUDA_VISIBLE_DEVICES if set to UUID instead of integer index.
# Metacentrum nodes sometimes export GPU UUIDs (e.g. "GPU-1cad794e-...")
# which confuse vLLM and transformers. Remapping to "0,1,..." fixes this.
_cvd = os.environ.get("CUDA_VISIBLE_DEVICES", "")
if _cvd and not _cvd.replace(",", "").isdigit():
    _remapped = ",".join(str(i) for i in range(len(_cvd.split(","))))
    os.environ["CUDA_VISIBLE_DEVICES"] = _remapped
    # Must be set before any CUDA-aware library is imported
    logger.info("CUDA_VISIBLE_DEVICES remapped: %r → %r", _cvd, _remapped)

#Note - the Remap solved when Metacentrum node exhibited UUID this way:
#
# (139env) (BOOKWORM).../llm_judge$ echo $CUDA_VISIBLE_DEVICES
# GPU-1cad794e-e425-8f4b-3a02-a512bba3497a

# This hack solves the problem:
# (139env) (BOOKWORM).../llm_judge$ CUDA_VISIBLE_DEVICES=0
# 0
# , but is tedious. The new above code should work always.


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

MODEL_MAX_TOKENS = 124000   # hard limit for Llama 3.1 8B is 128K (max_position_embeddings)

CRITERIA = ["instruction_following", "naturalness", "coherence"]

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

LANGUAGE_LOCALE_TO_LOCALE = {
    "Egyptian Arabic":            "ar_EG",
    "Bangla (Bangladesh)":        "bn_BD",
    "Czech (Czechia)":            "cs_CZ",
    "German (Germany)":           "de_DE",
    "English (United States)":    "en_US",
    "Hindi (India)":              "hi_IN",
    "Indonesian (Indonesia)":     "id_ID",
    "Japanese (Japan)":           "ja_JP",
    "Russian (Russia)":           "ru_RU",
    "Simplified Chinese (China)": "zh_CN",
}

try:
    _tpl = importlib.import_module(TEMPLATE_FILENAME) #all templates imported from HERE !!!
    JUDGE_TEMPLATES = _tpl.JUDGE_TEMPLATES
    LOCALE_TEMPLATES = _tpl.LOCALE_TEMPLATES
    logger.info("Loaded templates from %s.py", TEMPLATE_FILENAME)
except (ImportError, AttributeError):                 #fallback case
    logger.warning("%s.py not found – using built-in fallback.", TEMPLATE_FILENAME)
    LOCALE_TEMPLATES = {}
    JUDGE_TEMPLATES = {
        "instruction_following": {
            "default": (
                "Score the response generated by a system to a user's request in {language} "
                "on a likert scale from 1 to 7. The quality levels associated with numerical "
                "scores are provided below:\n\n"
                "7: The response fully adheres to all instructions that the user provided.\n"
                "5: The chatbot mostly followed the instructions, conforming to the main points "
                "of the request but missing some details.\n"
                "3: The chatbot followed only a small portion of the instructions or missed "
                "important points.\n"
                "1: The chatbot entirely disregarded the instructions; the response appears to "
                "have no relation to the user's request or is not in {language}.\n\n"
                "Return only the score and nothing else.\n\n"
                "Prompt: {input}\n"
                "Response: {response}\n\n"
                "Score (1-7):"
            ),
        },
        "naturalness": {
            "default": (
                "Score the response generated by a system to a user's request in {language} "
                "on a likert scale from 1 to 7. The quality levels associated with numerical "
                "scores are provided below:\n\n"
                "7: The response represents fluent {language} text that might have been written "
                "by a native human speaker.\n"
                "5: The response has some disfluencies that are noticeable but don't significantly "
                "hinder understanding the response.\n"
                "3: The response is highly disfluent. There are several grammatical errors. Most "
                "of the meaning can be determined, but only with conscious effort.\n"
                "1: The response is incomprehensible or is not in {language}.\n\n"
                "Return only the score and nothing else.\n\n"
                "Prompt: {input}\n"
                "Response: {response}\n\n"
                "Score (1-7):"
            ),
        },
        "coherence": {
            "default": (
                "Score the response generated by a system to a user's request in {language} "
                "on a likert scale from 1 to 7. The quality levels associated with numerical "
                "scores are provided below:\n\n"
                "7: The response is logically sound and appropriately structured with a clear "
                "sequence of nicely connected ideas and topics with no leaps in reasoning.\n"
                "5: The response is generally well-structured and has a generally clear overall "
                "progression of ideas, but introduces a few logical gaps, or suddenly switches "
                "topics without an appropriate transition.\n"
                "3: The response lacks an overall flow, and/or has multiple noticeable jumps "
                "between topics. It is possible to discern some relevant ideas, but the overall "
                "purpose of the response is incoherent.\n"
                "1: The response has no overall structure, is in no way logically sound, and/or "
                "can be divided into many mostly-unrelated sections. It is difficult to identify "
                "any points the text is trying to make.\n\n"
                "Return only the score and nothing else.\n\n"
                "Prompt: {input}\n"
                "Response: {response}\n\n"
                "Score (1-7):"
            ),
        },
    }
#end try-except


OUTPUT_FIELDNAMES = [
    "judge_model_name",
    "criterion",
    "submission_system_name",
    "original_instance_id",
    "locale",
    "score",
]

# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------


def get_judge_template(criterion: str, locale: str, template_variant: str = "default") -> str:
    """
    Return the judge prompt template for a given criterion and locale.

    If template_variant == 'default', locale is ignored and the default
    (English) template is returned. Otherwise, falls back to 'default'
    if no locale-specific template is available.
    """
    templates_for_criterion = JUDGE_TEMPLATES[criterion]
    if template_variant == "default":
        return templates_for_criterion["default"]
    # per_locale: try LOCALE_TEMPLATES, otherwise fallback to default (EN)
    locale_template = LOCALE_TEMPLATES.get(criterion, {}).get(locale, "")
    if locale_template:
        return locale_template
    return templates_for_criterion["default"]

    # templates_for_criterion = JUDGE_TEMPLATES[criterion]
    # if template_variant == "default":
    #     return templates_for_criterion["default"]
    # return templates_for_criterion.get(locale, templates_for_criterion["default"])


def build_prompt(criterion: str, locale: str, input_text: str,
                 response_text: str, template_variant: str = "default") -> str:
    """Fill in a judge template with actual content."""
    language = LOCALE_TO_LANGUAGE[locale]
    template = get_judge_template(criterion, locale, template_variant)
    return template.format(language=language, input=input_text, response=response_text)

#original parse_score for non-reasoning models
# def parse_score(raw: str, context: str = "") -> tuple[float, bool]:
#     """
#     Extract the first number from raw model output.
#     Returns (score, used_fallback).
#     Score is clipped to [1.0, 7.0].
#     """
#     match = re.search(r"\d+\.?\d*", raw.strip())
#     if match:
#         score = float(match.group())
#         score = max(min(score, 7.0), 1.0)
#         return score, False
#     # Fallback
#     score = float(random.randint(1, 7))
#     logger.warning(
#         "Score parsing FAILED for output %r (context: %s). Using random fallback %g.",
#         raw[:80], context, score,
#     )
#     return score, True

# PŮVODNÍ:
# def parse_score(raw: str, context: str = "") -> tuple[float, bool]:
#     """
#     Extract the first number from raw model output.
#     Returns (score, used_fallback).
#     Score is clipped to [1.0, 7.0].
#     """
#     match = re.search(r"\d+\.?\d*", raw.strip())
#     if match:
#         score = float(match.group())
#         score = max(min(score, 7.0), 1.0)
#         return score, False
#     # Fallback
#     score = float(random.randint(1, 7))
#     logger.warning(
#         "Score parsing FAILED for output %r (context: %s). Using random fallback %g.",
#         raw[:80], context, score,
#     )
#     return score, True

# NOVÉ:
# def parse_score(raw: str, context: str = "") -> tuple[float, bool]:
#     """
#     Extract score from raw model output.
#     With reasoning models: looks for score after </think> tag.
#     Falls back to searching full output if </think> missing (truncated).
#     Score is clipped to [1.0, 7.0].
#     Returns (score, used_fallback).
#     """
#     think_end = raw.find("</think>")
#     search_text = raw[think_end + len("</think>"):] if think_end != -1 else raw
#     match = re.search(r"\b([1-7])\b", search_text.strip())
#     if match:
#         return float(match.group(1)), False
#     # Fallback: hledej v celém raw (thinking mohl být oříznut)
#     match = re.search(r"\b([1-7])\b", raw.strip())
#     if match:
#         logger.warning(
#             "Score found in thinking block (</think> missing?) for %s.", context
#         )
#         return float(match.group(1)), True
#     score = float(random.randint(1, 7))
#     logger.warning(
#         "Score parsing FAILED for output %r (context: %s). Using random fallback %g.",
#         raw[:80], context, score,
#     )
#     return score, True

# Překlad nativních číslic → arabské ASCII
_DIGIT_MAP = str.maketrans(
    "০১২৩৪৫৬৭৮৯"   # bengálské    (bn_BD)
    "٠١٢٣٤٥٦٧٨٩"   # arabsko-ind. (ar_EG)
    "०१२३४५६७८९",  # dévanágarské (hi_IN)
    "0123456789"
    "0123456789"
    "0123456789",
)

# New implementation
def parse_score(raw: str, context: str = "") -> tuple[float, bool]:
    """
    Extract score from hybrid CoT or plain output.
    1. Přeloží nativní číslice (bengálské, arabské, dévanágarské) na ASCII.
    2. Hledá po </think> tagu, pokud je přítomen.
    3. Hledá číslo 1–7 na posledním neprázdném řádku.
    4. Fallback: poslední výskyt 1–7 v celém textu.
    5. Fallback: náhodné skóre.
    """
    # 1. Překlad nativních číslic
    text = raw.translate(_DIGIT_MAP)

    # 2. Odřízni <think> blok (Qwen) pokud přítomen, or </thought> for Gemma
    # think_end = text.find("</think>")

    # #this is buggy
    # think_end = max(text.find("</think>"), text.find("</thought>"))
    # search_text = text[think_end + len("</think>"):] if think_end != -1 else text

    # Correct version:
    _think_idx   = text.find("</think>")        #for Qwen
    _thought_idx = text.find("</thought>")      #for Gemma

    if _think_idx != -1 and (_thought_idx == -1 or _think_idx >= _thought_idx):
        search_text = text[_think_idx + len("</think>"):]
    elif _thought_idx != -1:
        search_text = text[_thought_idx + len("</thought>"):]
    else:
        search_text = text



    # 3. Poslední neprázdný řádek
    lines = [l.strip() for l in search_text.splitlines() if l.strip()]
    if lines:
        m = re.search(r"\b([1-7])\b", lines[-1])
        if m:
            return float(m.group(1)), False

    # 4. Poslední výskyt v celém search_text
    all_matches = list(re.finditer(r"\b([1-7])\b", search_text))
    if all_matches:
        logger.warning(
            "Score not on last line — using last occurrence in text (context: %s).", context
        )
        return float(all_matches[-1].group(1)), True

    # 5. Fallback do celého raw (thinking mohl být oříznut)
    all_matches = list(re.finditer(r"\b([1-7])\b", text))
    if all_matches:
        logger.warning(
            "Score found only in thinking block (</think> missing?) for %s.", context
        )
        return float(all_matches[-1].group(1)), True

    # 6. Náhodné skóre
    score = float(random.randint(1, 7))
    logger.warning(
        "Score parsing FAILED for output %r (context: %s). Using random fallback %g.",
        raw[:120], context, score,
    )
    return score, True


def load_checkpoint(output_csv: str) -> set:
    """Load existing output CSV and return a set of completed checkpoint keys."""
    done = set()
    path = Path(output_csv)
    if not path.exists():
        return done
    with open(path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            key = (
                row["judge_model_name"],
                row["criterion"],
                row["submission_system_name"],
                row["original_instance_id"],
                row["locale"],
            )
            done.add(key)
    logger.info("Checkpoint: %d rows already done in %s", len(done), output_csv)
    return done


def load_input_data(data_dir: str, locales: list[str],
                    max_rows: int | None) -> list[dict]:
    """
    Load all input CSV files and return a flat list of records.
    Each record has keys: system, prompt, response, doc_id, locale.
    """
    data_path = Path(data_dir)
    all_records = []

    if locales == ["all"]:
        csv_files = sorted(data_path.glob("data_*.csv"))
    else:
        csv_files = []
        for loc in locales:
            p = data_path / f"data_{loc}.csv"
            if p.exists():
                csv_files.append(p)
            else:
                logger.warning("File not found for locale %s: %s", loc, p)

    for csv_file in csv_files:
        # Derive locale from filename: data_cs_CZ.csv → cs_CZ
        stem = csv_file.stem  # e.g. "data_cs_CZ"
        locale = "_".join(stem.split("_")[1:])  # "cs_CZ"

        records_for_locale = []
        with open(csv_file, newline="", encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                records_for_locale.append({
                    "system": row["system"],
                    "prompt": row["prompt"],
                    "response": row["response"],
                    "doc_id": row["doc_id"],
                    "locale": locale,
                })
        # Deduplicate by (system, doc_id) – keep first occurrence
        seen = set()
        deduped = []
        for rec in records_for_locale:
            key = (rec["system"], rec["doc_id"])
            if key not in seen:
                seen.add(key)
                deduped.append(rec)

        if max_rows is not None:
            deduped = deduped[:max_rows]

        logger.info("Loaded %d unique (system, prompt) pairs from %s", len(deduped), csv_file.name)
        all_records.extend(deduped)

    return all_records


# ---------------------------------------------------------------------------
# Variant A: local vLLM 
# ---------------------------------------------------------------------------
 
 
def run_local(args, records: list[dict], done: set, writer, outfile) -> tuple[int, int]:
    """
    Local GPU inference via vLLM (with transformers fallback).
 
    Steps:
      1. Build all prompts, tokenise → compute max_model_len (max + 50).
      2. Initialise vLLM LLM; on failure fall back to transformers pipeline.
      3. Compute batch_size from VRAM formula (unless overridden via --batch_size).
      4. Process tasks_todo in batches, write CSV rows identical to variant B.
      5. Checkpoint/resume via the shared ``done`` set; progress log every 100 rows.
 
    Returns (completed, fallback_count).
    """
    # def _write_row(rec: dict, criterion: str, raw: str) -> None:
    #     nonlocal fallback_count, completed
    #     # prompt není v _write_row k dispozici – proto logovat dřív, v inference loopu

    import math

    # #Function to be used in stage 2 below -  no reasoning
    # def _apply_chat_template(tok, content: str) -> str:
    #     """
    #     Apply chat template in a model-agnostic way.
    #     Tries Qwen3-style thinking suppression first (enable_thinking=False).
    #     Falls back to plain apply_chat_template for models that don't support it
    #     (e.g. Gemma 4, Llama, ...).
    #     """
    #     messages = [{"role": "user", "content": content}]
    #     base_kwargs = dict(tokenize=False, add_generation_prompt=True)
    #     try:
    #         return tok.apply_chat_template(
    #             messages,
    #             enable_thinking=False,
    #             thinking_budget=512,
    #             **base_kwargs,
    #         )
    #     except TypeError:
    #         # Model tokenizer doesn't support thinking kwargs (Gemma 4, Llama, ...)
    #         return tok.apply_chat_template(messages, **base_kwargs)

    # version for reasoning ON
    def _apply_chat_template(tok, content: str) -> str:
        messages = [{"role": "user", "content": content}]
        base_kwargs = dict(tokenize=False, add_generation_prompt=True)
        try:
            return tok.apply_chat_template(
                messages,
                enable_thinking=True,   # reasoning zapnutý, bez budget limitu
                **base_kwargs,
            )
        except TypeError:
            # tokenizer enable_thinking nepodporuje — použij plain template
            return tok.apply_chat_template(messages, **base_kwargs)


    # judge_model_name = args.model.split("/")[-1]
    judge_model_name = args.model.split("/")[-1] + args.model_name_suffix #add suffix
 
    # ------------------------------------------------------------------
    # 1.  Build task list and apply checkpoint filter
    # ------------------------------------------------------------------
    tasks_all: list[tuple[dict, str]] = []
    for rec in records:
        for criterion in CRITERIA:
            tasks_all.append((rec, criterion))
 
    logger.info("Total tasks (before checkpoint): %d", len(tasks_all))
 
    tasks_todo: list[tuple[dict, str]] = []
    for rec, criterion in tasks_all:
        key = (judge_model_name, criterion, rec["system"], rec["doc_id"], rec["locale"])
        if key not in done:
            tasks_todo.append((rec, criterion))
 
    skipped = len(tasks_all) - len(tasks_todo)
    logger.info("Skipping %d already-done tasks. Remaining: %d", skipped, len(tasks_todo))
 
    if not tasks_todo:
        logger.info("Nothing to do. Exiting.")
        return 0, 0
 
    # ------------------------------------------------------------------
    # 2.  Pre-build all prompts (response HTML passed through verbatim)
    # ------------------------------------------------------------------
  
    # Former implementation
    # logger.info("Building all prompts for token-length pre-computation...")
    # all_prompts: list[str] = [
    #     build_prompt(
    #         criterion=criterion,
    #         locale=rec["locale"],
    #         input_text=rec["prompt"],
    #         response_text=rec["response"],   # HTML (<br>, **…**) kept as-is
    #         template_variant=args.template_variant,
    #     )
    #     for rec, criterion in tasks_todo
    # ]

    # # new implementation allowing to suppress reasoning for Qwen models
    # logger.info("Building all prompts for token-length pre-computation...")
    # from transformers import AutoTokenizer as _TplTok
    # _tpl_tok = _TplTok.from_pretrained(args.model)
    # all_prompts: list[str] = [
    #     _tpl_tok.apply_chat_template(
    #         [{"role": "user", "content": build_prompt(
    #             criterion=criterion,
    #             locale=rec["locale"],
    #             input_text=rec["prompt"],
    #             response_text=rec["response"],   # HTML (<br>, **…**) kept as-is
    #             template_variant=args.template_variant,
    #         )}],
    #         tokenize=False,
    #         add_generation_prompt=True,
    #         enable_thinking=False,  # DO NOT ALLOW allow <think>...</think>
    #         thinking_budget=512,   # newly added - cap thinking tokens; prevents runaway reasoning
  
    #     )
    #     for rec, criterion in tasks_todo
    # ]

    #New version for Gemma
    logger.info("Building all prompts for token-length pre-computation...")
    _tpl_tok = _TplTok.from_pretrained(args.model)

    all_prompts: list[str] = [
        _apply_chat_template(       #defined newly above
            _tpl_tok,
            build_prompt(
                criterion=criterion,
                locale=rec["locale"],
                input_text=rec["prompt"],
                response_text=rec["response"],   # HTML (<br>, **…**) kept as-is
                template_variant=args.template_variant,
            ),
        )
        for rec, criterion in tasks_todo
    ]
 
    # ------------------------------------------------------------------
    # 3.  Tokenise → max_model_len
    # ------------------------------------------------------------------
 
    MAX_OUT = 4096   # 64 = no reasoning, 4096 = reasoning 1280 = thinking_budget(512) + buffer pro </think> + digit(~64) + rezerva
    # 1024  # tokens reserved for generation for reasoning model (= max_tokens), originally 10
    logger.info("Tokenising prompts to compute max_model_len (model=%s)...", args.model)
    try:
        from transformers import AutoTokenizer as _AutoTokenizer
        # _pre_tok = _AutoTokenizer.from_pretrained(args.model)
        _pre_tok = _tpl_tok  # same tokenizer, read in section 2 already
        token_lengths = [len(_pre_tok.encode(p, add_special_tokens=False)) for p in all_prompts]
        max_input_len = max(token_lengths)

        # Cut-off prompts exceeding model's hard limit
        max_prompt_tokens = MODEL_MAX_TOKENS - MAX_OUT
        over = sum(1 for l in token_lengths if l > max_prompt_tokens)
        if over:
            logger.warning(
                "%d/%d prompts exceeds %d tokens and will be cut-off.",
                over, len(all_prompts), max_prompt_tokens,
            )
            new_prompts = []
            for p, tlen in zip(all_prompts, token_lengths):
                if tlen > max_prompt_tokens:
                    ids = _pre_tok.encode(p, add_special_tokens=False)[:max_prompt_tokens]
                    p = _pre_tok.decode(ids, skip_special_tokens=True)
                new_prompts.append(p)
            all_prompts = new_prompts
            max_input_len = max_prompt_tokens  # recompute after truncation

    except Exception as tok_err:
        logger.warning("Pre-tokenisation failed (%s). Using default max_model_len=4096.", tok_err)
        max_input_len = 4046

    max_model_len = min(max_input_len + MAX_OUT, MODEL_MAX_TOKENS)
    logger.info("Max prompt length: %d tokens → max_model_len=%d (hard cap: %d).",
                max_input_len, max_model_len, MODEL_MAX_TOKENS)

    #Note that this stage 3 writes cut-off prompts back to  all_prompts 
    #   (reassignment all_prompts = new_prompts). 
    # Both branches of inference in stage 8 read from the same list

    # Former code:
    # logger.info("Tokenising prompts to compute max_model_len (model=%s)...", args.model)
    # try:
    #     from transformers import AutoTokenizer as _AutoTokenizer
    #     _pre_tok = _AutoTokenizer.from_pretrained(args.model)
    #     token_lengths = [len(_pre_tok.encode(p, add_special_tokens=False)) for p in all_prompts]
    #     max_input_len = max(token_lengths)
    # except Exception as tok_err:
    #     # Very conservative safe default if tokeniser unavailable
    #     logger.warning("Pre-tokenisation failed (%s). Using default max_model_len=4096.", tok_err)
    #     max_input_len = 4046
 
    # max_model_len = max_input_len + 50
    # logger.info("Max prompt length: %d tokens → max_model_len=%d", max_input_len, max_model_len)
 

    # ------------------------------------------------------------------
    # 4.  Initialise vLLM; fall back to transformers on any error
    # ------------------------------------------------------------------
    use_vllm = True
    llm = None
 
    try:
        from vllm import LLM, SamplingParams  # type: ignore
        logger.info("Initialising vLLM (model=%s, dtype=auto, max_model_len=%d)...",
                    args.model, max_model_len)
        #original initialization
        # llm = LLM(model=args.model, dtype="auto", max_model_len=max_model_len)

        #no reasoning
        llm = LLM(model=args.model, dtype="auto", max_model_len=max_model_len)

        # #change to reasoning model having a budget limit
        # llm = LLM(
        #     model=args.model,
        #     dtype="auto",
        #     max_model_len=max_model_len,
        #     reasoning_config=ReasoningConfig(
        #         think_start_str="<think>",
        #         think_end_str="</think>",
        #     )
        # )


        logger.info("vLLM ready.")
    except Exception as vllm_err:
        logger.warning(
            "vLLM initialisation failed (%s). Falling back to transformers pipeline.",
            vllm_err,
        )
        use_vllm = False
 
    # ------------------------------------------------------------------
    # 5.  Compute batch_size (if not explicitly provided)
    # ------------------------------------------------------------------
    if args.batch_size is not None:
        batch_size = args.batch_size
        logger.info("Using user-supplied batch_size=%d.", batch_size)
    else:
        # Determine bytes-per-token from actual dtype
        bytes_per_token = 131_072  # default: bfloat16 / fp16
        if use_vllm and llm is not None:
            try:
                model_dtype = str(llm.llm_engine.model_config.dtype).lower()
                if "float32" in model_dtype or "fp32" in model_dtype:
                    bytes_per_token = 262_144
            except AttributeError:
                pass  # keep default
 
        vram_gb = 48
        model_gb = 16
        usable_bytes = (vram_gb * 0.90 - model_gb) * (1024 ** 3)
        batch_size = min(32, max(1, math.floor(usable_bytes / (max_model_len * bytes_per_token))))
        logger.info(
            "Computed batch_size=%d (bytes_per_token=%d, max_model_len=%d, usable=%.1fGB).",
            batch_size, bytes_per_token, max_model_len, usable_bytes / (1024 ** 3),
        )
 
    # ------------------------------------------------------------------
    # 6.  Open output CSV (append; write header only if file is new/empty)
    # ------------------------------------------------------------------
    output_path = Path(args.output_csv)
    write_header = not output_path.exists() or output_path.stat().st_size == 0
    _outfile = open(output_path, "a", newline="", encoding="utf-8")
    _writer = csv.DictWriter(_outfile, fieldnames=OUTPUT_FIELDNAMES)
    if write_header:
        _writer.writeheader()
 
    # ------------------------------------------------------------------
    # 7.  Shared helper: write one result row
    # ------------------------------------------------------------------
    fallback_count = 0
    completed = 0
    start_time = time.time()
 
    def _write_row(rec: dict, criterion: str, raw: str) -> None:
        nonlocal fallback_count, completed
        context_str = f"{rec['system']}/{rec['doc_id']}/{criterion}/{rec['locale']}"
        score, used_fallback = parse_score(raw, context=context_str)
        if used_fallback:
            fallback_count += 1
        _writer.writerow({
            "judge_model_name": judge_model_name,
            "criterion": criterion,
            "submission_system_name": rec["system"],
            "original_instance_id": rec["doc_id"],
            "locale": rec["locale"],
            "score": score,
        })
        completed += 1
 
    def _log_progress() -> None:
        if completed % 100 == 0 or completed == len(tasks_todo):
            elapsed = time.time() - start_time
            rate = completed / elapsed if elapsed > 0 else 0
            remaining = (len(tasks_todo) - completed) / rate if rate > 0 else float("inf")
            logger.info(
                "Progress: %d/%d (%.1f%%) | %.1f rows/s | ETA %.0fs | fallbacks: %d",
                completed, len(tasks_todo),
                100.0 * completed / len(tasks_todo),
                rate, remaining, fallback_count,
            )
 
    # ------------------------------------------------------------------
    # 8.  Inference loop
    # ------------------------------------------------------------------
    try:
        if use_vllm and llm is not None:
            # ---- 8a. vLLM batch inference --------------------------------
            # #no reasoning
            # sampling_params = SamplingParams(
            #     temperature=args.temperature,
            #     max_tokens=64,
            # )

            # #reasoning
            # sampling_params = SamplingParams(  # noqa: F821  (imported above)
            #     temperature=args.temperature,
            #     max_tokens=1280,  #originally 10 for non-reasoning, 1024 for reasoning, 1280 for reasoning + reserve
            #     thinking_token_budget=450,  # hard limit for thinking tokens
            # )

            # SamplingParams — bez thinking_token_budget:
            sampling_params = SamplingParams(
                temperature=args.temperature,
                max_tokens=4096,   # dost prostoru pro libovolně dlouhé myšlení + odpověď
            )

            for batch_start in range(0, len(tasks_todo), batch_size):
                batch_tasks = tasks_todo[batch_start: batch_start + batch_size]
                batch_prompts = all_prompts[batch_start: batch_start + batch_size]
 
                vllm_outputs = llm.generate(batch_prompts, sampling_params)
 
                for idx, ((rec, criterion), vout) in enumerate(zip(batch_tasks, vllm_outputs)):
                    raw = vout.outputs[0].text if vout.outputs else ""
                    _log_llm_io(all_prompts[batch_start + idx], raw)  # logging prompt, idx-th index in a batch
                    _write_row(rec, criterion, raw)
                    _log_progress()

                # for (rec, criterion), vout in zip(batch_tasks, vllm_outputs):
                #     raw = vout.outputs[0].text if vout.outputs else ""
                #     _log_llm_io(batch_prompts[i], raw)   # logging prompt, i-th index in a batch
                #     _write_row(rec, criterion, raw)
                #     _log_progress()
 
                _outfile.flush()
 
        else:
            # ---- 8b. transformers pipeline fallback ----------------------
            import torch  # noqa: F401
            from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline  # type: ignore
 
            logger.info("Loading transformers pipeline for model=%s...", args.model)
            _tok = AutoTokenizer.from_pretrained(args.model)
            # Ensure padding is defined (needed for batched generation)
            if _tok.pad_token_id is None:
                _tok.pad_token_id = _tok.eos_token_id
 
            pipe = pipeline(
                "text-generation",
                model=args.model,
                tokenizer=_tok,
                torch_dtype="auto",
                device_map="auto",
            )
            logger.info("transformers pipeline ready.")
 
            gen_kwargs: dict = {
                "max_new_tokens": 64,  # newly increased from 1024  #non-reasoning models 10, reasoning 1280
                "return_full_text": False,
            }
            if args.temperature > 0.0:
                gen_kwargs["do_sample"] = True
                gen_kwargs["temperature"] = args.temperature
            else:
                gen_kwargs["do_sample"] = False  # greedy
 
            for batch_start in range(0, len(tasks_todo), batch_size):
                batch_tasks = tasks_todo[batch_start: batch_start + batch_size]
                batch_prompts = all_prompts[batch_start: batch_start + batch_size]
 
                # pipe_outputs = pipe(batch_prompts, **gen_kwargs)   #former line
                # pipe_outputs = pipe(batch_prompts, **gen_kwargs, tokenizer=False)   #with reasoning suppression 
                pipe_outputs = pipe(batch_prompts, **gen_kwargs)

                for idx, ((rec, criterion), out) in enumerate(zip(batch_tasks, pipe_outputs)):
                    raw = out[0]["generated_text"] if out else ""
                    _log_llm_io(all_prompts[batch_start + idx], raw)
                    _write_row(rec, criterion, raw)
                    _log_progress()

                #former code
                # for (rec, criterion), out in zip(batch_tasks, pipe_outputs):
                #     # pipeline returns list[list[dict]] for batched input
                #     raw = out[0]["generated_text"] if out else ""
                #     _log_llm_io(batch_prompts[idx], raw) # logging
                #     _write_row(rec, criterion, raw)
                #     _log_progress()
 
                _outfile.flush()
 
    finally:
        _outfile.close()
 
    elapsed_total = time.time() - start_time
    logger.info(
        "Done. %d tasks completed in %.1fs. Fallback scores: %d.",
        completed, elapsed_total, fallback_count,
    )
    logger.info("Output written to: %s", output_path.resolve())

    # Cleanup distributed process group if initialized
    try:
        import torch.distributed as dist
        if dist.is_available() and dist.is_initialized():
            dist.destroy_process_group()
            logger.info("Distributed process group destroyed.")
    except Exception:
        pass  # not critical


    return completed, fallback_count
 


# ---------------------------------------------------------------------------
# Variant B: OpenRouter async API
# ---------------------------------------------------------------------------


async def call_openrouter(
    client: httpx.AsyncClient,
    semaphore: asyncio.Semaphore,
    model: str,
    prompt: str,
    temperature: float,
    context: str = "",
) -> tuple[str, int, int]:
    """
    Call OpenRouter API with exponential backoff on 429.
    Returns (raw_text, prompt_tokens, completion_tokens).
    """
    url = "https://openrouter.ai/api/v1/chat/completions"
    api_key = os.environ.get("OPENROUTER_API_KEY", "")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/wmt-mist-oeg",
        "X-Title": "WMT-MIST-OEG Judge",
    }
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 1280,       #10 for non-reasoning, 1024 for reasoning, 1280 for reasoning w a reserve
        "temperature": temperature,
        # "reasoning": {"exclude": True},   # ← added to disable thinking
    }

    backoff = 1.0
    max_retries = 8
    async with semaphore:
        for attempt in range(max_retries):
            try:
                resp = await client.post(url, headers=headers, json=payload, timeout=60.0)
                if resp.status_code == 429:
                    wait = backoff * (2 ** attempt) + random.uniform(0, 0.5)
                    logger.warning("Rate limited (429). Waiting %.1fs (attempt %d).", wait, attempt + 1)
                    await asyncio.sleep(wait)
                    continue
                resp.raise_for_status()
                data = resp.json()
                raw = data["choices"][0]["message"]["content"]
                _log_llm_io(prompt, raw)   # ← logging call
                usage = data.get("usage", {})
                pt = usage.get("prompt_tokens", 0)
                ct = usage.get("completion_tokens", 0)
                return raw, pt, ct
            except httpx.HTTPStatusError as e:
                if attempt == max_retries - 1:
                    logger.error("HTTP error for %s: %s", context, e)
                    return "", 0, 0
                await asyncio.sleep(backoff * (2 ** attempt))
            except Exception as e:
                if attempt == max_retries - 1:
                    logger.error("Request error for %s: %s", context, e)
                    return "", 0, 0
                await asyncio.sleep(backoff * (2 ** attempt))
    return "", 0, 0


async def main_async(args):
    # judge_model_name = args.model.split("/")[-1]
    judge_model_name = args.model.split("/")[-1] + args.model_name_suffix  #add suffix
    records = load_input_data(args.data_dir, args.locale, args.max_rows)

    # Build full task list (record × criterion)
    tasks_all = []
    for rec in records:
        for criterion in CRITERIA:
            tasks_all.append((rec, criterion))

    total_tasks = len(tasks_all)
    logger.info("Total tasks (before checkpoint): %d", total_tasks)

    # Load checkpoint
    done = load_checkpoint(args.output_csv)

    # Filter already-done tasks
    tasks_todo = []
    for rec, criterion in tasks_all:
        key = (judge_model_name, criterion, rec["system"], rec["doc_id"], rec["locale"])
        if key not in done:
            tasks_todo.append((rec, criterion))

    skipped = total_tasks - len(tasks_todo)
    logger.info("Skipping %d already-done tasks. Remaining: %d", skipped, len(tasks_todo))

    if not tasks_todo:
        logger.info("Nothing to do. Exiting.")
        return

    # Open output file (append if exists, write header only if new)
    output_path = Path(args.output_csv)
    write_header = not output_path.exists() or output_path.stat().st_size == 0

    outfile = open(output_path, "a", newline="", encoding="utf-8")
    writer = csv.DictWriter(outfile, fieldnames=OUTPUT_FIELDNAMES)
    if write_header:
        writer.writeheader()

    semaphore = asyncio.Semaphore(args.concurrency)
    total_prompt_tokens = 0
    total_completion_tokens = 0
    fallback_count = 0
    completed = 0
    start_time = time.time()

    async with httpx.AsyncClient() as client:

        async def process_task(rec: dict, criterion: str):
            nonlocal total_prompt_tokens, total_completion_tokens, fallback_count, completed

            prompt_text = build_prompt(
                criterion=criterion,
                locale=rec["locale"],
                input_text=rec["prompt"],
                response_text=rec["response"],
                template_variant=args.template_variant,
            )
            context_str = f"{rec['system']}/{rec['doc_id']}/{criterion}/{rec['locale']}"

            raw, pt, ct = await call_openrouter(
                client, semaphore, args.model, prompt_text,
                args.temperature, context=context_str,
            )

            score, used_fallback = parse_score(raw, context=context_str)
            if used_fallback:
                fallback_count += 1

            total_prompt_tokens += pt
            total_completion_tokens += ct
            completed += 1

            row = {
                "judge_model_name": judge_model_name,
                "criterion": criterion,
                "submission_system_name": rec["system"],
                "original_instance_id": rec["doc_id"],
                "locale": rec["locale"],
                "score": score,
            }
            writer.writerow(row)
            outfile.flush()

            # Progress logging every 100 completions
            if completed % 100 == 0 or completed == len(tasks_todo):
                elapsed = time.time() - start_time
                rate = completed / elapsed if elapsed > 0 else 0
                remaining = (len(tasks_todo) - completed) / rate if rate > 0 else float("inf")
                logger.info(
                    "Progress: %d/%d (%.1f%%) | %.1f req/s | ETA %.0fs | "
                    "tokens: %dK prompt / %d completion | fallbacks: %d",
                    completed, len(tasks_todo),
                    100.0 * completed / len(tasks_todo),
                    rate, remaining,
                    total_prompt_tokens // 1000,
                    total_completion_tokens,
                    fallback_count,
                )

        # Run all tasks concurrently (semaphore controls parallelism)
        await asyncio.gather(*[process_task(rec, crit) for rec, crit in tasks_todo])

    outfile.close()

    elapsed_total = time.time() - start_time
    logger.info(
        "Done. %d tasks completed in %.1fs. "
        "Total tokens: %dK prompt / %d completion. "
        "Fallback scores: %d.",
        completed, elapsed_total,
        total_prompt_tokens // 1000,
        total_completion_tokens,
        fallback_count,
    )
    logger.info("Output written to: %s", output_path.resolve())


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------


def main(args):

    global _llm_log_fh
    if args.llm_log:
        _llm_log_fh = open(args.llm_log, "a", encoding="utf-8")
        logger.info("LLM I/O logging → %s", args.llm_log)
    try:
        # ... původní kód main() ...
        logger.info("Starting run_judge.py | variant=%s | model=%s", args.variant, args.model)
        logger.info(
            "Settings: locale=%s | max_rows=%s | concurrency=%s | output=%s",
            args.locale, args.max_rows, args.concurrency, args.output_csv,
        )

        if args.variant == "local":
            records = load_input_data(args.data_dir, args.locale, args.max_rows)
            done = load_checkpoint(args.output_csv)
            run_local(args, records, done, None, None)
        elif args.variant == "api":
            asyncio.run(main_async(args))
        else:
            raise ValueError(f"Unknown variant: {args.variant!r}. Use 'local' or 'api'.")
        # ... původní kód main() ...
    finally:
        if _llm_log_fh:
            _llm_log_fh.close()
            _llm_log_fh = None


if __name__ == "__main__":
    main_args = parser.parse_args([] if "__file__" not in globals() else None)
    main(main_args)