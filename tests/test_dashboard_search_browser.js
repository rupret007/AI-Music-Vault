#!/usr/bin/env node
"use strict";

// Search regression with the real dashboard handlers and installed Chrome.
// No npm or browser downloads. DASHBOARD_HTML can select an earlier dashboard.
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
].find(candidate => fs.existsSync(candidate));
assert(chrome, "Install Chrome/Chromium or set CHROME (no browser is downloaded)");
const dashboard = process.env.DASHBOARD_HTML || path.resolve(__dirname, "../Jeff Story Song Vault Dashboard.html");

// Every exact name has a competing prefix that wins under the ordinary sort.
// Use synthetic metadata so catalog edits cannot accidentally remove coverage.
const songs = [
  { id: "Z-TITLE", t: "It’s Ready", aka: [], mom: 1, pot: 2, rdy: 3, lr: "audio_only" },
  { id: "A-TITLE", t: "A prefix rival", aka: ["It's Ready Again"], mom: 91, pot: 93, rdy: 92, lr: "logic_project_plus_key" },
  { id: "Z-ALIAS", t: "Z alias target", aka: ["We’re Home"], mom: 2, pot: 3, rdy: 1, lr: "key_only" },
  { id: "A-ALIAS", t: "A alias rival", aka: ["We're Home Again"], mom: 92, pot: 91, rdy: 93, lr: "logic_project_no_key" },
  { id: "Z-42", t: "Z id target", aka: [], mom: 3, pot: 1, rdy: 2, lr: "empty_logic_ready" },
  { id: "A-ID", t: "Z 42 Again", aka: [], mom: 93, pot: 92, rdy: 91, lr: "closest_logic_dropin" },
].map(song => ({ p: "Test project", st: "Test status", nx: "Confirm the chorus", lrf: [], ...song }));
const memos = songs.map(song => ({
  f: "Synthetic intake", n: "Synthetic evidence", s: song.id,
  d: "2026-01-" + String(song.mom > 90 ? song.mom - 70 : song.mom).padStart(2, "0"),
  x: "Synthetic evidence for the browser regression.",
}));
let html = fs.readFileSync(dashboard, "utf8");
for (const [name, payload] of [["DATA", songs], ["TX", memos]]) {
  const declaration = new RegExp(`^const ${name} = .*;$`, "m");
  assert(declaration.test(html), `dashboard must declare ${name}`);
  html = html.replace(declaration, () => `const ${name} = ${JSON.stringify(payload)};`);
}
const temporary = fs.mkdtempSync(path.join(os.tmpdir(), "vault-search-"));
const fixture = path.join(temporary, "dashboard.html");
fs.writeFileSync(fixture, html);
const browser = spawn(chrome, [
  "--headless=new", "--disable-gpu", "--no-first-run", "--no-default-browser-check",
  "--disable-extensions", "--disable-background-networking", "--disable-sync",
  "--remote-debugging-pipe", `--user-data-dir=${path.join(temporary, "profile")}`, "about:blank",
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
  const paint = () => evaluate("new Promise(resolve => requestAnimationFrame(() => resolve(true)))");
  const key = async (key, code, windowsVirtualKeyCode) => {
    await page("Input.dispatchKeyEvent", { type: "keyDown", key, code, windowsVirtualKeyCode });
    await page("Input.dispatchKeyEvent", { type: "keyUp", key, code, windowsVirtualKeyCode });
    await paint();
  };
  const search = async (term, sort) => {
    await evaluate(`(() => {
      document.getElementById('clearSongFilters').click();
      const sort = document.getElementById('sort');
      sort.value = ${JSON.stringify(sort)};
      sort.dispatchEvent(new Event('input'));
      const query = document.getElementById('q');
      query.value = ${JSON.stringify(term)};
      query.dispatchEvent(new Event('input'));
      query.focus();
    })()`);
    await paint();
  };
  const visibleIds = () => evaluate("[...document.querySelectorAll('#list .row')].map(row => row.dataset.songId)");
  const openedIds = () => evaluate("[...document.querySelectorAll('#list .rhead[aria-expanded=\"true\"]')].map(head => head.closest('.row').dataset.songId)");

  await page("Page.enable");
  await page("Page.navigate", { url: pathToFileURL(fixture).href });
  for (let attempt = 0; attempt < 100; attempt++) {
    if (await evaluate("document.querySelectorAll('#list .row').length > 0")) break;
    await new Promise(resolve => setTimeout(resolve, 50));
  }
  assert.equal((await visibleIds()).length, songs.length, "synthetic dashboard must render");

  const emptyOrders = {
    mom: ["A-ID", "A-ALIAS", "A-TITLE", "Z-42", "Z-ALIAS", "Z-TITLE"],
    pot: ["A-TITLE", "A-ID", "A-ALIAS", "Z-ALIAS", "Z-TITLE", "Z-42"],
    rdy: ["A-ALIAS", "A-TITLE", "A-ID", "Z-TITLE", "Z-42", "Z-ALIAS"],
    id: ["A-ALIAS", "A-ID", "A-TITLE", "Z-42", "Z-ALIAS", "Z-TITLE"],
    t: ["A-ALIAS", "A-TITLE", "Z-TITLE", "A-ID", "Z-ALIAS", "Z-42"],
    memo: ["A-ID", "A-ALIAS", "A-TITLE", "Z-42", "Z-ALIAS", "Z-TITLE"],
    logic: ["A-ID", "A-TITLE", "A-ALIAS", "Z-TITLE", "Z-ALIAS", "Z-42"],
  };
  const sortModes = await evaluate("[...document.getElementById('sort').options].map(option => option.value)");
  assert.deepEqual(sortModes, Object.keys(emptyOrders), "cover every offered song sort");
  const searches = [
    { label: "title", query: "  ITS READY!!  ", exact: "Z-TITLE", prefix: "A-TITLE" },
    { label: "alias", query: "were home", exact: "Z-ALIAS", prefix: "A-ALIAS" },
    { label: "catalog ID", query: "z 42", exact: "Z-42", prefix: "A-ID" },
  ];
  for (const sort of sortModes) {
    for (const { label, query, exact, prefix } of searches) {
      await search(query, sort);
      assert.deepEqual(await visibleIds(), [exact, prefix], `${sort}: exact normalized ${label} must precede its prefix`);
      await key("Enter", "Enter", 13);
      assert.deepEqual(await openedIds(), [exact], `${sort}: Enter must open the exact ${label}`);
      assert.equal(await evaluate("document.activeElement.id"), "song-row-" + exact, "opened result receives focus");

      await search(query, sort);
      await key("ArrowDown", "ArrowDown", 40);
      await key("ArrowDown", "ArrowDown", 40);
      assert.equal(await evaluate("document.getElementById('q').getAttribute('aria-activedescendant')"), "song-row-" + prefix);
      await key("Enter", "Enter", 13);
      assert.deepEqual(await openedIds(), [prefix], `${sort}: an explicit arrow selection must override the exact result`);
    }
    await evaluate(`(() => {
      const query = document.getElementById('q');
      query.value = '';
      query.dispatchEvent(new Event('input'));
      query.focus();
    })()`);
    await paint();
    assert.equal(await evaluate("document.getElementById('sort').value"), sort, "clearing the query preserves the chosen sort");
    assert.deepEqual(await visibleIds(), emptyOrders[sort], `${sort}: empty query must use the chosen sort`);
    await key("Enter", "Enter", 13);
    assert.deepEqual(await openedIds(), [], "empty search with no arrow selection must not open a song");
    console.log(`PASS search ${sort}: exact title/alias/ID, Enter, arrow override, empty-query sort`);
  }
  console.log(`dashboard search browser OK — ${sortModes.length * searches.length} exact-name cases across ${sortModes.length} sorts`);
}

main().catch(error => { console.error(error); process.exitCode = 1; }).finally(async () => {
  for (const request of pending.values()) clearTimeout(request.timer);
  if (browser.exitCode === null && browser.signalCode === null) {
    const exited = new Promise(resolve => browser.once("exit", resolve));
    browser.kill("SIGTERM");
    await exited;
  }
  fs.rmSync(temporary, { recursive: true, force: true });
});
