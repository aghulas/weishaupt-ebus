# Programs of room unit 2: wording for 0.5.15

**Superseded 2026-11-20.** Done on the lots, locally, for heating program 1 only (the program a
write proved shared): comments on lot H, French on lot L, `shared_with` on lot M (the shape the
companion asked for: on each slot, `<circuit>/<name>`, no `write`), contract and check in this
repository. Heating programs 2 and 3, hot water, circulation and the two setpoints stay without
marker until the checks of `evidence/room-units-shared-store.md` ("Not established"). The text
below is the proposal as it was.

Evidence: [evidence/room-units-shared-store.md](../evidence/room-units-shared-store.md). On the
test installation `75` answers its weekly programs from the store of `35`: a slot written to
`35` is read at `75` within 3 s, a program write to `75` is acknowledged and not kept. The setback
and frost-protection room setpoints are shared the same way (a write to either address is kept
and read at both); heating curve, flow maximum and circuit type are not.

What does not change: no ID, no name, no field, no write. The programs of `fs2` already have
no `write` in the metadata (read only since lot H); this adds the reason and where to edit
them. **No branch changes before the owner approves the wording below**: it adds 105 English
comments and their French strings, and one metadata key.

One limit runs through all of it: the sharing is seen on one installation, where one room unit
seems to run circuits 1 and 2. On an installation where `75` is a room unit of its own, its
programs are presumably its own. The wording therefore says "seen", and the companion checks
before it points to `fs1` (see 3).

## 1. Comments of `75.w.fs2` (lot H; French in lot L)

The 105 program messages of `src/wolf/75.w.fs2.tsp`. Today their comments equal those of
`fs1` and `fs3` (`heating program 1, Monday slot 1`). Proposed: the same text plus one clause.

| program | English (one example per pattern) | French |
|---|---|---|
| heating 1–3 | `heating program 1, Monday slot 1, read only: seen to be the slot of room unit 1, edited on 35.w.fs1` | `programme de chauffe 1, lundi, plage horaire 1, en lecture seule : vue comme la plage de la commande à distance 1, à modifier sur 35.w.fs1` |
| hot water | `hot-water program stored in the room unit, Monday slot 1, read only: seen to be the slot of room unit 1, edited on 35.w.fs1` | `programme ECS enregistré dans la commande à distance, lundi, plage horaire 1, en lecture seule : vue comme la plage de la commande à distance 1, à modifier sur 35.w.fs1` |
| circulation | `circulation program stored in the room unit, Monday slot 1, read only: seen to be the slot of room unit 1, edited on 35.w.fs1` | same pattern, `programme de circulation ECS enregistré …` |

The section comment above the programs (not in the CSV) becomes: "Weekly programs, read only.
On the test installation this address answers them from the store of room unit 1 (`35`): a
slot written to `35` is read here within seconds, a slot written here is acknowledged and not
kept (evidence room-units-shared-store). Edit them on `35.w.fs1`."

A lighter alternative, if 105 longer comments are not wanted in the CSV: leave the message
comments as they are, change only the section comment, and carry the pointer in the metadata
alone (2). The CSV user then sees no reason why the messages have no write line.

Heating programs 2 and 3, hot water and circulation: the sharing is shown by a write on
heating program 1 only; for the other four it rests on 105 equal slots and the same register
scheme, as the family rule of 2026-11-18 extends one proven slot to its program. Applying it
across the five programs is the owner's call; the comment wording does not change either way.

## 2. Metadata (lot M) and contract

One new key, no new label:

```toml
# Room unit 2 answers its programs from the store of room unit 1 on the test installation
# (a slot written to 35 is read at 75; a slot written to 75 is not kept): read only here.
[[entry]]
circuits = ["fs2"]
pattern = "HCProgram(?P<p>[1-3])(?P<day>Mon|Tue|Wed|Thu|Fri|Sat|Sun)(?P<slot>[1-3])"
...                                  # unchanged
evidence = ["room-units-programs", "room-units-shared-store"]
shared_with = "fs1"
```

the same on the `fs2` entries of the hot-water and circulation programs, and on the `fs2`
entries of `RoomSetbackTemp` and `RoomFrostProtectionTemp` (which keep their `write`).

Contract, `docs/companion-contract.md`, new row under the keys of a message (from 0.5.15):

> `shared_with` — a circuit of the same file family whose message of the same name was seen
> answering from the same store, on the installation of the evidence: a write to one is read at
> the other within seconds. On a message without `write`, it is where the value is edited. Seen
> on one installation; a consumer should confirm it (equal values) before relying on it.

`scripts/metadata.py`: accept the key, check that the named circuit has a message of the same
name, and pass it to the JSON unchanged. Version: an added key and comments, third number
(0.5.15).

## 3. What the companion does with it

- The programs of room unit 2 are shown read only (already the case: no `write`), with a line
  "Edited on room unit 1" (its own string, the companion's) linking to room unit 1's program
  of the same group.
- Before showing that pointer, it compares the slots of `fs2` with those of `fs1` (reads only,
  values it polls anyway). Equal: show the pointer. Different: show the programs read only
  without the pointer; on that installation `75` is presumably a room unit of its own, and its
  programs have no write in this release.
- After a write of a program slot, `RoomSetbackTemp` or `RoomFrostProtectionTemp` on `fs1`
  (or of the two setpoints on `fs2`), it refreshes the same message on the other circuit: the
  value changes there too.
- It never offers a program write on `fs2`: acknowledged by the device, not kept, and the user
  would believe it was.

## Date

2026-11-19.
