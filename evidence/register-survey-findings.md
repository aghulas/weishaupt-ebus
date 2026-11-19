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

## Date

2026-11-19.
