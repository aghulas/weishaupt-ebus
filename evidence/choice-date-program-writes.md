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
  curve. **Not done for now** (owner, 2026-11-18): boiler sequence and circuit type stay read
  only. A change of either can stop a boiler or reconfigure a circuit while it heats, and
  neither is a setting an operator changes in service; they belong to the commissioning of the
  installation.
- **Not in the plan**: the adaption (`15 01`) and the room factor (`0f 01`) of the three room
  units read 0x8000 (function not used); a write is not meaningful here.

## Definitions

Defined on 2026-11-18 from the captures on site: the five choices of batch A (lot C, value
lists in `wtc_inc`), the date and time broadcast (lot C, `broadcast`, as a write beside the
passive message of the general file), and the five programs of room unit 1 (lot H, 105 slots).
Not defined: the programs of `fs2`, `fs3`, `50`, the holiday dates, the control variation, the
boiler sequence and the circuit type.

**One slot per program and device stands for its 21 slots** (owner, 2026-11-18). The argument:
the 21 slots of one program of one device differ only in the register address, the weekday in
the high nibble of the first byte (1 to 7) and the slot in the low nibble (0 to 2), with the
program in the second byte; every slot has the same two-byte value (end, start, quarter hours,
bit 7 = disabled), the same checksum routine, the same source, and is answered the same way
by the read (lot H reads all 21 with one codec). A captured change of one slot proves the
device takes a write of that program from that source with that encoding; the other 20 would
need a different register stride or codec to behave otherwise, and none is seen. It does not
extend to another program or another device: their source and acceptance are tested
separately (batch E).

Defined on that basis (2026-11-18): **heating program 1 of `fs1`, its 21 slots**, read and
written in lot H (`35.w.fs1`, base `SwitchTimesSetting`), the captured slot being `20 14`
(`HCProgram1Tue1`). In the metadata, the 21 carry write conditions with source `31`, class
`comfort`, and proof `family` naming `HCProgram1Tue1`; the captured slot itself shows
`change-observed`. The contract was extended for it (write conditions on program slots).

The choices and dates need a read definition and a value list as well as the write: none is
in a lot today.


## Captures on site, 2026-11-18 evening

By the operator's deployment session, each on the owner's go, service tool disconnected, raw
telegrams through ebusd; exports of the telegram log for the period (installation data, not in
this repository). Only telegrams and dates are quoted.

### Clock: the broadcast is taken (read only)

Every `fe 07 00` telegram of the telegram log from `31` and from `f1`, 2026-11-08 20:42 to
2026-11-18 21:07: 520 from `31`, 14 332 from `f1`. `f1` broadcasts once a minute, at about
second 04, its time normally 0 to 1 s behind the host. In **72 of 72** cases where a broadcast
of `31` carried a time 3 s or more away from `f1`'s, the next regular broadcast of `f1` carried
the time sent by `31`. Examples (master data: outside temperature, then BCD second, minute,
hour, day, month, weekday, year):

| date | sender | time of the log | data | time carried |
|---|---|---|---|---|
| 2026-11-18 | `31` | 14:46:59 | `00 0d 00 46 14 18 11 03 26` | 14:46:00 (59 s late) |
| 2026-11-18 | `f1` | 14:48:04 | `00 0d 05 47 14 18 11 03 26` | 14:47:05: taken, 59 s behind |
| 2026-11-18 | `31` | 15:00:00 | `00 0d 00 00 15 18 11 03 26` | 15:00:00 |
| 2026-11-18 | `f1` | 15:01:04 | `00 0d 04 01 15 18 11 03 26` | 15:01:04: back on time |
| 2026-11-10 | `31` | 19:00:06 | `00 0d 00 00 19 10 11 02 26` | 19:00:00 (6 s late) |
| 2026-11-10 | `f1` | 19:01:11 | `00 0d 04 01 19 10 11 02 26` | 19:01:04: taken, 7 s behind |

- **Known limit**: the clock master takes the time as sent, seconds included. A broadcast sent
  late with second 00 (off the minute grid: 6 to 59 s late, seen 70 times) sets the whole
  installation behind until the next correct one; the half-hourly broadcast of an automation
  of the installation corrected each. A sender must send at second 00 of the minute it carries.
- Not explained: 167 of the 520 broadcasts of `31` are followed within 3 s by an `f1`
  telegram carrying a time 59 s ahead; `f1`'s next regular broadcast is normal.
- The outside temperature sent is replaced by `f1` with its own sensor within a minute.

