# Agent instructions — weishaupt-ebus

Read this file first, then `docs/plan.md` (what to do next) and `docs/upstream-checklist.md` (what a
change must satisfy before it enters the fork, and before it is proposed upstream).

## Goal

Publish proven eBUS message definitions for Weishaupt heating systems (WTC boilers, Kromschröder
WCM controllers) that any owner of such a system can use with ebusd, and keep adding what is
discovered later. Two tracks, in this order of priority:

1. **The fork is the deliverable.** The definitions are integrated on one branch of the fork of
   `ebusd-configuration` and published from it as compiled CSV releases. Work never waits for the
   upstream maintainer.
2. **Upstream in parallel.** The same definitions are kept ready as small pull requests to the
   official ebusd repositories maintained by john30, and proposed when the maintainer responds. A
   merged pull request is the best outcome, not a condition for progress.

Success is a published release that works on someone else's installation, not a working local setup.
The upstream form (rule 2) and the evidence (rule 3) apply to the fork exactly as to a pull request.

## Repositories

This repository is the workbench: plan, checks, evidence. It holds no definitions. The definitions
live in the forks, cloned under `repos/` (not versioned here, see `scripts/setup.sh`):

| Fork | Upstream | Holds |
|---|---|---|
| `aghulas/ebusd-configuration` | `john30/ebusd-configuration` | TypeSpec definitions, `src/wolf/`; integration branch and CSV releases |
| `aghulas/ebusd` | `john30/ebusd` | runtime CRC for Weishaupt messages; released builds |
| `aghulas/ebus-typespec` | `john30/ebus-typespec` | TypeSpec library: decorators, emitter |

The Home Assistant integration (`aghulas/ha-weishaupt`) is a separate project and is out of scope.
What it needs from here is one generated file per release, the metadata asset: its source is
`metadata/weishaupt.toml` on the top branch of the configuration fork, its format is in
`docs/companion-contract.md`, and rules 3 and 4 apply to it as to a definition.

## Rules

1. **TypeSpec is the only source.** Every definition is written in TypeSpec, in the fork of
   `ebusd-configuration`. CSV is a compiled output and is never edited by hand.
2. **Upstream form from the first commit.** English only. Follow `guidelines.md` of
   `ebusd-configuration` and the style guide of `ebus-typespec`. Run `scripts/check.sh` before every
   commit; a change is not ready while it reports a failure.
3. **Evidence for every definition.** A register, codec or value list enters the integration branch
   or a lot branch only with a record under `evidence/` showing how it was established (bus read,
   manual page, comparison with the vendor service tool). No evidence, no definition.
4. **Nothing site-specific.** No building, organisation or person names, no IP addresses, host names,
   credentials or serial numbers, in files, commit messages or pull request texts. Describe the test
   site only by its equipment.
5. **Small, reviewable lots.** A definition enters the integration branch as part of a lot (see
   `docs/plan.md`): one topic, useful on its own, one pull request upstream when it is proposed. A lot
   may build on another lot of the fork; it never waits for an upstream merge.
6. **Branches stay rebased** on upstream `master`, with a clean history: one topic per commit,
   message explaining what was observed and how. The integration branch is rebuilt from the lot
   branches, not edited directly.
7. **Read-only towards the heating system.** Work in this repository may read from a live bus. It
   never writes to a boiler or controller. Write tests belong to the operator of the installation.
8. **Ask before anything visible outside**: upstream, opening, retargeting or force-pushing a pull
   request, commenting on issues, pushing to a branch that backs an open pull request; in the forks,
   publishing a release.
9. **No mention of AI tools**: no co-author trailer, session link or tool name in commit messages,
   pull request texts, issue comments or files, in this repository and in the forks.

## Working loop

1. Pick the next open item in `docs/plan.md`, or the oldest entry in `docs/discoveries.md`.
2. Write or change the TypeSpec in the fork, on the lot branch named in the plan.
3. Add or update the evidence record.
4. Run `scripts/check.sh`. Fix until it is clean.
5. Rebuild the integration branch from the lot branches and check it the same way.
6. Update `docs/plan.md` (status, branch, commit) in the same session.
