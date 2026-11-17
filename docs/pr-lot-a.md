# Pull request text for Lot A

Used on 2026-11-16: john30/ebusd-configuration#717 was retargeted to this content (branch
`aghulas:weishaupt-pr`, same commits as `weishaupt-A`: 7 commits, 641 insertions, `.tsp` only).
Kept as the record of the title and body at that date; the text on #717 is the reference. It
was edited there on 2026-11-17 (boiler status messages, section "File names"). The branch has
changed since: 13 commits on 2026-11-17, files renamed with the identification; commit counts
and ids below are those of 2026-11-16.

---

## Title

Add Kromschröder/Weishaupt WTC read definitions to src/wolf

## Body

This extends the existing `src/wolf` (Kromschröder, manufacturer 0x50) with read definitions
for Weishaupt WTC condensing boilers and their WCM-FS controllers, which identify on eBUS as
Kromschröder. It is read-only, works with stock ebusd, and adds no new manufacturer and no
decorator `.js` in `src/`.

### Register reads carry a precomputed CRC

For 0x50 register reads (`PBSB 50 22`), the first ID byte is a CRC-8 (polynomial 0x5C,
init = first address byte) over the address bytes, not the constant `0x00` that `src/wolf`
currently emits (`regr`, `@base(MF, 0x22, 0x00)`). On a live bus the request for register
`0c 00` goes out as `74 0c 00`, for `0e 00` as `cc 0e 00`, etc. — the `0x00` form is only
correct for registers whose checksum happens to be zero.

Because a read's checksum depends only on the static address, it is precomputed and emitted as
a literal (a new `crcr` / `CrcRead` template with base `@base(MF, 0x22)`), so stock ebusd
addresses the register with no runtime CRC. (The existing `src/wolf` reads that hardcode `0x00`
look wrong for the same reason — happy to raise that separately with a capture if useful.)

### What is added

- **KA system-manager reads** (circuit `ka`): sensors, status and the read side of the main
  heating / hot-water settings.
- **Boiler status** broadcast (`KaStatus`) and the per-boiler status and burner load each boiler
  sends to the cascade master (`Boiler1Status`, `Boiler1Power`, `Boiler2Status`, `Boiler2Power`,
  in the file of the system manager, since ebusd loads no file for a master address).
- **File names** carry the identification these devices answer to the scan (`15.w.ka`,
  `50.w.em1`, ...), so that the existing Wolf files of the folder (`50..mc`) keep being picked
  for devices with another identification.
- **Room-controller / heating-module exchange** (`HcMode`) for three modules.
- **System clock** and the weekly **circulation** and **hot-water** programs (read side), on the
  heating module.

### Verification

Every definition was checked against a live bus (Weishaupt WTC boilers with WCM-FS modules):
values read back plausibly, the CRC was verified frame-by-frame against captured telegrams, and
the hot-water program read back a real schedule. The emitted CSV passes `tsp compile`,
`tsp format --check`, and `ebusd --checkconfig` (0 errors). Writes (`50 23`), the raw memory map,
and the fault history are intentionally left out of this change.

### Notes

- Does not depend on any other pull request.
- One topic per commit.

<!-- No AI-tool attribution in this text (project rule). -->
