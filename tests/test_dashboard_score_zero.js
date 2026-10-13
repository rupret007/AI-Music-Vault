"use strict";

// Run the real template and committed rendering code offline, without a browser.
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const { test } = require("node:test");
const root = path.resolve(__dirname, "..");
const html = fs.readFileSync(path.join(root, "Jeff Story Song Vault Dashboard.html"), "utf8");
const liveRows = JSON.parse(html.match(/const DATA = (.*);/)[1]);
const api = JSON.parse(fs.readFileSync(path.join(root, "data/app_api.json"), "utf8"));
const fixture = [
  { id: "ZERO", pot: 0, rdy: 0, mom: 0 },
  { id: "MAX", pot: 100, rdy: 100, mom: 100 },
  { id: "NULL", pot: null, rdy: null, mom: null },
  { id: "ABSENT" },
  { id: "BLANK", pot: "", rdy: "", mom: "" },
  { id: "OTHER", pot: null, rdy: 80, mom: 90 },
].map(row => ({ t: "Test song", p: "Test project", st: "Draft", nx: "Write chorus", ...row }));

for (const surface of ["scripts/build_dashboard.py", "Jeff Story Song Vault Dashboard.html"]) {
  const text = fs.readFileSync(path.join(root, surface), "utf8");
  const script = text.split("<script>")[1].split("</script>")[0];
  const functions = script.slice(script.indexOf("function esc("), script.indexOf("list.addEventListener('click'"));
  const stats = script.slice(script.indexOf("const scoredCount="), script.indexOf("function workKindLabel("));

  function context(rows = fixture) {
    const elements = { stats: {}, statsLine: {} };
    const fields = Object.fromEntries(["q", "proj", "scored", "scope", "evidence", "work", "logicReady"]
      .map(name => [name, { value: "" }]));
    const ctx = vm.createContext({
      ...fields, DATA: rows, TX: [], LOGIC_READY: { next: {}, label: {}, pill: {}, formats: {} },
      memoEvidenceBySong: {}, memoCountBySong: {}, activeWorkSongId: "",
      sort: { value: "id" }, list: {}, songResults: {}, clearSongFilters: {},
      document: { getElementById: id => elements[id] },
      RECOVERED_COUNT: 0, COVER_COUNT: 0, TX_MATCHED_TOTAL: 0, TX_SEARCHABLE_TOTAL: 0, TX_TOTAL: 0,
    });
    vm.runInContext(functions, ctx);
    vm.runInContext("updateWorkSessionState = () => {};", ctx);
    vm.runInContext(stats, ctx);
    ctx.elements = elements;
    return ctx;
  }

  test(`${surface}: scored stat includes zero and ignores missing`, () => {
    const ctx = context();
    assert.match(ctx.elements.statsLine.textContent, /6 songs · 2 scored ·/);
    assert.match(ctx.elements.stats.innerHTML, /<b>2<\/b><span>scored<\/span>/);
    const live = context(liveRows);
    assert.equal(api.counts.scored, 59);
    assert.equal(vm.runInContext("scoredCount", live), api.counts.scored);
    const changed = liveRows.map(row => ({ ...row }));
    changed.find(row => row.pot == null).pot = 0;
    assert.equal(vm.runInContext("scoredCount", context(changed)), 60);
  });

  test(`${surface}: scored/unscored filters partition rows including zero`, () => {
    const ctx = context();
    const ids = () => [...ctx.list.innerHTML.matchAll(/class="row" data-song-id="([^"]+)"/g)]
      .map(match => match[1]).sort();
    ctx.scored.value = "1";
    ctx.render();
    assert.deepEqual(ids(), ["MAX", "ZERO"]);
    ctx.scored.value = "0";
    ctx.render();
    assert.deepEqual(ids(), ["ABSENT", "BLANK", "NULL", "OTHER"]);
    ctx.scored.value = "";
    ctx.render();
    assert.equal(ids().length, 6);
  });

  test(`${surface}: zero bars have zero width and a visible zero`, () => {
    const ctx = context();
    for (const color of ["pot", "rdy", "mom"]) {
      assert.match(ctx.bar(0, color), /width:0%;/);
      assert.match(ctx.bar(0, color), /class="bar-n">0<\/span>/);
      assert.doesNotMatch(ctx.bar(0, color), /—/);
      assert.match(ctx.bar(100, color), /width:100%;/);
      for (const missing of [null, undefined, "", "   "]) {
        assert.match(ctx.bar(missing, color), /—/);
        assert.doesNotMatch(ctx.bar(missing, color), /class="bar-n"/);
      }
    }
  });

  test(`${surface}: rendered rows announce all zero scores accurately`, () => {
    const ctx = context();
    ctx.scored.value = "1";
    ctx.render();
    assert.match(ctx.list.innerHTML, /aria-label="Test song ZERO\. Potential 0, readiness 0, momentum 0"/);
    assert.equal((ctx.list.innerHTML.match(/class="bar-n">0<\/span>/g) || []).length, 3);
    assert.match(ctx.list.innerHTML, /<span class="pill">momentum 0<\/span>/);
    ctx.scored.value = "0";
    ctx.render();
    for (const id of ["NULL", "ABSENT", "BLANK"]) {
      assert.ok(ctx.list.innerHTML.includes(`aria-label="Test song ${id}. Potential unscored, readiness unscored, momentum unscored"`));
    }
    assert.equal((ctx.list.innerHTML.match(/>—<\/span>/g) || []).length, 10);
  });
}
