#!/usr/bin/env bash
#
# Builds the Apache Hop client distribution from a source checkout and unpacks it
# into <dist-dir> (unzipped, ready to run).
#
# Usage: build-client.sh <hop-checkout> <dist-dir>
#
# The full Maven reactor is built with tests skipped; the resulting
# assemblies/client/target/hop-client-*.zip is unpacked so individual JARs remain
# replaceable (e.g. hop-ui from a locally patched build).
#
set -euo pipefail

CHECKOUT="${1:?usage: build-client.sh <hop-checkout> <dist-dir>}"
DIST_DIR="${2:?usage: build-client.sh <hop-checkout> <dist-dir>}"

# Java 21-24 required: Hop 2.19/2.20 builds with Lombok 1.18.x, which does not run
# on newer JVMs (Java 25+ fails with missing generated methods). Prefer a compatible
# JAVA_HOME, otherwise auto-detect an sdkman Java 21.
java_major() { java -version 2>&1 | sed -nE 's/.*version "([0-9]+).*/\1/p' | head -1; }
java_compatible() {
  local major
  major="$(java_major)"
  [ -n "$major" ] && [ "$major" -ge 21 ] && [ "$major" -le 24 ]
}

if [ -n "${JAVA_HOME:-}" ]; then
  export PATH="$JAVA_HOME/bin:$PATH"
  if ! java_compatible; then
    echo "JAVA_HOME points to an incompatible Java ($(java -version 2>&1 | head -1)); looking for sdkman Java 21 ..." >&2
    JAVA_HOME=""
  fi
fi
if [ -z "${JAVA_HOME:-}" ] && [ -d "$HOME/.sdkman/candidates/java" ]; then
  JAVA_HOME="$(ls -d "$HOME"/.sdkman/candidates/java/21* 2>/dev/null | head -1 || true)"
fi
if [ -n "${JAVA_HOME:-}" ]; then
  export JAVA_HOME
  export PATH="$JAVA_HOME/bin:$PATH"
fi
if ! java_compatible; then
  echo "Java 21-24 required (found: $(java -version 2>&1 | head -1))." >&2
  echo "Hop's build uses Lombok 1.18.x, which does not run on newer JVMs." >&2
  exit 1
fi
echo "==> Using Java: $(java -version 2>&1 | head -1)"

if [ ! -x "$CHECKOUT/mvnw" ]; then
  echo "$CHECKOUT does not look like an Apache Hop checkout (mvnw missing)." >&2
  exit 1
fi

cd "$CHECKOUT"
echo "==> Building Hop client from $CHECKOUT (mvnw -DskipTests clean package) ..."
./mvnw -DskipTests clean package

ZIP="$(ls assemblies/client/target/hop-client-*.zip 2>/dev/null | head -1)"
if [ -z "$ZIP" ]; then
  echo "Client zip not found under $CHECKOUT/assemblies/client/target" >&2
  exit 1
fi

echo "==> Unpacking $ZIP into $DIST_DIR ..."
STAGE="$(mktemp -d)"
unzip -q "$ZIP" -d "$STAGE"
rm -rf "$DIST_DIR"
mkdir -p "$(dirname "$DIST_DIR")"
mv "$STAGE/hop" "$DIST_DIR"
rmdir "$STAGE"

echo "==> Done."
echo "    Start:  $DIST_DIR/hop-gui.sh"
echo "    Run:    $DIST_DIR/hop-run.sh -f <file.hpl> -r local"
