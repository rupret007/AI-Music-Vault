#!/usr/bin/env python3
"""Jeff Story Master Song Catalog builder — v1 (2026-08-18).
Entity resolution from: Google Drive inventory (357 records), 10 key doc texts,
SoundCloud public inventory (44/189 tracks). AUDIO NEVER LISTENED TO — all audio
status is 'metadata only'. Lyric evaluations are based on actual document text."""
import json, csv, datetime

def S(id, title, artist, cls, **kw):
    d = dict(song_id=id, canonical_title=title, artist_project=artist, classification=cls,
        alt_titles=kw.get('alt',[]), writers=kw.get('writers',['Jeff Story']),
        rights_confidence=kw.get('rights','high'), stage=kw.get('stage','cataloged'),
        lyric_pct=kw.get('lyr',None), music_pct=kw.get('mus',None), rec_pct=kw.get('rec',None),
        key=kw.get('key',''), bpm=kw.get('bpm',''),
        sources=kw.get('src',[]), soundcloud=kw.get('sc',[]),
        earliest_known=kw.get('early',''), latest_version=kw.get('late',''),
        best_source=kw.get('best',''), theme=kw.get('theme',''), hook=kw.get('hook',''),
        version_count=kw.get('vc',1), potential=kw.get('pot',None), readiness=kw.get('rdy',None),
        confidence=kw.get('conf','low'), audio_status=kw.get('aud','metadata only'),
        lyric_status=kw.get('lys','not read'), next_action=kw.get('next',''),
        ai_involvement='none', open_questions=kw.get('oq',''), notes=kw.get('notes',''))
    return d

songs = []

