# bc1, bc2 — fault counters of the boiler automat (read)

## What

One counter per fault number, kept by the WTC boiler automat in its EEPROM, read with the
memory read `PBSB 50 00` in `src/wolf/08.w.bc1.tsp` (target `08`), `src/wolf/18.w.bc2.tsp`
(target `18`) and the shared models `FaultCounters1` to `FaultCounters6` of
`src/wolf/wtc_inc.tsp`. Lot J, branch `weishaupt-J`.

| message | EEPROM | ID | fields (UIN, low byte first) |
|---|---|---|---|
| FaultCounters1 | `0x0196`, 12 bytes | `de 06 01 b2 96` | Code57, Code55, Code53, Code52, Code51, Code49 |
| FaultCounters2 | `0x01a2`, 12 bytes | `ea 06 01 b2 a2` | Code48, Code47, Code46, Code45, Code44, Code43 |
| FaultCounters3 | `0x01ae`, 12 bytes | `e6 06 01 b2 ae` | Code41, Code39, Code38, Code37, Code36, Code35 |
| FaultCounters4 | `0x01ba`, 12 bytes | `f2 06 01 b2 ba` | Code34, Code33, Code32, Code31, Code30, Code24 |
| FaultCounters5 | `0x01c6`, 12 bytes | `8e 06 01 b2 c6` | Code23, Code22, Code21, Code18, Code16, Code15 |
| FaultCounters6 | `0x01d2`, 6 bytes | `2e 06 01 52 d2` | Code14, Code12, Code11 |

33 counters per boiler, 12 messages in all.

## How it was established

### Address → fault number: the symbol table of the firmware

The symbol table of this firmware (`WH11928`, constants list = EEPROM; names and addresses
only, see `service-tool-log.md`, "`*.SYC` — symbol tables") names 33 consecutive symbols
`EEA_FC_<nn>`, two bytes apart, by descending number:

| Address | Symbol | Address | Symbol | Address | Symbol |
|---|---|---|---|---|---|
| `0x0196` | `EEA_FC_57` | `0x01ac` | `EEA_FC_43` | `0x01c2` | `EEA_FC_30` |
| `0x0198` | `EEA_FC_55` | `0x01ae` | `EEA_FC_41` | `0x01c4` | `EEA_FC_24` |
| `0x019a` | `EEA_FC_53` | `0x01b0` | `EEA_FC_39` | `0x01c6` | `EEA_FC_23` |
| `0x019c` | `EEA_FC_52` | `0x01b2` | `EEA_FC_38` | `0x01c8` | `EEA_FC_22` |
| `0x019e` | `EEA_FC_51` | `0x01b4` | `EEA_FC_37` | `0x01ca` | `EEA_FC_21` |
| `0x01a0` | `EEA_FC_49` | `0x01b6` | `EEA_FC_36` | `0x01cc` | `EEA_FC_18` |
| `0x01a2` | `EEA_FC_48` | `0x01b8` | `EEA_FC_35` | `0x01ce` | `EEA_FC_16` |
| `0x01a4` | `EEA_FC_47` | `0x01ba` | `EEA_FC_34` | `0x01d0` | `EEA_FC_15` |
| `0x01a6` | `EEA_FC_46` | `0x01bc` | `EEA_FC_33` | `0x01d2` | `EEA_FC_14` |
| `0x01a8` | `EEA_FC_45` | `0x01be` | `EEA_FC_32` | `0x01d4` | `EEA_FC_12` |
| `0x01aa` | `EEA_FC_44` | `0x01c0` | `EEA_FC_31` | `0x01d6` | `EEA_FC_11` |

The symbol before the first one is `EEA_FCODE_NOT` (`0x0194`), the one after the last is
`EEA_HBRONTAG` (`0x01d8`). The gap between two counters is 2 bytes everywhere, so a counter is
at most 2 bytes long. Read here from the memory map generated from the table (old work branch
of the fork, `src/kromschroeder/WH11928.tsp`); the comparison of that map with the table found
all its `EEA_FC_*` entries in the table (`service-tool-log.md`: 842 of 854 entries found, none
of the 12 others is a counter).

