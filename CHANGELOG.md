# Changelog

Release history of the Weishaupt / Kromschröder ebusd definitions published from
`aghulas/ebusd-configuration`.

## 1.5.0 (2026-11-28)

Compatible release on top of 1.4.1 (no breaking changes; 1 104 messages, 692 in metadata; no
existing name, type or ID changes):

- **New: `OperatingMode` (register `12 01`, read only)** on the three room units `fs1`–`fs3` and
  the modules `em2`, `em3`: the operating mode, with the value list of the vendor's eBUS /
  Modbus gateway manual (83272304, p. 46): `Standby` 1, `HeatingOperation` 3,
  `SetbackOperation` 4, `HolidaySummer` 5, `HeatingProgram1`–`3` 11–13. Read 11 on the room
  units (heating program 1, shown on the bus) and 12 on the modules (the mode a module would
  apply without a room unit). That the gateway's list is the list of this register rests on the
  value 11; one read of a unit in standby or setback confirms it. Not defined on `ka` and
  `em1`. Metadata: menu `settings`, label "Operating mode" / "Mode de fonctionnement", labels of
  the seven entries (the gateway manual's words), five readings in
  the fixtures. Record: `evidence/operating-mode.md`.
- **`open.vendor_codes`: 48 → 53 messages.** The five `OperatingMode` messages, reason
  `display`: candidate P111 *Mode Fct Chauf* (83277504, p. 32), not published until a display
  shows it (`docs/owner-checklist-room-units.md`, item 12).
- **`ForcedVenting` (operating phase 9) has a source**: phase 9 of the oil boiler WTC-OB
  (83314005, p. 45); a WTC-GB lists 0 to 8, a WTC 15-A … 32-A uses 9 for its post-purge.
  Comments of the value list and of the label, the notice's known limit, and
  `evidence/broadcast-kastatus.md` (sources for phases 0–9, fault codes from 11 in the same
  byte). The compiled value list is unchanged.
- Workbench only: vendor address classes and cyclic telegrams in `docs/ebus-protocol.md`; the
  WTC 15-A … 32-A parameter ranges in `evidence/automat-firmware-tables.md`; scheme notes
  (WCM-KA 2.0, WCM-FS 1.x) in `evidence/vendor-codes.md`.

## 1.4.1 (2026-11-27)

Compatible release on top of 1.4.0 (no breaking changes, same 1 099 messages and 687 in metadata;
definitions and CSV unchanged, only the metadata sidecar):

- **Metadata, vendor codes (lot 2).** 79 more codes, from the manuals alone: 77 messages and the
  field `Operation.pumpspeed` of each boiler (i22). System manager `ka` (16): the system info
  601–605 and 609, the cascade orders 533 / 534, and 112, 113, 342 of its direct circuit, whose
  registers it answers. Its direct circuit `em1` (15): 112, 113, 116–118, 341, 342 of the
  direct-circuit levels and 608, the manager's fault history, on the eight fault-log registers,
  in scheme `wcm-ka-3` (the direct circuit numbers slope, frost protection and changeover 116,
  117, 118, unlike a room unit). Room units `fs1`–`fs3` (14 each): P331 on the three outside
  values, P522 room temperature, P338 on the fault log, P339 on the version. Modules `em2`,
  `em3`: P341 on the version. 213 messages and 46 fields now carry codes.
- **`open.vendor_codes`: 141 → 48 messages.** 37 circuit pairs (the 34 of 1.4.0 and the flow
  setpoint of the three room units, P526 / P527); 10 whose candidate number only a display can
  confirm (room-unit heat demand, module flow values, the boiler fan speeds against i23, the
  manager's configuration status against 513); `ka/DHWLoadingPriority`, where the manual's 571 is
  the hot-water tank position, another register. 16 messages have no number in any menu of the
  manuals and are no longer listed open (no vendor code). In the sidecar, `[[vendor_open]]`
  takes two more reasons, `display` and `mismatch` (not published).
- The record `vendor-codes` is added to the `evidence` of the 77 newly coded messages; nothing
  else in the metadata changes. Source: `evidence/vendor-codes.md`, "Codes of lot 2"; what the
  displays still have to show: `docs/owner-checklist-room-units.md`, items 7 to 11.

## 1.4.0 (2026-11-27)

Compatible release on top of 1.3.2 (no breaking changes, same 1 099 messages and 687 in metadata;
circuit, message and field names, types, IDs and CSV contents unchanged):

- **Boiler automat files for software 1104 only.** `08.w.bc1` and `18.w.bc2` are renamed
  `08.w.bc1.SW1104` and `18.w.bc2.SW1104`. With `--scanconfig` ebusd now loads them only for an
  automat that answers the scan with identification `W` and software `1104`, the software every
  message of them was established on; the circuit names stay `bc1` and `bc2`. An automat with
  another software (a WTC 25-A scans as `W`, `0315`, and answers the memory reads of
  `InstallerParameters1`–`5` with other contents) gets the upstream Wolf file `08..hc` at `08`
  and no file at `18`, instead of definitions of another firmware's memory layout
  (`evidence/bc-automat-software.md`, checked with injected scan answers).
- **Metadata:** `devices.boiler1` / `boiler2`, `circuits[].file` name the new files.
- **Metadata, vendor codes (lot 1).** New optional keys under schema 1: `vendor_schemes` (the
  numbering of a vendor document: label, document number), `vendor_codes` on a message or on a
  field (code as the manual prints it, scheme, source) and `open.vendor_codes`. 164 codes on 136
  messages, 44 fields among them: the boilers' i-codes and P-parameters (`wtc-gb`, 17 messages
  each), the system manager's parameters 532–594 (`wcm-ka-3`, 26), the room units' and modules'
  P112–P610 (`wcm-fs-2`, 23 on `fs1` and `fs3`, 22 on `fs2`, 4 on `em2` and `em3`). The
  14 manager registers for which the service tool prints a 3xx and a 5xx take the manual's 5xx;
  the three legionella parameters the tool numbers one off take the manual's 581–583. 141
  messages are listed open: 34 with one number per heating circuit, until the display of the unit
  for circuits 1 and 2 shows which it uses, and 107 whose manual pages are not read yet.
  Numberings known only from third parties are left out. The record `vendor-codes` is added to
  the `evidence` of the coded messages; nothing else changes. Source:
  `evidence/vendor-codes.md`; format: `docs/companion-contract.md`, "Vendor codes"; schema:
  `schemas/metadata.schema.json`. A consumer that ignores unknown keys is not affected.
- **Installation notice (`docs/release-readme.md`):** the known limit on `InstallerParameters1`–`5`
  becomes "boiler automats: software 1104 only", with what another software gets. It adds what the
  vendor service tool's symbol tables say of other software versions (static analysis, no such
  automat read; `evidence/automat-firmware-tables.md`): one memory layout for every 11.xx of this
  automat generation, 10.xx differing in three live values, earlier versions in more, a WTC 25-A
  in another layout altogether.

