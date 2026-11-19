# Service tool — exploration of the user interface

Date: 2026-11-19, 19:01–19:22 (clock of the service PC; the bus snapshots carry the same time
within a few seconds).

What: the screens of WCM-Diagnose 5.5.19a that `evidence/service-tool-log.md` had not covered
(room units, heating modules, parameter tabs of the cascade manager, the developer window of the
second build), read from the screen and matched with the telegrams the tool sent.

Method: `docs/service-tool-protocol.md`, phase 2. The tool was driven through a remote-desktop
window on the service PC. After each screen, a snapshot of the telegrams grabbed by ebusd was
taken; the new telegrams with source `ff` are what the screen read. Labels are given in my own
words with the parameter number the tool prints. No vendor file, screenshot or text was copied.

Telegrams are `ZZ PBSB data / answer`. For `09 02` the data is `<register lo> <register hi> 02`
and the answer is `02 <lo> <hi>`; "register N" is the 16-bit number, as in `DL.Ini`.
"Defined" refers to the fork's branch `weishaupt-next` at `fbc46f1`.

## Summary

- The second build of the program (file name ending in `b`) has one more menu, `Development`,
  and a tool bar. Its boiler window shows the parameter list that stayed empty in the first build.
- The bus scan lists six devices. The tool never addresses `50`. It reaches room unit `75` and the
  heating modules `51` and `52` only through the windows of the room units `35` and `f5`.
- Room units, heating modules and cascade manager are read with `09 02`, one register per
  telegram, no CRC byte. 76 register numbers read this way have no definition in the fork yet
  (last table).
- **The fault history tab of a room unit writes.** The tool sends `09 03 9a 0b <n> 00` (register
  2970, entry number 0–9) to select each entry before reading it. See "History".
- The developer window names the boiler EEPROM bytes `0x02`–`0x18` and `0x1b`–`0x51` one by one
  and displays the counters with their sizes. All displayed values equal the bytes on the bus.
  This gives the displayed figure for burner starts and mains-on that lot D was missing.
- No parameter was changed and no reset was used. The only writes are the selector writes of the
  history tabs. The tool was left disconnected.

## Program and connection

| Item | Observed |
|---|---|
| Builds | Two executables. First: menus File, Window, Extras, Info. Second: the same plus `Development` and a tool bar with three icons. |
| Title | "User version"; "Offline-Mode" is appended while not connected. |
| Connection | Extras, Options, Interface, entry for the vendor interface: direct connection, serial port 3, PC bus address `ff` (address `00` greyed). After connecting the dialog shows interface version 156.24. |
| Extras | Bus scan (F3, greyed offline), Terminal, Datalogger (F4), Extra access (greyed), System time (not opened), Options (Interface, Language, Password). |
| File, Open | EndUser, Service, Manufacturer, Statistics, FaultHistory, Protocol, Io-Parameter, Graphic, KA, FB/EM, SOL. |
| Development (second build) | Variables, Test data, EEPROM, CM controller, eBus-Trigger, BCC, Analyse BCC, Sim FS (sub-menu). |

Both builds show an error box of the program itself when a boiler window opens (access
violation), and the second one another when the "End user" tab opens (empty string is not an
integer). They were dismissed; they do not concern the bus.

## 19:02:36–19:02:47 — bus scan

The tool sends one `07 04` to `f6`, `08`, `18`, `f5`, `35`, `15`, in that order of display. It does
not query `50`, `51`, `52`, `75`.

| Entry in the tree | Address | Answer to `07 04` | Window title |
|---|---|---|---|
| `KA-WST` | `f6` | `50 57 01 00 41 20 66 18 ff 01` | System heat control |
| `WCM-CPU-R5#A WTC 250` | `08` | `50 57 fa 00 19 33 11 04 05 01` | `... WTC 250 HA 11.0e` |
| `WCM-CPU-R5#B WTC 250` | `18` | `50 57 fa 00 19 13 11 04 05 01` | `... WTC 250 H 11.0e` |
| `FS#1+2` | `35` | `50 57 02 00 18 00 27 26 ff ff` | `FS#1+2 327.26` |
| `FS#3 EM-HZ#3` | `f5` | `50 57 02 00 08 00 27 26 ff ff` | `FS#3 EM-HZ#3 327.26` |
| `KA` | `15` | `50 57 01 00 41 20 66 18 ff 01` | `KA 266.18` |

- `f6` and `15` give the same identification: two addresses of the cascade manager.
- Which address belongs to which room-unit entry is established by the telegrams each window
  sent, not by the order of the scan.
- The two room units differ in one identification byte (`18` against `08`). The first one is shown
  as serving circuits 1 and 2, the second as serving circuit 3 with a heating module.

## Room unit `35`, window `FS#1+2`

Tabs: Process values, User, Engineer HC, Engineer HC2, Heating 1, Heating 2, Heating 3,
Configuration, History. The parameter tabs have `Read` and `Write` buttons, the User tab also
`Load` and `Save`; none was used. Each tab reads its registers when it is shown.

### 19:03:11 — Process values (target `35`)

| Label | Shown | Register | Answer | Defined |
|---|---|---|---|---|
| Error | 0 | 1 (`01 00`) | `00 00` | other circuits only |
| Current heat demand | 6,9 °C | 2 (`02 00`) | `45 00` | yes |
| DHW setpoint | -- | 3 (`03 00`) | `00 80` | other circuits only |
| Flow setpoint, heating circuit | 6,9 °C | 4 (`04 00`) | `45 00` | yes |
| Flow temperature, heat exchanger | -- | 13 (`0d 00`) | `00 80` | other circuits only |
| Room temperature | 27,4 °C | 17 (`11 00`) | `12 01` | yes |
| Room setpoint | 8,0 °C | 18 (`12 00`) | `50 00` | **no** |
| Outside temperature, mixed | 11,2 °C | 2586 (`1a 0a`) | `70 00` | **no** |
| Type of operation | "(0) Prog 1/DHW" | 274 (`12 01`) | `0b 00` | **no**; how 11 becomes the text is not established |

- **Established:** register 18 is the current room setpoint, tenths (8,0 here, 14,0 on `f5`, where
  the reduced setpoint is 14,0). Register 2586 is the mixed outside temperature, tenths, as
  `DL.Ini` says. `00 80` is displayed as "--".
- The tab is polled: the nine registers are read again every few seconds.

### 19:03:33 — User (target `35`)

| No. | Label | Shown | Register | Answer | Defined |
|---|---|---|---|---|---|
| 111 | Type of operation | (0) Prog 1 | 274 | `0b 00` | no |
| 141 | Holiday start | -- -- -- | 283, 284, 285 | 30, 10, 0 | yes |
| 141 | Holiday end | -- -- -- | 286, 287, 288 | 1, 11, 0 | yes |
| 142 | Holiday temperature level | frost protection | 317 | 0 | yes |
| 153 | Start of summer time | 25 March | 64990 (`de fd`), 64991 (`df fd`) | 25, 3 | **no** |
| 154 | End of summer time | 25 October | 64992 (`e0 fd`), 64993 (`e1 fd`) | 25, 10 | **no** |

