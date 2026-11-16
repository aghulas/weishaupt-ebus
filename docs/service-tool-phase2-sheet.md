# Service tool comparison — phase 2 session sheet

Run sheet for one session, following `docs/service-tool-protocol.md`. Read-only towards the
heating system (rule 7 of `AGENTS.md`). Findings go to `evidence/service-tool-log.md`.

## Seats

| Seat | Who | Does |
|---|---|---|
| PC | someone at the PC running the service tool | opens one screen at a time, reads values out, never changes anything |
| Bus | someone with access to ebusd | snapshots grabbed telegrams before and after each screen, matches them |
| Operator | the operator of the installation, reachable | answers any dialog that asks for a confirmation (the PC seat does not) |

## Before connecting the tool

1. **No other sender as `ff`.** Switch off every integration or automation that writes settings
   (`50 23`) with source `ff`, and check that it is really off (its own switch or log). Reads and
   polling from `31`, and the time broadcast `fe 07 00`, may continue.
2. Bus seat: check that ebusd grabs all telegrams (`grab result all` answers), and note the bus
   participants seen. Both boilers must be on (automats `08` and `18` present), otherwise their
   screens time out.
3. Bus seat: baseline snapshot, kept as `S0`.
4. PC seat: note the tool's version and the device versions it displays. No serial numbers in
   the log.
5. Connect the tool. Bus seat: snapshot `S1`. Telegrams with `QQ=ff` between `S0` and `S1` are
   the tool's own scan, kept as is.

## Per screen

1. Bus seat: snapshot `Sa`. Say "go".
2. PC seat: open exactly one screen, wait until every value is displayed, note the time.
3. PC seat: read out every label, value and unit. Take a screenshot if possible.
4. Bus seat: snapshot `Sb`. New telegrams with `QQ=ff` between `Sa` and `Sb` are what the
   screen reads.
5. Leave the screen without saving. If a dialog appears, stop and call the operator.

## Screens, in this order

### 1. Info values of the system manager (KA) — lot A open points

Goal: settle the sign of registers 3, 13, 14 and the meaning of register 13 before #717 is
reviewed. If the tool reads them, the requests should look like `ff 15 50 22 03 <ID>`:

| Register | Expected ID | Lot A name | Question |
|---|---|---|---|
| 2 | `b8 02 00` | `HeatDemandTemp` | cross-check only |
| 3 | `e4 03 00` | `DHWSetValue` | signed? |
| 12 | `74 0c 00` | `OutsideTemp` | cross-check only (signed, known) |
| 13 | `28 0d 00` | `SupplyWTCTemp` | signed? label on screen: boiler flow, or separator / exchanger B22? |
| 14 | `cc 0e 00` | `DHWTemp` | signed? |
| 44 | `48 2c 00` | `ModulationStatus` | cross-check only |
| 2572 | `7e 0c 0a` | `OutsideWeightedTemp` | cross-check only |

The sign is proven only by a negative value, or by an answer above `0x7fff`. Otherwise record
the label and the value, and leave the sign as an assumption.

### 2. Boiler counters (WTC, bc1 then bc2) — lot D, protocol question 1

Goal: the request the tool sends for operating hours and burner hours. Look for
`ff 08 50 00 <len> <ID>` (bc1) and `ff 18 50 00 …` (bc2).

Candidates computed with the same CRC routine as the `50 22` reads. The routine reproduces the
IDs already in the fork, for example `d2 06 01 02 e6`:

| Symbol (`WH11928`) | 1-byte read (deployed) | Multi-byte read (fork's `WH11928.tsp`) |
|---|---|---|
| `EEA_H_PON` `0x01E6` | `d2 06 01 02 e6` | 3 bytes: `ee 06 01 22 e6` |
| `EEA_H_BON` `0x01E9` | `dd 06 01 02 e9` | 2 bytes: `6d 06 01 12 e9` |
| `EEA_N_PON` `0x01DA` | — | 3 bytes: `d2 06 01 22 da` |
| `EEA_N_ZUE` `0x01EB` | — | 3 bytes: `e3 06 01 22 eb` |

To record for each request: the exact ID bytes, the answer length and bytes, and the value on
screen. Byte order and length follow from matching the answer to the displayed value.
Firmware 11.0e answers `0x8000` on the `50 22` burner totals: note whether the tool shows them
at all, and from which request.

### 3. Fault history and counters (WTC) — lot E

Goal: code texts and labels against the registers already read
(`evidence/em1-fault-log.md`), and the requests used for the history slots.

### 4. If time allows — `ChangeOverTime`, `FloorDryingTemp`, `RoomThermostatTemp`

Goal: displayed value against the 16-bit register (lot A, known gap 7 of #717).

## After the session

1. Disconnect the tool. Bus seat: snapshot `S9`; no more `QQ=ff` telegrams.
2. Switch the integrations from step 1 back on, and check that they work.
3. Write one log entry per screen in `evidence/service-tool-log.md` (format in the protocol).
   Nothing site-specific.
4. A value matched to a telegram and read back by ebusd with the same result is evidence: open
   or update the evidence record, then the definition, then run `scripts/check.sh`.
