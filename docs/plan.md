# Plan

State verified against the repositories on 2026-11-20. When this file and a repository disagree,
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
   of a shared program), then request HACS default store on the owner's word.
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
6. **Release 1.0.0**, the promise of stability, tagging both `aghulas/ebusd-configuration` and
   `aghulas/weishaupt-ebus` as `weishaupt-1.0.0`. Releases are no longer flagged pre-release from
   0.6.1 on (owner, 2026-11-20, « Oui, dès la 0.6.1 »): the stable companion requires them, the
   names are frozen and 0.6.0 runs on the installation. Every notice still says in its first
   lines that the definitions were checked on one installation.

Out of 1.0 (compatible additions for 1.x): boiler installer parameters P10–P71
(`docs/boiler-parameters-proposal.md`), remaining register-survey candidates
(`evidence/register-survey-findings.md`), write lines on `75.w.fs2` if proven on a second
installation with separate room units, and upstream merges.

## Current state

### Repositories and releases

| Repository | Branch / tag | Content |
|---|---|---|
| `aghulas/ebusd-configuration` | `weishaupt` `f69ce15` (`weishaupt-0.6.1`, `weishaupt-0.6.2`: same definitions, notice only) | 132 commits on `upstream/master` (`9c3ed3a`): `src/wolf/` definitions — **standard set** 1 074 messages (loads on a stock ebusd, incl. the 3-register carrier `fs1 HolidayStart`), **extension set** (`src/main-ext.tsp`, `src/wolf/*.ext.tsp`) 1 078 = +4 four-register carriers (long IDs, fork build only); 669 in metadata (carriers excluded), 92 writable settings, 252 writable program slots; `src/fr.yaml`, `metadata/weishaupt.toml`, library pin on `v0.31.0-weishaupt.2` |
| `aghulas/ebus-typespec` | `typespec-ext` (`v0.31.0-weishaupt.2`, pre-release); `wcrc-decorator` `75c7d58` (`v0.31.0-weishaupt.1`) | `@crc`, `@wcrc`, and `@fills` + message-level attributes (the `crc`/`fills` columns) |
| `aghulas/ebusd` | `v26.1-weishaupt.2` (extension: computed checksum `crc`, composite reads `fills`, IDs > 7 bytes); `crc` `492867d9` (`v26.1-weishaupt.1`) | Run-time `[WCRC]` register checksum + the extension |
| `aghulas/ha-weishaupt` | `v0.12.1` (Latest, 2026-11-21: Reconfigure is a menu — ebusd/mode, bus load & writes, telegram log — giving the options a UI path the panel's Configure button shadowed since v0.5.0). `v0.12.0`, `v0.11.0`, `v0.12.0b1` kept | Home Assistant companion (out of scope here; consumes `weishaupt-metadata-<version>.json`) |

### Open pull requests

| Pull request | Branch | Status |
|---|---|---|
| [john30/ebusd-configuration#717](https://github.com/john30/ebusd-configuration/pull/717) | `aghulas:weishaupt-pr` `4cd5a54` | Open, mergeable, no review yet |
| [john30/ebusd#1825](https://github.com/john30/ebusd/pull/1825) | `aghulas:crc` `492867d9` | Open, mergeable, no review yet |
| [john30/ebus-typespec#8](https://github.com/john30/ebus-typespec/pull/8) | `aghulas:wcrc-decorator` `75c7d58` | Open, mergeable, no review yet |

Also posted: john30/ebusd#1814 (arbitration data point) and john30/ebusd-configuration#616
(coordination with another contributor converting `J0EK3R/ebusd-configuration-weishaupt`).

Eleven local `upstream/<topic>` branches (`docs/pr-<topic>.md`) wait on #717 and can be refreshed
from `weishaupt` when the maintainer responds.

## Open

### Needs the owner

- **Writes with a stock ebusd (decision deferred by the owner, 2026-11-20).** A stock ebusd with
  the definitions wrote and restored a setting of the system manager on the bus; the system
  manager, room units and heating modules ignore the write checksum (`docs/ebus-protocol.md`,
  `evidence/write-methods.md`). To decide later: the installation notice (the build no longer
  needed for these devices), the companion's write requirement (1.1, guard change), the upstream
  write lots (no dependency on john30/ebusd#1825). Before changing the notice: one end-to-end write
  with the stock add-on on a room unit and a heating module.
- **ebusd extensions (option 2 of `docs/design-register-layer.md`): B and C landed.**
  `docs/ebusd-extension-spec.md`, approved 2026-11-20: computed checksum bytes (attribute `crc`,
  `[WCRC]` kept as alias), message IDs longer than 7 bytes (feature C), composite reads (field
  attribute `fills`, feature B). *Published (2026-11-21, owner's word):* ebusd
  `v26.1-weishaupt.2` (same binary as rc1), the prod add-on bumped, and the TypeSpec library
  `v0.31.0-weishaupt.2` (`@fills` + message attributes). *B landed on `weishaupt` (2026-11-21):*
  the composite-read carrier `fs1 HolidayStart` (3 registers, 7-byte ID), in the standard set;
  library repinned, `scripts/check.sh` on `v26.1-weishaupt.2`; the workbench scripts
  (`metadata.py`, `i18n-keys.py`, `fixtures.py`) made header-aware for the new `crc`/`fills`
  columns; carriers excluded from `metadata/weishaupt.toml` and the companion contract (detected
  via `fills`). *C landed on `weishaupt` (2026-11-21):* the four 4-register carriers (9-byte IDs)
  in an **extension-only variant** (`src/main-ext.tsp` + `src/wolf/*.ext.tsp`, option 1 of
  `out/.../C-isolation-proposal`), kept out of the standard set so it still loads on a stock
  ebusd: `BoilerInfoBlock` on `bc1`/`bc2` (boiler info values) and `RegisterSurvey` on
  `fs2`/`fs3` (a survey grouping, named honestly). `check.sh` now compiles both entry points and
  checkconfigs the **standard set on a standard ebusd** (`v26.1-weishaupt.1`, rejects long IDs →
  1074) and the **extension set on the fork build** (`v26.1-weishaupt.2` → 1078). Guarantee
  confirmed: the standard set loads on upstream ebusd 26.1 and `v26.1-weishaupt.1` (1074); all
  four carriers distribute to their targets on the extension build. Evidence + fixtures for all
  four (`evidence/composite-reads.md`, `evidence/fixtures.toml`). **Pending (separate steps):** the
  release form (extension archives from `release.sh`, to be submitted to the owner), the extension
  add-on wiring, and the upstream pull requests (spec, "Implementation").
- *Done (2026-11-20):* `0.6.0` and `ha-weishaupt` v0.10.0 run on the test installation: nine files
  loaded, no repair, the same number of entities, `LegionellaStartTime` read `08:30`, `DHWExcessTemp`
  10.0, `MixerPump` of `em2` `on`. v0.10.0 is Latest since.
- *Done (2026-11-20):* provisional strings and labels (item 2 of Road to 1.0): none left; the
  notice of 0.6.1 no longer carries the line.
- **Clock automation**: remove or adjust the Home Assistant start trigger that sends
  `Broadcast/Datetime` late after a restart (outside the definitions).
- *Done (2026-11-20):* old lot branches and `backup/*` deleted locally and on the fork, merged
  companion branches and `service-tool` deleted; commits kept in a verified bundle under
  `out/branch-backup-2026-11-20/` (not versioned). Kept: `weishaupt-pr`, `upstream/*`, `maint-0.1`.
- **GitHub support request**: text in `out/github-support-request.md` to purge pre-rewrite commits.

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

### Deferred to 1.x (next vendor service tool pass)

- Boiler installer parameters P10–P71 (`docs/boiler-parameters-proposal.md`).
- Single-source register-survey candidates (`evidence/register-survey-findings.md`).
- Participant at master `00` / slave `05` (`docs/discoveries.md`).
- Which copy (`fs` vs `em`) the regulation uses (`docs/retest-room-unit-2.md`, `copy-in-use`).

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
