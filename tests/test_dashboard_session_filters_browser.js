#!/usr/bin/env node
"use strict";

// Exercise real dashboard events in an isolated installed Chrome profile.
// No downloads, personal music, or clipboard access. DASHBOARD_HTML selects
// an earlier dashboard when proving this regression fails before the fix.
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
const storageKey = "vault:last-work:v1";
const songs = [
  { id: "TEST-A", t: "Alpha", p: "First project", mom: 90 },
  { id: "TEST-B", t: "Beta", p: "Second project", mom: 70 },
  { id: "TEST-C", t: "Gamma", p: "First project", mom: 50 },
  { id: "TEST-W", t: "Writing", p: "First project", mom: 95, nx: "Transcribe the synthetic chorus." },
].map(song => ({
  st: "Draft", pot: 60, rdy: 50, lr: "audio_only", lrf: [],
  nx: `Listen to the synthetic ${song.t} chorus and rate it.`, ...song,
}));
const memos = songs.map(song => ({
  s: song.id, f: "Synthetic intake", n: "Synthetic memo", d: "2026-01-01",
  x: "Synthetic transcript for the session regression.",
}));
let html = fs.readFileSync(dashboard, "utf8");
for (const [name, payload] of [["DATA", songs], ["TX", memos]]) {
  const declaration = new RegExp(`^const ${name} = .*;$`, "m");
  assert(declaration.test(html), `dashboard must declare ${name}`);
  html = html.replace(declaration, () => `const ${name} = ${JSON.stringify(payload)};`);
}
const temporary = fs.mkdtempSync(path.join(os.tmpdir(), "vault-session-filters-"));
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
  const waitFor = async (expression, label) => {
    for (let attempt = 0; attempt < 100; attempt++) {
      try {
        if (await evaluate(expression)) return;
      } catch (error) {
        // Reload destroys the old execution context before creating the new one.
        if (!String(error).includes("context")) throw error;
      }
      await new Promise(resolve => setTimeout(resolve, 50));
    }
    assert.fail(`timed out waiting for ${label}`);
  };
  const click = async selector => {
    await evaluate(`(() => {
      const element = document.querySelector(${JSON.stringify(selector)});
      if (!element || element.disabled || element.hidden) throw new Error('Unavailable control: ' + ${JSON.stringify(selector)});
      element.click();
    })()`);
    await paint();
  };
  const input = async (id, value) => {
    await evaluate(`(() => {
      const element = document.getElementById(${JSON.stringify(id)});
      element.value = ${JSON.stringify(value)};
      element.dispatchEvent(new Event('input', { bubbles: true }));
      element.focus();
    })()`);
    await paint();
  };
  const key = async (key, code, windowsVirtualKeyCode) => {
    await page("Input.dispatchKeyEvent", { type: "keyDown", key, code, windowsVirtualKeyCode });
    await page("Input.dispatchKeyEvent", { type: "keyUp", key, code, windowsVirtualKeyCode });
    await paint();
  };
  const state = () => evaluate(`(() => ({
    active: activeWorkSongId,
    stored: JSON.parse(localStorage.getItem(${JSON.stringify(storageKey)})),
    visible: [...document.querySelectorAll('#list .row')].map(row => row.dataset.songId),
    opened: [...document.querySelectorAll('#list .rhead[aria-expanded="true"]')].map(head => head.closest('.row').dataset.songId),
    query: q.value, project: proj.value, kind: work.value, hash: location.hash,
    nextText: workSessionNext.textContent,
    nextDisabled: workNext.disabled,
    controls: ['copyWorkNext', 'copyWorkLogic', 'openWorkEvidence'].map(id => {
      const element = document.getElementById(id);
      return { id, hidden: element.hidden, disabled: element.disabled, songId: element.dataset.songId };
    }),
  }))()`);
  const assertSelected = async (id, label) => {
    const current = await state();
    assert.equal(current.active, id, `${label}: selected work song`);
    assert.deepEqual(current.stored, { v: 1, kind: current.kind, id }, `${label}: exact saved session`);
    assert.deepEqual(current.opened, [id], `${label}: only selected song expands`);
    assert.equal(current.controls[0].songId, id, `${label}: next-step button belongs to selected song`);
    assert.equal(current.controls[0].hidden, false, `${label}: selected next step is available`);
    assert.equal(current.nextText, "Do this now: " + songs.find(song => song.id === id).nx, `${label}: selected song's next step`);
  };
  const assertRetained = async (visible, label) => {
    const current = await state();
    assert.equal(current.active, "TEST-B", `${label}: filtering must preserve the exact active work song`);
    assert.deepEqual(current.stored, { v: 1, kind: "listen", id: "TEST-B" }, `${label}: filtering must not overwrite Resume`);
    assert.deepEqual(current.visible, visible, `${label}: results still honor the filter`);
    assert.deepEqual(current.opened, [], `${label}: filtering must not start another song`);
    assert.equal(current.nextText, "", `${label}: no unrelated current next step`);
    for (const control of current.controls) {
      assert.equal(control.hidden, true, `${label}: ${control.id} hidden without a visible selection`);
      assert.equal(control.disabled, true, `${label}: ${control.id} disabled without a visible selection`);
      assert.equal(control.songId, "", `${label}: ${control.id} has no stale song`);
    }
    assert.equal(current.nextDisabled, !visible.length, `${label}: Next requires matching results`);
  };
  const startSecondSong = async () => {
    await click('[data-open-work="listen"]');
    await assertSelected("TEST-A", "explicit Start selects first song");
    await click("#workNext");
    await assertSelected("TEST-B", "Next selects second song");
  };

  await page("Page.enable");
  await page("Page.navigate", { url: pathToFileURL(fixture).href });
  await waitFor("document.querySelectorAll('#list .row').length === 4", "synthetic dashboard");
  for (const [width, height] of [[390, 844], [1280, 800]]) {
    await page("Emulation.setDeviceMetricsOverride", { width, height, deviceScaleFactor: 1, mobile: false });
    await startSecondSong();

    await input("q", "no-such-synthetic-song");
    await assertRetained([], "empty search");
    await input("q", "");
    await assertSelected("TEST-B", "clearing empty search restores exact song");

    await input("q", "Alpha");
    await assertRetained(["TEST-A"], "search excludes current song");
    await input("q", "");
    await assertSelected("TEST-B", "clearing matching search restores exact song");

    await input("proj", "First project");
    await assertRetained(["TEST-A", "TEST-C"], "project filter excludes current song");
    await input("q", "no-such-synthetic-song");
    await assertRetained([], "combined filters yield no songs");
    await input("q", "");
    await assertRetained(["TEST-A", "TEST-C"], "clearing query retains project filter");
    await input("proj", "");
    await assertSelected("TEST-B", "clearing project restores exact song");

    await input("q", "Alpha");
    await click("#resumeWorkButton");
    await assertSelected("TEST-B", "Resume restores saved song");
    assert.equal((await state()).query, "", "Resume clears search");

    await input("proj", "First project");
    const previousOrigin = await evaluate("performance.timeOrigin");
    await page("Page.reload", { ignoreCache: true });
    await waitFor(`performance.timeOrigin !== ${previousOrigin} && document.querySelectorAll('#list .row').length === 3`, "reloaded work session");
    await paint();
    await assertSelected("TEST-B", "refresh preserves exact saved song");
    assert.equal((await state()).hash, "#work=listen", "refresh restores the work route");
    assert.equal((await state()).project, "", "refresh clears temporary project filter");

    await input("q", "Alpha");
    await click("#workNext");
    await assertSelected("TEST-A", "explicit Next selects matching song");
    await startSecondSong();
    await input("proj", "First project");
    await input("q", "");
    await key("ArrowDown", "ArrowDown", 40);
    await key("ArrowDown", "ArrowDown", 40);
    assert.equal(await evaluate("q.getAttribute('aria-activedescendant')"), "song-row-TEST-C", "arrows select second visible match");
    await key("Enter", "Enter", 13);
    await assertSelected("TEST-C", "explicit Enter selects highlighted matching song");

    await input("work", "write");
    await assertSelected("TEST-W", "explicit work-kind change starts its first match");
    assert.equal((await state()).stored.kind, "write", "changed kind updates Resume");
    console.log(`PASS ${width}x${height}: temporary search/filter retention, Resume, refresh, explicit Next/Enter/kind selection`);
  }
  console.log("dashboard session filters browser OK — 2 viewports");
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
