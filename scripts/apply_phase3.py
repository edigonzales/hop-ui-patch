#!/usr/bin/env python3
"""Apply Phase 3 table and preview-grid refinements to Apache Hop 2.19.0."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

UPSTREAM = "46436154ae1a1e940861d485559819360c2af86e"


def fail(message: str) -> None:
    raise SystemExit(f"hop-ui-patch: {message}")


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text()
    count = text.count(old)
    if count != 1:
        fail(f"expected one source fragment in {path}, found {count}: {old!r}")
    path.write_text(text.replace(old, new, 1))


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

    theme = (
        hop
        / "ui/src/main/java/org/apache/hop/ui/core/gui/HopUiTheme.java"
    )
    if not theme.exists():
        fail("Phase 1 foundations are not applied: HopUiTheme.java is missing")
    theme_text = theme.read_text()
    for marker in ("TABLE_INDEX_COLUMN_WIDTH", "TABLE_TOOLBAR_GAP", "TOOLBAR_GROUP_GAP"):
        if marker not in theme_text:
            fail(f"current managed theme is missing Phase 3 marker: {marker}")

    table_view = hop / "ui/src/main/java/org/apache/hop/ui/core/widget/TableView.java"

    replace_once(
        table_view,
        """import org.apache.hop.ui.core.gui.GuiResource;\nimport org.apache.hop.ui.core.gui.GuiToolbarWidgets;""",
        """import org.apache.hop.ui.core.gui.GuiResource;\nimport org.apache.hop.ui.core.gui.GuiToolbarWidgets;\nimport org.apache.hop.ui.core.gui.HopUiTheme;""",
    )

    # Keep the native SWT Table and its platform selection behavior, but remove the full cell grid.
    # The header remains visible and receives Hop's quiet panel surface on Windows/Linux; macOS keeps
    # its native header foreground treatment.
    replace_once(
        table_view,
        """    table = new Table(this, style | SWT.MULTI);\n    PropsUi.setLook(table);\n    table.setLinesVisible(true);""",
        """    table = new Table(this, style | SWT.MULTI);\n    PropsUi.setLook(table);\n    table.setLinesVisible(false);\n    if (!Const.isOSX()) {\n      GuiResource gui = GuiResource.getInstance();\n      table.setHeaderBackground(gui.getColorDemoGray());\n      table.setHeaderForeground(gui.getColorBlack());\n    }""",
    )

    # TableView already uses the shared toolbar infrastructure, so Phase 1C's whitespace grouping
    # automatically applies here. SWT.FLAT removes the remaining native toolbar ridge.
    replace_once(
        table_view,
        "ToolbarFacade.createToolbarContainer(this, SWT.WRAP | SWT.LEFT | SWT.HORIZONTAL);",
        "ToolbarFacade.createToolbarContainer(\n              this, SWT.FLAT | SWT.WRAP | SWT.LEFT | SWT.HORIZONTAL);",
    )
    replace_once(
        table_view,
        """      PropsUi.setLook(toolbar, Props.WIDGET_STYLE_TOOLBAR);\n\n      toolbarWidgets.createToolbarWidgets(toolBarContainer, ID_TOOLBAR, removeToolItems);""",
        """      PropsUi.setLook(toolbar, Props.WIDGET_STYLE_TOOLBAR);\n      toolbar.setBackground(GuiResource.getInstance().getColorDemoGray());\n\n      toolbarWidgets.createToolbarWidgets(toolBarContainer, ID_TOOLBAR, removeToolItems);""",
    )

    replace_once(
        table_view,
        "fdTable.top = new FormAttachment(toolbar, 0);",
        "fdTable.top =\n          new FormAttachment(\n              toolbar,\n              (int) Math.round(HopUiTheme.TABLE_TOOLBAR_GAP * PropsUi.getNativeZoomFactor()));",
    )

    replace_once(
        table_view,
        "tableColumn[0].setWidth(addIndexColumn ? 25 : 0);",
        "tableColumn[0].setWidth(addIndexColumn ? HopUiTheme.TABLE_INDEX_COLUMN_WIDTH : 0);",
    )

    print(
        "Phase 3 applied: quieter TableView grid, flat table toolbar, modern header and index spacing."
    )


if __name__ == "__main__":
    main()
