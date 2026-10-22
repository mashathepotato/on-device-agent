#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
export SPOILER_TUNED_MODEL=
export SPOILER_DEFAULT_MODE=original
exec python3 -m spoiler.server
