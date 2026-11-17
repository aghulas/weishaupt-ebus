# Weishaupt / Kromschröder definitions for ebusd — @VERSION@

eBUS message definitions for Weishaupt WTC condensing boilers and their Kromschröder WCM
controllers (system manager KA, heating modules EM, room units FS), compiled to ebusd CSV.
These devices identify themselves on the bus as manufacturer `Kromschroeder`.

Source: branch `weishaupt` of https://github.com/aghulas/ebusd-configuration at @COMMIT@
(TypeSpec, `src/wolf`). How each definition was established is recorded in
https://github.com/aghulas/weishaupt-ebus under `evidence/`. The same definitions are proposed
to the official ebusd configuration; this archive exists so that they can be used meanwhile.

## Content

- `kromschroeder/` — one file per device address: `08..bc1`, `18..bc2` (boilers), `15..ka`
  (system manager), `35..fs1` (room unit), `50..em1`, `51..em2`, `52..em3` (heating modules),
  and the broadcast messages. It also holds the Wolf files of the official configuration, which
  share the folder.
- `broadcast.csv`, `memory.csv` — the general files of the official configuration.
- `sha256sums.txt`

@COUNT@ messages. Reads only, except the 17 settings of `15..ka`, `35..fs1` and `51..em2` that are
read and written.

## Use

```sh
tar xzf weishaupt-ebusd-config-@VERSION@.tar.gz
ebusd --scanconfig --configpath=/path/to/weishaupt-ebusd-config-@VERSION@ ...
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

## Known limits

- Checked on one installation: two WTC boilers in cascade (automat software 11.04), system
  manager, three heating circuits. Other models and software versions may differ.
- `10..bc1` and `10..bc2` (status telegrams the boilers send to the cascade master) were not
  loaded by `--scanconfig` in the test of this archive, as address `10` is a master and is not
  scanned. The same status is in the broadcast `KaStatus`.
- The write definitions were checked by decoding captured telegrams; ebusd sending them from
  these definitions has not been observed on a bus yet.

## Checked with

- ebusd: @EBUSD@ and the official 26.1 (`--checkconfig`: @COUNT@ messages, no error)
- TypeSpec library: @LIB@
