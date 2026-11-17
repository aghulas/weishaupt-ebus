# Contribution plan

Last updated: 2026-11-17.

## State of upstream

- `john30/ebusd`: last commit on `master` 2026-03-29. Several pull requests open since October 2026
  without review.
- `john30/ebusd-configuration`: last commit on `master` 2026-06-09.
- No review or comment by the maintainer on #1825 and #717 (checked again on 2026-11-17, 15:00).

Plan accordingly: each lot must be acceptable on its own, and nothing here may depend on a quick merge.

## Open pull requests

| PR | Branch | Head | State |
|---|---|---|---|
| john30/ebusd#1825 | `aghulas:crc` | `02f6de0f` | open, no review. 1 commit, 4 files. |
| john30/ebusd-configuration#717 | `aghulas:weishaupt-pr` | `a212e73` | **retargeted to Lot A on 2026-11-16**: 10 commits, 9 files, 638 lines, `.tsp` only, read-only, stock ebusd. Old 11 300-line version saved on local branch `backup/weishaupt-pr-717-big`. |

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
  rule 3). It comes back with one manual read by the operator (`50 22`, ID `4d 25 01`, to
  `ZZ 50`).
- Lot A, evidence pass of 2026-11-17 (read-only, nothing changed in the fork):
  - Program slots: all 42 read and recorded (`evidence/em1-clock-program.md`). The request
    payloads seen on the bus equal the `@ext` triples of `50..em1.tsp`, 42 of 42; the CRC byte
    of all 57 triples of the file was recomputed, no mismatch. Hot water is enabled on four
    non-contiguous weekdays, which confirms the weekday nibble. **Closed.**
  - Second boiler: still seen with the burner off only (`WTCStatus` phase `00`, load 0 %,
    `WTCPower` unchanged at `21 17 64`). `evidence/bc1-boiler-status.md` unchanged. **Open**:
    needs a capture while the second boiler fires (cold spell or cascade rotation).
  - Sign of KA registers 3, 13, 14: signed, by the "no sensor" answers of the same registers
    on the other devices (`18 fc` = -100.0, `00 80`) and by the vendor register list
    (`evidence/ka-reads.md`). **Closed**: `DHWSetValue`, `DeCoupleTemp` and `DHWTemp`
    changed from `temp10` to `otemp10` (commit `a212e73`, pushed to `weishaupt-pr`); lots E and
    D rebased on it and pushed again, `scripts/check.sh` clean (160 messages).
  - `SystemHour`: no read-only path. The running configuration has the hour at `25 01` for
    writing only, no cached value, and no telegram with that register in the capture. **Open**:
    one manual read by the operator (`50 22`, payload `4d 25 01`, to `ZZ 50`; expected answer
    two data bytes, hour low byte first, for example `0b 00` at 11 h).
- The comment of 2026-11-16 on #717 describes the former version; a follow-up comment was
  posted on 2026-11-17 (reshape, rename, the two questions still open).
- `weishaupt-E` and `weishaupt-D` were pushed to the ebusd-configuration fork on 2026-11-17 (no
  pull request). `wcrc-decorator` was pushed to the ebus-typespec fork the same day (no pull request).

## Step 0 — ask the maintainer

Before reshaping the pull request, ask on #717 (or issue john30/ebusd#167):
is a new manufacturer welcome, are smaller lots preferred, where should the CRC decorator live.
Status: asked on #717 on 2026-11-16. Rather than wait, #717 was **retargeted** the same day to
Lot A, which answers most of it in code: it extends `src/wolf` (no new manufacturer), is a small
read-only `.tsp`-only change (no `.js`), and needs no CRC decorator (CRC precomputed in the ID).
The `0x00` finding note (`docs/maintainer-note-crc.md`) is drafted but not posted.

## Lots

| Lot | Content | Depends on | Status |
|---|---|---|---|
| A | Read-only definitions: `5022` register reads with the CRC precomputed in the ID, passive status messages, time programs as read. No custom decorator needed at runtime, works with stock ebusd. | nothing | in progress — branch `weishaupt-A`, `src/wolf/15..ka.tsp` (18 evidenced reads) |
| B | CRC decorator in `ebus-typespec`. | maintainer's answer | **done + proven end-to-end** — fork `aghulas/ebus-typespec`, branch `wcrc-decorator`: `@crc(poly, ...)` (compile-time) and `@wcrc(...)` (runtime placeholder + `[WCRC]` marker), 91 tests pass, build clean (commit `5490298`, not pushed). Demo: installed the fork into the config and rewrote 3 ka reads as `@crc(0x5c, ...)` — the emitted `ka.csv` was **byte-identical** to the literal version and passed `ebusd --checkconfig`, so `@crc` reproduces the hand-computed CRCs end-to-end. Demo reverted (no change to `weishaupt-A`); the config's 0.26 toolchain restored. Still exploratory: `@wcrc` feeds Lot C writes (untestable on hardware, rule 7) and ebusd #1825; a permanent wiring needs the decorator released and the config's toolchain bumped (both the maintainer's call). |
| C | Writes (`5023`) with runtime CRC and setpoint ranges. | #1825, lot B (both unmerged, no review) | **prepared, not pushed** — local branch `weishaupt-C` (from `weishaupt-A`, 5 commits, head `e9b176b`): 17 settings read and written, ka (8), em2 (7), fs1 (2). Evidence in `evidence/register-write-crc.md` and `evidence/settings-writes.md`. `scripts/check.sh` clean (167 messages) with the local build of `wcrc-decorator`. Cannot be proposed before #1825 is merged and `@wcrc` is released. See "Lot C" below. |
| D | Raw memory map (`WH11928`). Separate pull request, or left out. | maintainer's answer | **blocked on evidence** — the `50 00` memory-read format is uncertain. The deployed config reads `EEA_H_PON`=90, `EEA_H_BON`=216 as 1-byte UCH, but #717 models them as 3-byte U3N and uses a different address byte (`22` vs the deployed `02`); the values are also physically impossible (90 h run < 216 h burner < 430 h since service). So the 1-byte reads are truncated/misaligned and cannot be shipped to the evidence bar (rule 3). Establishing the real format needs deeper reverse-engineering and the vendor service tool to cross-check. Left out until then. |
| E | WTC fault log, service hours. | lot A | **fault log done** on branch `weishaupt-E` (from `weishaupt-A`): 9 read registers `src/wolf/50..em1.tsp` (ErrorId selector + code/type/device/date/time), evidenced on the live boiler (`evidence/em1-fault-log.md`), checkconfig clean. A future PR, to open after #717 merges (depends on its templates). Boiler service hours added too: `BurnerServiceHours` (i45, `50 22` on `bc1` ZZ 08, `src/wolf/08..bc1.tsp`, read live 430 h). Boiler operating hours (`50 00` EEPROM) still belong to the raw memory-map lot. |