The names carry the number, not the kind (fault or warning).

### Fault number → meaning: the manual of the boiler

Installation and operating instruction, gas condensing boiler WTC-GB 120 … 300-A, document
83251702, edition 1/2011-02: warning codes on pages 75–76, error codes on pages 77–78, fault
history on page 74. The later French edition of the same manual (document 83251704, edition
1/2020-08, alarm codes on pages 90–91, fault codes on pages 92–93) adds W48 and F49. Meanings
below in our own words.

| No. | Kind in the manual | Meaning | No. | Kind | Meaning |
|---|---|---|---|---|---|
| 11 | F | safety limiter above 105 °C | 37 | F | return sensor defective |
| 12 | W | limiter, flow or return sensor above 95 °C | 38 | F | flue gas pressure switch does not release at the fan standstill check |
| 14 | W | limiter temperature rises too fast | 39 | W | de-coupling sensor defective |
| 15 | W, F after 30 warnings | flow/return difference too large | 41 | F | gas valve leaking |
| 16 | W | flue gas temperature too high | 43 | F | fan does not reach the requested speed |
| 18 | W, F after 30 warnings | limiter/flow difference too large | 44 | F | fan standstill check failed |
| 21 | W, F after 5 failed starts | no flame at burner start | 45 | F | air pressure switch does not switch |
| 22 | W (F21 after a failed restart) | flame lost during operation | 46 | F | pressure on the flue gas side too high |
| 23 | F | flame signal without a flame | 47 | W | gas pressure too low |
| 24 | W | input H2 closed, set as lockout input | 48 | F; in the later edition also W, F after 5 failed tries | run time of the flue gas damper exceeded |
| 30 | F | limiter sensor defective | 49 | F, later edition only | input H2 closed, set for a condensate lifting unit |
| 31 | F | flue gas sensor defective | 51 | F | boiler data record error |
| 32 | F | air pressure switch not at rest | 52 | F | burner data record error |
| 33 | W | outside sensor defective | 53 | F | supply voltage or frequency out of tolerance |
| 34 | W | hot-water sensor defective | 55 | F | reset too often |
| 35 | F | flow sensor defective | 57 | W and F | communication automat / operating unit faulty |
| 36 | F | water pressure too low | | | |

Count: the 2011 edition lists 23 warning codes and 24 error codes, on 43 distinct numbers; 32
of the 33 counter numbers are among them. The 2020 edition adds W48 and F49, so all 33 counter
numbers are listed. The manual numbers without a counter are 54 (F, electronic fault) and 80 to
89 (W, communication with other bus devices and the remote set-value signal). The fault history stores the same numbers in 7 bits with the kind in bit 7
(`bc-fault-history.md`), so one number space serves warnings and faults.

### Reads on the two boilers

**Through ebusd**, 2026-11-17, the 33 two-byte reads of the running configuration of the
installation (`<crc> 06 01 12 <address>`, same addresses), all answered on both boilers:

| No. | first | second | No. | first | second | No. | first | second |
|---|---|---|---|---|---|---|---|---|
| 57 | 20 | 11 | 43 | 0 | 35 | 30 | 0 | 1 |
| 55 | 1 | 0 | 41 | 0 | 0 | 24 | 0 | 0 |
| 53 | 1 | 3 | 39 | 0 | 0 | 23 | 0 | 0 |
| 52 | 0 | 0 | 38 | 0 | 0 | 22 | 17 | 14 |
| 51 | 0 | 0 | 37 | 0 | 0 | 21 | 24 | 19 |
| 49 | 0 | 0 | 36 | 102 | 309 | 18 | 0 | 3 |
| 48 | 0 | 2352 | 35 | 0 | 0 | 16 | 0 | 0 |
| 47 | 6 | 6 | 34 | 0 | 0 | 15 | 1 | 0 |
| 46 | 0 | 0 | 33 | 0 | 0 | 14 | 0 | 0 |
| 45 | 1 | 0 | 32 | 0 | 0 | 12 | 6 | 5 |
| 44 | 0 | 0 | 31 | 0 | 0 | 11 | 1 | 3 |

