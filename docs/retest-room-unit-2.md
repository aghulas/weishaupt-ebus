# Retest plan: program writes on room unit 2 (`75`)

For the deployment session, step by step. **Each write needs the owner's approval, given for
that step, in the session's window** (rule 7: nothing is written from this repository). Reads
first; a write only when the reads before it leave the question open. Prepared 2026-11-19.

## What is on record

Four program-slot writes to room unit 2, all acknowledged `00`, none kept
([evidence/choice-date-program-writes.md](../evidence/choice-date-program-writes.md)):

| When | Source | Telegram (`50 23`, master data) | Slot | Read back (`58 72 14` / `a4 10 14`) |
|---|---|---|---|---|
| 2026-11-18 21:13:56 | `31` | `75 5023 05 4c 72 14 09 08` | heating 1, Sunday slot 3, unused → 02:00–02:15 | `80 80` at 21:13:59, 21:14:05, 21:43:08 |
| 2026-11-18 21:42:51 | `ff` | the same | the same | `80 80` at 21:42:55 |
| 2026-11-19 08:43:45 | `31` | the same | the same | `80 80` at 08:43:48 and a minute later |
| 2026-11-19 08:46 | `31` | `75 5023 05 1e 10 14 47 1a` | heating 1, Monday slot 1, in use 06:30–18:00 → 06:30–17:45 | `48 1a` before, at 08:46:29 and 08:47:29 |

The same telegrams were kept by room unit 1 (`35`), room unit 3 (`f5`) and the system manager's
circuit (`50`, hot water and circulation). Room unit 2 took, from `ff`, its eleven numeric
settings, the holiday level, the holiday dates and the control variation: only program slots
are refused.

## What is new since

- **Room unit 2 holds a copy of room unit 1's programs.** All 105 slots of the five programs of
  `75` equal those of `35`, slot for slot; `f5` differs (Tuesday of heating program 1)
  ([evidence/room-units-programs.md](../evidence/room-units-programs.md), compared 2026-11-19).
- **The vendor tool groups units 1 and 2.** Its window is "FS#1+2" for `35`; the tab of the
  second heating circuit reads room unit `75` and module `51`; unit 3 has its own window with
  module `52` ([evidence/service-tool-ui-exploration.md](../evidence/service-tool-ui-exploration.md)).
  The room unit's manual (83277504, pages 11 and 105) has an address "WTC-Chauf.#1 + EM-Chauf.#2"
  for one room unit that controls two heating circuits.
- **`09 03` is a register write.** The tool writes registers with `09 03 <reg lo> <reg hi> <val lo>
  <val hi>` (the fault-log selector, taken from source `31`); the room units use `09 03` towards
  their modules from sources `70` and `f0`.
- The tool knows no lock on programs; `10 00` = 2 and `12 01` = 11 on all three units; `75`
  differs from `35` only in the circuit type (3 / 2) and the clock copy (register survey).
- Address `50` (the manager's own circuit) takes program writes from `31`.

## Hypotheses, ranked

1. **The programs of unit 2 are kept elsewhere and `75` mirrors them.** Its 105 slots are those of
   `35`, and the tool treats `35` as "FS#1+2". If `35` (or the manager) writes them into `75`, a
   write to `75` is acknowledged and replaced, or ignored, and the program of circuit 2 is edited
   on `35`. First test: a write on `35`, then read `75` (step 2).
2. **The role of unit 2 makes its store read-only** (P312 "Adresse FS", P335 "Config. FS"): the
   same effect seen from the unit. Test: the owner's reading of P312 / P335 (on-site checklist,
   `docs/owner-checklist-room-units.md`) and the display test (step 3).
3. **The source matters**: unit 2 takes programs only from its partner (`30`, the master
   address of `35`). Written from `31` and `ff` so far. Test: step 5, only if 1 and 2 leave it
   open.
4. **The service matters**: unit 2 takes programs by `09 03` only. Least likely (`35`, `f5`, `50`
   take `50 23`); cheap to test (step 4).

