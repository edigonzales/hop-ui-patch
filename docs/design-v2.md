# Hop UI v2 — design notes

v2 supersedes the earlier design.md approach. The v1 goal ("quieter gray surfaces") produced
too little visible difference and kept the parts users disliked most: gray-on-gray surfaces,
monochrome dark-blue icons, tight spacing, small icons. v2 inverts the priorities.

## Goals

1. **Light, not gray:** white and eggshell-white surfaces; gray remains only for secondary
   text and separators.
2. **Color comes from the icons:** full-color, recognizable icons (classic Kettle look as
   the visual reference) are the primary orientation — not tinted surfaces.
3. **More air:** generous spacing in dialogs, forms and around icons.
4. **Bigger icons** everywhere: toolbar/menu 20, sidebar rail 24 (rail 48 wide),
   canvas 40.
5. **No fork, no plugin patches:** a central override hook in `GuiResource` restyles plugin
   icons without touching a single plugin jar.
6. Native SWT controls stay; no owner-drawn replacements.

## Palette — light

| Role | Value |
|---|---|
| Application background | `#FFFFFF` |
| Panel / sidebar / toolbar | `#FAF9F5` (eggshell) |
| Canvas | `#FFFFFF` |
| Hover surface | `#F1EEE7` |
| Selection surface (rail) | `#E9E5DC` |
| Separator | `#E8E4DA` |
| Text primary / secondary | `#212529` / `#6C757D` |
| Accent (indicator, focus) | `#0A4A6B` (Hop brand blue, derived from logo `#033d5d`) |

Dark mode mirrors the hierarchy with warm neutrals (`#1E1C19` app, `#262421` panels,
`#23211E` canvas, accent `#7FB2D9`) — implemented later (Phase N5).

## Sizes

| Where | Before | v2 |
|---|---|---|
| Toolbar + menu icons (ConstUi.SMALL_ICON_SIZE) | 16 | **20** |
| Sidebar rail icons | 20 | **24** (rail 40 → **48**, hit targets 36 → **44**) |
| Canvas node icons (ConstUi.ICON_SIZE) | 32 | **40** |
| Medium icons (ConstUi.MEDIUM_ICON_SIZE) | 24 | **28** |
| Documentation icons | 14 | **16** |

## Spacing

| Token | Before | v2 |
|---|---|---|
| Dialog margin | 15/16 | **20** |
| Element gap in dialogs | 8/10 | **12** |
| Label ↔ control gap | 5/8 | **10** |
| Base spacing small / medium | 4 / 6 | 6 / 8 |
| Tab height | 26/28 | **30** |
| Toolbar group gap | 10 | **16** |
| Toolbar item padding | 2 | 4 |
| Table index column | 25/30 | **36** |
| Base font delta | — | **+1 pt** (`HopUiTheme.BASE_FONT_DELTA`) |

SWT tables have no cell padding; row height follows the font, so the +1 pt base font
(applied centrally in `GuiResource.loadFonts()`) is the single global lever for vertical air.

## Icon strategy

- **Central override hook:** `GuiResource.loadPluginUniversalImage()` checks
  `ui/images/overrides/<transforms|actions|plugins>/<pluginId>.svg` before falling back to
  the plugin's own image. Same mechanism in `loadPluginImage()` for database/value-meta icons.
- **Style guide for new icons:** 24×24 viewBox, full color with 1–2 shading steps, flat
  with subtle highlights, no outlines, 2 px safe margin, consistent stroke weight, no text
  (except well-known abbreviations such as "CSV"). The classic Kettle icon set
  (`pentaho-kettle`, Apache-2.0) is the visual reference for shapes and colors — not copied
  as files.
- **Batches:** core UI + perspective icons first (N2a), then transforms in batches of the
  most-used ones (N2b), then actions and databases (N2c). Progress lives in
  `docs/icon-mapping.md`.

## Phases

- **N1 — palette, surfaces & spacing (this repo state):** HopUiTheme v2, ConstUi sizes,
  GuiResource colors + base font delta, PropsUi tabs, sidebar rail 48/44/24,
  toolbar gaps/padding, white canvas.
- **N2 — icons:** override hook (in place since N1) + icon batches (N2a core/perspectives,
  N2b transforms, N2c actions & databases).
- **N3 — padding rollout:** BaseDialog, Label* widgets, TableView on the v2 tokens;
  combo fixes (10-row popup, SWT.FLAT) migrate from v1.
- **N4 — canvas feedback:** selection halo and name hover from v1, adapted to the v2 colors.
- **N5 (later) — dark mode** with the warm palette.

## Non-goals

- pixel-identical VS Code/JetBrains imitation
- rounded web controls everywhere
- animations
- replacing SWT
- changing pipeline/workflow semantics
- recoloring plugin icons indiscriminately (the override hook is opt-in per icon)
