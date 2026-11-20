# weishaupt-ebus

Workbench for eBUS message definitions of Weishaupt heating systems for
[ebusd](https://github.com/john30/ebusd): they are published from a fork and proposed to the
official project in parallel.

**To use the definitions**, go to the latest release
[weishaupt-0.6.1](https://github.com/aghulas/ebusd-configuration/releases/tag/weishaupt-0.6.1)
of the fork: its notice (also the `README.md` inside each archive) explains how to install them
with ebusd or the Home Assistant ebusd add-on, how to write settings, and their limits. Releases
up to 0.6.0 were flagged pre-release; from 0.6.1 they are normal releases.

The definitions cover Weishaupt WTC condensing boilers and their Kromschröder WCM controllers:
the system manager (WCM-KA, also called cascade manager), the heating modules (WCM-EM) and the
room units (WCM-FS). They are developed and checked on one installation: two WTC-GB 250 boilers
in cascade, a WCM-KA 3.0, two WCM-EM heating modules and two WCM-FS room units (one addressed for
heating circuits 1 and 2), three heating circuits.

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
| [weishaupt-0.6.1](https://github.com/aghulas/ebusd-configuration/releases/tag/weishaupt-0.6.1) | the definitions: compiled ebusd CSV in English and in French with the installation notice, and the metadata file the Home Assistant integration reads |
| [ebusd v26.1-weishaupt.1](https://github.com/aghulas/ebusd/releases/tag/v26.1-weishaupt.1) | ebusd with the run-time checksum (john30/ebusd#1825), needed to write settings; two static executables. For Home Assistant the same build is the add-on "eBUSd (Weishaupt CRC)" of the repository `https://github.com/aghulas/ha-addons#weishaupt` |
| [ebus-typespec 0.31.0-weishaupt.1](https://github.com/aghulas/ebus-typespec/releases/tag/v0.31.0-weishaupt.1) | library build with the `@crc` and `@wcrc` decorators, needed only to compile the definitions from source |

## Open pull requests

| Pull request | Subject |
|---|---|
| [john30/ebusd#1825](https://github.com/john30/ebusd/pull/1825) | CRC calculated at runtime for Weishaupt memory and register messages |
| [john30/ebusd-configuration#717](https://github.com/john30/ebusd-configuration/pull/717) | Kromschröder/Weishaupt WTC read definitions in `src/wolf` |
| [john30/ebus-typespec#8](https://github.com/john30/ebus-typespec/pull/8) | `@crc` and `@wcrc` decorators for message IDs with a leading CRC-8 |

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
- [ha-addons, branch `weishaupt`](https://github.com/aghulas/ha-addons/tree/weishaupt) — the ebusd add-on with the write-capable build

## License

GPL-3.0, like the upstream ebusd-configuration repository. See `LICENSE`.
