# Field checklist: next vendor service tool session (WCM-Diagnose)

Consolidated read-only checklist for the next session with the vendor service tool (WCM-Diagnose)
connected to the bus. Everything below targets compatible `1.x` additions; nothing in `1.0.0`
depends on it.

**Rule during the session:** never send any write from `ebusd` or Home Assistant while the vendor
service tool is connected (`QQ = ff` conflict). Capture telegrams passively (`ebusd` telegram log /
`ebusd_trames` snapshots before and after opening each screen).

## 1. Boiler installer parameters P10–P71 (for `1.1.0`)

Reference: [docs/boiler-parameters-proposal.md](boiler-parameters-proposal.md).

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

## 4. `copy-in-use` (`fs` vs `em` circuit settings — optional, after disconnecting the tool)

Reference: `open = ["copy-in-use"]` in `metadata/weishaupt.toml`.

- **Only after disconnecting WCM-Diagnose** (no `QQ = ff` for 15 min), and on the operator's word:
  - Pick one heating circuit (e.g. circuit 2: `fs2` `75` and `em2` `51`) during an active heating
    period.
  - Record `em2/SupplyHCSetTemp`, `fs2/RoomNormalTemp`, `em2/RoomNormalTemp`.
  - Change `em2/RoomNormalTemp` by +1.0 °C (from `ff`), wait 2 minutes, observe whether
    `em2/SupplyHCSetTemp` moves and whether `fs2` overwrites `em2` via `09 03`. Restore `em2`.
  - Repeat on `fs2/RoomNormalTemp` by +1.0 °C, wait 2 minutes, observe `em2/SupplyHCSetTemp` and
    `em2/RoomNormalTemp`. Restore `fs2`.
- Outcome: establishes which copy (`fs` or `em`) the regulation applies, allowing `open =
  ["copy-in-use"]` to be cleared in `metadata/weishaupt.toml`.
