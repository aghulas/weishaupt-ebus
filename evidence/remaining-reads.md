# Remaining single-register reads (fixture coverage completion)

Read-only bus reads captured on 2026-11-22 on the test installation (two WTC boilers in
cascade, WCM-KA 3.0 system manager, two WCM-EM heating modules, two WCM-FS room units across
three heating circuits) to provide a bus-captured fixture for the remaining 51 readable
messages whose definitions were previously evidenced on a sibling device address.

All reads are `50 22` register reads from ebusd (`QQ = 0x31`); nothing was written.

## Circuit `fs1` (`ZZ = 0x35`)

| Message | Master | Slave | Decoded |
|---|---|---|---|
| `VersionMinor` | `a1 9a 01` | `1a 00` | `26` |

## Circuit `em2` (`ZZ = 0x51`)

| Message | Master | Slave | Decoded |
|---|---|---|---|
| `MixerPump` | `70 52 00` | `01 00` | `on` |
| `CirculationReturnSetTemp` | `cc a9 04` | `2c 01` | `30.0` |

## Circuit `em3` (`ZZ = 0x52`)

| Message | Master | Slave | Decoded |
|---|---|---|---|
| `MixerParameter` | `61 8f 01` | `50 00` | `8.0` |
| `VersionMajor` | `45 99 01` | `74 01` | `372` |
| `VersionMinor` | `a1 9a 01` | `03 00` | `3` |

## Circuit `fs2` (`ZZ = 0x75`)

| Message | Master | Slave | Decoded |
|---|---|---|---|
| `RoomSetpointTemp` | `08 12 00` | `50 00` | `8.0` |
| `OutsideMixedTemp` | `5a 1a 0a` | `5c 00` | `9.2` |
| `VersionMajor` | `45 99 01` | `47 01` | `327` |
| `VersionMinor` | `a1 9a 01` | `1a 00` | `26` |
| `DHWLoadingPriority` | `d8 23 00` | `02 00` | `Parallel` |
| `DHWSetbackTemp` | `12 8a 02` | `90 01` | `40.0` |
| `DHWMaxTemp` | `ad 81 01` | `58 02` | `60.0` |
| `DHWLegionellaDay` | `5d 01 01` | `05 00` | `Friday` |
| `LegionellaCirculationTime` | `29 b1 09` | `b4 00` | `180` |
| `LegionellaSetpoint` | `3d 87 05` | `58 02` | `60.0` |
| `SummerTimeStartDay` | `09 de fd` | `19 00` | `25` |
| `SummerTimeStartMonth` | `55 df fd` | `03 00` | `March` |
| `SummerTimeEndDay` | `49 e0 fd` | `19 00` | `25` |
| `SummerTimeEndMonth` | `15 e1 fd` | `0a 00` | `October` |
| `ErrorId` | `ab 9a 0b` | `00 00` | `0` |
| `ErrorCode` | `f7 9b 0b` | `00 00` | `0` |
| `ErrorType` | `3f 9c 0b` | `03 00` | `3` |
| `ErrorDevice` | `63 9d 0b` | `00 00` | `0` |
| `ErrorMinute` | `db 9f 0b` | `33 00` | `51` |
| `ErrorHour` | `c7 a0 0b` | `03 00` | `3` |
| `ErrorDay` | `9b a1 0b` | `01 00` | `1` |
| `ErrorMonth` | `7f a2 0b` | `09 00` | `September` |
| `ErrorYear` | `23 a3 0b` | `00 00` | `0` |

## Circuit `fs3` (`ZZ = 0xf5`)

| Message | Master | Slave | Decoded |
|---|---|---|---|
| `OutsideMixedTemp` | `5a 1a 0a` | `5c 00` | `9.2` |
| `VersionMajor` | `45 99 01` | `47 01` | `327` |
| `VersionMinor` | `a1 9a 01` | `1a 00` | `26` |
| `DHWLoadingPriority` | `d8 23 00` | `02 00` | `Parallel` |
| `DHWSetbackTemp` | `12 8a 02` | `90 01` | `40.0` |
| `DHWMaxTemp` | `ad 81 01` | `58 02` | `60.0` |
| `DHWLegionellaDay` | `5d 01 01` | `05 00` | `Friday` |
| `LegionellaCirculationTime` | `29 b1 09` | `b4 00` | `180` |
| `LegionellaSetpoint` | `3d 87 05` | `58 02` | `60.0` |
| `SummerTimeStartDay` | `09 de fd` | `19 00` | `25` |
| `SummerTimeStartMonth` | `55 df fd` | `03 00` | `March` |
| `SummerTimeEndDay` | `49 e0 fd` | `19 00` | `25` |
| `SummerTimeEndMonth` | `15 e1 fd` | `0a 00` | `October` |
| `ErrorId` | `ab 9a 0b` | `00 00` | `0` |
| `ErrorCode` | `f7 9b 0b` | `00 00` | `0` |
| `ErrorType` | `3f 9c 0b` | `03 00` | `3` |
| `ErrorDevice` | `63 9d 0b` | `00 00` | `0` |
| `ErrorMinute` | `db 9f 0b` | `33 00` | `51` |
| `ErrorHour` | `c7 a0 0b` | `03 00` | `3` |
| `ErrorDay` | `9b a1 0b` | `01 00` | `1` |
| `ErrorMonth` | `7f a2 0b` | `09 00` | `September` |
| `ErrorYear` | `23 a3 0b` | `00 00` | `0` |
