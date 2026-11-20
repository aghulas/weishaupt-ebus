# Metadata of a definitions release

For developers of a user interface built on the definitions (the Home Assistant integration
`aghulas/ha-weishaupt` is the first). A release of the definitions carries, beside the CSV
archives:

| Asset | Content |
|---|---|
| `weishaupt-metadata-<version>.json` | this document |
| `weishaupt-fixtures-<version>.json` | telegrams from the evidence records and the values ebusd decodes them to, as test data (last section) |
| `sha256sums-<version>.txt` | checksums of the archives and of the two files |

The CSV says how to read and decode a message. The metadata says what the CSV cannot: which
device a message belongs to, where it sits in a menu, a short label in English and French,
a label for each entry of a value list, what kind of value it is, how the vendor tool polls it, and under which conditions a setting
may be written. Everything the CSV says is copied into the JSON, so that a consumer needs no
CSV parser; nothing is retyped by hand.

## Where it comes from

- **Source**: `metadata/weishaupt.toml` on the `weishaupt` branch of the configuration fork.
  The same commit pins definitions, translations and metadata. No upstream pull request carries it.
- **Generator**: `scripts/metadata.py build`, run by `scripts/release.sh` on the CSV the
  check has just compiled, English and every release language.
- **Schemas**: formal JSON Schemas (Draft 2020-12) live under `schemas/metadata.schema.json`
  (schema 1) and `schemas/fixtures.schema.json` (schema 2) in this repository, validated by
  `scripts/validate-schema.py` during `scripts/release.sh`.
- **Check**: `scripts/metadata.py check`, step 7 of `scripts/check.sh`. It fails when a
  message of the lot files has no entry or two, when an entry names a message that does not
  exist or a pattern does not match the stated number of messages, when a field of a
  multi-field message has no metadata, when a written setting has no write conditions or its
  evidence records do not name it, when a label lacks a language, when a menu or an evidence
  record does not exist, when an entry of a value list has no label in every language or a
  label names an entry no value list has. A renamed, removed or added message therefore stops the check until
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
status         { menus, labels, values }: "proposed" or "accepted", and the date of the
               acceptance (all three accepted by the owner of the project on 2026-11-18;
               `values`, the labels of the value-list entries, from release 0.5.0 on)
devices        <id>: type, label, circuits [{circuit, address, file}]
menus          <device type>: [{id, parent, label, source}]
messages       <circuit>/<name>: see below
groups         [{family, circuit, device, id, label, members}]
open           { poll, range, step }: keys of the messages that lack one (see "Left empty");
               value_labels: names of the value-list entries whose label is provisional
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
| `poll` | `passive`, `cyclic`, `on_demand`, or `null` |
| `poll_basis` | `passive`; `record`: the vendor service tool was seen to read it this way; `default`: no record, the class decided for its kind; `null` with `poll` null |
| `evidence` | records under `evidence/` of this repository |
| `write` | only on a setting a lot writes, see below |
| `same_as` | key of a message of the same device that reads the same register |
| `shared_with` | (from 0.5.15) key (`<circuit>/<name>`) of the message on another device that keeps the value: this device answers the message from that device's store, a write there is read here within seconds and a write here is not kept. Set on each member of a family, not on the group; only where an evidence record shows a write on the other device read back here with no telegram in between. A message carrying it has no `write`: the value is written on the message it names, even where the CSV keeps a write line for it (the device accepts that write; an interface does not offer it). Cases: `fs2/HCProgram1<day><slot>` → `fs1/HCProgram1<day><slot>` (21 slots, no write line); `fs2/RoomSetbackTemp`, `fs2/RoomFrostProtectionTemp` → the same names on `fs1` (write line kept in the CSV). Seen on one installation; a consumer may check that both read the same before relying on it |
| `family`, `group`, `position` | for a message of a family, see "Families" |
| `compose` | for a message with several fields, see "Fields" |
| `renamed_from` | former key (`<circuit>/<name>`), when a release renames a message. Kept in later releases. First case: `ka/DHWLoadingPriority`, `ka/DHWOperationMode` up to 0.4.3; second: `ka/DHWExcessTemp`, `ka/DHWExceeded` up to 0.5.15 |
| `fields` | list, in the order of the telegram |

`kind` on the message is the default for its fields; a field may carry its own.

### Fields

