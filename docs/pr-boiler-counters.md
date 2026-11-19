# Pull request text: boiler-counters

Prepared on 2026-11-19, **not opened**. Branch `upstream/boiler-counters` of the local clone of the fork (not
pushed), on `upstream/boiler-faults` (`9b29656`), head `ede1f45`; 3 files changed, 23 insertions(+).
`scripts/check.sh` with `CFG_REPO` on the head: clean, seven steps, 162 messages in `ebusd --checkconfig`.

Commits:

- `ede1f45` kromschroeder: add boiler counters (bc1, bc2)

---

## Title

Add Kromschröder/Weishaupt boiler operating counters to src/wolf

## Body

Depends on the pull request of `boiler-faults`: the diff of this branch includes their commits until they are merged.

Reads, stock ebusd. Builds on `memr` (fault history pull request).

Operating hours, burner hours and burner starts of both WTC boiler automats, one memory read
(`PBSB 50 00`) of their EEPROM counters each. Verified on a live bus: read on both boilers over
hours, operating hours step by one per hour of wall-clock time and the burner counters step as
the burners run (low byte first).

Checked with `tsp compile`, `tsp format --check` and `ebusd --checkconfig` (no error). One topic
per commit; the evidence for each definition (captures and their decoding) is kept with the
fork and available on request.