| F | Live values of the WTC automat read from memory (`50 00`, RAM and XRAM). | lot D (`memr` template) | **done** on branch `weishaupt-F` (from `weishaupt-D`, commits `ab5d76c` and `d91dfff`, pushed to the fork, no pull request): `Temperatures` (return, flue gas, flow, outside) and `Operation` (load, ionisation, pump speed), one memory read each, for both boilers. Evidence in `evidence/bc-live-values.md`, `scripts/check.sh` clean (164 messages). The two multi-item requests have not been sent by ebusd yet. |

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

- **Branch**: `weishaupt-C`, local, from `weishaupt-A` (`a212e73`), not pushed, no pull request.
  Based on lot A because it uses its templates and turns its `BlockingTime` read into a read /
  write setting; it touches none of the files of lots E, D and F except `wtc_inc.tsp` (two
  additions, expect a trivial rebase). Commits:
  - `7b6dda5` write template `crcw` / `CrcSetting` with `@wcrc`, `BlockingTime` (ka)
  - `2453311` `ChangeOverTime`, `DeCoupleMinTemp`, `CalorifierSwitchDiff` (ka)
  - `0e2b75b` `DHWSwitchDiff`, `DHWLoadTime`, `LegionellaSetpoint`, `LegionellaCirculationTime` (ka)
  - `eb13044` seven heating-circuit settings (em2)
  - `e9b176b` `SwitchOnRuntime`, `FrostProtectionLimitTemp` (fs1, new file `35..fs1.tsp`)
- **Evidence** (rule 3): for each of the 17 registers, a `50 23` telegram captured passively,
  its checksum recomputed offline, the acknowledgement, a captured read of the same register
  with the same value, and the captured telegram decoded by the lot in the ebusd of the check.
  The change of value itself rests on the operator's write tests of 2026-11-15, by their
  notes. Nothing was written to the installation for this lot (rule 7).
- **Toolchain**: the lot compiles only with `@wcrc`. Checked in a separate worktree of the fork
  clone with the local build of `repos/ebus-typespec` (`wcrc-decorator`, 0.31.0, compiler
  1.17.0) installed with `npm install --no-save`; nothing of that is committed. The clone
  itself was left on `weishaupt-F` with its 0.26 toolchain. To check the branch again: a
  worktree of `weishaupt-C`, the same install, then `CFG_REPO=<worktree> scripts/check.sh`.
- **Blocks the pull request**, in this order:
  1. john30/ebusd#1825 merged and in a released ebusd (run-time checksum, marker `[WCRC]`).
  2. `@crc` / `@wcrc` proposed to john30/ebus-typespec (lot B, no pull request yet), merged
     and released; then the version pin of ebusd-configuration raised to that release.
  3. #717 (lot A) merged, since lot C sits on it.
  4. The operator's test of the definitions through ebusd (four steps in
     `evidence/register-write-crc.md`).
- **Open questions**, for the owner before proposing:
  - `@wcrc` puts the placeholder on the read line too, so the read of a read / write setting
    needs the run-time checksum; `BlockingTime` loses its stock-ebusd read of lot A. Fix
    possible in lot B (emit the checksum of the address as placeholder, #1825 ignores its
    value). See `docs/discoveries.md`.
  - Source address: most settings are taken from `ff` only. The definitions set no `@qq`; a
    comment says `write -s ff`. Setting `@qq(0xff)` would make a plain `write` work but takes
    the address of the vendor service tool by default.
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
  lot B are in), and read `SystemHour` by hand to bring it back.
- Notes go to branch `service-tool`, file `evidence/service-tool-log.md`.

## Conventions

- Contribution branches: `weishaupt-<lot>` in the fork, rebased on upstream `master`.
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
  `weishaupt-D`: the emitted `wolf/` CSV files are identical. Upstream pins `~0.29` with
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
