# ka, em1, em2, em3 and `f6` — weekly programs outside the room units (50 22)

## What

No definition. This record settles what the devices other than the room units hold at the
program registers that lot A defines on `50` (hot water, circulation) and lot H on the room
units (three heating programs, hot water, circulation), which copy the installation applies,
and what was learned about the program selector `12 01`. It is the evidence for *not* adding
a lot (see "Why no definition").

Registers: `PBSB = 50 22`, ID `<crc> <addr> <sub>` (see [register-crc.md](register-crc.md)),
sub-bytes `14`, `15`, `16` (heating programs 1 to 3), `17` (hot water), `1a` (circulation);
address = weekday in the high nibble (`1` Monday to `7` Sunday), slot in the low nibble (`0`
to `2`). Answer: two bytes, stop time then start time, quarter hours in bits 0 to 6, bit 7 set
when the switch time is disabled (codec `SwitchTimes` of lot A,
[em1-clock-program.md](em1-clock-program.md)).

Devices read: the system manager (`15`), the device at `50` (file `50.w.em1`), the device at
`f6`, the heating modules `51` and `52`. 105 slots each, 525 in all.

## Result

| program | `15`, `50`, `f6` | `51`, `52` | room units `35`, `75`, `f5` (lot H) |
|---|---|---|---|
| heating 1 | 06:00 to 22:00 working days, 07:00 to 23:00 weekend | same as `15` | own schedules: four working days, Wednesday and weekend off; `f5` differs from `35` and `75` on Tuesday |
| heating 2 | 06:00 to 08:00 and 16:00 to 22:00 working days, 07:00 to 23:00 weekend | same as `15` | own schedules, 06:00 to 18:00 and a Saturday morning |
| heating 3 | 06:00 to 08:00 and 12:00 to 22:00 working days, 07:00 to 23:00 weekend | same as `15` | 06:00 to 22:00 working days, weekend off |
| hot water | 09:00 to 16:00 on Monday, Tuesday, Thursday, Friday; other days disabled | 05:00 to 21:00 working days, 06:00 to 22:00 weekend | same as `51` and `52` |
| circulation | all 21 slots disabled | three periods a day | same as `51` and `52` |

Slot by slot:

- **`15`, `50` and `f6` answer the same bytes on all 105 slots**, the hot-water schedule with
  its four non-contiguous weekdays included.
- **`51` and `52` answer the same bytes as each other on all 105 slots.** Their three heating
  programs equal those of `15` (63 of 63 slots); their hot-water and circulation programs
  equal those of the three room units (42 of 42 slots).
- **No module mirrors its room unit.** The heating programs of `50`, `51` and `52` differ from
  those of the room unit of the same circuit (`35`, `75`, `f5`) in every program.
- No device holds only disabled slots; the circulation program of `15` / `50` / `f6` is the one
  program that is entirely disabled.

Reading of it (inferred, not proven): the heating programs common to five devices of two
software versions (6618 and 7203), and the hot-water and circulation programs common to the
modules and the three room units, are most likely values nobody set on this site. The
schedules that carry site choices are the heating programs of the room units and the
hot-water program of the system manager. No manual was compared for factory values.

## Bytes read

Request payload, then for each device the two data bytes of the answer (length byte `02`
dropped) and the decoded slot, start to stop.

### Heating program 1 (sub-byte `14`)

