#!/usr/bin/env python3
"""Apply Phase 5A CCombo refinements to Apache Hop 2.19.0."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from patch_state import UPSTREAM, fail


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text()
    count = text.count(old)
    if count != 1:
        fail(f"expected one source fragment in {path}, found {count}: {old!r}")
    path.write_text(text.replace(old, new, 1))


def main() -> None:
    if len(sys.argv) != 2:
        fail("usage: apply_phase5a.py /path/to/apache-hop")

    hop = Path(sys.argv[1]).expanduser().resolve()
    if not (hop / ".git").exists():
        fail(f"{hop} is not a Git checkout")

    head = subprocess.check_output(
        ["git", "-C", str(hop), "rev-parse", "HEAD"], text=True
    ).strip()
    if head != UPSTREAM:
        fail(f"expected Apache Hop {UPSTREAM}, got {head}")

    props = hop / "ui/src/main/java/org/apache/hop/ui/core/PropsUi.java"
    label_combo = hop / "ui/src/main/java/org/apache/hop/ui/core/widget/LabelCombo.java"
    combo_var = hop / "ui/src/main/java/org/apache/hop/ui/core/widget/ComboVar.java"

    replace_once(
        props,
        "import org.eclipse.swt.custom.CTabFolder;",
        "import org.eclipse.swt.custom.CCombo;\nimport org.eclipse.swt.custom.CTabFolder;",
    )
    replace_once(
        props,
        """    setLook(widget, style);\n\n    if (widget instanceof Composite composite) {""",
        """    setLook(widget, style);\n\n    if (widget instanceof CCombo combo) {\n      combo.setVisibleItemCount(HopUiTheme.COMBO_VISIBLE_ITEM_COUNT);\n    }\n\n    if (widget instanceof Composite composite) {""",
    )

    # LabelCombo creates its CCombo after PropsUi.setLook(this), so the recursive look pass cannot
    # see the child. Apply the shared look explicitly and use CCombo's supported FLAT style.
    replace_once(
        label_combo,
        """    wCombo = new CCombo(this, textFlags);\n    FormData fdText = new FormData();""",
        """    wCombo = new CCombo(this, textFlags | SWT.FLAT);\n    PropsUi.setLook(wCombo);\n    FormData fdText = new FormData();""",
    )

    # ComboVar is the other shared CCombo wrapper. It already applies PropsUi.setLook(wCombo), so
    # only the construction style needs to be flattened.
    replace_once(
        combo_var,
        "wCombo = new CCombo(this, flags);",
        "wCombo = new CCombo(this, flags | SWT.FLAT);",
    )

    print(
        "Phase 5A applied: compact CCombo dropdowns and flatter shared combo controls."
    )


if __name__ == "__main__":
    main()
