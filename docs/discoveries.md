# Discoveries not yet in a contribution branch

Add an entry when something is learned on a live bus. Remove it when it has landed in a branch
listed in `plan.md`. Oldest first.

| Date | Finding | Established by | Target lot |
|---|---|---|---|
| 2026-10-30 | Regulator writes (`5023`) carry one register per telegram. | bus test | C (comment) |
| 2026-10-30 | Most FS and KA settings are accepted only from source address `ff`; from another master they are acknowledged but ignored. Registers the devices write to each other, and FS time program slots, accept any master. The rule is per register, not per device. | bus test, register by register | C (comment) |
| 2026-10-30 | The Weishaupt CRC does not depend on the source address. WTC automats require it on reads; EM modules do not check it on writes. | bus test | A, C |
| 2026-10-30 | Date and time are set only by the standard broadcast `fe 0700`, sent at second 00. | bus test | A (comment) |
| 2026-11-08 | `HolidayTempLevel` (`3d01`) is a choice (0 = antifreeze, 1 = setback), not a temperature. | bus read and write | C (was in the former #717, now only on `backup/weishaupt-pr-717-big`) |
| 2026-11-15 | Hydraulic decoupling / buffer registers (`e2fd`–`e9fd`) are in tenths. | bus read | C (was in the former #717, now only on `backup/weishaupt-pr-717-big`) |
| 2026-11-15 | Per-code fault counters of the WTC readable from EEPROM (`5000`), 33 two-byte counters at `0x0196`–`0x01d7`. The fault history itself has landed in lot E. Not written on 2026-11-17: the table "address → fault code" has no recorded source and no count has an independent figure (see `plan.md`). | bus read | not in a lot yet |
| 2026-11-15 | Info values of the service tool readable through `5022`, ID = CRC, register, bank. Hours since last service has landed in lot E; the other info values have not. | bus read, CRC checked offline | not in a lot yet |
| 2026-11-15 | Burner totals (starts, operating hours) answer `0x8000` (not available) on WTC firmware 11.0e. | bus read, both boilers | E (comment) |
| 2026-11-16 | `ChangeOverTime` is in hours with factor 1 on a 16-bit register; `temp1` (`D1C`) in the TypeSpec is suspect, as for `FloorDryingTemp` and `RoomThermostatTemp`. | to verify by bus read | A |
| 2026-11-16 | Register 13 of the system manager is the de-couple sensor B22, not the boiler flow. The service tool reads the system manager with `09 02`, no CRC. | service tool screen | A |
| 2026-11-17 | In cascade operation the automat's "Sup./Mod setpoint" (RAM `6e`) holds the modulation demand of the cascade manager in percent (2 and 0, as in `05 07`), not a flow setpoint. | bus read, both boilers | F (left out) |
| 2026-11-17 | Automat RAM `70` reads 13 while firing and 32 when idle: a state, but not the operating phase of the status telegram. Output byte RAM `2b` reads `fd` firing and `80` idle; valves and pump agree with the status telegram, bits not told apart yet. | bus read, both boilers | F (left out) |
