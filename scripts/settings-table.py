#!/usr/bin/env python3
"""Markdown table of the settings ebusd can write with these definitions, for the release notice.
Sends nothing.

  scripts/settings-table.py <weishaupt-metadata-<version>.json>   > table.md

One row per message name and range: the circuits that carry it, the values it takes (range or
value list), the step, the unit and the source address the devices take it from. A range that
only the metadata holds (the CSV cannot carry a fractional bound on an integer register) is
marked with an asterisk: ebusd does not enforce it. A setting without a range is marked "none":
its values have no established meaning. Program slots and the date and time broadcast are left
out. The output goes into docs/release-readme.md between the lines SETTINGS-TABLE-BEGIN and
SETTINGS-TABLE-END.
"""
import json
import sys


def num(x):
    return f"{x:g}"


def row_of(m):
    f = next(f for f in m["fields"] if not f.get("skip"))
    w = m["write"]
    if f.get("values"):
        values = ", ".join(f["values"][k] for k in sorted(f["values"], key=int))
        return values, "", "", w["source"]
    if "min" in f and "max" in f:
        rng = f"{num(f['min'])} to {num(f['max'])}"
        step = f.get("step", 1 / f.get("divisor", 1))
    elif "min" in w and "max" in w:
        rng = f"{num(w['min'])} to {num(w['max'])} *"
        step = w.get("step", 1 / f.get("divisor", 1))
    else:
        return "none", "", f.get("unit", ""), w["source"]
    return rng, num(step), f.get("unit", ""), w["source"]


def table(data):
    msgs = data["messages"]
    msgs = list(msgs.values()) if isinstance(msgs, dict) else msgs
    rows = {}
    for m in msgs:
        if "write" not in m or m.get("kind") != "setting" or m["circuit"] == "broadcast":
            continue
        key = (m["name"],) + row_of(m)
        rows.setdefault(key, []).append(m["circuit"])
    order = {c: i for i, c in enumerate(["ka", "em1", "em2", "em3", "fs1", "fs2", "fs3"])}
    lines = ["| Circuits | Message | Values | Step | Unit | Source |", "|---|---|---|---|---|---|"]
    for key in sorted(rows, key=lambda k: (min(order.get(c, 99) for c in rows[k]), k[0])):
        name, values, step, unit, source = key
        circuits = ", ".join(sorted(rows[key], key=lambda c: order.get(c, 99)))
        lines.append(f"| {circuits} | `{name}` | {values} | {step} | {unit} | `{source}` |")
    count = sum(len(c) for c in rows.values())
    return "\n".join(lines) + "\n", count


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    with open(sys.argv[1], encoding="utf-8") as f:
        text, count = table(json.load(f))
    sys.stdout.write(text)
    print(f"# {count} settings", file=sys.stderr)


if __name__ == "__main__":
    main()
