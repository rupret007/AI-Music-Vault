#!/usr/bin/env node
"use strict";

// Offline layout regression: Node 22+ and an installed Chrome/Chromium, no npm.
// CHROME may point to another installed browser; DASHBOARD_HTML enables testing
// a previous dashboard without changing the worktree. Screenshots are optional.
const assert = require("node:assert/strict");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const { spawn } = require("node:child_process");
const { pathToFileURL } = require("node:url");

const chrome = process.env.CHROME || [
  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
  "/Applications/Chromium.app/Contents/MacOS/Chromium",
  "/usr/bin/chromium", "/usr/bin/chromium-browser", "/usr/bin/google-chrome",
].find(p => fs.existsSync(p));
assert(chrome, "Install Chrome/Chromium or set CHROME (no browser is downloaded)");
const dashboard = process.env.DASHBOARD_HTML || path.resolve(__dirname, "../Jeff Story Song Vault Dashboard.html");
const profile = fs.mkdtempSync(path.join(os.tmpdir(), "vault-filters-"));
const browser = spawn(chrome, [
  "--headless=new", "--disable-gpu", "--no-first-run", "--no-default-browser-check",
  "--disable-extensions", "--disable-background-networking", "--disable-sync",
  "--remote-debugging-pipe", `--user-data-dir=${profile}`, "about:blank",
], { stdio: ["ignore", "ignore", "ignore", "pipe", "pipe"] });
let sequence = 0, buffer = "";
const pending = new Map();
function rejectPending(error) {
  for (const request of pending.values()) {
    clearTimeout(request.timer);
    request.reject(error);
  }
  pending.clear();
}
browser.on("error", rejectPending);
browser.on("exit", (code, signal) => rejectPending(new Error(`Chrome exited: ${signal || code}`)));
browser.stdio[4].on("data", chunk => {
  buffer += chunk.toString();
  let end;
  while ((end = buffer.indexOf("\0")) >= 0) {
    const message = JSON.parse(buffer.slice(0, end));
    buffer = buffer.slice(end + 1);
    const request = pending.get(message.id);
    if (request) {
      pending.delete(message.id);
      clearTimeout(request.timer);
      if (message.error) request.reject(new Error(JSON.stringify(message.error)));
      else request.resolve(message.result);
    }
  }
});
function send(method, params = {}, sessionId) {
  return new Promise((resolve, reject) => {
    const id = ++sequence;
    const timer = setTimeout(() => {
      pending.delete(id);
      reject(new Error(`CDP timeout: ${method}`));
    }, 10000);
    pending.set(id, { resolve, reject, timer });
    browser.stdio[3].write(JSON.stringify({ id, method, params, sessionId }) + "\0");
  });
}

