#!/usr/bin/env python3
"""HISTORICAL Mac-local organizer (Cowork paths). Do not re-run from this repo.

Build the organized vault layer for Jeff's Mac.
Best-practice archival approach: originals are NEVER moved/renamed; this creates a
navigable catalog layer (song sheets + link indexes + symlink views) on top."""
import json, os, shutil, re, collections

OUT='/home/claude/vault_organized/Jeff Story Song Vault'
def safe(s): return re.sub(r'[/\\:*?"<>|]','-',s).strip()
for d in ['00 Control Room','01 Source Manifests','02 Song Records','03 Voice Memos',
          '04 Suno Experiments','05 Producer Briefs','06 Working Copies','99 Source Links - Do Not Delete']:
    os.makedirs(f'{OUT}/{d}', exist_ok=True)

# ---- 00 Control Room ----
CR='/home/claude/vault/00_control_room'
for f in ['THE PLAN.md','Producer README.md','Priority Queue.md','Needs Jeff.md','Decision Log.md',
          'Session Log.md','Access Gaps.md','Rights and AI Provenance.md','Hidden Gems Listen List - Batch 1.md',
          'Jeff Story Master Song Catalog.xlsx','master_catalog.csv','master_catalog.json','covers_reference.csv']:
    src=f'{CR}/{f}'
    if os.path.exists(src): shutil.copy(src, f'{OUT}/00 Control Room/{f}')

# ---- 01 Source Manifests ----
SM='/home/claude/vault/01_source_manifests'
os.makedirs(f'{OUT}/01 Source Manifests/Google Drive', exist_ok=True)
os.makedirs(f'{OUT}/01 Source Manifests/SoundCloud', exist_ok=True)
os.makedirs(f'{OUT}/01 Source Manifests/Voice Memos', exist_ok=True)
shutil.copy(f'{SM}/gdrive/inventory.jsonl', f'{OUT}/01 Source Manifests/Google Drive/inventory.jsonl')
shutil.copy(f'{SM}/gdrive/summary.md', f'{OUT}/01 Source Manifests/Google Drive/summary.md')
if os.path.exists(f'{SM}/soundcloud/inventory.json'):
    shutil.copy(f'{SM}/soundcloud/inventory.json', f'{OUT}/01 Source Manifests/SoundCloud/inventory.json')
for f in ['voice_memo_db_inventory.json','vm_matches.json','vm_unmatched.json','vm_triage_batch1_results.json','vm_probable_rehearsals.json']:
    p=f'{SM}/voicememo/{f}'
    if os.path.exists(p): shutil.copy(p, f'{OUT}/01 Source Manifests/Voice Memos/{f}')

# ---- 02 Song Records: one sheet per entity ----
cat=json.load(open(f'{CR}/master_catalog.json'))
songs=cat['songs']
def sheet(s):
    L=[f"# {s['song_id']} — {s['canonical_title']}",'']
    L.append(f"**Project:** {s['artist_project']} · **Class:** {s['classification']} · **Stage:** {s.get('stage','')}")
    L.append(f"**Writers:** {', '.join(s['writers'])} · **Rights:** {s['rights_confidence']}")
    if s.get('alt_titles'): L.append(f"**Also known as:** {', '.join(s['alt_titles'])}")
    kb=[]
    if s.get('key'): kb.append(f"Key {s['key']}")
    if s.get('bpm'): kb.append(f"BPM {s['bpm']}")
    if kb: L.append('**'+' · '.join(kb)+'**')
    L.append('')
    if s.get('potential') or s.get('readiness'):
        L.append(f"**Potential:** {s.get('potential') or '—'}/100 · **Readiness:** {s.get('readiness') or '—'}/100 · **Confidence:** {s['confidence']}")
    L.append(f"**Lyric status:** {s['lyric_status']} · **Audio status:** {s['audio_status']}")
    if s.get('theme'): L.append(f"\n**Theme:** {s['theme']}")
    if s.get('hook'): L.append(f"**Hook:** {s['hook']}")
    if s.get('sources'):
        L.append('\n## Known assets / sources')
        for x in s['sources']: L.append(f"- {x}")
    if s.get('soundcloud'):
        L.append('\n## SoundCloud')
        for x in s['soundcloud']: L.append(f"- {x}")
    if s.get('best_source'): L.append(f"\n**Best current source:** {s['best_source']}")
    if s.get('next_action'): L.append(f"\n**Next action:** {s['next_action']}")
    if s.get('open_questions'): L.append(f"\n**Open questions:** {s['open_questions']}")
    if s.get('notes'): L.append(f"\n## Producer notes\n{s['notes']}")
    L.append(f"\n---\n*Generated 2026-08-18 from master catalog v1.10. Originals never moved; this sheet is the index.*")
    return '\n'.join(L)