| slot | addr sub | request | `15` | `50` | `f6` | `51` | `52` |
|---|---|---|---|---|---|---|---|
| Mon 1 | `10 14` | `a4 10 14` | `58 18` 06:00 to 22:00 | `58 18` 06:00 to 22:00 | `58 18` 06:00 to 22:00 | `58 18` 06:00 to 22:00 | `58 18` 06:00 to 22:00 |
| Mon 2 | `11 14` | `f8 11 14` | `80 80` disabled | `80 80` disabled | `80 80` disabled | `80 80` disabled | `80 80` disabled |
| Mon 3 | `12 14` | `1c 12 14` | `80 80` disabled | `80 80` disabled | `80 80` disabled | `80 80` disabled | `80 80` disabled |
| Tue 1 | `20 14` | `28 20 14` | `58 18` 06:00 to 22:00 | `58 18` 06:00 to 22:00 | `58 18` 06:00 to 22:00 | `58 18` 06:00 to 22:00 | `58 18` 06:00 to 22:00 |
| Tue 2 | `21 14` | `74 21 14` | `80 80` disabled | `80 80` disabled | `80 80` disabled | `80 80` disabled | `80 80` disabled |
| Tue 3 | `22 14` | `90 22 14` | `80 80` disabled | `80 80` disabled | `80 80` disabled | `80 80` disabled | `80 80` disabled |
| Wed 1 | `30 14` | `98 30 14` | `58 18` 06:00 to 22:00 | `58 18` 06:00 to 22:00 | `58 18` 06:00 to 22:00 | `58 18` 06:00 to 22:00 | `58 18` 06:00 to 22:00 |
| Wed 2 | `31 14` | `c4 31 14` | `80 80` disabled | `80 80` disabled | `80 80` disabled | `80 80` disabled | `80 80` disabled |
| Wed 3 | `32 14` | `20 32 14` | `80 80` disabled | `80 80` disabled | `80 80` disabled | `80 80` disabled | `80 80` disabled |
| Thu 1 | `40 14` | `6c 40 14` | `58 18` 06:00 to 22:00 | `58 18` 06:00 to 22:00 | `58 18` 06:00 to 22:00 | `58 18` 06:00 to 22:00 | `58 18` 06:00 to 22:00 |
| Thu 2 | `41 14` | `30 41 14` | `80 80` disabled | `80 80` disabled | `80 80` disabled | `80 80` disabled | `80 80` disabled |
| Thu 3 | `42 14` | `d4 42 14` | `80 80` disabled | `80 80` disabled | `80 80` disabled | `80 80` disabled | `80 80` disabled |
| Fri 1 | `50 14` | `dc 50 14` | `58 18` 06:00 to 22:00 | `58 18` 06:00 to 22:00 | `58 18` 06:00 to 22:00 | `58 18` 06:00 to 22:00 | `58 18` 06:00 to 22:00 |
| Fri 2 | `51 14` | `80 51 14` | `80 80` disabled | `80 80` disabled | `80 80` disabled | `80 80` disabled | `80 80` disabled |
| Fri 3 | `52 14` | `64 52 14` | `80 80` disabled | `80 80` disabled | `80 80` disabled | `80 80` disabled | `80 80` disabled |
| Sat 1 | `60 14` | `50 60 14` | `5c 1c` 07:00 to 23:00 | `5c 1c` 07:00 to 23:00 | `5c 1c` 07:00 to 23:00 | `5c 1c` 07:00 to 23:00 | `5c 1c` 07:00 to 23:00 |
| Sat 2 | `61 14` | `0c 61 14` | `80 80` disabled | `80 80` disabled | `80 80` disabled | `80 80` disabled | `80 80` disabled |
| Sat 3 | `62 14` | `e8 62 14` | `80 80` disabled | `80 80` disabled | `80 80` disabled | `80 80` disabled | `80 80` disabled |
| Sun 1 | `70 14` | `e0 70 14` | `5c 1c` 07:00 to 23:00 | `5c 1c` 07:00 to 23:00 | `5c 1c` 07:00 to 23:00 | `5c 1c` 07:00 to 23:00 | `5c 1c` 07:00 to 23:00 |
| Sun 2 | `71 14` | `bc 71 14` | `80 80` disabled | `80 80` disabled | `80 80` disabled | `80 80` disabled | `80 80` disabled |
| Sun 3 | `72 14` | `58 72 14` | `80 80` disabled | `80 80` disabled | `80 80` disabled | `80 80` disabled | `80 80` disabled |

### Heating program 2 (sub-byte `15`)

