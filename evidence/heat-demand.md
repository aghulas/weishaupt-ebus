# Heat demand telegrams `05 07` (PowerDemand: bc1, bc2, fs1, fs2, fs3)

## What

Passive telegrams of the standard eBUS service `05 07`, nine data bytes, sent about every
20 s without an answer (master to master). Five sender / receiver pairs are on the bus, and no
other:

| circuit | QQ → ZZ | sender | receiver | file |
|---|---|---|---|---|
| bc1 | `10` → `03` | cascade manager (master address of the system manager `15`) | first boiler (master address) | `src/wolf/08.w.bc1.tsp` |
| bc2 | `10` → `13` | cascade manager | second boiler (master address) | `src/wolf/18.w.bc2.tsp` |
| fs1 | `30` → `f1` | room unit of circuit 1 | cascade manager (`f1`, slave `f6`) | `src/wolf/35.w.fs1.tsp` |
| fs2 | `70` → `f1` | room unit of circuit 2 | cascade manager | `src/wolf/75.w.fs2.tsp` |
| fs3 | `f0` → `f1` | room unit of circuit 3 | cascade manager | `src/wolf/f5.w.fs3.tsp` |

ebusd loads a file for a scanned slave address only. The telegrams to the boilers go into the
file of the boiler (receiver), as lot A does for the status telegrams the boilers send to the
manager. The receiver of the room units' telegrams, `f1`, has a slave address (`f6`) without a
file, so these go into the file of the sender. One shared model, `PowerDemand` in
`src/wolf/wtc_inc.tsp`:

| byte | field | type | established by |
|---|---|---|---|
| 1 | `Status` | `UCH`, no value list | burner starts and stops (below); values not named |
| 2 | `Ukn2` | `UCH` | nothing: unnamed |
| 3–4 | `HeatDemandTemp` | `D2C` (sixteenths), °C, no range | register reads (below) |
| 5–6 | `Ukn5` | `HEX`, 2 bytes | nothing: unnamed (`00 80` in every telegram seen) |
| 7 | `Modulation` | `D1C`, % | memory read of the boiler automat (below) |
| 8 | `DHWSetTemp` | `D1C`, °C | memory read of the boiler automat and register read of the manager |
| 9 | `Ukn9` | `UCH` | nothing: unnamed (`ff`, other values with byte 1 `66`) |

The layout of the generic `05 07` of the official configuration (`src/opdata_inc.tsp`: status,
action, boiler target temperature, target pressure, setting degree, hot water target, fuel) and
the hand-made configuration this installation used before release 0.5.2 were hints for the
positions only. Every field is named here only where an independent figure ties it; the
others keep a neutral name.

## How it was established

Read-only throughout. Passive capture: ebusd's `grab result all` buffer read over its TCP port
every 10 to 20 s, nothing sent on the bus. Independent figures: `50 22` register reads of the
system manager (`15`) and of the room units, and `50 00` memory reads of the boiler automats,
sent with ebusd's `hex` command from `31`. 2026-11-18 13:33 to 17:28 (burner off, then a heat
request of room unit 3 at 14:10 and short cycles of the second boiler until the end) and
2026-11-19 11:28 to 11:48 (hot-water period, second boiler firing). Telegrams below are the
nine data bytes after the length byte.

### Requested flow temperature of the room units (bytes 3–4)

The value equals the register `HeatDemandTemp` (`b8 02 00`, tenths) read on the same room unit
in the same minute:

| date, time | QQ → ZZ | telegram | bytes 3–4 | register read | register |
|---|---|---|---|---|---|
| 2026-11-18 13:33 | `30` → `f1` | `55 ff 50 00 00 80 ff ff ff` | 5.0 | `35`: `32 00` | 5.0 |
| 2026-11-18 13:33 | `70` → `f1` | `55 ff 70 00 00 80 ff ff ff` | 7.0 | `75`: `46 00` | 7.0 |
| 2026-11-18 13:33 | `f0` → `f1` | `bb ff 9e 01 00 80 ff ff ff` | 25.875 | `f5`: `03 01` | 25.9 |
| 2026-11-19 11:47 | `30` → `f1` | `bb ff 10 03 00 80 ff ff ff` | 49.0 | `35`: `ea 01` | 49.0 |
| 2026-11-19 11:47 | `70` → `f1` | `bb ff 42 03 00 80 ff ff ff` | 52.125 | `75`: `09 02` | 52.1 |
| 2026-11-19 11:47 | `f0` → `f1` | `bb ff 53 03 00 80 ff ff ff` | 53.1875 | `f5`: `14 02` | 53.2 |

