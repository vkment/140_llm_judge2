"""
chat_local.py
-------------
Interactive terminal chat with a locally running LLM via Hugging Face Transformers.

The model is loaded once onto the GPU at startup; from then on the user can chat
without restarting the process.  System prompt, temperature, and max response
length can all be changed on the fly via /commands.
"""

# 1. IMPORTS
import argparse
import logging
import os
import sys

import warnings

from dotenv import load_dotenv
import torch
from transformers import pipeline


# 2. CLI ARGUMENT PARSER
parser = argparse.ArgumentParser(
    description="Interactive terminal chat with a local LLM on GPU (Transformers).",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
)
parser.add_argument("--model", default="Qwen/Qwen2.5-3B-Instruct", type=str,
    help='HuggingFace model name or local path. E.g. "Qwen/Qwen2.5-7B-Instruct"')
parser.add_argument("--temperature", default=0.7, type=float,
    help="Sampling temperature. 0.0 = greedy/deterministic, higher = more creative.")
parser.add_argument("--max_tokens", default=4096, type=int,
    help="Hard upper limit on new tokens generated per reply.  "
         "This is a technical safety cap, NOT an instruction to the model — "
         "the model decides reply length itself via the <eos> token and stops "
         "naturally well before this limit in most cases.  "
         "To influence reply length, use the system prompt instead "
         "(e.g. 'Be concise. Answer in 2-3 sentences.').")
parser.add_argument("--system", default="assistant", type=str,
    help="Name of the initial system prompt preset (see SYSTEM_PRESETS in the script).")


# 3. CONSTANTS

# Named system prompt presets.
# Add your own here, or define new ones at runtime with: /system new <name> <text>
SYSTEM_PRESETS: dict[str, str] = {
    "assistant": "You are a helpful assistant.",
    "teacher":   "You are a patient teacher. Explain every concept step by step, "
                 "using simple language and concrete examples.",
    "coder":     "You are an expert programmer. Give concise, correct code with brief explanations.",
    "czech":     "Jsi přátelský asistent. Vždy odpovídej česky, "
                 "i když se tě uživatel ptá v jiném jazyce.",
}


# 4. LOGGING SETUP
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


# 5. HELP TEXT
def print_help() -> None:
    """Print all available in-session commands."""
    print("""
Available commands (type at the chat prompt):
  /help                         Show this help message
  /system <name>                Switch to a named system prompt preset
  /system new <name> <text>     Define a new preset and switch to it immediately
  /system list                  List all available preset names and their texts
  /temp <value>                 Change temperature       e.g.  /temp 0.3
  /max <value>                  Change max new tokens    e.g.  /max 256
  /clear                        Clear conversation history (keeps current settings)
  /mode                         Show all current settings
  /quit  or  /exit              Exit the program
""")


