# ka, em2, fs1 — settings read and written (50 22 / 50 23)

## What

Lot C, branch `weishaupt-C` of the ebusd-configuration fork (on top of the stack of lots since 2026-11-17, first written on `weishaupt-A`). 62 settings
(17 until 2026-11-18, when the three marked † were added, then the two marked ‡ from the
telegram log of ebusd, section "Changes in the telegram log", then the eleven of room units 2
and 3, five of the direct circuit `em1`, six of module `em3` and seven more of room unit 1
from the captures on site, section "Captures on site"),
each emitted as an `r` message (`50 22`) and a `w` message (`50 23`) with the run-time checksum
(mechanism and checksum in [register-write-crc.md](register-write-crc.md)). The value is
16 bits, low byte first.

| circuit (ZZ) | message | addr sub | codec | range in the definition | source |
|---|---|---|---|---|---|
| ka (`15`) | BlockingTime | `25 00` | UIN, min | 0–30 | `ff` |
| ka | ChangeOverTime | `ec fd` | UIN, h | 0–250 | `ff` |
| ka | DeCoupleMinTemp | `e7 fd` | UIN/10, °C | 0–50, step 0.5 | `ff` |
| ka | CalorifierSwitchDiff | `e2 fd` | SIN/10, K | 1–20, step 0.5 | `ff` |
| ka | DHWSwitchDiff | `40 01` | SIN/10, K | -10 – -1, step 0.5 | `ff` |
| ka | DHWLoadTime | `80 01` | UIN, min | 0–180, step 10 | `ff` |
| ka | LegionellaSetpoint | `87 05` | UIN/10, °C | 40–80, step 0.5 | `ff` |
| ka | LegionellaCirculationTime | `b1 09` | UIN, s | 180–1200, step 60 | `ff` |
| ka | RegulationP † | `9f 02` | UIN | 10–300 | `ff` |
| ka | RegulationI † | `9e 02` | UIN | 10–200 | `ff` |
| em2 (`51`) | RoomNormalTemp | `05 00` | UIN/10, °C | 16–35, step 0.5 | `ff` |
| em2 | RoomSetbackTemp | `08 00` | UIN/10, °C | none (10.0–21.5) | `ff` |
| em2 | RoomFrostProtectionTemp | `14 0a` | UIN/10, °C | 4–16, step 0.5 | `ff` |
| em2 | GradientCurve | `0e 01` | UIN/10 | none (2.5–40.0) | `ff` |
| em2 | SummerWinterChangeOverTemp | `16 01` | UIN/10, °C | 8–30, step 0.5 | `ff` |
| em2 | SupplyMaxTemp | `28 00` | UIN/10, °C | 8–82, step 0.5 | `31` |
| em2 | SupplyMinTemp | `2b 01` | UIN/10, °C | 8–82, step 0.5 | `31` |
| fs1 (`35`) | SwitchOnRuntime | `10 01` | UIN, min | 0–10 | `ff` |
| fs1 | FrostProtectionLimitTemp | `be 02` | SIN/10, °C | -20–0, step 0.5 | `ff` |
| fs1 | BoilerMCBoostTemp † | `11 01` | SIN/10, K | 0–20, step 0.5 | `ff` |
| fs1 | RoomFrostProtectionTemp ‡ | `14 0a` | UIN/10, °C | 4–16, step 0.5 | `ff` |
| fs1 | RoomNormalTemp, RoomSetbackTemp, GradientCurve, SummerWinterChangeOverTemp, SupplyMaxTemp, SupplyMinTemp, DHWSetpoint (batch 5) | as on `fs2` | as on `fs2` | as on `fs2` | `ff` |
| em3 (`52`) | GradientCurve ‡ | `0e 01` | UIN/10 | none (2.5–40.0) | `ff` |
| em3 | RoomNormalTemp, RoomSetbackTemp, RoomFrostProtectionTemp, SummerWinterChangeOverTemp (`ff`), SupplyMaxTemp, SupplyMinTemp (`31`) | as on `em2` | as on `em2` | as on `em2` | `ff` / `31` |
| fs2 (`75`) | RoomNormalTemp, RoomSetbackTemp, RoomFrostProtectionTemp, GradientCurve, SummerWinterChangeOverTemp, SupplyMaxTemp, SupplyMinTemp, SwitchOnRuntime, FrostProtectionLimitTemp, BoilerMCBoostTemp | as on `fs1` / `em2` | as on `fs1` / `em2` | as on `fs1` / `em2` | `ff` |
| fs2 | DHWSetpoint | `13 00` | UIN/10, °C | 40–60, step 0.5 | `ff` |
| fs3 (`f5`) | the eleven settings of `fs2` | as on `fs2` | as on `fs2` | as on `fs2` | `ff` |
| em1 (`50`) | RoomNormalTemp, RoomSetbackTemp, RoomFrostProtectionTemp, GradientCurve, SummerWinterChangeOverTemp | as on `em2` | as on `em2` | as on `em2` | `ff` |

"Source" is the source address of the captured write. `BlockingTime` was a read of lot A
(`4c 25 00`); it is the same register, now read and written.

## How it was established

Four things for each register. Columns of the table below:

1. **Write seen**: the `50 23` telegram captured passively (ebusd `grab result all`, snapshots
   of 2026-11-16), master data `<crc> <addr> <sub> <value>`, with the number of writes counted
   by the capture. All were acknowledged (`00`); the checksum of each was recomputed offline.
2. **Read seen**: a `50 22` read of the same register by ebusd (`31`), captured the same way,
   and the two data bytes of the answer. They equal the value last written, for all 20.
   Requests marked × 4 read four registers in one telegram; the checksum of every read request
   was recomputed offline as well.
3. **Decoded**: the captured write, injected into the ebusd of `scripts/check.sh` loaded with
   the lot (no bus device), is decoded as a write of this message with this value.
