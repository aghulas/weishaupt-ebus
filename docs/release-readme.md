# Weishaupt / Kromschröder definitions for ebusd — @VERSION@

eBUS message definitions for Weishaupt WTC condensing boilers and their Kromschröder WCM
controllers (system manager KA, heating modules EM, room units FS), compiled to ebusd CSV.
These devices identify themselves on the bus as manufacturer `Kromschroeder`.

Source: branch `weishaupt` of https://github.com/aghulas/ebusd-configuration at @COMMIT@
(TypeSpec, `src/wolf`). How each definition was established is recorded in
https://github.com/aghulas/weishaupt-ebus under `evidence/`. The same definitions are proposed
to the official ebusd configuration; this archive exists so that they can be used meanwhile.

## Content

- `kromschroeder/` — one file per device address: `08.w.bc1`, `18.w.bc2` (boilers), `15.w.ka`
  (system manager), `35.w.fs1`, `75.w.fs2`, `f5.w.fs3` (room units), `50.w.em1`, `51.w.em2`,
  `52.w.em3` (heating modules), and the broadcast messages. It also holds the Wolf files of the official configuration, which
  share the folder.
- `broadcast.csv`, `memory.csv` — the general files of the official configuration.
- `sha256sums.txt`

@COUNT@ messages. Reads only, except what is read and written: 94 settings of `15.w.ka`,
`35.w.fs1`, `75.w.fs2`, `f5.w.fs3`, `50.w.em1`, `51.w.em2` and `52.w.em3` (89 numbers, 5
choices), 252 program slots (the five programs of `35.w.fs1` and of `f5.w.fs3`, the
hot-water and circulation programs of `50.w.em1`), and the date and time broadcast. More than half of the messages are the weekly programs of the room units, one
message per switch-time slot (heating programs 1 to 3, hot water, circulation).

## Changes since 0.5.14

- **Heating program 1 of room unit 2 is changed on room unit 1.** On the test installation the
  room unit at `75` answers heating program 1 from the store of the one at `35`: a slot written
  to `35` is read at `75` within seconds, and a slot written to `75` is acknowledged and not
  kept. The 21 slots of heating program 1 in `75.w.fs2` stay read only, as before; their
  comment now says so and names the place to change them, `35.w.fs1` (French:
  « … en lecture seule : vue comme la plage de la commande à distance 1, écrite via
  35.w.fs1 »). For a user: read the program of room unit 2 there, change it on room unit 1.
- **`shared_with` in the metadata** (new key, described in the contract of the companion): on
  each of these 21 slots, the key of the slot of `35.w.fs1` that keeps the value
  (`fs2/HCProgram1Mon1` → `fs1/HCProgram1Mon1`). An interface shows the slot read only with a
  pointer to room unit 1 and reads it again after a write there. Heating programs 2 and 3, the
  hot-water and circulation programs and the setpoints of `75.w.fs2` carry no marker: their
  sharing is not proven.
- `CalorifierExcessTemp` of `15.w.ka`: the comment names the buffer storage (parameter 561), not
  the hot water; name, register and value unchanged.
- **Users of 0.5.14 lose nothing.** Same 1 075 messages, same names, fields, types and writes; no
  write added or removed. The CSV of `15.w.ka` and `75.w.fs2` differ in comments only, English
  and French: ebusd shows the new comments after a start with the new files, and reads and
  publishes the same values meanwhile. An interface takes the metadata with a reload.

## Changes from 0.5.13 to 0.5.14

- **Units of five clock fields of `50.w.em1`.** `SystemHour`, `SystemMinute`, `SystemSecond`
  (the system clock) and `ErrorHour`, `ErrorMinute` (the time stamp of a fault-log entry) are
  times of the day, not durations: they lose the units `h`, `min`, `s`, like their neighbours
  day, month and year. Name, type, register and value are unchanged; an interface no longer
  shows them as durations. The CSV of `50.w.em1` changes: ebusd takes the new files at its next
  start, an interface the metadata with a reload.
