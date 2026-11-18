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
| E | Fault log of the system (`50.w.em1`), hours since last service and fault history of both boiler automats, first use of the memory read `50 00` (`08.w.bc1`, `18.w.bc2`); the first answer byte of every memory read is kept as the field `FirstByte` through the shared base `memr`. Hours since last service (`BurnerServiceHours`, i46) now carries the ×10 factor and is defined on both boilers (fix of 2026-11-18). | `weishaupt-E` `3b4d19c` (4 commits on A), pushed (0.4.1) | `em1-fault-log`, `bc-fault-history`, `bc-counters` |
| D | Counters of both automats: operating hours, burner hours, burner starts. Not the whole memory map. | `weishaupt-D` `5fb13ab` (1 commit on E), pushed (0.4.1) | `bc-counters` |
| F | Live values of both automats from RAM / XRAM: `Temperatures` (return, flue gas, flow, outside), `Operation` (load, ionisation, pump speed). | `weishaupt-F` `2933941` (2 commits on D), pushed (0.4.1) | `bc-live-values` |
| C | 17 settings read and written (`50 23`, checksum computed by ebusd at run time, decorator `@wcrc`): 8 on the system manager, 7 on heating module `51`, 2 on room unit `35`. | `weishaupt-C` `fb15d2b` (5 commits on F), pushed (0.4.1) | `register-write-crc`, `settings-writes` |
| G | Reads of the heating-circuit values and settings on the three room units (new files `75.w.fs2`, `f5.w.fs3`) and the three heating modules. A comment in `50.w.em1` now says `50` is the system manager's own direct circuit (same device as `15`), not a WCM-EM module like `51`/`52`, so its eight reads duplicate `15` (2026-11-18). | `weishaupt-G` `5c6e592` (2 commits on C), pushed (0.4.1) | `room-units-reads`, `heating-modules-reads` |
| H | Weekly programs of the three room units, read side: heating programs 1 to 3, then hot water and circulation in a second commit that can be dropped alone. 315 messages. | `weishaupt-H` `9778221` (3 commits on G), pushed (0.4.1) | `room-units-programs` |
| J | Fault counters of both automats: one counter per fault number (33, numbers 11 to 57), seven memory reads of at most 10 bytes of EEPROM `0x0196`–`0x01d7` per boiler, with the first answer byte kept as a field through the shared base `memr` (as every memory read since 2026-11-18), 14 messages. Address and number from the symbol table of the firmware, meaning from the manual of the boiler (48 as a warning and 49 only in its 2020 edition). | `weishaupt-J` `64a0daa` (1 commit on H), pushed (0.4.1) | `bc-fault-counters` |
| K | Boiler information values read with `50 22` (the WTC display "i" codes) on both boilers (`08`, `18`): five temperatures — flow i35, return i37, flue gas i31, outside i33, hot water i34 — plus (0.4.2 prep) the hydraulic-separator temperature i39 (`86 02`, no sensor here), and the two software versions i44 WCM-CPU and i45 WCM-CUI (`99 01` / `9a 01`, kept as the raw bytes `11 04` = scan `SW=1104`). Reuses the precomputed-CRC register base and the `SIN`/10 scalar. 16 messages. Reads only, stock ebusd. An unidentified per-boiler counter at `27 02` (731/543) is left out as a finding. | `weishaupt-K` `49e484b` (2 commits on J), pushed (0.4.2) | `bc-info-values` |
| L | French translation of the comments: `src/fr.yaml`, 277 keys for the 277 comment strings of the lots (vendor terms and owner-accepted wording; none provisional; the three 0.4.2 info-value strings accepted by the owner on 2026-11-18); the 24 Wolf comments of `wolf/broadcast` stay in English. No definition; no upstream pull request is cut from it. | `weishaupt-L` `b4cfa16` (8 commits on K), pushed (0.4.2) | `terms` |
| M | Metadata sidecar `metadata/weishaupt.toml`: devices, menu tree per device type, short labels in English and French, kind of value, polling class, write conditions and evidence record of every message of the lots (107 entries for 528 messages, the families by pattern). No definition; no upstream pull request is cut from it. Menu trees and labels **accepted by the owner on 2026-11-18** as proposed (`out/companion-menu-proposal.md`); default polling class by kind since. | `weishaupt-M` `b9d5359` (2 commits on L); `4d1ce1c` is on the fork, the second commit is **local, to push as a fast-forward** | the records the entries name; `service-tool-log` for the polling classes |
| I | Weekly programs of the devices other than the room units (`15`, `50`, `f6`, `51`, `52`): examined on 2026-11-17, **nothing defined**. `15`, `50` and `f6` answer identical bytes on all 105 slots; `51` and `52` hold the heating programs of `15` and the hot-water and circulation programs of the room units. Hot water follows the program of the system manager, which lot A already defines at `50`; the third heating circuit follows its room unit (lot H) and its module does not apply its own programs. The rest would be schedules the installation does not follow, or a copy of lots A and H. | none, no branch | `modules-programs` |
| B | Library: decorators `@crc` (checksum computed when emitting) and `@wcrc` (marker for the run-time checksum; the byte emitted is the checksum of the address, so reads stay valid on a stock ebusd). | `aghulas/ebus-typespec`, `wcrc-decorator` `75c7d58`. **Pull request #8.** | `register-write-crc` section 5 |
| — | ebusd: checksum computed at run time for messages marked `[WCRC]`. | `aghulas/ebusd`, `crc` `492867d9`. **Pull request #1825.** | `register-write-crc` |

