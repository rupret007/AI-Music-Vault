#!/usr/bin/env node
"use strict";

const fs = require("fs");
const path = require("path");

const root = path.resolve(__dirname, "..");
const html = fs.readFileSync(path.join(root, "Jeff Story Song Vault Dashboard.html"), "utf8");
const script = html.split("<script>")[1].split("</script>")[0];

function fail(message) {
  throw new Error(message);
}

function extractFunction(source, name) {
  const start = source.indexOf("function " + name + "(");
  if (start < 0) fail("missing function " + name);
  let cursor = source.indexOf("{", start);
  let depth = 0;
  for (; cursor < source.length; cursor += 1) {
    if (source[cursor] === "{") depth += 1;
    if (source[cursor] === "}") {
      depth -= 1;
      if (depth === 0) return source.slice(start, cursor + 1);
    }
  }
  fail("unclosed function " + name);
}

// Compile the whole generated program without running its browser side effects.
new Function(script);

for (const marker of [
  "data-open-memos",
  "data-open-song",
  "data-toggle-song",
  "data-copy-file",
  "function openSong(",
  "function openSongMemos(",
  "function memoMatches(",
  "function parseVaultHash(",
  "function sortMemoHits(",
  "function handleVaultKey(",
  "function normalizeSearch(",
  "function songAliases(",
  "function songSearchHit(",
  "function markNormalized(",
  "function sortSongRows(",
  "function focusFoundSong(",
  "function handleSongSearchKey(",
  "closest name first",
  "titles, aliases, hooks",
  "scrollIntoView({block:'center'})",
  "function copyMemoFile(",
  "function copyVaultText(",
  "function songWorkKind(",
  "function buildSongWorkCard(",
  "function copySongWork(",
  "function safeWorkNextStep(",
  "function nextStepIsIncomplete(",
  "function copyCurrentWorkNext(",
  "function reviewCurrentWorkEvidence(",
  "function allowedExactWorkSongId(",
  "function copyExactSongNextStep(",
  "function copyResumeWorkNext(",
  "safeWorkNextStep(d)",
  "function openWork(",
  "function updateWorkSessionState(",
  "function parseStoredWorkSession(",
  "function readStoredWorkSession(",
  "function storeWorkSession(",
  "function clearStoredWorkSession(",
  "function resumeLastWorkSession(",
  "function applyWorkHash(",
  "function forgetWorkSessionResult(",
  "function announceWorkSession(",
  "id=\"resumeWorkHint\"",
  "id=\"resumeWorkStatus\"",
  "aria-live=\"polite\"",
  "function latestMemoForSong(",
  "function stepWork(",
  "id=\"evidence\"",
  "id=\"work\"",
  "id=\"workSession\"",
  "id=\"workSessionNext\"",
  "id=\"copyWorkNext\"",
  "id=\"openWorkEvidence\"",
  "id=\"resumeWorkNext\"",
  "id=\"copyResumeNext\"",
  "id=\"workStarts\"",
  "id=\"resumeWork\"",
  "id=\"resumeWorkButton\"",
  "id=\"forgetWorkSession\"",
  "id=\"advancedFilters\"",
  "Start a work session",
  "More filters",
  "Sit-down",
  "data-open-work=",
  "data-work-step",
  "Sort: Latest memo evidence",
  "Copy intake name",
  "Copy work card",
  "newest first",
  "data-copy-work",
  "this page does not open audio",
  "aria-selected",
  "aria-expanded",
]) {
  if (!html.includes(marker)) fail("missing navigation marker " + marker);
}
if (html.includes("onclick=")) fail("generated dashboard must use delegated events, not inline clicks");
if (html.includes("<audio")) fail("generated dashboard must not open audio");
if (html.includes("Latest source (auto-resolved)") || html.includes("<h4>Known assets</h4>")) {
  fail("generated dashboard must not display owner-audio locators");
}

const names = { "JS-0001": "First Song", "JS-0002": "Second Song" };
const memoMatches = new Function(
  "sname",
  "return (" + extractFunction(script, "memoMatches") + ");",
)(names);
const memo = { s: "JS-0001", n: "Phone idea", x: "a lyric fragment lives here" };
if (!memoMatches(memo, "", "JS-0001")) fail("song scope must show every linked memo");
if (memoMatches(memo, "", "JS-0002")) fail("song scope must reject a different song");
if (!memoMatches(memo, "fragment", "")) fail("global search must match transcript text");
if (!memoMatches(memo, "phone", "")) fail("global search must match memo title");
if (!memoMatches(memo, "first song", "")) fail("global search must match linked catalog title");
if (memoMatches(memo, "missing", "")) fail("unmatched terms must stay out");

