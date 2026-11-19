# Pull request text: heat-demand-room-units

Prepared on 2026-11-19, **not opened**. Branch `upstream/heat-demand-room-units` of the local clone of the fork (not
pushed), on `upstream/circuit-reads` (`bb098af`), head `99c38aa`; 4 files changed, 73 insertions(+).
`scripts/check.sh` with `CFG_REPO` on the head: clean, seven steps, 214 messages in `ebusd --checkconfig`.

Commits:

- `99c38aa` kromschroeder: add the heat demand telegrams 05 07 of the room units (fs1, fs2, fs3)

---

## Title

Add Kromschröder/Weishaupt heat demand telegrams (05 07) of the room units to src/wolf

## Body

Depends on the pull request of `circuit-reads`: the diff of this branch includes their commits until they are merged.

Passive telegrams, stock ebusd. Builds on the circuit reads (files of the room units).

Each WCM-FS room unit (masters `0x30`, `0x70`, `0xf0`) sends the cascade manager (`0xf1`) a
heat demand about every 20 s, without an answer. Defined passive in `35.w.fs1`, `75.w.fs2`,
`f5.w.fs3` with the shared model `PowerDemand` in `wtc_inc`.

Verified on a live bus: the requested flow temperature equals the room unit's register
`b8 02` read in the same minutes; over ten days the request state is `0xbb`, or `0x55` mostly
at night with a low requested temperature; the modulation and hot-water bytes are the
replacement value. The boiler side is the pull request `heat-demand-boilers`, with its own copy
of the shared model: the one merged second drops its copy.

Checked with `tsp compile`, `tsp format --check` and `ebusd --checkconfig` (no error). One topic
per commit; the evidence for each definition (captures and their decoding) is kept with the
fork and available on request.
