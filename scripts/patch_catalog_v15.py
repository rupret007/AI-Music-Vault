#!/usr/bin/env python3
"""Catalog patch v1.5 — the Whisper transcript pass.
Adds 9 recovered song entities (lyric-verified from transcripts), applies new
memo matches, upgrades It's Alright / Andrea / Turn Over The Flag / Blue Skies
Fade / Better Than Now with transcript evidence."""
import json

CAT = '/home/claude/vault/00_control_room/master_catalog.json'
cat = json.load(open(CAT))
idx = {s['song_id']: s for s in cat['songs']}

def S(song_id, title, **kw):
    base = dict(song_id=song_id, canonical_title=title, artist_project='Jeff Story',
                classification='original', alt_titles=[], writers=['Jeff Story'],
                rights_confidence='high', stage='voice memo only (recovered 2026-08 via transcript pass)',
                sources=[], soundcloud=[], theme='', hook='', potential=None, readiness=None,
                confidence='medium', audio_status='transcription only — Whisper base.en, NOT listened to',
                lyric_status='partial — recovered from memo transcript(s), garbled in spots',
                next_action='', ai_involvement='none (transcription only)', open_questions=[], notes='')
    base.update(kw)
    return base

new = [
S('JS-0130','Been Loving You (working title)',
  theme='Long-relationship strain/ending — "I\'ve been loving you for quite some time / I think that it\'s best we..." + "it\'s a mess we both..."',
  hook='"Been loving you for quite some time"',
  notes='FOUR takes across 6 months: Maxwell Dr 76+77 (2022-11-17), Maxwell Dr 93 (2023-03-21), Maxwell Dr 99 (2023-05-25). Repeated work = Jeff cared about this one. Candy-thread shadow side. Chorus recurs in 4-5 separated places per take = real chorus.',
  next_action='LISTEN: play Maxwell Dr 99 (latest take). Verdict: gem / meh / "that\'s actually ___".'),
S('JS-0131','I Fall Pretty Down / City\'s Gone (working title)',
  theme='Falling apart while everything else does — "I fall pretty down, like the city\'s gone" + "breathing in the dark" + "we wrap our hearts"',
  hook='"I fall pretty down, like the city\'s gone"',
  stage='ACTIVELY WRITTEN Oct 2025 — the newest unknown song in the vault',
  notes='Crescent Dr 54 (20 min) + Crescent Dr 56 (11 min), BOTH 2025-10-03 — a full writing session. ~30 min of work on one day, chorus repeated across takes. This is the most recent new writing recovered anywhere in the catalog.',
  next_action='LISTEN FIRST among all gems: Crescent Dr 56. Most recent = most likely still alive in Jeff\'s head.'),
S('JS-0132','Don\'t Put Your Life Away (working title)',
  theme='Talking someone out of giving up — "Hey there darling, don\'t put your life away... if you stay here, fear in the unknown, you\'ll regret... don\'t be alone." THE MIND thread (protective side, like Take The Step).',
  hook='"Hey there darling, don\'t put your life away"',
  notes='FOUR-FIVE takes Mar–Apr 2021: Test song (03-23), New Recording 6 (03-25), If you\'re thinking of leaving (03-26), Maxwell Dr 20 (04-01). NOT the Hey There Delilah adaptation (JS-0054) — different lyric, different song. Verify not an alt-version of Prevent The Fall / Talk To Me before promoting.',
  open_questions=['Same song as Prevent The Fall or Talk To Me, or new? (Jeff: 5-second answer)'],
  next_action='LISTEN: "If you\'re thinking of leaving" (2021-03-26) — the clearest take.'),
S('JS-0133','A Place Where You Might (working title)',
  theme='Unknown — chorus "I\'m in a place where you might..." recurs in 10 separated places in one take.',
  hook='"I\'m in a place where you might..."',
  notes='Single take: Crescent Dr 21 (2024-03-06, 3:26). Strongest single-take chorus signal in the untitled pool.',
  next_action='LISTEN: Crescent Dr 21.'),
S('JS-0134','Anyone Can See / Here Is The Church (working title)',
  theme='Unknown — "(don\'t see what) anyone can see" + "here is the church and..." (children\'s rhyme repurposed?)',
  hook='"Don\'t see what anyone can see"',
  notes='TWO takes 7 months apart: Maxwell Dr 78 (2022-11-17) + Maxwell Dr 104 (2023-06-24). Return visits = it mattered.',
  next_action='LISTEN: Maxwell Dr 104 (later take).'),
S('JS-0135','Chasing Rainbows',
  theme='Searching/refusing easy belief — "Will you do anything to satisfy your soul?... don\'t believe it... let the whole world down"',
  hook='"Will you do anything to satisfy your soul?"',
  notes='OLDEST memo in the vault (2019-10-14, 3:11) with a real lyric throughout. Title is Jeff\'s own.',
  next_action='LISTEN: the 2019-10-14 memo — the vault\'s earliest recovered song.'),
S('JS-0136','The Way That You Love Me',
  theme='Unknown — love song w/ "tap my parachute, that\'s what keeps me [free]" + "diamond rings" imagery',
  hook='unclear (transcript heavily garbled)',
  confidence='low',
  notes='2019-10-15 memo (2:37), real sung lyric. Title could be a cover I can\'t place — verify before ranking.',
  open_questions=['Original or cover? (title matches no major hit exactly)'],
  next_action='LISTEN + verdict: original or cover?'),
S('JS-0137','Happy (working title)',
  theme='Wanting out of one\'s own head — "Maybe you\'ll be me... I wanna be happy, yeah"',
  hook='"I wanna be happy"',
  notes='THREE takes + one instrumental, all 2022-12-17 (Happy / Happy 2 / Happy v1.0 / Happy Instrumental). A one-day writing burst. Mind-thread adjacent.',
  next_action='LISTEN: Happy v1.0.'),
S('JS-0138','Find My Island (working title)',
  theme='Band-life defiance — "everyone is living in the past... we\'ve been ripped off / but we aren\'t on the radio / so we make the light of it"',
  hook='"We aren\'t on the radio, so we make the light of it"',
  notes='Find my island v1.0 (2022-12-17), short take, same day as Happy burst. A band-about-being-a-band lyric — Bar-thread adjacent, self-aware and funny-sad.',
  next_action='LISTEN: 98-second memo. Quick verdict.'),
]
existing = set(idx)
for s in new:
    assert s['song_id'] not in existing
    cat['songs'].append(s)

