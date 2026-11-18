#!/usr/bin/env python3
"""Checks the metadata sidecar of the configuration fork against the compiled CSV, and builds
the metadata file of a release from both.

  scripts/metadata.py check <sidecar.toml> <english csv tree>
  scripts/metadata.py build <sidecar.toml> <english csv tree> <out.json>
                            --version V --commit C [--loaded N] [--lang fr=<csv tree>]...
  scripts/metadata.py summary <sidecar.toml> <english csv tree>

<english csv tree> is the folder a compile without translations wrote (out/csv/@ebusd/ebus-typespec
after scripts/check.sh). The messages are those of the lot files, as scripts/i18n-keys.py finds
them: ZZ.w.<circuit>.csv and, in broadcast.csv, the messages of LOT_BROADCAST.

The sidecar (metadata/weishaupt.toml on the branch on top of the stack) holds only what the CSV
does not say: devices, menus, short labels, labels of the value-list entries, kind, polling
class, write conditions, evidence. An entry names a message of one or more circuits, or a
pattern with the number of messages it must match in each circuit. The format is described in
docs/companion-contract.md.
The fixtures file of a release is made by scripts/fixtures.py, which uses read_tree and resolve.

check fails (exit 1) when
  - a message of the lot files has no entry, or more than one;
  - an entry names a message that does not exist, or a pattern does not match its count;
  - a message with several fields has a field without metadata, or metadata for a field it
    does not have;
  - a written message has no write conditions, or write conditions sit on a message that is
    not written, or its evidence does not name it;
  - an entry has no evidence record, or names a record that is not under evidence/;
  - a label lacks one of the languages, a menu or a device is unknown, the menus are not a tree;
  - an entry of a value list of the lot files has no label in every language, or a label
    names an entry no value list has, or a weekday is labelled in [values] as well as [days];
  - the sidecar repeats a range the CSV already has;
  - the status says accepted without the day of the acceptance.

The polling class of a message is the one a record establishes (`poll` on its entry); failing
that, the default the owner decided for its kind (`[poll_default]`); failing that, none.

EVIDENCE_DIR  folder of the evidence records (default: evidence/ of the workbench)
"""
import csv
import glob
import hashlib
import json
import os
import re
import sys
import tomllib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOT = os.environ.get("LOT_DIR", "wolf")
LOT_BROADCAST = set(os.environ.get("LOT_BROADCAST", "KaStatus").split())
EVIDENCE = os.environ.get("EVIDENCE_DIR", os.path.join(ROOT, "evidence"))
MARKER = "[WCRC] "
SCHEMA = 1
LANGS = ("en", "fr")
KINDS = ("live", "state", "counter", "diagnostic", "setting", "program_slot")
POLLS = ("cyclic", "on_demand")  # "passive" is derived from the message type
RISKS = ("comfort", "regulation")  # "structural" settings are never writable
PROOFS = ("captured", "change-observed", "family")
# Kinds a write may sit on: settings, and the slots of weekly programs (from 0.5.6).
WRITABLE_KINDS = ("setting", "program_slot")
# Range of a write the definitions cannot carry (a fractional bound on an integer register).
WRITE_RANGE = ("min", "max", "step")
STATUS = ("proposed", "accepted")
RANGE_RE = re.compile(r"^(-?[\d.]+)-(-?[\d.]+)(?::([\d.]+))?$")


def num(s):
    f = float(s)
    return int(f) if f == int(f) else f


