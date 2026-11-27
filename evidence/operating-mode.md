# Operating mode of the room units and modules (`12 01`, read)

## What

`OperatingMode`, read only, on the three room units (`fs1`–`fs3`, slaves `35`, `75`, `f5`) and
the two heating modules (`em2`, `em3`, slaves `51`, `52`): `PBSB 50 22`, ID `09 12 01`
(precomputed checksum `09`, register `12 01`, number 274 in the vendor service tool), codec
`UIN` with the value list `operatingMode` in `src/wolf/wtc_inc.tsp`:

| value | name | meaning (heating circuit) |
|---|---|---|
| 1 | `Standby` | standby |
| 3 | `HeatingOperation` | heating, normal level |
| 4 | `SetbackOperation` | heating, reduced level |
| 5 | `HolidaySummer` | holiday / summer |
| 11 | `HeatingProgram1` | heating program 1 |
| 12 | `HeatingProgram2` | heating program 2 |
| 13 | `HeatingProgram3` | heating program 3 |

The register is the one `docs/discoveries.md` (2026-11-17) and the earlier records call the
program selector. It is not defined on the system manager (`15`, `ka`) nor on its direct
circuit (`50`, `em1`): at `50` the answer changes from read to read
([modules-programs.md](modules-programs.md), "Program selector `12 01`").

## How it was established

Three sources, each establishing one part.

1. **Address and codec: bus reads.** The register answers on the five devices with a 16-bit
   value; reads of 2026-11-17 ([modules-programs.md](modules-programs.md), table "Program
   selector `12 01`", and the table of the 18:00 snapshot), transcribed into
   `evidence/fixtures.toml`:

   | device | request | answer | value | date |
   |---|---|---|---|---|
   | `35` (`fs1`) | `09 12 01` | `0b 00` | 11 | 2026-11-17 |
   | `75` (`fs2`) | `09 12 01` | `0b 00` | 11 | 2026-11-17 |
   | `f5` (`fs3`) | `09 12 01` | `0b 00` | 11 | 2026-11-17 |
   | `51` (`em2`) | `09 12 01` | `0c 00` | 12 | 2026-11-17 |
   | `52` (`em3`) | `09 12 01` | `0c 00` | 12 | 2026-11-17 |

   The register survey of 2026-11-19 read 11 again on the three room units
   ([register-survey-findings.md](register-survey-findings.md), "Room unit 2 (`75`)"), and the
   vendor service tool's catalogue names register 274 "operating mode switch" / "type of
   operation" and showed "(0) Prog 1/DHW" on the room unit with 11 on the bus
   ([service-tool-ui-exploration.md](service-tool-ui-exploration.md); text mapping not
   established there).

2. **Value 11 = heating program 1: bus observation.** At the 18:00 switch time of 2026-11-17
   the third room unit went to setback and the first two did not; with the stored programs,
   only program 1 fits all three units reading 11 ([modules-programs.md](modules-programs.md)).

3. **The value list: vendor manual.** Installation manual of the vendor's eBUS / Modbus
   gateway 2.0, 83272304, edition 1/2024-05, p. 46: the operating mode of a room unit or a
   heating module (gateway register 650, read and write, range 1 … 13) takes 1 standby,
   3 heating, 4 reduced, 5 holiday / summer, 11 / 12 / 13 heating programs 1 / 2 / 3. For a
   hot-water module the page gives other meanings to the same numbers (standby, normal,
   reduced, reduced, and hot-water program for 11 to 13); the modules here drive heating
   circuits. The same page says that a module supplies these values when no room unit is
   fitted. Re-read on the portal on 2026-11-27.

**The tie between 2 and 3 rests on the value 11.** The gateway manual gives no eBUS register
for its mode register. That `12 01` is that register is inferred: the meaning of the menu
(type of operation), the 16-bit value in the same range, and value 11 meaning heating program
1 in both. A second installation adds one value: the room unit of the third-party bridge
([second-installation-ebus2mqtt.md](second-installation-ebus2mqtt.md), register 274) read 13
while its gateway showed "Programm-3", which fits the list; it is third-party data and is not
the evidence of this definition. **One read on site confirms the tie**: a unit set to standby
or reduced by its operator should read 1 or 4 (item 12 of
[owner-checklist-room-units.md](../docs/owner-checklist-room-units.md)).

**Vendor code, candidate only.** The room unit's user level has P111 "Mode Fct Chauf" in menu
"Réglage#1" (83277504, edition 3/2012-10, p. 32); the screen of the second circuit's heating
function also shows 111 (p. 98). Because the tie of `12 01` to that setting is inferred, the
code is not published: the metadata lists the five messages in `open.vendor_codes` with reason
`display` and the candidate in the note, to be checked with item 12 of the checklist.

**Modules.** `51` and `52` read 12 (heating program 2) while their own heating programs are
shown not to be applied with a room unit fitted ([modules-programs.md](modules-programs.md)).
Read as the gateway page puts it: the module holds the mode it would apply on its own; with a
room unit, the unit's mode is the one in effect. The comment of the definition says so.

## Equipment

Three WCM-FS 2.0 room units (software 2726), two WCM-EM heating modules (software 7203), a
WCM-KA system manager, two condensing boilers in cascade; all scanning as `MF=Kromschröder`,
`ID=W`.

## Date

Bus reads 2026-11-17 and 2026-11-19; manual pages read 2026-11-27.

## Not verified

- That `12 01` is the register of the gateway's operating mode (one read of a unit in
  standby or reduced, above).
- Values 1, 3, 4, 5 and 13 on this installation; 12 only on the modules, where it is not in
  effect.
- Whether a value outside the list occurs (the third-party bridge names 255, "control centre",
  which no vendor page lists).
- The vendor code P111 (display).
- Writing: the gateway writes this mode, but this project does not (rule 7); the definition is
  read only.
