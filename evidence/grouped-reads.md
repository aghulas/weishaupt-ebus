# Grouped reads: several registers per `50 22`, longer `50 00` memory blocks

Read-only test, 2026-11-20 14:10–14:15, on the test installation (two WTC boiler automats, one system manager,
two heating modules, three room units). Requests sent through ebusd from its own address with `hex` (no `-s`),
one every ~2 s, after checking that no telegram from `ff` (vendor tool) had been seen for 15 minutes. Only `50 22`
register reads and `50 00` memory reads; nothing written. 122 requests, every one answered, no NAK, no timeout.

## Method

- `50 22` request: `<crc> <reg1 lo> <reg1 hi> … <regN lo> <regN hi>`, NN = 1 + 2N, the checksum over the address
  bytes as in [register-crc.md](register-crc.md) (`scripts/register-survey.py`, `crc`); answer `2N` bytes, two per
  register in request order. The checksum routine reproduces the defined single reads (`28 0d 00` SupplyTemp,
  `0d 1b 01` HolidayStartDay).
- Each grouped read is surrounded by the single reads of the same registers, just before and just after.
- `50 00` request: `<crc> 06 01 <code> <addr lo>` per [bc-fault-history.md](bc-fault-history.md) (code high nibble
  = bytes − 1, low nibble 2 = EEPROM); 12 bytes = code `b2`, 16 bytes = `f2` (the largest one item can ask). 20 bytes
  were asked as two items, `f2 d8` then `32 e8`. Each compared with two 10-byte reads (`92 d8`, `92 e2`) of the same
  range. The routine reproduces the defined `d4 06 01 d2 d8` (EventCounters) and `26 06 01 72 e6` (Counters).

## Results

| Device | Test | Request | Answer | Against single reads |
|---|---|---|---|---|
| `08` | s1-2contig (000c 000d) | `08502205480c000d00` | `0478005802` | equal |
| `08` | s1-3contig (000c 000d 000e) | `08502207f00c000d000e00` | `067800580270fe` | equal |
| `08` | s1-4mixed (000d 0016 0145 02bc) | `08502209460d0016004501bc02` | `085802120230022c00` | 0x000d, 0x02bc equal; 0x0016 and 0x0145 (return and flue gas temperature, burner running) equal to the read just before, changed by the read after |
| `18` | s1-2contig (000c 000d) | `18502205480c000d00` | `0470fe2602` | equal |
| `18` | s1-3contig (000c 000d 000e) | `18502207f00c000d000e00` | `0670fe260270fe` | equal |
| `18` | s1-4mixed (000d 0016 0145 02bc) | `18502209460d0016004501bc02` | `0826021202f4012900` | equal |
| `75` | s1-2mixed (0011 0973) | `755022059111007309` | `041c010300` | equal |
| `75` | s1-4mixed (0011 0973 0a0c 013d) | `7550220991110073090c0a3d01` | `081c01030072000000` | equal |
| `f5` | s1-2mixed (0011 0973) | `f55022059111007309` | `0420010300` | equal |
| `f5` | s1-4mixed (0011 0973 0a0c 013d) | `f550220991110073090c0a3d01` | `082001030072000000` | equal |
| `35` | s2-holstart (011b 011c 011d) | `35502207d91b011c011d01` | `061e000a000000` | equal |
| `35` | s2-holend (011e 011f 0120) | `355022070d1e011f012001` | `0601000b000000` | equal |
| `75` | s2-holstart (011b 011c 011d) | `75502207d91b011c011d01` | `061e000a000000` | equal |
| `75` | s2-holend (011e 011f 0120) | `755022070d1e011f012001` | `0601000b000000` | equal |
| `f5` | s2-holstart (011b 011c 011d) | `f5502207d91b011c011d01` | `061e000a000000` | equal |
| `f5` | s2-holend (011e 011f 0120) | `f55022070d1e011f012001` | `0601000b000000` | equal |
| `08` | s3-ref10a (01d8 x10) | `08500005ac060192d8` | `0b000000dd0000040000bf05` | reference |
| `08` | s3-ref10b (01e2 x10) | `0850000596060192e2` | `0b0000010000bb5401e54e91` | reference |
| `08` | s3-12 (01d8 x12) | `08500005900601b2d8` | `0d000000dd0000040000bf050001` | equal to the two 10-byte reads, byte for byte |
| `08` | s3-16 (01d8 x16) | `08500005e80601f2d8` | `11000000dd0000040000bf0500010000bb54` | equal to the two 10-byte reads, byte for byte |
| `08` | s3-20(2 items) (01d8 x16+01e8 x4) | `085000071c0601f2d832e8` | `15000000dd0000040000bf0500010000bb5401e54e91` | equal to the two 10-byte reads, byte for byte |
| `18` | s3-ref10a (01d8 x10) | `18500005ac060192d8` | `0b000000e20000030000fb04` | reference |
| `18` | s3-ref10b (01e2 x10) | `1850000596060192e2` | `0b00000100004a44016d4e8b` | reference |
| `18` | s3-12 (01d8 x12) | `18500005900601b2d8` | `0d000000e20000030000fb040001` | equal to the two 10-byte reads, byte for byte |
| `18` | s3-16 (01d8 x16) | `18500005e80601f2d8` | `11000000e20000030000fb04000100004a44` | equal to the two 10-byte reads, byte for byte |
| `18` | s3-20(2 items) (01d8 x16+01e8 x4) | `185000071c0601f2d832e8` | `15000000e20000030000fb04000100004a44016d4e8b` | equal to the two 10-byte reads, byte for byte |

