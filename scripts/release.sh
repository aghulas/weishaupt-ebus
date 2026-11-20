#!/usr/bin/env bash
# Builds the CSV release archives of the integration branch under out/release/. Publishes nothing.
#
#   scripts/release.sh <version>      for example: scripts/release.sh 1.0.0
#
# Runs scripts/integrate.sh first (clean worktree check of the integration branch); the archives
# are made from the CSV that check compiled, and only if it passed: the English archive
# weishaupt-ebusd-config-<version>, and one more per language, ...-<version>-<lang>, with the same
# layout and the comments translated by src/<lang>.yaml of the integration branch.
#
# Beside the archives: weishaupt-metadata-<version>.json, generated from metadata/weishaupt.toml
# of the integration branch and the compiled CSV of every language (scripts/metadata.py, format
# in docs/companion-contract.md); weishaupt-fixtures-<version>.json, the readings of
# evidence/fixtures.toml, each decoded by ebusd on the same CSV (scripts/fixtures.py);
# sha256sums-<version>.txt, the checksums of all of them.
#
# RELEASE_LANGS  languages with an archive of their own (default: fr; empty: English only)
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
VERSION="${1:?usage: scripts/release.sh <version>}"
CFG="${CFG_REPO:-$ROOT/repos/ebusd-configuration}"
BRANCH="${INTEGRATION:-weishaupt}"
EBUSD="${EBUSD_RELEASE:-v26.1-weishaupt.1}"
NAME="weishaupt-ebusd-config-$VERSION"
REL="$ROOT/out/release"
LANGS="${RELEASE_LANGS-fr}"
TERMS="$ROOT/evidence/terms.md"

"$ROOT/scripts/integrate.sh" | tee "$ROOT/out/integrate.log"
grep -q '^ALL CHECKS PASSED$' "$ROOT/out/integrate.log" || { echo "check failed: no archive"; exit 1; }
count=$(grep -o 'found messages: [0-9]*' "$ROOT/out/integrate.log" | grep -o '[0-9]*' | tail -1)

commit=$(git -C "$CFG" rev-parse --short "$BRANCH")
epoch=$(git -C "$CFG" show -s --format=%ct "$BRANCH")
touch_ts=$(date -u -r "$epoch" +%Y%m%d%H%M.%S 2>/dev/null || date -u -d "@$epoch" +%Y%m%d%H%M.%S)
lib=$(node -p "require('$ROOT/out/integration/node_modules/@ebusd/ebus-typespec/package.json').version")
# Terms of the glossary that no vendor document gives yet, for the notice.
provisional=$(awk -F' *[|] *' '$6 == "provisional" {printf "%s%s", sep, $2; sep = ", "}' "$TERMS")

if tar --version 2>/dev/null | grep -qi gnu; then
  TAR_FLAGS=(--owner=0 --group=0 --numeric-owner --no-xattrs)
else
  TAR_FLAGS=(--uid 0 --gid 0 --no-xattrs)
fi

# archive <name> <csv tree>: root files, the lot folder as kromschroeder/, notice, checksums.
archive() {
  local name="$1" csv="$2"
  rm -rf "$REL/$name" "$REL/$name.tar.gz"
  mkdir -p "$REL/$name"
  cp "$csv"/*.csv "$REL/$name/"
  # The devices scan as manufacturer Kromschroeder; upstream keeps their files in the Wolf folder.
  cp -r "$csv/wolf" "$REL/$name/kromschroeder"
  sed -e "s|@VERSION@|$VERSION|g" -e "s|@COMMIT@|$commit|g" -e "s|@NAME@|$name|g" -e "s|@BASE@|$NAME|g" \
      -e "s|@COUNT@|$count|g" -e "s|@EBUSD@|$EBUSD|g" -e "s|@LIB@|$lib|g" \
      -e "s|@PROVISIONAL@|${provisional:-none}|g" \
      "$ROOT/docs/release-readme.md" >"$REL/$name/README.md"
  (cd "$REL/$name" && find . -type f ! -name sha256sums.txt | sort | sed 's|^\./||' | xargs shasum -a 256 >sha256sums.txt)
  # Fixed order, owner, timestamps and gzip header: the same input gives the same archive.
  find "$REL/$name" -exec touch -t "$touch_ts" {} +
  (cd "$REL" && find "$name" -type f | LC_ALL=C sort >"$name.list" \
    && COPYFILE_DISABLE=1 tar "${TAR_FLAGS[@]}" -cf - -T "$name.list" | gzip -n >"$name.tar.gz" \
    && rm "$name.list")
  (cd "$REL" && shasum -a 256 "$name.tar.gz")
  echo "archive: out/release/$name.tar.gz ($count messages), not published"
}

archive "$NAME" "$ROOT/out/csv/@ebusd/ebus-typespec"
assets="$NAME.tar.gz"
langargs=()
for lang in $LANGS; do
  # check.sh compiled it, compared it with English and loaded it: its lines are in the log.
  grep -q "^$lang: found messages: $count, as in English\$" "$ROOT/out/integrate.log" \
    || { echo "$lang: not compiled and checked by scripts/check.sh (no src/$lang.yaml on $BRANCH?): no archive"; exit 1; }
  archive "$NAME-$lang" "$ROOT/out/csv.$lang/@ebusd/ebus-typespec"
  assets="$assets $NAME-$lang.tar.gz"
  langargs+=(--lang "$lang=$ROOT/out/csv.$lang/@ebusd/ebus-typespec")
done

# Metadata and fixtures of the release, from the same compile as the archives.
SIDE="$ROOT/out/integration/metadata/weishaupt.toml"
META="$REL/weishaupt-metadata-$VERSION.json"
FIXT="$REL/weishaupt-fixtures-$VERSION.json"
python3 "$ROOT/scripts/metadata.py" build "$SIDE" "$ROOT/out/csv/@ebusd/ebus-typespec" \
  "$META" --version "$VERSION" --commit "$commit" --loaded "$count" \
  ${langargs[@]+"${langargs[@]}"}
case "$(uname -m)" in arm64|aarch64) arch=aarch64 ;; *) arch=amd64 ;; esac
python3 "$ROOT/scripts/fixtures.py" build "$ROOT/evidence/fixtures.toml" \
  "$ROOT/out/csv/@ebusd/ebus-typespec" "$FIXT" --version "$VERSION" \
  --commit "$commit" --sidecar "$SIDE" --ebusd "$ROOT/out/ebusd-$EBUSD-$arch" --release "$EBUSD"

python3 "$ROOT/scripts/validate-schema.py" "$ROOT/schemas/metadata.schema.json" "$META"
python3 "$ROOT/scripts/validate-schema.py" "$ROOT/schemas/fixtures.schema.json" "$FIXT"

assets="$assets weishaupt-metadata-$VERSION.json weishaupt-fixtures-$VERSION.json"
# shellcheck disable=SC2086
(cd "$REL" && shasum -a 256 $assets >"sha256sums-$VERSION.txt" && cat "sha256sums-$VERSION.txt")
echo "assets: out/release/sha256sums-$VERSION.txt lists them, not published"
echo "reminder: when publishing, tag both ebusd-configuration and weishaupt-ebus with weishaupt-$VERSION"
