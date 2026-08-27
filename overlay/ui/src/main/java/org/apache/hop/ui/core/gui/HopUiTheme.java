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

  private static RGB rgb(int red, int green, int blue) {
    return new RGB(red, green, blue);
  }
}
