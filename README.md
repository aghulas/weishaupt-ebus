# weishaupt-ebus

Workbench for eBUS message definitions of Weishaupt heating systems for
[ebusd](https://github.com/john30/ebusd): they are published from a fork and proposed to the
official project in parallel.

The definitions cover Weishaupt WTC condensing boilers and their Kromschröder WCM controllers
(cascade manager, remote controls, heating circuit modules, system controller). They are developed
and checked on a live installation with two WTC 250 boilers in cascade and three heating circuits.

## What is here

- `docs/plan.md` — current state, road to 1.0, conventions
- `CHANGELOG.md` — release history
- `docs/upstream-checklist.md` — what a change must satisfy before it enters the fork or is proposed upstream
- `docs/discoveries.md` — findings from the field that are not yet in definitions
- `evidence/` — how each definition was established, and `evidence/fixtures.toml`
- `docs/companion-contract.md` — the metadata and fixtures files released with the definitions
- `schemas/` — JSON Schemas (Draft 2020-12) for metadata (schema 1) and fixtures (schema 2)
- `scripts/` — setup, checks (commit hygiene, format, compile, `ebusd --checkconfig`, translations, metadata, fixtures, schema validation), integration worktree check, release archive
- `tests/` — unit tests for the workbench scripts and schemas
- `AGENTS.md` — instructions for coding agents working in this repository

The definitions themselves are not here. They are written in TypeSpec on the `weishaupt` branch
of a fork of [ebusd-configuration](https://github.com/john30/ebusd-configuration), from which
releases are published and upstream pull requests are cut on demand.

## Releases

| Release | Content |
|---|---|
| [weishaupt-0.6.0](https://github.com/aghulas/ebusd-configuration/releases/tag/weishaupt-0.6.0) | compiled ebusd CSV of all lots, in English and in French, with a notice on how to use them, and the metadata file the Home Assistant companion reads |
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
scripts/check.sh   # commit hygiene, format check, compile, ebusd --checkconfig, i18n, metadata, fixtures
scripts/integrate.sh   # checks `weishaupt` in a clean worktree (out/integration)
scripts/release.sh <version>   # builds reproducible CSV archives, JSON assets and checksums under out/release/
python3 -m unittest discover -s tests -v   # unit tests for workbench scripts and schemas
```

Requires Node.js (LTS major pinned in `.nvmrc`), Docker and the GitHub CLI.

## Related

- [ha-weishaupt](https://github.com/aghulas/ha-weishaupt) — Home Assistant integration built on these definitions

## License

GPL-3.0, like the upstream ebusd-configuration repository. See `LICENSE`.
