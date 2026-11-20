# Specification: two generic extensions of ebusd

Status: **approved by the owner on 2026-11-20** (« Oui, comme recommandé »): the eight choices of
section 7 as recommended — names `crc` and `fills`; the carrier not published; polling through
the carrier by default; a target's own telegram on a cache miss; strict receive check plus
`ignore`; 3-register carriers first, 4 once C1 is in the build the check uses; for A, a new
generic pull request later with #1825 closed with a pointer, **nothing upstream for now**; the
full set of `crc` keys. Implemented the same day on local branches, nothing pushed, `weishaupt`
and `crc` of the fork left as they are (see "Implementation" at the end). It follows
the decision of 2026-11-20 in [design-register-layer.md](design-register-layer.md) (option 2: a
generic extension of ebusd, maintained in the fork `aghulas/ebusd` until the maintainer merges
it). The facts of the bus are in [ebus-protocol.md](ebus-protocol.md).

Two features, independent of each other, each one pull request upstream:

- **A. Computed checksum bytes** in the master data: a definition says which byte is a checksum,
  over which bytes, with which algorithm and parameters. It generalises the `[WCRC]` / `wcrc`
  mechanism of branch `crc` (john30/ebusd#1825).
- **B. Composite reads**: the fields of one message's answer fill other, existing messages; when
  the composite telegram is answered, ebusd updates those messages and publishes their topics as
  if each had been read.

Plus a small prerequisite of B for groups of four registers: **C. message IDs longer than 7
bytes**.

Everything below was checked against the source of ebusd at upstream `master` `38db2d28`
("add typespec template option") and the fork's branch `crc` (`492867d9`, one commit on it).
Line numbers are those of branch `crc`.

---

## 1. How ebusd matches a telegram today

What both features must fit into.

**Definitions.** A CSV row is `type,circuit,level,name,comment,qq,zz,pbsb,id,` followed by groups
of field columns `name,part,type,divisor/values,unit,comment`. A column whose header name is not
one of these becomes an **attribute**: at message level when it stands before the first field
group, at field level when it stands inside it (`Message::create` and `DataField::create` pluck
the known keys, the rest of the row map is kept, `AttributedItem` in `data.h`). This is how the
`crc` branch reads `wcrc=1`. The TypeSpec emitter already writes field attributes (`@attr` on a
property, emitter option `--attrs`); it has no message-level attribute column, which is why the
`crc` branch also accepts the marker `[WCRC]` in the comment.

**Key.** Each message gets a 64-bit key (`Message::createKey`, `message.cpp:248`):

| Bits | Content |
|---|---|
| 63–61 | number of ID bytes after PB SB (**3 bits: 0 to 7**) |
| 60–56 | source: master number for a passive message, or a special value for active read / write |
| 55–48 | ZZ |
| 47–32 | PB, SB |
| 31–0 | the ID bytes after PB SB, XOR-folded four by four |

`MessageMap::find(master)` (`message.cpp:2820`) builds the key of a received telegram for the
longest ID length known (`m_maxIdLength`), then for every shorter length down to 0, and for each
tries the passive, any-source, active-read and active-write variants; within a bucket
`checkId` compares the ID bytes exactly. `MAX_ID_KEYLEN` (`message.cpp:40`) is defined and
unused. `--checkconfig` reports "max message ID length exceeded" and fails when an ID is longer
than 7 bytes (`main.cpp:411`): longer IDs overflow the 3-bit length.

**Cache.** A message keeps the raw bytes of its last telegram (`m_lastMasterData`,
`m_lastSlaveData`) with `m_lastUpdateTime` and `m_lastChangeTime`; values are decoded on demand
(`decodeLastData`). Every completed telegram — sent by ebusd (read, write, poll, scan), seen on
the bus, or injected with `inject` — goes through `BusHandler::notifyProtocolMessage`
(`bushandler.cpp:383`, called from `DirectProtocolHandler::messageCompleted` and
`MainLoop::executeInject`), which finds the message, invalidates other instances of the same name
(`MessageMap::invalidateCache`) and stores the bytes.

**Publication.** The main loop asks the message map every second for messages updated since the
last round and hands them to every data sink (MQTT, KNX) (`mainloop.cpp:355`). A message is
published because its update time moved, whoever caused it. MQTT definitions and Home Assistant
discovery are published for messages seen at least once (`mqtthandler.cpp:807`), and with the
`filter-seen` setting of the integration file discovery also raises the poll priority of those
messages.

**Read with cache.** `read` returns the cached value when it is younger than `maxage` (default
300 s), unless `-f`, `-s` or `-d` is given (`mainloop.cpp:869`). The poller skips a message
updated within the poll interval by other means (`bushandler.cpp:359`).

These three points make B cheap: if ebusd stores the right bytes in a target message, cache,
`read`, polling, MQTT, KNX and Home Assistant discovery follow without change.

---

## 2. Feature A: computed checksum bytes

### 2.1 The need, beyond one vendor

- Wolf and Weishaupt / Kromschröder controllers protect `50 22` / `50 23` (register read and
  write) and `50 00` / `50 01` (memory) with a CRC-8 in the first data byte. Reported upstream in
  2018, john30/ebusd#167 "Add support for crc8 checksum fields in messages", still open. The
  maintainer's answer then: if the devices ignore it, use `IGN:1`; he would accept a data type
  "but someone has to develop the data type and the tests for it" and kept the issue as a
  reminder. Later comments in the same issue: a Wolf boiler setting (HG15) that **is** refused
  with a wrong checksum (2023); the algorithm confirmed on Wolf vectors (2025); a request that
  ebusd "accepts CRC or 0xCC when listening", because some Wolf masters send a fixed `cc` in
  that byte and the user had to define every message twice (2025).
- The Weishaupt boiler automats are recalled by the operator of the test installation to check
  the checksum; the WCM devices ignore it ([ebus-protocol.md](ebus-protocol.md), section 3).
- john30/ebusd#1825 (fork branch `crc`) solved it for one polynomial and one layout, with a
  vendor-named marker. Upstream needs a parameter, not a vendor.

### 2.2 The algorithm, generic

The Weishaupt checksum, the Wolf checksum of #167 and the eBUS frame checksum are the **same
algorithm** with different polynomials: `crc = T[crc] XOR byte` for each byte, initial value 0,
where `T` is the table of the polynomial. ebusd already implements it for the frame
(`SymbolString::updateCrc`, `symbol.cpp:103`, polynomial 0x9B). "Initial value = first covered
byte", as `ebus-protocol.md` puts it, is what this algorithm does with an initial value of 0.
Recomputed for this document, all equal to recorded telegrams:

| Covered bytes | Polynomial | Result | Source |
|---|---|---|---|
| `25 00` | 0x5C | `4c` | Weishaupt register read |
| `25 00 02 00` | 0x5C | `cc` | Weishaupt register write |
| `1b 01 1c 01 1d 01` | 0x5C | `d9` | Weishaupt read of three registers |
| `06 01 f2 d8` | 0x5C | `e8` | Weishaupt memory read |
| `42 01 04 00 5d 01 00 00` | 0x5C | `d8` | Wolf setting HG07 = 4 (john30/ebusd#167) |

So the parameters are: algorithm (`crc8`, the only one in this proposal), polynomial, initial
value, which byte holds the result, which bytes are covered. The checksum works on the data bytes
as ebusd holds them (unescaped), unlike the frame checksum.

### 2.3 CSV syntax

A message-level attribute **`crc`** (a column in the header before the first field group):

```
crc8;poly=5c                                  the common case
crc8;poly=5c;pos=0;from=1;to=*;init=00;check=strict    the same, every default written out
```

| Key | Default | Meaning |
|---|---|---|
| first token | — | algorithm; `crc8` only for now (an unknown name is an error, so others can be added) |
| `poly` | `9b` | polynomial, hex |
| `init` | `00` | initial value, hex |
| `pos` | `0` | index of the checksum byte in the master data (0 = first byte after NN) |
| `from` | `pos+1` | index of the first covered byte |
| `to` | `*` | index after the last covered byte; `*` = end of the master data |
| `check` | `strict` | on receipt: `strict` = the telegram matches only if the byte equals the checksum; `ignore` = the byte is not checked (Wolf masters that send `cc`) |

Separators: `;` between items, `=` inside, as in value lists. Indexes are decimal.

The byte at `pos` may be in the ID or in a field:

- **in the ID** (the Wolf / Weishaupt case): the literal byte written in the ID column is a
  placeholder; it should be the checksum of the ID alone, so that a stock ebusd still sends a
  correct read (section 2.8);
- **in a field** (a checksum after the value, or at the end): the field holding it is an
  ordinary field (`HEX:1` or `IGN:1`); ebusd overwrites it when sending and checks it on
  receipt. Nothing in the key changes.

Example, Weishaupt setting written with `50 23` (one row, read and write share it through
TypeSpec's `@inherit`):

```
type,circuit,level,name,comment,qq,zz,pbsb,id,crc,*name,part,type,divisor/values,unit,comment
r,ka,,BlockingTime,,,15,5022,4c2500,crc8;poly=5c,,,UIN,,min,
w,ka,,BlockingTime,,,15,5023,4c2500,crc8;poly=5c,,,UIN,,min,
```

`write -c ka BlockingTime 2` sends `50 23 05 cc 25 00 02 00`.

Example, the Wolf write of #167 (same header), with a constant suffix after the value inside
the coverage; the placeholder `c1` is the checksum of `42 01` alone, and ebusd sends `d8` for the
value 4:

```
w,bm,,HG07,,,08,5023,c14201,crc8;poly=5c,,,UIN,,min,,suffix,,HEX:4,=5d010000,,
```

### 2.4 Compatibility with `[WCRC]` and `wcrc`

The fork keeps both forms as aliases of `crc8;poly=5c` (pos 0, from 1, to end, init 0, strict):

| In the definition | Fork build with A | Fork build `v26.1-weishaupt.1` | Stock ebusd |
|---|---|---|---|
| `[WCRC]` in the comment | computed | computed | literal byte (checksum of the ID alone) |
| attribute `wcrc=1` | computed | computed | literal byte, attribute shown by `find -a` |
| attribute `crc=crc8;poly=5c` | computed | literal byte | literal byte, attribute shown |

When both an alias and `crc` are present, `crc` wins and a notice is logged. The aliases are a
fork-only commit, not part of the upstream pull request (upstream never shipped them). They can
be dropped once no published definitions use them (section 6.3).

### 2.5 Parsing and storage

- New struct `ComputedByte` in `message.h`: `algorithm`, `poly`, `init`, `pos`, `from`, `to`
  (`SIZE_MAX` for end), `checkMode`; a static `parse(const string&, ComputedByte*, string*
  errorDescription)`, and `compute(const MasterSymbolString&)`, using a 256-entry table built
  once per polynomial (a small static cache keyed by polynomial; 0x9B reuses the frame table).
- `Message` gets `const ComputedByte* m_computed` (nullptr when absent) in place of
  `m_hasDynamicCrc`, filled in the constructor from the attributes (`crc`, then the aliases), and
  `getComputedByte()`. `derive()` copies the attributes, so derived messages inherit it.
- Validation in `Message::create` (an error rejects the row, like any other column error):
  unknown algorithm, bad hex, `pos` inside `[from, to)`, `pos` beyond the maximum master data
  length, `from >= to`, `pos` in the ID but the message is chained with differing bytes at
  `pos`. Error text: `crc <value>`.
- `MessageMap` keeps the set of distinct masks "ID positions holding a computed byte" (usually
  just `{0}`), in place of `m_hasDynamicCrc`.

### 2.6 Runtime

| Situation | Behaviour |
|---|---|
| Send (read, write, poll, scan) | `prepareMaster` builds the telegram as today, then sets byte `pos` to the checksum over `[from, to)` (generalises `calcDynamicCrc`). Also `ChainedMessage`, each part. |
| Receive, byte in the ID | the key is built with the byte cleared (generalises `keyId`); `find` first looks the telegram up as is, then, if nothing matched and the map has masks, once per mask with those positions cleared (generalises `findByKeyOf`). `checkId` skips the position and, with `check=strict`, compares it with the computed value. |
| Receive, byte in a field | key unchanged; with `strict` the telegram is stored only if the byte matches, otherwise logged as `unable to parse … checksum` like any decode error. |
| `check=ignore` | the byte is not compared; on sending it is still computed. |
| `hex` command | unchanged: sends the bytes given, computes nothing. |
| `find`, `find -a`, HTTP `/data` with definitions (`def`), `--dumpconfig` | the attribute is shown like any other; the dumped ID shows the placeholder. |
| `read -f`, `write` | as Send. The cached master data holds the computed byte, as sent. |
| `grab` | grabbed telegrams are keyed by the matching message, so the variants of one message (computed checksums of several values) collapse into one entry, as today. |

Error cases: a received telegram shorter than `to` (when `to` is a number) does not match;
a definition whose `to` exceeds its maximum length is rejected at load.

### 2.7 Code to change

`message.h` / `message.cpp`: `ComputedByte`; `Message` constructor, `checkId` (both overloads),
`prepareMaster`, `ChainedMessage::checkId` and `prepareMasterPart`; `MessageMap::add`, `find`,
`findByKeyOf`, `clear`. The `crc` branch's helpers (`isDynamicCrc`, `keyId`, `calcDynamicCrc`,
`checkDynamicCrc`, `idWithCrcOf`) become the generic ones. `ChangeLog.md`. No change in
`src/ebusd/`.

### 2.8 What a stock ebusd does with such a definition

It keeps `crc` as an unknown attribute and uses the ID as written. Reads send the precomputed
checksum of the ID alone: correct, since a read covers only the ID. Writes send the same
placeholder whatever the value: taken by devices that ignore the checksum (the WCM devices, most
Wolf settings), ignored by devices that check it (no harm, the value is not changed). A telegram
seen on the bus with another checksum does not match: the value is not updated (today's
behaviour). Nothing is sent that a stock ebusd would not send with today's definitions.

### 2.9 Tests (`src/lib/ebus/test/test_message.cpp`)

- Parser: each key, defaults, every error case above.
- Algorithm: the five vectors of 2.2, and the eBUS frame vector with the default polynomial.
- Send: read and write of 2.3, the Wolf write with the suffix, a checksum byte in a field
  (position after the value), a chained message.
- Receive: correct byte matched; wrong byte rejected (`strict`) and accepted (`ignore`, e.g. `cc`);
  two messages with the same PB SB and different registers both found; a message without
  checksum with the same PB SB still found first.
- Aliases: `[WCRC]` and `wcrc=1` behave exactly as `crc8;poly=5c` (the tests of the `crc` branch
  kept as they are).

The test table builds rows with the default field map; rows with a `crc` column need a header
row in the table, or the `Message` built directly with its attributes as the `crc` branch does.

### 2.10 TypeSpec

- `ebus-typespec` (pull request john30/ebus-typespec#8 to update): `@crc(poly, ...dd)` keeps
  emitting the precomputed byte and also sets the message attribute `crc8;poly=<poly>`.
  `@wcrc(...dd)` becomes `@crc(0x5c, ...dd)` in the fork's library (kept as a deprecated name
  while `ebusd-configuration` uses it).
- The emitter needs **message-level attributes**: a column after `id`, written in the header of
  a file only when one of its messages has a value, so files without it are emitted byte for byte
  as today. Proposed generically: `@attr` accepted on a model (today: scalar or property), and the
  `crc` value set by `@crc` through the same path.
- Options other than the default layout (`pos`, `from`, `to`, `check`) through
  `@crc(poly, ...dd)` with an options model, or `@attr("crc", "...")` written by hand. The
  common case needs nothing more.
- During the transition (section 6.3) the emitter writes both `[WCRC]` in the comment and the
  `crc` column for `@wcrc` messages, so the definitions work with every fork build.

---

## 3. Feature C: message IDs longer than 7 bytes

Needed by B for four registers in one `50 22` (9 ID bytes after PB SB); also lets Wolf and
Weishaupt boilers read 8 registers at once (17 bytes).

- Key: the length bits hold `min(length, 7)`; the XOR folding already covers every byte.
  `createKey` (both overloads) and the loop in `find`. IDs of 7 bytes and more share the length
  code and are told apart by the folded bytes, then by `checkId`, which compares every byte. A
  9-byte ID no longer looks like a 1-byte one in the key, which it does today (9 = `1001`, the top bit falls
  off, so it shares a length code with 1-byte IDs).
- `--checkconfig`: limit raised from 7 to the maximum the master data allows (no limit beyond
  `Message::create`'s length check), `main.cpp:411`.
- Tests: two 9-byte IDs differing only in the last byte both found; a 1-byte and a 9-byte ID with
  the same folded value told apart.
- Stock ebusd with such a definition: a running ebusd uses it (tried offline, 2026-11-20);
  `--checkconfig` fails. So the published definitions must not contain them until the fork
  build is the one their check runs with (section 7, choice 6).

About 30 lines and 40 lines of tests; one small pull request of its own upstream.

---

## 4. Feature B: composite reads

### 4.1 The need

One telegram can answer several values that are, for the user, separate settings: a `50 22`
with three or four registers, a `50 00` with several memory items, a manufacturer block read. A
definition of the grouped telegram is today another message with another name, another MQTT
topic, other Home Assistant entities; the grouped telegram updates only its own message
([ebus-protocol.md](ebus-protocol.md), section 4, tried offline with a stock ebusd). Grouping is
then a choice of names, and names are frozen. Wanted: group on the bus, keep one name per value.

No upstream issue asks for this as such; john30/ebusd#167 shows the symptom (a user defining
every value twice and sorting it out by topic).

### 4.2 Model

A **carrier** is an ordinary read message (active or passive) whose slave-data fields name a
**target** message. When a telegram matching the carrier is stored and decodes without error,
ebusd stores, in each target, the master data the target would have sent and the bytes of the
carrier fields that name it, as its slave data. The target then holds exactly what a read of it
would have stored: decoding, replacement values (`0x8000` "no value"), cache, `read`, polling,
MQTT and HTTP follow unchanged.

### 4.3 CSV syntax

A field-level attribute **`fills`**: the name of the target message, in the carrier's circuit.

```
type,circuit,level,name,comment,qq,zz,pbsb,id,*name,part,type,divisor/values,unit,comment,fills
r,fs1,,HolidayStart,,,35,5022,d91b011c011d01,day,,UIN,,,,HolidayStartDay,month,,UIN,,,,HolidayStartMonth,third,,UIN,,,,HolidayStartThird
```

- Several consecutive fields may name the same target; their bytes are concatenated in order.
- A field without `fills` is decoded as usual and not passed on. A constant field with
  verification (`==`) makes the whole carrier fail to decode when the value differs, which stops
  the distribution: this is how the `firstbyte` of a `50 00` answer is guarded.
- Only fields of the slave part (`s`). Fields of the master part and broadcast carriers are left
  for later (section 4.9).
- Same circuit only. Messages derived by the scan (circuit `ka.15` from a definition with no
  ZZ) keep their attributes and are resolved in their own derived circuit, so the rule holds.

### 4.4 Resolution and validation

Targets may be defined later in the same file or in another file loaded for the same device, and
messages are added at run time (scan, `define`). So:

- `Message` keeps the parsed links: `vector<FillLink>` with `{targetName, slaveOffset, length}`,
  offsets computed at load from the fixed lengths of the slave fields.
- `MessageMap::resolveFills()` resolves names to `Message*`, called where conditions are
  resolved (`ScanHelper::executeInstructions`, `scan.cpp:280`; the `--checkconfig` path in
  `main.cpp`; after `define`). It also builds the reverse map target → carriers. A map
  generation counter, bumped by `add`, `remove` and `clear`, makes a stale resolution redo itself
  on first use.

Errors. Load time (the row is rejected): a field with `fills` that has a variable length, or
after a field of variable length; a `fills` on a master-part field. Resolution time (the link is
disabled with an error logged, `--checkconfig` fails, the rest keeps working):

- no read message of that name in the circuit;
- the target is a write message, chained, or has master-data fields (its request could not be
  rebuilt without input);
- the target's destination differs from the carrier's (`SYN` matches anything);
- the target's slave length differs from the bytes given;
- the target is itself a carrier (no chains of carriers).

### 4.5 Runtime

The hook is one call in `BusHandler::notifyProtocolMessage`, after the carrier's bytes are stored
and decoded without error: `m_messages->distribute(message)`, a new `MessageMap` method in
`src/lib/ebus` so that it can be unit-tested. For each link it builds the target's master data
(`QQ` and `ZZ` of the telegram, the target's PB SB and ID, its computed byte if any), stores it
and the slave bytes in the target (`storeLastData`), invalidates the other instances of the
target's name as for any update, and logs `update <circuit> <name> from <carrier>` at the level of
the carrier's own update notice.

| Situation | Behaviour |
|---|---|
| ebusd reads the carrier (`read -f`, poll, HTTP) | answer stored in the carrier, then distributed. |
| Another master sends the carrier's telegram, seen passively | same: `find` matches active definitions for telegrams of any source, as today. |
| `inject` | same (it goes through the same hook). |
| Carrier answer empty, too short, or a verified constant differs | decode error logged for the carrier, nothing distributed, targets keep their values. |
| Target values | update time = the carrier's; change time moves only if the target's bytes changed, so MQTT "changed only" publishing works per target. |
| `read` of a target | served from the cache when younger than `maxage`, whatever filled it; otherwise the target's own telegram is sent. `read -f` always sends the target's own telegram. |
| Write to a target | as today the cached read of the same name is invalidated; also every carrier covering it, so a `read` of the carrier within `maxage` does not return the old grouped value. |
| Poll of a target | see 4.6. |
| MQTT, KNX | targets publish their own topics because their update time moved. The carrier is **not** published (4.7). |
| Home Assistant discovery | targets count as seen once filled: their entities appear without their own telegram ever being sent. |
| HTTP `/data` | carrier and targets listed; the carrier's fields show their `fills` attribute with `def`. |
| `find` | carrier listed like any message; `find -a` shows `fills`. A new `find` flag is not needed. |
| `grab` | the carrier's telegram is grabbed under the carrier. |

### 4.6 Polling through the carrier

The poller (`BusHandler::notifyProtocolStatus`, `MessageMap::getNextPoll`) picks a target due for
polling. If the target has a resolved carrier with the same destination, the **carrier** is sent
instead; the answer refreshes every target of the carrier, and the existing "updated within the
poll interval" check then skips the other targets when their turn comes. If the carrier's read
fails (timeout, empty answer, decode error), the target's own telegram is used for that target
until the next resolution, and the failure is logged once.

Why: Home Assistant discovery raises the poll priority of the messages it shows, which are the
targets; with this, grouping on the bus follows without the user doing anything, and carriers
need no poll priority of their own — which keeps them silent on a stock ebusd (4.8).

### 4.7 Is the carrier published?

**Recommendation: no.** A carrier is not handed to the data sinks (the loop in
`mainloop.cpp:355`, the MQTT definition loop and the `list` request in `mqtthandler.cpp`, KNX).
Reason: the point of the feature is one name per value; a published carrier gives every value a
second topic and a second Home Assistant entity, which is exactly the situation it removes. Its
unpassed fields (a `firstbyte`) are validity checks, not values for users. It stays readable by
`read`, `find` and HTTP for diagnosis.

Alternative: publish it too (simpler, one line less), at the cost of the double names. Or an
attribute to choose per carrier. See section 7, choice 2.

### 4.8 What a stock ebusd does with such a definition

It keeps `fills` as an unknown field attribute, and the carrier is an ordinary message under its
own name. With no poll priority on the carrier (4.6) a stock ebusd never sends it; it updates it
only if another master sends that exact telegram, and then publishes it under the carrier's name
(today's behaviour of a grouped definition: one more topic, no wrong value). Targets work as
today, by their own telegrams. Nothing is written. With a 4-register carrier a stock
`--checkconfig` fails (section 3).

### 4.9 Not in this proposal

Master-part and broadcast carriers (a broadcast that carries values of several messages), targets
in another circuit, a target served by a carrier on a cache miss of `read` (it is served by the
poller only), carriers of carriers, and splitting writes (the Weishaupt devices keep only the last
pair of a grouped write anyway).

### 4.10 Code to change

- `src/lib/ebus/data.h` / `data.cpp`: nothing new; `fills` is an attribute. A helper on
  `DataFieldSet` returning, for each slave field, its offset and fixed length.
- `src/lib/ebus/message.h` / `message.cpp`: `FillLink`; parsing in `Message::create`;
  `Message::isCarrier()`, `getFillLinks()`, `getCarriers()`; `Message::storeFromCarrier()`
  building the target's master data (shares the header building of `prepareMaster`, including
  the computed byte of A); `MessageMap::resolveFills()`, `distribute()`, generation counter,
  reverse map, `invalidateCache` extended to carriers; `getNextPoll` or its caller redirecting to
  the carrier.
- `src/ebusd/bushandler.cpp`: the call to `distribute` in `notifyProtocolMessage`; the poll
  redirect and its fallback in `notifyProtocolStatus`.
- `src/ebusd/scan.cpp`, `main.cpp`, `mainloop.cpp` (`define`): call `resolveFills`.
- `src/ebusd/mainloop.cpp`, `mqtthandler.cpp`, `knxhandler.cpp`: skip carriers in the data sinks.
- `ChangeLog.md`.

### 4.11 Tests

In `test_message.cpp` (library level, no bus):

- parsing: offsets with fixed fields; rejected rows (variable length, master part);
- resolution: each error case of 4.4; a target defined after the carrier; a derived circuit;
  re-resolution after `add`;
- distribution: the holiday date of 4.3 (`35 50 22 07 d9 1b 01 1c 01 1d 01` / `06 1e 00 0a 00
  00 00`) gives `HolidayStartDay` 30, `HolidayStartMonth` 10, `HolidayStartThird` 0, each with
  the master data of its own read, including its computed checksum byte; update and change times;
  a `50 00` carrier whose `firstbyte` is verified `==0` distributes with `00` and not with `03`;
  an empty answer distributes nothing; a target with a replacement value decodes as "no value".

In `src/ebusd` (no unit tests there today): a script test with `--inject` on a local MQTT broker,
as was done offline on 2026-11-20: one injected carrier telegram publishes the three target
topics and no carrier topic; a stock build publishes the carrier topic only.

### 4.12 TypeSpec

- `ebus-typespec`: a decorator `@fills(Target)` on a property, taking the target **model**, so a
  wrong or renamed target is a compile error; the emitter writes the normalised message name in a
  `fills` field column, added to a file's header only when used. (`@attr("fills", "Name")`
  works today with `--attrs fills`, without the check; usable for a first test.)
- The emitter checks: target in the same namespace (circuit), a read model, property in the slave
  part.
- `ebusd-configuration` (`src/wolf/`): carriers built from templates of the wolf folder, e.g. a
  `RegisterGroup` model with `@crc(0x5c, …)` over the register numbers and one `@fills` field
  per register. The register lists stay in the definitions, not in the library: nothing
  Weishaupt-specific enters `ebus-typespec`. Each carrier gets an evidence record (rule 3): the
  grouped reads of `evidence/grouped-reads.md` already compare every grouped answer with single
  reads.

---

## 5. Plan in small commits

Each commit builds, passes the unit tests, and is useful on its own. In the fork `aghulas/ebusd`,
on branches cut from upstream `master`:

| # | Branch | Commit | Size (C++ / tests, lines) |
|---|---|---|---|
| A1 | `checksum` | `ComputedByte`: parser, table, compute; unit tests; no behaviour change | 120 / 80 |
| A2 | `checksum` | send, receive, key masking and lookup through `ComputedByte`; tests of 2.9 | 150 / 120 |
| A3 | `weishaupt` only | `[WCRC]` and `wcrc=1` as aliases of `crc8;poly=5c`; the `crc` branch's tests kept | 30 / 0 |
| C1 | `long-id` | IDs longer than 7 bytes; tests | 30 / 40 |
| B1 | `composite` | `fills`: parsing, offsets, resolution, errors; tests | 200 / 150 |
| B2 | `composite` | distribution and its hook; carriers invalidated on writes to targets; tests | 120 / 120 |
| B3 | `composite` | carriers left out of MQTT, KNX and the `list` request | 30 / script |
| B4 | `composite` | poll through the carrier, with fallback | 80 / 60 |

Then `weishaupt` = upstream `master` + A1 A2 A3 + C1 + B1–B4 + the release workflow
(`d4ececb3`), replacing today's `crc` commit (A1–A3 supersede it).

TypeSpec and definitions, after the ebusd side passes its tests:

| # | Repository | Commit |
|---|---|---|
| T1 | `aghulas/ebus-typespec` | message-level attributes in the emitter (only in files that use them) |
| T2 | `aghulas/ebus-typespec` | `@crc` sets the `crc` attribute; `@wcrc` = `@crc(0x5c)`, both forms emitted during the transition |
| T3 | `aghulas/ebus-typespec` | `@fills(Target)` with its checks |
| D1 | `aghulas/ebusd-configuration` | library pin; regenerated CSV identical apart from the `crc` column (compared by script) |
| D2 | `aghulas/ebusd-configuration` | first carriers (the holiday dates of the room units, 3 registers), with evidence |
| D3 | `aghulas/ebusd-configuration` | 4-register carriers, once C1 is in the build that `scripts/check.sh` uses |

Estimated work: ebusd A + C about 2 sessions, B about 3 sessions, TypeSpec 1 to 2, definitions
and evidence 1 per batch of carriers. About 800 lines of C++ and 600 of tests in ebusd.

Verification, read-only (rule 7): unit tests; the offline Docker set-up of 2026-11-20 (stock and
fork builds, local broker, injected telegrams) for MQTT topics and discovery; then the fork build
on the test installation reading carriers only, every carrier value compared with the single
reads before and after, as in `evidence/grouped-reads.md`. Writes with the new checksum code are
the operator's to test (one WCM setting written and restored, as on 2026-11-20); the boiler
automats stay untouched.

---

## 6. How it reaches users

### 6.1 The add-on

"eBUSd (Weishaupt CRC)" (`aghulas/ha-addons`, branch `weishaupt`) downloads the static binary of
a release of the fork (`ebusd/Dockerfile`, `ARG EBUSD_RELEASE=v26.1-weishaupt.1`), built by the
fork's workflow on a `v*-weishaupt.*` tag of branch `weishaupt`. Steps, each on the owner's word
(rule 8: publishing a release, pushing a branch):

1. `weishaupt` rebuilt as in section 5 (a force-push of the fork's `weishaupt` branch).
2. Tag `v26.1-weishaupt.2`: the workflow builds aarch64 and amd64 and runs the unit tests.
3. The add-on: `EBUSD_RELEASE` and `version` (`26.1.10-weishaupt.2`), changelog. Its name could
   become "eBUSd (Weishaupt)" or follow the owner's "ebusd-weishaupt"; not needed for this.
4. Definitions with carriers released after the add-on, with a notice line: carriers need the
   add-on from version x; with the stock add-on they are silent (4.8).

### 6.2 Other users of the fork

Anyone can run the static binaries of the fork's releases with ebusd's usual options; nothing is
Home Assistant-specific. MQTT users get the per-register topics with grouped reads on the bus,
which is the reason for the choice of option 2.

### 6.3 Transition of the definitions

1. Fork build with A3 published in the add-on.
2. Library emits both `[WCRC]` and the `crc` column (T2); definitions released.
3. Once the add-on has shipped the new build for one release cycle, the library stops emitting
   `[WCRC]`; the alias stays in the fork until upstream merges A, and is dropped with the first
   fork release based on an upstream with A.

---

## 7. Open design choices

| # | Choice | Options | Recommendation |
|---|---|---|---|
| 1 | Attribute names | `crc` / `checksum`; `fills` / `target` / `updates` | `crc` (matches the decorator and #167's wording) and `fills` (`target` is ZZ in ebusd's vocabulary) |
| 2 | Is the carrier published? | no / yes / per-carrier attribute | **no** (4.7) |
| 3 | Poll through the carrier | yes, by default / opt-in per carrier / not at all | **yes, by default** (4.6): it is what makes Home Assistant discovery use grouped reads, and it keeps carriers silent on a stock ebusd |
| 4 | `read` of a target on a cache miss | own telegram / through the carrier | **own telegram**: predictable, one value asked, one value read; the poller does the grouping |
| 5 | Receive check for a checksum | strict only / `strict` and `ignore` / also a list of accepted constants | `strict` default plus `ignore` (covers the Wolf `cc` case of #167 without a second definition) |
| 6 | 4-register carriers in the published definitions | wait for C upstream / allow once `scripts/check.sh` uses the fork build / never (3 at most) | 3 registers first (dates need no more); 4 once the check runs the fork build, stated in the notice |
| 7 | Upstream form of A | new pull request "computed checksum bytes", closing #1825 with a pointer / force-push `crc` (#1825) to the new code | **a new pull request**, #1825 closed with a comment: the title and description of #1825 are Weishaupt-specific; a new one reads as a generic feature answering #167 |
| 8 | Scope of `crc` keys in the first version | full set of 2.3 / only `poly` and `check` | full set: the cost is the parser and its tests; the Wolf layout with a suffix already needs `to=*` |

Choices 2, 3 and 7 change what is built or what is visible upstream; the others are names and
defaults.

---

## 8. Upstream

One pull request per feature, generic wording, each with tests and a `ChangeLog.md` line, each
naming the Weishaupt case as one example among others:

1. **ebusd: "computed checksum bytes in master data (attribute `crc`)"** — A1, A2. Refers to
   john30/ebusd#167 (and closes it), examples: the eBUS-polynomial default, the Wolf setting write
   of #167, a Weishaupt register write. Says that `check=ignore` covers masters that send a fixed
   byte. Supersedes john30/ebusd#1825 (choice 7).
2. **ebusd: "message IDs longer than 7 bytes"** — C1. Small, independent.
3. **ebusd: "composite reads (field attribute `fills`)"** — B1–B4; depends on nothing, uses 2 only
   for groups beyond 7 ID bytes. Examples: three registers of a date; a memory block holding
   several values; any manufacturer block read whose values are also readable one by one.
4. **ebus-typespec**: message-level attributes and `@crc` (updating john30/ebus-typespec#8), then
   `@fills`.
5. **ebusd-configuration**: definitions using them, after 1 to 4 are merged.

Nothing is opened, retargeted or commented upstream without the owner's word (rule 8). Three
pull requests of this project are open and unanswered; these wait their turn the same way, and
the fork does not wait for them.

---

## Implementation (2026-11-20)

Local branches only, built and tested in an Alpine container (the build of upstream `master` does
not compile on macOS). Nothing pushed, no release, no pull request.

### `aghulas/ebusd`, cut from upstream `master` `38db2d28`

| Branch | Commits | Content |
|---|---|---|
| `checksum` | `d06e924a` A1, `05e398ce` A2 | A1: the computed byte (parser, CRC-8), no behaviour change; A2: attribute `crc` in messages |
| `wcrc-alias` | `0363a6ef` (on `checksum`) | A3: `[WCRC]` and `wcrc=1` as aliases, fork only |
| `long-id` | `aec9d6ae` | C1: IDs longer than 7 bytes |
| `composite` | `59020b45` B1, `26b2f78c` B2, `0dc15e18` B3, `55f04f61` B4 | B1: `fills` parsed and resolved; B2: carriers fill their targets; B3: carriers not published; B4: polled for their targets |
| `weishaupt-next` | `830ba9c8` … `de9f4a79` (9 commits) | upstream `master` + the commits above + the release workflow of `weishaupt`: the candidate to replace `weishaupt` |

The fork's `weishaupt` (`d4ececb3`) and `crc` (`492867d9`) are left as they are.

Differences from the text above, decided while building:

- A checksum mismatch makes the telegram not match the message, wherever the byte is (ID or
  field): it is logged as an unknown telegram, not as a decode error.
- The CRC is computed bit by bit (no table): one byte per bit shift, negligible.
- Targets of `fills` are active read messages only (not passive `u` messages).
- C is a bug fix as much as a feature: in a stock ebusd a 9-byte ID can be found for the
  telegram of a 1-byte ID with the same folded bytes (and adding it reports a duplicate). The
  unit test fails on upstream `master` and passes with the fix. No released definition triggers
  it today: upstream `ebusd-configuration` master (`9c3ed3a`), compiled and dumped by a stock
  ebusd 26.1 (12 989 messages, IDs up to 12 bytes), has no two messages sharing a key with
  different ID lengths under the old key (recomputed by script). So C1 is a latent bug, worth a
  small pull request of its own, not urgent. The same dump shows that upstream's own definitions
  already exceed the 7-byte limit, so a stock `--checkconfig` of the whole set reports "max
  message ID length exceeded" and exits with an error today.
- A carrier whose answer does not decode, or whose poll fails, is marked failed: its targets are
  polled directly until the carrier is answered again (e.g. seen on the bus) or the definitions
  change.

Checks:

- Every commit of every branch builds without a warning in the changed files and passes the four
  unit test suites (`ctest`), checked with a script that stops on a build error and runs a
  freshly built `test_message`. Checks of `test_message`: 347 on upstream `master`; A1 adds 21,
  A2 40, A3 4, C1 7, B1 12, B2 28, B4 32; 430 at the head of `weishaupt-next`. Among A2's: the
  writes of `ka BlockingTime` (register 0x0025) recorded on the bus, value 2 → `cc` and value 1 →
  `28`, sent and matched on receipt, as literal bytes. The vectors of
  section 2.2, the Wolf write of #167, the eBUS frame CRC, the holiday date of 4.3, the memory
  carrier with a verified first byte, and every load and resolution error of 4.4 are among them.
  A first assembly of `weishaupt-next` had a unit test file broken by a merge (two functions
  nested) and was tested with a stale binary; the count of 379 given for it earlier was the
  `composite` branch's. The branch was rebuilt with the test file regenerated from the feature
  branches.
- Offline, the built ebusd with a fake adapter (sends SYN, echoes, never answers), a local
  broker and injected telegrams: one 3-register and one 4-register carrier telegram publish the
  topics of the 3 and 4 single messages and no carrier topic; `read` of each single message
  answers from the cache; polls go out as the carrier telegram, then as single telegrams after
  the carrier's poll failed; `write -c fs1 HolidayStartDay 2` sends `50 23 05 dc 1b 01 02 00`
  (checksum of the value, not of the address): `fs1 HolidayStartDay` of the test file, register
  0x011b, covered bytes `1b 01 02 00`, `dc` also with the reference routine of
  [ebus-protocol.md](ebus-protocol.md) (BlockingTime, register 0x0025, gives `cc` for 2).
- Stock ebusd 26.1 loads definitions with the `crc` column and `fills` fields (same message
  count); with a 4-register carrier its `--checkconfig` fails on the ID length, the fork's
  passes.
- KNX is not built in the test container (as in the release build); its data sink is fed by the
  same loop that skips carriers.

### `aghulas/ebus-typespec`, branch `typespec-ext`

`51053ce` on `wcrc-decorator` (T1–T3 in one commit, done before the order of work was set; nothing of it is used by the fork of ebusd): `@attr` on a model (message attribute column,
only in files that use it), `@crc` and `@wcrc` set `crc=crc8;poly=<poly>` (`@wcrc` keeps the
`[WCRC]` marker for the transition), `@fills(Message)` (field column `fills`, only in files that
use it; a target in another namespace is a compile error). 93 tests pass.

### Effect on the definitions

`aghulas/ebusd-configuration` `weishaupt` (`8c7ec27`) compiled with this library: 7 files of
`src/wolf` change, by the added `crc` column only (688 rows, all `crc8;poly=5c`), checked row by
row by script; stock ebusd 26.1 and the fork build load the same 14 002 messages as before. No
carrier is defined yet (D2): each needs its evidence record first.

### Not done, needs the owner (rule 8)

1. Push the branches to `aghulas/ebusd` and `aghulas/ebus-typespec`; force-push `weishaupt` of
   `aghulas/ebusd` to `weishaupt-next`.
2. Tag `v26.1-weishaupt.2` (release workflow), then the add-on bump in `aghulas/ha-addons`.
3. Library release `v0.31.0-weishaupt.2`, library pin in `ebusd-configuration`, first carriers
   (D2) with evidence.
4. Upstream: new pull request for A (closing #167, superseding #1825), one for C, one for B, one
   for `ebus-typespec`.
