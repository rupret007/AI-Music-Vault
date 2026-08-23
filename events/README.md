# events/ — what the apps write back to the vault

StoryBoard is the band OS that should emit these. Drop files here; do not
invent a second song catalog — song ids come from `data/app_api.json`.

Drop-file inbox. Apps (or Jeff) write small JSON events here; the next Claude
session folds them into the catalog and then archives them.

**Show played** (Rad Dad Show Night / any gig):
```json
{"event":"show_played","date":"2026-09-14","band":"Rad Dad","venue":"...",
 "songs":["Drinking Song","Everyday","The Way I Love You"]}
```

**New bounce/version** (WebJam Reference Studio, Logic, anywhere):
```json
{"event":"bounce","song":"Manic","version":"v1.5","date":"2026-09-01",
 "path":"...","sha256":"..."}
```

**Jeff's verdict on a memo** (the listen queue):
```json
{"event":"verdict","memo":"Crescent Dr 56","song_id":"JS-0131",
 "verdict":"gem","note":"that's actually the one I was humming all fall"}
```

Why this matters: live-set history and version history are currently *inferred*
from file dates. Events make them **facts** — which makes the momentum score
real rather than estimated. One file per event, any filename.
