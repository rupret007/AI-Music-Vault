"use strict";

// Exercise the real rendering, queue, and storage functions with synthetic rows.
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const { test } = require("node:test");
const root = path.resolve(__dirname, "..");

function element() {
  return {
    value: "", hidden: true, disabled: false, textContent: "", dataset: {},
    attributes: {}, setAttribute(name, value) { this.attributes[name] = value; },
    focus() {}, scrollIntoView() {},
  };
}

function fixture(script) {
  const rows = [
    { id: "A", t: "Alpha", p: "North", mom: 90, pot: 80, scope: "live", lr: "ready" },
    { id: "B", t: "Beta", p: "South", mom: 80, pot: null, scope: "archive", lr: "other" },
    { id: "C", t: "Gamma", p: "North", mom: 70, pot: 60, scope: "live", lr: "ready" },
    { id: "D", t: "Delta", p: "South", mom: 60, nx: "Record lead guitar" },
  ].map(row => ({ nx: "Confirm the chorus lines", st: "Draft", ...row }));
  const fields = Object.fromEntries([
    "q", "proj", "sort", "scored", "scope", "evidence", "work", "logicReady",
    "songResults", "clearSongFilters", "workSession", "workSessionText", "workSessionNext",
    "workSessionLogic", "workSessionAssets", "workSessionEvidence", "copyWorkNext", "copyWorkLogic",
    "openWorkEvidence", "workPrev", "workNext", "resumeWork", "resumeWorkText", "resumeWorkButton",
    "resumeWorkNext", "copyResumeNext", "resumeWorkStatus", "resumeWorkLogic", "copyResumeLogic",
  ].map(name => [name, element()]));
  fields.sort.value = "mom";
  const memory = new Map();
  const storage = {
    getItem: key => memory.get(key) || null,
    setItem: (key, value) => memory.set(key, value),
    removeItem: key => memory.delete(key),
  };
  const list = {
    rows: [],
    set innerHTML(html) {
      this.rows = [...html.matchAll(/class="row" data-song-id="([^"]+)"/g)].map(([, id]) => {
        const head = element(), detail = element();
        detail.classList = { contains: name => name === "detail" };
        const row = { dataset: { songId: id }, head,
          querySelector: selector => selector === ".detail" ? detail : head };
        head.closest = () => row;
        return row;
      });
    },
    querySelectorAll(selector) {
      if (selector === "[data-song-id]") return this.rows;
      if (selector === '[data-toggle-song][aria-expanded="true"]') {
        return this.rows.map(row => row.head).filter(head => head.attributes["aria-expanded"] === "true");
      }
      return [];
    },
  };
  const ctx = vm.createContext({
    ...fields, list, DATA: rows, TX: [], sname: Object.fromEntries(rows.map(row => [row.id, row.t])),
    LOGIC_READY: { next: { ready: "Review in Logic", other: "Check the arrangement" }, formats: {} },
    memoEvidenceBySong: { A: { n: 1 }, B: { n: 1 } }, memoCountBySong: { A: 1, B: 1 },
    visibleSongIds: [], activeWorkSongId: "", lastWorkKind: "", songSearchCursor: -1,
    WORK_SESSION_KEY: "test-session", window: { localStorage: storage },
    requestAnimationFrame: callback => callback(), showTab() {},
  });
  vm.runInContext(script.slice(script.indexOf("function workKindLabel("), script.indexOf("workStarts.innerHTML=")), ctx);
  vm.runInContext(script.slice(script.indexOf("function esc("), script.indexOf("list.addEventListener('click'")), ctx);
  ctx.saved = () => JSON.parse(memory.get("test-session") || "null");
  ctx.openWork("write");
  ctx.stepWork(1);
  assert.equal(ctx.activeWorkSongId, "B", "start on a non-first work item");
  return ctx;
}