## 1.3.2 (2026-11-27)

Compatible maintenance release on top of 1.3.1 (no breaking changes, same 1 099 messages and 687 in
metadata; names, types, IDs and fields unchanged). Wording only, after the comparison with the
captures a second installation publishes (`evidence/second-installation-ebus2mqtt.md`, a WTC 25-A
with one room unit):

- **Comment of `PowerDemand`** of the three room units (`fs1`, `fs2`, `fs3`), in English and in
  French: the heat demand is sent to master `0xf1`, which is the cascade manager where one is
  fitted; the same telegram is reported on an installation without one.
- **Installation notice (`docs/release-readme.md`), known limits:** `InstallerParameters1`–`5` of
  the boiler automats were established on a WTC-GB, and a WTC 25-A answers the same requests with
  other contents; the room-unit registers and weekly programs were compared on a second
  installation.

## 1.3.1 (2026-11-24)

Compatible maintenance release on top of 1.3.0 (no breaking changes, same 1 099 messages and 687 in
metadata):

- **Metadata (`copy-in-use` cleared):** removed all 50 `open = ["copy-in-use"]` markers from
  `metadata/weishaupt.toml` following the 2026-11-23 active-heating test on circuit 2 establishing
  that the regulation loop follows the room-unit (`fs`) copy while the heating module (`em`) holds
  an independent local store (`evidence/settings-writes.md`).
