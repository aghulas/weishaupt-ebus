#!/usr/bin/env python3
"""Request list of the read-only register survey (evidence/register-survey-plan.md). Sends nothing.

Usage:
  scripts/register-survey.py <csv-dir> pass1 > requests.csv
  scripts/register-survey.py <csv-dir> pass2 <results.csv> [<catalogue.csv>] > requests.csv

<csv-dir> is the folder `kromschroeder/` of a release archive; every register a `50 22` read line
of it already defines is left out. pass1 surveys one device of each type (08, 15, 51, 35);
pass2 reads, on the other devices of the same type (18, 52, 75, f5), the registers that answered
in pass 1 with something other than 0x8000; on every device of a type, the registers of the
vendor-software catalogue (evidence/register-candidates.csv, status on-installation) that the
pass-1 ranges miss; and, on the pass-1 devices, the requests that failed, one register each.

Each request reads four registers in one `50 22` telegram (ID `<crc>` plus four addresses, the
checksum over the eight address bytes, as ebusd's own four-register reads on this bus), one on
the boilers. Output: one CSV row per request, grouped in chunks of at most CHUNK requests.
"""
import csv, glob, os, sys

CHUNK = 480          # 20 minutes at one request every 2.5 s
GAP_S = 2.5

# register ranges per device type, decimal, half-open; the weekly-program space (0x1400-0x1aff)
# is left out: its scheme is known and every program is defined or read already
RANGES = {
    "boiler": [(0x0000, 0x0400)],
    "manager": [(0x0000, 0x0400), (0x0500, 0x0600), (0x0900, 0x0c00), (0x1300, 0x1400), (0xfd00, 0xfe00)],
    "module": [(0x0000, 0x0400), (0x0900, 0x0c00)],
    "room": [(0x0000, 0x0400), (0x0900, 0x0c00), (0x1300, 0x1400)],
}
# registers per request: four where ebusd's own four-register reads were seen on this bus (15, 35,
# 51, 52, telegram log of 2026-11-10 to 2026-11-18); one on the boiler automats (never seen there)
SIZE = {"boiler": 1, "manager": 4, "module": 4, "room": 4}
TYPE = {"08": "boiler", "18": "boiler", "15": "manager", "51": "module", "52": "module",
        "35": "room", "75": "room", "f5": "room"}
PASS1 = {"08": "boiler", "15": "manager", "51": "module", "35": "room"}
PASS2 = {"18": "08", "52": "51", "75": "35", "f5": "35"}  # device: the device of pass 1 it follows
FILES = {"08": "08.w.bc1", "18": "18.w.bc2", "15": "15.w.ka", "50": "50.w.em1", "51": "51.w.em2",
         "52": "52.w.em3", "35": "35.w.fs1", "75": "75.w.fs2", "f5": "f5.w.fs3"}


def crc(d):
    c = d[0]
    for b in d[1:]:
        for _ in range(8):
            c = ((c << 1) ^ 0x5C) & 0xFF if c & 0x80 else (c << 1) & 0xFF
        c ^= b
    return c


def defined(csvdir, zz):
    regs = set()
    files = [FILES[zz]] + (["50.w.em1"] if zz == "15" else [])  # 50 is the same device as 15
    for name in files:
        for row in csv.reader(open(os.path.join(csvdir, name + ".csv"), encoding="utf-8")):
            if len(row) > 8 and row[7] == "5022" and len(row[8]) == 6:
                regs.add(int(row[8][4:6] + row[8][2:4], 16))
    return regs


def catalogue_extra(path):
    """Registers of the vendor-software catalogue on the installation, outside the pass-1 ranges."""
    out = {}
    for c in csv.DictReader(open(path, encoding="utf-8")):
        if c["access"] != "register" or c["status"] != "on-installation" or not c["register"].isdigit():
            continue
        if c["read_at"].startswith("address"):
            continue  # read at a master address, not a slave: not a 50 22 register of a device
        typ = ("manager" if c["device"].startswith("system manager") else
               "module" if c["read_at"] == "module" else "room")
        reg = int(c["register"])
        if not any(a <= reg < b for a, b in RANGES[typ]):
            out.setdefault(typ, set()).add(reg)
    return out


def blocks(regs, size):
    regs = sorted(regs)
    while regs:
        yield regs[:size]
        regs = regs[size:]


def request(zz, regs):
    addr = b"".join(bytes([r & 0xFF, r >> 8]) for r in regs)
    data = bytes([crc(addr)]) + addr
    return f"{zz}5022{len(data):02x}{data.hex()}"


def main():
    csvdir, mode = sys.argv[1], sys.argv[2]
    plan = []
    if mode == "pass1":
        for zz, typ in PASS1.items():
            known = defined(csvdir, zz)
            regs = [r for a, b in RANGES[typ] for r in range(a, b) if r not in known]
            plan += [(zz, blk) for blk in blocks(regs, SIZE[typ])]
    else:
        answered, failed = {}, {}
        for row in csv.DictReader(open(sys.argv[3], encoding="utf-8")):
            if row["status"] == "ok" and row["raw"] not in ("00 80", ""):
                answered.setdefault(row["zz"], set()).add(int(row["reg_dec"]))
            elif row["status"] != "ok":
                failed.setdefault(row["zz"], set()).add(int(row["reg_dec"]))
        extra = catalogue_extra(sys.argv[4] if len(sys.argv) > 4 else "evidence/register-candidates.csv")
        # pass-1 devices: the failed requests again, one register each, and the catalogue's
        # on-installation registers outside the pass-1 ranges
        for zz, typ in PASS1.items():
            known = defined(csvdir, zz)
            plan += [(zz, [r]) for r in sorted(failed.get(zz, ()))]
            plan += [(zz, blk) for blk in blocks((r for r in extra.get(typ, ()) if r not in known), SIZE[typ])]
        # the other devices of each type: what answered on the pass-1 device, and the same extras
        for zz, src in PASS2.items():
            known = defined(csvdir, zz)
            regs = (answered.get(src, set()) | extra.get(TYPE[zz], set())) - known
            plan += [(zz, blk) for blk in blocks(regs, SIZE[TYPE[zz]])]
    w = csv.writer(sys.stdout)
    w.writerow(["chunk", "seq", "zz", "registers", "request"])
    for i, (zz, blk) in enumerate(plan):
        w.writerow([i // CHUNK + 1, i + 1, zz, " ".join(f"{r:04x}" for r in blk), "hex " + request(zz, blk)])
    n = len(plan)
    print(f"# {n} requests, {sum(len(b) for _, b in plan)} registers, {-(-n // CHUNK)} chunks, "
          f"{n * GAP_S / 3600:.1f} h of bus time at one request every {GAP_S} s", file=sys.stderr)


if __name__ == "__main__":
    main()
