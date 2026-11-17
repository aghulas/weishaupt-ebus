# ka — system-manager register reads (50 22)

## What

Read-only registers of the KA system manager (circuit `ka`, default target 0x15), emitted
as `r` messages with `PBSB = 50 22` and ID `<crc> <addr> <sub>`, the `<crc>` precomputed
(see [register-crc.md](register-crc.md)). Shipped in `src/wolf/15.w.ka.tsp`
(the `src/kromschroeder` tree is a symlink to `src/wolf`, manufacturer 0x50).

| message | addr sub | id (crc+addr+sub) | codec | live value |
|---|---|---|---|---|
| ErrorStatus | 01 00 | `5c0100` | UIN | 0 |
| HeatDemandTemp | 02 00 | `b80200` | UIN/10 °C | 59.6 |
| DHWSetValue | 03 00 | `e40300` | SIN/10 °C | 50.0 |
| OutsideTemp | 0c 00 | `740c00` | SIN/10 °C | 11.0 |
| DeCoupleTemp | 0d 00 | `280d00` | SIN/10 °C | 56.0 |
| DHWTemp | 0e 00 | `cc0e00` | SIN/10 °C | 51.7 |
| ConfigStatus | 10 00 | `b01000` | UIN | 76 |
| OutsideWeightedTemp | 0c 0a | `7e0c0a` | SIN/10 °C | 11.3 |
| VersionMajor | 99 01 | `459901` | UIN | 266 |
| VersionMinor | 9a 01 | `a19a01` | UIN | 18 |
| RoomNormalTemp | 05 00 | `700500` | UIN/10 °C | 21.5 |
| RoomSetbackTemp | 08 00 | `580800` | UIN/10 °C | 16.0 |
| DHWSetpoint | 13 00 | `541300` | UIN/10 °C | 50.0 |
| DHWOperationMode | 23 00 | `d82300` | UIN enum | Priority |
| BlockingTime | 25 00 | `4c2500` | UIN min | 1 |
| SupplyMaxTemp | 28 00 | `642800` | UIN/10 °C | 82.0 |
| ModulationStatus | 2c 00 | `482c00` | UIN % | 8 |
| DHWExceeded | 2d 00 | `142d00` | UIN/10 °C | 10.0 |

The last eight are the **read side of settings that are also writable** (`50 23`); only the read
is shipped here, the write belongs to a later lot. `DHWOperationMode` decodes its enum
(0=Priority, 1=Sliding, 2=Parallel) to `Priority`, consistent with the heating-only use here.

## How it was established

Live bus, ebusd `read` of each message through the running ebusd (one read per message,
spaced). Each returned a plausible value (above), decoding with the stated codec. The ID's
first byte is the CRC-8 of the address (poly 0x5C), verified frame-by-frame for `0c 00 → 74`,
`0e 00 → cc` and `0c 0a → 7e` in [register-crc.md](register-crc.md); the others are the same
routine applied offline. Cross-check: OutsideTemp (11.0) and OutsideWeightedTemp (11.3) agree
as expected for an unweighted vs time-weighted outside reading.

Toolchain checks on the emitted CSV: `tsp compile` clean, `tsp format --check` clean,
`ebusd --checkconfig` clean (0 errors).

`DeCoupleTemp` was first named `SupplyWTCTemp` and described as the boiler flow. The vendor
service tool labels register `0d 00` "De-couple temperature B22" (see
[service-tool-log.md](service-tool-log.md)); renamed on 2026-11-17, address and codec unchanged.

### Sign of registers 3, 13 and 14

`DHWSetValue` (`03 00`), `DeCoupleTemp` (`0d 00`) and `DHWTemp` (`0e 00`) were first shipped
as unsigned (`temp10`, UIN). No negative reading exists for them: the system manager returned
`f4 01` (50.0), `54 02` (59.6) and `69 01` (36.1) on 2026-11-17. Three observations made the
same day point to a signed 16-bit value all the same:

1. The same register numbers, read with `50 22` on devices of the same family that do not
   have the sensor or the setting (passive capture, master `31`, request payload then the two
   data bytes of the reply):

   | register | request | system manager `15` | heating modules `51`, `52` | room unit `35` |
   |---|---|---|---|---|
   | 3 | `e4 03 00` | `f4 01` | `00 80` | `00 80` |
   | 13 | `28 0d 00` | `54 02` | `00 80` | `00 80` |
   | 14 | `cc 0e 00` | `69 01` | `18 fc` | `00 00` |

   `18 fc` is 0xfc18: -1000 as a signed value, -100.0 °C, a round figure; 64536 as an unsigned
   one, 6453.6 °C. `00 80` is 0x8000, the smallest signed 16-bit number and the eBUS
   replacement value of the signed type (the unsigned one is `ff ff`).
2. The system manager itself answers `18 fc` on its calorifier registers `76 00` and `78 00`
   (no calorifier sensor here), and the heating modules `51` and `52` answer `18 fc` on the
   outside temperature `0c 00`, which is already shipped as signed. The "no sensor" value of a
   temperature register in this family is therefore -100.0 °C, signed.
3. The register list of the vendor service tool gives, in its section for the system manager,
   "SInt × 0.1" for registers 3, 13 and 14 (see [service-tool-log.md](service-tool-log.md)).
   Its sections for other devices give "UInt" for 3 and 14; the bus answers above come from
   those other devices and are signed values nevertheless.

Conclusion: registers 3, 13 and 14 are signed tenths. The definitions use the signed
scalar (`otemp10`, SIN) since 2026-11-17; for the values read so far the decoded figure is
the same.

## Equipment

Kromschröder WCM/WTC regulators on eBUS; KA system manager scanning as `MF=Kromschröder`,
`ID=W`, software version reported by the bus scan (SW=6618).

## Date

2026-11-16; sign of registers 3, 13 and 14 examined on 2026-11-17.

## Not verified

- `SupplySetPointTemp` (04 00), `SupplyHCTemp` (0f 00), `OutsideBlendedTemp` (1a 00),
  `RoomTemp` (11 00), `RoomSetPointTemp` (12 00) and `MixerParameterTemp` (2b 00) gave
  no response on this site and were left out.
- Mixer and calorifier registers decode to the not-available / no-sensor sentinels here
  (no such peripheral on this site); left out pending a site that has them.
- Registers 3, 13 and 14 (`DHWSetValue`, `DeCoupleTemp`, `DHWTemp`) are signed by the evidence
  above, but no negative reading was taken on the system manager itself.
- The sign of `HeatDemandTemp` (register 2) is assumed positive (UIN); the vendor register
  list says "UInt × 0.1" for it, and no sentinel answer was seen.

## Note of 2026-11-17 — BlockingTime

The comment of `BlockingTime` was "minimum burner blocking time". Register `25 00` has the unit
and range (0 to 30 min) of parameter 537 of the system manager, which its installation manual
(WCM-KA 3.0, document 83258404, page 86) describes as the time during which no further boiler
of the cascade is switched on; the anti-cycling time of a burner is parameter P 34 of the
boiler. The comment now says so (lot A). Established from the manual; no test on the
installation shows what the register does.
