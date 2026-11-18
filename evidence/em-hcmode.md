# em — room-controller / heating-module exchange (HcMode)

## What

Each heating module (EM) exchanges with its room controller using `PBSB = 50 14`. The room
controller sends the first part (requested flow setpoint, room temperature, heating/DHW flags),
the module answers with the second (operating mode, pump/valve flags, actual flow, outside,
boost, min/max flow). Modelled passively as `HcMode` (`src/wolf/wtc_inc.tsp`), wired per module:

| circuit | QQ (controller) | ZZ (module) | file |
|---|---|---|---|
| em1 | 30 | 50 | `src/wolf/50.w.em1.tsp` |
| em2 | 70 | 51 | `src/wolf/51.w.em2.tsp` |
| em3 | f0 | 52 | `src/wolf/52.w.em3.tsp` |

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

## The three exchanges, with their source (2026-11-18)

Passive capture of 2026-11-18, 10:25 (ebusd `grab result all`, nothing sent), one exchange
per heating circuit; master part, then slave answer after its length byte:

| circuit | QQ → ZZ | master part | slave answer |
|---|---|---|---|
| em1 | `30` → `50` | `01 00 06 4d 17 08 ff` | `00 00 00 80 00 0b 04 a4 10` |
| em2 | `70` → `51` | `01 00 05 e6 17 08 ff` | `00 00 00 19 00 9c 04 96 10` |
| em3 | `f0` → `52` | `03 00 1b b3 17 00 ff` | `00 01 cd 19 00 9c 02 96 10` |

By the layout above: em1 has no flow sensor (`00 80`, not available), outside 11.0 °C
(`00 0b`), boost 2.0 K, flow limits 82.0 and 8.0 °C; em2 has a flow temperature of 25.0 °C
(`00 19`), boost 2.0 K, limits 75.0 and 8.0 °C; em3 a flow temperature of 25.8 °C (`cd 19`),
boost 1.0 K, the same limits. The modules `51` and `52` have no outside sensor and send
`00 9c` there: -100.0 as a signed value with a fraction byte, the "no sensor" value of this
family ([ka-reads.md](ka-reads.md), `18 fc` on a register), not the eBUS replacement value
`00 80` that the note of 2026-11-16 above calls a sentinel.

**Finding: ebusd does not decode the exchange of `51` and `52`.** The field `OutsideTemp` of
the answer is defined with the range of its type (-50 to 127 °C, written into the CSV by the
compile option `withMinMax`). Fed with the two telegrams above, without a bus, the ebusd of
`scripts/check.sh` loaded with the lot files logs `unable to parse update-read em2 HcMode …:
ERR: argument value out of valid range` (the same for em3), and `read -c em2 HcMode` returns
that error; a single field other than the outside temperature can still be read
(`read -c em2 HcMode supplyhctemp` gives 25.000). The exchange of `50`, whose outside
temperature is a real value, decodes. On an installation whose module has no outside sensor,
`em2/HcMode` and `em3/HcMode` therefore give an error in place of their values (checked on
the CSV of release 0.4.3). Not corrected here: the model belongs to lot A.

## Equipment

Kromschröder WCM-FS heating modules (room units) on eBUS, `MF=Kromschröder`, three modules.

## Date

2026-11-16.

## Not verified

- The `Ink*` and `Opmode_*` bit fields are named but not interpreted.
- `BoilerMCBoostTemp`, `SupplyHCMaxTemp`, `SupplyHCMinTemp` were seen at a single operating
  point only.
- Modelled passively (observed), not actively polled, to stay read-only towards the system.
