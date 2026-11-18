#!/usr/bin/env bash
# Checks the Weishaupt TypeSpec definitions: commit hygiene, format, compile, ebusd --checkconfig,
# translation files, metadata.
# Runs every step, then reports. Exit code 0 only if all steps pass.
#
#   scripts/check.sh           all steps
#   scripts/check.sh hygiene   commit hygiene only (lot branch and this repository)
#
# LOT_DIR      folder under src/ that holds the definitions (default: wolf)
# LOT_BASE     ref the lot branch is rebased on (default: upstream/master, detected otherwise)
# EXPECT_NAME, EXPECT_EMAIL
#              author and committer identity every checked commit must carry (default: user.name
#              and user.email of the repository being checked)
# HYGIENE_LAST number of recent commits of this repository checked besides the unpushed ones
#              (default: 20)
# CHECKCONFIG  local (Docker) or actions (GitHub Actions, workflow checkconfig.yml of this
#              repository). Default: local when Docker answers, actions otherwise.
#
# Translations (step 6): every src/<lang>.yaml other than en.yaml is compared with the comment
# strings of the lot files (scripts/i18n-keys.py). A file the base ref does not have is the
# fork's own: a key that matches no comment fails. A file with keys of the lot files is compiled
# to out/csv.<lang>, compared with the English CSV (only comments may differ) and loaded with
# --checkconfig (same message count).
#
# Metadata (step 7): metadata/weishaupt.toml, the sidecar the metadata file of a release is
# generated from, is compared with the compiled CSV (scripts/metadata.py check): every message
# of the lot files has an entry, every entry a message, every written setting its write
# conditions and an evidence record that names it. The file lives on the branch on top of the
# stack; a lot branch below it has none and the step says so. METADATA=required (set by
# scripts/integrate.sh) makes a missing file a failure.
set -uo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CFG="${CFG_REPO:-$ROOT/repos/ebusd-configuration}"
LOT="${LOT_DIR:-wolf}"
OUT="$ROOT/out"
RELEASE="${EBUSD_RELEASE:-v26.1-weishaupt.1}"
FORK="${EBUSD_FORK:-aghulas/ebusd}"
WORKBENCH="${CHECK_REPO:-aghulas/weishaupt-ebus}"
only="${1:-}"
fail=0

# Rule 9 of AGENTS.md: commit messages carry no tool trailer, tool name or session link.
MSG_RE='co-authored-by|claude|anthropic|copilot|chatgpt|generated with|https?://[^[:space:]]*/(share|chat|sessions?)/'
# Rule 4: obvious site data in added lines. Private or carrier-grade IPv4, MAC address, local host
# name, e-mail address, credential assigned a literal value.
SITE_RE='(^|[^0-9.])(10(\.[0-9]{1,3}){3}|192\.168(\.[0-9]{1,3}){2}|172\.(1[6-9]|2[0-9]|3[01])(\.[0-9]{1,3}){2}|100\.(6[4-9]|[7-9][0-9]|1[01][0-9]|12[0-7])(\.[0-9]{1,3}){2})\.?([^0-9.]|$)'
SITE_RE="$SITE_RE"'|(^|[^0-9a-f:])([0-9a-f]{2}:){5}[0-9a-f]{2}([^0-9a-f:]|$)'
SITE_RE="$SITE_RE"'|[a-z0-9-]+\.(local|lan|internal)([^a-z0-9]|$)'
SITE_RE="$SITE_RE"'|[a-z0-9._%+-]+@[a-z0-9-]+(\.[a-z0-9-]+)*\.[a-z]{2,}'
SITE_RE="$SITE_RE"'|(password|passwd|secret|token|api[_-]?key)[[:space:]]*[:=][[:space:]]*["'"'"']?[^[:space:]$"'"'"']'

