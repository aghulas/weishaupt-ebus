# Plan

State verified against the repositories on 2026-11-17 (evening). When this file and a
repository disagree, the repository is right: correct this file.

## Direction

Two tracks (`AGENTS.md`, "Goal"), decided on 2026-11-17 because the pull requests upstream had
no review and outside pull requests there have waited from three weeks to five months.

1. **Fork first.** The lots are stacked branches in `aghulas/ebusd-configuration`. The
   integration branch `weishaupt` is the top of the stack plus one commit that pins the library
   package of the fork. Compiled CSV are published from it as releases. Reads work with a stock
   ebusd; writes need the ebusd build of the fork until john30/ebusd#1825 is merged.
2. **Upstream in parallel.** The same lots stay ready as pull requests. Three are open; the
   others are opened lot by lot when the maintainer responds, on the owner's word (rule 8).

What this costs: the fork is a distribution to maintain (releases, following upstream version
bumps).

## Current state

### Lots

All lot branches are in `aghulas/ebusd-configuration`, one on top of the other in this order,
on upstream `master` (`9c3ed3a`, nothing to rebase). Files are under `src/wolf/`.

| Lot | Content | Branch, head | Evidence |
|---|---|---|---|
| A | Register reads (`50 22`, checksum precomputed in the ID) of the system manager; status broadcast and the status each boiler sends to the cascade master; room unit / module exchange `HcMode`; system clock and the weekly hot-water and circulation programs of `50`. Reads only, stock ebusd. Files `15.w.ka`, `50.w.em1`, `51.w.em2`, `52.w.em3`, `broadcast`, `wtc_inc`. | `weishaupt-A` `66b775e`, on the fork as `weishaupt-pr` (14 commits). **Pull request #717.** | `ka-reads`, `register-crc`, `broadcast-kastatus`, `bc1-boiler-status`, `em-hcmode`, `em1-clock-program` |
| E | Fault log of the system (`50.w.em1`), hours since last service and fault history of both boiler automats, first use of the memory read `50 00` (`08.w.bc1`, `18.w.bc2`). | `weishaupt-E` `3e9347f` (4 commits on A), pushed | `em1-fault-log`, `bc-fault-history` |
| D | Counters of both automats: operating hours, burner hours, burner starts. Not the whole memory map. | `weishaupt-D` `bd1c760` (1 commit on E), pushed | `bc-counters` |
| F | Live values of both automats from RAM / XRAM: `Temperatures` (return, flue gas, flow, outside), `Operation` (load, ionisation, pump speed). | `weishaupt-F` `c4bc54c` (2 commits on D), pushed | `bc-live-values` |
| C | 17 settings read and written (`50 23`, checksum computed by ebusd at run time, decorator `@wcrc`): 8 on the system manager, 7 on heating module `51`, 2 on room unit `35`. | `weishaupt-C` `1289f97` (5 commits on F), pushed | `register-write-crc`, `settings-writes` |
| G | Reads of the heating-circuit values and settings on the three room units (new files `75.w.fs2`, `f5.w.fs3`) and the three heating modules. | `weishaupt-G` `de1e38b` (2 commits on C), pushed | `room-units-reads`, `heating-modules-reads` |
| H | Weekly programs of the three room units, read side: heating programs 1 to 3, then hot water and circulation in a second commit that can be dropped alone. 315 messages. | `weishaupt-H` `6a46518` (3 commits on G), pushed | `room-units-programs` |
| J | Fault counters of both automats: one counter per fault number (33, numbers 11 to 57), six memory reads of EEPROM `0x0196`–`0x01d7` per boiler, 12 messages. Address and number from the symbol table of the firmware, meaning from the manual of the boiler (48 as a warning and 49 only in its 2020 edition). | `weishaupt-J` `9e8cdd3` (1 commit on H), **local only** | `bc-fault-counters` |
| L | French translation of the comments: `src/fr.yaml`, 267 keys for the 267 comment strings of the lots (193 from vendor terms, 68 accepted by the owner, 6 provisional); the 24 Wolf comments of `wolf/broadcast` stay in English. No definition; no upstream pull request is cut from it. | `weishaupt-L` `a22b797` (7 commits on J), pushed | `terms` |
| I | Weekly programs of the devices other than the room units (`15`, `50`, `f6`, `51`, `52`): examined on 2026-11-17, **nothing defined**. `15`, `50` and `f6` answer identical bytes on all 105 slots; `51` and `52` hold the heating programs of `15` and the hot-water and circulation programs of the room units. Hot water follows the program of the system manager, which lot A already defines at `50`; the third heating circuit follows its room unit (lot H) and its module does not apply its own programs. The rest would be schedules the installation does not follow, or a copy of lots A and H. | none, no branch | `modules-programs` |
| B | Library: decorators `@crc` (checksum computed when emitting) and `@wcrc` (marker for the run-time checksum; the byte emitted is the checksum of the address, so reads stay valid on a stock ebusd). | `aghulas/ebus-typespec`, `wcrc-decorator` `75c7d58`. **Pull request #8.** | `register-write-crc` section 5 |
| — | ebusd: checksum computed at run time for messages marked `[WCRC]`. | `aghulas/ebusd`, `crc` `492867d9`. **Pull request #1825.** | `register-write-crc` |

