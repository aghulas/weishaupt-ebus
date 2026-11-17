# bc1, bc2 — directed boiler status and load (WTCStatus, WTCPower)

## What

Each boiler of the cascade sends, to the controller (`ZZ = 10`), two passive telegrams: the
first boiler from source `QQ = 03` (`src/wolf/10..bc1.tsp`), the second from `QQ = 13`
(`src/wolf/10..bc2.tsp`):

- **WTCStatus** (`PBSB = 50 0A`): same 13-byte layout as the broadcast `KaStatus`
  (operating phase, burner flags, load, boiler/flue/DHW/outside temperatures), reusing the
  shared `Status` model.
- **WTCPower** (`PBSB = 05 04`): `CurrentLoad`, `MinLoad`, `MaxLoad`, each `UCH %`.

## How it was established

Live bus, passive capture (ebusd `grab result all`). Telegrams seen from `QQ=03` to `ZZ=10`,
data trimmed to the point:

```
WTCPower  05 04 : 36 17 64
WTCStatus 50 0A : 01 06 7f 62 33 7c ff ff 00 0b 4d 0b ff
```

Decoded:

| message | field | bytes | value |
|---|---|---|---|
| WTCPower | CurrentLoad / MinLoad / MaxLoad | `36` `17` `64` | 54 % / 23 % / 100 % |
| WTCStatus | OperatingPhase | `06` | BurnerInOperation |
| WTCStatus | OutsideTemp (D2B) | `00 0b` | 11.0 °C |
| WTCStatus | OutsideWeightedTemp (D2B) | `4d 0b` | 11.3 °C |

`OperatingPhase = BurnerInOperation` is consistent with a non-zero load (54 %). The outside
readings match the register reads and the broadcast `KaStatus` captured the same session,
which confirms the WTCStatus byte offsets.

### Second boiler (bc2)

Same capture method on 2026-11-17, telegrams seen from `QQ=13` to `ZZ=10`:

```
WTCPower  05 04 : 21 17 64
WTCStatus 50 0A : 01 00 07 00 00 80 ff ff 00 80 00 00 08
```

| message | field | bytes | value |
|---|---|---|---|
| WTCPower | CurrentLoad / MinLoad / MaxLoad | `21` `17` `64` | 33 % / 23 % / 100 % |
| WTCStatus | OperatingPhase | `00` | BurnerOff |
| WTCStatus | Load | `00` | 0 % |
| WTCStatus | SupplyTemp (D1C) | `80` | 64.0 °C |
| WTCStatus | OutsideTemp (D2B) | `00 80` | not available |

Same lengths and the same PBSB pair as the first boiler, so the shared `Status` and `Power`
models apply. The second boiler has no outside sensor of its own: the field carries the
not-available value.

Seen while firing on 2026-11-17, a few minutes after a start (same passive capture):

```
WTCPower  05 04 : 19 17 64
WTCStatus 50 0A : 01 06 7f 62 19 78 ff ff 00 80 00 00 ff
```

| message | field | bytes | value |
|---|---|---|---|
| WTCPower | CurrentLoad / MinLoad / MaxLoad | `19` `17` `64` | 25 % / 23 % / 100 % |
| WTCStatus | OperatingPhase | `06` | the phase the first boiler shows while firing |
| WTCStatus | Load | `19` | 25 % |
| WTCStatus | SupplyTemp (D1C) | `78` | 60.0 °C |
| WTCStatus | OutsideTemp (D2B) | `00 80` | not available |

Bytes 1 to 4 (`06 7f 62 19`) equal those of the first boiler firing at the same load
(`01 06 7f 62 19 72 …`). Load and flow agree with the memory reads taken in the same minute
(25 %, 60 °C, see [bc-live-values.md](bc-live-values.md)). With the burner on, `CurrentLoad`
of `WTCPower` equals `Load` of `WTCStatus`.

Toolchain: `tsp compile`, `tsp format --check`, `ebusd --checkconfig` all clean (0 errors).
`ZZ = 10` is taken from the file names `10..bc1` and `10..bc2`, as for the other circuits.

## Equipment

Kromschröder WCM/WTC condensing boilers (both boilers of a two-boiler cascade), eBUS,
`MF=Kromschröder`.

## Date

2026-11-16 (first boiler), 2026-11-17 (second boiler, burner off then firing).

## Not verified

- With the burner off, `WTCPower` of the second boiler still reports a current load (33 %)
  while `WTCStatus` reports 0 %; what `CurrentLoad` means with the burner off is not
  established. With the burner on the two agree (25 %).
- `ZZ = 10` is a master address; the directed form is modelled in addition to the broadcast
  `KaStatus`, which carries the same status unambiguously.
- `MinLoad` / `MaxLoad` were seen only at 23 % / 100 % (one operating point); not swept.
