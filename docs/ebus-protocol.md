# Reading and writing Weishaupt / Kromschröder devices on eBUS

What this project has established on the bus of its test installation: two WTC-GB condensing
boilers in cascade (automat software 11.04), a WCM-KA system manager, two WCM-EM heating modules,
two WCM-FS room units (one of them addressed for heating circuits 1 and 2). Every statement points
to its record under `evidence/`. The last section lists what is **not** established. Last update:
2026-11-20.

Notation: bytes in hexadecimal. A telegram is written `QQ ZZ PB SB NN data`: source, target,
service (two bytes), number of data bytes, data. A slave's answer follows a slash: `/ NN data`.

---

## 1. Who is on the bus

| Device | Master (sends) | Slave (answers) | Note |
|---|---|---|---|
| Boiler 1 (automat) | `03` | `08` | |
| Boiler 2 (automat) | `13` | `18` | |
| System manager WCM-KA (cascade manager) | `10`, `f1` | `15`, `f6` | the same software (66.18) at both slave addresses; `15` is also read at `50`, its direct circuit (circuit 1); `f6` has no definition. `f1` / `f6` is held by the system manager on this installation; a master `f1` is also seen on a second installation without a system manager (`second-installation-ebus2mqtt.md`): an observation, not a rule |
| Room unit for circuits 1 and 2 | `30`, `70` | `35`, `75` | one physical unit, two bus identities |
| Room unit for circuit 3 | `f0` | `f5` | |
| Heating modules EM #2 and EM #3 | — | `51`, `52` | slaves only |
| Unidentified participant (Kromschröder, software 01.20) | `00` | `05` | what it is, is not established |
| ebusd | `31` | `36` | its usual address, option `--address` |
| Vendor service tool (WCM-Diagnose) | `ff` | `04` | "PC address 255" in its configuration |

Circuit numbers are the vendor's: 1 = the system manager's direct circuit, 2 to 8 = heating
modules EM #2 to EM #8.

## 2. Two checksums not to confuse

1. **The eBUS frame checksum**, standard (CRC-8, polynomial 0x9B), at the end of each part of
   every telegram. The adapter and ebusd compute it; it is invisible here.
2. **The Weishaupt checksum**, specific to this vendor, **inside the data**, as their first byte,
   in the services `50 22` (register read), `50 23` (register write) and `50 00` (memory read).

The services `09 02` and `09 03` carry **no** Weishaupt checksum.

## 3. The Weishaupt checksum

CRC-8, polynomial `0x5C`, no reflection; the initial value is the **first covered byte**, then
each further byte is folded in:

```python
def crc(data):            # data = the bytes that follow the checksum in the telegram
    c = data[0]
    for b in data[1:]:
        for _ in range(8):
            c = ((c << 1) ^ 0x5C) & 0xFF if c & 0x80 else (c << 1) & 0xFF
        c ^= b
    return c
```

It covers **every data byte after it**:

| Service | Bytes covered | Consequence |
|---|---|---|
| `50 22` read | the register numbers | fixed for given registers: precomputed, a stock ebusd reads |
| `50 23` write | the register number **and the value** | depends on the value: computed when sending |
| `50 00` memory | the items of the request | fixed for a given request: precomputed |

Examples, recomputed for this document; each matches a recorded telegram:

| Bytes covered | Checksum |
|---|---|
| `25 00` (read register 0x0025) | `4c` |
| `25 00 02 00` (write 2 to 0x0025) | `cc` |
| `0c 00 0d 00` (read 0x000c and 0x000d) | `48` |
| `06 01 f2 d8` (16 bytes of EEPROM at 0x01d8) | `e8` |

**How it was established**: first on telegrams sent by the controllers themselves
(`register-crc.md`), then found again on a telegram of a Wolf boiler of the same family, taken
from the vendor's gateway and quoted in a public ebusd discussion (`register-write-crc.md`,
section 2).

**Which devices check it** (`write-methods.md`): the system manager (`15`), a room unit (`35`)
and a heating module (`51`) **do not check it on a write**: a `50 23` with the checksum inverted
is taken exactly like a correct one, from the same sources. The boiler automats were not tested;
the operator of the installation recalls that they do check it.

