# Boiler automat files: loaded for software 1104 only

## What

The two boiler automat files are named `08.w.bc1.SW1104` and `18.w.bc2.SW1104` (before: `08.w.bc1`,
`18.w.bc2`). With `--scanconfig`, ebusd loads them only for a device at `08` / `18` that answers
the scan with identification `W` and software `1104`. Circuit names (`bc1`, `bc2`), message names,
IDs and fields are unchanged.

Every message of the two files was established on automats with that software: the register
reads (`50 22`) by a sweep and reads of these two automats (`bc-info-values.md`,
`bc-live-values.md`), the memory reads (`50 00`) from the symbol table of their firmware,
`WH11928` (`bc-counters.md`, `bc-fault-counters.md`, `bc-fault-history.md`,
`bc-installer-parameters.md`, `service-tool-log.md`). The vendor tool itself picks a symbol file
per automat firmware. An automat with another software, scanned as `W` too (a WTC 25-A,
`08;Kromschroeder;W ;0315;0301`), answers `InstallerParameters1` with other contents at the same
EEPROM addresses (`second-installation-ebus2mqtt.md`, section 7), and no `50 22` read of an automat
with another software is on record. Until 1.3.2 such an automat got the same two files.

## How it was established

### The rule, from the source of ebusd

`src/ebusd/scan.cpp`, `ScanHelper::loadScanConfigFile` (ebusd 26.1, the fork build has the same
code), and `src/lib/ebus/message.cpp`, `MessageMap::extractDefaultsFromFilename`:

- The scan answer gives manufacturer, identification (5 characters; characters other than
  letters, digits and `_` are dropped, the rest lowercased: `W    ` → `w`), software and hardware
  (decimal of the BCD bytes: `11 04` → 1104, `03 15` → 315).
- Candidates are the files of the manufacturer folder whose name starts with the address and a
  dot (`08.`). The grammar, in the comment of the source:
  `ZZ.[ID.][*.][CIRCUIT.[?.]][*.][HW????.][*.][SW????.][*.]csv`. `.SWxxxx` and `.HWxxxx` are
  taken from the end of the name first (four decimal digits) and removed; the rest gives the
  identification (up to 5 characters, may be empty: `08..hc`), the circuit, and a one-digit suffix.
- A file with `SWxxxx` (or `HWxxxx`) is skipped unless the scanned value is the same number. The
  qualifier adds nothing to the score.
- Score: 1, plus the length of the identification when the file names one. A file's
  identification must equal the scanned one, or the scanned one with trailing digits removed
  one by one; a file with an empty identification matches any device. Highest score wins; on a
  tie, the longer file name.
- One file per address. Files of the folder not named `ZZ.` (here `broadcast.csv`) are loaded
  once as common files. No match: the error `unable to load scan config ZZ: no file from … matches
  ID …` and no file for that address. Inside a file, `!include` / `!load` instructions and
  per-message conditions on the scan (`[name]` prefix, emitted by `@condition(Id.Id.sw, …)`) are
  possible; upstream uses both the file-name qualifier (`src/vaillant/08.hmu.HW5103.tsp`,
  `15.350.HW7102.tsp`, `15.350.HW7202.tsp`) and scan conditions (`src/vaillant/15.430.tsp`,
  `08.bai.tsp`). `guidelines.md` of `ebusd-configuration` says nothing on either.

The TypeSpec emitter (`src/csv_emitter.ts` of `@ebusd/ebus-typespec`) names the CSV file after the
`.tsp` file (`#mkContext`: the base name of the source file, in the folder of the root namespace),
so the qualifier is part of the `.tsp` file name.

### Why the file name and not a scan condition

A condition `@condition(Id.Id.sw, "=1104")` on the namespaces `bc1` / `bc2` was compiled and
loaded first (2026-11-27). It keeps the file names, but:

