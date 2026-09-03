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
  "function copyMemoFile(",
  "function copyVaultText(",
  "function songWorkKind(",
  "function buildSongWorkCard(",
  "function copySongWork(",
  "function openWork(",
  "function updateWorkSessionState(",
  "function latestMemoForSong(",
  "function stepWork(",
  "id=\"evidence\"",
  "id=\"work\"",
  "id=\"workSession\"",
  "id=\"workStarts\"",
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

const songWorkKind = new Function(
  "return (" + extractFunction(script, "songWorkKind") + ");",
)();
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

const buildSongWorkCard = new Function(
  "flattenWorkField",
  "songWorkKind",
  "stripPrivateLocators",
  "workCardLeaks",
  "return (" + extractFunction(script, "buildSongWorkCard") + ");",
)(
  new Function("return (" + extractFunction(script, "flattenWorkField") + ");")(),
  songWorkKind,
  stripPrivateLocators,
  new Function("return (" + extractFunction(script, "workCardLeaks") + ");")(),
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
  "sname", "q", "proj", "scored", "scope", "sort", "evidence", "work",
  "showTab", "paint", "writeVaultHash", "recordFocus",
  "let lastWorkKind = ''; let activeWorkSongId = '';" +
    "function render(){ paint(); activeWorkSongId = 'JS-0001'; }" +
    "function focusWorkSong(id){ recordFocus(id); return true; }" +
    "const openWork = " + extractFunction(script, "openWork") + ";" +
    "return { openWork, active: () => activeWorkSongId };",
)(
  names, workFields.q, workFields.proj, workFields.scored, workFields.scope,
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
workNavigation.openWork("not-a-kind");
if (workFields.work.value !== "write") fail("openWork must reject unknown work kinds");

const sessionUi = {
  panel: { hidden: true }, text: { textContent: "" }, prev: {}, next: {},
};
const updateWorkSessionState = new Function(
  "workSession", "work", "workSessionText", "workPrev", "workNext",
  "visibleSongIds", "activeWorkSongId", "sname",
  "return (" + extractFunction(script, "updateWorkSessionState") + ");",
)(
  sessionUi.panel, { value: "write" }, sessionUi.text, sessionUi.prev, sessionUi.next,
  ["JS-0001", "JS-0002"], "JS-0002", names,
);
updateWorkSessionState();
if (sessionUi.panel.hidden || sessionUi.text.textContent !== "Write · 2 of 2 · Second Song") {
  fail("work session must name the exact current song and position");
}
if (sessionUi.prev.disabled || !sessionUi.next.disabled) {
  fail("work session navigation must stop honestly at the queue boundary");
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

console.log("dashboard song/memo navigation smoke ok");
