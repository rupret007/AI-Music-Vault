#!/usr/bin/env python3
"""Catalog v1.1 patch — folds in: 27 newly-read lyric docs (subagent full-text pass, saved to
doc_texts/) and signal-level audio analysis of 4 of 6 album bounces. Still NO aesthetic
listening and NO speech-to-text (blocked in sandbox); audio_status upgraded only to
'signal-analyzed' where applicable."""
import json

cat = json.load(open('/home/claude/vault/00_control_room/master_catalog.json'))
idx = {s['song_id']: s for s in cat['songs']}

AUD = 'signal-analyzed (duration/tempo/key-est/loudness) — NOT auditioned, no transcription'

# ---- audio analysis results (bounces) ----
patch_audio = {
 'ST-0001': dict(aud=AUD, analysis='2:00, ~206bpm feel, sounds-in ~Ebm (=E in Eb tuning, matches live chart). I=-13.0 LUFS, LRA 2.8, TRUE PEAK +0.3 dBFS (clipping). Flat energy profile — chorus lift is limited; supports the "more guitars" overdub. Outro drops at ~1:52.'),
 'ST-0003': dict(aud=AUD, analysis='2:16, ~216bpm feel, sounds-in ~Eb (doc says A — verify tuning/capo). I=-12.3 LUFS, LRA 1.7 (flattest of the four), TP +0.3 dBFS.'),
 'ST-0004': dict(aud=AUD, analysis='2:07, key-est C#m (weak r=0.48). I=-9.5 LUFS — 3dB HOTTER than the rest of the album, TP +0.6 dBFS. Needs album-level matching.'),
 'ST-0006': dict(aud=AUD, analysis='2:13, key-est A (doc A/A#, consistent). I=-12.3 LUFS, LRA 2.7, TP +0.4 dBFS. Cold open, ends clean at ~2:10.'),
}
for sid, p in patch_audio.items():
    idx[sid]['audio_status'] = p['aud']
    idx[sid]['notes'] += ' AUDIO ANALYSIS (2026-08-18): ' + p['analysis']

# album-wide mix note
for sid in ['ST-0001','ST-0002','ST-0003','ST-0004','ST-0005','ST-0006']:
    idx[sid]['notes'] += ' ALBUM MIX NOTE: all measured masters exceed 0 dBFS true peak — final pass should limit to -1.0 dBTP and level-match tracks (Manic is 3dB hot).'

