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

matched=0
total=0
differences=()
while IFS= read -r -d '' source; do
  relative="${source#${OVERLAY_DIR}/}"
  target="${HOP_DIR}/${relative}"
  total=$((total + 1))
  if [[ -f "${target}" ]] && cmp -s "${source}" "${target}"; then
    matched=$((matched + 1))
  else
    differences+=("${relative}")
  fi
done < <(find "${OVERLAY_DIR}" -type f -print0)

echo "Apache Hop: 2.19.0"
echo "Baseline:   ${HEAD_SHA}"
echo "Overlay:    ${matched} / ${total} files match"

if [[ ${#differences[@]} -eq 0 ]]; then
  echo "Status:     up to date"
else
  echo "Status:     ${#differences[@]} overlay file(s) differ"
  echo
  echo "Differing files:"
  for relative in "${differences[@]}"; do
    echo "  ! ${relative}"
  done
fi
