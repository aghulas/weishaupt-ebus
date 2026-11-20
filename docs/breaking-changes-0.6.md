# Breaking changes for definitions 0.6 (review, nothing changed)

Read-only review of the lots as published in 0.5.15 (1 075 messages loaded by ebusd; the lot
files `08.w.bc1`, `18.w.bc2`, `15.w.ka`, `50.w.em1`, `51.w.em2`, `52.w.em3`, `35.w.fs1`,
`75.w.fs2`, `f5.w.fs3` and the lot messages of `broadcast`; 669 messages in the metadata).
Prepared 2026-11-20 for "Road to 1.0" in `docs/plan.md`: 0.6 gathers every rename, removal or
retyping still wanted; after it the names are frozen. No lot branch, no metadata changed.

**Breaking**, by the convention of the plan ("Versions"): a message or a field renamed,
removed or retyped, a field inserted before others, a value-list name changed, a circuit (file)
renamed, or the `schema` of the metadata raised. What each breaks is given for a user of 0.5.15
in three places: ebusd (`read` / `write` names, `find` output), MQTT (topics
`ebusd/<circuit>/<name>` and the field names in the JSON payload), and the companion (0.9.1
identifies an entity by circuit, message and field; `renamed_from` in the metadata carries a
**message** key only, so a renamed **field** has no carrier today).

Recommendations: **do in 0.6**, **leave for good** (no change before or after 1.0), **owner**
(cannot decide without the owner). Where a rename is a matter of taste, the line says so.

Sources: guidelines.md of ebusd-configuration ("Dos and Don'ts"), the style guide of
ebus-typespec, the evidence records named, the metadata of 0.5.15.

## Summary

| # | Change | Recommendation |
|---|---|---|
| 1 | Remove the write lines of `RoomSetbackTemp`, `RoomFrostProtectionTemp` of `75.w.fs2` | do in 0.6 |
| 2 | `MixerPump` (`em2`, `em3`): number → value list `0=off;1=on` | do in 0.6 |
| 3 | `HcMode` fields `Opmode_4` … `Opmode_7` → `Ukn3_4` … `Ukn3_7` | do in 0.6 |
| 4 | `LegionellaStartTime` (`ka`): number of quarter hours → time of day (`TTQ`) | do in 0.6 |
| 5 | Metadata: a carrier for renamed fields (`renamed_from` on a field), needed if 3 is done | do in 0.6 (compatible addition, schema 1) |
| 6 | `HolidayStartThird`, `HolidayEndThird` (three room units): rename to `...Year` if the display test shows a year, else keep | owner |
| 7 | Circuit `em1` (address `50`, the system manager's own circuit) → another circuit name | owner (lean: leave) |
| 8 | `HcMode` fields `Ink1_*`, `Ink2_*` → `Ukn1_*`, `Ukn2_*` (taste) | owner (only together with 3) |
| 9 | `DHWExceeded` (`ka`) → `DHWExcessTemp`, unit K | owner |
| 10 | `CalorifierExcessTemp`, `CalorifierSwitchDiff` (`ka`) → `Buffer...` | leave for good |
| 11 | `DHWSetValue` (`ka`) → `DHWSetTemp` | leave for good (comment fix, compatible) |
| 12 | `ControlVariation` (room units): number → value list | leave for good |
| 13 | The eight reads of `50.w.em1` that duplicate `15`; the three `same_as` pairs | leave for good |
| 14 | `FirstByte` on every memory read (`50 00`) | leave for good |
| 15 | `Ukn*` fields of `PowerDemand`, `EventCounters`, `Boiler1Status`, `Boiler2Status` | leave for good |
| 16 | `VersionMajor` / `VersionMinor` against `SoftwareVersionCPU` / `SoftwareVersionCUI` (same registers) | leave for good |
| 17 | `Supply*` / `DHW*` against the `Flow*` / `Hwc*` of the Wolf and Vaillant files upstream | leave for good |
| 18 | `DeCouple*` (`ka`) against `HydraulicSeparatorTemp` (boilers) | leave for good |
| 19 | `RoomSetpointTemp` (in effect) against the `...SetTemp` of other in-effect values (taste) | leave for good |
| 20 | `ModulationStatus` (`ka`, a percentage) (taste) | leave for good |
| 21 | `SwitchOnRuntime` (a lead time) (taste) | leave for good |
| 22 | Mixed abbreviations: `Circ` / `Circulation`, `HC` / `Hc`, `DHWLegionellaDay` / `Legionella*` (taste) | leave for good |
| 23 | `fluegastemp` SCH in `Temperatures`, UCH in `FaultHistorySlot*` and `Boiler*Status` | leave for good |
| 24 | `boilertemp` in `FaultHistorySlot*` against `supplytemp` elsewhere | leave for good |
| 25 | `burnerhourstoday`, `ignitionstoday` named by the firmware symbol | leave for good |
| 26 | `HeatingCircuitType` value `Radiator70` (the tool shows "radiator 75 °C") | leave for good |
| 27 | Directory `src/wolf`, namespace `Wolf`, release folder `kromschroeder/` | leave for good |
| 28 | Identification `W` in the file names | leave for good |
| 29 | Metadata structure: schema 2 | leave for good (not needed) |

Count: **do in 0.6: 5** (1–5, of which 5 is a compatible addition that 3 needs); **owner: 4**
(6–9); **leave for good: 20** (10–29). Not breaking, listed at the end: enum names against the
style guide, and comment fixes.

## Do in 0.6

**1. Write lines of the setback and frost setpoints of `75.w.fs2`** (lot C).
`75.w.fs2` `w RoomSetbackTemp`, `w RoomFrostProtectionTemp`. Since 0.5.15 both carry
`shared_with = fs1/<name>` and no write conditions: a write to `35` is read at `75` within
seconds with no telegram between (`evidence/room-units-shared-store.md`, section 6). The write
lines stay in the CSV only to avoid a breaking change in a third-number release. Proposed:
remove the two `w` lines (the reads stay). Breaks: `ebusd write -c fs2 RoomSetbackTemp …` and
the MQTT `set` topic of these two; a script that used them writes `fs1` instead, same effect.
Companion: nothing (it offers no write there since 0.5.15). No `renamed_from` needed (the read
keeps its key). Reason: the CSV then says what the metadata says, one place to write a shared
value. Need, not taste.

**2. `MixerPump`** (lot O, `51.w.em2`, `52.w.em3`). `value: UIN` "state of the mixer-circuit
pump, 1 = on". Proposed: the value list of the other pump states (`0=off;1=on`, as `Pump` of
`HcMode` and the pump bits of `Boiler*Status`). Evidence: `evidence/survey-reads.md`, the tool's
screen on `52` (mixer pump on, register 1) and `51` reading 0. Breaks: the published value
becomes `on` / `off` instead of `1` / `0` (ebusd, MQTT); companion: the entity changes from a
number to a two-state value (same key; no rename). Reason: type weaker than the evidence and
inconsistent with every other pump field. Added in 0.5.14, few users.