(The register reads of 2026-11-18 went through the definitions of the release, `read -f -c
fs1 HeatDemandTemp` and so on, which print the value only; the bytes in the table are those
values in tenths.) The same equality was recorded on 2026-11-17 for three other values
([room-units-reads.md](room-units-reads.md)). Bytes 7 and 8 of the room units are `ff`, the
replacement value of `D1C`: ebusd prints `-`.

### Temperature the cascade manager sends to the boilers (bytes 3–4)

Not the heat demand of the system (`HeatDemandTemp` of `ka`, register `02 00`, 31.9 while the
telegram said 49.1). The value follows, at every point compared,

    system setpoint (register 02 00) + 10.0 K + (B24 - B22)

where B22 is the de-couple sensor (register `0d 00`, `DeCoupleTemp` of lot A), B24 the primary
sensor of the plate exchanger (register `40 0a`, read with the precomputed checksum `72`; no
definition in the release) and 10.0 K the value of the manager's register `e9 fd` (`64 00`,
tenths, read on 2026-11-18 and 2026-11-19). Register reads of `15` and the last telegram before
them:

| date, time | telegram `10 → 03` | bytes 3–4 | setpoint `02 00` | B22 `0d 00` | B24 `40 0a` | formula |
|---|---|---|---|---|---|---|
| 2026-11-18 13:39 | `55 05 12 03 00 80 00 10 ff` | 49.125 | `3f 01` 31.9 | `47 01` 32.7 | `8f 01` 39.9 | 49.1 |
| 2026-11-18 13:51 | `55 03 0d 03 00 80 00 10 ff` | 48.8125 | `3f 01` 31.9 | `44 01` 32.4 | `89 01` 39.3 | 48.8 |
| 2026-11-18 14:07 | `55 05 08 03 00 80 00 10 ff` | 48.5 | `3f 01` 31.9 | `41 01` 32.1 | `83 01` 38.7 | 48.5 |
| 2026-11-18 15:06 | `55 03 3e 04 00 80 00 10 ff` | 67.875 | `29 02` 55.3 | `5a 02` 60.2 | `74 02` 62.8 | 67.9 |
| 2026-11-19 11:47 | `ee 05 f2 04 00 80 84 64 ff` (`10 → 13`) | 79.125 | `94 02` 66.0 | `8a 02` 65.0 | `a9 02` 68.1 | 79.1 |

Over the 28 reads of 2026-11-18 13:39 to 14:07 (one a minute, burner off) the difference
between the telegram and setpoint + B24 − B22 was 9.985 K on average, with a standard
deviation of 0.055 K; against B22 alone it was 16.38 ± 0.09 K and against B24 alone 9.50 ±
0.20 K. The same value goes to both boilers.

The system manager manual (83258404, p. 87–88) defines a modulation limit temperature as the
system setpoint plus the modulation differential (parameter 538, 5 to 20 K), plus the drop
across the plate exchanger when there is one: the boilers' power is reduced as their flow
approaches it. The formula is that one with a modulation differential of 10.0 K. The manual
also says (p. 87) that 538 is to be raised when the boiler-side hydraulic optimisation is on,
which explains a value above its factory 5.0 K. That register `e9 fd` is parameter 538 rests
on its value only: no table of the manager's register numbers was at hand.

### Modulation demand (byte 7) and hot-water setpoint (byte 8)

The boiler automat holds the setpoint it receives in RAM: `50 00` memory read of the two bytes
`6e` and `6f` (request `93 01 6e 01 6f`; answer: status byte, then the two bytes), sent to
the second boiler (`18`) after each grab, 2026-11-19, second boiler firing:

| time | telegram `10 → 13` | byte 7 | byte 8 | answer of `18` | RAM `6e` | RAM `6f` |
|---|---|---|---|---|---|---|
| 11:42:32 | `ee 06 66 04 00 80 40 64 ff` | 32.0 % | 50.0 | `00 20 32` | 32 | 50 |
| 11:42:53 | `ee 06 d3 04 00 80 5c 64 ff` | 46.0 % | 50.0 | `00 2e 32` | 46 | 50 |
| 11:43:13 | `ee 05 d6 04 00 80 64 64 ff` | 50.0 % | 50.0 | `00 32 32` | 50 | 50 |
| 11:43:54 | `ee 05 db 04 00 80 70 64 ff` | 56.0 % | 50.0 | `00 38 32` | 56 | 50 |
| 11:44:15 | `ee 05 e0 04 00 80 78 64 ff` | 60.0 % | 50.0 | `00 3c 32` | 60 | 50 |
| 11:44:56 | `ee 05 ea 04 00 80 80 64 ff` | 64.0 % | 50.0 | `00 40 32` | 64 | 50 |
| 11:45:17 | `ee 05 ed 04 00 80 84 64 ff` | 66.0 % | 50.0 | `00 42 32` | 66 | 50 |

Over the 102 pairs of 11:28 to 11:46 (51 per boiler), byte 7 / 2 equalled RAM `6e` 98 times;
the four others are a change that reached the telegram before the memory read (the next pair
agrees). Byte 8 / 2 equalled RAM `6f` 102 times. The first boiler, not asked to fire, got
byte 7 = `00` and answered `00 00 32` (RAM `6e` 0, `6f` 50) at every read, for example at
11:44:15 `55 05 e0 04 00 80 00 64 ff`. On 2026-11-17 the same RAM byte read 2 and 0 while the
telegram said 2.0 % and 0 % ([bc-live-values.md](bc-live-values.md)).

The hot-water setpoint is also the manager's: 8.0 on 2026-11-18 at 13:34 (outside the
hot-water period) in the telegrams and in the register `DHWSetValue` of `ka` (`e4 03 00`,
read 8.0); 50.0 on 2026-11-19 in the hot-water period.

The modulation demand is the burner load the manager asks for, not the load: the second
boiler fired at 40 % while asked 60 % right after its start (2026-11-18 14:12), and at its
minimum 25 % while asked 2 % (15:04, status telegram of the boiler, lot A). The vendor manual
of the boiler says the info value i13 shows a power setpoint in % when the boiler is driven by
a cascade (WTC manual 83251704, p. 46).

### Byte 1 and the burner (2026-11-18)

Telegram `10 → 13` and the status the second boiler sends to the manager (`Boiler2Status` of
lot A), cached by ebusd:

| time | byte 1 | byte 7 | boiler 2 next |
|---|---|---|---|
| 14:10:26 | `00` → `ee` | 50.0 % | 14:12 burner in operation, load 40 % |
| 15:07:00 | `ee` → `00` | 0 % | 15:08 burner off |
| 15:12:22 | `00` → `ee` | 2.0 % | burner in operation, load 25 % |
| 15:17:13 | `ee` → `00` | 0 % | burner off |
| 15:23:25 | `00` → `ee` | 2.0 % | burner in operation, load 25 % |
| 15:27:16 | `ee` → `00` | 0 % | burner off |
| 15:33:59 to 16:43:29 | five more cycles the same way | | |

Byte 1 is `ee` exactly while byte 7 is not 0, and the burner follows it within about a minute.
The first boiler received `55` all the time it was not asked to fire, the second `00`. Over
both days, of 1 107 distinct telegrams to the boilers, byte 7 is 0 in every one with byte 1
`00` or `55` and above 0 in every one with byte 1 `ee` or `66`. `66` went to the first boiler
only, in 15 distinct telegrams held in ebusd's grab buffer on 2026-11-19 between the restart of
ebusd at 11:10 and the first capture at 11:28 (time of each not kept), with byte 7 from 31 % to
39 % and byte 8 50.0, for example `66 03 d3 04 00 80 4e 64 ff`; the first boiler fired during
that time, which was not observed. The room
units send `bb` and `55` (room unit 3: `bb` while heating, `55` in setback on 2026-11-17,
[modules-programs.md](modules-programs.md)). The standard eBUS values of this byte do not fit
(a room unit without hot water sending `55`, "hot water" in the standard list), so no value
is named: the field is `Status`, a plain number.

