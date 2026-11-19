# Register survey — findings (pass 1, from 2026-11-19)

Results of the read-only survey of [register-survey-plan.md](register-survey-plan.md), matched
with the manuals. **Nothing here is a definition**: each row says what a register most likely
is, how sure that is, and what would confirm it. Results file: `out/register-survey-pass1-results.csv`
(installation data, not versioned); this record quotes registers and values only.

Codecs tried on each answer `lo hi`: unsigned (`UIN`), signed tenths (`SIN/10`, as the
temperatures and differences of this family), and the low byte alone (`UCH`).

## Chunk 1 — boiler automat `08`, registers 0x0000–0x01e6 (2026-11-19, 17:38 to 18:20)

480 single-register requests, all answered, no error, burner off throughout. 446 registers
answered `00 80` (not available); 34 answered something else.

**Sources for the match.** The parameter list of the boiler manual (WTC-GB 120–300-A, document
83251704, pages 48 to 51: P10 to P71 with ranges and factory settings) and the vendor service
tool's screen of boiler A ([service-tool-log.md](service-tool-log.md), 15:51), which showed
**P31 = 80 °C, P30 = 8 °C, P70 = 4000 h** on this boiler, a WTC 250 (factory P31 = 79 °C; P35
ignition speed 37 %, P36 minimum load 23 % for the WTC 250). Both boilers are WTC 250 (window
titles of the tool), so a factory value is expected equal on both; a value an installer changed
may differ.

| Register | Answer | Read as | Likely | Confidence | What confirms it |
|---|---|---|---|---|---|
| `27 00` (0x0027) | `20 03` | 80.0 (SIN/10) | **P31 maximum flow temperature, 80 °C** | medium-high: equals the tool's screen, and 80 is not the factory 79 | pass 2 on `18`; P31 on the display of each boiler |
| `02 00`, `03 00`, `1f 00` | `50 00` each | 8.0 (SIN/10) | one of them **P30 minimum flow temperature, 8 °C**; the others possibly current setpoints at their minimum (burner off) | medium for "one is P30", low for which | re-read while the burner fires: a setpoint moves, P30 does not |
| `22 00` | `28 00` | 4.0 | P32 flow temperature differential, 4 K (factory) | low: 4 is also P49 and other factory values | the display of both boilers if one differs; pass 2 |
| `2d 00` | `64 00` | 10.0 | P50 hot-water boost 10 K, or P41 pump overrun 10 min (both factory 10) | low | display |
| `5a 01` (0x015a) | `e6 00` | 230 → 23.0 % in tenths | P36 minimum load, 23 % (factory of the WTC 250) | medium: an unusual value matching the model | pass 2 (expected 230 on `18`, the same model); display |
| `56 01`, `57 01` | `64 00` each | 100 | P37 maximum heating load and P38 maximum hot-water load, 100 % (factory) | low-medium: a pair, as P37 / P38; also P45 / P46 are 100 | display; a pair that differs on `18` |
| `3f 01`, `59 01` | `e8 03` each | 1000 → 100.0 in tenths | a percentage at 100 % in tenths (P37, P38, P45 or P46 family) | low | as above |
| `55 01` | `32 00` | 50 → 5.0 | P23 frost protection 5 °C (SIN/10) or P34 short-cycle lock 5 min (×10) | low | display |
| `5b 01`, `00 00` | `55 00` | 85, or 8.5 | 85 °C is the upper bound of P31 in the manual (85 °C − P32); not a parameter | low | — |
| `5d 01` | `04 00` | 4 | P32 4 K, P49 4 s, or P43 | low | display |
| `e1 01`, `e2 01` | `04 00`, `c8 00` | 4; 200 → 20.0 | a pair: P49 control inertia 4 s and P48 temperature difference 20 K (factory 4 and 20) | low-medium: two factory values side by side | display |
| `7f 01` | `03 00` | 3 | P42 hot-water pump overrun 3 min (factory), or P14 output MFA2 = 3, or P47 3 K | low | display |
| `78 01`, `42 01` | `01 00` | 1 | a switch at 1: P71 eBUS supply, P43 pump mode, P16 input H1 (all factory 1) | low | display |
| `76 01` | `0e 00` | 14 | none of the parameter list fits; a count or a code | none | pass 2; a second read later |
| `01 00`, `51 00`–`53 00`, `8a 00`, `43 01`, `60 01`, `6d 01`, `6f 01`, `70 01`, `75 01`, `77 01`, `d2 01` | `00 00` | 0 | parameters or states at 0 (P17, P20, P40 are 0 by factory) | none from one read | a read while the burner fires, pass 2 |

