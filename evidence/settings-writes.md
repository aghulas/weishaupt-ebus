# ka, em2, fs1 — settings read and written (50 22 / 50 23)

## What

Lot C, branch `weishaupt-C` of the ebusd-configuration fork (on top of the stack of lots since 2026-11-17, first written on `weishaupt-A`). 20 settings
(17 until 2026-11-18, when the three marked † were added),
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

## Equipment

Kromschröder WCM regulators on eBUS, scanning as `MF=Kromschröder`, `ID=W`: system manager at
`15` (SW=6618), room unit at `35` (SW=2726), heating module at `51` (SW=7203). Two condensing
boilers in cascade, no calorifier or buffer sensor fitted.

## Date

Captures 2026-10-29 and 2026-11-16; record written on 2026-11-17; three settings added and
the coverage section written on 2026-11-18.

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
| Telegram log of the ebusd add-on (SQLite, 10 days kept) | every telegram on the bus | not reachable with the read-only tools. It holds the writes of 2026-11-08 onwards, those of the operator's tests of 2026-11-15 included; the entries of 2026-11-15 leave it around 2026-11-25. The operator's log notes that writes sent with `-s ff` are stored there without their source byte, as invalid |
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
| `em2` | `05 00`, `08 00`, `14 0a`, `0e 01`, `16 01` (`ff`), `28 00`, `2b 01` (`31`) | 7 | writable (lot C) | this record | — |
| `ka` | `28 00` flow maximum, `13 00` hot-water setpoint | 2 | read (lot A) | operator's log 2026-10-30: changed from `ff`, read back, restored; no telegram | a captured change |
| `fs1` | `05 00`, `08 00`, `14 0a`, `0e 01`, `16 01`, `28 00`, `2b 01` (read, lot G), `13 00` (no read) | 8 | read or nothing | operator's log 2026-10-30: all eight changed from `ff` (refused from `31`), read back, restored; no telegram | a captured change |
| `fs2`, `fs3` | `05 00`, `08 00`, `14 0a`, `0e 01`, `16 01`, `28 00`, `2b 01`, `10 01`, `be 02` (read, lot G), `13 00`, `11 01` (no read) | 22 | read or nothing | none: same device type as `fs1`, never tested | a captured change, per device |
| `em1` | `05 00`, `08 00`, `14 0a`, `0e 01`, `16 01` (`ff`), `28 00`, `2b 01` (`31`) | 7 | read (lots A, G) | none. `50` is the same device as `15` (see `docs/discoveries.md`) | a captured change, and which of `50` and `15` it changes |
| `em3` | the same seven | 7 | read (lot G) | none: same device type as `em2` | a captured change |
| `ka` | `ea fd` modulation maximum, `eb fd` minimum | 2 | nothing | operator's log 2026-10-30: changed from `ff`, restored; the client cannot write them today (its old definition is a value list) | a read definition, a captured change, the owner's go; range 30 % to 100 %, minimum below maximum (WCM-KA 3.0, 83258404, pages 84 and 85, parameters 535 and 536) |
| `fs1`–`fs3` | `0f 01` room factor | 3 | nothing | none; the circuits have no room sensor (value not available); the client cannot write it today | a room sensor on the circuit, a captured change, the owner's go |

Total: 20 writable, 46 that one captured change each would prove, 5 that need a decision
before any test.

### Other writes of the client

| What | Registers | Evidence today | Missing |
|---|---|---|---|
| `ka` legionella day, circulation with legionella | `01 01`, `f3 13` | writes captured of the stored value (`e8 01 01 01 00`, `b4 f3 13 00 00`); the operator's log: writes of the same value | a change read back, and the value list (order of the days) |
| `ka` boiler sequence | `ca fd`, `cb fd` | writes captured of the stored value | a change read back; changing it reconfigures the cascade (boilers off): operator's decision |
| room units: holiday level | `3d 01` × 3 | `docs/discoveries.md` 2026-11-08: written and read back, 0 = antifreeze, 1 = setback; no telegram | a captured change |
| room units: adaption, control variation, circuit type | `15 01`, `41 01`, `73 09` × 3 | `41 01` of `fs1`: a captured write of the stored value; the others none; the circuit type reconfigures the circuit | the owner's decision, then a captured change |
| room units: holiday dates | `1b 01`–`20 01` × 3 | operator's log 2026-10-30 and 2026-11-07: written from `ff`, read back; the third register of each date does not hold as a year; no telegram | a captured change, and the meaning of the third register |
| weekly program slots | e.g. `10 14` | operator's log 2026-11-02/03: `31 35 5023 05 8e 10 14 48 1a` and the same to `75`, `f5`, acknowledged, read back `48 1a`, written from `31`; transcribed, not captured | a capture, and a write side of lot H |
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
| 1 | Before 2026-11-25: a read-only query of the telegram log of the ebusd add-on for every `50 23` telegram and the `50 22` reads that follow it, from 2026-11-08 on, exported to a file | the changes of the operator's tests of 2026-11-15 and every change made in service since 2026-11-08, with their telegrams: strengthens the 20, and proves any of the 46 the client changed meanwhile (number unknown until read) |
| 2 | Captured change of the eleven settings of `fs2` and the same of `fs3` | 22 |
| 3 | Captured change of the seven settings of `em1` and of `em3` | 14 (and tells whether `50` and `15` share the register) |
| 4 | Captured change of the eight settings of `fs1` not yet proven | 8 |
| 5 | Captured change of `ka` flow maximum and hot-water setpoint | 2 |
| 6 | The proof procedure of the client 0.1.1 (its notes, section 5), with a snapshot around each line | 2 of the above (`fs1` frost protection, `em3` heating curve); the other four lines repeat proven settings |
| 7 | Captured change of the legionella day and the holiday level (`ka`, three room units) | 4 choices, with their value lists |
| 8 | Owner's decision, then a captured change: modulation limits, room factor, boiler sequence, control variation, adaption, circuit type, holiday dates, a program slot | the rest |

Each change of a room-unit or module setting alters the regulation of its circuit for the
minute it lasts: an unoccupied period suits. Steps 2 to 5 are 92 writes (46 changes, 46
restores): a little over three hours within the client's rate limit (one write per register
every 10 s, 30 writes an hour).
