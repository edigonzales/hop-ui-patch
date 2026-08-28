# Phase 4 — Canvas interaction feedback

## Goal

Make pipeline and workflow canvases feel clearer and more contemporary while preserving Apache Hop's existing interaction model.

Phase 4 deliberately changes **feedback**, not semantics. Context actions, mouse gestures, keyboard shortcuts, hop creation, drag/drop and selection rules remain unchanged.

## Architecture

Pipeline and workflow drawing happens in the `engine` module through `BasePainter`, `PipelinePainter` and `WorkflowPainter`. This phase therefore does **not** import the SWT/UI `HopUiTheme` into the engine.

Instead it uses the existing `IGc.EColor` semantic palette. Desktop `SwtGc` and Web/SVG rendering already map those colors to the active Hop palette, retaining the engine/UI dependency boundary.

## Implemented changes

### 4A. Selected-node halo

Selected transforms and workflow actions get a restrained halo outside the existing icon/status border:

- translucent `LIGHTBLUE` surface;
- thin `HOP_DEFAULT` outline;
- existing red/deprecated/status border remains intact;
- existing selection mechanics and hit areas are unchanged.

This separates "selected" from "error/deprecated/status" instead of making one border carry several meanings.

### 4B. Consistent name hover

Transform/action names now use the same hover treatment on Desktop and Hop Web:

- subtle neutral hover surface behind the name;
- bold graph font while hovered;
- remove the desktop-only underline convention.

Single-click mode's existing always-visible edit/name surface is kept; the new hover surface is not layered on top of it.

### 4C. Lasso selection

The selection rectangle becomes a modern selection surface:

- low-alpha `LIGHTBLUE` fill;
- dashed `HOP_DEFAULT` border;
- negative-width/height selection handling remains unchanged.

## Non-goals

Phase 4 intentionally does **not**:

- replace Hop's context dialog/menu model;
- add inline action buttons over nodes;
- alter double-click or single-click behavior;
- change drag thresholds or drag/drop behavior;
- change hop creation shortcuts;
- change canvas hit testing;
- add an engine dependency on the UI module.

Those are larger interaction-design decisions and should be evaluated separately after the low-risk visual feedback changes have been used in practice.

## Files touched in the Apache Hop checkout

- `engine/src/main/java/org/apache/hop/core/gui/BasePainter.java`
- `engine/src/main/java/org/apache/hop/pipeline/PipelinePainter.java`
- `engine/src/main/java/org/apache/hop/workflow/WorkflowPainter.java`

The shared helpers in `BasePainter` intentionally keep pipeline and workflow behavior visually aligned.
