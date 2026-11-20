# Write methods and source address on the system manager, room units and heating modules

Write test, 2026-11-20 14:52–14:55, on the test installation (system manager `15`, room unit `35`, heating module
`51`; no boiler automat), on the operator's word, the vendor service tool disconnected (no telegram from `ff` before
or during the run). Sent through ebusd with `hex` (bytes sent as given, checksum included, source from `-s`). Each
cell: value read (`50 22`), write, read 3 s later; a changed value restored by a correct `50 23` from the source the
register is known to take, and read again. All 24 writes acknowledged `00`; every changed value restored and checked.

Methods: `50 23` with the correct checksum (CRC-8 over register and value bytes, as for reads,
[register-crc.md](register-crc.md)); `50 23` with the checksum inverted (`crc ^ ff`); `09 03 04 <reg lo> <reg hi>
<val lo> <val hi>`.

| Register | Values | `50 23` ok, ff | ok, 31 | wrong CRC, ff | wrong CRC, 31 | `09 03`, ff | `09 03`, 31 |
|---|---|---|---|---|---|---|---|
| `15` 0x0025 BlockingTime | 1 → 2 | taken | not taken | taken | not taken | taken | not taken |
| `35` 0x011b HolidayStartDay | 30 → 29 | taken | not taken | taken | not taken | taken | not taken |
| `51` 0x0a14 RoomFrostProtectionTemp | 100 → 95 | taken | not taken | taken | not taken | taken | not taken |
| `51` 0x012b SupplyMinTemp | 80 → 85 | taken | taken | taken | taken | taken | taken |

"Not taken" = acknowledged `00`, value unchanged at the read-back.

Telegrams (master part, sent from `ff` or `31`):

| Register | `50 23` correct | `50 23` wrong checksum | `09 03` |
|---|---|---|---|
| `15` 0x0025 ← 2 | `15 5023 05 cc 25 00 02 00` | `15 5023 05 33 25 00 02 00` | `15 0903 04 25 00 02 00` |
| `35` 0x011b ← 29 | `35 5023 05 fc 1b 01 1d 00` | `35 5023 05 03 1b 01 1d 00` | `35 0903 04 1b 01 1d 00` |
| `51` 0x0a14 ← 95 | `51 5023 05 4c 14 0a 5f 00` | `51 5023 05 b3 14 0a 5f 00` | `51 0903 04 14 0a 5f 00` |
| `51` 0x012b ← 85 | `51 5023 05 00 2b 01 55 00` | `51 5023 05 ff 2b 01 55 00` | `51 0903 04 2b 01 55 00` |

## What it shows

1. **The checksum byte of `50 23` is not checked** by the system manager, the room unit and the heating module: a
   write with an inverted checksum is taken exactly like a correct one. (The boiler automats were not tested.)
2. **`09 03` writes registers** on all three device types, with the same effect as `50 23`.
3. **The source rule follows the register, not the method**: 0x0025 (`15`), 0x011b (`35`) and 0x0a14 (`51`) are
   taken only from `ff`, whatever the method; 0x012b (`51`, flow minimum) is taken from `ff` and from `31`, whatever
   the method. A refused source is acknowledged `00` and leaves the value unchanged: only a read-back shows it.

## Grouped write: two registers in one `50 23` (room unit `f5`, 2026-11-20 14:56)

Same conditions, from `ff` (the holiday dates are taken only from `ff`, see the matrix). Checksum over the eight
register-and-value bytes. Values before: HolidayStartDay 0x011b = 30, HolidayStartMonth 0x011c = 10.

| Telegram (from ff) | Asked | Answer | Read 3 s later |
|---|---|---|---|
| `f5 5023 09 3c 1b 01 1d 00 1c 01 09 00` | day 29, month 9 | `00` | day **30**, month **9** |
| `f5 5023 09 34 1b 01 1e 00 1c 01 0a 00` | restore 30 / 10 | `00` | 30 / 10 |
| `f5 5023 09 80 1b 01 1c 00 1c 01 0d 00` | day 28, month 13 (out of range) | `00` | 30 / 10 (nothing taken) |
| `f5 5023 09 34 1b 01 1e 00 1c 01 0a 00` | restore 30 / 10 | `00` | 30 / 10 |

- Only the **last** register-value pair of a grouped `50 23` was taken (the month); the first (the day) was not.
  With the last value out of range, nothing was taken. So a holiday date cannot be written in one telegram this way;
  the three registers need three writes. Not yet tested: the pairs in the other order, which would tell whether the
  device keeps the last pair or the pair at a fixed position.

### Same test with the pairs reversed (2026-11-20 15:01)

Same conditions (from `ff`; the script's guard found no vendor-tool telegram in the 15 minutes before). Month pair
first, day pair last. Restored with two single writes after each step.

| Telegram (from ff) | Asked | Answer | Read 3 s later |
|---|---|---|---|
| `f5 5023 09 50 1c 01 09 00 1b 01 1d 00` | month 9, day 29 | `00` | day **29**, month **10** |
| `f5 5023 09 f4 1c 01 0d 00 1b 01 1c 00` | month 13 (out of range), day 28 | `00` | day **28**, month **10** |

- Again only the **last** pair was taken, now the day. The order of the pairs, not the register, decides which one.
- An out-of-range value in an earlier pair does not stop the last pair from being taken; in the first run nothing
  was taken only because the out-of-range value was itself in the last pair.
- Conclusion: a grouped `50 23` on the room unit writes one register, the last one; writing a date needs one
  telegram per register.
