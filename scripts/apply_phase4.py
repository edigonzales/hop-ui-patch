#!/usr/bin/env python3
"""Apply Phase 4 canvas interaction-feedback refinements to Apache Hop 2.19.0."""

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
        fail("usage: apply_phase4.py /path/to/apache-hop")

    hop = Path(sys.argv[1]).expanduser().resolve()
    if not (hop / ".git").exists():
        fail(f"{hop} is not a Git checkout")

    head = subprocess.check_output(
        ["git", "-C", str(hop), "rev-parse", "HEAD"], text=True
    ).strip()
    if head != UPSTREAM:
        fail(f"expected Apache Hop {UPSTREAM}, got {head}")

    base_painter = hop / "engine/src/main/java/org/apache/hop/core/gui/BasePainter.java"
    pipeline_painter = hop / "engine/src/main/java/org/apache/hop/pipeline/PipelinePainter.java"
    workflow_painter = hop / "engine/src/main/java/org/apache/hop/workflow/WorkflowPainter.java"

    # Keep interaction colors inside the engine's existing EColor vocabulary. The engine module must
    # not depend on the SWT/UI HopUiTheme class. SwtGc/SvgGc already map these semantic colors to the
    # active desktop/Web palette.
    replace_once(
        base_painter,
        """  protected boolean isWebCanvasRendering() {\n    return gc instanceof SvgGc;\n  }\n\n  public static EImage getStreamIconImage(StreamIcon streamIcon, boolean enabled) {""",
        """  protected boolean isWebCanvasRendering() {\n    return gc instanceof SvgGc;\n  }\n\n  /**\n   * Draw a restrained selection halo around a graph node without changing the node's own status\n   * border. Using the existing EColor palette keeps engine/UI module boundaries intact.\n   */\n  protected void drawNodeSelectionSurface(int x, int y, int width, int height) {\n    int inset = Math.max(4, lineWidth + 2);\n    int previousAlpha = gc.getAlpha();\n\n    gc.setAlpha(64);\n    gc.setBackground(EColor.LIGHTBLUE);\n    gc.fillRoundRectangle(\n        x - inset, y - inset, width + 2 * inset, height + 2 * inset, 12, 12);\n\n    gc.setAlpha(previousAlpha);\n    gc.setForeground(EColor.HOP_DEFAULT);\n    gc.setLineWidth(Math.max(1, lineWidth + 1));\n    gc.drawRoundRectangle(\n        x - inset, y - inset, width + 2 * inset, height + 2 * inset, 12, 12);\n    gc.setLineWidth(lineWidth);\n  }\n\n  /** Subtle hover surface behind a transform/action name; text is drawn by the caller. */\n  protected void drawNameHoverSurface(int x, int y, int width, int height) {\n    int previousAlpha = gc.getAlpha();\n    gc.setAlpha(105);\n    gc.setBackground(EColor.LIGHTGRAY);\n    gc.fillRoundRectangle(x, y, width, height, 8, 8);\n    gc.setAlpha(previousAlpha);\n  }\n\n  public static EImage getStreamIconImage(StreamIcon streamIcon, boolean enabled) {""",
    )

    # Replace the old outline-only DASHDOT lasso with a translucent selection surface and a quiet
    # Hop accent border. Selection semantics and hit testing remain untouched.
    replace_once(
        base_painter,
        """  protected void drawRect(Rectangle rect) {\n    if (rect == null) {\n      return;\n    }\n    gc.setLineStyle(ELineStyle.DASHDOT);\n    gc.setLineWidth(lineWidth);\n    gc.setForeground(EColor.BLACK);\n    // SWT on Windows doesn't cater for negative rect.width/height so handle here.\n    Point s = real2screen(rect.x, rect.y);\n    if (rect.width < 0) {\n      s.x = s.x + rect.width;\n    }\n    if (rect.height < 0) {\n      s.y = s.y + rect.height;\n    }\n    gc.drawRectangle(s.x, s.y, Math.abs(rect.width), Math.abs(rect.height));\n    gc.setLineStyle(ELineStyle.SOLID);\n  }""",
        """  protected void drawRect(Rectangle rect) {\n    if (rect == null) {\n      return;\n    }\n\n    // SWT on Windows doesn't cater for negative rect.width/height so normalise first.\n    Point s = real2screen(rect.x, rect.y);\n    if (rect.width < 0) {\n      s.x = s.x + rect.width;\n    }\n    if (rect.height < 0) {\n      s.y = s.y + rect.height;\n    }\n    int width = Math.abs(rect.width);\n    int height = Math.abs(rect.height);\n\n    int previousAlpha = gc.getAlpha();\n    gc.setAlpha(38);\n    gc.setBackground(EColor.LIGHTBLUE);\n    gc.fillRectangle(s.x, s.y, width, height);\n    gc.setAlpha(previousAlpha);\n\n    gc.setLineStyle(ELineStyle.DASH);\n    gc.setLineWidth(Math.max(1, lineWidth));\n    gc.setForeground(EColor.HOP_DEFAULT);\n    gc.drawRectangle(s.x, s.y, width, height);\n    gc.setLineStyle(ELineStyle.SOLID);\n  }""",
    )

    replace_once(
        pipeline_painter,
        """    String name = transformMeta.getName();\n\n    if (transformMeta.isSelected()) {\n      gc.setLineWidth(lineWidth + 2);\n    } else {\n      gc.setLineWidth(lineWidth);\n    }""",
        """    String name = transformMeta.getName();\n\n    if (transformMeta.isSelected()) {\n      drawNodeSelectionSurface(x, y, iconSize, iconSize);\n      gc.setLineWidth(lineWidth + 2);\n    } else {\n      gc.setLineWidth(lineWidth);\n    }""",
    )

    replace_once(
        pipeline_painter,
        """    gc.setForeground(EColor.BLACK);\n    boolean nameHovered = name.equals(mouseOverName);\n    if (nameHovered && isWebCanvasRendering()) {\n      gc.setFont(EFont.GRAPH_BOLD);\n    } else {\n      gc.setFont(EFont.GRAPH);\n    }\n    gc.drawText(name, namePosition.x, namePosition.y + 2, true);\n    boolean partitioned = false;\n\n    // Desktop: underline on hover. Hop Web: bold (see drawText above).\n    if (nameHovered && !isWebCanvasRendering()) {\n      gc.setLineWidth(lineWidth);\n      gc.drawLine(\n          namePosition.x,\n          namePosition.y + nameExtent.y,\n          namePosition.x + nameExtent.x,\n          namePosition.y + nameExtent.y);\n    }""",
        """    boolean nameHovered = name.equals(mouseOverName);\n    if (nameHovered && !isDrawingBorderAroundName()) {\n      drawNameHoverSurface(\n          namePosition.x - 5, namePosition.y, nameExtent.x + 10, nameExtent.y + 6);\n    }\n    gc.setForeground(EColor.BLACK);\n    gc.setFont(nameHovered ? EFont.GRAPH_BOLD : EFont.GRAPH);\n    gc.drawText(name, namePosition.x, namePosition.y + 2, true);\n    boolean partitioned = false;""",
    )

    replace_once(
        workflow_painter,
        """    String name = actionMeta.getName();\n    if (actionMeta.isSelected()) {\n      gc.setLineWidth(3);\n    } else {\n      gc.setLineWidth(1);\n    }""",
        """    String name = actionMeta.getName();\n    if (actionMeta.isSelected()) {\n      drawNodeSelectionSurface(x, y, iconSize, iconSize);\n      gc.setLineWidth(3);\n    } else {\n      gc.setLineWidth(1);\n    }""",
    )

    replace_once(
        workflow_painter,
        """    gc.setForeground(EColor.BLACK);\n    boolean nameHovered = name.equals(mouseOverName);\n    if (nameHovered && isWebCanvasRendering()) {\n      gc.setFont(EFont.GRAPH_BOLD);\n    } else {\n      gc.setFont(EFont.GRAPH);\n    }\n    gc.drawText(name, xPos, yPos, true);\n\n    // Desktop: underline on hover. Hop Web: bold (see drawText above).\n    if (nameHovered && !isWebCanvasRendering()) {\n      gc.drawLine(xPos, yPos + nameExtent.y, xPos + nameExtent.x, yPos + nameExtent.y);\n    }""",
        """    boolean nameHovered = name.equals(mouseOverName);\n    if (nameHovered && !isDrawingBorderAroundName()) {\n      drawNameHoverSurface(xPos - 5, yPos - 2, nameExtent.x + 10, nameExtent.y + 6);\n    }\n    gc.setForeground(EColor.BLACK);\n    gc.setFont(nameHovered ? EFont.GRAPH_BOLD : EFont.GRAPH);\n    gc.drawText(name, xPos, yPos, true);""",
    )

    print(
        "Phase 4 applied: selected-node halos, consistent name hover and translucent lasso feedback."
    )


if __name__ == "__main__":
    main()
