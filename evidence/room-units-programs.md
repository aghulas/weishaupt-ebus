# fs1, fs2, fs3 — weekly programs of the room units (50 22)

## What

Lot H, branch `weishaupt-H` of the ebusd-configuration fork (on `weishaupt-G`), two commits:
the three weekly heating programs, then the weekly hot-water and circulation programs. Read
side only, `PBSB = 50 22`, ID `<crc> <addr> <sub>` with the `<crc>` precomputed (see
[register-crc.md](register-crc.md)), on the three room units: `src/wolf/35.w.fs1.tsp` (slave
address `35`), `src/wolf/75.w.fs2.tsp` (`75`), `src/wolf/f5.w.fs3.tsp` (`f5`). The 105 models
are shared in `src/wolf/wtc_inc.tsp`; each uses the `SwitchTimes` codec of lot A
([em1-clock-program.md](em1-clock-program.md)).

| program | sub-byte | messages per unit |
|---|---|---|
| heating program 1 | `14` | `HCProgram1Mon1` … `HCProgram1Sun3` (21) |
| heating program 2 | `15` | `HCProgram2Mon1` … `HCProgram2Sun3` (21) |
| heating program 3 | `16` | `HCProgram3Mon1` … `HCProgram3Sun3` (21) |
| hot water | `17` | `DHWProgramMon1` … `DHWProgramSun3` (21) |
| circulation | `1a` | `CircProgramMon1` … `CircProgramSun3` (21) |

Register address: the weekday in the high nibble (`1` Monday to `7` Sunday), the slot in the
low nibble (`0` to `2`). The answer is two bytes, stop time then start time, each a count of
quarter hours in bits 0 to 6, bit 7 set when the switch time is disabled (`80 80` = slot not
used). 105 messages per unit, 315 in all.

## Bytes read

Request payload, then for each unit the two data bytes of the answer (length byte `02`
dropped) and the decoded slot, start to stop.

### Heating program 1 (sub-byte `14`)

| message | addr sub | request | fs1 (`35`) | fs2 (`75`) | fs3 (`f5`) |
|---|---|---|---|---|---|
| HCProgram1Mon1 | `10 14` | `a4 10 14` | `48 1a` 06:30 to 18:00 | `48 1a` 06:30 to 18:00 | `48 1a` 06:30 to 18:00 |
| HCProgram1Mon2 | `11 14` | `f8 11 14` | `80 80` disabled | `80 80` disabled | `80 80` disabled |
| HCProgram1Mon3 | `12 14` | `1c 12 14` | `80 80` disabled | `80 80` disabled | `80 80` disabled |
| HCProgram1Tue1 | `20 14` | `28 20 14` | `5a 1a` 06:30 to 22:30 | `5a 1a` 06:30 to 22:30 | `48 1a` 06:30 to 18:00 |
| HCProgram1Tue2 | `21 14` | `74 21 14` | `80 80` disabled | `80 80` disabled | `80 80` disabled |
| HCProgram1Tue3 | `22 14` | `90 22 14` | `80 80` disabled | `80 80` disabled | `80 80` disabled |
| HCProgram1Wed1 | `30 14` | `98 30 14` | `80 80` disabled | `80 80` disabled | `80 80` disabled |
| HCProgram1Wed2 | `31 14` | `c4 31 14` | `80 80` disabled | `80 80` disabled | `80 80` disabled |
| HCProgram1Wed3 | `32 14` | `20 32 14` | `80 80` disabled | `80 80` disabled | `80 80` disabled |
| HCProgram1Thu1 | `40 14` | `6c 40 14` | `48 1a` 06:30 to 18:00 | `48 1a` 06:30 to 18:00 | `48 1a` 06:30 to 18:00 |
| HCProgram1Thu2 | `41 14` | `30 41 14` | `80 80` disabled | `80 80` disabled | `80 80` disabled |
| HCProgram1Thu3 | `42 14` | `d4 42 14` | `80 80` disabled | `80 80` disabled | `80 80` disabled |
| HCProgram1Fri1 | `50 14` | `dc 50 14` | `48 1a` 06:30 to 18:00 | `48 1a` 06:30 to 18:00 | `48 1a` 06:30 to 18:00 |
| HCProgram1Fri2 | `51 14` | `80 51 14` | `80 80` disabled | `80 80` disabled | `80 80` disabled |
| HCProgram1Fri3 | `52 14` | `64 52 14` | `80 80` disabled | `80 80` disabled | `80 80` disabled |
| HCProgram1Sat1 | `60 14` | `50 60 14` | `80 80` disabled | `80 80` disabled | `80 80` disabled |
| HCProgram1Sat2 | `61 14` | `0c 61 14` | `80 80` disabled | `80 80` disabled | `80 80` disabled |
| HCProgram1Sat3 | `62 14` | `e8 62 14` | `80 80` disabled | `80 80` disabled | `80 80` disabled |
| HCProgram1Sun1 | `70 14` | `e0 70 14` | `80 80` disabled | `80 80` disabled | `80 80` disabled |
| HCProgram1Sun2 | `71 14` | `bc 71 14` | `80 80` disabled | `80 80` disabled | `80 80` disabled |
| HCProgram1Sun3 | `72 14` | `58 72 14` | `80 80` disabled | `80 80` disabled | `80 80` disabled |