const memoUi = { value: "old", focused: false, focus() { this.focused = true; } };
const memoCalls = [];
const memoNavigation = new Function(
  "sname",
  "memoCountBySong",
  "mq",
  "showTab",
  "mrender",
  "let activeMemoSong = ''; const openSongMemos = " +
    extractFunction(script, "openSongMemos") +
    "; return { openSongMemos, active: () => activeMemoSong };",
)(names, { "JS-0001": 2 }, memoUi, (tab) => memoCalls.push(tab), () => memoCalls.push("render"));
memoNavigation.openSongMemos("JS-0001");
if (memoNavigation.active() !== "JS-0001" || memoUi.value !== "" || !memoUi.focused) {
  fail("song to memo navigation must establish an exact scoped search");
}
if (memoCalls.join(",") !== "M,render") fail("song to memo navigation must open and paint Memo Search");
memoNavigation.openSongMemos("JS-0002");
if (memoNavigation.active() !== "JS-0001") fail("song without indexed memos must not replace the scope");

const fields = {
  q: { value: "old" }, proj: { value: "old" }, scored: { value: "old" },
  scope: { value: "old" }, sort: { value: "mom" },
};
const headUi = {
  focused: false,
  scrolled: false,
  focus() { this.focused = true; },
  scrollIntoView() { this.scrolled = true; },
};
const songCalls = [];
const list = {
  querySelectorAll: () => [{
    dataset: { songId: "JS-0001" },
    querySelector: () => headUi,
  }],
};
const openSong = new Function(
  "sname", "q", "proj", "scored", "scope", "sort", "showTab", "render",
  "requestAnimationFrame", "list", "toggleSong",
  "return (" + extractFunction(script, "openSong") + ");",
)(
  names, fields.q, fields.proj, fields.scored, fields.scope, fields.sort,
  (tab) => songCalls.push(tab), () => songCalls.push("render"), (callback) => callback(), list,
  (head, force) => songCalls.push(head === headUi && force === true ? "expanded" : "bad-expand"),
);
openSong("JS-0001");
if (fields.q.value !== "JS-0001" || fields.proj.value || fields.scored.value || fields.scope.value) {
  fail("memo to song navigation must isolate the exact catalog record");
}
if (fields.sort.value !== "id" || songCalls.join(",") !== "S,render,expanded") {
  fail("memo to song navigation must paint and expand the Songs view");
}
if (!headUi.focused || !headUi.scrolled) fail("opened song must receive focus and enter view");

const toggleSong = new Function(
  "return (" + extractFunction(script, "toggleSong") + ");",
)();
const detail = { hidden: true, classList: { contains: (name) => name === "detail" } };
const attrs = {};
const head = {
  nextElementSibling: detail,
  setAttribute: (name, value) => { attrs[name] = value; },
};
toggleSong(head);
if (detail.hidden || attrs["aria-expanded"] !== "true") fail("closed song must open honestly");
toggleSong(head);
if (!detail.hidden || attrs["aria-expanded"] !== "false") fail("open song must close honestly");
toggleSong(head, true);
if (detail.hidden || attrs["aria-expanded"] !== "true") fail("force-open must expand a song");
toggleSong(head, false);
if (!detail.hidden || attrs["aria-expanded"] !== "false") fail("force-close must collapse a song");

const parseVaultHash = new Function(
  "return (" + extractFunction(script, "parseVaultHash") + ");",
)();
if (!parseVaultHash("#memos=JS-0001", names) || parseVaultHash("#memos=JS-0001", names).kind !== "memos") {
  fail("hash must accept a known memo scope");
}
if (parseVaultHash("#memos=JS-9999", names)) fail("hash must reject unknown ids");
if (parseVaultHash("#open=JS-0001", names)) fail("hash must reject other kinds");
if (parseVaultHash("#memos=JS-0001<script>", names)) fail("hash must reject injected ids");
if (!parseVaultHash("#work=write", names) || parseVaultHash("#work=write", names).kind !== "work") {
  fail("hash must accept a known work kind");
}
if (parseVaultHash("#work=unknown", names)) fail("hash must reject unknown work");
if (parseVaultHash("#work=JS-0001", names)) fail("hash must reject a catalog id as work");

const sortMemoHits = new Function(
  "return (" + extractFunction(script, "sortMemoHits") + ");",
)();
const ordered = sortMemoHits([
  { m: { d: "2020-01-01", f: "old.m4a" } },
  { m: { d: "2024-12-01", f: "new.m4a" } },
  { m: { d: "", f: "z-empty.m4a" } },
]);
if (ordered[0].m.f !== "new.m4a") fail("newest memo must come first");
if (ordered[2].m.d !== "") fail("undated memo must sink");

