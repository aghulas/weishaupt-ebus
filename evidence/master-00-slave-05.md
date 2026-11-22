# The participant at master `00` / slave `05`

Test installation: two Weishaupt WTC gas boilers (automats `08`, `18`), a WCM system manager (`15`, own circuit
`50`), two WCM-EM heating modules (`51`, `52`), room units `35`/`75` (one physical unit) and `f5`, all on one eBUS.
Read only, from `31` (ebusd), 2026-11-20.

## Direct reads of slave `05` (15:24)

One request every 3 s, stop at the first odd answer (none came).

| Request | Telegram | Answer |
|---|---|---|
| Identification `07 04` | `05 0704 00` | `0a 50 00 00 00 00 00 01 20 00 98`: manufacturer `50` (Kromschröder), empty ID, SW `0120`, HW `0098` (same as on 2026-11-19) |
| Register 0x0199 | `05 5022 03 45 99 01` | `02 9c 00` → 0x009c (156) |
| Register 0x019a | `05 5022 03 a1 9a 01` | `02 18 00` → 0x0018 (24) |
| Register 0x000c | `05 5022 03 74 0c 00` | `02 00 00` → 0 |
| Register 0x0025 | `05 5022 03 4c 25 00` | `02 00 00` → 0 |
| Register 0x0011 | `05 5022 03 ec 11 00` | `02 00 00` → 0 |

The same two registers on the other WCM devices (register survey, 2026-11-19/20):

| Device | 0x0199 | 0x019a |
|---|---|---|
| `35`, `75`, `f5` room units | 0x0147 | 0x001a |
| `51`, `52` heating modules | 0x0174 | 0x0003 |
| `05` | **0x009c** | **0x0018** |

So `05` speaks the WCM register protocol (`50 22`) and answers registers the other WCM devices have, with a pair
of values of its own: a device type of its own, not a copy of a known one. The three general registers read zero.

## What master `00` sends (telegram log, 24 h to 2026-11-20 15:25)

- Only one service: **identification `07 04`**, nothing else (no `50 xx`, no broadcast, no write).
- **One scan cycle about every 10 minutes** (interval between two scans of `08`: min 73 s, mean 597 s, max 22 min;
  145 cycles in 24 h), each cycle about 50 s, one target every ~2 s.
- **37 targets per cycle, in a fixed order**: the 10 present slaves `f6`, `15`, `35`, `75`, `f5`, `50`, `51`,
  `52`, `08`, `18` (all answer `ok`) and 27 absent addresses (`1c`, `3c`, `7c`, `fc`, `24`, `44`, `16`, `54`–`58`,
  `38`, `78`, `f8`, `53`, `76`, `84`, `90`–`98`), each absent one tried twice (two timeouts ~70 ms apart).
- It does not scan `05` (its own slave) nor `31`/`36` (ebusd's).
- The answers it gets are those ebusd gets for the same devices (for example `08`: `50 57 fa 00 19 33 11 04 05 01`).
- The log also holds 513 short fragments `00 00 00 …` with source and target `00` and status timeout: collisions
  or line noise, not telegrams.
- Other masters address `00`/`05` only rarely: the vendor service tool (`ff`) sent `09 02` to `00` and to `05`
  on 2026-11-19 20:06–20:07 (no answer), and ebusd identified `05` today.

## Identified: the vendor's bus interface (2026-11-22)

The vendor service tool's connection dialog (Extras, Options, Interface, entry of the vendor
interface), shown on 2026-11-22 at 21:04:38 with the tool connected: direct connection, serial
port 3, PC bus address `ff` selected (`00` offered beside it, greyed), state "connected",
**version 156.24**. After `Disconnect` the version field is empty: the figure is read from the
interface when the tool connects (the same 156.24 was noted on 2026-11-19,
`evidence/service-tool-ui-exploration.md`, "Program and connection").

| Source | Major | Minor |
|---|---|---|
| Registers `99 01`, `9a 01` of slave `05`, read by ebusd on 2026-11-20 (above) | `0x009c` = 156 | `0x0018` = 24 |
| Version the tool displays for its interface | 156 | 24 |

On the room units and the heating modules the same two registers hold the software version the
tool shows in the window title (327.26, 372.03). So slave `05` answers its version registers
with the version of the vendor's bus interface: **master `00` / slave `05` is the vendor's
eBUS interface of the service PC** (the adapter the tool calls "W-EA"), which stays on the bus
and keeps scanning it every ten minutes whether the tool is connected or not. `00` is the
interface's own address; the tool itself sends as `ff` through it. The tool's bus scan lists it
in no entry of its own (its tree starts with a "PC" entry, then the heating devices).

- Not a part of the heating system: no definition, and nothing to read from it.
- An installation without the service interface connected has no participant at `00` / `05`.
- Not verified: the 2026-11-20 read was not repeated on 2026-11-22; the scan answer
  (`SW=0120;HW=0098`) is not explained by the dialog (it shows only 156.24).

## Reading

Master `00` / slave `05` is a Kromschröder WCM-family device that polls the identity of every bus address every
ten minutes and does nothing else on the bus: the behaviour of a gateway or remote-access module that keeps a list
of present devices (for example a WCM communication module). It holds no value the heating needs from it.
This reading of 2026-11-20 is settled by the section above: it is the vendor's bus interface.
