#!/usr/bin/env python3
"""Fixtures of a release: telegrams the evidence records hold, with the value each decodes to.

  scripts/fixtures.py check <fixtures.toml> <english csv tree> [--sidecar <sidecar.toml>]
                            [--ebusd <binary>] [--require-ebusd]
  scripts/fixtures.py build <fixtures.toml> <english csv tree> <out.json> --version V
                            --sidecar <sidecar.toml> --ebusd <binary> [--release NAME] [--commit C]

The source (evidence/fixtures.toml) is a transcription: every reading names the evidence record
it was copied from and the day of the capture, and carries the bytes as the record has them.
Nothing is invented and nothing is adjusted: a reading that does not decode to its value is a
finding about the record or about the definition.

check fails (exit 1) when a reading
  - names a message that is not in the lot files, or a record that is not under evidence/;
  - carries bytes, or a day, that its record does not have (`where = "row"`: request and
    answer on one line of the record, the row of a table; `"text"`: each somewhere in it);
  - has a request that is not the ID of the definition (read), is not to the register of the
    definition (write), or does not come from the source the definition names (passive);
  - is not recognised by ebusd as this message, or decodes to another value than `expect`;
  - carries `error` (ebusd refuses the telegram with the definitions as they are, a known
    defect) and ebusd decodes it, or refuses it for another reason.

Decoding is done by ebusd itself, not by this script: the binary given with --ebusd (the
release scripts/check.sh uses) is started without a bus, loaded with the lot files of the tree
only, and each telegram is injected (--inject=stop) and read back from its cache (`read -v`,
`find -w -d -v` for a write). ebusd says which message it took the telegram for and what every
field reads; both are compared. Without --ebusd only the structure is checked and single
16-bit registers are decoded by this script, which the output says; --require-ebusd makes the
missing binary a failure. On Linux the binary is run directly, elsewhere in Docker
(debian:trixie-slim), as scripts/check.sh does.

build runs the same check and writes the fixtures file; format in docs/companion-contract.md.

EVIDENCE_DIR  folder of the evidence records (default: evidence/ of the workbench)
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tomllib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import metadata as md  # noqa: E402

ROOT = md.ROOT
SCHEMA = 2
TYPES = {"read": "read", "write": "write", "passive": "update-read"}
HEXRE = re.compile(r"[0-9a-f]{2}( [0-9a-f]{2})*")
DATERE = re.compile(r"\d{4}-\d\d-\d\d")
NOTICE = re.compile(r"\[update notice\] received (\S+) (\S+) (\S+?)(?: QQ=([0-9a-f]{2}))?: (.*)$")
DONE = re.compile(r'\[main notice\] executed command "(.*?)": (.*)$')
REFUSED = re.compile(r"\[update error\] unable to parse (\S+) (\S+) (\S+) from [0-9a-f /]+: (.*)$")
FAILED = re.compile(r'\[main error\] executing command "(.*?)" failed: (.*)$')
# ebusd field types whose value is text, not a number
TEXT_TYPES = ("HEX", "STR", "NTS", "BDA", "BTI", "HDA", "HTI", "HTM", "VTI", "VTM", "MIN", "TTM", "TTH", "TTQ",
              "BDY", "HDY", "PIN", "DAY")
NA = "-"  # ebusd prints this for a replacement value


def load(path):
    """Readings of the source, the keys of their block filled in."""
    with open(path, "rb") as f:
        doc = tomllib.load(f)
    if doc.get("schema") != SCHEMA:
        sys.exit(f"{os.path.basename(path)}: schema is {doc.get('schema')}, this script knows {SCHEMA}")
    out = []
    for b, block in enumerate(doc.get("block", []), 1):
        common = {k: v for k, v in block.items() if k != "readings"}
        for r in block.get("readings", []):
            item = dict(common)
            item.update(r)
            item["block"] = b
            out.append(item)
    return out


def record_lines(name, cache={}):
    """Lines of an evidence record, table bars and code marks removed."""
    if name not in cache:
        p = os.path.join(md.EVIDENCE, name + ".md")
        if not os.path.exists(p):
            cache[name] = None
        else:
            with open(p, encoding="utf-8") as f:
                cache[name] = [re.sub(r"\s+", " ", re.sub(r"[`|]", " ", line)).strip() for line in f]
    return cache[name]


def holds(text, hexbytes):
    """The bytes are in the text, written with or without spaces, not inside a longer run."""
    for form in (hexbytes, hexbytes.replace(" ", "")):
        if re.search(rf"(?<![0-9a-f]){re.escape(form)}(?![0-9a-f])", text):
            return True
    return False


def nn(hexbytes):
    return f"{len(hexbytes.split()):02x}" + hexbytes.replace(" ", "")


def structure(readings, msgs):
    """Checks that need no ebusd. Returns the readings completed (zz, pbsb, telegram) and problems."""
    bad, items = [], []
    for n, r in enumerate(readings, 1):
        key = f"{r.get('circuit')}/{r.get('message')}"
        where = f"reading {n} ({key}, block {r['block']})"
        m = msgs.get(key)
        if m is None:
            bad.append(f"{where}: no such message in the lot files"); continue
        typ = r.get("type", "read")
        if typ not in TYPES:
            bad.append(f"{where}: type must be one of {', '.join(TYPES)}"); continue
        master, slave = r.get("master", ""), r.get("slave")
        if not HEXRE.fullmatch(master) or (slave not in (None, "") and not HEXRE.fullmatch(slave)):
            bad.append(f"{where}: master and slave are lists of hex bytes"); continue
        expect = r.get("expect", {})
        if not isinstance(expect, dict) or bool(expect) == ("error" in r):
            bad.append(f"{where}: needs expect, or error when ebusd refuses the telegram"); continue
        if not DATERE.fullmatch(str(r.get("date", ""))):
            bad.append(f"{where}: date is the day of the capture, YYYY-MM-DD"); continue
        lines = record_lines(r.get("evidence", ""))
        if lines is None:
            bad.append(f"{where}: evidence record '{r.get('evidence')}' not found"); continue
        text = " ".join(lines)
        parts = [b for b in (master, slave) if b]
        if r.get("where", "text") == "row":
            if not any(all(holds(line, b) for b in parts) for line in lines):
                bad.append(f"{where}: no line of evidence/{r['evidence']}.md holds {' and '.join(parts)}")
        elif r.get("where", "text") == "text":
            for b in parts:
                if not holds(text, b):
                    bad.append(f"{where}: the bytes {b} are not in evidence/{r['evidence']}.md")
        else:
            bad.append(f"{where}: where must be row or text")
        if r["date"] not in text:
            bad.append(f"{where}: evidence/{r['evidence']}.md does not name the day {r['date']}")
        kind = {"read": "r", "write": "w", "passive": "u"}[typ]
        if kind not in m["ids"]:
            bad.append(f"{where}: the lot has no {typ} line for this message"); continue
        pbsb, mid = m["ids"][kind][:4], m["ids"][kind][4:]
        qq = str(r.get("qq", "31" if typ == "read" else "")).lower()
        if not re.fullmatch(r"[0-9a-f]{2}", qq):
            bad.append(f"{where}: qq, the source address of the telegram, is needed"); continue
        if m["qq"] and qq != m["qq"]:
            bad.append(f"{where}: the definition takes this message from {m['qq']}, not from {qq}")
        flat = master.replace(" ", "")
        if typ == "read":
            if flat != mid:
                bad.append(f"{where}: master is not the ID of the definition ({mid})")
            if not slave:
                bad.append(f"{where}: a read needs the answer (slave)")
        elif typ == "write":
            # the first ID byte of a written register is a checksum over address and value
            if flat[2:len(mid)] != mid[2:]:
                bad.append(f"{where}: master is not a write to the register of the definition ({mid[2:]})")
            slave = slave or ""
        elif not flat.startswith(mid):
            bad.append(f"{where}: master does not start with the ID of the definition ({mid})")
        fields = {f["name"]: f for f in m["fields"] if not f["type"].startswith("IGN")}
        for name in expect:
            if name not in fields:
                bad.append(f"{where}: field {name} is not in the message")
        telegram = qq + m["zz"] + pbsb + nn(master)
        telegram += "/" + (nn(slave) if slave is not None else "")  # no slave part: sent to a master or to all
        item = {"n": n, "where": where, "key": key, "circuit": r["circuit"], "message": r["message"], "type": typ,
                "qq": qq, "zz": m["zz"], "pbsb": pbsb, "master": master, "slave": slave, "telegram": telegram,
                "expect": expect, "evidence": r["evidence"], "date": r["date"], "fields": fields}
        for k in ("case", "note", "error"):
            if k in r:
                item[k] = r[k]
        items.append(item)
    return items, bad


def typed(text, field):
    """A value as ebusd prints it, as a JSON value: null, a number, or the text."""
    if text == NA:
        return None
    if "values" in field or field["type"].split(":")[0] in TEXT_TYPES:
        return text
    try:
        return int(text)
    except ValueError:
        try:
            return float(text)
        except ValueError:
            return text


def agrees(want, got):
    """expect against what ebusd decoded. A number of the record is compared at the precision
    the record gives it (11.3 agrees with 11.301); "-" in the source is the replacement value."""
    if want == NA:
        return got is None
    if isinstance(want, bool) or got is None:
        return False
    if isinstance(want, int):
        return isinstance(got, (int, float)) and got == want
    if isinstance(want, float):
        if not isinstance(got, (int, float)):
            return False
        text = repr(want)
        return round(got, len(text.split(".")[1]) if "." in text else 0) == want
    return got == want


def run_ebusd(binary, tree, args):
    """Starts ebusd without a bus on the lot files of the tree and injects args. Returns its log."""
    cfg = os.path.join(ROOT, "out", "cfg.fixtures")
    shutil.rmtree(cfg, ignore_errors=True)
    os.makedirs(os.path.join(cfg, md.LOT))
    for name in os.listdir(tree):
        if name.endswith(".csv"):
            shutil.copy(os.path.join(tree, name), cfg)
    lot = os.path.join(tree, md.LOT)
    for name in os.listdir(lot):
        if re.fullmatch(r"..\.w\..*\.csv|broadcast\.csv", name):
            shutil.copy(os.path.join(lot, name), os.path.join(cfg, md.LOT))
    opts = ["-f", "--scanconfig=off", "-d", "/dev/null", "--inject=stop", "--log=all:notice"]
    binary = os.path.abspath(binary)
    if sys.platform.startswith("linux") and os.access(binary, os.X_OK):
        cmd = [binary, f"--configpath={cfg}"] + opts
    else:
        cmd = ["docker", "run", "--rm", "-v", f"{binary}:/ebusd:ro", "-v", f"{cfg}:/cfg:ro",
               "debian:trixie-slim", "/ebusd", "--configpath=/cfg"] + opts
    out = ""
    for i in range(0, len(args), 200):  # two arguments per reading
        p = subprocess.run(cmd + args[i:i + 200], capture_output=True, text=True, timeout=300)
        out += p.stdout + p.stderr
    return out


def decode(items, binary, tree):
    """Has ebusd decode every telegram. Fills decoded and text; returns problems."""
    args = []
    for it in items:
        if it["type"] == "write":
            query = f"find -w -e -d -v -c {it['circuit']} {it['message']}"
        else:
            query = f"read -m 1000 -v -c {it['circuit']} {it['message']}"
        it["query"] = query
        args += [it["telegram"], query]
    log = run_ebusd(binary, tree, args)
    bad, pos, seen = [], 0, None
    for line in log.splitlines():
        if pos >= len(items):
            break
        it = items[pos]
        m = NOTICE.search(line)
        if m:
            seen = m.groups(); continue
        m = REFUSED.search(line)
        if m:
            seen = ("error",) + m.groups(); continue
        m = FAILED.search(line)
        if m and m.group(1) == it["telegram"]:
            bad.append(f"{it['where']}: ebusd does not take the telegram {it['telegram']}: {m.group(2)}")
            seen = "refused"; continue
        if m and m.group(1) == it["query"]:
            if seen and seen[0] == "error":
                same = (seen[1], seen[2].lower(), seen[3]) == (TYPES[it["type"]], it["circuit"].lower(), it["message"])
                if "error" not in it:
                    bad.append(f"{it['where']}: ebusd cannot decode the telegram {it['telegram']}: {seen[4]}")
                elif not same or it["error"] not in seen[4]:
                    bad.append(f"{it['where']}: ebusd refuses {seen[1]} {seen[2]} {seen[3]} with '{seen[4]}', "
                               f"the reading says '{it['error']}'")
                else:
                    it["error"] = seen[4]
            elif seen != "refused":
                bad.append(f"{it['where']}: ebusd has no value after {it['telegram']}: {m.group(2)}"
                           + ("" if seen else " (telegram not recognised as a message)"))
            pos, seen = pos + 1, None; continue
        m = DONE.search(line)
        if not (m and m.group(1) == it["query"]):
            continue
        pos += 1
        got, seen = seen, None
        if not got or got == "refused":
            bad.append(f"{it['where']}: ebusd did not recognise the telegram {it['telegram']}"); continue
        if "error" in it:
            bad.append(f"{it['where']}: ebusd decodes the telegram, the reading says it refuses it "
                       f"('{it['error']}'): the defect is gone, give the reading its expect"); continue
        if (got[0], got[1].lower(), got[2]) != (TYPES[it["type"]], it["circuit"].lower(), it["message"]):
            bad.append(f"{it['where']}: ebusd takes the telegram for {got[0]} {got[1]} {got[2]}"); continue
        body = m.group(2).split(" ", 2)[2]
        body = body[2:] if body.startswith("= ") else body
        pairs = [p.split("=", 1) for p in body.split(";")]
        names = [p[0] for p in pairs]
        if names != list(it["fields"]) or any(len(p) != 2 for p in pairs):
            bad.append(f"{it['where']}: ebusd gives the fields {', '.join(names)}, the CSV has {', '.join(it['fields'])}")
            continue
        it["text"] = ";".join(p[1] for p in pairs)
        if it["text"] != got[4]:
            bad.append(f"{it['where']}: ebusd decoded '{got[4]}' on reception and reads back '{it['text']}'"); continue
        it["decoded"] = {k: typed(v, it["fields"][k]) for k, v in pairs}
        for name, want in it["expect"].items():
            if name in it["decoded"] and not agrees(want, it["decoded"][name]):
                bad.append(f"{it['where']}: {name} decodes to {pairs[names.index(name)][1]}, "
                           f"evidence/{it['evidence']}.md says {want}")
    if pos < len(items):
        bad.append(f"ebusd answered for {pos} of {len(items)} readings; end of its log:\n    "
                   + "\n    ".join(log.splitlines()[-5:]))
    return bad


def decode16(items):
    """Without ebusd: single 16-bit registers only, decoded by this script. Returns problems."""
    bad, done = [], 0
    for it in items:
        if "error" in it:
            continue
        fields = list(it["fields"].values())
        raw = it["slave"] if it["type"] == "read" else " ".join(it["master"].split()[3:5]) if it["type"] == "write" else ""
        if len(fields) != 1 or fields[0]["type"] not in ("UIN", "SIN") or "values" in fields[0] or len(raw.split()) != 2:
            continue
        lo, hi = (int(x, 16) for x in raw.split())
        v = lo | hi << 8
        f = fields[0]
        if v == (0x8000 if f["type"] == "SIN" else 0xffff):
            got = None
        else:
            if f["type"] == "SIN" and v >= 0x8000:
                v -= 0x10000
            d = f.get("divisor", 1)
            got = v / d if d > 0 else v * -d
        done += 1
        want = it["expect"].get(f["name"])
        if want is not None and not agrees(want, got):
            bad.append(f"{it['where']}: {f['name']} decodes to {got} (this script), the record says {want}")
    return bad, done


def coverage(items, msgs, resolved):
    """Messages with a reading against all messages, by kind and by device."""
    covered = {it["key"] for it in items}
    by_kind, by_device = {}, {}
    for key in msgs:
        r = resolved.get(key)
        kind, dev = (r["e"].get("kind", "?"), r["device"]) if r else ("?", "?")
        for table, k in ((by_kind, kind), (by_device, dev)):
            t = table.setdefault(k, {"messages": 0, "covered": 0})
            t["messages"] += 1
            t["covered"] += key in covered
    decodes = {it["key"] for it in items if "error" not in it}
    return {"messages": len(msgs), "covered": len(covered & set(msgs)), "readings": len(items),
            "by_kind": by_kind, "by_device": by_device,
            "not_covered": [k for k in msgs if k not in covered],
            "refused_by_ebusd": sorted(covered - decodes)}


def main():
    pos, opt = md.args_of([a for a in sys.argv[1:] if a != "--require-ebusd"])
    require = "--require-ebusd" in sys.argv
    if len(pos) < 3 or pos[0] not in ("check", "build") or (pos[0] == "build" and (
            len(pos) < 4 or not all(k in opt for k in ("version", "sidecar", "ebusd")))):
        sys.exit(__doc__)
    name = os.path.relpath(os.path.abspath(pos[1]), ROOT)
    msgs, _, _ = md.read_tree(pos[2])
    items, bad = structure(load(pos[1]), msgs)
    binary = opt.get("ebusd", [None])[0]
    how = ""
    if not bad:
        if binary and os.path.exists(binary):
            bad = decode(items, binary, pos[2])
            how = f"decoded by ebusd {opt.get('release', [os.path.basename(binary)])[0]}"
        elif require or pos[0] == "build":
            bad = [f"no ebusd binary ({binary}): the readings were not decoded"]
        else:
            bad, done = decode16(items)
            how = f"NOT decoded by ebusd (no binary): {done} single registers decoded by this script, the others unchecked"
    if bad:
        print(f"{name}: FAIL, {len(bad)} problems")
        for b in bad[:40]:
            print(f"  {b}")
        if len(bad) > 40:
            print(f"  ... and {len(bad) - 40} more")
        sys.exit(1)
    resolved = {}
    if "sidecar" in opt:
        side = md.load(opt["sidecar"][0])
        resolved, sbad = md.resolve(side, msgs)
        if sbad:
            sys.exit(f"{opt['sidecar'][0]}: {len(sbad)} problems, run scripts/metadata.py check")
    cov = coverage(items, msgs, resolved)
    print(f"{name}: ok, {cov['readings']} readings of {cov['covered']} messages out of {cov['messages']}, {how}")
    if resolved:
        for title, table in (("kind", cov["by_kind"]), ("device", cov["by_device"])):
            print(f"  by {title}: " + ", ".join(f"{k} {v['covered']}/{v['messages']}" for k, v in table.items()))
    if cov["refused_by_ebusd"]:
        print(f"  KNOWN DEFECT, ebusd refuses every recorded telegram of: {', '.join(cov['refused_by_ebusd'])}")
    if cov["not_covered"]:
        print(f"  no reading: {', '.join(cov['not_covered'][:12])}"
              + (f" and {len(cov['not_covered']) - 12} more" if len(cov["not_covered"]) > 12 else ""))
    if pos[0] == "check":
        return
    out = []
    for it in items:
        o = {k: it[k] for k in ("circuit", "message", "type", "qq", "zz", "pbsb", "master")}
        if it["slave"] is not None:
            o["slave"] = it["slave"]
        o["telegram"] = it["telegram"]
        o["device"] = resolved[it["key"]]["device"]
        if "error" in it:
            o["error"] = it["error"]
        else:
            o["expect"] = {k: (None if v == NA else v) for k, v in it["expect"].items()}
            o["decoded"], o["text"] = it["decoded"], it["text"]
        for k in ("evidence", "date", "case", "note"):
            if k in it:
                o[k] = it[k]
        out.append(o)
    doc = {
        "schema": SCHEMA,
        "definitions": {"version": opt["version"][0], "commit": opt.get("commit", [None])[0],
                        "messages": len(msgs)},
        "verified": {"by": "ebusd", "release": opt.get("release", [os.path.basename(binary)])[0],
                     "loaded": "lot files only, no scan"},
        "coverage": cov,
        "readings": out,
    }
    with open(pos[3], "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print(f"fixtures: {os.path.relpath(pos[3], ROOT)}, schema {SCHEMA}")


if __name__ == "__main__":
    main()