All single reads around them answered too (`02 <lo> <hi>`); the full list is in the workbench's run file, not
versioned (installation data).

## Summary per device

| Device | Max registers per `50 22` tried | Result | `50 00` bytes tried | Result |
|---|---|---|---|---|
| `08` boiler automat | 4 (contiguous and not) | all answered, values match | 12, 16 (one item), 20 (two items) | all answered, match |
| `18` boiler automat | 4 (contiguous and not) | all answered, values match | 12, 16, 20 (two items) | all answered, match |
| `35` room unit | 3 (holiday start, holiday end) | match | — | — |
| `75` room unit | 4 (not contiguous); 3 (holiday dates) | match | — | — |
| `f5` room unit | 4 (not contiguous); 3 (holiday dates) | match | — | — |
| `15`, `51`, `52` (earlier) | 4 | ebusd's own four-register reads and the register survey (pass 1, all ok) | — | — |

- A holiday date (day, month, third) reads in one `50 22` of three registers on `35`, `75` and `f5`
  (start `1e 00 0a 00 00 00`, end `01 00 0b 00 00 00`, the same on all three).
- One `50 00` item asks at most 16 bytes (the length nibble); 20 bytes need two items in one request, which the boiler
  answers in one telegram (length byte `15` = status + 20 bytes).
- Not tried: more than 4 registers per `50 22`; more than two items per `50 00`; any grouped write (`50 23` with
  several registers): never observed on this bus, and would need its own write test.

## Second run: more registers per read, more items per memory read (2026-11-20 14:43–14:47)

Same method; 127 requests, singles before and after each grouped read.

| Device | Registers per `50 22` | Answer | Against single reads |
|---|---|---|---|
| `15` system manager | 5 | `00` (empty answer, ACK) | — (no values) |
| `15` | 6 | `00` (empty) | — |
| `15` | 8 | no answer (timeout) | — |
| `35` room unit | 5 | `00` (empty) | — |
| `35` | 6 | `00` (empty) | — |
| `35` | 8 | no answer (timeout) | — |
| `08` boiler automat | 5 | 10 bytes | equal |
| `08` | 6 | 12 bytes | equal |
| `08` | 8 | 16 bytes | equal |

| Device | `50 00` items | Request | Answer | Against 10-byte reads |
|---|---|---|---|---|
| `08` | 3 × 4 bytes (`32 d8`, `32 dc`, `32 e0`) | `08 5000 09 8c 06 01 32 d8 32 dc 32 e0` | 13 bytes: status + 12 | equal to `0x01d8`–`0x01e3` |
| `08` | 4 × 4 bytes (+ `32 e4`) | `08 5000 0b 0c 06 01 32 d8 32 dc 32 e0 32 e4` | 17 bytes: status + 16 | equal to `0x01d8`–`0x01e7` |

- The system manager and the room units take at most **4** registers per `50 22`: with 5 or 6 they acknowledge and send
  nothing; with 8 they do not answer. The boiler automat takes at least 8 (more not tried).
- A `50 00` request takes several items: 4 items of 4 bytes are answered in one telegram, in item order.
- The single reads around each test all answered; 0x01e8–0x01eb (burner starts) had advanced by one between runs.

## Summary (both runs)

| Device | Max registers per `50 22` | Max bytes per `50 00` tried |
|---|---|---|
| `08`, `18` boiler automats | ≥ 8 on `08` (8 tried), ≥ 4 on `18` (4 tried) | 20 (16 + 4, two items); 4 items × 4 bytes |
| `15` system manager | 4 (5 and 6: empty answer; 8: no answer) | — |
| `35` room unit | 4 (same as `15`) | — |
| `51`, `52` heating modules | ≥ 4 (4 tried) | — |
| `75`, `f5` room units | ≥ 4 (4 tried) | — |

## Memory areas of `50 00` (boiler `08`, read only, 2026-11-20 14:57)

On the operator's word. One byte per request, from `31`, 3 s apart; the boiler's fault-history pointer (`50 00`
`1c 06 02 12 00`) and status broadcast (cache) read before and after. Stop rule: first NAK, timeout or change.

| Item | Area (low nibble) | Telegram | Answer |
|---|---|---|---|
| `01 62` | 1 RAM (known) | `08 5000 03 3e 01 62` | `02 00 43` (status 00, byte 0x43) |
| `06 01 02 d8` | 2 EEPROM (known) | `08 5000 05 ec 06 01 02 d8` | `02 00 00` |
| `03 62` | 3 XRAM (known) | `08 5000 03 86 03 62` | `02 00 00` |
| `00 62` | 0 | `08 5000 03 62 00 62` | **NAK** — run stopped here as planned |

