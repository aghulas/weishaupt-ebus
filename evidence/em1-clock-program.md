# em1 — system clock and weekly circulation program (read)

## What

Read-only registers on heating module #1 (circuit `em1`, target 0x50), `PBSB = 50 22`,
ID `<crc> <addr> <sub>` with the precomputed CRC (see [register-crc.md](register-crc.md)),
in `src/wolf/50..em1.tsp`:

- **System clock** (`sub = 01`): weekday, day, month, year, hour, minute, second.
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

2026-11-16.

## Not verified

- Only the **circulation** weekly program is shipped; the heating and hot-water weekly programs
  (other sub-addresses) are not yet included.
- The programs were read at one point in time, all slots disabled on this site; non-trivial
  switch times were not observed.
- Shipped read-only; the matching writes (`50 23`) belong to a later lot.
