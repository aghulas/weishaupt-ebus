# fs1, fs2, fs3 — holiday dates of the room units (50 22 / 50 23)

## What

Lot C, branch `weishaupt-C` of the ebusd-configuration fork: six settings on each room unit,
read with `50 22` and written with `50 23` from source address `ff`, the checksum of the write
computed by ebusd at run time (see [register-write-crc.md](register-write-crc.md)); files
`src/wolf/35.w.fs1.tsp`, `75.w.fs2.tsp`, `f5.w.fs3.tsp`.

| message | register | read request | content |
|---|---|---|---|
| `HolidayStartDay` | `1b 01` | `0d 1b 01` | day of the month the holiday period starts, 1 to 31 |
| `HolidayStartMonth` | `1c 01` | `c5 1c 01` | month it starts, 1 to 12 |
| `HolidayStartThird` | `1d 01` | `99 1d 01` | third register of the start date, meaning not established |
| `HolidayEndDay` | `1e 01` | `7d 1e 01` | day of the month it ends |
| `HolidayEndMonth` | `1f 01` | `21 1f 01` | month it ends |
| `HolidayEndThird` | `20 01` | `3d 20 01` | third register of the end date, meaning not established |

Each value is two bytes, low byte first, an unsigned number (`UIN`).

## How it was established

Batch D of [choice-date-program-writes.md](choice-date-program-writes.md), section "Ready to
run", sent on site on 2026-11-19 from 13:55:45 to 13:56:19 by the deployment session on the
owner's go, the vendor service tool disconnected: raw `hex` through ebusd, each write from
`ff`, each read from ebusd's own address `31`. Before: the stored period 30.10 to 01.11, both
third registers 0, holiday level `3d 01` 0 (frost protection) on the three units. Order per
unit: start day changed and restored; start month to 9 and kept while the end month went to
10 and back, then restored; end day changed and restored; end third to 24 and kept while the
start third went to 24 and back, then restored. Every intermediate period lay in the past, the
start before the end.

Every write was acknowledged `00`, and the read that followed it gave the value written: 18
changes and 18 restores, 36 of 36. The holiday level read 0 before and after on each unit.
Room unit 2 (`75`), which keeps no program-slot write, takes these. From the telegram log of
the installation, exported read only (`2026-11-19-batch-D.csv`): the write as master data of
`50 23` (the log keeps a write sent from `ff` without its source byte), its acknowledgement,
then the read and its answer.

