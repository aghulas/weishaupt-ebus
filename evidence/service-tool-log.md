# Service tool comparison — log

Notes taken while following `docs/service-tool-protocol.md`. Facts only; no vendor file is copied
here. Symbol names and addresses quoted below already appear in the fork's
`src/kromschroeder/*.tsp` files.

Tool: WCM-Diagnose 5.5.19a (Windows).

## Phase 1 — installation folder (no bus)

Date: 2026-11-16. Method: file listing, binary parsing with a throw-away script, comparison with
the fork's files. Nothing was run from the installation folder.

### Contents

| File(s) | Kind | What it holds |
|---|---|---|
| 36 × `*.SYC` (`0000360` … `0098370`, `WH00928` … `WH91928`) | binary | Firmware symbol tables, one per controller type and version (details below). |
| `DL.Ini` | INI | Data-logger channel definitions per device family: variable, data type, gain, offset, legend. |
| `Cxe.Ini` | INI | Interface settings of the tool. |
| `WCMDiag5519.exe`, `WCMDiag5519b.exe` | PE32 (Delphi) | The program. Two builds of the same size with different contents; the second one was not examined. |
| `HL_DLL.dll` | PE32 DLL | Not examined. |

No language file, parameter table or log file is present in the folder.

### `Cxe.Ini` — interface

- `Baudrate=2400`, `Protocol=CoCo`, `PC_Adr=255`.
- **Established:** the tool sends as master `0xff`. This confirms the address in the protocol
  document; it was previously known only from bus captures.

### `*.SYC` — symbol tables

Structure, the same in all 36 files, established by parsing every file to the last byte:

- Five lists. Each one opens with a header `7a 05 <count u16 LE> <u16> 20 00`, followed by
  `<count>` records `79 05 <len> <name: len bytes> <address u16 LE>`.
- Each list is closed by a title record `01 <len> <text>`. The titles, in order, are:
  `Liste der RAM-Daten`, `Bit-Liste`, `SFR-Liste`, `Liste der Konstanten`, `Liste der XRAM-Daten`.
- The record count in each header matches the records parsed, in all 36 files.
- **A record holds a name and an address only. There is no size, type, factor, unit or bank.**

The fork's `src/kromschroeder/*.tsp` files (36 of them, the raw memory maps in #717) were
generated from these tables. Matching on name and address:

| File | Entries in the `.tsp` | Found in the `.SYC` | Not found |
|---|---|---|---|
| 35 files | 392 … 1447 each | all but 0–5 | only the hand-added RAM aliases `BYTE_20/21/22/25/27` |
| `WH11928` | 854 | 842 | 12: `BYTE_20/21/22/25`, `EEA_ION_KALIB_2_INV`, `EEA_F_HIST_PTR`, `EEA_F_HIST_ANF1..6` |

So the `.SYC` files back the **names and addresses** in the memory maps. The **lengths and codecs**
(`UCH`, `UIN`, `U3N`) and the memory-read encoding byte (`0x02` / `0x12` / `0x22`) are **not**
in the `.SYC`: they were added when the `.tsp` files were made.

#### Hour and start counters (question 1 of the protocol, lot D)

Addresses in the constants list (EEPROM), from the `.SYC`:

| Symbol | `WH11928` | `0000360` | `0011366` | Gap to the next symbol |
|---|---|---|---|---|
| `EEA_N_PON` | `0x01DA` | `0x00E2` | `0x00E2` | 3 (`WH11928`) |
| `EEA_SHUT_OFF` | `0x01E3` | `0x00EB` | `0x00E9` | 3 |
| `EEA_H_PON` | `0x01E6` | `0x00EE` | `0x00EB` | **3** in all three |
| `EEA_H_BON` | `0x01E9` | `0x00F1` | `0x00EE` | **2** in all three (next: `EEA_N_ZUE`) |

- **Established:** in `WH11928`, `EEA_H_PON` is at most 3 bytes long and `EEA_H_BON` at most 2
  bytes long, because the next symbol starts there. The same spacing holds in the other firmware
  families checked.