- **24 new reads** (stock ebusd), each established by the vendor service tool's screen and an
  independent read with the same value. `15.w.ka`: `ModulationDiffTemp` (parameter 538, K),
  `DeCoupleExcessTemp`, `DeCoupleMaxTemp`, `CalorifierExcessTemp`, `SummerTimeStartDay`,
  `SummerTimeStartMonth`, `SummerTimeEndDay`, `SummerTimeEndMonth`, `BoilerSequence1First`,
  `BoilerSequence1Second`, `BoilerSequence2First`, `BoilerSequence2Second` (A or B),
  `DHWSetbackTemp`, `LegionellaStartTime` (quarter hours since midnight),
  `PlateExchangerPrimaryTemp` (sensor B24). Each room unit: `RoomSetpointTemp` (the room setpoint
  in effect), `OutsideMixedTemp`, `HeatingCircuitType` (read only). The CSV of `15.w.ka` and of the
  three room units gain these lines; nothing else changes in them.
- **54 more reads** (stock ebusd, 16 on each room unit, 3 on each heating module), with two
  sources each. Each room unit: `VersionMajor`,
  `VersionMinor`, the hot-water settings it stores (`DHWLoadingPriority`, `DHWSetbackTemp`,
  `DHWMaxTemp`, `DHWLegionellaDay`, `LegionellaCirculationTime`; the system manager's values are
  the ones in use where it prepares the hot water) and its fault log (`ErrorId` … `ErrorYear`, as
  on `50.w.em1`). Each heating module (`51.w.em2`, `52.w.em3`): `MixerParameter`, `VersionMajor`,
  `VersionMinor`.
- **21 more reads** (stock ebusd), two sources each. Both boilers: `EventCounters`, one memory
  read of six counters: burner hours and ignitions of the day (`burnerhourstoday`,
  `ignitionstoday`, named after the firmware symbols only, both read 0), mains switch-ons, resets,
  shut-offs, and `ukn6`, a counter whose meaning is not established. It sits with the other
  boiler counters (`Counters`) in the boiler files. Each room unit:
  `SummerTimeStartDay`, `SummerTimeStartMonth`, `SummerTimeEndDay`, `SummerTimeEndMonth`, and
  `LegionellaSetpoint` as it stores it. Each heating module: `MixerPump` (state of the
  mixer-circuit pump) and `CirculationReturnSetTemp`.
- 99 messages more in all; no message renamed, removed or retyped, no write added. ebusd takes the
  new files at its next start; an interface takes the metadata with a reload.

## Changes from 0.5.12 to 0.5.13

- **Comments only; no message, field, type or value changes.** ebusd still needs the new files:
  the comments are part of the CSV, so install the archive and restart ebusd with it, as for any
  release that changes the CSV. What ebusd reads, writes and publishes stays the same. An
  interface that reads the metadata file then takes it with a reload of its configuration (only
  the descriptions change).
- `PowerDemand` of the boilers and of the room units: the comment of `status` now says what ten
  days of telegrams show, power requested (`0x66` to the first boiler, `0xee` to the second) or
  not (`0x55`, `0x00`) from the cascade manager, `0xbb` or `0x55` from a room unit; the field
  stays a number.
- `ControlVariation` of the three room units: the comment names the values from the manual of
  the room unit (parameter 315), 0 constant flow temperature, 1 outside temperature; which of 2
  and 3 is room control is not established, so the field stays a number.
- Files that change: `08.w.bc1`, `18.w.bc2`, `35.w.fs1`, `75.w.fs2`, `f5.w.fs3`, English and
  French.

## Changes from 0.5.11 to 0.5.12

- **Metadata only; the CSV files are the same as in 0.5.11.** ebusd needs nothing; an interface
  that reads the metadata file takes this release with a reload of its configuration.
- New field key `absent`: the value a temperature reads when its sensor is not fitted, -40.0 on
  the boilers, -100.0 on the system manager and the heating modules, on the 22 temperature
  fields where the evidence shows or states it (information values outside, hot water and
  hydraulic separator and the four temperatures of the memory read of both boilers; outside,
  hot water and de-couple of the system manager; outside temperature of the exchange of the
  three heating circuits, flow temperature of the modules `51` and `52`). An interface can show
  "no sensor" instead of the number.
- Labels of the modulation limits of `15.w.ka` in the metadata: `ModulationMax` "Maximum
  modulation (optimal range)" / « Modulation maximale (plage optimale) », `ModulationMin`
  "Minimum modulation (optimal range)" / « Modulation minimale (plage optimale) » (were
  "Optimal range, upper / lower limit"). Message names unchanged.

