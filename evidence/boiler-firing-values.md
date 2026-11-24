# bc1, bc2 — boiler values captured with the burner firing (read)

## What

The boiler-automat values of `evidence/bc-live-values.md` that are zero or absent with the burner
idle, captured while boiler `18` (bc2) fired on 2026-11-22. This session only **read** the bus
(`PBSB 50 00` memory reads and `50 22` register reads), never wrote to a boiler or controller
(rule 7), and never triggered the fire. The fire was a **natural heating-circuit demand**: the
operator's concurrent DHW test (DHW comfort setpoint raised 50→60 from source `ff`) did **not**
cause it — the active DHW target stayed 8.0 °C in the reduced-DHW window and the burner did not
start for DHW (confirmed by the deploy session). So the captured burner-on window is a heating
cycle, not DHW. Firing was sampled over ~18:40:54–18:43:41 (ignition then established flame);
the boiler was idle again by 19:24 (the exact stop time was not sampled — the reader hit bus/socket
errors in between). Boiler `08` (bc1) stayed idle throughout and gives the idle reference.

This completes the firing-dependent items of the *Info* menu left open in
`evidence/bc-info-values.md` ("What is left out") and the firing-only RAM/XRAM channels left out
in `evidence/bc-live-values.md`.

| i (manual) | meaning | memory / register | model | idle | ignition | firing |
|---|---|---|---|---|---|---|
| i 11 | burner power / load | XRAM `f0b2` (`56 03 b2`) | `Load` (UCH %) | 0 | 23 | 25 |
| i 22 | pump speed | RAM `ed` (`b1 01 ed`) | `PumpSpeed` (UCH %) | 0 | 50 | 51 |
| i 32 | ionisation current | XRAM `f0d5` (`31 03 d5`) | `Ionisation` (UCH /10) | 0.0 | 0.0 | 12.1–12.7 |
| i 23 | fan speed set | XRAM `f0de` (`3a 03 de`) | `FanSpeedSet` (UCH) | 0 | 40 | 23 |
| i 23 | fan speed actual | RAM `77` (`2b 01 77`) | `FanSpeedActual` (UCH) | 0 | 34 | 23 |
| i 23 | fan PWM | RAM `7e` (`22 01 7e`) | `FanPWM` (UCH %) | 0 | 53 | 27 |
| i 30 | eSTB (flow safety limit) | RAM `5e` (`02 01 5e`) | `eSTBTemp` (SCH °C) | ≈flow | ≈flow | flow+1–3 |

Operating-state and output bytes (both `50 00` RAM reads), firing vs idle:

| byte | memory | idle (deep) | standby | ignition | firing |
|---|---|---|---|---|---|
| operating code | RAM `70` (`2c 01 70`) | `0x20` (32) | `0x00` | `0x0e` (14) | `0x0f` (15) |
| outputs | RAM `2b` (`77 01 2b`) | `0x00` | `0x80` | `0xf0` | `0xfd` |

## Live capture — boiler 18, 2026-11-22

Read-only through the ebusd `hex` command (`50 00` / `50 22` only), source `31`, answers after the
length byte (status byte `00` for `50 00`, two value bytes for `50 22`). One guarded reader; a
small number of reads returned a bus error ("timed out"/"broken pipe") and were skipped, as noted
in `evidence/bc-live-values.md` for the same `50 00` path.

| time | state | Load i11 | Ion i32 | Pump i22 | FanSet | FanAct | FanPWM | eSTB | RAM70 | RAM2b | flow | flue |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 18:39–18:40 | idle | 0 | 0.0 | 0 | 0 | 0 | 0 | 57 | `0x20` | `0x80` | 56 | 47 |
| 18:40:54 | ignition | 23 | 0.0 | 50 | 40 | 34 | 53 | 50 | `0x0e` | `0xf0` | 51 | 48 |
| 18:42:30 | firing | 25 | 12.1 | 51 | 23 | 23 | 27 | 60 | `0x0f` | `0xfd` | 59 | 53 |
| 18:43:41 | firing | 25 | 12.7 | 51 | 23 | 23 | 27 | 63 | `0x0f` | `0xfd` | 62 | 56 |
| 19:24–19:25 | idle | 0 | 0.0 | 0 | 0 | 0 | 0 | 56 | `0x20` | `0x80`/`0x00` | 55 | 47 |

