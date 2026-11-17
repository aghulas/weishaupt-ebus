# em1 — system clock and weekly circulation and hot-water programs (read)

## What

Read-only registers on heating module #1 (circuit `em1`, target 0x50), `PBSB = 50 22`,
ID `<crc> <addr> <sub>` with the precomputed CRC (see [register-crc.md](register-crc.md)),
in `src/wolf/50..em1.tsp`:

- **System clock** (`sub = 01`): weekday, day, month, year, minute, second (no hour, see below).
- **Weekly circulation program** (`sub = 1a`) and **weekly hot-water program** (`sub = 17`):
  three switch-time slots per weekday, each a start ("from") and stop ("to") time with an
  enable flag (model `SwitchTimes`).

## How it was established

Live bus, ebusd `read` of each message. Clock, read the same session:

| message | addr sub | id | value |
|---|---|---|---|
| SystemWeekday | 21 01 | `612101` | Monday |
| SystemDay | 22 01 | `852201` | 16 |
| SystemMonth | 23 01 | `d92301` | November |
| SystemYear | 24 01 | `112401` | 26 |
| SystemMinute | 26 01 | `a92601` | 46 |
| SystemSecond | 27 01 | `f52701` | 22 (read on 2026-11-17) |

Weekly program, e.g.:

| message | addr sub | id | value (ToTime;ToEnabled;FromTime;FromEnabled) |
|---|---|---|---|
| CircProgramMon1 | 10 1a | `aa101a` | 00:00; Disabled; 00:00; Disabled |
| DHWProgramMon1 | 10 17 | `a71017` | 16:00; Enabled; 09:00; Enabled |
| DHWProgramSat1 | 60 17 | `536017` | 00:00; Disabled; 00:00; Disabled |

The hot-water program carries a real schedule (Monday hot water enabled 09:00→16:00), which
confirms the `SwitchTimes` codec on non-trivial data, not just the disabled sentinel.

The clock reads back the real date and time of the capture (Monday, 16 November '26, minute 46),
which confirms both the addresses and the codecs. The program slot decodes to the four
TTQ/enable fields. CRCs computed by the verified routine; addresses taken from the running
ebusd definitions, cross-checked against the weishaupt-pr source.

Shared template: the register-read base (`crcr` / `CrcRead`) was moved to `src/wolf/wtc_inc.tsp`
so `15..ka.tsp` and `50..em1.tsp` share it; the 18 KA reads emit byte-for-byte as before.

Toolchain: `tsp compile`, `tsp format --check`, `ebusd --checkconfig` all clean (0 errors).

## Equipment

Kromschröder WCM-FS heating module on eBUS, `MF=Kromschröder`.

## Date

2026-11-16; `SystemSecond` read on 2026-11-17.

## Not verified

- `SystemHour` (`25 01`, id `4d2501`) was not read: the running configuration has no active
  read for it, and its address was only inferred from the sequence weekday to second (`21` to
  `27`). It was removed from the lot on 2026-11-17 and comes back once a read confirms it.
- Of the 42 program slots, three are recorded here (`CircProgramMon1`, `DHWProgramMon1`,
  `DHWProgramSat1`). The other addresses follow the same pattern (weekday in the high nibble
  of the address, slot number minus one in the low nibble) and come from the running definitions.
- The circulation program was read with all slots disabled; non-trivial switch times were
  seen in the hot-water program only (one slot).
- No heating program was found on this bus (only circulation and hot water).
- Shipped read-only; the matching writes (`50 23`) belong to a later lot.
