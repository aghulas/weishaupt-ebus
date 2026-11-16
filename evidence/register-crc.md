# register — the 5022 read ID carries a computed CRC-8, not 0x00

## What

For Kromschröder/Weishaupt register **reads** (`PBSB = 50 22`), the message ID is

```
<crc> <addr> <sub>
```

where `<crc>` is a CRC-8 (polynomial 0x5C, no reflection, init = first address byte)
computed over the address bytes `<addr> <sub>`. It is **not** a constant `0x00`.

Because a read's CRC depends only on the (static) address bytes, it can be precomputed at
build time and emitted as a literal first ID byte — no runtime CRC, works with stock ebusd.
(Register **writes**, `50 23`, additionally cover the data byte and cannot be precomputed.)

## How it was established

Live bus, passive capture of the frames the regulator's own controller sends (ebusd
`grab result all`), master address `31` → slave `08`, `PBSB = 5022`. Request payloads seen
(`<crc> <addr> <sub>`, trimmed to the point):

| request payload | addr sub | first byte = CRC |
|---|---|---|
| `74 0c 00` | `0c 00` | `74` |
| `cc 0e 00` | `0e 00` | `cc` |
| `94 1d 0c` | `1d 0c` | `94` |
| `7e 0c 0a` | `0c 0a` | `7e` |

The first byte varies with the address (and sub-byte: `0c 00` → `74` vs `0c 0a` → `7e`),
so it is not a constant and not a length — it tracks the address, i.e. a checksum.

Reproduction of the CRC-8 (poly 0x5C, init = first byte, then fold each further byte) for
`addr=0x0c, sub=0x00`:

```
crc = 0x0c
fold 0x00: 0c→18→30→60→c0→dc→e4→94→74 ; xor 0x00 → 0x74
```

→ `0x74`, identical to the captured frame `74 0c 00`. Same routine matches `0e 00 → cc`.

## Equipment

Kromschröder WCM/WTC regulators on eBUS, all slaves scanning as
`MF=Kromschröder` (manufacturer 0x50), `ID=W…`, software versions reported by the bus scan
(e.g. SW=6618, SW=2726, SW=7203). WTC condensing boilers with WCM-FS room units.

## Date

2026-11-16.

## Not verified

- Whether every register's CRC follows the same routine, or only the sample above — the
  routine matched every address checked, but not all ~140 read addresses were cross-checked
  frame-by-frame.
- Whether any register legitimately has CRC `0x00` (the upstream `src/kromschroeder/`
  hardcoded `0x00` would only ever reach such registers).
- The write (`50 23`) CRC, which also covers the data byte, is out of scope here.
