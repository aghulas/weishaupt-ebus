# Discoveries not yet in a contribution branch

Add an entry when something is learned on a live bus. Remove it when it has landed in a branch
listed in `plan.md`. Oldest first.

| Date | Finding | Established by | Target lot |
|---|---|---|---|
| 2026-10-30 | Regulator writes (`5023`) carry one register per telegram. | bus test | C (comment) |
| 2026-10-30 | Most FS and KA settings are accepted only from source address `ff`; from another master they are acknowledged but ignored. Registers the devices write to each other, and FS time program slots, accept any master. The rule is per register, not per device. | bus test, register by register | C (comment) |
| 2026-10-30 | The Weishaupt CRC does not depend on the source address. WTC automats require it on reads; EM modules do not check it on writes. | bus test | A, C |
| 2026-10-30 | Date and time are set only by the standard broadcast `fe 0700`, sent at second 00. | bus test | A (comment) |
| 2026-10-30 | Week day in registers: 1 = Monday … 7 = Sunday. | bus read after clock set | A |
| 2026-11-08 | `HolidayTempLevel` (`3d01`) is a choice (0 = antifreeze, 1 = setback), not a temperature. | bus read and write | in #717 |
| 2026-11-15 | Hydraulic decoupling / buffer registers (`e2fd`–`e9fd`) are in tenths. | bus read | in #717 |
| 2026-11-15 | WTC fault history (6 slots) and per-code fault counters readable from EEPROM (`5000`). | bus read | E |
| 2026-11-15 | Info values of the service tool readable through `5022`, ID = CRC, register, bank. Hours since last service confirmed. | bus read, CRC checked offline | E |
| 2026-11-15 | Burner totals (starts, operating hours) answer `0x8000` (not available) on WTC firmware 11.0e. | bus read, both boilers | E (comment) |
| 2026-11-16 | `ChangeOverTime` is in hours with factor 1 on a 16-bit register; `temp1` (`D1C`) in the TypeSpec is suspect, as for `FloorDryingTemp` and `RoomThermostatTemp`. | to verify by bus read | A |
| 2026-11-16 | `50 00` memory read is a list of `<code> <address>` items: high nibble of the code = length - 1, low nibble = area (1 RAM, 2 EEPROM), code `06` sets the address high byte. | service tool telegrams, self-consistent re-read | D |
| 2026-11-16 | WTC counters at EEPROM `0x01e6`: operating hours (3 bytes), burner hours (2), burner starts (3), low byte first. Operating hours seen to step by one. | service tool telegrams, two reads | D |
| 2026-11-16 | WTC fault history: 6 records of 8 bytes at EEPROM `0x0202` (code with bit 7 = warning, phase, load, pump PWM, boiler temp, flue gas temp, ionisation x0.1, return temp). | service tool screen, 48 of 48 values | E |
| 2026-11-16 | Register 13 of the system manager is the de-couple sensor B22, not the boiler flow. The service tool reads the system manager with `09 02`, no CRC. | service tool screen | A |
