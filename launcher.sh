#!/usr/bin/env bash
set -euo pipefail

# Resolve script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PY_SCRIPT="$SCRIPT_DIR/show_eposters.py"

# --- Hardcoded settings (edit here) ---
POSTER_TOKEN="A9993E364706816ABA3E25717850C26C9CD0D89D"
CACHE_REFRESH=60
DISPLAY_TIME=5
# ---------------------------------------

# Export (viewer reads these from env)
export POSTER_TOKEN
export CACHE_REFRESH
export DISPLAY_TIME

echo "[launcher] Starting ePoster viewer..."
echo "  POSTER_TOKEN: [HIDDEN]"
echo "  CACHE_REFRESH: $CACHE_REFRESH"
echo "  DISPLAY_TIME: $DISPLAY_TIME"

# Run the Python viewer (assumes dependencies already installed by setup_loader.py)
exec python3 "$PY_SCRIPT"
