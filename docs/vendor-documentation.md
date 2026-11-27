# Vendor documentation: inventory and what it unlocks

Survey of the vendor's partner portal on 2026-11-27, read-only, through its document search and
page reader. Until then the project used three manuals only: system manager 83258404, room unit
and module 83277504, boiler WTC-GB 83251704. This file records which other documents exist, what
they establish for the open items, and what each would unlock under rule 3.

Conventions: documents are named by their eight-digit number and edition (as printed: issue /
year-month); page numbers are those of the PDF. All editions found are **French**; searches with
English or German as the language returned nothing for the WCM documents, so no other language
was compared. Meanings are given in our own words; no vendor text is copied here and no PDF is
kept in any repository. Under rule 3, a manual page is accepted evidence for a vendor code or a
value list; it never replaces a bus read for a register address, and a value list documented for
another interface (the Modbus gateway below) needs one bus observation to be tied to an eBUS byte.

## 1. Inventory

Columns: **New** = not used by the project before this survey; **vs. ours** = relation to the
three manuals already used. Pages are given where the document was opened.

### Documents read for this survey

| Number | Edition | Pages | What it is | vs. ours | Value |
|---|---|---|---|---|---|
| 83272304 | 1/2024-05 | 56 | Installation manual of the vendor's **eBUS / Modbus gateway 2.0** (Unigate), RTU and TCP variants; chapter 10 is a register list per device (WCM-KA, WCM-SOL, WTC 1–5, WCM-FS / WCM-EM 1–8, time programs) | new | **high**: eBUS addresses of every device class, status bits and phase list of the boiler, operating-mode value list of room units and modules, program window coding, cyclic telegrams |
| 83272305 | 02/2012 (and 04/2011) | 32 | earlier edition of the same gateway manual | new | same register 109 / 110 layout (pp. 28–29); confirms the list is not new to the 2024 edition |
| 83053005 | 07/2005 | 76 | Installation manual, **WTC 15-A … 32-A** (gas, wall-hung; automat WCM-CPU 3.x) | new | **high** for the second installation: info values i10–i45 (p. 40), phases 0–9 (p. 41), parameters P10–P72 with ranges and factory values (pp. 42–44), service parameters A1–A12 (p. 46), fault and warning codes (pp. 55–58) |
| 83172004 | 1/2006 and 1/2012 | 4 each | Addenda to the WTC 15-A … 32-A manual: **WCM-CPU 3.x**, then **from 12.0** | new | which info numbers and sensor fault codes moved between automat generations (p. 3, p. 4) |
| 83251704 | 1/2025-01 | 120 | Installation manual, **WTC-GB 210 … 300-A** (current edition; title no longer covers 120 … 170-A) | newer than the editions used (2/2011, 7/2013, 3/2018, 8/2020) | phases (p. 44), info values (pp. 44–45), warning codes (pp. 84–85) and fault codes (pp. 86–87) unchanged for what we rely on (section 7) |
| 83314005 | 1/2024-06 | 152 | Installation manual, **WTC-OB 20 … 35-B** (oil, floor-standing; automat WCM-OB-CPU) | new | the boiler of `aghulas/ha-weishaupt#1`'s family: phases 1–9 with **9 = forced ventilation** (p. 45), its own info list i10–i49 (pp. 45–46), warning codes W80–W88 (p. 108) |
| 83277704 | 1/2012-04 | 48 | User manual, **WCM-FS 2.0** | new (user leaflet of 83277504) | the hot-water push ("Pouss ECS", p. 10) |
| 83251205 | 05/2009 (and 08/2008) | 92 | Installation manual, **WCM-FS (1.x) and WCM-EM 2.0** | new, predecessor of 83277504 | parameter numbers without the `P` prefix and partly shifted (p. 28: 116 slope, 121–124 circuit 2; info 412–422, pp. 33–37, 78–79) |
| 83258405 | 03/2009 | 120 | Installation manual, **WCM-KA 2.0** | new, predecessor of 83258404 | the three-digit numbers checked (513, 535, 571, 604; pp. 63–65, 80, 89) are the same as in the 3.0 manual |
| 83270004 | 1/2012-12 | 40 | Installation manual, **WCM-COM 1.0 expert** (the vendor's network gateway: LAN, GSM, M-Bus, eBUS) | new | no protocol published; eBUS address chosen automatically (p. 8); fault messages carry device and code (p. 30) |
| 83258404 | 1/2013-04 | 124 | WCM-KA 3.0 (ours) | same edition; the only one on the portal | re-read for its fault codes (p. 119) and fault history (p. 110) |
| 83277504 | 3/2012-10 | 112 | WCM-FS 2.0 / WCM-EM 2.1 (ours) | same edition; the only one on the portal | re-read for fault codes (pp. 106–108), circulation time of the push (p. 94), circuit pairs (pp. 32, 38) |

### Documents found, not opened

| Number | Edition | What it is | Why it may matter |
|---|---|---|---|
| 83279304 | 12/2012 | WCM-COM 1.0 home | the simpler WCM-COM; likely the same eBUS facts as 83270004 |
| 83240604 | 03/2006 | WCM-KA for WTC boilers (first generation) | a third system-manager generation; numbering not checked |
| 83277804 | 03/2012 | WCM-EM 2.1 (module alone) | module menus; 83277504 already covers the module |
| 83053204 | 11/2001 – 03/2005 | WCM-EM (first generation) | older modules |
| 83251105 | 08/2008, 05/2009 | WCM-FS (1.x), unit alone | user side of 83251205 |
| 83277604 | 10/2012 | WCM-FS 2.0 with solar controller WCM-SOL 1.0 home | solar registers 20–49 of the gateway list |
| 83172104 | 2005 – 1/2012 | WCM-CPU addenda for WTC 45/60-A | other automat generations |
| 83172004 | 10/2014 | replacement board WCM-CPU-R for WTC 15 … 32-A | automat replacement; software level |
| 83313905 | 06/2024 | WTC-OB 45 installation manual | sibling of 83314005 |
| 89004204 | 02/2021 | vendor information sheet: WTC-OB codes F21 / W22 / F22 | oil-boiler flame faults |
| 83536204, 83554104 | 2016 – 05/2022 | replacement of the WTC-OB automat board WCM-OB-CPU | automat generations of the WTC-OB |
| 83807204 | 11/2025 | Modbus TCP of WTC-GB 470-A / 620-A | a newer boiler generation, not our automats |
| 83053304, 83053404 | 2001 – 2005 | WCM-FB remote control (user, installer) | the predecessor of the WCM-FS (eBUS codes 81–88 of the WTC-A name it) |
| 83193304, 83756204, 83757004 | 2013 | maintenance sheet and inspection cards WTC 15/25/32-A and WTC-GB | maintenance only |

Not found: a published eBUS protocol of the vendor, a manual of the service tool WCM-Diagnose
(83053005 p. 46 points to a user manual of the software that the portal does not list), an
edition of the WTC-GB manual that still covers 120 … 170-A after 8/2020, and any document in
English or German through this portal.

## 2. The Modbus gateway (83272304): the most useful document

The gateway reads the eBUS devices and republishes their values as Modbus registers, so its
register list is a vendor statement of what each device publishes, with units and value lists.
It is not a statement of eBUS telegrams: which `50 22` register or which byte of a broadcast
feeds a Modbus register is not given. What it establishes:

**eBUS addresses by device class** (p. 7, p. 40). Boiler automats as masters `03`, `13`, `33`,
`73`, `f3` for boiler address P12 = A … E; room units #1 … #8 as masters `30`, `70`, `f0`, `17`,
`37`, `77`, `f7`, `1f`; heating modules #2 … #8 at `51` … `57`; system manager and solar
controller at `f1` / `10`; the gateway itself at `00`, `10` or `11`. Every address we observe
fits: `03` / `13` (slaves `08` / `18`), `30`, `70`, `f0` (slaves `35`, `75`, `f5`), `51`, `52`,
`10` / `f1`; addresses 33 … f3 and 17 … 1f are the ones a third to fifth boiler and room units
#4 … #8 would take. It also says that `00` is the source to use when a value is sent to a room unit or
module (p. 8), which agrees with our "the source address decides" findings
(`docs/ebus-protocol.md`, section 5). For `f1` without a system manager (the second
installation) it says nothing: `f1` is listed for the WCM-KA and the WCM-SOL only.

**Cyclic telegrams** (p. 9, p. 52): identification `07 04` at start-up; a boiler shows W80,
locks out and drops the outputs set as fault report when it receives no `05 07` from a WCM-KA,
WCM-FS, WCM-SOL or the gateway within 10 minutes; start conditions `50 09` every 15 minutes without a WCM-KA, every
40 s with one; the boiler sends block 1 of `50 0a` every 30 s.

**Boiler status bits** (register 109, p. 45; same in 83272305 p. 28). High byte: bits 8–10
reserved, then flame, valve 1, valve 2, pump, alarm. Low byte: chimney-sweep function,
summer / automatic, standby, maintenance, frost protection, cascade operation, and a two-bit
mode in bits 6–7 (none, heating, hot water, hot water with the pump in parallel).
Compared with `KaStatus` (`src/wolf/wtc_inc.tsp`, model `Status`):

| `KaStatus` byte 2 | gateway high byte | `KaStatus` byte 3 | gateway low byte |
|---|---|---|---|
| bits 0–2 `Ukn2_1`–`Ukn2_3` | reserved | bit 0 `ManualStartUp` | chimney-sweep function |
| bit 3 `Flame` | flame | bit 1 `BurnerStatus` | summer / automatic |
| bit 4 `GasValve1` | valve 1 | bit 2 `Ukn3_3` | standby |
| bit 5 `GasValve2` | valve 2 | bit 3 `Service` | maintenance |
| bit 6 `Pump` | pump | bit 4 `Ukn3_5` | frost protection |
| bit 7 `Error` | alarm | bit 5 `Fan` | cascade operation |
| | | bit 6 `CircPump` | mode, low bit (heating) |
| | | bit 7 `DHWPump` | mode, high bit (hot water) |

Byte 2 matches name for name, which makes it very likely that register 109 is bytes 2–3 of
`50 0a`. On byte 3 the gateway gives an explanation for the three points the second
installation raised (`evidence/second-installation-ebus2mqtt.md`, section 3): `BurnerStatus`
set with the burner off is "summer / automatic"; bit 6 (our `CircPump`, their "burner demand,
heating") is the heating mode; `Ukn3_5`, set in all their samples, is a named state. `Fan` would
be "cascade operation", a conflict with our name. Assessment: a value list from a manual, so
accepted for the names, but its tie to `50 0a` is inferred; one passive capture with a known
state (a hot-water load: bit 7; chimney-sweep mode set by the operator: bit 0) confirms it.

**Phase and fault code in one byte** (register 110, p. 45): the operating phase 0–8 (same list
as the WTC-GB manual), and the fault number instead of the phase when the alarm bit is set;
fault numbers start at 11 and are those of the boiler manual. This is the documentary basis for
the note in `evidence/broadcast-kastatus.md` that values from `0x0b` are fault codes. Phase 19
with the alarm bit clear (second installation, sample T2) is not explained by any document read.

**Room unit and module values** (pp. 46, 51): per unit the operating mode (read and write),
fault, current room / flow / hot-water setpoints, current heat demand, room and hot-water
temperatures, normal / reduced room setpoints, slope, frost setpoint, summer / winter limit,
hot-water setpoints, holiday flag; per module the flow temperature, normal / reduced flow
setpoints, outside and averaged outside temperature, circulation temperature. The operating-mode
value list (p. 46) is **1 standby, 3 heating (normal), 4 reduced, 5 holiday / summer, 11, 12,
13 heating programs 1, 2, 3** (for a hot-water module: standby, normal, reduced, program). The
values from a module are given when no room unit is fitted (p. 46).

**Time programs** (pp. 47–50): 105 registers per room unit (three heating programs, hot water,
circulation; 7 days × 3 windows), high byte the switch-off and low byte the switch-on time in
quarter hours from midnight, `80` for an empty slot. This is the coding established on the bus
(`evidence/room-units-programs.md`): same count (105 messages per unit), same order, same
empty marker.

**Boiler values** (p. 44, p. 52): the gateway's boiler registers 1xx are numbered after the
display's info values ("units and tens" = the i number): load (i11), weighted outside (i12),
setpoint (i13), valve position (i20), pump speed (i22), flow / safety temperature (i30, i35),
flue gas (i31), outside (i33), hot water (i34), return on a WTC-GB (i37), de-coupling on a
WTC-GB (i39), counters (i40–i46). That supports the boiler vendor codes of lot 1 and shows
which i numbers differ by series (i37, i39, i40–i46 have other meanings on a WTC-OW / WTC-OB).

## 3. What the documents settle for the open vendor codes

`open.vendor_codes` lists 48 messages after the 1.4.1 draft (`evidence/vendor-codes.md`).

- **Circuit pairs (37): not settled.** No document says which number a unit that drives
  circuits 1 and 2 shows for circuit 2. 83277504 is the only edition on the portal; it names
  the second set *Réglage #2 (pour WCM-FS#1+2)* (p. 38: P461–P465) and P121–P124 (p. 32) as
  before. The FS 1.x manual 83251205 has the same two sets without the `P` (p. 28). The gateway
  treats the two identities `30` / `70` as two room units #1 and #2 with separate register
  blocks (p. 40, p. 51), which fits our model (one physical unit, two bus identities) but gives
  no display number. Item 7 of `docs/owner-checklist-room-units.md` stays the way to settle it.
- **The 10 `display` candidates: supported in meaning, not in number.** The gateway confirms
  that a room unit publishes a current flow setpoint and a current heat demand (p. 46: two
  distinct values, matching `SupplyHCSetTemp` and `HeatDemandTemp`) and that a module
  publishes the actual flow temperature of its circuit (p. 46, register 690), the meaning
  lot 2 left unconfirmed for `em2` / `em3` `SupplyHCTemp`. It carries no display number. For
  `FanOperation`, the WTC-GB edition 1/2025-01 gives i23 as fan speed in 1/min × 10 (p. 44) as
  before. For `ka/ConfigStatus` nothing new. Items 8 to 11 of the checklist stay.
- **`ka/DHWLoadingPriority`: the mismatch holds.** The WCM-KA 2.0 manual gives 571 the same
  meaning as 3.0 (hot-water variant, 83258405 p. 64, p. 89). No document gives the system
  manager a hot-water priority setting.
- **Scheme `wcm-ka-3` also fits the WCM-KA 2.0** for the four numbers checked (513, 535, 571,
  604). The WCM-FS 1.x numbers differ from the 2.0 ones (83251205 p. 28 against 83277504 p. 32),
  so a `wcm-fs-2` code must not be shown for a 1.x room unit.

## 4. Fault and warning codes (lot 3 of `docs/design-vendor-codes.md`)

There is no third, hidden numbering. Two families of codes, with disjoint ranges:

1. **Boiler codes, W / F 11–89** (one number space, the letter is the kind). WTC-GB: 83251704
   1/2025-01 warnings pp. 84–85, faults pp. 86–87, the same set as the 8/2020 edition used in
   `evidence/bc-fault-counters.md` (W48 and F49 included; W80–W89 eBUS and input N1). WTC 15-A …
   32-A: 83053005 pp. 55–58, the same scheme but **not the same meanings** for some numbers:
   13 (flue gas over 120 °C), 38 / 39 (buffer sensors B10 / B11, where the WTC-GB has the flue
   gas pressure switch and the de-coupling sensor), 42 (no PWM pump signal), 56 (ionisation
   measurement) and 61–67 (combustion control calibration) exist on the WTC-A only; the
   sensor codes even moved between automat generations (addenda 83172004, p. 4 of each
   edition). WTC-OB: its own list (83314005, chapter on fault finding; only W80–W88 on p. 108
   read).
2. **WCM device codes, 130–202**, shared by the system manager and the room units / modules:
   sensors 130–139, actuators 142 / 149, internal 154, eBUS communication 180–199 (180 system
   manager, 181–188 room units, 189 input N1, 190 modules, 191–199 boiler automats), addressing
   200–202. System manager: 83258404 p. 119. Room unit and module, with the device that raises
   each code: 83277504 pp. 106–108. Their meaning agrees across the two manuals.

**Fault history** (83258404 p. 110, 83277504 p. 53): each entry is a source device, a code, a
date and a time; the end of a fault is an entry with code 00. The room-unit example shows a
boiler code (15) with the boiler as source. So an `ErrorCode` field is read in the scheme of
its `ErrorDevice`: boiler W / F codes when the source is a boiler, WCM codes otherwise. The
WCM-COM prints the same pair in its alarm messages (83270004 p. 30).

Assessment: these are value lists from manuals, accepted under rule 3. They unlock lot 3: two
schemes (`wtc-gb` for the boiler codes of a WTC-GB, a new `wcm` scheme for 130–202), value lists
for the code fields of the fault logs of `ka` and `em1` and for `ka/ErrorStatus`, and a note that
a WTC-A code needs its own scheme. The pairing of `ErrorCode` with `ErrorDevice` values (which
number means which device) still needs one fault on the bus; only code 0 has been read
(`evidence/em1-fault-log.md`).

## 5. Operating phases and status bits

| Phase | WTC-GB (83251704 1/2025-01 p. 44) | WTC 15-A … 32-A (83053005 p. 41) | WTC-OB (83314005 p. 45) |
|---|---|---|---|
| 0 | burner off | burner off | – |
| 1 | fan standstill check | fan standstill check | fan standstill |
| 2 | reach pre-purge speed | pre-purge speed reached | oil preheating |
| 3 | pre-purge | pre-purge countdown | pre-purge / pre-ignition |
| 4 | reach ignition speed | ignition speed reached | safety time |
| 5 | ignition (flame forming time) | safety time | post-ignition |
| 6 | burner in operation | burner in operation, control active | flame stabilisation |
| 7 | gas valve check | gas valve V1 check | controller released |
| 8 | reach post-purge speed, post-purge | gas valve V2 check | post-purge |
| 9 | – | post-purge speed reached, post-purge | **forced ventilation** |

What this changes:

- **`ForcedVenting` (phase 9) has a source now, for the oil boiler only.** The WTC-OB names
  phase 9 forced ventilation; the WTC-A uses 9 for post-purge (its 7 / 8 are the two gas valve
  checks); the WTC-GB stops at 8. Our phase names 0–8 follow the WTC-GB and fit the gateway
  list (83272304 p. 45). Closes the "no source" half of the discovery of 2026-11-19; the label
  is right for a WTC-OB and wrong for a WTC-A, and a WTC-GB never sends it.
- **Phase 19**: in no document. With the gateway's rule (fault number in this byte only when the
  alarm bit is set) and the alarm bit clear in that sample, it stays an unexplained phase of the
  WTC 25-A automat.
- **Status bits**: section 2.

## 6. WTC 15-A / 25-A parameters (for the second installation)

83053005 pp. 42–44 (automat 3.x, the generation the addenda 83172004 describe; the third-party
automat reports software `0315`, so 3.15 is the likely match, not established). Against the
third-party data and the vendor table `0003362` (`evidence/automat-firmware-tables.md`):

| Number | WTC 15-A / 25-A (83053005) | WTC-GB (ours) | Third-party / table |
|---|---|---|---|
| P20 | outside temperature correction, −4 … +4 K, factory 0 | same role | table predicts `0x2e` = `ff`, −1 K: in range |
| P30 | minimum flow setpoint, 8 … (P31 − P32) °C, factory 8 | same role | table predicts `0x37` = 41 °C: in range |
| P42 | minimum pump speed, 20 … P43 %, factory 30 | hot-water pump run-on | their `0x20`: agrees with the manual |
| P43 | maximum pump speed, P42 … 100 %, factory 60 (70 on the 25 kW) | other meaning | their `0x21`: agrees |
| P44 | flow adjustment with a hydraulic separator, 0 … 7 K, factory 4 | `IP2.pumploadmin` (pump rating minimum) | – : another meaning again |
| P45 | hot-water power, 20 … 100 %, factory 60 | pump rating maximum | – |
| P10–P18, P21–P23, P31–P41, P50–P53, P60–P62, P70–P72 | listed with range and factory value | partly other numbers | – |

Assessment: the manual is evidence for the numbers, ranges and factory values of a WTC 15-A …
32-A; it does not give EEPROM addresses. Together with the third-party block and table
`0003362` it supports the false-match warning of `docs/design-vendor-codes.md` (P42) with a
vendor page, and gives the value ranges a WTC 25-A file would declare. The file itself still
needs the three blocks and display values listed in the record's recommendation.

## 7. Newer editions of our three manuals

- **83258404 (WCM-KA 3.0)** and **83277504 (WCM-FS 2.0 / WCM-EM 2.1)**: the portal lists one
  edition each, the ones used (4/2013, 10/2012). Nothing changes.
- **83251704 (WTC-GB)**: edition 1/2025-01 is current. Phases 0–8 (p. 44), info values i10–i46
  (pp. 44–45; i44 automat software, i45 display unit software, i46 time since maintenance in
  h × 10), warning and fault codes (pp. 84–87) are the same as in the 8/2020 edition the
  records cite. The title now covers 210 … 300-A only; our boilers (250) stay covered. No
  page we rely on changes meaning; page numbers differ from the 8/2020 edition, so records
  keep their edition with each page.

## 8. WCM-COM and the eBUS itself

- **WCM-COM 1.0** (83270004): web, e-mail, SMS and M-Bus meter gateway on the eBUS; its eBUS
  address is set automatically (p. 8), it scans the bus at start-up (p. 22, p. 35) and its
  alarm messages name a device and a code (p. 30). No register list, no protocol. The gateway
  manual states that WCM-FB and WCM-COM cannot be connected (83272304 p. 8); in context this
  reads as "not together with the gateway", not established.
- **eBUS facts usable in `docs/ebus-protocol.md`**: the address table and cyclic telegrams of
  section 2, and the fact that the vendor's own gateway sends values to room units from source
  `00` (p. 8).
- **Hot-water push**: section 10.

## 9. Follow-up tasks, in order

| # | Task | Effort | Closes / advances |
|---|---|---|---|
| 1 | *Done 2026-11-27 (prepared locally, not released): `OperatingMode` on `fs1`–`fs3`, `em2`, `em3`, [record](../evidence/operating-mode.md); P111 open as `display`, checklist item 12.* **Program selector `12 01` value list.** Record the operating-mode list (83272304 p. 46: 1, 3, 4, 5, 11, 12, 13) with the survey read 11 = automatic / program 1 (`evidence/register-survey-findings.md`) and define `12 01` read-only on the room units and modules with that list. The address is already from the bus; the list is from the manual; the correspondence of the gateway's mode register with `12 01` rests on the value 11 and the menu meaning: one read on a unit set to standby or reduced confirms it. Candidate vendor code: the room unit's heating-mode setting, 111 (83277504 p. 98), to check on the display with item 7 of the checklist. | small (record + one message per circuit) | discovery 2026-11-17 (program selector, values 12 / 13), plan "Remaining 1.x candidates" first item, roadmap item 5 |
| 2 | **`KaStatus` status bits.** Record the bit list of 83272304 p. 45 against `Status`; rename `BurnerStatus`, `Fan`, `CircPump`, `DHWPump` and name `Ukn3_3`, `Ukn3_5` once one passive capture during a hot-water load (bit 7) confirms the tie to `50 0a`. Read-only. | small; needs the adapter | the three `KaStatus` names questioned in `evidence/second-installation-ebus2mqtt.md`; roadmap item 3 |
| 3 | *Done 2026-11-27: [record](../evidence/broadcast-kastatus.md), section "Phase list: sources"; comments on `weishaupt`, notice limit reworded.* **Phase list sources.** Update `evidence/broadcast-kastatus.md`: sources for phases 0–8 (WTC-GB, gateway), for 9 (WTC-OB forced ventilation, WTC-A post-purge), the "fault code when alarm" rule; reword the `ForcedVenting` comment to say it is the oil boiler's phase 9. | small | discovery 2026-11-19 (`ForcedVenting`, no source); not-verified list of `broadcast-kastatus.md` |
| 4 | **Vendor codes, lot 3 (fault codes).** Design addendum: schemes `wtc-gb` (W / F 11–89) and `wcm` (130–202), value lists for the code fields of `ka` / `em1` fault logs and `ka/ErrorStatus`, a WTC-A note; then the metadata on `weishaupt`. The device-number pairing waits for a fault on the bus. | medium | lot 3 of `docs/design-vendor-codes.md`; `evidence/em1-fault-log.md` (enumerations not decoded) |
| 5 | *Done 2026-11-27: `docs/ebus-protocol.md`, sections 1 and 7.* **eBUS address table.** Add the vendor's address classes and cyclic telegrams (section 2) to `docs/ebus-protocol.md` sections 1 and 7, with 83272304 pages. | small | wording of `f1` / `f6`; context for question 2 of section 8 |
| 6 | *Done 2026-11-27: `evidence/automat-firmware-tables.md`, section 5.* **WTC 25-A parameter ranges.** Add the table of section 6 to `evidence/automat-firmware-tables.md` (or the second-installation record) as the range source for a future WTC 25-A file. | small | prerequisite of roadmap item 3, owner decision (c) |
| 7 | *Done 2026-11-27: `evidence/vendor-codes.md`, "Schemes".* **Scheme notes.** Note in `evidence/vendor-codes.md` that `wcm-ka-3` numbers also hold for a WCM-KA 2.0 (four checked) and that WCM-FS 1.x numbers differ. | small | consistency of lot 1 / 2 for other installations |

Unchanged: the circuit pairs and the `display` candidates still need the displays (owner
checklist items 7 to 12); `ka/DHWLoadingPriority` stays a mismatch. Open: tasks 2 (needs the
adapter) and 4.

## 10. Notes for the owner on `aghulas/ha-weishaupt#1` (hot-water push)

Not a reply; facts to draw on.

- The function exists on the WCM-FS 2.0 as a key on the room unit: on the hot-water setpoint
  screen, available while hot water runs in reduced mode, it starts one load up to the normal
  hot-water setpoint and runs the circulation pump (user manual 83277704, p. 10). The
  circulation run time of that push is an installer setting, P609, 30 s to 20 min, factory
  3 min (83277504 p. 94).
- No document read describes a bus command for it. The vendor's Modbus gateway, which can set a
  room unit's operating mode and its normal and reduced hot-water setpoints (83272304 p. 46),
  offers no push either. So the push is a local function of the room unit; what goes on the bus
  is its consequence, a higher hot-water setpoint in the unit's `05 07` heat demand to the
  boiler.
- What would show how to trigger it from outside: the read-only capture already proposed on the
  issue, taken while the owner presses the key: the `05 07` from the unit (hot-water setpoint
  byte), and any `50 23` / `09 03` the unit sends at that moment.
- Workarounds a reader could weigh, none tested here and all writes (rule 7, theirs to try):
  raising the reduced hot-water setpoint for one load, or switching the unit's hot-water mode;
  both are settings the gateway manual shows as writable, not a push.
- Their boiler is a WTC-OB: its phases differ from a WTC-GB (section 5), and phase 9 there is
  forced ventilation.
