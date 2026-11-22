# Composite reads: one `50 22` telegram fills several single-register messages

How the first carrier definition (feature B, field attribute `fills`) was established and proven,
read-only. A carrier is an ordinary read message whose answer fields each fill an existing
single-register message, so every value keeps its own name and MQTT topic; the carrier itself is
not published. The extension is in `aghulas/ebusd` (`v26.1-weishaupt.2-rc1`); the decorator
`@fills(Target)` is in `aghulas/ebus-typespec` `typespec-ext`. See
[../docs/ebusd-extension-spec.md](../docs/ebusd-extension-spec.md) section 4.

## The carriers: three-register `50 22` composite reads (7-byte IDs)

A three-register `50 22` carrier has a 7-byte ID (the Weishaupt CRC-8 over the six address bytes,
poly `0x5c`, attribute `crc8;poly=5c`, followed by the three little-endian 16-bit register
addresses). Unlike four-register `50 22` reads (9-byte IDs, which stock `ebusd` rejects with `max
message ID length exceeded`), a three-register carrier loads cleanly on both stock `ebusd 26.1`
(`v26.1-weishaupt.1`) and the extension build (`v26.1-weishaupt.2`), so all eight proven
three-register carriers live in the single unified definition tree (`src/main.tsp`).

### Holiday start and end dates on the room units (`fs1` `0x35`, `fs2` `0x75`, `fs3` `0xf5`)

The holiday start date (`0x011b` day, `0x011c` month, `0x011d` third) and holiday end date
(`0x011e` day, `0x011f` month, `0x0120` third) are already defined and read/written one by one as
`HolidayStartDay` / `HolidayStartMonth` / `HolidayStartThird` and `HolidayEndDay` /
`HolidayEndMonth` / `HolidayEndThird`. The carriers `HolidayStart` and `HolidayEnd` read all three
registers of each date in one `50 22` telegram and fill those three messages.

Bus basis: rows `s2-holstart` and `s2-holend` on `35`, `75` and `f5` of
[grouped-reads.md](grouped-reads.md) (read-only, 2026-11-20). Message bytes as the definitions send
and receive them:

| message | circuit (ZZ) | master (request data) | slave (answer data) | decodes to |
|---|---|---|---|---|
| HolidayStart | fs1 (35) | d9 1b 01 1c 01 1d 01 | 1e 00 0a 00 00 00 | day 30, month 10, third 0 |
| HolidayEnd | fs1 (35) | 0d 1e 01 1f 01 20 01 | 01 00 0b 00 00 00 | day 1, month 11, third 0 |
| HolidayStart | fs2 (75) | d9 1b 01 1c 01 1d 01 | 1e 00 0a 00 00 00 | day 30, month 10, third 0 |
| HolidayEnd | fs2 (75) | 0d 1e 01 1f 01 20 01 | 01 00 0b 00 00 00 | day 1, month 11, third 0 |
| HolidayStart | fs3 (f5) | d9 1b 01 1c 01 1d 01 | 1e 00 0a 00 00 00 | day 30, month 10, third 0 |
| HolidayEnd | fs3 (f5) | 0d 1e 01 1f 01 20 01 | 01 00 0b 00 00 00 | day 1, month 11, third 0 |

### Boiler information temperatures (`bc1` `0x08`, `bc2` `0x18`)

The three consecutive boiler information temperatures `0x000c` (`OutsideTemp`, i33), `0x000d`
(`SupplyTemp`, i35) and `0x000e` (`DHWTemp`, i34) are read in one `50 22` telegram by the carrier
`InfoTemperatures` and distributed to `OutsideTemp`, `SupplyTemp` and `DHWTemp`.

Bus basis: row `s2-3consec` on `08` and `18` of [grouped-reads.md](grouped-reads.md) (read-only,
2026-11-20). Message bytes as the definition sends and receives them:

| message | circuit (ZZ) | master (request data) | slave (answer data) | decodes to |
|---|---|---|---|---|
| InfoTemperatures | bc1 (08) | f0 0c 00 0d 00 0e 00 | 78 00 58 02 70 fe | outside 12.0, supply 60.0, dhw -40.0 |
| InfoTemperatures | bc2 (18) | f0 0c 00 0d 00 0e 00 | 70 fe 26 02 70 fe | outside -40.0, supply 55.0, dhw -40.0 |

## End-to-end proof (local, read-only; nothing sent to the bus)

TypeSpec compiled to CSV with the `typespec-ext` library (`@fills` emits the `fills` column, and
`@crc(0x5c, ...)` emits `crc8;poly=5c` in the `crc` column without `[WCRC]` in the comment):

```
r,,,HolidayStart,...,5022,d91b011c011d01,crc8;poly=5c,day,,UIN,,,,HolidayStartDay,,month,,UIN,,,,HolidayStartMonth,,third,,UIN,,,,HolidayStartThird,
r,,,HolidayEnd,...,5022,0d1e011f012001,crc8;poly=5c,day,,UIN,,,,HolidayEndDay,,month,,UIN,,,,HolidayEndMonth,,third,,UIN,,,,HolidayEndThird,
r,,,InfoTemperatures,...,5022,f00c000d000e00,crc8;poly=5c,outside,,SIN,10,°C,,OutsideTemp,,supply,,SIN,10,°C,,SupplyTemp,,dhw,,SIN,10,°C,,DHWTemp,
```

- `ebusd --checkconfig` on the whole `wolf` lot: loads with both the extension build
  (`v26.1-weishaupt.2`) and a stock build (`v26.1-weishaupt.1`), 1081 messages each (1073 base
  messages + the 8 three-register carriers); no error. A stock ebusd keeps `fills` as an unknown
  attribute.
- Extension build, carrier telegram injected (`--inject=stop`, no bus): ebusd decodes the carrier
  (`received read fs1 HolidayStart QQ=31: 30;10;0`) and distributes —
  `filled fs1 HolidayStartDay from HolidayStart: 30`, `... HolidayStartMonth ... 10`,
  `... HolidayStartThird ... 0`. A `read` of each target then returns its value from the cache
  with no telegram sent, so each target keeps its own name and topic.
- Stock build, same injected carrier: the carrier decodes under its own name, but `read` of a
  target falls back to the target's own telegram (no distribution) — today's behaviour, unchanged.

So the eight carriers read three registers in one telegram on the extension build, each value keeps
one name and one MQTT topic, and a stock ebusd loads the exact same CSV tree and reads the registers
one by one.
