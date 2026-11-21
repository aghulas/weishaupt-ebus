# Changelog

Release history of the Weishaupt / Kromschröder ebusd definitions published from
`aghulas/ebusd-configuration`.

## 0.7.0 (2026-11-21)

Composite reads: one telegram can answer several registers and update each register's own message,
so a grouped read keeps one MQTT topic per value instead of adding a combined one under a separate
name. Three-register carriers (the holiday start date of a room unit) are in the standard set,
which still loads on a standard ebusd — 1 074 messages, verified on upstream ebusd 26.1.

- Four-register carriers (a boiler information block on each boiler; a survey read on each room
  unit) use message IDs longer than 7 bytes and ship in a separate extension variant
  (`weishaupt-ebusd-config-extension-0.7.0`, 1 078 messages) that needs the fork ebusd build
  v26.1-weishaupt.2 or the matching add-on; a standard ebusd refuses them.
- Every message now carries a `crc` column (the register checksum), ignored by a standard ebusd.
- Names, types and the metadata structure are unchanged; the metadata asset is unchanged in content
  (669 messages, the carriers excluded).

## 0.6.2 (2026-11-20)

Documentation only: the same definitions as 0.6.1, 1 073 messages loaded by ebusd. Changes to the
installation notice after a second cold read:

- No live write command as an example: placeholders, and a table "What can be written" of the 92
  settings by circuit and name with values, step, unit and source address, generated from the
  metadata by `scripts/settings-table.py`; what ebusd enforces (the CSV range and the value
  lists, not the step, not a range kept only in the metadata), verified with the build and no bus.
- One way to a shell in the add-on (Advanced SSH & Web Terminal, protection mode off, `docker
  exec`); the dry check as its own step before the restart.
- The add-on repository's store address next to its browsable one; start with the
  write-capable add-on when you mean to write; nothing carries over between two add-ons.
- The date and time broadcast no longer given as a command: what the controllers other than the
  clock master do with its outside temperature is not established; the integration sends it.
- Plain ebusd with the build: executable bit, 64-bit ARM and x86 only, packaged ebusd replaced by
  its updates, the official Docker image.
- Where to report a problem (issues of `aghulas/weishaupt-ebus`), and more terms in the glossary.

## 0.6.1 (2026-11-20)

First release not flagged pre-release. No message, field or type changes: 1 073 messages loaded
by ebusd, as in 0.6.0.

- Installation notice rewritten after a cold read by someone without context: use with a plain
  ebusd and with the Home Assistant add-on, each ending in a check with its expected answer; the
  write-capable ebusd and how to tell which one runs; how to write; known limits; counts with
  their origin; glossary.
- Label of operating phase 9 (`ForcedVenting`) accepted for its wording; nothing is provisional.
- Stated as not established: whether the other programs of `75.w.fs2` are shared with `35.w.fs1`,
  and what the participant at master `00` / slave `05` is.

## 0.6.0 (2026-11-20, pre-release)

**Last breaking release before 1.0.** Names of messages and fields, types and metadata schema are
frozen towards 1.0. 1 073 messages loaded by ebusd (669 in metadata, 949 fixtures).

- **`75.w.fs2` `RoomSetbackTemp`, `RoomFrostProtectionTemp`**: write lines removed (read only;
  shared with `35.w.fs1` on the test installation).
- **`51.w.em2`, `52.w.em3` `MixerPump`**: retyped from `UIN` (`0` / `1`) to value list
  `0=off;1=on`.
- **`15.w.ka` `LegionellaStartTime`**: retyped from `UIN` (quarter-hour count) to `TTQ` (`hh:mm`).
- **`15.w.ka` `DHWExceeded` → `DHWExcessTemp`**: renamed, unit `°C` → `K`, `renamed_from` in
  metadata.
- **`HcMode` (`50.w.em1`, `51.w.em2`, `52.w.em3`)**: 18 unknown bits renamed to `ukn<byte>_<bit>`
  (`ink1_*` → `ukn1_*`, `ink2_*` → `ukn2_*`, `opmode_4..7` → `ukn3_4..7`), with field-level
  `renamed_from` in metadata (schema stays 1).

## 0.5.15 (2026-11-20, pre-release)

- Added `shared_with` in metadata on the 21 slots of heating program 1 and the setback / frost
  setpoints of `75.w.fs2` (pointing to `35.w.fs1`); updated comments in English and French.
- Corrected `CalorifierExcessTemp` comment to name buffer storage (parameter 561).
- 1 075 messages (unchanged from 0.5.14).