Each field has `name`, `type` and, when the CSV has them, `divisor`, `unit`, `values` (the
value list, raw value to ebusd name), `value_labels` (see below), `min`, `max`, `step`,
`description`. Fields of type `IGN` are left out.

- A message with one field is one value: its label is the message's.
- A message with several fields has per field a `label` and a `kind`, or `skip: true` for a
  bit without a known meaning or a field the devices of the entry never fill (they always
  send the replacement value; from 0.5.10, `modulation` and `dhwsettemp` of the room units'
  `PowerDemand`). `compose: true` on the message means a field label needs the
  message label in front to be unique on the device ("Boiler 1 status" + "Flame");
  `compose: false` means the field label stands alone.
- `guard: true` (the field `firstbyte` of the memory reads): the reading is valid only when
  this field reads 0. Otherwise every value of that reading must be discarded.
- `absent` (from 0.5.12): the decoded value this field reads when its sensor is not fitted,
  -40.0 on the boilers, -100.0 on the system manager and the heating modules. The device sends
  it as an ordinary number, not the eBUS replacement value (which ebusd prints as `-` and the
  fixtures as `null`), so ebusd cannot mark it: an interface shows "no sensor" for a reading
  equal to `absent`, and not a temperature. Present only where an evidence record shows or
  states that value for that read.
- A field matched by a pattern carries `group`, the numbers of its name (`code57` gives
  `{ "n": 57 }`).
- `renamed_from` (from 0.6.0) on a field: its former name, when a release renames a field and
  keeps the message. Kept in later releases. A consumer that identifies an entity by circuit,
  message and field moves the entity of the former field name to the new one. In the sidecar
  it is a template on the key of the field set, `\1`, `\2` for the groups of the key's pattern
  (`"ukn([12])_(\d)" = { …, renamed_from = "ink\1_\2" }`); `scripts/metadata.py` checks that
  it gives a field name the message no longer has. First case: the 18 unknown bits of
  `HcMode` (`em1`, `em2`, `em3`), `ink1_n` → `ukn1_n`, `ink2_n` → `ukn2_n`, `opmode_n` →
  `ukn3_n`, all `skip: true`.

**Labels of the value-list entries** (from release 0.5.0 on). A field that has `values` also
has `value_labels`, with the same raw values as keys:

```
"values":       { "0": "Priority", "1": "Sliding", "2": "Parallel" }
"value_labels": { "0": { "en": "Priority", "fr": "Priorité" },
                  "1": { "en": "Sliding",  "fr": "Mobile" },
                  "2": { "en": "Parallel", "fr": "Parallèle" } }
```

- The label is only what an interface shows. ebusd returns the name (`Priority`), a write
  takes the name, an MQTT payload carries the name: a consumer maps name to label for
  display and never sends a label.
- Every entry of every value list has a label in each language of the file (the check fails
  otherwise): 7 lists, 38 entries, 793 fields in release 0.5.0. One name has one label
  wherever it is used (`on` is "On" / "Marche" on every bit).
- `open.value_labels` names the entries whose label is provisional because no source says
  what the entry is (`ForcedVenting` in 0.5.0); such a label may change in a release of the
  third number.
- In the sidecar the labels are the table `[values]`, keyed by ebusd name; the weekdays are
  not repeated there and take their label from `[days]`, which also names the days of the
  program slots.
- The on / off list labels outputs well ("Pump: On") and facts badly ("Fault: On"): for the
  bits that are facts an interface is better served by its own wording per kind of bit.
- A key added to a field without a change of `schema`: a consumer that ignores unknown keys
  is not affected.

### Write conditions

Present only when a lot defines the write and an evidence record names the message. A
message without `write` must not be written, whatever its kind. From 0.5.6 a write may sit on
a message of kind `setting` or `program_slot`; the keys are the same.

