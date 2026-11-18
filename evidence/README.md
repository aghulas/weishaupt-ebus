# Evidence

One Markdown file per topic (`<circuit>-<topic>.md`), so a reviewer can see why a definition is right.

Each record states:

- **What**: message name, ID, codec, value list
- **How it was established**: bus read (command and raw answer), manual (title, document number,
  page), or comparison with the vendor service tool
- **Equipment**: device type, software version as reported by the bus scan
- **Date**
- **Not verified**: what remains an assumption

Rules:

- Raw telegrams are welcome; trim them to what proves the point.
- Nothing site-specific: no names, addresses, host names or serial numbers.
- No copies of vendor manuals or vendor software. Cite title, document number and page.

`fixtures.toml` holds readings transcribed from these records (request, answer, decoded
value), each citing its record; `scripts/metadata.py fixtures` checks them against the record
and the definition and writes the fixtures file of a release.
