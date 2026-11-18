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
| A | Register reads (`50 22`, checksum precomputed in the ID) of the system manager; status broadcast and the status each boiler sends to the cascade master; room unit / module exchange `HcMode`; system clock and the weekly hot-water and circulation programs of `50`. Reads only, stock ebusd. Files `15.w.ka`, `50.w.em1`, `51.w.em2`, `52.w.em3`, `broadcast`, `wtc_inc`. | `weishaupt-A` `4cd5a54` (16 commits), on the fork as `weishaupt-pr`, pushed on 2026-11-18 with its two last commits: `HcMode` without outside sensor, `DHWOperationMode` renamed `DHWLoadingPriority`. **Pull request #717.** | `ka-reads`, `register-crc`, `broadcast-kastatus`, `bc1-boiler-status`, `em-hcmode`, `em1-clock-program` |
| E | Fault log of the system (`50.w.em1`), hours since last service and fault history of both boiler automats, first use of the memory read `50 00` (`08.w.bc1`, `18.w.bc2`); the first answer byte of every memory read is kept as the field `FirstByte` through the shared base `memr`. Hours since last service (`BurnerServiceHours`, i46) now carries the ×10 factor and is defined on both boilers (fix of 2026-11-18). | `weishaupt-E` `9d20b57` (4 commits on A), pushed | `em1-fault-log`, `bc-fault-history`, `bc-counters` |
| D | Counters of both automats: operating hours, burner hours, burner starts. Not the whole memory map. | `weishaupt-D` `71094a2` (1 commit on E), pushed | `bc-counters` |
| F | Live values of both automats from RAM / XRAM: `Temperatures` (return, flue gas, flow, outside), `Operation` (load, ionisation, pump speed). | `weishaupt-F` `b0526d3` (2 commits on D), pushed | `bc-live-values` |
| C | 66 settings read and written (`50 23`, checksum computed by ebusd at run time, decorator `@wcrc`): 12 on the system manager, 7 on its direct circuit `50`, 7 on heating module `51`, 7 on heating module `52`, 11 on each of the room units `35`, `75` and `f5`. The 44 since 0.5.2 come from the captures on site of 2026-11-18 (batches 1 to 7). Three added on 2026-11-18 from the operator's log (`RegulationP`, `RegulationI`, `BoilerMCBoostTemp` of `fs1`; in 0.5.1), two the same day from the telegram log of ebusd (`RoomFrostProtectionTemp` of `fs1`, `GradientCurve` of `em3`). Each one seen changed, read back and restored on the bus. | `weishaupt-C` `c12ba91` (16 commits on F; 49 settings added from the captures on site of 2026-11-18, batches 1 to 7), pushed (0.5.4) | `register-write-crc`, `settings-writes` |
| G | Reads of the heating-circuit values and settings on the three room units (new files `75.w.fs2`, `f5.w.fs3`) and the three heating modules. A comment in `50.w.em1` now says `50` is the system manager's own direct circuit (same device as `15`), not a WCM-EM module like `51`/`52`, so its eight reads duplicate `15` (2026-11-18). | `weishaupt-G` `4a5798c` (2 commits on C; the reads of `fs1` frost protection and `em3` curve now in C), `4a5798c` (the reads of the written settings of the room units, `em1`, `em3` now in C), pushed | `room-units-reads`, `heating-modules-reads` |
| H | Weekly programs of the three room units, read side: heating programs 1 to 3, then hot water and circulation in a second commit that can be dropped alone. 315 messages. | `weishaupt-H` `e6c8f72` (3 commits on G), pushed | `room-units-programs` |
| J | Fault counters of both automats: one counter per fault number (33, numbers 11 to 57), seven memory reads of at most 10 bytes of EEPROM `0x0196`–`0x01d7` per boiler, with the first answer byte kept as a field through the shared base `memr` (as every memory read since 2026-11-18), 14 messages. Address and number from the symbol table of the firmware, meaning from the manual of the boiler (48 as a warning and 49 only in its 2020 edition). | `weishaupt-J` `f6bae02` (1 commit on H), pushed | `bc-fault-counters` |
| K | Boiler information values read with `50 22` (the WTC display "i" codes) on both boilers (`08`, `18`): five temperatures — flow i35, return i37, flue gas i31, outside i33, hot water i34 — plus (0.4.2 prep) the hydraulic-separator temperature i39 (`86 02`, no sensor here), and the two software versions i44 WCM-CPU and i45 WCM-CUI (`99 01` / `9a 01`, kept as the raw bytes `11 04` = scan `SW=1104`). Reuses the precomputed-CRC register base and the `SIN`/10 scalar. 16 messages. Reads only, stock ebusd. An unidentified per-boiler counter at `27 02` (731/543) is left out as a finding. | `weishaupt-K` `b5f0bd9` (2 commits on J), pushed | `bc-info-values` |
| L | French translation of the comments: `src/fr.yaml`, 277 keys for the 277 comment strings of the lots (vendor terms and owner-accepted wording; none provisional; the three 0.4.2 info-value strings accepted by the owner on 2026-11-18); the 24 Wolf comments of `wolf/broadcast` stay in English. No definition; no upstream pull request is cut from it. | `weishaupt-L` `0e6c0bc` (10 commits on K; no new string since 0.5.1), pushed | `terms` |
| M | Metadata sidecar `metadata/weishaupt.toml`: devices, menu tree per device type, short labels in English and French, kind of value, polling class, write conditions and evidence record of every message of the lots (107 entries for 528 messages, the families by pattern). No definition; no upstream pull request is cut from it. Menu trees and labels **accepted by the owner on 2026-11-18** as proposed (`out/companion-menu-proposal.md`); default polling class by kind since. | `weishaupt-M` (6 commits on L: the two of 0.4.3, the rename to `DHWLoadingPriority` with `renamed_from`, the labels of the 38 value-list entries in `[values]`, the metadata of the three settings of 0.5.1, then of two more with every written setting `change-observed`, then the eleven of `fs2` and of `fs3`, five of `em1`, six of `em3`, seven more of `fs1`, two of `ka`, the flow limits of `em1`), `27ffd95` (13 commits), pushed | the records the entries name; `service-tool-log` for the polling classes |
| I | Weekly programs of the devices other than the room units (`15`, `50`, `f6`, `51`, `52`): examined on 2026-11-17, **nothing defined**. `15`, `50` and `f6` answer identical bytes on all 105 slots; `51` and `52` hold the heating programs of `15` and the hot-water and circulation programs of the room units. Hot water follows the program of the system manager, which lot A already defines at `50`; the third heating circuit follows its room unit (lot H) and its module does not apply its own programs. The rest would be schedules the installation does not follow, or a copy of lots A and H. | none, no branch | `modules-programs` |
| B | Library: decorators `@crc` (checksum computed when emitting) and `@wcrc` (marker for the run-time checksum; the byte emitted is the checksum of the address, so reads stay valid on a stock ebusd). | `aghulas/ebus-typespec`, `wcrc-decorator` `75c7d58`. **Pull request #8.** | `register-write-crc` section 5 |
| — | ebusd: checksum computed at run time for messages marked `[WCRC]`. | `aghulas/ebusd`, `crc` `492867d9`. **Pull request #1825.** | `register-write-crc` |