4. **Write test**: the operator of the installation changed the setting from the stated source,
   read it back, and restored it, on 2026-11-15. These
   tests were not run for this record and their intermediate telegrams were not kept: the
   capture holds the last telegram of each register only, the restored value. For the three
   settings added on 2026-11-18 the operator's log of 2026-11-15 gives the change: RegulationP
   and RegulationI 100 → 101 → 100, BoilerMCBoostTemp of `fs1` 2.0 → 2.5 → 2.0 K, the last
   one also through the client in service (its write switch, guard and read-back). The
   client's own register list still marked these three as awaiting validation; the log,
   written after the test, is the later source.

| message | write seen (count) | read seen → answer | decoded |
|---|---|---|---|
| BlockingTime | `28 25 00 01 00` (2) | `4c 25 00` → `01 00` | 1 |
| ChangeOverTime | `d4 ec fd 32 00` (2) | `3d ec fd` → `32 00` | 50 |
| DeCoupleMinTemp | `70 e7 fd 50 00` (2) | `43 e7 fd …` × 4 → `50 00` | 8.0 |
| CalorifierSwitchDiff | `0c e2 fd 14 00` (2) | `f1 e2 fd` → `14 00` | 2.0 |
| DHWSwitchDiff | `bf 40 01 ce ff` (2) | `0c 40 01 …` × 4 → `ce ff` | -5.0 |
| DHWLoadTime | `90 80 01 00 00` (2) | `f1 80 01` → `00 00` | 0 |
| LegionellaSetpoint | `72 87 05 58 02` (2) | `3d 87 05` → `58 02` | 60.0 |
| LegionellaCirculationTime | `46 b1 09 58 02` (2) | `29 b1 09` → `58 02` | 600 |
| RegulationP | `98 9f 02 64 00` (2) | `8d 9f 02 …` × 4 → `64 00` | 100 |
| RegulationI | `90 9e 02 64 00` (2) | `8e 9e 02` → `64 00` | 100 |
| RoomNormalTemp | `d8 05 00 d7 00` (5) | `b1 05 00 …` × 4 → `d7 00` | 21.5 |
| RoomSetbackTemp | `b0 08 00 d7 00` (3) | `58 08 00` → `d7 00` | 21.5 |
| RoomFrostProtectionTemp | `7c 14 0a 64 00` (3) | `96 14 0a` → `64 00` | 10.0 |
| GradientCurve | `a4 0e 01 64 00` (3) | `cd 0e 01` → `64 00` | 10.0 |
| SummerWinterChangeOverTemp | `dc 16 01 c8 00` (3) | `6a 16 01 …` × 4 → `c8 00` | 20.0 |
| SupplyMaxTemp | `66 28 00 ee 02` (4) | `64 28 00` → `ee 02` | 75.0 |
| SupplyMinTemp | `70 2b 01 50 00` (2) | `81 2b 01` → `50 00` | 8.0 |
| SwitchOnRuntime | `d8 10 01 03 00` (10) | `b1 10 01` → `03 00` | 3 |
| FrostProtectionLimitTemp | `a4 be 02 00 00` (2) | `b2 be 02` → `00 00` | 0.0 |
| BoilerMCBoostTemp | `a8 11 01 14 00` (4) | `ed 11 01` → `14 00` | 2.0 |

Further points:

- `SupplyMaxTemp` and `SupplyMinTemp` of the heating module are also written by its room unit
  with `09 03` (`70 51 0903 28 00 ee 02` and `2b 01 50 00`, about a hundred times each in the
  capture of 2026-10-29), with the same register numbers and the same values. That the module
  takes these two from a master other than `ff` fits with that.
- `SwitchOnRuntime`: the operator's test of 2026-11-15 found that 10 was kept and 20 was not,
  hence the range 0–10.
- `FrostProtectionLimitTemp`: the operator's test went 0.0, -0.5, 0.0, hence the signed type.
- `ChangeOverTime` is a number of hours with factor 1 on a 16-bit register (`32 00` = 50),
  which closes the entry of 2026-11-16 in `docs/discoveries.md` for this register.
- `RegulationP`, `RegulationI`: ranges 10 to 300 and 10 to 200, factory value 100, from the
  French installation manual of the WCM-KA 3.0 (document 83258404, pages 89 and 90, sections
  6.7.21 and 6.7.22, parameters 539 and 540), read on 2026-11-18. The manual gives no step;
  the operator's test changed each by 1.
- `BoilerMCBoostTemp` of `fs1`: range 0.0 to 20.0 K, factory value 2.0 K, from the French
  installation manual of the WCM-FS 2.0 (document 83277504, page 60, section 6.5.16), read on
  2026-11-18. Step 0.5 as the other temperature differences of the lot and the operator's
  test. Same register and comment as the read of lot G on the heating modules.
- The ranges of the 17 first settings are those of the table the operator of the installation keeps for these
  settings, which cites the installation manuals of the vendor: WCM-KA 3.0 (document
  83258401, pages 50 to 63, sections 6.7.32 to 6.7.40) for the system manager and WCM-FS 2.0
  (document 83277701, page 21, sections 4.7 and 6.5.28) for the room unit and heating circuit.
- Toolchain: the lot compiles only with the `@wcrc` decorator. Checked on 2026-11-17 with the
  local build of the ebus-typespec fork (branch `wcrc-decorator`, version 0.31.0, compiler
  1.17.0) installed in the working tree only, not committed. `scripts/check.sh` clean, 167
  messages.

## Changes in the telegram log

The telegram log of the ebusd of the installation (an SQLite file kept 10 days by the add-on)
was exported read-only on 2026-11-18 by the operator's deployment session: every `50 23`
write from 2026-11-08 to 2026-11-18 (84, all acknowledged `00`), and every `50 22` read sent to
the same device within 10 minutes after each write (575). The export is installation data
and is not in this repository; only the telegrams and dates below are quoted.

