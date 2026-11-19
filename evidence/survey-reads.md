# Reads established by the register survey and the service tool (lot O)

## What

Lot O, branch `weishaupt-O` of the ebusd-configuration fork (on lot N, below the translation and
metadata lots), reads only, stock ebusd (`50 22`, the checksum of the address precomputed in the
ID, [register-crc.md](register-crc.md)): fifteen registers of the system manager in
`src/wolf/15.w.ka.tsp`, three registers of each room unit as shared models in `wtc_inc.tsp`, used
in `35.w.fs1`, `75.w.fs2`, `f5.w.fs3`. The names were approved by the owner on 2026-11-19 from the
list in [register-survey-findings.md](register-survey-findings.md), "Ready for a lot", with one
change below (parameter 538).

## Sources

Each register has two independent sources:

1. the vendor service tool's screen of 2026-11-19, 19:03–19:15, with label, unit and value
   ([service-tool-ui-exploration.md](service-tool-ui-exploration.md)), and
2. a read by ebusd from its own address `31` in the register survey of the same evening
   ([register-survey-plan.md](register-survey-plan.md), results kept as installation data),
   with the same value; or, for the B24 sensor, the survey and an earlier record that used its
   value ([heat-demand.md](heat-demand.md)); for two room-unit registers, earlier reads.

The survey read four registers per telegram on the system manager and the room units; the
request column below gives the single-register ID the definition uses, and the answer column the
two bytes this register answered in the survey (or in the tool's own request, where named).

## System manager `15`

| Message | Register | Request (ID) | Answer | Decoded | Tool's screen |
|---|---|---|---|---|---|
| `ModulationDiffTemp` | `e9 fd` | `4d e9 fd` | `64 00` | 10.0 | P538 continuous temperature, 10,0 (manual: modulation differential, 5.0–20.0 K) |
| `DeCoupleExcessTemp` | `e8 fd` | `11 e8 fd` | `3c 00` | 6.0 | P551 de-couple excess, 6,0 K |
| `DeCoupleMaxTemp` | `e6 fd` | `dd e6 fd` | `0c 03` | 78.0 | P553 de-couple maximum, 78,0 °C |
| `CalorifierExcessTemp` | `e3 fd` | `ad e3 fd` | `0a 00` | 1.0 | P561 calorifier excess, 1,0 K |
| `SummerTimeStartDay` | `de fd` | `09 de fd` | `1d 00` | 29 | P593 start of summer time, 29 March |
| `SummerTimeStartMonth` | `df fd` | `55 df fd` | `03 00` | March | (same field) |
| `SummerTimeEndDay` | `e0 fd` | `49 e0 fd` | `19 00` | 25 | P594 end of summer time, 25 October |
| `SummerTimeEndMonth` | `e1 fd` | `15 e1 fd` | `0a 00` | October | (same field) |
| `BoilerSequence1First` | `ca fd` | `95 ca fd` | `00 00` | A | P533 boiler sequence 1, a b |
| `BoilerSequence1Second` | `cb fd` | `c9 cb fd` | `01 00` | B | (same field) |
| `BoilerSequence2First` | `d4 fd` | `e9 d4 fd` | `01 00` | B | P534 boiler sequence 2, b a |
| `BoilerSequence2Second` | `d5 fd` | `b5 d5 fd` | `00 00` | A | (same field) |
| `DHWSetbackTemp` | `8a 02` | `12 8a 02` | `50 00` | 8.0 | P573 DHW reduced setpoint, 8,0 °C |
| `LegionellaStartTime` | `f4 fd` | `d5 f4 fd` | `22 00` | 34 | P581 legionella time, 08:30 |
| `PlateExchangerPrimaryTemp` | `40 0a` | `72 40 0a` | `51 02` | 59.3 | sensor B24, 60,3 °C at 19:11 (a live value) |

**Parameter 538.** The tool's English screen labels `e9 fd` "continuous temperature", 10,0 °C.
The manual of the WCM-KA 3.0 (document 83258404, pages 87 and 88) describes parameter 538 as the
modulation differential: added to the system setpoint it gives the modulation limit
temperature, set in kelvin from 5.0 to 20.0 K. The vendor-software catalogue gives the same
register as parameter 538 "shut-down differential", K, 5–20, and as parameter 318, a shut-down
temperature in °C, in another configuration of the tool. On this cascade the manual decides:
the message is `ModulationDiffTemp`, type `diff10` (K), not the proposed `ContinuousTemp` in °C.
Its value, 10.0 K, is also the differential the heat-demand telegrams imply
([heat-demand.md](heat-demand.md)).

`DeCoupleMaxTemp` stays read only: a write of 78.5 was acknowledged and not taken
(`docs/discoveries.md`); the tool's catalogue sets this parameter from 8 to 78 °C, which
explains it. The four boiler-sequence registers stay read only (batch C not done, owner's
decision of 2026-11-18). `0` is boiler A and `1` boiler B (the tool shows "a, b" for sequence 1,
reading 0 and 1, and "b, a" for sequence 2, reading 1 and 0).

## Room units `35`, `75`, `f5`

| Message | Register | Request (ID) | Unit: answer, decoded | Source of the answer | Tool's screen |
|---|---|---|---|---|---|
| `RoomSetpointTemp` | `12 00` | `08 12 00` | `35`: `50 00` = 8.0 | survey | room setpoint 8,0 °C on `35` |
| `RoomSetpointTemp` | `12 00` | `08 12 00` | `f5`: `8c 00` = 14.0 | tool's request | room setpoint 14,0 °C on `f5`, its setback setpoint |
| `OutsideMixedTemp` | `1a 0a` | `5a 1a 0a` | `35`: `70 00` = 11.2 | tool's request | outside temperature, mixed, 11,2 °C on `35` and `f5` |
| `HeatingCircuitType` | `73 09` | `19 73 09` | `35`: `02 00` = Radiator60 | tool's request; read 2 before | radiator 60 °C |
| `HeatingCircuitType` | `73 09` | `19 73 09` | `75`: `03 00` = Radiator70 | tool's request; read 3 before | radiator 75 °C |
| `HeatingCircuitType` | `73 09` | `19 73 09` | `f5`: `03 00` = Radiator70 | tool's request; read 3 before | radiator 75 °C |

The second source of `OutsideMixedTemp` is the read of 2026-11-17 on the three room units
(`5a 1a 0a`, `92 00` = 14.6, [room-units-reads.md](room-units-reads.md)); of `HeatingCircuitType`,
the reads 2 / 3 / 3 of the batch-C preparation ([choice-date-program-writes.md](choice-date-program-writes.md)).
The circuit-type list follows the order of the room unit's manual (83277504, page 48: floor
base heating, underfloor heating, radiators 60, radiators 70, convectors, universal), which the
vendor-software catalogue gives with the same indices; only 2 and 3 were read. The tool names
type 3 "radiator 75 °C", the manual "radiators 70" with a factory flow setpoint of 75 °C; the
value name follows the manual. The circuit type stays read only. `OutsideMixedTemp` and the B24
sensor answer -100.0 when the sensor or value is not available (the tool shows "--").

