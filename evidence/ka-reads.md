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
| DHWLoadingPriority | 23 00 | `d82300` | UIN enum | Priority |
| BlockingTime | 25 00 | `4c2500` | UIN min | 1 |
| SupplyMaxTemp | 28 00 | `642800` | UIN/10 °C | 82.0 |
| ModulationStatus | 2c 00 | `482c00` | UIN % | 8 |
| DHWExceeded | 2d 00 | `142d00` | UIN/10 °C | 10.0 |

The last eight are the **read side of settings that are also writable** (`50 23`); only the read
is shipped here, the write belongs to a later lot. `DHWLoadingPriority` (named
`DHWOperationMode` until release 0.4.3) decodes its enum (0=Priority, 1=Sliding, 2=Parallel)
to `Priority`; see the note of 2026-11-18 below for what is established about this list.

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

## Bytes of the twelve reads without a kept telegram (2026-11-18)

The table of "What" gives a value for each message but no bytes. On 2026-11-18, between 10:26
and 10:27, each of the twelve registers below was read once, read-only, with the `hex` command
of ebusd (source `31`, `15 5022 03 <request>`, reads three seconds apart). The request is the
ID of the definition; the answer is the two data bytes after the length byte `02`.

| message | request | answer | value |
|---|---|---|---|
| ErrorStatus | `5c 01 00` | `00 00` | 0 |
| HeatDemandTemp | `b8 02 00` | `65 01` | 35.7 |
| ConfigStatus | `b0 10 00` | `4c 00` | 76 |
| VersionMajor | `45 99 01` | `0a 01` | 266 |
| VersionMinor | `a1 9a 01` | `12 00` | 18 |
| RoomNormalTemp | `70 05 00` | `d7 00` | 21.5 |
| RoomSetbackTemp | `58 08 00` | `a0 00` | 16.0 |
| DHWSetpoint | `54 13 00` | `f4 01` | 50.0 |
| DHWLoadingPriority | `d8 23 00` | `00 00` | Priority |
| SupplyMaxTemp | `64 28 00` | `34 03` | 82.0 |
| ModulationStatus | `48 2c 00` | `08 00` | 8 |
| DHWExceeded | `14 2d 00` | `64 00` | 10.0 |

Eleven of the twelve values are those of 2026-11-16; the heat demand is a live value. These
readings are transcribed in [fixtures.toml](fixtures.toml).

## Note of 2026-11-18 — DHWLoadingPriority: name, and what is established about its values

**Name.** Register `23 00` was shipped as `DHWOperationMode`, "hot water operating mode". Its
three settings are those of a parameter of the room unit that the vendor calls "DHW
operation" ("Service ECS" in French; P423 and P463), described in the chapter on setting the
priority of DHW loading: manual of the room unit WCM-FS 2.0 and of the heating module
WCM-EM 2.1, English edition 83277502, page 55, French edition 83277504, page 59. It says
what happens to a heating circuit while the hot water is loaded. The operating mode of the
hot water is another thing, a choice of the user level. On the owner's decision of
2026-11-18 the message is `DHWLoadingPriority` from release 0.5.0 on, and its comments
follow the manual; address, type and value list are unchanged. The name keeps the `DHW`
prefix of its neighbours (`DHWSetpoint`, `DHWExceeded`) and takes the words of the chapter
rather than the name of the parameter, which says nothing of what is set and is close to
the name it replaces.

**What the three settings mean** (same pages): priority, the heating circuit is cut while the
hot water is loaded; parallel, both are supplied; sliding, the heating circuit is cut when
the boiler is less than 10 K above the hot-water temperature and supplied again in parallel
above 20 K.

**Values.** Established by a read: 0 only. The register answered `00 00` on 2026-11-16 and
on 2026-11-18 (table above), and the list decodes it to `Priority`. That agrees with the
manual, which says on the same pages that the direct heating circuit always has the setting
"priority" and that the parameter is hidden for it: `15` is the system manager, whose own
circuit is the direct one.

Not established: 1 and 2. The list has 1 = `Sliding`, 2 = `Parallel`; both editions of the
manual list the settings in the order priority, parallel, sliding. The order on a page does
not prove the register values, and no record supports the order of the list either: 1 and 2
may be swapped. The origin of the order in the list is not recorded. The list is left as it
is, because a swap would be as unproven as what it replaces; a comment in
`src/wolf/15.w.ka.tsp` says the same. What would settle it: a read of register `23 00` on a
device whose setting is parallel or sliding (a heating circuit of a room unit, P423 or P463,
if the register exists there), or after the operator has changed the setting; neither was
done, and changing a setting is the operator's (rule 7). The message is read only in every
lot, so no value of the list is ever sent.

## Note of 2026-11-20 — DHWExceeded renamed DHWExcessTemp (0.6.0)

Decided by the owner of the test installation: the name was a past participle without the
`Temp` of its neighbours, and the value (10.0) is an excess, so the unit becomes K. Register
`2d 00`, ID `14 2d 00`, unsigned type unchanged. **A lead from one source, not evidence:** the
KA manual (83258404 p. 98) has parameter 576 "Elévation ECS", the boiler flow temperature
above the hot-water setpoint while loading, 10.0 to 30.0 K, factory 15.0 K; the register reads
10.0, inside that range. The comment says that the parameter is not established. Lot O, last
commit of the lot (`kromschroeder: DHWExceeded of the system manager renamed DHWExcessTemp`),
with its metadata as the last commit of lot M (`renamed_from = "ka/DHWExceeded"`), so that both
can be dropped alone.