### Heating program 2 (sub-byte `15`)

| message | addr sub | request | fs1 (`35`) | fs2 (`75`) | fs3 (`f5`) |
|---|---|---|---|---|---|
| HCProgram2Mon1 | `10 15` | `a5 10 15` | `48 18` 06:00 to 18:00 | `48 18` 06:00 to 18:00 | `48 18` 06:00 to 18:00 |
| HCProgram2Mon2 | `11 15` | `f9 11 15` | `80 80` disabled | `80 80` disabled | `80 80` disabled |
| HCProgram2Mon3 | `12 15` | `1d 12 15` | `80 80` disabled | `80 80` disabled | `80 80` disabled |
| HCProgram2Tue1 | `20 15` | `29 20 15` | `48 18` 06:00 to 18:00 | `48 18` 06:00 to 18:00 | `48 18` 06:00 to 18:00 |
| HCProgram2Tue2 | `21 15` | `75 21 15` | `80 80` disabled | `80 80` disabled | `80 80` disabled |
| HCProgram2Tue3 | `22 15` | `91 22 15` | `80 80` disabled | `80 80` disabled | `80 80` disabled |
| HCProgram2Wed1 | `30 15` | `99 30 15` | `48 18` 06:00 to 18:00 | `48 18` 06:00 to 18:00 | `48 18` 06:00 to 18:00 |
| HCProgram2Wed2 | `31 15` | `c5 31 15` | `80 80` disabled | `80 80` disabled | `80 80` disabled |
| HCProgram2Wed3 | `32 15` | `21 32 15` | `80 80` disabled | `80 80` disabled | `80 80` disabled |
| HCProgram2Thu1 | `40 15` | `6d 40 15` | `48 18` 06:00 to 18:00 | `48 18` 06:00 to 18:00 | `48 18` 06:00 to 18:00 |
| HCProgram2Thu2 | `41 15` | `31 41 15` | `80 80` disabled | `80 80` disabled | `80 80` disabled |
| HCProgram2Thu3 | `42 15` | `d5 42 15` | `80 80` disabled | `80 80` disabled | `80 80` disabled |
| HCProgram2Fri1 | `50 15` | `dd 50 15` | `48 18` 06:00 to 18:00 | `48 18` 06:00 to 18:00 | `48 18` 06:00 to 18:00 |
| HCProgram2Fri2 | `51 15` | `81 51 15` | `80 80` disabled | `80 80` disabled | `80 80` disabled |
| HCProgram2Fri3 | `52 15` | `65 52 15` | `80 80` disabled | `80 80` disabled | `80 80` disabled |
| HCProgram2Sat1 | `60 15` | `51 60 15` | `30 1c` 07:00 to 12:00 | `30 1c` 07:00 to 12:00 | `3c 1a` 06:30 to 15:00 |
| HCProgram2Sat2 | `61 15` | `0d 61 15` | `80 80` disabled | `80 80` disabled | `80 80` disabled |
| HCProgram2Sat3 | `62 15` | `e9 62 15` | `80 80` disabled | `80 80` disabled | `80 80` disabled |
| HCProgram2Sun1 | `70 15` | `e1 70 15` | `80 80` disabled | `80 80` disabled | `80 80` disabled |
| HCProgram2Sun2 | `71 15` | `bd 71 15` | `80 80` disabled | `80 80` disabled | `80 80` disabled |
| HCProgram2Sun3 | `72 15` | `59 72 15` | `80 80` disabled | `80 80` disabled | `80 80` disabled |