| Key | Meaning |
|---|---|
| `source` | source address of the captured write. `ff`: the setting is taken over only from the address of the vendor service tool, send with `write -s ff`. `31`: captured from ebusd's own address; not proven from another one |
| `runtime_checksum` | `true`: the telegram needs the register checksum computed at run time, that is an ebusd build with john30/ebusd#1825. A stock ebusd loads the message and sends a wrong checksum |
| `risk` | `comfort`: may be written directly once writes are enabled. `regulation`: only after a confirmation that shows current value, new value and range. Structural settings are never writable and never appear here |
| `proof` | `captured`: write telegram captured, acknowledged, and the register read back with the same value. `change-observed`: in addition a change of value was seen on the bus and read back. `family` (program slots only, from 0.5.6): a change was observed on another slot of the same program and device, named by `proof_slot`; same codec and register scheme. The captured slot itself shows `change-observed` |
| `proof_slot` | with `family`: the name of the captured slot |
| `open` | questions that may still remove the setting; `copy-in-use`: a room unit and its heating module both answer this register, and which copy the regulation uses is not established; `meaning` (from 0.5.11): the write is proven but what the value holds is not (the third register of the holiday dates; the control variation of the room units, a number whose values have no established name), so an interface should not offer it without saying so |
| `min`, `max`, `step` | (from 0.5.5) range of the write where the field has none: the definitions cannot carry a fractional bound on an integer register (setback room setpoint 10.0 to 21.5, heating curve 2.5 to 40.0). Never present when the field has them |
| `range_source` | with `min` / `max` / `step`: the document and page the range comes from |

Range and step are those of the field (`min`, `max`, `step`), or of the write conditions when
the field has none. Nothing is written while the vendor service tool is connected: it uses
the same source address.

Risk class `comfort`: the normal and setback room setpoints, the hot-water setpoint and the
program slots, on every device that writes them; every other written setting is `regulation`.
A program slot is written whole (end, start and their enable flags, one telegram per slot) and
bounded by its type; it never appears in `open.range` or `open.step`.

### Families

Weekly-program slots, fault-history slots and fault-counter blocks are described by a
pattern in the sidecar and expanded in the JSON: each message is listed, with `family`
(`program`, `fault_history`, `fault_counter`), `group` and `position` (for a program slot
`{ "day": 1…7, "slot": 1…3 }`, Monday = 1, plus `p` for a heating program). `groups` lists,
per circuit, each group with its label and its members in order: one weekly program is one
group of 21 messages. An interface shows a group as one object, not one entity per member.

## Left empty

Where no record establishes a value, the metadata has none; `open` lists the keys.

- **Polling class.** With `poll_basis: "record"`, the session log of the vendor service tool
  shows how the tool reads the value: polled while a tab is open (`cyclic`), or read once
  when it is opened (`on_demand`). With `"default"`, no record says anything and the class
  is the one decided for the kind of the message: live values `cyclic`; settings, program
  slots and diagnostics `on_demand`. Counters and states have no default, which leaves the
  service-hours counter of the boilers without a class. No interval is given anywhere: the
  load a bus accepts has not been measured, and choosing intervals is the consumer's.
- **Step** of the integer registers whose range has no step (`BlockingTime`,
  `ChangeOverTime`, `RegulationP`, `RegulationI`, `SwitchOnRuntime`): one unit of the
  register.
- **Linked bounds**. The user manual of the room unit shows them (the setback setpoint goes up
  to the normal one, the normal down to the setback one; the flow setpoints likewise), but the
  metadata has no key for them yet; a consumer applies them itself. Proposed key, not in the
  file: `write.below` / `write.above`, the name of the message on the same circuit whose
  current value bounds this one.

## Compatibility

The rule is in `docs/plan.md`, "Conventions", "Versions". In short: the second number of a
definitions version changes when a message or a field is renamed, removed, retyped or
inserted, or when `schema` changes; the third for additions. A consumer states the range it
accepts and still compares, message by message, with what ebusd loaded (`find -f`), because
ebusd cannot tell which release it runs.

## Fixtures

`weishaupt-fixtures-<version>.json` holds telegrams captured on the bus of the test
installation, for every message of the definitions, with the values they decode to. Two
uses: test data for a consumer that has no boiler (a simulated ebusd can answer from it), and
a regression test of the definitions (a recorded answer must keep decoding to the recorded
value).

### Where it comes from

- **Source**: `evidence/fixtures.toml` of this repository. A transcription: every reading
  names the evidence record that holds its telegram and the day of the capture. Nothing is
  invented or completed; a telegram is written into its record first.
- **Check**: `scripts/fixtures.py check`, in step 7 of `scripts/check.sh`. It fails when a
  reading names a message that does not exist, carries bytes or a day its record does not
  have, has a request that is not the one of the definition, or no longer decodes to the
  recorded value.
- **Decoding is ebusd's.** The ebusd release the check uses is started without a bus, loaded
  with the compiled lot files only, and fed each telegram (`--inject=stop`); it says which
  message it takes the telegram for and what every field reads (`read -v`, and
  `find -w -d -v` for a write). `decoded` and `text` are its output, not a computation of the
  generator. A release is built only with this verification (`verified.by` is `ebusd`).

