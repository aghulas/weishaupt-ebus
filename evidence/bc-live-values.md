# bc1, bc2 — live values of the boiler automat (read)

## What

Live values of the WTC boiler automat, read from its RAM and XRAM with the memory read
`PBSB 50 00`, in `src/wolf/08.w.bc1.tsp` (target `08`), `src/wolf/18.w.bc2.tsp` (target `18`) and
the shared models `Temperatures` and `Operation` of `src/wolf/wtc_inc.tsp`.

| message | ID | items | answer after the status byte |
|---|---|---|---|
| Temperatures | `40 11 62 01 68 01 6c` | RAM `62` (2 bytes), RAM `68`, RAM `6c` | 4 bytes |
| Operation | `d1 03 b2 03 d5 01 ed` | XRAM `b2`, XRAM `d5`, RAM `ed` | 3 bytes |

| Message | Byte | Field | Memory | Codec |
|---|---|---|---|---|
| Temperatures | 0 | ReturnTemp | RAM `0x62` | SCH, °C |
| Temperatures | 1 | FlueGasTemp | RAM `0x63` | SCH, °C |
| Temperatures | 2 | SupplyTemp (boiler flow) | RAM `0x68` | SCH, °C |
| Temperatures | 3 | OutsideTemp | RAM `0x6c` | SCH, °C |
| Operation | 0 | Load | XRAM `0xf0b2` | UCH, % |
| Operation | 1 | Ionisation | XRAM `0xf0d5` | UCH, divisor 10 |
| Operation | 2 | PumpSpeed | RAM `0xed` | UCH, % |

A temperature reads -40 when its sensor is not fitted.

## How it was established

**Addresses, lengths, factors.** The data logger of the vendor service tool (WCM-Diagnose
5.5.19a) reads these bytes; its channel table gives, for each one, a signed or unsigned byte and
a gain, and the symbol table of this firmware gives the address (`service-tool-log.md`,
"data logger channels"): return, flue gas, flow and outdoor are signed bytes with gain 1, the
modulation degree and the pump PWM unsigned bytes with gain 1, the ionisation an unsigned byte
with gain 0.1.

**ID format.** As for the fault history ([bc-fault-history.md](bc-fault-history.md)): CRC-8,
then items `<code> <address>`. The low nibble of the code is the memory area, `1` for RAM and
`3` for XRAM; an XRAM item carries the low byte of the address only. The tool's own logger
request holds the items of `Temperatures`, in the same order:

```
ff 08 5000 a8 01 27 11 62 01 68 01 6a 01 6c / ad | 40 3d | 41 | d8 | 0c
```

Its chart showed at that moment return about 64 °C (`40`), flue gas 63 falling to 61 °C (`3d`,
later `3b`), flow about 65 °C (`41`) and outdoor about 12 °C (`0c`). The tool read the items
of `Operation` as `03 b2` (answer `17` = 23 %, burner off, the minimum rating), `03 d5`
(`00`, burner off) and `01 ed` (`00`, pump channel selected alone).

The CRC routine of [register-crc.md](register-crc.md) reproduces the first byte of 14 captured
`50 00` requests, among them the tool's four logger requests and the seven single reads below.
It gives `40` and `d1` for the two IDs of this lot.

**Read through ebusd.** The running configuration reads each of the seven bytes with a
single-item request (source `31`). Two passes two minutes apart on 2026-11-17, first boiler
firing at its minimum load, second boiler idle; answers after the status byte `00`:

| Request | Address | First boiler `08` | Second boiler `18` |
|---|---|---|---|
| `3e 01 62` | RAM `62` | `35`, `34` = 53, 52 °C | `35`, `35` = 53 °C |
| `3f 01 63` | RAM `63` | `35`, `35` = 53 °C | `31`, `30` = 49, 48 °C |
| `34 01 68` | RAM `68` | `39`, `39` = 57 °C | `34`, `34` = 52 °C |
| `30 01 6c` | RAM `6c` | `0f`, `0f` = 15 °C | `d8`, `d8` = -40 |
| `56 03 b2` | XRAM `b2` | `19`, `19` = 25 % | `00`, `00` |
| `31 03 d5` | XRAM `d5` | `7f`, `79` = 12.7, 12.1 | `00`, `00` |
| `b1 01 ed` | RAM `ed` | `33`, `33` = 51 % | `00`, `00` |

**Compared with the status telegrams** each boiler sent in the same minute
([bc1-boiler-status.md](bc1-boiler-status.md)):

```
03 10 500a : 01 06 7f 62 19 72 ff ff 00 0f b3 0c ff      03 10 0504 : 19 17 64
13 10 500a : 01 00 07 00 00 68 ff ff 00 80 00 00 08
```

| Field | First boiler: memory / status | Second boiler: memory / status |
|---|---|---|
| SupplyTemp | 57 / `72` = 57.0 °C | 52 / `68` = 52.0 °C |
| OutsideTemp | 15 / `00 0f` = 15.0 °C | -40 / `00 80` = not available |
| Load | 25 / `19` = 25 % (also `WTCPower` `19`) | 0 / `00` = 0 % |
| Ionisation | 12.7, 12.1 / flame on, phase `06` | 0.0 / flame off, phase `00` |
| PumpSpeed | 51 / pump on | 0 / pump off |
| ReturnTemp | 53, 52: below the flow while firing | 53 |
| FlueGasTemp | 53 | 49, 48: cooling down |

- Flow, outside temperature and load equal an independent figure on both boilers, in two
  different states.