# ============ THE CURRENT ALBUM SIX (Stalemate, bounces v1.4-1.6, active thru Mar 2026) ============
songs += [
S('ST-0001','Turn Over The Flag','Stalemate','original', alt=['turn over'],
  key='E (live, Eb tuning)', stage='mixing — album track 1',
  lyr=100, mus=95, rec=90,
  src=['LYRICS/01 doc (rev 2025-12-29)','bounces/1. turn over mix 1.6 (2026-03-02)','turn over mix 1.5.wav master','turn over mix 1.4 (BackVox Overdubs).logicx ~40 stems','NEW SONGS 2024 demo m4a','Session v1.0 mp3 (2025-11-14)'],
  early='2024-05 demo', late='mix 1.6, 2026-03-02', best='bounces/1. turn over mix 1.6',
  theme='Protest anthem — flying the flag inverted as a distress signal for the country',
  hook='Chanted title chorus + "land of the brave / home of the enslaved" inversion',
  vc=6, pot=74, rdy=91, conf='high', lys='full text read',
  next='Record bridge "oohs" + add rhythm guitar layers (the only 2 items left on the Overdubs doc), then bounce mix 1.7',
  notes='POTENTIAL 74: hook 18 (chant chorus lands), lyric 13 (chorus inversion is the best line; verses lean on abstract veil/shadow imagery), truth 16 (sincere anger), structure 12 (bridge = children\'s plea answers the chorus), identity 8, replay 7. READINESS 91: most-iterated mix in the vault, 2 to-dos left.'),
S('ST-0002','The Way I Love You','Stalemate','original',
  key='A', bpm='214 (cut)', stage='overdubs — album track 2', lyr=100, mus=90, rec=85,
  src=['LYRICS/05 doc (chords+BPM)','bounces/2. the way i love you v1.4 (2026-01-24)','Crisis Averted chart+studio take','The Way I Love You v2.5 (SoundCloud 2023)','Rad Dad + Stalemate + Something Dirty setlists'],
  early='pre-2023 (Crisis Averted era)', late='v1.4 2026-01-24', best='bounces v1.4',
  theme='Finding the one who loves you for who you are, after the casualties and maybes',
  hook='"Nobody ever gonna come and call me baby / not like you do"',
  vc=5, pot=77, rdy=90, conf='high', lys='full text read',
  next='Track background vox + guitar solo; nudge verse vocals +0.2dB (per Overdubs doc)',
  oq='One Rad Dad tab credits this to "Paco Estrada" — confirm it is 100% Jeff\'s composition before any external upload.',
  notes='POTENTIAL 77: hook 19, lyric 14 ("fair handshake of casualties and maybes" is a keeper; a few stock lines), truth 15, structure 12 (softer V2 is real dynamics), identity 9, replay 8. Longest-serving song across three bands = proven live.'),
S('ST-0003','TBFH','Stalemate','original', alt=['To Be Fucking Honest','TBFH v4.5'],
  key='A', stage='overdubs — album track 3', lyr=100, mus=90, rec=85,
  src=['LYRICS/04 doc (rev 2026-01-10)','2020-Lyrics/TBFH (2024)','bounces/3. tbfh v1.4 (2026-01-10)','TBFH v4.5 (SoundCloud 2023)','Crisis Averted chart+studio'],
  early='<=2023', late='v1.4 2026-01-10', best='bounces v1.4',
  theme='Post-breakup honesty — still in love, knows it\'s dead, finally letting go',
  hook='The title itself, sung as the verse engine: "To be fucking honest..."',
  vc=6, pot=86, rdy=90, conf='high', lys='full text read',
  next='Background vox + chorus "oohs"; drums +1dB (per Overdubs doc)',
  notes='POTENTIAL 86 — highest scored lyric in the vault: hook 21 (title is the hook and it\'s unforgettable), lyric 16 ("Starring at Sir Paul McCartney" bridge is the most Jeff line in the catalog), truth 19 (v3 rewrite turns the ending from wallowing to walking away — real arc), structure 12, identity 10 (emotional honesty + profanity + humor = the Jeff Story sweet spot), replay 8.'),
S('ST-0004','Manic','Stalemate','original', alt=['Manic!','Manic!!','Manic?  No way!'],
  stage='overdubs — album track 4', lyr=95, mus=90, rec=85,
  src=['NEW SONGS 2024/Manic!! doc (rev 2025-05-22) + Manic! (New 05-2024).m4a','2020-Lyrics/Manic? No way! (2022)','bounces/4. manic v1.4 (2026-01-08)','Manic!! (SoundCloud 2024-08, 66 plays)'],
  early='2022 lyric', late='v1.4 2026-01-08', best='bounces v1.4',
  vc=4, pot=None, rdy=87, conf='medium', lys='not read — doc exists, snippet not captured',
  next='QUICK WIN: one overdub left (guitar octave part in chorus), then it is done',
  notes='Only ONE item on the Overdubs doc — the closest song to finished on the entire album. Potential unscored until I read the Manic!! lyric doc (top of next session\'s reading list).'),
S('ST-0005','Better Than Now','Stalemate','original',
  key='B (live)', stage='overdubs — album track 5', lyr=90, mus=85, rec=80,
  src=['bounces/5. better than now v1.4 (2026-01-08)','Session v1.0 (2025-11-14)','setlists 3-13-24 & 4-26-24 (marked Stalemate original, sung by S)'],
  early='<=2024-03', late='v1.4 2026-01-08', best='bounces v1.4',
  vc=3, pot=None, rdy=79, conf='medium', lys='no lyric doc found',
  next='Locate/transcribe lyrics (no doc exists!); then guitar solos + "Jeff take me away" chorus vox per Overdubs doc',
  oq='Sung by "S" (Che?) live — who wrote it? Confirm authorship split before release.',
  notes='On the album with no lyric doc anywhere in Drive — the lyric lives only in performances. Needs a lyric-capture pass.'),
S('ST-0006','Take The Step','Stalemate','original', alt=['Take This Step','13 - Take The Step'],
  key='A/A# (varies by chart)', bpm='145', stage='overdubs — album track 6', lyr=100, mus=90, rec=80,
  src=['LYRICS/13 doc (BPM 145)','bounces/6. take the step mix v1.4 (2026-01-24)','Jeff Story - Take This Step v1.2.wav (2023)','Crisis Averted chart+studio (different key)'],
  early='<=2023', late='v1.4 2026-01-24', best='bounces v1.4',
  theme='Quitting / recovery — changing your life one day at a time, for her',
  hook='"But first I need to finally take this step"',
  vc=5, pot=75, rdy=86, conf='high', lys='full text read',
  next='4 overdub items: chorus "wohs", background vox, bridge oohs/aahs, last-chorus lead vox',
  notes='POTENTIAL 75: hook 16, lyric 14 ("one day at a time" deployed sincerely — it works because the song is literally about that), truth 18 (recovery song addressed to his wife — heavy and real), structure 12 (Sail Away bridge lifts), identity 8, replay 7. Most overdub work left of the six.'),
]