- `ebusd --checkconfig` of the build with the run-time checksum (`v26.1-weishaupt.2`) reports
  `error resolving fills: … bc1 InfoTemperatures fills OutsideTemp: not found` (and the same for
  `SupplyTemp`, `DHWTemp`, and on `bc2`): without a scan answer the condition is false, and
  `MessageMap::resolveFills` of that build looks the targets up among available messages only.
  The same error is logged at run time for a device with another software.
- ebusd counts two more messages (1 101, the scan messages of `08` and `18` created for the
  conditions).
- A device answering `W` with another software still gets the file, with every message
  unavailable, and never `08..hc`.

The file-name qualifier has none of these effects and works with any ebusd.

### Checks with injected scan answers (offline, nothing sent on a bus)

ebusd `v26.1-weishaupt.2` in a container, no bus (`-d /dev/null`), `--scanconfig`, the archive
layout (root files, `wolf/` as `kromschroeder/`), the scan answers injected
(`--inject ff08070400/0a50572020202011040501`, the identification `W` padded with spaces), then `info`,
`find -c <circuit>` and `find -f -c bc1` / `bc2` over the command port. Compared with the
published `weishaupt-ebusd-config-1.3.2` (its `kromschroeder/` is byte-identical to the build of
`388889e` used here).

| Scan answer at `08` and `18` | 1.3.2 | With `SW1104` in the names |
|---|---|---|
| `W`, software `1104`, hardware `0501` | `08.w.bc1.csv`, `18.w.bc2.csv`; 35 + 35 messages | `08.w.bc1.SW1104.csv`, `18.w.bc2.SW1104.csv`; 35 + 35 messages; `find -f` output identical, only the file name in `info` differs |
| `W`, software `0315`, hardware `0301` | `08.w.bc1.csv`, `18.w.bc2.csv`; 35 + 35 messages | `08`: `08..hc.csv` (Wolf, 28 read and 12 write lines); `18`: no file (`unable to load scan config 18: no file … matches ID "w", SW0315, HW0301`) |
| `BAI00`, software `0315` (at `08` only) | `08..hc.csv` | `08..hc.csv` |

The two CSV files are byte-identical to those of `388889e` under their new names.
`scripts/integrate.sh` (`--checkconfig` on both builds): 1 099 messages, as in 1.3.2. The release
metadata built from the change differs from that of 1.3.2 only in `devices.boiler1/2.circuits[].file`
(`08.w.bc1.SW1104`, `18.w.bc2.SW1104`), besides version and commit.

### What `08..hc` gives an automat with another software

The upstream Wolf file of address `08`, the file every Weishaupt boiler at `08` got from the
official configuration before these definitions existed. 40 message lines, none polled: 28 reads
and 10 writes of registers (`50 22` / `50 23`), a heat demand `05 07` and a setpoint `08 00` as
writes to master `03`. Every one of the 38 register IDs starts with `00`; computed with the
check-byte routine of `docs/ebus-protocol.md` (section 3, `scripts/register-survey.py`, `crc`),
that byte is wrong for all 38 registers. What a Weishaupt automat does with such a read is not
established (a WTC 25-A did not answer a `50 00` read with a wrong check byte, once); in any case
the Wolf names and codecs say nothing about a Weishaupt automat. Nothing is sent unless asked, or
polled by an MQTT integration file that polls the definitions it publishes. Writes go out only on
an explicit `write`. So the boiler of another software is back where the official configuration
leaves it, and no longer decoded with memory layouts of another firmware.

## Equipment

- Here: two WTC-GB 250 automats, scan `W`, software `1104`, hardware `0501`, at `08` and `18`.
- Compared: a WTC 25-A automat, scan `W`, software `0315`, hardware `0301` (third-party data,
  `second-installation-ebus2mqtt.md`).

## Date

2026-11-27.

## Not verified

- Whether a WTC-GB with another software keeps the same register set and memory layout. It now
  gets no file of these definitions; renaming the file to its own software, or without the
  qualifier, loads them again, unchecked.
- What a Weishaupt automat answers to the Wolf reads of `08..hc`.
- The checks above injected scan answers; no device with another software was on the bus.
