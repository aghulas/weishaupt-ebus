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

@COUNT@ messages. Reads only, except the 44 settings of `15.w.ka`, `35.w.fs1`, `75.w.fs2`, `f5.w.fs3`,
`51.w.em2` and `52.w.em3` that are read and written. More than half of the messages are the weekly programs of the room units, one
message per switch-time slot (heating programs 1 to 3, hot water, circulation).

## Changes since 0.4.3

- **One message is renamed: this breaks whatever names it.** `DHWOperationMode` of the system
  manager (`15.w.ka`) is now `DHWLoadingPriority`. The register is not an operating mode: it
  is the parameter the vendor calls "DHW operation", which sets whether a heating circuit is
  cut while the hot water is loaded (priority), supplied at the same time (parallel) or cut
  depending on the boiler temperature (sliding). Register, type and value list are the same;
  only the name and the comments change. A `read -c ka DHWOperationMode`, an MQTT topic
  `ka/DHWOperationMode` or an automation built on it must take the new name; the metadata
  file gives the former key in `renamed_from`. Of the three values only 0 (`Priority`) has
  been read on a device: which of 1 and 2 is `Sliding` and which `Parallel` is not
  established.
- **`HcMode` of a heating module without outside sensor now decodes.** Such a module sends
  -100.0 as outside temperature; up to 0.4.3 that value was outside the range of the field
  and ebusd gave `ERR: argument value out of valid range` for the whole message (`51.w.em2`,
  `52.w.em3` on the test installation). The field has no range any more and reads -100.0,
  which means "no sensor". Nothing changes for a module that has the sensor.
- **Labels of the value-list entries in the metadata file** (`value_labels`, English and
  French, for the 38 entries of the seven value lists). The CSV are not concerned: the
  entries keep their names.
- No message added or removed, no other field changed.

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
  write while that tool is connected.

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

- Checked on one installation: two WTC boilers in cascade (automat software 11.04), system
  manager, three heating circuits. Other models and software versions may differ.
- The files are named with the identification the devices answer to the scan (`W`), for
  example `50.w.em1`. A device that answers another identification gets the Wolf file of the
  same address, if there is one.
- The write definitions were checked by decoding captured telegrams. Each of the 44 settings
  was seen on the installation changed by one step, read back with the new value and restored;
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
  for 0 only; the manual lists the settings in the order priority, parallel, sliding. The
  message is read only.
- The operating phase `ForcedVenting` (9) of the status messages comes from no manual and was
  never seen on a bus; its label in the metadata file is provisional.
- A temperature whose sensor is not fitted reads as a number: -100.0 on a heating module or
  the system manager, -40 on a boiler. Nothing in the telegram marks it.
- Every memory read (`50 00`) of the boilers — the fault history, the operating counters, the
  live values and the fault counters `FaultCounters1` to `7` — starts with the field
  `firstbyte`. It reads 0 in a normal answer. In 2 of 107 answers of one boiler it read the
  number of bytes asked for while every value of that answer read 0 although the memory held
  other values: when `firstbyte` is not 0, the values of that reading are not valid.

## Checked with

- ebusd: @EBUSD@ and the official 26.1 (`--checkconfig`: @COUNT@ messages, no error)
- TypeSpec library: @LIB@