# ============ STALEMATE CORE REPERTOIRE (not on current album) ============
songs += [
S('ST-0007','Be With You','Stalemate','original', alt=['Be With You v2.5'],
  key='A live / F on song list', stage='demo+release', lyr=100, mus=85, rec=70,
  src=['LYRICS/02 doc (rev 2026-02-06 — recently touched!)','Be With You v2.5 (SoundCloud, Another Bland EP 2023)','Crisis Averted chart + studio (different key)','setlist 4-26-24 original'],
  early='<=2023', late='doc rev 2026-02-06', best='Be With You v2.5 (SoundCloud)',
  theme='Love song to a partner in the punk scene — the show only matters because she\'s there',
  hook='"Gonna go to the punk rock show... all I wanna do is just be with you"',
  vc=4, pot=86, rdy=79, conf='high', lys='full text read',
  next='Decide: does this belong on the album (it was Prime Outline track 12) or the next EP?',
  notes='POTENTIAL 86 (tied for #1): hook 20 (chorus is instant), lyric 17 (the dance-party-broken-foot verse is the most charming specific detail in the catalog), truth 18, structure 12 (bridge "any mountain, any plane" pays off), identity 10 (pure Jeff: punk show + devotion), replay 9. Jeff edited the doc in Feb 2026 — it\'s alive in his head. Strongest song NOT on the current album.'),
S('ST-0008','It\'s Only Been 18','Stalemate','original', alt=['It\'s Been Only 18','Only 18'],
  key='C doc / G live', bpm='212', stage='demo+release', lyr=100, mus=85, rec=75,
  src=['LYRICS/09 doc','2020-Lyrics/Only 18 (2023)','Jeff Story - Only 18 v1.5.mp3 + .logicx (2023-12)','It\'s Been Only 18 (SoundCloud 2023)','Crisis Averted chart+studio'],
  early='<=2023', late='v1.5 2023-12', best='Only 18 v1.5',
  theme='18th anniversary road-trip song — still lit up after all these years',
  hook='"The only thing I know / is that you make me aglow... it\'s been only 18?"',
  vc=5, pot=76, rdy=80, conf='high', lys='full text read',
  notes='POTENTIAL 76: hook 16, lyric 15 (Vermont, windows down — specific and sweet), truth 18 (a real marriage, a real number), structure 11, identity 9, replay 7. NOTE: distinct from "Over 18" (2010 album track 12) — do NOT merge.',
  next='Candidate for next-EP shortlist; v1.5 mix may be nearly done — needs a listening pass'),
S('ST-0009','Long Long Drive','Stalemate','original',
  key='Am', bpm='123', stage='written + old recordings', lyr=100, mus=80, rec=60,
  src=['LYRICS/11 doc (chords, bg-vox map)','SoundCloud /something-dirty-long-long-drive (2019, 241 plays)','Times Have Changed set (2021)','Crisis Averted chart + studio (different key)','setlist 4-26-24 original','Prime Outline track 8'],
  early='2019', late='doc 2024-05', best='2019 SoundCloud recording (metadata only)',
  theme='Depression hidden inside a good life — "a loving wife and son, but I\'ve got a dark corner"',
  hook='"The headwinds are strong / I think I\'m gonna implode... exposed, woh oh"',
  vc=4, pot=81, rdy=80, conf='high', lys='full text read',
  next='EXPERIMENTAL SLOT: modern full-band arrangement built from the documented chart (Am, 123bpm, bg-vox map already written)',
  notes='POTENTIAL 81: hook 17, lyric 16 ("I wrote this at 39 / not to be a Sad Bear" — devastating opening), truth 20 (max score; the most honest song in the vault), structure 12 (bridge asks the question the chorus can\'t), identity 9, replay 7. Has survived 3 band eras (SD 2019 → Crisis Averted → Stalemate sets) — Jeff keeps coming back to it. The background-vox outro map in the doc is an arrangement already half-designed.'),
S('ST-0010','Wham Bam','Stalemate','original', key='E', bpm='150', stage='released 2010 + live',
  lyr=100, mus=90, rec=100,
  src=['LYRICS/06 doc','My Mom Says We\'re Cool track 01 (2010)','Crisis Averted chart+studio','setlists'],
  early='2010 album', late='doc 2024', best='2010 album master',
  vc=3, pot=59, rdy=85, conf='high', lys='full text read',
  next='HOLD for re-evaluation: the 2004-era judgmental framing reads differently in 2026 — keep the riff/hook, consider a lyric rethink or retire proudly as a period piece',
  notes='POTENTIAL 59: hook 17 (the wham-bam gang chant works), lyric 9, truth 8, structure 11, identity 7, replay 7. Fully finished recording exists; question is whether Jeff 2026 still wants to say this.'),
S('ST-0011','Planet Of The Flakes','Stalemate','original', stage='released 2010 + live', lyr=100, rec=100,
  src=['LYRICS/14 docx','My Mom Says We\'re Cool track 10 (2010)','setlist 4-26-24 (C#)'],
  early='2010', best='2010 album master', vc=2, pot=51, rdy=83, conf='high', lys='full text read',
  next='Archive-with-honor: finished, released, still playable live; not a development priority',
  notes='POTENTIAL 51: teenage insult-punk, fun live, limited ceiling.'),
S('ST-0012','Don\'t Call Me A Hero','Stalemate','original', alt=['08 - Don\'t call me a hero'], key='F# (live)',
  stage='performed, no lyric doc', src=['Set 6-1-2024 mp3 #08','setlist 4-26-24 original (sung by S)'],
  pot=None, rdy=None, conf='insufficient evidence', lys='no doc found',
  next='Transcribe lyric from the 6-1-2024 set recording',
  oq='Sung by S — authorship split?'),
S('ST-0013','Graveyard Swiftly','Stalemate','original', alt=['Graveyard Scwifty','Graveyard shifty'], key='E',
  stage='performed, no lyric doc', src=['Set 6-1-2024 mp3 #10','setlist 4-26-24 original (S)'],
  pot=None, rdy=None, conf='insufficient evidence', lys='no doc found',
  next='Transcribe from set recording', oq='Authorship — sung by S'),
S('ST-0014','Everyday','Stalemate','original', key='C', stage='released 2010 + Rad Dad set',
  src=['My Mom Says We\'re Cool track 02 (2010)','Rad Dad setlist (original)','Stalemate song list'],
  pot=None, rdy=None, conf='insufficient evidence', lys='no doc found',
  notes='Survived 16 years into current cover-band sets — that endurance is evidence of a real hook. Priority listen.'),
S('ST-0015','Annoying Me','Stalemate','original', key='C', stage='recorded 2021',
  src=['2020-Lyrics/Annoying Me (2021)','Annoying Me (SoundCloud 2021, 109 plays)','Prime Outline track 11','song list **'],
  pot=None, rdy=None, conf='low', lys='doc exists, not read', next='Read lyric doc next session'),
S('ST-0016','Times Have Changed','Stalemate','original', key='B (list) / G+A charts', stage='recorded 2021 (EP title track)',
  src=['2020-Lyrics doc (2020)','Times Have Changed EP (SoundCloud 2021, 233 plays — highest recent-era)','Crisis Averted charts in 2 keys'],
  pot=None, rdy=None, conf='low', lys='doc exists, not read',
  notes='Title track of his own 2021 EP + best recent-era play count. Priority read+listen.'),
S('ST-0017','What To Do','Stalemate','original', alt=['What to Do'], key='Em', stage='recorded 2020',
  src=['2020-Lyrics doc (2020)','SoundCloud 2020 ("an original song about being in the midst of depression")','Crisis Averted chart+studio','song list ***'],
  pot=None, rdy=None, conf='low', lys='doc exists, not read',
  notes='HIDDEN GEM CANDIDATE: Jeff\'s own description marks it as the depression companion to Long Long Drive. Priority read+listen.'),
S('ST-0018','In The End','Stalemate','original', key='D', stage='multiple recordings',
  src=['Crisis Averted chart + practice + studio links','Something Dirty - In The End (Rhodes) v1.0.logicx (2023)','song list ***'],
  pot=None, rdy=None, conf='low', lys='no doc read', notes='A Rhodes arrangement exists — someone cared enough to re-arrange it. Not the Linkin Park song; distinct from dustduff90\'s "The End".'),
S('ST-0019','Candi Lane','Stalemate / Something Dirty','original', alt=['Candy Lane (2017)'], key='A',
  stage='performed both bands', src=['2020-Lyrics/Candi Lane (2024) + Candy Lane (2017)','SD setlist 5-13-2023 (marked *)','Crisis Averted chart+studio (different key)','song list ***'],
  pot=None, rdy=None, conf='low', lys='docs exist, not read'),
S('ST-0020','Mom, You\'re The Bomb','Stalemate / Something Dirty','co-write', writers=['Jeff Story','Greg Baldia'],
  alt=['Mom','Something Dirty - Mom'], key='G list / C+D charts', stage='released 2011 + charts',
  src=['Something Dirty - Mom (SoundCloud 2011, 261 plays; desc: "Greg Baldia and I wrote this... about my amazing Mom Connie Story")','Jeff Story - Mom You\'re The Bomb v2.2.wav (2023)','Crisis Averted charts in C AND D','song list ***'],
  rights='co-write — Greg Baldia', pot=None, rdy=None, conf='medium', lys='not read',
  oq='LIKELY the same underlying song as 2011 "Mom" — treat as one entity pending Jeff\'s confirmation. Co-writer consent needed before any external/AI use.'),
S('ST-0021','I\'m Sorry I\'m Crazy','Jeff Story','original', key='B', stage='recorded 2021',
  src=['2020-Lyrics doc','SoundCloud 2021 (181 plays)','song list'], pot=None, rdy=None, conf='low', lys='not read'),
S('ST-0022','Life At The Bottom','Jeff Story','original', key='G', stage='recorded 2021',
  src=['2020-Lyrics doc (2021)','SoundCloud 2021 (137 plays)'], pot=None, rdy=None, conf='low', lys='not read'),
S('ST-0023','Highs and Lows','Stalemate','original', stage='demo 2024',
  src=['NEW SONGS 2024 doc+demo','Jeff Story - High and Lows v2.wav (2022)','Prime Outline track 5'],
  pot=None, rdy=None, conf='low', lys='not read'),
S('ST-0024','I Need You','Stalemate','original', stage='demo 2024',
  src=['NEW SONGS 2024 doc + demo (5-22-24)','Prime Outline TRACK 1'],
  pot=None, rdy=None, conf='low', lys='not read',
  notes='Was slated as Prime Outline album OPENER — but absent from the final six bounces. Why? Ask Jeff or check demo.'),
S('ST-0025','Dystopian Choice','Jeff Story','original', stage='recorded 2019 + demo 2024',
  src=['2020-Lyrics (2020) + NEW SONGS 2024 doc+demo','SoundCloud 2019 (18 plays)','Prime Outline track 9'],
  pot=None, rdy=None, conf='low', lys='not read'),
S('ST-0026','Brave New World','Jeff Story','original', stage='iPhone demo',
  src=['NEW SONGS 2024 doc + "8-31-23 3 capo" demo','SoundCloud 2022 demo (44 plays, "recorded on my iPhone")','song list'],
  pot=None, rdy=None, conf='low', lys='not read', notes='Hidden-gem queue: survived from 2022 demo to 2024 re-demo.'),
S('ST-0027','Morgan The Wizard','Stalemate','original', stage='lyric video only',
  src=['Prime Outline track 14','lyric video referenced; no doc/audio located'], pot=None, rdy=None, conf='insufficient evidence', lys='not found'),
S('ST-0028','The Prime Outline','Stalemate','original', stage='title only',
  src=['Prime Outline track 3 — the album\'s own title track; NO doc or audio found anywhere'],
  pot=None, rdy=None, conf='insufficient evidence', lys='not found',
  oq='Does this song exist (voice memo on phone?) or is it a concept?'),
S('ST-0029','Head in the Sand','Jeff Story','original', key='B', stage='lyric only',
  src=['2020-Lyrics (2021)','song list **'], pot=None, rdy=None, conf='low', lys='not read'),
S('ST-0030','Rabbit Hole','Stalemate','original', key='Bb', stage='listed only',
  src=['song list **'], pot=None, rdy=None, conf='insufficient evidence', lys='not found'),
S('ST-0031','Newfound Love','Jeff Story','original', alt=['New Found Love'], key='Am', stage='lyric only',
  src=['2020-Lyrics (2020)','song list'], pot=None, rdy=None, conf='low', lys='not read'),
S('ST-0032','Another Bland Love Song','Jeff Story','original', key='G', stage='recorded 2023 (EP title track)',
  src=['SoundCloud 2023 (Another Bland EP)','drums wav 2022 + mp3 2024-12','song list'],
  pot=None, rdy=None, conf='low', lys='no doc found', notes='He named an EP after it — self-aware title is very Jeff.'),
]