### Batch A: five choices proven (21:08 to 21:10, source `ff`)

| setting | date | source | change | read → answer | restore | read → answer |
|---|---|---|---|---|---|---|
| ka DHWLegionellaDay | 2026-11-18 21:08 | `ff` | `0c 01 01 02 00` | `5d 01 01` → `02 00` | `e8 01 01 01 00` | `5d 01 01` → `01 00` |
| ka CircWithLegionella | 2026-11-18 21:09 | `ff` | `e8 f3 13 01 00` | `f3 f3 13` → `01 00` | `b4 f3 13 00 00` | `f3 f3 13` → `00 00` |
| fs1 HolidayTempLevel | 2026-11-18 21:09 | `ff` | `54 3d 01 01 00` | `a5 3d 01` → `01 00` | `08 3d 01 00 00` | `a5 3d 01` → `00 00` |
| fs2 HolidayTempLevel | 2026-11-18 21:10 | `ff` | `54 3d 01 01 00` | `a5 3d 01` → `01 00` | `08 3d 01 00 00` | `a5 3d 01` → `00 00` |
| fs3 HolidayTempLevel | 2026-11-18 21:10 | `ff` | `54 3d 01 01 00` | `a5 3d 01` → `01 00` | `08 3d 01 00 00` | `a5 3d 01` → `00 00` |

10 writes acknowledged `00`, each read back with the value written, every value restored.
Value lists: the legionella day is 1 Monday (the protection runs on Mondays, operator's log of
2026-11-09) and 2 the next day; the rest of the list (0 off, 3 to 7) is the older community
template's and the client's, not observed. The circulation with legionella is 0 off, 1 on
(both observed, meaning from the client and the template). The holiday level is 0 antifreeze,
1 setback (`docs/discoveries.md`, 2026-11-08: the circuit went to the antifreeze setpoint with
0); 1 observed taken, its effect not.

### Batch E part 1: room unit 1, five programs proven; room unit 2 does not keep a slot

Sunday slot 3 of each program (`72 <program>`), from `31`, 21:11 to 21:14:

| setting | date | source | change | read → answer | restore | read → answer |
|---|---|---|---|---|---|---|
| fs1 HCProgram1Sun3 | 2026-11-18 21:11 | `31` | `4c 72 14 09 08` | `58 72 14` → `09 08` | `30 72 14 80 80` | `58 72 14` → `80 80` |
| fs1 HCProgram2Sun3 | 2026-11-18 21:12 | `31` | `f0 72 15 09 08` | `59 72 15` → `09 08` | `8c 72 15 80 80` | `59 72 15` → `80 80` |
| fs1 HCProgram3Sun3 | 2026-11-18 21:12 | `31` | `68 72 16 09 08` | `5a 72 16` → `09 08` | `14 72 16 80 80` | `5a 72 16` → `80 80` |
| fs1 DHWProgramSun3 | 2026-11-18 21:13 | `31` | `d4 72 17 09 08` | `5b 72 17` → `09 08` | `a8 72 17 80 80` | `5b 72 17` → `80 80` |
| fs1 CircProgramSun3 | 2026-11-18 21:13 | `31` | `3c 72 1a 4b 44` | `56 72 1a` → `4b 44` | `f4 72 1a 4c 44` | `56 72 1a` → `4c 44` |

`09 08` is 02:00 to 02:15, enabled; `80 80` the unused slot; `4b 44` / `4c 44` 17:00 to 18:45 /
19:00. With the rule above, each proves its program's 21 slots on `fs1`: the five programs of
room unit 1, 105 slots.

**Room unit 2 (`75`), heating program 1, Sunday slot 3**: 21:13:56, `31 75 5023` `4c 72 14 09 08`,
acknowledged `00` (the same master data and the same eBUS checksum as to `35`, only the
target differs); read `58 72 14` → `80 80` at 21:13:59, 21:14:05 and 21:43:08. Sent again from
`ff` at 21:42:51 (`ff 75 5023` `4c 72 14 09 08`), acknowledged, read `80 80` at 21:42:55: not
kept from either source. Nothing to restore. The batch stopped there: not sent, `fs2` four
other programs, `fs3` five, `50` two. The rule of one slot for 21 is not applied to `fs2`,
`fs3` or `50`.

### Why room unit 2 does not keep the slot: what the captures say

