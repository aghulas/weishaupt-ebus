"""Additional unit tests covering metadata, fixtures, i18n, patterns, and schema validation."""
import importlib.util
import io
import json
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(ROOT, "scripts")
SCHEMAS = os.path.join(ROOT, "schemas")


def load_module(name, filename):
    spec = importlib.util.spec_from_file_location(name, os.path.join(SCRIPTS, filename))
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


md = load_module("metadata", "metadata.py")
fx = load_module("fixtures", "fixtures.py")
i18n = load_module("i18n_keys", "i18n-keys.py")
pat = load_module("i18n_patterns", "i18n-patterns.py")
val = load_module("validate_schema", "validate-schema.py")


RICH_CSV_KA = """type,circuit,level,name,comment,qq,zz,pbsb,id,*name,part,type,divisor/values,range,unit,comment
r,ka,,BlockingTime,[WCRC] burner lock-out time,,15,5022,4c2500,value,,UIN,,1-60,min,minimum lock-out
w,ka,,BlockingTime,[WCRC] burner lock-out time,,15,5023,4c2500,value,,UIN,,1-60,min,minimum lock-out
r,ka,,HcMode,heating circuit mode,,15,5014,,pump,,BI0,0=off;1=on,,,pump state,ukn1_1,,BI1,,,,,outsidetemp,,D2B,,,°C,outside temperature
r,ka,,HCProgram1Mon1,heating program 1, Monday slot 1,,15,5022,aa0100,start,,TTM,,,,start time
r,ka,,HCProgram1Tue1,heating program 1, Tuesday slot 1,,15,5022,ab0200,start,,TTM,,,,start time
"""

RICH_CSV_KA_QUOTED = """type,circuit,level,name,comment,qq,zz,pbsb,id,*name,part,type,divisor/values,range,unit,comment
r,ka,,BlockingTime,[WCRC] burner lock-out time,,15,5022,4c2500,value,,UIN,,1-60,min,minimum lock-out
w,ka,,BlockingTime,[WCRC] burner lock-out time,,15,5023,4c2500,value,,UIN,,1-60,min,minimum lock-out
r,ka,,HcMode,heating circuit mode,,15,5014,,pump,,BI0,0=off;1=on,,,pump state,ukn1_1,,BI1,,,,,outsidetemp,,D2B,,,°C,outside temperature
r,ka,,HCProgram1Mon1,"heating program 1, Monday slot 1",,15,5022,aa0100,start,,TTM,,,,start time
r,ka,,HCProgram1Tue1,"heating program 1, Tuesday slot 1",,15,5022,ab0200,start,,TTM,,,,start time
"""

RICH_CSV_KA_FR = """type,circuit,level,name,comment,qq,zz,pbsb,id,*name,part,type,divisor/values,range,unit,comment
r,ka,,BlockingTime,[WCRC] temps de blocage,,15,5022,4c2500,value,,UIN,,1-60,min,blocage minimal
w,ka,,BlockingTime,[WCRC] temps de blocage,,15,5023,4c2500,value,,UIN,,1-60,min,blocage minimal
r,ka,,HcMode,mode circuit de chauffage,,15,5014,,pump,,BI0,0=off;1=on,,,état pompe,ukn1_1,,BI1,,,,,outsidetemp,,D2B,,,°C,température extérieure
r,ka,,HCProgram1Mon1,"programme de chauffe 1, lundi, plage horaire 1",,15,5022,aa0100,start,,TTM,,,,heure début
r,ka,,HCProgram1Tue1,"programme de chauffe 1, mardi, plage horaire 1",,15,5022,ab0200,start,,TTM,,,,heure début
"""

