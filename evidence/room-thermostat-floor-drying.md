# fs1, em2 — floor-drying and room-thermostat temperatures (13 0a, 1d 0a)

## What

Two heating-circuit sensor reads of the room units and heating modules, `PBSB = 50 22`, ID
`<crc> <addr> <sub>` with the `<crc>` precomputed (see [register-crc.md](register-crc.md)):

| message | addr sub | request | codec | answer | value |
|---|---|---|---|---|---|
| FloorDryingTemp | `13 0a` | `5e 13 0a` | SIN/10, °C | `00 80` | `-` (no sensor) |
| RoomThermostatTemp | `1d 0a` | `92 1d 0a` | SIN/10, °C | `00 80` | `-` (no sensor) |

Both registers answer two data bytes (`NN = 02`), low byte first, so the value is 16-bit. The
answer `00 80` is `0x8000`, the signed-integer "no value" code: ebusd decodes it as `-`. On this
installation neither a floor-drying (screed-drying) sensor nor an external room thermostat is
fitted, so both read the not-connected sentinel. The two-byte width settles the typing.

Defined in `src/wolf/wtc_inc.tsp` as `CrcRead<otemp10>` (16-bit signed tenths of °C, the type of
the other heating-circuit sensor reads), referenced read-only on `src/wolf/35.w.fs1.tsp` (room
unit, slave `35`) and `src/wolf/51.w.em2.tsp` (heating module, slave `51`), the two circuits the
reads were taken on.

## How it was established

- **Read.** Each register was read once on the room unit (slave `35`) and once on the heating
  module (slave `51`) by a raw `50 22` register read through the running ebusd on 2026-11-22. All
  four reads were answered `02 00 80`.
- **Width.** The answer carries two data bytes (`NN = 02`); the value is 16-bit, not the single
  byte the former upstream #717 assumed (`temp1` / `D1C`). That one-byte typing was the reason the
  two registers had been dropped from the definitions; the raw read re-establishes them as 16-bit.
- **Sentinel.** `00 80` = `0x8000`, the replacement value ebusd uses for a signed 16-bit field
  with no reading. Read on both the room unit and the module, so it is the register's
  not-connected answer, not a transient.
- **Checksum.** The first request byte is the precomputed Weishaupt CRC-8 (poly `0x5C`) over the
  two address bytes, as for every other `50 22` read on these devices (see
  [register-crc.md](register-crc.md)): `5e` for `13 0a`, `92` for `1d 0a`.

## Not verified

- The value with a sensor connected: this installation has neither sensor, so only the
  not-connected answer (`0x8000`) was seen. The 16-bit width and the signed tenths-of-°C codec
  follow the other heating-circuit sensor reads of these devices; a live value would confirm the
  scale but cannot change the established width.

## Equipment

Kromschröder WCM system (two condensing boilers in cascade behind a system manager); room units
answering at `35`, `75`, `f5` (software 2726) and heating modules at `50`, `51`, `52`. The reads
were taken on the room unit `35` and the heating module `51`.

## Date

2026-11-22.