Raw frames (boiler 18, firing at 18:43:41; `request` → `answer`):

```
Load i11        ff 18 5000 03 56 03 b2  →  02 00 19   = 25 %
Ionisation i32  ff 18 5000 03 31 03 d5  →  02 00 7f   = 12.7  (0x7f /10)
PumpSpeed i22   ff 18 5000 03 b1 01 ed  →  02 00 33   = 51 %
FanSpeedSet     ff 18 5000 03 3a 03 de  →  02 00 17   = 23
FanSpeedActual  ff 18 5000 03 2b 01 77  →  02 00 17   = 23
FanPWM          ff 18 5000 03 22 01 7e  →  02 00 1b   = 27 %
eSTB i30        ff 18 5000 03 02 01 5e  →  02 00 3f   = 63 °C
OpCode          ff 18 5000 03 2c 01 70  →  02 00 0f   = 0x0f
Outputs         ff 18 5000 03 77 01 2b  →  02 00 fd   = 0xfd
```

Ignition moment (18:40:54), the same requests: Load `17`=23, Ion `00`=0.0 (no flame yet),
Pump `32`=50, FanSet `28`=40, FanAct `22`=34, FanPWM `35`=53, eSTB `32`=50, OpCode `0e`,
Outputs `f0`.

### Grouped FanOperation read (the three fan bytes in one memory read)

The three fan channels are read in one `50 00` memory read with the ID `56 03 de 01 77 01 7e`
(CRC `56` over the items; the grouped read was verified on the bus and answers one status byte
then the three bytes, like `Operation`):

```
request                   answer (NN, status, set, actual, pwm)      set / actual / pwm
56 03 de 01 77 01 7e      04 00 00 00 00                              0 / 0 / 0     (idle, captured)
56 03 de 01 77 01 7e      04 00 28 22 35                              40 / 34 / 53  (ignition)
56 03 de 01 77 01 7e      04 00 17 17 1b                              23 / 23 / 27  (firing)
```

Provenance: the idle grouped answer `00 00 00 00` (bytes after the length byte) was captured
directly as a grouped read. The ignition answer `00 28 22 35` and the firing answer `00 17 17 1b`
are composed from the single-item reads above (FanSet XRAM `de`, FanAct RAM `77`, FanPWM RAM `7e`,
same memory bytes in the same order the grouped read returns them): `28 22 35` = 40/34/53 at
ignition, `17 17 1b` = 23/23/27 firing. No firing-time grouped telegram was captured as one frame;
the burner was idle again before one could be taken.

## How it was established

1. **CRC.** The first ID byte of every `50 00` item (`<crc> <code> <addr>`) and every `50 22`
   register (`<crc> <addr> <sub>`) was recomputed offline (CRC-8 poly 0x5C, per
   `evidence/register-crc.md`) and matches the frame sent; the reader self-tests against 22
   register mappings and 6 memory-item mappings before any bus read.
2. **Addresses, codecs.** From `evidence/bc-live-values.md` (vendor data-logger channel table,
   WCM-Diagnose 5.5.19a): Load/PumpSpeed/FanPWM unsigned bytes gain 1, Ionisation unsigned gain
   0.1, eSTB signed byte; the fan speed-set/actual are the data-logger channels "speed set" (XRAM
   `de`), "speed actual" (RAM `77`) left out there for want of a firing read.
3. **Firing confirmation.** Each firing-only value is 0 (or ≈flow for eSTB) with the burner idle
   on both boilers and takes a coherent value only while boiler 18 fires: ionisation 0.0 until the
   flame, then 12.1–12.7 (on the scale of the fault-history ionisation slots, 14–20); load 23–25;
   pump 50–51; fan set = actual = 23 (closed-loop) with PWM 27 steady, 40/34/53 during ignition
   purge. Flow and flue gas rise through the cycle as expected.
4. **Cross-check with the status telegram.** Boiler 18's `10 500a` status telegram in the firing
   minutes carried load `19` (25 %) and flow ~`72`–`78`, equal to the memory reads, as in
   `evidence/bc1-boiler-status.md`.

## Findings on the two state bytes

