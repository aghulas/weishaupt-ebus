# em1, em2, em3 — heating-circuit reads of the heating modules (50 22)

## What

Lot G, branch `weishaupt-G` of the ebusd-configuration fork (on `weishaupt-C`), second commit.
Registers read with `PBSB = 50 22`, ID `<crc> <addr> <sub>`, the `<crc>` precomputed (see
[register-crc.md](register-crc.md)), in `src/wolf/50.w.em1.tsp` (slave address `50`),
`src/wolf/51.w.em2.tsp` (`51`) and `src/wolf/52.w.em3.tsp` (`52`); shared models in
`src/wolf/wtc_inc.tsp`. The value is 16 bits, low byte first.

Request payload, then the two data bytes of each answer and the decoded value. "lot C": the
message exists on that module since lot C, read and written, and is not touched. "—": not
defined on that module.

| message | addr sub | request | codec | em1 (`50`) | em2 (`51`) | em3 (`52`) |
|---|---|---|---|---|---|---|
| SupplyHCSetTemp | `04 00` | `2c 04 00` | SIN/10, °C | — (`00 80`) | `ae 01` 43.0 | `ae 01` 43.0 |
| SupplyHCTemp | `0f 00` | `90 0f 00` | SIN/10, °C | — (`00 80`) | `ac 01` 42.8 | `aa 01` 42.6 |
| BoilerMCBoostTemp | `11 01` | `ed 11 01` | SIN/10, K | `14 00` 2.0 | `14 00` 2.0 | `0a 00` 1.0 |
| RoomNormalTemp | `05 00` | `70 05 00` | UIN/10, °C | `d7 00` 21.5 | lot C (`d7 00` 21.5) | `d7 00` 21.5 |
| RoomSetbackTemp | `08 00` | `58 08 00` | UIN/10, °C | `a0 00` 16.0 | lot C (`d7 00` 21.5) | `d7 00` 21.5 |
| RoomFrostProtectionTemp | `14 0a` | `96 14 0a` | UIN/10, °C | `64 00` 10.0 | lot C (`64 00` 10.0) | `64 00` 10.0 |
| GradientCurve | `0e 01` | `cd 0e 01` | UIN/10 | `64 00` 10.0 | lot C (`64 00` 10.0) | `64 00` 10.0 |
| SummerWinterChangeOverTemp | `16 01` | `25 16 01` | UIN/10, °C | `c8 00` 20.0 | lot C (`c8 00` 20.0) | `c8 00` 20.0 |
| SupplyMaxTemp | `28 00` | `64 28 00` | UIN/10, °C | `34 03` 82.0 | lot C (`ee 02` 75.0) | `ee 02` 75.0 |
| SupplyMinTemp | `2b 01` | `81 2b 01` | UIN/10, °C | `50 00` 8.0 | lot C (`50 00` 8.0) | `50 00` 8.0 |

New messages: 8 on `em1`, 3 on `em2`, 10 on `em3`. All are reads; no write is defined for
`em1` and `em3`.

## How it was established

1. **Read.** Each message was read once on each module through the running ebusd (master
   `31`), reads spaced, on 2026-11-17 between 16:56 and 16:57. All were answered; the two
   answers `00 80` of `50` are the not-available value, and those two messages are not
   defined for `em1`.
2. **Bytes.** Request and answer were taken from the passive capture of the same ebusd
   (`grab result all`, snapshot of 16:57): `31 → 50 / 51 / 52`, `50 22`, three request bytes,
   answer `02 <low> <high>`.
3. **Checksum.** The first request byte was recomputed offline for every telegram of the table
   (CRC-8, polynomial 0x5C, initial value = first address byte, over the address bytes): no
   mismatch. The IDs in the compiled CSV equal the request bytes.
