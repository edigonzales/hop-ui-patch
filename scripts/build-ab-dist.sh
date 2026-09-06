#!/usr/bin/env bash
#
# Builds both Hop client distributions side by side for A/B comparison:
#
#   <dist-base>/hop-main            current apache/hop main
#   <dist-base>/hop-2.19.0-patched  pinned 2.19.0 + hop-ui-patch overlay
#
# Usage: build-ab-dist.sh <hop-main-checkout> <hop-2.19.0-checkout> [dist-base]
#
set -euo pipefail

MAIN_CHECKOUT="${1:?usage: build-ab-dist.sh <hop-main-checkout> <hop-2.19.0-checkout> [dist-base]}"
PATCHED_CHECKOUT="${2:?usage: build-ab-dist.sh <hop-main-checkout> <hop-2.19.0-checkout> [dist-base]}"
DIST_BASE="${3:-dist}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

bash "$SCRIPT_DIR/build-client.sh" "$MAIN_CHECKOUT" "$DIST_BASE/hop-main"
bash "$SCRIPT_DIR/build-client.sh" "$PATCHED_CHECKOUT" "$DIST_BASE/hop-2.19.0-patched"

echo
echo "==> A/B clients ready:"
echo "    $DIST_BASE/hop-main            — current main"
echo "    $DIST_BASE/hop-2.19.0-patched  — 2.19.0 + hop-ui-patch overlay"
echo
echo "    Start side by side and compare screenshots."
