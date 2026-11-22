# Plan

State verified against the repositories on 2026-11-22. When this file and a repository disagree,
the repository is right: correct this file. Release history is in `CHANGELOG.md`.

## Direction

Two tracks (`AGENTS.md`, "Goal"):

1. **Fork first (trunk-based).** The definitions, translations (`src/fr.yaml`), metadata sidecar
   (`metadata/weishaupt.toml`) and library pin live on one branch, `weishaupt`, in
   `aghulas/ebusd-configuration`, kept rebased on `upstream/master`. Compiled CSV, metadata and
   fixtures are published from it as releases. Reads work with a stock ebusd; writes need the
   ebusd build of the fork until john30/ebusd#1825 is merged.
2. **Upstream in parallel.** Small, topic-focused pull requests are kept ready and cut from
   `weishaupt` on demand (`upstream/<topic>` branches). Three pull requests are open; the others
   are proposed one at a time when the maintainer responds, on the owner's word (rule 8).

## Road to 1.0

1.0 is a promise of stability, not of completeness: from 1.0 on, a message or field name, a type
and the structure of the metadata change only with a new first number, and someone outside can
install the release without help from here. A second installation is not a condition; until one
exists, the notice states in its first lines that the definitions were checked on one installation.

1. **0.6: last breaking changes, in one release.** *Done (2026-11-20, `weishaupt-0.6.0`).*
   Seven changes (`docs/breaking-changes-0.6.md`), 1 073 messages; names are frozen towards 1.0.
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
`out/ha-deploy-log.md`; evidence to fold into `evidence/write-methods.md` /
`evidence/settings-writes.md` for the next release.

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

## `weishaupt-1.1.0` — landed on `weishaupt`, ready to release

Landed on `weishaupt` (tip `2e9c0bc`), fork-only, nothing pushed or upstream. `scripts/integrate.sh`
green end to end (2026-11-22, Docker): `ebusd --checkconfig` 1 085 messages on both `v26.1-weishaupt.1`
(stock, 7-byte ID limit) and `v26.1-weishaupt.2`; translations fr/de 1 085; metadata 673 messages /
204 entries; fixtures 1 011 readings of 669 messages decoded by `v26.1-weishaupt.2`.

- `59ab941` — A1: fs2 heating program 2 + stored hot-water / circulation documented read-only,
  written through `35.w.fs1` (a direct write to `75` is not kept); heating program 3 left unmarked.
- `d6b2000` — H1Status: module H1 digital input `29 0a` on em2/em3 (on/off), renamed from the wrong
  "solar collector" label; `28 0a` left out (reads only 0).
- `2e9c0bc` — FanOperation: boiler fan speeds read while the burner fires (`bc1`, `bc2`, `@ext 0x56`,
  i23), captured 2026-11-22 (`evidence/boiler-firing-values.md`, `evidence/fixtures.toml`).

A2 (`e2fd`/`e7fd` writable) was already shipped in 1.0.0. Firing values i11/i22/i32 were already
defined (now confirmed with a flame); i30 / RAM `70` / output `2b` bits stay evidence-only (not
labelable without the service tool); i42 = burner starts / 256 is covered by the full counter.

