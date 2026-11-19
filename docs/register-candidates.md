# Register candidates from the vendor software

The catalogue of every value the vendor's diagnosis program knows how to read, recovered from
its files without running it ([evidence/vendor-software-analysis.md](../evidence/vendor-software-analysis.md)).
Data: [evidence/register-candidates.csv](../evidence/register-candidates.csv), 2 023 rows.

**These are candidates, not definitions.** A row says what the program would read and how it
would show it. It enters a lot only with a record of its own (rule 3): a bus read that agrees
with a display, a manual page, or a capture of the tool reading it.

## Reading the file

| Column | Content |
|---|---|
| `device` | device type, by the form of the program that shows it |
| `access` | `register` (a 16-bit number, read with `50 22`) or `memory` (a firmware symbol, read with `50 00`) |
| `firmware` | for memory rows, the symbol file the address was taken from (`WH11928` only) |
| `register`, `bus_bytes` | the number, and its two bytes as sent (`321`, `41 01`) |
| `area`, `address`, `mask` | for memory rows: RAM, XRAM or EEPROM, the address, the EEPROM address of a parameter in brackets, the bit mask |
| `vendor_param` | the vendor's number (`315`, `P31`, `A10`, `S22`, `I43`, `F3 6`) when the caption carries one |
| `type`, `factor`, `offset` | how the program converts: shown value = raw × factor + offset |
| `unit`, `min`, `max`, `range_note` | as the program shows and checks them; a range note may name another parameter as a bound |
| `values` | the value list, in our words; index = value |
| `special` | a raw value shown as a text ("sensor not fitted") |
| `meaning` | our short description of the caption; for memory rows the symbol name follows in brackets |
| `level` | display, user, installer or manufacturer, from the tab the field is on |
| `read_at` | `unit` or `module` (the address is a variable of the program), or an address written in the program (`0x70` is the master address of the second room unit, `0xf1` that of the system manager) |
| `status` | `defined`, `on-installation`, `not-on-installation` |
| `defined_as` | for `defined`: the message of release 0.5.13 that reads the same register or address |

`defined` compares with the compiled files of 0.5.13 (`15.w.ka`, the `fs`, `em` and `bc`
files): the same register number in a file of the same device group, or a memory address
covered by a read of `bc1` / `bc2`. It does not say that type, factor and value list agree; that
comparison is worth doing line by line when a lot is touched. `on-installation` means the
device type is on the test installation and the value is not defined: a bus read can confirm
it. Weekly programs are one row per block.

## Counts

Rows, and distinct registers or symbols in brackets (a register shown on two tabs, or with
two parameter numbers for two circuits, has several rows).

| Device type | Defined in 0.5.13 | On the installation, not defined | Not on the installation |
|---|---|---|---|
| System manager | 40 (27) | 69 (43) | |
| Room unit FS 2.0 with its heating and hot-water modules | 39 (29) | 104 (74) | |
| Boiler automat of the R5 generation (the installed boilers) | 41 (41) | 137 (107) | |
| Room unit, earlier form | | | 122 (93) |
| Remote control FB with module | | | 50 (50) |
| Solar controller | | | 83 (71) |
| Oil condensing boiler | | | 90 (89) |
| Oil boiler automat | | | 234 (182) |
| Gas boiler automats of five earlier generations | | | 1 014 (778) |
| **Total** | **120** | **310** | **1 593** |

## What it settles, and what it does not

