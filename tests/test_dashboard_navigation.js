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
  "id=\"evidence\"",
  "Sort: Latest memo evidence",
  "Copy intake name",
  "newest first",
  "this page does not open audio",
  "aria-selected",
  "aria-expanded",
]) {
  if (!html.includes(marker)) fail("missing navigation marker " + marker);
}
if (html.includes("onclick=")) fail("generated dashboard must use delegated events, not inline clicks");
if (html.includes("<audio")) fail("generated dashboard must not open audio");

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

const parseVaultHash = new Function(
  "return (" + extractFunction(script, "parseVaultHash") + ");",
)();
if (!parseVaultHash("#memos=JS-0001", names) || parseVaultHash("#memos=JS-0001", names).kind !== "memos") {
  fail("hash must accept a known memo scope");
}
if (parseVaultHash("#memos=JS-9999", names)) fail("hash must reject unknown ids");
if (parseVaultHash("#open=JS-0001", names)) fail("hash must reject other kinds");
if (parseVaultHash("#memos=JS-0001<script>", names)) fail("hash must reject injected ids");

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
if (!extractFunction(script, "copyMemoFile").includes("execCommand")) {
  fail("copy must fall back when the clipboard API is blocked");
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
