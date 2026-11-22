#!/usr/bin/env python3
"""Cross the register survey results with the vendor-software catalogue. Sends nothing.

Usage: scripts/survey-crosscheck.py <results.csv> [evidence/register-candidates.csv]

Prints markdown: per device type, each `register` row of the catalogue that is on the
installation (status `on-installation`) with what the survey answered (not surveyed yet, `00 80`,
answers within the catalogue's range, answers outside it), then the registers that answered
something other than `00 80` and have no catalogue row. Boiler rows of the catalogue are memory
reads (`50 00`), not registers: the boilers are listed by register only.
"""
import csv, sys, collections

SURVEYED = {"system manager (KA)": "15", "room unit FS 2.0 with its modules": "35"}
MODULE = "51"   # the catalogue's rows read "at module" are heating-module registers


def value(raw, typ, factor):
    lo, hi = raw.split()
    v = int(hi + lo, 16)
    if typ.upper().startswith("S") and v > 32767:
        v -= 65536
    try:
        return v * float(factor or 1)
    except ValueError:
        return v


def main():
    res_path = sys.argv[1]
    cat_path = sys.argv[2] if len(sys.argv) > 2 else "evidence/register-candidates.csv"
    results = collections.defaultdict(dict)
    with open(res_path, encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            if r["status"] == "ok":
                results[r["zz"]][int(r["reg_dec"])] = r
    with open(cat_path, encoding="utf-8") as fh:
        catalogue = list(csv.DictReader(fh))
    known = collections.defaultdict(set)
    counts = collections.Counter()
    print("| Device | Register | Vendor | Meaning | Type, factor, unit, range | Survey | Value |")
    print("|---|---|---|---|---|---|---|")
    for c in catalogue:
        if c["access"] != "register" or c["device"] not in SURVEYED or not c["register"].isdigit():
            continue
        zz = MODULE if c["read_at"] == "module" else SURVEYED[c["device"]]
        reg = int(c["register"])
        known[zz].add(reg)
        if c["status"] != "on-installation":
            continue
        r = results[zz].get(reg)
        if r is None:
            state, shown = "not surveyed yet", ""
        elif r["raw"] == "00 80":
            state, shown = "`00 80`", ""
        else:
            v = value(r["raw"], c["type"], c["factor"])
            ok = all(not b or (float(b) <= v if i == 0 else v <= float(b))
                     for i, b in enumerate((c["min"], c["max"]))
                     if b.replace(".", "", 1).replace("-", "", 1).isdigit())
            state = "answers, in range" if ok else "answers, **outside the range**"
            shown = f"`{r['raw']}` = {v:g} {c['unit']}".rstrip()
        counts[(zz, state)] += 1
        rng = f"{c['min']}–{c['max']}" if c["min"] or c["max"] else ""
        print(f"| `{zz}` | `{c['bus_bytes']}` ({reg}) | {c['vendor_param']} | {c['meaning']} | "
              f"{c['type']} ×{c['factor']} {c['unit']} {rng} | {state} | {shown} |")
    print()
    print("Counts: " + "; ".join(f"`{zz}` {s}: {n}" for (zz, s), n in sorted(counts.items())))
    print()
    print("Answering registers without a catalogue row:")
    print()
    for zz in sorted(results):
        extra = [r for reg, r in sorted(results[zz].items()) if r["raw"] != "00 80" and reg not in known[zz]]
        print(f"- `{zz}` ({len(extra)}): " + ", ".join(f"`{r['reg_hex']}` `{r['raw']}`" for r in extra))


if __name__ == "__main__":
    main()
