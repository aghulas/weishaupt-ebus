# Plan

Last updated: 2026-11-17.

## State of upstream

- `john30/ebusd`: last commit on `master` 2026-03-29. Several pull requests open since October 2026
  without review.
- `john30/ebusd-configuration`: last commit on `master` 2026-06-09.
- No review or comment by the maintainer on #1825 and #717 (checked again on 2026-11-17, 15:00).

Plan accordingly: nothing here depends on an answer from upstream (see "Direction").

## Direction (decided on 2026-11-17)

The lots were stacked behind two pull requests without review, and the last outside pull
requests merged upstream waited from three weeks to five months. The project therefore runs on
two tracks (`AGENTS.md`, "Goal"):

1. **Fork first.** One integration branch in `aghulas/ebusd-configuration` carries every lot
   that has its evidence; compiled CSV are published from it as releases, next to the released
   ebusd build with the run-time checksum (`aghulas/ebusd`, `v26.1-weishaupt.1`). Reads work
   with a stock ebusd; writes (lot C) need that build until john30/ebusd#1825 is merged.
2. **Upstream in parallel.** The lot branches stay rebased and ready. #717 and #1825 stay
   open; further pull requests are opened lot by lot when the maintainer responds, with the
   owner's word (rule 8).

Next items, fork track, in order:

| # | Item | State |
|---|---|---|
| 1 | Integration branch `weishaupt` in the configuration fork: the top of the stack of lots A, E, D, F, C, plus one commit that pins the library package of the fork. | **done** on 2026-11-17: `6af8f6e` (25 commits on upstream `master`), pushed. It installs with a plain `npm install` and passes `scripts/check.sh`, 198 messages. Current lot heads: A `041005d`, E `aced43d`, D `969986c`, F `bd83f61`, C `a9d2c37`. Since the same day lot G (`weishaupt-G`, head `a870515`, pushed to the fork, no pull request) sits on top of C, and lot H (`weishaupt-H`, head `1a9f922`, local only) on top of G; both are in the default `STACK` of `scripts/integrate.sh`. The integration branch has not been rebuilt with them; that and the push of lot H wait for the owner's word. |
| 2 | A script that rebuilds the integration branch from the lot branches, so that it is never edited by hand. | **done**: `scripts/integrate.sh` checks that the stack is linear, sets `weishaupt` to its top in a separate worktree (`out/integration`), adds the pin commit with fixed dates (same stack, same commit id) and runs `scripts/check.sh` there. |
| 3 | CSV releases of the fork. | **published** on 2026-11-17 as pre-releases: library package `v0.31.0-weishaupt.1` in `aghulas/ebus-typespec` (branch `weishaupt`, `135a949`); `weishaupt-0.1.0` (tag on `5bacbb7`) and, after the correction of item 6, `weishaupt-0.1.1` (tag on `720b33c`) in `aghulas/ebusd-configuration`, archives made by `scripts/release.sh <version>`, notice from `docs/release-readme.md`. 0.1.1 downloaded again after publication: checksum right, 197 messages in the official ebusd 26.1. `weishaupt-0.1.2` (tag on `6af8f6e`, with `SystemHour`, 198 messages) published the same day and checked the same way. The releases 0.1.0 and 0.1.1 and their tags were deleted from the fork the same day on the owner's request (superseded; the tags remain in the local clone). Next release: after a change of a lot, `scripts/release.sh <version>`, then tag and release on the owner's word. |
| 4 | Tests on the installation. Done on 2026-11-17: by reads (`hex` command of ebusd, `50 22` and `50 00` only), `SystemHour` (`02 0f 00` at 15 h), the two multi-item requests of lot F answered by both boilers, second boiler captured while firing; and, on the operator's decision, the write test of `BlockingTime` (1 → 2 → 1 from source `ff`, telegrams `cc 25 00 02 00` and `28 25 00 01 00` acknowledged and read back, `evidence/register-write-crc.md` section 6). | done |
| 6 | File names of the lots and the scan. ebusd loads one file per scanned **slave** address, the best match on `ZZ.ident`; with equal matches the longer name wins (`ScanHelper::loadScanConfigFile`). Two defects followed: `10..bc1` / `10..bc2` were never loaded (`10` is a master address), and `50..em1` / `08..bc1` took the place of upstream's `50..mc` / `08..hc` for every Kromschroeder device at those addresses, Wolf included. | **corrected** on 2026-11-17. Lot A, two commits on top (`77e25c8`, `ad46e81`, pushed to the branch of #717): the four status messages are in the file of the system manager as `Boiler1Status`, `Boiler1Power`, `Boiler2Status`, `Boiler2Power` with explicit `@qq` / `@zz(0x10)`; the files carry the identification the devices answer, `15.w.ka`, `50.w.em1`, `51.w.em2`, `52.w.em3`. Lots E, D, F, C replayed on it with `08.w.bc1`, `18.w.bc2`, `35.w.fs1` named so from the commit that adds them (pushed; the heads before the renaming, `2bc03e4`, `1b33e77`, `d91dfff`, `f55ad5c`, are kept locally as `backup/pre-rename-*` and under the tag `weishaupt-0.1.0`). `scripts/check.sh` clean on each lot (134, 158, 160, 164 messages) and on the integration branch (197). In the ebusd of the check without a bus: a device answering `W` gets the `.w.` file at 08, 15, 18, 35, 50, 51, 52, another identification gets `08..hc` / `50..mc`, and the status telegrams of both boilers decode from `15.w.ka` alone. Not known: what Wolf devices answer as identification; if it were `W` as well, the names would not tell them apart. The description of #717 was updated the same day (messages renamed, a section on the file names). |
| 5 | New findings (`docs/discoveries.md`) enter as lots on the integration branch as soon as they have their evidence, without waiting for the previous lot upstream. | ongoing |

