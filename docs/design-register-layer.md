# Design note: a register layer, apart from the telegrams

Status: proposal for discussion, 2026-11-20. Nothing is built. Facts are in
[ebus-protocol.md](ebus-protocol.md).

## The problem

In ebusd a definition is at once a telegram and a name: the message `ka/HolidayStartDay` is the
telegram `15 50 22 03 <crc> 1b 01`, its MQTT topic `ebusd/ka/HolidayStartDay`, and through
discovery a Home Assistant entity. Changing how a value is fetched changes its name:

- a grouped read of three registers is another message, with another topic and other entities;
  a grouped telegram does not update the single messages, nor the reverse (tested offline);
- reading or writing without checksum (`09 02` / `09 03`) would be other messages again.

The names are frozen towards 1.0. So, with ebusd as it is, the transport cannot be improved
without new names. The owner's proposal: **a layer of registers, each with a stable name, and
methods to read and write them chosen freely** (single or grouped, with or without checksum).

What the bus allows (all tested on the test installation, 2026-11-20):

| Method | Read | Write |
|---|---|---|
| `50 22` / `50 23`, Weishaupt checksum | up to 4 registers per telegram on every WCM device, 8 on a boiler | one register per telegram (a grouped write keeps only the last pair) |
| `09 02` / `09 03`, no checksum | one register | one register, same effect and same source rule as `50 23` |
| `50 00` memory (boilers) | up to 4 items, 16 bytes each | — |

The WCM devices ignore the write checksum: a stock ebusd writes their settings (tested on the
bus). Only the boiler automats may check it, and nothing writes to them.

The current definitions are already almost one message per register. The upper layer (stable
names) exists; it is the lower layer (transport) that is tied to it.

## What ebusd offers today

Checked in the source (`src/ebusd/main_args.cpp`, `mainloop.cpp`, branch `crc` of the fork):
no plugin, script or callback mechanism. The extension points are:

- **definitions** (CSV, loaded at start, or at run time with `define` when `--enabledefine`);
- **`hex`** (with `--enablehex`): sends any telegram as given and returns the slave's bytes, with
  no definition and no decoding; it updates no message and publishes nothing on MQTT;
- **MQTT integration files** (`mqtt-hassio.cfg`): templates for topic names and Home Assistant
  discovery; they rename and filter messages, they cannot split one message into several topics
  or merge several messages into one.

A new kind of checksum or a "this group fills these registers" rule needs a change to ebusd's
C++ code, as john30/ebusd#1825 did for the checksum.

## Options

### 1. Everything in the companion, with a stock ebusd (the owner's lead)

ebusd becomes a transport. The companion keeps a register model from the metadata it already
ships (device, register, type, factor, range, write source), and for each register chooses the
method: grouped `50 22` reads of up to 4 registers of one device, `50 00` blocks for the boilers,
`50 23` writes with the checksum computed by the companion (or `09 03`). It sends them with
`hex` and decodes the answers itself.

- For: a stock ebusd (no fork, no special add-on); nothing Weishaupt-specific added to a generic
  tool; full control of grouping, pacing and write method; the checksum is computed right.
- Against:
  - `--enablehex` lets any client of ebusd's port send any telegram. Today the port already
    allows writes through definitions; `hex` widens it to everything. The stock add-on does not
    set it; the companion would need the user to add it.
  - Decoding moves from ebusd's definitions to the companion's metadata: two decoders of one
    truth, kept in step by the release process (the metadata is generated from the same TypeSpec
    as the CSV, and the fixtures test both).
  - ebusd's own cache, polling and MQTT see nothing of what the companion reads: an MQTT user
    without Home Assistant keeps today's single messages, read by ebusd separately (twice the
    bus traffic if both run).
  - The companion's client today refuses every command but `info`, `find`, `read` and one form of
    `write -h`, on purpose. `hex` with a strict whitelist (`50 22`, `50 00`, and `50 23` / `09 03`
    only through the write guard) keeps that spirit, but the guard becomes the companion's alone.

### 2. A generic extension of ebusd, proposed upstream

Two features, both useful beyond Weishaupt:

- **Composite reads**: a definition says that its fields are other messages' fields ("this
  telegram fills `HolidayStartDay`, `HolidayStartMonth`, `HolidayStartThird`"); when it is
  answered, ebusd updates those messages and publishes their topics. Topics stay per register.
- **Computed ID bytes**: a checksum type with parameters (CRC-8 with a given polynomial and
  initial value over the following bytes), instead of the Weishaupt-only `[WCRC]` marker.
  Other vendors use such checksums.

- For: every ebusd user gets the benefit, MQTT included; the definitions describe it, the
  companion stays thin.
- Against: work in ebusd's core; depends on the maintainer, who has not answered the three open
  pull requests; meanwhile it lives in the fork and the special add-on.

### 3. Both, in steps

Option 1 in the companion first, for Home Assistant users, with a stock ebusd and `hex`; the
definitions stay as they are for MQTT users. Option 2 proposed upstream as generic features,
without waiting for it.

## Recommendation

Option 3, starting with option 1, with these limits:

- the companion keeps reading through definitions by default; the register layer is an option,
  enabled when `hex` is available and the user turns it on;
- `hex` limited in the client to the services above, writes only through the existing guard,
  with the checksum computed and the source rule of the metadata;
- the entity names do not change: an entity stays bound to its register, whatever method fills
  it;
- the companion stops requiring the fork's ebusd for writes on WCM devices (the decision the
  owner deferred today), since it computes the checksum itself.

For MQTT users, nothing changes until option 2 is accepted upstream or the owner decides to
publish register topics from the companion.

## Questions for the owner

1. Option 1 needs `--enablehex` on ebusd. Acceptable on a trusted network, with the companion's
   whitelist?
2. Should MQTT users get per-register topics too (option 2, or the companion publishing them), or
   is Home Assistant the target?
3. Writes: `50 23` with a computed checksum, or `09 03` (no checksum, same effect)? `50 23` is what
   the vendor tool and the definitions use; `09 03` is what the room units use.
4. Option 2 upstream: worth proposing now, given the three unanswered pull requests?
