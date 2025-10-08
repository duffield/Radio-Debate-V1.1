#!/usr/bin/env bash
set -euo pipefail

# Run a one-round debate about the existence of shapeshifters
# Usage:
#   ./debate_shapeshifters.sh            # uses default rounds=1
#   ROUNDS=3 ./debate_shapeshifters.sh   # override rounds via env var
#   ./debate_shapeshifters.sh --rounds 2 # pass extra args through

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

PY="$DIR/.venv/bin/python"
if [ ! -x "$PY" ]; then
  echo "❌ Virtualenv Python not found at $PY"
  echo "   Ensure your venv exists at .venv (or adjust this script)."
  exit 1
fi

TOPIC="The existence of shapeshifters"
ROUNDS="${ROUNDS:-1}"

exec "$PY" main.py --topic "$TOPIC" --rounds "$ROUNDS" "$@"
