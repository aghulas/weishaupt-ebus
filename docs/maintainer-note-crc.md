# Draft — note to the maintainer on the 0x50 register-read CRC

Superseded on 2026-11-17, not to be posted: the description of #717 states this finding and
Lot A ships the reads proposed below. Kept for the record.

Written for issue john30/ebusd#167 (or PR #717).

---

On the 0x50 (Kromschröder) register reads: the first ID byte after `50 22` is not a constant
`0x00`. On a live WCM/WTC bus it is a CRC-8 (polynomial 0x5C, init = the first address byte)
over the address bytes. Captured request telegrams, for example:

```
read reg 0c 00  ->  50 22 74 0c 00     (crc 74)
read reg 0e 00  ->  50 22 cc 0e 00     (crc cc)
read reg 0c 0a  ->  50 22 7e 0c 0a     (crc 7e)
```

The current `src/wolf/_templates.tsp` `regr` hardcodes `@base(MF, 0x22, 0x00)`, so those reads
go out as `50 22 00 <addr>`, which only matches registers whose checksum is zero. Since a
read's checksum depends only on the static address, it can be precomputed and emitted as a
literal — no runtime CRC needed, stock ebusd works. (Writes `50 23` additionally cover the data
byte, so those do need a runtime CRC, which is the subject of #167 / the ebusd PR.)

Happy to send the read definitions in that form (a small `src/wolf` addition) and/or a fix for
the existing reads — whichever you prefer.