RICH_SIDECAR = r"""schema = 1

[status]
menus = "accepted"
labels = "accepted"
values = "accepted"
date = "2026-11-18"

[poll_default]
live = "cyclic"
setting = "on_demand"
program_slot = "on_demand"

[days]
Mon = { en = "Monday", fr = "lundi" }
Tue = { en = "Tuesday", fr = "mardi" }
Wed = { en = "Wednesday", fr = "mercredi" }
Thu = { en = "Thursday", fr = "jeudi" }
Fri = { en = "Friday", fr = "vendredi" }
Sat = { en = "Saturday", fr = "samedi" }
Sun = { en = "Sunday", fr = "dimanche" }

[values]
off = { en = "Off", fr = "Arrêt" }
on = { en = "On", fr = "Marche" }

[devices.manager]
type = "manager"
circuits = ["ka"]
label = { en = "System manager", fr = "Manager de cascade" }

[menus.manager.root]
parent = ""
label = { en = "General", fr = "Général" }
source = "manual p. 1"

[menus.manager.programs]
parent = "root"
label = { en = "Programs", fr = "Programmes" }
source = "manual p. 2"

[[entry]]
circuits = ["ka"]
message = "BlockingTime"
menu = "root"
kind = "setting"
label = { en = "Blocking time", fr = "Temps de blocage" }
evidence = ["rec"]
[entry.write]
source = "ff"
risk = "regulation"
proof = "change-observed"

[fields.hcmode]
pump = { kind = "state", label = { en = "Pump", fr = "Pompe" } }
'ukn([12])_(\d)' = { skip = true, renamed_from = 'ink\1_\2' }
outsidetemp = { kind = "live", label = { en = "Outside temp", fr = "Température extérieure" }, absent = -100.0 }

[[entry]]
circuits = ["ka"]
message = "HcMode"
menu = "root"
kind = "live"
compose = false
fields = "hcmode"
label = { en = "Heating circuit mode", fr = "Mode circuit" }
evidence = ["rec"]

[[entry]]
circuits = ["ka"]
pattern = '^HCProgram(?P<p>1)(?P<day>Mon|Tue)(?P<slot>1)$'
count = 2
family = "program"
group = "hc1"
group_label = { en = "Heating program 1", fr = "Programme de chauffe 1" }
menu = "programs"
kind = "program_slot"
label = { en = "Heating 1 {day} {slot}", fr = "Chauffage 1 {day} {slot}" }
evidence = ["rec"]
"""

RICH_EVIDENCE = """# Record
2026-11-18
| BlockingTime | `4c 25 00` | `01 00` | 1 |
| BlockingTime write | `cc 25 00 02 00` | `` | 2 |
"""


def write_wolf(base, filename, content):
    wolf = os.path.join(base, "wolf")
    os.makedirs(wolf, exist_ok=True)
    with open(os.path.join(wolf, filename), "w", encoding="utf-8") as f:
        f.write(content)