Before and after: fault-history pointer `03 00 31 02` both times, error field 0, burner in operation both times. Areas
4, 5 and 7–15 not tried (stop rule). Area 0 is refused with a NAK, which is a clean refusal, not a fault.

Continued on the operator's word (14:58), NAK no longer a stop, timeout or a change of the fault pointer still a stop;
the fault pointer read after each request:

| Item | Area | Telegram | Answer |
|---|---|---|---|
| `04 62` | 4 | `08 5000 03 4e 04 62` | `02 00 62` (status 00, byte 0x62 — equal to the address byte) |
| `05 62` | 5 | `08 5000 03 12 05 62` | `02 00 00` |
| `07 62` | 7 | `08 5000 03 aa 07 62` | **no answer (timeout)** — stopped here |

Fault-history pointer `03 00 31 02` before, after each request and after the stop; error field 0; burner in operation
throughout. Areas 8–15 not tried. Summary: areas 1, 2, 3, 4, 5 answer; 0 is refused (NAK); 7 does not answer.

### Areas 8–15 (2026-11-20 15:08)

Continued on the operator's word, NAK and timeout allowed, stop on a change of the fault pointer or a failed guard
read. One request was sent:

| Item | Telegram | Answer on the wire |
|---|---|---|
| `08 62` | `08 5000 03 3a 08 62` | ACK, slave part `00 31 02` |

`00 31 02` is exactly the answer to the previous request (the fault-pointer guard, `1c 06 02 12 00`): the automat
seems to resend its last answer for an area it does not know. The guard read that followed was answered with an
invalid byte and then timed out, so the run stopped; a third guard read one second later gave `03 00 31 02` again,
error field 0. Areas 9–15 not tried.

### What areas 4 and 5 are (2026-11-20 15:09–15:11)

Same boiler, read only, fault pointer read after each request (unchanged throughout, error 0). One byte at four low
addresses in every area, four bytes at 0x00, and the high-address item `06 01` before 0x62:

| Address | Area 1 (RAM) | Area 2 (EEPROM) | Area 3 (XRAM) | Area 4 | Area 5 |
|---|---|---|---|---|---|
| 0x00 | `00` | `ff` | `0e` | `00` | `00` |
| 0x10 | `f6` | `28` | `23` | `10` | `00` |
| 0x62 | `37` | `78` | `00` | `62` | `00` |
| 0xe6 | `fe` | `ff` | `00` | `e6` | `00` |
| 0x00, 4 bytes | `00 06 01 04` | `ff ff 47 32` | `0c 00 00 0a` | `00 01 02 03` | `00 00 00 00` |
| 0x0162 (`06 01`) | — | `ff` | — | `62` | `00` |

- **Area 4 returns the low byte of the address**, one byte per address, whatever the high byte: an echo, not a
  memory. It differs from every real area at the same address.
- **Area 5 returns zero everywhere tried.** It is not the program memory: the code of this 8051-type controller
  starts at 0x0000 with a jump instruction, never `00 00 00 00`. Most likely an area the automat answers but does
  not map.
- The symbol table of `WH11928` has five lists (RAM, bits, special function registers, constants, XRAM) and no
  list for any other memory, so no symbol points at area 4 or 5. At the tested addresses it names RAM `TRLIST`
  0x62 and `ROM_DPL` 0xe6, and XRAM `VARIANTE` 0xf0e6 and `secFCodeW` 0xf062 (area 3 uses the low byte); none of
  them explain the area 4 and 5 answers.
- Overall: areas 1, 2, 3 are RAM, EEPROM and XRAM; 4 is an address echo; 5 reads zero; 0 is refused (NAK); 7 does
  not answer; 8 resends the previous answer and disturbs the next exchange; 9–15 not tried.

## Third run: 5, 6 and 8 registers on the heating modules and the room units (2026-11-20 15:21–15:24)

Read only, from `31`, 2.5 s apart; eight registers per device the register survey found answering, read singly
before and after. Heating modules `51`, `52`: 0x0001 0x0002 0x0009 0x000c 0x000e 0x0010 0x0012 0x0013. Room units
`75`, `f5`: 0x0001 0x0009 0x000e 0x0010 0x0012 0x0023 0x0058 0x0059.

| Device | 5 registers | 6 registers | 8 registers |
|---|---|---|---|
| `51` heating module | `00` (empty) | `00` (empty) | no answer (timeout) |
| `52` heating module | `00` (empty) | `00` (empty) | no answer (timeout) |
| `75` room unit | `00` (empty) | `00` (empty) | no answer (timeout) |
| `f5` room unit | `00` (empty) | `00` (empty) | no answer (timeout) |

Single reads before and after gave the same values (0x0009 counts up by one between them). So every WCM device
(`15`, `35`, `51`, `52`, `75`, `f5`) answers at most **4 registers** per `50 22`: 5 and 6 give an empty
acknowledged answer, 8 no answer. Only the boiler automats go further (`08`: 8 registers answered).