## Changes from 0.5.9 to 0.5.11

This release holds two steps; the first, 0.5.10, was not published on its own.

### New messages and writes

- **Holiday dates of the room units** (`35.w.fs1`, `75.w.fs2`, `f5.w.fs3`), read and written
  from `ff`: `HolidayStartDay`, `HolidayStartMonth`, `HolidayEndDay`, `HolidayEndMonth` (calendar
  day 1 to 31, month 1 to 12), and the third register of each date, `HolidayStartThird` and
  `HolidayEndThird`, whose meaning is not established (0 and 24 were written and read back; in
  the metadata their write conditions say `open = ["meaning"]`). Each register of the three
  units was changed and restored on site.
- **Control variation of the room units** (`ControlVariation`, register `41 01`), read and
  written from `ff`, a number: 1 is the value in service; 0 was written and read back, and while
  it was set the heating modules raised their flow setpoint (on one circuit to its maximum).
  No value has an established name (metadata: `open = ["meaning"]`).
- **Limits of the optimal operating range of the cascade** in `15.w.ka` (`ModulationMax`,
  `ModulationMin`, vendor parameters 535 and 536, percent, 30 to 100; the lower must stay below
  the upper), read and written from `ff`, each changed by one percent and restored on site.
- Writing needs the ebusd with the run-time checksum, as every write here. 46 messages more;
  nothing renamed.
- The CSV of the three room units and of `15.w.ka` change: unlike the metadata step below, ebusd needs the new files (a restart
  of ebusd with them), then the interface takes the metadata as before.

### Metadata (the step called 0.5.10)

- **Metadata only; the CSV files are the same as in 0.5.9.** ebusd needs nothing: keep the
  0.5.9 files or swap them, the messages are identical. An interface that reads the metadata
  file takes this release with a reload of its configuration, without a restart of ebusd or of
  the interface: the first update of the definitions that installs this way.
- `PowerDemand` of the room units (`35.w.fs1`, `75.w.fs2`, `f5.w.fs3`): `modulation` and
  `dhwsettemp` are marked `skip` in the metadata, as `ukn2` already was. The room units always
  send the replacement value there (ebusd prints `-`), so an interface no longer shows two
  values that never have one. The boilers keep these fields.
- The requested flow temperature of the room units' `PowerDemand` has its own label,
  "Requested flow temperature (sent)", so that it no longer has the label of the message
  `HeatDemandTemp` of the same device (an interface had to put the message label in front).
- A source comment of the boiler information values corrected (no effect on the CSV).

## Changes from 0.5.8 to 0.5.9

- **Heat demand telegrams `05 07`** (`PowerDemand`, five messages), passive, nothing polled:
  what each room unit asks the cascade manager (`35.w.fs1`, `75.w.fs2`, `f5.w.fs3`) and what
  the cascade manager asks each boiler (`08.w.bc1`, `18.w.bc2`). Named fields:
  `heatdemandtemp` (room unit: its requested flow temperature; manager: its modulation limit
  temperature), `modulation` (manager to boiler: the burner load asked for, in %),
  `dhwsettemp` (manager to boiler: the hot-water setpoint), `status` (a plain number: `238`
  or `102` while a boiler is asked for power). The other bytes are published as `ukn2`,
  `ukn5`, `ukn9`, meaning not established. Field names are lower case, as for every message
  of these files. Nothing else changed: no message renamed, no write added.

## Changes from 0.5.7 to 0.5.8

- **More weekly programs can be written**, one telegram per slot, from ebusd's own address: the
  four other programs of `f5.w.fs3` (heating 2 and 3, stored hot water and circulation) and
  the hot-water and circulation programs of `50.w.em1` (the hot-water program is the one the
  installation applies). In each program one slot was seen changed and read back. The
  programs of `75.w.fs2` stay read only: room unit 2 acknowledged four slot writes, on two days,
  an empty slot and a slot in use, and kept none. The read ids are unchanged.

## Changes from 0.5.6 to 0.5.7

