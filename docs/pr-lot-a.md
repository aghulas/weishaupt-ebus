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

---

## Comment prepared on 2026-11-18 — not posted

State: `weishaupt-A` and the local `weishaupt-pr` are at `4cd5a54`, two commits ahead of the
branch of the pull request on the fork (`66b775e`, 14 commits, no review). Nothing is pushed.
Pushing `weishaupt-pr` is a fast-forward (no force) and needs the owner's word (rule 8); the
comment below is to be posted after that push, from the owner's account.

The two changes are **two commits on top**, not amendments of the commits that own the code
(`0cc3902` for `HcMode`, `f1a1337` for the register reads): the branch moves by a
fast-forward, the fourteen commit ids already on the pull request stay valid, and each new
commit message says what was observed, which a fold into the original commits would bury.
It is also what was done for the three earlier corrections of this branch (`6583b61`,
`2ce6a8d`, `66b775e`). A reviewer who reads the whole diff sees the corrected state either
way. If the maintainer prefers a squashed history, the fold is one rebase away.

The description of #717 names neither `DHWOperationMode` nor the field concerned, so it
needs no change.

### Text of the comment

Two commits added on top; the earlier ones are unchanged.

**`HcMode` with a heating module that has no outside sensor** (`b2e2db7`). Two of the three
modules here have no outside sensor and send `00 9c` in the outside-temperature field of the
exchange: -100.0, the value these devices give for a sensor that is not fitted. The field was
`temp2`, whose range starts at -50, so ebusd refused the whole message for these two modules
(`ERR: argument value out of valid range`) while the third decoded. The field now uses a
`D2B` scalar in °C without a range, next to the `otemp10` the register reads already use for
the same reason. Checked by injecting the three captured exchanges into ebusd without a bus:

```
70 51 50 14 07 01 00 05 e6 17 08 ff / 09 00 00 00 19 00 9c 04 96 10   outsidetemp=-100.000
f0 52 50 14 07 03 00 1b b3 17 00 ff / 09 00 01 cd 19 00 9c 02 96 10   outsidetemp=-100.000
30 50 50 14 07 01 00 06 4d 17 08 ff / 09 00 00 00 80 00 0b 04 a4 10   outsidetemp=11.000
```

**`DHWOperationMode` renamed `DHWLoadingPriority`** (`4cd5a54`). The register is not an
operating mode. Its settings (priority, parallel, sliding) are those of the parameter the
vendor's manual calls "DHW operation", in the chapter on the priority of DHW loading: whether
a heating circuit is cut while the hot water is loaded. Name and comments follow the manual;
address, type and value list are unchanged. One caveat, also written as a comment in the
file: only the value 0 (`Priority`) has been read on a device. The manual lists the settings
as priority, parallel, sliding; the list has 1 = `Sliding`, 2 = `Parallel`, and no read
establishes either order. I left the values as they are rather than swap them without
evidence; the message is read only.

Both pass `tsp format --check`, `tsp compile` and `ebusd --checkconfig`.