What this costs: the fork becomes a distribution to maintain (releases, following upstream
version bumps). What it does not change: rules 1 to 4 and 7 to 9.

## Open pull requests

| PR | Branch | Head | State |
|---|---|---|---|
| john30/ebusd#1825 | `aghulas:crc` | `492867d9` (`02f6de0f` before the identity rewrite) | open, no review. 1 commit, 4 files. |
| john30/ebus-typespec#8 | `aghulas:wcrc-decorator` | `75c7d58` | **opened on 2026-11-17** (lot B): `@crc` and `@wcrc`, with `docs.md` regenerated and the README overview extended. 1 commit, 7 files, 91 tests pass. No review yet. |
| john30/ebusd-configuration#717 | `aghulas:weishaupt-pr` | `041005d` (13 commits, 7 files; `SystemHour` back, and the correction of 2026-11-17, see "Direction", item 6; `a212e73` before) | **retargeted to Lot A on 2026-11-16**: 10 commits, 9 files, 638 lines, `.tsp` only, read-only, stock ebusd. Old 11 300-line version saved on local branch `backup/weishaupt-pr-717-big`. |

## Gaps of the former #717 (11 300-line version)

The version of #717 that these gaps describe was replaced on 2026-11-16 by Lot A. It survives
only on the local branch `backup/weishaupt-pr-717-big`. What became of each gap:

1. Decorator `.js` / `.ts` files under `src/`: gone, Lot A is `.tsp` only. The decorators are
   Lot B, in the `ebus-typespec` fork.
2. Format: fixed, `tsp format --check` is clean on `src/wolf`.
3. Lint: run on 2026-11-17 (`npm run lint`, branch `weishaupt-D`). 7 warnings, all
   `missing-namespace` on enums of upstream's `src/_templates.tsp`, none in the files of the lots.
4. Size: fixed, 641 lines in Lot A. The raw memory map is left out.
5. Dependency on #1825: gone for Lots A, D and E (reads only). Still true for Lot C.
6. German i18n: no longer a new manufacturer. Still unknown whether new messages in `src/wolf`
   need `de.yaml` entries.
7. `ChangeOverTime`, `FloorDryingTemp`, `RoomThermostatTemp` typed `temp1` on 16-bit registers:
   closed for `ChangeOverTime` (hours with factor 1, in Lot C); the other two are in no lot.
8. Fault history, counters, service hours: done in Lots E and D. Per-code fault counters are
   still missing.

## Open items on the lots (audit of 2026-11-17)

- Lot A, in #717: `SupplyWTCTemp` is the de-couple sensor B22, not the boiler flow. Renamed to
  `DeCoupleTemp` on 2026-11-17 (commit `83241cc`, pushed to `weishaupt-pr`); `weishaupt-E` and
  `weishaupt-D` rebased and pushed again after each change, `scripts/check.sh` clean (160
  messages).
- Lot A, in #717: `SystemHour` had no bus read and was removed on 2026-11-17 (commit `19dc47c`,
  rule 3). Read on the bus the same day (see below) and added again (`041005d`).