def read_tree(tree):
    """Messages of the lot files: {key: message}, key = <circuit>/<name>, in file order.
    The read and the write line of a setting are one message."""
    files = sorted(glob.glob(os.path.join(tree, LOT, "??.w.*.csv")))
    if not files:
        sys.exit(f"no {LOT}/??.w.*.csv under {tree}")
    bc = os.path.join(tree, LOT, "broadcast.csv")
    if os.path.exists(bc):
        files.append(bc)
    out, lines, problems = {}, 0, []
    for path in files:
        base = os.path.basename(path)
        if base == "broadcast.csv":
            circuit, address = "broadcast", "fe"
        else:
            address, _, circuit = base[:-4].split(".", 2)
        with open(path, newline="", encoding="utf-8") as f:
            rows = list(csv.reader(f))
        for row in rows[1:]:
            if not row or row[0].startswith(("*", "#")) or len(row) < 9:
                continue
            if base == "broadcast.csv" and row[3] not in LOT_BROADCAST:
                continue
            lines += 1
            comment = row[4].strip()
            wcrc = comment.startswith(MARKER)
            if wcrc:
                comment = comment[len(MARKER):]
            fields = []
            for i in range(9, len(row), 7):
                c = (row[i:i + 7] + [""] * 7)[:7]
                if not c[0] and not c[2]:
                    continue
                fld = {"name": c[0], "type": c[2]}
                if "=" in c[3]:
                    fld["values"] = dict(p.split("=", 1) for p in c[3].split(";"))
                elif c[3]:
                    fld["divisor"] = num(c[3])
                m = RANGE_RE.match(c[4])
                if m:
                    fld["min"], fld["max"] = num(m.group(1)), num(m.group(2))
                    if m.group(3):
                        fld["step"] = num(m.group(3))
                elif c[4]:
                    problems.append(f"{base}: {row[3]}.{c[0]}: range '{c[4]}' not understood")
                if c[5]:
                    fld["unit"] = c[5]
                fld["comment"] = c[6].strip()
                fields.append(fld)
            key = f"{circuit}/{row[3]}"
            kind = row[0][0]
            msg = out.setdefault(key, {
                "circuit": circuit, "address": address, "file": base[:-4], "name": row[3],
                "comment": comment, "fields": fields, "read": False, "write": False,
                "passive": False, "wcrc": False, "ids": {},
                "qq": row[5].lower(), "zz": (row[6] or address).lower(),
            })
            msg["ids"][kind] = row[7] + row[8]
            shape = [(f["name"], f["type"]) for f in fields]
            if shape != [(f["name"], f["type"]) for f in msg["fields"]]:
                problems.append(f"{key}: read and write lines have different fields")
            if kind == "w":
                msg["write"] = True
            elif kind == "u":
                msg["passive"] = True
            else:
                msg["read"] = True
            msg["wcrc"] = msg["wcrc"] or wcrc
    return out, lines, problems


def load(path):
    """The sidecar; a field set that has `include` takes the keys of the set it names."""
    with open(path, "rb") as f:
        side = tomllib.load(f)
    sets = side.get("fields", {})
    for name, table in sets.items():
        inc = table.pop("include", None)
        if inc is not None:
            if inc not in sets or "include" in sets[inc]:
                sys.exit(f"fields.{name}: include names '{inc}', which is not a plain field set")
            for k, v in sets[inc].items():
                table.setdefault(k, v)
    return side


def has_langs(label):
    return isinstance(label, dict) and all(isinstance(label.get(x), str) and label[x].strip() for x in LANGS)


def fmt(label, groups, days):
    """A label with the groups of the pattern put in; a day token becomes the day name."""
    out = {}
    for lang in LANGS:
        g = dict(groups)
        if "day" in g:
            g["day"] = days[g["day"]][lang]
        try:
            out[lang] = label[lang].format(**g)
        except (KeyError, IndexError) as e:
            raise ValueError(f"label '{label[lang]}' uses {e}, which the pattern does not give")
    return out


