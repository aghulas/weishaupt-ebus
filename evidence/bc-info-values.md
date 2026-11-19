# bc1, bc2 — boiler automat information values (the WTC "i" codes) read through 50 22

## What

Lot K, branch `weishaupt-K` of the ebusd-configuration fork (on `weishaupt-J`, below the
translation branch `weishaupt-L`). The WTC-GB boiler automats answer register reads
(`PBSB = 50 22`, ID `<crc> <addr> <sub>`, the `<crc>` precomputed — see
[register-crc.md](register-crc.md)) that carry the same "information values" the WTC display
shows as `i` codes (menu *Info*, manual 83251704, pages 46–47). Eight information values that can be
read with the burner idle are defined on both boilers (slave `08` = bc1, `18` = bc2), in
`src/wolf/08.w.bc1.tsp`, `src/wolf/18.w.bc2.tsp` and the shared models of
`src/wolf/wtc_inc.tsp`. A temperature value is 16 bits, low byte first, signed tenths
(`SIN`/10 °C); a missing sensor answers `0xfe70` = −40.0.

| i (manual) | meaning | addr sub | request | codec | model |
|---|---|---|---|---|---|
| i 35 | flow temperature | `0d 00` | `28 0d 00` | SIN/10 °C | `SupplyTemp` |
| i 37 | return temperature | `16 00` | `24 16 00` | SIN/10 °C | `ReturnTemp` |
| i 31 | flue gas temperature | `45 01` | `09 45 01` | SIN/10 °C | `FlueGasTemp` |
| i 33 | outside temperature | `0c 00` | `74 0c 00` | SIN/10 °C | `OutsideTemp` (shared, lot A) |
| i 34 | domestic hot water temperature | `0e 00` | `cc 0e 00` | SIN/10 °C | `DHWTemp` |
| i 39 | hydraulic separator temperature | `86 02` | `66 86 02` | SIN/10 °C | `HydraulicSeparatorTemp` |
| i 44 | WCM-CPU software version | `99 01` | `45 99 01` | HEX, 2 bytes | `SoftwareVersionCPU` |
| i 45 | WCM-CUI software version | `9a 01` | `a1 9a 01` | HEX, 2 bytes | `SoftwareVersionCUI` |

The first five (i 35 … i 34) were added in release 0.4.1; the last three (i 39, i 44, i 45) in
the 0.4.1-successor. `i 33` reuses the top-level `OutsideTemp` already shared since lot A; the
other temperature models are new shared models in `wtc_inc`. Register `0d 00` is the system
manager's de-couple sensor B22 in lot A, and the boiler's flow sensor here: the `50 22`
register space is generic and the sensor wired to a register differs by device. The comment on
each read cites the `i` code.

The two version registers answer the two bytes `11 04`, which is exactly the software version
the bus scan reports for the boiler automat (`SW=1104`, bytes `0x11 0x04`). They are kept as
those raw bytes (`HEX`, two bytes, displayed `11 04`), the way the scan shows them, rather than
as a decimal `UIN` (which would print 1041 and not match the scan). The same two register
addresses are read as `UIN` on the system manager in lot A (`VersionMajor` / `VersionMinor`),
where they carry different values that are not the scan version; on the boilers they equal the
scan `SW`. The register ↔ `i`-code pairing (`99 01` = i 44 WCM-CPU, `9a 01` = i 45 WCM-CUI)
follows the order of the two version registers (lot A) and of the two version `i` codes
(manual); both registers read the same `11 04` on this installation, so the two cannot be told
apart by value here.

## Live confirmation (read-only, 2026-11-18)

Read on both boilers through a scratchpad `hex` reader restricted to `50 22`/`50 00`
(request `ZZ 5022 03 <crc> <addr> <sub>`, answer `02 <low> <high>`); no write was sent
(rule 7). Boilers running, burner idle on both at the time of the read.

| i | bc1 (`08`) request → answer → value | bc2 (`18`) request → answer → value |
|---|---|---|
| i 35 flow | `28 0d 00` → `02 f4 01` → 50.0 °C | `28 0d 00` → `02 4e 02` → 59.0 °C |
| i 37 return | `24 16 00` → `02 3a 02` → 57.0 °C | `24 16 00` → `02 4e 02` → 59.0 °C |
| i 31 flue gas | `09 45 01` → `02 86 01` → 39.0 °C | `09 45 01` → `02 30 02` → 56.0 °C |
| i 33 outside | `74 0c 00` → `02 6e 00` → 11.0 °C | `74 0c 00` → `02 70 fe` → −40.0 (no sensor) |
| i 34 DHW | `cc 0e 00` → `02 70 fe` → −40.0 (no sensor) | `cc 0e 00` → `02 70 fe` → −40.0 (no sensor) |

