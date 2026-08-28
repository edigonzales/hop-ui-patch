/*
 * Experimental UI modernization for Apache Hop.
 *
 * Keep this class dependency-light: it is a collection of semantic SWT color and spacing tokens,
 * not a widget framework. The intent is to remove repeated magic numbers from the UI while keeping
 * native SWT controls and platform behavior intact.
 */
package org.apache.hop.ui.core.gui;

import org.eclipse.swt.graphics.RGB;

public final class HopUiTheme {

  private HopUiTheme() {}

  // Spacing is intentionally modest. Hop has many dense configuration dialogs and a large global
  // spacing jump would make them unnecessarily tall.
  public static final int SPACING_SMALL = 4;
  public static final int SPACING_MEDIUM = 6;
  public static final int SPACING_LARGE = 12;

  public static final int TAB_HEIGHT = 26;

  // Perspective rail. Keep it compact, but leave enough breathing room around 20px icons.
  public static final int SIDEBAR_WIDTH = 40;
  public static final int SIDEBAR_BUTTON_SIZE = 36;
  public static final int SIDEBAR_ICON_SIZE = 20;
  public static final int SIDEBAR_INDICATOR_WIDTH = 3;
  public static final int SIDEBAR_INDICATOR_INSET = 8;

  // Toolbars. Keep Hop's existing 16px icon size: the modernization comes from flatter native
  // chrome and whitespace-based grouping, not from making already-small icons harder to hit.
  public static final int TOOLBAR_ICON_SIZE = 16;
  public static final int TOOLBAR_GROUP_GAP = 10;
  public static final int TOOLBAR_ITEM_PADDING = 2;
  public static final int TOOLBAR_CONTROL_GAP = 3;

  // Shared dialogs and form rows. These values deliberately stay compact because many Hop dialogs
  // contain long technical forms. The goal is clearer grouping, not web-style oversized controls.
  public static final int DIALOG_MARGIN = 16;
  public static final int DIALOG_ELEMENT_GAP = 8;
  public static final int FORM_LABEL_GAP = 8;

  public static RGB applicationBackground(boolean darkMode) {
    return darkMode ? rgb(35, 35, 35) : rgb(255, 255, 255);
  }

  public static RGB panelBackground(boolean darkMode) {
    return darkMode ? rgb(40, 40, 40) : rgb(247, 247, 248);
  }

  public static RGB canvasBackground(boolean darkMode) {
    return darkMode ? rgb(32, 32, 32) : rgb(250, 250, 250);
  }

  public static RGB separator(boolean darkMode) {
    return darkMode ? rgb(62, 62, 62) : rgb(229, 231, 235);
  }

  public static RGB textPrimary(boolean darkMode) {
    return darkMode ? rgb(235, 235, 235) : rgb(32, 33, 36);
  }

  public static RGB textSecondary(boolean darkMode) {
    return darkMode ? rgb(170, 170, 170) : rgb(107, 114, 128);
  }

  public static RGB sidebarBackground(boolean darkMode) {
    return panelBackground(darkMode);
  }

  public static RGB sidebarHover(boolean darkMode) {
    return darkMode ? rgb(51, 51, 53) : rgb(238, 239, 241);
  }

  public static RGB sidebarSelection(boolean darkMode) {
    return darkMode ? rgb(59, 61, 64) : rgb(231, 234, 237);
  }

  public static RGB sidebarIndicator(boolean darkMode) {
    // A restrained cool accent that already fits Hop's existing blue-gray UI vocabulary.
    return darkMode ? rgb(126, 159, 182) : rgb(61, 99, 128);
  }

  public static RGB toolbarBackground(boolean darkMode) {
    return panelBackground(darkMode);
  }

  private static RGB rgb(int red, int green, int blue) {
    return new RGB(red, green, blue);
  }
}
