# Boiler automat firmwares: which share the memory layout of the boiler files

## What

The vendor service tool reads a boiler automat's memory through the symbol table of its
firmware, one `.SYC` file per firmware family (36 files, [vendor-software-analysis.md](vendor-software-analysis.md)).
This record compares, table by table, every memory address the boiler files `08.w.bc1.SW1104` /
`18.w.bc2.SW1104` read with the symbol the vendor tables put there, and says which automat
software gets which table. It also identifies the table of the WTC 25-A of the second
installation and checks it against the EEPROM block read there
([second-installation-ebus2mqtt.md](second-installation-ebus2mqtt.md), section 7).

**No definition is changed by this record.** It is static analysis of vendor files plus one
third-party read.

Short answer:

- An automat of hardware generation 5 gets the table `WH` + its major software byte + `928`.
  `WH11928` (our automats, software 11.04) is the only table for every software 11.xx.
- `WH10928` (software 10.xx) has every symbol at the same address, except three live XRAM bytes
  (burner load, ionisation, fan set speed), one byte lower.
- `WH00928`, `WH01928`, `WH02928`, `WH90928`, `WH91928` keep the parameter block, the counters
  and the fault history; they differ in the first ten fault counters, in two of the four
  temperatures and in five of the six live bytes.
- The other 29 tables are other boards (`00…360`–`367`, `…370`): nearly nothing matches.
- The WTC 25-A (software 03.15, hardware 03.01) gets `0003362`. Its RAM-to-EEPROM rule follows
  from its constants; under it the twelve bytes read from `0x1b` decode to in-range parameters, and
  `0x20` / `0x21` hold the minimum and maximum pump rating that the third party reads there
  and sees on the display (P42 / P43, 60 % / 70 %). The vendor table and an independent bus read
  agree on two bytes; the layout of that family is supported, not established.

## How it was established

### 1. From the scan answer to the table

Read from the dispatch routine of the diagnosis program's main form (`dispatch.asm`, the
extracted disassembly) and from the program's constant strings, with the intact executable of
the installer (static reading only).

The routine works on a copy of the identification answer. Four bytes of it are used:

| Byte of the copy | Use in the code | Taken to be |
|---|---|---|
| first | the two characters of the file name (both nibbles as hex digits, a routine that turns a byte into two hex characters); the major part of the version label | software, major byte |
| second | the minor part of the version label: high nibble as a decimal digit, then a letter `a` + low nibble (`04` → `0e`) | software, minor byte |
| third | board choice: compared with 1, 3, 4, 5, `0x50` (oil), `0x51` (oil, other series) | hardware, major byte |
| fourth | sub-choice for 3, 4 and the gas series | hardware, minor byte |

**Read from the code:** the order and use of these four bytes. **Inferred:** that they are
software and hardware of the `07 04` answer. Two facts support it: for our automats the
label the code builds is `11.0e`, the version the tool showed, from software `11 04`; and
hardware 5 gives the form of the "R5" automat, the window title noted in
[service-tool-log.md](service-tool-log.md).

Choice of the file name, in the order of the code (`SS` = the two hex characters of the major
software byte; the file is `<name>.syc`):

| Hardware major | Hardware minor | Table | Form |
|---|---|---|---|
| 1 | any | `00SS361` if the rating in the label is 45 or 60, `00SS360` if 15, 25 or 32 | `frmWCM45`, `frmWCM` |
| 2, 3, 4, other | any | `00SS362` (default) | `frmWCM362` for `0000362`, else `frmWCM362FW1` |
| any but 1 | `0x50` | `00SS363`; `00SS367` if `SS` ≥ `0a` | `frmWCM363` / `frmWCM364` |
| 4 | 0 / ≥ 1 | `00SS364` / `00SS366` | `frmWCM364` |
| 3 | 2 to `0x4f` | `00SS366` | `frmWCM364` |
| `0x50` | any | `00SS365` | oil form |
| `0x51` | any | `00SS370` if `SS` < 4, else `WHSS370` | oil form, other series |
| **5** | any | **`WHSS928`** | **`frmWCM_5`** |

