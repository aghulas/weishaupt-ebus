"""Deep unit test coverage for all workbench Python scripts."""
import importlib.util
import io
import json
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from unittest.mock import patch

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
val = load_module("validate_schema", "validate-schema.py")
rn = load_module("render_notice", "render-notice.py")
rs = load_module("register_survey", "register-survey.py")
sc = load_module("survey_crosscheck", "survey-crosscheck.py")


CSV_KA = """type,circuit,level,name,comment,qq,zz,pbsb,id,*name,part,type,divisor/values,range,unit,comment
r,ka,,BlockingTime,[WCRC] burner lock-out time,,15,5022,4c2500,value,,UIN,,1-60,min,minutes
w,ka,,BlockingTime,[WCRC] burner lock-out time,,15,5023,4c2500,value,,UIN,,1-60,min,minutes
u,ka,,Boiler1Power,burner load,03,10,0504,,load,,UCH,,,%,load
"""

CSV_KA_FR = """type,circuit,level,name,comment,qq,zz,pbsb,id,*name,part,type,divisor/values,range,unit,comment
r,ka,,BlockingTime,[WCRC] temps de blocage,,15,5022,4c2500,value,,UIN,,1-60,min,minutes_fr
w,ka,,BlockingTime,[WCRC] temps de blocage,,15,5023,4c2500,value,,UIN,,1-60,min,minutes_fr
u,ka,,Boiler1Power,charge bruleur,03,10,0504,,load,,UCH,,,%,charge
"""

CSV_KA_DIFF = """type,circuit,level,name,comment,qq,zz,pbsb,id,*name,part,type,divisor/values,range,unit,comment
r,ka,,BlockingTime,[WCRC] temps de blocage,,15,5022,4c2500,value,,SIN,,1-60,min,minutes_fr
w,ka,,BlockingTime,[WCRC] temps de blocage,,15,5023,4c2500,value,,UIN,,1-60,min,minutes_fr
u,ka,,Boiler1Power,charge bruleur,03,10,0504,,load,,UCH,,,%,charge
"""


