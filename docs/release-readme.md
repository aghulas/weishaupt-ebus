# Weishaupt / Kromschröder definitions for ebusd — @VERSION@

eBUS message definitions for Weishaupt WTC condensing boilers and their Kromschröder WCM
controllers, compiled to ebusd CSV: the system manager (WCM-KA, also called cascade manager),
the heating modules (WCM-EM) and the room units (WCM-FS). These devices identify themselves on
the bus as manufacturer `Kromschroeder`. Unofficial: not made or endorsed by Weishaupt or
Kromschröder.

**Checked on one installation:** two Weishaupt WTC-GB 250 condensing boilers in cascade
(automat software 11.04), a WCM-KA 3.0 system manager, two WCM-EM heating modules and two WCM-FS
room units, one of them addressed for heating circuits 1 and 2; three heating circuits. Other
equipment may answer differently.

**Your responsibility.** Reading changes nothing. Writing changes the settings of a gas heating
appliance: do it only if you understand the setting, note its value first, and expect no help
from the manufacturer for an installation changed this way. When in doubt, leave settings to
your heating installer.

## Use

What you need: an eBUS adapter connected to the bus of the WCM controllers, and ebusd (any 26.1
build reads; writing needs the build named under "Write").

The files are installed by pointing ebusd at the unpacked folder with `--configpath`. ebusd then
uses these files instead of the definitions it would fetch online: message and entity names
change for an installation that used other definitions before (MQTT topics, automations).

### Read with a plain ebusd

1. Download `@BASE@.tar.gz` (English comments) or the same name ending in `-fr` (French comments) and
   `sha256sums-@VERSION@.txt` from the release page, check and unpack (this notice uses
   `@NAME@`, the archive it came in):

   ```sh
   sha256sum -c --ignore-missing sha256sums-@VERSION@.txt    # macOS: shasum -a 256 -c --ignore-missing …
   tar xzf @NAME@.tar.gz
   ```

2. Optional dry check, without a bus: `ebusd -f --checkconfig --configpath=/path/to/@NAME@`
   prints `found messages: @COUNT@ (…)` and no error.

3. Start ebusd on the folder, with a scan so that each device gets its file, and keep your other
   options (adapter, MQTT, address):

   ```sh
   ebusd --scanconfig --configpath=/path/to/@NAME@ --device=<your adapter> …
   ```

4. Check, once the scan has run (a minute or two):

   ```sh
   ebusctl scan result                 # one line per device: address;manufacturer;ID;software;hardware
   ebusctl info                        # version, signal, then one "address …" line per device
   ebusctl read -c ka OutsideTemp      # a temperature in °C
   ebusctl read -c ka LegionellaStartTime   # a time, e.g. 08:30
   ```

   On the test installation `scan result` lists twelve addresses, for example
   `15;Kromschroeder;W ;6618;-` (system manager) and `08;Kromschroeder;W?;1104;0501` (boiler
   automat): nine get a file (`08`, `18`, `15`, `50`, `51`, `52`, `35`, `75`, `f5`), three none
   (`05`, `0c`, `f6`), which is expected. `ERR: element not found` on a read means the file of
   that device was not loaded (see "Device identification" under Known limits).

### Read with the Home Assistant ebusd add-on

The steps are the same for the stock add-on "eBUSd" and for "eBUSd (Weishaupt CRC)" (see
"Write"). The add-on's `/config` is a folder of its own, `/addon_configs/<prefix>_ebusd/` on the
host (the prefix depends on the add-on repository; `ls /addon_configs/` shows it): not the
`/config` folder of Home Assistant.

1. Copy the unpacked folder `@NAME@` into `/addon_configs/<prefix>_ebusd/` (Samba share
   `addon_configs`, the Studio Code Server add-on, or SSH).
2. In the add-on's **Configuration**, **Additional ebusd options (one flag per entry)**, add two
   entries, each in a field of its own, and keep the others (`--mqttjson`, your address):

   ```text
   --scanconfig
   --configpath=/config/@NAME@
   ```

