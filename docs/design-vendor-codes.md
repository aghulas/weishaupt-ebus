# Design note: vendor codes in the metadata

Status: **proposal, 2026-11-27, waiting for the owner's decision.** Nothing is built: the sidecar,
the contract, the schemas and the generator are unchanged.

## The question

The metadata names every value by circuit, message and field (`ka/ModulationMin`) and gives it a
label. The vendor documents and the controller displays name the same value by a number:
parameter 535 on the system manager, P112 on a room unit, P31 or i35 on a boiler. Two other
bridges for this equipment (WcmToMqtt, which reads the vendor network gateway, and
`turbolooser/ebus2mqtt`, which reads the bus with WcmToMqtt-compatible topics) put that number
in their value names: `113-Absenk-Raumtemp`, `117-Steilheit`, `I33-Aussentemperatur`,
`P30-Min-VL-Soll`. The owner decided not to align MQTT topics with them, and asked whether a
per-message vendor code in the metadata would let any tool map the names, and let `ha-weishaupt`
show the display number next to a label.

## Recommendation

Add an optional list `vendor_codes` to a message or a field, each code with the **numbering
scheme** it belongs to and its **source**. Metadata schema 1 stays as it is, so it is a
compatible addition. Fill it in two lots: first the 136 messages (44 fields among them) whose
code is already in a record and agrees with the manual, then, after one manual pass and one
look at a room-unit display, the 141 messages that need it. The cost of lot 1 is one working
session: generator, schema, contract, a new evidence record, tests and a release of the
definitions. Lot 2 is a second session plus about 25 manual pages and five minutes at the
display of the room unit that drives circuits 1 and 2.

A code alone is not enough. The same number means different settings on different devices and
on different boiler series (section 2), so a code is only meaningful with its scheme.

## 1. What is already known

Source of the counts: the metadata of `weishaupt-1.3.2` (687 messages, 2 204 fields), the
compiled CSV of the same release (register of each `50 22` read), joined with
`evidence/register-candidates.csv` on device type and register bytes, the labels and
descriptions of the metadata, and the evidence records. The script is not kept; the join is
reproducible from those two files.

### Where codes come from

| Source | What it gives | Records |
|---|---|---|
| Our own labels and descriptions | i-codes of the boiler registers (`SupplyTemp` "info value i35"), P-numbers of the fields of `InstallerParameters1`–`5`, ten parameters of the system manager, 315 for `ControlVariation` | `bc-info-values`, `bc-installer-parameters`, `survey-reads`, `ka-reads`, `terms` |
| `evidence/register-candidates.csv` | the number the vendor service tool's form prints beside a register (`vendor_param`, 943 of 2 023 rows) | `vendor-software-analysis` |
| Vendor manuals, menu tables | the number the controller display shows | cited by page in `menus.source` and in the records above; read for this study: system manager 83258404 pp. 50–54 and 65–67, room unit and module 83277504 pp. 32–39 |

### Coverage, per message

