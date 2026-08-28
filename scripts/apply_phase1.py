#!/usr/bin/env python3
"""Apply Phase 1 of hop-ui-patch to a pinned Apache Hop 2.19.0 checkout."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

# Apache Hop 2.19.0 release source (tag 2.19.0-rc1).
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


def main() -> None:
    if len(sys.argv) != 2:
        fail("usage: apply_phase1.py /path/to/apache-hop")

    hop = Path(sys.argv[1]).expanduser().resolve()
    if not (hop / ".git").exists():
        fail(f"{hop} is not a Git checkout")

    head = subprocess.check_output(["git", "-C", str(hop), "rev-parse", "HEAD"], text=True).strip()
    dirty = subprocess.check_output(["git", "-C", str(hop), "status", "--porcelain"], text=True).strip()
    allow_dirty = os.environ.get("HOP_UI_PATCH_ALLOW_DIRTY") == "1"

    if head != UPSTREAM and not allow_dirty:
        fail(f"expected Apache Hop {UPSTREAM}, got {head}; set HOP_UI_PATCH_ALLOW_DIRTY=1 to override")
    if dirty and not allow_dirty:
        fail("Apache Hop checkout has local changes; set HOP_UI_PATCH_ALLOW_DIRTY=1 to override")

    repo = Path(__file__).resolve().parents[1]
    overlay = repo / "overlay" / "ui" / "src" / "main" / "java" / "org" / "apache" / "hop" / "ui" / "core" / "gui" / "HopUiTheme.java"
    target = hop / "ui" / "src" / "main" / "java" / "org" / "apache" / "hop" / "ui" / "core" / "gui" / "HopUiTheme.java"
    shutil.copyfile(overlay, target)

    gui = hop / "ui" / "src" / "main" / "java" / "org" / "apache" / "hop" / "ui" / "core" / "gui" / "GuiResource.java"
    replace_once(
        gui,
        """    colorBackground = new Color(display, props.contrastColor(new RGB(240, 240, 240)));\n    colorGraph = new Color(display, props.contrastColor(new RGB(235, 235, 235)));\n""",
        """    colorBackground = new Color(display, HopUiTheme.applicationBackground(props.isDarkMode()));\n    colorGraph = new Color(display, HopUiTheme.canvasBackground(props.isDarkMode()));\n""",
    )
    replace_once(
        gui,
        """    colorDemoGray = new Color(display, props.contrastColor(240, 240, 240));\n    colorLightGray = new Color(display, props.contrastColor(225, 225, 225));\n    colorGray = new Color(display, props.contrastColor(215, 215, 215));\n""",
        """    colorDemoGray = new Color(display, HopUiTheme.panelBackground(props.isDarkMode()));\n    colorLightGray = new Color(display, HopUiTheme.separator(props.isDarkMode()));\n    colorGray = new Color(display, props.contrastColor(215, 215, 215));\n""",
    )

    props = hop / "ui" / "src" / "main" / "java" / "org" / "apache" / "hop" / "ui" / "core" / "PropsUi.java"
    replace_once(
        props,
        "return (int) Math.round(8 * getNativeZoomFactor());",
        "return (int) Math.round(HopUiTheme.SPACING_MEDIUM * getNativeZoomFactor());",
    )
    replace_once(
        props,
        "import org.apache.hop.ui.core.gui.GuiResource;",
        "import org.apache.hop.ui.core.gui.GuiResource;\nimport org.apache.hop.ui.core.gui.HopUiTheme;",
    )
    # Tabs remain native SWT controls, but removing the extra CTabFolder border and shaving two
    # pixels off the fixed height makes the shell visibly quieter without owner drawing.
    text = props.read_text()
    text = text.replace("tabFolder.setBorderVisible(true);", "tabFolder.setBorderVisible(false);")
    text = text.replace("tabFolder.setTabHeight(28);", "tabFolder.setTabHeight(HopUiTheme.TAB_HEIGHT);")
    props.write_text(text)

    canvas = hop / "engine" / "src" / "main" / "java" / "org" / "apache" / "hop" / "core" / "gui" / "CanvasColorPalette.java"
    replace_once(canvas, "rgb(235, 235, 235),", "rgb(250, 250, 250),")
    replace_once(canvas, "rgb(215, 215, 215),\n        rgb(225, 225, 225),", "rgb(229, 231, 235),\n        rgb(238, 239, 241),")
    replace_once(canvas, "rgb(50, 50, 50),\n        rgb(255, 255, 255),", "rgb(32, 32, 32),\n        rgb(235, 235, 235),")

    # Phase 1B: turn the perspective sidebar into a compact IDE-style rail. Apache Hop 2.19 already
    # owner-draws these buttons, so we refine that existing custom control rather than introducing
    # another widget abstraction.
    hop_gui = hop / "ui" / "src" / "main" / "java" / "org" / "apache" / "hop" / "ui" / "hopgui" / "HopGui.java"
    replace_once(
        hop_gui,
        """import org.apache.hop.ui.core.gui.GuiToolbarWidgets;\nimport org.apache.hop.ui.core.gui.HopNamespace;\nimport org.apache.hop.ui.core.gui.IToolbarContainer;""",
        """import org.apache.hop.ui.core.gui.GuiToolbarWidgets;\nimport org.apache.hop.ui.core.gui.HopNamespace;\nimport org.apache.hop.ui.core.gui.HopUiTheme;\nimport org.apache.hop.ui.core.gui.IToolbarContainer;""",
    )
    replace_once(
        hop_gui,
        """import org.eclipse.swt.graphics.Point;\nimport org.eclipse.swt.graphics.Rectangle;""",
        """import org.eclipse.swt.graphics.Point;\nimport org.eclipse.swt.graphics.Rectangle;\nimport org.eclipse.swt.graphics.RGB;""",
    )
    replace_once(
        hop_gui,
        """  private void loadPerspectives() {""",
        """  private Color themeColor(RGB rgb) {\n    return GuiResource.getInstance().getColor(rgb.red, rgb.green, rgb.blue);\n  }\n\n  private int scaleUi(int value) {\n    return (int) Math.round(value * PropsUi.getNativeZoomFactor());\n  }\n\n  private void paintSidebarButtonBackground(\n      GC gc,\n      Point size,\n      boolean selected,\n      boolean hovered,\n      Color normalBg,\n      Color hoverBg,\n      Color selectionBg,\n      Color indicatorColor) {\n    gc.setBackground(selected ? selectionBg : hovered ? hoverBg : normalBg);\n    int inset = scaleUi(2);\n    gc.fillRectangle(\n        inset,\n        inset,\n        Math.max(1, size.x - 2 * inset),\n        Math.max(1, size.y - 2 * inset));\n\n    if (selected) {\n      int indicatorWidth = Math.max(1, scaleUi(HopUiTheme.SIDEBAR_INDICATOR_WIDTH));\n      int indicatorInset = scaleUi(HopUiTheme.SIDEBAR_INDICATOR_INSET);\n      gc.setBackground(indicatorColor);\n      gc.fillRectangle(\n          0,\n          indicatorInset,\n          indicatorWidth,\n          Math.max(1, size.y - 2 * indicatorInset));\n    }\n  }\n\n  private void loadPerspectives() {""",
    )
    replace_once(
        hop_gui,
        "int sidebarIconSize = 21;",
        "int sidebarIconSize = HopUiTheme.SIDEBAR_ICON_SIZE;",
    )
    replace_once(
        hop_gui,
        """        // Create styled sidebar button with hover, selection, and rounded corners\n        // This works for both desktop SWT and web/RAP modes""",
        """        // Create a compact sidebar rail button with hover and selection states.\n        // Desktop SWT gets the active indicator; RAP keeps the same semantic colors.""",
    )
    replace_once(
        hop_gui,
        """  /**\n   * Create a styled sidebar button with modern appearance. Features rounded corners, hover effects,\n   * and selection colors.\n   */""",
        """  /** Create a compact perspective-rail button with restrained hover and selection states. */""",
    )
    replace_once(
        hop_gui,
        """    GridData gd = new GridData();\n    gd.widthHint = (int) (34 * PropsUi.getNativeZoomFactor());\n    gd.heightHint = (int) (34 * PropsUi.getNativeZoomFactor());\n    button.composite.setLayoutData(gd);""",
        """    GridData gd = new GridData(SWT.CENTER, SWT.CENTER, false, false);\n    gd.widthHint = scaleUi(HopUiTheme.SIDEBAR_BUTTON_SIZE);\n    gd.heightHint = scaleUi(HopUiTheme.SIDEBAR_BUTTON_SIZE);\n    button.composite.setLayoutData(gd);""",
    )
    replace_once(
        hop_gui,
        "/** Custom sidebar button class with hover, selection, and rounded corners */",
        "/** Custom sidebar button class for the compact perspective rail. */",
    )
    replace_once(
        hop_gui,
        """    Color selectionBg = GuiResource.getInstance().getColorLightBlue();\n    Color hoverBg = GuiResource.getInstance().getColorGray();\n    Color normalBg = GuiResource.getInstance().getWidgetBackGroundColor();""",
        """    Color selectionBg = themeColor(HopUiTheme.sidebarSelection(props.isDarkMode()));\n    Color hoverBg = themeColor(HopUiTheme.sidebarHover(props.isDarkMode()));\n    Color normalBg = themeColor(HopUiTheme.sidebarBackground(props.isDarkMode()));\n    Color indicatorColor = themeColor(HopUiTheme.sidebarIndicator(props.isDarkMode()));""",
    )
    replace_once(
        hop_gui,
        """              gc.setAntialias(SWT.ON);\n\n              // Choose background color\n              if (isSelected) {\n                gc.setBackground(selectionBg);\n              } else if (isHovered) {\n                gc.setBackground(hoverBg);\n              } else {\n                gc.setBackground(normalBg);\n              }\n\n              // Fill rounded rectangle\n              gc.fillRoundRectangle(4, 4, size.x - 8, size.y - 8, 8, 8);""",
        """              paintSidebarButtonBackground(\n                  gc,\n                  size,\n                  isSelected,\n                  isHovered,\n                  normalBg,\n                  hoverBg,\n                  selectionBg,\n                  indicatorColor);""",
    )
    replace_once(
        hop_gui,
        """    int sidebarWidth = (int) (40 * PropsUi.getNativeZoomFactor());""",
        """    int sidebarWidth = scaleUi(HopUiTheme.SIDEBAR_WIDTH);""",
    )
    replace_once(
        hop_gui,
        """    perspectivesSidebar = new Composite(mainHopGuiComposite, SWT.NONE);\n    PropsUi.setLook(perspectivesSidebar);\n    perspectivesSidebar.setLayout(new FormLayout());""",
        """    perspectivesSidebar = new Composite(mainHopGuiComposite, SWT.NONE);\n    PropsUi.setLook(perspectivesSidebar);\n    Color sidebarBackground = themeColor(HopUiTheme.sidebarBackground(props.isDarkMode()));\n    perspectivesSidebar.setBackground(sidebarBackground);\n    perspectivesSidebar.setLayout(new FormLayout());""",
    )
    replace_once(
        hop_gui,
        """    perspectivesLayout.marginWidth = 1;\n    perspectivesLayout.marginHeight = 2;\n    perspectivesLayout.verticalSpacing = 1; // Minimal spacing between buttons\n    perspectivesContainer.setLayout(perspectivesLayout);""",
        """    perspectivesLayout.marginWidth = HopUiTheme.SPACING_SMALL / 2;\n    perspectivesLayout.marginHeight = HopUiTheme.SPACING_SMALL;\n    perspectivesLayout.verticalSpacing = HopUiTheme.SPACING_SMALL / 2;\n    perspectivesContainer.setLayout(perspectivesLayout);\n    perspectivesContainer.setBackground(sidebarBackground);""",
    )
    replace_once(
        hop_gui,
        """    bottomLayout.marginWidth = 0;\n    bottomLayout.marginHeight = 0;\n    bottomLayout.verticalSpacing = 1;\n    bottomToolbar.setLayout(bottomLayout);\n    bottomToolbar.setBackground(GuiResource.getInstance().getWidgetBackGroundColor());""",
        """    bottomLayout.marginWidth = HopUiTheme.SPACING_SMALL / 2;\n    bottomLayout.marginHeight = HopUiTheme.SPACING_SMALL;\n    bottomLayout.verticalSpacing = HopUiTheme.SPACING_SMALL / 2;\n    bottomToolbar.setLayout(bottomLayout);\n    bottomToolbar.setBackground(sidebarBackground);""",
    )
    replace_once(
        hop_gui,
        "fdBottomToolbar.bottom = new FormAttachment(100, -4);",
        "fdBottomToolbar.bottom = new FormAttachment(100, 0);",
    )
    replace_once(
        hop_gui,
        "int sidebarIconSize = 24;",
        "int sidebarIconSize = HopUiTheme.SIDEBAR_ICON_SIZE;",
    )
    replace_once(
        hop_gui,
        "fdSidebar.width = (int) (34 * PropsUi.getNativeZoomFactor());",
        "fdSidebar.width = scaleUi(HopUiTheme.SIDEBAR_WIDTH);",
    )
    replace_once(
        hop_gui,
        """    Color normalBg = GuiResource.getInstance().getWidgetBackGroundColor();\n    Color selectionBg = GuiResource.getInstance().getColorLightBlue();\n    Color hoverBg = GuiResource.getInstance().getColorGray();\n    int buttonSize = (int) (34 * PropsUi.getNativeZoomFactor());""",
        """    Color normalBg = themeColor(HopUiTheme.sidebarBackground(props.isDarkMode()));\n    Color selectionBg = themeColor(HopUiTheme.sidebarSelection(props.isDarkMode()));\n    Color hoverBg = themeColor(HopUiTheme.sidebarHover(props.isDarkMode()));\n    Color indicatorColor = themeColor(HopUiTheme.sidebarIndicator(props.isDarkMode()));\n    int buttonSize = scaleUi(HopUiTheme.SIDEBAR_BUTTON_SIZE);""",
    )
    replace_once(
        hop_gui,
        """        GridData gd = new GridData();\n        gd.widthHint = buttonSize;\n        gd.heightHint = buttonSize;\n        canvas.setLayoutData(gd);""",
        """        GridData gd = new GridData(SWT.CENTER, SWT.CENTER, false, false);\n        gd.widthHint = buttonSize;\n        gd.heightHint = buttonSize;\n        canvas.setLayoutData(gd);""",
    )
    replace_once(
        hop_gui,
        """              gc.setAntialias(SWT.ON);\n\n              boolean sel = Boolean.TRUE.equals(canvas.getData(\"selected\"));\n              boolean hov = Boolean.TRUE.equals(canvas.getData(\"hovered\"));\n              gc.setBackground(sel ? selectionBg : hov ? hoverBg : normalBg);\n              gc.fillRoundRectangle(4, 4, size.x - 8, size.y - 8, 8, 8);""",
        """              boolean sel = Boolean.TRUE.equals(canvas.getData(\"selected\"));\n              boolean hov = Boolean.TRUE.equals(canvas.getData(\"hovered\"));\n              paintSidebarButtonBackground(\n                  gc,\n                  size,\n                  sel,\n                  hov,\n                  normalBg,\n                  hoverBg,\n                  selectionBg,\n                  indicatorColor);""",
    )

    print("Phase 1A + 1B applied.")
    print("Review with: git -C", hop, "diff -- ui engine/src/main/java/org/apache/hop/core/gui/CanvasColorPalette.java")


if __name__ == "__main__":
    main()
