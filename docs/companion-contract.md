# Metadata of a definitions release

For developers of a user interface built on the definitions (the Home Assistant integration
`aghulas/ha-weishaupt` is the first). A release of the definitions carries, beside the CSV
archives:

| Asset | Content |
|---|---|
| `weishaupt-metadata-<version>.json` | this document |
| `weishaupt-fixtures-<version>.json` | readings from the evidence records, as test data (last section) |
| `sha256sums-<version>.txt` | checksums of the archives and of the two files |

The CSV says how to read and decode a message. The metadata says what the CSV cannot: which
device a message belongs to, where it sits in a menu, a short label in English and French,
what kind of value it is, how the vendor tool polls it, and under which conditions a setting
may be written. Everything the CSV says is copied into the JSON, so that a consumer needs no
CSV parser; nothing is retyped by hand.

## Where it comes from

- **Source**: `metadata/weishaupt.toml` on the branch `weishaupt-M` of the configuration
  fork, the top of the stack, above the translation file. The same commit pins definitions,
  translations and metadata. No upstream pull request is cut from it.
- **Generator**: `scripts/metadata.py build`, run by `scripts/release.sh` on the CSV the
  check has just compiled, English and every release language.
- **Check**: `scripts/metadata.py check`, step 7 of `scripts/check.sh`. It fails when a
  message of the lot files has no entry or two, when an entry names a message that does not
  exist or a pattern does not match the stated number of messages, when a field of a
  multi-field message has no metadata, when a written setting has no write conditions or its
  evidence records do not name it, when a label lacks a language, when a menu or an evidence
  record does not exist. A renamed, removed or added message therefore stops the check until
  the sidecar follows.

## Keys

A message is identified by `<circuit>/<name>`, for example `ka/BlockingTime`: the circuit is
the last part of the CSV file name (`15.w.ka` gives `ka`; `broadcast` for the broadcast file),
the name is the ebusd message name. These are the names `read -c <circuit> <name>` and
`write -c <circuit> <name>` take. The read line and the write line of a setting are one
message. A field is identified by its ebusd field name inside the message.

Names are the interface: an entity id must be built from circuit, message and field, never
from a label or a description.

## Structure (schema 1)

```
schema         1
definitions    version, commit of the integration branch, messages (528), csv_lines (545),
               loaded_by_ebusd (605: with the files of the official configuration that the
               archive also holds, which have no metadata), sidecar_sha256
languages      ["en", "fr"]
status         { menus, labels }: "proposed" or "accepted"
devices        <id>: type, label, circuits [{circuit, address, file}]
menus          <device type>: [{id, parent, label, source}]
messages       <circuit>/<name>: see below
groups         [{family, circuit, device, id, label, members}]
open           { poll, range, step }: keys of the messages that lack one (see "Left empty")
```

`label` and `description` are always `{ "en": …, "fr": … }`.

### Device

One per controller, not per bus address: `manager` has the circuits `ka` (address `15`) and
`em1` (address `50`), which are one device. `type` selects the menu tree: `boiler`,
`manager`, `module`, `room`, `system`. A device whose address is absent from the scan of
ebusd gets no device in the interface.

### Menu

A tree per device type, as a flat list with `parent` (empty at the root). `source` names the
menu of the vendor manual or the tab of the vendor service tool the grouping follows.

### Message

| Key | Meaning |
|---|---|
| `circuit`, `name`, `address` | as in the CSV |
| `device`, `menu` | where it belongs |
| `kind` | `live`, `state`, `counter`, `diagnostic`, `setting`, `program_slot` |
| `label` | short label, a name for an entity or a table row |
| `description` | the comment of the CSV, in each language |
| `read`, `passive` | it has a read line; it is a passive message (never requested) |
| `poll` | `passive`, `cyclic`, `on_demand`, or `null` when no record establishes one |
| `evidence` | records under `evidence/` of this repository |
| `write` | only on a setting a lot writes, see below |
| `same_as` | key of a message of the same device that reads the same register |
| `family`, `group`, `position` | for a message of a family, see "Families" |
| `compose` | for a message with several fields, see "Fields" |
| `renamed_from` | former key, when a release renames a message |
| `fields` | list, in the order of the telegram |

