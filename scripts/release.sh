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
EBUSD="${EBUSD_RELEASE:-v26.1-weishaupt.2}"
NAME="weishaupt-ebusd-config-$VERSION"
REL="$ROOT/out/release"
LANGS="${RELEASE_LANGS-fr}"
TERMS="$ROOT/evidence/terms.md"

# The scripts that build the release are tested first: no archive from a broken workbench.
(cd "$ROOT" && python3 -m unittest discover -s tests -q) || { echo "unit tests failed: no archive"; exit 1; }

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

# Message counts from the check log: the standard set (loads on a stock ebusd) and, when the
# branch has the extension variant (src/main-ext.tsp), the extension set (fork build only).
stdcount=$(grep -oE 'standard set on [^:]*: found messages: [0-9]+' "$ROOT/out/integrate.log" | grep -oE '[0-9]+$' | tail -1)
extcount=$(grep -oE 'extension set on [^:]*: found messages: [0-9]+' "$ROOT/out/integrate.log" | grep -oE '[0-9]+$' | tail -1)
[ -n "$stdcount" ] || stdcount="$count"
[ -n "$extcount" ] || extcount="$count"
EXTBASE="weishaupt-ebusd-config-extension-$VERSION"
has_ext=0
[ -f "$ROOT/out/integration/src/main-ext.tsp" ] && [ "$extcount" != "$stdcount" ] && has_ext=1
printf -v VARIANT_EXT '**Extension variant.** This archive adds composite reads over four registers (message IDs longer than 7 bytes), which only a fork ebusd build with long-ID support (%s or the matching add-on) can load; a stock ebusd cannot. Use it only with that build. For a stock ebusd, use the standard archive `%s.tar.gz` instead, which this variant extends: every value read here also has its own message in the standard archive, and nothing else differs.\n\n' "$EBUSD" "$NAME"

# archive <name> <csv tree> <count> <variant note>: root files, lot as kromschroeder/, notice, sums.
archive() {
  local name="$1" csv="$2" acount="$3" variant="$4"
  rm -rf "$REL/$name" "$REL/$name.tar.gz"
  mkdir -p "$REL/$name"
  cp "$csv"/*.csv "$REL/$name/"
  # The devices scan as manufacturer Kromschroeder; upstream keeps their files in the Wolf folder.
  cp -r "$csv/wolf" "$REL/$name/kromschroeder"
  python3 "$ROOT/scripts/render-notice.py" "$ROOT/docs/release-readme.md" \
      "VERSION=$VERSION" "COMMIT=$commit" "NAME=$name" "BASE=$NAME" "COUNT=$acount" "EBUSD=$EBUSD" \
      "LIB=$lib" "PROVISIONAL=$provisional" "VARIANT=$variant" >"$REL/$name/README.md"
  (cd "$REL/$name" && find . -type f ! -name sha256sums.txt | sort | sed 's|^\./||' | xargs shasum -a 256 >sha256sums.txt)
  # Fixed order, owner, timestamps and gzip header: the same input gives the same archive.
  find "$REL/$name" -exec touch -t "$touch_ts" {} +
  (cd "$REL" && find "$name" -type f | LC_ALL=C sort >"$name.list" \
    && COPYFILE_DISABLE=1 tar "${TAR_FLAGS[@]}" -cf - -T "$name.list" | gzip -n >"$name.tar.gz" \
    && rm "$name.list")
  (cd "$REL" && shasum -a 256 "$name.tar.gz")
  echo "archive: out/release/$name.tar.gz ($acount messages), not published"
}

# Standard archives (load on a stock ebusd) come from the standard compile; extension archives
# (fork build only) from the extension compile. The translated standard tree is compiled here, as
# scripts/check.sh only compiled the translated extension tree.
archive "$NAME" "$ROOT/out/csv-std/@ebusd/ebus-typespec" "$stdcount" ""
assets="$NAME.tar.gz"
[ "$has_ext" = 1 ] && { archive "$EXTBASE" "$ROOT/out/csv/@ebusd/ebus-typespec" "$extcount" "$VARIANT_EXT"; assets="$assets $EXTBASE.tar.gz"; }
langargs=()
for lang in $LANGS; do
  # check.sh compiled, compared and loaded the extension tree translated: its line is in the log.
  grep -q "^$lang: found messages: $extcount, as in English\$" "$ROOT/out/integrate.log" \
    || { echo "$lang: not compiled and checked by scripts/check.sh (no src/$lang.yaml on $BRANCH?): no archive"; exit 1; }
  # Standard translated tree: compile the standard entry with the translation of the branch.
  rm -rf "$ROOT/out/csv-std.$lang"
  (cd "$ROOT/out/integration" && npx tsp compile src/main.tsp --emit @ebusd/ebus-typespec \
      --option @ebusd/ebus-typespec.withMinMax=true \
      --option "@ebusd/ebus-typespec.translations=src/$lang.yaml" \
      --output-dir "$ROOT/out/csv-std.$lang" >"$ROOT/out/compile-std.$lang.log" 2>&1) \
    || { echo "$lang: standard translated compile failed, see out/compile-std.$lang.log"; exit 1; }
  archive "$NAME-$lang" "$ROOT/out/csv-std.$lang/@ebusd/ebus-typespec" "$stdcount" ""
  assets="$assets $NAME-$lang.tar.gz"
  [ "$has_ext" = 1 ] && { archive "$EXTBASE-$lang" "$ROOT/out/csv.$lang/@ebusd/ebus-typespec" "$extcount" "$VARIANT_EXT"; assets="$assets $EXTBASE-$lang.tar.gz"; }
  langargs+=(--lang "$lang=$ROOT/out/csv.$lang/@ebusd/ebus-typespec")
done

# Metadata and fixtures of the release, from the extension compile (carriers are excluded from
# both, so they are the same for the standard and the extension archives).
SIDE="$ROOT/out/integration/metadata/weishaupt.toml"
META="$REL/weishaupt-metadata-$VERSION.json"
FIXT="$REL/weishaupt-fixtures-$VERSION.json"
python3 "$ROOT/scripts/metadata.py" build "$SIDE" "$ROOT/out/csv/@ebusd/ebus-typespec" \
  "$META" --version "$VERSION" --commit "$commit" --loaded "$stdcount" \
  ${langargs[@]+"${langargs[@]}"}
case "$(uname -m)" in arm64|aarch64) arch=aarch64 ;; *) arch=amd64 ;; esac
python3 "$ROOT/scripts/fixtures.py" build "$ROOT/evidence/fixtures.toml" \
  "$ROOT/out/csv/@ebusd/ebus-typespec" "$FIXT" --version "$VERSION" \
  --commit "$commit" --sidecar "$SIDE" --ebusd "$ROOT/out/ebusd-$EBUSD-$arch" --release "$EBUSD"

# Strict: a release is not built on the basic check of a machine without the jsonschema package.
python3 "$ROOT/scripts/validate-schema.py" "$ROOT/schemas/metadata.schema.json" "$META" --require-jsonschema
python3 "$ROOT/scripts/validate-schema.py" "$ROOT/schemas/fixtures.schema.json" "$FIXT" --require-jsonschema

assets="$assets weishaupt-metadata-$VERSION.json weishaupt-fixtures-$VERSION.json"
# shellcheck disable=SC2086
(cd "$REL" && shasum -a 256 $assets >"sha256sums-$VERSION.txt" && cat "sha256sums-$VERSION.txt")
echo "assets: out/release/sha256sums-$VERSION.txt lists them, not published"
echo "reminder: when publishing, tag both ebusd-configuration and weishaupt-ebus with weishaupt-$VERSION"
