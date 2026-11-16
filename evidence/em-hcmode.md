# em — room-controller / heating-module exchange (HcMode)

## What

Each heating module (EM) exchanges with its room controller using `PBSB = 50 14`. The room
controller sends the first part (requested flow setpoint, room temperature, heating/DHW flags),
the module answers with the second (operating mode, pump/valve flags, actual flow, outside,
boost, min/max flow). Modelled passively as `HcMode` (`src/wolf/wtc_inc.tsp`), wired per module:

| circuit | QQ (controller) | ZZ (module) | file |
|---|---|---|---|
| em1 | 30 | 50 | `src/wolf/50..em1.tsp` |
| em2 | 70 | 51 | `src/wolf/51..em2.tsp` |
| em3 | f0 | 52 | `src/wolf/52..em3.tsp` |

## How it was established

Live bus, passive capture (ebusd `grab result all`). Exchange for em1 (`QQ=30 → ZZ=50`,
`PBSB=5014`), master part then slave answer, trimmed:

```
master: 01 00 31 4d 1b 08 ff
slave : 00 00 00 80 00 0b 04 a4 10
```

Decoded (slave part): `OutsideTemp` (D2B) = `00 0b` = **11.0 °C**, matching the register reads
and the boiler status captured the same session; `SupplyHCTemp` = `00 80` = the no-sensor
sentinel on this module. On em2 the opposite holds (`SupplyHCTemp` = `4d 32` = 50.3 °C,
`OutsideTemp` sentinel), which is consistent with different sensors wired per module and
confirms the field offsets either way.

Toolchain: `tsp compile`, `tsp format --check`, `ebusd --checkconfig` all clean (0 errors).
`ZZ` comes from each file name (50/51/52).

## Equipment

Kromschröder WCM-FS heating modules (room units) on eBUS, `MF=Kromschröder`, three modules.

## Date

2026-11-16.

## Not verified

- The `Ink*` and `Opmode_*` bit fields are named but not interpreted.
- `BoilerMCBoostTemp`, `SupplyHCMaxTemp`, `SupplyHCMinTemp` were seen at a single operating
  point only.
- Modelled passively (observed), not actively polled, to stay read-only towards the system.
