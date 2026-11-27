# broadcast — WTC boiler status (KaStatus, 50 0A)

## What

The boiler (WTC) broadcasts its status with `PBSB = 50 0A`, 13 data bytes. Modelled as a
passive broadcast read `KaStatus` in `src/wolf/broadcast.tsp` (fields in `src/wolf/wtc_inc.tsp`),
`ZZ = fe` (broadcast). Incoming only — ebusd decodes it, never sends it.

Field layout (13 bytes): `Status1:UCH`, `OperatingPhase:UCH` (enum), two bit bytes
(flame, gas valves, pump, error; manual start, burner, service, fan, circ pump, DHW pump),
`Load:UCH %`, `SupplyTemp:D1C °C`, `FlueGasTemp:UCH °C`, `DHWTemp:D1C °C`,
`OutsideTemp:D2B °C`, `OutsideWeightedTemp:D2B °C`, `SupplySetTemp:UCH °C`.

## How it was established

Live bus, passive capture (ebusd `grab result all`). Broadcast frame seen (master → `fe`,
PBSB `50 0A`), data trimmed to the point:

```
01 00 48 80 ff 76 ff 59 00 0b 4d 0b 42
```

Decoded with the layout above:

| field | bytes | value |
|---|---|---|
| OperatingPhase | `00` | BurnerOff (idle) |
| DHWTemp (D1C) | `59` | 44.5 °C |
| OutsideTemp (D2B) | `00 0b` | 11.0 °C |
| OutsideWeightedTemp (D2B) | `4d 0b` | 11.3 °C |

The outside readings (11.0 and 11.3 °C) match the register reads `OutsideTemp` (11.0) and
`OutsideWeightedTemp` (11.3) captured the same session in `ka-reads.md`, which confirms the
byte offsets and the D2B scaling. `OperatingPhase = BurnerOff` is consistent with the boiler
being idle at the time.

Toolchain: `tsp compile` clean, `tsp format --check` clean, `ebusd --checkconfig` clean
(0 errors). Emitted as a type `u` (passive update) message, `ZZ=fe`, ID `500a`.

## Source address, and a second capture (2026-11-18)

The capture of 2026-11-16 did not keep the source address of the broadcast. Passive capture of
2026-11-18, 10:25 (ebusd `grab result all`, nothing sent): the status broadcast comes from
`f1`, not from a boiler (`03` and `13` send theirs to `10`, see
[bc1-boiler-status.md](bc1-boiler-status.md)). On this installation `f1` is a master address
of the system manager: its slave side `f6` identifies with the manager's software. A second
installation, one boiler without a system manager, is reported to broadcast the same telegram
from `f1` ([second-installation-ebus2mqtt.md](second-installation-ebus2mqtt.md), third-party
data): who holds `f1` is an observation per installation, not a rule.

```
f1 fe 500a : 01 00 40 00 ff 50 ff 33 00 0b cd 0c 24
```

| field | bytes | value |
|---|---|---|
| OperatingPhase | `00` | BurnerOff |
| Load | `ff` | not available |
| SupplyTemp (D1C) | `50` | 40.0 °C |
| DHWTemp (D1C) | `33` | 25.5 °C |
| OutsideTemp (D2B) | `00 0b` | 11.0 °C |
| OutsideWeightedTemp (D2B) | `cd 0c` | 12.8 °C |
| SupplySetTemp | `24` | 36 °C |

## Equipment

Kromschröder WCM/WTC condensing boiler on eBUS, scanning as `MF=Kromschröder`.

## Date

2026-11-16.

## Not verified

- Only `_operatingPhase` values 0x00–0x09 (the normal operating phases) are enumerated; the
  fault/warning codes (0x0B+) the manual lists are not yet in the enum, and no fault state was
  observed on the live bus to confirm them.
- `ForcedVenting` (0x09) has no source (noted 2026-11-18): the manual of the boiler lists the
  phases 0 to 8 only (83251704, pages 46 and 89; English edition 83251702, page 39), the value
  9 was never seen on the bus, and where the name comes from is not recorded. The entry is
  kept in the list as it is, not established; the phases seen on the bus are 0 and 6.
- The two bit bytes: only the named flags are interpreted; the `Ukn` bits are left unnamed.
- The non-broadcast variant of this telegram (boiler master → another master) was also seen on
  the bus but is not shipped here; only the unambiguous broadcast form is.
