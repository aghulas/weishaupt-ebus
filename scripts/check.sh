#!/usr/bin/env bash
# Checks the Weishaupt TypeSpec definitions: format, compile, ebusd --checkconfig.
# Runs every step, then reports. Exit code 0 only if all steps pass.
set -uo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CFG="${CFG_REPO:-$ROOT/repos/ebusd-configuration}"
OUT="$ROOT/out"
RELEASE="${EBUSD_RELEASE:-v26.1-weishaupt.1}"
FORK="${EBUSD_FORK:-aghulas/ebusd}"
fail=0

[ -d "$CFG/src/weishaupt" ] || { echo "no $CFG/src/weishaupt — run scripts/setup.sh"; exit 2; }
mkdir -p "$OUT"
cd "$CFG" || exit 2
echo "branch: $(git branch --show-current) @ $(git rev-parse --short HEAD)"

echo "== 1/4 src/ holds only .tsp and .yaml"
extra=$(find src/weishaupt -type f ! -name '*.tsp' ! -name '*.yaml')
if [ -n "$extra" ]; then echo "FAIL:"; echo "$extra"; fail=1; else echo "ok"; fi

echo "== 2/4 format"
if npx tsp format --check "src/weishaupt/*.tsp" >"$OUT/format.log" 2>&1; then echo "ok"
else echo "FAIL: $(grep -oE '[0-9]+ need format' "$OUT/format.log" | head -1), see out/format.log (fix: npx tsp format \"src/weishaupt/*.tsp\")"; fail=1; fi

echo "== 3/4 compile"
rm -rf "$OUT/csv"
if npx tsp compile src/main.tsp --emit @ebusd/ebus-typespec \
     --option @ebusd/ebus-typespec.withMinMax=true --output-dir "$OUT/csv" >"$OUT/compile.log" 2>&1 \
   && ! grep -qE '^(warning|error) |Found [0-9]+ (warning|error)' "$OUT/compile.log"; then echo "ok"
else echo "FAIL: see out/compile.log"; tail -5 "$OUT/compile.log"; fail=1; fi

echo "== 4/4 ebusd --checkconfig ($FORK $RELEASE)"
case "$(uname -m)" in arm64|aarch64) arch=aarch64 ;; *) arch=amd64 ;; esac
bin="$OUT/ebusd-$RELEASE-$arch"
[ -s "$bin" ] || gh release download "$RELEASE" -R "$FORK" -p "ebusd-$arch" -O "$bin" || fail=1
chmod +x "$bin" 2>/dev/null
csv="$OUT/csv/@ebusd/ebus-typespec"
if [ -d "$csv/weishaupt" ] && docker run --rm -v "$bin":/ebusd:ro -v "$csv":/cfg:ro debian:trixie-slim \
     /ebusd --checkconfig --configpath=/cfg/weishaupt >"$OUT/checkconfig.log" 2>&1 \
   && ! grep -qi 'error' "$OUT/checkconfig.log"; then grep -o 'found messages: [0-9]*' "$OUT/checkconfig.log"
else echo "FAIL: see out/checkconfig.log"; tail -5 "$OUT/checkconfig.log" 2>/dev/null; fail=1; fi

[ "$fail" -eq 0 ] && echo "ALL CHECKS PASSED" || echo "CHECKS FAILED"
exit "$fail"