The lot letters are historical; the stack order is A, E, D, F, C, G, H, J, K, L, M (`STACK` in
`scripts/integrate.sh`). `weishaupt-L` (translation files) and `weishaupt-M` (metadata sidecar)
hold no definition and stay on top, in this order: a new lot goes below them (lot K was
inserted between J and L this way on 2026-11-18), then L and M are rebased and the sidecar
gets its entries. Lot C needs lot B to compile and #1825 to send. For a pull request
upstream, C, G and H are cut again on lot A.

**0.4.2 released (2026-11-18)** from `weishaupt` `f58a45f` (605 messages): 0.4.1 plus three boiler information values in lot K (see "Decisions and history"). **0.4.1 released (2026-11-18).** On top of 0.4.0: lot K (the
five boiler information-value `50 22` reads on both boilers), the lot-E fix of `BurnerServiceHours`
(×10 factor, now on both boilers), and the lot-G comment that `50` is the system manager's own
direct circuit. The whole stack E→L was rebuilt (new hashes in the table above; A unchanged at
`66b775e`); the ten lot branches and `weishaupt` `5298e90` were force-pushed on the owner's
word and released as `weishaupt-0.4.1` (tag on `5298e90`). The integration `weishaupt-next` `5298e90` and `weishaupt` `5298e90`
pass `scripts/check.sh`: **599 messages** in English, German and French (588 before), `src/fr.yaml`
274 keys for 274 strings (the lot-K "valeur d'information" wording accepted by the owner on
2026-11-18, none provisional). Archives built by `scripts/release.sh 0.4.1` and published as
`weishaupt-0.4.1` (two archives and `sha256sums.txt`); downloaded again after publication:
checksums right, 599 messages without error in the official ebusd 26.1. CSV diff
vs 0.4.0: only `08.w.bc1.csv` (+5 reads, `BurnerServiceHours` divisor → −10) and `18.w.bc2.csv`
(+6: `BurnerServiceHours` and the five reads) change; +11 messages, no other message altered.

