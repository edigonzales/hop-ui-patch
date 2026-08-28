# hop-ui-patch

Experimental UI modernization patch set for Apache Hop Desktop (SWT).

The project deliberately avoids a Hop fork. It keeps the changes small, reviewable and upstream-friendly: central design tokens, palette/canvas cleanup, then navigation and toolbar refinement.

## Phase 1

The implementation currently covers the visual foundations and the perspective rail:

- a central `HopUiTheme` with light/dark design tokens;
- calmer application and canvas surfaces;
- less visual weight in tabs;
- slightly tighter default spacing;
- matching desktop/Web canvas colors;
- a compact 40px perspective rail;
- unified 20px sidebar icons and 36px hit targets;
- neutral hover/selection surfaces instead of rounded button cards;
- a slim active indicator shared by perspective and bottom sidebar actions on desktop SWT.

No transform dialogs or business logic are changed.

## Upstream

The patch targets **Apache Hop 2.19.0** and is pinned to the release source commit:

`46436154ae1a1e940861d485559819360c2af86e`

See `UPSTREAM.md`.

## Apply

From a checkout of this repository:

```bash
bash scripts/apply-phase1.sh /path/to/apache-hop
```

The script refuses to modify an unexpected Hop revision unless `HOP_UI_PATCH_ALLOW_DIRTY=1` is set.

After applying, build Hop normally. A focused check is:

```bash
cd /path/to/apache-hop
./mvnw -pl ui,engine -am -DskipTests package
```

`package` is intentional here: `hop-engine` has a test-scope dependency on the `hop-core` tests JAR, which is attached during Maven's package phase and is therefore not available when the reactor is stopped at `compile`.

## Design direction

See `docs/design.md`. The goal is not a web-style skin or custom SWT widget framework. The target is a cleaner native desktop IDE: quieter surfaces, clearer hierarchy, fewer borders, consistent spacing and restrained use of accent colors.

Next: Phase 1C will refine the main toolbar while continuing to use standard SWT/Hop toolbar infrastructure.
