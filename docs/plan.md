# Contribution plan

Last updated: 2026-11-16.

## State of upstream

- `john30/ebusd`: last commit on `master` 2026-03-29. Several pull requests open since October 2026
  without review.
- `john30/ebusd-configuration`: last commit on `master` 2026-06-09.
- No review or comment yet on #1825 and #717.

Plan accordingly: each lot must be acceptable on its own, and nothing here may depend on a quick merge.

## Open pull requests

| PR | Branch | Head | State |
|---|---|---|---|
| john30/ebusd#1825 | `aghulas:crc` | `02f6de0f` | open, no review. 1 commit, 4 files. |
| john30/ebusd-configuration#717 | `aghulas:weishaupt-pr` | `8c62e41` | **retargeted to Lot A on 2026-11-16**: 7 commits, 9 files, 641 lines, `.tsp` only, read-only, stock ebusd. Old 11 300-line version saved on local branch `backup/weishaupt-pr-717-big`. |

## Known gaps of #717 against the upstream guidelines

1. `src/weishaupt/weishaupt.js` and `weishaupt.ts` (decorators `@wcrc`, `@crcext`, `@appendext`) sit in
   `src/`, which upstream reserves for `.tsp` and i18n YAML files. Decorators belong to the
   `ebus-typespec` library.
2. `tsp format --check` reports all 16 files of `src/weishaupt` as needing format.
3. Lint (`npm run lint`) not run yet: `@typespec/library-linter` was not installed.
4. Size: one pull request of ~11 300 lines, 6 008 of them in `WH11928.tsp` (raw memory map).
5. Depends on #1825 for every write.
6. No German i18n (`de.yaml`). Unknown whether upstream requires it for a new manufacturer.
7. `ChangeOverTime`, `FloorDryingTemp`, `RoomThermostatTemp` use `temp1` (emitted as `D1C`, one byte)
   where the registers are 16-bit with factor 1. To be settled by a bus read.
8. Missing: WTC fault history and fault counters (EEPROM, `5000`), hours since last service
   (info value read through `5022`).

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
| C | Writes (`5023`) with runtime CRC and setpoint ranges. | #1825, lot B | content exists in #717 |
| D | Raw memory map (`WH11928`). Separate pull request, or left out. | maintainer's answer | **blocked on evidence** — the `50 00` memory-read format is uncertain. The deployed config reads `EEA_H_PON`=90, `EEA_H_BON`=216 as 1-byte UCH, but #717 models them as 3-byte U3N and uses a different address byte (`22` vs the deployed `02`); the values are also physically impossible (90 h run < 216 h burner < 430 h since service). So the 1-byte reads are truncated/misaligned and cannot be shipped to the evidence bar (rule 3). Establishing the real format needs deeper reverse-engineering and the vendor service tool to cross-check. Left out until then. |
| E | WTC fault log, service hours. | lot A | **fault log done** on branch `weishaupt-E` (from `weishaupt-A`): 9 read registers `src/wolf/50..em1.tsp` (ErrorId selector + code/type/device/date/time), evidenced on the live boiler (`evidence/em1-fault-log.md`), checkconfig clean. A future PR, to open after #717 merges (depends on its templates). Boiler service hours added too: `BurnerServiceHours` (i45, `50 22` on `bc1` ZZ 08, `src/wolf/08..bc1.tsp`, read live 430 h). Boiler operating hours (`50 00` EEPROM) still belong to the raw memory-map lot. |

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
- `scripts/check.sh` targets `src/wolf` (set `LOT_DIR` for another folder). It compiles
  `src/main.tsp` and runs `ebusd --checkconfig` on the emitted root CSV files plus `wolf/`. The
  last step runs in Docker when available, otherwise in GitHub Actions (workflow
  `.github/workflows/checkconfig.yml` of this repository): the compiled CSV are sent as a
  workflow input, so nothing is pushed to the fork.

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
- Next: evidence records and definitions for the fault history (lot E) and the counters (lot D).
- Notes go to branch `service-tool`, file `evidence/service-tool-log.md`.

## Conventions

- Contribution branches: `weishaupt-<lot>` in the fork, rebased on upstream `master`.
- No mention of AI tools in commits, pull request texts or comments (rule 9 of `AGENTS.md`).
  Both pull request branches were cleaned on 2026-11-16 (messages only, trees unchanged).
- Toolchain: validated with `@ebusd/ebus-typespec` 0.26. Upstream pins `~0.29` with
  `@typespec/compiler ~1.12`, which did not install cleanly with a recent Node.js. Pin a Node.js LTS
  version and commit a lockfile in the fork before lot A.
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
