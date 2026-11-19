# Pull request text: boiler-faults

Prepared on 2026-11-19, **not opened**. Branch `upstream/boiler-faults` of the local clone of the fork (not
pushed), on `weishaupt-pr` (`4cd5a54`), head `9b29656`; 5 files changed, 206 insertions(+).
`scripts/check.sh` with `CFG_REPO` on the head: clean, seven steps, 160 messages in `ebusd --checkconfig`.

Commits:

- `bd9d0dd` kromschroeder: add fault log read registers (em1)
- `4828abe` kromschroeder: add boiler service-hours read (bc1)
- `91c0738` kromschroeder: add boiler fault history (bc1, bc2)
- `9b29656` kromschroeder: the service counter is info value i46, not i45 (bc1, bc2)

---

## Title

Add Kromschröder/Weishaupt boiler fault history, service hours and system fault log to src/wolf

## Body

Depends on #717 (merged first): the diff of this branch includes their commits until they are merged.

Reads, stock ebusd. Builds on the register reads of #717.

- **Fault history of the WTC boiler automats** (`08.w.bc1`, `18.w.bc2`, new files named with the
  identification the boilers answer, `W`): the six last faults, each an 8-byte slot of EEPROM
  (fault number with a warning bit, operating phase, load, boiler, flue gas and return
  temperatures, ionisation), and the pointer to the most recent slot. Read with the memory read
  `PBSB 50 00`, whose ID is a precomputed CRC-8 followed by items "code, address" (high nibble of
  the code = bytes minus one, low nibble = memory area); a shared base `memr` keeps the first
  answer byte as the field `FirstByte`, which reads 0 in a normal answer.
- **Hours since the last service** of both boilers (info value i46, a register read, factor 10).
- **Fault log of the system** (`50.w.em1`): the most recent entry of the system manager's log
  (code, type, device and time stamp).

Verified on a live bus with two WTC-GB boilers (automat software 11.04): the 48 values of the
six slots of the first boiler equal those the vendor service tool shows in its fault history;
the memory-read checksum recomputed offline matches every captured request.

Checked with `tsp compile`, `tsp format --check` and `ebusd --checkconfig` (no error). One topic
per commit; the evidence for each definition (captures and their decoding) is kept with the
fork and available on request.