# ============ JEFF STORY SOLO — mixes & demos ============
solo = [
 ('JS-0001','Drinking Song','Something Dirty / Stalemate / Rad Dad','original','Am','',
  ['Doc "Something Dirty - The Drinking Song" (2022, full lyric+chords)','Rad Dad setlist #15','2GB live video 15 Drinking Song.mp4 (luckyivy86)','SD sets'],
  79,82,'high','full text read',
  'Three bands keep it in the set. Bar-singalong with a complete arc. POTENTIAL 79: hook 18 ("Oh hey bartender" + Cheers! ending), lyric 15, truth 14, structure 13 (complete, chorded), identity 10, replay 9 (live weapon). Quick-win candidate for a proper studio recording.'),
 ('JS-0002','Going To New Mexico','Jeff Story','original','C','',
  ['Let\'s Go To New Mexico on song list','Going To New Mexico v1.4 (2023) + v1.5 (2024-09) wav'],None,None,'low','not read','Two mix versions = active. Listen next session.'),
 ('JS-0003','Less Miserable','Jeff Story','original','C','',
  ['song list','v1.0.mp3 (2022)','Less Miserable v1.1.logicx'],None,None,'low','not read',''),
 ('JS-0004','Thanksgiving','Jeff Story','original','C','',
  ['song list','Thanksgiving v1.4.wav (2022)'],None,None,'low','not read',''),
 ('JS-0005','The Leaves Are Weak','Jeff Story','original','','',
  ['NEW SONGS 2024 doc+demo','v1.0.wav (2023)','song list'],None,None,'low','not read',''),
 ('JS-0006','A Better Way','Jeff Story','original','','',
  ['song list','A Better Way v1.0 wav (2023-09) + mp3 (2024-01)'],None,None,'low','not read',''),
 ('JS-0007','31 Timberview','Jeff Story','original','','',
  ['song list ("31 Timberview")','31 Timber View Ln v1.0 wav+mp3 (2023-11)'],None,None,'low','not read',''),
 ('JS-0008','Better Together','Jeff Story','original','','',
  ['Better Together v1.1.wav (2024-09)'],None,None,'low','not read','No lyric doc located.'),
 ('JS-0009','Oui C\'est Fou','Jeff Story','original','','',
  ['Prime Outline "in development"','Oui C\'est Fou (Lyric Video).mp4 (2025-07)','99/90 Percent + Oui C\'est Fou mixes folder'],None,None,'low','not read','Has a finished LYRIC VIDEO — that\'s promotion-level effort. Priority look.'),
 ('JS-0010','90% / 99 Percent','Jeff Story','original','','',
  ['Prime Outline "in development" ("90%")','99/90 Percent mixes folder'],None,None,'insufficient evidence','not found',''),
 ('JS-0011','August Heated Nights','Jeff Story','original','','',
  ['NEW SONGS 2024 doc (2024-04) + demo','song list'],None,None,'low','not read',''),
 ('JS-0012','Don\'t Look Bach','Jeff Story','original','','',
  ['NEW SONGS 2024 doc + v1.3.wav','song list ("Don\'t look bach")'],None,None,'low','not read','Pun title. v1.3 wav = multiple passes.'),
 ('JS-0013','I Fall Down','Jeff Story','original','','',
  ['NEW SONGS 2024: I Fall Down Lyrics (2022) + m4a'],None,None,'low','not read',''),
 ('JS-0014','Justify','Jeff Story','original','','',
  ['NEW SONGS 2024 doc (2023) + m4a'],None,None,'low','not read',''),
 ('JS-0015','Minor Lessons','Jeff Story','original','','',
  ['NEW SONGS 2024 doc (2022) + Minor Lessons v2.m4a'],None,None,'low','not read',''),
 ('JS-0016','Prevent The Fall','Jeff Story','original','','',
  ['NEW SONGS 2024 doc (2023) + "Prevent the fall 3.m4a"'],None,None,'low','not read',''),
 ('JS-0017','Starlight','Jeff Story','original','','',
  ['NEW SONGS 2024 doc (2022) + "Starlight vocals 2.m4a"'],None,None,'low','not read','Not the Taylor Swift song (that would be in Trailer Swift folders) — verify.'),
 ('JS-0018','Synonyms For Stubborn','Jeff Story','original','','',
  ['NEW SONGS 2024 doc (2022) + v1.1.wav'],None,None,'low','not read','Great title.'),
 ('JS-0019','Taking Flight','Jeff Story','original','','',
  ['NEW SONGS 2024 "Taking Flight 5-2-24 2.m4a" (no doc)'],None,None,'low','not read',''),
 ('JS-0020','The Catalyst','Jeff Story','original','','',
  ['NEW SONGS 2024 doc (2023) + m4a'],None,None,'low','not read','Verify not the Linkin Park song.'),
 ('JS-0021','Why Do I...','Jeff Story','original','','',
  ['NEW SONGS 2024 doc (2024-01) + m4a'],None,None,'low','not read',''),
 ('JS-0022','You Complete Me','Jeff Story','original','','',
  ['NEW SONGS 2024 doc (2021) + You Complete Me v1.0_1.wav'],None,None,'low','not read',''),
 ('JS-0023','Unjustified','Jeff Story','original','','',
  ['NEW SONGS 2024 "unjustified v1.3 drums.wav"'],None,None,'insufficient evidence','not found','Related to "Justify"? Same song? Flag for review.'),
]
for sid,t,art,cls,key,bpm,src,pot,rdy,conf,lys,notes in solo:
    songs.append(S(sid,t,art,cls,key=key,bpm=bpm,src=src,pot=pot,rdy=rdy,conf=conf,lys=lys,notes=notes,
                   stage='demo/mix' ))