The lot letters are historical; the stack order is A, E, D, F, C, G, H, J, K, L, M (`STACK` in
`scripts/integrate.sh`). `weishaupt-L` (translation files) and `weishaupt-M` (metadata sidecar)
hold no definition and stay on top, in this order: a new lot goes below them (lot K was
inserted between J and L this way on 2026-11-18), then L and M are rebased and the sidecar
gets its entries. Lot C needs lot B to compile and #1825 to send. For a pull request
upstream, C, G and H are cut again on lot A.

**0.5.4 released (2026-11-18)** from `weishaupt` `970143b`, on the owner's word: lot branches C to M and `weishaupt` forced with leases, five files published as a pre-release. 66 writable settings: the flow limits of `50.w.em1`, taken from `ff` only (batch 7 on site); the CSV differ from 0.5.3 only in `50.w.em1`. Downloaded again: the four checksums right, 662 messages without error in the official ebusd, both archives. The same day `ha-weishaupt` v0.1.3 was released (latest), which sends these two from `ff`.
**0.5.3 released (2026-11-18)** from `weishaupt` `e3ed65f`, on the owner's word: the seven lot branches C to M and `weishaupt` forced with leases, five files published as a pre-release. 64 writable settings (22 in 0.5.2) from the captures on site, five reads added; the CSV differ from 0.5.2 only in `15.w.ka`, `35.w.fs1`, `50.w.em1`, `52.w.em3`, `75.w.fs2` and `f5.w.fs3`, by added lines. The notice was corrected before publication: 0.5.1 and 0.5.2 still listed the changes of 0.5.0. Downloaded again: the four checksums right, 660 messages without error in the official ebusd, both archives.
**0.5.2 released (2026-11-18)** from `weishaupt` `419821c`: 0.5.1 plus two writable settings proven by the telegram log (`fs1` `RoomFrostProtectionTemp`, `em3` `GradientCurve`), 22 in all; the CSV differ from 0.5.1 only in `35.w.fs1` and `52.w.em3`. Downloaded again: the four checksums right, 613 messages without error in the official ebusd 26.1.
**0.5.1 released (2026-11-18)** from `weishaupt` `da5a1ef`: 0.5.0 plus three writable settings in lot C (`ka` `RegulationP`, `RegulationI`, `fs1` `BoilerMCBoostTemp`), 20 in all; the CSV differ from 0.5.0 only in `15.w.ka` (+4 lines) and `35.w.fs1` (+2). Downloaded again: the four checksums right, 611 messages without error in the official ebusd 26.1. `weishaupt-0.5.0` stays online beside it.
**0.5.0 released (2026-11-18)** from `weishaupt` `24b03d7`, on the owner's word: the two commits of lot A pushed to `weishaupt-pr` (fast-forward) with a comment on #717, the ten lot branches forced, five files published. Downloaded again: the four checksums right, 605 messages without error in the official ebusd 26.1; the compiled CSV differ from 0.4.3 only in `15.w.ka` (the renamed message) and in the `HcMode` line of the three module files. `weishaupt-0.4.3` was deleted the same day on the owner's request, its tag kept in the local clone. The three decisions of the owner of
that day are applied (see "Decisions and history"): `HcMode` decodes for a module without
outside sensor, `DHWOperationMode` is `DHWLoadingPriority`, the 38 value-list entries have
labels in the metadata. Lot A has two more commits and every lot above it was replayed (new
hashes in the table; the fork still has those of 0.4.3, and `weishaupt` is still `0eb6d16`
locally and on the fork). Trial integration `weishaupt-next` `24b03d7`; `scripts/check.sh`
clean in seven steps on lot A (135 messages) and on the trial (605 messages in English,
German and French, 566 fixtures decoded by ebusd, none refused). The former heads are kept
locally as `backup/pre044-*`.

