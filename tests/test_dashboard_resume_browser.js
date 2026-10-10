#!/usr/bin/env node
"use strict";

// Requires an installed Playwright and Chromium; never downloads dependencies.
// Usage: node tests/test_dashboard_resume_browser.js /absolute/evidence/directory
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const { chromium } = require("playwright");
const html = fs.readFileSync(path.join(__dirname, "..", "Jeff Story Song Vault Dashboard.html"), "utf8");
const outdir = process.argv[2];
assert.ok(outdir && path.isAbsolute(outdir), "Supply an absolute screenshot output directory");
const dashboard = "https://vault.test/dashboard";
const storageKey = "vault:last-work:v1";

async function assertFirstScreen(page) {
  assert.equal(await page.evaluate(() => window.scrollY), 0, "Resume must start without scrolling");
  assert.equal(await page.locator("#catalogOverview").evaluate(el => el.open), false);
  assert.equal(await page.locator(".resume-details").evaluate(el => el.open), false);
  const viewport = page.viewportSize();
  const boxes = {};
  for (const id of ["resumeWorkButton", "resumeWorkNext", "copyResumeNext", "forgetWorkSession"]) {
    const el = page.locator("#" + id);
    assert.equal(await el.isVisible(), true, id + " must be visible");
    const box = await el.boundingBox();
    assert.ok(box && box.width > 0 && box.height > 0, id + " must have rendered bounds");
    assert.ok(box.x >= 0 && box.x + box.width <= viewport.width,
      id + " must fit horizontally");
    assert.ok(box.y >= 0 && box.y + box.height <= viewport.height,
      id + " must fit above the fold");
    if (id !== "resumeWorkNext") {
      assert.ok(box.height >= 44, id + " must retain a 44px target");
      assert.equal(await el.isEnabled(), true, id + " must be enabled");
    }
    boxes[id] = box;
  }
  assert.match(await page.locator("#resumeWorkButton").innerText(), /^Resume Listen · .+/);
  assert.match(await page.locator("#resumeWorkNext").innerText(), /^Do this now: .+/);
  return boxes;
}

(async () => {
  fs.mkdirSync(outdir, { recursive: true });
  const browser = await chromium.launch({
    headless: true,
    ...(process.env.CHROME ? { executablePath: process.env.CHROME } : {}),
  });
  const results = [];
  try {
    for (const viewport of [
      { name: "phone", width: 390, height: 844, isMobile: true },
      { name: "desktop", width: 1280, height: 800, isMobile: false },
    ]) {
      const context = await browser.newContext({
        viewport: { width: viewport.width, height: viewport.height },
        isMobile: viewport.isMobile, deviceScaleFactor: 1, colorScheme: "dark",
        serviceWorkers: "block",
      });
      try {
        // Serve the actual dashboard in memory: no localhost server or network.
        await context.route("**/*", route => route.request().url() === dashboard
          ? route.fulfill({ contentType: "text/html", body: html }) : route.abort());
        const page = await context.newPage();
        const errors = [];
        page.on("pageerror", error => errors.push(error.message));
        await page.goto(dashboard);
        await page.locator('[data-open-work="listen"]').click();
        const saved = await page.evaluate(key => JSON.parse(localStorage.getItem(key)), storageKey);
        assert.deepEqual(Object.keys(saved).sort(), ["id", "kind", "v"]);
        assert.equal(saved.kind, "listen");
        assert.equal(saved.v, 1);
        // Fresh landing with the session that the real UI saved, no work hash.
        await page.goto(dashboard);
        await page.locator("#resumeWorkButton").waitFor();
        const boxes = await assertFirstScreen(page);
        assert.equal(await page.locator("#copyResumeNext").getAttribute("data-song-id"), saved.id);
        await page.screenshot({ path: path.join(outdir, `resume-${viewport.name}.png`), fullPage: false });

        // Prove this geometry check rejects the review's offscreen CSS mutation.
        const mutation = await page.addStyleTag({ content: ".resume-work{margin-top:2000px!important}" });
        await assert.rejects(assertFirstScreen(page), /resumeWorkButton must fit above the fold/);
        await mutation.evaluate(el => el.remove());
        await assertFirstScreen(page);

        // Native browser keyboard order and Resume/Forget behavior.
        await page.keyboard.press("Tab");
        assert.equal(await page.locator(":focus").getAttribute("class"), "skip-link");
        for (const id of ["resumeWorkButton", "copyResumeNext", "forgetWorkSession"]) {
          await page.keyboard.press("Tab");
          assert.equal(await page.locator(":focus").getAttribute("id"), id);
        }
        await page.locator("#resumeWorkButton").click();
        assert.equal(await page.locator("#workSession").isVisible(), true);
        assert.equal(await page.locator("#copyWorkNext").getAttribute("data-song-id"), saved.id);
        await page.locator("#forgetWorkSession").click();
        assert.equal(await page.evaluate(key => localStorage.getItem(key), storageKey), null);
        assert.equal(await page.locator("#resumeWork").isVisible(), false);
        assert.equal(await page.locator("#catalogOverview").evaluate(el => el.open), true);
        assert.equal(await page.locator(":focus").getAttribute("data-open-work"), "write");
        await page.reload();
        assert.equal(await page.locator("#resumeWork").isVisible(), false);
        assert.deepEqual(errors, [], "Dashboard must not throw browser errors");
        results.push({ viewport, saved, boxes });
        console.log(`PASS: resume ${viewport.name} geometry, mutation rejection, keyboard, Resume and Forget`);
      } finally {
        await context.close();
      }
    }
    fs.writeFileSync(path.join(outdir, "resume-geometry.json"), JSON.stringify({
      browser: browser.version(), results,
    }, null, 2) + "\n");
  } finally {
    await browser.close();
  }
})().catch(error => {
  console.error(error);
  process.exitCode = 1;
});