**What ebusd does**: a stock ebusd cannot compute a checksum that depends on the value; the
build of this project (`v26.1-weishaupt.1`, john30/ebusd#1825) computes it when sending and
checks it when receiving, for messages marked `[WCRC]` or with the attribute `wcrc`. In the
definitions those messages carry, in place of the checksum, the checksum of the address alone,
so reads stay valid on a stock ebusd. Since the controllers above do not check the checksum, a
stock ebusd should write their settings as well. Offline, a stock ebusd 26.1 with the
definitions sends for `write -s ff -c ka BlockingTime 2` exactly `ff 15 50 23 05 4c 25 00 02 00`:
the checksum of the address (`4c`), not the right one (`cc`), whatever the value (seen on a
simulated adapter that records the bytes, 2026-11-20). **On the bus, the same day**: the stock
eBUSd add-on (ebusd 26.1.26.1) with the definitions 0.6.0 sent that telegram, the system manager
acknowledged it and took the value (read back 2), and the restore to 1 was taken the same way
(`write-methods.md`). **For the system manager, the room units and the heating modules, a stock
ebusd writes the settings of these definitions**; the project's build is not needed for them.

## 4. Reading registers: `50 22`

### Request and answer

```
QQ ZZ 50 22 NN  <crc> <reg lo> <reg hi> [<reg lo> <reg hi> …]
/ NN  <val lo> <val hi> [<val lo> <val hi> …]
```

- A **register** is a 16-bit number, low byte first: `25 00` is register 0x0025.
- Each value is 16 bits, low byte first. Its meaning (signed, factor 0.1, low byte only, mask)
  depends on the register; the vendor's service tool knows seven data types (low byte unsigned
  or signed, 16 bits unsigned or signed, 16 bits masked, low byte, high byte)
  (`vendor-software-analysis.md`).
- **`0x8000` means "no value"**: the register of a function that is absent or unused. A sensor
  that is not fitted gives an ordinary number instead: −40.0 °C on the boilers, −100.0 °C
  elsewhere.
- `NN` of the request = 1 + 2 × registers; `NN` of the answer = 2 × registers.

Single read (`register-write-crc.md`):

```
31 15 50 22 03  4c 25 00
/ 02  01 00                      register 0x0025 = 1
```

### Several registers in one telegram

Registers may be contiguous or not; the checksum covers the whole list (`grouped-reads.md`,
2026-11-20: every grouped answer compared with single reads of the same registers taken just
before and after).

| Device | Largest group answered | Beyond |
|---|---|---|
| Boilers `08`, `18` | 4 on both, 8 on `08` | not tried |
| System manager `15`, room unit `35` | 4 | 5 and 6: acknowledged with an empty answer; 8: no answer |
| Room units `75`, `f5`, heating modules `51`, `52` | 4 | 5 and 6: empty answer; 8: no answer |

Two contiguous registers of a boiler:

```
31 08 50 22 05  48 0c 00 0d 00
/ 04  78 00 58 02                0x000c = 0x0078, 0x000d = 0x0258
```

A holiday date (day, month, third register) of a room unit reads in one telegram:
`35 50 22 07 d9 1b 01 1c 01 1d 01`.

**Limit of ebusd definitions**: `ebusd --checkconfig` (stock 26.1) loads every definition but
reports "max message ID length exceeded" and exits with an error as soon as an ID is longer than
**7 bytes** (`src/ebusd/main.cpp`). A read of 4 registers (9 bytes) exceeds it; 3 registers
(7 bytes) do not. A definition that must pass the project's check can group **3 registers** at
most, which is what a date needs. A running ebusd does use 4-register IDs.

### Single and grouped reads in ebusd and MQTT

Tried offline on 2026-11-20 (stock ebusd 26.1 in Docker, a local MQTT broker, telegrams injected
as already seen): three single messages for the registers of a holiday start date, and one
message reading the three registers at once.

- **Topics differ.** Each message publishes its own topic, named after the message:
  `ebusd/ka/HolidayStartDay`, `…Month`, `…Third` for the singles; one topic
  `ebusd/ka/HolidayStart` with three fields for the grouped one (with `--mqttjson`:
  `{"day": {"value": 30}, "month": {"value": 10}, "third": {"value": 0}}`; without: `30;10;0`).
- **A telegram only updates its own message.** ebusd matches a telegram to a definition by its
  ID, and a grouped read has another ID (and checksum) than the single ones: the grouped telegram
  updates only the grouped topic, the single telegrams only the single topics.
- **Home Assistant discovery follows the messages**: the grouped message gives three sensors on
  one state topic (`value_json["day"].value`…), the singles three sensors on three topics; with
  the add-on's stock MQTT file, discovery is published only for messages ebusd has seen, so a
  definition never read gets no entity.
- **A 4-register definition** (9-byte ID) fails `--checkconfig`, but a running ebusd decodes and
  publishes it.
- Value topics are not retained.

So grouping is a choice of names: an MQTT user or an automation sees other topics and other
entities. Defining grouped reads beside the single ones gives both, at the cost of two names
for one value; replacing singles by groups would be a breaking change.