| Class | Messages | Note |
|---|---|---|
| **Code from a record, agreeing with the manual** (lot 1) | **136** | of which 16 boiler memory reads carry the code on their fields (44 fields) |
| Code needing a manual page or a display look (lot 2) | 141 | 42 have a number in the form that is not settled (two numbers, one per heating circuit, or a room-unit number on the manager's own circuit); 99 have no code in any record, but a manual menu lists them |
| No vendor code | 27 | status broadcasts, the standard heat demand `05 07`, boiler status telegrams of the manager, mode bit fields, pointers |
| Program slots | 357 | the manuals name a program ("Progr chauff.1"), never a slot; a group, not a code |
| Fault history and counters | 26 | their fields carry fault numbers (F57, W22: 66 fields), another numbering than parameters; left out of this proposal |
| **Total** | **687** | |

Counted by device, lot 1: each boiler 17 of its 34 messages (every register read, and every
memory read with a numbered field), the system manager 26 of its 50 (`ka`), each room unit 23
(22 on `fs2`) of its 50 or so non-program messages, each module 4 of its 17 or 19.

### At which level

- **Message**, for a message with one value (almost all register reads): `ka/ModulationMin` is
  535.
- **Field**, for a message that carries several numbered values: `bc1/InstallerParameters1`
  holds P31, P30, P18, P70 and P35 in five fields, `bc1/Counters` holds i43 and i42,
  `bc1/Operation` i11 and i32, `bc1/Temperatures` i31. The message itself has no code.
- **Never both** on the same value. A field code wins; a consumer looks at the field first.
- **One code on several messages** is normal and must be allowed: P141 (holiday) covers the six
  holiday-date registers of a room unit, 593 / 594 and P153 / P154 the day and the month of the
  summer-time dates, 533 / 534 the two boiler positions of each cascade order, 609 / P339 the
  two parts of a version, P338 the nine registers of the last fault. A code is therefore not a
  key: a consumer maps a code to a list of messages.
- **Several codes on one message** may happen (the same register in a user menu and an
  installer menu); none is established on this installation. A list keeps the door open at no
  cost.

### Conflicts found

| Conflict | Messages | Settled? |
|---|---|---|
| The service tool's form gives two numbers per register on the system manager, a 3xx and a 5xx (315 / 535, 317 / 537 …) | 14 | **Yes**: the manual of the WCM-KA 3.0 (83258404, pp. 65–66) lists the cascade, separator, buffer, hot-water and date parameters as 531–594. Its 3xx numbers are the levels of the direct circuit #1 (311 to 413, pp. 51–53) and mean other settings. The 3xx of the form are probably those of an earlier KA; not used. |
| The form is one off from the manual for three hot-water parameters: 581, 582 for `CircWithLegionella`, `LegionellaCirculationTime`, 580 for `LegionellaStartTime` | 3 | **Yes**, by the manual (p. 66): 582 circulation with legionella, 583 circulation time, 581 legionella start time. Our description of `LegionellaStartTime` already says 581. |
| Room units and modules: two numbers per register, one per heating circuit (P117 / P123 slope, P119 / P124 summer/winter, P421–P425 / P461–P465 flow limits, P313 / P314, P315 / P316) | 34 | **No.** The manual (83277504, pp. 32, 36–38) gives the second number to circuit 2 of a unit that drives circuits 1 and 2 ("Réglage #2, pour WCM-FS#1+2"). Here one unit answers at `35` and `75` for circuits 1 and 2 (`room2` shares its store with `room1`): `fs2` is probably the case of the second number, `fs1`, `fs3` and the modules of the first. One look at the display of that unit settles it (open question 3). |
| `em1` (the manager's own circuit at `50`) gets room-unit numbers from the form (P112, P421, P422 …), but its values are set on the manager's display, whose direct-circuit level numbers them 341 (min flow), 342 (max flow) … | 8 | **No.** The user level of the direct circuit (83258404, pp. 35–37) is not read yet. |
| The same number names another setting on another device: 601 (manager: outside temperature info; room unit: hot-water maximum), 341 (manager: min flow of the direct circuit; room unit: version of the module), 315 (room unit: control type; earlier manager form: modulation minimum) | — | Not a conflict once a code carries its scheme. |
| Boiler series: P42 is the hot-water pump run-on on the WTC-GB here, the minimum pump rating on the WTC 25-A of `ebus2mqtt`; P44 / P45 here are P42 / P43 there; the flow temperature is i35 here and I30 there; the time since service i46 here, I45 (label) or I70 (slot) there | — | Recorded in `second-installation-ebus2mqtt.md`; same consequence. |
| WcmToMqtt names the room-unit registers 5, 4 and 2586 `413`, `416` and `412`. The room-unit manual numbers them P112, P526 and P331 | 3 | A numbering of the vendor gateway, not of the display. Known only from a third party: not published here (rule 3). |

## 2. Same code, different devices

The vendor numbers parameters per product and per manual, not across the range:

- **System manager WCM-KA 3.0** (83258404): three digits, no letter on the display. 1xx and 3xx
  are the user and installer levels of the direct circuit #1, 5xx the installer level of the
  manager, 6xx its system info.
- **Room unit WCM-FS 2.0 and module WCM-EM 2.1** (83277504): `P` and three digits. 1xx user
  level, two numbers when one unit drives two circuits; 3xx commissioning and system info; 4xx
  per heating circuit (P42x for circuit #X, P46x for circuit 2 of a unit for circuits 1 and 2);
  5xx control behaviour and circuit info; 6xx hot water. A module has no display: its values
  are shown, and numbered, on the room unit.
- **Boiler automat of the WTC-GB** (83251704): `P` and two digits for the heating specialist,
  `i` and two digits for the info values. Another series (WTC 15-A / 25-A, manual 83247501)
  uses the same letters and many of the same numbers, but not all for the same setting.

So the same number may mean the same setting on several devices (P112, normal room
temperature, on every room unit and module) and another one elsewhere (601). **The field must
be a code plus its scheme**, and the scheme names the document. A tool may match a third-party
name on the code only within one scheme.

## 3. Crosswalk with `ebus2mqtt`

`ebus2mqtt/katalog.py`, commit `d377209` of 2026-11-27, read only (cloned under
`out/ebus2mqtt-vendor-codes/`, not run). It defines 81 value names: 58 compatible with
WcmToMqtt (its `WCM_NAMEN`) and 23 of its own. Its boiler values come from `50 03` display
slots of the WTC 25-A, its circuit values from `50 22` registers of a room unit at `35`.

| Their names | Count | Our message or field | Mapped automatically by a code + scheme? |
|---|---|---|---|
| `I11-Laststellung`, `I31-Abgastemperatur`, `I42-…` and `I43-…` (six names, raw and scaled), `P30-…`, `P31-…`, `P37-…`, `P12-…`, `P33-…`, `P35-…`, `P36-…`, `P41-…`, `P70-…` | 17 | `bcN/Operation.load`, `bcN/FlueGasTemp`, `bcN/Counters.burnerstarts` / `.burnerhours`, `bcN/InstallerParameters1`–`5` fields | **yes**, if the tool accepts WTC 25-A and WTC-GB codes as one scheme for these numbers (they agree in meaning; their scale differs for i42 / i43) |
| `Sondernieveau-Heizbetrieb` (label P18), `113-Absenk-Raumtemp`, `117-Steilheit`, `So-Wi-Umschalttemperatur` (label 119), `Raumfrosttemperatur` (label 118) | 5 | `IP1.specialleveltemp`, `fsN/RoomSetbackTemp`, `GradientCurve`, `SummerWinterChangeOverTemp`, `RoomFrostProtectionTemp` | **yes** (through the number in their name or label) |
| `I33-Aussentemperatur` | 1 | they read it at the room unit, register 12 = our `fsN/OutsideTemp`; i33 is our `bcN/OutsideTemp` | partly: the code lands on the boiler's sensor |
| Same value, numbered differently or not at all: `413-…`, `416-…`, `412-…`, `Vorlauftemperatur` (I30), `Zeit-letzte-Wartung` (I45 / I70), `I10-Betriebsphase`, `I10-Fehler`, `I12-…`, `Hk1-Regelvariante`, `Fussbodenerwaermung`, `151-Datum`, `152-Uhrzeit`, `Flamme`, `Gasventil`, `Pumpe`, `Vorlauf-Broadcast` | 16 | `fsN/RoomNormalTemp`, `SupplyHCSetTemp`, `OutsideMixedTemp`, `bcN/SupplyTemp`, `BurnerServiceHours`, status fields, `ka/ErrorStatus`, `fsN/OutsideWeightedTemp`, `ControlVariation`, `HeatingCircuitType`, `em1/System*` | no: a table by hand (the comparison record already holds most of it) |
| Weekly programs `ZP1-MO` … `ZP3-SO` | 21 | the three slots of one day of `fs1/HCProgram1`–`3` | no code on either side; by structure |
| **False match**: `P42-Pumpenleistung-min` | 1 | our P42 is `IP4.pumprunondhw`; their value is our P44, `IP2.pumploadmin` | **wrong** on a code alone; avoided by the scheme |
| Not defined here: P10, P11, P13, P15, P17, P20, P21, P22, P23, P32, P34, P39, P40, P43, P72, `I13-…`, `111-Betriebsart`, `501-Reduzierbetrieb`, `Brenneranforderung-Heizung`, `Frostschutztemperatur` (same register as our `HolidayTempLevel`, another meaning) | 20 | — | — |

Of 81 names, 61 have a counterpart here: **22 would map automatically** through a code with a
scheme (17 + 5), one more partly, 21 are programs, 16 need a hand table, and one (P42) maps
to our P44 by hand. Without the scheme the 22 come with one wrong mapping (P42). The vendor code helps the boiler and the user-level room
settings, which is where the other tools put numbers in their names; it does not replace a
crosswalk for the rest.

## 4. The field

### In the sidecar (`metadata/weishaupt.toml`)

A new array of tables, beside `[[entry]]`, so that entries that cover several circuits stay
whole and a code can differ by circuit:

```toml
[vendor_schemes.wcm-ka-3]
label = { en = "WCM-KA 3.0 system manager", fr = "Manager de cascade WCM-KA 3.0" }
document = "83258404"

[vendor_schemes.wcm-fs-2]
label = { en = "WCM-FS 2.0 room unit and WCM-EM 2.1 module", fr = "Commande à distance WCM-FS 2.0 et module WCM-EM 2.1" }
document = "83277504"

[vendor_schemes.wtc-gb]
label = { en = "WTC-GB boiler automat", fr = "Automate de la chaudière WTC-GB" }
document = "83251704"

[[vendor_code]]
circuits = ["ka"]
message = "ModulationMin"
code = "535"
scheme = "wcm-ka-3"
source = "system manager manual 83258404, p. 65 (menu Cascade); service tool form, register eb fd"
evidence = "vendor-codes"

[[vendor_code]]
circuits = ["bc1", "bc2"]
message = "InstallerParameters1"
field = "supplymaxtemp"
code = "P31"
scheme = "wtc-gb"
source = "boiler manual 83251704, p. 48"
evidence = "bc-installer-parameters"
```

`code` is written as the manual's parameter table prints it, without a space (`535`, `P112`,
`P31`, `i35`).

### In the generated JSON

```json
"vendor_schemes": {
  "wcm-ka-3": { "label": { "en": "WCM-KA 3.0 system manager", "fr": "Manager de cascade WCM-KA 3.0" }, "document": "83258404" }
},
"messages": {
  "ka/ModulationMin": {
    "…": "…",
    "vendor_codes": [ { "code": "535", "scheme": "wcm-ka-3",
                        "source": "system manager manual 83258404, p. 65 (menu Cascade); service tool form, register eb fd" } ]
  },
  "bc1/InstallerParameters1": {
    "fields": [ { "name": "supplymaxtemp", "…": "…",
                  "vendor_codes": [ { "code": "P31", "scheme": "wtc-gb", "source": "boiler manual 83251704, p. 48" } ] } ]
  }
},
"open": { "…": "…", "vendor_codes": [ "fs2/GradientCurve", "…" ] }
```

- `vendor_codes` is absent where no code is established; `open.vendor_codes` lists the messages
  a manual menu covers but whose code is not yet established (lot 2), as `open.poll` does for
  polling.
- The evidence record of each code is added to the message's `evidence` list, like a write's.

### Source (rule 3)

- A new record, `evidence/vendor-codes.md`: one table per scheme (message, field, code, manual
  page, form row of `register-candidates.csv` where there is one, and how a conflict was
  settled). The pages read for this study go there first. Codes already argued in another
  record (`bc-installer-parameters`, `bc-info-values`) may name that record instead.
- `scripts/metadata.py check` fails when a code has no scheme, an unknown scheme, no source or
  no evidence; when its evidence record does not contain both the message name and the code;
  when a message and one of its fields both carry codes; when a field code names a field the
  message does not have. The same as for write conditions.

### Compatibility with schema 1

Compatible. Precedents: `value_labels`, `absent`, `renamed_from`, `stored_only` were added under
schema 1. Both consumers check only `schema == 1` and read keys by name (`ha-weishaupt`'s model,
`weishaupt2mqtt`'s `model.py`), so an unknown key is ignored. It is a release with a new third
or second number, not a new first number. What changes:

- `docs/companion-contract.md`: `vendor_schemes` in "Structure", a row `vendor_codes` in the
  tables "Message" and "Fields", `open.vendor_codes` in "Left empty", a paragraph on scheme and
  many-to-one.
- `schemas/metadata.schema.json`: the top level and the `message` and `field` definitions have
  `additionalProperties: false`, so three properties are added there, plus a `$defs/vendorCode`
  (`code`, `scheme`, `source`, all required strings) and `$defs/vendorScheme`.
- `scripts/metadata.py`: read `[vendor_schemes]` and `[[vendor_code]]`, expand circuits, attach
  to message or field, the checks above, `open.vendor_codes`; tests under `tests/`.

## 5. What each consumer could do

- **`ha-weishaupt`**: an extra state attribute `vendor_code` (`"535"`, or `"P112"`) on each
  entity, and a column or a prefix in the panel's tables ("535 · Minimum modulation"), which
  is where installers search by number. Entity names and ids stay as they are: a prefix in the
  entity name would rename every entity of an existing installation. With the scheme label as a
  tooltip ("WCM-KA 3.0 system manager"). Search by number in the panel.
- **`weishaupt2mqtt`**: nothing to build. `bridge/metadata` publishes the metadata as it is,
  so the codes reach MQTT with the next definitions release baked into the add-on. Optionally
  the discovery payloads could carry the code in their attributes.
- **A third-party tool** (an ebus2mqtt-style bridge, a dashboard): read `bridge/metadata` or the
  release asset, build `(scheme, code) → [messages / fields]`, and match its own numbered names
  within a scheme. Section 3 says what that buys today: 22 of the 81 names of `ebus2mqtt`.

## 6. Effort

| Lot | Content | Work | Reading |
|---|---|---|---|
| **1** | Generator, schema, contract, tests; `evidence/vendor-codes.md`; **136 messages**: 17 boiler messages × 2 (i-codes on the registers, P- and i-codes on 44 fields), 26 messages of the system manager (5xx, conflicts above settled), 23 per room unit except `fs2/ControlVariation` (P112, P113, P118, P132, P133, P141, P142, P153, P154, P315, P502, P503, P601, P605, P606, P609), 4 per module (P112, P113, P118, P610) | one session, then a definitions release on the owner's word | none left: the pages read for this study are enough |
| **2** | **141 messages**: the circuit pairs of room units and modules (34); `em1` (8); the info values of the manager (601–609) and of the room units (P331, P337, P338, P339, P341, P521–P527); the cascade orders 533 / 534; the direct-circuit settings of `ka` (`SupplyMaxTemp`, `RoomNormalTemp`, `RoomSetbackTemp`); `DHWLoadingPriority` of `ka`; boiler fan and pump speeds (i22, i23) | a second session | see below |
| (3) | Fault numbers of the fault counters and history (66 fields), as their own scheme | not proposed now | — |

Pages for lot 2:

| Document | Pages | For |
|---|---|---|
| System manager WCM-KA 3.0, 83258404 | 35–37 (user level of the direct circuit #1) and 51–53 (installer level #1, read: 341, 342) | `em1` settings, `ka/RoomNormalTemp`, `ka/RoomSetbackTemp`, `ka/SupplyMaxTemp` |
| same | 67 and 105–110 (system info 601–609, fault log) | the live values and versions of `ka`, the fault registers of `em1` |
| same | 92–98 (6.7.14–6.7.16, 6.7.28) | 533 / 534 against `BoilerSequence*`, 571 against `ka/DHWLoadingPriority` |
| Room unit and module, 83277504 | 36 and 39 (P331, P337–P341, P521–P527), with the sections they point to | the live values and versions of the room units and modules |
| Boiler WTC-GB, 83251704 | 46–47 (info i10–i46) | i22, i23 for `Operation.pumpspeed`, `FanOperation`; i10 for the status phase |
| — | the display of the room unit that drives circuits 1 and 2: open Réglage #2 and note whether its slope is P123 | the 34 circuit pairs |

## 7. Decisions for the owner

1. **Go or no go**: add `vendor_codes` (code + scheme + source) under schema 1, lot 1 first?
2. **Level**: message, or field where a message carries several numbered values, never both,
   as proposed?
3. **Circuit pairs**: until the display of the unit for circuits 1 and 2 is looked at, leave
   the 34 paired messages empty (`open.vendor_codes`), or publish the circuit-1 number on all
   with a note? The proposal is to leave them empty.
4. **Spelling**: the code as the manual prints it (`535`, `P112`, `P31`, `i35`), compared without
   case and spaces by consumers? WcmToMqtt writes `113` where the room-unit manual writes P113,
   and `I33` where the boiler manual writes i 33.
5. **`ha-weishaupt`**: attribute and panel column only (no change of entity names), as proposed?
6. **Third-party numberings** (the WcmToMqtt gateway's 413, 416, 412; the WTC 25-A's P42 / P43):
   leave them out, as proposed, since only a third party documents them?
