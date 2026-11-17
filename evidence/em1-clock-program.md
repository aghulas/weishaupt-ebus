# em1 — system clock and weekly circulation and hot-water programs (read)

## What

Read-only registers on heating module #1 (circuit `em1`, target 0x50), `PBSB = 50 22`,
ID `<crc> <addr> <sub>` with the precomputed CRC (see [register-crc.md](register-crc.md)),
in `src/wolf/50.w.em1.tsp`:

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

Weekly program, all 42 slots, read one by one on 2026-11-17 (ebusd `read` of each slot, then
passive capture of the resulting telegrams, master `31` to slave `50`, `PBSB = 50 22`). The
`id` column is the request payload seen on the bus, the `answer` column the two data bytes of
the reply (length byte dropped):

| message | addr sub | id | answer | value (ToTime; ToEnabled; FromTime; FromEnabled) |
|---|---|---|---|---|
| CircProgramMon1 | 10 1a | `aa101a` | `80 80` | 00:00; Disabled; 00:00; Disabled |
| CircProgramMon2 | 11 1a | `f6111a` | `80 80` | 00:00; Disabled; 00:00; Disabled |
| CircProgramMon3 | 12 1a | `12121a` | `80 80` | 00:00; Disabled; 00:00; Disabled |
| CircProgramTue1 | 20 1a | `26201a` | `80 80` | 00:00; Disabled; 00:00; Disabled |
| CircProgramTue2 | 21 1a | `7a211a` | `80 80` | 00:00; Disabled; 00:00; Disabled |
| CircProgramTue3 | 22 1a | `9e221a` | `80 80` | 00:00; Disabled; 00:00; Disabled |
| CircProgramWed1 | 30 1a | `96301a` | `80 80` | 00:00; Disabled; 00:00; Disabled |
| CircProgramWed2 | 31 1a | `ca311a` | `80 80` | 00:00; Disabled; 00:00; Disabled |
| CircProgramWed3 | 32 1a | `2e321a` | `80 80` | 00:00; Disabled; 00:00; Disabled |
| CircProgramThu1 | 40 1a | `62401a` | `80 80` | 00:00; Disabled; 00:00; Disabled |
| CircProgramThu2 | 41 1a | `3e411a` | `80 80` | 00:00; Disabled; 00:00; Disabled |
| CircProgramThu3 | 42 1a | `da421a` | `80 80` | 00:00; Disabled; 00:00; Disabled |
| CircProgramFri1 | 50 1a | `d2501a` | `80 80` | 00:00; Disabled; 00:00; Disabled |
| CircProgramFri2 | 51 1a | `8e511a` | `80 80` | 00:00; Disabled; 00:00; Disabled |
| CircProgramFri3 | 52 1a | `6a521a` | `80 80` | 00:00; Disabled; 00:00; Disabled |
| CircProgramSat1 | 60 1a | `5e601a` | `80 80` | 00:00; Disabled; 00:00; Disabled |
| CircProgramSat2 | 61 1a | `02611a` | `80 80` | 00:00; Disabled; 00:00; Disabled |
| CircProgramSat3 | 62 1a | `e6621a` | `80 80` | 00:00; Disabled; 00:00; Disabled |
| CircProgramSun1 | 70 1a | `ee701a` | `80 80` | 00:00; Disabled; 00:00; Disabled |
| CircProgramSun2 | 71 1a | `b2711a` | `80 80` | 00:00; Disabled; 00:00; Disabled |
| CircProgramSun3 | 72 1a | `56721a` | `80 80` | 00:00; Disabled; 00:00; Disabled |
| DHWProgramMon1 | 10 17 | `a71017` | `40 24` | 16:00; Enabled; 09:00; Enabled |
| DHWProgramMon2 | 11 17 | `fb1117` | `80 80` | 00:00; Disabled; 00:00; Disabled |
| DHWProgramMon3 | 12 17 | `1f1217` | `80 80` | 00:00; Disabled; 00:00; Disabled |
| DHWProgramTue1 | 20 17 | `2b2017` | `40 24` | 16:00; Enabled; 09:00; Enabled |
| DHWProgramTue2 | 21 17 | `772117` | `80 80` | 00:00; Disabled; 00:00; Disabled |
| DHWProgramTue3 | 22 17 | `932217` | `80 80` | 00:00; Disabled; 00:00; Disabled |
| DHWProgramWed1 | 30 17 | `9b3017` | `80 80` | 00:00; Disabled; 00:00; Disabled |
| DHWProgramWed2 | 31 17 | `c73117` | `80 80` | 00:00; Disabled; 00:00; Disabled |
| DHWProgramWed3 | 32 17 | `233217` | `80 80` | 00:00; Disabled; 00:00; Disabled |
| DHWProgramThu1 | 40 17 | `6f4017` | `40 24` | 16:00; Enabled; 09:00; Enabled |
| DHWProgramThu2 | 41 17 | `334117` | `80 80` | 00:00; Disabled; 00:00; Disabled |
| DHWProgramThu3 | 42 17 | `d74217` | `80 80` | 00:00; Disabled; 00:00; Disabled |
| DHWProgramFri1 | 50 17 | `df5017` | `40 24` | 16:00; Enabled; 09:00; Enabled |
| DHWProgramFri2 | 51 17 | `835117` | `80 80` | 00:00; Disabled; 00:00; Disabled |
| DHWProgramFri3 | 52 17 | `675217` | `80 80` | 00:00; Disabled; 00:00; Disabled |
| DHWProgramSat1 | 60 17 | `536017` | `80 80` | 00:00; Disabled; 00:00; Disabled |
| DHWProgramSat2 | 61 17 | `0f6117` | `80 80` | 00:00; Disabled; 00:00; Disabled |
| DHWProgramSat3 | 62 17 | `eb6217` | `80 80` | 00:00; Disabled; 00:00; Disabled |
| DHWProgramSun1 | 70 17 | `e37017` | `80 80` | 00:00; Disabled; 00:00; Disabled |
| DHWProgramSun2 | 71 17 | `bf7117` | `80 80` | 00:00; Disabled; 00:00; Disabled |
| DHWProgramSun3 | 72 17 | `5b7217` | `80 80` | 00:00; Disabled; 00:00; Disabled |