- Lot A, evidence pass of 2026-11-17 (read-only, nothing changed in the fork):
  - Program slots: all 42 read and recorded (`evidence/em1-clock-program.md`). The request
    payloads seen on the bus equal the `@ext` triples of `50..em1.tsp`, 42 of 42; the CRC byte
    of all 57 triples of the file was recomputed, no mismatch. Hot water is enabled on four
    non-contiguous weekdays, which confirms the weekday nibble. **Closed.**
  - Second boiler: still seen with the burner off only (`WTCStatus` phase `00`, load 0 %,
    `WTCPower` unchanged at `21 17 64`). **Closed** later the same day: captured while firing
    (`01 06 7f 62 19 78 …`, `WTCPower` `19 17 64`), see `evidence/bc1-boiler-status.md`.
  - Sign of KA registers 3, 13, 14: signed, by the "no sensor" answers of the same registers
    on the other devices (`18 fc` = -100.0, `00 80`) and by the vendor register list
    (`evidence/ka-reads.md`). **Closed**: `DHWSetValue`, `DeCoupleTemp` and `DHWTemp`
    changed from `temp10` to `otemp10` (commit `a212e73`, pushed to `weishaupt-pr`); lots E and
    D rebased on it and pushed again, `scripts/check.sh` clean (160 messages).
  - `SystemHour`: no read-only path. The running configuration has the hour at `25 01` for
    writing only, no cached value, and no telegram with that register in the capture.
    **Closed** later the same day: read with the `hex` command of ebusd, answer `02 0f 00` at
    15 h (`evidence/em1-clock-program.md`). `SystemHour` is back in lot A since the same day
    (commit `041005d`, pushed to the branch of #717; lots E, D, F, C replayed on it).
- The comment of 2026-11-16 on #717 describes the former version; a follow-up comment was
  posted on 2026-11-17 (reshape, rename, the two questions still open).
- `weishaupt-E` and `weishaupt-D` were pushed to the ebusd-configuration fork on 2026-11-17 (no
  pull request). `wcrc-decorator` was pushed to the ebus-typespec fork the same day (no pull request).
- A comment on john30/ebusd-configuration#616 (2026-11-17) points another contributor working on
  Weishaupt files to #717, to avoid duplicate work. No answer yet.
- A comment on john30/ebusd#1814 (2026-11-17, arbitration lost on a WCM-FS installation) gives
  this installation as a data point: 30 forced reads in a row from master `31` to the room
  units `35` and `75` answered, max arbitration time 23 micros. No answer yet.

## Upstream track — question to the maintainer

Before reshaping the pull request, ask on #717 (or issue john30/ebusd#167):
is a new manufacturer welcome, are smaller lots preferred, where should the CRC decorator live.
Status: asked on #717 on 2026-11-16. Rather than wait, #717 was **retargeted** the same day to
Lot A, which answers most of it in code: it extends `src/wolf` (no new manufacturer), is a small
read-only `.tsp`-only change (no `.js`), and needs no CRC decorator (CRC precomputed in the ID).
The `0x00` finding note (`docs/maintainer-note-crc.md`) was drafted and is superseded: the
description of #717 states the finding (section "Register reads carry a precomputed CRC") and
Lot A already ships the reads the note proposed. It is not to be posted.

## Lots

| Lot | Content | Depends on | Status |
|---|---|---|---|
| A | Read-only definitions: `5022` register reads with the CRC precomputed in the ID, passive status messages, time programs as read. No custom decorator needed at runtime, works with stock ebusd. | nothing | in progress — branch `weishaupt-A`, `src/wolf/15..ka.tsp` (18 evidenced reads) |
| B | CRC decorator in `ebus-typespec`. | maintainer's answer | **done + proven end-to-end** — fork `aghulas/ebus-typespec`, branch `wcrc-decorator`: `@crc(poly, ...)` (compile-time) and `@wcrc(...)` (`[WCRC]` marker; the byte emitted is the checksum of the address, so a read stays valid without the run-time checksum, see `evidence/register-write-crc.md` section 5), 91 tests pass, build clean. Commit `7e85886` since 2026-11-17 (amended, one commit, replaces `5490298`), pushed to the fork, no pull request. Demo: installed the fork into the config and rewrote 3 ka reads as `@crc(0x5c, ...)` — the emitted `ka.csv` was **byte-identical** to the literal version and passed `ebusd --checkconfig`, so `@crc` reproduces the hand-computed CRCs end-to-end. Demo reverted (no change to `weishaupt-A`); the config's 0.26 toolchain restored. Still exploratory: `@wcrc` feeds Lot C writes (untestable on hardware, rule 7) and ebusd #1825; a permanent wiring needs the decorator released and the config's toolchain bumped (both the maintainer's call). |
| C | Writes (`5023`) with runtime CRC and setpoint ranges. | #1825, lot B (both unmerged, no review) | **prepared, pushed to the fork, no pull request** — branch `weishaupt-C` (from `weishaupt-A`, 5 commits, head `e9b176b`): 17 settings read and written, ka (8), em2 (7), fs1 (2). Evidence in `evidence/register-write-crc.md` and `evidence/settings-writes.md`. `scripts/check.sh` clean (167 messages) with the local build of `wcrc-decorator`. Cannot be proposed before #1825 is merged and `@wcrc` is released. See "Lot C" below. |
| D | Raw memory map (`WH11928`). Separate pull request, or left out. | maintainer's answer | **blocked on evidence** — the `50 00` memory-read format is uncertain. The deployed config reads `EEA_H_PON`=90, `EEA_H_BON`=216 as 1-byte UCH, but #717 models them as 3-byte U3N and uses a different address byte (`22` vs the deployed `02`); the values are also physically impossible (90 h run < 216 h burner < 430 h since service). So the 1-byte reads are truncated/misaligned and cannot be shipped to the evidence bar (rule 3). Establishing the real format needs deeper reverse-engineering and the vendor service tool to cross-check. Left out until then. |
| E | WTC fault log, service hours. | lot A | **fault log done** on branch `weishaupt-E` (from `weishaupt-A`): 9 read registers `src/wolf/50..em1.tsp` (ErrorId selector + code/type/device/date/time), evidenced on the live boiler (`evidence/em1-fault-log.md`), checkconfig clean. A future PR, to open after #717 merges (depends on its templates). Boiler service hours added too: `BurnerServiceHours` (i45, `50 22` on `bc1` ZZ 08, `src/wolf/08..bc1.tsp`, read live 430 h). Boiler operating hours (`50 00` EEPROM) still belong to the raw memory-map lot. |

| F | Live values of the WTC automat read from memory (`50 00`, RAM and XRAM). | lot D (`memr` template) | **done** on branch `weishaupt-F` (from `weishaupt-D`, commits `ab5d76c` and `d91dfff`, pushed to the fork, no pull request): `Temperatures` (return, flue gas, flow, outside) and `Operation` (load, ionisation, pump speed), one memory read each, for both boilers. Evidence in `evidence/bc-live-values.md`, `scripts/check.sh` clean (164 messages). The two multi-item requests were sent on 2026-11-17 (`hex` command of ebusd) and answered by both boilers, the second one through a burner start. |
| G | Read coverage of the room units and heating modules: the heating-circuit values and settings, `50 22` reads only. | lot C (stack order; `fs1` and `em2` files, `wtc_inc.tsp`) | **done, pushed to the fork, no pull request** on branch `weishaupt-G` (2026-11-17, from `weishaupt-C`, head `a870515` since the identity rewrite, commits `1d890d3` and `624edb5` before): 14 reads on each room unit, new files `75.w.fs2.tsp` and `f5.w.fs3.tsp`, 12 added to `35.w.fs1.tsp`; 8 reads added to `em1`, 3 to `em2`, 10 to `em3`; shared models in `wtc_inc.tsp`. Every register read on every device the same day, request and answer bytes from the capture, CRC recomputed, values cross-checked with the `05 07`, `50 14` and `09 03` telegrams of the devices. Evidence in `evidence/room-units-reads.md` and `evidence/heating-modules-reads.md`, `scripts/check.sh` clean (259 messages) in a worktree with the library package of the fork. No write for the new devices. Left out with the reason in both records: heat demand and room setpoint of the modules, boost offset of the room units, choices with value lists, weekly programs of the room units. Open: the room unit and its module hold different values in the same setting registers; `50` answers like `15`. For a pull request upstream the reads can be cut on lot A, except the two `fs1` settings and the `em2` settings of lot C. Checked again in the stack on 2026-11-17 on a trial integration branch (`weishaupt-next`, local): `scripts/check.sh` clean, 259 messages, and with `--scanconfig` and injected identifications ebusd picks `75.w.fs2` and `f5.w.fs3`. Not released. |
| H | Weekly programs of the room units, read side: three heating programs, hot water, circulation (`50 22`, sub-bytes `14`, `15`, `16`, `17`, `1a`), three switch-time slots per weekday. | lot G (`fs` files, `wtc_inc.tsp`); codec `SwitchTimes` of lot A | **done, local only** on branch `weishaupt-H` (2026-11-17, from `weishaupt-G`, not pushed, no pull request), two commits: `c4521ef` heating programs 1 to 3 (63 reads per unit), `1a9f922` hot-water and circulation programs (42 per unit); 105 models shared in `wtc_inc.tsp`, 315 messages on `fs1`, `fs2`, `fs3`. Every slot read once on every unit the same day, request and answer bytes from the capture, CRC recomputed for the 315 telegrams, compiled IDs equal to the request bytes; non-contiguous weekdays in program 1, slots 2 and 3 used by the circulation program, values that differ between the units. Evidence in `evidence/room-units-programs.md`, `scripts/check.sh` clean (448 messages after the first commit, 574 after the second) in a worktree with the library package of the fork. Not verified, see the record: which program a unit runs (`12 01` reads 11 on the three, value list from the running configuration only, register left out), the numbering of the heating programs, whether a room unit applies its hot-water and circulation programs (identical on the three units, the system manager prepares the hot water; the second commit can be dropped alone). No write. Open: the heating modules, the system manager and `f6` answer the same sub-bytes, heating programs included, against the note of lot A that the bus has no heating program; not examined. |

Lot A is the priority: it is the only one that can be merged without any other change upstream.

### Lot A — findings and direction (2026-11-16)

- **Manufacturer 0x50 is already upstream.** `src/kromschroeder/` is a symlink to `src/wolf/`
  (namespace `Wolf`, `MF = 0x50` Kromschröder) with register reads on the same `50 22` base.
  The WCM/WTC devices scan as `MF=Kromschröder`, so Lot A **extends `src/wolf/`** rather than
  adding a new `Weishaupt` manufacturer. Weishaupt's own id `0xc5` is the brand, not the bus id.
- **Upstream's read CRC is wrong.** `src/wolf/_templates.tsp` `regr` hardcodes `@base(MF,0x22,0x00)`;
  the live bus shows the first ID byte is a CRC-8 (poly 0x5C) over the address, not `0x00`
  (e.g. `0c 00 → 74`, `0e 00 → cc`). See `evidence/register-crc.md`. Lot A emits the real,
  precomputed CRC via a corrected template (`crcr` / `CrcRead<T>`, base `@base(MF,0x22)`),
  so stock ebusd addresses the register with no runtime CRC and no `.js`.
- **Shipped so far:** `src/wolf/15..ka.tsp`, 18 read registers evidenced against the live boiler
  (`evidence/ka-reads.md`): KA sensors/status plus the read side of heating/hot-water settings.
  Emitted CSV passes `tsp compile`, `tsp format --check`, and `ebusd --checkconfig` (0 errors).
- **Passive status, first message shipped:** `KaStatus` (boiler status broadcast, PBSB `50 0A`,
  `src/wolf/wtc_inc.tsp` + `broadcast.tsp`), layout decoded against a live broadcast frame
  (`evidence/broadcast-kastatus.md`). The passive models could not go in the shared root
  `src/opdata_inc.tsp` (imported by tem/ochsner/encon too), so they live in a wolf-local include.
- **Passive status shipped:** `KaStatus` broadcast (`evidence/broadcast-kastatus.md`), and the
  first boiler's directed `WTCStatus` + `WTCPower` (`QQ 03 → ZZ 10`, `src/wolf/10..bc1.tsp`,
  `evidence/bc1-boiler-status.md`). `ZZ` taken from observed frames, not #717's `@zz`.