# 2020 Lyrics deep archive — lyric-only entities (not yet read)
archive = ['A Simpler Life','Blindfolds','Bottom Of My Heart','Drums of War','Get Outta The City',
 'Go My Way','Heart Racing','Hey There','Independence Day','Insane','Life In America 2018','Mayhem',
 'Misery','My Muse Abuse','Old You','Our Last Night (Moonlight Pride)','Over 40','Resist',
 'Talk To Me','The World\'s Gonna End','Unity','Unknown Song','Room At The Top','Andrea (lyric rev 2023)']
for i,t in enumerate(archive, start=24):
    songs.append(S(f'JS-{i+ len(solo):04d}'.replace('JS-00','JS-00'), t, 'Jeff Story','original',
        stage='lyric only (deep archive)', src=['MUSIC/Lyrics (2020) folder'],
        conf='low', lys='not read', notes='Deep-archive lyric doc; unread. Batch-read in a later session.'))

# 2010 album-only tracks (recorded, released)
for i,t in enumerate(['Jettison','This Can\'t Be','My Mom Says We\'re Cool','I\'m A Loser',
                      'A New Girlfriend','Untrue','The Sky Is Blue','Over 18'], start=1):
    songs.append(S(f'ST-01{i:02d}', t, 'Stalemate','original', stage='released 2010',
        src=[f'My Mom Says We\'re Cool (2010 album)'], rec=100, conf='medium', lys='not read',
        aud='metadata only', notes='Finished 2010 recording exists. "Over 18" is DISTINCT from "It\'s Only Been 18".' if t=='Over 18' else 'Finished 2010 recording exists.'))
