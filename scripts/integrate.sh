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
# LIB_PACKAGE  package of the library that provides @wcrc, pinned by one commit on top of the
#              stack (default: the release of the library fork below); lot C needs it as long
#              as no official release has the decorator. LIB_PACKAGE=none: no pin commit, and
#              the check installs the built checkout TYPESPEC (default: repos/ebus-typespec)
# LIB_COMPILER, LIB_LINTER  versions of the compiler and of the linter that package needs
# The check runs in a separate worktree, out/integration; the checkout of the clone is not touched.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CFG="${CFG_REPO:-$ROOT/repos/ebusd-configuration}"
BRANCH="${INTEGRATION:-weishaupt}"
STACK="${STACK:-weishaupt-A weishaupt-E weishaupt-D weishaupt-F weishaupt-C}"
LIB="${TYPESPEC:-$ROOT/repos/ebus-typespec}"
PKG="${LIB_PACKAGE:-https://github.com/aghulas/ebus-typespec/releases/download/v0.31.0-weishaupt.1/ebusd-ebus-typespec-0.31.0-weishaupt.1.tgz}"
COMPILER="${LIB_COMPILER:-~1.17.0}"
LINTER="${LIB_LINTER:-~0.87.0}"
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
cd "$WT"
if [ "$PKG" != none ]; then
  # One commit on top of the stack, with the dates of the commit below it: the same stack and
  # the same package always give the same integration branch.
  npm pkg set "dependencies.@ebusd/ebus-typespec=$PKG" "dependencies.@typespec/compiler=$COMPILER" \
    "devDependencies.@typespec/library-linter=$LINTER"
  d="$(git log -1 --format=%aI)"
  GIT_AUTHOR_DATE="$d" GIT_COMMITTER_DATE="$d" git commit -q -am "use the library build of the fork that has the @crc and @wcrc decorators

The register writes are defined with @wcrc, which no official release of
@ebusd/ebus-typespec has yet. Until it has, this branch installs the build
published by the fork of the library, with the compiler it needs."
fi
echo "$BRANCH = $(git rev-parse --short HEAD) (top of the stack $below$([ "$PKG" != none ] && echo ', plus the library pin'))"
[ "$only" = build ] && exit 0

npm install --no-audit --no-fund >/dev/null 2>&1
if [ "$PKG" = none ]; then
  ver=$(node -p "const p=require('$LIB/package.json'); (p.devDependencies||{})['@typespec/compiler'] || (p.peerDependencies||{})['@typespec/compiler']" | tr -d '^~')
  npm install --no-save --no-audit --no-fund "$LIB" "@typespec/compiler@${TS_COMPILER:-$ver}" >/dev/null 2>&1
  echo "library: $(git -C "$LIB" log -1 --format='%h %s')"
else
  echo "library: $(node -p "require('./node_modules/@ebusd/ebus-typespec/package.json').version") (pinned package)"
fi
CFG_REPO="$WT" "$ROOT/scripts/check.sh"
