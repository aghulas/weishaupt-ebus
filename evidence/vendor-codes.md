# Vendor codes: the number a vendor document prints for a value

## What

The metadata of a release names every value by circuit, message and field, and gives it a
label. The vendor manuals and the controller displays name the same value by a number:
parameter 535 on the system manager, P112 on a room unit, P31 or i35 on a boiler. This record
is the source (rule 3) of the vendor codes of the metadata sidecar (`metadata/weishaupt.toml`,
tables `[vendor_schemes]`, `[[vendor_code]]` and `[[vendor_open]]` on the `weishaupt` branch of
the configuration fork), lots 1 and 2 of the study `docs/design-vendor-codes.md`, decided by
the owner on 2026-11-27. Format in `docs/companion-contract.md`, "Vendor codes".

Lot 1: **136 messages**, 44 of their fields among them, **164 codes**:

| Device | Circuits | Messages | Codes on the message | Codes on fields |
|---|---|---|---|---|
| boilers | `bc1`, `bc2` | 17 each | 9 each (i-codes of the register reads) | 22 each, on 8 memory reads |
| system manager | `ka` | 26 | 26 | — |
| room units | `fs1`, `fs3`; `fs2` | 23 each; 22 | 23 each; 22 | — |
| heating modules | `em2`, `em3` | 4 each | 4 each | — |

Lot 2 (from 1.4.1, prepared 2026-11-27): **77 more messages**, 2 more fields, **79 codes**, in
section "Codes of lot 2":

| Device | Circuits | Messages | Codes on the message | Codes on fields |
|---|---|---|---|---|
| boilers | `bc1`, `bc2` | — | — | 1 each (`Operation.pumpspeed`, i22) |
| system manager | `ka` | 16 | 16 | — |
| its direct circuit | `em1` | 15 | 15 | — |
| room units | `fs1`, `fs2`, `fs3` | 14 each | 14 each | — |
| heating modules | `em2`, `em3` | 2 each | 2 each | — |

## Schemes

The vendor numbers parameters per product and per manual, not across the range: the same
number names other settings on other devices (601: outside temperature info on the manager,
hot-water maximum on a room unit; 315: control type on a room unit, modulation minimum in an
earlier manager form), and on other boiler series (P42 is the hot-water pump run-on here, the
minimum pump rating on a WTC 25-A, `second-installation-ebus2mqtt.md`). A code is therefore
always given with its scheme, and the scheme names the document whose parameter table the code
is copied from.

| Scheme | Devices | Document | How the manual prints a code | Pattern in the sidecar |
|---|---|---|---|---|
| `wcm-ka-3` | system manager WCM-KA 3.0 | 83258404, 1/2013-04 (French) | three digits, no letter: `535` | `[0-9]{3}` |
| `wcm-fs-2` | room unit WCM-FS 2.0 and heating module WCM-EM 2.1 | 83277504, 3/2012-10 (French) | `P` and three digits: `P112` | `P[0-9]{3}` |
| `wtc-gb` | boiler automat of the WTC-GB 120 … 300-A | 83251704, 1/2020-08 (French) | `P` and two digits (parameters), `i` and two digits (info values), printed with a space: `P 31`, `i 35` | `[Pi][0-9]{2}` |

