#!/usr/bin/env node
/**
 * Exercise StoryBoard's real catalog importer, not the Python contract mirror.
 *
 * Production path: packages/shared/src/catalog-import.ts
 *   planCatalogImport → reconcileCatalogImport
 * Apply writes only createSongs/createSetlists. Re-applying the same Vault
 * feed must skip existing sourceKey/title rows (first write wins).
 */
import { spawnSync } from "node:child_process";
import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const root = resolve(here, "..");
const cache = process.env.STORYBOARD_IMPORT_CACHE || join("/tmp", "ai-music-vault-storyboard-import");
const STORYBOARD_RAW =
  process.env.STORYBOARD_CATALOG_IMPORT_URL ||
  "https://raw.githubusercontent.com/rupret007/StoryBoard/main/packages/shared/src/catalog-import.ts";

function fail(message) {
  throw new Error(message);
}

function siblingImporter() {
  return resolve(root, "..", "StoryBoard", "packages", "shared", "src", "catalog-import.ts");
}

function resolveImporterSource() {
  const override = process.env.STORYBOARD_CATALOG_IMPORT;
  if (override && existsSync(override)) return resolve(override);
  const sibling = siblingImporter();
  if (existsSync(sibling)) return sibling;
  mkdirSync(cache, { recursive: true });
  const dest = join(cache, "catalog-import.ts");
  const pulled = spawnSync("curl", ["-fsSL", STORYBOARD_RAW, "-o", dest], { encoding: "utf8" });
  if (pulled.status !== 0) {
    fail(
      "could not load StoryBoard catalog-import.ts from " +
        STORYBOARD_RAW +
        "\n" +
        (pulled.stderr || pulled.stdout || ""),
    );
  }
  return dest;
}

function ensureZod(workdir) {
  writeFileSync(
    join(workdir, "package.json"),
    JSON.stringify({ name: "vault-storyboard-import-test", type: "module", private: true }, null, 2),
  );
  if (existsSync(join(workdir, "node_modules", "zod", "package.json"))) return;
  const install = spawnSync("npm", ["install", "--silent", "--no-fund", "--no-audit", "zod@4.3.6"], {
    cwd: workdir,
    encoding: "utf8",
    env: process.env,
  });
  if (install.status !== 0) {
    fail("npm install zod failed\n" + (install.stderr || install.stdout || ""));
  }
}

function existingFromCreated(reconciliation) {
  return {
    songs: reconciliation.createSongs.map((song) => ({
      id: song.sourceKey,
      title: song.title,
      sourceKey: song.sourceKey,
    })),
    setlists: reconciliation.createSetlists.map((setlist) => ({
      id: setlist.sourceKey,
      sourceKey: setlist.sourceKey,
    })),
  };
}

const importerPath = resolveImporterSource();
const workdir = cache;
mkdirSync(workdir, { recursive: true });
const localImporter = join(workdir, "catalog-import.ts");
if (resolve(importerPath) !== resolve(localImporter)) {
  writeFileSync(localImporter, readFileSync(importerPath));
}
ensureZod(workdir);

const shared = await import(pathToFileURL(localImporter).href);
if (typeof shared.planCatalogImport !== "function" || typeof shared.reconcileCatalogImport !== "function") {
  fail("StoryBoard catalog-import.ts must export planCatalogImport and reconcileCatalogImport");
}

const appApi = JSON.parse(readFileSync(join(root, "data", "app_api.json"), "utf8"));
const plan = shared.planCatalogImport({ vault: appApi });
if (!plan.songs.length) fail("live data/app_api.json planned zero songs");
if (!plan.songs.every((song) => String(song.sourceKey || "").startsWith("vault:catalog_import_v1:"))) {
  fail("planned songs must use the Vault sourceKey constructor");
}

const first = shared.reconcileCatalogImport(plan, { songs: [], setlists: [] });
if (first.createSongs.length !== plan.songs.length) {
  fail("empty library must create every planned song");
}
if (first.skipSongs.length) fail("empty library must not skip planned songs");

const second = shared.reconcileCatalogImport(plan, existingFromCreated(first));
if (second.createSongs.length !== 0) {
  fail("re-importing the same Vault feed must create zero songs");
}
if (second.skipSongs.length !== plan.songs.length) {
  fail("re-import must skip every planned song");
}
if (!second.skipSongs.every((row) => row.reason === "source_key_exists")) {
  fail("re-import skips must be source_key_exists");
}

const titleHit = plan.songs[0];
const titled = shared.reconcileCatalogImport(plan, {
  songs: [{ id: "manual:existing", title: titleHit.title, sourceKey: "manual:existing" }],
  setlists: [],
});
const titleSkip = titled.skipSongs.find((row) => row.title === titleHit.title);
if (!titleSkip || titleSkip.reason !== "title_exists") {
  fail("existing non-Vault title must skip with title_exists");
}
if (titled.createSongs.some((song) => song.title === titleHit.title)) {
  fail("title collision must not mint a second song");
}
if (titled.createSongs.some((song) => song.sourceKey === "manual:existing")) {
  fail("reconcile must not rewrite the existing non-Vault sourceKey");
}

console.log(
  "storyboard importer OK — " +
    plan.songs.length +
    " planned · re-import skipped " +
    second.skipSongs.length +
    " · title collision first-write-wins · module " +
    importerPath,
);