**3. `HcMode` fields `Opmode_4` … `Opmode_7`** (lot A, `wtc_inc`, used by `em1`, `em2`, `em3`).
They are bits 3 to 6 of the byte that holds `Pump`, `ValveClosing`, `ValveOpening`, not bits of
`Opmode` (a byte of its own): the name says the wrong place. Proposed: `Ukn3_4` … `Ukn3_7` (third
byte of the answer, bit 4 to 7 counted from 1), the scheme `Boiler1Status` uses (`Ukn2_1`,
`Ukn3_3`). Breaks: four field names in the JSON of `HcMode` on three circuits (ebusd `read -v`,
MQTT payload). Companion: none (the metadata marks them `skip`). Evidence: `em-hcmode.md`
("named but not interpreted"). Reason: misleading, not taste; also what a reviewer of #717
would ask.

**4. `LegionellaStartTime`** (lot O, `15.w.ka`). `value: UIN`, "start time of the legionella
protection, in quarter hours (parameter 581)". Proposed: `TTQ` on the low byte (time of day in
quarter hours, a type of the library) and the high byte ignored, so ebusd shows `08:30` instead
of `34`. Evidence: `survey-reads.md`, register `f4 fd` read `22 00` = 34, the tool's P581 "08:30"
(34 quarter hours). Breaks: the published value changes format (number →
`hh:mm`); companion entity from number to time, same key. Reason: type weaker than the
evidence. Read only, added in 0.5.14. Low weight; drop it if the owner wants the fewest changes.

**5. A carrier for renamed fields in the metadata** (lot M, contract). `renamed_from` exists on
messages only. If 3 (or 8) is done, the contract should let a field say its former name
(`renamed_from` on a field), so that a consumer can follow it. Compatible addition, schema
stays 1. Needed only if a field is renamed.

## Owner

**6. `HolidayStartThird`, `HolidayEndThird`** (lot C, three room units). Third register of the
holiday start and end dates; took 0 and 24 and read them back; "meaning not established"
(`evidence/holiday-dates.md`). Its meaning is likely the year (the batch plan of
`choice-date-program-writes.md` calls it "year"), but no source establishes it. If it is the year and the name stays, the
frozen name says nothing; renaming it after 1.0 needs 2.0. Proposed: before 0.6, the display
test of `docs/discoveries.md` (a future holiday period entered on a room unit, read by ebusd,
step B); if the value is the year (or year − 2000), rename to `HolidayStartYear`,
`HolidayEndYear` in 0.6 with `renamed_from`; if not, keep `...Third` for good. Breaks (if
renamed): six messages (read and write) × three circuits; companion covered by
`renamed_from`. The test needs the owner at a display.

