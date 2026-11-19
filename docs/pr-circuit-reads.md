# Pull request text: circuit-reads

Prepared on 2026-11-19, **not opened**. Branch `upstream/circuit-reads` of the local clone of the fork (not
pushed), on `weishaupt-pr` (`4cd5a54`), head `bb098af`; 8 files changed, 729 insertions(+).
`scripts/check.sh` with `CFG_REPO` on the head: clean, seven steps, 211 messages in `ebusd --checkconfig`.

Commits:

- `52a3e1d` kromschroeder: add heating-circuit reads of the room units (fs1, fs2, fs3)
- `bb098af` kromschroeder: add heating-circuit reads of the heating modules (em1, em2, em3)

---

## Title

Add Kromschröder/Weishaupt heating-circuit reads of room units and heating modules to src/wolf

## Body

Depends on #717 (merged first): the diff of this branch includes their commits until they are merged.

Reads, stock ebusd. Builds on the register reads of #717.

- New files `75.w.fs2` and `f5.w.fs3`, and reads in `35.w.fs1`: the values and settings of the
  heating circuit of each WCM-FS room unit (heat demand, flow setpoint, outside and room
  temperature; room setpoints, curve, summer / winter changeover, flow limits, hot-water
  setpoint, boost offset, switch-on lead time, frost-protection limit).
- The same circuit reads on the two WCM-EM heating modules (`51.w.em2`, `52.w.em3`) and on the
  system manager's own circuit (`50.w.em1`).

Every register was read on a live bus through ebusd. A room unit and its heating module
answer the same setting registers with different values; which copy the regulation uses is
not established, and the comments say so.

Checked with `tsp compile`, `tsp format --check` and `ebusd --checkconfig` (no error). One topic
per commit; the evidence for each definition (captures and their decoding) is kept with the
fork and available on request.
