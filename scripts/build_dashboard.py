#!/usr/bin/env python3
"""Dashboard v2 — catalog v1.5 + Momentum Index + searchable memo transcripts."""
import json, re

cat = json.load(open('/home/claude/vault/00_control_room/master_catalog.json'))
slim = []
for s in cat['songs']:
    slim.append(dict(id=s['song_id'], t=s['canonical_title'], p=s['artist_project'],
        c=s['classification'], st=s.get('stage',''), key=s.get('key',''), bpm=s.get('bpm',''),
        pot=s.get('potential'), rdy=s.get('readiness'), mom=s.get('momentum'),
        la=s.get('last_activity',''), conf=s.get('confidence',''),
        th=s.get('theme',''), hk=s.get('hook',''), nx=s.get('next_action',''),
        ly=s.get('lyric_status',''), au=s.get('audio_status',''),
        src=s.get('sources',[]), sc=s.get('soundcloud',[]), oq=s.get('open_questions',''),
        wr=', '.join(s.get('writers',[])),
        live=s.get('live_latest',''), lp=[f"{e['band']} ({e['date']})" for e in s.get('live_presence',[])],
        gate=s.get('ai_upload_ok',''), bs=s.get('best_source_resolved','')))
DATA = json.dumps(slim, ensure_ascii=False).replace('</', '<\\/')

# transcripts: compact index (title, date, dur, cleaned text capped at 1500 chars)
joined = json.load(open('/home/claude/vault/vm_transcribed.json'))
def collapse(t):
    words = t.split(); out=[]
    for w in words:
        if len(out)>=2 and out[-1].lower()==w.lower() and out[-2].lower()==w.lower(): continue
        out.append(w)
    return ' '.join(out)
tx = []
for j in joined:
    txt = collapse(j['text'])[:1500]
    if len(txt) < 15: continue
    tx.append(dict(f=j['file'], n=j['title'] or '(untitled)', d=j['date'], u=j['dur'],
                   s=j.get('song_id') or '', x=txt))
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
input,select{background:var(--card);color:var(--ink);border:1px solid var(--line);border-radius:8px;padding:8px 10px;font-size:13px}
input{flex:1;min-width:160px}
.row{background:var(--card);border:1px solid var(--line);border-radius:10px;margin-bottom:6px;overflow:hidden}
.rhead{display:grid;grid-template-columns:64px 1fr 110px 110px 110px;gap:8px;align-items:center;padding:10px 12px;cursor:pointer}
.rhead:hover{background:var(--card2)}
@media(max-width:640px){.rhead{grid-template-columns:1fr 90px 90px}.rid,.bw-r{display:none}}
.rid{color:var(--ink3);font-size:11px;font-family:ui-monospace,Menlo,monospace}
.rtitle{font-weight:600} .rproj{color:var(--ink3);font-size:11px}
.barwrap{display:flex;align-items:center;gap:6px;font-size:11px;color:var(--ink2)}
.bar{height:6px;border-radius:4px;background:var(--card2);flex:1;overflow:hidden}
.bar i{display:block;height:100%;border-radius:4px}
.detail{display:none;padding:4px 14px 14px;border-top:1px solid var(--line);color:var(--ink2);font-size:13px}
.detail.open{display:block}
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
</style></head><body>
<h1>🎸 Jeff Story Song Vault</h1>
<div class="sub">Every song, one place · Catalog v1.5 · 2026-08-20 · now with the Momentum Index + all 916 memos searchable by what you actually sang</div>
<div class="stats" id="stats"></div>
<div class="lanes">
 <h2>The three lanes (+ on deck)</h2>
 <div class="lane"><span class="tag f">Flagship</span><b>Turn Over The Flag</b><span style="color:var(--ink3)">— mix 1.6, two overdubs left</span></div>
 <div class="lane"><span class="tag q">Quick win</span><b>Manic</b><span style="color:var(--ink3)">— ONE overdub (lead guitar: choruses + solos)</span></div>
 <div class="lane"><span class="tag x">Experimental</span><b>Long Long Drive</b><span style="color:var(--ink3)">— Suno arrangement test queued</span></div>
 <div class="lane"><span class="tag">On deck</span><b>It's Alright</b><span style="color:var(--ink3)">— in the live set, lyric 85% recovered; takes Manic's slot next</span></div>
 <div class="lane"><span class="tag">The Opus</span><b>Blue Skies Fade</b><span style="color:var(--ink3)">— Kimberly's suite; its own protected lane</span></div>
