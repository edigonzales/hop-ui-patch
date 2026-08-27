# Upstream baseline

This patch set is developed against Apache Hop `2.19.0` at:

- repository: `apache/hop`
- release source tag: `2.19.0-rc1`
- commit: `46436154ae1a1e940861d485559819360c2af86e`
- release branch: `release/2.19.0`

The root Maven project at this commit has version `2.19.0`. The exact commit pin is intentional: SWT/UI code changes quickly enough that a visual patch should fail loudly rather than silently apply to a structurally different revision.

When rebasing the patch, inspect at least these files in upstream Hop:

- `ui/src/main/java/org/apache/hop/ui/core/gui/GuiResource.java`
- `ui/src/main/java/org/apache/hop/ui/core/PropsUi.java`
- `engine/src/main/java/org/apache/hop/core/gui/CanvasColorPalette.java`
- `ui/src/main/java/org/apache/hop/ui/core/gui/GuiToolbarWidgets.java`
- `ui/src/main/java/org/apache/hop/ui/hopgui/HopGui.java`

The first three are modified in Phase 1. Toolbar and perspective/sidebar work is intentionally deferred until the common visual tokens exist.
