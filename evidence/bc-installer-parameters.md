# bc1, bc2 — heating-specialist parameters of the boiler automat (read)

## What

Messages `InstallerParameters1` to `InstallerParameters5` on both boilers (`08.w.bc1`,
`18.w.bc2`): the parameters of the heating-specialist level (boiler manual WTC-GB 120–300-A,
document 83251704, parameter list P10 to P71, pages 48 to 51), read only, with the five memory
reads (`PBSB 50 00`, EEPROM `0x1b` to `0x51`) the vendor service tool sends when it shows its
"Heating specialist" tab. Each field is one EEPROM byte.

| Message | ID | Field | EEPROM | Parameter | Codec |
|---|---|---|---|---|---|
| `InstallerParameters1` | `df b2 1b` | `SupplyMaxTemp` | `0x1b` | P31 maximum flow temperature | UCH, °C |
| | | `SupplyMinTemp` | `0x1c` | P30 minimum flow temperature | UCH, °C |
| | | `SpecialLevelTemp` | `0x22` | P18 special level, heating | UCH, °C |
| | | `ServiceInterval` | `0x24` | P70 service interval | UCH × 100, h |
| | | `IgnitionLoad` | `0x26` | P35 ignition rating | UCH, % |
| `InstallerParameters2` | `e3 b2 27` | `FlueGasSafetyTemp` | `0x29` | P33 flue gas switch-off temperature | UCH, °C |
| | | `LoadMin` | `0x2d` | P36 minimum boiler rating | UCH, % |
| | | `LoadMaxHeating` | `0x2f` | P37 maximum rating, heating | UCH, % |
| | | `PumpLoadMin` | `0x31` | P44 minimum pump rating, heating | UCH, % |
| | | `PumpLoadMax` | `0x32` | P45 maximum pump rating, heating | UCH, % |
| `InstallerParameters3` | `f7 b2 33` | `FlowReturnDiffTemp` | `0x35` | P48 temperature difference control | UCH, K |
| | | `PumpRunOnHeating` | `0x38` | P41 pump run-on, heating | UCH, min |
| | | `DHWBoostTemp` | `0x3c` | P50 hot-water excess | UCH, K |
| `InstallerParameters4` | `fb b2 3f` | `LoadMaxDHW` | `0x3f` | P38 maximum rating, hot water | UCH, % |
| | | `PumpLoadDHW` | `0x40` | P46 pump rating, hot water | UCH, % |
| | | `PumpRunOnDHW` | `0x41` | P42 pump run-on, hot water | UCH, min |
| `InstallerParameters5` | `ab 62 4b 02 44 02 37` | `BoilerAddress` | `0x4c` | P12 boiler address | UCH, 1 = A, 2 = B |

The ID follows the memory-read scheme of the other boiler reads (`evidence/bc-counters.md`):
checksum, then items "code, address", the high nibble of the code being the number of bytes
minus one and the low nibble 2 for EEPROM. `b2 1b` is twelve bytes from `0x1b`; the fifth read
asks for seven bytes from `0x4b`, then the single bytes `0x44` and `0x37`.

## How it was established

Three sources, each independent of the others.

1. **The tool's developer window** (2026-11-19, `evidence/service-tool-ui-exploration.md`,
   "NFS-Paras"): it names the 55 bytes `0x1b` to `0x51` one by one with the firmware symbol and
   displays each value; all 55 equal the bytes on the bus, in order. That gives the address of
   each symbol.
2. **The tool's "Heating specialist" tab, both boilers** (2026-11-22, 21:02 to 21:03, this
   record): it displays P10 to P71. A byte is a field here only where the symbol names the
   parameter and the displayed value is the byte: `MAXTVSOLL` / P31, `MINTVSOLL` / P30,
   `SONDERNIVEAU` / P18, `WARTUNGSINTERVALL` × 100 / P70, `NG_ZUEND` / P35, `MXTABGAS` / P33,
   `NG_HZ_MIN` / P36, `NG_HZ_MAX` / P37, `PUHZ_MIN` / P44, `PUHZ_MAX` / P45, `DT_VLRL_SOLL` /
   P48, `PNL_HZ` / P41, `TWWPLUS` / P50, `NG_WW_MAX` / P38, `PUHZ_WW` / P46, `PNL_WW` / P42,
   `V24_KM_ADR` / P12.
3. **The telegrams on the bus** (2026-11-22, grabbed by ebusd while each tab was shown, source
   `ff`): the five reads below, per boiler. Every displayed value equals its byte.

For five of the parameters the register survey of 2026-11-19 is a fourth source: read with
`50 22` from ebusd's own address on both boilers, the registers `27 00` (80.0), `11 02` (120.0),
`09 02` (37), `5a 01` (23.0) and `78 01` (1 on the first boiler, 2 on the second) hold the values
of P31, P33, P35, P36 and P12 (`evidence/register-survey-findings.md`).

### Displayed, 2026-11-22

The tab showed the same values on both boilers, except the two marked.