`kind` on the message is the default for its fields; a field may carry its own.

### Fields

Each field has `name`, `type` and, when the CSV has them, `divisor`, `unit`, `values` (the
value list, raw value to ebusd name), `min`, `max`, `step`, `description`. Fields of type
`IGN` are left out.

- A message with one field is one value: its label is the message's.
- A message with several fields has per field a `label` and a `kind`, or `skip: true` for a
  bit without a known meaning. `compose: true` on the message means a field label needs the
  message label in front to be unique on the device ("Boiler 1 status" + "Flame");
  `compose: false` means the field label stands alone.
- `guard: true` (the field `firstbyte` of the memory reads): the reading is valid only when
  this field reads 0. Otherwise every value of that reading must be discarded.
- A field matched by a pattern carries `group`, the numbers of its name (`code57` gives
  `{ "n": 57 }`).

Value-list entries have no translated label in schema 1: the ebusd name is all there is.

### Write conditions

Present only when a lot defines the write and an evidence record names the message. A
message without `write` must not be written, whatever its kind.

| Key | Meaning |
|---|---|
| `source` | source address of the captured write. `ff`: the setting is taken over only from the address of the vendor service tool, send with `write -s ff`. `31`: captured from ebusd's own address; not proven from another one |
| `runtime_checksum` | `true`: the telegram needs the register checksum computed at run time, that is an ebusd build with john30/ebusd#1825. A stock ebusd loads the message and sends a wrong checksum |
| `risk` | `comfort`: may be written directly once writes are enabled. `regulation`: only after a confirmation that shows current value, new value and range. Structural settings are never writable and never appear here |
| `proof` | `captured`: write telegram captured, acknowledged, and the register read back with the same value. `change-observed`: in addition a change of value was seen on the bus and read back |
| `open` | questions that may still remove the setting; `copy-in-use`: a room unit and its heating module both answer this register, and which copy the regulation uses is not established |

Range and step are those of the field (`min`, `max`, `step`). Nothing is written while the
vendor service tool is connected: it uses the same source address.

### Families

Weekly-program slots, fault-history slots and fault-counter blocks are described by a
pattern in the sidecar and expanded in the JSON: each message is listed, with `family`
(`program`, `fault_history`, `fault_counter`), `group` and `position` (for a program slot
`{ "day": 1…7, "slot": 1…3 }`, Monday = 1, plus `p` for a heating program). `groups` lists,
per circuit, each group with its label and its members in order: one weekly program is one
group of 21 messages. An interface shows a group as one object, not one entity per member.

## Left empty

Where no record establishes a value, the metadata has none; `open` lists the keys.

- **Polling class.** `cyclic` and `on_demand` are set only where the session log of the
  vendor service tool shows how the tool reads the value: polled while a tab is open, or
  read once when it is opened. No interval is given anywhere: the load a bus accepts has not
  been measured. For the other messages the consumer chooses.
- **Range** of two written settings (`em2/RoomSetbackTemp`, `em2/GradientCurve`) and **step**
  of five (these two, and three integer registers whose range has no step).
- **Linked bounds** (setback below normal, minimum below maximum) are in no record and
  therefore not in the metadata.

## Compatibility

The rule is in `docs/plan.md`, "Conventions", "Versions". In short: the second number of a
definitions version changes when a message or a field is renamed, removed, retyped or
inserted, or when `schema` changes; the third for additions. A consumer states the range it
accepts and still compares, message by message, with what ebusd loaded (`find -f`), because
ebusd cannot tell which release it runs.

## Fixtures

`weishaupt-fixtures-<version>.json`: `readings`, each with `circuit`, `message`, the bytes
captured on the bus (`read`: ID of the `50 22` request, `answer`: its data bytes, `write`:
data of the `50 23` telegram) and `expect`, the decoded value per field, with the evidence
record it was transcribed from. The generator checks each reading against that record and
against the definition. Schema 1 holds the 17 settings of `evidence/settings-writes.md`; the
other records are not transcribed yet (source: `evidence/fixtures.toml`).
