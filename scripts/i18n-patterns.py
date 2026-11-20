#!/usr/bin/env python3
"""Writes the patterned entries of a translation file: weekly-program slots and fault-history
slots, which differ only by a weekday and numbers.

  scripts/i18n-patterns.py <english csv tree> <lang>                   print the entries
  scripts/i18n-patterns.py <english csv tree> <lang> <translation.yaml>  rewrite them in the file

The lookup of the emitter is exact, so every string needs its own key. The keys are taken from
the compiled English tree (see scripts/i18n-keys.py), matched against PATTERNS and written with
the phrases of the language below; the terms come from evidence/terms.md. In the file, the
entries sit between the two marker lines; everything else in the file is left as it is.
"""
import importlib.util
import os
import re
import sys

BEGIN = "# patterned entries, written by scripts/i18n-patterns.py of the workbench: do not edit"
END = "# end of the patterned entries"
DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
DAY = "(?P<day>" + "|".join(DAYS) + ")"

# English pattern, name of the phrase. Order matters: the first match wins.
PATTERNS = [
    (rf"heating program (?P<n>\d+), {DAY} slot (?P<m>\d+), read only: seen to be the slot of room unit 1, written through 35\.w\.fs1", "heating_shared"),
    (rf"heating program (?P<n>\d+), {DAY} slot (?P<m>\d+)", "heating"),
    (rf"hot-water program stored in the room unit, {DAY} slot (?P<m>\d+)", "dhw_stored"),
    (rf"circulation program stored in the room unit, {DAY} slot (?P<m>\d+)", "circ_stored"),
    (rf"{DAY} slot (?P<m>\d+)", "slot"),
    (r"fault history slot (?P<n>\d+)", "fault"),
]

LANGS = {
    "fr": {
        "days": ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"],
        "heating_shared": "programme de chauffe {n}, {day}, plage horaire {m}, en lecture seule : vue comme la plage de la commande à distance 1, écrite via 35.w.fs1",
        "heating": "programme de chauffe {n}, {day}, plage horaire {m}",
        "dhw_stored": "programme ECS enregistré dans la commande à distance, {day}, plage horaire {m}",
        "circ_stored": "programme de circulation ECS enregistré dans la commande à distance, {day}, plage horaire {m}",
        "slot": "{day}, plage horaire {m}",
        "fault": "mémoire de défauts, emplacement {n}",
    },
}


def load_keys_module():
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "i18n-keys.py")
    spec = importlib.util.spec_from_file_location("i18n_keys", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def quote(s):
    """A YAML scalar for a key or a value: plain when it can be, double-quoted otherwise."""
    if re.search(r": |^[\s\-?:,\[\]{}#&*!|>'\"%@`]| #|\s$", s) or s == "":
        return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'
    return s


def natural(s):
    return [int(p) if p.isdigit() else p for p in re.split(r"(\d+)", s)]


def entries(tree, lang):
    table = LANGS.get(lang) or sys.exit(f"no phrases for '{lang}' in {os.path.basename(__file__)}")
    k = load_keys_module()
    strings = set(k.lot_comments(tree))
    out = []
    for name in [p[1] for p in PATTERNS]:
        group = []
        for s in strings:
            for rx, phrase in PATTERNS:
                m = re.fullmatch(rx, s)
                if m:
                    if phrase == name:
                        g = m.groupdict()
                        if "day" in g:
                            g["dayno"] = DAYS.index(g["day"])
                            g["day"] = table["days"][g["dayno"]]
                        group.append((g.get("n", "0"), g.get("dayno", 0), g.get("m", "0"), s,
                                      table[name].format(**g)))
                    break
        group.sort(key=lambda e: (natural(e[0]), e[1], natural(e[2])))
        out += [f"{quote(s)}: {quote(t)}" for _, _, _, s, t in group]
    return out


def main():
    if len(sys.argv) not in (3, 4):
        sys.exit(__doc__)
    lines = entries(sys.argv[1], sys.argv[2])
    if len(sys.argv) == 3:
        print("\n".join(lines))
        return
    path = sys.argv[3]
    with open(path, encoding="utf-8") as f:
        text = f.read().split("\n")
    if BEGIN in text and END in text:
        a, b = text.index(BEGIN), text.index(END)
        text = text[:a] + [BEGIN] + lines + text[b:]
    else:
        while text and text[-1] == "":
            text.pop()
        text += ["", BEGIN] + lines + [END, ""]
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(text))
    print(f"{os.path.basename(path)}: {len(lines)} patterned entries written")


if __name__ == "__main__":
    main()
