# register — the 5023 write ID carries a CRC-8 over address and value

## What

A Kromschröder/Weishaupt register **write** (`PBSB = 50 23`) carries, as master data,

```
<crc> <addr> <sub> <value low> <value high>
```

One register per telegram, value 16 bits, low byte first. `<crc>` is the same CRC-8 as on a
read (polynomial 0x5C, no reflection, initial value = first byte, see
[register-crc.md](register-crc.md)), computed over **all bytes that follow it**: the two
address bytes and the two value bytes. The slave acknowledges with `00`.

Because the checksum covers the value, it cannot be written into a definition. In lot C
(branch `weishaupt-C`) the write template `crcw` (`@write @base(MF, 0x23)`,
`src/wolf/wtc_inc.tsp`) leaves it to ebusd: the `@wcrc` decorator emits the marker `[WCRC]` in the comment and, in place of the
checksum, the checksum of the address alone, and ebusd with the run-time checksum (john30/ebusd#1825)
computes the byte when sending and checks it when receiving.

## How it was established

### 1. Write telegrams seen on the bus

Passive capture (ebusd `grab result all`, nothing sent for this record), snapshots of
2026-11-16 10:45 to 18:01. 26 distinct `50 23` telegrams, to the system manager (`15`), a room
unit (`35`) and a heating module (`51`). None came from a device of the vendor: all were sent
through ebusd by the operator of the installation, from source address `ff` (23 telegrams) or
from the address of ebusd, `31` (3 telegrams). The vendor service tool sent no write during its
sessions ([service-tool-log.md](service-tool-log.md)), and the room units write to the heating
modules with `09 03`, which has no checksum.

The checksum of each of the 26 was recomputed offline with the routine below: 26 of 26 match.
All 26 were acknowledged (`00`). Master data of each (`<crc> <addr> <sub> <value>`):

| ZZ | from `ff` | from `31` |
|---|---|---|
| `15` | `e8 01 01 01 00`, `28 25 00 01 00`, `bf 40 01 ce ff`, `90 80 01 00 00`, `72 87 05 58 02`, `90 9e 02 64 00`, `98 9f 02 64 00`, `46 b1 09 58 02`, `8c ca fd 00 00`, `d8 cb fd 01 00`, `0c e2 fd 14 00`, `70 e7 fd 50 00`, `d4 ec fd 32 00`, `b4 f3 13 00 00` | `5f e6 fd 11 03` |
| `35` | `d8 10 01 03 00`, `a8 11 01 14 00`, `50 41 01 01 00`, `a4 be 02 00 00` | |
| `51` | `d8 05 00 d7 00`, `b0 08 00 d7 00`, `a4 0e 01 64 00`, `7c 14 0a 64 00`, `dc 16 01 c8 00` | `66 28 00 ee 02`, `70 2b 01 50 00` |

```python
def crc(data):            # data = the bytes after the checksum
    c = data[0]
    for b in data[1:]:
        for _ in range(8):
            c = ((c << 1) ^ 0x5C) & 0xFF if c & 0x80 else (c << 1) & 0xFF
        c ^= b
    return c
# crc(bytes.fromhex("25000100")) == 0x28
```

### 2. A figure that does not come from this installation

These telegrams were built by the same routine that checks them, so the match above only shows
that the capture is intact. Two independent points:

- The read checksum is proven against frames of the vendor's own devices
  ([register-crc.md](register-crc.md)), and the write uses the same routine over a longer
  payload.
- john30/ebusd issue 167 (comment of 2025-12-16) quotes a write on a Wolf boiler of the same
  `50 23` family, taken from the vendor's gateway: ID `d8 42 01` followed by the value
  `04 00 5d 01 00 00`. The routine above over `42 01 04 00 5d 01 00 00` gives `d8`.

### 3. Decoding with the lot

The lot was compiled and loaded in the ebusd build that has the run-time checksum (fork
release `v26.1-weishaupt.1`, the build `scripts/check.sh` uses), in a container without any
bus device, and the 17 telegrams of the registers of the lot were injected as already seen
messages (`--inject=stop`). 17 of 17 were decoded as `write` of the expected message with the
expected value (list in [settings-writes.md](settings-writes.md)). The same telegram with a
wrong checksum (`29 25 00 01 00` for `28 …`) was reported as unknown, and the read
`4c 25 00 / 02 01 00` was decoded as `read ka BlockingTime 1`.

### 4. Which source address a device takes a value from

Recorded in `docs/discoveries.md` on 2026-10-30 from write tests by the operator: most settings
are acknowledged from any master but taken only from source address `ff`, the address of the
vendor service tool; the rule is per register. One captured case agrees with it: the last write
seen to the de-couple maximum of the system manager (`e6 fd`) came from `31` with `11 03`
(78.5) and was acknowledged; the snapshots up to 2026-11-16 18:01 show no later write to that
register, the captures taken since ebusd was restarted show no `50 23` at all, and a read on
2026-11-17 (`dd e6 fd`) answered `0c 03` (78.0). A write between those two captures would not
have been seen, so this is an indication, not a proof.

The definitions of the lot set no source address. A comment in each file says which source the
device takes the value from; the sender chooses it (`write -s ff`).

### 5. The byte emitted in place of the checksum

First version of `@wcrc` (commit `5490298` of the ebus-typespec fork): the byte was `00`, on
the write line and on the read line of a read / write setting (`50 22`, `00 25 00`). Such a
read needs the run-time checksum too; on an ebusd without it the request would go out with
checksum `00`, and `BlockingTime` lost the read it has in lot A.

Since 2026-11-17 (local commit `7e85886`, branch `wcrc-decorator`) the decorator emits the
checksum of the address alone, polynomial 0x5C, which is the checksum of a read:

- john30/ebusd#1825 does not use the value of that byte: the message key is built with the
  byte cleared, the comparison of an incoming telegram skips it and checks the computed
  checksum instead, and the byte is overwritten before sending (`keyId`, `checkId`,
  `prepareMaster` in `src/lib/ebus/message.cpp` of the branch).
- Lot C, unchanged, compiled with that build: the 17 read lines carry the checksum of the
  address, for instance `50 22` / `4c 25 00` for `BlockingTime`, the ID lot A ships; no line
  carries `00`. `scripts/check.sh` clean, 167 messages. The 91 tests of the library pass.
- In the ebusd of the check, without a bus, telegrams injected as already seen
  (`--inject=stop`): `28 25 00 01 00` and `cc 25 00 02 00` decoded as `write ka BlockingTime`
  1 and 2, `29 25 00 01 00` (wrong checksum) unknown, the read `4c 25 00` / `02 01 00` decoded
  as `read ka BlockingTime 1`, and a read with `00 25 00` unknown.

So a read defined with `@wcrc` is valid for an ebusd with or without the run-time checksum;
the write still needs it.

## Equipment

Kromschröder WCM regulators on eBUS, all scanning as `MF=Kromschröder`, `ID=W`: system manager
(SW=6618), room unit (SW=2726), heating module (SW=7203). ebusd 26.1 with the run-time
checksum.

## Date

Capture 2026-11-16; checksums recomputed and telegrams decoded with the lot on 2026-11-17.

## Not verified

- No write from a device or tool of the vendor was captured on this installation: the service
  tool was only used for reading.
- Whether the regulators check the checksum of a write. `docs/discoveries.md` (2026-10-30)
  records that the heating modules do not; nothing is recorded for the system manager and the
  room units. A wrong checksum was never sent for this record.
- The telegram ebusd builds from a definition of the lot was not captured on a bus: decoding of
  captured telegrams is proven, sending is not (rule 7). Test for the operator, with a test
  ebusd loaded with the lot, the service tool disconnected and nothing else sending as `ff`:
  1. `read -f -c ka BlockingTime`: the request on the bus must be `50 22`, data `4c 25 00`.
  2. `write -s ff -c ka BlockingTime 2`: expected telegram `ff 15 50 23 05 cc 25 00 02 00`,
     acknowledged; read again, expected 2.
  3. `write -s ff -c ka BlockingTime 1`: expected `ff 15 50 23 05 28 25 00 01 00`; read
     again, expected 1 (the value before the test).
  4. `write -s ff -c ka BlockingTime 31`: ebusd must refuse it (out of range) and send nothing.
- The telegrams ebusd **sends** with the corrected decorator (below) were not captured either;
  the operator's test above covers them.
- Multi-register writes: `docs/discoveries.md` records one register per telegram; nothing else
  was tried.