**0.4.3 released (2026-11-18)** from `weishaupt` `0eb6d16` (stack A to M plus the pin
commit, `weishaupt-M` `b9d5359`): the CSV are byte-identical to 0.4.2 (compared file by
file, English and French), and the release carries three more files, the metadata asset
`weishaupt-metadata-0.4.3.json` (528 messages, menu trees and labels accepted by the owner),
`weishaupt-fixtures-0.4.3.json` and `sha256sums-0.4.3.txt`. Downloaded again after
publication: the four checksums right, 605 messages without error in the official ebusd 26.1.
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
`weishaupt-0.2.0`, `weishaupt-0.3.0`, `weishaupt-0.3.1`, `weishaupt-0.3.2`, `weishaupt-0.4.0`, `weishaupt-0.4.1`, `weishaupt-0.4.2` and `weishaupt-0.4.3` were deleted from the fork on the owner's request once superseded, with their tags (kept in the local clone); `weishaupt-0.5.0`, `weishaupt-0.5.1`, `weishaupt-0.5.2`, `weishaupt-0.5.3` and `weishaupt-0.5.4` are the releases online.

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
| `aghulas/ebusd-configuration` | `weishaupt-0.5.4` (pre-release) | as 0.5.3, plus the flow limits of the direct circuit `50`, written from `ff` (66 in all). Downloaded again after publication: checksums right, 662 messages without error in the official ebusd. |
| `aghulas/ebusd-configuration` | `weishaupt-0.5.3` (pre-release) | as 0.5.2, plus 42 writable settings proven on site (64 in all) and five reads. Downloaded again after publication: checksums right, 660 messages without error in the official ebusd. |
| `aghulas/ebusd-configuration` | `weishaupt-0.5.2` (pre-release) | as 0.5.1, plus two writable settings (22 in all). Downloaded again after publication: checksums right, 613 messages without error in the official ebusd 26.1. |
| `aghulas/ebusd-configuration` | `weishaupt-0.5.1` (pre-release) | as 0.5.0, plus three writable settings in lot C (20 in all). Downloaded again after publication: checksums right, 611 messages without error in the official ebusd 26.1. |
| `aghulas/ebusd-configuration` | `weishaupt-0.5.0` (pre-release) | `HcMode` decodes for a heating module without an outside sensor; `DHWOperationMode` renamed `DHWLoadingPriority` (breaking); labels of the value-list entries in the metadata file; fixtures for every message (schema 2). Downloaded again after publication: checksums right, 605 messages without error in the official ebusd 26.1. |
| `aghulas/ebus-typespec` | `v0.31.0-weishaupt.1` (pre-release) | library package with `@crc` / `@wcrc`, the one the integration branch pins |
| `aghulas/ebusd` | `v26.1-weishaupt.1` | static ebusd with the run-time checksum, the one `scripts/check.sh` uses |

Releases 0.1.0, 0.1.1, 0.1.2, 0.2.0 and 0.3.0 were deleted from the fork on the owner's request; their tags
remain in the local clone.

### Open pull requests

| Pull request | Head | State on 2026-11-17 |
|---|---|---|
| john30/ebusd-configuration#717 (lot A) | `aghulas:weishaupt-pr` `4cd5a54` (since 2026-11-18: two commits on top, `HcMode` without an outside sensor and the rename to `DHWLoadingPriority`, explained in a comment posted the same day; `66b775e` before) | open, mergeable, no review (read again on 2026-11-18). Only the owner's two comments (2026-11-16, 2026-11-17). Description updated on 2026-11-17 (boiler status messages, section "File names"). **Two commits wait locally** (`b2e2db7`, `4cd5a54`): a fast-forward of `weishaupt-pr`, on the owner's word; comment to post with it in `docs/pr-lot-a.md`. |
| john30/ebusd#1825 (run-time checksum) | `aghulas:crc` `492867d9` | open, mergeable, no review, no comment |
| john30/ebus-typespec#8 (lot B) | `aghulas:wcrc-decorator` `75c7d58` | opened on 2026-11-17, mergeable, no review, no comment |

