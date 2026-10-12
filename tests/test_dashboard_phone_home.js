#!/usr/bin/env node
"use strict";

// Offline 390×844 home geometry: 12px body padding and 2-up stats when expanded.
// Node 22+ and an already-installed Chrome/Chromium. Never downloads a browser;
// the check will not download a browser if Chrome is missing.
// Missing Chrome or a crash before paint is fail-closed, not viewport proof.
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
const profile = fs.mkdtempSync(path.join(os.tmpdir(), "vault-phone-home-"));
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
  await page("Page.enable");
  await page("Page.navigate", { url: pathToFileURL(dashboard).href });
  for (let attempt = 0; attempt < 100; attempt++) {
    if (await evaluate("document.querySelectorAll('#stats .stat').length > 0 || document.querySelectorAll('#list .row').length > 0")) break;
    await new Promise(resolve => setTimeout(resolve, 50));
  }
  await page("Emulation.setDeviceMetricsOverride", {
    width: 390, height: 844, deviceScaleFactor: 1, mobile: true,
  });
  await evaluate("window.scrollTo(0, 0)");
  const home = await evaluate(`(() => {
    const body = getComputedStyle(document.body);
    const h1 = document.querySelector("h1");
    const work = document.getElementById("workStarts");
    return {
      innerWidth,
      innerHeight,
      paddingLeft: body.paddingLeft,
      paddingRight: body.paddingRight,
      h1Left: h1 ? Math.round(h1.getBoundingClientRect().left) : null,
      workVisible: !!(work && work.getBoundingClientRect().bottom > 0 && work.getBoundingClientRect().top < innerHeight),
      overflow: document.documentElement.scrollWidth > innerWidth + 1
    };
  })()`);
  assert.equal(home.innerWidth, 390, "viewport width must be 390");
  assert.equal(home.innerHeight, 844, "viewport height must be 844");
  assert.equal(home.paddingLeft, "12px", "390px home must use 12px body padding");
  assert.equal(home.paddingRight, "12px", "390px home must use 12px body padding");
  assert.equal(home.h1Left, 12, "H1 must sit on the 12px phone padding");
  assert.equal(home.workVisible, true, "Write / Produce / Listen must be on the first 390×844 screen");
  assert.equal(home.overflow, false, "390px home must not overflow horizontally");

  const expanded = await evaluate(`(() => {
    const fold = document.getElementById("statsFold");
    if (fold) fold.open = true;
    const stats = [...document.querySelectorAll("#stats .stat")].map(el => {
      const box = el.getBoundingClientRect();
      return {top: Math.round(box.top), left: box.left, right: box.right};
    });
    const firstTop = stats[0] && stats[0].top;
    const firstRow = stats.filter(stat => stat.top === firstTop);
    return {
      count: stats.length,
      firstRowCount: firstRow.length,
      clipped: stats.some(stat => stat.left < 0 || stat.right > innerWidth + 1),
      overflow: document.documentElement.scrollWidth > innerWidth + 1
    };
  })()`);
  assert.ok(expanded.count >= 2, "expanded stats must render cards");
  assert.equal(expanded.firstRowCount, 2, "expanded stats must be 2-up at 390px");
  assert.equal(expanded.clipped, false, "390px expanded stats must not clip");
  assert.equal(expanded.overflow, false, "390px expanded stats must not overflow horizontally");
  console.log("PASS 390x844 phone padding and 2-up stats");
}

main().catch(error => { console.error(error); process.exitCode = 1; }).finally(async () => {
  for (const request of pending.values()) clearTimeout(request.timer);
  if (browser.exitCode === null && browser.signalCode === null) {
    const exited = new Promise(resolve => browser.once("exit", resolve));
    browser.kill("SIGTERM");
    await exited;
  }
  try { fs.rmSync(profile, { recursive: true, force: true }); } catch {}
});