# ---- lyric scores from the 27-doc read ----
# (sid, potential, lyric_status, theme, hook, extra note)
L = 'full text read'
patch_lyrics = [
 ('ST-0004', 85, L, 'Bipolar mania as a night-out anthem — euphoria with poison underneath',
  '"Riding every wave" flipped to "Drowning in the wave" — double-chorus mirror; sardonic "just another perfect manic day!" outro',
  'POTENTIAL 85: hook 20 (mirror chorus is smart), lyric 15 ("Why is this poison in my brain?"; some stock neon), truth 19, structure 13, identity 10, replay 8. QUICK-WIN CHOICE VALIDATED — top-4 song, one overdub from done.'),
 ('ST-0017', 73, L, 'Suicidal-crisis confessional, raw first person',
  '"Betchu wonder what I\'m gonna do tonight" + antiphonal "(They keep getting closer)"',
  'POTENTIAL 73 (provisional — bridge marked "still need to write"): hook 16, lyric 14, truth 19, structure 10 (incomplete), identity 9, replay 5. Hidden gem CONFIRMED; finishing the bridge is the unlock.'),
 ('ST-0016', 56, L, 'Relationship strain after "Andrea" arrives; personal in-jokes',
  '"Can you say hi to Kimberley?"',
  'POTENTIAL 56: conversational charm but diluted hook, thin V2, cliché travel lines. NOTE: the "Andrea" here reads like an arrival (child? storm?) — different from the Andrea elegy. Ask Jeff.'),
 ('ST-0015', 55, L, 'Depression-fueled rage at home', '"I\'m sleep punching in the air... and I don\'t care"',
  'POTENTIAL 55: real subject; "worse/adverse" chorus rhyme is clinically stiff and fights the anger.'),
 ('ST-0110', 73, L, 'Elegy for a woman lost to addiction — beach romance turns overdose narrative',
  '"Andrea don\'t go away" / "(I know I\'ll be with you one day)"',
  'POTENTIAL 73: strongest narrative arc in the catalog (truth 18, structure 12); V1 meet-cute ("offer you a brew") needs a rewrite to match the weight of V3. Two "Verse 2" labels in doc.'),
 ('ST-0019', 65, L, 'Anniversary love song — 18 years, real memories (Loves truck stop, Ardmore OK, the cop)',
  '"Without her I\'m insane"',
  'POTENTIAL 65: sturdy singalong chorus; 2024 rewrite trades whimsy for specificity. LINEAGE: Our Life (2014) → Candy Lane (2017) → Candi Lane (2024) — same chorus throughout; catalog as one song, three eras. The 2017 tag "because she likes my band" is arguably the best variant.'),
 ('ST-0021', 66, L, 'Apology after a mental-health blowup', '"I\'m sorry I\'m crazy, and I was born this way"',
  'POTENTIAL 66: catchy pop-punk shrug; "born this way" collides with Lady Gaga; final-chorus tag keeps mutating (pick one).'),
 ('ST-0022', 64, L, 'Rock-bottom acceptance after a public breakdown', '"Who knew life at the bottom ain\'t so bad"',
  'POTENTIAL 64: good wry hook; chorus has a repeated typo-stumble ("I gotta it ain\'t so bad") to fix; "masses that are enslaved" drifts into soapbox (shared vocabulary with Turn Over The Flag).'),
 ('ST-0029', 58, L, 'Bitter breakup kiss-off (2012)', '"head submerged in the sand / I guess that\'s why they call me a man"',
  'POTENTIAL 58: the sand/man turn is the one clever move; verses high-cliché.'),
 ('ST-0031', 62, L, 'Rebuilding a marriage after self-destruction', '"But I gotta go through this to get to you"',
  'POTENTIAL 62: that refrain IS the hook; rest of chorus flat; Matrix blue-pill reference dates it.'),
 ('ST-0026', 50, L, 'Anti-hypocrisy protest — sweatshops vs performative talk', '"Inclusion only works for those on top"',
  'POTENTIAL 50: skeletal (V2 = 3 lines); chorus grammar breaks down; strong single line though.'),
 ('ST-0023', 64, L, 'Bipolar swings anchored by a devoted partner', '"Oh brain won\'t you go away / Oh brain just let me escape"',
  'POTENTIAL 64: bridge is the best section; "You\'re the blood in my heart" is a strong odd image; chorus wordy. Companion to Manic!!.'),
 ('ST-0024', 65, L, 'Needing a partner to see past his mental illness', '"To understand I don\'t mean what I say"',
  'POTENTIAL 65: echo-vocal chorus is radio-shaped; darker outro variant is the payoff; V2 smells greeting-card. Was Prime Outline TRACK 1 — worth a demo listen to see why it fell off the album.'),
 ('ST-0025', 62, L, 'Anti-two-party protest', '"I\'m just a pissed off American"',
  'POTENTIAL 62: the hook is a T-shirt; verses all abstraction.'),
 ('ST-0009', None, L, None, None, None),  # no change; placeholder
]
for sid, pot, lys, theme, hook, note in patch_lyrics:
    s = idx[sid]
    if pot: s['potential'] = pot
    s['lyric_status'] = lys
    if theme: s['theme'] = theme
    if hook: s['hook'] = hook
    if note: s['notes'] = (s['notes'] + ' ' + note).strip()
    if pot: s['confidence'] = 'high' if sid in ('ST-0004',) else 'medium'

