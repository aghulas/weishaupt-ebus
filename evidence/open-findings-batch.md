# Open findings — what settles each one, and batch G (prepared 2026-11-19, not sent)

The findings still open in `docs/discoveries.md` after the release of 0.5.12, each taken as
far as the captures, the manuals and ebusd's cache allow. No bus write is needed: batch G has
reads only, plus steps where the owner changes a setting on a display and ebusd reads the
register before and after. Nothing here was sent.

## Status of each finding

| Finding | Settled now? | What settles the rest |
|---|---|---|
| Register `27 02` of the boilers | **Yes, from the data**: the burner-start counter divided by 256 ([bc-info-values.md](bc-info-values.md)) | step A: one read of the neighbouring register `26 02`, which should then hold the low 16 bits |
| Device at `0c` (master `07`) | No; nothing to define either way: `07` only reads register `99 01` of `50`, `52`, `f6` with `09 02`, never `51` | none proposed; an on-site test (module `51` off the bus) costs more than the answer is worth. Close the entry as "no definition needed" |
| `PowerDemand` byte 1 (0, 85, 102, 187, 238), bytes 2 and 9 | No: the values are codes, not flags ([heat-demand.md](heat-demand.md)); the grab buffer keeps one telegram per kind | step D1: an export of the `05 07` telegrams of the telegram log over ten days, read beside the boiler status telegrams |
| `f1` answering 59 s ahead | **The 59 s, yes** (the clock master answers with the hour and minute received and its own second); which broadcasts it answers, no | step D3: the same export after the owner's clock automation has changed (no bus test can set the clock master's own second) |
| `ForcedVenting` (phase 9) | No: no manual lists a phase 9, never seen | none on the bus; if the vendor service tool is on site, the legend of its operating phase list (checklist, item 5). The label stays provisional |
| Third register of the holiday dates | No: 0 and 24 taken, nothing more | step B: the owner enters a future holiday period on a room unit's display, ebusd reads the six registers |
| `ControlVariation` 0 | **Yes**: 0 = constant flow, 1 = outside temperature, from the manual and the batch-B capture ([room-units-control-variation.md](room-units-control-variation.md)); in trial 0.5.13 as a comment | step C: which of 2 and 3 is "room" |
| `fs2` keeps no program write | No | checklist, items 1 to 3 (P312, P335 and a slot changed on the display of `fs2`), with step E |

## Batch G, ready to run

For the deployment session, on the owner's go, line by line. Reads go from ebusd's own address
(`hex` without `-s`); the answer is `02 <low> <high>`. Rule: if a "before" read does not answer
as stated, note it and go on (these are reads; nothing is restored by the session).

### Step A — register `26 02` beside `27 02` (reads only, under a minute)

Read in the same minute as the counters (`read -f -c bc1 Counters`, `read -f -c bc2 Counters`).

| # | Device | Read | Register | Expected if `27 02` is the upper 16 bits of the starts |
|---|---|---|---|---|
| A1 | `08` | `hex 08502203f62702` | `27 02` | 731 (`db 02`) while the starts are below 187 392 |
| A2 | `08` | `hex 08502203aa2602` | `26 02` | the low 16 bits of the starts: 187 277 gives `8d db` |
| A3 | `18` | `hex 18502203f62702` | `27 02` | 543 (`1f 02`) |
| A4 | `18` | `hex 18502203aa2602` | `26 02` | 139 101 gives `5d 1f` |
| A5 | `08` | `hex 085022034e2502` | `25 02` | for comparison, meaning unknown |
| A6 | `08` | `hex 08502203662802` | `28 02` | for comparison, meaning unknown |

Risk none. Outcomes: A2 and A4 equal to the starts modulo 65 536 → the two registers are a
16-bit window on the 24-bit counter, settled; anything else → `27 02` stays "starts / 256",
confirmed only when `08` passes 187 392 starts (then A1 reads 732).

### Step B — third register of the holiday dates (owner at the display of `fs1`, about 5 minutes)

| # | Who | Action | Expected |
|---|---|---|---|
| B1 | session | read `hex 355022030d1b01`, `…c51c01`, `…991d01`, `…7d1e01`, `…211f01`, `…3d2001`, `…a53d01` (start day, month, third, end day, month, third, holiday level) | 30, 10, 0, 1, 11, 0, 0 (as left by batch D) |
| B2 | owner | on `fs1`: user level (short press on the menu key), menu "Vacances", parameter 141 "Durée": a period from 24.12.2026 to 02.01.2027, confirm with OK | the display accepts it |
| B3 | session | the seven reads of B1 again | start 24 / 12, end 2 / 1; the third registers: **26 and 27 if they hold the year** (two digits), other values otherwise; level 0 |
| B4 | owner | on `fs1`: delete the period (or set it back as before), OK | — |
| B5 | session | the seven reads again | what the unit keeps when no period is set (to record) |

Risk none for the heating if the period lies in the future and is deleted at B4: nothing
changes before 24.12. If B4 is forgotten, circuit 1 goes to frost protection on 24.12 (the
holiday level is 0, frost protection): the checklist repeats it.

### Step C — values 2 and 3 of the control variation (owner at the display of `fs3`)

| # | Who | Action | Expected |
|---|---|---|---|
| C1 | owner | on `fs3`: installer level (hold the menu key 3 s), menu "Mise en service", parameter 315 "Ty régul#1"; turn the knob through the four settings and note their order; leave with "Fin", **without OK** | the order shown, likely the order of the values 0 to 3 (Const. Dép, Extérieur, …) |
| C2 | session (optional, only if C1 leaves a doubt) | read `hex f5502203254101` | 1 |
| C3 | owner (optional) | select "Ambiance", OK | — |
| C4 | session | read `hex f5502203254101` | 2 or 3: the value of "room" |
| C5 | owner | select "Extérieur" again, OK | — |
| C6 | session | read `hex f5502203254101` | 1 |

C1 has no effect on the heating. C2 to C6 put circuit 3 on room control for about a minute:
with the room at about 28 °C, above its setpoint, the module may lower the flow setpoint and
close the mixing valve for that minute; nothing lasting.

### Step D — exports of the telegram log (read only, no bus)

| # | Export | Settles |
|---|---|---|
| D1 | every `05 07` telegram (from `10` to `03` and `13`, from `30`, `70`, `f0` to `f1`) of the ten days the log keeps, with the boiler status broadcasts of the same period | byte 1, 2 and 9 of `PowerDemand` against firing, hot-water loading and setback |
| D2 | at the next restart of ebusd: the `07 04` and `07 fe` telegrams of its first two minutes | the `SW=7203` once filed under `75` |
| D3 | the `fe 07 00` broadcasts of `31` and `f1` over a week after the owner's clock automation has changed | which broadcasts the clock master answers |

### Step E — after the owner's checklist

With the owner's notes on P312 and P335 of the three room units (checklist, items 1 to 3):
if `fs2` differs, the next step follows from the difference (the manual: an address
"WTC-Chauf.#1+EM-Chauf.#2" serves two circuits from one room unit, with programs per circuit;
"#L" is the central control function, whose heating regulation is inactive, unlikely since
batch B changed the flow setpoint of circuit 2 through `fs2`). If item 3 shows
that a slot changed on the display of `fs2` is read back over the bus, `fs2` stores programs
and refuses only the bus write.

## Date

2026-11-19.
