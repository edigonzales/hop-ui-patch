#!/usr/bin/env python3
"""Idempotent Phase 1 patch manager for Apache Hop 2.19.0."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

from patch_state import (
    THEME,
    detect_phases,
    fail,
    verify_or_adopt,
    write_state,
)

PHASE_ORDER = ("1A", "1B", "1C")
PHASE_SCRIPTS = {
    "1A": "apply_phase1a.py",
    "1B": "apply_phase1b.py",
    "1C": "apply_phase1c.py",
}


def run_script(repo: Path, script: str, hop: Path) -> None:
    subprocess.run([sys.executable, str(repo / "scripts" / script), str(hop)], check=True)


def sync_theme(repo: Path, hop: Path) -> None:
    source = repo / "overlay" / THEME
    target = hop / THEME
    if not source.exists():
        fail(f"theme overlay missing: {source}")
    if target.exists() and target.read_bytes() == source.read_bytes():
        return
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)
    print("Updated managed HopUiTheme.java to the current patch definition.")


def print_status(hop: Path, phases: dict[str, str]) -> None:
    print("Apache Hop: 2.19.0")
    print("UI patch:")
    labels = {
        "1A": "Foundations",
        "1B": "Perspective rail",
        "1C": "Toolbar",
    }
    symbols = {"applied": "✓", "missing": "·", "partial": "!"}
    for phase in PHASE_ORDER:
        status = phases[phase]
        print(f"  {phase} {labels[phase]:18} {symbols[status]} {status}")


def apply_to(hop: Path, through: str = "1C") -> None:
    repo = Path(__file__).resolve().parents[1]
    phases = verify_or_adopt(hop)
    partial = [phase for phase, status in phases.items() if status == "partial"]
    if partial:
        fail("cannot continue from partial patch state: " + ", ".join(partial))

    target_index = PHASE_ORDER.index(through)
    for phase in PHASE_ORDER[: target_index + 1]:
        phases = detect_phases(hop)
        if phases[phase] == "applied":
            print(f"{phase}: already applied, skipping.")
            continue
        if phases[phase] == "partial":
            fail(f"{phase}: partially applied; refusing to guess")

        if phase != "1A":
            previous = PHASE_ORDER[PHASE_ORDER.index(phase) - 1]
            if phases[previous] != "applied":
                fail(f"{phase} requires {previous} to be applied first")
            # Older checkouts may contain an earlier HopUiTheme.java that predates later phase
            # tokens. Updating the managed theme file is safe after state/hash verification.
            sync_theme(repo, hop)
            write_state(hop)

        print(f"Applying {phase}...")
        run_script(repo, PHASE_SCRIPTS[phase], hop)
        phases = detect_phases(hop)
        if phases[phase] != "applied":
            fail(f"{phase} applicator completed but the resulting state is {phases[phase]}")
        write_state(hop)

    final_phases = verify_or_adopt(hop)
    print_status(hop, final_phases)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    apply_parser = subparsers.add_parser("apply", help="apply missing Phase 1 patches")
    apply_parser.add_argument("hop", type=Path)
    apply_parser.add_argument("--through", choices=PHASE_ORDER, default="1C")

    status_parser = subparsers.add_parser("status", help="show patch status")
    status_parser.add_argument("hop", type=Path)

    args = parser.parse_args()
    hop = args.hop.expanduser().resolve()

    if args.command == "apply":
        apply_to(hop, through=args.through)
    else:
        phases = verify_or_adopt(hop)
        print_status(hop, phases)


if __name__ == "__main__":
    main()
