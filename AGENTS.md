# Agent instructions — weishaupt-ebus

Read this file first, then `docs/plan.md` (what to do next) and `docs/upstream-checklist.md` (what a
change must satisfy before it is proposed upstream).

## Goal

Get the eBUS message definitions of Weishaupt heating systems (WTC boilers, Kromschröder WCM
controllers) merged into the official ebusd repositories maintained by john30, and keep contributing
what is discovered later. Success is a merged pull request, not a working local setup.

## Repositories

This repository is the workbench: plan, checks, evidence. It holds no definitions. The definitions
live in the forks, cloned under `repos/` (not versioned here, see `scripts/setup.sh`):

| Fork | Upstream | Holds |
|---|---|---|
| `aghulas/ebusd-configuration` | `john30/ebusd-configuration` | TypeSpec definitions, `src/wolf/` |
| `aghulas/ebusd` | `john30/ebusd` | runtime CRC for Weishaupt messages |
| `aghulas/ebus-typespec` | `john30/ebus-typespec` | TypeSpec library: decorators, emitter |

The Home Assistant integration (`aghulas/ha-weishaupt`) is a separate project and is out of scope.

## Rules

1. **TypeSpec is the only source.** Every definition is written in TypeSpec, in the fork of
   `ebusd-configuration`. CSV is a compiled output and is never edited by hand.
2. **Upstream form from the first commit.** English only. Follow `guidelines.md` of
   `ebusd-configuration` and the style guide of `ebus-typespec`. Run `scripts/check.sh` before every
   commit; a change is not ready while it reports a failure.
3. **Evidence for every definition.** A register, codec or value list enters a contribution branch
   only with a record under `evidence/` showing how it was established (bus read, manual page,
   comparison with the vendor service tool). No evidence, no definition.
4. **Nothing site-specific.** No building, organisation or person names, no IP addresses, host names,
   credentials or serial numbers, in files, commit messages or pull request texts. Describe the test
   site only by its equipment.
5. **Small, reviewable pull requests.** One lot per pull request (see `docs/plan.md`). A lot must be
   useful on its own and must not depend on an unmerged pull request unless the plan says so.
6. **Contribution branches stay rebased** on upstream `master`, with a clean history: one topic per
   commit, message explaining what was observed and how.
7. **Read-only towards the heating system.** Work in this repository may read from a live bus. It
   never writes to a boiler or controller. Write tests belong to the operator of the installation.
8. **Ask before anything visible upstream**: opening, retargeting or force-pushing a pull request,
   commenting on upstream issues, pushing to a branch that backs an open pull request.
9. **No mention of AI tools**: no co-author trailer, session link or tool name in commit messages,
   pull request texts, issue comments or files, in this repository and in the forks.

## Working loop

1. Pick the next open item in `docs/plan.md`, or the oldest entry in `docs/discoveries.md`.
2. Write or change the TypeSpec in the fork, on the branch named in the plan.
3. Add or update the evidence record.
4. Run `scripts/check.sh`. Fix until it is clean.
5. Update `docs/plan.md` (status, branch, commit) in the same session.
