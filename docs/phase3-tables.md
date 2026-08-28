# Phase 3 — Tables and preview grids

## Goal

Make Apache Hop's dense data grids feel calmer and more IDE-like without replacing SWT `Table`, changing editing semantics, or touching individual transform dialogs.

The central leverage point is `org.apache.hop.ui.core.widget.TableView`. Preview dialogs such as `PreviewRowsDialog` and `ShowRowsDialog` already build on `TableView`, so one conservative change propagates to a large part of Hop's daily UI.

## Implemented changes

### 3A. Quieter grid

- keep the native SWT `Table`;
- hide full cell grid lines (`setLinesVisible(false)`);
- keep selection, keyboard navigation, sorting, resizing and inline editing native;
- keep macOS header foreground handling native;
- use Hop's quiet panel surface for headers on Windows/Linux.

The goal is visual grouping by alignment and whitespace rather than a spreadsheet-like box around every cell.

### 3B. Table toolbar

- create the `TableView` toolbar with `SWT.FLAT`;
- reuse Phase 1C's whitespace toolbar grouping automatically through `GuiToolbarWidgets`;
- use the same quiet panel surface as the table header;
- add a small semantic gap between toolbar and data grid.

### 3C. Row-number column

The index column grows from 25 to 32 logical pixels. This is still compact but avoids cramped multi-digit row numbers, especially under HiDPI scaling.

## Scope reached automatically

Because they use `TableView`, these areas benefit without dialog-specific patches:

- transform/action configuration tables;
- preview rows;
- show-rows/result grids;
- parameter and field tables;
- metadata and mapping tables that use the shared widget.

## Non-goals

Phase 3 intentionally does **not**:

- owner-draw table cells or headers;
- add alternating row colors;
- change row height through `SWT.MeasureItem`;
- change sorting, clipboard, inline editor or validation behavior;
- remove caller-requested `SWT.BORDER` styles;
- patch individual preview dialogs.

Those choices keep native accessibility and platform behavior intact and make the patch suitable for upstreaming.

## Validation

The applicator is structural and pinned to Apache Hop 2.19.0. The patch manager recognises Phase 3 independently and can upgrade a checkout that already has Phase 1A–1C.
