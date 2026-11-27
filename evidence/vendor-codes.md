# Vendor codes: the number a vendor document prints for a value

## What

The metadata of a release names every value by circuit, message and field, and gives it a
label. The vendor manuals and the controller displays name the same value by a number:
parameter 535 on the system manager, P112 on a room unit, P31 or i35 on a boiler. This record
is the source (rule 3) of the vendor codes of the metadata sidecar (`metadata/weishaupt.toml`,
tables `[vendor_schemes]`, `[[vendor_code]]` and `[[vendor_open]]` on the `weishaupt` branch of
the configuration fork), lot 1 of the study `docs/design-vendor-codes.md`, decided by the owner
on 2026-11-27. Format in `docs/companion-contract.md`, "Vendor codes".

Lot 1: **136 messages**, 44 of their fields among them, **164 codes**:

| Device | Circuits | Messages | Codes on the message | Codes on fields |
|---|---|---|---|---|
| boilers | `bc1`, `bc2` | 17 each | 9 each (i-codes of the register reads) | 22 each, on 8 memory reads |
| system manager | `ka` | 26 | 26 | — |
| room units | `fs1`, `fs3`; `fs2` | 23 each; 22 | 23 each; 22 | — |
| heating modules | `em2`, `em3` | 4 each | 4 each | — |

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

## Left open

`open.vendor_codes` of the metadata lists the messages a manual menu covers but whose code is
not established. No code may sit on them (the check fails).