The lot letters are historical; the stack order is A, E, D, F, C, G, H, J, L (`STACK` in
`scripts/integrate.sh`). `weishaupt-L` holds the translation files and stays on top: a new lot
goes below it. Lot C needs lot B to compile and #1825 to send. For a pull request
upstream, C, G and H are cut again on lot A.

Integration branch: `weishaupt` `b831213`, the stack A to H, J and L plus the pin commit, on
the fork since 2026-11-18 (forced from `bd35b2c` on the owner's word, with `weishaupt-L`
fast-forward to `a22b797`). `scripts/check.sh` on it: clean, **586 messages** in English,
German and French. Released from it on 2026-11-18 as the pre-release `weishaupt-0.3.1` (tag
on `b831213`), made by `scripts/release.sh 0.3.1`: the French archive has the wording the
owner decided and the Wolf messages of the broadcast file in English again; the CSV files of
the English archive are those of 0.3.0, only the notice differs. Both archives downloaded
again after publication: checksums right, 586 messages without error in the official ebusd
26.1. Before it, `bd35b2c` was released on 2026-11-17 as the pre-release
`weishaupt-0.3.0` (tag on `bd35b2c`): an English archive and a French one
(`weishaupt-ebusd-config-0.3.0-fr`), made by `scripts/release.sh 0.3.0`. Both downloaded again
after publication: checksums right, 586 messages without error in the official ebusd 26.1.
`weishaupt-0.2.0` was deleted from the fork afterwards on the owner's request, with its tag (kept in the local clone).

**Comments corrected on 2026-11-17 (evening).** After the reading of the vendor manuals
(`evidence/terms.md`, "Findings") and on the owner's word: `BlockingTime` in lot A (one new
commit, `66b775e`) and the info code of `BurnerServiceHours` in lot E (one new commit,
`3e9347f`); the lots above were replayed. Pushed the same evening on the owner's word:
`weishaupt-pr` fast-forward (pull request #717 now has 14 commits), lots E to H forced (no
pull request on them). Then, on the owner's word again: `weishaupt-L` pushed as a new branch
at `d44fa6f` and the integration branch forced to `b66a563` (`41f39df` before), the pair
`scripts/check.sh` passed with the stack A to H plus L. On the fork the integration branch
now holds the two corrections and `src/fr.yaml`; no release was made. Later the same
evening, on the owner's word: `weishaupt-J` pushed as a new branch (`9e8cdd3`), `weishaupt-L`
replayed onto it and forced (`2d9c28b`), the integration branch forced to `bd35b2c`; local and
fork heads compared after the push, equal.

### Releases online

| Repository | Release | Content |
|---|---|---|
| `aghulas/ebusd-configuration` | `weishaupt-0.3.1` (pre-release) | the same definitions as 0.3.0 (English CSV identical); French archive with the wording decided by the owner on 2026-11-18, Wolf messages of the broadcast file in English. Downloaded again after publication: checksums right, 586 messages without error in the official ebusd 26.1. |
| `aghulas/ebusd-configuration` | `weishaupt-0.3.0` (pre-release) | compiled CSV of lots A to H and J under `kromschroeder/`, in an English and a French archive, notice, checksums. Downloaded again after publication: checksums right, 586 messages without error in the official ebusd 26.1. |
| `aghulas/ebus-typespec` | `v0.31.0-weishaupt.1` (pre-release) | library package with `@crc` / `@wcrc`, the one the integration branch pins |
| `aghulas/ebusd` | `v26.1-weishaupt.1` | static ebusd with the run-time checksum, the one `scripts/check.sh` uses |

