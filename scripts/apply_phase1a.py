#!/usr/bin/env python3
"""Apply Phase 1A foundations to a pinned Apache Hop 2.19.0 checkout."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

from patch_state import UPSTREAM, fail


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text()
    if old not in text:
        fail(f"expected source fragment not found in {path}")
    if text.count(old) != 1:
        fail(f"source fragment is not unique in {path}")
    path.write_text(text.replace(old, new, 1))


def main() -> None:
    if len(sys.argv) != 2:
        fail("usage: apply_phase1a.py /path/to/apache-hop")

    hop = Path(sys.argv[1]).expanduser().resolve()
    if not (hop / ".git").exists():
        fail(f"{hop} is not a Git checkout")
    head = subprocess.check_output(["git", "-C", str(hop), "rev-parse", "HEAD"], text=True).strip()
    if head != UPSTREAM:
        fail(f"expected Apache Hop {UPSTREAM}, got {head}")

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
    text = props.read_text()
    text = text.replace("tabFolder.setBorderVisible(true);", "tabFolder.setBorderVisible(false);")
    text = text.replace("tabFolder.setTabHeight(28);", "tabFolder.setTabHeight(HopUiTheme.TAB_HEIGHT);")
    props.write_text(text)

    canvas = hop / "engine" / "src" / "main" / "java" / "org" / "apache" / "hop" / "core" / "gui" / "CanvasColorPalette.java"
    replace_once(canvas, "rgb(235, 235, 235),", "rgb(250, 250, 250),")
    replace_once(canvas, "rgb(215, 215, 215),\n        rgb(225, 225, 225),", "rgb(229, 231, 235),\n        rgb(238, 239, 241),")
    replace_once(canvas, "rgb(50, 50, 50),\n        rgb(255, 255, 255),", "rgb(32, 32, 32),\n        rgb(235, 235, 235),")

    print("Phase 1A applied: theme foundations, surfaces, tabs and canvas palette.")


if __name__ == "__main__":
    main()