The hardware-5 test comes after the others and overrides them. A test-bench case also gives
`WHSS928` (an access-level test and two fixed identification characters). What the tool does
when the file for a software byte is not shipped was not traced.

So:

- **A hardware 05.xx automat can get only `WHSS928`**, and the tool picks it from the major
  software byte alone: every 11.xx gets `WH11928`. Shipped are `WH00928`, `WH01928`, `WH02928`,
  `WH10928`, `WH11928`, `WH90928`, `WH91928`. All of them are shown with the same form, so with
  the same types, factors and masks; only the addresses come from the table.
- **Software 03.15 / hardware 03.01 gets `0003362`** with the form `frmWCM362FW1` (hardware major
  3, minor 1: not `0x50`, not 2 to `0x4f`; the name is not `0000362`).

### 2. What the boiler files read, resolved in `WH11928`

From the compiled CSV of `08.w.bc1.SW1104` (`18.w.bc2.SW1104` reads the same) and the records.
A `50 00` ID is a check byte, then items `<code> <address>`: high nibble of the code = bytes − 1,
low nibble = area (1 RAM, 2 EEPROM, 3 XRAM, low byte of the address only); `06 <high>` sets the
high byte ([bc-fault-history.md](bc-fault-history.md)).

| Message | Area, addresses | `WH11928` symbols |
|---|---|---|
| `InstallerParameters1`–`5` | EEPROM `0x1b`–`0x26`, `0x27`–`0x32`, `0x33`–`0x3e`, `0x3f`–`0x4a`, `0x4b`–`0x51`, `0x44`, `0x37`; 17 fields | RAM mirrors `MAXTVSOLL`, `MINTVSOLL`, `SONDERNIVEAU`, `WARTUNGSINTERVALL`, `NG_ZUEND`, `MXTABGAS`, `NG_HZ_MIN`, `NG_HZ_MAX`, `PUHZ_MIN`, `PUHZ_MAX`, `DT_VLRL_SOLL`, `PNL_HZ`, `TWWPLUS`, `NG_WW_MAX`, `PUHZ_WW`, `PNL_WW`, `V24_KM_ADR` |
| `FaultCounters1`–`7` | EEPROM `0x196`–`0x1d7` | `EEA_FC_57` … `EEA_FC_11` (33 counters) |
| `FaultHistoryPointer`, `FaultHistorySlot1`–`6` | EEPROM `0x200`–`0x231` | `EEA_F_HIST_PTR_LOW`, `EEA_F_HIST_ANF`, `EEA_F_HIST_END` |
| `Counters` | EEPROM `0x1e6`–`0x1ed` | `EEA_H_PON`, `EEA_H_BON`, `EEA_N_ZUE` |
| `EventCounters` | EEPROM `0x1d8`–`0x1e5` | `EEA_HBRONTAG`, `EEA_NZUENDTAG`, `EEA_N_PON`, `EEA_N_KON`, `EEA_RES_CNT`, `EEA_SHUT_OFF` |
| `Temperatures` | RAM `0x62`, `0x63`, `0x68`, `0x6c` | `TRLIST`, `TABGAS`, `TVIST`, `TAUSSEN` |
| `Operation` | XRAM `0xf0b2`, `0xf0d5`, RAM `0xed` | `MODULATIONSGRAD`, `Z_IondmueA`, `PUHZPWM` |
| `FanOperation` | XRAM `0xf0de`, RAM `0x77`, `0x7e` | `MODI_NGSOLL`, `NGIST`, `YPWM` |

The other eleven messages of the files are `50 22` registers (temperatures, the two software
versions, burner service hours) and the heat demand `05 07`. Symbol tables say nothing about
registers, so this comparison does not cover them. The files read no identification block from
memory (`EEA_BAUSTAND`, `EEA_KUNDE`, `EEA_VARIANTE`, `EEA_SERIAL_NO` are at the same addresses in
all seven `WH…928` tables, but no message reads them).

