# Composite reads: one `50 22` telegram fills several single-register messages

How the first carrier definition (feature B, field attribute `fills`) was established and proven,
read-only. A carrier is an ordinary read message whose answer fields each fill an existing
single-register message, so every value keeps its own name and MQTT topic; the carrier itself is
not published. The extension is in `aghulas/ebusd` (`v26.1-weishaupt.2-rc1`); the decorator
`@fills(Target)` is in `aghulas/ebus-typespec` `typespec-ext`. See
[../docs/ebusd-extension-spec.md](../docs/ebusd-extension-spec.md) section 4.

## The carrier: `HolidayStart` of a room unit (circuit `fs1`, slave `0x35`)

The holiday start date is three consecutive registers — `0x011b` day, `0x011c` month, `0x011d`
third (meaning not established) — already defined and read one by one as `HolidayStartDay`,
`HolidayStartMonth`, `HolidayStartThird`. The carrier reads all three in one `50 22` and fills
those three messages.

- Definition: a read message, PB SB `5022`, ID `d91b011c011d01` (the Weishaupt CRC-8 `d9` over
  the six address bytes, poly `0x5c`, attribute `crc8;poly=5c`), three `UIN` fields `day` /
  `month` / `third`, each with `fills` naming its target in the same circuit.
- Bus basis: the grouped read is the `35` row `s2-holstart` of
  [grouped-reads.md](grouped-reads.md) (read-only, 2026-11-20). Reproduced here with the message
  bytes as the definition sends and receives them:

  | message | master (request data) | slave (answer data) | decodes to |
  |---|---|---|---|
  | HolidayStart | d9 1b 01 1c 01 1d 01 | 1e 00 0a 00 00 00 | day 30, month 10, third 0 |

  The three single reads of the same registers, surrounding the grouped read, returned the same
  values (day 30 `0d 1b 01` → `1e 00`, month 10 `c5 1c 01` → `0a 00`, third 0 `99 1d 01` →
  `00 00`), as recorded in [grouped-reads.md](grouped-reads.md).

## End-to-end proof (local, 2026-11-21, read-only; nothing sent to the bus)

TypeSpec compiled to CSV with the `typespec-ext` library (`@fills` emits the `fills` column):

```
r,,,HolidayStart,...,5022,d91b011c011d01,crc8;poly=5c,day,,UIN,,,,HolidayStartDay,,month,,UIN,,,,HolidayStartMonth,,third,,UIN,,,,HolidayStartThird,
```

- `ebusd --checkconfig` on the whole `wolf` lot: loads with both the extension build
  (`v26.1-weishaupt.2-rc1`) and a stock build (`v26.1-weishaupt.1`), 1074 messages each (the
  carrier is the one added message); no error. A stock ebusd keeps `fills` as an unknown
  attribute.
- Extension build, carrier telegram injected (`--inject=stop`, no bus): ebusd decodes the carrier
  (`received read fs1 HolidayStart QQ=31: 30;10;0`) and distributes —
  `filled fs1 HolidayStartDay from HolidayStart: 30`, `... HolidayStartMonth ... 10`,
  `... HolidayStartThird ... 0`. A `read` of each target then returns its value from the cache
  with no telegram sent, so each target keeps its own name and topic.
- Stock build, same injected carrier: the carrier decodes under its own name, but `read` of a
  target falls back to the target's own telegram (no distribution) — today's behaviour, unchanged.

So the carrier reads three registers in one telegram on the extension build, each value keeps one
name and one MQTT topic, and a stock ebusd ignores `fills` and reads the registers one by one.

## Four registers in one telegram: `BoilerInfoBlock` (circuit `bc1`, boiler `0x08`) — feature C seed

A four-register carrier needs a message ID longer than 7 bytes (9 ID bytes here), which is feature
C. It reads four boiler information values in one `50 22` and fills `SupplyTemp` (register `0x000d`),
`ReturnTemp` (`0x0016`), `FlueGasTemp` (`0x0145`) and `BurnerServiceHours` (`0x02bc`).

- Definition: a read message, PB SB `5022`, ID `460d0016004501bc02` (CRC `46` over the eight
  address bytes, poly `0x5c`), four `UIN` fields, each `fills` naming its target in circuit `bc1`.
  The fields are kept `UIN` (two bytes, the width each target reads); the carrier is not published,
  so its own decoding is diagnostic only — each target applies its own type.
- Bus basis: the `08` row `s1-4mixed` of [grouped-reads.md](grouped-reads.md) (read-only).

  | message | master (request data) | slave (answer data) |
  |---|---|---|
  | BoilerInfoBlock | 46 0d 00 16 00 45 01 bc 02 | 58 02 12 02 30 02 2c 00 |

- `ebusd --checkconfig` on the whole `wolf` lot: the extension build (`v26.1-weishaupt.2-rc1`)
  loads it (1075 messages, exit 0); the stock build (`v26.1-weishaupt.1`) **rejects** it with
  `max message ID length exceeded` (exit 1). So a 4-register carrier only enters the published
  definitions once the check runs the fork build (spec section 7, choice 6).
- Extension build, carrier telegram injected (no bus): distributes —
  `filled bc1 SupplyTemp from BoilerInfoBlock: 60.0`, `ReturnTemp 53.0`, `FlueGasTemp 56.0`,
  `BurnerServiceHours 440` — each target decoded with its own type and scaling.

This seeds feature C: the four-register carrier is accepted by the fork's `--checkconfig` and
distributes to its four targets, while a stock `--checkconfig` refuses it on the ID length.