- This is consistent with `U3N` for `EEA_H_PON` and `UIN` for `EEA_H_BON` in the fork's
  `WH11928.tsp`. It is **inconsistent** with the deployed 1-byte reads (encoding byte `0x02`),
  which return only one byte of a multi-byte counter. That explains the implausible values
  (90 h operating < 216 h burner).
- **Not established:** that the counters fill the whole gap, their byte order, and the meaning of
  the encoding byte. In the fork, its high nibble tracks the length (`0x02` = 1 byte, `0x12` = 2
  bytes, `0x22` = 3 bytes, 46 entries), and its low nibble is `1` for RAM entries and `2` for
  constants. That is the fork's convention, not something read from a vendor file. It needs a
  phase 2 capture of a `50 00` request sent by the tool.

#### Executable

- The program carries the names `EEA_BAUSTAND`, `EEA_N_PON`, `EEA_N_KON`, `EEA_RES_CNT`,
  `EEA_SHUT_OFF`, `EEA_H_PON`, `EEA_H_BON`, `EEA_N_ZUE`, `EEA_FC_01`, `EEA_FC_31`,
  `EEA_PRUEF_LOW`, `EEA_PRUEF_CRC`, `EEA_KUNDE`, `EEA_SERIAL_NO`, together with RAM names
  (`TVIST`, `TAUSSEN`, `TWWIST`, `TABGAS`, `YPWM`, `F_CODE`, `XPAGE_CONT`). It builds a list of
  items from them, each with a small constant integer. So the tool looks these symbols up by
  name, which is what makes the `.SYC` tables necessary.
- The integers are not the addresses of any shipped `.SYC`: at most 4 of 19 match any single
  file. Their meaning is not established.

### `DL.Ini` — data-logger channels

- The sections for the boiler automats (`WCM`, `WCM45`, `WCM3`, `WCM_5`, `WTO`, `WTO_OB`) name
  RAM symbols (for example `TA_MITTEL` `SChar` gain 0.25; `NGIST` `UChar`, gain 0.5 on `WCM45` /
  `WCM3` / `WTO`). These names resolve to addresses in the `.SYC` RAM or XRAM lists (for
  example in `WH11928`: `TVIST` `0x0068`, `TA_MITTEL` `0xF0B1`).
- The sections for the system and room devices (`KA`, `SOL`, `FB#n`, `EM#n`, `FS#…`, `EWW#n`)
  name **register numbers**. A number is the `50 22` register address read little-endian:
  `<lo> <hi>` = `<addr> <sub>` in the read ID.
  - **Established by cross-check** with registers already read on the bus
    (`evidence/ka-reads.md`):

    | Number | Bytes | Legend in `DL.Ini` | Type × gain | Existing definition |
    |---|---|---|---|---|
    | 2 | `02 00` | system setpoint | UInt × 0.1 | `HeatDemandTemp`, `temp10` |
    | 3 | `03 00` | DHW setpoint | SInt × 0.1 (KA), UInt × 0.1 (FB) | `DHWSetValue`, `temp10` |
    | 12 | `0c 00` | outside temperature | SInt × 0.1 | `OutsideTemp`, `otemp10` (SIN) |
    | 13 | `0d 00` | hydraulic separator / plate exchanger secondary, B22 | SInt × 0.1 | `SupplyWTCTemp`, `temp10` |
    | 14 | `0e 00` | DHW actual | SInt × 0.1 (KA), UInt × 0.1 (EWW) | `DHWTemp`, `temp10` |
    | 44 | `2c 00` | modulation setpoint | UInt × 1 | `ModulationStatus`, `percent` |
    | 2572 | `0c 0a` | outside temperature, weighted | SInt × 0.1 | `OutsideWeightedTemp`, `otemp10` (SIN) |

  - Factors agree with every existing definition. Signedness differs between sections of the
    file itself for registers 3 and 14, so the `DL.Ini` type is a hint for the sign, not proof.
  - Register 13 is labelled as sensor B22 on the hydraulic separator or plate exchanger
    secondary, not as the boiler flow. Its name in lot A should be checked against the screen in
    phase 2.
  - Registers listed with no definition yet (hints for a later lot; read on the bus first):
    4 heating-circuit flow setpoint, 15 heating-circuit flow actual, 17 room actual, 18 room
    setpoint (all UInt × 0.1); 82/83/86/87/100 mixer pump, charge pump, mixer open, mixer
    close, circulation pump (UInt); 118/120 buffer top/bottom (× 0.1); 130 flow rate
    (× 0.1); 425/426 control voltage/current (× 0.1); 475 solar power, 1706 solar yield
    (× 0.001); 645 pump PWM; 725 solar pump; 753 solar status; 756 and 5006 bit masks;
    1257 circulation temperature (SInt × 0.1); 2586 outside temperature, mixed (SInt × 0.1);
    2600/2601 H1 input; 2601–2604 solar sensors T1–T4 (SInt × 0.1, solar module); 2624 plate
    exchanger primary B24 (SInt × 0.1); 2702, 65008, 65010 relay states.

