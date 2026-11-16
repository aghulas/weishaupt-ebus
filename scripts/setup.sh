#!/usr/bin/env bash
# Clones the forks under repos/ (ignored by git) and adds the upstream remotes.
# An existing directory or symlink under repos/ is left untouched.
# Clones keep LF line endings and real symlinks (on Windows: Developer Mode must be on).
set -euo pipefail
export MSYS=winsymlinks:nativestrict

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OWNER="${FORK_OWNER:-aghulas}"
mkdir -p "$ROOT/repos"

for name in ebusd-configuration ebusd ebus-typespec; do
  dir="$ROOT/repos/$name"
  if [ -e "$dir" ]; then echo "$name: present"; continue; fi
  if git clone -c core.autocrlf=false -c core.eol=lf -c core.symlinks=true "https://github.com/$OWNER/$name.git" "$dir"; then
    git -C "$dir" remote add upstream "https://github.com/john30/$name.git"
    git -C "$dir" fetch -q upstream
  else
    echo "$name: no fork at $OWNER/$name yet (fork john30/$name first)"
  fi
done

if [ -f "$ROOT/repos/ebusd-configuration/package.json" ]; then
  (cd "$ROOT/repos/ebusd-configuration" && npm install)
  # ebus-typespec 0.29 pulls asset-emitter 0.79.3, which needs compiler 1.17: pin the pair that works.
  if (cd "$ROOT/repos/ebusd-configuration" && npm ls @ebusd/ebus-typespec 2>/dev/null | grep -q "@0.29."); then
    (cd "$ROOT/repos/ebusd-configuration" && npm install --no-save @typespec/compiler@1.12.0 @typespec/asset-emitter@0.79.1)
  fi
fi