Releases 0.1.0, 0.1.1 and 0.1.2 were deleted from the fork on the owner's request; their tags
remain in the local clone.

### Open pull requests

| Pull request | Head | State on 2026-11-17 |
|---|---|---|
| john30/ebusd-configuration#717 (lot A) | `aghulas:weishaupt-pr` `66b775e` (since 2026-11-17 evening: comment of `BlockingTime`; `813ac45` before) | open, mergeable, no review. Only the owner's two comments (2026-11-16, 2026-11-17). Description updated on 2026-11-17 (boiler status messages, section "File names"). |
| john30/ebusd#1825 (run-time checksum) | `aghulas:crc` `492867d9` | open, mergeable, no review, no comment |
| john30/ebus-typespec#8 (lot B) | `aghulas:wcrc-decorator` `75c7d58` | opened on 2026-11-17, mergeable, no review, no comment |

Comments posted on 2026-11-17, no answer yet: john30/ebusd-configuration#616 (points another
contributor working on Weishaupt files to #717) and john30/ebusd#1814 (this installation as a
data point on arbitration with room units).

## Open

### Needs the owner

- **GitHub support request** to remove the former commits (see "Commit identity"): text ready in
  `out/github-support-request.md` (not versioned), to send from the owner's account.
- **Is `50` the system manager?** It has the software version of `15` and answered every
  register read on both with the same value. How many heating modules are physically installed
  settles it; if two, `50` is the direct circuit of the system manager and `50.w.em1` should say
  so (eight reads of lot G duplicate `15`).
- **Which copy of a setting the regulation uses.** A room unit and its heating module answer the
  same setting registers with different values. Test: change the normal room setpoint by 0.5 K
  on the display of a room unit, both copies read before and after. If only the room unit's copy
  is in use, the seven settings lot C writes on `51` have no effect and must be removed or
  flagged.
- **Languages other than English.** French is pushed and released (`docs/i18n.md`, sections
  7 and 8): `src/fr.yaml` on `weishaupt-L`, French archive in `weishaupt-0.3.1` with the
  owner's decisions of 2026-11-18 on the wording. Still unread by the owner in
  `evidence/terms.md`: the six comments of the fault counters, the spelling
  "anti-légionelle", the design choices and the findings on the English wording
  ("calorifier").
- **Publishing** anything (release, pull request, comment) and pushing to a branch behind a pull
  request (rule 8).

### Needs the maintainer

- A review of #717, #1825, #8. The pull requests for E, D, F, C, G, H wait for #717; C also
  waits for #1825 and #8, then a released library and the version pin of ebusd-configuration.
