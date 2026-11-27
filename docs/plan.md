# Plan

State verified against the repositories on 2026-11-27. When this file and a repository disagree,
the repository is right: correct this file. Release history is in `CHANGELOG.md`.

## Roadmap (2026-11-27)

Everything deployed is green (definitions `weishaupt-1.3.1` inside the bridge `weishaupt2mqtt`
`v0.1.3`, companion `ha-weishaupt` `v1.4.1`). `weishaupt-1.3.2` (wording only) is published and not
deployed: the bridge is not rebuilt for three comment lines. What is left is about other people, in this order:

1. *Done (2026-11-27):* **Answer the two outside issues.** `aghulas/ha-weishaupt#1` (a WTC-OB with
   a WCM-FS 2.0, room-unit software `2726`, asking how to trigger the hot-water push: its `05 07`
   telegram decoded with `PowerDemand`, a read-only capture method proposed) and
   `aghulas/weishaupt-ebus#1` (the author of `ebus2mqtt` reusing the check byte and the write
   format). Both stay open; close `weishaupt-ebus#1` after a few days. Captures on
   `ha-weishaupt#1` would be the first evidence from a second installation.
2. **Make the MQTT architecture installable by an outsider.** First GitHub release of
   `weishaupt2mqtt` with notes (only tags so far), a bridge README a newcomer can follow, the MQTT
   path in `docs/release-readme.md` and the front `README.md` (neither mentions the bridge), then a
   cold read as for 0.6.x. In progress; publishing on the owner's word.
3. **Beyond one installation.** Work the captures of `ha-weishaupt#1` when they come; compare with
   what `ebus2mqtt` established on a WTC 15-A/25-A. *Compared offline 2026-11-27
   ([record](../evidence/second-installation-ebus2mqtt.md)): its published room-unit registers,
   63 program windows, status broadcast and check bytes decode with our definitions to its own
   values, one register differs in meaning, and it questions three names of `KaStatus` and the
   "cascade manager" wording around `f1`. Third-party data: no definition added or changed.
   Open: the read-only probe listed at the end of the record (`50 03` on both automats, the
   operating mode `12 01` and the clock registers on `35`), once the adapter is back.*
   *Wording corrected the same day on the owner's word, nothing else: `f1` / `f6` described as
   held by the system manager here and seen without one elsewhere (`docs/ebus-protocol.md`,
   `evidence/broadcast-kastatus.md`); two known limits in the notice (`InstallerParameters1`–`5`
   established on a WTC-GB, room-unit registers and programs compared on a second
   installation); the comment of `PowerDemand` of the three room units and its French key on
   `weishaupt` (`388889e`, local, `scripts/integrate.sh` green). That comment is in the
   compiled CSV (three lines, English and French): it goes out with the next definitions
   release, which the owner decides. Left as it is: the label "Heat demand to the cascade
   manager" of `metadata/weishaupt.toml`, a string accepted by the owner. The names of
   `KaStatus` wait for a bus read on site.*
   *Boiler automat files limited to software 1104 (2026-11-27, prepared locally, not
   released):* `08.w.bc1` / `18.w.bc2` renamed `08.w.bc1.SW1104` / `18.w.bc2.SW1104` on
   `weishaupt` (`c47596b`), so `--scanconfig` loads them only for automats scanned with software
   `1104`; another software gets `08..hc` at `08`, no file at `18`. Same 1 099 messages and CSV
   contents, circuits `bc1` / `bc2`; the metadata changes only in `circuits[].file`
   ([record](../evidence/bc-automat-software.md)). `scripts/integrate.sh` green. Draft in
   `CHANGELOG.md` and the notice. Waits for the owner: version (1.4.0 proposed, 1.3.3 possible)
   and release; then the bridge rebuild (`DEFS_VERSION`) and the metadata copies of the
   companion and the bridge follow by their own sessions, no code change needed there. A scan
   condition (`@condition(Id.Id.sw)`) was tried first and dropped: the extension build does not
   resolve `fills` to unavailable messages (`--checkconfig` error), a candidate fix for
   `aghulas/ebusd` (`MessageMap::resolveFills`).*