Comments posted on 2026-11-17, no answer yet: john30/ebusd-configuration#616 (points another
contributor working on Weishaupt files to #717) and john30/ebusd#1814 (this installation as a
data point on arbitration with room units).

## Open

### Needs the owner

- **Release 0.5.4: done** (2026-11-18, see "Current state").
- **Release 0.5.3: done** (2026-11-18, see "Current state").
- **Flow limits of `em1`: done.** Proven from `ff` on 2026-11-18 (batch 7), in 0.5.4; `ha-weishaupt` v0.1.3 sends them from `ff`.

- **Release 0.5.1: done** (2026-11-18, see "Current state").
- **Release 0.5.2: done** (2026-11-18, see "Current state"); it is the target of the switch of the installation's ebusd, prepared by the deployment session.
- **Telegram log: done.** Exported read-only on 2026-11-18 by the deployment session
  (`out/ebusd-telegram-log-export/`, installation data, not versioned); read into
  `evidence/settings-writes.md`, "Changes in the telegram log".
- **Captured changes of the settings the client writes** (actions 2 to 7 of
  `evidence/settings-writes.md`, "Coverage"): 44 numeric settings need one change and its
  restore each, sent by the client in service, then an export of the telegram log (no snapshot
  needed); 5 more (modulation limits, room factor), the choices and the program slots need the
  owner's decision first. In order of yield: `fs2` + `fs3` (22), `em1` + `em3` (13), `fs1` (7),
  `ka` flow maximum and hot-water setpoint (2).

- **Release 0.5.0: done** (2026-11-18, see "Current state"). The three new French strings of lot A were read and kept by the owner the same day; the label of burner phase 9 stays provisional.
- **Number of that release: settled, 0.5.0** (owner, 2026-11-18). A message is renamed, so
  the second number changes, as the rule below says. It was first built as 0.4.4 on the
  wording of the task; the content is the same. A consumer that accepts ">= 0.4.3, < 0.5"
  does not take this release without a look at `renamed_from`.
- **Values 1 and 2 of `DHWLoadingPriority`.** Only 0 (`Priority`) was read. The manual lists
  priority, parallel, sliding; the list has 1 = `Sliding`, 2 = `Parallel`; neither order is
  established (`evidence/ka-reads.md`, note of 2026-11-18). Settling it needs the register
  read on a circuit set to parallel or sliding: the operator's to arrange. Not swapped.
- **`ForcedVenting` (operating phase 9)** has no source; kept in the list, recorded as not
  established (`evidence/broadcast-kastatus.md`), its label `provisional`. Needs a source
  (a German or newer manual, or the phase seen on the bus) or the owner's word to accept
  the label as it is.
- **Three French comment strings written on 2026-11-18** for lot A, of vendor terms only
  (`evidence/terms.md`, "Coverage"): "priorité de la charge ECS sur le circuit de chauffage",
  "charge ECS prioritaire sur le circuit de chauffage, en parallèle, ou mobile",
  "température extérieure, -100.0 lorsque le module n'a pas de sonde extérieure". Not read
  by the owner yet.

- **Release carrying the metadata asset: done.** `weishaupt-0.4.3` was published on
  2026-11-18 on the owner's word (see "Current state"). Nothing waits here for the contract;
  the next step of the companion is its phase 1, in `aghulas/ha-weishaupt`.

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

- **Settings left out of lot C** (list in `evidence/settings-writes.md`, "Left out" and
  "Coverage"): each needs a write from source `ff` captured and read back, which is the
  operator's to do (rule 7). Of the 71 numeric settings the client in service writes, 22 are
  in lot C, 44 need one captured change each, 5 a decision first; the actions, ordered by what
  each unlocks, are in that record.
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
  integration branch), fixtures in the same step (every reading of `evidence/fixtures.toml`
  against its record, and decoded by the ebusd of the check: `scripts/fixtures.py`). `scripts/check.sh hygiene` runs the first step alone.
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
- **Fixtures.** `evidence/fixtures.toml` is a transcription of telegrams the evidence records
  hold, never a source: a telegram goes into its record first (how, when, on which device),
  with request and answer on one table row, then into the file with the name of the record
  and the day. A message added to a lot gets a reading the same way; `scripts/fixtures.py
  check` lists the messages without one. A reading that stops decoding to its value is a
  finding about the record or the definition: the number is not adjusted. A telegram ebusd
  refuses is kept with `error`, as a known defect. The fixtures file has its own `schema`
  number (2); adding readings does not change it.