### What phase 1 changes

- Lot D: the length question is narrowed. The memory map supports 3-byte `EEA_H_PON` and 2-byte
  `EEA_H_BON` on `WH11928`. The deployed 1-byte reads are wrong by construction. Still needed
  before the lot can ship: the request bytes the tool itself sends (phase 2, protocol question 1).
- Lot A: 7 existing register definitions agree with the tool's factors. The sign of
  `SupplyWTCTemp`, `DHWSetValue` and `DHWTemp` and the meaning of register 13 are open points
  for phase 2.

## Phase 2 — screens

Date: 2026-11-16, 15:47–15:59. Method: `docs/service-tool-phase2-sheet.md`. Snapshots of the
telegrams grabbed by ebusd before and after each screen; screens read from screenshots. The tool
sent no write (`50 23`) during the session: every telegram with `QQ=ff` was a `07 04`
identification, a `09 02` read, a `50 22` read or a `50 00` memory read. No setting was written
with source `ff` by anything else while the tool was connected.

Telegrams below are `QQ ZZ PBSB data / answer`, with the length bytes left out of the data.

### 15:49 — connection (no screen)

The tool sends one `07 04` identification to `08`, `15`, `18`, `35`, `f5`, `f6`. Not to `50`,
`51`, `52`, `75`.

### 15:50 — system manager, tab "Process values"

Device: system manager, scanned `SW=6618` (window title `KA 266.18`).

The tool reads this device with `09 02`, data `<register lo> <register hi> 02`, **no CRC byte**.
The answer is the 16-bit value, low byte first.

| Label on screen | Value | Unit | Telegram | Codec deduced |
|---|---|---|---|---|
| Set temperature System | 57,9 | °C | `ff 15 0902 02 00 02 / 43 02` | UIN or SIN, 0.1 |
| De-couple temperature B22 | 57,6 | °C | `ff 15 0902 0d 00 02 / 40 02` | UIN or SIN, 0.1 |
| De-couple temperature B24 | 60,8 | °C | `ff 15 0902 40 0a 02 / 60 02` | UIN or SIN, 0.1 |
| DHW set value | 50,0 | °C | `ff 15 0902 03 00 02 / f4 01` | UIN or SIN, 0.1 |
| DHW-temperature | 51,7 | °C | `ff 15 0902 0e 00 02 / 04 02` (51,6; polled, next read differs) | UIN or SIN, 0.1 |
| Control voltage | 0,0 | V | `ff 15 0902 a9 01 02 / 00 00` | value 0 only |
| Control current | 0,0 | mA | `ff 15 0902 aa 01 02 / 00 00` | value 0 only |
| H1 (check box) | off | | `ff 15 0902 28 0a 02 / 00 00` | 0 = off |
| MFA 1 (check box) | on | | `ff 15 0902 f2 fd 02 / 01 00` | 1 = on |
| MFA 2 (check box) | off | | `ff 15 0902 8e 0a 02 / 00 00` | 0 = off |
| VA (check box) | off | | `ff 15 0902 f0 fd 02 / 00 00` | 0 = off |
| Error code | empty | | `ff 15 0902 01 00 02 / 00 00` | 0 = none |
| Configuration: PWT, DHW KA, Calorifier 1 | list | | `ff 15 0902 10 00 02 / 4c 00` | bit field, bits 2, 3, 6 set; bit-to-text mapping not established |
| setpoint mod. degree | 1 | % | `ff 15 0902 2c 00 02 / 01 00` | factor 1 |
| Max. limit opt. operating range | 80 | % | `ff 15 0902 ea fd 02 / 50 00` | factor 1 |
| Min. limit opt. operating range | 30 | % | `ff 15 0902 eb fd 02 / 1e 00` | factor 1 |

