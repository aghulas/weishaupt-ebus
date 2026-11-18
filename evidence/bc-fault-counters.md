# bc1, bc2 — fault counters of the boiler automat (read)

## What

One counter per fault number, kept by the WTC boiler automat in its EEPROM, read with the
memory read `PBSB 50 00` in `src/wolf/08.w.bc1.tsp` (target `08`), `src/wolf/18.w.bc2.tsp`
(target `18`) and the shared models `FaultCounters1` to `FaultCounters7` of
`src/wolf/wtc_inc.tsp`. Lot J, branch `weishaupt-J`.

| message | EEPROM | ID | fields |
|---|---|---|---|
| FaultCounters1 | `0x0196`, 10 bytes | `e2 06 01 92 96` | FirstByte, Code57, Code55, Code53, Code52, Code51 |
| FaultCounters2 | `0x01a0`, 10 bytes | `d4 06 01 92 a0` | FirstByte, Code49, Code48, Code47, Code46, Code45 |
| FaultCounters3 | `0x01aa`, 10 bytes | `de 06 01 92 aa` | FirstByte, Code44, Code43, Code41, Code39, Code38 |
| FaultCounters4 | `0x01b4`, 10 bytes | `c0 06 01 92 b4` | FirstByte, Code37, Code36, Code35, Code34, Code33 |
| FaultCounters5 | `0x01be`, 10 bytes | `ca 06 01 92 be` | FirstByte, Code32, Code31, Code30, Code24, Code23 |
| FaultCounters6 | `0x01c8`, 10 bytes | `bc 06 01 92 c8` | FirstByte, Code22, Code21, Code18, Code16, Code15 |
| FaultCounters7 | `0x01d2`, 6 bytes | `2e 06 01 52 d2` | FirstByte, Code14, Code12, Code11 |

`FirstByte` is UCH, the counters are UIN (low byte first). 33 counters per boiler, 14 messages
in all. The first version of the lot (`9e8cdd3`, in release 0.3.1) had six reads of 12 bytes
with the first byte skipped; why it was changed is in "The six requests as written" and "The
seven 10-byte requests" below.

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
seven requests of the tool for this area and of `20 06 01 12 a4`; the IDs of the definitions
were computed with it. The first version used items of 12 bytes (code `b2`), the longest the
tool was seen to send (`df b2 1b`, `service-tool-log.md`); the lot now uses the 10 bytes
(code `92`) the tool sends for this area.

### The six requests as written, 2026-11-18

Sent from `31` with the `hex` command of ebusd (read-only, `50 00`), to both boilers, between
05:58 and 06:03; the running configuration of the installation does not carry the six
messages. Request on the bus: `31 <zz> 50 00 05 <ID>`. Answers after the length byte, status
byte first.

| Boiler | Message | ID | Answer | Data bytes | Counters | Answered |
|---|---|---|---|---|---|---|
| `08` | FaultCounters1 | `de 06 01 b2 96` | `00 14 00 01 00 01 00 00 00 00 00 00 00` | 12 | 20, 1, 1, 0, 0, 0 | 1 of 1 |
| `08` | FaultCounters2 | `ea 06 01 b2 a2` | `00 00 00 06 00 00 00 01 00 00 00 00 00` | 12 | 0, 6, 0, 1, 0, 0 | 1 of 1 |
| `08` | FaultCounters3 | `e6 06 01 b2 ae` | `00 00 00 00 00 00 00 00 00 66 00 00 00` | 12 | 0, 0, 0, 0, 102, 0 | 7 of 7 |
| `08` | FaultCounters4 | `f2 06 01 b2 ba` | `00 00 00 00 00 00 00 00 00 00 00 00 00` | 12 | 0, 0, 0, 0, 0, 0 | **3 of 12** |
| `08` | FaultCounters5 | `8e 06 01 b2 c6` | `00 00 00 11 00 18 00 00 00 00 00 01 00` | 12 | 0, 17, 24, 0, 0, 1 | 2 of 2 |
| `08` | FaultCounters6 | `2e 06 01 52 d2` | `00 00 00 06 00 01 00` | 6 | 0, 6, 1 | 1 of 1 |
| `18` | FaultCounters1 | `de 06 01 b2 96` | `00 0b 00 00 00 03 00 00 00 00 00 00 00` | 12 | 11, 0, 3, 0, 0, 0 | 1 of 1 |
| `18` | FaultCounters2 | `ea 06 01 b2 a2` | `00 30 09 06 00 00 00 00 00 00 00 23 00` | 12 | 2352, 6, 0, 0, 0, 35 | 1 of 1 |
| `18` | FaultCounters3 | `e6 06 01 b2 ae` | `00 00 00 00 00 00 00 00 00 35 01 00 00` | 12 | 0, 0, 0, 0, 309, 0 | 1 of 1 |
| `18` | FaultCounters4 | `f2 06 01 b2 ba` | `00 00 00 00 00 00 00 00 00 01 00 00 00` | 12 | 0, 0, 0, 0, 1, 0 | 2 of 2 |
| `18` | FaultCounters5 | `8e 06 01 b2 c6` | `00 00 00 0e 00 13 00 03 00 00 00 00 00` | 12 | 0, 14, 19, 3, 0, 0 | 1 of 1 |
| `18` | FaultCounters6 | `2e 06 01 52 d2` | `00 00 00 05 00 03 00` | 6 | 0, 5, 3 | 1 of 1 |