| slot | addr sub | request | `15` | `50` | `f6` | `51` | `52` |
|---|---|---|---|---|---|---|---|
| Mon 1 | `10 15` | `a5 10 15` | `20 18` 06:00 to 08:00 | `20 18` 06:00 to 08:00 | `20 18` 06:00 to 08:00 | `20 18` 06:00 to 08:00 | `20 18` 06:00 to 08:00 |
| Mon 2 | `11 15` | `f9 11 15` | `58 40` 16:00 to 22:00 | `58 40` 16:00 to 22:00 | `58 40` 16:00 to 22:00 | `58 40` 16:00 to 22:00 | `58 40` 16:00 to 22:00 |
| Mon 3 | `12 15` | `1d 12 15` | `80 80` disabled | `80 80` disabled | `80 80` disabled | `80 80` disabled | `80 80` disabled |
| Tue 1 | `20 15` | `29 20 15` | `20 18` 06:00 to 08:00 | `20 18` 06:00 to 08:00 | `20 18` 06:00 to 08:00 | `20 18` 06:00 to 08:00 | `20 18` 06:00 to 08:00 |
| Tue 2 | `21 15` | `75 21 15` | `58 40` 16:00 to 22:00 | `58 40` 16:00 to 22:00 | `58 40` 16:00 to 22:00 | `58 40` 16:00 to 22:00 | `58 40` 16:00 to 22:00 |
| Tue 3 | `22 15` | `91 22 15` | `80 80` disabled | `80 80` disabled | `80 80` disabled | `80 80` disabled | `80 80` disabled |
| Wed 1 | `30 15` | `99 30 15` | `20 18` 06:00 to 08:00 | `20 18` 06:00 to 08:00 | `20 18` 06:00 to 08:00 | `20 18` 06:00 to 08:00 | `20 18` 06:00 to 08:00 |
| Wed 2 | `31 15` | `c5 31 15` | `58 40` 16:00 to 22:00 | `58 40` 16:00 to 22:00 | `58 40` 16:00 to 22:00 | `58 40` 16:00 to 22:00 | `58 40` 16:00 to 22:00 |
| Wed 3 | `32 15` | `21 32 15` | `80 80` disabled | `80 80` disabled | `80 80` disabled | `80 80` disabled | `80 80` disabled |
| Thu 1 | `40 15` | `6d 40 15` | `20 18` 06:00 to 08:00 | `20 18` 06:00 to 08:00 | `20 18` 06:00 to 08:00 | `20 18` 06:00 to 08:00 | `20 18` 06:00 to 08:00 |
| Thu 2 | `41 15` | `31 41 15` | `58 40` 16:00 to 22:00 | `58 40` 16:00 to 22:00 | `58 40` 16:00 to 22:00 | `58 40` 16:00 to 22:00 | `58 40` 16:00 to 22:00 |
| Thu 3 | `42 15` | `d5 42 15` | `80 80` disabled | `80 80` disabled | `80 80` disabled | `80 80` disabled | `80 80` disabled |
| Fri 1 | `50 15` | `dd 50 15` | `20 18` 06:00 to 08:00 | `20 18` 06:00 to 08:00 | `20 18` 06:00 to 08:00 | `20 18` 06:00 to 08:00 | `20 18` 06:00 to 08:00 |
| Fri 2 | `51 15` | `81 51 15` | `58 40` 16:00 to 22:00 | `58 40` 16:00 to 22:00 | `58 40` 16:00 to 22:00 | `58 40` 16:00 to 22:00 | `58 40` 16:00 to 22:00 |
| Fri 3 | `52 15` | `65 52 15` | `80 80` disabled | `80 80` disabled | `80 80` disabled | `80 80` disabled | `80 80` disabled |
| Sat 1 | `60 15` | `51 60 15` | `5c 1c` 07:00 to 23:00 | `5c 1c` 07:00 to 23:00 | `5c 1c` 07:00 to 23:00 | `5c 1c` 07:00 to 23:00 | `5c 1c` 07:00 to 23:00 |
| Sat 2 | `61 15` | `0d 61 15` | `80 80` disabled | `80 80` disabled | `80 80` disabled | `80 80` disabled | `80 80` disabled |
| Sat 3 | `62 15` | `e9 62 15` | `80 80` disabled | `80 80` disabled | `80 80` disabled | `80 80` disabled | `80 80` disabled |
| Sun 1 | `70 15` | `e1 70 15` | `5c 1c` 07:00 to 23:00 | `5c 1c` 07:00 to 23:00 | `5c 1c` 07:00 to 23:00 | `5c 1c` 07:00 to 23:00 | `5c 1c` 07:00 to 23:00 |
| Sun 2 | `71 15` | `bd 71 15` | `80 80` disabled | `80 80` disabled | `80 80` disabled | `80 80` disabled | `80 80` disabled |
| Sun 3 | `72 15` | `59 72 15` | `80 80` disabled | `80 80` disabled | `80 80` disabled | `80 80` disabled | `80 80` disabled |

### Heating program 3 (sub-byte `16`)