## 0.5.14 (2026-11-19, pre-release)

- Added 99 read-only messages established by the register survey + vendor service tool / manual
  (system manager, room units, heating modules, boiler `EventCounters`). 1 075 messages.
- Removed duration units (`h`, `min`, `s`) from the five clock / timestamp fields of `50.w.em1`.

## 0.5.13 (2026-11-19, pre-release)

- Comments only: settled `PowerDemand` request state values from ten days of telegrams and
  `ControlVariation` values 0 and 1 from the room-unit manual (parameter 315). 976 messages.

## 0.5.12 (2026-11-19, pre-release)

- Metadata only (CSV identical to 0.5.11): added `absent` marker on 22 temperature fields (-40.0
  boilers, -100.0 system manager and heating modules); updated modulation limit labels.

## 0.5.11 (2026-11-19, pre-release)

- Added writable holiday dates and `ControlVariation` of the three room units, plus cascade
  modulation limits (`ModulationMax`, `ModulationMin`, P535/P536) on `15.w.ka` (94 writable
  settings, 976 messages).
- Included metadata step 0.5.10 (room-unit `PowerDemand` unused fields marked `skip`).

## 0.5.9 (2026-11-19, pre-release)

- Added five passive `PowerDemand` (`05 07`) messages (`bc1`, `bc2`, `fs1`, `fs2`, `fs3`).
  930 messages.

## 0.5.8 (2026-11-19, pre-release)

- Added write lines for the remaining four programs of `f5.w.fs3` and the hot-water and
  circulation programs of `50.w.em1` (252 writable program slots in all). 925 messages.

## 0.5.7 (2026-11-19, pre-release)

- Added write lines for heating program 1 of `f5.w.fs3` (21 slots). 799 messages.

## 0.5.6 (2026-11-18, pre-release)

- Added write lines for the five weekly programs of `35.w.fs1` (105 slots), five choice settings
  (`DHWLegionellaDay`, `CircWithLegionella`, `HolidayTempLevel`), and `Broadcast/Datetime`.
  778 messages.

## 0.5.5 (2026-11-18, pre-release)

- Metadata only (CSV identical to 0.5.4): added write ranges for setback setpoints and heating
  curves, unified `comfort` risk class on room and hot-water setpoints.

## 0.5.4 (2026-11-18, pre-release)

- Added writable flow limits (`SupplyMaxTemp`, `SupplyMinTemp`) of `50.w.em1` from source `ff`
  (66 writable settings). 662 messages.

## 0.5.3 (2026-11-18, pre-release)

- Added 42 writable settings captured on site (64 in all) and 5 reads across `15.w.ka`, `50.w.em1`,
  `52.w.em3` and the three room units. 660 messages.

## 0.5.2 (2026-11-18, pre-release)

- Added `RoomFrostProtectionTemp` (`fs1`) and `GradientCurve` (`em3`) writes (22 in all).
  613 messages.

## 0.5.1 (2026-11-18, pre-release)

- Added `RegulationP`, `RegulationI` (`ka`) and `BoilerMCBoostTemp` (`fs1`) writes (20 in all).
  611 messages.

## 0.5.0 (2026-11-18, pre-release)

- Breaking: renamed `ka/DHWOperationMode` to `ka/DHWLoadingPriority` (with `renamed_from`).
- Fixed `HcMode` decoding when a heating module has no outside sensor (-100.0).
- Added `value_labels` in metadata and full ebusd-verified fixtures (schema 2, 566 readings).
  605 messages.

## 0.4.0 – 0.4.3 (2026-11-18, superseded and deleted online)

- `0.4.3`: first release carrying `weishaupt-metadata.json` (schema 1) and `weishaupt-fixtures.json`.
- `0.4.2`: added boiler info values i39, i44, i45 (605 messages).
- `0.4.1`: added boiler info values i31, i33, i34, i35, i37; fixed `BurnerServiceHours` ×10 factor
  (599 messages).
- `0.4.0`: exposed `FirstByte` validity guard on all `50 00` memory reads (588 messages).

## 0.1.0 – 0.3.2 (2026-11-17 – 2026-11-18, superseded and deleted online)

- `0.3.2`: boiler fault counters as seven ≤10-byte reads with `FirstByte`.
- `0.3.0` / `0.3.1`: first French archive (`src/fr.yaml`), vendor terminology and owner wording.
- `0.1.0` – `0.2.0`: initial compiled CSV archives from TypeSpec (`src/wolf/`).
