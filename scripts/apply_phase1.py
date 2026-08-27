#!/usr/bin/env python3
"""Apply Phase 1 of hop-ui-patch to a pinned Apache Hop checkout."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

UPSTREAM = "bab67a10d01b76e6f93f30dde735d50fc87c1b04"


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

    print("Phase 1 applied.")
    print("Review with: git -C", hop, "diff -- ui engine/src/main/java/org/apache/hop/core/gui/CanvasColorPalette.java")


if __name__ == "__main__":
    main()