</div>
<div class="tabs">
 <div class="tab on" id="tabS" onclick="showTab('S')">Songs</div>
 <div class="tab" id="tabM" onclick="showTab('M')">Memo Search (916 transcripts)</div>
</div>
<div id="paneS">
<div class="controls">
 <input id="q" placeholder="Search songs, themes, hooks… (try: garden, Kimberly, ska)">
 <select id="proj"><option value="">All projects</option></select>
 <select id="sort">
  <option value="mom">Sort: Momentum (what's alive)</option>
  <option value="pot">Sort: Potential</option><option value="rdy">Sort: Readiness</option>
  <option value="id">Sort: Catalog ID</option><option value="t">Sort: Title</option></select>
 <select id="scored"><option value="">All songs</option><option value="1">Scored only</option><option value="0">Unscored / to explore</option></select>
</div>
<div class="legend"><span><span class="dot" style="background:var(--pot)"></span>Potential /100</span>
<span><span class="dot" style="background:var(--rdy)"></span>Readiness /100</span>
<span><span class="dot" style="background:var(--mom)"></span>Momentum /100 (how alive it is in your hands)</span></div>
<div id="list"></div>
<div class="covers-note">93 covers cataloged separately, never ranked against originals. Full data: “00 Control Room” on your Mac + the claude.ai project.</div>
</div>
<div id="paneM" style="display:none">
<div class="controls"><input id="mq" placeholder="Search everything you ever sang into your phone… (try: alright, garden, better than now)"></div>
<div id="mlist"><div class="mhint">Type 3+ letters to search all 916 memo transcripts. Transcripts are machine-made (Whisper, run locally on your Mac) — they mishear sung words constantly, so treat hits as leads, not gospel.</div></div>
</div>
<div class="foot">Originals never moved or renamed — this is an index on top. Ask Claude in the “2026 Song Organization” project to update or dig deeper.</div>
<script>
const DATA = __DATA__;
const TX = __TX__;
function showTab(w){document.getElementById('paneS').style.display=w==='S'?'':'none';
 document.getElementById('paneM').style.display=w==='M'?'':'none';
 document.getElementById('tabS').classList.toggle('on',w==='S');
 document.getElementById('tabM').classList.toggle('on',w==='M');}
const q=document.getElementById('q'),proj=document.getElementById('proj'),
 sort=document.getElementById('sort'),scored=document.getElementById('scored'),list=document.getElementById('list');
const projects=[...new Set(DATA.map(d=>d.p))].sort();
projects.forEach(p=>{const o=document.createElement('option');o.value=p;o.textContent=p;proj.appendChild(o);});
const scoredCount=DATA.filter(d=>d.pot).length;
document.getElementById('stats').innerHTML=
 `<div class="stat"><b>${DATA.length}</b><span>songs cataloged</span></div>`+
 `<div class="stat"><b>${scoredCount}</b><span>scored</span></div>`+
 `<div class="stat"><b>9</b><span>songs recovered from memos</span></div>`+
 `<div class="stat"><b>372</b><span>memos matched</span></div>`+
 `<div class="stat"><b>916</b><span>memos transcribed</span></div>`;
function esc(s){return (''+(s||'')).replace(/&/g,'&amp;').replace(/</g,'&lt;');}
function bar(v,c){return v?`<div class="barwrap"><div class="bar"><i style="width:${v}%;background:var(--${c})"></i></div><span>${v}</span></div>`:'<div class="barwrap"><span style="color:var(--ink3)">—</span></div>';}
function render(){
 const term=q.value.toLowerCase(), pv=proj.value, sv=scored.value;
 let rows=DATA.filter(d=>{
  if(pv&&d.p!==pv)return false;
  if(sv==='1'&&!d.pot)return false; if(sv==='0'&&d.pot)return false;
  if(!term)return true;
  return (d.t+' '+d.id+' '+d.th+' '+d.hk+' '+d.c+' '+d.st+' '+(d.src||[]).join(' ')).toLowerCase().includes(term);});
 const k=sort.value;
 rows.sort((a,b)=> k==='t'?a.t.localeCompare(b.t): k==='id'?a.id.localeCompare(b.id):((b[k]||0)-(a[k]||0)) || a.id.localeCompare(b.id));
 list.innerHTML=rows.length?rows.map((d,i)=>`
 <div class="row"><div class="rhead" onclick="this.nextElementSibling.classList.toggle('open')">
  <span class="rid">${d.id}</span>
  <span><span class="rtitle">${esc(d.t)}${d.live?` <span class="pill" style="color:var(--good);font-weight:700">LIVE ${esc(d.live)}</span>`:''}</span><br><span class="rproj">${esc(d.p)} · ${esc(d.st)}${d.la?` · last touched ${esc(d.la)}`:''}</span></span>
  ${bar(d.pot,'pot')}<span class="bw-r">${bar(d.rdy,'rdy')}</span>${bar(d.mom,'mom')}
 </div><div class="detail">
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
 </div></div>`).join(''):'<div class="empty">No songs match — clear a filter?</div>';
}
[q,proj,sort,scored].forEach(el=>el.addEventListener('input',render));
render();
// ---- memo transcript search ----
const mq=document.getElementById('mq'), mlist=document.getElementById('mlist');
const sname={}; DATA.forEach(d=>sname[d.id]=d.t);
function mrender(){
 const term=mq.value.toLowerCase().trim();
 if(term.length<3){mlist.innerHTML='<div class="mhint">Type 3+ letters to search all 916 memo transcripts. Hits are leads, not gospel — Whisper mishears sung words.</div>';return;}
 const hits=[];
 for(const m of TX){
  const lx=m.x.toLowerCase(); const i=lx.indexOf(term);
  if(i<0 && !m.n.toLowerCase().includes(term)) continue;
  let snip='';
  if(i>=0){const a=Math.max(0,i-80),b=Math.min(m.x.length,i+term.length+120);
   snip=(a>0?'…':'')+esc(m.x.slice(a,i))+'<mark>'+esc(m.x.slice(i,i+term.length))+'</mark>'+esc(m.x.slice(i+term.length,b))+(b<m.x.length?'…':'');}
  else snip=esc(m.x.slice(0,160))+'…';
  hits.push({m,snip});
  if(hits.length>=80)break;
 }
 mlist.innerHTML=hits.length?hits.map(({m,snip})=>`
  <div class="mrow"><div class="mmeta">${esc(m.d)} · ${Math.round(m.u/60)}min${m.s?` · matched to <b>${esc(sname[m.s]||m.s)}</b>`:' · unmatched'}</div>
  <b>${esc(m.n)}</b><div class="msnip">${snip}</div>
  <div class="mmeta" style="margin-top:4px">file: ${esc(m.f)} (Voice Memo Intake)</div></div>`).join('')
  :'<div class="empty">Nothing sung matches that — try fewer letters or a different word.</div>';
}
mq.addEventListener('input',mrender);
</script></body></html>'''

page = page.replace('__DATA__', DATA).replace('__TX__', TX)
open('/home/claude/vault/Jeff Story Song Vault Dashboard.html','w').write(page)
print('dashboard written,', len(page)//1024, 'KB,', len(tx), 'transcripts embedded')
