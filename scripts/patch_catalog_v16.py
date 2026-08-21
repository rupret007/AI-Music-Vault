#!/usr/bin/env python3
"""Catalog patch v1.6 — the Discovery Pass (lyric docs + session transcripts + public web)."""
import json

CAT = '/home/claude/vault/00_control_room/master_catalog.json'
cat = json.load(open(CAT))
idx = {s['song_id']: s for s in cat['songs']}
YES = 'YES — Jeff-written; SOLO recordings only (band performances never upload), private, logged'

def S(song_id, title, **kw):
    base = dict(song_id=song_id, canonical_title=title, artist_project='Jeff Story',
                classification='original', alt_titles=[], writers=['Jeff Story'],
                rights_confidence='high', stage='voice memo only (recovered 2026-08, discovery pass)',
                sources=[], soundcloud=[], theme='', hook='', potential=None, readiness=None,
                confidence='medium', audio_status='transcription only — NOT listened to',
                lyric_status='partial — recovered from memo transcript, garbled in spots',
                next_action='', ai_involvement='none (transcription only)', open_questions=[],
                notes='', ai_upload_ok=YES)
    base.update(kw); return base

new = [
S('JS-0139','A New Hope (working title)',
  theme='Star Wars-framed longing — "she\'s a girl out of my dreams... The princess... Every night I fall asleep with you, and then I wake up alone." Nerd-romance with real melancholy; "forty-five years" = a Jeff-age receipt (45 in 2024).',
  hook='"Every night I fall asleep with you, and then I wake up alone"',
  notes='Memo "A new hope 11-20-2024" (2:21) — real sung lyric throughout. Candy-thread adjacent with a genre frame — the same trick as Over 40\'s cop twist applied to romance.',
  next_action='LISTEN: the 11-20-2024 memo. Gem verdict.'),
S('JS-0140','Anthem Part 2 (working title)',
  theme='Protest — "Everything is [falling] to pieces... Corporate leaders, politicians... We\'ve been [waiting/dying] for that long time" (chorus recurs 5+ times). THE STATE thread.',
  hook='"We\'ve been ___ for that long time" (chorus phrase garbled — needs ear)',
  notes='Memo "Anthem Part 2 10-24-24" (3:47). Title implies an "Anthem Part 1" — possibly Good Charlotte\'s The Anthem (in the Rad Dad set) as the joke referent, or an earlier Jeff song. Ask when it comes up.',
  next_action='LISTEN: the 10-24-24 memo; catch the real chorus words.'),
]
for s in new:
    assert s['song_id'] not in idx
    cat['songs'].append(s)

# ---- updates ----
b = idx['JS-0107']  # Blue Skies Fade
b['lyric_status'] = 'OPENING MOVEMENT RECOVERED from "Blue skies beginning" memo transcript (2024-07-27): "Hello boy, won\'t you come out to play?... we make them fly into the blue sky / Where we all shall be?" + child/fear/paralysis imagery in the verses. Suite text also exists in Drive docs.'
b['notes'] = (b.get('notes','') + ' DISCOVERY PASS: the 2024 memo preserves the opening as SUNG in 2024 — the opus\'s current living form, not just the 1999 text.').strip()

bw = idx['ST-0007']  # Be With You
bw['stage'] = (bw.get('stage','') + ' + RELEASED v2.5 on "Another Bland EP" (SoundCloud, 2023-05-21)').strip()
bw['notes'] = (bw.get('notes','') + ' DISCOVERY PASS: NOT homeless — released Jan 2023 (v2.5) on the Another Bland EP (SoundCloud). The "next-record centerpiece" framing stands, but a public version exists.').strip()

ab = idx['ST-0032']  # Another Bland Love Song
ab['stage'] = (ab.get('stage','') + ' + TITLE TRACK of "Another Bland EP" (SoundCloud, 2023-05-21)').strip()
ab['notes'] = (ab.get('notes','') + ' DISCOVERY PASS: EP tracklist = Another Bland Love Song / The Way I Love You v2.5 / TBFH v4.5 / Be With You v2.5 / It\'s Been Only 18. The 2023 ancestor of the current album push.').strip()

cg = idx['SD-0007']  # Cigarettes In A
cg['potential'] = 68
cg['hook'] = '"Except for my friend(s) / Accept this my friend" (closing homophone twist)'
cg['theme'] = 'Smoking through the silence after a rupture — "quiet room laughs at me... it\'s been 3 days and still it\'s quiet, except for my friends."'
cg['lyric_status'] = 'FULL LYRIC READ (Drive doc, 2023-05-09): 2 verses + chorus + homophone outro. Complete.'
cg['notes'] = (cg.get('notes','') + ' DISCOVERY PASS: lyric finally read — scored 68 (hook 17 lyric 14 truth 15 structure 11 identity 6 replay 5). "Last dance with Savannahs" = unexplained specific, ask Jeff sometime. v6.9 Logic project + played live SD 2023 — this song is closer to done than its paper trail suggested.').strip()

rh = idx['ST-0030']  # Rabbit Hole
rh['notes'] = (rh.get('notes','') + ' DISCOVERY PASS: Drive doc "My muse abuse" (2021-04-06) shares its core image — "What used to be bright is now absent of light / And down the rabbit hole we go" + "unwanted calls and silver balls / pink sweaters that no longer matter." Likely the same song\'s seed or a sibling. Linked.').strip()

ht = idx['JS-0054']  # Hey There (adaptation)
ht['notes'] = (ht.get('notes','') + ' DISCOVERY PASS: full adaptation text read (Mexico City / Saint Angel / "pay the bills with this guitar"). Doc created 2021-03-23 — the SAME DAY the "Don\'t Put Your Life Away" memo cluster began, suggesting JS-0132 germinated from playing with the Delilah form that day.').strip()

ite = idx['ST-0018']  # In The End
ite['lyric_status'] = 'FRAGMENT ONLY (Drive doc): 93 BPM + 4 lines ("Thoughts shed on broken glass / You\'d think these feelings would pass..."). Rest of lyric uncaptured — Rhodes studio recording exists; transcribe from audio later.'

mw = idx.get('ST-0027')  # Morgan/MJ the Wizard
if mw:
    mw['notes'] = (mw.get('notes','') + ' DISCOVERY PASS: "Music Hall at Fair Park" memo (2023-11-25, 43 min) decoded = audience/backstage audio from MJ the Musical in Dallas (king-of-pop dialogue throughout) — an attended show, NOT catalog material; possible inspiration context for the MJ the Wizard title only.').strip()

cf = idx['JS-0105']  # Country Fried
cf['notes'] = (cf.get('notes','') + ' DISCOVERY PASS: "Country road rough" memo (2026-07-29 — the newest music in the vault) is a Take Me Home Country Roads rework sketch ("Don\'t you roll, take me home") — likely this thread continuing. Cover-derived: keep off AI tools.').strip()

cat['version'] = '1.6'
cat['updated'] = '2026-08-20'
json.dump(cat, open(CAT,'w'), indent=1)
print('v1.6:', len(cat['songs']), 'entities')
