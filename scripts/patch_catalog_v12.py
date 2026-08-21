#!/usr/bin/env python3
"""Catalog v1.2 — folds in: Jeff's rights answers (2026-08-18), 916 Voice Memos (matched),
deep-corner Drive enumeration (622 records), Dustin Duffy stems, J&C Nov-2024 demos."""
import json, collections, re, datetime

cat = json.load(open('/home/claude/vault/00_control_room/master_catalog.json'))
idx = {s['song_id']: s for s in cat['songs']}
by_title = {s['canonical_title']: s for s in cat['songs']}

# ---------- 1. RIGHTS ANSWERS FROM JEFF (verbatim decisions) ----------
s = idx['ST-0002']  # The Way I Love You
s['classification'] = 'outside composition — written by Paco Estrada, given to the band'
s['writers'] = ['Paco Estrada']
s['rights_confidence'] = 'performance rights OK per Jeff ("ours as Paco gave it to us"); composition credit = Paco Estrada. NO external/AI upload without revisiting rights.'
s['potential'] = None  # leaves the Jeff-originals ranking
s['open_questions'] = 'Was the song "given" informally or with any written understanding? Matters only if the album is commercially released.'
s['notes'] += ' RIGHTS RESOLVED 2026-08-18 (Jeff): Paco Estrada wrote it and gave it to the band. Stays album track 2; removed from Jeff-originals ranking; credit Paco on release.'

s = idx['ST-0005']  # Better Than Now
s['classification'] = 'band original — written by Sean (Stalemate bassist)'
s['writers'] = ['Sean (Stalemate bassist)']
s['rights_confidence'] = 'Sean\'s composition per Jeff. Band may record/perform; no external/AI upload without Sean\'s consent.'
s['open_questions'] = 'Sean\'s full name for credits; does he have the lyric written down? (replaces the "who wrote it" question)'
s['notes'] += ' RIGHTS RESOLVED 2026-08-18 (Jeff): Sean wrote it. Lyric-capture task now points at Sean.'

s = idx['ST-0009']  # Long Long Drive — confirmed Jeff's
s['rights_confidence'] = 'high — CONFIRMED by Jeff 2026-08-18: "long long drive is my song, i wrote it"'

for i in range(1, 14):  # Dustin Duffy songs
    u = idx.get(f'UNK-{i:04d}')
    if u:
        u['artist_project'] = 'Dustin Duffy (Stalemate Split)'
        u['classification'] = 'Dustin Duffy composition (Jeff\'s bandmate/buddy)'
        u['writers'] = ['Dustin Duffy']
        u['rights_confidence'] = 'Dustin\'s songs per Jeff 2026-08-18. Catalog as collaborator material; never rank as Jeff originals; no external use without Dustin.'

# Trailer Swift note
cat.setdefault('project_identities', {})['Trailer Swift'] = (
 'Jeff\'s SOLO project (per Jeff 2026-08-18) — Taylor Swift covers arranged/performed by Jeff. '
 'Rad Dad and Stalemate have also played these songs live. Compositions remain covers (excluded from originals ranking); '
 'the recordings/arrangements are Jeff\'s work product. Finished album: Trailer Swift FINAL/MP3+WAV, 13 tracks, 2025-07-09.')

# ---------- 2. VOICE MEMOS ----------
vm = json.load(open('/home/claude/vault/01_source_manifests/voicememo/vm_matches.json'))
recs = json.load(open('/home/claude/vault/01_source_manifests/voicememo/voice_memo_db_inventory.json'))
uid2rec = {r['uid']: r for r in recs}
for sid, uids in vm.items():
    s = idx.get(sid)
    if not s: continue
    dates = sorted(uid2rec[u]['date'] for u in uids if u in uid2rec)
    s['sources'].append(f'Voice Memos: {len(uids)} recordings ({dates[0]}..{dates[-1]}) — in Voice Memo Intake on Jeff\'s Mac')
    s['notes'] += f' VOICE MEMOS: {len(uids)} matched ({dates[0]} to {dates[-1]}).'

