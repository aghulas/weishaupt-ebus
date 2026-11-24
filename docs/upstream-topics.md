# Upstream topic pull requests (ready to cut on demand)

The read and write definitions currently sit upstream as one bundled pull request,
[john30/ebusd-configuration#717](https://github.com/john30/ebusd-configuration/pull/717). If the
maintainer asks for them split into smaller, reviewable topics, these are the prepared titles and
bodies, one per topic, to reuse when the `upstream/<topic>` branches are cut from `weishaupt` (rule
5 and 8 of `AGENTS.md`).

**Provenance.** The texts were written on 2026-11-19 against local, unpushed `upstream/<topic>`
branches, each stacked on the one before. The branch has moved a lot since (definitions reorganised
into the unified `src/wolf/` tree), so the commit ids, branch heads and message counts recorded then
are stale: **re-cut each branch from today's `weishaupt` and refresh the metadata before opening a
pull request.** The titles and bodies below carry over; only the plumbing figures need redoing.

The topics form a dependency chain on top of #717. `boiler-faults` is the first read topic; the
write topics at the end work on a stock `ebusd 26.1` without waiting on john30/ebusd#1825 or
john30/ebus-typespec#8 (see "Writes" below). The order below is the stacking order.

Each body ends, as in the originals, with: checked with `tsp compile`, `tsp format --check` and
`ebusd --checkconfig` (no error); one topic per commit; the evidence for each definition (captures
and their decoding) is kept with the fork and available on request.

---

## Reads (stock ebusd)

### 1. boiler-faults — depends on #717

**Title:** Add Kromschröder/Weishaupt boiler fault history, service hours and system fault log to src/wolf

Builds on the register reads of #717.

- **Fault history of the WTC boiler automats** (`08.w.bc1`, `18.w.bc2`, new files named with the
  identification the boilers answer, `W`): the six last faults, each an 8-byte slot of EEPROM
  (fault number with a warning bit, operating phase, load, boiler, flue gas and return
  temperatures, ionisation), and the pointer to the most recent slot. Read with the memory read
  `PBSB 50 00`, whose ID is a precomputed CRC-8 followed by items "code, address" (high nibble of
  the code = bytes minus one, low nibble = memory area); a shared base `memr` keeps the first
  answer byte as the field `FirstByte`, which reads 0 in a normal answer.
- **Hours since the last service** of both boilers (info value i46, a register read, factor 10).
- **Fault log of the system** (`50.w.em1`): the most recent entry of the system manager's log
  (code, type, device and time stamp).

Verified on a live bus with two WTC-GB boilers (automat software 11.04): the 48 values of the six
slots of the first boiler equal those the vendor service tool shows in its fault history; the
memory-read checksum recomputed offline matches every captured request.

### 2. boiler-counters — depends on boiler-faults

**Title:** Add Kromschröder/Weishaupt boiler operating counters to src/wolf

Builds on `memr`. Operating hours, burner hours and burner starts of both WTC boiler automats, one
memory read (`PBSB 50 00`) of their EEPROM counters each. Verified on a live bus: read on both
boilers over hours, operating hours step by one per hour of wall-clock time and the burner counters
step as the burners run (low byte first).

### 3. boiler-live-values — depends on boiler-counters

**Title:** Add Kromschröder/Weishaupt boiler live values read from memory to src/wolf

Builds on `memr`. Two memory reads per boiler automat: `Temperatures` (return, flue gas, flow,
outside) and `Operation` (load, ionisation, pump speed), from RAM / XRAM. Verified on a live bus
against the status telegram each boiler sent in the same minute, one boiler firing, the other idle.

### 4. boiler-fault-counters — depends on boiler-live-values

**Title:** Add Kromschröder/Weishaupt boiler fault counters to src/wolf

Builds on `memr`. One counter per fault number (33 counters, faults 11 to 57) of each WTC boiler
automat, seven memory reads of at most 10 bytes of EEPROM per boiler. Address and fault number from
the symbol table of the automat firmware, meaning from the boiler manual. Verified on a live bus:
the vendor service tool reads the same seven blocks, and its bytes equal the values ebusd decodes
for 32 of the 33 counters of the first boiler (one differs in byte order in the tool's log).

### 5. boiler-info-values — depends on boiler-fault-counters

**Title:** Add Kromschröder/Weishaupt boiler information values (register reads) to src/wolf

The information values the WTC display shows as "i" codes, read with `PBSB 50 22` on both boilers:
flow, return, flue gas, outside and hot-water temperatures, the hydraulic-separator temperature,
and the two software versions (kept as the raw bytes the scan reports as SW). Each was read on both
boilers through ebusd and compared with the automat's own memory values in the same minutes. Only
the files of the boilers change; the pull request stacks on the other boiler changes because they
create those files. It adds the shared read `OutsideTemp` to `wtc_inc`, which the circuit-reads
pull request adds too: the one merged second drops its copy.

### 6. heat-demand-boilers — depends on boiler-info-values

**Title:** Add Kromschröder/Weishaupt heat demand telegrams (05 07) to the boilers to src/wolf

Passive telegrams, builds on the boiler files of the chain before it. The cascade manager (master
`0x10`) sends each boiler automat (master addresses `0x03`, `0x13`) a heat demand about every 20 s,
without an answer: request state, requested flow temperature, modulation demand, hot-water setpoint.
Defined passive in `08.w.bc1` and `18.w.bc2` with a shared model `PowerDemand` in `wtc_inc`.

Verified on a live bus: the modulation demand and the hot-water setpoint equal what the automat
holds in RAM (read with `50 00` in the same minutes); over ten days of telegrams the request state
is `0x66` / `0xee` exactly while the modulation demand is above 0 and `0x55` / `0x00` otherwise.
Bytes without an independent figure stay unnamed (`ukn…`). The room units send the same telegram;
`heat-demand-room-units` adds them with its own copy of the shared model, and the one merged second
drops its copy.

### 7. circuit-reads — depends on #717

**Title:** Add Kromschröder/Weishaupt heating-circuit reads of room units and heating modules to src/wolf

Builds on the register reads of #717.

- New files `75.w.fs2` and `f5.w.fs3`, and reads in `35.w.fs1`: the values and settings of the
  heating circuit of each WCM-FS room unit (heat demand, flow setpoint, outside and room
  temperature; room setpoints, curve, summer / winter changeover, flow limits, hot-water setpoint,
  boost offset, switch-on lead time, frost-protection limit).
- The same circuit reads on the two WCM-EM heating modules (`51.w.em2`, `52.w.em3`) and on the
  system manager's own circuit (`50.w.em1`).

Every register was read on a live bus through ebusd. A room unit and its heating module answer the
same setting registers as independent stores; on the test installation (active-heating test on
circuit 2), the regulation loop follows the room-unit (`fs`) copy.

### 8. heat-demand-room-units — depends on circuit-reads

**Title:** Add Kromschröder/Weishaupt heat demand telegrams (05 07) of the room units to src/wolf

Passive telegrams, builds on the circuit reads (files of the room units). Each WCM-FS room unit
(masters `0x30`, `0x70`, `0xf0`) sends the cascade manager (`0xf1`) a heat demand about every 20 s,
without an answer. Defined passive in `35.w.fs1`, `75.w.fs2`, `f5.w.fs3` with the shared model
`PowerDemand` in `wtc_inc`.

Verified on a live bus: the requested flow temperature equals the room unit's register `b8 02` read
in the same minutes; over ten days the request state is `0xbb`, or `0x55` mostly at night with a low
requested temperature; the modulation and hot-water bytes are the replacement value. The boiler side
is `heat-demand-boilers`, with its own copy of the shared model: the one merged second drops its
copy.

### 9. room-unit-programs — depends on heat-demand-room-units

**Title:** Add Kromschröder/Weishaupt weekly programs of the room units (read side) to src/wolf

Builds on the circuit reads (and, in this chain, on the heat demand of the room units). The five
weekly programs of each room unit (heating 1 to 3, hot water, circulation), one message per
switch-time slot (105 per unit), with the register scheme in the comments. All 315 slots were read
on a live bus. Where a system manager prepares the hot water, the room units only store their
hot-water and circulation programs; the comments say so.

---

## Writes

The published settings are all on non-boiler controllers — the system manager (`ka`), the heating
modules (`em1`–`em3`) and the room units (`fs1`–`fs3`) — which accept a `50 23` write carrying the
placeholder checksum a stock ebusd sends, and take the value (established on `15`, `35` and `51`,
sources `ff` and `31`, 2026-11-22/23; `evidence/write-methods.md`). So these write lines load **and
take effect** on a stock `ebusd 26.1`. john30/ebusd#1825 (run-time checksum) and
john30/ebus-typespec#8 (`@wcrc`) make the sent checksum correct but are **not required** for these
controllers to accept the write, so the two write topics below can be cut without waiting on
#1825/#8. The boiler automats are never written.

### 10. settings-write — depends on room-unit-programs (#1825/#8 optional, see above)

**Title:** Add Kromschröder/Weishaupt setting writes (`50 23`) to src/wolf

- A register write is `PBSB 50 23` with master data `<crc> <address> <value>`, the CRC-8 over
  address and value. When cut without john30/ebus-typespec#8 (`@wcrc`), the write line uses a
  placeholder checksum byte accepted by the non-boiler controllers on stock `ebusd 26.1`; if
  #1825 and #8 are merged first, the template `crcw` and `@wcrc` let ebusd compute the byte at
  runtime. The read line of each setting keeps the precomputed address checksum and stays valid on
  a stock ebusd.
- 89 numeric settings of the system manager, the room units and the heating modules, with ranges
  where the manuals give integer bounds: 66 of the regular settings, the holiday dates of the room
  units (day, month and a third register whose meaning is not established, named so), their control
  variation (parameter 315; values 0 and 1 named in the comment) and the two modulation limits of
  the cascade (parameters 535, 536); five choices with value lists; the date and time broadcast as a
  write.

Each setting was changed by one step on a live bus (the holiday dates kept in the past), read back
with the new value and restored, the telegrams captured; each choice likewise; for the clock, 72 of
72 broadcasts whose time differed from the clock master's were taken over. The devices acknowledge a
write from any master but take most settings only from source address 0xff (the comment of each file
says which).

### 11. programs-write — depends on settings-write (#1825/#8 optional, see above)

**Title:** Add Kromschröder/Weishaupt weekly-program writes to src/wolf

The slots of the five programs of two room units and the two programs of the system manager's own
circuit are written one slot per telegram, read ids unchanged. In each program one slot was changed
on a live bus, read back and restored; the other slots share its codec and register scheme. One room
unit of the test installation acknowledged every slot write and kept none; its programs stay read
only.