Integration branch of 0.4.0: `weishaupt` was `de42c7c`, the stack A to H, J and L plus the pin
commit, on the fork since 2026-11-18 (forced from `4c034fc` on the owner's word, the eight lot
branches forced with it). The local `weishaupt` now points at the 0.4.1 integration `5298e90`
(above); the online release and its tag `weishaupt-0.4.0` still rest on `de42c7c`. `scripts/check.sh` on it: clean, **588 messages** in English, German and
French. Released from it on 2026-11-18 as the pre-release `weishaupt-0.4.0` (tag on
`de42c7c`), made by `scripts/release.sh 0.4.0`: the first answer byte of every memory read
(`50 00`) kept as the field `FirstByte` on lots E, D and F as well as J, with a line on it in
the notice. The two archives and the `sha256sums.txt` downloaded again after publication:
checksums right, 588 messages without error in the official ebusd 26.1. Before it,
`weishaupt-0.3.2` (tag on `4c034fc`, the first answer byte on lot J only) was released the
same day and stays online. `weishaupt-0.3.1` (tag on `b831213`, 586
messages, lot J as six 12-byte reads, of which an all-zero answer is lost most of the time)
was deleted from the fork on 2026-11-18 on the owner's request once superseded, its tag kept
in the local clone. Before that, `b831213` was the integration branch since 2026-11-18 (forced from `bd35b2c` on the owner's word, with `weishaupt-L`
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
`weishaupt-0.2.0`, `weishaupt-0.3.0`, `weishaupt-0.3.1`, `weishaupt-0.3.2`, `weishaupt-0.4.0` and `weishaupt-0.4.1` were deleted from the fork on the owner's request once superseded, with their tags (kept in the local clone); `weishaupt-0.4.2` is the only release online.

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
| `aghulas/ebusd-configuration` | `weishaupt-0.4.2` (pre-release) | as 0.4.1, plus three boiler information values on both boilers: hydraulic separator temperature i39, software versions i44 and i45. Downloaded again after publication: three assets, checksums right, 605 messages without error in the official ebusd 26.1. |
| `aghulas/ebus-typespec` | `v0.31.0-weishaupt.1` (pre-release) | library package with `@crc` / `@wcrc`, the one the integration branch pins |
| `aghulas/ebusd` | `v26.1-weishaupt.1` | static ebusd with the run-time checksum, the one `scripts/check.sh` uses |

Releases 0.1.0, 0.1.1, 0.1.2, 0.2.0 and 0.3.0 were deleted from the fork on the owner's request; their tags
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

- **Release carrying the metadata asset.** The menu trees and labels are accepted
  (2026-11-18); what remains is to publish. Local and waiting for the owner's word: the
  second commit of `weishaupt-M` (`b9d5359`, fast-forward of the branch on the fork) and the
  workbench commit that goes with it; then `scripts/release.sh 0.4.3` once more, push of
  `weishaupt`, tag `weishaupt-0.4.3`, release with five files: the two archives,
  `weishaupt-metadata-0.4.3.json`, `weishaupt-fixtures-0.4.3.json`, `sha256sums-0.4.3.txt`
  (the CSV are those of 0.4.2).

- **GitHub support request** to remove the former commits (see "Commit identity"): text ready in
  `out/github-support-request.md` (not versioned), to send from the owner's account.
- **Is `50` the system manager?** *Settled (owner, 2026-11-18): yes.* Two WCM-EM modules are
  installed (`51`, `52`), so `50` is the system manager's own direct heating circuit, the same
  device as `15`, and its eight lot-G reads duplicate `15`. `50.w.em1` (lot G) now says so and
  `evidence/heating-modules-reads.md` records the fact.
- **Which copy of a setting the regulation uses.** A room unit and its heating module answer the
  same setting registers with different values. Test: change the normal room setpoint by 0.5 K
  on the display of a room unit, both copies read before and after. If only the room unit's copy
  is in use, the seven settings lot C writes on `51` have no effect and must be removed or
  flagged.
- **Languages other than English.** French is pushed and released (`docs/i18n.md`, sections
  7 and 8): `src/fr.yaml` on `weishaupt-L`, French archive in `weishaupt-0.3.2` with the
  owner's decisions of 2026-11-18 on the wording, the fault-counter comments included
  (accepted 2026-11-18). Still unread by the owner in `evidence/terms.md`: the spelling
  "anti-légionelle", the design choices and the findings on the English wording
  ("calorifier").
- **Force-push the rebuilt lots and the breaking release (`FirstByte` on E, D, F).** Done on
  2026-11-18 on the owner's word: the eight lot branches and `weishaupt` (`de42c7c`)
  force-pushed, released as `weishaupt-0.4.0`. Earlier the same day a session had force-pushed
  and published this on its own user instruction before the main session's review; it was
  rolled back on the owner's word and redone cleanly from the main session, with the
  `sha256sums.txt` asset the first attempt lacked.
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
  on 2026-11-17 (see "Current state"); no pull request, no release. The six requests were
  sent as written to both boilers on 2026-11-18 (`hex`, read-only): 11 of the 12 are answered
  at every attempt, with the values of the 2-byte reads. `FaultCounters4` of the first boiler,
  whose six counters are zero, was answered 3 times out of 12: a 12-byte answer of zero bytes
  only is lost most of the time (6 answered of 20 over three addresses), 10 bytes of zeros
  never (19 answered of 19). The owner chose seven reads of at
  most 10 bytes, as the vendor tool does, sent as written the same morning: all answered on
  both boilers, all-zero blocks included. Second finding: 2 of 107 answers of the first boiler
  have the number of bytes asked for as first byte and all data at zero. On the owner's
  decision the lot keeps that byte as a field (`FirstByte`). **Pushed and released on 2026-11-18, on the
  owner's word:** `weishaupt-J` `78ac7af` (amended) and `weishaupt-L` `d5a88bd` (rebased, 269
  keys) forced, `weishaupt` rebuilt and forced to `4c034fc`; `scripts/check.sh` clean, 588
  messages in English and French; release `weishaupt-0.3.2` made from it. The eight French strings of the lot (seven
  message comments, first answer byte) were put to the owner on 2026-11-18 and accepted, so
  no lot has a provisional string left. Still open: no counter has been
  seen to step with a new entry of the fault history, which would also say whether a number
  listed as warning and fault (15, 18, 21, 48, 57) counts warnings, lockouts or both.
