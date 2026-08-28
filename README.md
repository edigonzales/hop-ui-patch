# hop-ui-patch

Experimental UI modernization patch set for Apache Hop Desktop (SWT).

The project deliberately avoids a Hop fork. It keeps the changes small, reviewable and upstream-friendly: central design tokens, palette/canvas cleanup, navigation refinement, flatter native toolbars, shared dialog/form styling, quieter shared tables and clearer canvas interaction feedback.

## Implemented phases

### Phase 1 — application shell

- central `HopUiTheme` with light/dark design tokens;
- calmer application and canvas surfaces;
- less visual weight in tabs;
- slightly tighter default spacing;
- matching desktop/Web canvas colors;
- compact 40px perspective rail;
- unified 20px sidebar icons and 36px hit targets;
- neutral hover/selection surfaces instead of rounded button cards;
- slim active indicator shared by perspective and bottom sidebar actions on desktop SWT;
- native `SWT.FLAT` main and status toolbars;
- 16px toolbar icons kept intentionally for legibility;
- toolbar groups separated by whitespace instead of classic SWT/RAP groove lines.

### Phase 2 — shared dialogs and forms

- semantic dialog margin, element-gap and label-gap tokens;
- `BaseDialog` spacing uses the central theme instead of local magic numbers;
- `LabelText`, `LabelTextVar`, `LabelCombo` and `LabelComboVar` share one label-to-control gap;
- the shared form composites keep native SWT controls and explicitly inherit Hop look/background handling;
- no individual transform/action dialog logic is changed.

### Phase 3 — tables and preview grids

- shared `TableView` uses semantic table tokens;
- permanent cell grid lines are disabled to reduce spreadsheet-like visual noise;
- native `SWT.FULL_SELECTION` makes the existing row selection clear across the whole table width;
- the row-number/index column is widened from 25px to 30px for clearer row scanning;
- native SWT table headers, sorting and scrollbars are retained;
- existing inline editors, row colors, keyboard shortcuts, clipboard behavior and Hop Web fallbacks remain unchanged;
- the existing TableView toolbar continues to use Hop's central toolbar/action infrastructure.

See `docs/phase2-3-plan.md` for the Phase 2/3 scope and non-goals.

### Phase 4 — canvas interaction feedback

- selected pipeline transforms and workflow actions get a restrained halo outside the existing status border;
- transform/action name hover is consistent on Desktop and Hop Web: subtle surface plus bold graph font;
- the old desktop-only hover underline is removed;
- lasso selection uses a low-alpha fill and dashed Hop accent border instead of an outline-only DASHDOT rectangle;
- context actions, shortcuts, drag/drop, hop creation, hit testing and selection rules remain unchanged;
- engine painters stay independent from the SWT/UI theme module by using the existing `IGc.EColor` palette.

See `docs/phase4-canvas.md` for the Phase 4 design boundaries.

## Upstream

The patch targets **Apache Hop 2.19.0** and is pinned to the release source commit:

`46436154ae1a1e940861d485559819360c2af86e`

See `UPSTREAM.md`.

## Apply the current patch set

From a checkout of this repository:

```bash
bash scripts/apply-ui-patch.sh /path/to/apache-hop
```

The command is idempotent. It detects every managed phase independently, skips phases that are already present and applies only the missing phases. Existing Phase 1, Phase 2 or Phase 3 checkouts can therefore be upgraded directly to the latest patch set.

Example on a Phase 3 checkout:

```text
1A: already applied, skipping.
1B: already applied, skipping.
1C: already applied, skipping.
2: already applied, skipping.
3: already applied, skipping.
Applying 4...
```

The manager is deliberately conservative. It refuses:

- a Hop checkout that is not the pinned 2.19.0 source revision;
- partially applied/inconsistent phase markers;
- unknown local changes outside the managed patch files;
- changes to managed files after their state was recorded.

The recorded state and SHA-256 hashes live inside the target Hop checkout's Git metadata (`.git/hop-ui-patch-state.json`), so no bookkeeping file is added to the Hop working tree. Older state files are migrated only after their recorded hashes and phase markers have been verified.

### Phase 1 compatibility command

The old command remains available and intentionally stops after Phase 1C:

```bash
bash scripts/apply-phase1.sh /path/to/apache-hop
```

## Status

```bash
bash scripts/status.sh /path/to/apache-hop
```

Example:

```text
Apache Hop: 2.19.0
UI patch:
  1A Foundations          ✓ applied
  1B Perspective rail     ✓ applied
  1C Toolbar              ✓ applied
   2 Shared dialogs/forms ✓ applied
   3 Tables/preview grids ✓ applied
   4 Canvas interaction   · missing
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

Phase 4 deliberately stops at visual interaction feedback. Changes to context actions, canvas gestures or other interaction semantics should remain separate and be evaluated only after the visual patch has been tested in daily use.