### Heating program 3 (sub-byte `16`)

| message | addr sub | request | fs1 (`35`) | fs2 (`75`) | fs3 (`f5`) |
|---|---|---|---|---|---|
| HCProgram3Mon1 | `10 16` | `a6 10 16` | `58 18` 06:00 to 22:00 | `58 18` 06:00 to 22:00 | `58 18` 06:00 to 22:00 |
| HCProgram3Mon2 | `11 16` | `fa 11 16` | `80 80` disabled | `80 80` disabled | `80 80` disabled |
| HCProgram3Mon3 | `12 16` | `1e 12 16` | `80 80` disabled | `80 80` disabled | `80 80` disabled |
| HCProgram3Tue1 | `20 16` | `2a 20 16` | `58 18` 06:00 to 22:00 | `58 18` 06:00 to 22:00 | `58 18` 06:00 to 22:00 |
| HCProgram3Tue2 | `21 16` | `76 21 16` | `80 80` disabled | `80 80` disabled | `80 80` disabled |
| HCProgram3Tue3 | `22 16` | `92 22 16` | `80 80` disabled | `80 80` disabled | `80 80` disabled |
| HCProgram3Wed1 | `30 16` | `9a 30 16` | `58 18` 06:00 to 22:00 | `58 18` 06:00 to 22:00 | `58 18` 06:00 to 22:00 |
| HCProgram3Wed2 | `31 16` | `c6 31 16` | `80 80` disabled | `80 80` disabled | `80 80` disabled |
| HCProgram3Wed3 | `32 16` | `22 32 16` | `80 80` disabled | `80 80` disabled | `80 80` disabled |
| HCProgram3Thu1 | `40 16` | `6e 40 16` | `58 18` 06:00 to 22:00 | `58 18` 06:00 to 22:00 | `58 18` 06:00 to 22:00 |
| HCProgram3Thu2 | `41 16` | `32 41 16` | `80 80` disabled | `80 80` disabled | `80 80` disabled |
| HCProgram3Thu3 | `42 16` | `d6 42 16` | `80 80` disabled | `80 80` disabled | `80 80` disabled |
| HCProgram3Fri1 | `50 16` | `de 50 16` | `58 18` 06:00 to 22:00 | `58 18` 06:00 to 22:00 | `58 18` 06:00 to 22:00 |
| HCProgram3Fri2 | `51 16` | `82 51 16` | `80 80` disabled | `80 80` disabled | `80 80` disabled |
| HCProgram3Fri3 | `52 16` | `66 52 16` | `80 80` disabled | `80 80` disabled | `80 80` disabled |
| HCProgram3Sat1 | `60 16` | `52 60 16` | `80 80` disabled | `80 80` disabled | `80 80` disabled |
| HCProgram3Sat2 | `61 16` | `0e 61 16` | `80 80` disabled | `80 80` disabled | `80 80` disabled |
| HCProgram3Sat3 | `62 16` | `ea 62 16` | `80 80` disabled | `80 80` disabled | `80 80` disabled |
| HCProgram3Sun1 | `70 16` | `e2 70 16` | `80 80` disabled | `80 80` disabled | `80 80` disabled |
| HCProgram3Sun2 | `71 16` | `be 71 16` | `80 80` disabled | `80 80` disabled | `80 80` disabled |
| HCProgram3Sun3 | `72 16` | `5a 72 16` | `80 80` disabled | `80 80` disabled | `80 80` disabled |

### Hot-water program (sub-byte `17`)

