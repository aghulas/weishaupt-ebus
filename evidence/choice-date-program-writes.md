# Choices, holiday dates, weekly programs and clock — writes of the client in service

## What

Inventory, 2026-11-18, of the writes the client in service (a Home Assistant integration, 0.1
series) sends besides the 71 numeric settings of [settings-writes.md](settings-writes.md):
16 choices (value lists), 6 holiday dates, the weekly program slots and the clock. For each:
register, device, codec, value list or format, source, what the captures prove, what is
missing. Then a plan of captured changes for the rest. Nothing here is defined in a lot yet
(section "Definitions"), and nothing was sent to the bus for this record.

Sources read: the client's register tables (branch `maint-0.1`); the snapshots of
`grab result all` (2026-10-29, 2026-11-16 to 2026-11-18); the exports of the telegram log of
ebusd of 2026-11-18 (every `50 23` write since 2026-11-10, and the seven on-site batches);
the operator's log of the installation (2026-10-30 to 2026-11-15); `docs/discoveries.md`.

All registers are `50 22` / `50 23` registers, 16 bits, low byte first, checksum as in
[register-write-crc.md](register-write-crc.md), unless said otherwise.

## Inventory

### Choices (16)

| Device | Setting | Register | Value list (client) | Value now (read) | Source | Captured writes | Proven |
|---|---|---|---|---|---|---|---|
| `ka` (`15`) | legionella day | `01 01` | 0 off, 1 Monday … 7 Sunday | 1 (`01 00`) | `ff` | `e8 01 01 01 00` (2026-11-15, the stored value) | no change seen |
| `ka` | circulation with legionella | `f3 13` | 0 off, 1 on | 0 | `ff` | `b4 f3 13 00 00` (2026-11-15, stored value) | no change seen |
| `ka` | boiler sequence 1 | `ca fd` | 0 boiler A, 1 boiler B, 240 off | 0 | `ff` | `8c ca fd 00 00` (2026-11-15, stored value) | no change seen |
| `ka` | boiler sequence 2 | `cb fd` | same | 1 | `ff` | `d8 cb fd 01 00` (2026-11-15, stored value) | no change seen |
| `fs1`–`fs3` (`35`, `75`, `f5`) | holiday level | `3d 01` | 0 antifreeze, 1 setback | 0 on all three | `ff` | none in the log; `docs/discoveries.md` 2026-11-08: written and read back, no telegram kept | no telegram |
| `fs1`–`fs3` | adaption | `15 01` | 0 off, 1 on | `00 80` (0x8000) on all three | `ff` | none | the function is not used here (no room sensor): **not testable** |
| `fs1`–`fs3` | control variation | `41 01` | 0 constant flow, 1 weather, 2 weather and room, 3 room | 1 on all three | `ff` | `50 41 01 01 00` to `35` (2026-11-15, stored value) | no change seen |
| `fs1`–`fs3` | circuit type | `73 09` | 0 floor, 1 floor 2, 2 radiator 60, 3 radiator 75, 4 convector, 5 universal | `fs1` 2, `fs2` 3, `fs3` 3 | `ff` | none | no telegram |