Reading of chunk 1:

- The boiler answers in the register space only a few dozen registers out of 480; most read
  0x8000. The answering ones cluster at 0x0000–0x002d and 0x013f–0x017f, with a pair at
  0x01e1–0x01e2: the shape of a settings block, as on the system manager (0x01xx).
- One match is strong: **`27 00` = P31 = 80 °C**, the value the service tool showed and not the
  factory value. Most of the others are factory values that occur several times in the list
  (4, 10, 100, 1, 3), so a single read cannot tell them apart.
- The register numbers do not follow the P-numbers, nor the EEPROM addresses the service tool
  read for the same parameters (P31 at EEPROM `0x1b`, P30 at `0x1c`).

**What would settle most of them at once.** The owner reads P10 to P71 on the display of both
boilers (installer level of the WTC, parameter menu, read only) and notes the values. Every
parameter whose value differs from its factory setting, or between the two boilers, then
points to one register; pass 2 on `18` gives the second boiler's registers. A read of the
0x0000–0x002d block while a burner fires separates live setpoints from settings.

## Chunk 2 — boiler `08`, registers 0x01e7–0x03ff (2026-11-19, until 18:51)

480 requests: 475 answered, 5 failed with "SYN received" (seq 816, 821, 823, 835, 837:
registers `38 03`, `3d 03`, `3f 03`, `4b 03`, `4d 03`), sent again one by one in pass 2. Burner
off throughout. Eleven registers answered other than `00 80`, all below 0x022b:

| Register | Answer | Read as | Likely | Confidence | What confirms it |
|---|---|---|---|---|---|
| `09 02` (0x0209) | `25 00` | 37 | **P35 ignition speed, 37 %** (factory of the WTC 250, a value no other parameter has) | medium-high | pass 2 on `18`; display |
| `11 02` (0x0211) | `b0 04` | 120.0 (SIN/10) | **P33 flue-gas safety temperature, 120 °C** (factory; range 80–120 °C) | medium | display; pass 2 |
| `2a 02` | `e5 4e` | 20 197 | burner operating hours (info value i43): equal to the burner hours lot D reads from EEPROM (20 197 h) | high; left out of the lots on purpose as a duplicate | — |
| `27 02` | `db 02` | 731 | burner starts / 256, as recorded in [bc-info-values.md](bc-info-values.md) | as there | the step at 187 392 starts |
| `fd 01` | `32 00` | 50 or 5.0 | as `55 01`: P23 (5 °C) or P34 (5 min) | low | display |
| `0d 02` | `16 00` | 22 or 2.2 | none from the list (22 % is P36 of other models) | none | pass 2 |
| `19 02`–`1d 02` | `00 02` / `01 02` | 512 / 513 | five neighbouring values `0x0200` / `0x0201`: a block of states or a version pair, not a parameter | none | a second read later; pass 2 |

**The boiler automat in the catalogue.** The vendor-software catalogue
([register-candidates.csv](register-candidates.csv), [docs/register-candidates.md](../docs/register-candidates.md))
lists the boiler automat of this generation by memory address only (`50 00` reads, 137 rows on
the installation and not defined), not by register. So none of the 45 boiler registers that
answer has a catalogue row; their matches above rest on the boiler manual and the service tool's
screen alone.

## Chunk 3 — boiler `08` (end) and system manager `15` (2026-11-19, until 19:22)

480 requests, all answered: the last 55 registers of `08` (nothing but `00 80`), then 425
four-register requests to `15`, registers 0x0000–0x0ac7 (1 700 registers). Burner off
throughout. 56 registers of `15` answered other than `00 80`.

### Crossed with the catalogue