class TestMetadataRich(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = self.tmp.name
        self.en = os.path.join(self.root, "en")
        self.fr = os.path.join(self.root, "fr")
        self.ev = os.path.join(self.root, "evidence")
        os.makedirs(self.ev)
        with open(os.path.join(self.ev, "rec.md"), "w", encoding="utf-8") as f:
            f.write(RICH_EVIDENCE)
        write_wolf(self.en, "15.w.ka.csv", RICH_CSV_KA_QUOTED)
        write_wolf(self.fr, "15.w.ka.csv", RICH_CSV_KA_FR)
        self.sidecar = os.path.join(self.root, "weishaupt.toml")
        with open(self.sidecar, "w", encoding="utf-8") as f:
            f.write(RICH_SIDECAR)
        self.orig_ev = md.EVIDENCE
        md.EVIDENCE = self.ev

    def tearDown(self):
        md.EVIDENCE = self.orig_ev
        self.tmp.cleanup()

    def test_assemble_patterns_fields_groups_and_counts(self):
        msgs, lines, problems = md.read_tree(self.en)
        self.assertEqual(problems, [])
        self.assertEqual(lines, 5)
        side = md.load(self.sidecar)
        resolved, res_problems = md.resolve(side, msgs)
        self.assertEqual(res_problems, [])
        fr_msgs, _, _ = md.read_tree(self.fr)
        doc = md.assemble(side, msgs, resolved, {"fr": fr_msgs})
        self.assertEqual(len(doc["groups"]), 1)
        self.assertEqual(len(doc["groups"][0]["members"]), 2)
        hc = doc["messages"]["ka/HcMode"]
        ukn = next(f for f in hc["fields"] if f["name"] == "ukn1_1")
        self.assertEqual(ukn["renamed_from"], "ink1_1")
        out_t = next(f for f in hc["fields"] if f["name"] == "outsidetemp")
        self.assertEqual(out_t["absent"], -100.0)
        by_kind, by_dev, _ = md.counts(doc)
        self.assertEqual(by_dev["manager"], 4)
        self.assertEqual(by_kind["program_slot"], 2)

    def test_pattern_count_mismatch_and_bad_menu_parent_fail(self):
        bad = RICH_SIDECAR.replace("count = 2", "count = 3").replace('parent = "root"', 'parent = "missing"')
        with open(self.sidecar, "w", encoding="utf-8") as f:
            f.write(bad)
        msgs, _, _ = md.read_tree(self.en)
        _, problems = md.resolve(md.load(self.sidecar), msgs)
        self.assertTrue(any("matches 2" in p for p in problems), problems)
        self.assertTrue(any("missing" in p for p in problems), problems)

    def test_duplicate_csv_range_in_write_fails(self):
        bad = RICH_SIDECAR.replace(
            'proof = "change-observed"',
            'proof = "change-observed"\nmin = 1\nmax = 60\nrange_source = "manual p. 1"',
        )
        with open(self.sidecar, "w", encoding="utf-8") as f:
            f.write(bad)
        msgs, _, _ = md.read_tree(self.en)
        _, problems = md.resolve(md.load(self.sidecar), msgs)
        self.assertTrue(any("range" in p or "min" in p for p in problems), problems)

    def test_args_of_parses_flags(self):
        pos, opts = md.args_of(["a", "b", "--version", "1.0", "--lang", "fr=/tmp/fr"])
        self.assertEqual(pos, ["a", "b"])
        self.assertEqual(opts["version"], ["1.0"])
        self.assertEqual(opts["lang"], ["fr=/tmp/fr"])


class TestFixturesInProcess(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = self.tmp.name
        self.en = os.path.join(self.root, "en")
        self.ev = os.path.join(self.root, "evidence")
        os.makedirs(self.ev)
        with open(os.path.join(self.ev, "rec.md"), "w", encoding="utf-8") as f:
            f.write(RICH_EVIDENCE)
        write_wolf(self.en, "15.w.ka.csv", RICH_CSV_KA_QUOTED)
        self.orig_ev = md.EVIDENCE
        md.EVIDENCE = self.ev
        fx.record_lines.__defaults__[0].clear()

    def tearDown(self):
        md.EVIDENCE = self.orig_ev
        fx.record_lines.__defaults__[0].clear()
        self.tmp.cleanup()

    def test_load_structure_decode16_and_coverage(self):
        toml_path = os.path.join(self.root, "fixtures.toml")
        with open(toml_path, "w", encoding="utf-8") as f:
            f.write("""schema = 2

[[block]]
evidence = "rec"
date = "2026-11-18"
where = "row"
readings = [
  { circuit = "ka", message = "BlockingTime", type = "read", qq = "31", zz = "15", pbsb = "5022", master = "4c 25 00", slave = "01 00", expect = { value = 1 } },
  { circuit = "ka", message = "BlockingTime", type = "write", qq = "ff", zz = "15", pbsb = "5023", master = "cc 25 00 02 00", slave = "", expect = { value = 2 } },
]
""")
        msgs, _, _ = md.read_tree(self.en)
        readings = fx.load(toml_path)
        self.assertEqual(len(readings), 2)
        items, bad = fx.structure(readings, msgs)
        self.assertEqual(bad, [])
        self.assertEqual(len(items), 2)
        self.assertEqual(fx.nn("4c 25 00"), "034c2500")
        self.assertEqual(fx.typed("12.5", {"type": "SIN"}), 12.5)
        self.assertEqual(fx.typed("-", {"type": "SIN"}), None)
        self.assertEqual(fx.typed("08:30", {"type": "TTQ"}), "08:30")
        dec_bad, dec_n = fx.decode16(items)
        self.assertEqual(dec_bad, [])
        self.assertEqual(dec_n, 2)
        cov = fx.coverage(items, msgs, {})
        self.assertEqual(cov["covered"], 1)
        self.assertEqual(cov["readings"], 2)

    def test_structure_catches_missing_evidence_and_wrong_id(self):
        toml_path = os.path.join(self.root, "bad.toml")
        with open(toml_path, "w", encoding="utf-8") as f:
            f.write("""schema = 2

[[block]]
evidence = "missing"
date = "2026-11-18"
readings = [
  { circuit = "ka", message = "BlockingTime", type = "read", qq = "31", zz = "15", pbsb = "5022", master = "00 00 00", slave = "01 00", expect = { value = 1 } },
]
""")
        msgs, _, _ = md.read_tree(self.en)
        _, bad = fx.structure(fx.load(toml_path), msgs)
        self.assertTrue(len(bad) >= 1)


class TestI18nAndPatternsInProcess(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.en = os.path.join(self.tmp.name, "en")
        self.fr = os.path.join(self.tmp.name, "fr")
        write_wolf(self.en, "15.w.ka.csv", RICH_CSV_KA_QUOTED)
        write_wolf(self.fr, "15.w.ka.csv", RICH_CSV_KA_FR)

    def tearDown(self):
        self.tmp.cleanup()

    def test_i18n_keys_and_patterns(self):
        comms = i18n.lot_comments(self.en)
        self.assertIn("burner lock-out time", comms)
        self.assertIn("heating program 1, Monday slot 1", comms)
        self.assertIn("a.", i18n.with_stop({"a."}))
        self.assertIn("a", i18n.with_stop({"a."}))

        yaml_path = os.path.join(self.tmp.name, "fr.yaml")
        with open(yaml_path, "w", encoding="utf-8") as f:
            f.write('burner lock-out time: temps de blocage\n"heating program 1, Monday slot 1": "programme de chauffe 1, lundi, plage horaire 1"\n')
        ks = [k for k, _, _ in i18n.keys(yaml_path)]
        self.assertIn("burner lock-out time", ks)

        lines = pat.entries(self.en, "fr")
        self.assertEqual(len(lines), 2)
        self.assertIn("programme de chauffe 1, lundi, plage horaire 1", lines[0])
        self.assertEqual(pat.quote("a: b"), '"a: b"')
        self.assertEqual(pat.quote("plain"), "plain")

        # Test rewriting a yaml file via pat.main()
        orig_argv = sys.argv
        try:
            sys.argv = ["i18n-patterns.py", self.en, "fr", yaml_path]
            buf = io.StringIO()
            with redirect_stdout(buf):
                pat.main()
            with open(yaml_path, encoding="utf-8") as f:
                content = f.read()
            self.assertIn(pat.BEGIN, content)
            self.assertIn(pat.END, content)
            # Re-run to hit the replace-between-markers branch
            with redirect_stdout(buf):
                pat.main()
        finally:
            sys.argv = orig_argv


class TestValidateSchemaInProcess(unittest.TestCase):
    def test_validate_schema_fails_on_invalid_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            bad_path = os.path.join(tmp, "bad.json")
            with open(bad_path, "w", encoding="utf-8") as f:
                json.dump({"schema": 99}, f)
            orig_argv = sys.argv
            try:
                sys.argv = ["validate-schema.py", os.path.join(SCHEMAS, "metadata.schema.json"), bad_path]
                err = io.StringIO()
                with redirect_stderr(err), self.assertRaises(SystemExit):
                    val.main()
            finally:
                sys.argv = orig_argv


if __name__ == "__main__":
    unittest.main()
