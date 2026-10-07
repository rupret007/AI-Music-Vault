# events/ — proposed write-back inbox

StoryBoard is the band OS that could emit these. Do not invent a second song
catalog — song ids come from `data/app_api.json`.

These are illustrative formats, not an implemented API. This repo has no event
consumer, validator, automatic catalog merge, or archiver. Reconciliation would
be manual, followed by export regeneration and the normal catalog gate.

This repository is public. Keep real event files, local paths, venue details, and
session notes outside it; do not commit them to this proposed inbox. Placeholders
below describe the intended shape, not current catalog records.

**Show played** (Rad Dad Show Night / any gig):
```json
{"event":"show_played","date":"YYYY-MM-DD","band":"<band>","venue":"<venue>",
 "songs":["<vault-id>"]}
```

**New bounce/version** (WebJam Reference Studio, Logic, anywhere):
```json
{"event":"bounce","song":"<vault-id>","version":"<version>","date":"YYYY-MM-DD",
 "path":"<local-only-path>","sha256":"<checksum>"}
```

**Jeff's verdict on a memo** (the listen queue):
```json
{"event":"verdict","memo":"<local-intake-name>","song_id":"<vault-id>",
 "verdict":"gem","note":"<local-only-note>"}
```

Why this matters: a verified played-set event or bounce checksum could supplement
the existing catalog's setlist evidence and file dates. An unverified event does
not establish a fact or automatically update momentum. Proposed convention: one
file per event, any filename.
