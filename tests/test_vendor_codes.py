"""Unit tests for the vendor codes of the metadata (scripts/metadata.py, schemas/metadata.schema.json).

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

# A message of two fields, as the memory reads of the boilers have.
CSV_PAIR = "r,ka,,Limits,limits,,15,5000,dfb21b,lower,,UCH,,,%,lower limit,upper,,UCH,,,%,upper limit\n"

SIDECAR_PAIR = """
[fields.limits]
lower = { label = { en = "Lower limit", fr = "Limite basse" } }
upper = { label = { en = "Upper limit", fr = "Limite haute" } }

[[entry]]
circuits = ["ka"]
message = "Limits"
menu = "settings"
kind = "setting"
fields = "limits"
label = { en = "Limits", fr = "Limites" }
evidence = ["sample"]
"""

SCHEMES = """
[vendor_schemes.wcm-ka-3]
label = { en = "WCM-KA 3.0 system manager", fr = "Manager de cascade WCM-KA 3.0" }
document = "83258404"
pattern = "[0-9]{3}"

[vendor_schemes.wtc-gb]
label = { en = "WTC-GB boiler automat", fr = "Automate de la chaudière WTC-GB" }
document = "83251704"
pattern = "[Pi][0-9]{2}"
"""

CODE_MSG = """
[[vendor_code]]
circuits = ["ka"]
message = "BlockingTime"
code = "537"
scheme = "wcm-ka-3"
source = "manual 83258404, p. 65"
evidence = "codes"
"""

CODE_FIELD = """
[[vendor_code]]
circuits = ["ka"]
message = "Limits"
field = "lower"
code = "P30"
scheme = "wtc-gb"
source = "manual 83251704, p. 49"
evidence = "codes"
"""

OPEN = """
[[vendor_open]]
circuits = ["ka"]
messages = ["PumpState"]
reason = "circuit-pair"
"""

CODES_EVIDENCE = """# Codes
| message | field | code |
|---|---|---|
| BlockingTime | | 537 |
| Limits | lower | P30 |
| Limits | upper | P31 |
| PumpState | | 538 |
"""


class TestVendorCodes(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = self.tmp.name
        self.en_tree = os.path.join(self.root, "en")
        self.fr_tree = os.path.join(self.root, "fr")
        self.ev_dir = os.path.join(self.root, "evidence")
        os.makedirs(self.ev_dir)
        for name, text in (("sample", "BlockingTime PumpState Limits\n"), ("codes", CODES_EVIDENCE)):
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

    def test_valid_codes_pass(self):
        self.assertEqual(self.problems(SCHEMES + CODE_MSG + CODE_FIELD + OPEN), [])

    def test_build_emits_codes_and_matches_schema(self):
        with open(self.sidecar, "w", encoding="utf-8") as f:
            f.write(SAMPLE_SIDECAR + SIDECAR_PAIR + SCHEMES + CODE_MSG + CODE_FIELD + OPEN)
        out = os.path.join(self.root, "meta.json")
        env = dict(os.environ, EVIDENCE_DIR=self.ev_dir)
        r = subprocess.run([sys.executable, os.path.join(SCRIPTS, "metadata.py"), "build", self.sidecar,
                            self.en_tree, out, "--version", "1.0.0", "--commit", "abcdef1",
                            "--lang", f"fr={self.fr_tree}"], capture_output=True, text=True, env=env)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        doc = json.load(open(out, encoding="utf-8"))
        self.assertEqual(doc["vendor_schemes"]["wcm-ka-3"],
                         {"label": {"en": "WCM-KA 3.0 system manager", "fr": "Manager de cascade WCM-KA 3.0"},
                          "document": "83258404"})
        m = doc["messages"]["ka/BlockingTime"]
        self.assertEqual(m["vendor_codes"], [{"code": "537", "scheme": "wcm-ka-3", "source": "manual 83258404, p. 65"}])
        self.assertEqual(m["evidence"], ["sample", "codes"])
        lim = doc["messages"]["ka/Limits"]
        self.assertNotIn("vendor_codes", lim)
        self.assertEqual(lim["fields"][0]["vendor_codes"][0]["code"], "P30")
        self.assertNotIn("vendor_codes", lim["fields"][1])
        self.assertEqual(doc["open"]["vendor_codes"], ["ka/PumpState"])
        v = subprocess.run([sys.executable, os.path.join(SCRIPTS, "validate-schema.py"),
                            os.path.join(SCHEMAS, "metadata.schema.json"), out], capture_output=True, text=True)
        self.assertEqual(v.returncode, 0, v.stdout + v.stderr)

    def test_no_codes_keeps_output_without_new_keys(self):
        with open(self.sidecar, "w", encoding="utf-8") as f:
            f.write(SAMPLE_SIDECAR + SIDECAR_PAIR)
        msgs, _, _ = md.read_tree(self.en_tree)
        side = md.load(self.sidecar)
        resolved, bad = md.resolve(side, msgs)
        self.assertEqual(bad, [])
        data = md.assemble(side, msgs, resolved, {"en": msgs})
        self.assertNotIn("vendor_schemes", data)
        self.assertNotIn("vendor_codes", data["open"])

    def test_unknown_scheme_fails(self):
        self.assertProblem(SCHEMES + CODE_MSG.replace('"wcm-ka-3"', '"wcm-fs-2"'), "is not in [vendor_schemes]")

    def test_scheme_needs_both_languages_and_document(self):
        self.assertProblem(SCHEMES.replace(', fr = "Manager de cascade WCM-KA 3.0"', ''), "label needs")
        self.assertProblem(SCHEMES.replace('document = "83258404"\n', ''), "document")

    def test_unknown_message_and_field_fail(self):
        self.assertProblem(SCHEMES + CODE_MSG.replace('"BlockingTime"', '"Nothing"'), "no message Nothing")
        self.assertProblem(SCHEMES + CODE_FIELD.replace('"lower"', '"middle"'), "has no field 'middle'")

    def test_field_code_on_single_field_message_fails(self):
        self.assertProblem(SCHEMES + CODE_MSG.replace('code = "537"', 'field = "value"\ncode = "537"'),
                           "the code goes on the message")

    def test_message_and_field_level_together_fail(self):
        both = CODE_FIELD + CODE_FIELD.replace('field = "lower"\n', '').replace('"P30"', '"P31"')
        self.assertProblem(SCHEMES + both, "one level only")

    def test_spelling_as_printed(self):
        self.assertProblem(SCHEMES + CODE_FIELD.replace('"P30"', '"P 30"'), "not spelled as")
        self.assertProblem(SCHEMES + CODE_FIELD.replace('"P30"', '"30"'), "not spelled as")
        self.assertProblem(SCHEMES + CODE_MSG.replace('"537"', '"P537"'), "not spelled as")

    def test_source_and_evidence_required(self):
        self.assertProblem(SCHEMES + CODE_MSG.replace('source = "manual 83258404, p. 65"\n', ''), "no source")
        self.assertProblem(SCHEMES + CODE_MSG.replace('evidence = "codes"\n', ''), "no evidence record")
        self.assertProblem(SCHEMES + CODE_MSG.replace('"codes"', '"missing"'), "is not under")

    def test_evidence_must_name_message_field_and_code(self):
        self.assertProblem(SCHEMES + CODE_MSG.replace('"537"', '"539"'), "does not name 539")
        self.assertProblem(SCHEMES + CODE_FIELD.replace('"lower"', '"upper"').replace('"P30"', '"P99"'),
                           "does not name P99")

    def test_code_on_open_message_fails(self):
        code = CODE_MSG.replace('"BlockingTime"', '"PumpState"').replace('"537"', '"538"')
        self.assertProblem(SCHEMES + code + OPEN, "is open (circuit-pair) but has a vendor code")

    def test_open_twice_and_bad_reason_fail(self):
        self.assertProblem(SCHEMES + OPEN + OPEN, "listed open twice")
        self.assertProblem(SCHEMES + OPEN.replace('"circuit-pair"', '"later"'), "reason must be one of")

    def test_display_and_mismatch_reasons_pass(self):
        for reason in ("display", "mismatch", "manual"):
            self.assertEqual(self.problems(SCHEMES + OPEN.replace('"circuit-pair"', f'"{reason}"')), [])

    def test_duplicate_code_fails(self):
        self.assertProblem(SCHEMES + CODE_MSG + CODE_MSG, "already has wcm-ka-3 537")

    def test_codes_without_schemes_fail(self):
        self.assertProblem(CODE_MSG, "is not in [vendor_schemes]")
        self.assertProblem(OPEN, "vendor codes without [vendor_schemes]")


if __name__ == "__main__":
    unittest.main()