- **Versions (definitions and companion).** Names are the interface: an entity of the
  companion is identified by circuit, message and field.
  1. Until 1.0 the **second** number of a definitions release changes for a breaking change:
     a message or a field renamed, removed, retyped, or a field inserted before others (as
     `FirstByte` was in 0.4.0), or the `schema` number of the metadata raised. The **third**
     changes for a compatible one: messages or trailing fields added, comments, translations,
     labels, menus, metadata values, a range widened or removed (values that were refused
     decode, as `HcMode` in 0.5.0). A rename changes what ebusd publishes (`read`, MQTT
     topic, entity key) and is the plainest breaking change:
     the entry carries `renamed_from` with the former key in the sidecar and keeps it in
     later releases, the notice of the release names the old and the new name and the reason
     under "Changes since", and the companion contract lists it. First case:
     `ka/DHWOperationMode` → `ka/DHWLoadingPriority` (release 0.5.0, prepared on
     2026-11-18).
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
  fixtures file (`evidence/fixtures.toml`, each reading decoded by ebusd on the CSV of the
  archives) and `sha256sums-<version>.txt` for all of them.
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

- **2026-11-18, batch 7 (flow limits of `em1` from `ff`) and trial release 0.5.4 (local).**
  Flow maximum and minimum of `50` changed and restored from `ff` (16:28 to 16:29, raw
  telegrams through ebusd), read back at `50` and `15`: the 44 numeric settings of the campaign
  are proven. Added to `50.w.em1` (lot C), their reads removed from lot G (one conflict, one
  comment fixup); metadata 66 written. Trial `INTEGRATION=weishaupt-next scripts/release.sh
  0.5.4`, `weishaupt-next` `970143b`: seven steps clean, 662 messages in three languages, 755
  fixtures decoded; C alone 295 messages. CSV against 0.5.3: only `50.w.em1.csv` (two write
  lines, the two reads with `[WCRC]` and their range, same ids). Notice: "Changes since 0.5.3",
  the read-only line of these two removed. Backups `backup/pre059-*`.

- **2026-11-18, captures on site, batch 6 (system manager) and trial release 0.5.3 (local).**
  Flow maximum and hot-water setpoint of `15` changed and restored from `ff` (15:46 to
  15:47), read back; `50` read the new flow maximum too, so the refusals at `50` came from the
  source `31`. The two reads of lot A become read / write in lot C (as `BlockingTime`; lot A
  untouched). Campaign: 42 of 44 numeric settings proven; lot C at 64. Trial
  `INTEGRATION=weishaupt-next scripts/release.sh 0.5.3`, `weishaupt-next` `e3ed65f`: seven steps
  clean, 660 messages in three languages, 64 written in the metadata, 747 fixtures decoded;
  `scripts/check.sh` clean on C (291 messages). CSV against 0.5.2: `15.w.ka`, `35.w.fs1`,
  `50.w.em1`, `52.w.em3`, `75.w.fs2`, `f5.w.fs3` only, +42 write lines, five new reads
  (hot-water setpoint of the three room units, boost offset of `fs2` and `fs3`), the other reads
  unchanged in ID with the `[WCRC]` marker and their range. Backups `backup/pre058-*`.

- **2026-11-18, captures on site, batch 5 (room unit `fs1`): lot C at 62 settings (local).**
  The seven settings of `35` still unproven changed and restored from `ff` (15:39 to 15:43),
  each read back. Added to `35.w.fs1` (lot C); the six reads of them removed from lot G (a
  fixup of its first commit, no textual conflict). `scripts/check.sh` clean on C (289
  messages) and on `weishaupt-next` `e51f0c5`: 658 messages, 62 written, 739 fixtures decoded.
  Backups `backup/pre057-*`. Left: the flow limits of `em1` (from `ff`) and the two of `ka`.

- **2026-11-18, captures on site, batch 4 (module `em3`): lot C at 55 settings (local).** Six
  settings of `52` changed and restored (15:36 to 15:39): the room setpoints and the summer /
  winter threshold from `ff`, the flow limits from `31`, taken on `52` as on `51` and unlike
  `50` (the accepted source per device is in `evidence/settings-writes.md`, batch 4, and in the
  comment of each file). Added to `52.w.em3` (lot C), its reads removed from lot G (one
  conflict). `scripts/check.sh` clean on C (275 messages) and on `weishaupt-next` `e935ad4`:
  650 messages, 55 written, 711 fixtures decoded. Backups `backup/pre056-*`. No archive yet.