| message | addr sub | request | fs1 (`35`) | fs2 (`75`) | fs3 (`f5`) |
|---|---|---|---|---|---|
| DHWProgramMon1 | `10 17` | `a7 10 17` | `54 14` 05:00 to 21:00 | `54 14` 05:00 to 21:00 | `54 14` 05:00 to 21:00 |
| DHWProgramMon2 | `11 17` | `fb 11 17` | `80 80` disabled | `80 80` disabled | `80 80` disabled |
| DHWProgramMon3 | `12 17` | `1f 12 17` | `80 80` disabled | `80 80` disabled | `80 80` disabled |
| DHWProgramTue1 | `20 17` | `2b 20 17` | `54 14` 05:00 to 21:00 | `54 14` 05:00 to 21:00 | `54 14` 05:00 to 21:00 |
| DHWProgramTue2 | `21 17` | `77 21 17` | `80 80` disabled | `80 80` disabled | `80 80` disabled |
| DHWProgramTue3 | `22 17` | `93 22 17` | `80 80` disabled | `80 80` disabled | `80 80` disabled |
| DHWProgramWed1 | `30 17` | `9b 30 17` | `54 14` 05:00 to 21:00 | `54 14` 05:00 to 21:00 | `54 14` 05:00 to 21:00 |
| DHWProgramWed2 | `31 17` | `c7 31 17` | `80 80` disabled | `80 80` disabled | `80 80` disabled |
| DHWProgramWed3 | `32 17` | `23 32 17` | `80 80` disabled | `80 80` disabled | `80 80` disabled |
| DHWProgramThu1 | `40 17` | `6f 40 17` | `54 14` 05:00 to 21:00 | `54 14` 05:00 to 21:00 | `54 14` 05:00 to 21:00 |
| DHWProgramThu2 | `41 17` | `33 41 17` | `80 80` disabled | `80 80` disabled | `80 80` disabled |
| DHWProgramThu3 | `42 17` | `d7 42 17` | `80 80` disabled | `80 80` disabled | `80 80` disabled |
| DHWProgramFri1 | `50 17` | `df 50 17` | `54 14` 05:00 to 21:00 | `54 14` 05:00 to 21:00 | `54 14` 05:00 to 21:00 |
| DHWProgramFri2 | `51 17` | `83 51 17` | `80 80` disabled | `80 80` disabled | `80 80` disabled |
| DHWProgramFri3 | `52 17` | `67 52 17` | `80 80` disabled | `80 80` disabled | `80 80` disabled |
| DHWProgramSat1 | `60 17` | `53 60 17` | `58 18` 06:00 to 22:00 | `58 18` 06:00 to 22:00 | `58 18` 06:00 to 22:00 |
| DHWProgramSat2 | `61 17` | `0f 61 17` | `80 80` disabled | `80 80` disabled | `80 80` disabled |
| DHWProgramSat3 | `62 17` | `eb 62 17` | `80 80` disabled | `80 80` disabled | `80 80` disabled |
| DHWProgramSun1 | `70 17` | `e3 70 17` | `58 18` 06:00 to 22:00 | `58 18` 06:00 to 22:00 | `58 18` 06:00 to 22:00 |
| DHWProgramSun2 | `71 17` | `bf 71 17` | `80 80` disabled | `80 80` disabled | `80 80` disabled |
| DHWProgramSun3 | `72 17` | `5b 72 17` | `80 80` disabled | `80 80` disabled | `80 80` disabled |

### Circulation program (sub-byte `1a`)

