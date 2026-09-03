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
    slim.append(dict(id=s['song_id'], t=s['canonical_title'], p=s['artist_project'],
        c=s['classification'], st=surface_stage_label(s.get('stage','')), key=s.get('key',''), bpm=s.get('bpm',''),
        pot=s.get('potential'), rdy=s.get('readiness'), mom=s.get('momentum'),
        la=s.get('last_activity',''), conf=s.get('confidence',''),
        th=s.get('theme',''), hk=s.get('hook',''), nx=s.get('next_action',''),
        ly=s.get('lyric_status',''), au=s.get('audio_status',''),
        src=s.get('sources',[]), sc=s.get('soundcloud',[]), oq=s.get('open_questions',''),
        wr=', '.join(s.get('writers',[])),
        live=played_badge_label(s.get('live_latest','')), lp=[f"{e['band']} ({e['date']})" for e in s.get('live_presence',[])],
        gate=s.get('ai_upload_ok',''), bs=s.get('best_source_resolved','')))
overlay_feed_scopes(slim, app_api)
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
.stats{display:flex;gap:10px;flex-wrap:wrap;margin-bottom:16px}
.stat{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:10px 14px;min-width:100px}
.stat b{font-size:20px;display:block} .stat span{color:var(--ink3);font-size:11px;text-transform:uppercase;letter-spacing:.5px}
.lanes{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:14px 16px;margin-bottom:16px}
.lanes h2{font-size:13px;text-transform:uppercase;letter-spacing:.6px;color:var(--ink2);margin-bottom:8px}
.lane{display:flex;gap:8px;align-items:baseline;padding:4px 0;border-bottom:1px dashed var(--line)}
.lane:last-child{border:none}
.tag{font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.5px;padding:2px 8px;border-radius:99px;background:var(--card2);color:var(--ink2);white-space:nowrap}
.tag.f{color:var(--pot)} .tag.q{color:var(--good)} .tag.x{color:var(--rdy)}
.tabs{display:flex;gap:6px;margin-bottom:12px}
.tab{padding:8px 16px;border-radius:99px;border:1px solid var(--line);background:var(--card);color:var(--ink2);cursor:pointer;font-size:13px;font-weight:600}
.tab.on{background:var(--card2);color:var(--ink);border-color:var(--ink3)}
.controls{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:12px;position:sticky;top:0;background:var(--bg);padding:8px 0;z-index:5}
input,select,.subtle-btn,.memo-link,.song-link{background:var(--card);color:var(--ink);border:1px solid var(--line);border-radius:8px;padding:8px 10px;font-size:13px}
input{flex:1;min-width:160px}
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
.msnip{color:var(--ink2);font-size:12.5px} .msnip mark{background:var(--pot);color:#fff;border-radius:3px;padding:0 2px}
.mhint{color:var(--ink3);font-size:12px;padding:16px;text-align:center}
.resultbar,.memo-scope{display:flex;align-items:center;justify-content:space-between;gap:10px;color:var(--ink3);font-size:12px;margin:0 0 10px}
.memo-scope{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:9px 12px;color:var(--ink2)}
.subtle-btn,.memo-link,.song-link{cursor:pointer;font-weight:600}
.subtle-btn:disabled{opacity:.45;cursor:default}.memo-link,.song-link{padding:4px 8px;color:var(--pot)}
.song-link{border:0;background:transparent;padding:0;font-size:inherit;text-decoration:underline;text-underline-offset:2px}
.memo-next{color:var(--ink3);font-size:12px;margin-top:3px}
.copied{color:var(--good)}
</style></head><body>
<h1>🎸 Jeff Story Song Vault</h1>
<div class="sub">Every song, one place · Catalog v1.6 · ''' + SURFACE_SUBTITLE + r''' · Momentum Index · __TX_TOTAL__ memos transcribed · __TX_SEARCHABLE_TOTAL__ usable-text transcripts searchable · no audio in this repo</div>
<div class="stats" id="stats"></div>
<div class="lanes">
 <h2>The three lanes (+ on deck)</h2>
 <div class="lane"><span class="tag f">Flagship</span><b>Turn Over The Flag</b><span style="color:var(--ink3)">— mix 1.6, two overdubs left</span></div>
 <div class="lane"><span class="tag q">Quick win</span><b>Manic</b><span style="color:var(--ink3)">— ONE overdub (lead guitar: choruses + solos)</span></div>
 <div class="lane"><span class="tag x">Experimental</span><b>Long Long Drive</b><span style="color:var(--ink3)">— Suno arrangement test queued</span></div>
 <div class="lane"><span class="tag">On deck</span><b>It's Alright</b><span style="color:var(--ink3)">— ''' + ON_DECK_NOTE + r'''; lyric 85% recovered; takes Manic's slot next</span></div>
 <div class="lane"><span class="tag">The Opus</span><b>Blue Skies Fade</b><span style="color:var(--ink3)">— Kimberly's suite; its own protected lane</span></div>
</div>
<div class="tabs" role="tablist" aria-label="Vault views">
 <button type="button" class="tab on" id="tabS" role="tab" aria-controls="paneS" aria-selected="true">Songs</button>
 <button type="button" class="tab" id="tabM" role="tab" aria-controls="paneM" aria-selected="false">Memo Search (__TX_SEARCHABLE_TOTAL__ searchable)</button>
</div>
<div id="paneS" role="tabpanel" aria-labelledby="tabS">
<div class="controls">
 <input id="q" placeholder="Search songs, themes, hooks… (try: garden, Kimberly, ska)">
 <select id="proj"><option value="">All projects</option></select>
 <select id="sort">
  <option value="mom">Sort: Momentum (what's alive)</option>
  <option value="pot">Sort: Potential</option><option value="rdy">Sort: Readiness</option>
  <option value="id">Sort: Catalog ID</option><option value="t">Sort: Title</option>
  <option value="memo">Sort: Latest memo evidence</option></select>
 <select id="scored"><option value="">All songs</option><option value="1">Scored only</option><option value="0">Unscored / to explore</option></select>
 <select id="scope"><option value="">All StoryBoard scopes</option></select>
 <select id="evidence"><option value="">Any memo evidence</option><option value="1">Has searchable memos</option><option value="0">No searchable memos</option></select>
</div>
<div class="resultbar"><span id="songResults" aria-live="polite"></span><button type="button" class="subtle-btn" id="clearSongFilters">Clear filters</button></div>
<div class="legend"><span><span class="dot" style="background:var(--pot)"></span>Potential /100</span>
<span><span class="dot" style="background:var(--rdy)"></span>Readiness /100</span>
<span><span class="dot" style="background:var(--mom)"></span>Momentum /100 (how alive it is in your hands)</span></div>
<div id="list"></div>
<div class="covers-note">93 covers cataloged separately, never ranked against originals. Catalog rows are not the official set. Show Night owns official sets. Spine: data/master_catalog.json · StoryBoard feed: data/app_api.json · validate: python3 scripts/validate_catalog.py</div>
</div>
<div id="paneM" role="tabpanel" aria-labelledby="tabM" hidden>
<div class="controls"><input id="mq" placeholder="Search __TX_SEARCHABLE_TOTAL__ usable transcript snippets… (try: alright, garden, better than now)"></div>
<div class="memo-scope" id="memoScope" hidden><div><span id="memoScopeText"></span><div class="memo-next" id="memoScopeNext" hidden></div></div><button type="button" class="subtle-btn" id="clearMemoScope">Show all memos</button></div>
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
const q=document.getElementById('q'),proj=document.getElementById('proj'),
 sort=document.getElementById('sort'),scored=document.getElementById('scored'),
 scope=document.getElementById('scope'),evidence=document.getElementById('evidence'),
 list=document.getElementById('list'),
 songResults=document.getElementById('songResults'),clearSongFilters=document.getElementById('clearSongFilters'),
 tabS=document.getElementById('tabS'),tabM=document.getElementById('tabM'),
 paneS=document.getElementById('paneS'),paneM=document.getElementById('paneM'),
 mq=document.getElementById('mq'),mlist=document.getElementById('mlist'),
 memoScope=document.getElementById('memoScope'),memoScopeText=document.getElementById('memoScopeText'),
 memoScopeNext=document.getElementById('memoScopeNext'),
 clearMemoScope=document.getElementById('clearMemoScope');
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
document.getElementById('stats').innerHTML=
 `<div class="stat"><b>${DATA.length}</b><span>songs cataloged</span></div>`+
 `<div class="stat"><b>${scoredCount}</b><span>scored</span></div>`+
 `<div class="stat"><b>${defaultLiveCount}</b><span>default-live catalog</span></div>`+
 `<div class="stat"><b>9</b><span>songs recovered from memos</span></div>`+
 `<div class="stat"><b>${TX_MATCHED_TOTAL}</b><span>memos matched</span></div>`+
 `<div class="stat"><b>${TX_SEARCHABLE_TOTAL}</b><span>memos searchable</span></div>`+
 `<div class="stat"><b>${TX_TOTAL}</b><span>memos transcribed</span></div>`;
function esc(s){return (s===null||s===undefined?'':String(s)).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&#39;');}
function bar(v,c){
 const n=Number(v);
 if(!Number.isFinite(n)||n<=0)return '<div class="barwrap"><span style="color:var(--ink3)">—</span></div>';
 const safe=Math.min(100,Math.max(0,n));
 return `<div class="barwrap"><div class="bar"><i style="width:${safe}%;background:var(--${c})"></i></div><span>${esc(n)}</span></div>`;
}
function render(){
 const term=q.value.toLowerCase().trim(), pv=proj.value, sv=scored.value, scv=scope.value,
  evv=(typeof evidence!=='undefined'&&evidence)?evidence.value:'';
 let rows=DATA.filter(d=>{
  if(pv&&d.p!==pv)return false;
  if(scv&&d.scope!==scv)return false;
  if(sv==='1'&&!d.pot)return false; if(sv==='0'&&d.pot)return false;
  if(evv==='1'&&!memoEvidenceBySong[d.id])return false;
  if(evv==='0'&&memoEvidenceBySong[d.id])return false;
  if(!term)return true;
  return (d.t+' '+d.id+' '+d.th+' '+d.hk+' '+d.c+' '+d.st+' '+(d.wr||'')+' '+(d.nx||'')+' '+(d.oq||'')+' '+(d.gate||'')+' '+(d.scope_label||'')+' '+(d.src||[]).join(' ')).toLowerCase().includes(term);});
 const k=sort.value;
 if(k==='memo'){
  rows.sort((a,b)=>{
   const ea=memoEvidenceBySong[a.id]||{n:0,last:''};
   const eb=memoEvidenceBySong[b.id]||{n:0,last:''};
   const da=String(ea.last||''), db=String(eb.last||'');
   if(!da&&!db)return (eb.n-ea.n)||a.id.localeCompare(b.id);
   if(!da)return 1;
   if(!db)return -1;
   return db.localeCompare(da) || (eb.n-ea.n) || a.id.localeCompare(b.id);
  });
 }else{
  rows.sort((a,b)=> k==='t'?a.t.localeCompare(b.t): k==='id'?a.id.localeCompare(b.id):((b[k]||0)-(a[k]||0)) || a.id.localeCompare(b.id));
 }
 songResults.textContent=`Showing ${rows.length} of ${DATA.length} songs`;
 clearSongFilters.disabled=!(term||pv||sv||scv||evv||k!=='mom');
 list.innerHTML=rows.length?rows.map((d,i)=>`
 <div class="row" data-song-id="${esc(d.id)}"><div class="rhead" role="button" tabindex="0" aria-expanded="false" data-toggle-song>
  <span class="rid">${esc(d.id)}</span>
  <span><span class="rtitle">${esc(d.t)}${d.live?` <span class="pill">${esc(d.live)}</span>`:''}${d.scope_label?` <span class="pill">${esc(d.scope_label)}</span>`:''}${memoEvidenceBySong[d.id]?` <button type="button" class="pill memo-link" data-open-memos="${esc(d.id)}">${memoEvidenceBySong[d.id].n} memo${memoEvidenceBySong[d.id].n===1?'':'s'}</button>`:''}</span><br><span class="rproj">${esc(d.p)} · ${esc(d.st)}${d.la?` · last touched ${esc(d.la)}`:''}${memoEvidenceBySong[d.id]&&memoEvidenceBySong[d.id].last?` · latest memo ${esc(memoEvidenceBySong[d.id].last)}`:''}</span></span>
  ${bar(d.pot,'pot')}<span class="bw-r">${bar(d.rdy,'rdy')}</span>${bar(d.mom,'mom')}
 </div><div class="detail" hidden>
  ${d.th?`<h4>Theme</h4>${esc(d.th)}`:''}
  ${d.hk?`<h4>Hook</h4>${esc(d.hk)}`:''}
  ${d.nx?`<h4>Next action</h4>${esc(d.nx)}`:''}
  <h4>Status</h4><span class="pill">${esc(d.c)}</span><span class="pill">lyrics: ${esc(d.ly)}</span><span class="pill">audio: ${esc(d.au).split('—')[0]}</span>${d.key?`<span class="pill">key ${esc(d.key)}</span>`:''}${d.bpm?`<span class="pill">${esc(d.bpm)} bpm</span>`:''}${d.mom?`<span class="pill">momentum ${d.mom}</span>`:''}<span class="pill">writers: ${esc(d.wr)}</span>
  ${d.gate?`<h4>AI-upload gate</h4><span class="pill" style="color:${d.gate.startsWith('YES')?'var(--good)':d.gate.startsWith('NEEDS')?'var(--rdy)':'var(--ink3)'}">${esc(d.gate)}</span>`:''}
  ${d.bs?`<h4>Latest source (auto-resolved)</h4>${esc(d.bs)}`:''}
  ${d.lp&&d.lp.length?`<h4>Played live</h4>${d.lp.map(x=>`<span class="pill">${esc(x)}</span>`).join('')}`:''}
  ${d.src&&d.src.length?`<h4>Known assets</h4><ul>${d.src.map(x=>`<li>${esc(x)}</li>`).join('')}</ul>`:''}
  ${d.sc&&d.sc.length?`<h4>SoundCloud</h4><ul>${d.sc.map(x=>`<li>${esc(x)}</li>`).join('')}</ul>`:''}
  ${d.oq?`<h4>Open questions</h4>${esc(d.oq)}`:''}
  ${memoCountBySong[d.id]?`<h4>Matched memo evidence</h4><button type="button" class="memo-link" data-open-memos="${esc(d.id)}">Open ${memoCountBySong[d.id]} searchable memo${memoCountBySong[d.id]===1?'':'s'}</button>`:''}
 </div></div>`).join(''):'<div class="empty">No songs match — clear a filter?</div>';
}
function toggleSong(head,forceOpen){
 const detail=head&&head.nextElementSibling;
 if(!detail||!detail.classList.contains('detail'))return;
 const open=forceOpen===true?true:detail.hidden;
 detail.hidden=!open;head.setAttribute('aria-expanded',String(open));
}
function parseVaultHash(raw,names){
 const text=String(raw||'').replace(/^#/,'');
 const eq=text.indexOf('=');
 if(eq<0)return null;
 const kind=text.slice(0,eq), id=text.slice(eq+1);
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
 else openSong(hit.id);
}
function openSong(songId){
 const id=String(songId||'');
 if(!sname[id])return;
 q.value=id;proj.value='';scored.value='';scope.value='';sort.value='id';
 if(typeof evidence!=='undefined'&&evidence)evidence.value='';
 showTab('S');render();
 requestAnimationFrame(()=>{
  const row=[...list.querySelectorAll('[data-song-id]')].find(x=>x.dataset.songId===id);
  const head=row&&row.querySelector('[data-toggle-song]');
  if(head){toggleSong(head,true);head.focus();head.scrollIntoView({block:'center'});}
 });
 if(typeof writeVaultHash==='function')writeVaultHash('song',id);
}
function openSongMemos(songId){
 const id=String(songId||'');
 if(!sname[id]||!memoCountBySong[id])return;
 activeMemoSong=id;mq.value='';showTab('M');mrender();mq.focus();
 if(typeof writeVaultHash==='function')writeVaultHash('memos',id);
}
function handleVaultKey(e){
 if(!e||e.key!=='Escape')return false;
 if(typeof paneM!=='undefined'&&paneM&&!paneM.hidden&&activeMemoSong){
  activeMemoSong='';mq.value='';
  if(typeof writeVaultHash==='function')writeVaultHash('','');
  mrender();mq.focus();
  return true;
 }
 if(typeof paneS!=='undefined'&&paneS&&!paneS.hidden&&sname[q.value]){
  q.value='';proj.value='';sort.value='mom';scored.value='';scope.value='';
  if(typeof evidence!=='undefined'&&evidence)evidence.value='';
  if(typeof writeVaultHash==='function')writeVaultHash('','');
  render();q.focus();
  return true;
 }
 return false;
}
list.addEventListener('click',e=>{
 const memos=e.target.closest('[data-open-memos]');
 if(memos){openSongMemos(memos.dataset.openMemos);return;}
 const head=e.target.closest('[data-toggle-song]');if(head)toggleSong(head);
});
list.addEventListener('keydown',e=>{
 if(e.target.closest('[data-open-memos]'))return;
 const head=e.target.closest('[data-toggle-song]');
 if(head&&(e.key==='Enter'||e.key===' ')){e.preventDefault();toggleSong(head);}
});
[q,proj,sort,scored,scope,evidence].forEach(el=>{if(el)el.addEventListener('input',render);});
clearSongFilters.addEventListener('click',()=>{q.value='';proj.value='';sort.value='mom';scored.value='';scope.value='';if(evidence)evidence.value='';if(typeof writeVaultHash==='function')writeVaultHash('','');render();q.focus();});
tabS.addEventListener('click',()=>showTab('S'));tabM.addEventListener('click',()=>showTab('M'));
render();
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
 const text=String(name||'');
 if(!text)return false;
 const done=()=>{
  if(btn){btn.textContent='Copied';btn.classList.add('copied');
   setTimeout(()=>{btn.textContent='Copy intake name';btn.classList.remove('copied');},1200);}
 };
 if(typeof navigator!=='undefined'&&navigator.clipboard&&navigator.clipboard.writeText){
  navigator.clipboard.writeText(text).then(done).catch(()=>{});
  return true;
 }
 return false;
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
  memoScopeNext.hidden=!(song&&song.nx);
  memoScopeNext.textContent=(song&&song.nx)?`Next action: ${song.nx}`:'';
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
 const song=e.target.closest('[data-open-song]');
 if(song)openSong(song.dataset.openSong);
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