- **2026-11-18, captures on site, batch 3 (direct circuit `em1`): lot C at 49 settings
  (local).** Five settings of `50` changed and restored from `ff` (14:59, 15:27 to 15:29), each
  read back at `50` and, with the same value, at `15`: the two addresses share the registers
  (comment in `50.w.em1`, lot C; `evidence/heating-modules-reads.md`). The flow limits written
  from `31` were acknowledged and not taken: not in the lot, a finding (a change from `ff` would
  prove them; the client writes them from `31`). Added to lot C in `50.w.em1`; lot G keeps the
  flow limits and the boost offset of `em1` as reads (one conflict resolved). Three restarts of
  Home Assistant fall outside every change / restore pair. `scripts/check.sh` clean on C (263
  messages) and on `weishaupt-next` `bfbf48a`: 644 messages, 49 written, 687 fixtures decoded.
  Backups `backup/pre055-*`. No archive yet.

- **2026-11-18, captures on site, batch 2 (room unit 3): lot C at 44 settings (local).** The
  eleven settings of `fs3` changed and restored from `ff` (14:53 to 14:58), 22 writes
  acknowledged, each read between change and restore equal to the written value. Added to lot
  C as `f5.w.fs3`, defined as `fs2` (same two conflicts resolved in G and H); metadata eleven
  `fs3` entries. `scripts/check.sh` clean on C (253 messages) and on `weishaupt-next` `7fd73dd`:
  639 messages, 44 written, 667 fixtures decoded. Backups `backup/pre054-*`. No archive yet.

- **2026-11-18, captures on site, batch 1 (room unit 2): lot C at 33 settings (local).** The
  deployment session changed and restored the eleven settings of `fs2` from `ff` with the client
  0.1.1 (14:40 to 14:49) and exported the telegram log: 22 writes acknowledged, every read after
  a write equal to the written value, every value restored. Added to lot C as `75.w.fs2` (the
  file now starts in C; lot G keeps the five live values of `fs2`, two conflicts resolved by
  hand, in G and H); the hot-water setpoint and the boost offset of `fs2` are new messages.
  Metadata: eleven `fs2` entries, `change-observed`. A restart of Home Assistant at 14:44 falls
  between two pairs and touched neither ebusd nor a proof. `scripts/check.sh` clean on C (231
  messages) and on `weishaupt-next` `4a5f63f` (`INTEGRATION=weishaupt-next
  scripts/integrate.sh`): 626 messages in three languages, 33 written, 623 fixtures decoded.
  No archive built: one trial release when the batches are done. Backups `backup/pre053-*`.

- **2026-11-18, telegram log read; lot C at 22 settings; release 0.5.2.**
  - **Export** of the telegram log of the ebusd add-on (deployment session, read-only): 84
    `50 23` writes from 2026-11-10 to 2026-11-18, all acknowledged, checksum right for all,
    29 device / register pairs, 575 reads after them. Matched write by write with the next read
    of the same register.
  - **Proven**: each of the 20 settings of 0.5.1 changed, read back and restored (2026-11-15,
    and 2026-11-17/18 for blocking time, change-over time, hot-water switching difference, flow
    maximum of `51`); two more, from the proof procedure of the client 0.1.1 on 2026-11-18:
    `fs1` `RoomFrostProtectionTemp` (8.0 → 8.5 → 8.0) and `em3` `GradientCurve` (10.0 → 10.5
    → 10.0), both from `ff`. Added to lot C (two commits); their reads leave lot G (two
    commits amended); metadata `change-observed` for all 22; no new French string.
  - **Not proven by the log**: writes of the stored value only (legionella day, circulation
    with legionella, boiler sequence, control variation); de-couple maximum 78.5 not taken from
    `ff` nor from `31`; the `ff` rule shown with telegrams on `51` (five settings acknowledged
    and ignored from `31`); `SwitchOnRuntime` above 10 not taken; one program slot of `fs1`
    written from `31` and taken twice (lot H, no write side).
  - **Check**: `scripts/check.sh` clean on C (209 messages) and on `weishaupt-next` `419821c`
    (`INTEGRATION=weishaupt-next scripts/release.sh 0.5.2`): 613 messages in English, German
    and French, 22 written in the metadata, 579 fixtures decoded by ebusd. CSV against 0.5.1:
    `35.w.fs1.csv` and `52.w.em3.csv` only, one write line each and the `[WCRC]` marker on the
    read. Backups `backup/pre052-*`. Pushed and published the same day from the main session on
    the owner's word (lots C to M forced, `weishaupt` `419821c`, five files); downloaded again:
    checksums right, 613 messages without error in the official ebusd 26.1.

