# Pull request text: room-unit-programs

Prepared on 2026-11-19, **not opened**. Branch `upstream/room-unit-programs` of the local clone of the fork (not
pushed), on `upstream/heat-demand-room-units` (`99c38aa`), head `adef8dd`; 4 files changed, 1425 insertions(+).
`scripts/check.sh` with `CFG_REPO` on the head: clean, seven steps, 529 messages in `ebusd --checkconfig`.

Commits:

- `adef8dd` kromschroeder: add the weekly programs of the room units, read side (fs1, fs2, fs3)

---

## Title

Add Kromschröder/Weishaupt weekly programs of the room units (read side) to src/wolf

## Body

Depends on the pull request of `heat-demand-room-units`: the diff of this branch includes their commits until they are merged.

Reads, stock ebusd. Builds on the circuit reads (and, in this chain, on the heat demand of the
room units).

The five weekly programs of each room unit (heating 1 to 3, hot water, circulation), one
message per switch-time slot (105 per unit), with the register scheme in the comments. All 315
slots were read on a live bus. Where a system manager prepares the hot water, the room units
only store their hot-water and circulation programs; the comments say so.

Checked with `tsp compile`, `tsp format --check` and `ebusd --checkconfig` (no error). One topic
per commit; the evidence for each definition (captures and their decoding) is kept with the
fork and available on request.
