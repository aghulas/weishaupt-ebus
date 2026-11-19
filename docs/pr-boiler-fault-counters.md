# Pull request text: boiler-fault-counters

Prepared on 2026-11-19, **not opened**. Branch `upstream/boiler-fault-counters` of the local clone of the fork (not
pushed), on `upstream/boiler-live-values` (`e25a877`), head `2a4d265`; 3 files changed, 189 insertions(+).
`scripts/check.sh` with `CFG_REPO` on the head: clean, seven steps, 180 messages in `ebusd --checkconfig`.

Commits:

- `2a4d265` kromschroeder: add the fault counters of the boiler automat (bc1, bc2)

---

## Title

Add Kromschröder/Weishaupt boiler fault counters to src/wolf

## Body

Depends on the pull request of `boiler-live-values`: the diff of this branch includes their commits until they are merged.

Reads, stock ebusd. Builds on `memr`.

One counter per fault number (33 counters, faults 11 to 57) of each WTC boiler automat, seven
memory reads of at most 10 bytes of EEPROM per boiler. Address and fault number from the symbol
table of the automat firmware, meaning from the boiler manual. Verified on a live bus: the
vendor service tool reads the same seven blocks, and its bytes equal the values ebusd decodes
for 32 of the 33 counters of the first boiler (one differs in byte order in the tool's log).

Checked with `tsp compile`, `tsp format --check` and `ebusd --checkconfig` (no error). One topic
per commit; the evidence for each definition (captures and their decoding) is kept with the
fork and available on request.