- **Established:** registers 64990–64993 are day and month of the start and of the end of summer
  time. Same four registers on the cascade manager, where the start reads 29 March.
- The holiday dates are shown as "--" although day and month are stored: the third register of
  each date is 0.

### 19:04:04 — Engineer HC (target `35`)

17 registers read for 14 fields.

| No. | Label | Shown | Register | Answer | Defined |
|---|---|---|---|---|---|
| 316 | Heating circuit type | radiator 60 °C | 2419 (`73 09`) | 2 | **no** |
| 318 | Control variation | weather compensated … | 321 | 1 | yes (`ControlVariation`) |
| 341 | Minimum flow temperature | 8,0 °C | 299 | 80 | yes |
| 342 | Maximum flow temperature | 75,0 °C | 40 | 750 | yes |
| 343 | DHW operation | parallel | 35 (`23 00`) | 2 | other circuits only (`DHWLoadingPriority`) |
| 381 | Reducing operation | reduce | 296 or 306 | 1 | no |
| 382 | Frost protection limit | 0 | 702 | 0 | yes |
| 383 | Start optimisation, maximum | 45 min | 272 | 3 | yes (`SwitchOnRuntime`) |
| 383 | Start optimisation, actual | -- | | | |
| 385 | Type of construction | empty | | | |
| 388 | Room thermostat | empty, greyed | | | |
| 390 | Adaption | empty, greyed | | | |
| 508 | Room influence, P part | empty | | | |
| | Room influence, I part | -- | | | |

- **Established:** register 2419 is the heating circuit type: 2 on `35` (radiator 60 °C), 3 on
  `75` and on `f5` (both radiator 75 °C).
- Not assigned to a field: registers 271, 277, 298, 1710, 1711, 2417, 2588 (all `00 80`, "no
  value"), 315 (`ff ff`), and the one of 296 / 306 that is not parameter 381. They belong to the six
  fields shown empty or "--".

### 19:04:53 — Engineer HC2 (targets `75` and `51`)

The tab of the second heating circuit reads the **other room unit, `75`**, and one register of
heating module `51`. 26 registers on `75`, 1 on `51`, for 27 fields.

| No. | Label | Shown | Target, register | Answer | Defined |
|---|---|---|---|---|---|
| 317 | Heating circuit type | radiator 75 °C | `75`, 2419 | 3 | no |
| 319 | Control variation | weather compensated … | `75`, 321 | 1 | yes |
| 361 | Minimum flow temperature | 8,0 °C | `75`, 299 | 80 | yes |
| 362 | Maximum flow temperature | 75,0 °C | `75`, 40 | 750 | yes |
| 363 | DHW operation, circuit 2 | parallel | `75`, 35 | 2 | other circuits only |
| 364 | Boiler excess over mixed circuit | 2,0 K | `75`, 273 | 20 | yes (`BoilerMCBoostTemp`) |
| 365 | Mixer parameter | 8.0 | `51`, 399 (`8f 01`) | 80 | **no**; candidate, the only value left for this field |
| 370 | Delay of the boiler | 0 s | one of `75` 282, 1556, 2651 | 0 | no |
| 371 | Screed function | off | one of `75` 282, 1556, 2651 | 0 | no |
| 331 | Function of input H1 | 0, standby with frost protection | one of `75` 282, 1556, 2651 | 0 | no |
| 325 | Outside sensor correction | -- K | | | |
| 366 | Frost protection | -- °C | | | |
| 367, 368 | Minimum, maximum pump speed | -- % | | | |
| 357 | Speed variation | empty, greyed | | | |
| 389 | Room thermostat | empty, greyed | | | |
| 372 | Screed day | 0, greyed | | | |
| 482 | Screed temperature | 10,0 °C | | | |
| 483–491 | Screed programme (start temperature, days and maxima of two phases) | 25,0 / 3 / 45,0 / 4 / 4 / 3 / 55,0 / 13 / 3, greyed | | | |

- The 17 remaining registers of `75` all answer `00 80`: 298, 303, 304, 443, 444, 2204–2210, 2560,
  2578, 2588, 3103, 3105. There are 17 remaining fields. The numbers shown for 372 and 482–491
  are therefore not read from the device: they are what the tool displays when the device has
  no value. Which register is which field is not established.

### 19:05:35, 19:06:12, 19:06:47 — Heating 1, 2, 3 (target `35`)

Three weekly programmes, seven days, three switch pairs per day. 21 registers per tab:
`<day><slot> <programme>` with day 1 (Monday) to 7, slot 0 to 2, programme `14`, `15`, `16`.
Answer: off time, then on time, in quarter hours; `80 80` = unused.

| Tab | Shown (first pair) | Register, answer |
|---|---|---|
| Heating 1 | 06:30–18:00 on four days | `10 14` / `48 1a` |
| Heating 2 | 06:00–18:00 on five days, 07:00–12:00 on Saturday | `10 15` / `48 18`, `60 15` / `30 1c` |
| Heating 3 | 06:00–22:00 on five days | `10 16` / `58 18` |

All 63 answers agree with the screen. These registers are defined in the fork (weekly programmes).

### 19:07:20 — Configuration (target `35`)

| Label | Shown | Register | Answer |
|---|---|---|---|
| Version of the room unit | 327.26 | none (from the scan) | |
| P335, configuration of the room unit | internal room sensor | 16 (`10 00`) | `02 00` |

### 19:07:50 — History (target `35`)

Ten entries, each with date, time, device and error code.

For each entry the tool sends a **write**, then reads eight registers:

```
35 0903 9a 0b <n> 00 / 00          n = 0 … 9
35 0902 9b 0b 02 00 / 02 bf 00     code
35 0902 9c 0b 02 00 / 02 03 00     type
35 0902 9d 0b 02 00 / 02 00 00     device
35 0902 9f 0b 02 00 / 02 35 00     minute
35 0902 a0 0b 02 00 / 02 0e 00     hour
35 0902 a1 0b 02 00 / 02 02 00     day
35 0902 a2 0b 02 00 / 02 07 00     month
35 0902 a3 0b 02 00 / 02 1a 00     year
```

(the answers above are those of the last entry, n = 9, shown as entry 10: 2 July 2026, 14:53,
device "KA", code 191.)

- **Established:** `09 03 <register lo> <register hi> <value lo> <value hi>` is a register write.
  Register 2970 (`9a 0b`) is the entry selector of the fault log, 0 = most recent. This is the same
  register as `ErrorId` in `evidence/em1-fault-log.md`; reading the log entry by entry needs this
  write. The room units use the same `09 03` service towards their heating modules (seen from
  sources `70` and `f0` in the same snapshots).
- Device value 0 is displayed as "KA". Codes seen: 0 and 191, alternating; several entries are
  dated in the year 2000 (clock not set at the time).
- **Side effect of this session:** the selector of room unit `35` was left at 9. It was at an
  unknown value before. The other history tabs were opened later, on the owner's word (see
  "Second visit").
