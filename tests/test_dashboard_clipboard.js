"use strict";

// Exercise the actual copy helper offline with synthetic text and a minimal DOM.
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const { test } = require("node:test");

const root = path.resolve(__dirname, "..");
const surfaces = ["scripts/build_dashboard.py", "Jeff Story Song Vault Dashboard.html"];

function deferred() {
  let resolve, reject;
  const promise = new Promise((yes, no) => { resolve = yes; reject = no; });
  return { promise, resolve, reject };
}

function fixture(source, options = {}) {
  const timers = new Map();
  const created = [];
  const adjacent = [];
  const calls = { modern: [], legacy: [], focus: [] };
  let timerId = 0;
  const document = {};

  function element(tagName) {
    const classes = new Set();
    return {
      tagName, textContent: "", value: "", disabled: false, style: {}, attributes: {},
      parentNode: null, parentElement: null, isConnected: false,
      classList: {
        add: name => classes.add(name),
        remove: name => classes.delete(name),
        contains: name => classes.has(name),
        toggle(name, force) {
          const enabled = force === undefined ? !classes.has(name) : force;
          if (enabled) classes.add(name);
          else classes.delete(name);
          return enabled;
        },
      },
      setAttribute(name, value) { this.attributes[name] = String(value); },
      getAttribute(name) { return this.attributes[name] ?? null; },
      focus(args) { calls.focus.push({ target: this, args }); document.activeElement = this; },
      select() { document.activeElement = this; },
      remove() { if (this.parentNode) this.parentNode.removeChild(this); },
      insertAdjacentElement(position, next) {
        assert.equal(position, "afterend");
        adjacent.push(next);
        next.parentNode = document.body;
        next.parentElement = document.body;
        next.isConnected = true;
        return next;
      },
    };
  }

  document.body = {
    children: [],
    appendChild(child) {
      this.children.push(child);
      child.parentNode = this;
      child.parentElement = this;
      child.isConnected = true;
      return child;
    },
    removeChild(child) {
      this.children = this.children.filter(item => item !== child);
      child.parentNode = null;
      child.parentElement = null;
      child.isConnected = false;
      return child;
    },
  };
  document.createElement = tagName => {
    const node = element(tagName);
    created.push(node);
    return node;
  };
  document.execCommand = command => {
    calls.legacy.push({ command, value: document.activeElement.value });
    return options.legacy ? options.legacy() : true;
  };
  const announcement = element("p");
  announcement.isConnected = true;
  document.getElementById = id => id === "copyStatus" ? announcement : null;
  const previousFocus = element("input");
  previousFocus.isConnected = true;
  document.activeElement = previousFocus;
  const button = element("button");
  button.textContent = "Copy next step";
  button.isConnected = true;
  const navigator = options.modern === undefined ? {} : {
    clipboard: { writeText(value) { calls.modern.push(value); return options.modern(value); } },
  };
  const context = vm.createContext({
    document, navigator,
    setTimeout(callback, delay) { const id = ++timerId; timers.set(id, { callback, delay }); return id; },
    clearTimeout(id) { timers.delete(id); },
  });
  vm.runInContext("const copyFeedback = new WeakMap(); let latestCopyAttempt = 0;\n" + source, context);

  return {
    copy: (text = "Review the synthetic chorus.", label = "Copy next step") => context.copyVaultText(text, button, label),
    copyWithoutButton: text => context.copyVaultText(text, null, "Copy"),
    copyWithButton: (text, target, label) => context.copyVaultText(text, target, label),
    newButton(label) {
      const target = element("button");
      target.textContent = label;
      target.isConnected = true;
      return target;
    },
    button, document, created, adjacent, calls, previousFocus, timers, announcement,
    runTimers() {
      const scheduled = [...timers.values()];
      timers.clear();
      for (const timer of scheduled) timer.callback();
    },
    status() {
      assert.equal(adjacent.length, 1, "copy feedback has one adjacent status reused across attempts");
      const status = adjacent[0];
      assert.equal(status.tagName, "span");
      assert.equal(status.getAttribute("role"), null, "only the permanent status region announces outcomes");
      assert.equal(status.getAttribute("aria-live"), null);
      assert(status.className === "copy-status" || status.classList.contains("copy-status"));
      return status.textContent;
    },
    assertRestored() {
      assert.equal(document.body.children.length, 0, "temporary clipboard textarea is removed");
      assert.equal(document.activeElement, previousFocus, "previous keyboard focus is restored");
      assert.equal(calls.focus.at(-1)?.args?.preventScroll, true, "focus restoration must not jump the page");
    },
    assertFailed() {
      assert.equal(button.textContent, "Copy next step");
      assert.equal(button.disabled, false);
      assert.equal(button.classList.contains("copied"), false);
      assert.equal(this.status(), "Copy next step: copy failed. Try again or copy the text manually.");
      assert.equal(announcement.textContent, this.status());
    },
  };
}

