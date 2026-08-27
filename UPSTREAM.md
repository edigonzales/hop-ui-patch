# Upstream baseline

This patch set is developed against Apache Hop `main` at:

- repository: `apache/hop`
- commit: `bab67a10d01b76e6f93f30dde735d50fc87c1b04`
- date: 2026-08-27

The pin is intentional. SWT/UI code changes quickly enough that a visual patch should fail loudly rather than silently apply to a structurally different revision.

When rebasing the patch, inspect at least these files in upstream Hop:

- `ui/src/main/java/org/apache/hop/ui/core/gui/GuiResource.java`
- `ui/src/main/java/org/apache/hop/ui/core/PropsUi.java`
- `engine/src/main/java/org/apache/hop/core/gui/CanvasColorPalette.java`
- `ui/src/main/java/org/apache/hop/ui/core/gui/GuiToolbarWidgets.java`
- `ui/src/main/java/org/apache/hop/ui/hopgui/HopGui.java`

The first three are modified in Phase 1. Toolbar and perspective/sidebar work is intentionally deferred until the common visual tokens exist.