- **Passive status, both boilers + heating modules shipped:** `WTCStatus`/`WTCPower` for bc1
  (`QQ 03`) and bc2 (`QQ 13`); `HcMode` room-controller/module exchange for em1/em2/em3
  (`src/wolf/5x..emN.tsp`, `evidence/em-hcmode.md`).
- **`FsStatus` (PBSB 50 10) not shippable here:** it does not appear on this installation
  (no frame, no cached value; the PBSBs actually seen are 0504/0507/0700/0704/07ff/0902/0903/
  5000/5009/500a/5014/5022/fe01). The heating circuits use `HcMode` (50 14) instead, which is
  already shipped. Left out for lack of evidence (rule 3).
- **Time programs shipped (read side):** em1 system clock (weekday/date/time), weekly
  circulation program (`sub 1a`) and weekly hot-water program (`sub 17`), 3 slots × 7 days each,
  `src/wolf/50..em1.tsp`, evidenced against live reads (`evidence/em1-clock-program.md`; the
  hot-water program showed a real schedule, Mon 09:00→16:00). Shared register-read template
  moved to `src/wolf/wtc_inc.tsp` (KA reads unchanged). The deployed ebusd config differs from
  weishaupt-pr (programs under `em1`, dotted names); addresses taken from the running config.
  No separate heating program exists on this bus (only circulation + hot water).
