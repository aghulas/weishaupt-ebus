#!/usr/bin/env python3
"""Lists the comment strings of the lot files and compares them with a translation file.

  scripts/i18n-keys.py <english csv tree> list
  scripts/i18n-keys.py <english csv tree> check <translation.yaml> [--strict] [--missing]
  scripts/i18n-keys.py <english csv tree> compare <translated csv tree>

<english csv tree> is the folder a compile without translations wrote, the one that holds
broadcast.csv and the lot folder (out/csv/@ebusd/ebus-typespec after scripts/check.sh).

The lot files are those named with the identification of the devices, ZZ.w.<circuit>.csv, and
broadcast.csv, in the lot folder (LOT_DIR, default wolf). The strings are the message comments
and the field comments of these files, as the emitter looks them up: whole string, exact,
without the "[WCRC] " marker it puts in front after translation. In broadcast.csv only the
messages of the lots count (LOT_BROADCAST, default KaStatus and Datetime): the others are the Wolf messages
of the official configuration, which stay in English.

check prints the coverage (strings with a key, strings without) and the keys of the file that
match no comment of the whole tree. With --strict, such a key is an error (exit 1): it is a
comment that changed or went away. Without it, keys that match another file of the tree are
reported apart: keys are global, a shared translation file may hold them (de.yaml of upstream).

compare checks that a tree compiled with a translation file differs from the English one only
in the comments: same files, same lines, every other column identical, the "[WCRC] " marker
kept. It prints how many lines of the lot files changed.
"""
import csv
import glob
import os
import re
import sys

LOT = os.environ.get("LOT_DIR", "wolf")
LOT_BROADCAST = set(os.environ.get("LOT_BROADCAST", "KaStatus Datetime").split())
MARKER = "[WCRC] "
KEY_RE = re.compile(r"""^(?:"((?:[^"\\]|\\.)*)"|'((?:[^']|'')*)'|([^#'"].*?))\s*:(?:\s+(.*))?$""")


def comments(path, only=None):
    """Message and field comments of one CSV file, in order; of the named messages if given."""
    out = []
    with open(path, newline="", encoding="utf-8") as f:
        rows = list(csv.reader(f))
    for row in rows[1:]:
        if not row or row[0].startswith(("*", "#")) or len(row) < 9:
            continue
        if only is not None and row[3] not in only:
            continue
        cells = [row[4]] + row[15::7]
        for c in cells:
            c = c.strip()
            if c.startswith(MARKER):
                c = c[len(MARKER):]
            if c:
                out.append(c)
    return out


def lot_files(tree):
    files = glob.glob(os.path.join(tree, LOT, "??.w.*.csv"))
    return sorted(files + glob.glob(os.path.join(tree, LOT, "broadcast.csv"))) if files else []


def lot_comments(tree):
    """Comments of the lot files; of broadcast.csv, those of the messages of the lots only."""
    out = []
    for f in lot_files(tree):
        out += comments(f, LOT_BROADCAST if os.path.basename(f) == "broadcast.csv" else None)
    return out


def tree_files(tree):
    return sorted(glob.glob(os.path.join(tree, "**", "*.csv"), recursive=True))


def keys(path):
    """Keys of a flat YAML map, in order, with value and line number. No YAML library needed:
    one "key: value" per line, key plain or quoted; indented lines continue the value above."""
    out = []
    with open(path, encoding="utf-8") as f:
        for n, line in enumerate(f, 1):
            line = line.rstrip("\n")
            if not line.strip() or line.lstrip().startswith("#") or line[0] in " \t":
                continue
            m = KEY_RE.match(line)
            if not m:
                sys.exit(f"{path}:{n}: not a 'key: value' line: {line}")
            if m.group(1) is not None:
                k = re.sub(r"\\(.)", r"\1", m.group(1))
            elif m.group(2) is not None:
                k = m.group(2).replace("''", "'")
            else:
                k = m.group(3)
            out.append((k, m.group(4) or "", n))
    return out