def value_labels(side, msgs):
    """Labels of the value-list entries, by ebusd name: ({name: {lang: label}}, provisional
    names, problems). The weekdays come from [days], the same source as the labels of the
    program slots, with a capital; every other entry from [values]."""
    bad, labels, provisional = [], {}, []
    for d in side.get("days", {}).values():
        if has_langs(d):
            labels[d["en"]] = {lang: d[lang][:1].upper() + d[lang][1:] for lang in LANGS}
    from_days = set(labels)
    for name, v in side.get("values", {}).items():
        if not has_langs(v):
            bad.append(f"values.{name}: needs {' and '.join(LANGS)}"); continue
        extra = set(v) - set(LANGS) - {"provisional"}
        if extra or not isinstance(v.get("provisional", False), bool):
            bad.append(f"values.{name}: only {', '.join(LANGS)} and provisional = true")
        if name in from_days:
            bad.append(f"values.{name}: a weekday, its label comes from [days]"); continue
        labels[name] = {lang: v[lang] for lang in LANGS}
        if v.get("provisional"):
            provisional.append(name)
    used = {}
    for key, m in msgs.items():
        for f in m["fields"]:
            for name in f.get("values", {}).values():
                used.setdefault(name, f"{key}.{f['name']}")
    for name, where in used.items():
        if name not in labels:
            bad.append(f"value-list entry {name} ({where}): no label in [values]")
    for name in side.get("values", {}):
        if name not in used:
            bad.append(f"values.{name}: no value list of the lot files has this entry")
    return labels, sorted(provisional), bad


def group_values(groups, days):
    out = {}
    for k, v in groups.items():
        if k == "day":
            out[k] = list(days).index(v) + 1
        else:
            out[k] = int(v) if v.isdigit() else v
    return out


