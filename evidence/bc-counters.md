# bc1, bc2 — boiler counters (read)

## What

Counters of the WTC boiler automat, one memory read `PBSB 50 00` of EEPROM `0x01e6`–`0x01ed`,
in `src/wolf/08.w.bc1.tsp` (target `08`), `src/wolf/18.w.bc2.tsp` (target `18`) and the shared
model `Counters` of `src/wolf/wtc_inc.tsp`.

| message | ID | answer after the status byte |
|---|---|---|
| Counters | `26 06 01 72 e6` | 8 bytes |

| Bytes | Field | Codec |
|---|---|---|
| 0–2 | OperatingHours (hours with mains on) | U3N, h |
| 3–4 | BurnerHours | UIN, h |
| 5–7 | BurnerStarts | U3N |

## How it was established

**Request.** The vendor service tool (WCM-Diagnose 5.5.19a) reads these eight bytes for its
statistics screen, as the first item of `9c 06 01 72 e6 06 00 02 24` (format of a `50 00` read:
see [bc-fault-history.md](bc-fault-history.md)). ebusd refuses an ID that long, so the
definition keeps the first item only, `06 01 72 e6`, with the CRC computed by the same routine
(`26`). The same shape, `06 02 72 <address>`, is read through ebusd for the fault history.

**Field boundaries.** The symbol table of this firmware (file names and addresses only, see
`service-tool-log.md`, phase 1) places operating hours at `0x01e6`, burner hours at `0x01e9`,
burner starts at `0x01eb` and the next symbol at `0x01ee`: 3 + 2 + 3 bytes.

**Captures** (answer without its status byte; the ninth byte belongs to the tool's second item):

```
15:53  ff 08 5000 9c 06 01 72 e6 06 00 02 24 / 5c 54 01 da 4e 5a db 02 | 28
15:55  ff 08 5000 (same)                     / 5d 54 01 da 4e 5a db 02 | 28
17:30  ff 08 5000 (same)                     / 5e 54 01 db 4e 5e db 02 | 28
17:14  ff 18 5000 (same)                     / ed 43 01 52 4e 09 1f 02 | 28
```

| | 15:53 | 15:55 | 17:30 | second boiler 17:14 |
|---|---|---|---|---|
| OperatingHours | 87 132 | 87 133 | 87 134 | 82 925 |
| BurnerHours | 20 186 | 20 186 | 20 187 | 20 050 |
| BurnerStarts | 187 226 | 187 226 | 187 230 | 139 017 |

- Byte order: each counter steps upwards by its first byte, the others stay. Low byte first.
- Operating hours step by one per hour of wall-clock time.
- Burner starts stepped by four while burner hours stepped by one.

**Burner hours, independent figure.** The tool's statistics screen shows `I46: Burner operation
since last service` wrongly, as a negative number. That number plus `BurnerHours` gives the
hours since the last service, which the `50 22` register `BurnerServiceHours` returns through
ebusd in steps of ten:

| | first boiler | second boiler |
|---|---|---|
| BurnerHours | 20 186 | 20 050 |
| `I46` on screen | -19 752 | -19 659 |
| sum | 434 | 391 |
| BurnerServiceHours (ebusd, `50 22`) | 430 | 390 |

The second boiler's 390 was predicted from the sum before it was read.

**Scale correction (2026-11-18, lot E).** `BurnerServiceHours` is register `bc 02`, in units of
ten hours (manual 83251704 p. 47: i 46 "Délai écoulé depuis le dernier entretien, h x 10").
Lot E first read it with a plain `UIN` and no factor, so ebusd reported 44 and 39 instead of
440 and 390 h — the message was 10× low in the 0.3.2 and 0.4.0 releases. Lot E now applies a
factor of 10 (ebusd divisor −10). The read was confirmed read-only on the live bus on
2026-11-18: `08` answers `02 2c 00` (`0x2c` = 44 → 440 h), `18` answers `02 27 00` (`0x27` =
39 → 390 h). The second boiler had no `BurnerServiceHours` message before; lot E now defines it
on both boilers.

Toolchain: `scripts/check.sh` clean (format, compile, `ebusd --checkconfig`, 161 messages).

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

- The message has not been read by ebusd itself: it is not in the running configuration, which
  still holds 1-byte reads of the same addresses (they return the first byte of each counter).
- `BurnerStarts` and `OperatingHours` have no figure from another source. The tool reads them
  but does not display them on this firmware. Their evidence is the address, the length and
  the way they count.
- The number of mains-on (`0x01da`, read 221 and 226) was not seen to change and is left out.
- Other firmware versions of the automat: the addresses come from this one.
