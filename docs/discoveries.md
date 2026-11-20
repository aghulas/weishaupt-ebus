# Discoveries not yet in definitions

Add an entry when something is learned on a live bus. Remove it when it has landed on `weishaupt`
(or been explicitly closed). Oldest first.

| Date | Finding | Established by | Status / target |
|---|---|---|---|
| 2026-11-15 | Hydraulic decoupling / buffer registers (`e2fd`–`e9fd`) are in tenths. `e2fd` and `e7fd` are writable; the others have no captured write. | bus read | `evidence/settings-writes.md` (1.x) |
| 2026-11-15 | Boiler info values needing a running burner (i11 power, i22 pump, i23 fan, i32 ionisation, i30 eSTB, i42 burner starts) are not yet captured. | bus read, CRC checked offline | needs capture while firing (1.x) |
| 2026-11-16 | `FloorDryingTemp` and `RoomThermostatTemp` were typed `temp1` (`D1C`) on 16-bit registers in the former #717; suspect. | to verify by bus read | needs read (1.x) |
| 2026-11-17 | In cascade operation the automat's "Sup./Mod setpoint" (RAM `6e`) holds the modulation demand of the cascade manager in percent (as in `05 07`), not a flow setpoint. | bus read, both boilers | left out (already in `PowerDemand`) |
| 2026-11-17 | Automat RAM `70` reads 13 while firing and 32 when idle; output byte RAM `2b` reads `fd` firing and `80` idle (bits not told apart yet). | bus read, both boilers | needs capture while firing (1.x) |
| 2026-11-17 | System manager de-couple maximum (`e6fd`) did not take 78.5 from `ff` or `31` (read 78.0 after both); likely above the device's own bound. | telegram log | needs lower value from `ff` (1.x) |
| 2026-11-17 | ebusd reads four registers in one `50 22` telegram on this bus (`<crc>` over the 8 address bytes, 8 data bytes back); checksum routine holds. | passive capture, CRC checked offline | fact only; nothing to define |
| 2026-11-17 | A room unit and its heating module answer the same setting registers (`05 00`, `08 00`, `14 0a`, `0e 01`, `16 01`, `10 01`, `be 02`) with different values; only flow limits (`28 00`, `2b 01`) agree. Which copy the regulation uses is not established. | bus read, three circuits | `copy-in-use` in metadata; needs 0.5 K display test |
| 2026-11-17 | Heat demand (`02 00`) of heating modules: `51` gives room-unit demand + boost, `52` gives flow maximum + boost (76.0) while its room unit asks 45.8. | bus read and passive capture | left out |
| 2026-11-17 | Program selector `12 01`: `11` selects heating program 1 on room units; `12` and `13` not proven. At `50` and `f6` the register changes at every read; at `15` it is stable `11`. | bus read | needs a room unit set to another program (1.x) |
| 2026-11-18 | Metadata contract gaps noted by companion: fault-history pointer rule (`0x0201 + 8*n`), linked bounds (`write.below` / `write.above`), explicit flag for stored-only programs, UI hints for two-state facts. | companion build | compatible 1.x contract extensions |
| 2026-11-18 | Unused-function registers answer `0x8000`: room influence P/I (`0f 01`, `71 09`), adaptation (`15 01`) on room units, H1 relay (`29 0a`) on `50`. | bus read | fact only; map `0x8000` if ever defined |
| 2026-11-18 | `H1Status` register of heating modules (present in pre-switch hand-made config) has no captured read or established meaning. | migration study | needs read and meaning (1.x) |
| 2026-11-19 | `PowerDemand` (`05 07`): boiler `status` settled (`66`/`ee` requesting, `55`/`00` idle); room-unit `55` likely setback (not established); bytes 2, 5–6, 9 unnamed. Three unanswered `10 → fc` telegrams observed. | 10-day telegram export | kept neutral (`ukn*`) |
| 2026-11-19 | `27 02` on boiler automats (`50 22`, CRC `f6`) equals burner starts / 256 (`731`/`543`); adjacent registers answer `0x8000`. | read comparison | not defined (duplicate of full counter in `Counters`) |
| 2026-11-19 | `ForcedVenting` (operating phase 9): never seen on bus, no manual lists it. | manuals, bus captures | provisional label in metadata (Road to 1.0 item 2) |
| 2026-11-19 | Identification answers: `f5` returns ID bytes `57 02 00 08 00` while `35` and `75` return `57 02 00 18 00` (modules return `57 03 00 08 00`). Meaning unknown. | scan captures | fact only |
| 2026-11-19 | Participant at master `00` / slave `05`: answers `07 04` as Kromschröder, empty ID, SW `0120`, HW `0098`; master `00` scans bus addresses ~248 times/day. Most likely a WCM communication / gateway module. | ebusd scan & telegram log | needs installation equipment list (1.x) |
| 2026-11-20 | `75.w.fs2` heating programs 2 and 3 and hot-water / circulation programs: sharing with `35.w.fs1` not proven (heating program 1 and setback / frost setpoints are proven shared). | bus captures | stated as known limit in `docs/release-readme.md` |
