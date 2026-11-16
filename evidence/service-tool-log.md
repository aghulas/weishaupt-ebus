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

Not started.