groups={'ST':'Stalemate','SD':'Something Dirty','JS':'Jeff Story solo','UN':'Collaborator - Uncertain'}
count=0
for s in songs:
    g=groups.get(s['song_id'][:2],'Other')
    d=f"{OUT}/02 Song Records/{g}"
    os.makedirs(d, exist_ok=True)
    open(f"{d}/{s['song_id']} - {safe(s['canonical_title'])}.md",'w').write(sheet(s))
    count+=1

# index
idx=['# Song Records Index — 141 entities','',
 '| ID | Title | Project | Potential | Readiness | Stage |','|---|---|---|---|---|---|']
for s in sorted(songs, key=lambda x:(-(x.get('potential') or 0), x['song_id'])):
    idx.append(f"| {s['song_id']} | {s['canonical_title']} | {s['artist_project']} | {s.get('potential') or ''} | {s.get('readiness') or ''} | {s.get('stage','')[:40]} |")
open(f'{OUT}/02 Song Records/INDEX.md','w').write('\n'.join(idx))

# ---- 99 Source Links: Drive URL index grouped by kind ----
recs=[json.loads(l) for l in open(f'{SM}/gdrive/inventory.jsonl')]
bykind=collections.defaultdict(list)
for r in recs: bykind[r.get('kind_guess','other')].append(r)
L=['# Google Drive Source Link Index','',
 f'{len(recs)} inventoried items. NEVER move, rename, or delete these originals — link to them.','']
for k in sorted(bykind):
    L.append(f'\n## {k} ({len(bykind[k])})')
    for r in sorted(bykind[k], key=lambda x:x['title'].lower()):
        url=r.get('viewUrl','')
        parent=r.get('parentName') or ''
        L.append(f"- [{r['title']}]({url}) — {parent} ({(r.get('modifiedTime') or '')[:10]})")
open(f'{OUT}/99 Source Links - Do Not Delete/Google Drive Index.md','w').write('\n'.join(L))

# ---- 04 / 05 ----
shutil.copy('/home/claude/vault/04_suno_experiments/EXP-001 Long Long Drive - Arrangement Test.md',
            f'{OUT}/04 Suno Experiments/EXP-001 Long Long Drive - Arrangement Test.md')
for f in os.listdir('/home/claude/vault/05_producer_briefs'):
    shutil.copy(f'/home/claude/vault/05_producer_briefs/{f}', f'{OUT}/05 Producer Briefs/{f}')
open(f'{OUT}/06 Working Copies/README.txt','w').write(
 'Working copies and exports only. Nothing in here is an original. Safe to regenerate.\n')

# ---- 03 Voice Memos: by-song symlink script (runs on the Mac) ----
vm=json.load(open(f'{SM}/voicememo/vm_matches.json'))
db=json.load(open(f'{SM}/voicememo/voice_memo_db_inventory.json'))
uid2={r['uid']:r for r in db}
id2title={s['song_id']:s['canonical_title'] for s in songs}
lines=['#!/bin/bash','# Creates "By Song" symlink views of matched voice memos. Originals untouched.',
 'VMI="$HOME/mnt/Music/Jeff Story Song Vault/Voice Memo Intake"',
 'OUT="$HOME/mnt/Music/Jeff Story Song Vault/03 Voice Memos/By Song"','mkdir -p "$OUT"']
n=0
for sid,uids in vm.items():
    t=id2title.get(sid)
    if not t: continue
    d=f"{sid} - {safe(t)}"
    lines.append(f'mkdir -p "$OUT/{d}"')
    for u in uids:
        r=uid2.get(u)
        if not r: continue
        fn=r['file'].split('/')[-1]
        title=safe(r['title'])[:60]
        lines.append(f'ln -sf "$VMI/{fn}" "$OUT/{d}/{r["date"][:10]} {title}.m4a" 2>/dev/null')
        n+=1
lines.append(f'echo "linked {n} memos into $(ls "$OUT" | wc -l) song folders"')
open(f'{OUT}/03 Voice Memos/link_memos_by_song.sh','w').write('\n'.join(lines))
open(f'{OUT}/03 Voice Memos/README.md','w').write(
 '# Voice Memos\n\nOriginals live in "Voice Memo Intake" (copies of your phone memos; the app originals are untouched).\n'
 'Run link_memos_by_song.sh (Claude does this) to build "By Song" folders of shortcuts — browse memos per song without duplicating audio.\n'
 'Unmatched/untitled memos: see 01 Source Manifests/Voice Memos/vm_unmatched.json and the Hidden Gems Listen List in the Control Room.\n')

print(f'built: {count} song sheets, drive index {len(recs)} links, memo link script {n} links')
EOF_MARKER_NOT_USED = None
