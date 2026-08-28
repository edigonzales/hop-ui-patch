# Overlay installation model

## Why this replaced the patch manager

Early versions of `hop-ui-patch` applied each visual phase through source-fragment replacement scripts and recorded phase markers plus SHA-256 hashes in `.git/hop-ui-patch-state.json`.

That became more complex than the UI patch itself. Small legitimate cleanups of already-managed files required legacy hash migrations, and an existing checkout could fail one managed file at a time even though the desired end state was well known.

The project now uses a simpler model: **the complete files in `overlay/` are the desired end state**.

## Installation semantics

`apply-ui-patch.sh` first verifies the exact Apache Hop 2.19.0 baseline. It then compares the overlay with the target checkout.

If every overlay file already matches, installation is a no-op.

If at least one file differs:

1. a dirty Hop working tree is saved with `git stash push -u`;
2. the overlay is copied over the clean pinned baseline;
3. `git diff --check` validates whitespace/conflict problems;
4. every overlay file is compared byte-for-byte with the installed copy.

The stash is a safety backup and is never restored automatically.

## Why full files are acceptable here

A full-file overlay would be risky against a moving upstream branch because it could overwrite unrelated upstream edits. This repository avoids that problem by refusing any Apache Hop commit except the pinned 2.19.0 source revision.

When the upstream baseline changes, the overlay must be regenerated/reviewed as a whole.

## Phase history

Phase names remain useful for design documentation and Git history, but the installed product is always one current overlay. There is intentionally no supported combination such as "Phase 1B + Phase 3 but without Phase 2".

Future visual work therefore changes the overlay and documentation; it does not add a new state schema or migration step.