# ---- upgrades to existing entities ----
u = idx['JS-0128']  # It's Alright
u['stage'] = 'written + IN CURRENT LIVE SET (Oct 2025 practice) — unrecorded, no lyric doc'
u['hook'] = '"Just when I think I\'m losing my mind, I know it\'s alright"'
u['theme'] = 'Optimism under strain — the Mind thread\'s RESOLUTION song. Sun-comes-up counterpart to Manic/What To Do.'
u['potential'] = 74
u['confidence'] = 'medium-high'
u['audio_status'] = 'transcription only (6 memos) — NOT listened to'
u['lyric_status'] = 'RECONSTRUCTED from 5-take transcript triangulation (see It\'s Alright — Song Workup); 2 chorus lines need Jeff\'s ear'
u['notes'] = (u.get('notes','') + ' TRANSCRIPT PASS: 6 memos — It\'s Alright (2022-01-08), It\'s alright vocals (02-08), Maxwell 38/39/40 + v1 + v2 (02-11), and 15 chorus reps inside the Eagle Mountain Dr 2 band practice (2025-10-10). Lyric ~85% recovered. Possible band name-drop: "It\'s noisy and Something Dirty / I\'d like to take you on my journey" (consistent across all 5 takes).').strip()
u['next_action'] = 'Jeff: confirm the 2 unclear chorus lines by ear (60s), then this is a finished lyric.'

a = idx['ST-0110']  # Andrea
a['notes'] = (a.get('notes','') + ' TRANSCRIPT PASS: Maxwell Dr 101 (2023-06-20) is an Andrea demo — hook "I know I\'ll be with you one day" + lake imagery ("Andrea, on the lake"?). Fits the 2023 re-record timeline. NOTE: lake imagery may link Andrea ↔ Home on the Lake (JS-0114?) — flag, not assert.').strip()

