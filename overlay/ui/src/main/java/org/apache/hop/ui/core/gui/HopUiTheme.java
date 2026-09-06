/*
 * Experimental UI modernization for Apache Hop (v2).
 *
 * Keep this class dependency-light: it is a collection of semantic SWT color and spacing tokens,
 * not a widget framework. The intent is to remove repeated magic numbers from the UI while keeping
 * native SWT controls and platform behavior intact.
 *
 * v2 palette: white / eggshell surfaces instead of gray, Hop brand blue (#0A4A6B, derived from
 * the logo color #033d5d) as accent, more generous spacing and larger icons.
 */
package org.apache.hop.ui.core.gui;

import org.eclipse.swt.graphics.RGB;

public final class HopUiTheme {

  private HopUiTheme() {}

  // Spacing: v2 deliberately adds air around the elements.
  public static final int SPACING_SMALL = 6;
  public static final int SPACING_MEDIUM = 8;
  public static final int SPACING_LARGE = 16;

  public static final int TAB_HEIGHT = 30;

  // SWT tables have no cell padding; the row height follows the font. One point of extra
  // base font height is the single global lever for more vertical air in tables, buttons,
  // combos and tabs. Applied centrally in GuiResource.loadFonts().
  public static final int BASE_FONT_DELTA = 1;

  // Perspective rail: compact but roomier than the classic 34px rail.
  public static final int SIDEBAR_WIDTH = 48;
  public static final int SIDEBAR_BUTTON_SIZE = 44;
  public static final int SIDEBAR_ICON_SIZE = 24;
  public static final int SIDEBAR_INDICATOR_WIDTH = 3;
  public static final int SIDEBAR_INDICATOR_INSET = 10;

  // Toolbars: bigger icons, whitespace-based grouping.
  public static final int TOOLBAR_ICON_SIZE = 20;
  public static final int TOOLBAR_GROUP_GAP = 16;
  public static final int TOOLBAR_ITEM_PADDING = 4;
  public static final int TOOLBAR_CONTROL_GAP = 6;

  // Shared dialogs and form rows.
  public static final int DIALOG_MARGIN = 20;
  public static final int DIALOG_ELEMENT_GAP = 12;
  public static final int FORM_LABEL_GAP = 10;

  // Shared tables and preview grids.
  public static final boolean TABLE_GRID_LINES_VISIBLE = false;
  public static final int TABLE_INDEX_COLUMN_WIDTH = 36;

  // CCombo popups can otherwise grow to almost the full screen for large technical value sets
  // such as Java character encodings.
  public static final int COMBO_VISIBLE_ITEM_COUNT = 10;

  public static RGB applicationBackground(boolean darkMode) {
    return darkMode ? rgb(30, 28, 25) : rgb(255, 255, 255);
  }

  public static RGB panelBackground(boolean darkMode) {
    return darkMode ? rgb(38, 36, 33) : rgb(250, 249, 245);
  }

  public static RGB canvasBackground(boolean darkMode) {
    return darkMode ? rgb(35, 33, 30) : rgb(255, 255, 255);
  }

  public static RGB separator(boolean darkMode) {
    return darkMode ? rgb(56, 52, 46) : rgb(232, 228, 218);
  }

  public static RGB textPrimary(boolean darkMode) {
    return darkMode ? rgb(236, 232, 225) : rgb(33, 37, 41);
  }

  public static RGB textSecondary(boolean darkMode) {
    return darkMode ? rgb(168, 162, 154) : rgb(108, 117, 125);
  }

  public static RGB accent(boolean darkMode) {
    return darkMode ? rgb(127, 178, 217) : rgb(10, 74, 107);
  }

  public static RGB sidebarBackground(boolean darkMode) {
    return panelBackground(darkMode);
  }

  public static RGB sidebarHover(boolean darkMode) {
    return darkMode ? rgb(47, 44, 40) : rgb(241, 238, 231);
  }

  public static RGB sidebarSelection(boolean darkMode) {
    return darkMode ? rgb(58, 54, 47) : rgb(233, 229, 220);
  }

  public static RGB sidebarIndicator(boolean darkMode) {
    return accent(darkMode);
  }

  public static RGB toolbarBackground(boolean darkMode) {
    return panelBackground(darkMode);
  }

  private static RGB rgb(int red, int green, int blue) {
    return new RGB(red, green, blue);
  }
}