| message | addr sub | request | fs1 (`35`) | fs2 (`75`) | fs3 (`f5`) |
|---|---|---|---|---|---|
| CircProgramMon1 | `10 1a` | `aa 10 1a` | `1c 18` 06:00 to 07:00 | `1c 18` 06:00 to 07:00 | `1c 18` 06:00 to 07:00 |
| CircProgramMon2 | `11 1a` | `f6 11 1a` | `34 2c` 11:00 to 13:00 | `34 2c` 11:00 to 13:00 | `34 2c` 11:00 to 13:00 |
| CircProgramMon3 | `12 1a` | `12 12 1a` | `4c 44` 17:00 to 19:00 | `4c 44` 17:00 to 19:00 | `4c 44` 17:00 to 19:00 |
| CircProgramTue1 | `20 1a` | `26 20 1a` | `1c 18` 06:00 to 07:00 | `1c 18` 06:00 to 07:00 | `1c 18` 06:00 to 07:00 |
| CircProgramTue2 | `21 1a` | `7a 21 1a` | `34 2c` 11:00 to 13:00 | `34 2c` 11:00 to 13:00 | `34 2c` 11:00 to 13:00 |
| CircProgramTue3 | `22 1a` | `9e 22 1a` | `4c 44` 17:00 to 19:00 | `4c 44` 17:00 to 19:00 | `4c 44` 17:00 to 19:00 |
| CircProgramWed1 | `30 1a` | `96 30 1a` | `1c 18` 06:00 to 07:00 | `1c 18` 06:00 to 07:00 | `1c 18` 06:00 to 07:00 |
| CircProgramWed2 | `31 1a` | `ca 31 1a` | `34 2c` 11:00 to 13:00 | `34 2c` 11:00 to 13:00 | `34 2c` 11:00 to 13:00 |
| CircProgramWed3 | `32 1a` | `2e 32 1a` | `4c 44` 17:00 to 19:00 | `4c 44` 17:00 to 19:00 | `4c 44` 17:00 to 19:00 |
| CircProgramThu1 | `40 1a` | `62 40 1a` | `1c 18` 06:00 to 07:00 | `1c 18` 06:00 to 07:00 | `1c 18` 06:00 to 07:00 |
| CircProgramThu2 | `41 1a` | `3e 41 1a` | `34 2c` 11:00 to 13:00 | `34 2c` 11:00 to 13:00 | `34 2c` 11:00 to 13:00 |
| CircProgramThu3 | `42 1a` | `da 42 1a` | `4c 44` 17:00 to 19:00 | `4c 44` 17:00 to 19:00 | `4c 44` 17:00 to 19:00 |
| CircProgramFri1 | `50 1a` | `d2 50 1a` | `1c 18` 06:00 to 07:00 | `1c 18` 06:00 to 07:00 | `1c 18` 06:00 to 07:00 |
| CircProgramFri2 | `51 1a` | `8e 51 1a` | `34 2c` 11:00 to 13:00 | `34 2c` 11:00 to 13:00 | `34 2c` 11:00 to 13:00 |
| CircProgramFri3 | `52 1a` | `6a 52 1a` | `4c 44` 17:00 to 19:00 | `4c 44` 17:00 to 19:00 | `4c 44` 17:00 to 19:00 |
| CircProgramSat1 | `60 1a` | `5e 60 1a` | `20 1c` 07:00 to 08:00 | `20 1c` 07:00 to 08:00 | `20 1c` 07:00 to 08:00 |
| CircProgramSat2 | `61 1a` | `02 61 1a` | `34 2c` 11:00 to 13:00 | `34 2c` 11:00 to 13:00 | `34 2c` 11:00 to 13:00 |
| CircProgramSat3 | `62 1a` | `e6 62 1a` | `4c 44` 17:00 to 19:00 | `4c 44` 17:00 to 19:00 | `4c 44` 17:00 to 19:00 |
| CircProgramSun1 | `70 1a` | `ee 70 1a` | `20 1c` 07:00 to 08:00 | `20 1c` 07:00 to 08:00 | `20 1c` 07:00 to 08:00 |
| CircProgramSun2 | `71 1a` | `b2 71 1a` | `34 2c` 11:00 to 13:00 | `34 2c` 11:00 to 13:00 | `34 2c` 11:00 to 13:00 |
| CircProgramSun3 | `72 1a` | `56 72 1a` | `4c 44` 17:00 to 19:00 | `4c 44` 17:00 to 19:00 | `4c 44` 17:00 to 19:00 |

## How it was established

1. **Read.** Each of the 315 slots was read once through the running ebusd (master `31`),
   forced to the bus, reads spaced, on 2026-11-17 between 17:07 and 17:11. All were answered,
   none with an error or with a not-available value.
2. **Bytes.** Request and answer were taken from the passive capture of the same ebusd
   (`grab result all`), snapshot of 17:07 before the reads and of 17:11 after them:
   `31 → 35 / 75 / f5`, `50 22`, three request bytes, answer `02 <stop> <start>`. Every one of
   the 315 telegrams is new in the second snapshot or has a higher count than in the first,
   with the same answer. They are the bytes of the tables.
3. **Checksum.** The first request byte was recomputed offline for the 315 telegrams with the
   routine of [register-crc.md](register-crc.md) (CRC-8, polynomial 0x5C, initial value =
   first address byte, over the address bytes): no mismatch. The 315 IDs in the compiled CSV
   equal the request bytes of the tables.
4. **Slot format.** Same registers and same two-byte answer as the hot-water and circulation
   programs of the heating module `50`, where the codec was proven
   ([em1-clock-program.md](em1-clock-program.md)): the sub-bytes `17` and `1a` and the
   request bytes of those 42 slots are identical on the room units. Supported here by the
   values themselves:
   - Every enabled time is a multiple of a quarter hour inside the day, and every start lies
     before its stop.
   - **Weekday nibble.** Heating program 1 is enabled on Monday, Tuesday, Thursday and Friday
     and disabled on Wednesday, Saturday and Sunday: the enabled days are not contiguous.
     Programs 2 and 3, hot water and circulation separate working days from the weekend at the
     same nibble values (`6`, `7`).
   - **Slot nibble.** The circulation program uses the three slots of every day, in ascending
     order of the low nibble: 06:00 to 07:00 (weekend 07:00 to 08:00), 11:00 to 13:00, 17:00
     to 19:00. This is the first record with switch times in slots 2 and 3.
   - **Stored per device.** The units do not echo one common table: Tuesday of heating
     program 1 ends at 22:30 on `35` and `75` and at 18:00 on `f5`; Saturday of heating
     program 2 is 07:00 to 12:00 on `35` and `75` and 06:30 to 15:00 on `f5`. The module `50`
     answers other values at the same registers (hot water 09:00 to 16:00 on four days,
     circulation disabled, see the lot A record).