- **Established:** register 13 (`0d 00`) is the de-couple sensor B22, as `DL.Ini` says. It is not
  the boiler flow. The lot A name `SupplyWTCTemp` is misleading.
- **Established:** registers 2, 3, 13, 14 and 2624 are in tenths.
- **Not established:** the sign of registers 3, 13 and 14 (no negative value on screen).
- Not matched, labels: `Operation mode` = "Automatic" (candidate: `ff 15 0902 12 01 02 / 0b 00`,
  one value only); `Calorifier temperature top` / `bottom`, both "--", no telegram.
- Not matched, cascade block (`Type of oper.`, `Nominal rating` 250 kW, `Current rating` 57,5 kW
  for boiler A, 0,0 kW for boiler B). The tool polls both automats directly:
  `ff 08 5000 1a 03 b2 01 21 01 25 01 65 01 6a / 00 19 55 02 00 d8` and
  `ff 18 5000 (same) / 00 00 40 80 00 d8`. By the grammar below this is one byte of area `3` at
  `b2` and four RAM bytes at `21`, `25`, `65`, `6a`. The first byte (25 on A, 0 on B) may be the
  load in percent; not proven.

### 15:51 — boiler automat A, tab "Heating specialist"

Device: WTC automat, scanned `SW=1104;HW=0501` (window title `WCM-CPU-R5#A WTC 250 HA 11.0e`).
The values were read, nothing was edited, `Write` / `Load` / `Save` were not used.

Telegrams (answer without its status byte `00`):

```
ff 08 5000 df b2 1b             / 50 08 44 00 0c 0a 02 3c 00 28 5c 25
ff 08 5000 e3 b2 27             / 19 e0 78 78 01 21 17 17 64 32 32 64
ff 08 5000 f7 b2 33             / 62 25 14 28 19 01 3c 1e 50 0a 17 17
ff 08 5000 fb b2 3f             / 64 64 03 09 08 0d 21 a1 41 22 a7 19
ff 08 5000 ab 62 4b 02 44 02 37 / c2 01 15 55 0c 4b b8 | 0d | 19
```

**Grammar of a `50 00` memory read, established from these telegrams.** After the CRC byte the
data is a list of items `<code> <address>`:

- high nibble of the code = number of bytes minus one (`b` = 12, `6` = 7, `0` = 1);
- low nibble of the code = memory area: `1` RAM, `2` EEPROM (the constants list of the `.SYC`);
- code `06` reads nothing: it sets the high byte of the address for the items that follow.

The answer is a status byte `00` followed by the bytes of all items, in order.

Proof inside the capture: the last telegram re-reads single bytes at `44` and `37`; it returns
`0d` and `19`, the bytes found at those addresses in the 12-byte blocks (`3f`+5, `33`+4).
Further proof: every later telegram of the session parses with this grammar and returns the
number of bytes it predicts.

Consequence: the read already used for `FaultCountW47`, `20 06 01 12 a4`, is "high byte `01`,
two EEPROM bytes at `a4`", address `0x01a4`. The fork's convention for the encoding byte
(`0x02` / `0x12` / `0x22`) is the tool's own.

Not matched: the parameters on screen (P10 … P71) to single addresses. The values are in the
block (`50` = P31 80 °C at `1b`, `08` = P30 8 °C at `1c`, `28` × 100 = P70 4000 h at `24`), but
several values occur twice. To be matched with the `.SYC` constants list.

### 15:53 and 15:55 — boiler automat A, tab "Statistic"