const esc = new Function("return (" + extractFunction(script, "esc") + ");")();
const markHay = new Function(
  "esc",
  "return (" + extractFunction(script, "markHay") + ");",
)(esc);
if (markHay("Hello Garden", "garden") !== "Hello <mark>Garden</mark>") {
  fail("title match must highlight without changing catalog feel");
}
if (markHay("<x>", "x") !== "&lt;<mark>x</mark>&gt;") fail("markHay must escape");
if (!extractFunction(script, "copyVaultText").includes("execCommand")) {
  fail("copy must fall back when the clipboard API is blocked");
}
if (!extractFunction(script, "copyMemoFile").includes("copyVaultText")) {
  fail("intake-name copy must reuse the shared clipboard helper");
}
const safeIntakeName = new Function(
  "return (" + extractFunction(script, "safeIntakeName") + ");",
)();
if (safeIntakeName("file:///Users/jeff/Voice Memos/Raw Take 1.m4a?download=1") !== "Raw Take 1.m4a") {
  fail("intake-name sanitizing must keep only the copy-safe basename");
}
if (safeIntakeName("(unknown intake)") !== "" || safeIntakeName("unknown intake") !== "") {
  fail("placeholder intake labels must not become copyable values");
}
if (safeIntakeName("file:///Users/jeff/Voice Memos/private-mix.wav") !== "") {
  fail("intake-name sanitizing must fail closed for owner-audio WAV basenames");
}
if (safeIntakeName("proof.aiff") !== "" || safeIntakeName("line.mid") !== "") {
  fail("intake-name sanitizing must fail closed for AIFF and MIDI basenames");
}
const copyMemoFile = new Function(
  "safeIntakeName",
  "copyVaultText",
  "return (" + extractFunction(script, "copyMemoFile") + ");",
)(safeIntakeName, (value) => !!value);
if (copyMemoFile("(unknown intake)", null)) {
  fail("copy intake name must fail closed when the memo row has no safe intake basename");
}
if (copyMemoFile("file:///tmp/private.logicx", null)) {
  fail("copy intake name must fail closed for owner Logic project basenames");
}
if (!copyMemoFile("file:///tmp/Clip.m4a", null)) {
  fail("copy intake name must still work for a sanitized real memo intake filename");
}

const songWorkKind = new Function(
  "return (" + extractFunction(script, "songWorkKind") + ");",
)();

const parseStoredWorkSession = new Function(
  "songWorkKind",
  "return (" + extractFunction(script, "parseStoredWorkSession") + ");",
)(songWorkKind);
const storedNames = { "JS-0001": "First Song", "JS-0002": "Second Song" };
const storedRows = [
  { id: "JS-0001", nx: "Jeff: confirm the 2 unclear chorus lines by ear" },
  { id: "JS-0002", nx: "Record lead guitar over choruses" },
];
const parsedSession = parseStoredWorkSession(
  JSON.stringify({ v: 1, kind: "write", id: "JS-0001" }),
  storedNames,
  storedRows,
);
if (!parsedSession || parsedSession.id !== "JS-0001" || parsedSession.kind !== "write") {
  fail("stored work session must accept one matching catalog id and work kind");
}
if (parseStoredWorkSession('{"v":1,"kind":"write","id":"JS-9999"}', storedNames, storedRows)) {
  fail("stored work session must reject an unknown catalog id");
}
if (parseStoredWorkSession('{"v":1,"kind":"listen","id":"JS-0001"}', storedNames, storedRows)) {
  fail("stored work session must reject a kind that no longer matches the catalog next action");
}
if (parseStoredWorkSession(
  '{"v":1,"kind":"write","id":"JS-0001","note":"private mix.wav"}',
  storedNames,
  storedRows,
)) {
  fail("stored work session must reject extra fields rather than retaining private text");
}

const storageKeyMatch = script.match(/const WORK_SESSION_KEY='([^']+)'/);
if (!storageKeyMatch) fail("missing versioned work-session storage key");
const storageKey = storageKeyMatch[1];
const readStoredWorkSession = new Function(
  "WORK_SESSION_KEY",
  "parseStoredWorkSession",
  "return (" + extractFunction(script, "readStoredWorkSession") + ");",
)(storageKey, parseStoredWorkSession);
const storeWorkSession = new Function(
  "WORK_SESSION_KEY",
  "parseStoredWorkSession",
  "return (" + extractFunction(script, "storeWorkSession") + ");",
)(storageKey, parseStoredWorkSession);
const clearStoredWorkSession = new Function(
  "WORK_SESSION_KEY",
  "return (" + extractFunction(script, "clearStoredWorkSession") + ");",
)(storageKey);
const memory = new Map();
const storage = {
  getItem(key) { return memory.has(key) ? memory.get(key) : null; },
  setItem(key, value) { memory.set(key, value); },
  removeItem(key) { memory.delete(key); },
};
if (!storeWorkSession(storage, "write", "JS-0001", storedNames, storedRows)) {
  fail("valid work session must be saved");
}
const storedPayload = JSON.parse(memory.get(storageKey));
if (Object.keys(storedPayload).sort().join("|") !== "id|kind|v") {
  fail("saved work session must contain only version, work kind, and catalog id");
}
if (!readStoredWorkSession(storage, storedNames, storedRows)) {
  fail("valid saved work session must be readable");
}
memory.set(
  storageKey,
  JSON.stringify({ v: 1, kind: "write", id: "JS-0001", path: "private.logicx" }),
);
if (readStoredWorkSession(storage, storedNames, storedRows) || memory.has(storageKey)) {
  fail("extra-field storage must fail closed and be cleared");
}
const blockedStorage = {
  getItem() { throw new Error("blocked"); },
  setItem() { throw new Error("blocked"); },
  removeItem() { throw new Error("blocked"); },
};
if (readStoredWorkSession(blockedStorage, storedNames, storedRows) !== null) {
  fail("unavailable browser storage must fail soft on read");
}
if (storeWorkSession(blockedStorage, "write", "JS-0001", storedNames, storedRows)) {
  fail("unavailable browser storage must fail soft on write");
}
if (clearStoredWorkSession(blockedStorage)) {
  fail("unavailable browser storage must fail soft on clear");
}
if (songWorkKind("Jeff: confirm the 2 unclear chorus lines by ear (60s)") !== "write") {
  fail("chorus-line next action must classify as write");
}
if (songWorkKind("Record lead guitar over choruses + solos (the one finishing overdub).") !== "produce") {
  fail("overdub next action must classify as produce");
}
if (songWorkKind("Listen to latest (take.logicx) and rate: finish / rest.") !== "listen") {
  fail("listen-to-latest next action must classify as listen");
}
if (songWorkKind("") !== "unknown") fail("empty next action must stay unknown");