5. **Second path on the bus.** The running configuration also polls these registers three or
   four at a time in one `50 22` telegram (for example `68 10 14 11 14 12 14` answered
   `06 48 1a 80 80 80 80` on `35`). In the same snapshot, 105 such telegrams to the three
   units cover 337 slot registers: each returns the bytes of the single read of the same
   slot, and the first byte of each equals the same CRC-8 over all address bytes.

Toolchain: `scripts/check.sh` clean on both commits, 448 messages after the heating programs
and 574 after the hot-water and circulation programs (259 before the lot).

## Equipment

Three Kromschröder WCM-FS room units on eBUS at slave addresses `35`, `75` and `f5`, all
scanning as `MF=Kromschröder`, `ID=W`, SW=2726. Each drives one heating circuit through a
heating module (`50`, `51`, `52`). Two condensing boilers in cascade behind a system manager
(`15`, SW=6618), which prepares the hot water.

## Date

2026-11-17.

## Not verified

- **Which heating program a unit runs.** Register `12 01` (request `09 12 01`) answers
  `0b 00` = 11 on the three units. The running configuration calls it the program selector
  and maps 11, 12, 13 to programs 1, 2, 3; that list has no independent source, and the
  register is not in the lot. At the time of the reads (a Tuesday, 17:10) the three programs
  were all inside a heating period, so the room setpoint could not tell them apart. A way to
  close it without writing: read the room setpoint (`12 00`) on a Wednesday at midday, when
  program 1 is off and programs 2 and 3 are on.
- **The numbering of the heating programs.** 1, 2, 3 follow the ascending sub-bytes `14`,
  `15`, `16`, as in the running configuration. That sub-byte `14` is what the room unit
  shows as its first program was not compared with the display of a unit. Program 1 is the
  only one with a site schedule (Wednesday off); 2 and 3 are near-identical on the three
  units.
- **The labels hot water (`17`) and circulation (`1a`)** come from lot A (same sub-bytes on
  the module `50`) and from the running configuration; the shape of the schedules fits (one
  long period a day; three short ones around meal times), nothing more.
- **Whether a room unit applies its hot-water and circulation programs.** The three units
  answer identical values, and the registers the running configuration reads as their
  hot-water settings (`33 01`, `34 01`, `35 01`, `37 01`) answer `00 80`. The hot water of
  this installation is prepared by the system manager. The two programs are defined as what
  the device stores.
- Heating programs and the hot-water program were seen with slot 1 only; slots 2 and 3 carry
  switch times in the circulation program only.
- No slot was changed to see the register follow, and no write was tried (rule 7). A switch
  time at 24:00 or a period over midnight was not seen. Every slot was read once, in one
  afternoon.
- Not in the lot: the same sub-bytes are also answered by the heating modules (`50`, `51`,
  `52`), the system manager (`15`) and the device at `f6`, with heating programs as well.
  This contradicts the note of the lot A record that no heating program exists on this bus;
  it was not examined here (lot H is the room units).
- No write definition (`50 23`): the running configuration has one per slot and
  `docs/discoveries.md` (2026-10-30) says the slots accept any master, but no telegram was
  kept.

## Addition of 2026-11-17 (evening)

Three points of "Not verified" were examined the same day by reads around switch times, see
[modules-programs.md](modules-programs.md):

- The selector value 11 selects heating program 1, sub-byte `14` (the third unit went to
  setback at 18:00, the other two did not). 12 and 13 remain unproven.
- The room units do not apply their hot-water program on this installation: the hot-water
  set value of the system manager follows the manager's own program. The definitions were
  kept and their comments changed to "stored in the room unit" (commit `0784552` on
  `weishaupt-H`, comments only, IDs and fields unchanged, 574 messages).
- The programs of the heating modules, of the system manager and of `f6` were read; nothing
  was defined for them.
