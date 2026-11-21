"""Unit tests for the workbench scripts and JSON Schemas.

Run with:
  python3 -m unittest discover -s tests -v
"""
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest

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
notice = load_module("render_notice", "render-notice.py")
settings_table = load_module("settings_table", "settings-table.py")


SAMPLE_CSV_KA = """type,circuit,level,name,comment,qq,zz,pbsb,id,*name,part,type,divisor/values,range,unit,comment
r,ka,,BlockingTime,[WCRC] burner lock-out time,,15,5022,2500,value,,UIN,,1-60,min,minimum lock-out
w,ka,,BlockingTime,[WCRC] burner lock-out time,,15,5023,2500,value,,UIN,,1-60,min,minimum lock-out
r,ka,,PumpState,pump status,,15,5022,2600,value,,UCH,0=off;1=on,,,pump
"""

SAMPLE_CSV_KA_FR = """type,circuit,level,name,comment,qq,zz,pbsb,id,*name,part,type,divisor/values,range,unit,comment
r,ka,,BlockingTime,[WCRC] temps de blocage,,15,5022,2500,value,,UIN,,1-60,min,blocage minimal
w,ka,,BlockingTime,[WCRC] temps de blocage,,15,5023,2500,value,,UIN,,1-60,min,blocage minimal
r,ka,,PumpState,état pompe,,15,5022,2600,value,,UCH,0=off;1=on,,,pompe
"""

SAMPLE_CSV_KA_BAD = """type,circuit,level,name,comment,qq,zz,pbsb,id,*name,part,type,divisor/values,range,unit,comment
r,ka,,BlockingTime,[WCRC] temps de blocage,,15,5022,2500,value,,SIN,,1-60,min,blocage minimal
w,ka,,BlockingTime,[WCRC] temps de blocage,,15,5023,2500,value,,UIN,,1-60,min,blocage minimal
r,ka,,PumpState,état pompe,,15,5022,2600,value,,UCH,0=off;1=on,,,pompe
"""

SAMPLE_SIDECAR = """schema = 1

[status]
menus = "accepted"
labels = "accepted"
values = "accepted"
date = "2026-11-18"

[poll_default]
live = "cyclic"
setting = "on_demand"

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

[menus.manager.settings]
parent = ""
label = { en = "Settings", fr = "Réglages" }
source = "manual p. 1"

[[entry]]
circuits = ["ka"]
message = "BlockingTime"
menu = "settings"
kind = "setting"
label = { en = "Blocking time", fr = "Temps de blocage" }
evidence = ["sample"]
[entry.write]
source = "ff"
risk = "regulation"
proof = "change-observed"

[[entry]]
circuits = ["ka"]
message = "PumpState"
menu = "settings"
kind = "live"
label = { en = "Pump state", fr = "État pompe" }
evidence = ["sample"]
"""

SAMPLE_EVIDENCE = """# Sample evidence
2026-11-18
BlockingTime: `31 15 50 22 02 25 00 / 02 01 00` = 1
PumpState: `31 15 50 22 02 26 00 / 01 01` = on
"""


def write_tree(base, csv_text):
    wolf = os.path.join(base, "wolf")
    os.makedirs(wolf, exist_ok=True)
    with open(os.path.join(wolf, "15.w.ka.csv"), "w", encoding="utf-8") as f:
        f.write(csv_text)