const stripPrivateLocators = new Function(
  "return (" + extractFunction(script, "stripPrivateLocators") + ");",
)();
if (stripPrivateLocators("Listen to latest (mix.wav) and rate") !== "Listen to latest and rate") {
  fail("work preview must strip owner-audio filenames");
}
if (stripPrivateLocators("LISTEN: play Maxwell Dr 99 (latest take). Verdict.") !== "LISTEN: play. Verdict.") {
  fail("work preview must strip known street fragments");
}
const workCardLeaks = new Function(
  "return (" + extractFunction(script, "workCardLeaks") + ");",
)();
const nextStepIsIncomplete = new Function(
  "return (" + extractFunction(script, "nextStepIsIncomplete") + ");",
)();
const safeWorkNextStep = new Function(
  "flattenWorkField",
  "stripPrivateLocators",
  "workCardLeaks",
  "nextStepIsIncomplete",
  "return (" + extractFunction(script, "safeWorkNextStep") + ");",
)(
  new Function("return (" + extractFunction(script, "flattenWorkField") + ");")(),
  stripPrivateLocators,
  workCardLeaks,
  nextStepIsIncomplete,
);
if (safeWorkNextStep({ nx: "Listen to latest (mix.wav) and rate: finish / rest." }) !== "Listen to latest and rate: finish / rest.") {
  fail("session next step must reuse sanitized catalog action text");
}
if (safeWorkNextStep(null) !== "" || safeWorkNextStep({ nx: "" }) !== "") {
  fail("session next step must fail closed without a usable catalog action");
}
if (safeWorkNextStep({ nx: "Open mix.wav" }) !== "") {
  fail("session next step must fail closed when sanitizing leaves only an incomplete verb");
}
if (safeWorkNextStep({ nx: "LISTEN: Crescent Dr 21." }) !== "") {
  fail("session next step must fail closed when a leftover listen verb is all that remains");
}

const buildSongWorkCard = new Function(
  "flattenWorkField",
  "songWorkKind",
  "stripPrivateLocators",
  "workCardLeaks",
  "safeWorkNextStep",
  "return (" + extractFunction(script, "buildSongWorkCard") + ");",
)(
  new Function("return (" + extractFunction(script, "flattenWorkField") + ");")(),
  songWorkKind,
  stripPrivateLocators,
  workCardLeaks,
  safeWorkNextStep,
);
const card = buildSongWorkCard({
  id: "JS-0128",
  t: "It's Alright",
  nx: "Jeff: confirm the 2 unclear chorus lines by ear (60s)",
  hk: "I know it's alright",
  oq: ["noisy and Something Dirty?"],
  src: ["take.wav"],
  bs: "file:///tmp/take.wav",
});
if (!card.includes("It's Alright (JS-0128)") || !card.includes("Work: write") || !card.includes("Hook: I know it's alright")) {
  fail("work card must carry title, write kind, and hook");
}
if (card.includes(".wav") || card.includes("file://") || card.includes("Maxwell")) {
  fail("work card must omit owner-audio locators and sources");
}
if (buildSongWorkCard({ id: "JS-9999", t: "Leak", nx: "do it", key: "open mix.wav" }) !== "") {
  fail("work card must fail closed when a locator remains");
}
const memoCard = buildSongWorkCard(
  { id: "JS-0128", t: "It's Alright", nx: "Jeff: confirm the 2 unclear chorus lines by ear (60s)" },
  { n: 3, last: "2025-10-14", f: "take.wav" },
);
if (!memoCard.includes("Memos: 3 searchable · latest 2025-10-14")) {
  fail("work card may include memo count and date");
}
if (memoCard.includes("take.wav")) fail("work card must omit intake filenames");