def resolve(side, msgs):
    """Matches entries and messages. Returns ({key: resolved metadata}, problems)."""
    bad = []
    days = side.get("days", {})
    for d, label in days.items():
        if not has_langs(label):
            bad.append(f"days.{d}: needs {' and '.join(LANGS)}")
    devices = side.get("devices", {})
    menus = side.get("menus", {})
    fieldsets = side.get("fields", {})
    status = side.get("status", {})
    if side.get("schema") != SCHEMA:
        bad.append(f"schema is {side.get('schema')}, this script knows {SCHEMA}")
    for what in ("menus", "labels", "values"):
        if status.get(what) not in STATUS:
            bad.append(f"status.{what} must be one of {', '.join(STATUS)}")
    if "accepted" in status.values() and not re.fullmatch(r"\d{4}-\d\d-\d\d", str(status.get("date", ""))):
        bad.append("status.date: the day of the acceptance, YYYY-MM-DD")
    for kind, poll in side.get("poll_default", {}).items():
        if kind not in KINDS or poll not in POLLS:
            bad.append(f"poll_default.{kind}: a kind and one of {', '.join(POLLS)}")

    circuits = {m["circuit"] for m in msgs.values()}
    device_of = {}
    for dev, d in devices.items():
        if not has_langs(d.get("label")):
            bad.append(f"devices.{dev}: label needs {' and '.join(LANGS)}")
        if d.get("type") not in menus:
            bad.append(f"devices.{dev}: no menus for type '{d.get('type')}'")
        for c in d.get("circuits", []):
            if c in device_of:
                bad.append(f"circuit {c} is in devices {device_of[c]} and {dev}")
            device_of[c] = dev
            if c not in circuits:
                bad.append(f"devices.{dev}: circuit {c} has no lot file")
    for c in sorted(circuits - set(device_of)):
        bad.append(f"circuit {c} belongs to no device")

    for typ, tree in menus.items():
        for mid, m in tree.items():
            if not has_langs(m.get("label")):
                bad.append(f"menus.{typ}.{mid}: label needs {' and '.join(LANGS)}")
            if not m.get("source"):
                bad.append(f"menus.{typ}.{mid}: no source (vendor tool tab or manual page)")
            seen, cur = set(), mid
            while cur:
                if cur in seen:
                    bad.append(f"menus.{typ}.{mid}: parents form a loop"); break
                seen.add(cur)
                if cur not in tree:
                    bad.append(f"menus.{typ}.{mid}: parent '{cur}' does not exist"); break
                cur = tree[cur].get("parent", "")

    resolved, used_menus = {}, set()
    for n, e in enumerate(side.get("entry", []), 1):
        where = f"entry {n} ({e.get('message') or e.get('pattern')})"
        if ("message" in e) == ("pattern" in e):
            bad.append(f"{where}: needs either message or pattern"); continue
        if not e.get("circuits"):
            bad.append(f"{where}: no circuits"); continue
        if e.get("kind") not in KINDS:
            bad.append(f"{where}: kind must be one of {', '.join(KINDS)}")
        if not has_langs(e.get("label")):
            bad.append(f"{where}: label needs {' and '.join(LANGS)}"); continue
        if "poll" in e and e["poll"] not in POLLS:
            bad.append(f"{where}: poll must be one of {', '.join(POLLS)}, or absent")
        ev = e.get("evidence", [])
        if not ev:
            bad.append(f"{where}: no evidence record")
        texts = []
        for rec in ev:
            p = os.path.join(EVIDENCE, rec + ".md")
            if not os.path.exists(p):
                bad.append(f"{where}: evidence record '{rec}' is not under {os.path.relpath(EVIDENCE, ROOT)}/")
            else:
                with open(p, encoding="utf-8") as f:
                    texts.append(f.read())
        w = e.get("write")
        if w is not None:
            if e.get("kind") not in WRITABLE_KINDS:
                bad.append(f"{where}: written but kind is not one of {', '.join(WRITABLE_KINDS)}")
            if w.get("proof") == "family" and e.get("kind") != "program_slot":
                bad.append(f"{where}: proof family is for program slots only")
            if w.get("proof") == "family" and not w.get("proof_slot"):
                bad.append(f"{where}: proof family without write.proof_slot (the captured slot)")
            if not re.fullmatch(r"[0-9a-f]{2}", str(w.get("source", ""))):
                bad.append(f"{where}: write.source must be a source address, two hex digits")
            if w.get("risk") not in RISKS:
                bad.append(f"{where}: write.risk must be one of {', '.join(RISKS)}")
            if w.get("proof") not in PROOFS:
                bad.append(f"{where}: write.proof must be one of {', '.join(PROOFS)}")
            for k in WRITE_RANGE:
                if k in w and (isinstance(w[k], bool) or not isinstance(w[k], (int, float))):
                    bad.append(f"{where}: write.{k} must be a number")
            if ("min" in w) != ("max" in w):
                bad.append(f"{where}: write.min and write.max go together")
            elif "min" in w and not w["min"] < w["max"]:
                bad.append(f"{where}: write.min must be below write.max")
            if any(k in w for k in WRITE_RANGE) and not w.get("range_source"):
                bad.append(f"{where}: write range without write.range_source (record, document and page)")
        fs = e.get("fields")
        if fs is not None and fs not in fieldsets:
            bad.append(f"{where}: field set '{fs}' does not exist"); fs = None
        rx = re.compile(e["pattern"]) if "pattern" in e else None
        for c in e["circuits"]:
            if c not in circuits:
                bad.append(f"{where}: circuit {c} has no lot file"); continue
            if rx is None:
                hits = [(f"{c}/{e['message']}", {})] if f"{c}/{e['message']}" in msgs else []
                if not hits:
                    bad.append(f"{where}: no message {e['message']} in circuit {c}")
            else:
                hits = []
                for key, m in msgs.items():
                    mm = rx.fullmatch(m["name"]) if m["circuit"] == c else None
                    if mm:
                        hits.append((key, mm.groupdict()))
                if len(hits) != e.get("count"):
                    bad.append(f"{where}: matches {len(hits)} messages in circuit {c}, count says {e.get('count')}")
            dev = device_of.get(c)
            typ = devices.get(dev, {}).get("type")
            if e.get("menu") not in menus.get(typ, {}):
                bad.append(f"{where}: menu '{e.get('menu')}' does not exist for device type '{typ}' (circuit {c})")
            used_menus.add((typ, e.get("menu")))
            for key, groups in hits:
                m = msgs[key]
                if key in resolved:
                    bad.append(f"{key}: matched by entry {resolved[key]['entry']} and entry {n}"); continue
                try:
                    r = {"entry": n, "device": dev, "e": e, "groups": groups,
                         "label": fmt(e["label"], groups, days)}
                    if "group_label" in e:
                        r["group_label"] = fmt(e["group_label"], groups, days)
                    r["group_id"] = e.get("group_id", e.get("family", "")).format(**groups)
                except ValueError as err:
                    bad.append(f"{where}: {err}"); continue
                resolved[key] = r
                # write conditions follow the CSV, both ways
                if m["write"] and w is None:
                    bad.append(f"{key}: written in the lot, no write conditions in the metadata")
                if w is not None and not m["write"]:
                    bad.append(f"{key}: write conditions, but the lot does not write it")
                if w is not None and w.get("proof") == "family" and (
                        f"{c}/{w.get('proof_slot')}" not in msgs or rx is None or not rx.fullmatch(w.get("proof_slot", ""))):
                    bad.append(f"{key}: write.proof_slot must name a slot of the same entry and circuit")
                if w is not None and m["write"] and not any(
                        re.search(rf"\b{re.escape(m['name'])}\b", t) for t in texts):
                    bad.append(f"{key}: written, but none of its evidence records ({', '.join(ev)}) names it")
                if m["passive"] and "poll" in e:
                    bad.append(f"{key}: passive message, poll must be absent")
                if any(k in e for k in ("range", "step")) and any("min" in f for f in m["fields"]):
                    bad.append(f"{key}: the CSV already has a range, the metadata must not repeat one")
                if w is not None and any(k in w for k in WRITE_RANGE) and any(
                        k in f for f in m["fields"] for k in WRITE_RANGE if k in w):
                    bad.append(f"{key}: write range repeats a bound the CSV already has")
                if "same_as" in e and e["same_as"].format(circuit=c, name=m["name"]) not in msgs:
                    bad.append(f"{key}: same_as names a message that does not exist")
                # fields
                real = [f for f in m["fields"] if not f["type"].startswith("IGN")]
                if fs is None:
                    if len(real) > 1:
                        bad.append(f"{key}: {len(real)} fields and no field set")
                    continue
                hit_keys = set()
                for f in real:
                    ks = [k for k in fieldsets[fs] if re.fullmatch(k, f["name"])]
                    if len(ks) != 1:
                        bad.append(f"{key}: field {f['name']} matches {len(ks)} keys of field set {fs}")
                    hit_keys.update(ks)
                for k in set(fieldsets[fs]) - hit_keys:
                    bad.append(f"{key}: field set {fs} has '{k}', the message has no such field")
    for key in msgs:
        if key not in resolved:
            bad.append(f"{key}: no metadata")
    for fs, table in fieldsets.items():
        for k, f in table.items():
            if f.get("skip"):
                continue
            if not has_langs(f.get("label")):
                bad.append(f"fields.{fs}.{k}: label needs {' and '.join(LANGS)}, or skip = true")
            if "kind" in f and f["kind"] not in KINDS:
                bad.append(f"fields.{fs}.{k}: kind must be one of {', '.join(KINDS)}")
    for typ, tree in menus.items():
        parents = {m.get("parent") for m in tree.values()}
        for mid in tree:
            if (typ, mid) not in used_menus and mid not in parents:
                bad.append(f"menus.{typ}.{mid}: no message and no sub-menu")
    bad += value_labels(side, msgs)[2]
    return resolved, bad


