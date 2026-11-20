# Weishaupt / Kromschröder definitions for ebusd — @VERSION@

eBUS message definitions for Weishaupt WTC condensing boilers and their Kromschröder WCM
controllers (system manager KA, heating modules EM, room units FS), compiled to ebusd CSV.
These devices identify themselves on the bus as manufacturer `Kromschroeder`.

**Checked on one installation:** two WTC-GB condensing boilers in cascade behind a WCM-KA
system manager, two WCM-EM heating modules and two WCM-FS room units (one of them addressed
for circuits 1 and 2), three heating circuits. Other equipment may answer differently.

Source: branch `weishaupt` of https://github.com/aghulas/ebusd-configuration at @COMMIT@
(TypeSpec, `src/wolf`). How each definition was established is recorded in
https://github.com/aghulas/weishaupt-ebus under `evidence/`. The same definitions are proposed
to the official ebusd configuration; this archive exists so that they can be used meanwhile.

## Use

1. Unpack the archive (English `@BASE@.tar.gz` or the same name ending in `-fr.tar.gz` for French) and verify checksums:

   ```sh
   tar xzf @NAME@.tar.gz
   cd @NAME@ && sha256sum -c sha256sums.txt
   ```

2. Point ebusd at the extracted directory with `--scanconfig`:

   ```sh
   ebusd --scanconfig --configpath=/path/to/@NAME@ ...
   ```

   ebusd selects each device file automatically from the identification answered to the bus scan.

