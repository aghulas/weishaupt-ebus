# weishaupt-ebus

Workbench for eBUS message definitions of Weishaupt heating systems for
[ebusd](https://github.com/john30/ebusd): they are published from a fork and proposed to the
official project in parallel.

The definitions cover Weishaupt WTC condensing boilers and their Kromschröder WCM controllers
(cascade manager, remote controls, heating circuit modules, system controller). They are developed
and checked on a live installation with two WTC 250 boilers in cascade and three heating circuits.

## What is here

- `docs/plan.md` — the plan, lot by lot: what is in the fork, what is proposed upstream
- `docs/upstream-checklist.md` — what a change must satisfy before it enters the fork or is proposed upstream
- `docs/discoveries.md` — findings from the field that are not yet in a lot branch
- `evidence/` — how each definition was established
- `scripts/` — setup, checks (commit hygiene, format, compile, `ebusd --checkconfig`), integration branch, release archive
- `AGENTS.md` — instructions for coding agents working in this repository

The definitions themselves are not here. They are written in TypeSpec in a fork of
[ebusd-configuration](https://github.com/john30/ebusd-configuration), which carries them on an
integration branch and from which the pull requests are opened.

## Releases

| Release | Content |
|---|---|
| [weishaupt-0.4.0](https://github.com/aghulas/ebusd-configuration/releases/tag/weishaupt-0.4.0) | compiled ebusd CSV of all lots, in English and in French, with a notice on how to use them |
| [ebus-typespec 0.31.0-weishaupt.1](https://github.com/aghulas/ebus-typespec/releases/tag/v0.31.0-weishaupt.1) | library build with the `@crc` and `@wcrc` decorators, needed to compile the definitions |

## Open pull requests

| Pull request | Subject |
|---|---|
| [john30/ebusd#1825](https://github.com/john30/ebusd/pull/1825) | CRC calculated at runtime for Weishaupt memory and register messages |
| [john30/ebusd-configuration#717](https://github.com/john30/ebusd-configuration/pull/717) | Kromschröder/Weishaupt WTC read definitions in `src/wolf` (lot A) |
| [john30/ebus-typespec#8](https://github.com/john30/ebus-typespec/pull/8) | `@crc` and `@wcrc` decorators for message IDs with a leading CRC-8 (lot B) |

## Getting started

```sh
scripts/setup.sh   # clones the forks under repos/
scripts/check.sh   # commit hygiene, format check, compile, ebusd --checkconfig
scripts/integrate.sh   # rebuilds the integration branch from the lots and checks it
scripts/release.sh <version>   # builds the CSV release archive under out/release/, publishes nothing
```

Requires Node.js (LTS major pinned in `.nvmrc`), Docker and the GitHub CLI.

## Related

- [ha-weishaupt](https://github.com/aghulas/ha-weishaupt) — Home Assistant integration built on these definitions

## License

GPL-3.0, like the upstream ebusd-configuration repository. See `LICENSE`.
