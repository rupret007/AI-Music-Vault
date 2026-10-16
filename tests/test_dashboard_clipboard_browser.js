#!/usr/bin/env node
"use strict";

// Offline clipboard feedback regression using an already-installed browser.
// Clipboard APIs are replaced before the dashboard loads; only synthetic text
// reaches the fakes. This test never reads or writes the system clipboard.
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
const profile = fs.mkdtempSync(path.join(os.tmpdir(), "vault-clipboard-"));
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

const installClipboardFakes = `(() => {
  const state = window.__copyTest = {
    mode: 'deferred', fallback: false, writes: [], legacyWrites: [], resolve: null,
  };
  const clipboard = { writeText(value) {
    if (!String(value).startsWith('Write a synthetic')) throw new Error('Unexpected non-synthetic clipboard text');
    state.writes.push(value);
    if (state.mode === 'blocked') return Promise.reject(new DOMException('Denied by test', 'NotAllowedError'));
    if (state.mode === 'success') return Promise.resolve();
    return new Promise(resolve => { state.resolve = resolve; });
  } };
  Object.defineProperty(navigator, 'clipboard', {
    configurable: true, get: () => state.mode === 'legacy' ? undefined : clipboard,
  });
  Object.defineProperty(document, 'execCommand', {
    configurable: true, value(command) {
      const area = document.querySelector('textarea');
      if (command !== 'copy' || !area || !area.value.startsWith('Write a synthetic')) {
        throw new Error('Unexpected legacy clipboard operation');
      }
      state.legacyWrites.push(area.value);
      if (state.fallback === 'throw') throw new DOMException('Denied by test', 'NotAllowedError');
      return state.fallback;
    },
  });
})();`;

