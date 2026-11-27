# Second installation — comparison with the captures published in `turbolooser/ebus2mqtt`

## What

A comparison, made offline on 2026-11-27, of the definitions on `weishaupt` (fork of
`ebusd-configuration`, commit `84fe069`) with the telegrams and raw values an independent project
publishes from another installation. It covers the room-unit registers (`50 22` at `35`), the
weekly programs, the status broadcast `50 0a`, the heat demand `05 07`, the check byte and the
write format `50 23`, and lists what that project reads that this one does not.

**This is third-party data, not a bus read of this project.** By rule 3 of `AGENTS.md` it can
confirm or question a definition that exists; it adds none. Nothing here was sent on any bus, and
the code and images of the other project were not run.

## Source

Repository [turbolooser/ebus2mqtt](https://github.com/turbolooser/ebus2mqtt) (GPL-3.0), commit
`d377209ff7b4d06ef0102d6fff090c22e6ad6bc1` of 2026-11-27. Its captures are of 2026-11-23, one
later reading of 2026-11-27. Files read:

| File | Holds |
|---|---|
| `tools/ebusd_inject_test.py` | nine telegrams "as in the capture", request and answer |
| `tests/test_wandlung.py` | raw values "as ebusd delivers them" per register and display slot, one broadcast |
| `tests/daten/wcm-werte-2026-11-23T1500.tsv` | the 58 values the vendor's network gateway gave at 15:00 the same day, as text |
| `tests/daten/wcm-discovery-2026-11-23.json` | names, bounds and value lists the gateway bridge announces |
| `ebus2mqtt/katalog.py`, `schreiben.py`, `quellen.py`, `wandler.py`, `daten/maps.json` | sources per value, conversions, value lists, comments quoting telegrams |
| `ebusd/csv/wtc25.csv`, `wtca-eeprom.csv` | its ebusd definitions: 53 display slots, 89 registers, two passive telegrams, five memory blocks |

Two kinds of data, marked in the tables below: **T**, a telegram published byte for byte; **N**, a
raw value published as a number, from which the telegram was rebuilt here (request = the ID of our
definition, answer = the value, low byte first). The text values of the gateway are a second,
independent reading of the same registers by a vendor device.

Its register numbers ("infoNr") are the register numbers of `register-candidates.csv`: number
= address, low byte first on the bus (270 = `0e 01`).

## Equipment

- There: one Weishaupt WTC 25-A gas condensing boiler, automat Kromschröder `W 0315 / 0301`
  (master `03`, slave `08`), one WCM-FS room unit (master `30`, slave `35`), the vendor's network
  gateway as master `ff`, ebusd as `31`. No system manager, no heating module. A master `f1`
  sends the status broadcast.
- Here: two WTC-GB boilers in cascade (`08`, `18`), a WCM-KA system manager (`15`, `f6`, own
  circuit `50`), WCM-EM heating modules (`51`, `52`), WCM-FS 2.0 room units (`35` / `75`, `f5`).

## How it was compared

- **ebusd**: `scripts/check.sh`'s method for fixtures. The definitions were compiled
  (`tsp compile src/main.tsp`, emitter `@ebusd/ebus-typespec`), loaded in ebusd
  `v26.1-weishaupt.2` without a bus (Docker, `--scanconfig=off -d /dev/null --inject=stop`), each
  telegram injected and read back (`read -m 1000 -v -c <circuit> <message>`, `find -w -e -d -v`
  for a write). The value in the tables is the one ebusd printed.
- **script**: the check-byte routine of `scripts/register-survey.py` (`crc`), run on their bytes.
- **reading**: definitions read side by side, where they publish no value.

## 1. Room unit registers, `50 22` at `35`

All by **ebusd**, circuit `fs1`. "Gateway" is the text of the 15:00 table.

| Their number, name | Kind | Request / answer | Our message | ebusd prints | Gateway | Agrees? | Note |
|---|---|---|---|---|---|---|---|
| 4, flow setpoint (416) | N | `2c 04 00` / `c5 01` | `SupplyHCSetTemp` | 45.3 | 45.3 | yes | signed, tenths, both |
| 5, normal room temperature (413) | T | `70 05 00` / `c3 00` | `RoomNormalTemp` | 19.5 | 19.5 | yes | |
| 8, setback room temperature (113) | N | `58 08 00` / `c3 00` | `RoomSetbackTemp` | 19.5 | 19.5 | yes | |
| 12, outside temperature (i33) | N | `74 0c 00` / `1e 00` | `OutsideTemp` | 3.0 | 3 | yes | signed, tenths, both |
| 270, slope (117) | N | `cd 0e 01` / `6e 00` | `GradientCurve` | 11.0 | 11.0 | yes | no unit, both (they removed the gateway's °C) |
| 278, summer / winter changeover | N | `25 16 01` / `a0 00` | `SummerWinterChangeOverTemp` | 16.0 | 16.0 | yes | bounds differ, see below |
| 317, "frost protection temperature" | N | `a5 3d 01` / `00 00` | `HolidayTempLevel` | Antifreeze | 0.0 | **no** | same register, another meaning, see below |
| 321, control variant | N | `25 41 01` / `01 00` | `ControlVariation` | 1 | Witterungsführung | value yes | our message has no value list |
| 2419, "floor warming" | N | `19 73 09` / `02 00` | `HeatingCircuitType` | Radiator60 | 2 | value yes | their name is the first entry of our list |
| 2572, outside temperature, damped (i12) | N | `7e 0c 0a` / `1e 00` | `OutsideWeightedTemp` | 3.0 | 3 | yes | |
| 2572, reading of 2026-11-27 02:27 | N | `7e 0c 0a` / `ff ff` | `OutsideWeightedTemp` | -0.1 | – | yes | they read `ff ff` as -0.1 too; their unsigned ebusd type printed `-`, our signed one does not |
| 2580, room frost protection (118) | N | `96 14 0a` / `64 00` | `RoomFrostProtectionTemp` | 10.0 | 10.0 | yes | |
| 2586, outside temperature, mixed (412) | N | `5a 1a 0a` / `1e 00` | `OutsideMixedTemp` | 3.0 | 3.0 | yes | |

Thirteen readings of twelve registers: twelve readings agree on the value (for two of them ebusd
prints another text than the gateway: a number without list, a list entry for a number), one
register differs in meaning.

- **317 (`3d 01`)**. They take the name and the conversion (a temperature in tenths) from the
  gateway bridge; the only value seen is 0. Our definition is a choice of two levels (vendor
  parameter 142, holiday level, in `register-candidates.csv`), written and read back here
  (`choice-date-program-writes.md`). A frost protection temperature of 0.0 °C beside a room frost protection
  of 10.0 °C (register 2580) is not plausible; nothing here questions `HolidayTempLevel`. A value
  1 on their side would read 0.1 °C with their conversion.
- **321 (`41 01`)**. Their list, from the gateway bridge: 0 constant flow, 1 weather, 2 weather
  with room influence, 3 room. `register-candidates.csv` has the same four in the same order from
  the vendor tool; the room-unit manual lists the menu in another order
  (`room-units-control-variation.md`). Two sources for 2 and 3 now, no bus proof of either; the
  message stays without a list.
- **278 (`16 01`)**. The gateway bridge announces -4 to 30 °C; our range is 8 to 30 °C, unsigned,
  from the vendor tool (parameter 124; parameter 119 of the same register is signed there). No
  negative value was read or written on either bus: their -4 is a bound of the bridge and a unit
  test, not a capture.
- **5 and 8**: the bridge gives no bound; their own write guard uses 10 to 30 °C. Ours: 16 to 35
  for the normal setpoint, none for the setback. Not comparable.
- **2 (`02 00`)**, which they poll as an unnamed candidate, is our `HeatDemandTemp`.

### Registers they read at `35` that `35.w.fs1` does not define

| Their number, name | Kind | Request / answer | Known here as | Note |
|---|---|---|---|---|
| 1, fault code | N | `5c 01 00` / `00 00` | `ErrorStatus` of `15.w.ka` (prints 0, **ebusd**); "fault", room unit, in `register-candidates.csv` | their value list is the boiler's fault list |
| 274, operating mode (111) | T | `09 12 01` / `0d 00` | the program selector `12 01` of `docs/discoveries.md`, not defined | see below |
| 306, reduced operation (501) | N | `35 32 01` / `01 00` | `32 01`, one of the pair `28 01` / `32 01` of `register-survey-findings.md`, not defined | their list: 0 frost, 1 setback |
| 290–294, day, month, year, hour, minute | N | `85 22 01` / `17 00`, `d9 23 01` / `0b 00`, `11 24 01` / `1a 00`, `4d 25 01` / `0e 00`, `a9 26 01` / `38 00` | `SystemDay` … `SystemMinute` of `50.w.em1` (same registers at `50`) | with those definitions **ebusd** prints 23, November, 26, 14, 56 = gateway `23.11.2026`, `14:56` |

- **274 (`12 01`)**: the answer `0d 00` = 13 was read while the gateway showed "Programm-3", and
  the bridge's list is 1 standby, 3 normal, 4 setback, 5 summer, 11 / 12 / 13 program 1 / 2 / 3,
  255 as the control centre. Here the register reads 11 on the three room units and 11 was shown
  to select program 1 (`modules-programs.md`); 12 and 13 were not proven. Their reading is a
  second installation with 13 and a vendor device naming it program 3.
- **306 (`32 01`)**: parameter 501 in the bridge and in `register-candidates.csv` (reduced
  operation, 0 frost protection, 1 setback). It supports `32 01`, not `28 01`, as the register of
  that parameter.

## 2. Weekly programs, registers 5136 to 5746

**ebusd**, circuit `fs1`, 63 registers (three programs × seven days × three windows). Published as
raw values per window (N), the same for every day; the first window of Monday of program 1 also
as a telegram (T, `a4 10 14` / `34 18`). Their numbering equals ours: 5136 = `10 14`, day in the
high nibble of the low byte, window in the low nibble, program in the high byte (`14`, `15`,
`16`).

| Program | Their raw windows | Answers | Our messages | ebusd prints | Gateway | Agrees? |
|---|---|---|---|---|---|---|
| 1 | `0x1834`, `0x3c58`, `0x8080` | `34 18`, `58 3c`, `80 80` | `HCProgram1<Day>1`–`3` | 06:00–13:00, 15:00–22:00, disabled | 06:00–13:00, 15:00–22:00 | yes, 21 registers |
| 2 | `0x1836`, `0x3c5c`, `0x8080` | `36 18`, `5c 3c`, `80 80` | `HCProgram2<Day>1`–`3` | 06:00–13:30, 15:00–23:00, disabled | 06:00–13:30, 15:00–23:00 | yes, 21 registers |
| 3 | `0x185a`, `0x8080`, `0x8080` | `5a 18`, `80 80`, `80 80` | `HCProgram3<Day>1`–`3` | 06:00–22:30, disabled, disabled | 06:00–22:30 | yes, 21 registers |

Same coding on both sides: first byte the end, second byte the start, in quarter hours, `80` in
a byte for an unused window. The 21 day programs rebuilt from ebusd's output equal the 21 texts
of the gateway.

## 3. Status broadcast `50 0a` from `f1`

**ebusd**, `KaStatus` of `broadcast`. Three samples: T1 quoted in `katalog.py` (burner on,
14:13), T2 in `tests/test_wandlung.py` (burner starting), T3 in a test double of
`tests/test_bruecke.py` (burner off).

```
T1  f1 fe 50 0a 0d  01 06 7f 52 22 52 ff ff 00 03 02 03 2d
T2  f1 fe 50 0a 0d  01 13 47 12 51 4a ff ff 00 03 02 03 2d
T3  f1 fe 50 0a 0d  01 00 47 12 00 4e ff ff 00 03 02 03 2d
```

| Field (byte) | T1 | T2 | T3 | Their reading | Agrees? |
|---|---|---|---|---|---|
| `operatingphase` (1) | BurnerInOperation | 19 | BurnerOff | operating phase; 0, 6, 8, 19 seen | yes; 19 is not in our list, ebusd prints the number |
| `flame` (2, `08`) | on | off | off | flame (candidate) | yes |
| `gasvalve1` (2, `10`) | on | off | off | gas valve (candidate) | yes |
| `gasvalve2` (2, `20`) | on | off | off | not read | – |
| `pump` (2, `40`) | on | on | on | pump (candidate); gateway said on with the flame off | yes |
| `ukn2_1`–`ukn2_3` (2, `07`) | 1 1 1 | 1 1 1 | 1 1 1 | not read | – ; 0 in both captures here |
| `burnerstatus` (3, `02`) | on | on | on | not read | **questions the name**: on with the burner off |
| `ukn3_5` (3, `10`) | 1 | 1 | 1 | not read | – |
| `circpump` (3, `40`) | on | off | off | "burner demand, heating" (candidate): `12` off, `52` with a demand | **no**, another name for the same bit |
| `load` (4) | 34 | 81 | 0 | load in % (= i11) | yes |
| `supplytemp` (5) | 41.0 | 37.0 | 39.0 | flow temperature, half degrees; gateway 37 at T2 | yes |
| `fluegastemp` (6) | - | - | - | not read; their flue gas temperature (39 °C) comes from a display slot | not shown: `ff` there as in both captures here |
| `dhwtemp` (7) | - | - | - | not read (no hot water on that boiler) | – |
| `outsidetemp` (8–9) | 3.000 | 3.000 | 3.000 | "constant so far" | yes with their register 12 (3.0) |
| `outsideweightedtemp` (10–11) | 3.008 | 3.008 | 3.008 | "constant so far" | yes with their register 2572 (3.0) |
| `supplysettemp` (12) | 45 | 45 | 45 | "constant so far" | plausible: their register 4 reads 45.3, their boiler demand slot 41 |

The layout holds on a boiler of another series: phase, load, flow temperature, flame, gas valve
and pump are their readings too, and bytes 8 to 12, which they leave unread, decode to their own
outside temperatures. Three things differ or stay open:

- **Bit `40` of byte 3**: `circpump` here, a burner demand for them. Both are assignments by
  observation; neither side has a proof.
- **Bit `02` of byte 3** (`burnerstatus`) is set in all three samples, burner off included; here
  byte 3 was `80` and `00` with the burner off (`broadcast-kastatus.md`).
- **Phase 19** exists (burner starting, before the flame). Our list ends at 9; the gateway bridge
  names 17 to 22 "unassigned".

**Who sends it.** There `f1` broadcasts without a system manager on the bus; their catalogue
calls `f1` the burner control. Here the slave side of `f1`, `f6`, identifies with the software of
the system manager (`docs/ebus-protocol.md`, section 1), and `broadcast-kastatus.md` calls `f1`
"the master address of the system manager's cascade function". Both fit one reading: `f1` / `f6`
is the address of the heat generation manager, held by the boiler itself when it is alone and by
the system manager when there is one. That is an inference; their repository has no
identification answer of `f6`. For the naming: the message name `KaStatus` and its comment
("boiler status broadcast by the WTC") stand for both installations; the sentence of
`broadcast-kastatus.md` and the row of `docs/ebus-protocol.md` that tie `f1` to the system
manager describe this installation only.

## 4. Heat demand `05 07` from `30` to `f1`

**Reading** only: they define the telegram as nine undecoded bytes and publish no sample. The
pair is the one of our `PowerDemand` in `35.w.fs1` (`30` → `f1`), nine bytes, and their comment
gives the standard layout (state, action, boiler setpoint in sixteenths, pressure, setting
degree, hot-water setpoint, fuel) with the same byte split as ours (1, 1, 2, 2, 1, 1, 1). So the
room unit sends its demand to `f1` on an installation without a cascade manager; the comment of
our message ("heat demand of the room unit to the cascade manager") is narrower than the bus.
No value could be compared.

## 5. Check byte and write format

| What | Method | Result |
|---|---|---|
| the 89 `50 22` IDs of `wtc25.csv` (among them `96 14 0a`, `cd 0e 01`, `a4 10 14`) | script | 89 of 89 equal our check byte |
| two more IDs from their capture: 19 `54 13 00` (our `DHWSetpoint`), 650 `12 8a 02` (DHW setback, `register-candidates.csv`) | script | equal |
| write `35 50 23 05 f8 05 00 c8 00`, sent there from `31` at 17:40:12 (T) | script, **ebusd** | check byte over address and value equal; `RoomNormalTemp` = 20.0 |
| write `35 50 23 05 44 05 00 c3 00` (N, a test value) | script, **ebusd** | equal; `RoomNormalTemp` = 19.5 |
| the five `50 00` IDs of `wtca-eeprom.csv` (`df b2 1b` … `ab 62 4b 02 44 02 37`) | script | equal; they are the IDs of our `InstallerParameters1`–`5` |

The write of 17:40 was acknowledged by their room unit and not taken from `31`; they write the
room unit only as `ff`. Same rule as here (`docs/ebus-protocol.md`, "The source address
decides"). They tested one register (the normal room temperature); that the program windows need
`ff` there is their extension, not a test. Here the program windows are taken from `31`.

## 6. What they read that we do not

### Display slots of the boiler: `50 03` (read) and `50 04` (write)

Read `08 50 03 01 <slot>`, answer six bytes for a slot below `80` (type, value, two slot
numbers, two more bytes), five for a slot from `80` on (type, 16-bit value low byte first, two
slot numbers). Five telegrams are published:

```
31 08 50 03 01 1e  /  06 36 29 17 1f 08 08      P30 = 41
31 08 50 03 01 14  /  06 37 ff 11 15 fc fc      P20 = -1
31 08 50 03 01 2a  /  06 35 3c 29 2b 14 14      P42 = 60
31 08 50 03 01 aa  /  05 60 e6 01 29 2b         i42 = 486
31 08 50 03 01 8c  /  05 b6 03 00 0b 0d         slot 8c = 3
```

Their slot table (WTC 25-A), all marked proven against the display unless noted:

| Slots | Content |
|---|---|
| `0b`–`0e`, `0f`, `11`, `12` | P10, P11, P12, P13, P15, P17, P18 |
| `14`–`17` | P20, P21, P22 (× 0.5), P23 |
| `1e`–`25`, `27`–`2b` | P30 to P37, P39 (× 0.1), P40, P41, P42, P43 |
| `46`, `48` | P70, P72 (× 0.1) |
| `8b`, `8d` | i11 load, i13 heat demand |
| `9e`, `9f` | i30 flow temperature, i31 flue gas temperature |
| `aa`, `ab`, `ad` | i42 burner starts (× 1000), i43 burner hours (× 100 h), i45 time since service (× 10 h) |
| `8c`, `a0`, `a1` and sixteen more from `8a` to `ae` | open (candidates) |

Seen in that table, not stated by them: the slot is the parameter number from P15 on (`1e` = 30,
`2b` = 43, `46` = 70) and `80` + the number for the information values (`8b` = i11, `aa` = i42);
`a1`, which they found to follow the outside temperature, would be i33 and `8c` i12. In the three
one-byte examples the last two bytes equal the lower bound of the parameter (8, -4, 20).

The parameter numbers are those of the WTC 15/25-A, not of the WTC-GB: P42 / P43 are the minimum
and maximum pump rating there (P44 / P45 here, where P42 is the hot-water pump run-on). The
vendor tool's lists for the earlier automat forms have the same numbering as theirs
(`register-candidates.csv`, "min. pump output" as P42 for four forms).

Write `03 50 04 02 <slot> <value>`, master to master, no check byte, taken there from `31`
(P30, P31, P42, P43, each read back on the slot). Not tested here and not to be (rule 7).

### Memory layout of the WTC 25-A (`50 00`)

They read our five `InstallerParameters` blocks and name two bytes: `0x20` = P42 and `0x21` =
P43 (60 and 70, as on the display, after a write also 70). On the WTC-GB these two bytes are
inside the five bytes `InstallerParameters1` skips, and our `PumpLoadMin` / `PumpLoadMax` are at
`0x31` / `0x32`. The block bytes themselves are not published, so nothing else of the layout
(for example whether `0x1b` / `0x1c` are P31 / P30 there too) could be checked.

### Candidate registers at `35`

Numbers the gateway bridge reads on the boiler and they try on the room unit; no value is
published for any of them.

| Their number | Address | Known here? |
|---|---|---|
| 2 | `02 00` | yes: `HeatDemandTemp` (`35.w.fs1`) |
| 82 | `52 00` | yes: mixer circuit pump, `MixerPump` of `51.w.em2` / `52.w.em3`; not defined on the room unit |
| 81 | `51 00` | no: neither in the definitions nor in `register-candidates.csv` |
| 373 | `75 01` | no |
| 466 | `d2 01` | no |
| 1497 | `d9 05` | no |
| 2419, 2572, 2586 | `73 09`, `0c 0a`, `1a 0a` | yes, defined (section 1); 2572 is not in `register-candidates.csv` |

## 7. Data given by its author on request (2026-11-27)

Asked on aghulas/weishaupt-ebus#1 for what the repository does not hold, the author of that
project answered the same day. Third-party data as the rest; decoded here by hand calculation,
not through ebusd.

**Identification.** Scan result of the WTC 25-A bus: slave `08` answers `Kromschroeder`, `W`,
software `0315`, hardware `0301`; slave `f6` answers `Kromschroeder`, `WWST1`, software `0315`,
hardware `0301` (`f6 07 04 00` → `0a 50 57 57 53 54 31 03 15 03 01`). Masters seen: `03`, `30`,
`f1`, and ebusd. The room unit `35` is listed without an identification.

So on that bus `f1` / `f6` carries the software and hardware versions of the boiler automat
itself, under another identification (`WWST1`). Here `f6` answers with the software of the
system manager. This supports the reading of section 3: the address of the heat generation
manager, held by the boiler when it is alone and by the system manager when there is one. Two
installations, still an observation.

**Heat demand.** One raw telegram, `30 f1 05 07 09 bb ff ce 02 00 80 ff ff ff`, CRC `d0`,
acknowledged. With the layout of `PowerDemand` (`heat-demand.md`): status `bb` (requesting),
second byte `ff`, requested temperature `ce 02` = 718 / 16 = 44.9 °C, `00 80` no value,
modulation `ff`, hot-water setpoint `ff`, last byte `ff`. Same length, same split, and the
values a room unit sends here (`bb`, `ff` in the second and eighth bytes).

**Memory read.** Request `31 08 50 00 03 df b2 1b`, answer `0d 00 82 51 51 99 83 3c 46 60 14 ff
04 00`: first byte `00`, then 12 bytes of EEPROM from `0x1b`. The requests `e3 b2 27`, `f7 b2 33`
and `fb b2 3f` were answered too. The four check bytes are those of the routine of
`docs/ebus-protocol.md` (section 3) over the two bytes that follow.

| Address | WTC 25-A | Reading there | WTC-GB here (`bc-installer-parameters.md`) |
|---|---|---|---|
| `0x1b` | `82` | not assigned | `50`, maximum flow temperature 80 °C |
| `0x20` | `3c` | pump rating minimum, 60 % (their P42) | `0a`, a byte of `InstallerParameters1` with no field |
| `0x21` | `46` | pump rating maximum, 70 % (their P43) | `02`, a byte of `InstallerParameters1` with no field |

The request of `InstallerParameters1` is accepted and answered with the same shape; the bytes
mean something else. The definitions of the boiler memory hold for the WTC-GB only.

**A wrong check byte on a memory read.** The author also sent `a8 b2 1b` once (the value a
CRC-8 that folds the byte in before shifting gives) and got no answer (read timeout); he had not
isolated the cause. If it is the check byte, the automat of a WTC 25-A checks it on a `50 00`
read, where the system manager, room units and heating modules here take a `50 23` with a wrong
one (`write-methods.md`). One attempt, not repeated: an indication for open question 2 of
`docs/ebus-protocol.md`, not an answer.

## What this changes

**Confirmed on a second installation** (another boiler series, a room unit of the same family,
the vendor gateway as a second reader): the check byte on 91 register IDs and two writes; the
address, type and factor of nine room-unit registers (`SupplyHCSetTemp`, `RoomNormalTemp`,
`RoomSetbackTemp`, `OutsideTemp`, `GradientCurve`, `SummerWinterChangeOverTemp`,
`OutsideWeightedTemp`, `RoomFrostProtectionTemp`, `OutsideMixedTemp`); the address of
`ControlVariation` and `HeatingCircuitType`; the 63 program registers of `35.w.fs1` and their
window coding; the layout of `KaStatus` for phase, load, flow temperature, flame, first gas
valve, pump and the two outside temperatures; the pair `30` → `f1` of `PowerDemand`; "acknowledged
is not taken" for a `50 23` from `31`.

**Differs or is questioned** (no definition is changed by this record):

- `KaStatus` (`src/wolf/wtc_inc.tsp`): the names `burnerstatus` (set with the burner off) and
  `circpump` (a burner demand for them); `fluegastemp` shows `ff` on both installations and has
  no reading behind it; the phase list lacks 19.
- `PowerDemand` of `35.w.fs1`, `75.w.fs2`, `f5.w.fs3`: the comment names the cascade manager as
  receiver; `f1` exists without one. The same for the row of `f1` in `docs/ebus-protocol.md`
  and the paragraph on the source address in `broadcast-kastatus.md`.
- `InstallerParameters1`–`5` of `08.w.bc1` / `18.w.bc2`: the request is accepted by a WTC 25-A
  but the bytes mean something else there (`0x20` / `0x21` pump rating). The notice should say
  these five messages hold for the WTC-GB only (already in `docs/discoveries.md`). Done later
  the same day by limiting both boiler files to scanned software `1104`
  ([bc-automat-software.md](bc-automat-software.md)).
- `HolidayTempLevel`: they read the register as a temperature; our reading stands.
- `SummerWinterChangeOverTemp`: a lower bound of -4 °C in the gateway bridge against our 8 °C,
  unsigned.

**Unknown to us**: the services `50 03` and `50 04`; registers 81, 373, 466, 1497; on the room
unit the fault register 1, the date and time registers 290 to 294, the operating mode 274 with
its value list and the reduced operation 306, which are known here by number or on another
device but not defined in `35.w.fs1`.

**For a read-only probe here, once the adapter is back** (nothing is written; one request, then
compare, stop at the first refusal or odd answer, as for the memory areas in
`docs/ebus-protocol.md`, section 6):

1. `50 03` on both automats. There is no Weishaupt check byte in this service; the last byte
   below is the eBUS telegram CRC for source `31`, which ebusd adds itself
   (`hex 08500301<slot>`, `hex 18500301<slot>`; ebusd also escapes the byte `aa`).

   | Slot | Expected content | To `08` | To `18` | Compare with |
   |---|---|---|---|---|
   | `1e` | P30 | `31 08 50 03 01 1e 73` | `31 18 50 03 01 1e 9a` | `InstallerParameters1` `supplymintemp` |
   | `1f` | P31 | `31 08 50 03 01 1f 72` | `31 18 50 03 01 1f 9b` | `InstallerParameters1` `supplymaxtemp` |
   | `2a` | P42 | `31 08 50 03 01 2a 47` | `31 18 50 03 01 2a ae` | `InstallerParameters4` `pumprunondhw` (P42 of the WTC-GB) |
   | `2b` | P43 | `31 08 50 03 01 2b 46` | `31 18 50 03 01 2b af` | no byte established (`docs/discoveries.md`) |
   | `8b` | i11 | `31 08 50 03 01 8b e6` | `31 18 50 03 01 8b 0f` | burner load of `Operation` |
   | `9e` | i30 | `31 08 50 03 01 9e f3` | `31 18 50 03 01 9e 1a` | `SupplyTemp` (i35 here) |
   | `9f` | i31 | `31 08 50 03 01 9f f2` | `31 18 50 03 01 9f 1b` | `FlueGasTemp` (i31 here too) |
   | `aa` | i42 | `31 08 50 03 01 aa c7` | `31 18 50 03 01 aa 2e` | burner starts / 1000 of `Counters` |

   Start with `1e` on one boiler. If the service answers, the slots of the parameters left out
   of `InstallerParameters*` (P20, P23, P32, P34, P40, P43 and the others of
   `docs/discoveries.md`) are the next reads: the display value without knowing its byte.
2. On the room unit `35`, registers already known by number: 274 `09 12 01` (expected 11), 306
   `35 32 01`, 1 `5c 01 00`, and the clock 290 to 294 (`85 22 01`, `d9 23 01`, `11 24 01`,
   `4d 25 01`, `a9 26 01`), to see whether the room unit holds a date and time of its own.
3. The four registers unknown here, on `35`: 81 `94 51 00`, 373 `85 75 01`, 466 `81 d2 01`,
   1497 `39 d9 05`.
4. `KaStatus` over a burner start: byte 1 (a phase above 9) and bit `02` of byte 3 against the
   burner state.
5. With the same visit, the display looks for the vendor codes still open, items 7 to 11 of
   `docs/owner-checklist-room-units.md` (items 8 to 11 with a bus read at the same minute).

## Date

Their captures: 2026-11-23 (one reading 2026-11-27). Comparison: 2026-11-27.

## Not verified

- Everything in this record about the other installation rests on what its repository
  publishes. The rebuilt telegrams (N) carry their numbers, not their bytes.
- The repository publishes no telegram `05 07` and no memory block; one of each came from its
  author afterwards (section 7) and was decoded by hand, not through ebusd.
- Whether the WTC-GB automats answer `50 03`, and with the same slot numbers.
- Whether the automat of the WTC 25-A checks the check byte of a `50 00` read: one unanswered
  request, cause not isolated (section 7).
- Their slot and register candidates carry no values; their own 24-hour comparison is not in the
  repository.