### Structure (schema 2)

```
schema       2
definitions  version, commit, messages (528)
verified     { by: "ebusd", release: the ebusd build, loaded: "lot files only, no scan" }
coverage     messages, covered, readings, by_kind and by_device ({messages, covered}),
             not_covered [keys], refused_by_ebusd [keys]
readings     list, see below
```

| Key | Meaning |
|---|---|
| `circuit`, `message` | key of the message, as in the metadata |
| `device` | device id of the metadata (`boiler1`, `manager`, …) |
| `type` | `read`: a `50 22` register read or a `50 00` memory read, request and answer. `write`: a captured `50 23` telegram, acknowledged. `passive`: a telegram between other devices |
| `qq`, `zz`, `pbsb` | source address, target address, command; `zz` says which boiler or device the telegram was captured on |
| `master` | data bytes the source sent, after the length byte. For a read this is the ID of the definition, that is the request exactly as ebusd sends it; for a write: checksum, address, value |
| `slave` | data bytes of the answer, after the length byte; `""` for an acknowledged write; absent when the target is a master or the telegram a broadcast |
| `telegram` | the same as one string in the form ebusd takes with `--inject` and prints in its log: `QQZZPBSBNN<master>/NN<slave>` |
| `expect` | value per field as the evidence record states it, at the precision of the record (a record that says 11.3 agrees with 11.301). Only the fields the record states; `null` is the replacement value |
| `decoded` | value of every field as ebusd decodes it: a number, the name of a value-list entry or a text (time, hex), `null` for the replacement value (ebusd prints `-`). Field names as in the metadata |
| `text` | the values as ebusd returns them to `read -c <circuit> <message>`: joined by `;`, in field order |
| `error` | in place of `expect`, `decoded` and `text`: ebusd refuses this telegram with the definitions of this release and returns this error. A known defect, see below; none in 0.5.0 |
| `evidence`, `date` | record under `evidence/` of this repository, day of the capture |
| `case` | what the reading is an example of, see below |
| `note` | a remark |

Several readings may name the same message (a boiler idle and firing, a setting read and
written). The order of the list has no meaning.

### Cases a consumer must handle

- `first-byte-not-zero` (two readings of the fault counters of the first boiler): the answer
  of a memory read came without data, its first byte being the number of bytes asked for.
  `firstbyte` is not 0 and the counters read 0 although they are not. The reading must be
  discarded (`guard` in the metadata).
- `not-available`: a field holds the eBUS replacement value, `null` in `decoded`, `-` in
  `text` (outside temperature of the second boiler in its status, flow temperature of a
  circuit without mixer).
- `no-sensor`: a temperature reads the value the device gives for a sensor that is not
  fitted: -40 or -40.0 on a boiler, -100.0 on a heating module (`outsidetemp` of
  `em2/HcMode` and `em3/HcMode`). It decodes as a number; nothing in the telegram marks it.
- `refused`: ebusd rejects the telegram with the definitions of the release, and the reading
  carries `error`. No reading of 0.5.0 is in this case. In the fixtures built on 0.4.3 the
  two `HcMode` readings above were: -100.0 lay outside the range the field then had, and
  ebusd gave `ERR: argument value out of valid range` for the whole message. Corrected in
  0.5.0 (`evidence/em-hcmode.md`); with the definitions of 0.4.3 these two messages still
  give that error on an installation whose module has no outside sensor.

### What a consumer may rely on

- Every reading was decoded by the named ebusd build from the CSV of the same release, and
  `expect` agreed with it. `telegram` injected into that ebusd gives `text`.
- Keys and field names are those of the metadata of the same release; `coverage` says which
  messages have a reading (`not_covered` is empty in 0.5.0: 528 of 528).
- The bytes are real captures of one installation: two boilers in cascade, a system manager,
  two heating modules, two room units (one of them addressed for circuits 1 and 2, so three
  room-unit addresses). They show what these devices answered on the day
  given, not what another installation holds, and not the whole range of a value.
- Not to rely on: the number of readings per message, their order, the values of `note`.
  New readings are added without a change of schema; `schema` changes when a key is renamed,
  removed or changes meaning. Schema 1 (release 0.4.3 only) had one entry per setting with
  the keys `read`, `answer`, `write`: now `master` and `slave` of two readings of type `read`
  and `write`.