| slot | addr sub | request | `15` | `50` | `f6` | `51` | `52` |
|---|---|---|---|---|---|---|---|
| Mon 1 | `10 16` | `a6 10 16` | `20 18` 06:00 to 08:00 | `20 18` 06:00 to 08:00 | `20 18` 06:00 to 08:00 | `20 18` 06:00 to 08:00 | `20 18` 06:00 to 08:00 |
| Mon 2 | `11 16` | `fa 11 16` | `58 30` 12:00 to 22:00 | `58 30` 12:00 to 22:00 | `58 30` 12:00 to 22:00 | `58 30` 12:00 to 22:00 | `58 30` 12:00 to 22:00 |
| Mon 3 | `12 16` | `1e 12 16` | `80 80` disabled | `80 80` disabled | `80 80` disabled | `80 80` disabled | `80 80` disabled |
| Tue 1 | `20 16` | `2a 20 16` | `20 18` 06:00 to 08:00 | `20 18` 06:00 to 08:00 | `20 18` 06:00 to 08:00 | `20 18` 06:00 to 08:00 | `20 18` 06:00 to 08:00 |
| Tue 2 | `21 16` | `76 21 16` | `58 30` 12:00 to 22:00 | `58 30` 12:00 to 22:00 | `58 30` 12:00 to 22:00 | `58 30` 12:00 to 22:00 | `58 30` 12:00 to 22:00 |
| Tue 3 | `22 16` | `92 22 16` | `80 80` disabled | `80 80` disabled | `80 80` disabled | `80 80` disabled | `80 80` disabled |
| Wed 1 | `30 16` | `9a 30 16` | `20 18` 06:00 to 08:00 | `20 18` 06:00 to 08:00 | `20 18` 06:00 to 08:00 | `20 18` 06:00 to 08:00 | `20 18` 06:00 to 08:00 |
| Wed 2 | `31 16` | `c6 31 16` | `58 30` 12:00 to 22:00 | `58 30` 12:00 to 22:00 | `58 30` 12:00 to 22:00 | `58 30` 12:00 to 22:00 | `58 30` 12:00 to 22:00 |
| Wed 3 | `32 16` | `22 32 16` | `80 80` disabled | `80 80` disabled | `80 80` disabled | `80 80` disabled | `80 80` disabled |
| Thu 1 | `40 16` | `6e 40 16` | `20 18` 06:00 to 08:00 | `20 18` 06:00 to 08:00 | `20 18` 06:00 to 08:00 | `20 18` 06:00 to 08:00 | `20 18` 06:00 to 08:00 |
| Thu 2 | `41 16` | `32 41 16` | `58 30` 12:00 to 22:00 | `58 30` 12:00 to 22:00 | `58 30` 12:00 to 22:00 | `58 30` 12:00 to 22:00 | `58 30` 12:00 to 22:00 |
| Thu 3 | `42 16` | `d6 42 16` | `80 80` disabled | `80 80` disabled | `80 80` disabled | `80 80` disabled | `80 80` disabled |
| Fri 1 | `50 16` | `de 50 16` | `20 18` 06:00 to 08:00 | `20 18` 06:00 to 08:00 | `20 18` 06:00 to 08:00 | `20 18` 06:00 to 08:00 | `20 18` 06:00 to 08:00 |
| Fri 2 | `51 16` | `82 51 16` | `58 30` 12:00 to 22:00 | `58 30` 12:00 to 22:00 | `58 30` 12:00 to 22:00 | `58 30` 12:00 to 22:00 | `58 30` 12:00 to 22:00 |
| Fri 3 | `52 16` | `66 52 16` | `80 80` disabled | `80 80` disabled | `80 80` disabled | `80 80` disabled | `80 80` disabled |
| Sat 1 | `60 16` | `52 60 16` | `5c 1c` 07:00 to 23:00 | `5c 1c` 07:00 to 23:00 | `5c 1c` 07:00 to 23:00 | `5c 1c` 07:00 to 23:00 | `5c 1c` 07:00 to 23:00 |
| Sat 2 | `61 16` | `0e 61 16` | `80 80` disabled | `80 80` disabled | `80 80` disabled | `80 80` disabled | `80 80` disabled |
| Sat 3 | `62 16` | `ea 62 16` | `80 80` disabled | `80 80` disabled | `80 80` disabled | `80 80` disabled | `80 80` disabled |
| Sun 1 | `70 16` | `e2 70 16` | `5c 1c` 07:00 to 23:00 | `5c 1c` 07:00 to 23:00 | `5c 1c` 07:00 to 23:00 | `5c 1c` 07:00 to 23:00 | `5c 1c` 07:00 to 23:00 |
| Sun 2 | `71 16` | `be 71 16` | `80 80` disabled | `80 80` disabled | `80 80` disabled | `80 80` disabled | `80 80` disabled |
| Sun 3 | `72 16` | `5a 72 16` | `80 80` disabled | `80 80` disabled | `80 80` disabled | `80 80` disabled | `80 80` disabled |

### Hot-water program (sub-byte `17`)