Proven (a change written, acknowledged, read back): **0 of 16**. Read already captured for
all 16. No lot defines any of these registers, not even as a read. The value lists come from
the client's tables and the older community templates; for the legionella day only 1 =
Monday is established (read 1 on a Monday schedule, operator's log 2026-11-09).

### Holiday dates (6)

Start and end date of each of the three room units, three registers each: day, month, and a
third register that does not hold as a year (`docs/discoveries.md`, operator's log of
2026-11-07: a start equal to the day of the write has it reset to 0; a past one keeps it).

| Device | Date | Registers | Value now | Captured writes | Proven |
|---|---|---|---|---|---|
| `fs1`–`fs3` | holiday start | `1b 01` day, `1c 01` month, `1d 01` third | 30, 10, 0 (`1e 00`, `0a 00`, `00 00`) | none in the log (the writes of 2026-10-30 and 2026-11-07 predate it) | no telegram |
| `fs1`–`fs3` | holiday end | `1e 01`, `1f 01`, `20 01` | 1, 11, 0 | none | no telegram |

Proven: **0 of 6**. The meaning of the third register is not settled.

### Weekly program slots

Format of a slot (lot H, [room-units-programs.md](room-units-programs.md)): register
`<day><slot> <program>`, day 1 Monday to 7 Sunday in the high nibble, slot 0 to 2 in the low
one, program `14`, `15`, `16` heating 1 to 3, `17` hot water, `1a` circulation; value two
bytes, end then start, quarter hours, bit 7 set = disabled (`80 80` = unused slot). The client
writes them from ebusd's own address `31`.

| Device | Programs | Slots | Captured writes | Proven |
|---|---|---|---|---|
| `fs1` (`35`) | heating 1 | `20 14` (Tuesday slot 1) | `31 35 5023` `5a 20 14 5a 1a` 2026-11-10 17:06, read `5a 1a`; `52 20 14 48 1a` 2026-11-17 22:30, read `48 1a`; both acknowledged | **one slot**: changed twice, read back each time, from `31` |
| `fs1`–`fs3` | heating 1 to 3, hot water, circulation (315 slots, lot H) | the others | none in the log; operator's log 2026-11-02/03: `10 14` on the three, transcribed | no telegram |
| `em1` (`50`) | hot water, circulation (42 slots, lot A) | all | none | no telegram |

Proven: **1 slot of 357**, one program of one device.

### Clock

The clock is not a register write: the standard date / time broadcast `fe 07 00` (BCD
seconds, minutes, hours, day, month, weekday, year after the outside temperature), sent at
second 00, which the clock master `f1` takes over. The client sends it from `31`; an
automation of the installation sends the same every 30 minutes since 2026-11-02. Captured:
`31 fe 0700` `00 0c 00 45 11 18 11 03 26` (snapshot of 2026-11-18, 11:45:00, eight such
telegrams counted) beside `f1`'s own broadcast. The operator's log of 2026-10-30 records the
first one (17:59:00) resetting the whole installation to that time. The general file
`broadcast.csv` of the official configuration decodes the telegram as a passive message
(`u`, `Broadcast/Datetime`); no file defines it as a write.

Proven: not yet with telegrams. What is missing is a captured case where `f1` showed another
time and, after the broadcast, the time sent.

### Numeric settings the client cannot write (5)

| Device | Setting | Register | Value now | What the client sends | Result |
|---|---|---|---|---|---|
| `ka` | modulation maximum | `ea fd` | 80 % (`50 00`) | `write -s ff -c ka ModulationMax <value>` | refused by ebusd (`element not found`: its old definition is a value list), nothing sent |
| `ka` | modulation minimum | `eb fd` | 30 % (`1e 00`) | `write -s ff -c ka ModulationMin <value>` | same |
| `fs1`–`fs3` | room factor (influence P) | `0f 01` | `00 80` (0x8000) on all three | `write -s ff -c fsN RoomFactorCurve <value>` | same; and the function is not used here (no room sensor) |

The operator's log of 2026-10-30 records changes of `ea fd` and `eb fd` from `ff`, restored,
with no telegram kept. Range: 30 % to the maximum, the minimum to 100 % (WCM-KA 3.0, document
83258404, pages 84 and 85, parameters 535 and 536).

### Totals

| Kind | Writes | Proven | Missing |
|---|---|---|---|
| Choices | 16 | 0 | 16 (3 of them not testable: adaption reads 0x8000) |
| Holiday dates | 6 (18 registers) | 0 | 6 |
| Program slots | 357 (17 programs × 21) | 1 slot | 356 |
| Clock | 1 | 0 (sent every 30 min, adoption not captured) | 1 |
| Numeric, not writable by the client | 5 | 0 | 5 (3 not testable: room factor reads 0x8000) |

## Proof plan

For the operator and the deployment session, each batch on the owner's go; nothing here was
sent. As for the numeric campaign: one step and its restore per setting, sent by the client
in service or as the same raw telegram through ebusd (`hex -s <source>`), service tool
disconnected, then an export of the telegram log for the period. Each row gives the change,
the restore and the read that must follow each (`50 22`, master data). Precondition: read
the register first; if it does not answer the "now" value, do not send the row.

Columns: batch, device (address), setting, register, source, values, change telegram,
restore telegram, read, risk.

| Batch | Device | Setting | Register | Source | Values | Change (`50 23`) | Restore | Read (`50 22`) | Risk |
|---|---|---|---|---|---|---|---|---|---|
| A | `ka` (`15`) | legionella day | `01 01` | `ff` | 1 → 2 → 1 | `0c 01 01 02 00` | `e8 01 01 01 00` | `5d 01 01` | low: matters only at the legionella time (Monday 08:30); not on a Tuesday morning |
| A | `ka` (`15`) | circulation with legionella | `f3 13` | `ff` | 0 → 1 → 0 | `e8 f3 13 01 00` | `b4 f3 13 00 00` | `f3 f3 13` | low: matters only during the legionella protection |
| A | `fs1` (`35`) | holiday level | `3d 01` | `ff` | 0 → 1 → 0 | `54 3d 01 01 00` | `08 3d 01 00 00` | `a5 3d 01` | low: matters only during a holiday period (none active) |
| A | `fs2` (`75`) | holiday level | `3d 01` | `ff` | 0 → 1 → 0 | `54 3d 01 01 00` | `08 3d 01 00 00` | `a5 3d 01` | low: matters only during a holiday period (none active) |
| A | `fs3` (`f5`) | holiday level | `3d 01` | `ff` | 0 → 1 → 0 | `54 3d 01 01 00` | `08 3d 01 00 00` | `a5 3d 01` | low: matters only during a holiday period (none active) |
| B | `fs1` (`35`) | control variation | `41 01` | `ff` | 1 → 0 → 1 | `0c 41 01 00 00` | `50 41 01 01 00` | `25 41 01` | **medium**: the circuit runs on a constant flow setpoint for the minute between change and restore |
| B | `fs2` (`75`) | control variation | `41 01` | `ff` | 1 → 0 → 1 | `0c 41 01 00 00` | `50 41 01 01 00` | `25 41 01` | **medium**: the circuit runs on a constant flow setpoint for the minute between change and restore |
| B | `fs3` (`f5`) | control variation | `41 01` | `ff` | 1 → 0 → 1 | `0c 41 01 00 00` | `50 41 01 01 00` | `25 41 01` | **medium**: the circuit runs on a constant flow setpoint for the minute between change and restore |
| C | `ka` (`15`) | boiler sequence 1 | `ca fd` | `ff` | 0 → 1 → 0 | `d0 ca fd 01 00` | `8c ca fd 00 00` | `95 ca fd` | **high**: reorders the cascade (boiler A / B); may switch a boiler off or on. Owner, boilers without demand |
| C | `ka` (`15`) | boiler sequence 2 | `cb fd` | `ff` | 1 → 0 → 1 | `84 cb fd 00 00` | `d8 cb fd 01 00` | `c9 cb fd` | **high**: same, sent right after the line above so that A and B stay distinct |
| C | `fs1` (`35`) | circuit type | `73 09` | `ff` | 2 → 3 → 2 | `b4 73 09 03 00` | `e8 73 09 02 00` | `19 73 09` | **high**: reconfigures the circuit (radiator 60 to 75); may reset the curve. Owner |
| C | `fs2` (`75`) | circuit type | `73 09` | `ff` | 3 → 2 → 3 | `e8 73 09 02 00` | `b4 73 09 03 00` | `19 73 09` | **high**: same (radiator 75 to 60). Owner |
| C | `fs3` (`f5`) | circuit type | `73 09` | `ff` | 3 → 2 → 3 | `e8 73 09 02 00` | `b4 73 09 03 00` | `19 73 09` | **high**: same (radiator 75 to 60). Owner |
| D | `fs1` (`35`) | holiday start, day | `1b 01` | `ff` | 30 → 29 → 30 | `fc 1b 01 1d 00` | `18 1b 01 1e 00` | `0d 1b 01` | low to medium: the period stays in the past (year 2000); an immediate effect was once seen on a room unit when a period covering the day was written |
| D | `fs1` (`35`) | holiday start, month | `1c 01` | `ff` | 10 → 9 → 10 | `58 1c 01 09 00` | `bc 1c 01 0a 00` | `c5 1c 01` | same |
| D | `fs1` (`35`) | holiday start, year | `1d 01` | `ff` | 0 → 24 → 0 | `bc 1d 01 18 00` | `54 1d 01 00 00` | `99 1d 01` | same |
| D | `fs1` (`35`) | holiday end, day | `1e 01` | `ff` | 1 → 2 → 1 | `f4 1e 01 02 00` | `10 1e 01 01 00` | `7d 1e 01` | same |
| D | `fs1` (`35`) | holiday end, month | `1f 01` | `ff` | 11 → 12 → 11 | `30 1f 01 0c 00` | `f8 1f 01 0b 00` | `21 1f 01` | same |
| D | `fs1` (`35`) | holiday end, year | `20 01` | `ff` | 0 → 24 → 0 | `08 20 01 18 00` | `e0 20 01 00 00` | `3d 20 01` | same |
| D | `fs2` (`75`) | holiday start, day | `1b 01` | `ff` | 30 → 29 → 30 | `fc 1b 01 1d 00` | `18 1b 01 1e 00` | `0d 1b 01` | low to medium: the period stays in the past (year 2000); an immediate effect was once seen on a room unit when a period covering the day was written |
| D | `fs2` (`75`) | holiday start, month | `1c 01` | `ff` | 10 → 9 → 10 | `58 1c 01 09 00` | `bc 1c 01 0a 00` | `c5 1c 01` | same |
| D | `fs2` (`75`) | holiday start, year | `1d 01` | `ff` | 0 → 24 → 0 | `bc 1d 01 18 00` | `54 1d 01 00 00` | `99 1d 01` | same |
| D | `fs2` (`75`) | holiday end, day | `1e 01` | `ff` | 1 → 2 → 1 | `f4 1e 01 02 00` | `10 1e 01 01 00` | `7d 1e 01` | same |
| D | `fs2` (`75`) | holiday end, month | `1f 01` | `ff` | 11 → 12 → 11 | `30 1f 01 0c 00` | `f8 1f 01 0b 00` | `21 1f 01` | same |
| D | `fs2` (`75`) | holiday end, year | `20 01` | `ff` | 0 → 24 → 0 | `08 20 01 18 00` | `e0 20 01 00 00` | `3d 20 01` | same |
| D | `fs3` (`f5`) | holiday start, day | `1b 01` | `ff` | 30 → 29 → 30 | `fc 1b 01 1d 00` | `18 1b 01 1e 00` | `0d 1b 01` | low to medium: the period stays in the past (year 2000); an immediate effect was once seen on a room unit when a period covering the day was written |
| D | `fs3` (`f5`) | holiday start, month | `1c 01` | `ff` | 10 → 9 → 10 | `58 1c 01 09 00` | `bc 1c 01 0a 00` | `c5 1c 01` | same |
| D | `fs3` (`f5`) | holiday start, year | `1d 01` | `ff` | 0 → 24 → 0 | `bc 1d 01 18 00` | `54 1d 01 00 00` | `99 1d 01` | same |
| D | `fs3` (`f5`) | holiday end, day | `1e 01` | `ff` | 1 → 2 → 1 | `f4 1e 01 02 00` | `10 1e 01 01 00` | `7d 1e 01` | same |
| D | `fs3` (`f5`) | holiday end, month | `1f 01` | `ff` | 11 → 12 → 11 | `30 1f 01 0c 00` | `f8 1f 01 0b 00` | `21 1f 01` | same |
| D | `fs3` (`f5`) | holiday end, year | `20 01` | `ff` | 0 → 24 → 0 | `08 20 01 18 00` | `e0 20 01 00 00` | `3d 20 01` | same |
| E | `fs1` (`35`) | heating program 1, Sunday slot 3 | `72 14` | `31` | 8080 → 0908 → 8080 | `4c 72 14 09 08` | `30 72 14 80 80` | `58 72 14` | low: 02:00–02:15 on Sunday, restored within a minute |
| E | `fs1` (`35`) | heating program 2, Sunday slot 3 | `72 15` | `31` | 8080 → 0908 → 8080 | `f0 72 15 09 08` | `8c 72 15 80 80` | `59 72 15` | low: 02:00–02:15 on Sunday, restored within a minute |
| E | `fs1` (`35`) | heating program 3, Sunday slot 3 | `72 16` | `31` | 8080 → 0908 → 8080 | `68 72 16 09 08` | `14 72 16 80 80` | `5a 72 16` | low: 02:00–02:15 on Sunday, restored within a minute |
| E | `fs1` (`35`) | hot-water program (stored only), Sunday slot 3 | `72 17` | `31` | 8080 → 0908 → 8080 | `d4 72 17 09 08` | `a8 72 17 80 80` | `5b 72 17` | low: 02:00–02:15 on Sunday, restored within a minute |
| E | `fs1` (`35`) | circulation program (stored only), Sunday slot 3 | `72 1a` | `31` | 4c44 → 4b44 → 4c44 | `3c 72 1a 4b 44` | `f4 72 1a 4c 44` | `56 72 1a` | none: stored only (17:00–19:00 → 17:00–18:45) |
| E | `fs2` (`75`) | heating program 1, Sunday slot 3 | `72 14` | `31` | 8080 → 0908 → 8080 | `4c 72 14 09 08` | `30 72 14 80 80` | `58 72 14` | low: 02:00–02:15 on Sunday, restored within a minute |
| E | `fs2` (`75`) | heating program 2, Sunday slot 3 | `72 15` | `31` | 8080 → 0908 → 8080 | `f0 72 15 09 08` | `8c 72 15 80 80` | `59 72 15` | low: 02:00–02:15 on Sunday, restored within a minute |
| E | `fs2` (`75`) | heating program 3, Sunday slot 3 | `72 16` | `31` | 8080 → 0908 → 8080 | `68 72 16 09 08` | `14 72 16 80 80` | `5a 72 16` | low: 02:00–02:15 on Sunday, restored within a minute |
| E | `fs2` (`75`) | hot-water program (stored only), Sunday slot 3 | `72 17` | `31` | 8080 → 0908 → 8080 | `d4 72 17 09 08` | `a8 72 17 80 80` | `5b 72 17` | low: 02:00–02:15 on Sunday, restored within a minute |
| E | `fs2` (`75`) | circulation program (stored only), Sunday slot 3 | `72 1a` | `31` | 4c44 → 4b44 → 4c44 | `3c 72 1a 4b 44` | `f4 72 1a 4c 44` | `56 72 1a` | none: stored only (17:00–19:00 → 17:00–18:45) |
| E | `fs3` (`f5`) | heating program 1, Sunday slot 3 | `72 14` | `31` | 8080 → 0908 → 8080 | `4c 72 14 09 08` | `30 72 14 80 80` | `58 72 14` | low: 02:00–02:15 on Sunday, restored within a minute |
| E | `fs3` (`f5`) | heating program 2, Sunday slot 3 | `72 15` | `31` | 8080 → 0908 → 8080 | `f0 72 15 09 08` | `8c 72 15 80 80` | `59 72 15` | low: 02:00–02:15 on Sunday, restored within a minute |
| E | `fs3` (`f5`) | heating program 3, Sunday slot 3 | `72 16` | `31` | 8080 → 0908 → 8080 | `68 72 16 09 08` | `14 72 16 80 80` | `5a 72 16` | low: 02:00–02:15 on Sunday, restored within a minute |
| E | `fs3` (`f5`) | hot-water program (stored only), Sunday slot 3 | `72 17` | `31` | 8080 → 0908 → 8080 | `d4 72 17 09 08` | `a8 72 17 80 80` | `5b 72 17` | low: 02:00–02:15 on Sunday, restored within a minute |
| E | `fs3` (`f5`) | circulation program (stored only), Sunday slot 3 | `72 1a` | `31` | 4c44 → 4b44 → 4c44 | `3c 72 1a 4b 44` | `f4 72 1a 4c 44` | `56 72 1a` | none: stored only (17:00–19:00 → 17:00–18:45) |
| E | `em1` (`50`) | hot-water program, Sunday slot 3 | `72 17` | `31 (then ff if not taken)` | 8080 → 0908 → 8080 | `d4 72 17 09 08` | `a8 72 17 80 80` | `5b 72 17` | low: hot water / circulation 02:00–02:15 on Sunday, restored within a minute |
| E | `em1` (`50`) | circulation program, Sunday slot 3 | `72 1a` | `31 (then ff if not taken)` | 8080 → 0908 → 8080 | `b0 72 1a 09 08` | `cc 72 1a 80 80` | `56 72 1a` | low: hot water / circulation 02:00–02:15 on Sunday, restored within a minute |
| F | `ka` (`15`) | modulation maximum | `ea fd` | `ff` | 80 → 79 → 80 | `38 ea fd 4f 00` | `18 ea fd 50 00` | `a9 ea fd` | **medium**: shifts the switch-on point of the next boiler of the cascade for a minute |
| F | `ka` (`15`) | modulation minimum | `eb fd` | `ff` | 30 → 31 → 30 | `f8 eb fd 1f 00` | `a4 eb fd 1e 00` | `f5 eb fd` | **medium**: same, switch-off point |


### Order and risks

- **First, without any write: the clock.** An export of the telegram log of every `fe 07 00`
  telegram from `31` and from `f1` over the ten days it keeps. If `f1`'s clock drifts (its
  backup is known to be faulty), one of the half-hourly broadcasts of the automation will be
  followed by an `f1` broadcast that carries the time sent where the one before did not: that
  is the proof, with no new write. There is no harmless way to provoke a clock change: a
  broadcast of the time the devices already show proves nothing, and any other time moves the
  heating programs of every circuit until the next correction.
