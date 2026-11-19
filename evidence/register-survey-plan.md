# Register survey — read-only plan (prepared 2026-11-19, not run)

## Goal

Find the registers (`50 22` reads) that answer on each Kromschröder / Weishaupt device of the
installation but that no definition of release 0.5.13 covers, so that they can be matched with
the parameter lists of the manuals (WCM-KA 3.0 83258404, WCM-FS 2.0 / WCM-EM 2.1 83277504,
WTC-GB 83251704: P-numbers and info values) and the register list of the vendor service tool
([service-tool-log.md](service-tool-log.md)). Reads only (rule 7): no `50 23`, no other
primary command.

## What is known about the register space

A register is a 16-bit number; on the bus it goes low byte first after the checksum byte
([register-crc.md](register-crc.md)): `27 02` is register 0x0227 = 551. The defined and
captured registers fall in a few blocks, which set the ranges:

| Block | Holds (examples) |
|---|---|
| 0x0000–0x03ff | live values and settings of every device type: temperatures `0c 00`, `0d 00`, setpoints `05 00`, `08 00`, settings `0e 01`–`41 01`, info values of the boilers `45 01`, `99 01`, `27 02`, `bc 02` |
| 0x0500–0x05ff | system manager: legionella setpoint `87 05` |
| 0x0900–0x0bff | circuit type `73 09`, legionella circulation `b1 09`, outside values `0c 0a`, `14 0a`, `1a 0a`, B24 `40 0a`, clock and date `9a 0b`–`a3 0b` |
| 0x1300–0x13ff | circulation with legionella `f3 13` |
| 0x1400–0x1aff | weekly programs (scheme known, all programs defined or read): **left out** |
| 0xfd00–0xfdff | hydraulic and cascade settings of the system manager `e2 fd`–`ec fd`, sequence `ca fd`, `cb fd` |

`50` answers every register with the values of `15` (one device at two addresses), so only `15`
is surveyed. Registers already defined in 0.5.13 (a `50 22` read line of the device's file, and
of `50.w.em1` for `15`) are left out.

## Design

- **Pass 1**: one device of each type, the full ranges of its type:

  | Device | Type | Ranges | Registers | Registers per request | Requests |
  |---|---|---|---|---|---|
  | `08` | boiler automat | 0x0000–0x03ff | 1 015 | 1 | 1 015 |
  | `15` | system manager | 0x0000–0x03ff, 0x0500–0x05ff, 0x0900–0x0bff, 0x1300–0x13ff, 0xfd00–0xfdff | 2 508 | 4 | 627 |
  | `51` | heating module | 0x0000–0x03ff, 0x0900–0x0bff | 1 782 | 4 | 446 |
  | `35` | room unit | 0x0000–0x03ff, 0x0900–0x0bff, 0x1300–0x13ff | 2 024 | 4 | 506 |
  | | | | **7 329** | | **2 594** |

  Four registers per request where ebusd's own four-register reads were seen on this bus
  (telegram log, `15`, `35`, `51`, `52`): ID `<crc> <a1 lo> <a1 hi> … <a4 lo> <a4 hi>`, the
  checksum over the eight address bytes, answer eight bytes in the same order (checked on two
  captured requests: `b1 05 00 08 00 14 0a 0e 01` and `0c 16 01 28 00 2b 01 13 00`). One
  register per request on the boilers, where such reads were never seen.
- **Pass 2**: on `18`, `52`, `75`, `f5`, the registers that answered in pass 1 on `08`, `51`,
  `35` with anything but `00 80`; generated from the pass-1 results. Expected a few hundred
  requests, one or two chunks.
- **Pace**: one request every 2.5 s (never less than 2 s), about 0.6 % of the bus capacity.
  Chunks of at most 480 requests (20 minutes), at least 10 minutes between two chunks.
- **Burner pause**: before every group of 20 requests, look at ebusd's cache (no bus traffic):
  if `bc1 Status` or `bc2 Status` says the flame is on, or `ka ModulationStatus` is above 0,
  wait and look again every 60 s; resume when both burners are off.
- **Total**: pass 1 is 2 594 requests, **1.8 h of bus time in 6 chunks** (5 of 480 and one of
  194), so about 3 h with the pauses between chunks, more if the burners run.

## Ready to run

For the deployment session, on the owner's go. The vendor service tool must be disconnected.

1. Generate the request list (sends nothing):

   ```sh
   scripts/register-survey.py out/release/weishaupt-ebusd-config-0.5.13/kromschroeder pass1 > out/register-survey-pass1-requests.csv
   ```

   Columns: `chunk`, `seq`, `zz`, `registers` (the 16-bit numbers in hex, as read: `0227`
   is the bus bytes `27 02`), `request` (the `hex` command for ebusd, sent from ebusd's own
   address, no `-s`). Example rows: `1,35,08,0026,hex 08502203a82600` and
   `5,2089,35,0000 0001 0003 0006,hex 355022091c0000010003000600`.
2. Send the requests of one chunk in `seq` order at the pace above, with the burner pause.
   On a NAK or timeout: one retry after 5 s; if a four-register request fails twice, send its
   four registers one by one (`hex <zz>502203<crc><lo><hi>`, the checksum as in
   `register-crc.md`) and mark them `split`.
3. Write the results, one row per register, to
   `out/register-survey-pass1-results.csv` (installation data, not versioned):

   | Column | Content |
   |---|---|
   | `chunk`, `seq` | from the request list |
   | `time_local` | time of the answer, local, to the second |
   | `zz` | device |
   | `reg_dec`, `reg_hex` | the register: decimal, and the bus bytes `lo hi` (`551`, `27 02`) |
   | `request` | the `hex` command sent |
   | `status` | `ok`, `nak`, `timeout`, `short` (fewer bytes than asked), `split` |
   | `raw` | the two bytes of this register, `lo hi` (`db 02`); empty unless `ok` |
   | `burner` | `on` / `off` at the time of the request (from the cache) |

4. After pass 1, generate pass 2 from the results and run it the same way:

   ```sh
   scripts/register-survey.py out/release/weishaupt-ebusd-config-0.5.13/kromschroeder pass2 out/register-survey-pass1-results.csv > out/register-survey-pass2-requests.csv
   ```

5. Hand both result files to the definitions session. Nothing of them goes into this repository
   but the registers and values an evidence record quotes.

## What the results become

Each register that answers something other than `00 80` is compared with the parameter lists
of the manuals and the vendor tool's register list, by value (a factory value, a value shown on
a display) and by neighbourhood (registers next to a defined one). A register becomes a
definition only with a record that names it (rule 3): a value equal to a display or a manual
figure, or a change observed. `18 fc` (-100.0) and `70 fe` (-40.0) answers are recorded as
"sensor not fitted".

## Risk

None for the heating: reads only, at a pace below ebusd's own polling. The only cost is bus
time, kept to one request every 2.5 s and stopped while a burner runs.

## Date

2026-11-19.
