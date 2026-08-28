# Phase 5A — Combo/dropdown controls

## Goal

Reduce the most intrusive visual behavior of Apache Hop's SWT `CCombo` controls without changing their API or replacing them with a different widget type.

The motivating case is a long technical list such as **File encoding**. A `CCombo` with hundreds of Java character encodings can otherwise open a popup that occupies a large part of the screen.

## Implemented changes

### Compact popup height

`PropsUi.setLook(...)` now applies a shared visible-row limit to `CCombo` controls:

```java
combo.setVisibleItemCount(HopUiTheme.COMBO_VISIBLE_ITEM_COUNT);
```

The theme token is currently:

```java
public static final int COMBO_VISIBLE_ITEM_COUNT = 10;
```

Lists with fewer items stay naturally small. Longer lists show a scrollbar after ten visible rows; no items are removed or reordered.

### Flatter shared combo wrappers

SWT `CCombo` explicitly supports `SWT.FLAT`. Phase 5A enables it in Hop's two shared wrappers:

```java
new CCombo(this, textFlags | SWT.FLAT)
new CCombo(this, flags | SWT.FLAT)
```

This reduces the visual weight of the arrow/button chrome for `LabelCombo` and `ComboVar` without changing their public `CCombo` API.

### Shared look for `LabelCombo`

`LabelCombo` calls `PropsUi.setLook(this)` before its inner `CCombo` exists, so the normal recursive look pass cannot style that child. Phase 5A explicitly calls:

```java
PropsUi.setLook(wCombo);
```

immediately after creating the inner combo. `ComboVar` already applies the common look to its `CCombo`.

## Compatibility boundaries

Phase 5A intentionally keeps `org.eclipse.swt.custom.CCombo`.

It does **not** change:

- public methods returning `CCombo`;
- editable versus read-only behavior;
- item order or item contents;
- selection and modify listeners;
- keyboard navigation;
- variable completion in `ComboVar`;
- control hit testing;
- transform/action metadata semantics.

The central visible-row limit is applied after Hop's normal platform-specific look handling, so Windows/macOS/Linux and Hop Web retain their existing color/font paths. Eclipse RAP's `CCombo` also supports `setVisibleItemCount(int)`.

## Known limitation

Directly constructed `CCombo` controls keep their construction style; Phase 5A does not rewrite every plugin dialog to add `SWT.FLAT`. They still benefit from the central ten-row popup limit whenever Hop applies `PropsUi.setLook(...)`.

The distinctive `CCombo` arrow/button and border therefore remain partly custom rather than truly native on macOS. A full native look would require a later Phase 5B based on `org.eclipse.swt.widgets.Combo` and explicit compatibility work.

## Files patched in Apache Hop

- `ui/src/main/java/org/apache/hop/ui/core/PropsUi.java`
- `ui/src/main/java/org/apache/hop/ui/core/widget/LabelCombo.java`
- `ui/src/main/java/org/apache/hop/ui/core/widget/ComboVar.java`
- managed `HopUiTheme.java`