- **Expansion ceiling reached.** The EM "sensor" messages are not a distinct passive set —
  they are active `50 22` reads of the same registers already shipped (e.g. DHWTemp, OutsideTemp),
  just on another circuit. The running config exposes 227+ messages on em1 alone. Going further
  means either duplicating the clock/programs onto em2/em3 (ZZ 51/52) or adding hundreds more
  register reads — both work against rule 5 (small, reviewable PRs) and recreate the #717
  problem. **Recommendation: treat Lot A as complete and scope the PR.** Any mass register
  coverage should be its own later lot, not bundled here.
- **To raise with the maintainer (needs approval, upstream-visible):** the existing `src/wolf`
  reads send `0x00` where the device expects a computed CRC — a latent bug, with bus evidence.
- `scripts/check.sh` targets `src/wolf` (set `LOT_DIR` for another folder). After the commit
  hygiene step (see Conventions) it compiles
  `src/main.tsp` and runs `ebusd --checkconfig` on the emitted root CSV files plus `wolf/`. The
  last step runs in Docker when available, otherwise in GitHub Actions (workflow
  `.github/workflows/checkconfig.yml` of this repository): the compiled CSV are sent as a
  workflow input, so nothing is pushed to the fork.

## Lot C — writes (prepared on 2026-11-17, local only)