The tool read the statistics when the tab was opened and again on `Read` (`Reset` not used).
Both times the same 11 telegrams. **The screen stayed empty** except `I44: Version CPU`,
`I45: Version CUI`, `I46: Burner operation since last service` (-19752) and
`with service interval (P70)` (4000). So the counters could not be compared with a displayed value.

```
ff 08 5000 9c 06 01 72 e6 06 00 02 24 / 5c 54 01 da 4e 5a db 02 | 28      (15:53)
ff 08 5000 9c 06 01 72 e6 06 00 02 24 / 5d 54 01 da 4e 5a db 02 | 28      (15:55)
ff 08 5000 e2 06 01 92 96             / 14 00 01 00 01 00 00 00 00 00
ff 08 5000 d4 06 01 92 a0             / 00 00 00 00 06 00 00 00 01 00
ff 08 5000 de 06 01 92 aa             / 00 00 00 00 00 00 00 00 00 00
ff 08 5000 c0 06 01 92 b4             / 00 00 66 00 00 00 00 00 00 00
ff 08 5000 ca 06 01 92 be             / 00 00 00 00 00 00 00 00 00 00
ff 08 5000 bc 06 01 92 c8             / 11 00 18 00 00 00 00 00 00 01
ff 08 5000 a6 06 01 92 d2             / 00 00 06 00 01 00 00 00 dd 00
ff 08 5000 a8 06 01 92 dc             / 00 04 00 00 bf 05 00 01 00 00
ff 08 5000 a5 06 03 12 05             / 4d 27
ff 08 5022 a9 01 00 9a 01             / 00 00 11 04
```

- **Established:** the tool reads the hour and start counters as one block of 8 EEPROM bytes at
  `0x01e6`. With the `.SYC` addresses (`EEA_H_PON` `0x01e6`, `EEA_H_BON` `0x01e9`, `EEA_N_ZUE`
  `0x01eb`, next symbol at `0x01ee`) the block is exactly 3 + 2 + 3 bytes.
- **Established:** `EEA_H_PON` is an hour counter, low byte first. Its first byte went from `5c`
  to `5d` between the two reads, the other bytes did not change: 87 132 h, then 87 133 h.
- **Established:** `with service interval (P70)` 4000 h is the EEPROM byte at `0x24` (`28` = 40)
  times 100.
- Consistent, not compared with a display: `EEA_H_BON` = `da 4e` = 20 186 h, `EEA_N_ZUE` =
  `5a db 02` = 187 226, `EEA_N_PON` (`0x01da`, 3 bytes) = `dd 00 00` = 221. The low bytes agree
  with the earlier 1-byte reads of the deployed configuration (90 and 216, now 92/93 and 218).
- The fault counters are read as 2-byte values in the area `0x0196` … `0x01e5`. The one already
  defined, `FaultCountW47` at `0x01a4`, reads `06 00` here as it does through ebusd.
- Not matched: `I46` -19752 (no telegram carries it; the `50 22` service-hours read through
  ebusd returned 430 during the session); `I44` showed 1.0 before `Read` and 11.0e after.
- Not verified: the split 3 + 2 + 3 against a displayed value; byte order of `EEA_H_BON`,
  `EEA_N_ZUE`, `EEA_N_PON` (assumed as for `EEA_H_PON`); labels of the counters between `0x0196`
  and `0x01e5` other than `FaultCountW47`.

### 15:56 — boiler automat A, tab "Error history"

Five telegrams, 10 EEPROM bytes each, `0x0200` … `0x0231`:

```
ff 08 5000 ec 06 02 92 00 / 31 02 8c 06 2a 64 5e 2f c6 27
ff 08 5000 e6 06 02 92 0a / 8c 06 1f 39 5e 3d 8d 42 8c 06
ff 08 5000 f8 06 02 92 14 / 22 3c 5e 3b 93 46 8c 06 2f 48
ff 08 5000 f2 06 02 92 1e / 5e 42 ad 47 0b 00 27 32 69 42
ff 08 5000 c4 06 02 92 28 / 00 47 8c 08 2c 64 5e 31 00 28
```

