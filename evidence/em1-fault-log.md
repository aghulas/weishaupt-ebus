# em1 — fault log (read)

## What

Read-only fault-log registers on heating module #1 (circuit `em1`, target 0x50), `PBSB 50 22`,
ID `<crc> <addr> <sub>` with the precomputed CRC (see [register-crc.md](register-crc.md)), in
`src/wolf/50..em1.tsp`. `ErrorId` selects the entry (0 = most recent); the other fields return
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