| unit | time | register | write `50 23` | ack | value | read `50 22` | answer |
|---|---|---|---|---|---|---|---|
| `35` | 13:55:47 | start day | `fc 1b 01 1d 00` | `00` | 29 | `0d 1b 01` | `1d 00` |
| `35` | 13:55:47 | start day | `18 1b 01 1e 00` | `00` | 30 | `0d 1b 01` | `1e 00` |
| `35` | 13:55:47 | start month | `58 1c 01 09 00` | `00` | 9 | `c5 1c 01` | `09 00` |
| `35` | 13:55:48 | end month | `a4 1f 01 0a 00` | `00` | 10 | `21 1f 01` | `0a 00` |
| `35` | 13:55:48 | end month | `f8 1f 01 0b 00` | `00` | 11 | `21 1f 01` | `0b 00` |
| `35` | 13:55:48 | start month | `bc 1c 01 0a 00` | `00` | 10 | `c5 1c 01` | `0a 00` |
| `35` | 13:55:49 | end day | `f4 1e 01 02 00` | `00` | 2 | `7d 1e 01` | `02 00` |
| `35` | 13:55:49 | end day | `10 1e 01 01 00` | `00` | 1 | `7d 1e 01` | `01 00` |
| `35` | 13:55:50 | end, third | `08 20 01 18 00` | `00` | 24 | `3d 20 01` | `18 00` |
| `35` | 13:55:50 | start, third | `bc 1d 01 18 00` | `00` | 24 | `99 1d 01` | `18 00` |
| `35` | 13:55:51 | start, third | `54 1d 01 00 00` | `00` | 0 | `99 1d 01` | `00 00` |
| `35` | 13:55:51 | end, third | `e0 20 01 00 00` | `00` | 0 | `3d 20 01` | `00 00` |
| `75` | 13:55:57 | start day | `fc 1b 01 1d 00` | `00` | 29 | `0d 1b 01` | `1d 00` |
| `75` | 13:55:57 | start day | `18 1b 01 1e 00` | `00` | 30 | `0d 1b 01` | `1e 00` |
| `75` | 13:55:58 | start month | `58 1c 01 09 00` | `00` | 9 | `c5 1c 01` | `09 00` |
| `75` | 13:55:58 | end month | `a4 1f 01 0a 00` | `00` | 10 | `21 1f 01` | `0a 00` |
| `75` | 13:55:59 | end month | `f8 1f 01 0b 00` | `00` | 11 | `21 1f 01` | `0b 00` |
| `75` | 13:55:59 | start month | `bc 1c 01 0a 00` | `00` | 10 | `c5 1c 01` | `0a 00` |
| `75` | 13:56:00 | end day | `f4 1e 01 02 00` | `00` | 2 | `7d 1e 01` | `02 00` |
| `75` | 13:56:00 | end day | `10 1e 01 01 00` | `00` | 1 | `7d 1e 01` | `01 00` |
| `75` | 13:56:01 | end, third | `08 20 01 18 00` | `00` | 24 | `3d 20 01` | `18 00` |
| `75` | 13:56:01 | start, third | `bc 1d 01 18 00` | `00` | 24 | `99 1d 01` | `18 00` |
| `75` | 13:56:02 | start, third | `54 1d 01 00 00` | `00` | 0 | `99 1d 01` | `00 00` |
| `75` | 13:56:02 | end, third | `e0 20 01 00 00` | `00` | 0 | `3d 20 01` | `00 00` |
| `f5` | 13:56:13 | start day | `fc 1b 01 1d 00` | `00` | 29 | `0d 1b 01` | `1d 00` |
| `f5` | 13:56:13 | start day | `18 1b 01 1e 00` | `00` | 30 | `0d 1b 01` | `1e 00` |
| `f5` | 13:56:14 | start month | `58 1c 01 09 00` | `00` | 9 | `c5 1c 01` | `09 00` |
| `f5` | 13:56:14 | end month | `a4 1f 01 0a 00` | `00` | 10 | `21 1f 01` | `0a 00` |
| `f5` | 13:56:15 | end month | `f8 1f 01 0b 00` | `00` | 11 | `21 1f 01` | `0b 00` |
| `f5` | 13:56:15 | start month | `bc 1c 01 0a 00` | `00` | 10 | `c5 1c 01` | `0a 00` |
| `f5` | 13:56:16 | end day | `f4 1e 01 02 00` | `00` | 2 | `7d 1e 01` | `02 00` |
| `f5` | 13:56:16 | end day | `10 1e 01 01 00` | `00` | 1 | `7d 1e 01` | `01 00` |
| `f5` | 13:56:17 | end, third | `08 20 01 18 00` | `00` | 24 | `3d 20 01` | `18 00` |
| `f5` | 13:56:17 | start, third | `bc 1d 01 18 00` | `00` | 24 | `99 1d 01` | `18 00` |
| `f5` | 13:56:17 | start, third | `54 1d 01 00 00` | `00` | 0 | `99 1d 01` | `00 00` |
| `f5` | 13:56:18 | end, third | `e0 20 01 00 00` | `00` | 0 | `3d 20 01` | `00 00` |

## What the third register is

Not settled. Both third registers took 24 (`18 00`) and 0 and read them back on the three
units, with the dates of a period in the past. Nothing seen tells a year, a year offset or any
other unit apart: the values 0 and 24 are all that was written. The operator's log of
2026-11-07 reports the third register set back to 0 when the start written is the day of the
write; that was not tried here. The messages are named `...Third` and carry no unit and no
range.

## Day and month

The ranges 1 to 31 and 1 to 12 are those of a calendar date; the values written and read here
(1, 2, 9 to 11, 29, 30) lie inside them. Whether a unit refuses a day that the month does not
have was not tried.

## Equipment

Three Kromschröder WCM-FS room units (`35`, `75`, `f5`, `SW=2726`) of a system with a WCM-KA
system manager, two WCM-EM heating modules and two WTC-GB boilers.

## Date

2026-11-19.

## Not verified

- The meaning of the third register of each date, and its range.
- The effect of a period that covers the day (not written: the batch kept every period in the
  past). The holiday level decides what the circuit does during a period (`HolidayTempLevel`).
- A day the month does not have.