Layout: 2 bytes at `0x0200` (`31 02`, not decoded), then six records of 8 bytes from `0x0202`.
The record at `0x0202` is "Error 6" on screen, the one at `0x022a` is "Error 1".

| Byte | Label on screen | Codec deduced |
|---|---|---|
| 0 | Error code | bit 7 set = warning (`W`), clear = fault (`F`); bits 0–6 = number, shown as two digits (`8c` = `W1 2`, `0b` = `F1 1`) |
| 1 | I10: Operating phase | UCH |
| 2 | I11: Load setting | UCH, % |
| 3 | I22: Set speed PWM pump | UCH, % |
| 4 | I30: Boiler temperature | UCH, °C |
| 5 | I31: Flue gas temperature | UCH, °C |
| 6 | I32: Ionisation signal | UCH, 0.1 |
| 7 | I37: Return temperature | UCH, °C |

All 48 values on screen match:

| Screen | Address | Bytes | Code | I10 | I11 | I22 | I30 | I31 | I32 | I37 |
|---|---|---|---|---|---|---|---|---|---|---|
| Error 1 | `0x022a` | `8c 08 2c 64 5e 31 00 28` | W1 2 | 8 | 44 | 100 | 94 | 49 | 0,0 | 40 |
| Error 2 | `0x0222` | `0b 00 27 32 69 42 00 47` | F1 1 | 0 | 39 | 50 | 105 | 66 | 0,0 | 71 |
| Error 3 | `0x021a` | `8c 06 2f 48 5e 42 ad 47` | W1 2 | 6 | 47 | 72 | 94 | 66 | 17,3 | 71 |
| Error 4 | `0x0212` | `8c 06 22 3c 5e 3b 93 46` | W1 2 | 6 | 34 | 60 | 94 | 59 | 14,7 | 70 |
| Error 5 | `0x020a` | `8c 06 1f 39 5e 3d 8d 42` | W1 2 | 6 | 31 | 57 | 94 | 61 | 14,1 | 66 |
| Error 6 | `0x0202` | `8c 06 2a 64 5e 2f c6 27` | W1 2 | 6 | 42 | 100 | 94 | 47 | 19,8 | 39 |

Not verified: whether the six records are a ring (the newest was at the highest address in this
capture) and what the two bytes at `0x0200` mean; the second automat; temperatures below 0 °C.

### 15:58 — boiler automat A, tab "Process values WTC"

The screen stayed empty and the tool sent no telegram for it. Nothing to match.

### 15:59 — end

Five more `50 00` reads to `08` were grabbed between 15:58:29 and 15:59:19, with no screenshot
(EEPROM `0x02`–`0x0d`, `0x0e`–`0x18`, `0x1b`–`0x1d`, `0x25`, `0x2d`, `0x2e`, `0x0300`–`0x0304`).
They are reads by the grammar above, and the bytes at `1b`, `1c`, `1d`, `25`, `2d`, `2e` equal
those of the 15:51 blocks. Which screen issued them is not known.

After the tool was disconnected, two snapshots 11 s apart showed no new telegram with `QQ=ff`.

### What phase 2 changes

- Lot D: the request format is no longer uncertain. A `50 00` read is a list of
  `<code> <address>` items; the counters are 3-, 2- and 3-byte values at `0x01e6`, `0x01e9`,
  `0x01eb`, low byte first for `EEA_H_PON`. Missing for the evidence bar: one independent
  figure for burner hours or burner starts (boiler display, service record).
- Lot E: the automat fault history is fully decoded (6 records × 8 bytes at `0x0202`), each
  field checked against the tool's screen.
- Lot A: register 13 is the de-couple sensor B22; `SupplyWTCTemp` should be renamed. The tool
  reads the system manager with `09 02` and no CRC, where lot A uses `50 22` with a CRC; both
  return the same values.

## Session 2 — second boiler and data logger

Date: 2026-11-16, 17:11–17:45. Same method. The tool sent no write; nothing else sent as `ff`.
Every boiler window of the tool opens with an error box of the program itself (access
violation in the executable, both builds, also in Windows compatibility mode). This is the
likely reason why some of its screens stay empty although the requests go out and are answered.

