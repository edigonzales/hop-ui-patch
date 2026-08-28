# Phase 2 and Phase 3 plan

The next UI work deliberately moves from the outer Hop shell into shared controls that affect day-to-day configuration work.

## Phase 2 — Shared dialog and form foundations

Goal: make common configuration dialogs calmer and more consistent without rewriting individual transform/action dialogs or replacing native SWT controls.

Scope:

- central dialog/form spacing tokens in `HopUiTheme`;
- `BaseDialog` uses semantic dialog margin, element gap and label gap tokens instead of local magic numbers;
- shared `LabelText`, `LabelTextVar`, `LabelCombo` and `LabelComboVar` rows use one semantic label-to-control gap;
- shared form composites explicitly inherit Hop look/background handling;
- patch manager is generalized beyond “Phase 1” while keeping the existing Phase 1 commands compatible;
- state-file migration remains safe for checkouts already managed by the Phase 1 patch manager.

Non-goals:

- no individual plugin dialog rewrites;
- no custom-drawn text/combo/button controls;
- no forced font replacement;
- no change to field semantics, tab order or validation.

## Phase 3 — Tables and preview grids

Goal: reduce the visual density of the table surfaces used throughout Hop while retaining native SWT table behavior and all editing/selection semantics.

Scope:

- central table tokens in `HopUiTheme`;
- `TableView` removes always-on cell grid lines in favor of row/column structure from spacing and native selection;
- slightly wider row-number/index column for readability;
- table toolbar remains native and keeps all existing actions/shortcuts;
- existing sort indicators, inline editors, row colors, clipboard behavior and Hop Web fallbacks remain unchanged;
- Phase 3 is independently detectable/idempotent in the patch manager.

Non-goals:

- no owner-drawn replacement table;
- no per-plugin table changes;
- no virtualization/data-model changes;
- no redesign of Preview/Execution data semantics.

## Delivery

Phase 2 and Phase 3 are kept as separate reviewable changes. Phase 3 depends on Phase 2 because both extend the same semantic theme and patch-manager state model.