- **Batch A** (5 writes and 5 restores): low risk.
- **Batch E** (17 slots): low risk; heating, hot water and circulation of a Sunday 02:00–02:15
  for the minute the slot is changed. For the two programs of `50`, the source is not known:
  send from `31` first; if the read gives the old value, send from `ff`.
- **Batch D** (18 registers): the period stays in the past (year 2000 or 2024). Low to medium:
  the writes of 2026-10-30, a period covering the day, had an immediate effect on one room unit
  that was never explained. An unoccupied time.
- **Batch B** (3): **medium**, the circuit runs on a constant flow setpoint for a minute. An
  unoccupied time.
- **Batch F** (2): **medium**, the cascade staging moves for a minute.
- **Batch C** (5): **high**, structural: the boiler sequence reorders the cascade and may
  switch a boiler on or off; the circuit type reconfigures the circuit and may reset its
  curve. **Owner's decision**, with the boilers without demand, or not at all.
- **Not in the plan**: the adaption (`15 01`) and the room factor (`0f 01`) of the three room
  units read 0x8000 (function not used); a write is not meaningful here.

## Definitions

None in this record yet. Only one write meets the rule (a change captured, acknowledged and
read back): the slot `20 14` of `fs1`. Two things stop its definition:

- The metadata allows write conditions only on a message of kind `setting`; a program slot is
  `program_slot`. The contract (`docs/companion-contract.md`) would need write conditions for
  program slots, or the slots a kind of their own: a change of the contract, to decide first.
- One slot of one device out of 357. Whether one captured slot per program and device stands
  for the 21 slots of that program (same register scheme, same codec) is the **owner's
  decision**; with it, batch E would prove all 357 slots in 17 changes.

The choices and dates need a read definition and a value list as well as the write: none is
in a lot today.

## Equipment

Kromschröder WCM regulators on eBUS, `MF=Kromschröder`, `ID=W`: system manager at `15`
(its own circuit at `50`), room units at `35`, `75`, `f5`, heating modules at `51`, `52`,
clock master at `f1`.

## Date

2026-11-18.

## Not verified

- The value lists of the choices beyond the values read (legionella day 1, sequence 0 and 1,
  holiday level 0, control variation 1, circuit type 2 and 3).
- That `50` takes program writes from `31`.
- The third register of a holiday date.
