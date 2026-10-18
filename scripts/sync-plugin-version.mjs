#!/usr/bin/env node
// Copies package.json's version into .claude-plugin/plugin.json.
// Runs as part of `npm run version`, right after `changeset version`.

import { readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const repo = join(dirname(fileURLToPath(import.meta.url)), "..");
const pluginPath = join(repo, ".claude-plugin", "plugin.json");

const { version } = JSON.parse(readFileSync(join(repo, "package.json"), "utf8"));
const source = readFileSync(pluginPath, "utf8");

// Rewrite only the version line, so key order and formatting survive.
const updated = source.replace(/("version"\s*:\s*")[^"]*(")/, `$1${version}$2`);
if (JSON.parse(updated).version !== version) {
  console.error(`Could not find a version field in ${pluginPath}.`);
  process.exit(1);
}
writeFileSync(pluginPath, updated);
console.log(`plugin.json version -> ${version}`);
