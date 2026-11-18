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
value), each citing its record and the day of the capture. It is a transcription and never a
source: a telegram goes into a record first, with how and when it was captured, and only then
into `fixtures.toml`. `scripts/fixtures.py` (step 7 of `scripts/check.sh`) checks that the
bytes and the day of each reading are in its record, that the request is the one of the
definition, and that ebusd decodes the telegram to the recorded value; it also writes the
fixtures file of a release. A record meant to be transcribed keeps request and answer on one
table row, bytes in code marks, the answer without its length byte.