- **Installation notice (`docs/release-readme.md`):** aligned *Use*, *Write* and *Known limits*
  with the stock `ebusd 26.1` write results, `75.w.fs2` heating program 3 sharing, `copy-in-use`
  resolution and `@EBUSD@` (`v26.1-weishaupt.2`); parameterized the metadata message count
  (`@META_COUNT@`) in `scripts/release.sh` so it no longer drifts.

## 1.3.0 (2026-11-22)

Compatible additions on top of 1.2.0 (no breaking changes): two re-added read-only messages and a
sharing clarification. 1 099 messages, 687 in metadata; loaded on both `v26.1-weishaupt.1` (stock)
and `v26.1-weishaupt.2`.

- **`FloorDryingTemp` / `RoomThermostatTemp` (re-added reads):** the floor-drying (`13 0a`) and
  room-thermostat (`1d 0a`) temperatures on the room unit `fs1` and the heating module `em2`,
  read-only, 16-bit (`otemp10`). Raw reads on `35` and `51` answered `02 0080` (`0x8000`, the
  no-value code a device returns when the sensor is not connected), settling the width against the
  former #717 one-byte typing that had caused them to be dropped
  (`evidence/room-thermostat-floor-drying.md`).
- **`75.w.fs2` heating program 3 shared:** shown shared with `35.w.fs1` the same way as programs 1
  and 2 (a slot written to `35` was read at `75` within 3 s) and documented read-only, written
  through `35.w.fs1` (`evidence/room-units-shared-store.md`, section 5). All five `fs2` program
  stores (heating 1/2/3, hot water, circulation) now carry the `shared_with` marker.
- **`DeCoupleMinTemp` write path confirmed (no definition change):** writable from `ff`, a
  regulation-class setting (two-screen confirmation), with its 0–50 °C bound enforced before the
  bus; `DeCoupleMaxTemp` stays read-only (`evidence/settings-writes.md`).
- **`copy-in-use` refined (no definition change):** a disambiguating write showed the room-unit and
  heating-module copies of the shared setting registers independent in both directions; the
  `open = ["copy-in-use"]` marker stays until the copy the regulation follows is identified.
- **Fixtures:** `weishaupt-fixtures-1.3.0.json` — 1 025 readings of 683 messages, verified against
  `v26.1-weishaupt.2`.

## 1.2.0 (2026-11-22)

Compatible additions on top of 1.1.0 (no breaking changes): ten read-only messages. 1 095
messages, 683 in metadata; loaded on both `v26.1-weishaupt.1` (stock) and `v26.1-weishaupt.2`.

- **`InstallerParameters1`–`5` (new reads):** the heating-specialist parameters of the boiler
  automat on `bc1` and `bc2`, five memory reads of EEPROM `0x1b` to `0x51`, 17 fields: P12 boiler
  address, P18, P30, P31, P33, P35–P38, P41, P42, P44–P46, P48, P50, P70. Established with the
  vendor service tool on both boilers (`evidence/bc-installer-parameters.md`); the other
  parameters of that level are left out until their byte is established. New metadata menu
  `specialist` for the boilers.
- **Participant at master `00` / slave `05`:** identified as the bus interface of the vendor's
  service tool (`evidence/master-00-slave-05.md`); the notice's *Known limits* say so.
- **Fixtures:** `weishaupt-fixtures-1.2.0.json` — 1 021 readings of 679 messages.

## 1.1.0 (2026-11-22)

