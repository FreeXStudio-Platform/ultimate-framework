#!/usr/bin/env sh
set -eu
ROOT="${1:-$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)}"
python3 "$ROOT/04_enforcement/validators/absolute_validate.py" "$ROOT"