for (const surface of ["scripts/build_dashboard.py", "Jeff Story Song Vault Dashboard.html"]) {
  const text = fs.readFileSync(path.join(root, surface), "utf8");
  const script = text.split("<script>")[1].split("</script>")[0];

  for (const [field, value] of [["q", "Alpha"], ["proj", "North"], ["scored", "1"],
    ["scope", "live"], ["evidence", "0"], ["logicReady", "ready"]]) {
    test(`${surface}: ${field} hides the selected song without replacing Resume`, () => {
      const ctx = fixture(script);
      ctx[field].value = value;
      ctx.render();
      assert.equal(ctx.activeWorkSongId, "B", "filtering must not select another song");
      assert.deepEqual(ctx.saved(), { v: 1, kind: "write", id: "B" });
      assert.ok(ctx.visibleSongIds.length > 0 && !ctx.visibleSongIds.includes("B"));
      for (const button of [ctx.copyWorkNext, ctx.copyWorkLogic, ctx.openWorkEvidence]) {
        assert.equal(button.hidden, true, "hidden selection cannot offer an unrelated action");
        assert.equal(button.disabled, true);
        assert.equal(button.dataset.songId, "");
      }
      assert.equal(ctx.workSessionNext.textContent, "");
      assert.equal(ctx.workSessionLogic.textContent, "");
      assert.match(ctx.workSessionText.textContent, /hidden by filters/);
      assert.equal(ctx.copyResumeNext.dataset.songId, "B", "Resume still offers the saved next step");
      assert.equal(ctx.workPrev.disabled, true);
      assert.equal(ctx.workNext.disabled, false);
      ctx[field].value = "";
      ctx.render();
      assert.equal(ctx.activeWorkSongId, "B");
      assert.equal(ctx.saved().id, "B");
      assert.equal(ctx.copyWorkNext.dataset.songId, "B");
      assert.match(ctx.workSessionText.textContent, /2 of 3 · Beta/);
    });
  }

  test(`${surface}: no matches, sorting, and clearing the query preserve the exact song`, () => {
    const ctx = fixture(script);
    ctx.q.value = "no matching title";
    ctx.render();
    assert.equal(ctx.visibleSongIds.length, 0);
    assert.equal(ctx.activeWorkSongId, "B");
    assert.equal(ctx.saved().id, "B");
    assert.equal(ctx.workNext.disabled, true);
    assert.equal(ctx.workPrev.disabled, true);
    assert.equal(ctx.stepWork(1), false);
    ctx.sort.value = "t";
    ctx.render();
    ctx.q.value = "";
    ctx.render();
    assert.equal(ctx.activeWorkSongId, "B");
    assert.equal(ctx.saved().id, "B");
    assert.equal(ctx.copyWorkNext.dataset.songId, "B");
  });

  for (const choose of ["next", "enter"]) {
    test(`${surface}: explicit ${choose} can replace a filtered-out selection`, () => {
      const ctx = fixture(script);
      ctx.q.value = "Alpha";
      ctx.render();
      assert.equal(ctx.saved().id, "B");
      const selected = choose === "next" ? ctx.stepWork(1)
        : ctx.handleSongSearchKey({ key: "Enter", preventDefault() {} });
      assert.equal(selected, true);
      assert.equal(ctx.activeWorkSongId, "A");
      assert.equal(ctx.saved().id, "A");
      assert.equal(ctx.copyWorkNext.dataset.songId, "A");
    });
  }

  test(`${surface}: Resume restores the hidden song and explicit starts reset the queue`, () => {
    const ctx = fixture(script);
    ctx.proj.value = "North";
    ctx.render();
    assert.equal(ctx.resumeLastWorkSession(), true);
    assert.equal(ctx.proj.value, "");
    assert.equal(ctx.activeWorkSongId, "B");
    ctx.openWork("write");
    assert.equal(ctx.activeWorkSongId, "A");
    ctx.openWork("produce");
    assert.equal(ctx.activeWorkSongId, "D");
    assert.deepEqual(ctx.saved(), { v: 1, kind: "produce", id: "D" });
  });

  test(`${surface}: blocked storage still preserves the active in-memory selection`, () => {
    const ctx = fixture(script);
    ctx.window.localStorage = {
      getItem() { throw new Error("blocked"); }, setItem() { throw new Error("blocked"); },
    };
    ctx.q.value = "Alpha";
    ctx.render();
    assert.equal(ctx.activeWorkSongId, "B");
    ctx.q.value = "no matches";
    ctx.render();
    ctx.q.value = "";
    ctx.render();
    assert.equal(ctx.activeWorkSongId, "B");
    assert.equal(ctx.copyWorkNext.dataset.songId, "B");
    assert.equal(ctx.resumeWork.hidden, true);
  });
}