Spelling: as the manual prints it, without the space (`P31`, `i35`); consumers compare without
case and spaces (owner's decision 4). A module has no display: its values are set and numbered
on the room unit, so modules and room units share one scheme.

**Other editions (survey of the vendor's portal, 2026-11-27,
[vendor-documentation.md](../docs/vendor-documentation.md), sections 1 and 3).**

- `wcm-ka-3` also holds for a **WCM-KA 2.0**: in its manual (83258405, 03/2009) the four numbers
  checked have the same meaning as in the 3.0 manual: 513 *Conf WCM-KA* (p. 63), 535 *Modul Min*
  (pp. 63, 80), 571 *Variante ECS* (pp. 64, 89), 604 *Info KA* (p. 65). Four of the 3.0 numbers
  were compared, not the whole table; a consumer may show a `wcm-ka-3` code on a WCM-KA 2.0 with
  that reserve. The portal lists one edition of the 3.0 manual, the one used.
- `wcm-fs-2` does **not** hold for a **WCM-FS 1.x**: its manual (83251205, WCM-FS and WCM-EM 2.0,
  05/2009) prints the numbers without the `P` and partly shifted (p. 28: 114 and 115 the flow
  setpoints, 116 the slope, 117 the frost protection, 118 the summer / winter changeover, where
  83277504 p. 32 has P115, P116, P117, P118, P119; no 111 and no 114 acceptance; the second
  circuit's 121–124 and 132, 133, 141, 151–154 keep their numbers). A `wcm-fs-2` code must not
  be shown for a 1.x room unit; such a unit would need its own scheme, which this project has
  no unit to check against.
- The boiler scheme `wtc-gb` does not hold for a WTC 15-A … 32-A (83053005), whose P42–P45
  mean other settings ([automat-firmware-tables.md](automat-firmware-tables.md), section 5).

## How the codes were established

- **Manual pages, read on 2026-11-27** through the document store, French editions, text of
  the parameter tables: system manager 83258404 pp. 65–67 (installer menus *Cascade*,
  *Casse-pression / Echangeur*, *Tampon*, *E C S*, *Date*, *Info système*); room unit and module
  83277504 pp. 31–39 (user menus *Réglage#1*, *Réglage#2*, *E C S*, *Vacances*, *Date*; installer
  menus *Mise en service*, *Info système*, *Circuit chauffage*, *Comport. régul*, *E C S*);
  boiler 83251704 pp. 46–51 (menu *Info* i10–i46, menu *Paramètres* P10–P71). Each code below
  is the number the table prints beside the setting whose meaning matches the message (its
  description, its range and its factory value), not only a number from one source.
- **Vendor service tool form**: the number the form prints beside a register,
  `register-candidates.csv` (column `vendor_param`, joined on device and register), from the
  analysis in `vendor-software-analysis.md`. It agrees with the manual for every code below
  except the conflicts settled in the next section.
- **Records of the messages**: the record that established the register or the memory read
  (last column), where the code often already appears in the description (`info value i35`,
  `parameter P31`, `parameter 551`).

## Conflicts, and how they were settled

1. **3xx and 5xx on the system manager** (14 messages: `ChangeOverTime`, `ModulationMin`,
   `ModulationMax`, `BlockingTime`, `ModulationDiffTemp`, `DeCoupleExcessTemp`,
   `DeCoupleMinTemp`, `DeCoupleMaxTemp`, `CalorifierExcessTemp`, `CalorifierSwitchDiff`,
   `DHWSetpoint`, `DHWSwitchDiff`, `DHWExcessTemp`, `DHWLegionellaDay`). The service tool's
   form prints two numbers per register, for example 315 / 535 for `ModulationMin`. The
   manual of the WCM-KA 3.0 lists these settings as 531–594 (pp. 65–66); its 3xx numbers are
   the installer level of the direct circuit #1 (pp. 51–53) and mean other settings (341 is
   the minimum flow temperature of that circuit, not the calorifier excess). The 5xx is kept;
   the 3xx of the form is probably the numbering of an earlier KA and is not published.
2. **Three hot-water parameters one off.** The form prints 580 for `LegionellaStartTime`, 581
   for `CircWithLegionella` and 582 for `LegionellaCirculationTime`. The manual (p. 66) prints
   580 *Cons.temp.antilég.* (setpoint, = `LegionellaSetpoint`, form 580 as well), 581 *Tps fct
   légion.* (start time, factory 22:00), 582 *Circ.Légion.* (circulation pump during the
   protection, factory Arrêt) and 583 *Temps circul.* (circulation time, factory 03:00 min).
   The meanings, the factory values and the types of the registers (a time, an on/off, a
   duration) follow the manual: 581, 582, 583. The description of `LegionellaStartTime`
   already said 581. Two messages carrying 580 in the form is itself the sign of the shift.
3. **`ControlVariation` on the room units**: the form prints 315 / 316, one per heating circuit
   (*Ty régul#1*, *Ty régul#2*, p. 36). `fs1` and `fs3` take P315 (circuit 1 of their unit,
   `room-units-control-variation.md`); `fs2`, the second circuit of the unit for circuits 1
   and 2, is left open (below).
4. **One code on several messages** is not a conflict: P141 (*Vacances, Durée*) covers the six
   holiday-date registers of a room unit, 593 / 594 and P153 / P154 the day and the month of
   the summer-time dates, i31 the register `FlueGasTemp` and the field `fluegastemp` of the
   memory read `Temperatures`.
5. **Room-unit numbers on the heating modules**: a module has no display; P112, P113, P118 and
   P610 are the numbers the room unit shows for the module's circuit (p. 32 and 39). The
   module messages whose number differs by circuit are open (below).

## Codes of lot 1

### WCM-KA 3.0 system manager (`wcm-ka-3`, document 83258404)

| Circuit | Message | Code | Manual (page, menu) | Form register (numbers the form prints) | Record of the message |
|---|---|---|---|---|---|
| `ka` | ChangeOverTime | 532 | p. 65, Cascade | 65004 (312 / 532) | `settings-writes`, `register-write-crc` |
| `ka` | ModulationMin | 535 | p. 65, Cascade | 65003 (315 / 535) | `ka-modulation-limits` |
| `ka` | ModulationMax | 536 | p. 65, Cascade | 65002 (316 / 536) | `ka-modulation-limits` |
| `ka` | BlockingTime | 537 | p. 65, Cascade | 37 (317 / 537) | `settings-writes`, `register-write-crc` |
| `ka` | ModulationDiffTemp | 538 | p. 65, Cascade | 65001 (318 / 538) | `survey-reads` |
| `ka` | RegulationP | 539 | p. 65, Cascade | 671 (539) | `settings-writes`, `register-write-crc` |
| `ka` | RegulationI | 540 | p. 65, Cascade | 670 (540) | `settings-writes`, `register-write-crc` |
| `ka` | DeCoupleExcessTemp | 551 | p. 66, Hydraulic separator / exchanger | 65000 (331 / 551) | `survey-reads` |
| `ka` | DeCoupleMinTemp | 552 | p. 66, Hydraulic separator / exchanger | 64999 (332 / 552) | `settings-writes`, `register-write-crc` |
| `ka` | DeCoupleMaxTemp | 553 | p. 66, Hydraulic separator / exchanger | 64998 (333 / 553) | `survey-reads` |
| `ka` | CalorifierExcessTemp | 561 | p. 66, Buffer | 64995 (341 / 561) | `survey-reads` |
| `ka` | CalorifierSwitchDiff | 562 | p. 66, Buffer | 64994 (342 / 562) | `settings-writes`, `register-write-crc` |
| `ka` | DHWSetpoint | 572 | p. 66, Hot water | 19 (351 / 572) | `settings-writes`, `ka-reads` |
| `ka` | DHWSetbackTemp | 573 | p. 66, Hot water | 650 (573) | `survey-reads` |
| `ka` | DHWSwitchDiff | 575 | p. 66, Hot water | 320 (354 / 575) | `settings-writes`, `register-write-crc` |
| `ka` | DHWExcessTemp | 576 | p. 66, Hot water | 45 (355 / 576) | `ka-reads` |
| `ka` | DHWLoadTime | 577 | p. 66, Hot water | 384 (577) | `settings-writes`, `register-write-crc` |
| `ka` | DHWLegionellaDay | 579 | p. 66, Hot water | 257 (356 / 579) | `choice-date-program-writes` |
| `ka` | LegionellaSetpoint | 580 | p. 66, Hot water | 1415 (580) | `settings-writes`, `register-write-crc` |
| `ka` | LegionellaStartTime | 581 | p. 66, Hot water | 65012 (580) | `survey-reads` |
| `ka` | CircWithLegionella | 582 | p. 66, Hot water | 5107 (581) | `choice-date-program-writes` |
| `ka` | LegionellaCirculationTime | 583 | p. 66, Hot water | 2481 (582) | `settings-writes`, `register-write-crc` |
| `ka` | SummerTimeStartDay | 593 | p. 66, Date | 64990 (593) | `survey-reads` |
| `ka` | SummerTimeStartMonth | 593 | p. 66, Date | 64991 (593) | `survey-reads` |
| `ka` | SummerTimeEndDay | 594 | p. 66, Date | 64992 (594) | `survey-reads` |
| `ka` | SummerTimeEndMonth | 594 | p. 66, Date | 64993 (594) | `survey-reads` |

### WCM-FS 2.0 room unit and WCM-EM 2.1 module (`wcm-fs-2`, document 83277504)

| Circuits | Message | Code | Manual (page, menu) | Form register | Record of the message |
|---|---|---|---|---|---|
| `fs1`, `fs2`, `fs3`, `em2`, `em3` | RoomNormalTemp | P112 | p. 32, Réglage#1 | 5 | `settings-writes`, `room-units-reads`, `heating-modules-reads` |
| `fs1`, `fs2`, `fs3`, `em2`, `em3` | RoomSetbackTemp | P113 | p. 32, Réglage#1 | 8 | `settings-writes`, `room-units-reads`, `room-units-shared-store`, `heating-modules-reads` |
| `fs1`, `fs2`, `fs3`, `em2`, `em3` | RoomFrostProtectionTemp | P118 | p. 32, Réglage#1 | 2580 | `settings-writes`, `room-units-reads`, `room-units-shared-store`, `heating-modules-reads` |
| `fs1`, `fs2`, `fs3` | DHWSetpoint | P132 | p. 32, ECS | 19 | `settings-writes` |
| `fs1`, `fs2`, `fs3` | DHWSetbackTemp | P133 | p. 32, ECS | 650 | `survey-reads` |
| `fs1`, `fs2`, `fs3` | HolidayStartDay | P141 | p. 32, Vacances | 283 | `holiday-dates` |
| `fs1`, `fs2`, `fs3` | HolidayStartMonth | P141 | p. 32, Vacances | 284 | `holiday-dates` |
| `fs1`, `fs2`, `fs3` | HolidayStartThird | P141 | p. 32, Vacances | 285 | `holiday-dates` |
| `fs1`, `fs2`, `fs3` | HolidayEndDay | P141 | p. 32, Vacances | 286 | `holiday-dates` |
| `fs1`, `fs2`, `fs3` | HolidayEndMonth | P141 | p. 32, Vacances | 287 | `holiday-dates` |
| `fs1`, `fs2`, `fs3` | HolidayEndThird | P141 | p. 32, Vacances | 288 | `holiday-dates` |
| `fs1`, `fs2`, `fs3` | HolidayTempLevel | P142 | p. 32, Vacances | 317 | `choice-date-program-writes` |
| `fs1`, `fs2`, `fs3` | SummerTimeStartDay | P153 | p. 32, Date | 64990 | `survey-reads` |
| `fs1`, `fs2`, `fs3` | SummerTimeStartMonth | P153 | p. 32, Date | 64991 | `survey-reads` |
| `fs1`, `fs2`, `fs3` | SummerTimeEndDay | P154 | p. 32, Date | 64992 | `survey-reads` |
| `fs1`, `fs2`, `fs3` | SummerTimeEndMonth | P154 | p. 32, Date | 64993 | `survey-reads` |
| `fs1`, `fs3` | ControlVariation | P315 | p. 36, Mise en service | 321 | `room-units-control-variation` |
| `fs1`, `fs2`, `fs3` | FrostProtectionLimitTemp | P502 | p. 38, Comport. régul | 702 | `settings-writes`, `room-units-reads` |
| `fs1`, `fs2`, `fs3` | SwitchOnRuntime | P503 | p. 38, Comport. régul | 272 | `settings-writes`, `room-units-reads` |
| `fs1`, `fs2`, `fs3` | DHWMaxTemp | P601 | p. 39, ECS | 385 | `survey-reads` |
| `fs1`, `fs2`, `fs3` | DHWLegionellaDay | P605 | p. 39, ECS | 257 | `survey-reads` |
| `fs1`, `fs2`, `fs3` | LegionellaSetpoint | P606 | p. 39, ECS | 1415 | `survey-reads` |
| `fs1`, `fs2`, `fs3` | LegionellaCirculationTime | P609 | p. 39, ECS | 2481 | `survey-reads` |
| `em2`, `em3` | CirculationReturnSetTemp | P610 | p. 39, ECS | 1193 | `survey-reads` |

### WTC-GB boiler automat (`wtc-gb`, document 83251704)

| Circuits | Message | Field | Code | Manual (page, menu) | Form row | Record of the message |
|---|---|---|---|---|---|---|
| `bc1`, `bc2` | SupplyTemp | — | i35 | p. 46, Info | — | `bc-info-values` |
| `bc1`, `bc2` | ReturnTemp | — | i37 | p. 47, Info | — | `bc-info-values` |
| `bc1`, `bc2` | FlueGasTemp | — | i31 | p. 46, Info | — | `bc-info-values` |
| `bc1`, `bc2` | OutsideTemp | — | i33 | p. 46, Info | — | `bc-info-values` |
| `bc1`, `bc2` | DHWTemp | — | i34 | p. 46, Info | — | `bc-info-values` |
| `bc1`, `bc2` | HydraulicSeparatorTemp | — | i39 | p. 47, Info | — | `bc-info-values` |
| `bc1`, `bc2` | SoftwareVersionCPU | — | i44 | p. 47, Info | — | `bc-info-values` |
| `bc1`, `bc2` | SoftwareVersionCUI | — | i45 | p. 47, Info | — | `bc-info-values` |
| `bc1`, `bc2` | BurnerServiceHours | — | i46 | p. 47, Info | — | `bc-counters` |
| `bc1`, `bc2` | Counters | burnerstarts | i42 | p. 47, Info | I42 | `bc-counters` |
| `bc1`, `bc2` | Counters | burnerhours | i43 | p. 47, Info | I43 | `bc-counters` |
| `bc1`, `bc2` | Operation | load | i11 | p. 46, Info | I11 | `bc-live-values` |
| `bc1`, `bc2` | Operation | ionisation | i32 | p. 46, Info | I32 | `bc-live-values` |
| `bc1`, `bc2` | Temperatures | fluegastemp | i31 | p. 46, Info | I31 | `bc-live-values` |
| `bc1`, `bc2` | InstallerParameters1 | supplymaxtemp | P31 | p. 49, Parameters | — | `bc-installer-parameters` |
| `bc1`, `bc2` | InstallerParameters1 | supplymintemp | P30 | p. 49, Parameters | — | `bc-installer-parameters` |
| `bc1`, `bc2` | InstallerParameters1 | specialleveltemp | P18 | p. 49, Parameters | — | `bc-installer-parameters` |
| `bc1`, `bc2` | InstallerParameters1 | serviceinterval | P70 | p. 51, Parameters | — | `bc-installer-parameters` |
| `bc1`, `bc2` | InstallerParameters1 | ignitionload | P35 | p. 49, Parameters | — | `bc-installer-parameters` |
| `bc1`, `bc2` | InstallerParameters2 | fluegassafetytemp | P33 | p. 49, Parameters | — | `bc-installer-parameters` |
| `bc1`, `bc2` | InstallerParameters2 | loadmin | P36 | p. 50, Parameters | — | `bc-installer-parameters` |
| `bc1`, `bc2` | InstallerParameters2 | loadmaxheating | P37 | p. 50, Parameters | — | `bc-installer-parameters` |
| `bc1`, `bc2` | InstallerParameters2 | pumploadmin | P44 | p. 50, Parameters | — | `bc-installer-parameters` |
| `bc1`, `bc2` | InstallerParameters2 | pumploadmax | P45 | p. 50, Parameters | — | `bc-installer-parameters` |
| `bc1`, `bc2` | InstallerParameters3 | flowreturndifftemp | P48 | p. 51, Parameters | — | `bc-installer-parameters` |
| `bc1`, `bc2` | InstallerParameters3 | pumprunonheating | P41 | p. 50, Parameters | — | `bc-installer-parameters` |
| `bc1`, `bc2` | InstallerParameters3 | dhwboosttemp | P50 | p. 51, Parameters | — | `bc-installer-parameters` |
| `bc1`, `bc2` | InstallerParameters4 | loadmaxdhw | P38 | p. 50, Parameters | — | `bc-installer-parameters` |
| `bc1`, `bc2` | InstallerParameters4 | pumploaddhw | P46 | p. 50, Parameters | — | `bc-installer-parameters` |
| `bc1`, `bc2` | InstallerParameters4 | pumprunondhw | P42 | p. 50, Parameters | — | `bc-installer-parameters` |
| `bc1`, `bc2` | InstallerParameters5 | boileraddress | P12 | p. 48, Parameters | — | `bc-installer-parameters` |

## Codes of lot 2

Lot 2 took the 107 messages that `weishaupt-1.4.0` listed open for an unread manual page (the
34 circuit pairs were out of scope) and read the pages the study names, through the document
store, French editions, on 2026-11-27: system manager 83258404 pp. 33–46 (standard info
display, user level of the direct circuit #1), 50–62 (installer level of the direct circuit
#1), 65–71 (installer menu tables, configuration views), 82–86 and 92–98 (cascade orders, hot
water) and 105–110 (system info, fault history); room unit and module 83277504 pp. 35–39
(installer menu tables) and the chapters they point to (6.5.9 *Info système*, pp. 52–53; the
module menus pp. 99–100; the standard display p. 28); boiler 83251704 pp. 46–47 (menu
*Info*). The service tool's form prints no number for any register of lot 2 except the one
named under `DHWLoadingPriority` below.

Outcome: **77 messages and 2 fields coded** (79 codes), **14 messages still open** (3 circuit
pairs, 10 for the display, 1 mismatch), and **16 found to have no number in any menu** of the
manuals, so no longer listed open.

### The direct circuit of the system manager

The direct circuit #1 of the WCM-KA has its own user level (`Utilisateur #1`, 111–118, 141,
142, pp. 37–46) and installer level (`Installateur #1`, 311–413, pp. 51–62), both in document
83258404, so its codes are in scheme `wcm-ka-3`; no new scheme is needed. They are set on the
manager's display, not on a room unit's: address `50` (`em1`) is that circuit (same device as
`15`, `heating-modules-reads.md`, `em1-clock-program.md`), and address `15` (`ka`) answers the
same registers 5, 8 and 0x0028 with the same values. The direct circuit numbers its settings
differently from a room unit (scheme `wcm-fs-2`): 116 is its slope, 117 its frost protection
room temperature and 118 its summer / winter changeover, where a room unit has P117 slope,
P118 frost protection and P119 changeover. The scheme keeps them apart.

