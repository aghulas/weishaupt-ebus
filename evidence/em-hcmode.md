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
the CSV of release 0.4.3). Corrected in lot A the same day, next section.

## Correction: a type without range for the outside temperature (2026-11-18)

**Why ebusd refused.** The answer part of `HcMode` had `OutsideTemp: temp2`. `temp2` is the
shared template of the official configuration: `D2B` (signed, one fraction byte) in °C with
the range -50 to 127 and a step of 0.5, which the compile option `withMinMax` writes into the
CSV (`-50-127:0.5`). ebusd checks a decoded value against the range of its field and, when
one field fails, gives the error for the whole message. What the three modules send in that
field:

| circuit | bytes | as `D2B` | within -50 to 127 |
|---|---|---|---|
| em1 (`50`) | `00 0b` | 11.0 | yes |
| em2 (`51`) | `00 9c` | -100.0 | no |
| em3 (`52`) | `00 9c` | -100.0 | no |

`00 9c` is not the replacement value of the type (`00 80`, which ebusd prints as `-` and
which em1 sends as flow temperature): it is an ordinary value of `D2B`, the -100.0 this family
answers for a temperature whose sensor is not fitted ([ka-reads.md](ka-reads.md): the same
modules answer `18 fc`, -100.0 in signed tenths, to a register read of the outside
temperature). No type of ebusd can turn it into "not available"; the definition can only stop
refusing it.

**The change.** In `src/wolf/wtc_inc.tsp` (lot A) the field has a type of its own,
`otemp2`: `D2B` in °C without range, the counterpart of `otemp10` that the register reads
already use for the same reason. The comment of the field says that -100.0 means a module
without outside sensor. Only this field changes: the other temperatures of the exchange keep
`temp2` (no value outside its range was seen on them), and so does the status broadcast of
the boilers. In the compiled CSV the field loses its range and gains the sentence in its
comment, in the three files `50.w.em1`, `51.w.em2`, `52.w.em3`; name, position and type
(`D2B`) are the same, so a value read before reads the same.

**Proof.** The three exchanges of the table above ("The three exchanges"), injected into the
ebusd of `scripts/check.sh` started without a bus and loaded with the lot files compiled from
the corrected lot A, then read back (`read -v -c <circuit> HcMode`):

| circuit | flow | outside | boost | max | min |
|---|---|---|---|---|---|
| em1 | `-` (not available) | 11.000 | 2.0 | 82.0 | 8.0 |
| em2 | 25.000 | -100.000 | 2.0 | 75.0 | 8.0 |
| em3 | 25.801 | -100.000 | 1.0 | 75.0 | 8.0 |

em1 reads what it read before the change; em2 and em3, refused before, decode to the values
the layout gives. The two readings are in [fixtures.toml](fixtures.toml) with their values
(case `no-sensor`) in place of the error, and step 7 of `scripts/check.sh` decodes them at
every run.

**What a reader of the value must know.** -100.0 is a number like any other in the telegram:
an interface has to treat it as "no sensor", as it does for the -40 of a boiler without
outside sensor. Not established: whether a module with a sensor can send a value below -50
(the reason no lower bound was put back), and whether the same -100.0 can appear in the
other temperatures of the exchange.

## Equipment

Kromschröder WCM-FS heating modules (room units) on eBUS, `MF=Kromschröder`, three modules.

## Date

2026-11-16; the three exchanges with their source, the finding and the correction on
2026-11-18.

## Not verified

- The `Ink*` and `Opmode_*` bit fields are named but not interpreted.
- `BoilerMCBoostTemp`, `SupplyHCMaxTemp`, `SupplyHCMinTemp` were seen at a single operating
  point only.
- Modelled passively (observed), not actively polled, to stay read-only towards the system.

## Addition of 2026-11-20 — field names in 0.6.0

The bits not interpreted keep their positions and types and take the scheme `Ukn<byte>_<bit>`
of `Boiler1Status`: `Ink1_n` → `Ukn1_n`, `Ink2_n` → `Ukn2_n` (the two flag bytes the room
controller sends), and `Opmode_4` … `Opmode_7` → `Ukn3_4` … `Ukn3_7`: they are bits 3 to 6 of
the answer's flag byte that holds `Pump`, `ValveClosing`, `ValveOpening`, not bits of the byte
`Opmode`, which their former name suggested. No meaning is claimed for any of them. Lot G,
`kromschroeder: unknown bits of HcMode named Ukn<byte>_<bit>`; the metadata gives each its former
name (`renamed_from` on the field).