- **Not the telegram**: byte for byte the one `fs1` kept, checksum and acknowledgement alike.
- **Not the source**: refused from `31` and from `ff`; `fs2` took, the same evening, the holiday
  level from `ff` (21:10) and, that afternoon, eleven numeric settings from `ff`.
- **Not a delayed write**: three reads over half an hour give `80 80`; no later write to
  `72 14` of `75` is in the log.
- **Not the program content**: `fs1`, `fs2` and `fs3` read the same slots (Monday slot 1 of
  heating program 1 `48 1a`, all Sunday heating slots `80 80`); the program selector reads 11
  on the three (`docs/discoveries.md`, 2026-11-17).
- **Earlier**: the operator's log records Monday slot 1 of heating program 1 (`10 14`) written
  on the three room units from `31` on 2026-11-02 (06:00 to 22:00) and restored on 2026-11-03,
  read back `48 1a`: a **used** slot, changed in place, apparently taken by `fs2` then
  (transcribed, no telegram kept; whether the change was read back on `fs2` is not written).

Hypotheses, in the order the captures leave them open:

1. `fs2` does not take a write that **enables an unused slot** (`80 80` → a time), but takes a
   change of a slot in use; `fs1` would then differ (it is the room unit at `35`, the one whose
   date and time the others follow, `docs/discoveries.md` 2026-10-30).
2. `fs2` takes **no program write at all** now (an access or lock setting of the room unit, the
   "access to heating circuit without remote control" of the manual, WCM-FS 2.0 user manual
   83277702, chapter 4.7.27, not read here); the 2026-11-02 case would then be a write not
   checked on `fs2`.
3. Something particular to `fs2` that evening (its display in a menu, a user at the unit).

### Smallest next test (not sent)

One write, one restore, on **room unit 3**, the same slot: `31 f5 5023` `4c 72 14 09 08`, read
`58 72 14`, restore `30 72 14 80 80`. If `fs3` keeps it, `fs2` is the odd one (hypothesis 3 or a
setting of `fs2`); if `fs3` refuses it too, `fs1` is the odd one and hypotheses 1 and 2 remain.
Then, only if needed, on `fs2` a **used** slot changed in place and restored: Monday slot 1 of
heating program 1, `48 1a` (06:30 to 18:00) → `47 1a` (06:30 to 17:45): `31 75 5023`
`1e 10 14 47 1a`, restore `8e 10 14 48 1a` (the restore telegram of 2026-11-03); it
tells hypothesis 1 from 2. The first changes heating for a Sunday night only; the second
shortens a heating period by 15 minutes for the minute it lasts.

### Room unit 3, heating program 1 (2026-11-19)

| setting | date | source | change | read → answer | restore | read → answer |
|---|---|---|---|---|---|---|
| fs3 HCProgram1Sun3 | 2026-11-19 07:55 | `31` | `4c 72 14 09 08` | `58 72 14` → `09 08` | `30 72 14 80 80` | `58 72 14` → `80 80` |

Read `80 80` before the change. The same telegrams as kept by room unit 1. Heating program 1
of `fs3` is proven, its 21 slots by the rule above; its four other programs are not (one
program captured). **Room unit 2 is the one that differs**, not room unit 1.

What could differ on room unit 2, from the captures only:

- Not the software: the scan gives the three room units the same software and hardware
  (`SW=2726`, `HW=ffff`); the fifth byte of the identification reads `18` on `35` and `75`,
  `08` on `f5`: room unit 2 has the value of room unit 1, which keeps the slot.
- Not a setting read so far: of 205 registers read on the three units, six differ, all current
  values (heat demand, flow setpoint, room temperature, room setpoint), the curve, and the
  circuit type (`fs1` 2, `fs2` and `fs3` 3): room unit 2 has the values of room unit 3, which
  keeps the slot.
- Its pairing: room unit 2 (master `70`) drives heating module `51`, room unit 3 (`f0`) module
  `52`, room unit 1 (`30`) the system manager's circuit `50`. The two modules have the same
  software (`SW=7203`); what each takes from its room unit by `09 03` is the same list.
- Left: a setting of room unit 2 no register read shows (an access or lock of program edits,
  WCM-FS 2.0 user manual 83277702, chapter 4.7.27, not read here); a state of the unit at
  21:13 and 21:42 on 2026-11-18 (a menu open on its display, someone at the unit); or a
  refusal to enable an unused slot that the two others do not have.