- Sign: the second boiler has no outside sensor. Its status telegram says not available and
  its RAM byte is `d8`, -40 as a signed byte, the same value the tool's logger read for the
  two sensors not fitted on the first boiler (`service-tool-log.md`, session 2).
- The status telegram carries `ff` for the flue gas temperature and no return temperature, so
  these two rest on the tool's chart and on their behaviour.
- Ionisation is on the scale of the fault history, where the slots written with the burner in
  operation hold 14.1 to 19.8 and the others 0.0.

**The two requests as written**, sent on 2026-11-17 from `31` with the `hex` command of ebusd
(read-only, `50 00`), to both boilers; answers after the length byte, status byte first:

| Time | Boiler | `40 11 62 01 68 01 6c` | `d1 03 b2 03 d5 01 ed` | State |
|---|---|---|---|---|
| 15:50 | `08` | `00 3c 34 3f 0f` = 60, 52, 63, 15 °C | `00 00 00 00` | burner off, pump off |
| 15:50 | `18` | `00 41 38 42 d8` = 65, 56, 66, -40 | `00 1c 00 32` = 28 %, 0.0, 50 % | pump just started |
| 15:50 | `18` | `00 31 39 3c d8` = 49, 57, 60, -40 | `00 17 00 32` = 23 %, 0.0, 50 % | 20 s later |
| 15:50 | `18` | `00 3b 39 38 d8` = 59, 57, 56, -40 | `00 28 00 32` = 40 %, 0.0, 50 % | no flame yet |
| 15:51 | `18` | `00 38 39 3c d8` = 56, 57, 60, -40 | `00 22 5a 39` = 34 %, 9.0, 57 % | flame on |
| 15:51 | `18` | `00 37 39 3c d8` | `00 19 53 33` = 25 %, 8.3, 51 % | firing |
| 15:52 | `18` | `00 38 39 3c d8` | `00 19 5f 33` = 25 %, 9.5, 51 % | firing |

- Both boilers answer the two multi-item requests with one status byte and as many bytes as
  the model has fields (4 and 3). One request out of 18 failed with a bus error ("wrong symbol
  received") and succeeded when repeated.
- Status telegrams of the same minutes: first boiler `01 00 07 00 00 7e ff ff 00 0f …` (flow
  `7e` = 63.0 °C, outside `00 0f` = 15.0 °C, load 0 %); second boiler firing
  `01 06 7f 62 19 78 ff ff 00 80 …` (load `19` = 25 %, flow `78` = 60.0 °C, outside not
  available). Flow, outside temperature and load of the grouped answers equal them.
- A single-item read of RAM `ed` sent right after each `Operation` request to the second
  boiler gave `32`, `39`, `32`, `33`, `33` against `32`, `39`, `33`, `33`, `33` in the grouped
  answers: the last field is the pump byte.
- The second boiler was seen through a start: ionisation `00` without flame, 8.3 to 9.5 with
  it; pump 0 before, 50 % and more after.

Toolchain: `scripts/check.sh` clean (hygiene, format, compile, `ebusd --checkconfig`, 164
messages).

## Equipment

Two WTC condensing boilers in cascade, automat scanned `MF=Kromschroeder;SW=1104;HW=0501`
(firmware shown by the tool as 11.0e). The first boiler carries the outside sensor.

## Date

2026-11-16 (service tool), 2026-11-17 (reads through ebusd, single-item then grouped).

## Not verified

- `Load` before the flame. During the start of the second boiler (pump on, no flame yet) XRAM
  `b2` read 23 to 40 while the status telegram said 0 %; once firing both said 25 %. The byte
  seems to hold the load the automat prepares, not only the load of a burning flame. One start
  observed, not examined further.
- `ReturnTemp` and `FlueGasTemp` against a displayed figure other than the tool's chart, read
  off its curves.
- `PumpSpeed` and `Ionisation` against a displayed figure. Their evidence is the tool's channel
  table, zero with pump and flame off, and a plausible value with them on. The unit of the
  ionisation signal is not known.
- Temperatures below 0 °C: signed is taken from the tool's channel table and from the -40
  answer of a missing sensor.
- Other firmware versions of the automat: the addresses come from this one.

## Left out

Channels of the same data logger that did not reach this standard:

| Channel | Memory | Why |
|---|---|---|
| Sup./Mod setpoint | RAM `6e` | Read 2 and 0, the modulation demand of the cascade manager (`05 07`, 2.0 % and 0 %). Its unit depends on the control mode; no flow setpoint in °C was seen. |
| DHW setpoint | RAM `6f` | 50 on both boilers, equal to the demand telegram, one value only. |
| DHW actual B3, de-couple B11 | RAM `6a`, XRAM `7c` | Sensors not fitted on either boiler: -40 only. |
| Sup. act. (eSTB) | RAM `5e` | Reads 1 to 2 K above the flow; no independent figure. |
| Speed set, speed actual, PWM fan | XRAM `de`, RAM `77`, RAM `7e` | 23, 23 and 27 while firing, 0 when idle. Unit of the speed not known, nothing to compare with. |
| 0-10 V input | XRAM `77` | `ff` on both boilers, input not used. |
| Lockout code | RAM `65` | 0 only. |
| Inputs (GPS, APS, WPS, H1, H2) | RAM `27` | `dd` and `ad`; no state to compare with. |
| Outputs (ignition, valves, pump, relays) | RAM `2b` | `fd` firing, `80` idle. Valves and pump agree with the status telegram, but all three change together, so the bus does not tell the bits apart; ignition and the relays were not compared with anything. |

The operating phase has no channel in the data logger. RAM `70` reads 13 while firing and 32
when idle, which is not the phase of the status telegram (6 and 0).