async function main() {
  const { targetId } = await send("Target.createTarget", { url: "about:blank" });
  const { sessionId } = await send("Target.attachToTarget", { targetId, flatten: true });
  const page = (method, params) => send(method, params, sessionId);
  const evaluate = async expression => {
    const response = await page("Runtime.evaluate", { expression, returnByValue: true, awaitPromise: true });
    assert(!response.exceptionDetails, JSON.stringify(response.exceptionDetails));
    return response.result.value;
  };
  const key = async (key, code, windowsVirtualKeyCode) => {
    await page("Input.dispatchKeyEvent", { type: "keyDown", key, code, windowsVirtualKeyCode });
    await page("Input.dispatchKeyEvent", { type: "keyUp", key, code, windowsVirtualKeyCode });
  };
  await page("Page.enable");
  await page("Page.navigate", { url: pathToFileURL(dashboard).href });
  for (let attempt = 0; attempt < 100; attempt++) {
    if (await evaluate("document.querySelectorAll('#list .row').length > 0")) break;
    await new Promise(resolve => setTimeout(resolve, 50));
  }
  assert(await evaluate("document.querySelectorAll('#list .row').length > 0"), "dashboard must render");

  for (const [width, height] of [[1280, 800], [640, 800], [390, 844], [320, 640]]) {
    await page("Emulation.setDeviceMetricsOverride", { width, height, deviceScaleFactor: 1, mobile: false });
    await evaluate("document.getElementById('advancedFilters').open = false; window.scrollTo(0, 0)");
    const closedTop = await evaluate("document.getElementById('list').getBoundingClientRect().top + scrollY");
    await evaluate("document.querySelector('#advancedFilters summary').focus()");
    await key("Enter", "Enter", 13);
    assert(await evaluate("document.getElementById('advancedFilters').open"), "Enter opens native details");
    const geometry = await evaluate(`(() => {
      const rect = selector => { const r = document.querySelector(selector).getBoundingClientRect();
        return {top:r.top + scrollY, bottom:r.bottom + scrollY, left:r.left, right:r.right, width:r.width, height:r.height}; };
      return {menu:rect('.advanced-menu'), details:rect('#advancedFilters'), row:rect('#list .row'),
        list:rect('#list'), controls:rect('#paneS .controls'), overflow:document.documentElement.scrollWidth > innerWidth,
        selects:[...document.querySelectorAll('.advanced-menu select')].map(s => {
          const r=s.getBoundingClientRect(); return {left:r.left, right:r.right, height:r.height}; })};
    })()`);
    assert(geometry.list.top - closedTop >= geometry.menu.height, `${width}px: opening filters must push the list down by the menu height`);
    assert(geometry.row.top >= geometry.menu.bottom, `${width}px: filters must not cover the first song`);
    assert(!geometry.overflow, `${width}px: no horizontal overflow`);
    assert(geometry.menu.left >= 0 && geometry.menu.right <= width, `${width}px: menu stays in viewport`);
    if (width <= 640) assert(Math.abs(geometry.menu.width - geometry.controls.width) < 1, `${width}px: phone menu fills toolbar width`);
    for (const select of geometry.selects) {
      assert(select.left >= geometry.menu.left && select.right <= geometry.menu.right, "select stays inside menu");
      assert(select.height >= 44, "filter has a 44px target");
    }
    await key("Tab", "Tab", 9);
    assert.equal(await evaluate("document.activeElement.id"), "proj", "Tab reaches first filter");
    // Scroll the list into view: a tall sticky toolbar must not cover titles.
    await evaluate("document.querySelector('#list .row').scrollIntoView({block:'start'})");
    assert(await evaluate("document.querySelector('.advanced-menu').getBoundingClientRect().bottom <= document.querySelector('#list .row').getBoundingClientRect().top"), `${width}px: scrolling must not pin the menu over songs`);
    if (process.env.FILTER_SCREENSHOTS) {
      await evaluate("document.getElementById('advancedFilters').scrollIntoView({block:'start'})");
      fs.mkdirSync(process.env.FILTER_SCREENSHOTS, { recursive: true });
      const shot = await page("Page.captureScreenshot", { format: "png" });
      fs.writeFileSync(path.join(process.env.FILTER_SCREENSHOTS, `filters-${width}.png`), Buffer.from(shot.data, "base64"));
    }
    await evaluate("document.querySelector('#advancedFilters summary').focus()");
    await key(" ", "Space", 32);
    assert.equal(await evaluate("document.getElementById('advancedFilters').open"), false, "Space closes native details");
    const restoredTop = await evaluate("document.getElementById('list').getBoundingClientRect().top + scrollY");
    assert(Math.abs(restoredTop - closedTop) < 1, "closing restores list position");
    console.log(`PASS filters layout and keyboard: ${width}x${height}`);
  }

  // Exercise real select input handlers, including combinations and clear.
  const semantics = await evaluate(`(() => {
    const check = (condition, message) => {if(!condition) throw new Error(message);};
    const ids = () => [...document.querySelectorAll('#list .row')].map(el=>el.dataset.songId).sort();
    const change = (id,value) => {const el=document.getElementById(id);el.value=value;el.dispatchEvent(new Event('input'));};
    const matches = {
      proj:(d,v)=>d.p===v, scored:(d,v)=>v==='1'?Number.isFinite(d.pot):!Number.isFinite(d.pot),
      scope:(d,v)=>d.scope===v, evidence:(d,v)=>v==='1'?!!memoEvidenceBySong[d.id]:!memoEvidenceBySong[d.id],
      work:(d,v)=>songWorkKind(d.nx)===v, logicReady:(d,v)=>d.lr===v
    };
    let count=0;
    for(const [id,match] of Object.entries(matches)) {
      for(const option of document.getElementById(id).options) {
        document.getElementById('clearSongFilters').click();
        change(id,option.value);
        const expected=DATA.filter(d=>!option.value||match(d,option.value)).map(d=>d.id).sort();
        check(JSON.stringify(ids())===JSON.stringify(expected),id+' option '+option.value);
        const before=JSON.stringify(ids());
        document.getElementById('advancedFilters').open=true;
        document.getElementById('advancedFilters').open=false;
        check(document.getElementById(id).value===option.value && JSON.stringify(ids())===before,'toggle preserves '+id);
        count++;
      }
    }
    document.getElementById('clearSongFilters').click();
    change('scored','1'); change('evidence','1');
    check(JSON.stringify(ids())===JSON.stringify(DATA.filter(d=>Number.isFinite(d.pot)&&memoEvidenceBySong[d.id]).map(d=>d.id).sort()),'filters intersect');
    document.getElementById('clearSongFilters').click();
    check(ids().length===DATA.length,'clear restores all songs');
    check(Object.keys(matches).every(id=>document.getElementById(id).value===''),'clear resets all selects');
    return count;
  })()`);
  console.log(`PASS filter semantics: ${semantics} options, intersection, toggle retention, clear`);
}

main().catch(error => { console.error(error); process.exitCode = 1; }).finally(async () => {
  for (const request of pending.values()) clearTimeout(request.timer);
  if (browser.exitCode === null && browser.signalCode === null) {
    const exited = new Promise(resolve => browser.once("exit", resolve));
    browser.kill("SIGTERM");
    await exited;
  }
  fs.rmSync(profile, { recursive: true, force: true });
});