const latestMemoForSong = new Function(
  "return (" + extractFunction(script, "latestMemoForSong") + ");",
)();
const latest = latestMemoForSong("JS-0001", [
  { s: "JS-0001", d: "2020-01-01", f: "old.m4a" },
  { s: "JS-0001", d: "2024-12-01", f: "new.m4a" },
  { s: "JS-0002", d: "2025-01-01", f: "other.m4a" },
]);
if (!latest || latest.f !== "new.m4a") fail("latest memo must be the newest searchable row");

const workFields = {
  q: { value: "old" }, proj: { value: "old" }, scored: { value: "old" },
  scope: { value: "old" }, sort: { value: "id" }, evidence: { value: "old" },
  work: { value: "", focus() { this.focused = true; } },
};
const workCalls = [];
const workNavigation = new Function(
  "sname", "DATA", "songWorkKind", "q", "proj", "scored", "scope", "sort", "evidence", "work",
  "showTab", "paint", "writeVaultHash", "recordFocus",
  "let lastWorkKind = ''; let activeWorkSongId = '';" +
    "function render(){ paint(); if(!activeWorkSongId)activeWorkSongId = 'JS-0001'; }" +
    "function focusWorkSong(id){ recordFocus(id); return true; }" +
    "const openWork = " + extractFunction(script, "openWork") + ";" +
    "return { openWork, active: () => activeWorkSongId };",
)(
  names, storedRows, songWorkKind, workFields.q, workFields.proj, workFields.scored, workFields.scope,
  workFields.sort, workFields.evidence, workFields.work,
  (tab) => workCalls.push(tab), () => workCalls.push("render"),
  (kind, id) => workCalls.push(String(kind) + ":" + String(id)),
  (id) => workCalls.push("focus:" + id),
);
workNavigation.openWork("write");
if (workFields.work.value !== "write" || workFields.q.value !== "") {
  fail("openWork must set the write filter without isolating a song");
}
if (workCalls.join(",") !== "S,render,work:write,focus:JS-0001") {
  fail("openWork must paint Songs, write the work hash, and open the first match");
}
workCalls.length = 0;
workNavigation.openWork("write", "JS-0001");
if (workNavigation.active() !== "JS-0001" || workCalls.join(",") !== "S,render,work:write,focus:JS-0001") {
  fail("resume must reopen the exact validated song inside its matching work queue");
}
const hashCalls = [];
const applyWorkHash = new Function(
  "openWork",
  "return (" + extractFunction(script, "applyWorkHash") + ");",
)((kind, id) => { hashCalls.push(String(kind) + ":" + String(id || "")); return !!id; });
if (!applyWorkHash("write", { v: 1, kind: "write", id: "JS-0002" }) || hashCalls.join(",") !== "write:JS-0002") {
  fail("matching work hash must resume the exact stored song, not the first queue match");
}
hashCalls.length = 0;
if (applyWorkHash("write", { v: 1, kind: "produce", id: "JS-0002" }) || hashCalls.join(",") !== "write:") {
  fail("mismatched stored kind must start the hash kind instead of keeping the old song");
}
hashCalls.length = 0;
if (applyWorkHash("write", null) || hashCalls.join(",") !== "write:") {
  fail("missing stored session must start the hash kind");
}
const forgetWorkSessionResult = new Function(
  "return (" + extractFunction(script, "forgetWorkSessionResult") + ");",
)();
const forgot = forgetWorkSessionResult(true, null);
if (!forgot.ok || forgot.message !== "Forgot this browser record.") {
  fail("Forget must announce a cleared browser record");
}
const blocked = forgetWorkSessionResult(false, { v: 1, kind: "write", id: "JS-0001" });
if (blocked.ok || blocked.message !== "Could not clear this browser record.") {
  fail("Forget must soft-fail when the browser record remains");
}
const unread = forgetWorkSessionResult(false, null);
if (unread.ok || unread.message !== "") {
  fail("Forget must soft-fail quietly when storage is unreadable");
}
if (!extractFunction(script, "forgetLastWorkSession").includes("writeVaultHash(")) {
  fail("Forget must drop the work hash so a refresh does not mint a new record");
}
workNavigation.openWork("not-a-kind");
if (workFields.work.value !== "write") fail("openWork must reject unknown work kinds");

