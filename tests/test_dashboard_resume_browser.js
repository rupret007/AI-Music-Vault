#!/usr/bin/env node
"use strict";

// Requires an already-installed Chrome/Chromium. Never downloads a browser.
// Same launch style as shot.sh (system Chrome + CDP). Fail closed on missing
// Chrome or a crash before paint — that is not viewport proof.
// Usage: node tests/test_dashboard_resume_browser.js /absolute/evidence/directory
const assert = require("node:assert/strict");
const fs = require("node:fs");
const http = require("node:http");
const net = require("node:net");
const os = require("node:os");
const path = require("node:path");
const { spawn } = require("node:child_process");

const htmlPath = path.join(__dirname, "..", "Jeff Story Song Vault Dashboard.html");
const htmlName = path.basename(htmlPath);
const outdir = process.argv[2];
assert.ok(outdir && path.isAbsolute(outdir), "Supply an absolute screenshot output directory");
const storageKey = "vault:last-work:v1";

function chromePath() {
  if (process.env.CHROME && fs.existsSync(process.env.CHROME)) return process.env.CHROME;
  const candidates = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
  ];
  return candidates.find(candidate => fs.existsSync(candidate)) || "";
}

function freePort() {
  return new Promise((resolve, reject) => {
    const server = net.createServer();
    server.listen(0, "127.0.0.1", () => {
      const { port } = server.address();
      server.close(err => err ? reject(err) : resolve(port));
    });
    server.on("error", reject);
  });
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function waitJson(url, tries = 50) {
  for (let i = 0; i < tries; i++) {
    try {
      const res = await fetch(url);
      if (res.ok) return await res.json();
    } catch {}
    await sleep(100);
  }
  throw new Error("Chrome debug port not ready: " + url);
}

class CDP {
  constructor(wsUrl) {
    this.ws = new WebSocket(wsUrl);
    this.id = 0;
    this.pending = new Map();
    this.ws.addEventListener("message", ev => {
      const msg = JSON.parse(ev.data);
      if (msg.id && this.pending.has(msg.id)) {
        const { resolve, reject } = this.pending.get(msg.id);
        this.pending.delete(msg.id);
        if (msg.error) reject(new Error(JSON.stringify(msg.error)));
        else resolve(msg.result || {});
      }
    });
  }
  ready() {
    return new Promise((resolve, reject) => {
      this.ws.addEventListener("open", resolve, { once: true });
      this.ws.addEventListener("error", reject, { once: true });
    });
  }
  send(method, params = {}) {
    const id = ++this.id;
    return new Promise((resolve, reject) => {
      const timer = setTimeout(() => {
        this.pending.delete(id);
        reject(new Error("CDP timeout " + method));
      }, 20000);
      this.pending.set(id, {
        resolve: value => { clearTimeout(timer); resolve(value); },
        reject: error => { clearTimeout(timer); reject(error); },
      });
      this.ws.send(JSON.stringify({ id, method, params }));
    });
  }
  close() { try { this.ws.close(); } catch {} }
}

async function evalValue(cdp, expression) {
  const res = await cdp.send("Runtime.evaluate", {
    expression,
    returnByValue: true,
    awaitPromise: true,
  });
  if (res.exceptionDetails) {
    throw new Error("eval failed: " + JSON.stringify(res.exceptionDetails));
  }
  return res.result && res.result.value;
}

async function waitFor(cdp, expression, label) {
  const start = Date.now();
  while (Date.now() - start < 15000) {
    if (await evalValue(cdp, expression)) return;
    await sleep(100);
  }
  throw new Error("timed out waiting for " + label);
}

const MEASURE_EXPR = `(() => {
  const viewport = { width: window.innerWidth, height: window.innerHeight, scrollY: window.scrollY };
  const boxes = {};
  for (const id of ["resumeWorkButton", "resumeWorkNext", "copyResumeNext", "forgetWorkSession"]) {
    const el = document.getElementById(id);
    if (!el) { boxes[id] = null; continue; }
    const box = el.getBoundingClientRect();
    const style = getComputedStyle(el);
    const hidden = !!(el.hidden || el.closest("[hidden]"));
    boxes[id] = {
      x: box.x, y: box.y, width: box.width, height: box.height,
      visible: !hidden && style.display !== "none" && style.visibility !== "hidden"
        && box.width > 0 && box.height > 0,
      disabled: !!el.disabled,
      text: String(el.innerText || "").trim(),
    };
  }
  const overview = document.getElementById("catalogOverview");
  const details = document.querySelector(".resume-details");
  return {
    viewport, boxes,
    overviewOpen: !!(overview && overview.open),
    detailsOpen: !!(details && details.open),
    copySongId: (document.getElementById("copyResumeNext") || {}).getAttribute
      ? document.getElementById("copyResumeNext").getAttribute("data-song-id") : "",
    focusId: (document.activeElement || {}).id || "",
    focusClass: (document.activeElement || {}).className || "",
    focusOpenWork: (document.activeElement || {}).getAttribute
      ? document.activeElement.getAttribute("data-open-work") : "",
    resumeHidden: !!(document.getElementById("resumeWork") && document.getElementById("resumeWork").hidden),
    workSessionHidden: !!(document.getElementById("workSession") && document.getElementById("workSession").hidden),
    workCopySongId: (document.getElementById("copyWorkNext") || {}).getAttribute
      ? document.getElementById("copyWorkNext").getAttribute("data-song-id") : "",
    stored: localStorage.getItem(${JSON.stringify(storageKey)}),
  };
})()`;

function assertFirstScreen(state, viewport) {
  assert.equal(state.viewport.scrollY, 0, "Resume must start without scrolling");
  assert.equal(state.overviewOpen, false, "Catalog details must start collapsed");
  assert.equal(state.detailsOpen, false, "Logic-ready details must start collapsed");
  assert.equal(state.viewport.width, viewport.width, "viewport width must match the required shot");
  assert.equal(state.viewport.height, viewport.height, "viewport height must match the required shot");
  const boxes = {};
  for (const id of ["resumeWorkButton", "resumeWorkNext", "copyResumeNext", "forgetWorkSession"]) {
    const box = state.boxes[id];
    assert.ok(box && box.visible, id + " must be visible");
    assert.ok(box.width > 0 && box.height > 0, id + " must have rendered bounds");
    assert.ok(box.x >= 0 && box.x + box.width <= viewport.width, id + " must fit horizontally");
    assert.ok(box.y >= 0 && box.y + box.height <= viewport.height, id + " must fit above the fold");
    if (id !== "resumeWorkNext") {
      assert.ok(box.height >= 44, id + " must retain a 44px target");
      assert.equal(box.disabled, false, id + " must be enabled");
    }
    boxes[id] = { x: box.x, y: box.y, width: box.width, height: box.height };
  }
  assert.match(state.boxes.resumeWorkButton.text, /^Resume Listen · .+/);
  assert.match(state.boxes.resumeWorkNext.text, /^Do this now: .+/);
  return boxes;
}

async function connectPage(debugPort) {
  const pages = await waitJson("http://127.0.0.1:" + debugPort + "/json/list");
  const page = pages.find(item => item.type === "page" && item.webSocketDebuggerUrl);
  assert.ok(page, "Chrome did not expose a page target");
  const cdp = new CDP(page.webSocketDebuggerUrl);
  await cdp.ready();
  await cdp.send("Page.enable");
  await cdp.send("Runtime.enable");
  return cdp;
}

async function tabTo(cdp) {
  await cdp.send("Input.dispatchKeyEvent", { type: "keyDown", key: "Tab", windowsVirtualKeyCode: 9, nativeVirtualKeyCode: 9 });
  await cdp.send("Input.dispatchKeyEvent", { type: "keyUp", key: "Tab", windowsVirtualKeyCode: 9, nativeVirtualKeyCode: 9 });
}

(async () => {
  fs.mkdirSync(outdir, { recursive: true });
  const chrome = chromePath();
  if (!chrome) {
    throw new Error("Chrome/Chromium not found (offline; will not download a browser)");
  }
  const debugPort = await freePort();
  const serverPort = await freePort();
  const userData = fs.mkdtempSync(path.join(os.tmpdir(), "vault-resume-chrome-"));
  const dashboard = `http://127.0.0.1:${serverPort}/${encodeURIComponent(htmlName)}`;
  const server = http.createServer((req, res) => {
    const wanted = decodeURIComponent((req.url || "/").split("?")[0]);
    if (wanted === "/" + htmlName || wanted === "/" + encodeURIComponent(htmlName)) {
      res.writeHead(200, { "Content-Type": "text/html; charset=utf-8" });
      fs.createReadStream(htmlPath).pipe(res);
      return;
    }
    res.writeHead(404);
    res.end();
  });
  await new Promise((resolve, reject) => {
    server.listen(serverPort, "127.0.0.1", resolve);
    server.on("error", reject);
  });
  const chromeLogs = [];
  const browser = spawn(chrome, [
    "--headless=new",
    "--disable-gpu",
    "--no-first-run",
    "--no-default-browser-check",
    "--disable-extensions",
    "--disable-background-networking",
    "--disable-sync",
    "--hide-scrollbars",
    "--force-device-scale-factor=1",
    "--force-color-profile=srgb",
    "--remote-debugging-address=127.0.0.1",
    `--remote-debugging-port=${debugPort}`,
    `--user-data-dir=${userData}`,
    "about:blank",
  ], { stdio: ["ignore", "pipe", "pipe"] });
  const logChunk = chunk => chromeLogs.push(String(chunk));
  browser.stdout.on("data", logChunk);
  browser.stderr.on("data", logChunk);
  const chromeExit = new Promise(resolve => browser.on("exit", (code, signal) => resolve({ code, signal })));
  let cdp;
  const results = [];
  try {
    const died = await Promise.race([
      waitJson("http://127.0.0.1:" + debugPort + "/json/version").then(info => ({ info })),
      chromeExit.then(exit => exit),
    ]);
    if (!died.info) {
      throw new Error("Chrome exited before debugging started: " + JSON.stringify({
        code: died.code, logs: chromeLogs.join("").slice(-2000),
      }));
    }
    cdp = await connectPage(debugPort);
    for (const viewport of [
      { name: "phone", width: 390, height: 844, mobile: true },
      { name: "desktop", width: 1280, height: 800, mobile: false },
    ]) {
      await cdp.send("Emulation.setDeviceMetricsOverride", {
        width: viewport.width,
        height: viewport.height,
        deviceScaleFactor: 1,
        mobile: viewport.mobile,
      });
      await cdp.send("Emulation.setEmulatedMedia", {
        features: [{ name: "prefers-color-scheme", value: "dark" }],
      });
      await cdp.send("Emulation.setFocusEmulationEnabled", { enabled: true }).catch(() => {});
      await cdp.send("Storage.clearDataForOrigin", {
        origin: "http://127.0.0.1:" + serverPort,
        storageTypes: "local_storage",
      }).catch(() => {});
      await cdp.send("Page.navigate", { url: dashboard, transitionType: "reload" });
      await waitFor(cdp, `!!document.querySelector('#workStarts button')`, "work starts");
      await evalValue(cdp, `document.querySelector('[data-open-work="listen"]').click()`);
      await waitFor(cdp, `!document.getElementById("workSession").hidden`, "listen session");
      const saved = JSON.parse(await evalValue(cdp, `localStorage.getItem(${JSON.stringify(storageKey)})`));
      assert.deepEqual(Object.keys(saved).sort(), ["id", "kind", "v"]);
      assert.equal(saved.kind, "listen");
      assert.equal(saved.v, 1);
      await cdp.send("Page.navigate", { url: dashboard, transitionType: "reload" });
      await waitFor(cdp, `!!(document.getElementById("resumeWorkButton") && !document.getElementById("resumeWork").hidden)`, "Resume");
      await evalValue(cdp, `window.scrollTo(0,0)`);
      let state = await evalValue(cdp, MEASURE_EXPR);
      const boxes = assertFirstScreen(state, viewport);
      assert.equal(state.copySongId, saved.id);
      const shot = await cdp.send("Page.captureScreenshot", { format: "png", fromSurface: true });
      fs.writeFileSync(path.join(outdir, `resume-${viewport.name}.png`), Buffer.from(shot.data, "base64"));

      await evalValue(cdp, `(() => {
        const style = document.createElement("style");
        style.id = "a02-offscreen-mutation";
        style.textContent = ".resume-work{margin-top:2000px!important}";
        document.head.appendChild(style);
        return true;
      })()`);
      state = await evalValue(cdp, MEASURE_EXPR);
      assert.throws(
        () => assertFirstScreen(state, viewport),
        /resumeWorkButton must fit above the fold/,
      );
      await evalValue(cdp, `(() => {
        const style = document.getElementById("a02-offscreen-mutation");
        if (style) style.remove();
        window.scrollTo(0,0);
        return true;
      })()`);
      state = await evalValue(cdp, MEASURE_EXPR);
      assertFirstScreen(state, viewport);

      await evalValue(cdp, `window.focus()`);
      await tabTo(cdp);
      state = await evalValue(cdp, MEASURE_EXPR);
      assert.equal(state.focusClass.split(/\s+/)[0], "skip-link");
      for (const id of ["resumeWorkButton", "copyResumeNext", "forgetWorkSession"]) {
        await tabTo(cdp);
        state = await evalValue(cdp, MEASURE_EXPR);
        assert.equal(state.focusId, id);
      }
      await evalValue(cdp, `document.getElementById("resumeWorkButton").click()`);
      await waitFor(cdp, `!document.getElementById("workSession").hidden`, "resumed work session");
      state = await evalValue(cdp, MEASURE_EXPR);
      assert.equal(state.workSessionHidden, false);
      assert.equal(state.workCopySongId, saved.id);
      await evalValue(cdp, `document.getElementById("forgetWorkSession").click()`);
      await waitFor(cdp, `!!(document.getElementById("resumeWork") && document.getElementById("resumeWork").hidden)`, "Forget");
      await waitFor(cdp, `document.activeElement && document.activeElement.getAttribute("data-open-work")==="write"`, "Forget focus");
      state = await evalValue(cdp, MEASURE_EXPR);
      assert.equal(state.stored, null);
      assert.equal(state.resumeHidden, true);
      assert.equal(state.overviewOpen, true);
      assert.equal(state.focusOpenWork, "write");
      await cdp.send("Page.reload");
      await waitFor(cdp, `!!document.querySelector('#workStarts button')`, "reload after Forget");
      state = await evalValue(cdp, MEASURE_EXPR);
      assert.equal(state.resumeHidden, true);
      assert.equal(state.stored, null);
      results.push({ viewport, saved, boxes });
      console.log(`PASS: resume ${viewport.name} geometry, mutation rejection, keyboard, Resume and Forget`);
    }
    const version = await waitJson("http://127.0.0.1:" + debugPort + "/json/version");
    fs.writeFileSync(path.join(outdir, "resume-geometry.json"), JSON.stringify({
      browser: version.Browser || version["Browser"],
      results,
    }, null, 2) + "\n");
  } finally {
    if (cdp) cdp.close();
    if (browser.exitCode === null) browser.kill("SIGKILL");
    await Promise.race([chromeExit, sleep(3000)]);
    server.close();
    for (let i = 0; i < 8; i++) {
      try {
        fs.rmSync(userData, { recursive: true, force: true });
        break;
      } catch (err) {
        if (i === 7) {
          console.error("warning: leftover Chrome profile " + userData + " (" + err.message + ")");
        } else {
          await sleep(250);
        }
      }
    }
  }
})().catch(error => {
  console.error(error);
  process.exitCode = 1;
});
