"""
run_judge_transf.py
-------------------
LLM-as-a-Judge inference script for the OEG multilingual evaluation pipeline.

For each (prompt, response, locale) row in the input CSVs and each of the three
criteria (instruction_following, naturalness, coherence) the script:
  1. Fills the appropriate judge prompt template.
  2. Passes the filled template to a local HuggingFace Transformers text-generation
     pipeline (i.e. a GPU-resident LLM).
  3. Parses the numeric score (1-7) from the model output.
  4. Appends the result to the output CSV in the format expected by
     judge_human_agreement.py.

Supports checkpoint/resume: already-scored rows are skipped on restart.
"""

# 1. IMPORTS
import argparse
import csv
import glob
import importlib.util
import logging
import os
import random
import re
import sys
import time
from pathlib import Path

import torch
from dotenv import load_dotenv
from transformers import pipeline

# for Qwen/Qwen3-8B
# Uniquely support of seamless switching between thinking mode (for complex logical reasoning,
# math, and coding) and non-thinking mode (for efficient, general-purpose dialogue) within single model,

# 2. CLI ARGUMENT PARSER  
parser = argparse.ArgumentParser(description="Run LLM-as-a-Judge evaluation on OEG human eval data.")
parser.add_argument("--model", default="Qwen/Qwen3-8B", type=str,
    help='Model name. Eg. "Qwen/Qwen3.5-9B"'
         'It is usually taken from the left top corner of model page on HuggingFace'
         'Part after "/" program uses as judge_model_name in output CSV.',)
parser.add_argument("--model_name_suffix", default="_h13", type=str,
    help='Suffix appended to base model name in judge_model_name column. E.g. "_h13". Empty = no suffix.'
         "Suffix is a label that you use to distinguishing the run's subvariant parameters of given model"
         'Eg. "Qwen3.5-9B_h13" would be indicated in the output CSV'
         'Can be empty, or use something short and/or guiding yourself what the run was about',)
parser.add_argument("--batch_size", default=24, type=int,
    help="Batch size for local inference",)
parser.add_argument("--max_rows", default=None, type=int,
    help="Process only first N rows per locale. None means: all.",)
parser.add_argument("--locale", default=["all"], nargs="+",
    help='Locale(s) to process, e.g. ["cs_CZ", "en_US"], or ["all"].'
         'It allows to narrow the inference just for few chosen languages (and their order, too)',)
parser.add_argument("--temperature", default=0.0, type=float,
    help="Temperature for model. Given him as the parameter",)
parser.add_argument("--output_csv", default="oeg_judge_outloc66_9_submission_data.csv", type=str,
    help="Path to output CSV file.",)
parser.add_argument("--llm_log", default="run_judge_transf66_9.log", type=str,
    help='File for LLM I/O logging (exact prompt + raw response). Eg. "run_judge_transf61.log". None = off.',)

# 3. FILE-LEVEL CONSTANTS
# Name of the external file (without .py extension) that holds JUDGE_TEMPLATES
# and LOCALE_TEMPLATES.  The file is expected to reside in the same directory
# as this script.
TEMPLATE_FILENAME = "judge_templates_locales_hybrid13"

# Directory that contains data_<locale>.csv input files.
INPUT_FILES_DIRECTORY = "oeg_human_eval_raw_data"

# How many extra tokens to reserve for the model's answer on top of the maximum
# input length found across all filled templates.
TOKENS_RESERVE = 50 #can be significantly larger, eg. 1280 for thinking models etc.

# Criteria evaluated per row – order is preserved in the output CSV.
CRITERIA = ["instruction_following", "naturalness", "coherence"]


