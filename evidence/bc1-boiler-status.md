# Boiler status and load sent to the cascade master (Boiler1Status, Boiler1Power, Boiler2Status, Boiler2Power)

## What

Each boiler of the cascade sends, to the controller (`ZZ = 10`), two passive telegrams: the
first boiler from source `QQ = 03` (messages `Boiler1Status`, `Boiler1Power`), the second from
`QQ = 13` (`Boiler2Status`, `Boiler2Power`). They are defined in `src/wolf/15.w.ka.tsp`, the
file of the system manager, whose master address is `10`, on the shared models `Status` and
`Power`:

- **Status** (`PBSB = 50 0A`): same 13-byte layout as the broadcast `KaStatus`
  (operating phase, burner flags, load, boiler/flue/DHW/outside temperatures), reusing the
  shared `Status` model.
- **Power** (`PBSB = 05 04`): `CurrentLoad`, `MinLoad`, `MaxLoad`, each `UCH %`.

## How it was established

Live bus, passive capture (ebusd `grab result all`). Telegrams seen from `QQ=03` to `ZZ=10`,
data trimmed to the point:

```
Power  05 04 : 36 17 64
Status 50 0A : 01 06 7f 62 33 7c ff ff 00 0b 4d 0b ff
```

Decoded:

| message | field | bytes | value |
|---|---|---|---|
| Power | CurrentLoad / MinLoad / MaxLoad | `36` `17` `64` | 54 % / 23 % / 100 % |
| Status | OperatingPhase | `06` | BurnerInOperation |
| Status | OutsideTemp (D2B) | `00 0b` | 11.0 °C |
| Status | OutsideWeightedTemp (D2B) | `4d 0b` | 11.3 °C |

`OperatingPhase = BurnerInOperation` is consistent with a non-zero load (54 %). The outside
readings match the register reads and the broadcast `KaStatus` captured the same session,
which confirms the Status byte offsets.

### Second boiler (bc2)

Same capture method on 2026-11-17, telegrams seen from `QQ=13` to `ZZ=10`:

```
Power  05 04 : 21 17 64
Status 50 0A : 01 00 07 00 00 80 ff ff 00 80 00 00 08
```

| message | field | bytes | value |
|---|---|---|---|
| Power | CurrentLoad / MinLoad / MaxLoad | `21` `17` `64` | 33 % / 23 % / 100 % |
| Status | OperatingPhase | `00` | BurnerOff |
| Status | Load | `00` | 0 % |
| Status | SupplyTemp (D1C) | `80` | 64.0 °C |
| Status | OutsideTemp (D2B) | `00 80` | not available |

Same lengths and the same PBSB pair as the first boiler, so the shared `Status` and `Power`
models apply. The second boiler has no outside sensor of its own: the field carries the
not-available value.

Seen while firing on 2026-11-17, a few minutes after a start (same passive capture):

```
Power  05 04 : 19 17 64
Status 50 0A : 01 06 7f 62 19 78 ff ff 00 80 00 00 ff
```

| message | field | bytes | value |
|---|---|---|---|
| Power | CurrentLoad / MinLoad / MaxLoad | `19` `17` `64` | 25 % / 23 % / 100 % |
| Status | OperatingPhase | `06` | the phase the first boiler shows while firing |
| Status | Load | `19` | 25 % |
| Status | SupplyTemp (D1C) | `78` | 60.0 °C |
| Status | OutsideTemp (D2B) | `00 80` | not available |

Bytes 1 to 4 (`06 7f 62 19`) equal those of the first boiler firing at the same load
(`01 06 7f 62 19 72 …`). Load and flow agree with the memory reads taken in the same minute
(25 %, 60 °C, see [bc-live-values.md](bc-live-values.md)). With the burner on, `CurrentLoad`
of `Power` equals `Load` of `Status`.

Toolchain: `tsp compile`, `tsp format --check`, `ebusd --checkconfig` all clean (0 errors).
Until 2026-11-17 these messages were `WTCStatus` and `WTCPower` in the files `10..bc1` and
`10..bc2`, `ZZ = 10` coming from the file name. With `--scanconfig` ebusd loads one file per
scanned slave address (`ScanHelper::loadScanConfigFile`), and `10` is a master address: the two
files were never loaded. The messages now carry `@qq` and `@zz(0x10)` themselves, in the file
ebusd loads for the slave address `15` of that master. Checked in the ebusd of the check without
a bus: with that file alone, the telegrams above of both boilers are decoded as
`ka Boiler1Status`, `ka Boiler2Power` and so on.

## Equipment

Kromschröder WCM/WTC condensing boilers (both boilers of a two-boiler cascade), eBUS,
`MF=Kromschröder`.

## Date

2026-11-16 (first boiler), 2026-11-17 (second boiler, burner off then firing).

## Not verified

- With the burner off, `Power` of the second boiler still reports a current load (33 %)
  while `Status` reports 0 %; what `CurrentLoad` means with the burner off is not
  established. With the burner on the two agree (25 %).
- `ZZ = 10` is a master address; the directed form is modelled in addition to the broadcast
  `KaStatus`, which carries the same status unambiguously.
- `MinLoad` / `MaxLoad` were seen only at 23 % / 100 % (one operating point); not swept.