- **RAM `70` (operating code).** Four values seen: `0x20` (32) idle, `0x00` deep standby/off,
  `0x0e` (14) during ignition/pre-flame, `0x0f` (15) with the flame established. This is not the
  operating phase of the status telegram (6 firing, 0 idle). The 2026-11-17 discovery read `13`
  firing; this capture reads `15`, so the code distinguishes ignition (14) from steady firing (15)
  and the earlier figure was a different sub-state. Idle `32` reproduced.
- **Outputs RAM `2b`.** Four states now tell the transitions apart (the 2026-11-17 note only had
  `fd` firing / `80` idle, "all change together"):
  - off `0x00` → standby `0x80`: bit 7 sets (controller ready).
  - standby `0x80` → ignition `0xf0`: bits 4,5,6 set (fan / pump / ignition-stage outputs).
  - ignition `0xf0` → firing `0xfd`: bits 0,2,3 set, bit 1 stays clear (gas valve(s) / flame
    stage). The exact output wired to each bit is not proven here (no service-tool output view),
    but each transition toggles a distinct group, so the byte is a usable output bitfield.

## What can be defined vs what still needs more

- **Definable now** (firing proof in hand, read-only, on `08`+`18` models): `FanSpeedSet`,
  `FanSpeedActual`, `FanPWM` (i 23) — the three fan channels of the data logger, previously left
  out. They join `Load`, `Ionisation`, `PumpSpeed` already defined in `evidence/bc-live-values.md`,
  which this capture confirms with a live flame (ionisation 12.x, load/pump non-zero).
- **eSTB RAM `5e` (i 30).** Confirmed to track the flow (+1–3 K) through the fire; still no
  independent displayed figure to pin the exact offset. Can be defined as a flow-safety temperature
  (`SCH`, °C) with that caveat, or kept out as before — a judgement for the integration step.
- **RAM `70` operating code.** Observed values `0x20`/`0x00`/`0x0e`/`0x0f`; a full value list
  (every phase) needs more firing states (DHW vs heating, modulation sweep). Define as a raw
  `UCH`/`HEX` state byte with the four observed values noted, or defer for a complete list.
- **i 42 burner starts (`27 02`, `50 22`).** Read 543 on `18` before, during and after the fire
  (one start does not cross a 1/256 boundary). Confirms the "starts / 256" reading of
  `evidence/bc-info-values.md`; lot D already holds the full counter, so nothing new to define.
- **Still needs the burner firing (more time).** Boiler `08` (bc1) did not fire, so the fan/flame
  values are proven on `18` only (the models are shared). A heating-mode fire (not DHW) and a
  modulation sweep would fill the RAM `70` value list and a higher-load point.

## Equipment

Two WTC condensing boiler automats on eBUS (slaves `08`, `18`), scanning
`MF=Kromschroeder;ID=W?;SW=1104;HW=0501`, in cascade under a WCM system manager. Read-only; no
write was sent (rule 7). The burner-on window was a natural heating-circuit demand (not the
operator's concurrent DHW-setpoint test, which did not start the burner).

## Date

2026-11-22.

## Not verified

- Fan speed unit (set/actual read 23 = 23, closed-loop, but the engineering unit — rpm, % of max
  — is not known; the PWM is a drive percentage per the data-logger channel).
- Exact bit→output map of RAM `2b` (no service-tool output screen to compare); only the state
  transitions above are established.
- RAM `70` is not a complete value list; only idle/standby/ignition/firing seen, on a DHW fire.
- eSTB offset above flow not pinned to a displayed figure.
- All firing values proven on boiler `18` only; `08` stayed idle this window (shared models).

## Follow-up (2026-11-24)

Live `ebusd` reads (`read -f`) captured in the grab buffer (`ebusd` `v26.1-weishaupt.2`, read-only):

- `bc1` (`08`, idle): `31 08 50 00 07 56 03 de 01 77 01 7e / 04 00 00 00 00` → `FanOperation` = `0;0;0;0`
  (`firstbyte=0`, `fanspeedset=0`, `fanspeedactual=0`, `fanpwm=0`).
- `bc2` (`18`, firing): `31 18 50 00 07 56 03 de 01 77 01 7e / 04 00 25 25 33` → `FanOperation` = `0;37;37;51`
  (`firstbyte=0`, `fanspeedset=37`, `fanspeedactual=37`, `fanpwm=51`).
