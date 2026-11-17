# fs1, fs2, fs3 — heating-circuit reads of the room units (50 22)

## What

Lot G, branch `weishaupt-G` of the ebusd-configuration fork (on `weishaupt-C`), first commit.
Fourteen registers read with `PBSB = 50 22`, ID `<crc> <addr> <sub>`, the `<crc>` precomputed
(see [register-crc.md](register-crc.md)), on the three room units: `src/wolf/35.w.fs1.tsp`
(slave address `35`), new `src/wolf/75.w.fs2.tsp` (`75`) and `src/wolf/f5.w.fs3.tsp` (`f5`).
The models are shared in `src/wolf/wtc_inc.tsp`. The value is 16 bits, low byte first.

The last two rows were already in lot C for `fs1`, read and written; they are added for
`fs2` and `fs3` as reads only. No write is defined for `fs2` and `fs3`.

Request payload, then the two data bytes of each answer and the decoded value:

| message | addr sub | request | codec | fs1 (`35`) | fs2 (`75`) | fs3 (`f5`) |
|---|---|---|---|---|---|---|
| HeatDemandTemp | `02 00` | `b8 02 00` | UIN/10, °C | `a7 01` 42.3 | `c2 01` 45.0 | `ca 01` 45.8 |
| SupplyHCSetTemp | `04 00` | `2c 04 00` | SIN/10, °C | `a7 01` 42.3 | `ae 01` 43.0 | `b6 01` 43.8 |
| OutsideTemp | `0c 00` | `74 0c 00` | SIN/10, °C | `96 00` 15.0 | `96 00` 15.0 | `96 00` 15.0 |
| OutsideWeightedTemp | `0c 0a` | `7e 0c 0a` | SIN/10, °C | `86 00` 13.4 | `86 00` 13.4 | `86 00` 13.4 |
| RoomTemp | `11 00` | `ec 11 00` | SIN/10, °C | `1a 01` 28.2 | `1a 01` 28.2 | `1c 01` 28.4 |
| RoomNormalTemp | `05 00` | `70 05 00` | UIN/10, °C | `d2 00` 21.0 | `d2 00` 21.0 | `d2 00` 21.0 |
| RoomSetbackTemp | `08 00` | `58 08 00` | UIN/10, °C | `8c 00` 14.0 | `8c 00` 14.0 | `8c 00` 14.0 |
| RoomFrostProtectionTemp | `14 0a` | `96 14 0a` | UIN/10, °C | `50 00` 8.0 | `50 00` 8.0 | `50 00` 8.0 |
| GradientCurve | `0e 01` | `cd 0e 01` | UIN/10 | `be 00` 19.0 | `c8 00` 20.0 | `d2 00` 21.0 |
| SummerWinterChangeOverTemp | `16 01` | `25 16 01` | UIN/10, °C | `96 00` 15.0 | `96 00` 15.0 | `96 00` 15.0 |
| SupplyMaxTemp | `28 00` | `64 28 00` | UIN/10, °C | `ee 02` 75.0 | `ee 02` 75.0 | `ee 02` 75.0 |
| SupplyMinTemp | `2b 01` | `81 2b 01` | UIN/10, °C | `50 00` 8.0 | `50 00` 8.0 | `50 00` 8.0 |
| SwitchOnRuntime | `10 01` | `b1 10 01` | UIN, min | `03 00` 3 | `03 00` 3 | `03 00` 3 |
| FrostProtectionLimitTemp | `be 02` | `b2 be 02` | SIN/10, °C | `00 00` 0.0 | `00 00` 0.0 | `00 00` 0.0 |

## How it was established

1. **Read.** Each message was read once on each unit through the running ebusd (master `31`),
   reads spaced, on 2026-11-17 between 16:55 and 16:57. All 42 reads were answered.
2. **Bytes.** Request and answer were taken from the passive capture of the same ebusd
   (`grab result all`, snapshot of 16:57): `31 → 35 / 75 / f5`, `50 22`, three request bytes,
   answer `02 <low> <high>`. They are the bytes of the table.
3. **Checksum.** The first request byte was recomputed offline for the 42 telegrams with the
   routine of [register-crc.md](register-crc.md) (CRC-8, polynomial 0x5C, initial value = first
   address byte, over the address bytes): no mismatch. The IDs in the compiled CSV equal the
   request bytes of the table.
