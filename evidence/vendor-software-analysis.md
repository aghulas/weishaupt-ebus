# Vendor software — static analysis

## What

A read of the vendor's PC software as files: what each program is, where it keeps the parameter
lists of the devices, and how the PC talks to the vendor's eBUS adapter. The registers found are
in [register-candidates.csv](register-candidates.csv), read with
[docs/register-candidates.md](../docs/register-candidates.md). **Nothing here is a definition**
(rule 3): a row of the catalogue becomes one only with a bus read or a manual page of its own.

No vendor program or installer was run. Nothing was sent to a bus. No vendor file, and no
passage of vendor text, is in this repository: the records below state facts (numbers, types,
structures) in our own words. Everything extracted stays in a scratch folder that is not
versioned (`out/vendor-analysis/`), with the throw-away scripts that produced it.

## Method and tools

| Step | Tool |
|---|---|
| Unpacking installers, extraction only | 7-Zip (`7zz`) for the NSIS installer and the MSI; a script for the two installers of the bus monitor and of the driver library (below) |
| File kinds, versions, hashes, exports, resources | Python with `pefile` |
| Delphi forms (resource type RCDATA, binary form format) to text | a script written for it; all 39 forms of the diagnosis program parse to the last byte |
| Delphi class tables (class names, field names with offsets, published methods) | a script that scans the code section for class tables |
| Machine code | the `capstone` disassembler, driven by a script that follows register and stack contents along each function |
| Manuals shipped with the software | `pdftotext` |

## Inventory

"The vendor software folder" is the folder the owner provided; its path is not recorded.