- The tab has a `Reset` button; it was not used.

## Room unit `f5` with heating module `52`, window `FS#3 EM-HZ#3`

Tabs: Process values, User, Engineer HC, Heating 1–3, Configuration, History. Heating 1–3 were
not opened; History: see "Second visit".

### 19:08:40 — Process values (targets `f5` and `52`)

| Label | Shown | Target, register | Answer | Defined |
|---|---|---|---|---|
| Error | 0 | `f5`, 1 | `00 00` | other circuits only |
| Current heat demand | 30,2 °C | `f5`, 2 | `2e 01` | yes |
| Flow setpoint, heating circuit | 28,2 °C | `f5`, 4 | `1a 01` | yes |
| Flow temperature, heat exchanger | -- | `f5`, 13 | `00 80` | other circuits only |
| Room temperature | 27,6 °C | `f5`, 17 | `14 01` | yes |
| Room setpoint | 14,0 °C | `f5`, 18 | `8c 00` | no |
| Outside temperature, mixed | 11,2 °C | `f5`, 2586 | `70 00` | no |
| Type of operation | "(0) Prog 1/DHW" | `f5`, 274 | `0b 00` | no |
| Outside temperature (module) | -- | `52`, 12 (`0c 00`) | `18 fc` | other circuits only |
| Input H1 (check box) | off | `52`, 2601 (`29 0a`) | 0 | **no** |
| Mixer pump (check box) | on | `52`, 82 (`52 00`) | 1 | **no** |
| Mixer pump PWM | 0 % | `52`, 645 (`85 02`) | 0 | **no** |
| Mixer opening (check box) | off | `52`, 86 (`56 00`) | 0 | **no** |
| Mixer closing (check box) | off | `52`, 87 (`57 00`) | 0 | **no** |

- **Established:** on a heating module, register 82 is the state of the mixer-circuit pump (the
  only box ticked, the only register reading 1). `18 fc` = -100,0 is displayed as "--": a module
  without outside sensor.
- Registers 86, 87, 645 and 2601 all read 0 and the four fields all show off or 0: assigned by the
  legends of `DL.Ini` (mixer open, mixer close, pump PWM, H1 input), not by a value.

### 19:09:19 — User (target `f5`)

| No. | Label | Shown | Register | Answer | Defined |
|---|---|---|---|---|---|
| 111 | Type of operation | (0) Prog 1 | 274 | 11 | no |
| 112 | Normal room temperature | 21,0 °C | 5 | 210 | yes |
| 113 | Reduced room temperature | 14,0 °C | 8 | 140 | yes |
| 117 | Gradient | 21,0 | 270 | 210 | yes |
| 118 | Room frost protection | 8,0 °C | 2580 | 80 | yes |
| 119 | Summer/winter change-over | 15,0 °C | 278 | 150 | yes |
| 114 | Setpoint reduction on solar yield | -- K | one of 129, 297, 298 | `00 80` | no |
| 115, 116 | Normal and reduced flow setpoint | -- °C | two of 129, 297, 298 | `00 80` | no |
| 141, 142 | Holiday | as on `35` | 283–288, 317 | same values | yes |

The five settings with a value confirm the existing definitions (`RoomNormalTemp`,
`RoomSetbackTemp`, `GradientCurve`, `RoomFrostProtectionTemp`, `SummerWinterChangeOverTemp`).
Register 40 is read by this tab as well.

### 19:09:58 — Engineer HC (targets `f5` and `52`)

Same fields and same registers as on `35`, with these differences: heating circuit type shows
radiator 75 °C and register 2419 reads 3; register 1710 is read on the module `52` (answer 0)
instead of the room unit.

### 19:10:19 — Configuration (targets `52` and `f5`)

| Label | Shown | Target, register | Answer | Defined |
|---|---|---|---|---|
| P315, type | mixed heating circuit | `52`, 65019 (`fb fd`) | 2 | **no** |
| Pump | multi-stage | `52`, 65019 or 857 | | no |
| Outside sensor | not available | `52`, 65019 or 857 | | no |
| Voltage | automatic, off | `52`, 857 (`59 03`) | 0 | **no** |
| Version of the module | 372.03 | `52`, 409 and 410 | 372, 3 | other circuits only |
| Version of the room unit | 327.26 | none (from the scan) | | |
| P335, configuration of the room unit | internal room sensor | `f5`, 16 | 2 | other circuits only |

Four fields are filled from two registers (65019, 857); the split is not established.

## Cascade manager, entry `KA-WST` (`f6`), 19:11:01

One window, no tab: heat demand per heating circuit HC1–HC8 (6, 8, 30 shown for circuits 1–3,
the rest empty), release of heating per circuit (only circuit 3 ticked), release of DHW per
circuit (circuits 1–3 ticked), system setpoint 36, DHW setpoint 8.

The tool sent a single request: `f6 0902 03 00 02 / 02 50 00` (register 3 = 8,0, the DHW
setpoint). Everything else on this screen was displayed without a request: the tool takes it
from the telegrams the room units and the manager send on their own. The three demands agree,
truncated, with register 2 read on the room units (6,9 on `35`, 30,2 on `f5`) and the system
setpoint with register 2 of `15` (36,2).

## Cascade manager, entry `KA` (`15`)

Tabs: Process values, Engineer HC, Engineer DHW, DHW, Circulation, Error history, Configuration.
Error history: see "Second visit".

### 19:11:51 — Process values

Same registers as on 2026-11-16. Values this time: system setpoint 36,2 (register 2), sensor B22
48,4 (13), sensor B24 60,3 (2624), DHW setpoint 8,0 (3), DHW temperature 35,3 (14), both boilers
"standby" with 0,0 kW, configuration list showing two entries for register 16 = `4c 00`.
Registers 425, 426, 2600, 2624, 2702, 65008, 65010 and 274 are still without a definition.

### 19:12:33 — Engineer HC

25 registers.