- **Heating program 1 of `f5.w.fs3` can be written** (21 slots, from ebusd's own address), on
  one slot seen changed and read back, as the programs of `35.w.fs1`. The other programs of
  room unit 3, the programs of `75.w.fs2` (it acknowledged a slot write and did not keep it)
  and those of `50.w.em1` stay read only.

## Changes from 0.5.5 to 0.5.6

- **The five weekly programs of `35.w.fs1` can be written**: 105 slots, one telegram per slot,
  from ebusd's own address (`write -c fs1 HCProgram1Tue1 18:00;Enabled;06:30;Enabled`). In each
  program one slot was seen changed and read back on the test installation; the other 20 share
  its codec and register scheme (`proof: family` in the metadata). The programs of `75.w.fs2`,
  `f5.w.fs3` and `50.w.em1` stay read only: room unit 2 acknowledged the same slot write and did
  not keep it. The read ids are unchanged.
- **Five choices**, read and written: `DHWLegionellaDay` and `CircWithLegionella` of
  `15.w.ka`, `HolidayTempLevel` of the three room units (taken from `ff`).
- **Date and time**: `Broadcast/Datetime` can be sent (`write -c Broadcast Datetime
  <outside>;<hh:mm:ss>;<dd.mm.yyyy>`); the clock master takes the time as sent, seconds
  included. Send at second 00 of the minute carried: a late broadcast sets the installation
  late until the next one.
- The metadata may carry write conditions on program slots (`docs/companion-contract.md`).

## Changes from 0.5.4 to 0.5.5

- **Metadata only; the definitions are those of 0.5.4.** The setback room setpoint and the
  heating curve of every circuit get a range in their write conditions (10.0 to 21.5 and
  2.5 to 40.0, step 0.5, from the user manual of the room unit), which the definitions cannot
  carry. The normal and setback room setpoints and the hot-water setpoint are class `comfort`
  on every device (before: only on `51.w.em2`).
- From 0.5.3 to 0.5.4: **two more settings can be written, 66 in all**: `SupplyMaxTemp` and `SupplyMinTemp` of
  `50.w.em1`. They are taken only from `ff` (written from another address they are
  acknowledged and not taken); each was seen on the test installation changed by one step from
  `ff`, read back with the new value and restored; no message renamed or removed.
- From 0.5.2 to 0.5.3: 42 settings became writable (64 in all) and five reads were added
  (`DHWSetpoint` of the three room units, `BoilerMCBoostTemp` of `75.w.fs2` and `f5.w.fs3`).
- From 0.4.x: 0.5.0 renamed `DHWOperationMode` of `15.w.ka` to `DHWLoadingPriority` (the
  metadata file gives the former key in `renamed_from`) and made `HcMode` of a heating module
  without outside sensor decode (-100.0 means no sensor).

## Other files of the release

Beside the archives the release carries three files. ebusd needs none of them; they are for
user interfaces built on the definitions (format: `docs/companion-contract.md` in
https://github.com/aghulas/weishaupt-ebus).

- `weishaupt-metadata-@VERSION@.json` — for every message of the Weishaupt files: its device,
  menu, short label in English and French, kind of value, polling class, a label for each
  entry of a value list and, for a setting, the conditions of a write.
- `weishaupt-fixtures-@VERSION@.json` — for every message, telegrams captured on a bus
  (request, answer) with the values ebusd decodes them to, as test data.
- `sha256sums-@VERSION@.txt` — checksums of the archives and of these two files.

## Use

```sh
tar xzf @NAME@.tar.gz
ebusd --scanconfig --configpath=/path/to/@NAME@ ...
```

ebusd picks the files from the identification each device answers to the scan.

- **Reading** works with a stock ebusd: the read requests carry a precomputed checksum. The
  archive loads in the official ebusd 26.1 without error.
- **Writing** a setting needs an ebusd that computes the register checksum at run time
  (john30/ebusd#1825, not merged yet). A build is published at
  https://github.com/aghulas/ebusd/releases/tag/@EBUSD@. With a stock ebusd the write messages
  load but the device does not get a valid checksum: do not use them.
- Most settings are acknowledged from any source address but taken over only from `ff`:
  `write -s ff -c ka BlockingTime 2`. `ff` is the address of the vendor's service tool; do not
  write while that tool is connected. The flow limits of `51.w.em2` and `52.w.em3` are taken
  from ebusd's own address as well; those of `50.w.em1` only from `ff`.

## Languages

The release has one archive per language, with the same files and the same messages:

- `@BASE@.tar.gz`: comments in English;
- the same name ending in `-fr`: comments in French.

Choose by downloading the archive of the language and giving its folder to `--configpath`.
With a local configuration path, ebusd loads the files it finds: `--configlang` and the `LANG`
environment variable do not select anything here. This archive is `@NAME@`.

Only the comments of messages and fields are translated, those `find -v` and the JSON
definitions show. Message names, field names, circuit names, the entries of value lists (for
example `BurnerInOperation`) and units are the same in every language: they are what `read`,
`write`, MQTT topics and automations use, so a configuration made with one archive works with
the other. With the stock MQTT integration file, Home Assistant shows names, not comments: the
French archive changes nothing there.

The French terms are those of the vendor's French manuals where they give one (list with
document number and page: `evidence/terms.md` in https://github.com/aghulas/weishaupt-ebus).
Where no manual at hand gives a term, the wording was chosen with the operator of the test
installation; still provisional, comments and labels of the metadata file together:
@PROVISIONAL@.

The Wolf messages in `kromschroeder/broadcast.csv`, the other Wolf files of the folder and the
general files keep their English comments, except a comment that is word for word one of
those translated here (for example `temperature`).

## Known limits

- One room unit of the test installation (`75.w.fs2`) acknowledges program-slot writes and keeps
  none; its programs are read only here. Heating program 1 is shown to be the one of `35.w.fs1`
  (see "Changes since 0.5.14"); whether one room unit answers at both addresses there, and
  whether `75` behaves the same on another installation, is not established. The two other
  room units keep their slot writes.
- Checked on one installation: two WTC boilers in cascade (automat software 11.04), system
  manager, three heating circuits. Other models and software versions may differ.
- The files are named with the identification the devices answer to the scan (`W`), for
  example `50.w.em1`. A device that answers another identification gets the Wolf file of the
  same address, if there is one.
- The write definitions were checked by decoding captured telegrams. Each of the 71 settings
  and one slot of each written program was seen on the installation changed by one step, read back with the new value and restored;
  the telegrams were the expected ones. They were built by the ebusd of the installation with
  its own configuration or by a client sending raw telegrams; ebusd sending from the files of
  this archive has not been observed yet.
- A room unit and its heating module answer the same setting registers with different values;
  which copy the regulation uses is not established. The written settings of `51.w.em2` and
  `52.w.em3` are the copies of the modules, those of `35.w.fs1`, `75.w.fs2` and `f5.w.fs3` the
  copies of the room units.
- The room units answer hot-water and circulation programs as well. On the installation they
  are stored only: the hot water follows the program of the system manager (`DHWProgram…` of
  `50.w.em1`). The heating of a circuit follows the program of its room unit; a room unit
  whose selector reads 11 runs heating program 1. The selector is not defined.
- The value list of `DHWLoadingPriority` (`0=Priority;1=Sliding;2=Parallel`) is established
  for 0 (read on the system manager) and 2 (shown as "parallel" by the vendor tool on two room
  units); 1 follows by elimination. Its comment in `15.w.ka` still says only 0 is established.
  The message is read only.
- The operating phase `ForcedVenting` (9) of the status messages comes from no manual and was
  never seen on a bus; its label in the metadata file is provisional.
- A temperature whose sensor is not fitted reads as a number: -100.0 on a heating module or
  the system manager, -40 on a boiler. Nothing in the telegram marks it; the metadata file
  marks the fields concerned with `absent`.
- Every memory read (`50 00`) of the boilers — the fault history, the operating counters, the
  live values and the fault counters `FaultCounters1` to `7` — starts with the field
  `firstbyte`. It reads 0 in a normal answer. In 2 of 107 answers of one boiler it read the
  number of bytes asked for while every value of that answer read 0 although the memory held
  other values: when `firstbyte` is not 0, the values of that reading are not valid.

## Checked with

- ebusd: @EBUSD@ and the official 26.1 (`--checkconfig`: @COUNT@ messages, no error)
- TypeSpec library: @LIB@