**The RAM-mirror rule.** Every table with a RAM parameter block names its start and its check
byte twice: RAM `IRAEPKANF` … `KES_DAT_CRC`, EEPROM constants `EEAEPKANF` … `EEAEPKCRC`. The rule
used is `EEPROM = RAM − IRAEPKANF + EEAEPKANF`. In all 30 tables that have the block, the block
has the same length on both sides, so `KES_DAT_CRC` lands on `EEAEPKCRC`. That is a check from the
constants, not proof that the firmware copies the block byte for byte.

- **Established** for `WH11928`: the tool's developer window names the 55 bytes `0x1b`–`0x51` one
  by one with these symbols, and the bus values equal the displayed ones
  ([bc-installer-parameters.md](bc-installer-parameters.md)). `0x1b` = `0xab − 0x90`.
- **Assumed** for every other table (the same constant pair, the same length check).

In all seven `WH…928` tables the 55 bytes of the block carry the same symbols in the same order,
and the 44 mask constants of packed bytes are the same. Only the RAM base differs (`0xab` for 10.xx
and 11.xx, `0x7e` for the others). The EEPROM start is `0x1b` in all seven.

### 3. The matrix

Each cell compares, field by field, the address of the symbol in that table with its address in
`WH11928`. **same**: every symbol of the message at the same address. **shifted**: the symbol
exists but elsewhere. **absent**: the table has no such symbol. Script: a throw-away Python
script over the extracted tables (`out/vendor-analysis/syc.json`), not versioned.

| Table (software) | `InstallerParameters1`–`5` | `FaultCounters1`–`7` | Fault history | `Counters` | `EventCounters` | `Temperatures` | `Operation` | `FanOperation` |
|---|---|---|---|---|---|---|---|---|
| `WH11928` (11.xx) | same (established) | same | same | same | same | same | same | same |
| `WH10928` (10.xx) | same | same | same | same | same | same | load, ionisation shifted −1; pump same | set speed shifted −1; actual speed, PWM same |
| `WH00928`, `WH01928`, `WH02928`, `WH90928`, `WH91928` (00, 01, 02, 90, 91.xx) | same | `1`: shifted +2 (`0x196` is `EEA_FCODE_NOT`); `2`: `EEA_FC_49` absent, `0x1a0` is `EEA_FC_51`, the other four same; `3`–`7` same | same | same | same | return, flue gas shifted (`0x7c`, `0x7d`); flow, outside same | all three shifted (load and ionisation in XRAM page `0xff`, pump `0xc0`) | set speed shifted (page `0xff`); actual speed same; PWM shifted (`0x62`) |
| 23 tables `00SS360`–`00SS367` (other boards, among them `0003362`) | 9 or 12 of 17 symbols absent, the rest shifted | 1 to 15 of 33 absent, the rest 226 to 255 bytes lower | absent (history elsewhere, other symbols) | shifted −248 to −251, or 2 of 3 absent | shifted, or 2 of 6 absent | 1 to 3 of 4 absent, the rest shifted | absent or shifted | absent or shifted |
| 6 tables `00SS370`, `WH04370` (oil series) | absent (no RAM parameter block) | absent | absent | 1 of 3 absent, the rest shifted | 5 of 6 absent | absent | absent | absent |

In `WH10928` the `WH11928` addresses `0xf0b2`, `0xf0d5`, `0xf0de` hold `SECBROFF`, `Z_IonOffdmueA`,
`MERK_NG_RAMPE`: a 10.xx automat would answer `Operation` and `FanOperation` with other values
in those three fields. The lengths implied by the next symbol (counters 3 + 2 + 3 bytes, event
counters, the 50-byte history) are the same in all seven `WH…928` tables.

### 4. The WTC 25-A: table `0003362`

