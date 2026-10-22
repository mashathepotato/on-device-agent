#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
export SPOILER_TUNED_MODEL="${SPOILER_TUNED_MODEL:-lfm-click-tuned:checkpoint128}"
export SPOILER_DEFAULT_MODE=tuned
exec python3 -m spoiler.server
