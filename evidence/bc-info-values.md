# bc1, bc2 — boiler automat information values (the WTC "i" codes) read through 50 22

## What

Lot K, branch `weishaupt-K` of the ebusd-configuration fork (on `weishaupt-J`, below the
translation branch `weishaupt-L`). The WTC-GB boiler automats answer register reads
(`PBSB = 50 22`, ID `<crc> <addr> <sub>`, the `<crc>` precomputed — see
[register-crc.md](register-crc.md)) that carry the same "information values" the WTC display
shows as `i` codes (menu *Info*, manual 83251704, pages 46–47). Five temperatures that can be
read with the burner idle are defined on both boilers (slave `08` = bc1, `18` = bc2), in
`src/wolf/08.w.bc1.tsp`, `src/wolf/18.w.bc2.tsp` and the shared models of
`src/wolf/wtc_inc.tsp`. The value is 16 bits, low byte first, signed tenths (`SIN`/10 °C); a
missing sensor answers `0xfe70` = −40.0.

| i (manual) | meaning | addr sub | request | codec | model |
|---|---|---|---|---|---|
| i 35 | flow temperature | `0d 00` | `28 0d 00` | SIN/10 °C | `SupplyTemp` |
| i 37 | return temperature | `16 00` | `24 16 00` | SIN/10 °C | `ReturnTemp` |
| i 31 | flue gas temperature | `45 01` | `09 45 01` | SIN/10 °C | `FlueGasTemp` |
| i 33 | outside temperature | `0c 00` | `74 0c 00` | SIN/10 °C | `OutsideTemp` (shared, lot A) |
| i 34 | domestic hot water temperature | `0e 00` | `cc 0e 00` | SIN/10 °C | `DHWTemp` |

`i 33` reuses the top-level `OutsideTemp` already shared since lot A; the other four are new
shared models. Register `0d 00` is the system manager's de-couple sensor B22 in lot A, and the
boiler's flow sensor here: the `50 22` register space is generic and the sensor wired to a
register differs by device. The comment on each read cites the `i` code.

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
   "Température extérieure", i 34 "Température ECS".

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
- Other populated sub-02 registers were not identified (a per-boiler counter at `27`, a
  temperature with no sensor at `86`); sub-01 holds parameters and setpoints, not read here.