# ---------- 3. STATUS UPGRADES from deep-corner enumeration ----------
up = {
 'ST-0028': ('The Prime Outline EXISTS: 10 voice memos (2024-02..2025-05) + J&C The Prime Outline v2.1.wav (Nov 2024 demo w/ Che) + The Prime Outline v1.3.logicx (Dec 2024). Stage: developed demo, was wrongly "title only".', 'demo + logic project'),
 'ST-0027': ('Morgan The Wizard = the "MJ the Wizard" Logic lineage: v2.0 (2022) -> v3.0 (2023) -> v4.2 (2024) + 9 voice memos. A long-развиваемая song, not a stub.', 'multiple logic versions'),
 'ST-0110': ('Andrea revival found: Stalemate - Andrea v1.2.logicx + v1.3.wav (Jul 2023), "Ne Andrea"/"Hey There Andrea" projects, 2023 remaster of the 2010 track. ALSO: Dustin Duffy holds an "andrea lyrics" doc — SAME song, same words/chords (his copy or old co-write? ask casually).', 'released 2010 + 2023 remaster + 2023 re-arrangement'),
 'ST-0016': ('Crisis Averted folder 11: chart in 2 keys + practice + studio takes confirmed.', None),
 'ST-0017': ('Chart read: Key Cm, 84 BPM — a slow dark one. Studio take exists (different key).', None),
}
for sid,(note,stage) in up.items():
    idx[sid]['notes'] += ' ' + note
    if stage: idx[sid]['stage'] = stage

idx['ST-0006']['notes'] += ' Older Take This Step v1.1/1.2 logicx (2023) + Crisis Averted studio take exist.'
idx['ST-0010']['notes'] += ' 2023 remaster WAV exists (My Mom Says We\'re Cool/2023).'
idx['ST-0011']['notes'] += ' 2023 remaster WAV exists.'

# Dustin bass lines note on relevant songs
for sid in ['ST-0003','ST-0010','ST-0002','ST-0006','ST-0017','ST-0027']:
    idx[sid]['notes'] += ' Dustin Duffy recorded bass lines for this song (Stalemate Split/Bass Lines, 2023-12..2024-01).'

# Dustin stems folders now have BPMs — update UNK entries
bpms = {'Catharsis':185,'Deadweight':170,"She's Not All There":155,"Rockin' R":190,'Scapegoat':165,
 'Searching':155,'Guns, Glory and Goners':85,'Fool':175,'Rock Brigade':180,'mp3.com':145,"Captain Freedom's Workout":160}
for u in cat['songs']:
    if u['song_id'].startswith('UNK-') and u['canonical_title'] in bpms:
        u['bpm'] = str(bpms[u['canonical_title']])
        u['sources'].append('Stalemate Split/Stems/<song> <bpm>bpm folder (Aug 2025 — ACTIVE project)')

# ---------- 4. NEW SONG ENTITIES ----------
def S(id, title, artist, cls, **kw):
    return dict(song_id=id, canonical_title=title, artist_project=artist, classification=cls,
        alt_titles=kw.get('alt',[]), writers=kw.get('writers',['Jeff Story']),
        rights_confidence=kw.get('rights','high'), stage=kw.get('stage','cataloged'),
        lyric_pct=None, music_pct=None, rec_pct=None, key=kw.get('key',''), bpm=kw.get('bpm',''),
        sources=kw.get('src',[]), soundcloud=[], earliest_known=kw.get('early',''), latest_version=kw.get('late',''),
        best_source=kw.get('best',''), theme=kw.get('theme',''), hook=kw.get('hook',''),
        version_count=kw.get('vc',1), potential=None, readiness=None,
        confidence=kw.get('conf','low'), audio_status='metadata only', lyric_status=kw.get('lys','not read'),
        next_action=kw.get('next',''), ai_involvement='none', open_questions=kw.get('oq',''), notes=kw.get('notes',''))

