#!/usr/bin/env python3
"""State detection and verification for the Apache Hop UI patch set."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

UPSTREAM = "46436154ae1a1e940861d485559819360c2af86e"
STATE_VERSION = 5
STATE_FILENAME = "hop-ui-patch-state.json"
PHASE_ORDER = ("1A", "1B", "1C", "2", "3", "4", "5A")

THEME = "ui/src/main/java/org/apache/hop/ui/core/gui/HopUiTheme.java"
GUI_RESOURCE = "ui/src/main/java/org/apache/hop/ui/core/gui/GuiResource.java"
PROPS_UI = "ui/src/main/java/org/apache/hop/ui/core/PropsUi.java"
CANVAS_PALETTE = "engine/src/main/java/org/apache/hop/core/gui/CanvasColorPalette.java"
HOP_GUI = "ui/src/main/java/org/apache/hop/ui/hopgui/HopGui.java"
GUI_TOOLBAR = "ui/src/main/java/org/apache/hop/ui/core/gui/GuiToolbarWidgets.java"
BASE_DIALOG = "ui/src/main/java/org/apache/hop/ui/core/dialog/BaseDialog.java"
LABEL_TEXT = "ui/src/main/java/org/apache/hop/ui/core/widget/LabelText.java"
LABEL_TEXT_VAR = "ui/src/main/java/org/apache/hop/ui/core/widget/LabelTextVar.java"
LABEL_COMBO = "ui/src/main/java/org/apache/hop/ui/core/widget/LabelCombo.java"
LABEL_COMBO_VAR = "ui/src/main/java/org/apache/hop/ui/core/widget/LabelComboVar.java"
COMBO_VAR = "ui/src/main/java/org/apache/hop/ui/core/widget/ComboVar.java"
TABLE_VIEW = "ui/src/main/java/org/apache/hop/ui/core/widget/TableView.java"
BASE_PAINTER = "engine/src/main/java/org/apache/hop/core/gui/BasePainter.java"
PIPELINE_PAINTER = "engine/src/main/java/org/apache/hop/pipeline/PipelinePainter.java"
WORKFLOW_PAINTER = "engine/src/main/java/org/apache/hop/workflow/WorkflowPainter.java"

KNOWN_PATHS = (
    THEME,
    GUI_RESOURCE,
    PROPS_UI,
    CANVAS_PALETTE,
    HOP_GUI,
    GUI_TOOLBAR,
    BASE_DIALOG,
    LABEL_TEXT,
    LABEL_TEXT_VAR,
    LABEL_COMBO,
    LABEL_COMBO_VAR,
    COMBO_VAR,
    TABLE_VIEW,
    BASE_PAINTER,
    PIPELINE_PAINTER,
    WORKFLOW_PAINTER,
)

PHASE_PATHS = {
    "1A": {THEME, GUI_RESOURCE, PROPS_UI, CANVAS_PALETTE},
    "1B": {THEME, HOP_GUI},
    "1C": {THEME, HOP_GUI, GUI_TOOLBAR},
    "2": {THEME, BASE_DIALOG, LABEL_TEXT, LABEL_TEXT_VAR, LABEL_COMBO, LABEL_COMBO_VAR},
    "3": {THEME, TABLE_VIEW},
    "4": {BASE_PAINTER, PIPELINE_PAINTER, WORKFLOW_PAINTER},
    "5A": {THEME, PROPS_UI, LABEL_COMBO, COMBO_VAR},
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
    "2": {
        BASE_DIALOG: (
            "MARGIN_SIZE = HopUiTheme.DIALOG_MARGIN",
            "LABEL_SPACING = HopUiTheme.FORM_LABEL_GAP",
            "ELEMENT_SPACING = HopUiTheme.DIALOG_ELEMENT_GAP",
        ),
        LABEL_TEXT: ("HopUiTheme.FORM_LABEL_GAP", "PropsUi.setLook(this);"),
        LABEL_TEXT_VAR: ("int margin = HopUiTheme.FORM_LABEL_GAP;",),
        LABEL_COMBO: ("int margin = HopUiTheme.FORM_LABEL_GAP;",),
        LABEL_COMBO_VAR: ("int margin = HopUiTheme.FORM_LABEL_GAP;",),
    },
    "3": {
        TABLE_VIEW: (
            "SWT.MULTI | SWT.FULL_SELECTION",
            "HopUiTheme.TABLE_GRID_LINES_VISIBLE",
            "HopUiTheme.TABLE_INDEX_COLUMN_WIDTH",
        ),
    },
    "4": {
        BASE_PAINTER: (
            "protected void drawNodeSelectionSurface(",
            "protected void drawNameHoverSurface(",
            "gc.setAlpha(38);",
            "gc.setForeground(EColor.HOP_DEFAULT);",
        ),
        PIPELINE_PAINTER: (
            "drawNodeSelectionSurface(x, y, iconSize, iconSize);",
            "gc.setFont(nameHovered ? EFont.GRAPH_BOLD : EFont.GRAPH);",
        ),
        WORKFLOW_PAINTER: (
            "drawNodeSelectionSurface(x, y, iconSize, iconSize);",
            "drawNameHoverSurface(xPos - 5, yPos - 2, nameExtent.x + 10, nameExtent.y + 6);",
        ),
    },
    "5A": {
        PROPS_UI: (
            "widget instanceof CCombo combo",
            "combo.setVisibleItemCount(HopUiTheme.COMBO_VISIBLE_ITEM_COUNT);",
        ),
        LABEL_COMBO: (
            "new CCombo(this, textFlags | SWT.FLAT)",
            "PropsUi.setLook(wCombo);",
        ),
        COMBO_VAR: ("new CCombo(this, flags | SWT.FLAT)",),
    },
}

# State v1 could be recorded while the Phase 1C branch still contained the earlier Web-toolbar
# spacer implementation. The final Phase 1C cleanup changed GuiToolbarWidgets.java without changing
# the structural 1C markers. Accept only this exact historical hash transition; all other managed
# file hash mismatches remain fatal.
LEGACY_HASH_TRANSITIONS = {
    (
        1,
        GUI_TOOLBAR,
        "c214f1f614a2562550e99e59981fd6a8e898a9846d38201a68021e47c59b5447",
        "7d91ba78ca39fd6e0eb3f4d7c149c9e9bafe7416e408d0f81f92189e0599ffee",
    ): "Phase 1C toolbar spacer cleanup",
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
    phases = {phase: phase_status(hop, phase) for phase in PHASE_ORDER}
    if any(value == "partial" for value in phases.values()):
        return phases

    for index, phase in enumerate(PHASE_ORDER[1:], start=1):
        previous = PHASE_ORDER[index - 1]
        if phases[phase] == "applied" and phases[previous] != "applied":
            phases[phase] = "partial"
    return phases


def dirty_paths(hop: Path) -> set[str]:
    # Do not pass porcelain output through git(), whose .strip() would remove the leading
    # whitespace of entries such as " M engine/..." and corrupt the path ("engine" -> "ngine").
    output = subprocess.check_output(
        ["git", "-C", str(hop), "status", "--porcelain", "--untracked-files=all"],
        text=True,
    )
    if not output:
        return set()
    paths: set[str] = set()
    for line in output.splitlines():
        if len(line) < 4:
            continue
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


def known_legacy_hash_transition(
    state_version: int,
    relative: str,
    expected_hash: str | None,
    actual_hash: str | None,
) -> bool:
    label = LEGACY_HASH_TRANSITIONS.get(
        (state_version, relative, expected_hash, actual_hash)
    )
    if label is None:
        return False
    print(f"Migrating known legacy managed-file state for {relative}: {label}.")
    return True


def verify_recorded_state(hop: Path, state: dict) -> dict[str, str]:
    state_version = state.get("version")
    if not isinstance(state_version, int) or state_version < 1 or state_version > STATE_VERSION:
        fail("patch state file belongs to an unsupported patch-manager version")
    if state.get("upstream") != UPSTREAM:
        fail("patch state file belongs to another Hop baseline")

    phases = detect_phases(hop)
    recorded_phases = state.get("phases", {})
    if not isinstance(recorded_phases, dict):
        fail("patch state file contains an invalid phase map")
    for phase, recorded_status in recorded_phases.items():
        if phase not in phases or phases[phase] != recorded_status:
            fail(
                "patch markers changed since the last managed run: "
                f"recorded={recorded_phases}, actual={phases}"
            )

    # Older state files know about fewer managed paths. Verify exactly what they recorded first;
    # once that succeeds we can safely migrate the state file to the current schema. A tiny set of
    # exact historical hash transitions is allowed for known patch-generated cleanup commits.
    expected_hashes = state.get("files", {})
    if not isinstance(expected_hashes, dict):
        fail("patch state file contains an invalid file hash map")
    for relative, expected_hash in expected_hashes.items():
        actual_hash = sha256(hop / relative)
        if actual_hash != expected_hash and not known_legacy_hash_transition(
            state_version, relative, expected_hash, actual_hash
        ):
            fail(f"unknown local change in managed file: {relative}")

    unknown = dirty_paths(hop) - allowed_paths(phases)
    if unknown:
        fail("unknown local changes outside the managed patch: " + ", ".join(sorted(unknown)))

    if state_version != STATE_VERSION or set(recorded_phases) != set(PHASE_ORDER):
        write_state(hop)
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