async function main() {
  const { targetId } = await send("Target.createTarget", { url: "about:blank" });
  const { sessionId } = await send("Target.attachToTarget", { targetId, flatten: true });
  const page = (method, params) => send(method, params, sessionId);
  const evaluate = async expression => {
    const response = await page("Runtime.evaluate", { expression, returnByValue: true, awaitPromise: true });
    assert(!response.exceptionDetails, JSON.stringify(response.exceptionDetails));
    return response.result.value;
  };
  await page("Page.enable");
  await page("Page.addScriptToEvaluateOnNewDocument", { source: installClipboardFakes });

  for (const [width, height] of [[390, 844], [1280, 800]]) {
    await page("Emulation.setDeviceMetricsOverride", { width, height, deviceScaleFactor: 1, mobile: width < 640 });
    await page("Page.navigate", { url: "about:blank" });
    await page("Page.navigate", { url: pathToFileURL(dashboard).href });
    for (let attempt = 0; attempt < 100; attempt++) {
      if (await evaluate("typeof copyVaultText === 'function' && document.querySelectorAll('#list .row').length > 0")) break;
      await new Promise(resolve => setTimeout(resolve, 50));
    }
    assert(await evaluate("typeof copyVaultText === 'function' && document.querySelectorAll('#list .row').length > 0"), "dashboard must render");

    const result = await evaluate(`(async () => {
      const check = (condition, message) => { if (!condition) throw new Error(message); };
      const tick = () => new Promise(resolve => setTimeout(resolve, 0));
      const state = window.__copyTest;
      const liveStatus = document.getElementById('copyStatus');
      check(liveStatus && liveStatus.textContent === '', 'Clipboard live region exists and is empty before copying');
      check(liveStatus.getAttribute('role') === 'status', 'Clipboard live region has status semantics');
      check(liveStatus.getAttribute('aria-live') === 'polite', 'Clipboard live region is polite');
      check(!liveStatus.hidden && getComputedStyle(liveStatus).display !== 'none' && getComputedStyle(liveStatus).visibility !== 'hidden', 'Clipboard live region remains accessible');
      const wrapper = document.createElement('div');
      const button = document.createElement('button');
      button.type = 'button'; button.textContent = 'Copy next step';
      wrapper.appendChild(button); document.body.prepend(wrapper);
      const value = 'Write a synthetic draft with new chorus lines.';
      const failureText = 'Copy next step: copy failed. Try again or copy the text manually.';
      const assertFailure = target => {
        const status = target.nextElementSibling;
        check(target.textContent === 'Copy next step', 'Failure restores the idle button label');
        check(!target.disabled, 'Failure keeps retry enabled');
        check(!target.classList.contains('copied'), 'Failure never claims a successful copy');
        check(status && status.classList.contains('copy-status'), 'Failure has an inline sibling status');
        check(status.textContent === failureText && !status.hidden, 'Failure explains how to recover');
        check(liveStatus.textContent === failureText, 'Failure reaches the existing live region');
        return status;
      };

      button.focus();
      copyVaultText(value, button, 'Copy next step');
      check(state.writes.length === 1 && state.writes[0] === value, 'Modern API receives exactly the synthetic text');
      check(button.textContent !== 'Copied' && !button.classList.contains('copied'), 'Pending writes must not claim success');
      state.resolve(); await tick();
      check(button.textContent === 'Copied' && button.classList.contains('copied'), 'Resolved writes announce success');

      state.mode = 'blocked'; state.fallback = false;
      copyVaultText(value, button, 'Copy next step'); await tick();
      const status = assertFailure(button);
      check(state.legacyWrites.length === 1, 'Denied modern writes try the legacy fallback');
      check(document.querySelectorAll('textarea').length === 0, 'Failed fallback removes its temporary textarea');
      check(document.activeElement === button, 'Failed fallback restores focus');
      await new Promise(resolve => setTimeout(resolve, 1300));
      check(status.textContent === failureText && !status.hidden, 'Failure persists after an earlier success timer');
      assertFailure(button);

      state.mode = 'success';
      copyVaultText(value, button, 'Copy next step'); await tick();
      check(button.textContent === 'Copied' && button.classList.contains('copied'), 'Retry can succeed');
      check(status.textContent === 'Copy next step: copied.' && !status.hidden, 'Successful retry replaces failure with an accessible success announcement');
      check(liveStatus.textContent === 'Copy next step: copied.', 'Retry success reaches the existing live region');
      check(!button.disabled, 'Successful retry leaves the button enabled');

      state.mode = 'legacy'; state.fallback = true;
      button.focus();
      copyVaultText(value, button, 'Copy next step'); await tick();
      check(button.textContent === 'Copied' && button.classList.contains('copied'), 'Legacy success announces success');
      check(document.querySelectorAll('textarea').length === 0, 'Legacy success removes its temporary textarea');
      check(document.activeElement === button, 'Legacy success restores focus');
      state.fallback = 'throw';
      copyVaultText(value, button, 'Copy next step'); await tick();
      assertFailure(button);
      check(document.querySelectorAll('textarea').length === 0, 'Throwing fallback removes its temporary textarea');
      check(document.activeElement === button, 'Throwing fallback restores focus');
      wrapper.remove();

      // Exercise the actual work-session event handler with synthetic in-memory
      // next-action text; committed catalog metadata is never changed.
      const song = DATA.find(row => songWorkKind(row.nx) === 'write');
      check(!!song, 'The dashboard has a writing session fixture');
      song.nx = value;
      openWork('write', song.id);
      await new Promise(resolve => requestAnimationFrame(resolve));
      const workButton = document.getElementById('copyWorkNext');
      check(!workButton.hidden && !workButton.disabled, 'Work-session copy action is available');
      const writesBeforeWork = state.writes.length;
      state.mode = 'blocked'; state.fallback = false;
      workButton.focus(); workButton.click(); await tick();
      const workStatus = assertFailure(workButton);
      check(state.writes.length === writesBeforeWork + 1 && state.writes.at(-1) === value, 'Real work action passes its exact synthetic next step');
      check(document.activeElement === workButton, 'Real work copy failure preserves focus');
      workStatus.scrollIntoView({ block: 'center' });
      const box = workStatus.getBoundingClientRect();
      check(box.width > 0 && box.height > 0, 'Failure explanation is visibly rendered');
      check(box.left >= 0 && box.right <= innerWidth + 1, 'Failure explanation fits the viewport');
      check(document.documentElement.scrollWidth <= innerWidth + 1, 'Failure feedback does not cause horizontal overflow');
      state.mode = 'success';
      workButton.click(); await tick();
      check(workButton.textContent === 'Copied' && workButton.classList.contains('copied'), 'Real work action retries successfully: ' + JSON.stringify({label: workButton.textContent, disabled: workButton.disabled, writes: state.writes.length, status: workStatus.textContent}));
      check(workStatus.textContent === 'Copy next step: copied.' && !workStatus.hidden, 'Real work retry replaces its failure explanation with success');
      check(document.querySelectorAll('textarea').length === 0, 'All temporary textareas are cleaned up');
      return { modernWrites: state.writes.length, legacyWrites: state.legacyWrites.length };
    })()`);
    console.log(`PASS clipboard feedback and retry: ${width}x${height} (${result.modernWrites} modern, ${result.legacyWrites} legacy attempts)`);
  }
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
