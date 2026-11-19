# Pull request text: settings-write

Prepared on 2026-11-19, **not opened**. Branch `upstream/settings-write` of the local clone of the fork (not
pushed), on `upstream/room-unit-programs` (`adef8dd`), head `417feff`; 9 files changed, 566 insertions(+), 127 deletions(-).
`scripts/check.sh` with `CFG_REPO` on the head: clean, seven steps, 661 messages in `ebusd --checkconfig`.

Commits:

- `dad94e3` kromschroeder: write the settings of the system manager, room units and heating modules
- `d5c8066` kromschroeder: add five choices, read and write (ka, fs1, fs2, fs3)
- `4ff744d` kromschroeder: write the date and time broadcast (Broadcast)
- `3e3de20` kromschroeder: read and write the holiday dates of the room units (fs1, fs2, fs3)
- `bc3fd32` kromschroeder: read and write the modulation limits of the cascade (ka)
- `417feff` kromschroeder: read and write the control variation of the room units (fs1, fs2, fs3)

---

## Title

Add Kromschröder/Weishaupt setting writes (50 23, run-time checksum) to src/wolf

## Body

Depends on john30/ebusd#1825, john30/ebus-typespec#8 and the pull request of `room-unit-programs`: the diff of this branch includes their commits until they are merged.

Writes. **Requires john30/ebusd#1825** (ebusd computes the checksum when sending) and
**john30/ebus-typespec#8** (`@wcrc`) to compile; with a stock ebusd the write lines load but the
device gets a wrong checksum.

- A register write is `PBSB 50 23` with master data `<crc> <address> <value>`, the CRC-8 over
  address and value. The template `crcw` and the decorator `@wcrc` leave the byte to ebusd; the
  read line of each setting keeps the precomputed address checksum and stays valid on a stock
  ebusd.
- 89 numeric settings of the system manager, the room units and the heating modules, with
  ranges where the manuals give integer bounds: 66 of the regular settings, the holiday dates
  of the room units (day, month and a third register whose meaning is not established, named
  so), their control variation (parameter 315; values 0 and 1 named in the comment) and the
  two modulation limits of the cascade (parameters 535, 536); five choices with value lists;
  the date and time broadcast as a write.

Each setting was changed by one step on a live bus (the holiday dates kept in the past), read
back with the new value and restored, the telegrams captured; each choice likewise; for the clock, 72 of 72 broadcasts
whose time differed from the clock master's were taken over. The devices acknowledge a write
from any master but take most settings only from source address 0xff (the comment of each file
says which).

Checked with `tsp compile`, `tsp format --check` and `ebusd --checkconfig` (no error). One topic
per commit; the evidence for each definition (captures and their decoding) is kept with the
fork and available on request.
