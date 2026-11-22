# Boiler installer parameters: proposal for a lot (waits for the displayed values)

> **Superseded on 2026-11-22.** The second pass of the vendor tool showed both boilers set alike,
> so the `50 22` registers below that share a value stay ambiguous. The parameters were defined
> instead from the EEPROM bytes the tool itself reads (`InstallerParameters1`–`5`,
> `evidence/bc-installer-parameters.md`), where each address is named by the tool. The register
> table is kept as a record of the survey.

The register survey read the boiler automats' registers `0x0000`–`0x03ff` (both boilers; the
parameter registers below read the same on both, except the boiler address); the vendor tool's "Heating specialist" tab displayed
P10–P71 of boiler A, and its developer window the EEPROM bytes behind them
([evidence/service-tool-ui-exploration.md](../evidence/service-tool-ui-exploration.md),
[evidence/register-survey-findings.md](../evidence/register-survey-findings.md)). A register
becomes a definition when its value equals one displayed parameter and no other: the second pass
of the vendor tool (both boilers, as displayed) is the second source and settles the ambiguous
ones. **No branch changes before the owner approves the names.**

Proposed lot: **K** (the boiler register reads, `50 22`, already the information values; above
lot F, so it can be replayed). Files `08.w.bc1`, `18.w.bc2`, shared models in `wtc_inc`. Read
only, stock ebusd.

## Matched, one candidate each (with the displayed values of boiler A)

| Register | Read (both boilers) | Parameter (manual 83251704, p. 48–51) | Displayed | Proposed name | Type |
|---|---|---|---|---|---|
| `27 00` | 800 | P31 maximum flow temperature | 80 °C | `SupplyMaxTemp` | temp10 |
| `11 02` | 1200 | P33 flue-gas safety temperature | 120 °C | `FlueGasSafetyTemp` | temp10 |
| `09 02` | 37 | P35 ignition rating | 37 % | `IgnitionLoad` | percent |
| `5a 01` | 230 | P36 minimum rating | 23 % | `LoadMin` | percent, tenths |
| `2d 00` | 100 | P50 hot-water excess | 10 K | `DHWBoostTemp` | diff10 |
| `7f 01` | 3 | P42 pump run-on, hot water | 3 min | `PumpRunOnDHW` | minutes |
| `e2 01` | 200 | P48 flow–return difference | 20 K | `FlowReturnDiffTemp` | diff10 |
| `78 01` | 1 / 2 | P12 boiler address (A, b) | A on boiler A | `BoilerAddress` (1 = A, 2 = b) | UIN |

## Matched to a value that several parameters share (the tool's display of both boilers decides)

| Register | Read | Candidates (displayed value) | Proposed name if confirmed |
|---|---|---|---|
| `02 00`, `03 00`, `1f 00` | 80 each (8.0) | P30 minimum flow temperature 8 °C; the others possibly live setpoints at their minimum | `SupplyMinTemp` (one of the three) |
| `22 00` | 40 (4.0) | P32 switching difference 4; P49 4 s; P43 4 | `SupplySwitchDiff` |
| `5d 01` | 4 | P43 pump control function 4; P49 4 s; P32 | `PumpControlMode` or `PumpControlInterval` |
| `e1 01` | 4 | P49 pump control interval 4 s (beside P48 at `e2 01`) | `PumpControlInterval` |
| `42 01` | 1 | P41 pump run-on, heating 1 min; P71 eBUS feed 1 | `PumpRunOnHeating` or `EbusFeed` |
| `55 01`, `fd 01` | 50 each | P44 pump rating minimum 50 %; P23 frost protection 5 °C (×10) | `PumpLoadMin`, `FrostProtectionTemp` |
| `56 01`, `57 01` | 100 each | P37, P38 maximum rating heating, hot water; P45, P46 pump rating 100 % | `LoadMaxHeating`, `LoadMaxDHW` |
| `3f 01`, `59 01` | 1000 each (100.0) | a rating of 100 % in tenths | as above |

Values both boilers share cannot be told apart by the second boiler; the second pass of the tool
can, by the values it displays on boiler B, and a parameter the owner has set differently on the
two boilers would tell one register at once.

## What the definitions will say

Each message: "P<nn> of the boiler automat, read only", the unit of the manual, the register and
both sources (the tool's display and the survey's read). Writes stay out (rule 7; the boiler is
not written from ebusd).

## Date

2026-11-19.