for (const surface of surfaces) {
  const text = fs.readFileSync(path.join(root, surface), "utf8");
  const start = text.indexOf("function copyVaultText(");
  const end = text.indexOf("function copySongWork(", start);
  assert(start >= 0 && end > start, `${surface}: copy helper must exist`);
  const source = text.slice(start, end);

  test(`${surface}: a permanent empty status region announces clipboard outcomes`, () => {
    const markup = text.slice(0, text.indexOf("<script>"));
    const status = markup.match(/<p\b[^>]*\bid="copyStatus"[^>]*>\s*<\/p>/);
    assert(status, "clipboard announcements must have an empty region present before copying starts");
    assert.match(status[0], /\brole="status"/);
    assert.match(status[0], /\baria-live="polite"/);
    assert.match(status[0], /\bclass="sr-only"/);
    assert.doesNotMatch(status[0], /\bhidden(?:\s|=|>)/);
  });

  test(`${surface}: empty input does not copy or show success`, () => {
    const env = fixture(source, { modern: () => Promise.resolve() });
    for (const value of ["", null, undefined]) assert.equal(env.copyWithoutButton(value), false);
    assert.equal(env.calls.modern.length, 0);
    assert.equal(env.calls.legacy.length, 0);
    assert.equal(env.created.length, 0);
  });

  test(`${surface}: modern success is pending until confirmed and resets its label`, async () => {
    const pending = deferred();
    const env = fixture(source, { modern: () => pending.promise });
    const result = env.copy();
    assert.equal(typeof result?.then, "function", "pending clipboard operations return their eventual outcome");
    assert.equal(env.button.textContent, "Copying…");
    assert.equal(env.button.disabled, false, "pending copy preserves keyboard access and retry");
    assert.equal(env.document.activeElement, env.previousFocus);
    assert.equal(env.button.classList.contains("copied"), false);
    assert.doesNotMatch(env.status(), /: copied\./);
    assert.equal(env.announcement.textContent, "");
    pending.resolve();
    assert.equal(await result, true);
    assert.deepEqual(env.calls.modern, ["Review the synthetic chorus."]);
    assert.equal(env.calls.legacy.length, 0);
    assert.equal(env.button.textContent, "Copied");
    assert.equal(env.button.disabled, false);
    assert.equal(env.button.classList.contains("copied"), true);
    assert.equal(env.status(), "Copy next step: copied.");
    assert.equal(env.announcement.textContent, env.status());
    assert.equal([...env.timers.values()][0]?.delay, 1200);
    env.runTimers();
    assert.equal(env.button.textContent, "Copy next step");
    assert.equal(env.button.classList.contains("copied"), false);
    assert.equal(env.announcement.textContent, "Copy next step: copied.", "label reset does not erase the announcement");
  });

  for (const [name, modern] of [
    ["rejected modern API", () => Promise.reject(new Error("Permission denied"))],
    ["synchronously throwing modern API", () => { throw new Error("Unavailable clipboard"); }],
    ["unavailable modern API", undefined],
  ]) {
    test(`${surface}: ${name} falls back, cleans up, and restores focus`, async () => {
      const env = fixture(source, { modern });
      assert.equal(await env.copy(), true);
      assert.deepEqual(env.calls.legacy, [{ command: "copy", value: "Review the synthetic chorus." }]);
      assert.equal(env.status(), "Copy next step: copied.");
      assert.equal(env.announcement.textContent, env.status());
      env.assertRestored();
    });
  }

  for (const [name, legacy] of [
    ["false", () => false],
    ["throw", () => { throw new Error("Copy is blocked"); }],
  ]) {
    test(`${surface}: legacy ${name} reports failure and removes the textarea`, async () => {
      const env = fixture(source, { modern: () => Promise.reject(new Error("Permission denied")), legacy });
      assert.equal(await env.copy(), false);
      env.assertFailed();
      env.assertRestored();
      env.runTimers();
      env.assertFailed();
    });
  }

  test(`${surface}: a failed copy can be retried with one accessible status`, async () => {
    let allowed = false;
    const env = fixture(source, { legacy: () => allowed });
    assert.equal(await env.copy(), false);
    env.assertFailed();
    allowed = true;
    assert.equal(await env.copy(), true);
    assert.equal(env.status(), "Copy next step: copied.");
    assert.equal(env.button.textContent, "Copied");
    assert.equal(env.button.disabled, false);
    env.assertRestored();
  });

  test(`${surface}: a prior success timer cannot replace newer failure feedback`, async () => {
    let allowed = true;
    const env = fixture(source, { legacy: () => allowed });
    assert.equal(await env.copy(), true);
    assert.equal(env.timers.size, 1);
    allowed = false;
    assert.equal(await env.copy(), false);
    assert.equal(env.timers.size, 0, "a new attempt cancels the previous label reset");
    env.runTimers();
    env.assertFailed();
  });

  test(`${surface}: stale completion cannot change the latest pending attempt`, async () => {
    const first = deferred(), second = deferred();
    let attempt = 0;
    const env = fixture(source, { modern: () => (++attempt === 1 ? first : second).promise, legacy: () => false });
    const oldResult = env.copy("First synthetic handoff.");
    const newResult = env.copy("Latest synthetic handoff.");
    first.resolve();
    assert.equal(await oldResult, true);
    assert.equal(env.button.textContent, "Copying…");
    assert.equal(env.button.disabled, false, "the newest pending attempt remains retryable");
    assert.equal(env.button.classList.contains("copied"), false);
    assert.doesNotMatch(env.status(), /: copied\./);
    assert.equal(env.announcement.textContent, "", "stale success does not announce over the pending attempt");
    second.reject(new Error("Permission denied"));
    assert.equal(await newResult, false);
    env.assertFailed();
    env.runTimers();
    env.assertFailed();
  });

  test(`${surface}: stale rejection cannot overwrite a newer successful copy`, async () => {
    const first = deferred(), second = deferred();
    let attempt = 0;
    const env = fixture(source, { modern: () => (++attempt === 1 ? first : second).promise });
    const oldResult = env.copy("First synthetic handoff.");
    const newResult = env.copy("Latest synthetic handoff.");
    second.resolve();
    assert.equal(await newResult, true);
    first.reject(new Error("Earlier copy was denied"));
    assert.equal(await oldResult, false);
    assert.equal(env.calls.legacy.length, 0, "a superseded copy must not overwrite the latest clipboard value");
    assert.equal(env.status(), "Copy next step: copied.");
    assert.equal(env.announcement.textContent, env.status());
    assert.equal(env.button.textContent, "Copied");
    assert.equal(env.timers.size, 1);
  });

  test(`${surface}: an earlier button cannot overwrite a different button's successful copy`, async () => {
    const first = deferred(), second = deferred();
    let attempt = 0;
    const env = fixture(source, { modern: () => (++attempt === 1 ? first : second).promise });
    const otherButton = env.newButton("Copy intake name");
    const oldResult = env.copy("First synthetic handoff.");
    const newResult = env.copyWithButton("Synthetic intake name", otherButton, "Copy intake name");
    second.resolve();
    assert.equal(await newResult, true);
    first.reject(new Error("Earlier copy was denied"));
    assert.equal(await oldResult, false);
    assert.equal(env.calls.legacy.length, 0, "clipboard ownership is shared across all copy buttons");
    assert.equal(otherButton.textContent, "Copied");
    assert.equal(env.adjacent.length, 2, "each button retains its own accessible feedback");
    assert.equal(env.adjacent[1].textContent, "Copy intake name: copied.");
    assert.equal(env.announcement.textContent, "Copy intake name: copied.", "stale failure cannot replace the newest announcement");
    assert.equal(env.button.textContent, "Copy next step");
    assert.equal(env.adjacent[0].textContent, "Copy next step: copy failed. Try again or copy the text manually.");
  });

  test(`${surface}: copy without a button still returns an honest outcome`, async () => {
    const env = fixture(source, { legacy: () => false });
    assert.equal(await env.copyWithoutButton("Synthetic clipboard value."), false);
    assert.equal(env.adjacent.length, 0);
    env.assertRestored();
  });
}