Generated with `scripts/survey-crosscheck.py out/register-survey-pass1-results.csv`. Of the 69
catalogue rows of the system manager that are on the installation and not defined (43 distinct
registers), 20 rows are surveyed: 18 answer within the catalogue's type and range, 2 answer
`00 80`; 49 rows are not surveyed yet (beyond 0x0ac7). The room unit and heating-module rows
(104) wait for chunks 5 and 6.

| Register | Catalogue (type, factor, unit, range) | Answer | Status |
|---|---|---|---|
| `40 0a` (2624) | plate exchanger primary B24, SIN ×0.1 °C | `51 02` = 59.3 °C | **ready**: the same register was read before as B24 and its value used in the manager's demand formula ([heat-demand.md](heat-demand.md)); bus read, catalogue and that record agree |
| `81 01` (385) | DHW maximum (vendor 353 / 574), UIN ×0.1 °C, 8–80 | `58 02` = 60.0 °C | plausible (60 °C is the factory DHW maximum of the room unit's list, P601); needs the system manager's own manual or display |
| `8a 02` (650) | DHW setback setpoint (573), UIN ×0.1 °C, 8–80 | `50 00` = 8.0 °C | plausible (the lowest value); needs a second source |
| `12 01` (274) | operating mode switch, UIN | `0b 00` = 11 | the register `discoveries.md` calls the program selector (11 on `15`); catalogue and finding agree on the register, not yet on the meaning of 11; needs the value list |
| `76 00`, `78 00` (118, 120) | buffer temperature top, bottom, SIN ×0.1 °C | `18 fc` = −100.0 | the "sensor not fitted" value ([ka-reads.md](ka-reads.md) read them so, as calorifier registers); definable with `absent = -100.0`, but no fitted value is seen here: needs the manual's sensor names (B10, B11) |
| `a9 01`, `aa 01` (425, 426) | control voltage V, control current mA, UIN ×0.1 | `00 00` | 0 only (the analogue input is not used); needs a second source |
| `28 0a` (2600), `8e 0a` (2702) | input H1, output MFA 2 | `00 00` | 0 only; needs a second source |
| `0b 00` (11) | read by the program logic, no display | `0a 01` = 266 | 266 is the software version of the system manager (the tool's title "KA 266.18"), and master `07` reads the same 266 from `99 01` of `50` and `f6`: a version register |
| `33 01`, `35 01` (307, 309) | DHW minimum (352), DHW variant (571) | `00 80` | not available on this system manager |

Registers of `15` that answer and have no catalogue row (45): `16 00` `18 fc`; `51 00`, `53 00`,
`64 00`, `67 00`, `6f 00`, `72 00`, `ff 00` `00 00`; `58 00`, `59 00`, `63 00` `01 00`; `68 00`
`41 20` (the identification bytes `41 20` that `15` answers to the scan); `09 01`, `0d 01`,
`15 01`, `1d 01`, `20 01`, `3d 01`, `44 01` `00 00`; `0f 01` `05 00`; `10 01` `08 00`; `13 01`
`02 00`; `17 01` `c8 00` (20.0); `1b 01`, `1c 01`, `1e 01`, `1f 01`, `28 01`, `32 01`, `48 01`
`01 00`; `46 01` `57 00`; `47 01` `50 00`; `f1 01` `00 00`; `f2 01` `45 00`; `a2 02` `01 00`;
`be 02` `0a 00`; `70 09`, `71 09` `ff 00`; `72 09` `0a 00`; `0d 0a`, `23 0a` `00 00`; `0e 0a`
`ee 00`; `0f 0a` `03 00`; `11 0a` `01 00`; `1c 0a` `0a 00`. Several are registers the room units
define (`1b 01`–`20 01` holiday dates, `3d 01`, `be 02`), answering on the system manager too.

### Ready for a lot, and what still needs a second source

- **Ready with the survey read as evidence**: `40 0a` B24 of the system manager (bus read,
  catalogue meaning, and an earlier record that used its value). One register.
- **Needs a second source** (manual page, display value, or a value that moves as expected):
  `81 01`, `8a 02`, `12 01` (value list), `76 00` / `78 00` (no fitted sensor), `a9 01`,
  `aa 01`, `28 0a`, `8e 0a`, `0b 00`. The boiler registers of chunks 1 and 2 likewise (the owner's
  reading of P10–P71 on both displays settles most of them).
- A catalogue row alone is never evidence (rule 3).

## Chunk 4 — system manager `15` (end) and heating module `51` (2026-11-19, until 19:52)

480 requests, all answered, burner off throughout: 202 four-register requests to `15`
(registers 0x0ac9–0xfdff, 808 registers, 31 answering other than `00 80`) and 278 to `51`
(0x0000–0x0960, 1 112 registers, 74 answering).

- **`15`**: the answering registers are the `0xfd` block of the cascade and hot-water settings
  (`ca fd`–`d8 fd` boiler sequences, `de fd`–`e1 fd` summer time, `e3 fd`–`e9 fd` excesses and
  limits, `a4 fd`–`f3 fd` input and output functions, `f4 fd` legionella time), `f1 13`,
  `f2 13`, and `ae 0b` / `af 0b` (3 and 0). With chunk 3, every catalogue register of the system
  manager is now surveyed: of its 69 on-installation rows, 65 answer within the catalogue's type
  and range, 4 answer `00 80`.
- **`51`**: 15 of its 21 catalogue rows answer within range (the other 6 lie outside the pass-1
  ranges and are in pass 2). Among the 74 answering registers: a copy of the clock at
  `21 01`–`27 01` (4, 19, 11, 26, 19, 43, 57: Thursday 19.11.26, 19:43:57, the time of the read);
  `29 01` = 75.0 and `2a 01` = 45.0, the normal and reduced flow setpoints already read on the
  modules ([heating-modules-reads.md](heating-modules-reads.md)), equal to the factory values of
  parameters 121 / 122 in the room unit's manual (83277504, page 32); `8f 01` = 8.0 (mixer
  parameter, below); the version `99 01` / `9a 01` = 372, 3 (the tool's "372.03"); `81 01` = 60.0
  and `8a 02` = 40.0 (hot-water maximum and reduced setpoint as on the manager, values of the
  room unit's list P601 60, P133 40); `40 01` = −3.0 (the factory hot-water switching difference
  P602, −3 K). Not matched yet: the rest.

## The service tool's screens against the survey

The tool's screens of 19:03–19:15 ([service-tool-ui-exploration.md](service-tool-ui-exploration.md),
"Registers without a definition") give label, unit, factor and the tool's own answer; the survey
read the same registers independently, from ebusd's address `31`, 20 to 50 minutes later. A
register counts as **two sources** when the tool's screen gives its meaning by a value (or a pair
of values) and the survey reads the same value on the same device.