# Andrea has both album track + 2023 lyric revision — merge note
songs.append(S('ST-0110','Andrea','Stalemate','original', stage='released 2010, lyric revised 2023',
    src=['My Mom Says We\'re Cool track 03 (2010)','2020-Lyrics/Andrea doc (rev 2023-11)'],
    rec=100, conf='medium', lys='not read',
    notes='Jeff revised this lyric 13 years after release — something pulled him back. Hidden-gem queue.'))

# ============ SOMETHING DIRTY ============
sd = [
 ('SD-0001','I Hate This Part','original','',['2011 EP track 01 ("I Hate The Part")','SoundCloud 2012 (430 plays)','SD setlist 5-13-23'],'Title matches a Pussycat Dolls song but this is the 2011 SD original — verified distinct by era; lyric unverified.'),
 ('SD-0002','I\'m OK','original','',['2011 EP track 02'],''),
 ('SD-0003','Love In A Pill','original','',['2011 EP track 03'],''),
 ('SD-0004','Velvet Roses','original','G',['2011 EP track 04','SD setlist 5-13-23'],''),
 ('SD-0005','Day In The Life','original','',['2011 EP track 05','SoundCloud 2012 (476 plays — 2nd highest all-time)'],'Beatles-title ambiguity: probably an original sharing the title; VERIFY lyric before ranking. 476 plays = his most-heard band recording.'),
 ('SD-0006','Going To Cali','original','B',['2020-Lyrics doc (2019)','Going to Cali v1.0.logicx x2 (2022+2023)','SD - Going to Cali v3.0.logicx','SD setlist'],'THREE Logic projects = the most-arranged unreleased song in the vault. Priority listen.'),
 ('SD-0007','Cigarettes In A','original','A',['SD - Cigerettes in A v6.9.logicx (2023) — note v6.9!','SD setlist 5-13-23 *'],'v6.9 = ~7 project revisions. Someone loves this song. No lyric doc found.'),
 ('SD-0008','Bad Idea','original','Em',['SD setlist 5-13-23 *'],''),
 ('SD-0009','Dr Pepper','original','',['SD setlist 5-13-23 *'],''),
 ('SD-0010','Disconnect','original','C',['SD setlist 5-13-23 *'],''),
 ('SD-0011','Our Life','original','',['SD folder lyric doc (2014)'],''),
]
for sid,t,cls,key,src,notes in sd:
    songs.append(S(sid,t,'Something Dirty',cls,key=key,src=src,conf='low' if src else 'insufficient evidence',
        lys='not read', notes=notes, stage='varies'))