**7. Circuit `em1`** (file `50.w.em1`, 67 messages). `em` reads as the WCM-EM heating module;
`50` is the system manager's own direct circuit, the same device as `15`
(`evidence/heating-modules-reads.md`). Proposed, if wanted: a circuit name that says so (for
example `hc1`, or `ka1`). Breaks: every key of the file (ebusd `-c em1`, MQTT `ebusd/em1/…`,
67 companion entities; `renamed_from` can carry all 67 message keys, the circuit itself has no
carrier). Lean: **leave**. The metadata already puts `em1` under the device `manager` with its
own labels, the name is a label of the address, and the cost is the largest of the list. But
it is the one rename that is impossible after 1.0 short of 2.0, so it needs the owner's word.

**8. `HcMode` fields `Ink1_1` … `Ink2_8`** (lot A). Unknown bits named `Ink`, where the other
unknown fields of the lots are `Ukn`. Proposed: `Ukn1_*`, `Ukn2_*`, together with 3 so that
`HcMode` has one scheme. Taste (the names are not wrong, only different); no companion impact
(`skip`); breaks the JSON field names of `HcMode`. Worth doing only in the same release as 3.

**9. `DHWExceeded`** (lot A, `15.w.ka`, read; value 10.0, `UIN/10 °C`). The name is a past
participle and lacks the `...Temp` its neighbours have (`DeCoupleExcessTemp`,
`CalorifierExcessTemp`); the value looks like an excess (a difference, K), not a temperature.
Proposed: `DHWExcessTemp`, unit K (a unit change alone is compatible). The source of the name
is the operator's earlier configuration; no manual parameter is matched to it
(`evidence/ka-reads.md`). Breaks: one message key; companion covered by `renamed_from`. Partly
taste; the owner decides whether one more rename is worth it. Lean: rename only if a manual
parameter is found for it before 0.6.

## Leave for good

**10. `CalorifierExcessTemp`, `CalorifierSwitchDiff`** (`15.w.ka`). The first is the buffer
storage excess (P561, KA p. 92); the comment says so since 0.5.15. But "calorifier" is the
vendor's own English word for the buffer storage (WTC-en p. 25, where the French edition says
"stock tampon"; `evidence/terms.md`), and the metadata labels say "buffer". The second is
written from `ff`; renaming it would break writes for a word the vendor uses. Keep both.