| Device | Register | Tool: label, value | Survey (`31`) | Agrees |
|---|---|---|---|---|
| `15` | `e9 fd` (65001) | P538 continuous temperature, 10,0 °C | `64 00` = 100 | yes |
| `15` | `e8 fd` (65000) | P551 de-couple excess, 6,0 K | `3c 00` = 60 | yes |
| `15` | `e6 fd` (64998) | P553 de-couple maximum, 78,0 °C | `0c 03` = 780 | yes |
| `15` | `e3 fd` (64995) | P561 calorifier excess, 1,0 K | `0a 00` = 10 | yes |
| `15` | `de fd`, `df fd` (64990, 64991) | P593 start of summer time, 29 March | 29, 3 | yes |
| `15` | `e0 fd`, `e1 fd` (64992, 64993) | P594 end of summer time, 25 October | 25, 10 | yes |
| `15` | `ca fd`, `cb fd` (64970, 64971) | P533 boiler sequence 1, a, b (0, 1) | 0, 1 | yes |
| `15` | `d4 fd`, `d5 fd` (64980, 64981) | P534 boiler sequence 2, b, a (1, 0) | 1, 0 | yes |
| `15` | `8a 02` (650) | P573 DHW reduced setpoint, 8,0 °C | `50 00` = 80 | yes |
| `15` | `f4 fd` (65012) | P581 legionella time, 08:30 = 34 quarter hours | `22 00` = 34 | yes |
| `15` | `81 01` (385) | P574 DHW maximum, 60,0 °C (by elimination) | 600 | yes, meaning by elimination |
| `15` | `f2 13` (5106) | P578 maximum load during DHW, 100 % (by elimination) | 100 | yes, meaning by elimination |
| `15` | `f1 13` (5105) | solar recovery with legionella, off (by elimination) | 0 | yes, meaning by elimination |
| `15` | `a4 fd`, `c2 fd`, `ed fd`, `ef fd`, `f1 fd`, `f3 fd` | functions of MFA 1, MFA 2, VA, H1, N1, sequence change (2, 0, 2, 3, 1, 3, order not assigned) | 2, 0, 2, 3, 1, 3 | values yes, assignment no |
| `15` | `ee fd` (65006) | P525 special level, no value | `00 80` | yes (no value) |
| `15` | `76 00`, `78 00` (118, 120) | buffer top, bottom, "--" (no sensor) | `18 fc` | yes (no sensor) |
| `15` | `12 01` (274) | type of operation, "automatic" / "(0) Prog 1" | 11 | value yes, text mapping no |
| `15` | `35 01` (309) | DHW variation, no value | `00 80` | yes (no value) |
| `35` | `12 00` (18) | room setpoint, 8,0 °C (14,0 °C on `f5`) | `50 00` = 80 | yes |
| `35` | `28 01`, `32 01` (296, 306) | one is P381 reducing operation, "reduce" (1) | 1, 1 | values yes, which one no |
| `35` | `1a 01` (282) | one of P370 / P371 / P331 (0) | 0 | values yes, which one no |
| `35` | `81 00`, `29 01`, `2a 01`, `0f 01`, `15 01`, `2f 01`, `30 01` | no value | `00 80` | yes (no value on the room unit) |
| `51` | `8f 01` (399) | P365 mixer parameter, 8.0 (the only register left for the field) | `50 00` = 80 | yes, meaning by elimination |
| `51` | `52 00`, `56 00`, `57 00`, `85 02`, `29 0a` | read by the tool on `52`: pump 1, mixer 0, 0, PWM 0, H1 0 | on `51`: 0, 0, 0, 0, 1 | other device; pass 2 reads `52` |
| `35` | `1a 0a`, `73 09`, `de fd`–`e1 fd`, `3b 01`, `af 06`, `71 09`, `1c 0a`, `14 06`, `5b 0a`, `bb 01`, `bc 01`, `00 0a`, `12 0a`, `1f 0c`, `21 0c` | various | not surveyed yet | chunks 5 and 6, or pass 2 |
| `51` | `fb fd`, `ae 06` | module configuration; engineer tab | not surveyed yet | pass 2 |