- **Branch**: `weishaupt-C`. Restacked on 2026-11-17 on `weishaupt-F` (head `0af74ee` after the renaming of the files the same day, `f55ad5c` before; the commit ids below are those before the renaming), so
  that the lots form one linear stack and the integration branch is its top; the files of the
  lot are unchanged, the two shared files (`wtc_inc.tsp`, `main.tsp`) keep the additions of
  both sides. Pushed to the fork the same day (forced, no pull request on it); the former branch on lot A
  (`e9b176b`) is kept locally as `backup/weishaupt-C-on-A`.
  For a pull request upstream the lot is cut again on lot A. It was first based on lot A because it uses its templates and turns its `BlockingTime` read into a read /
  write setting; it touches none of the files of lots E, D and F except `wtc_inc.tsp` (two
  additions, expect a trivial rebase). Commits:
  - `9b94a86` (was `7b6dda5`) write template `crcw` / `CrcSetting` with `@wcrc`, `BlockingTime` (ka)
  - `8bf852c` (was `2453311`) `ChangeOverTime`, `DeCoupleMinTemp`, `CalorifierSwitchDiff` (ka)
  - `44bd3cd` (was `0e2b75b`) `DHWSwitchDiff`, `DHWLoadTime`, `LegionellaSetpoint`, `LegionellaCirculationTime` (ka)
  - `b6afe27` (was `eb13044`) seven heating-circuit settings (em2)
  - `f55ad5c` (was `e9b176b`) `SwitchOnRuntime`, `FrostProtectionLimitTemp` (fs1, new file `35..fs1.tsp`)
- **Evidence** (rule 3): for each of the 17 registers, a `50 23` telegram captured passively,
  its checksum recomputed offline, the acknowledgement, a captured read of the same register
  with the same value, and the captured telegram decoded by the lot in the ebusd of the check.
  The change of value itself rests on the operator's write tests of 2026-11-15, by their
  notes. Nothing was written to the installation for this lot (rule 7).
- **Toolchain**: the lot compiles only with `@wcrc`. Checked in a separate worktree of the fork
  clone with the local build of `repos/ebus-typespec` (`wcrc-decorator`, 0.31.0, compiler
  1.17.0) installed with `npm install --no-save`; nothing of that is committed. Checked again
  the same day with the corrected `@wcrc` (`7e85886`), lot C unchanged: clean, 167 messages. The clone
  itself was left on `weishaupt-F` with its 0.26 toolchain. To check the branch again: a
  worktree of `weishaupt-C`, the same install, then `CFG_REPO=<worktree> scripts/check.sh`.
- **Blocks the pull request**, in this order:
  1. john30/ebusd#1825 merged and in a released ebusd (run-time checksum, marker `[WCRC]`).
  2. `@crc` / `@wcrc` proposed to john30/ebus-typespec (lot B, no pull request yet), merged
     and released; then the version pin of ebusd-configuration raised to that release.
  3. #717 (lot A) merged, since lot C sits on it.
  4. The operator's test of the definitions through ebusd (four steps in
     `evidence/register-write-crc.md`).
- **Decided on 2026-11-17**:
  - Source address: the definitions set no `@qq`. Most settings are taken from `ff` only, the
    address of the vendor service tool; ebusd must not take it by default, so the comment
    `write -s ff` stays and the caller chooses.
  - `35..fs1.tsp` stays in the lot (two registers, each with its captured write); it is the
    last commit and can still be dropped alone if the maintainer prefers.
- **Open questions**, for the owner before proposing:
  - Ranges come from the operator's table, which cites the vendor manuals; pages not compared
    for this lot.
  - `maintsp` (`npm run maintsp`) rewrites unrelated lines of `src/main.tsp` on this base; the
    import of `35..fs1.tsp` was added by hand.
- **Left out, with what is missing**: table "Left out" of `evidence/settings-writes.md` (the
  four lot A settings of the system manager without a captured write, `DHWOperationMode`,
  `DHWExceeded`, `ModulationStatus`, de-couple maximum, regulator P / I, legionella day and
  circulation, boiler sequence, two room-unit settings, holiday level, program slots).

## Service tool comparison (2026-11-16)

- Protocol written: `docs/service-tool-protocol.md` (two seats, read-only rules, log format).
- Bus side ready: ebusd grabs all telegrams; a baseline snapshot was taken. The tool (`ff`) and
  ebusd (`31`) do not share an address. Setting writes also use source `ff`: none may be sent
  while the tool is connected.
