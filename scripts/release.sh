#!/usr/bin/env bash
# Builds the CSV release archive of the integration branch under out/release/. Publishes nothing.
#
#   scripts/release.sh <version>      for example: scripts/release.sh 0.1.0
#
# Runs scripts/integrate.sh first (rebuild of the integration branch and full check); the archive
# is made from the CSV that check compiled, and only if it passed.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
VERSION="${1:?usage: scripts/release.sh <version>}"
CFG="${CFG_REPO:-$ROOT/repos/ebusd-configuration}"
BRANCH="${INTEGRATION:-weishaupt}"
EBUSD="${EBUSD_RELEASE:-v26.1-weishaupt.1}"
NAME="weishaupt-ebusd-config-$VERSION"
REL="$ROOT/out/release"
CSV="$ROOT/out/csv/@ebusd/ebus-typespec"

"$ROOT/scripts/integrate.sh" | tee "$ROOT/out/integrate.log"
grep -q '^ALL CHECKS PASSED$' "$ROOT/out/integrate.log" || { echo "check failed: no archive"; exit 1; }
count=$(grep -o 'found messages: [0-9]*' "$ROOT/out/integrate.log" | grep -o '[0-9]*' | tail -1)

rm -rf "$REL/$NAME" "$REL/$NAME.tar.gz"
mkdir -p "$REL/$NAME"
cp "$CSV"/*.csv "$REL/$NAME/"
# The devices scan as manufacturer Kromschroeder; upstream keeps their files in the Wolf folder.
cp -r "$CSV/wolf" "$REL/$NAME/kromschroeder"
sed -e "s|@VERSION@|$VERSION|g" -e "s|@COMMIT@|$(git -C "$CFG" rev-parse --short "$BRANCH")|g" \
    -e "s|@COUNT@|$count|g" -e "s|@EBUSD@|$EBUSD|g" \
    -e "s|@LIB@|$(node -p "require('$ROOT/out/integration/node_modules/@ebusd/ebus-typespec/package.json').version")|g" \
    "$ROOT/docs/release-readme.md" >"$REL/$NAME/README.md"
(cd "$REL/$NAME" && find . -type f ! -name sha256sums.txt | sort | sed 's|^\./||' | xargs shasum -a 256 >sha256sums.txt)
# Fixed order, owner and dates: the same input gives the same archive.
(cd "$REL" && find "$NAME" -type f | LC_ALL=C sort >"$NAME.list" \
  && COPYFILE_DISABLE=1 tar --uid 0 --gid 0 --no-xattrs -czf "$NAME.tar.gz" -T "$NAME.list" && rm "$NAME.list")
(cd "$REL" && shasum -a 256 "$NAME.tar.gz")
echo "archive: out/release/$NAME.tar.gz ($count messages), not published"
