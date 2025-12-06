#!/usr/bin/env bash
set -euo pipefail

BASE="/home/eposter"
PY_SCRIPT="$BASE/show_eposters.py"

# --- Settings ---
export POSTER_TOKEN="A9993E364706816ABA3E25717850C26C9CD0D89D"
export CACHE_REFRESH=60
export DISPLAY_TIME=5

echo "[launcher] Starting ePoster viewer…"
echo "  POSTER_TOKEN: [HIDDEN]"
echo "  CACHE_REFRESH=$CACHE_REFRESH"
echo "  DISPLAY_TIME=$DISPLAY_TIME"

exec python3 "$PY_SCRIPT"