### As ebusd publishes byte 1, release 0.5.9 (2026-11-19)

ebusd prints the field `status` as a decimal number: the values of this record are `00` = 0,
`55` = 85, `66` = 102, `bb` = 187, `ee` = 238. Read from ebusd's cache over HTTP (`/data`,
nothing sent on the bus) after the installation's ebusd took release 0.5.9 at 12:13:

| circuit | updated | status | heatdemandtemp | modulation | dhwsettemp |
|---|---|---|---|---|---|
| bc1 | 12:16:08 | 85 (`55`) | 78.31 | 0.0 | 50.0 |
| bc2 | 12:16:09 | 238 (`ee`) | 78.38 | 64.0 | 50.0 |
| fs1 | 12:15:55 | 187 (`bb`) | 49.0 | - | - |
| fs2 | 12:15:57 | 187 (`bb`) | 52.12 | - | - |
| fs3 | 12:15:57 | 187 (`bb`) | 53.19 | - | - |

The same picture as the captures: the first boiler not asked for power gets 85, the second,
firing, 238; the room units, all heating, send 187. `ukn2` and `ukn9` of the room units and
`ukn9` of the boilers are empty in the cache: `ff` is the replacement value of `UCH`.

As bits the values do not fall into a pattern: every one has two equal nibbles (`0`, `5`,
`6`, `b`, `e`), like the status list of the standard `05 07` (`55`, `aa`, `bb`, `cc`, `dd`,
`ee`, `66`, `44`), which reads as a list of codes chosen far apart, not as flags; `ee` and
`66` (both "asked for power") differ by `88`, `bb` and `55` (room unit heating, setback) by
`ee`. Nothing ties a single bit to a state, so the field stays a plain number.

### Unnamed bytes

- **Byte 2**: `03` and `05` alternate from the manager while the hot-water period is off, `05`
  and `06` in it; `ff` from the room units. Nothing compared.
- **Bytes 5–6**: `00 80` in every telegram of both days (the replacement value of a signed
  two-byte number); kept as raw bytes.
- **Byte 9**: `ff` (published empty) in every telegram, except in some of the 15 with byte 1 `66`, which carry
  `81`, `83`, `86`, `8c`, `8d`, `8e` there (for example `66 03 d6 04 00 80 40 64 8d`).

## Names compared with the configuration used before release 0.5.2

The hand-made configuration of the installation defined the same telegrams as `PowerDemand`
in the circuits `bc1`, `bc2`, `fs1`, `fs2`, `fs3`, with the fields `Status`, `Action`,
`HeatDemandTemp`, `SetPressure` (ignored), `Modulation`, `DHWSetTemp`, `Fueltype` (ignored).
The lot keeps the circuit, the message name and the names `HeatDemandTemp`, `Modulation`,
`DHWSetTemp` and `Status`; ebusd publishes field names in lower case from the compiled CSV, so
the key of a value is `bc1/PowerDemand/heatdemandtemp` where it was
`bc1/PowerDemand/HeatDemandTemp`. `Action` is `ukn2`; the two ignored fields are `ukn5` and
`ukn9`, now published.

## Equipment

Kromschröder WCM-KA cascade manager (scan `SW=6618`), two Weishaupt WTC-GB boilers (`SW=1104`),
three WCM-FS room units (`SW=2726`), a plate heat exchanger between the boilers and the
heating circuits.

## Date

2026-11-18 and 2026-11-19.

## Not verified

- The meaning of each value of byte 1 (`66` in particular) and of byte 2, bytes 5–6 and byte 9.
- That register `e9 fd` of the manager is parameter 538 (value only).
- The temperature the manager sends on an installation without a plate exchanger (the manual
  drops the exchanger term then).
- A telegram to the first boiler while it fires (it did not fire during the captures).