# ============ AUTHORSHIP-UNCERTAIN (dustduff90 "Structures, Progressions and Changes") ============
dd = ['Deadweight','She\'s Not All There','Rock Brigade','Captain Freedom\'s Workout','Catharsis',
      'Fool','Guns, Glory and Goners','mp3.com','Rockin\' R','Scapegoat','Searching','The End','Castle (Chains of Pain)']
for i,t in enumerate(dd, start=1):
    extra=''
    if t=='mp3.com': extra='Lyric namechecks "Jeff and Che got me squared away" — about joining this band.'
    if t=='Rock Brigade': extra='Shares a title with a Def Leppard song but the lyric is different/original.'
    if t.startswith('Castle'): extra='Castle v1.3.wav owned by dustduff90; Jeff\'s song list has "Chains of pain (castle)" — probable co-write.'
    songs.append(S(f'UNK-{i:04d}', t, 'Stalemate Split (Dust/dustduff90)','authorship uncertain',
        writers=['dustduff90 (probable)','Jeff Story (unknown)'], rights='uncertain — do NOT use externally',
        src=['Structures, Progressions and Changes doc (dustduff90@gmail.com, rev 2025-10-31)'] + (['Castle v1.3.wav'] if t.startswith('Castle') else []),
        conf='medium', lys='full text read' if t in('Deadweight','She\'s Not All There','Rock Brigade','Captain Freedom\'s Workout','Catharsis','Guns, Glory and Goners','mp3.com','Rockin\' R','Scapegoat','Searching') else 'partial',
        stage='split project', notes=('Part of an apparent Stalemate Split release with a collaborator. '+extra).strip(),
        oq='Who wrote what? These 12-13 songs appear ONLY in the collaborator\'s doc.'))

# ============ DORIVALLAND (dver.artist collaborator) ============
songs.append(S('UNK-0100','Dorivalland Song','collab: dver.artist','authorship uncertain',
    writers=['dver.artist','Jeff Story (unknown)'], rights='uncertain',
    src=['song lyrics/song ideas folder (dver.artist@gmail.com)','"What Happened in Dorivalland" doc — EDITED 2026-08-14, four days ago'],
    conf='low', lys='not read', stage='active collab?',
    notes='The Dorivalland doc was edited FOUR DAYS AGO — this is Jeff\'s most currently-active collaboration. Worth asking about.'))