| Open question | From the vendor software | Status |
|---|---|---|
| `ControlVariation` (`41 01`), values 2 and 3 | Parameter 315 (316 for a second circuit) is register 321 shown through a list of four entries, index = value: 0 constant flow temperature, 1 weather-compensated, **2 weather-compensated with room influence, 3 room-controlled**. | Settled as far as the tool goes; one read on a unit set to 2 or 3 confirms it. |
| Third register of the holiday dates (`1d 01`, `20 01`) | Registers 285 and 288 feed the third box of the start and of the end date; the boxes are named "year". Their list is filled while the program runs, with only "none" at index 0. | It is the **year**; how a year is encoded is not in the files (step B of batch G still gives it). |
| Room unit 2 keeps no program write: P312, P335 | The field captioned P335 on the configuration tab is register 16 (`10 00`) of the room unit, a list: 1 external room sensor, 2 internal room sensor, 4 unit mounted in the boiler (0 and 3 unused). P312, the address of the unit, has no register in the tool: the tool takes it from the bus address. The tool knows no lock or protection parameter for programs; it writes them as plain registers. | Not settled. New leads: read `10 00` and the operating mode `12 01` on the three units; value 14 of the mode is "as the master unit". |
| Program selector `12 01` | Register 274. A list of the form named after parameter 111, indexed by the raw value: 1 standby, 3 normal, 4 setback, 5 summer, **11 program 1, 12 program 2, 13 program 3, 14 as the master unit**; for hot water (parameter 131): 0 standby, 3 normal, 4 setback, 11 program, 12 as the master unit. On the system manager: 0 service, 1 standby, 5 summer, 11 automatic, 20 boiler standby. | Agrees with the one proven value (11). The tie between list and register is by name, not traced in code. |
| Operating phase 9, `ForcedVenting` | The program shows the phase as a number (I10) and holds no list of phases, in forms, strings or channel file. | Not settled; stays provisional. |
| Register `27 02` of the boilers | The tool reads the boilers through memory, never through registers, so it names none of them. The file shipped upstream for another make at address `08` names the neighbours: `26 02` burner starts, `28 02` hours with mains on, `2a 02` burner hours. | Supports "starts / 256" (the register next to the start counter of the sister product); not proof. |
| System manager `e9 fd` = parameter 538 | Parameter 538 is register 65001 (`e9 fd`), tenths, 5 to 20 K, a shut-down differential. | Settled as far as the tool goes (the value read on the bus, 10.0, is in range). |
| Register 13 (`0d 00`) and B24 (`40 0a`) | Shown as hydraulic separator / plate exchanger secondary B22 and primary B24, signed tenths, -40.0 shown as "no sensor". | Agrees with the service-tool log. |
| Sign and "not fitted" values | Temperatures of the system manager and room units are signed 16-bit in tenths; -40.0 or -100.0 are replaced by dashes. | A hint for the metadata gap noted in `docs/discoveries.md`. |
| Register `99 01` read by master `07` | Registers 409 and 410 are read without a display field on the room-unit and system-manager forms; 410 answered the software version on a boiler in the service-tool log. | 409 / 410 are identification registers; nothing to define. |

## Boiler parameters: three sources that agree

The tool reads the installer parameters of an automat from EEPROM. The block captured from
boiler A on 2026-11-16 ([service-tool-log.md](../evidence/service-tool-log.md)), decoded with
the types, masks and factors of the catalogue, gives the value of each parameter on that
boiler. The read-only survey ([register-survey-findings.md](../evidence/register-survey-findings.md),
boiler `08`) gives the registers that answer. The file shipped upstream for another make of
the same controller family at address `08` (`08..hc` of the release, not part of our
definitions and not evidence for Weishaupt) names some of these registers.

| Parameter | EEPROM | Value on boiler A | Answering register with that value | Upstream name of that register (other make) |
|---|---|---|---|---|
| P10 device type | `0x4e` | 85 | `00 00`, `5b 01` (85) | |
| P12 boiler address | `0x4c` | 1 (A) | `78 01` (1) | eBUS address |
| P23 system frost protection | `0x42`, mask `1f`, offset -4 | 5 °C | `fd 01` (5.0 if tenths; 50 would be A33, pump output at pre-purge) | |
| P30 minimum flow temperature | `0x1c` | 8 °C | `1f 00` (8.0) | boiler minimum temperature |
| P31 maximum flow temperature | `0x1b` | 80 °C | `27 00` (80.0) | boiler maximum temperature |
| P32 switching differential | `0x1d`, two nibbles | 4 K | `22 00` (4.0) | flow temperature hysteresis |
| P33 flue gas cut-out temperature | `0x29` | 120 °C | `11 02` (120.0) | |
| P34 burner anti-cycling time | `0x1e` | 0 min | `43 01` (0) | anti-cycling time |
| P35 ignition load | `0x26` | 37 % | `09 02` (37) | |
| P36 minimum boiler load | `0x2d` | 23 % | `5a 01` (23.0) | lower fan speed |
| P37 maximum load, heating | `0x2f` | 100 % | `3f 01` (100.0) | upper fan speed, heating |
| P38 maximum load, hot water | `0x3f` | 100 % | `59 01` (100.0) | upper fan speed, hot water |
| P41 pump overrun, heating | `0x38`, mask `7f` | 1 min | `42 01` (1) | heating pump overrun |
| P42 pump overrun, hot water | `0x41` | 3 min | `7f 01` (3) | |
| P44 minimum pump output | `0x31` | 50 % | `55 01` (50) | minimum pump output |
| P45 maximum pump output | `0x32` | 100 % | `56 01` (100) | maximum pump output |
| P46 pump output, hot water | `0x40` | 100 % | `57 01` (100) | |
| P48 temperature difference B12/B13 | `0x35` | 20 K | `e2 01` (20.0) | |
| P50 boost for hot-water charging | `0x3c` | 10 K | `2d 00` (10.0 if tenths) | |
| P70 service interval | `0x24` | 4000 h | none | |

