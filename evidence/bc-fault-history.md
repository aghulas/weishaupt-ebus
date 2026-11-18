# bc1, bc2 — boiler fault history (read)

## What

Fault history of the WTC boiler automat, read from its EEPROM with the memory read
`PBSB 50 00`, in `src/wolf/08.w.bc1.tsp` (target `08`), `src/wolf/18.w.bc2.tsp` (target `18`)
and the shared models of `src/wolf/wtc_inc.tsp`.

| message | EEPROM | ID | codec |
|---|---|---|---|
| FaultHistoryPointer | `0x0200`, 2 bytes | `1c 06 02 12 00` | UIN |
| FaultHistorySlot1 | `0x0202`, 8 bytes | `5a 06 02 72 02` | slot |
| FaultHistorySlot2 | `0x020a` | `52 06 02 72 0a` | slot |
| FaultHistorySlot3 | `0x0212` | `4a 06 02 72 12` | slot |
| FaultHistorySlot4 | `0x021a` | `42 06 02 72 1a` | slot |
| FaultHistorySlot5 | `0x0222` | `7a 06 02 72 22` | slot |
| FaultHistorySlot6 | `0x022a` | `72 06 02 72 2a` | slot |

The answer starts with the first byte (`00` here, kept as the field `FirstByte`, see below).
A slot is 8 bytes:

| Byte | Field | Codec |
|---|---|---|
| 0, bits 0–6 | Number | fault number |
| 0, bit 7 | Kind | 0 = fault (F), 1 = warning (W) |
| 1 | OperatingPhase | UCH, same value list as the status broadcast |
| 2 | Load | UCH, % |
| 3 | PumpSpeed | UCH, % |
| 4 | BoilerTemp | UCH, °C |
| 5 | FlueGasTemp | UCH, °C |
| 6 | Ionisation | UCH, divisor 10 |
| 7 | ReturnTemp | UCH, °C |

The six slots form a ring. `FaultHistoryPointer` is the address of the last byte written: the
slot ending there is the most recent fault.

## How it was established

**ID format.** A `50 00` read is the CRC-8 (poly 0x5C, same routine as
[register-crc.md](register-crc.md)) followed by items `<code> <address>`: high nibble of the
code = number of bytes minus one, low nibble = memory area (`2` = EEPROM), code `06` = high
byte of the address. Established from the telegrams of the vendor service tool
(`service-tool-log.md`, 15:51). The CRC routine reproduces the first byte of ten captured
`50 00` requests, among them `ec 06 02 92 00`, `9c 06 01 72 e6 06 00 02 24` and `df b2 1b`.

**Slot layout.** Comparison with the vendor service tool (WCM-Diagnose 5.5.19a), tab
"Error history" of the first boiler. The tool read `0x0200`–`0x0231` in five requests:

```
ff 08 5000 ec 06 02 92 00 / 31 02 8c 06 2a 64 5e 2f c6 27
ff 08 5000 e6 06 02 92 0a / 8c 06 1f 39 5e 3d 8d 42 8c 06
ff 08 5000 f8 06 02 92 14 / 22 3c 5e 3b 93 46 8c 06 2f 48
ff 08 5000 f2 06 02 92 1e / 5e 42 ad 47 0b 00 27 32 69 42
ff 08 5000 c4 06 02 92 28 / 00 47 8c 08 2c 64 5e 31 00 28
```

and displayed six columns of eight values. All 48 values equal the bytes:

| Screen | Slot | Bytes | Code | I10 phase | I11 load | I22 pump | I30 boiler | I31 flue gas | I32 ionisation | I37 return |
|---|---|---|---|---|---|---|---|---|---|---|
| Error 1 | 6 | `8c 08 2c 64 5e 31 00 28` | W1 2 | 8 | 44 | 100 | 94 | 49 | 0,0 | 40 |
| Error 2 | 5 | `0b 00 27 32 69 42 00 47` | F1 1 | 0 | 39 | 50 | 105 | 66 | 0,0 | 71 |
| Error 3 | 4 | `8c 06 2f 48 5e 42 ad 47` | W1 2 | 6 | 47 | 72 | 94 | 66 | 17,3 | 71 |
| Error 4 | 3 | `8c 06 22 3c 5e 3b 93 46` | W1 2 | 6 | 34 | 60 | 94 | 59 | 14,7 | 70 |
| Error 5 | 2 | `8c 06 1f 39 5e 3d 8d 42` | W1 2 | 6 | 31 | 57 | 94 | 61 | 14,1 | 66 |
| Error 6 | 1 | `8c 06 2a 64 5e 2f c6 27` | W1 2 | 6 | 42 | 100 | 94 | 47 | 19,8 | 39 |

`8c` = warning 12, `0b` = fault 11: bit 7 separates W from F.

**Read back through ebusd.** The messages above, sent by ebusd (source `31`) with one 8-byte
item per slot, a form the tool itself does not use for this screen:

| | Pointer | Slot 1 | Slot 2 | Slot 3 | Slot 4 | Slot 5 | Slot 6 |
|---|---|---|---|---|---|---|---|
| bc1 | 561 (`0x0231`) | W12 6 42 100 94 47 19.8 39 | W12 6 31 57 94 61 14.1 66 | W12 6 34 60 94 59 14.7 70 | W12 6 47 72 94 66 17.3 71 | F11 0 39 50 105 66 0.0 71 | W12 8 44 100 94 49 0.0 40 |
| bc2 | 521 (`0x0209`) | F36 0 0 0 20 20 0.0 20 | F36 0 0 0 78 68 0.0 78 | F36 0 27 50 73 53 0.0 66 | F36 0 28 50 77 58 0.0 72 | F36 0 28 50 69 51 0.0 61 | F36 0 0 0 24 20 0.0 26 |