- **Circuit pairs (34 messages, owner's decision 3).** The form and the manual give two
  numbers per register, one per heating circuit (P117 / P123 slope, P119 / P124 summer/winter,
  P421–P425 / P461–P465 flow limits, hot-water priority, boost and mixer, P313 / P314,
  P315 / P316). The manual (83277504, pp. 32, 36–38) gives the second number to circuit 2 of a
  unit that drives circuits 1 and 2 (*Réglage #2 (pour WCM-FS#1+2)*). One look at the display
  of that unit settles which applies where: `fs1/HeatingCircuitType`, `fs1/DHWLoadingPriority`, `fs1/GradientCurve`, `fs1/SummerWinterChangeOverTemp`, `fs1/SupplyMaxTemp`, `fs1/SupplyMinTemp`, `fs1/BoilerMCBoostTemp`, `em2/BoilerMCBoostTemp`, `em2/MixerParameter`, `em2/GradientCurve`, `em2/SummerWinterChangeOverTemp`, `em2/SupplyMaxTemp`, `em2/SupplyMinTemp`, `em3/GradientCurve`, `em3/SummerWinterChangeOverTemp`, `em3/SupplyMaxTemp`, `em3/SupplyMinTemp`, `em3/BoilerMCBoostTemp`, `em3/MixerParameter`, `fs2/HeatingCircuitType`, `fs2/DHWLoadingPriority`, `fs2/GradientCurve`, `fs2/SummerWinterChangeOverTemp`, `fs2/SupplyMaxTemp`, `fs2/SupplyMinTemp`, `fs2/BoilerMCBoostTemp`, `fs2/ControlVariation`, `fs3/HeatingCircuitType`, `fs3/DHWLoadingPriority`, `fs3/GradientCurve`, `fs3/SummerWinterChangeOverTemp`, `fs3/SupplyMaxTemp`, `fs3/SupplyMinTemp`, `fs3/BoilerMCBoostTemp`.
- **Lot 2 (107 messages)**, a code in a manual menu but not read yet: the manager's own circuit
  `em1` (its user and installer levels, 83258404 pp. 35–37 and 51–53), the info values and
  versions of the manager (601–609) and of the room units and modules (P331, P337–P341,
  P521–P527), the cascade orders 533 / 534, the direct-circuit settings and the hot-water
  priority of `ka`, the fan and pump speeds of the boilers (i22, i23): `bc1/EventCounters`, `bc1/FanOperation`, `ka/ErrorStatus`, `ka/HeatDemandTemp`, `ka/DHWSetValue`, `ka/OutsideTemp`, `ka/DeCoupleTemp`, `ka/DHWTemp`, `ka/ConfigStatus`, `ka/OutsideWeightedTemp`, `ka/VersionMajor`, `ka/VersionMinor`, `ka/RoomNormalTemp`, `ka/RoomSetbackTemp`, `ka/DHWLoadingPriority`, `ka/ModulationStatus`, `ka/SupplyMaxTemp`, `ka/BoilerSequence1First`, `ka/BoilerSequence1Second`, `ka/BoilerSequence2First`, `ka/BoilerSequence2Second`, `ka/PlateExchangerPrimaryTemp`, `bc2/EventCounters`, `bc2/FanOperation`, `fs1/HeatDemandTemp`, `fs1/SupplyHCSetTemp`, `fs1/OutsideTemp`, `fs1/OutsideWeightedTemp`, `fs1/RoomTemp`, `fs1/FloorDryingTemp`, `fs1/RoomThermostatTemp`, `fs1/RoomSetpointTemp`, `fs1/OutsideMixedTemp`, `fs1/VersionMajor`, `fs1/VersionMinor`, `fs1/ErrorCode`, `fs1/ErrorType`, `fs1/ErrorDevice`, `fs1/ErrorMinute`, `fs1/ErrorHour`, `fs1/ErrorDay`, `fs1/ErrorMonth`, `fs1/ErrorYear`, `em1/RoomNormalTemp`, `em1/RoomSetbackTemp`, `em1/RoomFrostProtectionTemp`, `em1/GradientCurve`, `em1/SummerWinterChangeOverTemp`, `em1/SupplyMaxTemp`, `em1/SupplyMinTemp`, `em1/BoilerMCBoostTemp`, `em1/ErrorCode`, `em1/ErrorType`, `em1/ErrorDevice`, `em1/ErrorMinute`, `em1/ErrorHour`, `em1/ErrorDay`, `em1/ErrorMonth`, `em1/ErrorYear`, `em2/SupplyHCSetTemp`, `em2/SupplyHCTemp`, `em2/MixerPump`, `em2/H1Status`, `em2/FloorDryingTemp`, `em2/RoomThermostatTemp`, `em2/VersionMajor`, `em2/VersionMinor`, `em3/SupplyHCSetTemp`, `em3/SupplyHCTemp`, `em3/MixerPump`, `em3/H1Status`, `em3/VersionMajor`, `em3/VersionMinor`, `fs2/HeatDemandTemp`, `fs2/SupplyHCSetTemp`, `fs2/OutsideTemp`, `fs2/OutsideWeightedTemp`, `fs2/RoomTemp`, `fs2/RoomSetpointTemp`, `fs2/OutsideMixedTemp`, `fs2/VersionMajor`, `fs2/VersionMinor`, `fs2/ErrorCode`, `fs2/ErrorType`, `fs2/ErrorDevice`, `fs2/ErrorMinute`, `fs2/ErrorHour`, `fs2/ErrorDay`, `fs2/ErrorMonth`, `fs2/ErrorYear`, `fs3/HeatDemandTemp`, `fs3/SupplyHCSetTemp`, `fs3/OutsideTemp`, `fs3/OutsideWeightedTemp`, `fs3/RoomTemp`, `fs3/RoomSetpointTemp`, `fs3/OutsideMixedTemp`, `fs3/VersionMajor`, `fs3/VersionMinor`, `fs3/ErrorCode`, `fs3/ErrorType`, `fs3/ErrorDevice`, `fs3/ErrorMinute`, `fs3/ErrorHour`, `fs3/ErrorDay`, `fs3/ErrorMonth`, `fs3/ErrorYear`.
- Not open, no vendor code (27): status broadcasts, the standard heat demand `05 07`, the
  boiler status telegrams of the manager, the mode bit fields, the fault-log pointers and the
  clock registers of `em1`: `bc1/PowerDemand`, `bc1/FaultHistoryPointer`, `ka/Boiler1Status`, `ka/Boiler1Power`, `ka/Boiler2Status`, `ka/Boiler2Power`, `bc2/PowerDemand`, `bc2/FaultHistoryPointer`, `fs1/PowerDemand`, `fs1/ErrorId`, `em1/HcMode`, `em1/SystemWeekday`, `em1/SystemDay`, `em1/SystemMonth`, `em1/SystemYear`, `em1/SystemHour`, `em1/SystemMinute`, `em1/SystemSecond`, `em1/ErrorId`, `em2/HcMode`, `em3/HcMode`, `fs2/PowerDemand`, `fs2/ErrorId`, `fs3/PowerDemand`, `fs3/ErrorId`, `broadcast/KaStatus`, `broadcast/Datetime`. Program slots, fault counters and fault history
  are outside lot 1 (fault numbers are another numbering).

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
- The codes on the boilers are those of the WTC-GB manual 83251704. Another boiler series that
  answers the same reads may number them differently (scheme `wtc-gb` only).
- Only the French editions were read for this record; the English editions were not compared
  parameter by parameter.