# 6. MAIN LOGIC
def main(args: argparse.Namespace) -> None:

    # ------------------------------------------------------------------
    # 6.1  Validate the requested system prompt preset
    # ------------------------------------------------------------------
    if args.system not in SYSTEM_PRESETS:
        logger.warning(
            "Unknown preset %r — falling back to 'assistant'. Available: %s",
            args.system, list(SYSTEM_PRESETS.keys()),
        )
        args.system = "assistant"

    # ------------------------------------------------------------------
    # 6.2  Load the model pipeline onto the GPU
    #
    # = pipeline() is the heavy one-time initialisation step.  Calling it:
    #   - Downloads or reads from the local cache the model weights
    #     (potentially tens of gigabytes of binary data from HuggingFace Hub).
    #   - Loads those weights into GPU VRAM.
    #     device_map="auto" distributes them across all available GPUs.
    #   - Loads the tokenizer associated with the model.
    #   - Returns a callable Pipeline object that wraps both the model
    #     and the tokenizer together.
    #
    # After this line completes the model is fully resident in GPU memory
    # and ready to answer queries.  All subsequent calls to
    # chat_pipeline(...) are fast (milliseconds to seconds per reply);
    # only this initial load is slow (seconds to minutes, depending on
    # model size and disk speed).
    # ------------------------------------------------------------------
    # Load HF_TOKEN from .env file in the same directory.
    # Without a token, HuggingFace Hub warns about unauthenticated requests
    # and applies stricter rate limits on downloads.
    load_dotenv()
    hf_token: str | None = os.getenv("HF_TOKEN")
    if not hf_token:
        logger.warning("HF_TOKEN not found in .env — proceeding without authentication.")

    # Suppress the "Both max_new_tokens and max_length have been set" message.
    # IMPORTANT: transformers emits this via its own logging system (logger.warning_once),
    # NOT via Python's warnings.warn — so warnings.filterwarnings() has no effect.
    # The correct fix is a logging.Filter on the transformers logger.
    class _SuppressMaxLengthConflict(logging.Filter):
        def filter(self, record: logging.LogRecord) -> bool:
            msg = record.getMessage()
            return not ("max_new_tokens" in msg and "max_length" in msg)

    # Another way how to suppress it
    warnings.filterwarnings("ignore", message=".*both `max_new_tokens` and `max_length`.*")

    logging.getLogger("transformers").addFilter(_SuppressMaxLengthConflict())

    logger.info("Loading model %r onto GPU — this may take a while …", args.model)
    chat_pipeline = pipeline(
        task="text-generation",     # generate text that continues / replies to the input
        model=args.model,           # HuggingFace model name or local path
        device_map="auto",          # spread weights across all available GPUs automatically
        dtype=torch.bfloat16,       # bf16: halves VRAM usage, preserves float32 dynamic range
        token=hf_token,             # HF auth token — enables higher rate limits and private models
    )
    logger.info("Model loaded successfully.  Ready to chat.\n")

    # Read the model's context window size from its configuration.
    # This is the absolute maximum number of tokens (input + output combined)
    # the model can handle in a single forward pass — a hard architectural limit
    # baked into the model weights.  Exceeding it causes SILENT truncation of
    # the oldest tokens in the history.
    max_context_tokens: int = getattr(
        chat_pipeline.model.config, "max_position_embeddings",
        getattr(chat_pipeline.model.config, "max_model_len", 8192),
    )
    logger.info("Model context window: %d tokens.", max_context_tokens)

    # ------------------------------------------------------------------
    # 6.3  Print startup banner and help
    # ------------------------------------------------------------------
    print("=" * 62)
    print("  Local LLM chat  —  type /help for available commands")
    print("=" * 62)
    print_help()

    # ------------------------------------------------------------------
    # 6.4  Mutable session state
    #
    # These three variables hold all settings that can be changed during
    # a session without restarting the program.
    # ------------------------------------------------------------------
    current_preset: str   = args.system       # name of the active system prompt preset
    temperature:    float = args.temperature  # sampling temperature
    max_tokens:     int   = args.max_tokens   # max new tokens the model may generate

    # ------------------------------------------------------------------
    # 6.5  Single Conversation (chat) History
    #
    # `history` is the list of messages passed to the model on every
    # call.  Modern instruct models expect messages in this format:
    #
    #   [
    #     {"role": "system",    "content": "<system instructions for the model>"},
    #     {"role": "user",      "content": "<first user message>"},
    #     {"role": "assistant", "content": "<model reply>"},
    #     {"role": "user",      "content": "<second user message>"},
    #     ...
    #   ]
    #
    # The tokenizer automatically applies the model's chat template to
    # convert this list into a single formatted string before encoding.
    #
    # Growing this list turn by turn is what gives the model its
    # "memory" within a single conversation.
    # NOTE: "system instructions" can be invisible for the user 
    # ------------------------------------------------------------------
    def fresh_history() -> list[dict]:
        """Return a new history list containing only the system prompt."""
        return [{"role": "system", "content": SYSTEM_PRESETS[current_preset]}]

    history: list[dict] = fresh_history()

    # ------------------------------------------------------------------
    # 6.6  Main chat loop
    # ------------------------------------------------------------------
    while True:

        # The prompt string shown to the user reflects all live settings.
        prompt_str = f"[{current_preset} | temp={temperature} | max={max_tokens}]> "

        try:
            user_input = input(prompt_str).strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break

        if not user_input:
            continue  # ignore empty lines

        # --------------------------------------------------------------
        # 6.6.1  Handle /commands — these never reach the model
        # --------------------------------------------------------------
        if user_input.startswith("/"):
            parts = user_input.split(maxsplit=3)  # split into at most 4 tokens
            cmd = parts[0].lower()

            if cmd in ("/quit", "/exit"):
                print("Bye!")
                break

            elif cmd == "/help":
                print_help()

            elif cmd == "/mode":
                turns = (len(history) - 1) // 2  # number of completed user+assistant pairs
                print(f"  system preset : {current_preset}")
                print(f"  system text   : {SYSTEM_PRESETS[current_preset]}")
                print(f"  temperature   : {temperature}")
                print(f"  max_tokens    : {max_tokens}  (technical cap, not an instruction to the model)")
                print(f"  history turns : {turns}")

            elif cmd == "/clear":
                history = fresh_history()
                print("  Conversation history cleared.")

            elif cmd == "/temp":
                if len(parts) < 2:
                    print("  Usage: /temp <value>   e.g. /temp 0.3")
                else:
                    try:
                        temperature = float(parts[1])
                        print(f"  Temperature set to {temperature}.")
                    except ValueError:
                        print(f"  Invalid value {parts[1]!r} — expected a number.")

            elif cmd == "/max":
                if len(parts) < 2:
                    print("  Usage: /max <value>   e.g. /max 256")
                else:
                    try:
                        max_tokens = int(parts[1])
                        print(f"  Max tokens set to {max_tokens}.")
                    except ValueError:
                        print(f"  Invalid value {parts[1]!r} — expected an integer.")

            elif cmd == "/system":
                if len(parts) < 2:
                    print("  Usage: /system <name>  |  /system new <name> <text>  |  /system list")

                elif parts[1].lower() == "list":
                    print("  Available presets:")
                    for name, text in SYSTEM_PRESETS.items():
                        marker = " *" if name == current_preset else ""
                        print(f"    {name:14s}{text[:55]}{marker}")

                elif parts[1].lower() == "new":
                    # /system new <name> <text of the prompt>
                    if len(parts) < 4:
                        print("  Usage: /system new <name> <text>")
                    else:
                        new_name = parts[2]
                        new_text = parts[3]
                        SYSTEM_PRESETS[new_name] = new_text
                        current_preset = new_name
                        history = fresh_history()
                        print(f"  Preset {new_name!r} created and activated. History cleared.")

                else:
                    # /system <name>  — switch to an existing preset
                    name = parts[1]
                    if name not in SYSTEM_PRESETS:
                        print(f"  Unknown preset {name!r}. Use /system list to see all presets.")
                    else:
                        current_preset = name
                        history = fresh_history()
                        print(f"  Switched to preset {name!r}. History cleared.")

            else:
                print(f"  Unknown command: {cmd!r}. Type /help for available commands.")

            continue  # back to the top of the loop — no model call

        # --------------------------------------------------------------
        # 6.6.2  Normal user message — string used to call the model
        #
        # Step 1: Append the user's message to the history.
        #         The model will see the full conversation up to this point.
        # --------------------------------------------------------------
        history.append({"role": "user", "content": user_input})  # <-- this goes to the LLM later as user's text

        # --------------------------------------------------------------
        # Step 2: Run the model on the GPU.
        #
        # IMPORTANT — the entire conversation history is sent to the GPU
        # from scratch on every single turn!  The Transformers pipeline is
        # stateless between Python calls: it holds no memory of previous
        # turns inside the GPU.  "Memory" exists only in our `history` list
        # in Python, which we rebuild and retransmit each time.
        #
        # Inside one call, inference proceeds in two distinct phases:
        #
        #   PREFILL phase  (processes the input — fast):
        #     All input tokens (the entire history) are fed into the
        #     transformer in ONE parallel matrix operation on the GPU.
        #     The GPU then computes and caches the Key-Value (KV) vectors for
        #     every input token.  KV cache is the transformer's internal
        #     representation of "what has been read so far" — it avoids
        #     recomputing attention over the input during generation.
        #     Because all input tokens are processed in parallel, prefill
        #     is relatively fast even for long histories.
        #     (It is alo the reason why input tokens are cheaper for commercial models).
        #
        #   DECODE phase  (generates the reply — slower):
        #     New tokens are generated ONE AT A TIME.  Each new token
        #     attends to the KV cache of all previous tokens (input +
        #     already generated tokens), then the new token's KV vectors
        #     are appended to the cache.  This is inherently sequential —
        #     each token depends on the previous one — so it cannot be
        #     parallelised.  This is the phase you perceive as the model
        #     "typing out" its answer.
        #
        #   ↳ Practical consequence: as the conversation grows longer,
        #     the prefill phase takes more time (more input tokens to
        #     process), so the delay before the first word of the reply
        #     increases with history length.
        #
        # NOTE — the KV cache described above lives only for the duration
        # of this one call.  When chat_pipeline() returns, the cache is
        # discarded.  The next turn starts prefill from scratch again.
        #
        # NOTE 2:
        # Production serving frameworks such as vLLM implement "prefix
        # caching": they persist the KV cache across calls and reuse the
        # cached vectors for the parts of the history that have not
        # changed (system prompt, previous turns).  This makes long
        # multi-turn conversations significantly faster — but it requires
        # a dedicated server process and is beyond the scope of this
        # introductory script.
        #
        # The returned structure is a list with one element per input:
        #   [{"generated_text": <reply>}]
        #
        # return_full_text=False means generated_text contains ONLY the
        # model's new reply — not the entire input echoed back first.
        # --------------------------------------------------------------
        do_sample = temperature > 0.0  # False → greedy (deterministic), True → random sampling

        # In Transformers 5.x the pipeline stores the model's generation_config
        # internally.  Passing any generation parameters alongside it (whether as
        # loose kwargs or as a separate GenerationConfig object) triggers a
        # deprecation warning because two configs would have to be merged.
        #
        # The clean solution: mutate the model's generation_config IN PLACE
        # before every call, then pass NO generation kwargs to the pipeline.
        # This way there is exactly one config and no conflict.
        cfg = chat_pipeline.model.generation_config
        cfg.max_new_tokens = max_tokens          # hard cap on reply length in tokens
        # Attempt to solve the warning - does not work
        # cfg.max_length     = None                # clear the default max_length=20 the model ships with
        # 2nd Warning solution - if max_length exists in attributes, we delete it
        # if hasattr(cfg, "max_length"):
        #     delattr(cfg, "max_length")

        cfg.max_length     = 1000000    #artificially large number
        cfg.do_sample      = do_sample           # False = greedy/deterministic, True = random sampling
        cfg.temperature    = temperature if do_sample else 1.0  # only meaningful when do_sample=True

        outputs = chat_pipeline(
            history,               # full conversation as a list of role/content dicts
            return_full_text=False, # return only the new reply, not the echoed input
        )

        # --------------------------------------------------------------
        # Step 3: Extract the reply text from the pipeline output.
        #
        # outputs[0]["generated_text"] can be either:
        #   - a dict  {"role": "assistant", "content": "..."}
        #        when the pipeline used the chat template path, or
        #   - a plain string
        #        as a fallback for older models / pipeline versions.
        # --------------------------------------------------------------
        reply_obj = outputs[0]["generated_text"]

        if isinstance(reply_obj, dict):
            reply_text: str = reply_obj["content"]
        else:
            reply_text: str = str(reply_obj)

        # --------------------------------------------------------------
        # Step 4: Append the model's reply to the history.
        #         The next user turn will include this as context,
        #         giving the model its "memory" of the conversation.
        # --------------------------------------------------------------
        history.append({"role": "assistant", "content": reply_text}) #  <-- this gets into chat's history

        # --------------------------------------------------------------
        # Step 5: Print the reply to the terminal.
        # --------------------------------------------------------------
        print(f"\nAssistant: {reply_text}\n")

        # --------------------------------------------------------------
        # Step 6: Show context window usage.
        #
        # Apply the chat template to the current history (which now
        # includes the assistant reply) and count the resulting tokens.
        # This is the exact number of tokens that will be sent to the
        # GPU as input on the *next* turn.
        #
        # If this approaches the model's context window limit, the
        # pipeline will silently truncate the oldest tokens — the model
        # will effectively "forget" the beginning of the conversation
        # without any error or warning.  Use /clear to reset.
        # --------------------------------------------------------------
        # Count tokens in the current history accurately:
        # Step 1 — apply_chat_template with tokenize=False returns a plain string
        #          (the formatted conversation exactly as the model will receive it).
        # Step 2 — tokenizer.encode() converts that string to a list of ints.
        # Step 3 — len() on that plain list gives the true token count.
        # This two-step approach is more reliable than tokenize=True, which may
        # return a BatchEncoding dict in some transformers versions, causing
        # len() to return the number of dict keys (2) instead of token count.
        formatted_history = chat_pipeline.tokenizer.apply_chat_template(
            history, tokenize=False, add_generation_prompt=True
        )
        token_ids   = chat_pipeline.tokenizer.encode(formatted_history)
        used_tokens = len(token_ids)
        pct = used_tokens / max_context_tokens * 100
        context_info = (
            f"[context: {used_tokens:,} / {max_context_tokens:,} tokens  ({pct:.1f}%)]"
        )
        if pct >= 85:
            print(f"  ⚠  WARNING: {context_info}")
            print("     Context window almost full — use /clear to start a fresh conversation.")
        else:
            print(f"  {context_info}")


# 7. ENTRY POINT
if __name__ == "__main__":
    # [] if "__file__" not in globals() else None:
    #   - Normal shell run:   parse_args(None) reads from sys.argv[1:]
    #   - Jupyter notebook:   parse_args([])   uses all argument defaults
    main_args = parser.parse_args([] if "__file__" not in globals() else None)
    main(main_args)