The first boiler carries an outside sensor (11.0 °C); the second does not (−40.0), as its RAM
also shows. Neither boiler has a hot-water sensor on this installation (−40.0 at `0e 00`). An
independent morning read on 2026-11-18, boilers idle, gave lower temperatures
(flow 52/54, return 49/52, flue 42/43, outside 11.0/−40.0), decoding the same way: two reads
on two occasions.

The three values added to the lot for the 0.4.1-successor were read the same way on both
boilers, read-only, each twice (burner idle):

| i | bc1 (`08`) request → answer → value | bc2 (`18`) request → answer → value |
|---|---|---|
| i 39 hydraulic separator | `66 86 02` → `02 70 fe` → −40.0 (no sensor) | `66 86 02` → `02 70 fe` → −40.0 (no sensor) |
| i 44 WCM-CPU version | `45 99 01` → `02 11 04` → `11 04` | `45 99 01` → `02 11 04` → `11 04` |
| i 45 WCM-CUI version | `a1 9a 01` → `02 11 04` → `11 04` | `a1 9a 01` → `02 11 04` → `11 04` |

Neither boiler has a hydraulic-separator sensor on this installation (−40.0 at `86 02`); the
message is defined so the read exists where the sensor is fitted, as i 33 / i 34 are. Both
version registers read `11 04` on both boilers, matching the scanned `SW=1104`.

## How it was established

1. **Register space.** A full sweep of `50 22` on `08`, sub = `00`, `01`, `02`, `03`,
   `addr` `0x00`–`0xff` each, read-only through the `hex` command (`50 22`/`50 00` only). Most
   registers answer `02 00 80` = `0x8000`, the "not available" sentinel; a few answer a real
   value. Sub `00` is the generic register space shared with the system manager (lot A).
2. **Checksum.** The first request byte of every register in the table was recomputed offline
   (CRC-8 poly 0x5C, init = first address byte; 8 shift/xor rounds then fold each further byte,
   see [register-crc.md](register-crc.md)) and matches the frame sent: `0d 00 → 28`,
   `16 00 → 24`, `45 01 → 09`, `0c 00 → 74`, `0e 00 → cc`. `0c 00`, `0e 00` and `0d 00` equal
   the IDs lot A already uses for the same register numbers on the system manager (the CRC
   depends only on the address, not the device).
3. **Cross-check against the sensors.** The boiler automat's own RAM, read in the same minutes
   with a `50 00` memory read (the lot-F reads), gave matching figures for return, flue, flow
   and outside on `08`, confirming each register ↔ sensor pairing and the SIN/10 codec.
4. **Manual meanings.** Document 83251704 (WTC-GB 120 … 300-A, 1/2020-08), menu *Info*
   (pages 46–47): i 35 "T° départ", i 37 "Température retour", i 31 "T° fumées", i 33
   "Température extérieure", i 34 "Température ECS" (p. 46); i 39 "T° bouteille" (hydraulic
   separator, p. 47); i 44 "Version du logiciel WCM-CPU", i 45 "Version du logiciel WCM-CUI"
   (p. 47). The vendor service tool on this installation showed the same two version values as
   "I44: Version CPU" and "I45: Version CUI" (`service-tool-log.md`). The boiler automat is the
   WCM-CPU: its software version equals the scanned `SW=1104`, so `99 01` = i 44 and, in the
   same register and `i`-code order, `9a 01` = i 45.

## What is left out

- **i 43 burner operating hours** (`2a 02`, request `de 2a 02`, UIN h): read 20196 on `08` and
  20054 on `18`. This is the same figure lot D already publishes as `Counters.BurnerHours`
  (EEPROM counter `EEA_H_BON`, cross-checked in [bc-counters.md](bc-counters.md)) — the display
  shows it ×100. Omitted to avoid two messages decoding the same physical counter; it can be
  added later if a `50 22`-only read path is wanted.