**Its rule.** `IRAEPKANF` = RAM `0x80`, `EEAEPKANF` = EEPROM `0x17`; `KES_DAT_CRC` = RAM `0xa5`,
`EEAEPKCRC` = EEPROM `0x3c`. So `EEPROM = RAM − 0x69` for `0x17`–`0x3c`. A second block gives the
same picture (`IRAEPMANF` `0xa6` … `MAINPARACRC` `0xac` against `EEAEPMANF` `0x3d` … `EEAEPMCRC`
`0x43`). In this family P31 (`MAXTVSOLL`) is at `0x17` and P30 (`MINTVSOLL`) at `0x37`.

**Against the third-party block** (`31 08 50 00 03 df b2 1b`, answer after the status byte
`82 51 51 99 83 3c 46 60 14 ff 04 00`), decoded with the type, mask, factor and offset of the
form `frmWCM362FW1` for each symbol (our own short descriptions of the vendor captions):

| EEPROM | Byte | Symbol (RAM) | Parameter, form range | Decoded |
|---|---|---|---|---|
| `0x1b` | `82` | `HZ_KTND` (`0x84`), masks `07` / `f8` | A2 flow controller I part, 1–7; A3 D part (× 2), 0–63 | 2; 32 |
| `0x1c` | `51` | `NG_KESSEL_MIN` (`0x85`) | P36 minimum boiler rating, × 0.390625 + 0.39, 19.9–100 % | 32 % |
| `0x1d` | `51` | `NG_HZ_FREI` (`0x86`) | A11 delayed start rating, same scale | 32 % |
| `0x1e` | `99` | `NG_HZ_MAX` (`0x87`) | P37 maximum rating, heating, same scale | 60 % |
| `0x1f` | `83` | `PNL_HZ` (`0x88`), masks `80` / `40` / `3f` | P40 pump continuous run 0–1; P21 building type 0–1; P41 pump run-on, heating, 1–60 min | 1; 0; 3 min |
| `0x20` | `3c` | `PUHZOFFS` (`0x89`) | **P42 minimum pump rating, 20–99 %** | **60 %** |
| `0x21` | `46` | `PUHZSTEIG` (`0x8a`) | **P43 maximum pump rating, 21–100 %** | **70 %** |
| `0x22` | `60` | `WW_HYS` (`0x8b`), masks `f8` / `07` | P45 pump rating, hot water (× 5), 20–100 %; P51 hot-water switching difference (−3 − value), −10 to −3 K | 60 %; −3 K |
| `0x23` | `14` | `TWWPLUS` (`0x8c`) | P50 hot-water excess, 10–30 K | 20 K |
| `0x24` | `ff` | `NG_WW_MAX` (`0x8d`) | P38 maximum rating, hot water, × 0.390625 + 0.39 | 100 % |
| `0x25` | `04` | `IO_KORR` (`0x8e`), signed | P39 O2 correction, × 0.1, −0.5 to 1.0 | 0.4 |
| `0x26` | `00` | `V24_KM_ADR` (`0x8f`) | boiler address in a cascade, 0–5 | 0 (single boiler) |

- **Pump minimum / maximum land on `0x20` / `0x21`**: yes. The form names them P42 / P43, the
  numbering the third party uses for that boiler. They read 60 and 70 on the display and saw
  `0x21` follow a write of P43 (their test; not repeated here, rule 7).
- **The other ten bytes** all decode inside the range the form gives their parameter. Nothing
  else is known for that boiler, so none of the ten is confirmed. The masks are the table's
  constants, the scales the form's.
- What our `InstallerParameters1` would show there: `SupplyMaxTemp` 130 °C (`HZ_KTND`),
  `SupplyMinTemp` 81 °C (`NG_KESSEL_MIN`), `SpecialLevelTemp` 96 °C (`WW_HYS`), `ServiceInterval`
  25 500 h (`NG_WW_MAX`), `IgnitionLoad` 0 % (`V24_KM_ADR`). Of the 17 fields, twelve land on
  other parameters of the block, `DHWBoostTemp` on its check byte, three on user settings of the
  next block (summer / winter changeover, hot-water setpoint, room day temperature) and
  `BoilerAddress` outside both. Limiting the files to software 1104 was right for this automat.

