# Test protocol: end-to-end writes with a stock ebusd (room unit & heating module)

**Purpose.** `evidence/write-methods.md` proved two things:
1. On the system manager (`15`), room unit (`35`) and heating module (`51`), the `50 23` checksum
   byte is not checked by the controller (inverted checksum was taken like a valid one).
2. On the system manager (`15.w.ka`, `BlockingTime`), an unmodified stock `ebusd 26.1` with the
   released definitions wrote, read back, and restored the register end to end.

Before deciding whether the installation notice, `ha-weishaupt` write guard, and upstream write PRs
can drop the dependency on `john30/ebusd#1825` for non-boiler controllers, run the same end-to-end
check on **one room unit (`35.w.fs1`)** and **one heating module (`51.w.em2`)** using the stock
`ebusd` add-on (`26.1`, no run-time checksum).

**Safety (rule 7).** Run only by the operator of the installation, in a supervised window, with the
vendor service tool disconnected (no telegram from `ff` in the 15 minutes before). Never write to a
boiler automat (`08`, `18`).

## Pre-checks

1. Confirm no vendor service tool traffic (`QQ = ff`) in the last 15 minutes.
2. Unpack `weishaupt-ebusd-config-1.3.0.tar.gz` into the stock `ebusd` add-on config folder.
3. Stop the Weishaupt `ebusd` add-on, start the stock `ebusd` add-on with
   `--configpath=/config/weishaupt-ebusd-config-1.3.0 --scanconfig --address=31`.
4. Confirm `ebusctl info` shows a stock `ebusd 26.1` (no `-weishaupt` build tag, so no run-time
   checksum) and all 9 Kromschröder files loaded (`08.w.bc1`, `15.w.ka`, `18.w.bc2`, `35.w.fs1`,
   `50.w.em1`, `51.w.em2`, `52.w.em3`, `75.w.fs2`, `f5.w.fs3`).

## Step 1 — Room unit (`35.w.fs1`, `HolidayStartDay`, source `ff`)

Low impact: changes only the stored holiday start day by 1 day for ~10 s, then restores it.

| # | Command | Expected |
|---|---|---|
| 1a | `ebusctl read -f -c fs1 HolidayStartDay` | note initial value `V` (e.g. `30`) |
| 1b | `ebusctl write -s ff -c fs1 HolidayStartDay <V-1>` | `done` (stock ebusd sends placeholder CRC `0d`) |
| 1c | wait 3 s, `ebusctl read -f -c fs1 HolidayStartDay` | `<V-1>` (**taken**) or `V` (not taken) |
| 1d | `ebusctl write -s ff -c fs1 HolidayStartDay <V>` | `done` (restore) |
| 1e | wait 3 s, `ebusctl read -f -c fs1 HolidayStartDay` | `V` (confirmed restored) |

## Step 2 — Heating module (`51.w.em2`, `SupplyMinTemp`, source `31`)

Low impact: moves minimum flow temperature by +0.5 °C for ~10 s, then restores it.

| # | Command | Expected |
|---|---|---|
| 2a | `ebusctl read -f -c em2 SupplyMinTemp` | note initial value `V` (e.g. `8.0`) |
| 2b | `ebusctl write -c em2 SupplyMinTemp <V+0.5>` | `done` (source `31`, placeholder CRC `81`) |
| 2c | wait 3 s, `ebusctl read -f -c em2 SupplyMinTemp` | `<V+0.5>` (**taken**) or `V` (not taken) |
| 2d | `ebusctl write -c em2 SupplyMinTemp <V>` | `done` (restore) |
| 2e | wait 3 s, `ebusctl read -f -c em2 SupplyMinTemp` | `V` (confirmed restored) |

## Step 3 — Heating module (`51.w.em2`, `RoomFrostProtectionTemp`, source `ff`)

Optional confirmation of `-s ff` on a heating module (same low impact: −0.5 °C for ~10 s, then
restore).

| # | Command | Expected |
|---|---|---|
| 3a | `ebusctl read -f -c em2 RoomFrostProtectionTemp` | note initial value `V` (e.g. `10.0`) |
| 3b | `ebusctl write -s ff -c em2 RoomFrostProtectionTemp <V-0.5>` | `done` |
| 3c | wait 3 s, `ebusctl read -f -c em2 RoomFrostProtectionTemp` | `<V-0.5>` |
| 3d | `ebusctl write -s ff -c em2 RoomFrostProtectionTemp <V>` | `done` (restore) |
| 3e | wait 3 s, `ebusctl read -f -c em2 RoomFrostProtectionTemp` | `V` (confirmed restored) |

## Post-steps & decision

1. Stop the stock `ebusd` add-on and restart the Weishaupt `ebusd` add-on.
2. Append the raw telegrams from ebusd's log to `evidence/write-methods.md`.
3. If Steps 1–3 all return **taken**, then **all non-boiler controllers** (`ka`, `em1`–`em3`,
   `fs1`–`fs3`) can be written end to end by a stock `ebusd 26.1` without `john30/ebusd#1825`.
   Decision for the next compatible release (`1.x`):
   - Update `docs/release-readme.md` (stock ebusd suffices for reads and non-boiler writes; fork
     build needed only for `@fills` composite-read distribution).
   - Relax the `capability == "present"` write guard in `ha-weishaupt` (optional, opt-in or
     per-device-type).
   - Submit upstream write PRs to `john30/ebusd-configuration` without waiting on `#1825`.
