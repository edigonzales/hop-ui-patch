#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

python3 "${SCRIPT_DIR}/apply_phase1.py" "$@"
python3 "${SCRIPT_DIR}/apply_phase1c.py" "$@"
