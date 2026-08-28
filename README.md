# hop-ui-patch

Experimental UI modernization patch set for Apache Hop Desktop (SWT).

The project deliberately avoids a Hop fork. It keeps the changes small, reviewable and upstream-friendly: central design tokens, palette/canvas cleanup, navigation refinement, flatter native toolbars, calmer shared data grids and clearer canvas interaction feedback.

## Implemented phases

### Phase 1 — application shell

- a central `HopUiTheme` with light/dark design tokens;
- calmer application and canvas surfaces;
- less visual weight in tabs;
- slightly tighter default spacing;
- matching desktop/Web canvas colors;
- a compact 40px perspective rail;
- unified 20px sidebar icons and 36px hit targets;
- neutral hover/selection surfaces instead of rounded button cards;
- a slim active indicator shared by perspective and bottom sidebar actions on desktop SWT;
- native `SWT.FLAT` main and status toolbars;
- 16px toolbar icons kept intentionally for legibility;
- toolbar groups separated by whitespace instead of classic SWT/RAP groove lines;
- shared toolbar spacing tokens for desktop and Web/RAP paths.

### Phase 3 — tables and preview grids

- shared `TableView` remains a native SWT `Table`;
- full cell grid lines are hidden for a quieter IDE-style grid;
- Windows/Linux headers use the quiet panel surface while macOS keeps native foreground handling;
- the shared table toolbar uses `SWT.FLAT` and Phase 1C whitespace grouping;
- a small semantic gap separates toolbar commands from table data;
- the row-number column is widened slightly for better HiDPI legibility;
- preview/show-rows and many transform configuration grids inherit the change automatically through `TableView`.

See `docs/phase3-tables.md`.

### Phase 4 — canvas interaction feedback

- selected pipeline transforms and workflow actions get a restrained halo outside their existing status border;
- transform/action name hover is consistent on Desktop and Hop Web: subtle surface plus bold graph font;
- the old desktop-only hover underline is removed;
- lasso selection uses a low-alpha fill and dashed Hop accent border instead of an outline-only DASHDOT rectangle;
- context actions, shortcuts, drag/drop, hop creation, hit testing and selection rules are unchanged;
- engine painters stay independent from the SWT/UI theme module by using the existing `IGc.EColor` palette.

See `docs/phase4-canvas.md`.

No transform business logic is changed.

## Upstream

The patch targets **Apache Hop 2.19.0** and is pinned to the release source commit:

`46436154ae1a1e940861d485559819360c2af86e`

See `UPSTREAM.md`.

## Apply

Phase 1 only:

```bash
bash scripts/apply-phase1.sh /path/to/apache-hop
```

Through Phase 3:

```bash
bash scripts/apply-phase3.sh /path/to/apache-hop
```

Current UI patch through Phase 4:

```bash
bash scripts/apply-phase4.sh /path/to/apache-hop
```

The manager is idempotent. It detects phases independently, skips phases that are already present and applies only the missing phases. This supports upgrading older checkouts, for example from Phase 1 or Phase 3 directly to Phase 4.

The manager is deliberately conservative. It refuses:

- a Hop checkout that is not the pinned 2.19.0 source revision;
- partially applied/inconsistent phase markers;
- unknown local changes outside the managed patch files;
- changes to managed files after their state was recorded.

The recorded state and SHA-256 hashes live inside the target Hop checkout's Git metadata (`.git/hop-ui-patch-state.json`), so no bookkeeping file is added to the Hop working tree. Older state files that predate later phases are migrated by treating unknown later phases as not-yet-applied, while still verifying all hashes that were recorded previously.

## Status

```bash
bash scripts/status.sh /path/to/apache-hop
```

Example:

```text
Apache Hop: 2.19.0
UI patch:
  1A Foundations        ✓ applied
  1B Perspective rail   ✓ applied
  1C Toolbar            ✓ applied
   3 Tables & preview   ✓ applied
   4 Canvas interaction · missing
```

## Build

After applying, build Hop normally. A focused check is:

```bash
cd /path/to/apache-hop
./mvnw -pl ui,engine -am -DskipTests package
```

`package` is intentional here: `hop-engine` has a test-scope dependency on the `hop-core` tests JAR, which is attached during Maven's package phase and is therefore not available when the reactor is stopped at `compile`.

## Design direction

See `docs/design.md`. The goal is not a web-style skin or custom SWT widget framework. The target is a cleaner native desktop IDE: quieter surfaces, clearer hierarchy, fewer borders, consistent spacing and restrained use of accent colors.

The next larger GUI phase should be shared dialog/form infrastructure rather than more one-off visual patches.