### 17:13 — boiler automat B, window opened on tab "Error history"

Device: WTC automat at `18`, scanned `SW=1104;HW=0501` (window title `WCM-CPU-R5#B WTC 250 H 11.0e`).

```
ff 18 5000 ec 06 02 92 00 / 09 02 24 00 00 00 14 14 00 14
ff 18 5000 e6 06 02 92 0a / 24 00 00 00 4e 44 00 4e 24 00
ff 18 5000 f8 06 02 92 14 / 1b 32 49 35 00 42 24 00 1c 32
ff 18 5000 f2 06 02 92 1e / 4d 3a 00 48 24 00 1c 32 45 33
ff 18 5000 c4 06 02 92 28 / 00 3d 24 00 00 00 18 14 00 1a
```

The order on screen was predicted before the screen was opened, from the slots read through
ebusd and the pointer `0x0209` (last byte of slot 1). The screen showed exactly that:

| Screen | Slot | Code | I10 | I11 | I22 | I30 | I31 | I32 | I37 |
|---|---|---|---|---|---|---|---|---|---|
| Error 1 | 1 | F3 6 | 0 | 0 | 0 | 20 | 20 | 0,0 | 20 |
| Error 2 | 6 | F3 6 | 0 | 0 | 0 | 24 | 20 | 0,0 | 26 |
| Error 3 | 5 | F3 6 | 0 | 28 | 50 | 69 | 51 | 0,0 | 61 |
| Error 4 | 4 | F3 6 | 0 | 28 | 50 | 77 | 58 | 0,0 | 72 |
| Error 5 | 3 | F3 6 | 0 | 27 | 50 | 73 | 53 | 0,0 | 66 |
| Error 6 | 2 | F3 6 | 0 | 0 | 0 | 78 | 68 | 0,0 | 78 |

- **Established:** the history is a ring. The slot that ends at the pointer is "Error 1"; older
  entries follow downwards, wrapping from slot 1 to slot 6. Seen with two pointer positions
  (`0x0231` on A, `0x0209` on B).

The window also read the parameter block when it opened (as on A, so those reads belong to the
window, not to a tab). EEPROM `0x1b`–`0x4a` is identical on both automats. In `0x4b`–`0x51`
three bytes differ: `0x4c` = `01` (A) / `02` (B), probably P12 boiler address; `0x4e` = `55` /
`45`; `0x51` = `b8` / `c8`, probably a checksum.

### 17:14 — boiler automat B, tab "Statistic" (`Read`)

Same 11 requests as on A. The screen again showed only `I44`, `I45`, `I46` (-19659) and P70.

```
ff 18 5000 9c 06 01 72 e6 06 00 02 24 / ed 43 01 52 4e 09 1f 02 | 28
ff 18 5000 a5 06 03 12 05             / 4c ca
ff 18 5000 a6 06 01 92 d2             / 00 00 05 00 03 00 00 00 e2 00
```

Cross-check of the burner hours (`EEA_H_BON`, 2 bytes at `0x01e9`, low byte first):

| | Automat A | Automat B |
|---|---|---|
| `EEA_H_BON` from the bus | `da 4e` = 20 186 | `52 4e` = 20 050 |
| `I46` shown by the tool | -19 752 | -19 659 |
| sum | 434 | 391 |
| `BurnerServiceHours` (`50 22`, read through ebusd) | 430 | 390 |

- **Established:** `EEA_H_BON` is a 2-byte value, low byte first. The tool's `I46` plus this
  value gives the hours since the last service, which an independent `50 22` read returns in
  steps of ten. The value for B (390) was predicted from the sum before it was read.
- The two bytes at `0x0305` (`4d 27` on A, `4c ca` on B), high byte first, are 19 751 and
  19 658: the bitwise complement of what the tool displays as `I46`, and one less than
  `EEA_H_BON` minus the sum above. Probably the burner hours stored at the last service; the
  byte order is the opposite of the counters. Not used in a definition.
- Automat B: `EEA_H_PON` = `ed 43 01` = 82 925 h, `EEA_N_ZUE` = `09 1f 02` = 139 017,
  `EEA_N_PON` = `e2 00 00` = 226.

