# Modern Hop UI — design notes

## Goals

1. Reduce the visual weight of the SWT chrome without fighting SWT.
2. Improve hierarchy primarily through surfaces, spacing and typography rather than decoration.
3. Keep native platform behavior where SWT provides it.
4. Centralize new visual constants before touching more components.
5. Keep light and dark mode behavior explicit and testable.

## Phase 1 tokens

Light mode:

- application background: `#FFFFFF`
- secondary/panel surface: `#F7F7F8`
- canvas: `#FAFAFA`
- separator: `#E5E7EB`
- primary text: `#202124`
- secondary text: `#6B7280`
- selection/accent: retain Hop identity rather than inventing a new brand color

Dark mode mirrors the hierarchy instead of merely inverting RGB values.

## Perspective rail

The 2.19.0 desktop sidebar already uses an owner-drawn SWT `Canvas`, so it is a safe place to be more deliberate than with normal SWT controls. Phase 1B turns it into an IDE-style rail rather than a column of rounded buttons:

- 40 logical-pixel rail;
- 36 logical-pixel hit targets;
- 20 logical-pixel perspective/action icons;
- neutral panel background;
- subtle rectangular hover and selected surfaces;
- 3 logical-pixel active indicator on the left;
- one shared paint routine for perspective and bottom action buttons;
- matching semantic colors for RAP, while the active indicator itself is desktop-only for now.

The active state should read from peripheral vision without turning the whole navigation item into a colored card.

## SWT strategy

Do not introduce owner-drawn replacements for standard text fields, buttons, tables or scroll bars in the first phases. Those controls are expensive to maintain and tend to regress accessibility and platform behavior.

Prefer, in order:

1. existing Hop resource/palette abstractions;
2. existing `PropsUi.setLook(...)` hooks;
3. standard SWT control properties;
4. owner drawing only for controls Hop already draws itself (canvas, existing sidebar canvases, SVG-label navigation etc.).

## Phase sequence

### Phase 1A — foundations

- central theme/design tokens;
- application/panel/canvas surfaces;
- compact tab styling;
- slightly reduced generic spacing;
- desktop/Web canvas palette parity.

### Phase 1B — navigation

- compact perspective rail;
- consistent icon and hit-target sizing;
- borderless, non-rounded desktop buttons;
- active perspective/action indicator;
- shared renderer for top and bottom sidebar buttons;
- hover/selected states based on theme tokens.

### Phase 1C — toolbar

- reduce visual density;
- normalize small icon sizing;
- group actions with whitespace rather than heavy separators;
- flat hover/selected states.

### Phase 2 — shared dialogs/widgets

Only after the shell, navigation and canvas feel coherent: inspect `TableView`, common label/text composites and base dialogs. Avoid per-transform restyling unless a reusable abstraction can cover it.

## Non-goals

- pixel-identical VS Code/JetBrains imitation;
- rounded web controls everywhere;
- animations;
- replacing SWT;
- changing pipeline/workflow semantics;
- recoloring plugin icons indiscriminately.
