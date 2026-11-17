#!/usr/bin/env bash
# Rebuilds the integration branch of the configuration fork from the lot branches, then checks it.
# The branch is never edited by hand: change a lot branch, restack, and run this again.
#
#   scripts/integrate.sh            rebuild and check
#   scripts/integrate.sh build      rebuild only
#
# The lots are stacked, each on the previous one (STACK, bottom to top). The integration branch
# is the top of the stack; the script refuses to move it when the stack is not linear, that is
# when a lot does not contain the lot below it (rebase it first).
#
# INTEGRATION  name of the integration branch (default: weishaupt)
# STACK        lot branches, bottom to top
# TYPESPEC     built checkout of the library that provides @wcrc (default: repos/ebus-typespec);
#              lot C needs it as long as no released library has the decorator
# The check runs in a separate worktree, out/integration; the checkout of the clone is not touched.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CFG="${CFG_REPO:-$ROOT/repos/ebusd-configuration}"
BRANCH="${INTEGRATION:-weishaupt}"
STACK="${STACK:-weishaupt-A weishaupt-E weishaupt-D weishaupt-F weishaupt-C}"
LIB="${TYPESPEC:-$ROOT/repos/ebus-typespec}"
WT="$ROOT/out/integration"
only="${1:-}"

cd "$CFG"
below=upstream/master
for lot in $STACK; do
  if ! git merge-base --is-ancestor "$below" "$lot"; then
    echo "$lot does not contain $below: rebase it (git rebase --onto $below <old base> $lot)"; exit 1
  fi
  echo "$lot: $(git rev-parse --short "$lot"), $(git rev-list --count "$below..$lot") commit(s) on $below"
  below="$lot"
done
git worktree remove --force "$WT" 2>/dev/null || true
git worktree prune
git worktree add -q -B "$BRANCH" "$WT" "$below"
echo "$BRANCH = $(git rev-parse --short "$BRANCH") (top of the stack, $below)"
[ "$only" = build ] && exit 0

cd "$WT"
npm install --no-audit --no-fund >/dev/null 2>&1
ver=$(node -p "const p=require('$LIB/package.json'); (p.devDependencies||{})['@typespec/compiler'] || (p.peerDependencies||{})['@typespec/compiler']" | tr -d '^~')
npm install --no-save --no-audit --no-fund "$LIB" "@typespec/compiler@${TS_COMPILER:-$ver}" >/dev/null 2>&1
echo "library: $(git -C "$LIB" log -1 --format='%h %s')"
CFG_REPO="$WT" "$ROOT/scripts/check.sh"