### `09 02`: the same read without checksum

```
QQ ZZ 09 02 03  <reg lo> <reg hi> 02
/ 02  <val lo> <val hi>
```

Used by the vendor's service tool on the system manager, and by the room units towards their
modules (`service-tool-log.md`):

```
ff 15 09 02 03  02 00 02
/ 02  43 02                      0x0002 = 0x0243 = 579 → 57.9 °C (system setpoint)
```

The last request byte (`02`) looks like a length in bytes; no other value was tried.

## 5. Writing registers

### `50 23`

```
QQ ZZ 50 23 05  <crc> <reg lo> <reg hi> <val lo> <val hi>
/ 00                             acknowledgement
```

Write test of 2026-11-17 with read-back (`register-write-crc.md`, section 6):

```
ff 15 50 23 05  cc 25 00 02 00   / 00        write 2 to 0x0025
31 15 50 22 03  4c 25 00         / 02 02 00  read back: 2
```

### `09 03`: the same write without checksum

```
QQ ZZ 09 03 04  <reg lo> <reg hi> <val lo> <val hi>
```

Seen from the room units towards their modules (for example `70 51 09 03 04 20 0a 00 00`), and
from the vendor's service tool, which writes the fault-log selector (register 0x0b9a) this way
when its history tabs are opened. Tested on 2026-11-20 (`write-methods.md`): it **writes the
registers of the system manager, a room unit and a heating module with the same effect as
`50 23`**, under the same source rule. The operator recalls that it does not write on the
boilers; not tested.

### One register per telegram

A `50 23` carrying two register-value pairs (holiday day and month of room unit `f5`, checksum
over the eight bytes, `f5 50 23 09 3c 1b 01 1d 00 1c 01 09 00`) is acknowledged, but **only the
last pair is taken**, whichever register it is (tried in both orders); an out-of-range first pair
does not stop the last one (`write-methods.md`). A date takes one telegram per register.

### The source address decides, register by register

24 writes on 2026-11-20 (`write-methods.md`): three methods (`50 23` with the right checksum,
`50 23` with the checksum inverted, `09 03`) × two sources (`ff`, `31`) × four registers. All were
acknowledged `00`.

| Register | Taken from `ff` | Taken from `31` |
|---|---|---|
| `15` 0x0025 BlockingTime | yes, all three methods | no |
| `35` 0x011b HolidayStartDay | yes, all three methods | no |
| `51` 0x0a14 RoomFrostProtectionTemp | yes, all three methods | no |
| `51` 0x012b SupplyMinTemp | yes, all three methods | yes, all three methods |

- The rule follows the **register**, not the method or the checksum.
- Most settings are taken only from **`ff`**, the vendor service tool's address. Taken from
  ebusd's address too: the flow limits of the heating modules, the program slots, the date and
  time broadcast.
- **Acknowledged is not taken**: a refused source is acknowledged `00` and leaves the value
  unchanged; only a read-back from the device shows it.
- Two senders cannot share `ff`: **no write while the vendor service tool is connected**.

### A write acknowledged and lost: room unit 2

The room unit addressed for circuits 1 and 2 answers at `35` and at `75`, but `75` reads heating
program 1 and the setback and frost setpoints from the store of `35`. A write addressed to `75`
is acknowledged and lost; write to `35` (`room-units-shared-store.md`).

## 6. Reading memory: `50 00`

For the boiler automats, which are organised by memory, not by registers. The vendor's service
tool reads **symbols** whose addresses it takes from the symbol table of each firmware (36 tables).

### Request

```
QQ ZZ 50 00 NN  <crc> <item> [<item> …]
```

An item is a **code** byte followed by an **address** byte:

| Code | Meaning |
|---|---|
| `06 <hh>` | sets the high address byte of the following items |
| `<n><z> <ll>` | reads `n + 1` bytes from area `z` at low address `ll` |

The byte count is a nibble: **16 bytes at most per item**. Several items fit in one request:
boiler `08` answered 2, 3 and 4 items (up to 20 bytes) equal byte for byte to separate reads
(`grouped-reads.md`).

Examples (`bc-fault-history.md`, `bc-live-values.md`, `grouped-reads.md`):

```
ff 08 50 00 05  ec 06 02 92 00              EEPROM 0x0200, 10 bytes
31 08 50 00 07  40 11 62 01 68 01 6c        RAM 0x62 (2 bytes), RAM 0x68, RAM 0x6c
31 08 50 00 05  e8 06 01 f2 d8              EEPROM 0x01d8, 16 bytes
31 08 50 00 07  1c 06 01 f2 d8 32 e8        EEPROM 0x01d8 (16) then 0x01e8 (4): 20 bytes
```

