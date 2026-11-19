# Pull request text: boiler-info-values

Prepared on 2026-11-19, **not opened**. Branch `upstream/boiler-info-values` of the local clone of the fork (not
pushed), on `upstream/boiler-fault-counters` (`2a4d265`), head `5b93079`; 3 files changed, 100 insertions(+).
`scripts/check.sh` with `CFG_REPO` on the head: clean, seven steps, 196 messages in `ebusd --checkconfig`.

Commits:

- `844fc4d` kromschroeder: add the boiler information values read with 50 22 (bc1, bc2)
- `5b93079` kromschroeder: add more boiler information values read with 50 22 (bc1, bc2)

---

## Title

Add Kromschröder/Weishaupt boiler information values (register reads) to src/wolf

## Body

Depends on the pull request of `boiler-fault-counters`: the diff of this branch includes their commits until they are merged.

Reads, stock ebusd.

The information values the WTC display shows as "i" codes, read with `PBSB 50 22` on both
boilers: flow, return, flue gas, outside and hot-water temperatures, the hydraulic-separator
temperature, and the two software versions (kept as the raw bytes the scan reports as SW).
Each was read on both boilers through ebusd and compared with the automat's own memory values
in the same minutes. Only the files of the boilers change; the pull request stacks on the other
boiler changes because they create those files. It adds the shared read `OutsideTemp` to
`wtc_inc`, which the circuit-reads pull request adds too: the one merged second drops its
copy.

Checked with `tsp compile`, `tsp format --check` and `ebusd --checkconfig` (no error). One topic
per commit; the evidence for each definition (captures and their decoding) is kept with the
fork and available on request.