# 4. LOCALE / LANGUAGE MAPPINGS
# locale code (as used in judge CSV columns) → human-readable language name
# used to fill the {language} placeholder inside judge templates.
LOCALE_TO_LANGUAGE: dict[str, str] = {
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

# language_locale value (column in data_*.csv) → locale code used in output CSV
LANGUAGE_LOCALE_TO_LOCALE: dict[str, str] = {
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

# 5. LOGGING SETUP
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

# 6. HELPER: LOAD TEMPLATE MODULE DYNAMICALLY
def load_template_module(filename_stem: str):
    """
    Dynamically import `filename_stem`.py from the same directory as this
    script and return the loaded module object.
    """
    script_dir = Path(__file__).resolve().parent if "__file__" in globals() else Path.cwd()
    module_path = script_dir / f"{filename_stem}.py"
    if not module_path.exists():
        raise FileNotFoundError(
            f"Template file not found: {module_path}\n"
            "Make sure TEMPLATE_FILENAME points to the correct file."
        )
    spec = importlib.util.spec_from_file_location(filename_stem, module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

# 7. HELPER: GET JUDGE TEMPLATE TEXT
def get_judge_template(
    criterion: str,
    locale: str,
    judge_templates: dict,
    locale_templates: dict,
) -> str:
    """
    Return the judge prompt template string for the given criterion and locale.
    Either locale specific, or the English default one.

    Priority:
      1. locale_templates[criterion][locale]  if non-empty
      2. judge_templates[criterion]["default"]  (English fallback)
    """
    locale_text = locale_templates.get(criterion, {}).get(locale, "")
    if locale_text:
        return locale_text
    return judge_templates[criterion]["default"]


# 8. SCORE PARSING (exact implementation required by the spec)
# Digit translation table: native script digits → ASCII digits
_DIGIT_MAP = str.maketrans(
    "০১২৩৪৫৬৭৮৯"    # Bangla  (bn_BD)
    "٠١٢٣٤٥٦٧٨٩"    # Arabic script digits (ar_EG)
    "०१२३४५६७८९",   # Devanagari (hi_IN)
    "0123456789"
    "0123456789"
    "0123456789",
)


def parse_score(raw: str, context: str = "") -> tuple[float, bool]:
    """
    Extract a 1-7 integer score from a (possibly chain-of-thought) model output.
    Steps:
      1. Translate native-script digits (Bangla, Arabic, Devanagari) to ASCII.
      2. If a </think> or </thought> closing tag is present, restrict the search
         to the text that follows it (skip the thinking block).
      3a. Find a 1-7 digit on the *first* non-empty line (models that answer first,
          then explain — e.g. "6\n\nExplanation: ...").
      3b. Find a 1-7 digit on the *last* non-empty line (models that reason first,
          then conclude).
      4. Fallback: last occurrence of 1-7 anywhere in the remaining text.
      5. Fallback: last occurrence of 1-7 in the full raw text (thinking block
         included — handles models that omit the closing </think> tag).
      6. Last-resort fallback: random integer 1-7 (should be extremely rare).
    Returns:
        (score, is_fallback) — is_fallback=True means a fallback was used.
    """
    # Step 1 – normalise native digits to ASCII
    text = raw.translate(_DIGIT_MAP)

    # Step 2 – locate the end of the thinking block, if any
    _think_idx   = text.find("</think>")      # Qwen-style thinking tag
    _thought_idx = text.find("</thought>")    # Gemma-style thinking tag

    if _think_idx != -1 and (_thought_idx == -1 or _think_idx >= _thought_idx):
        search_text = text[_think_idx + len("</think>"):]
    elif _thought_idx != -1:
        search_text = text[_thought_idx + len("</thought>"):]
    else:
        search_text = text

    lines = [l.strip() for l in search_text.splitlines() if l.strip()]

    # Step 3a – look on the *first* non-empty line
    # Handles models that emit the score first, then explain (e.g. "6\n\nExplanation: ...")
    if lines:
        m = re.search(r"\b([1-7])\b", lines[0])
        if m:
            return float(m.group(1)), False    # clean parse, no fallback

    # Step 3b – look on the *last* non-empty line
    # Handles models that reason first, then conclude with a score
    if lines:
        m = re.search(r"\b([1-7])\b", lines[-1])
        if m:
            return float(m.group(1)), False    # clean parse, no fallback

    # Step 4 – last occurrence of a valid score anywhere in search_text
    all_matches = list(re.finditer(r"\b([1-7])\b", search_text))
    if all_matches:
        logger.warning(
            "Score not on first or last line — using last occurrence in text (context: %s).", context
        )
        return float(all_matches[-1].group(1)), True

    # Step 5 – look in the thinking block itself (closing tag may be missing)
    all_matches = list(re.finditer(r"\b([1-7])\b", text))
    if all_matches:
        logger.warning(
            "Score found only in thinking block (</think> missing?) for %s.", context
        )
        return float(all_matches[-1].group(1)), True

    # Step 6 – random fallback (score parsing completely failed)
    score = float(random.randint(1, 7))
    logger.warning(
        "Score parsing FAILED for output %r (context: %s). Using random fallback %g.",
        raw[:120], context, score,
    )
    return score, True


# 9. HELPER: LOAD EXISTING OUTPUT CSV (checkpoint)
def load_checkpoint(output_csv: str) -> set[tuple]:
    """
    Read already-completed rows from output_csv and return a set of 5-tuples:
        (judge_model_name, criterion, submission_system_name,
         original_instance_id, locale)

    These tuples are used to skip rows that were already scored in a previous run.
    """
    done: set[tuple] = set()
    if not os.path.exists(output_csv):
        return done
    with open(output_csv, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = (
                row["judge_model_name"],
                row["criterion"],
                row["submission_system_name"],
                row["original_instance_id"],
                row["locale"],
            )
            done.add(key)
    logger.info("Checkpoint: %d rows already present in %s — will be skipped.", len(done), output_csv)
    return done

# 10. HELPER: DETERMINE WHICH LOCALES TO PROCESS
def resolve_locales(locale_arg: list[str], input_dir: str) -> list[str]:
    """
    Expand ["all"] to every locale found in input_dir, or validate the
    explicitly provided locale codes.
    Returns an ordered list of locale strings (e.g. ["cs_CZ", "en_US"]).
    """
    if locale_arg == ["all"]:
        csv_files = sorted(glob.glob(os.path.join(input_dir, "data_*.csv")))
        locales = []
        for path in csv_files:
            stem = Path(path).stem          # "data_cs_CZ"
            locale = stem[len("data_"):]    # "cs_CZ"
            locales.append(locale)
        if not locales:
            raise FileNotFoundError(f"No data_*.csv files found in {input_dir!r}.")
        return locales
    return locale_arg


# 11. MAIN LOGIC
def main(args):
    # 11.1  Authenticate with HuggingFace (token from .env)
    load_dotenv()
    hf_token = os.getenv("HF_TOKEN")
    if hf_token:
        logger.info("HuggingFace token loaded from .env.")
    else:
        logger.warning("HF_TOKEN not found in .env — private/gated models may fail.")

    # 11.2  Derive judge model name that will appear in the output CSV
    # Take everything after the last "/" in the --model argument, then
    # append the optional suffix.  Examples:
    #   "meta-llama/llama-4-maverick" + "_h13"  →  "llama-4-maverick_h13"
    #   "Qwen/Qwen3.5-9B"             + ""       →  "Qwen3.5-9B"
    base_name = args.model.split("/")[-1]
    judge_model_name = base_name + args.model_name_suffix
    logger.info("judge_model_name = %r", judge_model_name)

    # 11.3  Load judge prompt templates from the external .py file
    logger.info("Loading templates from %s.py …", TEMPLATE_FILENAME)
    tmpl_module = load_template_module(TEMPLATE_FILENAME)
    JUDGE_TEMPLATES  = tmpl_module.JUDGE_TEMPLATES   # always-filled English defaults
    LOCALE_TEMPLATES = tmpl_module.LOCALE_TEMPLATES  # locale-specific overrides (may be "")

    # 11.4  Determine locales to process
    locales = resolve_locales(args.locale, INPUT_FILES_DIRECTORY)
    logger.info("Locales to process: %s", locales)

    # 11.5  Read all input rows
    # Each element: dict with keys matching the input CSV columns.
    all_rows: list[dict] = []
    for locale in locales:
        csv_path = os.path.join(INPUT_FILES_DIRECTORY, f"data_{locale}.csv")
        if not os.path.exists(csv_path):
            logger.warning("Input file not found, skipping: %s", csv_path)
            continue
        with open(csv_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            count = 0
            for row in reader:
                row["_locale"] = locale    # attach the locale code derived from filename
                all_rows.append(row)
                count += 1
                if args.max_rows and count >= args.max_rows:
                    break
        logger.info("  Loaded %d rows from %s.", count, csv_path)

    logger.info("Total input rows: %d", len(all_rows))

    # 11.6  Load checkpoint — skip already-done (judge, criterion, row) combos
    done_keys = load_checkpoint(args.output_csv)


    # 11.6b  Load the tokenizer (lightweight — no model weights, no GPU allocation).
    # We need it here, before building jobs, because apply_chat_template() is called
    # during job construction in 11.7.  The same tokenizer object is later reused in
    # 11.8 for token-length pre-scanning, so we load it only once.
    logger.info("Loading tokenizer for %r …", args.model)
    from transformers import AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained(args.model, token=hf_token)
    logger.info("Tokenizer loaded.")



    # 11.7  Build the full list of jobs: (filled_template, metadata)
    # A "job" is one LLM call: one (row × criterion) combination.
    jobs: list[dict] = []
    for row in all_rows:
        locale      = row["_locale"]
        language    = LOCALE_TO_LANGUAGE.get(locale, locale)
        prompt_text = row["prompt"]
        response_text = row["response"]
        system_name = row["system"]
        doc_id      = row["doc_id"]

        for criterion in CRITERIA:
            checkpoint_key = (judge_model_name, criterion, system_name, doc_id, locale)
            if checkpoint_key in done_keys:
                continue    # already scored in a previous run

            # 1. Read the template string (it is either locale specific, or the default English one)
            template = get_judge_template(criterion, locale, JUDGE_TEMPLATES, LOCALE_TEMPLATES)

            # 2. Fill the judge template with the actual prompt, response, and language.
            # This produces the *human-readable* instruction text — e.g.:
            #   "You are an LLM judge … Score (1-7):"
            # It is NOT yet in the format the model expects on the token level.
            raw_content = template.format(
                language=language,
                input=prompt_text,
                response=response_text,
            )

            # Wrap the filled template in a single-turn chat message and apply the
            # model's chat template.  This is the critical step that was missing
            # before: an instruction-tuned model like'Qwen3-8B' are trained to receive
            # inputs formatted as a structured conversation (with special tokens such
            # as <|im_start|>user … <|im_end|><|im_start|>assistant), NOT as plain
            # text.  Sending raw text bypasses that format and puts the model into
            # an unintended "text completion" mode instead of "instruction following"
            # mode, which produces different — and less reliable — scores.
            #
            # Note: we deliberately use a *single-message* list here, not a
            # multi-turn history list like chat_local.py does.  The judge task is
            # stateless: each (row × criterion) call is fully independent with no
            # conversational context to carry over.  A single {"role": "user", ...}
            # entry is therefore the correct structure.
            #
            # apply_chat_template() with tokenize=False returns a plain string —
            # the exact byte sequence the tokenizer will later encode and send to
            # the GPU.  Storing this string in filled_prompt means the LLM I/O log
            # records precisely what the model received, not just the human-readable
            # template text.
            #
            # enable_thinking=False suppresses Qwen3's chain-of-thought ("thinking")
            # mode.  Without this flag the model may emit a long <think>…</think>
            # reasoning block before the score, which wastes tokens and makes output
            # parsing harder.  thinking_budget=512 is a secondary cap that limits
            # thinking tokens even if thinking were somehow enabled.
            # For models whose tokenizer does not support these kwargs (e.g. Llama,
            # Gemma) the TypeError fallback applies the template without them.
            messages = [{"role": "user", "content": raw_content}]
            try:
                filled_prompt = tokenizer.apply_chat_template(  # <-- key call of apply_chat_template
                    messages,
                    tokenize=False,
                    add_generation_prompt=True,
                    enable_thinking=False,
                    thinking_budget=512,
                )
            except TypeError:
                # Tokenizer does not support thinking-related kwargs — use plain template.
                filled_prompt = tokenizer.apply_chat_template(
                    messages,
                    tokenize=False,
                    add_generation_prompt=True,
                )

            # NOTE: the exact special tokens inserted by apply_chat_template() are model-specific.
            # For example, Qwen3 uses <|im_start|>/<|im_end|>, Llama 3 uses <|start_header_id|>/
            # <|eot_id|>, Gemma uses <start_of_turn>/<end_of_turn>, etc.
            # The correct template for the loaded model is stored in its tokenizer_config.json
            # and applied automatically — do not assume any particular token format in the output,
            # or be prepared to handle all of them somehow.

            jobs.append({                            # <-- here 1 job is created
                "filled_prompt":       filled_prompt,   # <-- chat-formatted string; exact model input to be sent to LLM,
                                                            # Metadata needed to write the output CSV row:
                "judge_model_name":    judge_model_name,    # The name of judge model currently used
                "criterion":           criterion,           # Criterion (on of three)
                "submission_system_name": system_name,      # System which created the response (part of filled_prompt)
                "original_instance_id":   doc_id,           # Hash value, just the reference to connect prompts in locales
                "locale":              locale,              # Locale
                "checkpoint_key":      checkpoint_key,          # The potential identification to check the checkpoint
            })

    logger.info("Jobs to run (after checkpoint skip): %d", len(jobs))
    if not jobs:
        logger.info("Nothing to do. Exiting.")
        return

    # 11.8  Pre-scan all token lengths to determine max_length for the model.
    # The tokenizer was already loaded in 11.6b and is reused here — no second load needed.
    # Because filled_prompt now contains the chat-formatted string (not the raw template
    # text), the token counts measured here accurately reflect what the model will receive.
    logger.info("Pre-scanning token lengths across all %d filled prompts …", len(jobs))

    max_input_tokens = 0
    for job in jobs:
        token_count = len(tokenizer.encode(job["filled_prompt"]))
        if token_count > max_input_tokens:
            max_input_tokens = token_count

    # Add a safety buffer for the model's output (score + optional CoT)
    max_model_len = max_input_tokens + TOKENS_RESERVE
    logger.info(
        "Max input length: %d tokens.  max_model_len = %d (+ %d reserve).",
        max_input_tokens, max_model_len, TOKENS_RESERVE,
    )
    del tokenizer    # free memory before loading the full model

    # 11.9  Open LLM I/O log file (if requested)
    llm_log_enabled = args.llm_log and args.llm_log.lower() != "none"
    llm_log_file = None
    if llm_log_enabled:
        llm_log_file = open(args.llm_log, "a", encoding="utf-8")
        logger.info("LLM I/O log: %s", args.llm_log)

    # 11.10  Load the model as a HuggingFace text-generation pipeline
    # ----------------------------------------------------------------
    # HOW THE MODEL IS LOADED AND CALLED — EDUCATIONAL NOTES
    # ----------------------------------------------------------------
    #
    # We use the high-level `transformers.pipeline` API with:
    #
    #   task="text-generation"
    #       The pipeline accepts a raw text string (or a list of them for
    #       batching) and returns the model's continuation of that text.
    #
    #   device_map="auto"
    #       Accelerate distributes the model layers across all available
    #       GPUs (and optionally CPU RAM) automatically.  For a single-GPU
    #       machine this simply places everything on GPU 0.
    #
    #   torch_dtype=torch.bfloat16
    #       Uses Brain Float 16 precision.  Halves VRAM usage vs. float32
    #       while keeping the same dynamic range as float32 (unlike float16
    #       which can overflow).  Most modern NVIDIA GPUs support bf16.
    #
    #   max_new_tokens
    #       Caps how many tokens the model may generate per call.  For a
    #       judge task the answer is a single digit (1-7) — TOKENS_RESERVE
    #       is deliberately generous to accommodate chain-of-thought models
    #       that reason before emitting their final score.
    #
    #   temperature / do_sample
    #       temperature=0.0 → greedy decoding (deterministic, recommended
    #       for judge tasks for reproducibility).
    #       temperature>0   → random sampling (do_sample=True is set
    #       automatically by the pipeline when temperature > 0).
    #
    #   truncation=True
    #       Silently truncates inputs that exceed the model's context window.
    #       Should not trigger given the pre-scan above, but acts as a safety net.
    #
    # BATCHING:
    #   Passing a Python list of strings to the pipeline triggers batched
    #   inference: all strings in the batch are padded to the same length
    #   and processed in a single GPU forward pass.  This is substantially
    #   faster than calling the model once per string.
    #
    # WHAT IS LOGGED vs. WHAT IS SENT TO THE MODEL:
    #   - `job["filled_prompt"]`  is the *exact* string that enters the
    #     tokenizer and then the model.  Nothing is modified between the
    #     template-filling step (11.7) and this call.
    #   - `raw_text` (extracted below from the pipeline output) is the
    #     *exact* continuation string produced by the model, before any
    #     post-processing.  Both are written verbatim to the LLM log file.
    # ----------------------------------------------------------------

    # Build pipeline kwargs; do_sample=False is set here (at init level) for greedy decoding
    # to avoid the deprecation warning that arises when do_sample is passed both at init
    # and at call time via generation_kwargs.
    pipeline_kwargs = dict(
        task="text-generation",
        model=args.model,
        device_map="auto",              # distribute across available GPU(s) automatically
        dtype=torch.bfloat16,           # bf16: halves VRAM, maintains float32 dynamic range
        token=hf_token,                 # authentication token, some models require authentication
        max_new_tokens=TOKENS_RESERVE,  # model may produce at most TOKENS_RESERVE new tokens
        truncation=True,                # safety-net truncation (should not trigger normally)
        return_full_text=False,         # return only the generated continuation, not the input
    )
    if args.temperature == 0.0:
        pipeline_kwargs["do_sample"] = False   # greedy decoding set at init level — avoids deprecation warning

    # Logger will ignore anything but ERRORs (Suppression of annoying Warnings)
    # It suppresses the Warning: "Both `max_new_tokens` (=50) and `max_length`(=20) seem to have 
    #                             been set. `max_new_tokens` will take precedence."
    logging.getLogger("transformers.generation.utils").setLevel(logging.ERROR)

    logger.info("Loading model %r onto GPU …", args.model)
    judge_pipeline = pipeline(**pipeline_kwargs)    # originates from `from transformers import pipeline` above
    logger.info("Model loaded successfully.")
    logger.info("Model device: %s", judge_pipeline.model.device)  # shows GPU (correct) vs CPU (mistake)

    # The above is the heavy initialization step, not eg. only a lightweight config object. 
    # Concretely, calling pipeline(...) at that point:
        # - Downloads or reads from cache the model weights (potentially tens of gigabytes of 
        #   binary data from HuggingFace Hub or local disk).
        # - Loads the weights into GPU VRAM (distributed across GPUs according to device_map="auto").
        # - Loads the tokenizer associated with the model.
        # - Constructs and returns a callable Pipeline object that wraps both the model and the 
        #   tokenizer together.

    # After this line completes, the model is fully resident in GPU memory and ready to run forward passes. 
    # The returned judge_pipeline object is then used as a function — calling judge_pipeline(batch_prompts, ...) 
    # later triggers the actual tokenization and GPU forward pass for each batch. So the distinction is:
        # - pipeline(...) — one-time setup, loads model into GPU (~seconds to minutes)
        # - judge_pipeline([...]) — repeated inference, runs the model on a batch (~milliseconds to seconds per call)

    # generation_kwargs: additional parameters passed at each inference call.
    # For temperature=0.0 do_sample was already set at pipeline init level above — not repeated here.
    generation_kwargs: dict = {}
    if args.temperature > 0.0:
        generation_kwargs["do_sample"] = True
        generation_kwargs["temperature"] = args.temperature

    # 11.11  Open (or append to) the output CSV
    output_exists = os.path.exists(args.output_csv)
    out_file = open(args.output_csv, "a", newline="", encoding="utf-8")
    out_writer = csv.DictWriter(
        out_file,
        fieldnames=[
            "judge_model_name", "criterion", "submission_system_name",
            "original_instance_id", "locale", "score",
        ],
    )
    if not output_exists:
        out_writer.writeheader()

    # ------------------------------------------------------------------
    # 11.12  Main inference loop with batching
    # ------------------------------------------------------------------
    total_jobs   = len(jobs)
    done_count   = 0
    fallback_count = 0
    start_time   = time.time()

    logger.info("Starting inference.  batch_size=%d, temperature=%g", args.batch_size, args.temperature)

    for batch_start in range(0, total_jobs, args.batch_size):
        batch_jobs = jobs[batch_start : batch_start + args.batch_size]

        # Collect the exact strings that will be sent to the model.
        # This list is what the tokenizer and model actually receive — nothing more,
        # nothing less.  Any change here would break the LLM log's faithfulness.
        batch_prompts: list[str] = [job["filled_prompt"] for job in batch_jobs] # List of "filled_prompt" for each included job 

        # ---- GPU INFERENCE ----
        # The pipeline tokenises `batch_prompts`, runs a batched forward pass on
        # the GPU, and decodes the output token IDs back to text.
        # Each element of `outputs` is a list of dicts; [0]["generated_text"]
        # holds the raw continuation string produced by the model.
        outputs = judge_pipeline(  #each element gives `[0]["generated_text"]` output answer (inside one batch)
            # In our case each element gives just `[0]["generated_text"]` — the model's answer.
            # With different settings, each output dict could also contain:
            #   "generated_token_ids" — raw token IDs (if return_tensors=True)
            #   "score"               — sequence confidence (if num_beams > 1)
            #   "tokens"              — token-level detail (if return_token_type_ids=True)
            #   "conversation"        — chat message history (if input is passed as message
            #                           dicts instead of plain strings, for some instruct models)
            batch_prompts,                  # a plain list of input strings (inside one batch)
            batch_size=len(batch_prompts),  # process all at once on the GPU
            **generation_kwargs,            # do_sample=False (greedy) or do_sample=True + temperature (sampling)
        )
        # ---- END GPU INFERENCE ----

        # Process each (prompt, output) pair in the batch
        for job, prompt_text, output_list in zip(batch_jobs, batch_prompts, outputs):
            # `output_list` is a list with one element (one generation per prompt)
            raw_text: str = output_list[0]["generated_text"]
            # `raw_text` is the EXACT string the model produced — logged verbatim below.

            # Build a short context label for warning messages
            context = (
                f"{job['criterion']}|{job['submission_system_name']}"
                f"|{job['original_instance_id'][:8]}|{job['locale']}"
            )

            # Log exact input and output to the LLM I/O log file
            if llm_log_file:
                llm_log_file.write("=" * 72 + "\n")
                llm_log_file.write(f"CONTEXT: {context}\n")
                llm_log_file.write("--- INPUT (sent to model) ---\n")
                llm_log_file.write(prompt_text + "\n")
                llm_log_file.write("--- OUTPUT (received from model) ---\n")
                llm_log_file.write(raw_text + "\n")
                llm_log_file.flush()

            # Parse score from raw model output
            score, is_fallback = parse_score(raw_text, context=context)
            if is_fallback:
                fallback_count += 1

            # Clamp score to [1.0, 7.0] as a safety measure
            score = max(min(score, 7.0), 1.0)

            # Write result to the output CSV immediately (enables safe resume)
            out_writer.writerow({
                "judge_model_name":       job["judge_model_name"],
                "criterion":              job["criterion"],
                "submission_system_name": job["submission_system_name"],
                "original_instance_id":   job["original_instance_id"],
                "locale":                 job["locale"],
                "score":                  score,
            })
            out_file.flush()    # ensure disk write before next batch

            done_count += 1

        # Progress & ETA logging after each batch
        elapsed = time.time() - start_time
        rate = done_count / elapsed if elapsed > 0 else 0
        remaining = total_jobs - done_count
        eta_sec = remaining / rate if rate > 0 else float("inf")
        logger.info(
            "Progress: %d / %d  (%.1f %%)  |  %.1f rows/s  |  fallbacks: %d  |  ETA: %s",
            done_count, total_jobs,
            100 * done_count / total_jobs,
            rate,
            fallback_count,
            f"{eta_sec:.0f}s" if eta_sec < float("inf") else "?",
        )

    # 11.13  Cleanup
    out_file.close()
    if llm_log_file:
        llm_log_file.close()

    elapsed_total = time.time() - start_time
    logger.info(
        "Done.  %d rows written to %s in %.1f s.  Fallback count: %d.",
        done_count, args.output_csv, elapsed_total, fallback_count,
    )


# 12. ENTRY POINT
if __name__ == "__main__":
    # `[] if "__file__" not in globals() else None`:
    #   - In a normal shell run:  parse_args(None) reads sys.argv[1:]
    #   - In a Jupyter notebook:  "__file__" is absent, so parse_args([])
    #     uses the argument defaults without complaining about notebook argv.
    main_args = parser.parse_args([] if "__file__" not in globals() else None)
    main(main_args)