class TestMetadata(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = self.tmp.name
        self.en_tree = os.path.join(self.root, "en")
        self.fr_tree = os.path.join(self.root, "fr")
        self.ev_dir = os.path.join(self.root, "evidence")
        os.makedirs(self.ev_dir)
        with open(os.path.join(self.ev_dir, "sample.md"), "w", encoding="utf-8") as f:
            f.write(SAMPLE_EVIDENCE)
        write_tree(self.en_tree, SAMPLE_CSV_KA)
        write_tree(self.fr_tree, SAMPLE_CSV_KA_FR)
        self.sidecar = os.path.join(self.root, "weishaupt.toml")
        with open(self.sidecar, "w", encoding="utf-8") as f:
            f.write(SAMPLE_SIDECAR)
        self.orig_ev = md.EVIDENCE
        md.EVIDENCE = self.ev_dir

    def tearDown(self):
        md.EVIDENCE = self.orig_ev
        self.tmp.cleanup()

    def test_valid_sidecar_resolves_and_matches_schema(self):
        out_path = os.path.join(self.root, "meta.json")
        env = dict(os.environ, EVIDENCE_DIR=self.ev_dir)
        build = subprocess.run(
            [sys.executable, os.path.join(SCRIPTS, "metadata.py"),
             "build", self.sidecar, self.en_tree, out_path,
             "--version", "1.0.0", "--commit", "abcdef1", "--loaded", "3",
             "--lang", f"fr={self.fr_tree}"],
            capture_output=True, text=True, env=env,
        )
        self.assertEqual(build.returncode, 0, build.stdout + build.stderr)
        r = subprocess.run(
            [sys.executable, os.path.join(SCRIPTS, "validate-schema.py"),
             os.path.join(SCHEMAS, "metadata.schema.json"), out_path],
            capture_output=True, text=True,
        )
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_missing_message_fails(self):
        bad = SAMPLE_SIDECAR.split('[[entry]]\ncircuits = ["ka"]\nmessage = "PumpState"')[0]
        with open(self.sidecar, "w", encoding="utf-8") as f:
            f.write(bad)
        msgs, _, _ = md.read_tree(self.en_tree)
        _, problems = md.resolve(md.load(self.sidecar), msgs)
        self.assertTrue(any("PumpState" in p for p in problems), problems)

    def test_missing_french_label_fails(self):
        bad = SAMPLE_SIDECAR.replace(', fr = "Marche"', '')
        with open(self.sidecar, "w", encoding="utf-8") as f:
            f.write(bad)
        msgs, _, _ = md.read_tree(self.en_tree)
        _, problems = md.resolve(md.load(self.sidecar), msgs)
        self.assertTrue(any("on" in p for p in problems), problems)

    def test_accepted_status_without_date_fails(self):
        bad = SAMPLE_SIDECAR.replace('date = "2026-11-18"', '')
        with open(self.sidecar, "w", encoding="utf-8") as f:
            f.write(bad)
        msgs, _, _ = md.read_tree(self.en_tree)
        _, problems = md.resolve(md.load(self.sidecar), msgs)
        self.assertTrue(any("date" in p for p in problems), problems)

    def test_shared_with_same_device_fails(self):
        bad = SAMPLE_SIDECAR + '\nshared_with = "ka/BlockingTime"\n'
        with open(self.sidecar, "w", encoding="utf-8") as f:
            f.write(bad)
        msgs, _, _ = md.read_tree(self.en_tree)
        _, problems = md.resolve(md.load(self.sidecar), msgs)
        self.assertTrue(any("shared_with" in p for p in problems), problems)


class TestFixtures(unittest.TestCase):
    def test_holds_respects_hex_boundaries(self):
        self.assertTrue(fx.holds("req 25 00 ans 01 00", "25 00"))
        self.assertTrue(fx.holds("req 2500 ans 0100", "25 00"))
        self.assertFalse(fx.holds("req a2500b ans", "25 00"))
        self.assertFalse(fx.holds("req 125 00 ans", "25 00"))

    def test_agrees_precision_and_na(self):
        self.assertTrue(fx.agrees(11.3, 11.301))
        self.assertTrue(fx.agrees(11.3, 11.29))
        self.assertFalse(fx.agrees(11.3, 11.4))
        self.assertTrue(fx.agrees(fx.NA, None))
        self.assertFalse(fx.agrees(fx.NA, 0))
        self.assertTrue(fx.agrees("on", "on"))
        self.assertFalse(fx.agrees("on", "off"))


class TestI18nKeys(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.en_tree = os.path.join(self.tmp.name, "en")
        self.fr_tree = os.path.join(self.tmp.name, "fr")
        self.bad_tree = os.path.join(self.tmp.name, "bad")
        write_tree(self.en_tree, SAMPLE_CSV_KA)
        write_tree(self.fr_tree, SAMPLE_CSV_KA_FR)
        write_tree(self.bad_tree, SAMPLE_CSV_KA_BAD)

    def tearDown(self):
        self.tmp.cleanup()

    def test_compare_accepts_comment_only_diff(self):
        r = subprocess.run(
            [sys.executable, os.path.join(SCRIPTS, "i18n-keys.py"),
             self.en_tree, "compare", self.fr_tree],
            capture_output=True, text=True,
        )
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_compare_rejects_type_change(self):
        r = subprocess.run(
            [sys.executable, os.path.join(SCRIPTS, "i18n-keys.py"),
             self.en_tree, "compare", self.bad_tree],
            capture_output=True, text=True,
        )
        self.assertNotEqual(r.returncode, 0)


class TestSchemas(unittest.TestCase):
    def test_schemas_are_valid_json(self):
        for name in ("metadata.schema.json", "fixtures.schema.json"):
            with open(os.path.join(SCHEMAS, name), encoding="utf-8") as f:
                doc = json.load(f)
            self.assertEqual(doc["$schema"], "https://json-schema.org/draft/2020-12/schema")


class TestCheckconfigErrorFilter(unittest.TestCase):
    """The filter that fails the check on an error line of ebusd --checkconfig: the same in the
    local check and in the workflow, and one that knows every log facility of ebusd."""
    FACILITIES = ("main", "network", "bus", "device", "update", "other")  # s_facilityNames, log.cpp

    def _filters(self):
        import re
        found = {}
        for rel in ("scripts/check.sh", ".github/workflows/checkconfig.yml"):
            with open(os.path.join(ROOT, rel), encoding="utf-8") as f:
                m = re.search(r"grep -Eq '([^']*error[^']*)'", f.read())
            self.assertIsNotNone(m, rel)
            found[rel] = m.group(1)
        return found

    def test_same_filter_in_check_and_workflow(self):
        self.assertEqual(len(set(self._filters().values())), 1)

    def test_filter_matches_every_facility(self):
        pattern = next(iter(self._filters().values()))
        for facility in self.FACILITIES:
            line = f"2026-01-01 00:00:00.000 [{facility} error] something failed"
            out = subprocess.run(["grep", "-Eq", pattern], input=line, text=True)
            self.assertEqual(out.returncode, 0, facility)
        notice = "2026-01-01 00:00:00.000 [main notice] found messages: 1073"
        self.assertNotEqual(subprocess.run(["grep", "-Eq", pattern], input=notice, text=True).returncode, 0)


if __name__ == "__main__":
    unittest.main()


class TestRenderNotice(unittest.TestCase):
    KEYS = {"VERSION": "9.9.9", "COMMIT": "abc1234", "NAME": "n", "BASE": "b", "COUNT": "1",
            "EBUSD": "e", "LIB": "l", "VARIANT": ""}

    def test_no_provisional_sentence_when_empty(self):
        out = notice.render("one.@PROVISIONAL_SENTENCE@ Two.", {**self.KEYS, "PROVISIONAL": ""})
        self.assertEqual(out, "one. Two.")

    def test_provisional_sentence_when_listed(self):
        out = notice.render("one.@PROVISIONAL_SENTENCE@ Two.", {**self.KEYS, "PROVISIONAL": "A, B"})
        self.assertEqual(out, "one. Still provisional: A, B. Two.")

    def test_token_left_fails(self):
        with self.assertRaises(ValueError):
            notice.render("@VERSION@ @UNKNOWN@", {"VERSION": "1"})

    def test_release_notice_renders(self):
        with open(os.path.join(ROOT, "docs", "release-readme.md"), encoding="utf-8") as f:
            out = notice.render(f.read(), {**self.KEYS, "PROVISIONAL": ""})
        self.assertNotIn("Still provisional", out)
        self.assertNotIn("@", out.replace("@ebusd", ""))
        self.assertIn("9.9.9", out)


class TestSettingsTable(unittest.TestCase):
    def meta(self):
        def msg(circuit, name, field, write, kind="setting"):
            return {"circuit": circuit, "name": name, "kind": kind, "fields": [field], "write": write}
        ff = {"source": "ff"}
        return {"messages": [
            msg("ka", "BlockingTime", {"name": "value", "unit": "min", "min": 0, "max": 30}, ff),
            msg("fs1", "RoomSetbackTemp", {"name": "value", "divisor": 10, "unit": "°C"},
                {"source": "ff", "min": 10.0, "max": 21.5, "step": 0.5}),
            msg("fs3", "RoomSetbackTemp", {"name": "value", "divisor": 10, "unit": "°C"},
                {"source": "ff", "min": 10.0, "max": 21.5, "step": 0.5}),
            msg("fs1", "ControlVariation", {"name": "value"}, ff),
            msg("ka", "CircWithLegionella", {"name": "value", "values": {"1": "on", "0": "off"}}, ff),
            msg("em2", "SupplyMaxTemp", {"name": "value", "divisor": 10, "unit": "°C", "min": 8, "max": 82,
                                         "step": 0.5}, {"source": "31"}),
            msg("fs1", "HCProgram1Mon1", {"name": "totime"}, {"source": "31"}, kind="program_slot"),
            {"circuit": "fs2", "name": "RoomNormalTemp", "kind": "setting", "fields": [{"name": "value"}]},
        ]}

    def test_rows_and_count(self):
        text, count = settings_table.table(self.meta())
        self.assertEqual(count, 6)  # program slot and read-only message left out
        self.assertIn("| ka | `BlockingTime` | 0 to 30 | 1 | min | `ff` |", text)
        self.assertIn("| fs1, fs3 | `RoomSetbackTemp` | 10 to 21.5 * | 0.5 | °C | `ff` |", text)
        self.assertIn("| fs1 | `ControlVariation` | none |  |  | `ff` |", text)
        self.assertIn("| ka | `CircWithLegionella` | off, on |  |  | `ff` |", text)
        self.assertIn("| em2 | `SupplyMaxTemp` | 8 to 82 | 0.5 | °C | `31` |", text)
        self.assertNotIn("HCProgram", text)