**11. `DHWSetValue`** (`15.w.ka`, live). It is the hot-water setpoint in effect (it follows the
manager's program, `modules-programs.md`); `DHWSetpoint` is the setting. Same comment on both
today ("domestic hot water setpoint"). The labels already differ ("Current hot water setpoint"
/ "Hot water setpoint"). Keep the name; change the comment to "hot water setpoint in effect"
(compatible, any release).

**12. `ControlVariation`** (room units). A number; 0 and 1 are named in the comment (owner,
2026-11-19), 2 and 3 are not established. A value list now would leave two values without a
name and change the published value; a value list later would be a retype after the freeze.
Keep the number for good; the comment carries the names.

**13. Duplicates of `15` in `50.w.em1`.** Its eight reads (setpoints, curve, changeover, flow
limits, boost) give the values of `15`; three are also defined on `ka` and linked by
`same_as`. `50.w.em1` is the circuit's view and the place where the writes from `ff` are
proven; removing either side breaks keys and gains nothing a consumer cannot do with `same_as`.

**14. `FirstByte`** (every `50 00` read of lots D, E, F, J and `EventCounters`). A protocol
byte made a field in 0.4.0 because it marks an answer whose data read zero
(`bc-fault-history.md`). It is the validity indicator a consumer can use; removing it now is a
break for no gain. Keep.

**15. `Ukn*` fields** (`PowerDemand` `ukn2`, `ukn5`, `ukn9`; `EventCounters` `ukn6`;
`Boiler1Status`, `Boiler2Status` `ukn2_1` … `ukn3_5`). Stable placeholders by byte (and bit)
position, comments say "meaning not established"; the companion skips them. If a meaning is
found after 1.0, the comment says it; the name stays.

**16. Versions.** Registers `99 01` / `9a 01` read as `SoftwareVersionCPU` / `CUI` (HEX) on the
boiler automats (info values i44, i45, `bc-info-values.md`) and as `VersionMajor` / `Minor`
(numbers) on the WCM devices (the scan's `SW` and the tool's version, `survey-reads.md`). Two
firmware families, each name and type as its evidence says.

**17. `Supply*` / `DHW*`** against upstream `Flowtemp` / `Hwctemp` (Wolf) and `FlowTemp` /
`HwcTemp` (Vaillant). Consistent across all the lots, used in the open pull request #717;
upstream itself has no single scheme. A global rename for an unasked review is not worth the
break.

**18. `DeCoupleTemp`, `DeCoupleMinTemp`, `DeCoupleExcessTemp`, `DeCoupleMaxTemp`** (`ka`).
Sensor B22 is the separator or the plate exchanger's secondary side (KA manual), wider than the
boilers' `HydraulicSeparatorTemp` (info value i39). Different quantities, different names.

**19.–22. Taste.** `RoomSetpointTemp` (the in-effect room setpoint; `SupplyHCSetTemp` is the
in-effect flow setpoint), `ModulationStatus` (a percentage), `SwitchOnRuntime` (the lead time of
the optimised switch-on), and the mixed abbreviations (`CircProgram` / `CirculationReturnSetTemp`
/ `CircWithLegionella`, `HCProgram` / `HcMode`, `DHWLegionellaDay` beside `LegionellaSetpoint`).
Each could be argued; none misleads with its comment and label. Keep.

**23. `fluegastemp`** is SCH in `Temperatures` (lot F, one RAM block of four signed bytes) and UCH
in `FaultHistorySlot*` and `Boiler*Status`. Each type follows its block; the values seen are
inside both ranges (flue-gas safety limit 120 °C).

**24. `boilertemp`** in the fault history: the column of the history as the vendor shows it
(`bc-fault-history.md`); not the flow sensor reading of the other messages.

**25. `burnerhourstoday`, `ignitionstoday`** (`EventCounters`): named after the firmware
symbols, the comment says so; both read 0. A meaning found later goes to the comment.

**26. `HeatingCircuitType` value `Radiator70`**: the room unit's manual (83277504 p. 48) says
"radiators 70" with a factory flow setpoint of 75 °C; the tool says "radiator 75 °C". The value
name follows the manual (`survey-reads.md`).

**27. `src/wolf`, namespace `Wolf`, `kromschroeder/`.** Upstream's structure (Kromschröder
devices share the Wolf folder; `src/kromschroeder` is a link to it). Not visible to a user of
the CSV: the release folder is `kromschroeder/`, as ebusd expects for the manufacturer.

**28. `W` in the file names**: the identification the devices answer to the scan; ebusd selects
the file by it. Cannot change.

**29. Metadata schema.** Schema 1 holds everything the lots need (`same_as`, `shared_with`,
`renamed_from`, `absent`, write conditions). No structural change is wanted; carry
`renamed_from` of `ka/DHWLoadingPriority` (from `ka/DHWOperationMode`) and add one for each
0.6 rename.

## Not breaking (any release, listed for completeness)

- **Enum names** (`_DHWOperation`, `_faultKind`, `_onoff`, `_weekday`, … in `wtc_inc.tsp`): the
  style guide of ebus-typespec asks for `Values_<name>`, and `_DHWOperation` keeps the name the
  message lost in 0.5.0. The CSV does not carry enum names: renaming them changes no output. A
  reviewer of #717 may ask; do it with the next lot A update.
- **Comments**: `DHWSetValue` (11).

## Looked at and found fine

- **A** (`ka` registers, `KaStatus`, `Boiler*Status`, `Boiler*Power`, `HcMode`, clock and
  programs of `50`): names, types and value lists as their evidence; only 3, 8, 9 above.
- **E** (fault log of `50`, `BurnerServiceHours`, fault history of both automats): fine; 14, 24.
- **D** (`Counters`: operating hours, burner hours, starts): fine.
- **F** (`Temperatures`, `Operation`): fine; 23.
- **C** (66 written settings, holiday dates, control variation, modulation limits, programs
  written): fine apart from 1, 6.
- **G** (circuit values and settings of the room units and modules): fine; 7, 13.
- **H** (315 program slots of the room units): names and codec consistent across the three
  units; nothing.
- **J** (fault counters `code11` … `code57`): fine.
- **K** (boiler info values i31–i46): fine; 16.
- **N** (`PowerDemand`, five pairs): fine; 15.
- **O** (reads of the register survey): 2, 4; the rest fine (10 decided above).
- **L** (French comments): not breaking by nature; provisional strings are item 2 of "Road to
  1.0", not this list.
- **M** (metadata, schema 1): 5, 29.
- **broadcast** (`KaStatus`, `Datetime`): fine.

## Date

2026-11-20.
