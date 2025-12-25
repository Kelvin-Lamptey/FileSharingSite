#!/usr/bin/env bash
# Simple starter script
set -euo pipefail
PORT=${PORT:-8000}
DIR=${DIR:-files}
exec uv run python3 server.py --port "$PORT" --dir "$DIR"