Every request payload seen on the bus is byte for byte the `@ext` triple of the message of the
same weekday and slot in `src/wolf/50.w.em1.tsp` (42 of 42, no mismatch). The first byte of
each is also what the CRC routine of [register-crc.md](register-crc.md) gives for the address,
recomputed offline for all 57 `@ext` triples of the file.

Each answer is two bytes, stop time then start time, each a count of quarter hours in bits 0
to 6 with bit 7 set when the switch time is disabled: `40 24` is 16:00 and 09:00, both
enabled; `80 80` is the disabled slot. ebusd decodes the same values with the `SwitchTimes`
fields.

The hot-water program carries a real schedule in slot 1 of Monday, Tuesday, Thursday and
Friday (09:00 to 16:00) and nothing on Wednesday, Saturday and Sunday. The enabled days are
not contiguous, so the weekday is confirmed to sit in the high nibble of the address
(`1` Monday to `7` Sunday), and the `SwitchTimes` codec is confirmed on non-trivial data, not
just the disabled sentinel.

The clock reads back the real date and time of the capture (Monday, 16 November '26, minute 46),
which confirms both the addresses and the codecs. The program slot decodes to the four
TTQ/enable fields. CRCs computed by the verified routine; addresses taken from the running
ebusd definitions, cross-checked against the weishaupt-pr source.

Shared template: the register-read base (`crcr` / `CrcRead`) was moved to `src/wolf/wtc_inc.tsp`
so `15.w.ka.tsp` and `50.w.em1.tsp` share it; the 18 KA reads emit byte-for-byte as before.

Toolchain: `tsp compile`, `tsp format --check`, `ebusd --checkconfig` all clean (0 errors).

**`SystemHour`** (`25 01`, id `4d2501`). Removed from the lot on 2026-11-17 for want of a bus
read: the running configuration defines the hour at `25 01` for writing only and no telegram
naming that register appeared in the passive capture. Read the same day with the `hex` command
of ebusd (`31 50 5022 03 4d 25 01`): answer `02 0f 00`, 15, at 15:50 local time. The register
is the hour, UIN, as its neighbours `21` to `24`, `26` and `27`. It is in the lot again since
that day (`SystemHour`, `@ext(0x4d, 0x25, 0x01)`).

## Equipment

Kromschröder WCM-FS heating module on eBUS, `MF=Kromschröder`.

## Date

2026-11-16; `SystemSecond`, `SystemHour` and the 42 program slots read on 2026-11-17.

## Not verified

- The circulation program was read with all 21 slots disabled; non-trivial switch times were
  seen in the hot-water program only (slot 1 of four weekdays). Slots 2 and 3 were seen
  disabled only.
- No heating program was found on this bus (only circulation and hot water).
  **Corrected on 2026-11-17, see below: this statement is wrong.**
- Shipped read-only; the matching writes (`50 23`) belong to a later lot.

## Correction of 2026-11-17 — heating programs do exist on this bus

The statement above ("no heating program was found") came from looking only at the two
sub-bytes this lot defines. It does not hold:

- The device at `50` answers the three heating programs at sub-bytes `14`, `15` and `16`, same
  address layout and same two-byte slot as the programs of this record. All 63 slots were read
  on 2026-11-17: program 1 is 06:00 to 22:00 on working days and 07:00 to 23:00 at the
  weekend; programs 2 and 3 use slots 1 and 2 on working days (06:00 to 08:00, then 16:00 or
  12:00 to 22:00). Bytes in [modules-programs.md](modules-programs.md).
- The same sub-bytes are answered by the system manager (`15`), the device at `f6`, the
  heating modules `51` and `52`, and the three room units (`35`, `75`, `f5`; lot H,
  [room-units-programs.md](room-units-programs.md)).
- The 42 hot-water and circulation slots of this record were read again the same day
  (17:30 to 17:37): unchanged, and identical byte for byte on `15`, `50` and `f6`.
- What the programs of this record are: the hot-water program is the one the installation
  applies (hot-water set value of the system manager 50.0 inside the period, 8.0 outside it,
  see [modules-programs.md](modules-programs.md)). The heating programs at `50` are not in
  this lot and were not seen to be applied.

The definitions of this lot are not affected: they are the hot-water and circulation
programs, and both read as recorded.