| slot | addr sub | request | `15` | `50` | `f6` | `51` | `52` |
|---|---|---|---|---|---|---|---|
| Mon 1 | `10 17` | `a7 10 17` | `40 24` 09:00 to 16:00 | `40 24` 09:00 to 16:00 | `40 24` 09:00 to 16:00 | `54 14` 05:00 to 21:00 | `54 14` 05:00 to 21:00 |
| Mon 2 | `11 17` | `fb 11 17` | `80 80` disabled | `80 80` disabled | `80 80` disabled | `80 80` disabled | `80 80` disabled |
| Mon 3 | `12 17` | `1f 12 17` | `80 80` disabled | `80 80` disabled | `80 80` disabled | `80 80` disabled | `80 80` disabled |
| Tue 1 | `20 17` | `2b 20 17` | `40 24` 09:00 to 16:00 | `40 24` 09:00 to 16:00 | `40 24` 09:00 to 16:00 | `54 14` 05:00 to 21:00 | `54 14` 05:00 to 21:00 |
| Tue 2 | `21 17` | `77 21 17` | `80 80` disabled | `80 80` disabled | `80 80` disabled | `80 80` disabled | `80 80` disabled |
| Tue 3 | `22 17` | `93 22 17` | `80 80` disabled | `80 80` disabled | `80 80` disabled | `80 80` disabled | `80 80` disabled |
| Wed 1 | `30 17` | `9b 30 17` | `80 80` disabled | `80 80` disabled | `80 80` disabled | `54 14` 05:00 to 21:00 | `54 14` 05:00 to 21:00 |
| Wed 2 | `31 17` | `c7 31 17` | `80 80` disabled | `80 80` disabled | `80 80` disabled | `80 80` disabled | `80 80` disabled |
| Wed 3 | `32 17` | `23 32 17` | `80 80` disabled | `80 80` disabled | `80 80` disabled | `80 80` disabled | `80 80` disabled |
| Thu 1 | `40 17` | `6f 40 17` | `40 24` 09:00 to 16:00 | `40 24` 09:00 to 16:00 | `40 24` 09:00 to 16:00 | `54 14` 05:00 to 21:00 | `54 14` 05:00 to 21:00 |
| Thu 2 | `41 17` | `33 41 17` | `80 80` disabled | `80 80` disabled | `80 80` disabled | `80 80` disabled | `80 80` disabled |
| Thu 3 | `42 17` | `d7 42 17` | `80 80` disabled | `80 80` disabled | `80 80` disabled | `80 80` disabled | `80 80` disabled |
| Fri 1 | `50 17` | `df 50 17` | `40 24` 09:00 to 16:00 | `40 24` 09:00 to 16:00 | `40 24` 09:00 to 16:00 | `54 14` 05:00 to 21:00 | `54 14` 05:00 to 21:00 |
| Fri 2 | `51 17` | `83 51 17` | `80 80` disabled | `80 80` disabled | `80 80` disabled | `80 80` disabled | `80 80` disabled |
| Fri 3 | `52 17` | `67 52 17` | `80 80` disabled | `80 80` disabled | `80 80` disabled | `80 80` disabled | `80 80` disabled |
| Sat 1 | `60 17` | `53 60 17` | `80 80` disabled | `80 80` disabled | `80 80` disabled | `58 18` 06:00 to 22:00 | `58 18` 06:00 to 22:00 |
| Sat 2 | `61 17` | `0f 61 17` | `80 80` disabled | `80 80` disabled | `80 80` disabled | `80 80` disabled | `80 80` disabled |
| Sat 3 | `62 17` | `eb 62 17` | `80 80` disabled | `80 80` disabled | `80 80` disabled | `80 80` disabled | `80 80` disabled |
| Sun 1 | `70 17` | `e3 70 17` | `80 80` disabled | `80 80` disabled | `80 80` disabled | `58 18` 06:00 to 22:00 | `58 18` 06:00 to 22:00 |
| Sun 2 | `71 17` | `bf 71 17` | `80 80` disabled | `80 80` disabled | `80 80` disabled | `80 80` disabled | `80 80` disabled |
| Sun 3 | `72 17` | `5b 72 17` | `80 80` disabled | `80 80` disabled | `80 80` disabled | `80 80` disabled | `80 80` disabled |

### Circulation program (sub-byte `1a`)