4. **Codec and meaning**, register by register:
   - `HeatDemandTemp`: equals the setpoint the unit broadcasts to the cascade in its standard
     `05 07` telegram of the same minute (bytes 3 and 4, sixteenths): `30 → f1` `a5 02` =
     42.31, `70 → f1` `d0 02` = 45.0, `f0 → f1` `dd 02` = 45.81. Same register as
     `HeatDemandTemp` of the system manager ([ka-reads.md](ka-reads.md)).
   - `SupplyHCSetTemp`: the setpoint the room controller sends to its heating module in `50 14`
     ([em-hcmode.md](em-hcmode.md)) was `00 2a` = 42, `00 2b` = 43 and `00 2b` = 43 in the same
     snapshot, whole degrees. The heating modules `51` and `52` answer the same register with
     43.0 ([heating-modules-reads.md](heating-modules-reads.md)); the devices without a mixed
     circuit (`15`, `50`) answer `00 80`, hence the signed type.
   - `OutsideTemp`, `OutsideWeightedTemp`: the system manager answered the same registers with
     `96 00` and `86 00` in the same minutes; both are in lot A as signed tenths.
   - `RoomTemp`: the room temperature in the `50 14` telegram of each unit was `4d 1c` = 28.3,
     `00 1c` = 28.0 and `cd 1c` = 28.8 in the same snapshot, within 0.4 K of the read. The
     devices without a room sensor (`15`, `50`, `51`, `52`) answer `00 80`, hence the signed
     type.
   - `RoomNormalTemp`, `RoomSetbackTemp`, `RoomFrostProtectionTemp`, `GradientCurve`,
     `SummerWinterChangeOverTemp`, `SupplyMaxTemp`, `SupplyMinTemp`: the registers lot C
     reads and writes on the heating module `51`, same codecs
     ([settings-writes.md](settings-writes.md)); the values lie in the ranges given there.
     `SupplyMaxTemp` and `SupplyMinTemp` equal what the second and third unit write to their
     heating module with `09 03` (`70 → 51` and `f0 → 52`: `28 00 ee 02`, `2b 01 50 00`). The
     heating curve is the one value that differs between the three units (19.0, 20.0, 21.0).
   - `SwitchOnRuntime`, `FrostProtectionLimitTemp`: the registers lot C reads and writes on
     the first room unit, same codecs; the second and third unit answer the same values as the
     first one.

Toolchain: `scripts/check.sh` clean on the commit, 238 messages (198 before: 12 for `fs1`, 14
each for `fs2` and `fs3`).

## Equipment

Three Kromschröder WCM-FS room units on eBUS at slave addresses `35`, `75` and `f5` (masters
`30`, `70`, `f0`), all scanning as `MF=Kromschröder`, `ID=W`, SW=2726. Each drives one
heating circuit through a heating module (`50`, `51`, `52`). Two condensing boilers in
cascade behind a system manager (`15`, SW=6618).

## Date

2026-11-17.

## Not verified

- Every value was read once, in one afternoon. No setting was changed to see the register
  follow, and no write was tried (rule 7); the meaning of the setting registers rests on the
  heating module and on the first room unit, where lot C has the writes.
- `FrostProtectionLimitTemp` answers `00 00` on all three units. It is the value proven on
  the first unit by the operator's write test (0.0, -0.5, 0.0), but this device type also
  answers `00 00` on a register it does not have (`0e 00`, hot water sensor): on the second
  and third unit a zero alone would not tell the two apart.
- The room unit and its heating module answer the same setting registers with different
  values (room unit 21.0 / 14.0 / 8.0 / 15.0 and a curve of 19 to 21, module 21.5 / 21.5 /
  10.0 / 20.0 and a curve of 10.0); only the two flow limits agree. Which copy the regulation
  uses was not established. The room unit writes the flow limits to the module, which suggests
  the room unit leads.
- The sign of `RoomTemp` and `SupplyHCSetTemp`: no negative reading, the signed type follows
  from the `00 80` answers of the other devices.
- `RoomTemp` near 28 °C on all three units: confirmed by the `50 14` telegrams, not compared
  with a thermometer.

Left out, read on the three units the same day:

| register | answer | why it is not in the lot |
|---|---|---|
| `RoomSetPointTemp` `12 00` (`08 12 00`) | `d2 00` = 21.0 on the three units | equals the normal setpoint during an occupied period; to call it the current setpoint it must be seen at 14.0 during a setback period |
| `BoilerMCBoostTemp` `11 01` (`ed 11 01`) | `14 00` = 2.0 K on the three units | the heating module of the third circuit answers 1.0 K and sends 1.0 K in `50 14`; the value of the room unit is not the one in use there |
| `ErrorStatus` `01 00` (`5c 01 00`) | `00 00` | zero on every device; cannot be told from an unused register |
| `OutsideBlendedTemp` `1a 0a` (`5a 1a 0a`) | `92 00` = 14.6 | lies between the outside temperature and the weighted one; name from the running configuration only |
| `RoomSensorCorrectionTemp` `09 01` (`05 09 01`) | `00 00` | zero, register proven nowhere |
| `ConfigStatus` `10 00` (`b0 10 00`) | `02 00` | meaning of the value not known |
| `HolidayTempLevel` `3d 01` (`a5 3d 01`), holiday dates `1b 01`–`20 01` | `00 00`; 30 October to 1 November, year 0 | value list without a kept telegram (`docs/discoveries.md`); year 0 not understood |
| operating mode, circuit type, control variation, construction type and other choices | small integers | value lists come from the running configuration only |
| weekly programs (sub-byte `14`, `15`, `16` heating, `17` hot water, `1a` circulation, 21 slots each) | answered with two bytes per slot | a lot of its own (rule 5); slot format not compared with lot A for this record |
| most other candidates of the running configuration | `00 80` or `18 fc` | not available on this device type |