- **2026-11-18, lot C extended to 20 settings; release 0.5.1.**
  - **Added**: `ka` `RegulationP` (`9f 02`, 10 to 300) and `RegulationI` (`9e 02`, 10 to 200),
    `fs1` `BoilerMCBoostTemp` (`11 01`, 0.0 to 20.0 K, step 0.5). Same evidence as the 17: the
    write of the stored value from `ff` captured and acknowledged on 2026-11-16, the read by
    ebusd equal, and the change in the operator's log of 2026-11-15 (100 → 101 → 100; 2.0 → 2.5
    → 2.0 K). The record had them as "awaiting validation", after the client's register list;
    the operator's log, written after the test, says otherwise. Ranges read in the French
    manuals (WCM-KA 3.0 pages 89 and 90; WCM-FS 2.0 page 60). The boost offset carries
    `copy-in-use` in the metadata.
  - **Searched for other captures**: 85 snapshots of `grab result all` (27 distinct `50 23`
    telegrams, all already in the records), the ebusd add-on log, the Home Assistant log, the
    operator's log; the telegram log of the add-on is the one source left (see "Needs the
    owner"). Nothing else met the rule: every other setting has at most notes of a test or a
    write of the stored value. Inventory of the 71 numeric settings and the other writes of the
    client, with the action that would prove each: `evidence/settings-writes.md`, "Coverage".
  - **Stack**: C two commits, G to K replayed (one conflict in `35.w.fs1.tsp`, the boost offset
    and the program slots of lot H side by side), L one commit (three French strings, vendor
    terms, `evidence/terms.md`), M one commit. Backups `backup/pre051-*`. `scripts/check.sh`
    clean on C (seven steps, 205 messages) and on the trial `weishaupt-next` `da5a1ef`
    (`INTEGRATION=weishaupt-next scripts/release.sh 0.5.1`): 611 messages in English, German
    and French, 531 messages in the metadata, 20 written, 571 fixtures decoded by ebusd. CSV
    against 0.5.0: only `15.w.ka.csv` (+4 lines) and `35.w.fs1.csv` (+2 lines), English and
    French; the notice says 20 settings. Pushed and published the same day from the main session on the
    owner's word (lots C to M forced, `weishaupt` `da5a1ef`, five files); downloaded again: checksums
    right, 611 messages without error in the official ebusd 26.1.

