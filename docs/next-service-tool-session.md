# Field checklist: next vendor service tool session (WCM-Diagnose)

Consolidated read-only checklist for the next session with the vendor service tool (WCM-Diagnose)
connected to the bus. Everything below targets compatible `1.x` additions; nothing in `1.0.0`
depends on it.

**Rule during the session:** never send any write from `ebusd` or Home Assistant while the vendor
service tool is connected (`QQ = ff` conflict). Capture telegrams passively (`ebusd` telegram log /
`ebusd_trames` snapshots before and after opening each screen).

> **Pass of 2026-11-22 & 2026-11-23.** Sections 1 to 3 were run on 2026-11-22 (display only): the
> boiler parameters are defined as `InstallerParameters1`–`5` (`evidence/bc-installer-parameters.md`),
> the participant at `00` / `05` is the vendor's bus interface (`evidence/master-00-slave-05.md`), and the
> remaining single-source candidates cannot be separated by a display (`docs/discoveries.md`).
> Section 4 (`copy-in-use`) was executed on 2026-11-23 on the operator's approval during active heating:
> the regulation loop strictly follows the room-unit (`fs`) copy (`evidence/settings-writes.md`). All sections
> of this checklist are now complete.

## 1. Boiler installer parameters P10–P71 (for `1.1.0`)

Reference: [evidence/bc-installer-parameters.md](../evidence/bc-installer-parameters.md).

- Take a baseline `ebusd_trames` snapshot.
- Open the **Heating specialist** tab on **boiler A** (`08`) and **boiler B** (`18`), and note all
  displayed values P10–P71 for both boilers (especially any parameter whose value differs between
  boiler A and boiler B).
- Take a second `ebusd_trames` snapshot to confirm the read telegrams.
- Outcome:
  - 8 unambiguous parameters (`SupplyMaxTemp` P31, `FlueGasSafetyTemp` P33, `IgnitionLoad` P35,
    `LoadMin` P36, `DHWBoostTemp` P50, `PumpRunOnDHW` P42, `FlowReturnDiffTemp` P48,
    `BoilerAddress` P12) are ready to enter `08.w.bc1.tsp` / `18.w.bc2.tsp` once displayed values
    on boiler B are confirmed and names are approved.
  - Ambiguous pairs (`SupplyMinTemp` P30, `SupplySwitchDiff` P32, `PumpControlMode` P43,
    `PumpControlInterval` P49, `PumpRunOnHeating` P41, `EbusFeed` P71, `PumpLoadMin` P44,
    `FrostProtectionTemp` P23, `LoadMaxHeating` P37, `LoadMaxDHW` P38) are resolved wherever
    boiler B or the tool's EEPROM view separates them.

## 2. Participant at master `00` / slave `05`

Reference: [evidence/master-00-slave-05.md](../evidence/master-00-slave-05.md),
[docs/discoveries.md](discoveries.md).

- Open the **Bus / Participants** (device list) view in WCM-Diagnose and record how address
  `00` / `05` (`MF=Kromschroeder;ID=;SW=0120;HW=0098`) is labelled by the vendor tool (most likely
  a communication module such as WCM-COM).
- Note whether WCM-Diagnose exposes any info or diagnostic screen for it; if so, open it between
  two `ebusd_trames` snapshots.

## 3. Single-source register-survey candidates

Reference: [evidence/register-survey-findings.md](../evidence/register-survey-findings.md).

- While browsing the tabs of the system manager (`15`), heating modules (`51`, `52`) and room units
  (`35`, `75`, `f5`), note displayed values for any remaining single-source survey candidates so
  each candidate has two independent sources (bus read + vendor tool display) before entering
  `src/wolf/`.

## 4. `copy-in-use` (`fs` vs `em` circuit settings — resolved 2026-11-23)

Reference: `open = ["copy-in-use"]` in `metadata/weishaupt.toml`, `evidence/settings-writes.md`.

- **Executed on 2026-11-23 on the operator's word during active heating on circuit 2:**
  - Baseline: `em2/SupplyHCSetTemp` = 58.0 °C, `fs2/RoomNormalTemp` = 21.0 °C, `em2/RoomNormalTemp` = 21.5 °C.
  - Step A: `em2/RoomNormalTemp` changed to 22.5 °C. No change in `SupplyHCSetTemp` (stayed 58.0 °C), no change in
    `RoomSetpointTemp` (21.0 °C), no `09 03` overwrite. Restored to 21.5 °C.
  - Step B: `fs2/RoomNormalTemp` changed to 22.0 °C. `fs2/RoomSetpointTemp` changed to 22.0 °C immediately;
    `fs2.PowerDemand` increased (`c2 03` → `ee 03`); `fs2/SupplyHCSetTemp` jumped from 58.1 to 60.9 °C; and
    `em2/SupplyHCSetTemp` jumped from 58.0 to 60.0 °C. Restored to 21.0 °C (both returned to 58.1 / 58.0 °C).
- Outcome: establishes unambiguously that the regulation calculates from and applies the room-unit (`fs`) copy.
  `open = ["copy-in-use"]` can now be cleared from the metadata.
