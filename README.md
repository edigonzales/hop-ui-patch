# hop-ui-patch

Experimental UI modernization for Apache Hop Desktop (SWT), targeting **Apache Hop 2.19.0**.

The project deliberately avoids a permanent Hop fork. The repository contains a complete source-file overlay representing the current desired UI state. Applying the patch means copying those files over a pinned Apache Hop checkout.

## Current UI state (v2)

The v1 phase history (gray-on-gray surfaces, monochrome icons) has been superseded.
v2 inverts the priorities — see `docs/design-v2.md` for the full design:

- **N1 — palette, surfaces & spacing:** white/eggshell surfaces instead of gray
  (`#FFFFFF` app, `#FAF9F5` panels, white canvas), Hop brand blue accent `#0A4A6B`,
  bigger spacing tokens, +1 pt base font, 30px tabs.
- **N1 — sizes:** toolbar/menu icons 16 → **20**, sidebar rail 40 → **48** (icons 24,
  hit targets 44), canvas icons 32 → **40**, medium 28.
- **N2 (in progress) — icons:** central override hook in `GuiResource`
  (`ui/images/overrides/<pluginId>.svg`, fallback to the plugin's own image) plus new
  full-color icons in the classic Kettle style; progress in `docs/icon-mapping.md`.

Planned: **N3** padding rollout to dialogs/widgets/tables, **N4** canvas feedback,
**N5** dark mode.

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

| Client | Source | Purpose |
|---|---|---|
| `hop-main` | apache/hop `main` (= latest `2.20.0-SNAPSHOT`) | current upstream state |
| `hop-2.19.0-patched` | pinned 2.19.0 commit + overlay | the patched variant |

Everything lives under one base directory — here `~/sources/hop-ab` ("hop" + "A/B";
any name works, the scripts take the paths as arguments):

```text
~/sources/hop-ab/
├── hop-main/                  apache/hop clone on main, used as checkout AND as
│                              the shared git object store for the worktree below
├── hop-2.19.0/                git worktree at the pinned 2.19.0 commit
│                              (46436154…), with the overlay applied on top
└── dist/                      built clients (unzipped, ready to run)
    ├── hop-main/              ← ./hop-gui.sh, ./hop-run.sh, lib/core/…
    └── hop-2.19.0-patched/    ← same layout, with the patched jars
```

### 1. One-time setup

```bash
bash scripts/setup-checkouts.sh ~/sources/hop-ab
```

What this does, step by step:

1. `git clone https://github.com/apache/hop.git ~/sources/hop-ab/hop-main`
   (full clone, ~1 GB, done once — also serves as object store for the worktree)
2. `git worktree add ~/sources/hop-ab/hop-2.19.0 46436154ae1a1e940861d485559819360c2af86e`
   (second working tree at the pinned 2.19.0 commit, no second clone needed)
3. `scripts/apply-ui-patch.sh ~/sources/hop-ab/hop-2.19.0`
   (copies the 16 overlay files; refuses any other Hop revision)

Example output:

```text
==> Cloning apache/hop (full clone, ~1 GB) into …/hop-main ...
==> Adding worktree …/hop-2.19.0 at 46436154ae1a1e940861d485559819360c2af86e ...
==> Applying hop-ui-patch overlay ...
Apache Hop 2.19.0: 46436154ae1a1e940861d485559819360c2af86e
Installed 16 overlay files.
```

Re-running the setup is safe: existing directories are fetched/reset and the
overlay application is idempotent.

### 2. Build both clients

```bash
bash scripts/build-ab-dist.sh \
  ~/sources/hop-ab/hop-main \
  ~/sources/hop-ab/hop-2.19.0 \
  ~/sources/hop-ab/dist
```

Each client build runs `./mvnw -DskipTests clean package` inside the checkout
(full reactor including all plugins; ~20–40 min cold, ~5–15 min warm) and then
unpacks the official `assemblies/client/target/hop-client-*.zip` into
`dist/<name>/`. The result is **unzipped on purpose**: individual JARs stay
replaceable, e.g. swapping in a locally patched `hop-ui`.

Requirements: `git`, a JDK **21–24** (an sdkman Java 21 is auto-detected; Java 25+
does not work — Lombok 1.18.x does not run on it), ~10 GB disk.

### 3. Start and compare

```bash
~/sources/hop-ab/dist/hop-main/hop-gui.sh              # current upstream main
~/sources/hop-ab/dist/hop-2.19.0-patched/hop-gui.sh    # 2.19.0 + overlay
```

Headless smoke test (proves classpath + plugins without opening a window):

```bash
cd ~/sources/hop-ab/dist/hop-main
./hop-run.sh -f config/projects/samples/pipelines/pipeline-with-parameter.hpl -r local -p samples
# → "Execution finished on a local pipeline engine with run configuration 'local'"
```

### 4. Pull the newest 2.20.0-SNAPSHOT

The snapshots move daily. To build the latest `main` again:

```bash
git -C ~/sources/hop-ab/hop-main pull --ff-only
bash scripts/build-client.sh ~/sources/hop-ab/hop-main ~/sources/hop-ab/dist/hop-main
```

`build-client.sh` deletes and recreates `dist/hop-main`, so an old state can
never linger. The 2.19.0 worktree is unaffected by the pull.

### 5. Iterating on the patch

1. Edit files in `overlay/`.
2. `bash scripts/apply-ui-patch.sh ~/sources/hop-ab/hop-2.19.0`
   (idempotent; only changed files are copied)
3. `bash scripts/build-client.sh ~/sources/hop-ab/hop-2.19.0 ~/sources/hop-ab/dist/hop-2.19.0-patched`
   (incremental, a few minutes — only `ui`/`engine` sources changed)

See `docs/source-builds.md` for script reference and troubleshooting.

## Developing further UI changes

For new phases, modify the desired Apache Hop source files in `overlay/` directly (or regenerate them from a clean pinned Hop checkout), then run the normal CI build. No new phase applicator, marker set or state migration is required.

The design target remains a cleaner native desktop IDE rather than a web-style skin or a replacement SWT widget framework: quieter surfaces, clearer hierarchy, fewer borders, consistent spacing and restrained accent usage.
