# Pull request text: boiler-live-values

Prepared on 2026-11-19, **not opened**. Branch `upstream/boiler-live-values` of the local clone of the fork (not
pushed), on `upstream/boiler-counters` (`ede1f45`), head `e25a877`; 3 files changed, 56 insertions(+), 3 deletions(-).
`scripts/check.sh` with `CFG_REPO` on the head: clean, seven steps, 166 messages in `ebusd --checkconfig`.

Commits:

- `0ea870b` kromschroeder: add boiler temperatures read from memory (bc1, bc2)
- `e25a877` kromschroeder: add boiler load, ionisation and pump speed read from memory (bc1, bc2)

---

## Title

Add Kromschröder/Weishaupt boiler live values read from memory to src/wolf

## Body

Depends on the pull request of `boiler-counters`: the diff of this branch includes their commits until they are merged.

Reads, stock ebusd. Builds on `memr`.

Two memory reads per boiler automat: `Temperatures` (return, flue gas, flow, outside) and
`Operation` (load, ionisation, pump speed), from RAM / XRAM. Verified on a live bus against the
status telegram each boiler sent in the same minute, one boiler firing, the other idle.

Checked with `tsp compile`, `tsp format --check` and `ebusd --checkconfig` (no error). One topic
per commit; the evidence for each definition (captures and their decoding) is kept with the
fork and available on request.
