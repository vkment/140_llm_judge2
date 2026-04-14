"""
local_chat_fancy.py
-------------------
Interactive terminal chat with a locally running LLM via Hugging Face Transformers.
Identical to chat_local.py, with one difference: the model's reply is streamed to
the terminal token by token as it is generated — just like commercial chatbots do.

The model is loaded once onto the GPU at startup; from then on the user can chat
without restarting the process.  System prompt, temperature, and max response
length can all be changed on the fly via /commands.
"""

# 1. IMPORTS
import argparse
import logging
import os
import sys
import threading       # needed to run the pipeline in a background thread during streaming
# import warnings        # residuum, unused already

from dotenv import load_dotenv
import torch
from transformers import pipeline, TextIteratorStreamer


# 2. CLI ARGUMENT PARSER
parser = argparse.ArgumentParser(
    description="Interactive terminal chat with a local LLM on GPU (Transformers) — streaming version.",
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

    # Ensure the terminal speaks UTF-8 so Czech (and other non-ASCII)
    # characters are read and printed correctly regardless of the system locale.
    # sys.stdin.reconfigure(encoding='utf-8')  # Did not help with Czech Unicode characters
    sys.stdout.reconfigure(encoding='utf-8')

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
    # pipeline() is the heavy one-time initialisation step.  Calling it:
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
    # transformers emits this via its own logging system (logger.warning_once),
    # NOT via Python's warnings.warn — so warnings.filterwarnings() has no effect.
    # The working fix is a logging.Filter on the transformers logger, OR simply
    # raising the log level of the relevant module (chosen approach below).
    #
    # Alternatives that do NOT work / were tried:
    #   warnings.filterwarnings("ignore", message=".*both `max_new_tokens`.*")
    #   logging.getLogger("transformers").addFilter(...)
    logging.getLogger("transformers.generation.utils").setLevel(logging.ERROR)

    logger.info("Loading model %r onto GPU — this may take a while …", args.model)
    chat_pipeline = pipeline(
        task="text-generation",     # generate text that continues / replies to the input
        model=args.model,           # HuggingFace model name or local path
        device_map="auto",          # spread weights across all available GPUs automatically
        dtype=torch.bfloat16,       # bf16: halves VRAM usage, preserves float32 dynamic range
        token=hf_token,             # HF auth token — enables higher rate limits and private models
    )
    logger.info("Model loaded successfully.  Ready to chat.\n")

    logger.info("Model device: %s", chat_pipeline.model.device)  # shows GPU (correct) vs CPU (mistake)

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
    print("  Local LLM chat (streaming)  —  type /help for commands")
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
    # "memory" of the conversation.
    # NOTE: the system prompt is never shown to the user in the terminal,
    #       but the model sees it on every single turn.
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

        # This was not enough to code Czech unicode characters properly
        # try:
        #     user_input = input(prompt_str).strip()

        #New implementation of Czech unicode charactes
        try:
            sys.stdout.write(prompt_str)
            sys.stdout.flush()
            raw = sys.stdin.buffer.readline()
            if not raw:          # EOF (Ctrl-D)
                raise EOFError
            user_input = raw.decode('utf-8', errors='replace').rstrip('\n').strip()

        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break

        if not user_input:
            continue  # ignore empty lines

        # --------------------------------------------------------------
        # 6.6.1  Handle /commands — these never reach the model
        # --------------------------------------------------------------
        if user_input.startswith("/"):
            parts = user_input.split(maxsplit=3)
            cmd = parts[0].lower()

            if cmd in ("/quit", "/exit"):
                print("Bye!")
                break

            elif cmd == "/help":
                print_help()

            elif cmd == "/mode":
                turns = (len(history) - 1) // 2
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
        # 6.6.2  Normal user message — run the model WITH STREAMING
        #
        # KEY DIFFERENCE vs chat_local.py:
        #   In chat_local.py the pipeline call is synchronous — the main
        #   thread blocks until the full reply is ready, then prints it
        #   all at once.
        #
        #   Here we want to print each token as it comes off the GPU,
        #   exactly like commercial chatbots do.  This requires splitting
        #   the work across two threads:
        #
        #     main thread       — reads user input, then iterates over
        #                         the streamer queue and prints tokens.
        #     background thread — runs chat_pipeline(), which generates
        #                         tokens and pushes them into the queue.
        #
        #   The streamer (TextIteratorStreamer) is the shared queue that
        #   connects the two threads.  See Steps 2–4 below.
        #
        #   Note: only the DECODE phase produces tokens one-by-one and
        #   benefits from streaming.  The PREFILL phase (processing the
        #   full input history) still happens in one blocking GPU call
        #   before any token appears — see chat_local.py for details.
        #
        # Step 1: Append the user's message to the history.
        # --------------------------------------------------------------
        history.append({"role": "user", "content": user_input})  # <-- this goes to the LLM later as user's text



        # --------------------------------------------------------------
        # Step 2: Set up the streamer and generation config.
        #
        # TextIteratorStreamer is a queue-like object that receives tokens
        # from the model one by one as they are generated (decode phase)
        # and makes them available to the main thread via iteration.
        #
        # Parameters:
        #   skip_prompt=True         — do not re-emit the input tokens,
        #                              only the newly generated reply.
        #   skip_special_tokens=True — strip control tokens such as
        #                              <|im_end|> from the output text.
        # --------------------------------------------------------------
        streamer = TextIteratorStreamer(
            chat_pipeline.tokenizer,
            skip_prompt=True,
            skip_special_tokens=True,
        )

        # Update generation config in place (same approach as chat_local.py).
        do_sample = temperature > 0.0
        cfg = chat_pipeline.model.generation_config
        cfg.max_new_tokens = max_tokens
        cfg.max_length     = 1_000_000   # large sentinel so it never conflicts
        cfg.do_sample      = do_sample
        cfg.temperature    = temperature if do_sample else 1.0

        # --------------------------------------------------------------
        # Step 3: Start GPU inference in a background thread.
        #
        # WHY A THREAD?
        #   chat_pipeline(...) is a blocking call — it returns only when
        #   the full response is generated.  If we called it directly here,
        #   the main thread would be stuck waiting and could not print
        #   tokens as they arrive.
        #
        #   By running the pipeline in a background thread, the main thread
        #   is free to iterate over `streamer` and print each token the
        #   moment it comes off the GPU.  The two threads communicate via
        #   the streamer's internal queue:
        #
        #     background thread  →  [queue]  →  main thread
        #       (GPU generates)               (prints to terminal)
        #
        #   This is the standard pattern recommended by HuggingFace for
        #   streaming with the Transformers pipeline.
        # --------------------------------------------------------------
        generation_thread = threading.Thread(
            target=chat_pipeline,
            kwargs=dict(
                text_inputs=history,       # full conversation history
                streamer=streamer,         # tokens are pushed here instead of returned
                return_full_text=False,    # only the new reply, not the echoed input
            ),
        )
        generation_thread.start()

        # --------------------------------------------------------------
        # Step 4: Print tokens as they arrive (this IS the streaming).
        #
        # `for token in streamer` blocks briefly on each iteration,
        # waiting for the next token to be placed in the queue by the
        # background thread.  As soon as a token arrives it is printed
        # immediately with flush=True so the terminal shows it at once
        # without buffering.
        #
        # This loop exits automatically when the model emits its
        # end-of-sequence token and the streamer signals completion.
        # --------------------------------------------------------------
        print("\nAssistant: ", end="", flush=True)
        reply_text = ""
        for token in streamer:
            print(token, end="", flush=True)
            reply_text += token
        print("\n")                        # newline after the streamed reply

        generation_thread.join()           # wait for background thread 
        
        # here GPU is now idle until next turn

        # --------------------------------------------------------------
        # Step 5: Append the complete reply to the history.
        #         (Same as in chat_local.py — nothing changes here.)
        # --------------------------------------------------------------
        history.append({"role": "assistant", "content": reply_text})   # <-- this gets into chat's history

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
