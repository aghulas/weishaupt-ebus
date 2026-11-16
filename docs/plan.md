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
| john30/ebusd-configuration#717 | `aghulas:weishaupt-pr` | `34b33cd` | open, no review. 3 commits, 19 files, ~11 300 lines. |

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
Status: **asked on #717 on 2026-11-16**, waiting for an answer.

## Lots

| Lot | Content | Depends on | Status |
|---|---|---|---|
| A | Read-only definitions: `5022` register reads with the CRC precomputed in the ID, passive status messages, time programs as read. No custom decorator needed at runtime, works with stock ebusd. | nothing | in progress — branch `weishaupt-A`, `src/wolf/15..ka.tsp` (18 evidenced reads) |
| B | CRC decorator in `ebus-typespec` (fork to create). Removes the `.js` / `.ts` files from `src/`. | maintainer's answer | to do |
| C | Writes (`5023`) with runtime CRC and setpoint ranges. | #1825, lot B | content exists in #717 |
| D | Raw memory map (`WH11928`). Separate pull request, or left out. | maintainer's answer | content exists in #717 |
| E | WTC fault history, fault counters, service hours. | lot A | to port from the CSV definitions |

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
- **Still to add to Lot A (bus-proven, no CRC):** passive status messages (`KaStatus`,
  `WTCStatus`, `WTCPower`, `HcMode`) and time programs as read.
- **To raise with the maintainer (needs approval, upstream-visible):** the existing `src/wolf`
  reads send `0x00` where the device expects a computed CRC — a latent bug, with bus evidence.
- **Caveat:** `scripts/check.sh` is wired to `src/weishaupt`; it needs a variant for the
  `src/wolf` layout (compile `src/main.tsp`, checkconfig the emitted `wolf/` with root templates).

## Conventions

- Contribution branches: `weishaupt-<lot>` in the fork, rebased on upstream `master`.
- No mention of AI tools in commits, pull request texts or comments (rule 9 of `AGENTS.md`).
  Both pull request branches were cleaned on 2026-11-16 (messages only, trees unchanged).
- Toolchain: validated with `@ebusd/ebus-typespec` 0.26. Upstream pins `~0.29` with
  `@typespec/compiler ~1.12`, which did not install cleanly with a recent Node.js. Pin a Node.js LTS
  version and commit a lockfile in the fork before lot A.