## Second group (approved by the owner on 2026-11-19)

Lot O, two more commits: the room units' version, stored hot-water settings and fault log, and
the heating modules' mixer parameter and version. Read only, shared models in `wtc_inc.tsp`.
Answers from the register survey (pass 1, `35` and `51`); `75`, `f5` and `52` are read in pass 2.

| Unit | Message | Register | Request (ID) | Answer, decoded | Second source |
|---|---|---|---|---|---|
| `35` | `VersionMajor`, `VersionMinor` | `99 01`, `9a 01` | `45 99 01`, `a1 9a 01` | `47 01` = 327, `1a 00` = 26 | the scan (`SW=2726`) and the tool's version 327.26 |
| `35` | `DHWLoadingPriority` | `23 00` | `d8 23 00` | `02 00` = Parallel | the tool's screen: P343 "parallel", reading 2, on `35` and `75` |
| `35` | `DHWSetbackTemp` | `8a 02` | `12 8a 02` | `90 01` = 40.0 | room unit manual 83277504, P133 factory 40 °C (p. 32) |
| `35` | `DHWMaxTemp` | `81 01` | `ad 81 01` | `58 02` = 60.0 | the same manual, P601 factory 60 °C (p. 39) |
| `35` | `DHWLegionellaDay` | `01 01` | `5d 01 01` | `05 00` = Friday | the same manual, P605 factory Friday (p. 39) |
| `35` | `LegionellaCirculationTime` | `b1 09` | `29 b1 09` | `b4 00` = 180 s | the same manual, P609 factory 3 min (p. 39) |
| `35` | `ErrorId` | `9a 0b` | `ab 9a 0b` | `00 00` = 0 (the most recent entry) | the tool's History tab reads these nine registers on `35`, entry by entry, and shows date, time, device and code |
| `35` | `ErrorCode` | `9b 0b` | `f7 9b 0b` | `00 00` = 0 | as above (codes 0 and 191 shown) |
| `35` | `ErrorType` | `9c 0b` | `3f 9c 0b` | `03 00` = 3 | as above |
| `35` | `ErrorDevice` | `9d 0b` | `63 9d 0b` | `00 00` = 0 (shown "KA") | as above |
| `35` | `ErrorMinute` | `9f 0b` | `db 9f 0b` | `33 00` = 51 | as above |
| `35` | `ErrorHour` | `a0 0b` | `c7 a0 0b` | `03 00` = 3 | as above |
| `35` | `ErrorDay` | `a1 0b` | `9b a1 0b` | `01 00` = 1 | as above |
| `35` | `ErrorMonth` | `a2 0b` | `7f a2 0b` | `09 00` = September | as above |
| `35` | `ErrorYear` | `a3 0b` | `23 a3 0b` | `00 00` = 0 | as above (entries dated 2000 shown) |
| `51` | `MixerParameter` | `8f 01` | `61 8f 01` | `50 00` = 8.0 K | the tool's P365 "mixer parameter" 8.0 on `51` (its own request), and the manual's P425 factory 8 K (p. 37) |
| `51` | `VersionMajor`, `VersionMinor` | `99 01`, `9a 01` | `45 99 01`, `a1 9a 01` | `74 01` = 372, `03 00` = 3 | the tool's "version of the module 372.03" (read on `52`) |

The fault log of `35` was read at 20:51, after the entry selectors that the tool had left at 9
were written back to 0 (19:53): it is entry 0. `DHWLoadingPriority`: the tool's "parallel" for 2
also settles value 2 of the system manager's list (`DHWOperation`, whose comment in lot A still
says only 0 is established; lot A is not changed here). The hot-water settings are what the room
unit stores; the system manager prepares the hot water on this installation and its values are the
ones in use.

## Equipment

A Kromschröder WCM-KA system manager (266.18) of a cascade of two WTC-GB boilers with a plate
exchanger, three WCM-FS room units (327.26), two WCM-EM heating modules (372.03).

## Date

2026-11-19.

## Not verified

- A change of any of these values: all were read at their current value only.
- The circuit types 0, 1, 4, 5; the summer-time registers on the room units (read by the tool,
  `25 / 3`, `25 / 10` on `35`, not yet by the survey; not defined there).
- `RoomSetpointTemp` while a unit is in normal operation (its normal setpoint expected).