# ============ COVERS & REFERENCE (kept OUT of original-song ranking) ============
covers = []
def C(t, orig, ctx): covers.append(dict(title=t, original_artist=orig, context=ctx, classification='cover'))
for t,a in [('First Date','Blink-182'),('She','Green Day'),('Linoleum','NOFX'),('Basket Case','Green Day'),
 ('American Idiot','Green Day'),('Holiday','Green Day'),('Brain Stew','Green Day'),('Jaded','Green Day'),
 ('When I Come Around','Green Day'),('Hitchin\' A Ride','Green Day'),('Longview','Green Day'),
 ('Holden Caulfield','Green Day'),('Christie Road','Green Day'),('Burnout','Green Day'),('Nice Guys Finish Last','Green Day'),
 ('86','Green Day'),('Novacaine','Green Day'),('Pulling Teeth','Green Day'),('Jesus of Suburbia','Green Day'),
 ('Knowledge','Operation Ivy/Green Day'),('Rebel Girl','Bikini Kill (listed under Green Day tab)'),
 ('Dammit','Blink-182'),('All The Small Things','Blink-182'),('The Rock Show','Blink-182'),('Aliens Exist','Blink-182'),
 ('Wendy Clear','Blink-182'),('Carousel','Blink-182'),('M&M\'s','Blink-182'),('Dick Lips','Blink-182'),
 ('Dumpweed','Blink-182'),('What\'s My Age Again?','Blink-182'),('Not Now','Blink-182'),('Asthenia','Blink-182'),
 ('I Won\'t Be Home For Christmas','Blink-182'),('Wasting Time (8-bit)','Blink-182'),
 ('Chick Magnet','MxPx'),('Tomorrow\'s Another Day','MxPx'),('Middle Name','MxPx'),('Responsibility','MxPx'),
 ('In Bloom','Nirvana'),('Breed','Nirvana'),('On A Plain','Nirvana'),('Territorial Pissings','Nirvana'),
 ('Santeria','Sublime'),('Ruby Soho','Rancid'),('KKK Took My Baby Away','Ramones'),('Blitzkrieg Bop','Ramones'),
 ('Sheena Is A Punk Rocker','Ramones'),('Stand By Me','Ben E. King via Pennywise'),('Blind','Face to Face'),
 ('Creep','Radiohead'),('My Own Worst Enemy','Lit'),('The Middle','Jimmy Eat World'),('1985','Bowling For Soup'),
 ('Come Back To Texas','Bowling For Soup'),('They Call Me Steve','Teenage Bottlerocket'),
 ('Somewhere On Fullerton','Allister'),('All My Fault','Riverfenix'),('Miles Away','Goldfinger'),
 ('The Anthem','Good Charlotte'),('In Too Deep','Sum 41'),('Fat Lip','Sum 41'),('Pieces (8-bit)','Sum 41'),
 ('Easy','Faith No More/Commodores'),('Knockin\' On Heaven\'s Door','Bob Dylan'),
 ('Where The Sidewalk Ends','?'),('Armatage Shanks','Green Day'),('No Cigar (8-bit)','Millencolin'),
 ('Gives You Hell (8-bit)','All-American Rejects'),('On A Plain (8-bit)','Nirvana'),
 ('Olympia WA (8-bit)','Rancid'),('Oi To The World','The Vandals'),('Grandma Got Run Over By A Reindeer','Elmo & Patsy'),
 ('I Celebrate The Day','Relient K'),('Christmas Medley','various'),('Ice Ice Baby','Vanilla Ice'),
 ('Somewhere Over The Rainbow','Arlen/Harburg'),('Saw Her Standing There','The Beatles'),
 ('Sparks Fly','Taylor Swift'),('The Story Of Us','Taylor Swift'),('Stay Stay Stay','Taylor Swift'),
 ('You Belong With Me','Taylor Swift'),('Ready For It','Taylor Swift'),('You Need To Calm Down','Taylor Swift'),
 ('Enchanted','Taylor Swift'),('Cruel Summer','Taylor Swift'),('Mine','Taylor Swift'),('Paper Rings','Taylor Swift'),
 ('Mean','Taylor Swift'),('I Knew You Were Trouble','Taylor Swift'),('All Too Well','Taylor Swift'),
 ('Ours','Taylor Swift'),('The Decline','NOFX')]:
    C(t,a,'Rad Dad / Stalemate sets / Trailer Swift / 8-bit series / SoundCloud')

# ---------- write outputs ----------
out = dict(
  generated='2026-08-18', session='Cowork session 1',
  honesty_note='NO AUDIO HAS BEEN LISTENED TO in this session. All audio: metadata only. All scores derive from lyric documents actually read (marked lyric_status="full text read") plus production evidence.',
  original_song_entities=len(songs), covers_reference=len(covers),
  songs=songs, covers=covers)
json.dump(out, open('/home/claude/vault/00_control_room/master_catalog.json','w'), indent=1)

cols=['song_id','canonical_title','artist_project','classification','alt_titles','writers','rights_confidence',
 'stage','key','bpm','potential','readiness','confidence','lyric_status','audio_status','theme','hook',
 'sources','soundcloud','best_source','next_action','open_questions','notes']
with open('/home/claude/vault/00_control_room/master_catalog.csv','w',newline='') as f:
    w=csv.writer(f); w.writerow(cols)
    for s in songs:
        w.writerow([('; '.join(s[c]) if isinstance(s[c],list) else s[c]) for c in cols])
with open('/home/claude/vault/00_control_room/covers_reference.csv','w',newline='') as f:
    w=csv.writer(f); w.writerow(['title','original_artist','context'])
    for c in covers: w.writerow([c['title'],c['original_artist'],c['context']])

print(f"songs: {len(songs)}  covers: {len(covers)}")
scored=[s for s in songs if s['potential']]
for s in sorted(scored,key=lambda x:-x['potential']):
    print(f"  {s['song_id']} {s['canonical_title']:28} pot={s['potential']} rdy={s['readiness']}")
