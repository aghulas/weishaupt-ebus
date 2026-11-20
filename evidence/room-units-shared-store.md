# fs1, fs2 — room unit 2 answers its weekly programs from the store of room unit 1

## What

On the test installation, slave addresses `35` (`fs1`) and `75` (`fs2`) answer the weekly
program registers (`50 22`, sub-bytes `14`, `15`, `16`, `17`, `1a`, see
[room-units-programs.md](room-units-programs.md)) from one store: a slot written to `35` is
read back at once, with the same value, at `75`, and a program slot written to `75` with
`50 23` is acknowledged and not kept. The other settings of the two addresses are not one
store: `75` keeps its own heating curve, flow maximum and circuit type, while the setback and
frost-protection room setpoints written to `35` are read at `75` too.

Use in the definitions (0.5.15, local, 2026-11-20): the 21 messages of heating program 1 of
`75.w.fs2` keep no write and their comment says they are written through `35.w.fs1` (lot H);
in the metadata each of them carries `shared_with = "fs1/<same name>"` (lot M). So do
`RoomSetbackTemp` and `RoomFrostProtectionTemp` of `fs2`, which lose their write conditions
there (they are written on `fs1`; the write lines of the CSV stay), after the full log of 6.
Heating programs 2 and 3 and the hot-water and circulation programs carry no marker: see "Not
established".

## How it was established

### 1. A write on `35`, read on both (2026-11-19, 22:31 to 22:42)

By the operator's deployment session, on the owner's approval, raw `hex` from ebusd's address
`31`; the vendor service tool was not on the bus. Slot used: heating program 1, Sunday slot 3
(register `72 14`, request `58 72 14`), unused on both (`80 80`). Answers as `02 <stop> <start>`.

| time | telegram | answer of `35` | answer of `75` |
|---|---|---|---|
| 22:31:53 | read `31 35 50 22 03 58 72 14`, then the same to `75` | `80 80` | `80 80` |
| 22:31:53 | write `31 35 50 23 05 4c 72 14 09 08` (02:00–02:15) | ack `00` | — |
| 22:31:57 (+3 s) | reads as above | `09 08` | `09 08` |
| 22:32:54 (+60 s) | reads | `09 08` | `09 08` |
| 22:36:54 (+5 min) | reads | `09 08` | `09 08` |
| 22:36:55 | restore `31 35 50 23 05 30 72 14 80 80` | ack `00` | — |
| 22:36:58 (+3 s) | reads | `80 80` | `80 80` |
| 22:37:56 (+60 s) | reads | `80 80` | `80 80` |
| 22:41:56 (+5 min) | reads | `80 80` | `80 80` |

The telegram log of ebusd for 22:31:52 to 22:42:06 (516 telegrams, installation data, not in
this repository) has, between the write and the first read of `75`, no telegram to `75` and
none from `30`, `70` or `f1` to `35` or `75`: no copy of the slot travels on the bus. In the
whole period the only telegrams to `35` and `75` are ebusd's reads from `31` and one
identification request from `00` to each, answered with the same bytes by both
(`50 57 02 00 18 00 27 26 ff ff`; room unit 3 answers `08` in place of `18`, see
`docs/discoveries.md`).

### 2. Writes on `75` are not kept (2026-11-18 and 2026-11-19)

Four program-slot writes to `75` (`50 23`, from `31` and from `ff`), each acknowledged `00`,
none read back: [choice-date-program-writes.md](choice-date-program-writes.md) and
[docs/retest-room-unit-2.md](../docs/retest-room-unit-2.md). The same telegrams to `35`, to
room unit 3 (`f5`) and to the system manager's circuit (`50`) were kept.

### 3. No program write between the two addresses in ten days (2026-11-09 to 2026-11-19)

Telegram-log export of every `50 22`, `50 23`, `09 02` and `09 03` telegram from `30` or `70`
or to `35`, `75` or `51`, and of every write to a program register (`0x1410` to `0x1a72`) of
any device (272 319 telegrams): every program write of the period is ours (`35` 24, `f5` 11,
`50` 4, `75` 3). None from `30` or `f1` to `75`, none from `70` or `30` to `35`.

### 4. The 105 slots are equal

All 105 program slots of `75` equal those of `35`, slot for slot, on 2026-11-17
([room-units-programs.md](room-units-programs.md)); in the ten-day log, 105 program registers
read on both addresses within 30 s of each other never differ except during the write of
step 1, where `75` follows `35`.

### 5. Which other registers share the store

From the same log and the batch exports: every pair of reads of one register on `35` and on
`75` less than 30 s apart (163 registers, 105 of them program slots).

**Always different** (each pair):

| register | name | `35` | `75` | pairs |
|---|---|---|---|---|
| `0e 01` | `GradientCurve` | `be 00` (19.0) | `c8 00` (20.0) | 2 505 |
| `73 09` | `HeatingCircuitType` | `02 00` (2) | `03 00` (3) | 941 |
| `02 00` | `HeatDemandTemp` | e.g. `a7 01` | e.g. `c2 01` | 200 |
| `04 00` | `SupplyHCSetTemp` | e.g. `a7 01` | e.g. `ae 01` | 148 of 168 |

