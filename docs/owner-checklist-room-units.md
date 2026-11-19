# On-site checklist: room units (one page)

For the owner, at the three room units (WCM-FS) of the installation: `fs1` (bus address `35`,
circuit 1), `fs2` (`75`, circuit 2), `fs3` (`f5`, circuit 3). Display only; items 1, 2 and 5
change nothing. Menu names as the French display shows them (manual of the WCM-FS 2.0 /
WCM-EM 2.1, document 83277504). Note what you read in the right-hand column.

**Installer level**: hold the menu key for 3 seconds; turn the knob to page through the menus;
"Fin" leaves without saving. **User level**: a short press on the menu key.

| # | Unit | Menu → parameter | What to note | What each value would mean |
|---|---|---|---|---|
| 1 | `fs1`, `fs2`, `fs3` | Installer → "Mise en service" → **312 "Adresse FS"** (if the unit shows it; the manual sets it only at commissioning or after a reset) | the address shown | "WTC-Chauf.#1": circuit driven directly by a boiler; "EM-Chauff.#2" … "#8": the circuit of heating module #2 … #8 (must equal the address switch of the module); "WTC-Chauf.#1+EM-Chauf.#2": one room unit for two circuits, programs per circuit; "#L": central control (DHW, circulation, clock; no heating regulation). **Expected**: three different addresses, `fs2` "EM-Chauff.#2" and `fs3` "EM-Chauff.#3". A different form on `fs2` is the most likely cause of its refusal |
| 2 | `fs1`, `fs2`, `fs3` | Installer → "Info système" → **335 "Config. FS"**; also 332 "Config WTC" and 336 "Config EM#X" | every line shown | the configuration the unit took at commissioning. Any line where `fs2` differs from `fs3` is the lead |
| 3 | `fs2` | User → "Progr. horaire" → "Progr chauff.1", **Sunday**, third period | change it to 02:00–02:15, OK; tell the session, which reads the slot; then set it back to empty, OK | read back as 02:00–02:15: `fs2` stores programs and refuses only the bus write; not read back: it does not use its own program store (role, item 1) |
| 4 | `fs1` | User → "Vacances" → 141 "Durée" | with the session (batch G, step B): enter 24.12.2026 → 02.01.2027, OK; after the session's reads, **delete the period** | tells what the third register of each date holds (two-digit year if it reads 26 and 27). **Do not leave the period set**: circuit 1 would go to frost protection on 24.12 |
| 5 | `fs3` | Installer → "Mise en service" → 315 "Ty régul#1" | turn the knob through the four settings, note their order, leave with **Fin (no OK)** | the order of "Const. Dép", "Extérieur", "Ambiance", "Exté./Amb." is likely that of the values 0 to 3; 0 and 1 are known, this tells 2 and 3. Optional with the session (step C): select "Ambiance", OK, the session reads, set back "Extérieur", OK — about a minute of room control on circuit 3 |
| 6 | (if the vendor service tool WCM-Diagnose is connected anyway) | its operating-phase legend for the boilers | the name of phase 9, if listed | settles the label `ForcedVenting` |

Items 3, 4 and 5 (optional part) change a setting for a few minutes and are set back by you;
the deployment session only reads. Prepared on 2026-11-19 (`evidence/open-findings-batch.md`).
