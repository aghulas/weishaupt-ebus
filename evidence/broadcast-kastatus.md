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

## Phase list: sources (2026-11-27)

Vendor manuals read on the partner portal ([vendor-documentation.md](../docs/vendor-documentation.md),
sections 2 and 5); meanings in our words.

| value | name | WTC-GB (83251704, 1/2025-01, p. 44) | gateway (83272304, 1/2024-05, p. 45) | WTC 15-A … 32-A (83053005, 07/2005, p. 41) | WTC-OB (83314005, 1/2024-06, p. 45) |
|---|---|---|---|---|---|
| 0 | `BurnerOff` | burner off | burner off | burner off | – |
| 1 | `StandbyCheckFan` | fan standstill check | fan standstill check | fan standstill check | fan standstill |
| 2 | `PrepurgeSpeedAchieved` | reach pre-purge speed | reach pre-purge speed | pre-purge speed reached | oil preheating |
| 3 | `Prepurge` | pre-purge | pre-purge | pre-purge countdown | pre-purge / pre-ignition |
| 4 | `IgnitionSpeedAchieved` | reach ignition speed | reach ignition speed | ignition speed reached | safety time |
| 5 | `Ignition` | ignition | ignition | safety time | post-ignition |
| 6 | `BurnerInOperation` | burner in operation | burner in operation | burner in operation | flame stabilisation |
| 7 | `GasValveCheck` | gas valve check | gas valve check | gas valve V1 check | controller released |
| 8 | `PostPurge` | reach post-purge speed, post-purge | reach post-purge speed, post-purge | gas valve V2 check | post-purge |
| 9 | `ForcedVenting` | – | – | post-purge speed reached, post-purge | forced ventilation |

- **Phases 0 to 8** follow the WTC-GB, the boilers of this installation, and the gateway's list
  for its register 110 (the operating phase of each WTC it reads), which is the same list. The
  English edition of the WTC-GB manual cited before (83251702, p. 39) agrees.
- **Phase 9** is in two manuals with two meanings: forced ventilation on the oil boiler WTC-OB,
  the post-purge on the WTC 15-A … 32-A (whose 7 and 8 are the two gas-valve checks). A WTC-GB
  stops at 8. So the name `ForcedVenting` is right for a WTC-OB only; on a WTC-GB the value is
  not expected, and on a WTC-A it would mean post-purge. The list is not split per boiler
  series: the definitions are established on WTC-GB automats, and the other series' phases 2 to
  8 differ as well.
- **Fault codes in the same byte.** The gateway page gives, after the phases, that fault codes
  start at the value 11 and mean what the boiler's manual says (the W / F codes, 11 to 89,
  [vendor-documentation.md](../docs/vendor-documentation.md), section 4). Our reading: while
  the boiler shows a fault or warning (bit 15, "alarm", of the gateway's status register,
  which corresponds to `Error` in the second bit byte here), this byte carries its number in
  place of the phase. The phase page does not state that condition in so many words; the
  page on missing heat-demand telegrams does for one case: warning W80 sets the alarm bit and
  puts 80 in the phase register (83272304, p. 52). No fault was seen on the bus. The value 19 seen with the alarm bit clear on a WTC 25-A of another
  installation ([second-installation-ebus2mqtt.md](second-installation-ebus2mqtt.md)) is in
  no document read.

## Equipment

Kromschröder WCM/WTC condensing boiler on eBUS, scanning as `MF=Kromschröder`.

## Date

2026-11-16 and 2026-11-18 (bus); manual pages 2026-11-27.

## Not verified

- Only the phases 0 to 9 are enumerated. The fault and warning codes from 11 (`0x0b`) are not
  in the list, and no fault state was seen on the bus to confirm that the byte carries them
  (section "Phase list: sources").
- Phase 9 (`ForcedVenting`) was never seen on the bus. Its name has a source since 2026-11-27,
  for the oil boiler WTC-OB only (83314005, p. 45); the WTC-GB lists 0 to 8 and the WTC-A gives
  9 another meaning (same section). Noted without a source on 2026-11-18.
- The two bit bytes: only the named flags are interpreted; the `Ukn` bits are left unnamed.
- The non-broadcast variant of this telegram (boiler master → another master) was also seen on
  the bus but is not shipped here; only the unambiguous broadcast form is.