# JS solo entities — find by title
by_title = {s['canonical_title']: s for s in cat['songs']}
js_patch = [
 ('Why Do I...', 77, 'Suicidal ideation despite a good life — stark and unadorned',
  '"Why do I wanna die? / I have such a great life" — brutal because it\'s unpoetic',
  'POTENTIAL 77: truth 20 (max), hook 18; ★★★★ from lyric-editor pass. With Manic!! and Why Do I..., there is a devastating mental-health song cluster in NEW SONGS 2024. Companion: What To Do, Long Long Drive.'),
 ('Synonyms For Stubborn', 75, 'Regret over a burned relationship, cycled through literal thesaurus words',
  '"What binds us, divides us" + the V3 turn from stubborn to "A loser for all my life"',
  'POTENTIAL 75: cleverest structural idea in the batch; V3 redeems the gimmick.'),
 ('I Fall Down', 72, 'Bender/relapse romp, Alice-in-Wonderland framing',
  '"Down down down down... down the rabbit hole again" (stuttered singalong)',
  'POTENTIAL 72: fun hook, jump-blues chords documented (F Bb7 C7 F) — the only chord info in the whole NEW SONGS batch.'),
 ('Minor Lessons', 68, 'Roman-plebs-as-modern-populism concept song, ends in Latin',
  '"We\'re all guilty in our thinking / That the other side is drinking / Their establishment\'s punch"',
  'POTENTIAL 68: most ambitious writing in the batch; Les Mis-adjacent mutating chorus; "Accountability in Dallas" rhyme-grab to fix.'),
 ('Going To Cali', 68, 'Escape-the-city road anthem (Something Dirty core song)',
  '"Live the American dream / A SigAlert / What the fuck does that mean?"',
  'POTENTIAL 68: the SigAlert joke is great; solid chorus; outro chant closer. Combined with THREE Logic projects = readiness is real. (Scored under SD-0006 too.)'),
 ('Don\'t Look Bach', 60, 'Corporate music industry vs artistic purity, Bach-pun conceit',
  '"Johann, in your grave, do you toss and turn?"', 'POTENTIAL 60: fun live pun; cliché cluster + typos.'),
 ('Prevent The Fall', 60, 'Depression recovery credited to a partner', '"Depression my proverbial noose"',
  'POTENTIAL 60: mantra chorus hypnotic-or-monotonous depending on riff; V3 sermonizes.'),
 ('Justify', 58, 'Political-economic doom protest', '"Our future scares the shit outta me"',
  'POTENTIAL 58 (provisional, bridge TBD). CREDIT FLAG: quotes Emerson\'s "Boston" verbatim ("For what avail the plough or sail...") — needs attribution if released.'),
 ('The Catalyst', 54, 'Populist unity anthem', '"Our leaders are the ones who should live in fear"',
  'POTENTIAL 54: polysyllabic chorus fights the melody; "tarriance" is a dictionary reach.'),
 ('Starlight', 52, 'Devotional love song, night-sky frame', '"Time flies by when you\'re awake"',
  'POTENTIAL 52: pleasant, rhyme-by-numbers.'),
 ('You Complete Me', 52, 'Long-distance love / airport goodbye', '"Feels like 10,000 days since you went away"',
  'POTENTIAL 52: Jerry Maguire catchphrase hook — sweet, well-trodden.'),
 ('August Heated Nights', 52, 'Ballad of pirate Black Sam Bellamy', '"We scorn to do mischief, but we must fight"',
  'POTENTIAL 52: title unrelated to lyric; CREDIT FLAG: bridge paraphrases Bellamy\'s real recorded speech; reads AI-assisted — confirm provenance with Jeff.'),
 ('The Leaves Are Weak', 48, 'Conformity-vs-free-will via falling leaves', '"The leaves are falling without thought"',
  'POTENTIAL 48: uniformly abstract, no concrete human anywhere; reads AI-polished — confirm provenance.'),
]
for title, pot, theme, hook, note in js_patch:
    s = by_title.get(title)
    if not s: continue
    s['potential'] = pot; s['lyric_status'] = 'full text read'; s['confidence'] = 'medium'
    s['theme'] = theme; s['hook'] = hook; s['notes'] = (s['notes'] + ' ' + note).strip()

# SD-0006 Going to Cali mirror
sd6 = idx.get('SD-0006')
if sd6:
    sd6['potential'] = 68; sd6['lyric_status'] = 'full text read'; sd6['confidence'] = 'medium'
    sd6['hook'] = '"A SigAlert / What the fuck does that mean?"'
    sd6['notes'] += ' Lyric read 2026-08-18: solid chorus + great ironic joke; 3 Logic projects; top SD revival candidate.'

# SD-0011 Our Life
sd11 = idx.get('SD-0011')
if sd11:
    sd11['potential'] = 55; sd11['lyric_status'] = 'full text read'; sd11['confidence'] = 'medium'
    sd11['notes'] += ' Through-composed, no chorus; death stanzas have real weight. ANCESTOR DOC of Candy Lane/Candi Lane — the lineage source.'

# Dorivalland reclassification
u100 = idx.get('UNK-0100')
if u100:
    u100['classification'] = 'reference material (collaborator musical project)'
    u100['notes'] += ' READ 2026-08-18: these are staging/libretto notes for dver.artist\'s musical (samba number, Bolsonaro allegory) — NOT Jeff catalog songs. Kept as reference; edited 4 days ago so the collab is live.'

cat['generated'] = '2026-08-18 v1.1'
cat['honesty_note'] = ('Lyrics: 41 songs now read in full. Audio: 4 of 6 album bounces signal-analyzed '
 '(duration/tempo/key-estimate/loudness/energy) — NO aesthetic listening and NO speech-to-text has occurred '
 '(ASR model downloads blocked in sandbox). SoundCloud stats remain weak supporting evidence only.')
json.dump(cat, open('/home/claude/vault/00_control_room/master_catalog.json','w'), indent=1)

# regen CSV
import csv
cols=['song_id','canonical_title','artist_project','classification','alt_titles','writers','rights_confidence',
 'stage','key','bpm','potential','readiness','confidence','lyric_status','audio_status','theme','hook',
 'sources','soundcloud','best_source','next_action','open_questions','notes']
with open('/home/claude/vault/00_control_room/master_catalog.csv','w',newline='') as f:
    w=csv.writer(f); w.writerow(cols)
    for s in cat['songs']:
        w.writerow([('; '.join(s[c]) if isinstance(s[c],list) else s[c]) for c in cols])

scored=[(s['potential'],s['song_id'],s['canonical_title']) for s in cat['songs'] if s['potential']]
scored.sort(reverse=True)
print(f"v1.1 saved. scored songs: {len(scored)}")
for p,i,t in scored[:20]: print(f"  {p}  {i}  {t}")
