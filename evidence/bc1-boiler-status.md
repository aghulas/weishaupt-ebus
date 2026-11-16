# bc1 — directed boiler status and load (WTCStatus, WTCPower)

## What

The first boiler (source `QQ = 03`) sends, to the controller (`ZZ = 10`), two passive
telegrams decoded in `src/wolf/10..bc1.tsp`:

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

Toolchain: `tsp compile`, `tsp format --check`, `ebusd --checkconfig` all clean (0 errors).
`ZZ = 10` is taken from the file name `10..bc1`, as for the other circuits.

## Equipment

Kromschröder WCM/WTC condensing boiler (first boiler of a two-boiler cascade), eBUS,
`MF=Kromschröder`.

## Date

2026-11-16.

## Not verified

- The second boiler (`QQ = 13 → ZZ = 10`) sends the same telegrams and is not shipped here yet.
- `ZZ = 10` is a master address; the directed form is modelled in addition to the broadcast
  `KaStatus`, which carries the same status unambiguously.
- `MinLoad` / `MaxLoad` were seen only at 23 % / 100 % (one operating point); not swept.