def compare(tree, other):
    a = {os.path.relpath(f, tree) for f in tree_files(tree)}
    b = {os.path.relpath(f, other) for f in tree_files(other)}
    bad = [f"only in one tree: {f}" for f in sorted(a ^ b)]
    lot = {os.path.relpath(f, tree) for f in lot_files(tree)}
    changed = total = 0
    for rel in sorted(a & b):
        with open(os.path.join(tree, rel), newline="", encoding="utf-8") as f:
            ra = list(csv.reader(f))
        with open(os.path.join(other, rel), newline="", encoding="utf-8") as f:
            rb = list(csv.reader(f))
        if len(ra) != len(rb):
            bad.append(f"{rel}: {len(ra)} lines in English, {len(rb)} translated")
            continue
        for n, (x, y) in enumerate(zip(ra, rb), 1):
            if x == y:
                total += rel in lot
                continue
            data = n > 1 and x and not x[0].startswith(("*", "#")) and len(x) >= 9
            where = {4} | set(range(15, max(len(x), len(y)), 7)) if data else set()
            if len(x) != len(y) or any(p != q and i not in where for i, (p, q) in enumerate(zip(x, y))):
                bad.append(f"{rel}:{n}: differs outside the comment columns")
            elif any(x[i].startswith(MARKER) != y[i].startswith(MARKER) for i in where if i < len(x)):
                bad.append(f"{rel}:{n}: {MARKER.strip()} marker lost or added")
            elif any(bool(x[i]) != bool(y[i]) for i in where if i < len(x)):
                bad.append(f"{rel}:{n}: a comment appeared or went away")
            if rel in lot:
                total += 1
                changed += 1
    if bad:
        print(f"compare: FAIL, {len(bad)} differences")
        for line in bad[:20]:
            print(f"  {line}")
        sys.exit(1)
    print(f"compare: ok, {len(a)} files, same lines, only comments differ "
          f"({changed} of {total} lines of the lot files translated)")


def with_stop(strings):
    """The emitter also matches a key without its final full stop."""
    s = set(strings)
    return s | {x[:-1] for x in s if x.endswith(".")}


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    flags = {a for a in sys.argv[1:] if a.startswith("--")}
    if len(args) < 2 or args[1] not in ("list", "check", "compare") or (args[1] != "list" and len(args) < 3):
        sys.exit(__doc__)
    tree = args[0]
    if args[1] == "compare":
        return compare(tree, args[2])
    files = lot_files(tree)
    if not files:
        sys.exit(f"no {LOT}/??.w.*.csv under {tree}")
    lot = lot_comments(tree)
    distinct = sorted(set(lot))
    if args[1] == "list":
        print("\n".join(distinct))
        return
    pairs = keys(args[2])
    name = os.path.basename(args[2])
    seen, dup = set(), []
    for k, _, n in pairs:
        if k in seen:
            dup.append(f"{n}: {k}")
        seen.add(k)
    have = with_stop(seen)
    everything = set()
    for f in tree_files(tree):
        everything |= set(comments(f))
    missing = [s for s in distinct if s not in have]
    inlot = [k for k in seen if k in set(distinct) or k + "." in set(distinct)]
    nowhere = sorted(k for k in seen if k not in everything and k + "." not in everything)
    elsewhere = len(seen) - len(inlot) - len(nowhere)
    print(f"{name}: {len(seen)} keys, {len(inlot)} for the {len(distinct)} comment strings of "
          f"the lot files, {len(missing)} strings without a key"
          + (f", {elsewhere} keys of other files" if elsewhere else ""))
    if "--missing" in flags:
        for s in missing:
            print(f"  no key: {s}")
    bad = 0
    if dup:
        print(f"{name}: FAIL, {len(dup)} duplicate keys"); bad = 1
        for d in dup:
            print(f"  line {d}")
    if nowhere and "--strict" in flags:
        print(f"{name}: FAIL, {len(nowhere)} keys match no comment"); bad = 1
        for k in nowhere:
            print(f"  {k}")
    elif nowhere:
        print(f"{name}: {len(nowhere)} keys match no comment of the tree (not checked: shared file)")
    sys.exit(bad)


if __name__ == "__main__":
    main()