- Every answer received has one status byte `00` and as many data bytes as the model has
  fields times two; no answer was short or long, and every counter decodes.
- The 33 two-byte reads of the running configuration, repeated on both boilers right after
  (06:03, all 66 answered), give the same value as the grouped answers for every counter. All
  66 values are also those of 2026-11-17: no counter has moved.
- **`FaultCounters4` to the first boiler failed 9 times out of 12** with `ERR: SYN received`
  (no answer seen by ebusd): three times in a row at the first pass, then mixed with successes
  over three minutes, while the requests sent between the attempts were answered. Its answer
  is the only one of the twelve made of zero bytes only.

**Control reads**, same minutes, first boiler, in the area `0x01b8`–`0x01c7` where its eight
counters (numbers 35 to 23) are all zero, plus the non-zero `FaultCounters3` in between:

| Item | Requests | Zero bytes in a row in the answer (status included) | Answered |
|---|---|---|---|
| 12 bytes at `0x01ba` (`f2 06 01 b2 ba`), `0x01b8` (`f0 06 01 b2 b8`), `0x01bc` (`f4 06 01 b2 bc`) | 12 + 4 + 4 | 13 | 3 + 2 + 1 = 6 of 20 |
| 11 bytes at `0x01ba` (`42 06 01 a2 ba`) | 4 | 12 | 2 of 4 |
| 10 bytes at `0x01ba` (`ce 06 01 92 ba`), `0x01b8` (`cc 06 01 92 b8`), `0x01bc` (`c8 06 01 92 bc`) | 9 + 5 + 5 | 11 | 19 of 19 |
| 8 bytes at `0x01ba` (`7a 06 01 72 ba`) | 4 | 9 | 4 of 4 |
| 12 bytes at `0x01ae`, not all zero (`e6 06 01 b2 ae`) | 7 | 10 | 7 of 7 |

- The loss follows the content of the answer, not the address or the request: three different
  12-byte requests whose answer is all zero fail alike, the same length with one non-zero
  counter is answered every time, and so is the same address with 10 or 8 bytes.
- The longest run of zero bytes seen answered every time is 11 (19 of 19); with 12 half of the
  answers were lost, with 13 two thirds.
- Where the answer is lost (automat, bus level, adapter or ebusd) is not established. The
  frame checksums do not explain it: neither the request nor the all-zero answer has a
  checksum byte that needs escaping (computed, `46` for the answer).
- The vendor tool reads this area in items of 10 bytes (`e2 06 01 92 96` …), never 12.

Consequence: five of the six messages are confirmed as written on the values present. A 12-byte
message whose six counters are all zero, which is the normal state of a boiler without faults,
is not read reliably on this installation. Change accepted by the owner on 2026-11-18 and made
the same day (see the next section): seven reads of at most 10 bytes per boiler, on the
boundaries of the vendor tool, the last one unchanged:

