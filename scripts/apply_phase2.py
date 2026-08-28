#!/usr/bin/env python3
"""Apply Phase 2 shared dialog/form refinements to Apache Hop 2.19.0."""

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


def main() -> None:
    if len(sys.argv) != 2:
        fail("usage: apply_phase2.py /path/to/apache-hop")

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
        fail("Phase 1 foundations are not applied: HopUiTheme.java is missing")
    theme_text = theme.read_text()
    for marker in ("DIALOG_MARGIN", "DIALOG_ELEMENT_GAP", "FORM_LABEL_GAP"):
        if marker not in theme_text:
            fail(f"current managed theme is missing expected Phase 2 marker: {marker}")

    base_dialog = hop / "ui/src/main/java/org/apache/hop/ui/core/dialog/BaseDialog.java"
    replace_once(
        base_dialog,
        "import org.apache.hop.ui.core.gui.GuiResource;\n",
        "import org.apache.hop.ui.core.gui.GuiResource;\nimport org.apache.hop.ui.core.gui.HopUiTheme;\n",
    )
    replace_once(
        base_dialog,
        """  public static final int MARGIN_SIZE = 15;\n  public static final int LABEL_SPACING = 5;\n  public static final int ELEMENT_SPACING = 10;""",
        """  public static final int MARGIN_SIZE = HopUiTheme.DIALOG_MARGIN;\n  public static final int LABEL_SPACING = HopUiTheme.FORM_LABEL_GAP;\n  public static final int ELEMENT_SPACING = HopUiTheme.DIALOG_ELEMENT_GAP;""",
    )

    label_text = hop / "ui/src/main/java/org/apache/hop/ui/core/widget/LabelText.java"
    replace_once(
        label_text,
        "import org.apache.hop.ui.core.PropsUi;\n",
        "import org.apache.hop.ui.core.PropsUi;\nimport org.apache.hop.ui.core.gui.HopUiTheme;\n",
    )
    replace_once(
        label_text,
        """        props.getMiddlePct(),\n        PropsUi.getMargin());""",
        """        props.getMiddlePct(),\n        HopUiTheme.FORM_LABEL_GAP);""",
    )
    replace_once(
        label_text,
        """    super(composite, SWT.NONE);\n\n    FormLayout formLayout = new FormLayout();""",
        """    super(composite, SWT.NONE);\n    PropsUi.setLook(this);\n\n    FormLayout formLayout = new FormLayout();""",
    )

    for relative in (
        "ui/src/main/java/org/apache/hop/ui/core/widget/LabelTextVar.java",
        "ui/src/main/java/org/apache/hop/ui/core/widget/LabelCombo.java",
        "ui/src/main/java/org/apache/hop/ui/core/widget/LabelComboVar.java",
    ):
        path = hop / relative
        replace_once(
            path,
            "import org.apache.hop.ui.core.PropsUi;\n",
            "import org.apache.hop.ui.core.PropsUi;\nimport org.apache.hop.ui.core.gui.HopUiTheme;\n",
        )
        replace_once(
            path,
            "    int margin = PropsUi.getMargin();",
            "    int margin = HopUiTheme.FORM_LABEL_GAP;",
        )

    print(
        "Phase 2 applied: semantic dialog spacing and consistent shared label/control form rows."
    )


if __name__ == "__main__":
    main()
