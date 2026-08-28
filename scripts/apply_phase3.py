#!/usr/bin/env python3
"""Apply Phase 3 shared TableView refinements to Apache Hop 2.19.0."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

UPSTREAM = "46436154ae1a1e940861d485559819360c2af86e"


def fail(message: str) -> None:
    raise SystemExit(f"hop-ui-patch: {message}")


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text()
    if old not in text:
        fail(f"expected source fragment not found in {path}")
    if text.count(old) != 1:
        fail(f"source fragment is not unique in {path}")
    path.write_text(text.replace(old, new, 1))


def replace_exact(path: Path, old: str, new: str, expected: int) -> None:
    text = path.read_text()
    count = text.count(old)
    if count != expected:
        fail(f"expected {expected} occurrences in {path}, found {count}: {old!r}")
    path.write_text(text.replace(old, new))


def main() -> None:
    if len(sys.argv) != 2:
        fail("usage: apply_phase3.py /path/to/apache-hop")

    hop = Path(sys.argv[1]).expanduser().resolve()
    if not (hop / ".git").exists():
        fail(f"{hop} is not a Git checkout")

    head = subprocess.check_output(
        ["git", "-C", str(hop), "rev-parse", "HEAD"], text=True
    ).strip()
    if head != UPSTREAM:
        fail(f"expected Apache Hop {UPSTREAM}, got {head}")

    theme = hop / "ui/src/main/java/org/apache/hop/ui/core/gui/HopUiTheme.java"
    if not theme.exists():
        fail("managed HopUiTheme.java is missing")
    theme_text = theme.read_text()
    for marker in ("TABLE_GRID_LINES_VISIBLE", "TABLE_INDEX_COLUMN_WIDTH"):
        if marker not in theme_text:
            fail(f"current managed theme is missing expected Phase 3 marker: {marker}")

    table_view = hop / "ui/src/main/java/org/apache/hop/ui/core/widget/TableView.java"
    replace_once(
        table_view,
        "import org.apache.hop.ui.core.gui.GuiResource;\n",
        "import org.apache.hop.ui.core.gui.GuiResource;\nimport org.apache.hop.ui.core.gui.HopUiTheme;\n",
    )
    replace_once(
        table_view,
        "table = new Table(this, style | SWT.MULTI);",
        "table = new Table(this, style | SWT.MULTI | SWT.FULL_SELECTION);",
    )
    replace_exact(
        table_view,
        "table.setLinesVisible(true);",
        "table.setLinesVisible(HopUiTheme.TABLE_GRID_LINES_VISIBLE);",
        2,
    )
    replace_once(
        table_view,
        "tableColumn[0].setWidth(addIndexColumn ? 25 : 0);",
        "tableColumn[0].setWidth(addIndexColumn ? HopUiTheme.TABLE_INDEX_COLUMN_WIDTH : 0);",
    )

    print(
        "Phase 3 applied: quieter shared tables with full-row selection, hidden grid lines and a clearer index column."
    )


if __name__ == "__main__":
    main()
