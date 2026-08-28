#!/usr/bin/env python3
"""State detection and verification for the Apache Hop Phase 1 UI patch."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

UPSTREAM = "46436154ae1a1e940861d485559819360c2af86e"
STATE_VERSION = 1
STATE_FILENAME = "hop-ui-patch-state.json"

THEME = "ui/src/main/java/org/apache/hop/ui/core/gui/HopUiTheme.java"
GUI_RESOURCE = "ui/src/main/java/org/apache/hop/ui/core/gui/GuiResource.java"
PROPS_UI = "ui/src/main/java/org/apache/hop/ui/core/PropsUi.java"
CANVAS_PALETTE = "engine/src/main/java/org/apache/hop/core/gui/CanvasColorPalette.java"
HOP_GUI = "ui/src/main/java/org/apache/hop/ui/hopgui/HopGui.java"
GUI_TOOLBAR = "ui/src/main/java/org/apache/hop/ui/core/gui/GuiToolbarWidgets.java"

KNOWN_PATHS = (THEME, GUI_RESOURCE, PROPS_UI, CANVAS_PALETTE, HOP_GUI, GUI_TOOLBAR)
PHASE_PATHS = {
    "1A": {THEME, GUI_RESOURCE, PROPS_UI, CANVAS_PALETTE},
    "1B": {THEME, HOP_GUI},
    "1C": {THEME, HOP_GUI, GUI_TOOLBAR},
}

PHASE_MARKERS = {
    "1A": {
        THEME: ("public final class HopUiTheme", "applicationBackground(boolean darkMode)"),
        GUI_RESOURCE: ("HopUiTheme.applicationBackground(props.isDarkMode())",),
        PROPS_UI: ("HopUiTheme.SPACING_MEDIUM * getNativeZoomFactor()", "HopUiTheme.TAB_HEIGHT"),
        CANVAS_PALETTE: ("rgb(250, 250, 250),", "rgb(229, 231, 235),"),
    },
    "1B": {
        HOP_GUI: (
            "private void paintSidebarButtonBackground(",
            "HopUiTheme.SIDEBAR_BUTTON_SIZE",
            "HopUiTheme.sidebarSelection(props.isDarkMode())",
        ),
    },
    "1C": {
        HOP_GUI: ("SWT.FLAT | SWT.WRAP | SWT.RIGHT | SWT.HORIZONTAL",),
        GUI_TOOLBAR: (
            "private void addToolbarGroupGap(ToolBar toolBar)",
            "HopUiTheme.TOOLBAR_ICON_SIZE",
        ),
    },
}


def fail(message: str) -> None:
    raise SystemExit(f"hop-ui-patch: {message}")


def git(hop: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(hop), *args], text=True).strip()


def ensure_checkout(hop: Path) -> None:
    if not (hop / ".git").exists():
        fail(f"{hop} is not a Git checkout")
    head = git(hop, "rev-parse", "HEAD")
    if head != UPSTREAM:
        fail(f"expected Apache Hop {UPSTREAM}, got {head}")


def state_path(hop: Path) -> Path:
    git_dir = Path(git(hop, "rev-parse", "--git-dir"))
    if not git_dir.is_absolute():
        git_dir = hop / git_dir
    return git_dir.resolve() / STATE_FILENAME


def read_text(hop: Path, relative: str) -> str:
    path = hop / relative
    return path.read_text() if path.exists() else ""


def phase_status(hop: Path, phase: str) -> str:
    checks: list[bool] = []
    for relative, markers in PHASE_MARKERS[phase].items():
        text = read_text(hop, relative)
        checks.extend(marker in text for marker in markers)
    if all(checks):
        return "applied"
    if not any(checks):
        return "missing"
    return "partial"


def detect_phases(hop: Path) -> dict[str, str]:
    phases = {phase: phase_status(hop, phase) for phase in ("1A", "1B", "1C")}
    if any(value == "partial" for value in phases.values()):
        return phases
    if phases["1B"] == "applied" and phases["1A"] != "applied":
        phases["1B"] = "partial"
    if phases["1C"] == "applied" and phases["1B"] != "applied":
        phases["1C"] = "partial"
    return phases


def dirty_paths(hop: Path) -> set[str]:
    output = git(hop, "status", "--porcelain", "--untracked-files=all")
    if not output:
        return set()
    paths: set[str] = set()
    for line in output.splitlines():
        path = line[3:]
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        paths.add(path)
    return paths


def allowed_paths(phases: dict[str, str]) -> set[str]:
    allowed: set[str] = set()
    for phase, status in phases.items():
        if status == "applied":
            allowed.update(PHASE_PATHS[phase])
    return allowed


def sha256(path: Path) -> str | None:
    if not path.exists():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def snapshot_hashes(hop: Path) -> dict[str, str | None]:
    return {relative: sha256(hop / relative) for relative in KNOWN_PATHS}


def write_state(hop: Path) -> None:
    phases = detect_phases(hop)
    if any(status == "partial" for status in phases.values()):
        fail(f"cannot record partial patch state: {phases}")
    payload = {
        "version": STATE_VERSION,
        "upstream": UPSTREAM,
        "phases": phases,
        "files": snapshot_hashes(hop),
    }
    state_path(hop).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def load_state(hop: Path) -> dict | None:
    path = state_path(hop)
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        fail(f"invalid patch state file {path}: {exc}")


def verify_recorded_state(hop: Path, state: dict) -> dict[str, str]:
    if state.get("version") != STATE_VERSION or state.get("upstream") != UPSTREAM:
        fail("patch state file belongs to another patch-manager version or Hop baseline")

    phases = detect_phases(hop)
    if phases != state.get("phases"):
        fail(f"patch markers changed since the last managed run: recorded={state.get('phases')}, actual={phases}")

    expected_hashes = state.get("files", {})
    actual_hashes = snapshot_hashes(hop)
    for relative in KNOWN_PATHS:
        if expected_hashes.get(relative) != actual_hashes.get(relative):
            fail(f"unknown local change in managed file: {relative}")

    unknown = dirty_paths(hop) - allowed_paths(phases)
    if unknown:
        fail("unknown local changes outside the managed patch: " + ", ".join(sorted(unknown)))
    return phases


def adopt_legacy_state(hop: Path) -> dict[str, str]:
    phases = detect_phases(hop)
    partial = [phase for phase, status in phases.items() if status == "partial"]
    if partial:
        fail("incomplete/partially applied UI patch detected: " + ", ".join(partial))

    unknown = dirty_paths(hop) - allowed_paths(phases)
    if unknown:
        fail("unknown local changes prevent safe patch-state adoption: " + ", ".join(sorted(unknown)))

    write_state(hop)
    return phases


def verify_or_adopt(hop: Path) -> dict[str, str]:
    ensure_checkout(hop)
    state = load_state(hop)
    if state is None:
        return adopt_legacy_state(hop)
    return verify_recorded_state(hop, state)
