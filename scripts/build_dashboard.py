#!/usr/bin/env python3
"""Dashboard v2 — catalog v1.6 + Momentum Index + searchable memo transcripts.

First useful surface reuses data/app_api.json for StoryBoard import_scope.
Catalog rows are not the official live set. Show Night owns official sets.
Repo-relative paths (the old /home/claude/vault/... Cowork copies are gone).
Run from anywhere:  python3 scripts/build_dashboard.py
"""
import json, os, sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from catalog_surface import (  # noqa: E402
    ON_DECK_NOTE,
    SURFACE_SUBTITLE,
    build_memo_search_index,
    overlay_feed_scopes,
    played_badge_label,
    song_aliases,
    song_work_kind,
    surface_stage_label,
)

CAT_PATH = os.path.join(HERE, "data", "master_catalog.json")
API_PATH = os.path.join(HERE, "data", "app_api.json")
TX_PATH = os.path.join(HERE, "data", "vm_transcribed.json")
VM_MATCHES_PATH = os.path.join(HERE, "01_source_manifests", "voicememo", "vm_matches.json")
OUT_PATH = os.path.join(HERE, "Jeff Story Song Vault Dashboard.html")

cat = json.load(open(CAT_PATH))
app_api = json.load(open(API_PATH)) if os.path.exists(API_PATH) else {}
slim = []
for s in cat['songs']:
    row = dict(id=s['song_id'], t=s['canonical_title'], p=s['artist_project'],
        c=s['classification'], st=surface_stage_label(s.get('stage','')), key=s.get('key',''), bpm=s.get('bpm',''),
        pot=s.get('potential'), rdy=s.get('readiness'), mom=s.get('momentum'),
        la=s.get('last_activity',''), conf=s.get('confidence',''),
        th=s.get('theme',''), hk=s.get('hook',''), nx=s.get('next_action',''),
        ly=s.get('lyric_status',''), au=s.get('audio_status',''),
        src=s.get('sources',[]), sc=s.get('soundcloud',[]), oq=s.get('open_questions',''),
        wr=', '.join(s.get('writers',[])),
        live=played_badge_label(s.get('live_latest','')), lp=[f"{e['band']} ({e['date']})" for e in s.get('live_presence',[])],
        gate=s.get('ai_upload_ok',''), bs=s.get('best_source_resolved',''))
    aliases = song_aliases(s)
    if aliases:
        row['aka'] = aliases
    slim.append(row)
overlay_feed_scopes(slim, app_api)


def _lane_work_pill(song_id: str) -> str:
    row = next((item for item in slim if item.get("id") == song_id), None)
    kind = song_work_kind((row or {}).get("nx"))
    if not kind or kind == "unknown":
        return ""
    return f'<span class="pill wk-{kind} lane-work">{kind}</span>'

DATA = json.dumps(slim, ensure_ascii=False).replace('</', '<\\/')

# Transcripts: compact index (title, date, duration, cleaned text capped at 1500
# chars). Overlay song_id from vm_matches.json (372/88); the transcript file
# still carries the first-pass 326 matches. Source totals and searchable-index
# totals stay separate because short collapsed text is intentionally not useful
# enough to embed for search.
joined = json.load(open(TX_PATH))
matches_by_song = {}
if os.path.exists(VM_MATCHES_PATH):
    matches_by_song = json.load(open(VM_MATCHES_PATH))
tx, memo_counts = build_memo_search_index(joined, matches_by_song)
TX_TOTAL = memo_counts["transcribed"]
TX_MATCHED_TOTAL = memo_counts["matched"]
TX_SEARCHABLE_TOTAL = memo_counts["searchable"]
TX_SEARCHABLE_MATCHED = memo_counts["searchable_matched"]
TX = json.dumps(tx, ensure_ascii=False).replace('</', '<\\/')