| slot | addr sub | request | `15` | `50` | `f6` | `51` | `52` |
|---|---|---|---|---|---|---|---|
| Mon 1 | `10 1a` | `aa 10 1a` | `80 80` disabled | `80 80` disabled | `80 80` disabled | `1c 18` 06:00 to 07:00 | `1c 18` 06:00 to 07:00 |
| Mon 2 | `11 1a` | `f6 11 1a` | `80 80` disabled | `80 80` disabled | `80 80` disabled | `34 2c` 11:00 to 13:00 | `34 2c` 11:00 to 13:00 |
| Mon 3 | `12 1a` | `12 12 1a` | `80 80` disabled | `80 80` disabled | `80 80` disabled | `4c 44` 17:00 to 19:00 | `4c 44` 17:00 to 19:00 |
| Tue 1 | `20 1a` | `26 20 1a` | `80 80` disabled | `80 80` disabled | `80 80` disabled | `1c 18` 06:00 to 07:00 | `1c 18` 06:00 to 07:00 |
| Tue 2 | `21 1a` | `7a 21 1a` | `80 80` disabled | `80 80` disabled | `80 80` disabled | `34 2c` 11:00 to 13:00 | `34 2c` 11:00 to 13:00 |
| Tue 3 | `22 1a` | `9e 22 1a` | `80 80` disabled | `80 80` disabled | `80 80` disabled | `4c 44` 17:00 to 19:00 | `4c 44` 17:00 to 19:00 |
| Wed 1 | `30 1a` | `96 30 1a` | `80 80` disabled | `80 80` disabled | `80 80` disabled | `1c 18` 06:00 to 07:00 | `1c 18` 06:00 to 07:00 |
| Wed 2 | `31 1a` | `ca 31 1a` | `80 80` disabled | `80 80` disabled | `80 80` disabled | `34 2c` 11:00 to 13:00 | `34 2c` 11:00 to 13:00 |
| Wed 3 | `32 1a` | `2e 32 1a` | `80 80` disabled | `80 80` disabled | `80 80` disabled | `4c 44` 17:00 to 19:00 | `4c 44` 17:00 to 19:00 |
| Thu 1 | `40 1a` | `62 40 1a` | `80 80` disabled | `80 80` disabled | `80 80` disabled | `1c 18` 06:00 to 07:00 | `1c 18` 06:00 to 07:00 |
| Thu 2 | `41 1a` | `3e 41 1a` | `80 80` disabled | `80 80` disabled | `80 80` disabled | `34 2c` 11:00 to 13:00 | `34 2c` 11:00 to 13:00 |
| Thu 3 | `42 1a` | `da 42 1a` | `80 80` disabled | `80 80` disabled | `80 80` disabled | `4c 44` 17:00 to 19:00 | `4c 44` 17:00 to 19:00 |
| Fri 1 | `50 1a` | `d2 50 1a` | `80 80` disabled | `80 80` disabled | `80 80` disabled | `1c 18` 06:00 to 07:00 | `1c 18` 06:00 to 07:00 |
| Fri 2 | `51 1a` | `8e 51 1a` | `80 80` disabled | `80 80` disabled | `80 80` disabled | `34 2c` 11:00 to 13:00 | `34 2c` 11:00 to 13:00 |
| Fri 3 | `52 1a` | `6a 52 1a` | `80 80` disabled | `80 80` disabled | `80 80` disabled | `4c 44` 17:00 to 19:00 | `4c 44` 17:00 to 19:00 |
| Sat 1 | `60 1a` | `5e 60 1a` | `80 80` disabled | `80 80` disabled | `80 80` disabled | `20 1c` 07:00 to 08:00 | `20 1c` 07:00 to 08:00 |
| Sat 2 | `61 1a` | `02 61 1a` | `80 80` disabled | `80 80` disabled | `80 80` disabled | `34 2c` 11:00 to 13:00 | `34 2c` 11:00 to 13:00 |
| Sat 3 | `62 1a` | `e6 62 1a` | `80 80` disabled | `80 80` disabled | `80 80` disabled | `4c 44` 17:00 to 19:00 | `4c 44` 17:00 to 19:00 |
| Sun 1 | `70 1a` | `ee 70 1a` | `80 80` disabled | `80 80` disabled | `80 80` disabled | `20 1c` 07:00 to 08:00 | `20 1c` 07:00 to 08:00 |
| Sun 2 | `71 1a` | `b2 71 1a` | `80 80` disabled | `80 80` disabled | `80 80` disabled | `34 2c` 11:00 to 13:00 | `34 2c` 11:00 to 13:00 |
| Sun 3 | `72 1a` | `56 72 1a` | `80 80` disabled | `80 80` disabled | `80 80` disabled | `4c 44` 17:00 to 19:00 | `4c 44` 17:00 to 19:00 |
## How it was established

1. **Read.** Each of the 525 slots was read once through the running ebusd (master `31`),
   forced to the bus, one register per telegram, reads spaced, on 2026-11-17 between 17:30
   and 17:37. All were answered. Two reads first failed on the network link to ebusd and were
   repeated.
2. **Bytes.** Request and answer come from the passive capture of the same ebusd
   (`grab result all`), snapshots of 17:30:26 and 17:36:56: `31 → 15 / 50 / f6 / 51 / 52`,
   `50 22`, three request bytes, answer `02 <stop> <start>`. Each of the 525 telegrams has a
   higher count in the second snapshot than in the first. They are the bytes of the tables.