- **First answer byte of the memory reads of lots E, D and F — done 2026-11-18, local.** The
  field was folded into the shared base model `memr` (`memrf` dropped, lot J re-inherits
  `memr`), so every memory read of lots E, D, F and J now carries the field `FirstByte` (see
  the history entry below and `evidence/bc-fault-counters.md`). Still open: observe how often
  an answer without data occurs over a longer time, and whether the second boiler sends one.
- **Lot F, what was left out**: 23 of the 30 data-logger channels, the output bits (RAM `2b`),
  and `Load` before the flame (reads 23 to 40 while the status says 0 %).
- **Info values of the service tool** readable through `50 22`: the five temperatures (i35,
  i37, i31, i33, i34), the hydraulic-separator temperature (i39), and the two software versions
  (i44 WCM-CPU, i45 WCM-CUI) are now lot K on both boilers; the hours since last service (i46)
  are in lot E. Still out: the values that need the burner firing (i11 power, i22 pump, i23
  fan, i32 ionisation, i30 eSTB, i42 burner starts) — a capture while a boiler fires (operator).
  Burner operating hours (i43, `2a 02`) were left out of lot K as a duplicate of lot D's EEPROM
  counter; the per-boiler counter at `27 02` (731/543) matches no `i` code and stays a finding
  (`evidence/bc-info-values.md`).
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
  compile per language, only comments differ, same message count), metadata (every message of
  the lot files against the sidecar; skipped on a branch below `weishaupt-M`, required on the
  integration branch). `scripts/check.sh hygiene` runs the first step alone.
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
- **Metadata.** What a user interface needs beyond the CSV is in `metadata/weishaupt.toml` on
  `weishaupt-M` (worktree `out/lot-M`), never in the lots and never in this repository. A
  message added, renamed or removed in a lot needs its entry there: rebase `weishaupt-M` onto
  the new top, and let step 7 of `scripts/check.sh` (`scripts/metadata.py check`) say what is
  missing or left over. A setting is marked written only when a lot writes it and an evidence
  record names it; a polling class, a range or a step that no record establishes stays empty.
  Format of the generated file: `docs/companion-contract.md`.
