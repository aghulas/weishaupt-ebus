# ka — modulation limits of the cascade (50 22 / 50 23)

## What

Lot C, branch `weishaupt-C` of the ebusd-configuration fork, file `src/wolf/15.w.ka.tsp`:
two settings of the system manager (`15`), read with `50 22` and written with `50 23` from
source address `ff`, the checksum of the write computed by ebusd at run time
([register-write-crc.md](register-write-crc.md)). Two bytes, low byte first, percent.

| message | register | read request | vendor | value in service |
|---|---|---|---|---|
| `ModulationMax` | `ea fd` | `a9 ea fd` | "Max. limit opt. operating range", parameter 535 | 80 % |
| `ModulationMin` | `eb fd` | `f5 eb fd` | "Min. limit opt. operating range", parameter 536 | 30 % |

The names and values in service are those of the vendor service tool
([service-tool-log.md](service-tool-log.md): `ff 15 0902 ea fd 02 / 50 00` and
`... eb fd 02 / 1e 00`). Range: the lower limit 30 % to the upper limit, the upper limit the
lower limit to 100 % (WCM-KA 3.0, document 83258404, pages 84 and 85); the definition carries
30 to 100 on both, the dependence between them is not expressed.

## How it was established

Batch F of [choice-date-program-writes.md](choice-date-program-writes.md), "Ready to run",
sent on site on 2026-11-19 from 14:00:38 to 14:01:07 by the deployment session on the owner's
go, the vendor service tool disconnected: raw `hex` through ebusd, writes from `ff`, reads from
`31`. Before: `50 00` and `1e 00`. From the telegram log, exported read only
(`2026-11-19-batch-F.csv`; a write from `ff` is kept without its source byte):

| time | message | write `50 23` | ack | value | read `50 22` | answer |
|---|---|---|---|---|---|---|
| 14:00:38 | `ModulationMax` | `38 ea fd 4f 00` | `00` | 79 % | `a9 ea fd` | `4f 00` |
| 14:00:45 | `ModulationMax` | `18 ea fd 50 00` | `00` | 80 % | `a9 ea fd` | `50 00` |
| 14:00:57 | `ModulationMin` | `f8 eb fd 1f 00` | `00` | 31 % | `f5 eb fd` | `1f 00` |
| 14:01:04 | `ModulationMin` | `a4 eb fd 1e 00` | `00` | 30 % | `f5 eb fd` | `1e 00` |

All four writes acknowledged `00` and read back with the value written. Both boilers were off
(burner off, load 0) before and after, and the system manager's modulation read 8 %: no effect
on the heating could be seen, nor was one expected for a minute at one percent.

## Equipment

Kromschröder WCM-KA system manager (`15`) of a cascade of two WTC-GB boilers.

## Date

2026-11-19.

## Not verified

- A value outside the range, or a lower limit above the upper one: not tried.
- The effect of the limits on the staging of the boilers.
