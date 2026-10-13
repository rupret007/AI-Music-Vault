"use strict";

// Execute the real rendering functions without a browser or external packages.
const fs = require("node:fs");
const vm = require("node:vm");
const path = require("node:path");
const html = fs.readFileSync(process.argv[2] || path.join(__dirname, "../Jeff Story Song Vault Dashboard.html"), "utf8");
const script = html.split("<script>")[1].split("</script>")[0];
const functions = script.slice(script.indexOf("function esc("), script.indexOf("list.addEventListener('click'"));
const fields = Object.fromEntries(["q", "proj", "scored", "scope", "evidence", "work", "logicReady"].map(name => [name, { value: "" }]));
const context = vm.createContext({ ...fields, sort: { value: "id" }, list: {}, songResults: {}, clearSongFilters: {} });
vm.runInContext(functions, context);
vm.runInContext(`
  const DATA = [
    { id: 'TEST-1', t: 'Test song', p: 'Test project', st: 'Draft', nx: 'Write the chorus', pot: 75, rdy: 40, mom: 65, lr: 'fixture' },
    { id: 'TEST-2', t: 'No memo song', p: 'Test project', st: 'Draft', nx: 'Write the chorus' }
  ];
  const TX = [{ s: 'TEST-1', d: '2026-01-01', f: 'test-intake', x: 'Test lyric' }];
  const LOGIC_READY = { next: { fixture: 'Review in Logic.' }, label: {}, pill: {}, formats: {} };
  const memoEvidenceBySong = { 'TEST-1': { n: 2, last: '2026-01-01' } };
  const memoCountBySong = { 'TEST-1': 2 };
  let activeWorkSongId = '';
  // Session chrome is separate from row rendering under test.
  updateWorkSessionState = () => {};
  render();
`, context);
process.stdout.write(context.list.innerHTML);