const sessionUi = {
  panel: { hidden: true }, text: { textContent: "" },
  action: { hidden: true, textContent: "" }, evidence: { textContent: "" },
  copy: { hidden: true, disabled: true, dataset: {}, setAttribute(name, value) { this[name] = value; } },
  review: { hidden: true, disabled: true, dataset: {}, setAttribute(name, value) { this[name] = value; } },
  prev: {}, next: {},
};
const updateWorkSessionState = new Function(
  "workSession", "work", "workSessionText", "workSessionNext", "workSessionEvidence",
  "copyWorkNext", "openWorkEvidence", "workPrev", "workNext",
  "visibleSongIds", "activeWorkSongId", "sname", "DATA", "safeWorkNextStep", "memoEvidenceBySong",
  "return (" + extractFunction(script, "updateWorkSessionState") + ");",
)(
  sessionUi.panel, { value: "write" }, sessionUi.text, sessionUi.action, sessionUi.evidence,
  sessionUi.copy, sessionUi.review, sessionUi.prev, sessionUi.next,
  ["JS-0001", "JS-0002"], "JS-0002", names,
  [
    { id: "JS-0001", nx: "Write the verse" },
    { id: "JS-0002", nx: "Confirm the chorus" },
  ],
  safeWorkNextStep,
  { "JS-0002": { n: 2, last: "2026-09-01" } },
);
updateWorkSessionState();
if (sessionUi.panel.hidden || sessionUi.text.textContent !== "Write · 2 of 2 · Second Song") {
  fail("work session must name the exact current song and position");
}
if (sessionUi.prev.disabled || !sessionUi.next.disabled) {
  fail("work session navigation must stop honestly at the queue boundary");
}
if (sessionUi.action.hidden || sessionUi.action.textContent !== "Do this now: Confirm the chorus") {
  fail("work session must surface the exact safe next step without hunting in the row");
}
if (sessionUi.copy.hidden || sessionUi.copy.disabled || sessionUi.copy.dataset.songId !== "JS-0002") {
  fail("safe next step must enable the exact-song copy action");
}
if (sessionUi.review.hidden || sessionUi.review.disabled || !sessionUi.evidence.textContent.includes("2 searchable memos")) {
  fail("matched evidence must enable review and name its honest receipt count");
}

const copiedNext = [];
const copyExactSongNextStep = new Function(
  "DATA", "safeWorkNextStep", "copyVaultText", "allowedExactWorkSongId", "songWorkKind", "work",
  "return (" + extractFunction(script, "copyExactSongNextStep") + ");",
)(
  [{ id: "JS-0002", nx: "Listen to latest (mix.wav) and rate it" }],
  safeWorkNextStep,
  (value, button, label) => { copiedNext.push({ value, button, label }); return !!value; },
  (id) => id === "JS-0002" ? id : "",
  songWorkKind,
  { value: "listen" },
);
const copyButton = { dataset: { songId: "JS-0002" } };
if (!copyExactSongNextStep(copyButton.dataset.songId, copyButton) || copiedNext[0].value !== "Listen to latest and rate it" || copiedNext[0].label !== "Copy next step") {
  fail("copy next step must copy only the sanitized current-song action");
}
if (copyExactSongNextStep("missing", { dataset: { songId: "missing" } })) {
  fail("copy next step must fail closed for a missing song");
}
const wrongKindCopy = new Function(
  "DATA", "safeWorkNextStep", "copyVaultText", "allowedExactWorkSongId", "songWorkKind", "work",
  "return (" + extractFunction(script, "copyExactSongNextStep") + ");",
)(
  [{ id: "JS-0002", nx: "Listen to latest (mix.wav) and rate it" }],
  safeWorkNextStep,
  () => true,
  (id) => id,
  songWorkKind,
  { value: "write" },
);
if (wrongKindCopy("JS-0002", copyButton)) {
  fail("copy next step must fail closed when the stored kind no longer matches");
}

const reviewedEvidence = [];
const reviewCurrentWorkEvidence = new Function(
  "allowedExactWorkSongId", "memoCountBySong", "openSongMemos",
  "return (" + extractFunction(script, "reviewCurrentWorkEvidence") + ");",
)((id) => id === "JS-0002" ? id : "", { "JS-0002": 2 }, (id) => reviewedEvidence.push(id));
if (!reviewCurrentWorkEvidence({ dataset: { songId: "JS-0002" } }) || reviewedEvidence.join(",") !== "JS-0002") {
  fail("review evidence must open the exact scoped memo set");
}
if (reviewCurrentWorkEvidence({ dataset: { songId: "JS-0001" } })) {
  fail("review evidence must fail closed when the song is not the exact current session");
}

const resumeUi = {
  panel: { hidden: true },
  hint: { hidden: true },
  text: { textContent: "" },
  button: { setAttribute(name, value) { this[name] = value; } },
  action: { hidden: true, textContent: "" },
  copy: { hidden: true, disabled: true, dataset: {}, setAttribute(name, value) { this[name] = value; } },
};
const updateResumeWork = new Function(
  "resumeWork", "resumeWorkHint", "resumeWorkText", "resumeWorkButton",
  "resumeWorkNext", "copyResumeNext", "sname", "DATA",
  "readStoredWorkSession", "vaultStorage", "safeWorkNextStep",
  "return (" + extractFunction(script, "updateResumeWork") + ");",
)(
  resumeUi.panel, resumeUi.hint, resumeUi.text, resumeUi.button,
  resumeUi.action, resumeUi.copy, names,
  [
    { id: "JS-0002", nx: "Confirm the chorus" },
    { id: "JS-0133", nx: "LISTEN: Crescent Dr 21." },
  ],
  () => ({ v: 1, kind: "write", id: "JS-0002" }),
  () => ({}),
  safeWorkNextStep,
);
const resumed = updateResumeWork();
if (!resumed || resumeUi.panel.hidden || resumeUi.text.textContent !== "Write · Second Song") {
  fail("resume must still name the exact stored song");
}
if (resumeUi.action.hidden || resumeUi.action.textContent !== "Do this now: Confirm the chorus") {
  fail("resume must put the exact safe next step in front of Jeff without reopening first");
}
if (resumeUi.copy.hidden || resumeUi.copy.disabled || resumeUi.copy.dataset.songId !== "JS-0002") {
  fail("resume must enable copy only for the exact stored song");
}

