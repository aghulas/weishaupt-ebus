"""Unit tests for the code lists of the metadata (scripts/metadata.py, schemas/metadata.schema.json):
the fault codes a field carries, numbered in a vendor scheme.

Run with:
  python3 -m unittest discover -s tests -v
"""
import json
import os
import subprocess
import sys
import tempfile
import unittest

from test_scripts import SAMPLE_CSV_KA, SAMPLE_CSV_KA_FR, SAMPLE_SIDECAR, SCHEMAS, SCRIPTS, md, write_tree
from test_vendor_codes import CSV_PAIR, SIDECAR_PAIR

SCHEMES = """
[vendor_schemes.wtc-gb]
label = { en = "WTC-GB boiler automat", fr = "Automate de la chaudière WTC-GB" }
document = "83251704"
pattern = "[PiWF][0-9]{2}"

[vendor_schemes.wcm]
label = { en = "WCM fault codes", fr = "Codes défauts WCM" }
document = "83277504"
pattern = "[0-9]{3}"
"""

LISTS = """
[vendor_code_lists.boiler-faults]
scheme = "wtc-gb"
label = { en = "Boiler fault codes", fr = "Codes défauts de la chaudière" }
source = "manual 83251704, pp. 84-87"
evidence = "codes"
status = "proposed"

[vendor_code_lists.boiler-faults.entries]
11 = { codes = ["F11"], label = { en = "Limiter above 105 °C", fr = "Limiteur au-dessus de 105 °C" } }
15 = { codes = ["W15", "F15"], label = { en = "Flow/return difference", fr = "Écart départ/retour" } }

[vendor_code_lists.wcm-faults]
scheme = "wcm"
label = { en = "WCM fault codes", fr = "Codes défauts WCM" }
source = "manual 83277504, pp. 106-108"
evidence = "codes"
status = "proposed"

[vendor_code_lists.wcm-faults.entries]
181 = { codes = ["181"], label = { en = "No communication with a room unit", fr = "Pas de communication avec une commande à distance" } }
"""

USE = """
[[vendor_code_list_use]]
circuits = ["ka"]
messages = ["Limits"]
field = "lower"
lists = ["boiler-faults", "wcm-faults"]
evidence = "codes"
"""

EVIDENCE = """# Codes
Lists boiler-faults (F11, W15, F15) and wcm-faults (181).
| message | field |
|---|---|
| Limits | lower |
| PumpState | value |
| BlockingTime | value |
"""