**Next step — release.** `weishaupt-1.1.0` is ready to tag and publish (`scripts/release.sh <version>`,
then push / tag / release on the owner's word, rule 8). The UI-only companion `v1.1.0` is already out
and compatible.

### Deferred (compatible 1.x, not in 1.1.0)

- `FloorDryingTemp` `13 0a` / `RoomThermostatTemp` `1d 0a` suspected 16-bit typing — needs a raw read
  (temp defs on the Pi ebusd + reload, or the next service-tool pass).
- Program selector `12 01` values 12/13 — not reachable through the companion / Pi ebusd (register
  undefined and unpolled, no entity); owner action via the service tool.
- `e6fd` de-couple maximum lower value — `DeCoupleMaxTemp` is read-only in the companion (no `[WCRC]`);
  a raw `ff` write via the service tool / operator.
- `copy-in-use`: 2026-11-22 showed the unit (`fs1`/35) and module (`em1`/50) copies are independent and
  the room-unit entity writes the unit copy; which copy the regulation follows is still open (a
  disambiguating write, unit → a value ≠ module, would settle propagation). `75.w.fs2` heating
  program 3 also still unproven.
- **D — vendor service-tool pass: done 2026-11-22** (display only, both boilers; the tool was
  left disconnected). Landed on `weishaupt` as `4dac6af`, not pushed, not released:
  - *Boiler heating-specialist parameters*: `InstallerParameters1`–`5` on `bc1`, `bc2`, five
    read-only memory reads (the tool's own telegrams), 17 fields: P12, P18, P30, P31, P33, P35–P38,
    P41, P42, P44–P46, P48, P50, P70 (`evidence/bc-installer-parameters.md`). Left out, with the
    reason in the record: P20, P34 (display 0), P23, P32, P40, P43, P47, P49, P51, P71 (no byte
    established), P10, P11, P13–P17 (option bytes). **For the owner:** the new menu "Heating
    specialist parameters" / « Paramètres chauffagiste », the field labels and the French strings
    were written without being put to the owner first; the first read of the five telegrams from
    ebusd's own address is to be looked at when a release with them is deployed.
  - *Single-source register-survey candidates*: every candidate with two sources was already
    defined (1.0.0, 1.1.0). The rest share their value with a neighbour on the same screen, so a
    display-only pass cannot separate them; closed as such in `docs/discoveries.md`.
  - *Participant `00` / `05`*: identified as the vendor's bus interface of the service PC
    (interface version 156.24 in the tool = its version registers); not a part of the heating
    system, no definition (`evidence/master-00-slave-05.md`). Notice "Known limits" updated for
    the next release.
  `scripts/integrate.sh` green (2026-11-22): 1 095 messages on both ebusd builds, 683 in
  metadata / 209 entries, 1 021 fixture readings of 679 messages. A `weishaupt-1.2.0` (compatible:
  ten read-only messages) can be cut on the owner's word once the labels are accepted.
- **E — upstream, in parallel** (owner's word): follow-ups / reviews of #717, #1825, #8.

## Current state

### Repositories and releases

| Repository | Branch / tag | Content |
|---|---|---|
| `aghulas/ebusd-configuration` | `weishaupt` (tip `4dac6af`, local, not pushed: `InstallerParameters1`–`5` on top of `2e9c0bc`, 1 095 messages; released `weishaupt-1.0.0`) | 137 commits on `upstream/master` (`9c3ed3a`): unified `src/wolf/` definitions (`src/main.tsp`) — 1 085 messages (1 077 single-register/memory messages + 8 three-register composite-read carriers with 7-byte IDs that load on both stock `ebusd 26.1` and `v26.1-weishaupt.2`: `HolidayStart` and `HolidayEnd` on `fs1`, `fs2`, `fs3`, `InfoTemperatures` on `bc1`, `bc2`); 673 in metadata (carriers excluded), 92 writable settings, 252 writable program slots; `src/fr.yaml`, `metadata/weishaupt.toml` (with linked bounds `write.below`/`write.above`, `stored_only` on room-unit DHW/circulation programs, `pointer` on `fault_history`, and `shared_with` on `fs2` `HCProgram1`/`HCProgram2`/`DHWProgram`/`CircProgram`), library pin on `v0.31.0-weishaupt.2`; 1.1.0 additions on top of 1.0.0: `H1Status` (module H1 input `29 0a` on em2/em3), `FanOperation` (boiler fan speeds read while the burner fires, `bc1`/`bc2`, `@ext`), and fs2 heating program 2 / stored hot-water / circulation documented as written through `35.w.fs1` |
| `aghulas/ebus-typespec` | `typespec-ext` (`v0.31.0-weishaupt.2`, pre-release); `wcrc-decorator` `75c7d58` (`v0.31.0-weishaupt.1`) | `@crc`, `@wcrc`, and `@fills` + message-level attributes (the `crc`/`fills` columns) |
| `aghulas/ebusd` | `v26.1-weishaupt.2` (extension: computed checksum `crc`, composite reads `fills`, IDs > 7 bytes); `crc` `492867d9` (`v26.1-weishaupt.1`) | Run-time `[WCRC]` register checksum + the extension |
| `aghulas/ha-weishaupt` | `v1.1.0` (Latest, 2026-11-22: UI only — global search, quick filters, program editor; PR #3). `v1.0.0` (definitions 1.0.0, `stored_only` badge), `v0.13.0` (consumes the 0.8.0 metadata fields: linked bounds, `stored_only`, fault pointer, `shared_with`) kept. On the Pi, verified loaded | Home Assistant companion (out of scope here; consumes `weishaupt-metadata-<version>.json`) |

### Open pull requests

| Pull request | Branch | Status |
|---|---|---|
| [john30/ebusd-configuration#717](https://github.com/john30/ebusd-configuration/pull/717) | `aghulas:weishaupt-pr` `4cd5a54` | Open, mergeable, no review yet |
| [john30/ebusd#1825](https://github.com/john30/ebusd/pull/1825) | `aghulas:crc` `492867d9` | Open, mergeable, no review yet |
| [john30/ebus-typespec#8](https://github.com/john30/ebus-typespec/pull/8) | `aghulas:wcrc-decorator` `75c7d58` | Open, mergeable, no review yet |

Also posted: john30/ebusd#1814 (arbitration data point) and john30/ebusd-configuration#616
(coordination with another contributor converting `J0EK3R/ebusd-configuration-weishaupt`).

Upstream topic branches (`upstream/<topic>`, `docs/pr-<topic>.md`) are cut on demand from
`weishaupt` when the maintainer responds to #717.

## Open

### Needs the owner

- **Writes with a stock ebusd (decision deferred by the owner, 2026-11-20).** A stock ebusd with
  the definitions wrote and restored a setting of the system manager on the bus; the system
  manager, room units and heating modules ignore the write checksum (`docs/ebus-protocol.md`,
  `evidence/write-methods.md`). Protocol ready in `docs/test-stock-ebusd-writes.md` for the
  remaining two checks (one room unit and one heating module with the stock add-on).
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
- Which copy (`fs` vs `em`) the regulation uses (`copy-in-use`). *Partly answered 2026-11-22: the
  system manager's DHW setpoint (device 15) is independent of the room-unit copy (ka→fs direction);
  the 0.5 K display test on a room unit vs its module is still open.*

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
