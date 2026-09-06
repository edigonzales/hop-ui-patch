# Icon overrides (hop-ui-patch v2)

This folder is the central override mechanism for plugin icons. At startup
`GuiResource.loadPluginUniversalImage()` checks `ui/images/overrides/<category>/<pluginId>.svg`
first and falls back to the plugin's own image.

- `transforms/<pluginId>.svg` — transform icons (canvas, explorer, preview)
- `actions/<pluginId>.svg` — workflow action icons
- `plugins/<pluginId>.svg` — database and value-meta icons (small sizes)

Icons are drawn in the v2 style (see `docs/design-v2.md`): full color, 24×24
viewBox, flat with subtle shading, no outlines. The classic Kettle icon set
(pentaho-kettle, Apache-2.0) serves as the visual reference.

See `docs/icon-mapping.md` for the mapping table and progress.