# hygiene <label> <repository> <scan diff: yes|no>, commit ids on stdin.
# Messages and identities are checked on every commit, added lines only when asked.
hygiene() {
  local label="$1" repo="$2" scan="$3" shas name email bad n
  shas=$(sort -u)
  if [ -z "$shas" ]; then echo "$label: ok (no commit)"; return 0; fi
  n=$(printf '%s\n' "$shas" | wc -l | tr -d ' ')
  name="${EXPECT_NAME:-$(git -C "$repo" config user.name)}"
  email="${EXPECT_EMAIL:-$(git -C "$repo" config user.email)}"
  bad=""
  if [ -z "$name" ] || [ -z "$email" ]; then
    bad="expected identity unknown: set user.name and user.email, or EXPECT_NAME and EXPECT_EMAIL"$'\n'
  else
    bad+=$(printf '%s\n' "$shas" | git -C "$repo" log --no-walk --stdin --format='%h%x09%an%x09%ae%x09%cn%x09%ce' |
      awk -F'\t' -v n="$name" -v e="$email" '
        $2 != n || $3 != e { print $1 " author is " $2 " <" $3 ">, expected " n " <" e ">" }
        $4 != n || $5 != e { print $1 " committer is " $4 " <" $5 ">, expected " n " <" e ">" }')
    [ -n "$bad" ] && bad+=$'\n'
  fi
  bad+=$(printf '%s\n' "$shas" | git -C "$repo" log --no-walk --stdin --format='@@commit %h%n%B' |
    awk '/^@@commit /{c=$2; next} {print c " message: " $0}' | grep -Ei "$MSG_RE")
  if [ "$scan" = yes ]; then
    [ -n "$bad" ] && bad+=$'\n'
    bad+=$(printf '%s\n' "$shas" | git -C "$repo" log --no-walk --stdin -p --no-color --format='@@commit %h' |
      awk '/^@@commit /{c=$2; next} /^\+\+\+ /{f=substr($0,7); next} /^\+/{print c " " f ": " substr($0,2)}' |
      grep -Ei "$SITE_RE")
  fi
  bad=$(printf '%s\n' "$bad" | grep -v '^$')
  if [ -n "$bad" ]; then echo "$label: FAIL ($n commits)"; printf '%s\n' "$bad" | sed 's/^/  /'; return 1; fi
  echo "$label: ok ($n commits)"
}

# GitHub CLI installed on Windows but not yet on the PATH of this shell
command -v gh >/dev/null 2>&1 || { [ -x "/c/Program Files/GitHub CLI/gh.exe" ] && PATH="$PATH:/c/Program Files/GitHub CLI"; }

# checkconfig <csv tree> <name>: loads the root files and the lot folder of the tree in ebusd.
# Log in out/<name>.log; returns 0 when ebusd ran, the caller reads the log.
checkconfig() {
  local csv="$1" name="$2" cfail=0 arch bin sums want have payload label run
  local log="$OUT/$name.log" cfg="$OUT/${name/checkconfig/cfg}"
  rm -f "$log"
  if [ ! -d "$csv/$LOT" ]; then
    echo "FAIL: nothing compiled for $LOT"; cfail=1
  elif [ "$mode" = local ]; then
    case "$(uname -m)" in arm64|aarch64) arch=aarch64 ;; *) arch=amd64 ;; esac
    bin="$OUT/ebusd-$RELEASE-$arch"
    sums="$OUT/sha256sums-$RELEASE.txt"
    [ -s "$bin" ] || gh release download "$RELEASE" -R "$FORK" -p "ebusd-$arch" -O "$bin" || cfail=1
    [ -s "$sums" ] || gh release download "$RELEASE" -R "$FORK" -p sha256sums.txt -O "$sums" || cfail=1
    # The binary, freshly downloaded or cached, must match sha256sums.txt of the same release.
    want=$(awk -v f="ebusd-$arch" '$2 == f || $2 == "*" f {print $1}' "$sums" 2>/dev/null)
    have=$( { sha256sum "$bin" 2>/dev/null || shasum -a 256 "$bin" 2>/dev/null; } | awk '{print $1}')
    if [ -z "$want" ] || [ "$have" != "$want" ]; then
      echo "FAIL: sha256 of out/$(basename "$bin") is ${have:-unknown}, sha256sums.txt says ${want:-nothing} (delete both files in out/ to download again)"
      cfail=1
    else
      chmod +x "$bin" 2>/dev/null
      rm -rf "$cfg" && mkdir -p "$cfg" && cp "$csv"/*.csv "$cfg/" && cp -r "$csv/$LOT" "$cfg/"
      docker run --rm -v "$bin":/ebusd:ro -v "$cfg":/cfg:ro debian:trixie-slim \
        /ebusd --checkconfig --configpath=/cfg >"$log" 2>&1 || cfail=1
    fi
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
          && cp "$OUT/checkconfig/checkconfig.log" "$log"
      fi
    else echo "FAIL: could not start the workflow (gh auth status?)"; cfail=1; fi
  fi
  [ -s "$log" ] && ! grep -qi 'error' "$log" && [ "$cfail" -eq 0 ]
}

[ -d "$CFG/src/$LOT" ] || { echo "no $CFG/src/$LOT — run scripts/setup.sh, or set LOT_DIR"; exit 2; }
mkdir -p "$OUT"
cd "$CFG" || exit 2
echo "branch: $(git branch --show-current) @ $(git rev-parse --short HEAD), lot folder src/$LOT"

want=$(tr -d 'v \r\n' <"$ROOT/.nvmrc" 2>/dev/null | cut -d. -f1)
have=$(node -v 2>/dev/null | tr -d v | cut -d. -f1)
[ -z "$want" ] || [ "$have" = "$want" ] || echo "WARN: Node.js ${have:-not found}, .nvmrc pins major $want"

echo "== 1/7 commit hygiene (AGENTS.md rules 4 and 9)"
base="${LOT_BASE:-}"
if [ -z "$base" ]; then
  up=$(git remote -v | awk '$2 ~ /john30\// {print $1; exit}')
  for ref in upstream/master upstream/main ${up:+"$up/master" "$up/main"}; do
    git rev-parse -q --verify "$ref^{commit}" >/dev/null && { base="$ref"; break; }
  done
fi
if [ -z "$base" ] || ! git rev-parse -q --verify "$base^{commit}" >/dev/null; then
  echo "lot branch: FAIL, no upstream ref (git fetch upstream, or set LOT_BASE)"; fail=1
else
  git rev-list "$base..HEAD" | hygiene "lot branch ($base..HEAD)" "$CFG" yes || fail=1
fi
# This repository: every commit not yet pushed, with its added lines, and the last pushed ones.
wb=main; git -C "$ROOT" rev-parse -q --verify origin/main >/dev/null && wb=origin/main
if [ "$wb" = origin/main ]; then
  git -C "$ROOT" rev-list origin/main..HEAD | hygiene "workbench (origin/main..HEAD)" "$ROOT" yes || fail=1
fi
git -C "$ROOT" rev-list -n "${HYGIENE_LAST:-20}" HEAD | hygiene "workbench (last ${HYGIENE_LAST:-20})" "$ROOT" no || fail=1
if [ "$only" = hygiene ]; then
  [ "$fail" -eq 0 ] && echo "HYGIENE PASSED" || echo "HYGIENE FAILED"
  exit "$fail"
fi

echo "== 2/7 src/$LOT holds only .tsp and .yaml"
extra=$(find "src/$LOT/" -type f ! -name '*.tsp' ! -name '*.yaml')
if [ -n "$extra" ]; then echo "FAIL:"; echo "$extra"; fail=1; else echo "ok"; fi

echo "== 3/7 format"
if npx tsp format --check "src/$LOT/*.tsp" >"$OUT/format.log" 2>&1; then echo "ok"
else echo "FAIL: $(grep -oE '[0-9]+ need format' "$OUT/format.log" | head -1), see out/format.log (fix: npx tsp format \"src/$LOT/*.tsp\"; on Windows check core.autocrlf=false first)"; fail=1; fi

echo "== 4/7 compile"
rm -rf "$OUT/csv"
if npx tsp compile src/main.tsp --emit @ebusd/ebus-typespec \
     --option @ebusd/ebus-typespec.withMinMax=true --output-dir "$OUT/csv" >"$OUT/compile.log" 2>&1 \
   && ! grep -qE '^(warning|error) |Found [0-9]+ (warning|error)' "$OUT/compile.log"; then echo "ok"
else echo "FAIL: see out/compile.log"; tail -5 "$OUT/compile.log"; fail=1; fi

csv="$OUT/csv/@ebusd/ebus-typespec"
mode="${CHECKCONFIG:-}"
[ -n "$mode" ] || { docker info >/dev/null 2>&1 && mode=local || mode=actions; }
echo "== 5/7 ebusd --checkconfig ($FORK $RELEASE, $mode)"
count=""
if checkconfig "$csv" checkconfig; then
  count=$(grep -o 'found messages: [0-9]*' "$OUT/checkconfig.log" | tail -1)
  echo "${count:-ok}"
else echo "FAIL: see out/checkconfig.log"; tail -5 "$OUT/checkconfig.log" 2>/dev/null; fail=1; fi

echo "== 6/7 translations"
rm -rf "$OUT"/csv.?? "$OUT"/cfg.?? "$OUT"/checkconfig.??.log
found=0
for y in src/??.yaml; do
  [ -f "$y" ] || continue
  lang=$(basename "$y" .yaml)
  [ "$lang" = en ] && continue
  found=1
  # A translation file the base ref does not have belongs to the fork: its keys must all match.
  strict=--strict
  [ -n "$base" ] && git cat-file -e "$base:$y" 2>/dev/null && strict=""
  rep=$(python3 "$ROOT/scripts/i18n-keys.py" "$csv" check "$y" $strict) || { echo "$rep"; fail=1; continue; }
  echo "$rep"
  case "$rep" in *" keys, 0 for the "*) continue ;; esac
  if ! { npx tsp compile src/main.tsp --emit @ebusd/ebus-typespec \
           --option @ebusd/ebus-typespec.withMinMax=true \
           --option "@ebusd/ebus-typespec.translations=$y" --output-dir "$OUT/csv.$lang" >"$OUT/compile.$lang.log" 2>&1 \
         && ! grep -qE '^(warning|error) |Found [0-9]+ (warning|error)' "$OUT/compile.$lang.log"; }; then
    echo "$lang: FAIL: see out/compile.$lang.log"; tail -5 "$OUT/compile.$lang.log"; fail=1; continue
  fi
  python3 "$ROOT/scripts/i18n-keys.py" "$csv" compare "$OUT/csv.$lang/@ebusd/ebus-typespec" | sed "s/^/$lang: /"
  [ "${PIPESTATUS[0]}" -eq 0 ] || fail=1
  if checkconfig "$OUT/csv.$lang/@ebusd/ebus-typespec" "checkconfig.$lang"; then
    lcount=$(grep -o 'found messages: [0-9]*' "$OUT/checkconfig.$lang.log" | tail -1)
    if [ "$lcount" = "$count" ]; then echo "$lang: ${lcount:-ok}, as in English"
    else echo "$lang: FAIL: ${lcount:-no count}, English has ${count:-none}"; fail=1; fi
  else echo "$lang: FAIL: see out/checkconfig.$lang.log"; tail -5 "$OUT/checkconfig.$lang.log" 2>/dev/null; fail=1; fi
done
[ "$found" -eq 1 ] || echo "ok (no translation file)"

echo "== 7/7 metadata"
if [ -f metadata/weishaupt.toml ]; then
  python3 "$ROOT/scripts/metadata.py" check metadata/weishaupt.toml "$csv" || fail=1
elif [ "${METADATA:-}" = required ]; then
  echo "FAIL: no metadata/weishaupt.toml on this branch"; fail=1
else echo "ok (no metadata file on this branch)"; fi

[ "$fail" -eq 0 ] && echo "ALL CHECKS PASSED" || echo "CHECKS FAILED"
exit "$fail"