Next tests, none sent: the same telegram to `75` again at another time (`31 75 5023`
`4c 72 14 09 08`, restore `30 72 14 80 80`): kept now means a passing state; refused again,
then a used slot changed in place (`1e 10 14 47 1a`, restore `8e 10 14 48 1a`): kept means
room unit 2 refuses only to enable an unused slot. A look at the display of room unit 2 (menu,
access level) answers the rest.


### Batch of 2026-11-19: the other programs of room unit 3, the programs of `50`, room unit 2 again

08:41 to 08:44, on the owner's word, service tool disconnected, all from `31`; each register read
before (the "now" value) and after each write.

| setting | date | source | change | read → answer | restore | read → answer |
|---|---|---|---|---|---|---|
| fs3 HCProgram2Sun3 | 2026-11-19 08:41 | `31` | `f0 72 15 09 08` | `59 72 15` → `09 08` | `8c 72 15 80 80` | `59 72 15` → `80 80` |
| fs3 HCProgram3Sun3 | 2026-11-19 08:41 | `31` | `68 72 16 09 08` | `5a 72 16` → `09 08` | `14 72 16 80 80` | `5a 72 16` → `80 80` |
| fs3 DHWProgramSun3 | 2026-11-19 08:42 | `31` | `d4 72 17 09 08` | `5b 72 17` → `09 08` | `a8 72 17 80 80` | `5b 72 17` → `80 80` |
| fs3 CircProgramSun3 | 2026-11-19 08:42 | `31` | `3c 72 1a 4b 44` | `56 72 1a` → `4b 44` | `f4 72 1a 4c 44` | `56 72 1a` → `4c 44` |
| em1 DHWProgramSun3 | 2026-11-19 08:43 | `31` | `d4 72 17 09 08` | `5b 72 17` → `09 08` | `a8 72 17 80 80` | `5b 72 17` → `80 80` |
| em1 CircProgramSun3 | 2026-11-19 08:43 | `31` | `b0 72 1a 09 08` | `56 72 1a` → `09 08` | `cc 72 1a 80 80` | `56 72 1a` → `80 80` |

12 writes acknowledged `00`, each read back with the value written and restored. `50` takes the
program writes from `31` (unlike its flow limits); its hot-water slot, the applied program,
was changed for 4 s. With the rule above: the five programs of room unit 3 and the two of `50`
are proven, 147 slots.

**Room unit 2 again**, same batch: `31 75 5023` `4c 72 14 09 08` at 08:43:45, acknowledged, read
`58 72 14` → `80 80` at 08:43:48 and one minute later. Nobody looked at its display. Refused on
2026-11-18 at 21:13 and 21:42 and on 2026-11-19 at 08:43: **not a passing state**. Left: a
setting of room unit 2 that no register read shows (a lock of program edits, an access level),
or a refusal to enable an unused slot that room units 1 and 3 do not have. Next, if wanted: a
used slot changed in place (`1e 10 14 47 1a`, restore `8e 10 14 48 1a`), and a look at the
display and access settings of room unit 2.

### Room unit 2 refuses a slot in use too (2026-11-19 08:46)

| setting | date | source | change | read → answer |
|---|---|---|---|---|
| fs2 HCProgram1Mon1 | 2026-11-19 08:46 | `31` | `1e 10 14 47 1a` (06:30 to 17:45) | `a4 10 14` → `48 1a` before, at 08:46:29 and at 08:47:29 |

Acknowledged `00`, not kept; nothing to restore. So room unit 2 does not refuse only the
enabling of an unused slot: it keeps **no program write**, from `31` or from `ff`, used or
unused slot, on two days. **The programs of `fs2` stay read only.**

What is left, read only:

- **No lock in the manuals.** The user manual of the WCM-FS 2.0 (document 83277702) gives the
  programs as editable at the end-user level (chapters 4.7.24 and 4.7.25, pages 38 and 39) and
  names no lock or access code for them; its "Lockout" (page 9) is a fault display. The
  installer manual (document 83277504, page 36) lists the commissioning parameter P312
  "address of the room unit", which sets the role of each unit (control centre, heating circuit
  1 of the boiler, heating circuit of extension module 2, or both; user manual page 37); the user
  manual's chapter 4.7.27 (page 41) lets one room unit set an extension module that has no room
  unit of its own, its time programs included. Which register holds P312, and whether the
  role of room unit 2 keeps its programs elsewhere, is not established.
- **No candidate among the registers read.** Of 205 registers read on the three room units, six
  differ (heat demand, flow setpoint, room temperature, room setpoint: current values; the
  curve; the circuit type, where room unit 2 equals room unit 3). None is a lock. The
  identification differs in one byte (`18` on `35` and `75`, `08` on `f5`), room unit 2 having
  the value of room unit 1, which keeps program writes.