| Message | ID | Counters |
|---|---|---|
| FaultCounters1 | `e2 06 01 92 96` | 57, 55, 53, 52, 51 |
| FaultCounters2 | `d4 06 01 92 a0` | 49, 48, 47, 46, 45 |
| FaultCounters3 | `de 06 01 92 aa` | 44, 43, 41, 39, 38 |
| FaultCounters4 | `c0 06 01 92 b4` | 37, 36, 35, 34, 33 |
| FaultCounters5 | `ca 06 01 92 be` | 32, 31, 30, 24, 23 |
| FaultCounters6 | `bc 06 01 92 c8` | 22, 21, 18, 16, 15 |
| FaultCounters7 | `2e 06 01 52 d2` | 14, 12, 11 |

The first ID is the one the tool sends; the others are computed with the CRC-8 of
[register-crc.md](register-crc.md) and were sent in the next section. The message comments
("fault counters, numbers 57 to 51" …) and their French follow the boundaries.

### The seven 10-byte requests, 2026-11-18

The owner chose the 10-byte cut. Before any change of the definitions the seven requests of
the table above were sent as written to both boilers, same method, 06:06 to 06:13, five times
each in turn, then the last two again on the first boiler.

| Boiler | ID | Answer (status byte first) | Counters | Answered |
|---|---|---|---|---|
| `08` | `e2 06 01 92 96` | `00 14 00 01 00 01 00 00 00 00 00` | 20, 1, 1, 0, 0 | 5 of 5 |
| `08` | `d4 06 01 92 a0` | `00 00 00 00 00 06 00 00 00 01 00` | 0, 0, 6, 0, 1 | 5 of 5 |
| `08` | `de 06 01 92 aa` | `00 00 00 00 00 00 00 00 00 00 00` | 0, 0, 0, 0, 0 | 5 of 5 |
| `08` | `c0 06 01 92 b4` | `00 00 00 66 00 00 00 00 00 00 00` | 0, 102, 0, 0, 0 | 5 of 5 |
| `08` | `ca 06 01 92 be` | `00 00 00 00 00 00 00 00 00 00 00` | 0, 0, 0, 0, 0 | 5 of 5 |
| `08` | `bc 06 01 92 c8` | `00 11 00 18 00 00 00 00 00 01 00` | 17, 24, 0, 0, 1 | 15 of 15, one of them `0a 00 …` |
| `08` | `2e 06 01 52 d2` | `00 00 00 06 00 01 00` | 0, 6, 1 | 25 of 25, one of them `06 00 …` |
| `18` | `e2 06 01 92 96` | `00 0b 00 00 00 03 00 00 00 00 00` | 11, 0, 3, 0, 0 | 5 of 5 |
| `18` | `d4 06 01 92 a0` | `00 00 00 30 09 06 00 00 00 00 00` | 0, 2352, 6, 0, 0 | 5 of 5 |
| `18` | `de 06 01 92 aa` | `00 00 00 23 00 00 00 00 00 00 00` | 0, 35, 0, 0, 0 | 5 of 5 |
| `18` | `c0 06 01 92 b4` | `00 00 00 35 01 00 00 00 00 00 00` | 0, 309, 0, 0, 0 | 5 of 5 |
| `18` | `ca 06 01 92 be` | `00 00 00 00 00 01 00 00 00 00 00` | 0, 0, 1, 0, 0 | 5 of 5 |
| `18` | `bc 06 01 92 c8` | `00 0e 00 13 00 03 00 00 00 00 00` | 14, 19, 3, 0, 0 | 5 of 5 |
| `18` | `2e 06 01 52 d2` | `00 00 00 05 00 03 00` | 0, 5, 3 | 15 of 15 |

- No request was left without an answer, the two all-zero blocks of the first boiler included
  (10 of 10); with the control reads above, 29 all-zero 10-byte answers of 29.
- Every counter equals the two-byte reads.
- **Two answers of the first boiler carry no data.** At 06:06:50 the 6-byte request was
  answered `06 00 00 00 00 00 00`, and at 06:12 the 10-byte request at `0x01c8` was answered
  `0a 00 00 00 00 00 00 00 00 00 00`: the first byte is the number of bytes asked for instead
  of `00`, and all data bytes are zero where the counters are 6 and 1, and 17, 24 and 1. The
  same requests were answered with the values before and after. Over the morning: 2 such
  answers among 107 answers of the first boiler, none among 52 of the second; none in the
  earlier records of this repository.