- **Versions (definitions and companion).** Names are the interface: an entity of the
  companion is identified by circuit, message and field.
  1. Until 1.0 the **second** number of a definitions release changes for a breaking change:
     a message or a field renamed, removed, retyped, or a field inserted before others (as
     `FirstByte` was in 0.4.0), or the `schema` number of the metadata raised. The **third**
     changes for a compatible one: messages or trailing fields added, comments, translations,
     labels, menus, metadata values. A rename carries `renamed_from` in the sidecar.
  2. The metadata has its own `schema` number (1), raised only when its structure changes.
     While `status` says `proposed`, menu ids and labels may still change without notice;
     the keys never do outside a breaking release.
  3. Every release from 0.4.3 on carries `weishaupt-metadata-<version>.json`, generated from
     the same commit as the archives. A release without it is not complete.
  4. A companion release has its own numbers. It names the definitions release it embeds and
     the range it accepts (for example `>= 0.4.3, < 0.5`) in its README and its diagnostics;
     a new definitions release does not force a companion release.
  5. At run time the companion never trusts the range alone: it compares, message by
     message, with what ebusd loaded, since ebusd cannot tell which release it runs.
- **Release.** `scripts/release.sh <version>` rebuilds and checks the integration branch and
  makes the archives under `out/release/`, English and one per language of `RELEASE_LANGS`
  (default `fr`), with the notice from `docs/release-readme.md`, then the metadata file, the
  fixtures file (`evidence/fixtures.toml`) and `sha256sums-<version>.txt` for all of them.
  Then, on
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

- **2026-11-18, companion repository cleaned.** `aghulas/ha-weishaupt`, the separate
  Home Assistant project, had its history rewritten on the owner's decision (identity, tool
  mentions, site-specific content through every file version; then English code and
  translations on the owner's request) and `main` and `v0.1.0` force-pushed from the main
  session at 08:46 UTC, 29 tests passing. Its former commits stay reachable on GitHub by id
  until the purge is asked; the addition to the request is in the cleanup note under `out/`.
- **2026-11-18, menu trees and labels of the metadata accepted.** The owner accepted the
  proposal as written, with the recommendation on each of its seven questions. In the sidecar
  (`weishaupt-M` `b9d5359`, a second commit, so the branch on the fork moves by a
  fast-forward): `status` says `accepted` with the date, and a table `[poll_default]` gives a
  polling class by kind to the messages no record classes — live values cyclic, settings,
  program slots and diagnostics on demand. The metadata file tells the two apart
  (`poll_basis`: `record` for 45 messages, `default` for 473, `passive` for 8); counters and
  states have no default, so `BurnerServiceHours` of both boilers stays without a class.
  Nothing else changed: placements, risk classes (2 comfort, 15 regulation) and labels are
  those proposed. Left for phase 1, as recommended: French labels of the 43 value-list
  entries, intervals. The French labels without a vendor source are recorded as `owner`
  terms in `evidence/terms.md` ("Short labels of the metadata"); the release notice has a
  section on the three files beside the archives. Trial again,
  `INTEGRATION=weishaupt-next scripts/release.sh 0.4.3`: `weishaupt-next` `0eb6d16`,
  `scripts/check.sh` clean in seven steps, 605 messages in English, German and French, CSV of
  both archives byte-identical to 0.4.2. Local only; local `weishaupt` still `f58a45f`.
