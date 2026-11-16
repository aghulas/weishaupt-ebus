#!/usr/bin/env bash
# Checks the Weishaupt TypeSpec definitions: format, compile, ebusd --checkconfig.
# Runs every step, then reports. Exit code 0 only if all steps pass.
#
# LOT_DIR    folder under src/ that holds the definitions (default: wolf)
# CHECKCONFIG  local (Docker) or actions (GitHub Actions, workflow checkconfig.yml of this
#            repository). Default: local when Docker answers, actions otherwise.
set -uo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CFG="${CFG_REPO:-$ROOT/repos/ebusd-configuration}"
LOT="${LOT_DIR:-wolf}"
OUT="$ROOT/out"
RELEASE="${EBUSD_RELEASE:-v26.1-weishaupt.1}"
FORK="${EBUSD_FORK:-aghulas/ebusd}"
WORKBENCH="${CHECK_REPO:-aghulas/weishaupt-ebus}"
fail=0

# GitHub CLI installed on Windows but not yet on the PATH of this shell
command -v gh >/dev/null 2>&1 || { [ -x "/c/Program Files/GitHub CLI/gh.exe" ] && PATH="$PATH:/c/Program Files/GitHub CLI"; }

[ -d "$CFG/src/$LOT" ] || { echo "no $CFG/src/$LOT — run scripts/setup.sh, or set LOT_DIR"; exit 2; }
mkdir -p "$OUT"
cd "$CFG" || exit 2
echo "branch: $(git branch --show-current) @ $(git rev-parse --short HEAD), lot folder src/$LOT"

echo "== 1/4 src/$LOT holds only .tsp and .yaml"
extra=$(find "src/$LOT/" -type f ! -name '*.tsp' ! -name '*.yaml')
if [ -n "$extra" ]; then echo "FAIL:"; echo "$extra"; fail=1; else echo "ok"; fi

echo "== 2/4 format"
if npx tsp format --check "src/$LOT/*.tsp" >"$OUT/format.log" 2>&1; then echo "ok"
else echo "FAIL: $(grep -oE '[0-9]+ need format' "$OUT/format.log" | head -1), see out/format.log (fix: npx tsp format \"src/$LOT/*.tsp\"; on Windows check core.autocrlf=false first)"; fail=1; fi

echo "== 3/4 compile"
rm -rf "$OUT/csv"
if npx tsp compile src/main.tsp --emit @ebusd/ebus-typespec \
     --option @ebusd/ebus-typespec.withMinMax=true --output-dir "$OUT/csv" >"$OUT/compile.log" 2>&1 \
   && ! grep -qE '^(warning|error) |Found [0-9]+ (warning|error)' "$OUT/compile.log"; then echo "ok"
else echo "FAIL: see out/compile.log"; tail -5 "$OUT/compile.log"; fail=1; fi

csv="$OUT/csv/@ebusd/ebus-typespec"
mode="${CHECKCONFIG:-}"
[ -n "$mode" ] || { docker info >/dev/null 2>&1 && mode=local || mode=actions; }
echo "== 4/4 ebusd --checkconfig ($FORK $RELEASE, $mode)"
cfail=0; rm -f "$OUT/checkconfig.log"
if [ ! -d "$csv/$LOT" ]; then
  echo "FAIL: nothing compiled for $LOT"; cfail=1
elif [ "$mode" = local ]; then
  case "$(uname -m)" in arm64|aarch64) arch=aarch64 ;; *) arch=amd64 ;; esac
  bin="$OUT/ebusd-$RELEASE-$arch"
  [ -s "$bin" ] || gh release download "$RELEASE" -R "$FORK" -p "ebusd-$arch" -O "$bin" || cfail=1
  chmod +x "$bin" 2>/dev/null
  rm -rf "$OUT/cfg" && mkdir -p "$OUT/cfg" && cp "$csv"/*.csv "$OUT/cfg/" && cp -r "$csv/$LOT" "$OUT/cfg/"
  docker run --rm -v "$bin":/ebusd:ro -v "$OUT/cfg":/cfg:ro debian:trixie-slim \
    /ebusd --checkconfig --configpath=/cfg >"$OUT/checkconfig.log" 2>&1 || cfail=1
else
  # CSV root files and the lot folder only, sent as a workflow input: nothing is pushed.
  payload=$(cd "$csv" && tar czf - ./*.csv "$LOT" | base64 | tr -d '\n')
  label="$(git branch --show-current)@$(git rev-parse --short HEAD) $(date -u +%Y%m%dT%H%M%SZ)-$RANDOM"
  if gh workflow run checkconfig.yml -R "$WORKBENCH" --ref main -f csv_tgz_b64="$payload" \
       -f label="$label" -f ebusd_fork="$FORK" -f ebusd_release="$RELEASE" >/dev/null; then
    run=""
    for _ in $(seq 1 30); do
      run=$(gh run list -R "$WORKBENCH" -w checkconfig.yml -e workflow_dispatch -L 10 \
              --json databaseId,displayTitle --jq ".[] | select(.displayTitle == \"checkconfig $label\") | .databaseId" | head -1)
      [ -n "$run" ] && break; sleep 2
    done
    if [ -z "$run" ]; then echo "FAIL: workflow run not found"; cfail=1
    else
      echo "run: https://github.com/$WORKBENCH/actions/runs/$run"
      gh run watch "$run" -R "$WORKBENCH" --exit-status >/dev/null 2>&1 || cfail=1
      rm -rf "$OUT/checkconfig" && gh run download "$run" -R "$WORKBENCH" -n checkconfig -D "$OUT/checkconfig" >/dev/null 2>&1 \
        && cp "$OUT/checkconfig/checkconfig.log" "$OUT/checkconfig.log"
    fi
  else echo "FAIL: could not start the workflow (gh auth status?)"; cfail=1; fi
fi
if [ -s "$OUT/checkconfig.log" ] && ! grep -qi 'error' "$OUT/checkconfig.log" && [ "$cfail" -eq 0 ]; then
  grep -o 'found messages: [0-9]*' "$OUT/checkconfig.log" || echo "ok"
else echo "FAIL: see out/checkconfig.log"; tail -5 "$OUT/checkconfig.log" 2>/dev/null; fail=1; fi

[ "$fail" -eq 0 ] && echo "ALL CHECKS PASSED" || echo "CHECKS FAILED"
exit "$fail"