| Parameter | Boiler A (`08`), 21:02:29 | Boiler B (`18`), 21:02:49 |
|---|---|---|
| P10 type of unit | version H | version H |
| External sensor | **yes** | **no** |
| P11 type of gas | natural gas with flue gas damper | the same |
| P12 boiler address | **A** | **B** |
| P13, P14, P15 function of MFA1, MFA2, VA | 9, 2, 7 | 9, 2, 7 |
| P16, P17 inputs H1, H2 | 4, 4 | 4, 4 |
| P18 special level, heating | 60 °C | 60 °C |
| P20 outside sensor correction | 0 K | 0 K (greyed) |
| P23 frost protection | 5 °C | 5 °C (greyed) |
| P30, P31 flow temperature minimum, maximum | 8 °C, 80 °C | 8 °C, 80 °C |
| P32 switching difference | 4 °C | 4 °C |
| P33 flue gas switch-off temperature | 120 °C | 120 °C |
| P34 burner stop/start block | 0 min | 0 min |
| P35 ignition rating | 37 % | 37 % |
| P36 minimum boiler rating | 23 % | 23 % |
| P37, P38 maximum rating heating, hot water | 100 %, 100 % | 100 %, 100 % |
| P40 continuous run of the pump | 0 | 0 |
| P41, P42 pump run-on heating, hot water | 1 min, 3 min | 1 min, 3 min |
| P43 pump control function | 4 | 4 |
| P44, P45, P46 pump rating minimum, maximum, hot water | 50 %, 100 %, 100 % | 50 %, 100 %, 100 % |
| P47, P48 temperature difference control | 2 K, 20 K | 2 K, 20 K |
| P49 pump control interval | 4 s | 4 s |
| P50, P51 hot-water excess, negative difference | 10 K, -5 K | 10 K, -5 K |
| P70 service interval | 4000 h | 4000 h |
| P71 eBUS feed | 1 | 1 |

### Telegrams, 2026-11-22 (source `ff`, request and answer after the length byte)

| Boiler | Message | Request | Answer | Decoded |
|---|---|---|---|---|
| `08` | `InstallerParameters1` | `df b2 1b` | `00 50 08 44 00 0c 0a 02 3c 00 28 5c 25` | 80 °C, 8 °C, 60 °C, 4000 h, 37 % |
| `08` | `InstallerParameters2` | `e3 b2 27` | `00 19 e0 78 78 01 21 17 17 64 32 32 64` | 120 °C, 23 %, 100 %, 50 %, 100 % |
| `08` | `InstallerParameters3` | `f7 b2 33` | `00 62 25 14 28 19 01 3c 1e 50 0a 17 17` | 20 K, 1 min, 10 K |
| `08` | `InstallerParameters4` | `fb b2 3f` | `00 64 64 03 09 08 0d 21 a1 41 22 a7 19` | 100 %, 100 %, 3 min |
| `08` | `InstallerParameters5` | `ab 62 4b 02 44 02 37` | `00 c2 01 15 55 0c 4b b8 0d 19` | 1 (A) |
| `18` | `InstallerParameters1` | `df b2 1b` | `00 50 08 44 00 0c 0a 02 3c 00 28 5c 25` | 80 °C, 8 °C, 60 °C, 4000 h, 37 % |
| `18` | `InstallerParameters2` | `e3 b2 27` | `00 19 e0 78 78 01 21 17 17 64 32 32 64` | 120 °C, 23 %, 100 %, 50 %, 100 % |
| `18` | `InstallerParameters3` | `f7 b2 33` | `00 62 25 14 28 19 01 3c 1e 50 0a 17 17` | 20 K, 1 min, 10 K |
| `18` | `InstallerParameters4` | `fb b2 3f` | `00 64 64 03 09 08 0d 21 a1 41 22 a7 19` | 100 %, 100 %, 3 min |
| `18` | `InstallerParameters5` | `ab 62 4b 02 44 02 37` | `00 c2 02 15 45 0c 4b c8 0d 19` | 2 (B) |

The first answer byte is the status byte of a memory read (0). The two boilers differ in three
bytes: `0x4c` (1, 2: the address), `0x4e` (`55`, `45`: one bit, as the external sensor box) and
`0x51` (the checksum of the block).

## Equipment

Two WTC 250 condensing boilers with WCM-CPU automats (firmware 11.0e, scan `SW=1104;HW=0501`) in
cascade under a system manager; vendor service tool 5.5.19a on a service PC with the vendor's
bus interface; ebusd on the same bus, listening only.

## Date

2026-11-22. The tool was connected for the pass and disconnected at 21:04:46; only the two
"Heating specialist" tabs, one process-value tab of a room unit and the interface dialog were
shown. Nothing was written, no history tab was opened.

## Not verified

- **Read from ebusd's own address.** The five telegrams were seen with source `ff` only. The
  boilers answer the other memory reads (`Counters`, `EventCounters`, the fault counters) to
  ebusd's address the same way; the first read of these five by ebusd itself is still to be
  looked at.
- **Left out on purpose**: parameters whose byte is not established. P20 and P34 display 0
  (`TAUSS_KORREKTUR`, `TBRMINOFF` by the names; a zero shows neither scale nor sign). P23, P32,
  P40, P43, P47, P49, P51 and P71 have no symbol of their own that holds the displayed value:
  several bytes look packed (`HZ_HYS` = `0x44` beside P32 = 4, `PUHZ_DT_REG` = `0x62` beside
  P47 = 2, `WW_HYS` = `0x50` beside P51 = -5), which one read does not prove. P10, P11, P13 to
  P17 are choices held in option bytes (`SEL_IN_*`, `SEL_PR_*`, `KESS_OPT*`), not decoded.
- **`BoilerAddress`**: 1 and 2 are seen for A and B. The tab offers "1", A, B, C, D, E; the
  values of the others are not seen.
- **A second installation.** Both boilers are the same model set alike: every value but the
  address is seen once. A parameter set differently elsewhere would show the scale of its byte
  (all are taken as whole units, as displayed here).
- The `50 22` registers of the same parameters (`27 00` and the others above) are not defined:
  the memory read covers them, and most of the other candidates of the survey hold values that
  several parameters share.
