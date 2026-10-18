#!/usr/bin/env node
// Enforces the invariants in CLAUDE.md. Run with `npm run check`; CI runs it
// on every push and pull request. Exits 1 and lists every violation.

import { execFileSync } from "node:child_process";
import { existsSync, readFileSync, readdirSync } from "node:fs";
import { dirname, join, relative, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const repo = join(dirname(fileURLToPath(import.meta.url)), "..");
const PROMOTED = ["engineering", "productivity"];
const BUCKETS = [...PROMOTED, "in-progress", "deprecated"];
const EM_DASH = String.fromCharCode(0x2014);
const errors = [];
const fail = (msg) => errors.push(msg);
const read = (p) => readFileSync(join(repo, p), "utf8");

// Every file git would publish: tracked plus untracked-but-not-ignored.
const files = execFileSync("git", ["ls-files", "--cached", "--others", "--exclude-standard"], {
  cwd: repo,
  encoding: "utf8",
})
  .split("\n")
  .filter((f) => f && existsSync(join(repo, f)));

// 1. Nothing from private/ is publishable.
for (const f of files) if (f.startsWith("private/")) fail(`${f}: private/ must stay gitignored`);

// 2. Skills: frontmatter, bucket, Codex metadata.
const skills = files
  .filter((f) => f.startsWith("skills/") && f.endsWith("/SKILL.md"))
  .map((f) => {
    const dir = dirname(f);
    const [, bucket, name] = dir.split("/");
    return { dir, bucket, name, file: f };
  });

for (const s of skills) {
  if (!BUCKETS.includes(s.bucket)) fail(`${s.file}: unknown bucket "${s.bucket}"`);
  const m = read(s.file).match(/^---\n([\s\S]*?)\n---\n/);
  if (!m) {
    fail(`${s.file}: missing YAML frontmatter`);
    continue;
  }
  const name = m[1].match(/^name:\s*(.+)$/m)?.[1].trim();
  const description = m[1].match(/^description:\s*(.+)$/m)?.[1].trim();
  if (name !== s.name) fail(`${s.file}: frontmatter name "${name}" must equal folder name "${s.name}"`);
  if (!description) fail(`${s.file}: missing description`);
  else if (description.length > 1024) fail(`${s.file}: description is ${description.length} chars, limit 1024`);
  if (!files.includes(`${s.dir}/agents/openai.yaml`)) fail(`${s.dir}: missing agents/openai.yaml`);
}

// 3. Promoted skills appear in the plugin, both READMEs and the docs tree; nothing else does.
const plugin = JSON.parse(read(".claude-plugin/plugin.json"));
const promoted = skills.filter((s) => PROMOTED.includes(s.bucket));
const want = promoted.map((s) => `./${s.dir}`).sort();
const have = [...plugin.skills].sort();
if (JSON.stringify(want) !== JSON.stringify(have))
  fail(`plugin.json skills ${JSON.stringify(have)} must equal promoted set ${JSON.stringify(want)}`);

const readme = read("README.md");
for (const s of promoted) {
  if (!readme.includes(`(./${s.dir}/SKILL.md)`)) fail(`README.md: no link to ./${s.dir}/SKILL.md`);
  const bucketReadme = `skills/${s.bucket}/README.md`;
  if (!files.includes(bucketReadme)) fail(`${bucketReadme}: missing`);
  else if (!read(bucketReadme).includes(`(./${s.name}/SKILL.md)`)) fail(`${bucketReadme}: no link to ./${s.name}/SKILL.md`);
  if (!files.includes(`docs/${s.bucket}/${s.name}.md`)) fail(`docs/${s.bucket}/${s.name}.md: missing docs page`);
}
for (const f of files.filter((f) => f.startsWith("docs/") && f.endsWith(".md"))) {
  const [, bucket, page] = f.split("/");
  if (!promoted.some((s) => s.bucket === bucket && `${s.name}.md` === page)) fail(`${f}: docs page for a skill that is not promoted`);
}

// 4. Versions agree.
const pkg = JSON.parse(read("package.json"));
if (plugin.version !== pkg.version) fail(`plugin.json version ${plugin.version} != package.json ${pkg.version}`);

// 5. Prose rules and links, over every text file.
const text = files.filter((f) => /\.(md|json|ya?ml|mjs|sh)$/.test(f) && f !== "package-lock.json");
for (const f of text) {
  const body = read(f);
  body.split("\n").forEach((line, i) => {
    if (line.includes(EM_DASH)) fail(`${f}:${i + 1}: em dash; rewrite the sentence`);
  });
  if (!f.endsWith(".md")) continue;
  for (const [, target] of body.matchAll(/\]\(([^)\s]+)\)/g)) {
    if (/^(https?:|mailto:|#)/.test(target)) continue;
    const path = resolve(repo, dirname(f), target.split("#")[0]);
    if (!existsSync(path)) fail(`${f}: broken link ${target}`);
  }
}

if (errors.length) {
  console.error(errors.map((e) => `x ${e}`).join("\n"));
  console.error(`\n${errors.length} problem(s).`);
  process.exit(1);
}
console.log(`ok: ${skills.length} skill(s), ${promoted.length} promoted, ${text.length} text files checked`);