| No. | Label | Shown | Register | Answer | Defined |
|---|---|---|---|---|---|
| 532 | Change-over time | 50 h | 65004 | 50 | yes |
| 535, 536 | Modulation minimum, maximum | 30 %, 80 % | 65003, 65002 | 30, 80 | yes |
| 537 | Blocking time | 1 min | 37 | 1 | yes |
| 538 | Continuous temperature | 10,0 °C | 65001 (`e9 fd`) | 100 | **no** |
| 539, 540 | Controller P and I part | 100, 100 | 671, 670 | 100, 100 | yes |
| 551 | De-couple excess | 6,0 K | 65000 (`e8 fd`) | 60 | **no** |
| 552 | De-couple minimum | 8,0 °C | 64999 | 80 | yes |
| 553 | De-couple maximum | 78,0 °C | 64998 (`e6 fd`) | 780 | **no** |
| 561 | Calorifier excess | 1,0 K | 64995 (`e3 fd`) | 10 | **no** |
| 562 | Calorifier switching difference | 2,0 K | 64994 | 20 | yes |
| 593 | Start of summer time | 29 March | 64990, 64991 | 29, 3 | **no** |
| 594 | End of summer time | 25 October | 64992, 64993 | 25, 10 | **no** |
| 533 | Boiler sequence 1 | a, b | 64970 (`ca fd`), 64971 (`cb fd`) | 0, 1 | **no** |
| 534 | Boiler sequence 2 | b, a | 64980 (`d4 fd`), 64981 (`d5 fd`) | 1, 0 | **no** |
| 525 | Special level | --, greyed | 65006 (`ee fd`) | `00 80` | **no** |
| 521, 522, 523 | Function of outputs MFA 1, MFA 2, VA | feeder pump, circulation pump, DHW pump | among 64932, 64962, 65005, 65007, 65009, 65011 | 2, 0, 2, 3, 1, 3 | no |
| 524, 526 | Function of inputs H1, N1 | standby of the system, 2–10 V | same group | | no |
| 531 | Sequence change mode | by time | same group | | no |
| | Type of operation | automatic | 274 | 11 | no |

- **Established by a value that occurs once:** 65001, 65000, 64998, 64995 (tenths), and the summer
  time registers. Established by a pair of values: the two boiler sequences (0 = a, 1 = b).
- The six function registers are a group; which is which is not established. Registers 65008 and
  65010, next to them, are the states of VA and MFA 1 (log of 2026-11-16).

### 19:13:11 — Engineer DHW

14 registers.

| No. | Label | Shown | Register | Answer | Defined |
|---|---|---|---|---|---|
| 572 | DHW normal setpoint | 50,0 °C | 19 | 500 | yes |
| 573 | DHW reduced setpoint | 8,0 °C | 650 (`8a 02`) | 80 | **no** |
| 574 | DHW maximum | 60,0 °C | 385 (`81 01`) | 600 | **no**; by elimination |
| 575 | DHW switching difference | -5,0 K | 320 | `ce ff` | yes; **signed** |
| 576 | DHW excess | 10,0 K | 45 | 100 | yes |
| 577 | DHW load time | off | 384 | 0 | yes |
| 578 | Maximum load during DHW | 100 % | 5106 (`f2 13`) | 100 | **no**; by elimination |
| 579 | Legionella function | Monday | 257 | 1 | yes |
| | Solar recovery with legionella (check box) | off | 5105 (`f1 13`) | 0 | **no**; by elimination |
| 580 | Legionella setpoint | 60,0 °C | 1415 | 600 | yes |
| 581 | Legionella time | 08:30 | 65012 (`f4 fd`) | 34 | **no** |
| 582 | Circulation with legionella (check box) | off | 5107 | 0 | yes |
| 583 | Circulation time | 10:00 min | 2481 | 600 | yes |
| | DHW variation | empty, greyed | 309 (`35 01`) | `00 80` | no |

- **Established:** register 650 is the reduced DHW setpoint (the only 80). Register 65012 is the
  legionella time in quarter hours (34 = 08:30). Register 320 is signed.
- Three registers read 600. Two are defined (legionella setpoint, circulation time in seconds);
  the third, 385, is left for the DHW maximum. The same reasoning gives 5106 and 5105.

### 19:13:51 and 19:14:29 — DHW and Circulation programmes

Same layout as the heating programmes, programme byte `17` (DHW) and `1a` (circulation).
DHW: 09:00–16:00 on four days, `10 17` / `40 24`. Circulation: empty, all `80 80`. The numbers
501–507 and 551–557 are printed in front of the days.

### 19:14:50 — Configuration

Three groups numbered 512 (two lines, one per boiler: address letter, 250, variant), 513 (four
lines: empty, "DHW by the manager", "--", empty) and 514 (circuits 1 and 3). Read for this tab:
registers 118 (`76 00`) and 120 (`78 00`), both `18 fc` = -100,0 (buffer top and bottom in
`DL.Ini`, no sensor), not defined. The rest comes from register 16 and from the scan.

## Boiler automat A (`08`), second build

Window title as on 2026-11-16. Tabs: Process values WTC, End user, Heating specialist,
Manufacturer, Statistic, Error history (see "Second visit").

### 19:15:55 — Heating specialist

The window read the same five `50 00` blocks as on 2026-11-16 (EEPROM `0x1b`–`0x51`). This build
displays the values:

| Parameter | Shown | | Parameter | Shown |
|---|---|---|---|---|
| P10 type of unit | version H | | P34 burner stop/start block | 0 min |
| P11 type of gas | natural gas with flue gas damper | | P35 ignition rating | 37 % |
| P12 boiler address | A | | P36 minimum boiler rating | 23 % |
| P13 function of MFA1 | 9, flue gas damper control (greyed) | | P37 maximum rating, heating | 100 % |
| P14 function of MFA2 | 2, boiler pump | | P38 maximum rating, DHW | 100 % (greyed) |
| P15 function of VA | 7, heating circuit pump | | P40 continuous run of the pump | 0 |
| P16 input H1 | 4, damper feedback open (greyed) | | P41 pump run-on, heating | 1 min |
| P17 input H2 | 4, damper feedback closed (greyed) | | P42 pump run-on, DHW | 3 min (greyed) |
| P18 special level | 60 °C (greyed) | | P43 pump control function | 4 |
| P20 outside sensor correction | 0 K | | P44, P45 pump rating min, max | 50 %, 100 % |
| P23 frost protection | 5 °C | | P46 pump rating, DHW | 100 % (greyed) |
| P30 minimum flow temperature | 8 °C | | P47, P48 temperature difference control | 2 K, 20 K (greyed) |
| P31 maximum flow temperature | 80 °C | | P49 pump control interval | 4 s |
| P32 switching difference | 4 °C | | P50, P51 DHW excess, negative difference | 10 K, -5 K (greyed) |
| P33 flue gas switch-off temperature | 120 °C | | P70 service interval | 4000 h |
| | | | P71 eBUS feed | 1 |

A third column, A1–A32 (controller parts, fan limits, expansion limits), is greyed and empty.
The address of each parameter follows from the developer window below.

### 19:16:30 — Manufacturer

The tab lists S0, S11–S13, S21–S24, S31–S34, S41–S45, S51–S53, S55, S61–S64 and S01–S03, all
greyed and empty at this access level. It read EEPROM `0x02`–`0x18`, `0x25`, `0x2d`, `0x2e`:

```
08 5000 c6 b2 02             / 00 47 32 23 50 64 2c 28 c2 60 78 69 5f
08 5000 09 a2 0e 02 2d       / 00 1e 14 28 05 05 60 03 01 05 15 a9 | 17
08 5000 8a 02 25 02 2e       / 00 5c | 17
```

These are the reads grabbed without a screen at 15:59 on 2026-11-16.

### 19:16:57 — End user

Three fields (normal temperature setpoint, reduced temperature setpoint, DHW setpoint by day)
and a winter/summer choice, all empty. Read: EEPROM `0x0300`–`0x0304` (`3d 40 32 00 73`) and
`0x1b`, `0x1c`, `0x1d`. Not matched to the fields.

### 19:17:35 — Process values WTC

Empty, and no telegram, as in the first build. Fields offered: inputs H1, H2, flame, gas pressure
switch, air pressure switch, siphon switch, water pressure; outputs MFA1, MFA2, VA, ignition, gas
valves 1 and 2, pump; fan set speed, actual speed and PWM; I15 input N1; I32 ionisation; pump
minimum, setpoint, maximum; type of operation for heating and DHW; error; burner block time;
I11 load; effective setpoints with release; I30 flow (safety sensor), I31 flue gas, I33 outside,
I34 DHW, I35 flow (B12), I37 return, I39 de-couple sensor.

### 19:18:06 — Statistic

Still empty except I44–I46 and P70. The tab lists, in this order, the counters F11, W12, W14,
F15/W15, W16, F18/W18, F21, W22, F23, W24, F30, F31, F32, W34, F35, F36, F37, F38, W39, F41, F43,
F44, F45, F46, W47, F48/W48, F49, F51, F52, F53, F55, F57, then I42 (burner starts), I43 (burner
hours), I44–I46, P70, number of mains-on, operating hours of the boiler. `Reset` not used.

## Developer window of the second build (`Development`, Test data)

After a question whether to load the symbol file of the automat from the tool's own folder
(answered yes; nothing goes to the bus), a window named after that symbol file opens. Tabs:
FS-Paras, NFS-Paras, Statistik, Funktionen, Prozesswerte, MasterReset/HW/etc, BCC-ID, Logger,
Memory remains, Ion-Kalib. The tabs MasterReset and Ion-Kalib were not opened. Several tabs hold
send, enter and reset buttons; none was used. `Variables` and `EEPROM` of the same menu showed
nothing.

Showing FS-Paras, NFS-Paras and Statistik made the tool read boiler `08` (19:19:20–19:19:45):
only `50 00` reads, the blocks already known plus the statistics area in ten-byte steps from
`0x0192`. The other tabs sent nothing.

### FS-Paras — EEPROM `0x02`–`0x18`

23 fields in a fixed order. All 23 displayed values equal the 23 bytes read, in order:

| Address | Symbol | Shown | | Address | Symbol | Shown |
|---|---|---|---|---|---|---|
| `0x02` | option byte | 71 | | `0x0e` | `ION_ON` | 30 |
| `0x03` | `TCVSP` | 50 | | `0x0f` | `ION_OFF` | 20 |
| `0x04` | `TCHZZ` | 35 | | `0x10` | `LIM_ION_FLASTAB` | 40 |
| `0x05` | `TCNSP` | 80 | | `0x11` | `TC_PRUEF_V1` | 5 |
| `0x06` | `TCFLASTAB` | 100 | | `0x12` | `TC_PRUEF_V2` | 5 |
| `0x07` | `NG_VSP` | 44 | | `0x13` | `P_LPG` | 96 |
| `0x08` | `NG_NSP` | 40 | | `0x14` | `KASK_P_ANHEB` | 3 |
| `0x09` | `NG_GR_MIN` | 194 | | `0x15` | `KLAPPE_P_ANHEB` | 1 |
| `0x0a` | `NG_GR_MAX` | 96 | | `0x16` | `MAXGFASTART` | 5 |
| `0x0b` | `NG_MAX_LIMIT` | 120 | | `0x17` | `NG_BR_MIN` | 21 |
| `0x0c` | `MXSTB_K` | 105 | | `0x18` | `EE_CONST_CRC` | 169 |
| `0x0d` | `MXSTW_K` | 95 | | | | |

The option byte is shown as eight check boxes: bits 0, 1, 2 and 6 ticked for 71 (`0x47`). Their
names: bit 0 `OPTRESTART`, 1 `OPTNACHFAC`, 2 `OPTLDW_VSP`, 3 `OPT_NGIST`, 4 `OPTNOLDW`, 5
`OPT_TC`, 6 `OPT_GDW`, 7 `OPTNOEMERGENCYB`. This block is the manufacturer level (the S list).

### NFS-Paras — EEPROM `0x1b`–`0x51`

55 fields in a fixed order. All 55 displayed values equal the 55 bytes, in order. This closes the
open point of 2026-11-16 ("parameters not matched to single addresses").

| Addr. | Symbol | Shown | Addr. | Symbol | Shown | Addr. | Symbol | Shown |
|---|---|---|---|---|---|---|---|---|
| `1b` | `MAXTVSOLL` | 80 | `2e` | `NG_HZ_FREI` | 23 | `41` | `PNL_WW` | 3 |
| `1c` | `MINTVSOLL` | 8 | `2f` | `NG_HZ_MAX` | 100 | `42` | `TFRS_A` | 9 |
| `1d` | `HZ_HYS` | 68 | `30` | `PUHZ_VSP` | 50 | `43` | `NG_KP` | 8 |
| `1e` | `TBRMINOFF` | 0 | `31` | `PUHZ_MIN` | 50 | `44` | `NG_KTN` | 13 |
| `1f` | `TC_SOFTSTART` | 12 | `32` | `PUHZ_MAX` | 100 | `45` | `NG_REG_ANPASS` | 33 |
| `20` | `HZ_KP` | 10 | `33` | `PUHZ_DT_REG` | 98 | `46` | `SEL_IN_1_2` | 161 |
| `21` | `HZ_KTND` | 2 | `34` | `PU_TAKT` | 37 | `47` | `SEL_IN_3_4` | 65 |
| `22` | `SONDERNIVEAU` | 60 | `35` | `DT_VLRL_SOLL` | 20 | `48` | `SEL_PR_1_2` | 34 |
| `23` | `TAUSS_KORREKTUR` | 0 | `36` | `DT_VLRL_MAX` | 40 | `49` | `SEL_PR_3_4` | 167 |
| `24` | `WARTUNGSINTERVALL` | 40 | `37` | `DT_VL_ESTB2_MAX` | 25 | `4a` | `KLAPPENLAUFZEIT` | 25 |
| `25` | `MX_DREHZ_KESSEL` | 92 | `38` | `PNL_HZ` | 1 | `4b` | `PARA_DT_WEICHE` | 194 |
| `26` | `NG_ZUEND` | 37 | `39` | `MAXWWSOLL` | 60 | `4c` | `V24_KM_ADR` | 1 |
| `27` | `KESSEL_VARIANTE` | 25 | `3a` | `MINWWSOLL` | 30 | `4d` | `KESS_OPT` | 21 |
| `28` | `MXGRADTVIST` | 224 | `3b` | `WW_HYS` | 80 | `4e` | `KESS_OPT_2` | 85 |
| `29` | `MXTABGAS` | 120 | `3c` | `TWWPLUS` | 10 | `4f` | `KESS_BITS` | 12 |
| `2a` | `TOL_TIME` | 120 | `3d` | `NG_WW_MIN` | 23 | `50` | `REF_KORR` | 75 |
| `2b` | `NG_DGESCHW` | 1 | `3e` | `NG_WW_FREI` | 23 | `51` | `KES_DAT_CRC` | 184 |
| `2c` | `NG_INCR_DECR` | 33 | `3f` | `NG_WW_MAX` | 100 | | | |
| `2d` | `NG_HZ_MIN` | 23 | `40` | `PUHZ_WW` | 100 | | | |