- **2026-11-18, three decisions of the owner applied; release 0.5.0.** Pushed and published
  the same day from the main session on the owner's word, the branch behind #717 included.
  - **`HcMode` (lot A, `b2e2db7`).** ebusd refused `em2/HcMode` and `em3/HcMode` because the
    field `OutsideTemp` of the answer had the type `temp2` (`D2B`, range -50 to 127 written
    into the CSV) and the modules without outside sensor send `00 9c`, -100.0: an ordinary
    value of the type, not its replacement value, so no type can show it as "not
    available". The field has a scalar of its own, `otemp2` (`D2B`, °C, no range), and its
    comment says what -100.0 means. The three recorded exchanges decode in ebusd (em1 as
    before, 11.000; em2 and em3 -100.000); the two fixtures carry their values, case
    `no-sensor`, and no fixture is refused any more. `evidence/em-hcmode.md`.
  - **Hot-water loading priority (lot A, `4cd5a54`).** `DHWOperationMode` is renamed
    `DHWLoadingPriority`: `DHW` prefix of its neighbours, words of the vendor's chapter on
    the priority of DHW loading (manual of the room unit, 83277502 p. 55, 83277504 p. 59)
    rather than the parameter name "DHW operation", which says nothing of what is set and
    would be mistaken again for a mode. Comments rewritten from the manual; value list
    unchanged. Recorded in `evidence/ka-reads.md` and as a comment in the file: only 0 was
    read; 1 and 2 are not established and were not swapped. Carried to `src/fr.yaml` (lot
    L: two keys out, three in, 278), the sidecar (lot M: new key, `renamed_from`, label
    "Hot water loading priority" / "Priorité de la charge ECS", menu `dhw` unchanged since
    it is still a hot-water setting), the fixtures, the glossary (the row "hot water
    operating mode", misapplied, replaced), `evidence/settings-writes.md`.
  - **Form on lot A**: two commits on top of the fourteen, not amendments, so that
    `weishaupt-pr` moves by a fast-forward and each message states its observation
    (`docs/pr-lot-a.md`). The lots above were replayed without conflict (`git rebase
    --onto`); one commit of lot C changed in its context lines only.
  - **Labels of the value-list entries (lot M, `17a4bc7`).** The proposal accepted by the
    owner is applied: table `[values]` of the sidecar, keyed by ebusd name, 31 entries, the
    7 weekdays taken from `[days]` (one source, French with a capital); `[status]` gains
    `values = "accepted"`. `scripts/metadata.py` writes `value_labels` beside `values` on
    the 793 fields that have a list, lists the provisional labels in `open.value_labels`
    (`ForcedVenting`), and its check fails for an entry without a label in each language, a
    label for an entry no list has, or a weekday labelled twice (tried on five altered
    copies of the sidecar). `evidence/terms.md` has the 38 rows (22 `vendor`, 15 `owner`,
    1 `provisional`). Count corrected in `docs/i18n.md`: 7 lists and 38 entries of the
    lots, not 8 and 43 (the eighth is a Wolf list); the "43" of the two entries below is
    that older count.
  - **Trial**: `INTEGRATION=weishaupt-next scripts/release.sh 0.5.0` (first built as 0.4.4,
    then again under the number the owner chose: a rename takes the second number),
    `weishaupt-next` `24b03d7`, seven steps clean, 605 messages in English, German and French (528 of the
    lots, 545 CSV lines), 566 readings decoded by ebusd. **CSV against 0.4.3**: four lines
    in four files, in both archives — `15.w.ka.csv`, the line of the renamed message (name,
    message comment, field comment); `50.w.em1.csv`, `51.w.em2.csv`, `52.w.em3.csv`, the
    line of `HcMode` (field `outsidetemp`: range `-50-127:0.5` removed, comment). No line
    added or removed, no other column changed. **Metadata against 0.4.3**: key
    `ka/DHWOperationMode` gone, `ka/DHWLoadingPriority` with `renamed_from`, label and
    descriptions; `outsidetemp` of the three `HcMode` without `min`, `max`, `step`;
    `value_labels` on 793 fields; `status.values`, `open.value_labels`; schema 1 unchanged.
    **Fixtures**: the online file of 0.4.3 is schema 1 with 17 settings; the trial file is
    schema 2 with 566 readings, as prepared earlier the same day, now with the renamed key
    and the two `HcMode` readings decoded (`refused_by_ebusd` empty).
  - **The clone**: `weishaupt-F` is the branch its own checkout is on; its ref was moved
    with the others and the two files of lot A that differ brought in line there, nothing
    else touched. Temporary worktrees of the session removed.

- **2026-11-18, fixtures for every message, verified by ebusd.** Local only: workbench
  commits, no change in the forks, nothing pushed or published.
  - **Before**: 17 readings of 17 settings (3 % of the 528 messages), checked by a decoder of
    the script for 16-bit registers. The records held a request and an answer for 483
    messages (91 %): all 357 program slots of the room units and the 42 of `50`, the register
    reads of the room units and modules, the fault counters, live values and information
    values of both boilers, the settings, the status telegrams. 45 messages had a value in
    their record but no bytes in the form ebusd sends: 12 registers of the system manager,
    6 of the clock and the 9 of the fault log of `50`, the counters and the fault history of
    both boilers (16, read so far only through the multi-item requests of the vendor tool),
    and the exchange `HcMode` of the modules `51` and `52`.
  - **Read on the bus, read-only, once each** (2026-11-18, 10:26 to 10:28, `hex` command,
    `50 22` and `50 00` only, IDs taken from the compiled CSV, three seconds apart): those 43
    registers, all answered at the first attempt, no repeat. The two `HcMode` exchanges and a
    status broadcast with its source address come from the passive capture of the same
    minute (nothing sent). Each reading was written into its record first: `ka-reads`,
    `em1-clock-program`, `em1-fault-log`, `bc-counters`, `bc-fault-history`, `em-hcmode`,
    `broadcast-kastatus`. They agree with the earlier values (same fault-log entry, same
    fault history on both boilers; operating hours of the first boiler 41 higher than 41
    hours before).
  - **After**: `evidence/fixtures.toml` (schema 2), 566 readings of 528 messages out of 528:
    535 reads, 17 writes, 14 passive telegrams. By kind: program slots 357, settings 65,
    live values 44, diagnostics 37, counters 18, states 7. By device: boilers 26 and 26,
    system manager 96 (`ka` 29, `em1` 67), modules 11 and 11, room units 119 each,
    broadcast 1. Awkward cases included: the two answers without data of lot J (first byte
    6 and 10), replacement values in passive telegrams, sensors not fitted (-40), memory
    reads of both boilers, a boiler idle and firing.
  - **Verification** (`scripts/fixtures.py`, in step 7 of `scripts/check.sh` and in
    `scripts/release.sh`): ebusd itself decodes each telegram. The build of the check is
    started without a bus on the lot files, each telegram injected (`--inject=stop`) and read
    back from the cache; ebusd names the message and gives every field. The former decoder
    of the script remains only as a fallback where no ebusd can run
    (`CHECKCONFIG=actions`), and says so. Tried on nine altered copies of the source (a
    value, a byte, a name, a day, an ID): each one fails.
  - **One discrepancy**: `em2/HcMode` and `em3/HcMode`, refused by ebusd (see "Needs the
    owner"). No other reading disagrees with its record. One transcription error of the day
    (a load typed 27 for `1c`) was caught by the check before the commit.
  - **Left without a reading of its kind**: no `50 22` read of a defined message answers the
    replacement value `00 80` on this installation (such registers were left out of the
    lots), so the fixtures show it in passive telegrams only; no reading of a boiler in
    lockout, of a negative temperature on a fitted sensor, or of a status broadcast with the
    burner on. Each needs the installation in that state.
  - **Trial**: `INTEGRATION=weishaupt-next scripts/release.sh 0.4.4`, `weishaupt-next`
    `0eb6d16`, `scripts/check.sh` clean in seven steps, 605 messages in English, German and
    French; CSV of both archives identical to 0.4.3 (only the notice differs: one sentence
    on the fixtures file), metadata identical but for the version.

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
