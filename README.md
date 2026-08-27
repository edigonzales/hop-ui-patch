# hop-ui-patch

Experimental UI modernization patch set for Apache Hop Desktop (SWT).

The project deliberately avoids a Hop fork. It keeps the changes small, reviewable and upstream-friendly: central design tokens, palette/canvas cleanup, then navigation and toolbar refinement.

## Phase 1

The first implementation changes only high-leverage UI infrastructure:

- a central `HopUiTheme` with light/dark design tokens;
- calmer application and canvas surfaces;
- less visual weight in tabs;
- slightly tighter default spacing;
- matching desktop/Web canvas colors.

No transform dialogs or business logic are changed.

## Upstream

The patch is currently pinned to Apache Hop commit:

`bab67a10d01b76e6f93f30dde735d50fc87c1b04`

See `UPSTREAM.md`.

## Apply

From a checkout of this repository:

```bash
./scripts/apply-phase1.sh /path/to/apache-hop
```

The script refuses to modify an unexpected Hop revision unless `HOP_UI_PATCH_ALLOW_DIRTY=1` is set.

After applying, build Hop normally. A focused first check is:

```bash
cd /path/to/apache-hop
./mvnw -pl ui,engine -am -DskipTests package
```

## Design direction

See `docs/design.md`. The goal is not a web-style skin or custom SWT widget framework. The target is a cleaner native desktop IDE: quieter surfaces, clearer hierarchy, fewer borders, consistent spacing and restrained use of Hop accent colors.
