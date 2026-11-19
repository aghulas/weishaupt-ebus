# fs1, fs2, fs3 — control variation of the room units (50 22 / 50 23)

## What

Lot C, branch `weishaupt-C` of the ebusd-configuration fork: `ControlVariation`, register
`41 01` of each room unit, read with `50 22` (request `25 41 01`) and written with `50 23` from
source address `ff`, the checksum of the write computed by ebusd at run time
([register-write-crc.md](register-write-crc.md)); files `src/wolf/35.w.fs1.tsp`,
`75.w.fs2.tsp`, `f5.w.fs3.tsp`. Two bytes, low byte first, an unsigned number (`UIN`), no list
of names.

## How it was established

Batch B of [choice-date-program-writes.md](choice-date-program-writes.md), "Ready to run",
sent on site on 2026-11-19 from 13:57:34 to 13:58:23 by the deployment session on the owner's
go, the vendor service tool disconnected: raw `hex` through ebusd, writes from `ff`, reads
from `31`. Before: `01 00` (1) on the three units, the value in service (the operator's log of
2026-11-15 has a write of that same value, `50 41 01 01 00` to `35`). Per unit: read, write 0,
read, ten seconds, write 1, read. From the telegram log of the installation, exported read
only (`2026-11-19-batch-B.csv`; the log keeps a write sent from `ff` without its source byte):

| unit | time | write `50 23` | ack | value | read `50 22` | answer |
|---|---|---|---|---|---|---|
| `35` | 13:57:34 | `0c 41 01 00 00` | `00` | 0 | `25 41 01` | `00 00` |
| `35` | 13:57:45 | `50 41 01 01 00` | `00` | 1 | `25 41 01` | `01 00` |
| `75` | 13:57:50 | `0c 41 01 00 00` | `00` | 0 | `25 41 01` | `00 00` |
| `75` | 13:58:01 | `50 41 01 01 00` | `00` | 1 | `25 41 01` | `01 00` |
| `f5` | 13:58:07 | `0c 41 01 00 00` | `00` | 0 | `25 41 01` | `00 00` |
| `f5` | 13:58:18 | `50 41 01 01 00` | `00` | 1 | `25 41 01` | `01 00` |

All six writes acknowledged `00` and read back with the value written.

## What value 0 did (observed, not a definition)

The deployment session followed the flow setpoint each heating module broadcasts in its
`HcMode` (ebusd's cache) during the batch:

| circuit | module | before | while 0 was set | after the restore |
|---|---|---|---|---|
| 1 (room unit `35`) | `50` | 47 °C | 60 °C, 6 s after the write, still 5 s after the restore | 47 °C at 13:58:29 |
| 2 (room unit `75`) | `51` | 48 °C | 75 °C, its maximum flow temperature, 10 s after the write, still 5 s after the restore | 48 °C at 13:58:29 |
| 3 (room unit `f5`) | `52` | 49 °C | no change seen (its next broadcast may have come after the ten seconds) | 49 °C |

On circuit 2 the mixing valve opened briefly: flow 46.7 → 50.4 °C, back to 49.6 °C at 14:00:15.
So with 0 the module raised the flow setpoint, on circuit 2 to the circuit's maximum; that
fits a constant flow setpoint, but neither the name of value 0 nor what 2 or 3 would do is
established. The client's table of the operator lists 0 constant flow, 1 weather-compensated,
2 weather and room, 3 room; no manual read so far names them. The definition keeps a number.

## Equipment

Three Kromschröder WCM-FS room units (`35`, `75`, `f5`, `SW=2726`), their heating modules at
`50` (the system manager's own circuit), `51`, `52`; a WCM-KA system manager and two WTC-GB
boilers.

## Date

2026-11-19.

## Not verified

- The meaning of each value; values 2 and 3 not tried.
- The effect of 0 on circuit 3.
- That 60 °C on circuit 1 is that circuit's maximum (its `SupplyMaxTemp` was not read then).
