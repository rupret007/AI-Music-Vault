#!/usr/bin/env python3
# HISTORICAL one-shot. Do not re-run — writes /home/claude/vault/...
# Current spine: data/master_catalog.json · validate: scripts/validate_catalog.py
"""Catalog v1.4 — deep-archive read complete (all 2020-folder docs). Scores, reclassifications,
lineage merges. Also saves archive texts summary for future sessions."""
import json

cat = json.load(open('/home/claude/vault/00_control_room/master_catalog.json'))
idx = {s['song_id']: s for s in cat['songs']}
by_title = {s['canonical_title'].lower(): s for s in cat['songs']}
L='full text read'

def upd(key, pot, theme, hook, note, conf='medium'):
    s = by_title.get(key.lower()) or idx.get(key)
    if not s: print('MISS', key); return
    s['potential']=pot; s['lyric_status']=L; s['confidence']=conf
    if theme: s['theme']=theme
    if hook: s['hook']=hook
    s['notes']=(s['notes']+' '+note).strip()

# ---- NEW STRONG ENTRY ----
upd('Misery', 79, 'His wife watching his depression, 18 years in — sung from awareness of what it costs her',
 '"She\'s gettin\' real tired of my misery / I\'m only half of what I used to be"',
 'ARCHIVE STANDOUT (2019): hook 17, lyric 15 ("wanna-be rockstar in BIG D"), truth 19 (the empathy flip — her fatigue, not just his pain — is rare in this catalog), structure 12 (solo+bridge complete), identity 9, replay 7 = 79. TOP-6 SONG, previously invisible. On the UnRecorded list too.')

# ---- solid mid-tier ----
upd('Old You', 70, 'Wanting the person someone used to be — long-marriage erosion', '"I want the you I used to know / just look at the bright north star above"',
 'ARCHIVE: 70 — real ache, "drove to Maine" specificity; bridge darkens honestly. Logic project v3.2 exists (2022).')
upd('Our Last Night (Moonlight Pride)', 64, 'A relationship\'s last night, mental illness in the room', '"It\'s not right / this will be known as our last night"',
 'ARCHIVE: 64. SAME SONG FAMILY as "Go my way" (shares the "went my way / normal brain" verse) — treat Go my way as an ancestor draft, one entity.')
upd('Candi Lane', 70, None, None,
 'Candy Lane 2017 full read RAISES the ceiling: the life-arc verses (kid, empty nest, "one day one of us will go") are quietly devastating, and "especially because she likes my band" is the best tag of any version. Composite potential 70. Best-of-both edit is a real opportunity.')
upd('Blindfolds', 62, 'Keeping-up-with-the-neighbors consumerism satire (2016)', '"Their blindfolds are better than ours"',
 'ARCHIVE: 62 — the hook line is genuinely good; verses need tightening.')
upd('I\'m Sorry I\'m Crazy', 66, None, None, 'Full read confirms 66: charming shrug-apology; drop the "born this way" collision.')
upd('Life In America 2018', 58, 'State-of-the-nation lament with a family frame', '"This is life in America... where sanity is no longer found"',
 'ARCHIVE: 58 — Mommy/Daddy verses are the distinctive part.')
upd('Head in the Sand', 58, None, None, 'Full read (2012 doc) confirms 58; complete song, one clever turn.')
upd('Over 40', 60, 'Comedy narrative: over-40 guy, age-gap misadventure, jail-twist ending', '"God it sucks being over 40"',
 'ARCHIVE: 60 AS COMEDY — complete story arc with punchline; a live crowd-pleaser for the right room. Content is bawdy; fine for bars.')
upd('Heart Racing', 60, 'Panic/crisis from the inside — "mental jail"', '"I just can\'t handle mental jail"',
 'ARCHIVE: 60 — max honesty, minimal craft polish; part of the crisis cluster (What To Do, Why Do I..., Manic). Handle with care and Jeff\'s lead.')
upd('A Simpler Life', 55, 'Pastoral escape dream', '"A simpler life for you and me"',
 'ARCHIVE: 55. NOTE THE GARDEN MOTIF: "fresh garden" here, "under the garden" in Long Long Drive AND Life at the Bottom, "painting in the garden" in Our Last Night — a recurring Jeff image = candidate album/EP concept thread.')
