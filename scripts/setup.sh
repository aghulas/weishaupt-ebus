#!/usr/bin/env bash
# Clones the forks under repos/ (ignored by git) and adds the upstream remotes.
# An existing directory or symlink under repos/ is left untouched.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OWNER="${FORK_OWNER:-aghulas}"
mkdir -p "$ROOT/repos"

for name in ebusd-configuration ebusd ebus-typespec; do
  dir="$ROOT/repos/$name"
  if [ -e "$dir" ]; then echo "$name: present"; continue; fi
  if git clone "https://github.com/$OWNER/$name.git" "$dir"; then
    git -C "$dir" remote add upstream "https://github.com/john30/$name.git"
    git -C "$dir" fetch -q upstream
  else
    echo "$name: no fork at $OWNER/$name yet (fork john30/$name first)"
  fi
done

if [ -f "$ROOT/repos/ebusd-configuration/package.json" ]; then
  (cd "$ROOT/repos/ebusd-configuration" && npm install)
fi
