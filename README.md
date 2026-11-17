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
- `scripts/` — setup and checks (commit hygiene, format, compile, `ebusd --checkconfig`)
- `AGENTS.md` — instructions for coding agents working in this repository

The definitions themselves are not here. They are written in TypeSpec in a fork of
[ebusd-configuration](https://github.com/john30/ebusd-configuration), which carries them on an
integration branch and from which the pull requests are opened.

## Open pull requests

| Pull request | Subject |
|---|---|
| [john30/ebusd#1825](https://github.com/john30/ebusd/pull/1825) | CRC calculated at runtime for Weishaupt memory and register messages |
| [john30/ebusd-configuration#717](https://github.com/john30/ebusd-configuration/pull/717) | Kromschröder/Weishaupt WTC read definitions in `src/wolf` (lot A) |

## Getting started

```sh
scripts/setup.sh   # clones the forks under repos/
scripts/check.sh   # commit hygiene, format check, compile, ebusd --checkconfig
```

Requires Node.js (LTS major pinned in `.nvmrc`), Docker and the GitHub CLI.

## Related

- [ha-weishaupt](https://github.com/aghulas/ha-weishaupt) — Home Assistant integration built on these definitions

## License

GPL-3.0, like the upstream ebusd-configuration repository. See `LICENSE`.
