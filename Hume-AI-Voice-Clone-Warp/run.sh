#!/usr/bin/env bash
set -euo pipefail

# One-shot launcher for the Hume AI Voice Clone app.
# - Creates .venv and installs deps if needed
# - Loads .env (without printing secrets)
# - Runs the app; defaults to realtime test if no args provided

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

VENV_DIR="$SCRIPT_DIR/.venv"
PY="$VENV_DIR/bin/python"
PIP="$VENV_DIR/bin/pip"

if [[ ! -x "$PY" ]]; then
  echo "Creating virtual environment and installing dependencies..."
  /usr/bin/python3 -m venv "$VENV_DIR"
  "$PY" -m pip install --upgrade pip
  "$PIP" install -r "$SCRIPT_DIR/requirements.txt"
else
  # Ensure newly added dependencies are installed without forcing a full reinstall
  if ! "$PY" - <<'PY'
import importlib, sys
missing = 0
for m in ("hume",):
    try:
        importlib.import_module(m)
    except Exception:
        missing += 1
sys.exit(missing)
PY
  then
    "$PIP" install -r "$SCRIPT_DIR/requirements.txt"
  fi
fi

# Load .env (if present). Do not echo any secrets.
if [[ -f "$SCRIPT_DIR/.env" ]]; then
  set -a
  # shellcheck disable=SC1091
  source "$SCRIPT_DIR/.env"
  set +a
else
  echo "WARN: .env not found in project root. You can create one with your Hume credentials." >&2
fi

# Provide a default headphone output if not set
if [[ -z "${AUDIO_OUTPUT_DEVICE:-}" ]]; then
  AUDIO_OUTPUT_DEVICE="Headphones"
fi

# Sanity checks for required vars
missing=0
for var in HUME_API_KEY HUME_SECRET_KEY; do
  if [[ -z "${!var:-}" ]]; then
    echo "WARN: $var not set (set it in .env)" >&2
    missing=1
  fi
done
if [[ -z "${HUME_WS_URL:-}" ]]; then
  echo "INFO: HUME_WS_URL not set. That's OK if using the Hume SDK with HUME_CONFIG_ID." >&2
fi
if (( missing )); then
  echo "ERROR: Missing required environment variables. Aborting." >&2
  exit 1
fi

# Default to quick realtime test if no args provided
if [[ $# -eq 0 ]]; then
  set -- --record-seconds 10 --output data/voice_sample.wav --realtime
fi

# If AUDIO_OUTPUT_DEVICE is set, pass it through
if [[ -n "${AUDIO_OUTPUT_DEVICE:-}" ]]; then
  set -- "$@" --output-device "$AUDIO_OUTPUT_DEVICE"
fi
# If HUME_CONFIG_ID is set, pass it through
if [[ -n "${HUME_CONFIG_ID:-}" ]]; then
  set -- "$@" --config-id "$HUME_CONFIG_ID"
fi

exec "$PY" "$SCRIPT_DIR/src/app.py" "$@"
