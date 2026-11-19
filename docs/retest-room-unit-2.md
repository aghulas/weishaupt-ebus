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

## Step 1 done (2026-11-19, read only): what the bus shows

Telegram-log export over ten days, 272 319 telegrams
(`out/ebusd-telegram-log-export/2026-11-19-retest-75-step1.csv`, installation data):

- **No mirror on the bus.** Every program-register write (`0x1410`–`0x1a72`) of the ten days is
  ours: `35` ×24, `f5` ×11, `50` ×4, `75` ×3. None from `30` or `f1` to `75`, none from `70` or
  `30` to `35`. No edit on a display reached the bus as `50 23` or `09 03`.
- **Room unit 1 (`30`) is silent**: two reads, both to `f6`.
- **Room unit 2 (`70`) drives module `51`, and only it**, about 17 000 telegrams a day:
  - `09 03` writes of its own settings into the module, about every ten minutes (1 400 each):
    `28 00` = `ee 02` (75.0, maximum flow), `2b 01` = `50 00` (8.0, minimum flow), `41 01` =
    `01 00` (control variation 1), `73 09` = `03 00` (circuit type 3), `b1 09` = `b4 00` (180 s);
  - `09 03` writes every 20 s or so (42 000 each) of `20 0a` = 0 (once 232) and `85 02` = 0;
  - `09 02` reads of the module's `0c 0a` (the weighted outside temperature, 12–13 °C), `29 0a`
    (input H1, 0 and 1) and `59 03`.
- Step 2a read: slot `72 14` = `80 80` on `35` and `75`.

What it says: **the unit that runs circuit 2 is `75`**. It writes its settings into module
`51`, sends the heat demand of the circuit (`70 → f1`, `05 07`) and the room-unit / module
exchange (`HcMode`, `70 → 51`); batch B showed it too (the control variation written on `75`
moved the flow setpoint of `51`). The "FS#1+2" window of the vendor tool groups units 1 and 2 on
screen; the bus does not show unit 1 controlling circuit 2. The program of circuit 2 is then
evaluated by `75` itself, from its own store, whose 105 slots equal those of `35` (most likely
copied once, at commissioning). A read-only check of that: on a Tuesday between 22:05 and 22:25,
when heating program 1 of `75` still runs (to 22:30) and the programs of `15`, `50`, `51` have
ended (22:00), the flow setpoint of `51` and the room setpoint of `75` (`12 00`) show which
program circuit 2 follows.

## Hypotheses, ranked (after step 1)

1. **The role or an access setting of unit 2 refuses program edits from the bus** (P312 "Adresse
   FS", P335 "Config. FS", or a setting no register read shows): `75` runs its circuit from its
   own programs and takes every other setting from `ff`. Test: the owner's reading of P312 /
   P335 and the display test (step 3), then the installer level open (step 6).
2. **The source matters**: unit 2 takes program writes only from a given master. Written from
   `31` and `ff` so far. Test: step 5 (`30`), only if 1 leaves it open.
3. **The service matters**: `09 03` instead of `50 23` (step 4). Unit 2 itself writes its module
   with `09 03`; cheap to test.
4. **The programs of unit 2 are kept elsewhere and `75` mirrors them**: no mirror is seen on the
   bus in ten days; weakened, not excluded (a copy at commissioning, or a path not logged). Step 2
   still settles it in six minutes, and the deploy session is asking the owner for it.

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
