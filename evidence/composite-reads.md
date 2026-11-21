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

## Four-register carriers (feature C): message IDs longer than 7 bytes

A four-register `50 22` carrier has a 9-byte ID, which a stock ebusd rejects (`max message ID
length exceeded`). So these carriers are **not** in the standard published set: they are compiled
only into the extension variant (`src/main-ext.tsp`, files `*.ext.tsp`), loaded by a fork ebusd
that supports long IDs. The standard set stays loadable by a stock ebusd (verified: it loads on
upstream ebusd 26.1 and `v26.1-weishaupt.1`, which both reject long IDs). Each carrier is diagnostic
and not published; its fields are typed to the targets where it reads naturally (the temperatures
as `otemp10`), the rest kept `UIN` (two bytes, the width each target reads).

Bus basis: the `s1-4mixed` rows of [grouped-reads.md](grouped-reads.md) (read-only, 2026-11-20).
Message bytes as the carrier sends/receives them:

| carrier | circuit (ZZ) | master (request data) | slave (answer data) | registers → targets |
|---|---|---|---|---|
| BoilerInfoBlock | bc1 (08) | 46 0d 00 16 00 45 01 bc 02 | 58 02 12 02 30 02 2c 00 | 000d SupplyTemp, 0016 ReturnTemp, 0145 FlueGasTemp, 02bc BurnerServiceHours |
| BoilerInfoBlock | bc2 (18) | 46 0d 00 16 00 45 01 bc 02 | 26 02 12 02 f4 01 29 00 | same four |
| RegisterSurvey | fs2 (75) | 91 11 00 73 09 0c 0a 3d 01 | 1c 01 03 00 72 00 00 00 | 0011 RoomTemp, 0973 HeatingCircuitType, 0a0c OutsideWeightedTemp, 013d HolidayTempLevel |
| RegisterSurvey | fs3 (f5) | 91 11 00 73 09 0c 0a 3d 01 | 20 01 03 00 72 00 00 00 | same four |

`BoilerInfoBlock` groups four boiler information values — a coherent read. `RegisterSurvey` on the
room units (`fs2`, `fs3`) is **not** a functional block: those four registers merely happened to be
read together in one `50 22` during the register survey; the name says so, and the carrier exists
only to spare three extra telegrams, each value still keeping its own message.

Proof (local, read-only, 2026-11-21):
- `ebusd --checkconfig`: the standard set loads on `v26.1-weishaupt.1` (1074 messages) and on
  upstream ebusd 26.1; the extension set loads on `v26.1-weishaupt.2` (1078 = 1074 + the four
  carriers) and is **rejected** on `v26.1-weishaupt.1` (`max message ID length exceeded`), which is
  why it is kept out of the standard set.
- Extension build, each carrier telegram injected (no bus): all four distribute to their targets,
  each decoded with its own type — e.g. `filled bc1 SupplyTemp from BoilerInfoBlock: 60.0`,
  `filled bc2 FlueGasTemp from BoilerInfoBlock: 50.0`, `filled fs2 HeatingCircuitType from
  RegisterSurvey: Radiator70`, `filled fs3 HolidayTempLevel from RegisterSurvey: Antifreeze`.