**Verdict.** The vendor table and an independent bus read agree on the two bytes that can be
compared, and every other byte of the read is plausible under the table. That supports the
layout of `0003362` for `0x17`–`0x3c` on this automat; it does not establish it field by field.
Two more bytes are already predicted. The third party also read `e3 b2 27` and `f7 b2 33`. If
the table is right, `0x2e` (`TAUSSEN_KORR`, signed) holds `ff` = −1 K, their P20 by the `50 03`
slot read, and `0x37` (`MINTVSOLL`) holds `29` = 41 °C, their P30 by the slot read.

### 5. Parameter ranges of the WTC 15-A … 32-A manual

Installation manual of the WTC 15-A … 32-A, 83053005, edition 07/2005, pp. 42–44 (automat
generation 3.x; the addenda 83172004 describe it; software `0315` is likely in it, not
established). Read on the vendor's partner portal on 2026-11-27
([vendor-documentation.md](../docs/vendor-documentation.md), sections 1 and 6). The manual gives
numbers, ranges and factory values, no EEPROM address. Against the form ranges and the decoded
third-party block of section 4, and against the WTC-GB numbering of our files:

| Number | Meaning on a WTC 15-A … 32-A | Range, factory value (83053005) | Decoded on the WTC 25-A (section 4) | WTC-GB (our files) |
|---|---|---|---|---|
| P20 | outside temperature correction | −4 … +4 K, factory 0 (p. 42) | predicted `0x2e` = `ff`, −1 K: in range | same role |
| P21 | building type (light / heavy) | 0 / 1, factory 0 (p. 42) | 0 | – |
| P30 | minimum flow setpoint | 8 … (P31 − P32) °C, factory 8 (p. 43) | predicted `0x37` = `29`, 41 °C: in range | same role |
| P36 | minimum boiler rating | 33 … 100 %, on the WTC 25 32 … 100 %, factory 32 (p. 43, note 2 on p. 44) | 32 %: the WTC 25 factory value | other numbering |
| P37 | maximum boiler rating, heating | 33 … 100 % (WTC 25: 32 … 100 %), factory 100 | 60 %: in range, set on site | other numbering |
| P38 | maximum boiler rating, hot water | same range, factory 100 | 100 %: factory | other numbering |
| P39 | O2 correction | −0.5 … +1 %-points, factory 0 | 0.4: in range | other numbering |
| P40 | boiler pump in heating: run-on 0, continuous 1 | 0 / 1, factory 0 | 1 | other numbering |
| P41 | pump run-on, heating | 1 … 60 min, factory 3 | 3 min: factory | other numbering |
| P42 | minimum pump speed (PWM pump) | 20 … P43 %, factory 30 | 60 %, the display's value | hot-water pump run-on |
| P43 | maximum pump speed (PWM pump) | P42 … 100 %, factory 60 (WTC 25: 70, note 3 on p. 44) | 70 %: the WTC 25 factory value | other meaning |
| P44 | flow adjustment with a hydraulic separator (PWM pump) | 0 … 7 K or off, factory 4 | – | `IP2.pumploadmin` (pump rating minimum) |
| P45 | pump rating, hot water (PWM pump) | 20 … 100 %, factory 60 | 60 %: factory | pump rating maximum |
| P50 | flow excess for a hot-water load | 10 … 30 K, factory 20 | 20 K: factory | other numbering |
| P51 | hot-water switching difference | −1 … −10 K, factory −3 | −3 K: factory | other numbering |

Also listed with range and factory value, not compared: P10–P18, P22, P23, P31–P35, P52, P53,
P60–P62, P70–P72 (pp. 42–44).