Parameters of the heating-specialist tab that follow from name and value together (my reading,
each to be confirmed against the symbol table before a definition):

| Parameter | Shown | Symbol | Address |
|---|---|---|---|
| P12 boiler address | A | `V24_KM_ADR` = 1 (2 on automat B, log of 2026-11-16) | `0x4c` |
| P18 special level | 60 °C | `SONDERNIVEAU` | `0x22` |
| P20 outside sensor correction | 0 K | `TAUSS_KORREKTUR` | `0x23` |
| P30, P31 flow temperature min, max | 8, 80 °C | `MINTVSOLL`, `MAXTVSOLL` | `0x1c`, `0x1b` |
| P33 flue gas switch-off | 120 °C | `MXTABGAS` | `0x29` |
| P34 burner block | 0 min | `TBRMINOFF` | `0x1e` |
| P35 ignition rating | 37 % | `NG_ZUEND` | `0x26` |
| P36, P37 rating min, max, heating | 23, 100 % | `NG_HZ_MIN`, `NG_HZ_MAX` | `0x2d`, `0x2f` |
| P38 maximum rating, DHW | 100 % | `NG_WW_MAX` | `0x3f` |
| P41, P42 pump run-on | 1, 3 min | `PNL_HZ`, `PNL_WW` | `0x38`, `0x41` |
| P44, P45, P46 pump rating | 50, 100, 100 % | `PUHZ_MIN`, `PUHZ_MAX`, `PUHZ_WW` | `0x31`, `0x32`, `0x40` |
| P48 temperature difference | 20 K | `DT_VLRL_SOLL` | `0x35` |
| P50 DHW excess | 10 K | `TWWPLUS` | `0x3c` |
| P70 service interval | 4000 h | `WARTUNGSINTERVALL` × 100 | `0x24` |

### Statistik — EEPROM `0x0192`–`0x01ed`

The tab prints the size next to each counter and displays the values. Bytes from the reads of
19:19, low byte first:

| Symbol, size as printed | Address | Bytes | Shown |
|---|---|---|---|
| `EEA_HBRONTAG`, 1 byte | `0x01d8` | `00` | 0 |
| `EEA_NZUENDTAG`, 1 byte | `0x01d9` | `00` | 0 |
| `EEA_N_PON`, 3 bytes | `0x01da` | `dd 00 00` | 221 |
| `EEA_N_KON`, 3 bytes | `0x01dd` | `04 00 00` | 4 |
| `EEA_RES_CNT`, 3 bytes | `0x01e0` | `bf 05 00` | 1471 |
| `EEA_SHUT_OFF`, 3 bytes | `0x01e3` | `01 00 00` | 1 |
| `EEA_H_PON`, 3 bytes | `0x01e6` | `a8 54 01` | 87208 |
| `EEA_H_BON`, 2 bytes | `0x01e9` | `e5 4e` | 20197 |
| `EEA_N_ZUE`, 3 bytes | `0x01eb` | `8d db 02` | 187277 |

- **Established:** sizes and byte order of all nine counters, each against a value displayed by
  the tool. `EEA_N_ZUE` (burner starts) and `EEA_N_PON` (mains-on) now have the independent figure
  that `evidence/service-tool-log.md` listed as missing. Automat A only.

Fault counters, 2 bytes each, from `0x0192` in this order; all 35 displayed values equal the bytes:

| Address | Symbol | Shown | Address | Symbol | Shown | Address | Symbol | Shown |
|---|---|---|---|---|---|---|---|---|
| `0192` | `EEA_WRONG_ADR` | 0 | `01aa` | `EEA_FC_44` | 0 | `01c2` | `EEA_FC_30` | 0 |
| `0194` | `EEA_FCODE_NOT` | 0 | `01ac` | `EEA_FC_43` | 0 | `01c4` | `EEA_FC_24` | 0 |
| `0196` | `EEA_FC_57` | 20 | `01ae` | `EEA_FC_41` | 0 | `01c6` | `EEA_FC_23` | 0 |
| `0198` | `EEA_FC_55` | 1 | `01b0` | `EEA_FC_39` | 0 | `01c8` | `EEA_FC_22` | 17 |
| `019a` | `EEA_FC_53` | 1 | `01b2` | `EEA_FC_38` | 0 | `01ca` | `EEA_FC_21` | 24 |
| `019c` | `EEA_FC_52` | 0 | `01b4` | `EEA_FC_37` | 0 | `01cc` | `EEA_FC_18` | 0 |
| `019e` | `EEA_FC_51` | 0 | `01b6` | `EEA_FC_36` | 102 | `01ce` | `EEA_FC_16` | 0 |
| `01a0` | `EEA_FC_49` | 0 | `01b8` | `EEA_FC_35` | 0 | `01d0` | `EEA_FC_15` | 1 |
| `01a2` | `EEA_FC_48` | 0 | `01ba` | `EEA_FC_34` | 0 | `01d2` | `EEA_FC_14` | 0 |
| `01a4` | `EEA_FC_47` | 6 | `01bc` | `EEA_FC_33` | 0 | `01d4` | `EEA_FC_12` | 6 |
| `01a6` | `EEA_FC_46` | 0 | `01be` | `EEA_FC_32` | 0 | `01d6` | `EEA_FC_11` | 1 |
| `01a8` | `EEA_FC_45` | 1 | `01c0` | `EEA_FC_31` | 0 | | | |

The order is the reverse of the Statistic tab of the boiler window (which starts with code 11).

### Other tabs of the developer window (looked at, nothing read)

