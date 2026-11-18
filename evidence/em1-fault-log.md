# em1 — fault log (read)

## What

Read-only fault-log registers on heating module #1 (circuit `em1`, target 0x50), `PBSB 50 22`,
ID `<crc> <addr> <sub>` with the precomputed CRC (see [register-crc.md](register-crc.md)), in
`src/wolf/50.w.em1.tsp`. `ErrorId` selects the entry (0 = most recent); the other fields return
that entry's code, source and timestamp.

| message | addr sub | id | codec | live value |
|---|---|---|---|---|
| ErrorId | 9a 0b | `ab9a0b` | UIN | 0 |
| ErrorCode | 9b 0b | `f79b0b` | UIN | 0 |
| ErrorType | 9c 0b | `3f9c0b` | UIN | — |
| ErrorDevice | 9d 0b | `639d0b` | UIN | 1 |
| ErrorMinute | 9f 0b | `db9f0b` | UIN min | 30 |
| ErrorHour | a0 0b | `c7a00b` | UIN h | 3 |
| ErrorDay | a1 0b | `9ba10b` | UIN | 7 |
| ErrorMonth | a2 0b | `7fa20b` | UIN (enum) | November |
| ErrorYear | a3 0b | `23a30b` | UIN | 26 |

## How it was established

Live bus, ebusd `read` of each message. Entry 0 (most recent) read back a coherent record:
device 1, dated **7 November 2026, 03:30**, code 0. CRCs computed by the verified routine;
the service-hours register `bc 02` cross-checks the routine (CRC `0a`, matching the captured
frame `0a bc 02`).

Toolchain: `tsp compile`, `tsp format --check`, `ebusd --checkconfig` all clean (0 errors).

## Bytes of the nine registers (2026-11-18)

The table of "What" gives values without bytes. On 2026-11-18, between 10:27:11 and 10:27:36,
each register was read once, read-only, with the `hex` command of ebusd (source `31`,
`50 5022 03 <request>`, three seconds apart); answer after the length byte `02`:

| message | request | answer | value |
|---|---|---|---|
| ErrorId | `ab 9a 0b` | `00 00` | 0 |
| ErrorCode | `f7 9b 0b` | `00 00` | 0 |
| ErrorType | `3f 9c 0b` | `0a 00` | 10 |
| ErrorDevice | `63 9d 0b` | `01 00` | 1 |
| ErrorMinute | `db 9f 0b` | `1e 00` | 30 |
| ErrorHour | `c7 a0 0b` | `03 00` | 3 |
| ErrorDay | `9b a1 0b` | `07 00` | 7 |
| ErrorMonth | `7f a2 0b` | `0b 00` | November |
| ErrorYear | `23 a3 0b` | `1a 00` | 26 |

The same entry as on 2026-11-16 (device 1, 7 November 2026, 03:30, code 0). `ErrorType` reads
10; the first reading recorded no value for it.

## Equipment

Kromschröder WCM-FS heating module on eBUS, `MF=Kromschröder`.

## Date

2026-11-16.

## Not verified

- Only entry 0 was read. Browsing older entries needs a write to `ErrorId` (a later, write lot).
- `ErrorType`, `ErrorCode`, `ErrorDevice` value meanings (enumerations) are not decoded here;
  they were 0/1 with no active fault.
- Boiler operating/burner hours (`EEA_H_PON` / `EEA_H_BON`) are `50 00` EEPROM-memory reads,
  not `50 22`; they belong to the raw memory-map lot, not this one.

## Also in this lot — boiler service hours

`BurnerServiceHours` (the i46 maintenance counter; the comment said i45 until 2026-11-17, the service tool and the boiler manual, document 83251704 page 47, number it i 46) is a `50 22` read on the boiler itself
(circuit `bc1`, target 0x08, `src/wolf/08.w.bc1.tsp`), ID `0abc02` (addr `bc 02`, CRC `0a`,
which matches the captured frame `0a bc 02`). Read live: **430 h**. Codec `UIN h`.
`ebusd --checkconfig` clean.
