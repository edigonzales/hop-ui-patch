#!/usr/bin/env bash
set -euo pipefail

UPSTREAM="46436154ae1a1e940861d485559819360c2af86e"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
OVERLAY_DIR="${REPO_DIR}/overlay"

if [[ $# -ne 1 ]]; then
  echo "usage: $0 /path/to/apache-hop" >&2
  exit 2
fi

HOP_DIR="$(cd "$1" 2>/dev/null && pwd)" || {
  echo "hop-ui-patch: Apache Hop checkout not found: $1" >&2
  exit 1
}

if ! git -C "${HOP_DIR}" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "hop-ui-patch: ${HOP_DIR} is not a Git checkout" >&2
  exit 1
fi

HEAD_SHA="$(git -C "${HOP_DIR}" rev-parse HEAD)"
if [[ "${HEAD_SHA}" != "${UPSTREAM}" ]]; then
  echo "hop-ui-patch: expected Apache Hop ${UPSTREAM}, got ${HEAD_SHA}" >&2
  exit 1
fi

# Old versions of hop-ui-patch stored bookkeeping in the target repository's Git metadata.
# The overlay installer is stateless; remove the obsolete file if it is still present.
GIT_DIR="$(git -C "${HOP_DIR}" rev-parse --git-dir)"
if [[ "${GIT_DIR}" != /* ]]; then
  GIT_DIR="${HOP_DIR}/${GIT_DIR}"
fi
if [[ -f "${GIT_DIR}/hop-ui-patch-state.json" ]]; then
  rm -f "${GIT_DIR}/hop-ui-patch-state.json"
  echo "Removed obsolete hop-ui-patch state metadata."
fi

mismatches=()
total=0
while IFS= read -r -d '' source; do
  relative="${source#${OVERLAY_DIR}/}"
  target="${HOP_DIR}/${relative}"
  total=$((total + 1))
  if [[ ! -f "${target}" ]] || ! cmp -s "${source}" "${target}"; then
    mismatches+=("${relative}")
  fi
done < <(find "${OVERLAY_DIR}" -type f -print0)

if [[ ${#mismatches[@]} -eq 0 ]]; then
  echo "Apache Hop 2.19.0: ${HEAD_SHA}"
  echo "UI overlay already up to date (${total}/${total} files match)."
  exit 0
fi

echo "Apache Hop 2.19.0: ${HEAD_SHA}"
echo "Installing UI overlay: ${#mismatches[@]} of ${total} files differ."

# Preserve the complete current working tree before replacing files. This intentionally includes
# untracked files (for example HopUiTheme.java from an older patch version). The stash is a backup;
# it is never popped automatically because doing so could reintroduce an older UI patch over the
# newly installed snapshot.
if [[ -n "$(git -C "${HOP_DIR}" status --porcelain --untracked-files=all)" ]]; then
  STASH_MESSAGE="hop-ui-patch backup $(date '+%Y-%m-%d %H:%M:%S')"
  git -C "${HOP_DIR}" stash push -u -m "${STASH_MESSAGE}" >/dev/null
  echo "Previous working tree saved as:"
  git -C "${HOP_DIR}" stash list -1 --format='  %gd: %s'
  echo "The stash was not reapplied automatically."
fi

cp -R "${OVERLAY_DIR}/." "${HOP_DIR}/"

git -C "${HOP_DIR}" diff --check

remaining=0
while IFS= read -r -d '' source; do
  relative="${source#${OVERLAY_DIR}/}"
  target="${HOP_DIR}/${relative}"
  if [[ ! -f "${target}" ]] || ! cmp -s "${source}" "${target}"; then
    echo "hop-ui-patch: overlay verification failed for ${relative}" >&2
    remaining=$((remaining + 1))
  fi
done < <(find "${OVERLAY_DIR}" -type f -print0)

if [[ ${remaining} -ne 0 ]]; then
  exit 1
fi

echo "Installed ${total} overlay files."
echo "Run: bash scripts/status.sh ${HOP_DIR}"
