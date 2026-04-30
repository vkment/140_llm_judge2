#!/bin/bash

# Usage:
#   ./run_clean.sh run_judge81_2.py; [ $? -eq 0 ] && exit
#   ./run_clean.sh run_judge81_2.py --model gemma --batch 32; [ $? -eq 0 ] && exit
#
# Meaning of this wrapper's exit code:
#   0     = cleanup was done; caller may exit node
#   != 0  = cleanup was NOT done; stay on node

# Behavior summary:
#   - Normal Python exit (status 0):
#         → cleanup is performed, wrapper returns 0
#
#   - Python runtime error (exception, CUDA error, OOM, etc.):
#         → cleanup is performed, wrapper returns 0
#
#   - Interrupted by user (Ctrl+C) or SIGTERM:
#         → NO cleanup, wrapper returns nonzero (e.g. 130)
#
#   - Script not found / cannot start Python:
#         → NO cleanup, wrapper returns nonzero
#
#   - Status 137 (SIGKILL / possible OOM kill):
#         → treated as crash → cleanup IS performed (best-effort assumption)
#
# Rationale:
#   Cleanup is done only if Python actually started and finished on its own
#   (successfully or with an internal error). Any external interruption is
#   treated as "manual intervention", so scratch is preserved for inspection.

set -u

WORKDIR="/storage/vestec1-elixir/home/vok/py26/llm_judge"

interrupted=0
python_pid=""

on_interrupt() {
    interrupted=1
    echo
    echo "=== Interrupted; scratch will NOT be cleaned. ==="

    if [ -n "${python_pid:-}" ]; then
        kill -TERM "$python_pid" 2>/dev/null || true
        wait "$python_pid" 2>/dev/null || true
    fi

    exit 130
}

trap on_interrupt INT TERM

cd "$WORKDIR" || {
    echo "Error: Cannot cd to $WORKDIR"
    exit 2
}

if [ $# -lt 1 ]; then
    echo "Usage: $0 script.py [args...]"
    exit 2
fi

SCRIPT="$1"
shift

if [ ! -f "$SCRIPT" ]; then
    echo "Error: $SCRIPT not found in $WORKDIR"
    echo "Nothing was run, scratch will NOT be cleaned."
    exit 2
fi

cleanup() {
    echo
    echo "=== Cleaning scratch ==="

    if [ -n "${SCRATCHDIR:-}" ] && [ -d "$SCRATCHDIR" ]; then
        cd "$SCRATCHDIR" && clean_scratch
    else
        echo "Warning: SCRATCHDIR is not set or does not exist; trying clean_scratch anyway."
        clean_scratch || echo "Warning: clean_scratch failed"
    fi
}

echo "=== Starting $SCRIPT at $(date) ==="

python "$SCRIPT" "$@" &
python_pid=$!

wait "$python_pid"
status=$?
python_pid=""

echo "=== Python finished with status $status at $(date) ==="

case "$status" in
    130|143)
        echo "=== Python was interrupted; scratch will NOT be cleaned. ==="
        exit "$status"
        ;;
esac

# Optional: treat SIGKILL/OOM as cleanup-worthy.
# Status 137 can mean OOM kill, but also manual kill -9.
if [ "$status" -eq 137 ]; then
    echo "=== Python ended with status 137: possible OOM/SIGKILL. ==="
    echo "=== Assuming crash/OOM; scratch WILL be cleaned. ==="
fi

cleanup

echo "=== Done at $(date) ==="

# Return 0 to tell the caller: it is safe to exit the node.
exit 0