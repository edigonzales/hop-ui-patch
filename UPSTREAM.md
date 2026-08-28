# Upstream baseline

The UI overlay is developed against Apache Hop `2.19.0` at:

- repository: `apache/hop`
- release source tag: `2.19.0-rc1`
- commit: `46436154ae1a1e940861d485559819360c2af86e`
- release branch: `release/2.19.0`

The root Maven project at this commit has version `2.19.0`.

The exact commit pin is intentional. `overlay/` contains complete source-file snapshots, so applying those files to another Hop revision could silently discard upstream changes in the same classes. The installer therefore refuses any other `HEAD`.

## Rebasing to another Hop revision

Do not simply relax the commit check. Instead:

1. check out the new Apache Hop baseline;
2. reapply the intended UI changes to that baseline;
3. regenerate/update the complete files in `overlay/`;
4. update the pinned commit in the scripts and this document;
5. run the full Java 21 Maven validation build.

Important upstream files currently represented in the overlay include the central palette/theme hooks, `PropsUi`, `HopGui`, shared toolbar/dialog/widget classes, `TableView` and the pipeline/workflow painters. The overlay directory itself is the definitive file list.