- What identification Wolf devices answer to the scan (asked in the description of #717). If it
  is `W` as for these devices, the file names do not tell them apart.
- Whether new messages in `src/wolf` need `de.yaml` entries.

### Can be done now (reads only)

- **Heating copy of the first and second circuit.** Programs outside the room units were read
  on 2026-11-17 (`modules-programs`): the third circuit follows its room unit, not its module.
  For the other two, read room setpoint (`12 00`) and flow setpoint (`04 00`) on a Tuesday
  between 22:05 and 22:25, when the room units are still in program 1 and the programs of
  `50` and `51` are over.
- **Program selector `12 01`.** 11 = heating program 1 is proven on the room units; 12 and 13
  are not. Needs a room unit its operator has set to another program, then reads around a
  switch time where that program differs from program 1 (a Wednesday between 06:00 and 18:00).
- **`50` and `f6`.** Same program slots and values as the system manager, except `12 01`, which
  changes at every read there. One device with three roles fits; not proven by reads.
- **Lot H, comments (owner's decision of 2026-11-17: keep and comment).** Commit `0784552` on
  `weishaupt-H` says in the 126 comments that the hot-water and circulation programs are
  stored in the room unit; `scripts/check.sh` clean, 574 messages. The integration branch was
  rebuilt on it (`41f39df`). Both pushed to the fork on 2026-11-17 on the owner's word
  (`weishaupt-H` fast-forward, `weishaupt` forced, no pull request on either). The release
  Released since in `weishaupt-0.3.0`.
- **Lot J, fault counters (written on 2026-11-17, `evidence/bc-fault-counters.md`).** Local
  branch `weishaupt-J` `9e8cdd3`, in `STACK` below `weishaupt-L`, which was rebased onto it and
  holds the French of its 39 comment strings (`2d9c28b`). All three pushed to the fork
  on 2026-11-17 (see "Current state"); no pull request, no release. Open on the bus: the six
  12-byte reads have not been sent through ebusd (the values come from 2-byte reads of the same
  addresses); no counter has been seen to step with a new entry of the fault history, which
  would also say whether a number listed as warning and fault (15, 18, 21, 48, 57) counts
  warnings, lockouts or both.
- **Lot F, what was left out**: 23 of the 30 data-logger channels, the output bits (RAM `2b`),
  and `Load` before the flame (reads 23 to 40 while the status says 0 %).
- **Info values of the service tool** readable through `50 22`; only the hours since last
  service are in a lot.
- Other entries of `docs/discoveries.md` and the "Not verified" sections of `evidence/`.

### Blocked on something else

- **Settings left out of lot C** (list in `evidence/settings-writes.md`, "Left out"): each needs
  a write from source `ff` captured and read back, which is the operator's to do (rule 7).
- **Writes sent from the files of the lots**: the one write test done (`BlockingTime`, see
  below) was built by the running configuration of the installation, not by lot C.
- `FloorDryingTemp`, `RoomThermostatTemp`: typed as one-byte temperatures on 16-bit registers in
  the first version of #717; in no lot, need a read.

## Conventions

- **Stack and integration.** One branch per lot, `weishaupt-<letter>`, each on the previous one.
  After a change in a lot, replay the lots above it (`git rebase --onto`, without
  `--update-refs` if backup branches point into the range: it moves them too), then
  `scripts/integrate.sh`: it checks that the stack is linear, sets `weishaupt` to its top in the
  worktree `out/integration`, adds the pin commit with fixed dates and runs the full check.
  `INTEGRATION=<name> scripts/integrate.sh` does the same on a trial branch and leaves
  `weishaupt` alone. The integration branch is never edited by hand.
- **Check.** `scripts/check.sh`: commit hygiene (identity, no tool trailer or name, no site data
  in added lines), file types, format, compile, `ebusd --checkconfig` in Docker with the ebusd
  release of the fork (checksum verified), translation files (keys against the comment strings,
  compile per language, only comments differ, same message count). `scripts/check.sh hygiene` runs the first step alone.
  `CFG_REPO=<absolute path>` checks another worktree. Lots C, G and H compile only with the
  library package of the fork: in a worktree, plain `npm install`, then
  `npm install --no-save` of that package and `@typespec/compiler@1.17.0`; never commit
  `package.json`.
- **Local clone.** `repos/ebusd-configuration` stays on `weishaupt-F` with an old toolchain
  (library 0.26) and an untracked `package-lock.json`; lots A, E, D, F compile there. Work on
  another lot in a separate git worktree. Only one session at a time edits this clone.
- **File names.** `ZZ.w.<circuit>.tsp`: slave address, the identification the devices answer
  to the scan (`W`), circuit. ebusd loads one file per scanned slave address, the best match on
  the identification, and the longer name between equal matches; a name without identification
  would replace the Wolf files of the same address (`08..hc`, `50..mc`). ebusd loads no file for
  a master address: messages sent to a master go into the file of its slave address with
  explicit `@qq` / `@zz`. Imports in `src/main.tsp` are added by hand, sorted (`npm run maintsp`
  rewrites unrelated lines).
- **Translations.** A comment changed or added in a lot needs its key in `src/fr.yaml` on
  `weishaupt-L`: rebase that branch onto the new top of the stack, write the patterned entries
  again (`scripts/i18n-patterns.py`), add the others from `evidence/terms.md` (a term without a
  row gets one first), and let `scripts/check.sh` say what is missing or left over. Worktree of
  the branch: `out/lot-L`.
- **Release.** `scripts/release.sh <version>` rebuilds and checks the integration branch and
  makes the archives under `out/release/`, English and one per language of `RELEASE_LANGS`
  (default `fr`), with the notice from `docs/release-readme.md`. Then, on
  the owner's word: push `weishaupt`, tag `weishaupt-<version>`, release, download it again and
  load it in the official ebusd.
- **Writes use source `ff`.** Most settings are acknowledged from any master but taken over only
  from `ff`, the address of the vendor service tool. The definitions set no `@qq`; the caller
  passes `-s ff`. Nothing is written while the service tool is connected.
- **Commit identity.** All repositories are configured with the GitHub noreply address of the
  account; `scripts/check.sh` expects it. No mention of AI tools anywhere (rule 9).
- **Toolchain.** Node.js LTS major pinned in `.nvmrc`. Upstream ebusd-configuration pins the
  library `~0.29` with compiler `~1.12` and does not compile from a fresh install (reported
  upstream in #727 and #674); the lots give identical CSV with 0.26, 0.29 and 0.31. On Windows
  the fork's symlinks need Developer Mode and `core.symlinks true`.
- The default branch of `ebus-typespec` is `main`; the two other upstreams use `master`.
- Notes of sessions with the vendor service tool go to branch `service-tool` of this
  repository, file `evidence/service-tool-log.md`; protocol in `docs/service-tool-protocol.md`.

## Decisions and history

Dated, newest first. Commit ids quoted in `evidence/` and in older texts are those of their
date; see 2026-11-17 "Commit identity".

- **2026-11-17, commit identity.** Every commit of the owner in the four repositories was
  rewritten to the noreply address (metadata only; the tree of every branch and tag compared
  before and after, identical) and pushed again, the branches of #717 and #1825 included;
  release tags moved with their commits, assets unchanged. All commit ids changed. The former
  commits stay reachable on GitHub by id and through the force-push events of the pull requests
  until GitHub support removes them. Earlier the same day and on 2026-11-16, tool trailers and
  another identity had been removed from messages and metadata the same way.
- **2026-11-17, write test.** On the operator's decision, `BlockingTime` of the system manager
  was written 1 → 2 → 1 from source `ff`: telegrams `cc 25 00 02 00` and `28 25 00 01 00`
  acknowledged and read back (`evidence/register-write-crc.md`, section 6). The only write this
  project has sent.
- **2026-11-17, tests by reads.** With the `hex` command of ebusd (`50 22` and `50 00` only):
  `SystemHour` read and put back into lot A; the two multi-item requests of lot F answered by
  both boilers; the second boiler captured while firing.
- **2026-11-17, file names and the scan.** `10..bc1` / `10..bc2` were never loaded with
  `--scanconfig` (master address), and `50..em1` / `08..bc1` took the place of the Wolf files.
  Corrected in lot A (two commits) and replayed through the stack: boiler status messages
  `Boiler1Status`, `Boiler1Power`, `Boiler2Status`, `Boiler2Power` in `15.w.ka`; files named with
  the identification. Checked in ebusd without a bus with injected scan answers.
- **2026-11-17, `@wcrc`.** The decorator first emitted `00` in place of the checksum, also on
  the read line of a read / write setting; it now emits the checksum of the address.
- **2026-11-17, lot C decisions.** No `@qq` in the definitions (see "Writes use source `ff`").
  `35.w.fs1` stays in the lot. Lot C was restacked from lot A onto lot F so that the stack is
  linear.
- **2026-11-17, lot A.** `SupplyWTCTemp` renamed `DeCoupleTemp` (it is the de-couple sensor
  B22); registers 3, 13, 14 of the system manager read as signed.
- **2026-11-16, #717 retargeted.** The first version (11 300 lines, a new manufacturer,
  decorators in JavaScript, writes, the raw memory map) was replaced by lot A: it extends
  `src/wolf` because the devices scan as manufacturer `0x50` Kromschröder, which upstream
  already has (`src/kromschroeder` is a symlink to `src/wolf`). The old version survives only
  on the local branch `backup/weishaupt-pr-717-big`. The note `docs/maintainer-note-crc.md` is
  superseded by the description of #717.
- **2026-11-16, register checksum.** Upstream's `src/wolf` reads send `00` as first ID byte; the
  bus shows a CRC-8 (polynomial 0x5C) over the address (`evidence/register-crc.md`). Stated in
  the description of #717.
- **2026-11-16, service tool sessions.** The memory-read grammar `50 00`, the fault history and
  the counters were established from the telegrams of the vendor service tool
  (`evidence/service-tool-log.md`); they made lots E, D and F possible.
- **Not on this installation:** `FsStatus` (`50 10`) never appears; the heating circuits use
  `HcMode` (`50 14`).

Local branches kept as backups in the clone: `backup/pre-rename-*` (lots before the renaming),
`backup/weishaupt-C-on-A`, `backup/weishaupt-pr-717-big`; local tags `weishaupt-0.1.0` to
`0.1.2`. They carry the rewritten identity; none is on the fork.