- **2026-11-18, companion contract (phase 0 of the Home Assistant companion).** Pushed the
  same day on the owner's word (`weishaupt-M`, workbench), no release carries the asset yet. The
  owner decided on 2026-11-18 that a generated metadata file is part of every definitions
  release and that its source lives on a branch on top of the stack. Built:
  - **Sidecar** `metadata/weishaupt.toml` on the new branch `weishaupt-M` (`4d1ce1c`, one
    commit on `weishaupt-L`), in `STACK`. TOML: read by the standard library of Python, with
    comments, and a repeated key is a parse error. An entry is keyed by circuit and message
    name, or by a pattern with the number of messages it must match per circuit; 107 entries
    cover the 528 messages of the lot files (545 CSV lines: the 17 written settings have a
    read and a write line; ebusd counts 605 with the files of the official configuration
    the archive also holds, which have no metadata).
  - **Generator and check** `scripts/metadata.py`, step 7 of `scripts/check.sh`;
    `scripts/release.sh` writes `weishaupt-metadata-<version>.json`,
    `weishaupt-fixtures-<version>.json` and `sha256sums-<version>.txt` beside the archives.
  - **Content.** By kind: 357 program slots, 65 settings, 44 live values, 37 diagnostics,
    18 counters, 7 states. Written: the 17 settings of lot C, each with the source address of
    the captured write (`ff` for 15, `31` for the two flow limits of `51`), a risk class
    (2 comfort, 15 regulation), a level of proof (`change-observed` for `BlockingTime`,
    `captured` for the others) and, on the seven of `51`, the open question of which copy
    the regulation uses.
  - **Left empty for lack of a record.** Polling class of 475 messages (set for 53: 8
    passive, 11 polled and 34 read on demand by the vendor tool, `service-tool-log`); no
    interval anywhere; range of `RoomSetbackTemp` and `GradientCurve` of `51`; step of these
    two and of `BlockingTime`, `ChangeOverTime`, `SwitchOnRuntime`; linked bounds; French
    labels of the 43 value-list entries.
  - **Menu trees and labels**: proposal in `out/companion-menu-proposal.md` (not versioned),
    from the menus of the three vendor manuals and the tabs of the vendor tool; marked
    `proposed` in the sidecar until the owner accepts them.
  - **Fixtures** (`evidence/fixtures.toml`): the 17 settings of `settings-writes`, each with
    its read ID, answer, write telegram and decoded value, checked against the record and
    the definition. The other records quote telegrams in prose; transcribing them is one
    reading per record, and checking the decoded values of multi-field messages needs an
    ebusd that decodes an injected answer, not prototyped yet.
  - **Trial.** `INTEGRATION=weishaupt-next scripts/release.sh 0.4.3`: stack linear,
    `weishaupt-next` `5442f91`, `scripts/check.sh` clean in seven steps, 605 messages in
    English, German and French; the CSV files of both archives are byte-identical to 0.4.2
    (`diff -r`, notice apart). Local `weishaupt` still at `f58a45f`; nothing pushed, nothing
    published.

- **2026-11-18, release 0.4.2.** Three more boiler
  information values read with `50 22`, added to lot K on both boilers (`08`, `18`), each
  confirmed read-only on the live bus and tied to the manual (83251704, menu *Info*, p. 47):
  - **i 39 hydraulic separator temperature** (`86 02`, SIN/10 °C like the other sensor reads);
    reads −40.0 (no sensor fitted) on both boilers here, defined so the read exists where the
    sensor is present, as i 33 / i 34 are.
  - **i 44 WCM-CPU software version** (`99 01`) and **i 45 WCM-CUI software version**
    (`9a 01`), kept as the raw two bytes (`HEX`, displayed `11 04`) because that equals the
    software version the bus scan reports for the boiler automat (`SW=1104`); a decimal `UIN`
    would read 1041 and not match. The two read the same `11 04` here, so the CPU/CUI split
    follows the register order (lot A) and the `i`-code order (manual).

  Left out as a finding: the per-boiler counter at `27 02` (731 / 543), which matches no
  *Info* `i` code (`evidence/bc-info-values.md`). Lot K `dec3adf` → `49e484b` (second
  commit); `weishaupt-L` rebased onto it and its info-value French commit amended with the
  three new keys (`935363b` → `b4cfa16`, 277 keys for 277 strings, none provisional, the three
  new strings accepted by the owner on 2026-11-18). Stack linear; `scripts/check.sh`
  clean on K (`49e484b`), L (`b4cfa16`) and the trial integration `weishaupt-next` (`f58a45f`):
  **605 messages** (599 before), English = German = French. CSV diff vs 0.4.1 (English): only `08.w.bc1.csv` and
  `18.w.bc2.csv` change, each +3 reads (i 39, i 44, i 45); +6 messages, no other message
  altered (French CSV: same lines, comments only). On the owner's word `weishaupt-K`,
  `weishaupt-L` and `weishaupt` (`f58a45f`) were pushed and `weishaupt-0.4.2` published from
  the main session (two archives and `sha256sums.txt`, rebuilt by `scripts/release.sh 0.4.2`
  just before); downloaded again: checksums right, 605 messages without error in the official
  ebusd 26.1. `weishaupt-0.4.1` was deleted the same day on the owner's request, its tag kept in the local clone.