The log stores the writes ebusd sent with `-s ff` without their source byte (marked invalid,
the raw telegram starting at the target). Those rows are the writes of the operator's tests
and of the client in service, which send every setting from `ff` except the flow limits of the
modules; the 16 rows from `31` are stored whole. The checksum of all 84 was recomputed: 84 of
84 match.

Each row: the change (a write of another value), the next read of the register by ebusd and
its answer, then the restore and its read. Dates 2026-11-15 (the operator's tests) and
2026-11-18 (the proof procedure of the client 0.1.1, sent raw by the client).

| setting | date | source | change | read → answer | restore | read → answer |
|---|---|---|---|---|---|---|
| ka BlockingTime | 2026-11-15 | `ff` | `cc 25 00 02 00` | `4c 25 00` → `02 00` | `28 25 00 01 00` | `4c 25 00` → `01 00` |
| ka ChangeOverTime | 2026-11-15 | `ff` | `88 ec fd 33 00` | `3d ec fd` → `33 00` | `d4 ec fd 32 00` | `3d ec fd` → `32 00` |
| ka DeCoupleMinTemp | 2026-11-15 | `ff` | `00 e7 fd 55 00` | `81 e7 fd` → `55 00` | `70 e7 fd 50 00` | `81 e7 fd` → `50 00` |
| ka CalorifierSwitchDiff | 2026-11-15 | `ff` | `24 e2 fd 19 00` | `f1 e2 fd` → `19 00` | `0c e2 fd 14 00` | `f1 e2 fd` → `14 00` |
| ka DHWSwitchDiff | 2026-11-15 | `ff` | `77 40 01 c9 ff` | `79 40 01` → `c9 ff` | `bf 40 01 ce ff` | `79 40 01` → `ce ff` |
| ka DHWLoadTime | 2026-11-15 | `ff` | `70 80 01 0a 00` | `f1 80 01` → `0a 00` | `90 80 01 00 00` | `f1 80 01` → `00 00` |
| ka LegionellaSetpoint | 2026-11-15 | `ff` | `02 87 05 5d 02` | `3d 87 05` → `5d 02` | `72 87 05 58 02` | `3d 87 05` → `58 02` |
| ka LegionellaCirculationTime | 2026-11-15 | `ff` | `ba b1 09 94 02` | `29 b1 09` → `94 02` | `46 b1 09 58 02` | `29 b1 09` → `58 02` |
| ka RegulationP | 2026-11-15 | `ff` | `c4 9f 02 65 00` | `d2 9f 02` → `65 00` | `98 9f 02 64 00` | `d2 9f 02` → `64 00` |
| ka RegulationI | 2026-11-15 | `ff` | `cc 9e 02 65 00` | `8e 9e 02` → `65 00` | `90 9e 02 64 00` | `8e 9e 02` → `64 00` |
| fs1 SwitchOnRuntime | 2026-11-15 | `ff` | `10 10 01 04 00` | `b1 10 01` → `04 00` | `d8 10 01 03 00` | `b1 10 01` → `03 00` |
| fs1 FrostProtectionLimitTemp | 2026-11-15 | `ff` | `e3 be 02 fb ff` | `b2 be 02` → `fb ff` | `a4 be 02 00 00` | `b2 be 02` → `00 00` |
| fs1 BoilerMCBoostTemp | 2026-11-15 | `ff` | `80 11 01 19 00` | `ed 11 01` → `19 00` | `a8 11 01 14 00` | `ed 11 01` → `14 00` |
| fs1 RoomFrostProtectionTemp | 2026-11-18 | `ff` | `ac 14 0a 55 00` | `96 14 0a` → `55 00` | `dc 14 0a 50 00` | `96 14 0a` → `50 00` |
| em2 RoomNormalTemp | 2026-11-15 | `ff` | `64 05 00 dc 00` | `70 05 00` → `dc 00` | `d8 05 00 d7 00` | `70 05 00` → `d7 00` |
| em2 RoomSetbackTemp | 2026-11-15 | `ff` | `c0 08 00 d2 00` | `58 08 00` → `d2 00` | `b0 08 00 d7 00` | `58 08 00` → `d7 00` |
| em2 RoomFrostProtectionTemp | 2026-11-15 | `ff` | `54 14 0a 69 00` | `96 14 0a` → `69 00` | `7c 14 0a 64 00` | `96 14 0a` → `64 00` |
| em2 GradientCurve | 2026-11-15 | `ff` | `8c 0e 01 69 00` | `cd 0e 01` → `69 00` | `a4 0e 01 64 00` | `cd 0e 01` → `64 00` |
| em2 SummerWinterChangeOverTemp | 2026-11-15 | `ff` | `ac 16 01 cd 00` | `25 16 01` → `cd 00` | `dc 16 01 c8 00` | `25 16 01` → `c8 00` |
| em2 SupplyMaxTemp | 2026-11-15 | `31` | `fe 28 00 f3 02` | `64 28 00` → `f3 02` | `66 28 00 ee 02` | `64 28 00` → `ee 02` |
| em2 SupplyMinTemp | 2026-11-15 | `31` | `00 2b 01 55 00` | `81 2b 01` → `55 00` | `70 2b 01 50 00` | `81 2b 01` → `50 00` |
| em3 GradientCurve | 2026-11-18 | `ff` | `8c 0e 01 69 00` | `cd 0e 01` → `69 00` | `a4 0e 01 64 00` | `cd 0e 01` → `64 00` |

Further points from the log:

- **Every one of the 22 settings** was seen changed, read back with the new value, restored and
  read back with the former one. For the 17 first settings and the three of 2026-11-18 this is
  the change their record lacked (until then a note of the operator's test); `proof` is
  `change-observed` in the metadata for all 22.
- **The `ff` rule, now with telegrams.** On module `51`, 2026-11-15 12:56, the same change was
  sent first from `31`, then from `ff`: from `31` the room setpoints (`64 05 00 dc 00`,
  `c0 08 00 d2 00`), the frost protection setpoint (`54 14 0a 69 00`), the curve
  (`8c 0e 01 69 00`) and the summer / winter threshold (`ac 16 01 cd 00`) were acknowledged and
  the read gave the old value (`d7 00`, `d7 00`, `64 00`, `64 00`, `c8 00`); from `ff` the
  value was taken. The flow limits (`28 00`, `2b 01`) were taken from `31`.
- **`SwitchOnRuntime` range.** 2026-11-15 12:20 to 12:21, from `ff`: 120, 60, 30 and 20
  (`90 10 01 78 00`, `c4 10 01 3c 00`, `40 10 01 1e 00`, `a0 10 01 14 00`) acknowledged and
  not taken (read `03 00`); 10 (`dc 10 01 0a 00`) and 5 taken. Hence the maximum 10.
- **De-couple maximum (`e6 fd`)**: 2026-11-15 13:41, 78.5 (`5f e6 fd 11 03`) sent from `ff` and
  from `31`, both acknowledged, read `0c 03` (78.0) after both: not taken from either source.
  78.5 may lie above the device's own bound; the register stays out.
- **Writes of the stored value only** (no change, nothing proven): `ka` legionella day
  (`e8 01 01 01 00`), circulation with legionella (`b4 f3 13 00 00`), boiler sequence
  (`8c ca fd 00 00`, `d8 cb fd 01 00`); `fs1` control variation (`50 41 01 01 00`).
- **A weekly program slot**, `fs1` heating program 1, Tuesday slot 1 (`20 14`, read by lot H as
  `HCProgram1Tue1`), written from `31`: 2026-11-10 `5a 20 14 5a 1a`, read `5a 1a`; 2026-11-17
  `52 20 14 48 1a`, read `48 1a`; both acknowledged. One slot of one device: no write side is
  defined for the programs (lot H), see "Coverage".

## Captures on site

Changes made on purpose for this record, by the operator's deployment session, with the client
in service (0.1.1, raw `50 23` from `ff`), one step and back, then an export of the telegram log
of ebusd for the period (read-only). Each row as in the previous section. The export is
installation data, not in this repository.

### Batch 1 — room unit 2 (`75`), 2026-11-18 14:40 to 14:49

| setting | date, time | source | change | read → answer | restore | read → answer |
|---|---|---|---|---|---|---|
| fs2 RoomNormalTemp | 2026-11-18 14:40–14:40 | `ff` | `88 05 00 cd 00` | `70 05 00` → `cd 00` | `a8 05 00 d2 00` | `70 05 00` → `d2 00` |
| fs2 RoomSetbackTemp | 2026-11-18 14:40–14:40 | `ff` | `78 08 00 87 00` | `58 08 00` → `87 00` | `c4 08 00 8c 00` | `58 08 00` → `8c 00` |
| fs2 RoomFrostProtectionTemp | 2026-11-18 14:41–14:41 | `ff` | `d0 14 0a 4b 00` | `96 14 0a` → `4b 00` | `dc 14 0a 50 00` | `96 14 0a` → `50 00` |
| fs2 GradientCurve | 2026-11-18 14:41–14:41 | `ff` | `a0 0e 01 c3 00` | `cd 0e 01` → `c3 00` | `1c 0e 01 c8 00` | `cd 0e 01` → `c8 00` |
| fs2 SummerWinterChangeOverTemp | 2026-11-18 14:42–14:42 | `ff` | `10 16 01 91 00` | `25 16 01` → `91 00` | `d8 16 01 96 00` | `25 16 01` → `96 00` |
| fs2 SupplyMaxTemp | 2026-11-18 14:42–14:43 | `ff` | `ae 28 00 e9 02` | `64 28 00` → `e9 02` | `66 28 00 ee 02` | `64 28 00` → `ee 02` |
| fs2 SupplyMinTemp | 2026-11-18 14:43–14:43 | `ff` | `00 2b 01 55 00` | `81 2b 01` → `55 00` | `70 2b 01 50 00` | `81 2b 01` → `50 00` |
| fs2 SwitchOnRuntime | 2026-11-18 14:43–14:44 | `ff` | `84 10 01 02 00` | `b1 10 01` → `02 00` | `d8 10 01 03 00` | `b1 10 01` → `03 00` |
| fs2 FrostProtectionLimitTemp | 2026-11-18 14:48–14:48 | `ff` | `e3 be 02 fb ff` | `b2 be 02` → `fb ff` | `a4 be 02 00 00` | `b2 be 02` → `00 00` |
| fs2 DHWSetpoint | 2026-11-18 14:48–14:48 | `ff` | `bd 13 00 ef 01` | `54 13 00` → `ef 01` | `b1 13 00 f4 01` | `54 13 00` → `f4 01` |
| fs2 BoilerMCBoostTemp | 2026-11-18 14:48–14:49 | `ff` | `a4 11 01 0f 00` | `ed 11 01` → `0f 00` | `a8 11 01 14 00` | `ed 11 01` → `14 00` |

- 22 writes, all acknowledged `00`, checksum right for all 22; every read after a write gave
  the written value; every setting ended at its value before the batch.
- The hot-water setpoint of the room unit, bounded 40 to 60: 40 °C up to the hot-water maximum
  of the room unit (WCM-FS 2.0, document 83277504, page 86, section 6.5.34, parameter 601,
  factory value 60.0 °C, settable 40 to 80). A room unit set to a higher maximum accepts more;
  the definition keeps the factory bound.
- Home Assistant was restarted by someone else at about 14:44, between the restore of the
  switch-on lead time (14:44:05, read 14:44:06) and the change of the frost limit (14:48:00).
  No change / restore pair spans it; ebusd and the bus were not restarted (its reads of the room
  unit continue at 14:45:07, with the values before the next change). One write was refused by
  the client during the restart and not sent.
- The client's guard refused one restore sent less than 10 s after the change (nothing sent);
  it was sent 16 s later. The client's display of the curve lagged one poll behind the bus;
  the bus values above are what counts.

### Batch 2 — room unit 3 (`f5`), 2026-11-18 14:53 to 14:58

| setting | date, time | source | change | read → answer | restore | read → answer |
|---|---|---|---|---|---|---|
| fs3 RoomNormalTemp | 2026-11-18 14:53–14:53 | `ff` | `88 05 00 cd 00` | `70 05 00` → `cd 00` | `a8 05 00 d2 00` | `70 05 00` → `d2 00` |
| fs3 RoomSetbackTemp | 2026-11-18 14:53–14:53 | `ff` | `78 08 00 87 00` | `58 08 00` → `87 00` | `c4 08 00 8c 00` | `58 08 00` → `8c 00` |
| fs3 RoomFrostProtectionTemp | 2026-11-18 14:54–14:54 | `ff` | `d0 14 0a 4b 00` | `96 14 0a` → `4b 00` | `dc 14 0a 50 00` | `96 14 0a` → `50 00` |
| fs3 GradientCurve | 2026-11-18 14:54–14:54 | `ff` | `6c 0e 01 cd 00` | `cd 0e 01` → `cd 00` | `4c 0e 01 d2 00` | `cd 0e 01` → `d2 00` |
| fs3 SummerWinterChangeOverTemp | 2026-11-18 14:55–14:55 | `ff` | `10 16 01 91 00` | `25 16 01` → `91 00` | `d8 16 01 96 00` | `25 16 01` → `96 00` |
| fs3 SupplyMaxTemp | 2026-11-18 14:55–14:55 | `ff` | `ae 28 00 e9 02` | `64 28 00` → `e9 02` | `66 28 00 ee 02` | `64 28 00` → `ee 02` |
| fs3 SupplyMinTemp | 2026-11-18 14:55–14:56 | `ff` | `00 2b 01 55 00` | `81 2b 01` → `55 00` | `70 2b 01 50 00` | `81 2b 01` → `50 00` |
| fs3 SwitchOnRuntime | 2026-11-18 14:56–14:56 | `ff` | `84 10 01 02 00` | `b1 10 01` → `02 00` | `d8 10 01 03 00` | `b1 10 01` → `03 00` |
| fs3 FrostProtectionLimitTemp | 2026-11-18 14:56–14:57 | `ff` | `e3 be 02 fb ff` | `b2 be 02` → `fb ff` | `a4 be 02 00 00` | `b2 be 02` → `00 00` |
| fs3 DHWSetpoint | 2026-11-18 14:57–14:57 | `ff` | `bd 13 00 ef 01` | `54 13 00` → `ef 01` | `b1 13 00 f4 01` | `54 13 00` → `f4 01` |
| fs3 BoilerMCBoostTemp | 2026-11-18 14:57–14:58 | `ff` | `a4 11 01 0f 00` | `ed 11 01` → `0f 00` | `a8 11 01 14 00` | `ed 11 01` → `14 00` |

- 22 writes, all acknowledged `00`, checksum right for all 22 (one telegram carries the byte
  `aa` escaped as `a9 01` in the raw log, read unescaped); every read after a write gave the
  written value, each read lying between its change and the restore; every setting ended at
  its value before the batch. No other write to the room unit in the export.
- Room unit 3 had the same values as room unit 2 for ten settings; its heating curve was 21.0
  (20.5 and back).

### Batch 3 — direct circuit `em1` (`50`), 2026-11-18 14:59 to 15:36

The column "at `15`" is the read of the same register at the system manager between the change
and the restore.

| setting | date, time | source | change | read at `50` → answer | at `15` | restore | read at `50` → answer |
|---|---|---|---|---|---|---|---|
| em1 RoomNormalTemp | 2026-11-18 14:59–14:59 | `ff` | `a8 05 00 d2 00` | `70 05 00` → `d2 00` | `d2 00` | `d8 05 00 d7 00` | `70 05 00` → `d7 00` |
| em1 RoomSetbackTemp | 2026-11-18 15:27–15:28 | `ff` | `bc 08 00 9b 00` | `58 08 00` → `9b 00` | `9b 00` | `8c 08 00 a0 00` | `58 08 00` → `a0 00` |
| em1 RoomFrostProtectionTemp | 2026-11-18 15:28–15:28 | `ff` | `4c 14 0a 5f 00` | `96 14 0a` → `5f 00` | `5f 00` | `7c 14 0a 64 00` | `96 14 0a` → `64 00` |
| em1 GradientCurve | 2026-11-18 15:28–15:29 | `ff` | `94 0e 01 5f 00` | `cd 0e 01` → `5f 00` | `5f 00` | `a4 0e 01 64 00` | `cd 0e 01` → `64 00` |
| em1 SummerWinterChangeOverTemp | 2026-11-18 15:29–15:29 | `ff` | `60 16 01 c3 00` | `25 16 01` → `c3 00` | `c3 00` | `dc 16 01 c8 00` | `25 16 01` → `c8 00` |

- 10 writes from `ff`, all acknowledged `00`, checksum right; each read at `50` after a write gave
  the written value, and `15` answered the same value after each change and the former one
  after each restore: `50` and `15` share these registers.
- **Flow limits, not taken from `31`.** Maximum: 15:29:43, `31 50 5023` `b3 28 00 2f 03`
  (81.5), acknowledged `00`, read at once `64 28 00` → `34 03` (82.0), at `15` 82.0 as well.
  Minimum: 15:35:14, `00 2b 01 55 00` (8.5) from `31`, acknowledged, read `50 00` (8.0) at `50`
  and `15`. Nothing changed, nothing to restore. On `50` / `15` these registers are not taken
  from ebusd's own address, unlike modules `51` and `52`; the operator's log of 2026-10-30 has
  the flow maximum of `15` taken only from `ff`. Not in the lot. The client in service writes
  them from `31` on `em1`, so its writes of these two have had no effect.
- Home Assistant was restarted three times that afternoon, outside the session (about 14:44,
  15:21, 15:31): the first before the batch, the second during a pause between the first
  setting (14:59) and the second (15:27), the third between the two flow-limit attempts. No
  change / restore pair spans one; ebusd was not restarted. The client in service was 0.1.1
  for the first setting and 0.1.2 from 15:15 on; its telegrams are the same.

### Batch 4 — heating module `em3` (`52`), 2026-11-18 15:36 to 15:39

| setting | date, time | source | change | read → answer | restore | read → answer |
|---|---|---|---|---|---|---|
| em3 RoomNormalTemp | 2026-11-18 15:36–15:36 | `ff` | `64 05 00 dc 00` | `70 05 00` → `dc 00` | `d8 05 00 d7 00` | `70 05 00` → `d7 00` |
| em3 RoomSetbackTemp | 2026-11-18 15:36–15:36 | `ff` | `c0 08 00 d2 00` | `58 08 00` → `d2 00` | `b0 08 00 d7 00` | `58 08 00` → `d7 00` |
| em3 RoomFrostProtectionTemp | 2026-11-18 15:37–15:37 | `ff` | `4c 14 0a 5f 00` | `96 14 0a` → `5f 00` | `7c 14 0a 64 00` | `96 14 0a` → `64 00` |
| em3 SummerWinterChangeOverTemp | 2026-11-18 15:37–15:37 | `ff` | `60 16 01 c3 00` | `25 16 01` → `c3 00` | `dc 16 01 c8 00` | `25 16 01` → `c8 00` |
| em3 SupplyMaxTemp | 2026-11-18 15:38–15:38 | `31` | `ae 28 00 e9 02` | `64 28 00` → `e9 02` | `66 28 00 ee 02` | `64 28 00` → `ee 02` |
| em3 SupplyMinTemp | 2026-11-18 15:38–15:38 | `31` | `00 2b 01 55 00` | `81 2b 01` → `55 00` | `70 2b 01 50 00` | `81 2b 01` → `50 00` |

- 12 writes, all acknowledged `00`, checksum right; each read after a write, before the
  restore, gave the written value; every setting ended at its value before the batch.
- **Accepted source of the flow limits, per device.** On module `52`, as on module `51`
  (2026-11-15), the flow maximum and minimum are taken from ebusd's own address `31`. On the
  direct circuit `50` (shared with the system manager `15`) the same writes from `31` were
  acknowledged and not taken (batch 3). The settings of the lot carry no source; the comment of
  each file says which source the device takes: `51.w.em2` and `52.w.em3` the flow limits from
  `31` too, `50.w.em1` only `ff`.

### Batch 5 — room unit 1 (`35`), 2026-11-18 15:39 to 15:43

| setting | date, time | source | change | read → answer | restore | read → answer |
|---|---|---|---|---|---|---|
| fs1 RoomNormalTemp | 2026-11-18 15:39–15:40 | `ff` | `88 05 00 cd 00` | `70 05 00` → `cd 00` | `a8 05 00 d2 00` | `70 05 00` → `d2 00` |
| fs1 RoomSetbackTemp | 2026-11-18 15:40–15:40 | `ff` | `78 08 00 87 00` | `58 08 00` → `87 00` | `c4 08 00 8c 00` | `58 08 00` → `8c 00` |
| fs1 GradientCurve | 2026-11-18 15:40–15:41 | `ff` | `b4 0e 01 b9 00` | `cd 0e 01` → `b9 00` | `7c 0e 01 be 00` | `cd 0e 01` → `be 00` |
| fs1 SummerWinterChangeOverTemp | 2026-11-18 15:41–15:41 | `ff` | `10 16 01 91 00` | `25 16 01` → `91 00` | `d8 16 01 96 00` | `25 16 01` → `96 00` |
| fs1 SupplyMaxTemp | 2026-11-18 15:41–15:42 | `ff` | `ae 28 00 e9 02` | `64 28 00` → `e9 02` | `66 28 00 ee 02` | `64 28 00` → `ee 02` |
| fs1 SupplyMinTemp | 2026-11-18 15:42–15:42 | `ff` | `00 2b 01 55 00` | `81 2b 01` → `55 00` | `70 2b 01 50 00` | `81 2b 01` → `50 00` |
| fs1 DHWSetpoint | 2026-11-18 15:42–15:43 | `ff` | `bd 13 00 ef 01` | `54 13 00` → `ef 01` | `b1 13 00 f4 01` | `54 13 00` → `f4 01` |

- 14 writes, all acknowledged `00`, checksum right; each read after a write, before the
  restore, gave the written value; every setting ended at its value before the batch. The
  three room units now have the same eleven settings written.

## Equipment

Kromschröder WCM regulators on eBUS, scanning as `MF=Kromschröder`, `ID=W`: system manager at
`15` (SW=6618), room unit at `35` (SW=2726), heating modules at `51` and `52` (SW=7203). Two condensing
boilers in cascade, no calorifier or buffer sensor fitted.

## Date

Captures 2026-10-29 and 2026-11-16; record written on 2026-11-17; three settings added and
the coverage section written on 2026-11-18; telegram log 2026-11-10 to 2026-11-18 read and
two more settings added on 2026-11-18.

## Not verified

- The source byte of the writes from `ff` in the telegram log: the log does not store it
  (section "Changes in the telegram log"). That they came from `ff` rests on the sender: the
  operator's commands and the client's code send these settings from `ff`, and on module `51`
  the same values sent from `31` were not taken.
- The ranges were not compared with the manuals for this record; the pages are those cited by
  the operator's table. `RoomSetbackTemp` and `GradientCurve` have no range in the definition
  (fractional bound).
- Names and units of `CalorifierSwitchDiff` and `DeCoupleMinTemp` (no calorifier or buffer
  here, nothing reacts to them), the sign of `CalorifierSwitchDiff` (only 2.0 was seen), and
  the unit of `LegionellaCirculationTime` (600 fits seconds in the range 180–1200; no screen
  or manual page was compared).
- The same settings on the other heating modules (`50`, `52`) and the other room units: same
  device types, no write captured, not in the lot.
- The definitions through ebusd on a bus: see the test in
  [register-write-crc.md](register-write-crc.md).

## Left out — not yet proven

| register | what exists | what is missing |
|---|---|---|
| ka `RoomNormalTemp` `05 00`, `RoomSetbackTemp` `08 00`, `SupplyMaxTemp` `28 00`, `DHWSetpoint` `13 00` (read in lot A) | read at `15`; the operator's table lists hot-water setpoint and maximum flow as tested on 2026-10-30 | a captured `50 23` to `15`. Test from `ff`, then restore: `99 13 00 f9 01` (50.5) / `b1 13 00 f4 01` (50.0); `64 05 00 dc 00` (22.0) / `d8 05 00 d7 00` (21.5); `fc 08 00 a5 00` (16.5) / `8c 08 00 a0 00` (16.0); `b3 28 00 2f 03` (81.5) / `bf 28 00 34 03` (82.0) |
| ka `DHWLoadingPriority` `23 00` (`DHWOperationMode` until 0.4.3), `DHWExceeded` `2d 00` (read in lot A) | read only | any write test; for the priority, a change alters how the heating circuits are supplied while the hot water is loaded: operator's decision |
| ka `ModulationStatus` `2c 00` (read in lot A) | read; the vendor register list calls it a setpoint | nothing says it is a setting. No write to try without the vendor's documentation |
| ka de-couple maximum `e6 fd` | write from `31` acknowledged, value not taken (see register-write-crc.md) | a write from `ff`: `5f e6 fd 11 03` (78.5), then `c7 e6 fd 0c 03` (78.0) |
| ka legionella day `01 01`, circulation with legionella `f3 13`, boiler sequence `ca fd` / `cb fd` | one write each, of the value already stored | the value lists, and a change read back. Changing the boiler sequence reconfigures the cascade: boilers off, operator's decision |
| fs1 `ControlVariationMode` `41 01` | write captured (`50 41 01 01 00`), of the value already stored (the operator's log of 2026-11-15: a write of the same value) | a change read back. The control variation changes how the circuit is regulated: operator's decision |
| holiday level `3d 01` and holiday dates of the room unit | `docs/discoveries.md`, 2026-11-08: written and read back | no telegram kept |
| time-program slots (writes) | `docs/discoveries.md`, 2026-10-30: accepted from any master | no telegram kept; the read side is in lot A |
| modulation limits `ea fd` / `eb fd`, other hydraulic registers `e3 fd`–`e9 fd` | listed by the operator's table or read only | no telegram |

## Coverage of the settings a client writes in service

Written on 2026-11-18. The client in service on the test installation (a Home Assistant
integration, 0.1 series) writes 71 numeric settings, a few choices, the holiday dates, weekly
program slots and the clock. Each is classified below: writable in the lot (with this record),
or missing, with what is missing and the smallest action on the installation that would give
it. Nothing below was sent to the bus for this record.

### Where captures of past writes were looked for

| Source | What it holds | Writes found |
|---|---|---|
| Snapshots of `grab result all` taken by the read-only bus tools (85 files, 2026-10-29, 2026-11-16 to 2026-11-18) | the last telegram of each distinct request since the last start of ebusd, with its answer and a count | 27 distinct `50 23` telegrams, all of 2026-11-16 and 2026-11-17: the 26 of [register-write-crc.md](register-write-crc.md) section 1 and `cc 25 00 02 00` of the write test. None on 2026-10-29. The snapshot of 2026-11-18 11:46 (after a restart of ebusd) holds none, only the `09 03` writes of the room units to the modules |
| Log of the ebusd add-on (last 400 lines) | update notices since the restart | no write command |
| Log of Home Assistant (last lines) | warnings and errors | no line of the integration: its write line is logged at level info, below the configured level |
| The client's write events (`weishaupt_write`) | value before, raw value, value read back, source | kept in the recorder of Home Assistant, which the read-only tools do not reach |
| Telegram log of the ebusd add-on (SQLite, 10 days kept) | every telegram on the bus | exported read-only on 2026-11-18 by the deployment session (2026-11-08 to 2026-11-18): 84 writes, 29 device / register pairs, with the reads that followed. A change read back and restored for each of the 22 settings of the lot, 2 of them new; section "Changes in the telegram log" |
| The operator's log of the installation (2026-10-30 to 2026-11-15) | notes of each test: register, source, values, read-back | notes, no telegram kept, except one program slot (below) |
| Vendor service tool log ([service-tool-log.md](service-tool-log.md)) | sessions of the tool | no write: the tool was used for reading only |

### Numeric settings (71)

`ka` = system manager (`15`); `fs1`–`fs3` = room units (`35`, `75`, `f5`); `em1` = the direct
circuit of the system manager (`50`); `em2`, `em3` = heating modules (`51`, `52`). "Lot" says
where the read is defined today.

| Device | Registers | Count | State | Evidence of a write today | Missing |
|---|---|---|---|---|---|
| `ka` | `25 00`, `ec fd`, `e7 fd`, `e2 fd`, `40 01`, `80 01`, `87 05`, `b1 09` | 8 | writable (lot C) | this record | — |
| `ka` | `9f 02`, `9e 02` | 2 | **writable (lot C), added 2026-11-18** | this record | — |
| `fs1` | `10 01`, `be 02` | 2 | writable (lot C) | this record | — |
| `fs1` | `11 01` | 1 | **writable (lot C), added 2026-11-18** | this record | — |
| `fs1` | `14 0a` | 1 | **writable (lot C), added 2026-11-18 from the telegram log** | this record | — |
| `em3` | `0e 01` | 1 | **writable (lot C), added 2026-11-18 from the telegram log** | this record | — |
| `em2` | `05 00`, `08 00`, `14 0a`, `0e 01`, `16 01` (`ff`), `28 00`, `2b 01` (`31`) | 7 | writable (lot C) | this record | — |
| `ka` | `28 00` flow maximum, `13 00` hot-water setpoint | 2 | read (lot A) | operator's log 2026-10-30: changed from `ff`, read back, restored; no telegram | a captured change |
| `fs1` | `05 00`, `08 00`, `0e 01`, `16 01`, `28 00`, `2b 01`, `13 00` | 7 | **writable (lot C), added 2026-11-18 from the captures on site** | this record | — |
| `fs2` | `05 00`, `08 00`, `14 0a`, `0e 01`, `16 01`, `28 00`, `2b 01`, `10 01`, `be 02`, `13 00`, `11 01` | 11 | **writable (lot C), added 2026-11-18 from the captures on site** | this record | — |
| `fs3` | the same eleven | 11 | **writable (lot C), added 2026-11-18 from the captures on site** | this record | — |
| `em1` | `05 00`, `08 00`, `14 0a`, `0e 01`, `16 01` | 5 | **writable (lot C), added 2026-11-18 from the captures on site**; shared with `15` | this record | — |
| `em1` | `28 00`, `2b 01` | 2 | read (lot G) | written from `31` on 2026-11-18: acknowledged, not taken | a captured change from `ff` (the client writes them from `31` today) |
| `em3` | `05 00`, `08 00`, `14 0a`, `16 01` (`ff`), `28 00`, `2b 01` (`31`) | 6 | **writable (lot C), added 2026-11-18 from the captures on site** | this record | — |
| `ka` | `ea fd` modulation maximum, `eb fd` minimum | 2 | nothing | operator's log 2026-10-30: changed from `ff`, restored; the client cannot write them today (its old definition is a value list) | a read definition, a captured change, the owner's go; range 30 % to 100 %, minimum below maximum (WCM-KA 3.0, 83258404, pages 84 and 85, parameters 535 and 536) |
| `fs1`–`fs3` | `0f 01` room factor | 3 | nothing | none; the circuits have no room sensor (value not available); the client cannot write it today | a room sensor on the circuit, a captured change, the owner's go |

Total: 62 writable, 4 that one captured change each would prove (the two flow limits of
`em1` from another source than the client uses, the two of `ka`), 5 that need a decision
before any test.

### Other writes of the client

| What | Registers | Evidence today | Missing |
|---|---|---|---|
| `ka` legionella day, circulation with legionella | `01 01`, `f3 13` | writes captured of the stored value (`e8 01 01 01 00`, `b4 f3 13 00 00`), also in the telegram log (2026-11-15) | a change read back, and the value list (order of the days) |
| `ka` boiler sequence | `ca fd`, `cb fd` | writes captured of the stored value | a change read back; changing it reconfigures the cascade (boilers off): operator's decision |
| room units: holiday level | `3d 01` × 3 | `docs/discoveries.md` 2026-11-08: written and read back, 0 = antifreeze, 1 = setback; no telegram | a captured change |
| room units: adaption, control variation, circuit type | `15 01`, `41 01`, `73 09` × 3 | `41 01` of `fs1`: a captured write of the stored value; the others none; the circuit type reconfigures the circuit | the owner's decision, then a captured change |
| room units: holiday dates | `1b 01`–`20 01` × 3 | operator's log 2026-10-30 and 2026-11-07: written from `ff`, read back; the third register of each date does not hold as a year; no telegram | a captured change, and the meaning of the third register |
| weekly program slots | e.g. `10 14`, `20 14` | telegram log: `fs1` slot `20 14` changed twice from `31` and read back (2026-11-10, 2026-11-17); operator's log 2026-11-02/03: `10 14` on the three room units, transcribed | a write side in lot H; one slot of one device proven, the other slots and devices by a captured change each, or the owner's word that one slot stands for the family |
| clock | broadcast `fe 07 00` | the standard broadcast, not a register write | outside this lot |

### Actions on the installation that would prove the rest

For the operator and the session that deploys on the installation, not for this record. In
order of the number of settings each unlocks. "Captured change" means: a snapshot of
`grab result all` (the read-only bus tools take one), the change by one step from the client
in service (0.1.1, raw `50 23` from the stated source), a snapshot, the restore, a snapshot,
with the read-back of the client after each write; service tool disconnected. The capture
keeps every distinct telegram, so the change and the restore are both kept; the answer of the
read is kept only as last seen, hence the snapshot after each step.

| # | Action | Unlocks |
|---|---|---|
| 1 | ~~Export of the telegram log~~ — done on 2026-11-18; a new export after any session of writes is the cheapest proof of what was written | 2 (done) |
| 2 | ~~Captured change of the eleven settings of `fs2` and of `fs3`~~ — done 2026-11-18, batches 1 and 2 | 22 (done) |
| 3 | Captured change of the two flow limits of `em1` from `ff` (82.0 → 81.5 → 82.0, 8.0 → 8.5 → 8.0, reads at `50` and `15`); five of `em1` and six of `em3` done 2026-11-18, batches 3 and 4 | 2 left (11 done) |
| 4 | ~~Captured change of the seven settings of `fs1` not yet proven~~ — done 2026-11-18, batch 5 | 7 (done) |
| 5 | Captured change of `ka` flow maximum and hot-water setpoint | 2 |
| 6 | Captured change of the legionella day and the holiday level (`ka`, three room units) | 4 choices, with their value lists |
| 7 | Owner's decision, then a captured change: modulation limits, room factor, boiler sequence, control variation, adaption, circuit type, holiday dates, program slots | the rest |

A "captured change" can now be had without snapshots: the client in service sends it, and an
export of the telegram log afterwards gives change, read and restore with their dates.

Each change of a room-unit or module setting alters the regulation of its circuit for the
minute it lasts: an unoccupied period suits. Steps 3 and 5 are 8 writes (4 changes, 4
restores): a few minutes within the client's rate limit (one write per register
every 10 s, 30 writes an hour).