- The models skip the first byte (`ign`), so such an answer decodes as counters at zero,
  without an error. This is a property of the memory read, not of the 10-byte cut: the 6-byte
  request is the one of the published definitions, and every message built on `memr` (fault
  history, counters, live values, fault counters) skips the byte the same way.

The owner then chose to keep the first byte as a field. The lot was first rewritten the same
day (`weishaupt-J` `78ac7af`): the seven requests above, on a base model `memrf` whose only
field is `FirstByte`, while the shared model `memr` of the other memory reads was left to skip
the byte. On 2026-11-18 the owner extended the decision to lots E, D and F, and the field was
folded into `memr` itself (`memrf` dropped, this lot's reads inherit `memr` again); the
behaviour of the fault counters is identical. In the compiled CSV each memory read now starts
with `firstbyte,,UCH,,,,"first answer byte: 0, or the number of bytes asked for when the data
read 0"` where before only the fault counters did and the others had `ign,,IGN:1`. A read of
`FaultCounters7` on the first boiler gives `0;0;6;1`; the answer without data of 06:06:50 would
give `6;0;0;0`.

The name and the comment of the field say what was seen and nothing else: `00` in front of
the data, the number of bytes asked for in front of zeros. The comment is shared by every
memory read, so its wording is general ("the data read 0"), not specific to the counters.

### Level of proof

| Statement | Counters | Level |
|---|---|---|
| address ↔ number | all 33 | source: symbol name of the firmware table |
| address ↔ number | 11, 12, 36 | also consistent with the fault history |
| two bytes, low byte first | all 33 | spacing of the symbols; values of 309 and 2352; same order as the hour counters (`bc-counters.md`) |
| meaning of the number | 32 of 33 | source: manual of the boiler, both editions |
| meaning of the number | 49 | source: later edition of the manual only (printed nine years after the first; whether it describes this firmware is not established) |
| value compared with a displayed figure | none | the tool shows no counter on this firmware |
| 12-byte request of the first version answered | 11 of the 12 messages | answered at every attempt, values equal to the two-byte reads |
| 12-byte request of the first version answered | `FaultCounters4`, first boiler (all zero) | answered 3 times out of 12 |
| 10-byte request of the lot answered as written | all 14 messages | answered at every attempt (5 to 25), values equal to the two-byte reads |
| first byte | 157 of 159 answers | `00`; the two others are the number of bytes asked for, with no data |

Toolchain, 2026-11-18: `CFG_REPO=<worktree> scripts/check.sh` clean on `weishaupt-J`
`78ac7af`, on `weishaupt-L` `d5a88bd` and on a trial integration branch (format, compile,
`ebusd --checkconfig`, 588 messages in English and in French, 269 French keys for 269
strings). Rechecked the same way after the field was folded into `memr` for lots E, D and F:
`weishaupt-J` `58345b2`, `weishaupt-L` `915f5cc`, trial integration `weishaupt-next` `de42c7c`,
clean, 588 messages in English, German and French; the field layout changed only in the
memory reads of lots E, D and F (`ign` → `firstbyte`), no message gained or lost a field.

## Equipment

Two WTC condensing boilers in cascade, automat scanned `MF=Kromschroeder;SW=1104;HW=0501`
(firmware shown by the tool as 11.0e), about 87 000 and 83 000 hours with mains on.

## Date

2026-11-17 (two-byte reads), 2026-11-18 (the six requests as written, control reads).

## Not verified

- **A 12-byte answer of zero bytes only is lost most of the time** (first boiler, 6 answered
  of 20, see "The six requests as written"). Not established: where it is lost; whether the
  second boiler behaves alike (none of its 12-byte blocks is all zero); whether another
  adapter or installation shows it.
- **Answers whose first byte is the number of bytes asked for, with all data at zero** (2 of
  107 answers of the first boiler): what the automat means by them, how often they occur
  over a longer time, and whether the second boiler sends them. The earlier statement that
  the first byte is a status byte `00` rests on answers that all had `00`.
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