page = r'''<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Jeff Story Song Vault</title>
<style>
:root{--bg:#1a1a19;--card:#242423;--card2:#2c2c2a;--ink:#ffffff;--ink2:#c3c2b7;--ink3:#8f8e85;
 --pot:#3987e5;--rdy:#d95926;--mom:#199e70;--line:#3a3a38;--good:#199e70;}
@media (prefers-color-scheme: light){:root{--bg:#fcfcfb;--card:#ffffff;--card2:#f3f3f0;--ink:#1a1a19;
 --ink2:#4a4a45;--ink3:#8f8e85;--pot:#2a78d6;--rdy:#eb6834;--mom:#1baf7a;--line:#e3e2dc;--good:#1baf7a;}}
*{box-sizing:border-box;margin:0;padding:0}
body{background:var(--bg);color:var(--ink);font:14px/1.5 -apple-system,'Segoe UI',Helvetica,Arial,sans-serif;padding:20px;max-width:980px;margin:0 auto}
h1{font-size:22px;letter-spacing:.4px} .sub{color:var(--ink2);margin:4px 0 16px}
.stats{display:flex;gap:10px;flex-wrap:wrap;margin-bottom:12px}
.stat{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:10px 14px;min-width:100px}
.stat b{font-size:20px;display:block} .stat span{color:var(--ink3);font-size:11px;text-transform:uppercase;letter-spacing:.5px}
.work-now{background:linear-gradient(135deg,var(--card),var(--card2));border:1px solid var(--line);border-radius:12px;padding:14px 16px;margin-bottom:16px}
.work-now h2{font-size:15px}.work-now p{color:var(--ink3);font-size:12px;margin:2px 0 10px}
.work-starts{display:flex;gap:8px;flex-wrap:wrap}
.work-start{background:var(--bg);color:var(--ink);border:1px solid var(--line);border-radius:9px;padding:9px 13px;cursor:pointer;font-weight:700}
.work-start span{color:var(--ink3);font-weight:500;margin-left:4px}
.work-start:hover,.work-start:focus-visible{border-color:var(--pot);outline:2px solid var(--pot);outline-offset:2px}
.resume-work{display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin-top:9px;padding-top:9px;border-top:1px solid var(--line)}
.resume-work .work-start{flex:1;text-align:left}
.resume-next{flex:1 1 100%;font-weight:700;color:var(--ink);max-width:650px}
.resume-work .primary-action{border-color:var(--pot);color:var(--ink)}
.resume-hint,.resume-status{color:var(--ink3);font-size:12px;margin:8px 0 0}
.resume-status{color:var(--ink2);min-height:1.2em}
.lanes{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:14px 16px;margin-bottom:16px}
.lanes h2{font-size:13px;text-transform:uppercase;letter-spacing:.6px;color:var(--ink2);margin-bottom:8px}
.lane{display:flex;gap:8px;align-items:baseline;padding:4px 0;border-bottom:1px dashed var(--line)}
.lane:last-child{border:none}
.tag{font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.5px;padding:2px 8px;border-radius:99px;background:var(--card2);color:var(--ink2);white-space:nowrap}
.tag.f{color:var(--pot)} .tag.q{color:var(--good)} .tag.x{color:var(--rdy)}
.tabs{display:flex;gap:6px;margin-bottom:12px}
.tab{padding:8px 16px;border-radius:99px;border:1px solid var(--line);background:var(--card);color:var(--ink2);cursor:pointer;font-size:13px;font-weight:600}
.tab.on{background:var(--card2);color:var(--ink);border-color:var(--ink3)}
.controls{display:flex;gap:8px;align-items:flex-start;flex-wrap:wrap;margin-bottom:12px;position:sticky;top:0;background:var(--bg);padding:8px 0;z-index:5}
input,select,.subtle-btn,.memo-link,.song-link{background:var(--card);color:var(--ink);border:1px solid var(--line);border-radius:8px;padding:8px 10px;font-size:13px}
input{flex:1;min-width:160px}
.advanced-filters{position:relative}
.advanced-filters summary{list-style:none;background:var(--card);color:var(--ink2);border:1px solid var(--line);border-radius:8px;padding:8px 10px;font-size:13px;cursor:pointer;font-weight:600}
.advanced-filters summary::-webkit-details-marker{display:none}
.advanced-filters summary::after{content:' +';color:var(--ink3)}
.advanced-filters[open] summary::after{content:' −'}
.advanced-menu{position:absolute;right:0;top:42px;display:grid;gap:8px;width:min(340px,calc(100vw - 40px));padding:10px;background:var(--card2);border:1px solid var(--line);border-radius:10px;box-shadow:0 12px 30px #0008;z-index:8}
.advanced-menu select{width:100%}
.row{background:var(--card);border:1px solid var(--line);border-radius:10px;margin-bottom:6px;overflow:hidden}
.rhead{display:grid;grid-template-columns:64px 1fr 110px 110px 110px;gap:8px;align-items:center;padding:10px 12px;cursor:pointer}
.rhead:hover,.rhead:focus-visible{background:var(--card2);outline:2px solid var(--pot);outline-offset:-2px}
@media(max-width:640px){.rhead{grid-template-columns:1fr 90px 90px}.rid,.bw-r{display:none}}
.rid{color:var(--ink3);font-size:11px;font-family:ui-monospace,Menlo,monospace}
.rtitle{font-weight:600} .rproj{color:var(--ink3);font-size:11px}
.barwrap{display:flex;align-items:center;gap:6px;font-size:11px;color:var(--ink2)}
.bar{height:6px;border-radius:4px;background:var(--card2);flex:1;overflow:hidden}
.bar i{display:block;height:100%;border-radius:4px}
.detail{padding:4px 14px 14px;border-top:1px solid var(--line);color:var(--ink2);font-size:13px}
[hidden]{display:none!important}
.detail h4{font-size:11px;text-transform:uppercase;letter-spacing:.5px;color:var(--ink3);margin:10px 0 3px}
.detail ul{margin-left:18px} .detail li{margin:2px 0}
.pill{display:inline-block;font-size:11px;background:var(--card2);border-radius:99px;padding:2px 9px;margin:2px 3px 2px 0;color:var(--ink2)}
.covers-note,.foot{color:var(--ink3);font-size:12px;margin:14px 0}
.legend{display:flex;gap:14px;font-size:11px;color:var(--ink2);margin:0 0 10px;flex-wrap:wrap}
.dot{display:inline-block;width:9px;height:9px;border-radius:2px;margin-right:5px;vertical-align:-1px}
.empty{color:var(--ink3);text-align:center;padding:30px}
.mrow{background:var(--card);border:1px solid var(--line);border-radius:10px;margin-bottom:6px;padding:10px 14px}
.mrow b{font-size:13px} .mmeta{color:var(--ink3);font-size:11px;margin-bottom:4px}
.msnip{color:var(--ink2);font-size:12.5px} .msnip mark,.rtitle mark,.aka-hit mark{background:var(--pot);color:#fff;border-radius:3px;padding:0 2px}
.mhint{color:var(--ink3);font-size:12px;padding:16px;text-align:center}
.resultbar,.memo-scope{display:flex;align-items:center;justify-content:space-between;gap:10px;color:var(--ink3);font-size:12px;margin:0 0 10px}
.memo-scope{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:9px 12px;color:var(--ink2)}
.subtle-btn,.memo-link,.song-link{cursor:pointer;font-weight:600}
.subtle-btn:disabled{opacity:.45;cursor:default}.memo-link,.song-link{padding:4px 8px;color:var(--pot)}
.song-link{border:0;background:transparent;padding:0;font-size:inherit;text-decoration:underline;text-underline-offset:2px}
.lane .song-link{font-weight:700;color:var(--ink)}
.memo-next{color:var(--ink3);font-size:12px;margin-top:3px}
.copied{color:var(--good)}
.pill.wk-write{color:var(--pot)}.pill.wk-produce{color:var(--rdy)}.pill.wk-listen{color:var(--mom)}
.work-copy,.sit-down{margin-top:8px}
.sit-memo{margin-top:4px}
.lane-work{margin-left:4px}
.work-session-copy{font-weight:700;color:var(--ink);margin-top:4px;max-width:650px}
.work-session-actions{display:flex;align-items:center;gap:6px;flex-wrap:wrap;justify-content:flex-end}
.work-session-actions .primary-action{border-color:var(--pot);color:var(--ink)}
@media(max-width:640px){.work-start{flex:1}.resume-work{align-items:stretch}.controls>input{flex-basis:100%}.advanced-filters{margin-left:auto}.memo-scope{align-items:flex-start;flex-direction:column}.work-session-actions{justify-content:flex-start}.advanced-menu{right:0}}
</style></head><body>
<h1>🎸 Jeff Story Song Vault</h1>
<div class="sub">Every song, one place · Catalog v1.6 · ''' + SURFACE_SUBTITLE + r''' · Momentum Index · __TX_TOTAL__ memos transcribed · __TX_SEARCHABLE_TOTAL__ usable-text transcripts searchable · no audio in this repo</div>
<div class="stats" id="stats"></div>
<section class="work-now" aria-labelledby="workNowTitle">
 <h2 id="workNowTitle">Start a work session</h2>
 <p>Pick one intention. The Vault opens one highest-momentum match and keeps the rest in a bounded queue. Refresh keeps that exact song in this browser. Resume names it and puts its sanitized next step in front of you. Forget clears the local record.</p>
 <div class="work-starts" id="workStarts"></div>
 <div class="resume-work" id="resumeWork" hidden>
  <button type="button" class="work-start" id="resumeWorkButton">Resume <span id="resumeWorkText"></span></button>
  <button type="button" class="subtle-btn" id="forgetWorkSession" aria-label="Forget this browser work session">Forget</button>
  <div class="resume-next" id="resumeWorkNext" hidden></div>
  <button type="button" class="subtle-btn primary-action" id="copyResumeNext" hidden>Copy next step</button>
 </div>
 <p class="resume-hint" id="resumeWorkHint" hidden>This browser keeps only a work kind and catalog ID. Forget clears it. The Session Log stays the handoff.</p>
 <p class="resume-status" id="resumeWorkStatus" aria-live="polite"></p>
</section>
<div class="lanes">
 <h2>The three lanes (+ on deck)</h2>
 <div class="lane"><span class="tag f">Flagship</span><button type="button" class="song-link" data-open-song="ST-0001">Turn Over The Flag</button> ''' + _lane_work_pill("ST-0001") + r'''<span style="color:var(--ink3)">— mix 1.6, two overdubs left</span></div>
 <div class="lane"><span class="tag q">Quick win</span><button type="button" class="song-link" data-open-song="ST-0004">Manic</button> ''' + _lane_work_pill("ST-0004") + r'''<span style="color:var(--ink3)">— ONE overdub (lead guitar: choruses + solos)</span></div>
 <div class="lane"><span class="tag x">Experimental</span><button type="button" class="song-link" data-open-song="ST-0009">Long Long Drive</button> ''' + _lane_work_pill("ST-0009") + r'''<span style="color:var(--ink3)">— Suno arrangement test queued</span></div>
 <div class="lane"><span class="tag">On deck</span><button type="button" class="song-link" data-open-song="JS-0128">It's Alright</button> ''' + _lane_work_pill("JS-0128") + r'''<span style="color:var(--ink3)">— ''' + ON_DECK_NOTE + r'''; lyric 85% recovered; takes Manic's slot next</span></div>
 <div class="lane"><span class="tag">The Opus</span><button type="button" class="song-link" data-open-song="JS-0107">Blue Skies Fade</button> ''' + _lane_work_pill("JS-0107") + r'''<span style="color:var(--ink3)">— Kimberly's suite; its own protected lane</span></div>
</div>
<div class="tabs" role="tablist" aria-label="Vault views">
 <button type="button" class="tab on" id="tabS" role="tab" aria-controls="paneS" aria-selected="true">Songs</button>
 <button type="button" class="tab" id="tabM" role="tab" aria-controls="paneM" aria-selected="false">Memo Search (__TX_SEARCHABLE_TOTAL__ searchable)</button>
</div>
<div id="paneS" role="tabpanel" aria-labelledby="tabS">
<div class="controls">
 <input id="q" placeholder="Search titles, aliases, hooks… (try: candy lane, only 18, garden)" autocomplete="off" aria-label="Search songs by title, alias, hook, or memo lyric">
 <select id="sort">
  <option value="mom">Sort: Momentum (what's alive)</option>
  <option value="pot">Sort: Potential</option><option value="rdy">Sort: Readiness</option>
  <option value="id">Sort: Catalog ID</option><option value="t">Sort: Title</option>
  <option value="memo">Sort: Latest memo evidence</option></select>
 <details class="advanced-filters" id="advancedFilters"><summary>More filters</summary><div class="advanced-menu">
  <select id="proj"><option value="">All projects</option></select>
  <select id="scored"><option value="">All songs</option><option value="1">Scored only</option><option value="0">Unscored / to explore</option></select>
  <select id="scope"><option value="">All StoryBoard scopes</option></select>
  <select id="evidence"><option value="">Any memo evidence</option><option value="1">Has searchable memos</option><option value="0">No searchable memos</option></select>
  <select id="work"><option value="">Any work</option><option value="write">Write</option><option value="produce">Produce</option><option value="listen">Listen</option><option value="rest">Rest</option><option value="inventory">Inventory</option><option value="decide">Decide</option></select>
 </div></details>
</div>
<div class="resultbar"><span id="songResults" aria-live="polite"></span><button type="button" class="subtle-btn" id="clearSongFilters">Clear filters</button></div>
<div class="memo-scope" id="workSession" hidden><div><span id="workSessionText"></span><div class="work-session-copy" id="workSessionNext" hidden></div><div class="memo-next" id="workSessionEvidence"></div></div><span class="work-session-actions"><button type="button" class="subtle-btn primary-action" id="copyWorkNext" hidden>Copy next step</button> <button type="button" class="subtle-btn" id="openWorkEvidence" hidden>Review memo evidence</button> <button type="button" class="subtle-btn" id="workPrev" data-work-step="-1">Previous</button> <button type="button" class="subtle-btn" id="workNext" data-work-step="1">Next</button></span></div>
<div class="legend"><span><span class="dot" style="background:var(--pot)"></span>Potential /100</span>
<span><span class="dot" style="background:var(--rdy)"></span>Readiness /100</span>
<span><span class="dot" style="background:var(--mom)"></span>Momentum /100 (how alive it is in your hands)</span></div>
<div id="list"></div>
<div class="covers-note">93 covers cataloged separately, never ranked against originals. Catalog rows are not the official set. Show Night owns official sets. Spine: data/master_catalog.json · StoryBoard feed: data/app_api.json · validate: python3 scripts/validate_catalog.py</div>
</div>
<div id="paneM" role="tabpanel" aria-labelledby="tabM" hidden>
<div class="controls"><input id="mq" placeholder="Search __TX_SEARCHABLE_TOTAL__ usable transcript snippets… (try: alright, garden, better than now)"></div>
<div class="memo-scope" id="memoScope" hidden><div><span id="memoScopeText"></span><div class="memo-next" id="memoScopeNext" hidden></div><div class="memo-next" id="memoScopeHook" hidden></div></div><span><button type="button" class="subtle-btn" id="copyMemoWork" hidden data-copy-work="">Copy work card</button> <button type="button" class="subtle-btn" id="clearMemoScope">Show all memos</button></span></div>
<div id="mlist"><div class="mhint">Type 3+ letters to search __TX_SEARCHABLE_TOTAL__ usable-text transcripts. Source truth: __TX_TOTAL__ transcribed and __TX_MATCHED_TOTAL__ matched; __TX_SEARCHABLE_MATCHED__ matched rows have enough text for this search index. Transcripts are machine-made (Whisper, run locally on your Mac) — they mishear sung words constantly, so treat hits as leads, not gospel.</div></div>
</div>
<div class="foot">Originals never moved or renamed — this is an index on top. Three active songs only (flagship / quick win / experimental). Blue Skies Fade stays its own protected lane. Logic projects, keys, and WAVs stay on your Mac — this page does not open audio.</div>
<script>
const DATA = __DATA__;
const TX = __TX__;
const TX_TOTAL = __TX_TOTAL__;
const TX_MATCHED_TOTAL = __TX_MATCHED_TOTAL__;
const TX_SEARCHABLE_TOTAL = __TX_SEARCHABLE_TOTAL__;
const TX_SEARCHABLE_MATCHED = __TX_SEARCHABLE_MATCHED__;
const WORK_SESSION_KEY='vault:last-work:v1';
const q=document.getElementById('q'),proj=document.getElementById('proj'),
 sort=document.getElementById('sort'),scored=document.getElementById('scored'),
 scope=document.getElementById('scope'),evidence=document.getElementById('evidence'),
 work=document.getElementById('work'),workStarts=document.getElementById('workStarts'),
 list=document.getElementById('list'),
 songResults=document.getElementById('songResults'),clearSongFilters=document.getElementById('clearSongFilters'),
 workSession=document.getElementById('workSession'),workSessionText=document.getElementById('workSessionText'),
 workSessionNext=document.getElementById('workSessionNext'),workSessionEvidence=document.getElementById('workSessionEvidence'),
 copyWorkNext=document.getElementById('copyWorkNext'),openWorkEvidence=document.getElementById('openWorkEvidence'),
 workPrev=document.getElementById('workPrev'),workNext=document.getElementById('workNext'),
 resumeWork=document.getElementById('resumeWork'),resumeWorkButton=document.getElementById('resumeWorkButton'),
 resumeWorkText=document.getElementById('resumeWorkText'),forgetWorkSession=document.getElementById('forgetWorkSession'),
 resumeWorkHint=document.getElementById('resumeWorkHint'),resumeWorkStatus=document.getElementById('resumeWorkStatus'),
 resumeWorkNext=document.getElementById('resumeWorkNext'),copyResumeNext=document.getElementById('copyResumeNext'),
 tabS=document.getElementById('tabS'),tabM=document.getElementById('tabM'),
 paneS=document.getElementById('paneS'),paneM=document.getElementById('paneM'),
 mq=document.getElementById('mq'),mlist=document.getElementById('mlist'),
 memoScope=document.getElementById('memoScope'),memoScopeText=document.getElementById('memoScopeText'),
 memoScopeNext=document.getElementById('memoScopeNext'),
 memoScopeHook=document.getElementById('memoScopeHook'),
 copyMemoWork=document.getElementById('copyMemoWork'),
 clearMemoScope=document.getElementById('clearMemoScope');
let lastWorkKind='';
let visibleSongIds=[];
let activeWorkSongId='';
const sname={}; DATA.forEach(d=>sname[d.id]=d.t);
const memoEvidenceBySong={};
const memoCountBySong={};
TX.forEach(m=>{
 if(m.s&&sname[m.s]){
  const ev=memoEvidenceBySong[m.s]||(memoEvidenceBySong[m.s]={n:0,first:'',last:''});
  ev.n+=1;
  if(m.d&&(!ev.first||m.d<ev.first))ev.first=m.d;
  if(m.d&&(!ev.last||m.d>ev.last))ev.last=m.d;
  memoCountBySong[m.s]=ev.n;
 }
});
let activeMemoSong='';
function showTab(w){
 const memo=w==='M';
 paneS.hidden=memo;paneM.hidden=!memo;
 tabS.classList.toggle('on',!memo);tabM.classList.toggle('on',memo);
 tabS.setAttribute('aria-selected',String(!memo));tabM.setAttribute('aria-selected',String(memo));
}
const projects=[...new Set(DATA.map(d=>d.p))].sort();
projects.forEach(p=>{const o=document.createElement('option');o.value=p;o.textContent=p;proj.appendChild(o);});
const scopes=[...new Set(DATA.map(d=>d.scope).filter(Boolean))].sort();
scopes.forEach(s=>{const o=document.createElement('option');o.value=s;o.textContent=(DATA.find(d=>d.scope===s)||{}).scope_label||s;scope.appendChild(o);});
const scoredCount=DATA.filter(d=>d.pot).length;
const defaultLiveCount=DATA.filter(d=>d.scope==='default_live').length;
const workCounts={write:0,produce:0,listen:0};
DATA.forEach(d=>{const wk=songWorkKind(d.nx);if(workCounts[wk]!=null)workCounts[wk]+=1;});
document.getElementById('stats').innerHTML=
 `<div class="stat"><b>${DATA.length}</b><span>songs cataloged</span></div>`+
 `<div class="stat"><b>${scoredCount}</b><span>scored</span></div>`+
 `<div class="stat"><b>${defaultLiveCount}</b><span>default-live catalog</span></div>`+
 `<div class="stat"><b>9</b><span>songs recovered from memos</span></div>`+
 `<div class="stat"><b>${TX_MATCHED_TOTAL}</b><span>memos matched</span></div>`+
 `<div class="stat"><b>${TX_SEARCHABLE_TOTAL}</b><span>memos searchable</span></div>`+
 `<div class="stat"><b>${TX_TOTAL}</b><span>memos transcribed</span></div>`;
workStarts.innerHTML=['write','produce','listen'].map(kind=>
 `<button type="button" class="work-start" data-open-work="${kind}">${kind[0].toUpperCase()+kind.slice(1)} <span>${workCounts[kind]} songs</span></button>`
).join('');
function esc(s){return (s===null||s===undefined?'':String(s)).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&#39;');}
function flattenWorkField(value){
 if(value==null)return '';
 if(Array.isArray(value))return value.map(v=>String(v||'').trim()).filter(Boolean).join('; ');
 return String(value).trim();
}
function songWorkKind(nx){
 const text=String(nx||'').trim();
 if(!text)return 'unknown';
 const low=text.toLowerCase();
 if(low.startsWith('released')||low.includes('archive-with-honor')||low.includes('not a development priority')||low.includes('rests unless'))return 'rest';
 if(low.includes('inventory pass')||low.includes('no dated source')||low.includes('voice memo intake')||low.includes('connector limit'))return 'inventory';
 if(['chorus lines','transcribe','read lyric','locate/transcribe','hum 30','has lyric','lyric rethink','confirm the 2','catch the real chorus'].some(m=>low.includes(m)))return 'write';
 if(['overdub','bounce mix','track background','record lead guitar','record bridge','add rhythm guitar','full-band arrangement','arrangement built'].some(m=>low.includes(m)))return 'produce';
 if(low.startsWith('listen')||low.includes('listen:')||low.includes('listen first')||low.includes('listen + verdict'))return 'listen';
 if(low.startsWith('decide')||low.startsWith('hold for')||low.includes('candidate for next-ep'))return 'decide';
 return 'unknown';
}
function parseStoredWorkSession(raw,names,rows){
 try{
  const value=typeof raw==='string'?JSON.parse(raw):raw;
  if(!value||typeof value!=='object'||Array.isArray(value)||value.v!==1)return null;
  if(Object.keys(value).sort().join('|')!=='id|kind|v')return null;
  const kind=String(value.kind||''),id=String(value.id||'');
  if(kind!=='write'&&kind!=='produce'&&kind!=='listen'&&kind!=='rest'&&kind!=='inventory'&&kind!=='decide')return null;
  if(!id||!names||!names[id]||!Array.isArray(rows))return null;
  const song=rows.find(row=>row&&row.id===id);
  if(!song||songWorkKind(song.nx)!==kind)return null;
  return {v:1,kind,id};
 }catch(err){return null;}
}
function readStoredWorkSession(storage,names,rows){
 if(!storage||typeof storage.getItem!=='function')return null;
 try{
  const raw=storage.getItem(WORK_SESSION_KEY);
  if(!raw)return null;
  const parsed=parseStoredWorkSession(raw,names,rows);
  if(!parsed&&typeof storage.removeItem==='function')storage.removeItem(WORK_SESSION_KEY);
  return parsed;
 }catch(err){return null;}
}
function storeWorkSession(storage,kind,id,names,rows){
 const parsed=parseStoredWorkSession({v:1,kind:String(kind||''),id:String(id||'')},names,rows);
 if(!parsed||!storage||typeof storage.setItem!=='function')return false;
 try{
  storage.setItem(WORK_SESSION_KEY,JSON.stringify(parsed));
  return true;
 }catch(err){return false;}
}
function clearStoredWorkSession(storage){
 if(!storage||typeof storage.removeItem!=='function')return false;
 try{storage.removeItem(WORK_SESSION_KEY);return true;}catch(err){return false;}
}
function vaultStorage(){
 try{return typeof window!=='undefined'?window.localStorage:null;}catch(err){return null;}
}
function announceWorkSession(message){
 if(typeof resumeWorkStatus==='undefined'||!resumeWorkStatus)return;
 resumeWorkStatus.textContent=String(message||'');
}
function applyWorkHash(kind,saved){
 const k=String(kind||'');
 const id=saved&&saved.kind===k?String(saved.id||''):'';
 return openWork(k,id);
}
function forgetWorkSessionResult(cleared,remaining){
 if(cleared&&!remaining)return {ok:true,message:'Forgot this browser record.'};
 if(remaining)return {ok:false,message:'Could not clear this browser record.'};
 return {ok:false,message:''};
}
function updateResumeWork(){
 if(typeof resumeWork==='undefined'||!resumeWork)return null;
 const saved=readStoredWorkSession(vaultStorage(),sname,DATA);
 resumeWork.hidden=!saved;
 if(typeof resumeWorkHint!=='undefined'&&resumeWorkHint)resumeWorkHint.hidden=!saved;
 const song=saved&&typeof DATA!=='undefined'?DATA.find(row=>row&&row.id===saved.id):null;
 const next=typeof safeWorkNextStep==='function'?safeWorkNextStep(song):'';
 if(saved&&resumeWorkText){
  const label=saved.kind[0].toUpperCase()+saved.kind.slice(1);
  const title=sname[saved.id]||'';
  resumeWorkText.textContent=`${label} · ${title}`;
  if(resumeWorkButton)resumeWorkButton.setAttribute('aria-label',`Resume ${label} session for ${title}`);
 }
 if(resumeWorkNext){
  resumeWorkNext.hidden=!next;
  resumeWorkNext.textContent=next?`Do this now: ${next}`:'';
 }
 if(copyResumeNext){
  copyResumeNext.hidden=!next;
  copyResumeNext.disabled=!next;
  copyResumeNext.dataset.songId=next&&song?String(song.id||''):'';
  copyResumeNext.setAttribute('aria-label',next&&song?`Copy next step for ${sname[song.id]||song.id}`:'No safe next step to copy');
 }
 return saved;
}
function rememberWorkSession(kind,id){
 const saved=storeWorkSession(vaultStorage(),kind,id,sname,DATA);
 updateResumeWork();
 return saved;
}
function resumeLastWorkSession(){
 const saved=readStoredWorkSession(vaultStorage(),sname,DATA);
 if(!saved){
  clearStoredWorkSession(vaultStorage());
  updateResumeWork();
  announceWorkSession('No matching browser record to resume.');
  return false;
 }
 announceWorkSession('');
 return openWork(saved.kind,saved.id);
}
function forgetLastWorkSession(){
 const storage=vaultStorage();
 const cleared=clearStoredWorkSession(storage);
 const remaining=readStoredWorkSession(storage,sname,DATA);
 const result=forgetWorkSessionResult(cleared,remaining);
 if(result.ok){
  if(typeof lastWorkKind!=='undefined')lastWorkKind='';
  if(typeof writeVaultHash==='function')writeVaultHash('','');
 }
 updateResumeWork();
 announceWorkSession(result.message);
 return result.ok;
}
function stripPrivateLocators(text){
 let s=String(text||'');
 s=s.replace(/\([^()]{0,200}\.(?:wav|aiff|aif|logicx|m4a|mp3|flac|band)\)/ig,'');
 s=s.replace(/\b[\w./' -]+\.(?:wav|aiff|aif|logicx|m4a|mp3|flac|band)\b/ig,'');
 s=s.replace(new RegExp('file:'+'//\\S+','ig'),'');
 s=s.replace(/\b(?:Maxwell Dr|Crescent Dr|Eagle Mountain Dr)\b[^,.;]*/ig,'');
 return s.replace(/\s{2,}/g,' ').replace(/\s+([,.;:])/g,'$1').replace(/^[\s-]+|[\s-]+$/g,'');
}
function workCardLeaks(text){
 const low=String(text||'').toLowerCase();
 if(low.includes('file:'+'//'))return true;
 if(/\.(wav|aiff|aif|logicx|m4a|mp3|flac|band)\b/.test(low))return true;
 return low.includes('maxwell dr')||low.includes('crescent dr')||low.includes('eagle mountain dr');
}
function nextStepIsIncomplete(text){
 return ['open','play','listen','listen to latest','listen: play'].includes(String(text||'').toLowerCase().replace(/[ .:]+$/,''));
}
function safeWorkNextStep(song){
 if(!song)return '';
 const next=stripPrivateLocators(flattenWorkField(song.nx));
 return next&&!nextStepIsIncomplete(next)&&!workCardLeaks(next)?next:'';
}
function latestMemoForSong(songId,rows){
 const id=String(songId||'');
 const src=rows||(typeof TX!=='undefined'?TX:[]);
 let best=null;
 for(const m of src){
  if(!m||String(m.s||'')!==id)continue;
  if(!best){best=m;continue;}
  const dd=String(m.d||'').localeCompare(String(best.d||''));
  if(dd>0||(dd===0&&String(m.f||'').localeCompare(String(best.f||''))>0))best=m;
 }
 return best;
}
function buildSongWorkCard(song,evidence){
 if(!song)return '';
 const kind=songWorkKind(song.nx);
 const title=flattenWorkField(song.t), id=flattenWorkField(song.id);
 const lines=[];
 if(title||id)lines.push(title?(id?title+' ('+id+')':title):id);
 const aliases=typeof songAliases==='function'?songAliases(song):[];
 if(aliases.length)lines.push('Also known as: '+aliases.join('; '));
 lines.push('Work: '+kind);
 const nx=safeWorkNextStep(song);
 if(nx)lines.push('Next: '+nx);
 const hk=stripPrivateLocators(flattenWorkField(song.hk));
 if(hk)lines.push('Hook: '+hk);
 const th=stripPrivateLocators(flattenWorkField(song.th));
 if(th)lines.push('Theme: '+th);
 const oq=stripPrivateLocators(flattenWorkField(song.oq));
 if(oq)lines.push('Open questions: '+oq);
 const ly=stripPrivateLocators(flattenWorkField(song.ly));
 if(ly)lines.push('Lyrics: '+ly);
 const au=stripPrivateLocators(flattenWorkField(String(song.au||'').split('—')[0]));
 if(au)lines.push('Audio: '+au);
 if(song.key)lines.push('Key: '+String(song.key));
 if(song.bpm)lines.push('BPM: '+String(song.bpm));
 const gate=flattenWorkField(String(song.gate||'').split('—')[0]);
 if(gate)lines.push('Gate: '+gate);
 const ev=evidence||(song&&typeof memoEvidenceBySong!=='undefined'&&memoEvidenceBySong[song.id])||null;
 if(ev&&ev.n)lines.push('Memos: '+ev.n+' searchable'+(ev.last?' · latest '+ev.last:''));
 const card=lines.filter(Boolean).join('\n');
 return workCardLeaks(card)?'':card;
}
function normalizeSearch(text){
 return String(text||'').toLowerCase().replace(/['’`]/g,'').replace(/[^a-z0-9]+/g,' ').trim().replace(/\s+/g,' ');
}
function songAliases(row){
 const raw=row&&row.aka;
 if(!Array.isArray(raw))return [];
 const title=normalizeSearch(row.t||'');
 const out=[], seen={};
 raw.forEach(item=>{
  const name=String(item||'').trim();
  const key=normalizeSearch(name);
  if(!name||!key||seen[key]||(title&&key===title))return;
  seen[key]=true;out.push(name);
 });
 return out;
}
const memoLyricNormBySong={};
function memoLyricNorm(songId){
 const id=String(songId||'');
 if(id&&Object.prototype.hasOwnProperty.call(memoLyricNormBySong,id))return memoLyricNormBySong[id];
 const parts=[];
 (typeof TX!=='undefined'?TX:[]).forEach(m=>{
  if(m&&String(m.s||'')===id&&m.x)parts.push(String(m.x));
 });
 const norm=normalizeSearch(parts.join(' '));
 if(id)memoLyricNormBySong[id]=norm;
 return norm;
}
function songSearchHit(row,term){
 if(!row)return {hit:false,rank:99,via:''};
 const norm=normalizeSearch(term);
 if(!norm)return {hit:true,rank:99,via:''};
 const names=[];
 if(row.id)names.push(normalizeSearch(row.id));
 if(row.t)names.push(normalizeSearch(row.t));
 songAliases(row).forEach(alias=>names.push(normalizeSearch(alias)));
 const kept=names.filter(Boolean);
 const qtok=norm.split(' ').filter(Boolean);
 if(kept.some(name=>name===norm))return {hit:true,rank:0,via:'name'};
 if(qtok.length&&kept.some(name=>{
  const toks=name.split(' ').filter(Boolean);
  return toks.length>=qtok.length&&toks.slice(0,qtok.length).join(' ')===qtok.join(' ');
 }))return {hit:true,rank:0,via:'name'};
 if(kept.some(name=>name.startsWith(norm)))return {hit:true,rank:1,via:'name'};
 if(kept.some(name=>name.includes(norm)))return {hit:true,rank:2,via:'name'};
 const audio=String(row.au||'').split('—')[0];
 const field=normalizeSearch([row.th,row.hk,row.c,row.st,row.wr,stripPrivateLocators(row.nx||''),row.oq,row.gate,row.scope_label,row.ly,audio,row.key].join(' '));
 if(field.includes(norm))return {hit:true,rank:3,via:'field'};
 if(norm.length>=3&&memoLyricNorm(row.id).includes(norm))return {hit:true,rank:4,via:'memo'};
 return {hit:false,rank:99,via:''};
}
function markNormalized(text,term){
 const src=String(text||'');
 const needle=normalizeSearch(term);
 if(!needle)return esc(src);
 const units=[];
 let norm='';
 let pendingSpace=false;
 for(let i=0;i<src.length;i++){
  const ch=src[i];
  if(/['’`]/.test(ch))continue;
  if(/[0-9A-Za-z]/.test(ch)){
   if(pendingSpace&&norm){norm+=' ';units.push({start:i,end:i});}
   pendingSpace=false;
   norm+=ch.toLowerCase();
   units.push({start:i,end:i+1});
  }else pendingSpace=true;
 }
 const at=norm.indexOf(needle);
 if(at<0||!units[at]||!units[at+needle.length-1])return esc(src);
 const start=units[at].start;
 const end=units[at+needle.length-1].end||units[at+needle.length-1].start;
 return esc(src.slice(0,start))+'<mark>'+esc(src.slice(start,end))+'</mark>'+esc(src.slice(end));
}
function sortSongRows(rows,term,sortKey){
 const decorated=rows.map(row=>({row,hit:term?songSearchHit(row,term):{hit:true,rank:99,via:''}}));
 decorated.sort((a,b)=>{
  if(term&&a.hit.rank!==b.hit.rank)return a.hit.rank-b.hit.rank;
  const k=sortKey||'mom';
  if(k==='memo'){
   const ea=(typeof memoEvidenceBySong!=='undefined'&&memoEvidenceBySong[a.row.id])||{n:0,last:''};
   const eb=(typeof memoEvidenceBySong!=='undefined'&&memoEvidenceBySong[b.row.id])||{n:0,last:''};
   const da=String(ea.last||''), db=String(eb.last||'');
   if(!da&&!db)return (eb.n-ea.n)||a.row.id.localeCompare(b.row.id);
   if(!da)return 1;
   if(!db)return -1;
   return db.localeCompare(da)||(eb.n-ea.n)||a.row.id.localeCompare(b.row.id);
  }
  if(k==='t')return a.row.t.localeCompare(b.row.t)||a.row.id.localeCompare(b.row.id);
  if(k==='id')return a.row.id.localeCompare(b.row.id);
  return ((b.row[k]||0)-(a.row[k]||0))||a.row.id.localeCompare(b.row.id);
 });
 return decorated;
}
function bar(v,c){
 const n=Number(v);
 if(!Number.isFinite(n)||n<=0)return '<div class="barwrap"><span style="color:var(--ink3)">—</span></div>';
 const safe=Math.min(100,Math.max(0,n));
 return `<div class="barwrap"><div class="bar"><i style="width:${safe}%;background:var(--${c})"></i></div><span>${esc(n)}</span></div>`;
}
function render(){
 const rawTerm=q.value, term=String(rawTerm||'').trim(), pv=proj.value, sv=scored.value, scv=scope.value,
  evv=(typeof evidence!=='undefined'&&evidence)?evidence.value:'',
  wv=(typeof work!=='undefined'&&work)?work.value:'';
 const filtered=[];
 DATA.forEach(d=>{
  if(pv&&d.p!==pv)return;
  if(scv&&d.scope!==scv)return;
  if(sv==='1'&&!d.pot)return; if(sv==='0'&&d.pot)return;
  if(evv==='1'&&!memoEvidenceBySong[d.id])return;
  if(evv==='0'&&memoEvidenceBySong[d.id])return;
  if(wv&&songWorkKind(d.nx)!==wv)return;
  const hit=term?songSearchHit(d,term):{hit:true,rank:99,via:''};
  if(hit.hit)filtered.push(d);
 });
 const k=sort.value;
 const decorated=sortSongRows(filtered,term,k);
 const rows=decorated.map(item=>item.row);
 const viaById={};
 decorated.forEach(item=>{viaById[item.row.id]=item.hit.via;});
 songResults.textContent=term
  ?`Showing ${rows.length} of ${DATA.length} songs · closest name first`
  :`Showing ${rows.length} of ${DATA.length} songs`;
 clearSongFilters.disabled=!(term||pv||sv||scv||evv||wv||k!=='mom');
 if(typeof visibleSongIds!=='undefined')visibleSongIds=rows.map(d=>d.id);
 list.innerHTML=rows.length?rows.map((d,i)=>{
  const wk=songWorkKind(d.nx);
  const rawNx=flattenWorkField(d.nx);
  const nxt=safeWorkNextStep(d);
  const nxtShort=nxt.length>90?nxt.slice(0,87)+'…':nxt;
  const latest=latestMemoForSong(d.id);
  const hook=stripPrivateLocators(flattenWorkField(d.hk));
  const theme=stripPrivateLocators(flattenWorkField(d.th));
  const questions=stripPrivateLocators(flattenWorkField(d.oq));
  const aliases=songAliases(d);
  const akaLabel=aliases.length?aliases.join(' · '):'';
  const via=viaById[d.id]||'';
  return `
 <div class="row" data-song-id="${esc(d.id)}"><div class="rhead" role="button" tabindex="0" aria-expanded="false" data-toggle-song>
  <span class="rid">${esc(d.id)}</span>
  <span><span class="rtitle">${markNormalized(d.t,term)}${d.live?` <span class="pill">${esc(d.live)}</span>`:''}${d.scope_label?` <span class="pill">${esc(d.scope_label)}</span>`:''}${wk&&wk!=='unknown'?` <span class="pill wk-${esc(wk)}">${esc(wk)}</span>`:''}${akaLabel?` <span class="pill aka-hit">aka ${markNormalized(akaLabel,term)}</span>`:''}${via==='memo'?` <span class="pill">memo lyric</span>`:''}${memoEvidenceBySong[d.id]?` <button type="button" class="pill memo-link" data-open-memos="${esc(d.id)}">${memoEvidenceBySong[d.id].n} memo${memoEvidenceBySong[d.id].n===1?'':'s'}</button>`:''}</span><br><span class="rproj">${esc(d.p)} · ${esc(d.st)}${nxtShort?` · ${esc(nxtShort)}`:''}${d.la?` · last touched ${esc(d.la)}`:''}${memoEvidenceBySong[d.id]&&memoEvidenceBySong[d.id].last?` · latest memo ${esc(memoEvidenceBySong[d.id].last)}`:''}</span></span>
  ${bar(d.pot,'pot')}<span class="bw-r">${bar(d.rdy,'rdy')}</span>${bar(d.mom,'mom')}
 </div><div class="detail" hidden>
  <div class="sit-down"><h4>Sit-down</h4>${wk&&wk!=='unknown'?`<span class="pill wk-${esc(wk)}">${esc(wk)}</span>`:''}${nxt?`<div>Next: ${esc(nxt)}</div>`:rawNx?`<div class="memo-next">No safe catalog next step.</div>`:''}${latest?`<div class="sit-memo">Latest memo evidence: ${esc(latest.d||'undated')} · Voice Memo Intake <span>${esc(latest.f)}</span> <button type="button" class="subtle-btn" data-copy-file="${esc(latest.f)}">Copy intake name</button><div class="memo-next">Copy the intake name; write, produce, or listen on your Mac. This page does not open audio.</div></div>`:`<div class="sit-memo memo-next">No searchable memo evidence — write, produce, or listen on your Mac. This page does not open audio.</div>`}</div>
  ${theme?`<h4>Theme</h4>${esc(theme)}`:''}
  ${hook?`<h4>Hook</h4>${esc(hook)}`:''}
  <h4>Status</h4><span class="pill">${esc(d.c)}</span><span class="pill">lyrics: ${esc(d.ly)}</span><span class="pill">audio: ${esc(String(d.au||'').split('—')[0])}</span>${d.key?`<span class="pill">key ${esc(d.key)}</span>`:''}${d.bpm?`<span class="pill">${esc(d.bpm)} bpm</span>`:''}${d.mom?`<span class="pill">momentum ${d.mom}</span>`:''}<span class="pill">writers: ${esc(d.wr)}</span>
  ${d.gate?`<h4>AI-upload gate</h4><span class="pill" style="color:${d.gate.startsWith('YES')?'var(--good)':d.gate.startsWith('NEEDS')?'var(--rdy)':'var(--ink3)'}">${esc(d.gate)}</span>`:''}
  ${d.lp&&d.lp.length?`<h4>Played live</h4>${d.lp.map(x=>`<span class="pill">${esc(x)}</span>`).join('')}`:''}
  ${d.sc&&d.sc.length?`<h4>SoundCloud</h4><ul>${d.sc.map(x=>`<li>${esc(x)}</li>`).join('')}</ul>`:''}
  ${questions?`<h4>Open questions</h4>${esc(questions)}`:''}
  <div class="work-copy"><button type="button" class="subtle-btn" data-copy-work="${esc(d.id)}">Copy work card</button></div>
  ${memoCountBySong[d.id]?`<h4>Matched memo evidence</h4><button type="button" class="memo-link" data-open-memos="${esc(d.id)}">Open ${memoCountBySong[d.id]} searchable memo${memoCountBySong[d.id]===1?'':'s'}</button>`:''}
 </div></div>`;}).join(''):'<div class="empty">No songs match — clear a filter?</div>';
 if(wv&&visibleSongIds.length){
  if(!visibleSongIds.includes(activeWorkSongId))activeWorkSongId=visibleSongIds[0];
  focusWorkSong(activeWorkSongId,false);
 }else if(!wv||!visibleSongIds.length){
  activeWorkSongId='';
 }
 updateWorkSessionState();
}
function focusFoundSong(id){
 const row=[...list.querySelectorAll('[data-song-id]')].find(x=>x.dataset.songId===id);
 const head=row&&row.querySelector('[data-toggle-song]');
 if(!head)return false;
 list.querySelectorAll('[data-toggle-song][aria-expanded="true"]').forEach(open=>{
  if(open!==head)toggleSong(open,false);
 });
 toggleSong(head,true);
 requestAnimationFrame(()=>{head.focus();head.scrollIntoView({block:'center'});});
 return true;
}
function handleSongSearchKey(e){
 if(!e||e.key!=='Enter')return false;
 const term=q&&String(q.value||'').trim();
 if(!term)return false;
 const ids=typeof visibleSongIds!=='undefined'?visibleSongIds:[];
 if(!ids.length)return false;
 if(e.preventDefault)e.preventDefault();
 const id=ids[0];
 if(typeof work!=='undefined'&&work&&work.value&&typeof focusWorkSong==='function')return focusWorkSong(id);
 return focusFoundSong(id);
}
function toggleSong(head,forceOpen){
 const detail=head&&head.nextElementSibling;
 if(!detail||!detail.classList.contains('detail'))return;
 const open=forceOpen===true?true:forceOpen===false?false:detail.hidden;
 detail.hidden=!open;head.setAttribute('aria-expanded',String(open));
}
function parseVaultHash(raw,names){
 const text=String(raw||'').replace(/^#/,'');
 const eq=text.indexOf('=');
 if(eq<0)return null;
 const kind=text.slice(0,eq), id=text.slice(eq+1);
 if(kind==='work'){
  return (id==='write'||id==='produce'||id==='listen'||id==='rest'||id==='inventory'||id==='decide')?{kind:kind,id:id}:null;
 }
 if((kind!=='memos'&&kind!=='song')||!names||!names[id])return null;
 return {kind:kind,id:id};
}
function writeVaultHash(kind,id){
 try{
  if(typeof history==='undefined'||!history.replaceState||typeof location==='undefined')return;
  const next=(kind&&id)?'#'+kind+'='+id:'';
  const dest=next||(location.pathname+location.search);
  if((location.hash||'')!==next)history.replaceState(null,'',dest);
 }catch(err){}
}
function applyVaultHash(){
 const hit=parseVaultHash(typeof location==='undefined'?'':location.hash,sname);
 if(!hit)return;
 if(hit.kind==='memos')openSongMemos(hit.id);
 else if(hit.kind==='work'){
  const saved=readStoredWorkSession(vaultStorage(),sname,DATA);
  applyWorkHash(hit.id,saved);
 }
 else openSong(hit.id);
}
function openWork(kind,songId){
 const k=String(kind||'');
 if(k!=='write'&&k!=='produce'&&k!=='listen'&&k!=='rest'&&k!=='inventory'&&k!=='decide')return;
 if(typeof lastWorkKind!=='undefined')lastWorkKind=k;
 if(typeof activeWorkSongId!=='undefined'){
  activeWorkSongId='';
  const requested=String(songId||'');
  if(requested&&typeof DATA!=='undefined'){
   const candidate=DATA.find(row=>row&&row.id===requested);
   if(candidate&&songWorkKind(candidate.nx)===k)activeWorkSongId=requested;
  }
 }
 q.value='';proj.value='';scored.value='';scope.value='';
 if(typeof sort!=='undefined'&&sort)sort.value='mom';
 if(typeof evidence!=='undefined'&&evidence)evidence.value='';
 if(typeof work!=='undefined'&&work)work.value=k;
 showTab('S');render();
 if(typeof writeVaultHash==='function')writeVaultHash('work',k);
 if(typeof activeWorkSongId!=='undefined'&&activeWorkSongId)focusWorkSong(activeWorkSongId);
 return typeof activeWorkSongId!=='undefined'&&!!activeWorkSongId;
}
function updateWorkSessionState(){
 if(typeof workSession==='undefined'||!workSession)return;
 const kind=typeof work!=='undefined'&&work?String(work.value||''):'';
 const ids=typeof visibleSongIds!=='undefined'?visibleSongIds:[];
 const idx=typeof activeWorkSongId!=='undefined'?ids.indexOf(activeWorkSongId):-1;
 workSession.hidden=!kind;
 if(kind&&workSessionText){
  const label=kind[0].toUpperCase()+kind.slice(1);
  workSessionText.textContent=!ids.length
   ?`${label} · no matching songs`
   :idx>=0
    ?`${label} · ${idx+1} of ${ids.length} · ${sname[ids[idx]]}`
    :`${label} · ${ids.length} song${ids.length===1?'':'s'}`;
 }
 const song=idx>=0&&typeof DATA!=='undefined'?DATA.find(row=>row&&row.id===ids[idx]):null;
 const next=safeWorkNextStep(song);
 const ev=song&&typeof memoEvidenceBySong!=='undefined'?memoEvidenceBySong[song.id]:null;
 if(workSessionNext){
  workSessionNext.hidden=!next;
  workSessionNext.textContent=next?`Do this now: ${next}`:'';
 }
 if(copyWorkNext){
  copyWorkNext.hidden=!next;
  copyWorkNext.disabled=!next;
  copyWorkNext.dataset.songId=next&&song?String(song.id||''):'';
  copyWorkNext.setAttribute('aria-label',next&&song?`Copy next step for ${sname[song.id]||song.id}`:'No safe next step to copy');
 }
 if(workSessionEvidence){
  workSessionEvidence.textContent=!song
   ?'Choose a song to see its verified catalog action.'
   :ev&&ev.n
    ?`${ev.n} searchable memo${ev.n===1?'':'s'}${ev.last?' · latest '+ev.last:''}. Review the evidence before working on your Mac.`
    :next?'No searchable memo evidence for this song. The next step comes from the catalog.':'No safe catalog next step or searchable memo evidence.';
 }
 if(openWorkEvidence){
  openWorkEvidence.hidden=!(song&&ev&&ev.n);
  openWorkEvidence.disabled=!(song&&ev&&ev.n);
  openWorkEvidence.dataset.songId=song&&ev&&ev.n?String(song.id||''):'';
  openWorkEvidence.setAttribute('aria-label',song&&ev&&ev.n?`Review memo evidence for ${sname[song.id]||song.id}`:'No memo evidence to review');
 }
 if(workPrev)workPrev.disabled=idx<=0;
 if(workNext)workNext.disabled=!ids.length||(idx>=0&&idx>=ids.length-1);
}
function focusWorkSong(id,moveFocus){
 const row=[...list.querySelectorAll('[data-song-id]')].find(x=>x.dataset.songId===id);
 const head=row&&row.querySelector('[data-toggle-song]');
 if(!head)return false;
 list.querySelectorAll('[data-toggle-song][aria-expanded="true"]').forEach(open=>{
  if(open!==head)toggleSong(open,false);
 });
 toggleSong(head,true);
 if(typeof activeWorkSongId!=='undefined')activeWorkSongId=String(id||'');
 const kind=typeof work!=='undefined'&&work?String(work.value||''):'';
 if(kind&&typeof rememberWorkSession==='function')rememberWorkSession(kind,activeWorkSongId);
 updateWorkSessionState();
 if(moveFocus!==false)requestAnimationFrame(()=>{head.focus();head.scrollIntoView({block:'center'});});
 return true;
}
function stepWork(delta){
 const ids=typeof visibleSongIds!=='undefined'?visibleSongIds:[];
 if(!ids.length)return false;
 const idx=typeof activeWorkSongId!=='undefined'?ids.indexOf(activeWorkSongId):-1;
 const nextIndex=idx<0?(Number(delta||0)>0?0:ids.length-1):idx+Number(delta||0);
 if(nextIndex<0||nextIndex>=ids.length)return false;
 return focusWorkSong(ids[nextIndex]);
}
function openSong(songId){
 const id=String(songId||'');
 if(!sname[id])return;
 if(typeof activeWorkSongId!=='undefined')activeWorkSongId='';
 q.value=id;proj.value='';scored.value='';scope.value='';sort.value='id';
 if(typeof evidence!=='undefined'&&evidence)evidence.value='';
 if(typeof work!=='undefined'&&work)work.value='';
 showTab('S');render();
 const row=[...list.querySelectorAll('[data-song-id]')].find(x=>x.dataset.songId===id);
 const head=row&&row.querySelector('[data-toggle-song]');
 if(head)toggleSong(head,true);
 requestAnimationFrame(()=>{
  if(head){head.focus();head.scrollIntoView({block:'center'});}
 });
 if(typeof writeVaultHash==='function')writeVaultHash('song',id);
}
function openSongMemos(songId){
 const id=String(songId||'');
 if(!sname[id]||!memoCountBySong[id])return;
 if(typeof lastWorkKind!=='undefined'&&typeof work!=='undefined'&&work&&work.value)lastWorkKind=work.value;
 activeMemoSong=id;mq.value='';showTab('M');mrender();mq.focus();
 if(typeof writeVaultHash==='function')writeVaultHash('memos',id);
}
function handleVaultKey(e){
 if(!e||e.key!=='Escape')return false;
 if(typeof paneM!=='undefined'&&paneM&&!paneM.hidden&&activeMemoSong){
  activeMemoSong='';mq.value='';
  if(typeof lastWorkKind!=='undefined'&&lastWorkKind){
   if(typeof writeVaultHash==='function')writeVaultHash('work',lastWorkKind);
  }else if(typeof writeVaultHash==='function')writeVaultHash('','');
  mrender();mq.focus();
  return true;
 }
 const hasWork=typeof work!=='undefined'&&work&&work.value;
 const hasSearch=!!(q&&String(q.value||'').trim());
 const hasFilters=!!((proj&&proj.value)||(scored&&scored.value)||(scope&&scope.value)||(typeof evidence!=='undefined'&&evidence&&evidence.value)||(sort&&sort.value&&sort.value!=='mom'));
 if(typeof paneS!=='undefined'&&paneS&&!paneS.hidden&&(sname[q.value]||hasWork||hasSearch||hasFilters)){
  q.value='';proj.value='';sort.value='mom';scored.value='';scope.value='';
  if(typeof evidence!=='undefined'&&evidence)evidence.value='';
  if(typeof work!=='undefined'&&work)work.value='';
  if(typeof lastWorkKind!=='undefined')lastWorkKind='';
  if(typeof activeWorkSongId!=='undefined')activeWorkSongId='';
  if(typeof writeVaultHash==='function')writeVaultHash('','');
  render();q.focus();
  return true;
 }
 return false;
}
function copyVaultText(text,btn,idleLabel){
 const value=String(text||'');
 if(!value)return false;
 const done=()=>{
  if(btn){btn.textContent='Copied';btn.classList.add('copied');
   setTimeout(()=>{btn.textContent=idleLabel||'Copy';btn.classList.remove('copied');},1200);}
 };
 const fallback=()=>{
  try{
   const ta=document.createElement('textarea');
   ta.value=value;ta.setAttribute('readonly','');
   ta.style.position='fixed';ta.style.left='-9999px';
   document.body.appendChild(ta);ta.select();
   const ok=document.execCommand('copy');
   document.body.removeChild(ta);
   if(ok)done();
   return ok;
  }catch(err){return false;}
 };
 if(typeof navigator!=='undefined'&&navigator.clipboard&&navigator.clipboard.writeText){
  navigator.clipboard.writeText(value).then(done).catch(()=>{fallback();});
  return true;
 }
 return fallback();
}
function copySongWork(songId,btn){
 const song=DATA.find(d=>d.id===String(songId||''));
 return copyVaultText(buildSongWorkCard(song),btn,'Copy work card');
}
function allowedExactWorkSongId(songId){
 const id=String(songId||'');
 if(!id)return '';
 if(typeof activeWorkSongId!=='undefined'&&String(activeWorkSongId||'')===id)return id;
 const saved=typeof readStoredWorkSession==='function'?readStoredWorkSession(vaultStorage(),typeof sname!=='undefined'?sname:null,typeof DATA!=='undefined'?DATA:null):null;
 return saved&&String(saved.id||'')===id?id:'';
}
function copyExactSongNextStep(songId,btn){
 const id=allowedExactWorkSongId(songId);
 if(!id||typeof DATA==='undefined')return false;
 const song=DATA.find(d=>d&&d.id===id);
 if(!song)return false;
 const kind=(typeof work!=='undefined'&&work&&work.value)?String(work.value||''):'';
 const saved=(!kind&&typeof readStoredWorkSession==='function')?readStoredWorkSession(vaultStorage(),typeof sname!=='undefined'?sname:null,DATA):null;
 const expected=kind||(saved&&saved.kind)||'';
 if(!expected||songWorkKind(song.nx)!==expected)return false;
 return copyVaultText(safeWorkNextStep(song),btn,'Copy next step');
}
function copyCurrentWorkNext(btn){
 const id=btn&&btn.dataset?String(btn.dataset.songId||''):'';
 return copyExactSongNextStep(id,btn);
}
function copyResumeWorkNext(btn){
 const id=btn&&btn.dataset?String(btn.dataset.songId||''):'';
 return copyExactSongNextStep(id,btn);
}
function reviewCurrentWorkEvidence(btn){
 const id=allowedExactWorkSongId(btn&&btn.dataset?btn.dataset.songId:'');
 if(!id||!memoCountBySong[id])return false;
 openSongMemos(id);
 return true;
}
list.addEventListener('click',e=>{
 const copyFile=e.target.closest('[data-copy-file]');
 if(copyFile){copyMemoFile(copyFile.dataset.copyFile,copyFile);return;}
 const copy=e.target.closest('[data-copy-work]');
 if(copy){copySongWork(copy.dataset.copyWork,copy);return;}
 const memos=e.target.closest('[data-open-memos]');
 if(memos){openSongMemos(memos.dataset.openMemos);return;}
 const head=e.target.closest('[data-toggle-song]');if(head)toggleSong(head);
});
list.addEventListener('keydown',e=>{
 if(e.target.closest('[data-open-memos]')||e.target.closest('[data-copy-work]')||e.target.closest('[data-copy-file]'))return;
 const head=e.target.closest('[data-toggle-song]');
 if(head&&(e.key==='Enter'||e.key===' ')){e.preventDefault();toggleSong(head);}
});
if(q)q.addEventListener('keydown',handleSongSearchKey);
[q,proj,sort,scored,scope,evidence,work].forEach(el=>{if(el)el.addEventListener('input',()=>{
 if(el===work){
  if(typeof lastWorkKind!=='undefined')lastWorkKind=work.value||'';
  if(typeof activeWorkSongId!=='undefined')activeWorkSongId='';
 }
 render();
 if(el===work){
  if(work.value)writeVaultHash('work',work.value);
  else writeVaultHash('','');
  if(work.value&&typeof activeWorkSongId!=='undefined'&&activeWorkSongId)focusWorkSong(activeWorkSongId);
 }
});});
clearSongFilters.addEventListener('click',()=>{q.value='';proj.value='';sort.value='mom';scored.value='';scope.value='';if(evidence)evidence.value='';if(work)work.value='';if(typeof lastWorkKind!=='undefined')lastWorkKind='';if(typeof activeWorkSongId!=='undefined')activeWorkSongId='';if(typeof writeVaultHash==='function')writeVaultHash('','');render();q.focus();});
document.querySelector('.lanes').addEventListener('click',e=>{
 const song=e.target.closest('[data-open-song]');
 if(song)openSong(song.dataset.openSong);
});
workStarts.addEventListener('click',e=>{
 const hit=e.target.closest('[data-open-work]');
 if(hit)openWork(hit.dataset.openWork);
});
if(resumeWorkButton)resumeWorkButton.addEventListener('click',resumeLastWorkSession);
if(forgetWorkSession)forgetWorkSession.addEventListener('click',forgetLastWorkSession);
if(workPrev)workPrev.addEventListener('click',()=>stepWork(-1));
if(workNext)workNext.addEventListener('click',()=>stepWork(1));
if(copyWorkNext)copyWorkNext.addEventListener('click',()=>copyCurrentWorkNext(copyWorkNext));
if(copyResumeNext)copyResumeNext.addEventListener('click',()=>copyResumeWorkNext(copyResumeNext));
if(openWorkEvidence)openWorkEvidence.addEventListener('click',()=>reviewCurrentWorkEvidence(openWorkEvidence));
tabS.addEventListener('click',()=>{
 showTab('S');
 if(typeof lastWorkKind!=='undefined'&&lastWorkKind&&work&&!work.value&&!q.value)openWork(lastWorkKind);
});
tabM.addEventListener('click',()=>{showTab('M');mrender();});
render();
updateResumeWork();
// ---- memo transcript search ----
function memoMatches(m,term,songId){
 if(songId&&m.s!==songId)return false;
 if(!term)return !!songId;
 return String(m.x||'').toLowerCase().includes(term)||String(m.n||'').toLowerCase().includes(term)||String(sname[m.s]||'').toLowerCase().includes(term);
}
function markHay(text,term){
 const src=String(text||'');
 if(!term)return esc(src);
 const i=src.toLowerCase().indexOf(term);
 if(i<0)return esc(src);
 return esc(src.slice(0,i))+'<mark>'+esc(src.slice(i,i+term.length))+'</mark>'+esc(src.slice(i+term.length));
}
function sortMemoHits(hits){
 const dated=[], empty=[];
 (hits||[]).forEach(hit=>{
  const row=hit&&(hit.m||hit);
  if(row&&String(row.d||'').trim())dated.push(hit); else empty.push(hit);
 });
 const byDateThenFile=(a,b)=>{
  const am=a.m||a, bm=b.m||b;
  const dd=String(bm.d||'').localeCompare(String(am.d||''));
  return dd||String(bm.f||'').localeCompare(String(am.f||''));
 };
 dated.sort(byDateThenFile);
 empty.sort((a,b)=>String((b.m||b).f||'').localeCompare(String((a.m||a).f||'')));
 return dated.concat(empty);
}
function copyMemoFile(name,btn){
 return copyVaultText(name,btn,'Copy intake name');
}
function mrender(){
 const term=mq.value.toLowerCase().trim();
 if(activeMemoSong&&!sname[activeMemoSong])activeMemoSong='';
 const ev=memoEvidenceBySong[activeMemoSong];
 memoScope.hidden=!activeMemoSong;
 const span=ev&&ev.first&&ev.last?(ev.first===ev.last?` · ${ev.first}`:` · ${ev.first} → ${ev.last}`):'';
 memoScopeText.textContent=activeMemoSong?`${ev?ev.n:0} searchable memo${ev&&ev.n===1?'':'s'} for ${sname[activeMemoSong]}${span}`:'';
 const song=activeMemoSong&&DATA.find(d=>d.id===activeMemoSong);
 if(memoScopeNext){
  const nxt=song?safeWorkNextStep(song):'';
  memoScopeNext.hidden=!nxt;
  memoScopeNext.textContent=nxt?`Next action: ${nxt}`:'';
 }
 if(memoScopeHook){
  const hook=song?stripPrivateLocators(flattenWorkField(song.hk)):'';
  memoScopeHook.hidden=!hook;
  memoScopeHook.textContent=hook?`Hook: ${hook}`:'';
 }
 if(copyMemoWork){
  copyMemoWork.hidden=!song;
  copyMemoWork.dataset.copyWork=song?song.id:'';
 }
 if((!activeMemoSong&&term.length<3)||(term.length>0&&term.length<3)){
  mlist.innerHTML=`<div class="mhint">${activeMemoSong?'Leave search empty to see every matched memo, newest first, or type':'Type'} 3+ letters to search. Source truth: ${TX_TOTAL} transcribed and ${TX_MATCHED_TOTAL} matched; ${TX_SEARCHABLE_MATCHED} matched rows are searchable. Hits are leads, not gospel — Whisper mishears sung words. Copy the intake name; do not open audio from this page.</div>`;return;
 }
 const hits=[];
 for(const m of TX){
  if(!memoMatches(m,term,activeMemoSong))continue;
  const lx=m.x.toLowerCase(); const i=term?lx.indexOf(term):-1;
  let snip='';
  if(term&&i>=0){const a=Math.max(0,i-80),b=Math.min(m.x.length,i+term.length+120);
   snip=(a>0?'…':'')+esc(m.x.slice(a,i))+'<mark>'+esc(m.x.slice(i,i+term.length))+'</mark>'+esc(m.x.slice(i+term.length,b))+(b<m.x.length?'…':'');}
  else snip=esc(m.x.slice(0,160))+(m.x.length>160?'…':'');
  hits.push({m,snip});
 }
 const ordered=sortMemoHits(hits);
 const visible=ordered.slice(0,80);
 const summary=ordered.length?`<div class="resultbar"><span>Showing ${visible.length}${ordered.length>visible.length?` of ${ordered.length}`:''} matching memo${ordered.length===1?'':'s'} · newest first</span></div>`:'';
 mlist.innerHTML=ordered.length?summary+visible.map(({m,snip})=>`
  <div class="mrow"><div class="mmeta">${esc(m.d)} · ${Math.round((Number(m.u)||0)/60)}min${m.s&&sname[m.s]?` · matched to <button type="button" class="song-link" data-open-song="${esc(m.s)}">${esc(sname[m.s])}</button>`:' · unmatched'}</div>
  <b>${markHay(m.n,term)}</b><div class="msnip">${snip}</div>
  <div class="mmeta" style="margin-top:4px">file: ${esc(m.f)} (Voice Memo Intake) <button type="button" class="subtle-btn" data-copy-file="${esc(m.f)}">Copy intake name</button></div></div>`).join('')
  :'<div class="empty">No matched memo evidence found — clear the song filter or try a different word.</div>';
}
mq.addEventListener('input',mrender);
mlist.addEventListener('click',e=>{
 const copy=e.target.closest('[data-copy-file]');
 if(copy){copyMemoFile(copy.dataset.copyFile,copy);return;}
 const workCard=e.target.closest('[data-copy-work]');
 if(workCard){copySongWork(workCard.dataset.copyWork,workCard);return;}
 const song=e.target.closest('[data-open-song]');
 if(song)openSong(song.dataset.openSong);
});
if(copyMemoWork)copyMemoWork.addEventListener('click',e=>{
 copySongWork(copyMemoWork.dataset.copyWork,copyMemoWork);
 e.preventDefault();
});
clearMemoScope.addEventListener('click',()=>{activeMemoSong='';mq.value='';if(typeof writeVaultHash==='function')writeVaultHash('','');mrender();mq.focus();});
if(typeof document!=='undefined')document.addEventListener('keydown',handleVaultKey);
if(typeof window!=='undefined'){window.addEventListener('hashchange',applyVaultHash);applyVaultHash();}
</script></body></html>'''

page = (page.replace('__DATA__', DATA)
    .replace('__TX__', TX)
    .replace('__TX_TOTAL__', str(TX_TOTAL))
    .replace('__TX_MATCHED_TOTAL__', str(TX_MATCHED_TOTAL))
    .replace('__TX_SEARCHABLE_TOTAL__', str(TX_SEARCHABLE_TOTAL))
    .replace('__TX_SEARCHABLE_MATCHED__', str(TX_SEARCHABLE_MATCHED)))
open(OUT_PATH,'w').write(page)
print('dashboard written,', OUT_PATH, len(page)//1024, 'KB,',
      TX_SEARCHABLE_TOTAL, 'searchable transcripts from', TX_TOTAL, 'transcribed')