**By the vendor service tool**, 2026-11-16 (`service-tool-log.md`, tab "Statistic"): the tool
reads `0x0196`–`0x01db` in seven requests of 10 bytes (`e2 06 01 92 96` … `a6 06 01 92 d2`) and
displays none of the values on this firmware. On the first boiler its 33 byte pairs equal the
ebusd values above for 32 counters; for number 15 the log has `00 01` where ebusd reads 1
(`01 00`), see "Not verified". On the second boiler the block at `0x01d2` was logged:
`00 00 05 00 03 00`, numbers 14, 12 and 11 = 0, 5, 3, as through ebusd.

**Fault history** (lot E, `bc-fault-history.md`), the only other record of faults in the
automat. Every number present in a history has a counter that is not zero and not smaller
than its occurrences there:

| Boiler | In the six history slots | Counter |
|---|---|---|
| first | W12 five times | Code12 = 6 |
| first | F11 once | Code11 = 1 |
| second | F36 six times | Code36 = 309 |

Other observations, consistent, none a proof: number 47 (gas pressure, a supply common to
both boilers) reads 6 on both; numbers 21 and 22 (flame) are of the same order on both; 18 of
the 33 counters are zero on both boilers.

**IDs.** The CRC-8 of [register-crc.md](register-crc.md) reproduces the first byte of the
seven requests of the tool for this area and of `20 06 01 12 a4`; the six IDs of the
definitions were computed with it. The item length of 12 bytes (code `b2`) is the longest the
tool was seen to send (`df b2 1b`, `service-tool-log.md`), so six reads cover the 66 bytes.

### Level of proof

| Statement | Counters | Level |
|---|---|---|
| address ↔ number | all 33 | source: symbol name of the firmware table |
| address ↔ number | 11, 12, 36 | also consistent with the fault history |
| two bytes, low byte first | all 33 | spacing of the symbols; values of 309 and 2352; same order as the hour counters (`bc-counters.md`) |
| meaning of the number | 32 of 33 | source: manual of the boiler, both editions |
| meaning of the number | 49 | source: later edition of the manual only (printed nine years after the first; whether it describes this firmware is not established) |
| value compared with a displayed figure | none | the tool shows no counter on this firmware |

Toolchain: `CFG_REPO=<worktree of weishaupt-J> scripts/check.sh` clean (format, compile,
`ebusd --checkconfig`, 586 messages, translations).

## Equipment

Two WTC condensing boilers in cascade, automat scanned `MF=Kromschroeder;SW=1104;HW=0501`
(firmware shown by the tool as 11.0e), about 87 000 and 83 000 hours with mains on.

## Date

2026-11-17.

## Not verified

- **The six messages have not been sent through ebusd.** The values above come from 2-byte
  reads of the same addresses. A 12-byte item after the address prefix `06 01` follows from the
  grammar; the tool was seen with 12 bytes without the prefix and with 10 and 8 bytes after it.
- **No counter was seen to step.** The observation that would close this: a new entry in the
  fault history of a boiler with the counter of its number one higher than before.
- **Which event a counter counts** when the manual lists the number both as a warning and as a
  fault (15, 18, 21, 48, 57): warnings, lockouts or both. Same observation as above, with the kind
  of the new history entry.
- The second boiler reads 2352 for number 48 (flue gas damper) and 35 for number 43 (fan
  speed); no other record explains these figures. The later edition of the manual has a
  warning W48 before the lockout F48, so the figure may count warnings; not established.
- The running configuration of the installation labels number 49 as a condensate safety
  switch, which agrees with the later edition of the manual, and number 33 as a fault without
  text, where the manual has a warning. The source of its labels is not recorded.
- The log line of the tool for `0x01c8` ends with `00 01` at `0x01d0` (256 low byte first)
  where ebusd reads 1 on the same boiler a day later. The capture itself is not kept; a
  transposition in the log is the likely cause.
- Other firmware versions of the automat: the addresses come from this one.
- Values above 255 on the first boiler; the maximum of a counter (65 535 assumed).
