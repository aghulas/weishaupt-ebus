# Pull request text: heat-demand-boilers

Prepared on 2026-11-19, **not opened**. Branch `upstream/heat-demand-boilers` of the local clone of the fork (not
pushed), on `upstream/boiler-info-values` (`5b93079`), head `9e0f796`; 3 files changed, 66 insertions(+).
`scripts/check.sh` with `CFG_REPO` on the head: clean, seven steps, 198 messages in `ebusd --checkconfig`.

Commits:

- `9e0f796` kromschroeder: add the heat demand telegrams 05 07 to the boilers (bc1, bc2)

---

## Title

Add Kromschröder/Weishaupt heat demand telegrams (05 07) to the boilers to src/wolf

## Body

Depends on the pull request of `boiler-info-values`: the diff of this branch includes their commits until they are merged.

Passive telegrams, stock ebusd. Builds on the boiler files of the chain before it.

The cascade manager (master `0x10`) sends each boiler automat (master addresses `0x03`,
`0x13`) a heat demand about every 20 s, without an answer: request state, requested flow
temperature, modulation demand, hot-water setpoint. Defined passive in `08.w.bc1` and
`18.w.bc2` with a shared model `PowerDemand` in `wtc_inc`.

Verified on a live bus: the modulation demand and the hot-water setpoint equal what the
automat holds in RAM (read with `50 00` in the same minutes); over ten days of telegrams the
request state is `0x66` / `0xee` exactly while the modulation demand is above 0 and `0x55` /
`0x00` otherwise. Bytes without an independent figure stay unnamed (`ukn…`). The room units
send the same telegram; the pull request `heat-demand-room-units` adds them with its own copy
of the shared model, and the one merged second drops its copy.

Checked with `tsp compile`, `tsp format --check` and `ebusd --checkconfig` (no error). One topic
per commit; the evidence for each definition (captures and their decoding) is kept with the
fork and available on request.