| Circuits | Message | Code | Manual (page, menu) | Fit with the definition |
|---|---|---|---|---|
| `ka`, `em1` | RoomNormalTemp | 112 | pp. 37, 39, *Réglage #1* | *Ambiance normale*, 16.0–35.0 °C, factory 21.5: the range of `em1` |
| `ka`, `em1` | RoomSetbackTemp | 113 | pp. 37, 40, *Réglage #1* | *Ambiance réduite*, 10.0–21.5 °C, factory 16.0: the range noted in `50.w.em1.tsp` |
| `em1` | GradientCurve | 116 | pp. 37, 44, *Réglage #1* | *Pente*, 2.5–40.0 (type *Universel*), factory 10.0: the range noted in `50.w.em1.tsp` |
| `em1` | RoomFrostProtectionTemp | 117 | pp. 37, 45, *Réglage #1* | *Ambiance antigel*, 4.0–16.0 °C, factory 10.0: same range |
| `em1` | SummerWinterChangeOverTemp | 118 | pp. 37, 46, *Réglage #1* | *Commut. Été/hiver*, 8.0–30.0 °C or off, factory 20.0: same range |
| `em1` | SupplyMinTemp | 341 | pp. 53, 57, *Circuit direct #1* | *min départ*, factory 8.0 °C; the manual bounds it by 342 (8.0–75.0 on the screen), the definition by 8–82 |
| `ka`, `em1` | SupplyMaxTemp | 342 | pp. 53, 55, 57, *Circuit direct #1* | *Max départ*, 8.0–82.0 °C (upper bound by circuit type, p. 55), factory 75.0: same range |
| `em1` | ErrorCode | 608 | pp. 67, 110, *Info système* | *Historique défauts*: ten entries with origin, code, date and time; code 00 when a fault clears |
| `em1` | ErrorType | 608 | pp. 67, 110, *Info système* | the same entry (the selector `ErrorId` has no number: it is the scroll of the display) |
| `em1` | ErrorDevice | 608 | pp. 67, 110, *Info système* | origin of the entry (`KA#` in the manual's example) |
| `em1` | ErrorMinute | 608 | pp. 67, 110, *Info système* | time of the entry |
| `em1` | ErrorHour | 608 | pp. 67, 110, *Info système* | time of the entry |
| `em1` | ErrorDay | 608 | pp. 67, 110, *Info système* | date of the entry |
| `em1` | ErrorMonth | 608 | pp. 67, 110, *Info système* | date of the entry |
| `em1` | ErrorYear | 608 | pp. 67, 110, *Info système* | date of the entry |

The fault log of `em1` (`em1-fault-log.md`) is the manager's: `50` is the manager itself, and
the manual keeps one history, under 608 of the manager's installer menu. The direct-circuit
level has no fault history of its own.

### System info and cascade of the system manager

| Circuit | Message | Code | Manual (page, menu) | Fit with the definition |
|---|---|---|---|---|
| `ka` | HeatDemandTemp | 602 | pp. 67, 109, *Info système* | *T° cons*, the system setpoint temperature; the form names register 2 the same way; read 59.6 and 35.7 °C (`ka-reads.md`) |
| `ka` | OutsideTemp | 601 | pp. 67, 109, *Info système* | *Extérieur, actuel*: the current outside temperature (sensor B1) |
| `ka` | OutsideWeightedTemp | 601 | pp. 67, 109, *Info système* | *Extérieur, pondéré*: the weighted outside temperature |
| `ka` | ModulationStatus | 603 | pp. 67, 109, *Info système* | *Modulation*: the current modulation degree, % |
| `ka` | DeCoupleTemp | 604 | pp. 67, 109, *Info système* | *Info KA, Casse pression* / *Secondaire échangeur*: sensor B22 |
| `ka` | PlateExchangerPrimaryTemp | 604 | pp. 67, 109, *Info système* | *Info KA, Primaire échangeur*: sensor B24 (p. 109; see the conflict below) |
| `ka` | DHWTemp | 605 | pp. 67, 109, *Info système* | *E C S*: the hot-water temperature |
| `ka` | VersionMajor | 609 | pp. 67, 109, *Info système* | *Version WCM-KA*: software version, one code on its two parts |
| `ka` | VersionMinor | 609 | pp. 67, 109, *Info système* | the same version, minor part |
| `ka` | BoilerSequence1First | 533 | pp. 65, 82, *Cascade* | *Ordre casc 1*, factory `A B C D`: the boilers in their order, one code on its positions |
| `ka` | BoilerSequence1Second | 533 | pp. 65, 82, *Cascade* | the same order, second position |
| `ka` | BoilerSequence2First | 534 | pp. 65, 83, *Cascade* | *Ordre casc 2*, factory `D C B A` |
| `ka` | BoilerSequence2Second | 534 | pp. 65, 83, *Cascade* | the same order, second position |

The outside values are shown a second time on the direct-circuit level (411, *Extérieur*, p.
62), and the circuit and system setpoints under 413 (*Info HK*). Those numbers are the same
values seen from the direct circuit; only the manager's own 6xx are published, one code per
message.

### Room units and modules

| Circuits | Message | Code | Manual (page, menu) | Fit with the definition |
|---|---|---|---|---|
| `fs1`, `fs2`, `fs3` | OutsideTemp | P331 | pp. 36, 52, *Info système* | *Extérieur, Actuel*: current outside temperature |
| `fs1`, `fs2`, `fs3` | OutsideWeightedTemp | P331 | pp. 36, 52, *Info système* | *Extérieur, Pondéré*: the weighted value used as reference |
| `fs1`, `fs2`, `fs3` | OutsideMixedTemp | P331 | pp. 36, 52, *Info système* | *Extérieur, Mélangé*: outside temperature with the building's characteristics |
| `fs1`, `fs2`, `fs3` | RoomTemp | P522 | p. 39, *Info CircuitChauf.* | *T. Ambiance*, °C, also the main line of the standard display (p. 28); one room sensor per unit, so the same number on both circuits of the unit for circuits 1 and 2 |
| `fs1`, `fs2`, `fs3` | VersionMajor | P339 | pp. 36, 52, *Info système* | *Version WCM-FS*: software version of the unit, one code on its two parts |
| `fs1`, `fs2`, `fs3` | VersionMinor | P339 | pp. 36, 52, *Info système* | the same version, minor part |
| `fs1`, `fs2`, `fs3` | ErrorCode | P338 | pp. 36, 52–53, *Info système* | *Historique des défauts*: ten entries with origin, code, date and time |
| `fs1`, `fs2`, `fs3` | ErrorType | P338 | pp. 36, 52–53, *Info système* | the same entry |
| `fs1`, `fs2`, `fs3` | ErrorDevice | P338 | pp. 36, 52–53, *Info système* | origin of the entry (`WTC-G#1` in the example) |
| `fs1`, `fs2`, `fs3` | ErrorMinute | P338 | pp. 36, 52–53, *Info système* | time of the entry |
| `fs1`, `fs2`, `fs3` | ErrorHour | P338 | pp. 36, 52–53, *Info système* | time of the entry |
| `fs1`, `fs2`, `fs3` | ErrorDay | P338 | pp. 36, 52–53, *Info système* | date of the entry |
| `fs1`, `fs2`, `fs3` | ErrorMonth | P338 | pp. 36, 52–53, *Info système* | date of the entry |
| `fs1`, `fs2`, `fs3` | ErrorYear | P338 | pp. 36, 52–53, *Info système* | date of the entry |
| `em2`, `em3` | VersionMajor | P341 | pp. 36, 52, *Info système* of the room unit | *Version WCM-EM* (p. 99: *Version EM-Chauff.#X*): software version of the module |
| `em2`, `em3` | VersionMinor | P341 | pp. 36, 52, *Info système* of the room unit | the same version, minor part |

P331, P338 and P339 are values of the unit, not of a circuit: the unit for circuits 1 and 2
shows them once, so `fs2` takes the same number as `fs1` (unlike the circuit pairs).

### Boiler

| Circuits | Message | Field | Code | Manual (page, menu) | Fit with the definition |
|---|---|---|---|---|---|
| `bc1`, `bc2` | Operation | pumpspeed | i22 | p. 46, *Info* | *Puissance circulateur*, %: the pump speed, 50–51 % while firing (`boiler-firing-values.md`) |

`Operation` was coded on its fields in lot 1 (i11, i32); i22 completes it.

### Conflicts found in lot 2

1. **`ka/DHWLoadingPriority` and 571** (mismatch, stays open). The study pointed at 571 for
   it. 571 is *Variante ECS* (p. 94): where the hot-water tank sits (after the hydraulic
   separator, the plate exchanger or the buffer), factory *Casse-pression*; our message reads
   register 0x0023 with the values Priority / Sliding / Parallel. The service tool's form gives
   571 (*DHW variant*) to another register, 309 (`35 01`, `register-candidates.csv`). The
   direct-circuit menus (111–118, 311–413) have no hot-water priority. No number fits.
2. **Sensor letters of the plate exchanger.** The direct-circuit system info (412, p. 62)
   prints the primary side as B22 and the secondary as B24; the manager's system info (604,
   p. 109) prints primary B24 and secondary B22, as does the configuration view (513, p. 70:
   "sensors B22 and B24"). The definitions follow p. 109 (`DeCoupleTemp` B22,
   `PlateExchangerPrimaryTemp` B24); the code, 604, is the same either way.
3. **`em1/SupplyMinTemp` range.** The manual bounds 341 by 342 (screen 8.0–75.0 °C, p. 57);
   the definition carries the fixed range 8–82. The meaning and the factory value agree; the
   upper bound of the definition is the wider one. Not changed in this lot (a range is a
   definition matter, `settings-writes.md`).

### Still open after lot 2

| Circuits | Message | Reason | Why |
|---|---|---|---|
| `fs1`, `fs2`, `fs3` | SupplyHCSetTemp | circuit-pair | *Temp. Consigne* of P526 (circuit 1) or P527 (circuit 2), p. 39: one number per heating circuit, settled with the 34 pairs at the display of the unit for circuits 1 and 2 |
| `fs1`, `fs2`, `fs3` | HeatDemandTemp | display | P337 *Temp Cons syst* (p. 36, "current system setpoint temperatures") or the *Temp Cons syst* of P526 / P527 (p. 39); neither is described further. Compare with the display |
| `em2`, `em3` | SupplyHCSetTemp | display | P526 / P527 *Temp. Consigne*, or the unnumbered *Temp. Consigne#X* of a module without a room unit (p. 99); not described |
| `em2`, `em3` | SupplyHCTemp | display | P523 *Départ#2* (p. 39; *Départ#X*, p. 99) is very likely the flow temperature of the module's circuit (sensor B6), but the manual does not say so |
| `bc1`, `bc2` | FanOperation | display | i23 *Vitesse du ventilateur*, 1/min x 10 (p. 46): one speed, where the message carries set speed, actual speed and PWM; the raw value (23 while firing) is on no stated scale. Compare i23 with the fields while a boiler fires |
| `ka` | ConfigStatus | display | candidate 513 *Conf WCM-KA* (p. 70), a view of the cascade configuration (separator or exchanger, hot water by the cascade or one boiler, buffer with one or two sensors, N1 as 4–20 mA or 2–10 V); the read value 76 is not compared with that view |
| `ka` | DHWLoadingPriority | mismatch | conflict 1 above |
| `fs1`, `fs2`, `fs3`, `em2`, `em3` | OperatingMode | display | added 2026-11-27 with the definition: candidate P111 *Mode Fct Chauf* (83277504 p. 32; the second circuit's heating function also shows 111, p. 98); the tie of register `12 01` to that setting rests on the value 11 ([operating-mode.md](operating-mode.md)). Compare at the display (item 12 of the owner's checklist) |

### No number in any menu (no longer open)

The study listed these as covered by a manual menu. The full menu tables of the three manuals
(83258404 pp. 37, 53, 65–67; 83277504 pp. 32, 36–39; 83251704 pp. 46–51) give them no number:

- `ka/ErrorStatus` (the pending fault, shown as *Défaut* on the standard info display, p. 33,
  without a number; 608 is the history) and `ka/DHWSetValue` (the hot-water setpoint in
  effect; the menus number only the settings 572 and 573).
- `em1/BoilerMCBoostTemp`: the direct circuit has no mixer and its menus no boost; the room
  unit's P424 / P464 (*Elév. Circ mélan*) belong to a mixer circuit (they are among the
  circuit pairs of `em2`, `em3`, `fs1`–`fs3`).
