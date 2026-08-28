#!/usr/bin/env python3
"""Apply Phase 1C toolbar refinements after the Phase 1A/1B patch."""

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
        fail("usage: apply_phase1c.py /path/to/apache-hop")

    hop = Path(sys.argv[1]).expanduser().resolve()
    if not (hop / ".git").exists():
        fail(f"{hop} is not a Git checkout")

    head = subprocess.check_output(
        ["git", "-C", str(hop), "rev-parse", "HEAD"], text=True
    ).strip()
    if head != UPSTREAM:
        fail(f"expected Apache Hop {UPSTREAM}, got {head}")

    # Phase 1C is intentionally layered on top of Phase 1A/1B. The checkout is expected to be
    # dirty at this point, but the shared theme file must already have been installed by Phase 1.
    theme = (
        hop
        / "ui"
        / "src"
        / "main"
        / "java"
        / "org"
        / "apache"
        / "hop"
        / "ui"
        / "core"
        / "gui"
        / "HopUiTheme.java"
    )
    if not theme.exists():
        fail("Phase 1 foundations are not applied: HopUiTheme.java is missing")
    theme_text = theme.read_text()
    for marker in ("SIDEBAR_WIDTH", "TOOLBAR_GROUP_GAP", "toolbarBackground"):
        if marker not in theme_text:
            fail(f"Phase 1 theme is missing expected marker: {marker}")

    hop_gui = (
        hop
        / "ui"
        / "src"
        / "main"
        / "java"
        / "org"
        / "apache"
        / "hop"
        / "ui"
        / "hopgui"
        / "HopGui.java"
    )

    # Use SWT's native flat toolbar mode. This is deliberately preferable to owner-drawing toolbar
    # buttons: SWT keeps platform hit testing, disabled state, keyboard behavior and accessibility.
    replace_exact(
        hop_gui,
        "ToolbarFacade.createToolbarContainer(shell, SWT.WRAP | SWT.RIGHT | SWT.HORIZONTAL);",
        "ToolbarFacade.createToolbarContainer(\n            shell, SWT.FLAT | SWT.WRAP | SWT.RIGHT | SWT.HORIZONTAL);",
        2,
    )
    replace_once(
        hop_gui,
        """    PropsUi.setLook(mainToolbar, Props.WIDGET_STYLE_TOOLBAR);\n\n    mainToolbarWidgets = new GuiToolbarWidgets();""",
        """    PropsUi.setLook(mainToolbar, Props.WIDGET_STYLE_TOOLBAR);\n    mainToolbar.setBackground(themeColor(HopUiTheme.toolbarBackground(props.isDarkMode())));\n\n    mainToolbarWidgets = new GuiToolbarWidgets();""",
    )
    replace_once(
        hop_gui,
        """    PropsUi.setLook(statusToolbar, Props.WIDGET_STYLE_TOOLBAR);\n\n    statusToolbarWidgets = new GuiToolbarWidgets();""",
        """    PropsUi.setLook(statusToolbar, Props.WIDGET_STYLE_TOOLBAR);\n    statusToolbar.setBackground(themeColor(HopUiTheme.toolbarBackground(props.isDarkMode())));\n\n    statusToolbarWidgets = new GuiToolbarWidgets();""",
    )

    toolbar = (
        hop
        / "ui"
        / "src"
        / "main"
        / "java"
        / "org"
        / "apache"
        / "hop"
        / "ui"
        / "core"
        / "gui"
        / "GuiToolbarWidgets.java"
    )

    # Replace visual separator grooves with whitespace. ToolItem#setControl on a separator is a
    # standard SWT mechanism, so this keeps the toolbar native while making grouping much quieter.
    replace_once(
        toolbar,
        """  /** ToolBar (desktop) path: add one item to an SWT ToolBar. */\n  private void addToolbarWidgetsToToolBar(ToolBar toolBar, GuiToolbarItem toolbarItem) {\n    if (toolbarItem.isAddingSeparator()) {\n      new ToolItem(toolBar, SWT.SEPARATOR);\n    }""",
        """  private int scaleUi(int value) {\n    return (int) Math.round(value * PropsUi.getNativeZoomFactor());\n  }\n\n  private void addToolbarGroupGap(ToolBar toolBar) {\n    ToolItem spacerItem = new ToolItem(toolBar, SWT.SEPARATOR);\n    Label spacer = new Label(toolBar, SWT.NONE);\n    spacer.setBackground(toolBar.getBackground());\n    spacerItem.setWidth(scaleUi(HopUiTheme.TOOLBAR_GROUP_GAP));\n    spacerItem.setControl(spacer);\n  }\n\n  /** ToolBar (desktop) path: add one item to an SWT ToolBar. */\n  private void addToolbarWidgetsToToolBar(ToolBar toolBar, GuiToolbarItem toolbarItem) {\n    if (toolbarItem.isAddingSeparator()) {\n      addToolbarGroupGap(toolBar);\n    }""",
    )

    replace_once(
        toolbar,
        """  /**\n   * Vertical separator with groove look for Hop Web toolbar (matches desktop ToolItem SEPARATOR).\n   * Uses toolbar background so no visible strip; draws groove full height with no top/bottom\n   * margin.\n   */\n  private void addWebToolbarSeparator(Composite parent) {\n    int width = 6;\n    int height = (int) (ConstUi.SMALL_ICON_SIZE * PropsUi.getNativeZoomFactor()) + 6;\n    Canvas canvas = new Canvas(parent, SWT.NONE);\n    canvas.setLayoutData(new RowData(width, height));\n    canvas.setBackground(parent.getBackground());\n    PropsUi.setLook(canvas, Props.WIDGET_STYLE_TOOLBAR);\n    canvas.addPaintListener(\n        new PaintListener() {\n          @Override\n          public void paintControl(PaintEvent e) {\n            GC gc = e.gc;\n            Display display = e.display;\n            Color highlight = display.getSystemColor(SWT.COLOR_WIDGET_LIGHT_SHADOW);\n            Color shadow = display.getSystemColor(SWT.COLOR_WIDGET_NORMAL_SHADOW);\n            int w = e.width;\n            int h = e.height;\n            int x = w / 2 - 1;\n            gc.setForeground(highlight);\n            gc.drawLine(x, 0, x, h - 1);\n            gc.setForeground(shadow);\n            gc.drawLine(x + 1, 0, x + 1, h - 1);\n          }\n        });\n  }""",
        """  /** Whitespace group gap for Hop Web, matching the flat desktop toolbar. */\n  private void addWebToolbarSeparator(Composite parent) {\n    int width = scaleUi(HopUiTheme.TOOLBAR_GROUP_GAP);\n    int height = scaleUi(HopUiTheme.TOOLBAR_ICON_SIZE + 2 * HopUiTheme.TOOLBAR_ITEM_PADDING);\n    Canvas canvas = new Canvas(parent, SWT.NONE);\n    canvas.setLayoutData(new RowData(width, height));\n    canvas.setBackground(parent.getBackground());\n    PropsUi.setLook(canvas, Props.WIDGET_STYLE_TOOLBAR);\n    canvas.addPaintListener(\n        new PaintListener() {\n          @Override\n          public void paintControl(PaintEvent e) {\n            // Deliberately paint only the toolbar surface: grouping is expressed by whitespace,\n            // not by the classic two-line SWT/RAP groove.\n            GC gc = e.gc;\n            Display display = e.display;\n            gc.setBackground(parent.getBackground());\n            gc.fillRectangle(0, 0, e.width, e.height);\n            display.getSystemColor(SWT.COLOR_WIDGET_BACKGROUND);\n          }\n        });\n  }""",
    )

    # Keep the current 16px visual icon size but make it a semantic theme token. This prevents the
    # main toolbar and web/RAP toolbar paths from drifting apart later.
    replace_once(
        toolbar,
        """    int width = ConstUi.SMALL_ICON_SIZE;\n    int height = ConstUi.SMALL_ICON_SIZE;""",
        """    int width = HopUiTheme.TOOLBAR_ICON_SIZE;\n    int height = HopUiTheme.TOOLBAR_ICON_SIZE;""",
    )
    replace_exact(
        toolbar,
        "ConstUi.SMALL_ICON_SIZE * PropsUi.getNativeZoomFactor() + toolbarItem.getExtraWidth()",
        "HopUiTheme.TOOLBAR_ICON_SIZE * PropsUi.getNativeZoomFactor()\n                + toolbarItem.getExtraWidth()",
        2,
    )

    # The two composite-based toolbar button paths (direct Web composite and RAP ToolBar wrapper)
    # use the same small internal spacing tokens.
    replace_exact(
        toolbar,
        """    layout.marginWidth = 0;\n    layout.marginHeight = 0;\n    layout.horizontalSpacing = 4;\n    layout.verticalSpacing = 0;""",
        """    layout.marginWidth = scaleUi(HopUiTheme.TOOLBAR_ITEM_PADDING);\n    layout.marginHeight = scaleUi(HopUiTheme.TOOLBAR_ITEM_PADDING);\n    layout.horizontalSpacing = scaleUi(HopUiTheme.TOOLBAR_CONTROL_GAP);\n    layout.verticalSpacing = 0;""",
        2,
    )

    print("Phase 1C applied: flat toolbars, whitespace groups, shared toolbar tokens.")


if __name__ == "__main__":
    main()