def write_file(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


class TestRegisterSurveyAndCrosscheck(unittest.TestCase):
    def test_crc_and_request(self):
        # Known Weishaupt CRC-8 (poly 0x5C): register 25 00 -> 0x4c
        self.assertEqual(rs.crc(bytes.fromhex("25 00")), 0x4C)
        self.assertEqual(rs.request("15", [0x0025]), "155022034c2500")
        self.assertEqual(list(rs.blocks([3, 1, 2, 4, 5], 2)), [[1, 2], [3, 4], [5]])

    def test_survey_pass1_and_pass2(self):
        with tempfile.TemporaryDirectory() as tmp:
            for name in rs.FILES.values():
                write_file(os.path.join(tmp, name + ".csv"), CSV_KA if name == "15.w.ka" else "type,circuit,level,name,comment,qq,zz,pbsb,id\n")
            self.assertIn(0x0025, rs.defined(tmp, "15"))

            cat_path = os.path.join(tmp, "cat.csv")
            write_file(cat_path, "\n".join([
                "device,read_at,access,register,bus_bytes,vendor_param,meaning,type,factor,unit,min,max,status",
                "system manager (KA),manager,register,4000,a0 0f,P1,extra,UIN,1,K,0,10,on-installation",
                "room unit FS 2.0 with its modules,module,register,4001,a1 0f,P2,mod,UIN,1,,0,10,on-installation",
                "room unit FS 2.0 with its modules,address 30,register,4002,a2 0f,P3,skip,UIN,1,,0,10,on-installation",
                "boiler,boiler,memory,10,0a 00,P4,mem,UIN,1,,0,10,on-installation",
            ]) + "\n")
            extra = rs.catalogue_extra(cat_path)
            self.assertEqual(extra["manager"], {4000})
            self.assertEqual(extra["module"], {4001})

            res_path = os.path.join(tmp, "res.csv")
            write_file(res_path, "\n".join([
                "zz,reg_dec,reg_hex,raw,status",
                "08,10,0a 00,05 00,ok",
                "08,11,0b 00,00 80,ok",
                "08,12,0c 00,,timeout",
            ]) + "\n")

            with patch.object(rs, "RANGES", {"boiler": [(0, 4)], "manager": [(0x25, 0x27)], "module": [(0, 2)], "room": [(0, 2)]}):
                out1, err1 = io.StringIO(), io.StringIO()
                with patch.object(sys, "argv", ["register-survey.py", tmp, "pass1"]), \
                        redirect_stdout(out1), redirect_stderr(err1):
                    rs.main()
                self.assertIn("chunk,seq,zz,registers,request", out1.getvalue())
                self.assertIn("requests,", err1.getvalue())

                out2, err2 = io.StringIO(), io.StringIO()
                with patch.object(sys, "argv", ["register-survey.py", tmp, "pass2", res_path, cat_path]), \
                        redirect_stdout(out2), redirect_stderr(err2):
                    rs.main()
                self.assertIn("18,000a", out2.getvalue())
                self.assertIn("08,000c", out2.getvalue())

    def test_survey_crosscheck_value_and_main(self):
        self.assertEqual(sc.value("0a 00", "UIN", "0.1"), 1.0)
        self.assertEqual(sc.value("ff ff", "SIN", "1"), -1.0)
        self.assertEqual(sc.value("05 00", "UIN", "bad"), 5)

        with tempfile.TemporaryDirectory() as tmp:
            res_path = os.path.join(tmp, "res.csv")
            cat_path = os.path.join(tmp, "cat.csv")
            write_file(res_path, "\n".join([
                "zz,reg_dec,reg_hex,raw,status",
                "15,1,01 00,05 00,ok",
                "15,2,02 00,00 80,ok",
                "15,3,03 00,ff 00,ok",
                "15,99,63 00,07 00,ok",
            ]) + "\n")
            write_file(cat_path, "\n".join([
                "device,read_at,access,register,bus_bytes,vendor_param,meaning,type,factor,unit,min,max,status",
                "system manager (KA),manager,register,1,01 00,P1,inrange,UIN,1,K,0,10,on-installation",
                "system manager (KA),manager,register,2,02 00,P2,na,UIN,1,K,0,10,on-installation",
                "system manager (KA),manager,register,3,03 00,P3,outrange,UIN,1,K,0,10,on-installation",
                "system manager (KA),manager,register,4,04 00,P4,missing,UIN,1,K,0,10,on-installation",
                "system manager (KA),manager,register,5,05 00,P5,off,UIN,1,K,0,10,not-installed",
                "boiler,boiler,memory,6,06 00,P6,skip,UIN,1,K,0,10,on-installation",
            ]) + "\n")
            out = io.StringIO()
            with patch.object(sys, "argv", ["survey-crosscheck.py", res_path, cat_path]), redirect_stdout(out):
                sc.main()
            txt = out.getvalue()
            self.assertIn("answers, in range", txt)
            self.assertIn("`00 80`", txt)
            self.assertIn("outside the range", txt)
            self.assertIn("not surveyed yet", txt)
            self.assertIn("`63 00`", txt)


class TestI18nKeysCLI(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.en = os.path.join(self.tmp.name, "en")
        self.fr = os.path.join(self.tmp.name, "fr")
        self.bad = os.path.join(self.tmp.name, "bad")
        write_file(os.path.join(self.en, "wolf", "15.w.ka.csv"), CSV_KA)
        write_file(os.path.join(self.fr, "wolf", "15.w.ka.csv"), CSV_KA_FR)
        write_file(os.path.join(self.bad, "wolf", "15.w.ka.csv"), CSV_KA_DIFF)
        self.yaml_ok = os.path.join(self.tmp.name, "fr.yaml")
        write_file(self.yaml_ok, "\n".join([
            "burner lock-out time: temps de blocage",
            "minutes: minutes_fr",
            "burner load: charge bruleur",
            "load: charge",
        ]) + "\n")
        self.yaml_extra = os.path.join(self.tmp.name, "extra.yaml")
        write_file(self.yaml_extra, "orphan key: valeur\nburner lock-out time: temps de blocage\n")

    def tearDown(self):
        self.tmp.cleanup()

    def test_list_check_and_compare_in_process(self):
        out = io.StringIO()
        with patch.object(sys, "argv", ["i18n-keys.py", self.en, "list"]), redirect_stdout(out):
            i18n.main()
        self.assertIn("burner lock-out time", out.getvalue())

        out = io.StringIO()
        with patch.object(sys, "argv", ["i18n-keys.py", self.en, "check", self.yaml_ok, "--strict"]), \
                redirect_stdout(out), self.assertRaises(SystemExit) as cm:
            i18n.main()
        self.assertEqual(cm.exception.code, 0)
        self.assertIn("0 strings without a key", out.getvalue())

        out = io.StringIO()
        with patch.object(sys, "argv", ["i18n-keys.py", self.en, "check", self.yaml_extra, "--strict"]), \
                redirect_stdout(out), self.assertRaises(SystemExit) as cm:
            i18n.main()
        self.assertEqual(cm.exception.code, 1)

        out = io.StringIO()
        with patch.object(sys, "argv", ["i18n-keys.py", self.en, "compare", self.fr]), redirect_stdout(out):
            i18n.main()
        self.assertIn("compare: ok", out.getvalue())

        out = io.StringIO()
        with patch.object(sys, "argv", ["i18n-keys.py", self.en, "compare", self.bad]), \
                redirect_stdout(out), self.assertRaises(SystemExit) as cm:
            i18n.main()
        self.assertEqual(cm.exception.code, 1)


class TestFixturesDecodeAndCLI(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.en = os.path.join(self.tmp.name, "en")
        self.ev = os.path.join(self.tmp.name, "evidence")
        write_file(os.path.join(self.en, "wolf", "15.w.ka.csv"), CSV_KA)
        write_file(os.path.join(self.ev, "rec.md"), "\n".join([
            "# Record",
            "2026-11-18",
            "| BlockingTime | `4c 25 00` | `01 00` | 1 |",
            "| BlockingTime write | `cc 25 00 02 00` | `` | 2 |",
            "| Boiler1Power | `03 10 05 04 01 32` | | 50 |",
        ]) + "\n")
        self.toml = os.path.join(self.tmp.name, "fixtures.toml")
        write_file(self.toml, """schema = 2

[[block]]
evidence = "rec"
date = "2026-11-18"
where = "text"
readings = [
  { circuit = "ka", message = "BlockingTime", type = "read", qq = "31", zz = "15", pbsb = "5022", master = "4c 25 00", slave = "01 00", expect = { value = 1 } },
  { circuit = "ka", message = "BlockingTime", type = "write", qq = "ff", zz = "15", pbsb = "5023", master = "cc 25 00 02 00", slave = "", expect = { value = 2 } },
  { circuit = "ka", message = "Boiler1Power", type = "passive", qq = "03", zz = "10", pbsb = "0504", master = "32", expect = { load = 50 } },
]
""")
        self.orig_ev = md.EVIDENCE
        md.EVIDENCE = self.ev
        fx.record_lines.__defaults__[0].clear()

    def tearDown(self):
        md.EVIDENCE = self.orig_ev
        fx.record_lines.__defaults__[0].clear()
        self.tmp.cleanup()

    def test_decode_with_mocked_ebusd_and_build_cli(self):
        fake_log = "\n".join([
            '[update notice] received read ka BlockingTime QQ=31: 1',
            '[main notice] executed command "read -m 1000 -v -c ka BlockingTime": ka BlockingTime value=1',
            '[update notice] received write ka BlockingTime QQ=ff: 2',
            '[main notice] executed command "find -w -e -d -v -c ka BlockingTime": ka BlockingTime = value=2',
            '[update notice] received update-read ka Boiler1Power QQ=03: 50',
            '[main notice] executed command "read -m 1000 -v -c ka Boiler1Power": ka Boiler1Power load=50',
        ])
        sidecar = os.path.join(self.tmp.name, "sidecar.toml")
        write_file(sidecar, """schema = 1
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
[devices.manager]
type = "manager"
circuits = ["ka"]
label = { en = "Manager", fr = "Manager" }
[menus.manager.root]
parent = ""
label = { en = "Root", fr = "Racine" }
source = "p1"
[[entry]]
circuits = ["ka"]
message = "BlockingTime"
menu = "root"
kind = "setting"
label = { en = "Blocking", fr = "Blocage" }
evidence = ["rec"]
[entry.write]
source = "ff"
risk = "regulation"
proof = "change-observed"
[[entry]]
circuits = ["ka"]
message = "Boiler1Power"
menu = "root"
kind = "live"
label = { en = "Power", fr = "Puissance" }
evidence = ["rec"]
""")
        fake_bin = os.path.join(self.tmp.name, "ebusd")
        write_file(fake_bin, "")
        out_json = os.path.join(self.tmp.name, "fixtures.json")
        buf = io.StringIO()
        with patch.object(fx, "run_ebusd", return_value=fake_log), \
                patch.object(sys, "argv", [
                    "fixtures.py", "build", self.toml, self.en, out_json,
                    "--version", "1.0.0", "--commit", "abcdef1", "--sidecar", sidecar,
                    "--ebusd", fake_bin, "--release", "v26.1-test",
                ]), redirect_stdout(buf):
            fx.main()
        self.assertTrue(os.path.exists(out_json))
        # Validate against schemas/fixtures.schema.json in-process!
        vbuf = io.StringIO()
        with patch.object(sys, "argv", ["validate-schema.py", os.path.join(SCHEMAS, "fixtures.schema.json"), out_json]), \
                redirect_stdout(vbuf):
            val.main()
        self.assertIn("schema: ok", vbuf.getvalue())

    def test_check_without_ebusd_fallback(self):
        buf = io.StringIO()
        with patch.object(sys, "argv", ["fixtures.py", "check", self.toml, self.en]), redirect_stdout(buf):
            fx.main()
        self.assertIn("fixtures.toml: ok", buf.getvalue())


class TestValidateSchemaAndRenderNoticeCLI(unittest.TestCase):
    def test_validate_schema_fallback_without_jsonschema(self):
        with tempfile.TemporaryDirectory() as tmp:
            good = os.path.join(tmp, "good.json")
            bad = os.path.join(tmp, "bad.json")
            write_file(good, json.dumps({"schema": 1}))
            write_file(bad, json.dumps({"schema": 2}))
            with patch.dict(sys.modules, {"jsonschema": None}):
                buf = io.StringIO()
                with patch.object(sys, "argv", ["validate-schema.py", os.path.join(SCHEMAS, "metadata.schema.json"), good]), \
                        redirect_stdout(buf):
                    val.main()
                self.assertIn("basic check only", buf.getvalue())

                with patch.object(sys, "argv", ["validate-schema.py", os.path.join(SCHEMAS, "metadata.schema.json"), bad]), \
                        self.assertRaises(SystemExit):
                    val.main()

                with patch.object(sys, "argv", ["validate-schema.py", os.path.join(SCHEMAS, "metadata.schema.json"), good, "--require-jsonschema"]), \
                        self.assertRaises(SystemExit):
                    val.main()

    def test_render_notice_main_cli(self):
        with tempfile.TemporaryDirectory() as tmp:
            tpl = os.path.join(tmp, "tpl.md")
            write_file(tpl, "Version @VERSION@@PROVISIONAL_SENTENCE@")
            buf = io.StringIO()
            with patch.object(sys, "argv", ["render-notice.py", tpl, "VERSION=1.0.0", "PROVISIONAL="]), \
                    redirect_stdout(buf):
                rn.main()
            self.assertEqual(buf.getvalue(), "Version 1.0.0")


if __name__ == "__main__":
    unittest.main()