3. **Checksum.** The first request byte was recomputed offline for the 105 requests with the
   routine of [register-crc.md](register-crc.md) (CRC-8, polynomial 0x5C, initial value =
   first address byte, over the address bytes) and equals the byte on the bus for the 525
   telegrams. The requests are byte for byte those of lot H on the room units.
4. **Comparison with the room units.** The room-unit side is the table of
   [room-units-programs.md](room-units-programs.md) (read the same day, 17:07 to 17:11). 280
   of its 315 slots were still in the capture of 17:36 and are unchanged; the other 35 were
   not read again.
5. **Lot A.** The 42 hot-water and circulation slots of `50` equal the table of
   [em1-clock-program.md](em1-clock-program.md), 42 of 42.

## Which copy is applied

### Hot water: the program of the system manager

Hot-water set value of the system manager (`03 00`, request `e4 03 00`, tenths) against its
hot-water setpoint (`13 00`, `f4 01` = 50.0) and its minimum (8.0):

| time (Tuesday) | `15` answers | system manager program (09:00 to 16:00) | room unit / module program (05:00 to 21:00) |
|---|---|---|---|
| 11:17 | 50.0 | inside | inside |
| 17:39 | `50 00` = 8.0 | outside | inside |
| 17:56 | 8.0 | outside | inside |
| 18:03 | `50 00` = 8.0 | outside | inside |

The tank sensor read 27.6 at 17:39 (`0e 00`, `14 01`) and was not being reheated. The set
value is down at a time when the program of the room units and of the modules still asks for
hot water, so that program is not the one applied; the set value follows the 09:00 to 16:00
period of the system manager. `50` and `f6` answered the same values (`50 00`, `f4 01`,
`13 01` = 27.5) in the same minute.

Limits: the 11:17 value is the cached read of the running ebusd as listed in its inventory
of 11:41, not a read of this session; the switch itself (09:00 or 16:00) was not watched;
one day only.

### Heating, third circuit: the program of the room unit

On a Tuesday the heating programs disagree at 18:00: on room unit `f5` programs 1 and 2 end
at 18:00 and program 3 at 22:00; on `35` and `75` program 1 ends at 22:30, program 2 at
18:00, program 3 at 22:00; every heating program of `15`, `50`, `51`, `52` runs to 22:00.
Reads at 17:56 and 18:03, bytes from the capture snapshots of 17:56:44 and 18:03:50:

| register | request | device | 17:56 | 18:03 |
|---|---|---|---|---|
| room setpoint `12 00` | `08 12 00` | `35` | `d2 00` 21.0 | `d2 00` 21.0 |
| | | `75` | `d2 00` 21.0 | `d2 00` 21.0 |
| | | `f5` | `d2 00` 21.0 | `8c 00` 14.0 |
| heat demand `02 00` | `b8 02 00` | `35` | `a7 01` 42.3 | `a7 01` 42.3 |
| | | `75` | `c2 01` 45.0 | `c2 01` 45.0 |
| | | `f5` | `ca 01` 45.8 | `d6 00` 21.4 |
| flow setpoint `04 00` | `2c 04 00` | `35` | `a7 01` 42.3 | `a7 01` 42.3 |
| | | `75` | `ae 01` 43.0 | `ae 01` 43.0 |
| | | `f5` | `b6 01` 43.8 | `c2 00` 19.4 |
| | | `51` | `ae 01` 43.0 | `ae 01` 43.0 |
| | | `52` | `ae 01` 43.0 | `be 00` 19.0 |
| selector `12 01` | `09 12 01` | `35`, `75`, `f5` | `0b 00` 11 | `0b 00` 11 |

Passive telegrams of the third room unit in the same snapshots: to its module (`f0 → 52`,
`50 14`) `03 00 2b cd 1c 00 ff` before and `01 00 13 66 1c 00 ff` after (flow setpoint 43,
then 19); to the cascade (`f0 → f1`, `05 07`) `bb ff dd 02 …` (45.8) before and
`55 ff 56 01 …` (21.4) after. The telegrams of the first and second unit did not change.

14.0 is the setback room temperature of the unit (`08 00`, `8c 00`), 21.0 its normal one.
So at 18:00 the third room unit went to setback and the flow setpoint of its module `52`
followed, although every heating program stored in `52` (and in `15`) runs to 22:00: on the
third circuit the copy applied is the room unit's, and the module does not apply its own.

Not shown for the first and second circuit: their room units stay in the heating period
until 22:30 and the programs of `50` and `51` until 22:00, so nothing told them apart at
18:00. A read of the same registers on a Tuesday between 22:05 and 22:25 would: the room
units still at 21.0 with the modules' programs over means the room-unit copy, again.

## Program selector `12 01`