t = idx['ST-0001']  # Turn Over The Flag
t['notes'] = (t.get('notes','') + ' TRANSCRIPT PASS: 2 new solo demos found — Maxwell Dr 133 (2024-02-16, 3 chorus reps) and Maxwell Dr 156 (2024-08-21, 7 reps).').strip()

b = idx['JS-0107']  # Blue Skies Fade
b['notes'] = (b.get('notes','') + ' TRANSCRIPT PASS: "Blue skies beginning" memo (2024-07-27, NINE minutes) = a 2024 runthrough of the opus\'s opening. Add to opus source list.').strip()

btn = idx['ST-0005']  # Better Than Now
btn['lyric_status'] = 'FRAGMENTS captured from memo 2024-07-25 transcript: "Better than now!" / "I\'m willing to" / "Take me away to the bad place" / "I\'m feeling down, you\'re feeling down" / "I\'m a little bit away". Not a full lyric — verify with Sean.'
btn['notes'] = (btn.get('notes','') + ' Possible earlier stage: "Take me away" memos 2023-07-28 / 2023-08-25 (10× "take me away", no "bad place") — uncertain link.').strip()

cat['version'] = '1.5'
cat['updated'] = '2026-08-20'
json.dump(cat, open(CAT,'w'), indent=1)
print('v1.5 saved:', len(cat['songs']), 'entities')

# ---- new memo matches merged ----
vm = json.load(open('/home/claude/vault/01_source_manifests/voicememo/vm_matches.json'))
joined = json.load(open('/home/claude/vault/vm_transcribed.json'))
byfile = {j['file']: j for j in joined}
tit = json.load(open('/home/claude/vault/vm_title_rematch.json'))['new_title_matches']

lyric_matches = {  # verified by transcript reading
 'JS-0128': ['20220208','20220211'],  # handled via title rematch mostly
}
add = {}
for f, sid in tit.items():
    add.setdefault(sid, []).append(byfile[f]['uid'])
# verified phrase-matches from analysis
verified = {
 'ST-0001': ['20240216 ', '20240821 '],
 'ST-0110': ['20230620 '],
 'JS-0132': ['20210323','20210325','20210326','20210401'],
 'JS-0130': ['20221117','20230321','20230525'],
 'JS-0131': ['20251003'],
 'JS-0133': ['20240306 '],
 'JS-0134': ['20221117','20230624'],
 'JS-0135': ['20191014'],
 'JS-0136': ['20191015'],
 'JS-0137': ['20221217'],
 'JS-0138': ['20221217'],
}
name_filter = {'JS-0132': ('test song','new recording 6','thinking of leaving','maxwell dr 20'),
               'JS-0130': ('maxwell dr 76','maxwell dr 77','maxwell dr 93','maxwell dr 99'),
               'JS-0131': ('crescent dr 54','crescent dr 56'),
               'JS-0133': ('crescent dr 21',), 'JS-0134': ('maxwell dr 78','maxwell dr 104'),
               'JS-0135': ('chasing rainbows',), 'JS-0136': ('the way that you love me',),
               'JS-0137': ('happy',), 'JS-0138': ('find my island',),
               'ST-0001': ('maxwell dr 133','maxwell dr 156'), 'ST-0110': ('maxwell dr 101',)}
for sid, prefixes in verified.items():
    for j in joined:
        if any(j['file'].startswith(p.strip()) for p in prefixes):
            tl = (j['title'] or '').lower()
            if sid in name_filter and not any(nf in tl for nf in name_filter[sid]): continue
            add.setdefault(sid, []).append(j['uid'])
n_new = 0
for sid, uids in add.items():
    cur = set(vm.get(sid, []))
    fresh = [u for u in dict.fromkeys(uids) if u not in cur]
    n_new += len(fresh)
    vm[sid] = sorted(cur | set(fresh))
json.dump(vm, open('/home/claude/vault/01_source_manifests/voicememo/vm_matches.json','w'), indent=1)
tot = sum(len(v) for v in vm.values())
print(f'matches: +{n_new} new memo links -> {tot} total matched memos across {len(vm)} songs')