### Areas

One byte read at low address `62` on boiler `08`, burner running, fault pointer read after each
request and unchanged (`grouped-reads.md`, 2026-11-20):

| Area | Answer |
|---|---|
| `0` | refused (NAK) |
| `1` RAM | data |
| `2` EEPROM | data |
| `3` XRAM (low address byte only: `03 b2` is 0xf0b2) | data |
| `4` | the low address byte itself (4 bytes at 0x00 give `00 01 02 03`): an echo, not a memory |
| `5` | `00` at every address tried: not program memory, which would start with a jump |
| `6` | not tried: `06` is the high-byte item |
| `7` | no answer (timeout) |
| `8` | acknowledged, but the boiler resent its previous answer; the next read was invalid then timed out, the one after normal |

Areas 9 to 15 were not tried and will not be: area 8 made a safety device answer wrongly for a
moment. The symbol table of this firmware (WH11928) knows RAM, bits, special function registers,
constants and XRAM only.

### Answer

```
/ NN  <first byte> <data…>
```

`NN` = 1 + bytes asked. The **first byte** is `00` in a normal answer; rarely the boiler puts
there the number of bytes asked and returns zeros for the data. The definitions make it a field
(`firstbyte`); a reading where it is not 0 is to be discarded.

## 7. Other messages on the bus

| Service | Between | What | Definition |
|---|---|---|---|
| `07 04` | ebusd → each device | standard eBUS identification (manufacturer, `W`, software, hardware) | by ebusd, at the scan |
| `50 14` | room unit ↔ module (`30`→`50`, `70`→`51`, `f0`→`52`) | requested flow setpoint, room temperature; answer: mode, pump, valves, flow, outside | `HcMode`, passive |
| `05 07` | system manager (`10`) → boilers (`03`, `13`); room units → master `f1` (the system manager on this installation) | heat demand, modulation, hot-water setpoint, state | `PowerDemand`, passive |
| `50 0a` | `f1` (the system manager on this installation) → broadcast (`fe`) | boiler status, 13 bytes | `KaStatus`, passive |
| date and time | broadcast | the installation's clock; its first field is an outside temperature | sent by the companion at second 00 |
| `09 02` / `09 03` | room units → modules, about every 20 s | read and write without checksum | not defined |

Bus load measured on 2026-11-20: about 13 % of the bus time; ebusd takes 2 to 3 %
(`out/bus-load-2026-11-20.md`, not versioned).

## 8. Open questions

1. **Writing with a stock ebusd: settled.** It works on the system manager (one register written
   and restored on the bus, 2026-11-20); the room units and heating modules ignore the checksum
   the same way. What follows for the installation notice, the companion's write requirement
   and the upstream write lots is a decision still to take.
2. **The boiler automats**: whether they check the checksum and take `09 03` (the operator
   recalls: yes and no); not tested, and the project does not write to them.
3. **The third register of the holiday dates**: reads 0 on the three room units for dates in
   October and November. The operator thinks it is the year, coded otherwise than in clear. To
   test on site: a holiday period of another year entered on a room unit's display, then read.
4. **Why some registers take `31`**: known register by register, no general rule.
5. **More than 8 registers** on the boilers: not tried. (Every WCM device, 15, 35, 75, f5, 51
   and 52, stops at 4.)
6. *Settled 2026-11-22.* **The participant at `00` / `05`** is the vendor's bus interface of
   the service PC: its version registers 0x0199 = 0x009c, 0x019a = 0x0018 are the version
   156.24 the vendor tool displays for its interface; master `00` sends only identification
   requests (`07 04`), a cycle of 37 addresses about every 10 minutes
   (`master-00-slave-05.md`). Not a part of the heating system.
7. **Room unit `35` / `75`**: shared, established by writing `35` and reading `75` 3 s later
   (`room-units-shared-store.md`): heating programs 1 and 2, the hot-water and circulation
   programs, the setback and frost setpoints. Heating program 3 is the only one not tried.

## Records

`evidence/register-crc.md`, `register-write-crc.md`, `write-methods.md`, `grouped-reads.md`,
`bc-fault-history.md`, `bc-live-values.md`, `bc-counters.md`, `service-tool-log.md`,
`vendor-software-analysis.md`, `em-hcmode.md`, `heat-demand.md`, `broadcast-kastatus.md`,
`room-units-shared-store.md`, `settings-writes.md`, `second-installation-ebus2mqtt.md`;
`docs/discoveries.md`.