4. *Done (2026-11-27, owner's word):* status note posted on #717 (the later write topics no longer
   depend on #1825 or #8, a second installation, release 1.3.2), and a reply on
   `aghulas/weishaupt-ebus#1` asking the author of `ebus2mqtt` for a scan result, the
   identification of `f6`, and raw `05 07` / `50 00` samples; that issue stays open for the
   `50 03` probe on site. Answered the same day with all three (record, section 7): `f6`
   identifies as `WWST1` with the automat's versions, the `05 07` sample decodes with
   `PowerDemand`, the memory block confirms the other layout; replied on the check byte. No capture yet on `ha-weishaupt#1`. Earlier text of this item:
   **Upstream.** #717, #1825 and #8 have had no review and no activity since 2026-11-18. A short
   note on #717 that the write topics no longer depend on #1825 or #8 (`docs/upstream-topics.md`),
   on the owner's word.
5. **Low priority, next vendor service-tool pass:** program selector `12 01`, `e6fd` lower bound,
   the installer parameters left out of `InstallerParameters1`–`5`.
6. **Housekeeping:** the GitHub support request to purge pre-rewrite commits
   (`out/github-support-request.md`, to be sent by the owner). *Done (2026-11-27, owner's word):* merged
   branches of `aghulas/ha-weishaupt` deleted on the fork and locally (three remote, five local;
   each commit already in `main`); kept: `maint-0.1`, the branches behind #717, #1825 and #8, and
   the proposal branches of the ebusd fork.

7. **Vendor codes in the metadata (study, 2026-11-27).** Proposal in
   [design-vendor-codes.md](design-vendor-codes.md): an optional `vendor_codes` list (code, numbering
   scheme, source) on messages and fields under schema 1; lot 1 covers 136 messages from existing
   records, lot 2 needs a manual pass and one look at a room-unit display. *Lot 1 approved by the
   owner on 2026-11-27 with the six choices of section 7, and prepared locally the same day, not
   released:* contract section "Vendor codes", `vendor_schemes` / `vendor_codes` /
   `open.vendor_codes` in `schemas/metadata.schema.json` (schema 1), the checks and the output in
   `scripts/metadata.py` with `tests/test_vendor_codes.py`, the record
   [vendor-codes.md](../evidence/vendor-codes.md) (manual pages re-read: 83258404 pp. 65–67,
   83277504 pp. 31–39, 83251704 pp. 46–51), and the data on `weishaupt` (`metadata: vendor codes,
   lot 1`): 164 codes on 136 messages (44 fields), 141 messages open (34 circuit pairs, 107 of
   lot 2). `scripts/integrate.sh` green, `scripts/release.sh 1.4.0` built locally, nothing
   published. Goes out with the boiler-file change in the next release (draft in `CHANGELOG.md`),
   on the owner's word. Next: `ha-weishaupt` shows the code as an attribute and a panel column
   (decision 5, its own session after the release); lot 2 (a manual pass, pages listed in section
   6 of the study, and one look at the display of the unit for circuits 1 and 2).

## Direction

Two tracks (`AGENTS.md`, "Goal"):

1. **Fork first (trunk-based).** The definitions, translations (`src/fr.yaml`), metadata sidecar
   (`metadata/weishaupt.toml`) and library pin live on one branch, `weishaupt`, in
   `aghulas/ebusd-configuration`, kept rebased on `upstream/master`. Compiled CSV, metadata and
   fixtures are published from it as releases. Reads work with a stock ebusd; the non-boiler
   controllers (`ka`, `em1`–`em3`, `fs1`–`fs3`) also take writes from a stock ebusd end to end
   (placeholder checksum, proven 2026-11-22/23 on `15`, `35`, `51`), so the fork ebusd build adds
   the composite-read distribution (`@fills`) and the run-time checksum (john30/ebusd#1825) but is
   not required to write the settings published here.
2. **Upstream in parallel.** Small, topic-focused pull requests are kept ready and cut from
   `weishaupt` on demand (`upstream/<topic>` branches). Three pull requests are open; the others
   are proposed one at a time when the maintainer responds, on the owner's word (rule 8).

## Road to 1.0

1.0 is a promise of stability, not of completeness: from 1.0 on, a message or field name, a type
and the structure of the metadata change only with a new first number, and someone outside can
install the release without help from here. A second installation is not a condition; until one
exists, the notice states in its first lines that the definitions were checked on one installation.

1. **0.6: last breaking changes, in one release.** *Done (2026-11-20, `weishaupt-0.6.0`).*
   Seven changes, 1 073 messages; names are frozen towards 1.0.
2. **Nothing provisional left.** *Done (2026-11-20, for 0.6.1).* Every French string and the
   wording choices accepted by the owner; the label of `ForcedVenting` kept as "Ventilation
   forcée" (« je préfère Ventilation forcée »): the wording, not the meaning, which stays not
   established. `evidence/terms.md` and `metadata/weishaupt.toml` hold nothing provisional.
3. **Known doubts settled or stated.** *Done (2026-11-20, for 0.6.1).* Stated as not
   established in "Known limits" of `docs/release-readme.md`: the sharing of heating programs 2
   and 3 and the hot-water and circulation programs of `75.w.fs2`, the participant at `00` /
   `05`, and what phase 9 (`ForcedVenting`) is. 0.6.1 (compatible) waits for the cold read of
   the notice (item 4).
4. **An installation notice someone else can follow**, start to end (`docs/release-readme.md`):
   files, ebusd build for writes, companion. Read once without workbench context. *Cold read of
   0.6.0 done (2026-11-20, `out/cold-read-0.6.0.md`): reading yes, add-on by guessing, writing no.
   Notice rewritten for 0.6.1 (definitions side): use and limits first; walk-throughs for a plain
   ebusd and the add-on with expected output; the write-capable build for both and a check of
   which ebusd runs (both verified in containers, nothing sent); how to write; counts with their
   source; glossary. Front `README.md` the same. Published as `weishaupt-0.6.1`, the first
   normal release, with the companion's README of v0.10.1 (2026-11-20). The front page of
   `aghulas/ha-addons` (branch `weishaupt`) now says what the add-on is and how to install it
   (owner's word, 2026-11-20). *Second cold read of the published 0.6.1 done
   (`out/cold-read-0.6.1.md`): reading yes; writing yes for one numeric setting after opening the
   CSV, no for the date and time. Third pass on the owner's « Oui, les trois »: notice and front
   README for 0.6.2 (documentation only, workbench); the companion's README and the add-on's
   documentation by their sessions. Published 2026-11-20: `weishaupt-0.6.2`, `ha-weishaupt`
   v0.10.2 (Latest), the add-on's DOCS.md, README and store description on `aghulas/ha-addons`
   `weishaupt`. The companion was checked on site with port 8888 of the add-on not published.
   Open: a third cold read is optional; the remaining doubt is that every reading so far was on
   paper, without a heating system.*
5. **Companion.** Complete the two remaining checks on site (non-admin user view, dashboard card
   of a shared program). HACS default store not pursued — the companion stays a custom repository
   (owner, 2026-11-22, « Reste en dépôt personnalisé »): it already installs that way, and the
   default store would need an original non-trademark icon plus a `home-assistant/brands` PR and a
   `hacs/default` PR, all owner-driven. Companion thread closed.
   *0.12.0b1 (pre-release, 2026-11-21): choice of the ebusd (`out/companion-ebusd-choice-proposal.md`,
   approved as recommended). Next: the on-site read-only checks listed in
   `out/ha-weishaupt-0.12.0-release-notes.md`, by the deploy session on the owner's word in its window,
   then 0.12.0.*
   *0.12.0 published 2026-11-21 (Latest): the follow/pin choice got a UI path (a « Which ebusd » step at
   the end of Reconfigure), the on-site read-only trial of the beta passed (migration, follow switch, probe,
   repairs — nothing on the bus). The deploy session updates the Pi from the beta to 0.12.0. Known limit, since
   v0.5.0: the Configure button opens the panel, so the options flow (bus load/writes, telegram log per ebusd)
   has no UI path — a candidate follow-up to fold into Reconfigure.*
   *0.12.1 published 2026-11-21 (Latest): that follow-up is done — Reconfigure became a menu (ebusd/mode,
   bus load & writes, telegram log per ebusd), the options flow kept for the API and tests, both paths sharing
   the same helpers. The deploy session updates the Pi from the beta straight to 0.12.1.*
   *Companion closed 2026-11-22: stays a custom repository (HACS default store not pursued). The Pi
   update is done and the companion has moved on past it: the deploy session installed, through the
   Marketplace under its own service user (connector PR #15), `0.13.0`, then `1.0.0`, then `1.1.0`,
   each verified loaded on the Pi (last: v1.1.0 installed, integration `loaded`, panel checked in the
   browser — search, quick filters, program editor). `1.1.0` (2026-11-22) is UI only, no definitions
   change. Definitions metadata fields added for the companion (linked bounds, `stored_only`, fault
   pointer, `shared_with`) are now exercised end-to-end on the installation (see On-site write
   validation below).*
6. **Release 1.0.0**, the promise of stability, tagging both `aghulas/ebusd-configuration` and
   `aghulas/weishaupt-ebus` as `weishaupt-1.0.0`. *Published 2026-11-22* (alongside `ha-weishaupt`
   `v1.0.0`; 1 081 messages, 669 in metadata, 668/668 readable messages covered by 1 008 fixtures).
   Every notice still says in its first lines that the definitions were checked on one installation.

### On-site write validation (2026-11-22)

Four guarded, reversible write tests on the installation, each on the owner's yes in the deploy
session's own window, through `ha-weishaupt` (0.13.0→1.0.0) on the extension build
(`v26.1-weishaupt.2`). They prove the companion writes settings from source `ff` with the run-time
computed checksum, and that the `1.0.0` metadata fields behave as intended. Logged in
`out/ha-deploy-log.md`; findings folded into `evidence/settings-writes.md` and
`evidence/room-units-shared-store.md` (published in `weishaupt-1.3.0`).

1. **Shared program (room unit 35 → 75).** A heating program slot written on `fs1` read back
   identical on `fs2` within 3 s; exactly two `50 23` from `ff`, none to `75`. Confirms the
   `shared_with` store, write path proven.
2. **Linked bounds (setback, 35).** Valid value taken; out-of-bound value **rejected by the entity
   before any bus write** ("outside valid range"), nothing emitted; sibling bound constrains the
   range. Confirms `write.below`/`write.above`.
3. **System manager DHW setpoint (device 15, first write to 15).** Taken on `15`; the room unit's
   `fs1` DHW setpoint stayed put — so this setpoint is **independent** of the room-unit copy
   (advances `copy-in-use`, ka→fs direction). Two `50 23` to `15`.
4. **Regulation-class write (heating module 51, Maximum flow temperature).** Regulation write path
   validated end-to-end with its **two-screen confirmation** (caution note + "Write to the
   controller"); two `50 23` to `51`. Comfort writes are immediate, regulation ones need the second
   screen.

Across the four: write path confirmed on **three device types** (room unit 35 with shared store,
system manager 15, heating module 51) and both risk classes. Nothing left applied; Writes off.

## `1.1.0` – `1.3.0` (published and deployed, 2026-11-22)

Three compatible releases on top of `1.0.0` (no breaking changes), all tagged on both
`aghulas/ebusd-configuration` and `aghulas/weishaupt-ebus`, verified with `scripts/integrate.sh`
against both `v26.1-weishaupt.1` (stock 7-byte ID limit) and `v26.1-weishaupt.2`, and deployed up
to `weishaupt-1.3.0` on the test installation (`out/ha-deploy-log.md`):

- **`weishaupt-1.1.0`** (`2e9c0bc`, 1 085 messages / 673 in metadata / 1 011 fixtures):
  - `59ab941` — `75.w.fs2` heating program 2 + stored hot-water / circulation documented read-only,
    written through `35.w.fs1`.
  - `d6b2000` — `H1Status`: module H1 digital input `29 0a` on `em2`/`em3` (on/off).
  - `2e9c0bc` — `FanOperation`: boiler fan speeds read while the burner fires (`bc1`, `bc2`, `@ext
    0x56`, i23; `evidence/boiler-firing-values.md`).
- **`weishaupt-1.2.0`** (`4dac6af`, 1 095 messages / 683 in metadata / 1 021 fixtures):
  - `InstallerParameters1`–`5` on `bc1`/`bc2` (17 heating-specialist parameters P12–P70 from the
    2026-11-22 vendor service-tool pass, `evidence/bc-installer-parameters.md`), new metadata menu
    `specialist`. First live read by ebusd confirmed on deployment (`InstallerParameters1` / `2`).
  - Participant `00` / `05` identified as the vendor's bus interface (`evidence/master-00-slave-05.md`);
    notice *Known limits* updated.
  - Remaining single-source survey candidates closed for a display-only pass (`docs/discoveries.md`).
- **`weishaupt-1.3.0`** (`7462afb`, Latest, 1 099 messages / 687 in metadata / 210 entries / 1 025
  fixtures of 683 messages; deployed on the test installation):
  - `b24a3b5` — `FloorDryingTemp` (`13 0a`) / `RoomThermostatTemp` (`1d 0a`) re-added read-only as
    16-bit (`otemp10`) on `fs1` and `em2` (`evidence/room-thermostat-floor-drying.md`).
  - `7462afb` — `75.w.fs2` heating program 3 documented shared with `35.w.fs1` (`shared_with` now
    covers all five `fs2` program stores; `evidence/room-units-shared-store.md`, section 5).
  - Evidence-only additions (`evidence/settings-writes.md`): `DeCoupleMinTemp` write path confirmed
    (regulation class, 0–50 bound enforced; `DeCoupleMaxTemp` stays read-only) and `copy-in-use`
    shown independent in both directions (`open = ["copy-in-use"]` kept).

- **`weishaupt-1.3.2`** (`388889e`, Latest, 1 099 messages / 687 in metadata / 210 entries / 1 029
  fixtures of 686 messages; published 2026-11-27 on the owner's word, re-downloaded, checksums
  verified, both archives loaded by the stock `john30/ebusd:v26.1`: 1 099 messages): comment of
  `PowerDemand` of the three room units (master `0xf1`, the cascade manager where one is fitted)
  and two known limits in the notice, after the comparison with a second installation
  (`evidence/second-installation-ebus2mqtt.md`). Not verified on site (adapter down).

- **`weishaupt-1.3.1`** (`84fe069`, 1 099 messages / 687 in metadata / 210 entries / 1 025
  fixtures of 683 messages; published 2026-11-24):
  - `84fe069` — cleared all 50 `open = ["copy-in-use"]` markers in `metadata/weishaupt.toml`
    following the 2026-11-23 active-heating resolution (`evidence/settings-writes.md`).
  - Installation notice (`docs/release-readme.md`) aligned on stock `ebusd 26.1` writes,
    `75.w.fs2` program 3 sharing, `copy-in-use` resolution, and `@EBUSD@`; metadata count
    parameterized as `@META_COUNT@` in `scripts/release.sh`.

### Remaining 1.x candidates (low priority, no release blocked)

- Program selector `12 01` values 12/13 — not reachable through the companion / Pi ebusd (register
  undefined and unpolled, no entity); owner action via the service tool.
- `e6fd` de-couple maximum lower value — `DeCoupleMaxTemp` stays read-only (no `[WCRC]`); requires
  a raw `ff` write below 78.0 °C via the service tool / operator.
- `copy-in-use` (`fs` vs `em` copies) — resolved 2026-11-23 on circuit 2 during active heating:
  regulation strictly follows the room-unit (`fs`) copy (`SupplyHCSetTemp` moved from 58.1 to 60.9 °C;
  module write did not move flow setpoint); `evidence/settings-writes.md`.
- Upstream follow-ups / reviews of #717, #1825, #8, #1835 (on the maintainer's reply, owner's word).

## Current state

### Repositories and releases

| Repository | Branch / tag | Content |
|---|---|---|
| `aghulas/ebusd-configuration` | `weishaupt` (tip `388889e`; released `weishaupt-1.3.2`, Latest, 1 099 messages) | 140 commits on `upstream/master` (`9c3ed3a`): unified `src/wolf/` definitions (`src/main.tsp`) — 1 099 messages (including 10 composite-read carriers with 7-byte IDs that load on both stock `ebusd 26.1` and `v26.1-weishaupt.2`: `HolidayStart` / `HolidayEnd` on `fs1`–`fs3`, `InfoTemperatures` / `FanOperation` on `bc1`–`bc2`); 687 in metadata (210 entries, `copy-in-use` cleared), 92 writable settings, 252 writable program slots; `src/fr.yaml`, `metadata/weishaupt.toml` (with linked bounds `write.below`/`write.above`, `stored_only` on room-unit DHW/circulation programs, `pointer` on `fault_history`, `specialist` menu for `InstallerParameters1`–`5`, and `shared_with` on all five `fs2` program stores), library pin on `v0.31.0-weishaupt.2`. On the test installation at `1.3.1`, bundled in the `weishaupt2mqtt` add-on (`out/ha-deploy-log.md`) |
| `aghulas/ebus-typespec` | `typespec-ext` (`v0.31.0-weishaupt.2`, pre-release); `wcrc-decorator` `75c7d58` (`v0.31.0-weishaupt.1`) | `@crc`, `@wcrc`, and `@fills` + message-level attributes (the `crc`/`fills` columns) |
| `aghulas/ebusd` | `v26.1-weishaupt.2` (extension: computed checksum `crc`, composite reads `fills`, IDs > 7 bytes); `crc` `492867d9` (`v26.1-weishaupt.1`) | Run-time `[WCRC]` register checksum + the extension |
| `aghulas/weishaupt2mqtt` | `main` (tagged `v0.1.3`, 2026-11-25; no GitHub release yet, see Roadmap item 2) | All-in-one functional MQTT bridge (pure Python 3.11+, bundles ebusd with CRC and definitions 1.3.1, guarded level-1/level-2 writes under Option B, program diffs, hourly on-demand settings/counters poll, native clock sync, HA Supervisor MQTT auto-auth). Deployed on the test installation as add-on `09e0ce7c_weishaupt2mqtt` |
| `aghulas/ha-weishaupt` | `v1.4.1` (Latest, 2026-11-25: fix of the clock-offset sensor in MQTT mode; on the test installation, 319 tests pass). `v1.4.0` (MQTT transport mode consuming `weishaupt2mqtt` over HA MQTT with guarded Level 1/Level 2 writes and seamless migration from ebusd TCP; deployed and write-verified on site), `v1.3.0` (opt-in **Allow writes on a stock ebusd**), `v1.2.0` (definitions 1.3.0), `v1.1.0` (UI), `v1.0.0`, `v0.13.0` kept | Home Assistant companion (consumes `weishaupt2mqtt` MQTT or `ebusd` TCP + `weishaupt-metadata-<version>.json`) |

### Open pull requests

| Pull request | Branch | Status |
|---|---|---|
| [john30/ebusd-configuration#717](https://github.com/john30/ebusd-configuration/pull/717) | `aghulas:weishaupt-pr` `4cd5a54` | Open, mergeable, no review yet |
| [john30/ebusd#1825](https://github.com/john30/ebusd/pull/1825) | `aghulas:crc` `492867d9` | Open, mergeable, no review yet |
| [john30/ebus-typespec#8](https://github.com/john30/ebus-typespec/pull/8) | `aghulas:wcrc-decorator` `75c7d58` | Open, mergeable, no review yet |

Checked 2026-11-27: no review on any of the three, last activity 2026-11-17/18.

Also posted: john30/ebusd#1814 (arbitration data point) and john30/ebusd-configuration#616
(coordination with another contributor converting `J0EK3R/ebusd-configuration-weishaupt`).

Upstream topic branches (`upstream/<topic>`) are cut on demand from `weishaupt` when the maintainer
responds to #717; their prepared titles and bodies are in `docs/upstream-topics.md`.

## Open

### Needs the owner

- *Done (2026-11-24):* **Functional MQTT bridge (`weishaupt2mqtt`).** Architecture deployed on site
  to make MQTT the single default interface for all operations (replacing raw ebusd TCP):
  `aghulas/weishaupt2mqtt` created, tested with unit tests and live reversible write tests, and
  deployed as Home Assistant add-on `09e0ce7c_weishaupt2mqtt` v0.1.2. Legacy `09e0ce7c_ebusd` uninstalled.
  Option B level separation applied: level 1 user writes on `weishaupt/<circuit>/set`, level 2
  installer writes on `weishaupt/<circuit>/installer/set` with confirmation, minimal program diffs
  on `weishaupt/<circuit>/program/<id>/set`. `ha-weishaupt` consumes MQTT directly since `v1.4.0`
  (2026-11-25); the add-on is at `v0.1.3`.
- *Done (2026-11-23):* **Writes with a stock ebusd.** The two remaining end-to-end checks ran on
  site (operator present, vendor service tool disconnected, no `ff` telegram in the prior 15 min)
  with the stock `ebusd 26.1.26.1` (no `-weishaupt` build) and the 1.3.0 definitions: room unit
  `fs1` (`HolidayStartDay`, source `ff`), heating module `em2` (`SupplyMinTemp`, source `31`;
  `RoomFrostProtectionTemp`, source `ff`) — all three TAKEN, restored, the controller accepting a
  placeholder/unchecked CRC byte (`evidence/write-methods.md`, section 2026-11-23). With the
  earlier system-manager `15` result, **all non-boiler controllers** (`ka`, `em1`–`em3`,
  `fs1`–`fs3`) can be written end to end by a stock `ebusd 26.1` without `john30/ebusd#1825`; the
  fork build is needed only for `@fills` composite-read distribution. The decision in
  `docs/test-stock-ebusd-writes.md` is carried out: notice wording updated
  (`docs/release-readme.md`, `README.md`); the `ha-weishaupt` write guard relaxed as an opt-in
  **Allow writes on a stock ebusd** (PR #4, released `v1.3.0` on the owner's word, 2026-11-23); the
  upstream write topics prepared to cut without `#1825`/`#8` (`docs/upstream-topics.md`), held until
  the maintainer responds.
- *Done (2026-11-22):* **Clock automation** verified on site (`weishaupt_clock_sync` triggers only
  every 30 min, no HA start trigger; preserves outside temperature from `f1fe070009`).
- **GitHub support request**: text ready in `out/github-support-request.md` to purge pre-rewrite
  commits on the four repositories.
- **ebusd extensions (option 2 of `docs/design-register-layer.md`): unified 3-register carriers landed.**
  `docs/ebusd-extension-spec.md`, approved 2026-11-20: computed checksum bytes (attribute `crc`,
  `[WCRC]` kept as alias), message IDs longer than 7 bytes (feature C), composite reads (field
  attribute `fills`, feature B). *Published (2026-11-21, owner's word):* ebusd
  `v26.1-weishaupt.2`, the prod add-on bumped, and the TypeSpec library `v0.31.0-weishaupt.2`
  (`@fills` + message attributes). *Unified on `weishaupt` (2026-11-22):* rather than maintaining a
  separate 4-register extension variant (`src/main-ext.tsp`, 9-byte IDs rejected by stock ebusd),
  the single unified `src/main.tsp` tree carries all eight proven 3-register composite-read
  carriers (7-byte IDs, `@crc(0x5c, ...)` + `@fills`): `HolidayStart` and `HolidayEnd` on `fs1`,
  `fs2`, `fs3`, and `InfoTemperatures` on `bc1`, `bc2`. `scripts/check.sh` verifies that the single
  compiled CSV tree loads cleanly on both `v26.1-weishaupt.1` (stock 7-byte ID limit → 1 081
  messages) and `v26.1-weishaupt.2` (extension build → 1 081 messages), and `scripts/release.sh`
  produces a single pair of archives (EN and FR).
- *Done (2026-11-20):* `0.6.0` and `ha-weishaupt` v0.10.0 run on the test installation: nine files
  loaded, no repair, the same number of entities, `LegionellaStartTime` read `08:30`, `DHWExcessTemp`
  10.0, `MixerPump` of `em2` `on`. v0.10.0 is Latest since.
- *Done (2026-11-20):* provisional strings and labels (item 2 of Road to 1.0): none left; the
  notice of 0.6.1 no longer carries the line.
- *Done (2026-11-20):* old lot branches and `backup/*` deleted locally and on the fork, merged
  companion branches and `service-tool` deleted; commits kept in a verified bundle under
  `out/branch-backup-2026-11-20/` (not versioned). Kept: `weishaupt-pr`, `maint-0.1`.

### Needs the maintainer

- **Home Assistant forum topic** posted by the owner on 2026-11-20 (category Share your Projects ›
  Custom Integrations, without screenshots), awaiting the forum's review.
- **Replies posted 2026-11-20** (owner's word): john30/ebusd#167 (the generic checksum proposal,
  following the owner's comments of March) and john30/ebusd-configuration#461 (the maintainer's
  "integrate weishaupt": what exists, #717, coordination with #616, call for testers).
- **Discussion john30/ebusd#1835** (opened 2026-11-20, owner's word): the protocol in short, what is
  published, and the three proposals of `docs/ebusd-extension-spec.md` (computed checksum bytes,
  composite reads, IDs longer than 7 bytes), with four questions to the maintainer and a call for
  testers. Answers there may change the spec before the ebusd code is reviewed.
- Review of #717, #1825, #8.
- Clarification on Wolf device scan identification (asked in #717) and `de.yaml` expectations.

### Deferred to 1.x (next vendor service tool pass — checklist in `docs/next-service-tool-session.md`)

- *Done 2026-11-22 (see "Deferred", item D):* boiler heating-specialist parameters landed
  (`4dac6af`); the remaining single-source survey candidates closed for a display-only pass;
  participant `00` / `05` identified (the vendor's bus interface).
- Which copy (`fs` vs `em`) the regulation uses (`copy-in-use`). *Resolved 2026-11-23: both
  copies are independent stores; the +1.0 °C supply-setpoint test confirmed the regulation loop
  calculates exclusively from the room unit (`fs`) copy (`evidence/settings-writes.md`).*

## Conventions

- **Trunk and integration.** Work goes directly on `weishaupt` in `repos/ebusd-configuration`
  (one topic per commit, rebased on `upstream/master`). `scripts/integrate.sh` checks out
  `weishaupt` in a clean worktree (`out/integration`), verifies it is rebased on
  `upstream/master`, installs dependencies and runs `scripts/check.sh` with `METADATA=required`.
- **Check.** `scripts/check.sh` runs 7 steps: commit hygiene (identity, no tool mention, no site
  data), file types, `tsp format --check`, `tsp compile`, `ebusd --checkconfig` in Docker (with
  SHA-256 verified binary), translations (`scripts/i18n-keys.py`), and metadata + fixtures
  (`scripts/metadata.py`, `scripts/fixtures.py`). Run `python3 -m unittest discover -s tests -v`
  after editing workbench scripts or schemas.
- **File names.** `ZZ.w.<circuit>.tsp`: slave address, scan identification (`W`), circuit. Imports
  in `src/main.tsp` are kept sorted by hand (`npm run maintsp` rewrites unrelated lines).
- **Translations.** Every English comment added or changed needs its key in `src/fr.yaml`
  (patterned entries regenerated via `scripts/i18n-patterns.py`; terms recorded in
  `evidence/terms.md`).
- **Metadata & schemas.** `metadata/weishaupt.toml` lives on `weishaupt`; generated JSON assets
  are validated against `schemas/metadata.schema.json` (schema 1) and
  `schemas/fixtures.schema.json` (schema 2) by `scripts/validate-schema.py` during
  `scripts/release.sh`.
- **Fixtures.** `evidence/fixtures.toml` transcribes telegrams already recorded in `evidence/*.md`
  and is decoded by the real `ebusd` binary (`--inject=stop`).
- **Versions.** Up to 0.6.0, breaking changes bumped the second number. Names, types and the
  metadata structure are frozen since 0.6.0: a breaking change now needs a new first number.
  Renames carry `renamed_from` in metadata.
- **Notice table.** The table "What can be written" of `docs/release-readme.md` is the output of
  `scripts/settings-table.py` on the release's metadata, pasted between its two markers: run it
  again when a write is added, removed or its range changes.
- **Release.** `scripts/release.sh <version>` builds reproducible archives (`weishaupt-ebusd-config-<version>.tar.gz` and `-fr.tar.gz`), `weishaupt-metadata-<version>.json`,
  `weishaupt-fixtures-<version>.json` and `sha256sums-<version>.txt` under `out/release/`. On the
  owner's word: push `weishaupt`, tag both `ebusd-configuration` and `weishaupt-ebus` as
  `weishaupt-<version>`, publish the release (a normal release from 0.6.1 on, not a
  pre-release), re-download and verify against official ebusd.
- **Writes use source `ff`.** Definitions never hardcode `@qq`; callers pass `-s ff` where
  required and never write while the vendor service tool is connected.
- **Commit identity & toolchain.** All repos use the account's GitHub noreply address; no mention
  of AI tools (rule 9). Node.js LTS major is pinned in `.nvmrc`.
