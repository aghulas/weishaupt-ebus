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

Two ways. In Home Assistant, the MQTT bridge described first below, which needs nothing from this
archive. Anywhere, ebusd with the files of this archive, described after it.

What you need for the second: an eBUS adapter connected to the bus of the WCM controllers, and
ebusd (any 26.1 build both reads and writes the settings here — see "Write"; the fork build only
adds the composite-read distribution). In Home Assistant that is the add-on **eBUSd** (stock) or
**eBUSd (Weishaupt CRC)** (the fork build); either writes these settings.

The files are installed by pointing ebusd at the unpacked folder with `--configpath`. ebusd then
uses these files instead of the definitions it would fetch online: message and entity names
change for an installation that used other definitions before (MQTT topics, automations).

### Home Assistant: the MQTT bridge (recommended)

For Home Assistant the recommended way is the add-on **Weishaupt2MQTT**
([aghulas/weishaupt2mqtt](https://github.com/aghulas/weishaupt2mqtt)): one add-on with ebusd, these
definitions and a bridge that publishes the heating system as JSON on MQTT (`weishaupt/…`) and
takes guarded write commands, off by default. For MQTT alone (your own MQTT sensors, another
tool) you then need **nothing from this archive**: the add-on downloads the definitions itself
when it is built, and no `--configpath`, no `ebusctl` and no copy into an add-on folder is
involved. The same holds with the integration ha-weishaupt from its version 1.5.0 (step 5).

1. An eBUS adapter reachable over the network, and the **Mosquitto broker** add-on with the MQTT
   integration. Stop any ebusd add-on that uses the adapter.
2. In the add-on store, ⋮ → Repositories, add `https://github.com/aghulas/ha-addons#weishaupt`
   (see "Write" below for what that address is) and install **Weishaupt2MQTT**; it is built on your
   machine, which takes several minutes.
3. Set its option `ebus_device` to your adapter (ebusd's form, for example `ens:<address>:9999`)
   and start it.
4. Check: *Settings → Devices & services → MQTT → Configure → Listen to a topic*, `weishaupt/#`.
   `weishaupt/bridge/state` reads `online`, `weishaupt/bridge/info` lists the devices found, and
   one `weishaupt/<device code>/state` per device follows.
5. For entities, the panel and confirmed writes, the integration
   [ha-weishaupt](https://github.com/aghulas/ha-weishaupt), **1.5.0 or later**: *Settings →
   Devices & services → Add integration → Weishaupt → Weishaupt2MQTT (MQTT bridge)*, with the
   base topic `weishaupt`. Earlier versions cannot create their entry with the bridge alone; an
   entry that already exists against an ebusd add-on is switched from its *⋮ → Reconfigure* menu
   (1.4.0 or later). Its README, "With Weishaupt2MQTT (MQTT)", says what differs in that mode.

The bridge's README is the manual: the options, the first start, the topics, how to write a
setting or a program over MQTT, how to undo, and its own limits (read them; take the bridge
0.1.4 or later: in 0.1.3 the clock option stopped all reading and `online` did not follow the
bus). The
bundled definitions are those of the add-on's version, which may be older than this archive:
`weishaupt/bridge/info` gives `definitions_version`. Checked on the same single installation.

The rest of "Use" is the other way: ebusd alone, with these files, for use without Home Assistant
or with ebusd's own MQTT or `ebusctl`.

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

3. Start ebusd on the folder, with a scan so that each device gets its file (the scan asks every
   device for its identification), and keep your other options (adapter, MQTT, and `--address`
   if you set one):

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
   automat; ebusd prints the identification as the devices send it, `W` and a second character
   that differs): nine get a file (`08`, `18`, `15`, `50`, `51`, `52`, `35`, `75`, `f5`), three none
   (`05`, `0c`, `f6`), which is expected. `ERR: element not found` on a read means the file of
   that device was not loaded (see "Device identification" under Known limits).

### Read with the Home Assistant ebusd add-on

The steps are the same for the stock add-on "eBUSd" and for "eBUSd (Weishaupt CRC)" (see
"Write"). The add-on's `/config` is a folder of its own, `/addon_configs/<prefix>_ebusd/` on the
host (the prefix depends on the add-on repository; `ls /addon_configs/` shows it): not the
`/config` folder of Home Assistant.

**A shell inside the add-on**, for the checks below: install the add-on **Advanced SSH & Web
Terminal** (community add-ons), switch its **Protection mode** off on its own Info page, open it,
then `docker ps` shows the ebusd add-on's container (`app_<prefix>_ebusd` on the test
installation); every command below runs as `docker exec <container> <command>` (prefix both with
`sudo` if your user needs it). This is the route used on the test installation. The ebusd add-on's
own documentation also offers a terminal under **Open Web UI**; that page was not opened there.

1. Copy the unpacked folder `@NAME@` into `/addon_configs/<prefix>_ebusd/` (Samba share
   `addon_configs`, the Studio Code Server add-on, or SSH).
2. In the add-on's **Configuration**, **Additional ebusd options (one flag per entry)**, add two
   entries, each in a field of its own, and keep the others (`--mqttjson`, and `--address=…` if
   one is there):

   ```text
   --scanconfig
   --configpath=/config/@NAME@
   ```

3. Dry check, before the restart: `docker exec <container> ebusd -f --checkconfig
   --configpath=/config/@NAME@` prints `found messages: @COUNT@ (…)` and exits; it reads the
   files only and opens no adapter.
4. Restart the add-on and wait for the scan (a minute or two).
5. Check with the `ebusctl` commands of step 4 above, each as `docker exec <container> ebusctl …`,
   with the same expected answers.

Home Assistant integrations reach the add-on's ebusd by its internal host name (`<prefix>-ebusd`,
port 8888) without publishing a port. Publishing 8888 on the add-on's **Network** page opens
ebusd's command port, writes included, to your whole network.

With the MQTT integration file the add-on seeds (`mqtt-hassio.cfg`, `filter-direction = r|u`),
Home Assistant gets read-only entities; writable messages become entities only if you change
that filter (see "Write" below before enabling writes).

### Write

**The ebusd build and the checksum.** Each write telegram carries a checksum over its register and
value. The official `ebusd 26.1` does not compute it yet (john30/ebusd#1825) and sends a
placeholder; the build [@EBUSD@](https://github.com/aghulas/ebusd/releases/tag/@EBUSD@) computes
it. Every setting in the table below is on a non-boiler controller — the system manager (`ka`), the
heating modules (`em1`–`em3`) and the room units (`fs1`–`fs3`) — and these accept the placeholder
and take the value, so a stock `ebusd 26.1` writes them all end to end (established on the system
manager, a room unit and a heating module, sources `ff` and `31`; the boiler automats are never
written). The build stays useful for reads — it distributes the composite reads and
loads message IDs longer than 7 bytes — but it is not required to write the settings here. To run
it anyway (for the composite reads, or by preference):

- **Home Assistant:** in the add-on store, ⋮ → Repositories, add
  `https://github.com/aghulas/ha-addons#weishaupt`. That form is for the add-on store only: in a
  browser it opens the default branch `main`, not this add-on; the page to read is
  `https://github.com/aghulas/ha-addons/tree/weishaupt`. Install **eBUSd (Weishaupt CRC)**; it is
  built on your machine at install (there is no prebuilt image), so the install takes a while.
  If the stock eBUSd runs, stop it (one adapter, one add-on) and set the new one up as above: its
  folder, options and host name are its own, nothing carries over, so copy the definitions and
  enter the options again.
- **Plain ebusd:** the release holds two static executables, `ebusd-aarch64` (64-bit ARM) and
  `ebusd-amd64` (64-bit x86); no other machine is built for (no 32-bit ARM). They have MQTT, no
  TLS, no KNX. Check yours against its `sha256sums.txt`, make it executable (`chmod +x`), and
  start it by its own path with your usual options. Keep it apart from a packaged ebusd (for
  example `/usr/local/bin/ebusd-weishaupt`, with the service pointed at it): an update of the
  package replaces a packaged `ebusd` with the stock build. In Docker, mount it into the official
  image and start it as the entry point: `docker run --entrypoint /ebusd-weishaupt -v
  /path/to/ebusd-amd64:/ebusd-weishaupt:ro … john30/ebusd:v26.1 <your options>`.

**Which ebusd runs.** The first line of `ebusctl info` is the version of the running ebusd: the
build shows `version: ebusd 26.1.p20261120`; a stock 26.1 shows another string (for example
`26.1.26.1`). Which one you started: in Home Assistant, the add-on's Info page names **eBUSd
(Weishaupt CRC)** with a version matching `@EBUSD@`; on a plain install, the executable
you start is the one whose checksum matches the release's `sha256sums.txt`
(`sha256sum /path/to/ebusd`). The Home Assistant integration tells the two builds apart by
itself, without sending anything: the attribute `run_time_checksum` of its write switch reads
`present` with the build and `absent` with a stock ebusd.

**How to write.**

- **Before:** read the value and note it (`ebusctl read -f -c ka BlockingTime`). **After:** read it
  again with `-f` (from the device, not ebusd's cache); only that read shows that the value was
  taken. To restore, write the noted value.
- **The command** is `ebusctl write -s ff -c <circuit> <name> <value>`, with the circuit, name
  and range of the table "What can be written" below. `ebusctl find -w -c <circuit>` lists the
  writable names of a circuit, without their range.
- **Source address.** The devices acknowledge a write from any address but take most settings
  only from `ff`, the address of the vendor's service tool, hence `-s ff`. Taken from ebusd's own
  address (no `-s`): the flow limits `SupplyMaxTemp` and `SupplyMinTemp` of `51.w.em2` and
  `52.w.em3` (the column "Source" of the table) and every program slot. A wrong source is
  acknowledged and not taken: only the read-back shows it.
- **Not while the vendor's service tool is connected** to the bus: it uses `ff` too.
- **Program slots** (`ebusctl write -c <circuit> <HCProgram…> "<end>;Enabled;<start>;Enabled"`)
  take four values, end first: the field order of the message is `totime`, `toenabled`,
  `fromtime`, `fromenabled`, times in quarter hours (`06:30`, `18:00`). Written programs: the five
  of `35.w.fs1` and of `f5.w.fs3`, the hot-water and circulation programs of `50.w.em1`.
- **Date and time** (`Broadcast/Datetime`): not given here as a command. Its first field is an
  outside temperature; the clock master replaces it with its own sensor within a minute, but what
  the other controllers do with the value sent meanwhile is not established. The Home Assistant
  integration sends it, with the outside temperature the clock master last sent, at second 00 of
  the minute it carries: a late broadcast sets the installation late until the next one.
- **Settings to treat with care:** `ControlVariation` of the room units (while 0 was set on site,
  the heating modules raised their flow setpoint, on one circuit to its maximum); the third
  holiday registers `HolidayStartThird` and `HolidayEndThird`, whose meaning is not established;
  the settings of `15.w.ka`, which act on the whole cascade.
- **Write sparingly.** The devices keep their settings over a power cut; how many writes their
  memory bears is not known.
- **A stock ebusd is enough for these writes.** The system manager, the room units and the heating
  modules take a write with a placeholder checksum (established 2026-11-22/23 on `15`, `35` and
  `51`, sources `ff` and `31`), so the build's run-time checksum is not needed for them. The boiler
  automats are never written; whether one would check the checksum is untested, so do not write a
  boiler with a stock ebusd.

The MQTT bridge (see "Home Assistant: the MQTT bridge" above) and the Home Assistant integration
[ha-weishaupt](https://github.com/aghulas/ha-weishaupt) do all this for you (build check, source
address, read-back, a confirmation for the settings that act on the regulation).

### What can be written

The 92 settings by circuit and message name. *Values*: the range ebusd refuses to leave (`ERR:
argument value out of valid range`, nothing sent), or the value list (an unknown entry: `ERR:
element not found`). `*`: the range is in the metadata only (the CSV cannot carry it); ebusd does
not refuse a value outside it. `none`: no range and no established meaning (see "Settings to
treat with care"); the Home Assistant integration does not offer these nine. *Step*: the step of
the setting; ebusd does not refuse a value off the step. *Source*: `ff` = `-s ff`, `31` = ebusd's
own address. Generated from `weishaupt-metadata-@VERSION@.json` by `scripts/settings-table.py` of
the workbench.

<!-- SETTINGS-TABLE-BEGIN -->
| Circuits | Message | Values | Step | Unit | Source |
|---|---|---|---|---|---|
| ka | `BlockingTime` | 0 to 30 | 1 | min | `ff` |
| ka | `CalorifierSwitchDiff` | 1 to 20 | 0.5 | K | `ff` |
| ka | `ChangeOverTime` | 0 to 250 | 1 | h | `ff` |
| ka | `CircWithLegionella` | off, on |  |  | `ff` |
| ka | `DHWLegionellaDay` | off, Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, Sunday |  |  | `ff` |
| ka | `DHWLoadTime` | 0 to 180 | 10 | min | `ff` |
| ka, fs1, fs2, fs3 | `DHWSetpoint` | 40 to 60 | 0.5 | °C | `ff` |
| ka | `DHWSwitchDiff` | -10 to -1 | 0.5 | K | `ff` |
| ka | `DeCoupleMinTemp` | 0 to 50 | 0.5 | °C | `ff` |
| ka | `LegionellaCirculationTime` | 180 to 1200 | 60 | s | `ff` |
| ka | `LegionellaSetpoint` | 40 to 80 | 0.5 | °C | `ff` |
| ka | `ModulationMax` | 30 to 100 | 1 | % | `ff` |
| ka | `ModulationMin` | 30 to 100 | 1 | % | `ff` |
| ka | `RegulationI` | 10 to 200 | 1 |  | `ff` |
| ka | `RegulationP` | 10 to 300 | 1 |  | `ff` |
| ka, em1, fs1, fs2, fs3 | `SupplyMaxTemp` | 8 to 82 | 0.5 | °C | `ff` |
| em1, em2, em3, fs1, fs2, fs3 | `GradientCurve` | 2.5 to 40 * | 0.5 |  | `ff` |
| em1, em2, em3, fs1, fs3 | `RoomFrostProtectionTemp` | 4 to 16 | 0.5 | °C | `ff` |
| em1, em2, em3, fs1, fs2, fs3 | `RoomNormalTemp` | 16 to 35 | 0.5 | °C | `ff` |
| em1, em2, em3, fs1, fs3 | `RoomSetbackTemp` | 10 to 21.5 * | 0.5 | °C | `ff` |
| em1, em2, em3, fs1, fs2, fs3 | `SummerWinterChangeOverTemp` | 8 to 30 | 0.5 | °C | `ff` |
| em1, fs1, fs2, fs3 | `SupplyMinTemp` | 8 to 82 | 0.5 | °C | `ff` |
| em2, em3 | `SupplyMaxTemp` | 8 to 82 | 0.5 | °C | `31` |
| em2, em3 | `SupplyMinTemp` | 8 to 82 | 0.5 | °C | `31` |
| fs1, fs2, fs3 | `BoilerMCBoostTemp` | 0 to 20 | 0.5 | K | `ff` |
| fs1, fs2, fs3 | `ControlVariation` | none |  |  | `ff` |
| fs1, fs2, fs3 | `FrostProtectionLimitTemp` | -20 to 0 | 0.5 | °C | `ff` |
| fs1, fs2, fs3 | `HolidayEndDay` | 1 to 31 | 1 |  | `ff` |
| fs1, fs2, fs3 | `HolidayEndMonth` | 1 to 12 | 1 |  | `ff` |
| fs1, fs2, fs3 | `HolidayEndThird` | none |  |  | `ff` |
| fs1, fs2, fs3 | `HolidayStartDay` | 1 to 31 | 1 |  | `ff` |
| fs1, fs2, fs3 | `HolidayStartMonth` | 1 to 12 | 1 |  | `ff` |
| fs1, fs2, fs3 | `HolidayStartThird` | none |  |  | `ff` |
| fs1, fs2, fs3 | `HolidayTempLevel` | Antifreeze, Setback |  |  | `ff` |
| fs1, fs2, fs3 | `SwitchOnRuntime` | 0 to 10 | 1 | min | `ff` |
<!-- SETTINGS-TABLE-END -->

### Report a problem

On https://github.com/aghulas/weishaupt-ebus/issues, with: the release you use, the output of
`ebusctl scan result` and of `ebusctl info` (replace the adapter's address and any host name),
what you ran and what it answered. A device that answers another identification than those
above, or gets no file, is worth a report: it is how the definitions reach another installation.

## Known limits

- **One installation checked** (see the top). Other models and software versions may differ.
  Compared since with the captures another project publishes from a second installation (one
  WTC 25-A, one room unit at `35`; third-party data, not a read of this project): the room-unit
  registers it reads and the three heating programs of `35.w.fs1` decode to its own values.
- **Boiler automats: software 1104 only.** The files of the two boiler automats
  (`08.w.bc1.SW1104`, `18.w.bc2.SW1104`) were established on WTC-GB automats that answer the
  scan with software `1104`; `SW1104` in the name makes ebusd load them for that software only.
  A WTC 25-A (software `0315`) is reported to answer the memory reads of `InstallerParameters1`
  to `5` with other contents, and the registers of other software are not established. An
  automat with another software gets, at `08`, the upstream Wolf file `08..hc` (Wolf
  definitions, which decode nothing of a Weishaupt automat), at `18` no file. Renaming the file
  to drop `SW1104` loads it again, unchecked: compare each value with the boiler's display first,
  and report it (see "Report a problem"). From the vendor service tool's symbol tables (static
  analysis, no such automat read): the tool uses one memory layout for every software 11.xx of
  this automat generation; 10.xx differs in three live values of `Operation` and `FanOperation`;
  earlier versions also in the first fault counters and two temperatures; a WTC 25-A uses another
  layout altogether. Registers (`50 22`) are not covered by those tables.
- **Device identification.** The files are named after the identification the devices answer to
  the scan: address, `W`, name (`15.w.ka`), and for the boiler automats the software
  (`08.w.bc1.SW1104`). A device that answers another identification gets no
  file from this folder, or the upstream Wolf file of the same address (`08..hc`, `50..mc`): its
  values are then decoded with another manufacturer's definitions. `ebusctl info` shows which file
  each address got.
- **Room unit 2 (`75.w.fs2`).** On the test installation one room unit is addressed for circuits
  1 and 2 and answers at `35` and `75`. `75` answers heating programs 1, 2 and 3, the stored
  hot-water and circulation programs, and the setback and frost setpoints from the store of `35`:
  they are read only in `75.w.fs2` and written through `35.w.fs1`. A room unit at `75` addressed
  for circuit 2 alone may keep its own.
- **Two copies of each circuit setting.** A room unit and its heating module answer the same
  setting registers as independent stores, sometimes with different values. On the test
  installation (active-heating test on circuit 2), the regulation loop follows the room-unit
  (`fs`) copy, while changing the heating-module (`em`) copy does not move the flow setpoint.
- **Room-unit hot-water and circulation programs** are stored only: on the test installation hot
  water follows the system manager's program (`50.w.em1`). The program selector register (`12 01`)
  is not defined.
- **`DHWLoadingPriority`:** `0` (`Priority`) and `2` (`Parallel`) are established; `1`
  (`Sliding`) follows by elimination. Read only.
- **`DHWExcessTemp`:** which vendor parameter it is, is not established.
- **`ForcedVenting` (operating phase 9):** never seen on the bus. The name is the phase 9 of the
  oil boiler WTC-OB (its manual, 83314005); a WTC-GB lists phases 0 to 8 only, and a WTC 15-A …
  32-A uses 9 for its post-purge.
- **Participant at master `00` / slave `05`:** answers the scan as Kromschröder with an empty ID
  (software `0120`) and scans the bus from master `00`. On the test installation it is the bus
  interface of the vendor's service tool, left connected (its version registers hold the version
  the tool displays for its interface); it is not a part of the heating system and no file is
  defined for it.
- **Absent temperature sensors** read as an ordinary number (-100.0 on the system manager and the
  modules, -40.0 on the boilers), not the eBUS replacement value.
- **Memory reads (`50 00`), field `firstbyte`:** `0` in a normal answer. Rarely the boiler returns
  the number of bytes asked for in `firstbyte` and zeros for the data: when `firstbyte` is not 0,
  discard the reading.

## Content and counts

- `kromschroeder/` — one file per device address: `08.w.bc1.SW1104`, `18.w.bc2.SW1104` (boiler
  automats 1 and 2, software 1104), `15.w.ka` (system manager), `50.w.em1` (heating circuit 1, the system manager's own direct
  circuit), `51.w.em2`, `52.w.em3` (heating modules EM#2 and EM#3, circuits 2 and 3), `35.w.fs1`,
  `75.w.fs2`, `f5.w.fs3` (the room-unit addresses of circuits 1, 2 and 3), and `broadcast.csv`.
  The numbers are the vendor's circuit numbers. The folder also holds the upstream Wolf files that
  share it (the official configuration keeps Kromschröder and Wolf definitions in one folder).
- `broadcast.csv`, `memory.csv` — general files of the official configuration.
- `sha256sums.txt` — checksums of the files of the archive.

Counts, and where each comes from:

- **@COUNT@ messages** loaded by ebusd (`--checkconfig`): every read, write and passive line of the
  folder, the Wolf and general files included.
- **@META_COUNT@ messages** in the metadata file: the Weishaupt messages by name, a read and a write line of
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
- **Register:** a numbered value inside a device that ebusd reads (`50 22`) or writes (`50 23`); a
  setting is one register. **Scan:** ebusd asks each device for its identification and, with
  `--scanconfig`, loads the file named after it. **Master / slave:** a device that sends
  requests on the bus (ebusd at `31`, the tool at `ff`) / one that answers them (`08`, `15` …).
  **Wolf file:** a file of the official configuration for Wolf devices, which share the folder.
- **Protection mode:** a switch on the Info page of a Home Assistant add-on; off, the add-on may
  run `docker` commands. **MQTT integration file** (`mqtt-hassio.cfg`): tells ebusd which values to
  publish as Home Assistant entities; its `filter-direction` says reads only or writes too.
- **Telegram:** one exchange on the bus. **Slot:** one period of a weekly program (three per day).
  **Store:** the memory a device answers a value from. **Acknowledged / taken:** a device
  acknowledges every well-formed write and takes (stores) the value only from the right source.
  **Passive:** a message ebusd only listens to. **Clock master:** the device whose clock the
  others follow. **Memory read (`50 00`):** a read of the boiler automat's memory rather than of a
  register. **Replacement value:** the eBUS code for "no value", shown as `-`.

## Changes in @VERSION@

The history of every release is in
[`CHANGELOG.md`](https://github.com/aghulas/weishaupt-ebus/blob/main/CHANGELOG.md).

- Compatible release on top of `1.3.2`, no breaking change (@COUNT@ messages, @META_COUNT@ in
  metadata; circuit, message and field names, types and IDs unchanged).
- **Boiler automat files renamed** `08.w.bc1.SW1104` and `18.w.bc2.SW1104` (contents unchanged):
  ebusd loads them only for an automat that answers the scan with software `1104`, the software
  they were established on. Until 1.3.2 a boiler automat with another software at `08` / `18` got
  them too and was read with the memory layout of another firmware; it now gets the upstream Wolf
  file `08..hc` at `08` and no file at `18` (see *Known limits*). On an installation with software
  `1104` nothing changes but the file names `ebusctl info` shows; the metadata file names them in
  `devices.<device>.circuits[].file`.

Source: branch `weishaupt` of https://github.com/aghulas/ebusd-configuration at @COMMIT@
(TypeSpec, `src/wolf`). How each definition was established:
[`evidence/`](https://github.com/aghulas/weishaupt-ebus/tree/main/evidence) of the workbench. The definitions are proposed to the official ebusd
configuration as well; this archive lets them be used meanwhile.

## Checked with

- ebusd: @EBUSD@ and the official 26.1 (`--checkconfig`: @COUNT@ messages, no error)
- TypeSpec library: @LIB@
