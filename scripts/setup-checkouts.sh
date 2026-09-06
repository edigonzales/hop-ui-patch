#!/usr/bin/env bash
#
# Sets up two Apache Hop source checkouts for A/B testing of the hop-ui-patch overlay:
#
#   <base>/hop-main    current apache/hop main
#   <base>/hop-2.19.0  pinned 2.19.0 commit + the overlay applied
#
# Usage: setup-checkouts.sh <base-dir>
#
# Environment:
#   HOP_REPO_URL        default https://github.com/apache/hop.git
#   HOP_PINNED_COMMIT   default 46436154ae1a1e940861d485559819360c2af86e (2.19.0)
#
set -euo pipefail

HOP_REPO_URL="${HOP_REPO_URL:-https://github.com/apache/hop.git}"
HOP_PINNED_COMMIT="${HOP_PINNED_COMMIT:-46436154ae1a1e940861d485559819360c2af86e}"

BASE="${1:?usage: setup-checkouts.sh <base-dir>}"
PATCH_REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

MAIN_DIR="$BASE/hop-main"
PATCHED_DIR="$BASE/hop-2.19.0"

command -v git >/dev/null || { echo "git is required" >&2; exit 1; }
mkdir -p "$BASE"

if [ ! -d "$MAIN_DIR/.git" ]; then
  echo "==> Cloning apache/hop (full clone, ~1 GB) into $MAIN_DIR ..."
  git clone "$HOP_REPO_URL" "$MAIN_DIR"
else
  echo "==> Updating existing checkout $MAIN_DIR ..."
  git -C "$MAIN_DIR" fetch origin
fi

if [ ! -d "$PATCHED_DIR/.git" ]; then
  echo "==> Adding worktree $PATCHED_DIR at $HOP_PINNED_COMMIT ..."
  git -C "$MAIN_DIR" worktree add "$PATCHED_DIR" "$HOP_PINNED_COMMIT"
else
  echo "==> Worktree $PATCHED_DIR already exists, resetting to pinned commit ..."
  git -C "$PATCHED_DIR" reset --hard "$HOP_PINNED_COMMIT"
  git -C "$PATCHED_DIR" clean -fd
fi

echo "==> Applying hop-ui-patch overlay ..."
bash "$PATCH_REPO/scripts/apply-ui-patch.sh" "$PATCHED_DIR"

echo
echo "==> Done. Checkouts:"
echo "    main:    $MAIN_DIR ($(git -C "$MAIN_DIR" rev-parse --short HEAD))"
echo "    patched: $PATCHED_DIR ($(git -C "$PATCHED_DIR" rev-parse --short HEAD) + overlay)"
echo
echo "    Build both clients with:"
echo "    bash $PATCH_REPO/scripts/build-ab-dist.sh \"$MAIN_DIR\" \"$PATCHED_DIR\""