| Item | Kind | What it is |
|---|---|---|
| Diagnosis program 5.5.19, installer | NSIS 2 self-extracting installer (PE32, built 2009-12) | Holds the program, one DLL, 36 symbol files, two INI files, an uninstaller. |
| Diagnosis program, executable | PE32, Delphi (Borland), 4 593 664 bytes, SHA-256 `4311729a…6db29fba` | The service tool. 41 RCDATA resources, 39 of them forms; no version resource. |
| `HL_DLL.dll` | PE32 DLL, Delphi, 316 928 bytes, SHA-256 `44ae56fc…01626364` | Access to a hardware protection key (it imports the key vendor's driver DLL). 16 exports, all about the key: presence, login, access level, counters, stored values. It has nothing to do with the bus. |
| 36 symbol files (`.SYC`) | binary | Symbol tables of the boiler automat firmwares (below). Identical in the installer and beside it. |
| `DL.Ini`, `Cxe.Ini` | INI | Data-logger channels; interface settings (2400 baud, protocol name, PC address 255, flags for echo, DTR, RTS, USB). Already described in [service-tool-log.md](service-tool-log.md). |
| eBUS driver package | `Ebus32.dll` 5.08 (PE32 DLL, Delphi, 60 exports), two configuration tools, a setup program, a Windows 9x virtual device driver, a Pascal interface file, the API manual | The generic PC driver of the eBUS user association, not a Weishaupt product. It serves three kinds of adapter: a passive one through the Windows 9x driver, an active one directly or through a modem, and a point-to-point one. |
| Bus monitor, installer | PE32, an installer of a small vendor ("GP-Install"), payload behind the executable | Unpacked: a generic eBUS monitor 1.22 of the same association, its manual and help file, the driver DLL 5.11 and the Pascal interface file. |
| Driver library, installer | same installer kind | Unpacked: the two configuration tools, the API manual, change lists, the driver DLL. |
| Remote-control software 3.0.28 | MSI built with InstallShield, plus the installed files beside it (MSVC / MFC program, ten language DLLs, a logger DLL, a key DLL, a parallel-port driver, ODBC drivers for Excel) | The controller maker's software for its own controller families, with reporting by text message through the adapter. |
| Modem tool | PE32, Delphi | Sets up a modem. No bus content. |
| Serial-to-USB driver | the chip maker's standard driver package | No bus content. |
| Documentation | PDF | Manual of the service package (adapter, wiring, diagnosis program), a supplement, modem manuals. |

**The loose copies of the executable and of `HL_DLL.dll` in the folder are damaged.** They
differ from the files inside the installer in three places: two runs of bytes of the executable
(one inside a list of device names, one a symbol name) and two bytes of code in the DLL are
replaced by unrelated text, and the files are two and four bytes longer. The installer's copies
are intact (every import and resource parses). Whether the PC used on site runs a damaged copy
is not known; the SHA-256 of the intact executable is the one in the table above. This may be
the cause of the error box and the empty screens noted in the service-tool log, and is worth
one check on that PC. The second build mentioned in that log is not in the folder.

The two "GP-Install" installers keep their payload after the executable as two archives. Each
archive is a list of entries: name length, time stamp, attribute, original size, stored size,
nine more bytes whose first tells stored from compressed, the name, the data. Compressed
entries are LH5 streams; wrapped in an LHA header, 7-Zip expands them to the stated sizes.

## The diagnosis program: where the parameters are

### Two families of devices, two ways to read

| Family | Forms | Read with | Item class |
|---|---|---|---|
| System manager, room units, remote controls with their modules, solar controller | `KA`, `FS` (two forms), `FB`, `SOL` | **registers**: a 16-bit number, the one of the `50 22` / `09 02` reads | one class, 1 249 items created |
| Boiler automats (gas, eight forms by generation; oil) | `WCM…`, `WTO…` | **memory** (`50 00`), by **symbol name** resolved in the symbol file of the firmware | a second class with two descendants, 1 912 items created |

No table of parameters exists as data. Each form creates its items in code, one constructor
call per value shown, and adds them to a list. The arguments of every call were recovered by
following the code: 3 447 calls found by their call instruction (item creations, and the calls
that set limits, special texts and masks), all 3 447 decoded.

**Register item** (constructor arguments, in order): register number; data type; an offset and
a factor (two 64-bit floats; shown value = raw × factor + offset); the screen control; the
kind of control; two formatting numbers; in a second constructor, also the bus address the
value is read from. Data types, from the conversion routine: 0 low byte unsigned, 1 low byte
signed, 2 16-bit unsigned, 3 16-bit signed, 4 16-bit masked (the mask is set by a separate
call), 12 low byte, 13 high byte. Raw `0x8000` is treated apart, as "no value". Two more calls
may follow the creation: one sets a minimum, a maximum and a range text, one sets a text shown
for one special value (for example `--` for -40.0 or -100.0: the "sensor not fitted" values).

**Kind of control** decides how a value list is used: for a drop-down list the shown entry is
the one whose index equals the converted value. So the order of a list in the form is the
value list of the register (index 0 = value 0), unless the factor or offset says otherwise.

**Symbol item**: symbol name; data type; offset and factor; control; kind; formatting; for
parameters also minimum, maximum and an optional range text; the symbol table of the device.
Data types, from the conversion routine: 0 unsigned byte, 1 signed byte, 2 / 3 16-bit unsigned
/ signed with the high byte first, 4 / 5 masked byte unsigned / signed, 6 single bit, 7 / 10
16-bit unsigned / signed with the low byte first, 8 24-bit with the low byte first, 9 a
reciprocal (factor divided by the raw value).

**Labels, units, value lists** are in the forms: captions of the fields (many start with the
vendor's parameter number), units after a separator in the caption, drop-down lists. Each form
also carries its captions in 15 languages in one block. **Access level** is the tab a field is
on (display, user, installer, manufacturer); the manufacturer tabs are opened by the hardware
key or a password dialog. The catalogue takes its level from the tab.

### How a symbol name becomes an address

Read from the routine that resolves a name, and checked against the symbol files:

1. Leading underscores are dropped. The name is looked up in the RAM list: found, it is a RAM
   address (memory area `1` of a `50 00` read).
2. Else in the XRAM list: the low byte of the address is used (area `3`).
3. Else in the bit list: the entry is a bit number; byte = `0x20` + number / 8, mask = 1 shifted
   by number mod 8; the item is forced to the bit type.
4. A name of the form `BASE__SUFFIX` is split: `BASE` is resolved as above, and the **mask** is
   the value stored under the full name in the list of constants. In `WH11928` that list holds
   44 such masks (for example two nibbles of one byte for the functions of two outputs).
5. Names starting with `EEA_` are in the list of constants too and are EEPROM addresses (area `2`).

A symbol file has five lists (RAM, bits, special function registers, constants, XRAM), each a
header, records of name and 16-bit address, and a closing title. The title's tag byte is 0 in
the older files and 1 in the newer ones. All 36 files parse to the end.

**Parameters live twice.** The installer parameters are RAM symbols; the tool reads them from
EEPROM. In `WH11928` the EEPROM address is the RAM address minus `0x90` for the block
`0xab`–`0xe0` (EEPROM `0x1b`–`0x50`, the block the constants list names as the parameter
block, with its checksum at `0x51`). Checked on four values captured from boiler A
([service-tool-log.md](service-tool-log.md)): P31 at `0x1b`, P30 at `0x1c`, P70 at `0x24`,
boiler address at `0x4c`. Decoding the whole captured block with the types, masks and factors
of the form gives a plausible value for every installer parameter (table in
[docs/register-candidates.md](../docs/register-candidates.md)).

### How the program picks the form and the symbol file

From the dispatch routine of the main form (decision points read, not every branch traced):

- The boiler is named by its slave address: `08`, `18`, `38`, `78`, `f8` are automats A to E.
- The identification answer (`07 04`) gives the rest. The file name is a prefix, two
  characters made from the software version byte, and a three-digit board code:
  `00` + version + `360` … `367`, `370`, or `WH` + version + `928` / `370`. The board code and
  the prefix follow from the device, hardware and software bytes of the answer; hardware
  generation 5 gives `WH…928` and the form of the "R5" automat.
- So the two boilers of the test installation (software 11.04, hardware 05.01) use `WH11928`
  and the R5 form; this agrees with the window title noted in the service-tool log.
- A few fixed file names exist for test-bench use. Which of the two room-unit forms a given
  software version gets was not traced.

## The link between the PC and the adapter

Facts, from the service-package manual, the API manual of the driver and the code:

- **The vendor's adapter is an active device**, with its own supply, a microcontroller, DIP
  switches that choose between direct PC connection with high bus priority, direct connection
  with low priority and modem operation, signalling inputs, and settings kept in the adapter.
  The PC is connected by a null-modem RS232 cable (or a serial-to-USB converter).
- **The generic driver DLL is not used for it.** The manual says so, and the diagnosis program
  has two protocol classes: one that calls the driver DLL (passive adapter, Windows 9x only)
  and one of its own for the vendor adapter. The connection dialog of the second offers:
  adapter direct, adapter through a modem, a passive opto adapter, a mobile link.
- **Handshake** of the vendor protocol, 2400 baud. The PC sends short framed requests, ten
  bytes each, that carry a command code and a number, and waits for an answer that repeats
  them with a value: two version reads (their numbers, `01 99` and `01 9a`, are those of the
  version registers 409 and 410 the tool also reads on the bus, so the adapter seems to be
  read like a bus device), a read of the SYN time, then a command that switches the adapter to a **transparent mode**. A code number can
  be required (there is a message for a wrong one). The program takes the first `aa` byte it
  receives as the sign that the transparent mode is active.
- **In transparent mode the PC speaks eBUS itself**: the same unit expands `a9` / `aa` in what
  it sends, computes the CRC, answers telegrams addressed to the PC with an acknowledge byte,
  and has settings for hardware echo, automatic SYN generation, a lock counter and the PC's
  bus address (`00` or `ff`).

Not established: whether the adapter sends the PC's first byte to the bus at once or holds it
until it has won the bus on its own; the delay it adds in each direction; whether the
transparent mode survives a closed port or a power cycle; the meaning of each byte of the ten-byte
requests.

### Could ebusd use this adapter?

Assessment, not a test:

- **Not as it is.** After power-up the adapter expects the vendor handshake; ebusd sends none
  and would receive nothing it understands.
- **Listening is plausible** once something else has switched the adapter to transparent mode
  (a few bytes at 2400 baud before ebusd opens the port), if the mode holds.
- **Sending is doubtful.** ebusd on a plain serial device must put its address on the bus within
  the arbitration window after a SYN and read it back at once. A microcontroller that receives
  a byte from the PC and repeats it adds at least one character time (4.2 ms at 2400 baud) each
  way, which is too late, unless the adapter does the arbitration itself, in which case the
  timing ebusd sees is not the bus timing either. ebusd's own adapter protocol ("enhanced")
  exists for this reason, and this adapter does not speak it.
- The passive opto adapter the dialog also lists is the kind of plain level converter ebusd
  can drive directly; it is a different piece of hardware.

**The capture that would settle it** (owner's PC, no risk for the heating; the tool only
connects and displays): a recording of both directions of the serial port, with time stamps to
the millisecond, while the diagnosis program connects and shows one screen. A software port
monitor on the PC is enough for the content; a logic analyser on the RS232 lines and on the bus
at once is needed for the delay. It shows: the handshake bytes and the answers; whether the
stream after it is the raw bus (SYN bytes, every telegram, the PC's own bytes echoed back);
and how long after a byte from the PC the same byte appears on the bus. A delay well under one
bit time (0.4 ms) would mean a plain converter after the handshake; several milliseconds would
rule out sending with ebusd.

## The other programs

- **Bus monitor and driver library**: generic tools of the eBUS user association. They show
  and send raw telegrams. No device description, no parameter database, in any format.
- **Remote-control software**: parameter pages for the controller maker's own families, built
  as dialog resources and code, with the texts in language DLLs; no database file. Its register
  numbers were not recovered (a different compiler and framework; the method above would have
  to be redone). It is the program that sets up the adapter's text-message reporting.

## Limits

- Static analysis: what the code would do, not what a device answers. A register in the
  catalogue may not exist on a given software version; several forms create an item only when
  a version or configuration test passes, and those tests were not followed. Where a form
  creates two items for one parameter with different factors or ranges, the catalogue keeps
  both.
- The bus address a register is read from is a variable in most items (the unit, or its
  module); the catalogue says "unit" or "module" from the variable used, not from a capture.
- Addresses of boiler symbols are given for `WH11928` only. For the other boiler forms the
  catalogue gives the symbol; the address is in the symbol file of each firmware.
- Meanings are our own short descriptions of the vendor's captions, made with a glossary. Some
  are terse or awkward; a few fields have no caption. The vendor's parameter number is the
  reliable key.
- The program holds no list of operating phases and no fault-text table for the automats other
  than the captions of the statistics tab.

## Date

2026-11-19.