- **i 46 time since last service** (`bc 02`): already defined as `BurnerServiceHours` in lot E,
  and corrected there to apply the ×10 factor (see below).
- **i 30 eSTB, i 32 ionisation, i 11 power, i 22 pump, i 23 fan speed, i 10 phase, i 42 burner
  starts**: not definable from this read session. i 11/i 22/i 23/i 32 are 0 with the burner off
  and could not be told from the many zero/`0x8000` registers; the eSTB register `5e 01`
  answers `0x8000`; i 42 (≈ 187000 / 139000 starts) does not fit a 16-bit register. These need
  a capture while a boiler is firing, which only the operator can arrange.
- **Register `27 02`** answers a per-boiler number (731 on `08`, 543 on `18`) that steps
  independently and is stable across reads. No `i` code of the *Info* menu matches it: the only
  Info counters are i 42 (burner starts, × 1000) and i 43 (burner hours, × 100), and neither
  figure fits 731 / 543. Left out; recorded as a finding (see "Not verified").

## Relation to lot E (i 46)

Register `bc 02` (i 46) is in units of ten hours (`0x2c` = 44 → 440 h on `08`, `0x27` = 39 →
390 h on `18`; matches [bc-counters.md](bc-counters.md)). Lot E's `BurnerServiceHours` first
read it with a plain `UIN` and no factor, so it reported 44 instead of 440 — 10× low in the
0.3.2 and 0.4.0 releases. Lot E now applies a factor of 10 (ebusd divisor −10) on both boilers
and reads 440 / 390. The second boiler had no `BurnerServiceHours` message before; lot E adds
it. See the lot-E history entry in `docs/plan.md`.

## Equipment

Two Kromschröder WCM-CPU boiler automats on eBUS (slaves `08`, `18`), scanning as
`MF=Kromschröder`, `ID=W`, `SW=1104; HW=0501` (WTC-GB condensing boilers, firmware 11.0e), in
cascade under a WCM system manager (`15`). Read-only; no write was sent (rule 7).

## Date

2026-11-18.

## Not verified

- Every value was read once or twice in one day, boilers idle. No service tool was connected to
  give an independent display figure for the temperatures; they are cross-checked against the
  automat's own RAM and against each other.
- Sign of the temperatures: taken from `otemp10` (SIN/10) and the `0xfe70` = −40.0
  "no sensor" answer; no genuine negative reading was seen on a fitted sensor.
- i 39 reads −40.0 (no sensor) on both boilers: the hydraulic-separator meaning is from the
  manual, not from a live figure on a fitted sensor. The message is defined so the read exists
  where the sensor is present, as i 33 / i 34 already are.
- i 44 / i 45: both version registers read the same `11 04` here, so which register is the
  WCM-CPU version and which the WCM-CUI version is taken from the register order (lot A) and
  the `i`-code order (manual), not proven by distinct values. The `11 04` equals the scanned
  `SW=1104` of the WCM-CPU; the WCM-CUI version was not read separately from the scan.
- **Register `27 02`** (731 on `08`, 543 on `18`): a per-boiler number, stable and stepping on
  its own, not matched to any *Info* `i` code (the Info counters i 42 and i 43 do not fit it).
  Left out of the lot; a finding for a later session with the service tool.
  **Identified on 2026-11-19 from the data** (no new read): it is the burner-start counter
  divided by 256, the upper 16 bits of the 24-bit counter lot D reads from EEPROM
  ([bc-counters.md](bc-counters.md)): its 187 226 to 187 230 starts on `08` and 139 017 on `18`
  give 731 and 543, the values read here; 187 277 and 139 101 in ebusd's cache on 2026-11-19
  still give 731 and 543 (any count from 187 136 to 187 391 gives 731).
  Not confirmed by a step: `08` should read 732 once its starts pass 187 392. Not defined, lot
  D holds the full counter.
  Batch G, step A (2026-11-19 15:37, read only): starts 187 277 and 139 104; `27 02` read
  `db 02` (731) and `1f 02` (543) again. The neighbouring registers do not complete it:
  `26 02` answers `00 80` (0x8000, not available) on both boilers, and so do `25 02` and
  `28 02` of `08`. So `27 02` is not the upper half of a 16-bit window on the counter; it
  stays "starts / 256", confirmed by a step only when `08` passes 187 392 starts. Other sub-01
  registers hold parameters and setpoints and were not read here.
