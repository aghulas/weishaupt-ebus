# ka, em2, fs1 — settings read and written (50 22 / 50 23)

## What

Lot C, branch `weishaupt-C` of the ebusd-configuration fork (from `weishaupt-A`). 17 settings,
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
| em2 (`51`) | RoomNormalTemp | `05 00` | UIN/10, °C | 16–35, step 0.5 | `ff` |
| em2 | RoomSetbackTemp | `08 00` | UIN/10, °C | none (10.0–21.5) | `ff` |
| em2 | RoomFrostProtectionTemp | `14 0a` | UIN/10, °C | 4–16, step 0.5 | `ff` |
| em2 | GradientCurve | `0e 01` | UIN/10 | none (2.5–40.0) | `ff` |
| em2 | SummerWinterChangeOverTemp | `16 01` | UIN/10, °C | 8–30, step 0.5 | `ff` |
| em2 | SupplyMaxTemp | `28 00` | UIN/10, °C | 8–82, step 0.5 | `31` |
| em2 | SupplyMinTemp | `2b 01` | UIN/10, °C | 8–82, step 0.5 | `31` |
| fs1 (`35`) | SwitchOnRuntime | `10 01` | UIN, min | 0–10 | `ff` |
| fs1 | FrostProtectionLimitTemp | `be 02` | SIN/10, °C | -20–0, step 0.5 | `ff` |

"Source" is the source address of the captured write. `BlockingTime` was a read of lot A
(`4c 25 00`); it is the same register, now read and written.

## How it was established

Four things for each register. Columns of the table below:

1. **Write seen**: the `50 23` telegram captured passively (ebusd `grab result all`, snapshots
   of 2026-11-16), master data `<crc> <addr> <sub> <value>`, with the number of writes counted
   by the capture. All were acknowledged (`00`); the checksum of each was recomputed offline.
2. **Read seen**: a `50 22` read of the same register by ebusd (`31`), captured the same way,
   and the two data bytes of the answer. They equal the value last written, for all 17.
   Requests marked × 4 read four registers in one telegram; the checksum of every read request
   was recomputed offline as well.
3. **Decoded**: the captured write, injected into the ebusd of `scripts/check.sh` loaded with
   the lot (no bus device), is decoded as a write of this message with this value.
4. **Write test**: the operator of the installation changed the setting from the stated source,
   read it back, and restored it, on 2026-11-15. These
   tests were not run for this record and their intermediate telegrams were not kept: the
   capture holds the last telegram of each register only, the restored value.

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
| RoomNormalTemp | `d8 05 00 d7 00` (5) | `b1 05 00 …` × 4 → `d7 00` | 21.5 |
| RoomSetbackTemp | `b0 08 00 d7 00` (3) | `58 08 00` → `d7 00` | 21.5 |
| RoomFrostProtectionTemp | `7c 14 0a 64 00` (3) | `96 14 0a` → `64 00` | 10.0 |
| GradientCurve | `a4 0e 01 64 00` (3) | `cd 0e 01` → `64 00` | 10.0 |
| SummerWinterChangeOverTemp | `dc 16 01 c8 00` (3) | `6a 16 01 …` × 4 → `c8 00` | 20.0 |
| SupplyMaxTemp | `66 28 00 ee 02` (4) | `64 28 00` → `ee 02` | 75.0 |
| SupplyMinTemp | `70 2b 01 50 00` (2) | `81 2b 01` → `50 00` | 8.0 |
| SwitchOnRuntime | `d8 10 01 03 00` (10) | `b1 10 01` → `03 00` | 3 |
| FrostProtectionLimitTemp | `a4 be 02 00 00` (2) | `b2 be 02` → `00 00` | 0.0 |

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
- The ranges are those of the table the operator of the installation keeps for these
  settings, which cites the installation manuals of the vendor: WCM-KA 3.0 (document
  83258401, pages 50 to 63, sections 6.7.32 to 6.7.40) for the system manager and WCM-FS 2.0
  (document 83277701, page 21, sections 4.7 and 6.5.28) for the room unit and heating circuit.
- Toolchain: the lot compiles only with the `@wcrc` decorator. Checked on 2026-11-17 with the
  local build of the ebus-typespec fork (branch `wcrc-decorator`, version 0.31.0, compiler
  1.17.0) installed in the working tree only, not committed. `scripts/check.sh` clean, 167
  messages.

## Equipment

Kromschröder WCM regulators on eBUS, scanning as `MF=Kromschröder`, `ID=W`: system manager at
`15` (SW=6618), room unit at `35` (SW=2726), heating module at `51` (SW=7203). Two condensing
boilers in cascade, no calorifier or buffer sensor fitted.

## Date

Captures 2026-10-29 and 2026-11-16; record written on 2026-11-17.

## Not verified

- The change itself. No telegram shows a value different from the one already stored: the
  proof that a device takes a new value is the operator's test, by its notes. To put a figure
  on it, per register, with the service tool disconnected and nothing else sending as `ff`:
  snapshot, read, write a neighbouring value from the stated source, snapshot, read, write the
  former value, snapshot, read. Example for `BlockingTime`: `28 25 00 01 00` is 1 min,
  `cc 25 00 02 00` is 2 min.
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
| ka `DHWOperationMode` `23 00`, `DHWExceeded` `2d 00` (read in lot A) | read only | any write test; for the mode, a change of mode alters the hot-water priority: operator's decision |
| ka `ModulationStatus` `2c 00` (read in lot A) | read; the vendor register list calls it a setpoint | nothing says it is a setting. No write to try without the vendor's documentation |
| ka de-couple maximum `e6 fd` | write from `31` acknowledged, value not taken (see register-write-crc.md) | a write from `ff`: `5f e6 fd 11 03` (78.5), then `c7 e6 fd 0c 03` (78.0) |
| ka `RegulationP` `9f 02`, `RegulationI` `9e 02` | writes captured (`98 9f 02 64 00`, `90 9e 02 64 00`), equal to the stored value; marked as awaiting validation in the operator's table | a write of another value read back, for example `c4 9f 02 65 00` (101) then `98 9f 02 64 00` (100) |
| ka legionella day `01 01`, circulation with legionella `f3 13`, boiler sequence `ca fd` / `cb fd` | one write each, of the value already stored | the value lists, and a change read back. Changing the boiler sequence reconfigures the cascade: boilers off, operator's decision |
| fs1 `BoilerMCBoostTemp` `11 01`, `ControlVariationMode` `41 01` | writes captured (`a8 11 01 14 00`, `50 41 01 01 00`), awaiting validation in the operator's table | a change read back: `80 11 01 19 00` (2.5 K) then `a8 11 01 14 00` (2.0 K). The control variation changes how the circuit is regulated: operator's decision |
| holiday level `3d 01` and holiday dates of the room unit | `docs/discoveries.md`, 2026-11-08: written and read back | no telegram kept |
| time-program slots (writes) | `docs/discoveries.md`, 2026-10-30: accepted from any master | no telegram kept; the read side is in lot A |
| modulation limits `ea fd` / `eb fd`, other hydraulic registers `e3 fd`–`e9 fd` | listed by the operator's table or read only | no telegram |