new = [
 S('JS-0100','Airtime','Jeff Story','original', src=['Prime Outline "in development"','Voice Memos: 6 recordings titled Airtime'], notes='Exists only as voice memos — hidden-gem listen queue.'),
 S('JS-0101','Shine On Through The Darkness','Jeff Story','original', alt=['Shine On'], src=['Shine On v1.0.logicx (2024-12)','Voice Memos: ~5 (Shine On / Shine On Through The Darkness)','Prime Outline in-development'], notes='Logic project + memos — real song, unread/unheard.'),
 S('JS-0102','Suddenly Stranded','Jeff Story','original', src=['Suddenly Stranded v1.0.logicx (2024-12)','Voice Memos: 2'], notes=''),
 S('JS-0103','Political Circus','Jeff Story','original', src=['Political Circus v1.0.logicx (2024-12)','Prime Outline in-development'], notes=''),
 S('JS-0104','Run Away','Jeff Story','original', src=['Run Away v1.0.logicx (2022, Logic folder)','Voice Memos: ~3 "Runaway"'], notes=''),
 S('JS-0105','Country Fried','Jeff Story','original', alt=['Chicken Fried','Sunburnt Country?'], src=['Country Fried v1.0.logicx (2022)','Chicken Fried v1.0.logicx (2022)','Sunburnt Country v1.0.logicx (2022)'], oq='One song or three? Country/novelty direction — ask Jeff.', notes=''),
 S('JS-0106','Four Walls','Jeff Story','original', src=['1. Intro and Four Walls v1.0.logicx (2023-03)'], notes='Numbered "1." — part of a planned sequence?'),
 S('JS-0107','Blue Skies Fade','Jeff Story','original', src=['Blue Skies Fade 2024 v1.0.logicx (2024-07)'], notes=''),
 S('JS-0108','Home on the Lake','Jeff Story','original', src=['Home on the Lake v1.0.wav (2024-12)'], notes='Finished-sounding demo mix, no other trace.'),
 S('JS-0109','Champ Elysisis','Jeff Story','original', src=['Champ Elysisis.logicx (2024-12)'], notes='Title sic (Champs-Élysées?). Unknown content.'),
 S('JS-0110','Dah','Jeff Story','original', src=['Dah v1.0.wav (2019, Tracks Backup)'], notes=''),
 S('JS-0111','Everything\'s Beautiful','Jeff Story','original', src=['Everything\'s beautiful 2.m4a (2019, Tracks Backup)'], notes=''),
 S('JS-0112','Home','Jeff Story','original', src=['Home.m4a (2019, Tracks Backup)'], notes=''),
 S('JS-0113','Bom Bom','Jeff Story','original fragment', src=['Bom bom.m4a (2019)'], notes=''),
 S('UNK-0200','Your New Boyfriend','Travis Story','collaborator material', writers=['Travis Story'], rights='Travis\'s song', src=['Travis Story - Your New Boyfriend.logicx (2022)','Travis Set (2016)','Travis Worsham Songs doc (2010)'], oq='Travis Story / Travis Worsham — brother? bandmate? clarify relationship for the catalog.', notes=''),
 S('UNK-0201','TAD project (Wrapped in Linen / Rise of the Unicorn)','Dustin Duffy (TAD)','collaborator material', writers=['Dustin Duffy'], rights='Dustin\'s project', src=['dustduff90 shared: Full Mixes + Stripped Mixes (2024-12..2025-03)'], notes='Separate Dustin project shared with Jeff.'),
]
existing_titles = {s['canonical_title'].lower() for s in cat['songs']}
for n in new:
    if n['canonical_title'].lower() not in existing_titles:
        cat['songs'].append(n)

# ---------- 5. Unmatched voice memo pool entity note ----------
cat['voice_memo_pool'] = dict(
  total=916, matched=326, matched_songs=73, unmatched=590,
  location_named_untitled=collections.Counter(),  # summarized below in note
  note=('590 unmatched memos: ~290 carry location-default names (Maxwell Dr ~196, Crescent Dr ~60, Briar Creek Ln 8, '
        'Merlin Ct 8, Sundown Blvd 7, ...) = UNTITLED IDEAS, the hidden-gem pool for transcription/listening. '
        'Named-but-unmatched include: Airtime (6), Shine On (5), Suddenly Stranded (2), Castle chorus take (2), '
        'Time machine bridge (2), New ska song (2), Ditty, Tacos, plus many cover practice takes (Linoleum, Just Like Heaven, '
        'Burnout, Carousel, In Bloom, ...). Full list: 01_source_manifests/voicememo/vm_unmatched.json'))
cat['voice_memo_pool'].pop('location_named_untitled')

cat['generated'] = '2026-08-18 v1.2'
json.dump(cat, open('/home/claude/vault/00_control_room/master_catalog.json','w'), indent=1)

import csv
cols=['song_id','canonical_title','artist_project','classification','alt_titles','writers','rights_confidence',
 'stage','key','bpm','potential','readiness','confidence','lyric_status','audio_status','theme','hook',
 'sources','soundcloud','best_source','next_action','open_questions','notes']
with open('/home/claude/vault/00_control_room/master_catalog.csv','w',newline='') as f:
    w=csv.writer(f); w.writerow(cols)
    for s in cat['songs']:
        w.writerow([('; '.join(map(str,s[c])) if isinstance(s[c],list) else s[c]) for c in cols])
print('v1.2 saved:', len(cat['songs']), 'song entities')