const closedUi = {
  panel: { hidden: true },
  hint: { hidden: true },
  text: { textContent: "" },
  button: { setAttribute() {} },
  action: { hidden: true, textContent: "stale" },
  copy: { hidden: false, disabled: false, dataset: { songId: "JS-0133" }, setAttribute() {} },
};
const closedResume = new Function(
  "resumeWork", "resumeWorkHint", "resumeWorkText", "resumeWorkButton",
  "resumeWorkNext", "copyResumeNext", "sname", "DATA",
  "readStoredWorkSession", "vaultStorage", "safeWorkNextStep",
  "return (" + extractFunction(script, "updateResumeWork") + ");",
)(
  closedUi.panel, closedUi.hint, closedUi.text, closedUi.button,
  closedUi.action, closedUi.copy, { "JS-0133": "Leftover Listen" },
  [{ id: "JS-0133", nx: "LISTEN: Maxwell Dr 104 (later take)." }],
  () => ({ v: 1, kind: "listen", id: "JS-0133" }),
  () => ({}),
  safeWorkNextStep,
);
const closed = closedResume();
if (!closed || closed.id !== "JS-0133" || closedUi.panel.hidden) {
  fail("fail-closed resume must still keep the exact stored song");
}
if (!closedUi.action.hidden || closedUi.action.textContent !== "" || closedUi.action.textContent.includes("LISTEN")) {
  fail("fail-closed resume must not show a leftover listen verb as the next step");
}
if (!closedUi.copy.hidden || !closedUi.copy.disabled || closedUi.copy.dataset.songId) {
  fail("fail-closed resume must hide Copy next step when sanitizing leaves no useful action");
}

const workStepper = new Function(
  "let visibleSongIds = ['JS-0001', 'JS-0002']; let activeWorkSongId = 'JS-0001';" +
    "function focusWorkSong(id){ activeWorkSongId = id; return true; }" +
    "const stepWork = " + extractFunction(script, "stepWork") + ";" +
    "return { stepWork, active: () => activeWorkSongId };",
)();
if (!workStepper.stepWork(1) || workStepper.active() !== "JS-0002") {
  fail("next must advance to the following work item");
}
if (workStepper.stepWork(1) || workStepper.active() !== "JS-0002") {
  fail("next must not wrap and pretend the queue has not ended");
}

const escapeNav = new Function(
  "paneM",
  "paneS",
  "mq",
  "q",
  "sname",
  "proj",
  "sort",
  "scored",
  "scope",
  "evidence",
  "let activeMemoSong = 'JS-0001'; let hashed = ''; let painted = '';" +
    "function writeVaultHash(kind, id) { hashed = String(kind || '') + ':' + String(id || ''); }" +
    "function mrender() { painted = 'memos'; }" +
    "function render() { painted = 'songs'; }" +
    "const handleVaultKey = " + extractFunction(script, "handleVaultKey") + ";" +
    "return { handleVaultKey, active: () => activeMemoSong, hashed: () => hashed, painted: () => painted };",
)(
  { hidden: false },
  { hidden: true },
  { value: "old", focus() {} },
  { value: "JS-0001", focus() {} },
  names,
  { value: "" },
  { value: "id" },
  { value: "" },
  { value: "" },
  { value: "" },
);
if (!escapeNav.handleVaultKey({ key: "Escape" }) || escapeNav.active() !== "") {
  fail("escape must clear the scoped memo set");
}
if (escapeNav.painted() !== "memos" || escapeNav.hashed() !== ":") {
  fail("escape must repaint Memo Search and drop the hash");
}

