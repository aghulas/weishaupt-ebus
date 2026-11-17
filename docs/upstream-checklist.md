# Upstream checklist

Taken from `guidelines.md` of `john30/ebusd-configuration` and the style guide of
`john30/ebus-typespec`. Re-read both when upstream changes.

## Before a commit

- [ ] `scripts/check.sh` is clean: commit hygiene (identity, no tool trailer, no site data in added
      lines), format, compile without diagnostics, `ebusd --checkconfig` without error
- [ ] Declarations and comments in English
- [ ] `src/` holds only `.tsp` files and i18n YAML files
- [ ] One top-level namespace for the manufacturer, one unique namespace per circuit, unique message names
- [ ] Read / write and active / passive variants of a message combined where possible
- [ ] A single field in a message is named `value`
- [ ] Incoming-only fields marked optional
- [ ] Predefined types preferred over new ones; only eBUS internal scalars are all upper case
- [ ] Shared models reused through the include schema (`union _includes`)
- [ ] Comments add information; none that only repeats the message or field name
- [ ] Models not nested too deep in the type graph
- [ ] `src/main.tsp` lists every file added or removed, imports sorted. Upstream asks for
      `npm run maintsp`; on the current base it rewrites unrelated lines, so the import is added by
      hand and the pull request says so if asked
- [ ] A new file is named `ZZ.<identification>.<circuit>.tsp` with a slave address, so that ebusd
      loads it for the right devices only and no existing file of the folder is replaced (see
      `docs/plan.md`, "File names")
- [ ] An evidence record exists for every new or changed definition

## Before a pull request

- [ ] Branch rebased on upstream `master` (`main` for `ebus-typespec`); a lot stacked on other
      lots of the fork is cut again on what is merged upstream
- [ ] One topic, reviewable in one sitting
- [ ] Does not depend on an unmerged pull request, or says so in its first line
- [ ] Description states what was verified on a live bus and what was not
- [ ] Nothing site-specific anywhere (see `AGENTS.md`, rule 4)
- [ ] Reviewed by the repository owner
