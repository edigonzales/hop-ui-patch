#!/usr/bin/env python3
"""Compatibility entry point: apply managed Phase 1A + 1B."""

from __future__ import annotations

import sys
from pathlib import Path

from patch_manager import apply_to
from patch_state import fail


def main() -> None:
    if len(sys.argv) != 2:
        fail("usage: apply_phase1.py /path/to/apache-hop")
    apply_to(Path(sys.argv[1]).expanduser().resolve(), through="1B")


if __name__ == "__main__":
    main()
