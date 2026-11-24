# Field checklist: remaining registers on the test installation

Actionable checklist to finalize the last open registers using the test installation's own
equipment (two WTC-GB 250 boilers, WCM-KA 3.0, two WCM-EM, two WCM-FS). Everything below targets
compatible `1.x` additions.

> **Previous pass (2026-11-22 & 2026-11-23) — complete:** `InstallerParameters1`–`5` landed in
> `1.2.0`; participant `00` / `05` identified as the vendor bus interface; `copy-in-use` resolved
> (`fs` drives regulation, `em` is a decoupled local store; cleared in `1.3.1`); `100%` readable
> fixture coverage restored on 2026-11-24 (686/686 readable messages, 1 029 readings).

**Safety rules:**
- **Never** send any write from `ebusd` or Home Assistant while the vendor service tool
  (WCM-Diagnose) is connected to the bus (`QQ = ff` conflict).
- For every reversible change (Lot 2 and Lot 3): **note the baseline value first, change by one
  step, capture, and restore immediately.**

---

## Lot 2 — Short reversible tests without WCM-Diagnose (operator present)

Requires the vendor service tool to be **disconnected** from the bus.

### 2A. `DeCoupleMaxTemp` (`e6fd` on `15.w.ka`)

`78.5` was not taken earlier (likely above the controller's upper bound). Test a **lower** value
from source `ff`:

1. Read baseline: `ebusctl read -f -c ka DeCoupleMaxTemp` (expected `78.0`).
2. Send a raw `50 23` write from `ff` to `15` for register `e6 fd` with value `77.5 °C`
   (`775` = `0x0307`, little-endian `07 03`, CRC-8 over `e6 fd 07 03`):
   - Note: because `DeCoupleMaxTemp` is currently read-only, use a raw `hex` write via `ebusctl`
     (or a temporary local write line on the test ebusd).
3. Read back: `ebusctl read -f -c ka DeCoupleMaxTemp`.
4. If taken (`77.5`), restore `78.0` (`780` = `0x030c`, `0c 03`) and confirm `78.0` with `-f`.
5. **Outcome:** if taken, `DeCoupleMaxTemp` can become writable (regulation class, upper bound
   established) in `15.w.ka.tsp`.

### 2B. Heating program selector (`12 01` on `35.w.fs1` / `f5.w.fs3`)

Currently only `11` (Heating Program 1) is proven.

1. Read baseline on `35` (or `f5`): raw read `50 22` of register `12 01` (CRC `46`, master data
   `46 12 01`; expected `11 00`).
2. On the room unit display, switch temporarily to **Heating Program 2** → read `12 01` (expected
   `12 00`).
3. Switch temporarily to **Heating Program 3** → read `12 01` (expected `13 00`).
4. Restore **Heating Program 1** → confirm `11 00`.
5. **Outcome:** proves the 3-value list (`Program1=17`, `Program2=18`, `Program3=19` or `0x11`–`0x13`)
   so `HeatingProgram` can be added read-only (and tested for writes later if desired).

---

## Lot 3 — Targeted WCM-Diagnose / boiler display session

Requires WCM-Diagnose connected (so **no `ebusd` writes**). Capture passively with `ebusd_trames`
snapshots before and after each step.

### 3A. Remaining boiler heating-specialist parameters (`bc1` / `bc2`)

Reference: [evidence/bc-installer-parameters.md](../evidence/bc-installer-parameters.md).

Remaining unmapped parameters (identical on both boilers in display-only mode):
- **Numeric / packed pairs (10):** `P20`, `P23` (frost protection), `P32` (switch diff, `HZ_HYS`
  `0x44`), `P34`, `P40`, `P43` (pump mode), `P47`, `P49` (pump interval, `PUHZ_DT_REG` `0x62`),
  `P51` (`WW_HYS` `0x50`), `P71` (eBUS feed).
- **Option bytes:** `P10`, `P11`, `P13`–`P17`, and confirmation of bit `0x10` in `KESS_OPT_2`
  (`0x4e`, external sensor fitted).

**Protocol (boiler idle):**
1. Take a baseline `ebusd_trames` snapshot and read EEPROM block `0x1b`–`0x65` on the idle boiler.
2. Change **one** parameter by one step on the boiler display or WCM-Diagnose.
3. Capture the changed EEPROM byte(s) via `ebusd_trames` / read-only `50 00`.
4. Restore the parameter immediately and verify the byte returns to its baseline value.

### 3B. Burner firing status bits (`bc1` / `bc2` while firing)

Reference: [evidence/boiler-firing-values.md](../evidence/boiler-firing-values.md).

While a boiler runs a natural heating cycle with WCM-Diagnose open on its status / outputs tab:
- Compare WCM-Diagnose indicators against:
  - `i30` (eSTB temperature / offset),
  - RAM `70` operating code (seen `0x20`, `0x00`, `0x0e`, `0x0f`),
  - RAM `2b` output bitfield (seen `0xf0` ignition, `0xfd` flame).

### 3C. Remaining single-source register-survey candidates

Reference: [evidence/register-survey-findings.md](../evidence/register-survey-findings.md).

1. **Heating modules (`51` / `52`) — pump / mixer tab:** open the module view in WCM-Diagnose
   (skipped on 2026-11-22) to confirm `56 00`, `57 00`, `85 02` (mixer pump PWM).
2. **Value-tied candidates:** `28 01` / `32 01`, `1a 01`, `5b 0a`, the six system-manager function
   registers (`15`), and `fb fd` / `59 03`. Separate only by changing one setting by one step in
   WCM-Diagnose, capturing the changed register, and restoring immediately.

---

## Out of scope on this installation

Accepted as not establishable without a second installation or different hardware:
- `ForcedVenting` (operating phase 9 — never emitted),
- `HolidayStartThird` / `HolidayEndThird` and `ControlVariation` values 2/3,
- `ukn*` bytes of `PowerDemand` (`05 07`),
- standalone `75.w.fs2` (not shared with `35.w.fs1`).
