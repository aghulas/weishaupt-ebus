# Comparison with the vendor service tool

How to use the vendor service tool as a source of evidence (rule 3 of `AGENTS.md`) without ever
writing to the heating system (rule 7).

## Setup

- Service tool: WCM-Diagnose 5.5.19a, on a Windows PC, connected to the same eBUS through its own
  adapter. It sends with source address `ff`.
- ebusd listens on the same bus as master `31` (slave `36`) and records every telegram
  (`grab result all`), whoever sent it.
- Two seats work together:
  - **PC seat**: at the service tool. Opens screens, notes what is displayed.
  - **Bus seat**: at ebusd. Takes a snapshot of the grabbed telegrams before and after each screen.
- Shared notes: branch `service-tool` of this repository, file `evidence/service-tool-log.md`.

## Addresses

| Participant | Master | Slave |
|---|---|---|
| ebusd | `31` | `36` |
| Service tool | `ff` | `04` |

The two do not share an address, so nothing has to be changed on the adapter or in ebusd.

One overlap remains: setting writes (`5023`) are sent with source `ff`, because the devices accept
most settings only from that address (`docs/discoveries.md`, 2026-10-30). Two senders using `ff` at
the same moment cannot be separated by arbitration. **While the service tool is connected, nothing
else may send as `ff`**: no setting write through ebusd, no automation that writes settings.
Reads and polling from `31` can continue.

## Safety rules

The service tool can change parameters. During a comparison session:

1. Only display screens: info values, parameter lists as shown, fault history, counters.
2. Never change a value, never confirm a transfer to the device, never reset anything (fault
   history, service counter, burner totals, factory settings).
3. Any dialog that asks for a confirmation is left to the operator of the installation.
4. One screen at a time, and the tool is disconnected from the bus at the end of the session.

## Phase 1 — without the bus

Inspect the installation folder of the service tool on the PC: parameter tables, description
files, logs, language files. Look for register addresses, names, units, factors and value lists.

Record findings only (file name, structure, the fact established). No vendor file is copied into
this repository or into a fork (`evidence/README.md`).

## Phase 2 — screen by screen

For each screen:

1. Bus seat: snapshot of the grabbed telegrams.
2. PC seat: open exactly one screen, wait until all values are displayed, note the time.
3. PC seat: write down every label, value and unit shown, in the log.
4. Bus seat: second snapshot. The new telegrams with `QQ=ff` are what the screen reads.
5. Match each displayed value to a telegram (ID, answer bytes), deduce codec and factor.

A value that is matched this way, and read back from ebusd with the same result, is evidence for a
definition. A value seen only on the screen is a hint, not evidence.

## Log entry

```
### <date> <time> — <screen name as displayed>
Device: <type, software version from the bus scan>
| Label on screen | Value | Unit | Telegram (QQ ZZ PBSB data / answer) | Codec deduced |
|---|---|---|---|---|
Not matched: <labels with no telegram, telegrams with no label>
```

Nothing site-specific in the log: no names, host names, serial numbers.

## What to look at first

| Order | Question | Lot |
|---|---|---|
| 1 | Boiler operating hours and burner hours: how the tool reads them from EEPROM (`50 00`), address bytes and length (1 byte or 3 bytes). | D |
| 2 | Burner totals (starts, operating hours) that answer `0x8000` on firmware 11.0e: does the tool show them, and from where. | E |
| 3 | `ChangeOverTime`, `FloorDryingTemp`, `RoomThermostatTemp`: displayed value against the 16-bit register. | A |
| 4 | Fault history and fault counters: labels and code texts against the registers already read. | E |
| 5 | Info value list: any value shown by the tool that has no definition yet. | later lot |
