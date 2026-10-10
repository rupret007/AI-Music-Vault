#!/usr/bin/env node
"use strict";

// Resume must lead in reading/tab order as well as on the screen.
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const html = fs.readFileSync(path.join(__dirname, "..", "Jeff Story Song Vault Dashboard.html"), "utf8");
const script = html.split("<script>")[1].split("</script>")[0];
const resume = html.match(/<section[^>]*id="resumeWork"[^>]*>([\s\S]*?)<\/section>/);
assert.ok(resume, "Resume needs its own section before catalog details and new sessions");
assert.ok(html.indexOf("</h1>") < resume.index);
assert.ok(resume.index < html.indexOf('id="catalogOverview"'));
assert.ok(resume.index < html.indexOf('id="workStarts"'));
assert.match(resume[0], /aria-labelledby="resumeWorkButton"/);
assert.match(resume[1], /<h2>[\s\S]*id="resumeWorkButton"[\s\S]*<\/h2>/);
assert.ok(resume[1].indexOf('id="resumeWorkNext"') < resume[1].indexOf('id="copyResumeNext"'));
assert.ok(resume[1].indexOf('id="copyResumeNext"') < resume[1].indexOf('id="forgetWorkSession"'));
assert.ok(resume[1].indexOf('id="forgetWorkSession"') < resume[1].indexOf('id="resumeWorkLogic"'));
assert.match(resume[1], /<details class="resume-details"><summary>Logic-ready next and session details<\/summary>/);
assert.match(resume[1], /WAVs\/AIFF\/MIDI preference/);
const overview = html.match(/<details[^>]*id="catalogOverview"[^>]*>([\s\S]*?)<\/details>/);
assert.ok(overview, "Subtitle and counts must remain available in native disclosure");
assert.match(overview[1], /<summary[^>]*id="catalogOverviewSummary"/);
assert.match(overview[1], /class="sub"/);
assert.match(overview[1], /id="stats"/);
assert.match(overview[1], /no audio in this repo/);
assert.match(overview[1], /catalog rows are not the live set/);

function extractFunction(name) {
  const start = script.indexOf("function " + name + "(");
  assert.ok(start >= 0, "Missing function " + name);
  let depth = 0;
  for (let i = script.indexOf("{", start); i < script.length; i++) {
    if (script[i] === "{") depth++;
    if (script[i] === "}" && --depth === 0) return script.slice(start, i + 1);
  }
  assert.fail("Unclosed function " + name);
}
const element = () => ({ hidden: false, textContent: "", dataset: {}, setAttribute() {} });
const memory = new Map();
const storage = {
  getItem: key => memory.get(key) || null,
  setItem: (key, value) => memory.set(key, value),
  removeItem: key => memory.delete(key),
};
let focused = false;
const context = vm.createContext({
  WORK_SESSION_KEY: "resume-test",
  window: { localStorage: storage },
  DATA: [{ id: "TEST-1", nx: "Confirm the chorus lines" }],
  sname: { "TEST-1": "Test Song" },
  resumeWork: element(), resumeWorkHint: element(), resumeWorkText: element(),
  resumeWorkButton: element(), resumeWorkNext: element(), copyResumeNext: element(),
  resumeWorkStatus: element(),
  catalogOverview: { open: true }, catalogOverviewSummary: { hidden: true },
  workStarts: { querySelector: () => ({ focus() { focused = true; } }) },
});
for (const name of ["songWorkKind", "parseStoredWorkSession", "readStoredWorkSession", "storeWorkSession",
  "clearStoredWorkSession", "vaultStorage", "announceWorkSession", "forgetWorkSessionResult",
  "flattenWorkField", "stripPrivateLocators", "workCardLeaks", "nextStepIsIncomplete", "safeWorkNextStep",
  "updateResumeWork", "forgetLastWorkSession"]) {
  vm.runInContext(extractFunction(name), context);
}
context.updateResumeWork();
assert.equal(context.resumeWork.hidden, true);
assert.equal(context.catalogOverview.open, true);
assert.equal(context.catalogOverviewSummary.hidden, true);
assert.equal(context.storeWorkSession(storage, "write", "TEST-1", context.sname, context.DATA), true);
assert.deepEqual(Object.keys(JSON.parse(memory.get("resume-test"))).sort(), ["id", "kind", "v"]);
context.updateResumeWork();
assert.equal(context.resumeWork.hidden, false);
assert.equal(context.resumeWorkText.textContent, "Write · Test Song");
assert.equal(context.resumeWorkNext.hidden, false);
assert.equal(context.resumeWorkNext.textContent, "Do this now: Confirm the chorus lines");
assert.equal(context.copyResumeNext.hidden, false);
assert.equal(context.copyResumeNext.disabled, false);
assert.equal(context.copyResumeNext.dataset.songId, "TEST-1");
assert.equal(context.catalogOverview.open, false, "Saved session must collapse subtitle and counts");
assert.equal(context.catalogOverviewSummary.hidden, false, "Counts must still be discoverable");
// Explicitly opening the details must survive a refresh of the resume text.
context.catalogOverview.open = true;
context.updateResumeWork();
assert.equal(context.catalogOverview.open, true);
// A valid session with an unsafe next step must clear previously visible copy.
context.DATA[0].nx = "Confirm the chorus lines file:///private/demo.wav";
context.updateResumeWork();
assert.equal(context.resumeWorkNext.textContent, "Do this now: Confirm the chorus lines");
context.DATA[0].nx = "Listen: Crescent Dr 21.";
assert.equal(context.storeWorkSession(storage, "listen", "TEST-1", context.sname, context.DATA), true);
context.updateResumeWork();
assert.equal(context.resumeWork.hidden, false);
assert.equal(context.resumeWorkNext.hidden, true);
assert.equal(context.resumeWorkNext.textContent, "");
assert.equal(context.copyResumeNext.hidden, true);
assert.equal(context.copyResumeNext.disabled, true);
assert.equal(context.copyResumeNext.dataset.songId, "");
assert.equal(context.forgetLastWorkSession(), true);
assert.equal(memory.size, 0);
assert.equal(context.resumeWork.hidden, true);
assert.equal(context.catalogOverview.open, true);
assert.equal(context.catalogOverviewSummary.hidden, true);
assert.equal(focused, true, "Forget must move keyboard focus to a visible start choice");
assert.equal(context.resumeWorkStatus.textContent, "Forgot this browser record.");
context.DATA[0].nx = "Confirm the chorus lines";
for (const raw of ['{"v":1,"kind":"write","id":"missing"}',
  '{"v":1,"kind":"write","id":"TEST-1","title":"extra"}', "bad JSON"]) {
  memory.set("resume-test", raw);
  context.updateResumeWork();
  assert.equal(context.resumeWork.hidden, true);
  assert.equal(context.catalogOverview.open, true);
  assert.equal(memory.size, 0);
}
context.window.localStorage = { getItem() { throw new Error("blocked"); } };
context.updateResumeWork();
assert.equal(context.resumeWork.hidden, true);
assert.equal(context.catalogOverview.open, true);
console.log("dashboard resume first-screen checks OK");