bc1 returns the same six records as the tool's screen. Its pointer `0x0231` is the last byte of
slot 6, which the tool shows as "Error 1" (most recent).

**Ring.** On bc2 the pointer is `0x0209`, the last byte of slot 1. The tool's screen for the
second boiler, predicted from these reads before it was opened, shows slot 1 as "Error 1", then
slots 6, 5, 4, 3, 2 as "Error 2" to "Error 6" (`service-tool-log.md`, session 2). So the slot
ending at the pointer is the most recent, and older entries follow downwards with wrap-around.
All 48 values of that screen equal the bc2 row above.

Toolchain: `scripts/check.sh` clean (format, compile, `ebusd --checkconfig`, 159 messages).

## The seven requests as written, on both boilers (2026-11-18)

The read-back above gives values, not bytes. On 2026-11-18, between 10:27:43 and 10:28:28,
each of the seven requests was sent once to each boiler, read-only, with the `hex` command of
ebusd (source `31`, `<zz> 5000 05 <request>`, three seconds apart); answer after the length
byte, first answer byte first. Values in the order of the fields: FirstByte, then Value for
the pointer; FirstByte, Number, Kind, OperatingPhase, Load, PumpSpeed, BoilerTemp,
FlueGasTemp, Ionisation, ReturnTemp for a slot.

| boiler | message | request | answer | values |
|---|---|---|---|---|
| `08` | FaultHistoryPointer | `1c 06 02 12 00` | `00 31 02` | 0, 561 |
| `08` | FaultHistorySlot1 | `5a 06 02 72 02` | `00 8c 06 2a 64 5e 2f c6 27` | 0, 12, warning, BurnerInOperation, 42, 100, 94, 47, 19.8, 39 |
| `08` | FaultHistorySlot2 | `52 06 02 72 0a` | `00 8c 06 1f 39 5e 3d 8d 42` | 0, 12, warning, BurnerInOperation, 31, 57, 94, 61, 14.1, 66 |
| `08` | FaultHistorySlot3 | `4a 06 02 72 12` | `00 8c 06 22 3c 5e 3b 93 46` | 0, 12, warning, BurnerInOperation, 34, 60, 94, 59, 14.7, 70 |
| `08` | FaultHistorySlot4 | `42 06 02 72 1a` | `00 8c 06 2f 48 5e 42 ad 47` | 0, 12, warning, BurnerInOperation, 47, 72, 94, 66, 17.3, 71 |
| `08` | FaultHistorySlot5 | `7a 06 02 72 22` | `00 0b 00 27 32 69 42 00 47` | 0, 11, fault, BurnerOff, 39, 50, 105, 66, 0.0, 71 |
| `08` | FaultHistorySlot6 | `72 06 02 72 2a` | `00 8c 08 2c 64 5e 31 00 28` | 0, 12, warning, PostPurge, 44, 100, 94, 49, 0.0, 40 |
| `18` | FaultHistoryPointer | `1c 06 02 12 00` | `00 09 02` | 0, 521 |
| `18` | FaultHistorySlot1 | `5a 06 02 72 02` | `00 24 00 00 00 14 14 00 14` | 0, 36, fault, BurnerOff, 0, 0, 20, 20, 0.0, 20 |
| `18` | FaultHistorySlot2 | `52 06 02 72 0a` | `00 24 00 00 00 4e 44 00 4e` | 0, 36, fault, BurnerOff, 0, 0, 78, 68, 0.0, 78 |
| `18` | FaultHistorySlot3 | `4a 06 02 72 12` | `00 24 00 1b 32 49 35 00 42` | 0, 36, fault, BurnerOff, 27, 50, 73, 53, 0.0, 66 |
| `18` | FaultHistorySlot4 | `42 06 02 72 1a` | `00 24 00 1c 32 4d 3a 00 48` | 0, 36, fault, BurnerOff, 28, 50, 77, 58, 0.0, 72 |
| `18` | FaultHistorySlot5 | `7a 06 02 72 22` | `00 24 00 1c 32 45 33 00 3d` | 0, 36, fault, BurnerOff, 28, 50, 69, 51, 0.0, 61 |
| `18` | FaultHistorySlot6 | `72 06 02 72 2a` | `00 24 00 00 00 18 14 00 1a` | 0, 36, fault, BurnerOff, 0, 0, 24, 20, 0.0, 26 |

The eight data bytes of every slot of the first boiler are those the vendor tool read on
2026-11-16, and the values of both boilers are those of the read-back above: no entry was
added in two days. The names of the operating phase are those of the value list of the status
broadcast; the record of 2026-11-16 gives the number (6, 0, 8).

## First answer byte

On 2026-11-18 the first byte of every memory read (`50 00`) was made a visible field
`FirstByte` (UCH), folded into the shared base model `memr`, after an answer was seen whose
first byte was the number of bytes asked for in front of all-zero data (2 of 107 answers of
one boiler; see [bc-fault-counters.md](bc-fault-counters.md), "first answer byte"). Before that
the byte was ignored. The field adds no message and does not change the data that follows. Read
read-only on the live bus the same day: `FirstByte` is `00` and the data decode as before.

## Equipment

Two WTC condensing boilers in cascade, automat scanned `MF=Kromschroeder;SW=1104;HW=0501`
(firmware shown by the tool as 11.0e).

## Date

2026-11-16.

## Not verified

- The texts of the fault numbers. The tool's statistics screen lists some of them (for example
  `W1 2: STW Excess temperature supply`, `F3 6: Water pressure too low`); no value list is
  shipped.
- The unit of the ionisation signal. The history screen gives none.
- Temperatures below 0 °C or above 127 °C (unsigned is assumed; 105 °C was seen).
- Other firmware versions of the automat: the EEPROM addresses come from this one.