## Steps

Reads use ebusd's address (`hex` without `-s`); the answer is `02 <lo> <hi>`. Slot used: heating
program 1, Sunday slot 3 (`72 14`), unused on all three units (`80 80`), so a change touches a
Sunday 02:00–02:15 only. **"Taken"** = the read-back after 3 s and after 60 s gives the written
value; **"acknowledged, not taken"** = ack `00` and the old value. Stop at once if any write is
not acknowledged, if any read of another device changes unexpectedly, or on the owner's word;
restore before stopping.

### Step 1 — read only: who writes `75` (telegram log, no bus)

Export from the telegram log (ten days) every telegram with source `30` or `70`, or target `35`,
`75` or `51`, of service `50 22`, `50 23`, `09 02` or `09 03`, and every write (`50 23` or
`09 03`) to a register `0x1410`–`0x1a72` of any device. Read for: a `30 → 75` or `f1 → 75` write
of program registers (the mirror), a `70 → 51` `09 03` (unit 2 passing its programs to its
module), and the days when someone changed a program on a display (the real write path).
Expected if hypothesis 1 holds: writes into `75` from `30` (or `f1`) after a change on `35`.

### Step 2 — a write on `35`, read on `75` (owner's approval)

The write path proven on `35` (2026-11-18 21:11).

| # | Command | Expected |
|---|---|---|
| 2a | `hex 35502203587214`, `hex 75502203587214` | `02 80 80` on both |
| 2b | `hex 355023054c72140908` | ack `00` |
| 2c | after 3 s, 60 s and 5 min: the two reads of 2a | `35` → `09 08`; `75` → `09 08` **if it mirrors `35`**, `80 80` otherwise |
| 2d | restore `hex 355023053072148080` | ack `00` |
| 2e | after 3 s, 60 s and 5 min: the two reads | `80 80` on both (if `75` followed in 2c, it follows back) |

Risk low: a Sunday 02:00–02:15 heating slot of circuit 1 (and 2 if mirrored) for about six
minutes. Result: `75` follows → hypothesis 1 holds; the programs of circuit 2 are edited through
`35`, and `75`'s program messages stay read only by design (a comment, no write).

### Step 3 — the owner edits the slot on the display of unit 2 (owner's action)

With the deploy session watching the bus (telegram log and `grab result all` before and after):
the owner opens heating program 1 on the display of `75`, sets Sunday's third period to
02:00–02:15, confirms; the session reads `58 72 14` on `75`, `35`, `51` and `15`; the owner sets
it back to empty; the session reads again. The telegrams sent by `70` (and by `30`) in those two
minutes are the real write path: the target and the service of the write. Matches the on-site
checklist item 3.

### Step 4 — `09 03` to `75` (only if 1–3 leave it open; owner's approval)

| # | Command | Expected |
|---|---|---|
| 4a | `hex 75502203587214` | `02 80 80` |
| 4b | `hex 7509030472140908` (`09 03`, register `72 14`, value `09 08`) | ack `00` |
| 4c | after 3 s and 60 s: `hex 75502203587214` | `09 08` = taken by `09 03` |
| 4d | restore `hex 7509030472148080`, then read | `80 80` |

### Step 5 — source `30` (only if 1–4 leave it open; owner's approval)

`hex -s 30 755023054c72140908`, read as in 4c, restore `hex -s 30 755023053072148080`. Sending
from `30` borrows the master address of room unit 1: arbitration protects the bus, but unit 2
may take it as a message of unit 1. One write and one restore, nothing else from `30`.

### Step 6 — mode or access level (fall-back)

With the installer level open on the display of `75` (owner), step 4 or the original `50 23`
write once more. If still refused, the on-site checklist (P312, P335) decides.

## Second pass of the vendor tool

The session `wcm-diagnose-ui` notes how the tool groups the units and anything in which `75`
differs on screen. Its findings go here, before step 2 is run:

- (to be filled)

## Date

2026-11-19.