def assemble(side, msgs, resolved, langs):
    """The metadata of a release, as a plain structure. langs: {lang: messages of that tree}."""
    days = side.get("days", {})
    fieldsets = side.get("fields", {})
    vlabels, vprovisional, _ = value_labels(side, msgs)
    out_msgs, groups, open_poll, open_range, open_step = {}, {}, [], [], []
    for key, m in msgs.items():
        r = resolved[key]
        e = r["e"]
        # a record first, then the default the owner decided for the kind, then nothing
        if m["passive"]:
            poll, basis = "passive", "passive"
        elif "poll" in e:
            poll, basis = e["poll"], "record"
        elif e["kind"] in side.get("poll_default", {}):
            poll, basis = side["poll_default"][e["kind"]], "default"
        else:
            poll, basis = None, None
        description = {lang: tree[key]["comment"] for lang, tree in langs.items()}
        fields = []
        real = [f for f in m["fields"] if not f["type"].startswith("IGN")]
        for i, f in enumerate(m["fields"]):
            if f["type"].startswith("IGN"):
                continue
            o = {k: f[k] for k in ("name", "type", "divisor", "unit", "values", "min", "max", "step") if k in f}
            if "values" in f:
                o["value_labels"] = {raw: vlabels[name] for raw, name in f["values"].items()}
            fdesc = {lang: tree[key]["fields"][i]["comment"] for lang, tree in langs.items()}
            if any(fdesc.values()):
                o["description"] = fdesc
            if e.get("fields"):
                table = fieldsets[e["fields"]]
                k = next(k for k in table if re.fullmatch(k, f["name"]))
                meta = table[k]
                mm = re.fullmatch(k, f["name"])
                if meta.get("skip"):
                    o["skip"] = True
                else:
                    o["label"] = fmt(meta["label"], mm.groupdict(), days)
                    o["kind"] = meta.get("kind", e["kind"])
                if meta.get("guard"):
                    o["guard"] = True
                if mm.groupdict():
                    o["group"] = group_values(mm.groupdict(), days)
            if len(real) == 1 and "min" not in f and e.get("range"):
                o["min"], o["max"] = e["range"]
            if len(real) == 1 and "step" not in f and e.get("step") is not None:
                o["step"] = e["step"]
            fields.append(o)
        o = {
            "circuit": m["circuit"], "name": m["name"], "address": m["address"], "device": r["device"],
            "menu": e["menu"], "kind": e["kind"], "label": r["label"], "description": description,
            "read": m["read"], "passive": m["passive"], "poll": poll, "poll_basis": basis, "evidence": e["evidence"],
        }
        if e.get("fields"):
            o["compose"] = bool(e.get("compose", False))
        if "same_as" in e:
            o["same_as"] = e["same_as"].format(circuit=m["circuit"], name=m["name"])
        if "renamed_from" in e:
            o["renamed_from"] = e["renamed_from"]
        if e.get("family"):
            o["family"] = e["family"]
            o["group"] = r["group_id"]
            if r["groups"]:
                o["position"] = group_values(r["groups"], days)
            g = groups.setdefault((e["family"], m["circuit"], r["group_id"]), {
                "family": e["family"], "circuit": m["circuit"], "device": r["device"],
                "id": r["group_id"], "label": r.get("group_label", r["label"]), "members": []})
            g["members"].append(key)
        if m["write"]:
            w = e["write"]
            o["write"] = {"source": w["source"], "runtime_checksum": m["wcrc"], "risk": w["risk"],
                          "proof": w["proof"], "open": w.get("open", [])}
            for k in WRITE_RANGE:
                if k in w:
                    o["write"][k] = w[k]
            if "range_source" in w:
                o["write"]["range_source"] = w["range_source"]
            if w["proof"] == "family" and key.split("/")[1] == w.get("proof_slot"):
                o["write"]["proof"] = "change-observed"  # the captured slot itself
            elif w["proof"] == "family":
                o["write"]["proof_slot"] = w["proof_slot"]
            f0 = fields[0]
            # a program slot is bounded by its type (quarter hours of a day, enable flags)
            if e.get("kind") == "setting" and "min" not in f0 and "min" not in w:
                open_range.append(key)
            if e.get("kind") == "setting" and "step" not in f0 and "step" not in w:
                open_step.append(key)
        o["fields"] = fields
        out_msgs[key] = o
        if poll is None:
            open_poll.append(key)
    devices = {}
    for dev, d in side["devices"].items():
        cs = []
        for c in d["circuits"]:
            a = next(m for m in msgs.values() if m["circuit"] == c)
            cs.append({"circuit": c, "address": a["address"], "file": a["file"]})
        devices[dev] = {"type": d["type"], "label": d["label"], "circuits": cs}
    menus = {typ: [{"id": mid, "parent": m.get("parent", ""), "label": m["label"], "source": m["source"]}
                   for mid, m in tree.items()] for typ, tree in side["menus"].items()}
    return {
        "devices": devices, "menus": menus, "messages": out_msgs, "groups": list(groups.values()),
        "open": {"poll": open_poll, "range": open_range, "step": open_step, "value_labels": vprovisional},
    }