- Funktionen: a free send string with answer field and cyclic sending, three initialisation or
  reset commands, a choice of ten addresses (`03`, `13`, `33`, `73`, `f3`, `1f`, `3f`, `7f`, `10`,
  `f1`), and the list of RAM symbols of the automat with their address in decimal, with a choice
  of list (RAM, XRAM, bit, SFR) and of type (bit, unsigned or signed byte, unsigned or signed
  16 bit, 2-byte and 3-byte unsigned), gain, offset and decimals.
- BCC-ID: three identification fields and a system statistic of ten two-part entries with a
  pointer and three reset counters.
- Logger: an empty chart.
- Memory remains: read-out of a memory range by area (ROM, EEPROM, RAM, stack, XRAM), a CRC
  over a range, three address/value pairs to send, and test-bench commands.
- Prozesswerte: empty until variables are added from the Funktionen tab.

## Terminal, Datalogger, device types not on the bus

- **Terminal** (19:20:58): a passive monitor. It prints each telegram seen on the bus in hex with
  the PC time, sync bytes included. Opening it sent nothing.
- **Datalogger**: one chart with a temperature axis (-15 to 110 °C) and a speed axis (to 6600 rpm)
  and a tool bar; while opening it listed the two automats, the two room-unit entries and `KA`
  (not `KA-WST`). No channel was selected, nothing was started, nothing was sent.
- File, Open does not open a device type that is not on the bus; it only loads a saved
  parameter file (the `Development` menu can: see "Third visit"): the entries SOL and FB/EM ask for a file with the extension `ESO` and `EEM`.
  No such file is on the PC. Both dialogs were cancelled.

## Second visit, 19:30–19:36 — fault histories

On the owner's word the history tabs were opened on the other devices. The tool was connected
again at 19:29:58 and disconnected at 19:35:40.

### 19:30:57 — room unit `f5`, Process values (seen again)

One more field than at 19:08: flow temperature of the heating circuit, 38,2 °C, read on the module:
`52 0902 0f 00 02 / 02 7f 01` (register 15 = 38,3; polled, the display was one read behind).
Register 15 on a heating module is not defined for `52` in the fork. The field was absent at 19:08
and no request for register 15 was sent then.

### 19:31:38 — room unit `f5`, History

Ten writes `f5 0903 9a 0b <n> 00` (n = 0–9), each followed by the eight reads, as on `35`.

| Entry | Date | Time | Device shown | Code |
|---|---|---|---|---|
| 1 | 01.09.2000 | 03:51 | WTC | 0 |
| 2 | 03.09.2000 | 11:42 | WTC | 191 |
| 3 | 03.09.2000 | 10:28 | WTC | 0 |
| 4 | 01.09.2000 | 19:57 | WTC | 191 |
| 5 | 01.09.2000 | 17:56 | WTC | 181 |
| 6 | 01.09.2000 | 01:11 | WTC | 191 |
| 7 | 01.09.2000 | 00:55 | WTC | 0 |
| 8 | 01.09.2000 | 00:15 | WTC | 191 |
| 9 | 19.09.2000 | 23:58 | WTC | 0 |
| 10 | 02.09.2000 | 06:36 | WTC | 191 |

Registers of entry 10: code `bf 00`, type `03 00`, device `00 00`, minute 36, hour 6, day 2,
month 9, year 0.

- Year 0 is displayed as 2000.
- Entry 10 of `35` and entry 10 of `f5` both read type 3 and device 0, yet the device column says
  "KA" in one window and "WTC" in the other. The text of that column is therefore not derived
  from registers 2972 / 2973 alone. Not established.
- Eight of the ten entries of `f5` are also in the list of `35` (same date, time and code).

### 19:32:53 — cascade manager `15`, Error history

Same mechanism: ten writes `15 0903 9a 0b <n> 00`, eight reads each.

| Entry | Date as shown | Time | Device shown | Code |
|---|---|---|---|---|
| 1 | 07.11.2026 | 03:30 | WTC 2 | 0 |
| 2 | 07.11.2026 | 03:30 | WTC 1 | 0 |
| 3 | 01.01.20165 | 00:00 | WTC 2 | 80 |
| 4 | 01.01.20165 | 00:00 | WTC 1 | 80 |
| 5 | 00.00.2000 | 03:51 | KA | 0 |
| 6 | 03.00.2000 | 11:27 | KA | 191 |
| 7 | 03.00.2000 | 10:28 | KA | 0 |
| 8 | 03.00.2000 | 10:28 | KA | 192 |
| 9 | 01.00.2000 | 19:42 | KA | 191 |
| 10 | 01.00.2000 | 17:41 | KA | 181 |

Registers of entry 10: code `b5 00` (181), type `09 00`, device `00 00`, minute 41, hour 17,
day 1, month 0, year 0.

- Entries 1 and 2 carry the date and time of the entry read through ebusd on `50`
  (`evidence/em1-fault-log.md`: 7 November 2026, 03:30, code 0, device 1). That read returned
  device 1 for selector 0; the tool shows "WTC 2" first. Which of the two is selector 0 was not
  separated in this capture (only the registers of the last entry stay in the snapshot).
- Month 0 is displayed as "00"; the year of entries 3 and 4 is displayed with five digits.
- **Established: `15` and `50` share the selector.** Right after this tab, a read through ebusd
  (`read -f -c em1 ErrorId`, target `50`) returned 9. It returned 0 on 2026-11-18. Until the
  selector is written back to 0, the fault-log messages of `em1` return entry 9, not the most
  recent one.

### 19:34:26 — boiler automat A, Error history

Five `50 00` reads of EEPROM `0x0200`–`0x0231`, no write. The six entries and all 48 values are
the ones recorded on 2026-11-16 (W12, F11, W12, W12, W12, W12): no new entry since.

### 19:34:56 and 19:35:25 — boiler automat B

The tool answered twice that the selected device is not available, and sent no telegram to `18`
either time. Not opened. Its history is in the log of 2026-11-16.

### Selectors

After this visit the selectors of `35`, `f5` and `15` (and so `50`) were at 9. The tool offers no
way to write them back; a `Read` in the tab runs through 0–9 again. Writing them back to 0 is a
bus write and was handed to the session that runs the on-site write tests, with the owner's words.

Written back on the owner's word, 19:53:05–19:53:23, by that session, through ebusd, one device at
a time, from ebusd's own address `31`:

| Target | Read before | Write | Answer | Read after |
|---|---|---|---|---|
| `35` | `0902 9a 0b 02` / `02 09 00` | `0903 9a 0b 00 00` | `00` | `02 00 00` |
| `f5` | `02 09 00` | same | `00` | `02 00 00` |
| `15` | `02 09 00` | same | `00` | `02 00 00` |

Checked from this session afterwards: the three writes with source `31` are in the grabbed
telegrams, each answered `00`, and `read -f -c em1 ErrorId` (target `50`) returns 0 again.

- **Established:** the selector takes a `09 03` write from source `31`; source `ff` is not needed
  for this register (unlike the `50 23` settings). Selector 9 was read back from all three devices
  before the write, so the value the tool leaves behind is confirmed on the bus.