const stripForSearch = new Function(
  "return (" + extractFunction(script, "stripPrivateLocators") + ");",
)();
const normalizeSearch = new Function(
  "return (" + extractFunction(script, "normalizeSearch") + ");",
)();
if (normalizeSearch("Don't Put Your Life Away") !== normalizeSearch("dont put your life away")) {
  fail("song search must fold apostrophes");
}
if (normalizeSearch("Manic?  No way!") !== "manic no way") {
  fail("song search must fold punctuation on remembered names");
}
const songAliases = new Function(
  "normalizeSearch",
  "return (" + extractFunction(script, "songAliases") + ");",
)(normalizeSearch);
if (songAliases({ t: "Candi Lane", aka: ["Candy Lane (2017)", "Candi Lane"] }).join("|") !== "Candy Lane (2017)") {
  fail("aliases must stay existing alt titles and drop the canonical duplicate");
}
const songSearchHit = new Function(
  "normalizeSearch",
  "songAliases",
  "stripPrivateLocators",
  "memoLyricNorm",
  "return (" + extractFunction(script, "songSearchHit") + ");",
)(
  normalizeSearch,
  songAliases,
  stripForSearch,
  (id) => ({ "JS-9999": normalizeSearch("we drove down candy lane tonight") }[id] || ""),
);
const aliasHit = songSearchHit(
  { id: "ST-0019", t: "Candi Lane", aka: ["Candy Lane (2017)"], th: "" },
  "candy lane",
);
if (!aliasHit.hit || aliasHit.via !== "name" || aliasHit.rank !== 0) {
  fail("an existing alias must be an exact name match");
}
const fieldHit = songSearchHit(
  { id: "JS-9998", t: "Other Song", th: "candy lane is in the notes" },
  "candy lane",
);
if (!fieldHit.hit || fieldHit.via !== "field" || fieldHit.rank !== 3) {
  fail("theme text must stay behind a real name match");
}
const memoHit = songSearchHit(
  { id: "JS-9999", t: "Unrelated" },
  "candy lane",
);
if (!memoHit.hit || memoHit.via !== "memo" || memoHit.rank !== 4) {
  fail("a long enough query may find a song from memo lyric text only");
}
if (songSearchHit({ id: "JS-9999", t: "Unrelated" }, "ca").hit) {
  fail("short queries must not scan memo lyrics");
}
const sortSongRows = new Function(
  "songSearchHit",
  "return (" + extractFunction(script, "sortSongRows") + ");",
)(songSearchHit);
const ranked = sortSongRows(
  [
    { id: "JS-9998", t: "Other Song", th: "candy lane is in the notes", mom: 90 },
    { id: "ST-0019", t: "Candi Lane", aka: ["Candy Lane (2017)"], th: "", mom: 10 },
    { id: "JS-9999", t: "Unrelated", th: "", mom: 80 },
  ],
  "candy lane",
  "mom",
);
if (ranked[0].row.id !== "ST-0019" || ranked[0].hit.via !== "name") {
  fail("closest remembered name must beat a higher-momentum field hit");
}
if (ranked[1].row.id !== "JS-9998" || ranked[2].row.id !== "JS-9999") {
  fail("field hits must outrank memo-lyric-only hits");
}
const markNormalized = new Function(
  "esc",
  "normalizeSearch",
  "return (" + extractFunction(script, "markNormalized") + ");",
)(esc, normalizeSearch);
if (markNormalized("Don't Put Your Life Away", "dont put") !== "<mark>Don&#39;t Put</mark> Your Life Away") {
  fail("title highlight must survive apostrophe folding");
}
if (markNormalized("Candi Lane", "candy lane") === "Candi Lane".replace("Candi", "<mark>Candi</mark>")) {
  fail("a title that is not the typed alias must stay unhighlighted");
}
if (markNormalized("Candy Lane (2017)", "candy lane") !== "<mark>Candy Lane</mark> (2017)") {
  fail("the matching alias must highlight");
}

const searchFocus = { id: "", focused: 0 };
const searchKey = new Function(
  "q",
  "visibleSongIds",
  "work",
  "focusWorkSong",
  "focusFoundSong",
  "return (" + extractFunction(script, "handleSongSearchKey") + ");",
)(
  { value: "candy lane" },
  ["ST-0019", "JS-9998"],
  { value: "" },
  () => { searchFocus.id = "work"; return true; },
  (id) => { searchFocus.id = id; searchFocus.focused += 1; return true; },
);
if (!searchKey({ key: "Enter", preventDefault() {} }) || searchFocus.id !== "ST-0019") {
  fail("Enter in Songs search must open the closest name match");
}
if (searchKey({ key: "Tab" }) || searchFocus.focused !== 1) {
  fail("non-Enter keys must leave the search results alone");
}

const searchEscape = new Function(
  "paneM",
  "paneS",
  "mq",
  "q",
  "sname",
  "proj",
  "sort",
  "scored",
  "scope",
  "evidence",
  "let hashed = ''; let painted = '';" +
    "function writeVaultHash(kind, id) { hashed = String(kind || '') + ':' + String(id || ''); }" +
    "function render() { painted = 'songs'; }" +
    "const handleVaultKey = " + extractFunction(script, "handleVaultKey") + ";" +
    "return { handleVaultKey, hashed: () => hashed, painted: () => painted, q };",
)(
  { hidden: true },
  { hidden: false },
  { value: "", focus() {} },
  { value: "candy lane", focus() {} },
  names,
  { value: "" },
  { value: "mom" },
  { value: "" },
  { value: "" },
  { value: "" },
);
if (!searchEscape.handleVaultKey({ key: "Escape" }) || searchEscape.q.value !== "") {
  fail("escape must clear a remembered-name search");
}
if (searchEscape.painted() !== "songs" || searchEscape.hashed() !== ":") {
  fail("escape must repaint Songs after clearing a name search");
}

console.log("dashboard song/memo navigation smoke ok");