def counts(data):
    by_kind, by_device, by_poll = {}, {}, {}
    for m in data["messages"].values():
        by_kind[m["kind"]] = by_kind.get(m["kind"], 0) + 1
        by_device[m["device"]] = by_device.get(m["device"], 0) + 1
        p = f"{m['poll']} ({m['poll_basis']})" if m["poll"] else "none"
        by_poll[p] = by_poll.get(p, 0) + 1
    return by_kind, by_device, by_poll


def args_of(argv):
    pos, opt, i = [], {}, 0
    while i < len(argv):
        if argv[i].startswith("--"):
            opt.setdefault(argv[i][2:], []).append(argv[i + 1]); i += 2
        else:
            pos.append(argv[i]); i += 1
    return pos, opt


def main():
    pos, opt = args_of(sys.argv[1:])
    if len(pos) < 3 or pos[0] not in ("check", "build", "summary"):
        sys.exit(__doc__)
    side = load(pos[1])
    msgs, lines, problems = read_tree(pos[2])
    resolved, bad = resolve(side, msgs)
    bad = problems + bad
    name = os.path.basename(pos[1])
    if bad:
        print(f"{name}: FAIL, {len(bad)} problems")
        for b in bad[:40]:
            print(f"  {b}")
        if len(bad) > 40:
            print(f"  ... and {len(bad) - 40} more")
        sys.exit(1)
    langs = {"en": msgs}
    for spec in opt.get("lang", []):
        lang, tree = spec.split("=", 1)
        other, _, _ = read_tree(tree)
        if set(other) != set(msgs):
            sys.exit(f"{lang}: the tree {tree} does not hold the same messages as the English one")
        langs[lang] = other
    data = assemble(side, msgs, resolved, langs)
    by_kind, by_device, by_poll = counts(data)
    written = sum(1 for m in data["messages"].values() if "write" in m)
    st = side["status"]
    print(f"{name}: ok, {len(msgs)} messages ({lines} CSV lines, {written} written) in "
          f"{len(side.get('entry', []))} entries, {len(data['devices'])} devices; "
          f"menus {st['menus']}, labels {st['labels']}; "
          f"{sum(1 for m in data['messages'].values() for f in m['fields'] if 'value_labels' in f)} fields with "
          f"a value list, labels of the entries {st['values']}"
          + (f" ({', '.join(data['open']['value_labels'])} provisional)" if data["open"]["value_labels"] else ""))
    if pos[0] == "check":
        return
    if pos[0] == "summary":
        for title, table in (("kind", by_kind), ("device", by_device), ("poll", by_poll)):
            print(f"by {title}: " + ", ".join(f"{k} {v}" for k, v in sorted(table.items(), key=lambda x: -x[1])))
        for k in ("range", "step"):
            print(f"written, no {k}: " + (", ".join(data["open"][k]) or "none"))
        return
    if len(pos) < 4 or "version" not in opt or "commit" not in opt:
        sys.exit(__doc__)
    with open(pos[1], "rb") as f:
        digest = hashlib.sha256(f.read()).hexdigest()
    doc = {
        "schema": SCHEMA,
        "definitions": {
            "version": opt["version"][0], "commit": opt["commit"][0],
            "messages": len(msgs), "csv_lines": lines,
            "loaded_by_ebusd": int(opt["loaded"][0]) if "loaded" in opt else None,
            "sidecar_sha256": digest,
        },
        "languages": list(langs),
        "status": side["status"],
    }
    doc.update(data)
    with open(pos[3], "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print(f"metadata: {os.path.relpath(pos[3], ROOT)}, schema {SCHEMA}, {len(msgs)} messages, "
          f"languages {', '.join(langs)}")


if __name__ == "__main__":
    main()