upd('The World\'s Gonna End', 55, 'Apocalypse singalong satire (2012)', '"The world\'s gonna end (somebody stop it)"',
 'ARCHIVE: 55 — call-and-response structure is stage-ready; topical references date it.')
upd('Newfound Love', 62, None, None, 'Full read confirms 62.')
upd('Talk To Me', 58, 'Lost-muse plea, half-comic', '"I lost my muse... that\'s the worst thing to lose"',
 'ARCHIVE: 58.')
upd('Bottom Of My Heart', 56, 'Groveling win-back apology', '"you and I are meant to be Sublime"',
 'ARCHIVE: 56 — the Sublime pun is the personality moment.')
upd('Independence Day', 50, 'Lockdown-era freedom protest', None, 'ARCHIVE: 50 — of-its-moment.')
upd('Unity', 48, 'Teenage unity protest (2010)', None, 'ARCHIVE: 48 — period piece; "1,2,3 GO" is fun.')
upd('Drums of War', 52, 'Anti-apathy war warning (2015)', '"Apathy makes enemies"',
 'ARCHIVE: 52. NOTE: closing lines borrow the famous Dante-paraphrase ("hottest places in hell...") — attribution-safe (common paraphrase) but flag.')
upd('Get Outta The City', 45, None, None, 'ARCHIVE: fragment, 45.')
upd('My Muse Abuse', 45, None, None, 'ARCHIVE: fragment, 45; rabbit-hole image links to I Fall Down.')
upd('Mayhem', 42, 'Comedy dog elegy (craigslist pup named Mayhem, a.k.a. Dump Truck)', None, 'ARCHIVE: fragment, 42 — pure charm, no structure yet.')
upd('Unknown Song', 38, None, None, 'ARCHIVE: 8-line fragment, 38.')
upd('Insane', 30, None, None, 'ARCHIVE: 2-line phone-typo fragment, 30.')

# Go my way -> mark as ancestor of Our Last Night
g = by_title.get('go my way')
if g:
    g['classification']='draft/ancestor of Our Last Night (Moonlight Pride)'
    g['notes']=(g.get('notes','')+' Shares verse text with Our Last Night — same song family, earlier draft.').strip()

# ---- RECLASSIFY: covers/adaptations found in archive ----
recl = [
 ('Hey There','adaptation/parody — "Hey There Delilah" (Plain White T\'s) with rewritten Andrea lyric',
  'RECLASSIFIED: full text = Hey There Delilah melody/structure with Andrea substituted. NOT an original; never rank, never upload. "Hey There Andrea v.1.0.logicx" (2022) is the recording of this.'),
 ('Room At The Top','cover chart — Tom Petty "Room at the Top"','RECLASSIFIED: doc is a chord chart of the Petty song.'),
]
for t,cls,note in recl:
    s=by_title.get(t.lower())
    if s:
        s['classification']=cls; s['potential']=None; s['writers']=['(original artist)']
        s['rights_confidence']='cover/adaptation — excluded from originals; no external upload'
        s['lyric_status']=L; s['notes']=(s['notes']+' '+note).strip()

# Resist + Resist? merge note
r1=by_title.get('resist')
if r1:
    r1['alt_titles']=list(set(r1.get('alt_titles',[])+['Resist?','Resist Lyrics']))
    r1['potential']=52; r1['lyric_status']=L; r1['confidence']='medium'
    r1['notes']=(r1['notes']+' Two doc versions (2020, 2021) = one song; checklist-protest structure; datedness is the risk. 52.').strip()

# Song ideas doc note (sensitive)
cat['archive_notes'] = ('Lyrics(2020)/"Song ideas" (2019-20) contains raw crisis-era fragments referencing Andrea. '
 'Preserved, not ranked, not for external use. The crisis cluster (What To Do, Heart Racing, Why Do I..., Manic, Song ideas) '
 'is some of the most honest material in the catalog; development only at Jeff\'s pace and choice.')

cat['generated']='2026-08-18 v1.4 — lyric corpus COMPLETE for all located docs'
json.dump(cat, open('/home/claude/vault/00_control_room/master_catalog.json','w'), indent=1)

scored=[(s['potential'],s['song_id'],s['canonical_title']) for s in cat['songs'] if s.get('potential')]
scored.sort(reverse=True)
print(len(scored),'scored')
for p,i,t in scored[:16]: print(f"  {p}  {i}  {t}")
