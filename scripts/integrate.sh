#!/usr/bin/env bash
# Checks the integration branch of the configuration fork in a clean worktree (out/integration).
# The fork is trunk-based on `weishaupt`, rebased on upstream/master; upstream pull requests are
# cut on demand from it.
#
#   scripts/integrate.sh            prepare worktree and run full check
#   scripts/integrate.sh build      prepare worktree only
#
# INTEGRATION  branch to check (default: weishaupt)
# LIB_PACKAGE  default: use the @ebusd/ebus-typespec pinned in package.json of the branch.
#              LIB_PACKAGE=none: override with the local checkout TYPESPEC (default: repos/ebus-typespec).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CFG="${CFG_REPO:-$ROOT/repos/ebusd-configuration}"
BRANCH="${INTEGRATION:-weishaupt}"
LIB="${TYPESPEC:-$ROOT/repos/ebus-typespec}"
PKG="${LIB_PACKAGE:-pinned}"
WT="$ROOT/out/integration"
only="${1:-}"

cd "$CFG"
if ! git rev-parse -q --verify "$BRANCH^{commit}" >/dev/null; then
  echo "branch $BRANCH not found in $CFG"; exit 1
fi
if git rev-parse -q --verify upstream/master^{commit} >/dev/null; then
  if ! git merge-base --is-ancestor upstream/master "$BRANCH"; then
    echo "$BRANCH is not rebased on upstream/master: rebase it first"; exit 1
  fi
  echo "$BRANCH: $(git rev-parse --short "$BRANCH"), $(git rev-list --count "upstream/master..$BRANCH") commit(s) on upstream/master"
else
  echo "$BRANCH: $(git rev-parse --short "$BRANCH") (no upstream/master ref)"
fi

git worktree remove --force "$WT" 2>/dev/null || true
git worktree prune
git worktree add -q --detach "$WT" "$BRANCH"
cd "$WT"
[ "$only" = build ] && exit 0

npm install --no-audit --no-fund >/dev/null 2>&1
if [ "$PKG" = none ]; then
  ver=$(node -p "const p=require('$LIB/package.json'); (p.devDependencies||{})['@typespec/compiler'] || (p.peerDependencies||{})['@typespec/compiler']" | tr -d '^~')
  npm install --no-save --no-audit --no-fund "$LIB" "@typespec/compiler@${TS_COMPILER:-$ver}" >/dev/null 2>&1
  echo "library: $(git -C "$LIB" log -1 --format='%h %s') (local checkout)"
else
  echo "library: $(node -p "require('./node_modules/@ebusd/ebus-typespec/package.json').version") (pinned in package.json)"
fi
CFG_REPO="$WT" METADATA=required "$ROOT/scripts/check.sh"
