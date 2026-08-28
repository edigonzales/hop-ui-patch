# hop-ui-patch

Experimental UI modernization patch set for Apache Hop Desktop (SWT).

The project deliberately avoids a Hop fork. It keeps the changes small, reviewable and upstream-friendly: central design tokens, palette/canvas cleanup, navigation refinement and a flatter native toolbar.

## Phase 1

The implementation currently covers the visual foundations, perspective rail and main/status toolbars:

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

The command is idempotent. It detects Phase 1A, 1B and 1C independently, skips phases that are already present and applies only the missing phases. This also supports upgrading an older checkout where, for example, only Phase 1A was applied.

Example on a partially patched checkout:

```text
1A: already applied, skipping.
Applying 1B...
Applying 1C...
```

The manager is deliberately conservative. It refuses:

- a Hop checkout that is not the pinned 2.19.0 source revision;
- partially applied/inconsistent phase markers;
- unknown local changes outside the managed patch files;
- changes to managed files after their state was recorded.

The recorded state and SHA-256 hashes live inside the target Hop checkout's Git metadata (`.git/hop-ui-patch-state.json`), so no bookkeeping file is added to the Hop working tree. Existing Phase 1 checkouts created before the state manager are adopted once from structural phase markers; subsequent runs are hash-verified.

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
  1C Toolbar            · missing
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

Next: Phase 2 should move into shared dialogs/widgets, starting with reusable table/form infrastructure rather than individual transform dialogs.