- **The change of 2026-11-02** on the three room units (Monday slot 1, the operator's log) was
  never checked on room unit 2: the log gives the restore read back, not the change.

Next, read only: the display of room unit 2 (installer level, P312 and the menu "Access HC
w.o. FS" of the other units), and the parameter P335 "configuration of the room unit" on
each.

### The identification of room unit 2 (2026-11-19)

After a restart of ebusd on 2026-11-19 at 08:27, the operator's deployment session read
`SW=7203` (the software of the heating modules) for `75` in ebusd's list of participants.
Checked read only:

- Every identification answer of `75` captured, 2026-10-29 to 2026-11-19 08:39 (snapshots of
  `grab result all`, the scans of master `00`): `0a 50 57 02 00 18 00 27 26 ff ff`, that is
  `MF=Kromschröder`, `ID=W`, `SW=2726`, `HW=ffff`; the same as room unit 1 (`35`); room unit
  3 (`f5`) differs only in the fifth byte of the identification (`08`). The modules `51`
  and `52` answer `… 03 00 08 00 72 03 ff ff` (`SW=7203`).
- ebusd's list at 08:39 the same morning gives `75` `SW=2726` again.
- At its start ebusd broadcast an inquiry of existence (`31 fe 07fe`); masters answer it with an
  identification broadcast (`<qq> fe 0704`), which ebusd may file under the slave address of
  the sender (master + 5). The capture keeps only the last one (from `f0`, `SW=2726`); which
  master, if any, broadcast `7203` is not in the captures.

So `SW=2726` for room unit 2 stands, and the `7203` of 08:27 was not seen again; nothing shows
a second device answering at `75`: on 2026-11-18 its numeric settings were written and read
back as on the other units, which two devices at one address would not give. The file name
`75.w.fs2` depends on the identification `W` only, which both values share: the same file
loads either way. For the program slot refused by room unit 2 this changes nothing; the open
hypotheses stay those above.

To settle where `7203` came from, read only: an export of the telegram log of every `07 04` and
`07 fe` telegram (scans and identification broadcasts, with their sender) on 2026-11-19 from
08:27 to 08:33, and of every identification broadcast `fe 07 04` over the ten days kept.

### Shortest batch for the other programs of `fs3` and the two of `50` (not sent)

Six slots, each changed and restored: 12 writes, from `31` (for `50`: from `31` first, then
`ff` if the read gives the old value). Read the register first and send nothing if it does not
answer the "now" value. Each changes a program for a Sunday 02:00–02:15 (or a stored-only
circulation slot) for the minute it lasts: low risk; the hot-water program of `50` is the one
the installation applies.

| device | program | register | values | change | restore | read |
|---|---|---|---|---|---|---|
| `fs3` (`f5`) | heating program 2, Sunday slot 3 | `72 15` | `80 80` → `09 08` → back | `f0 72 15 09 08` | `8c 72 15 80 80` | `59 72 15` |
| `fs3` (`f5`) | heating program 3, Sunday slot 3 | `72 16` | `80 80` → `09 08` → back | `68 72 16 09 08` | `14 72 16 80 80` | `5a 72 16` |
| `fs3` (`f5`) | hot-water program (stored only), Sunday slot 3 | `72 17` | `80 80` → `09 08` → back | `d4 72 17 09 08` | `a8 72 17 80 80` | `5b 72 17` |
| `fs3` (`f5`) | circulation program (stored only), Sunday slot 3 | `72 1a` | `4c 44` → `4b 44` → back | `3c 72 1a 4b 44` | `f4 72 1a 4c 44` | `56 72 1a` |
| `em1` (`50`) | hot-water program (applied), Sunday slot 3 | `72 17` | `80 80` → `09 08` → back | `d4 72 17 09 08` | `a8 72 17 80 80` | `5b 72 17` |
| `em1` (`50`) | circulation program, Sunday slot 3 | `72 1a` | `80 80` → `09 08` → back | `b0 72 1a 09 08` | `cc 72 1a 80 80` | `56 72 1a` |

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
- The date and time broadcast has no fixture: ebusd keeps no value for a message it can only
  send, so the check cannot decode it back; its telegrams are those quoted above.
- ebusd building a slot write from the files of the lot: the definition decodes the two
  captured telegrams (fixtures); sending from it has not been observed.
- The third register of a holiday date.