- `bc1/EventCounters`, `bc2/EventCounters`: hours and ignitions of the day, switch-ons, resets
  and shut-offs are not in the boiler's *Info* menu (i10–i46), which counts only starts (i42)
  and hours (i43).
- `fs1/RoomSetpointTemp`, `fs2/RoomSetpointTemp`, `fs3/RoomSetpointTemp` (the room setpoint
  in effect), `fs1/FloorDryingTemp`, `em2/FloorDryingTemp` (P442 shows the floor-drying day and
  its setpoint, not a measured temperature, p. 72), `fs1/RoomThermostatTemp`,
  `em2/RoomThermostatTemp` (P505 / P506 are switching differentials), `em2/MixerPump`,
  `em3/MixerPump` (the pump state appears only on the output test screen P403 and on the
  module's LEDs) and `em2/H1Status`, `em3/H1Status` (P401 sets the function of H1; its state is
  not shown).

## Left open

`open.vendor_codes` of the metadata lists the messages a manual menu covers but whose code is
not established. No code may sit on them (the check fails).

- **Circuit pairs (34 messages, owner's decision 3).** The form and the manual give two
  numbers per register, one per heating circuit (P117 / P123 slope, P119 / P124 summer/winter,
  P421–P425 / P461–P465 flow limits, hot-water priority, boost and mixer, P313 / P314,
  P315 / P316). The manual (83277504, pp. 32, 36–38) gives the second number to circuit 2 of a
  unit that drives circuits 1 and 2 (*Réglage #2 (pour WCM-FS#1+2)*). One look at the display
  of that unit settles which applies where: `fs1/HeatingCircuitType`, `fs1/DHWLoadingPriority`, `fs1/GradientCurve`, `fs1/SummerWinterChangeOverTemp`, `fs1/SupplyMaxTemp`, `fs1/SupplyMinTemp`, `fs1/BoilerMCBoostTemp`, `em2/BoilerMCBoostTemp`, `em2/MixerParameter`, `em2/GradientCurve`, `em2/SummerWinterChangeOverTemp`, `em2/SupplyMaxTemp`, `em2/SupplyMinTemp`, `em3/GradientCurve`, `em3/SummerWinterChangeOverTemp`, `em3/SupplyMaxTemp`, `em3/SupplyMinTemp`, `em3/BoilerMCBoostTemp`, `em3/MixerParameter`, `fs2/HeatingCircuitType`, `fs2/DHWLoadingPriority`, `fs2/GradientCurve`, `fs2/SummerWinterChangeOverTemp`, `fs2/SupplyMaxTemp`, `fs2/SupplyMinTemp`, `fs2/BoilerMCBoostTemp`, `fs2/ControlVariation`, `fs3/HeatingCircuitType`, `fs3/DHWLoadingPriority`, `fs3/GradientCurve`, `fs3/SummerWinterChangeOverTemp`, `fs3/SupplyMaxTemp`, `fs3/SupplyMinTemp`, `fs3/BoilerMCBoostTemp`.
- **After lot 2 (14 messages)**: 3 more circuit pairs (`fs1`, `fs2`, `fs3` `SupplyHCSetTemp`,
  P526 / P527), 10 messages whose candidate number only the display can confirm (reason
  `display`) and 1 whose manual number means another setting (`mismatch`), each with its
  reason in "Still open after lot 2" above: `bc1/FanOperation`, `ka/ConfigStatus`,
  `ka/DHWLoadingPriority`, `bc2/FanOperation`, `fs1/HeatDemandTemp`, `fs1/SupplyHCSetTemp`,
  `em2/SupplyHCSetTemp`, `em2/SupplyHCTemp`, `em3/SupplyHCSetTemp`, `em3/SupplyHCTemp`,
  `fs2/HeatDemandTemp`, `fs2/SupplyHCSetTemp`, `fs3/HeatDemandTemp`, `fs3/SupplyHCSetTemp`.
- Not open, no vendor code (27): status broadcasts, the standard heat demand `05 07`, the
  boiler status telegrams of the manager, the mode bit fields, the fault-log pointers and the
  clock registers of `em1`: `bc1/PowerDemand`, `bc1/FaultHistoryPointer`, `ka/Boiler1Status`, `ka/Boiler1Power`, `ka/Boiler2Status`, `ka/Boiler2Power`, `bc2/PowerDemand`, `bc2/FaultHistoryPointer`, `fs1/PowerDemand`, `fs1/ErrorId`, `em1/HcMode`, `em1/SystemWeekday`, `em1/SystemDay`, `em1/SystemMonth`, `em1/SystemYear`, `em1/SystemHour`, `em1/SystemMinute`, `em1/SystemSecond`, `em1/ErrorId`, `em2/HcMode`, `em3/HcMode`, `fs2/PowerDemand`, `fs2/ErrorId`, `fs3/PowerDemand`, `fs3/ErrorId`, `broadcast/KaStatus`, `broadcast/Datetime`. Program slots, fault counters and fault history
  are outside lots 1 and 2 (fault numbers are another numbering). Lot 2 adds 16 messages
  with no number in any menu ("No number in any menu" above), 43 in all.

## Left out

Numberings known only from a third party are not published (owner's decision 6): the
WcmToMqtt gateway names room-unit registers 5, 4 and 2586 `413`, `416` and `412` (the
room-unit manual numbers register 5 P112); the WTC 25-A numbers our P44 / P45 P42 / P43. They
are recorded in `second-installation-ebus2mqtt.md`, not here.

## Equipment and date

Two WTC-GB boilers in cascade (automat software 1104), a system manager WCM-KA 3.0, two heating
modules WCM-EM 2.1 and two room units WCM-FS 2.0 (one of them for circuits 1 and 2, so three
room-unit addresses). The codes come from documents and the service tool's form, not from a
bus read; the bus reads that established each message are in the records of the last column.
Manual pages read 2026-11-27.

## Not verified

- Which of the two numbers of a circuit pair a unit for circuits 1 and 2 shows (open, above).
- The ten `display` messages of lot 2: which candidate number the display shows for them
  (`HeatDemandTemp` of the room units, the flow values of the modules, i23 against
  `FanOperation`, 513 against `ka/ConfigStatus`).
- Lot 2 reads the manuals only: no display was looked at and no bus was read for it. The fit
  of each code rests on the meaning, range and factory value printed in the manual against
  the definition and its record.
- The codes on the boilers are those of the WTC-GB manual 83251704. Another boiler series that
  answers the same reads may number them differently (scheme `wtc-gb` only).
- Only the French editions were read for this record; the English editions were not compared
  parameter by parameter.