| device | answers (2026-11-17) |
|---|---|
| `35`, `75`, `f5` | `0b 00` = 11 at every read (08:40 to 18:03) |
| `15` | `0b 00` = 11 at every read (09:03, 15:18, 17:39, 17:41) |
| `51`, `52` | `0c 00` = 12 at every read |
| `50` | a different value at each read: 53728, 42254 (`0e a5`), 2, 9613 (`8d 25`) |
| `f6` | a different value at each read: 35544, 1023 (`ff 03`), 16, 24908 (`4c 61`) |

The values of the morning and early afternoon are cached reads of the running ebusd from its
inventories; those from 17:38 on are reads of this session.

What the 18:00 observation proves, with the tables of lot H:

- `f5` went to setback at 18:00: it runs program 1 or 2 (both end at 18:00), not program 3.
- `35` and `75` did not: they run program 1 or 3, not program 2.
- The three units have the same software version and the same selector value, 11. One value
  list for one firmware leaves a single program consistent with all three: **11 selects
  heating program 1, the program at sub-byte `14`.** This also settles that sub-byte `14` is
  the program a unit set to 11 follows.

Not proven: that 12 and 13 select programs 2 and 3 (sub-bytes `15`, `16`), as the running
configuration has it, and any other value of the list. `51` and `52` answer 12, but their
own programs are not applied (above), so their value shows nothing. The register is not
stored at `50` and `f6`, where it changes from read to read.

What would close it without a write by this project: a room unit whose operator has set
another program, then the same before-and-after reads at a switch time where that program
differs from program 1 (with today's schedules: any Wednesday between 06:00 and 18:00, when
program 1 is off and programs 2 and 3 are on). A direct confirmation of 11 on the first two
units: Tuesday between 22:05 and 22:25 (program 1 on, program 3 off).

## `50` and `f6` against the system manager

For one device answering at three addresses:

- 105 of 105 program slots identical on `15`, `50` and `f6`, among them a hot-water schedule
  set on site, which `51` and `52` do not have.
- Same software version (6618); hot-water set value, setpoint and tank temperature equal
  within 0.1 K in the same minute; heat demand 51.8 on the three.
- `f1` / `f6` is the address the room units send their heat demand to (`05 07`), the role of
  the cascade manager; `50` is the address the first room unit exchanges `50 14` with.

Against a plain alias: register `12 01` is stable at `15` and changes at every read at `50`
and at `f6`. So the three addresses are not three views of one register table in every
respect; the address is part of what is answered.

Conclusion kept to what the reads show: the three addresses return the same stored programs
and the same values wherever a value was compared, except `12 01`. That fits one device with
three roles (system manager, cascade manager, first heating circuit); three devices kept in
step is not excluded by bus reads alone. Proof would be a change of one slot at one address
seen at the other two (a write, rule 7: the operator's), or the wiring.

## Why no definition

- **Heating programs of `15`, `50`, `f6`, `51`, `52`**: stored and readable, but identical
  on five devices, different from every room unit, and on the third circuit shown not to be
  applied. 63 messages per device that describe a schedule the installation does not follow
  would mislead a user. Whether they apply on an installation without room units is not
  known.
- **Hot-water and circulation programs of `51` and `52`**: the same 42 slots as the room
  units (lot H), and the hot-water one is shown not to be applied.
- **Hot-water and circulation programs of `15` and `f6`**: the program that is applied, and
  already defined by lot A at `50` (`DHWProgram…`, `CircProgram…` in `50.w.em1`), identical
  on 42 of 42 slots. Defining them again at `15` would be a copy of the same messages.
- **Selector `12 01`**: one value of its list is proven (11); a read-only number with one
  known value is left out until a second value is seen.

## Equipment

System manager at slave address `15` (SW=6618), devices with the same software version at
`50` and `f6`, two heating modules at `51` and `52` (SW=7203), three WCM-FS room units at
`35`, `75`, `f5` (SW=2726), all scanning as `MF=Kromschröder`, `ID=W`. Three heating
circuits, two condensing boilers in cascade, hot water prepared by the system manager.

## Date

2026-11-17 (a Tuesday), 17:30 to 18:04.

## Not verified

- Factory values: the reading "not set on this site" for the common programs is an inference
  from their being identical across devices.
- The hot-water switch times themselves, and the circulation output: the circulation program
  applied is all disabled, nothing was observed about the pump.
- Which heating copy the first and second circuit apply (see above for the read that shows
  it), and what the heating programs of `50` are for.
- Values 12 and 13 of the selector; where the room unit stores the choice shown as 12 by the
  modules.
- Every slot was read once, in one afternoon; no write was sent (rule 7).