- **2026-11-18, release 0.4.1.** Three changes on
  top of 0.4.0, each with evidence:
  - **Lot K (new, `weishaupt-K` `dec3adf`, inserted between J and L).** Five boiler information
    values read with `50 22` on both boilers (`08`, `18`): flow i35 (`0d 00`), return i37
    (`16 00`), flue gas i31 (`45 01`), outside i33 (`0c 00`), hot water i34 (`0e 00`), all
    `SIN`/10 °C, reusing the precomputed-CRC register base and the shared `otemp10` scalar
    (`i33` reuses the top-level `OutsideTemp` of lot A). Each CRC was reproduced offline and each
    value read read-only on both boilers (`evidence/bc-info-values.md`). Burner hours i43
    (`2a 02`) left out as a duplicate of lot D's EEPROM counter.
  - **Lot E fix (`weishaupt-E` `3b4d19c`).** `BurnerServiceHours` (i46, `bc 02`) now carries a
    ×10 factor (ebusd divisor −10): it read 44/39 instead of 440/390 h in 0.3.2 and 0.4.0 — 10×
    low. The read is now defined on the second boiler too. Folded into lot E's own commits; the
    stack above was rebuilt. (`evidence/bc-counters.md`.)
  - **Lot G clarification (`weishaupt-G` `5c6e592`).** A comment in `50.w.em1` now states that
    `50` is the system manager's own direct heating circuit (same device as `15`), not a WCM-EM
    module like `51`/`52` (two are installed), so its eight reads duplicate `15`. Confirmed by
    the owner. (`evidence/heating-modules-reads.md`.)
  - **French (lot L `935363b`).** Five new keys for the lot-K comments, provisional
    ("valeur d'information iNN", awaits the owner); 274 keys for 274 strings.

  The whole stack E→L was rebuilt (new hashes in the "Lots" table; A unchanged). Local
  `weishaupt` and trial `weishaupt-next` both `5298e90`; `scripts/check.sh` clean, 599 messages
  in English, German and French. Archives built by `scripts/release.sh 0.4.1` under
  `out/release/`. Backups of the 0.4.0 lot heads kept locally as `backup/pre041-*`. On the
  owner's word the ten lot branches and `weishaupt` (`5298e90`) were force-pushed and
  `weishaupt-0.4.1` published (three assets); downloaded again, checksums right, 599 messages
  without error in the official ebusd 26.1. The owner validated the "valeur d'information iNN"
  wording the same day, so no lot has a provisional French string left.
- **2026-11-18, first answer byte on lots E, D and F.** On the owner's decision the first byte
  of every memory read (`50 00`) is now a visible field `FirstByte` (UCH), as lot J already
  did. The field was folded into the shared base model `memr` (which no message outside E, D,
  F and J uses): `memrf` was dropped and lot J's fault counters re-inherit `memr`, behaviour
  identical. The field comment was generalised from the counter-specific "when all counters
  read 0" to "when the data read 0" and its French updated (`weishaupt-L`); no new provisional
  string. The change was folded into the commits that own the code — the memr field into lot
  E's fault-history commit, the `memrf` removal into lot J's commit — and lots D, F, C, G, H,
  J, L were rebased so the stack stays linear. `scripts/check.sh` clean on E (`20506af`),
  D (`193e2d5`), F (`d6f797f`) and on the trial integration `weishaupt-next` (`de42c7c`): 588
  messages in English, German and French, 269 French keys for 269 strings. Compared with the
  released CSV (`weishaupt` `4c034fc`), the field layout changed only in the 20 memory reads of
  E, D and F (`ign` → `firstbyte`, both boilers); the 14 fault-counter messages kept their
  field and only their comment changed; no other message changed and none gained or lost a
  field. One reading of each of E, D and F confirmed on the live bus read-only (`50 00` hex):
  `FirstByte` is `00`, the data decode as before. Pushed and released on 2026-11-18 as
  `weishaupt-0.4.0` (`weishaupt` `de42c7c`), with a `sha256sums.txt` asset; `weishaupt-0.3.2`
  stays online beside it. A session had first force-pushed and published this without the
  owner's go-ahead; it was rolled back on the owner's word and redone cleanly from the main
  session.
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