3. Restart the add-on and wait for the scan (a minute or two).
4. Check with the `ebusctl` commands of step 4 above, run inside the add-on, with the same
   expected answers. The add-on's documentation offers a shell there under **Open Web UI**; where
   that page shows ebusd's web page instead, use the SSH add-on (with its protection mode off):
   `docker ps` shows the add-on's container (its name ends in `_ebusd`), then
   `docker exec <container> ebusctl scan result`. In the same shell, before a restart,
   `ebusd -f --checkconfig --configpath=/config/@NAME@` is the dry check (`found messages:
   @COUNT@ (…)`).

Home Assistant integrations reach the add-on's ebusd by its internal host name (`<prefix>-ebusd`,
port 8888) without publishing a port. Publishing 8888 on the add-on's **Network** page opens
ebusd's command port, writes included, to your whole network.

With the MQTT integration file the add-on seeds (`mqtt-hassio.cfg`, `filter-direction = r|u`),
Home Assistant gets read-only entities; writable messages become entities only if you change
that filter. Do not change it with a stock ebusd (see "Write").

### Write

**The ebusd build.** Each write telegram carries a checksum over its register and value, which
ebusd must compute when it sends. The official ebusd cannot yet (john30/ebusd#1825): it loads the
write lines of these files but sends a wrong checksum. Use the build
[@EBUSD@](https://github.com/aghulas/ebusd/releases/tag/@EBUSD@):

- **Home Assistant:** in the add-on store, ⋮ → Repositories, add
  `https://github.com/aghulas/ha-addons#weishaupt` and install **eBUSd (Weishaupt CRC)**. Stop
  the stock eBUSd (one adapter, one add-on) and set the new one up as above: it has its own
  `/addon_configs/<prefix>_ebusd/` folder, so copy the definitions there too.
- **Plain ebusd:** the release holds two static executables, `ebusd-aarch64` and `ebusd-amd64`
  (MQTT, no TLS, no KNX). Check them against its `sha256sums.txt` and run the one of your
  machine in place of `ebusd`, with the same options.

**Which ebusd runs.** The first line of `ebusctl info` is the version of the running ebusd: the
build shows `version: ebusd 26.1.p20261029`; a stock 26.1 shows another string (for example
`26.1.26.1`). Which one you started: in Home Assistant, the add-on's Info page names **eBUSd
(Weishaupt CRC)** with a version ending in `-weishaupt.1`; on a plain install, the executable
you start is the one whose checksum matches the release's `sha256sums.txt`
(`sha256sum $(command -v ebusd)`). The Home Assistant integration tells the two builds apart by
itself, without sending anything: the attribute `run_time_checksum` of its write switch reads
`present` with the build and `absent` with a stock ebusd.

**How to write.**

- **Before:** read the value and note it (`ebusctl read -f -c ka BlockingTime`). **After:** read it
  again with `-f` (from the device, not ebusd's cache); only that read shows that the value was
  taken. To restore, write the noted value.
- **Source address.** The devices acknowledge a write from any address but take most settings
  only from `ff`, the address of the vendor's service tool: `ebusctl write -s ff -c ka
  BlockingTime 2`. Taken from ebusd's own address (no `-s`): the flow limits `SupplyMaxTemp` and
  `SupplyMinTemp` of `51.w.em2` and `52.w.em3` (from `ff` as well), every program slot, and the
  date and time broadcast. A wrong source is acknowledged and not taken: only the read-back shows
  it.
- **Not while the vendor's service tool is connected** to the bus: it uses `ff` too.
- **Program slots** take four values, end first: `ebusctl write -c fs1 HCProgram1Tue1
  "18:00;Enabled;06:30;Enabled"` is Tuesday, slot 1, 06:30 to 18:00 (the field order of the
  message: `totime`, `toenabled`, `fromtime`, `fromenabled`).
- **Date and time** (`ebusctl write -c Broadcast Datetime "<outside>;<hh:mm:ss>;<dd.mm.yyyy>"`):
  send it at second 00 of the minute it carries; a late broadcast sets the installation late
  until the next one.
- **Settings to treat with care:** `ControlVariation` of the room units (while 0 was set on site,
  the heating modules raised their flow setpoint, on one circuit to its maximum); the third
  holiday registers `HolidayStartThird` and `HolidayEndThird`, whose meaning is not established;
  the settings of `15.w.ka`, which act on the whole cascade.
- **Write sparingly.** The devices keep their settings over a power cut; how many writes their
  memory bears is not known.
- **A wrong checksum** (a stock ebusd) is no safe failure: whether the system manager and the room
  units ignore it is not established, and an operator's test recorded that the heating modules
  do not check it. Do not write with a stock ebusd.

The Home Assistant integration [ha-weishaupt](https://github.com/aghulas/ha-weishaupt) does all
this for you (build check, source address, read-back, a confirmation for the settings that act
on the regulation).

## Known limits

- **One installation checked** (see the top). Other models and software versions may differ.
- **Device identification.** The files are named after the identification the devices answer to
  the scan: address, `W`, name (`15.w.ka`). A device that answers another identification gets no
  file from this folder, or the upstream Wolf file of the same address (`08..hc`, `50..mc`): its
  values are then decoded with another manufacturer's definitions. `ebusctl info` shows which file
  each address got.
- **Room unit 2 (`75.w.fs2`).** On the test installation one room unit is addressed for circuits
  1 and 2 and answers at `35` and `75`. `75` answers heating program 1 and the setback and frost
  setpoints from the store of `35`: they are read only in `75.w.fs2` and written through
  `35.w.fs1`. Its heating programs 2 and 3 and its hot-water and circulation programs are read
  only too; whether they are shared the same way is not established. A room unit at `75`
  addressed for circuit 2 alone may keep its own.
- **Two copies of each circuit setting.** A room unit and its heating module answer the same
  setting registers, sometimes with different values; which copy the regulation applies is not
  established. A change of one copy may show no effect on the heating.
- **Room-unit hot-water and circulation programs** are stored only: on the test installation hot
  water follows the system manager's program (`50.w.em1`). The program selector register (`12 01`)
  is not defined.
- **`DHWLoadingPriority`:** `0` (`Priority`) and `2` (`Parallel`) are established; `1`
  (`Sliding`) follows by elimination. Read only.
- **`DHWExcessTemp`:** which vendor parameter it is, is not established.
- **`ForcedVenting` (operating phase 9):** in no manual at hand and never seen on the bus; what the
  phase is, is not established. Its label keeps the name, not a confirmed meaning.
- **Participant at master `00` / slave `05`:** answers the scan as Kromschröder with an empty ID
  (software `0120`) and scans the bus from master `00`. What device it is, is not established
  (most likely a communication module); no file is defined for it.
- **Absent temperature sensors** read as an ordinary number (-100.0 on the system manager and the
  modules, -40.0 on the boilers), not the eBUS replacement value.
- **Memory reads (`50 00`), field `firstbyte`:** `0` in a normal answer. Rarely the boiler returns
  the number of bytes asked for in `firstbyte` and zeros for the data: when `firstbyte` is not 0,
  discard the reading.

## Content and counts

- `kromschroeder/` — one file per device address: `08.w.bc1`, `18.w.bc2` (boiler automats 1 and
  2), `15.w.ka` (system manager), `50.w.em1` (heating circuit 1, the system manager's own direct
  circuit), `51.w.em2`, `52.w.em3` (heating modules EM#2 and EM#3, circuits 2 and 3), `35.w.fs1`,
  `75.w.fs2`, `f5.w.fs3` (the room-unit addresses of circuits 1, 2 and 3), and `broadcast.csv`.
  The numbers are the vendor's circuit numbers. The folder also holds the upstream Wolf files that
  share it (the official configuration keeps Kromschröder and Wolf definitions in one folder).
- `broadcast.csv`, `memory.csv` — general files of the official configuration.
- `sha256sums.txt` — checksums of the files of the archive.

Counts, and where each comes from:

- **@COUNT@ messages** loaded by ebusd (`--checkconfig`): every read, write and passive line of the
  folder, the Wolf and general files included.
- **669 messages** in the metadata file: the Weishaupt messages by name, a read and a write line of
  the same name counting once.
- **Written: 92 settings** of `15.w.ka`, `35.w.fs1`, `75.w.fs2`, `f5.w.fs3`, `50.w.em1`,
  `51.w.em2` and `52.w.em3` (87 numbers, 5 choices), **252 program slots** (the five programs of
  `35.w.fs1` and of `f5.w.fs3`, the hot-water and circulation programs of `50.w.em1`) and the
  date and time broadcast. Each of the 92 settings was changed by one step on the test
  installation, read back with the new value and restored; for the programs, one slot of each of
  the 12 was, the others follow the same register scheme. These writes went through ebusd with
  the files loaded, which sent each telegram only after matching it to a write line of the files.
  The Home Assistant integration offers 83 of the 92: it leaves out the nine without a range,
  `ControlVariation`, `HolidayStartThird` and `HolidayEndThird` of the three room units, whose
  values have no established meaning.

The release also holds `weishaupt-metadata-@VERSION@.json` and `weishaupt-fixtures-@VERSION@.json`
for user interfaces built on these definitions (labels, menus, write conditions; captured
telegrams with their decoded values), and `sha256sums-@VERSION@.txt`. ebusd needs none of them.

## Languages

One archive per language, with the same files, message, field and circuit names, value-list
entries (e.g. `BurnerInOperation`) and units: `@BASE@.tar.gz` with English comments, the same
name ending in `-fr` with French comments. `read`, `write`, MQTT topics and automations work the
same with either. French terms follow the vendor's French manuals where they print
one.@PROVISIONAL_SENTENCE@ Wolf messages and the general files keep their English comments.

## Glossary

- **Device codes** (circuit names in ebusd, `-c`): `bc1`, `bc2` boiler automats; `ka` system
  manager; `em1` heating circuit 1 (the system manager's direct circuit), `em2`, `em3` heating
  modules; `fs1`–`fs3` room units by circuit. Elsewhere "circuit" means a heating circuit.
- **Addresses** are hexadecimal bus addresses: `08`, `15`, `35` … are devices; `ff` is the address
  of the vendor's service tool; `31` is ebusd's usual own address (option `--address`).
- **Vendor's service tool:** Weishaupt's installer software (WCM-Diagnose) with its bus interface.
- **The build** (with the run-time checksum): ebusd @EBUSD@. **Stock ebusd:** any official build.
  `[WCRC]` at the start of a comment marks a message whose checksum the build computes.
- **Telegram:** one exchange on the bus. **Slot:** one period of a weekly program (three per day).
  **Store:** the memory a device answers a value from. **Acknowledged / taken:** a device
  acknowledges every well-formed write and takes (stores) the value only from the right source.
  **Passive:** a message ebusd only listens to. **Clock master:** the device whose clock the
  others follow. **Memory read (`50 00`):** a read of the boiler automat's memory rather than of a
  register. **Replacement value:** the eBUS code for "no value", shown as `-`.

## Changes in @VERSION@

The history of every release is in `CHANGELOG.md` of https://github.com/aghulas/weishaupt-ebus.

- No message, field or type changes (@COUNT@ messages, as in 0.6.0). Names have been frozen
  since 0.6.0: they change only with a new first number.
- No longer flagged pre-release: from 0.6.1 the releases are normal releases (names frozen,
  0.6.0 running on the test installation). 1.0 remains the promise of stability.
- The label of operating phase 9 is no longer provisional: nothing is provisional any more.
- This notice is rewritten for installation: use with a plain ebusd and with the add-on, the
  write-capable build and how to check it, how to write, limits, counts, glossary.

Source: branch `weishaupt` of https://github.com/aghulas/ebusd-configuration at @COMMIT@
(TypeSpec, `src/wolf`). How each definition was established: `evidence/` of
https://github.com/aghulas/weishaupt-ebus. The definitions are proposed to the official ebusd
configuration as well; this archive lets them be used meanwhile.

## Checked with

- ebusd: @EBUSD@ and the official 26.1 (`--checkconfig`: @COUNT@ messages, no error)
- TypeSpec library: @LIB@