- **Every compared byte is inside the manual's range**, and seven of them hold the factory value
  of a WTC 25 (P36, P38, P41, P43, P45, P50, P51). That is a second, independent support for
  the layout of `0003362` on that automat, from a vendor page rather than the program's forms.
- **Where the manual and the form differ**: P51 is −1 … −10 K in the manual and −10 … −3 K in
  the form (its scale stores −3 − value); P36 starts at 32 % on a WTC 25 in the manual, at 19.9 % in
  the form. A file for that boiler declares the manual's ranges, not the
  form's.
- **The false match**: P42 is the minimum pump speed here and the hot-water pump run-on on a
  WTC-GB (the false match of `docs/design-vendor-codes.md`), P44 / P45 are other settings again. This
  page is the vendor source for that warning.
- This is the range source a future WTC 25-A file (`08.w.<circuit>.SW0315`) would cite. It does
  not replace the evidence that file still needs (Recommendation).

## Equipment

- Here: two WTC-GB automats, scan `W`, software `1104`, hardware `0501` (table `WH11928`).
- Compared: a WTC 25-A automat, scan `W`, software `0315`, hardware `0301` (table `0003362`),
  third-party data.
- Vendor diagnosis program 5.5.19 (installer copy, intact), its 36 symbol tables; nothing run.

## Date

2026-11-27.

## Recommendation

No definition changes with this record.

1. **Known limits, 1.4.0** (drafted in `docs/release-readme.md`, under "software 1104 only"):
   from the vendor tool's tables, every 11.xx automat uses the same memory layout, 10.xx the same
   except three live bytes, earlier versions differ in several messages, and the WTC 25-A uses
   another table.
2. **Widening the files: not now.** ebusd's file-name qualifier takes one exact software number,
   so covering 11.xx would mean one copy of each file per version, for versions nobody has
   reported. The memory part would be backed by the vendor table, but the `50 22` registers
   would not (the tables do not cover registers). The way to cover a range is a scan condition
   on `bc1` / `bc2`: ebusd's condition values accept ranges (`splitValues` in
   `src/lib/ebus/message.cpp`: `1100-1199`, `<1200`). It would need: the fix of
   `MessageMap::resolveFills` in `aghulas/ebusd`, so that `fills` to an unavailable message no
   longer fail `--checkconfig` (the reason the condition was dropped,
   [bc-automat-software.md](bc-automat-software.md)); the file name without `.SW1104`; and, under
   rule 3, at least one scan answer and one read of an automat with another 11.xx software. 10.xx
   would need three fields of `Operation` / `FanOperation` per version on top. Until a user
   reports such an automat, the exact `SW1104` stays.
3. **A WTC 25-A file: possible later, not on this evidence.** It would be a file of its own
   (`08.w.<circuit>.SW0315`, from table `0003362`), not a variant of ours. Rule 3 still needs, from
   that boiler: the other three blocks the third party already read (`e3 b2 27`, `f7 b2 33`,
   `fb b2 3f`) to test the two predictions above and decode the rest; a display or `50 03` value for
   each parameter put in a field, with at least one set differently from its default (as for our
   files); the history, counters and live values of that family, which this record does not map
   (other symbol names, `EEAHIST_*` from `0x100`); and its `50 22` registers, if any. A second
   WTC 15/25-A, or a value changed by its operator, would turn "supported" into "established".

## Not verified

- **Static analysis.** The tables and forms say what the tool plans to read, not what a device
  answers. The RAM-mirror rule is established on `WH11928` only and assumed elsewhere.
- **No automat with software 10.xx, 00–02.xx or 9x.xx was ever read**, here or by anyone cited.
- That the four bytes the dispatch code uses are those of the `07 04` answer (inferred, section 1),
  and what the tool does when the table for a software byte is not shipped.
- The board codes `360`–`370` are read only as far as needed for hardware 5 and 03.01; the
  branches for hardware 1 depend on a rating in the label and were not followed further.
- The WTC 25-A block is third-party data, one read, decoded here by hand; only `0x20` / `0x21`
  are compared with an independent value.
