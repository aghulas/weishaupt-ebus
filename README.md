# weishaupt-ebus

Workbench for eBUS message definitions of Weishaupt heating systems for
[ebusd](https://github.com/john30/ebusd): they are published from a fork and proposed to the
official project in parallel.

**In Home Assistant**, the recommended way is the MQTT bridge
[weishaupt2mqtt](https://github.com/aghulas/weishaupt2mqtt): one add-on (**Weishaupt2MQTT**, from
the add-on repository `https://github.com/aghulas/ha-addons#weishaupt`) that holds ebusd, the
definitions and guarded writes, and publishes the heating system on MQTT; the integration
[ha-weishaupt](https://github.com/aghulas/ha-weishaupt) turns that into devices and entities. Start
with the bridge's README: it gives the installation, the checks, how to write a setting and how to
undo, and its limits. Nothing has to be downloaded from here for that way (integration 1.5.0 or
later; earlier versions create their entry against an ebusd add-on only).

**To use the definitions with ebusd alone**, go to the latest release
[weishaupt-1.6.0](https://github.com/aghulas/ebusd-configuration/releases/tag/weishaupt-1.6.0)
of the fork: its notice (also the `README.md` inside each archive) explains how to install them
with ebusd or the Home Assistant ebusd add-on, how to write settings, and their limits. From 1.0.0
the message and field names, types and the metadata structure are stable (they change only with a
new first number). A stock ebusd 26.1 writes the settings published here end to end (they are all
on non-boiler controllers, which take a placeholder checksum); the write-capable build is for the
composite reads, not required to write. Problems and reports from
other installations: [issues](https://github.com/aghulas/weishaupt-ebus/issues) of this repository.

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
- `docs/mqtt-contract.md` — the MQTT topics and payloads of the bridge `weishaupt2mqtt`
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
| [weishaupt-1.6.0](https://github.com/aghulas/ebusd-configuration/releases/tag/weishaupt-1.6.0) | the definitions: compiled ebusd CSV in English and in French with the installation notice, and the metadata file the Home Assistant integration reads |
| [ebusd v26.1-weishaupt.2](https://github.com/aghulas/ebusd/releases/tag/v26.1-weishaupt.2) | ebusd with the run-time checksum (john30/ebusd#1825), composite reads and IDs longer than 7 bytes; it computes the checksum, but a stock ebusd 26.1 writes the settings here end to end, so it is not required for writing; two static executables. For Home Assistant the same build is the add-on "eBUSd (Weishaupt CRC)": add `https://github.com/aghulas/ha-addons#weishaupt` in the add-on store (that form is for the store only; to read it in a browser, open [`/tree/weishaupt`](https://github.com/aghulas/ha-addons/tree/weishaupt)) |
| [weishaupt2mqtt](https://github.com/aghulas/weishaupt2mqtt) 0.1.4 | the MQTT bridge: ebusd v26.1-weishaupt.2, the definitions 1.3.1 and the write guards in one container; a Home Assistant add-on (**Weishaupt2MQTT**, same add-on repository as above) or a Docker image built from the repository; topics in `docs/mqtt-contract.md` |
| [ha-weishaupt](https://github.com/aghulas/ha-weishaupt/releases) 1.5.0 | the Home Assistant integration, over the MQTT bridge (set up with the bridge alone from 1.5.0) or over ebusd |
| [ebus-typespec 0.31.0-weishaupt.2](https://github.com/aghulas/ebus-typespec/releases/tag/v0.31.0-weishaupt.2) | library build with the `@crc`, `@wcrc` and `@fills` decorators, needed only to compile the definitions from source |

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

- [weishaupt2mqtt](https://github.com/aghulas/weishaupt2mqtt) — the MQTT bridge (ebusd, definitions and guarded writes in one add-on or container)
- [ha-weishaupt](https://github.com/aghulas/ha-weishaupt) — Home Assistant integration built on these definitions, over the bridge or over ebusd
- [ha-addons, branch `weishaupt`](https://github.com/aghulas/ha-addons/tree/weishaupt) — the fork ebusd add-on (run-time checksum and composite-read distribution)

## License

GPL-3.0, like the upstream ebusd-configuration repository. See `LICENSE`.
