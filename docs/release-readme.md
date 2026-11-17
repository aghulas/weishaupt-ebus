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

@COUNT@ messages. Reads only, except the 17 settings of `15.w.ka`, `35.w.fs1` and `51.w.em2` that are
read and written. More than half of the messages are the weekly programs of the room units, one
message per switch-time slot (heating programs 1 to 3, hot water, circulation).

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
installation; still provisional: @PROVISIONAL@.

The Wolf messages in `kromschroeder/broadcast.csv`, the other Wolf files of the folder and the
general files keep their English comments, except a comment that is word for word one of
those translated here (for example `temperature`).

## Known limits

- Checked on one installation: two WTC boilers in cascade (automat software 11.04), system
  manager, three heating circuits. Other models and software versions may differ.
- The files are named with the identification the devices answer to the scan (`W`), for
  example `50.w.em1`. A device that answers another identification gets the Wolf file of the
  same address, if there is one.
- The write definitions were checked by decoding captured telegrams. One write was tested on
  the installation (`BlockingTime`, 1 to 2 and back, from `ff`): the telegrams were the expected
  ones and the device took the value. They were built by the ebusd of the installation with its
  own configuration; ebusd sending from the files of this archive has not been observed yet.
- A room unit and its heating module answer the same setting registers with different values;
  which copy the regulation uses is not established. The written settings of `51.w.em2` are the
  copy of the module.
- The room units answer hot-water and circulation programs as well. On the installation they
  are stored only: the hot water follows the program of the system manager (`DHWProgram…` of
  `50.w.em1`). The heating of a circuit follows the program of its room unit; a room unit
  whose selector reads 11 runs heating program 1. The selector is not defined.

## Checked with

- ebusd: @EBUSD@ and the official 26.1 (`--checkconfig`: @COUNT@ messages, no error)
- TypeSpec library: @LIB@