### 17:30 — data logger on boiler automat A

When the logger started, the tool read the counters of A again:

| Counter | 15:53 | 15:55 | 17:30 |
|---|---|---|---|
| `EEA_H_PON` (`0x01e6`, 3 bytes) | 87 132 | 87 133 | 87 134 |
| `EEA_H_BON` (`0x01e9`, 2 bytes) | 20 186 | 20 186 | 20 187 |
| `EEA_N_ZUE` (`0x01eb`, 3 bytes) | 187 226 | 187 226 | 187 230 |

- **Established:** all three step upwards by their first byte: low byte first. Four more burner
  starts and one more burner hour in about 95 minutes.
- Not verified: `EEA_N_ZUE` and `EEA_N_PON` against any displayed figure.

With 20 channels selected (first 20 of the list), the tool polls about every 2 s:

```
ff 08 5000 a8 01 27 11 62 01 68 01 6a 01 6c / ad | 40 3d | 41 | d8 | 0c
ff 08 5000 12 03 77 03 7c 03 d5 03 de       / ff | d8 | 00 | 00
ff 08 5000 fd 11 6e 01 77 01 7e 01 ed       / 00 08 | 00 | 00 | 00
ff 18 5000 7b 01 27                         / ad
```

Matched to the chart (values read off the curves, so approximate):

| Channel | Chart | Address | Byte |
|---|---|---|---|
| Sup. act (NTC) B12 | about 65 °C | RAM `0x68` | `41` = 65 |
| RL B13 | about 64 °C | RAM `0x62` | `40` = 64 |
| Flue gas temp. | 63, falling to 61 °C | RAM `0x63` | `3d` = 61, later `3b` |
| Outdoor temp. | about 12 °C | RAM `0x6c` | `0c` = 12 |

Channel selection reduced to one channel, then to the ten channels not selected before:

| Selection | Request | Answer | Symbol known to the running ebusd |
|---|---|---|---|
| Sup./Mod setpoint | `ff 08 5000 32 01 6e` | `00` | `TVSOLL` |
| PWM pump | `ff 08 5000 b1 01 ed` | `00` | `PUHZPWM` |
| Speed act. | `ff 08 5000 2b 01 77` | `00` | `NGIST` |
| .MFA1, .MFA2, VA, Ignition, Valve 1, Valve 2, Pump, Lockout, Sup. act. (eSTB), Modgrad | `ff 08 5000 16 01 2b 01 5e 01 65 03 b2` | `70 | 42 | 00 | 17` | |

- The three single selections were made one after the other without a snapshot in between and
  all returned 0 (burner off). Each request is assigned to its channel by the symbol name, not
  by timing.
- Ten channels need four reads: the eight on/off channels are bits of one or two bytes.
  Candidates: `Sup. act. (eSTB)` = RAM `0x5e` (`42` = 66 °C, one degree from B12) and `Modgrad`
  = area `3` at `b2` (`17` = 23 %, the minimum boiler rating P36; the same byte is in the cascade
  poll of session 1).
- Not matched: DHW actual B3, De-couple temp. B11, Speed set, Io actual, 0-10V N1, PWM fan
  against RAM `0x6a`, `0x7e` and area `3` at `77`, `7c`, `d5`, `de`. Two of these bytes are `d8`
  (-40 as a signed byte), as expected for the two sensors that are not fitted.
- Not established: which symbol list area `3` is.

No telegram with `QQ=ff` after 17:45.

### What session 2 changes

- Lot E: the ring order is proven on both automats; the last open point of
  `evidence/bc-fault-history.md` about the second boiler is closed.
- Lot D: burner hours have their independent figure, on both automats. Operating hours and
  burner starts behave as low-byte-first counters. Still without an independent figure: the
  number of burner starts and the number of mains-on.
- Later lot: live values of the automat (temperatures, setpoint, fan, pump, inputs and outputs)
  are RAM reads with the same `50 00` grammar. The channel table of the tool and the symbol
  table give the addresses; four channels are matched on the bus so far.