- **Phase 1 done** (installation folder, no bus), recorded in `evidence/service-tool-log.md`:
  - The `*.SYC` files are firmware symbol tables (name + address, five lists, no size or codec).
    The fork's 36 memory maps were generated from them; names and addresses agree.
  - Lot D: on `WH11928`, `EEA_H_PON` is at most 3 bytes and `EEA_H_BON` at most 2 bytes (address
    gaps, same spacing in the other firmware families). The deployed 1-byte reads are therefore
    truncated. Still missing: the `50 00` request bytes sent by the tool (phase 2).
  - `DL.Ini` lists `50 22` register numbers with type and factor. 7 lot A definitions agree
    with it. Open for phase 2: sign of registers 3, 13 and 14, and register 13 labelled "B22"
    (hydraulic separator / plate exchanger secondary), not boiler flow.
  - `Cxe.Ini` confirms the tool sends as `0xff`.
- **Phase 2 done** on 2026-11-16 (one session, five screens), recorded in the same log:
  - Lot D: the `50 00` request grammar is established from the tool's own telegrams (list of
    `<code> <address>` items: high nibble = length - 1, low nibble = area, `06` = address high
    byte). The tool reads the counters as 8 bytes at `0x01e6` (3 + 2 + 3). `EEA_H_PON` seen to
    step 87 132 -> 87 133 h, low byte first. The tool does not display the counters on firmware
    11.0e, so burner hours (20 186 h) and starts (187 226) still lack an independent figure.
    **Lot D is no longer blocked on the format**; it needs that one cross-check, then a scoped
    lot (counters only, not the whole memory map).
  - Lot E: automat fault history decoded, 6 records of 8 bytes at `0x0202`, 48 of 48 values
    matched to the screen. Ready to be written as definitions with an evidence record.
  - Lot A: register 13 is the de-couple sensor B22, not the boiler flow; `SupplyWTCTemp` to be
    renamed (touches the branch behind #717: ask first). Sign of registers 3, 13, 14 still open.
- **Lot E, automat fault history: done** on branch `weishaupt-E` (commit `2bc03e4`, pushed to
  the fork on 2026-11-17): `FaultHistoryPointer` and `FaultHistorySlot1..6` for both boilers
  (`src/wolf/08..bc1.tsp`, new `src/wolf/18..bc2.tsp`, shared models in `wtc_inc.tsp`),
  evidence in `evidence/bc-fault-history.md`, `scripts/check.sh` clean (159 messages).
  First use of the `50 00` memory read in the lots: `memr` template with the precomputed CRC.
- **Session 2 done** on 2026-11-16 (second boiler, data logger), in the same log:
  - Lot E: ring order of the fault history proven on both automats (screen of the second
    boiler predicted, then matched 48 of 48).
  - Lot D: burner hours cross-checked on both automats against the `50 22` service-hours read;
    operating hours and burner starts seen to count upwards, low byte first. Burner starts and
    mains-on count still have no independent figure. **Lot D can be written** for operating
    hours and burner hours; starts and mains-on go in with that caveat or wait.
  - New: the data logger reads live values of the automat from RAM with the same `50 00`
    grammar (4 channels matched on the bus, the rest to be resolved from the channel table).
- **Lot D, counters: done** on branch `weishaupt-D` (from `weishaupt-E`, commit `1b33e77`,
  pushed to the fork on 2026-11-17): one message `Counters` per boiler (operating hours, burner hours, burner
  starts), evidence in `evidence/bc-counters.md`, `scripts/check.sh` clean (161 messages).
  Scoped to these counters; the raw memory map stays out. Not yet read by ebusd itself.
- Data logger channel table merged (30 channels of the automat resolved to RAM / XRAM
  addresses, area `3` = XRAM). Material for a later lot of live automat values.
- **Lot F, live values: done** on branch `weishaupt-F` (2026-11-17, see the Lots table). 7 of
  the 30 data-logger channels are in; the others are listed with the reason in
  `evidence/bc-live-values.md` ("Left out"). To close it: load the lot in a test ebusd and read
  `Temperatures` and `Operation` once on each boiler; capture a burner start to tell the output
  bits (RAM `2b`) apart.
- Per-code fault counters (EEPROM `0x0196`–`0x01d7`, 2 bytes each): looked at on 2026-11-17,
  **not written**. The running configuration reads 33 of them on both boilers and the tool
  reads the same area, but no record says where the table "address → fault code" comes from,
  and the tool's statistics screen stays empty on this firmware, so no count has an independent
  figure. Consistent with the fault history for three codes only (first boiler F11 = 1 and
  W12 = 6, second boiler F36 = 309). Missing: the source of the table, and one counter seen to
  step together with a new history entry.
- Next: decide the order of the pull requests after #717 (E, then D, then F; C when #1825 and
  lot B are in).
- Notes go to branch `service-tool`, file `evidence/service-tool-log.md`.

## Conventions