The register survey (2026-11-19, [register-survey-findings.md](register-survey-findings.md))
adds `09 00` and the copy of the clock (`25 01`, `26 01`), read minutes apart, so possibly
only time; of the 97 undefined registers it read on both, the rest are equal.

**Always equal** apart from a pair taken across a test write: `RoomNormalTemp`
(`05 00`, 2 502 pairs), `RoomSetbackTemp` (`08 00`), `RoomTemp` (`11 00`, 166 pairs, three
differ by 0.1 °C over 10 s), `RoomSetpointTemp` (`12 00`), `DHWSetpoint` (`13 00`),
`RoomFrostProtectionTemp` (`14 0a`), `SummerWinterChangeOverTemp` (`16 01`), `SupplyMaxTemp`
(`28 00`), `SupplyMinTemp` (`2b 01`), `HolidayTempLevel` (`3d 01`), the holiday dates
(`1b 01` to `20 01`), `ControlVariation` (`41 01`), `FrostProtectionLimitTemp` (`be 02`).

**Written to `35` only, followed by `75`.** Three writes from the operator's client, source
`ff`, to `35` alone (the telegrams of the log, the client's log names the target):

| setting | write to `35` | `75` before | `75` after the write | restore to `35` | `75` after the restore |
|---|---|---|---|---|---|
| `RoomFrostProtectionTemp` (`14 0a`) | 2026-11-18 20:12:39.9 `35 50 23 05 ac 14 0a 55 00` (8.5) | 8.0 (20:01:00) | 8.5 at 20:12:42.1, still 8.5 at 20:59:30 | 21:05:24 `… dc 14 0a 50 00` (8.0) | 8.0 at 21:11:12 |
| `RoomSetbackTemp` (`08 00`) | 2026-11-19 15:54:14.3 `35 50 23 05 78 08 00 87 00` (13.5) | 14.0 (15:51:21) | 13.5 at 15:54:14.8 | 15:58:02 `… c4 08 00 8c 00` (14.0) | 14.0 at 15:58:41 |
| `RoomFrostProtectionTemp` | 2026-11-19 15:58:35 `… ac 14 0a 55 00` (8.5) | 8.0 (15:54:10) | 8.5 at 15:58:37.4 | 15:59:05 `… dc 14 0a 50 00` (8.0) | 8.0 at 16:31:12 |

No telegram to `75` other than ebusd's reads lies between each write and the read that shows
the new value. These two setpoints share the store, as the programs do.

**Test writes, read on the other address while the change held.** The eleven numeric
settings (batch 1, `75`, 2026-11-18 14:40 to 14:49; batch 5, `35`, 15:39 to 15:43,
[settings-writes.md](settings-writes.md)), the holiday level (2026-11-18 21:09 to 21:10),
the holiday dates (2026-11-19 13:55 to 13:56) and the control variation (13:57 to 13:58) were
each changed for 10 to 40 s on one address and restored. Only two of these windows contain a
read of the other address:

- `GradientCurve`: `75` changed 20.0 → 19.5 at 14:41:34; `35` read 14:41:49 = 19.0, its own
  value. Not shared.
- `SupplyMaxTemp`: `35` changed 75.0 → 74.5 at 15:41:45; `75` read 15:41:47 = 75.0. Not
  shared.

For `RoomNormalTemp`, `SummerWinterChangeOverTemp`, `SupplyMinTemp`, `SwitchOnRuntime`,
`FrostProtectionLimitTemp`, `DHWSetpoint`, `BoilerMCBoostTemp`, the holiday level, the
holiday dates and the control variation, no read of the other address falls inside a change:
whether a write on one changes the other is **not known** from the records. Each was written
on both addresses in turn and both read back the written value. A write to `75` of a setting
is kept (batch 1, eleven settings, each read back), unlike a write to `75` of a program slot.

### 6. The full telegram log of the three setpoint writes (exported 2026-11-20)

Every telegram of the telegram log, unfiltered, for the three windows of 5 (27, 21 and 28
telegrams; installation data, not in this repository). The writes are logged without their
source byte (ebusd's own sends from the operator's client, source `ff` in its log); their
bytes, from the target on:

| window | write (target, `50 23`, data) | register ← value | setting | read of `75` that shows it |
|---|---|---|---|---|
| 2026-11-18 20:12:35–20:12:45 | 20:12:39.948 `35 50 23 05 ac 14 0a 55 00`, ack `00` | `0x0a14` ← `0x0055` (8.5) | `RoomFrostProtectionTemp` | 20:12:42.075 `31 75 50 22 03 96 14 0a` → `02 55 00`; `35` read 20:12:37.944 → `50 00`, 20:12:41.940 → `55 00` |
| 2026-11-19 15:54:10–15:54:20 | 15:54:14.346 `35 50 23 05 78 08 00 87 00`, ack `00` | `0x0008` ← `0x0087` (13.5) | `RoomSetbackTemp` | 15:54:14.849 `31 75 50 22 03 58 08 00` → `02 87 00`; `75` read 15:51:21 → `8c 00` (14.0) before; `35` read 15:54:10.347 → `8c 00`, 15:54:16.356 → `87 00` |
| 2026-11-19 15:58:30–15:58:39 | 15:58:35.104 `35 50 23 05 ac 14 0a 55 00`, ack `00` | `0x0a14` ← `0x0055` (8.5) | `RoomFrostProtectionTemp` | 15:58:37.394 `31 75 50 22 03 96 14 0a` → `02 55 00`; `75` read 15:54:10.484 → `50 00` before; `35` read 15:58:33.223 → `50 00`, 15:58:37.060 → `55 00` |

Checked in each window, between the write and the read of `75`:

- **No telegram to `75`** but ebusd's reads from `31`; in the three windows no master other
  than `31` sends to `75`.
- **Masters `30` and `70`** (the room units' masters) send only what they send every few
  seconds: `30 → 50` and `70 → 51` `50 14`, `30 → f1` and `70 → f1` `05 07` (heat demand),
  `70 → 51` `09 02` reads of `0c 0a` and `29 0a`, and `70 → 51` `09 03` writes of `20 0a` = 0 and
  `85 02` = 0. These two `09 03` are the ones step 1 found every 20 s for ten days; none carries
  `0x0a14`, `0x0008` or the new value, so none forwards the change, and none is addressed to
  `75`.
- The other telegrams are the cascade manager's broadcasts (`f1 → fe` `50 0a`, and `09 03` of
  register `0x0076` and `0x0078`, every 10 s in every export), the boilers' exchange with their
  automats (`10`, `13`, `03`), module `52` and its master `f0`, and ebusd's reads. In the 15:58
  window two lines of the log are fragments without a source (`20` and `51 50 22 03 81 2b`, a
  read of `51`); neither is to `75`.

Each setpoint has a window of its own: the frost-protection setpoint two, the setback setpoint
one. Restores (2026-11-18 21:05:24, 2026-11-19 15:58:02 and 15:59:05) were followed at `75` too
(section 5), from the filtered export only.

## Established

- The weekly programs of `75` are those of `35`: a write on `35` is answered at `75` within
  3 s, both ways, with nothing on the bus between; a program write to `75` is acknowledged and
  not kept. Shown on heating program 1, Sunday slot 3; the 105 slots of the five programs are
  equal on both addresses, and the four writes `75` did not keep were all in heating
  program 1.
- The setback and frost-protection room setpoints are shared the same way: written to `35`,
  read at `75` 0.5 to 2.5 s later with no telegram to `75` in between (three writes, the full
  log of 6).
- `75` is not a mirror of `35`: the heating curve, the flow maximum and the circuit type
  differ or stay apart, and `75` runs heating circuit 2 itself (it writes its settings into
  module `51` with `09 03` and sends the circuit's heat demand, `70 → f1`, see
  [docs/retest-room-unit-2.md](../docs/retest-room-unit-2.md) step 1).

## Not established

- **Heating programs 2 and 3, hot water, circulation of `75`.** No write of these on `35` was
  followed by a read of `75` (the writes of 2026-11-18 21:12 to 21:13 on `35` had no read of
  `75` in between). Without a write from here: the next change of one of their slots on `35`
  (by the owner), followed by a read of the same slot on `75` within a minute and an export of
  all telegrams of that minute.

- **One physical room unit or two: settled 2026-11-20.** The owner reports the room units
  configured as "#1+2" and "#3". The room unit and module manual (83277504, p. 11 and p. 105)
  describes the address "WTC-Chauf.#1+EM-Chauf.#2": one room unit that runs heating circuits 1
  and 2 in one room. `35` (master `30`) and `75` (master `70`) are that one unit's two bus
  identities, one per circuit; this is why the programs and the setpoints it keeps once are
  answered at both, while what is per circuit (curve, flow maximum, circuit type) is not.
- **Which other settings share the store**: the seven numeric settings, the holiday level
  and dates and the control variation listed in 5. A write on one address and a
  read of the other within the same minute would tell, per setting.
- **Whether this holds elsewhere.** On an installation where `75` is a room unit of its own
  for circuit 2, its programs are presumably its own. The record is of one installation.

## Equipment

Two condensing boilers in cascade behind a Kromschröder system manager (`15`, its own circuit
at `50`), two heating modules (`51`, `52`), and room units answering at `35`, `75` and `f5`,
all with software 2726. `75` drives heating circuit 2 (module `51`), `f5` circuit 3 (module
`52`).

## Date

2026-11-19; full log of the setpoint writes and use in the definitions 2026-11-20.
