# Source builds for A/B testing

Builds two runnable, **unzipped** Apache Hop clients from source — current `main`
and the pinned 2.19.0 commit with the `hop-ui-patch` overlay — so the UI changes
can be compared side by side.

## Why source builds

The official client assembly (`assemblies/client`) already encodes every
distribution detail — provided-scope handling, classloader groups, `lib/jdbc`,
marketplace exclusions. Building from source therefore reproduces the official
client exactly. Since the patch is source-based anyway, one build path covers
both variants and the comparison is honest.

## Directory layout

```text
<base>/                        e.g. ~/sources/hop-ab  (any name works)
├── hop-main/                  clone of apache/hop on main
├── hop-2.19.0/                worktree at the pinned 2.19.0 commit + overlay
└── dist/
    ├── hop-main/
    └── hop-2.19.0-patched/
```

`hop-main` serves double duty: it is the `main` checkout **and** the shared git
object store for the `hop-2.19.0` worktree — the 2.19.0 sources cost almost no
extra disk space.

## Scripts

### `scripts/setup-checkouts.sh <base>`

Creates the two checkouts and applies the overlay:

1. `git clone https://github.com/apache/hop.git <base>/hop-main`
2. `git worktree add <base>/hop-2.19.0 46436154ae1a1e940861d485559819360c2af86e`
3. `scripts/apply-ui-patch.sh <base>/hop-2.19.0`

Idempotent: existing directories are fetched/reset, the overlay application is a
no-op when already installed.

Environment: `HOP_REPO_URL` (default `https://github.com/apache/hop.git`),
`HOP_PINNED_COMMIT` (default `46436154ae1a1e940861d485559819360c2af86e`).

### `scripts/build-client.sh <hop-checkout> <dist-dir>`

Runs `./mvnw -DskipTests clean package` inside the checkout and unpacks the
resulting `assemblies/client/target/hop-client-*.zip` into `<dist-dir>` —
recreating it, so a stale state can never linger. The result is unzipped on
purpose: individual JARs stay replaceable.

Enforces Java 21–24 (Hop 2.19/2.20 builds with Lombok 1.18.x, which does not
run on Java 25+) and auto-detects an sdkman Java 21 when `JAVA_HOME` is unset
or incompatible.

### `scripts/build-ab-dist.sh <hop-main-checkout> <hop-2.19.0-checkout> [dist-base]`

Calls `build-client.sh` twice; outputs `dist-base/hop-main` and
`dist-base/hop-2.19.0-patched` (default `dist-base`: `dist`).

## Example: first run end to end

```bash
# 1. one-time setup (clone + worktree + overlay)
bash scripts/setup-checkouts.sh ~/sources/hop-ab

# 2. build both clients
bash scripts/build-ab-dist.sh \
  ~/sources/hop-ab/hop-main \
  ~/sources/hop-ab/hop-2.19.0 \
  ~/sources/hop-ab/dist

# 3. start and compare
~/sources/hop-ab/dist/hop-main/hop-gui.sh
~/sources/hop-ab/dist/hop-2.19.0-patched/hop-gui.sh
```

Verify the patch made it into the built client:

```bash
unzip -l ~/sources/hop-ab/dist/hop-2.19.0-patched/lib/core/hop-ui-2.19.0.jar | grep HopUiTheme
```

Headless smoke test (classpath + plugins, no window):

```bash
cd ~/sources/hop-ab/dist/hop-main
./hop-run.sh -f config/projects/samples/pipelines/pipeline-with-parameter.hpl -r local -p samples
# → "Execution finished on a local pipeline engine with run configuration 'local'"
```

## Daily update of the 2.20.0-SNAPSHOT client

```bash
git -C ~/sources/hop-ab/hop-main pull --ff-only
bash scripts/build-client.sh ~/sources/hop-ab/hop-main ~/sources/hop-ab/dist/hop-main
```

## Troubleshooting

- **Build fails with `cannot find symbol` in `hop-core`** — the build ran on
  Java 25+. Lombok 1.18.x does not run on Java 25, so all generated methods are
  missing. Use JDK 21–24: set `JAVA_HOME` accordingly, or let `build-client.sh`
  auto-detect the sdkman Java 21.
- **`apply-ui-patch.sh` refuses the checkout** — the 2.19.0 worktree must be at
  exactly `46436154ae…`. Re-create it:
  `git -C <base>/hop-main worktree add <base>/hop-2.19.0 46436154ae1a1e940861d485559819360c2af86e`.
- **`git pull` in `hop-main` fails** — the additional worktree pins the
  repository; a plain `git pull` of the `main` branch still works. If in doubt:
  `git -C <base>/hop-main fetch origin && git -C <base>/hop-main reset --hard origin/main`.
- **Disk space** — each built client is ~400 MB; the Maven `target/` directories
  and `~/.m2` add several GB in total.
