# Pull request text: programs-write

Prepared on 2026-11-19, **not opened**. Branch `upstream/programs-write` of the local clone of the fork (not
pushed), on `upstream/settings-write` (`1c12b5b`), head `bbad5a0`; 4 files changed, 526 insertions(+), 300 deletions(-).
`scripts/check.sh` with `CFG_REPO` on the head: clean, seven steps, 864 messages in `ebusd --checkconfig`.

Commits:

- `bbad5a0` kromschroeder: write the weekly programs of room units 1 and 3 and of the direct circuit

---

## Title

Add Kromschröder/Weishaupt weekly-program writes to src/wolf

## Body

Depends on john30/ebusd#1825, john30/ebus-typespec#8 and the pull request of `settings-write`: the diff of this branch includes their commits until they are merged.

Writes, same requirements as the setting writes.

The slots of the five programs of two room units and the two programs of the system manager's
own circuit are written one slot per telegram, read ids unchanged. In each program one slot
was changed on a live bus, read back and restored; the other slots share its codec and
register scheme. One room unit of the test installation acknowledged every slot write and kept
none; its programs stay read only.

Checked with `tsp compile`, `tsp format --check` and `ebusd --checkconfig` (no error). One topic
per commit; the evidence for each definition (captures and their decoding) is kept with the
fork and available on request.