Eleven registers are named the same way by two independent sources and carry the value the
third predicts. This is still a match by value on one boiler, with the burner off. Pass 2 of
the survey on boiler B tests it: the EEPROM of B differs from A at `0x4c` (2 instead of 1) and
at `0x4e` (`45` instead of `55`), so **`78 01` should read 2 on `18`, and `00 00` / `5b 01`
should read 69 if they are P10**. The other registers of the table should read the same on both.

Also from the upstream file, for registers that answered and have no parameter: `02 00` flow
setpoint, `03 00` hot-water setpoint, `6d 01` pump PWM, `70 01` ionisation value, `2a 02` burner
hours (the last equal to the lot D counter, as the survey record says).

Answering registers of `08` that nothing names: `01 00`, `51 00`–`53 00`, `8a 00`, `5d 01`,
`60 01`, `6f 01`, `75 01`–`77 01`, `d2 01`, `e1 01`, `0d 02`, `19 02`–`1d 02`, `27 02`. For
`01 00`, `52 00` and `53 00` the tool's lists for other device types use the same numbers
(fault code, mixer circuit pump, charging pump).

The survey of the system manager had just started when this was written (a few dozen registers read);
its answers can be matched with the 70 registers of the catalogue's system manager rows by
number, without any guess by value.

## What is new for the installation

Without listing the file: the vendor's numbers for the settings already defined (for example
112 / 113 room temperatures, 117 slope, 119 changeover, 421 / 422 flow limits, 502 frost
limit), and, not defined yet:

- **System manager**: outputs and inputs (`f2 fd`, `8e 0a`, `f0 fd`, `28 0a`) and their
  functions 521 to 525, cascade sequence and change-over (531, 532, sequence registers
  `ca fd` …), modulation limits 535 / 536, lock time 537, controller terms 539 / 540, hydraulic
  separator and buffer settings 551 to 562, hot-water settings 571 to 582, daylight-saving
  dates 593 / 594, control voltage and current, buffer temperatures.
- **Room units and modules**: process values (room and flow setpoints, pumps, mixer, H1
  input), heating-circuit type 313, H1 function 401 / 402, hot-water operation 423, mixer and
  pump settings 425 to 431, screed drying 441 to 451, reduced operation 501, building
  construction 504, room thermostat function 505, adaptation 507, room influence 508,
  hot-water and legionella settings 601 to 611, configuration (pump kind, P335).
- **Boilers**: every installer parameter P10 to P71 and the plant parameters A1 to A33 with
  EEPROM address, mask, factor and range; manufacturer parameters S0 to S64; the 32 fault
  counters by code (already read as a block); process values in RAM (speed setpoint and actual,
  fan PWM, anti-cycling timer, inputs and outputs by bit).

## Worth doing at the tool, after this

Read-only steps at the PC, each with ebusd grabbing as in `docs/service-tool-protocol.md`:

1. **Check the program file first.** The loose copy of the executable in the vendor folder is
   damaged in three places; compare the SHA-256 of the installed executable with the intact one
   (`4311729a…6db29fba`) and reinstall from the installer if it differs. Then reopen the two
   boiler tabs that stayed empty (statistics, process values).
2. **System manager, installer tabs**: opening them makes the tool read every register of the
   catalogue's rows in one go; the grab gives number, address read and raw value for some
   forty candidates at once, against what the screen shows.
3. **Room unit windows of units 1 and 2**, configuration and user tabs: P335, the versions, the
   operating mode; the grab shows which registers the tool reads at the unit and which at its
   module (the `read_at` column is a variable in the code).
4. **Value lists**: on the installer tabs of a room unit, note the entry shown for 313, 315, 401,
   423, 429, 441, 501 to 508 next to the raw value grabbed.
5. **Holiday year**: with a holiday period set on a unit, the third box of parameter 141 in the
   tool, against registers `1d 01` and `20 01`.
6. **The adapter**: the serial capture described in the analysis record, if the owner wants to
   know whether ebusd could use it.

## Date

2026-11-19.