class TestCodeLists(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = self.tmp.name
        self.en_tree = os.path.join(self.root, "en")
        self.fr_tree = os.path.join(self.root, "fr")
        self.ev_dir = os.path.join(self.root, "evidence")
        os.makedirs(self.ev_dir)
        for name, text in (("sample", "BlockingTime PumpState Limits\n"), ("codes", EVIDENCE)):
            with open(os.path.join(self.ev_dir, name + ".md"), "w", encoding="utf-8") as f:
                f.write(text)
        write_tree(self.en_tree, SAMPLE_CSV_KA + CSV_PAIR)
        write_tree(self.fr_tree, SAMPLE_CSV_KA_FR + CSV_PAIR)
        self.sidecar = os.path.join(self.root, "weishaupt.toml")
        self.orig_ev = md.EVIDENCE
        md.EVIDENCE = self.ev_dir

    def tearDown(self):
        md.EVIDENCE = self.orig_ev
        self.tmp.cleanup()

    def problems(self, extra):
        with open(self.sidecar, "w", encoding="utf-8") as f:
            f.write(SAMPLE_SIDECAR + SIDECAR_PAIR + extra)
        msgs, _, _ = md.read_tree(self.en_tree)
        return md.resolve(md.load(self.sidecar), msgs)[1]

    def assertProblem(self, extra, text):
        p = self.problems(extra)
        self.assertTrue(any(text in x for x in p), p)

    def test_valid_lists_pass(self):
        self.assertEqual(self.problems(SCHEMES + LISTS + USE), [])

    def test_build_emits_lists_and_matches_schema(self):
        with open(self.sidecar, "w", encoding="utf-8") as f:
            f.write(SAMPLE_SIDECAR + SIDECAR_PAIR + SCHEMES + LISTS + USE)
        out = os.path.join(self.root, "meta.json")
        env = dict(os.environ, EVIDENCE_DIR=self.ev_dir)
        r = subprocess.run([sys.executable, os.path.join(SCRIPTS, "metadata.py"), "build", self.sidecar,
                            self.en_tree, out, "--version", "1.0.0", "--commit", "abcdef1",
                            "--lang", f"fr={self.fr_tree}"], capture_output=True, text=True, env=env)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("code lists boiler-faults (2), wcm-faults (1) on 1 fields", r.stdout)
        doc = json.load(open(out, encoding="utf-8"))
        bl = doc["vendor_code_lists"]["boiler-faults"]
        self.assertEqual(bl["scheme"], "wtc-gb")
        self.assertEqual(bl["status"], "proposed")
        self.assertEqual(list(bl["entries"]), ["11", "15"])
        self.assertEqual(bl["entries"]["15"]["codes"], ["W15", "F15"])
        lim = doc["messages"]["ka/Limits"]
        self.assertEqual(lim["fields"][0]["code_lists"], ["boiler-faults", "wcm-faults"])
        self.assertNotIn("code_lists", lim["fields"][1])
        self.assertEqual(lim["evidence"], ["sample", "codes"])
        v = subprocess.run([sys.executable, os.path.join(SCRIPTS, "validate-schema.py"),
                            os.path.join(SCHEMAS, "metadata.schema.json"), out], capture_output=True, text=True)
        self.assertEqual(v.returncode, 0, v.stdout + v.stderr)

    def test_no_lists_keeps_output_without_new_keys(self):
        with open(self.sidecar, "w", encoding="utf-8") as f:
            f.write(SAMPLE_SIDECAR + SIDECAR_PAIR + SCHEMES)
        msgs, _, _ = md.read_tree(self.en_tree)
        side = md.load(self.sidecar)
        resolved, bad = md.resolve(side, msgs)
        self.assertEqual(bad, [])
        data = md.assemble(side, msgs, resolved, {"en": msgs})
        self.assertNotIn("vendor_code_lists", data)
        self.assertFalse(any("code_lists" in f for m in data["messages"].values() for f in m["fields"]))

    def test_list_needs_known_scheme_label_source_status(self):
        self.assertProblem(SCHEMES + LISTS.replace('scheme = "wcm"', 'scheme = "other"') + USE,
                           "scheme 'other' is not in [vendor_schemes]")
        self.assertProblem(SCHEMES + LISTS.replace(', fr = "Codes défauts WCM" }\nsource', ' }\nsource') + USE,
                           "label needs")
        self.assertProblem(SCHEMES + LISTS.replace('source = "manual 83277504, pp. 106-108"\n', '') + USE,
                           "no source")
        self.assertProblem(SCHEMES + LISTS.replace('status = "proposed"', 'status = "draft"', 1) + USE,
                           "status must be one of")

    def test_code_must_be_spelled_and_carry_its_number(self):
        self.assertProblem(SCHEMES + LISTS.replace('["F11"]', '["F 11"]') + USE, "not spelled as")
        self.assertProblem(SCHEMES + LISTS.replace('["F11"]', '["F12"]') + USE, "does not carry the number 11")
        self.assertProblem(SCHEMES + LISTS.replace('["181"]', '["F81"]') + USE, "not spelled as")

    def test_entry_needs_label_in_every_language(self):
        self.assertProblem(SCHEMES + LISTS.replace(', fr = "Limiteur au-dessus de 105 °C"', '') + USE, "label needs")

    def test_evidence_must_name_list_and_codes(self):
        self.assertProblem(SCHEMES + LISTS.replace('["F11"]', '["W11"]') + USE, "does not name W11")
        self.assertProblem(SCHEMES + LISTS.replace('evidence = "codes"', 'evidence = "missing"', 1) + USE,
                           "is not under")

    def test_use_checks_message_field_and_lists(self):
        self.assertProblem(SCHEMES + LISTS + USE.replace('"lower"', '"middle"'), "has no field 'middle'")
        self.assertProblem(SCHEMES + LISTS + USE.replace('["Limits"]', '["Nothing"]'), "no message Nothing")
        self.assertProblem(SCHEMES + LISTS + USE.replace('"wcm-faults"]', '"other"]'), "ids of [vendor_code_lists]")
        self.assertProblem(SCHEMES + LISTS + USE + USE, "already has code lists")

    def test_use_on_value_list_field_fails(self):
        use = USE.replace('["Limits"]', '["PumpState"]').replace('"lower"', '"value"')
        self.assertProblem(SCHEMES + LISTS + use, "has a value list in the CSV")

    def test_lists_of_one_field_share_no_number(self):
        lists = LISTS + '182 = { codes = ["182"], label = { en = "x", fr = "x" } }\n'
        lists = lists.replace('181 = { codes = ["181"]', '15 = { codes = ["015"]')
        self.assertProblem(SCHEMES + lists + USE, "both have 15")


if __name__ == "__main__":
    unittest.main()