Compatible additions on top of 1.0.0 (no breaking changes): two new reads and a documentation
clarification. 1 085 messages, 673 in metadata; loaded on both `v26.1-weishaupt.1` (stock) and
`v26.1-weishaupt.2`, with the published archive re-verified on stock ebusd.

- **`FanOperation` (new read):** the boiler fan speeds (set, actual, PWM) read while the burner
  fires, on `bc1` and `bc2` (`@ext` composite read, 7-byte ID), captured on a heating cycle
  (`evidence/boiler-firing-values.md`); `i11` / `i22` / `i32` confirmed with a live flame.
- **`H1Status` (new read):** the heating modules' H1 digital input (`29 0a`) on `em2` / `em3`,
  on/off, renamed from the former (wrong) "solar collector" label.
- **`75.w.fs2` sharing clarified:** heating program 2 and the stored hot-water and circulation
  programs are documented read-only, written through `35.w.fs1` (a direct write to `75` is not kept).
- **Fixtures:** `weishaupt-fixtures-1.1.0.json` — 1 011 readings of 669 messages, including the
  `FanOperation` firing captures, verified against `v26.1-weishaupt.2`.

## 1.0.0 (2026-11-22)

**First stable release.** Message names, field names, types, and the companion metadata / fixtures
JSON Schemas (schema 1 and schema 2) are stable; breaking changes require a new major version.

- **Definitions (1 081 messages, 669 in metadata):** identical to `0.8.0`, validated live on the
  test installation with `v26.1-weishaupt.2` and `ha-weishaupt` `v0.13.0` (all eight 3-register
  composite-read carriers verified distributing to their single-register targets on the bus).
- **100% readable fixture coverage:** 1 008 bus-captured readings covering all 668 readable
  messages across all 9 devices (`evidence/remaining-reads.md`, `evidence/fixtures.toml`); only
  the write-only `broadcast/Datetime` has no read fixture.
- **Installation notice (`docs/release-readme.md`):** updated *Known limits* to reflect that
  `75.w.fs2` `HCProgram2`, `DHWProgram` and `CircProgram` are proven shared with `35.w.fs1`.

## 0.8.0 (2026-11-22)

Unified single CSV tree and completed metadata contract (schema 1).

- **Unified composite-read carriers (1 081 messages):** replaced the separate 4-register extension
  variant (`src/main-ext.tsp`, 9-byte IDs rejected by stock ebusd) with the eight proven
  3-register composite-read carriers (7-byte IDs, `@crc(0x5c, ...)` + `@fills`) in `src/main.tsp`:
  `HolidayStart` and `HolidayEnd` on `fs1`, `fs2`, `fs3`, and `InfoTemperatures` (`OutsideTemp`,
  `SupplyTemp`, `DHWTemp`) on `bc1`, `bc2`. One single pair of archives (English and French) now
  loads cleanly on both stock `ebusd 26.1` / `v26.1-weishaupt.1` and `v26.1-weishaupt.2`.
- **Metadata contract additions (backward-compatible in schema 1, 669 messages):**
  - Linked bounds `write.below` / `write.above` on writable bound pairs (`ModulationMax` /
    `ModulationMin` on `ka`; `RoomNormalTemp` / `RoomSetbackTemp` and `SupplyMaxTemp` /
    `SupplyMinTemp` on `em1`–`em3`, `fs1`–`fs3`).
  - `stored_only: true` on the room units' stored `DHWProgram` and `CircProgram` groups
    (`fs1`, `fs2`, `fs3`).
  - `pointer` metadata (`FaultHistoryPointer`, field `value`, base `513`, step `8`) on the boiler
    `fault_history` groups (`bc1`, `bc2`).
  - `shared_with: "fs1/{name}"` extended to `fs2` `HCProgram2`, `DHWProgram` and `CircProgram`
    (84 shared program slots total).
- **Schema validation:** `weishaupt-metadata-0.8.0.json` and `weishaupt-fixtures-0.8.0.json` are
  validated against `schemas/metadata.schema.json` and `schemas/fixtures.schema.json`.

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