4. **Independent figure.** Each module answers its room controller in `50 14`
   ([em-hcmode.md](em-hcmode.md)); the answers in the same snapshot, after the length byte:

   | module | answer | flow temperature | outside | boost | flow max | flow min |
   |---|---|---|---|---|---|---|
   | `50` | `00 00 00 80 00 0f 04 a4 10` | not available | 15.0 | 2.0 K | 82.0 | 8.0 |
   | `51` | `00 01 80 2a 00 9c 04 96 10` | 42.5 | -100.0 | 2.0 K | 75.0 | 8.0 |
   | `52` | `00 01 33 2a 00 9c 02 96 10` | 42.2 | -100.0 | 1.0 K | 75.0 | 8.0 |

   - `SupplyHCTemp`: 42.8 and 42.6 read, 42.5 and 42.2 in the telegram within a minute; `50`
     has no value in either place.
   - `BoilerMCBoostTemp`: 2.0, 2.0 and 1.0 K in both places, which also gives the codec
     (tenths; `04`, `04`, `02` are halves in the telegram).
   - `SupplyMaxTemp`, `SupplyMinTemp`: equal in both places on the three modules. The room
     units of the second and third circuit write the same two values to `51` and `52` with
     `09 03` (`28 00 ee 02`, `2b 01 50 00`).
   - `SupplyHCSetTemp`: the room controllers of the second and third circuit send 43 as the
     requested flow setpoint in the master part of the same telegram (`00 2b`); both modules
     read 43.0.
5. **Settings.** The seven setting registers are those of lot C on `51`, same codecs
   ([settings-writes.md](settings-writes.md)). `52` (same device type and software version
   as `51`) answers them with the very values `51` has. `50` answers them with the values the
   system manager `15` gave for the same registers in the same minutes (21.5, 16.0, 10.0,
   10.0, 20.0, 82.0, 8.0); three of them are in lot A for `15` (`RoomNormalTemp`,
   `RoomSetbackTemp`, `SupplyMaxTemp`).

Toolchain: `scripts/check.sh` clean on the commit, 259 messages (238 before).

## Equipment

Kromschröder WCM regulators on eBUS, scanning as `MF=Kromschröder`, `ID=W`: heating modules
at `51` and `52` (SW=7203), each with a mixed heating circuit and a WCM-FS room unit
(SW=2726); a device at `50` with the software version of the system manager (SW=6618) and no
mixed circuit. System manager at `15` (SW=6618), two condensing boilers in cascade.

## Date

2026-11-17.

## Not verified

- Every value was read once, in one afternoon. No setting was changed and no write was tried
  (rule 7): that `50` and `52` take a write on these registers is not known and not defined.
- `50` and `15` have the same software version and gave the same answer on every register
  read on both (the seven settings, heat demand, outside temperature, boost offset,
  configuration status 76; the weighted outside temperature 13.3 and 13.4 a minute apart). They are probably one device answering at two addresses; the
  scan does not say so. If they are, the `em1` settings are a second view of the system
  manager's registers.
- The setting registers of a module and of its room unit hold different values (see
  [room-units-reads.md](room-units-reads.md)); which copy the regulation uses was not
  established.
- Sign of `SupplyHCSetTemp` and `SupplyHCTemp`: from the `00 80` answer of `50`; no negative
  reading. Sign of `BoilerMCBoostTemp`: positive values only.

Left out, read on the three modules the same day:

| register | answer | why it is not in the lot |
|---|---|---|
| `HeatDemandTemp` `02 00` (`b8 02 00`) | `50`: 51.8 (as `15`), `51`: 47.0, `52`: 76.0 | `51` gives the demand of its room unit plus the boost (45.0 + 2.0), `52` gives flow maximum plus boost (75.0 + 1.0) while its room unit asks 45.8: two modules of the same type, two behaviours, not understood |
| `RoomSetPointTemp` `12 00` (`08 12 00`) | `50`: `00 80`, `51`: 10.0, `52`: 21.5 | `51` gives its frost setpoint and `52` its normal setpoint at the same moment, while both room units give 21.0 |
| `SwitchOnRuntime` `10 01`, `FrostProtectionLimitTemp` `be 02` | 8 min and 1.0 °C on the three modules | proven on the room unit, where the values are 3 and 0.0; whether the module's copy is used is not known |
| `MixerParameterTemp` `2b 00`, `NormalSplSetTemp` `29 01`, `ReducedSplSetTemp` `2a 01` | 8.0 K, 75.0, 45.0 on `51` and `52`, `00 80` on `50` | names from the running configuration only |
| `OutsideTemp` `0c 00` | `18 fc` (-100.0) on `51` and `52` | no sensor; on `50` it is the value of the system manager, already in lot A |
| `ErrorStatus` `01 00`, `ConfigStatus` `10 00` | 0; 76 on `50`, 1024 on `51` and `52` | zero cannot be told from an unused register; meaning of the configuration value not known |
| weekly programs, holiday settings, choices with value lists | not read for this record | later lot |
