# hop-ui-patch

Experimental UI modernization for Apache Hop Desktop (SWT), targeting **Apache Hop 2.19.0**.

The project deliberately avoids a permanent Hop fork. The repository contains a complete source-file overlay representing the current desired UI state. Applying the patch means copying those files over a pinned Apache Hop checkout.

## Current UI improvements

The phase names remain useful as design history, but they are no longer installation units.

- **Phase 1A — foundations:** central `HopUiTheme`, calmer application/canvas surfaces, lighter tabs and tighter spacing.
- **Phase 1B — perspective rail:** compact 40px rail, consistent icons/hit targets, restrained hover/selection and active indicator.
- **Phase 1C — toolbar:** native `SWT.FLAT` toolbars, whitespace grouping and shared toolbar sizing tokens.
- **Phase 2 — dialogs/forms:** shared dialog margins and consistent label/control spacing.
- **Phase 3 — tables:** quieter `TableView`, full-row selection and clearer row-number column.
- **Phase 4 — canvas feedback:** selection halo, consistent name hover and quieter lasso feedback.
- **Phase 5A — combo controls:** compact `CCombo` popups and flatter shared combo wrappers.

See the files in `docs/` for the design decisions and phase-specific scope.

## Delivery model: full-file overlay

`overlay/` is the authoritative current patch. It mirrors paths from the Apache Hop repository and contains the **complete patched Java source files**, not fragments or replacement instructions.

Example:

```text
overlay/
├── engine/src/main/java/org/apache/hop/...
└── ui/src/main/java/org/apache/hop/...
```

There is no patch state database, no per-phase migration engine and no stored file-hash history. Git records the evolution of the overlay itself.

## Upstream baseline

The overlay targets Apache Hop 2.19.0 at exactly:

```text
46436154ae1a1e940861d485559819360c2af86e
```

The installer refuses another Hop revision. See `UPSTREAM.md`.

## Apply

```bash
bash scripts/apply-ui-patch.sh /path/to/apache-hop
```

The installer does the following:

1. verifies the pinned Apache Hop commit;
2. compares every file in `overlay/` with the target checkout;
3. exits without changing anything when the overlay is already installed;
4. if files differ and the Hop working tree contains changes, runs `git stash push -u` first;
5. copies the complete overlay into the Hop checkout;
6. runs `git diff --check` and verifies every copied file byte-for-byte.

An old `.git/hop-ui-patch-state.json` from previous versions is removed automatically because it is no longer used.

### Existing local changes

Before copying, an existing dirty Hop working tree is saved as a stash such as:

```text
stash@{0}: On (no branch): hop-ui-patch backup 2026-08-28 17:45:00
```

The stash is **not** popped automatically. This is intentional: an old UI patch stored in that stash could otherwise overwrite the newly installed overlay.

Inspect backups with:

```bash
git -C /path/to/apache-hop stash list
git -C /path/to/apache-hop stash show -p stash@{0}
```

Only reapply a stash manually when you actually want its changes back.

## Status

```bash
bash scripts/status.sh /path/to/apache-hop
```

Example after installation:

```text
Apache Hop: 2.19.0
Baseline:   46436154ae1a1e940861d485559819360c2af86e
Overlay:    16 / 16 files match
Status:     up to date
```

If a file differs, `status.sh` lists the exact path. There is no historical state to migrate.

## Build

A focused validation build is:

```bash
cd /path/to/apache-hop
./mvnw -pl ui,engine -am -DskipTests package
```

`package` is intentional: `hop-engine` has a test-scope dependency on the `hop-core` tests JAR, which is attached during Maven's package phase.

## Source builds for A/B testing

The patch is validated by building two Hop clients from source and comparing them
side by side:

| Directory | Source | Purpose |
|---|---|---|
| `hop-main` | apache/hop `main` | current upstream state |
| `hop-2.19.0` | pinned 2.19.0 commit + overlay | the patched variant |

### One-time setup

```bash
# full clone of apache/hop + a worktree at the pinned 2.19.0 commit + overlay applied
bash scripts/setup-checkouts.sh ~/sources/hop-ab
```

Creates `~/sources/hop-ab/hop-main` and `~/sources/hop-ab/hop-2.19.0` (shared git object
store, ~1 GB once). The overlay installer verifies the pinned commit — no other Hop revision
is accepted.

### Build both clients

```bash
bash scripts/build-ab-dist.sh \
  ~/sources/hop-ab/hop-main \
  ~/sources/hop-ab/hop-2.19.0 \
  ~/sources/hop-ab/dist
```

Each build runs `./mvnw -DskipTests clean package` in the checkout (full reactor including
all plugins) and unpacks the official `assemblies/client/target/hop-client-*.zip` into
`dist/hop-main/` and `dist/hop-2.19.0-patched/`. The results are **unzipped** so individual
JARs stay replaceable.

```bash
~/sources/hop-ab/dist/hop-main/hop-gui.sh                # current main
~/sources/hop-ab/dist/hop-2.19.0-patched/hop-gui.sh      # 2.19.0 + overlay
```

Requirements: `git`, a JDK **21–24** (`JAVA_HOME`; an sdkman Java 21 is auto-detected —
Java 25+ does not work because Lombok 1.18.x does not run on it), ~10 GB disk.
First build per checkout takes ~20–40 min (cold Maven cache), afterwards ~5–15 min.

### Iterating on the patch

1. Edit files in `overlay/`.
2. `bash scripts/apply-ui-patch.sh ~/sources/hop-ab/hop-2.19.0` — idempotent, only
   changed files are copied.
3. `bash scripts/build-client.sh ~/sources/hop-ab/hop-2.19.0 ~/sources/hop-ab/dist/hop-2.19.0-patched`
   — incremental build, a few minutes (only `ui`/`engine` sources changed).

## Developing further UI changes

For new phases, modify the desired Apache Hop source files in `overlay/` directly (or regenerate them from a clean pinned Hop checkout), then run the normal CI build. No new phase applicator, marker set or state migration is required.

The design target remains a cleaner native desktop IDE rather than a web-style skin or a replacement SWT widget framework: quieter surfaces, clearer hierarchy, fewer borders, consistent spacing and restrained accent usage.