Two registers have a second, earlier independent read as well: `1a 0a` of the room units read
14.6 on 2026-11-17 ([room-units-reads.md](room-units-reads.md), `OutsideBlendedTemp`), and
`73 09` read 2 / 3 / 3 on the three room units in the preparation of batch C.

## Burner starts: the developer window, lot D and `27 02`

The developer window of the second build displayed **`EEA_N_ZUE` = 187 277** on automat A
from the EEPROM bytes `8d db 02` at `0x01eb` (19:19). That is the counter lot D reads
(`BurnerStarts`, 187 277 in ebusd's cache at 13:47 and 15:17 the same day: no start in between),
and the register `27 02` answered `db 02` (731) in the survey: **the two upper bytes of that
counter, `db 02`, exactly**. So `27 02` is a 16-bit register mapped on EEPROM `0x01ec`–`0x01ed`,
the upper two bytes of the burner-start counter (starts / 256), now established by the tool's
display and two independent reads. It stays undefined: lot D reads the full counter.

The same tab shows six counters no lot reads, with the tool's display as their only source:
`EEA_HBRONTAG` (`0x01d8`, 0), `EEA_NZUENDTAG` (`0x01d9`, 0), `EEA_N_PON` (`0x01da`, 3 bytes,
221), `EEA_N_KON` (`0x01dd`, 4), `EEA_RES_CNT` (`0x01e0`, 1 471), `EEA_SHUT_OFF` (`0x01e3`, 1).
An independent read is one memory request per boiler (below, pass 2).

## Ready for a lot (proposed names for the owner)

Reads only, stock ebusd, two sources each (the tool's screen and the survey, or the survey and
an earlier record). Proposed as **a new lot of reads**, below L and M like N, one commit per
device type; names to approve:

| Device, file | Register | Proposed name | Type | From |
|---|---|---|---|---|
| system manager `15.w.ka` | `e9 fd` | `ContinuousTemp` (parameter 538) | temp10 | screen + survey |
| | `e8 fd` | `DeCoupleExcessTemp` (551) | diff10 | screen + survey |
| | `e6 fd` | `DeCoupleMaxTemp` (553) | temp10 | screen + survey |
| | `e3 fd` | `CalorifierExcessTemp` (561) | diff10 | screen + survey |
| | `de fd`, `df fd`, `e0 fd`, `e1 fd` | `SummerTimeStartDay`, `SummerTimeStartMonth`, `SummerTimeEndDay`, `SummerTimeEndMonth` (593, 594) | UIN | screen + survey |
| | `ca fd`, `cb fd`, `d4 fd`, `d5 fd` | `BoilerSequence1First`, `BoilerSequence1Second`, `BoilerSequence2First`, `BoilerSequence2Second` (533, 534; 0 = boiler a, 1 = boiler b) | value list | screen (pair) + survey |
| | `8a 02` | `DHWSetbackTemp` (573) | temp10 | screen + survey |
| | `f4 fd` | `LegionellaStartTime` (581, quarter hours) | UIN, 34 = 08:30 | screen + survey |
| | `40 0a` | `PlateExchangerPrimaryTemp` (sensor B24) | otemp10 | survey + catalogue + [heat-demand.md](heat-demand.md) |
| room units `35`, `75`, `f5` | `12 00` | `RoomSetpointTemp` (current room setpoint) | temp10 | screen (8,0 / 14,0 on two units) + survey |
| | `1a 0a` | `OutsideMixedTemp` | otemp10 | screen + read of 2026-11-17 |
| | `73 09` | `HeatingCircuitType` (2 radiators 60 °C, 3 radiators 70 / 75 °C), read only | value list | screen (three units) + earlier reads |

Note: `e6 fd` is the de-couple maximum whose write of 78.5 was not taken (`docs/discoveries.md`);
the read is defined here, the write stays out. `ca fd`–`d5 fd` are the boiler sequences batch C
left read only; reading them is what the owner kept.

**Still lacking a source** (one source only, or the meaning by elimination):
`81 01`, `f2 13`, `f1 13` (meaning by elimination); `8f 01` on the modules (elimination);
the six function registers (values agree, assignment not established); `12 01` (text of 11);
`28 01` / `32 01` and `1a 01` (which of two or three fields); `76 00`, `78 00` (no fitted sensor);
`a9 01`, `aa 01`, `28 0a`, `8e 0a`, `0b 00`, `68 00`; the module registers read by the tool on
`52` (pass 2); the boiler parameters of chunks 1 and 2 (the owner's reading of P10–P71); the
six boiler counters of the developer window (pass 2, memory read).

## Pass 2, as now generated

`scripts/register-survey.py <csv-dir> pass2 out/register-survey-pass1-results.csv` now also
sends the five failed requests of `08` again, one register each, and adds on every device of a
type the catalogue's on-installation registers that the pass-1 ranges miss: 6 for the heating
modules (`a9 04`, `e9 04`, `ae 06`, `1f 0c`, `fb fd`), 20 for the room units (legionella
`87 05`, WTC delay `14 06`, solar yield `ae 06`–`b1 06`, the floor-drying registers `9c 08`–`a2 08`,
`1f 0c`, `21 0c`, daylight saving `de fd`–`e1 fd`, legionella start `f4 fd`). None for the system
manager (all its catalogue registers lie inside its pass-1 ranges). Rows the catalogue reads at a
master address (`0x70`, `0x4c`, `0xf1`) are left out: they are not slave registers. The full
pass 2 is generated once pass 1 has ended.

Two memory reads join pass 2 by hand, one per boiler, for the six counters of the developer
window (14 EEPROM bytes from `0x01d8`, the checksum computed as for lot D's `Counters`, checked:
lot D's `06 01 72 e6` gives `26`):

```
hex 08500005d40601d2d8
hex 18500005d40601d2d8
```

Expected on `08`: a first byte 0, then `00 00 dd 00 00 04 00 00 bf 05 00 01 00 00` if nothing
changed since 19:19. Every register of the tool's table is covered by pass 1 (chunks 5, 6) or by
the catalogue additions of pass 2; none needed adding.

## Date

2026-11-19.
