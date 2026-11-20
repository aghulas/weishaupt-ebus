#!/usr/bin/env python3
"""Renders the release notice (docs/release-readme.md) for one archive. Sends nothing.

  scripts/render-notice.py <template> KEY=VALUE ... > README.md

Each @KEY@ of the template is replaced by its value. PROVISIONAL is special: a comma-separated
list of the terms still provisional (from evidence/terms.md); the token @PROVISIONAL_SENTENCE@
becomes " Still provisional: <list>." when the list is not empty, and nothing when it is, so the
notice never says "still provisional: none". A token left unreplaced is an error.
"""
import re
import sys


def render(template, values):
    provisional = values.pop("PROVISIONAL", "").strip()
    out = template.replace("@PROVISIONAL_SENTENCE@",
                           f" Still provisional: {provisional}." if provisional else "")
    for key, value in values.items():
        out = out.replace(f"@{key}@", value)
    left = sorted(set(re.findall(r"@[A-Z_]+@", out)))
    if left:
        raise ValueError(f"tokens left unreplaced: {', '.join(left)}")
    return out


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    values = dict(arg.split("=", 1) for arg in sys.argv[2:])
    with open(sys.argv[1], encoding="utf-8") as f:
        sys.stdout.write(render(f.read(), values))


if __name__ == "__main__":
    main()