3. **Reading vs writing:**
   - **Reading** works with a stock ebusd: read requests carry a precomputed checksum. This archive
     loads in the official ebusd 26.1 without error.
   - **Writing** a setting or program slot needs an ebusd build that computes the register checksum
     at run time (john30/ebusd#1825, not merged yet). Prebuilt binaries are published at
     https://github.com/aghulas/ebusd/releases/tag/@EBUSD@. With a stock ebusd the write messages
     load, but the device receives an invalid checksum: do not use them.
   - Most settings are acknowledged from any master address but taken over only from `ff`:
     `write -s ff -c ka BlockingTime 2`. `ff` is the address of the vendor's service tool; do not
     write while that tool is connected. Flow limits on `51.w.em2` and `52.w.em3` are taken from
     ebusd's own address as well; those on `50.w.em1` only from `ff`.

4. **Home Assistant companion (`ha-weishaupt`):**
   Beside the CSV archives, the release includes three files for user interfaces built on these
   definitions (contract: `docs/companion-contract.md` and JSON Schemas under `schemas/` in
   https://github.com/aghulas/weishaupt-ebus):
   - `weishaupt-metadata-@VERSION@.json` — devices, menus, short labels (EN/FR), kinds, polling
     classes, value-list labels, and write conditions.
   - `weishaupt-fixtures-@VERSION@.json` — captured bus telegrams and ebusd-decoded values.
   - `sha256sums-@VERSION@.txt` — checksums of the archives and JSON files.

   ebusd itself does not need these files.

## Languages

One archive is published per language, with identical files, message names, field names, circuit
names, value-list entries (e.g. `BurnerInOperation`) and units:

- `@BASE@.tar.gz`: comments in English;
- the same name ending in `-fr.tar.gz`: comments in French.

With a local `--configpath`, ebusd loads the files in the folder directly (`--configlang` and
`LANG` do not switch folders). Because names and value-list entries are language-independent,
`read`, `write`, MQTT topics and automations work identically with either archive.

French terms follow the vendor's French manuals where available (`evidence/terms.md` in
https://github.com/aghulas/weishaupt-ebus). Still provisional, comments and metadata labels
together: @PROVISIONAL@.

Wolf messages in `kromschroeder/broadcast.csv`, the other Wolf files of the folder and the
general root files keep their English comments, except where a comment matches a translated
string word for word.

## Content

- `kromschroeder/` — one file per device address: `08.w.bc1`, `18.w.bc2` (boilers), `15.w.ka`
  (system manager), `50.w.em1` (heating circuit 1, the system manager's direct circuit),
  `51.w.em2`, `52.w.em3` (heating modules EM#2 and EM#3, circuits 2 and 3), `35.w.fs1`,
  `75.w.fs2`, `f5.w.fs3` (room-unit addresses of circuits 1, 2 and 3), and `broadcast.csv`.
  Numbers are the vendor's circuit numbers. Also includes the upstream Wolf files that share the
  folder.
- `broadcast.csv`, `memory.csv` — general files of the official configuration.
- `sha256sums.txt`

@COUNT@ messages loaded by ebusd. Reads only, except: 92 settings across `15.w.ka`, `35.w.fs1`,
`75.w.fs2`, `f5.w.fs3`, `50.w.em1`, `51.w.em2` and `52.w.em3` (87 numbers, 5 choices), 252
program slots (`35.w.fs1`, `f5.w.fs3`, and hot-water / circulation programs of `50.w.em1`), and
the `Broadcast/Datetime` message.

## Changes in @VERSION@

Full release history is in `CHANGELOG.md` in https://github.com/aghulas/weishaupt-ebus.

**Breaking release (0.6.0, last breaking release before 1.0).** Message and field names, types
and metadata schema are frozen towards 1.0:

- **`75.w.fs2` `RoomSetbackTemp`, `RoomFrostProtectionTemp`**: read only (write lines removed;
  written via `35.w.fs1` on the test installation).
- **`51.w.em2`, `52.w.em3` `MixerPump`**: `0` / `1` → `off` / `on`.
- **`15.w.ka` `LegionellaStartTime`**: quarter-hour count (`34`) → time of day (`08:30`, `TTQ`).
- **`15.w.ka` `DHWExceeded` → `DHWExcessTemp`**: renamed, unit `°C` → `K` (`renamed_from` in
  metadata).
- **`HcMode` (`50.w.em1`, `51.w.em2`, `52.w.em3`)**: 18 unknown bits renamed to `ukn<byte>_<bit>`
  (`ink1_*`, `ink2_*`, `opmode_4..7` → `ukn1_*`, `ukn2_*`, `ukn3_4..7`), with field-level
  `renamed_from` in metadata (schema stays 1).

## Known limits

- **Single installation checked:** two WTC boilers in cascade (automat software 11.04), system
  manager, two heating modules, two room units (one addressed `#1+2`), three heating circuits.
  Other models and software versions may differ.
- **Room unit 2 (`75.w.fs2`):** on the test installation one physical room unit handles circuits
  1 and 2 (`35` and `75`). `75` answers heating program 1 and the setback / frost setpoints from
  the store of `35` and keeps no write of its own there, so they are read only in `75.w.fs2`
  (written via `35.w.fs1`). Heating programs 2 and 3 and hot-water / circulation programs of
  `75.w.fs2` are read only too (sharing not established). On another installation with a
  dedicated room unit at `75`, write lines for `75.w.fs2` can be added as a compatible 1.x
  extension once proven.
- **Scan identification:** files are named with identification `W` (e.g. `50.w.em1`). A device
  answering another identification falls back to the Wolf file for that address, if any.
- **Write verification:** each of the 92 writable settings and one slot per written program was
  changed by one step on site, read back and restored; telegrams matched the definitions.
- **Duplicate copies (`fs` vs `em`):** a room unit and its heating module answer the same setting
  registers with different values; which copy the regulation applies is not established.
- **Stored room-unit DHW / circulation programs:** on the test installation, hot water follows
  the system manager's program (`50.w.em1`), while room-unit DHW / circulation programs are
  stored only. The program selector register (`12 01`) is not defined yet.
- **`DHWLoadingPriority`:** values `0` (`Priority`) and `2` (`Parallel`) are established; `1`
  (`Sliding`) follows by elimination. Read only.
- **`ForcedVenting` (operating phase 9):** not in any manual at hand and never seen on the bus;
  what the phase is, is not established. Its label ("Forced venting", « Ventilation forcée »)
  keeps the name, not a confirmed meaning.
- **Participant at master `00` / slave `05`:** answers the identification as Kromschröder with
  an empty ID (software `0120`) and scans the bus from master `00`. What device it is, is not
  established (most likely a communication module); no file is defined for it.
- **Absent temperature sensors:** reported as an ordinary number (-100.0 on manager / modules,
  -40.0 on boilers), not the eBUS replacement value. The metadata marks affected fields with
  `absent`.
- **Memory reads (`50 00`) `firstbyte`:** reads `0` in a normal answer. In rare cases the boiler
  returns the requested byte count in `firstbyte` and all zeros for the payload; when `firstbyte`
  is non-zero, discard the reading (`guard: true` in metadata).

## Checked with

- ebusd: @EBUSD@ and the official 26.1 (`--checkconfig`: @COUNT@ messages, no error)
- TypeSpec library: @LIB@