- The selector is ordinary read/write state: reading the fault log entry by entry is possible from
  ebusd with a write of the entry number followed by the eight reads.

## Third visit, 19:43–19:45 — `Development`, Sim FS, tool offline

Looked at on the owner's suggestion, with the tool disconnected so that nothing could reach the
bus. The sub-menu offers nine device types: FS1, FS2, FS1+2, control centre, FS+EM, EM, FS+EWW,
EWW, KA. Choosing one asks a yes/no question about an "FS 1.0" generation (answered no), then
opens the window of that device type as if the scan had found it, with an invented version
number. **This is the way to open a device type that is not on the bus.** Offline every field
stays empty and the error field shows 11.

| Entry | Window title | Tabs |
|---|---|---|
| EWW | DHW extension module, circuit 2, version 267.00 | Process values, User, Engineer WW, DHW, Circulation, Configuration |
| control centre | room unit "L", version 196.00 | the same six tabs |
| EM | heating extension module, circuit 2, version 267.00 | Process values, User, Engineer HC, Heating 1–3, Configuration |

Parameter lists of the DHW extension module (a type not installed here), numbers as printed:

- User: 132 normal DHW setpoint, 133 reduced DHW setpoint, 141 holiday start and end, 142 holiday
  temperature level.
- Engineer WW: 391 maximum DHW temperature, 395 legionella function, 605 solar use for
  legionella (check box), 606 legionella setpoint, 396 legionella time, 608 circulation with
  legionella (check box), 397 circulation time, 611 DHW from solar yield (list, with two check
  boxes: on coverage, on excess temperature).
- Process values: type of operation, error, DHW setpoint, current heat demand.
- Configuration: empty until read.

The EM entry opens the window of a heating module on its own, for circuit 2: process values (type
of operation, error, room setpoint, flow setpoint, current heat demand, mixed outside temperature,
flow temperature of the heat exchanger) and the tabs listed above. With the tool connected this
window would presumably read module `51` directly instead of through the room unit.

Not established: what these entries send when the tool is connected (reads of the chosen type
only, or telegrams in the name of a simulated device). Not tried online. The other six entries
were not opened.

## Registers without a definition, by device

Candidates for the definitions session. "Value" = established by a value that occurs once on the
screen; "pair" = by a set of values; "legend" = by the `DL.Ini` legend and a consistent value;
"elimination" = the only register left for the field; "group" = the register belongs to the tab
but not to one field.

| Device | Register | Bytes | Meaning | How |
|---|---|---|---|---|
| room unit | 18 | `12 00` | room setpoint in effect, tenths | value, two units |
| room unit | 2586 | `1a 0a` | outside temperature, mixed, tenths | value, legend |
| room unit, manager | 274 | `12 01` | type of operation (reads 11 everywhere) | group |
| room unit | 2419 | `73 09` | heating circuit type (2 = radiator 60 °C, 3 = radiator 75 °C) | value, three units |
| room unit, manager | 64990–64993 | `de fd`–`e1 fd` | summer time: start day, start month, end day, end month | value, two devices |
| room unit | 296, 306 | `28 01`, `32 01` | one of them: reducing operation (1 = reduce) | group |
| room unit | 129, 297, 298 | | flow setpoints normal and reduced, reduction on solar yield (no value here) | group |
| room unit | 271, 277, 315, 1711, 2417, 2588 | | start optimisation actual, construction type, room thermostat, adaption, room influence (no value here) | group |
| room unit (second circuit) | 282, 1556, 2651 | | boiler delay, screed function, function of H1 (all 0) | group |
| room unit (second circuit) | 303, 304, 443, 444, 2204–2210, 2560, 2578, 3103, 3105 | | sensor correction, frost protection, pump speeds, screed programme (no value here) | group |
| heating module | 82 | `52 00` | mixer-circuit pump on | value |
| heating module | 86, 87 | `56 00`, `57 00` | mixer opening, mixer closing | legend |
| heating module | 645 | `85 02` | mixer pump PWM, % | legend |
| heating module | 2601 | `29 0a` | input H1 | legend |
| heating module | 399 | `8f 01` | mixer parameter, tenths | elimination |
| heating module | 65019, 857 | `fb fd`, `59 03` | configuration (type, pump, outside sensor, voltage) | group |
| heating module | 1710 | `ae 06` | read with the engineer tab (0) | group |
| manager | 65001 | `e9 fd` | continuous temperature, tenths | value |
| manager | 65000 | `e8 fd` | de-couple excess, tenths of K | value |
| manager | 64998 | `e6 fd` | de-couple maximum, tenths | value |
| manager | 64995 | `e3 fd` | calorifier excess, tenths of K | value |
| manager | 64970, 64971 | `ca fd`, `cb fd` | boiler sequence 1, positions 1 and 2 (0 = a, 1 = b) | pair |
| manager | 64980, 64981 | `d4 fd`, `d5 fd` | boiler sequence 2, positions 1 and 2 | pair |
| manager | 65006 | `ee fd` | special level (no value here) | elimination |
| manager | 64932, 64962, 65005, 65007, 65009, 65011 | | functions of MFA 1, MFA 2, VA, H1, N1 and sequence change mode | group |
| manager | 650 | `8a 02` | DHW reduced setpoint, tenths | value |
| manager | 65012 | `f4 fd` | legionella time, quarter hours | value |
| manager | 385 | `81 01` | DHW maximum, tenths | elimination |
| manager | 5106 | `f2 13` | maximum load during DHW, % | elimination |
| manager | 5105 | `f1 13` | solar recovery with legionella | elimination |
| manager | 309 | `35 01` | DHW variation (no value here) | elimination |
| manager | 118, 120 | `76 00`, `78 00` | buffer top, bottom (-100,0 = no sensor) | legend |
| manager | 425, 426, 2600, 2624, 2702, 65008, 65010 | | as in the log of 2026-11-16 | |

A value seen only on the screen and in the tool's own request is a hint. Before a definition, each
register is to be read from ebusd with the same result (`docs/service-tool-protocol.md`).

## Not opened, not verified

- Heating programmes of `f5`: not opened.
- Automat B: not opened (the tool reported it as not available on the second visit).
- System time, Extra access, Password, eBus-Trigger, CM controller, BCC, Analyse BCC, and the
  tabs MasterReset and Ion-Kalib of the developer window: not opened. Sim FS: offline only.
- The meaning of the values of the enumerations (circuit type, functions of inputs and outputs)
  beyond the ones displayed.

## Equipment

Two WTC condensing boilers with WCM-CPU automats (firmware 11.0e), a Kromschröder cascade manager
(266.18), two room units answering the scan (327.26), a third room unit and two heating modules
(372.03) reached through them, the vendor's bus interface on a service PC.