- **Commit identity (2026-11-17, evening).** Every commit of the owner in the four repositories
  (this one, and the forks of ebusd-configuration, ebusd and ebus-typespec) was rewritten to
  carry the GitHub noreply address of the account instead of a personal address: metadata only,
  the tree of every branch and tag was compared before and after and is identical. All branches
  were pushed again (forced), the branches of #717 and #1825 included, and the release tags
  (`weishaupt-0.1.2`, `v0.31.0-weishaupt.1`, `v26.1-weishaupt.1`) moved with their commits, assets
  unchanged. **Every commit id quoted in this plan and in `evidence/` before that moment is a
  former id.** Current heads: lots A `813ac45` (= `weishaupt-pr`, #717), E `f089bc1`, D `e8082bc`,
  F `3dd8ca8`, C `7d62e60`, G `a870515`, H `1a9f922` (local), integration `weishaupt` `cacbf7b` (= tag
  `weishaupt-0.1.2`); ebusd `crc` `492867d9`, `weishaupt` `d4ececb3`; ebus-typespec
  `wcrc-decorator` `75c7d58`, `weishaupt` `6e3e4fc`. The former commits stay reachable on GitHub
  by their id and through the force-push events of the pull requests until GitHub support
  removes them (request to be sent by the owner). `scripts/check.sh` expects the identity
  configured in each repository, now the noreply address.

- Contribution branches: `weishaupt-<lot>` in the fork, rebased on upstream `master`. The
  default branch of `ebus-typespec` is `main`, not `master`: `wcrc-decorator` is rebased on
  upstream `main`.
- No mention of AI tools in commits, pull request texts or comments (rule 9 of `AGENTS.md`).
  Both pull request branches were cleaned on 2026-11-16 (messages only, trees unchanged).
  On 2026-11-17 the same was done for the other fork branches (`master` and `weishaupt-wip`
  of ebusd-configuration, `weishaupt` and `build-macos` of ebusd, tag `v26.1-weishaupt.1`
  moved with its branch, release assets unchanged) and the history of this repository was
  rewritten (commit metadata only, trees unchanged). Older commits stay reachable on GitHub
  through the force-push events of #717 and #1825.
- `scripts/check.sh`, since 2026-11-17, five steps. Step 1 is commit hygiene (rules 4 and 9): on
  the lot branch (`upstream/master..HEAD`, or `LOT_BASE`) and on this repository (unpushed
  commits and the last 20), every commit must carry the expected author and committer identity
  (`user.name` / `user.email` of the repository, or `EXPECT_NAME` / `EXPECT_EMAIL`) and a
  message without tool trailer, tool name or session link; the added lines of the lot branch
  and of the unpushed commits here must hold no private IPv4 address, MAC address, local host
  name, e-mail address or credential assignment. `scripts/check.sh hygiene` runs that step
  alone. In local (Docker) mode the ebusd binary, cached or not, is verified against
  `sha256sums.txt` of its release, as the workflow already did. Each new check was proven with
  a failing case in throwaway clones.
- Toolchain: validated with `@ebusd/ebus-typespec` 0.26. Checked on 2026-11-17 with the
  upstream pins (0.29, compiler 1.12.0, asset-emitter 0.79.1) in a scratch clone of
  `weishaupt-D`: the emitted `wolf/` CSV files are identical. Checked the same day with the
  released library (0.31.0, compiler 1.17) in a scratch copy of `weishaupt-F`: 82 CSV files on
  each side, identical output, so a toolchain bump upstream does not break the lots. Upstream pins `~0.29` with
  `@typespec/compiler ~1.12`, which did not install cleanly with a recent Node.js. Node.js is
  pinned to the LTS major 26 in `.nvmrc` of this repository since 2026-11-17 (`scripts/check.sh`
  warns on another major). Still open: commit a lockfile in the fork (an untracked
  `package-lock.json` sits in the local clone).
  - Cause found (2026-11-16): `ebus-typespec` 0.29 depends on `@typespec/asset-emitter ^0.79.1`;
    without a lockfile npm picks 0.79.3, which imports `sanitizePathSegment` from the compiler
    (present only from 1.17). Workaround on `weishaupt-pr`:
    `npm install --no-save @typespec/compiler@1.12.0 @typespec/asset-emitter@0.79.1`
    (lost on the next plain `npm install`). The upstream config does not compile from a
    fresh install. Already reported in #727 (point 1) and #674; the root cause (asset-emitter
    0.79.2/0.79.3 raised their compiler peer to ^1.16/^1.17) was added as a comment on #727 on
    2026-11-16.
  - Windows: the fork has symlinks (`src/kromschroeder` → `wolf`, `src/vaillant/15.720.tsp`).
    They need Developer Mode and `git config core.symlinks true` before checkout, otherwise they
    become text files and `tsp compile` fails on them.
